"""RK-01: Related Keywords Live paid-probe contract, hardened gate, and inspect.

Every test is credential-free and zero-network: sentinel credentials, mock or loopback
transport, and temporary Evidence Stores only. No DataForSEO request is ever made.
"""

from __future__ import annotations

import base64
import json
import socket
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

import httpx
import pytest

from observatory.capture import PUBLISHED_AR_INPUTS, capture_fixture
from observatory.capture_event import (
    HTTP_ADAPTER_CONTRACT,
    ORGANIC_ADAPTER_CONTRACT,
    PAID_ADAPTER_CONTRACT,
    RELATED_KEYWORDS_ADAPTER_CONTRACT,
    RELATED_KEYWORDS_AUTHORIZED_COST_MICRO_USD,
    RELATED_KEYWORDS_HOST,
    RELATED_KEYWORDS_PATH,
    DocumentError,
    canonical_json,
    content_digest,
    organic_http_attempt_document,
    organic_http_capture_document,
    paid_http_attempt_document,
    related_keywords_http_attempt_document,
    related_keywords_http_capture_document,
    related_keywords_http_fingerprint_document,
    related_keywords_http_request,
    validate_attempt,
    validate_related_keywords_http_parameters,
    validate_related_keywords_http_request,
)
from observatory.dataforseo_google_organic_paid_probe import (
    _exchange as organic_exchange,
)
from observatory.dataforseo_google_organic_paid_probe import (
    _issue_verified_attempt as issue_organic,
)
from observatory.dataforseo_google_organic_paid_probe import (
    closed_organic_parameters,
    organic_request_body_bytes,
)
from observatory.dataforseo_google_related_keywords_paid_probe import (
    _TIMEOUT,
    MAX_RESPONSE_BODY_BYTES,
    RelatedKeywordsPaidProbeInputs,
    _committed_attempt,
    _exchange,
    _issue_verified_attempt,
    _run_gated_capture,
    _VerifiedAttempt,
    capture_dataforseo_google_related_keywords_paid_probe,
    closed_related_keywords_parameters,
    inspect_related_keywords_paid_probe_body,
    main,
    related_keywords_request_body_bytes,
)
from observatory.dataforseo_paid_probe import (
    _exchange as paid_exchange,
)
from observatory.dataforseo_paid_probe import (
    _issue_verified_attempt as issue_paid,
)
from observatory.dataforseo_paid_probe import (
    closed_paid_parameters,
    paid_request_body_bytes,
)
from observatory.derive import DEFAULT_VERSION, derive
from observatory.evidence import scrub_store
from observatory.evidence_store import EvidenceStore, StoreError, create_store, inspect_store
from observatory.keyword_overview_derive import derive_keyword_overview
from observatory.migrate import connect
from observatory.settings import (
    DATAFORSEO_LOGIN_ENV,
    DATAFORSEO_PASSWORD_ENV,
    CredentialError,
    DataForSEOCredentials,
)

SENTINEL_LOGIN = "sentinel-login-rk01-mm11"
SENTINEL_PASSWORD = "sentinel-password-rk01-nn22"
SENTINEL_BASIC = "Basic " + base64.b64encode(
    f"{SENTINEL_LOGIN}:{SENTINEL_PASSWORD}".encode()
).decode("ascii")
AUTHORIZE = 200000
KEYWORD = "conspiracy theories"
ALT_KEYWORD = "flat earth"
NONCE = "6666666666666666666666666666666666666666666666666666666666666666"
AUTHORIZED_AT = "2026-08-28T20:00:00.000000Z"
SOFTWARE = "conformance-related-keywords-paid-probe-v1"
REQUEST_STARTED_AT = "2026-08-28T20:00:00.100000Z"
RESPONSE_HEADERS_AT = "2026-08-28T20:00:00.200000Z"
RESPONSE_BODY_ENDED_AT = "2026-08-28T20:00:00.300000Z"
TRANSPORT_ENDED_AT = "2026-08-28T20:00:00.400000Z"

# Independent literals. Written by hand from the closed RK-01 contract, NOT derived from
# any production constructor. The production path must reproduce these exactly.
RK_REQUEST_BODY = (
    b'[{"depth":3,"ignore_synonyms":false,"include_clickstream_data":false,'
    b'"include_seed_keyword":true,"include_serp_info":true,'
    b'"keyword":"conspiracy theories","language_code":"en","limit":1000,'
    b'"location_code":2840,"offset":0,'
    b'"order_by":["keyword_data.keyword_info.search_volume,desc"],'
    b'"replace_with_core_keyword":false}]'
)
RK_REQUEST_BODY_SHA256 = "cf6e74c5ee61c617145fc6e4901046056779815dd3d3dbf154e604a53702bdc1"
RK_FINGERPRINT = "a766fbbd886e720b4af1ab2016e0b86bcf54a1d2dfb62300e009649f9982b10e"
RK_ATTEMPT_ID = "5a673a457e994be7fa432f755a1ff8bd7df65a0da9d2c9a5aa35c309a26e9fc6"
RK_RESPONSE_BODY = b'{"cost":0.082}'
RK_RESPONSE_BODY_SHA256 = content_digest(RK_RESPONSE_BODY)
# Existing accepted adapter vectors that must remain byte-identical.
ORGANIC_ATTEMPT_ID = "b577bc1fb75f4ba7576a96c1328fbe74df9d975f3bd03f6c01d7441dfed1a1be"
PAID_ATTEMPT_ID = "89904bf8a6812fb3d0d845310e4705962bb4db928b80da3be67342dff5def185"
SMALL_LIMIT = 16
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


def _credentials() -> DataForSEOCredentials:
    return DataForSEOCredentials(SENTINEL_LOGIN, SENTINEL_PASSWORD)


def _inputs(
    keyword: str = KEYWORD,
    *,
    nonce: str = NONCE,
    authorized_at: str = AUTHORIZED_AT,
) -> RelatedKeywordsPaidProbeInputs:
    return RelatedKeywordsPaidProbeInputs(
        keyword=keyword,
        attempt_nonce=nonce,
        authorized_at=authorized_at,
        observatory_version=SOFTWARE,
    )


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
    inputs: RelatedKeywordsPaidProbeInputs | None = None,
    *,
    authorize: object = AUTHORIZE,
    max_response_body_bytes: int | None = None,
) -> Any:
    client = _mock_client(handler)
    try:
        return _run_gated_capture(
            store,
            inputs or _inputs(),
            _credentials(),
            authorize,  # type: ignore[arg-type]
            client=client,
            max_response_body_bytes=max_response_body_bytes,
        )
    finally:
        client.close()


