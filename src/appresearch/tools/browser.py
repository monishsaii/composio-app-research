"""L4 browser tool (Playwright, headless Chromium). OBSERVE ONLY: no sign-ups, no form submission, no paywall bypass.

Composio's browser toolkits (browserbase/browser_use/hyperbrowser/anchor_browser) all require their own paid API keys
(checked in the SDK catalog, 2026-11-23), so with a $0 budget this uses local Playwright; noted in README.
"""
from __future__ import annotations

from .. import cache
from .http_fetch import html_to_text

SHOTS = cache.ROOT / "data" / "screenshots"


def render(url: str, app_id: str, idx: int) -> dict:
    k = cache.key("browser", url)
    hit = cache.get("browser", k)
    if hit:
        return hit
    from playwright.sync_api import sync_playwright

    SHOTS.mkdir(parents=True, exist_ok=True)
    shot = SHOTS / f"{app_id}-{idx}.png"
    rec = {"url": url, "status": 0, "final_url": url, "text": "", "screenshot": None}
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            page = b.new_page(viewport={"width": 1280, "height": 900})
            resp = page.goto(url, wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(1500)
            rec["status"] = resp.status if resp else 0
            rec["final_url"] = page.url
            rec["title"] = page.title()
            body_text = page.inner_text("body")
            rec["text"] = body_text if len(body_text) > 300 else html_to_text(page.content())
            page.screenshot(path=str(shot), full_page=False)
            rec["screenshot"] = str(shot.relative_to(cache.ROOT)).replace("\\", "/")
            b.close()
    except Exception as e:
        rec["error"] = str(e)[:300]
    rec["fetched_at"] = cache.now_iso()
    rec["via"] = "playwright:chromium"
    rec["text"] = rec["text"][:120_000]
    cache.put("browser", k, rec)
    cache.log_event("browser", url=url, status=rec["status"], chars=len(rec["text"]))
    return rec
