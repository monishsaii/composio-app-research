"""Report shape/validity of L2 responses (used to decide reject-and-retry)."""
import json
import os

from .. import cache
from . import l2_second_pass as L


def main():
    d = cache.CACHE / "llm" / "responses" / "l2"
    bad = []
    for f in sorted(os.listdir(d)):
        raw = json.load(open(d / f, encoding="utf-8"))
        ev = raw.get("evidence")
        labeled = isinstance(ev, dict) or (isinstance(ev, list) and ev and all(("field" in e or "group" in e) for e in ev))
        ok = L._load_l2(f[:-5]) is not None
        if not (labeled and ok):
            bad.append((f[:-5], "evidence" if not labeled else "schema"))
    print("needs retry:", bad)
    return bad


if __name__ == "__main__":
    main()
