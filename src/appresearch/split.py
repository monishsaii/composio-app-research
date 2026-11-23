"""Stratified gold sample: 30 apps (3 per category), forced to include known gated/ambiguous apps.
10 DEV (may be used to tune loops) / 20 TEST (locked). Seeded; committed before any loop code exists."""
from __future__ import annotations

import json
import random

from . import cache
from .apps import APPS, CATEGORIES

SEED = 20261123
FORCED = ["meta-ads", "linkedin-ads", "amazon-selling-partner", "pitchbook", "dealcloud",
          "notebooklm", "sherlock", "paygent-connect", "fanbasis"]


def make_split() -> dict:
    rng = random.Random(SEED)
    by_cat = {c: [a["id"] for a in APPS if a["category_key"] == c] for c in CATEGORIES}
    sample: dict[str, list[str]] = {}
    for c, ids in by_cat.items():
        forced = [i for i in ids if i in FORCED]
        rest = [i for i in ids if i not in forced]
        rng.shuffle(rest)
        sample[c] = (forced + rest)[:3]
    dev, test = [], []
    for c in CATEGORIES:  # 1 DEV per category, rest TEST
        ids = sample[c][:]
        rng.shuffle(ids)
        dev.append(ids[0])
        test.extend(ids[1:])
    out = {"seed": SEED, "created_at": cache.now_iso(), "design": "3 per category x 10 categories; forced-include gated/ambiguous apps; 1 DEV + 2 TEST per category",
           "forced_include": FORCED, "dev": sorted(dev), "test": sorted(test)}
    assert len(out["dev"]) == 10 and len(out["test"]) == 20 and not set(dev) & set(test)
    assert set(FORCED) <= set(dev) | set(test)
    (cache.DATA / "gold_split.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def load() -> dict:
    return json.loads((cache.DATA / "gold_split.json").read_text(encoding="utf-8"))
