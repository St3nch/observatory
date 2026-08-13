"""CE-07: attempt envelope, integrity 409, logical API rebuild."""

from __future__ import annotations

import secrets
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from observatory.api import create_app
from observatory.capture import CaptureOutcome, FixtureCaptureInputs, capture_fixture
from observatory.derive import DEFAULT_VERSION, derive
from observatory.evidence_store import EvidenceStore, IntegrityError, create_store
from observatory.fixture_algorithm import SCENARIOS
from observatory.migrate import connect
from observatory.settings import Settings

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
SHARED_TIMES = {
    "authorized_at": "2026-08-11T20:15:30.123456Z",
    "observatory_version": "conformance-v1",
    "request_started_at": "2026-08-11T20:15:30.200000Z",
    "transport_ended_at": "2026-08-11T20:15:31.000000Z",
}


def _inputs(scenario: str) -> FixtureCaptureInputs:
    no_response = scenario == "no_response"
    return FixtureCaptureInputs(
        scenario=scenario,
        panel_id="panel-alpha",
        subject_key="subject-one",
        depth=2,
        attempt_nonce=secrets.token_hex(32),
        response_headers_at=None if no_response else "2026-08-11T20:15:30.900000Z",
        response_body_ended_at=None if no_response else "2026-08-11T20:15:30.950000Z",
        **SHARED_TIMES,
    )


def _populate_matrix(store: EvidenceStore) -> dict[str, CaptureOutcome]:
    populated: dict[str, CaptureOutcome] = {}
    for scenario in SCENARIOS:
        populated[scenario] = capture_fixture(store, _inputs(scenario))
    return populated

VERSION_B = "fixture-panel-v1-derive-v2"


def _app(store: EvidenceStore, dsn: str, version: str = DEFAULT_VERSION) -> TestClient:
    settings = Settings(
        environment="test",
        database_url=dsn,
        evidence_root=store.root,
        derivation_version_id=version,
    )
    return TestClient(create_app(settings, store=store))


def _xmin_snapshot(dsn: str) -> tuple[list[tuple[object, ...]], list[tuple[object, ...]]]:
    with connect(dsn) as connection:
        outcomes = connection.execute(
            """
            SELECT xmin::text, attempt_id, capture_id, derivation_version_id,
                   classification, observation_count
            FROM outcomes
            ORDER BY attempt_id, capture_id NULLS FIRST
            """
        ).fetchall()
        observations = connection.execute(
            """
            SELECT xmin::text, capture_id, derivation_version_id, within_capture_result_id
            FROM observations
            ORDER BY capture_id, result_index
            """
        ).fetchall()
    return list(outcomes), list(observations)


