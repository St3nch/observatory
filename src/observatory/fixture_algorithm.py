"""Normative fixture-panel-v1 response construction. Pure; no Evidence Store."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final, Literal

from observatory.capture_event import canonical_json

SCENARIOS: Final[tuple[str, ...]] = (
    "admitted_results",
    "admitted_empty",
    "provider_refusal",
    "provider_failure",
    "malformed_response",
    "wrong_media_type",
    "response_partial",
    "no_response",
    "extra_subject",
    "too_many_results",
)

H_JSON: Final[list[list[str]]] = [["content-type", "application/json"]]
H_PLAIN: Final[list[list[str]]] = [["content-type", "text/plain"]]

MALFORMED_BYTES: Final[bytes] = bytes.fromhex(
    "7b22636f6e7472616374223a22666978747572652d70616e656c2d7631222c"
    "22737461747573223a226f6b222c"
)

TransportState = Literal["response_complete", "response_partial", "no_response"]
Completeness = Literal["complete", "partial"]


@dataclass(frozen=True)
class FixtureTransportResult:
    """Complete in-process transport result, retained until Capture commit."""

    transport_state: TransportState
    headers: list[list[str]] | None
    completeness: Completeness | None
    body: bytes | None
    transport_failure: Mapping[str, str] | None
    classification: str
    observation_count: int


def alt_subject_key(subject_key: str) -> str:
    if subject_key == "other-subject":
        return "other-subject-2"
    return "other-subject"


def admitted_results_body(panel_id: str, subject_key: str, depth: int) -> dict[str, object]:
    results: list[dict[str, object]] = []
    for index in range(1, depth + 1):
        results.append(
            {
                "label": "fixture-result-" + str(index),
                "result_index": index,
                "score": 1000 - index,
                "subject_key": subject_key,
            }
        )
    return {
        "contract": "fixture-panel-v1",
        "panel_id": panel_id,
        "result_count": depth,
        "results": results,
        "status": "ok",
        "subject_key": subject_key,
    }


def admitted_empty_body(panel_id: str, subject_key: str) -> dict[str, object]:
    return {
        "contract": "fixture-panel-v1",
        "panel_id": panel_id,
        "result_count": 0,
        "results": [],
        "status": "ok",
        "subject_key": subject_key,
    }


def refusal_body(panel_id: str, subject_key: str) -> dict[str, object]:
    return {
        "code": "fixture_refusal",
        "contract": "fixture-panel-v1",
        "panel_id": panel_id,
        "status": "refused",
        "subject_key": subject_key,
    }


def failure_body(panel_id: str, subject_key: str) -> dict[str, object]:
    return {
        "code": "fixture_failure",
        "contract": "fixture-panel-v1",
        "panel_id": panel_id,
        "status": "failed",
        "subject_key": subject_key,
    }


def extra_subject_body(panel_id: str, subject_key: str) -> dict[str, object]:
    return {
        "contract": "fixture-panel-v1",
        "panel_id": panel_id,
        "result_count": 1,
        "results": [
            {
                "label": "fixture-result-1",
                "result_index": 1,
                "score": 999,
                "subject_key": alt_subject_key(subject_key),
            }
        ],
        "status": "ok",
        "subject_key": subject_key,
    }


def too_many_results_body(panel_id: str, subject_key: str, depth: int) -> dict[str, object]:
    count = depth + 1
    results: list[dict[str, object]] = []
    for index in range(1, count + 1):
        results.append(
            {
                "label": "fixture-result-" + str(index),
                "result_index": index,
                "score": 1000 - index,
                "subject_key": subject_key,
            }
        )
    return {
        "contract": "fixture-panel-v1",
        "panel_id": panel_id,
        "result_count": count,
        "results": results,
        "status": "ok",
        "subject_key": subject_key,
    }


def construct_fixture_transport(
    panel_id: str,
    subject_key: str,
    depth: int,
    scenario: str,
) -> FixtureTransportResult:
    """Return the normative transport result for one closed fixture scenario."""

    if scenario not in SCENARIOS:
        raise ValueError(f"unknown fixture scenario: {scenario}")
    json_headers = [list(pair) for pair in H_JSON]
    plain_headers = [list(pair) for pair in H_PLAIN]
    if scenario == "admitted_results":
        body = canonical_json(admitted_results_body(panel_id, subject_key, depth))
        return FixtureTransportResult(
            "response_complete", json_headers, "complete", body, None,
            "observation_admitted", depth,
        )
    if scenario == "admitted_empty":
        body = canonical_json(admitted_empty_body(panel_id, subject_key))
        return FixtureTransportResult(
            "response_complete", json_headers, "complete", body, None,
            "observation_admitted_empty", 0,
        )
    if scenario == "provider_refusal":
        body = canonical_json(refusal_body(panel_id, subject_key))
        return FixtureTransportResult(
            "response_complete", json_headers, "complete", body, None,
            "provider_refusal", 0,
        )
    if scenario == "provider_failure":
        body = canonical_json(failure_body(panel_id, subject_key))
        return FixtureTransportResult(
            "response_complete", json_headers, "complete", body, None,
            "provider_failure", 0,
        )
    if scenario == "malformed_response":
        return FixtureTransportResult(
            "response_complete", json_headers, "complete", MALFORMED_BYTES, None,
            "transport_complete_non_admissible", 0,
        )
    if scenario == "wrong_media_type":
        body = canonical_json(admitted_empty_body(panel_id, subject_key))
        return FixtureTransportResult(
            "response_complete", plain_headers, "complete", body, None,
            "transport_complete_non_admissible", 0,
        )
    if scenario == "response_partial":
        full = canonical_json(admitted_results_body(panel_id, subject_key, depth))
        return FixtureTransportResult(
            "response_partial", json_headers, "partial", full[:32], None,
            "response_partial", 0,
        )
    if scenario == "no_response":
        return FixtureTransportResult(
            "no_response",
            None,
            None,
            None,
            {"code": "fixture_no_response", "phase": "receive_response"},
            "no_response",
            0,
        )
    if scenario == "extra_subject":
        body = canonical_json(extra_subject_body(panel_id, subject_key))
        return FixtureTransportResult(
            "response_complete", json_headers, "complete", body, None,
            "admission_rejected", 0,
        )
    body = canonical_json(too_many_results_body(panel_id, subject_key, depth))
    return FixtureTransportResult(
        "response_complete", json_headers, "complete", body, None,
        "admission_rejected", 0,
    )
