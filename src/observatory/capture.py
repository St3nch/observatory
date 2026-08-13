"""Fixture-panel-v1 capture: gated transport, all ten scenarios, CLI."""

from __future__ import annotations

import argparse
import secrets
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final

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
from observatory.fixture_algorithm import (
    SCENARIOS,
    FixtureTransportResult,
    construct_fixture_transport,
)

PUBLISHED_AR_ATTEMPT_ID: Final[str] = (
    "46d5fb97c109b9f64a42ff3a5e62978e2c25551d6b7274603fc88456acfd9a0f"
)
PUBLISHED_AR_CAPTURE_ID: Final[str] = (
    "604663f0e7842f1e076189652667357083d4c4a5e56a44d67ea4596ef624ad44"
)
PUBLISHED_RP_ATTEMPT_ID: Final[str] = (
    "2af733226ee72e74ee0a1d5196353d74df816faf0a7801f634fb1a0d0d6784e0"
)
PUBLISHED_RP_CAPTURE_ID: Final[str] = (
    "f1d0ba4aaba85458c6e9aae540d6baf30ba958ebe7104d59c13e65107a6f677b"
)
PUBLISHED_NR_ATTEMPT_ID: Final[str] = (
    "8d94de30e27141dc315bc747afdc8f4ea5877709279a6383c738d6dade855ca2"
)
PUBLISHED_NR_CAPTURE_ID: Final[str] = (
    "b7cde7e1f921598fd7daf1ac7f7fe16a964832a58adb3cf5b6e47ed017e02134"
)

__all__ = [
    "AdmittedResultsInputs",
    "CaptureOutcome",
    "FixtureCaptureInputs",
    "PUBLISHED_AR_CAPTURE_ID",
    "PUBLISHED_AR_ATTEMPT_ID",
    "PUBLISHED_AR_INPUTS",
    "PUBLISHED_NR_CAPTURE_ID",
    "PUBLISHED_NR_ATTEMPT_ID",
    "PUBLISHED_NR_INPUTS",
    "PUBLISHED_RP_CAPTURE_ID",
    "PUBLISHED_RP_ATTEMPT_ID",
    "PUBLISHED_RP_INPUTS",
    "capture_admitted_results",
    "capture_fixture",
    "main",
]


@dataclass(frozen=True)
class FixtureCaptureInputs:
    """Frozen inputs for one fixture-panel-v1 capture."""

    scenario: str
    panel_id: str
    subject_key: str
    depth: int
    attempt_nonce: str
    authorized_at: str
    observatory_version: str
    request_started_at: str
    response_headers_at: str | None
    response_body_ended_at: str | None
    transport_ended_at: str


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

    def as_fixture_inputs(self) -> FixtureCaptureInputs:
        return FixtureCaptureInputs(
            scenario="admitted_results",
            panel_id=self.panel_id,
            subject_key=self.subject_key,
            depth=self.depth,
            attempt_nonce=self.attempt_nonce,
            authorized_at=self.authorized_at,
            observatory_version=self.observatory_version,
            request_started_at=self.request_started_at,
            response_headers_at=self.response_headers_at,
            response_body_ended_at=self.response_body_ended_at,
            transport_ended_at=self.transport_ended_at,
        )


def _published(
    scenario: str,
    nonce: str,
    *,
    headers_at: str | None,
    body_ended_at: str | None,
) -> FixtureCaptureInputs:
    return FixtureCaptureInputs(
        scenario=scenario,
        panel_id="panel-alpha",
        subject_key="subject-one",
        depth=2,
        attempt_nonce=nonce,
        authorized_at="2026-08-11T20:15:30.123456Z",
        observatory_version="conformance-v1",
        request_started_at="2026-08-11T20:15:30.200000Z",
        response_headers_at=headers_at,
        response_body_ended_at=body_ended_at,
        transport_ended_at="2026-08-11T20:15:31.000000Z",
    )


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
PUBLISHED_RP_INPUTS: Final[FixtureCaptureInputs] = _published(
    "response_partial",
    "1123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    headers_at="2026-08-11T20:15:30.900000Z",
    body_ended_at="2026-08-11T20:15:30.920000Z",
)
PUBLISHED_NR_INPUTS: Final[FixtureCaptureInputs] = _published(
    "no_response",
    "2123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    headers_at=None,
    body_ended_at=None,
)


