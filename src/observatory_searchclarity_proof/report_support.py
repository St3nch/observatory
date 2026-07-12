from __future__ import annotations

import hashlib
import json
from typing import Any

from observatory_typed_read_prototype import (
    ReadError,
    coverage_blind_spot_read,
    evidence_lookup,
    freshness_check,
    observation_package_read,
)

from .errors import SearchClarityProofError
from .fixtures import (
    ADMITTED_SOURCE_FAMILIES,
    PRIVATE_OR_CUSTOMER_FIELDS,
    REPORT_OR_RECOMMENDATION_FIELDS,
    REQUIRED_CAVEAT_FIELDS,
)
from .models import (
    ALLOWED_OUTPUT_USE,
    CLAIM_INTENTS,
    CONTRACT_VERSION,
    REQUEST_TYPES,
    ReportSupportRequest,
)
from .references import map_synthetic_report_safe_references

_REQUEST_MAP = {
    "report_support_evidence_lookup": "evidence_lookup",
    "report_support_observation_package": "observation_package_read",
    "report_support_freshness_check": "freshness_check",
    "report_support_coverage_check": "coverage_blind_spot_read",
}


def validate_customer_clean_request(payload: dict[str, Any]) -> None:
    forbidden = set(payload) & PRIVATE_OR_CUSTOMER_FIELDS
    if forbidden:
        if "overlay_values" in forbidden or "overlay_no_storage_assertion" in forbidden:
            raise SearchClarityProofError("blocked_not_admitted")
        raise SearchClarityProofError("blocked_private_data")
    if set(payload) & REPORT_OR_RECOMMENDATION_FIELDS:
        field = sorted(set(payload) & REPORT_OR_RECOMMENDATION_FIELDS)[0]
        if "recommend" in field or field == "strategy":
            raise SearchClarityProofError("blocked_recommendation")
        raise SearchClarityProofError("blocked_report_content")


def build_report_support_request(**payload: Any) -> ReportSupportRequest:
    validate_customer_clean_request(payload)
    allowed = {
        "contract_version", "request_id", "request_type", "scope_id", "claim_intent",
        "current_or_historical_use", "requested_evidence_families", "freshness_requirement",
        "report_support_purpose_code", "allowed_output_use", "evidence_id",
    }
    if set(payload) - allowed:
        raise SearchClarityProofError("blocked_customer_data")
    if payload.get("contract_version") != CONTRACT_VERSION:
        raise SearchClarityProofError("blocked_request_type")
    if payload.get("request_type") not in REQUEST_TYPES:
        raise SearchClarityProofError("blocked_request_type")
    if payload.get("claim_intent") not in CLAIM_INTENTS:
        raise SearchClarityProofError("blocked_claim_intent")
    if payload.get("allowed_output_use") != ALLOWED_OUTPUT_USE:
        raise SearchClarityProofError("blocked_report_content")
    scope_id = payload.get("scope_id")
    if not isinstance(scope_id, str) or not scope_id.startswith("scope_"):
        raise SearchClarityProofError("blocked_scope")
    families = tuple(sorted(set(payload.get("requested_evidence_families") or ())))
    if not families:
        raise SearchClarityProofError("blocked_claim_support")
    return ReportSupportRequest(
        contract_version=CONTRACT_VERSION,
        request_id=str(payload["request_id"]),
        request_type=str(payload["request_type"]),
        scope_id=scope_id,
        claim_intent=str(payload["claim_intent"]),
        current_or_historical_use=str(payload["current_or_historical_use"]),
        requested_evidence_families=families,
        freshness_requirement=str(payload["freshness_requirement"]),
        report_support_purpose_code=str(payload["report_support_purpose_code"]),
        allowed_output_use=ALLOWED_OUTPUT_USE,
        evidence_id=payload.get("evidence_id"),
    )


