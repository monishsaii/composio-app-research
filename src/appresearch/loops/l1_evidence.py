"""L1 evidence validator.

For every evidence item: RE-FETCH the cited URL (force), then
  exact   : normalised quote is a substring of normalised page text
  fuzzy   : rapidfuzz partial_ratio >= 85 against the page
  else    : queued for an LLM entailment check (Sonnet tier) on the best-matching page window
            -> entailed | unsupported
  unfetchable: page could not be fetched (status != 200 or empty) -> queued for entailment against cached copy if any,
            else unsupported.
Groups left with zero supported evidence have their claimed values reset to "unknown" (non-negotiable rule 1);
the removed values are kept in rec["l1_removed"] so L5 can re-research them.
"""
from __future__ import annotations

import copy
import json
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor

from rapidfuzz import fuzz

from .. import cache
from ..tools import composio_tools as web

THRESH = 85
ENTAIL_STAGE = "l1_entail"
TASKS = cache.CACHE / "llm" / "tasks" / ENTAIL_STAGE
RESP = cache.CACHE / "llm" / "responses" / ENTAIL_STAGE


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = re.sub(r"[`*_#>\[\]\(\)|]", " ", s)
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


def best_window(text: str, quote: str, width: int = 1500) -> str:
    """Locate the region of `text` most similar to `quote` (for the entailment prompt)."""
    t = text or ""
    if not t:
        return ""
    words = [w for w in re.findall(r"[A-Za-z0-9]{4,}", quote)][:12]
    best, best_i = -1, 0
    for i in range(0, max(1, len(t) - width), width // 3):
        seg = t[i : i + width].lower()
        sc = sum(1 for w in words if w.lower() in seg)
        if sc > best:
            best, best_i = sc, i
    return t[best_i : best_i + width]


def match(quote: str, text: str) -> tuple[str, int]:
    q, t = norm(quote), norm(text)
    if not q:
        return "unsupported", 0
    if q in t:
        return "exact", 100
    score = int(fuzz.partial_ratio(q, t)) if len(t) < 400_000 else 0
    return ("fuzzy", score) if score >= THRESH else ("pending", score)


def refetch_all(records: list[dict]) -> None:
    urls = sorted({e["url"] for r in records for g, evs in r.get("evidence", {}).items() if g != "composio" for e in evs})
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(lambda u: web.fetch(u, force=True), urls))
    print(f"  L1 re-fetched {len(urls)} unique URLs")


def first_pass(records: list[dict], refetch: bool = True) -> tuple[list[dict], dict]:
    """String-match every evidence item; emit entailment tasks for the rest."""
    if refetch:
        refetch_all(records)
    TASKS.mkdir(parents=True, exist_ok=True)
    out, stats = [], {"exact": 0, "fuzzy": 0, "pending": 0, "unfetchable": 0}
    for r in records:
        r = copy.deepcopy(r)
        pend = []
        for g, evs in r.get("evidence", {}).items():
            if g == "composio":  # catalog evidence is generated from SDK data, not a page quote
                for e in evs:
                    e["support"] = "sdk_catalog"
                continue
            for i, e in enumerate(evs):
                page = web.fetch(e["url"])  # cached (just re-fetched)
                if page.get("status") != 200 or len(page.get("text", "")) < 50:
                    e["support"] = "unfetchable"
                    stats["unfetchable"] += 1
                    pend.append((g, i, e, ""))
                    continue
                kind, score = match(e["quote"], page["text"])
                e["support"], e["match_score"] = kind, score
                stats[kind] += 1
                if kind == "pending":
                    pend.append((g, i, e, best_window(page["text"], e["quote"])))
        if pend:
            lines = [(TASK_HEADER)]
            for g, i, e, window in pend:
                lines.append(f"\n### ITEM {g}#{i}\nURL: {e['url']}\nCLAIMED QUOTE/PARAPHRASE: {e['quote']}\n"
                             f"FIELD GROUP: {g}\nPAGE WINDOW (best match):\n{window or '(page not fetchable)'}\n")
            (TASKS / f"{r['id']}.md").write_text("".join(lines), encoding="utf-8")
        out.append(r)
    return out, stats


TASK_HEADER = """# l1_entail v1 — evidence entailment check
For each ITEM decide whether the PAGE WINDOW supports the CLAIMED QUOTE/PARAPHRASE (same meaning; wording may differ).
If the window is empty or unrelated, answer unsupported. Output ONLY JSON: {"<group>#<index>": "entailed"|"unsupported", ...}
"""

GROUP_FIELDS = {
    "auth": {"auth_methods": [], "oauth_details": None},
    "access": {"access": "unknown"},
    "sandbox": {"sandbox_or_test_env": "unknown"},
    "mcp": {"mcp": {"exists": "unknown", "url": None}},
    "api_surface": {"api_surface": {"style": [], "breadth": "unknown", "approx_endpoint_count": None, "webhooks": "unknown",
                                    "pagination_documented": "unknown", "rate_limits_documented": "unknown", "official_sdks": []}},
}


def finalize(records: list[dict]) -> tuple[list[dict], dict]:
    """Apply entailment answers; drop unsupported evidence; reset unsupported claims to unknown."""
    out, stats = [], {"entailed": 0, "unsupported": 0, "groups_reset": 0}
    for r in records:
        r = copy.deepcopy(r)
        ans = {}
        p = RESP / f"{r['id']}.json"
        if p.exists():
            try:
                txt = p.read_text(encoding="utf-8")
                ans = json.loads(txt[txt.find("{") : txt.rfind("}") + 1])
            except Exception:
                ans = {}
        for g, evs in list(r.get("evidence", {}).items()):
            keep = []
            for i, e in enumerate(evs):
                if e.get("support") in ("pending", "unfetchable"):
                    e["support"] = "entailed" if ans.get(f"{g}#{i}") == "entailed" else "unsupported"
                    stats[e["support"]] += 1
                if e.get("support") != "unsupported":
                    keep.append(e)
                else:
                    r.setdefault("l1_dropped_evidence", []).append({**e, "group": g})
            r["evidence"][g] = keep
            if not keep and g in GROUP_FIELDS:
                removed = {k: r.get(k) for k in GROUP_FIELDS[g]}
                claimed = any(v not in (None, "unknown", [], {"exists": "unknown", "url": None}) for k, v in removed.items() if k != "api_surface")
                if "api_surface" in removed:
                    claimed = (removed["api_surface"] or {}).get("breadth", "unknown") != "unknown"
                if "mcp" in removed:  # "none_found" is an absence finding, not a claim needing a quote
                    claimed = (removed["mcp"] or {}).get("exists") in ("official", "community")
                if claimed:
                    r.setdefault("l1_removed", {})[g] = removed
                    r.update(copy.deepcopy(GROUP_FIELDS[g]))
                    r.setdefault("flags", []).append(f"L1 reset {g} to unknown: no supported evidence")
                    r.setdefault("confidence", {})[g] = "low"
                    r["needs_human"] = True
                    stats["groups_reset"] += 1
        out.append(r)
    return out, stats
