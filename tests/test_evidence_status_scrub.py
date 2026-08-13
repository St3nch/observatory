"""CE-08: status, report-only scrub, and refuse verification."""

from __future__ import annotations

import os
import secrets
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from observatory.api import create_app
from observatory.capture import FixtureCaptureInputs, capture_fixture
from observatory.capture_event import (
    canonical_json,
    content_digest,
    fingerprint_document,
    fixture_request,
)
from observatory.derive import DEFAULT_VERSION, derive
from observatory.evidence import main, report_path, scrub_store
from observatory.evidence_store import (
    EvidenceStore,
    IntegrityError,
    create_store,
    inspect_store,
    open_store,
)
from observatory.migrate import connect
from observatory.settings import Settings

SHARED_TIMES = {
    "authorized_at": "2026-08-11T20:15:30.123456Z",
    "observatory_version": "conformance-v1",
    "request_started_at": "2026-08-11T20:15:30.200000Z",
    "transport_ended_at": "2026-08-11T20:15:31.000000Z",
}


def _inputs(scenario: str = "admitted_results") -> FixtureCaptureInputs:
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


def _store(tmp_path: Path) -> EvidenceStore:
    return create_store(tmp_path / "evidence")


def _snapshot(root: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    return files


def _plant_tmp(root: Path) -> Path:
    planted = root / ".tmp" / "planted-residue"
    planted.parent.mkdir(parents=True, exist_ok=True)
    planted.write_bytes(b"do-not-purge")
    return planted


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    repo = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "-m", "observatory.evidence", *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
    )


def _app(store: EvidenceStore, dsn: str) -> TestClient:
    settings = Settings(
        environment="test",
        database_url=dsn,
        evidence_root=store.root,
        derivation_version_id=DEFAULT_VERSION,
    )
    return TestClient(create_app(settings, store=store))


def test_status_recognizes_openable_format2_store(tmp_path: Path) -> None:
    store = _store(tmp_path)
    result = _run_cli("status", "--evidence-root", str(store.root))
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_status_fails_closed_on_missing_format(tmp_path: Path) -> None:
    root = tmp_path / "empty"
    root.mkdir()
    planted = _plant_tmp(root)
    assert main(["status", "--evidence-root", str(root)]) == 2
    assert planted.is_file()
    assert planted.read_bytes() == b"do-not-purge"


def test_status_fails_closed_on_wrong_format_without_tmp_purge(tmp_path: Path) -> None:
    root = tmp_path / "bad"
    root.mkdir()
    (root / "FORMAT.json").write_bytes(b'{"store_format":1}')
    planted = _plant_tmp(root)
    before = planted.read_bytes()
    assert main(["status", "--evidence-root", str(root)]) == 2
    assert planted.read_bytes() == before


def test_inspect_store_does_not_purge_tmp(tmp_path: Path) -> None:
    store = _store(tmp_path)
    planted = _plant_tmp(store.root)
    inspect_store(store.root)
    assert planted.read_bytes() == b"do-not-purge"
    opened = open_store(store.root)
    assert not planted.exists()
    assert opened.root == store.root


def test_scrub_accepts_clean_committed_attempt_and_capture(tmp_path: Path) -> None:
    store = _store(tmp_path)
    outcome = capture_fixture(store, _inputs("admitted_results"))
    before = _snapshot(store.root)
    planted = _plant_tmp(store.root)
    assert main(["scrub", "--evidence-root", str(store.root)]) == 0
    after = {
        key: value
        for key, value in _snapshot(store.root).items()
        if key != ".tmp/planted-residue"
    }
    assert after == before
    assert planted.read_bytes() == b"do-not-purge"
    assert store.read_attempt(outcome.attempt_id) is not None
    assert store.read_capture(outcome.capture_id) is not None


def test_scrub_cli_module_entrypoint_clean(tmp_path: Path) -> None:
    store = _store(tmp_path)
    capture_fixture(store, _inputs("admitted_empty"))
    result = _run_cli("scrub", "--evidence-root", str(store.root))
    assert result.returncode == 0, result.stderr


