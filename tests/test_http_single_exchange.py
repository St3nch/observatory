"""PF-09: internal bounded HTTP single-exchange seam."""

from __future__ import annotations

import socket
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any, cast

import httpx
import pytest

from observatory.capture_event import (
    HTTP_ADAPTER_CONTRACT,
    HTTP_HEADERS,
    PAID_ADAPTER_CONTRACT,
    canonical_json,
    content_digest,
    http_attempt_document,
    http_fingerprint_document,
    paid_http_attempt_document,
    paid_http_fingerprint_document,
)
from observatory.dataforseo_paid_probe import (
    _TIMEOUT as PAID_TIMEOUT,
)
from observatory.dataforseo_paid_probe import (
    MAX_RESPONSE_BODY_BYTES as PAID_MAX_RESPONSE_BODY_BYTES,
)
from observatory.dataforseo_paid_probe import (
    PaidProbeInputs,
    closed_paid_parameters,
    paid_request_body_bytes,
)
from observatory.dataforseo_paid_probe import (
    _exchange as paid_exchange,
)
from observatory.dataforseo_paid_probe import (
    _issue_verified_attempt as issue_paid,
)
from observatory.dataforseo_sandbox import (
    _TIMEOUT as SANDBOX_TIMEOUT,
)
from observatory.dataforseo_sandbox import (
    MAX_RESPONSE_BODY_BYTES as SANDBOX_MAX_RESPONSE_BODY_BYTES,
)
from observatory.dataforseo_sandbox import (
    SandboxCaptureInputs,
    closed_sandbox_parameters,
    request_body_bytes,
)
from observatory.dataforseo_sandbox import (
    _exchange as sandbox_exchange,
)
from observatory.dataforseo_sandbox import (
    _issue_verified_attempt as issue_sandbox,
)
from observatory.evidence_store import StoreError, create_store
from observatory.http_single_exchange import (
    perform_bounded_http_exchange,
    production_http_client,
)
from observatory.settings import DataForSEOCredentials

APPLICATION_HEADERS = [
    ["accept", "application/json"],
    ["accept-encoding", "identity"],
    ["connection", "close"],
    ["content-type", "application/json"],
    ["user-agent", "observatory-dataforseo-v1"],
]
AUTHORIZATION = "Basic dGVzdDp0ZXN0"
LOOPBACK_URL = "http://127.0.0.1:9/v3/internal"
SMALL_LIMIT = 16
SENTINEL_LOGIN = "sentinel-login-pf09-ee55"
SENTINEL_PASSWORD = "sentinel-password-pf09-ff66"


@pytest.fixture(autouse=True)
def _no_public_network(monkeypatch: pytest.MonkeyPatch) -> None:
    real = socket.create_connection

    def guarded(address: Any, *args: Any, **kwargs: Any) -> socket.socket:
        host = address[0] if isinstance(address, tuple) else address
        if host not in {"127.0.0.1", "::1"}:
            raise AssertionError(f"public-network request forbidden: {host}")
        return real(address, *args, **kwargs)

    monkeypatch.setattr(socket, "create_connection", guarded)


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


def _exchange(
    handler: Any,
    *,
    body: bytes = b"[]",
    max_response_body_bytes: int = SMALL_LIMIT,
    headers: list[list[str]] | None = None,
) -> Any:
    client = _mock_client(handler)
    try:
        return perform_bounded_http_exchange(
            url=LOOPBACK_URL,
            body=body,
            application_headers=headers or APPLICATION_HEADERS,
            authorization=AUTHORIZATION,
            timeout=httpx.Timeout(30.0),
            max_response_body_bytes=max_response_body_bytes,
            client=client,
        )
    finally:
        client.close()


def _credentials() -> DataForSEOCredentials:
    return DataForSEOCredentials(SENTINEL_LOGIN, SENTINEL_PASSWORD)


