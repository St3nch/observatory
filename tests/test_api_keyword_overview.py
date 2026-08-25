"""PF-08: provider Attempt audit and Keyword Overview history API."""

from __future__ import annotations

import copy
import json
import secrets
import shutil
import socket
from collections.abc import Callable, Mapping
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient

from observatory.api import create_app
from observatory.capture import FixtureCaptureInputs, capture_fixture
from observatory.capture_event import (
    body_ref,
    canonical_json,
    content_digest,
    paid_http_attempt_document,
    paid_http_capture_document,
    validate_capture,
)
from observatory.dataforseo_keyword_overview import (
    BACKLINKS_KIND,
    CORE_RECIPE,
    CORE_RECIPE_ID,
    COVERAGE_KIND,
    EXTENDED_RECIPE,
    EXTENDED_RECIPE_ID,
    INTENT_KIND,
    METRICS_KIND,
    MONTHLY_KIND,
    PROPERTIES_KIND,
    TREND_KIND,
)
from observatory.dataforseo_paid_probe import closed_paid_parameters, paid_request_body_bytes
from observatory.derive import DEFAULT_VERSION, derive
from observatory.evidence_store import EvidenceStore, IntegrityError, create_store
from observatory.keyword_overview_derive import (
    derive_keyword_overview,
    derive_keyword_overview_extended,
)
from observatory.migrate import apply_migrations, connect
from observatory.provider_recipe import (
    IDENTITY_SCHEMA,
    IDENTITY_VERSION,
    TEST_RECIPE,
    TEST_RECIPE_ID,
    observation_identity,
    recipe_bytes,
    register_provider_recipe,
)
from observatory.provider_recipe_selection import (
    NOT_SELECTED_SIGNAL,
    select_provider_recipe,
)
from observatory.settings import Settings

SHARED_TIMES = {
    "authorized_at": "2026-08-11T20:15:30.123456Z",
    "observatory_version": "conformance-v1",
    "request_started_at": "2026-08-11T20:15:30.200000Z",
    "transport_ended_at": "2026-08-11T20:15:31.000000Z",
}
HISTORY = "/v1/providers/dataforseo/google/keyword-overview/history"
OUTCOMES = "/v1/providers/dataforseo/google/keyword-overview/outcomes"
HOLDINGS = "/v1/providers/dataforseo/google/keyword-overview/holdings"
ORGANIC_HOLDINGS = "/v1/providers/dataforseo/google/organic/holdings"
MENTIONS_HOLDINGS = (
    "/v1/providers/dataforseo/google/ai-optimization/search-mentions/holdings"
)
HOLDINGS_KEYS = {
    "provider",
    "adapter_contract",
    "total_matching",
    "returned_count",
    "limit",
    "order",
    "has_more",
    "holdings",
}
HOLDINGS_ITEM_KEYS = {
    "requested_keyword",
    "request",
    "attempt_count",
    "capture_count",
    "unresolved_count",
    "first_authorized_at",
    "last_authorized_at",
    "first_request_started_at",
    "last_request_started_at",
}
HISTORY_KEYS = {
    "provider",
    "adapter_contract",
    "requested_keyword",
    "derivation_version_id",
    "recipe_resolution",
    "observation_kinds",
    "captures",
    "total_matching",
    "returned_count",
    "limit",
    "order",
    "has_more",
}
OUTCOMES_KEYS = {
    "provider",
    "adapter_contract",
    "requested_keyword",
    "derivation_version_id",
    "recipe_resolution",
    "observation_kinds",
    "total_matching",
    "returned_count",
    "limit",
    "order",
    "has_more",
    "outcomes",
}
OUTCOME_ITEM_KEYS = {
    "attempt_id",
    "capture_id",
    "provider",
    "adapter_contract",
    "derivation_version_id",
    "authorized_at",
    "request_started_at",
    "transport_ended_at",
    "transport_state",
    "request",
    "attempt_outcome",
    "capture_outcome",
}
KO_REQUEST_KEYS = {
    "keywords",
    "location_code",
    "language_code",
    "include_serp_info",
    "include_clickstream_data",
}


def _fixture_inputs() -> FixtureCaptureInputs:
    return FixtureCaptureInputs(
        scenario="admitted_results",
        panel_id="panel-alpha",
        subject_key="subject-one",
        depth=2,
        attempt_nonce=secrets.token_hex(32),
        response_headers_at="2026-08-11T20:15:30.900000Z",
        response_body_ended_at="2026-08-11T20:15:30.950000Z",
        **SHARED_TIMES,
    )

FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_keyword_overview_pf03.json"
)
KEYWORDS = (
    "seo api",
    "keyword research",
    "local seo",
    "generative engine optimization",
    "ai search optimization",
)
INTEGRITY_SIGNAL = "evidence_integrity_failure"


@pytest.fixture(autouse=True)
def _no_public_network(monkeypatch: pytest.MonkeyPatch) -> None:
    real = socket.create_connection

    def guarded(address: Any, *args: Any, **kwargs: Any) -> socket.socket:
        host = address[0] if isinstance(address, tuple) else address
        if host not in {"127.0.0.1", "::1", "localhost"}:
            raise AssertionError(f"public-network request forbidden: {host}")
        return real(address, *args, **kwargs)

    monkeypatch.setattr(socket, "create_connection", guarded)
PROVIDER_TABLES = (
    "provider_recipes",
    "provider_recipe_selections",
    "outcomes",
    "observation_envelopes",
    "keyword_overview_coverage",
    "keyword_overview_metrics",
    "keyword_overview_monthly_search_volume",
    "keyword_overview_search_volume_trend",
    "keyword_overview_properties",
    "keyword_overview_avg_backlinks",
    "keyword_overview_search_intent",
)


def _body() -> bytes:
    return FIXTURE.read_bytes()


def _decoded(body: bytes | None = None) -> dict[str, Any]:
    decoder = json.JSONDecoder(parse_int=int, parse_float=Decimal)
    value, _end = decoder.raw_decode((body or _body()).decode("utf-8"))
    assert isinstance(value, dict)
    return value


def _encode(value: object) -> bytes:
    if value is None:
        return b"null"
    if isinstance(value, bool):
        return b"true" if value else b"false"
    if isinstance(value, int):
        return str(value).encode()
    if isinstance(value, Decimal):
        return format(value, "f").encode()
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False).encode()
    if isinstance(value, list):
        return b"[" + b",".join(_encode(item) for item in value) + b"]"
    if isinstance(value, dict):
        parts = [
            json.dumps(str(key), ensure_ascii=False).encode() + b":" + _encode(item)
            for key, item in value.items()
        ]
        return b"{" + b",".join(parts) + b"}"
    raise TypeError(type(value))


def _commit_paid(
    store: EvidenceStore,
    body: bytes,
    nonce: str,
    *,
    started: str,
    authorized_at: str = "2026-08-16T21:37:00.000000Z",
    keywords: tuple[str, ...] = KEYWORDS,
) -> tuple[str, str]:
    parameters = closed_paid_parameters(keywords=list(keywords))
    attempt = paid_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at=authorized_at,
        observatory_version="pf08-test-v1",
    )
    attempt_id = store.commit_attempt(
        attempt, request_body=paid_request_body_bytes(parameters)
    )
    capture_id = store.commit_capture(
        paid_http_capture_document(
            attempt=attempt,
            request_started_at=started,
            transport_ended_at=started.replace(".100000Z", ".400000Z"),
            transport_state="response_complete",
            response={
                "status": 200,
                "http_version": "HTTP/1.1",
                "header_policy": "http-headers-v1",
                "headers": [["content-type", "application/json"]],
                "omitted_headers": [],
                "body": {"state": "present_nonempty", "body": body_ref(body)},
                "completeness": "complete",
            },
            transport_failure=None,
            response_headers_at=started.replace(".100000Z", ".200000Z"),
            response_body_ended_at=started.replace(".100000Z", ".300000Z"),
        ),
        response_body=body,
    )
    return attempt_id, capture_id


def _app(store: EvidenceStore, dsn: str) -> TestClient:
    settings = Settings(
        environment="test",
        database_url=dsn,
        evidence_root=store.root,
        derivation_version_id=DEFAULT_VERSION,
    )
    return TestClient(create_app(settings, store=store))


