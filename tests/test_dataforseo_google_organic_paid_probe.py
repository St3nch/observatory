"""PF-10: Google Organic Live Advanced paid-probe contract, gate, and inspect."""

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
    ORGANIC_AUTHORIZED_COST_MICRO_USD,
    PAID_ADAPTER_CONTRACT,
    DocumentError,
    canonical_json,
    content_digest,
    http_attempt_document,
    http_capture_document,
    organic_http_attempt_document,
    organic_http_capture_document,
    organic_http_fingerprint_document,
    organic_http_request,
    paid_http_attempt_document,
    paid_http_capture_document,
    validate_attempt,
    validate_http_parameters,
    validate_organic_http_parameters,
    validate_organic_http_request,
    validate_paid_http_parameters,
)
from observatory.dataforseo_google_organic_paid_probe import (
    _TIMEOUT,
    MAX_RESPONSE_BODY_BYTES,
    GoogleOrganicPaidProbeInputs,
    _exchange,
    _issue_verified_attempt,
    _run_gated_capture,
    _VerifiedAttempt,
    capture_dataforseo_google_organic_paid_probe,
    closed_organic_parameters,
    inspect_organic_paid_probe_body,
    main,
    organic_request_body_bytes,
)
from observatory.dataforseo_paid_probe import (
    _exchange as paid_exchange,
)
from observatory.dataforseo_paid_probe import (
    _issue_verified_attempt as issue_paid,
)
from observatory.dataforseo_paid_probe import (
    closed_paid_parameters,
    inspect_paid_probe_body,
    paid_request_body_bytes,
)
from observatory.dataforseo_sandbox import (
    _exchange as sandbox_exchange,
)
from observatory.dataforseo_sandbox import (
    _issue_verified_attempt as issue_sandbox,
)
from observatory.dataforseo_sandbox import (
    closed_sandbox_parameters,
    request_body_bytes,
)
from observatory.derive import DEFAULT_VERSION, derive
from observatory.evidence import scrub_store
from observatory.evidence_store import EvidenceStore, StoreError, create_store, inspect_store
from observatory.keyword_overview_derive import derive_keyword_overview
from observatory.migrate import connect
from observatory.settings import (
    DATAFORSEO_LOGIN_ENV,
    DATAFORSEO_PASSWORD_ENV,
    DataForSEOCredentials,
)

SENTINEL_LOGIN = "sentinel-login-pf10-gg77"
SENTINEL_PASSWORD = "sentinel-password-pf10-hh88"
SENTINEL_BASIC = "Basic " + base64.b64encode(
    f"{SENTINEL_LOGIN}:{SENTINEL_PASSWORD}".encode()
).decode("ascii")
AUTHORIZE = 30000
KEYWORD = "observatory test"
NONCE = "5555555555555555555555555555555555555555555555555555555555555555"
AUTHORIZED_AT = "2026-08-18T20:00:00.000000Z"
SOFTWARE = "conformance-google-organic-paid-probe-v1"
REQUEST_STARTED_AT = "2026-08-18T20:00:00.100000Z"
RESPONSE_HEADERS_AT = "2026-08-18T20:00:00.200000Z"
RESPONSE_BODY_ENDED_AT = "2026-08-18T20:00:00.300000Z"
TRANSPORT_ENDED_AT = "2026-08-18T20:00:00.400000Z"

ORGANIC_REQUEST_BODY = (
    b'[{"depth":100,"device":"desktop","group_organic_results":true,'
    b'"keyword":"observatory test","language_code":"en",'
    b'"load_async_ai_overview":true,"location_code":2840,"os":"windows"}]'
)
ORGANIC_REQUEST_BODY_SHA256 = (
    "0ea1022be28baf54e8a68f49002c963ada85f78082dec843030db28458498e2b"
)
ORGANIC_FINGERPRINT = "9ab79d6031d2a82a9aec4d9c6c5399bd540fcbbea80fca8a0216911333cedb02"
ORGANIC_ATTEMPT_ID = "b577bc1fb75f4ba7576a96c1328fbe74df9d975f3bd03f6c01d7441dfed1a1be"
ORGANIC_RESPONSE_BODY = b'{"cost":0.022}'
ORGANIC_RESPONSE_BODY_SHA256 = (
    "3d2170a13d940e4fb5ed584257fee22a0f105753c2d2cc7b41b967da3c5abc8e"
)
ORGANIC_CAPTURE_ID = "ab94c98e528e776317c459a2dc2f8010b33b8ce142bab52d4e699fb5599d41c4"
HTTP_ATTEMPT_ID = "22adc4841c86b7cd98b90bba683aeac204a0cb568428b590fd399e8627eb4640"
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


