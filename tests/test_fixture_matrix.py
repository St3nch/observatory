"""CE-04 fixture-panel-v1 matrix, transport branches, ≤1 Capture, RP/NR."""

from __future__ import annotations

import json
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
    construct_fixture_transport,
)

# Permitted panel_id / subject_key alphabet from the closed parameter schema.
# This corpus does not enumerate every valid string.
_PERMITTED_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._:-"
_ADMITTED_TOP_LEVEL = {
    "contract",
    "panel_id",
    "result_count",
    "results",
    "status",
    "subject_key",
}
_RESULT_FIELDS = {"label", "result_index", "score", "subject_key"}
_REFUSAL_FAILURE_FIELDS = {"code", "contract", "panel_id", "status", "subject_key"}

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


def _closed(body: bytes) -> dict[str, object]:
    parsed = json.loads(body)
    assert isinstance(parsed, dict)
    return parsed


def _assert_result_item(item: object, index: int, subject_key: str) -> None:
    assert isinstance(item, dict)
    assert set(item) == _RESULT_FIELDS
    assert item["label"] == "fixture-result-" + str(index)
    assert item["result_index"] == index
    assert item["score"] == 1000 - index
    assert item["subject_key"] == subject_key


def _assert_admitted_shape(
    obj: dict[str, object],
    panel_id: str,
    subject_key: str,
    count: int,
    *,
    result_subject: str | None = None,
) -> None:
    assert set(obj) == _ADMITTED_TOP_LEVEL
    assert obj["contract"] == "fixture-panel-v1"
    assert obj["panel_id"] == panel_id
    assert obj["subject_key"] == subject_key
    assert obj["status"] == "ok"
    assert obj["result_count"] == count
    results = obj["results"]
    assert isinstance(results, list)
    assert len(results) == count
    expected_subject = subject_key if result_subject is None else result_subject
    for index, item in enumerate(results, start=1):
        _assert_result_item(item, index, expected_subject)


def _independent_admitted_results_bytes(
    panel_id: str, subject_key: str, depth: int
) -> bytes:
    return canonical_json(
        {
            "contract": "fixture-panel-v1",
            "panel_id": panel_id,
            "result_count": depth,
            "results": [
                {
                    "label": "fixture-result-" + str(index),
                    "result_index": index,
                    "score": 1000 - index,
                    "subject_key": subject_key,
                }
                for index in range(1, depth + 1)
            ],
            "status": "ok",
            "subject_key": subject_key,
        }
    )


def _independent_admitted_empty_bytes(panel_id: str, subject_key: str) -> bytes:
    return canonical_json(
        {
            "contract": "fixture-panel-v1",
            "panel_id": panel_id,
            "result_count": 0,
            "results": [],
            "status": "ok",
            "subject_key": subject_key,
        }
    )


def _independent_refusal_bytes(panel_id: str, subject_key: str) -> bytes:
    return canonical_json(
        {
            "code": "fixture_refusal",
            "contract": "fixture-panel-v1",
            "panel_id": panel_id,
            "status": "refused",
            "subject_key": subject_key,
        }
    )


def _independent_failure_bytes(panel_id: str, subject_key: str) -> bytes:
    return canonical_json(
        {
            "code": "fixture_failure",
            "contract": "fixture-panel-v1",
            "panel_id": panel_id,
            "status": "failed",
            "subject_key": subject_key,
        }
    )


def _alt_subject(subject_key: str) -> str:
    if subject_key == "other-subject":
        return "other-subject-2"
    return "other-subject"


