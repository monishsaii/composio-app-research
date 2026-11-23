# appresearch: integration readiness of 100 apps for agent tool-calling

For each of 100 apps, the pipeline records how it authenticates and what gates API credentials. It also records how big the API is, whether an MCP server exists, and a rubric verdict (BUILD_NOW … BLOCKED_NO_PUBLIC_API). Every non-unknown value carries `{url, ≤25-word quote, source_type, fetched_at}`. The output is `site/index.html`, a self-contained case study, plus `data/final.json`.

**How it runs (no hidden autonomy).** Python handles search plumbing, fetch, cache, validation, rule checks, analysis and the site. The LLM steps are done by **Claude Code subagents** inside a Claude Code session: Haiku extracts and labels claim support (L1; the shipped L1 run used Sonnet), Sonnet runs the adversarial pass and L5 adjudication, Haiku handles format retries, and Opus was used only for the blind auditor. Python writes a task file, a subagent answers it, and Python validates the answer with pydantic and retries invalid output. There is no Anthropic API key and no API spend. Composio's SDK supplies the toolkit catalog, and Composio search is tried first; see Limitations.

## Two modes

| | Needs | Does |
|---|---|---|
| **Offline replay** (reviewers) | Python 3.11+ only. No keys, no network | Recomputes `accuracy.json`, `analysis.json` and `site/index.html` from committed `data/*.json` |
| **Fresh research** | Claude Code session + `COMPOSIO_API_KEY` | Runs new searches/fetches and asks subagents to answer the emitted task files |

```bash
pip install -e ".[dev]"
python -m appresearch replay          # offline: rebuild every number + the page
python -m pytest -q                   # rule checks + rubric + schema tests
```

### Fresh research for one app (inside Claude Code)
```bash
cp .env.example .env                  # add COMPOSIO_API_KEY
python -m appresearch queries --app "Notion"
#  -> in Claude Code: WebSearch each query, then record the result URLs:
python -m appresearch record-search "<exact query>" URL1 URL2 ...
python -m appresearch research --app "Notion" --stage pass1      # fetch pages, write task file
#  -> ask a subagent: "Read src/appresearch/prompts/subagent_pass1.md and follow it for: Notion"
python -m appresearch research --app "Notion" --ingest-only      # validate + print record
```
All 100 apps: `research --all --stage pass1`, then `verify --loop L1` … `verify --loop L5`. Each loop stops and prints the pending task files whenever subagent answers are needed (the runner prompts are `prompts/subagent_*.md`). Re-run the same command after the answers are written. Everything is cached under `cache/` and the run is resumable.

A saved real trace of one app: [`data/traces/`](data/traces/) (queries → sources → extraction → validation → each loop → final).

## Verification
- **Gold sample.** 30 apps, 3 per category, forced to include the known hard cases. Split 10 DEV / 20 TEST, seeded, and committed before any results existed (`data/gold_split.json`, see git history). TEST was never used for tuning.
- **L1 evidence.** Re-fetch every cited URL, string-match the quote (exact, or rapidfuzz ≥85), then a Sonnet claim-support check: does the quote support the claimed value? Unsupported groups are reset to `unknown` (rule: no evidence → unknown).
- **L2 adversarial.** A Sonnet pass told to prove pass 1 wrong, using different queries and different pages. Field-level diff. An L2 value is adopted only if its quote string-matches its page.
- **L3 rules** (unit-tested, `tests/test_rules.py`). The deterministic rubric verdict. oauth2 ⇒ authorize/token evidence. paid ⇒ pricing evidence. Official MCP ⇒ resolves on a vendor domain. docs_url is 200 and not a marketing page. Breadth matches the endpoint count.
- **L4 browser.** Playwright renders the 15 hardest apps (screenshots in `data/screenshots/`) to recover JS-rendered evidence. Observe only.
- **L5 adjudication.** Sonnet (lowered from Opus to cut usage) takes each disputed or low-confidence field, with the conflicting evidence plus targeted re-research. Its quotes must string-match too. Anything unresolved goes to `data/human_queue.md`.
- **Human check.** `data/human_check.csv` (30 apps × 6 fields) is filled by a human. A blind Opus "auditor" also answers the same fields without seeing the agent's answers. It is reported separately and is **not** ground truth.

## Verdict rubric (code: `src/appresearch/rubric.py`, first match wins)
1. NOT_APPLICABLE_NOT_A_SERVICE: blocker cli_or_local_only (local OSS/CLI; wrap it as a skill).
2. BLOCKED_NO_PUBLIC_API: access no_public_api or blocker no_api.
3. BLOCKED_NEEDS_OUTREACH: access partner_or_contact_sales, or blocker partner_gate / enterprise_only.
4. UNCLEAR: access unknown, or blocker ambiguous_product.
5. BUILD_NOW: self-serve (free or trial), blocker none, and breadth not narrow.
6. BUILD_WITH_CAVEATS: everything else (paid tier, app review, admin approval, narrow API, auth complexity).

## Cost and time
$0 API spend: the LLM work ran inside a Claude Code session. Subagent token counts and agent-minutes per stage are in `data/agent_runs.jsonl` and on the page. Wall-clock time per pipeline phase is in `data/timings.json`.

## Limitations and assumptions
- **Composio search is retired.** `COMPOSIO_SEARCH_*` returned HTTP 410 "toolkit version retired" for every version on 2026-11-23, including via Tool Router sessions. Search therefore fell back to Claude Code WebSearch. Results are recorded into the same cache (`via: fallback:claude_code_websearch`) and each fallback is logged in `cache/events.jsonl`. Composio is still used for the toolkit catalog (1,842 toolkits) behind `composio_existing_toolkit`.
- **Search cap.** WebSearch is capped at 200 calls per Claude Code turn, shared by all subagents, so the run spanned several turns. Pass 1 used 3 queries per app, L2 used 2, and the auditor at most 2.
- **Pass 1 is deliberately thin**: ≤5 pages and one shot. Many of its unknowns come from JS-rendered or 403/404 pages.
- **Small schema relaxation.** `est_effort` may be null (not estimated) rather than a forced guess. Type-only normalisation (null list → `[]`, null tri-state → `"unknown"`) is logged per field.
- `est_tool_count` and effort are heuristics. Company size is not collected, so gating vs size is not reported.
- Facts are as of 2026-11-23. Pricing and partner programs change.

## Layout
`src/appresearch/`: `cli.py`, `research.py` (discover/emit/ingest), `schema.py`, `rubric.py`, `loops/l1..l5`, `tools/` (Composio catalog + search, httpx fetch, Playwright), `prompts/` (all LLM prompts + subagent runners), `accuracy.py`, `analyze.py`, `human.py`, `trace.py`, `site/`.
`data/`: `pass1.json`, `after_L1..L4.json`, `final.json`, `gold_split.json`, `human_check.csv`, `accuracy.json`, `analysis.json`, `human_queue.md`, `loop_stats.json`, `agent_runs.jsonl`, `traces/`.
`cache/llm/responses/`: every raw subagent answer (committed). Page and search caches are not committed because of their size.
