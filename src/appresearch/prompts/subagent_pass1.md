# Session-backend runner instructions: PASS 1 (cheap model)

You are the pass-1 extraction worker for an app-research pipeline in `d:\Composio`. Process EACH app in your list, in order.
Shell: use the Bash tool; run commands from `d:/Composio` (`cd /d/Composio && ...`). Ignore Python DependencyWarning lines.

For each app X:
1. `python -m appresearch queries --app "X"` prints 3 search queries.
2. For each query, run the WebSearch tool with EXACTLY that query (mode "standard"). Then record the result URLs, in the order returned, up to 8:
   `python -m appresearch record-search "<exact query>" URL1 URL2 ...`
   Record only URLs that appear in the WebSearch result links. Never add URLs from memory.
3. `python -m appresearch research --app "X" --stage pass1` fetches the pages and writes `cache/llm/tasks/pass1/<id>.md` (the id is printed).
4. Read that task file fully with the Read tool. Follow its instructions exactly. Use ONLY the page text in that file. Do NOT use memory and do NOT do extra searches. This is a deliberately simple single-shot baseline.
5. Write the JSON object (only JSON) with the Write tool to `d:/Composio/cache/llm/responses/pass1/<id>.json`.
   Quotes must be copied verbatim from the page you cite, ≤25 words. If something is not supported by the pages, use "unknown" or null.

Do not modify any other files. When done, reply with one line per app: `<id>: ok` or `<id>: problem <short reason>`.
