"""L3: deterministic rule checks. Pure functions over a record + an injected `fetch(url)->dict` (testable).

Each rule returns violations; some rules also apply a deterministic correction (recorded in rec["flags"]).
"""
from __future__ import annotations

import copy
import re
from typing import Callable
from urllib.parse import urlparse

from .. import rubric

Fetch = Callable[[str], dict]

DOCS_HINT = re.compile(r"(^|[./-])(docs?|developers?|dev|api|apis|reference|openapi|swagger|readme|help|support|learn|platform|open)([./-]|$)", re.I)
OAUTH_TERMS = re.compile(r"oauth|authorize|authorization code|access[_ ]token|token endpoint|/token|client[_ ]id|redirect", re.I)
PRICE_TERMS = re.compile(r"\$|€|£|price|pricing|plan|tier|subscription|per month|/mo|enterprise|paid|upgrade|billing", re.I)


def _host(u: str | None) -> str:
    if not u:
        return ""
    h = urlparse(u).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def _root(u: str | None) -> str:
    parts = _host(u).split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else _host(u)


def _ev(rec: dict, group: str) -> list[dict]:
    return (rec.get("evidence") or {}).get(group) or []


def _flag(rec: dict, msg: str) -> None:
    rec.setdefault("flags", [])
    if msg not in rec["flags"]:
        rec["flags"].append(msg)


def official_roots(rec: dict) -> set[str]:
    """Domains considered 'official' for this app: docs_url root + roots of official_* evidence."""
    roots = {_root(rec.get("docs_url"))}
    for evs in (rec.get("evidence") or {}).values():
        for e in evs:
            if e.get("source_type") in ("official_docs", "pricing_page"):
                roots.add(_root(e["url"]))
    roots.discard("")
    return roots


def name_tokens(rec: dict) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", rec["name"].lower()) if len(t) > 2]


# ------------------------------------------------------------------ rules
def r_oauth_has_endpoints(rec: dict, fetch: Fetch) -> list[str]:
    if "oauth2" not in (rec.get("auth_methods") or []):
        return []
    quotes = " ".join(e.get("quote", "") for e in _ev(rec, "auth"))
    if OAUTH_TERMS.search(quotes):
        if rec.get("oauth_details") is None:
            rec["oauth_details"] = {"flows": [], "scopes_granular": "unknown", "app_review_required": "unknown"}
        return []
    # look at the cited auth pages themselves
    for e in _ev(rec, "auth"):
        if OAUTH_TERMS.search(fetch(e["url"]).get("text", "")[:200_000] or ""):
            return []
    rec.setdefault("confidence", {})["auth"] = "low"
    return ["oauth2 claimed but no authorize/token evidence on cited auth pages"]


def r_paid_needs_pricing(rec: dict, fetch: Fetch) -> list[str]:
    if rec.get("access") != "paid_plan_required":
        return []
    evs = _ev(rec, "access")
    if any(e.get("source_type") == "pricing_page" for e in evs) or any(PRICE_TERMS.search(e.get("quote", "")) for e in evs):
        return []
    rec.setdefault("confidence", {})["access"] = "low"
    return ["paid_plan_required without pricing evidence"]


def r_mcp_official(rec: dict, fetch: Fetch) -> list[str]:
    m = rec.get("mcp") or {}
    if m.get("exists") != "official":
        if m.get("exists") == "community" and not m.get("url"):
            return ["mcp community claimed without url"]
        return []
    url = m.get("url")
    if not url:
        rec["mcp"]["exists"] = "unknown"
        return ["mcp official without url -> unknown"]
    r = fetch(url)
    if r.get("status") not in (200, 401, 403):  # 401/403: protected MCP endpoints legitimately reject GET
        rec["mcp"]["exists"] = "unknown"
        return [f"mcp url does not resolve (status {r.get('status')}) -> unknown"]
    host, roots = _host(url), official_roots(rec)
    on_official = _root(url) in roots
    if not on_official and host in ("github.com", "www.github.com"):
        org = urlparse(url).path.strip("/").split("/")[0].lower()
        on_official = any(t in org for t in name_tokens(rec))
    if not on_official and any(t in host.replace("-", "") for t in name_tokens(rec)):
        on_official = True
    if not on_official:
        rec["mcp"]["exists"] = "community"
        return [f"mcp 'official' but {host} not an official domain -> community"]
    return []


def r_docs_url(rec: dict, fetch: Fetch) -> list[str]:
    u = rec.get("docs_url")
    if not u:
        return [] if rec.get("access") in ("no_public_api", "unknown") else ["docs_url missing"]
    r = fetch(u)
    out = []
    if r.get("status") not in (200,):
        out.append(f"docs_url status {r.get('status')}")
    final = r.get("final_url") or u
    if not (DOCS_HINT.search(_host(final)) or DOCS_HINT.search(urlparse(final).path) or "github.com" in final):
        out.append("docs_url looks like a marketing page")
    return out


def r_breadth_vs_count(rec: dict, fetch: Fetch) -> list[str]:
    api = rec.get("api_surface") or {}
    n = api.get("approx_endpoint_count")
    if not n:
        return []
    want = "broad" if n > 100 else "medium" if n >= 20 else "narrow"
    if api.get("breadth") != want:
        old = api.get("breadth")
        api["breadth"] = want
        return [f"breadth {old} inconsistent with ~{n} endpoints -> {want}"]
    return []


def r_verdict_rubric(rec: dict, fetch: Fetch) -> list[str]:
    b = rec.setdefault("buildability", {})
    want = rubric.verdict(rec)
    if b.get("verdict") != want:
        old = b.get("verdict")
        b["verdict"] = want
        return [f"verdict {old} -> {want} per rubric"]
    return []


def r_low_conf_needs_human(rec: dict, fetch: Fetch) -> list[str]:
    conf = rec.get("confidence") or {}
    if conf.get("access") == "low" or rec.get("access") == "unknown":
        rec["needs_human"] = True
        if "access low-confidence/unknown" not in (rec.get("needs_human_reason") or ""):
            rec["needs_human_reason"] = ((rec.get("needs_human_reason") or "") + "; access low-confidence/unknown").strip("; ")
    return []


RULES = [r_oauth_has_endpoints, r_paid_needs_pricing, r_mcp_official, r_docs_url, r_breadth_vs_count,
         r_verdict_rubric, r_low_conf_needs_human]


def check(rec: dict, fetch: Fetch) -> tuple[dict, list[str]]:
    rec = copy.deepcopy(rec)
    violations = []
    for rule in RULES:
        for v in rule(rec, fetch):
            violations.append(f"{rule.__name__}: {v}")
            _flag(rec, f"L3 {v}")
    return rec, violations
