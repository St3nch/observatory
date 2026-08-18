"""Internal bounded one-request/one-response HTTP-v2 exchange mechanics."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final
from urllib.parse import urlparse

import httpx

from observatory.capture_event import body_ref

_SECRET_RESPONSE_HEADERS: Final[frozenset[str]] = frozenset(
    {
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
    }
)

__all__ = [
    "HttpExchangeResult",
    "perform_bounded_http_exchange",
    "production_http_client",
]


@dataclass(frozen=True)
class HttpExchangeResult:
    transport_state: str
    request_started_at: str
    transport_ended_at: str
    response_headers_at: str | None
    response_body_ended_at: str | None
    response: dict[str, object] | None
    body: bytes | None
    transport_failure: dict[str, str] | None


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def production_http_client(timeout: httpx.Timeout) -> httpx.Client:
    """Build the accepted production client using an adapter-owned timeout."""

    client = httpx.Client(
        trust_env=False,
        verify=True,
        http2=False,
        follow_redirects=False,
        timeout=timeout,
        limits=httpx.Limits(max_keepalive_connections=0, max_connections=1),
    )
    client.headers.clear()
    return client


def _sent_headers(
    *,
    application_headers: Sequence[Sequence[str]],
    authorization: str,
    host: str,
    content_length: int,
) -> list[tuple[str, str]]:
    headers = [(name, value) for name, value in application_headers]
    headers.append(("authorization", authorization))
    headers.append(("host", host))
    headers.append(("content-length", str(content_length)))
    return headers


def _normalize_response_headers(
    raw_pairs: list[tuple[bytes, bytes]],
) -> tuple[list[list[str]], list[dict[str, int | str]]]:
    retained: list[list[str]] = []
    omitted_counts: dict[str, int] = {}
    for name_b, value_b in raw_pairs:
        name = name_b.decode("iso-8859-1").lower()
        value = value_b.decode("iso-8859-1")
        if name in _SECRET_RESPONSE_HEADERS:
            omitted_counts[name] = omitted_counts.get(name, 0) + 1
            continue
        retained.append([name, value])
    omitted: list[dict[str, int | str]] = [
        {"count": omitted_counts[name], "name": name} for name in sorted(omitted_counts)
    ]
    return retained, omitted


def _body_state(data: bytes) -> dict[str, object]:
    if len(data) == 0:
        return {"state": "present_zero_bytes", "body": body_ref(data)}
    return {"state": "present_nonempty", "body": body_ref(data)}


def _map_failure(exc: BaseException, *, have_headers: bool) -> tuple[str, str]:
    if have_headers:
        if isinstance(exc, httpx.TimeoutException):
            return "receive_body", "timeout"
        if isinstance(exc, httpx.RemoteProtocolError):
            return "receive_body", "protocol_failed"
        return "receive_body", "read_failed"
    if isinstance(exc, (httpx.ConnectTimeout, httpx.PoolTimeout)):
        return "connect", "timeout"
    if isinstance(exc, httpx.ConnectError):
        return "connect", "connection_failed"
    if isinstance(exc, httpx.WriteTimeout):
        return "send_request", "timeout"
    if isinstance(exc, httpx.WriteError):
        return "send_request", "write_failed"
    if isinstance(exc, httpx.TimeoutException):
        return "receive_headers", "timeout"
    if isinstance(exc, httpx.RemoteProtocolError):
        return "receive_headers", "protocol_failed"
    if isinstance(exc, httpx.ReadError):
        return "receive_headers", "read_failed"
    return "connect", "connection_failed"


def _http_version(value: str) -> str | None:
    if value in {"HTTP/1.0", "HTTP/1.1", "HTTP/2"}:
        return value
    return None


def perform_bounded_http_exchange(
    *,
    url: str,
    body: bytes,
    application_headers: Sequence[Sequence[str]],
    authorization: str,
    timeout: httpx.Timeout,
    max_response_body_bytes: int,
    client: httpx.Client | None = None,
) -> HttpExchangeResult:
    """Perform one bounded POST exchange. Caller must already be adapter-gated."""

    host = urlparse(url).netloc
    headers = _sent_headers(
        application_headers=application_headers,
        authorization=authorization,
        host=host,
        content_length=len(body),
    )
    own_client = client is None
    http = client if client is not None else production_http_client(timeout)
    request_started_at = _utc_now()
    have_headers = False
    response_headers_at: str | None = None
    prefix = bytearray()
    stream_response: httpx.Response | None = None
    try:
        with http.stream("POST", url, content=body, headers=headers) as response:
            stream_response = response
            have_headers = True
            response_headers_at = _utc_now()
            version = _http_version(response.http_version)
            if version is None:
                ended = _utc_now()
                return HttpExchangeResult(
                    transport_state="no_response",
                    request_started_at=request_started_at,
                    transport_ended_at=ended,
                    response_headers_at=None,
                    response_body_ended_at=None,
                    response=None,
                    body=None,
                    transport_failure={
                        "phase": "receive_headers",
                        "code": "protocol_failed",
                    },
                )
            raw_headers = [(name, value) for name, value in response.headers.raw]
            exceeded = False
            try:
                for chunk in response.iter_raw():
                    if not chunk:
                        continue
                    remaining = max_response_body_bytes - len(prefix)
                    if len(chunk) > remaining:
                        prefix.extend(chunk[:remaining])
                        exceeded = True
                        break
                    prefix.extend(chunk)
            except BaseException as exc:
                if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                    raise
                phase, code = _map_failure(exc, have_headers=True)
                retained, omitted = _normalize_response_headers(raw_headers)
                received = bytes(prefix)
                body_ended = _utc_now()
                ended = _utc_now()
                if ended < body_ended:
                    ended = body_ended
                return HttpExchangeResult(
                    transport_state="response_partial",
                    request_started_at=request_started_at,
                    transport_ended_at=ended,
                    response_headers_at=response_headers_at,
                    response_body_ended_at=body_ended,
                    response={
                        "status": response.status_code,
                        "http_version": version,
                        "header_policy": "http-headers-v1",
                        "headers": retained,
                        "omitted_headers": omitted,
                        "body": _body_state(received),
                        "completeness": "partial",
                    },
                    body=received,
                    transport_failure={"phase": phase, "code": code},
                )
            response_body_ended_at = _utc_now()
            received = bytes(prefix)
            retained, omitted = _normalize_response_headers(raw_headers)
            ended = _utc_now()
            if ended < response_body_ended_at:
                ended = response_body_ended_at
            if exceeded:
                return HttpExchangeResult(
                    transport_state="response_partial",
                    request_started_at=request_started_at,
                    transport_ended_at=ended,
                    response_headers_at=response_headers_at,
                    response_body_ended_at=response_body_ended_at,
                    response={
                        "status": response.status_code,
                        "http_version": version,
                        "header_policy": "http-headers-v1",
                        "headers": retained,
                        "omitted_headers": omitted,
                        "body": _body_state(received),
                        "completeness": "partial",
                    },
                    body=received,
                    transport_failure={
                        "phase": "receive_body",
                        "code": "read_failed",
                    },
                )
            return HttpExchangeResult(
                transport_state="response_complete",
                request_started_at=request_started_at,
                transport_ended_at=ended,
                response_headers_at=response_headers_at,
                response_body_ended_at=response_body_ended_at,
                response={
                    "status": response.status_code,
                    "http_version": version,
                    "header_policy": "http-headers-v1",
                    "headers": retained,
                    "omitted_headers": omitted,
                    "body": _body_state(received),
                    "completeness": "complete",
                },
                body=received,
                transport_failure=None,
            )
    except BaseException as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        if have_headers and stream_response is not None:
            phase, code = _map_failure(exc, have_headers=True)
            version = _http_version(stream_response.http_version) or "HTTP/1.1"
            retained, omitted = _normalize_response_headers(
                [(name, value) for name, value in stream_response.headers.raw]
            )
            received = bytes(prefix)
            headers_at = response_headers_at or request_started_at
            body_ended = _utc_now()
            ended = _utc_now()
            if ended < body_ended:
                ended = body_ended
            return HttpExchangeResult(
                transport_state="response_partial",
                request_started_at=request_started_at,
                transport_ended_at=ended,
                response_headers_at=headers_at,
                response_body_ended_at=body_ended,
                response={
                    "status": stream_response.status_code,
                    "http_version": version,
                    "header_policy": "http-headers-v1",
                    "headers": retained,
                    "omitted_headers": omitted,
                    "body": _body_state(received),
                    "completeness": "partial",
                },
                body=received,
                transport_failure={"phase": phase, "code": code},
            )
        phase, code = _map_failure(exc, have_headers=False)
        ended = _utc_now()
        return HttpExchangeResult(
            transport_state="no_response",
            request_started_at=request_started_at,
            transport_ended_at=ended,
            response_headers_at=None,
            response_body_ended_at=None,
            response=None,
            body=None,
            transport_failure={"phase": phase, "code": code},
        )
    finally:
        if own_client:
            http.close()
