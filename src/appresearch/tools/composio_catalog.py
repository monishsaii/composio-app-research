"""Composio toolkit catalog (via Composio SDK) -> deterministic `composio_existing_toolkit`.

Matching is by normalised slug/name against an explicit alias table; every match is recorded with the
catalog entry's slug + tool count as evidence (https://composio.dev/toolkits/<slug>).
"""
from __future__ import annotations

import json
import os
import re

from .. import cache

CATALOG = cache.DATA / "composio_toolkits.json"

# app id -> candidate Composio slugs (checked in order). Only used to *look up*; absence => False.
ALIASES = {
    "zoho-crm": ["zoho", "zoho_crm"], "close": ["close"], "help-scout": ["help_scout", "helpscout"],
    "lark-larksuite": ["lark", "larksuite", "feishu"], "whatsapp-business": ["whatsapp"],
    "google-ads": ["googleads", "google_ads"], "meta-ads": ["metaads", "facebook_ads", "meta_ads", "facebook"],
    "linkedin-ads": ["linkedin_ads", "linkedinads"], "gohighlevel": ["gohighlevel", "highlevel_location", "highlevel_agency", "highlevel_mcp"],
    "threads-meta": ["threads"], "salesforce-commerce-cloud": ["salesforce_commerce_cloud", "sfcc"],
    "magento-adobe-commerce": ["magento", "adobe_commerce"], "amazon-selling-partner": ["amazon_selling_partner", "amazon_sp_api", "amazon_seller"],
    "se-ranking": ["se_ranking", "seranking"], "bright-data": ["brightdata", "bright_data"], "waterfall-io": ["waterfall", "waterfall_io"],
    "mongodb-atlas": ["mongodb_atlas", "mongodb"], "monday-com": ["monday", "monday_com"], "systeme-io": ["systeme_io", "systeme"],
    "paygent-connect": ["paygent", "paygent_connect", "nmi"], "otter-ai": ["otter", "otter_ai", "otter_ai_mcp"], "mermaid-cli": ["mermaid", "mermaid_cli"],
    "youtube-transcript": ["transcriptapi", "youtube_transcript"], "notebooklm": ["notebooklm", "notebook_lm"],
    "mrscraper": ["mrscraper", "mr_scraper"], "ipayx": ["ipayx"], "quickbooks": ["quickbooks"],
}


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def refresh() -> list[dict]:
    from composio import Composio

    c = Composio(api_key=os.environ["COMPOSIO_API_KEY"])
    items, cursor = [], None
    while True:
        r = c.client.toolkits.list(limit=1000, cursor=cursor) if cursor else c.client.toolkits.list(limit=1000)
        for it in r.items:
            d = it.model_dump()
            meta = d.get("meta") or {}
            items.append({"slug": d["slug"], "name": d.get("name"), "auth_schemes": d.get("auth_schemes"),
                          "no_auth": d.get("no_auth"), "tools_count": meta.get("tools_count"),
                          "triggers_count": meta.get("triggers_count"), "version": meta.get("version"),
                          "app_url": meta.get("app_url")})
        cursor = r.next_cursor
        if not cursor or not r.items:
            break
    out = {"fetched_at": cache.now_iso(), "count": len(items), "via": "composio-sdk client.toolkits.list", "items": items}
    CATALOG.write_text(json.dumps(out, indent=1), encoding="utf-8")
    cache.log_event("composio_catalog", count=len(items))
    return items


def load() -> dict:
    if not CATALOG.exists():
        refresh()
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def lookup(app: dict) -> dict | None:
    cat = load()
    by_slug = {norm(i["slug"]): i for i in cat["items"]}
    by_name = {norm(i["name"] or ""): i for i in cat["items"]}
    base = ALIASES.get(app["id"], []) + [app["id"], app["name"]]
    # Composio also lists hosted-MCP wrappers as "<slug>_mcp" (e.g. netlify_mcp, pylon_mcp, devin_mcp).
    # NOT applied to mermaid-cli: "mermaid_chart_mcp" is Mermaid Chart (SaaS), a different product.
    cands = base + ([f"{c}_mcp" for c in base] if app["id"] != "mermaid-cli" else [])
    for c in cands:
        hit = by_slug.get(norm(c)) or by_name.get(norm(c))
        if hit:
            return hit
    return None


def evidence_for(app: dict) -> tuple[bool, list[dict]]:
    cat = load()
    hit = lookup(app)
    if hit:
        return True, [{"url": f"https://composio.dev/toolkits/{hit['slug']}",
                       "quote": f"Composio catalog entry '{hit['slug']}' ({hit['name']}), {int(hit['tools_count'] or 0)} tools, auth {hit['auth_schemes']}",
                       "source_type": "official_docs", "fetched_at": cat["fetched_at"]}]
    return False, [{"url": "https://composio.dev/toolkits", "quote": f"No matching slug among {cat['count']} toolkits returned by Composio SDK toolkits.list",
                    "source_type": "official_docs", "fetched_at": cat["fetched_at"]}]
