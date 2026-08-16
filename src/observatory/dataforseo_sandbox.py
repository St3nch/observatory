"""DataForSEO sandbox HTTP transport: one gated POST, at most one Capture."""

from __future__ import annotations

import argparse
import secrets
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final
from urllib.parse import urlparse

import httpx

from observatory import __version__
from observatory.capture_event import (
    HTTP_ADAPTER_CONTRACT,
    HTTP_HEADERS,
    HTTP_HOST,
    HTTP_PATH,
    HTTP_POLICY,
    body_ref,
    canonical_json,
    content_digest,
    http_attempt_document,
    http_capture_document,
    validate_http_parameters,
)
from observatory.evidence_store import (
    EvidenceStore,
    StoreError,
    create_store,
    open_store,
)
from observatory.settings import (
    CredentialError,
    DataForSEOCredentials,
    load_dataforseo_credentials,
)

MAX_RESPONSE_BODY_BYTES: Final[int] = 8_388_608
PRODUCTION_URL: Final[str] = (
    "https://sandbox.dataforseo.com/v3/serp/google/organic/live/advanced"
)
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
_TIMEOUT: Final[httpx.Timeout] = httpx.Timeout(30.0)

__all__ = [
    "MAX_RESPONSE_BODY_BYTES",
    "SandboxCaptureInputs",
    "SandboxCaptureOutcome",
    "capture_dataforseo_sandbox",
    "main",
]


@dataclass(frozen=True)
class SandboxCaptureInputs:
    """Caller-supplied sandbox measurement plus frozen authorization fields."""

    keyword: str
    location_code: int
    language_code: str
    attempt_nonce: str
    authorized_at: str
    observatory_version: str


@dataclass(frozen=True)
class SandboxCaptureOutcome:
    attempt_id: str
    capture_id: str
    transport_state: str


@dataclass(frozen=True)
class _ExchangeResult:
    transport_state: str
    request_started_at: str
    transport_ended_at: str
    response_headers_at: str | None
    response_body_ended_at: str | None
    response: dict[str, object] | None
    body: bytes | None
    transport_failure: dict[str, str] | None


def _freeze_maps(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze_maps(item) for key, item in value.items()})
    if isinstance(value, list):
        return [_freeze_maps(item) for item in value]
    return value


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _fresh_nonce() -> str:
    return secrets.token_hex(32)


def request_body_bytes(parameters: Mapping[str, object]) -> bytes:
    """Return JCS(singleton task array) for validated HTTP-v2 parameters."""

    task = {
        "depth": parameters["depth"],
        "device": parameters["device"],
        "keyword": parameters["keyword"],
        "language_code": parameters["language_code"],
        "location_code": parameters["location_code"],
        "os": parameters["os"],
    }
    return canonical_json([task])


def closed_sandbox_parameters(
    *,
    keyword: str,
    location_code: int,
    language_code: str,
) -> dict[str, object]:
    return validate_http_parameters(
        {
            "contract": HTTP_ADAPTER_CONTRACT,
            "depth": 10,
            "device": "desktop",
            "keyword": keyword,
            "language_code": language_code,
            "location_code": location_code,
            "os": "windows",
        }
    )


def _open_or_create(root: Path) -> EvidenceStore:
    if (root / "FORMAT.json").is_file():
        return open_store(root)
    return create_store(root)


def _require_sandbox_target(document: Mapping[str, object]) -> None:
    if document.get("adapter_contract") != HTTP_ADAPTER_CONTRACT:
        raise StoreError("frozen Attempt is not the sandbox adapter contract")
    if document.get("version") != 2:
        raise StoreError("frozen Attempt is not HTTP event version 2")
    if document.get("policy") != HTTP_POLICY:
        raise StoreError("frozen Attempt is not sandbox_no_spend policy")
    request = document.get("request")
    if not isinstance(request, Mapping):
        raise StoreError("frozen Attempt request is missing")
    if (
        request.get("scheme") != "https"
        or request.get("host") != HTTP_HOST
        or request.get("port") is not None
        or request.get("path") != HTTP_PATH
        or request.get("method") != "POST"
        or request.get("query") != []
        or request.get("headers") != HTTP_HEADERS
    ):
        raise StoreError("frozen Attempt is not the sandbox HTTP target")


