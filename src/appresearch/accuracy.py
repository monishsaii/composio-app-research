"""Accuracy report — every number is computed here from saved files (pass1/after_L*/final.json, human_check.csv,
auditor responses). Human gold and LLM-auditor agreement are kept strictly separate."""
from __future__ import annotations

import json
import math
import os

from . import cache, human, research, rubric, split
from .loops.l2_second_pass import get

SNAPSHOTS = [("pass1", "pass1.json"), ("L1", "after_L1.json"), ("L2", "after_L2.json"), ("L3", "after_L3.json"),
             ("L4", "after_L4.json"), ("final", "final.json")]
FIELDS = human.KEY_FIELDS
GATED_ACCESS = rubric.GATED_ACCESS | {"no_public_api"}


def norm(field: str, v) -> str:
    if field == "auth_methods":
        if isinstance(v, str):
            v = [x.strip() for x in v.replace(",", "|").split("|") if x.strip()]
        return "|".join(sorted(v or []))
    if isinstance(v, list):
        return "|".join(sorted(v))
    return "" if v is None else str(v).strip()


def wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    if n == 0:
        return [0.0, 0.0]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0, c - h), 3), round(min(1, c + h), 3)]


def score(records: dict, gold: dict, ids: list[str]) -> dict:
    per_field, k_all, n_all = {}, 0, 0
    for f in FIELDS:
        k = n = 0
        for aid in ids:
            if (aid, f) not in gold or aid not in records:
                continue
            n += 1
            k += norm(f, get(records[aid], f)) == norm(f, gold[(aid, f)])
        per_field[f] = {"k": k, "n": n, "acc": round(k / n, 3) if n else None, "ci95": wilson(k, n)}
        k_all += k
        n_all += n
    v = per_field["buildability.verdict"]
    return {"field_level": {"k": k_all, "n": n_all, "acc": round(k_all / n_all, 3) if n_all else None, "ci95": wilson(k_all, n_all)},
            "verdict": v, "per_field": per_field}


def gated_pr(records: dict, gold: dict, ids: list[str]) -> dict:
    tp = fp = fn = tn = 0
    for aid in ids:
        if (aid, "access") not in gold:
            continue
        g = gold[(aid, "access")] in GATED_ACCESS
        p = records[aid].get("access") in GATED_ACCESS
        tp += g and p
        fp += p and not g
        fn += g and not p
        tn += (not g) and (not p)
    prec = tp / (tp + fp) if tp + fp else None
    rec = tp / (tp + fn) if tp + fn else None
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": prec and round(prec, 3), "recall": rec and round(rec, 3)}


def confusion(records: dict, gold: dict, ids: list[str]) -> dict:
    m: dict = {}
    for aid in ids:
        g = gold.get((aid, "buildability.verdict"))
        if g is None:
            continue
        p = records[aid]["buildability"]["verdict"]
        m.setdefault(g, {}).setdefault(p, 0)
        m[g][p] += 1
    return m


def cause(rec: dict, field: str, note: str) -> str:
    if note:
        return f"human note: {note}"
    from .apps import BY_ID

    flags = " ".join(rec.get("flags", []))
    if BY_ID[rec["id"]].get("ambiguity") and field in ("access", "buildability.main_blocker", "buildability.verdict"):
        tag = "ambiguous product / unclear tier"
    elif any(e.get("support") == "unfetchable" for evs in rec.get("evidence", {}).values() for e in evs) or "L4" in flags:
        tag = "JS-rendered or blocked page"
    elif get(rec, field) in ("unknown", None, "", []):
        tag = "insufficient evidence found"
    elif field == "access":
        tag = "misread pricing/access gate"
    else:
        tag = "misread docs"
    return tag


