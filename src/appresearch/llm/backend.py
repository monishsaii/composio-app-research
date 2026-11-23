"""LLM backends.

session   (default; used for the shipped data): tasks are written to cache/llm/tasks/<stage>/<id>.md and
          answered by Claude Code subagents (Haiku = extraction, Sonnet = adversarial/entailment,
          Opus = adjudication), which write cache/llm/responses/<stage>/<id>.json. $0 API spend.
anthropic (optional): answers the same task files via the Messages API. Requires ANTHROPIC_API_KEY.
"""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .. import cache

MODELS = {  # stage -> model tier (same mapping used for subagents in session mode)
    "pass1": "claude-haiku-5-5",
    "l1_entail": "claude-sonnet-5-5",
    "l2": "claude-sonnet-5-5",
    "l5": "claude-opus-5-5",
    "auditor": "claude-opus-5-5",
}
TASKS = cache.CACHE / "llm" / "tasks"
RESP = cache.CACHE / "llm" / "responses"


def pending(stage: str) -> list[Path]:
    return [t for t in sorted((TASKS / stage).glob("*.md")) if not (RESP / stage / f"{t.stem}.json").exists()]


def run_anthropic(stage: str, concurrency: int = 8) -> int:
    import anthropic  # optional dependency

    client = anthropic.Anthropic()
    model = MODELS.get(stage.split("_")[0], MODELS["pass1"])

    def one(t: Path):
        msg = client.messages.create(model=model, max_tokens=4000, messages=[{"role": "user", "content": t.read_text(encoding="utf-8")}])
        out = RESP / stage / f"{t.stem}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(msg.content[0].text, encoding="utf-8")
        cache.log_event("llm", backend="anthropic", stage=stage, model=model, id=t.stem,
                        in_tok=msg.usage.input_tokens, out_tok=msg.usage.output_tokens)

    todo = pending(stage)
    with ThreadPoolExecutor(concurrency) as ex:
        list(ex.map(one, todo))
    return len(todo)


def answer(stage: str, backend: str | None = None) -> int:
    backend = backend or os.environ.get("LLM_BACKEND", "session")
    if backend == "anthropic":
        return run_anthropic(stage)
    todo = pending(stage)
    if todo:
        print(f"[session backend] {len(todo)} task(s) awaiting subagent answers in {TASKS / stage}")
    return 0