def test_uncommitted_directory_is_not_admitted_or_reported(tmp_path: Path) -> None:
    store = _store(tmp_path)
    live = capture_fixture(store, _inputs("provider_failure"))
    residue = store.capture_path("c" * 64)
    residue.mkdir(parents=True)
    (residue / "capture.json").write_bytes(b"{}")
    before = _snapshot(store.root)
    code, output = _run_scrub(store.root)
    assert code == 0
    assert report_path(store.root, residue) not in output
    assert store.read_capture("c" * 64) is None
    assert store.read_capture(live.capture_id) is not None
    assert _snapshot(store.root) == before


def _run_scrub(root: Path) -> tuple[int, str]:
    from io import StringIO

    buffer = StringIO()
    err = StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = buffer, err
    try:
        code = main(["scrub", "--evidence-root", str(root)])
    finally:
        sys.stdout, sys.stderr = old_out, old_err
    return code, buffer.getvalue()


def test_scrub_reports_wrong_committed_contents(tmp_path: Path) -> None:
    store = _store(tmp_path)
    outcome = capture_fixture(store, _inputs("admitted_results"))
    parent = store.read_attempt(outcome.attempt_id)
    assert parent is not None
    fingerprint = parent["request_fingerprint"]
    assert isinstance(fingerprint, str)
    bundle = store.attempt_path(
        fingerprint, SHARED_TIMES["authorized_at"], outcome.attempt_id
    )
    (bundle / "COMMITTED").write_bytes(b"not-the-event-id\n")
    planted = _plant_tmp(store.root)
    before = _snapshot(store.root)
    code, output = _run_scrub(store.root)
    assert code == 1
    assert report_path(store.root, bundle) in output
    assert _snapshot(store.root) == before
    assert planted.read_bytes() == b"do-not-purge"
    with pytest.raises(IntegrityError):
        store.read_attempt(outcome.attempt_id)


def test_scrub_reports_manifest_digest_mismatch(tmp_path: Path) -> None:
    store = _store(tmp_path)
    outcome = capture_fixture(store, _inputs("admitted_results"))
    bundle = store.capture_path(outcome.capture_id)
    raw = bytearray((bundle / "capture.json").read_bytes())
    raw[0] ^= 0x01
    (bundle / "capture.json").write_bytes(bytes(raw))
    before = _snapshot(store.root)
    code, output = _run_scrub(store.root)
    assert code == 1
    assert report_path(store.root, bundle) in output
    assert _snapshot(store.root) == before
    with pytest.raises(IntegrityError):
        store.read_capture(outcome.capture_id)


def test_scrub_reports_incorrect_terminal_identity(tmp_path: Path) -> None:
    store = _store(tmp_path)
    capture_fixture(store, _inputs("admitted_results"))
    misplaced = store.root / "captures" / "v1" / "zz" / "not-sharded" / "wrong-name"
    misplaced.mkdir(parents=True)
    (misplaced / "capture.json").write_bytes(b'{"schema":"observatory.capture-event"}')
    (misplaced / "COMMITTED").write_bytes(b"wrong-name\n")
    before = _snapshot(store.root)
    output = _run_scrub(store.root)[1]
    assert report_path(store.root, misplaced) in output
    assert main(["scrub", "--evidence-root", str(store.root)]) == 1
    assert _snapshot(store.root) == before
    discovered = inspect_store(store.root).list_commitment_claiming_directories("captures")
    assert misplaced in discovered


