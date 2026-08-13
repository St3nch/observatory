"""CE-06: full fixture derive matrix, rebuild, multi-version, damage refuse."""

from __future__ import annotations

import secrets
from pathlib import Path

import psycopg
import pytest

from observatory.capture import (
    CaptureOutcome,
    FixtureCaptureInputs,
    capture_fixture,
)
from observatory.capture_event import (
    attempt_document,
    body_ref,
    canonical_json,
    capture_document,
    validate_parameters,
)
from observatory.derive import derive
from observatory.evidence_store import EvidenceStore, IntegrityError, create_store
from observatory.fixture_algorithm import SCENARIOS
from observatory.migrate import connect

# Independent spec table. Not imported from the production classifier.
EXPECTED_CAPTURE: dict[str, tuple[str, int]] = {
    "admitted_results": ("observation_admitted", 2),
    "admitted_empty": ("observation_admitted_empty", 0),
    "provider_refusal": ("provider_refusal", 0),
    "provider_failure": ("provider_failure", 0),
    "malformed_response": ("transport_complete_non_admissible", 0),
    "wrong_media_type": ("transport_complete_non_admissible", 0),
    "response_partial": ("response_partial", 0),
    "no_response": ("no_response", 0),
    "extra_subject": ("admission_rejected", 0),
    "too_many_results": ("admission_rejected", 0),
}
VERSION_A = "fixture-panel-v1-derive-v1"
VERSION_B = "fixture-panel-v1-derive-v2"
SHARED_TIMES = {
    "authorized_at": "2026-08-11T20:15:30.123456Z",
    "observatory_version": "conformance-v1",
    "request_started_at": "2026-08-11T20:15:30.200000Z",
    "transport_ended_at": "2026-08-11T20:15:31.000000Z",
}
HEADERS_AT = "2026-08-11T20:15:30.900000Z"
BODY_ENDED_AT = "2026-08-11T20:15:30.950000Z"


def _store(tmp_path: Path) -> EvidenceStore:
    return create_store(tmp_path / "evidence")


def _inputs(scenario: str, *, depth: int = 2) -> FixtureCaptureInputs:
    no_response = scenario == "no_response"
    return FixtureCaptureInputs(
        scenario=scenario,
        panel_id="panel-alpha",
        subject_key="subject-one",
        depth=depth,
        attempt_nonce=secrets.token_hex(32),
        response_headers_at=None if no_response else HEADERS_AT,
        response_body_ended_at=None if no_response else BODY_ENDED_AT,
        **SHARED_TIMES,
    )


def _populate_matrix(store: EvidenceStore) -> dict[str, CaptureOutcome]:
    populated: dict[str, CaptureOutcome] = {}
    for scenario in SCENARIOS:
        populated[scenario] = capture_fixture(store, _inputs(scenario))
    return populated


def _logical_snapshot(
    connection: psycopg.Connection[tuple[object, ...]],
) -> tuple[list[tuple[object, ...]], list[tuple[object, ...]], list[tuple[object, ...]]]:
    versions = connection.execute(
        """
        SELECT derivation_version_id, adapter_contract
        FROM derivation_versions
        ORDER BY derivation_version_id
        """
    ).fetchall()
    outcomes = connection.execute(
        """
        SELECT attempt_id, capture_id, derivation_version_id, classification, observation_count
        FROM outcomes
        ORDER BY derivation_version_id, attempt_id, capture_id NULLS FIRST
        """
    ).fetchall()
    observations = connection.execute(
        """
        SELECT
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
        FROM observations
        ORDER BY derivation_version_id, capture_id, result_index
        """
    ).fetchall()
    return list(versions), list(outcomes), list(observations)


def _xmin_snapshot(
    connection: psycopg.Connection[tuple[object, ...]], version: str
) -> tuple[list[tuple[object, ...]], list[tuple[object, ...]], list[tuple[object, ...]]]:
    versions = connection.execute(
        """
        SELECT xmin::text, derivation_version_id, adapter_contract
        FROM derivation_versions
        WHERE derivation_version_id = %s
        """,
        (version,),
    ).fetchall()
    outcomes = connection.execute(
        """
        SELECT xmin::text, attempt_id, capture_id, derivation_version_id,
               classification, observation_count
        FROM outcomes
        WHERE derivation_version_id = %s
        ORDER BY attempt_id, capture_id NULLS FIRST
        """,
        (version,),
    ).fetchall()
    observations = connection.execute(
        """
        SELECT xmin::text, capture_id, derivation_version_id, within_capture_result_id,
               attempt_id, provider, panel_id, subject_key, result_index, label, score
        FROM observations
        WHERE derivation_version_id = %s
        ORDER BY capture_id, result_index
        """,
        (version,),
    ).fetchall()
    return list(versions), list(outcomes), list(observations)