def _inputs() -> GoogleOrganicPaidProbeInputs:
    return GoogleOrganicPaidProbeInputs(
        keyword=KEYWORD,
        attempt_nonce=NONCE,
        authorized_at=AUTHORIZED_AT,
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
    inputs: GoogleOrganicPaidProbeInputs | None = None,
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


def _complete_response() -> dict[str, object]:
    return {
        "status": 200,
        "http_version": "HTTP/1.1",
        "header_policy": "http-headers-v1",
        "headers": [["content-type", "application/json"]],
        "omitted_headers": [],
        "body": {
            "state": "present_nonempty",
            "body": {"bytes": 14, "sha256": ORGANIC_RESPONSE_BODY_SHA256},
        },
        "completeness": "complete",
    }


def _organic_attempt() -> dict[str, object]:
    return organic_http_attempt_document(
        parameters=closed_organic_parameters(keyword=KEYWORD),
        attempt_nonce=NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=SOFTWARE,
    )


def _tree_bytes(root: Path) -> bytes:
    chunks: list[bytes] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            chunks.append(path.read_bytes())
    return b"\n".join(chunks)


def _assert_no_secrets(*surfaces: object) -> None:
    for surface in surfaces:
        text = surface if isinstance(surface, str) else repr(surface)
        assert SENTINEL_LOGIN not in text
        assert SENTINEL_PASSWORD not in text
        assert SENTINEL_BASIC not in text


def test_closed_request_vector_and_attempt_identity() -> None:
    parameters = closed_organic_parameters(keyword=KEYWORD)
    body = organic_request_body_bytes(parameters)
    assert body == ORGANIC_REQUEST_BODY
    assert content_digest(body) == ORGANIC_REQUEST_BODY_SHA256
    attempt = _organic_attempt()
    request = attempt["request"]
    assert isinstance(request, Mapping)
    fingerprint = organic_http_fingerprint_document(request=request)
    assert content_digest(canonical_json(fingerprint)) == ORGANIC_FINGERPRINT
    assert content_digest(canonical_json(attempt)) == ORGANIC_ATTEMPT_ID
    capture = organic_http_capture_document(
        attempt=attempt,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response=_complete_response(),
        transport_failure=None,
        response_headers_at=RESPONSE_HEADERS_AT,
        response_body_ended_at=RESPONSE_BODY_ENDED_AT,
    )
    assert content_digest(canonical_json(capture)) == ORGANIC_CAPTURE_ID
    assert parameters["depth"] == 100
    assert parameters["load_async_ai_overview"] is True
    assert parameters["group_organic_results"] is True
    task = json.loads(body)
    assert isinstance(task, list) and len(task) == 1
    assert "contract" not in task[0]


def test_existing_sandbox_and_paid_identities_unchanged() -> None:
    sandbox = http_attempt_document(
        parameters=closed_sandbox_parameters(
            keyword="observatory test", location_code=2840, language_code="en"
        ),
        attempt_nonce="3333333333333333333333333333333333333333333333333333333333333333",
        authorized_at="2026-08-14T20:00:00.000000Z",
        observatory_version="conformance-http-v2",
    )
    assert content_digest(canonical_json(sandbox)) == HTTP_ATTEMPT_ID
    paid = paid_http_attempt_document(
        parameters=closed_paid_parameters(
            keywords=(
                "seo api",
                "keyword research",
                "local seo",
                "generative engine optimization",
                "ai search optimization",
            )
        ),
        attempt_nonce="4444444444444444444444444444444444444444444444444444444444444444",
        authorized_at="2026-08-16T16:00:00.000000Z",
        observatory_version="conformance-paid-probe-v1",
    )
    assert content_digest(canonical_json(paid)) == PAID_ATTEMPT_ID


@pytest.mark.parametrize(
    "keyword",
    [
        "SITE:example.com",
        "cache:example.com",
        "definition:seo",
        "related:seo",
        "-site:example.com",
        "allinurl:observatory",
    ],
)
def test_operator_keywords_are_rejected(keyword: str) -> None:
    with pytest.raises(DocumentError):
        closed_organic_parameters(keyword=keyword)


def test_website_comparison_is_allowed() -> None:
    parameters = closed_organic_parameters(keyword="website comparison")
    assert parameters["keyword"] == "website comparison"


@pytest.mark.parametrize(
    "keyword",
    [
        "",
        "a" * 81,
        "a b c d e f g h i j k",
        " observatory",
        "observatory ",
        "observatory!",
        "observatory\ttest",
    ],
)
def test_keyword_grammar_rejects_invalid_forms(keyword: str) -> None:
    with pytest.raises(DocumentError):
        closed_organic_parameters(keyword=keyword)


def test_confused_contracts_are_rejected() -> None:
    organic = closed_organic_parameters(keyword=KEYWORD)
    with pytest.raises(DocumentError):
        validate_http_parameters(organic)
    with pytest.raises(DocumentError):
        validate_paid_http_parameters(organic)
    paid = closed_paid_parameters(keywords=("seo api",))
    with pytest.raises(DocumentError):
        validate_organic_http_parameters(paid)
    sandbox = closed_sandbox_parameters(
        keyword=KEYWORD, location_code=2840, language_code="en"
    )
    with pytest.raises(DocumentError):
        validate_organic_http_parameters(sandbox)
    request = organic_http_request(body=ORGANIC_REQUEST_BODY)
    with pytest.raises(DocumentError):
        validate_organic_http_request({**request, "host": "sandbox.dataforseo.com"})
    with pytest.raises(DocumentError):
        validate_organic_http_request(
            {**request, "path": "/v3/dataforseo_labs/google/keyword_overview/live"}
        )


def test_adapter_owns_32mib_and_120s_read_timeout() -> None:
    import observatory.http_single_exchange as shared

    assert MAX_RESPONSE_BODY_BYTES == 33_554_432
    assert _TIMEOUT.connect == 30.0
    assert _TIMEOUT.read == 120.0
    assert _TIMEOUT.write == 30.0
    assert _TIMEOUT.pool == 30.0
    source = Path(shared.__file__).read_text(encoding="utf-8")
    assert "33_554_432" not in source
    assert "Timeout(connect=30.0, read=120.0" not in source
    assert not hasattr(shared, "MAX_RESPONSE_BODY_BYTES")


def test_forged_capability_cannot_reach_send() -> None:
    with pytest.raises(TypeError, match="cannot construct"):
        _VerifiedAttempt()
    forged: Any = object.__new__(_VerifiedAttempt)
    object.__setattr__(forged, "attempt_id", "0" * 64)
    object.__setattr__(forged, "document", {"adapter_contract": ORGANIC_ADAPTER_CONTRACT})
    object.__setattr__(forged, "request_body", ORGANIC_REQUEST_BODY)
    object.__setattr__(forged, "_used", False)
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(forged, _credentials())


def test_authorization_required_before_attempt(tmp_path: Path) -> None:
    store = create_store(tmp_path / "auth")
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, ORGANIC_RESPONSE_BODY)

    for value in (0, 20000, 29999, 30001, True):
        with pytest.raises(StoreError, match="authorize-max-micro-usd 30000"):
            _capture_mock(store, handler, authorize=value)
    assert calls == []
    assert store.list_committed_ids("attempts") == []