def test_complete_nonempty_response() -> None:
    payload = b'{"ok":true}'

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "127.0.0.1"
        assert request.headers["authorization"] == AUTHORIZATION
        assert request.headers["accept"] == "application/json"
        return _streamed_response(200, payload)

    result = _exchange(handler, body=payload)
    assert result.transport_state == "response_complete"
    assert result.body == payload
    assert result.transport_failure is None
    assert result.response is not None
    assert result.response["completeness"] == "complete"
    assert result.response["status"] == 200
    assert result.response["body"]["state"] == "present_nonempty"


def test_complete_zero_byte_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, b"")

    result = _exchange(handler, body=b"")
    assert result.transport_state == "response_complete"
    assert result.body == b""
    assert result.transport_failure is None
    assert result.response is not None
    assert result.response["completeness"] == "complete"
    assert result.response["body"]["state"] == "present_zero_bytes"


def test_secret_headers_omitted_retained_order_and_duplicates() -> None:
    secret_headers = [
        ("authorization", "secret-authorization"),
        ("set-cookie", "secret-set-cookie"),
        ("x-api-key", "secret-x-api-key"),
    ]
    retained = [
        ("content-type", "application/json"),
        ("x-request-id", "one"),
        ("x-request-id", "two"),
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, b"{}", headers=retained + secret_headers)

    result = _exchange(handler)
    assert result.response is not None
    assert result.response["headers"][:3] == [
        ["content-type", "application/json"],
        ["x-request-id", "one"],
        ["x-request-id", "two"],
    ]
    omitted = result.response["omitted_headers"]
    assert omitted == [
        {"count": 1, "name": "authorization"},
        {"count": 1, "name": "set-cookie"},
        {"count": 1, "name": "x-api-key"},
    ]
    dumped = canonical_json(result.response)
    assert b"secret-authorization" not in dumped
    assert b"secret-set-cookie" not in dumped
    assert b"secret-x-api-key" not in dumped


def test_pre_header_failures_are_no_response() -> None:
    cases: list[tuple[BaseException, str, str]] = [
        (httpx.ConnectError("no"), "connect", "connection_failed"),
        (httpx.ConnectTimeout("no"), "connect", "timeout"),
        (httpx.WriteError("no"), "send_request", "write_failed"),
        (httpx.WriteTimeout("no"), "send_request", "timeout"),
        (httpx.RemoteProtocolError("no"), "receive_headers", "protocol_failed"),
        (httpx.ReadError("no"), "receive_headers", "read_failed"),
        (httpx.ReadTimeout("no"), "receive_headers", "timeout"),
    ]
    for exc, phase, code in cases:

        def handler(request: httpx.Request, boom: BaseException = exc) -> httpx.Response:
            raise boom

        result = _exchange(handler)
        assert result.transport_state == "no_response"
        assert result.response is None
        assert result.body is None
        assert result.transport_failure == {"phase": phase, "code": code}


def _after_headers_failure(exc: BaseException) -> Any:
    class _RaisingStream(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b'{"partial":'
            raise exc

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
        return perform_bounded_http_exchange(
            url=LOOPBACK_URL,
            body=b"[]",
            application_headers=APPLICATION_HEADERS,
            authorization=AUTHORIZATION,
            timeout=httpx.Timeout(30.0),
            max_response_body_bytes=SMALL_LIMIT,
            client=client,
        )
    finally:
        client.close()


def test_mid_body_read_failure_keeps_prefix() -> None:
    result = _after_headers_failure(httpx.ReadError("cut"))
    assert result.transport_state == "response_partial"
    assert result.body == b'{"partial":'
    assert result.transport_failure == {"phase": "receive_body", "code": "read_failed"}
    assert result.response is not None
    assert result.response["completeness"] == "partial"


def test_after_headers_timeout_and_protocol_mapping() -> None:
    timeout = _after_headers_failure(httpx.ReadTimeout("slow"))
    assert timeout.transport_state == "response_partial"
    assert timeout.body == b'{"partial":'
    assert timeout.transport_failure == {"phase": "receive_body", "code": "timeout"}
    protocol = _after_headers_failure(httpx.RemoteProtocolError("bad"))
    assert protocol.transport_state == "response_partial"
    assert protocol.body == b'{"partial":'
    assert protocol.transport_failure == {
        "phase": "receive_body",
        "code": "protocol_failed",
    }


def test_limit_plus_one_truncates_to_exact_prefix() -> None:
    payload = b"abcdefghijklmnopq"  # 17 bytes

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, payload)

    result = _exchange(handler, max_response_body_bytes=SMALL_LIMIT)
    assert result.transport_state == "response_partial"
    assert result.body == payload[:SMALL_LIMIT]
    assert result.transport_failure == {"phase": "receive_body", "code": "read_failed"}


