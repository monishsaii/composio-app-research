"""Pattern analysis: every number here is computed from data/final.json (+ pass1.json for 'what changed')."""
from __future__ import annotations

import json
from collections import Counter

from . import cache, research, rubric
from .apps import APPS, CATEGORIES

VERDICTS = ["BUILD_NOW", "BUILD_WITH_CAVEATS", "BLOCKED_NEEDS_OUTREACH", "BLOCKED_NO_PUBLIC_API",
            "NOT_APPLICABLE_NOT_A_SERVICE", "UNCLEAR"]
ACCESS = ["self_serve_free", "self_serve_trial", "paid_plan_required", "admin_approval", "app_review_required",
          "partner_or_contact_sales", "no_public_api", "unknown"]
REGULATED = {"finance"}  # payments/banking/brokerage: PCI, KYC, financial-data regulation


def pct(k, n):
    return round(100 * k / n) if n else 0


def matrix(recs, row_key, col_key, rows, cols):
    m = {r: {c: 0 for c in cols} for r in rows}
    for r in recs:
        m[row_key(r)][col_key(r)] += 1
    return m


def headlines(a: dict, final: list, cat_key: dict) -> list[dict]:
    """Plain statements, each number computed here, each with a table filter."""
    n, v, ac = a["n"], a["verdicts"], a["access"]
    h = []
    ss = a["self_serve"]
    h.append({"text": f"{ss} of {n} apps give a developer working API credentials free and self-serve "
                      f"({ac['self_serve_free']} free, {ac['self_serve_trial']} via trial).",
              "filter": {"acc": "self_serve_free"}})
    gated = a["gated"]
    top_gate = max(("paid_plan_required", "app_review_required", "admin_approval", "partner_or_contact_sales", "no_public_api"), key=lambda k: ac[k])
    h.append({"text": f"{gated} of {n} are gated. The most common gate is {top_gate.replace('_', ' ')} ({ac[top_gate]} apps); "
                      f"only {ac['partner_or_contact_sales']} require partner or sales contact.",
              "filter": {"acc": top_gate}})
    auth = a["auth_single"]
    top = list(auth.items())[:2]
    h.append({"text": f"Auth is dominated by {top[0][0]} ({top[0][1]} apps) and {top[1][0]} ({top[1][1]}); "
                      f"{a['oauth']} apps support OAuth 2.0, so per-user OAuth is the norm Composio must handle.",
              "filter": {"auth": "oauth2"}})
    mcp = a["mcp"]
    h.append({"text": f"{mcp.get('official', 0)} of {n} vendors now publish an official MCP server; "
                      f"{mcp.get('community', 0)} more have only community servers.", "filter": {}})
    gap = a["composio_gap_build_now"]
    h.append({"text": f"{v['BUILD_NOW']} apps are BUILD_NOW. {len(gap)} of them have no Composio toolkit today: "
                      + ", ".join(x["name"] for x in gap[:6]) + ("…" if len(gap) > 6 else "") + ".",
              "filter": {"ver": "BUILD_NOW"}})
    reg = a["regulated_vs_not"]
    h.append({"text": f"Finance is the most gated category among those with known access: {reg['regulated']['gated']} of "
                      f"{reg['regulated']['n']} finance apps are gated vs {reg['other']['gated']} of {reg['other']['n']} elsewhere."
              if reg["regulated"]["n"] and reg["regulated"]["gated"] / reg["regulated"]["n"] >= max(
                  (g["gated"] / g["known"]) for g in a["gating_by_category"].values() if g["known"]) else
              f"Finance apps: {reg['regulated']['gated']} of {reg['regulated']['n']} gated vs {reg['other']['gated']} of "
              f"{reg['other']['n']} in other categories.", "filter": {"cat": "Finance/Fintech"}})
    ch = a["changed_pass1_to_final"]
    vch = sum(1 for c in ch if "verdict" in c["changes"])
    h.append({"text": f"Verification changed the verdict for {vch} of {n} apps versus the single-shot pass 1; "
                      f"access went from {a['pass1_unknown_access']} unknown to {ac['unknown']} unknown.",
              "filter": {}})
    return h


