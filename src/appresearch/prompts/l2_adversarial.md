# l2_adversarial v1 — independent, adversarial second pass

A first-pass agent produced the record below for ONE app. Your job is to TRY TO PROVE IT WRONG.
Assume each field may be wrong: auth methods, how credentials are actually obtained (free self-serve? trial? paid plan? admin
approval? app review? partner program / contact sales? no public API at all?), API breadth, webhooks, sandbox, MCP server
(official = published by the vendor on a vendor domain or vendor GitHub org; community = third party), main blocker, verdict.
Pay special attention to the "known ambiguity" line: resolve WHICH product/entity this is, with evidence.

Method:
- Use DIFFERENT pages from the first pass. Prefer primary sources: official docs, developer portal, pricing page, official GitHub.
- Run the provided search queries (at most 1 more of your own), record them, and read pages ONLY via
  `python -m appresearch fetch "<url>" --show 20000` (so every page you cite is cached and re-checkable).
- Quotes must be copied VERBATIM from the fetched page text, <=25 words. If you cannot find support, use "unknown".
- Gated-with-evidence is a correct finding. "unknown" is better than a guess.

Output ONE JSON object: the full record in the same schema as the first pass (all fields), PLUS
  "disputes": [{"field": "<path e.g. access | auth_methods | api_surface.breadth | mcp.exists | buildability.main_blocker>",
                "first_pass": <value>, "yours": <value>, "why": "<=30 words"}]
Verdict rubric: BUILD_NOW = self-serve credentials + documented public API + standard auth + no blocker;
BUILD_WITH_CAVEATS = buildable but needs app review, paid tier, narrow API, or per-customer admin setup;
BLOCKED_NEEDS_OUTREACH = credentials need partnership/sales/approval a developer cannot self-serve;
BLOCKED_NO_PUBLIC_API = no documented public API; NOT_APPLICABLE_NOT_A_SERVICE = local CLI/OSS tool (say how to wrap it).
Enums: auth_methods [oauth2, api_key, basic, bearer_token, jwt_service_account, hmac_signature, session_cookie, none, other];
access [self_serve_free, self_serve_trial, paid_plan_required, admin_approval, app_review_required, partner_or_contact_sales, no_public_api, unknown];
main_blocker [none, partner_gate, paid_plan_gate, app_review, enterprise_only, no_api, unstable_or_undocumented_api, auth_complexity, regulatory_or_pci, cli_or_local_only, ambiguous_product, other];
breadth broad(>100 endpoints)/medium(20-100)/narrow(<20)/none/unknown; source_type [official_docs, pricing_page, official_repo, third_party].
