"""DataForSEO Labs Google Related Keywords Live paid probe: one gated POST.

The transport gate is hardened from birth (RK-01). Closure-owned issuance state is the
sole authority for what is sent, for replay refusal, for the Capture's parent Attempt, and
for the returned capture-result ``attempt_id``. Caller-visible capability attributes are
mirrors with no authority at any point in the lifecycle.
"""

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
    HTTP_HEADERS,
    HTTP_PROVIDER,
    RELATED_KEYWORDS_ADAPTER_CONTRACT,
    RELATED_KEYWORDS_AUTHORIZED_COST_MICRO_USD,
    RELATED_KEYWORDS_HOST,
    RELATED_KEYWORDS_PATH,
    RELATED_KEYWORDS_POLICY,
    DocumentError,
    canonical_json,
    content_digest,
    related_keywords_http_attempt_document,
    related_keywords_http_capture_document,
    validate_attempt,
    validate_related_keywords_http_parameters,
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

PRODUCTION_URL: Final[str] = f"https://{RELATED_KEYWORDS_HOST}{RELATED_KEYWORDS_PATH}"
MAX_RESPONSE_BODY_BYTES: Final[int] = 33_554_432
_TIMEOUT: Final[httpx.Timeout] = httpx.Timeout(
    connect=30.0,
    read=120.0,
    write=30.0,
    pool=30.0,
)
_LOOPBACK_ERROR: Final[str] = "loopback endpoint is not the authorized local override"
_CREDENTIAL_ECHO_ERROR: Final[str] = "response contained credential material"
_ONE_SHOT_ERROR: Final[str] = (
    "store already has a committed related-keywords paid-probe Attempt"
)
_AUTHORIZE_ERROR: Final[str] = (
    "related keywords paid probe requires --authorize-max-micro-usd 200000"
)
_INSPECT_COMPLETE_ERROR: Final[str] = (
    "inspect requires a verified complete related-keywords paid-probe Capture"
)
_INSPECT_INVALID_ERROR: Final[str] = "inspect rejected invalid Evidence"
_INSPECT_ID_ERROR: Final[str] = "inspect capture-id is invalid"
_CAPTURE_FAILED: Final[str] = "related keywords paid probe capture failed"
_ONE_EXCHANGE_ERROR: Final[str] = (
    "related keywords paid probe transport capability is one-exchange only"
)
_ISSUANCE_MISMATCH_ERROR: Final[str] = (
    "issued transport capability does not match the closure-owned issuance record"
)
_VERIFY_ON_READ_ERROR: Final[str] = "committed Attempt failed verify-on-read"
_UNVERIFIED_CAPABILITY_ERROR: Final[str] = (
    "DataForSEO related keywords paid probe transport requires a verified "
    "committed Attempt"
)
_CONCRETE_STORE_ERROR: Final[str] = (
    "DataForSEO related keywords paid probe transport requires the concrete "
    "EvidenceStore from create_store/open_store"
)

__all__ = [
    "RelatedKeywordsPaidProbeInputs",
    "RelatedKeywordsPaidProbeOutcome",
    "capture_dataforseo_google_related_keywords_paid_probe",
    "closed_related_keywords_parameters",
    "inspect_related_keywords_paid_probe_body",
    "main",
    "related_keywords_request_body_bytes",
]


@dataclass(frozen=True)
class RelatedKeywordsPaidProbeInputs:
    """Caller-supplied seed keyword plus frozen authorization fields."""

    keyword: str
    attempt_nonce: str
    authorized_at: str
    observatory_version: str


@dataclass(frozen=True)
class RelatedKeywordsPaidProbeOutcome:
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


def related_keywords_request_body_bytes(parameters: Mapping[str, object]) -> bytes:
    """Return JCS(singleton task array) for validated Related Keywords parameters."""

    task = {key: parameters[key] for key in parameters if key != "contract"}
    return canonical_json([task])