def test_one_shot_is_keyed_by_organic_adapter_not_paid_mode(tmp_path: Path) -> None:
    store = create_store(tmp_path / "oneshot")
    paid_parameters = closed_paid_parameters(keywords=("seo api",))
    paid_document = paid_http_attempt_document(
        parameters=paid_parameters,
        attempt_nonce="b" * 64,
        authorized_at="2026-08-16T16:00:00.000000Z",
        observatory_version="conformance-paid-probe-v1",
    )
    store.commit_attempt(paid_document, request_body=paid_request_body_bytes(paid_parameters))

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, ORGANIC_RESPONSE_BODY)

    first = _capture_mock(store, handler)
    assert store.read_attempt(first.attempt_id) is not None
    with pytest.raises(StoreError, match="organic paid-probe Attempt"):
        _capture_mock(
            store,
            handler,
            GoogleOrganicPaidProbeInputs(
                keyword=KEYWORD,
                attempt_nonce="c" * 64,
                authorized_at="2026-08-18T20:00:01.000000Z",
                observatory_version=SOFTWARE,
            ),
        )


def test_complete_exchange_commits_verified_capture(tmp_path: Path) -> None:
    store = create_store(tmp_path / "complete")
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return _streamed_response(200, ORGANIC_RESPONSE_BODY)

    outcome = _capture_mock(store, handler)
    assert len(seen) == 1
    assert seen[0].url.host == "127.0.0.1" or seen[0].headers.get("authorization")
    assert outcome.transport_state == "response_complete"
    assert store.read_capture_body(outcome.capture_id) == ORGANIC_RESPONSE_BODY
    loaded = store.read_attempt(outcome.attempt_id)
    assert loaded is not None
    assert loaded["adapter_contract"] == ORGANIC_ADAPTER_CONTRACT
    request = loaded["request"]
    assert isinstance(request, Mapping)
    assert request["host"] == "api.dataforseo.com"
    assert request["path"] == "/v3/serp/google/organic/live/advanced"
    _assert_no_secrets(_tree_bytes(store.root), loaded)
    assert scrub_store(store) == []


