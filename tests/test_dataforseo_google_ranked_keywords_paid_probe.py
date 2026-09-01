"""RANK-02: Ranked Keywords Live paid-probe contract, hardened gate, and inspect.

Every test is credential-free and zero-network: sentinel credentials, mock or loopback
transport, and temporary Evidence Stores only. No DataForSEO request is ever made.

RANK-02 preserves bytes. Nothing here asserts Ranked Keywords response semantics; provider
counts, rank/movement/loss fields, keyword metrics, and cost arithmetic stay unasserted
until real Evidence exists.
"""

from __future__ import annotations

import base64
import gc
import json
import socket
from collections.abc import Iterator, Mapping
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
import pytest

from observatory.capture import PUBLISHED_AR_INPUTS, capture_fixture
from observatory.capture_event import (
    HTTP_ADAPTER_CONTRACT,
    ORGANIC_ADAPTER_CONTRACT,
    PAID_ADAPTER_CONTRACT,
    RANKED_KEYWORDS_ADAPTER_CONTRACT,
    RANKED_KEYWORDS_AUTHORIZED_COST_MICRO_USD,
    RANKED_KEYWORDS_HOST,
    RANKED_KEYWORDS_PATH,
    RELATED_KEYWORDS_ADAPTER_CONTRACT,
    DocumentError,
    canonical_json,
    content_digest,
    organic_http_attempt_document,
    paid_http_attempt_document,
    ranked_keywords_http_attempt_document,
    ranked_keywords_http_capture_document,
    ranked_keywords_http_fingerprint_document,
    ranked_keywords_http_request,
    related_keywords_http_attempt_document,
    related_keywords_http_capture_document,
    validate_attempt,
    validate_ranked_keywords_http_parameters,
    validate_ranked_keywords_http_request,
    validate_related_keywords_http_parameters,
)
from observatory.dataforseo_google_organic_paid_probe import (
    closed_organic_parameters,
    organic_request_body_bytes,
)
from observatory.dataforseo_google_ranked_keywords_paid_probe import (
    _TIMEOUT,
    MAX_RESPONSE_BODY_BYTES,
    PRODUCTION_URL,
    RankedKeywordsPaidProbeInputs,
    _commit_ranked_keywords_capture,
    _committed_attempt,
    _exchange,
    _issue_verified_attempt,
    _run_gated_capture,
    _VerifiedAttempt,
    capture_dataforseo_google_ranked_keywords_paid_probe,
    closed_ranked_keywords_parameters,
    inspect_ranked_keywords_paid_probe_body,
    main,
    ranked_keywords_request_body_bytes,
)
from observatory.dataforseo_google_related_keywords_paid_probe import (
    _exchange as related_exchange,
)
from observatory.dataforseo_google_related_keywords_paid_probe import (
    _issue_verified_attempt as issue_related,
)
from observatory.dataforseo_google_related_keywords_paid_probe import (
    closed_related_keywords_parameters,
    related_keywords_request_body_bytes,
)
from observatory.dataforseo_paid_probe import (
    closed_paid_parameters,
    paid_request_body_bytes,
)
from observatory.derive import DEFAULT_VERSION, derive
from observatory.evidence import scrub_store
from observatory.evidence_store import EvidenceStore, StoreError, create_store, inspect_store
from observatory.google_organic_derive import derive_google_organic
from observatory.google_related_keywords_derive import derive_google_related_keywords
from observatory.http_single_exchange import production_http_client
from observatory.keyword_overview_derive import derive_keyword_overview
from observatory.migrate import connect
from observatory.settings import (
    DATAFORSEO_LOGIN_ENV,
    DATAFORSEO_PASSWORD_ENV,
    CredentialError,
    DataForSEOCredentials,
)

SENTINEL_LOGIN = "sentinel-login-rank02-pp33"
SENTINEL_PASSWORD = "sentinel-password-rank02-qq44"
SENTINEL_BASIC = "Basic " + base64.b64encode(
    f"{SENTINEL_LOGIN}:{SENTINEL_PASSWORD}".encode()
).decode("ascii")
AUTHORIZE = 50000
TARGET = "theconspiratory.com"
ALT_TARGET = "example.com"
NONCE = "9" * 64
ALT_NONCE = "8" * 64
AUTHORIZED_AT = "2026-09-01T20:00:00.000000Z"
ALT_AUTHORIZED_AT = "2026-09-01T21:00:00.000000Z"
SOFTWARE = "conformance-ranked-keywords-paid-probe-v1"
REQUEST_STARTED_AT = "2026-09-01T20:00:00.100000Z"
RESPONSE_HEADERS_AT = "2026-09-01T20:00:00.200000Z"
RESPONSE_BODY_ENDED_AT = "2026-09-01T20:00:00.300000Z"
TRANSPORT_ENDED_AT = "2026-09-01T20:00:00.400000Z"

ITEM_TYPES = ["organic", "paid", "featured_snippet", "local_pack", "ai_overview_reference"]