def _prepare_pf03(
    tmp_path: Path,
    postgres_dsn: str,
    *,
    extended: bool = True,
    core: bool = True,
    select: bool = True,
) -> tuple[EvidenceStore, str, str]:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_paid(
        store, _body(), "21" * 32, started="2026-08-16T21:37:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        if core:
            derive_keyword_overview(store, connection)
        if extended:
            derive_keyword_overview_extended(store, connection)
        if select and extended:
            select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
        elif select and core:
            select_provider_recipe(connection, store_adapter(), CORE_RECIPE_ID)
    return store, attempt_id, capture_id


def store_adapter() -> str:
    return "dataforseo-labs-google-keyword-overview-live-paid-probe-v1"


def _history(
    client: TestClient,
    keyword: str,
    **params: object,
) -> Any:
    query = {"requested_keyword": keyword, **params}
    return client.get(HISTORY + "?" + urlencode(query, doseq=True))


def _outcomes(
    client: TestClient,
    keyword: str,
    **params: object,
) -> Any:
    query = {"requested_keyword": keyword, **params}
    return client.get(OUTCOMES + "?" + urlencode(query, doseq=True))


def _assert_outcomes_envelope(
    body: dict[str, object],
    *,
    total_matching: int,
    returned_count: int,
    limit: int = 20,
    order: str = "asc",
) -> None:
    assert set(body) == OUTCOMES_KEYS
    assert body["total_matching"] == total_matching
    assert body["returned_count"] == returned_count
    assert body["limit"] == limit
    assert body["order"] == order
    assert body["has_more"] is (total_matching > returned_count)
    items = body["outcomes"]
    assert isinstance(items, list)
    assert len(items) == returned_count


def _assert_outcomes_409(response: Any) -> None:
    assert response.status_code == 409
    assert response.json() == {"detail": INTEGRITY_SIGNAL}
    payload = response.json()
    assert "outcomes" not in payload
    assert "total_matching" not in payload
    assert "returned_count" not in payload
    assert "has_more" not in payload


def _holdings(client: TestClient, **params: object) -> Any:
    if params:
        return client.get(HOLDINGS + "?" + urlencode(params, doseq=True))
    return client.get(HOLDINGS)


def _holdings_app(store: EvidenceStore, dsn: str | None = None) -> TestClient:
    settings = Settings(
        environment="test",
        database_url=dsn,
        evidence_root=store.root,
        derivation_version_id=DEFAULT_VERSION,
    )
    return TestClient(create_app(settings, store=store))


def _assert_holdings_envelope(
    body: dict[str, object],
    *,
    total_matching: int,
    returned_count: int,
    limit: int = 20,
    order: str = "asc",
) -> None:
    assert set(body) == HOLDINGS_KEYS
    assert body["provider"] == "dataforseo"
    assert body["adapter_contract"] == store_adapter()
    assert body["total_matching"] == total_matching
    assert body["returned_count"] == returned_count
    assert body["limit"] == limit
    assert body["order"] == order
    assert body["has_more"] is (total_matching > returned_count)
    items = body["holdings"]
    assert isinstance(items, list)
    assert len(items) == returned_count
    assert "requested_keyword" not in body
    assert "derivation_version_id" not in body
    assert "recipe_resolution" not in body
    assert "observation_kinds" not in body


def _assert_holdings_409(response: Any) -> None:
    assert response.status_code == 409
    assert response.json() == {"detail": INTEGRITY_SIGNAL}
    payload = response.json()
    assert "holdings" not in payload
    assert "total_matching" not in payload
    assert "returned_count" not in payload
    assert "has_more" not in payload


def _assert_holdings_item(item: dict[str, object]) -> None:
    assert set(item) == HOLDINGS_ITEM_KEYS
    assert "attempt_id" not in item
    assert "capture_id" not in item
    assert "request_fingerprint" not in item
    assert "derivation_version_id" not in item
    request = item["request"]
    assert isinstance(request, dict)
    assert set(request) == KO_REQUEST_KEYS
    assert "contract" not in request
    attempt_count = item["attempt_count"]
    capture_count = item["capture_count"]
    unresolved_count = item["unresolved_count"]
    assert isinstance(attempt_count, int)
    assert isinstance(capture_count, int)
    assert isinstance(unresolved_count, int)
    assert attempt_count == capture_count + unresolved_count


class _OverrideAttemptStore(EvidenceStore):
    def __init__(
        self,
        store: EvidenceStore,
        override: Callable[[dict[str, object], str], dict[str, object]],
    ) -> None:
        super().__init__(store.root)
        self._store = store
        self._override = override
        self.recorded_ops = store.recorded_ops

    def read_attempt(self, attempt_id: str) -> dict[str, object] | None:
        document = self._store.read_attempt(attempt_id)
        if document is None:
            return None
        return self._override(dict(document), attempt_id)

    def read_capture(self, capture_id: str) -> dict[str, object] | None:
        return self._store.read_capture(capture_id)

    def list_committed_ids(self, kind: Literal["attempts", "captures"]) -> list[str]:
        return self._store.list_committed_ids(kind)


def _plant_retargeted_capture(
    store: EvidenceStore, capture_id: str, attempt_id: str
) -> str:
    original = store.read_capture(capture_id)
    assert original is not None
    mutated = dict(original)
    mutated["attempt_id"] = attempt_id
    raw = canonical_json(validate_capture(mutated))
    planted_id = content_digest(raw)
    src = store.capture_path(capture_id)
    dst = store.capture_path(planted_id)
    shutil.copytree(src, dst)
    (dst / "capture.json").write_bytes(raw)
    (dst / "COMMITTED").write_bytes(f"{planted_id}\n".encode())
    return planted_id


def _commit_paid_attempt_only(
    store: EvidenceStore,
    nonce: str,
    *,
    authorized_at: str,
    keywords: tuple[str, ...] = KEYWORDS,
) -> str:
    parameters = closed_paid_parameters(keywords=list(keywords))
    attempt = paid_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at=authorized_at,
        observatory_version="pf08-test-v1",
    )
    return store.commit_attempt(attempt, request_body=paid_request_body_bytes(parameters))


def _commit_paid_no_response(
    store: EvidenceStore,
    nonce: str,
    *,
    started: str,
    authorized_at: str,
    keywords: tuple[str, ...] = KEYWORDS,
) -> tuple[str, str]:
    parameters = closed_paid_parameters(keywords=list(keywords))
    attempt = paid_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at=authorized_at,
        observatory_version="pf08-test-v1",
    )
    attempt_id = store.commit_attempt(
        attempt, request_body=paid_request_body_bytes(parameters)
    )
    capture_id = store.commit_capture(
        paid_http_capture_document(
            attempt=attempt,
            request_started_at=started,
            transport_ended_at=started.replace(".100000Z", ".400000Z"),
            transport_state="no_response",
            response=None,
            transport_failure={"phase": "connect", "code": "timeout"},
            response_headers_at=None,
            response_body_ended_at=None,
        ),
        response_body=None,
    )
    return attempt_id, capture_id


def _assert_history_envelope(
    body: dict[str, object],
    *,
    total_matching: int,
    returned_count: int,
    limit: int = 20,
    order: str = "asc",
) -> None:
    assert set(body) == HISTORY_KEYS
    assert body["total_matching"] == total_matching
    assert body["returned_count"] == returned_count
    assert body["limit"] == limit
    assert body["order"] == order
    assert body["has_more"] is (total_matching > returned_count)
    captures = body["captures"]
    assert isinstance(captures, list)
    assert len(captures) == returned_count


def _assert_history_409(response: Any) -> None:
    assert response.status_code == 409
    assert response.json() == {"detail": INTEGRITY_SIGNAL}


def _assert_history_openapi(spec: dict[str, Any], path: str) -> None:
    schema = spec["paths"][path]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    ref = schema.get("$ref")
    if isinstance(ref, str):
        schema = spec["components"]["schemas"][ref.rsplit("/", 1)[-1]]
    assert set(schema["required"]) == HISTORY_KEYS
    props = schema["properties"]
    assert set(props) == HISTORY_KEYS
    assert props["total_matching"]["type"] == "integer"
    assert props["returned_count"]["type"] == "integer"
    assert props["limit"]["type"] == "integer"
    assert props["has_more"]["type"] == "boolean"
    assert props["captures"]["type"] == "array"
    assert props["captures"]["items"].get("type") == "object"
    text = json.dumps(schema).lower()
    assert "admitted" in text and "capture" in text
    assert "request_started_at" in text and "capture_id" in text
    assert "pagination" in text
    assert "never measured" in text
    assert "failed" in text
    assert "observation envelope" in text or "observation envelopes" in text
    capture_desc = str(props["captures"].get("description", "")).lower()
    assert "not one universal" in capture_desc or "surface-specific" in capture_desc


def _xmin_snapshot(dsn: str) -> dict[str, list[tuple[object, ...]]]:
    snapshot: dict[str, list[tuple[object, ...]]] = {}
    with connect(dsn) as connection:
        for table in PROVIDER_TABLES:
            rows = connection.execute(f"SELECT xmin::text, * FROM {table}").fetchall()
            snapshot[table] = sorted(
                rows, key=lambda row: tuple(str(item) for item in row[1:])
            )
    return snapshot


