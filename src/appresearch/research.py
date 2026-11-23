"""Stage runner: discover pages -> emit LLM task -> (backend answers) -> ingest + validate."""
from __future__ import annotations

import json
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

from pydantic import ValidationError

from . import cache
from .apps import APPS
from .schema import Record
from .tools import composio_catalog as catalog
from .tools import composio_tools as web

PROMPTS = Path(__file__).parent / "prompts"
TASKS = cache.CACHE / "llm" / "tasks"
RESP = cache.CACHE / "llm" / "responses"
CONCURRENCY = 8

THIRD_PARTY = (
    "medium.com", "reddit.com", "stackoverflow.com", "youtube.com", "zapier.com", "rapidapi.com", "composio.dev",
    "pipedream.com", "make.com", "n8n.io", "g2.com", "capterra.com", "linkedin.com", "wikipedia.org", "quora.com",
    "dev.to", "postman.com", "apitracker.io", "merge.dev", "nango.dev", "unified.to", "getknit.dev", "x.com",
    "twitter.com", "facebook.com", "apideck.com", "rollout.com", "truto.one", "integrate.io", "pulsemcp.com",
    "mcp.so", "glama.ai", "smithery.ai", "mcpservers.org", "lobehub.com", "playbooks.com", "skywork.ai",
)

KEYWORDS = re.compile(
    r"(oauth|api[ _-]?key|token|authenticat|authoriz|scope|pricing|plan|enterprise|partner|approval|review|"
    r"rate limit|webhook|pagination|sandbox|test mode|endpoint|sdk|developer|mcp|model context)", re.I)


def domain(u: str) -> str:
    h = urlparse(u).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def root_domain(u: str) -> str:
    parts = domain(u).split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else domain(u)


def is_third_party(u: str) -> bool:
    d = domain(u)
    return any(d == t or d.endswith("." + t) for t in THIRD_PARTY)


def guess_official_root(results: list[dict], app: dict) -> str | None:
    tokens = [t for t in re.split(r"[^a-z0-9]+", app["name"].lower()) if len(t) > 2]
    cands = [root_domain(r["url"]) for r in results if not is_third_party(r["url"]) and "github.com" not in r["url"]]
    for c in cands:  # name token in domain wins
        if any(t in c.replace("-", "") for t in tokens):
            return c
    return Counter(cands).most_common(1)[0][0] if cands else None


def excerpt(text: str, budget: int = 9000) -> str:
    """Head of page + keyword windows, so the extractor sees auth/pricing passages on long pages."""
    if len(text) <= budget:
        return text
    head = text[:2500]
    windows, used = [], set()
    for m in KEYWORDS.finditer(text, 2500):
        s = max(2500, m.start() - 350)
        if any(abs(s - u) < 500 for u in used):
            continue
        used.add(s)
        windows.append(text[s : s + 700])
        if sum(map(len, windows)) > budget - 2500:
            break
    return head + "\n[...]\n" + "\n[...]\n".join(windows)


# ---------------------------------------------------------------- pass 1 discovery
def pass1_queries(app: dict) -> list[str]:
    n = app["name"]
    return [f"{n} API documentation developer", f"{n} API authentication OAuth API key pricing plan access",
            f"{n} MCP server model context protocol"]


def discover_pass1(app: dict) -> list[dict]:
    """Single sweep: 3 searches, <=5 pages. Returns fetched page records."""
    qd, qa, qm = pass1_queries(app)
    q_docs = web.search(qd, 8)
    q_access = web.search(qa, 8)
    q_mcp = web.search(qm, 6)
    official = guess_official_root(q_docs + q_access, app)
    picks: list[str] = []
    if app.get("hint_url"):
        picks.append(app["hint_url"])

    def add(results, k, need_official=True):
        c = 0
        for r in results:
            u = r["url"]
            if u in picks or is_third_party(u):
                continue
            if need_official and official and root_domain(u) != official:
                continue
            picks.append(u)
            c += 1
            if c >= k:
                return

    add(q_docs, 2)
    add(q_access, 2)
    add(q_mcp, 1, need_official=False)
    picks = picks[:5]
    with ThreadPoolExecutor(4) as ex:
        pages = list(ex.map(web.fetch, picks))
    return [{"url": p["url"], "status": p["status"], "via": p["via"], "file": web.page_path(p["url"]), "text": p["text"]} for p in pages]


