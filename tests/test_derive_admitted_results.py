"""CE-05: derive admitted_results into real PostgreSQL."""

from __future__ import annotations

import os
import secrets
import subprocess
import sys
from pathlib import Path

import psycopg
import pytest

from observatory.capture import (
    PUBLISHED_AR_ATTEMPT_ID,
    PUBLISHED_AR_CAPTURE_ID,
    PUBLISHED_AR_INPUTS,
    PUBLISHED_NR_INPUTS,
    FixtureCaptureInputs,
    capture_admitted_results,
    capture_fixture,
)
from observatory.capture_event import (
    attempt_document,
    body_ref,
    canonical_json,
    capture_document,
    validate_parameters,
)
from observatory.derive import (
    DEFAULT_VERSION,
    DerivationError,
    derive_admitted_results,
    main,
)
from observatory.evidence_store import EvidenceStore, IntegrityError, create_store
from observatory.migrate import apply_migrations, apply_schema, connect

AR_RESPONSE_BODY = (
    b'{"contract":"fixture-panel-v1","panel_id":"panel-alpha","result_count":2,'
    b'"results":[{"label":"fixture-result-1","result_index":1,"score":999,'
    b'"subject_key":"subject-one"},{"label":"fixture-result-2","result_index":2,'
    b'"score":998,"subject_key":"subject-one"}],"status":"ok",'
    b'"subject_key":"subject-one"}'
)

PUBLISHED_AR_OBSERVATIONS = (
    {
        "within_capture_result_id": "result:1",
        "result_index": 1,
        "label": "fixture-result-1",
        "score": 999,
        "panel_id": "panel-alpha",
        "subject_key": "subject-one",
    },
    {
        "within_capture_result_id": "result:2",
        "result_index": 2,
        "label": "fixture-result-2",
        "score": 998,
        "panel_id": "panel-alpha",
        "subject_key": "subject-one",
    },
)
SHARED_TIMES = {
    "authorized_at": "2026-08-11T20:15:30.123456Z",
    "observatory_version": "conformance-v1",
    "request_started_at": "2026-08-11T20:15:30.200000Z",
    "transport_ended_at": "2026-08-11T20:15:31.000000Z",
}


def _store(tmp_path: Path) -> EvidenceStore:
    return create_store(tmp_path / "evidence")


def _depth_inputs(depth: int, panel: str, subject: str) -> FixtureCaptureInputs:
    return FixtureCaptureInputs(
        scenario="admitted_results",
        panel_id=panel,
        subject_key=subject,
        depth=depth,
        attempt_nonce=secrets.token_hex(32),
        response_headers_at="2026-08-11T20:15:30.900000Z",
        response_body_ended_at="2026-08-11T20:15:30.950000Z",
        **SHARED_TIMES,
    )


def _fetch_outcomes(connection: psycopg.Connection[tuple[object, ...]]) -> list[tuple[object, ...]]:
    rows = connection.execute(
        """
        SELECT attempt_id, capture_id, derivation_version_id, classification, observation_count
        FROM outcomes
        ORDER BY capture_id NULLS FIRST, attempt_id
        """
    ).fetchall()
    return list(rows)