def test_fixture_attempt_json_is_unchanged_when_provider_rows_exist(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    fixture = capture_fixture(store, _fixture_inputs())
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
    with _app(store, postgres_dsn) as client:
        response = client.get(f"/v1/attempts/{fixture.attempt_id}")
    body = response.json()
    assert response.status_code == 200
    assert set(body) == {
        "attempt_id",
        "derivation_version_id",
        "attempt_outcome",
        "capture_outcome",
        "observations",
    }
    assert "recipe_resolution" not in body
    assert "adapter_contract" not in body
    assert body["derivation_version_id"] == DEFAULT_VERSION
    assert body["observations"][0]["panel_id"] == "panel-alpha"
    assert body["observations"][0]["score"] == 999


def test_provider_attempt_selected_and_pinned_recipes(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        selected = client.get(f"/v1/attempts/{attempt_id}")
        pinned = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={CORE_RECIPE_ID}"
        )
    assert selected.status_code == 200
    selected_body = selected.json()
    assert selected_body["attempt_id"] == attempt_id
    assert selected_body["provider"] == "dataforseo"
    assert selected_body["adapter_contract"] == store_adapter()
    assert selected_body["derivation_version_id"] == EXTENDED_RECIPE_ID
    assert selected_body["recipe_resolution"] == "selected"
    assert selected_body["attempt_outcome"]["classification"] == "authorized_unresolved"
    assert selected_body["capture_outcome"]["capture_id"] == capture_id
    assert selected_body["capture_outcome"]["observation_count"] == 471
    assert "observations" not in selected_body
    assert "panel_id" not in selected_body
    assert pinned.status_code == 200
    pinned_body = pinned.json()
    assert pinned_body["derivation_version_id"] == CORE_RECIPE_ID
    assert pinned_body["recipe_resolution"] == "pinned"
    assert pinned_body["capture_outcome"]["observation_count"] == 10
    with connect(postgres_dsn) as connection:
        select_provider_recipe(connection, store_adapter(), CORE_RECIPE_ID)
        extended_count = connection.execute(
            """
            SELECT observation_count FROM outcomes
            WHERE attempt_id = %s AND capture_id = %s
              AND derivation_version_id = %s
            """,
            (attempt_id, capture_id, EXTENDED_RECIPE_ID),
        ).fetchone()
    with _app(store, postgres_dsn) as client:
        after = client.get(f"/v1/attempts/{attempt_id}")
    assert after.json()["derivation_version_id"] == CORE_RECIPE_ID
    assert after.json()["capture_outcome"]["observation_count"] == 10
    assert extended_count == (471,)


def test_provider_attempt_http_errors(tmp_path: Path, postgres_dsn: str) -> None:
    store, attempt_id, _capture_id = _prepare_pf03(
        tmp_path, postgres_dsn, extended=False, select=False
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, TEST_RECIPE)
        register_provider_recipe(connection, EXTENDED_RECIPE)
    with _app(store, postgres_dsn) as client:
        missing_selection = client.get(f"/v1/attempts/{attempt_id}")
        unselected_history = _history(client, "ai search optimization")
        unknown = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={'ab' * 32}"
        )
        wrong = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={TEST_RECIPE_ID}"
        )
    assert missing_selection.status_code == 503
    assert missing_selection.json()["detail"] == NOT_SELECTED_SIGNAL
    assert unselected_history.status_code == 503
    assert unselected_history.json()["detail"] == NOT_SELECTED_SIGNAL
    assert unknown.status_code == 404
    assert wrong.status_code == 404
    with connect(postgres_dsn) as connection:
        select_provider_recipe(connection, store_adapter(), CORE_RECIPE_ID)
    with _app(store, postgres_dsn) as client:
        empty = _history(client, "not-a-requested-keyword")
        only_core = _history(
            client, "ai search optimization", derivation_version_id=EXTENDED_RECIPE_ID
        )
    assert empty.status_code == 200
    _assert_history_envelope(empty.json(), total_matching=0, returned_count=0)
    assert empty.json()["captures"] == []
    assert empty.json()["derivation_version_id"] == CORE_RECIPE_ID
    assert only_core.status_code == 200
    _assert_history_envelope(
        only_core.json(),
        total_matching=0,
        returned_count=0,
        limit=20,
    )
    assert only_core.json()["captures"] == []
    assert only_core.json()["derivation_version_id"] == EXTENDED_RECIPE_ID
    assert only_core.json()["observation_kinds"] == [
        COVERAGE_KIND,
        METRICS_KIND,
        MONTHLY_KIND,
        TREND_KIND,
        PROPERTIES_KIND,
        BACKLINKS_KIND,
        INTENT_KIND,
    ]


def test_history_core_and_extended_shapes(tmp_path: Path, postgres_dsn: str) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        extended = _history(client, "ai search optimization")
        core = _history(
            client,
            "ai search optimization",
            derivation_version_id=CORE_RECIPE_ID,
        )
        spec = client.get("/api/v1/openapi.json")
    assert spec.status_code == 200
    assert extended.status_code == 200
    body = extended.json()
    _assert_history_envelope(body, total_matching=1, returned_count=1)
    assert body["provider"] == "dataforseo"
    assert body["adapter_contract"] == store_adapter()
    assert body["requested_keyword"] == "ai search optimization"
    assert body["derivation_version_id"] == EXTENDED_RECIPE_ID
    assert body["recipe_resolution"] == "selected"
    assert body["observation_kinds"] == [
        COVERAGE_KIND,
        METRICS_KIND,
        MONTHLY_KIND,
        TREND_KIND,
        PROPERTIES_KIND,
        BACKLINKS_KIND,
        INTENT_KIND,
    ]
    assert len(body["captures"]) == 1
    group = body["captures"][0]
    assert group["attempt_id"] == attempt_id
    assert group["capture_id"] == capture_id
    assert group["request"] == {
        "location_code": 2840,
        "language_code": "en",
        "include_serp_info": False,
        "include_clickstream_data": False,
    }
    assert group["coverage"]["observation_kind"] == COVERAGE_KIND
    assert group["metrics"]["observation_kind"] == METRICS_KIND
    assert group["capture_outcome"]["observation_count"] == 471
    assert len(group["monthly_search_volume"]) == 85
    assert group["capture_outcome"]["observation_count"] != len(
        group["monthly_search_volume"]
    )
    assert body["total_matching"] != group["capture_outcome"]["observation_count"]
    assert body["total_matching"] != len(group["monthly_search_volume"])
    _assert_history_openapi(spec.json(), HISTORY)
    assert group["search_volume_trend"]["observation_kind"] == TREND_KIND
    assert group["properties"]["observation_kind"] == PROPERTIES_KIND
    assert group["avg_backlinks"]["observation_kind"] == BACKLINKS_KIND
    assert group["search_intent"]["observation_kind"] == INTENT_KIND
    assert "score" not in group
    assert "value" not in group
    core_body = core.json()
    assert core.status_code == 200
    assert core_body["derivation_version_id"] == CORE_RECIPE_ID
    assert core_body["recipe_resolution"] == "pinned"
    assert core_body["observation_kinds"] == [COVERAGE_KIND, METRICS_KIND]
    core_group = core_body["captures"][0]
    assert "monthly_search_volume" not in core_group
    assert "search_volume_trend" not in core_group
    assert "properties" not in core_group
    assert "avg_backlinks" not in core_group
    assert "search_intent" not in core_group
    assert core_group["metrics"] is not None
    assert core_group["capture_outcome"]["observation_count"] == 10