def emit_task(stage: str, app: dict, pages: list[dict], prompt_file: str, extra: str = "") -> Path:
    prompt = (PROMPTS / prompt_file).read_text(encoding="utf-8")
    parts = [prompt, f"\n## App\nid: {app['id']}\nname: {app['name']}\ncategory: {app['category']}\n"
             f"hint_url (starting point only, may be wrong): {app.get('hint_url')}\n"
             f"known ambiguity to resolve with evidence: {app.get('ambiguity')}\n", extra, "\n## Pages\n"]
    for i, p in enumerate(pages, 1):
        body = excerpt(p["text"]) if p["text"] else "(fetch failed or empty: status %s)" % p["status"]
        parts.append(f"\n### PAGE {i}: {p['url']}  (status {p['status']})\n{body}\n")
    out = TASKS / stage / f"{app['id']}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(parts), encoding="utf-8")
    return out


def run_discovery(stage: str, apps: list[dict]) -> None:
    def one(a):
        pages = discover_pass1(a)
        emit_task(stage, a, pages, "pass1_extract.md")
        return a["id"], len(pages), sum(1 for p in pages if p["text"])

    with ThreadPoolExecutor(CONCURRENCY) as ex:
        for aid, n, ok in ex.map(one, apps):
            print(f"  {aid}: {ok}/{n} pages")


# ---------------------------------------------------------------- ingest
def _parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    s, e = text.find("{"), text.rfind("}")
    return json.loads(text[s : e + 1])


TRI_PATHS = [("sandbox_or_test_env",), ("api_surface", "webhooks"), ("api_surface", "pagination_documented"),
             ("api_surface", "rate_limits_documented"), ("api_surface", "breadth"), ("access",), ("mcp", "exists"),
             ("oauth_details", "scopes_granular"), ("oauth_details", "app_review_required")]
LIST_PATHS = [("auth_methods",), ("api_surface", "style"), ("api_surface", "official_sdks"), ("oauth_details", "flows")]


def normalize(raw: dict, rid: str) -> dict:
    """Type-only normalisation before strict validation: JSON null in a list field -> []. Logged; never adds values."""
    for path in LIST_PATHS:
        cur = raw
        for k in path[:-1]:
            cur = cur.get(k) if isinstance(cur, dict) else None
        if isinstance(cur, dict) and path[-1] in cur and cur[path[-1]] in (None, "unknown", "none_found"):
            cache.log_event("normalize", id=rid, field=".".join(path), change=f"{cur[path[-1]]!r}->[]")
            cur[path[-1]] = []
    for path in (("one_liner",), ("auth_notes",), ("access_notes",), ("needs_human_reason",), ("buildability", "rationale")):
        cur = raw
        for k in path[:-1]:
            cur = cur.get(k) if isinstance(cur, dict) else None
        if isinstance(cur, dict) and path[-1] in cur and cur[path[-1]] is None:
            cur[path[-1]] = ""
            cache.log_event("normalize", id=rid, field=".".join(path), change="null->''")
    od = raw.get("oauth_details")
    if isinstance(od, dict) and isinstance(od.get("flows"), list):
        syn = {"authorization_code": "auth_code", "pkce": "PKCE", "device_code": "device", "auth_code_pkce": "PKCE"}
        flows, dropped = [], []
        for f in od["flows"]:
            g = syn.get(str(f).lower(), f)
            (flows if g in ("auth_code", "client_credentials", "device", "PKCE") else dropped).append(g)
        if dropped or flows != od["flows"]:
            cache.log_event("normalize", id=rid, field="oauth_details.flows", change=f"{od['flows']}->{flows}; dropped {dropped}")
        od["flows"] = list(dict.fromkeys(flows))
        if dropped:
            raw["auth_notes"] = ((raw.get("auth_notes") or "") + f" Other OAuth flows: {', '.join(map(str, dropped))}.").strip()
    if raw.get("needs_human") is None:
        raw["needs_human"] = False
    if raw.get("confidence") is None:
        raw["confidence"] = {}
    for path in TRI_PATHS:
        cur = raw
        for k in path[:-1]:
            cur = cur.get(k) if isinstance(cur, dict) else None
        if isinstance(cur, dict) and path[-1] in cur and cur[path[-1]] is None:
            cur[path[-1]] = "unknown"
            cache.log_event("normalize", id=rid, field=".".join(path), change="null->'unknown'")
    return raw