def test_adapter_owned_limit_controls_truncation() -> None:
    payload = b"0123456789abcdefXYZ"

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, payload)

    small = _exchange(handler, max_response_body_bytes=8)
    large = _exchange(handler, max_response_body_bytes=20)
    assert small.transport_state == "response_partial"
    assert small.body == b"01234567"
    assert large.transport_state == "response_complete"
    assert large.body == payload


def test_redirect_is_complete_testimony_and_not_followed() -> None:
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url))
        return _streamed_response(
            302,
            b"",
            headers=[("location", "https://example.invalid/elsewhere")],
        )

    result = _exchange(handler)
    assert seen == [LOOPBACK_URL]
    assert result.transport_state == "response_complete"
    assert result.transport_failure is None
    assert result.response is not None
    assert result.response["status"] == 302


def test_production_client_uses_supplied_timeout_not_global_30s() -> None:
    timeout = httpx.Timeout(connect=1.25, read=2.5, write=3.75, pool=4.0)
    client = production_http_client(timeout)
    try:
        assert client.timeout.connect == 1.25
        assert client.timeout.read == 2.5
        assert client.timeout.write == 3.75
        assert client.timeout.pool == 4.0
        assert client.trust_env is False
        assert client.follow_redirects is False
    finally:
        client.close()


def test_exchange_passes_timeout_into_production_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[httpx.Timeout] = []

    def wrapped(timeout: httpx.Timeout) -> httpx.Client:
        captured.append(timeout)
        return _mock_client(lambda request: _streamed_response(200, b"ok"))

    monkeypatch.setattr(
        "observatory.http_single_exchange.production_http_client",
        wrapped,
    )
    timeout = httpx.Timeout(12.0)
    perform_bounded_http_exchange(
        url=LOOPBACK_URL,
        body=b"[]",
        application_headers=APPLICATION_HEADERS,
        authorization=AUTHORIZATION,
        timeout=timeout,
        max_response_body_bytes=SMALL_LIMIT,
    )
    assert captured == [timeout]


def test_production_client_ignores_ambient_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:9")
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9")
    monkeypatch.setenv("ALL_PROXY", "http://127.0.0.1:9")
    client = production_http_client(httpx.Timeout(5.0))
    try:
        assert client.trust_env is False
        assert client.follow_redirects is False
    finally:
        client.close()


def test_sentinel_authorization_does_not_enter_exchange_result() -> None:
    sentinel = f"Basic {SENTINEL_LOGIN}:{SENTINEL_PASSWORD}"

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(
            200,
            b'{"ok":true}',
            headers=[
                ("authorization", sentinel),
                ("x-api-key", SENTINEL_PASSWORD),
                ("content-type", "application/json"),
            ],
        )

    client = _mock_client(handler)
    try:
        result = perform_bounded_http_exchange(
            url=LOOPBACK_URL,
            body=b"[]",
            application_headers=APPLICATION_HEADERS,
            authorization=sentinel,
            timeout=httpx.Timeout(30.0),
            max_response_body_bytes=SMALL_LIMIT,
            client=client,
        )
    finally:
        client.close()
    assert result.transport_state == "response_complete"
    assert result.response is not None
    dumped = canonical_json(result.response)
    assert SENTINEL_LOGIN.encode() not in dumped
    assert SENTINEL_PASSWORD.encode() not in dumped
    assert sentinel.encode() not in dumped
    assert result.transport_failure is None
    assert result.body == b'{"ok":true}'


