"""AI-13: Historical Live paid-probe contract, gate, and inspect."""

from __future__ import annotations

import base64
import copy
import hashlib
import inspect
import json
import pickle
import socket
import threading
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

import httpx
import pytest

from observatory.capture import PUBLISHED_AR_INPUTS, capture_fixture
from observatory.capture_event import (
    HISTORICAL_ADAPTER_CONTRACT,
    HISTORICAL_AUTHORIZED_COST_MICRO_USD,
    HTTP_ADAPTER_CONTRACT,
    MENTIONS_ADAPTER_CONTRACT,
    ORGANIC_ADAPTER_CONTRACT,
    PAID_ADAPTER_CONTRACT,
    TARGET_METRICS_ADAPTER_CONTRACT,
    DocumentError,
    canonical_json,
    content_digest,
    historical_http_attempt_document,
    historical_http_capture_document,
    historical_http_fingerprint_document,
    http_attempt_document,
    http_capture_document,
    mentions_http_attempt_document,
    organic_http_attempt_document,
    paid_http_attempt_document,
    target_metrics_http_attempt_document,
    validate_attempt,
    validate_historical_http_parameters,
    validate_historical_http_request,
    validate_http_parameters,
    validate_mentions_http_parameters,
    validate_organic_http_parameters,
    validate_paid_http_parameters,
    validate_target_metrics_http_parameters,
)
from observatory.dataforseo_ai_optimization_llm_mentions_historical_paid_probe import (
    _TIMEOUT,
    MAX_RESPONSE_BODY_BYTES,
    HistoricalPaidProbeInputs,
    _exchange,
    _issue_verified_attempt,
    _run_gated_capture,
    _VerifiedAttempt,
    capture_dataforseo_ai_optimization_llm_mentions_historical_paid_probe,
    closed_historical_parameters,
    historical_request_body_bytes,
    inspect_historical_paid_probe_body,
    main,
)
from observatory.dataforseo_ai_optimization_search_mentions_paid_probe import (
    _exchange as mentions_exchange,
)
from observatory.dataforseo_ai_optimization_search_mentions_paid_probe import (
    _issue_verified_attempt as issue_mentions,
)
from observatory.dataforseo_ai_optimization_search_mentions_paid_probe import (
    closed_mentions_parameters,
    mentions_request_body_bytes,
)
from observatory.dataforseo_ai_optimization_target_metrics_paid_probe import (
    _exchange as metrics_exchange,
)
from observatory.dataforseo_ai_optimization_target_metrics_paid_probe import (
    _issue_verified_attempt as issue_metrics,
)
from observatory.dataforseo_ai_optimization_target_metrics_paid_probe import (
    closed_target_metrics_parameters,
    target_metrics_request_body_bytes,
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
from observatory.google_organic_derive import derive_google_organic
from observatory.keyword_overview_derive import derive_keyword_overview
from observatory.migrate import connect
from observatory.search_mentions_derive import derive_search_mentions
from observatory.settings import (
    DATAFORSEO_LOGIN_ENV,
    DATAFORSEO_PASSWORD_ENV,
    DataForSEOCredentials,
)
from observatory.target_metrics_derive import derive_target_metrics

SENTINEL_LOGIN = "sentinel-login-ai13-hist11"
SENTINEL_PASSWORD = "sentinel-password-ai13-hist22"
SENTINEL_BASIC = "Basic " + base64.b64encode(
    f"{SENTINEL_LOGIN}:{SENTINEL_PASSWORD}".encode()
).decode("ascii")
AUTHORIZE = 200000
FROZEN_KEYWORD = "generative engine optimization"
NONCE = "8888888888888888888888888888888888888888888888888888888888888888"
AUTHORIZED_AT = "2026-08-25T20:00:00.000000Z"
SOFTWARE = "conformance-llm-mentions-historical-paid-probe-v1"
REQUEST_STARTED_AT = "2026-08-25T20:00:00.100000Z"
RESPONSE_HEADERS_AT = "2026-08-25T20:00:00.200000Z"
RESPONSE_BODY_ENDED_AT = "2026-08-25T20:00:00.300000Z"
TRANSPORT_ENDED_AT = "2026-08-25T20:00:00.400000Z"
HISTORICAL_PATH = "/v3/ai_optimization/llm_mentions/historical/live"

HISTORICAL_REQUEST_BODY = (
    b'[{"date_from":"2025-08-01","date_to":"2026-07-31","language_code":"en",'
    b'"location_code":2840,"platform":"google","target":[{"keyword":'
    b'"generative engine optimization","match_type":"word_match",'
    b'"search_filter":"include","search_scope":["answer"]}]}]'
)
HISTORICAL_REQUEST_BODY_SHA256 = (
    "9f40139201acaa18f72fc14d6ae7b2f582317474bbc9e90f0661a5360740f480"
)
HISTORICAL_FINGERPRINT = (
    "6b4977c1630976a3c6c55680adb5566f3d496aee99abe7614ffbcbd07f02bbb0"
)
HISTORICAL_ATTEMPT_ID = (
    "8f8694807187c47a68b7fcb82185a36df8cddde6f6ec222ca9a11720c4652444"
)
HISTORICAL_RESPONSE_BODY = b'{"ok":true}'
HISTORICAL_RESPONSE_BODY_SHA256 = (
    "4062edaf750fb8074e7e83e0c9028c94e32468a8b6f1614774328ef045150f93"
)
HISTORICAL_CAPTURE_ID = (
    "7b3311189261e0906ea6d6f7dd438c2be2b79615aaa1f63017579e85b35c5084"
)
HTTP_ATTEMPT_ID = "22adc4841c86b7cd98b90bba683aeac204a0cb568428b590fd399e8627eb4640"
PAID_ATTEMPT_ID = "89904bf8a6812fb3d0d845310e4705962bb4db928b80da3be67342dff5def185"
ORGANIC_ATTEMPT_ID = "b577bc1fb75f4ba7576a96c1328fbe74df9d975f3bd03f6c01d7441dfed1a1be"
MENTIONS_ATTEMPT_ID = "5cf959940bec672f8f67bf1f7b5ad18aee2b86fd89e33dd00280f4092cf2741e"
TARGET_METRICS_ATTEMPT_ID = (
    "1d2716ea2a6888c3c7b7aeb0d0ec4f9b5b3f84d4e8780f1ae270d306f89c907d"
)
REPLACEMENT_BODY = (
    b'[{"internal_list_limit":10,"language_code":"en","location_code":2840,'
    b'"platform":"google","target":[{"keyword":"observatory test",'
    b'"match_type":"word_match","search_filter":"include",'
    b'"search_scope":["answer"]}]}]'
)
SMALL_LIMIT = 16
EIGHT_MIB = 8_388_608
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


def _inputs(**overrides: str) -> HistoricalPaidProbeInputs:
    return HistoricalPaidProbeInputs(
        attempt_nonce=overrides.get("attempt_nonce", NONCE),
        authorized_at=overrides.get("authorized_at", AUTHORIZED_AT),
        observatory_version=overrides.get("observatory_version", SOFTWARE),
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
    inputs: HistoricalPaidProbeInputs | None = None,
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
            "body": {"bytes": 11, "sha256": HISTORICAL_RESPONSE_BODY_SHA256},
        },
        "completeness": "complete",
    }


