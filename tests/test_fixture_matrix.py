"""CE-04 fixture-panel-v1 matrix, transport branches, ≤1 Capture, RP/NR."""

from __future__ import annotations

import secrets
from pathlib import Path
from typing import Any

import pytest

from observatory.capture import (
    PUBLISHED_AR_ATTEMPT_ID,
    PUBLISHED_AR_CAPTURE_ID,
    PUBLISHED_AR_INPUTS,
    PUBLISHED_NR_ATTEMPT_ID,
    PUBLISHED_NR_CAPTURE_ID,
    PUBLISHED_NR_INPUTS,
    PUBLISHED_RP_ATTEMPT_ID,
    PUBLISHED_RP_CAPTURE_ID,
    PUBLISHED_RP_INPUTS,
    FixtureCaptureInputs,
    capture_admitted_results,
    capture_fixture,
    main,
)
from observatory.capture_event import (
    attempt_document,
    body_ref,
    canonical_json,
    capture_document,
    content_digest,
)
from observatory.evidence_store import IntegrityError, StoreError, create_store
from observatory.fixture_algorithm import (
    MALFORMED_BYTES,
    SCENARIOS,
    admitted_empty_body,
    admitted_results_body,
    alt_subject_key,
    construct_fixture_transport,
    extra_subject_body,
    too_many_results_body,
)

SHARED_TIMES = {
    "authorized_at": "2026-08-11T20:15:30.123456Z",
    "observatory_version": "conformance-v1",
    "request_started_at": "2026-08-11T20:15:30.200000Z",
    "transport_ended_at": "2026-08-11T20:15:31.000000Z",
}
HEADERS_AT = "2026-08-11T20:15:30.900000Z"
BODY_ENDED_AT = "2026-08-11T20:15:30.950000Z"
RP_PARTIAL_DIGEST = "02e3821de6b9055e97976f31da2896fd48f513e011459a84841665990fed04df"

EXPECTED: dict[str, tuple[str, str | None, str | None, str, int]] = {
    # scenario: state, completeness, failure-code, classification, obs
    "admitted_results": ("response_complete", "complete", None, "observation_admitted", -1),
    "admitted_empty": ("response_complete", "complete", None, "observation_admitted_empty", 0),
    "provider_refusal": ("response_complete", "complete", None, "provider_refusal", 0),
    "provider_failure": ("response_complete", "complete", None, "provider_failure", 0),
    "malformed_response": (
        "response_complete",
        "complete",
        None,
        "transport_complete_non_admissible",
        0,
    ),
    "wrong_media_type": (
        "response_complete",
        "complete",
        None,
        "transport_complete_non_admissible",
        0,
    ),
    "response_partial": ("response_partial", "partial", None, "response_partial", 0),
    "no_response": ("no_response", None, "fixture_no_response", "no_response", 0),
    "extra_subject": ("response_complete", "complete", None, "admission_rejected", 0),
    "too_many_results": ("response_complete", "complete", None, "admission_rejected", 0),
}


def _inputs(
    scenario: str,
    *,
    panel: str = "panel-alpha",
    subject: str = "subject-one",
    depth: int = 2,
) -> FixtureCaptureInputs:
    no_response = scenario == "no_response"
    return FixtureCaptureInputs(
        scenario=scenario,
        panel_id=panel,
        subject_key=subject,
        depth=depth,
        attempt_nonce=secrets.token_hex(32),
        response_headers_at=None if no_response else HEADERS_AT,
        response_body_ended_at=None if no_response else BODY_ENDED_AT,
        **SHARED_TIMES,
    )


def test_malformed_bytes_are_exactly_45_and_have_no_trailing_newline() -> None:
    assert len(MALFORMED_BYTES) == 45
    assert not MALFORMED_BYTES.endswith(b"\n")
    assert MALFORMED_BYTES == b'{"contract":"fixture-panel-v1","status":"ok",'


@pytest.mark.parametrize("scenario", SCENARIOS)
@pytest.mark.parametrize("depth", list(range(1, 17)))
def test_algorithm_all_scenarios_all_depths(scenario: str, depth: int) -> None:
    result = construct_fixture_transport("panel-alpha", "subject-one", depth, scenario)
    state, completeness, failure_code, classification, obs = EXPECTED[scenario]
    assert result.transport_state == state
    assert result.completeness == completeness
    assert result.classification == classification
    if obs == -1:
        assert result.observation_count == depth
    else:
        assert result.observation_count == obs
    if failure_code is None:
        assert result.transport_failure is None
    else:
        assert result.transport_failure == {
            "code": failure_code,
            "phase": "receive_response",
        }
    if scenario == "no_response":
        assert result.body is None
        assert result.headers is None
    else:
        assert result.body is not None
        assert result.headers is not None
        if scenario == "wrong_media_type":
            assert result.headers == [["content-type", "text/plain"]]
        else:
            assert result.headers == [["content-type", "application/json"]]
        if scenario == "response_partial":
            full = canonical_json(admitted_results_body("panel-alpha", "subject-one", depth))
            assert result.body == full[:32]
            assert len(result.body) == 32
        if scenario == "malformed_response":
            assert result.body == MALFORMED_BYTES
        if scenario == "wrong_media_type":
            assert result.body == canonical_json(
                admitted_empty_body("panel-alpha", "subject-one")
            )
        if scenario == "too_many_results":
            assert result.body == canonical_json(
                too_many_results_body("panel-alpha", "subject-one", depth)
            )