# Independent literals. Written by hand from the closed RANK-02 contract, NOT derived from
# any production constructor. The production path must reproduce these exactly.
RK_REQUEST_BODY = (
    b'[{"historical_serp_mode":"all","ignore_synonyms":false,'
    b'"include_clickstream_data":false,'
    b'"item_types":["organic","paid","featured_snippet","local_pack",'
    b'"ai_overview_reference"],"language_code":"en","limit":100,'
    b'"load_rank_absolute":true,"location_code":2840,"offset":0,'
    b'"order_by":["ranked_serp_element.serp_item.rank_group,asc"],'
    b'"target":"theconspiratory.com"}]'
)
RK_REQUEST_BODY_SHA256 = "70ef3e2a12ac7a6f840fd98ad0c114622a8f1d28163aaafa3aafa2dd3094a758"
RK_FINGERPRINT = "e082900f9253eb5aa5729a65b5d55716fdf06e9aefb77add3f01ab3db1cbdf2f"
RK_ATTEMPT_ID = "7b61e54336c109d12a6747a29e0d78a6e5a3a2b38d022de1c2c1bd255bd66347"
ALT_ATTEMPT_ID = "fcfaad5a9120016a6caf94d87d7603a289b7144670a3be9814a60b308f574d8f"
RK_RESPONSE_BODY = b'{"cost":0.024}'
# Existing accepted adapter vectors that must remain byte-identical.
ORGANIC_ATTEMPT_ID = "b577bc1fb75f4ba7576a96c1328fbe74df9d975f3bd03f6c01d7441dfed1a1be"
PAID_ATTEMPT_ID = "89904bf8a6812fb3d0d845310e4705962bb4db928b80da3be67342dff5def185"
RELATED_ATTEMPT_ID = "5a673a457e994be7fa432f755a1ff8bd7df65a0da9d2c9a5aa35c309a26e9fc6"
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
    target: str = TARGET,
    *,
    nonce: str = NONCE,
    authorized_at: str = AUTHORIZED_AT,
) -> RankedKeywordsPaidProbeInputs:
    return RankedKeywordsPaidProbeInputs(
        target=target,
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
    inputs: RankedKeywordsPaidProbeInputs | None = None,
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


def _rk_attempt(
    target: str = TARGET,
    *,
    nonce: str = NONCE,
    authorized_at: str = AUTHORIZED_AT,
) -> dict[str, object]:
    return ranked_keywords_http_attempt_document(
        parameters=closed_ranked_keywords_parameters(target=target),
        attempt_nonce=nonce,
        authorized_at=authorized_at,
        observatory_version=SOFTWARE,
    )


def _rk_body(target: str = TARGET) -> bytes:
    return ranked_keywords_request_body_bytes(
        closed_ranked_keywords_parameters(target=target)
    )


def _issue_rk(store: EvidenceStore, target: str = TARGET) -> Any:
    return _issue_verified_attempt(
        store,
        _rk_attempt(target),
        _rk_body(target),
        authorize_max_micro_usd=AUTHORIZE,
    )


def _issuance_record(capability: object) -> Any:
    """Reach the closure-owned issuance record through GC only.

    The production module publishes no accessor for this record. The helper exists solely
    so hostile tests can prove that mutating closure-owned state still cannot authorize a
    send, replay an exchange, or redirect Capture parentage.
    """

    for referrer in gc.get_referrers(capability):
        if type(referrer).__name__ == "_Issuance":
            return referrer
    raise AssertionError("closure-owned issuance record was not reachable")


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


def _commit_related_neighbour(store: EvidenceStore) -> str:
    parameters = closed_related_keywords_parameters(keyword="conspiracy theories")
    return store.commit_attempt(
        related_keywords_http_attempt_document(
            parameters=parameters,
            attempt_nonce="6" * 64,
            authorized_at="2026-08-28T20:00:00.000000Z",
            observatory_version="conformance-related-keywords-paid-probe-v1",
        ),
        request_body=related_keywords_request_body_bytes(parameters),
    )


# --- closed contract, vector, and identity ----------------------------------


def test_closed_request_vector_and_attempt_identity() -> None:
    parameters = closed_ranked_keywords_parameters(target=TARGET)
    body = ranked_keywords_request_body_bytes(parameters)
    assert body == RK_REQUEST_BODY
    assert len(body) == 359
    assert content_digest(body) == RK_REQUEST_BODY_SHA256
    attempt = _rk_attempt()
    request = attempt["request"]
    assert isinstance(request, Mapping)
    fingerprint = ranked_keywords_http_fingerprint_document(request=request)
    assert content_digest(canonical_json(fingerprint)) == RK_FINGERPRINT
    assert attempt["request_fingerprint"] == RK_FINGERPRINT
    assert content_digest(canonical_json(attempt)) == RK_ATTEMPT_ID
    task = json.loads(body)
    assert isinstance(task, list) and len(task) == 1
    assert "contract" not in task[0]
    assert parameters["contract"] == RANKED_KEYWORDS_ADAPTER_CONTRACT
    assert PRODUCTION_URL == "https://api.dataforseo.com/v3/dataforseo_labs/google/ranked_keywords/live"


def test_every_closed_request_value_is_exact() -> None:
    task = json.loads(RK_REQUEST_BODY)[0]
    assert task == {
        "historical_serp_mode": "all",
        "ignore_synonyms": False,
        "include_clickstream_data": False,
        "item_types": ITEM_TYPES,
        "language_code": "en",
        "limit": 100,
        "load_rank_absolute": True,
        "location_code": 2840,
        "offset": 0,
        "order_by": ["ranked_serp_element.serp_item.rank_group,asc"],
        "target": TARGET,
    }
    assert task["ignore_synonyms"] is False
    assert task["include_clickstream_data"] is False
    assert task["load_rank_absolute"] is True
    assert "filters" not in task
    assert "tag" not in task
    assert "location_name" not in task
    assert "language_name" not in task


def test_item_types_order_is_provider_significant() -> None:
    parameters = closed_ranked_keywords_parameters(target=TARGET)
    assert parameters["item_types"] == ITEM_TYPES
    # Exact sequence equality, not set equality: order changes the returned ordering.
    reordered = ["paid", "organic", "featured_snippet", "local_pack", "ai_overview_reference"]
    assert set(reordered) == set(ITEM_TYPES)
    assert reordered != ITEM_TYPES
    candidate = dict(parameters)
    candidate["item_types"] = reordered
    with pytest.raises(DocumentError):
        validate_ranked_keywords_http_parameters(candidate)
    assert canonical_json([{"item_types": reordered}]) != canonical_json(
        [{"item_types": ITEM_TYPES}]
    )
    for bad in (
        list(reversed(ITEM_TYPES)),
        ITEM_TYPES[:4],
        [*ITEM_TYPES, "organic"],
        [*ITEM_TYPES[:4], "video"],
        [],
        "organic",
        tuple(ITEM_TYPES),
        [*ITEM_TYPES[:4], None],
    ):
        candidate = dict(parameters)
        candidate["item_types"] = bad
        with pytest.raises(DocumentError):
            validate_ranked_keywords_http_parameters(candidate)


def test_alternate_contract_values_fail_closed() -> None:
    base = dict(closed_ranked_keywords_parameters(target=TARGET))
    mutations: list[dict[str, object]] = [
        {"limit": 1000},
        {"limit": 99},
        {"limit": True},
        {"offset": 100},
        {"offset": True},
        {"location_code": 2826},
        {"location_code": True},
        {"language_code": "de"},
        {"ignore_synonyms": True},
        {"include_clickstream_data": True},
        {"load_rank_absolute": False},
        {"historical_serp_mode": "live"},
        {"historical_serp_mode": "lost"},
        {"order_by": []},
        {"order_by": ["ranked_serp_element.serp_item.rank_absolute,asc"]},
        {"order_by": "ranked_serp_element.serp_item.rank_group,asc"},
        {"order_by": ["ranked_serp_element.serp_item.rank_group,asc", "x,desc"]},
        {"filters": []},
        {"tag": "rank"},
        {"location_name": "United States"},
        {"language_name": "English"},
        {"unknown_key": 1},
        {"contract": RELATED_KEYWORDS_ADAPTER_CONTRACT},
    ]
    for mutation in mutations:
        candidate = dict(base)
        candidate.update(mutation)
        with pytest.raises(DocumentError):
            validate_ranked_keywords_http_parameters(candidate)
    for missing in base:
        candidate = {key: value for key, value in base.items() if key != missing}
        with pytest.raises(DocumentError):
            validate_ranked_keywords_http_parameters(candidate)


# --- Observatory two-label ASCII domain restriction ---------------------------


@pytest.mark.parametrize(
    "target",
    [
        "theconspiratory.com",
        "example.com",
        "a1-b.com",
        "a.co",
        "0a.io",
        "ex--ample.net",
        "x" * 63 + ".com",
        "ab." + "c" * 63,
    ],
)
def test_target_grammar_accepts_two_label_ascii_domains(target: str) -> None:
    parameters = closed_ranked_keywords_parameters(target=target)
    assert parameters["target"] == target


@pytest.mark.parametrize(
    "target",
    [
        "www.com",
        "www.theconspiratory.com",
        "blog.theconspiratory.com",
        "example.co.uk",
        "xn--fsq.com",
        "com.xn--fsq",
        "127.0.0.1",
        "localhost",
        "Example.com",
        "THECONSPIRATORY.COM",
        "theConspiratory.com",
        "ünïcode.com",
        "еxample.com",
        "http://example.com",
        "https://example.com",
        "//example.com",
        "example.com/",
        "example.com/path",
        "example.com:443",
        "example.com?q=1",
        "example.com#fragment",
        "user:pass@example.com",
        "user@example.com",
        "example.com.",
        ".example.com",
        " example.com",
        "example.com ",
        "exam ple.com",
        "example.com\n",
        "example.com\r",
        "example.com\t",
        "example\n.com",
        "\nexample.com",
        "ex_ample.com",
        "example_.com",
        ".com",
        "example.",
        "-example.com",
        "example-.com",
        "example.-com",
        "example.com-",
        "example.1com",
        "example.9",
        "a" * 64 + ".com",
        "ab." + "c" * 64,
        "",
        ".",
        "..",
        "example..com",
        "example",
        "a.b.c",
    ],
)
def test_target_grammar_rejects_without_normalizing(target: str) -> None:
    with pytest.raises(DocumentError):
        closed_ranked_keywords_parameters(target=target)


def test_target_grammar_rejects_rather_than_repairing() -> None:
    """Rejected forms must never be lowercased, peeled, stripped, or IDNA-encoded."""

    for hostile in (
        "WWW.THECONSPIRATORY.COM",
        "https://theconspiratory.com/",
        "www.theconspiratory.com",
        "theconspiratory.com.",
    ):
        with pytest.raises(DocumentError):
            closed_ranked_keywords_parameters(target=hostile)
    accepted = closed_ranked_keywords_parameters(target=TARGET)
    assert accepted["target"] == TARGET
    assert ranked_keywords_request_body_bytes(accepted) == RK_REQUEST_BODY


def test_target_grammar_rejects_non_string() -> None:
    base = dict(closed_ranked_keywords_parameters(target=TARGET))
    for value in (None, 5, True, ["a"], {"a": 1}, b"example.com"):
        candidate = dict(base)
        candidate["target"] = value
        with pytest.raises(DocumentError):
            validate_ranked_keywords_http_parameters(candidate)


def test_request_object_is_the_closed_ranked_keywords_target() -> None:
    request = ranked_keywords_http_request(body=RK_REQUEST_BODY)
    assert request["host"] == RANKED_KEYWORDS_HOST
    assert request["path"] == RANKED_KEYWORDS_PATH
    assert request["method"] == "POST"
    assert request["scheme"] == "https"
    assert request["port"] is None
    assert request["query"] == []
    validate_ranked_keywords_http_request(request)
    with pytest.raises(DocumentError):
        ranked_keywords_http_request(body=b"")
    for bad_path in (
        "/v3/dataforseo_labs/google/related_keywords/live",
        "/v3/dataforseo_labs/google/keyword_overview/live",
        "/v3/dataforseo_labs/google/ranked_keywords/task_post",
    ):
        wrong = dict(request)
        wrong["path"] = bad_path
        with pytest.raises(DocumentError):
            validate_ranked_keywords_http_request(wrong)


def test_existing_adapter_identities_and_validators_unchanged() -> None:
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
    related_parameters = closed_related_keywords_parameters(keyword="conspiracy theories")
    related = related_keywords_http_attempt_document(
        parameters=related_parameters,
        attempt_nonce="6" * 64,
        authorized_at="2026-08-28T20:00:00.000000Z",
        observatory_version="conformance-related-keywords-paid-probe-v1",
    )
    assert content_digest(canonical_json(related)) == RELATED_ATTEMPT_ID
    assert RANKED_KEYWORDS_ADAPTER_CONTRACT not in {
        HTTP_ADAPTER_CONTRACT,
        PAID_ADAPTER_CONTRACT,
        ORGANIC_ADAPTER_CONTRACT,
        RELATED_KEYWORDS_ADAPTER_CONTRACT,
    }
    # Neighbouring validators must not have been widened to accept the Ranked contract.
    with pytest.raises(DocumentError):
        validate_related_keywords_http_parameters(
            closed_ranked_keywords_parameters(target=TARGET)
        )
    with pytest.raises(DocumentError):
        validate_ranked_keywords_http_parameters(related_parameters)


def test_adapter_owns_32mib_and_120s_read_timeout() -> None:
    assert MAX_RESPONSE_BODY_BYTES == 33_554_432
    assert _TIMEOUT.connect == 30.0
    assert _TIMEOUT.read == 120.0
    assert _TIMEOUT.write == 30.0
    assert _TIMEOUT.pool == 30.0
    assert RANKED_KEYWORDS_AUTHORIZED_COST_MICRO_USD == 50000
    policy = validate_attempt(_rk_attempt())["policy"]
    assert isinstance(policy, Mapping)
    assert policy["max_authorized_cost_micro_usd"] == 50000
    assert policy["mode"] == "paid_probe"
    assert policy["policy_version"] == (
        "dataforseo-labs-google-ranked-keywords-live-paid-probe-v1"
    )
    assert policy["pricing_basis"] == (
        "dataforseo-labs-google-ranked-keywords-live-2026-09-01"
    )


def test_production_client_disables_redirects_proxies_http2_and_retries() -> None:
    client = production_http_client(_TIMEOUT)
    try:
        assert client.follow_redirects is False
        assert client.trust_env is False
        assert client.timeout == _TIMEOUT
        assert dict(client.headers) == {}
        # Private httpx/httpcore seams: the only place these settings are observable.
        pool = client._transport._pool  # type: ignore[attr-defined]
        assert pool._http2 is False
        assert pool._http1 is True
        assert pool._retries == 0
    finally:
        client.close()


# --- authorization and store gates ------------------------------------------


def test_exact_authorization_required_at_the_library_boundary(tmp_path: Path) -> None:
    store = create_store(tmp_path / "auth")
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, RK_RESPONSE_BODY)

    for value in (
        0,
        20000,
        49999,
        50001,
        200000,
        True,
        False,
        50000.0,
        "50000",
        Decimal(50000),
        None,
        [50000],
    ):
        with pytest.raises(StoreError, match="authorize-max-micro-usd 50000"):
            _capture_mock(store, handler, authorize=value)
        with pytest.raises(StoreError, match="authorize-max-micro-usd 50000"):
            _issue_verified_attempt(
                store,
                _rk_attempt(),
                RK_REQUEST_BODY,
                authorize_max_micro_usd=value,
            )
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
    object.__setattr__(forged, "attempt_id", RK_ATTEMPT_ID)
    object.__setattr__(forged, "document", _rk_attempt())
    object.__setattr__(forged, "request_body", RK_REQUEST_BODY)
    object.__setattr__(forged, "_used", False)
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(forged, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _committed_attempt(forged)

    class _Subclass(_VerifiedAttempt):  # type: ignore[misc]
        pass

    subclass: Any = object.__new__(_Subclass)
    object.__setattr__(subclass, "attempt_id", RK_ATTEMPT_ID)
    object.__setattr__(subclass, "document", _rk_attempt())
    object.__setattr__(subclass, "request_body", RK_REQUEST_BODY)
    object.__setattr__(subclass, "_used", False)
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(subclass, _credentials())

    ranked_store = create_store(tmp_path / "ranked")
    ranked_cap = _issue_rk(ranked_store)
    related_store = create_store(tmp_path / "related")
    related_parameters = closed_related_keywords_parameters(keyword="conspiracy theories")
    related_cap = issue_related(
        related_store,
        related_keywords_http_attempt_document(
            parameters=related_parameters,
            attempt_nonce="6" * 64,
            authorized_at="2026-08-28T20:00:00.000000Z",
            observatory_version="conformance-related-keywords-paid-probe-v1",
        ),
        related_keywords_request_body_bytes(related_parameters),
        authorize_max_micro_usd=200000,
    )
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(related_cap, _credentials())
    with pytest.raises(TypeError, match="verified committed Attempt"):
        related_exchange(ranked_cap, _credentials())


def test_visible_body_replacement_refuses_before_transport(tmp_path: Path) -> None:
    store = create_store(tmp_path / "body")
    issued = _issue_rk(store)
    replacement = _rk_body(ALT_TARGET)
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
    replacement = _rk_attempt(ALT_TARGET)
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
    replacement = _rk_attempt(ALT_TARGET)
    validate_attempt(replacement)
    object.__setattr__(issued, "document", replacement)
    object.__setattr__(issued, "request_body", _rk_body(ALT_TARGET))
    client, calls = _refusing_client()
    try:
        with pytest.raises(StoreError, match="closure-owned issuance record"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == []


def test_visible_attempt_id_replacement_refuses_before_transport(tmp_path: Path) -> None:
    store = create_store(tmp_path / "visibleid")
    issued = _issue_rk(store)
    object.__setattr__(issued, "attempt_id", ALT_ATTEMPT_ID)
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


def test_closure_owned_consumed_reset_cannot_replay(tmp_path: Path) -> None:
    """Replay safety must not rest on one mutable flag, visible or closure-owned."""

    store = create_store(tmp_path / "consumedreset")
    issued = _issue_rk(store)
    client, calls = _sending_client()
    try:
        first = _exchange(issued, _credentials(), client=client)
        record = _issuance_record(issued)
        assert record.consumed is True
        object.__setattr__(issued, "_used", False)
        object.__setattr__(record, "consumed", False)
        assert record.consumed is False
        with pytest.raises(StoreError, match="one-exchange"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert first.transport_state == "response_complete"
    assert calls == [RK_REQUEST_BODY]


def test_closure_owned_store_substitution_cannot_redirect_send(tmp_path: Path) -> None:
    store = create_store(tmp_path / "substitute-a")
    issued = _issue_rk(store)
    record = _issuance_record(issued)

    empty = create_store(tmp_path / "substitute-empty")
    object.__setattr__(record, "store", empty)
    client, calls = _refusing_client()
    try:
        with pytest.raises(StoreError, match="committed Evidence root"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == []
    assert empty.list_committed_ids("attempts") == []


def test_closure_owned_store_and_root_substitution_still_fails_closed(
    tmp_path: Path,
) -> None:
    """Defeat the root binding too; the committed-bytes checks must still refuse."""

    store = create_store(tmp_path / "substitute-b")
    issued = _issue_rk(store)
    record = _issuance_record(issued)

    decoy = create_store(tmp_path / "decoy")
    decoy_attempt = _rk_attempt(ALT_TARGET, nonce=ALT_NONCE, authorized_at=ALT_AUTHORIZED_AT)
    decoy.commit_attempt(decoy_attempt, request_body=_rk_body(ALT_TARGET))
    assert len(decoy.list_committed_ids("attempts")) == 1

    object.__setattr__(record, "store", decoy)
    object.__setattr__(record, "root", decoy.root)
    client, calls = _refusing_client()
    try:
        with pytest.raises(StoreError, match="not readable as Evidence"):
            _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == []


def test_closure_owned_store_substitution_after_exchange_cannot_reparent(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path / "substitute-post")
    issued = _issue_rk(store)
    client, calls = _sending_client()
    try:
        result = _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == [RK_REQUEST_BODY]

    record = _issuance_record(issued)
    decoy = create_store(tmp_path / "decoy-post")
    decoy_attempt = _rk_attempt(ALT_TARGET, nonce=ALT_NONCE, authorized_at=ALT_AUTHORIZED_AT)
    decoy.commit_attempt(decoy_attempt, request_body=_rk_body(ALT_TARGET))
    object.__setattr__(record, "store", decoy)
    object.__setattr__(record, "root", decoy.root)

    capture_id = _commit_ranked_keywords_capture(store, issued, result, _credentials())
    capture = store.read_capture(capture_id)
    assert capture is not None
    assert capture["attempt_id"] == RK_ATTEMPT_ID
    assert decoy.list_committed_ids("captures") == []


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


def test_committed_attempt_document_tamper_refused(tmp_path: Path) -> None:
    store = create_store(tmp_path / "attempttamper")
    issued = _issue_rk(store)
    bundle = _attempt_bundle(store, issued)
    (bundle / "attempt.json").write_bytes(canonical_json(_rk_attempt(ALT_TARGET)))
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
            PRODUCTION_URL,
            f"https://{RANKED_KEYWORDS_HOST}{RANKED_KEYWORDS_PATH}",
            "https://127.0.0.1:9" + RANKED_KEYWORDS_PATH,
            "http://localhost:9" + RANKED_KEYWORDS_PATH,
            "http://[::1]:9" + RANKED_KEYWORDS_PATH,
            "http://127.0.0.1:9/v3/dataforseo_labs/google/related_keywords/live",
            "http://127.0.0.1:9" + RANKED_KEYWORDS_PATH + "?x=1",
            "http://127.0.0.1:9" + RANKED_KEYWORDS_PATH + "#f",
            "http://user:pass@127.0.0.1:9" + RANKED_KEYWORDS_PATH,
            "http://127.0.0.2:9" + RANKED_KEYWORDS_PATH,
            "http://127.0.0.1" + RANKED_KEYWORDS_PATH,
            "http://127.0.0.1:0" + RANKED_KEYWORDS_PATH,
            "ftp://127.0.0.1:9" + RANKED_KEYWORDS_PATH,
            "",
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
    # The public constructor already refuses empty values, so an empty credential object
    # is built through the private seam. Passing a constructor call here would raise before
    # ever reaching the gate and prove nothing.
    empty = object.__new__(DataForSEOCredentials)
    object.__setattr__(empty, "_login", "")
    object.__setattr__(empty, "_password", "")
    refusing, refused = _refusing_client()
    try:
        with pytest.raises(CredentialError):
            _exchange(issued, empty, client=refusing)
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


# --- closure-owned authority AFTER exchange ---------------------------------


def test_post_exchange_mirror_mutation_cannot_change_capture_or_result(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path / "postexchange")
    issued = _issue_rk(store)
    client, calls = _sending_client()
    try:
        result = _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == [RK_REQUEST_BODY]

    replacement = _rk_attempt(ALT_TARGET)
    validate_attempt(replacement)
    replacement_id = content_digest(canonical_json(replacement))
    assert replacement_id == ALT_ATTEMPT_ID != RK_ATTEMPT_ID
    object.__setattr__(issued, "document", replacement)
    object.__setattr__(issued, "attempt_id", replacement_id)
    object.__setattr__(issued, "request_body", _rk_body(ALT_TARGET))

    # Commit the replacement Attempt too, so the mis-parented Capture would be a *valid*
    # commit if the mirror still had authority.
    store.commit_attempt(replacement, request_body=_rk_body(ALT_TARGET))
    assert store.read_attempt(replacement_id) is not None

    capture_id = _commit_ranked_keywords_capture(store, issued, result, _credentials())
    capture = store.read_capture(capture_id)
    assert capture is not None
    assert capture["attempt_id"] == RK_ATTEMPT_ID
    assert capture["attempt_id"] != replacement_id
    committed_id, committed_document = _committed_attempt(issued)
    assert committed_id == RK_ATTEMPT_ID
    assert content_digest(canonical_json(committed_document)) == RK_ATTEMPT_ID


def test_private_snapshot_mutation_cannot_poison_closure_authority(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path / "authority-leak")
    issued = _issue_rk(store)
    client, calls = _sending_client()
    try:
        result = _exchange(issued, _credentials(), client=client)
    finally:
        client.close()
    assert calls == [RK_REQUEST_BODY]

    replacement = _rk_attempt(ALT_TARGET)
    store.commit_attempt(replacement, request_body=_rk_body(ALT_TARGET))
    assert store.read_attempt(ALT_ATTEMPT_ID) is not None

    committed_id, snapshot = _committed_attempt(issued)
    assert committed_id == RK_ATTEMPT_ID
    snapshot.clear()
    snapshot.update(replacement)
    parameters = snapshot.get("parameters")
    assert isinstance(parameters, dict)
    parameters["target"] = ALT_TARGET

    reread_id, reread = _committed_attempt(issued)
    assert reread_id == RK_ATTEMPT_ID
    assert content_digest(canonical_json(reread)) == RK_ATTEMPT_ID
    assert reread["attempt_nonce"] == NONCE
    reread_parameters = reread["parameters"]
    assert isinstance(reread_parameters, Mapping)
    assert reread_parameters["target"] == TARGET

    capture_id = _commit_ranked_keywords_capture(store, issued, result, _credentials())
    capture = store.read_capture(capture_id)
    assert capture is not None
    assert capture["attempt_id"] == RK_ATTEMPT_ID


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
    assert str(request.url) == PRODUCTION_URL
    assert request.url.query == b""
    assert request.content == RK_REQUEST_BODY
    assert request.headers["authorization"] == SENTINEL_BASIC
    assert request.headers["content-type"] == "application/json"
    assert request.headers["accept"] == "application/json"
    assert request.headers["accept-encoding"] == "identity"
    assert request.headers["connection"] == "close"
    assert request.headers["user-agent"] == "observatory-dataforseo-v1"
    assert request.headers["host"] == RANKED_KEYWORDS_HOST
    assert request.headers["content-length"] == str(len(RK_REQUEST_BODY))
    assert outcome.transport_state == "response_complete"


def test_synthetic_continuation_fields_do_not_cause_a_second_exchange(
    tmp_path: Path,
) -> None:
    """Structural proof: the adapter never parses the body, so it cannot continue."""

    store = create_store(tmp_path / "continuation")
    body = json.dumps(
        {
            "tasks": [
                {
                    "id": "keep-going",
                    "result": [
                        {
                            "target": TARGET,
                            "total_count": 5000,
                            "items_count": 100,
                            "offset": 0,
                            "offset_token": "next-page",
                            "items": [],
                        }
                    ],
                }
            ]
        }
    ).encode()
    calls: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.content)
        return _streamed_response(200, body)

    outcome = _capture_mock(store, handler)
    assert calls == [RK_REQUEST_BODY]
    assert outcome.transport_state == "response_complete"
    assert store.read_capture_body(outcome.capture_id) == body
    assert inspect_ranked_keywords_paid_probe_body(store, outcome.capture_id) == body
    assert len(store.list_committed_ids("attempts")) == 1
    assert len(store.list_committed_ids("captures")) == 1


def test_non_2xx_zero_byte_and_body_ceiling_branches(tmp_path: Path) -> None:
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
        inspect_ranked_keywords_paid_probe_body(empty_store, empty.capture_id)

    ceiling_store = create_store(tmp_path / "ceiling")
    calls: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.content)
        return _streamed_response(200, b"x" * 4096)

    limited = _capture_mock(
        ceiling_store, handler, max_response_body_bytes=SMALL_LIMIT
    )
    # A body-ceiling event is the existing PF-09 partial state, not a new classification.
    # There is deliberately no adapter-invented `over_limit` transport state.
    assert limited.transport_state == "response_partial"
    assert limited.transport_state in {
        "response_complete",
        "response_partial",
        "no_response",
    }
    assert calls == [RK_REQUEST_BODY]
    body = ceiling_store.read_capture_body(limited.capture_id)
    assert body is not None and len(body) == SMALL_LIMIT
    ceiling_capture = ceiling_store.read_capture(limited.capture_id)
    assert ceiling_capture is not None
    assert ceiling_capture["transport_state"] == "response_partial"
    ceiling_response = ceiling_capture["response"]
    assert isinstance(ceiling_response, Mapping)
    assert ceiling_response["completeness"] == "partial"
    with pytest.raises(StoreError, match="verified complete"):
        inspect_ranked_keywords_paid_probe_body(ceiling_store, limited.capture_id)


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
    assert capture["response"] is None


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
            endpoint="http://127.0.0.1:8931" + RANKED_KEYWORDS_PATH,
            client=client,
        )
    finally:
        client.close()
    assert len(seen) == 1
    assert str(seen[0].url) == "http://127.0.0.1:8931" + RANKED_KEYWORDS_PATH
    assert seen[0].content == RK_REQUEST_BODY
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
    omitted = response["omitted_headers"]
    assert isinstance(omitted, list)
    assert {entry["name"] for entry in omitted} == set(DENYLIST)
    chunks: list[bytes] = []
    for path in sorted(store.root.rglob("*")):
        if path.is_file():
            chunks.append(path.read_bytes())
    _assert_no_secrets(b"\n".join(chunks).decode("utf-8", "replace"))


def test_credential_echo_in_body_is_refused(tmp_path: Path) -> None:
    store = create_store(tmp_path / "echo")
    with pytest.raises(StoreError, match="credential material") as excinfo:
        _capture_mock(
            store,
            lambda request: _streamed_response(200, SENTINEL_PASSWORD.encode()),
        )
    _assert_no_secrets(str(excinfo.value))
    assert store.list_committed_ids("captures") == []
    assert len(store.list_committed_ids("attempts")) == 1


def test_credential_echo_in_header_is_refused(tmp_path: Path) -> None:
    store = create_store(tmp_path / "echohdr")
    with pytest.raises(StoreError, match="credential material") as excinfo:
        _capture_mock(
            store,
            lambda request: _streamed_response(
                200,
                RK_RESPONSE_BODY,
                [("x-echo", SENTINEL_LOGIN), ("content-type", "application/json")],
            ),
        )
    _assert_no_secrets(str(excinfo.value))
    assert store.list_committed_ids("captures") == []


# --- one-shot semantics ------------------------------------------------------


def _first_attempt(store: EvidenceStore, first: str) -> None:
    if first == "complete":
        _capture_mock(store, lambda request: _streamed_response(200, RK_RESPONSE_BODY))
    elif first == "body_ceiling_partial":
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
    elif first == "transport_exception":
        def _interrupt(request: httpx.Request) -> httpx.Response:
            raise KeyboardInterrupt("operator abort mid-exchange")

        with pytest.raises(KeyboardInterrupt):
            _capture_mock(store, _interrupt)
        assert store.list_committed_ids("captures") == []
    else:
        store.commit_attempt(_rk_attempt(), request_body=RK_REQUEST_BODY)


@pytest.mark.parametrize(
    "first",
    [
        "complete",
        "body_ceiling_partial",
        "no_response",
        "credential_echo",
        "transport_exception",
        "unresolved",
    ],
)
def test_one_shot_refuses_second_attempt_after_any_first_state(
    tmp_path: Path, first: str
) -> None:
    store = create_store(tmp_path / f"oneshot-{first}")
    _first_attempt(store, first)
    assert len(store.list_committed_ids("attempts")) == 1
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, RK_RESPONSE_BODY)

    with pytest.raises(StoreError, match="ranked-keywords paid-probe Attempt"):
        _capture_mock(
            store,
            handler,
            _inputs(ALT_TARGET, nonce=ALT_NONCE, authorized_at=ALT_AUTHORIZED_AT),
        )
    assert calls == []
    assert len(store.list_committed_ids("attempts")) == 1


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
    related_id = _commit_related_neighbour(store)
    assert related_id == RELATED_ATTEMPT_ID
    outcome = _capture_mock(store, lambda request: _streamed_response(200, RK_RESPONSE_BODY))
    assert outcome.attempt_id == RK_ATTEMPT_ID
    assert scrub_store(store) == []


