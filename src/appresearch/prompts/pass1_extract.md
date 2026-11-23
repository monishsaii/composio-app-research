# pass1_extract v1 — single-shot extraction (baseline; deliberately simple)

You are extracting integration-readiness facts about ONE app from the cached web pages below.
Use ONLY the pages provided. Do not use memory for facts. If the pages do not support a value, output "unknown".
A confident wrong answer is the worst outcome; "unknown" is acceptable.

Output ONE JSON object (no prose, no code fence) matching this shape:

{
 "id": "<given>", "name": "<given>", "category": "<given>",
 "one_liner": "<=20 words: what the product is",
 "docs_url": "canonical API docs URL or null", "openapi_spec_url": "URL or null",
 "auth_methods": ["oauth2"|"api_key"|"basic"|"bearer_token"|"jwt_service_account"|"hmac_signature"|"session_cookie"|"none"|"other"],
 "auth_notes": "short",
 "oauth_details": null | {"flows": ["auth_code"|"client_credentials"|"device"|"PKCE"], "scopes_granular": true|false|"unknown", "app_review_required": true|false|"unknown"},
 "access": "self_serve_free"|"self_serve_trial"|"paid_plan_required"|"admin_approval"|"app_review_required"|"partner_or_contact_sales"|"no_public_api"|"unknown",
 "access_notes": "what exactly gates getting credentials; cost if stated; wait if stated",
 "sandbox_or_test_env": true|false|"unknown",
 "api_surface": {"style": ["rest"|"graphql"|"soap"|"sdk_only"|"cli_only"|"websocket"|"other"], "breadth": "broad"|"medium"|"narrow"|"none"|"unknown", "approx_endpoint_count": int|null, "webhooks": bool|"unknown", "pagination_documented": bool|"unknown", "rate_limits_documented": bool|"unknown", "official_sdks": ["python", ...]},
 "mcp": {"exists": "official"|"community"|"none_found"|"unknown", "url": null|"URL"},
 "buildability": {"verdict": "BUILD_NOW"|"BUILD_WITH_CAVEATS"|"BLOCKED_NEEDS_OUTREACH"|"BLOCKED_NO_PUBLIC_API"|"NOT_APPLICABLE_NOT_A_SERVICE"|"UNCLEAR",
                  "main_blocker": "none"|"partner_gate"|"paid_plan_gate"|"app_review"|"enterprise_only"|"no_api"|"unstable_or_undocumented_api"|"auth_complexity"|"regulatory_or_pci"|"cli_or_local_only"|"ambiguous_product"|"other",
                  "rationale": "<=40 words", "est_tool_count_if_built": int|null, "est_effort": "S"|"M"|"L"|"XL"},
 "evidence": {"<group>": [{"url": "<one of the page URLs>", "quote": "<=25 words copied VERBATIM from that page", "source_type": "official_docs"|"pricing_page"|"official_repo"|"third_party"}]},
 "confidence": {"<group>": "high"|"medium"|"low"},
 "needs_human": bool, "needs_human_reason": "..."
}

Field groups for evidence/confidence: identity, auth, access, sandbox, api_surface, mcp, buildability.
Breadth: broad = >100 endpoints, medium = 20-100, narrow = <20.
Verdict rubric:
- BUILD_NOW: self-serve credentials + documented public API + standard auth + no blocker.
- BUILD_WITH_CAVEATS: buildable but needs app review, paid tier, narrow API, or per-customer admin setup.
- BLOCKED_NEEDS_OUTREACH: credentials need partnership/sales/approval a developer cannot self-serve.
- BLOCKED_NO_PUBLIC_API: no documented public API.
- NOT_APPLICABLE_NOT_A_SERVICE: local CLI/OSS tool, not a hosted API (say in rationale how to wrap it, e.g. as a skill).
Rules: every quote must be copied verbatim from the page whose URL you cite. Omit a group's evidence rather than invent it.