def classify_report_support_disposition(
    *,
    evidence_units: list[dict[str, Any]],
    claim_intent: str,
    requested_evidence_families: tuple[str, ...],
) -> tuple[str, list[str]]:
    blockers: set[str] = set()
    for family in requested_evidence_families:
        if family not in ADMITTED_SOURCE_FAMILIES:
            blockers.add("source_family_not_admitted")
    for unit in evidence_units:
        status = unit.get("evidence_status")
        if status in {"blocked_by_rights", "expired_by_retention", "withdrawn", "invalidated"}:
            blockers.add(status)
        if unit.get("source_family") not in ADMITTED_SOURCE_FAMILIES:
            blockers.add("source_family_not_admitted")
        if claim_intent == "provider_metric_statement" and not unit.get("provider_attribution"):
            blockers.add("missing_provider_attribution")
        if claim_intent == "absence_statement" and not unit.get("sample_bound_warning"):
            blockers.add("missing_absence_sample_context")
        if claim_intent == "current_state_observation" and unit.get("freshness_status") in {"stale", "unknown", "historical_only"}:
            blockers.add("blocked_freshness_for_current_use")
        if any(not unit.get(field) for field in REQUIRED_CAVEAT_FIELDS):
            blockers.add("missing_mandatory_caveats")
    if blockers:
        return "blocked", sorted(blockers)
    if any(unit.get("evidence_status") == "superseded" or unit.get("freshness_status") in {"stale", "unknown", "historical_only"} for unit in evidence_units):
        return "historical_support_only", []
    return "supportable_with_caveats", []


def _typed_read(request: ReportSupportRequest) -> dict[str, Any]:
    m14_claim_intent = {
        "provider_metric_statement": "historical_observation",
        "ai_geo_sampled_observation": "historical_observation",
    }.get(request.claim_intent, request.claim_intent)
    kwargs = {
        "caller_class": "searchclarity_internal",
        "scope_id": request.scope_id,
        "claim_intent": m14_claim_intent,
    }
    try:
        if request.request_type == "report_support_evidence_lookup":
            if not request.evidence_id:
                raise SearchClarityProofError("blocked_claim_support")
            return evidence_lookup(evidence_id=request.evidence_id, **kwargs)
        if request.request_type == "report_support_observation_package":
            return observation_package_read(**kwargs)
        if request.request_type == "report_support_freshness_check":
            if not request.evidence_id:
                raise SearchClarityProofError("blocked_claim_support")
            return freshness_check(evidence_id=request.evidence_id, **kwargs)
        return coverage_blind_spot_read(**kwargs)
    except ReadError as exc:
        if exc.code == "not_found":
            raise SearchClarityProofError("not_found") from exc
        if exc.code in {"blocked_scope", "blocked_authorization"}:
            raise SearchClarityProofError("blocked_scope") from exc
        if exc.code == "blocked_freshness":
            raise SearchClarityProofError("blocked_claim_support") from exc
        raise SearchClarityProofError("blocked_claim_support") from exc


def build_report_support_pack(request: ReportSupportRequest) -> dict[str, Any]:
    typed = _typed_read(request)
    units = typed.get("evidence_units", [])
    disposition, blockers = classify_report_support_disposition(
        evidence_units=units,
        claim_intent=request.claim_intent,
        requested_evidence_families=request.requested_evidence_families,
    )
    evidence_ids = [str(unit["evidence_id"]) for unit in units]
    refs = map_synthetic_report_safe_references(scope_id=request.scope_id, evidence_ids=evidence_ids)
    required_caveats = sorted({
        str(unit[field])
        for unit in units
        for field in REQUIRED_CAVEAT_FIELDS
        if unit.get(field)
    })
    response_seed = json.dumps({"request": request.as_dict(), "ids": sorted(evidence_ids)}, sort_keys=True, separators=(",", ":"))
    response_id = "scr_" + hashlib.sha256(response_seed.encode()).hexdigest()[:20]
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": request.request_id,
        "response_id": response_id,
        "scope_id": request.scope_id,
        "claim_intent": request.claim_intent,
        "report_support_disposition": disposition,
        "blockers": blockers,
        "evidence_units": units,
        "required_caveats": required_caveats,
        "coverage_blind_spots": sorted(typed.get("coverage_blind_spots", [])),
        "reference_mode": "synthetic_report_safe_fixture",
        "report_support_references": refs,
        "consumer_promotion_required": True,
        "customer_facing_output_authorized": False,
        "human_review_required": True,
        "truncated": bool(typed.get("truncated", False)),
        "omitted_evidence_unit_count": int(typed.get("omitted_evidence_unit_count", 0)),
    }


def serialize_report_support_pack(pack: dict[str, Any]) -> str:
    return json.dumps(pack, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