def _assert_normative_body(
    scenario: str,
    body: bytes | None,
    panel_id: str,
    subject_key: str,
    depth: int,
) -> None:
    if scenario == "no_response":
        assert body is None
        return
    assert body is not None
    if scenario == "malformed_response":
        assert body == MALFORMED_BYTES
        return
    if scenario == "response_partial":
        full = _independent_admitted_results_bytes(panel_id, subject_key, depth)
        assert body == full[:32]
        assert len(body) == 32
        return
    if scenario == "wrong_media_type":
        assert body == _independent_admitted_empty_bytes(panel_id, subject_key)
        return
    obj = _closed(body)
    if scenario == "admitted_results":
        _assert_admitted_shape(obj, panel_id, subject_key, depth)
        assert body == _independent_admitted_results_bytes(panel_id, subject_key, depth)
        return
    if scenario == "admitted_empty":
        _assert_admitted_shape(obj, panel_id, subject_key, 0)
        assert body == _independent_admitted_empty_bytes(panel_id, subject_key)
        return
    if scenario == "provider_refusal":
        assert set(obj) == _REFUSAL_FAILURE_FIELDS
        assert obj["code"] == "fixture_refusal"
        assert obj["contract"] == "fixture-panel-v1"
        assert obj["panel_id"] == panel_id
        assert obj["status"] == "refused"
        assert obj["subject_key"] == subject_key
        assert body == _independent_refusal_bytes(panel_id, subject_key)
        return
    if scenario == "provider_failure":
        assert set(obj) == _REFUSAL_FAILURE_FIELDS
        assert obj["code"] == "fixture_failure"
        assert obj["contract"] == "fixture-panel-v1"
        assert obj["panel_id"] == panel_id
        assert obj["status"] == "failed"
        assert obj["subject_key"] == subject_key
        assert body == _independent_failure_bytes(panel_id, subject_key)
        return
    if scenario == "extra_subject":
        _assert_admitted_shape(
            obj, panel_id, subject_key, 1, result_subject=_alt_subject(subject_key)
        )
        return
    if scenario == "too_many_results":
        _assert_admitted_shape(obj, panel_id, subject_key, depth + 1)
        return
    raise AssertionError(f"unhandled scenario {scenario}")


def _parameter_corpus() -> list[tuple[str, str, int]]:
    cases: list[tuple[str, str, int]] = []
    for index, char in enumerate(_PERMITTED_ALPHABET):
        other = _PERMITTED_ALPHABET[(index + 13) % len(_PERMITTED_ALPHABET)]
        cases.append((char, other, 1 + (index % 16)))
    long_panel = (_PERMITTED_ALPHABET * 2)[:128]
    long_subject = (_PERMITTED_ALPHABET[::-1] * 2)[:128]
    cases.append((long_panel, long_subject, 16))
    cases.append((long_panel, "A", 1))
    cases.append(("Z", long_subject, 8))
    cases.append(("Az0._:-", ":-_.0zA", 5))
    cases.append(("panel-mix", "other-subject", 3))
    cases.append(("other-subject", "other-subject", 2))
    cases.append(("panel-alpha", "subject-two", 4))
    cases.append(("panel-beta", "subject-one", 9))
    return cases


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
        _assert_normative_body(
            scenario, result.body, "panel-alpha", "subject-one", depth
        )


def test_normative_admitted_results_fields() -> None:
    result = construct_fixture_transport("panel-alpha", "subject-one", 2, "admitted_results")
    _assert_normative_body(
        "admitted_results", result.body, "panel-alpha", "subject-one", 2
    )


def test_normative_admitted_empty_object() -> None:
    result = construct_fixture_transport("panel-x", "subject-y", 4, "admitted_empty")
    _assert_normative_body("admitted_empty", result.body, "panel-x", "subject-y", 4)


def test_normative_provider_refusal_object() -> None:
    result = construct_fixture_transport("panel-x", "subject-y", 4, "provider_refusal")
    _assert_normative_body("provider_refusal", result.body, "panel-x", "subject-y", 4)


def test_normative_provider_failure_object() -> None:
    result = construct_fixture_transport("panel-x", "subject-y", 4, "provider_failure")
    _assert_normative_body("provider_failure", result.body, "panel-x", "subject-y", 4)


def test_normative_wrong_media_type_empty_bytes_and_plain_header() -> None:
    result = construct_fixture_transport("panel-x", "subject-y", 4, "wrong_media_type")
    assert result.headers == [["content-type", "text/plain"]]
    _assert_normative_body("wrong_media_type", result.body, "panel-x", "subject-y", 4)


def test_normative_response_partial_is_first_32_of_independent_full() -> None:
    result = construct_fixture_transport("panel-x", "subject-y", 4, "response_partial")
    _assert_normative_body("response_partial", result.body, "panel-x", "subject-y", 4)


