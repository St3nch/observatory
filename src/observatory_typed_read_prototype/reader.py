from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any

from .authorization import authorize
from .errors import ReadError
from .fixtures import COVERAGE, EVIDENCE
from .models import CLAIM_INTENTS, CONTRACT_VERSION, REQUEST_TYPES, EvidenceUnit

_CURSOR_KEY = b"observatory-fixture-cursor-v0.1"
MAX_PAGE_SIZE = 2
MAX_TOTAL_RESULTS = 4


def _validate_request(scope_id: str, request_type: str, claim_intent: str) -> None:
    if request_type not in REQUEST_TYPES:
        raise ReadError("blocked_request_type")
    if claim_intent not in CLAIM_INTENTS:
        raise ReadError("blocked_claim_intent")
    if not scope_id.startswith("scope_"):
        raise ReadError("blocked_scope")


def _visible(unit: EvidenceUnit, historical: bool) -> bool:
    if unit.evidence_status == "active":
        return True
    if unit.evidence_status == "superseded" and historical:
        return True
    return False


def _freshness_guard(unit: EvidenceUnit, historical: bool) -> None:
    if not historical and unit.freshness_status in {"stale", "unknown", "historical_only"}:
        raise ReadError("blocked_freshness")


def _response(request_type: str, caller_class: str, scope_id: str, claim_intent: str, units: list[EvidenceUnit], coverage: list[str] | None = None, truncated: bool = False, omitted: int = 0) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": "req_fixture_static",
        "response_id": "resp_fixture_static",
        "request_type": request_type,
        "caller_class": caller_class,
        "scope_id": scope_id,
        "scope_class": "market_watch",
        "claim_intent": claim_intent,
        "current_or_historical_use": "historical" if claim_intent == "historical_observation" else "current",
        "evidence_units": [u.as_dict() for u in units],
        "coverage_blind_spots": sorted(coverage or []),
        "truncated": truncated,
        "omitted_evidence_unit_count": omitted,
        "warnings": sorted({w for unit in units for w in unit.warnings}),
        "consumer_promotion_required": False,
    }


def evidence_lookup(*, caller_class: str, scope_id: str, evidence_id: str, claim_intent: str) -> dict[str, Any]:
    _validate_request(scope_id, "evidence_lookup", claim_intent)
    authorize(caller_class, scope_id, "evidence_lookup")
    unit = EVIDENCE.get(evidence_id)
    historical = claim_intent == "historical_observation"
    if unit is None or unit.scope_id != scope_id or not _visible(unit, historical):
        raise ReadError("not_found")
    _freshness_guard(unit, historical)
    return _response("evidence_lookup", caller_class, scope_id, claim_intent, [unit])


def observation_package_read(*, caller_class: str, scope_id: str, claim_intent: str, page_size: int = 2, cursor: str | None = None) -> dict[str, Any]:
    _validate_request(scope_id, "observation_package_read", claim_intent)
    authorize(caller_class, scope_id, "observation_package_read")
    if page_size < 1 or page_size > MAX_PAGE_SIZE:
        raise ReadError("blocked_result_ceiling")
    historical = claim_intent == "historical_observation"
    units = sorted((u for u in EVIDENCE.values() if u.scope_id == scope_id and _visible(u, historical)), key=lambda u: u.evidence_id)
    if len(units) > MAX_TOTAL_RESULTS:
        units = units[:MAX_TOTAL_RESULTS]
    start = 0
    if cursor:
        start = _decode_cursor(cursor, caller_class, scope_id, "observation_package_read", claim_intent)
    page = units[start:start + page_size]
    for unit in page:
        _freshness_guard(unit, historical)
    omitted = max(0, len(units) - (start + len(page)))
    return _response("observation_package_read", caller_class, scope_id, claim_intent, page, truncated=omitted > 0, omitted=omitted)


def freshness_check(*, caller_class: str, scope_id: str, evidence_id: str, claim_intent: str) -> dict[str, Any]:
    authorize(caller_class, scope_id, "freshness_check")
    result = evidence_lookup(caller_class=caller_class, scope_id=scope_id, evidence_id=evidence_id, claim_intent=claim_intent)
    result["request_type"] = "freshness_check"
    return result


def coverage_blind_spot_read(*, caller_class: str, scope_id: str, claim_intent: str) -> dict[str, Any]:
    _validate_request(scope_id, "coverage_blind_spot_read", claim_intent)
    authorize(caller_class, scope_id, "coverage_blind_spot_read")
    return _response("coverage_blind_spot_read", caller_class, scope_id, claim_intent, [], COVERAGE.get(scope_id, ["coverage unknown"]))


def make_cursor(*, caller_class: str, scope_id: str, request_type: str, claim_intent: str, offset: int) -> str:
    payload = json.dumps({"caller": caller_class, "scope": scope_id, "request_type": request_type, "claim_intent": claim_intent, "offset": offset, "contract": CONTRACT_VERSION}, sort_keys=True, separators=(",", ":")).encode()
    sig = hmac.new(_CURSOR_KEY, payload, hashlib.sha256).hexdigest().encode()
    return base64.urlsafe_b64encode(payload + b"." + sig).decode()


def _decode_cursor(cursor: str, caller_class: str, scope_id: str, request_type: str, claim_intent: str) -> int:
    try:
        raw = base64.urlsafe_b64decode(cursor.encode())
        payload, sig = raw.rsplit(b".", 1)
        expected = hmac.new(_CURSOR_KEY, payload, hashlib.sha256).hexdigest().encode()
        if not hmac.compare_digest(sig, expected):
            raise ValueError
        data = json.loads(payload)
    except Exception as exc:
        raise ReadError("blocked_filter") from exc
    expected_bindings = {"caller": caller_class, "scope": scope_id, "request_type": request_type, "claim_intent": claim_intent, "contract": CONTRACT_VERSION}
    if any(data.get(k) != v for k, v in expected_bindings.items()):
        raise ReadError("blocked_filter")
    offset = data.get("offset")
    if not isinstance(offset, int) or offset < 0:
        raise ReadError("blocked_filter")
    return offset
