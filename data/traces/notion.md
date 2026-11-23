# Execution trace: Notion

Assembled by `python -m appresearch trace --app "Notion"` from saved artifacts. LLM steps were executed by Claude Code subagents (pass 1: Haiku; L2/L1-entailment: Sonnet; L5: Opus). Search: Composio COMPOSIO_SEARCH attempted first (HTTP 410 retired) -> Claude Code WebSearch, recorded into the cache.

## 1. Pass-1 searches

**`Notion API documentation developer`** — via `fallback:claude_code_websearch` at 2026-11-23T13:46:50Z
  - https://developers.notion.com/reference/intro.md
  - https://developers.notion.com/page/changelog.md
  - https://developers.notion.com/reference/post-page.md
  - https://developers.notion.com/reference/admin/intro.md
  - https://developers.notion.com/guides
  - https://developers.notion.com/guides/get-started/overview.md
  - https://developers.notion.com/reference
  - https://developers.notion.com/llms.txt

**`Notion API authentication OAuth API key pricing plan access`** — via `fallback:claude_code_websearch` at 2026-11-23T13:46:50Z
  - https://developers.notion.com/guides/authorization/overview.md
  - https://developers.notion.com/docs/authorization
  - https://requestly.com/api-explorer/notion/
  - https://www.activepieces.com/blog/notion-api-quickstart-get-a-key-and-make-your-first-call.md
  - https://developers.notion.com/guides/get-started/authorization
  - https://developers.notion.com/reference/authentication.md

**`Notion MCP server model context protocol`** — via `fallback:claude_code_websearch` at 2026-11-23T13:46:50Z
  - https://docsearch.algolia.com/mcp/docs/repo/makenotion/notion-mcp-server
  - https://raw.githubusercontent.com/awkoy/notion-mcp-server/HEAD/README.md
  - https://www.notion.com/blog/notions-hosted-mcp-server-an-inside-look
  - https://github.com/mcp/makenotion/notion-mcp-server

## 2. Pages fetched for pass 1 (<=5)

- PAGE 1: https://developers.notion.com/reference/intro.md  (status 200)
- PAGE 2: https://developers.notion.com/page/changelog.md  (status 200)
- PAGE 3: https://developers.notion.com/guides/authorization/overview.md  (status 200)
- PAGE 4: https://developers.notion.com/docs/authorization  (status 200)
- PAGE 5: https://docsearch.algolia.com/mcp/docs/repo/makenotion/notion-mcp-server  (status 200)

## 3. Pass-1 extraction (raw subagent output, Haiku)

