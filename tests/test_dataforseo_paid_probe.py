"""PF-03: DataForSEO Keyword Overview paid probe constructors, gate, and inspect."""

from __future__ import annotations

import base64
import hashlib
import inspect
import json
import re
import socket
import threading
from collections.abc import Iterator, Mapping
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
import pytest

from observatory.capture import PUBLISHED_AR_INPUTS, capture_fixture
from observatory.capture_event import (
    HTTP_ADAPTER_CONTRACT,
    PAID_ADAPTER_CONTRACT,
    PAID_POLICY,
    DocumentError,
    body_ref,
    canonical_json,
    content_digest,
    http_attempt_document,
    http_capture_document,
    paid_http_attempt_document,
    paid_http_capture_document,
    paid_http_fingerprint_document,
    paid_http_request,
    validate_attempt,
    validate_capture,
    validate_fingerprint,
    validate_http_parameters,
    validate_http_request,
    validate_paid_http_parameters,
    validate_paid_http_request,
)
from observatory.dataforseo_paid_probe import (
    MAX_RESPONSE_BODY_BYTES,
    PaidProbeInputs,
    _exchange,
    _issue_verified_attempt,
    _run_gated_capture,
    _VerifiedAttempt,
    capture_dataforseo_paid_probe,
    closed_paid_parameters,
    inspect_paid_probe_body,
    main,
    paid_request_body_bytes,
)
from observatory.evidence import scrub_store
from observatory.evidence_store import EvidenceStore, StoreError, create_store, inspect_store
from observatory.settings import (
    DATAFORSEO_LOGIN_ENV,
    DATAFORSEO_PASSWORD_ENV,
    CredentialError,
    DataForSEOCredentials,
    Settings,
    load_dataforseo_credentials,
)

SENTINEL_LOGIN = "sentinel-login-pf03-cc33"
SENTINEL_PASSWORD = "sentinel-password-pf03-dd44"
SENTINEL_BASIC = "Basic " + base64.b64encode(
    f"{SENTINEL_LOGIN}:{SENTINEL_PASSWORD}".encode()
).decode("ascii")

PAID_KEYWORDS = (
    "seo api",
    "keyword research",
    "local seo",
    "generative engine optimization",
    "ai search optimization",
)
TEN_WORDS = "a b c d e f g h i j"
TEN_WORDS_REPEATED_SPACES = "a  b  c  d  e  f  g  h  i  j"
ELEVEN_WORDS = "a b c d e f g h i j k"
ELEVEN_WORDS_REPEATED_SPACES = "a  b  c  d  e  f  g  h  i  j  k"
PAID_NONCE = "4444444444444444444444444444444444444444444444444444444444444444"
PAID_AUTHORIZED_AT = "2026-08-16T16:00:00.000000Z"
PAID_REQUEST_STARTED_AT = "2026-08-16T16:00:00.100000Z"
PAID_RESPONSE_HEADERS_AT = "2026-08-16T16:00:00.200000Z"
PAID_RESPONSE_BODY_ENDED_AT = "2026-08-16T16:00:00.300000Z"
PAID_TRANSPORT_ENDED_AT = "2026-08-16T16:00:00.400000Z"
PAID_SOFTWARE = "conformance-paid-probe-v1"

PAID_REQUEST_BODY = (
    b'[{"include_clickstream_data":false,"include_serp_info":false,"keywords":'
    b'["seo api","keyword research","local seo","generative engine optimization",'
    b'"ai search optimization"],"language_code":"en","location_code":2840}]'
)
PAID_REQUEST_BODY_SHA256 = "3fc7205a55a1a5c464c0ae4ebca21a1e3088c2022565929a670fdf757ab7987b"
PAID_FINGERPRINT_PREIMAGE = (
    b'{"adapter_contract":"dataforseo-labs-google-keyword-overview-live-paid-probe-v1",'
    b'"provider":"dataforseo","request":{"body":{"body":{"bytes":216,"sha256":'
    b'"3fc7205a55a1a5c464c0ae4ebca21a1e3088c2022565929a670fdf757ab7987b"},'
    b'"state":"present_nonempty"},"headers":[["accept","application/json"],'
    b'["accept-encoding","identity"],["connection","close"],'
    b'["content-type","application/json"],["user-agent","observatory-dataforseo-v1"]],'
    b'"host":"api.dataforseo.com","method":"POST",'
    b'"path":"/v3/dataforseo_labs/google/keyword_overview/live","port":null,"query":[],'
    b'"scheme":"https"},"schema":"observatory.request-fingerprint","version":2}'
)
PAID_FINGERPRINT = "6cc5765911abe752a974d2fba268d927fdc055147c1286fffdfe0ee585cdc610"
PAID_ATTEMPT_PREIMAGE = (
    b'{"adapter_contract":"dataforseo-labs-google-keyword-overview-live-paid-probe-v1",'
    b'"attempt_nonce":"4444444444444444444444444444444444444444444444444444444444444444",'
    b'"authorized_at":"2026-08-16T16:00:00.000000Z",'
    b'"parameters":{"contract":"dataforseo-labs-google-keyword-overview-live-paid-probe-v1",'
    b'"include_clickstream_data":false,"include_serp_info":false,"keywords":'
    b'["seo api","keyword research","local seo","generative engine optimization",'
    b'"ai search optimization"],"language_code":"en","location_code":2840},'
    b'"policy":{"max_authorized_cost_micro_usd":20000,"mode":"paid_probe",'
    b'"policy_version":"dataforseo-paid-probe-v1",'
    b'"pricing_basis":"dataforseo-labs-google-live-2026-08-16"},"provider":"dataforseo",'
    b'"request":{"body":{"body":{"bytes":216,"sha256":'
    b'"3fc7205a55a1a5c464c0ae4ebca21a1e3088c2022565929a670fdf757ab7987b"},'
    b'"state":"present_nonempty"},"headers":[["accept","application/json"],'
    b'["accept-encoding","identity"],["connection","close"],'
    b'["content-type","application/json"],["user-agent","observatory-dataforseo-v1"]],'
    b'"host":"api.dataforseo.com","method":"POST",'
    b'"path":"/v3/dataforseo_labs/google/keyword_overview/live","port":null,"query":[],'
    b'"scheme":"https"},"request_fingerprint":'
    b'"6cc5765911abe752a974d2fba268d927fdc055147c1286fffdfe0ee585cdc610",'
    b'"schema":"observatory.attempt-event","software":'
    b'{"observatory_version":"conformance-paid-probe-v1"},"version":2}'
)
PAID_ATTEMPT_ID = "89904bf8a6812fb3d0d845310e4705962bb4db928b80da3be67342dff5def185"
PAID_RESPONSE_BODY = b'{"cost":0.0126,"tasks":[]}'
PAID_RESPONSE_BODY_SHA256 = "5b69c7675c3f03d95bb5071bf0da855e3a476521939dccd757d3295746cd33d1"
PAID_CAPTURE_PREIMAGE = (
    b'{"adapter_contract":"dataforseo-labs-google-keyword-overview-live-paid-probe-v1",'
    b'"attempt_id":"89904bf8a6812fb3d0d845310e4705962bb4db928b80da3be67342dff5def185",'
    b'"provider":"dataforseo","request":{"body":{"body":{"bytes":216,"sha256":'
    b'"3fc7205a55a1a5c464c0ae4ebca21a1e3088c2022565929a670fdf757ab7987b"},'
    b'"state":"present_nonempty"},"headers":[["accept","application/json"],'
    b'["accept-encoding","identity"],["connection","close"],'
    b'["content-type","application/json"],["user-agent","observatory-dataforseo-v1"]],'
    b'"host":"api.dataforseo.com","method":"POST",'
    b'"path":"/v3/dataforseo_labs/google/keyword_overview/live","port":null,"query":[],'
    b'"scheme":"https"},"request_fingerprint":'
    b'"6cc5765911abe752a974d2fba268d927fdc055147c1286fffdfe0ee585cdc610",'
    b'"request_started_at":"2026-08-16T16:00:00.100000Z","response":{"body":{"body":'
    b'{"bytes":26,"sha256":"5b69c7675c3f03d95bb5071bf0da855e3a476521939dccd757d3295746cd33d1"},'
    b'"state":"present_nonempty"},"completeness":"complete","header_policy":"http-headers-v1",'
    b'"headers":[["content-type","application/json"]],"http_version":"HTTP/1.1",'
    b'"omitted_headers":[],"status":200},"response_body_ended_at":'
    b'"2026-08-16T16:00:00.300000Z","response_headers_at":"2026-08-16T16:00:00.200000Z",'
    b'"schema":"observatory.capture-event","software":'
    b'{"observatory_version":"conformance-paid-probe-v1"},'
    b'"transport_ended_at":"2026-08-16T16:00:00.400000Z","transport_failure":null,'
    b'"transport_state":"response_complete","version":2}'
)
PAID_CAPTURE_ID = "dbaaf68a38e54e39d4fc03807d72eda37f8efd9a212220c0a99d270ddcec6917"

