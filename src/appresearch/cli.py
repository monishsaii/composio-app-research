"""appresearch CLI.  python -m appresearch <command>"""
from __future__ import annotations

import argparse
import json
import sys

from dotenv import load_dotenv

from . import cache

load_dotenv(cache.ROOT / ".env")


def cmd_research(a):
    from . import research
    from .apps import APPS, find
    from .llm import backend

    apps = APPS if a.all else [find(x) for x in a.app]
    with cache.Timer(f"{a.stage}:discover"):
        if not a.ingest_only:
            research.run_discovery(a.stage, apps)
    if backend.report_pending(a.stage) and not a.ingest_only:
        print("Answer the task(s) with Claude Code subagents, then: python -m appresearch research --app ... --ingest-only")
        return
    with cache.Timer(f"{a.stage}:ingest"):
        good, bad = research.ingest(a.stage, apps)
    for b in bad:
        print("INVALID/MISSING:", b.splitlines()[0][:200])
    if a.retry_invalid:
        print(f"re-emitted {research.emit_retries(a.stage, bad)} retry task(s)")
    if a.all:
        research.save("pass1.json", good)
    else:
        for r in good:
            print(json.dumps(r, indent=1, ensure_ascii=False))
    print(f"ingested {len(good)} valid, {len(bad)} invalid/missing")


def cmd_fetch(a):
    from .tools import composio_tools as web

    r = web.fetch(a.url, force=a.force)
    print(json.dumps({k: r[k] for k in ("url", "final_url", "status", "via", "fetched_at")}, indent=1))
    print("cached text file:", web.page_path(a.url), f"({len(r['text'])} chars)")
    if a.show:
        print(r["text"][: a.show])


def cmd_search(a):
    from .tools import composio_tools as web

    for r in web.search(a.query, a.n):
        print(r["url"], "|", r["title"][:80])


def cmd_queries(a):
    from . import research
    from .apps import find

    for q in research.pass1_queries(find(a.app)):
        print(q)


def cmd_record_search(a):
    """Record externally-run search results (Claude Code WebSearch) into the cache.
    Usage: record-search "query" URL [URL ...]   (optionally URL|title)"""
    from .tools import composio_tools as web

    res = []
    for u in a.urls:
        url, _, title = u.partition("|")
        if url.startswith("http"):
            res.append({"url": url.strip(), "title": title.strip(), "snippet": ""})
    web.record_search(a.query, res)
    print(f"recorded {len(res)} results for: {a.query}")


def cmd_catalog(a):
    from .apps import APPS
    from .tools import composio_catalog as cat

    items = cat.refresh() if a.refresh else cat.load()["items"]
    print(f"{len(items)} toolkits in catalog")
    hits = [(x["name"], (cat.lookup(x) or {}).get("slug")) for x in APPS]
    print(f"{sum(1 for _, s in hits if s)}/100 apps have a Composio toolkit")
    for n, s in hits:
        print(f"  {n:28} {s or '-'}")


def cmd_smoke(a):
    from .tools import composio_tools as web

    print(json.dumps(web.smoke(), indent=1))


def main(argv=None):
    p = argparse.ArgumentParser(prog="appresearch")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("research", help="run a research stage for one/all apps")
    g = r.add_mutually_exclusive_group(required=True)
    g.add_argument("--app", action="append", help="app name (repeatable)")
    g.add_argument("--all", action="store_true")
    r.add_argument("--stage", default="pass1")
    r.add_argument("--ingest-only", action="store_true")
    r.add_argument("--retry-invalid", action="store_true", help="move invalid responses aside and re-emit tasks with the error")
    r.set_defaults(fn=cmd_research)

    f = sub.add_parser("fetch", help="fetch+cache a URL (the only way subagents may add pages)")
    f.add_argument("url")
    f.add_argument("--force", action="store_true")
    f.add_argument("--show", type=int, default=0)
    f.set_defaults(fn=cmd_fetch)

    s = sub.add_parser("search", help="search via Composio (cached)")
    s.add_argument("query")
    s.add_argument("-n", type=int, default=8)
    s.set_defaults(fn=cmd_search)

    sub.add_parser("smoke", help="check Composio connectivity").set_defaults(fn=cmd_smoke)

    q = sub.add_parser("queries", help="print the pass-1 search queries for an app")
    q.add_argument("--app", required=True)
    q.set_defaults(fn=cmd_queries)

    rs = sub.add_parser("record-search", help="record external search results into the cache")
    rs.add_argument("query")
    rs.add_argument("urls", nargs="*")
    rs.set_defaults(fn=cmd_record_search)

    c = sub.add_parser("catalog", help="Composio toolkit catalog lookup for all 100 apps")
    c.add_argument("--refresh", action="store_true")
    c.set_defaults(fn=cmd_catalog)

    from . import cli_ext  # verify/analyze/accuracy/build-site/split/human-check

    cli_ext.register(sub)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