def test_normative_extra_subject_identity_and_other_subject_branch() -> None:
    ordinary = construct_fixture_transport("p", "subject-one", 2, "extra_subject")
    _assert_normative_body("extra_subject", ordinary.body, "p", "subject-one", 2)
    special = construct_fixture_transport("p", "other-subject", 2, "extra_subject")
    _assert_normative_body("extra_subject", special.body, "p", "other-subject", 2)


def test_normative_too_many_results_is_depth_plus_one() -> None:
    for depth in range(1, 17):
        result = construct_fixture_transport("p", "s", depth, "too_many_results")
        _assert_normative_body("too_many_results", result.body, "p", "s", depth)


@pytest.mark.parametrize(("panel_id", "subject_key", "depth"), _parameter_corpus())
def test_generated_parameter_corpus(panel_id: str, subject_key: str, depth: int) -> None:
    admitted = construct_fixture_transport(
        panel_id, subject_key, depth, "admitted_results"
    )
    _assert_normative_body(
        "admitted_results", admitted.body, panel_id, subject_key, depth
    )
    assert admitted.observation_count == depth
    extra = construct_fixture_transport(panel_id, subject_key, depth, "extra_subject")
    _assert_normative_body("extra_subject", extra.body, panel_id, subject_key, depth)
    too_many = construct_fixture_transport(
        panel_id, subject_key, depth, "too_many_results"
    )
    _assert_normative_body(
        "too_many_results", too_many.body, panel_id, subject_key, depth
    )
    empty = construct_fixture_transport(panel_id, subject_key, depth, "admitted_empty")
    _assert_normative_body("admitted_empty", empty.body, panel_id, subject_key, depth)
    refusal = construct_fixture_transport(
        panel_id, subject_key, depth, "provider_refusal"
    )
    _assert_normative_body("provider_refusal", refusal.body, panel_id, subject_key, depth)
    failure = construct_fixture_transport(
        panel_id, subject_key, depth, "provider_failure"
    )
    _assert_normative_body("provider_failure", failure.body, panel_id, subject_key, depth)
    wrong = construct_fixture_transport(panel_id, subject_key, depth, "wrong_media_type")
    assert wrong.headers == [["content-type", "text/plain"]]
    _assert_normative_body("wrong_media_type", wrong.body, panel_id, subject_key, depth)
    partial = construct_fixture_transport(
        panel_id, subject_key, depth, "response_partial"
    )
    _assert_normative_body("response_partial", partial.body, panel_id, subject_key, depth)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_store_all_scenarios_durable(tmp_path: Path, scenario: str) -> None:
    store = create_store(tmp_path / scenario)
    inputs = _inputs(scenario)
    state, _completeness, failure_code, classification, obs = EXPECTED[scenario]
    outcome = capture_fixture(store, inputs)
    assert outcome.classification == classification
    if obs == -1:
        assert outcome.observation_count == inputs.depth
    else:
        assert outcome.observation_count == obs
    assert store.read_attempt(outcome.attempt_id) is not None
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["transport_state"] == state
    capture_dir = store.capture_path(outcome.capture_id)
    if scenario == "no_response":
        assert capture["response"] is None
        assert capture["transport_failure"] == {
            "code": failure_code,
            "phase": "receive_response",
        }
        assert not (capture_dir / "response.body").exists()
    else:
        stored = (capture_dir / "response.body").read_bytes()
        assert not (capture_dir / "request.body").exists()
        _assert_normative_body(
            scenario, stored, inputs.panel_id, inputs.subject_key, inputs.depth
        )


def test_published_rp_identities_and_partial_body(tmp_path: Path) -> None:
    store = create_store(tmp_path / "rp")
    outcome = capture_fixture(store, PUBLISHED_RP_INPUTS)
    assert outcome.attempt_id == PUBLISHED_RP_ATTEMPT_ID
    assert outcome.capture_id == PUBLISHED_RP_CAPTURE_ID
    body = store.capture_path(outcome.capture_id) / "response.body"
    payload = body.read_bytes()
    assert len(payload) == 32
    assert content_digest(payload) == RP_PARTIAL_DIGEST
    assert payload == b'{"contract":"fixture-panel-v1","'
    full = _independent_admitted_results_bytes("panel-alpha", "subject-one", 2)
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
    _assert_normative_body(
        "extra_subject", body, "panel-alpha", "other-subject", 2
    )