SANDBOX_REQUEST_BODY = (
    b'[{"depth":10,"device":"desktop","keyword":"observatory test",'
    b'"language_code":"en","location_code":2840,"os":"windows"}]'
)
SANDBOX_PARAMETERS: dict[str, Any] = {
    "contract": HTTP_ADAPTER_CONTRACT,
    "depth": 10,
    "device": "desktop",
    "keyword": "observatory test",
    "language_code": "en",
    "location_code": 2840,
    "os": "windows",
}
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
HTTP_ATTEMPT_ID = "22adc4841c86b7cd98b90bba683aeac204a0cb568428b590fd399e8627eb4640"

TIMESTAMP_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
DENYLIST = (
    "api-key",
    "authentication-info",
    "authorization",
    "cookie",
    "proxy-authentication-info",
    "proxy-authorization",
    "set-cookie",
    "x-access-token",
    "x-api-key",
    "x-auth-token",
)
AUTHORIZE = 20000


@pytest.fixture(autouse=True)
def _no_public_network(monkeypatch: pytest.MonkeyPatch) -> None:
    real = socket.create_connection

    def guarded(address: Any, *args: Any, **kwargs: Any) -> socket.socket:
        host = address[0] if isinstance(address, tuple) else address
        if host not in {"127.0.0.1", "::1"}:
            raise AssertionError(f"public-network request forbidden: {host}")
        return real(address, *args, **kwargs)

    monkeypatch.setattr(socket, "create_connection", guarded)


@pytest.fixture(autouse=True)
def _isolate_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(DATAFORSEO_LOGIN_ENV, raising=False)
    monkeypatch.delenv(DATAFORSEO_PASSWORD_ENV, raising=False)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _credentials() -> DataForSEOCredentials:
    return DataForSEOCredentials(SENTINEL_LOGIN, SENTINEL_PASSWORD)


def _inputs(
    *, keywords: tuple[str, ...] = PAID_KEYWORDS, nonce: str = PAID_NONCE
) -> PaidProbeInputs:
    return PaidProbeInputs(
        keywords=keywords,
        attempt_nonce=nonce,
        authorized_at=PAID_AUTHORIZED_AT,
        observatory_version=PAID_SOFTWARE,
    )


def _paid_parameters() -> dict[str, object]:
    return closed_paid_parameters(keywords=PAID_KEYWORDS)


def _paid_attempt() -> dict[str, object]:
    return paid_http_attempt_document(
        parameters=_paid_parameters(),
        attempt_nonce=PAID_NONCE,
        authorized_at=PAID_AUTHORIZED_AT,
        observatory_version=PAID_SOFTWARE,
    )


def _replacement_paid_body() -> bytes:
    return paid_request_body_bytes(
        closed_paid_parameters(keywords=("forged keyword",))
    )


def _replacement_paid_document() -> dict[str, object]:
    return paid_http_attempt_document(
        parameters=closed_paid_parameters(keywords=("forged keyword",)),
        attempt_nonce=PAID_NONCE,
        authorized_at=PAID_AUTHORIZED_AT,
        observatory_version=PAID_SOFTWARE,
    )


def _complete_response() -> dict[str, object]:
    return {
        "status": 200,
        "http_version": "HTTP/1.1",
        "header_policy": "http-headers-v1",
        "headers": [["content-type", "application/json"]],
        "omitted_headers": [],
        "body": {
            "state": "present_nonempty",
            "body": {"bytes": 26, "sha256": PAID_RESPONSE_BODY_SHA256},
        },
        "completeness": "complete",
    }


def _streamed_response(
    status: int,
    content: bytes,
    headers: list[tuple[str, str]] | None = None,
) -> httpx.Response:
    hdrs: list[tuple[str, str]] = list(headers or [])
    if not any(name.lower() == "content-length" for name, _ in hdrs):
        hdrs.append(("content-length", str(len(content))))
    return httpx.Response(status, headers=hdrs, stream=httpx.ByteStream(content))


def _mock_client(handler: Any) -> httpx.Client:
    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        trust_env=False,
        follow_redirects=False,
        timeout=httpx.Timeout(30.0),
    )
    client.headers.clear()
    return client


def _capture_mock(
    store: EvidenceStore,
    handler: Any,
    inputs: PaidProbeInputs | None = None,
    authorize: int = AUTHORIZE,
) -> Any:
    client = _mock_client(handler)
    try:
        return _run_gated_capture(
            store,
            inputs or _inputs(),
            _credentials(),
            authorize,
            client=client,
        )
    finally:
        client.close()


def _tree_bytes(root: Path) -> bytes:
    chunks: list[bytes] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            chunks.append(path.read_bytes())
    return b"\n".join(chunks)


def _tree_snapshot(root: Path) -> dict[str, tuple[int, int, bytes]]:
    snapshot: dict[str, tuple[int, int, bytes]] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            stat = path.stat()
            snapshot[str(path.relative_to(root))] = (stat.st_ino, stat.st_size, path.read_bytes())
    return snapshot


def _assert_no_secrets(*surfaces: object) -> None:
    for surface in surfaces:
        text = surface if isinstance(surface, str) else repr(surface)
        assert SENTINEL_LOGIN not in text
        assert SENTINEL_PASSWORD not in text
        assert SENTINEL_BASIC not in text
        assert SENTINEL_BASIC.removeprefix("Basic ") not in text


# ===========================================================================
# Independent paid vector and sandbox/v1 regression
# ===========================================================================


def test_independent_paid_vector_bytes_and_ids() -> None:
    assert len(PAID_REQUEST_BODY) == 216
    assert _sha256(PAID_REQUEST_BODY) == PAID_REQUEST_BODY_SHA256
    assert len(PAID_FINGERPRINT_PREIMAGE) == 622
    assert _sha256(PAID_FINGERPRINT_PREIMAGE) == PAID_FINGERPRINT
    assert len(PAID_ATTEMPT_PREIMAGE) == 1367
    assert _sha256(PAID_ATTEMPT_PREIMAGE) == PAID_ATTEMPT_ID
    assert len(PAID_RESPONSE_BODY) == 26
    assert _sha256(PAID_RESPONSE_BODY) == PAID_RESPONSE_BODY_SHA256
    assert len(PAID_CAPTURE_PREIMAGE) == 1433
    assert _sha256(PAID_CAPTURE_PREIMAGE) == PAID_CAPTURE_ID


def test_paid_constructors_reproduce_independent_vector() -> None:
    request = paid_http_request(body=PAID_REQUEST_BODY)
    fingerprint = paid_http_fingerprint_document(request=request)
    attempt = _paid_attempt()
    capture = paid_http_capture_document(
        attempt=attempt,
        request_started_at=PAID_REQUEST_STARTED_AT,
        transport_ended_at=PAID_TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response=_complete_response(),
        transport_failure=None,
        response_headers_at=PAID_RESPONSE_HEADERS_AT,
        response_body_ended_at=PAID_RESPONSE_BODY_ENDED_AT,
    )
    assert canonical_json(fingerprint) == PAID_FINGERPRINT_PREIMAGE
    assert content_digest(canonical_json(fingerprint)) == PAID_FINGERPRINT
    assert canonical_json(attempt) == PAID_ATTEMPT_PREIMAGE
    assert content_digest(canonical_json(attempt)) == PAID_ATTEMPT_ID
    assert canonical_json(capture) == PAID_CAPTURE_PREIMAGE
    assert content_digest(canonical_json(capture)) == PAID_CAPTURE_ID


def test_paid_preimages_revalidate() -> None:
    assert validate_fingerprint(PAID_FINGERPRINT_PREIMAGE)["adapter_contract"] == (
        PAID_ADAPTER_CONTRACT
    )
    assert validate_attempt(PAID_ATTEMPT_PREIMAGE)["version"] == 2
    assert validate_capture(PAID_CAPTURE_PREIMAGE)["version"] == 2
    assert canonical_json(validate_attempt(PAID_ATTEMPT_PREIMAGE)) == PAID_ATTEMPT_PREIMAGE
    assert canonical_json(validate_capture(PAID_CAPTURE_PREIMAGE)) == PAID_CAPTURE_PREIMAGE


def test_event_v1_and_sandbox_ids_remain_unchanged() -> None:
    assert content_digest(V1_AR_ATTEMPT) == V1_AR_ATTEMPT_ID
    loaded = validate_attempt(V1_AR_ATTEMPT)
    assert loaded["version"] == 1
    assert canonical_json(loaded) == V1_AR_ATTEMPT
    sandbox = http_attempt_document(
        parameters=SANDBOX_PARAMETERS,
        attempt_nonce="3333333333333333333333333333333333333333333333333333333333333333",
        authorized_at="2026-08-14T20:00:00.000000Z",
        observatory_version="conformance-http-v2",
    )
    assert content_digest(canonical_json(sandbox)) == HTTP_ATTEMPT_ID


# ===========================================================================
# Closed parameters, policy, confusion
# ===========================================================================


def test_closed_paid_parameters_and_independent_jcs_request_bytes() -> None:
    parameters = _paid_parameters()
    body = paid_request_body_bytes(parameters)
    assert body == PAID_REQUEST_BODY
    assert len(body) == 216
    assert _sha256(body) == PAID_REQUEST_BODY_SHA256
    task = json.loads(body)
    assert isinstance(task, list) and len(task) == 1
    assert "contract" not in task[0]
    assert task[0]["location_code"] == 2840
    assert task[0]["language_code"] == "en"
    assert task[0]["include_serp_info"] is False
    assert task[0]["include_clickstream_data"] is False
    assert task[0]["keywords"] == list(PAID_KEYWORDS)