def _fetch_observations(
    connection: psycopg.Connection[tuple[object, ...]],
) -> list[tuple[object, ...]]:
    rows = connection.execute(
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
        ORDER BY result_index
        """
    ).fetchall()
    return list(rows)


def _snapshot(
    connection: psycopg.Connection[tuple[object, ...]],
) -> tuple[list[tuple[object, ...]], list[tuple[object, ...]]]:
    outcomes = connection.execute(
        """
        SELECT xmin::text, attempt_id, capture_id, derivation_version_id,
               classification, observation_count
        FROM outcomes
        ORDER BY capture_id NULLS FIRST, attempt_id
        """
    ).fetchall()
    observations = connection.execute(
        """
        SELECT xmin::text, capture_id, derivation_version_id, within_capture_result_id,
               attempt_id, provider, panel_id, subject_key, result_index, label, score
        FROM observations
        ORDER BY result_index
        """
    ).fetchall()
    return list(outcomes), list(observations)


def test_real_postgres_is_postgresql(postgres_dsn: str) -> None:
    with connect(postgres_dsn) as connection:
        row = connection.execute("SELECT version()").fetchone()
        vendor = connection.execute("SHOW server_version").fetchone()
    assert row is not None
    assert str(row[0]).startswith("PostgreSQL")
    assert vendor is not None
    assert str(vendor[0])


def test_migrate_creates_authorized_tables(postgres_dsn: str) -> None:
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        names = {
            row[0]
            for row in connection.execute(
                """
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename IN (
                    'derivation_versions', 'outcomes', 'observations'
                  )
                """
            ).fetchall()
        }
        unique = connection.execute(
            """
            SELECT conname, pg_get_constraintdef(oid)
            FROM pg_constraint
            WHERE conname = 'outcomes_identity'
            """
        ).fetchone()
        pk = connection.execute(
            """
            SELECT pg_get_constraintdef(oid)
            FROM pg_constraint
            WHERE conrelid = 'observations'::regclass AND contype = 'p'
            """
        ).fetchone()
    assert names == {"derivation_versions", "outcomes", "observations"}
    assert unique is not None
    assert "UNIQUE NULLS NOT DISTINCT" in str(unique[1])
    assert pk is not None
    assert "capture_id" in str(pk[0])
    assert "derivation_version_id" in str(pk[0])
    assert "within_capture_result_id" in str(pk[0])


def test_derive_registers_derivation_version(tmp_path: Path, postgres_dsn: str) -> None:
    store = _store(tmp_path)
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    with connect(postgres_dsn) as connection:
        derive_admitted_results(store, connection, DEFAULT_VERSION)
        row = connection.execute(
            """
            SELECT derivation_version_id, adapter_contract
            FROM derivation_versions
            """
        ).fetchone()
    assert row == (DEFAULT_VERSION, "fixture-panel-v1")


def test_published_ar_attempt_stage_outcome(tmp_path: Path, postgres_dsn: str) -> None:
    store = _store(tmp_path)
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    with connect(postgres_dsn) as connection:
        derive_admitted_results(store, connection, DEFAULT_VERSION)
        attempt_row = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE attempt_id = %s
              AND capture_id IS NULL
              AND derivation_version_id = %s
            """,
            (PUBLISHED_AR_ATTEMPT_ID, DEFAULT_VERSION),
        ).fetchone()
    assert attempt_row == ("authorized_unresolved", 0)