def closed_related_keywords_parameters(*, keyword: str) -> dict[str, object]:
    """Build the one closed Related Keywords task. Only the seed keyword varies."""

    return validate_related_keywords_http_parameters(
        {
            "contract": RELATED_KEYWORDS_ADAPTER_CONTRACT,
            "depth": 3,
            "ignore_synonyms": False,
            "include_clickstream_data": False,
            "include_seed_keyword": True,
            "include_serp_info": True,
            "keyword": keyword,
            "language_code": "en",
            "limit": 1000,
            "location_code": 2840,
            "offset": 0,
            "order_by": ["keyword_data.keyword_info.search_volume,desc"],
            "replace_with_core_keyword": False,
        }
    )


def _require_authorization(authorize_max_micro_usd: object) -> None:
    if (
        type(authorize_max_micro_usd) is not int
        or authorize_max_micro_usd != RELATED_KEYWORDS_AUTHORIZED_COST_MICRO_USD
    ):
        raise StoreError(_AUTHORIZE_ERROR)


def _related_keywords_attempt_exists(store: EvidenceStore) -> bool:
    for attempt_id in store.list_committed_ids("attempts"):
        document = store.read_attempt(attempt_id)
        if document is None:
            continue
        if document.get("adapter_contract") == RELATED_KEYWORDS_ADAPTER_CONTRACT:
            return True
    return False


def _refuse_second_related_keywords_attempt(store: EvidenceStore) -> None:
    if _related_keywords_attempt_exists(store):
        raise StoreError(_ONE_SHOT_ERROR)


def _require_related_keywords_target(document: Mapping[str, object]) -> None:
    if document.get("adapter_contract") != RELATED_KEYWORDS_ADAPTER_CONTRACT:
        raise StoreError("frozen Attempt is not the related-keywords adapter contract")
    if document.get("version") != 2:
        raise StoreError("frozen Attempt is not HTTP event version 2")
    if document.get("provider") != HTTP_PROVIDER:
        raise StoreError("frozen Attempt is not the related-keywords provider")
    if document.get("policy") != RELATED_KEYWORDS_POLICY:
        raise StoreError("frozen Attempt is not the related-keywords paid_probe policy")
    request = document.get("request")
    if not isinstance(request, Mapping):
        raise StoreError("frozen Attempt request is missing")
    if (
        request.get("scheme") != "https"
        or request.get("host") != RELATED_KEYWORDS_HOST
        or request.get("port") is not None
        or request.get("path") != RELATED_KEYWORDS_PATH
        or request.get("method") != "POST"
        or request.get("query") != []
        or request.get("headers") != HTTP_HEADERS
    ):
        raise StoreError("frozen Attempt is not the related-keywords HTTP target")
    parameters = document.get("parameters")
    if not isinstance(parameters, Mapping):
        raise StoreError("frozen Attempt parameters are missing")
    if not isinstance(parameters.get("keyword"), str):
        raise StoreError("frozen Attempt does not have one seed keyword")
    if parameters.get("location_code") != 2840:
        raise StoreError("frozen Attempt is not location_code 2840")
    if parameters.get("language_code") != "en":
        raise StoreError("frozen Attempt is not language_code en")
    if parameters.get("depth") != 3:
        raise StoreError("frozen Attempt is not depth 3")
    if parameters.get("limit") != 1000:
        raise StoreError("frozen Attempt is not limit 1000")
    if parameters.get("offset") != 0:
        raise StoreError("frozen Attempt is not offset 0")
    if parameters.get("order_by") != ["keyword_data.keyword_info.search_volume,desc"]:
        raise StoreError("frozen Attempt is not the closed related-keywords ordering")
    if parameters.get("include_seed_keyword") is not True:
        raise StoreError("frozen Attempt does not keep include_seed_keyword on")
    if parameters.get("include_serp_info") is not True:
        raise StoreError("frozen Attempt does not keep include_serp_info on")
    if parameters.get("include_clickstream_data") is not False:
        raise StoreError("frozen Attempt does not keep include_clickstream_data off")
    if parameters.get("ignore_synonyms") is not False:
        raise StoreError("frozen Attempt does not keep ignore_synonyms off")
    if parameters.get("replace_with_core_keyword") is not False:
        raise StoreError("frozen Attempt does not keep replace_with_core_keyword off")
    policy = document.get("policy")
    if not isinstance(policy, Mapping):
        raise StoreError("frozen Attempt policy is missing")
    if (
        policy.get("max_authorized_cost_micro_usd")
        != RELATED_KEYWORDS_AUTHORIZED_COST_MICRO_USD
    ):
        raise StoreError("frozen Attempt authorization ceiling is not 200000")


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
        or parsed.path != RELATED_KEYWORDS_PATH
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