def _complete_response(body: bytes = RK_RESPONSE_BODY) -> dict[str, object]:
    return {
        "status": 200,
        "http_version": "HTTP/1.1",
        "header_policy": "http-headers-v1",
        "headers": [["content-type", "application/json"]],
        "omitted_headers": [],
        "body": {
            "state": "present_nonempty",
            "body": {"bytes": len(body), "sha256": content_digest(body)},
        },
        "completeness": "complete",
    }


def _rk_attempt(keyword: str = KEYWORD, *, nonce: str = NONCE) -> dict[str, object]:
    return related_keywords_http_attempt_document(
        parameters=closed_related_keywords_parameters(keyword=keyword),
        attempt_nonce=nonce,
        authorized_at=AUTHORIZED_AT,
        observatory_version=SOFTWARE,
    )


def _issue_rk(store: EvidenceStore, keyword: str = KEYWORD) -> Any:
    return _issue_verified_attempt(
        store,
        _rk_attempt(keyword),
        related_keywords_request_body_bytes(
            closed_related_keywords_parameters(keyword=keyword)
        ),
        authorize_max_micro_usd=AUTHORIZE,
    )


def _refusing_client() -> tuple[httpx.Client, list[bytes]]:
    calls: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.content)
        raise AssertionError("handler must not run")

    return _mock_client(handler), calls


def _sending_client(body: bytes = RK_RESPONSE_BODY) -> tuple[httpx.Client, list[bytes]]:
    calls: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.content)
        return _streamed_response(200, body)

    return _mock_client(handler), calls


def _attempt_bundle(store: EvidenceStore, issued: Any) -> Path:
    return store.attempt_path(
        str(issued.document["request_fingerprint"]),
        str(issued.document["authorized_at"]),
        issued.attempt_id,
    )


def _request_body_digest(issued: Any) -> str:
    request = issued.document["request"]
    assert isinstance(request, Mapping)
    body_state = request["body"]
    assert isinstance(body_state, Mapping)
    body_ref = body_state["body"]
    assert isinstance(body_ref, Mapping)
    digest = body_ref["sha256"]
    assert isinstance(digest, str)
    return digest


def _assert_no_secrets(*surfaces: object) -> None:
    for surface in surfaces:
        text = surface if isinstance(surface, str) else repr(surface)
        assert SENTINEL_LOGIN not in text
        assert SENTINEL_PASSWORD not in text
        assert SENTINEL_BASIC not in text


# --- closed contract, vector, and identity ----------------------------------


def test_closed_request_vector_and_attempt_identity() -> None:
    parameters = closed_related_keywords_parameters(keyword=KEYWORD)
    body = related_keywords_request_body_bytes(parameters)
    assert body == RK_REQUEST_BODY
    assert len(body) == 315
    assert content_digest(body) == RK_REQUEST_BODY_SHA256
    attempt = _rk_attempt()
    request = attempt["request"]
    assert isinstance(request, Mapping)
    fingerprint = related_keywords_http_fingerprint_document(request=request)
    assert content_digest(canonical_json(fingerprint)) == RK_FINGERPRINT
    assert attempt["request_fingerprint"] == RK_FINGERPRINT
    assert content_digest(canonical_json(attempt)) == RK_ATTEMPT_ID
    task = json.loads(body)
    assert isinstance(task, list) and len(task) == 1
    assert "contract" not in task[0]
    assert parameters["contract"] == RELATED_KEYWORDS_ADAPTER_CONTRACT


def test_every_closed_request_value_is_exact() -> None:
    task = json.loads(RK_REQUEST_BODY)[0]
    assert task == {
        "depth": 3,
        "ignore_synonyms": False,
        "include_clickstream_data": False,
        "include_seed_keyword": True,
        "include_serp_info": True,
        "keyword": KEYWORD,
        "language_code": "en",
        "limit": 1000,
        "location_code": 2840,
        "offset": 0,
        "order_by": ["keyword_data.keyword_info.search_volume,desc"],
        "replace_with_core_keyword": False,
    }
    for flag in ("ignore_synonyms", "include_clickstream_data", "replace_with_core_keyword"):
        assert task[flag] is False
    for flag in ("include_seed_keyword", "include_serp_info"):
        assert task[flag] is True
    assert "filters" not in task
    assert "tag" not in task


def test_alternate_contract_values_fail_closed() -> None:
    base = dict(closed_related_keywords_parameters(keyword=KEYWORD))
    mutations: list[dict[str, object]] = [
        {"depth": 1},
        {"depth": 4},
        {"depth": True},
        {"limit": 100},
        {"limit": 1001},
        {"offset": 100},
        {"offset": True},
        {"location_code": 2826},
        {"location_code": True},
        {"language_code": "de"},
        {"include_seed_keyword": False},
        {"include_serp_info": False},
        {"include_clickstream_data": True},
        {"ignore_synonyms": True},
        {"replace_with_core_keyword": True},
        {"order_by": []},
        {"order_by": ["keyword_data.keyword_info.cpc,desc"]},
        {"order_by": "keyword_data.keyword_info.search_volume,desc"},
        {"order_by": ["keyword_data.keyword_info.search_volume,desc", "x,desc"]},
        {"filters": []},
        {"tag": "rk"},
        {"unknown_key": 1},
    ]
    for mutation in mutations:
        candidate = dict(base)
        candidate.update(mutation)
        with pytest.raises(DocumentError):
            validate_related_keywords_http_parameters(candidate)
    for missing in base:
        candidate = {key: value for key, value in base.items() if key != missing}
        with pytest.raises(DocumentError):
            validate_related_keywords_http_parameters(candidate)


