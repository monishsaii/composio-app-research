"""Direct HTTP fallback (httpx + trafilatura) and DuckDuckGo HTML search fallback."""
from __future__ import annotations

import html as htmllib
import re
from urllib.parse import parse_qs, unquote, urlparse

import httpx

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36 appresearch/0.1"


def _client() -> httpx.Client:
    return httpx.Client(follow_redirects=True, timeout=25, headers={"User-Agent": UA, "Accept-Language": "en-US,en"})


def html_to_text(html: str) -> str:
    try:
        import trafilatura

        t = trafilatura.extract(html, include_links=False, include_tables=True, favor_recall=True)
        if t and len(t) > 200:
            return t
    except Exception:
        pass
    t = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", html)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", htmllib.unescape(t)).strip()


def fetch(url: str) -> dict:
    try:
        with _client() as c:
            r = c.get(url)
        ctype = r.headers.get("content-type", "")
        if "html" in ctype or "xml" in ctype or ctype == "":
            text = html_to_text(r.text)
        elif "json" in ctype or "yaml" in ctype or "text" in ctype:
            text = r.text
        else:
            text = ""
        return {"url": url, "final_url": str(r.url), "status": r.status_code, "content_type": ctype, "text": text}
    except Exception as e:
        return {"url": url, "final_url": url, "status": 0, "content_type": "", "text": "", "error": str(e)[:200]}


def ddg_search(query: str, n: int = 8) -> list[dict]:
    try:
        with _client() as c:
            r = c.post("https://html.duckduckgo.com/html/", data={"q": query})
        out = []
        for m in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r.text, re.S):
            href = htmllib.unescape(m.group(1))
            if "uddg=" in href:
                href = unquote(parse_qs(urlparse(href).query).get("uddg", [href])[0])
            out.append({"url": href, "title": re.sub("<[^>]+>", "", m.group(2)), "snippet": ""})
            if len(out) >= n:
                break
        return out
    except Exception:
        return []