def _build_transport_gate() -> tuple[Any, Any, Any, type]:
    class _Issuance:
        """Closure-owned issuance record. Not a capability attribute."""

        __slots__ = (
            "capability",
            "store",
            "attempt_id",
            "document_preimage",
            "request_body",
            "consumed",
        )
        capability: object
        store: EvidenceStore
        attempt_id: str
        document_preimage: bytes
        request_body: bytes
        consumed: bool

        def __init__(
            self,
            *,
            capability: object,
            store: EvidenceStore,
            attempt_id: str,
            document_preimage: bytes,
            request_body: bytes,
        ) -> None:
            self.capability = capability
            self.store = store
            self.attempt_id = attempt_id
            self.document_preimage = document_preimage
            self.request_body = request_body
            self.consumed = False

    issued: list[_Issuance] = []

    class _VerifiedAttempt:
        """Internal capability. Not supported public API. Fields are mirrors only."""

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

    def _issuance_for(attempt: object) -> _Issuance | None:
        for record in issued:
            if record.capability is attempt:
                return record
        return None

    def _require_issued(attempt: object) -> _Issuance:
        if type(attempt) is not _VerifiedAttempt:
            raise TypeError(_UNVERIFIED_CAPABILITY_ERROR)
        record = _issuance_for(attempt)
        if record is None or record.capability is not attempt:
            raise TypeError(_UNVERIFIED_CAPABILITY_ERROR)
        return record

    def _require_visible_fields_match(attempt: Any, record: _Issuance) -> None:
        try:
            visible_id = attempt.attempt_id
            visible_document = attempt.document
            visible_body = attempt.request_body
        except AttributeError as exc:
            raise StoreError("issued transport capability is missing issuance fields") from exc
        if visible_id != record.attempt_id:
            raise StoreError(_ISSUANCE_MISMATCH_ERROR)
        try:
            visible_preimage = canonical_json(visible_document)
        except DocumentError as exc:
            raise StoreError(_ISSUANCE_MISMATCH_ERROR) from exc
        if visible_preimage != record.document_preimage:
            raise StoreError(_ISSUANCE_MISMATCH_ERROR)
        if not isinstance(visible_body, (bytes, bytearray)):
            raise StoreError(_ISSUANCE_MISMATCH_ERROR)
        if bytes(visible_body) != record.request_body:
            raise StoreError(_ISSUANCE_MISMATCH_ERROR)

    def _revalidate_committed(record: _Issuance) -> bytes:
        store = record.store
        if type(store) is not EvidenceStore:
            raise TypeError(_CONCRETE_STORE_ERROR)
        try:
            read_back = store.read_attempt(record.attempt_id)
        except IntegrityError as exc:
            raise StoreError(_VERIFY_ON_READ_ERROR) from exc
        if read_back is None:
            raise StoreError("committed Attempt is not readable as Evidence")
        read_preimage = canonical_json(read_back)
        if content_digest(read_preimage) != record.attempt_id:
            raise StoreError("read-back Attempt identity does not match")
        if read_preimage != record.document_preimage:
            raise StoreError("read-back Attempt does not match committed document")
        fingerprint = read_back.get("request_fingerprint")
        authorized_at = read_back.get("authorized_at")
        if not isinstance(fingerprint, str) or not isinstance(authorized_at, str):
            raise StoreError("frozen Attempt path fields are missing")
        bundle = store.attempt_path(fingerprint, authorized_at, record.attempt_id)
        try:
            verified = store.verify_attempt_directory(bundle)
        except IntegrityError as exc:
            raise StoreError(_VERIFY_ON_READ_ERROR) from exc
        if canonical_json(verified) != record.document_preimage:
            raise StoreError("read-back Attempt does not match committed document")
        if content_digest(canonical_json(verified)) != record.attempt_id:
            raise StoreError("read-back Attempt identity does not match")
        try:
            stored_body = (bundle / "request.body").read_bytes()
        except OSError as exc:
            raise StoreError("committed request body is not readable as Evidence") from exc
        if stored_body != record.request_body:
            raise StoreError("read-back request body does not match committed bytes")
        parameters = verified.get("parameters")
        if not isinstance(parameters, Mapping):
            raise StoreError("frozen Attempt parameters are missing")
        try:
            closed = validate_related_keywords_http_parameters(parameters)
        except DocumentError as exc:
            raise StoreError(
                "frozen Attempt parameters are not the closed related-keywords contract"
            ) from exc
        recomputed = related_keywords_request_body_bytes(closed)
        if recomputed != stored_body or recomputed != record.request_body:
            raise StoreError("recomputed request body does not match committed bytes")
        _require_related_keywords_target(verified)
        return bytes(record.request_body)

    def issue(
        store: EvidenceStore,
        document: Mapping[str, object],
        request_body: bytes,
        *,
        authorize_max_micro_usd: object,
    ) -> _VerifiedAttempt:
        _require_authorization(authorize_max_micro_usd)
        if type(store) is not EvidenceStore:
            raise TypeError(_CONCRETE_STORE_ERROR)
        inspector = inspect_store(store.root)
        _refuse_second_related_keywords_attempt(inspector)
        _require_related_keywords_target(document)
        attempt_id = store.commit_attempt(document, request_body=request_body)
        read_back = store.read_attempt(attempt_id)
        if read_back is None:
            raise StoreError("committed Attempt is not readable as Evidence")
        preimage = canonical_json(read_back)
        if content_digest(preimage) != attempt_id:
            raise StoreError("read-back Attempt identity does not match")
        if preimage != canonical_json(document):
            raise StoreError("read-back Attempt does not match committed document")
        bundle = store.attempt_path(
            str(read_back["request_fingerprint"]),
            str(read_back["authorized_at"]),
            attempt_id,
        )
        stored_body = (bundle / "request.body").read_bytes()
        if stored_body != request_body:
            raise StoreError("read-back request body does not match committed bytes")
        _require_related_keywords_target(read_back)
        committed_body = bytes(stored_body)
        capability = object.__new__(_VerifiedAttempt)
        object.__setattr__(capability, "attempt_id", attempt_id)
        object.__setattr__(capability, "document", _freeze_maps(read_back))
        object.__setattr__(capability, "request_body", committed_body)
        object.__setattr__(capability, "_used", False)
        issued.append(
            _Issuance(
                capability=capability,
                store=store,
                attempt_id=attempt_id,
                document_preimage=preimage,
                request_body=committed_body,
            )
        )
        return capability

    def exchange(
        attempt: object,
        credentials: DataForSEOCredentials,
        *,
        endpoint: str | None = None,
        client: httpx.Client | None = None,
        max_response_body_bytes: int | None = None,
    ) -> HttpExchangeResult:
        record = _require_issued(attempt)
        if record.consumed:
            raise StoreError(_ONE_EXCHANGE_ERROR)
        credentials.require_nonempty()
        url = _resolved_exchange_url(endpoint)
        record.consumed = True
        object.__setattr__(attempt, "_used", True)
        _require_visible_fields_match(attempt, record)
        body = _revalidate_committed(record)
        authorization = credentials.basic_authorization_header()
        ceiling = (
            MAX_RESPONSE_BODY_BYTES
            if max_response_body_bytes is None
            else max_response_body_bytes
        )
        return perform_bounded_http_exchange(
            url=url,
            body=body,
            application_headers=HTTP_HEADERS,
            authorization=authorization,
            timeout=_TIMEOUT,
            max_response_body_bytes=ceiling,
            client=client,
        )

    def _committed_snapshot(record: _Issuance) -> dict[str, object]:
        """Rebuild a detached Attempt document from closure-owned immutable bytes.

        The closure retains only ``document_preimage`` bytes and ``attempt_id``. Every call
        re-parses and re-validates those bytes into fresh objects, so no authoritative
        mapping - and no mutable child of one - is ever handed to a caller. Mutating the
        returned snapshot cannot reach closure authority.
        """

        snapshot = validate_attempt(record.document_preimage)
        if canonical_json(snapshot) != record.document_preimage:
            raise StoreError("closure-owned Attempt snapshot does not re-canonicalize")
        if content_digest(canonical_json(snapshot)) != record.attempt_id:
            raise StoreError("closure-owned Attempt snapshot identity does not match")
        return snapshot

    def committed_attempt(attempt: object) -> tuple[str, dict[str, object]]:
        """Return closure-owned committed identity plus a detached Attempt snapshot.

        This is the smallest accessor needed so Capture commit and the returned capture
        result stay authoritative after exchange, closing the post-exchange caller-visible
        mirror window that PF-16/PF-17 deliberately left in scope-bounded remediation. The
        snapshot is rebuilt from immutable closure bytes on every call and is safe to hand
        out: it aliases no closure state.
        """

        record = _require_issued(attempt)
        return record.attempt_id, _committed_snapshot(record)

    return issue, exchange, committed_attempt, _VerifiedAttempt