```json
{"id": "notion", "name": "Notion", "category": "Productivity/PM", "one_liner": "Workspace of pages and databases, with a REST API at api.notion.com for reading and writing them.", "docs_url": "https://developers.notion.com/reference/intro", "openapi_spec_url": null, "auth_methods": ["bearer_token", "oauth2"], "auth_notes": "Internal connection API tokens and personal access tokens are sent as a Bearer token. OAuth 2.0 integrations use an authorization code flow. Pages must be shared with each connection.", "oauth_details": {"flows": ["auth_code"], "scopes_granular": "unknown", "app_review_required": false}, "access": "unknown", "access_notes": "Internal connections are created in the Developer portal and require workspace owner role. PATs are created by a user in the Developer portal. No cost stated on the fetched pages.", "sandbox_or_test_env": "unknown", "api_surface": {"style": ["rest"], "breadth": "unknown", "approx_endpoint_count": null, "webhooks": true, "pagination_documented": true, "rate_limits_documented": "unknown", "official_sdks": ["javascript"]}, "mcp": {"exists": "official", "url": "https://mcp.notion.com/mcp"}, "buildability": {"verdict": "BUILD_WITH_CAVEATS", "main_blocker": "other", "rationale": "Self-serve credentials and documented REST API with pagination and webhooks. Caveat: each customer must manually share pages with the connection before API calls succeed.", "est_tool_count_if_built": null, "est_effort": "M"}, "evidence": {"identity": [{"url": "https://developers.notion.com/reference/intro.md", "quote": "Find the base URL, headers, and data formats for Notion API requests.", "source_type": "official_docs"}], "auth": [{"url": "https://developers.notion.com/guides/authorization/overview.md", "quote": "Authenticate Notion API requests with personal access tokens, internal connection tokens, or OAuth integration OAuth flows.", "source_type": "official_docs"}], "access": [{"url": "https://developers.notion.com/guides/authorization/overview.md", "quote": "You are required to be a workspace owner to create a connection.", "source_type": "official_docs"}], "api_surface": [{"url": "https://developers.notion.com/reference/intro.md", "quote": "Most endpoints use JSON.", "source_type": "official_docs"}, {"url": "https://developers.notion.com/reference/intro.md", "quote": "For lists with more than one page", "source_type": "official_docs"}, {"url": "https://developers.notion.com/page/changelog.md", "quote": "webhook events now arrive right away, usually within a few seconds", "source_type": "official_docs"}], "mcp": [{"url": "https://developers.notion.com/page/changelog.md", "quote": "Notion MCP is retiring its legacy SSE endpoint", "source_type": "official_docs"}, {"url": "https://docsearch.algolia.com/mcp/docs/repo/makenotion/notion-mcp-server", "quote": "You can install and configure the Notion MCP server using npx.", "source_type": "official_repo"}], "buildability": [{"url": "https://developers.notion.com/guides/authorization/overview.md", "quote": "the page must be manually shared with the connection", "source_type": "official_docs"}, {"url": "https://developers.notion.com/guides/authorization/overview.md", "quote": "Marketplace submission or review is not required.", "source_type": "official_docs"}]}, "confidence": {"identity": "high", "auth": "high", "access": "medium", "sandbox": "low", "api_surface": "medium", "mcp": "high", "buildability": "medium"}, "needs_human": false, "needs_human_reason": ""}

```

## 4. L1 evidence validation (re-fetch + fuzzy match + entailment)

| group | url | support | score |
|---|---|---|---|
| identity | https://developers.notion.com/reference/intro.md | exact | 100 |
| auth | https://developers.notion.com/guides/authorization/overview.md | exact | 100 |
| api_surface | https://developers.notion.com/reference/intro.md | exact | 100 |
| api_surface | https://developers.notion.com/page/changelog.md | exact | 100 |
| mcp | https://developers.notion.com/page/changelog.md | exact | 100 |
| buildability | https://developers.notion.com/guides/authorization/overview.md | exact | 100 |
| composio | https://composio.dev/toolkits/notion | sdk_catalog |  |
| access | https://developers.notion.com/guides/authorization/overview.md | **dropped: unsupported** | 100 |
| api_surface | https://developers.notion.com/reference/intro.md | **dropped: unsupported** | 100 |
| mcp | https://docsearch.algolia.com/mcp/docs/repo/makenotion/notion-mcp-server | **dropped: unsupported** | 100 |
| buildability | https://developers.notion.com/guides/authorization/overview.md | **dropped: unsupported** | 100 |

Groups reset to unknown: `[]`

## 5. L2 adversarial pass (Sonnet) — disputes

- `access`: pass1 `unknown` vs L2 `self_serve_free` -> adopted L2: True
- `api_surface.breadth`: pass1 `unknown` vs L2 `medium` -> adopted L2: True
- `buildability.main_blocker`: pass1 `other` vs L2 `none` -> adopted L2: True
- `buildability.verdict`: pass1 `BUILD_WITH_CAVEATS` vs L2 `BUILD_NOW` -> adopted L2: True

## 6. L3 rule checks


## 7. L4 browser verification

- https://developers.notion.com/reference/intro status 200 screenshot `data/screenshots/notion-0.png`
- https://developers.notion.com/guides/authorization/overview.md status 200 screenshot `data/screenshots/notion-1.png`
- https://developers.notion.com/reference/intro.md status 200 screenshot `data/screenshots/notion-2.png`
- https://docsearch.algolia.com/mcp/docs/repo/makenotion/notion-mcp-server status 200 screenshot `data/screenshots/notion-3.png`

## 8. L5 adjudication + final


