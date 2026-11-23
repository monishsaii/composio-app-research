# Claude Code subagent runner: L1 entailment check (mid-tier model)

For EACH app id in your list: Read `d:/Composio/cache/llm/tasks/l1_entail/<id>.md`, follow its instructions, and Write ONLY the
JSON answer to `d:/Composio/cache/llm/responses/l1_entail/<id>.json`. Judge strictly from the PAGE WINDOW text shown:
"entailed" only if the window states the same fact as the claimed quote. Do not search or fetch anything. Do not edit other files.
Finish with one line per id: `<id>: N entailed, M unsupported`.
