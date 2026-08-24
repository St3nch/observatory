"""AI-08: Target Metrics Live paid-probe contract, gate, and inspect."""

from __future__ import annotations

import base64
import copy
import hashlib
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
    HTTP_ADAPTER_CONTRACT,
    MENTIONS_ADAPTER_CONTRACT,
    ORGANIC_ADAPTER_CONTRACT,
    PAID_ADAPTER_CONTRACT,
    TARGET_METRICS_ADAPTER_CONTRACT,
    TARGET_METRICS_AUTHORIZED_COST_MICRO_USD,
    DocumentError,
    canonical_json,
    content_digest,
    http_attempt_document,
    http_capture_document,
    mentions_http_attempt_document,
    organic_http_attempt_document,
    paid_http_attempt_document,
    target_metrics_http_attempt_document,
    target_metrics_http_capture_document,
    target_metrics_http_fingerprint_document,
    target_metrics_http_request,
    validate_attempt,
    validate_http_parameters,
    validate_mentions_http_parameters,
    validate_organic_http_parameters,
    validate_paid_http_parameters,
    validate_target_metrics_http_parameters,
    validate_target_metrics_http_request,
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
    _TIMEOUT,
    MAX_RESPONSE_BODY_BYTES,
    TargetMetricsPaidProbeInputs,
    _exchange,
    _issue_verified_attempt,
    _run_gated_capture,
    _VerifiedAttempt,
    capture_dataforseo_ai_optimization_target_metrics_paid_probe,
    closed_target_metrics_parameters,
    inspect_target_metrics_paid_probe_body,
    main,
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

SENTINEL_LOGIN = "sentinel-login-ai08-tm11"
SENTINEL_PASSWORD = "sentinel-password-ai08-tm22"
SENTINEL_BASIC = "Basic " + base64.b64encode(
    f"{SENTINEL_LOGIN}:{SENTINEL_PASSWORD}".encode()
).decode("ascii")
AUTHORIZE = 200000
KEYWORD = "observatory test"
NONCE = "7777777777777777777777777777777777777777777777777777777777777777"
AUTHORIZED_AT = "2026-08-23T20:00:00.000000Z"
SOFTWARE = "conformance-target-metrics-paid-probe-v1"
REQUEST_STARTED_AT = "2026-08-23T20:00:00.100000Z"
RESPONSE_HEADERS_AT = "2026-08-23T20:00:00.200000Z"
RESPONSE_BODY_ENDED_AT = "2026-08-23T20:00:00.300000Z"
TRANSPORT_ENDED_AT = "2026-08-23T20:00:00.400000Z"
TARGET_METRICS_PATH = "/v3/ai_optimization/llm_mentions/target_metrics/live"

TARGET_METRICS_REQUEST_BODY = (
    b'[{"internal_list_limit":10,"language_code":"en","location_code":2840,'
    b'"platform":"google","target":[{"keyword":"observatory test",'
    b'"match_type":"word_match","search_filter":"include",'
    b'"search_scope":["answer"]}]}]'
)
TARGET_METRICS_REQUEST_BODY_SHA256 = (
    "4414f03561a728f03a6b0e859bcb210f8876968c5e2b7c2e2cc5eeb1d209e170"
)
TARGET_METRICS_FINGERPRINT = (
    "1404ce81eb7884e21a5571a30db02e1c0555fdcf6db5e805391255cf6e604bbd"
)
TARGET_METRICS_ATTEMPT_ID = (
    "1d2716ea2a6888c3c7b7aeb0d0ec4f9b5b3f84d4e8780f1ae270d306f89c907d"
)
TARGET_METRICS_RESPONSE_BODY = b'{"ok":true}'
TARGET_METRICS_RESPONSE_BODY_SHA256 = (
    "4062edaf750fb8074e7e83e0c9028c94e32468a8b6f1614774328ef045150f93"
)
TARGET_METRICS_CAPTURE_ID = (
    "36ba18e80cce117709c56fab7e7b1df8256defd87390d43a7550c1faa8681e84"
)
HTTP_ATTEMPT_ID = "22adc4841c86b7cd98b90bba683aeac204a0cb568428b590fd399e8627eb4640"
PAID_ATTEMPT_ID = "89904bf8a6812fb3d0d845310e4705962bb4db928b80da3be67342dff5def185"
ORGANIC_ATTEMPT_ID = "b577bc1fb75f4ba7576a96c1328fbe74df9d975f3bd03f6c01d7441dfed1a1be"
MENTIONS_ATTEMPT_ID = "5cf959940bec672f8f67bf1f7b5ad18aee2b86fd89e33dd00280f4092cf2741e"
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


