"""Web tools for the agent: Composio COMPOSIO_SEARCH toolkit first, direct fallback second.

Composio toolkit `composio_search` is no-auth (Composio-managed). Tools used:
  COMPOSIO_SEARCH_TAVILY            -> ranked web results
  COMPOSIO_SEARCH_DUCK_DUCK_GO      -> ranked web results (secondary)
  COMPOSIO_SEARCH_FETCH_URL_CONTENT -> page -> markdown (Exa)
Every call is cached; every fallback is logged to cache/events.jsonl.
"""
from __future__ import annotations

import json
import os
import re
import threading
from typing import Any

from .. import cache
from . import http_fetch

_client = None
_lock = threading.Lock()
USER_ID = os.environ.get("COMPOSIO_USER_ID", "appresearch-agent")


def _composio():
    global _client
    with _lock:
        if _client is None:
            if not os.environ.get("COMPOSIO_API_KEY"):
                return None
            from composio import Composio

            _client = Composio(api_key=os.environ["COMPOSIO_API_KEY"], toolkit_versions={"composio_search": "latest"})
        return _client


def _execute(slug: str, arguments: dict) -> dict | None:
    c = _composio()
    if c is None:
        return None
    try:
        r = c.tools.execute(slug, user_id=USER_ID, arguments=arguments, dangerously_skip_version_check=True)
    except Exception as e:  # network, quota, schema
        cache.log_event("composio_error", tool=slug, error=str(e)[:300])
        return None
    if not r or not r.get("successful", True) or r.get("error"):
        cache.log_event("composio_error", tool=slug, error=str(r.get("error") if r else "empty")[:300])
        return None
    return r.get("data", r)


def _walk_results(data: Any) -> list[dict]:
    """Normalise varied result payloads into [{url,title,snippet}]."""
    out: list[dict] = []

    def visit(x):
        if isinstance(x, dict):
            u = x.get("url") or x.get("link") or x.get("href")
            if isinstance(u, str) and u.startswith("http"):
                out.append({"url": u, "title": x.get("title", ""), "snippet": (x.get("content") or x.get("snippet") or x.get("body") or "")[:400]})
                return
            for v in x.values():
                visit(v)
        elif isinstance(x, list):
            for v in x:
                visit(v)

    visit(data)
    seen, uniq = set(), []
    for r in out:
        if r["url"] not in seen:
            seen.add(r["url"])
            uniq.append(r)
    return uniq


_RETIRED: dict[str, str] = {}  # slug -> error, memoised so we don't hammer a retired toolkit


def _try_composio(slug: str, args: dict):
    if slug in _RETIRED:
        return None
    data = _execute(slug, args)
    if data is None:
        # inspect last logged error for 410/403 and memoise
        try:
            last = (cache.CACHE / "events.jsonl").read_text(encoding="utf-8").strip().splitlines()[-1]
            if '"410' in last or "retired" in last or '"403' in last:
                _RETIRED[slug] = last
        except Exception:
            pass
    return data


class SearchNotRecorded(RuntimeError):
    pass


def search_key(query: str) -> str:
    return cache.key("search", query.strip().lower())


def record_search(query: str, results: list[dict], via: str = "fallback:claude_code_websearch") -> None:
    """Store search results produced outside Python (Claude Code WebSearch) in the same cache."""
    cache.put("search", search_key(query), {"query": query, "via": via, "at": cache.now_iso(), "results": results})
    cache.log_event("fallback", kind="search", via=via, query=query, n=len(results))


def search(query: str, n: int = 8, allow_missing: bool = False) -> list[dict]:
    """Composio search first (COMPOSIO_SEARCH_*); then a recorded fallback search; else raise.

    As of 2026-11-23 every COMPOSIO_SEARCH version returns HTTP 410 'retired', so in practice results come
    from recorded Claude Code WebSearch calls (via="fallback:claude_code_websearch"). See README.
    """
    k = search_key(query)
    hit = cache.get("search", k)
    if hit is not None:
        return hit["results"][:n]
    for slug, args in (("COMPOSIO_SEARCH_TAVILY", {"query": query, "max_results": n}),
                       ("COMPOSIO_SEARCH_DUCK_DUCK_GO", {"query": query})):
        data = _try_composio(slug, args)
        if data is not None:
            results = _walk_results(data)[:n]
            if results:
                cache.put("search", k, {"query": query, "via": f"composio:{slug}", "at": cache.now_iso(), "results": results})
                cache.log_event("search", via=f"composio:{slug}", query=query, n=len(results))
                return results
    results = http_fetch.ddg_search(query, n)
    if results:
        record_search(query, results, via="fallback:duckduckgo_html")
        return results
    if allow_missing:
        return []
    raise SearchNotRecorded(query)


def fetch(url: str, force: bool = False) -> dict:
    """Return {url, final_url, status, text, via, fetched_at}. Text is markdown/plain."""
    k = cache.key("fetch", url)
    hit = None if force else cache.get("fetch", k)
    if hit is not None:
        return hit
    if os.environ.get("APPRESEARCH_OFFLINE"):
        raise RuntimeError(f"offline replay attempted a network fetch: {url}")
    rec = None
    # Direct fetch first gives us HTTP status (needed by L3); Composio fetch for JS/blocked pages.
    direct = http_fetch.fetch(url)
    if direct["status"] == 200 and len(direct["text"]) > 400:
        rec = {**direct, "via": "direct:httpx"}
    else:
        data = _try_composio("COMPOSIO_SEARCH_FETCH_URL_CONTENT", {"urls": [url]})
        text = _extract_text(data) if data is not None else ""
        if len(text) > 200:
            rec = {**direct, "text": text, "via": "composio:COMPOSIO_SEARCH_FETCH_URL_CONTENT", "composio_used": True}
        else:
            rec = {**direct, "via": "direct:httpx(thin)"}
    rec["fetched_at"] = cache.now_iso()
    rec["text"] = rec["text"][:120_000]
    cache.put("fetch", k, rec)
    cache.log_event("fetch", via=rec["via"], url=url, status=rec["status"], chars=len(rec["text"]))
    return rec


def _extract_text(data: Any) -> str:
    texts: list[str] = []

    def visit(x):
        if isinstance(x, dict):
            for key in ("text", "markdown", "content"):
                if isinstance(x.get(key), str) and len(x[key]) > 50:
                    texts.append(x[key])
                    return
            for v in x.values():
                visit(v)
        elif isinstance(x, list):
            for v in x:
                visit(v)

    visit(data)
    return "\n\n".join(texts)


def page_path(url: str) -> str:
    """Path to the cached fetch file (what subagents read)."""
    return str(cache.path("fetch", cache.key("fetch", url)))


def smoke() -> dict:
    out = {"composio_key": bool(os.environ.get("COMPOSIO_API_KEY"))}
    out["tavily"] = _execute("COMPOSIO_SEARCH_TAVILY", {"query": "Notion API documentation", "max_results": 3}) is not None
    d = _execute("COMPOSIO_SEARCH_FETCH_URL_CONTENT", {"urls": ["https://developers.notion.com/"]})
    out["fetch_chars"] = len(_extract_text(d)) if d else 0
    return out


if __name__ == "__main__":
    print(json.dumps(smoke(), indent=1))