def test_scrub_reports_self_consistent_schema_failure(tmp_path: Path) -> None:
    store = _store(tmp_path)
    capture_fixture(store, _inputs("admitted_results"))
    invalid = {
        "adapter_contract": "fixture-panel-v1",
        "attempt_nonce": "0" * 64,
        "authorized_at": SHARED_TIMES["authorized_at"],
        "extra": "not-in-schema",
        "parameters": {
            "contract": "fixture-panel-v1",
            "depth": 2,
            "panel_id": "panel-alpha",
            "scenario": "admitted_results",
            "subject_key": "subject-one",
        },
        "policy": {"mode": "fixture_no_spend", "policy_version": "fixture-v1"},
        "provider": "fixture",
        "request": fixture_request(
            body=canonical_json(
                {
                    "contract": "fixture-panel-v1",
                    "depth": 2,
                    "panel_id": "panel-alpha",
                    "scenario": "admitted_results",
                    "subject_key": "subject-one",
                }
            )
        ),
        "request_fingerprint": "0" * 64,
        "schema": "observatory.attempt-event",
        "software": {"observatory_version": "conformance-v1"},
        "version": 1,
    }
    raw = canonical_json(invalid)
    event_id = content_digest(raw)
    bundle = store.root / "attempts" / "v1" / event_id[:2] / event_id[2:4] / event_id
    bundle.mkdir(parents=True)
    (bundle / "attempt.json").write_bytes(raw)
    (bundle / "COMMITTED").write_bytes(f"{event_id}\n".encode())
    assert content_digest((bundle / "attempt.json").read_bytes()) == event_id
    before = _snapshot(store.root)
    output = _run_scrub(store.root)[1]
    assert report_path(store.root, bundle) in output
    assert main(["scrub", "--evidence-root", str(store.root)]) == 1
    assert _snapshot(store.root) == before
    with pytest.raises(IntegrityError):
        store.verify_attempt_directory(bundle)


def test_scrub_reports_request_body_tamper(tmp_path: Path) -> None:
    store = _store(tmp_path)
    outcome = capture_fixture(store, _inputs("admitted_results"))
    parent = store.read_attempt(outcome.attempt_id)
    assert parent is not None
    fingerprint = parent["request_fingerprint"]
    assert isinstance(fingerprint, str)
    bundle = store.attempt_path(
        fingerprint, SHARED_TIMES["authorized_at"], outcome.attempt_id
    )
    body = bundle / "request.body"
    payload = bytearray(body.read_bytes())
    payload[0] ^= 0x01
    body.write_bytes(bytes(payload))
    before = _snapshot(store.root)
    output = _run_scrub(store.root)[1]
    assert report_path(store.root, bundle) in output
    assert _snapshot(store.root) == before
    with pytest.raises(IntegrityError):
        store.read_attempt(outcome.attempt_id)


def test_scrub_reports_response_body_tamper(tmp_path: Path) -> None:
    store = _store(tmp_path)
    outcome = capture_fixture(store, _inputs("admitted_results"))
    bundle = store.capture_path(outcome.capture_id)
    body = bundle / "response.body"
    payload = bytearray(body.read_bytes())
    payload[-1] ^= 0x01
    body.write_bytes(bytes(payload))
    before = _snapshot(store.root)
    output = _run_scrub(store.root)[1]
    assert report_path(store.root, bundle) in output
    assert _snapshot(store.root) == before
    with pytest.raises(IntegrityError):
        store.read_capture(outcome.capture_id)


def test_scrub_reports_pool_object_tamper(tmp_path: Path) -> None:
    store = _store(tmp_path)
    outcome = capture_fixture(store, _inputs("admitted_results"))
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    response = capture["response"]
    assert isinstance(response, dict)
    state = response["body"]
    assert isinstance(state, dict)
    ref = state["body"]
    assert isinstance(ref, dict)
    digest = ref["sha256"]
    assert isinstance(digest, str)
    pool = store.object_path(digest)
    payload = bytearray(pool.read_bytes())
    payload[1] ^= 0x01
    pool.write_bytes(bytes(payload))
    before = _snapshot(store.root)
    output = _run_scrub(store.root)[1]
    assert report_path(store.root, store.capture_path(outcome.capture_id)) in output
    assert _snapshot(store.root) == before
    with pytest.raises(IntegrityError):
        store.read_capture(outcome.capture_id)