def test_fresh_nonce_shape_and_timestamp_format() -> None:
    from observatory.dataforseo_paid_probe import _fresh_nonce, _utc_now

    nonce = _fresh_nonce()
    assert HEX64_RE.fullmatch(nonce)
    assert _fresh_nonce() != nonce
    assert TIMESTAMP_RE.fullmatch(_utc_now())


@pytest.mark.parametrize(
    "keywords",
    [
        (),
        ("a", "b", "c", "d", "e", "f"),
        ("seo api", "seo api"),
        ("",),
        ("x" * 81,),
        (" seo",),
        ("seo ",),
        ("-seo",),
        ("seo!",),
        ("seo@",),
        ("seo?",),
        ("s\teo",),
        ("sëo",),
        ("seo\n",),
    ],
)
def test_paid_keywords_reject_boundaries(keywords: tuple[str, ...]) -> None:
    with pytest.raises(DocumentError):
        closed_paid_parameters(keywords=keywords)


@pytest.mark.parametrize(
    "keyword",
    [
        "A",
        "z9",
        "seo & ads",
        "what's next",
        "geo (us) 1",
        "a+b",
        "a,b",
        "a.b",
        "a/b",
        "a:b",
        "a-b",
        "x" * 80,
    ],
)
def test_paid_keywords_accept_permitted_charset(keyword: str) -> None:
    parsed = closed_paid_parameters(keywords=(keyword,))
    assert parsed["keywords"] == [keyword]


def test_paid_keywords_accept_exactly_ten_simple_words() -> None:
    parsed = closed_paid_parameters(keywords=(TEN_WORDS,))
    assert parsed["keywords"] == [TEN_WORDS]


def test_paid_keywords_accept_exactly_ten_words_with_repeated_internal_spaces() -> None:
    parsed = closed_paid_parameters(keywords=(TEN_WORDS_REPEATED_SPACES,))
    assert parsed["keywords"] == [TEN_WORDS_REPEATED_SPACES]


def test_paid_keywords_reject_eleven_simple_words_below_eighty_characters() -> None:
    assert len(ELEVEN_WORDS) < 80
    with pytest.raises(DocumentError):
        closed_paid_parameters(keywords=(ELEVEN_WORDS,))


def test_paid_keywords_reject_eleven_words_with_repeated_spaces() -> None:
    assert len(ELEVEN_WORDS_REPEATED_SPACES) < 80
    with pytest.raises(DocumentError):
        closed_paid_parameters(keywords=(ELEVEN_WORDS_REPEATED_SPACES,))


def _manual_paid_parameters(*keywords: str) -> dict[str, object]:
    return {
        "contract": PAID_ADAPTER_CONTRACT,
        "include_clickstream_data": False,
        "include_serp_info": False,
        "keywords": list(keywords),
        "language_code": "en",
        "location_code": 2840,
    }


def _consistent_manual_paid_attempt(keyword: str) -> dict[str, object]:
    parameters = _manual_paid_parameters(keyword)
    task = {key: value for key, value in parameters.items() if key != "contract"}
    request = paid_http_request(body=canonical_json([task]))
    fingerprint = paid_http_fingerprint_document(request=request)
    return {
        "adapter_contract": PAID_ADAPTER_CONTRACT,
        "attempt_nonce": PAID_NONCE,
        "authorized_at": PAID_AUTHORIZED_AT,
        "parameters": parameters,
        "policy": dict(PAID_POLICY),
        "provider": "dataforseo",
        "request": request,
        "request_fingerprint": content_digest(canonical_json(fingerprint)),
        "schema": "observatory.attempt-event",
        "software": {"observatory_version": PAID_SOFTWARE},
        "version": 2,
    }


def test_document_validation_accepts_ten_word_keywords() -> None:
    ten = validate_paid_http_parameters(_manual_paid_parameters(TEN_WORDS))
    assert ten["keywords"] == [TEN_WORDS]
    spaced = validate_paid_http_parameters(_manual_paid_parameters(TEN_WORDS_REPEATED_SPACES))
    assert spaced["keywords"] == [TEN_WORDS_REPEATED_SPACES]
    attempt = validate_attempt(_consistent_manual_paid_attempt(TEN_WORDS))
    parameters = attempt["parameters"]
    assert isinstance(parameters, dict)
    assert parameters["keywords"] == [TEN_WORDS]


def test_document_validation_rejects_eleven_word_keywords() -> None:
    with pytest.raises(DocumentError):
        validate_paid_http_parameters(_manual_paid_parameters(ELEVEN_WORDS))
    with pytest.raises(DocumentError):
        validate_paid_http_parameters(_manual_paid_parameters(ELEVEN_WORDS_REPEATED_SPACES))
    with pytest.raises(DocumentError):
        validate_attempt(_consistent_manual_paid_attempt(ELEVEN_WORDS))
    with pytest.raises(DocumentError):
        validate_attempt(_consistent_manual_paid_attempt(ELEVEN_WORDS_REPEATED_SPACES))


@pytest.mark.parametrize("keyword", [TEN_WORDS, TEN_WORDS_REPEATED_SPACES])
def test_ten_word_public_capture_is_accepted(tmp_path: Path, keyword: str) -> None:
    store = create_store(tmp_path / "ten-word")
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, PAID_RESPONSE_BODY)

    outcome = _capture_mock(store, handler, inputs=_inputs(keywords=(keyword,)))
    assert len(calls) == 1
    assert store.list_committed_ids("attempts") == [outcome.attempt_id]
    assert store.list_committed_ids("captures") == [outcome.capture_id]


@pytest.mark.parametrize("keyword", [ELEVEN_WORDS, ELEVEN_WORDS_REPEATED_SPACES])
def test_eleven_word_public_capture_creates_no_attempt_handler_or_capture(
    tmp_path: Path, keyword: str
) -> None:
    store = create_store(tmp_path / "eleven-word")
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, PAID_RESPONSE_BODY)

    with pytest.raises(DocumentError):
        _capture_mock(store, handler, inputs=_inputs(keywords=(keyword,)))
    assert calls == []
    assert store.list_committed_ids("attempts") == []
    assert store.list_committed_ids("captures") == []


def test_confused_and_manual_paid_parameters_cannot_bypass_ten_word_limit() -> None:
    with pytest.raises(DocumentError):
        paid_http_attempt_document(
            parameters=_manual_paid_parameters(ELEVEN_WORDS),
            attempt_nonce=PAID_NONCE,
            authorized_at=PAID_AUTHORIZED_AT,
            observatory_version=PAID_SOFTWARE,
        )
    mixed = dict(_paid_parameters())
    mixed["keywords"] = [*PAID_KEYWORDS[:4], ELEVEN_WORDS]
    with pytest.raises(DocumentError):
        validate_paid_http_parameters(mixed)
    with pytest.raises(DocumentError):
        paid_http_attempt_document(
            parameters=mixed,
            attempt_nonce=PAID_NONCE,
            authorized_at=PAID_AUTHORIZED_AT,
            observatory_version=PAID_SOFTWARE,
        )
    confused = dict(_paid_parameters())
    confused["keywords"] = [ELEVEN_WORDS_REPEATED_SPACES]
    with pytest.raises(DocumentError):
        validate_paid_http_parameters(confused)
    document = json.loads(PAID_ATTEMPT_PREIMAGE)
    document["parameters"]["keywords"] = [ELEVEN_WORDS]
    with pytest.raises(DocumentError):
        validate_attempt(document)


def test_published_paid_request_vector_remains_byte_identical() -> None:
    body = paid_request_body_bytes(_paid_parameters())
    assert body == PAID_REQUEST_BODY
    assert len(body) == 216
    assert _sha256(body) == PAID_REQUEST_BODY_SHA256
    attempt = _paid_attempt()
    assert canonical_json(attempt) == PAID_ATTEMPT_PREIMAGE
    assert content_digest(canonical_json(attempt)) == PAID_ATTEMPT_ID
    assert content_digest(V1_AR_ATTEMPT) == V1_AR_ATTEMPT_ID
    sandbox = http_attempt_document(
        parameters=SANDBOX_PARAMETERS,
        attempt_nonce="3333333333333333333333333333333333333333333333333333333333333333",
        authorized_at="2026-08-14T20:00:00.000000Z",
        observatory_version="conformance-http-v2",
    )
    assert content_digest(canonical_json(sandbox)) == HTTP_ATTEMPT_ID


@pytest.mark.parametrize(
    "patch",
    [
        {"location_code": 2841},
        {"language_code": "de"},
        {"include_serp_info": True},
        {"include_clickstream_data": True},
        {"contract": HTTP_ADAPTER_CONTRACT},
        {"extra": 1},
    ],
)
def test_paid_parameters_reject_fixed_field_violations(patch: dict[str, object]) -> None:
    parameters = dict(_paid_parameters())
    if "extra" in patch:
        parameters["extra"] = patch["extra"]
    else:
        parameters.update(patch)
    with pytest.raises(DocumentError):
        validate_paid_http_parameters(parameters)


