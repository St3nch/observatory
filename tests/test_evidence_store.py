"""Evidence Store foundation: FORMAT, D1–D7, verify-on-read. Real POSIX roots."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from observatory.capture_event import (
    attempt_document,
    body_ref,
    capture_document,
    content_digest,
)
from observatory.evidence_store import (
    FORMAT_BYTES,
    FORMAT_DIGEST,
    EvidenceStore,
    FormatError,
    IntegrityError,
    StoreError,
    create_store,
    open_store,
)

AR_REQUEST_BODY = (
    b'{"contract":"fixture-panel-v1","depth":2,"panel_id":"panel-alpha",'
    b'"scenario":"admitted_results","subject_key":"subject-one"}'
)
AR_RESPONSE_BODY = (
    b'{"contract":"fixture-panel-v1","panel_id":"panel-alpha","result_count":2,'
    b'"results":[{"label":"fixture-result-1","result_index":1,"score":999,'
    b'"subject_key":"subject-one"},{"label":"fixture-result-2","result_index":2,'
    b'"score":998,"subject_key":"subject-one"}],"status":"ok",'
    b'"subject_key":"subject-one"}'
)
AR_ATTEMPT_ID = "46d5fb97c109b9f64a42ff3a5e62978e2c25551d6b7274603fc88456acfd9a0f"
AR_CAPTURE_ID = "604663f0e7842f1e076189652667357083d4c4a5e56a44d67ea4596ef624ad44"
AR_FINGERPRINT = "d18682cc029a8db08b0b761b900db2c7c91f92a99087597281cbdbdaec70e88b"
AR_NONCE = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
AUTHORIZED_AT = "2026-08-11T20:15:30.123456Z"
REQUEST_STARTED_AT = "2026-08-11T20:15:30.200000Z"
RESPONSE_HEADERS_AT = "2026-08-11T20:15:30.900000Z"
TRANSPORT_ENDED_AT = "2026-08-11T20:15:31.000000Z"
OBSERVATORY_VERSION = "conformance-v1"
AR_PARAMETERS: dict[str, Any] = {
    "contract": "fixture-panel-v1",
    "depth": 2,
    "panel_id": "panel-alpha",
    "scenario": "admitted_results",
    "subject_key": "subject-one",
}
ALT_NONCE = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdee"


def _ar_attempt() -> dict[str, Any]:
    return attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )


def _alt_attempt() -> dict[str, Any]:
    return attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=ALT_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )


def _ar_capture(attempt: dict[str, Any]) -> dict[str, Any]:
    return capture_document(
        attempt=attempt,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response={
            "headers": [["content-type", "application/json"]],
            "body": {"state": "present_nonempty", "body": body_ref(AR_RESPONSE_BODY)},
            "completeness": "complete",
        },
        transport_failure=None,
        response_headers_at=RESPONSE_HEADERS_AT,
        response_body_ended_at="2026-08-11T20:15:30.950000Z",
    )


def _store(tmp_path: Path) -> EvidenceStore:
    return create_store(tmp_path / "evidence")


def _commit_ar(store: EvidenceStore) -> tuple[str, str]:
    attempt = _ar_attempt()
    attempt_id = store.commit_attempt(attempt, request_body=AR_REQUEST_BODY)
    capture_id = store.commit_capture(_ar_capture(attempt), response_body=AR_RESPONSE_BODY)
    return attempt_id, capture_id


# ---------------------------------------------------------------------------
# FORMAT / D7
# ---------------------------------------------------------------------------


def test_create_and_open_enforces_exact_format_bytes_and_digest(tmp_path: Path) -> None:
    root = tmp_path / "evidence"
    create_store(root)
    data = (root / "FORMAT.json").read_bytes()
    assert data == FORMAT_BYTES
    assert not data.endswith(b"\n")
    assert content_digest(data) == FORMAT_DIGEST
    opened = open_store(root)
    assert opened.root == root


def test_d7_open_rejects_missing_format_without_modifying_tmp(tmp_path: Path) -> None:
    root = tmp_path / "not-a-store"
    root.mkdir()
    debris = root / ".tmp"
    debris.mkdir()
    marker = debris / "keep-me"
    marker.write_bytes(b"x")
    with pytest.raises(FormatError):
        open_store(root)
    assert marker.read_bytes() == b"x"


def test_d7_open_rejects_malformed_format_without_purging_tmp(tmp_path: Path) -> None:
    root = tmp_path / "broken"
    root.mkdir()
    (root / "FORMAT.json").write_bytes(b"{not-json")
    tmp = root / ".tmp"
    tmp.mkdir()
    marker = tmp / "keep-me"
    marker.write_bytes(b"x")
    with pytest.raises(FormatError):
        open_store(root)
    assert marker.exists()


def test_d7_open_rejects_noncanonical_format_without_purging_tmp(tmp_path: Path) -> None:
    root = tmp_path / "spaces"
    root.mkdir()
    (root / "FORMAT.json").write_bytes(FORMAT_BYTES + b"\n")
    tmp = root / ".tmp"
    tmp.mkdir()
    marker = tmp / "keep-me"
    marker.write_bytes(b"x")
    with pytest.raises(FormatError):
        open_store(root)
    assert marker.exists()


def test_d7_open_rejects_unsupported_format_without_purging_tmp(tmp_path: Path) -> None:
    root = tmp_path / "unsupported"
    root.mkdir()
    (root / "FORMAT.json").write_bytes(
        FORMAT_BYTES.replace(b'"store_format":2', b'"store_format":1')
    )
    tmp = root / ".tmp"
    tmp.mkdir()
    marker = tmp / "keep-me"
    marker.write_bytes(b"x")
    with pytest.raises(FormatError):
        open_store(root)
    assert marker.exists()


def test_d7_successful_open_purges_tmp_only_after_format_validation(tmp_path: Path) -> None:
    root = tmp_path / "evidence"
    create_store(root)
    debris = root / ".tmp" / "leftover"
    debris.write_bytes(b"stale")
    open_store(root)
    assert not debris.exists()


def test_create_rejects_existing_format(tmp_path: Path) -> None:
    root = tmp_path / "evidence"
    create_store(root)
    with pytest.raises(FormatError):
        create_store(root)


# ---------------------------------------------------------------------------
# D1 exclusive install via link(2)
# ---------------------------------------------------------------------------


def test_d1_exclusive_install_uses_link_not_rename(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden_rename(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("rename(2) must not be used to install")

    monkeypatch.setattr(os, "rename", forbidden_rename)
    store = _store(tmp_path)
    attempt_id = store.commit_attempt(_ar_attempt(), request_body=AR_REQUEST_BODY)
    assert attempt_id == AR_ATTEMPT_ID
    links = [path for op, path in store.recorded_ops if op == "link"]
    assert any(path.endswith("FORMAT.json") for path in links)
    assert any(path.endswith("attempt.json") for path in links)
    assert any(path.endswith("COMMITTED") for path in links)


def test_d1_occupied_final_path_fails_closed(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.commit_attempt(_ar_attempt(), request_body=AR_REQUEST_BODY)
    with pytest.raises(StoreError, match="terminal bundle directory exists"):
        store.commit_attempt(_ar_attempt(), request_body=AR_REQUEST_BODY)


# ---------------------------------------------------------------------------
# D2 / D3 path kinds
# ---------------------------------------------------------------------------


def test_d3_pool_recurrence_accepted_mismatch_fails_closed(tmp_path: Path) -> None:
    store = _store(tmp_path)
    digest = store.install_object(AR_REQUEST_BODY)
    again = store.install_object(AR_REQUEST_BODY)
    assert digest == again
    pool = store.object_path(digest)
    pool.write_bytes(b"tampered-pool-bytes-not-matching-digest")
    with pytest.raises(IntegrityError, match="mismatch"):
        store.install_object(AR_REQUEST_BODY)


def test_d2_shared_directories_recur_terminal_eexist_fails_closed(tmp_path: Path) -> None:
    store = _store(tmp_path)
    first = store.commit_attempt(_ar_attempt(), request_body=AR_REQUEST_BODY)
    second = store.commit_attempt(_alt_attempt(), request_body=AR_REQUEST_BODY)
    first_dir = store.attempt_path(AR_FINGERPRINT, AUTHORIZED_AT, first)
    second_dir = store.attempt_path(AR_FINGERPRINT, AUTHORIZED_AT, second)
    assert first_dir.parent == second_dir.parent
    assert first_dir.parent.is_dir()
    with pytest.raises(StoreError, match="terminal bundle directory exists"):
        store.commit_attempt(_ar_attempt(), request_body=AR_REQUEST_BODY)


# ---------------------------------------------------------------------------
# D4 paths, bodies, COMMITTED last
# ---------------------------------------------------------------------------


def test_ar_paths_follow_format2_and_authorized_at_date(tmp_path: Path) -> None:
    store = _store(tmp_path)
    attempt_id, capture_id = _commit_ar(store)
    assert attempt_id == AR_ATTEMPT_ID
    assert capture_id == AR_CAPTURE_ID
    attempt_dir = store.attempt_path(AR_FINGERPRINT, AUTHORIZED_AT, attempt_id)
    expected_attempt = (
        store.root
        / "attempts"
        / "v1"
        / AR_FINGERPRINT[:2]
        / AR_FINGERPRINT[2:4]
        / AR_FINGERPRINT
        / "2026"
        / "08"
        / "11"
        / AR_ATTEMPT_ID
    )
    assert attempt_dir == expected_attempt
    assert (attempt_dir / "attempt.json").is_file()
    assert (attempt_dir / "request.body").is_file()
    assert (attempt_dir / "COMMITTED").read_bytes() == f"{AR_ATTEMPT_ID}\n".encode()
    assert not (attempt_dir / "response.body").exists()
    capture_dir = store.capture_path(capture_id)
    expected_capture = (
        store.root / "captures" / "v1" / AR_CAPTURE_ID[:2] / AR_CAPTURE_ID[2:4] / AR_CAPTURE_ID
    )
    assert capture_dir == expected_capture
    assert (capture_dir / "capture.json").is_file()
    assert (capture_dir / "response.body").is_file()
    assert not (capture_dir / "request.body").exists()
    assert (capture_dir / "COMMITTED").read_bytes() == f"{AR_CAPTURE_ID}\n".encode()


def test_d4_bundle_bodies_are_independent_copies_with_link_count_1(tmp_path: Path) -> None:
    root = tmp_path / "evidence"
    store = create_store(root)
    store.commit_attempt(_ar_attempt(), request_body=AR_REQUEST_BODY)
    debris = root / ".tmp" / "extra-link"
    bundle_body = store.attempt_path(AR_FINGERPRINT, AUTHORIZED_AT, AR_ATTEMPT_ID) / "request.body"
    pool = store.object_path(content_digest(AR_REQUEST_BODY))
    os.link(bundle_body, debris)
    assert bundle_body.stat().st_nlink == 2
    reopened = open_store(root)
    body = reopened.attempt_path(AR_FINGERPRINT, AUTHORIZED_AT, AR_ATTEMPT_ID) / "request.body"
    assert body.stat().st_nlink == 1
    assert body.stat().st_ino != pool.stat().st_ino
    assert body.read_bytes() == AR_REQUEST_BODY
    assert pool.read_bytes() == AR_REQUEST_BODY


def test_d4_committed_is_installed_last(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.commit_attempt(_ar_attempt(), request_body=AR_REQUEST_BODY)
    links = [path for op, path in store.recorded_ops if op == "link"]
    attempt_links = [
        path for path in links if AR_ATTEMPT_ID in path or path.endswith("request.body")
    ]
    committed = [path for path in attempt_links if path.endswith("COMMITTED")]
    manifest = [path for path in attempt_links if path.endswith("attempt.json")]
    body = [path for path in attempt_links if path.endswith("request.body")]
    assert committed
    assert manifest
    assert body
    assert links.index(manifest[0]) < links.index(committed[0])
    assert links.index(body[0]) < links.index(committed[0])


# ---------------------------------------------------------------------------
# D4a / D5 / D6
# ---------------------------------------------------------------------------


def test_d4a_commit_is_evidence_only_after_verify(tmp_path: Path) -> None:
    store = _store(tmp_path)
    attempt_id = store.commit_attempt(_ar_attempt(), request_body=AR_REQUEST_BODY)
    document = store.read_attempt(attempt_id)
    assert document is not None
    assert document["attempt_nonce"] == AR_NONCE


def test_d6_uncommitted_bundle_is_ignored(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.commit_attempt(_ar_attempt(), request_body=AR_REQUEST_BODY)
    bundle = store.attempt_path(AR_FINGERPRINT, AUTHORIZED_AT, AR_ATTEMPT_ID)
    (bundle / "COMMITTED").unlink()
    assert store.read_attempt(AR_ATTEMPT_ID) is None


def test_d5_verify_after_commit_runs_full_sequence(tmp_path: Path) -> None:
    store = _store(tmp_path)
    attempt_id, capture_id = _commit_ar(store)
    attempt = store.read_attempt(attempt_id)
    capture = store.read_capture(capture_id)
    assert attempt is not None
    assert capture is not None
    manifest = store.attempt_path(AR_FINGERPRINT, AUTHORIZED_AT, attempt_id) / "attempt.json"
    assert content_digest(manifest.read_bytes()) == AR_ATTEMPT_ID
    request_ref = attempt["request"]
    assert isinstance(request_ref, dict)
    body_state = request_ref["body"]
    assert isinstance(body_state, dict)
    ref = body_state["body"]
    assert isinstance(ref, dict)
    assert ref["sha256"] == content_digest(AR_REQUEST_BODY)
    assert ref["bytes"] == len(AR_REQUEST_BODY)
    response = capture["response"]
    assert isinstance(response, dict)
    response_state = response["body"]
    assert isinstance(response_state, dict)
    response_ref = response_state["body"]
    assert isinstance(response_ref, dict)
    assert response_ref["sha256"] == content_digest(AR_RESPONSE_BODY)


def test_d6_committed_but_unreadable_is_integrity_failure(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.commit_attempt(_ar_attempt(), request_body=AR_REQUEST_BODY)
    manifest = store.attempt_path(AR_FINGERPRINT, AUTHORIZED_AT, AR_ATTEMPT_ID) / "attempt.json"
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    with pytest.raises(IntegrityError):
        store.read_attempt(AR_ATTEMPT_ID)


# ---------------------------------------------------------------------------
# Tamper
# ---------------------------------------------------------------------------


def test_tamper_manifest_fails_closed(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.commit_attempt(_ar_attempt(), request_body=AR_REQUEST_BODY)
    path = store.attempt_path(AR_FINGERPRINT, AUTHORIZED_AT, AR_ATTEMPT_ID) / "attempt.json"
    data = bytearray(path.read_bytes())
    data[-1] ^= 0x01
    path.write_bytes(bytes(data))
    with pytest.raises(IntegrityError):
        store.read_attempt(AR_ATTEMPT_ID)


def test_tamper_pool_object_fails_closed(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.commit_attempt(_ar_attempt(), request_body=AR_REQUEST_BODY)
    pool = store.object_path(content_digest(AR_REQUEST_BODY))
    pool.write_bytes(b"x" * len(AR_REQUEST_BODY))
    with pytest.raises(IntegrityError):
        store.read_attempt(AR_ATTEMPT_ID)


def test_tamper_bundle_body_fails_closed(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.commit_attempt(_ar_attempt(), request_body=AR_REQUEST_BODY)
    body = store.attempt_path(AR_FINGERPRINT, AUTHORIZED_AT, AR_ATTEMPT_ID) / "request.body"
    body.write_bytes(b"y" * len(AR_REQUEST_BODY))
    with pytest.raises(IntegrityError):
        store.read_attempt(AR_ATTEMPT_ID)


def test_tamper_request_pool_fails_capture_verify(tmp_path: Path) -> None:
    store = _store(tmp_path)
    _commit_ar(store)
    pool = store.object_path(content_digest(AR_REQUEST_BODY))
    pool.write_bytes(b"q" * len(AR_REQUEST_BODY))
    with pytest.raises(IntegrityError):
        store.read_capture(AR_CAPTURE_ID)


def test_tamper_capture_response_body_fails_closed(tmp_path: Path) -> None:
    store = _store(tmp_path)
    _commit_ar(store)
    body = store.capture_path(AR_CAPTURE_ID) / "response.body"
    body.write_bytes(b"z" * len(AR_RESPONSE_BODY))
    with pytest.raises(IntegrityError):
        store.read_capture(AR_CAPTURE_ID)
