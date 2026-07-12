from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Iterable

from .errors import CrossCheckError
from .models import CONTRACT_VERSION, FORBIDDEN_REQUEST_FLAGS, REQUEST_TYPES, ProviderSide

_REQUIRED_CONTEXT = ("subject_type", "subject_value", "surface_family", "locale", "language", "device", "location")


def build_cross_check_request(*, request_id: str, scope_id: str, side_ids: list[str], comparison_purpose: str = "evidence_disagreement") -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": request_id,
        "request_type": "provider_cross_check",
        "scope_id": scope_id,
        "side_ids": list(side_ids),
        "comparison_purpose": comparison_purpose,
    }


def validate_cross_check_request(request: dict[str, Any]) -> None:
    if request.get("request_type") not in REQUEST_TYPES:
        raise CrossCheckError("blocked_request_type")
    scope_id = request.get("scope_id")
    if not isinstance(scope_id, str) or not scope_id.startswith("scope_provider_"):
        raise CrossCheckError("blocked_scope")
    side_ids = request.get("side_ids")
    if not isinstance(side_ids, list) or len(side_ids) < 2 or not all(isinstance(x, str) for x in side_ids):
        raise CrossCheckError("blocked_missing_context")
    for flag, code in FORBIDDEN_REQUEST_FLAGS.items():
        if request.get(flag):
            raise CrossCheckError(code)
    allowed = {"contract_version", "request_id", "request_type", "scope_id", "side_ids", "comparison_purpose", *FORBIDDEN_REQUEST_FLAGS}
    if set(request) - allowed:
        raise CrossCheckError("blocked_missing_context")


def _parse_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _distance_seconds(values: Iterable[str | None]) -> int | None:
    parsed = [v for v in (_parse_time(x) for x in values) if v is not None]
    if len(parsed) < 2:
        return None
    return int((max(parsed) - min(parsed)).total_seconds())


def _guard_sides(scope_id: str, sides: list[ProviderSide]) -> None:
    if any(side.scope_id != scope_id for side in sides):
        raise CrossCheckError("blocked_cross_scope")
    for side in sides:
        if not all((side.provider_name, side.provider_family, side.endpoint_or_surface, side.metric_name, side.evidence_handle)):
            raise CrossCheckError("blocked_missing_attribution")
        if side.rights_class == "blocked" or side.retention_class == "blocked" or side.evidence_status in {"blocked_by_rights", "expired_by_retention"}:
            raise CrossCheckError("blocked_rights_or_retention")
        if side.source_admission_status != "admitted_synthetic_fixture":
            raise CrossCheckError("blocked_source_not_admitted")
        if side.evidence_status not in {"active", "superseded"}:
            raise CrossCheckError("blocked_status_or_drift")
        if any(not side.context.get(key) for key in _REQUIRED_CONTEXT):
            raise CrossCheckError("blocked_missing_context")


def classify_comparability(sides: list[ProviderSide]) -> tuple[str, list[str], list[str]]:
    first = sides[0]
    aligned: list[str] = []
    misaligned: list[str] = []
    for key in _REQUIRED_CONTEXT:
        values = {str(side.context.get(key)) for side in sides}
        (aligned if len(values) == 1 else misaligned).append(key)
    for field in ("metric_name", "metric_unit"):
        values = {str(getattr(side, field)) for side in sides}
        (aligned if len(values) == 1 else misaligned).append(field)
    proprietary_unknown = any(side.metric_posture == "provider_model_output" and not side.metric_definition for side in sides)
    if proprietary_unknown:
        misaligned.append("metric_definition")
        return "unresolved_incomparability", sorted(set(aligned)), sorted(set(misaligned))
    if misaligned:
        return "partially_comparable", sorted(set(aligned)), sorted(set(misaligned))
    if any(side.freshness_status in {"stale", "unknown", "historical_only"} for side in sides):
        return "partially_comparable", sorted(set(aligned)), ["freshness_status"]
    return "comparable_with_caveat", sorted(set(aligned)), []


def classify_disagreement_types(sides: list[ProviderSide], disposition: str) -> list[str]:
    types: set[str] = set()
    values = [side.metric_value for side in sides]
    if len(set(map(repr, values))) > 1:
        if all(isinstance(v, bool) for v in values):
            types.add("presence_absence_difference")
        elif sides[0].metric_name == "rank_position":
            types.add("rank_position_difference")
        else:
            types.add("value_difference")
    if len({side.freshness_status for side in sides}) > 1:
        types.add("freshness_difference")
    if len({side.provider_name for side in sides}) > 1:
        types.add("provider_model_difference")
    if disposition == "unresolved_incomparability":
        types.add("unresolved_incomparability")
    return sorted(types)


def build_provider_cross_check(request: dict[str, Any], sides_by_id: dict[str, ProviderSide]) -> dict[str, Any]:
    validate_cross_check_request(request)
    try:
        sides = [sides_by_id[side_id] for side_id in request["side_ids"]]
    except KeyError as exc:
        raise CrossCheckError("not_found") from exc
    _guard_sides(request["scope_id"], sides)
    disposition, aligned, misaligned = classify_comparability(sides)
    capture_distance = _distance_seconds(side.captured_at for side in sides)
    provider_distance = _distance_seconds(side.provider_reported_time for side in sides)
    caveats = {
        "provider testimony only; not truth",
        "provider attribution and independent evidence state preserved",
    }
    if disposition != "comparable_with_caveat":
        caveats.add("comparison downgraded because dimensions, definitions, or freshness do not fully align")
    if capture_distance:
        caveats.add("captures are non-synchronous")
    if provider_distance:
        caveats.add("provider-reported times are non-synchronous")
    if any(side.metric_name == "sampled_presence" for side in sides):
        caveats.add("sampled presence or absence is not universal presence or absence")
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": request["request_id"],
        "response_id": f"resp_{request['request_id']}",
        "scope_id": request["scope_id"],
        "comparison_context": dict(sorted(sides[0].context.items())),
        "provider_sides": [side.as_dict() for side in sorted(sides, key=lambda item: item.side_id)],
        "comparison_disposition": disposition,
        "disagreement_types": classify_disagreement_types(sides, disposition),
        "aligned_dimensions": aligned,
        "misaligned_dimensions": misaligned,
        "capture_time_distance": capture_distance,
        "provider_time_distance": provider_distance,
        "required_caveats": sorted(caveats),
        "claim_use_warning": "provider disagreement is evidence; consumer interpretation required",
        "consumer_promotion_required": True,
        "truth_value_produced": False,
        "winner_selected": False,
        "composite_score_produced": False,
    }


def serialize_provider_cross_check(result: dict[str, Any]) -> str:
    return json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