@dataclass(frozen=True)
class CaptureOutcome:
    attempt_id: str
    capture_id: str
    classification: str
    observation_count: int


def _freeze_maps(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze_maps(item) for key, item in value.items()})
    if isinstance(value, list):
        return [_freeze_maps(item) for item in value]
    return value


def _build_transport_gate() -> tuple[object, object, type]:
    """Closure-held issuance registry. Ordinary code cannot mint membership."""

    issued: list[object] = []

    class _VerifiedAttempt:
        """Internal capability. Not supported public API."""

        __slots__ = (
            "attempt_id",
            "document",
            "request_body",
            "_panel_id",
            "_subject_key",
            "_depth",
            "_scenario",
        )
        attempt_id: str
        document: Mapping[str, object]
        request_body: bytes
        _panel_id: str
        _subject_key: str
        _depth: int
        _scenario: str

        def __init__(self, *args: object, **kwargs: object) -> None:
            raise TypeError("cannot construct a transport capability")

        def __setattr__(self, name: str, value: object) -> None:
            raise AttributeError("issued transport capability is immutable")

        def __delattr__(self, name: str) -> None:
            raise AttributeError("issued transport capability is immutable")

    def _is_issued(attempt: object) -> bool:
        return any(candidate is attempt for candidate in issued)

    def issue(
        store: EvidenceStore,
        document: Mapping[str, object],
        request_body: bytes,
    ) -> _VerifiedAttempt:
        if type(store) is not EvidenceStore:
            raise TypeError(
                "fixture transport requires the concrete EvidenceStore "
                "from create_store/open_store"
            )
        attempt_id = store.commit_attempt(document, request_body=request_body)
        read_back = store.read_attempt(attempt_id)
        if read_back is None:
            raise StoreError("committed Attempt is not readable as Evidence")
        frozen_parameters = validate_parameters(request_body)
        scenario = frozen_parameters["scenario"]
        panel_id = frozen_parameters["panel_id"]
        subject_key = frozen_parameters["subject_key"]
        depth = frozen_parameters["depth"]
        if not isinstance(scenario, str) or scenario not in SCENARIOS:
            raise StoreError("scenario is not a fixture-panel-v1 scenario")
        if not isinstance(panel_id, str) or not isinstance(subject_key, str):
            raise StoreError("panel_id and subject_key must be strings")
        if not isinstance(depth, int) or isinstance(depth, bool):
            raise StoreError("depth must be an integer")
        capability = object.__new__(_VerifiedAttempt)
        object.__setattr__(capability, "attempt_id", attempt_id)
        object.__setattr__(capability, "document", _freeze_maps(read_back))
        object.__setattr__(capability, "request_body", bytes(request_body))
        object.__setattr__(capability, "_panel_id", panel_id)
        object.__setattr__(capability, "_subject_key", subject_key)
        object.__setattr__(capability, "_depth", depth)
        object.__setattr__(capability, "_scenario", scenario)
        issued.append(capability)
        return capability

    def transport(attempt: object) -> FixtureTransportResult:
        if type(attempt) is not _VerifiedAttempt or not _is_issued(attempt):
            raise TypeError("fixture transport requires a verified committed Attempt")
        return construct_fixture_transport(
            attempt._panel_id,
            attempt._subject_key,
            attempt._depth,
            attempt._scenario,
        )

    return issue, transport, _VerifiedAttempt


_issue_verified_attempt: Any
_admitted_results_transport: Any
_VerifiedAttempt: type
_issue_verified_attempt, _admitted_results_transport, _VerifiedAttempt = (
    _build_transport_gate()
)


def _require_concrete_store(store: EvidenceStore) -> None:
    if type(store) is not EvidenceStore:
        raise TypeError(
            "fixture transport requires the concrete EvidenceStore "
            "from create_store/open_store"
        )