def test_shared_module_has_no_global_eight_mib_or_timeout_policy() -> None:
    import observatory.http_single_exchange as mod

    text = Path(mod.__file__).read_text(encoding="utf-8")
    assert "8_388_608" not in text
    assert "8388608" not in text
    assert "Timeout(30.0)" not in text
    assert not hasattr(mod, "MAX_RESPONSE_BODY_BYTES")


def test_existing_adapters_keep_owned_eight_mib_and_30s() -> None:
    assert SANDBOX_MAX_RESPONSE_BODY_BYTES == 8_388_608
    assert PAID_MAX_RESPONSE_BODY_BYTES == 8_388_608
    assert httpx.Timeout(30.0) == SANDBOX_TIMEOUT
    assert httpx.Timeout(30.0) == PAID_TIMEOUT


def test_shared_module_is_not_a_public_runner() -> None:
    import observatory.http_single_exchange as mod

    assert not hasattr(mod, "main")
    assert getattr(mod, "__name__", "") != "__main__"
    source = Path(mod.__file__).read_text(encoding="utf-8")
    assert "argparse" not in source
    assert 'if __name__ == "__main__"' not in source


def test_published_http_v2_and_paid_identities_recompute() -> None:
    sandbox_parameters = closed_sandbox_parameters(
        keyword="observatory test",
        location_code=2840,
        language_code="en",
    )
    sandbox_body = request_body_bytes(sandbox_parameters)
    sandbox_attempt = http_attempt_document(
        parameters=sandbox_parameters,
        attempt_nonce="3333333333333333333333333333333333333333333333333333333333333333",
        authorized_at="2026-08-14T20:00:00.000000Z",
        observatory_version="conformance-http-v2",
    )
    sandbox_request = sandbox_attempt["request"]
    assert isinstance(sandbox_request, Mapping)
    sandbox_fingerprint = http_fingerprint_document(
        request=cast(Mapping[str, object], sandbox_request)
    )
    assert content_digest(sandbox_body) == (
        "d10484d2237e4b08e37a4f3fe66bd678a3dbc2dab96f9b712af1b858b8d6d070"
    )
    assert content_digest(canonical_json(sandbox_fingerprint)) == (
        "6b28e6d02fee14c8d8852889336baeb46bfa9918c5d4eee7b51e889f1823a2bb"
    )
    assert content_digest(canonical_json(sandbox_attempt)) == (
        "22adc4841c86b7cd98b90bba683aeac204a0cb568428b590fd399e8627eb4640"
    )

    paid_parameters = closed_paid_parameters(
        keywords=(
            "seo api",
            "keyword research",
            "local seo",
            "generative engine optimization",
            "ai search optimization",
        )
    )
    paid_body = paid_request_body_bytes(paid_parameters)
    paid_attempt = paid_http_attempt_document(
        parameters=paid_parameters,
        attempt_nonce="4444444444444444444444444444444444444444444444444444444444444444",
        authorized_at="2026-08-16T16:00:00.000000Z",
        observatory_version="conformance-paid-probe-v1",
    )
    paid_request = paid_attempt["request"]
    assert isinstance(paid_request, Mapping)
    paid_fingerprint = paid_http_fingerprint_document(
        request=cast(Mapping[str, object], paid_request)
    )
    assert content_digest(paid_body) == (
        "3fc7205a55a1a5c464c0ae4ebca21a1e3088c2022565929a670fdf757ab7987b"
    )
    assert content_digest(canonical_json(paid_fingerprint)) == (
        "6cc5765911abe752a974d2fba268d927fdc055147c1286fffdfe0ee585cdc610"
    )
    assert content_digest(canonical_json(paid_attempt)) == (
        "89904bf8a6812fb3d0d845310e4705962bb4db928b80da3be67342dff5def185"
    )


def test_sandbox_capability_cannot_execute_paid_path(tmp_path: Path) -> None:
    store = create_store(tmp_path / "cross-sandbox")
    parameters = closed_sandbox_parameters(
        keyword="observatory test",
        location_code=2840,
        language_code="en",
    )
    document = http_attempt_document(
        parameters=parameters,
        attempt_nonce="a" * 64,
        authorized_at="2026-08-14T20:00:00.000000Z",
        observatory_version="conformance-http-v2",
    )
    capability = issue_sandbox(store, document, request_body_bytes(parameters))
    with pytest.raises(TypeError, match="verified committed Attempt"):
        paid_exchange(capability, _credentials())


