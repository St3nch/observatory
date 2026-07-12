"""Local-only C2 first-slice validation model.

M12 boundary:
- no provider calls
- no provider clients
- no database connections
- no API/MCP exposure
- no dashboard code
- no customer data
- no strategy/recommendation storage

This module represents the first executable C2 spine with pure Python data
objects and validation behavior. It is deliberately fixture-based and does
not persist anything.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from hashlib import sha256
from typing import Iterable, Literal, Sequence
from uuid import uuid4

ALLOWED_SCOPE_CLASSES = {"internal_fixture", "owner_controlled_fixture"}
ALLOWED_SOURCE_FAMILIES = {"controlled_public_fixture", "owner_controlled_public_fixture"}
ALLOWED_CAPTURE_METHODS = {"manual_controlled_fixture"}
ALLOWED_RIGHTS_CLASSES = {"expressly_permitted", "not_expressly_prohibited"}
ALLOWED_RETENTION_CLASSES = {"retain_project_evidence", "retain_until_review", "manifest_only"}
NO_RAW_RETENTION_CLASSES = {"no_storage_overlay_only", "forbidden_no_capture"}

STRATEGY_MARKERS = (
    "should optimize",
    "should target",
    "recommend ",
    "recommendation",
    "seo strategy",
    "geo strategy",
    "content strategy",
    "opportunity score",
    "provider winner",
    "average truth score",
)

CUSTOMER_PRIVATE_MARKERS = (
    "customer_email=",
    "customer_id=",
    "order_id=",
    "searchclarity_order=",
    "ga4_property=",
    "gsc_property=",
    "shopify_admin",
    "etsy_seller_dashboard",
)

PackageStatus = Literal["draft", "validated", "rejected", "admitted"]
CandidateStatus = Literal["pending", "valid", "rejected"]
AuditEventType = Literal[
    "package_rejected",
    "package_validated",
    "observation_admitted",
    "observation_superseded",
    "observation_withdrawn",
    "raw_support_purged",
]


@dataclass(frozen=True)
class ValidationIssue:
    """One fail-closed validation issue."""

    code: str
    message: str


@dataclass(frozen=True)
class ScopeContext:
    """Safe C2 scope context.

    The first slice permits only internal/owner-controlled fixture scopes.
    Customer records and private account identifiers are rejected.
    """

    scope_id: str
    scope_class: str
    scope_label: str = ""


@dataclass(frozen=True)
class RawSupportManifest:
    """Optional raw-support manifest.

    Raw support is optional but first-class when included. The manifest uses
    pointer/hash posture only and does not approve raw retention by default.
    """

    raw_support_id: str
    raw_pointer: str
    raw_sha256: str
    raw_bytes: int | None
    raw_media_type: str
    retention_class: str
    hash_verification_status: str = "pending"

    def verify_text(self, text: str) -> "RawSupportManifest":
        digest = sha256(text.encode("utf-8")).hexdigest()
        status = "verified" if digest == self.raw_sha256 else "mismatch"
        return replace(self, hash_verification_status=status)


@dataclass(frozen=True)
class ObservationPackage:
    """C2 observation package envelope."""

    observation_package_id: str
    scope: ScopeContext
    source_family: str
    capture_method: str
    operator_intent: str
    artifact_reference: str
    captured_at: datetime | None
    rights_class: str
    rights_basis: str
    retention_class: str
    retention_basis: str
    claim_use_warning: str
    package_status: PackageStatus = "draft"


@dataclass(frozen=True)
class CandidateObservation:
    """Possible observation before admission.

    Candidate observations are never evidence until admitted.
    """

    candidate_observation_id: str
    observation_package_id: str
    candidate_type: str
    observed_text: str
    candidate_status: CandidateStatus = "pending"
    validation_errors: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EvidenceIdentity:
    """Internal-only evidence identity for an admitted observation."""

    evidence_id: str
    observation_id: str
    citation_handle: str
    evidence_status: str = "active"


@dataclass(frozen=True)
class AuditEvent:
    """Minimum audit event concept for consequential C2 transitions."""

    audit_event_id: str
    event_type: AuditEventType
    entity_type: str
    entity_id: str
    event_time: datetime
    event_reason: str


@dataclass(frozen=True)
class AdmissionResult:
    """Result of admitting one candidate observation."""

    observation_id: str
    package: ObservationPackage
    candidate: CandidateObservation
    evidence: EvidenceIdentity
    audit_events: tuple[AuditEvent, ...]


def _contains_marker(value: str, markers: Iterable[str]) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in markers)


def _issue(code: str, message: str) -> ValidationIssue:
    return ValidationIssue(code=code, message=message)


def validate_observation_package(
    package: ObservationPackage,
    *,
    raw_support: RawSupportManifest | None = None,
) -> tuple[ValidationIssue, ...]:
    """Validate the C2 observation envelope and optional raw support.

    This function is fail-closed: missing or unclear scope/rights/retention
    produces validation issues and prevents admission.
    """

    issues: list[ValidationIssue] = []

    if not package.scope.scope_id:
        issues.append(_issue("missing_scope", "scope_id is required"))
    if package.scope.scope_class not in ALLOWED_SCOPE_CLASSES:
        issues.append(_issue("unknown_scope_class", "scope_class is not allowed for C2"))
    if _contains_marker(package.scope.scope_label, CUSTOMER_PRIVATE_MARKERS):
        issues.append(_issue("customer_private_scope", "customer/private identity marker found in scope_label"))

    if package.source_family not in ALLOWED_SOURCE_FAMILIES:
        issues.append(_issue("unsupported_source_family", "source_family is outside C2"))
    if package.capture_method not in ALLOWED_CAPTURE_METHODS:
        issues.append(_issue("unsupported_capture_method", "capture_method is outside C2"))

    if not package.operator_intent:
        issues.append(_issue("missing_operator_intent", "operator_intent is required"))
    if _contains_marker(package.operator_intent, STRATEGY_MARKERS):
        issues.append(_issue("strategy_intent", "operator_intent contains strategy/recommendation language"))

    if not package.artifact_reference:
        issues.append(_issue("missing_artifact_reference", "artifact_reference is required"))
    if _contains_marker(package.artifact_reference, CUSTOMER_PRIVATE_MARKERS):
        issues.append(_issue("customer_private_artifact", "customer/private marker found in artifact_reference"))

    if package.captured_at is None:
        issues.append(_issue("missing_captured_at", "captured_at is required"))
    elif package.captured_at.tzinfo is None:
        issues.append(_issue("naive_captured_at", "captured_at must be timezone-aware"))

    if package.rights_class not in ALLOWED_RIGHTS_CLASSES:
        issues.append(_issue("rights_fail_closed", "rights_class is missing or not allowed"))
    if not package.rights_basis:
        issues.append(_issue("missing_rights_basis", "rights_basis is required"))

    if package.retention_class not in ALLOWED_RETENTION_CLASSES:
        issues.append(_issue("retention_fail_closed", "retention_class is missing or not allowed"))
    if not package.retention_basis:
        issues.append(_issue("missing_retention_basis", "retention_basis is required"))

    if not package.claim_use_warning:
        issues.append(_issue("missing_claim_use_warning", "point-in-time claim-use warning is required"))
    elif "point-in-time" not in package.claim_use_warning.lower():
        issues.append(_issue("weak_claim_use_warning", "claim_use_warning must preserve point-in-time caveat"))

    if raw_support is not None:
        issues.extend(validate_raw_support(raw_support))
        if package.retention_class in NO_RAW_RETENTION_CLASSES:
            issues.append(_issue("raw_retention_blocked", "package retention posture blocks raw support"))

    return tuple(issues)


def validate_raw_support(raw_support: RawSupportManifest) -> tuple[ValidationIssue, ...]:
    """Validate optional raw support manifest."""

    issues: list[ValidationIssue] = []

    if not raw_support.raw_support_id:
        issues.append(_issue("missing_raw_support_id", "raw_support_id is required"))
    if not raw_support.raw_pointer:
        issues.append(_issue("missing_raw_pointer", "raw_pointer is required when raw support exists"))
    if not raw_support.raw_sha256:
        issues.append(_issue("missing_raw_sha256", "raw_sha256 is required when raw support exists"))
    if raw_support.raw_sha256 and len(raw_support.raw_sha256) != 64:
        issues.append(_issue("invalid_raw_sha256", "raw_sha256 must be a SHA-256 hex digest"))
    if not raw_support.raw_media_type:
        issues.append(_issue("missing_raw_media_type", "raw_media_type is required when raw support exists"))
    if raw_support.retention_class not in ALLOWED_RETENTION_CLASSES:
        issues.append(_issue("raw_retention_fail_closed", "raw retention_class is missing or not allowed"))
    if raw_support.hash_verification_status not in {"pending", "verified"}:
        issues.append(_issue("raw_hash_not_verified", "raw support hash must be pending or verified before admission path"))

    return tuple(issues)


def validate_candidate_observation(candidate: CandidateObservation) -> tuple[ValidationIssue, ...]:
    """Validate candidate observation content without admitting it as evidence."""

    issues: list[ValidationIssue] = []

    if not candidate.candidate_observation_id:
        issues.append(_issue("missing_candidate_id", "candidate_observation_id is required"))
    if not candidate.observation_package_id:
        issues.append(_issue("missing_candidate_package", "observation_package_id is required"))
    if not candidate.candidate_type:
        issues.append(_issue("missing_candidate_type", "candidate_type is required"))
    if not candidate.observed_text:
        issues.append(_issue("missing_observed_text", "observed_text is required"))
    if _contains_marker(candidate.observed_text, STRATEGY_MARKERS):
        issues.append(_issue("strategy_text_rejected", "candidate observed_text contains strategy/recommendation language"))
    if _contains_marker(candidate.observed_text, CUSTOMER_PRIVATE_MARKERS):
        issues.append(_issue("customer_private_candidate", "candidate observed_text contains customer/private marker"))

    return tuple(issues)


def admit_candidate_observation(
    package: ObservationPackage,
    candidate: CandidateObservation,
    *,
    raw_support: RawSupportManifest | None = None,
    now: datetime | None = None,
) -> AdmissionResult:
    """Admit a valid candidate as C2 evidence.

    Raises ValueError when fail-closed validation issues exist. This keeps
    invalid candidates from becoming evidence IDs.
    """

    now = now or datetime.now(timezone.utc)
    package_issues = validate_observation_package(package, raw_support=raw_support)
    candidate_issues = validate_candidate_observation(candidate)
    all_issues = package_issues + candidate_issues
    if all_issues:
        codes = ", ".join(issue.code for issue in all_issues)
        raise ValueError(f"cannot admit invalid C2 observation: {codes}")

    observation_id = f"obs_{uuid4().hex}"
    evidence_id = f"ev_{uuid4().hex}"
    admitted_package = replace(package, package_status="admitted")
    valid_candidate = replace(candidate, candidate_status="valid", validation_errors=())
    evidence = EvidenceIdentity(
        evidence_id=evidence_id,
        observation_id=observation_id,
        citation_handle=f"cite:{evidence_id}",
    )
    audit_event = AuditEvent(
        audit_event_id=f"audit_{uuid4().hex}",
        event_type="observation_admitted",
        entity_type="observation",
        entity_id=observation_id,
        event_time=now,
        event_reason="C2 candidate observation admitted after local validation",
    )

    return AdmissionResult(
        observation_id=observation_id,
        package=admitted_package,
        candidate=valid_candidate,
        evidence=evidence,
        audit_events=(audit_event,),
    )


def supersede_observation(result: AdmissionResult, *, reason: str, now: datetime | None = None) -> tuple[AdmissionResult, AuditEvent]:
    """Return a superseded copy plus audit event without mutating original result."""

    if not reason:
        raise ValueError("supersession reason is required")
    now = now or datetime.now(timezone.utc)
    superseded = replace(
        result,
        evidence=replace(result.evidence, evidence_status="superseded"),
        audit_events=result.audit_events
        + (
            AuditEvent(
                audit_event_id=f"audit_{uuid4().hex}",
                event_type="observation_superseded",
                entity_type="observation",
                entity_id=result.observation_id,
                event_time=now,
                event_reason=reason,
            ),
        ),
    )
    return superseded, superseded.audit_events[-1]


def validate_no_external_markers(paths_or_names: Sequence[str]) -> tuple[ValidationIssue, ...]:
    """Reject file/module names that would smuggle forbidden surfaces into C2."""

    forbidden_markers = (
        "dataforseo",
        "provider_client",
        "api_server",
        "mcp",
        "dashboard",
        "customer",
        "searchclarity_report",
        "scheduler",
        "crawler",
        "scraper",
        "browser_extension",
        "strategy",
        "recommendation",
    )
    issues: list[ValidationIssue] = []
    for name in paths_or_names:
        lowered = name.lower()
        if any(marker in lowered for marker in forbidden_markers):
            issues.append(_issue("forbidden_surface_marker", f"forbidden C2 surface marker in {name}"))
    return tuple(issues)
