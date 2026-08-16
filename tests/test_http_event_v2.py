"""PF-01: HTTP event v2 construction, dispatch, mixed-store verify, derive skip."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from observatory.api import create_app
from observatory.capture import PUBLISHED_AR_ATTEMPT_ID, PUBLISHED_AR_INPUTS, capture_fixture
from observatory.capture_event import (
    DocumentError,
    body_ref,
    canonical_json,
    content_digest,
    http_attempt_document,
    http_capture_document,
    http_fingerprint_document,
    http_request,
    validate_attempt,
    validate_capture,
    validate_fingerprint,
    validate_http_parameters,
    validate_http_request,
)
from observatory.derive import DEFAULT_VERSION, derive
from observatory.evidence import scrub_store
from observatory.evidence_store import EvidenceStore, IntegrityError, create_store
from observatory.migrate import connect
from observatory.settings import Settings

# ---------------------------------------------------------------------------
# Independent published HTTP-v2 literals (spec §HTTP-v2 conformance vector)
# ---------------------------------------------------------------------------

HTTP_ADAPTER = "dataforseo-serp-google-organic-live-advanced-sandbox-v1"
HTTP_NONCE = "3333333333333333333333333333333333333333333333333333333333333333"
HTTP_AUTHORIZED_AT = "2026-08-14T20:00:00.000000Z"
HTTP_REQUEST_STARTED_AT = "2026-08-14T20:00:00.100000Z"
HTTP_RESPONSE_HEADERS_AT = "2026-08-14T20:00:00.200000Z"
HTTP_RESPONSE_BODY_ENDED_AT = "2026-08-14T20:00:00.300000Z"
HTTP_TRANSPORT_ENDED_AT = "2026-08-14T20:00:00.400000Z"
HTTP_SOFTWARE = "conformance-http-v2"

HTTP_REQUEST_BODY = (
    b'[{"depth":10,"device":"desktop","keyword":"observatory test",'
    b'"language_code":"en","location_code":2840,"os":"windows"}]'
)
HTTP_REQUEST_BODY_SHA256 = "d10484d2237e4b08e37a4f3fe66bd678a3dbc2dab96f9b712af1b858b8d6d070"
HTTP_FINGERPRINT_PREIMAGE = (
    b'{"adapter_contract":"dataforseo-serp-google-organic-live-advanced-sandbox-v1",'
    b'"provider":"dataforseo","request":{"body":{"body":{"bytes":119,"sha256":'
    b'"d10484d2237e4b08e37a4f3fe66bd678a3dbc2dab96f9b712af1b858b8d6d070"},'
    b'"state":"present_nonempty"},"headers":[["accept","application/json"],'
    b'["accept-encoding","identity"],["connection","close"],'
    b'["content-type","application/json"],["user-agent","observatory-dataforseo-v1"]],'
    b'"host":"sandbox.dataforseo.com","method":"POST",'
    b'"path":"/v3/serp/google/organic/live/advanced","port":null,"query":[],'
    b'"scheme":"https"},"schema":"observatory.request-fingerprint","version":2}'
)
HTTP_FINGERPRINT = "6b28e6d02fee14c8d8852889336baeb46bfa9918c5d4eee7b51e889f1823a2bb"
HTTP_ATTEMPT_PREIMAGE = (
    b'{"adapter_contract":"dataforseo-serp-google-organic-live-advanced-sandbox-v1",'
    b'"attempt_nonce":"3333333333333333333333333333333333333333333333333333333333333333",'
    b'"authorized_at":"2026-08-14T20:00:00.000000Z",'
    b'"parameters":{"contract":"dataforseo-serp-google-organic-live-advanced-sandbox-v1",'
    b'"depth":10,"device":"desktop","keyword":"observatory test","language_code":"en",'
    b'"location_code":2840,"os":"windows"},"policy":{"mode":"sandbox_no_spend",'
    b'"policy_version":"dataforseo-sandbox-v1"},"provider":"dataforseo","request":'
    b'{"body":{"body":{"bytes":119,"sha256":'
    b'"d10484d2237e4b08e37a4f3fe66bd678a3dbc2dab96f9b712af1b858b8d6d070"},'
    b'"state":"present_nonempty"},"headers":[["accept","application/json"],'
    b'["accept-encoding","identity"],["connection","close"],'
    b'["content-type","application/json"],["user-agent","observatory-dataforseo-v1"]],'
    b'"host":"sandbox.dataforseo.com","method":"POST",'
    b'"path":"/v3/serp/google/organic/live/advanced","port":null,"query":[],'
    b'"scheme":"https"},"request_fingerprint":'
    b'"6b28e6d02fee14c8d8852889336baeb46bfa9918c5d4eee7b51e889f1823a2bb",'
    b'"schema":"observatory.attempt-event","software":'
    b'{"observatory_version":"conformance-http-v2"},"version":2}'
)
HTTP_ATTEMPT_ID = "22adc4841c86b7cd98b90bba683aeac204a0cb568428b590fd399e8627eb4640"
HTTP_RESPONSE_BODY = b'{"status_code":20000,"status_message":"Ok.","tasks":[]}'
HTTP_RESPONSE_BODY_SHA256 = "a38a556da546f074db94ab0ea18cf557bdac6b44d637f414cc0d431a7c19a9b3"
HTTP_CAPTURE_PREIMAGE = (
    b'{"adapter_contract":"dataforseo-serp-google-organic-live-advanced-sandbox-v1",'
    b'"attempt_id":"22adc4841c86b7cd98b90bba683aeac204a0cb568428b590fd399e8627eb4640",'
    b'"provider":"dataforseo","request":{"body":{"body":{"bytes":119,"sha256":'
    b'"d10484d2237e4b08e37a4f3fe66bd678a3dbc2dab96f9b712af1b858b8d6d070"},'
    b'"state":"present_nonempty"},"headers":[["accept","application/json"],'
    b'["accept-encoding","identity"],["connection","close"],'
    b'["content-type","application/json"],["user-agent","observatory-dataforseo-v1"]],'
    b'"host":"sandbox.dataforseo.com","method":"POST",'
    b'"path":"/v3/serp/google/organic/live/advanced","port":null,"query":[],'
    b'"scheme":"https"},"request_fingerprint":'
    b'"6b28e6d02fee14c8d8852889336baeb46bfa9918c5d4eee7b51e889f1823a2bb",'
    b'"request_started_at":"2026-08-14T20:00:00.100000Z","response":{"body":{"body":'
    b'{"bytes":55,"sha256":"a38a556da546f074db94ab0ea18cf557bdac6b44d637f414cc0d431a7c19a9b3"},'
    b'"state":"present_nonempty"},"completeness":"complete","header_policy":"http-headers-v1",'
    b'"headers":[["content-type","application/json"],["x-request-id","sandbox-vector"]],'
    b'"http_version":"HTTP/1.1","omitted_headers":[{"count":1,"name":"set-cookie"}],'
    b'"status":200},"response_body_ended_at":"2026-08-14T20:00:00.300000Z",'
    b'"response_headers_at":"2026-08-14T20:00:00.200000Z","schema":"observatory.capture-event",'
    b'"software":{"observatory_version":"conformance-http-v2"},'
    b'"transport_ended_at":"2026-08-14T20:00:00.400000Z","transport_failure":null,'
    b'"transport_state":"response_complete","version":2}'
)
HTTP_CAPTURE_ID = "f347962c8dad05a762a19898898fff7ed60b7c06270b61dc3d7a158fa0d396b7"

HTTP_PARAMETERS: dict[str, Any] = {
    "contract": HTTP_ADAPTER,
    "depth": 10,
    "device": "desktop",
    "keyword": "observatory test",
    "language_code": "en",
    "location_code": 2840,
    "os": "windows",
}

# Event-v1 published AR bytes (independent of production builders).
V1_AR_REQUEST_BODY = (
    b'{"contract":"fixture-panel-v1","depth":2,"panel_id":"panel-alpha",'
    b'"scenario":"admitted_results","subject_key":"subject-one"}'
)
V1_AR_ATTEMPT = (
    b'{"adapter_contract":"fixture-panel-v1","attempt_nonce":'
    b'"0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",'
    b'"authorized_at":"2026-08-11T20:15:30.123456Z",'
    b'"parameters":{"contract":"fixture-panel-v1","depth":2,'
    b'"panel_id":"panel-alpha","scenario":"admitted_results",'
    b'"subject_key":"subject-one"},"policy":{"mode":"fixture_no_spend",'
    b'"policy_version":"fixture-v1"},"provider":"fixture","request":'
    b'{"body":{"body":{"bytes":124,"sha256":'
    b'"f16972cae6bea7a84acc0c6d0b181a2de3fabf7870663b1fb76f389aed4c38ec"},'
    b'"state":"present_nonempty"},"headers":[["content-type","application/json"]],'
    b'"host":"fixture-panel","method":"POST","path":"/v1/measure","port":null,'
    b'"query":[],"scheme":"fixture"},"request_fingerprint":'
    b'"d18682cc029a8db08b0b761b900db2c7c91f92a99087597281cbdbdaec70e88b",'
    b'"schema":"observatory.attempt-event","software":'
    b'{"observatory_version":"conformance-v1"},"version":1}'
)
V1_AR_ATTEMPT_ID = "46d5fb97c109b9f64a42ff3a5e62978e2c25551d6b7274603fc88456acfd9a0f"
V1_AR_CAPTURE = (
    b'{"adapter_contract":"fixture-panel-v1","attempt_id":'
    b'"46d5fb97c109b9f64a42ff3a5e62978e2c25551d6b7274603fc88456acfd9a0f",'
    b'"provider":"fixture","request":{"body":{"body":{"bytes":124,"sha256":'
    b'"f16972cae6bea7a84acc0c6d0b181a2de3fabf7870663b1fb76f389aed4c38ec"},'
    b'"state":"present_nonempty"},"headers":[["content-type","application/json"]],'
    b'"host":"fixture-panel","method":"POST","path":"/v1/measure","port":null,'
    b'"query":[],"scheme":"fixture"},"request_fingerprint":'
    b'"d18682cc029a8db08b0b761b900db2c7c91f92a99087597281cbdbdaec70e88b",'
    b'"request_started_at":"2026-08-11T20:15:30.200000Z","response":{"body":{"body":'
    b'{"bytes":299,"sha256":"40735fbc1cd0f98e140857bec1b1e8c6d6f666baa0fb49bfd0e782aaa6513eac"},'
    b'"state":"present_nonempty"},"completeness":"complete",'
    b'"headers":[["content-type","application/json"]]},'
    b'"response_body_ended_at":"2026-08-11T20:15:30.950000Z",'
    b'"response_headers_at":"2026-08-11T20:15:30.900000Z",'
    b'"schema":"observatory.capture-event","software":'
    b'{"observatory_version":"conformance-v1"},'
    b'"transport_ended_at":"2026-08-11T20:15:31.000000Z","transport_failure":null,'
    b'"transport_state":"response_complete","version":1}'
)
V1_AR_CAPTURE_ID = "604663f0e7842f1e076189652667357083d4c4a5e56a44d67ea4596ef624ad44"

HTTP_HEADERS = [
    ["accept", "application/json"],
    ["accept-encoding", "identity"],
    ["connection", "close"],
    ["content-type", "application/json"],
    ["user-agent", "observatory-dataforseo-v1"],
]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _http_attempt() -> dict[str, Any]:
    return http_attempt_document(
        parameters=HTTP_PARAMETERS,
        attempt_nonce=HTTP_NONCE,
        authorized_at=HTTP_AUTHORIZED_AT,
        observatory_version=HTTP_SOFTWARE,
    )


def _complete_response() -> dict[str, Any]:
    return {
        "status": 200,
        "http_version": "HTTP/1.1",
        "header_policy": "http-headers-v1",
        "headers": [["content-type", "application/json"], ["x-request-id", "sandbox-vector"]],
        "omitted_headers": [{"count": 1, "name": "set-cookie"}],
        "body": {"state": "present_nonempty", "body": body_ref(HTTP_RESPONSE_BODY)},
        "completeness": "complete",
    }


def _http_complete_capture(attempt: dict[str, Any] | None = None) -> dict[str, Any]:
    return http_capture_document(
        attempt=attempt if attempt is not None else _http_attempt(),
        request_started_at=HTTP_REQUEST_STARTED_AT,
        transport_ended_at=HTTP_TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response=_complete_response(),
        transport_failure=None,
        response_headers_at=HTTP_RESPONSE_HEADERS_AT,
        response_body_ended_at=HTTP_RESPONSE_BODY_ENDED_AT,
    )


def _commit_http_complete(store: EvidenceStore) -> tuple[str, str]:
    attempt = _http_attempt()
    attempt_id = store.commit_attempt(attempt, request_body=HTTP_REQUEST_BODY)
    capture_id = store.commit_capture(
        _http_complete_capture(attempt), response_body=HTTP_RESPONSE_BODY
    )
    return attempt_id, capture_id


def _app(store: EvidenceStore, dsn: str) -> TestClient:
    settings = Settings(
        environment="test",
        database_url=dsn,
        evidence_root=store.root,
        derivation_version_id=DEFAULT_VERSION,
    )
    return TestClient(create_app(settings, store=store))


def _row_counts(connection: Any) -> dict[str, int]:
    versions = connection.execute("SELECT count(*) FROM derivation_versions").fetchone()
    outcomes = connection.execute("SELECT count(*) FROM outcomes").fetchone()
    observations = connection.execute("SELECT count(*) FROM observations").fetchone()
    assert versions is not None and outcomes is not None and observations is not None
    return {
        "derivation_versions": int(versions[0]),
        "outcomes": int(outcomes[0]),
        "observations": int(observations[0]),
    }


def _all_ids(connection: Any) -> tuple[set[str], set[str]]:
    attempt_ids = {
        str(row[0]) for row in connection.execute("SELECT attempt_id FROM outcomes").fetchall()
    }
    attempt_ids.update(
        str(row[0]) for row in connection.execute("SELECT attempt_id FROM observations").fetchall()
    )
    capture_ids = {
        str(row[0])
        for row in connection.execute(
            "SELECT capture_id FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchall()
    }
    capture_ids.update(
        str(row[0]) for row in connection.execute("SELECT capture_id FROM observations").fetchall()
    )
    return attempt_ids, capture_ids


# ===========================================================================
# Published HTTP-v2 vectors and event-v1 regression
# ===========================================================================


def test_published_http_v2_vectors_match_independent_sha256_and_lengths() -> None:
    assert len(HTTP_REQUEST_BODY) == 119
    assert _sha256(HTTP_REQUEST_BODY) == HTTP_REQUEST_BODY_SHA256
    assert len(HTTP_FINGERPRINT_PREIMAGE) == 612
    assert _sha256(HTTP_FINGERPRINT_PREIMAGE) == HTTP_FINGERPRINT
    assert len(HTTP_ATTEMPT_PREIMAGE) == 1159
    assert _sha256(HTTP_ATTEMPT_PREIMAGE) == HTTP_ATTEMPT_ID
    assert len(HTTP_RESPONSE_BODY) == 55
    assert _sha256(HTTP_RESPONSE_BODY) == HTTP_RESPONSE_BODY_SHA256
    assert len(HTTP_CAPTURE_PREIMAGE) == 1482
    assert _sha256(HTTP_CAPTURE_PREIMAGE) == HTTP_CAPTURE_ID


def test_http_v2_constructors_reproduce_published_bytes_and_ids() -> None:
    request = http_request(body=HTTP_REQUEST_BODY)
    fingerprint = http_fingerprint_document(request=request)
    attempt = _http_attempt()
    capture = _http_complete_capture(attempt)

    assert canonical_json(fingerprint) == HTTP_FINGERPRINT_PREIMAGE
    assert content_digest(canonical_json(fingerprint)) == HTTP_FINGERPRINT
    assert canonical_json(attempt) == HTTP_ATTEMPT_PREIMAGE
    assert content_digest(canonical_json(attempt)) == HTTP_ATTEMPT_ID
    assert canonical_json(capture) == HTTP_CAPTURE_PREIMAGE
    assert content_digest(canonical_json(capture)) == HTTP_CAPTURE_ID


def test_published_http_v2_preimages_revalidate() -> None:
    assert validate_fingerprint(HTTP_FINGERPRINT_PREIMAGE)["version"] == 2
    assert validate_attempt(HTTP_ATTEMPT_PREIMAGE)["version"] == 2
    assert validate_capture(HTTP_CAPTURE_PREIMAGE)["version"] == 2
    assert canonical_json(validate_attempt(HTTP_ATTEMPT_PREIMAGE)) == HTTP_ATTEMPT_PREIMAGE
    assert canonical_json(validate_capture(HTTP_CAPTURE_PREIMAGE)) == HTTP_CAPTURE_PREIMAGE


def test_event_v1_published_bytes_and_ids_are_unchanged() -> None:
    assert _sha256(V1_AR_REQUEST_BODY) == (
        "f16972cae6bea7a84acc0c6d0b181a2de3fabf7870663b1fb76f389aed4c38ec"
    )
    assert _sha256(V1_AR_ATTEMPT) == V1_AR_ATTEMPT_ID
    assert _sha256(V1_AR_CAPTURE) == V1_AR_CAPTURE_ID
    loaded_attempt = validate_attempt(V1_AR_ATTEMPT)
    loaded_capture = validate_capture(V1_AR_CAPTURE)
    assert loaded_attempt["version"] == 1
    assert loaded_capture["version"] == 1
    assert canonical_json(loaded_attempt) == V1_AR_ATTEMPT
    assert canonical_json(loaded_capture) == V1_AR_CAPTURE
    assert content_digest(canonical_json(loaded_attempt)) == V1_AR_ATTEMPT_ID
    assert content_digest(canonical_json(loaded_capture)) == V1_AR_CAPTURE_ID


# ===========================================================================
# Dispatch: schema/version only, then closed re-validation
# ===========================================================================


@pytest.mark.parametrize("version", [0, 3, True, "2"])
def test_unknown_fingerprint_version_fails_closed(version: object) -> None:
    document = json.loads(HTTP_FINGERPRINT_PREIMAGE)
    document["version"] = version
    with pytest.raises(DocumentError):
        validate_fingerprint(document)


@pytest.mark.parametrize("version", [0, 3, True, "2"])
def test_unknown_attempt_version_fails_closed(version: object) -> None:
    document = json.loads(HTTP_ATTEMPT_PREIMAGE)
    document["version"] = version
    with pytest.raises(DocumentError):
        validate_attempt(document)


@pytest.mark.parametrize("version", [0, 3, True, "2"])
def test_unknown_capture_version_fails_closed(version: object) -> None:
    document = json.loads(HTTP_CAPTURE_PREIMAGE)
    document["version"] = version
    with pytest.raises(DocumentError):
        validate_capture(document)


def test_unknown_schema_fails_closed() -> None:
    attempt = json.loads(HTTP_ATTEMPT_PREIMAGE)
    attempt["schema"] = "observatory.http-event"
    with pytest.raises(DocumentError):
        validate_attempt(attempt)
    capture = json.loads(HTTP_CAPTURE_PREIMAGE)
    capture["schema"] = "observatory.http-event"
    with pytest.raises(DocumentError):
        validate_capture(capture)
    fingerprint = json.loads(HTTP_FINGERPRINT_PREIMAGE)
    fingerprint["schema"] = "observatory.http-fingerprint"
    with pytest.raises(DocumentError):
        validate_fingerprint(fingerprint)


def test_version_confused_v1_keys_on_v2_attempt_fail() -> None:
    document = json.loads(HTTP_ATTEMPT_PREIMAGE)
    document["prior_attempt_id"] = "0" * 64
    with pytest.raises(DocumentError):
        validate_attempt(document)


def test_version_confused_v2_response_keys_on_v1_capture_fail() -> None:
    document = json.loads(V1_AR_CAPTURE)
    response = document["response"]
    assert isinstance(response, dict)
    response["status"] = 200
    response["http_version"] = "HTTP/1.1"
    response["header_policy"] = "http-headers-v1"
    response["omitted_headers"] = []
    with pytest.raises(DocumentError):
        validate_capture(document)


def test_fixture_document_with_version_2_fails_closed() -> None:
    document = json.loads(V1_AR_ATTEMPT)
    document["version"] = 2
    with pytest.raises(DocumentError):
        validate_attempt(document)
    capture = json.loads(V1_AR_CAPTURE)
    capture["version"] = 2
    with pytest.raises(DocumentError):
        validate_capture(capture)


def test_unknown_adapter_contract_fails_closed() -> None:
    document = json.loads(HTTP_ATTEMPT_PREIMAGE)
    document["adapter_contract"] = "dataforseo-serp-google-organic-live-advanced-v1"
    with pytest.raises(DocumentError):
        validate_attempt(document)


# ===========================================================================
# Adapter parameters, policy, request headers
# ===========================================================================


def test_http_parameters_accept_the_closed_sandbox_contract() -> None:
    parsed = validate_http_parameters(dict(HTTP_PARAMETERS))
    assert parsed["depth"] == 10
    assert parsed["device"] == "desktop"
    assert parsed["os"] == "windows"
    assert parsed["contract"] == HTTP_ADAPTER


@pytest.mark.parametrize(
    "patch",
    [
        {"keyword": ""},
        {"keyword": "x" * 701},
        {"location_code": 0},
        {"location_code": 9007199254740992},
        {"language_code": "EN"},
        {"language_code": "e"},
        {"language_code": "eng"},
        {"depth": 9},
        {"depth": 11},
        {"device": "mobile"},
        {"os": "linux"},
        {"contract": "fixture-panel-v1"},
        {"extra": 1},
    ],
)
def test_http_parameters_reject_boundary_violations(patch: dict[str, object]) -> None:
    parameters = dict(HTTP_PARAMETERS)
    if "extra" in patch:
        parameters["extra"] = patch["extra"]
    else:
        parameters.update(patch)
    with pytest.raises(DocumentError):
        validate_http_parameters(parameters)


def test_http_parameters_accept_keyword_length_bounds() -> None:
    short = dict(HTTP_PARAMETERS)
    short["keyword"] = "a"
    long_ok = dict(HTTP_PARAMETERS)
    long_ok["keyword"] = "b" * 700
    assert validate_http_parameters(short)["keyword"] == "a"
    assert validate_http_parameters(long_ok)["keyword"] == "b" * 700


def test_sandbox_policy_requires_https_sandbox_host_one_task_depth_10() -> None:
    request = http_request(body=HTTP_REQUEST_BODY)
    assert request["scheme"] == "https"
    assert request["host"] == "sandbox.dataforseo.com"
    assert request["port"] is None
    assert request["path"] == "/v3/serp/google/organic/live/advanced"
    assert request["query"] == []
    task = json.loads(HTTP_REQUEST_BODY)
    assert isinstance(task, list) and len(task) == 1
    assert task[0]["depth"] == 10
    attempt = _http_attempt()
    assert attempt["policy"] == {
        "mode": "sandbox_no_spend",
        "policy_version": "dataforseo-sandbox-v1",
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("scheme", "http"),
        ("host", "api.dataforseo.com"),
        ("port", 443),
        ("path", "/v3/serp/google/organic/live/regular"),
        ("query", [["q", "x"]]),
        ("method", "GET"),
    ],
)
def test_http_request_rejects_non_sandbox_target(field: str, value: object) -> None:
    request = dict(http_request(body=HTTP_REQUEST_BODY))
    request[field] = value
    with pytest.raises(DocumentError):
        validate_http_request(request)


def test_http_request_rejects_credential_class_and_reordered_headers() -> None:
    base = dict(http_request(body=HTTP_REQUEST_BODY))
    with pytest.raises(DocumentError):
        validate_http_request({**base, "headers": HTTP_HEADERS + [["authorization", "Basic x"]]})
    with pytest.raises(DocumentError):
        validate_http_request({**base, "headers": HTTP_HEADERS + [["cookie", "a=b"]]})
    with pytest.raises(DocumentError):
        validate_http_request(
            {**base, "headers": HTTP_HEADERS + [["proxy-authorization", "Basic x"]]}
        )
    reordered = [HTTP_HEADERS[1], HTTP_HEADERS[0], *HTTP_HEADERS[2:]]
    with pytest.raises(DocumentError):
        validate_http_request({**base, "headers": reordered})
    missing = HTTP_HEADERS[:-1]
    with pytest.raises(DocumentError):
        validate_http_request({**base, "headers": missing})
    upper = [list(pair) for pair in HTTP_HEADERS]
    upper[0][0] = "Accept"
    with pytest.raises(DocumentError):
        validate_http_request({**base, "headers": upper})


def test_http_attempt_rejects_wrong_policy_or_prior_attempt_id() -> None:
    document = json.loads(HTTP_ATTEMPT_PREIMAGE)
    document["policy"] = {"mode": "paid", "policy_version": "dataforseo-sandbox-v1"}
    with pytest.raises(DocumentError):
        validate_attempt(document)
    document = json.loads(HTTP_ATTEMPT_PREIMAGE)
    document["prior_attempt_id"] = HTTP_ATTEMPT_ID
    with pytest.raises(DocumentError):
        validate_attempt(document)


# ===========================================================================
# Response headers, omission, branches, failure table
# ===========================================================================


def test_response_headers_enforce_policy_denylist_order_and_omissions() -> None:
    ok = validate_capture(HTTP_CAPTURE_PREIMAGE)
    response = ok["response"]
    assert isinstance(response, dict)
    assert response["header_policy"] == "http-headers-v1"
    assert response["headers"] == [
        ["content-type", "application/json"],
        ["x-request-id", "sandbox-vector"],
    ]
    assert response["omitted_headers"] == [{"count": 1, "name": "set-cookie"}]


@pytest.mark.parametrize(
    "headers,omitted",
    [
        ([["Content-Type", "application/json"]], []),
        ([["authorization", "secret"]], []),
        ([["set-cookie", "sid=1"]], [{"count": 1, "name": "set-cookie"}]),
        ([["content-type", "application/json"]], [{"count": 1, "name": "content-type"}]),
        ([["content-type", "application/json"]], [{"count": 0, "name": "set-cookie"}]),
        ([["content-type", "application/json"]], [{"count": 1, "name": "x-unknown"}]),
        (
            [["content-type", "application/json"]],
            [{"count": 1, "name": "set-cookie"}, {"count": 1, "name": "cookie"}],
        ),
        (
            [["content-type", "application/json"]],
            [{"count": 1, "name": "set-cookie"}, {"count": 2, "name": "set-cookie"}],
        ),
        (
            [["content-type", "application/json"]],
            [{"count": 1, "name": "set-cookie", "value": "x"}],
        ),
    ],
)
def test_response_header_and_omission_boundaries_fail(
    headers: list[list[str]], omitted: list[dict[str, object]]
) -> None:
    document = json.loads(HTTP_CAPTURE_PREIMAGE)
    response = document["response"]
    assert isinstance(response, dict)
    response["headers"] = headers
    response["omitted_headers"] = omitted
    with pytest.raises(DocumentError):
        validate_capture(document)


def test_retained_response_headers_preserve_order_and_duplicates() -> None:
    document = json.loads(HTTP_CAPTURE_PREIMAGE)
    response = document["response"]
    assert isinstance(response, dict)
    response["headers"] = [
        ["content-type", "application/json"],
        ["x-request-id", "first"],
        ["x-request-id", "second"],
        ["content-type", "text/plain"],
    ]
    loaded = validate_capture(document)
    loaded_response = loaded["response"]
    assert isinstance(loaded_response, dict)
    assert loaded_response["headers"] == [
        ["content-type", "application/json"],
        ["x-request-id", "first"],
        ["x-request-id", "second"],
        ["content-type", "text/plain"],
    ]


def test_omitted_headers_must_be_uniquely_sorted_by_name() -> None:
    document = json.loads(HTTP_CAPTURE_PREIMAGE)
    response = document["response"]
    assert isinstance(response, dict)
    response["omitted_headers"] = [
        {"count": 1, "name": "set-cookie"},
        {"count": 2, "name": "authorization"},
    ]
    with pytest.raises(DocumentError):
        validate_capture(document)
    response["omitted_headers"] = [
        {"count": 2, "name": "authorization"},
        {"count": 1, "name": "set-cookie"},
    ]
    loaded = validate_capture(document)
    loaded_response = loaded["response"]
    assert isinstance(loaded_response, dict)
    assert loaded_response["omitted_headers"] == [
        {"count": 2, "name": "authorization"},
        {"count": 1, "name": "set-cookie"},
    ]


def test_complete_partial_and_no_response_branches() -> None:
    attempt = _http_attempt()
    complete = _http_complete_capture(attempt)
    assert complete["transport_state"] == "response_complete"
    assert complete["transport_failure"] is None

    partial = http_capture_document(
        attempt=attempt,
        request_started_at=HTTP_REQUEST_STARTED_AT,
        transport_ended_at=HTTP_TRANSPORT_ENDED_AT,
        transport_state="response_partial",
        response={
            "status": 200,
            "http_version": "HTTP/1.1",
            "header_policy": "http-headers-v1",
            "headers": [["content-type", "application/json"]],
            "omitted_headers": [],
            "body": {"state": "present_zero_bytes", "body": body_ref(b"")},
            "completeness": "partial",
        },
        transport_failure={"phase": "receive_body", "code": "timeout"},
        response_headers_at=HTTP_RESPONSE_HEADERS_AT,
        response_body_ended_at=HTTP_RESPONSE_BODY_ENDED_AT,
    )
    assert partial["transport_state"] == "response_partial"
    failure = partial["transport_failure"]
    assert isinstance(failure, dict)
    assert failure["phase"] == "receive_body"

    missing = http_capture_document(
        attempt=attempt,
        request_started_at=HTTP_REQUEST_STARTED_AT,
        transport_ended_at=HTTP_TRANSPORT_ENDED_AT,
        transport_state="no_response",
        response=None,
        transport_failure={"phase": "connect", "code": "connection_failed"},
        response_headers_at=None,
        response_body_ended_at=None,
    )
    assert missing["response"] is None
    no_response_failure = missing["transport_failure"]
    assert isinstance(no_response_failure, dict)
    assert no_response_failure["phase"] == "connect"


def test_complete_rejects_status_http_version_and_timestamp_gaps() -> None:
    attempt = _http_attempt()
    with pytest.raises(DocumentError):
        http_capture_document(
            attempt=attempt,
            request_started_at=HTTP_REQUEST_STARTED_AT,
            transport_ended_at=HTTP_TRANSPORT_ENDED_AT,
            transport_state="response_complete",
            response={**_complete_response(), "completeness": "partial"},
            transport_failure=None,
            response_headers_at=HTTP_RESPONSE_HEADERS_AT,
            response_body_ended_at=HTTP_RESPONSE_BODY_ENDED_AT,
        )
    document = json.loads(HTTP_CAPTURE_PREIMAGE)
    response = document["response"]
    assert isinstance(response, dict)
    response["status"] = 99
    with pytest.raises(DocumentError):
        validate_capture(document)
    response["status"] = 200
    response["http_version"] = "HTTP/3"
    with pytest.raises(DocumentError):
        validate_capture(document)
    document = json.loads(HTTP_CAPTURE_PREIMAGE)
    document["transport_failure"] = {"phase": "receive_body", "code": "timeout"}
    with pytest.raises(DocumentError):
        validate_capture(document)


def test_partial_requires_receive_body_failure_and_present_body() -> None:
    attempt = _http_attempt()
    present = {
        "status": 200,
        "http_version": "HTTP/1.1",
        "header_policy": "http-headers-v1",
        "headers": [["content-type", "application/json"]],
        "omitted_headers": [],
        "body": {"state": "present_nonempty", "body": body_ref(b"abc")},
        "completeness": "partial",
    }
    with pytest.raises(DocumentError):
        http_capture_document(
            attempt=attempt,
            request_started_at=HTTP_REQUEST_STARTED_AT,
            transport_ended_at=HTTP_TRANSPORT_ENDED_AT,
            transport_state="response_partial",
            response=present,
            transport_failure=None,
            response_headers_at=HTTP_RESPONSE_HEADERS_AT,
            response_body_ended_at=HTTP_RESPONSE_BODY_ENDED_AT,
        )
    with pytest.raises(DocumentError):
        http_capture_document(
            attempt=attempt,
            request_started_at=HTTP_REQUEST_STARTED_AT,
            transport_ended_at=HTTP_TRANSPORT_ENDED_AT,
            transport_state="response_partial",
            response=present,
            transport_failure={"phase": "connect", "code": "timeout"},
            response_headers_at=HTTP_RESPONSE_HEADERS_AT,
            response_body_ended_at=HTTP_RESPONSE_BODY_ENDED_AT,
        )
    absent = dict(present)
    absent["body"] = {"state": "absent"}
    with pytest.raises(DocumentError):
        http_capture_document(
            attempt=attempt,
            request_started_at=HTTP_REQUEST_STARTED_AT,
            transport_ended_at=HTTP_TRANSPORT_ENDED_AT,
            transport_state="response_partial",
            response=absent,
            transport_failure={"phase": "receive_body", "code": "read_failed"},
            response_headers_at=HTTP_RESPONSE_HEADERS_AT,
            response_body_ended_at=HTTP_RESPONSE_BODY_ENDED_AT,
        )


def test_no_response_rejects_receive_body_and_non_null_response() -> None:
    attempt = _http_attempt()
    with pytest.raises(DocumentError):
        http_capture_document(
            attempt=attempt,
            request_started_at=HTTP_REQUEST_STARTED_AT,
            transport_ended_at=HTTP_TRANSPORT_ENDED_AT,
            transport_state="no_response",
            response=None,
            transport_failure={"phase": "receive_body", "code": "timeout"},
            response_headers_at=None,
            response_body_ended_at=None,
        )
    with pytest.raises(DocumentError):
        http_capture_document(
            attempt=attempt,
            request_started_at=HTTP_REQUEST_STARTED_AT,
            transport_ended_at=HTTP_TRANSPORT_ENDED_AT,
            transport_state="no_response",
            response=_complete_response(),
            transport_failure={"phase": "connect", "code": "timeout"},
            response_headers_at=None,
            response_body_ended_at=None,
        )


@pytest.mark.parametrize(
    "phase,code,ok",
    [
        ("connect", "timeout", True),
        ("connect", "connection_failed", True),
        ("connect", "write_failed", False),
        ("connect", "read_failed", False),
        ("send_request", "timeout", True),
        ("send_request", "connection_failed", True),
        ("send_request", "write_failed", True),
        ("send_request", "protocol_failed", False),
        ("receive_headers", "timeout", True),
        ("receive_headers", "connection_failed", True),
        ("receive_headers", "protocol_failed", True),
        ("receive_headers", "read_failed", True),
        ("receive_headers", "write_failed", False),
        ("receive_body", "timeout", True),
        ("receive_body", "connection_failed", True),
        ("receive_body", "protocol_failed", True),
        ("receive_body", "read_failed", True),
        ("receive_body", "write_failed", False),
        ("receive_response", "fixture_no_response", False),
    ],
)
def test_http_failure_phase_code_table(phase: str, code: str, ok: bool) -> None:
    attempt = _http_attempt()
    state = "response_partial" if phase == "receive_body" else "no_response"
    kwargs: dict[str, Any] = {
        "attempt": attempt,
        "request_started_at": HTTP_REQUEST_STARTED_AT,
        "transport_ended_at": HTTP_TRANSPORT_ENDED_AT,
        "transport_state": state,
        "transport_failure": {"phase": phase, "code": code},
    }
    if state == "response_partial":
        kwargs["response"] = {
            "status": 200,
            "http_version": "HTTP/1.1",
            "header_policy": "http-headers-v1",
            "headers": [["content-type", "application/json"]],
            "omitted_headers": [],
            "body": {"state": "present_nonempty", "body": body_ref(b"x")},
            "completeness": "partial",
        }
        kwargs["response_headers_at"] = HTTP_RESPONSE_HEADERS_AT
        kwargs["response_body_ended_at"] = HTTP_RESPONSE_BODY_ENDED_AT
    else:
        kwargs["response"] = None
        kwargs["response_headers_at"] = None
        kwargs["response_body_ended_at"] = None
    if ok:
        document = http_capture_document(**kwargs)
        failure = document["transport_failure"]
        assert isinstance(failure, dict)
        assert failure["phase"] == phase
        assert failure["code"] == code
    else:
        with pytest.raises(DocumentError):
            http_capture_document(**kwargs)


@pytest.mark.parametrize(
    "key,value",
    [
        ("url", "https://sandbox.dataforseo.com/v3/serp/google/organic/live/advanced"),
        ("final_url", "https://sandbox.dataforseo.com/redirect"),
        ("redirect_chain", []),
        ("tasks", []),
        ("cost", 0),
        ("classification", "ok"),
        ("observations", []),
        ("authorization", "Basic x"),
    ],
)
def test_http_events_reject_forbidden_fields(key: str, value: object) -> None:
    attempt = json.loads(HTTP_ATTEMPT_PREIMAGE)
    attempt[key] = value
    with pytest.raises(DocumentError):
        validate_attempt(attempt)
    capture = json.loads(HTTP_CAPTURE_PREIMAGE)
    capture[key] = value
    with pytest.raises(DocumentError):
        validate_capture(capture)


def test_http_failure_rejects_free_text_message() -> None:
    document = json.loads(HTTP_CAPTURE_PREIMAGE)
    document["transport_state"] = "no_response"
    document["response"] = None
    document["response_headers_at"] = None
    document["response_body_ended_at"] = None
    document["transport_failure"] = {
        "phase": "connect",
        "code": "timeout",
        "message": "connection refused",
    }
    with pytest.raises(DocumentError):
        validate_capture(document)


# ===========================================================================
# Format-2 commit/read, tamper, mixed scrub
# ===========================================================================


def test_http_v2_commits_to_unchanged_v1_layouts_and_passes_d5(tmp_path: Path) -> None:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_http_complete(store)
    assert attempt_id == HTTP_ATTEMPT_ID
    assert capture_id == HTTP_CAPTURE_ID
    attempt_dir = store.attempt_path(HTTP_FINGERPRINT, HTTP_AUTHORIZED_AT, attempt_id)
    assert attempt_dir == (
        store.root
        / "attempts"
        / "v1"
        / HTTP_FINGERPRINT[:2]
        / HTTP_FINGERPRINT[2:4]
        / HTTP_FINGERPRINT
        / "2026"
        / "08"
        / "14"
        / HTTP_ATTEMPT_ID
    )
    capture_dir = store.capture_path(capture_id)
    shard_a = HTTP_CAPTURE_ID[:2]
    shard_b = HTTP_CAPTURE_ID[2:4]
    expected_capture = store.root / "captures" / "v1" / shard_a / shard_b / HTTP_CAPTURE_ID
    assert capture_dir == expected_capture
    loaded_attempt = store.read_attempt(attempt_id)
    loaded_capture = store.read_capture(capture_id)
    assert loaded_attempt is not None
    assert loaded_capture is not None
    assert loaded_attempt["version"] == 2
    assert loaded_capture["attempt_id"] == attempt_id
    request_bundle = attempt_dir / "request.body"
    response_bundle = capture_dir / "response.body"
    request_pool = store.object_path(HTTP_REQUEST_BODY_SHA256)
    response_pool = store.object_path(HTTP_RESPONSE_BODY_SHA256)
    assert request_bundle.read_bytes() == HTTP_REQUEST_BODY
    assert response_bundle.read_bytes() == HTTP_RESPONSE_BODY
    assert request_pool.read_bytes() == HTTP_REQUEST_BODY
    assert response_pool.read_bytes() == HTTP_RESPONSE_BODY
    assert request_bundle.stat().st_ino != request_pool.stat().st_ino
    assert response_bundle.stat().st_ino != response_pool.stat().st_ino
    assert store.read_capture_body(capture_id) == HTTP_RESPONSE_BODY
    format_bytes = (store.root / "FORMAT.json").read_bytes()
    assert b'"store_format":2' in format_bytes
    assert b'"attempt_bundle_layout":"v1"' in format_bytes
    assert b'"capture_bundle_layout":"v1"' in format_bytes


def test_tampered_committed_v2_manifest_and_body_are_integrity_failures(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_http_complete(store)
    attempt_dir = store.attempt_path(HTTP_FINGERPRINT, HTTP_AUTHORIZED_AT, attempt_id)
    capture_dir = store.capture_path(capture_id)

    raw = bytearray((attempt_dir / "attempt.json").read_bytes())
    raw[0] ^= 0x01
    (attempt_dir / "attempt.json").write_bytes(bytes(raw))
    with pytest.raises(IntegrityError):
        store.read_attempt(attempt_id)
    assert attempt_dir in scrub_store(store)

    store = create_store(tmp_path / "evidence-body")
    attempt_id, capture_id = _commit_http_complete(store)
    capture_dir = store.capture_path(capture_id)
    payload = bytearray((capture_dir / "response.body").read_bytes())
    payload[0] ^= 0x01
    (capture_dir / "response.body").write_bytes(bytes(payload))
    with pytest.raises(IntegrityError):
        store.read_capture(capture_id)
    assert capture_dir in scrub_store(store)


def test_mixed_store_scrubs_clean_and_unknown_version_is_failure(tmp_path: Path) -> None:
    store = create_store(tmp_path / "mixed")
    capture_fixture(store, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    _commit_http_complete(store)
    assert scrub_store(store) == []

    unknown = json.loads(HTTP_ATTEMPT_PREIMAGE)
    unknown["version"] = 3
    raw = canonical_json(unknown)
    event_id = content_digest(raw)
    bundle = store.root / "attempts" / "v1" / "ee" / "ee" / event_id
    bundle.mkdir(parents=True)
    (bundle / "attempt.json").write_bytes(raw)
    (bundle / "COMMITTED").write_bytes(f"{event_id}\n".encode())
    failed = scrub_store(store)
    assert bundle in failed


# ===========================================================================
# Mixed-store derive skip and API
# ===========================================================================


def test_mixed_store_derive_writes_only_fixture_rows(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    fixture_store = create_store(tmp_path / "fixture")
    fixture_outcome = capture_fixture(fixture_store, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    with connect(postgres_second_dsn) as baseline:
        baseline_summary = derive(fixture_store, baseline, DEFAULT_VERSION)
        baseline_counts = _row_counts(baseline)
        baseline_attempts, baseline_captures = _all_ids(baseline)
        baseline_versions = baseline.execute(
            "SELECT derivation_version_id, adapter_contract FROM derivation_versions"
        ).fetchall()
        baseline_outcomes = baseline.execute(
            """
            SELECT attempt_id, capture_id, derivation_version_id, classification,
                   observation_count
            FROM outcomes
            ORDER BY capture_id NULLS FIRST
            """
        ).fetchall()
        baseline_observations = baseline.execute(
            """
            SELECT capture_id, attempt_id, provider, panel_id, subject_key, result_index
            FROM observations
            ORDER BY result_index
            """
        ).fetchall()

    mixed = create_store(tmp_path / "mixed")
    mixed_fixture = capture_fixture(mixed, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    provider_attempt, provider_capture = _commit_http_complete(mixed)
    assert mixed_fixture.attempt_id == fixture_outcome.attempt_id
    with connect(postgres_dsn) as connection:
        summary = derive(mixed, connection, DEFAULT_VERSION)
        counts = _row_counts(connection)
        attempts, captures = _all_ids(connection)
        versions = connection.execute(
            "SELECT derivation_version_id, adapter_contract FROM derivation_versions"
        ).fetchall()
        outcomes = connection.execute(
            """
            SELECT attempt_id, capture_id, derivation_version_id, classification,
                   observation_count
            FROM outcomes
            ORDER BY capture_id NULLS FIRST
            """
        ).fetchall()
        observations = connection.execute(
            """
            SELECT capture_id, attempt_id, provider, panel_id, subject_key, result_index
            FROM observations
            ORDER BY result_index
            """
        ).fetchall()
        provider_outcome_rows = connection.execute(
            "SELECT count(*) FROM outcomes WHERE attempt_id = %s OR capture_id = %s",
            (provider_attempt, provider_capture),
        ).fetchone()
        provider_observation_rows = connection.execute(
            "SELECT count(*) FROM observations WHERE attempt_id = %s OR capture_id = %s",
            (provider_attempt, provider_capture),
        ).fetchone()
        provider_version_rows = connection.execute(
            "SELECT count(*) FROM derivation_versions WHERE adapter_contract = %s",
            (HTTP_ADAPTER,),
        ).fetchone()

    assert summary.integrity_failures == 0
    assert summary.attempt_outcomes == baseline_summary.attempt_outcomes
    assert summary.capture_outcomes == baseline_summary.capture_outcomes
    assert summary.observations == baseline_summary.observations
    assert counts == baseline_counts
    assert counts == {"derivation_versions": 1, "outcomes": 2, "observations": 2}
    assert attempts == baseline_attempts == {fixture_outcome.attempt_id}
    assert captures == baseline_captures == {fixture_outcome.capture_id}
    assert versions == baseline_versions == [(DEFAULT_VERSION, "fixture-panel-v1")]
    assert outcomes == baseline_outcomes
    assert observations == baseline_observations
    assert provider_outcome_rows == (0,)
    assert provider_observation_rows == (0,)
    assert provider_version_rows == (0,)
    assert provider_attempt not in attempts
    assert provider_capture not in captures


def test_fixture_api_unchanged_and_provider_attempt_is_404(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    fixture_store = create_store(tmp_path / "fixture")
    fixture_only = capture_fixture(fixture_store, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    with connect(postgres_second_dsn) as baseline:
        derive(fixture_store, baseline, DEFAULT_VERSION)
    with _app(fixture_store, postgres_second_dsn) as baseline_client:
        baseline_response = baseline_client.get(f"/v1/attempts/{fixture_only.attempt_id}")
    assert baseline_response.status_code == 200

    store = create_store(tmp_path / "mixed")
    fixture = capture_fixture(store, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    provider_attempt, _provider_capture = _commit_http_complete(store)
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
    with _app(store, postgres_dsn) as client:
        fixture_response = client.get(f"/v1/attempts/{fixture.attempt_id}")
        provider_response = client.get(f"/v1/attempts/{provider_attempt}")
    assert fixture_response.status_code == 200
    assert fixture_response.json() == baseline_response.json()
    body = fixture_response.json()
    assert body["attempt_id"] == PUBLISHED_AR_ATTEMPT_ID
    assert body["attempt_outcome"]["classification"] == "authorized_unresolved"
    assert body["capture_outcome"]["classification"] == "observation_admitted"
    assert body["capture_outcome"]["observation_count"] == 2
    assert len(body["observations"]) == 2
    assert provider_response.status_code == 404
    assert "attempt_outcome" not in provider_response.json()
    assert "observations" not in provider_response.json()