def test_history_ignores_foreign_attempt_outcome_for_same_capture(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    foreign_attempt = "ab" * 32
    assert foreign_attempt != attempt_id
    with connect(postgres_dsn) as connection:
        valid = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE attempt_id = %s AND capture_id = %s
              AND derivation_version_id = %s
            """,
            (attempt_id, capture_id, EXTENDED_RECIPE_ID),
        ).fetchone()
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (foreign_attempt, capture_id, EXTENDED_RECIPE_ID, "provider_error", 0),
        )
    assert valid == ("observation_admitted", 471)
    with _app(store, postgres_dsn) as client:
        response = _history(client, "ai search optimization")
    assert response.status_code == 200
    captures = response.json()["captures"]
    assert [item["capture_id"] for item in captures] == [capture_id]
    assert captures[0]["attempt_id"] == attempt_id
    assert captures[0]["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": 471,
    }
    assert all(item["attempt_id"] != foreign_attempt for item in captures)
    assert all(
        item["capture_outcome"]["classification"] != "provider_error"
        for item in captures
    )


def test_historical_revision_is_visible_through_history_api(
    tmp_path: Path, postgres_dsn: str
) -> None:
    original = _body()
    document = _decoded(original)
    target = next(
        item
        for item in document["tasks"][0]["result"][0]["items"]
        if item["keyword"] == "ai search optimization"
    )
    point = next(
        item
        for item in target["keyword_info"]["monthly_searches"]
        if item["year"] == 2019 and item["month"] == 6
    )
    assert point["search_volume"] == 0
    point["search_volume"] = 7
    store = create_store(tmp_path / "evidence")
    first_attempt, first_capture = _commit_paid(
        store,
        original,
        "31" * 32,
        started="2026-08-16T21:37:01.100000Z",
        authorized_at="2026-08-16T21:37:00.000000Z",
    )
    later_attempt, later_capture = _commit_paid(
        store,
        _encode(document),
        "32" * 32,
        started="2026-08-16T21:38:01.100000Z",
        authorized_at="2026-08-16T21:38:00.000000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
    expected_identity = observation_identity(
        {
            "axes": {
                "requested_keyword": "ai search optimization",
                "year": 2019,
                "month": 6,
            },
            "observation_kind": MONTHLY_KIND,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        EXTENDED_RECIPE,
    )
    with _app(store, postgres_dsn) as client:
        ascending = _history(client, "ai search optimization", order="asc")
        descending = _history(client, "ai search optimization", order="desc", limit=2)
        limited = _history(client, "ai search optimization", order="asc", limit=1)
    assert ascending.status_code == 200
    captures = ascending.json()["captures"]
    assert [item["capture_id"] for item in captures] == [first_capture, later_capture]
    assert [item["attempt_id"] for item in captures] == [first_attempt, later_attempt]
    assert captures[0]["request_started_at"] < captures[1]["request_started_at"]
    first_month = next(
        item
        for item in captures[0]["monthly_search_volume"]
        if item["data_period"] == {"year": 2019, "month": 6}
    )
    later_month = next(
        item
        for item in captures[1]["monthly_search_volume"]
        if item["data_period"] == {"year": 2019, "month": 6}
    )
    assert first_month["search_volume"] == {"state": "stated", "value": 0}
    assert later_month["search_volume"] == {"state": "stated", "value": 7}
    assert first_month["within_capture_identity"] == later_month["within_capture_identity"]
    assert first_month["within_capture_identity"] == expected_identity
    assert first_month["data_period"] != captures[0]["request_started_at"]
    assert descending.json()["captures"][0]["capture_id"] == later_capture
    assert descending.json()["captures"][1]["capture_id"] == first_capture
    assert [item["capture_id"] for item in limited.json()["captures"]] == [first_capture]
    _assert_history_envelope(
        limited.json(), total_matching=2, returned_count=1, limit=1
    )
    _assert_history_envelope(
        descending.json(), total_matching=2, returned_count=2, limit=2, order="desc"
    )
    assert len(limited.json()["captures"][0]["monthly_search_volume"]) == 85


def test_field_states_clocks_and_decimals(tmp_path: Path, postgres_dsn: str) -> None:
    document = _decoded()
    items = document["tasks"][0]["result"][0]["items"]
    seo = next(item for item in items if item["keyword"] == "seo api")
    seo["keyword_info"]["categories"] = []
    ai_item = next(item for item in items if item["keyword"] == "ai search optimization")
    ai_item["keyword_info"]["cpc"] = Decimal("1.234567890123456789")
    omitted = copy.deepcopy(document)
    omitted["tasks"][0]["result"][0]["items"] = [
        item for item in items if item["keyword"] != "local seo"
    ]
    omitted["tasks"][0]["result"][0]["items_count"] = 4
    store = create_store(tmp_path / "states")
    _commit_paid(
        store,
        _encode(document),
        "41" * 32,
        started="2026-08-16T21:37:01.100000Z",
    )
    _commit_paid(
        store,
        _encode(omitted),
        "42" * 32,
        started="2026-08-16T21:37:02.100000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
    with _app(store, postgres_dsn) as client:
        ai = _history(client, "ai search optimization", limit=1, order="asc").json()[
            "captures"
        ][0]
        seo_api = _history(client, "seo api", limit=1, order="asc").json()["captures"][0]
        research = _history(client, "keyword research", limit=1, order="asc").json()[
            "captures"
        ][0]
        local = _history(client, "local seo", order="desc").json()["captures"]
    month = next(
        item
        for item in ai["monthly_search_volume"]
        if item["data_period"] == {"year": 2019, "month": 6}
    )
    assert month["search_volume"] == {"state": "stated", "value": 0}
    assert ai["metrics"]["search_partners"] == {"state": "stated", "value": False}
    assert seo_api["metrics"]["categories"] == {"state": "stated", "value": []}
    assert seo_api["properties"]["core_keyword"] == {"state": "json_null", "value": None}
    absent = local[0]
    assert absent["coverage"]["covered"] is False
    assert absent["coverage"]["returned_keyword"] == {"state": "absent", "value": None}
    assert absent["metrics"] is None
    assert "provider_update_time" not in month
    assert "provider_update_time" not in ai["search_volume_trend"]
    assert "provider_update_time" not in ai["properties"]
    assert ai["metrics"]["provider_update_time"]["value"] == "2026-07-16 07:54:24 +00:00"
    assert ai["avg_backlinks"]["provider_update_time"]["value"] == (
        "2026-08-01 07:28:00 +00:00"
    )
    assert ai["search_intent"]["provider_update_time"]["value"] == (
        "2026-04-29 01:54:23 +00:00"
    )
    assert ai["metrics"]["provider_update_time"] != ai["avg_backlinks"]["provider_update_time"]
    assert ai["metrics"]["provider_update_time"] != ai["search_intent"]["provider_update_time"]
    assert (
        ai["avg_backlinks"]["provider_update_time"]
        != ai["search_intent"]["provider_update_time"]
    )
    assert ai["avg_backlinks"]["backlinks"] == {"state": "stated", "value": "1571.3"}
    assert research["search_intent"]["foreign_intent"]["state"] == "json_null"
    assert ai["metrics"]["cpc"] == {
        "state": "stated",
        "value": "1.234567890123456789",
    }
    assert ai["metrics"]["cpc"]["value"] != str(float("1.234567890123456789"))


def test_provider_damage_returns_409(tmp_path: Path, postgres_dsn: str) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    attempt = store.read_attempt(attempt_id)
    assert attempt is not None
    fingerprint = attempt["request_fingerprint"]
    authorized_at = attempt["authorized_at"]
    assert isinstance(fingerprint, str)
    assert isinstance(authorized_at, str)

    def assert_409(client: TestClient) -> None:
        history = _history(client, "ai search optimization")
        resource = client.get(f"/v1/attempts/{attempt_id}")
        _assert_history_409(history)
        assert resource.status_code == 409
        assert "evidence_integrity_failure" in resource.text
        assert "capture_outcome" not in resource.json()

    body_path = store.capture_path(capture_id) / "response.body"
    payload = bytearray(body_path.read_bytes())
    payload[0] ^= 0x01
    body_path.write_bytes(bytes(payload))
    with _app(store, postgres_dsn) as client:
        assert_409(client)
    body_path.write_bytes(bytes(bytearray(payload[0] ^ 0x01) + payload[1:]))

    manifest = store.capture_path(capture_id) / "capture.json"
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    with _app(store, postgres_dsn) as client:
        assert_409(client)
    manifest.write_bytes(bytes(bytearray(raw[0] ^ 0x01) + raw[1:]))

    attempt_manifest = (
        store.attempt_path(fingerprint, authorized_at, attempt_id) / "attempt.json"
    )
    attempt_raw = bytearray(attempt_manifest.read_bytes())
    attempt_raw[0] ^= 0x01
    attempt_manifest.write_bytes(bytes(attempt_raw))
    with _app(store, postgres_dsn) as client:
        resource = client.get(f"/v1/attempts/{attempt_id}")
        history = _history(client, "ai search optimization")
    assert resource.status_code == 409
    assert "evidence_integrity_failure" in resource.text
    _assert_history_409(history)
    attempt_manifest.write_bytes(bytes(bytearray(attempt_raw[0] ^ 0x01) + attempt_raw[1:]))
    committed = store.attempt_path(fingerprint, authorized_at, attempt_id) / "COMMITTED"
    committed.unlink()
    with _app(store, postgres_dsn) as client:
        missing = client.get(f"/v1/attempts/{attempt_id}")
        missing_history = _history(client, "ai search optimization")
    assert missing.status_code == 409
    assert "evidence_integrity_failure" in missing.text
    _assert_history_409(missing_history)


def test_api_reads_do_not_mutate_provider_state(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, _capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    before_ops = list(store.recorded_ops)
    before_pg = _xmin_snapshot(postgres_dsn)
    with _app(store, postgres_dsn) as client:
        assert client.get(f"/v1/attempts/{attempt_id}").status_code == 200
        assert _history(client, "ai search optimization").status_code == 200
    assert store.recorded_ops == before_ops
    assert _xmin_snapshot(postgres_dsn) == before_pg


def test_two_databases_return_equal_history(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_paid(store, _body(), "51" * 32, started="2026-08-16T21:37:01.100000Z")
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)
    for dsn in (postgres_dsn, postgres_second_dsn):
        with connect(dsn) as connection:
            derive_keyword_overview_extended(store, connection)
            select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
    with (
        _app(store, postgres_dsn) as left,
        _app(store, postgres_second_dsn) as right,
    ):
        left_body = _history(left, "keyword research")
        right_body = _history(right, "keyword research")
    assert left_body.status_code == 200
    assert right_body.status_code == 200
    assert left_body.json() == right_body.json()


def test_selector_isolation_does_not_leak(tmp_path: Path, postgres_dsn: str) -> None:
    store, attempt_id, _capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    other = str(TEST_RECIPE["adapter_contract"])
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, TEST_RECIPE)
        select_provider_recipe(connection, other, TEST_RECIPE_ID)
    with _app(store, postgres_dsn) as client:
        body = client.get(f"/v1/attempts/{attempt_id}").json()
        history = _history(client, "seo api").json()
    assert body["derivation_version_id"] == EXTENDED_RECIPE_ID
    assert history["derivation_version_id"] == EXTENDED_RECIPE_ID
    with connect(postgres_dsn) as connection:
        other_current = connection.execute(
            """
            SELECT derivation_version_id
            FROM provider_recipe_selections
            WHERE adapter_contract = %s
            """,
            (other,),
        ).fetchone()
    assert other_current == (TEST_RECIPE_ID,)


def test_history_excludes_non_admitted_sibling_and_keeps_healthy_capture(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    healthy_attempt, healthy_capture = _commit_paid(
        store, _body(), "61" * 32, started="2026-08-16T21:37:01.100000Z"
    )
    planted_attempt, planted_capture = _commit_paid(
        store, _body(), "62" * 32, started="2026-08-16T21:38:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
        connection.execute(
            """
            UPDATE outcomes
            SET classification = 'provider_error'
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (planted_capture, EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        response = _history(client, "ai search optimization")
    assert response.status_code == 200
    captures = response.json()["captures"]
    _assert_history_envelope(response.json(), total_matching=1, returned_count=1)
    assert [item["capture_id"] for item in captures] == [healthy_capture]
    assert captures[0]["attempt_id"] == healthy_attempt
    assert captures[0]["capture_outcome"]["classification"] == "observation_admitted"
    assert planted_attempt not in {item["attempt_id"] for item in captures}


def test_history_missing_typed_row_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        deleted = connection.execute(
            """
            DELETE FROM keyword_overview_metrics
            WHERE capture_id = %s AND derivation_version_id = %s
              AND requested_keyword = 'seo api'
            RETURNING within_capture_identity
            """,
            (capture_id, EXTENDED_RECIPE_ID),
        ).fetchone()
        assert deleted is not None
    before_ops = list(store.recorded_ops)
    before_pg = _xmin_snapshot(postgres_dsn)
    with _app(store, postgres_dsn) as client:
        missing = _history(client, "keyword research")
        attempt = client.get(f"/v1/attempts/{attempt_id}")
    _assert_history_409(missing)
    assert attempt.status_code == 200
    assert attempt.json()["capture_outcome"]["observation_count"] == 471
    assert store.recorded_ops == before_ops
    assert _xmin_snapshot(postgres_dsn) == before_pg


def test_history_wrong_outcome_count_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = observation_count + 1
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, EXTENDED_RECIPE_ID),
        )
    before_ops = list(store.recorded_ops)
    before_pg = _xmin_snapshot(postgres_dsn)
    with _app(store, postgres_dsn) as client:
        wrong_count = _history(client, "keyword research")
        attempt = client.get(f"/v1/attempts/{attempt_id}")
    assert wrong_count.status_code == 409
    assert wrong_count.json()["detail"] == INTEGRITY_SIGNAL
    assert attempt.status_code == 200
    assert attempt.json()["capture_outcome"]["observation_count"] == 472
    assert store.recorded_ops == before_ops
    assert _xmin_snapshot(postgres_dsn) == before_pg