def test_paid_capability_cannot_execute_sandbox_path(tmp_path: Path) -> None:
    store = create_store(tmp_path / "cross-paid")
    parameters = closed_paid_parameters(keywords=("seo api",))
    document = paid_http_attempt_document(
        parameters=parameters,
        attempt_nonce="b" * 64,
        authorized_at="2026-08-16T16:00:00.000000Z",
        observatory_version="conformance-paid-probe-v1",
    )
    capability = issue_paid(
        store,
        document,
        paid_request_body_bytes(parameters),
        authorize_max_micro_usd=20000,
    )
    with pytest.raises(TypeError, match="verified committed Attempt"):
        sandbox_exchange(capability, _credentials())


def test_fabricated_object_cannot_reach_either_exchange() -> None:
    forged = object()
    with pytest.raises(TypeError, match="verified committed Attempt"):
        sandbox_exchange(forged, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        paid_exchange(forged, _credentials())


def test_used_capabilities_remain_one_exchange(tmp_path: Path) -> None:
    sandbox_store = create_store(tmp_path / "used-sandbox")
    sandbox_parameters = closed_sandbox_parameters(
        keyword="observatory test",
        location_code=2840,
        language_code="en",
    )
    sandbox_document = http_attempt_document(
        parameters=sandbox_parameters,
        attempt_nonce="c" * 64,
        authorized_at="2026-08-14T20:00:00.000000Z",
        observatory_version="conformance-http-v2",
    )
    sandbox_cap = issue_sandbox(
        sandbox_store,
        sandbox_document,
        request_body_bytes(sandbox_parameters),
    )
    client = _mock_client(lambda request: _streamed_response(200, b"{}"))
    try:
        sandbox_exchange(sandbox_cap, _credentials(), client=client)
        with pytest.raises(StoreError, match="one-exchange"):
            sandbox_exchange(sandbox_cap, _credentials(), client=client)
    finally:
        client.close()

    paid_store = create_store(tmp_path / "used-paid")
    paid_parameters = closed_paid_parameters(keywords=("seo api",))
    paid_document = paid_http_attempt_document(
        parameters=paid_parameters,
        attempt_nonce="d" * 64,
        authorized_at="2026-08-16T16:00:00.000000Z",
        observatory_version="conformance-paid-probe-v1",
    )
    paid_cap = issue_paid(
        paid_store,
        paid_document,
        paid_request_body_bytes(paid_parameters),
        authorize_max_micro_usd=20000,
    )
    client = _mock_client(lambda request: _streamed_response(200, b"{}"))
    try:
        paid_exchange(paid_cap, _credentials(), client=client)
        with pytest.raises(StoreError, match="one-exchange"):
            paid_exchange(paid_cap, _credentials(), client=client)
    finally:
        client.close()


def test_adapters_still_supply_their_own_headers_constant() -> None:
    assert HTTP_HEADERS == APPLICATION_HEADERS
    assert HTTP_ADAPTER_CONTRACT.endswith("sandbox-v1")
    assert PAID_ADAPTER_CONTRACT.endswith("paid-probe-v1")


def test_sandbox_and_paid_inputs_types_remain() -> None:
    sandbox = SandboxCaptureInputs(
        keyword="observatory test",
        location_code=2840,
        language_code="en",
        attempt_nonce="e" * 64,
        authorized_at="2026-08-14T20:00:00.000000Z",
        observatory_version="conformance-http-v2",
    )
    paid = PaidProbeInputs(
        keywords=("seo api",),
        attempt_nonce="f" * 64,
        authorized_at="2026-08-16T16:00:00.000000Z",
        observatory_version="conformance-paid-probe-v1",
    )
    assert sandbox.keyword == "observatory test"
    assert paid.keywords == ("seo api",)