def capture_fixture(store: EvidenceStore, inputs: FixtureCaptureInputs) -> CaptureOutcome:
    """Run Attempt → gated fixture transport → Capture for one closed scenario."""

    _require_concrete_store(store)
    parameters = validate_parameters(
        {
            "contract": "fixture-panel-v1",
            "depth": inputs.depth,
            "panel_id": inputs.panel_id,
            "scenario": inputs.scenario,
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
    if transport_result.transport_state == "no_response":
        capture = capture_document(
            attempt=verified.document,
            request_started_at=inputs.request_started_at,
            transport_ended_at=inputs.transport_ended_at,
            transport_state="no_response",
            response=None,
            transport_failure=(
                dict(transport_result.transport_failure)
                if transport_result.transport_failure is not None
                else None
            ),
            response_headers_at=None,
            response_body_ended_at=None,
        )
        response_body: bytes | None = None
    else:
        if transport_result.body is None or transport_result.headers is None:
            raise StoreError("response-bearing transport produced no body or headers")
        if transport_result.completeness is None:
            raise StoreError("response-bearing transport produced no completeness")
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
        response_body = transport_result.body
    capture_id = store.commit_capture(capture, response_body=response_body)
    return CaptureOutcome(
        attempt_id=verified.attempt_id,
        capture_id=capture_id,
        classification=transport_result.classification,
        observation_count=transport_result.observation_count,
    )


def capture_admitted_results(
    store: EvidenceStore,
    inputs: AdmittedResultsInputs,
) -> CaptureOutcome:
    """CE-03B entrypoint: admitted_results / response_complete only."""

    return capture_fixture(store, inputs.as_fixture_inputs())


def _open_or_create(root: Path) -> EvidenceStore:
    if (root / "FORMAT.json").is_file():
        return open_store(root)
    return create_store(root)


def _fresh_nonce() -> str:
    return secrets.token_hex(32)


def main(argv: list[str] | None = None) -> int:
    """CLI: fixture-panel-v1 capture. Default is published AR (CE-03B)."""

    parser = argparse.ArgumentParser(
        prog="observatory.capture",
        description="Fixture-panel-v1 capture (CE-04 matrix; default published AR).",
    )
    parser.add_argument(
        "--evidence-root",
        required=True,
        type=Path,
        help="Format-2 Evidence Store root (created if FORMAT.json is absent).",
    )
    parser.add_argument(
        "--vector",
        choices=("AR", "RP", "NR"),
        help="Use a published frozen conformance vector.",
    )
    parser.add_argument(
        "--scenario",
        choices=SCENARIOS,
        help="Fixture scenario (fresh nonce; ignored when --vector is set).",
    )
    args = parser.parse_args(argv)
    if args.vector is not None and args.scenario is not None:
        parser.error("use either --vector or --scenario, not both")
    store = _open_or_create(args.evidence_root)
    if args.vector == "RP":
        outcome = capture_fixture(store, PUBLISHED_RP_INPUTS)
    elif args.vector == "NR":
        outcome = capture_fixture(store, PUBLISHED_NR_INPUTS)
    elif args.vector == "AR" or args.scenario is None:
        outcome = capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    else:
        generated = FixtureCaptureInputs(
            scenario=args.scenario,
            panel_id="panel-alpha",
            subject_key="subject-one",
            depth=2,
            attempt_nonce=_fresh_nonce(),
            authorized_at="2026-08-11T20:15:30.123456Z",
            observatory_version="conformance-v1",
            request_started_at="2026-08-11T20:15:30.200000Z",
            response_headers_at=(
                None
                if args.scenario == "no_response"
                else "2026-08-11T20:15:30.900000Z"
            ),
            response_body_ended_at=(
                None
                if args.scenario == "no_response"
                else "2026-08-11T20:15:30.950000Z"
            ),
            transport_ended_at="2026-08-11T20:15:31.000000Z",
        )
        outcome = capture_fixture(store, generated)
    sys.stdout.write(f"attempt_id {outcome.attempt_id}\n")
    sys.stdout.write(f"capture_id {outcome.capture_id}\n")
    sys.stdout.write(f"classification {outcome.classification}\n")
    sys.stdout.write(f"observation_count {outcome.observation_count}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