def test_scrub_reports_capture_request_mismatch(tmp_path: Path) -> None:
    store = _store(tmp_path)
    outcome = capture_fixture(store, _inputs("admitted_results"))
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    alt_body = canonical_json(
        {
            "contract": "fixture-panel-v1",
            "depth": 2,
            "panel_id": "panel-beta",
            "scenario": "admitted_results",
            "subject_key": "subject-one",
        }
    )
    store.install_object(alt_body)
    mutated = dict(capture)
    request = fixture_request(body=alt_body)
    mutated["request"] = request
    mutated["request_fingerprint"] = content_digest(
        canonical_json(fingerprint_document(request=request))
    )
    raw = canonical_json(mutated)
    new_id = content_digest(raw)
    bundle = store.capture_path(new_id)
    bundle.mkdir(parents=True)
    (bundle / "capture.json").write_bytes(raw)
    (bundle / "COMMITTED").write_bytes(f"{new_id}\n".encode())
    assert store.verify_capture_directory(store.capture_path(outcome.capture_id)) is not None
    with pytest.raises(IntegrityError):
        store.verify_capture_directory(bundle)
    before = _snapshot(store.root)
    output = _run_scrub(store.root)[1]
    assert report_path(store.root, bundle) in output
    assert report_path(store.root, store.capture_path(outcome.capture_id)) not in output
    assert _snapshot(store.root) == before


def test_scrub_reports_uncommitted_parent_attempt(tmp_path: Path) -> None:
    store = _store(tmp_path)
    outcome = capture_fixture(store, _inputs("admitted_results"))
    parent = store.read_attempt(outcome.attempt_id)
    assert parent is not None
    fingerprint = parent["request_fingerprint"]
    assert isinstance(fingerprint, str)
    attempt_dir = store.attempt_path(
        fingerprint, SHARED_TIMES["authorized_at"], outcome.attempt_id
    )
    (attempt_dir / "COMMITTED").unlink()
    capture_dir = store.capture_path(outcome.capture_id)
    before = _snapshot(store.root)
    output = _run_scrub(store.root)[1]
    assert report_path(store.root, capture_dir) in output
    assert report_path(store.root, attempt_dir) not in output
    assert _snapshot(store.root) == before
    assert store.read_attempt(outcome.attempt_id) is None
    with pytest.raises(IntegrityError):
        store.read_capture(outcome.capture_id)


def test_scrub_format_failure_does_not_purge_tmp(tmp_path: Path) -> None:
    root = tmp_path / "broken"
    root.mkdir()
    (root / "FORMAT.json").write_bytes(b"not-format-2")
    planted = _plant_tmp(root)
    assert main(["scrub", "--evidence-root", str(root)]) == 2
    assert planted.read_bytes() == b"do-not-purge"


def test_failed_candidates_are_not_valid_evidence(tmp_path: Path) -> None:
    store = _store(tmp_path)
    outcome = capture_fixture(store, _inputs("admitted_results"))
    bundle = store.capture_path(outcome.capture_id)
    raw = bytearray((bundle / "capture.json").read_bytes())
    raw[2] ^= 0x01
    (bundle / "capture.json").write_bytes(bytes(raw))
    failed = scrub_store(inspect_store(store.root))
    assert bundle in failed
    with pytest.raises(IntegrityError):
        store.read_capture(outcome.capture_id)


