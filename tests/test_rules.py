from appresearch import rubric
from appresearch.loops import l3_rules as L3
from appresearch.schema import Record


def base(**kw):
    r = {
        "id": "x", "name": "Acme", "category": "CRM & Sales", "docs_url": "https://developers.acme.com/docs",
        "auth_methods": ["api_key"], "access": "self_serve_free",
        "api_surface": {"style": ["rest"], "breadth": "broad", "approx_endpoint_count": None},
        "mcp": {"exists": "none_found", "url": None},
        "buildability": {"verdict": "BUILD_NOW", "main_blocker": "none"},
        "evidence": {"auth": [{"url": "https://developers.acme.com/auth", "quote": "Use your API key", "source_type": "official_docs", "fetched_at": "t"}]},
        "confidence": {"access": "high"},
    }
    r.update(kw)
    return r


def ok_fetch(url):
    return {"status": 200, "final_url": url, "text": "page"}


def dead_fetch(url):
    return {"status": 404, "final_url": url, "text": ""}


# ---------------- rubric
def test_rubric_build_now():
    assert rubric.verdict(base()) == "BUILD_NOW"


def test_rubric_paid_is_caveats():
    assert rubric.verdict(base(access="paid_plan_required", buildability={"main_blocker": "paid_plan_gate"})) == "BUILD_WITH_CAVEATS"


def test_rubric_partner_is_outreach():
    assert rubric.verdict(base(access="partner_or_contact_sales", buildability={"main_blocker": "partner_gate"})) == "BLOCKED_NEEDS_OUTREACH"


def test_rubric_enterprise_blocker_is_outreach_even_if_paid():
    assert rubric.verdict(base(access="paid_plan_required", buildability={"main_blocker": "enterprise_only"})) == "BLOCKED_NEEDS_OUTREACH"


def test_rubric_no_api():
    assert rubric.verdict(base(access="no_public_api", buildability={"main_blocker": "no_api"})) == "BLOCKED_NO_PUBLIC_API"


def test_rubric_cli_tool():
    assert rubric.verdict(base(access="no_public_api", buildability={"main_blocker": "cli_or_local_only"})) == "NOT_APPLICABLE_NOT_A_SERVICE"


def test_rubric_unknown_access_unclear():
    assert rubric.verdict(base(access="unknown")) == "UNCLEAR"


def test_rubric_narrow_self_serve_is_caveats():
    r = base()
    r["api_surface"]["breadth"] = "narrow"
    assert rubric.verdict(r) == "BUILD_WITH_CAVEATS"


# ---------------- L3 rules
def test_verdict_corrected_by_rubric():
    r, v = L3.check(base(access="partner_or_contact_sales", buildability={"verdict": "BUILD_NOW", "main_blocker": "partner_gate"}), ok_fetch)
    assert r["buildability"]["verdict"] == "BLOCKED_NEEDS_OUTREACH"
    assert any("per rubric" in x for x in v)


def test_oauth_without_endpoint_evidence_flags_low_confidence():
    rec = base(auth_methods=["oauth2"])
    r, v = L3.check(rec, ok_fetch)
    assert r["confidence"]["auth"] == "low"
    assert any("oauth2 claimed" in x for x in v)


def test_oauth_with_authorize_quote_passes():
    rec = base(auth_methods=["oauth2"])
    rec["evidence"]["auth"][0]["quote"] = "Redirect users to the /oauth/authorize endpoint"
    r, v = L3.check(rec, ok_fetch)
    assert not any("oauth2 claimed" in x for x in v)
    assert r["oauth_details"] is not None


def test_paid_without_pricing_evidence():
    rec = base(access="paid_plan_required", buildability={"verdict": "BUILD_WITH_CAVEATS", "main_blocker": "paid_plan_gate"})
    rec["evidence"]["access"] = [{"url": "https://acme.com/x", "quote": "Contact us", "source_type": "official_docs", "fetched_at": "t"}]
    r, v = L3.check(rec, ok_fetch)
    assert any("pricing evidence" in x for x in v)


def test_paid_with_pricing_page_passes():
    rec = base(access="paid_plan_required", buildability={"verdict": "BUILD_WITH_CAVEATS", "main_blocker": "paid_plan_gate"})
    rec["evidence"]["access"] = [{"url": "https://acme.com/pricing", "quote": "API access", "source_type": "pricing_page", "fetched_at": "t"}]
    _, v = L3.check(rec, ok_fetch)
    assert not any("pricing evidence" in x for x in v)


def test_official_mcp_on_third_party_domain_downgraded():
    rec = base(mcp={"exists": "official", "url": "https://mcp.so/server/acme"})
    r, _ = L3.check(rec, ok_fetch)
    assert r["mcp"]["exists"] == "community"


def test_official_mcp_on_vendor_github_org_kept():
    rec = base(mcp={"exists": "official", "url": "https://github.com/acme-inc/acme-mcp"})
    r, _ = L3.check(rec, ok_fetch)
    assert r["mcp"]["exists"] == "official"


def test_official_mcp_dead_url_unknown():
    rec = base(mcp={"exists": "official", "url": "https://developers.acme.com/mcp"})
    r, _ = L3.check(rec, dead_fetch)
    assert r["mcp"]["exists"] == "unknown"


def test_docs_marketing_page_flagged():
    _, v = L3.check(base(docs_url="https://acme.com/"), ok_fetch)
    assert any("marketing" in x for x in v)


def test_breadth_from_count():
    rec = base()
    rec["api_surface"].update(breadth="narrow", approx_endpoint_count=250)
    r, _ = L3.check(rec, ok_fetch)
    assert r["api_surface"]["breadth"] == "broad"


# ---------------- schema rule 1
def test_schema_claim_without_evidence_needs_human():
    r = Record.model_validate({"id": "x", "name": "A", "category": "c", "access": "self_serve_free", "evidence": {}})
    assert r.needs_human and "access" in r.needs_human_reason


def test_schema_rejects_bad_enum():
    import pytest
    with pytest.raises(Exception):
        Record.model_validate({"id": "x", "name": "A", "category": "c", "access": "free_forever"})


def test_official_mcp_405_counts_as_resolving():
    rec = base(mcp={"exists": "official", "url": "https://mcp.acme.com/mcp"})
    r, _ = L3.check(rec, lambda u: {"status": 405, "final_url": u, "text": ""})
    assert r["mcp"]["exists"] == "official"


def test_official_mcp_without_url_kept_with_vendor_evidence():
    rec = base(mcp={"exists": "official", "url": None})
    rec["evidence"]["mcp"] = [{"url": "https://developers.acme.com/mcp", "quote": "Acme MCP server", "source_type": "official_docs", "fetched_at": "t"}]
    r, _ = L3.check(rec, ok_fetch)
    assert r["mcp"]["exists"] == "official"