def _production_client() -> httpx.Client:
    client = httpx.Client(
        trust_env=False,
        verify=True,
        http2=False,
        follow_redirects=False,
        timeout=_TIMEOUT,
        limits=httpx.Limits(max_keepalive_connections=0, max_connections=1),
    )
    client.headers.clear()
    return client


def _sent_headers(
    *,
    authorization: str,
    host: str,
    content_length: int,
) -> list[tuple[str, str]]:
    headers = [(name, value) for name, value in HTTP_HEADERS]
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


def _build_transport_gate() -> tuple[Any, Any, type]:
    issued: list[object] = []

    class _VerifiedAttempt:
        """Internal capability. Not supported public API."""

        __slots__ = ("attempt_id", "document", "request_body", "_used")
        attempt_id: str
        document: Mapping[str, object]
        request_body: bytes
        _used: bool

        def __init__(self, *args: object, **kwargs: object) -> None:
            raise TypeError("cannot construct a transport capability")

        def __setattr__(self, name: str, value: object) -> None:
            raise AttributeError("issued transport capability is immutable")

        def __delattr__(self, name: str) -> None:
            raise AttributeError("issued transport capability is immutable")

    def _is_issued(attempt: object) -> bool:
        return any(candidate is attempt for candidate in issued)

    def issue(
        store: EvidenceStore,
        document: Mapping[str, object],
        request_body: bytes,
    ) -> _VerifiedAttempt:
        if type(store) is not EvidenceStore:
            raise TypeError(
                "DataForSEO sandbox transport requires the concrete EvidenceStore "
                "from create_store/open_store"
            )
        _require_sandbox_target(document)
        attempt_id = store.commit_attempt(document, request_body=request_body)
        read_back = store.read_attempt(attempt_id)
        if read_back is None:
            raise StoreError("committed Attempt is not readable as Evidence")
        if content_digest(canonical_json(read_back)) != attempt_id:
            raise StoreError("read-back Attempt identity does not match")
        if canonical_json(read_back) != canonical_json(document):
            raise StoreError("read-back Attempt does not match committed document")
        bundle = store.attempt_path(
            str(read_back["request_fingerprint"]),
            str(read_back["authorized_at"]),
            attempt_id,
        )
        stored_body = (bundle / "request.body").read_bytes()
        if stored_body != request_body:
            raise StoreError("read-back request body does not match committed bytes")
        _require_sandbox_target(read_back)
        capability = object.__new__(_VerifiedAttempt)
        object.__setattr__(capability, "attempt_id", attempt_id)
        object.__setattr__(capability, "document", _freeze_maps(read_back))
        object.__setattr__(capability, "request_body", bytes(request_body))
        object.__setattr__(capability, "_used", False)
        issued.append(capability)
        return capability

    def exchange(
        attempt: object,
        credentials: DataForSEOCredentials,
        *,
        endpoint: str | None = None,
        client: httpx.Client | None = None,
    ) -> _ExchangeResult:
        if type(attempt) is not _VerifiedAttempt or not _is_issued(attempt):
            raise TypeError(
                "DataForSEO sandbox transport requires a verified committed Attempt"
            )
        if attempt._used:
            raise StoreError("sandbox transport capability is one-exchange only")
        object.__setattr__(attempt, "_used", True)
        document = attempt.document
        _require_sandbox_target(document)
        body = bytes(attempt.request_body)
        authorization = credentials.basic_authorization_header()
        url = PRODUCTION_URL if endpoint is None else endpoint
        host = urlparse(url).netloc
        headers = _sent_headers(
            authorization=authorization,
            host=host,
            content_length=len(body),
        )
        own_client = client is None
        http = client if client is not None else _production_client()
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
                    return _ExchangeResult(
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
                raw_headers = [
                    (name, value) for name, value in response.headers.raw
                ]
                exceeded = False
                try:
                    for chunk in response.iter_raw():
                        if not chunk:
                            continue
                        remaining = MAX_RESPONSE_BODY_BYTES - len(prefix)
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
                    return _ExchangeResult(
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
                    return _ExchangeResult(
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
                return _ExchangeResult(
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
                return _ExchangeResult(
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
            return _ExchangeResult(
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

    return issue, exchange, _VerifiedAttempt


_issue_verified_attempt: Any
_exchange: Any
_VerifiedAttempt: type
_issue_verified_attempt, _exchange, _VerifiedAttempt = _build_transport_gate()


def _commit_sandbox_capture(
    store: EvidenceStore,
    capability: Any,
    result: _ExchangeResult,
) -> str:
    capture = http_capture_document(
        attempt=capability.document,
        request_started_at=result.request_started_at,
        transport_ended_at=result.transport_ended_at,
        transport_state=result.transport_state,
        response=result.response,
        transport_failure=result.transport_failure,
        response_headers_at=result.response_headers_at,
        response_body_ended_at=result.response_body_ended_at,
    )
    capture_id = store.commit_capture(capture, response_body=result.body)
    read_back = store.read_capture(capture_id)
    if read_back is None:
        raise StoreError("committed Capture is not readable as Evidence")
    if content_digest(canonical_json(read_back)) != capture_id:
        raise StoreError("read-back Capture identity does not match")
    if canonical_json(read_back) != canonical_json(capture):
        raise StoreError("read-back Capture does not match committed document")
    if result.body is not None:
        stored_body = store.read_capture_body(capture_id)
        if stored_body != result.body:
            raise StoreError("read-back response body does not match committed bytes")
    return capture_id


def _run_gated_capture(
    store: EvidenceStore,
    inputs: SandboxCaptureInputs,
    credentials: DataForSEOCredentials,
    *,
    endpoint: str | None = None,
    client: httpx.Client | None = None,
) -> SandboxCaptureOutcome:
    if type(store) is not EvidenceStore:
        raise TypeError(
            "DataForSEO sandbox transport requires the concrete EvidenceStore "
            "from create_store/open_store"
        )
    parameters = closed_sandbox_parameters(
        keyword=inputs.keyword,
        location_code=inputs.location_code,
        language_code=inputs.language_code,
    )
    request_body = request_body_bytes(parameters)
    document = http_attempt_document(
        parameters=parameters,
        attempt_nonce=inputs.attempt_nonce,
        authorized_at=inputs.authorized_at,
        observatory_version=inputs.observatory_version,
    )
    verified = _issue_verified_attempt(store, document, request_body)
    result = _exchange(verified, credentials, endpoint=endpoint, client=client)
    capture_id = _commit_sandbox_capture(store, verified, result)
    return SandboxCaptureOutcome(
        attempt_id=verified.attempt_id,
        capture_id=capture_id,
        transport_state=result.transport_state,
    )


def capture_dataforseo_sandbox(
    store: EvidenceStore,
    inputs: SandboxCaptureInputs,
    credentials: DataForSEOCredentials,
) -> SandboxCaptureOutcome:
    """Commit Attempt, send the one sandbox exchange, commit at most one Capture."""

    return _run_gated_capture(store, inputs, credentials)


def _generic_cli_error() -> None:
    sys.stderr.write("sandbox capture failed\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="observatory.dataforseo_sandbox",
        description=(
            "One DataForSEO sandbox POST after a committed HTTP-v2 Attempt "
            "(no-spend, no redirect, no retry)."
        ),
    )
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--keyword", required=True)
    parser.add_argument("--location-code", required=True, type=int)
    parser.add_argument("--language-code", required=True)
    args = parser.parse_args(argv)
    try:
        credentials = load_dataforseo_credentials()
    except CredentialError as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    try:
        store = _open_or_create(args.evidence_root)
        inputs = SandboxCaptureInputs(
            keyword=args.keyword,
            location_code=args.location_code,
            language_code=args.language_code,
            attempt_nonce=_fresh_nonce(),
            authorized_at=_utc_now(),
            observatory_version=__version__,
        )
        outcome = capture_dataforseo_sandbox(store, inputs, credentials)
    except Exception:
        _generic_cli_error()
        return 1
    sys.stdout.write(f"attempt_id {outcome.attempt_id}\n")
    sys.stdout.write(f"capture_id {outcome.capture_id}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