@pytest.mark.parametrize(
    "keyword",
    [
        KEYWORD,
        ALT_KEYWORD,
        "a",
        "seo & geo",
        "o'brien",
        "n/a coverage",
        "site:example.com",
        "x" * 80,
        "one two three four five six seven eight nine ten",
    ],
)
def test_seed_grammar_accepts_ordinary_queries(keyword: str) -> None:
    parameters = closed_related_keywords_parameters(keyword=keyword)
    assert parameters["keyword"] == keyword


@pytest.mark.parametrize(
    "keyword",
    [
        "",
        " leading",
        "trailing ",
        "-leading",
        "trailing-",
        "x" * 81,
        "one two three four five six seven eight nine ten eleven",
        "emoji \U0001f600",
        "tab\tsep",
        "new\nline",
        "semi;colon",
        "star*",
        "quote\"mark",
        "under_score",
    ],
)
def test_seed_grammar_rejects_invalid_shapes(keyword: str) -> None:
    with pytest.raises(DocumentError):
        closed_related_keywords_parameters(keyword=keyword)


def test_seed_grammar_rejects_non_string() -> None:
    base = dict(closed_related_keywords_parameters(keyword=KEYWORD))
    for value in (None, 5, True, ["a"], {"a": 1}):
        candidate = dict(base)
        candidate["keyword"] = value
        with pytest.raises(DocumentError):
            validate_related_keywords_http_parameters(candidate)


def test_request_object_is_the_closed_related_keywords_target() -> None:
    request = related_keywords_http_request(body=RK_REQUEST_BODY)
    assert request["host"] == RELATED_KEYWORDS_HOST
    assert request["path"] == RELATED_KEYWORDS_PATH
    assert request["method"] == "POST"
    assert request["scheme"] == "https"
    assert request["port"] is None
    assert request["query"] == []
    validate_related_keywords_http_request(request)
    with pytest.raises(DocumentError):
        related_keywords_http_request(body=b"")
    wrong_path = dict(request)
    wrong_path["path"] = "/v3/dataforseo_labs/google/keyword_overview/live"
    with pytest.raises(DocumentError):
        validate_related_keywords_http_request(wrong_path)


def test_existing_adapter_identities_unchanged() -> None:
    organic_parameters = closed_organic_parameters(keyword="observatory test")
    organic = organic_http_attempt_document(
        parameters=organic_parameters,
        attempt_nonce="5" * 64,
        authorized_at="2026-08-18T20:00:00.000000Z",
        observatory_version="conformance-google-organic-paid-probe-v1",
    )
    assert content_digest(canonical_json(organic)) == ORGANIC_ATTEMPT_ID
    paid_parameters = closed_paid_parameters(
        keywords=(
            "seo api",
            "keyword research",
            "local seo",
            "generative engine optimization",
            "ai search optimization",
        )
    )
    paid = paid_http_attempt_document(
        parameters=paid_parameters,
        attempt_nonce="4" * 64,
        authorized_at="2026-08-16T16:00:00.000000Z",
        observatory_version="conformance-paid-probe-v1",
    )
    assert content_digest(canonical_json(paid)) == PAID_ATTEMPT_ID
    assert RELATED_KEYWORDS_ADAPTER_CONTRACT not in {
        HTTP_ADAPTER_CONTRACT,
        PAID_ADAPTER_CONTRACT,
        ORGANIC_ADAPTER_CONTRACT,
    }


def test_adapter_owns_32mib_and_120s_read_timeout() -> None:
    assert MAX_RESPONSE_BODY_BYTES == 33_554_432
    assert _TIMEOUT.connect == 30.0
    assert _TIMEOUT.read == 120.0
    assert _TIMEOUT.write == 30.0
    assert _TIMEOUT.pool == 30.0
    assert RELATED_KEYWORDS_AUTHORIZED_COST_MICRO_USD == 200000
    policy = validate_attempt(_rk_attempt())["policy"]
    assert isinstance(policy, Mapping)
    assert policy["max_authorized_cost_micro_usd"] == 200000
    assert policy["pricing_basis"] == "dataforseo-labs-google-related-keywords-live-2026-08-28"


# --- authorization and store gates ------------------------------------------


def test_authorization_required_before_attempt(tmp_path: Path) -> None:
    store = create_store(tmp_path / "auth")
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, RK_RESPONSE_BODY)

    for value in (0, 20000, 199999, 200001, True, 200000.0, "200000", None):
        with pytest.raises(StoreError, match="authorize-max-micro-usd 200000"):
            _capture_mock(store, handler, authorize=value)
    assert calls == []
    assert store.list_committed_ids("attempts") == []


def test_concrete_store_required_before_attempt(tmp_path: Path) -> None:
    real = create_store(tmp_path / "concrete")

    class _Sneaky(EvidenceStore):
        pass

    fake = _Sneaky(real.root)
    with pytest.raises(TypeError, match="concrete"):
        _run_gated_capture(fake, _inputs(), _credentials(), AUTHORIZE)
    with pytest.raises(TypeError, match="concrete"):
        _issue_verified_attempt(
            fake,
            _rk_attempt(),
            RK_REQUEST_BODY,
            authorize_max_micro_usd=AUTHORIZE,
        )
    assert real.list_committed_ids("attempts") == []


def test_attempt_and_body_are_committed_before_transport(tmp_path: Path) -> None:
    store = create_store(tmp_path / "before")
    seen: list[tuple[int, int]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(
            (
                len(store.list_committed_ids("attempts")),
                len(store.list_committed_ids("captures")),
            )
        )
        return _streamed_response(200, RK_RESPONSE_BODY)

    outcome = _capture_mock(store, handler)
    assert seen == [(1, 0)]
    assert outcome.attempt_id == RK_ATTEMPT_ID
    bundle = store.attempt_path(RK_FINGERPRINT, AUTHORIZED_AT, RK_ATTEMPT_ID)
    assert (bundle / "request.body").read_bytes() == RK_REQUEST_BODY


def test_commit_failure_never_reaches_transport(tmp_path: Path) -> None:
    store = create_store(tmp_path / "commitfail")
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, RK_RESPONSE_BODY)

    broken = dict(_rk_attempt())
    broken["attempt_nonce"] = "not-hex"
    client = _mock_client(handler)
    try:
        with pytest.raises((DocumentError, StoreError)):
            _exchange(
                _issue_verified_attempt(
                    store, broken, RK_REQUEST_BODY, authorize_max_micro_usd=AUTHORIZE
                ),
                _credentials(),
                client=client,
            )
    finally:
        client.close()
    assert calls == []
    assert store.list_committed_ids("attempts") == []


