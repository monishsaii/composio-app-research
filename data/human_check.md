# Human check (gold sample)

Fill `human_correct` with Y or N for each row. If N, put the right value in `human_value` (same enum). Add a `note` if useful.
Open `doc_link` / `evidence_url` to check. Edit the CSV, not this file. TEST rows (20 apps) come first; DEV rows (10 apps) follow.

Enums: access = self_serve_free | self_serve_trial | paid_plan_required | admin_approval | app_review_required | partner_or_contact_sales | no_public_api | unknown;
verdict = BUILD_NOW | BUILD_WITH_CAVEATS | BLOCKED_NEEDS_OUTREACH | BLOCKED_NO_PUBLIC_API | NOT_APPLICABLE_NOT_A_SERVICE | UNCLEAR;
breadth = broad(>100) | medium(20-100) | narrow(<20) | none | unknown; mcp = official | community | none_found | unknown.


## Amazon Selling Partner (TEST)  [docs](https://developer-docs.amazon.com/sp-api)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `oauth2` | [Public applications must use OAuth 2.0 to obtain authorization from selling part](https://developer-docs.amazon.com/sp-api/docs/onboarding-overview) |
| access | `app_review_required` | [When you create a developer account, you must request and qualify for the specif](https://developer-docs.amazon.com/sp-api/docs/onboarding-overview) |
| api_surface.breadth | `broad` | [The SP-API uses the token bucket algorithm to rate-limit requests to the API.](https://developer-docs.amazon.com/sp-api/docs/usage-plans-and-rate-limits) |
| mcp.exists | `official` | [A Model Context Protocol (MCP) server that provides AI agents with access to Ama](https://github.com/jay-trivedi/amazon_sp_mcp) |
| buildability.main_blocker | `app_review` | [When you create a developer account, you must request and qualify for the specif](https://developer-docs.amazon.com/sp-api/docs/onboarding-overview) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [When you create a developer account, you must request and qualify for the specif](https://developer-docs.amazon.com/sp-api/docs/onboarding-overview) |

## Copper (TEST)  [docs](https://developer.copper.com/)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `api_key|oauth2` | [There are two ways to access the Copper Developer API: API keys and OAuth2.0.](https://developer.copper.com/introduction/authentication.html) |
| access | `paid_plan_required` | [Available on our trial, professional and business plan](https://support.copper.com/en/articles/8823462-api-docs-and-tips) |
| api_surface.breadth | `unknown` | [The API provides a RESTful interface with JSON-formatted responses to use Copper](https://support.copper.com/en/articles/8823462-api-docs-and-tips) |
| mcp.exists | `official` | [Copper is launching an official MCP server, built and hosted by Copper. The beta](https://www.copper.com/mcp) |
| buildability.main_blocker | `paid_plan_gate` | [Available on our trial, professional and business plan](https://support.copper.com/en/articles/8823462-api-docs-and-tips) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [Available on our trial, professional and business plan](https://support.copper.com/en/articles/8823462-api-docs-and-tips) |

## DealCloud (TEST)  [docs](https://api.docs.dealcloud.com/docs)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `api_key|oauth2` | [DealCloud uses the OAuth2 Client Credentials flow to generate a bearer token, wh](https://api.docs.dealcloud.com/docs/token) |
| access | `admin_approval` | [If you do not see the Admin section, contact your organization's admin or DealCl](https://api.docs.dealcloud.com/docs/apikeys) |
| api_surface.breadth | `unknown` | []() |
| mcp.exists | `official` | [DealCloud now provides a Model Context Protocol (MCP) server which gives AI agen](https://api.docs.dealcloud.com/releases) |
| buildability.main_blocker | `other` | [If you do not see the Admin section, contact your organization's admin or DealCl](https://api.docs.dealcloud.com/docs/apikeys) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [If you do not see the Admin section, contact your organization's admin or DealCl](https://api.docs.dealcloud.com/docs/apikeys) |

## fanbasis (TEST)  [docs]()

| field | agent value | evidence |
|---|---|---|
| auth_methods | `api_key` | [All requests to the Manager API must be authenticated using an API Key sent in t](https://docs.openstage.live/manager/guides) |
| access | `paid_plan_required` | [Fanbase API is available exclusively to artists on the Legendary plan.](https://fanbaseapi.openstage.live/guides.html) |
| api_surface.breadth | `unknown` | [The response does not include the fan's ID. To get it, listen for the fan.create](https://docs.openstage.live/manager/guides) |
| mcp.exists | `unknown` | []() |
| buildability.main_blocker | `ambiguous_product` | [Fanbase API is available exclusively to artists on the Legendary plan.](https://fanbaseapi.openstage.live/guides.html) |
| buildability.verdict | `UNCLEAR` | [Fanbase API is available exclusively to artists on the Legendary plan.](https://fanbaseapi.openstage.live/guides.html) |

## Google Ads (TEST)  [docs](https://developers.google.com/google-ads/api/docs/catalog)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `jwt_service_account|oauth2` | [Application Default Credentials (OAuth 2.0 user credentials or service account) ](https://developers.google.com/google-ads/api/docs/developer-toolkit/mcp-server) |
| access | `app_review_required` | [apply for Explorer access on the Google Ads API Overview page to access producti](https://developers.google.com/google-ads/api/docs/access-levels?authuser=8) |
| api_surface.breadth | `broad` | [Java, .NET, PHP, Python, Ruby, Perl, Code samples, REST interface](https://developers.google.com/adwords/api/docs/?csw=1) |
| mcp.exists | `official` | [The Google Ads MCP server provides a standardized bridge to the Google Ads API.](https://developers.google.com/google-ads/api/docs/developer-toolkit/mcp-server) |
| buildability.main_blocker | `app_review` | [apply for Explorer access on the Google Ads API Overview page to access producti](https://developers.google.com/google-ads/api/docs/access-levels?authuser=8) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [apply for Explorer access on the Google Ads API Overview page to access producti](https://developers.google.com/google-ads/api/docs/access-levels?authuser=8) |

## higgsfield (TEST)  [docs](https://docs.higgsfield.ai/docs)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `api_key` | [authenticate server-side with Authorization: Key YOUR_KEY_ID:YOUR_KEY_SECRET.](https://docs.higgsfield.ai/docs/help/faq) |
| access | `paid_plan_required` | [Add a payment method and top up your balance.](https://higgsfield.ai/blog/higgsfield-api) |
| api_surface.breadth | `unknown` | [Connect through the Python or TypeScript SDK, or call the REST API directly from](https://higgsfield.ai/creator-hub/help-center/integrations/what-is-the-higgsfield-api) |
| mcp.exists | `official` | [No. Add the Higgsfield MCP server URL in your agent's settings and authenticate ](https://higgsfield.ai/cli) |
| buildability.main_blocker | `paid_plan_gate` | [Add a payment method and top up your balance.](https://higgsfield.ai/blog/higgsfield-api) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [Add a payment method and top up your balance.](https://higgsfield.ai/blog/higgsfield-api) |

## Lark (Larksuite) (TEST)  [docs](https://open.larksuite.com/llms.txt)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `bearer_token|oauth2` | [Obtaining user_access_token follows standard OAuth 2.0.](https://open.larksuite.com/llms.txt) |
| access | `admin_approval` | [Only ISV-qualified users can create store apps.](https://open.larksuite.com/llms.txt) |
| api_surface.breadth | `broad` | [Traditional webhook mode, requiring you to provide a public internet address for](https://open.larksuite.com/llms.txt) |
| mcp.exists | `official` | [npm install @larksuiteoapi/lark-mcp -g](https://open.larksuite.com/document/uAjLw4CM/ukTMukTMukTM/mcp_integration/advanced-configuration.md) |
| buildability.main_blocker | `other` | [Only ISV-qualified users can create store apps.](https://open.larksuite.com/llms.txt) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [Only ISV-qualified users can create store apps.](https://open.larksuite.com/llms.txt) |

## Linear (TEST)  [docs](https://linear.app/developers/graphql)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `api_key|oauth2` | [The Linear API supports personal API keys and OAuth2 authentication.](https://linear.app/docs/api/graphql) |
| access | `self_serve_free` | [API and webhook access](https://linear.app/pricing) |
| api_surface.breadth | `unknown` | [It supports introspection so you can query the whole schema.](https://linear.app/docs/api/graphql) |
| mcp.exists | `official` | [Read-write access is provided through https://mcp.linear.app/mcp by default.](https://linear.app/docs/mcp) |
| buildability.main_blocker | `none` | [API and webhook access](https://linear.app/pricing) |
| buildability.verdict | `BUILD_NOW` | [API and webhook access](https://linear.app/pricing) |

## Meta Ads (TEST)  [docs](https://developers.facebook.com/docs/marketing-apis/)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `bearer_token|oauth2` | [System user token](https://skaler.app/blog/meta-marketing-api) |
| access | `app_review_required` | [If it manages other people's ad accounts (an agency tool or a SaaS product), you](https://skaler.app/blog/meta-marketing-api) |
| api_surface.breadth | `broad` | [The Marketing API has its own throttling, separate from general Graph API limits](https://skaler.app/blog/meta-marketing-api) |
| mcp.exists | `unknown` | []() |
| buildability.main_blocker | `app_review` | [If it manages other people's ad accounts (an agency tool or a SaaS product), you](https://skaler.app/blog/meta-marketing-api) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [If it manages other people's ad accounts (an agency tool or a SaaS product), you](https://skaler.app/blog/meta-marketing-api) |

## Otter AI (TEST)  [docs](https://help.otter.ai/hc/en-us/articles/36130822688279-Otter-ai-Public-API-beta)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `api_key|oauth2` | [the Public API is gated to Enterprise workspaces and authenticates with Bearer A](https://www.scalekit.com/blog/otter-mcp-vs-api) |
| access | `partner_or_contact_sales` | [The Public API is a REST surface at api.otter.ai/v1, available to Enterprise wor](https://www.scalekit.com/blog/otter-mcp-vs-api) |
| api_surface.breadth | `narrow` | [Public API (beta): https://help.otter.ai/hc/en-us/articles/36130822688279-Otter-](https://otter.ai/llms.txt) |
| mcp.exists | `community` | [Agents can read and write in Otter.ai.](https://www.stackone.com/connectors/otterai/mcp/) |
| buildability.main_blocker | `enterprise_only` | [The Public API is a REST surface at api.otter.ai/v1, available to Enterprise wor](https://www.scalekit.com/blog/otter-mcp-vs-api) |
| buildability.verdict | `BLOCKED_NEEDS_OUTREACH` | [The Public API is a REST surface at api.otter.ai/v1, available to Enterprise wor](https://www.scalekit.com/blog/otter-mcp-vs-api) |

## Paygent Connect (TEST)  [docs]()

| field | agent value | evidence |
|---|---|---|
| auth_methods | `` | []() |
| access | `unknown` | []() |
| api_surface.breadth | `unknown` | []() |
| mcp.exists | `none_found` | []() |
| buildability.main_blocker | `ambiguous_product` | []() |
| buildability.verdict | `UNCLEAR` | []() |

## PitchBook (TEST)  [docs]()

| field | agent value | evidence |
|---|---|---|
| auth_methods | `` | []() |
| access | `partner_or_contact_sales` | [neither PitchBook nor Crunchbase publishes API prices. Both sell API access by q](https://privateequitylist.com/intelligence/md/pitchbook-crunchbase-api-pricing) |
| api_surface.breadth | `unknown` | []() |
| mcp.exists | `unknown` | []() |
| buildability.main_blocker | `enterprise_only` | [neither PitchBook nor Crunchbase publishes API prices. Both sell API access by q](https://privateequitylist.com/intelligence/md/pitchbook-crunchbase-api-pricing) |
| buildability.verdict | `BLOCKED_NEEDS_OUTREACH` | [neither PitchBook nor Crunchbase publishes API prices. Both sell API access by q](https://privateequitylist.com/intelligence/md/pitchbook-crunchbase-api-pricing) |

## Plain (TEST)  [docs](https://help.plain.com/article/developer)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `api_key` | [A machine user can have several API keys, so you can rotate them without downtim](https://www.plain.com/docs/graphql/authentication.md) |
| access | `self_serve_trial` | [In Settings, open Machine Users and create a machine user with read-only permiss](https://help.plain.com/article/does-the-plain-mcp-server-support-api-key-authentication-h7d83qtfdzxo4h49x4oyklwx) |
| api_surface.breadth | `broad` | [For TypeScript, the GraphQL SDK gives you a fully typed client for these operati](https://help.plain.com/article/developer) |
| mcp.exists | `official` | [The Plain Model Context Protocol (MCP) server at https://mcp.plain.com/mcp suppo](https://help.plain.com/article/does-the-plain-mcp-server-support-api-key-authentication-h7d83qtfdzxo4h49x4oyklwx) |
| buildability.main_blocker | `none` | [In Settings, open Machine Users and create a machine user with read-only permiss](https://help.plain.com/article/does-the-plain-mcp-server-support-api-key-authentication-h7d83qtfdzxo4h49x4oyklwx) |
| buildability.verdict | `BUILD_NOW` | [In Settings, open Machine Users and create a machine user with read-only permiss](https://help.plain.com/article/does-the-plain-mcp-server-support-api-key-authentication-h7d83qtfdzxo4h49x4oyklwx) |

## Pylon (TEST)  [docs](https://docs.usepylon.com/pylon-docs/developer/api)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `bearer_token` | [The Pylon API uses Bearer authentication.](https://docs.usepylon.com/pylon-docs/developer/api/authentication) |
| access | `paid_plan_required` | [Only Admins can create and manage API tokens.](https://docs.usepylon.com/pylon-docs/developer/api/authentication) |
| api_surface.breadth | `medium` | [Webhooks](https://docs.usepylon.com/pylon-docs/developer/webhooks.md): Receive w](https://docs.usepylon.com/llms.txt) |
| mcp.exists | `official` | [Server URL (US): https://mcp.usepylon.com](https://docs.usepylon.com/pylon-docs/integrations/mcp) |
| buildability.main_blocker | `paid_plan_gate` | [Only Admins can create and manage API tokens.](https://docs.usepylon.com/pylon-docs/developer/api/authentication) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [Only Admins can create and manage API tokens.](https://docs.usepylon.com/pylon-docs/developer/api/authentication) |

## Sentry (TEST)  [docs](https://docs.sentry.io/api/)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `bearer_token|oauth2` | [For third-party applications that need to access Sentry on behalf of users, Sent](https://docs.sentry.io/api/guides/oauth/) |
| access | `self_serve_free` | [For solo devs working on small projects](https://sentry.io/pricing/) |
| api_surface.breadth | `broad` | [Each endpoint has its own maximum number of requests and window size.](https://docs.sentry.io/api/ratelimits/) |
| mcp.exists | `official` | [The subagent connects to a remote MCP server and has access to Sentry tools.](https://docsearch.algolia.com/mcp/docs/repo/getsentry/sentry-mcp) |
| buildability.main_blocker | `none` | [For solo devs working on small projects](https://sentry.io/pricing/) |
| buildability.verdict | `BUILD_NOW` | [For solo devs working on small projects](https://sentry.io/pricing/) |

## Sherlock (TEST)  [docs](https://github.com/sherlock-project/sherlock/blob/master/docs/README.md)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `none` | []() |
| access | `no_public_api` | [pip or uv may be used in place of pipx](https://github.com/sherlock-project/sherlock) |
| api_surface.breadth | `none` | [Accounts found will be stored in an individual text file with the corresponding ](https://github.com/sherlock-project/sherlock) |
| mcp.exists | `unknown` | []() |
| buildability.main_blocker | `cli_or_local_only` | [pip or uv may be used in place of pipx](https://github.com/sherlock-project/sherlock) |
| buildability.verdict | `NOT_APPLICABLE_NOT_A_SERVICE` | [pip or uv may be used in place of pipx](https://github.com/sherlock-project/sherlock) |

## Smartsheet (TEST)  [docs](https://developers.smartsheet.com/api/smartsheet/guides/basics/authentication)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `bearer_token|oauth2` | [The API authenticates using access tokens (API keys).](https://developers.smartsheet.com/api/smartsheet/guides/basics/authentication) |
| access | `paid_plan_required` | [Required plan: Business, Enterprise, or Advanced Work Management](https://developers.smartsheet.com/api/smartsheet/introduction.md) |
| api_surface.breadth | `broad` | [The MCP Server routes the request through Smartsheet REST API, pulling structure](https://www.smartsheet.com/content-center/product-insights/product-updates/introducing-smartsheet-mcp-server) |
| mcp.exists | `official` | [The Smartsheet MCP Server is an open, protocol-based integration layer built on ](https://www.smartsheet.com/content-center/product-insights/product-updates/introducing-smartsheet-mcp-server) |
| buildability.main_blocker | `paid_plan_gate` | [Required plan: Business, Enterprise, or Advanced Work Management](https://developers.smartsheet.com/api/smartsheet/introduction.md) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [Required plan: Business, Enterprise, or Advanced Work Management](https://developers.smartsheet.com/api/smartsheet/introduction.md) |

## Supabase (TEST)  [docs](https://supabase.com/docs)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `api_key|bearer_token|oauth2` | [All API requests require an access token to be included in the Authorization hea](https://supabase.com/docs/guides/platform/management-api) |
| access | `self_serve_free` | [Free projects are paused after 1 week of inactivity. Limit of 2 active projects.](https://supabase.com/pricing) |
| api_surface.breadth | `unknown` | [POST /v1/projects is organization-scoped, using the organization_slug in the req](https://supabase.com/docs/guides/platform/management-api) |
| mcp.exists | `official` | [Connecting an LLM to your Supabase projects carries security risks.](https://supabase.com/docs/guides/getting-started/mcp) |
| buildability.main_blocker | `none` | [Free projects are paused after 1 week of inactivity. Limit of 2 active projects.](https://supabase.com/pricing) |
| buildability.verdict | `BUILD_NOW` | [Free projects are paused after 1 week of inactivity. Limit of 2 active projects.](https://supabase.com/pricing) |

## Telegram (TEST)  [docs](https://core.telegram.org/api)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `api_key|other` | [Before invoking API methods, you must obtain an access token in your Telegram Ga](https://core.telegram.org/gateway/verification-tutorial) |
| access | `self_serve_free` | [You are welcome to use both APIs free of charge.](https://core.telegram.org/api) |
| api_surface.breadth | `broad` | [You communicate with this server via a simple HTTPS interface that offers a simp](https://core.telegram.org/api) |
| mcp.exists | `community` | [The server is a bridge between the Telegram API and the AI assistants and is bas](https://github.com/sparfenyuk/mcp-telegram) |
| buildability.main_blocker | `none` | [You are welcome to use both APIs free of charge.](https://core.telegram.org/api) |
| buildability.verdict | `BUILD_NOW` | [You are welcome to use both APIs free of charge.](https://core.telegram.org/api) |

## Waterfall.io (TEST)  [docs](https://www.waterfall.io/)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `api_key` | [The API key is sent in the `x-api-key` header with each request.](https://www.withone.ai/knowledge/waterfall/md) |
| access | `partner_or_contact_sales` | [Contact the team for API access and pricing.](https://docs.waterfall.io/v1/authentication) |
| api_surface.breadth | `medium` | [## Actions (23)](https://www.withone.ai/knowledge/waterfall/md) |
| mcp.exists | `none_found` | []() |
| buildability.main_blocker | `partner_gate` | [Contact the team for API access and pricing.](https://docs.waterfall.io/v1/authentication) |
| buildability.verdict | `BLOCKED_NEEDS_OUTREACH` | [Contact the team for API access and pricing.](https://docs.waterfall.io/v1/authentication) |

## Datadog (DEV)  [docs](https://docs.datadoghq.com/api/latest)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `api_key|oauth2|other` | [Authenticate to the API with an API key using the header DD-API-KEY.](https://docs.datadoghq.com/ko/api/latest) |
| access | `paid_plan_required` | [Use these resources to test out and learn about the unified Datadog platform.](https://www.datadoghq.com/free-datadog-trial/) |
| api_surface.breadth | `broad` | [returns JSON from all requests, and uses standard HTTP response codes.](https://docs.datadoghq.com/ko/api/latest) |
| mcp.exists | `official` | [Datadog MCP サーバーは、Datadog のオブザーバビリティデータと Model Context Protocol (MCP) をサポートする AI](https://docs.datadoghq.com/ja/bits_ai/mcp_server/) |
| buildability.main_blocker | `paid_plan_gate` | [Use these resources to test out and learn about the unified Datadog platform.](https://www.datadoghq.com/free-datadog-trial/) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [Use these resources to test out and learn about the unified Datadog platform.](https://www.datadoghq.com/free-datadog-trial/) |

## Help Scout (DEV)  [docs](https://developer.helpscout.com)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `api_key|oauth2` | [This is an HTTPS-only API and it uses OAuth 2.0 authorization, implementing Auth](https://developer.helpscout.com/mailbox-api/overview/authentication) |
| access | `paid_plan_required` | [You need to create an OAuth2 application before you can use the API.](https://developer.helpscout.com/mailbox-api/overview/authentication) |
| api_surface.breadth | `unknown` | [HAL+JSON with embedded resources and pagination](https://developer.helpscout.com/llms.txt) |
| mcp.exists | `official` | [Today, we're bringing Help Scout's Model Context Protocol (MCP) server out of be](https://articles.helpscout.com/blog/introducing-help-scout-mcp/) |
| buildability.main_blocker | `none` | [You need to create an OAuth2 application before you can use the API.](https://developer.helpscout.com/mailbox-api/overview/authentication) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [You need to create an OAuth2 application before you can use the API.](https://developer.helpscout.com/mailbox-api/overview/authentication) |

## LinkedIn Ads (DEV)  [docs](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/ads-overview)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `oauth2` | [All permissions listed are Member Permissions (3-legged OAuth), meaning they req](https://learn.microsoft.com/linkedin/marketing/increasing-access) |
| access | `app_review_required` | [Vetted Product with development and standard tiers](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/ads-overview) |
| api_surface.breadth | `unknown` | [If you've tried calling LinkedIn's /rest/adAnalytics endpoint by hand](https://pypi.org/project/linkedin-ads-mcp/) |
| mcp.exists | `community` | [There's no official LinkedIn MCP.](https://pypi.org/project/linkedin-ads-mcp/) |
| buildability.main_blocker | `app_review` | [Vetted Product with development and standard tiers](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/ads-overview) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [Vetted Product with development and standard tiers](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/ads-overview) |

## MrScraper (DEV)  [docs](https://docs.mrscraper.com/docs/api/overview)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `api_key` | [All API endpoints require authentication using an API token passed in the x-api-](https://docs.mrscraper.com/docs/api/overview) |
| access | `self_serve_free` | [Initialize with your free API token from mrscraper.com](https://mrscraper.com/blog/free-web-scraping-apis) |
| api_surface.breadth | `medium` | [Built on REST principles, our API offers predictable resource-oriented URLs, acc](https://docs.mrscraper.com/docs/api/overview) |
| mcp.exists | `official` | [An MCP server exposing the seven MrScraper services through hosted HTTP or local](https://github.com/mrscraper-com/mrscraper-mcp) |
| buildability.main_blocker | `other` | [Initialize with your free API token from mrscraper.com](https://mrscraper.com/blog/free-web-scraping-apis) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [Initialize with your free API token from mrscraper.com](https://mrscraper.com/blog/free-web-scraping-apis) |

## NotebookLM (DEV)  [docs](https://developers.google.com/notebook/docs/authentication)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `oauth2` | [The Gemini Notebook API uses OAuth 2.0 to authenticate requests on behalf of a G](https://developers.google.com/notebook/docs/authentication) |
| access | `self_serve_free` | [During the Public Preview, the Gemini Notebook API is only available for persona](https://developers.google.com/notebook/docs/authentication) |
| api_surface.breadth | `narrow` | [REST Resource: v1.notebooks.sources](https://developers.google.com/notebook/reference/rest) |
| mcp.exists | `official` | [The Gemini Notebook API provides a remote Model Context Protocol (MCP)](https://developers.google.com/notebook/docs/mcp) |
| buildability.main_blocker | `unstable_or_undocumented_api` | [During the Public Preview, the Gemini Notebook API is only available for persona](https://developers.google.com/notebook/docs/authentication) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [During the Public Preview, the Gemini Notebook API is only available for persona](https://developers.google.com/notebook/docs/authentication) |

## Notion (DEV)  [docs](https://developers.notion.com/reference/intro)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `bearer_token|oauth2` | [Authenticate Notion API requests with personal access tokens, internal connectio](https://developers.notion.com/guides/authorization/overview.md) |
| access | `self_serve_free` | [You need a Notion account and a terminal.](https://developers.notion.com/guides/get-started/create-a-notion-integration.md) |
| api_surface.breadth | `medium` | [Most endpoints use JSON.](https://developers.notion.com/reference/intro.md) |
| mcp.exists | `official` | [Notion MCP is retiring its legacy SSE endpoint](https://developers.notion.com/page/changelog.md) |
| buildability.main_blocker | `none` | [You need a Notion account and a terminal.](https://developers.notion.com/guides/get-started/create-a-notion-integration.md) |
| buildability.verdict | `BUILD_NOW` | [You need a Notion account and a terminal.](https://developers.notion.com/guides/get-started/create-a-notion-integration.md) |

## Podio (DEV)  [docs](https://developers.podio.com/doc)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `oauth2` | [The Podio API uses the OAuth2 protocol for authentication.](https://developers.podio.com/authentication) |
| access | `self_serve_free` | [API Integrations | 1000 calls per hour | 1000 calls per hour Upgrade with Add-on](https://www.progress.com/podio/pricing) |
| api_surface.breadth | `broad` | [The general limit is 1,000 API calls per hour](https://developers.podio.com/index/limits) |
| mcp.exists | `official` | [The server is live at https://mcp.podio.com — just point your AI platform at it ](https://www.progress.com/podio/documentation/using-podio/podio-mcp-server) |
| buildability.main_blocker | `none` | [API Integrations | 1000 calls per hour | 1000 calls per hour Upgrade with Add-on](https://www.progress.com/podio/pricing) |
| buildability.verdict | `BUILD_NOW` | [API Integrations | 1000 calls per hour | 1000 calls per hour Upgrade with Add-on](https://www.progress.com/podio/pricing) |

## QuickBooks (DEV)  [docs](https://developer.intuit.com/app/developer/qbo/docs/learn/explore-the-quickbooks-online-api)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `oauth2` | [This server uses OAuth 2.0 to authenticate to a QuickBooks Online company.](https://raw.githubusercontent.com/intuit/quickbooks-online-mcp-server/main/README.md) |
| access | `self_serve_free` | [Monthly Fee: $0](https://www.apideck.com/blog/quickbooks-api-pricing-and-the-intuit-app-partner-program) |
| api_surface.breadth | `broad` | [It includes full CRUD operations for 29 entity types and 11 financial reports](https://raw.githubusercontent.com/intuit/quickbooks-online-mcp-server/main/README.md) |
| mcp.exists | `official` | [this is a local MCP server. It runs as a stdio subprocess on the developer's or ](https://github.com/intuit/quickbooks-online-mcp-server) |
| buildability.main_blocker | `auth_complexity` | [Monthly Fee: $0](https://www.apideck.com/blog/quickbooks-api-pricing-and-the-intuit-app-partner-program) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [Monthly Fee: $0](https://www.apideck.com/blog/quickbooks-api-pricing-and-the-intuit-app-partner-program) |

## Shopify (DEV)  [docs](https://shopify.dev/apps/tools/api-libraries)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `oauth2|other` | [Your app sends the token in the X-Shopify-Access-Token header on every GraphQL A](https://shopify.dev/docs/apps/build/authentication-authorization) |
| access | `self_serve_free` | [Some APIs also require Shopify's approval or a specific Shopify plan.](https://shopify.dev/apps/tools/api-libraries) |
| api_surface.breadth | `broad` | [GraphQL Admin API reads and writes products, customers, orders, inventory, and t](https://shopify.dev/apps/tools/api-libraries) |
| mcp.exists | `official` | [Shopify MCP lets merchants and partners set up and manage a store through the AI](https://shopify.dev/apps/tools/api-libraries) |
| buildability.main_blocker | `other` | [Some APIs also require Shopify's approval or a specific Shopify plan.](https://shopify.dev/apps/tools/api-libraries) |
| buildability.verdict | `BUILD_WITH_CAVEATS` | [Some APIs also require Shopify's approval or a specific Shopify plan.](https://shopify.dev/apps/tools/api-libraries) |

## Twilio (DEV)  [docs](https://www.twilio.com/docs)

| field | agent value | evidence |
|---|---|---|
| auth_methods | `api_key|basic|oauth2` | [Whenever the integration supports OAuth 2.0 or a Restricted API Key, use it.](https://www.twilio.com/docs/usage/api-security-reference-guide/secure-auth) |
| access | `self_serve_trial` | [A Twilio account (you can sign up for free, here) and a Twilio API Key](https://twilio.com/en-us/blog/introducing-twilio-alpha-mcp-server) |
| api_surface.breadth | `broad` | [Learn how to interact with the REST API for account management, development test](https://twilio.com/docs/api) |
| mcp.exists | `official` | [today, we're equally excited to introduce the Twilio Alpha MCP server.](https://twilio.com/en-us/blog/introducing-twilio-alpha-mcp-server) |
| buildability.main_blocker | `none` | [A Twilio account (you can sign up for free, here) and a Twilio API Key](https://twilio.com/en-us/blog/introducing-twilio-alpha-mcp-server) |
| buildability.verdict | `BUILD_NOW` | [A Twilio account (you can sign up for free, here) and a Twilio API Key](https://twilio.com/en-us/blog/introducing-twilio-alpha-mcp-server) |
