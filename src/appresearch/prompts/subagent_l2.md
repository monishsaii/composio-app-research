# Session-backend runner instructions: L2 adversarial pass (mid-tier model)

Work in `d:/Composio` using the Bash tool (`cd /d/Composio && ...`). Ignore Python DependencyWarning lines.
For EACH app id in your list:
1. Read `d:/Composio/cache/llm/tasks/l2/<id>.md` (instructions, first-pass record, suggested queries).
2. Run the suggested queries with WebSearch (mode "standard"), recording each one:
   `python -m appresearch record-search "<exact query>" URL1 URL2 ...` (only URLs from the results).
3. Read up to 6 pages that were NOT used by the first pass, only via `python -m appresearch fetch "<url>" --show 20000`.
   For JS-heavy pages that return little text, try another official page (e.g. the docs page's .md variant, llms.txt, GitHub README).
4. Write the output JSON (only JSON) with the Write tool to `d:/Composio/cache/llm/responses/l2/<id>.json`.
Do not edit any other file. Finish with one line per app: `<id>: ok, N disputes` or `<id>: problem <reason>`.
