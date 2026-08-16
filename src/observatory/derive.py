"""Derive fixture-panel-v1 Outcomes and Observations from verified Evidence."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from psycopg import Connection

from observatory.evidence_store import EvidenceStore, IntegrityError, open_store
from observatory.migrate import apply_schema, connect, resolve_database_url

VERSION_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9._+:-]{1,128}$")
ADAPTER_CONTRACT: Final[str] = "fixture-panel-v1"
DEFAULT_VERSION: Final[str] = "fixture-panel-v1-derive-v1"
ATTEMPT_CLASSIFICATION: Final[str] = "authorized_unresolved"
PROVIDER: Final[str] = "fixture"
H_JSON: Final[list[list[str]]] = [["content-type", "application/json"]]
REFUSAL_FIELDS: Final[frozenset[str]] = frozenset(
    {"code", "contract", "panel_id", "status", "subject_key"}
)

Interrupt = Callable[[str], None]


class DerivationError(Exception):
    """Derivation refused to proceed."""


@dataclass(frozen=True)
class DeriveSummary:
    derivation_version_id: str
    attempt_outcomes: int
    capture_outcomes: int
    observations: int
    integrity_failures: int


def _require_version(derivation_version_id: str) -> str:
    if VERSION_RE.fullmatch(derivation_version_id) is None:
        raise ValueError(
            "derivation_version_id must match [A-Za-z0-9._+:-]{1,128}"
        )
    return derivation_version_id


def _within_capture_result_id(result_index: int) -> str:
    return "result:" + str(result_index)


def _admit_ok_results(
    parameters: Mapping[str, object], body: bytes
) -> list[dict[str, object]] | None:
    """Apply the spec admission rule for status=ok structured bodies."""

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    if parsed.get("contract") != ADAPTER_CONTRACT:
        return None
    if parsed.get("status") != "ok":
        return None
    if parsed.get("panel_id") != parameters["panel_id"]:
        return None
    if parsed.get("subject_key") != parameters["subject_key"]:
        return None
    results = parsed.get("results")
    if not isinstance(results, list):
        return None
    count = parsed.get("result_count")
    if not isinstance(count, int) or isinstance(count, bool) or count != len(results):
        return None
    depth = parameters["depth"]
    if not isinstance(depth, int) or isinstance(depth, bool):
        return None
    if count < 0 or count > depth:
        return None
    admitted: list[dict[str, object]] = []
    indexes: list[int] = []
    for item in results:
        if not isinstance(item, dict):
            return None
        index = item.get("result_index")
        label = item.get("label")
        score = item.get("score")
        subject = item.get("subject_key")
        if not isinstance(index, int) or isinstance(index, bool):
            return None
        if not isinstance(label, str) or not isinstance(score, int) or isinstance(score, bool):
            return None
        if subject != parameters["subject_key"]:
            return None
        indexes.append(index)
        admitted.append(
            {
                "result_index": index,
                "label": label,
                "score": score,
                "subject_key": subject,
            }
        )
    if sorted(indexes) != list(range(1, count + 1)):
        return None

    def result_index_of(row: dict[str, object]) -> int:
        value = row["result_index"]
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("result_index must be an integer")
        return value

    admitted.sort(key=result_index_of)
    return admitted


def _json_media_type(response: Mapping[str, object]) -> bool:
    return response.get("headers") == H_JSON


def _closed_status_body(
    parsed: Mapping[str, object],
    parameters: Mapping[str, object],
    *,
    status: str,
    code: str,
) -> bool:
    return (
        set(parsed) == REFUSAL_FIELDS
        and parsed.get("code") == code
        and parsed.get("contract") == ADAPTER_CONTRACT
        and parsed.get("status") == status
        and parsed.get("panel_id") == parameters["panel_id"]
        and parsed.get("subject_key") == parameters["subject_key"]
    )


def _classify_capture(
    parameters: Mapping[str, object],
    capture: Mapping[str, object],
    body: bytes | None,
) -> tuple[str, list[dict[str, object]]] | None:
    """Classify from verified Capture branch, headers, body, and admission."""

    state = capture.get("transport_state")
    if state == "no_response":
        return "no_response", []
    if state == "response_partial":
        return "response_partial", []
    if state != "response_complete":
        return None
    response = capture.get("response")
    if not isinstance(response, Mapping) or response.get("completeness") != "complete":
        return "transport_complete_non_admissible", []
    if not _json_media_type(response):
        return "transport_complete_non_admissible", []
    if body is None:
        return "transport_complete_non_admissible", []
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return "transport_complete_non_admissible", []
    if not isinstance(parsed, dict):
        return "transport_complete_non_admissible", []
    if _closed_status_body(parsed, parameters, status="refused", code="fixture_refusal"):
        return "provider_refusal", []
    if _closed_status_body(parsed, parameters, status="failed", code="fixture_failure"):
        return "provider_failure", []
    if parsed.get("status") == "ok":
        admitted = _admit_ok_results(parameters, body)
        if admitted is None:
            return "admission_rejected", []
        if len(admitted) == 0:
            return "observation_admitted_empty", []
        return "observation_admitted", admitted
    return "transport_complete_non_admissible", []


def _register_version(connection: Connection[Any], derivation_version_id: str) -> None:
    with connection.transaction():
        existing = connection.execute(
            """
            SELECT adapter_contract
            FROM derivation_versions
            WHERE derivation_version_id = %s
            """,
            (derivation_version_id,),
        ).fetchone()
        if existing is None:
            connection.execute(
                """
                INSERT INTO derivation_versions (
                    derivation_version_id, adapter_contract, registered_at
                )
                VALUES (%s, %s, now())
                """,
                (derivation_version_id, ADAPTER_CONTRACT),
            )
            return
        registered = existing[0]
        if registered != ADAPTER_CONTRACT:
            raise DerivationError(
                f"derivation version {derivation_version_id!r} is already "
                f"registered with conflicting adapter_contract {registered!r}"
            )


def _write_attempt_outcome(
    connection: Connection[Any],
    derivation_version_id: str,
    attempt_id: str,
) -> None:
    with connection.transaction():
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id,
                capture_id,
                derivation_version_id,
                classification,
                observation_count
            )
            VALUES (%s, NULL, %s, %s, 0)
            ON CONFLICT ON CONSTRAINT outcomes_identity DO NOTHING
            """,
            (attempt_id, derivation_version_id, ATTEMPT_CLASSIFICATION),
        )