def test_published_ar_capture_stage_and_observations(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    with connect(postgres_dsn) as connection:
        derive_admitted_results(store, connection, DEFAULT_VERSION)
        capture_row = connection.execute(
            """
            SELECT classification, observation_count, attempt_id
            FROM outcomes
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (PUBLISHED_AR_CAPTURE_ID, DEFAULT_VERSION),
        ).fetchone()
        observations = _fetch_observations(connection)
    assert capture_row == ("observation_admitted", 2, PUBLISHED_AR_ATTEMPT_ID)
    assert len(observations) == 2
    for expected, row in zip(PUBLISHED_AR_OBSERVATIONS, observations, strict=True):
        assert row[0] == PUBLISHED_AR_CAPTURE_ID
        assert row[1] == DEFAULT_VERSION
        assert row[2] == expected["within_capture_result_id"]
        assert row[3] == PUBLISHED_AR_ATTEMPT_ID
        assert row[4] == "fixture"
        assert row[5] == expected["panel_id"]
        assert row[6] == expected["subject_key"]
        assert row[7] == expected["result_index"]
        assert row[8] == expected["label"]
        assert row[9] == expected["score"]


def test_depth_governs_observation_count(tmp_path: Path, postgres_dsn: str) -> None:
    store = _store(tmp_path)
    panel = "panel-gamma"
    subject = "subject-deep"
    depth = 4
    outcome = capture_fixture(store, _depth_inputs(depth, panel, subject))
    with connect(postgres_dsn) as connection:
        derive_admitted_results(store, connection, DEFAULT_VERSION)
        capture_row = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE capture_id = %s AND capture_id IS NOT NULL
            """,
            (outcome.capture_id,),
        ).fetchone()
        observations = _fetch_observations(connection)
    assert capture_row == ("observation_admitted", depth)
    assert len(observations) == depth
    for index, row in enumerate(observations, start=1):
        assert row[2] == "result:" + str(index)
        assert row[3] == outcome.attempt_id
        assert row[4] == "fixture"
        assert row[5] == panel
        assert row[6] == subject
        assert row[7] == index
        assert row[8] == "fixture-result-" + str(index)
        assert row[9] == 1000 - index


def test_tampered_capture_yields_no_observations(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    manifest = store.capture_path(PUBLISHED_AR_CAPTURE_ID) / "capture.json"
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    with pytest.raises(IntegrityError):
        store.read_capture(PUBLISHED_AR_CAPTURE_ID)
    with connect(postgres_dsn) as connection:
        summary = derive_admitted_results(store, connection, DEFAULT_VERSION)
        outcomes = _fetch_outcomes(connection)
        observations = _fetch_observations(connection)
    assert summary.integrity_failures >= 1
    assert observations == []
    assert len(outcomes) == 1
    assert outcomes[0][0] == PUBLISHED_AR_ATTEMPT_ID
    assert outcomes[0][1] is None
    assert outcomes[0][3] == "authorized_unresolved"


def test_uncommitted_capture_residue_is_not_derived(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    residue = store.capture_path("b" * 64)
    residue.mkdir(parents=True)
    (residue / "capture.json").write_bytes(b"{}")
    assert "b" * 64 not in store.list_committed_ids("captures")
    with connect(postgres_dsn) as connection:
        derive_admitted_results(store, connection, DEFAULT_VERSION)
        capture_ids = {
            row[0]
            for row in connection.execute("SELECT capture_id FROM observations").fetchall()
        }
    assert capture_ids == {PUBLISHED_AR_CAPTURE_ID}


def test_non_admitted_scenario_gets_attempt_stage_only(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    nr = capture_fixture(store, PUBLISHED_NR_INPUTS)
    with connect(postgres_dsn) as connection:
        derive_admitted_results(store, connection, DEFAULT_VERSION)
        outcomes = _fetch_outcomes(connection)
        observations = _fetch_observations(connection)
    assert observations == []
    assert len(outcomes) == 1
    assert outcomes[0][0] == nr.attempt_id
    assert outcomes[0][1] is None
    assert outcomes[0][3] == "authorized_unresolved"


def test_admitted_results_plain_media_type_is_not_admitted(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    parameters = validate_parameters(
        {
            "contract": "fixture-panel-v1",
            "depth": PUBLISHED_AR_INPUTS.depth,
            "panel_id": PUBLISHED_AR_INPUTS.panel_id,
            "scenario": "admitted_results",
            "subject_key": PUBLISHED_AR_INPUTS.subject_key,
        }
    )
    request_body = canonical_json(parameters)
    attempt = attempt_document(
        parameters=parameters,
        attempt_nonce=PUBLISHED_AR_INPUTS.attempt_nonce,
        authorized_at=PUBLISHED_AR_INPUTS.authorized_at,
        observatory_version=PUBLISHED_AR_INPUTS.observatory_version,
    )
    attempt_id = store.commit_attempt(attempt, request_body=request_body)
    parent = store.read_attempt(attempt_id)
    assert parent is not None
    capture = capture_document(
        attempt=parent,
        request_started_at=PUBLISHED_AR_INPUTS.request_started_at,
        transport_ended_at=PUBLISHED_AR_INPUTS.transport_ended_at,
        transport_state="response_complete",
        response={
            "headers": [["content-type", "text/plain"]],
            "body": {"state": "present_nonempty", "body": body_ref(AR_RESPONSE_BODY)},
            "completeness": "complete",
        },
        transport_failure=None,
        response_headers_at=PUBLISHED_AR_INPUTS.response_headers_at,
        response_body_ended_at=PUBLISHED_AR_INPUTS.response_body_ended_at,
    )
    capture_id = store.commit_capture(capture, response_body=AR_RESPONSE_BODY)
    verified = store.read_capture(capture_id)
    assert verified is not None
    assert verified["transport_state"] == "response_complete"
    response = verified["response"]
    assert isinstance(response, dict)
    assert response["completeness"] == "complete"
    assert response["headers"] == [["content-type", "text/plain"]]
    with connect(postgres_dsn) as connection:
        derive_admitted_results(store, connection, DEFAULT_VERSION)
        outcomes = _fetch_outcomes(connection)
        observations = _fetch_observations(connection)
    assert observations == []
    assert len(outcomes) == 1
    assert outcomes[0][0] == PUBLISHED_AR_ATTEMPT_ID
    assert outcomes[0][1] is None
    assert outcomes[0][3] == "authorized_unresolved"


def test_conflicting_adapter_contract_fails_before_derived_rows(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    with connect(postgres_dsn) as connection:
        apply_schema(connection)
        connection.execute(
            """
            INSERT INTO derivation_versions (
                derivation_version_id, adapter_contract, registered_at
            )
            VALUES (%s, %s, TIMESTAMPTZ '2026-01-01 00:00:00+00')
            """,
            (DEFAULT_VERSION, "not-fixture-panel-v1"),
        )
        connection.commit()
        before = connection.execute(
            """
            SELECT derivation_version_id, adapter_contract, registered_at
            FROM derivation_versions
            """
        ).fetchone()
        with pytest.raises(DerivationError, match="conflicting adapter_contract"):
            derive_admitted_results(store, connection, DEFAULT_VERSION)
        after = connection.execute(
            """
            SELECT derivation_version_id, adapter_contract, registered_at
            FROM derivation_versions
            """
        ).fetchone()
        outcomes = _fetch_outcomes(connection)
        observations = _fetch_observations(connection)
    assert before == after
    assert before is not None
    assert before[0] == DEFAULT_VERSION
    assert before[1] == "not-fixture-panel-v1"
    assert outcomes == []
    assert observations == []


def test_same_version_rerun_does_not_duplicate_or_mutate(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    with connect(postgres_dsn) as connection:
        derive_admitted_results(store, connection, DEFAULT_VERSION)
        before = _snapshot(connection)
        derive_admitted_results(store, connection, DEFAULT_VERSION)
        after = _snapshot(connection)
        outcome_count = connection.execute("SELECT count(*) FROM outcomes").fetchone()
        observation_count = connection.execute("SELECT count(*) FROM observations").fetchone()
    assert before == after
    assert outcome_count == (2,)
    assert observation_count == (2,)
    assert [row[1:] for row in before[0]] == [
        (
            PUBLISHED_AR_ATTEMPT_ID,
            None,
            DEFAULT_VERSION,
            "authorized_unresolved",
            0,
        ),
        (
            PUBLISHED_AR_ATTEMPT_ID,
            PUBLISHED_AR_CAPTURE_ID,
            DEFAULT_VERSION,
            "observation_admitted",
            2,
        ),
    ]


def test_capture_unit_rollback_leaves_no_partial_rows(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _store(tmp_path)
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)

    def interrupt(step: str) -> None:
        if step == "observation":
            raise RuntimeError("forced capture-unit failure")

    with connect(postgres_dsn) as connection:
        with pytest.raises(RuntimeError, match="forced capture-unit failure"):
            derive_admitted_results(
                store, connection, DEFAULT_VERSION, interrupt=interrupt
            )
        outcomes = _fetch_outcomes(connection)
        observations = _fetch_observations(connection)
    assert observations == []
    assert len(outcomes) == 1
    assert outcomes[0][1] is None
    assert outcomes[0][3] == "authorized_unresolved"


def test_derive_cli_on_real_postgres(tmp_path: Path, postgres_dsn: str) -> None:
    root = tmp_path / "evidence"
    store = create_store(root)
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    repo = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "observatory.derive",
            "--evidence-root",
            str(root),
            "--database-url",
            postgres_dsn,
            "--derivation-version",
            DEFAULT_VERSION,
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
    )
    assert result.returncode == 0, result.stderr
    assert f"derivation_version {DEFAULT_VERSION}\n" in result.stdout
    assert "attempt_outcomes 1\n" in result.stdout
    assert "capture_outcomes 1\n" in result.stdout
    assert "observations 2\n" in result.stdout
    with connect(postgres_dsn) as connection:
        observations = _fetch_observations(connection)
        attempt = connection.execute(
            """
            SELECT classification FROM outcomes
            WHERE capture_id IS NULL AND attempt_id = %s
            """,
            (PUBLISHED_AR_ATTEMPT_ID,),
        ).fetchone()
    assert attempt == ("authorized_unresolved",)
    assert len(observations) == 2
    assert observations[0][2] == "result:1"
    assert observations[1][2] == "result:2"


def test_migrate_cli_on_real_postgres(postgres_dsn: str) -> None:
    repo = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "observatory.migrate",
            "--database-url",
            postgres_dsn,
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
    )
    assert result.returncode == 0, result.stderr
    with connect(postgres_dsn) as connection:
        apply_schema(connection)
        count = connection.execute(
            """
            SELECT count(*) FROM pg_tables
            WHERE schemaname = 'public'
              AND tablename IN (
                'derivation_versions', 'outcomes', 'observations'
              )
            """
        ).fetchone()
    assert count == (3,)


def test_list_committed_ids_ignores_uncommitted_residue(tmp_path: Path) -> None:
    store = _store(tmp_path)
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    residue = store.capture_path("c" * 64)
    residue.mkdir(parents=True)
    (residue / "capture.json").write_bytes(b"{}")
    assert store.list_committed_ids("captures") == [PUBLISHED_AR_CAPTURE_ID]
    assert store.list_committed_ids("attempts") == [PUBLISHED_AR_ATTEMPT_ID]


def test_main_entrypoint_rejects_missing_database_url(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from observatory import migrate as migrate_mod
    from observatory.settings import Settings

    monkeypatch.setattr(migrate_mod, "get_settings", lambda: Settings(database_url=None))
    root = tmp_path / "evidence"
    create_store(root)
    code = main(
        [
            "--evidence-root",
            str(root),
            "--derivation-version",
            DEFAULT_VERSION,
        ]
    )
    assert code == 2
