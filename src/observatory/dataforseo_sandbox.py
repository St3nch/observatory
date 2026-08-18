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
from observatory.http_single_exchange import (
    HttpExchangeResult,
    perform_bounded_http_exchange,
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


_LOOPBACK_ERROR: Final[str] = "loopback endpoint is not the authorized local override"
_CREDENTIAL_ECHO_ERROR: Final[str] = "response contained credential material"


def _require_loopback_endpoint(endpoint: str) -> None:
    try:
        parsed = urlparse(endpoint)
        port = parsed.port
    except ValueError as exc:
        raise StoreError(_LOOPBACK_ERROR) from exc
    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or port is None
        or port < 1
        or port > 65535
        or parsed.path != HTTP_PATH
        or parsed.params != ""
        or parsed.query != ""
        or parsed.fragment != ""
        or parsed.username is not None
        or parsed.password is not None
        or parsed.netloc != f"127.0.0.1:{port}"
    ):
        raise StoreError(_LOOPBACK_ERROR)


def _resolved_exchange_url(endpoint: str | None) -> str:
    if endpoint is None:
        return PRODUCTION_URL
    _require_loopback_endpoint(endpoint)
    return endpoint


def _reject_credential_echo(
    credentials: DataForSEOCredentials,
    result: HttpExchangeResult,
) -> None:
    credentials.require_nonempty()
    if result.body is not None and credentials.contains_secret_bytes(result.body):
        raise StoreError(_CREDENTIAL_ECHO_ERROR)
    response = result.response
    if not isinstance(response, Mapping):
        return
    headers = response.get("headers")
    if not isinstance(headers, list):
        return
    for pair in headers:
        if not isinstance(pair, list) or len(pair) != 2:
            continue
        value = pair[1]
        if isinstance(value, str) and credentials.contains_secret_text(value):
            raise StoreError(_CREDENTIAL_ECHO_ERROR)


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
    ) -> HttpExchangeResult:
        if type(attempt) is not _VerifiedAttempt or not _is_issued(attempt):
            raise TypeError(
                "DataForSEO sandbox transport requires a verified committed Attempt"
            )
        if attempt._used:
            raise StoreError("sandbox transport capability is one-exchange only")
        credentials.require_nonempty()
        url = _resolved_exchange_url(endpoint)
        object.__setattr__(attempt, "_used", True)
        document = attempt.document
        _require_sandbox_target(document)
        authorization = credentials.basic_authorization_header()
        return perform_bounded_http_exchange(
            url=url,
            body=bytes(attempt.request_body),
            application_headers=HTTP_HEADERS,
            authorization=authorization,
            timeout=_TIMEOUT,
            max_response_body_bytes=MAX_RESPONSE_BODY_BYTES,
            client=client,
        )

    return issue, exchange, _VerifiedAttempt


_issue_verified_attempt: Any
_exchange: Any
_VerifiedAttempt: type
_issue_verified_attempt, _exchange, _VerifiedAttempt = _build_transport_gate()


def _commit_sandbox_capture(
    store: EvidenceStore,
    capability: Any,
    result: HttpExchangeResult,
    credentials: DataForSEOCredentials,
) -> str:
    _reject_credential_echo(credentials, result)
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
    credentials.require_nonempty()
    if endpoint is not None:
        _require_loopback_endpoint(endpoint)
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
    capture_id = _commit_sandbox_capture(store, verified, result, credentials)
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