# --- closure-owned transport authority: pre-send ----------------------------


def test_forged_and_cross_gate_capabilities_cannot_transport(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="cannot construct"):
        _VerifiedAttempt()
    forged: Any = object.__new__(_VerifiedAttempt)
    object.__setattr__(forged, "attempt_id", "0" * 64)
    object.__setattr__(forged, "document", {"adapter_contract": RELATED_KEYWORDS_ADAPTER_CONTRACT})
    object.__setattr__(forged, "request_body", RK_REQUEST_BODY)
    object.__setattr__(forged, "_used", False)
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(forged, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _committed_attempt(forged)

    class _Subclass(_VerifiedAttempt):  # type: ignore[misc]
        pass

    subclass: Any = object.__new__(_Subclass)
    object.__setattr__(subclass, "attempt_id", "0" * 64)
    object.__setattr__(subclass, "document", {})
    object.__setattr__(subclass, "request_body", RK_REQUEST_BODY)
    object.__setattr__(subclass, "_used", False)
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(subclass, _credentials())

    rk_store = create_store(tmp_path / "rk")
    rk_cap = _issue_rk(rk_store)
    organic_store = create_store(tmp_path / "org")
    organic_parameters = closed_organic_parameters(keyword="observatory test")
    organic_cap = issue_organic(
        organic_store,
        organic_http_attempt_document(
            parameters=organic_parameters,
            attempt_nonce="c" * 64,
            authorized_at="2026-08-18T20:00:00.000000Z",
            observatory_version="conformance-google-organic-paid-probe-v1",
        ),
        organic_request_body_bytes(organic_parameters),
        authorize_max_micro_usd=30000,
    )
    paid_store = create_store(tmp_path / "paid")
    paid_parameters = closed_paid_parameters(keywords=("seo api",))
    paid_cap = issue_paid(
        paid_store,
        paid_http_attempt_document(
            parameters=paid_parameters,
            attempt_nonce="b" * 64,
            authorized_at="2026-08-16T16:00:00.000000Z",
            observatory_version="conformance-paid-probe-v1",
        ),
        paid_request_body_bytes(paid_parameters),
        authorize_max_micro_usd=20000,
    )
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(organic_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(paid_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        organic_exchange(rk_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        paid_exchange(rk_cap, _credentials())


def test_visible_body_replacement_refuses_before_transport(tmp_path: Path) -> None:
    store = create_store(tmp_path / "body")
    issued = _issue_rk(store)
    replacement = related_keywords_request_body_bytes(
        closed_related_keywords_parameters(keyword=ALT_KEYWORD)
    )
    assert replacement != RK_REQUEST_BODY
    object.__setattr__(issued, "request_body", replacement)
    client, calls = _refusing_client()
    try:
        with pytest.raises(StoreError, match="closure-owned issuance record"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == []


def test_visible_document_only_replacement_refuses_before_transport(tmp_path: Path) -> None:
    store = create_store(tmp_path / "doc")
    issued = _issue_rk(store)
    replacement = _rk_attempt(ALT_KEYWORD)
    validate_attempt(replacement)
    object.__setattr__(issued, "document", replacement)
    assert bytes(issued.request_body) == RK_REQUEST_BODY
    client, calls = _refusing_client()
    try:
        with pytest.raises(StoreError, match="closure-owned issuance record"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == []


def test_visible_document_and_matching_body_replacement_refuses(tmp_path: Path) -> None:
    store = create_store(tmp_path / "docbody")
    issued = _issue_rk(store)
    replacement = _rk_attempt(ALT_KEYWORD)
    replacement_body = related_keywords_request_body_bytes(
        closed_related_keywords_parameters(keyword=ALT_KEYWORD)
    )
    validate_attempt(replacement)
    object.__setattr__(issued, "document", replacement)
    object.__setattr__(issued, "request_body", replacement_body)
    client, calls = _refusing_client()
    try:
        with pytest.raises(StoreError, match="closure-owned issuance record"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == []


def test_used_flag_reset_cannot_replay(tmp_path: Path) -> None:
    store = create_store(tmp_path / "replay")
    issued = _issue_rk(store)
    client, calls = _sending_client()
    try:
        first = _exchange(issued, _credentials(), client=client)
        object.__setattr__(issued, "_used", False)
        assert issued._used is False
        with pytest.raises(StoreError, match="one-exchange"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert first.transport_state == "response_complete"
    assert calls == [RK_REQUEST_BODY]


def test_object_pool_tamper_refused_with_bundle_unchanged(tmp_path: Path) -> None:
    store = create_store(tmp_path / "pool")
    issued = _issue_rk(store)
    bundle = _attempt_bundle(store, issued)
    pool = store.object_path(_request_body_digest(issued))
    bundle_body = bundle / "request.body"
    assert pool.is_file() and bundle_body.is_file()
    assert pool.read_bytes() == RK_REQUEST_BODY
    assert bundle_body.read_bytes() == RK_REQUEST_BODY
    assert pool.stat().st_ino != bundle_body.stat().st_ino
    pool.write_bytes(b"[{}]")
    assert bundle_body.read_bytes() == RK_REQUEST_BODY
    client, calls = _refusing_client()
    try:
        with pytest.raises(StoreError, match="verify-on-read"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == []


def test_bundle_request_body_tamper_refused(tmp_path: Path) -> None:
    store = create_store(tmp_path / "bundle")
    issued = _issue_rk(store)
    bundle = _attempt_bundle(store, issued)
    pool = store.object_path(_request_body_digest(issued))
    (bundle / "request.body").write_bytes(b"[{}]")
    assert pool.read_bytes() == RK_REQUEST_BODY
    client, calls = _refusing_client()
    try:
        with pytest.raises(StoreError, match="verify-on-read"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == []


def test_failed_evidence_verification_consumes_issuance(tmp_path: Path) -> None:
    store = create_store(tmp_path / "consume")
    issued = _issue_rk(store)
    bundle = _attempt_bundle(store, issued)
    (bundle / "request.body").write_bytes(b"[{}]")
    client, calls = _refusing_client()
    try:
        with pytest.raises(StoreError, match="verify-on-read"):
            _exchange(issued, _credentials(), client=client)
        with pytest.raises(StoreError, match="one-exchange"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == []


def test_endpoint_validation_failure_leaves_issuance_reusable(tmp_path: Path) -> None:
    store = create_store(tmp_path / "endpoint")
    issued = _issue_rk(store)
    refusing, refused = _refusing_client()
    try:
        for endpoint in (
            f"https://{RELATED_KEYWORDS_HOST}{RELATED_KEYWORDS_PATH}",
            "http://127.0.0.1:9/v3/dataforseo_labs/google/keyword_overview/live",
            "http://127.0.0.1:9" + RELATED_KEYWORDS_PATH + "?x=1",
            "http://user:pass@127.0.0.1:9" + RELATED_KEYWORDS_PATH,
            "http://127.0.0.2:9" + RELATED_KEYWORDS_PATH,
        ):
            with pytest.raises(StoreError, match="loopback"):
                _exchange(issued, _credentials(), endpoint=endpoint, client=refusing)
    finally:
        refusing.close()
    assert refused == []
    sending, calls = _sending_client()
    try:
        result = _exchange(issued, _credentials(), client=sending)
    finally:
        sending.close()
    assert result.transport_state == "response_complete"
    assert calls == [RK_REQUEST_BODY]


def test_credential_validation_failure_leaves_issuance_reusable(tmp_path: Path) -> None:
    store = create_store(tmp_path / "creds")
    issued = _issue_rk(store)
    refusing, refused = _refusing_client()
    try:
        with pytest.raises(CredentialError):
            _exchange(issued, DataForSEOCredentials("", ""), client=refusing)
    finally:
        refusing.close()
    assert refused == []
    sending, calls = _sending_client()
    try:
        result = _exchange(issued, _credentials(), client=sending)
    finally:
        sending.close()
    assert result.transport_state == "response_complete"
    assert calls == [RK_REQUEST_BODY]


# --- closure-owned authority AFTER exchange (RK-01 hardening beyond PF-17) ---


def test_post_exchange_mirror_mutation_cannot_change_capture_or_result(
    tmp_path: Path,
) -> None:
    """RK-01 closes PF-16/PF-17's post-exchange caller-visible mirror window."""

    store = create_store(tmp_path / "postexchange")
    issued = _issue_rk(store)
    client, calls = _sending_client()
    try:
        result = _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == [RK_REQUEST_BODY]

    # Mutate every visible mirror AFTER the exchange, before Capture commit.
    replacement = _rk_attempt(ALT_KEYWORD)
    validate_attempt(replacement)
    replacement_id = content_digest(canonical_json(replacement))
    assert replacement_id != RK_ATTEMPT_ID
    object.__setattr__(issued, "document", replacement)
    object.__setattr__(issued, "attempt_id", replacement_id)
    object.__setattr__(
        issued,
        "request_body",
        related_keywords_request_body_bytes(
            closed_related_keywords_parameters(keyword=ALT_KEYWORD)
        ),
    )

    from observatory.dataforseo_google_related_keywords_paid_probe import (
        _commit_related_keywords_capture,
    )

    # Commit the replacement Attempt too, so the mis-parented Capture would be a *valid*
    # commit if the mirror still had authority. Without closure-owned authority this test
    # would otherwise fail only because the replacement parent is missing from the store.
    store.commit_attempt(
        replacement,
        request_body=related_keywords_request_body_bytes(
            closed_related_keywords_parameters(keyword=ALT_KEYWORD)
        ),
    )
    assert store.read_attempt(replacement_id) is not None

    capture_id = _commit_related_keywords_capture(store, issued, result, _credentials())
    capture = store.read_capture(capture_id)
    assert capture is not None
    assert capture["attempt_id"] == RK_ATTEMPT_ID
    assert capture["attempt_id"] != replacement_id
    committed_id, committed_document = _committed_attempt(issued)
    assert committed_id == RK_ATTEMPT_ID
    assert content_digest(canonical_json(committed_document)) == RK_ATTEMPT_ID


def test_capture_result_attempt_id_is_closure_owned(tmp_path: Path) -> None:
    store = create_store(tmp_path / "resultid")
    outcome = _capture_mock(
        store, lambda request: _streamed_response(200, RK_RESPONSE_BODY)
    )
    assert outcome.attempt_id == RK_ATTEMPT_ID
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["attempt_id"] == RK_ATTEMPT_ID


# --- transport shape and PF-09 branches -------------------------------------


def test_handler_sees_exactly_one_post_with_exact_body_path_and_headers(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path / "shape")
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return _streamed_response(200, RK_RESPONSE_BODY)

    outcome = _capture_mock(store, handler)
    assert len(seen) == 1
    request = seen[0]
    assert request.method == "POST"
    assert str(request.url) == f"https://{RELATED_KEYWORDS_HOST}{RELATED_KEYWORDS_PATH}"
    assert request.content == RK_REQUEST_BODY
    assert request.headers["authorization"] == SENTINEL_BASIC
    assert request.headers["content-type"] == "application/json"
    assert request.headers["accept"] == "application/json"
    assert request.headers["accept-encoding"] == "identity"
    assert request.headers["user-agent"] == "observatory-dataforseo-v1"
    assert outcome.transport_state == "response_complete"


def test_synthetic_pagination_fields_do_not_cause_a_second_exchange(
    tmp_path: Path,
) -> None:
    """Structural proof: the adapter never parses the body, so it cannot continue."""

    store = create_store(tmp_path / "pagination")
    body = json.dumps(
        {
            "tasks": [
                {
                    "result": [
                        {
                            "seed_keyword": KEYWORD,
                            "total_count": 5000,
                            "items_count": 100,
                            "offset": 0,
                            "offset_token": "keep-going",
                            "items": [],
                        }
                    ]
                }
            ]
        }
    ).encode()
    calls: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.content)
        return _streamed_response(200, body)

    outcome = _capture_mock(store, handler)
    assert len(calls) == 1
    assert outcome.transport_state == "response_complete"
    assert store.read_capture_body(outcome.capture_id) == body
    assert inspect_related_keywords_paid_probe_body(store, outcome.capture_id) == body
    assert len(store.list_committed_ids("attempts")) == 1
    assert len(store.list_committed_ids("captures")) == 1


def test_non_2xx_zero_byte_and_limit_branches(tmp_path: Path) -> None:
    error_store = create_store(tmp_path / "err")
    error = _capture_mock(
        error_store, lambda request: _streamed_response(402, b'{"status_code":40200}')
    )
    assert error.transport_state == "response_complete"
    capture = error_store.read_capture(error.capture_id)
    assert capture is not None
    response = capture["response"]
    assert isinstance(response, Mapping)
    assert response["status"] == 402

    empty_store = create_store(tmp_path / "empty")
    empty = _capture_mock(empty_store, lambda request: _streamed_response(200, b""))
    assert empty.transport_state == "response_complete"
    with pytest.raises(StoreError):
        inspect_related_keywords_paid_probe_body(empty_store, empty.capture_id)

    limit_store = create_store(tmp_path / "limit")
    limited = _capture_mock(
        limit_store,
        lambda request: _streamed_response(200, b"x" * 4096),
        max_response_body_bytes=SMALL_LIMIT,
    )
    assert limited.transport_state == "response_partial"
    body = limit_store.read_capture_body(limited.capture_id)
    assert body is not None and len(body) == SMALL_LIMIT


def test_mid_body_and_no_response_branches(tmp_path: Path) -> None:
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

    store = create_store(tmp_path / "partial")
    client = httpx.Client(
        transport=PartialTransport(),
        trust_env=False,
        follow_redirects=False,
        timeout=httpx.Timeout(30.0),
    )
    client.headers.clear()
    try:
        outcome = _run_gated_capture(store, _inputs(), _credentials(), AUTHORIZE, client=client)
    finally:
        client.close()
    assert outcome.transport_state == "response_partial"
    assert store.read_capture_body(outcome.capture_id) == b'{"partial":'

    fail_store = create_store(tmp_path / "noresp")

    def boom(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no")

    failed = _capture_mock(fail_store, boom)
    capture = fail_store.read_capture(failed.capture_id)
    assert capture is not None
    assert capture["transport_state"] == "no_response"


def test_authorized_loopback_path_sends_once(tmp_path: Path) -> None:
    store = create_store(tmp_path / "loopback")
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return _streamed_response(200, RK_RESPONSE_BODY)

    client = _mock_client(handler)
    try:
        outcome = _run_gated_capture(
            store,
            _inputs(),
            _credentials(),
            AUTHORIZE,
            endpoint="http://127.0.0.1:8931" + RELATED_KEYWORDS_PATH,
            client=client,
        )
    finally:
        client.close()
    assert len(seen) == 1
    assert str(seen[0].url) == "http://127.0.0.1:8931" + RELATED_KEYWORDS_PATH
    assert outcome.transport_state == "response_complete"


# --- credentials -------------------------------------------------------------


def test_secret_headers_omitted_and_never_persisted(tmp_path: Path) -> None:
    store = create_store(tmp_path / "headers")
    headers = [(name, "leak") for name in DENYLIST]
    headers.append(("content-type", "application/json"))
    outcome = _capture_mock(
        store, lambda request: _streamed_response(200, RK_RESPONSE_BODY, headers)
    )
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    response = capture["response"]
    assert isinstance(response, Mapping)
    retained = response["headers"]
    assert isinstance(retained, list)
    retained_names = {pair[0] for pair in retained}
    for name in DENYLIST:
        assert name not in retained_names
    chunks: list[bytes] = []
    for path in sorted(store.root.rglob("*")):
        if path.is_file():
            chunks.append(path.read_bytes())
    _assert_no_secrets(b"\n".join(chunks).decode("utf-8", "replace"))


def test_credential_echo_in_body_is_refused(tmp_path: Path) -> None:
    store = create_store(tmp_path / "echo")
    with pytest.raises(StoreError, match="credential material"):
        _capture_mock(
            store,
            lambda request: _streamed_response(200, SENTINEL_PASSWORD.encode()),
        )
    assert store.list_committed_ids("captures") == []
    assert len(store.list_committed_ids("attempts")) == 1


def test_credential_echo_in_header_is_refused(tmp_path: Path) -> None:
    store = create_store(tmp_path / "echohdr")
    with pytest.raises(StoreError, match="credential material"):
        _capture_mock(
            store,
            lambda request: _streamed_response(
                200,
                RK_RESPONSE_BODY,
                [("x-echo", SENTINEL_LOGIN), ("content-type", "application/json")],
            ),
        )
    assert store.list_committed_ids("captures") == []


# --- one-shot semantics ------------------------------------------------------


@pytest.mark.parametrize(
    "first",
    ["complete", "partial", "no_response", "credential_echo", "unresolved"],
)
def test_one_shot_refuses_second_attempt_after_any_first_state(
    tmp_path: Path, first: str
) -> None:
    store = create_store(tmp_path / f"oneshot-{first}")
    if first == "complete":
        _capture_mock(store, lambda request: _streamed_response(200, RK_RESPONSE_BODY))
    elif first == "partial":
        _capture_mock(
            store,
            lambda request: _streamed_response(200, b"x" * 4096),
            max_response_body_bytes=SMALL_LIMIT,
        )
    elif first == "no_response":
        def _boom(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("no")

        outcome = _capture_mock(store, _boom)
        capture = store.read_capture(outcome.capture_id)
        assert capture is not None
        assert capture["transport_state"] == "no_response"
    elif first == "credential_echo":
        with pytest.raises(StoreError):
            _capture_mock(
                store, lambda request: _streamed_response(200, SENTINEL_PASSWORD.encode())
            )
    else:
        store.commit_attempt(_rk_attempt(), request_body=RK_REQUEST_BODY)
    with pytest.raises(StoreError, match="related-keywords paid-probe Attempt"):
        _capture_mock(
            store,
            lambda request: _streamed_response(200, RK_RESPONSE_BODY),
            _inputs(ALT_KEYWORD, nonce="7" * 64, authorized_at="2026-08-28T21:00:00.000000Z"),
        )


def test_one_shot_allows_neighbouring_adapter_evidence(tmp_path: Path) -> None:
    store = create_store(tmp_path / "neighbours")
    capture_fixture(store, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    paid_parameters = closed_paid_parameters(keywords=("seo api",))
    store.commit_attempt(
        paid_http_attempt_document(
            parameters=paid_parameters,
            attempt_nonce="b" * 64,
            authorized_at="2026-08-16T16:00:00.000000Z",
            observatory_version="conformance-paid-probe-v1",
        ),
        request_body=paid_request_body_bytes(paid_parameters),
    )
    organic_parameters = closed_organic_parameters(keyword="observatory test")
    store.commit_attempt(
        organic_http_attempt_document(
            parameters=organic_parameters,
            attempt_nonce="c" * 64,
            authorized_at="2026-08-18T20:00:00.000000Z",
            observatory_version="conformance-google-organic-paid-probe-v1",
        ),
        request_body=organic_request_body_bytes(organic_parameters),
    )
    outcome = _capture_mock(store, lambda request: _streamed_response(200, RK_RESPONSE_BODY))
    assert outcome.attempt_id == RK_ATTEMPT_ID
    assert scrub_store(store) == []


# --- inspect -----------------------------------------------------------------


def test_inspect_returns_exact_complete_body(tmp_path: Path) -> None:
    store = create_store(tmp_path / "inspect")
    outcome = _capture_mock(store, lambda request: _streamed_response(200, RK_RESPONSE_BODY))
    reader = inspect_store(store.root)
    assert inspect_related_keywords_paid_probe_body(reader, outcome.capture_id) == (
        RK_RESPONSE_BODY
    )


def test_inspect_rejects_bad_ids_wrong_adapter_and_tamper(tmp_path: Path) -> None:
    store = create_store(tmp_path / "inspectbad")
    outcome = _capture_mock(store, lambda request: _streamed_response(200, RK_RESPONSE_BODY))
    for bad in ("", "zz", "A" * 64, "g" * 64, RK_ATTEMPT_ID.upper(), 5):
        with pytest.raises(StoreError, match="capture-id is invalid"):
            inspect_related_keywords_paid_probe_body(store, bad)  # type: ignore[arg-type]
    with pytest.raises(StoreError, match="verified complete"):
        inspect_related_keywords_paid_probe_body(store, "0" * 64)

    other = create_store(tmp_path / "otheradapter")
    organic_parameters = closed_organic_parameters(keyword="observatory test")
    organic_attempt = organic_http_attempt_document(
        parameters=organic_parameters,
        attempt_nonce="c" * 64,
        authorized_at="2026-08-18T20:00:00.000000Z",
        observatory_version="conformance-google-organic-paid-probe-v1",
    )
    other.commit_attempt(
        organic_attempt, request_body=organic_request_body_bytes(organic_parameters)
    )
    partial_store = create_store(tmp_path / "inspectpartial")
    partial = _capture_mock(
        partial_store,
        lambda request: _streamed_response(200, b"x" * 4096),
        max_response_body_bytes=SMALL_LIMIT,
    )
    with pytest.raises(StoreError, match="verified complete"):
        inspect_related_keywords_paid_probe_body(partial_store, partial.capture_id)

    bundle = store.capture_path(outcome.capture_id)
    (bundle / "response.body").write_bytes(b"tampered")
    with pytest.raises(StoreError):
        inspect_related_keywords_paid_probe_body(store, outcome.capture_id)


# --- isolation from existing Derivations, scrub, and public surface ----------


def test_existing_derivations_skip_related_keywords_evidence(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "mixed")
    fixture = capture_fixture(store, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    paid_parameters = closed_paid_parameters(keywords=("seo api",))
    store.commit_attempt(
        paid_http_attempt_document(
            parameters=paid_parameters,
            attempt_nonce="e" * 64,
            authorized_at="2026-08-16T16:00:00.000000Z",
            observatory_version="conformance-paid-probe-v1",
        ),
        request_body=paid_request_body_bytes(paid_parameters),
    )
    attempt = _rk_attempt()
    store.commit_attempt(attempt, request_body=RK_REQUEST_BODY)
    capture = related_keywords_http_capture_document(
        attempt=attempt,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response=_complete_response(),
        transport_failure=None,
        response_headers_at=RESPONSE_HEADERS_AT,
        response_body_ended_at=RESPONSE_BODY_ENDED_AT,
    )
    capture_id = store.commit_capture(capture, response_body=RK_RESPONSE_BODY)
    assert scrub_store(store) == []
    with connect(postgres_dsn) as connection:
        fixture_summary = derive(store, connection, DEFAULT_VERSION)
        ko_summary = derive_keyword_overview(store, connection)
        rk_rows = connection.execute(
            "SELECT count(*) FROM outcomes WHERE attempt_id = %s OR capture_id = %s",
            (RK_ATTEMPT_ID, capture_id),
        ).fetchone()
        fixture_rows = connection.execute(
            "SELECT count(*) FROM outcomes WHERE attempt_id = %s",
            (fixture.attempt_id,),
        ).fetchone()
    assert fixture_summary.integrity_failures == 0
    assert ko_summary.integrity_failures == 0
    assert rk_rows == (0,)
    assert fixture_rows is not None and fixture_rows[0] >= 1


def test_public_surface_exposes_no_contract_widening_seam() -> None:
    names = capture_dataforseo_google_related_keywords_paid_probe.__code__.co_varnames
    for hidden in ("endpoint", "max_response_body_bytes", "client", "depth", "limit", "offset"):
        assert hidden not in names
    fields = set(RelatedKeywordsPaidProbeInputs.__dataclass_fields__)
    assert fields == {"keyword", "attempt_nonce", "authorized_at", "observatory_version"}


def test_cli_refuses_extra_options_and_wrong_authorization(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    for argv in (
        ["capture", "--evidence-root", str(tmp_path / "c"), "--keyword", KEYWORD],
        ["capture", "--evidence-root", str(tmp_path / "c"), "--keyword", KEYWORD,
         "--authorize-max-micro-usd", "200000", "--depth", "3"],
        ["capture", "--evidence-root", str(tmp_path / "c"), "--keyword", KEYWORD,
         "--authorize-max-micro-usd", "200000", "--limit", "1000"],
    ):
        with pytest.raises(SystemExit):
            main(argv)
    monkeypatch.setenv(DATAFORSEO_LOGIN_ENV, SENTINEL_LOGIN)
    monkeypatch.setenv(DATAFORSEO_PASSWORD_ENV, SENTINEL_PASSWORD)
    code = main(
        [
            "capture",
            "--evidence-root",
            str(tmp_path / "cli"),
            "--keyword",
            KEYWORD,
            "--authorize-max-micro-usd",
            "20000",
        ]
    )
    assert code == 1
    captured = capsys.readouterr()
    assert "capture failed" in captured.err
    _assert_no_secrets(captured.err, captured.out)


def test_cli_requires_credentials(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(
        [
            "capture",
            "--evidence-root",
            str(tmp_path / "nocreds"),
            "--keyword",
            KEYWORD,
            "--authorize-max-micro-usd",
            "200000",
        ]
    )
    assert code == 2
    assert not (tmp_path / "nocreds").exists()


# --- RK-01 remediation proofs ------------------------------------------------


def test_private_snapshot_mutation_cannot_poison_closure_authority(
    tmp_path: Path,
) -> None:
    """The post-exchange accessor must hand out no authoritative mutable state.

    Attacks the private seam directly: take whatever the accessor returns, mutate it in
    place into a *different, committed* Related Keywords Attempt so mis-parentage would be
    a valid commit, and require the Capture and capture result to still cite the original.
    """

    store = create_store(tmp_path / "authority-leak")
    issued = _issue_rk(store)
    client, calls = _sending_client()
    try:
        result = _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == [RK_REQUEST_BODY]

    replacement = _rk_attempt(ALT_KEYWORD)
    validate_attempt(replacement)
    replacement_id = content_digest(canonical_json(replacement))
    assert replacement_id != RK_ATTEMPT_ID
    store.commit_attempt(
        replacement,
        request_body=related_keywords_request_body_bytes(
            closed_related_keywords_parameters(keyword=ALT_KEYWORD)
        ),
    )
    assert store.read_attempt(replacement_id) is not None

    committed_id, snapshot = _committed_attempt(issued)
    assert committed_id == RK_ATTEMPT_ID
    # In-place mutation of the handed-out mapping, including nested children.
    snapshot.clear()
    snapshot.update(replacement)
    parameters = snapshot.get("parameters")
    assert isinstance(parameters, dict)
    parameters["keyword"] = ALT_KEYWORD

    # Closure authority must be unchanged for every later read.
    reread_id, reread = _committed_attempt(issued)
    assert reread_id == RK_ATTEMPT_ID
    assert content_digest(canonical_json(reread)) == RK_ATTEMPT_ID
    assert reread["attempt_nonce"] == NONCE
    reread_parameters = reread["parameters"]
    assert isinstance(reread_parameters, Mapping)
    assert reread_parameters["keyword"] == KEYWORD

    from observatory.dataforseo_google_related_keywords_paid_probe import (
        _commit_related_keywords_capture,
    )

    capture_id = _commit_related_keywords_capture(store, issued, result, _credentials())
    capture = store.read_capture(capture_id)
    assert capture is not None
    assert capture["attempt_id"] == RK_ATTEMPT_ID
    assert capture["attempt_id"] != replacement_id


def test_private_snapshot_is_detached_on_every_call(tmp_path: Path) -> None:
    store = create_store(tmp_path / "detached")
    issued = _issue_rk(store)
    _, first = _committed_attempt(issued)
    _, second = _committed_attempt(issued)
    assert first is not second
    assert first == second
    assert first["parameters"] is not second["parameters"]
    first["attempt_nonce"] = "7" * 64
    _, third = _committed_attempt(issued)
    assert third["attempt_nonce"] == NONCE
    assert content_digest(canonical_json(third)) == RK_ATTEMPT_ID


def test_inspect_rejects_valid_wrong_adapter_capture(tmp_path: Path) -> None:
    """A committed, valid, verifiable Capture from another adapter must be refused."""

    store = create_store(tmp_path / "wrongadapter")
    fixture = capture_fixture(store, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    assert store.read_capture(fixture.capture_id) is not None
    reader = inspect_store(store.root)
    with pytest.raises(StoreError, match="verified complete"):
        inspect_related_keywords_paid_probe_body(reader, fixture.capture_id)

    organic_store = create_store(tmp_path / "organiccapture")
    organic_parameters = closed_organic_parameters(keyword="observatory test")
    organic_attempt = organic_http_attempt_document(
        parameters=organic_parameters,
        attempt_nonce="c" * 64,
        authorized_at="2026-08-18T20:00:00.000000Z",
        observatory_version="conformance-google-organic-paid-probe-v1",
    )
    organic_body = organic_request_body_bytes(organic_parameters)
    organic_store.commit_attempt(organic_attempt, request_body=organic_body)
    organic_response = b'{"cost":0.022}'
    organic_capture_id = organic_store.commit_capture(
        organic_http_capture_document(
            attempt=organic_attempt,
            request_started_at=REQUEST_STARTED_AT,
            transport_ended_at=TRANSPORT_ENDED_AT,
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
                        "bytes": len(organic_response),
                        "sha256": content_digest(organic_response),
                    },
                },
                "completeness": "complete",
            },
            transport_failure=None,
            response_headers_at=RESPONSE_HEADERS_AT,
            response_body_ended_at=RESPONSE_BODY_ENDED_AT,
        ),
        response_body=organic_response,
    )
    organic_reader = inspect_store(organic_store.root)
    assert organic_reader.read_capture(organic_capture_id) is not None
    with pytest.raises(StoreError, match="verified complete"):
        inspect_related_keywords_paid_probe_body(organic_reader, organic_capture_id)


def test_inspect_rejects_no_response_capture(tmp_path: Path) -> None:
    store = create_store(tmp_path / "inspectnoresp")

    def boom(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no")

    outcome = _capture_mock(store, boom)
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["transport_state"] == "no_response"
    assert capture["response"] is None
    reader = inspect_store(store.root)
    with pytest.raises(StoreError, match="verified complete"):
        inspect_related_keywords_paid_probe_body(reader, outcome.capture_id)
