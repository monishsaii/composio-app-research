# Claude Code subagent runner: L1 claim-support / entailment check (mid-tier model)

For EACH app id in your list: Read `d:/Composio/cache/llm/tasks/l1_entail/<id>.md`, follow its instructions, and Write ONLY
the JSON answer to `d:/Composio/cache/llm/responses/l1_entail/<id>.json` (one key per ITEM, e.g. "auth#0").
Be strict: "supports" only if the quote itself backs the claimed value (e.g. a quote about bearer tokens supports auth
bearer_token but NOT access=self_serve_free). Do not search or fetch anything. Do not edit other files.
Finish with one line per id: `<id>: S supports, I irrelevant, C contradicts, N not_on_page`.
