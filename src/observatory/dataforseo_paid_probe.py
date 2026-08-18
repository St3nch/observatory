"""DataForSEO Keyword Overview paid probe: one gated POST, at most one Capture."""

from __future__ import annotations

import argparse
import secrets
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final
from urllib.parse import urlparse

import httpx

from observatory import __version__
from observatory.capture_event import (
    HTTP_HEADERS,
    HTTP_PROVIDER,
    PAID_ADAPTER_CONTRACT,
    PAID_AUTHORIZED_COST_MICRO_USD,
    PAID_HOST,
    PAID_PATH,
    PAID_POLICY,
    canonical_json,
    content_digest,
    paid_http_attempt_document,
    paid_http_capture_document,
    validate_paid_http_parameters,
)
from observatory.evidence_store import (
    EvidenceStore,
    IntegrityError,
    StoreError,
    create_store,
    inspect_store,
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

PRODUCTION_URL: Final[str] = f"https://{PAID_HOST}{PAID_PATH}"
MAX_RESPONSE_BODY_BYTES: Final[int] = 8_388_608
_TIMEOUT: Final[httpx.Timeout] = httpx.Timeout(30.0)
_LOOPBACK_ERROR: Final[str] = "loopback endpoint is not the authorized local override"
_CREDENTIAL_ECHO_ERROR: Final[str] = "response contained credential material"
_ONE_SHOT_ERROR: Final[str] = "store already has a committed paid-probe Attempt"
_AUTHORIZE_ERROR: Final[str] = "paid probe requires --authorize-max-micro-usd 20000"
_INSPECT_COMPLETE_ERROR: Final[str] = (
    "inspect requires a verified complete paid-probe Capture"
)
_INSPECT_INVALID_ERROR: Final[str] = "inspect rejected invalid Evidence"
_INSPECT_ID_ERROR: Final[str] = "inspect capture-id is invalid"
_CAPTURE_FAILED: Final[str] = "paid probe capture failed"

__all__ = [
    "PaidProbeInputs",
    "PaidProbeOutcome",
    "capture_dataforseo_paid_probe",
    "closed_paid_parameters",
    "inspect_paid_probe_body",
    "main",
    "paid_request_body_bytes",
]


@dataclass(frozen=True)
class PaidProbeInputs:
    """Caller-supplied paid keywords plus frozen authorization fields."""

    keywords: tuple[str, ...]
    attempt_nonce: str
    authorized_at: str
    observatory_version: str


@dataclass(frozen=True)
class PaidProbeOutcome:
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


def paid_request_body_bytes(parameters: Mapping[str, object]) -> bytes:
    """Return JCS(singleton task array) for validated paid HTTP-v2 parameters."""

    task = {key: parameters[key] for key in parameters if key != "contract"}
    return canonical_json([task])


def closed_paid_parameters(*, keywords: Sequence[str]) -> dict[str, object]:
    return validate_paid_http_parameters(
        {
            "contract": PAID_ADAPTER_CONTRACT,
            "include_clickstream_data": False,
            "include_serp_info": False,
            "keywords": list(keywords),
            "language_code": "en",
            "location_code": 2840,
        }
    )


def _require_authorization(authorize_max_micro_usd: object) -> None:
    if (
        type(authorize_max_micro_usd) is not int
        or authorize_max_micro_usd != PAID_AUTHORIZED_COST_MICRO_USD
    ):
        raise StoreError(_AUTHORIZE_ERROR)


def _paid_attempt_exists(store: EvidenceStore) -> bool:
    for attempt_id in store.list_committed_ids("attempts"):
        document = store.read_attempt(attempt_id)
        if document is None:
            continue
        if document.get("adapter_contract") == PAID_ADAPTER_CONTRACT:
            return True
    return False


def _refuse_second_paid_attempt(store: EvidenceStore) -> None:
    if _paid_attempt_exists(store):
        raise StoreError(_ONE_SHOT_ERROR)


def _require_paid_target(document: Mapping[str, object]) -> None:
    if document.get("adapter_contract") != PAID_ADAPTER_CONTRACT:
        raise StoreError("frozen Attempt is not the paid adapter contract")
    if document.get("version") != 2:
        raise StoreError("frozen Attempt is not HTTP event version 2")
    if document.get("provider") != HTTP_PROVIDER:
        raise StoreError("frozen Attempt is not the paid provider")
    if document.get("policy") != PAID_POLICY:
        raise StoreError("frozen Attempt is not the paid_probe policy")
    request = document.get("request")
    if not isinstance(request, Mapping):
        raise StoreError("frozen Attempt request is missing")
    if (
        request.get("scheme") != "https"
        or request.get("host") != PAID_HOST
        or request.get("port") is not None
        or request.get("path") != PAID_PATH
        or request.get("method") != "POST"
        or request.get("query") != []
        or request.get("headers") != HTTP_HEADERS
    ):
        raise StoreError("frozen Attempt is not the paid HTTP target")
    parameters = document.get("parameters")
    if not isinstance(parameters, Mapping):
        raise StoreError("frozen Attempt parameters are missing")
    keywords = parameters.get("keywords")
    if not isinstance(keywords, list) or not (1 <= len(keywords) <= 5):
        raise StoreError("frozen Attempt does not have 1..5 keywords")
    if parameters.get("include_serp_info") is not False:
        raise StoreError("frozen Attempt does not keep include_serp_info off")
    if parameters.get("include_clickstream_data") is not False:
        raise StoreError("frozen Attempt does not keep include_clickstream_data off")
    if parameters.get("location_code") != 2840:
        raise StoreError("frozen Attempt is not location_code 2840")
    if parameters.get("language_code") != "en":
        raise StoreError("frozen Attempt is not language_code en")
    policy = document.get("policy")
    if not isinstance(policy, Mapping):
        raise StoreError("frozen Attempt policy is missing")
    if policy.get("max_authorized_cost_micro_usd") != PAID_AUTHORIZED_COST_MICRO_USD:
        raise StoreError("frozen Attempt authorization ceiling is not 20000")


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
        or parsed.path != PAID_PATH
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
        *,
        authorize_max_micro_usd: object,
    ) -> _VerifiedAttempt:
        _require_authorization(authorize_max_micro_usd)
        if type(store) is not EvidenceStore:
            raise TypeError(
                "DataForSEO paid probe transport requires the concrete EvidenceStore "
                "from create_store/open_store"
            )
        inspector = inspect_store(store.root)
        _refuse_second_paid_attempt(inspector)
        _require_paid_target(document)
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
        _require_paid_target(read_back)
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
                "DataForSEO paid probe transport requires a verified committed Attempt"
            )
        if attempt._used:
            raise StoreError("paid probe transport capability is one-exchange only")
        credentials.require_nonempty()
        url = _resolved_exchange_url(endpoint)
        object.__setattr__(attempt, "_used", True)
        document = attempt.document
        _require_paid_target(document)
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


