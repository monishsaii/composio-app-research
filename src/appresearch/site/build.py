"""Build site/index.html: one self-contained page (inline CSS/JS/SVG, data embedded, no external requests)
plus site/findings.json, findings.csv, human_check.csv, llms.txt, schema.json."""
from __future__ import annotations

import csv
import html
import io
import json
import shutil
from pathlib import Path

from .. import cache, rubric
from ..schema import json_schema

SITE = cache.ROOT / "site"
TEMPLATE = Path(__file__).parent / "template.html"


def _load(name, default=None):
    p = cache.DATA / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def slim(r: dict) -> dict:
    ev = {g: [{k: e.get(k) for k in ("url", "quote", "source_type", "fetched_at", "support")} for e in evs]
          for g, evs in (r.get("evidence") or {}).items()}
    return {
        "id": r["id"], "name": r["name"], "category": r["category"], "one_liner": r.get("one_liner"),
        "docs_url": r.get("docs_url"), "openapi_spec_url": r.get("openapi_spec_url"),
        "auth_methods": r.get("auth_methods") or [], "auth_notes": r.get("auth_notes"), "oauth": r.get("oauth_details"),
        "access": r["access"], "access_notes": r.get("access_notes"), "sandbox": r.get("sandbox_or_test_env"),
        "api": r.get("api_surface"), "mcp": r.get("mcp"), "b": r.get("buildability"),
        "composio": r.get("composio_existing_toolkit"), "evidence": ev, "confidence": r.get("confidence") or {},
        "needs_human": r.get("needs_human"), "needs_human_reason": r.get("needs_human_reason"),
        "flags": [f for f in r.get("flags", []) if not f.startswith("L4 browser")][:12],
        "browser": r.get("browser_evidence") or [],
    }


def run_stats() -> dict:
    runs = []
    p = cache.DATA / "agent_runs.jsonl"
    if p.exists():
        runs = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_stage = {}
    for r in runs:
        s = by_stage.setdefault(r["stage"], {"model": r["model"], "agents": 0, "tokens": 0, "minutes": 0.0})
        s["agents"] += 1
        s["tokens"] += r.get("tokens", 0)
        s["minutes"] += r.get("ms", 0) / 60000
    for s in by_stage.values():
        s["minutes"] = round(s["minutes"], 1)
    ev = {"search_composio": 0, "search_fallback": 0, "fetch_direct": 0, "fetch_composio": 0, "composio_errors": 0,
          "browser": 0, "normalize": 0, "retry": 0}
    ep = cache.CACHE / "events.jsonl"
    if ep.exists():
        for line in ep.read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            k = e.get("event")
            if k == "fallback":
                ev["search_fallback"] += 1
            elif k == "search" and str(e.get("via", "")).startswith("composio"):
                ev["search_composio"] += 1
            elif k == "fetch":
                ev["fetch_composio" if "composio" in e.get("via", "") else "fetch_direct"] += 1
            elif k == "composio_error":
                ev["composio_errors"] += 1
            elif k in ("browser", "normalize", "retry"):
                ev[k] += 1
    return {"by_stage": by_stage, "events": ev, "total_tokens": sum(r.get("tokens", 0) for r in runs),
            "agents": len(runs)}


def findings_csv(records) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "name", "category", "verdict", "main_blocker", "access", "auth_methods", "api_breadth", "webhooks",
                "mcp", "composio_toolkit", "docs_url", "access_notes", "needs_human"])
    for r in records:
        w.writerow([r["id"], r["name"], r["category"], r["buildability"]["verdict"], r["buildability"]["main_blocker"],
                    r["access"], "|".join(r.get("auth_methods") or []), (r.get("api_surface") or {}).get("breadth"),
                    (r.get("api_surface") or {}).get("webhooks"), (r.get("mcp") or {}).get("exists"),
                    r.get("composio_existing_toolkit"), r.get("docs_url") or "", r.get("access_notes") or "", r.get("needs_human")])
    return buf.getvalue()


def main() -> None:
    final = _load("final.json", [])
    analysis = _load("analysis.json", {})
    accuracy = _load("accuracy.json", {})
    split = _load("gold_split.json", {})
    timings = _load("timings.json", {})
    catalog = _load("composio_toolkits.json", {})
    SITE.mkdir(exist_ok=True)
    data = {
        "generated_at": cache.now_iso(), "research_date": "2026-11-23",
        "records": [slim(r) for r in final], "analysis": analysis, "accuracy": accuracy, "split": split,
        "runs": run_stats(), "timings": {k: round(sum(x["seconds"] for x in v)) for k, v in timings.items()},
        "composio_catalog_count": catalog.get("count"), "rubric": rubric.RUBRIC_TEXT,
        "headlines": analysis.get("headlines", []),
    }
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    n = len(final)
    jsonld = {
        "@context": "https://schema.org", "@type": "Dataset",
        "name": "Integration readiness of 100 SaaS apps for agent tool-calling",
        "description": f"Auth methods, credential access gates, API surface, MCP availability and a buildability verdict for {n} apps, "
                       "each non-unknown value backed by a cited source quote. Researched 2026-11-23.",
        "dateCreated": "2026-11-23", "variableMeasured": ["auth_methods", "access", "api_surface", "mcp", "buildability.verdict"],
        "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": "findings.json"},
                         {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": "findings.csv"}],
    }
    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("/*__DATA__*/", blob).replace("/*__JSONLD__*/", json.dumps(jsonld))
    (SITE / "index.html").write_text(page, encoding="utf-8")
    (SITE / "findings.json").write_text(json.dumps(final, ensure_ascii=False, indent=1), encoding="utf-8")
    (SITE / "findings.csv").write_text(findings_csv(final), encoding="utf-8")
    (SITE / "schema.json").write_text(json.dumps(json_schema(), indent=1), encoding="utf-8")
    if (cache.DATA / "human_check.csv").exists():
        shutil.copy(cache.DATA / "human_check.csv", SITE / "human_check.csv")
    (SITE / "llms.txt").write_text(llms_txt(final, analysis, accuracy), encoding="utf-8")
    size = (SITE / "index.html").stat().st_size
    print(f"site/index.html {size/1024:.0f} KB ({'OK' if size < 2_000_000 else 'TOO BIG'})")


def llms_txt(final, analysis, accuracy) -> str:
    v = analysis.get("verdicts", {})
    lines = ["# Integration readiness: 100 apps for agent tool-calling", "",
             "> For each app: auth methods, what gates API credentials, API surface, MCP server, and a rubric verdict. "
             "Every non-unknown value cites a URL + quote. Research date 2026-11-23. Agent: Claude Code subagents + Composio SDK.", "",
             "## Files", "- [findings.json](findings.json): full records with evidence", "- [findings.csv](findings.csv): one row per app",
             "- [schema.json](schema.json): JSON Schema of a record", "- [human_check.csv](human_check.csv): gold-sample human audit sheet", "",
             "## Verdict counts", *[f"- {k}: {c}" for k, c in v.items()], "", "## Headline findings",
             *[f"- {h['text']}" for h in analysis.get("headlines", [])], "", "## Apps",
             *[f"- {r['name']}: {r['buildability']['verdict']} (access {r['access']}; auth {'+'.join(r.get('auth_methods') or ['unknown'])})" for r in final]]
    return "\n".join(lines) + "\n"
