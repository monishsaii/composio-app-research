"""L5: adjudicate every disputed / low-confidence / L1-reset field with the strongest model + conflicting evidence.

Adjudicator evidence is accepted only if it string-matches its cited page (same check as L1). A field whose
decision has no verified evidence, or that the adjudicator marks unresolved, goes to needs_human / human_queue.md.
After applying decisions, L3 rules run again (rubric verdict) to produce final.json.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from .. import cache
from ..apps import BY_ID
from ..tools import composio_tools as web
from . import l1_evidence as L1
from .l2_second_pass import KEY_FIELDS, get, put

STAGE = "l5"
TASKS = cache.CACHE / "llm" / "tasks" / STAGE
RESP = cache.CACHE / "llm" / "responses" / STAGE
PROMPT = Path(__file__).resolve().parents[1] / "prompts" / "l5_adjudicate.md"
ADJ_FIELDS = ["auth_methods", "access", "sandbox_or_test_env", "api_surface.breadth", "api_surface.webhooks",
              "mcp.exists", "mcp.url", "buildability.main_blocker"]
GROUP_OF = {**KEY_FIELDS, "mcp.url": "mcp"}
RESET_FIELDS = {"auth": ["auth_methods"], "access": ["access"], "sandbox": ["sandbox_or_test_env"],
                "mcp": ["mcp.exists", "mcp.url"], "api_surface": ["api_surface.breadth", "api_surface.webhooks"]}


def fields_to_adjudicate(r: dict) -> list[str]:
    f = []
    for d in r.get("disputes", []):
        if d["field"] in ADJ_FIELDS:
            f.append(d["field"])
    for g in r.get("l1_removed", {}):
        f += RESET_FIELDS.get(g, [])
    conf = r.get("confidence") or {}
    if conf.get("access") == "low" or r.get("access") == "unknown":
        f += ["access", "buildability.main_blocker"]
    if conf.get("auth") == "low" or not r.get("auth_methods"):
        f.append("auth_methods")
    if (r.get("mcp") or {}).get("exists") == "unknown":
        f.append("mcp.exists")
    if (r.get("api_surface") or {}).get("breadth") == "unknown" and r.get("access") != "no_public_api":
        f.append("api_surface.breadth")
    return [x for x in dict.fromkeys(f) if x in ADJ_FIELDS]


def emit(records: list[dict]) -> int:
    TASKS.mkdir(parents=True, exist_ok=True)
    prompt = PROMPT.read_text(encoding="utf-8")
    n = 0
    for r in records:
        fields = fields_to_adjudicate(r)
        if not fields:
            continue
        app = BY_ID[r["id"]]
        cur = {f: get(r, f) for f in fields}
        ctx = {
            "current_values": cur,
            "disputes": [{k: d[k] for k in ("field", "pass1", "l2", "adopted_l2", "l2_evidence")} for d in r.get("disputes", []) if d["field"] in fields],
            "values_reset_by_L1_for_lack_of_verified_evidence": r.get("l1_removed", {}),
            "evidence_dropped_by_L1": r.get("l1_dropped_evidence", [])[:12],
            "current_evidence": {g: r.get("evidence", {}).get(g, []) for g in {GROUP_OF[f] for f in fields}},
            "access_notes": r.get("access_notes"), "auth_notes": r.get("auth_notes"), "docs_url": r.get("docs_url"),
            "browser_pages": r.get("browser_evidence", []),
        }
        body = (f"{prompt}\n## App\nid: {app['id']}\nname: {app['name']}\ncategory: {app['category']}\n"
                f"known ambiguity: {app.get('ambiguity')}\n\n## Fields to adjudicate\n" + "\n".join(f"- {f}" for f in fields) +
                f"\n\n## Context\n```json\n{json.dumps(ctx, indent=1, ensure_ascii=False)[:30000]}\n```\n")
        (TASKS / f"{app['id']}.md").write_text(body, encoding="utf-8")
        n += 1
    return n


def apply(records: list[dict]) -> tuple[list[dict], dict, list[dict]]:
    out, queue = [], []
    stats = {"apps": 0, "fields": 0, "changed": 0, "resolved": 0, "unresolved": 0, "evidence_rejected": 0}
    for r in records:
        r = copy.deepcopy(r)
        p = RESP / f"{r['id']}.json"
        fields = fields_to_adjudicate(r)
        if not p.exists() or not fields:
            out.append(r)
            continue
        txt = p.read_text(encoding="utf-8")
        try:
            ans = json.loads(txt[txt.find("{") : txt.rfind("}") + 1])
        except ValueError:
            ans = {"fields": {}}
        stats["apps"] += 1
        r["l5"] = {"fields": fields}
        for f in fields:
            stats["fields"] += 1
            d = (ans.get("fields") or {}).get(f)
            g = GROUP_OF[f]
            if not d or not d.get("resolved"):
                stats["unresolved"] += 1
                queue.append({"id": r["id"], "name": r["name"], "field": f, "current": get(r, f),
                              "why": (d or {}).get("why", "adjudicator did not resolve"), "docs_url": r.get("docs_url")})
                r["needs_human"] = True
                continue
            ver = []
            for e in d.get("evidence", []):
                page = web.fetch(e["url"])
                kind, sc = L1.match(e.get("quote", ""), page.get("text", "")) if page.get("status") == 200 else ("unfetchable", 0)
                if kind in ("exact", "fuzzy"):
                    ver.append({**e, "support": kind, "match_score": sc, "fetched_at": page["fetched_at"], "from": "L5"})
                else:
                    stats["evidence_rejected"] += 1
            value = d.get("value")
            if not ver and value not in ("unknown", None, "none_found"):
                stats["unresolved"] += 1
                queue.append({"id": r["id"], "name": r["name"], "field": f, "current": get(r, f), "proposed": value,
                              "why": "adjudicator evidence failed verification", "docs_url": r.get("docs_url")})
                r["needs_human"] = True
                continue
            if get(r, f) != (sorted(value) if isinstance(value, list) else value):
                stats["changed"] += 1
                r.setdefault("flags", []).append(f"L5 {f}: {get(r, f)} -> {value}")
            put(r, f, value)
            ev = r.setdefault("evidence", {}).setdefault(g, [])
            known = {(e["url"], e["quote"]) for e in ev}
            ev += [e for e in ver if (e["url"], e["quote"]) not in known]
            r.setdefault("confidence", {})[g] = d.get("confidence", "medium")
            stats["resolved"] += 1
        if ans.get("access_notes") and "access" in fields:
            r["access_notes"] = ans["access_notes"]
        if ans.get("rationale"):
            r.setdefault("buildability", {})["rationale"] = ans["rationale"][:300]
        if ans.get("needs_human_reason"):
            r["needs_human"] = True
            r["needs_human_reason"] = ((r.get("needs_human_reason") or "") + "; " + ans["needs_human_reason"]).strip("; ")
        out.append(r)
    return out, stats, queue


def write_queue(queue: list[dict], records: list[dict]) -> Path:
    p = cache.DATA / "human_queue.md"
    lines = ["# Human queue", "", "Fields the agent could not settle with verified evidence after L5 (plus records flagged needs_human).", "",
             "| app | field | current value | why | docs |", "|---|---|---|---|---|"]
    for q in queue:
        lines.append(f"| {q['name']} | {q['field']} | `{q.get('current')}`{' (proposed `'+str(q['proposed'])+'`)' if q.get('proposed') else ''} | {q['why'][:120]} | {q.get('docs_url') or ''} |")
    other = [r for r in records if r.get("needs_human") and r["id"] not in {q["id"] for q in queue}]
    if other:
        lines += ["", "## Other needs_human records", ""]
        lines += [f"- **{r['name']}**: {(r.get('needs_human_reason') or '')[:200]}" for r in other]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p
