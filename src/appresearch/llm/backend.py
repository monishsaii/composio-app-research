"""LLM execution = Claude Code subagents (the only backend; $0 additional API spend).

The pipeline writes task files to cache/llm/tasks/<stage>/<id>.md. A Claude Code session answers them with subagents
following prompts/subagent_<stage>.md, writing cache/llm/responses/<stage>/<id>.json. Python then validates and ingests.
Model tier per stage (subagent `model` parameter):
"""
from __future__ import annotations

from pathlib import Path

from .. import cache

MODEL_TIER = {
    "pass1": "haiku (cheap extraction)",
    "l1_entail": "sonnet (entailment check)",
    "l2": "sonnet (adversarial second pass)",
    "l5": "opus (adjudication)",
    "auditor": "opus (independent LLM auditor; NOT ground truth)",
}
TASKS = cache.CACHE / "llm" / "tasks"
RESP = cache.CACHE / "llm" / "responses"


def pending(stage: str) -> list[Path]:
    return [t for t in sorted((TASKS / stage).glob("*.md")) if not (RESP / stage / f"{t.stem}.json").exists()]


def report_pending(stage: str) -> int:
    todo = pending(stage)
    if todo:
        print(f"[claude-code subagents] {len(todo)} {stage} task(s) awaiting answers in {TASKS / stage}")
        print(f"  model tier: {MODEL_TIER.get(stage, '?')}; runner instructions: src/appresearch/prompts/subagent_{stage}.md")
    return len(todo)