def _inputs(**overrides: str) -> TargetMetricsPaidProbeInputs:
    return TargetMetricsPaidProbeInputs(
        keyword=overrides.get("keyword", KEYWORD),
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
    inputs: TargetMetricsPaidProbeInputs | None = None,
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
            "body": {"bytes": 11, "sha256": TARGET_METRICS_RESPONSE_BODY_SHA256},
        },
        "completeness": "complete",
    }


def _target_metrics_attempt() -> dict[str, object]:
    return target_metrics_http_attempt_document(
        parameters=closed_target_metrics_parameters(keyword=KEYWORD),
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


def test_independent_literal_vectors() -> None:
    assert hashlib.sha256(TARGET_METRICS_REQUEST_BODY).hexdigest() == (
        TARGET_METRICS_REQUEST_BODY_SHA256
    )
    assert hashlib.sha256(TARGET_METRICS_RESPONSE_BODY).hexdigest() == (
        TARGET_METRICS_RESPONSE_BODY_SHA256
    )
    assert len(TARGET_METRICS_REQUEST_BODY) == 210


def test_closed_request_vector_and_attempt_identity() -> None:
    parameters = closed_target_metrics_parameters(keyword=KEYWORD)
    body = target_metrics_request_body_bytes(parameters)
    assert body == TARGET_METRICS_REQUEST_BODY
    assert content_digest(body) == TARGET_METRICS_REQUEST_BODY_SHA256
    attempt = _target_metrics_attempt()
    request = attempt["request"]
    assert isinstance(request, Mapping)
    fingerprint = target_metrics_http_fingerprint_document(request=request)
    assert content_digest(canonical_json(fingerprint)) == TARGET_METRICS_FINGERPRINT
    assert content_digest(canonical_json(attempt)) == TARGET_METRICS_ATTEMPT_ID
    capture = target_metrics_http_capture_document(
        attempt=attempt,
        request_started_at=REQUEST_STARTED_AT,
        transport_ended_at=TRANSPORT_ENDED_AT,
        transport_state="response_complete",
        response=_complete_response(),
        transport_failure=None,
        response_headers_at=RESPONSE_HEADERS_AT,
        response_body_ended_at=RESPONSE_BODY_ENDED_AT,
    )
    assert content_digest(canonical_json(capture)) == TARGET_METRICS_CAPTURE_ID
    assert parameters["platform"] == "google"
    assert parameters["internal_list_limit"] == 10
    assert parameters["location_code"] == 2840
    assert parameters["language_code"] == "en"
    assert "offset" not in parameters
    assert "limit" not in parameters
    target = parameters["target"]
    assert isinstance(target, list) and len(target) == 1
    entry = target[0]
    assert isinstance(entry, Mapping)
    assert entry["match_type"] == "word_match"
    assert entry["search_filter"] == "include"
    assert entry["search_scope"] == ["answer"]
    task = json.loads(body)
    assert isinstance(task, list) and len(task) == 1
    assert "contract" not in task[0]
    assert "match_type " not in json.dumps(task[0])
    assert task[0]["internal_list_limit"] == 10


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
    assert TARGET_METRICS_ADAPTER_CONTRACT != HTTP_ADAPTER_CONTRACT
    assert TARGET_METRICS_ADAPTER_CONTRACT != PAID_ADAPTER_CONTRACT
    assert TARGET_METRICS_ADAPTER_CONTRACT != ORGANIC_ADAPTER_CONTRACT
    assert TARGET_METRICS_ADAPTER_CONTRACT != MENTIONS_ADAPTER_CONTRACT


def test_live_call_candidate_keyword_is_accepted() -> None:
    parameters = closed_target_metrics_parameters(
        keyword="generative engine optimization"
    )
    target = parameters["target"]
    assert isinstance(target, list)
    entry = target[0]
    assert isinstance(entry, Mapping)
    assert entry["keyword"] == "generative engine optimization"


def test_operator_keywords_are_not_denied() -> None:
    parameters = closed_target_metrics_parameters(keyword="site:example.com")
    target = parameters["target"]
    assert isinstance(target, list)
    entry = target[0]
    assert isinstance(entry, Mapping)
    assert entry["keyword"] == "site:example.com"
    with pytest.raises(DocumentError):
        closed_organic_parameters(keyword="site:example.com")


@pytest.mark.parametrize(
    "keyword",
    [
        "",
        " observatory",
        "observatory ",
        "a" * 81,
        "one two three four five six seven eight nine ten eleven",
        "emoji \u2603",
    ],
)
def test_keyword_grammar_rejects_invalid_forms(keyword: str) -> None:
    with pytest.raises(DocumentError):
        closed_target_metrics_parameters(keyword=keyword)


def _valid_parameters(**overrides: object) -> dict[str, object]:
    parameters: dict[str, object] = {
        "contract": TARGET_METRICS_ADAPTER_CONTRACT,
        "internal_list_limit": 10,
        "language_code": "en",
        "location_code": 2840,
        "platform": "google",
        "target": [
            {
                "keyword": KEYWORD,
                "match_type": "word_match",
                "search_filter": "include",
                "search_scope": ["answer"],
            }
        ],
    }
    parameters.update(overrides)
    return parameters


@pytest.mark.parametrize(
    "patch",
    [
        {"initial_dataset_filters": [["ai_search_volume", ">", 1]]},
        {"filters": [["ai_search_volume", ">", 1]]},
        {"order_by": ["ai_search_volume,desc"]},
        {"search_after_token": "abc"},
        {"tag": "probe"},
        {"platform": "chat_gpt"},
        {"internal_list_limit": 1},
        {"internal_list_limit": 11},
        {"internal_list_limit": 20},
        {"internal_list_limit": True},
        {"offset": 0},
        {"limit": 5},
        {"location_code": 2841},
        {"language_code": "es"},
        {"location_name": "United States"},
        {"language_name": "English"},
        {"location_code": True},
        {"target": []},
        {
            "target": [
                {
                    "keyword": KEYWORD,
                    "match_type": "word_match",
                    "search_filter": "include",
                    "search_scope": ["answer"],
                },
                {
                    "keyword": "bmw",
                    "match_type": "word_match",
                    "search_filter": "include",
                    "search_scope": ["answer"],
                },
            ]
        },
        {
            "target": [
                {
                    "domain": "example.com",
                    "search_filter": "include",
                }
            ]
        },
        {
            "target": [
                {
                    "keyword": KEYWORD,
                    "include_subdomains": False,
                    "match_type": "word_match",
                    "search_filter": "include",
                    "search_scope": ["answer"],
                }
            ]
        },
        {
            "target": [
                {
                    "keyword": KEYWORD,
                    "match_type ": "word_match",
                    "search_filter": "include",
                    "search_scope": ["answer"],
                }
            ]
        },
        {
            "target": [
                {
                    "keyword": KEYWORD,
                    "match_type": "partial_match",
                    "search_filter": "include",
                    "search_scope": ["answer"],
                }
            ]
        },
        {
            "target": [
                {
                    "keyword": KEYWORD,
                    "match_type": "word_match",
                    "search_filter": "exclude",
                    "search_scope": ["answer"],
                }
            ]
        },
        {
            "target": [
                {
                    "keyword": KEYWORD,
                    "match_type": "word_match",
                    "search_filter": "include",
                    "search_scope": ["question"],
                }
            ]
        },
        {"contract": MENTIONS_ADAPTER_CONTRACT},
        {"contract": ORGANIC_ADAPTER_CONTRACT},
    ],
)
def test_frozen_fields_are_rejected(patch: dict[str, object]) -> None:
    with pytest.raises(DocumentError):
        validate_target_metrics_http_parameters(_valid_parameters(**patch))


def test_missing_required_keys_are_rejected() -> None:
    for key in (
        "contract",
        "target",
        "location_code",
        "language_code",
        "platform",
        "internal_list_limit",
    ):
        parameters = _valid_parameters()
        del parameters[key]
        with pytest.raises(DocumentError):
            validate_target_metrics_http_parameters(parameters)
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
            validate_target_metrics_http_parameters(parameters)


def test_wrong_policy_fields_are_rejected() -> None:
    attempt = _target_metrics_attempt()
    raw_policy = attempt["policy"]
    assert isinstance(raw_policy, Mapping)
    policy = dict(raw_policy)
    for key, value in (
        ("policy_version", "dataforseo-ai-optimization-search-mentions-live-paid-probe-v1"),
        ("pricing_basis", "dataforseo-llm-mentions-live-2026-08-20"),
        ("mode", "sandbox_no_spend"),
        ("max_authorized_cost_micro_usd", 20000),
    ):
        broken = dict(attempt)
        broken["policy"] = {**policy, key: value}
        with pytest.raises(DocumentError):
            validate_attempt(broken)


def test_confused_contracts_are_rejected() -> None:
    metrics = closed_target_metrics_parameters(keyword=KEYWORD)
    with pytest.raises(DocumentError):
        validate_http_parameters(metrics)
    with pytest.raises(DocumentError):
        validate_paid_http_parameters(metrics)
    with pytest.raises(DocumentError):
        validate_organic_http_parameters(metrics)
    with pytest.raises(DocumentError):
        validate_mentions_http_parameters(metrics)
    paid = closed_paid_parameters(keywords=("seo api",))
    with pytest.raises(DocumentError):
        validate_target_metrics_http_parameters(paid)
    mentions = closed_mentions_parameters(keyword=KEYWORD)
    with pytest.raises(DocumentError):
        validate_target_metrics_http_parameters(mentions)
    request = target_metrics_http_request(body=TARGET_METRICS_REQUEST_BODY)
    with pytest.raises(DocumentError):
        validate_target_metrics_http_request(
            {**request, "host": "sandbox.dataforseo.com"}
        )
    with pytest.raises(DocumentError):
        validate_target_metrics_http_request(
            {**request, "path": "/v3/ai_optimization/llm_mentions/search_mentions/live"}
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
            _target_metrics_attempt(),
            TARGET_METRICS_REQUEST_BODY,
            authorize_max_micro_usd=AUTHORIZE,
        )


def test_authorization_required_before_attempt(tmp_path: Path) -> None:
    store = create_store(tmp_path / "auth")
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, TARGET_METRICS_RESPONSE_BODY)

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
        assert attempt_ids == [TARGET_METRICS_ATTEMPT_ID]
        document = store.read_attempt(attempt_ids[0])
        assert document is not None
        assert document["adapter_contract"] == TARGET_METRICS_ADAPTER_CONTRACT
        bundle = store.attempt_path(
            str(document["request_fingerprint"]),
            str(document["authorized_at"]),
            attempt_ids[0],
        )
        stored = (bundle / "request.body").read_bytes()
        assert stored == TARGET_METRICS_REQUEST_BODY
        assert request.content == TARGET_METRICS_REQUEST_BODY
        assert request.headers["authorization"] == SENTINEL_BASIC
        assert request.headers["accept"] == "application/json"
        assert request.headers["accept-encoding"] == "identity"
        assert request.headers["connection"] == "close"
        assert request.headers["content-type"] == "application/json"
        assert request.headers["user-agent"] == "observatory-dataforseo-v1"
        assert request.headers["host"] == "api.dataforseo.com"
        assert request.headers["content-length"] == str(len(TARGET_METRICS_REQUEST_BODY))
        seen.append(stored)
        return _streamed_response(200, TARGET_METRICS_RESPONSE_BODY)

    outcome = _capture_mock(store, handler)
    assert seen == [TARGET_METRICS_REQUEST_BODY]
    assert outcome.transport_state == "response_complete"
    assert store.read_capture_body(outcome.capture_id) == TARGET_METRICS_RESPONSE_BODY
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
    object.__setattr__(
        forged, "attempt_id", "0" * 64
    )
    object.__setattr__(
        forged, "document", {"adapter_contract": TARGET_METRICS_ADAPTER_CONTRACT}
    )
    object.__setattr__(forged, "request_body", TARGET_METRICS_REQUEST_BODY)
    object.__setattr__(forged, "_used", False)
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(forged, _credentials())

    store = create_store(tmp_path / "cap")
    issued = _issue_verified_attempt(
        store,
        _target_metrics_attempt(),
        TARGET_METRICS_REQUEST_BODY,
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
        lambda request: _streamed_response(200, TARGET_METRICS_RESPONSE_BODY)
    )
    try:
        _exchange(issued, _credentials(), client=client)
        with pytest.raises(StoreError, match="one-exchange"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()


def _replacement_target_metrics_body() -> bytes:
    return target_metrics_request_body_bytes(
        closed_target_metrics_parameters(keyword="forged keyword")
    )


def _replacement_target_metrics_document() -> dict[str, object]:
    return target_metrics_http_attempt_document(
        parameters=closed_target_metrics_parameters(keyword="forged keyword"),
        attempt_nonce=NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=SOFTWARE,
    )


def test_issued_request_body_replacement_cannot_transport(tmp_path: Path) -> None:
    store = create_store(tmp_path / "issued-body")
    issued = _issue_verified_attempt(
        store,
        _target_metrics_attempt(),
        TARGET_METRICS_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    replacement = _replacement_target_metrics_body()
    assert replacement != TARGET_METRICS_REQUEST_BODY
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
        _target_metrics_attempt(),
        TARGET_METRICS_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    replacement_document = _replacement_target_metrics_document()
    replacement_body = _replacement_target_metrics_body()
    assert replacement_document != _target_metrics_attempt()
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
        _target_metrics_attempt(),
        TARGET_METRICS_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    calls: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.content)
        return _streamed_response(200, TARGET_METRICS_RESPONSE_BODY)

    client = _mock_client(handler)
    try:
        first = _exchange(issued, _credentials(), client=client)
        object.__setattr__(issued, "_used", False)
        with pytest.raises(StoreError, match="one-exchange"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert first.transport_state == "response_complete"
    assert calls == [TARGET_METRICS_REQUEST_BODY]


def test_pre_send_verifies_committed_attempt_and_request_body(tmp_path: Path) -> None:
    replacement = _replacement_target_metrics_body()
    body_store = create_store(tmp_path / "pre-send-body")
    body_issued = _issue_verified_attempt(
        body_store,
        _target_metrics_attempt(),
        TARGET_METRICS_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    object.__setattr__(body_issued, "request_body", replacement)
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
        _target_metrics_attempt(),
        TARGET_METRICS_REQUEST_BODY,
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
    assert bundle_body.read_bytes() == TARGET_METRICS_REQUEST_BODY
    assert pool.read_bytes() == TARGET_METRICS_REQUEST_BODY
    assert pool.stat().st_ino != bundle_body.stat().st_ino
    pool.write_bytes(replacement)
    assert bundle_body.read_bytes() == TARGET_METRICS_REQUEST_BODY
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
        _target_metrics_attempt(),
        TARGET_METRICS_REQUEST_BODY,
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
        _target_metrics_attempt(),
        TARGET_METRICS_REQUEST_BODY,
        authorize_max_micro_usd=AUTHORIZE,
    )
    clean_calls: list[bytes] = []

    def clean_handler(request: httpx.Request) -> httpx.Response:
        clean_calls.append(request.content)
        return _streamed_response(200, TARGET_METRICS_RESPONSE_BODY)

    clean_client = _mock_client(clean_handler)
    try:
        outcome = _exchange(clean_issued, _credentials(), client=clean_client)
        with pytest.raises(StoreError, match="one-exchange"):
            _exchange(clean_issued, _credentials(), client=clean_client)
    finally:
        clean_client.close()
    assert outcome.transport_state == "response_complete"
    assert clean_calls == [TARGET_METRICS_REQUEST_BODY]


def test_cross_adapter_capabilities_are_isolated(tmp_path: Path) -> None:
    metrics_store = create_store(tmp_path / "metrics")
    metrics_cap = _issue_verified_attempt(
        metrics_store,
        _target_metrics_attempt(),
        TARGET_METRICS_REQUEST_BODY,
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
    organic_store = create_store(tmp_path / "org")
    organic_parameters = closed_organic_parameters(keyword=KEYWORD)
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
    mentions_parameters = closed_mentions_parameters(keyword=KEYWORD)
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
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(sandbox_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(paid_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(organic_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(mentions_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        sandbox_exchange(metrics_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        paid_exchange(metrics_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        organic_exchange(metrics_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        mentions_exchange(metrics_cap, _credentials())


def test_one_shot_is_adapter_specific_and_allows_neighbors(tmp_path: Path) -> None:
    store = create_store(tmp_path / "neighbors")
    capture_fixture(store, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    sandbox_parameters = closed_sandbox_parameters(
        keyword=KEYWORD, location_code=2840, language_code="en"
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
    organic_parameters = closed_organic_parameters(keyword=KEYWORD)
    store.commit_attempt(
        organic_http_attempt_document(
            parameters=organic_parameters,
            attempt_nonce="c" * 64,
            authorized_at="2026-08-18T20:00:00.000000Z",
            observatory_version="conformance-google-organic-paid-probe-v1",
        ),
        request_body=organic_request_body_bytes(organic_parameters),
    )
    mentions_parameters = closed_mentions_parameters(keyword=KEYWORD)
    store.commit_attempt(
        mentions_http_attempt_document(
            parameters=mentions_parameters,
            attempt_nonce="d" * 64,
            authorized_at="2026-08-20T20:00:00.000000Z",
            observatory_version="conformance-search-mentions-paid-probe-v1",
        ),
        request_body=mentions_request_body_bytes(mentions_parameters),
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, TARGET_METRICS_RESPONSE_BODY)

    assert scrub_store(store) == []
    first = _capture_mock(store, handler)
    assert store.read_attempt(first.attempt_id) is not None
    assert scrub_store(store) == []
    with pytest.raises(StoreError, match="target-metrics paid-probe Attempt"):
        _capture_mock(
            store,
            handler,
            _inputs(
                attempt_nonce="e" * 64, authorized_at="2026-08-23T20:00:01.000000Z"
            ),
        )


def test_unresolved_attempt_blocks_second_invocation(tmp_path: Path) -> None:
    store = create_store(tmp_path / "unresolved")
    store.commit_attempt(
        _target_metrics_attempt(), request_body=TARGET_METRICS_REQUEST_BODY
    )
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, TARGET_METRICS_RESPONSE_BODY)

    with pytest.raises(StoreError, match="target-metrics paid-probe Attempt"):
        _capture_mock(
            store,
            handler,
            _inputs(
                attempt_nonce="f" * 64, authorized_at="2026-08-23T20:00:02.000000Z"
            ),
        )
    assert calls == []
    assert store.list_committed_ids("attempts") == [TARGET_METRICS_ATTEMPT_ID]
    assert store.list_committed_ids("captures") == []


def test_token_in_body_is_still_one_exchange(tmp_path: Path) -> None:
    store = create_store(tmp_path / "continue")
    calls: list[httpx.Request] = []
    body = (
        b'{"tasks":[{"result":[{"aggregated_metrics":{"total":{"mentions":1}},'
        b'"items":[],"items_count":0,"search_after_token":"next","total_count":0}]}]}'
    )

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, body)

    outcome = _capture_mock(store, handler)
    assert len(calls) == 1
    assert calls[0].content == TARGET_METRICS_REQUEST_BODY
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
    assert store.list_committed_ids("attempts") == [TARGET_METRICS_ATTEMPT_ID]
    calls: list[object] = []

    def second(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, TARGET_METRICS_RESPONSE_BODY)

    with pytest.raises(StoreError, match="target-metrics paid-probe Attempt"):
        _capture_mock(
            store,
            second,
            _inputs(
                attempt_nonce="1" * 64, authorized_at="2026-08-23T20:00:03.000000Z"
            ),
        )
    assert calls == []


def test_credential_echo_in_retained_header_is_refused(tmp_path: Path) -> None:
    store = create_store(tmp_path / "echo-header")

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(
            200,
            TARGET_METRICS_RESPONSE_BODY,
            headers=[("x-request-id", SENTINEL_LOGIN)],
        )

    with pytest.raises(StoreError, match="credential material"):
        _capture_mock(store, handler)
    assert store.list_committed_ids("captures") == []
    assert store.list_committed_ids("attempts") == [TARGET_METRICS_ATTEMPT_ID]


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
        return _streamed_response(200, TARGET_METRICS_RESPONSE_BODY)

    with pytest.raises(StoreError, match="target-metrics paid-probe Attempt"):
        _capture_mock(
            store,
            second,
            _inputs(
                attempt_nonce="2" * 64, authorized_at="2026-08-23T20:00:04.000000Z"
            ),
        )
    assert calls == []


def test_complete_status_classes_and_zero_byte(tmp_path: Path) -> None:
    cases = (
        (200, "2026-08-23T20:01:00.000000Z", "a" * 64),
        (302, "2026-08-23T20:02:00.000000Z", "b" * 64),
        (404, "2026-08-23T20:03:00.000000Z", "c" * 64),
        (500, "2026-08-23T20:04:00.000000Z", "d" * 64),
    )
    for status, authorized_at, nonce in cases:
        store = create_store(tmp_path / f"status-{status}")

        def handler(
            request: httpx.Request, code: int = status
        ) -> httpx.Response:
            return _streamed_response(code, TARGET_METRICS_RESPONSE_BODY)

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
        _inputs(attempt_nonce="3" * 64, authorized_at="2026-08-23T20:00:06.000000Z"),
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
            200, TARGET_METRICS_RESPONSE_BODY, headers=retained + secret_headers
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
        return _streamed_response(200, TARGET_METRICS_RESPONSE_BODY)

    client = _mock_client(handler)
    try:
        with pytest.raises(StoreError, match="loopback"):
            _run_gated_capture(
                store,
                _inputs(),
                _credentials(),
                AUTHORIZE,
                endpoint=f"https://api.dataforseo.com{TARGET_METRICS_PATH}",
                client=client,
            )
        with pytest.raises(StoreError, match="loopback"):
            _run_gated_capture(
                store,
                _inputs(),
                _credentials(),
                AUTHORIZE,
                endpoint="http://127.0.0.1:9/v3/ai_optimization/llm_mentions/search_mentions/live",
                client=client,
            )
        for bad in (
            f"http://127.0.0.1{TARGET_METRICS_PATH}",
            f"http://127.0.0.1:9{TARGET_METRICS_PATH}?q=1",
            f"http://127.0.0.1:9{TARGET_METRICS_PATH}#x",
            f"http://user@127.0.0.1:9{TARGET_METRICS_PATH}",
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
            endpoint=f"http://127.0.0.1:9{TARGET_METRICS_PATH}",
            client=client,
        )
    finally:
        client.close()
    assert [str(item.url) for item in calls] == [
        f"http://127.0.0.1:9{TARGET_METRICS_PATH}"
    ]
    assert outcome.transport_state == "response_complete"
    attempt = store.read_attempt(outcome.attempt_id)
    assert attempt is not None
    request = attempt["request"]
    assert isinstance(request, Mapping)
    assert request["scheme"] == "https"
    assert request["host"] == "api.dataforseo.com"
    assert request["path"] == TARGET_METRICS_PATH


def test_loopback_server_sees_attempt_and_does_not_follow_redirect(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path / "wire")
    recorded: dict[str, object] = {}
    payload = TARGET_METRICS_RESPONSE_BODY
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
    endpoint = f"http://127.0.0.1:{port}{TARGET_METRICS_PATH}"
    outcome = _run_gated_capture(
        store, _inputs(), _credentials(), AUTHORIZE, endpoint=endpoint
    )
    thread.join(timeout=5)
    assert recorded["attempt_ids"] == [TARGET_METRICS_ATTEMPT_ID]
    assert recorded["request_bodies"] == [TARGET_METRICS_REQUEST_BODY]
    raw = recorded["raw"]
    assert isinstance(raw, bytes)
    assert TARGET_METRICS_REQUEST_BODY in raw
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
        _inputs(attempt_nonce="4" * 64, authorized_at="2026-08-23T20:00:07.000000Z"),
        _credentials(),
        AUTHORIZE,
        endpoint=f"http://127.0.0.1:{port}{TARGET_METRICS_PATH}",
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
    attempt = _target_metrics_attempt()
    store.commit_attempt(attempt, request_body=TARGET_METRICS_REQUEST_BODY)
    capture = target_metrics_http_capture_document(
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
        capture, response_body=TARGET_METRICS_RESPONSE_BODY
    )
    before = _tree_snapshot(store.root)
    body = inspect_target_metrics_paid_probe_body(inspect_store(store.root), capture_id)
    assert body == TARGET_METRICS_RESPONSE_BODY
    code = main(
        ["inspect", "--evidence-root", str(store.root), "--capture-id", capture_id]
    )
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.encode() == TARGET_METRICS_RESPONSE_BODY or captured.out == (
        TARGET_METRICS_RESPONSE_BODY.decode()
    )
    assert _tree_snapshot(store.root) == before
    assert "{" not in captured.err
    assert SENTINEL_LOGIN not in captured.out


def test_inspect_rejects_wrong_adapter_partial_zero_and_tamper(tmp_path: Path) -> None:
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
    sandbox_id = store.commit_capture(
        sandbox_capture, response_body=TARGET_METRICS_RESPONSE_BODY
    )
    with pytest.raises(StoreError):
        inspect_target_metrics_paid_probe_body(inspect_store(store.root), sandbox_id)
    metrics = _target_metrics_attempt()
    store.commit_attempt(metrics, request_body=TARGET_METRICS_REQUEST_BODY)
    prefix = b'{"partial":'
    partial = target_metrics_http_capture_document(
        attempt=metrics,
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
        inspect_target_metrics_paid_probe_body(inspect_store(store.root), partial_id)
    nr_store = create_store(tmp_path / "inspect-nr")
    nr_attempt = _target_metrics_attempt()
    nr_store.commit_attempt(nr_attempt, request_body=TARGET_METRICS_REQUEST_BODY)
    nr_id = nr_store.commit_capture(
        target_metrics_http_capture_document(
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
        inspect_target_metrics_paid_probe_body(inspect_store(nr_store.root), nr_id)
    zero_store = create_store(tmp_path / "inspect-zero")
    zero_attempt = _target_metrics_attempt()
    zero_store.commit_attempt(zero_attempt, request_body=TARGET_METRICS_REQUEST_BODY)
    empty = b""
    zero_id = zero_store.commit_capture(
        target_metrics_http_capture_document(
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
        inspect_target_metrics_paid_probe_body(inspect_store(zero_store.root), zero_id)
    with pytest.raises(StoreError):
        inspect_target_metrics_paid_probe_body(inspect_store(store.root), "ZZ")
    with pytest.raises(StoreError):
        inspect_target_metrics_paid_probe_body(
            inspect_store(store.root), TARGET_METRICS_ATTEMPT_ID.upper()
        )
    complete_store = create_store(tmp_path / "inspect-complete")
    complete_attempt = _target_metrics_attempt()
    complete_store.commit_attempt(
        complete_attempt, request_body=TARGET_METRICS_REQUEST_BODY
    )
    complete_id = complete_store.commit_capture(
        target_metrics_http_capture_document(
            attempt=complete_attempt,
            request_started_at=REQUEST_STARTED_AT,
            transport_ended_at=TRANSPORT_ENDED_AT,
            transport_state="response_complete",
            response=_complete_response(),
            transport_failure=None,
            response_headers_at=RESPONSE_HEADERS_AT,
            response_body_ended_at=RESPONSE_BODY_ENDED_AT,
        ),
        response_body=TARGET_METRICS_RESPONSE_BODY,
    )
    with pytest.raises(StoreError):
        inspect_paid_probe_body(inspect_store(complete_store.root), complete_id)
    bundle = complete_store.capture_path(complete_id)
    (bundle / "response.body").write_bytes(b"tampered-bytes!!")
    with pytest.raises(StoreError):
        inspect_target_metrics_paid_probe_body(
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
                KEYWORD,
                "--authorize-max-micro-usd",
                "200000",
                "--timeout",
                "5",
            ]
        )
    with pytest.raises(SystemExit):
        main(["capture", "--evidence-root", "/tmp/x", "--keyword", KEYWORD])
    err = capsys.readouterr().err
    assert "timeout" in err or "unrecognized" in err or "required" in err
    assert (
        "endpoint"
        not in capture_dataforseo_ai_optimization_target_metrics_paid_probe.__code__.co_varnames
    )
    assert (
        "max_response_body_bytes"
        not in capture_dataforseo_ai_optimization_target_metrics_paid_probe.__code__.co_varnames
    )
    policy = validate_attempt(_target_metrics_attempt())["policy"]
    assert isinstance(policy, Mapping)
    assert policy["pricing_basis"] == "dataforseo-llm-mentions-live-2026-08-23"
    assert TARGET_METRICS_AUTHORIZED_COST_MICRO_USD == 200000


def test_fixture_and_provider_derive_skip_target_metrics(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "mixed")
    fixture = capture_fixture(store, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    attempt = _target_metrics_attempt()
    store.commit_attempt(attempt, request_body=TARGET_METRICS_REQUEST_BODY)
    capture = target_metrics_http_capture_document(
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
        capture, response_body=TARGET_METRICS_RESPONSE_BODY
    )
    assert scrub_store(store) == []
    with connect(postgres_dsn) as connection:
        fixture_summary = derive(store, connection, DEFAULT_VERSION)
        ko_summary = derive_keyword_overview(store, connection)
        organic_summary = derive_google_organic(store, connection)
        mentions_summary = derive_search_mentions(store, connection)
        metrics_outcomes = connection.execute(
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
    assert metrics_outcomes == (0,)
    assert fixture_attempts is not None and fixture_attempts[0] >= 1