def main() -> dict:
    sp = split.load()
    hum = human.load_human()
    aud = human.load_auditor()
    notes = {}
    if human.CSV.exists():
        import csv

        with human.CSV.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("note"):
                    notes[(row["app_id"], row["field"])] = row["note"]
    snaps = {}
    for name, fn in SNAPSHOTS:
        p = cache.DATA / fn
        if p.exists():
            snaps[name] = {r["id"]: r for r in research.load(fn)}
    out = {"generated_at": cache.now_iso(), "offline_replay": bool(os.environ.get("APPRESEARCH_OFFLINE")),
           "gold_source": {"human": len(hum), "auditor": len(aud)}, "split": {k: sp[k] for k in ("dev", "test")}}
    for label, gold in (("human", hum), ("auditor_NOT_ground_truth", aud)):
        if not gold:
            out[label] = None
            continue
        res = {}
        for part in ("dev", "test"):
            ids = sp[part]
            res[part] = {s: score(recs, gold, ids) for s, recs in snaps.items()}
            if "final" in snaps:
                res[part]["gated_final"] = gated_pr(snaps["final"], gold, ids)
                res[part]["gated_pass1"] = gated_pr(snaps["pass1"], gold, ids)
                res[part]["verdict_confusion_final"] = confusion(snaps["final"], gold, ids)
        # marginal gain per loop (TEST and DEV), field-level
        for part in ("dev", "test"):
            order = [s for s, _ in SNAPSHOTS if s in res[part]]
            res[part]["marginal_gain"] = {order[i]: round((res[part][order[i]]["field_level"]["acc"] or 0) - (res[part][order[i - 1]]["field_level"]["acc"] or 0), 3)
                                          for i in range(1, len(order))}
        if "final" in snaps:
            misses = []
            for part in ("test", "dev"):
                for aid in sp[part]:
                    for f in FIELDS:
                        if (aid, f) in gold and norm(f, get(snaps["final"][aid], f)) != norm(f, gold[(aid, f)]):
                            misses.append({"split": part, "id": aid, "name": snaps["final"][aid]["name"], "field": f,
                                           "agent": norm(f, get(snaps["final"][aid], f)), "gold": norm(f, gold[(aid, f)]),
                                           "pass1": norm(f, get(snaps["pass1"][aid], f)),
                                           "cause": cause(snaps["final"][aid], f, notes.get((aid, f), "") if label == "human" else "")})
            res["misses_final"] = misses
            hits = []
            for part in ("test", "dev"):
                for aid in sp[part]:
                    for f in FIELDS:
                        if (aid, f) in gold and norm(f, get(snaps["pass1"][aid], f)) != norm(f, gold[(aid, f)]) \
                                and norm(f, get(snaps["final"][aid], f)) == norm(f, gold[(aid, f)]):
                            hits.append({"split": part, "id": aid, "field": f, "pass1": norm(f, get(snaps["pass1"][aid], f)),
                                         "final": norm(f, get(snaps["final"][aid], f))})
            res["fixed_by_loops"] = hits
        out[label] = res
    # human vs auditor agreement on the same rows
    common = set(hum) & set(aud)
    out["human_vs_auditor"] = {"n": len(common), "agree": sum(norm(f, hum[(a, f)]) == norm(f, aud[(a, f)]) for a, f in common)}
    # evidence support rate per snapshot (all 100 apps)
    sup = {}
    for s, recs in snaps.items():
        tot = ok = 0
        for r in recs.values():
            for g, evs in r.get("evidence", {}).items():
                if g == "composio":
                    continue
                for e in evs:
                    tot += 1
                    ok += e.get("support") in ("exact", "fuzzy", "entailed", "browser_exact", "browser_fuzzy")
        sup[s] = {"items": tot, "verified": ok, "rate": round(ok / tot, 3) if tot else None}
    out["evidence_support"] = sup
    p = cache.DATA / "loop_stats.json"
    out["loop_stats"] = json.loads(p.read_text()) if p.exists() else {}
    (cache.DATA / "accuracy.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("accuracy.json written; gold rows: human", len(hum), "auditor", len(aud))
    return out