def test_one_shot_scan_fails_closed_on_damaged_committed_attempt(tmp_path: Path) -> None:
    """A discovered commitment that cannot be verified must never be silently skipped."""

    store = create_store(tmp_path / "damaged")
    related_id = _commit_related_neighbour(store)
    bundle = store._find_bundle("attempts", related_id)
    assert bundle is not None
    (bundle / "attempt.json").write_bytes(b'{"tampered":true}')
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, RK_RESPONSE_BODY)

    with pytest.raises(StoreError, match="cannot be verified or classified"):
        _capture_mock(store, handler)
    assert calls == []
    assert store.list_committed_ids("attempts") == [related_id]


def test_one_shot_scan_fails_closed_on_missing_committed_manifest(tmp_path: Path) -> None:
    store = create_store(tmp_path / "missing")
    related_id = _commit_related_neighbour(store)
    bundle = store._find_bundle("attempts", related_id)
    assert bundle is not None
    (bundle / "attempt.json").unlink()
    with pytest.raises(StoreError, match="cannot be verified or classified"):
        _capture_mock(store, lambda request: _streamed_response(200, RK_RESPONSE_BODY))
    assert store.list_committed_ids("attempts") == [related_id]


# --- inspect -----------------------------------------------------------------


def test_inspect_returns_exact_complete_body(tmp_path: Path) -> None:
    store = create_store(tmp_path / "inspect")
    body = b'{"tasks":[{"result":[{"target":"theconspiratory.com","items":[]}]}]}'
    outcome = _capture_mock(store, lambda request: _streamed_response(200, body))
    reader = inspect_store(store.root)
    assert inspect_ranked_keywords_paid_probe_body(reader, outcome.capture_id) == body


