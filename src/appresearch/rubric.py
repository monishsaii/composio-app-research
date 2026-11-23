"""Deterministic verdict rubric (also printed on the page and in the README).

Order matters; first matching rule wins:
 1. NOT_APPLICABLE_NOT_A_SERVICE  blocker == cli_or_local_only, or style is cli_only/sdk_only with access no_public_api
 2. BLOCKED_NO_PUBLIC_API         access == no_public_api, or blocker == no_api
 3. BLOCKED_NEEDS_OUTREACH        access == partner_or_contact_sales, or blocker in {partner_gate, enterprise_only}
 4. UNCLEAR                       access == unknown, or blocker == ambiguous_product
 5. BUILD_NOW                     access in {self_serve_free, self_serve_trial} AND blocker == none AND breadth != narrow
 6. BUILD_WITH_CAVEATS            everything else (paid tier, app review, admin approval, narrow API, auth complexity...)
"""
from __future__ import annotations

SELF_SERVE = {"self_serve_free", "self_serve_trial"}
GATED_ACCESS = {"paid_plan_required", "admin_approval", "app_review_required", "partner_or_contact_sales"}


def verdict(rec: dict) -> str:
    access = rec.get("access", "unknown")
    b = rec.get("buildability", {}) or {}
    blocker = b.get("main_blocker", "other")
    api = rec.get("api_surface", {}) or {}
    style = set(api.get("style") or [])
    breadth = api.get("breadth", "unknown")
    if blocker == "cli_or_local_only" or (style and style <= {"cli_only", "sdk_only"} and access == "no_public_api"):
        return "NOT_APPLICABLE_NOT_A_SERVICE"
    if access == "no_public_api" or blocker == "no_api":
        return "BLOCKED_NO_PUBLIC_API"
    if access == "partner_or_contact_sales" or blocker in ("partner_gate", "enterprise_only"):
        return "BLOCKED_NEEDS_OUTREACH"
    if access == "unknown" or blocker == "ambiguous_product":
        return "UNCLEAR"
    if access in SELF_SERVE and blocker == "none" and breadth != "narrow":
        return "BUILD_NOW"
    return "BUILD_WITH_CAVEATS"


def is_gated(rec: dict) -> bool:
    """'Gated' = a developer cannot get working credentials free and self-serve."""
    return rec.get("access") in GATED_ACCESS or rec.get("access") == "no_public_api"


RUBRIC_TEXT = __doc__