def _historical_attempt() -> dict[str, object]:
    return historical_http_attempt_document(
        parameters=closed_historical_parameters(),
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


def _tree_snapshot(root: Path) -> dict[str, tuple[int, int, bytes]]:
    snapshot: dict[str, tuple[int, int, bytes]] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            stat = path.stat()
            snapshot[str(path.relative_to(root))] = (
                stat.st_ino,
                stat.st_size,
                path.read_bytes(),
            )
    return snapshot


def _assert_no_secrets(*surfaces: object) -> None:
    for surface in surfaces:
        text = surface if isinstance(surface, str) else repr(surface)
        assert SENTINEL_LOGIN not in text
        assert SENTINEL_PASSWORD not in text
        assert SENTINEL_BASIC not in text


def _serve_once(
    response: bytes,
    recorded: dict[str, object],
    store: EvidenceStore,
) -> tuple[int, threading.Thread]:
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
                recorded["attempt_ids"] = store.list_committed_ids("attempts")
                recorded["request_bodies"] = [
                    (
                        store.attempt_path(
                            str(document["request_fingerprint"]),
                            str(document["authorized_at"]),
                            attempt_id,
                        )
                        / "request.body"
                    ).read_bytes()
                    for attempt_id in store.list_committed_ids("attempts")
                    if (document := store.read_attempt(attempt_id)) is not None
                ]
                conn.sendall(response)
        finally:
            sock.close()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return port, thread


def _valid_parameters(**overrides: object) -> dict[str, object]:
    parameters: dict[str, object] = {
        "contract": HISTORICAL_ADAPTER_CONTRACT,
        "date_from": "2025-08-01",
        "date_to": "2026-07-31",
        "language_code": "en",
        "location_code": 2840,
        "platform": "google",
        "target": [
            {
                "keyword": FROZEN_KEYWORD,
                "match_type": "word_match",
                "search_filter": "include",
                "search_scope": ["answer"],
            }
        ],
    }
    parameters.update(overrides)
    return parameters


def _frozen_target(**overrides: object) -> list[dict[str, object]]:
    entry: dict[str, object] = {
        "keyword": FROZEN_KEYWORD,
        "match_type": "word_match",
        "search_filter": "include",
        "search_scope": ["answer"],
    }
    entry.update(overrides)
    return [entry]


def test_independent_literal_vectors() -> None:
    assert hashlib.sha256(HISTORICAL_REQUEST_BODY).hexdigest() == (
        HISTORICAL_REQUEST_BODY_SHA256
    )
    assert hashlib.sha256(HISTORICAL_RESPONSE_BODY).hexdigest() == (
        HISTORICAL_RESPONSE_BODY_SHA256
    )
    assert len(HISTORICAL_REQUEST_BODY) == 247


def test_closed_request_vector_and_attempt_identity() -> None:
    assert inspect.signature(closed_historical_parameters).parameters == {}
    parameters = closed_historical_parameters()
    body = historical_request_body_bytes(parameters)
    assert body == HISTORICAL_REQUEST_BODY
    assert content_digest(body) == HISTORICAL_REQUEST_BODY_SHA256
    assert parameters["contract"] == HISTORICAL_ADAPTER_CONTRACT
    attempt = _historical_attempt()
    request = attempt["request"]
    assert isinstance(request, Mapping)
    fingerprint = historical_http_fingerprint_document(request=request)
    assert content_digest(canonical_json(fingerprint)) == HISTORICAL_FINGERPRINT
    assert content_digest(canonical_json(attempt)) == HISTORICAL_ATTEMPT_ID
    capture = historical_http_capture_document(
        attempt=attempt,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response=_complete_response(),
        transport_failure=None,
        response_headers_at=RESPONSE_HEADERS_AT,
        response_body_ended_at=RESPONSE_BODY_ENDED_AT,
    )
    assert content_digest(canonical_json(capture)) == HISTORICAL_CAPTURE_ID
    assert parameters["platform"] == "google"
    assert parameters["date_from"] == "2025-08-01"
    assert parameters["date_to"] == "2026-07-31"
    assert parameters["location_code"] == 2840
    assert parameters["language_code"] == "en"
    assert "internal_list_limit" not in parameters
    assert "offset" not in parameters
    assert "limit" not in parameters
    target = parameters["target"]
    assert isinstance(target, list) and len(target) == 1
    entry = target[0]
    assert isinstance(entry, Mapping)
    assert entry["keyword"] == FROZEN_KEYWORD
    assert entry["match_type"] == "word_match"
    assert entry["search_filter"] == "include"
    assert entry["search_scope"] == ["answer"]
    task = json.loads(body)
    assert isinstance(task, list) and len(task) == 1
    assert "contract" not in task[0]
    assert task[0]["date_from"] == "2025-08-01"
    assert task[0]["date_to"] == "2026-07-31"


def test_existing_adapter_identities_unchanged() -> None:
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
    organic = organic_http_attempt_document(
        parameters=closed_organic_parameters(keyword="observatory test"),
        attempt_nonce="5555555555555555555555555555555555555555555555555555555555555555",
        authorized_at="2026-08-18T20:00:00.000000Z",
        observatory_version="conformance-google-organic-paid-probe-v1",
    )
    assert content_digest(canonical_json(organic)) == ORGANIC_ATTEMPT_ID
    mentions = mentions_http_attempt_document(
        parameters=closed_mentions_parameters(keyword="observatory test"),
        attempt_nonce="6666666666666666666666666666666666666666666666666666666666666666",
        authorized_at="2026-08-20T20:00:00.000000Z",
        observatory_version="conformance-search-mentions-paid-probe-v1",
    )
    assert content_digest(canonical_json(mentions)) == MENTIONS_ATTEMPT_ID
    metrics = target_metrics_http_attempt_document(
        parameters=closed_target_metrics_parameters(keyword="observatory test"),
        attempt_nonce="7777777777777777777777777777777777777777777777777777777777777777",
        authorized_at="2026-08-23T20:00:00.000000Z",
        observatory_version="conformance-target-metrics-paid-probe-v1",
    )
    assert content_digest(canonical_json(metrics)) == TARGET_METRICS_ATTEMPT_ID
    assert HISTORICAL_ADAPTER_CONTRACT != HTTP_ADAPTER_CONTRACT
    assert HISTORICAL_ADAPTER_CONTRACT != PAID_ADAPTER_CONTRACT
    assert HISTORICAL_ADAPTER_CONTRACT != ORGANIC_ADAPTER_CONTRACT
    assert HISTORICAL_ADAPTER_CONTRACT != MENTIONS_ADAPTER_CONTRACT
    assert HISTORICAL_ADAPTER_CONTRACT != TARGET_METRICS_ADAPTER_CONTRACT


def test_http_v2_dispatch_peeks_schema_and_version_only() -> None:
    source = Path(
        __import__("observatory.capture_event", fromlist=["capture_event"]).__file__
        or ""
    ).read_text(encoding="utf-8")
    start = source.index("def _schema_version")
    fragment = source[start : source.index("\ndef _is_version", start)]
    assert "obj.get(\"schema\")" in fragment
    assert "obj.get(\"version\")" in fragment
    assert "adapter_contract" not in fragment
    assert HISTORICAL_ADAPTER_CONTRACT in source
    validate_attempt(_historical_attempt())


@pytest.mark.parametrize(
    "patch",
    [
        {"initial_dataset_filters": [["ai_search_volume", ">", 1]]},
        {"filters": [["ai_search_volume", ">", 1]]},
        {"order_by": ["ai_search_volume,desc"]},
        {"search_after_token": "abc"},
        {"tag": "probe"},
        {"platform": "chat_gpt"},
        {"internal_list_limit": 10},
        {"offset": 0},
        {"limit": 5},
        {"location_code": 2841},
        {"language_code": "es"},
        {"location_name": "United States"},
        {"language_name": "English"},
        {"location_code": True},
        {"location_code": 2840.0},
        {"date_from": "2025-08-02"},
        {"date_to": "2026-08-01"},
        {"date_from": "2026-07-31", "date_to": "2025-08-01"},
        {"platform": None},
        {"target": []},
        {"target": _frozen_target(keyword="observatory test")},
        {"target": _frozen_target(keyword="bmw")},
        {
            "target": _frozen_target()
            + [
                {
                    "keyword": "bmw",
                    "match_type": "word_match",
                    "search_filter": "include",
                    "search_scope": ["answer"],
                }
            ]
        },
        {"target": [{"domain": "example.com", "search_filter": "include"}]},
        {"target": _frozen_target(**{"include_subdomains": False})},
        {"target": _frozen_target(**{"match_type ": "word_match"})},
        {"target": _frozen_target(match_type="partial_match")},
        {"target": _frozen_target(search_filter="exclude")},
        {"target": _frozen_target(search_scope=["question"])},
        {"contract": TARGET_METRICS_ADAPTER_CONTRACT},
        {"contract": MENTIONS_ADAPTER_CONTRACT},
    ],
)
def test_frozen_fields_are_rejected(patch: dict[str, object]) -> None:
    with pytest.raises(DocumentError):
        validate_historical_http_parameters(_valid_parameters(**patch))


def test_missing_required_keys_are_rejected() -> None:
    for key in (
        "contract",
        "target",
        "location_code",
        "language_code",
        "platform",
        "date_from",
        "date_to",
    ):
        parameters = _valid_parameters()
        del parameters[key]
        with pytest.raises(DocumentError):
            validate_historical_http_parameters(parameters)
    target = _valid_parameters()["target"]
    assert isinstance(target, list)
    entry = target[0]
    assert isinstance(entry, dict)
    for key in ("keyword", "search_filter", "search_scope", "match_type"):
        parameters = _valid_parameters()
        missing = dict(entry)
        del missing[key]
        parameters["target"] = [missing]
        with pytest.raises(DocumentError):
            validate_historical_http_parameters(parameters)


def test_wrong_policy_fields_are_rejected() -> None:
    attempt = _historical_attempt()
    raw_policy = attempt["policy"]
    assert isinstance(raw_policy, Mapping)
    policy = dict(raw_policy)
    for key, value in (
        ("policy_version", "dataforseo-ai-optimization-target-metrics-live-paid-probe-v1"),
        ("pricing_basis", "dataforseo-llm-mentions-live-2026-08-23"),
        ("mode", "sandbox_no_spend"),
        ("max_authorized_cost_micro_usd", 20000),
    ):
        broken = dict(attempt)
        broken["policy"] = {**policy, key: value}
        with pytest.raises(DocumentError):
            validate_attempt(broken)


def test_confused_contracts_are_rejected() -> None:
    historical = closed_historical_parameters()
    with pytest.raises(DocumentError):
        validate_http_parameters(historical)
    with pytest.raises(DocumentError):
        validate_paid_http_parameters(historical)
    with pytest.raises(DocumentError):
        validate_organic_http_parameters(historical)
    with pytest.raises(DocumentError):
        validate_mentions_http_parameters(historical)
    with pytest.raises(DocumentError):
        validate_target_metrics_http_parameters(historical)
    metrics = closed_target_metrics_parameters(keyword="observatory test")
    with pytest.raises(DocumentError):
        validate_historical_http_parameters(metrics)
    attempt = _historical_attempt()
    request = dict(attempt["request"])  # type: ignore[arg-type]
    assert isinstance(request, dict)
    with pytest.raises(DocumentError):
        validate_historical_http_request(
            {**request, "path": "/v3/ai_optimization/llm_mentions/target_metrics/live"}
        )


def test_adapter_owns_8mib_and_120s_read_timeout() -> None:
    import observatory.http_single_exchange as shared

    assert MAX_RESPONSE_BODY_BYTES == EIGHT_MIB
    assert _TIMEOUT.connect == 30.0
    assert _TIMEOUT.read == 120.0
    assert _TIMEOUT.write == 30.0
    assert _TIMEOUT.pool == 30.0
    source = Path(shared.__file__).read_text(encoding="utf-8")
    assert "8_388_608" not in source
    assert "Timeout(connect=30.0, read=120.0" not in source
    assert not hasattr(shared, "MAX_RESPONSE_BODY_BYTES")


def test_subclassed_store_cannot_issue(tmp_path: Path) -> None:
    class LyingStore(EvidenceStore):
        def commit_attempt(
            self, document: Mapping[str, object], *, request_body: bytes | None
        ) -> str:
            raise AssertionError("lying store must not commit")

    with pytest.raises(TypeError, match="concrete EvidenceStore"):
        _issue_verified_attempt(
            LyingStore(tmp_path / "lie"),
            _historical_attempt(),
            HISTORICAL_REQUEST_BODY,
            authorize_max_micro_usd=AUTHORIZE,
        )


def test_authorization_required_before_attempt(tmp_path: Path) -> None:
    store = create_store(tmp_path / "auth")
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, HISTORICAL_RESPONSE_BODY)

    for value in (0, 20000, 199999, 200001, True, 200000.0, "200000"):
        with pytest.raises(StoreError, match="authorize-max-micro-usd 200000"):
            _capture_mock(store, handler, authorize=value)
    assert calls == []
    assert store.list_committed_ids("attempts") == []


