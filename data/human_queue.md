# Human queue

Fields the agent could not settle with verified evidence after L5 (plus records flagged needs_human).

| app | field | current value | why | docs |
|---|---|---|---|---|
| Close | access | `unknown` | Key creation is self-serve but whether a paid plan or trial is needed was not stated in fetched pages. | https://developer.close.com/api |
| fanbasis | access | `paid_plan_required` | Prior Legendary-plan evidence was for Openstage, not fanbasis; fanbasis key acquisition not verified. |  |
| fanbasis | api_surface.webhooks | `True` | Prior webhook evidence was Openstage; no fanbasis webhook page fetched. |  |
| fanbasis | buildability.main_blocker | `ambiguous_product` | Real fanbasis API exists (official SDK) but docs not readable; access terms unverified. |  |
| fanbasis | mcp.exists | `unknown` | No MCP evidence found. |  |
| Gladly | mcp.exists | `unknown` | Only a third-party StackOne MCP was seen; no official Gladly MCP verified. | https://developer.gladly.com/rest/ |
| Harvest | mcp.exists | `unknown` | Search result snippet shows Harvest support article 'Harvest MCP' (endpoint api.harvestapp.com/mcp), but the page return | https://help.getharvest.com:443/api-v2/introduction/overview/general/ |
| Meta Ads | mcp.exists | `unknown` (proposed `official`) | adjudicator evidence failed verification | https://developers.facebook.com/docs/marketing-apis/ |
| MrScraper | buildability.main_blocker | `other` (proposed `none`) | adjudicator evidence failed verification | https://docs.mrscraper.com/docs/api/overview |
| Neo4j | buildability.main_blocker | `other` (proposed `ambiguous_product`) | adjudicator evidence failed verification | https://neo4j.com/api_docs |
| NotebookLM | api_surface.webhooks | `unknown` | adjudicator evidence failed verification | https://developers.google.com/notebook/docs/authentication |
| Paygent Connect | access | `unknown` | No Paygent Connect signup or credential docs found. |  |
| Paygent Connect | buildability.main_blocker | `ambiguous_product` | Product identity unclear (NMI-powered vs Japanese PSP). |  |
| PitchBook | mcp.exists | `unknown` | Only third-party GitHub results seen; no vendor-published MCP verified; official pages 403. |  |
| Pumble | api_surface.webhooks | `unknown` | No webhook info on fetched page. | https://pumble.com/help/integrations/api-keys-integration |
| Pylon | sandbox_or_test_env | `unknown` | No sandbox evidence found in fetched pages. | https://docs.usepylon.com/pylon-docs/developer/api |
| Salesforce Commerce Cloud | access | `unknown` | Official docs return 403; only third-party repo says instance with OCAPI access needed. | https://developer.salesforce.com/docs/commerce/commerce-api/overview |
| Salesforce Commerce Cloud | buildability.main_blocker | `other` | Requires licensed per-instance Commerce Cloud; gate type unverified. | https://developer.salesforce.com/docs/commerce/commerce-api/overview |
| Sherlock | mcp.exists | `unknown` | No MCP evidence found in README; not searched further. | https://github.com/sherlock-project/sherlock/blob/master/docs/README.md |
| Shopify | buildability.main_blocker | `other` | Evidence lacks a verified quote; dev stores self-serve but some scopes and public apps need approval. | https://shopify.dev/apps/tools/api-libraries |
| Threads (Meta) | api_surface.webhooks | `True` | Webhooks page fetch returned HTTP 400; no verified evidence either way. | https://developers.facebook.com/docs/threads |
| Twenty | sandbox_or_test_env | `unknown` | No verified sandbox evidence; trial and self-hosting exist but are not a documented sandbox. | https://docs.twenty.com/developers/extend/api.md |
| Twenty | buildability.main_blocker | `other` (proposed `none`) | adjudicator evidence failed verification | https://docs.twenty.com/developers/extend/api.md |
| WhatsApp Business | buildability.main_blocker | `other` | Meta docs mostly not fetchable; app review applies mainly to tech providers, direct developers can use test number. | https://developers.facebook.com/docs/whatsapp |
| WhatsApp Business | mcp.exists | `unknown` | No evidence fetched. | https://developers.facebook.com/docs/whatsapp |
| Zendesk | mcp.exists | `unknown` | Search found only third-party servers; no vendor-published MCP verified. | https://developer.zendesk.com/api-reference/ |

## Other needs_human records

- **Mermaid CLI**: no evidence for: auth