def test_derive_and_api_against_damaged_attempt(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = _store(tmp_path)
    damaged = capture_fixture(store, _inputs("admitted_results"))
    sibling = capture_fixture(store, _inputs("provider_refusal"))
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
    parent = store.read_attempt(damaged.attempt_id)
    assert parent is not None
    fingerprint = parent["request_fingerprint"]
    assert isinstance(fingerprint, str)
    bundle = store.attempt_path(
        fingerprint, SHARED_TIMES["authorized_at"], damaged.attempt_id
    )
    raw = bytearray((bundle / "attempt.json").read_bytes())
    raw[0] ^= 0x01
    (bundle / "attempt.json").write_bytes(bytes(raw))
    before = _snapshot(store.root)
    output = _run_scrub(store.root)[1]
    assert report_path(store.root, bundle) in output
    assert _snapshot(store.root) == before
    with _app(store, postgres_dsn) as client:
        response = client.get(f"/v1/attempts/{damaged.attempt_id}")
        sibling_ok = client.get(f"/v1/attempts/{sibling.attempt_id}")
    assert response.status_code == 409
    assert "evidence_integrity_failure" in response.text
    assert "attempt_outcome" not in response.json()
    assert sibling_ok.status_code == 200
    with connect(postgres_second_dsn) as empty:
        derive(store, empty, DEFAULT_VERSION)
        ids = {
            row[0]
            for row in empty.execute("SELECT attempt_id FROM outcomes").fetchall()
        }
        assert damaged.attempt_id not in ids
        assert sibling.attempt_id in ids


def test_derive_and_api_against_damaged_capture(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = _store(tmp_path)
    damaged = capture_fixture(store, _inputs("admitted_results"))
    sibling = capture_fixture(store, _inputs("admitted_empty"))
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
    bundle = store.capture_path(damaged.capture_id)
    raw = bytearray((bundle / "capture.json").read_bytes())
    raw[0] ^= 0x01
    (bundle / "capture.json").write_bytes(bytes(raw))
    before = _snapshot(store.root)
    output = _run_scrub(store.root)[1]
    assert report_path(store.root, bundle) in output
    assert _snapshot(store.root) == before
    with _app(store, postgres_dsn) as client:
        response = client.get(f"/v1/attempts/{damaged.attempt_id}")
        sibling_ok = client.get(f"/v1/attempts/{sibling.attempt_id}")
    assert response.status_code == 409
    assert "evidence_integrity_failure" in response.text
    assert "capture_outcome" not in response.json()
    assert sibling_ok.status_code == 200
    with connect(postgres_second_dsn) as empty:
        derive(store, empty, DEFAULT_VERSION)
        attempt_row = empty.execute(
            """
            SELECT classification FROM outcomes
            WHERE attempt_id = %s AND capture_id IS NULL
            """,
            (damaged.attempt_id,),
        ).fetchone()
        capture_count = empty.execute(
            "SELECT count(*) FROM outcomes WHERE capture_id = %s",
            (damaged.capture_id,),
        ).fetchone()
        sibling_row = empty.execute(
            "SELECT classification FROM outcomes WHERE capture_id = %s",
            (sibling.capture_id,),
        ).fetchone()
        observations = empty.execute("SELECT count(*) FROM observations").fetchone()
    assert attempt_row == ("authorized_unresolved",)
    assert capture_count == (0,)
    assert sibling_row == ("observation_admitted_empty",)
    assert observations == (0,)


def test_derive_and_api_against_damaged_response_body(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = _store(tmp_path)
    damaged = capture_fixture(store, _inputs("admitted_results"))
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
    body = store.capture_path(damaged.capture_id) / "response.body"
    payload = bytearray(body.read_bytes())
    payload[0] ^= 0x01
    body.write_bytes(bytes(payload))
    before = _snapshot(store.root)
    output = _run_scrub(store.root)[1]
    assert report_path(store.root, store.capture_path(damaged.capture_id)) in output
    assert _snapshot(store.root) == before
    with _app(store, postgres_dsn) as client:
        response = client.get(f"/v1/attempts/{damaged.attempt_id}")
    assert response.status_code == 409
    assert "evidence_integrity_failure" in response.text
    with connect(postgres_second_dsn) as empty:
        derive(store, empty, DEFAULT_VERSION)
        attempt_row = empty.execute(
            """
            SELECT classification FROM outcomes
            WHERE attempt_id = %s AND capture_id IS NULL
            """,
            (damaged.attempt_id,),
        ).fetchone()
        capture_count = empty.execute(
            "SELECT count(*) FROM outcomes WHERE capture_id = %s",
            (damaged.capture_id,),
        ).fetchone()
    assert attempt_row == ("authorized_unresolved",)
    assert capture_count == (0,)