def test_wrong_media_type_body_matches_admitted_empty() -> None:
    empty = construct_fixture_transport("p", "s", 3, "admitted_empty")
    wrong = construct_fixture_transport("p", "s", 3, "wrong_media_type")
    assert empty.body == wrong.body
    assert wrong.headers == [["content-type", "text/plain"]]
    assert empty.headers == [["content-type", "application/json"]]


def test_extra_subject_alt_key_and_other_subject_branch() -> None:
    assert alt_subject_key("subject-one") == "other-subject"
    assert alt_subject_key("other-subject") == "other-subject-2"
    ordinary = extra_subject_body("p", "subject-one")
    results = ordinary["results"]
    assert isinstance(results, list)
    first = results[0]
    assert isinstance(first, dict)
    assert first["subject_key"] == "other-subject"
    special = extra_subject_body("p", "other-subject")
    special_results = special["results"]
    assert isinstance(special_results, list)
    special_first = special_results[0]
    assert isinstance(special_first, dict)
    assert special_first["subject_key"] == "other-subject-2"
    built = construct_fixture_transport("p", "other-subject", 2, "extra_subject")
    assert built.body == canonical_json(special)


@pytest.mark.parametrize(
    "token",
    ["A", "z", "0", ".", "_", ":", "-", "Az0._:-", "A" * 128],
)
def test_algorithm_panel_and_subject_tokens(token: str) -> None:
    result = construct_fixture_transport(token, token, 1, "admitted_results")
    assert result.classification == "observation_admitted"
    assert result.observation_count == 1
    body = admitted_results_body(token, token, 1)
    assert result.body == canonical_json(body)


def test_algorithm_min_length_tokens() -> None:
    result = construct_fixture_transport("A", "B", 1, "admitted_empty")
    assert result.body == canonical_json(admitted_empty_body("A", "B"))


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_store_all_scenarios_durable(tmp_path: Path, scenario: str) -> None:
    store = create_store(tmp_path / scenario)
    inputs = _inputs(scenario)
    expected = construct_fixture_transport(
        inputs.panel_id, inputs.subject_key, inputs.depth, scenario
    )
    outcome = capture_fixture(store, inputs)
    assert outcome.classification == expected.classification
    assert outcome.observation_count == expected.observation_count
    assert store.read_attempt(outcome.attempt_id) is not None
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["transport_state"] == expected.transport_state
    capture_dir = store.capture_path(outcome.capture_id)
    if scenario == "no_response":
        assert capture["response"] is None
        assert capture["transport_failure"] == {
            "code": "fixture_no_response",
            "phase": "receive_response",
        }
        assert not (capture_dir / "response.body").exists()
    else:
        assert (capture_dir / "response.body").is_file()
        assert not (capture_dir / "request.body").exists()
        assert (capture_dir / "response.body").read_bytes() == expected.body


def test_published_rp_identities_and_partial_body(tmp_path: Path) -> None:
    store = create_store(tmp_path / "rp")
    outcome = capture_fixture(store, PUBLISHED_RP_INPUTS)
    assert outcome.attempt_id == PUBLISHED_RP_ATTEMPT_ID
    assert outcome.capture_id == PUBLISHED_RP_CAPTURE_ID
    body = store.capture_path(outcome.capture_id) / "response.body"
    payload = body.read_bytes()
    assert len(payload) == 32
    assert content_digest(payload) == RP_PARTIAL_DIGEST
    full = canonical_json(admitted_results_body("panel-alpha", "subject-one", 2))
    assert payload == full[:32]
    assert not (store.capture_path(outcome.capture_id) / "request.body").exists()


def test_published_nr_identities_and_no_response_body(tmp_path: Path) -> None:
    store = create_store(tmp_path / "nr")
    outcome = capture_fixture(store, PUBLISHED_NR_INPUTS)
    assert outcome.attempt_id == PUBLISHED_NR_ATTEMPT_ID
    assert outcome.capture_id == PUBLISHED_NR_CAPTURE_ID
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["response"] is None
    assert not (store.capture_path(outcome.capture_id) / "response.body").exists()


def test_ar_entrypoint_still_matches_published_ids(tmp_path: Path) -> None:
    store = create_store(tmp_path / "ar")
    outcome = capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    assert outcome.attempt_id == PUBLISHED_AR_ATTEMPT_ID
    assert outcome.capture_id == PUBLISHED_AR_CAPTURE_ID
    assert outcome.classification == "observation_admitted"
    assert outcome.observation_count == 2