def _commit_paid_capture(
    store: EvidenceStore,
    capability: Any,
    result: HttpExchangeResult,
    credentials: DataForSEOCredentials,
) -> str:
    _reject_credential_echo(credentials, result)
    capture = paid_http_capture_document(
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
    inputs: PaidProbeInputs,
    credentials: DataForSEOCredentials,
    authorize_max_micro_usd: int,
    *,
    endpoint: str | None = None,
    client: httpx.Client | None = None,
) -> PaidProbeOutcome:
    if type(store) is not EvidenceStore:
        raise TypeError(
            "DataForSEO paid probe transport requires the concrete EvidenceStore "
            "from create_store/open_store"
        )
    _require_authorization(authorize_max_micro_usd)
    credentials.require_nonempty()
    if endpoint is not None:
        _require_loopback_endpoint(endpoint)
    inspector = inspect_store(store.root)
    _refuse_second_paid_attempt(inspector)
    parameters = closed_paid_parameters(keywords=inputs.keywords)
    request_body = paid_request_body_bytes(parameters)
    document = paid_http_attempt_document(
        parameters=parameters,
        attempt_nonce=inputs.attempt_nonce,
        authorized_at=inputs.authorized_at,
        observatory_version=inputs.observatory_version,
    )
    verified = _issue_verified_attempt(
        store,
        document,
        request_body,
        authorize_max_micro_usd=authorize_max_micro_usd,
    )
    result = _exchange(verified, credentials, endpoint=endpoint, client=client)
    capture_id = _commit_paid_capture(store, verified, result, credentials)
    return PaidProbeOutcome(
        attempt_id=verified.attempt_id,
        capture_id=capture_id,
        transport_state=result.transport_state,
    )