def test_attempt_is_committed_before_first_handler(tmp_path: Path) -> None:
    store = create_store(tmp_path / "order")
    seen: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempt_ids = store.list_committed_ids("attempts")
        assert attempt_ids == [HISTORICAL_ATTEMPT_ID]
        document = store.read_attempt(attempt_ids[0])
        assert document is not None
        assert document["adapter_contract"] == HISTORICAL_ADAPTER_CONTRACT
        bundle = store.attempt_path(
            str(document["request_fingerprint"]),
            str(document["authorized_at"]),
            attempt_ids[0],
        )
        stored = (bundle / "request.body").read_bytes()
        assert stored == HISTORICAL_REQUEST_BODY
        assert request.content == HISTORICAL_REQUEST_BODY
        assert request.headers["authorization"] == SENTINEL_BASIC
        assert request.headers["accept"] == "application/json"
        assert request.headers["accept-encoding"] == "identity"
        assert request.headers["connection"] == "close"
        assert request.headers["content-type"] == "application/json"
        assert request.headers["user-agent"] == "observatory-dataforseo-v1"
        assert request.headers["host"] == "api.dataforseo.com"
        assert request.headers["content-length"] == str(len(HISTORICAL_REQUEST_BODY))
        assert str(request.url.path) == HISTORICAL_PATH
        seen.append(stored)
        return _streamed_response(200, HISTORICAL_RESPONSE_BODY)

    outcome = _capture_mock(store, handler)
    assert seen == [HISTORICAL_REQUEST_BODY]
    assert outcome.transport_state == "response_complete"
    assert store.read_capture_body(outcome.capture_id) == HISTORICAL_RESPONSE_BODY
    assert scrub_store(store) == []