| field | pass1 | final |
|---|---|---|
| auth_methods | `['bearer_token', 'oauth2']` | `['bearer_token', 'oauth2']` |
| access | `unknown` | `self_serve_free` |
| sandbox_or_test_env | `unknown` | `unknown` |
| api_surface.breadth | `unknown` | `medium` |
| mcp.exists | `official` | `official` |
| buildability.main_blocker | `other` | `none` |
| buildability.verdict | `BUILD_WITH_CAVEATS` | `BUILD_NOW` |

### Final record

```json
{
 "id": "notion",
 "name": "Notion",
 "category": "Productivity/PM",
 "one_liner": "Workspace of pages and databases, with a REST API at api.notion.com for reading and writing them.",
 "docs_url": "https://developers.notion.com/reference/intro",
 "openapi_spec_url": null,
 "auth_methods": [
  "bearer_token",
  "oauth2"
 ],
 "auth_notes": "Internal connection API tokens and personal access tokens are sent as a Bearer token. OAuth 2.0 integrations use an authorization code flow. Pages must be shared with each connection.",
 "oauth_details": {
  "flows": [
   "auth_code"
  ],
  "scopes_granular": "unknown",
  "app_review_required": false
 },
 "access": "self_serve_free",
 "access_notes": "Quickstart needs only a Notion account and a PAT from the Developer portal; no plan tier required. Business/Enterprise admins may restrict PAT creation. [sandbox_or_test_env: Use a free personal workspace (no dedicated sandbox documented)]",
 "sandbox_or_test_env": "unknown",
 "api_surface": {
  "style": [
   "rest"
  ],
  "breadth": "medium",
  "approx_endpoint_count": null,
  "webhooks": true,
  "pagination_documented": true,
  "rate_limits_documented": "unknown",
  "official_sdks": [
   "javascript"
  ]
 },
 "mcp": {
  "exists": "official",
  "url": "https://mcp.notion.com/mcp"
 },
 "buildability": {
  "verdict": "BUILD_NOW",
  "main_blocker": "none",
  "rationale": "Self-serve credentials and documented REST API with pagination and webhooks. Caveat: each customer must manually share pages with the connection before API calls succeed.",
  "est_tool_count_if_built": null,
  "est_effort": "M"
 },
 "composio_existing_toolkit": true,
 "evidence": {
  "identity": [
   {
    "url": "https://developers.notion.com/reference/intro.md",
    "quote": "Find the base URL, headers, and data formats for Notion API requests.",
    "source_type": "official_docs",
    "fetched_at": "2026-11-23T13:46:51Z",
    "support": "exact",
    "match_score": 100,
    "claim_check": "supports"
   }
  ],
  "auth": [
   {
    "url": "https://developers.notion.com/guides/authorization/overview.md",
    "quote": "Authenticate Notion API requests with personal access tokens, internal connection tokens, or OAuth integration OAuth flows.",
    "source_type": "official_docs",
    "fetched_at": "2026-11-23T13:46:51Z",
    "support": "exact",
    "match_score": 100,
    "claim_check": "supports"
   }
  ],
  "access": [
   {
    "url": "https://developers.notion.com/guides/get-started/create-a-notion-integration.md",
    "quote": "You need a Notion account and a terminal.",
    "source_type": "official_docs",
    "fetched_at": "2026-11-23T16:26:55Z",
    "support": "exact",
    "match_score": 100,
    "from": "L2"
   },
   {
    "url": "https://developers.notion.com/guides/get-started/create-a-notion-integration.md",
    "quote": "On Business and Enterprise plans, PAT creation is restricted by default. Ask a workspace owner to enable it",
    "source_type": "official_docs",
    "fetched_at": "2026-11-23T16:26:55Z",
    "support": "exact",
    "match_score": 100,
    "from": "L2"
   }
  ],
  "api_surface": [
   {
    "url": "https://developers.notion.com/reference/intro.md",
    "quote": "Most endpoints use JSON.",
    "source_type": "official_docs",
    "fetched_at": "2026-11-23T13:46:51Z",
    "support": "exact",
    "match_score": 100,
    "claim_check": "supports"
   },
   {
    "url": "https://developers.notion.com/page/changelog.md",
    "quote": "webhook events now arrive right away, usually within a few seconds",
    "source_type": "official_docs",
    "fetched_at": "2026-11-23T13:46:51Z",
    "support": "exact",
    "match_score": 100,
    "claim_check": "supports"
   },
   {
    "url": "https://developers.notion.com/reference/request-limits.md",
    "quote": "| Business and Enterprise | 600 requests per minute (an average of 10 per second) |",
    "source_type": "official_docs",
    "fetched_at": "2026-11-23T16:26:51Z",
    "support": "exact",
    "match_score": 100,
    "from": "L2"
   },
   {
    "url": "https://developers.notion.com/reference/webhooks.md",
    "quote": "Whenever a page or database changes, Notion sends a secure HTTP POST request to your webhook endpoint.",
    "source_type": "official_docs",
    "fetched_at": "2026-11-23T16:26:52Z",
    "support": "exact",
    "match_score": 100,
    "from": "L2"
   }
  ],
  "mcp": [
   {
    "url": "https://developers.notion.com/page/changelog.md",
    "quote": "Notion MCP is retiring its legacy SSE endpoint",
    "source_type": "official_docs",
    "fetched_at": "2026-11-23T13:46:51Z",
    "support": "exact",
    "match_score": 100,
    "claim_check": "supports"
   }
  ],
  "buildability": [
   {
    "url": "https://developers.notion.com/guides/authorization/overview.md",
    "quote": "the page must be manually shared with the connection",
    "source_type": "official_docs",
    "fetched_at": "2026-11-23T13:46:51Z",
    "support": "exact",
    "match_score": 100,
    "claim_check": "supports"
   },
   {
    "url": "https://developers.notion.com/reference/request-limits.md",
    "quote": "| All other plans | 180 requests per minute (an average of 3 per second) |",
    "source_type": "official_docs",
    "fetched_at": "2026-11-23T16:26:51Z",
    "support": "exact",
    "match_score": 100,
    "from": "L2"
   }
  ],
  "composio": [
   {
    "url": "https://composio.dev/toolkits/notion",
    "quote": "Composio catalog entry 'notion' (Notion), 57 tools, auth ['OAUTH2', 'API_KEY']",
    "source_type": "official_docs",
    "fetched_at": "2026-11-23T13:46:15Z",
    "support": "sdk_catalog"
   }
  ]
 },
 "confidence": {
  "identity": "high",
  "auth": "high",
  "access": "low",
  "sandbox": "low",
  "api_surface": "low",
  "mcp": "high",
  "buildability": "low"
 },
 "needs_human": false,
 "needs_human_reason": "",
 "flags": [
  "L4 browser-verified"
 ],
 "l1_dropped_evidence": [
  {
   "url": "https://developers.notion.com/guides/authorization/overview.md",
   "quote": "You are required to be a workspace owner to create a connection.",
   "source_type": "official_docs",
   "fetched_at": "2026-11-23T13:46:51Z",
   "support": "unsupported",
   "match_score": 100,
   "claim_check": "irrelevant",
   "group": "access"
  },
  {
   "url": "https://developers.notion.com/reference/intro.md",
   "quote": "For lists with more than one page",
   "source_type": "official_docs",
   "fetched_at": "2026-11-23T13:46:51Z",
   "support": "unsupported",
   "match_score": 100,
   "claim_check": "irrelevant",
   "group": "api_surface"
  },
  {
   "url": "https://docsearch.algolia.com/mcp/docs/repo/makenotion/notion-mcp-server",
   "quote": "You can install and configure the Notion MCP server using npx.",
   "source_type": "official_repo",
   "fetched_at": "2026-11-23T13:46:52Z",
   "support": "unsupported",
   "match_score": 100,
   "claim_check": "irrelevant",
   "group": "mcp"
  },
  {
   "url": "https://developers.notion.com/guides/authorization/overview.md",
   "quote": "Marketplace submission or review is not required.",
   "source_type": "official_docs",
   "fetched_at": "2026-11-23T13:46:51Z",
   "support": "unsupported",
   "match_score": 100,
   "claim_check": "irrelevant",
   "group": "buildability"
  }
 ],
 "disputes": [
  {
   "field": "access",
   "group": "access",
   "pass1": "unknown",
   "l2": "self_serve_free",
   "adopted_l2": true,
   "l2_evidence": [
    {
     "url": "https://developers.notion.com/guides/get-started/create-a-notion-integration.md",
     "quote": "You need a Notion account and a terminal.",
     "source_type": "official_docs",
     "fetched_at": "2026-11-23T16:26:55Z",
     "support": "exact",
     "match_score": 100,
     "from": "L2"
    },
    {
     "url": "https://developers.notion.com/guides/get-started/create-a-notion-integration.md",
     "quote": "On Business and Enterprise plans, PAT creation is restricted by default. Ask a workspace owner to enable it",
     "source_type": "official_docs",
     "fetched_at": "2026-11-23T16:26:55Z",
     "support": "exact",
     "match_score": 100,
     "from": "L2"
    }
   ]
  },
  {
   "field": "api_surface.breadth",
   "group": "api_surface",
   "pass1": "unknown",
   "l2": "medium",
   "adopted_l2": true,
   "l2_evidence": [
    {
     "url": "https://developers.notion.com/reference/request-limits.md",
     "quote": "| Business and Enterprise | 600 requests per minute (an average of 10 per second) |",
     "source_type": "official_docs",
     "fetched_at": "2026-11-23T16:26:51Z",
     "support": "exact",
     "match_score": 100,
     "from": "L2"
    },
    {
     "url": "https://developers.notion.com/reference/webhooks.md",
     "quote": "Whenever a page or database changes, Notion sends a secure HTTP POST request to your webhook endpoint.",
     "source_type": "official_docs",
     "fetched_at": "2026-11-23T16:26:52Z",
     "support": "exact",
     "match_score": 100,
     "from": "L2"
    }
   ]
  },
  {
   "field": "buildability.main_blocker",
   "group": "buildability",
   "pass1": "other",
   "l2": "none",
   "adopted_l2": true,
   "l2_evidence": [
    {
     "url": "https://developers.notion.com/reference/request-limits.md",
     "quote": "| All other plans | 180 requests per minute (an average of 3 per second) |",
     "source_type": "official_docs",
     "fetched_at": "2026-11-23T16:26:51Z",
     "support": "exact",
     "match_score": 100,
     "from": "L2"
    }
   ]
  },
  {
   "field": "buildability.verdict",
   "group": "buildability",
   "pass1": "BUILD_WITH_CAVEATS",
   "l2": "BUILD_NOW",
   "adopted_l2": true,
   "l2_evidence": [
    {
     "url": "https://developers.notion.com/reference/request-limits.md",
     "quote": "| All other plans | 180 requests per minute (an average of 3 per second) |",
     "source_type": "official_docs",
     "fetched_at": "2026-11-23T16:26:51Z",
     "support": "exact",
     "match_score": 100,
     "from": "L2"
    }
   ]
  }
 ],
 "browser_evidence": [
  {
   "url": "https://developers.notion.com/reference/intro",
   "status": 200,
   "screenshot": "data/screenshots/notion-0.png",
   "chars": 2222,
   "fetched_at": "2026-11-23T16:33:06Z"
  },
  {
   "url": "https://developers.notion.com/guides/authorization/overview.md",
   "status": 200,
   "screenshot": "data/screenshots/notion-1.png",
   "chars": 26900,
   "fetched_at": "2026-11-23T16:33:09Z"
  },
  {
   "url": "https://developers.notion.com/reference/intro.md",
   "status": 200,
   "screenshot": "data/screenshots/notion-2.png",
   "chars": 2290,
   "fetched_at": "2026-11-23T16:33:12Z"
  },
  {
   "url": "https://docsearch.algolia.com/mcp/docs/repo/makenotion/notion-mcp-server",
   "status": 200,
   "screenshot": "data/screenshots/notion-3.png",
   "chars": 11370,
   "fetched_at": "2026-11-23T16:33:18Z"
  }
 ]
}
```