def main() -> dict:
    final = research.load("final.json")
    pass1 = {r["id"]: r for r in research.load("pass1.json")}
    cat_key = {a["id"]: a["category_key"] for a in APPS}
    n = len(final)
    by_v = Counter(r["buildability"]["verdict"] for r in final)
    by_a = Counter(r["access"] for r in final)
    auth_single = Counter(m for r in final for m in r.get("auth_methods") or [])
    auth_combo = Counter("+".join(sorted(r.get("auth_methods") or [])) or "unknown" for r in final)
    blockers = Counter(r["buildability"]["main_blocker"] for r in final if r["buildability"]["main_blocker"] != "none")
    mcp = Counter((r.get("mcp") or {}).get("exists", "unknown") for r in final)
    composio = sum(1 for r in final if r.get("composio_existing_toolkit") is True)
    gated = [r for r in final if rubric.is_gated(r)]
    known_access = [r for r in final if r["access"] != "unknown"]
    self_serve = [r for r in final if r["access"] in rubric.SELF_SERVE]
    oauth = [r for r in final if "oauth2" in (r.get("auth_methods") or [])]

    cat_access = matrix(final, lambda r: cat_key[r["id"]], lambda r: r["access"], list(CATEGORIES), ACCESS)
    cat_verdict = matrix(final, lambda r: cat_key[r["id"]], lambda r: r["buildability"]["verdict"], list(CATEGORIES), VERDICTS)
    gating_by_cat = {}
    for c in CATEGORIES:
        rs = [r for r in final if cat_key[r["id"]] == c and r["access"] != "unknown"]
        g = sum(1 for r in rs if rubric.is_gated(r))
        gating_by_cat[c] = {"gated": g, "known": len(rs), "pct": pct(g, len(rs))}
    reg = [r for r in known_access if cat_key[r["id"]] in REGULATED]
    nonreg = [r for r in known_access if cat_key[r["id"]] not in REGULATED]
    mcp_by_cat = {c: Counter((r.get("mcp") or {}).get("exists", "unknown") for r in final if cat_key[r["id"]] == c) for c in CATEGORIES}

    def row(r):
        return {"id": r["id"], "name": r["name"], "category": r["category"], "access": r["access"],
                "blocker": r["buildability"]["main_blocker"], "verdict": r["buildability"]["verdict"],
                "tools": r["buildability"].get("est_tool_count_if_built"), "composio": r.get("composio_existing_toolkit"),
                "mcp": (r.get("mcp") or {}).get("exists"), "notes": (r.get("access_notes") or "")[:220],
                "docs_url": r.get("docs_url")}

    easy = sorted([row(r) for r in final if r["buildability"]["verdict"] == "BUILD_NOW"],
                  key=lambda x: (x["composio"] is True, -(x["tools"] or 0)))
    outreach = [row(r) for r in final if r["buildability"]["verdict"] == "BLOCKED_NEEDS_OUTREACH"]
    changed = []
    for r in final:
        p = pass1.get(r["id"])
        if not p:
            continue
        diffs = {}
        for k, get in (("verdict", lambda x: x["buildability"]["verdict"]), ("access", lambda x: x["access"]),
                       ("blocker", lambda x: x["buildability"]["main_blocker"]),
                       ("mcp", lambda x: (x.get("mcp") or {}).get("exists"))):
            if get(p) != get(r):
                diffs[k] = [get(p), get(r)]
        if diffs:
            changed.append({"id": r["id"], "name": r["name"], "changes": diffs})
    needs_human = [r["id"] for r in final if r.get("needs_human")]
    composio_gap_build_now = [x for x in easy if x["composio"] is not True]

    out = {
        "generated_at": cache.now_iso(), "n": n,
        "verdicts": {v: by_v.get(v, 0) for v in VERDICTS},
        "access": {a: by_a.get(a, 0) for a in ACCESS},
        "auth_single": dict(auth_single.most_common()), "auth_combos": dict(auth_combo.most_common(12)),
        "blockers": dict(blockers.most_common()), "mcp": dict(mcp), "mcp_by_category": {c: dict(v) for c, v in mcp_by_cat.items()},
        "composio_existing": composio, "self_serve": len(self_serve), "gated": len(gated), "known_access": len(known_access),
        "oauth": len(oauth),
        "category_access": cat_access, "category_verdict": cat_verdict, "gating_by_category": gating_by_cat,
        "regulated_vs_not": {"regulated": {"gated": sum(map(rubric.is_gated, reg)), "n": len(reg)},
                             "other": {"gated": sum(map(rubric.is_gated, nonreg)), "n": len(nonreg)}},
        "easy_wins": easy, "composio_gap_build_now": composio_gap_build_now, "outreach": outreach,
        "changed_pass1_to_final": changed, "needs_human": needs_human,
        "categories": CATEGORIES,
    }
    out["pass1_unknown_access"] = sum(1 for r in pass1.values() if r["access"] == "unknown")
    out["headlines"] = headlines(out, final, cat_key)
    out["defeated"] = [{"id": r["id"], "name": r["name"],
                        "why": (r.get("needs_human_reason") or "unresolved after all loops")[:220]}
                       for r in final if r["buildability"]["verdict"] == "UNCLEAR" or r["access"] == "unknown"]
    (cache.DATA / "analysis.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"analysis.json: {n} apps; verdicts {dict(by_v)}")
    return out
