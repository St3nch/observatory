from __future__ import annotations

from copy import deepcopy

from .models import CONTRACT_VERSION, REQUEST_TYPE, EvidenceWindow

SCOPE_A = "scope_market_watch_alpha"
SCOPE_B = "scope_market_watch_beta"

EVIDENCE_WINDOWS = {
    SCOPE_A: (
        EvidenceWindow(
            evidence_id="ev_overlay_a_01",
            scope_id=SCOPE_A,
            window_start="2026-07-01T00:00:00Z",
            window_end="2026-07-07T23:59:59Z",
            direction="up",
            freshness_status="fresh",
            coverage_warning="bounded synthetic public-observation window",
        ),
        EvidenceWindow(
            evidence_id="ev_overlay_a_02",
            scope_id=SCOPE_A,
            window_start="2026-07-08T00:00:00Z",
            window_end="2026-07-12T23:59:59Z",
            direction="down",
            freshness_status="fresh",
            coverage_warning="bounded synthetic public-observation window",
        ),
    ),
    SCOPE_B: (
        EvidenceWindow(
            evidence_id="ev_overlay_b_01",
            scope_id=SCOPE_B,
            window_start="2026-07-01T00:00:00Z",
            window_end="2026-07-12T23:59:59Z",
            direction="flat",
            freshness_status="stale",
            coverage_warning="synthetic scope B has stale evidence",
        ),
    ),
}

_BASE = {
    "contract_version": CONTRACT_VERSION,
    "request_type": REQUEST_TYPE,
    "caller_class": "internal_llm",
    "overlay_supplied_by_consumer": True,
    "overlay_no_storage_assertion": True,
    "overlay_discard_required": True,
    "alignment_intent": "evidence_support_only",
}

REQUEST_FIXTURES = {
    "owned_aligned": {
        **_BASE,
        "request_id": "req_overlay_owned_aligned",
        "scope_id": SCOPE_A,
        "overlay_kind": "owned_internal_series",
        "external_overlay_reference": "overlay_local_owned_01",
        "overlay_timestamp": "2026-07-12T18:00:00Z",
        "overlay_freshness_status": "fresh",
        "overlay_scope_context": SCOPE_A,
        "overlay_allowed_use": "bounded_value_alignment",
        "field_manifest": ["timestamp", "value"],
        "values": [
            {"timestamp": "2026-07-03T12:00:00Z", "value": 10},
            {"timestamp": "2026-07-10T12:00:00Z", "value": 7},
        ],
    },
    "customer_stale": {
        **_BASE,
        "request_id": "req_overlay_customer_stale",
        "scope_id": SCOPE_A,
        "overlay_kind": "customer_first_party_series",
        "external_overlay_reference": "overlay_local_customer_01",
        "overlay_timestamp": "2026-06-15T18:00:00Z",
        "overlay_freshness_status": "stale",
        "overlay_scope_context": SCOPE_A,
        "overlay_allowed_use": "bounded_value_alignment",
        "field_manifest": ["timestamp", "value"],
        "values": [
            {"timestamp": "2026-07-03T12:00:00Z", "value": 5},
        ],
    },
    "timeline": {
        **_BASE,
        "request_id": "req_overlay_timeline",
        "scope_id": SCOPE_A,
        "overlay_kind": "intervention_timeline",
        "external_overlay_reference": "overlay_local_timeline_01",
        "overlay_timestamp": "2026-07-12T18:00:00Z",
        "overlay_freshness_status": "fresh",
        "overlay_scope_context": SCOPE_A,
        "overlay_allowed_use": "temporal_alignment",
        "field_manifest": ["timestamp", "event_kind"],
        "values": [
            {"timestamp": "2026-07-08T09:00:00Z", "event_kind": "synthetic_title_change"},
        ],
    },
    "scope_b": {
        **_BASE,
        "request_id": "req_overlay_scope_b",
        "scope_id": SCOPE_B,
        "overlay_kind": "owned_internal_series",
        "external_overlay_reference": "overlay_local_owned_b",
        "overlay_timestamp": "2026-07-12T18:00:00Z",
        "overlay_freshness_status": "fresh",
        "overlay_scope_context": SCOPE_B,
        "overlay_allowed_use": "bounded_value_alignment",
        "field_manifest": ["timestamp", "value"],
        "values": [{"timestamp": "2026-07-05T12:00:00Z", "value": 2}],
    },
}


def get_request_fixture(name: str) -> dict:
    return deepcopy(REQUEST_FIXTURES[name])
