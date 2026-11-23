"""verify / split / analyze / accuracy / human-check / build-site commands."""
from __future__ import annotations

import json

from . import cache

LOOPS = ["L1", "L2", "L3", "L4", "L5"]
INPUT = {"L1": "pass1.json", "L2": "after_L1.json", "L3": "after_L2.json", "L4": "after_L3.json", "L5": "after_L4.json"}


def _stats(loop: str, d: dict) -> None:
    p = cache.DATA / "loop_stats.json"
    s = json.loads(p.read_text()) if p.exists() else {}
    s[loop] = d
    p.write_text(json.dumps(s, indent=1))


def _pending(stage: str, backend=None) -> bool:
    from .llm import backend as B

    return B.report_pending(stage) > 0


def run_loop(loop: str, backend: str | None = None, refetch: bool = True) -> bool:
    from . import research
    from .loops import l1_evidence as L1, l2_second_pass as L2, l3_rules as L3, l4_browser as L4, l5_adjudicate as L5
    from .tools import composio_tools as web

    recs = research.load(INPUT[loop])
    with cache.Timer(f"verify:{loop}"):
        if loop == "L1":
            marker = cache.CACHE / "llm" / "l1_refetched.flag"
            recs1, s1 = L1.first_pass(recs, refetch=refetch and not marker.exists())
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text(cache.now_iso())
            if _pending(L1.ENTAIL_STAGE, backend):
                return False
            out, s2 = L1.finalize(recs1)
            _stats("L1", {**s1, **s2})
        elif loop == "L2":
            L2.emit(recs)
            if _pending(L2.STAGE, backend):
                return False
            out, s, l2_raw = L2.merge(recs)
            research.save("l2_raw.json", list(l2_raw.values()))
            _stats("L2", s)
        elif loop == "L3":
            out, viol = [], {}
            for r in recs:
                r2, v = L3.check(r, web.fetch)
                out.append(r2)
                if v:
                    viol[r["id"]] = v
            counts = {}
            for vs in viol.values():
                for v in vs:
                    k = v.split(":")[0]
                    counts[k] = counts.get(k, 0) + 1
            _stats("L3", {"records_with_violations": len(viol), "by_rule": counts})
            (cache.DATA / "l3_violations.json").write_text(json.dumps(viol, indent=1))
        elif loop == "L4":
            ids = L4.select(recs)
            out, s = L4.run(recs, ids)
            _stats("L4", {**s, "selected": ids})
        elif loop == "L5":
            L5.emit(recs)
            if _pending(L5.STAGE, backend):
                return False
            out, s, queue = L5.apply(recs)
            final = []
            for r in out:  # rules again so verdict follows the rubric after adjudication
                r2, _ = L3.check(r, web.fetch)
                final.append(r2)
            out = final
            queued = {}
            for q in queue:
                queued.setdefault(q["id"], []).append(q["field"])
            for r in out:  # recompute from the FINAL state (pass-1 flags are stale by now)
                why = []
                if r["id"] in queued:
                    why.append("unresolved after L5: " + ", ".join(queued[r["id"]]))
                if r["access"] == "unknown":
                    why.append("access unknown")
                if r["buildability"]["verdict"] == "UNCLEAR":
                    why.append("verdict UNCLEAR")
                missing = [g for g in ("auth", "access") if (g == "auth" and r.get("auth_methods") or g == "access" and r["access"] != "unknown") and not (r.get("evidence") or {}).get(g)]
                if missing:
                    why.append("no evidence for: " + ", ".join(missing))
                r["needs_human"], r["needs_human_reason"] = bool(why), "; ".join(why)
            L5.write_queue(queue, out)
            _stats("L5", {**s, "queue": len(queue)})
            research.save("final.json", out)
    research.save(f"after_{loop}.json", out)
    print(f"  {loop} done -> data/after_{loop}.json")
    return True


def cmd_verify(a):
    loops = LOOPS if a.all else [a.loop]
    for lp in loops:
        print(f"== {lp}")
        if not run_loop(lp, None, refetch=not a.no_refetch):
            return


def cmd_split(a):
    from . import split

    print(json.dumps(split.make_split() if a.make else split.load(), indent=1))


def cmd_accuracy(a):
    from . import accuracy

    accuracy.main()


def cmd_analyze(a):
    from . import analyze

    analyze.main()


def cmd_human_check(a):
    from . import human

    human.main()


def cmd_build_site(a):
    from .site import build

    build.main()


def cmd_replay(a):
    """OFFLINE REPLAY: no API keys, no network. Recomputes verification summaries, analysis and the site from
    committed data/*.json. This is NOT fresh AI research (see README: 'Fresh research')."""
    import os

    os.environ["APPRESEARCH_OFFLINE"] = "1"
    from . import accuracy, analyze
    from .site import build

    accuracy.main()
    analyze.main()
    build.main()
    print("offline replay complete: data/accuracy.json, data/analysis.json, site/index.html")


def cmd_trace(a):
    from . import trace
    from .apps import find

    print(trace.write(find(a.app)["id"]))


def register(sub):
    sub.add_parser("replay", help="OFFLINE: rebuild accuracy, analysis and site from committed data (no keys/network)").set_defaults(fn=cmd_replay)
    t = sub.add_parser("trace", help="write data/traces/<app>.md: queries, sources, extraction, validation, final")
    t.add_argument("--app", required=True)
    t.set_defaults(fn=cmd_trace)
    v = sub.add_parser("verify", help="run verification loops L1..L5 (resumable)")
    g = v.add_mutually_exclusive_group(required=True)
    g.add_argument("--loop", choices=LOOPS)
    g.add_argument("--all", action="store_true")
    v.add_argument("--no-refetch", action="store_true", help="L1: use cached pages instead of re-fetching")
    v.set_defaults(fn=cmd_verify)
    s = sub.add_parser("split", help="show (or --make) the gold DEV/TEST split")
    s.add_argument("--make", action="store_true")
    s.set_defaults(fn=cmd_split)
    sub.add_parser("accuracy", help="compute accuracy from pass1/after_L*/final vs gold").set_defaults(fn=cmd_accuracy)
    sub.add_parser("analyze", help="pattern analysis -> data/analysis.json").set_defaults(fn=cmd_analyze)
    sub.add_parser("human-check", help="generate human_check.csv/.md + auditor tasks").set_defaults(fn=cmd_human_check)
    sub.add_parser("build-site", help="build site/index.html").set_defaults(fn=cmd_build_site)