def attach_fetch_meta(rec: dict) -> dict:
    """fetched_at comes from OUR cache, never from the model. Uncached cited URLs are fetched now."""
    for group, evs in (rec.get("evidence") or {}).items():
        for ev in evs:
            f = web.fetch(ev["url"])
            ev["fetched_at"] = f["fetched_at"]
            ev.setdefault("source_type", "third_party")
    return rec


def ingest(stage: str, apps: list[dict] | None = None) -> tuple[list[dict], list[str]]:
    apps = apps or APPS
    good, bad = [], []
    for a in apps:
        p = RESP / stage / f"{a['id']}.json"
        if not p.exists():
            bad.append(f"{a['id']}: missing response")
            continue
        try:
            raw = _parse_json(p.read_text(encoding="utf-8"))
            raw.update(id=a["id"], name=a["name"], category=a["category"])
            raw = normalize(raw, a["id"])
            raw = attach_fetch_meta(raw)
            has, ev = catalog.evidence_for(a)  # deterministic, from Composio SDK toolkit catalog
            raw["composio_existing_toolkit"] = has
            raw.setdefault("evidence", {})["composio"] = ev
            rec = Record.model_validate(raw)
            good.append(rec.model_dump())
        except (ValidationError, ValueError, KeyError) as e:
            bad.append(f"{a['id']}: {str(e)[:300]}")
    return good, bad


RETRY_MARK = "\n\n## RETRY"


def emit_retries(stage: str, bad: list[str]) -> int:
    """Reject-and-retry: keep the invalid attempt (<id>.attemptN.json) and re-emit the task with the validation error."""
    n = 0
    for b in bad:
        aid, _, err = b.partition(": ")
        if err == "missing response":
            continue
        resp, task = RESP / stage / f"{aid}.json", TASKS / stage / f"{aid}.md"
        k = 1
        while (RESP / stage / f"{aid}.attempt{k}.json").exists():
            k += 1
        if k > 2:  # max 2 retries -> leave invalid, flagged
            continue
        resp.rename(RESP / stage / f"{aid}.attempt{k}.json")
        body = task.read_text(encoding="utf-8").split(RETRY_MARK)[0]
        task.write_text(body + f"{RETRY_MARK} {k}\nYour previous JSON failed schema validation:\n{err[:800]}\n"
                        "Return the corrected full JSON object. Lists must be JSON arrays (use [] if none); "
                        "enums exactly as listed.\n", encoding="utf-8")
        cache.log_event("retry", stage=stage, id=aid, attempt=k, error=err[:300])
        n += 1
    return n


def save(name: str, records: list[dict]) -> Path:
    p = cache.DATA / name
    p.write_text(json.dumps(sorted(records, key=lambda r: r["id"]), ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def load(name: str) -> list[dict]:
    return json.loads((cache.DATA / name).read_text(encoding="utf-8"))
