# Claude Code subagent runner: independent LLM auditor (strongest model) — NOT human ground truth

Work in `d:/Composio` via the Bash tool (`cd /d/Composio && ...`); ignore Python DependencyWarning lines.
You are BLIND to the research agent's answers: do not open data/*.json, cache/llm/responses/pass1|l2|l5, or human_check files.
For EACH app id in your list:
1. Read `d:/Composio/cache/llm/tasks/auditor/<id>.md`.
2. At most 2 WebSearch calls per app (mode "standard"); record each with
   `python -m appresearch record-search "<exact query>" URL1 URL2 ...`.
   Read pages ONLY with `python -m appresearch fetch "<url>" --show 15000` (max ~4 pages per app; prefer official docs,
   developer portal, pricing page, official GitHub; try .md / llms.txt variants for JS-rendered docs).
3. Write ONLY the JSON answer to `d:/Composio/cache/llm/responses/auditor/<id>.json`. Quotes verbatim from fetched text.
If the WebSearch budget is exhausted, stop and report which ids are unfinished. Never create accounts or bypass logins.
Finish with one line per id: `<id>: ok` or `<id>: problem <reason>`.