def test_inspect_rejects_bad_ids_and_uncommitted_material(tmp_path: Path) -> None:
    store = create_store(tmp_path / "inspectbad")
    _capture_mock(store, lambda request: _streamed_response(200, RK_RESPONSE_BODY))
    for bad in ("", "zz", "A" * 64, "g" * 64, RK_ATTEMPT_ID.upper(), 5, None):
        with pytest.raises(StoreError, match="capture-id is invalid"):
            inspect_ranked_keywords_paid_probe_body(store, bad)  # type: ignore[arg-type]
    with pytest.raises(StoreError, match="verified complete"):
        inspect_ranked_keywords_paid_probe_body(store, "0" * 64)


def test_inspect_rejects_valid_wrong_adapter_capture(tmp_path: Path) -> None:
    """A committed, valid, verifiable Capture from another adapter must be refused."""

    store = create_store(tmp_path / "wrongadapter")
    fixture = capture_fixture(store, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    assert store.read_capture(fixture.capture_id) is not None
    reader = inspect_store(store.root)
    with pytest.raises(StoreError, match="verified complete"):
        inspect_ranked_keywords_paid_probe_body(reader, fixture.capture_id)

    sibling = create_store(tmp_path / "relatedcapture")
    related_parameters = closed_related_keywords_parameters(keyword="conspiracy theories")
    related_attempt = related_keywords_http_attempt_document(
        parameters=related_parameters,
        attempt_nonce="6" * 64,
        authorized_at="2026-08-28T20:00:00.000000Z",
        observatory_version="conformance-related-keywords-paid-probe-v1",
    )
    sibling.commit_attempt(
        related_attempt,
        request_body=related_keywords_request_body_bytes(related_parameters),
    )
    related_response = b'{"cost":0.082}'
    related_capture_id = sibling.commit_capture(
        related_keywords_http_capture_document(
            attempt=related_attempt,
            request_started_at=REQUEST_STARTED_AT,
            transport_ended_at=TRANSPORT_ENDED_AT,
            transport_state="response_complete",
            response=_complete_response(related_response),
            transport_failure=None,
            response_headers_at=RESPONSE_HEADERS_AT,
            response_body_ended_at=RESPONSE_BODY_ENDED_AT,
        ),
        response_body=related_response,
    )
    sibling_reader = inspect_store(sibling.root)
    assert sibling_reader.read_capture(related_capture_id) is not None
    with pytest.raises(StoreError, match="verified complete"):
        inspect_ranked_keywords_paid_probe_body(sibling_reader, related_capture_id)


def test_inspect_rejects_response_body_tamper(tmp_path: Path) -> None:
    store = create_store(tmp_path / "inspecttamper")
    outcome = _capture_mock(store, lambda request: _streamed_response(200, RK_RESPONSE_BODY))
    reader = inspect_store(store.root)
    assert inspect_ranked_keywords_paid_probe_body(reader, outcome.capture_id) == (
        RK_RESPONSE_BODY
    )
    bundle = store.capture_path(outcome.capture_id)
    (bundle / "response.body").write_bytes(b"tampered-but-same-length")
    with pytest.raises(StoreError):
        inspect_ranked_keywords_paid_probe_body(inspect_store(store.root), outcome.capture_id)


def test_inspect_rejects_no_response_capture(tmp_path: Path) -> None:
    store = create_store(tmp_path / "inspectnoresp")

    def boom(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no")

    outcome = _capture_mock(store, boom)
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["transport_state"] == "no_response"
    reader = inspect_store(store.root)
    with pytest.raises(StoreError, match="verified complete"):
        inspect_ranked_keywords_paid_probe_body(reader, outcome.capture_id)


# --- public surface and CLI ---------------------------------------------------


def test_public_surface_exposes_no_contract_widening_seam() -> None:
    names = capture_dataforseo_google_ranked_keywords_paid_probe.__code__.co_varnames
    for hidden in (
        "endpoint",
        "max_response_body_bytes",
        "client",
        "limit",
        "offset",
        "item_types",
        "historical_serp_mode",
    ):
        assert hidden not in names
    fields = set(RankedKeywordsPaidProbeInputs.__dataclass_fields__)
    assert fields == {"target", "attempt_nonce", "authorized_at", "observatory_version"}


def test_cli_exposes_target_only_and_no_internal_seams(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = str(tmp_path / "cli-reject")
    for argv in (
        ["capture", "--evidence-root", root, "--target", TARGET],
        ["capture", "--evidence-root", root, "--keyword", TARGET,
         "--authorize-max-micro-usd", "50000"],
        ["capture", "--evidence-root", root, "--domain", TARGET,
         "--authorize-max-micro-usd", "50000"],
        ["capture", "--evidence-root", root, "--url", "https://" + TARGET,
         "--authorize-max-micro-usd", "50000"],
        ["capture", "--evidence-root", root, "--target", TARGET,
         "--authorize-max-micro-usd", "50000", "--limit", "100"],
        ["capture", "--evidence-root", root, "--target", TARGET,
         "--authorize-max-micro-usd", "50000", "--max-response-body-bytes", "16"],
        ["capture", "--evidence-root", root, "--target", TARGET,
         "--authorize-max-micro-usd", "50000", "--endpoint", "http://127.0.0.1:9/x"],
        ["inspect", "--evidence-root", root],
    ):
        with pytest.raises(SystemExit):
            main(argv)
    capsys.readouterr()
    assert not (tmp_path / "cli-reject").exists()


def test_cli_refuses_wrong_authorization_without_leaking(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(DATAFORSEO_LOGIN_ENV, SENTINEL_LOGIN)
    monkeypatch.setenv(DATAFORSEO_PASSWORD_ENV, SENTINEL_PASSWORD)
    code = main(
        [
            "capture",
            "--evidence-root",
            str(tmp_path / "cli"),
            "--target",
            TARGET,
            "--authorize-max-micro-usd",
            "20000",
        ]
    )
    assert code == 1
    captured = capsys.readouterr()
    assert "capture failed" in captured.err
    _assert_no_secrets(captured.err, captured.out)
    assert not (tmp_path / "cli").exists()


def test_cli_refuses_rejected_target_without_creating_evidence(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(DATAFORSEO_LOGIN_ENV, SENTINEL_LOGIN)
    monkeypatch.setenv(DATAFORSEO_PASSWORD_ENV, SENTINEL_PASSWORD)
    root = tmp_path / "clitarget"
    code = main(
        [
            "capture",
            "--evidence-root",
            str(root),
            "--target",
            "www." + TARGET,
            "--authorize-max-micro-usd",
            "50000",
        ]
    )
    assert code == 1
    captured = capsys.readouterr()
    assert "capture failed" in captured.err
    store = inspect_store(root)
    assert store.list_committed_ids("attempts") == []


def test_cli_requires_credentials(tmp_path: Path) -> None:
    code = main(
        [
            "capture",
            "--evidence-root",
            str(tmp_path / "nocreds"),
            "--target",
            TARGET,
            "--authorize-max-micro-usd",
            "50000",
        ]
    )
    assert code == 2
    assert not (tmp_path / "nocreds").exists()


def test_cli_inspect_writes_exact_bytes(
    tmp_path: Path, capsysbinary: pytest.CaptureFixture[bytes]
) -> None:
    store = create_store(tmp_path / "cliinspect")
    body = b'{"tasks":[{"result":[{"target":"theconspiratory.com"}]}]}'
    outcome = _capture_mock(store, lambda request: _streamed_response(200, body))
    code = main(
        ["inspect", "--evidence-root", str(store.root), "--capture-id", outcome.capture_id]
    )
    assert code == 0
    assert capsysbinary.readouterr().out == body


# --- isolation from existing Derivations -------------------------------------


def test_existing_derivations_skip_ranked_keywords_evidence(
    tmp_path: Path, postgres_dsn: str
) -> None:
    """Compatibility proof only. RANK-02 adds no Ranked Derivation semantics."""

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
    capture = ranked_keywords_http_capture_document(
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
        organic_summary = derive_google_organic(store, connection)
        related_summary = derive_google_related_keywords(store, connection)
        ranked_rows = connection.execute(
            "SELECT count(*) FROM outcomes WHERE attempt_id = %s OR capture_id = %s",
            (RK_ATTEMPT_ID, capture_id),
        ).fetchone()
        fixture_rows = connection.execute(
            "SELECT count(*) FROM outcomes WHERE attempt_id = %s",
            (fixture.attempt_id,),
        ).fetchone()
    assert fixture_summary.integrity_failures == 0
    assert ko_summary.integrity_failures == 0
    assert organic_summary.integrity_failures == 0
    assert related_summary.integrity_failures == 0
    assert ranked_rows == (0,)
    assert fixture_rows is not None and fixture_rows[0] >= 1
