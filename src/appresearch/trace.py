"""Single-app execution trace assembled from saved artifacts (search cache, fetch cache, task/response files, snapshots)."""
from __future__ import annotations

import json

from . import cache, research
from .apps import BY_ID
from .loops import l2_second_pass as L2
from .tools import composio_tools as web

FIELDS = ["auth_methods", "access", "sandbox_or_test_env", "api_surface.breadth", "mcp.exists",
          "buildability.main_blocker", "buildability.verdict"]


def _search(q: str) -> dict | None:
    return cache.get("search", web.search_key(q))


def write(aid: str) -> str:
    app = BY_ID[aid]
    snaps = {}
    for name, fn in (("pass1", "pass1.json"), ("L1", "after_L1.json"), ("L2", "after_L2.json"), ("L3", "after_L3.json"),
                     ("L4", "after_L4.json"), ("final", "final.json")):
        try:
            snaps[name] = {r["id"]: r for r in research.load(fn)}.get(aid)
        except FileNotFoundError:
            pass
    L = [f"# Execution trace: {app['name']}", "",
         "Assembled by `python -m appresearch trace --app \"%s\"` from saved artifacts. LLM steps were executed by Claude Code"
         " subagents (pass 1: Haiku; L2/L1-entailment: Sonnet; L5: Opus). Search: Composio COMPOSIO_SEARCH attempted first"
         " (HTTP 410 retired) -> Claude Code WebSearch, recorded into the cache." % app["name"], ""]
    from . import research as R

    L += ["## 1. Pass-1 searches", ""]
    for q in R.pass1_queries(app):
        s = _search(q)
        L.append(f"**`{q}`** — via `{(s or {}).get('via')}` at {(s or {}).get('at')}")
        for x in (s or {}).get("results", [])[:8]:
            L.append(f"  - {x['url']}")
        L.append("")
    task = cache.CACHE / "llm" / "tasks" / "pass1" / f"{aid}.md"
    pages = [ln[4:] for ln in task.read_text(encoding="utf-8").splitlines() if ln.startswith("### PAGE")] if task.exists() else []
    L += ["## 2. Pages fetched for pass 1 (<=5)", ""] + [f"- {p}" for p in pages] + [""]
    resp = cache.CACHE / "llm" / "responses" / "pass1" / f"{aid}.json"
    if resp.exists():
        L += ["## 3. Pass-1 extraction (raw subagent output, Haiku)", "", "```json", resp.read_text(encoding="utf-8")[:6000], "```", ""]
    if snaps.get("L1"):
        L += ["## 4. L1 evidence validation (re-fetch + fuzzy match + entailment)", "", "| group | url | support | score |", "|---|---|---|---|"]
        for g, evs in snaps["L1"].get("evidence", {}).items():
            for e in evs:
                L.append(f"| {g} | {e['url']} | {e.get('support')} | {e.get('match_score', '')} |")
        for e in snaps["L1"].get("l1_dropped_evidence", []):
            L.append(f"| {e['group']} | {e['url']} | **dropped: {e.get('support')}** | {e.get('match_score', '')} |")
        L += ["", f"Groups reset to unknown: `{list(snaps['L1'].get('l1_removed', {}).keys())}`", ""]
    if snaps.get("L2"):
        L += ["## 5. L2 adversarial pass (Sonnet) — disputes", ""]
        for d in snaps["L2"].get("disputes", []):
            L.append(f"- `{d['field']}`: pass1 `{d['pass1']}` vs L2 `{d['l2']}` -> adopted L2: {d['adopted_l2']}")
        L.append("")
    if snaps.get("L3"):
        L += ["## 6. L3 rule checks", ""] + [f"- {f}" for f in snaps["L3"].get("flags", []) if f.startswith("L3")] + [""]
    if snaps.get("L4") and snaps["L4"].get("browser_evidence"):
        L += ["## 7. L4 browser verification", ""] + [f"- {b['url']} status {b['status']} screenshot `{b['screenshot']}`" for b in snaps["L4"]["browser_evidence"]] + [""]
    if snaps.get("final"):
        f = snaps["final"]
        L += ["## 8. L5 adjudication + final", ""] + [f"- {x}" for x in f.get("flags", []) if x.startswith("L5")] + [""]
        L += ["| field | pass1 | final |", "|---|---|---|"]
        for fld in FIELDS:
            L.append(f"| {fld} | `{L2.get(snaps['pass1'], fld) if snaps.get('pass1') else ''}` | `{L2.get(f, fld)}` |")
        L += ["", "### Final record", "", "```json", json.dumps(f, indent=1, ensure_ascii=False)[:12000], "```"]
    out = cache.DATA / "traces" / f"{aid}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    return str(out)