def test_sandbox_and_paid_validators_reject_confused_contracts() -> None:
    paid = dict(_paid_parameters())
    with pytest.raises(DocumentError):
        validate_http_parameters(paid)
    sandbox = dict(SANDBOX_PARAMETERS)
    with pytest.raises(DocumentError):
        validate_paid_http_parameters(sandbox)
    paid_request = paid_http_request(body=PAID_REQUEST_BODY)
    with pytest.raises(DocumentError):
        validate_http_request(paid_request)
    from observatory.capture_event import http_request

    sandbox_request = http_request(body=SANDBOX_REQUEST_BODY)
    with pytest.raises(DocumentError):
        validate_paid_http_request(sandbox_request)


def test_paid_request_rejects_sandbox_host_path_and_policy() -> None:
    request = dict(paid_http_request(body=PAID_REQUEST_BODY))
    request["host"] = "sandbox.dataforseo.com"
    with pytest.raises(DocumentError):
        validate_paid_http_request(request)
    request = dict(paid_http_request(body=PAID_REQUEST_BODY))
    request["path"] = "/v3/serp/google/organic/live/advanced"
    with pytest.raises(DocumentError):
        validate_paid_http_request(request)
    document = json.loads(PAID_ATTEMPT_PREIMAGE)
    document["policy"] = {"mode": "sandbox_no_spend", "policy_version": "dataforseo-sandbox-v1"}
    with pytest.raises(DocumentError):
        validate_attempt(document)
    document = json.loads(PAID_ATTEMPT_PREIMAGE)
    document["adapter_contract"] = HTTP_ADAPTER_CONTRACT
    with pytest.raises(DocumentError):
        validate_attempt(document)


# ===========================================================================
# Authorization and one-shot
# ===========================================================================


@pytest.mark.parametrize("value", [0, 1, 19999, 20001, -1])
def test_wrong_authorization_fails_before_attempt(tmp_path: Path, value: int) -> None:
    store = create_store(tmp_path / f"auth-{value}")
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, PAID_RESPONSE_BODY)

    with pytest.raises(StoreError, match="authorize-max-micro-usd 20000"):
        _capture_mock(store, handler, authorize=value)
    assert calls == []
    assert store.list_committed_ids("attempts") == []
    assert store.list_committed_ids("captures") == []


def test_issuer_requires_authorization_before_attempt_or_exchange(tmp_path: Path) -> None:
    store = create_store(tmp_path / "issuer-auth")
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, PAID_RESPONSE_BODY)

    client = _mock_client(handler)
    try:
        with pytest.raises(TypeError):
            _issue_verified_attempt(store, _paid_attempt(), PAID_REQUEST_BODY)
        with pytest.raises(TypeError, match="verified committed Attempt"):
            _exchange(object(), _credentials(), client=client)
    finally:
        client.close()
    assert calls == []
    assert store.list_committed_ids("attempts") == []
    assert store.list_committed_ids("captures") == []


@pytest.mark.parametrize(
    "value",
    [20000.0, "20000", Decimal("20000"), True, False, None, 0, 1, 19999, 20001, -1],
)
def test_issuer_rejects_malformed_and_wrong_authorization_before_attempt(
    tmp_path: Path, value: object
) -> None:
    store = create_store(tmp_path / f"issuer-{type(value).__name__}-{id(value)}")
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, PAID_RESPONSE_BODY)

    client = _mock_client(handler)
    try:
        with pytest.raises(StoreError, match="authorize-max-micro-usd 20000"):
            _issue_verified_attempt(
                store,
                _paid_attempt(),
                PAID_REQUEST_BODY,
                authorize_max_micro_usd=value,
            )
        with pytest.raises(TypeError, match="verified committed Attempt"):
            _exchange(object(), _credentials(), client=client)
    finally:
        client.close()
    assert calls == []
    assert store.list_committed_ids("attempts") == []
    assert store.list_committed_ids("captures") == []


@pytest.mark.parametrize(
    "value",
    [20000.0, "20000", Decimal("20000"), True, False, None],
)
def test_public_path_rejects_non_int_authorization_before_attempt(
    tmp_path: Path, value: object
) -> None:
    store = create_store(tmp_path / f"public-{type(value).__name__}")
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, PAID_RESPONSE_BODY)

    with pytest.raises(StoreError, match="authorize-max-micro-usd 20000"):
        _capture_mock(store, handler, authorize=value)  # type: ignore[arg-type]
    assert calls == []
    assert store.list_committed_ids("attempts") == []
    assert store.list_committed_ids("captures") == []


def test_exact_integer_20000_still_permits_mock_and_loopback(tmp_path: Path) -> None:
    store = create_store(tmp_path / "exact-int")
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return _streamed_response(200, PAID_RESPONSE_BODY)

    outcome = _capture_mock(store, handler, authorize=20000)
    assert calls["n"] == 1
    assert store.list_committed_ids("attempts") == [outcome.attempt_id]
    assert store.list_committed_ids("captures") == [outcome.capture_id]
    assert store.read_attempt(outcome.attempt_id) is not None
    assert store.read_capture(outcome.capture_id) is not None


def test_missing_authorization_cli_fails_before_attempt(tmp_path: Path) -> None:
    store = create_store(tmp_path / "cli-auth")
    with pytest.raises(SystemExit):
        main(
            [
                "capture",
                "--evidence-root",
                str(store.root),
                "--keyword",
                "seo api",
            ]
        )
    assert store.list_committed_ids("attempts") == []


def test_one_shot_refuses_second_paid_attempt_without_capture(tmp_path: Path) -> None:
    store = create_store(tmp_path / "oneshot")
    attempt = _paid_attempt()
    store.commit_attempt(attempt, request_body=PAID_REQUEST_BODY)
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, PAID_RESPONSE_BODY)

    with pytest.raises(StoreError, match="already has a committed paid-probe"):
        _capture_mock(
            store,
            handler,
            inputs=_inputs(nonce="5" * 64),
        )
    assert calls == []
    assert store.list_committed_ids("attempts") == [PAID_ATTEMPT_ID]
    assert store.list_committed_ids("captures") == []


def test_one_shot_allows_fixture_and_sandbox_neighbors(tmp_path: Path) -> None:
    store = create_store(tmp_path / "neighbors")
    capture_fixture(store, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    sandbox = http_attempt_document(
        parameters=SANDBOX_PARAMETERS,
        attempt_nonce="3333333333333333333333333333333333333333333333333333333333333333",
        authorized_at="2026-08-14T20:00:00.000000Z",
        observatory_version="conformance-http-v2",
    )
    store.commit_attempt(sandbox, request_body=SANDBOX_REQUEST_BODY)

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, PAID_RESPONSE_BODY)

    outcome = _capture_mock(store, handler)
    assert store.read_attempt(outcome.attempt_id) is not None
    assert store.read_capture(outcome.capture_id) is not None
    assert scrub_store(store) == []


# ===========================================================================
# Structural gate
# ===========================================================================


def test_forged_capability_cannot_reach_send() -> None:
    with pytest.raises(TypeError, match="cannot construct"):
        _VerifiedAttempt()
    forged: Any = object.__new__(_VerifiedAttempt)
    object.__setattr__(forged, "attempt_id", "0" * 64)
    object.__setattr__(forged, "document", {"adapter_contract": PAID_ADAPTER_CONTRACT})
    object.__setattr__(forged, "request_body", PAID_REQUEST_BODY)
    object.__setattr__(forged, "_used", False)
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(forged, _credentials())


def test_subclassed_store_cannot_issue(tmp_path: Path) -> None:
    class LyingStore(EvidenceStore):
        def commit_attempt(
            self, document: Mapping[str, object], *, request_body: bytes | None
        ) -> str:
            raise AssertionError("lying store must not commit")

    with pytest.raises(TypeError, match="concrete EvidenceStore"):
        _issue_verified_attempt(
            LyingStore(tmp_path / "lie"),
            _paid_attempt(),
            PAID_REQUEST_BODY,
            authorize_max_micro_usd=AUTHORIZE,
        )


