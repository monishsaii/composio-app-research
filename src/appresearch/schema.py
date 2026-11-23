"""Record schema (pydantic). Invalid LLM output is rejected and retried."""
from __future__ import annotations

from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

Tri = Union[bool, Literal["unknown"]]
SourceType = Literal["official_docs", "pricing_page", "official_repo", "third_party", "none"]
Conf = Literal["high", "medium", "low"]

AuthMethod = Literal[
    "oauth2", "api_key", "basic", "bearer_token", "jwt_service_account",
    "hmac_signature", "session_cookie", "none", "other",
]
OAuthFlow = Literal["auth_code", "client_credentials", "device", "PKCE"]
Access = Literal[
    "self_serve_free", "self_serve_trial", "paid_plan_required", "admin_approval",
    "app_review_required", "partner_or_contact_sales", "no_public_api", "unknown",
]
Style = Literal["rest", "graphql", "soap", "sdk_only", "cli_only", "websocket", "other"]
Breadth = Literal["broad", "medium", "narrow", "none", "unknown"]
McpExists = Literal["official", "community", "none_found", "unknown"]
Verdict = Literal[
    "BUILD_NOW", "BUILD_WITH_CAVEATS", "BLOCKED_NEEDS_OUTREACH", "BLOCKED_NO_PUBLIC_API",
    "NOT_APPLICABLE_NOT_A_SERVICE", "UNCLEAR",
]
Blocker = Literal[
    "none", "partner_gate", "paid_plan_gate", "app_review", "enterprise_only", "no_api",
    "unstable_or_undocumented_api", "auth_complexity", "regulatory_or_pci",
    "cli_or_local_only", "ambiguous_product", "other",
]
Effort = Literal["S", "M", "L", "XL"]

FIELD_GROUPS = ["identity", "auth", "access", "sandbox", "api_surface", "mcp", "buildability", "composio"]


class Evidence(BaseModel):
    url: str
    quote: str = Field(description="<=25 words, verbatim preferred")
    source_type: SourceType
    fetched_at: str
    support: Optional[str] = None  # set by L1: exact|fuzzy|entailed|unsupported|unfetchable

    @field_validator("quote")
    @classmethod
    def _short(cls, v: str) -> str:
        if len(v.split()) > 30:  # 25 + small tolerance; truncate rather than reject
            v = " ".join(v.split()[:25])
        return v


class OAuthDetails(BaseModel):
    flows: list[OAuthFlow] = []
    scopes_granular: Tri = "unknown"
    app_review_required: Tri = "unknown"


class ApiSurface(BaseModel):
    style: list[Style] = []
    breadth: Breadth = "unknown"
    approx_endpoint_count: Optional[int] = None
    webhooks: Tri = "unknown"
    pagination_documented: Tri = "unknown"
    rate_limits_documented: Tri = "unknown"
    official_sdks: list[str] = []


class Mcp(BaseModel):
    exists: McpExists = "unknown"
    url: Optional[str] = None


class Buildability(BaseModel):
    verdict: Verdict = "UNCLEAR"
    main_blocker: Blocker = "other"
    rationale: str = ""
    est_tool_count_if_built: Optional[int] = None
    est_effort: Effort = "M"


class Record(BaseModel):
    id: str
    name: str
    category: str
    one_liner: str = ""
    docs_url: Optional[str] = None
    openapi_spec_url: Optional[str] = None
    auth_methods: list[AuthMethod] = []
    auth_notes: str = ""
    oauth_details: Optional[OAuthDetails] = None
    access: Access = "unknown"
    access_notes: str = ""
    sandbox_or_test_env: Tri = "unknown"
    api_surface: ApiSurface = ApiSurface()
    mcp: Mcp = Mcp()
    buildability: Buildability = Buildability()
    composio_existing_toolkit: Tri = "unknown"
    evidence: dict[str, list[Evidence]] = {}
    confidence: dict[str, Conf] = {}
    needs_human: bool = False
    needs_human_reason: str = ""
    flags: list[str] = []  # appended by loops

    @model_validator(mode="after")
    def _evidence_rule(self):
        """Non-negotiable rule 1: any non-unknown group must carry evidence, else needs_human."""
        missing = [g for g in self.claimed_groups() if not self.evidence.get(g)]
        if missing:
            self.needs_human = True
            msg = f"no evidence for: {','.join(missing)}"
            if msg not in self.needs_human_reason:
                self.needs_human_reason = (self.needs_human_reason + "; " + msg).strip("; ")
        return self

    def claimed_groups(self) -> list[str]:
        g = []
        if self.auth_methods:
            g.append("auth")
        if self.access != "unknown":
            g.append("access")
        if self.sandbox_or_test_env != "unknown":
            g.append("sandbox")
        if self.api_surface.breadth != "unknown":
            g.append("api_surface")
        if self.mcp.exists not in ("unknown", "none_found"):
            g.append("mcp")
        if self.composio_existing_toolkit is True:
            g.append("composio")
        return g


def json_schema() -> dict:
    return Record.model_json_schema()
