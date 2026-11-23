"""Human checkpoint: human_check.csv/.md for the gold sample + blind LLM-auditor tasks (labelled NOT ground truth).

The human columns (human_value, human_correct, note) are left EMPTY. Never filled by the agent.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from . import cache, research, split
from .apps import BY_ID
from .loops.l2_second_pass import get

KEY_FIELDS = ["auth_methods", "access", "api_surface.breadth", "mcp.exists", "buildability.main_blocker", "buildability.verdict"]
GROUP = {"auth_methods": "auth", "access": "access", "api_surface.breadth": "api_surface", "mcp.exists": "mcp",
         "buildability.main_blocker": "access", "buildability.verdict": "access"}
CSV = cache.DATA / "human_check.csv"
AUD_TASKS = cache.CACHE / "llm" / "tasks" / "auditor"
PROMPT = Path(__file__).parent / "prompts" / "auditor.md"
COLS = ["split", "app_id", "app", "field", "agent_value", "doc_link", "evidence_url", "evidence_quote",
        "human_value", "human_correct", "note"]


def fmt(v) -> str:
    if isinstance(v, list):
        return "|".join(v)
    return "" if v is None else str(v)


def main() -> None:
    sp = split.load()
    final = {r["id"]: r for r in research.load("final.json")}
    if CSV.exists():
        with CSV.open(encoding="utf-8") as f:
            if any((row.get("human_correct") or "").strip() for row in csv.DictReader(f)):
                print("human_check.csv already has human answers -> not overwriting")
                return
    rows = []
    for part in ("test", "dev"):
        for aid in sp[part]:
            r = final[aid]
            for fld in KEY_FIELDS:
                ev = (r.get("evidence") or {}).get(GROUP[fld]) or []
                rows.append({"split": part.upper(), "app_id": aid, "app": r["name"], "field": fld,
                             "agent_value": fmt(get(r, fld)), "doc_link": r.get("docs_url") or "",
                             "evidence_url": ev[0]["url"] if ev else "", "evidence_quote": ev[0]["quote"] if ev else "",
                             "human_value": "", "human_correct": "", "note": ""})
    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    md = ["# Human check (gold sample)", "",
          "Fill `human_correct` with Y or N for each row. If N, put the right value in `human_value` (same enum). Add a `note` if useful.",
          "Open `doc_link` / `evidence_url` to check. Edit the CSV, not this file. TEST rows (20 apps) come first; DEV rows (10 apps) follow.", "",
          "Enums: access = self_serve_free | self_serve_trial | paid_plan_required | admin_approval | app_review_required | partner_or_contact_sales | no_public_api | unknown;",
          "verdict = BUILD_NOW | BUILD_WITH_CAVEATS | BLOCKED_NEEDS_OUTREACH | BLOCKED_NO_PUBLIC_API | NOT_APPLICABLE_NOT_A_SERVICE | UNCLEAR;",
          "breadth = broad(>100) | medium(20-100) | narrow(<20) | none | unknown; mcp = official | community | none_found | unknown.", ""]
    cur = None
    for row in rows:
        if row["app_id"] != cur:
            cur = row["app_id"]
            md += ["", f"## {row['app']} ({row['split']})  [docs]({row['doc_link']})", "", "| field | agent value | evidence |", "|---|---|---|"]
        md.append(f"| {row['field']} | `{row['agent_value']}` | [{row['evidence_quote'][:80]}]({row['evidence_url']}) |")
    (cache.DATA / "human_check.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {CSV} ({len(rows)} rows), human_check.md; auditor tasks: {emit_auditor()}")


def emit_auditor() -> int:
    """Blind auditor tasks: app name only, never the agent's answers."""
    sp = split.load()
    AUD_TASKS.mkdir(parents=True, exist_ok=True)
    prompt = PROMPT.read_text(encoding="utf-8")
    for aid in sp["test"] + sp["dev"]:
        a = BY_ID[aid]
        (AUD_TASKS / f"{aid}.md").write_text(f"{prompt}\n## App\nid: {aid}\nname: {a['name']}\ncategory: {a['category']}\n"
                                              f"known ambiguity: {a.get('ambiguity')}\n", encoding="utf-8")
    return len(sp["test"]) + len(sp["dev"])


def apply_overrides() -> int:
    """final.json = agent output (after_L5.json) + human corrections from human_check.csv (N rows with a value),
    verdict recomputed by the rubric. Overrides are labelled; the agent snapshot stays untouched for scoring."""
    import copy

    from . import rubric
    from .loops.l2_second_pass import put

    recs = {r["id"]: r for r in research.load("after_L5.json")}
    n = 0
    if CSV.exists():
        with CSV.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if not (row.get("human_correct") or "").strip().upper().startswith("N") or not row.get("human_value", "").strip():
                    continue
                r = recs[row["app_id"]]
                v = row["human_value"].strip()
                old = get(r, row["field"])
                val = sorted(x for x in v.replace(",", "|").split("|") if x) if row["field"] == "auth_methods" else v
                put(r, row["field"], val)
                group = GROUP[row["field"]] if row["field"] != "buildability.main_blocker" else "buildability"
                r.setdefault("evidence", {}).setdefault(group, []).append(
                    {"url": r.get("docs_url") or "", "quote": f"Human reviewer correction: {old} -> {v}. {row.get('note', '')}"[:200],
                     "source_type": "none", "fetched_at": "2026-11-23", "support": "human_review"})
                r.setdefault("flags", []).append(f"HUMAN {row['field']}: {old} -> {v}")
                r.setdefault("human_overrides", []).append({"field": row["field"], "agent": old, "human": v, "note": row.get("note", "")})
                n += 1
    for r in recs.values():
        if r.get("human_overrides"):
            r["buildability"]["verdict"] = rubric.verdict(r)
    research.save("final.json", list(recs.values()))
    return n


def load_human() -> dict:
    """{(app_id, field): gold_value} from filled rows. Y -> agent value is gold; N -> human_value is gold."""
    gold = {}
    if not CSV.exists():
        return gold
    with CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            c = (row.get("human_correct") or "").strip().upper()
            if c.startswith("Y"):
                gold[(row["app_id"], row["field"])] = row["agent_value"]
            elif c.startswith("N") and row.get("human_value", "").strip():
                gold[(row["app_id"], row["field"])] = row["human_value"].strip()
    return gold


def load_auditor() -> dict:
    out = {}
    d = cache.CACHE / "llm" / "responses" / "auditor"
    for p in sorted(d.glob("*.json")) if d.exists() else []:
        txt = p.read_text(encoding="utf-8")
        try:
            j = json.loads(txt[txt.find("{") : txt.rfind("}") + 1])
        except ValueError:
            continue
        for fld in KEY_FIELDS:
            if fld in j and isinstance(j[fld], dict):
                out[(p.stem, fld)] = fmt(sorted(j[fld]["value"]) if isinstance(j[fld].get("value"), list) else j[fld].get("value"))
    return out