def _write_capture_unit(
    connection: Connection[Any],
    derivation_version_id: str,
    attempt_id: str,
    capture_id: str,
    panel_id: str,
    subject_key: str,
    classification: str,
    results: list[dict[str, object]],
    interrupt: Interrupt | None,
) -> None:
    with connection.transaction():
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id,
                capture_id,
                derivation_version_id,
                classification,
                observation_count
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT ON CONSTRAINT outcomes_identity DO NOTHING
            """,
            (
                attempt_id,
                capture_id,
                derivation_version_id,
                classification,
                len(results),
            ),
        )
        if interrupt is not None:
            interrupt("outcome")
        for result in results:
            index = result["result_index"]
            if not isinstance(index, int):
                raise TypeError("admitted result_index must be an integer")
            connection.execute(
                """
                INSERT INTO observations (
                    capture_id,
                    derivation_version_id,
                    within_capture_result_id,
                    attempt_id,
                    provider,
                    panel_id,
                    subject_key,
                    result_index,
                    label,
                    score
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (capture_id, derivation_version_id, within_capture_result_id)
                DO NOTHING
                """,
                (
                    capture_id,
                    derivation_version_id,
                    _within_capture_result_id(index),
                    attempt_id,
                    PROVIDER,
                    panel_id,
                    subject_key,
                    index,
                    result["label"],
                    result["score"],
                ),
            )
            if interrupt is not None:
                interrupt("observation")


def derive(
    store: EvidenceStore,
    connection: Connection[Any],
    derivation_version_id: str,
    *,
    interrupt: Interrupt | None = None,
) -> DeriveSummary:
    """Derive Attempt/Capture Outcomes and admitted Observations into PostgreSQL."""

    if type(store) is not EvidenceStore:
        raise TypeError("derive requires the concrete EvidenceStore")
    version = _require_version(derivation_version_id)
    apply_schema(connection)
    registered = False
    integrity_failures = 0
    attempt_written = 0

    def ensure_registered() -> None:
        nonlocal registered
        if registered:
            return
        _register_version(connection, version)
        registered = True

    for attempt_id in store.list_committed_ids("attempts"):
        try:
            document = store.read_attempt(attempt_id)
        except IntegrityError:
            integrity_failures += 1
            continue
        if document is None:
            continue
        if document.get("adapter_contract") != ADAPTER_CONTRACT:
            continue
        ensure_registered()
        _write_attempt_outcome(connection, version, attempt_id)
        attempt_written += 1
    capture_written = 0
    observation_written = 0
    for capture_id in store.list_committed_ids("captures"):
        try:
            capture = store.read_capture(capture_id)
        except IntegrityError:
            integrity_failures += 1
            continue
        if capture is None:
            continue
        cited = capture["attempt_id"]
        if not isinstance(cited, str):
            integrity_failures += 1
            continue
        attempt_id = cited
        try:
            attempt = store.read_attempt(attempt_id)
        except IntegrityError:
            integrity_failures += 1
            continue
        if attempt is None:
            integrity_failures += 1
            continue
        if (
            capture.get("adapter_contract") != ADAPTER_CONTRACT
            or attempt.get("adapter_contract") != ADAPTER_CONTRACT
        ):
            continue
        parameters = attempt["parameters"]
        if not isinstance(parameters, Mapping):
            continue
        panel_id = parameters.get("panel_id")
        subject_key = parameters.get("subject_key")
        if not isinstance(panel_id, str) or not isinstance(subject_key, str):
            continue
        body: bytes | None = None
        if capture.get("transport_state") != "no_response":
            try:
                body = store.read_capture_body(capture_id)
            except IntegrityError:
                integrity_failures += 1
                continue
        classified = _classify_capture(parameters, capture, body)
        if classified is None:
            continue
        classification, results = classified
        ensure_registered()
        _write_capture_unit(
            connection,
            version,
            attempt_id,
            capture_id,
            panel_id,
            subject_key,
            classification,
            results,
            interrupt,
        )
        capture_written += 1
        observation_written += len(results)
    return DeriveSummary(
        derivation_version_id=version,
        attempt_outcomes=attempt_written,
        capture_outcomes=capture_written,
        observations=observation_written,
        integrity_failures=integrity_failures,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="observatory.derive",
        description="Derive fixture-panel-v1 Outcomes and Observations from Evidence.",
    )
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--database-url", default=None)
    parser.add_argument(
        "--derivation-version",
        required=True,
        help="Operator-supplied derivation version identity ([A-Za-z0-9._+:-]{1,128}).",
    )
    args = parser.parse_args(argv)
    try:
        dsn = resolve_database_url(args.database_url)
        version = _require_version(args.derivation_version)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    store = open_store(args.evidence_root)
    with connect(dsn) as connection:
        summary = derive(store, connection, version)
    sys.stdout.write(f"derivation_version {summary.derivation_version_id}\n")
    sys.stdout.write(f"attempt_outcomes {summary.attempt_outcomes}\n")
    sys.stdout.write(f"capture_outcomes {summary.capture_outcomes}\n")
    sys.stdout.write(f"observations {summary.observations}\n")
    sys.stdout.write(f"integrity_failures {summary.integrity_failures}\n")
    return 0


derive_admitted_results = derive


if __name__ == "__main__":
    raise SystemExit(main())