def test_failed_attempt_commit_never_reaches_handler(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = create_store(tmp_path / "fail-commit")
    calls: list[object] = []

    def boom(*_args: object, **_kwargs: object) -> str:
        raise StoreError("attempt commit failed")

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        raise AssertionError("handler must not run")

    monkeypatch.setattr(store, "commit_attempt", boom)
    with pytest.raises(StoreError, match="attempt commit failed"):
        _capture_mock(store, handler)
    assert calls == []
    assert store.list_committed_ids("attempts") == []


def test_forged_copied_mutated_and_replayed_capability_cannot_transport(
    tmp_path: Path,
) -> None:
    with pytest.raises(TypeError, match="cannot construct"):
        _VerifiedAttempt()
    forged: Any = object.__new__(_VerifiedAttempt)
    object.__setattr__(forged, "attempt_id", "0" * 64)
    object.__setattr__(
        forged, "document", {"adapter_contract": HISTORICAL_ADAPTER_CONTRACT}
    )
    object.__setattr__(forged, "request_body", HISTORICAL_REQUEST_BODY)
    object.__setattr__(forged, "_used", False)
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(forged, _credentials())

    store = create_store(tmp_path / "cap")
    issued = _issue_verified_attempt(
        store,
        _historical_attempt(),
        HISTORICAL_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    with pytest.raises(AttributeError, match="immutable"):
        issued.request_body = b"mutated"
    with pytest.raises(AttributeError, match="immutable"):
        copy.copy(issued)
    try:
        pickled = pickle.dumps(issued)
    except Exception:
        pickled = None
    if pickled is not None:
        restored = pickle.loads(pickled)
        with pytest.raises(TypeError, match="verified committed Attempt"):
            _exchange(restored, _credentials())
    client = _mock_client(
        lambda request: _streamed_response(200, HISTORICAL_RESPONSE_BODY)
    )
    try:
        _exchange(issued, _credentials(), client=client)
        with pytest.raises(StoreError, match="one-exchange"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()


def _replacement_historical_document() -> dict[str, object]:
    return historical_http_attempt_document(
        parameters=closed_historical_parameters(),
        attempt_nonce="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        authorized_at=AUTHORIZED_AT,
        observatory_version=SOFTWARE,
    )


def test_issued_request_body_replacement_cannot_transport(tmp_path: Path) -> None:
    store = create_store(tmp_path / "issued-body")
    issued = _issue_verified_attempt(
        store,
        _historical_attempt(),
        HISTORICAL_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    assert REPLACEMENT_BODY != HISTORICAL_REQUEST_BODY
    object.__setattr__(issued, "request_body", REPLACEMENT_BODY)
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
        _historical_attempt(),
        HISTORICAL_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    replacement_document = _replacement_historical_document()
    assert replacement_document != _historical_attempt()
    validate_attempt(replacement_document)
    object.__setattr__(issued, "document", replacement_document)
    object.__setattr__(issued, "request_body", HISTORICAL_REQUEST_BODY)
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
        _historical_attempt(),
        HISTORICAL_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    calls: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.content)
        return _streamed_response(200, HISTORICAL_RESPONSE_BODY)

    client = _mock_client(handler)
    try:
        first = _exchange(issued, _credentials(), client=client)
        object.__setattr__(issued, "_used", False)
        with pytest.raises(StoreError, match="one-exchange"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert first.transport_state == "response_complete"
    assert calls == [HISTORICAL_REQUEST_BODY]


def test_pre_send_verifies_committed_attempt_and_request_body(tmp_path: Path) -> None:
    body_store = create_store(tmp_path / "pre-send-body")
    body_issued = _issue_verified_attempt(
        body_store,
        _historical_attempt(),
        HISTORICAL_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    object.__setattr__(body_issued, "request_body", REPLACEMENT_BODY)
    body_calls: list[bytes] = []

    def body_handler(request: httpx.Request) -> httpx.Response:
        body_calls.append(request.content)
        raise AssertionError("handler must not run")

    body_client = _mock_client(body_handler)
    try:
        with pytest.raises(StoreError):
            _exchange(body_issued, _credentials(), client=body_client)
    finally:
        body_client.close()
    assert body_calls == []

    evidence_store = create_store(tmp_path / "pre-send-evidence")
    evidence_issued = _issue_verified_attempt(
        evidence_store,
        _historical_attempt(),
        HISTORICAL_REQUEST_BODY,
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
    assert bundle_body.read_bytes() == HISTORICAL_REQUEST_BODY
    assert pool.read_bytes() == HISTORICAL_REQUEST_BODY
    assert pool.stat().st_ino != bundle_body.stat().st_ino
    pool.write_bytes(REPLACEMENT_BODY)
    assert bundle_body.read_bytes() == HISTORICAL_REQUEST_BODY
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
        _historical_attempt(),
        HISTORICAL_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    bundle_only = bundle_store.attempt_path(
        str(bundle_issued.document["request_fingerprint"]),
        str(bundle_issued.document["authorized_at"]),
        bundle_issued.attempt_id,
    )
    (bundle_only / "request.body").write_bytes(REPLACEMENT_BODY)
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
        _historical_attempt(),
        HISTORICAL_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    clean_calls: list[bytes] = []

    def clean_handler(request: httpx.Request) -> httpx.Response:
        clean_calls.append(request.content)
        return _streamed_response(200, HISTORICAL_RESPONSE_BODY)

    clean_client = _mock_client(clean_handler)
    try:
        outcome = _exchange(clean_issued, _credentials(), client=clean_client)
        with pytest.raises(StoreError, match="one-exchange"):
            _exchange(clean_issued, _credentials(), client=clean_client)
    finally:
        clean_client.close()
    assert outcome.transport_state == "response_complete"
    assert clean_calls == [HISTORICAL_REQUEST_BODY]


def test_cross_adapter_capabilities_are_isolated(tmp_path: Path) -> None:
    historical_store = create_store(tmp_path / "historical")
    historical_cap = _issue_verified_attempt(
        historical_store,
        _historical_attempt(),
        HISTORICAL_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    sandbox_store = create_store(tmp_path / "sbx")
    sandbox_parameters = closed_sandbox_parameters(
        keyword="observatory test", location_code=2840, language_code="en"
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
    mentions_store = create_store(tmp_path / "mentions")
    mentions_parameters = closed_mentions_parameters(keyword="observatory test")
    mentions_cap = issue_mentions(
        mentions_store,
        mentions_http_attempt_document(
            parameters=mentions_parameters,
            attempt_nonce="d" * 64,
            authorized_at="2026-08-20T20:00:00.000000Z",
            observatory_version="conformance-search-mentions-paid-probe-v1",
        ),
        mentions_request_body_bytes(mentions_parameters),
        authorize_max_micro_usd=200000,
    )
    metrics_store = create_store(tmp_path / "metrics")
    metrics_parameters = closed_target_metrics_parameters(keyword="observatory test")
    metrics_cap = issue_metrics(
        metrics_store,
        target_metrics_http_attempt_document(
            parameters=metrics_parameters,
            attempt_nonce="e" * 64,
            authorized_at="2026-08-23T20:00:00.000000Z",
            observatory_version="conformance-target-metrics-paid-probe-v1",
        ),
        target_metrics_request_body_bytes(metrics_parameters),
        authorize_max_micro_usd=200000,
    )
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(sandbox_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(paid_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(organic_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(mentions_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(metrics_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        sandbox_exchange(historical_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        paid_exchange(historical_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        organic_exchange(historical_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        mentions_exchange(historical_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        metrics_exchange(historical_cap, _credentials())


def test_one_shot_is_adapter_specific_and_allows_neighbors(tmp_path: Path) -> None:
    store = create_store(tmp_path / "neighbors")
    capture_fixture(store, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    sandbox_parameters = closed_sandbox_parameters(
        keyword="observatory test", location_code=2840, language_code="en"
    )
    store.commit_attempt(
        http_attempt_document(
            parameters=sandbox_parameters,
            attempt_nonce="a" * 64,
            authorized_at="2026-08-14T20:00:00.000000Z",
            observatory_version="conformance-http-v2",
        ),
        request_body=request_body_bytes(sandbox_parameters),
    )
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
    mentions_parameters = closed_mentions_parameters(keyword="observatory test")
    store.commit_attempt(
        mentions_http_attempt_document(
            parameters=mentions_parameters,
            attempt_nonce="d" * 64,
            authorized_at="2026-08-20T20:00:00.000000Z",
            observatory_version="conformance-search-mentions-paid-probe-v1",
        ),
        request_body=mentions_request_body_bytes(mentions_parameters),
    )
    metrics_parameters = closed_target_metrics_parameters(keyword="observatory test")
    store.commit_attempt(
        target_metrics_http_attempt_document(
            parameters=metrics_parameters,
            attempt_nonce="e" * 64,
            authorized_at="2026-08-23T20:00:00.000000Z",
            observatory_version="conformance-target-metrics-paid-probe-v1",
        ),
        request_body=target_metrics_request_body_bytes(metrics_parameters),
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, HISTORICAL_RESPONSE_BODY)

    assert scrub_store(store) == []
    first = _capture_mock(store, handler)
    assert store.read_attempt(first.attempt_id) is not None
    assert scrub_store(store) == []
    with pytest.raises(StoreError, match="historical paid-probe Attempt"):
        _capture_mock(
            store,
            handler,
            _inputs(
                attempt_nonce="f" * 64, authorized_at="2026-08-25T20:00:01.000000Z"
            ),
        )


def test_unresolved_attempt_blocks_second_invocation(tmp_path: Path) -> None:
    store = create_store(tmp_path / "unresolved")
    store.commit_attempt(
        _historical_attempt(), request_body=HISTORICAL_REQUEST_BODY
    )
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, HISTORICAL_RESPONSE_BODY)

    with pytest.raises(StoreError, match="historical paid-probe Attempt"):
        _capture_mock(
            store,
            handler,
            _inputs(
                attempt_nonce="1" * 64, authorized_at="2026-08-25T20:00:02.000000Z"
            ),
        )
    assert calls == []
    assert store.list_committed_ids("attempts") == [HISTORICAL_ATTEMPT_ID]
    assert store.list_committed_ids("captures") == []


def test_token_in_body_is_still_one_exchange(tmp_path: Path) -> None:
    store = create_store(tmp_path / "continue")
    calls: list[httpx.Request] = []
    body = (
        b'{"tasks":[{"result":[{"items":[],"items_count":0,'
        b'"search_after_token":"next"}]}]}'
    )

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, body)

    outcome = _capture_mock(store, handler)
    assert len(calls) == 1
    assert calls[0].content == HISTORICAL_REQUEST_BODY
    assert b"search_after_token" not in calls[0].content
    assert outcome.transport_state == "response_complete"
    assert store.list_committed_ids("attempts") == [outcome.attempt_id]
    assert store.list_committed_ids("captures") == [outcome.capture_id]
    assert store.read_capture_body(outcome.capture_id) == body


def test_credential_echo_leaves_unresolved_one_shot(tmp_path: Path) -> None:
    store = create_store(tmp_path / "echo")

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, SENTINEL_PASSWORD.encode())

    with pytest.raises(StoreError, match="credential material"):
        _capture_mock(store, handler)
    assert store.list_committed_ids("captures") == []
    assert store.list_committed_ids("attempts") == [HISTORICAL_ATTEMPT_ID]
    calls: list[object] = []

    def second(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, HISTORICAL_RESPONSE_BODY)

    with pytest.raises(StoreError, match="historical paid-probe Attempt"):
        _capture_mock(
            store,
            second,
            _inputs(
                attempt_nonce="2" * 64, authorized_at="2026-08-25T20:00:03.000000Z"
            ),
        )
    assert calls == []


def test_credential_echo_in_retained_header_is_refused(tmp_path: Path) -> None:
    store = create_store(tmp_path / "echo-header")

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(
            200,
            HISTORICAL_RESPONSE_BODY,
            headers=[("x-request-id", SENTINEL_LOGIN)],
        )

    with pytest.raises(StoreError, match="credential material"):
        _capture_mock(store, handler)
    assert store.list_committed_ids("captures") == []
    assert store.list_committed_ids("attempts") == [HISTORICAL_ATTEMPT_ID]


def test_default_8mib_ceiling_is_partial(tmp_path: Path) -> None:
    store = create_store(tmp_path / "eight-mib")
    payload = b"x" * (EIGHT_MIB + 1)

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, payload)

    outcome = _capture_mock(store, handler)
    assert outcome.transport_state == "response_partial"
    body = store.read_capture_body(outcome.capture_id)
    assert body is not None
    assert len(body) == EIGHT_MIB
    assert scrub_store(store) == []


def test_over_limit_partial_consumes_one_shot(tmp_path: Path) -> None:
    store = create_store(tmp_path / "limit")
    payload = b"abcdefghijklmnopq"

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, payload)

    outcome = _capture_mock(store, handler, max_response_body_bytes=SMALL_LIMIT)
    assert outcome.transport_state == "response_partial"
    assert store.read_capture_body(outcome.capture_id) == payload[:SMALL_LIMIT]
    assert scrub_store(store) == []
    calls: list[object] = []

    def second(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, HISTORICAL_RESPONSE_BODY)

    with pytest.raises(StoreError, match="historical paid-probe Attempt"):
        _capture_mock(
            store,
            second,
            _inputs(
                attempt_nonce="3" * 64, authorized_at="2026-08-25T20:00:04.000000Z"
            ),
        )
    assert calls == []


def test_complete_status_classes_and_zero_byte(tmp_path: Path) -> None:
    cases = (
        (200, "2026-08-25T20:01:00.000000Z", "a" * 64),
        (302, "2026-08-25T20:02:00.000000Z", "b" * 64),
        (404, "2026-08-25T20:03:00.000000Z", "c" * 64),
        (500, "2026-08-25T20:04:00.000000Z", "d" * 64),
    )
    for status, authorized_at, nonce in cases:
        store = create_store(tmp_path / f"status-{status}")

        def handler(
            request: httpx.Request, code: int = status
        ) -> httpx.Response:
            return _streamed_response(code, HISTORICAL_RESPONSE_BODY)

        outcome = _capture_mock(
            store,
            handler,
            _inputs(attempt_nonce=nonce, authorized_at=authorized_at),
        )
        capture = store.read_capture(outcome.capture_id)
        assert capture is not None
        assert capture["transport_state"] == "response_complete"
        response = capture["response"]
        assert isinstance(response, Mapping)
        assert response["status"] == status
        assert scrub_store(store) == []

    zero_store = create_store(tmp_path / "zero")

    def empty(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, b"")

    zero = _capture_mock(zero_store, empty)
    assert zero.transport_state == "response_complete"
    assert zero_store.read_capture_body(zero.capture_id) == b""
    assert scrub_store(zero_store) == []


def test_mid_body_timeout_and_no_response(tmp_path: Path) -> None:
    class _RaisingStream(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b'{"partial":'
            raise httpx.ReadTimeout("cut")

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
    assert scrub_store(store) == []

    fail_store = create_store(tmp_path / "noresp")

    def boom(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no")

    failed = _capture_mock(
        fail_store,
        boom,
        _inputs(attempt_nonce="4" * 64, authorized_at="2026-08-25T20:00:06.000000Z"),
    )
    capture = fail_store.read_capture(failed.capture_id)
    assert capture is not None
    assert capture["transport_state"] == "no_response"
    assert capture["response"] is None
    assert scrub_store(fail_store) == []


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
            200, HISTORICAL_RESPONSE_BODY, headers=retained + secret_headers
        )

    outcome = _capture_mock(store, handler)
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    response = capture["response"]
    assert isinstance(response, Mapping)
    assert ["content-type", "application/json"] in response["headers"]
    assert ["x-request-id", "one"] in response["headers"]
    assert ["x-request-id", "two"] in response["headers"]
    tree = _tree_bytes(store.root)
    for name in DENYLIST:
        assert f"secret-{name}".encode() not in tree
    _assert_no_secrets(tree, capture)


def test_loopback_override_is_strict(tmp_path: Path) -> None:
    store = create_store(tmp_path / "loop")
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, HISTORICAL_RESPONSE_BODY)

    client = _mock_client(handler)
    try:
        with pytest.raises(StoreError, match="loopback"):
            _run_gated_capture(
                store,
                _inputs(),
                _credentials(),
                AUTHORIZE,
                endpoint=f"https://api.dataforseo.com{HISTORICAL_PATH}",
                client=client,
            )
        with pytest.raises(StoreError, match="loopback"):
            _run_gated_capture(
                store,
                _inputs(),
                _credentials(),
                AUTHORIZE,
                endpoint=(
                    "http://127.0.0.1:9/v3/ai_optimization/llm_mentions/"
                    "target_metrics/live"
                ),
                client=client,
            )
        for bad in (
            f"http://127.0.0.1{HISTORICAL_PATH}",
            f"http://127.0.0.1:9{HISTORICAL_PATH}?q=1",
            f"http://127.0.0.1:9{HISTORICAL_PATH}#x",
            f"http://user@127.0.0.1:9{HISTORICAL_PATH}",
        ):
            with pytest.raises(StoreError, match="loopback"):
                _run_gated_capture(
                    store,
                    _inputs(),
                    _credentials(),
                    AUTHORIZE,
                    endpoint=bad,
                    client=client,
                )
        outcome = _run_gated_capture(
            store,
            _inputs(),
            _credentials(),
            AUTHORIZE,
            endpoint=f"http://127.0.0.1:9{HISTORICAL_PATH}",
            client=client,
        )
    finally:
        client.close()
    assert [str(item.url) for item in calls] == [
        f"http://127.0.0.1:9{HISTORICAL_PATH}"
    ]
    assert outcome.transport_state == "response_complete"
    attempt = store.read_attempt(outcome.attempt_id)
    assert attempt is not None
    request = attempt["request"]
    assert isinstance(request, Mapping)
    assert request["scheme"] == "https"
    assert request["host"] == "api.dataforseo.com"
    assert request["path"] == HISTORICAL_PATH


def test_loopback_server_sees_attempt_and_does_not_follow_redirect(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path / "wire")
    recorded: dict[str, object] = {}
    payload = HISTORICAL_RESPONSE_BODY
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
    port, thread = _serve_once(response, recorded, store)
    endpoint = f"http://127.0.0.1:{port}{HISTORICAL_PATH}"
    outcome = _run_gated_capture(
        store, _inputs(), _credentials(), AUTHORIZE, endpoint=endpoint
    )
    thread.join(timeout=5)
    assert recorded["attempt_ids"] == [HISTORICAL_ATTEMPT_ID]
    assert recorded["request_bodies"] == [HISTORICAL_REQUEST_BODY]
    raw = recorded["raw"]
    assert isinstance(raw, bytes)
    assert HISTORICAL_REQUEST_BODY in raw
    assert SENTINEL_BASIC.encode() in raw
    assert b"accept-encoding: identity" in raw.lower()
    assert b"connection: close" in raw.lower()
    assert store.read_capture_body(outcome.capture_id) == payload

    redir_store = create_store(tmp_path / "redir")
    redir_recorded: dict[str, object] = {}
    redir = (
        b"HTTP/1.1 302 Found\r\n"
        b"Location: https://api.dataforseo.com/elsewhere\r\n"
        b"Content-Length: 0\r\n"
        b"\r\n"
    )
    port, thread = _serve_once(redir, redir_recorded, redir_store)
    redirected = _run_gated_capture(
        redir_store,
        _inputs(attempt_nonce="5" * 64, authorized_at="2026-08-25T20:00:07.000000Z"),
        _credentials(),
        AUTHORIZE,
        endpoint=f"http://127.0.0.1:{port}{HISTORICAL_PATH}",
    )
    thread.join(timeout=5)
    capture = redir_store.read_capture(redirected.capture_id)
    assert capture is not None
    assert capture["transport_state"] == "response_complete"
    response_obj = capture["response"]
    assert isinstance(response_obj, Mapping)
    assert response_obj["status"] == 302
    assert redir_recorded.get("attempt_ids") == [redirected.attempt_id]


def test_inspect_emits_exact_bytes_without_mutation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = create_store(tmp_path / "inspect")
    attempt = _historical_attempt()
    store.commit_attempt(attempt, request_body=HISTORICAL_REQUEST_BODY)
    capture = historical_http_capture_document(
        attempt=attempt,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response=_complete_response(),
        transport_failure=None,
        response_headers_at=RESPONSE_HEADERS_AT,
        response_body_ended_at=RESPONSE_BODY_ENDED_AT,
    )
    capture_id = store.commit_capture(
        capture, response_body=HISTORICAL_RESPONSE_BODY
    )
    before = _tree_snapshot(store.root)
    body = inspect_historical_paid_probe_body(inspect_store(store.root), capture_id)
    assert body == HISTORICAL_RESPONSE_BODY
    code = main(
        ["inspect", "--evidence-root", str(store.root), "--capture-id", capture_id]
    )
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.encode() == HISTORICAL_RESPONSE_BODY or captured.out == (
        HISTORICAL_RESPONSE_BODY.decode()
    )
    assert _tree_snapshot(store.root) == before
    assert "{" not in captured.err
    assert SENTINEL_LOGIN not in captured.out


def test_inspect_rejects_wrong_adapter_partial_zero_and_tamper(tmp_path: Path) -> None:
    store = create_store(tmp_path / "inspect-bad")
    sandbox_parameters = closed_sandbox_parameters(
        keyword="observatory test", location_code=2840, language_code="en"
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
    sandbox_id = store.commit_capture(
        sandbox_capture, response_body=HISTORICAL_RESPONSE_BODY
    )
    with pytest.raises(StoreError):
        inspect_historical_paid_probe_body(inspect_store(store.root), sandbox_id)
    historical = _historical_attempt()
    store.commit_attempt(historical, request_body=HISTORICAL_REQUEST_BODY)
    prefix = b'{"partial":'
    partial = historical_http_capture_document(
        attempt=historical,
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
        inspect_historical_paid_probe_body(inspect_store(store.root), partial_id)
    nr_store = create_store(tmp_path / "inspect-nr")
    nr_attempt = _historical_attempt()
    nr_store.commit_attempt(nr_attempt, request_body=HISTORICAL_REQUEST_BODY)
    nr_id = nr_store.commit_capture(
        historical_http_capture_document(
            attempt=nr_attempt,
            request_started_at=REQUEST_STARTED_AT,
            transport_ended_at=TRANSPORT_ENDED_AT,
            transport_state="no_response",
            response=None,
            transport_failure={"phase": "connect", "code": "connection_failed"},
            response_headers_at=None,
            response_body_ended_at=None,
        ),
        response_body=None,
    )
    with pytest.raises(StoreError):
        inspect_historical_paid_probe_body(inspect_store(nr_store.root), nr_id)
    zero_store = create_store(tmp_path / "inspect-zero")
    zero_attempt = _historical_attempt()
    zero_store.commit_attempt(zero_attempt, request_body=HISTORICAL_REQUEST_BODY)
    empty = b""
    zero_id = zero_store.commit_capture(
        historical_http_capture_document(
            attempt=zero_attempt,
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
                    "state": "present_zero_bytes",
                    "body": {"bytes": 0, "sha256": content_digest(empty)},
                },
                "completeness": "complete",
            },
            transport_failure=None,
            response_headers_at=RESPONSE_HEADERS_AT,
            response_body_ended_at=RESPONSE_BODY_ENDED_AT,
        ),
        response_body=empty,
    )
    with pytest.raises(StoreError):
        inspect_historical_paid_probe_body(inspect_store(zero_store.root), zero_id)
    with pytest.raises(StoreError):
        inspect_historical_paid_probe_body(inspect_store(store.root), "ZZ")
    with pytest.raises(StoreError):
        inspect_historical_paid_probe_body(
            inspect_store(store.root), HISTORICAL_ATTEMPT_ID.upper()
        )
    complete_store = create_store(tmp_path / "inspect-complete")
    complete_attempt = _historical_attempt()
    complete_store.commit_attempt(
        complete_attempt, request_body=HISTORICAL_REQUEST_BODY
    )
    complete_id = complete_store.commit_capture(
        historical_http_capture_document(
            attempt=complete_attempt,
            request_started_at=REQUEST_STARTED_AT,
            transport_ended_at=TRANSPORT_ENDED_AT,
            transport_state="response_complete",
            response=_complete_response(),
            transport_failure=None,
            response_headers_at=RESPONSE_HEADERS_AT,
            response_body_ended_at=RESPONSE_BODY_ENDED_AT,
        ),
        response_body=HISTORICAL_RESPONSE_BODY,
    )
    with pytest.raises(StoreError):
        inspect_paid_probe_body(inspect_store(complete_store.root), complete_id)
    bundle = complete_store.capture_path(complete_id)
    (bundle / "response.body").write_bytes(b"tampered-bytes!!")
    with pytest.raises(StoreError):
        inspect_historical_paid_probe_body(
            inspect_store(complete_store.root), complete_id
        )


def test_public_cli_and_function_have_no_injection_seams(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        main(
            [
                "capture",
                "--evidence-root",
                "/tmp/x",
                "--keyword",
                FROZEN_KEYWORD,
                "--authorize-max-micro-usd",
                "200000",
            ]
        )
    with pytest.raises(SystemExit):
        main(
            [
                "capture",
                "--evidence-root",
                "/tmp/x",
                "--date-from",
                "2025-08-01",
                "--authorize-max-micro-usd",
                "200000",
            ]
        )
    with pytest.raises(SystemExit):
        main(["capture", "--evidence-root", "/tmp/x"])
    err = capsys.readouterr().err
    assert "unrecognized" in err or "required" in err
    public = capture_dataforseo_ai_optimization_llm_mentions_historical_paid_probe
    names = public.__code__.co_varnames
    assert "keyword" not in names
    assert "date_from" not in names
    assert "endpoint" not in names
    assert "max_response_body_bytes" not in names
    assert tuple(inspect.signature(closed_historical_parameters).parameters) == ()
    policy = validate_attempt(_historical_attempt())["policy"]
    assert isinstance(policy, Mapping)
    assert policy["pricing_basis"] == "dataforseo-llm-mentions-historical-live-2026-08-25"
    assert HISTORICAL_AUTHORIZED_COST_MICRO_USD == 200000


def test_fixture_and_provider_derive_skip_historical(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "mixed")
    fixture = capture_fixture(store, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    attempt = _historical_attempt()
    store.commit_attempt(attempt, request_body=HISTORICAL_REQUEST_BODY)
    capture = historical_http_capture_document(
        attempt=attempt,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response=_complete_response(),
        transport_failure=None,
        response_headers_at=RESPONSE_HEADERS_AT,
        response_body_ended_at=RESPONSE_BODY_ENDED_AT,
    )
    capture_id = store.commit_capture(
        capture, response_body=HISTORICAL_RESPONSE_BODY
    )
    assert scrub_store(store) == []
    with connect(postgres_dsn) as connection:
        fixture_summary = derive(store, connection, DEFAULT_VERSION)
        ko_summary = derive_keyword_overview(store, connection)
        organic_summary = derive_google_organic(store, connection)
        mentions_summary = derive_search_mentions(store, connection)
        metrics_summary = derive_target_metrics(store, connection)
        historical_outcomes = connection.execute(
            "SELECT count(*) FROM outcomes WHERE attempt_id = %s OR capture_id = %s",
            (content_digest(canonical_json(attempt)), capture_id),
        ).fetchone()
        fixture_attempts = connection.execute(
            "SELECT count(*) FROM outcomes WHERE attempt_id = %s",
            (fixture.attempt_id,),
        ).fetchone()
    assert fixture_summary.integrity_failures == 0
    assert ko_summary.integrity_failures == 0
    assert organic_summary.integrity_failures == 0
    assert mentions_summary.integrity_failures == 0
    assert metrics_summary.integrity_failures == 0
    assert historical_outcomes == (0,)
    assert fixture_attempts is not None and fixture_attempts[0] >= 1
