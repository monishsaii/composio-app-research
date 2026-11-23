"""L4: browser verification for the ~15 hardest apps.

Hardness score = 2*(L1 groups reset) + unsupported/unfetchable evidence + disputes + 2*(access unknown/low conf)
+ 1 if the app carries a known ambiguity. For each selected app we render (Playwright) its docs_url, every cited-but-
unfetchable URL, and every dropped-evidence URL (<=5 per app), save screenshot + text, then:
  * re-check dropped evidence against the rendered text; restore it (and any L1-reset values) if it now matches;
  * write rendered text into the fetch cache when it is richer than the plain-HTTP text (so L5 sees JS-rendered docs).
"""
from __future__ import annotations

import copy

from .. import cache
from ..apps import BY_ID
from ..tools import browser
from ..tools import composio_tools as web
from . import l1_evidence as L1

N_HARDEST = 15


def hardness(r: dict) -> int:
    s = 2 * len(r.get("l1_removed", {}))
    s += len(r.get("l1_dropped_evidence", []))
    s += len(r.get("disputes", []))
    if r.get("access") == "unknown" or (r.get("confidence") or {}).get("access") == "low":
        s += 2
    if BY_ID[r["id"]].get("ambiguity"):
        s += 1
    return s


def select(records: list[dict], n: int = N_HARDEST) -> list[str]:
    ranked = sorted(records, key=lambda r: (-hardness(r), r["id"]))
    return [r["id"] for r in ranked[:n] if hardness(r) > 0]


def run(records: list[dict], ids: list[str]) -> tuple[list[dict], dict]:
    out, stats = [], {"apps": len(ids), "pages": 0, "restored_evidence": 0, "restored_groups": 0, "cache_upgrades": 0}
    for r in records:
        r = copy.deepcopy(r)
        if r["id"] not in ids:
            out.append(r)
            continue
        urls = []
        if r.get("docs_url"):
            urls.append(r["docs_url"])
        urls += [e["url"] for e in r.get("l1_dropped_evidence", [])]
        urls += [e["url"] for evs in r.get("evidence", {}).values() for e in evs if e.get("support") == "unfetchable"]
        urls = list(dict.fromkeys(urls))[:5]
        rendered = {}
        for i, u in enumerate(urls):
            b = browser.render(u, r["id"], i)
            stats["pages"] += 1
            rendered[u] = b
            plain = web.fetch(u)
            if b.get("status") == 200 and len(b.get("text", "")) > 1.5 * len(plain.get("text", "")) + 200:
                cache.put("fetch", cache.key("fetch", u), {**plain, "text": b["text"], "status": 200,
                                                          "via": "playwright:chromium", "fetched_at": b["fetched_at"]})
                stats["cache_upgrades"] += 1
        r["browser_evidence"] = [{"url": u, "status": b.get("status"), "screenshot": b.get("screenshot"),
                                  "chars": len(b.get("text", "")), "fetched_at": b.get("fetched_at")} for u, b in rendered.items()]
        keep_dropped = []
        for e in r.get("l1_dropped_evidence", []):
            if e.get("claim_check") in ("irrelevant", "contradicts"):  # dropped for meaning, not page access
                keep_dropped.append(e)
                continue
            b = rendered.get(e["url"])
            kind = L1.match(e["quote"], b["text"])[0] if b and b.get("text") else "unsupported"
            if kind in ("exact", "fuzzy"):
                g = e.pop("group")
                r.setdefault("evidence", {}).setdefault(g, []).append({**e, "support": f"browser_{kind}", "fetched_at": b["fetched_at"]})
                stats["restored_evidence"] += 1
                if g in r.get("l1_removed", {}):
                    r.update(r["l1_removed"].pop(g))
                    r.setdefault("flags", []).append(f"L4 restored {g} via rendered page")
                    stats["restored_groups"] += 1
            else:
                keep_dropped.append(e)
        r["l1_dropped_evidence"] = keep_dropped
        r.setdefault("flags", []).append("L4 browser-verified")
        out.append(r)
    return out, stats