def test_all_ten_attempt_and_capture_stage_outcomes(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    populated = _populate_matrix(store)
    with connect(postgres_dsn) as connection:
        derive(store, connection, VERSION_A)
        attempt_rows = connection.execute(
            """
            SELECT attempt_id, classification, observation_count
            FROM outcomes
            WHERE capture_id IS NULL
            ORDER BY attempt_id
            """
        ).fetchall()
        capture_rows = {
            row[0]: (row[1], row[2], row[3])
            for row in connection.execute(
                """
                SELECT capture_id, attempt_id, classification, observation_count
                FROM outcomes
                WHERE capture_id IS NOT NULL
                """
            ).fetchall()
        }
    assert len(attempt_rows) == 10
    assert {row[1] for row in attempt_rows} == {"authorized_unresolved"}
    assert {row[2] for row in attempt_rows} == {0}
    assert {row[0] for row in attempt_rows} == {
        populated[scenario].attempt_id for scenario in SCENARIOS
    }
    for scenario, expected in EXPECTED_CAPTURE.items():
        outcome = populated[scenario]
        row = capture_rows[outcome.capture_id]
        assert row[0] == outcome.attempt_id
        assert row[1] == expected[0]
        assert row[2] == expected[1]


def test_observation_counts_only_admitted_results(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    populated = _populate_matrix(store)
    with connect(postgres_dsn) as connection:
        derive(store, connection, VERSION_A)
        observations = connection.execute(
            """
            SELECT capture_id, count(*)
            FROM observations
            GROUP BY capture_id
            """
        ).fetchall()
    counts = {row[0]: row[1] for row in observations}
    assert counts == {populated["admitted_results"].capture_id: 2}
    for scenario in SCENARIOS:
        if scenario == "admitted_results":
            continue
        assert populated[scenario].capture_id not in counts


def test_admitted_results_identity_values_and_provenance(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    populated = _populate_matrix(store)
    ar = populated["admitted_results"]
    with connect(postgres_dsn) as connection:
        derive(store, connection, VERSION_A)
        rows = connection.execute(
            """
            SELECT within_capture_result_id, attempt_id, provider, panel_id, subject_key,
                   result_index, label, score
            FROM observations
            WHERE capture_id = %s
            ORDER BY result_index
            """,
            (ar.capture_id,),
        ).fetchall()
    assert rows == [
        (
            "result:1",
            ar.attempt_id,
            "fixture",
            "panel-alpha",
            "subject-one",
            1,
            "fixture-result-1",
            999,
        ),
        (
            "result:2",
            ar.attempt_id,
            "fixture",
            "panel-alpha",
            "subject-one",
            2,
            "fixture-result-2",
            998,
        ),
    ]


def test_admitted_empty_success_has_zero_observations(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    empty = capture_fixture(store, _inputs("admitted_empty"))
    with connect(postgres_dsn) as connection:
        derive(store, connection, VERSION_A)
        capture_row = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE capture_id = %s
            """,
            (empty.capture_id,),
        ).fetchone()
        count = connection.execute("SELECT count(*) FROM observations").fetchone()
    assert capture_row == ("observation_admitted_empty", 0)
    assert count == (0,)


@pytest.mark.parametrize("depth", [1, 16])
def test_admitted_results_depth_boundaries(
    tmp_path: Path, postgres_dsn: str, depth: int
) -> None:
    store = _store(tmp_path)
    outcome = capture_fixture(store, _inputs("admitted_results", depth=depth))
    with connect(postgres_dsn) as connection:
        derive(store, connection, VERSION_A)
        capture_row = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE capture_id = %s
            """,
            (outcome.capture_id,),
        ).fetchone()
        rows = connection.execute(
            """
            SELECT result_index, label, score, within_capture_result_id, subject_key
            FROM observations
            ORDER BY result_index
            """
        ).fetchall()
    assert capture_row == ("observation_admitted", depth)
    assert len(rows) == depth
    for index, row in enumerate(rows, start=1):
        assert row == (
            index,
            "fixture-result-" + str(index),
            1000 - index,
            "result:" + str(index),
            "subject-one",
        )


def test_classification_follows_capture_not_scenario_name(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    parameters = validate_parameters(
        {
            "contract": "fixture-panel-v1",
            "depth": 2,
            "panel_id": "panel-alpha",
            "scenario": "admitted_results",
            "subject_key": "subject-one",
        }
    )
    request_body = canonical_json(parameters)
    attempt = attempt_document(
        parameters=parameters,
        attempt_nonce=secrets.token_hex(32),
        authorized_at=SHARED_TIMES["authorized_at"],
        observatory_version=SHARED_TIMES["observatory_version"],
    )
    attempt_id = store.commit_attempt(attempt, request_body=request_body)
    parent = store.read_attempt(attempt_id)
    assert parent is not None
    body = canonical_json(
        {
            "contract": "fixture-panel-v1",
            "panel_id": "panel-alpha",
            "result_count": 1,
            "results": [
                {
                    "label": "fixture-result-1",
                    "result_index": 1,
                    "score": 999,
                    "subject_key": "other-subject",
                }
            ],
            "status": "ok",
            "subject_key": "subject-one",
        }
    )
    capture = capture_document(
        attempt=parent,
        request_started_at=SHARED_TIMES["request_started_at"],
        transport_ended_at=SHARED_TIMES["transport_ended_at"],
        transport_state="response_complete",
        response={
            "headers": [["content-type", "application/json"]],
            "body": {"state": "present_nonempty", "body": body_ref(body)},
            "completeness": "complete",
        },
        transport_failure=None,
        response_headers_at=HEADERS_AT,
        response_body_ended_at=BODY_ENDED_AT,
    )
    capture_id = store.commit_capture(capture, response_body=body)
    with connect(postgres_dsn) as connection:
        derive(store, connection, VERSION_A)
        capture_row = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE capture_id = %s
            """,
            (capture_id,),
        ).fetchone()
        count = connection.execute("SELECT count(*) FROM observations").fetchone()
    assert capture_row == ("admission_rejected", 0)
    assert count == (0,)


def test_logical_rebuild_equivalence_two_real_databases(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = _store(tmp_path)
    _populate_matrix(store)
    with connect(postgres_dsn) as first:
        derive(store, first, VERSION_A)
        left = _logical_snapshot(first)
    with connect(postgres_second_dsn) as second:
        derive(store, second, VERSION_A)
        right = _logical_snapshot(second)
    assert left == right
    assert left[0] == [(VERSION_A, "fixture-panel-v1")]
    assert len(left[1]) == 20
    assert len(left[2]) == 2


def test_new_version_appends_without_mutating_prior(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    _populate_matrix(store)
    with connect(postgres_dsn) as connection:
        derive(store, connection, VERSION_A)
        before = _xmin_snapshot(connection, VERSION_A)
        derive(store, connection, VERSION_B)
        after = _xmin_snapshot(connection, VERSION_A)
        versions = {
            row[0]
            for row in connection.execute(
                "SELECT derivation_version_id FROM derivation_versions"
            ).fetchall()
        }
        b_outcomes = connection.execute(
            "SELECT count(*) FROM outcomes WHERE derivation_version_id = %s",
            (VERSION_B,),
        ).fetchone()
        b_observations = connection.execute(
            "SELECT count(*) FROM observations WHERE derivation_version_id = %s",
            (VERSION_B,),
        ).fetchone()
    assert before == after
    assert versions == {VERSION_A, VERSION_B}
    assert b_outcomes == (20,)
    assert b_observations == (2,)


def test_damaged_attempt_refuses_only_that_chain(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    ar = capture_fixture(store, _inputs("admitted_results"))
    other = capture_fixture(store, _inputs("provider_refusal"))
    parent = store.read_attempt(ar.attempt_id)
    assert parent is not None
    fingerprint = parent["request_fingerprint"]
    assert isinstance(fingerprint, str)
    attempt_dir = store.attempt_path(fingerprint, SHARED_TIMES["authorized_at"], ar.attempt_id)
    raw = bytearray((attempt_dir / "attempt.json").read_bytes())
    raw[0] ^= 0x01
    (attempt_dir / "attempt.json").write_bytes(bytes(raw))
    with pytest.raises(IntegrityError):
        store.read_attempt(ar.attempt_id)
    with connect(postgres_dsn) as connection:
        summary = derive(store, connection, VERSION_A)
        attempt_ids = {
            row[0]
            for row in connection.execute("SELECT attempt_id FROM outcomes").fetchall()
        }
        capture_ids = {
            row[0]
            for row in connection.execute(
                "SELECT capture_id FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
        observations = connection.execute("SELECT count(*) FROM observations").fetchone()
    assert summary.integrity_failures >= 1
    assert ar.attempt_id not in attempt_ids
    assert ar.capture_id not in capture_ids
    assert other.attempt_id in attempt_ids
    assert other.capture_id in capture_ids
    assert observations == (0,)


def test_damaged_capture_preserves_valid_attempt_and_other_chain(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    ar = capture_fixture(store, _inputs("admitted_results"))
    other = capture_fixture(store, _inputs("admitted_empty"))
    manifest = store.capture_path(ar.capture_id) / "capture.json"
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    with pytest.raises(IntegrityError):
        store.read_capture(ar.capture_id)
    with connect(postgres_dsn) as connection:
        summary = derive(store, connection, VERSION_A)
        ar_attempt = connection.execute(
            """
            SELECT classification FROM outcomes
            WHERE attempt_id = %s AND capture_id IS NULL
            """,
            (ar.attempt_id,),
        ).fetchone()
        ar_capture = connection.execute(
            "SELECT count(*) FROM outcomes WHERE capture_id = %s",
            (ar.capture_id,),
        ).fetchone()
        other_capture = connection.execute(
            """
            SELECT classification FROM outcomes WHERE capture_id = %s
            """,
            (other.capture_id,),
        ).fetchone()
        observations = connection.execute("SELECT count(*) FROM observations").fetchone()
    assert summary.integrity_failures >= 1
    assert ar_attempt == ("authorized_unresolved",)
    assert ar_capture == (0,)
    assert other_capture == ("observation_admitted_empty",)
    assert observations == (0,)


def test_damaged_response_body_preserves_attempt_stage(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    ar = capture_fixture(store, _inputs("admitted_results"))
    body_path = store.capture_path(ar.capture_id) / "response.body"
    payload = bytearray(body_path.read_bytes())
    payload[0] ^= 0x01
    body_path.write_bytes(bytes(payload))
    with pytest.raises(IntegrityError):
        store.read_capture(ar.capture_id)
    with connect(postgres_dsn) as connection:
        summary = derive(store, connection, VERSION_A)
        ar_attempt = connection.execute(
            """
            SELECT classification FROM outcomes
            WHERE attempt_id = %s AND capture_id IS NULL
            """,
            (ar.attempt_id,),
        ).fetchone()
        ar_capture = connection.execute(
            "SELECT count(*) FROM outcomes WHERE capture_id = %s",
            (ar.capture_id,),
        ).fetchone()
        observations = connection.execute("SELECT count(*) FROM observations").fetchone()
    assert summary.integrity_failures >= 1
    assert ar_attempt == ("authorized_unresolved",)
    assert ar_capture == (0,)
    assert observations == (0,)


def test_uncommitted_material_is_ignored(tmp_path: Path, postgres_dsn: str) -> None:
    store = _store(tmp_path)
    live = capture_fixture(store, _inputs("provider_failure"))
    residue_attempt = store.attempt_path("d" * 64, SHARED_TIMES["authorized_at"], "e" * 64)
    residue_attempt.mkdir(parents=True)
    (residue_attempt / "attempt.json").write_bytes(b"{}")
    residue_capture = store.capture_path("f" * 64)
    residue_capture.mkdir(parents=True)
    (residue_capture / "capture.json").write_bytes(b"{}")
    with connect(postgres_dsn) as connection:
        derive(store, connection, VERSION_A)
        attempt_ids = {
            row[0]
            for row in connection.execute("SELECT attempt_id FROM outcomes").fetchall()
        }
        capture_ids = {
            row[0]
            for row in connection.execute(
                "SELECT capture_id FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
    assert attempt_ids == {live.attempt_id}
    assert capture_ids == {live.capture_id}
    assert "e" * 64 not in attempt_ids
    assert "f" * 64 not in capture_ids