def capture_dataforseo_paid_probe(
    store: EvidenceStore,
    inputs: PaidProbeInputs,
    credentials: DataForSEOCredentials,
    authorize_max_micro_usd: int,
) -> PaidProbeOutcome:
    """Commit Attempt, send the one paid exchange, commit at most one Capture."""

    return _run_gated_capture(store, inputs, credentials, authorize_max_micro_usd)


def inspect_paid_probe_body(store: EvidenceStore, capture_id: str) -> bytes:
    """Return exact complete paid-probe response-body bytes. No mutation."""

    if not isinstance(capture_id, str) or len(capture_id) != 64:
        raise StoreError(_INSPECT_ID_ERROR)
    try:
        int(capture_id, 16)
    except ValueError as exc:
        raise StoreError(_INSPECT_ID_ERROR) from exc
    if capture_id != capture_id.lower():
        raise StoreError(_INSPECT_ID_ERROR)
    try:
        capture = store.read_capture(capture_id)
    except IntegrityError as exc:
        raise StoreError(_INSPECT_INVALID_ERROR) from exc
    if capture is None:
        raise StoreError(_INSPECT_COMPLETE_ERROR)
    if (
        capture.get("adapter_contract") != PAID_ADAPTER_CONTRACT
        or capture.get("version") != 2
        or capture.get("transport_state") != "response_complete"
    ):
        raise StoreError(_INSPECT_COMPLETE_ERROR)
    response = capture.get("response")
    if not isinstance(response, Mapping):
        raise StoreError(_INSPECT_COMPLETE_ERROR)
    if response.get("completeness") != "complete":
        raise StoreError(_INSPECT_COMPLETE_ERROR)
    body_state = response.get("body")
    if not isinstance(body_state, Mapping) or body_state.get("state") != "present_nonempty":
        raise StoreError(_INSPECT_COMPLETE_ERROR)
    body = store.read_capture_body(capture_id)
    if body is None or len(body) == 0:
        raise StoreError(_INSPECT_COMPLETE_ERROR)
    return body


def _open_or_create(root: Path) -> EvidenceStore:
    if (root / "FORMAT.json").is_file():
        inspector = inspect_store(root)
        _refuse_second_paid_attempt(inspector)
        return open_store(root)
    return create_store(root)


def _generic_capture_error() -> None:
    sys.stderr.write(f"{_CAPTURE_FAILED}\n")


def _run_capture_cli(args: argparse.Namespace) -> int:
    try:
        credentials = load_dataforseo_credentials()
    except CredentialError as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    try:
        _require_authorization(args.authorize_max_micro_usd)
        store = _open_or_create(args.evidence_root)
        inputs = PaidProbeInputs(
            keywords=tuple(args.keyword),
            attempt_nonce=_fresh_nonce(),
            authorized_at=_utc_now(),
            observatory_version=__version__,
        )
        outcome = capture_dataforseo_paid_probe(
            store,
            inputs,
            credentials,
            args.authorize_max_micro_usd,
        )
    except Exception:
        _generic_capture_error()
        return 1
    sys.stdout.write(f"attempt_id {outcome.attempt_id}\n")
    sys.stdout.write(f"capture_id {outcome.capture_id}\n")
    return 0


def _run_inspect_cli(args: argparse.Namespace) -> int:
    try:
        store = inspect_store(args.evidence_root)
        body = inspect_paid_probe_body(store, args.capture_id)
    except StoreError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1
    except Exception:
        sys.stderr.write(f"{_INSPECT_INVALID_ERROR}\n")
        return 1
    sys.stdout.buffer.write(body)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="observatory.dataforseo_paid_probe",
        description=(
            "One DataForSEO Keyword Overview paid POST after a committed "
            "HTTP-v2 Attempt, or a read-only body inspect."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    capture = sub.add_parser("capture")
    capture.add_argument("--evidence-root", required=True, type=Path)
    capture.add_argument("--keyword", required=True, action="append")
    capture.add_argument("--authorize-max-micro-usd", required=True, type=int)

    inspect_cmd = sub.add_parser("inspect")
    inspect_cmd.add_argument("--evidence-root", required=True, type=Path)
    inspect_cmd.add_argument("--capture-id", required=True)

    args = parser.parse_args(argv)
    if args.command == "capture":
        return _run_capture_cli(args)
    if args.command == "inspect":
        return _run_inspect_cli(args)
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