def test_failed_commit_prevents_send(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = create_store(tmp_path / "evidence")
    sent: list[object] = []

    def boom(*_args: object, **_kwargs: object) -> str:
        raise StoreError("commit failed")

    def spy(*_args: object, **_kwargs: object) -> object:
        sent.append("sent")
        raise AssertionError("send must not run")

    monkeypatch.setattr(store, "commit_attempt", boom)
    monkeypatch.setattr("observatory.dataforseo_paid_probe._exchange", spy)
    with pytest.raises(StoreError, match="commit failed"):
        capture_dataforseo_paid_probe(store, _inputs(), _credentials(), AUTHORIZE)
    assert sent == []
    assert store.list_committed_ids("attempts") == []


def test_failed_readback_prevents_send(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = create_store(tmp_path / "evidence")
    sent: list[object] = []
    real_commit = store.commit_attempt

    def commit_then_hide(
        document: dict[str, object], *, request_body: bytes | None
    ) -> str:
        return real_commit(document, request_body=request_body)

    monkeypatch.setattr(store, "commit_attempt", commit_then_hide)
    monkeypatch.setattr(store, "read_attempt", lambda _id: None)

    def spy(*_args: object, **_kwargs: object) -> object:
        sent.append("sent")
        raise AssertionError("send must not run")

    monkeypatch.setattr("observatory.dataforseo_paid_probe._exchange", spy)
    with pytest.raises(StoreError, match="not readable"):
        capture_dataforseo_paid_probe(store, _inputs(), _credentials(), AUTHORIZE)
    assert sent == []


def test_wrong_adapter_sandbox_host_and_unknown_version_cannot_issue(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path / "evidence")
    sandbox = http_attempt_document(
        parameters=SANDBOX_PARAMETERS,
        attempt_nonce="3333333333333333333333333333333333333333333333333333333333333333",
        authorized_at="2026-08-14T20:00:00.000000Z",
        observatory_version="conformance-http-v2",
    )
    with pytest.raises((DocumentError, StoreError)):
        _issue_verified_attempt(
            store,
            sandbox,
            SANDBOX_REQUEST_BODY,
            authorize_max_micro_usd=AUTHORIZE,
        )
    paid = dict(_paid_attempt())
    paid["version"] = 3
    with pytest.raises((DocumentError, StoreError)):
        _issue_verified_attempt(
            store, paid, PAID_REQUEST_BODY, authorize_max_micro_usd=AUTHORIZE
        )
    fixture = validate_attempt(V1_AR_ATTEMPT)
    with pytest.raises((DocumentError, StoreError, TypeError)):
        _issue_verified_attempt(
            store, fixture, PAID_REQUEST_BODY, authorize_max_micro_usd=AUTHORIZE
        )
    assert store.list_committed_ids("attempts") == []


def test_issue_then_send_is_one_exchange(tmp_path: Path) -> None:
    store = create_store(tmp_path / "evidence")
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return _streamed_response(200, PAID_RESPONSE_BODY)

    outcome = _capture_mock(store, handler)
    assert calls["n"] == 1
    assert len(store.list_committed_ids("attempts")) == 1
    assert len(store.list_committed_ids("captures")) == 1
    assert store.read_attempt(outcome.attempt_id) is not None
    reuse_store = create_store(tmp_path / "reuse")
    verified = _issue_verified_attempt(
        reuse_store,
        paid_http_attempt_document(
            parameters=_paid_parameters(),
            attempt_nonce="5" * 64,
            authorized_at="2026-08-16T16:00:01.000000Z",
            observatory_version=PAID_SOFTWARE,
        ),
        PAID_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    client = _mock_client(handler)
    try:
        _exchange(verified, _credentials(), client=client)
        with pytest.raises(StoreError, match="one-exchange"):
            _exchange(verified, _credentials(), client=client)
    finally:
        client.close()


# ===========================================================================
# F13 closure-owned transport authority
# ===========================================================================


def test_issued_request_body_replacement_cannot_transport(tmp_path: Path) -> None:
    store = create_store(tmp_path / "issued-body")
    issued = _issue_verified_attempt(
        store,
        _paid_attempt(),
        PAID_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    replacement = _replacement_paid_body()
    assert replacement != PAID_REQUEST_BODY
    object.__setattr__(issued, "request_body", replacement)
    calls: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.content)
        raise AssertionError("handler must not run")

    client = _mock_client(handler)
    try:
        with pytest.raises(StoreError):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == []


def test_issued_document_replacement_cannot_transport(tmp_path: Path) -> None:
    store = create_store(tmp_path / "issued-doc")
    issued = _issue_verified_attempt(
        store,
        _paid_attempt(),
        PAID_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    replacement_document = _replacement_paid_document()
    replacement_body = _replacement_paid_body()
    assert replacement_document != _paid_attempt()
    validate_attempt(replacement_document)
    object.__setattr__(issued, "document", replacement_document)
    object.__setattr__(issued, "request_body", replacement_body)
    calls: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.content)
        raise AssertionError("handler must not run")

    client = _mock_client(handler)
    try:
        with pytest.raises(StoreError):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == []


def test_closure_owned_replay_protection_ignores_used_attribute(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path / "replay-used")
    issued = _issue_verified_attempt(
        store,
        _paid_attempt(),
        PAID_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    calls: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.content)
        return _streamed_response(200, PAID_RESPONSE_BODY)

    client = _mock_client(handler)
    try:
        first = _exchange(issued, _credentials(), client=client)
        object.__setattr__(issued, "_used", False)
        with pytest.raises(StoreError, match="one-exchange"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert first.transport_state == "response_complete"
    assert calls == [PAID_REQUEST_BODY]


def test_pre_send_verifies_committed_attempt_and_request_body(tmp_path: Path) -> None:
    replacement = _replacement_paid_body()
    evidence_store = create_store(tmp_path / "pre-send-evidence")
    evidence_issued = _issue_verified_attempt(
        evidence_store,
        _paid_attempt(),
        PAID_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    request = evidence_issued.document["request"]
    assert isinstance(request, Mapping)
    body_state = request["body"]
    assert isinstance(body_state, Mapping)
    body_ref = body_state["body"]
    assert isinstance(body_ref, Mapping)
    digest = body_ref["sha256"]
    assert isinstance(digest, str)
    bundle = evidence_store.attempt_path(
        str(evidence_issued.document["request_fingerprint"]),
        str(evidence_issued.document["authorized_at"]),
        evidence_issued.attempt_id,
    )
    pool = evidence_store.object_path(digest)
    bundle_body = bundle / "request.body"
    assert pool.is_file()
    assert bundle_body.read_bytes() == PAID_REQUEST_BODY
    assert pool.read_bytes() == PAID_REQUEST_BODY
    assert pool.stat().st_ino != bundle_body.stat().st_ino
    pool.write_bytes(replacement)
    assert bundle_body.read_bytes() == PAID_REQUEST_BODY
    evidence_calls: list[bytes] = []

    def evidence_handler(request: httpx.Request) -> httpx.Response:
        evidence_calls.append(request.content)
        raise AssertionError("handler must not run")

    evidence_client = _mock_client(evidence_handler)
    try:
        with pytest.raises(StoreError):
            _exchange(evidence_issued, _credentials(), client=evidence_client)
    finally:
        evidence_client.close()
    assert evidence_calls == []

    bundle_store = create_store(tmp_path / "pre-send-bundle")
    bundle_issued = _issue_verified_attempt(
        bundle_store,
        _paid_attempt(),
        PAID_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    bundle_only = bundle_store.attempt_path(
        str(bundle_issued.document["request_fingerprint"]),
        str(bundle_issued.document["authorized_at"]),
        bundle_issued.attempt_id,
    )
    (bundle_only / "request.body").write_bytes(replacement)
    bundle_calls: list[bytes] = []

    def bundle_handler(request: httpx.Request) -> httpx.Response:
        bundle_calls.append(request.content)
        raise AssertionError("handler must not run")

    bundle_client = _mock_client(bundle_handler)
    try:
        with pytest.raises(StoreError):
            _exchange(bundle_issued, _credentials(), client=bundle_client)
    finally:
        bundle_client.close()
    assert bundle_calls == []

    clean_store = create_store(tmp_path / "pre-send-clean")
    clean_issued = _issue_verified_attempt(
        clean_store,
        _paid_attempt(),
        PAID_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    clean_calls: list[bytes] = []

    def clean_handler(request: httpx.Request) -> httpx.Response:
        clean_calls.append(request.content)
        return _streamed_response(200, PAID_RESPONSE_BODY)

    clean_client = _mock_client(clean_handler)
    try:
        outcome = _exchange(clean_issued, _credentials(), client=clean_client)
        with pytest.raises(StoreError, match="one-exchange"):
            _exchange(clean_issued, _credentials(), client=clean_client)
    finally:
        clean_client.close()
    assert outcome.transport_state == "response_complete"
    assert clean_calls == [PAID_REQUEST_BODY]


def test_failed_pre_send_verification_consumes_issuance(tmp_path: Path) -> None:
    replacement = _replacement_paid_body()
    store = create_store(tmp_path / "failed-verify")
    issued = _issue_verified_attempt(
        store,
        _paid_attempt(),
        PAID_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    request = issued.document["request"]
    assert isinstance(request, Mapping)
    body_state = request["body"]
    assert isinstance(body_state, Mapping)
    body_ref = body_state["body"]
    assert isinstance(body_ref, Mapping)
    digest = body_ref["sha256"]
    assert isinstance(digest, str)
    bundle = store.attempt_path(
        str(issued.document["request_fingerprint"]),
        str(issued.document["authorized_at"]),
        issued.attempt_id,
    )
    pool = store.object_path(digest)
    bundle_body = bundle / "request.body"
    assert pool.is_file()
    assert bundle_body.read_bytes() == PAID_REQUEST_BODY
    assert pool.read_bytes() == PAID_REQUEST_BODY
    assert pool.stat().st_ino != bundle_body.stat().st_ino
    pool.write_bytes(replacement)
    assert bundle_body.read_bytes() == PAID_REQUEST_BODY
    calls: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.content)
        raise AssertionError("handler must not run")

    client = _mock_client(handler)
    try:
        with pytest.raises(StoreError):
            _exchange(issued, _credentials(), client=client)
        object.__setattr__(issued, "_used", False)
        with pytest.raises(StoreError, match="one-exchange"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == []


def test_endpoint_validation_failure_leaves_issuance_reusable(tmp_path: Path) -> None:
    store = create_store(tmp_path / "endpoint-reuse")
    issued = _issue_verified_attempt(
        store,
        _paid_attempt(),
        PAID_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    calls: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.content)
        return _streamed_response(200, PAID_RESPONSE_BODY)

    client = _mock_client(handler)
    try:
        with pytest.raises(StoreError, match="loopback"):
            _exchange(
                issued,
                _credentials(),
                endpoint=(
                    "https://api.dataforseo.com/v3/dataforseo_labs/"
                    "google/keyword_overview/live"
                ),
                client=client,
            )
        assert calls == []
        outcome = _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert outcome.transport_state == "response_complete"
    assert calls == [PAID_REQUEST_BODY]


def test_credential_validation_failure_leaves_issuance_reusable(tmp_path: Path) -> None:
    store = create_store(tmp_path / "credential-reuse")
    issued = _issue_verified_attempt(
        store,
        _paid_attempt(),
        PAID_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    emptied = _credentials()
    object.__setattr__(emptied, "_login", "")
    object.__setattr__(emptied, "_password", "")
    calls: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.content)
        return _streamed_response(200, PAID_RESPONSE_BODY)

    client = _mock_client(handler)
    try:
        with pytest.raises(CredentialError):
            _exchange(issued, emptied, client=client)
        assert calls == []
        outcome = _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert outcome.transport_state == "response_complete"
    assert calls == [PAID_REQUEST_BODY]


# ===========================================================================
# Headers, credentials, mock branches
# ===========================================================================


def test_mock_sent_headers_and_body_equation(tmp_path: Path) -> None:
    store = create_store(tmp_path / "evidence")
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return _streamed_response(200, PAID_RESPONSE_BODY)

    _capture_mock(store, handler)
    assert len(seen) == 1
    request = seen[0]
    assert bytes(request.content) == PAID_REQUEST_BODY
    items = [(k.lower(), v) for k, v in request.headers.multi_items()]
    names = [name for name, _ in items]
    assert ("accept", "application/json") in items
    assert ("accept-encoding", "identity") in items
    assert ("connection", "close") in items
    assert ("content-type", "application/json") in items
    assert ("user-agent", "observatory-dataforseo-v1") in items
    assert ("authorization", SENTINEL_BASIC) in items
    assert ("host", "api.dataforseo.com") in items
    assert ("content-length", str(len(PAID_REQUEST_BODY))) in items
    assert "transfer-encoding" not in names
    assert "cookie" not in names
    assert names.count("accept") == 1
    assert names.count("user-agent") == 1


def test_credentials_absent_from_evidence_stdout_repr_and_exceptions(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = create_store(tmp_path / "evidence")

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(
            200,
            PAID_RESPONSE_BODY,
            headers=[("set-cookie", "sid=secret"), ("authorization", SENTINEL_BASIC)],
        )

    outcome = _capture_mock(store, handler)
    tree = _tree_bytes(store.root)
    assert SENTINEL_LOGIN.encode() not in tree
    assert SENTINEL_PASSWORD.encode() not in tree
    assert SENTINEL_BASIC.encode() not in tree
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    response = capture["response"]
    assert isinstance(response, dict)
    assert ["authorization", SENTINEL_BASIC] not in response["headers"]
    creds = _credentials()
    _assert_no_secrets(creds, Settings(), load_dataforseo_credentials.__doc__)
    try:
        raise RuntimeError("transport exploded")
    except RuntimeError as exc:
        _assert_no_secrets(exc, repr(exc))
    captured = capsys.readouterr()
    _assert_no_secrets(captured.out, captured.err)


def test_missing_credentials_fail_before_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = create_store(tmp_path / "evidence")
    monkeypatch.delenv(DATAFORSEO_LOGIN_ENV, raising=False)
    with pytest.raises(CredentialError):
        load_dataforseo_credentials()
    code = main(
        [
            "capture",
            "--evidence-root",
            str(store.root),
            "--keyword",
            "seo api",
            "--authorize-max-micro-usd",
            "20000",
        ]
    )
    assert code == 2
    assert store.list_committed_ids("attempts") == []


def test_complete_nonempty_zero_byte_and_status_classes(tmp_path: Path) -> None:
    cases = (
        (200, PAID_RESPONSE_BODY),
        (200, b""),
        (302, b"moved"),
        (404, b"missing"),
        (500, b"failed"),
    )
    for index, (status, body) in enumerate(cases):
        store = create_store(tmp_path / f"case-{index}")

        def handler(
            request: httpx.Request, status: int = status, body: bytes = body
        ) -> httpx.Response:
            return _streamed_response(status, body)

        outcome = _capture_mock(store, handler, inputs=_inputs(nonce=f"{index:064x}"))
        capture = store.read_capture(outcome.capture_id)
        assert capture is not None
        assert capture["transport_state"] == "response_complete"
        assert capture["transport_failure"] is None
        response = capture["response"]
        assert isinstance(response, dict)
        assert response["status"] == status
        stored = store.read_capture_body(outcome.capture_id)
        assert stored == (body if body else b"")
        assert scrub_store(store) == []


def test_duplicate_retained_and_every_denylisted_header(tmp_path: Path) -> None:
    store = create_store(tmp_path / "evidence")
    secret_headers = [(name, f"secret-{name}") for name in DENYLIST]
    retained = [
        ("content-type", "application/json"),
        ("x-request-id", "one"),
        ("x-request-id", "two"),
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, PAID_RESPONSE_BODY, headers=retained + secret_headers)

    outcome = _capture_mock(store, handler)
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    response = capture["response"]
    assert isinstance(response, dict)
    assert ["x-request-id", "one"] in response["headers"]
    assert ["x-request-id", "two"] in response["headers"]
    assert response["omitted_headers"] == [{"count": 1, "name": name} for name in sorted(DENYLIST)]
    tree = _tree_bytes(store.root)
    for name in DENYLIST:
        assert f"secret-{name}".encode() not in tree


def test_connect_send_and_header_failures_are_no_response(tmp_path: Path) -> None:
    failures: list[BaseException] = [
        httpx.ConnectError("no"),
        httpx.ConnectTimeout("no"),
        httpx.WriteError("no"),
        httpx.WriteTimeout("no"),
        httpx.RemoteProtocolError("no"),
    ]
    for index, exc in enumerate(failures):
        store = create_store(tmp_path / f"fail-{index}")

        def handler(request: httpx.Request, exc: BaseException = exc) -> httpx.Response:
            raise exc

        outcome = _capture_mock(store, handler, inputs=_inputs(nonce=f"{index + 10:064x}"))
        capture = store.read_capture(outcome.capture_id)
        assert capture is not None
        assert capture["transport_state"] == "no_response"
        assert capture["response"] is None
        failure = capture["transport_failure"]
        assert isinstance(failure, dict)
        assert failure["phase"] != "receive_body"
        dumped = json.dumps(capture["transport_failure"])
        assert "no" not in dumped
        assert store.read_attempt(outcome.attempt_id) is not None
        assert scrub_store(store) == []


def test_partial_body_read_failure(tmp_path: Path) -> None:
    store = create_store(tmp_path / "partial")

    class _RaisingStream(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b'{"partial":'
            raise httpx.ReadError("cut")

    class PartialTransport(httpx.BaseTransport):
        def handle_request(self, request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                headers=[("content-type", "application/json")],
                stream=_RaisingStream(),
            )

    client = httpx.Client(
        transport=PartialTransport(),
        trust_env=False,
        follow_redirects=False,
        timeout=httpx.Timeout(30.0),
    )
    client.headers.clear()
    try:
        outcome = _run_gated_capture(
            store, _inputs(), _credentials(), AUTHORIZE, client=client
        )
    finally:
        client.close()
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["transport_state"] == "response_partial"
    failure = capture["transport_failure"]
    assert isinstance(failure, dict)
    assert failure["phase"] == "receive_body"
    assert store.read_capture_body(outcome.capture_id) == b'{"partial":'
    assert "cut" not in json.dumps(capture)


@pytest.mark.parametrize(
    ("size", "state"),
    [
        (MAX_RESPONSE_BODY_BYTES - 1, "response_complete"),
        (MAX_RESPONSE_BODY_BYTES, "response_complete"),
        (MAX_RESPONSE_BODY_BYTES + 1, "response_partial"),
    ],
)
def test_eight_mib_boundary(tmp_path: Path, size: int, state: str) -> None:
    store = create_store(tmp_path / f"bound-{size}")
    payload = b"x" * size

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, payload)

    outcome = _capture_mock(
        store,
        handler,
        inputs=_inputs(nonce=hashlib.sha256(str(size).encode()).hexdigest()),
    )
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["transport_state"] == state
    body = store.read_capture_body(outcome.capture_id)
    assert body is not None
    if state == "response_complete":
        assert len(body) == size
        assert capture["transport_failure"] is None
    else:
        assert len(body) == MAX_RESPONSE_BODY_BYTES
        failure = capture["transport_failure"]
        assert isinstance(failure, dict)
        assert failure == {"phase": "receive_body", "code": "read_failed"}


def test_credential_echo_in_body_commits_no_capture(tmp_path: Path) -> None:
    store = create_store(tmp_path / "echo-body")

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, SENTINEL_LOGIN.encode())

    with pytest.raises(StoreError) as raised:
        _capture_mock(store, handler)
    _assert_no_secrets(raised.value, repr(raised.value), str(raised.value))
    assert store.list_committed_ids("captures") == []
    assert len(store.list_committed_ids("attempts")) == 1


def test_credential_echo_in_retained_header_commits_no_capture(tmp_path: Path) -> None:
    store = create_store(tmp_path / "echo-header")
    token = SENTINEL_BASIC.removeprefix("Basic ")

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, PAID_RESPONSE_BODY, headers=[("x-echo", token)])

    with pytest.raises(StoreError) as raised:
        _capture_mock(store, handler)
    _assert_no_secrets(raised.value, repr(raised.value), str(raised.value))
    assert store.list_committed_ids("captures") == []
    assert len(store.list_committed_ids("attempts")) == 1


# ===========================================================================
# Loopback
# ===========================================================================


def _serve_once(response: bytes, recorded: dict[str, bytes]) -> tuple[int, threading.Thread]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 0))
    sock.listen(1)
    port = int(sock.getsockname()[1])

    def run() -> None:
        try:
            conn, _ = sock.accept()
            with conn:
                data = bytearray()
                while b"\r\n\r\n" not in data:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data.extend(chunk)
                header_blob, rest = data.split(b"\r\n\r\n", 1)
                length = 0
                for line in header_blob.split(b"\r\n"):
                    if line.lower().startswith(b"content-length:"):
                        length = int(line.split(b":", 1)[1].strip())
                body = bytearray(rest)
                while len(body) < length:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    body.extend(chunk)
                recorded["raw"] = bytes(header_blob) + b"\r\n\r\n" + bytes(body)
                conn.sendall(response)
        finally:
            sock.close()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return port, thread


def _parse_raw_request(raw: bytes) -> tuple[dict[str, list[str]], bytes]:
    header_blob, body = raw.split(b"\r\n\r\n", 1)
    headers: dict[str, list[str]] = {}
    for line in header_blob.split(b"\r\n")[1:]:
        name, value = line.split(b":", 1)
        key = name.decode("iso-8859-1").lower()
        headers.setdefault(key, []).append(value.decode("iso-8859-1").strip())
    return headers, body


def test_loopback_on_wire_headers_body_and_single_request(tmp_path: Path) -> None:
    store = create_store(tmp_path / "loopback")
    recorded: dict[str, bytes] = {}
    payload = PAID_RESPONSE_BODY
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/json\r\n"
        b"Content-Length: "
        + str(len(payload)).encode()
        + b"\r\n"
        b"Set-Cookie: sid=loop\r\n"
        b"\r\n"
        + payload
    )
    port, thread = _serve_once(response, recorded)
    endpoint = f"http://127.0.0.1:{port}/v3/dataforseo_labs/google/keyword_overview/live"
    outcome = _run_gated_capture(
        store, _inputs(), _credentials(), AUTHORIZE, endpoint=endpoint
    )
    thread.join(timeout=5)
    raw = recorded["raw"]
    headers, body = _parse_raw_request(raw)
    assert body == PAID_REQUEST_BODY
    assert headers["content-length"] == [str(len(PAID_REQUEST_BODY))]
    assert headers["accept"] == ["application/json"]
    assert headers["accept-encoding"] == ["identity"]
    assert headers["connection"] == ["close"]
    assert headers["content-type"] == ["application/json"]
    assert headers["user-agent"] == ["observatory-dataforseo-v1"]
    assert headers["authorization"] == [SENTINEL_BASIC]
    assert headers["host"] == [f"127.0.0.1:{port}"]
    assert set(headers) == {
        "accept",
        "accept-encoding",
        "authorization",
        "connection",
        "content-length",
        "content-type",
        "host",
        "user-agent",
    }
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["transport_state"] == "response_complete"
    assert store.read_capture_body(outcome.capture_id) == payload
    attempt = store.read_attempt(outcome.attempt_id)
    assert attempt is not None
    attempt_request = attempt["request"]
    assert isinstance(attempt_request, dict)
    assert attempt_request["host"] == "api.dataforseo.com"
    assert attempt_request["path"] == "/v3/dataforseo_labs/google/keyword_overview/live"
    assert scrub_store(store) == []
    assert SENTINEL_LOGIN.encode() not in _tree_bytes(store.root)


def test_loopback_redirect_is_complete_and_not_followed(tmp_path: Path) -> None:
    store = create_store(tmp_path / "redir")
    recorded: dict[str, bytes] = {}
    response = (
        b"HTTP/1.1 302 Found\r\n"
        b"Location: https://api.dataforseo.com/elsewhere\r\n"
        b"Content-Length: 0\r\n"
        b"\r\n"
    )
    port, thread = _serve_once(response, recorded)
    endpoint = f"http://127.0.0.1:{port}/v3/dataforseo_labs/google/keyword_overview/live"
    outcome = _run_gated_capture(
        store, _inputs(), _credentials(), AUTHORIZE, endpoint=endpoint
    )
    thread.join(timeout=5)
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["transport_state"] == "response_complete"
    response_obj = capture["response"]
    assert isinstance(response_obj, dict)
    assert response_obj["status"] == 302


def test_loopback_truncated_body_is_partial(tmp_path: Path) -> None:
    store = create_store(tmp_path / "trunc")
    recorded: dict[str, bytes] = {}
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/json\r\n"
        b"Content-Length: 80\r\n"
        b"\r\n"
        b'{"truncated":'
    )
    port, thread = _serve_once(response, recorded)
    endpoint = f"http://127.0.0.1:{port}/v3/dataforseo_labs/google/keyword_overview/live"
    outcome = _run_gated_capture(
        store, _inputs(), _credentials(), AUTHORIZE, endpoint=endpoint
    )
    thread.join(timeout=5)
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["transport_state"] == "response_partial"
    body = store.read_capture_body(outcome.capture_id)
    assert body == b'{"truncated":'


def _assert_endpoint_rejected(tmp_path: Path, endpoint: str) -> None:
    store = create_store(tmp_path / hashlib.sha256(endpoint.encode()).hexdigest()[:16])
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, PAID_RESPONSE_BODY)

    client = _mock_client(handler)
    try:
        with pytest.raises(StoreError):
            _run_gated_capture(
                store,
                _inputs(),
                _credentials(),
                AUTHORIZE,
                endpoint=endpoint,
                client=client,
            )
    finally:
        client.close()
    assert calls == []
    assert store.list_committed_ids("attempts") == []
    assert store.list_committed_ids("captures") == []


def test_sandbox_and_remote_endpoint_override_rejected_before_attempt(tmp_path: Path) -> None:
    _assert_endpoint_rejected(
        tmp_path, "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_overview/live"
    )
    _assert_endpoint_rejected(
        tmp_path, "http://127.0.0.1:9/v3/serp/google/organic/live/advanced"
    )
    _assert_endpoint_rejected(
        tmp_path, "https://example.invalid/v3/dataforseo_labs/google/keyword_overview/live"
    )


# ===========================================================================
# Inspect, CLI, public surface
# ===========================================================================


def test_each_branch_commits_one_verified_capture(tmp_path: Path) -> None:
    store = create_store(tmp_path / "evidence")

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, PAID_RESPONSE_BODY)

    outcome = _capture_mock(store, handler)
    assert store.list_committed_ids("attempts") == [outcome.attempt_id]
    assert store.list_committed_ids("captures") == [outcome.capture_id]
    assert store.read_capture_body(outcome.capture_id) == PAID_RESPONSE_BODY
    assert scrub_store(store) == []


def test_inspect_emits_exact_bytes_without_write_or_network(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = create_store(tmp_path / "inspect")
    attempt = _paid_attempt()
    store.commit_attempt(attempt, request_body=PAID_REQUEST_BODY)
    capture = paid_http_capture_document(
        attempt=attempt,
        request_started_at=PAID_REQUEST_STARTED_AT,
        transport_ended_at=PAID_TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response=_complete_response(),
        transport_failure=None,
        response_headers_at=PAID_RESPONSE_HEADERS_AT,
        response_body_ended_at=PAID_RESPONSE_BODY_ENDED_AT,
    )
    capture_id = store.commit_capture(capture, response_body=PAID_RESPONSE_BODY)
    before = _tree_snapshot(store.root)
    inspector = inspect_store(store.root)
    body = inspect_paid_probe_body(inspector, capture_id)
    assert body == PAID_RESPONSE_BODY
    code = main(
        ["inspect", "--evidence-root", str(store.root), "--capture-id", capture_id]
    )
    captured = capsys.readouterr()
    assert code == 0
    decoded = PAID_RESPONSE_BODY.decode()
    assert captured.out.encode() == PAID_RESPONSE_BODY or captured.out == decoded
    assert _tree_snapshot(store.root) == before
    assert SENTINEL_LOGIN not in captured.out
    assert SENTINEL_LOGIN not in captured.err


def test_inspect_rejects_wrong_adapter_partial_zero_and_tamper(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = create_store(tmp_path / "inspect-reject")
    sandbox = http_attempt_document(
        parameters=SANDBOX_PARAMETERS,
        attempt_nonce="3333333333333333333333333333333333333333333333333333333333333333",
        authorized_at="2026-08-14T20:00:00.000000Z",
        observatory_version="conformance-http-v2",
    )
    sandbox_id = store.commit_attempt(sandbox, request_body=SANDBOX_REQUEST_BODY)
    sandbox_capture = http_capture_document(
        attempt=sandbox,
        request_started_at="2026-08-14T20:00:00.100000Z",
        transport_ended_at="2026-08-14T20:00:00.400000Z",
        transport_state="response_complete",
        response={
            "status": 200,
            "http_version": "HTTP/1.1",
            "header_policy": "http-headers-v1",
            "headers": [["content-type", "application/json"]],
            "omitted_headers": [],
            "body": {
                "state": "present_nonempty",
                "body": {
                    "bytes": 26,
                    "sha256": PAID_RESPONSE_BODY_SHA256,
                },
            },
            "completeness": "complete",
        },
        transport_failure=None,
        response_headers_at="2026-08-14T20:00:00.200000Z",
        response_body_ended_at="2026-08-14T20:00:00.300000Z",
    )
    sandbox_capture_id = store.commit_capture(
        sandbox_capture, response_body=PAID_RESPONSE_BODY
    )
    paid = _paid_attempt()
    store.commit_attempt(paid, request_body=PAID_REQUEST_BODY)
    partial_body = b'{"partial":'
    partial = paid_http_capture_document(
        attempt=paid,
        request_started_at=PAID_REQUEST_STARTED_AT,
        transport_ended_at=PAID_TRANSPORT_ENDED_AT,
        transport_state="response_partial",
        response={
            "status": 200,
            "http_version": "HTTP/1.1",
            "header_policy": "http-headers-v1",
            "headers": [["content-type", "application/json"]],
            "omitted_headers": [],
            "body": {"state": "present_nonempty", "body": body_ref(partial_body)},
            "completeness": "partial",
        },
        transport_failure={"phase": "receive_body", "code": "read_failed"},
        response_headers_at=PAID_RESPONSE_HEADERS_AT,
        response_body_ended_at=PAID_RESPONSE_BODY_ENDED_AT,
    )
    partial_id = store.commit_capture(partial, response_body=partial_body)
    sibling = create_store(tmp_path / "inspect-no-response")
    no_response_attempt = paid_http_attempt_document(
        parameters=closed_paid_parameters(keywords=("seo api",)),
        attempt_nonce="6" * 64,
        authorized_at=PAID_AUTHORIZED_AT,
        observatory_version=PAID_SOFTWARE,
    )
    sibling.commit_attempt(
        no_response_attempt,
        request_body=paid_request_body_bytes(closed_paid_parameters(keywords=("seo api",))),
    )
    no_response = paid_http_capture_document(
        attempt=no_response_attempt,
        request_started_at=PAID_REQUEST_STARTED_AT,
        transport_ended_at=PAID_TRANSPORT_ENDED_AT,
        transport_state="no_response",
        response=None,
        transport_failure={"phase": "connect", "code": "connection_failed"},
        response_headers_at=None,
        response_body_ended_at=None,
    )
    no_response_id = sibling.commit_capture(no_response, response_body=None)
    with pytest.raises(StoreError):
        inspect_paid_probe_body(store, sandbox_capture_id)
    with pytest.raises(StoreError):
        inspect_paid_probe_body(store, partial_id)
    with pytest.raises(StoreError):
        inspect_paid_probe_body(sibling, no_response_id)
    with pytest.raises(StoreError):
        inspect_paid_probe_body(store, "0" * 64)
    with pytest.raises(StoreError):
        inspect_paid_probe_body(store, "GG" + "0" * 62)
    unknown = json.loads(PAID_CAPTURE_PREIMAGE)
    unknown["version"] = 3
    raw = canonical_json(unknown)
    unknown_id = content_digest(raw)
    bundle = store.capture_path(unknown_id)
    bundle.mkdir(parents=True)
    (bundle / "capture.json").write_bytes(raw)
    (bundle / "COMMITTED").write_bytes(f"{unknown_id}\n".encode())
    with pytest.raises(StoreError, match="invalid Evidence"):
        inspect_paid_probe_body(store, unknown_id)
    missing = main(
        ["inspect", "--evidence-root", str(store.root), "--capture-id", sandbox_capture_id]
    )
    captured = capsys.readouterr()
    assert missing == 1
    assert PAID_RESPONSE_BODY.decode() not in captured.out
    assert '{"partial":' not in captured.out
    assert sandbox_id in store.list_committed_ids("attempts")


def test_inspect_rejects_zero_body_and_tampered_evidence(tmp_path: Path) -> None:
    store = create_store(tmp_path / "zero")
    paid = paid_http_attempt_document(
        parameters=closed_paid_parameters(keywords=("seo api",)),
        attempt_nonce=PAID_NONCE,
        authorized_at=PAID_AUTHORIZED_AT,
        observatory_version=PAID_SOFTWARE,
    )
    request_body = paid_request_body_bytes(closed_paid_parameters(keywords=("seo api",)))
    store.commit_attempt(paid, request_body=request_body)
    empty = paid_http_capture_document(
        attempt=paid,
        request_started_at=PAID_REQUEST_STARTED_AT,
        transport_ended_at=PAID_TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response={
            "status": 200,
            "http_version": "HTTP/1.1",
            "header_policy": "http-headers-v1",
            "headers": [["content-type", "application/json"]],
            "omitted_headers": [],
            "body": {
                "state": "present_zero_bytes",
                "body": {
                    "bytes": 0,
                    "sha256": content_digest(b""),
                },
            },
            "completeness": "complete",
        },
        transport_failure=None,
        response_headers_at=PAID_RESPONSE_HEADERS_AT,
        response_body_ended_at=PAID_RESPONSE_BODY_ENDED_AT,
    )
    empty_id = store.commit_capture(empty, response_body=b"")
    with pytest.raises(StoreError):
        inspect_paid_probe_body(store, empty_id)

    other = create_store(tmp_path / "tamper")
    other_attempt = _paid_attempt()
    other.commit_attempt(other_attempt, request_body=PAID_REQUEST_BODY)
    complete = paid_http_capture_document(
        attempt=other_attempt,
        request_started_at=PAID_REQUEST_STARTED_AT,
        transport_ended_at=PAID_TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response=_complete_response(),
        transport_failure=None,
        response_headers_at=PAID_RESPONSE_HEADERS_AT,
        response_body_ended_at=PAID_RESPONSE_BODY_ENDED_AT,
    )
    capture_id = other.commit_capture(complete, response_body=PAID_RESPONSE_BODY)
    raw = bytearray((other.capture_path(capture_id) / "capture.json").read_bytes())
    raw[0] ^= 0x01
    (other.capture_path(capture_id) / "capture.json").write_bytes(bytes(raw))
    with pytest.raises(StoreError, match="invalid Evidence"):
        inspect_paid_probe_body(other, capture_id)


def test_cli_prints_only_ids(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    store_root = tmp_path / "cli"
    monkeypatch.setenv(DATAFORSEO_LOGIN_ENV, SENTINEL_LOGIN)
    monkeypatch.setenv(DATAFORSEO_PASSWORD_ENV, SENTINEL_PASSWORD)

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, PAID_RESPONSE_BODY)

    client = _mock_client(handler)

    def fake_run(
        store: EvidenceStore,
        inputs: PaidProbeInputs,
        credentials: DataForSEOCredentials,
        authorize_max_micro_usd: int,
    ) -> Any:
        return _run_gated_capture(
            store, inputs, credentials, authorize_max_micro_usd, client=client
        )

    monkeypatch.setattr(
        "observatory.dataforseo_paid_probe.capture_dataforseo_paid_probe", fake_run
    )
    code = main(
        [
            "capture",
            "--evidence-root",
            str(store_root),
            "--keyword",
            "seo api",
            "--keyword",
            "keyword research",
            "--authorize-max-micro-usd",
            "20000",
        ]
    )
    client.close()
    assert code == 0
    out = capsys.readouterr()
    assert out.out.startswith("attempt_id ")
    assert "capture_id " in out.out
    assert SENTINEL_LOGIN not in out.out
    assert SENTINEL_PASSWORD not in out.out
    assert PAID_RESPONSE_BODY.decode() not in out.out
    assert "cost" not in out.out


def test_cli_rejects_forbidden_arguments(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main(
            [
                "capture",
                "--evidence-root",
                str(tmp_path),
                "--keyword",
                "seo api",
                "--authorize-max-micro-usd",
                "20000",
                "--login",
                SENTINEL_LOGIN,
            ]
        )
    with pytest.raises(SystemExit):
        main(
            [
                "capture",
                "--evidence-root",
                str(tmp_path),
                "--keyword",
                "seo api",
                "--authorize-max-micro-usd",
                "20000",
                "--endpoint",
                "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_overview/live",
            ]
        )
    with pytest.raises(SystemExit):
        main(
            [
                "inspect",
                "--evidence-root",
                str(tmp_path),
                "--capture-id",
                "0" * 64,
                "--pretty",
            ]
        )


def test_public_api_has_no_url_or_header_injection() -> None:
    signature = inspect.signature(capture_dataforseo_paid_probe)
    assert "endpoint" not in signature.parameters
    assert "url" not in signature.parameters
    assert "headers" not in signature.parameters
    assert "client" not in signature.parameters
    assert "location" not in signature.parameters
    assert "language" not in signature.parameters
    inspect_sig = inspect.signature(inspect_paid_probe_body)
    assert "endpoint" not in inspect_sig.parameters
    assert "client" not in inspect_sig.parameters
