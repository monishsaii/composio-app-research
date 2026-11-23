"""Disk cache: every fetch/search/LLM call is keyed by sha256 of its inputs. Resumable + idempotent."""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "cache"
DATA = ROOT / "data"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def key(*parts) -> str:
    return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:24]


def path(kind: str, k: str, ext: str = "json") -> Path:
    p = CACHE / kind / f"{k}.{ext}"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def get(kind: str, k: str):
    p = path(kind, k)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def put(kind: str, k: str, value) -> None:
    p = path(kind, k)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(p)


def log_event(name: str, **kw) -> None:
    """Append-only JSONL log of tool calls (used for fallback counts + timings)."""
    p = CACHE / "events.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"t": now_iso(), "event": name, **kw}) + "\n")


class Timer:
    def __init__(self, phase: str):
        self.phase = phase

    def __enter__(self):
        self.t0 = time.time()
        return self

    def __exit__(self, *a):
        p = DATA / "timings.json"
        d = json.loads(p.read_text()) if p.exists() else {}
        d.setdefault(self.phase, []).append({"started": datetime.fromtimestamp(self.t0, timezone.utc).isoformat(), "seconds": round(time.time() - self.t0, 1)})
        p.write_text(json.dumps(d, indent=1))