_issue_verified_attempt: Any
_exchange: Any
_committed_attempt: Any
_VerifiedAttempt: type
(
    _issue_verified_attempt,
    _exchange,
    _committed_attempt,
    _VerifiedAttempt,
) = _build_transport_gate()


def _commit_related_keywords_capture(
    store: EvidenceStore,
    capability: Any,
    result: HttpExchangeResult,
    credentials: DataForSEOCredentials,
) -> str:
    _reject_credential_echo(credentials, result)
    _, committed_document = _committed_attempt(capability)
    capture = related_keywords_http_capture_document(
        attempt=committed_document,
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
    inputs: RelatedKeywordsPaidProbeInputs,
    credentials: DataForSEOCredentials,
    authorize_max_micro_usd: int,
    *,
    endpoint: str | None = None,
    client: httpx.Client | None = None,
    max_response_body_bytes: int | None = None,
) -> RelatedKeywordsPaidProbeOutcome:
    if type(store) is not EvidenceStore:
        raise TypeError(_CONCRETE_STORE_ERROR)
    _require_authorization(authorize_max_micro_usd)
    credentials.require_nonempty()
    if endpoint is not None:
        _require_loopback_endpoint(endpoint)
    inspector = inspect_store(store.root)
    _refuse_second_related_keywords_attempt(inspector)
    parameters = closed_related_keywords_parameters(keyword=inputs.keyword)
    request_body = related_keywords_request_body_bytes(parameters)
    document = related_keywords_http_attempt_document(
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
    result = _exchange(
        verified,
        credentials,
        endpoint=endpoint,
        client=client,
        max_response_body_bytes=max_response_body_bytes,
    )
    capture_id = _commit_related_keywords_capture(store, verified, result, credentials)
    committed_attempt_id, _ = _committed_attempt(verified)
    return RelatedKeywordsPaidProbeOutcome(
        attempt_id=committed_attempt_id,
        capture_id=capture_id,
        transport_state=result.transport_state,
    )


def capture_dataforseo_google_related_keywords_paid_probe(
    store: EvidenceStore,
    inputs: RelatedKeywordsPaidProbeInputs,
    credentials: DataForSEOCredentials,
    authorize_max_micro_usd: int,
) -> RelatedKeywordsPaidProbeOutcome:
    """Commit Attempt, send the one Related Keywords exchange, commit at most one Capture."""

    return _run_gated_capture(store, inputs, credentials, authorize_max_micro_usd)


def inspect_related_keywords_paid_probe_body(store: EvidenceStore, capture_id: str) -> bytes:
    """Return exact complete Related Keywords response-body bytes. No parsing, no mutation."""

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
        capture.get("adapter_contract") != RELATED_KEYWORDS_ADAPTER_CONTRACT
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
        _refuse_second_related_keywords_attempt(inspector)
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
        inputs = RelatedKeywordsPaidProbeInputs(
            keyword=args.keyword,
            attempt_nonce=_fresh_nonce(),
            authorized_at=_utc_now(),
            observatory_version=__version__,
        )
        outcome = capture_dataforseo_google_related_keywords_paid_probe(
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
        body = inspect_related_keywords_paid_probe_body(store, args.capture_id)
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
        prog="observatory.dataforseo_google_related_keywords_paid_probe",
        description=(
            "One DataForSEO Labs Google Related Keywords Live paid POST after a "
            "committed HTTP-v2 Attempt, or a read-only body inspect."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    capture = sub.add_parser("capture")
    capture.add_argument("--evidence-root", required=True, type=Path)
    capture.add_argument("--keyword", required=True)
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