def test_attempt_envelope_distinguishes_all_ten_classifications(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    populated = _populate_matrix(store)
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
    with _app(store, postgres_dsn) as client:
        for scenario in SCENARIOS:
            outcome = populated[scenario]
            response = client.get(f"/v1/attempts/{outcome.attempt_id}")
            assert response.status_code == 200, response.text
            assert "authorization" not in {key.lower() for key in response.request.headers}
            body = response.json()
            expected_class, expected_count = EXPECTED_CAPTURE[scenario]
            assert body["attempt_id"] == outcome.attempt_id
            assert body["derivation_version_id"] == DEFAULT_VERSION
            assert body["attempt_outcome"]["classification"] == "authorized_unresolved"
            assert body["attempt_outcome"]["capture_id"] is None
            assert body["attempt_outcome"]["observation_count"] == 0
            assert body["attempt_outcome"]["attempt_id"] == outcome.attempt_id
            assert body["attempt_outcome"]["derivation_version_id"] == DEFAULT_VERSION
            capture = body["capture_outcome"]
            assert capture is not None
            assert capture["classification"] == expected_class
            assert capture["observation_count"] == expected_count
            assert capture["capture_id"] == outcome.capture_id
            assert capture["attempt_id"] == outcome.attempt_id
            if expected_count == 0:
                assert body["observations"] == []


def test_admitted_observations_identities_values_and_provenance(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    populated = _populate_matrix(store)
    ar = populated["admitted_results"]
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
    with _app(store, postgres_dsn) as client:
        body = client.get(f"/v1/attempts/{ar.attempt_id}").json()
    observations = body["observations"]
    assert len(observations) == 2
    assert observations[0]["within_capture_result_id"] == "result:1"
    assert observations[1]["within_capture_result_id"] == "result:2"
    for index, row in enumerate(observations, start=1):
        assert row["attempt_id"] == ar.attempt_id
        assert row["capture_id"] == ar.capture_id
        assert row["derivation_version_id"] == DEFAULT_VERSION
        assert row["provider"] == "fixture"
        assert row["panel_id"] == "panel-alpha"
        assert row["subject_key"] == "subject-one"
        assert row["result_index"] == index
        assert row["label"] == "fixture-result-" + str(index)
        assert row["score"] == 1000 - index


def test_configured_version_is_not_mixed(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    populated = _populate_matrix(store)
    ar = populated["admitted_results"]
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
        derive(store, connection, VERSION_B)
    with _app(store, postgres_dsn, DEFAULT_VERSION) as client:
        body = client.get(f"/v1/attempts/{ar.attempt_id}").json()
    assert body["derivation_version_id"] == DEFAULT_VERSION
    assert body["attempt_outcome"]["derivation_version_id"] == DEFAULT_VERSION
    assert body["capture_outcome"]["derivation_version_id"] == DEFAULT_VERSION
    assert {item["derivation_version_id"] for item in body["observations"]} == {
        DEFAULT_VERSION
    }


def test_damaged_attempt_returns_integrity_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    populated = _populate_matrix(store)
    ar = populated["admitted_results"]
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
    parent = store.read_attempt(ar.attempt_id)
    assert parent is not None
    fingerprint = parent["request_fingerprint"]
    assert isinstance(fingerprint, str)
    manifest = (
        store.attempt_path(fingerprint, SHARED_TIMES["authorized_at"], ar.attempt_id)
        / "attempt.json"
    )
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    with pytest.raises(IntegrityError):
        store.read_attempt(ar.attempt_id)
    with _app(store, postgres_dsn) as client:
        response = client.get(f"/v1/attempts/{ar.attempt_id}")
    assert response.status_code == 409
    assert "evidence_integrity_failure" in response.text
    assert "attempt_outcome" not in response.json()
    assert "observations" not in response.json()


def test_damaged_capture_returns_integrity_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    populated = _populate_matrix(store)
    ar = populated["admitted_results"]
    other = populated["admitted_empty"]
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
    manifest = store.capture_path(ar.capture_id) / "capture.json"
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    with pytest.raises(IntegrityError):
        store.read_capture(ar.capture_id)
    with _app(store, postgres_dsn) as client:
        damaged = client.get(f"/v1/attempts/{ar.attempt_id}")
        intact = client.get(f"/v1/attempts/{other.attempt_id}")
    assert damaged.status_code == 409
    assert "evidence_integrity_failure" in damaged.text
    assert "capture_outcome" not in damaged.json()
    assert intact.status_code == 200
    assert intact.json()["capture_outcome"]["classification"] == "observation_admitted_empty"


def test_damaged_response_body_returns_integrity_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    populated = _populate_matrix(store)
    ar = populated["admitted_results"]
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
    body_path = store.capture_path(ar.capture_id) / "response.body"
    payload = bytearray(body_path.read_bytes())
    payload[0] ^= 0x01
    body_path.write_bytes(bytes(payload))
    with pytest.raises(IntegrityError):
        store.read_capture(ar.capture_id)
    with _app(store, postgres_dsn) as client:
        response = client.get(f"/v1/attempts/{ar.attempt_id}")
    assert response.status_code == 409
    assert "evidence_integrity_failure" in response.text
    assert "observations" not in response.json()


def test_logical_api_rebuild_equivalence(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    populated = _populate_matrix(store)
    with connect(postgres_dsn) as first:
        derive(store, first, DEFAULT_VERSION)
    with connect(postgres_second_dsn) as second:
        derive(store, second, DEFAULT_VERSION)
    with _app(store, postgres_dsn) as left_client, _app(store, postgres_second_dsn) as right_client:
        for scenario in SCENARIOS:
            attempt_id = populated[scenario].attempt_id
            left = left_client.get(f"/v1/attempts/{attempt_id}")
            right = right_client.get(f"/v1/attempts/{attempt_id}")
            assert left.status_code == 200
            assert right.status_code == 200
            assert left.json() == right.json()


def test_api_reads_do_not_mutate_evidence_or_postgres(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    populated = _populate_matrix(store)
    ar = populated["admitted_results"]
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
    before_ops = list(store.recorded_ops)
    before_pg = _xmin_snapshot(postgres_dsn)
    parent = store.read_attempt(ar.attempt_id)
    assert parent is not None
    fingerprint = parent["request_fingerprint"]
    assert isinstance(fingerprint, str)
    attempt_bytes = (
        store.attempt_path(fingerprint, SHARED_TIMES["authorized_at"], ar.attempt_id)
        / "attempt.json"
    ).read_bytes()
    with _app(store, postgres_dsn) as client:
        assert client.get(f"/v1/attempts/{ar.attempt_id}").status_code == 200
    after_pg = _xmin_snapshot(postgres_dsn)
    assert store.recorded_ops == before_ops
    assert after_pg == before_pg
    after_bytes = (
        store.attempt_path(fingerprint, SHARED_TIMES["authorized_at"], ar.attempt_id)
        / "attempt.json"
    ).read_bytes()
    assert after_bytes == attempt_bytes


def test_unknown_attempt_is_not_a_success_envelope(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
    with _app(store, postgres_dsn) as client:
        missing = client.get("/v1/attempts/" + ("a" * 64))
        malformed = client.get("/v1/attempts/not-an-id")
    assert missing.status_code == 404
    assert malformed.status_code == 404
    assert "attempt_outcome" not in missing.json()
