"""admitted_results tracer: Attempt commit, gated fixture transport, Capture, CLI."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Literal

from observatory.capture_event import (
    attempt_document,
    body_ref,
    canonical_json,
    capture_document,
    validate_parameters,
)
from observatory.evidence_store import (
    EvidenceStore,
    StoreError,
    create_store,
    open_store,
)

_ISSUER: Final[object] = object()

PUBLISHED_AR_ATTEMPT_ID: Final[str] = (
    "46d5fb97c109b9f64a42ff3a5e62978e2c25551d6b7274603fc88456acfd9a0f"
)
PUBLISHED_AR_CAPTURE_ID: Final[str] = (
    "604663f0e7842f1e076189652667357083d4c4a5e56a44d67ea4596ef624ad44"
)

__all__ = [
    "AdmittedResultsInputs",
    "CaptureOutcome",
    "PUBLISHED_AR_CAPTURE_ID",
    "PUBLISHED_AR_ATTEMPT_ID",
    "PUBLISHED_AR_INPUTS",
    "VerifiedAttempt",
    "capture_admitted_results",
    "main",
]


@dataclass(frozen=True)
class AdmittedResultsInputs:
    """Frozen inputs for the admitted_results / response_complete tracer."""

    panel_id: str
    subject_key: str
    depth: int
    attempt_nonce: str
    authorized_at: str
    observatory_version: str
    request_started_at: str
    response_headers_at: str
    response_body_ended_at: str
    transport_ended_at: str


PUBLISHED_AR_INPUTS: Final[AdmittedResultsInputs] = AdmittedResultsInputs(
    panel_id="panel-alpha",
    subject_key="subject-one",
    depth=2,
    attempt_nonce="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    authorized_at="2026-08-11T20:15:30.123456Z",
    observatory_version="conformance-v1",
    request_started_at="2026-08-11T20:15:30.200000Z",
    response_headers_at="2026-08-11T20:15:30.900000Z",
    response_body_ended_at="2026-08-11T20:15:30.950000Z",
    transport_ended_at="2026-08-11T20:15:31.000000Z",
)


@dataclass(frozen=True)
class VerifiedAttempt:
    """Capability: a committed Attempt that has passed D5 verify-on-read.

    Only `_issue_verified_attempt` may construct a valid instance. Transport
    accepts this type and nothing else, so the transport call is unreachable
    without a verified commit result.
    """

    attempt_id: str
    document: Mapping[str, object]
    request_body: bytes
    _issued_by: object = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._issued_by is not _ISSUER:
            raise TypeError(
                "VerifiedAttempt is issued only after a verified Attempt commit"
            )


@dataclass(frozen=True)
class FixtureTransportResult:
    """Complete in-process transport result, retained until Capture commit."""

    transport_state: Literal["response_complete"]
    headers: list[list[str]]
    completeness: Literal["complete"]
    body: bytes


@dataclass(frozen=True)
class CaptureOutcome:
    attempt_id: str
    capture_id: str


def _issue_verified_attempt(
    store: EvidenceStore,
    document: Mapping[str, object],
    request_body: bytes,
) -> VerifiedAttempt:
    """Commit+verify an Attempt, then issue the transport capability.

    `store.commit_attempt` returns only after D4 and D5. A raise here means
    no VerifiedAttempt exists, so `_admitted_results_transport` cannot be called.
    """

    attempt_id = store.commit_attempt(document, request_body=request_body)
    read_back = store.read_attempt(attempt_id)
    if read_back is None:
        raise StoreError("committed Attempt is not readable as Evidence")
    return VerifiedAttempt(
        attempt_id=attempt_id,
        document=read_back,
        request_body=request_body,
        _issued_by=_ISSUER,
    )


def _admitted_results_body(panel_id: str, subject_key: str, depth: int) -> dict[str, object]:
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


def _admitted_results_transport(attempt: VerifiedAttempt) -> FixtureTransportResult:
    """In-process admitted_results transport. Requires a VerifiedAttempt capability."""

    if not isinstance(attempt, VerifiedAttempt):
        raise TypeError("fixture transport requires a VerifiedAttempt")
    if attempt._issued_by is not _ISSUER:
        raise TypeError("fixture transport requires an issued VerifiedAttempt")
    parameters = attempt.document["parameters"]
    if not isinstance(parameters, Mapping):
        raise StoreError("Attempt parameters are missing")
    if parameters.get("scenario") != "admitted_results":
        raise StoreError("this tracer implements only scenario=admitted_results")
    panel_id = parameters["panel_id"]
    subject_key = parameters["subject_key"]
    depth = parameters["depth"]
    if not isinstance(panel_id, str) or not isinstance(subject_key, str):
        raise StoreError("panel_id and subject_key must be strings")
    if not isinstance(depth, int) or isinstance(depth, bool):
        raise StoreError("depth must be an integer")
    body = canonical_json(_admitted_results_body(panel_id, subject_key, depth))
    return FixtureTransportResult(
        transport_state="response_complete",
        headers=[["content-type", "application/json"]],
        completeness="complete",
        body=body,
    )


def capture_admitted_results(
    store: EvidenceStore,
    inputs: AdmittedResultsInputs,
) -> CaptureOutcome:
    """Run the admitted_results Attempt → transport → Capture path.

    Transport is invoked only with the VerifiedAttempt issued after commit+verify.
    The FixtureTransportResult is retained in this frame until Capture commit,
    which is the authorized fixture journal-skip condition.
    """

    parameters = validate_parameters(
        {
            "contract": "fixture-panel-v1",
            "depth": inputs.depth,
            "panel_id": inputs.panel_id,
            "scenario": "admitted_results",
            "subject_key": inputs.subject_key,
        }
    )
    request_body = canonical_json(parameters)
    document = attempt_document(
        parameters=parameters,
        attempt_nonce=inputs.attempt_nonce,
        authorized_at=inputs.authorized_at,
        observatory_version=inputs.observatory_version,
    )
    verified = _issue_verified_attempt(store, document, request_body)
    transport_result = _admitted_results_transport(verified)
    capture = capture_document(
        attempt=verified.document,
        request_started_at=inputs.request_started_at,
        transport_ended_at=inputs.transport_ended_at,
        transport_state=transport_result.transport_state,
        response={
            "headers": [list(pair) for pair in transport_result.headers],
            "body": {
                "state": "present_nonempty",
                "body": body_ref(transport_result.body),
            },
            "completeness": transport_result.completeness,
        },
        transport_failure=None,
        response_headers_at=inputs.response_headers_at,
        response_body_ended_at=inputs.response_body_ended_at,
    )
    capture_id = store.commit_capture(capture, response_body=transport_result.body)
    return CaptureOutcome(attempt_id=verified.attempt_id, capture_id=capture_id)


def _open_or_create(root: Path) -> EvidenceStore:
    if (root / "FORMAT.json").is_file():
        return open_store(root)
    return create_store(root)


def main(argv: list[str] | None = None) -> int:
    """CLI: admitted_results tracer with published AR frozen inputs."""

    parser = argparse.ArgumentParser(
        prog="observatory.capture",
        description="Fixture admitted_results capture tracer (CE-03B).",
    )
    parser.add_argument(
        "--evidence-root",
        required=True,
        type=Path,
        help="Format-2 Evidence Store root (created if FORMAT.json is absent).",
    )
    args = parser.parse_args(argv)
    store = _open_or_create(args.evidence_root)
    outcome = capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    sys.stdout.write(f"attempt_id {outcome.attempt_id}\n")
    sys.stdout.write(f"capture_id {outcome.capture_id}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