def test_small_bound_truncates_without_32mib_allocation(tmp_path: Path) -> None:
    store = create_store(tmp_path / "limit")
    payload = b"abcdefghijklmnopq"

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, payload)

    outcome = _capture_mock(store, handler, max_response_body_bytes=SMALL_LIMIT)
    assert outcome.transport_state == "response_partial"
    body = store.read_capture_body(outcome.capture_id)
    assert body == payload[:SMALL_LIMIT]


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
        outcome = _run_gated_capture(
            store, _inputs(), _credentials(), AUTHORIZE, client=client
        )
    finally:
        client.close()
    assert outcome.transport_state == "response_partial"
    assert store.read_capture_body(outcome.capture_id) == b'{"partial":'

    fail_store = create_store(tmp_path / "noresp")

    def boom(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no")

    failed = _capture_mock(
        fail_store,
        boom,
        GoogleOrganicPaidProbeInputs(
            keyword=KEYWORD,
            attempt_nonce="d" * 64,
            authorized_at="2026-08-18T20:00:02.000000Z",
            observatory_version=SOFTWARE,
        ),
    )
    capture = fail_store.read_capture(failed.capture_id)
    assert capture is not None
    assert capture["transport_state"] == "no_response"


def test_secret_headers_omitted(tmp_path: Path) -> None:
    store = create_store(tmp_path / "headers")
    secret_headers = [(name, f"secret-{name}") for name in DENYLIST]
    retained = [
        ("content-type", "application/json"),
        ("x-request-id", "one"),
        ("x-request-id", "two"),
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(
            200, ORGANIC_RESPONSE_BODY, headers=retained + secret_headers
        )

    outcome = _capture_mock(store, handler)
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    response = capture["response"]
    assert isinstance(response, Mapping)
    assert response["headers"][:3] == [
        ["content-type", "application/json"],
        ["x-request-id", "one"],
        ["x-request-id", "two"],
    ]
    tree = _tree_bytes(store.root)
    for name in DENYLIST:
        assert f"secret-{name}".encode() not in tree


def test_cross_adapter_capabilities_are_isolated(tmp_path: Path) -> None:
    organic_store = create_store(tmp_path / "org")
    organic_cap = _issue_verified_attempt(
        organic_store,
        _organic_attempt(),
        ORGANIC_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    sandbox_store = create_store(tmp_path / "sbx")
    sandbox_parameters = closed_sandbox_parameters(
        keyword=KEYWORD, location_code=2840, language_code="en"
    )
    sandbox_cap = issue_sandbox(
        sandbox_store,
        http_attempt_document(
            parameters=sandbox_parameters,
            attempt_nonce="a" * 64,
            authorized_at="2026-08-14T20:00:00.000000Z",
            observatory_version="conformance-http-v2",
        ),
        request_body_bytes(sandbox_parameters),
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
        _exchange(sandbox_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(paid_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        sandbox_exchange(organic_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        paid_exchange(organic_cap, _credentials())
    client = _mock_client(lambda request: _streamed_response(200, ORGANIC_RESPONSE_BODY))
    try:
        _exchange(organic_cap, _credentials(), client=client)
        with pytest.raises(StoreError, match="one-exchange"):
            _exchange(organic_cap, _credentials(), client=client)
    finally:
        client.close()


def test_credential_echo_in_body_is_refused(tmp_path: Path) -> None:
    store = create_store(tmp_path / "echo")

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, SENTINEL_PASSWORD.encode())

    with pytest.raises(StoreError, match="credential material"):
        _capture_mock(store, handler)
    assert store.list_committed_ids("captures") == []
    expected_attempt = content_digest(canonical_json(_organic_attempt()))
    assert store.list_committed_ids("attempts") == [expected_attempt]


def test_authorized_loopback_path_sends_once(tmp_path: Path) -> None:
    store = create_store(tmp_path / "ok-loop")
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url))
        return _streamed_response(200, ORGANIC_RESPONSE_BODY)

    client = _mock_client(handler)
    try:
        outcome = _run_gated_capture(
            store,
            _inputs(),
            _credentials(),
            AUTHORIZE,
            endpoint="http://127.0.0.1:9/v3/serp/google/organic/live/advanced",
            client=client,
        )
    finally:
        client.close()
    assert seen == ["http://127.0.0.1:9/v3/serp/google/organic/live/advanced"]
    assert outcome.transport_state == "response_complete"


def test_loopback_only_path_is_organic(tmp_path: Path) -> None:
    store = create_store(tmp_path / "loop")
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, ORGANIC_RESPONSE_BODY)

    client = _mock_client(handler)
    try:
        with pytest.raises(StoreError, match="loopback"):
            _run_gated_capture(
                store,
                _inputs(),
                _credentials(),
                AUTHORIZE,
                endpoint="https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
                client=client,
            )
        with pytest.raises(StoreError, match="loopback"):
            _run_gated_capture(
                store,
                _inputs(),
                _credentials(),
                AUTHORIZE,
                endpoint="http://127.0.0.1:9/v3/dataforseo_labs/google/keyword_overview/live",
                client=client,
            )
    finally:
        client.close()
    assert calls == []
    assert store.list_committed_ids("attempts") == []


def test_public_cli_refuses_extra_options(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main(
            [
                "capture",
                "--evidence-root",
                "/tmp/x",
                "--keyword",
                KEYWORD,
                "--authorize-max-micro-usd",
                "30000",
                "--timeout",
                "5",
            ]
        )
    with pytest.raises(SystemExit):
        main(["capture", "--evidence-root", "/tmp/x", "--keyword", KEYWORD])
    err = capsys.readouterr().err
    assert "timeout" in err or "unrecognized" in err or "required" in err


def test_inspect_emits_exact_complete_body(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = create_store(tmp_path / "inspect")
    attempt = _organic_attempt()
    store.commit_attempt(attempt, request_body=ORGANIC_REQUEST_BODY)
    capture = organic_http_capture_document(
        attempt=attempt,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response=_complete_response(),
        transport_failure=None,
        response_headers_at=RESPONSE_HEADERS_AT,
        response_body_ended_at=RESPONSE_BODY_ENDED_AT,
    )
    capture_id = store.commit_capture(capture, response_body=ORGANIC_RESPONSE_BODY)
    body = inspect_organic_paid_probe_body(inspect_store(store.root), capture_id)
    assert body == ORGANIC_RESPONSE_BODY
    code = main(
        ["inspect", "--evidence-root", str(store.root), "--capture-id", capture_id]
    )
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.encode() == ORGANIC_RESPONSE_BODY or captured.out == (
        ORGANIC_RESPONSE_BODY.decode()
    )


def test_inspect_rejects_wrong_adapter_and_partial(tmp_path: Path) -> None:
    store = create_store(tmp_path / "inspect-bad")
    sandbox_parameters = closed_sandbox_parameters(
        keyword=KEYWORD, location_code=2840, language_code="en"
    )
    sandbox = http_attempt_document(
        parameters=sandbox_parameters,
        attempt_nonce="a" * 64,
        authorized_at="2026-08-14T20:00:00.000000Z",
        observatory_version="conformance-http-v2",
    )
    store.commit_attempt(sandbox, request_body=request_body_bytes(sandbox_parameters))
    sandbox_capture = http_capture_document(
        attempt=sandbox,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response=_complete_response(),
        transport_failure=None,
        response_headers_at=RESPONSE_HEADERS_AT,
        response_body_ended_at=RESPONSE_BODY_ENDED_AT,
    )
    sandbox_id = store.commit_capture(sandbox_capture, response_body=ORGANIC_RESPONSE_BODY)
    with pytest.raises(StoreError):
        inspect_organic_paid_probe_body(inspect_store(store.root), sandbox_id)
    organic = _organic_attempt()
    store.commit_attempt(organic, request_body=ORGANIC_REQUEST_BODY)
    prefix = b'{"partial":'
    partial = organic_http_capture_document(
        attempt=organic,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="response_partial",
        response={
            "status": 200,
            "http_version": "HTTP/1.1",
            "header_policy": "http-headers-v1",
            "headers": [["content-type", "application/json"]],
            "omitted_headers": [],
            "body": {
                "state": "present_nonempty",
                "body": {"bytes": len(prefix), "sha256": content_digest(prefix)},
            },
            "completeness": "partial",
        },
        transport_failure={"phase": "receive_body", "code": "read_failed"},
        response_headers_at=RESPONSE_HEADERS_AT,
        response_body_ended_at=RESPONSE_BODY_ENDED_AT,
    )
    partial_id = store.commit_capture(partial, response_body=prefix)
    with pytest.raises(StoreError):
        inspect_organic_paid_probe_body(inspect_store(store.root), partial_id)
    paid_parameters = closed_paid_parameters(keywords=("seo api",))
    paid = paid_http_attempt_document(
        parameters=paid_parameters,
        attempt_nonce="b" * 64,
        authorized_at="2026-08-16T16:00:00.000000Z",
        observatory_version="conformance-paid-probe-v1",
    )
    store.commit_attempt(paid, request_body=paid_request_body_bytes(paid_parameters))
    paid_capture = paid_http_capture_document(
        attempt=paid,
        request_started_at="2026-08-16T16:00:00.100000Z",
        transport_ended_at="2026-08-16T16:00:00.400000Z",
        transport_state="response_complete",
        response=_complete_response(),
        transport_failure=None,
        response_headers_at="2026-08-16T16:00:00.200000Z",
        response_body_ended_at="2026-08-16T16:00:00.300000Z",
    )
    paid_id = store.commit_capture(paid_capture, response_body=ORGANIC_RESPONSE_BODY)
    with pytest.raises(StoreError):
        inspect_organic_paid_probe_body(inspect_store(store.root), paid_id)
    no_store = create_store(tmp_path / "inspect-nr")
    nr_attempt = _organic_attempt()
    no_store.commit_attempt(nr_attempt, request_body=ORGANIC_REQUEST_BODY)
    nr_capture = organic_http_capture_document(
        attempt=nr_attempt,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="no_response",
        response=None,
        transport_failure={"phase": "connect", "code": "connection_failed"},
        response_headers_at=None,
        response_body_ended_at=None,
    )
    nr_id = no_store.commit_capture(nr_capture, response_body=None)
    with pytest.raises(StoreError):
        inspect_organic_paid_probe_body(inspect_store(no_store.root), nr_id)
    complete_store = create_store(tmp_path / "inspect-complete")
    complete_attempt = _organic_attempt()
    complete_store.commit_attempt(complete_attempt, request_body=ORGANIC_REQUEST_BODY)
    complete_id = complete_store.commit_capture(
        organic_http_capture_document(
            attempt=complete_attempt,
            request_started_at=REQUEST_STARTED_AT,
            transport_ended_at=TRANSPORT_ENDED_AT,
            transport_state="response_complete",
            response=_complete_response(),
            transport_failure=None,
            response_headers_at=RESPONSE_HEADERS_AT,
            response_body_ended_at=RESPONSE_BODY_ENDED_AT,
        ),
        response_body=ORGANIC_RESPONSE_BODY,
    )
    with pytest.raises(StoreError):
        inspect_paid_probe_body(inspect_store(complete_store.root), complete_id)
    bundle = complete_store.capture_path(complete_id)
    (bundle / "response.body").write_bytes(b"tampered-bytes!!")
    with pytest.raises(StoreError):
        inspect_organic_paid_probe_body(inspect_store(complete_store.root), complete_id)


def test_fixture_and_keyword_overview_derive_skip_organic(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "mixed")
    fixture = capture_fixture(store, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    paid_parameters = closed_paid_parameters(keywords=("seo api",))
    paid_document = paid_http_attempt_document(
        parameters=paid_parameters,
        attempt_nonce="e" * 64,
        authorized_at="2026-08-16T16:00:00.000000Z",
        observatory_version="conformance-paid-probe-v1",
    )
    store.commit_attempt(paid_document, request_body=paid_request_body_bytes(paid_parameters))
    attempt = _organic_attempt()
    store.commit_attempt(attempt, request_body=ORGANIC_REQUEST_BODY)
    capture = organic_http_capture_document(
        attempt=attempt,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response=_complete_response(),
        transport_failure=None,
        response_headers_at=RESPONSE_HEADERS_AT,
        response_body_ended_at=RESPONSE_BODY_ENDED_AT,
    )
    capture_id = store.commit_capture(capture, response_body=ORGANIC_RESPONSE_BODY)
    assert scrub_store(store) == []
    with connect(postgres_dsn) as connection:
        fixture_summary = derive(store, connection, DEFAULT_VERSION)
        ko_summary = derive_keyword_overview(store, connection)
        organic_outcomes = connection.execute(
            "SELECT count(*) FROM outcomes WHERE attempt_id = %s OR capture_id = %s",
            (content_digest(canonical_json(attempt)), capture_id),
        ).fetchone()
        fixture_attempts = connection.execute(
            "SELECT count(*) FROM outcomes WHERE attempt_id = %s",
            (fixture.attempt_id,),
        ).fetchone()
    assert fixture_summary.integrity_failures == 0
    assert ko_summary.integrity_failures == 0
    assert organic_outcomes == (0,)
    assert fixture_attempts is not None and fixture_attempts[0] >= 1


def test_public_capture_function_has_no_endpoint_or_limit() -> None:
    assert "endpoint" not in capture_dataforseo_google_organic_paid_probe.__code__.co_varnames
    assert (
        "max_response_body_bytes"
        not in capture_dataforseo_google_organic_paid_probe.__code__.co_varnames
    )
    assert HTTP_ADAPTER_CONTRACT != ORGANIC_ADAPTER_CONTRACT
    assert PAID_ADAPTER_CONTRACT != ORGANIC_ADAPTER_CONTRACT
    assert ORGANIC_AUTHORIZED_COST_MICRO_USD == 30000
    policy = validate_attempt(_organic_attempt())["policy"]
    assert isinstance(policy, Mapping)
    assert policy["pricing_basis"] == "dataforseo-google-organic-live-2026-08-18"
