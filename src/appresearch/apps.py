"""The 100 apps under study. Hints are starting points only, NOT answers."""
from __future__ import annotations

import re

CATEGORIES = {
    "crm": "CRM & Sales",
    "support": "Support & Helpdesk",
    "comms": "Comms & Messaging",
    "marketing": "Marketing/Ads/Email/Social",
    "ecommerce": "Ecommerce",
    "data": "Data/SEO/Scraping",
    "dev": "Dev/Infra/Data",
    "productivity": "Productivity/PM",
    "finance": "Finance/Fintech",
    "ai": "AI/Research/Media",
}

# (name, category_key, hint, ambiguity_note)
_RAW = [
    ("Salesforce", "crm", None, None),
    ("HubSpot", "crm", None, None),
    ("Pipedrive", "crm", None, None),
    ("Attio", "crm", None, None),
    ("Twenty", "crm", None, "Open-source CRM (twenty.com); self-host vs cloud API."),
    ("Podio", "crm", None, None),
    ("Zoho CRM", "crm", None, None),
    ("Close", "crm", None, "close.com CRM; generic name."),
    ("Copper", "crm", None, None),
    ("DealCloud", "crm", None, "Intapp DealCloud; API existence/tier unclear."),
    ("Zendesk", "support", None, None),
    ("Intercom", "support", None, None),
    ("Freshdesk", "support", None, None),
    ("Front", "support", None, None),
    ("Pylon", "support", None, "usepylon.com B2B support; API tier unclear."),
    ("LiveAgent", "support", None, None),
    ("Plain", "support", None, "plain.com support; GraphQL API."),
    ("Help Scout", "support", None, None),
    ("Gorgias", "support", None, None),
    ("Gladly", "support", None, "API existence/tier unclear."),
    ("Slack", "comms", None, None),
    ("Twilio", "comms", None, None),
    ("Zoho Cliq", "comms", None, None),
    ("Lark (Larksuite)", "comms", None, "Lark (intl) vs Feishu (CN) open platforms."),
    ("Pumble", "comms", None, None),
    ("Discord", "comms", None, None),
    ("Telegram", "comms", None, "Bot API vs MTProto client API."),
    ("WhatsApp Business", "comms", None, "Cloud API vs on-prem (sunset) vs BSP; Meta app review."),
    ("Aircall", "comms", None, None),
    ("Vonage", "comms", None, None),
    ("Google Ads", "marketing", None, "Developer token access levels."),
    ("Meta Ads", "marketing", None, "Marketing API; app review / access tiers."),
    ("LinkedIn Ads", "marketing", None, "Advertising API requires partner/access application."),
    ("GoHighLevel", "marketing", None, "API v2 / marketplace app; plan tiers."),
    ("Mailchimp", "marketing", None, "Marketing vs Transactional (Mandrill) APIs."),
    ("Klaviyo", "marketing", None, None),
    ("systeme.io", "marketing", None, "API existence/tier."),
    ("Pinterest", "marketing", None, "API v5; trial vs standard access."),
    ("Threads (Meta)", "marketing", None, "Threads API; Meta app review."),
    ("SendGrid", "marketing", None, None),
    ("Shopify", "ecommerce", None, None),
    ("WooCommerce", "ecommerce", None, "Self-hosted WordPress plugin; per-store REST API."),
    ("BigCommerce", "ecommerce", None, None),
    ("Salesforce Commerce Cloud", "ecommerce", None, "B2C Commerce SCAPI/OCAPI; per-instance auth."),
    ("Magento (Adobe Commerce)", "ecommerce", None, "Per-instance REST/GraphQL; self-hosted vs Adobe Commerce cloud."),
    ("Squarespace", "ecommerce", None, None),
    ("Ecwid", "ecommerce", None, None),
    ("Gumroad", "ecommerce", None, None),
    ("Amazon Selling Partner", "ecommerce", None, "SP-API developer registration; restricted roles."),
    ("fanbasis", "ecommerce", None, "Small creator-commerce platform; API existence unclear."),
    ("DataForSEO", "data", None, None),
    ("SE Ranking", "data", None, "API on paid plans only?"),
    ("Ahrefs", "data", None, "API on enterprise plan only?"),
    ("MrScraper", "data", None, None),
    ("Apify", "data", None, None),
    ("Firecrawl", "data", None, None),
    ("Bright Data", "data", None, None),
    ("Sherlock", "data", "https://github.com/sherlock-project/sherlock", "Local OSS CLI, not a hosted API."),
    ("Waterfall.io", "data", None, "Contact-enrichment API; existence/tier unclear."),
    ("Clay", "data", None, "clay.com; public API existence unclear."),
    ("GitHub", "dev", None, None),
    ("Vercel", "dev", None, None),
    ("Netlify", "dev", None, None),
    ("Cloudflare", "dev", None, None),
    ("Supabase", "dev", None, "Management API vs per-project API (PostgREST)."),
    ("Neo4j", "dev", None, "Drivers/Query API vs Aura management API."),
    ("Snowflake", "dev", None, "SQL API vs drivers; key-pair JWT."),
    ("MongoDB Atlas", "dev", None, "Atlas Admin API vs Data API (deprecated)."),
    ("Datadog", "dev", None, None),
    ("Sentry", "dev", None, None),
    ("Notion", "productivity", None, None),
    ("Airtable", "productivity", None, None),
    ("Linear", "productivity", None, None),
    ("Jira", "productivity", None, None),
    ("Asana", "productivity", None, None),
    ("Monday.com", "productivity", None, None),
    ("ClickUp", "productivity", None, None),
    ("Coda", "productivity", None, None),
    ("Smartsheet", "productivity", None, None),
    ("Harvest", "productivity", None, "getharvest.com time tracking."),
    ("Stripe", "finance", None, None),
    ("Plaid", "finance", None, None),
    ("Binance", "finance", None, "API key + HMAC; regional restrictions."),
    ("Paygent Connect", "finance", None, "NMI-powered gateway; verify which 'Paygent' (also a Japanese PSP)."),
    ("iPayX", "finance", "https://ipayx.ai/docs", "Unknown small product; verify."),
    ("QuickBooks", "finance", None, None),
    ("Xero", "finance", None, None),
    ("Brex", "finance", None, None),
    ("Ramp", "finance", None, None),
    ("PitchBook", "finance", None, "API is enterprise add-on?"),
    ("NotebookLM", "ai", "https://cloud.google.com/gemini", "Consumer app vs NotebookLM Enterprise API."),
    ("Otter AI", "ai", None, "Public API existence unclear."),
    ("Fathom", "ai", None, "fathom.video meeting notes; API existence unclear."),
    ("Consensus", "ai", None, "consensus.app research search; API tier unclear."),
    ("Reducto", "ai", None, None),
    ("Devin", "ai", None, "Cognition Devin API; plan tier."),
    ("higgsfield", "ai", "https://higgsfield.ai/cli", "Gen-media; CLI vs API."),
    ("Mermaid CLI", "ai", "https://github.com/mermaid-js/mermaid-cli", "Local OSS CLI, not a hosted API."),
    ("YouTube Transcript", "ai", "https://transcriptapi.com", "Third-party transcript API (transcriptapi.com), not YouTube itself."),
    ("Grain", "ai", None, "grain.com meeting recorder; API tier unclear."),
]


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


APPS = [
    {
        "id": slugify(n),
        "name": n,
        "category": CATEGORIES[c],
        "category_key": c,
        "hint_url": h,
        "ambiguity": a,
    }
    for (n, c, h, a) in _RAW
]
assert len(APPS) == 100, len(APPS)
assert len({a["id"] for a in APPS}) == 100

BY_ID = {a["id"]: a for a in APPS}


def find(name_or_id: str) -> dict:
    key = slugify(name_or_id)
    if key in BY_ID:
        return BY_ID[key]
    for a in APPS:
        if a["name"].lower().startswith(name_or_id.lower()):
            return a
    raise KeyError(name_or_id)
