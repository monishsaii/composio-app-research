# CHANGELOG

Accuracy below is agreement with the blind LLM auditor (Opus), NOT human ground truth; human-gold numbers replace it after the human check. 6 key fields per app; TEST n=120, DEV n=60 field judgements.

| snapshot | TEST | DEV | what changed |
|---|---|---|---|
| pass 1 | 40% | 40% | Haiku single shot, <=5 pages; 59/100 access unknown |
| after L1 | 38% | 37% | 154 quotes dropped as not supporting their claim; 20 groups reset to unknown (accuracy dips: honest unknowns) |
| after L2 | 65% | 60% | Sonnet adversarial pass; 340/800 disagreements, 287 adopted on string-verified evidence |
| after L3 | 65% | 62% | rules: 51 records flagged; verdicts forced to rubric |
| after L4 | 65% | 62% | Playwright on 15 apps; 0 quotes restored (L1 found all verbatim) |
| final (L5) | 69% | 63% | Sonnet adjudication of 92 unresolved fields: 66 resolved, 26 to human queue |

## Process notes
- Composio COMPOSIO_SEARCH retired (HTTP 410) on 2026-11-23 -> Claude Code WebSearch fallback, logged.
- 3 search records written by subagents without a real search were deleted (logged as removed_fabricated_search / removed_empty_search).
- L3 rule bug fixes (HTTP semantics: 405 = resolves; vendor GitHub org) and an L4 bug fix (never restore quotes L1 dropped as irrelevant) were made after seeing aggregate rule hits, not gold labels.
- Cost changes mid-run: L1 claim-check and retries moved to Haiku, L5 from Opus to Sonnet, L5 scoped to genuinely unresolved fields.