def test_history_consistency_damage_outside_limit_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_paid(store, _body(), "81" * 32, started="2026-08-16T21:37:01.100000Z")
    later_attempt, later_capture = _commit_paid(
        store, _body(), "82" * 32, started="2026-08-16T21:38:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
        connection.execute(
            """
            DELETE FROM keyword_overview_metrics
            WHERE capture_id = %s AND derivation_version_id = %s
              AND requested_keyword = 'seo api'
            """,
            (later_capture, EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        limited = _history(client, "keyword research", limit=1, order="asc")
        later = client.get(f"/v1/attempts/{later_attempt}")
    _assert_history_409(limited)
    assert later.status_code == 200


def _assert_ko_item(item: dict[str, object], *, attempt_id: str) -> None:
    assert set(item) == OUTCOME_ITEM_KEYS
    assert item["attempt_id"] == attempt_id
    assert item["provider"] == "dataforseo"
    assert item["adapter_contract"] == store_adapter()
    request = item["request"]
    assert isinstance(request, dict)
    assert set(request) == KO_REQUEST_KEYS
    assert request["keywords"] == list(KEYWORDS)
    assert "contract" not in request
    assert item["attempt_outcome"] == {
        "classification": "authorized_unresolved",
        "observation_count": 0,
    }


def test_keyword_overview_outcomes_empty_unresolved_admitted_and_grain(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        empty = _outcomes(client, "not-a-member")
        member = _outcomes(client, "seo api")
        other = _outcomes(client, "keyword research")
        missing_query = client.get(OUTCOMES)
        spec = client.get("/api/v1/openapi.json").json()
    assert empty.status_code == 200
    _assert_outcomes_envelope(empty.json(), total_matching=0, returned_count=0)
    assert member.status_code == 200
    body = member.json()
    _assert_outcomes_envelope(body, total_matching=1, returned_count=1)
    item = body["outcomes"][0]
    _assert_ko_item(item, attempt_id=attempt_id)
    assert item["capture_id"] == capture_id
    assert item["transport_state"] == "response_complete"
    assert item["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": 471,
    }
    assert other.json()["outcomes"][0]["attempt_id"] == attempt_id
    assert missing_query.status_code == 422
    schema = spec["paths"][OUTCOMES]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    ref = schema.get("$ref")
    if isinstance(ref, str):
        schema = spec["components"]["schemas"][ref.rsplit("/", 1)[-1]]
    assert set(schema["required"]) == OUTCOMES_KEYS
    text = json.dumps(spec).lower()
    assert "one attempt" in text or "one verified attempt" in text
    assert "authorized_unresolved" in text
    assert "not definitely unsent" in text
    assert "pagination" in text
    assert "observation envelope" in text or "observation-envelope" in text
    assert "unreadable" in text or "same root" in text
    enums = spec["components"]["schemas"]["CaptureOutcomeView"]["properties"][
        "classification"
    ]["enum"]
    assert set(enums) == {
        "no_response",
        "response_partial",
        "transport_complete_non_admissible",
        "provider_envelope_rejected",
        "provider_error",
        "reconciliation_failed",
        "observation_admitted",
        "observation_admitted_empty",
    }


def test_keyword_overview_outcomes_unresolved_and_no_response(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    unresolved_id = _commit_paid_attempt_only(
        store, "a1" * 32, authorized_at="2026-08-16T21:36:00.000000Z"
    )
    failed_id, failed_capture = _commit_paid_no_response(
        store,
        "a2" * 32,
        started="2026-08-16T21:37:01.100000Z",
        authorized_at="2026-08-16T21:37:00.000000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
    with _app(store, postgres_dsn) as client:
        response = _outcomes(client, "local seo", order="asc")
    assert response.status_code == 200
    body = response.json()
    _assert_outcomes_envelope(body, total_matching=2, returned_count=2, order="asc")
    first, second = body["outcomes"]
    assert first["attempt_id"] == unresolved_id
    assert first["capture_id"] is None
    assert first["request_started_at"] is None
    assert first["transport_ended_at"] is None
    assert first["transport_state"] is None
    assert first["capture_outcome"] is None
    assert second["attempt_id"] == failed_id
    assert second["capture_id"] == failed_capture
    assert second["capture_outcome"] == {
        "classification": "no_response",
        "observation_count": 0,
    }


def test_keyword_overview_outcomes_limit_order_and_admitted_empty(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    first_id, first_capture = _commit_paid(
        store,
        _body(),
        "b1" * 32,
        started="2026-08-16T21:37:01.100000Z",
        authorized_at="2026-08-16T21:37:00.000000Z",
    )
    second_id, second_capture = _commit_paid_no_response(
        store,
        "b2" * 32,
        started="2026-08-16T21:38:01.100000Z",
        authorized_at="2026-08-16T21:38:00.000000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
        connection.execute(
            """
            UPDATE outcomes
            SET classification = 'observation_admitted_empty', observation_count = 0
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (second_capture, EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        limited = _outcomes(client, "seo api", limit=1, order="asc")
        descending = _outcomes(client, "seo api", order="desc")
    assert limited.status_code == 200
    _assert_outcomes_envelope(
        limited.json(), total_matching=2, returned_count=1, limit=1
    )
    assert limited.json()["outcomes"][0]["attempt_id"] == first_id
    assert limited.json()["outcomes"][0]["capture_id"] == first_capture
    assert descending.status_code == 200
    ids = [item["attempt_id"] for item in descending.json()["outcomes"]]
    assert ids == [second_id, first_id]
    assert descending.json()["outcomes"][0]["capture_outcome"] == {
        "classification": "observation_admitted_empty",
        "observation_count": 0,
    }


def test_keyword_overview_outcomes_integrity_and_foreign_damage(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    fixture = capture_fixture(store, _fixture_inputs())
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
    with _app(store, postgres_dsn) as client:
        healthy = _outcomes(client, "seo api")
        history = _history(client, "seo api")
    assert healthy.status_code == 200
    assert history.status_code == 200

    manifest = store.capture_path(fixture.capture_id) / "capture.json"
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    with _app(store, postgres_dsn) as client:
        damaged = _outcomes(client, "seo api")
        history_after = _history(client, "seo api")
    _assert_outcomes_409(damaged)
    assert history_after.status_code == 200
    manifest.write_bytes(bytes(bytearray(raw[0] ^ 0x01) + raw[1:]))

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = observation_count + 1
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        stale = _outcomes(client, "seo api")
        audit = client.get(f"/v1/attempts/{attempt_id}")
    _assert_outcomes_409(stale)
    assert audit.status_code == 200
    assert audit.json()["capture_outcome"]["observation_count"] == 472


def test_keyword_overview_outcomes_missing_rows_two_captures_and_zero_admitted(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    first_id, first_capture = _commit_paid(
        store,
        _body(),
        "c1" * 32,
        started="2026-08-16T21:37:01.100000Z",
        authorized_at="2026-08-16T21:37:00.000000Z",
    )
    second_id, second_capture = _commit_paid(
        store,
        _body(),
        "c2" * 32,
        started="2026-08-16T21:38:01.100000Z",
        authorized_at="2026-08-16T21:38:00.000000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
        connection.execute(
            """
            DELETE FROM outcomes
            WHERE attempt_id = %s AND capture_id IS NULL
              AND derivation_version_id = %s
            """,
            (second_id, EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        partial = _outcomes(client, "seo api", limit=1, order="asc")
    _assert_outcomes_409(partial)

    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, CORE_RECIPE)
        select_provider_recipe(connection, store_adapter(), CORE_RECIPE_ID)
        connection.execute(
            "DELETE FROM outcomes WHERE derivation_version_id = %s",
            (CORE_RECIPE_ID,),
        )
    with _app(store, postgres_dsn) as client:
        missing_all = _outcomes(client, "seo api")
    _assert_outcomes_409(missing_all)

    with connect(postgres_dsn) as connection:
        select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, NULL, %s, 'authorized_unresolved', 0)
            """,
            (second_id, EXTENDED_RECIPE_ID),
        )
        connection.execute(
            """
            UPDATE outcomes
            SET classification = 'observation_admitted', observation_count = 0
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (second_capture, EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        zero_admitted = _outcomes(client, "seo api")
    _assert_outcomes_409(zero_admitted)

    store2 = create_store(tmp_path / "two-captures")
    attempt_id, capture_id = _commit_paid(
        store2, _body(), "d1" * 32, started="2026-08-16T21:37:01.100000Z"
    )
    committed = store2.capture_path(capture_id) / "COMMITTED"
    hidden = committed.with_name("COMMITTED.hidden")
    committed.rename(hidden)
    attempt = store2.read_attempt(attempt_id)
    assert attempt is not None
    store2.commit_capture(
        paid_http_capture_document(
            attempt=attempt,
            request_started_at="2026-08-16T21:37:02.100000Z",
            transport_ended_at="2026-08-16T21:37:02.400000Z",
            transport_state="no_response",
            response=None,
            transport_failure={"phase": "connect", "code": "timeout"},
            response_headers_at=None,
            response_body_ended_at=None,
        ),
        response_body=None,
    )
    hidden.rename(committed)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store2, connection)
        select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
    with _app(store2, postgres_dsn) as client:
        two = _outcomes(client, "seo api")
        no_capture_stage = client.get(
            OUTCOMES + "?requested_keyword=seo api"
        )
    _assert_outcomes_409(two)
    _assert_outcomes_409(no_capture_stage)


def test_keyword_overview_outcomes_missing_capture_stage_is_not_unresolved(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            DELETE FROM outcomes
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, EXTENDED_RECIPE_ID),
        )
    before_ops = list(store.recorded_ops)
    before_pg = _xmin_snapshot(postgres_dsn)
    with _app(store, postgres_dsn) as client:
        response = _outcomes(client, "seo api")
        history = _history(client, "seo api")
    _assert_outcomes_409(response)
    assert history.status_code == 200
    assert history.json()["captures"] == []
    assert store.recorded_ops == before_ops
    assert _xmin_snapshot(postgres_dsn) == before_pg
    assert attempt_id
    assert "captures" not in response.json()


def test_keyword_overview_outcomes_does_not_mutate(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    before_ops = list(store.recorded_ops)
    before_pg = _xmin_snapshot(postgres_dsn)
    with _app(store, postgres_dsn) as client:
        assert _outcomes(client, "seo api").status_code == 200
        assert _history(client, "seo api").status_code == 200
    assert store.recorded_ops == before_ops
    assert _xmin_snapshot(postgres_dsn) == before_pg


def _damage_attempt_manifest(store: EvidenceStore, attempt_id: str) -> None:
    attempt = store.read_attempt(attempt_id)
    assert attempt is not None
    fingerprint = attempt["request_fingerprint"]
    authorized_at = attempt["authorized_at"]
    assert isinstance(fingerprint, str)
    assert isinstance(authorized_at, str)
    path = store.attempt_path(fingerprint, authorized_at, attempt_id) / "attempt.json"
    raw = bytearray(path.read_bytes())
    raw[0] ^= 0x01
    path.write_bytes(bytes(raw))


def test_keyword_overview_outcomes_tie_break_and_remediation_409s(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "tie")
    authorized = "2026-08-16T21:37:00.000000Z"
    first = _commit_paid_attempt_only(store, "aa" * 32, authorized_at=authorized)
    second = _commit_paid_attempt_only(store, "bb" * 32, authorized_at=authorized)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
    expected = sorted((first, second))
    with _app(store, postgres_dsn) as client:
        ascending = _outcomes(client, "seo api", order="asc")
        descending = _outcomes(client, "seo api", order="desc", limit=1)
    assert ascending.status_code == 200
    assert [item["attempt_id"] for item in ascending.json()["outcomes"]] == expected
    assert descending.status_code == 200
    _assert_outcomes_envelope(
        descending.json(), total_matching=2, returned_count=1, limit=1, order="desc"
    )
    assert descending.json()["outcomes"][0]["attempt_id"] == expected[-1]

    fixture = capture_fixture(store, _fixture_inputs())
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
    _damage_attempt_manifest(store, fixture.attempt_id)
    with _app(store, postgres_dsn) as client:
        foreign_attempt = _outcomes(client, "seo api")
    _assert_outcomes_409(foreign_attempt)


def test_keyword_overview_outcomes_recipe_identity_and_envelope_provenance(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        stored = connection.execute(
            """
            SELECT recipe_canonical_bytes
            FROM provider_recipes
            WHERE derivation_version_id = %s
            """,
            (EXTENDED_RECIPE_ID,),
        ).fetchone()
        assert stored is not None
        original = bytes(stored[0])
        connection.execute(
            """
            UPDATE provider_recipes
            SET provider = 'acme'
            WHERE derivation_version_id = %s
            """,
            (EXTENDED_RECIPE_ID,),
        )
    with _app(store, postgres_dsn) as client:
        wrong_provider = _outcomes(client, "not-a-member")
    _assert_outcomes_409(wrong_provider)

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE provider_recipes
            SET provider = 'dataforseo', recipe_canonical_bytes = %s
            WHERE derivation_version_id = %s
            """,
            (b"{", EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        bad_json = _outcomes(client, "not-a-member")
    _assert_outcomes_409(bad_json)

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE provider_recipes
            SET recipe_canonical_bytes = %s
            WHERE derivation_version_id = %s
            """,
            (b"\xff\xfe", EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        bad_utf8 = _outcomes(client, "not-a-member")
    _assert_outcomes_409(bad_utf8)

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE provider_recipes
            SET recipe_canonical_bytes = %s
            WHERE derivation_version_id = %s
            """,
            (original[:1] + b" " + original[1:], EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        non_jcs = _outcomes(client, "not-a-member")
    _assert_outcomes_409(non_jcs)

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE provider_recipes
            SET recipe_canonical_bytes = %s
            WHERE derivation_version_id = %s
            """,
            (recipe_bytes(CORE_RECIPE), EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        digest = _outcomes(client, "not-a-member")
    _assert_outcomes_409(digest)

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE provider_recipes
            SET recipe_canonical_bytes = %s
            WHERE derivation_version_id = %s
            """,
            (original, EXTENDED_RECIPE_ID),
        )
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, 'no_response', 0)
            """,
            (attempt_id, "ab" * 32, EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        extra_stage = _outcomes(client, "seo api")
    _assert_outcomes_409(extra_stage)

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            DELETE FROM outcomes
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            ("ab" * 32, EXTENDED_RECIPE_ID),
        )
    store_rel = create_store(tmp_path / "wrong-capture")
    _rel_attempt, rel_capture = _commit_paid_no_response(
        store_rel,
        "e1" * 32,
        started="2026-08-16T21:39:01.100000Z",
        authorized_at="2026-08-16T21:39:00.000000Z",
    )
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store_rel, connection)
        connection.execute(
            """
            UPDATE outcomes
            SET capture_id = %s
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            ("dd" * 32, rel_capture, EXTENDED_RECIPE_ID),
        )
    with _app(store_rel, postgres_dsn) as client:
        wrong_capture = _outcomes(client, "seo api")
    _assert_outcomes_409(wrong_capture)

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE observation_envelopes
            SET attempt_id = %s
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            ("aa" * 32, capture_id, EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        envelope_attempt = _outcomes(client, "seo api")
    _assert_outcomes_409(envelope_attempt)

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE observation_envelopes
            SET attempt_id = %s, provider = 'acme'
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (attempt_id, capture_id, EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        envelope_provider = _outcomes(client, "seo api")
    _assert_outcomes_409(envelope_provider)

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE observation_envelopes
            SET provider = 'dataforseo', adapter_contract = 'other-adapter-v1'
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        envelope_adapter = _outcomes(client, "seo api")
    _assert_outcomes_409(envelope_adapter)

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE observation_envelopes
            SET adapter_contract = %s
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (store_adapter(), capture_id, EXTENDED_RECIPE_ID),
        )
        connection.execute(
            """
            INSERT INTO observation_envelopes (
                capture_id, attempt_id, derivation_version_id, provider,
                adapter_contract, observation_kind, within_capture_identity
            )
            VALUES (%s, %s, %s, 'dataforseo', %s, 'not.a.declared.kind.v1', %s)
            """,
            (capture_id, attempt_id, EXTENDED_RECIPE_ID, store_adapter(), "cc" * 32),
        )
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = observation_count + 1
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        envelope_kind = _outcomes(client, "seo api")
    _assert_outcomes_409(envelope_kind)

    _damage_attempt_manifest(store, attempt_id)
    with _app(store, postgres_dsn) as client:
        drifted = _outcomes(client, "seo api")
    _assert_outcomes_409(drifted)


def _resolve_openapi_schema(spec: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    ref = schema.get("$ref")
    if isinstance(ref, str):
        resolved = spec["components"]["schemas"][ref.rsplit("/", 1)[-1]]
        assert isinstance(resolved, dict)
        return resolved
    return schema


def _holdings_route_schemas(
    spec: dict[str, Any], path: str
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    operation = spec["paths"][path]["get"]
    names: set[str] = set()
    for item in operation.get("parameters") or []:
        parameter = item
        ref = item.get("$ref") if isinstance(item, dict) else None
        if isinstance(ref, str):
            parameter = spec["components"]["parameters"][ref.rsplit("/", 1)[-1]]
        if isinstance(parameter, dict) and parameter.get("in") == "query":
            names.add(str(parameter["name"]))
    assert names == {"limit", "order"}
    response = operation["responses"]["200"]["content"]["application/json"]["schema"]
    envelope = _resolve_openapi_schema(spec, response)
    assert set(envelope["required"]) == HOLDINGS_KEYS
    item_schema = _resolve_openapi_schema(spec, envelope["properties"]["holdings"]["items"])
    assert set(item_schema["required"]) == HOLDINGS_ITEM_KEYS
    request_schema = _resolve_openapi_schema(spec, item_schema["properties"]["request"])
    return envelope, item_schema, request_schema


def _assert_holdings_count_time_schema(
    envelope: dict[str, Any], item_schema: dict[str, Any]
) -> None:
    env_props = envelope["properties"]
    assert env_props["total_matching"]["minimum"] == 0
    assert env_props["returned_count"]["minimum"] == 0
    assert env_props["limit"]["minimum"] == 1
    assert env_props["limit"]["maximum"] == 100
    item_props = item_schema["properties"]
    assert item_props["attempt_count"]["minimum"] == 1
    assert item_props["capture_count"]["minimum"] == 0
    assert item_props["unresolved_count"]["minimum"] == 0
    attempt_text = str(item_props["attempt_count"].get("description", "")).lower()
    capture_text = str(item_props["capture_count"].get("description", "")).lower()
    assert "attempt" in attempt_text and "capture" in attempt_text
    assert "observation" in attempt_text or "observation" in capture_text
    assert "rank" in attempt_text or "mention" in attempt_text or "rank" in capture_text
    assert "minimum" in str(item_props["first_authorized_at"].get("description", "")).lower()
    assert "maximum" in str(item_props["last_authorized_at"].get("description", "")).lower()
    started = str(item_props["first_request_started_at"].get("description", "")).lower()
    assert "null" in started and "capture_count" in started
    unresolved = str(item_props["unresolved_count"].get("description", "")).lower()
    assert "not definitely unsent" in unresolved
    empty = str(env_props["total_matching"].get("description", "")).lower()
    assert "unselected" in empty or "recipe" in empty
    has_more = str(env_props["has_more"].get("description", "")).lower()
    assert "pagination" in has_more or "unavailable" in has_more
    strategy = json.dumps({"envelope": envelope, "item": item_schema}).lower()
    assert "recommendation" in strategy or "cadence" in strategy or "strategy" in strategy


def test_keyword_overview_holdings_empty_closed_query_and_openapi(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path / "empty")
    with _holdings_app(store) as client:
        empty = _holdings(client)
        extra_keyword = _holdings(client, requested_keyword="seo api")
        extra_pin = _holdings(client, derivation_version_id="ab" * 32)
        extra_offset = _holdings(client, offset=0)
        extra_cursor = _holdings(client, cursor="next")
        bad_limit = _holdings(client, limit=0)
        high_limit = _holdings(client, limit=101)
        bad_order = _holdings(client, order="sideways")
        spec = client.get("/api/v1/openapi.json").json()
    assert empty.status_code == 200
    _assert_holdings_envelope(empty.json(), total_matching=0, returned_count=0)
    assert empty.json()["holdings"] == []
    for response in (
        extra_keyword,
        extra_pin,
        extra_offset,
        extra_cursor,
        bad_limit,
        high_limit,
        bad_order,
    ):
        assert response.status_code == 422
        assert "holdings" not in response.json()
    envelope, item_schema, request_schema = _holdings_route_schemas(spec, HOLDINGS)
    _assert_holdings_count_time_schema(envelope, item_schema)
    assert set(request_schema["required"]) == KO_REQUEST_KEYS
    expansion = json.dumps({"item": item_schema, "request": request_schema}).lower()
    assert "independent exchanges" in expansion or "n measurements" in expansion
    grain = str(item_schema["properties"]["requested_keyword"].get("description", "")).lower()
    assert (
        "exact requested subject" in grain
        or "subject-plus" in grain
        or "not one attempt" in grain
    )


def test_keyword_overview_holdings_inventory_grouping_and_expansion(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path / "inventory")
    unresolved = _commit_paid_attempt_only(
        store, "a1" * 32, authorized_at="2026-08-16T21:36:00.000000Z", keywords=("seo api",)
    )
    captured_id, _capture_id = _commit_paid_no_response(
        store,
        "a2" * 32,
        started="2026-08-16T21:37:01.100000Z",
        authorized_at="2026-08-16T21:37:00.000000Z",
        keywords=("seo api",),
    )
    later = _commit_paid_attempt_only(
        store, "a3" * 32, authorized_at="2026-08-16T21:38:00.000000Z", keywords=("seo api",)
    )
    five = _commit_paid_attempt_only(
        store, "a4" * 32, authorized_at="2026-08-16T21:39:00.000000Z", keywords=KEYWORDS
    )
    solo = _commit_paid_attempt_only(
        store,
        "a5" * 32,
        authorized_at="2026-08-16T21:40:00.000000Z",
        keywords=("apple one", "banana two"),
    )
    later_solo = _commit_paid_attempt_only(
        store,
        "a6" * 32,
        authorized_at="2026-08-16T21:41:00.000000Z",
        keywords=("apple one", "cherry three"),
    )
    assert unresolved
    assert captured_id
    assert later
    assert five
    assert solo
    assert later_solo
    with _holdings_app(store) as client:
        response = _holdings(client, order="asc")
        limited = _holdings(client, limit=1, order="desc")
    assert response.status_code == 200
    body = response.json()
    items = body["holdings"]
    assert isinstance(items, list)
    by_subject = {item["requested_keyword"]: item for item in items}
    seo = [item for item in items if item["requested_keyword"] == "seo api"]
    assert len(seo) == 2
    grouped = next(item for item in seo if item["request"]["keywords"] == ["seo api"])
    expanded = next(item for item in seo if item["request"]["keywords"] == list(KEYWORDS))
    _assert_holdings_item(grouped)
    _assert_holdings_item(expanded)
    assert grouped["attempt_count"] == 3
    assert grouped["capture_count"] == 1
    assert grouped["unresolved_count"] == 2
    assert grouped["first_authorized_at"] == "2026-08-16T21:36:00.000000Z"
    assert grouped["last_authorized_at"] == "2026-08-16T21:38:00.000000Z"
    assert grouped["first_request_started_at"] == "2026-08-16T21:37:01.100000Z"
    assert grouped["last_request_started_at"] == "2026-08-16T21:37:01.100000Z"
    members = [item for item in items if item["request"]["keywords"] == list(KEYWORDS)]
    assert len(members) == 5
    assert {item["requested_keyword"] for item in members} == set(KEYWORDS)
    for item in members:
        _assert_holdings_item(item)
        assert item["request"]["keywords"] == list(KEYWORDS)
        assert item["attempt_count"] == 1
        assert item["capture_count"] == 0
        assert item["unresolved_count"] == 1
        assert item["first_authorized_at"] == "2026-08-16T21:39:00.000000Z"
        assert item["last_authorized_at"] == "2026-08-16T21:39:00.000000Z"
        assert item["first_request_started_at"] is None
        assert item["last_request_started_at"] is None
    apple = [
        item
        for item in items
        if item["requested_keyword"] == "apple one"
    ]
    assert [item["request"]["keywords"] for item in apple] == [
        ["apple one", "banana two"],
        ["apple one", "cherry three"],
    ]
    keys = [
        (
            item["requested_keyword"],
            tuple(item["request"]["keywords"]),
            item["request"]["location_code"],
            item["request"]["language_code"],
            item["request"]["include_serp_info"],
            item["request"]["include_clickstream_data"],
        )
        for item in items
    ]
    assert keys == sorted(keys)
    _assert_holdings_envelope(
        body, total_matching=len(items), returned_count=len(items)
    )
    assert limited.status_code == 200
    _assert_holdings_envelope(
        limited.json(),
        total_matching=len(items),
        returned_count=1,
        limit=1,
        order="desc",
    )
    assert limited.json()["holdings"][0]["requested_keyword"] == items[-1]["requested_keyword"]
    assert limited.json()["holdings"][0]["request"]["keywords"] == items[-1]["request"]["keywords"]
    assert by_subject


def test_keyword_overview_holdings_tail_beyond_100_and_dsn_independence(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "tail")
    for index in range(101):
        _commit_paid_attempt_only(
            store,
            format(index, "x").zfill(64),
            authorized_at="2026-08-16T21:37:00.000000Z",
            keywords=(f"hold{index:03d}",),
        )
    apply_migrations(postgres_dsn)
    with _holdings_app(store) as unset:
        capped = _holdings(unset, limit=100)
    assert capped.status_code == 200
    _assert_holdings_envelope(
        capped.json(), total_matching=101, returned_count=100, limit=100
    )
    assert capped.json()["has_more"] is True
    unreachable = "postgresql://127.0.0.1:1/observatory_holdings_missing"
    with _holdings_app(store, unreachable) as down:
        still = _holdings(down, limit=100)
    assert still.status_code == 200
    assert still.json()["total_matching"] == 101
    store_pf03, _attempt_id, _capture_id = _prepare_pf03(tmp_path / "pf03", postgres_dsn)
    before_ops = list(store_pf03.recorded_ops)
    before_pg = _xmin_snapshot(postgres_dsn)
    with _holdings_app(store_pf03) as client:
        derived = _holdings(client)
        extra_pin = _holdings(client, derivation_version_id=EXTENDED_RECIPE_ID)
    assert derived.status_code == 200
    assert extra_pin.status_code == 422
    assert derived.json()["total_matching"] == 5
    assert store_pf03.recorded_ops == before_ops
    assert _xmin_snapshot(postgres_dsn) == before_pg


def test_keyword_overview_holdings_integrity_vectors(tmp_path: Path) -> None:
    store = create_store(tmp_path / "integrity")
    _commit_paid_attempt_only(
        store, "b1" * 32, authorized_at="2026-08-16T21:37:00.000000Z", keywords=("seo api",)
    )
    fixture = capture_fixture(store, _fixture_inputs())
    _damage_attempt_manifest(store, fixture.attempt_id)
    with _holdings_app(store) as client:
        foreign = _holdings(client, limit=1)
    _assert_holdings_409(foreign)

    store_ok = create_store(tmp_path / "ok")
    attempt_id = _commit_paid_attempt_only(
        store_ok, "b2" * 32, authorized_at="2026-08-16T21:37:00.000000Z", keywords=("seo api",)
    )
    wrong = _OverrideAttemptStore(
        store_ok, lambda document, _id: {**document, "provider": "acme"}
    )
    with _holdings_app(wrong) as client:
        wrong_provider = _holdings(client)
    _assert_holdings_409(wrong_provider)

    def _empty_keywords(document: dict[str, object], _id: str) -> dict[str, object]:
        raw = document["parameters"]
        assert isinstance(raw, Mapping)
        return {**document, "parameters": {**dict(raw), "keywords": []}}

    malformed = _OverrideAttemptStore(store_ok, _empty_keywords)
    with _holdings_app(malformed) as client:
        bad_params = _holdings(client)
    _assert_holdings_409(bad_params)

    def _drop_flag(document: dict[str, object], _id: str) -> dict[str, object]:
        raw = document["parameters"]
        assert isinstance(raw, Mapping)
        parameters = dict(raw)
        del parameters["include_serp_info"]
        return {**document, "parameters": parameters}

    missing_flag = _OverrideAttemptStore(store_ok, _drop_flag)
    with _holdings_app(missing_flag) as client:
        _assert_holdings_409(_holdings(client))

    missing_time = _OverrideAttemptStore(
        store_ok, lambda document, _id: {**document, "authorized_at": ""}
    )
    with _holdings_app(missing_time) as client:
        no_time = _holdings(client)
    _assert_holdings_409(no_time)

    stored = store_ok.read_attempt(attempt_id)
    assert stored is not None
    copied = store_ok.attempt_path(
        str(stored["request_fingerprint"]),
        "2026-08-16T21:37:00.000000Z",
        attempt_id,
    )
    shutil.copytree(
        copied,
        store_ok.root
        / "attempts"
        / "v1"
        / "ff"
        / "ff"
        / ("ff" * 32)
        / "2026"
        / "08"
        / "16"
        / attempt_id,
    )
    with _holdings_app(store_ok) as client:
        duplicate = _holdings(client, limit=1)
    _assert_holdings_409(duplicate)

    two = create_store(tmp_path / "two")
    two_attempt, two_capture = _commit_paid_no_response(
        two,
        "c1" * 32,
        started="2026-08-16T21:37:01.100000Z",
        authorized_at="2026-08-16T21:37:00.000000Z",
        keywords=("seo api",),
    )
    committed = two.capture_path(two_capture) / "COMMITTED"
    hidden = committed.with_name("COMMITTED.hidden")
    committed.rename(hidden)
    parent = two.read_attempt(two_attempt)
    assert parent is not None
    two.commit_capture(
        paid_http_capture_document(
            attempt=parent,
            request_started_at="2026-08-16T21:37:02.100000Z",
            transport_ended_at="2026-08-16T21:37:02.400000Z",
            transport_state="no_response",
            response=None,
            transport_failure={"phase": "connect", "code": "timeout"},
            response_headers_at=None,
            response_body_ended_at=None,
        ),
        response_body=None,
    )
    hidden.rename(committed)
    with _holdings_app(two) as client:
        two_caps = _holdings(client, limit=1)
    _assert_holdings_409(two_caps)

    parent_store = create_store(tmp_path / "parent")
    _parent_attempt, parent_capture = _commit_paid_no_response(
        parent_store,
        "d1" * 32,
        started="2026-08-16T21:37:01.100000Z",
        authorized_at="2026-08-16T21:37:00.000000Z",
        keywords=("seo api",),
    )
    capture_manifest = parent_store.capture_path(parent_capture) / "capture.json"
    raw = bytearray(capture_manifest.read_bytes())
    raw[0] ^= 0x01
    capture_manifest.write_bytes(bytes(raw))
    with _holdings_app(parent_store) as client:
        parent_damage = _holdings(client, limit=1)
    _assert_holdings_409(parent_damage)

    missing_parent = create_store(tmp_path / "missing-parent")
    missing_attempt, missing_capture = _commit_paid_no_response(
        missing_parent,
        "e1" * 32,
        started="2026-08-16T21:37:01.100000Z",
        authorized_at="2026-08-16T21:37:00.000000Z",
        keywords=("seo api",),
    )
    parent_doc = missing_parent.read_attempt(missing_attempt)
    assert parent_doc is not None
    committed_attempt = (
        missing_parent.attempt_path(
            str(parent_doc["request_fingerprint"]),
            "2026-08-16T21:37:00.000000Z",
            missing_attempt,
        )
        / "COMMITTED"
    )
    committed_attempt.rename(committed_attempt.with_name("COMMITTED.hidden"))
    with _holdings_app(missing_parent) as client:
        _assert_holdings_409(_holdings(client, limit=1))
    assert missing_capture


def test_holdings_foreign_capture_and_parent_agreement_on_all_routes(
    tmp_path: Path,
) -> None:
    damaged = create_store(tmp_path / "foreign")
    _commit_paid_attempt_only(
        damaged, "f1" * 32, authorized_at="2026-08-16T21:37:00.000000Z", keywords=("seo api",)
    )
    fixture = capture_fixture(damaged, _fixture_inputs())
    capture_path = damaged.capture_path(fixture.capture_id) / "capture.json"
    payload = bytearray(capture_path.read_bytes())
    payload[0] ^= 0x01
    capture_path.write_bytes(bytes(payload))
    with pytest.raises(IntegrityError):
        damaged.read_capture(fixture.capture_id)
    with _holdings_app(damaged) as client:
        for path in (HOLDINGS, ORGANIC_HOLDINGS, MENTIONS_HOLDINGS):
            _assert_holdings_409(client.get(path))

    parented = create_store(tmp_path / "parent-disagree")
    ko_attempt = _commit_paid_attempt_only(
        parented, "f2" * 32, authorized_at="2026-08-16T21:37:00.000000Z", keywords=("seo api",)
    )
    fixture_ok = capture_fixture(parented, _fixture_inputs())
    planted_id = _plant_retargeted_capture(
        parented, fixture_ok.capture_id, ko_attempt
    )
    with pytest.raises(IntegrityError, match="does not agree with its parent Attempt"):
        parented.read_capture(planted_id)
    with _holdings_app(parented) as client:
        for path in (HOLDINGS, ORGANIC_HOLDINGS, MENTIONS_HOLDINGS):
            _assert_holdings_409(client.get(path))
