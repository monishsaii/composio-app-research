"""L2: independent adversarial second pass + field-level diff + evidence-gated merge.

Merge policy (deterministic): on a disagreement, the L2 value is adopted only if L2's evidence for that field group
string-matches its cited page (exact/fuzzy, same check as L1). Every disagreement is recorded in rec["disputes"]
for L5 adjudication regardless of which value was kept.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from pydantic import ValidationError

from .. import cache
from ..apps import BY_ID
from ..schema import Record
from ..tools import composio_tools as web
from . import l1_evidence as L1

STAGE = "l2"
TASKS = cache.CACHE / "llm" / "tasks" / STAGE
RESP = cache.CACHE / "llm" / "responses" / STAGE
PROMPT = Path(__file__).resolve().parents[1] / "prompts" / "l2_adversarial.md"

# field path -> evidence group
KEY_FIELDS = {
    "auth_methods": "auth", "access": "access", "sandbox_or_test_env": "sandbox",
    "api_surface.breadth": "api_surface", "api_surface.webhooks": "api_surface",
    "mcp.exists": "mcp", "buildability.main_blocker": "buildability", "buildability.verdict": "buildability",
}


def get(rec: dict, path: str):
    cur = rec
    for p in path.split("."):
        cur = (cur or {}).get(p) if isinstance(cur, dict) else None
    if isinstance(cur, list):
        return sorted(cur)
    return cur


def put(rec: dict, path: str, val) -> None:
    parts = path.split(".")
    cur = rec
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    cur[parts[-1]] = val


def queries(app: dict) -> list[str]:
    n = app["name"]
    # 2 queries/app (WebSearch is capped at 200 calls per Claude Code turn, shared by all subagents)
    return [f"{n} API access requirements which plan pricing developer app review partner",
            f"{n} API reference rate limits webhooks official MCP server"]


def emit(records: list[dict]) -> int:
    TASKS.mkdir(parents=True, exist_ok=True)
    prompt = PROMPT.read_text(encoding="utf-8")
    n = 0
    for r in records:
        app = BY_ID[r["id"]]
        used = sorted({e["url"] for evs in r.get("evidence", {}).values() for e in evs})
        slim = {k: v for k, v in r.items() if k not in ("evidence", "flags", "l1_dropped_evidence")}
        body = (f"{prompt}\n## App\nid: {app['id']}\nname: {app['name']}\ncategory: {app['category']}\n"
                f"hint_url (starting point only): {app.get('hint_url')}\nknown ambiguity: {app.get('ambiguity')}\n"
                f"\n## Suggested queries (run each)\n" + "\n".join(f"- {q}" for q in queries(app)) +
                f"\n\n## Pages the first pass already used (do NOT rely on these)\n" + "\n".join(used) +
                f"\n\n## First-pass record (try to prove it wrong)\n```json\n{json.dumps(slim, indent=1)}\n```\n")
        (TASKS / f"{app['id']}.md").write_text(body, encoding="utf-8")
        n += 1
    return n


def _load_l2(rid: str) -> dict | None:
    p = RESP / f"{rid}.json"
    if not p.exists():
        return None
    txt = p.read_text(encoding="utf-8")
    try:
        raw = json.loads(txt[txt.find("{") : txt.rfind("}") + 1])
    except ValueError:
        return None
    app = BY_ID[rid]
    raw.update(id=rid, name=app["name"], category=app["category"])
    for evs in (raw.get("evidence") or {}).values():
        for e in evs:
            e["fetched_at"] = web.fetch(e["url"])["fetched_at"]
            e.setdefault("source_type", "third_party")
    disputes = raw.pop("disputes", [])
    try:
        rec = Record.model_validate(raw).model_dump()
    except ValidationError as ex:
        cache.log_event("l2_invalid", id=rid, error=str(ex)[:300])
        return None
    rec["_l2_disputes"] = disputes
    return rec


def _verified(evs: list[dict]) -> list[dict]:
    ok = []
    for e in evs:
        page = web.fetch(e["url"])
        kind, score = L1.match(e.get("quote", ""), page.get("text", "")) if page.get("status") == 200 else ("unfetchable", 0)
        if kind in ("exact", "fuzzy"):
            ok.append({**e, "support": kind, "match_score": score, "from": "L2"})
    return ok


def merge(records: list[dict]) -> tuple[list[dict], dict, dict]:
    out, stats, l2_all = [], {"compared": 0, "agree": 0, "disagree": 0, "adopted_l2": 0, "missing_l2": 0}, {}
    for r in records:
        r = copy.deepcopy(r)
        l2 = _load_l2(r["id"])
        if l2 is None:
            stats["missing_l2"] += 1
            out.append(r)
            continue
        l2_all[r["id"]] = l2
        r["disputes"] = []
        for path, group in KEY_FIELDS.items():
            a, b = get(r, path), get(l2, path)
            stats["compared"] += 1
            if a == b:
                stats["agree"] += 1
                continue
            stats["disagree"] += 1
            ver = _verified((l2.get("evidence") or {}).get(group, []))
            adopted = bool(ver) and b not in (None, "unknown", [])
            r["disputes"].append({"field": path, "group": group, "pass1": a, "l2": b, "adopted_l2": adopted,
                                  "l2_evidence": ver or (l2.get("evidence") or {}).get(group, [])})
            if adopted:
                put(r, path, b)
                r.setdefault("evidence", {}).setdefault(group, [])
                known = {(e["url"], e["quote"]) for e in r["evidence"][group]}
                r["evidence"][group] += [e for e in ver if (e["url"], e["quote"]) not in known]
                if group == "auth" and l2.get("oauth_details"):
                    r["oauth_details"] = l2["oauth_details"]
                if group == "access":
                    r["access_notes"] = l2.get("access_notes") or r.get("access_notes")
                stats["adopted_l2"] += 1
        # agreement raises confidence; disagreement lowers it
        for path, group in KEY_FIELDS.items():
            conf = r.setdefault("confidence", {})
            if any(d["group"] == group for d in r["disputes"]):
                conf[group] = "low" if conf.get(group) != "high" else "medium"
            elif conf.get(group) in (None, "low", "medium") and (r.get("evidence") or {}).get(group):
                conf[group] = "high" if conf.get(group) == "medium" else "medium"
        # fill gaps the first pass left (docs_url, one_liner) only when empty
        for k in ("docs_url", "openapi_spec_url", "one_liner"):
            if not r.get(k) and l2.get(k):
                r[k] = l2[k]
        out.append(r)
    return out, stats, l2_all
