# Claude Code subagent runner: L5 adjudication (Sonnet tier)

Work in `d:/Composio` via the Bash tool (`cd /d/Composio && ...`); ignore Python DependencyWarning lines.
For EACH app id in your list:
1. Read `d:/Composio/cache/llm/tasks/l5/<id>.md` fully and follow it.
2. Targeted re-research only where the given evidence is insufficient: WebSearch (mode "standard"), record each search with
   `python -m appresearch record-search "<exact query>" URL1 URL2 ...`, read pages ONLY with
   `python -m appresearch fetch "<url>" --show 20000`. Quotes must be verbatim from that fetched text (<=25 words).
   Prefer `.md`/llms.txt/GitHub README variants when a docs page is JS-rendered and returns little text.
3. Write ONLY the JSON answer to `d:/Composio/cache/llm/responses/l5/<id>.json`.
Never create accounts or try to bypass logins/paywalls. Do not edit other files.
Finish with one line per id: `<id>: resolved X/Y fields`.
