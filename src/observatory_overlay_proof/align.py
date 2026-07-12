from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from typing import Any

from .errors import OverlayProofError
from .fixtures import EVIDENCE_WINDOWS, get_request_fixture
from .models import (
    ALLOWED_CALLERS,
    ALLOWED_FIELDS,
    ALLOWED_FRESHNESS,
    ALLOWED_KINDS,
    ALLOWED_USES,
    CONTRACT_VERSION,
    REQUEST_FIELDS,
    REQUEST_TYPE,
)

_FORBIDDEN_KEYS = {
    "customer_id", "account_id", "email", "name", "url", "file", "filepath",
    "screenshot", "csv", "pdf", "credential", "token", "password", "evidence_id",
    "observation_id", "capture_id", "raw_payload_id", "citation_handle",
}
_FORBIDDEN_INTENTS = {"canonical_ingestion", "recommendation", "causality", "report_generation", "provider_capture"}


def build_overlay_request(fixture_name: str) -> dict[str, Any]:
    try:
        return get_request_fixture(fixture_name)
    except KeyError as exc:
        raise OverlayProofError("not_found") from exc


def validate_overlay_request(request: dict[str, Any]) -> None:
    if set(request) != REQUEST_FIELDS or request.get("request_type") != REQUEST_TYPE:
        raise OverlayProofError("blocked_request_type")
    if request.get("contract_version") != CONTRACT_VERSION:
        raise OverlayProofError("blocked_request_type")
    if request.get("caller_class") not in ALLOWED_CALLERS:
        raise OverlayProofError("blocked_scope")
    scope_id = request.get("scope_id")
    if not isinstance(scope_id, str) or scope_id not in EVIDENCE_WINDOWS:
        raise OverlayProofError("blocked_scope")
    if request.get("overlay_scope_context") != scope_id:
        raise OverlayProofError("blocked_cross_scope")
    if request.get("overlay_kind") not in ALLOWED_KINDS:
        raise OverlayProofError("blocked_missing_metadata")
    if request.get("overlay_allowed_use") not in ALLOWED_USES:
        raise OverlayProofError("blocked_missing_metadata")
    if request.get("overlay_freshness_status") not in ALLOWED_FRESHNESS:
        raise OverlayProofError("blocked_unknown_freshness")
    if request.get("overlay_supplied_by_consumer") is not True or not request.get("overlay_timestamp"):
        raise OverlayProofError("blocked_missing_metadata")
    if request.get("overlay_no_storage_assertion") is not True:
        raise OverlayProofError("blocked_no_storage_not_asserted")
    if request.get("overlay_discard_required") is not True:
        raise OverlayProofError("blocked_discard_not_required")
    if request.get("alignment_intent") in _FORBIDDEN_INTENTS:
        raise OverlayProofError("blocked_recommendation_or_causality")

    manifest = request.get("field_manifest")
    values = request.get("values")
    if not isinstance(manifest, list) or not manifest or not set(manifest) <= ALLOWED_FIELDS:
        raise OverlayProofError("blocked_field_overreach")
    if set(manifest) & _FORBIDDEN_KEYS:
        raise OverlayProofError("blocked_private_identity")
    if not isinstance(values, list) or not values:
        raise OverlayProofError("blocked_missing_metadata")
    for row in values:
        if not isinstance(row, dict) or set(row) != set(manifest):
            raise OverlayProofError("blocked_field_overreach")
        if set(row) & _FORBIDDEN_KEYS:
            raise OverlayProofError("blocked_private_identity")
        if any(isinstance(v, str) and ("/" in v or "\\" in v) for v in row.values()):
            raise OverlayProofError("blocked_file_or_screenshot")
        if not isinstance(row.get("timestamp"), str):
            raise OverlayProofError("blocked_missing_metadata")


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def align_overlay_to_evidence(request: dict[str, Any]) -> dict[str, Any]:
    validate_overlay_request(request)
    rows = deepcopy(request["values"])
    windows = EVIDENCE_WINDOWS[request["scope_id"]]
    matched = []
    for window in windows:
        start, end = _parse(window.window_start), _parse(window.window_end)
        count = sum(1 for row in rows if start <= _parse(row["timestamp"]) <= end)
        if count:
            matched.append({
                "evidence_id": window.evidence_id,
                "window_overlap_count": count,
                "evidence_direction": window.direction,
                "evidence_freshness_status": window.freshness_status,
                "coverage_warning": window.coverage_warning,
            })
    disposition = "aligned_with_caveat" if matched else "blocked_by_incomparability"
    return {
        "alignment_disposition": disposition,
        "aligned_evidence_units": sorted(matched, key=lambda x: x["evidence_id"]),
        "alignment_summary": {
            "overlay_point_count": len(rows),
            "aligned_window_count": len(matched),
            "temporal_alignment_only": request["overlay_kind"] == "intervention_timeline",
        },
    }


def build_discard_status() -> str:
    return "discarded_after_response_build"


def build_overlay_alignment_response(request: dict[str, Any]) -> dict[str, Any]:
    result = align_overlay_to_evidence(request)
    caveats = [
        "overlay values were supplied at read time and were not stored as Observatory evidence",
        "alignment does not establish causality or authorize recommendations",
    ]
    if request["overlay_freshness_status"] == "stale":
        caveats.append("overlay freshness was consumer-supplied and stale")
    if result["alignment_disposition"] != "aligned_with_caveat":
        caveats.append("overlay and Observatory evidence windows were not safely aligned")
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": request["request_id"],
        "response_id": f"resp_{request['request_id']}",
        "scope_id": request["scope_id"],
        "external_overlay_reference": request["external_overlay_reference"],
        "overlay_kind": request["overlay_kind"],
        **result,
        "required_caveats": sorted(caveats),
        "overlay_discard_status": build_discard_status(),
        "overlay_persisted": False,
        "overlay_cached": False,
        "overlay_logged": False,
        "overlay_evidence_promoted": False,
        "overlay_values_returned": False,
        "consumer_promotion_required": True,
        "customer_facing_output_authorized": False,
    }


def serialize_overlay_alignment_response(response: dict[str, Any]) -> str:
    return json.dumps(response, sort_keys=True, separators=(",", ":"))
