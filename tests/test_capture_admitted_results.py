"""CE-03B admitted_results tracer: AR vectors, D8 gate, CLI, journal skip."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import pytest

from observatory import capture as capture_mod
from observatory.capture import (
    PUBLISHED_AR_ATTEMPT_ID,
    PUBLISHED_AR_CAPTURE_ID,
    PUBLISHED_AR_INPUTS,
    capture_admitted_results,
    main,
)
from observatory.capture_event import DocumentError, canonical_json, content_digest
from observatory.evidence_store import (
    EvidenceStore,
    IntegrityError,
    StoreError,
    create_store,
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
AR_FINGERPRINT = "d18682cc029a8db08b0b761b900db2c7c91f92a99087597281cbdbdaec70e88b"
AUTHORIZED_AT = "2026-08-11T20:15:30.123456Z"


def _store(tmp_path: Path) -> EvidenceStore:
    return create_store(tmp_path / "evidence")


def test_frozen_ar_inputs_produce_published_ids_on_disk(tmp_path: Path) -> None:
    store = _store(tmp_path)
    outcome = capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    assert outcome.attempt_id == PUBLISHED_AR_ATTEMPT_ID
    assert outcome.capture_id == PUBLISHED_AR_CAPTURE_ID
    assert store.read_attempt(PUBLISHED_AR_ATTEMPT_ID) is not None
    assert store.read_capture(PUBLISHED_AR_CAPTURE_ID) is not None


def test_ar_request_and_response_bodies_match_published_vector(tmp_path: Path) -> None:
    store = _store(tmp_path)
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    attempt_dir = store.attempt_path(AR_FINGERPRINT, AUTHORIZED_AT, PUBLISHED_AR_ATTEMPT_ID)
    capture_dir = store.capture_path(PUBLISHED_AR_CAPTURE_ID)
    request_body = (attempt_dir / "request.body").read_bytes()
    response_body = (capture_dir / "response.body").read_bytes()
    assert request_body == AR_REQUEST_BODY
    assert content_digest(request_body) == content_digest(AR_REQUEST_BODY)
    assert response_body == AR_RESPONSE_BODY
    assert content_digest(response_body) == (
        "40735fbc1cd0f98e140857bec1b1e8c6d6f666baa0fb49bfd0e782aaa6513eac"
    )
    assert canonical_json(
        {
            "contract": "fixture-panel-v1",
            "panel_id": "panel-alpha",
            "result_count": 2,
            "results": [
                {
                    "label": "fixture-result-1",
                    "result_index": 1,
                    "score": 999,
                    "subject_key": "subject-one",
                },
                {
                    "label": "fixture-result-2",
                    "result_index": 2,
                    "score": 998,
                    "subject_key": "subject-one",
                },
            ],
            "status": "ok",
            "subject_key": "subject-one",
        }
    ) == AR_RESPONSE_BODY


def test_d4_body_placement_request_on_attempt_response_on_capture(tmp_path: Path) -> None:
    store = _store(tmp_path)
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    attempt_dir = store.attempt_path(AR_FINGERPRINT, AUTHORIZED_AT, PUBLISHED_AR_ATTEMPT_ID)
    capture_dir = store.capture_path(PUBLISHED_AR_CAPTURE_ID)
    assert (attempt_dir / "request.body").is_file()
    assert not (attempt_dir / "response.body").exists()
    assert (capture_dir / "response.body").is_file()
    assert not (capture_dir / "request.body").exists()


def test_module_issuer_token_bypass_no_longer_works() -> None:
    assert not hasattr(capture_mod, "_ISSUER")
    with pytest.raises(TypeError, match="cannot construct"):
        capture_mod._VerifiedAttempt(
            attempt_id=PUBLISHED_AR_ATTEMPT_ID,
            document={"parameters": {"scenario": "admitted_results", "depth": 2}},
            request_body=AR_REQUEST_BODY,
            _issued_by=object(),
        )
    forged: Any = object.__new__(capture_mod._VerifiedAttempt)
    object.__setattr__(forged, "attempt_id", PUBLISHED_AR_ATTEMPT_ID)
    object.__setattr__(
        forged,
        "document",
        {"parameters": {"scenario": "admitted_results", "depth": 2, "panel_id": "x"}},
    )
    object.__setattr__(forged, "request_body", AR_REQUEST_BODY)
    object.__setattr__(forged, "_panel_id", "panel-alpha")
    object.__setattr__(forged, "_subject_key", "subject-one")
    object.__setattr__(forged, "_depth", 2)
    with pytest.raises(TypeError, match="verified committed Attempt"):
        capture_mod._admitted_results_transport(forged)


def test_transport_rejects_non_capability_and_unissued_instance() -> None:
    with pytest.raises(TypeError):
        capture_mod._admitted_results_transport(object())
    with pytest.raises(TypeError, match="cannot construct"):
        capture_mod._VerifiedAttempt()


def test_copying_genuine_capability_fields_is_not_accepted(tmp_path: Path) -> None:
    store = _store(tmp_path)
    issued: list[object] = []
    real_issue = capture_mod._issue_verified_attempt

    def wrap(
        inner_store: EvidenceStore,
        document: Mapping[str, object],
        request_body: bytes,
    ) -> object:
        capability = real_issue(inner_store, document, request_body)
        issued.append(capability)
        return capability

    capture_mod._issue_verified_attempt = wrap
    try:
        capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    finally:
        capture_mod._issue_verified_attempt = real_issue
    genuine = issued[0]
    copy: Any = object.__new__(capture_mod._VerifiedAttempt)
    for name in (
        "attempt_id",
        "document",
        "request_body",
        "_panel_id",
        "_subject_key",
        "_depth",
    ):
        object.__setattr__(copy, name, getattr(genuine, name))
    with pytest.raises(TypeError, match="verified committed Attempt"):
        capture_mod._admitted_results_transport(copy)


def test_mutating_capability_cannot_change_transport_output(tmp_path: Path) -> None:
    store = _store(tmp_path)
    issued: list[object] = []
    real_issue = capture_mod._issue_verified_attempt

    def wrap(
        inner_store: EvidenceStore,
        document: Mapping[str, object],
        request_body: bytes,
    ) -> object:
        capability = real_issue(inner_store, document, request_body)
        issued.append(capability)
        return capability

    capture_mod._issue_verified_attempt = wrap
    try:
        capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    finally:
        capture_mod._issue_verified_attempt = real_issue
    genuine: Any = issued[0]
    document = genuine.document
    parameters = document["parameters"]
    with pytest.raises(TypeError):
        parameters["depth"] = 16
    result = capture_mod._admitted_results_transport(genuine)
    assert result.body == AR_RESPONSE_BODY
    assert content_digest(result.body) == (
        "40735fbc1cd0f98e140857bec1b1e8c6d6f666baa0fb49bfd0e782aaa6513eac"
    )


def test_public_runner_rejects_pretend_store_before_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class PretendStore:
        def commit_attempt(
            self, document: Mapping[str, object], *, request_body: bytes | None
        ) -> str:
            return "0" * 64

        def read_attempt(self, attempt_id: str) -> dict[str, object]:
            return {
                "parameters": {
                    "contract": "fixture-panel-v1",
                    "depth": 2,
                    "panel_id": "panel-alpha",
                    "scenario": "admitted_results",
                    "subject_key": "subject-one",
                }
            }

        def commit_capture(
            self, document: Mapping[str, object], *, response_body: bytes | None
        ) -> str:
            return "1" * 64

    calls: list[object] = []

    def spy(attempt: object) -> Any:
        calls.append(attempt)
        raise AssertionError("transport must not run")

    monkeypatch.setattr(capture_mod, "_admitted_results_transport", spy)
    with pytest.raises(TypeError, match="concrete EvidenceStore"):
        capture_admitted_results(PretendStore(), PUBLISHED_AR_INPUTS)  # type: ignore[arg-type]
    assert calls == []


def test_public_runner_rejects_lying_evidencestore_subclass_before_transport(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class LyingStore(EvidenceStore):
        def commit_attempt(
            self, document: Mapping[str, object], *, request_body: bytes | None
        ) -> str:
            return "0" * 64

        def read_attempt(self, attempt_id: str) -> dict[str, object]:
            return {
                "parameters": {
                    "contract": "fixture-panel-v1",
                    "depth": 2,
                    "panel_id": "panel-alpha",
                    "scenario": "admitted_results",
                    "subject_key": "subject-one",
                }
            }

        def commit_capture(
            self, document: Mapping[str, object], *, response_body: bytes | None
        ) -> str:
            return "1" * 64

    calls: list[object] = []

    def spy(attempt: object) -> Any:
        calls.append(attempt)
        raise AssertionError("transport must not run")

    monkeypatch.setattr(capture_mod, "_admitted_results_transport", spy)
    with pytest.raises(TypeError, match="concrete EvidenceStore"):
        capture_admitted_results(LyingStore(tmp_path / "lie"), PUBLISHED_AR_INPUTS)
    assert calls == []


def test_attempt_commit_failure_prevents_transport(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = _store(tmp_path)
    calls: list[object] = []

    def spy(attempt: object) -> Any:
        calls.append(attempt)
        return capture_mod._admitted_results_transport(attempt)

    def fail_commit(*_args: object, **_kwargs: object) -> str:
        raise StoreError("attempt commit failed")

    monkeypatch.setattr(store, "commit_attempt", fail_commit)
    monkeypatch.setattr(capture_mod, "_admitted_results_transport", spy)
    with pytest.raises(StoreError, match="attempt commit failed"):
        capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    assert calls == []


def test_post_committed_verify_failure_prevents_transport(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = _store(tmp_path)
    calls: list[object] = []

    def spy(attempt: object) -> capture_mod.FixtureTransportResult:
        calls.append(attempt)
        raise AssertionError("transport must not run")

    from observatory import evidence_store as store_mod
    from observatory.capture_event import validate_attempt

    calls_validate = {"n": 0}

    def fail_after_commit(value: object) -> dict[str, object]:
        calls_validate["n"] += 1
        if calls_validate["n"] >= 2:
            raise DocumentError("forced post-COMMITTED verify failure")
        return validate_attempt(value)

    monkeypatch.setattr(store_mod, "validate_attempt", fail_after_commit)
    monkeypatch.setattr(capture_mod, "_admitted_results_transport", spy)
    with pytest.raises(IntegrityError):
        capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    assert calls == []


def test_only_issued_capability_reaches_transport_from_runner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = _store(tmp_path)
    seen: list[object] = []
    real_transport = capture_mod._admitted_results_transport

    def spy(attempt: object) -> Any:
        seen.append(attempt)
        assert type(attempt) is capture_mod._VerifiedAttempt
        return real_transport(attempt)

    monkeypatch.setattr(capture_mod, "_admitted_results_transport", spy)
    outcome = capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    assert outcome.attempt_id == PUBLISHED_AR_ATTEMPT_ID
    assert len(seen) == 1
    assert capture_mod._admitted_results_transport is spy
    # The runner is the only production call path; a second transport on the
    # issued object is allowed (same capability) but forgeries are not.
    assert real_transport(seen[0]).body == AR_RESPONSE_BODY


def test_journal_is_not_written(tmp_path: Path) -> None:
    store = _store(tmp_path)
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    journal = store.root / "journal"
    assert not journal.exists()


def test_cli_prints_both_full_ids(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "evidence"
    assert main(["--evidence-root", str(root)]) == 0
    out = capsys.readouterr().out
    assert f"attempt_id {PUBLISHED_AR_ATTEMPT_ID}\n" in out
    assert f"capture_id {PUBLISHED_AR_CAPTURE_ID}\n" in out
    from observatory.evidence_store import open_store

    opened = open_store(root)
    assert opened.read_attempt(PUBLISHED_AR_ATTEMPT_ID) is not None
    assert opened.read_capture(PUBLISHED_AR_CAPTURE_ID) is not None


def test_cli_module_entrypoint_prints_ids(tmp_path: Path) -> None:
    root = tmp_path / "evidence"
    repo = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "observatory.capture", "--evidence-root", str(root)],
        check=False,
        capture_output=True,
        text=True,
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(repo / "src")},
    )
    assert result.returncode == 0, result.stderr
    assert f"attempt_id {PUBLISHED_AR_ATTEMPT_ID}" in result.stdout
    assert f"capture_id {PUBLISHED_AR_CAPTURE_ID}" in result.stdout


def test_cli_does_not_derive_or_touch_postgresql(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    imported: list[str] = []
    real_import = __import__

    def guard(
        name: str,
        globals: Mapping[str, object] | None = None,
        locals: Mapping[str, object] | None = None,
        fromlist: Sequence[str] = (),
        level: int = 0,
    ) -> object:
        imported.append(name)
        if name.startswith(("psycopg", "sqlalchemy", "observatory.derive")):
            raise AssertionError(f"CLI imported excluded module {name}")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", guard)
    assert main(["--evidence-root", str(tmp_path / "evidence")]) == 0
    assert not any(name.startswith("observatory.derive") for name in imported)
    assert not (tmp_path / "evidence" / "derived").exists()


def test_committed_ar_events_pass_verify_on_read(tmp_path: Path) -> None:
    store = _store(tmp_path)
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    attempt = store.read_attempt(PUBLISHED_AR_ATTEMPT_ID)
    capture = store.read_capture(PUBLISHED_AR_CAPTURE_ID)
    assert attempt is not None
    assert capture is not None
    assert capture["attempt_id"] == PUBLISHED_AR_ATTEMPT_ID


def test_bit_flip_of_committed_ar_evidence_fails_closed(tmp_path: Path) -> None:
    store = _store(tmp_path)
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    attempt_manifest = (
        store.attempt_path(AR_FINGERPRINT, AUTHORIZED_AT, PUBLISHED_AR_ATTEMPT_ID)
        / "attempt.json"
    )
    data = bytearray(attempt_manifest.read_bytes())
    data[0] ^= 0x01
    attempt_manifest.write_bytes(bytes(data))
    with pytest.raises(IntegrityError):
        store.read_attempt(PUBLISHED_AR_ATTEMPT_ID)
    capture_manifest = store.capture_path(PUBLISHED_AR_CAPTURE_ID) / "capture.json"
    capture_bytes = bytearray(capture_manifest.read_bytes())
    capture_bytes[-2] ^= 0x01
    capture_manifest.write_bytes(bytes(capture_bytes))
    with pytest.raises(IntegrityError):
        store.read_capture(PUBLISHED_AR_CAPTURE_ID)
