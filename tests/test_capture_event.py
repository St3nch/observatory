"""In-memory Capture Event identity: JCS, closed schemas, content IDs."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest

from observatory.capture_event import (
    EMPTY_BODY_SHA256,
    DocumentError,
    attempt_document,
    body_ref,
    canonical_json,
    capture_document,
    content_digest,
    fingerprint_document,
    fixture_request,
    validate_attempt,
    validate_capture,
    validate_fingerprint,
    validate_fixture_request,
    validate_parameters,
)

# ---------------------------------------------------------------------------
# Published conformance vectors (docs/specs/capture-event-v2.md §Conformance)
# ---------------------------------------------------------------------------

AR_REQUEST_BODY = (
    b'{"contract":"fixture-panel-v1","depth":2,"panel_id":"panel-alpha",'
    b'"scenario":"admitted_results","subject_key":"subject-one"}'
)
AR_REQUEST_BODY_SHA256 = "f16972cae6bea7a84acc0c6d0b181a2de3fabf7870663b1fb76f389aed4c38ec"
AR_FINGERPRINT = "d18682cc029a8db08b0b761b900db2c7c91f92a99087597281cbdbdaec70e88b"
AR_ATTEMPT_ID = "46d5fb97c109b9f64a42ff3a5e62978e2c25551d6b7274603fc88456acfd9a0f"
AR_RESPONSE_BODY = (
    b'{"contract":"fixture-panel-v1","panel_id":"panel-alpha","result_count":2,'
    b'"results":[{"label":"fixture-result-1","result_index":1,"score":999,'
    b'"subject_key":"subject-one"},{"label":"fixture-result-2","result_index":2,'
    b'"score":998,"subject_key":"subject-one"}],"status":"ok",'
    b'"subject_key":"subject-one"}'
)
AR_RESPONSE_BODY_SHA256 = "40735fbc1cd0f98e140857bec1b1e8c6d6f666baa0fb49bfd0e782aaa6513eac"
AR_CAPTURE_ID = "604663f0e7842f1e076189652667357083d4c4a5e56a44d67ea4596ef624ad44"
AR_NONCE = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

RP_REQUEST_BODY = (
    b'{"contract":"fixture-panel-v1","depth":2,"panel_id":"panel-alpha",'
    b'"scenario":"response_partial","subject_key":"subject-one"}'
)
RP_REQUEST_BODY_SHA256 = "96681c6e071e21092d930892b95218d2f84df814ee47034de23715b5fa6dac01"
RP_FINGERPRINT = "decf4fda3e0dafde1ddd1857b74c86603453c056c3a151cb882099f29b2291ce"
RP_ATTEMPT_ID = "2af733226ee72e74ee0a1d5196353d74df816faf0a7801f634fb1a0d0d6784e0"
RP_RESPONSE_BODY = bytes.fromhex(
    "7b22636f6e7472616374223a22666978747572652d70616e656c2d7631222c22"
)
RP_RESPONSE_BODY_SHA256 = "02e3821de6b9055e97976f31da2896fd48f513e011459a84841665990fed04df"
RP_CAPTURE_ID = "f1d0ba4aaba85458c6e9aae540d6baf30ba958ebe7104d59c13e65107a6f677b"
RP_NONCE = "1123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

NR_REQUEST_BODY = (
    b'{"contract":"fixture-panel-v1","depth":2,"panel_id":"panel-alpha",'
    b'"scenario":"no_response","subject_key":"subject-one"}'
)
NR_REQUEST_BODY_SHA256 = "62ac69e163508f05477523a344d9bf491225aa241a9969cf4138372f73808105"
NR_FINGERPRINT = "54a73fea1fa17796ac1e3b5a97d16687f506a43a9d861380cd2c9b311f75aaa6"
NR_ATTEMPT_ID = "8d94de30e27141dc315bc747afdc8f4ea5877709279a6383c738d6dade855ca2"
NR_CAPTURE_ID = "b7cde7e1f921598fd7daf1ac7f7fe16a964832a58adb3cf5b6e47ed017e02134"
NR_NONCE = "2123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

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
RP_PARAMETERS: dict[str, Any] = {
    "contract": "fixture-panel-v1",
    "depth": 2,
    "panel_id": "panel-alpha",
    "scenario": "response_partial",
    "subject_key": "subject-one",
}
NR_PARAMETERS: dict[str, Any] = {
    "contract": "fixture-panel-v1",
    "depth": 2,
    "panel_id": "panel-alpha",
    "scenario": "no_response",
    "subject_key": "subject-one",
}

# FORMAT.json is out of scope as a store document; the published JCS string is
# still a useful encoder golden (key sort + integer + digest).
FORMAT_JSON = (
    b'{"attempt_bundle_layout":"v1","body_addressing":"sha256-content",'
    b'"bundle_body_materialization":"fixed-names-v1","canonical_json":"rfc8785-jcs",'
    b'"capture_bundle_layout":"v1","committed_marker":"event-id-newline",'
    b'"durability_profile":"local-posix-fsync-v1",'
    b'"event_id_encoding":"lowercase-hex-sha256","hash_algorithm":"sha256",'
    b'"path_sharding":"sha256-aa-bb","schema":"observatory.evidence-store-format",'
    b'"store_format":2,"timestamp_encoding":"utc-six-fractional-digits-z"}'
)
FORMAT_JSON_SHA256 = "67fb338d3237a22a29f50110c705e552cd9af29f830c1bfffa9ee1cafa876c7e"


def _ar_attempt() -> dict[str, Any]:
    return attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )


def _ar_capture() -> dict[str, Any]:
    return capture_document(
        attempt=_ar_attempt(),
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


def _nr_capture() -> dict[str, Any]:
    attempt = attempt_document(
        parameters=NR_PARAMETERS,
        attempt_nonce=NR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    return capture_document(
        attempt=attempt,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="no_response",
        response=None,
        transport_failure={"code": "fixture_no_response", "phase": "receive_response"},
        response_headers_at=None,
        response_body_ended_at=None,
    )


# ===========================================================================
# JCS and content digest
# ===========================================================================


def test_canonical_json_has_no_whitespace_or_trailing_newline() -> None:
    encoded = canonical_json({"b": 1, "a": True})

    assert encoded == b'{"a":true,"b":1}'
    assert not encoded.endswith(b"\n")


def test_canonical_json_sorts_keys_by_utf16_code_units() -> None:
    # U+1F600 sorts before U+E000 in UTF-16 (surrogate lead D83D < E000)
    # and after U+E000 in Unicode code-point order.
    encoded = canonical_json({"\ue000": 1, "\U0001f600": 2, "a": 3})

    assert encoded == '{"a":3,"\U0001f600":2,"\ue000":1}'.encode()


def test_canonical_json_rejects_floats() -> None:
    with pytest.raises(DocumentError):
        canonical_json({"n": 1.0})


def test_canonical_json_rejects_bool_as_integer_lookalike_in_array() -> None:
    encoded = canonical_json([True, False, None, 0])

    assert encoded == b"[true,false,null,0]"


def test_canonical_json_string_matches_rfc8785_section_3_2_2_example() -> None:
    """RFC 8785 §3.2.2 string member; expected bytes from §3.2.4 hex dump."""

    # Transcribed from RFC 8785 §3.2.2: "\u20ac$\u000F\u000aA'\u0042\u0022\u005c\\\"\/"
    parsed = json.loads('"\\u20ac$\\u000F\\u000aA\'\\u0042\\u0022\\u005c\\\\\\"\\/"')
    # String token hex from RFC 8785 §3.2.4:
    # 22 e2 82 ac 24 5c 75 30 30 30 66 5c 6e 41 27 42 5c 22 5c 5c 5c 5c 5c 22 2f 22
    expected = bytes.fromhex("22e282ac245c75303030665c6e4127425c225c5c5c5c5c222f22")

    assert parsed == '€$\x0f\nA\'B"\\\\"/'
    assert canonical_json(parsed) == expected


def test_canonical_json_emits_bmp_and_astral_characters_literally() -> None:
    assert canonical_json("ö") == '"ö"'.encode()
    assert canonical_json("\U0001f600") == '"\U0001f600"'.encode()
    assert b"\\u" not in canonical_json("ö")
    assert b"\\u" not in canonical_json("\U0001f600")


def test_canonical_json_does_not_escape_u2028_or_u2029() -> None:
    encoded = canonical_json("\u2028\u2029")

    assert encoded == '"\u2028\u2029"'.encode()
    assert b"\\u2028" not in encoded
    assert b"\\u2029" not in encoded


def test_canonical_json_uses_rfc8785_short_form_control_escapes() -> None:
    assert canonical_json("\b\t\n\f\r") == b'"\\b\\t\\n\\f\\r"'


def test_canonical_json_uses_lowercase_u_escapes_for_other_controls() -> None:
    assert canonical_json("\u0000\u0001\u000e\u001f") == b'"\\u0000\\u0001\\u000e\\u001f"'


def test_canonical_json_does_not_escape_forward_slash() -> None:
    assert canonical_json("/") == b'"/"'
    assert canonical_json("http://x") == b'"http://x"'


def test_canonical_json_rejects_lone_surrogates_as_document_error() -> None:
    with pytest.raises(DocumentError):
        canonical_json("\ud800")
    with pytest.raises(DocumentError):
        canonical_json("\udead")
    with pytest.raises(DocumentError):
        canonical_json({"\ud800": 1})


def test_content_digest_is_lowercase_sha256_of_exact_bytes() -> None:
    data = b"abc"

    assert content_digest(data) == hashlib.sha256(data).hexdigest()
    assert (
        content_digest(data)
        == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )


def test_empty_body_digest_matches_published_vector() -> None:
    assert content_digest(b"") == EMPTY_BODY_SHA256
    assert EMPTY_BODY_SHA256 == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_canonical_json_matches_published_format_object_bytes() -> None:
    value = json.loads(FORMAT_JSON)

    assert canonical_json(value) == FORMAT_JSON
    assert content_digest(canonical_json(value)) == FORMAT_JSON_SHA256


# ===========================================================================
# Closed schemas — body, parameters, request
# ===========================================================================


def test_body_ref_digest_and_size_match_bytes() -> None:
    ref = body_ref(AR_REQUEST_BODY)

    assert ref == {"bytes": 124, "sha256": AR_REQUEST_BODY_SHA256}


def test_body_ref_empty_bytes_uses_published_empty_digest() -> None:
    ref = body_ref(b"")

    assert ref == {"bytes": 0, "sha256": EMPTY_BODY_SHA256}


def test_parameters_accepts_closed_fixture_document() -> None:
    assert validate_parameters(AR_PARAMETERS) == AR_PARAMETERS


def test_parameters_rejects_unknown_property() -> None:
    with pytest.raises(DocumentError):
        validate_parameters({**AR_PARAMETERS, "extra": "nope"})


def test_parameters_rejects_unknown_scenario() -> None:
    with pytest.raises(DocumentError):
        validate_parameters({**AR_PARAMETERS, "scenario": "not-a-scenario"})


def test_parameters_rejects_depth_out_of_range() -> None:
    with pytest.raises(DocumentError):
        validate_parameters({**AR_PARAMETERS, "depth": 0})
    with pytest.raises(DocumentError):
        validate_parameters({**AR_PARAMETERS, "depth": 17})


def test_parameters_rejects_bool_where_integer_required() -> None:
    with pytest.raises(DocumentError):
        validate_parameters({**AR_PARAMETERS, "depth": True})


def test_parameters_rejects_invalid_panel_id() -> None:
    with pytest.raises(DocumentError):
        validate_parameters({**AR_PARAMETERS, "panel_id": "has space"})


def test_body_ref_rejects_unknown_property() -> None:
    request = fixture_request(body=AR_REQUEST_BODY)
    body_state = request["body"]
    assert isinstance(body_state, dict)
    ref = body_state["body"]
    assert isinstance(ref, dict)

    with pytest.raises(DocumentError):
        validate_fixture_request(
            {**request, "body": {**body_state, "body": {**ref, "representation": "raw"}}}
        )


def test_request_rejects_unknown_top_level_property() -> None:
    request = fixture_request(body=AR_REQUEST_BODY)
    with pytest.raises(DocumentError):
        validate_fixture_request({**request, "timeout_ms": 1})


def test_policy_rejects_unknown_property() -> None:
    document = _ar_attempt()
    policy = document["policy"]
    assert isinstance(policy, dict)
    with pytest.raises(DocumentError):
        validate_attempt({**document, "policy": {**policy, "spend_limit": 0}})


def test_software_rejects_unknown_property() -> None:
    document = _ar_attempt()
    software = document["software"]
    assert isinstance(software, dict)
    with pytest.raises(DocumentError):
        validate_attempt({**document, "software": {**software, "git_sha": "deadbeef"}})


def test_transport_failure_rejects_unknown_property() -> None:
    document = _nr_capture()
    failure = document["transport_failure"]
    assert isinstance(failure, dict)
    with pytest.raises(DocumentError):
        validate_capture({**document, "transport_failure": {**failure, "message": "nope"}})


def test_capture_rejects_unknown_top_level_property() -> None:
    document = _ar_capture()
    with pytest.raises(DocumentError):
        validate_capture({**document, "elapsed_ms": 1})


def test_request_rejects_unknown_property_at_nested_body() -> None:
    request = fixture_request(body=AR_REQUEST_BODY)
    nested = request["body"]
    assert isinstance(nested, dict)
    nested = {**nested, "representation": "raw"}

    with pytest.raises(DocumentError):
        validate_fixture_request({**request, "body": nested})


def test_request_rejects_non_fixture_constants() -> None:
    request = fixture_request(body=AR_REQUEST_BODY)

    with pytest.raises(DocumentError):
        validate_fixture_request({**request, "method": "GET"})
    with pytest.raises(DocumentError):
        validate_fixture_request({**request, "port": 443})
    with pytest.raises(DocumentError):
        validate_fixture_request({**request, "headers": [["Content-Type", "application/json"]]})


def test_body_state_absent_rejects_null_body() -> None:
    request = fixture_request(body=AR_REQUEST_BODY)
    with pytest.raises(DocumentError):
        validate_fixture_request({**request, "body": {"state": "absent", "body": None}})


def test_body_state_absent_omits_body() -> None:
    request = fixture_request(body=AR_REQUEST_BODY)
    with pytest.raises(DocumentError):
        # fixture requests must be present_nonempty; absent is the wrong discriminant
        validate_fixture_request({**request, "body": {"state": "absent"}})


def test_body_state_present_zero_requires_empty_digest() -> None:
    request = fixture_request(body=AR_REQUEST_BODY)
    with pytest.raises(DocumentError):
        validate_fixture_request(
            {
                **request,
                "body": {
                    "state": "present_zero_bytes",
                    "body": {"bytes": 0, "sha256": AR_REQUEST_BODY_SHA256},
                },
            }
        )


def test_body_state_present_zero_accepted_on_complete_response() -> None:
    attempt = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    document = capture_document(
        attempt=attempt,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response={
            "headers": [["content-type", "application/json"]],
            "body": {"state": "present_zero_bytes", "body": body_ref(b"")},
            "completeness": "complete",
        },
        transport_failure=None,
        response_headers_at=RESPONSE_HEADERS_AT,
        response_body_ended_at="2026-08-11T20:15:30.950000Z",
    )

    body = document["response"]
    assert isinstance(body, dict)
    state = body["body"]
    assert isinstance(state, dict)
    assert state["state"] == "present_zero_bytes"
    ref = state["body"]
    assert isinstance(ref, dict)
    assert ref == {"bytes": 0, "sha256": EMPTY_BODY_SHA256}


def test_body_state_present_nonempty_rejects_zero_bytes() -> None:
    request = fixture_request(body=AR_REQUEST_BODY)
    with pytest.raises(DocumentError):
        validate_fixture_request(
            {
                **request,
                "body": {
                    "state": "present_nonempty",
                    "body": {"bytes": 0, "sha256": EMPTY_BODY_SHA256},
                },
            }
        )


def test_pair_array_rejects_extra_element() -> None:
    request = fixture_request(body=AR_REQUEST_BODY)
    with pytest.raises(DocumentError):
        validate_fixture_request({**request, "query": [["a", "b", "c"]]})


# ===========================================================================
# Fingerprint, Attempt, Capture — construction, IDs, omit/null
# ===========================================================================


def test_fingerprint_id_matches_published_ar_vector() -> None:
    request = fixture_request(body=AR_REQUEST_BODY)
    document = fingerprint_document(request=request)

    assert content_digest(canonical_json(document)) == AR_FINGERPRINT
    assert document["schema"] == "observatory.request-fingerprint"
    assert document["version"] == 1
    assert document["provider"] == "fixture"
    assert document["adapter_contract"] == "fixture-panel-v1"


def test_fingerprint_rejects_unknown_property() -> None:
    request = fixture_request(body=AR_REQUEST_BODY)
    document = fingerprint_document(request=request)
    with pytest.raises(DocumentError):
        validate_fingerprint({**document, "note": "nope"})


def test_attempt_construction_matches_published_ar_bytes_and_id() -> None:
    document = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )

    encoded = canonical_json(document)
    assert content_digest(encoded) == AR_ATTEMPT_ID
    assert "prior_attempt_id" not in document
    assert encoded == _published_ar_attempt_bytes()


def test_attempt_omits_prior_attempt_id_when_absent() -> None:
    document = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    encoded = canonical_json(document)

    assert b"prior_attempt_id" not in encoded
    assert "prior_attempt_id" not in json.loads(encoded)


def test_attempt_rejects_null_prior_attempt_id() -> None:
    document = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    with pytest.raises(DocumentError):
        validate_attempt({**document, "prior_attempt_id": None})


def test_attempt_accepts_present_prior_attempt_id() -> None:
    prior = "a" * 64
    document = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
        prior_attempt_id=prior,
    )

    assert document["prior_attempt_id"] == prior
    assert b'"prior_attempt_id":"' + prior.encode() in canonical_json(document)


def test_attempt_nonce_rejects_invalid_length_and_charset() -> None:
    with pytest.raises(DocumentError):
        attempt_document(
            parameters=AR_PARAMETERS,
            attempt_nonce="0123456789abcdef",
            authorized_at=AUTHORIZED_AT,
            observatory_version=OBSERVATORY_VERSION,
        )
    with pytest.raises(DocumentError):
        attempt_document(
            parameters=AR_PARAMETERS,
            attempt_nonce="G" * 64,
            authorized_at=AUTHORIZED_AT,
            observatory_version=OBSERVATORY_VERSION,
        )
    with pytest.raises(DocumentError):
        attempt_document(
            parameters=AR_PARAMETERS,
            attempt_nonce="A" * 64,
            authorized_at=AUTHORIZED_AT,
            observatory_version=OBSERVATORY_VERSION,
        )


def test_attempt_rejects_timestamp_not_matching_frozen_syntax() -> None:
    for bad in (
        "2026-08-11T20:15:30Z",
        "2026-08-11T20:15:30.123456z",
        "2026-08-11T20:15:30.12345Z",
        "2026-08-11T20:15:30.1234567Z",
        "2026-08-11 20:15:30.123456Z",
        "2026-08-11T20:15:30.123456+00:00",
    ):
        with pytest.raises(DocumentError):
            attempt_document(
                parameters=AR_PARAMETERS,
                attempt_nonce=AR_NONCE,
                authorized_at=bad,
                observatory_version=OBSERVATORY_VERSION,
            )


def test_attempt_rejects_wrong_schema_version_provider_or_contract() -> None:
    document = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    with pytest.raises(DocumentError):
        validate_attempt({**document, "schema": "observatory.capture-event"})
    with pytest.raises(DocumentError):
        validate_attempt({**document, "version": 2})
    with pytest.raises(DocumentError):
        validate_attempt({**document, "provider": "dataforseo"})
    with pytest.raises(DocumentError):
        validate_attempt({**document, "adapter_contract": "other-v1"})


def test_fingerprint_rejects_wrong_schema_version_provider_or_contract() -> None:
    document = fingerprint_document(request=fixture_request(body=AR_REQUEST_BODY))
    with pytest.raises(DocumentError):
        validate_fingerprint({**document, "schema": "observatory.attempt-event"})
    with pytest.raises(DocumentError):
        validate_fingerprint({**document, "version": 2})
    with pytest.raises(DocumentError):
        validate_fingerprint({**document, "provider": "dataforseo"})
    with pytest.raises(DocumentError):
        validate_fingerprint({**document, "adapter_contract": "other-v1"})


def test_capture_rejects_wrong_schema_version_provider_or_contract() -> None:
    document = _ar_capture()
    with pytest.raises(DocumentError):
        validate_capture({**document, "schema": "observatory.attempt-event"})
    with pytest.raises(DocumentError):
        validate_capture({**document, "version": 2})
    with pytest.raises(DocumentError):
        validate_capture({**document, "provider": "dataforseo"})
    with pytest.raises(DocumentError):
        validate_capture({**document, "adapter_contract": "other-v1"})


def test_attempt_rejects_embedded_attempt_id() -> None:
    document = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    with pytest.raises(DocumentError):
        validate_attempt({**document, "attempt_id": AR_ATTEMPT_ID})


def test_attempt_rejects_mismatched_request_fingerprint() -> None:
    document = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    with pytest.raises(DocumentError):
        validate_attempt({**document, "request_fingerprint": "0" * 64})


def test_attempt_rejects_parameters_that_do_not_match_request_body() -> None:
    document = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    with pytest.raises(DocumentError):
        validate_attempt({**document, "parameters": RP_PARAMETERS})


def test_capture_ar_construction_matches_published_id() -> None:
    attempt = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    document = capture_document(
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

    assert content_digest(canonical_json(document)) == AR_CAPTURE_ID
    assert document["attempt_id"] == AR_ATTEMPT_ID


def test_capture_complete_rejects_non_null_transport_failure() -> None:
    attempt = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    with pytest.raises(DocumentError):
        capture_document(
            attempt=attempt,
            request_started_at=REQUEST_STARTED_AT,
            transport_ended_at=TRANSPORT_ENDED_AT,
            transport_state="response_complete",
            response={
                "headers": [["content-type", "application/json"]],
                "body": {
                    "state": "present_nonempty",
                    "body": body_ref(AR_RESPONSE_BODY),
                },
                "completeness": "complete",
            },
            transport_failure={"code": "fixture_no_response", "phase": "receive_response"},
            response_headers_at=RESPONSE_HEADERS_AT,
            response_body_ended_at="2026-08-11T20:15:30.950000Z",
        )


def test_capture_complete_rejects_partial_completeness() -> None:
    attempt = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    with pytest.raises(DocumentError):
        capture_document(
            attempt=attempt,
            request_started_at=REQUEST_STARTED_AT,
            transport_ended_at=TRANSPORT_ENDED_AT,
            transport_state="response_complete",
            response={
                "headers": [["content-type", "application/json"]],
                "body": {
                    "state": "present_nonempty",
                    "body": body_ref(AR_RESPONSE_BODY),
                },
                "completeness": "partial",
            },
            transport_failure=None,
            response_headers_at=RESPONSE_HEADERS_AT,
            response_body_ended_at="2026-08-11T20:15:30.950000Z",
        )


def test_capture_complete_rejects_null_response() -> None:
    attempt = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    with pytest.raises(DocumentError):
        capture_document(
            attempt=attempt,
            request_started_at=REQUEST_STARTED_AT,
            transport_ended_at=TRANSPORT_ENDED_AT,
            transport_state="response_complete",
            response=None,
            transport_failure=None,
            response_headers_at=RESPONSE_HEADERS_AT,
            response_body_ended_at="2026-08-11T20:15:30.950000Z",
        )


def test_capture_partial_rejects_absent_or_zero_body() -> None:
    attempt = attempt_document(
        parameters=RP_PARAMETERS,
        attempt_nonce=RP_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    with pytest.raises(DocumentError):
        capture_document(
            attempt=attempt,
            request_started_at=REQUEST_STARTED_AT,
            transport_ended_at=TRANSPORT_ENDED_AT,
            transport_state="response_partial",
            response={
                "headers": [["content-type", "application/json"]],
                "body": {"state": "absent"},
                "completeness": "partial",
            },
            transport_failure=None,
            response_headers_at=RESPONSE_HEADERS_AT,
            response_body_ended_at="2026-08-11T20:15:30.920000Z",
        )


def test_capture_no_response_rejects_non_null_response_fields() -> None:
    attempt = attempt_document(
        parameters=NR_PARAMETERS,
        attempt_nonce=NR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    with pytest.raises(DocumentError):
        capture_document(
            attempt=attempt,
            request_started_at=REQUEST_STARTED_AT,
            transport_ended_at=TRANSPORT_ENDED_AT,
            transport_state="no_response",
            response={
                "headers": [["content-type", "application/json"]],
                "body": {"state": "absent"},
                "completeness": "complete",
            },
            transport_failure={"code": "fixture_no_response", "phase": "receive_response"},
            response_headers_at=None,
            response_body_ended_at=None,
        )


def test_capture_no_response_rejects_null_transport_failure() -> None:
    attempt = attempt_document(
        parameters=NR_PARAMETERS,
        attempt_nonce=NR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    with pytest.raises(DocumentError):
        capture_document(
            attempt=attempt,
            request_started_at=REQUEST_STARTED_AT,
            transport_ended_at=TRANSPORT_ENDED_AT,
            transport_state="no_response",
            response=None,
            transport_failure=None,
            response_headers_at=None,
            response_body_ended_at=None,
        )


def test_capture_no_response_rejects_wrong_failure_object() -> None:
    attempt = attempt_document(
        parameters=NR_PARAMETERS,
        attempt_nonce=NR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    with pytest.raises(DocumentError):
        capture_document(
            attempt=attempt,
            request_started_at=REQUEST_STARTED_AT,
            transport_ended_at=TRANSPORT_ENDED_AT,
            transport_state="no_response",
            response=None,
            transport_failure={"code": "timeout", "phase": "receive_response"},
            response_headers_at=None,
            response_body_ended_at=None,
        )


def test_capture_rejects_timestamp_order_violation() -> None:
    attempt = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    with pytest.raises(DocumentError):
        capture_document(
            attempt=attempt,
            request_started_at=TRANSPORT_ENDED_AT,
            transport_ended_at=REQUEST_STARTED_AT,
            transport_state="response_complete",
            response={
                "headers": [["content-type", "application/json"]],
                "body": {
                    "state": "present_nonempty",
                    "body": body_ref(AR_RESPONSE_BODY),
                },
                "completeness": "complete",
            },
            transport_failure=None,
            response_headers_at=RESPONSE_HEADERS_AT,
            response_body_ended_at="2026-08-11T20:15:30.950000Z",
        )


def test_capture_rejects_unknown_property_at_response_depth() -> None:
    attempt = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    with pytest.raises(DocumentError):
        capture_document(
            attempt=attempt,
            request_started_at=REQUEST_STARTED_AT,
            transport_ended_at=TRANSPORT_ENDED_AT,
            transport_state="response_complete",
            response={
                "headers": [["content-type", "application/json"]],
                "body": {
                    "state": "present_nonempty",
                    "body": body_ref(AR_RESPONSE_BODY),
                },
                "completeness": "complete",
                "status": 200,
            },
            transport_failure=None,
            response_headers_at=RESPONSE_HEADERS_AT,
            response_body_ended_at="2026-08-11T20:15:30.950000Z",
        )


def test_capture_rejects_parent_attempt_mismatch() -> None:
    attempt = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    document = capture_document(
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
    other = attempt_document(
        parameters=RP_PARAMETERS,
        attempt_nonce=RP_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    with pytest.raises(DocumentError):
        validate_capture(document, attempt=other)


# ===========================================================================
# Published vectors — bytes, IDs, re-JCS
# ===========================================================================


def test_published_request_bodies_hash_to_published_digests() -> None:
    assert len(AR_REQUEST_BODY) == 124
    assert content_digest(AR_REQUEST_BODY) == AR_REQUEST_BODY_SHA256
    assert len(RP_REQUEST_BODY) == 124
    assert content_digest(RP_REQUEST_BODY) == RP_REQUEST_BODY_SHA256
    assert len(NR_REQUEST_BODY) == 119
    assert content_digest(NR_REQUEST_BODY) == NR_REQUEST_BODY_SHA256
    assert len(AR_RESPONSE_BODY) == 299
    assert content_digest(AR_RESPONSE_BODY) == AR_RESPONSE_BODY_SHA256
    assert len(RP_RESPONSE_BODY) == 32
    assert content_digest(RP_RESPONSE_BODY) == RP_RESPONSE_BODY_SHA256
    assert AR_RESPONSE_BODY[:32] == RP_RESPONSE_BODY
    assert content_digest(_published_ar_fingerprint_bytes()) == AR_FINGERPRINT
    assert content_digest(_published_ar_attempt_bytes()) == AR_ATTEMPT_ID
    assert content_digest(_published_ar_capture_bytes()) == AR_CAPTURE_ID
    assert content_digest(_published_rp_fingerprint_bytes()) == RP_FINGERPRINT
    assert content_digest(_published_rp_attempt_bytes()) == RP_ATTEMPT_ID
    assert content_digest(_published_rp_capture_bytes()) == RP_CAPTURE_ID
    assert content_digest(_published_nr_fingerprint_bytes()) == NR_FINGERPRINT
    assert content_digest(_published_nr_attempt_bytes()) == NR_ATTEMPT_ID
    assert content_digest(_published_nr_capture_bytes()) == NR_CAPTURE_ID


def test_constructed_ar_rp_nr_identities_match_published_digests() -> None:
    ar = attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    rp = attempt_document(
        parameters=RP_PARAMETERS,
        attempt_nonce=RP_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    nr = attempt_document(
        parameters=NR_PARAMETERS,
        attempt_nonce=NR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )

    ar_request = ar["request"]
    assert isinstance(ar_request, dict)
    assert content_digest(canonical_json(fingerprint_document(request=ar_request))) == (
        AR_FINGERPRINT
    )
    assert content_digest(canonical_json(ar)) == AR_ATTEMPT_ID
    assert content_digest(canonical_json(rp)) == RP_ATTEMPT_ID
    assert content_digest(canonical_json(nr)) == NR_ATTEMPT_ID

    ar_capture = capture_document(
        attempt=ar,
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
    rp_capture = capture_document(
        attempt=rp,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="response_partial",
        response={
            "headers": [["content-type", "application/json"]],
            "body": {"state": "present_nonempty", "body": body_ref(RP_RESPONSE_BODY)},
            "completeness": "partial",
        },
        transport_failure=None,
        response_headers_at=RESPONSE_HEADERS_AT,
        response_body_ended_at="2026-08-11T20:15:30.920000Z",
    )
    nr_capture = capture_document(
        attempt=nr,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="no_response",
        response=None,
        transport_failure={"code": "fixture_no_response", "phase": "receive_response"},
        response_headers_at=None,
        response_body_ended_at=None,
    )

    assert content_digest(canonical_json(ar_capture)) == AR_CAPTURE_ID
    assert content_digest(canonical_json(rp_capture)) == RP_CAPTURE_ID
    assert content_digest(canonical_json(nr_capture)) == NR_CAPTURE_ID


def test_re_jcs_of_parsed_published_vectors_equals_original_bytes() -> None:
    cases = (
        (AR_REQUEST_BODY, validate_parameters),
        (RP_REQUEST_BODY, validate_parameters),
        (NR_REQUEST_BODY, validate_parameters),
        (_published_ar_fingerprint_bytes(), validate_fingerprint),
        (_published_ar_attempt_bytes(), validate_attempt),
        (_published_ar_capture_bytes(), validate_capture),
        (_published_rp_fingerprint_bytes(), validate_fingerprint),
        (_published_rp_attempt_bytes(), validate_attempt),
        (_published_rp_capture_bytes(), validate_capture),
        (_published_nr_fingerprint_bytes(), validate_fingerprint),
        (_published_nr_attempt_bytes(), validate_attempt),
        (_published_nr_capture_bytes(), validate_capture),
    )
    for raw, loader in cases:
        loaded = loader(raw)
        assert canonical_json(loaded) == raw


def test_vector_validation_does_not_write_the_filesystem(tmp_path: Any, monkeypatch: Any) -> None:
    monkeypatch.chdir(tmp_path)
    attempt_document(
        parameters=AR_PARAMETERS,
        attempt_nonce=AR_NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=OBSERVATORY_VERSION,
    )
    assert list(tmp_path.iterdir()) == []


def _published_ar_fingerprint_bytes() -> bytes:
    return (
        b'{"adapter_contract":"fixture-panel-v1","provider":"fixture","request":'
        b'{"body":{"body":{"bytes":124,"sha256":"'
        + AR_REQUEST_BODY_SHA256.encode()
        + b'"},"state":"present_nonempty"},"headers":[["content-type",'
        b'"application/json"]],"host":"fixture-panel","method":"POST",'
        b'"path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},'
        b'"schema":"observatory.request-fingerprint","version":1}'
    )


def _published_ar_attempt_bytes() -> bytes:
    return (
        b'{"adapter_contract":"fixture-panel-v1","attempt_nonce":"'
        + AR_NONCE.encode()
        + b'","authorized_at":"'
        + AUTHORIZED_AT.encode()
        + b'","parameters":{"contract":"fixture-panel-v1","depth":2,'
        b'"panel_id":"panel-alpha","scenario":"admitted_results",'
        b'"subject_key":"subject-one"},"policy":{"mode":"fixture_no_spend",'
        b'"policy_version":"fixture-v1"},"provider":"fixture","request":'
        b'{"body":{"body":{"bytes":124,"sha256":"'
        + AR_REQUEST_BODY_SHA256.encode()
        + b'"},"state":"present_nonempty"},"headers":[["content-type",'
        b'"application/json"]],"host":"fixture-panel","method":"POST",'
        b'"path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},'
        b'"request_fingerprint":"'
        + AR_FINGERPRINT.encode()
        + b'","schema":"observatory.attempt-event","software":'
        b'{"observatory_version":"conformance-v1"},"version":1}'
    )


def _published_ar_capture_bytes() -> bytes:
    return (
        b'{"adapter_contract":"fixture-panel-v1","attempt_id":"'
        + AR_ATTEMPT_ID.encode()
        + b'","provider":"fixture","request":{"body":{"body":{"bytes":124,"sha256":"'
        + AR_REQUEST_BODY_SHA256.encode()
        + b'"},"state":"present_nonempty"},"headers":[["content-type",'
        b'"application/json"]],"host":"fixture-panel","method":"POST",'
        b'"path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},'
        b'"request_fingerprint":"'
        + AR_FINGERPRINT.encode()
        + b'","request_started_at":"'
        + REQUEST_STARTED_AT.encode()
        + b'","response":{"body":{"body":{"bytes":299,"sha256":"'
        + AR_RESPONSE_BODY_SHA256.encode()
        + b'"},"state":"present_nonempty"},"completeness":"complete",'
        b'"headers":[["content-type","application/json"]]},'
        b'"response_body_ended_at":"2026-08-11T20:15:30.950000Z",'
        b'"response_headers_at":"'
        + RESPONSE_HEADERS_AT.encode()
        + b'","schema":"observatory.capture-event","software":'
        b'{"observatory_version":"conformance-v1"},"transport_ended_at":"'
        + TRANSPORT_ENDED_AT.encode()
        + b'","transport_failure":null,"transport_state":"response_complete",'
        b'"version":1}'
    )


def _published_rp_fingerprint_bytes() -> bytes:
    return (
        b'{"adapter_contract":"fixture-panel-v1","provider":"fixture","request":'
        b'{"body":{"body":{"bytes":124,"sha256":"'
        + RP_REQUEST_BODY_SHA256.encode()
        + b'"},"state":"present_nonempty"},"headers":[["content-type",'
        b'"application/json"]],"host":"fixture-panel","method":"POST",'
        b'"path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},'
        b'"schema":"observatory.request-fingerprint","version":1}'
    )


def _published_rp_attempt_bytes() -> bytes:
    return (
        b'{"adapter_contract":"fixture-panel-v1","attempt_nonce":"'
        + RP_NONCE.encode()
        + b'","authorized_at":"'
        + AUTHORIZED_AT.encode()
        + b'","parameters":{"contract":"fixture-panel-v1","depth":2,'
        b'"panel_id":"panel-alpha","scenario":"response_partial",'
        b'"subject_key":"subject-one"},"policy":{"mode":"fixture_no_spend",'
        b'"policy_version":"fixture-v1"},"provider":"fixture","request":'
        b'{"body":{"body":{"bytes":124,"sha256":"'
        + RP_REQUEST_BODY_SHA256.encode()
        + b'"},"state":"present_nonempty"},"headers":[["content-type",'
        b'"application/json"]],"host":"fixture-panel","method":"POST",'
        b'"path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},'
        b'"request_fingerprint":"'
        + RP_FINGERPRINT.encode()
        + b'","schema":"observatory.attempt-event","software":'
        b'{"observatory_version":"conformance-v1"},"version":1}'
    )


def _published_rp_capture_bytes() -> bytes:
    return (
        b'{"adapter_contract":"fixture-panel-v1","attempt_id":"'
        + RP_ATTEMPT_ID.encode()
        + b'","provider":"fixture","request":{"body":{"body":{"bytes":124,"sha256":"'
        + RP_REQUEST_BODY_SHA256.encode()
        + b'"},"state":"present_nonempty"},"headers":[["content-type",'
        b'"application/json"]],"host":"fixture-panel","method":"POST",'
        b'"path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},'
        b'"request_fingerprint":"'
        + RP_FINGERPRINT.encode()
        + b'","request_started_at":"'
        + REQUEST_STARTED_AT.encode()
        + b'","response":{"body":{"body":{"bytes":32,"sha256":"'
        + RP_RESPONSE_BODY_SHA256.encode()
        + b'"},"state":"present_nonempty"},"completeness":"partial",'
        b'"headers":[["content-type","application/json"]]},'
        b'"response_body_ended_at":"2026-08-11T20:15:30.920000Z",'
        b'"response_headers_at":"'
        + RESPONSE_HEADERS_AT.encode()
        + b'","schema":"observatory.capture-event","software":'
        b'{"observatory_version":"conformance-v1"},"transport_ended_at":"'
        + TRANSPORT_ENDED_AT.encode()
        + b'","transport_failure":null,"transport_state":"response_partial",'
        b'"version":1}'
    )


def _published_nr_fingerprint_bytes() -> bytes:
    return (
        b'{"adapter_contract":"fixture-panel-v1","provider":"fixture","request":'
        b'{"body":{"body":{"bytes":119,"sha256":"'
        + NR_REQUEST_BODY_SHA256.encode()
        + b'"},"state":"present_nonempty"},"headers":[["content-type",'
        b'"application/json"]],"host":"fixture-panel","method":"POST",'
        b'"path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},'
        b'"schema":"observatory.request-fingerprint","version":1}'
    )


def _published_nr_attempt_bytes() -> bytes:
    return (
        b'{"adapter_contract":"fixture-panel-v1","attempt_nonce":"'
        + NR_NONCE.encode()
        + b'","authorized_at":"'
        + AUTHORIZED_AT.encode()
        + b'","parameters":{"contract":"fixture-panel-v1","depth":2,'
        b'"panel_id":"panel-alpha","scenario":"no_response",'
        b'"subject_key":"subject-one"},"policy":{"mode":"fixture_no_spend",'
        b'"policy_version":"fixture-v1"},"provider":"fixture","request":'
        b'{"body":{"body":{"bytes":119,"sha256":"'
        + NR_REQUEST_BODY_SHA256.encode()
        + b'"},"state":"present_nonempty"},"headers":[["content-type",'
        b'"application/json"]],"host":"fixture-panel","method":"POST",'
        b'"path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},'
        b'"request_fingerprint":"'
        + NR_FINGERPRINT.encode()
        + b'","schema":"observatory.attempt-event","software":'
        b'{"observatory_version":"conformance-v1"},"version":1}'
    )


def _published_nr_capture_bytes() -> bytes:
    return (
        b'{"adapter_contract":"fixture-panel-v1","attempt_id":"'
        + NR_ATTEMPT_ID.encode()
        + b'","provider":"fixture","request":{"body":{"body":{"bytes":119,"sha256":"'
        + NR_REQUEST_BODY_SHA256.encode()
        + b'"},"state":"present_nonempty"},"headers":[["content-type",'
        b'"application/json"]],"host":"fixture-panel","method":"POST",'
        b'"path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},'
        b'"request_fingerprint":"'
        + NR_FINGERPRINT.encode()
        + b'","request_started_at":"'
        + REQUEST_STARTED_AT.encode()
        + b'","response":null,"response_body_ended_at":null,'
        b'"response_headers_at":null,"schema":"observatory.capture-event",'
        b'"software":{"observatory_version":"conformance-v1"},'
        b'"transport_ended_at":"'
        + TRANSPORT_ENDED_AT.encode()
        + b'","transport_failure":{"code":"fixture_no_response",'
        b'"phase":"receive_response"},"transport_state":"no_response","version":1}'
    )