def test_second_capture_for_same_attempt_rejected(tmp_path: Path) -> None:
    store = create_store(tmp_path / "uniq")
    first = capture_fixture(store, _inputs("admitted_results"))
    parent = store.read_attempt(first.attempt_id)
    assert parent is not None
    response = (store.capture_path(first.capture_id) / "response.body").read_bytes()
    second = capture_document(
        attempt=parent,
        request_started_at=SHARED_TIMES["request_started_at"],
        transport_ended_at=SHARED_TIMES["transport_ended_at"],
        transport_state="response_complete",
        response={
            "headers": [["content-type", "application/json"]],
            "body": {"state": "present_nonempty", "body": body_ref(response)},
            "completeness": "complete",
        },
        transport_failure=None,
        response_headers_at=HEADERS_AT,
        response_body_ended_at="2026-08-11T20:15:30.951000Z",
    )
    assert content_digest(canonical_json(second)) != first.capture_id
    with pytest.raises(StoreError, match="already has committed Capture"):
        store.commit_capture(second, response_body=response)
    assert store.read_capture(first.capture_id) is not None


def test_uncommitted_capture_residue_is_ignored_by_uniqueness(tmp_path: Path) -> None:
    store = create_store(tmp_path / "residue")
    attempt = attempt_document(
        parameters={
            "contract": "fixture-panel-v1",
            "depth": 2,
            "panel_id": "panel-alpha",
            "scenario": "admitted_results",
            "subject_key": "subject-one",
        },
        attempt_nonce=secrets.token_hex(32),
        authorized_at=SHARED_TIMES["authorized_at"],
        observatory_version="conformance-v1",
    )
    request_body = canonical_json(attempt["parameters"])
    attempt_id = store.commit_attempt(attempt, request_body=request_body)
    fake_id = "a" * 64
    residue = store.capture_path(fake_id)
    residue.mkdir(parents=True)
    (residue / "capture.json").write_bytes(b"{}")
    parent = store.read_attempt(attempt_id)
    assert parent is not None
    expected = construct_fixture_transport("panel-alpha", "subject-one", 2, "admitted_results")
    assert expected.body is not None
    capture = capture_document(
        attempt=parent,
        request_started_at=SHARED_TIMES["request_started_at"],
        transport_ended_at=SHARED_TIMES["transport_ended_at"],
        transport_state="response_complete",
        response={
            "headers": [["content-type", "application/json"]],
            "body": {"state": "present_nonempty", "body": body_ref(expected.body)},
            "completeness": "complete",
        },
        transport_failure=None,
        response_headers_at=HEADERS_AT,
        response_body_ended_at=BODY_ENDED_AT,
    )
    capture_id = store.commit_capture(capture, response_body=expected.body)
    assert store.read_capture(capture_id) is not None
    assert store.read_capture(fake_id) is None


def test_corrupt_committed_capture_during_uniqueness_is_integrity_failure(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path / "corrupt")
    first = capture_fixture(store, _inputs("admitted_results"))
    manifest = store.capture_path(first.capture_id) / "capture.json"
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    parent = store.read_attempt(first.attempt_id)
    assert parent is not None
    response = store.object_path(
        content_digest(
            construct_fixture_transport(
                "panel-alpha", "subject-one", 2, "admitted_results"
            ).body
            or b""
        )
    )
    body = response.read_bytes()
    second = capture_document(
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
        response_body_ended_at="2026-08-11T20:15:30.951000Z",
    )
    with pytest.raises(IntegrityError):
        store.commit_capture(second, response_body=body)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_attempt_before_transport_every_scenario(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, scenario: str
) -> None:
    from observatory import capture as capture_mod

    store = create_store(tmp_path / f"d8-{scenario}")
    calls: list[object] = []

    def spy(attempt: object) -> Any:
        calls.append(attempt)
        raise AssertionError("transport must not run")

    def fail_commit(*_args: object, **_kwargs: object) -> str:
        raise StoreError("attempt commit failed")

    monkeypatch.setattr(store, "commit_attempt", fail_commit)
    monkeypatch.setattr(capture_mod, "_admitted_results_transport", spy)
    with pytest.raises(StoreError, match="attempt commit failed"):
        capture_fixture(store, _inputs(scenario))
    assert calls == []


def test_cli_vector_rp(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "cli-rp"
    assert main(["--evidence-root", str(root), "--vector", "RP"]) == 0
    out = capsys.readouterr().out
    assert f"attempt_id {PUBLISHED_RP_ATTEMPT_ID}\n" in out
    assert f"capture_id {PUBLISHED_RP_CAPTURE_ID}\n" in out
    assert "classification response_partial\n" in out


def test_cli_scenario_covers_matrix(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "cli-sc"
    assert main(["--evidence-root", str(root), "--scenario", "provider_refusal"]) == 0
    out = capsys.readouterr().out
    assert "classification provider_refusal\n" in out
    assert "observation_count 0\n" in out
    assert "attempt_id " in out
    assert "capture_id " in out


def test_store_extra_subject_other_subject_key(tmp_path: Path) -> None:
    store = create_store(tmp_path / "other")
    outcome = capture_fixture(
        store,
        _inputs("extra_subject", subject="other-subject"),
    )
    assert outcome.classification == "admission_rejected"
    body = (store.capture_path(outcome.capture_id) / "response.body").read_bytes()
    assert body == canonical_json(extra_subject_body("panel-alpha", "other-subject"))
