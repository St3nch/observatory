"""AI-06: Search Mentions Attempt dispatch and history API."""

from __future__ import annotations

import copy
import json
import secrets
import shutil
import socket
import uuid
from collections.abc import Callable, Mapping
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlencode

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from observatory.api import create_app
from observatory.capture import FixtureCaptureInputs, capture_fixture
from observatory.capture_event import (
    MENTIONS_ADAPTER_CONTRACT,
    ORGANIC_ADAPTER_CONTRACT,
    PAID_ADAPTER_CONTRACT,
    body_ref,
    http_attempt_document,
    mentions_http_attempt_document,
    mentions_http_capture_document,
    organic_http_attempt_document,
    organic_http_capture_document,
    paid_http_attempt_document,
    paid_http_capture_document,
)
from observatory.dataforseo_ai_optimization_search_mentions import (
    ITEM_KIND,
    MONTHLY_KIND,
    SEARCH_MENTIONS_RECIPE,
    SEARCH_MENTIONS_RECIPE_ID,
    SOURCE_KIND,
)
from observatory.dataforseo_ai_optimization_search_mentions_paid_probe import (
    closed_mentions_parameters,
    mentions_request_body_bytes,
)
from observatory.dataforseo_google_organic import GOOGLE_ORGANIC_RECIPE, GOOGLE_ORGANIC_RECIPE_ID
from observatory.dataforseo_google_organic_paid_probe import (
    closed_organic_parameters,
    organic_request_body_bytes,
)
from observatory.dataforseo_keyword_overview import CORE_RECIPE, CORE_RECIPE_ID, EXTENDED_RECIPE_ID
from observatory.dataforseo_paid_probe import closed_paid_parameters, paid_request_body_bytes
from observatory.dataforseo_sandbox import closed_sandbox_parameters, request_body_bytes
from observatory.derive import DEFAULT_VERSION, derive
from observatory.evidence_store import EvidenceStore, create_store
from observatory.google_organic_derive import derive_google_organic
from observatory.keyword_overview_derive import derive_keyword_overview_extended
from observatory.migrate import apply_migrations, connect
from observatory.provider_recipe import (
    TEST_RECIPE,
    TEST_RECIPE_ID,
    ObservationEnvelope,
    register_provider_recipe,
    validate_recipe,
    write_observation_envelope,
)
from observatory.provider_recipe_selection import NOT_SELECTED_SIGNAL, select_provider_recipe
from observatory.search_mentions_derive import derive_search_mentions
from observatory.settings import Settings

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_ai_optimization_search_mentions_ai03.json"
)
KO_FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_keyword_overview_pf03.json"
)
ORGANIC_FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_google_organic_pf10.json"
)
KEYWORD = "generative engine optimization"
HISTORY = "/v1/providers/dataforseo/google/ai-optimization/search-mentions/history"
OUTCOMES = "/v1/providers/dataforseo/google/ai-optimization/search-mentions/outcomes"
HOLDINGS = "/v1/providers/dataforseo/google/ai-optimization/search-mentions/holdings"
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
MENTIONS_HOLDINGS_REQUEST_KEYS = {
    "keyword",
    "match_type",
    "search_filter",
    "search_scope",
    "platform",
    "location_code",
    "language_code",
    "limit",
    "offset",
}
KO_HISTORY = "/v1/providers/dataforseo/google/keyword-overview/history"
ORGANIC_HISTORY = "/v1/providers/dataforseo/google/organic/history"
INTEGRITY_SIGNAL = "evidence_integrity_failure"
ACCEPTED_RECIPE_ID = "bd3dfbf87eba83df35dc7ae6eecd25c223a89ad72d910db346d8ebafb61933e0"
MENTIONS_KINDS = [ITEM_KIND, MONTHLY_KIND, SOURCE_KIND]
DISAGREEMENTS = {
    ("search engine optimized", 135000, 110000),
    ("seos", 110000, 60500),
    ("engine optimization service", 110000, 49500),
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
CAPTURE_KEYS = {
    "attempt_id",
    "capture_id",
    "provider",
    "adapter_contract",
    "derivation_version_id",
    "authorized_at",
    "request_started_at",
    "transport_ended_at",
    "request",
    "capture_outcome",
    "result_context",
    "search_mention_items",
    "monthly_search_volume",
    "structured_sources",
}
REQUEST_KEYS = {
    "match_type",
    "search_filter",
    "search_scope",
    "platform",
    "location_code",
    "language_code",
    "limit",
    "offset",
}
CONTEXT_KEYS = {
    "requested_keyword",
    "total_count",
    "result_offset",
    "items_count",
    "search_after_token",
}
ITEM_KEYS = {
    "observation_kind",
    "within_capture_identity",
    "requested_keyword",
    "platform",
    "model_name",
    "location_code",
    "language_code",
    "question",
    "answer",
    "ai_search_volume",
    "is_web_search_based",
    "first_response_at",
    "last_response_at",
    "search_results",
    "brand_entities",
    "fan_out_queries",
    "occurrences",
}
MONTHLY_KEYS = {
    "observation_kind",
    "within_capture_identity",
    "requested_keyword",
    "model_name",
    "question",
    "data_period",
    "search_volume",
    "occurrences",
}
SOURCE_KEYS = {
    "observation_kind",
    "within_capture_identity",
    "requested_keyword",
    "model_name",
    "question",
    "url",
    "title",
    "domain",
    "source_name",
    "snippet",
    "publication_date",
    "thumbnail",
    "markdown",
    "occurrences",
}
ITEM_OCCURRENCE_KEYS = {"item_index"}
MONTHLY_OCCURRENCE_KEYS = {"item_index"}
SOURCE_OCCURRENCE_KEYS = {"item_index", "rank"}
MENTIONS_TABLES = (
    "search_mentions_result_context",
    "search_mentions_items",
    "search_mentions_item_occurrences",
    "search_mentions_monthly_search_volume",
    "search_mentions_monthly_occurrences",
    "search_mentions_sources",
    "search_mentions_source_occurrences",
)
READONLY_TABLES = (
    "provider_recipes",
    "provider_recipe_selections",
    "outcomes",
    "observation_envelopes",
    *MENTIONS_TABLES,
)
JSON_NULL = {"state": "json_null", "value": None}


@pytest.fixture(autouse=True)
def _no_public_network(monkeypatch: pytest.MonkeyPatch) -> None:
    real_connect = socket.create_connection
    real_gai = socket.getaddrinfo

    def guarded_connect(address: Any, *args: Any, **kwargs: Any) -> socket.socket:
        host = address[0] if isinstance(address, tuple) else address
        if host not in {"127.0.0.1", "::1", "localhost"}:
            raise AssertionError(f"public-network request forbidden: {host}")
        return real_connect(address, *args, **kwargs)

    def guarded_gai(host: Any, *args: Any, **kwargs: Any) -> Any:
        if host not in {"127.0.0.1", "::1", "localhost", None}:
            raise AssertionError(f"DNS forbidden: {host}")
        return real_gai(host, *args, **kwargs)

    def forbidden_credentials(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("credential load forbidden")

    monkeypatch.setattr(socket, "create_connection", guarded_connect)
    monkeypatch.setattr(socket, "getaddrinfo", guarded_gai)
    monkeypatch.setattr(
        "observatory.settings.load_dataforseo_credentials", forbidden_credentials
    )
    monkeypatch.setattr(
        "observatory.dataforseo_ai_optimization_search_mentions_paid_probe"
        ".load_dataforseo_credentials",
        forbidden_credentials,
    )


def _replace_dbname(dsn: str, dbname: str) -> str:
    info = conninfo_to_dict(dsn)
    info["dbname"] = dbname
    return make_conninfo("", **info)


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


def _result(document: dict[str, Any]) -> dict[str, Any]:
    result = document["tasks"][0]["result"][0]
    assert isinstance(result, dict)
    return result


def _set_items(document: dict[str, Any], items: list[Any]) -> None:
    result = _result(document)
    result["items"] = items
    result["items_count"] = len(items)


def _parameters() -> dict[str, object]:
    return closed_mentions_parameters(keyword=KEYWORD)


def _commit_mentions(
    store: EvidenceStore,
    body: bytes,
    nonce: str,
    *,
    started: str,
    authorized_at: str = "2026-08-20T17:36:00.000000Z",
) -> tuple[str, str]:
    parameters = _parameters()
    attempt = mentions_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at=authorized_at,
        observatory_version="ai06-test-v1",
    )
    attempt_id = store.commit_attempt(
        attempt, request_body=mentions_request_body_bytes(parameters)
    )
    capture_id = store.commit_capture(
        mentions_http_capture_document(
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


def _commit_ko(store: EvidenceStore, nonce: str, started: str) -> tuple[str, str]:
    parameters = closed_paid_parameters(
        keywords=["keyword research", "ai search optimization"]
    )
    attempt = paid_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at="2026-08-16T21:37:00.000000Z",
        observatory_version="ai06-ko-v1",
    )
    attempt_id = store.commit_attempt(
        attempt, request_body=paid_request_body_bytes(parameters)
    )
    body = KO_FIXTURE.read_bytes()
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


def _commit_organic(store: EvidenceStore, nonce: str, started: str) -> tuple[str, str]:
    parameters = closed_organic_parameters(keyword="conspiracy theories")
    attempt = organic_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at="2026-08-18T17:37:00.000000Z",
        observatory_version="ai06-organic-v1",
    )
    attempt_id = store.commit_attempt(
        attempt, request_body=organic_request_body_bytes(parameters)
    )
    body = ORGANIC_FIXTURE.read_bytes()
    capture_id = store.commit_capture(
        organic_http_capture_document(
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


def _commit_sandbox(store: EvidenceStore) -> str:
    parameters = closed_sandbox_parameters(
        keyword="observatory test", location_code=2840, language_code="en"
    )
    attempt = http_attempt_document(
        parameters=parameters,
        attempt_nonce="33" * 32,
        authorized_at="2026-08-14T20:00:00.000000Z",
        observatory_version="ai06-sandbox-v1",
    )
    return store.commit_attempt(attempt, request_body=request_body_bytes(parameters))


def _app(store: EvidenceStore, dsn: str) -> TestClient:
    settings = Settings(
        environment="test",
        database_url=dsn,
        evidence_root=store.root,
        derivation_version_id=DEFAULT_VERSION,
    )
    return TestClient(create_app(settings, store=store))


def _history(client: TestClient, keyword: str = KEYWORD, **params: object) -> Any:
    query = {"requested_keyword": keyword, **params}
    return client.get(HISTORY + "?" + urlencode(query, doseq=True))


def _outcomes(client: TestClient, keyword: str = KEYWORD, **params: object) -> Any:
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
    assert set(body) == {
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
    assert "outcomes" not in response.json()
    assert "total_matching" not in response.json()
    assert "returned_count" not in response.json()
    assert "has_more" not in response.json()


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
    assert body["adapter_contract"] == MENTIONS_ADAPTER_CONTRACT
    assert body["total_matching"] == total_matching
    assert body["returned_count"] == returned_count
    assert body["limit"] == limit
    assert body["order"] == order
    assert body["has_more"] is (total_matching > returned_count)
    items = body["holdings"]
    assert isinstance(items, list)
    assert len(items) == returned_count


def _assert_holdings_409(response: Any) -> None:
    assert response.status_code == 409
    assert response.json() == {"detail": INTEGRITY_SIGNAL}
    payload = response.json()
    assert "holdings" not in payload
    assert "total_matching" not in payload
    assert "returned_count" not in payload
    assert "has_more" not in payload


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


def _commit_mentions_keyword(
    store: EvidenceStore, nonce: str, *, keyword: str, authorized_at: str
) -> str:
    parameters = closed_mentions_parameters(keyword=keyword)
    attempt = mentions_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at=authorized_at,
        observatory_version="ai06-test-v1",
    )
    return store.commit_attempt(
        attempt, request_body=mentions_request_body_bytes(parameters)
    )


def _commit_mentions_attempt_only(
    store: EvidenceStore, nonce: str, *, authorized_at: str
) -> str:
    parameters = _parameters()
    attempt = mentions_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at=authorized_at,
        observatory_version="ai06-test-v1",
    )
    return store.commit_attempt(
        attempt, request_body=mentions_request_body_bytes(parameters)
    )


def _commit_mentions_no_response(
    store: EvidenceStore,
    nonce: str,
    *,
    started: str,
    authorized_at: str,
) -> tuple[str, str]:
    parameters = _parameters()
    attempt = mentions_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at=authorized_at,
        observatory_version="ai06-test-v1",
    )
    attempt_id = store.commit_attempt(
        attempt, request_body=mentions_request_body_bytes(parameters)
    )
    capture_id = store.commit_capture(
        mentions_http_capture_document(
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
    assert response.json() == {"detail": "evidence_integrity_failure"}


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


def _prepare_frozen(
    tmp_path: Path,
    postgres_dsn: str,
    *,
    select: bool = True,
    derive: bool = True,
) -> tuple[EvidenceStore, str, str]:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_mentions(
        store, _body(), "11" * 32, started="2026-08-20T17:36:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        if derive:
            derive_search_mentions(store, connection)
        else:
            register_provider_recipe(connection, SEARCH_MENTIONS_RECIPE)
        if select:
            select_provider_recipe(
                connection, MENTIONS_ADAPTER_CONTRACT, SEARCH_MENTIONS_RECIPE_ID
            )
    return store, attempt_id, capture_id


def _xmin_snapshot(dsn: str) -> dict[str, list[tuple[object, ...]]]:
    snapshot: dict[str, list[tuple[object, ...]]] = {}
    with connect(dsn) as connection:
        for table in READONLY_TABLES:
            rows = connection.execute(f"SELECT xmin::text, * FROM {table}").fetchall()
            snapshot[table] = sorted(
                rows, key=lambda row: tuple(str(item) for item in row[1:])
            )
    return snapshot


def _as_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


def _state_value(state: object, value: object) -> dict[str, object]:
    if isinstance(value, tuple):
        value = list(value)
    return {"state": str(state), "value": value}


def _second_recipe() -> dict[str, object]:
    document = copy.deepcopy(SEARCH_MENTIONS_RECIPE)
    document["reconciliation"] = {"rule": "attempt_parameters_item_context_v2"}
    return validate_recipe(document)


def _group_occurrences(
    rows: list[tuple[object, ...]], builder: Any
) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row[0]), []).append(builder(row))
    return grouped


def _persisted_projection(dsn: str, capture_id: str) -> dict[str, Any]:
    """Map accepted AI-05 rows to the AI-06 response shape without product helpers."""

    with connect(dsn) as connection:
        context = connection.execute(
            """
            SELECT requested_keyword, total_count, result_offset, items_count,
                   search_after_token, search_after_token_state
            FROM search_mentions_result_context
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchone()
        items = connection.execute(
            """
            SELECT within_capture_identity, observation_kind, requested_keyword,
                   platform, model_name, location_code, language_code, question,
                   answer, ai_search_volume, is_web_search_based,
                   first_response_at, last_response_at, search_results_state,
                   brand_entities_state, fan_out_queries_state
            FROM search_mentions_items
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY model_name, question, within_capture_identity
            """,
            (capture_id, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchall()
        item_occ = connection.execute(
            """
            SELECT within_capture_identity, item_index
            FROM search_mentions_item_occurrences
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY item_index
            """,
            (capture_id, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchall()
        monthly = connection.execute(
            """
            SELECT within_capture_identity, observation_kind, requested_keyword,
                   model_name, question, year, month, search_volume
            FROM search_mentions_monthly_search_volume
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY year, month, model_name, question, within_capture_identity
            """,
            (capture_id, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchall()
        monthly_occ = connection.execute(
            """
            SELECT within_capture_identity, item_index
            FROM search_mentions_monthly_occurrences
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY item_index
            """,
            (capture_id, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchall()
        sources = connection.execute(
            """
            SELECT within_capture_identity, observation_kind, requested_keyword,
                   model_name, question, url, title, domain, source_name, snippet,
                   publication_date, publication_date_state, thumbnail,
                   thumbnail_state, markdown, markdown_state
            FROM search_mentions_sources
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY model_name, question, url, within_capture_identity
            """,
            (capture_id, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchall()
        source_occ = connection.execute(
            """
            SELECT within_capture_identity, item_index, rank
            FROM search_mentions_source_occurrences
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY item_index, rank
            """,
            (capture_id, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchall()
        envelopes = connection.execute(
            """
            SELECT count(*) FROM observation_envelopes
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchone()
    assert context is not None
    assert envelopes is not None
    item_occ_by = _group_occurrences(
        item_occ, lambda row: {"item_index": _as_int(row[1], "item_index")}
    )
    monthly_occ_by = _group_occurrences(
        monthly_occ, lambda row: {"item_index": _as_int(row[1], "item_index")}
    )
    source_occ_by = _group_occurrences(
        source_occ,
        lambda row: {
            "item_index": _as_int(row[1], "item_index"),
            "rank": _as_int(row[2], "rank"),
        },
    )
    return {
        "envelope_count": _as_int(envelopes[0], "envelope_count"),
        "result_context": {
            "requested_keyword": str(context[0]),
            "total_count": _as_int(context[1], "total_count"),
            "result_offset": _as_int(context[2], "result_offset"),
            "items_count": _as_int(context[3], "items_count"),
            "search_after_token": _state_value(context[5], context[4]),
        },
        "search_mention_items": [
            {
                "observation_kind": str(row[1]),
                "within_capture_identity": str(row[0]),
                "requested_keyword": str(row[2]),
                "platform": str(row[3]),
                "model_name": str(row[4]),
                "location_code": _as_int(row[5], "location_code"),
                "language_code": str(row[6]),
                "question": str(row[7]),
                "answer": str(row[8]),
                "ai_search_volume": _as_int(row[9], "ai_search_volume"),
                "is_web_search_based": bool(row[10]),
                "first_response_at": str(row[11]),
                "last_response_at": str(row[12]),
                "search_results": _state_value(row[13], None),
                "brand_entities": _state_value(row[14], None),
                "fan_out_queries": _state_value(row[15], None),
                "occurrences": item_occ_by.get(str(row[0]), []),
            }
            for row in items
        ],
        "monthly_search_volume": [
            {
                "observation_kind": str(row[1]),
                "within_capture_identity": str(row[0]),
                "requested_keyword": str(row[2]),
                "model_name": str(row[3]),
                "question": str(row[4]),
                "data_period": {
                    "year": _as_int(row[5], "year"),
                    "month": _as_int(row[6], "month"),
                },
                "search_volume": _as_int(row[7], "search_volume"),
                "occurrences": monthly_occ_by.get(str(row[0]), []),
            }
            for row in monthly
        ],
        "structured_sources": [
            {
                "observation_kind": str(row[1]),
                "within_capture_identity": str(row[0]),
                "requested_keyword": str(row[2]),
                "model_name": str(row[3]),
                "question": str(row[4]),
                "url": str(row[5]),
                "title": str(row[6]),
                "domain": str(row[7]),
                "source_name": str(row[8]),
                "snippet": str(row[9]),
                "publication_date": _state_value(row[11], row[10]),
                "thumbnail": _state_value(row[13], row[12]),
                "markdown": _state_value(row[15], row[14]),
                "occurrences": source_occ_by.get(str(row[0]), []),
            }
            for row in sources
        ],
    }


@pytest.fixture(scope="module")
def frozen_pg(postgres_admin_dsn: str, tmp_path_factory: pytest.TempPathFactory) -> Any:
    dbname = "obs_" + uuid.uuid4().hex
    with psycopg.connect(postgres_admin_dsn, autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
    dsn = _replace_dbname(postgres_admin_dsn, dbname)
    store_root = tmp_path_factory.mktemp("frozen-mentions")
    store, attempt_id, capture_id = _prepare_frozen(store_root, dsn)
    try:
        yield store, dsn, attempt_id, capture_id
    finally:
        with psycopg.connect(postgres_admin_dsn, autocommit=True) as admin:
            admin.execute(
                sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(
                    sql.Identifier(dbname)
                )
            )


def test_fixture_ko_and_organic_remain_isolated_from_search_mentions_selection(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, mentions_attempt, _mentions_capture = _prepare_frozen(tmp_path, postgres_dsn)
    ko_attempt, _ko_capture = _commit_ko(
        store, "51" * 32, started="2026-08-16T21:37:01.100000Z"
    )
    organic_attempt, _organic_capture = _commit_organic(
        store, "61" * 32, started="2026-08-18T17:37:01.100000Z"
    )
    fixture = capture_fixture(
        store,
        FixtureCaptureInputs(
            scenario="admitted_results",
            panel_id="panel-alpha",
            subject_key="subject-one",
            depth=2,
            attempt_nonce=secrets.token_hex(32),
            authorized_at="2026-08-11T20:15:30.123456Z",
            observatory_version="conformance-v1",
            request_started_at="2026-08-11T20:15:30.200000Z",
            transport_ended_at="2026-08-11T20:15:31.000000Z",
            response_headers_at="2026-08-11T20:15:30.900000Z",
            response_body_ended_at="2026-08-11T20:15:30.950000Z",
        ),
    )
    second = _second_recipe()
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
        derive_keyword_overview_extended(store, connection)
        derive_google_organic(store, connection)
        register_provider_recipe(connection, CORE_RECIPE)
        register_provider_recipe(connection, GOOGLE_ORGANIC_RECIPE)
        registered = register_provider_recipe(connection, second)
        select_provider_recipe(connection, PAID_ADAPTER_CONTRACT, EXTENDED_RECIPE_ID)
        select_provider_recipe(
            connection, ORGANIC_ADAPTER_CONTRACT, GOOGLE_ORGANIC_RECIPE_ID
        )
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, 'observation_admitted', 1)
            """,
            (mentions_attempt, _mentions_capture, registered.derivation_version_id),
        )
        connection.execute(
            """
            INSERT INTO search_mentions_result_context (
                capture_id, derivation_version_id, attempt_id,
                requested_keyword, match_type, search_filter, search_scope,
                platform, location_code, language_code, request_limit,
                request_offset, total_count, result_offset, items_count,
                search_after_token, search_after_token_state
            )
            VALUES (
                %s, %s, %s, %s, 'word_match', 'include', ARRAY['answer'],
                'google', 2840, 'en', 5, 0, 3055, 0, 5, 'other-token', 'stated'
            )
            """,
            (
                _mentions_capture,
                registered.derivation_version_id,
                mentions_attempt,
                KEYWORD,
            ),
        )
        mentions_before = connection.execute(
            """
            SELECT derivation_version_id FROM provider_recipe_selections
            WHERE adapter_contract = %s
            """,
            (MENTIONS_ADAPTER_CONTRACT,),
        ).fetchone()
        ko_before = connection.execute(
            """
            SELECT derivation_version_id FROM provider_recipe_selections
            WHERE adapter_contract = %s
            """,
            (PAID_ADAPTER_CONTRACT,),
        ).fetchone()
        organic_before = connection.execute(
            """
            SELECT derivation_version_id FROM provider_recipe_selections
            WHERE adapter_contract = %s
            """,
            (ORGANIC_ADAPTER_CONTRACT,),
        ).fetchone()
        select_provider_recipe(connection, PAID_ADAPTER_CONTRACT, CORE_RECIPE_ID)
        select_provider_recipe(
            connection, MENTIONS_ADAPTER_CONTRACT, SEARCH_MENTIONS_RECIPE_ID
        )
        mentions_after = connection.execute(
            """
            SELECT derivation_version_id FROM provider_recipe_selections
            WHERE adapter_contract = %s
            """,
            (MENTIONS_ADAPTER_CONTRACT,),
        ).fetchone()
        organic_after = connection.execute(
            """
            SELECT derivation_version_id FROM provider_recipe_selections
            WHERE adapter_contract = %s
            """,
            (ORGANIC_ADAPTER_CONTRACT,),
        ).fetchone()
        select_provider_recipe(connection, PAID_ADAPTER_CONTRACT, EXTENDED_RECIPE_ID)
    assert mentions_before == mentions_after == (SEARCH_MENTIONS_RECIPE_ID,)
    assert ko_before == (EXTENDED_RECIPE_ID,)
    assert organic_before == organic_after == (GOOGLE_ORGANIC_RECIPE_ID,)
    sandbox_id = _commit_sandbox(store)
    with _app(store, postgres_dsn) as client:
        fixture_body = client.get(f"/v1/attempts/{fixture.attempt_id}").json()
        ko_body = client.get(
            f"/v1/attempts/{ko_attempt}?derivation_version_id={EXTENDED_RECIPE_ID}"
        ).json()
        organic = client.get(f"/v1/attempts/{organic_attempt}").json()
        mentions = client.get(f"/v1/attempts/{mentions_attempt}").json()
        sandbox = client.get(f"/v1/attempts/{sandbox_id}")
        ko_history = client.get(
            KO_HISTORY
            + "?"
            + urlencode(
                {
                    "requested_keyword": "keyword research",
                    "derivation_version_id": EXTENDED_RECIPE_ID,
                }
            )
        )
        organic_history = client.get(
            ORGANIC_HISTORY + "?" + urlencode({"requested_keyword": "conspiracy theories"})
        )
        mentions_history = _history(client)
    assert set(fixture_body) == {
        "attempt_id",
        "derivation_version_id",
        "attempt_outcome",
        "capture_outcome",
        "observations",
    }
    assert fixture_body["observations"][0]["panel_id"] == "panel-alpha"
    assert fixture_body["observations"][0]["score"] == 999
    assert ko_body["adapter_contract"] == PAID_ADAPTER_CONTRACT
    assert ko_body["derivation_version_id"] == EXTENDED_RECIPE_ID
    assert "observations" not in ko_body
    assert organic["adapter_contract"] == ORGANIC_ADAPTER_CONTRACT
    assert organic["derivation_version_id"] == GOOGLE_ORGANIC_RECIPE_ID
    assert mentions["adapter_contract"] == MENTIONS_ADAPTER_CONTRACT
    assert mentions["derivation_version_id"] == SEARCH_MENTIONS_RECIPE_ID
    assert sandbox.status_code == 404
    assert sandbox.json() == {"detail": "not found"}
    assert ko_history.status_code == 200
    assert ko_history.json()["adapter_contract"] == PAID_ADAPTER_CONTRACT
    assert organic_history.status_code == 200
    assert organic_history.json()["adapter_contract"] == ORGANIC_ADAPTER_CONTRACT
    assert mentions_history.status_code == 200
    body = mentions_history.json()
    assert body["adapter_contract"] == MENTIONS_ADAPTER_CONTRACT
    assert body["derivation_version_id"] == SEARCH_MENTIONS_RECIPE_ID
    assert len(body["captures"]) == 1
    assert body["captures"][0]["capture_outcome"]["observation_count"] == 113
    assert body["captures"][0]["derivation_version_id"] == SEARCH_MENTIONS_RECIPE_ID


def test_search_mentions_attempt_selected_pinned_and_http_errors(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_frozen(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, TEST_RECIPE)
        register_provider_recipe(connection, CORE_RECIPE)
    with _app(store, postgres_dsn) as client:
        selected = client.get(f"/v1/attempts/{attempt_id}")
        pinned = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={SEARCH_MENTIONS_RECIPE_ID}"
        )
        wrong = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={CORE_RECIPE_ID}"
        )
        unknown = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={'ab' * 32}"
        )
        test_recipe = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={TEST_RECIPE_ID}"
        )
        malformed = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id=not-a-digest"
        )
        wrong_history = _history(client, derivation_version_id=CORE_RECIPE_ID)
        unknown_history = _history(client, derivation_version_id="ab" * 32)
        malformed_history = _history(client, derivation_version_id="not-a-digest")
    assert selected.status_code == 200
    body = selected.json()
    assert body["attempt_id"] == attempt_id
    assert body["provider"] == "dataforseo"
    assert body["adapter_contract"] == MENTIONS_ADAPTER_CONTRACT
    assert body["derivation_version_id"] == SEARCH_MENTIONS_RECIPE_ID
    assert body["recipe_resolution"] == "selected"
    assert body["attempt_outcome"]["classification"] == "authorized_unresolved"
    assert body["capture_outcome"]["capture_id"] == capture_id
    assert body["capture_outcome"]["observation_count"] == 113
    assert "observations" not in body
    assert "panel_id" not in body
    assert "search_mention_items" not in body
    assert "monthly_search_volume" not in body
    assert "structured_sources" not in body
    assert pinned.status_code == 200
    assert pinned.json()["recipe_resolution"] == "pinned"
    assert pinned.json()["derivation_version_id"] == SEARCH_MENTIONS_RECIPE_ID
    assert wrong.status_code == 404
    assert unknown.status_code == 404
    assert test_recipe.status_code == 404
    assert malformed.status_code == 404
    assert wrong_history.status_code == 404
    assert unknown_history.status_code == 404
    assert malformed_history.status_code == 404
    assert wrong_history.json() == {"detail": "not found"}
    empty_store = create_store(tmp_path / "empty")
    empty_attempt, _empty_capture = _commit_mentions(
        empty_store, _body(), "12" * 32, started="2026-08-20T17:36:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, SEARCH_MENTIONS_RECIPE)
        select_provider_recipe(
            connection, MENTIONS_ADAPTER_CONTRACT, SEARCH_MENTIONS_RECIPE_ID
        )
    with _app(empty_store, postgres_dsn) as client:
        missing_rows = client.get(f"/v1/attempts/{empty_attempt}")
        empty_history = _history(client, "not-a-requested-keyword")
        blank_history = _history(client, "")
    assert missing_rows.status_code == 404
    assert empty_history.status_code == 200
    _assert_history_envelope(empty_history.json(), total_matching=0, returned_count=0)
    assert empty_history.json()["captures"] == []
    assert blank_history.status_code == 200
    _assert_history_envelope(blank_history.json(), total_matching=0, returned_count=0)
    assert blank_history.json()["captures"] == []
    unselected = create_store(tmp_path / "unselected")
    unselected_attempt, _cap = _commit_mentions(
        unselected, _body(), "13" * 32, started="2026-08-20T17:36:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(unselected, connection)
        connection.execute(
            "DELETE FROM provider_recipe_selections WHERE adapter_contract = %s",
            (MENTIONS_ADAPTER_CONTRACT,),
        )
    with _app(unselected, postgres_dsn) as client:
        missing_selection = client.get(f"/v1/attempts/{unselected_attempt}")
        unselected_history = _history(client)
    assert missing_selection.status_code == 503
    assert missing_selection.json()["detail"] == NOT_SELECTED_SIGNAL
    assert unselected_history.status_code == 503
    assert unselected_history.json()["detail"] == NOT_SELECTED_SIGNAL


def test_frozen_history_shape_counts_token_and_volume_disagreements(
    frozen_pg: Any,
) -> None:
    store, dsn, attempt_id, capture_id = frozen_pg
    with _app(store, dsn) as client:
        response = _history(client)
        pinned = _history(client, derivation_version_id=SEARCH_MENTIONS_RECIPE_ID)
        spec = client.get("/api/v1/openapi.json")
        missing = client.get(HISTORY)
        bad_limit = _history(client, limit=0)
        high_limit = _history(client, limit=101)
        bad_order = _history(client, order="sideways")
    assert SEARCH_MENTIONS_RECIPE_ID == ACCEPTED_RECIPE_ID
    assert response.status_code == 200
    body = response.json()
    expected = _persisted_projection(dsn, capture_id)
    _assert_history_envelope(body, total_matching=1, returned_count=1)
    assert set(body) == HISTORY_KEYS
    assert body["provider"] == "dataforseo"
    assert body["adapter_contract"] == MENTIONS_ADAPTER_CONTRACT
    assert body["requested_keyword"] == KEYWORD
    assert body["derivation_version_id"] == SEARCH_MENTIONS_RECIPE_ID
    assert body["recipe_resolution"] == "selected"
    assert body["observation_kinds"] == MENTIONS_KINDS
    assert len(body["captures"]) == 1
    group = body["captures"][0]
    assert set(group) == CAPTURE_KEYS
    assert group["attempt_id"] == attempt_id
    assert group["capture_id"] == capture_id
    assert group["provider"] == "dataforseo"
    assert group["adapter_contract"] == MENTIONS_ADAPTER_CONTRACT
    assert group["derivation_version_id"] == SEARCH_MENTIONS_RECIPE_ID
    assert group["authorized_at"] == "2026-08-20T17:36:00.000000Z"
    assert group["request_started_at"] == "2026-08-20T17:36:01.100000Z"
    assert group["transport_ended_at"] == "2026-08-20T17:36:01.400000Z"
    assert set(group["request"]) == REQUEST_KEYS
    assert group["request"] == {
        "match_type": "word_match",
        "search_filter": "include",
        "search_scope": ["answer"],
        "platform": "google",
        "location_code": 2840,
        "language_code": "en",
        "limit": 5,
        "offset": 0,
    }
    assert "adapter_contract" not in group["request"]
    assert group["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": 113,
    }
    context = group["result_context"]
    assert set(context) == CONTEXT_KEYS
    assert context == expected["result_context"]
    assert context["requested_keyword"] == KEYWORD
    assert context["total_count"] == 3055
    assert context["result_offset"] == 0
    assert context["items_count"] == 5
    token = context["search_after_token"]
    assert token["state"] == "stated"
    assert isinstance(token["value"], str)
    assert len(token["value"]) == 628
    assert context["items_count"] != group["capture_outcome"]["observation_count"]
    assert body["total_matching"] != group["capture_outcome"]["observation_count"]
    assert body["total_matching"] != context["total_count"]
    assert body["total_matching"] != context["items_count"]
    assert group["capture_outcome"]["observation_count"] == 113
    assert context["total_count"] == 3055
    assert expected["envelope_count"] == 113
    dumped = json.dumps(body)
    assert "cost" not in dumped
    assert "panel_id" not in dumped
    items = group["search_mention_items"]
    assert items == expected["search_mention_items"]
    assert len(items) == 5
    assert all(set(row) == ITEM_KEYS for row in items)
    assert all(row["observation_kind"] == ITEM_KIND for row in items)
    assert all(len(str(row["within_capture_identity"])) == 64 for row in items)
    assert all(row["search_results"] == JSON_NULL for row in items)
    assert all(row["brand_entities"] == JSON_NULL for row in items)
    assert all(row["fan_out_queries"] == JSON_NULL for row in items)
    assert all(len(row["occurrences"]) >= 1 for row in items)
    assert all(
        set(item) == ITEM_OCCURRENCE_KEYS
        for row in items
        for item in row["occurrences"]
    )
    item_occ = [item for row in items for item in row["occurrences"]]
    assert len(item_occ) == 5
    assert [row["question"] for row in items] == sorted(row["question"] for row in items)
    monthly = group["monthly_search_volume"]
    assert monthly == expected["monthly_search_volume"]
    assert len(monthly) == 60
    assert all(set(row) == MONTHLY_KEYS for row in monthly)
    assert all(row["observation_kind"] == MONTHLY_KIND for row in monthly)
    assert all(set(row["data_period"]) == {"year", "month"} for row in monthly)
    assert all(
        set(item) == MONTHLY_OCCURRENCE_KEYS
        for row in monthly
        for item in row["occurrences"]
    )
    monthly_occ = [item for row in monthly for item in row["occurrences"]]
    assert len(monthly_occ) == 60
    sources = group["structured_sources"]
    assert sources == expected["structured_sources"]
    assert len(sources) == 48
    assert all(set(row) == SOURCE_KEYS for row in sources)
    assert all(row["observation_kind"] == SOURCE_KIND for row in sources)
    assert all(
        set(item) == SOURCE_OCCURRENCE_KEYS
        for row in sources
        for item in row["occurrences"]
    )
    source_occ = [item for row in sources for item in row["occurrences"]]
    assert len(source_occ) == 48
    assert len({(row["model_name"], row["question"], row["url"]) for row in sources}) == 48
    newest: dict[tuple[str, str], tuple[int, int, int]] = {}
    for row in monthly:
        key = (str(row["model_name"]), str(row["question"]))
        period = row["data_period"]
        assert isinstance(period, dict)
        stamp = (
            _as_int(period["year"], "year"),
            _as_int(period["month"], "month"),
            _as_int(row["search_volume"], "search_volume"),
        )
        current = newest.get(key)
        if current is None or stamp[:2] > current[:2]:
            newest[key] = stamp
    found = {
        (
            str(row["question"]),
            _as_int(row["ai_search_volume"], "ai_search_volume"),
            newest[(str(row["model_name"]), str(row["question"]))][2],
        )
        for row in items
        if newest[(str(row["model_name"]), str(row["question"]))][2]
        != _as_int(row["ai_search_volume"], "ai_search_volume")
    }
    assert found == DISAGREEMENTS
    clocks = {row["question"]: (row["first_response_at"], row["last_response_at"]) for row in items}
    assert clocks["enception"] == ("2026-01-27 03:48:11 +00:00", "2026-01-27 03:48:11 +00:00")
    assert all(
        row["first_response_at"] != group["request_started_at"]
        and row["last_response_at"] != group["transport_ended_at"]
        for row in items
    )
    assert pinned.status_code == 200
    assert pinned.json()["recipe_resolution"] == "pinned"
    assert pinned.json()["captures"] == body["captures"]
    assert spec.status_code == 200
    assert HISTORY in spec.json()["paths"]
    history_spec = spec.json()["paths"][HISTORY]["get"]
    params = {item["name"] for item in history_spec["parameters"]}
    assert params == {"requested_keyword", "derivation_version_id", "limit", "order"}
    _assert_history_openapi(spec.json(), HISTORY)
    assert missing.status_code == 422
    assert bad_limit.status_code == 422
    assert high_limit.status_code == 422
    assert bad_order.status_code == 422


def test_admitted_empty_and_non_admitted_context_stay_distinct(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    _set_items(document, [])
    store = create_store(tmp_path / "empty")
    empty_attempt, empty_capture = _commit_mentions(
        store, _encode(document), "26" * 32, started="2026-08-20T17:36:02.100000Z"
    )
    frozen_attempt, frozen_capture = _commit_mentions(
        store, _body(), "11" * 32, started="2026-08-20T17:36:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        select_provider_recipe(
            connection, MENTIONS_ADAPTER_CONTRACT, SEARCH_MENTIONS_RECIPE_ID
        )
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                "ab" * 32,
                "cd" * 32,
                SEARCH_MENTIONS_RECIPE_ID,
                "provider_error",
                0,
            ),
        )
        connection.execute(
            """
            INSERT INTO search_mentions_result_context (
                capture_id, derivation_version_id, attempt_id,
                requested_keyword, match_type, search_filter, search_scope,
                platform, location_code, language_code, request_limit,
                request_offset, total_count, result_offset, items_count,
                search_after_token, search_after_token_state
            )
            VALUES (
                %s, %s, %s, %s, 'word_match', 'include', ARRAY['answer'],
                'google', 2840, 'en', 5, 0, 3055, 0, 0, NULL, 'json_null'
            )
            """,
            ("cd" * 32, SEARCH_MENTIONS_RECIPE_ID, "ab" * 32, KEYWORD),
        )
        envelopes = connection.execute(
            "SELECT count(*) FROM observation_envelopes WHERE capture_id = %s",
            (empty_capture,),
        ).fetchone()
    assert envelopes == (0,)
    with _app(store, postgres_dsn) as client:
        response = _history(client, order="asc")
    assert response.status_code == 200
    captures = response.json()["captures"]
    _assert_history_envelope(response.json(), total_matching=2, returned_count=2, order="asc")
    assert [item["capture_id"] for item in captures] == [frozen_capture, empty_capture]
    assert captures[0]["attempt_id"] == frozen_attempt
    empty = captures[1]
    assert empty["attempt_id"] == empty_attempt
    assert empty["capture_outcome"] == {
        "classification": "observation_admitted_empty",
        "observation_count": 0,
    }
    assert empty["result_context"]["items_count"] == 0
    assert empty["result_context"]["total_count"] == 3055
    assert empty["search_mention_items"] == []
    assert empty["monthly_search_volume"] == []
    assert empty["structured_sources"] == []
    assert all(item["capture_id"] != "cd" * 32 for item in captures)


def test_swapped_outcome_classification_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    _set_items(document, [])
    store = create_store(tmp_path / "swap")
    _empty_attempt, empty_capture = _commit_mentions(
        store, _encode(document), "26" * 32, started="2026-08-20T17:36:02.100000Z"
    )
    _frozen_attempt, frozen_capture = _commit_mentions(
        store, _body(), "11" * 32, started="2026-08-20T17:36:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        select_provider_recipe(
            connection, MENTIONS_ADAPTER_CONTRACT, SEARCH_MENTIONS_RECIPE_ID
        )
        rows = connection.execute(
            """
            SELECT capture_id, classification, observation_count
            FROM outcomes
            WHERE capture_id IN (%s, %s) AND derivation_version_id = %s
            """,
            (frozen_capture, empty_capture, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchall()
        by_id = {str(row[0]): (str(row[1]), int(row[2])) for row in rows}
        frozen_envelopes = connection.execute(
            """
            SELECT count(*) FROM observation_envelopes
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (frozen_capture, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchone()
        empty_envelopes = connection.execute(
            """
            SELECT count(*) FROM observation_envelopes
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (empty_capture, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchone()
    assert by_id[frozen_capture] == ("observation_admitted", 113)
    assert by_id[empty_capture] == ("observation_admitted_empty", 0)
    assert frozen_envelopes == (113,)
    assert empty_envelopes == (0,)
    with _app(store, postgres_dsn) as client:
        healthy = _history(client, order="asc")
    assert healthy.status_code == 200
    healthy_captures = healthy.json()["captures"]
    assert [item["capture_id"] for item in healthy_captures] == [
        frozen_capture,
        empty_capture,
    ]
    assert healthy_captures[0]["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": 113,
    }
    assert len(healthy_captures[0]["search_mention_items"]) == 5
    assert healthy_captures[1]["capture_outcome"] == {
        "classification": "observation_admitted_empty",
        "observation_count": 0,
    }
    assert healthy_captures[1]["search_mention_items"] == []
    assert healthy_captures[1]["monthly_search_volume"] == []
    assert healthy_captures[1]["structured_sources"] == []

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE outcomes
            SET classification = 'observation_admitted_empty'
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (frozen_capture, SEARCH_MENTIONS_RECIPE_ID),
        )
        planted = connection.execute(
            """
            SELECT classification, observation_count FROM outcomes
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (frozen_capture, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchone()
        still_envelopes = connection.execute(
            """
            SELECT count(*) FROM observation_envelopes
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (frozen_capture, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchone()
    assert planted == ("observation_admitted_empty", 113)
    assert still_envelopes == (113,)
    with _app(store, postgres_dsn) as client:
        empty_label = _history(client)
    assert empty_label.status_code == 409
    assert empty_label.json()["detail"] == INTEGRITY_SIGNAL
    _assert_history_409(empty_label)

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE outcomes
            SET classification = 'observation_admitted'
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (frozen_capture, SEARCH_MENTIONS_RECIPE_ID),
        )
        connection.execute(
            """
            UPDATE outcomes
            SET classification = 'observation_admitted'
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (empty_capture, SEARCH_MENTIONS_RECIPE_ID),
        )
        planted_empty = connection.execute(
            """
            SELECT classification, observation_count FROM outcomes
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (empty_capture, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchone()
        still_empty_envelopes = connection.execute(
            """
            SELECT count(*) FROM observation_envelopes
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (empty_capture, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchone()
    assert planted_empty == ("observation_admitted", 0)
    assert still_empty_envelopes == (0,)
    with _app(store, postgres_dsn) as client:
        admitted_label = _history(client)
    assert admitted_label.status_code == 409
    assert admitted_label.json()["detail"] == INTEGRITY_SIGNAL
    _assert_history_409(admitted_label)


def test_classification_disagreement_outside_limit_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "outside")
    _commit_mentions(store, _body(), "81" * 32, started="2026-08-20T17:36:01.100000Z")
    later_attempt, later_capture = _commit_mentions(
        store,
        _body(),
        "82" * 32,
        started="2026-08-20T17:37:01.100000Z",
        authorized_at="2026-08-20T17:37:00.000000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        select_provider_recipe(
            connection, MENTIONS_ADAPTER_CONTRACT, SEARCH_MENTIONS_RECIPE_ID
        )
        connection.execute(
            """
            UPDATE outcomes
            SET classification = 'observation_admitted_empty'
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (later_capture, SEARCH_MENTIONS_RECIPE_ID),
        )
        planted = connection.execute(
            """
            SELECT classification, observation_count FROM outcomes
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (later_capture, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchone()
    assert planted == ("observation_admitted_empty", 113)
    with _app(store, postgres_dsn) as client:
        limited = _history(client, limit=1, order="asc")
        later = client.get(f"/v1/attempts/{later_attempt}")
    _assert_history_409(limited)
    assert later.status_code == 200
    assert later.json()["capture_outcome"]["classification"] == "observation_admitted_empty"
    assert later.json()["capture_outcome"]["observation_count"] == 113


def test_duplicate_identities_collapse_and_cross_question_urls_stay_separate(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    items = _result(document)["items"]
    first_url = items[0]["sources"][0]["url"]
    first_question = items[0]["question"]
    second_question = items[1]["question"]
    items.append(copy.deepcopy(items[0]))
    extra_same = copy.deepcopy(items[0]["sources"][0])
    extra_same_rank = len(items[0]["sources"]) + 1
    extra_same["rank"] = extra_same_rank
    items[0]["sources"].append(extra_same)
    extra_other = copy.deepcopy(items[0]["sources"][0])
    extra_other_rank = len(items[1]["sources"]) + 1
    extra_other["rank"] = extra_other_rank
    items[1]["sources"].append(extra_other)
    _set_items(document, items)
    store = create_store(tmp_path / "dup")
    _attempt_id, capture_id = _commit_mentions(
        store, _encode(document), "27" * 32, started="2026-08-20T17:36:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        select_provider_recipe(
            connection, MENTIONS_ADAPTER_CONTRACT, SEARCH_MENTIONS_RECIPE_ID
        )
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    assert response.status_code == 200
    group = response.json()["captures"][0]
    assert group["capture_id"] == capture_id
    item_parents = group["search_mention_items"]
    assert len(item_parents) == 5
    by_question = {row["question"]: row for row in item_parents}
    assert sorted(item["item_index"] for item in by_question[first_question]["occurrences"]) == [
        0,
        5,
    ]
    sources = group["structured_sources"]
    same = [
        row
        for row in sources
        if row["url"] == first_url and row["question"] == first_question
    ]
    other = [
        row
        for row in sources
        if row["url"] == first_url and row["question"] == second_question
    ]
    assert len(same) == 1
    assert len(other) == 1
    assert same[0]["within_capture_identity"] != other[0]["within_capture_identity"]
    assert {(item["item_index"], item["rank"]) for item in same[0]["occurrences"]} >= {
        (0, 1),
        (0, extra_same_rank),
        (5, 1),
    }
    assert any(item["rank"] == extra_other_rank for item in other[0]["occurrences"])


def test_second_capture_order_limit_and_tie_break(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "two")
    first_attempt, first_capture = _commit_mentions(
        store, _body(), "31" * 32, started="2026-08-20T17:36:01.100000Z"
    )
    later_attempt, later_capture = _commit_mentions(
        store,
        _body(),
        "32" * 32,
        started="2026-08-20T17:37:01.100000Z",
        authorized_at="2026-08-20T17:37:00.000000Z",
    )
    tied_a_attempt, tied_a_capture = _commit_mentions(
        store,
        _body(),
        "33" * 32,
        started="2026-08-20T17:38:01.100000Z",
        authorized_at="2026-08-20T17:38:00.000000Z",
    )
    tied_b_attempt, tied_b_capture = _commit_mentions(
        store,
        _body(),
        "34" * 32,
        started="2026-08-20T17:38:01.100000Z",
        authorized_at="2026-08-20T17:38:00.500000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        select_provider_recipe(
            connection, MENTIONS_ADAPTER_CONTRACT, SEARCH_MENTIONS_RECIPE_ID
        )
    with _app(store, postgres_dsn) as client:
        ascending = _history(client, order="asc")
        descending = _history(client, order="desc", limit=2)
        limited = _history(client, order="asc", limit=1)
    assert ascending.status_code == 200
    captures = ascending.json()["captures"]
    assert [item["capture_id"] for item in captures] == [
        first_capture,
        later_capture,
        *sorted([tied_a_capture, tied_b_capture]),
    ]
    assert captures[0]["attempt_id"] == first_attempt
    assert captures[1]["attempt_id"] == later_attempt
    assert len(captures[0]["search_mention_items"]) == 5
    assert len(captures[0]["monthly_search_volume"]) == 60
    assert len(captures[0]["structured_sources"]) == 48
    assert descending.json()["captures"][0]["capture_id"] == max(
        tied_a_capture, tied_b_capture
    )
    assert [item["capture_id"] for item in limited.json()["captures"]] == [first_capture]
    _assert_history_envelope(
        limited.json(), total_matching=4, returned_count=1, limit=1
    )
    _assert_history_envelope(
        descending.json(), total_matching=4, returned_count=2, limit=2, order="desc"
    )
    _assert_history_envelope(ascending.json(), total_matching=4, returned_count=4)
    assert len(limited.json()["captures"][0]["search_mention_items"]) == 5
    assert {captures[2]["attempt_id"], captures[3]["attempt_id"]} == {
        tied_a_attempt,
        tied_b_attempt,
    }
    assert captures[2]["request_started_at"] == captures[3]["request_started_at"]
    assert captures[2]["capture_id"] < captures[3]["capture_id"]


def test_foreign_attempt_outcome_does_not_supply_history(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_frozen(tmp_path, postgres_dsn)
    foreign_attempt = "ab" * 32
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (foreign_attempt, capture_id, SEARCH_MENTIONS_RECIPE_ID, "provider_error", 0),
        )
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    assert response.status_code == 200
    captures = response.json()["captures"]
    assert [item["capture_id"] for item in captures] == [capture_id]
    assert captures[0]["attempt_id"] == attempt_id
    assert captures[0]["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": 113,
    }


def test_request_context_integrity_and_damage_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_frozen(tmp_path, postgres_dsn)
    later_attempt, later_capture = _commit_mentions(
        store,
        _body(),
        "41" * 32,
        started="2026-08-20T17:37:01.100000Z",
        authorized_at="2026-08-20T17:37:00.000000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        select_provider_recipe(
            connection, MENTIONS_ADAPTER_CONTRACT, SEARCH_MENTIONS_RECIPE_ID
        )
        connection.execute(
            """
            UPDATE search_mentions_result_context
            SET location_code = 9999
            WHERE capture_id = %s
            """,
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        disagreed = _history(client)
    assert disagreed.status_code == 409
    assert disagreed.json()["detail"] == INTEGRITY_SIGNAL
    _assert_history_409(disagreed)

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE search_mentions_result_context
            SET location_code = 2840, request_limit = 9
            WHERE capture_id = %s
            """,
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        limit_disagreed = _history(client)
    assert limit_disagreed.status_code == 409
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE search_mentions_result_context
            SET request_limit = 5, request_offset = 9
            WHERE capture_id = %s
            """,
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        offset_disagreed = _history(client)
    assert offset_disagreed.status_code == 409
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE search_mentions_result_context
            SET request_offset = 0
            WHERE capture_id = %s
            """,
            (capture_id,),
        )

    real_read = EvidenceStore.read_attempt.__get__(store, EvidenceStore)

    def _install_mutator(drop: str | None, mistype: str | None) -> None:
        def mutated(value: str) -> dict[str, object] | None:
            attempt = real_read(value)
            if attempt is None:
                return None
            raw_parameters = attempt["parameters"]
            if not isinstance(raw_parameters, dict):
                raise TypeError("verified Attempt parameters must be an object")
            parameters = dict(raw_parameters)
            if drop is not None:
                parameters.pop(drop, None)
            if mistype is not None:
                parameters[mistype] = "not-an-int"
            changed = dict(attempt)
            changed["parameters"] = parameters
            return changed

        store.read_attempt = mutated  # type: ignore[method-assign, assignment]

    _install_mutator(drop="limit", mistype=None)
    with _app(store, postgres_dsn) as client:
        missing_limit = _history(client)
    _install_mutator(drop=None, mistype="location_code")
    with _app(store, postgres_dsn) as client:
        wrong_type = _history(client)
    store.read_attempt = real_read  # type: ignore[method-assign]
    assert missing_limit.status_code == 409
    _assert_history_409(missing_limit)
    assert wrong_type.status_code == 409
    _assert_history_409(wrong_type)

    real_capture = EvidenceStore.read_capture.__get__(store, EvidenceStore)

    def cross_linked(value: str) -> dict[str, object] | None:
        capture = real_capture(value)
        if capture is None:
            return None
        changed = dict(capture)
        changed["attempt_id"] = "ab" * 32
        return changed

    store.read_capture = cross_linked  # type: ignore[method-assign, assignment]
    with _app(store, postgres_dsn) as client:
        linked = _history(client)
    assert linked.status_code == 409

    def wrong_adapter(value: str) -> dict[str, object] | None:
        capture = real_capture(value)
        if capture is None:
            return None
        changed = dict(capture)
        changed["adapter_contract"] = ORGANIC_ADAPTER_CONTRACT
        return changed

    store.read_capture = wrong_adapter  # type: ignore[method-assign, assignment]
    with _app(store, postgres_dsn) as client:
        adapter = _history(client)
    store.read_capture = real_capture  # type: ignore[method-assign]
    assert adapter.status_code == 409

    body_path = store.capture_path(later_capture) / "response.body"
    payload = bytearray(body_path.read_bytes())
    payload[0] ^= 0x01
    body_path.write_bytes(bytes(payload))
    with _app(store, postgres_dsn) as client:
        outside = _history(client, limit=1, order="asc")
        resource = client.get(f"/v1/attempts/{later_attempt}")
    assert outside.status_code == 409
    _assert_history_409(outside)
    assert resource.status_code == 409
    body_path.write_bytes(bytes(bytearray(payload[0] ^ 0x01) + payload[1:]))

    manifest = store.capture_path(capture_id) / "capture.json"
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    with _app(store, postgres_dsn) as client:
        damaged_capture = _history(client)
    assert damaged_capture.status_code == 409
    _assert_history_409(damaged_capture)
    manifest.write_bytes(bytes(bytearray(raw[0] ^ 0x01) + raw[1:]))

    attempt_manifest = next(store.root.glob(f"attempts/**/{attempt_id}/attempt.json"))
    attempt_raw = bytearray(attempt_manifest.read_bytes())
    attempt_raw[0] ^= 0x01
    attempt_manifest.write_bytes(bytes(attempt_raw))
    with _app(store, postgres_dsn) as client:
        damaged_attempt = _history(client)
    assert damaged_attempt.status_code == 409


def test_token_presence_performs_zero_continuation_or_transport(
    tmp_path: Path, postgres_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, attempt_id, capture_id = _prepare_frozen(tmp_path, postgres_dsn)

    def boom(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("continuation, capture, or derive action is forbidden")

    monkeypatch.setattr("observatory.search_mentions_derive.derive_search_mentions", boom)
    monkeypatch.setattr(
        "observatory.dataforseo_ai_optimization_search_mentions_paid_probe"
        ".capture_dataforseo_ai_optimization_search_mentions_paid_probe",
        boom,
    )
    monkeypatch.setattr(
        "observatory.http_single_exchange.perform_bounded_http_exchange", boom
    )
    monkeypatch.setattr("observatory.capture.capture_fixture", boom)
    before_ops = list(store.recorded_ops)
    before_pg = _xmin_snapshot(postgres_dsn)
    with _app(store, postgres_dsn) as client:
        response = _history(client)
        attempt = client.get(f"/v1/attempts/{attempt_id}")
    assert response.status_code == 200
    token = response.json()["captures"][0]["result_context"]["search_after_token"]
    assert token["state"] == "stated"
    assert token["value"]
    assert attempt.status_code == 200
    assert store.recorded_ops == before_ops
    assert _xmin_snapshot(postgres_dsn) == before_pg
    assert capture_id == response.json()["captures"][0]["capture_id"]


def test_api_reads_do_not_mutate_search_mentions_state(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, _capture_id = _prepare_frozen(tmp_path, postgres_dsn)
    before_ops = list(store.recorded_ops)
    before_pg = _xmin_snapshot(postgres_dsn)
    with _app(store, postgres_dsn) as client:
        assert client.get(f"/v1/attempts/{attempt_id}").status_code == 200
        assert _history(client).status_code == 200
        assert _history(client, derivation_version_id=SEARCH_MENTIONS_RECIPE_ID).status_code == 200
    assert store.recorded_ops == before_ops
    assert _xmin_snapshot(postgres_dsn) == before_pg


def test_two_databases_return_equal_search_mentions_history(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_mentions(store, _body(), "51" * 32, started="2026-08-20T17:36:01.100000Z")
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)
    for dsn in (postgres_dsn, postgres_second_dsn):
        with connect(dsn) as connection:
            derive_search_mentions(store, connection)
            select_provider_recipe(
                connection, MENTIONS_ADAPTER_CONTRACT, SEARCH_MENTIONS_RECIPE_ID
            )
    with (
        _app(store, postgres_dsn) as left,
        _app(store, postgres_second_dsn) as right,
    ):
        left_body = _history(left)
        right_body = _history(right)
    assert left_body.status_code == 200
    assert right_body.status_code == 200
    assert left_body.json() == right_body.json()
    assert left_body.json()["captures"]
    assert left_body.json()["captures"][0]["capture_outcome"]["observation_count"] == 113
    assert len(left_body.json()["captures"][0]["search_mention_items"]) == 5


def test_history_missing_and_extra_typed_rows_are_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_frozen(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        deleted = connection.execute(
            """
            DELETE FROM search_mentions_item_occurrences
            WHERE ctid IN (
                SELECT ctid FROM search_mentions_item_occurrences
                WHERE capture_id = %s AND derivation_version_id = %s
                LIMIT 1
            )
            RETURNING within_capture_identity
            """,
            (capture_id, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchone()
        assert deleted is not None
        connection.execute(
            """
            DELETE FROM search_mentions_items
            WHERE capture_id = %s AND derivation_version_id = %s
              AND within_capture_identity = %s
            """,
            (capture_id, SEARCH_MENTIONS_RECIPE_ID, deleted[0]),
        )
    before_ops = list(store.recorded_ops)
    before_pg = _xmin_snapshot(postgres_dsn)
    with _app(store, postgres_dsn) as client:
        missing = _history(client)
        attempt = client.get(f"/v1/attempts/{attempt_id}")
    assert missing.status_code == 409
    assert missing.json()["detail"] == INTEGRITY_SIGNAL
    _assert_history_409(missing)
    assert attempt.status_code == 200
    assert attempt.json()["capture_outcome"]["observation_count"] == 113
    assert store.recorded_ops == before_ops
    assert _xmin_snapshot(postgres_dsn) == before_pg
    with connect(postgres_dsn) as connection:
        connection.execute(
            "DELETE FROM search_mentions_result_context WHERE capture_id = %s",
            (capture_id,),
        )

    store2, _attempt2, capture2 = _prepare_frozen(tmp_path / "extra", postgres_dsn)
    extra_identity = "ef" * 32
    with connect(postgres_dsn) as connection:
        write_observation_envelope(
            connection,
            ObservationEnvelope(
                capture_id=capture2,
                attempt_id=_attempt2,
                derivation_version_id=SEARCH_MENTIONS_RECIPE_ID,
                provider="dataforseo",
                adapter_contract=MENTIONS_ADAPTER_CONTRACT,
                observation_kind=ITEM_KIND,
                within_capture_identity=extra_identity,
            ),
        )
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = observation_count + 1
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture2, SEARCH_MENTIONS_RECIPE_ID),
        )
    with _app(store2, postgres_dsn) as client:
        extra = _history(client)
    assert extra.status_code == 409
    assert extra.json()["detail"] == INTEGRITY_SIGNAL


def test_history_extra_envelope_wrong_count_and_zero_occurrences_are_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_frozen(tmp_path, postgres_dsn)
    extra_identity = "cd" * 32
    with connect(postgres_dsn) as connection:
        write_observation_envelope(
            connection,
            ObservationEnvelope(
                capture_id=capture_id,
                attempt_id=attempt_id,
                derivation_version_id=SEARCH_MENTIONS_RECIPE_ID,
                provider="dataforseo",
                adapter_contract=MENTIONS_ADAPTER_CONTRACT,
                observation_kind=ITEM_KIND,
                within_capture_identity=extra_identity,
            ),
        )
    with _app(store, postgres_dsn) as client:
        extra_envelope = _history(client)
        attempt = client.get(f"/v1/attempts/{attempt_id}")
    assert extra_envelope.status_code == 409
    assert extra_envelope.json()["detail"] == INTEGRITY_SIGNAL
    assert attempt.status_code == 200
    assert attempt.json()["capture_outcome"]["observation_count"] == 113

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            DELETE FROM observation_envelopes
            WHERE capture_id = %s AND within_capture_identity = %s
            """,
            (capture_id, extra_identity),
        )
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = observation_count + 1
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, SEARCH_MENTIONS_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        wrong_count = _history(client)
        attempt_wrong = client.get(f"/v1/attempts/{attempt_id}")
    assert wrong_count.status_code == 409
    assert attempt_wrong.status_code == 200
    assert attempt_wrong.json()["capture_outcome"]["observation_count"] == 114

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = 113
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, SEARCH_MENTIONS_RECIPE_ID),
        )
        item = connection.execute(
            """
            SELECT within_capture_identity FROM search_mentions_items
            WHERE capture_id = %s ORDER BY question LIMIT 1
            """,
            (capture_id,),
        ).fetchone()
        monthly = connection.execute(
            """
            SELECT within_capture_identity
            FROM search_mentions_monthly_search_volume
            WHERE capture_id = %s ORDER BY year, month LIMIT 1
            """,
            (capture_id,),
        ).fetchone()
        source = connection.execute(
            """
            SELECT within_capture_identity FROM search_mentions_sources
            WHERE capture_id = %s ORDER BY url LIMIT 1
            """,
            (capture_id,),
        ).fetchone()
        assert item is not None and monthly is not None and source is not None
        connection.execute(
            """
            DELETE FROM search_mentions_item_occurrences
            WHERE capture_id = %s AND within_capture_identity = %s
            """,
            (capture_id, item[0]),
        )
    with _app(store, postgres_dsn) as client:
        zero_item = _history(client)
    assert zero_item.status_code == 409
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            INSERT INTO search_mentions_item_occurrences (
                capture_id, derivation_version_id, within_capture_identity,
                observation_kind, item_index
            )
            SELECT capture_id, derivation_version_id, within_capture_identity,
                   observation_kind, 0
            FROM search_mentions_items
            WHERE capture_id = %s AND within_capture_identity = %s
            """,
            (capture_id, item[0]),
        )
        connection.execute(
            """
            DELETE FROM search_mentions_monthly_occurrences
            WHERE capture_id = %s AND within_capture_identity = %s
            """,
            (capture_id, monthly[0]),
        )
    with _app(store, postgres_dsn) as client:
        zero_monthly = _history(client)
    assert zero_monthly.status_code == 409
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            INSERT INTO search_mentions_monthly_occurrences (
                capture_id, derivation_version_id, within_capture_identity,
                observation_kind, item_index
            )
            SELECT capture_id, derivation_version_id, within_capture_identity,
                   observation_kind, 0
            FROM search_mentions_monthly_search_volume
            WHERE capture_id = %s AND within_capture_identity = %s
            """,
            (capture_id, monthly[0]),
        )
        connection.execute(
            """
            DELETE FROM search_mentions_source_occurrences
            WHERE capture_id = %s AND within_capture_identity = %s
            """,
            (capture_id, source[0]),
        )
    with _app(store, postgres_dsn) as client:
        zero_source = _history(client)
    assert zero_source.status_code == 409


def test_history_consistency_damage_outside_limit_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_mentions(store, _body(), "81" * 32, started="2026-08-20T17:36:01.100000Z")
    later_attempt, later_capture = _commit_mentions(
        store,
        _body(),
        "82" * 32,
        started="2026-08-20T17:37:01.100000Z",
        authorized_at="2026-08-20T17:37:00.000000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        select_provider_recipe(
            connection, MENTIONS_ADAPTER_CONTRACT, SEARCH_MENTIONS_RECIPE_ID
        )
        deleted = connection.execute(
            """
            DELETE FROM search_mentions_item_occurrences
            WHERE ctid IN (
                SELECT ctid FROM search_mentions_item_occurrences
                WHERE capture_id = %s AND derivation_version_id = %s
                LIMIT 1
            )
            RETURNING within_capture_identity
            """,
            (later_capture, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchone()
        assert deleted is not None
        connection.execute(
            """
            DELETE FROM search_mentions_items
            WHERE capture_id = %s AND derivation_version_id = %s
              AND within_capture_identity = %s
            """,
            (later_capture, SEARCH_MENTIONS_RECIPE_ID, deleted[0]),
        )
    with _app(store, postgres_dsn) as client:
        limited = _history(client, limit=1, order="asc")
        later = client.get(f"/v1/attempts/{later_attempt}")
    _assert_history_409(limited)
    assert later.status_code == 200
    assert later.json()["capture_outcome"]["observation_count"] == 113


def test_search_mentions_outcomes_admitted_request_and_no_continuation(
    tmp_path: Path, postgres_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, attempt_id, capture_id = _prepare_frozen(tmp_path, postgres_dsn)

    def boom(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("continuation, capture, or derive action is forbidden")

    monkeypatch.setattr("observatory.search_mentions_derive.derive_search_mentions", boom)
    monkeypatch.setattr(
        "observatory.dataforseo_ai_optimization_search_mentions_paid_probe"
        ".capture_dataforseo_ai_optimization_search_mentions_paid_probe",
        boom,
    )
    monkeypatch.setattr(
        "observatory.http_single_exchange.perform_bounded_http_exchange", boom
    )
    with _app(store, postgres_dsn) as client:
        empty = _outcomes(client, "not-measured")
        admitted = _outcomes(client)
        spec = client.get("/api/v1/openapi.json").json()
    assert empty.status_code == 200
    _assert_outcomes_envelope(empty.json(), total_matching=0, returned_count=0)
    assert admitted.status_code == 200
    body = admitted.json()
    _assert_outcomes_envelope(body, total_matching=1, returned_count=1)
    item = body["outcomes"][0]
    assert item["attempt_id"] == attempt_id
    assert item["capture_id"] == capture_id
    assert item["request"]["keyword"] == KEYWORD
    assert item["request"]["limit"] == 5
    assert item["request"]["offset"] == 0
    assert "search_after_token" not in item
    assert "search_after_token" not in item["request"]
    assert item["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": 113,
    }
    request_schema = spec["components"]["schemas"]["SearchMentionsOutcomeRequest"]
    assert "keyword" in request_schema["required"]
    assert "offset" in request_schema["required"]
    text = json.dumps(request_schema).lower()
    assert "continuation" in text or "not an outcomes cursor" in text


def test_search_mentions_outcomes_unresolved_no_response_and_admitted_empty(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    unresolved = _commit_mentions_attempt_only(
        store, "a1" * 32, authorized_at="2026-08-20T17:35:00.000000Z"
    )
    failed_id, failed_capture = _commit_mentions_no_response(
        store,
        "a2" * 32,
        started="2026-08-20T17:36:01.100000Z",
        authorized_at="2026-08-20T17:36:00.000000Z",
    )
    admitted_id, admitted_capture = _commit_mentions(
        store,
        _body(),
        "a3" * 32,
        started="2026-08-20T17:37:01.100000Z",
        authorized_at="2026-08-20T17:37:00.000000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        select_provider_recipe(
            connection, MENTIONS_ADAPTER_CONTRACT, SEARCH_MENTIONS_RECIPE_ID
        )
        connection.execute(
            """
            UPDATE outcomes
            SET classification = 'observation_admitted_empty', observation_count = 0
            WHERE capture_id = %s
            """,
            (failed_capture,),
        )
    with _app(store, postgres_dsn) as client:
        limited = _outcomes(client, limit=1, order="asc")
        full = _outcomes(client, order="desc")
    _assert_outcomes_envelope(limited.json(), total_matching=3, returned_count=1, limit=1)
    assert limited.json()["outcomes"][0]["attempt_id"] == unresolved
    assert [item["attempt_id"] for item in full.json()["outcomes"]] == [
        admitted_id,
        failed_id,
        unresolved,
    ]
    assert full.json()["outcomes"][0]["capture_outcome"]["classification"] == (
        "observation_admitted"
    )
    assert full.json()["outcomes"][1]["capture_outcome"]["classification"] == (
        "observation_admitted_empty"
    )


def test_search_mentions_outcomes_integrity_vectors(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_frozen(tmp_path, postgres_dsn)
    _ko_attempt, ko_capture = _commit_ko(
        store, "51" * 32, started="2026-08-16T21:37:01.100000Z"
    )
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
    payload = bytearray((store.capture_path(ko_capture) / "capture.json").read_bytes())
    payload[0] ^= 0x01
    (store.capture_path(ko_capture) / "capture.json").write_bytes(bytes(payload))
    with _app(store, postgres_dsn) as client:
        foreign = _outcomes(client)
        history = _history(client)
    _assert_outcomes_409(foreign)
    assert history.status_code == 200
    (store.capture_path(ko_capture) / "capture.json").write_bytes(
        bytes(bytearray(payload[0] ^ 0x01) + payload[1:])
    )

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = observation_count + 1
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, SEARCH_MENTIONS_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        stale = _outcomes(client)
        audit = client.get(f"/v1/attempts/{attempt_id}")
    _assert_outcomes_409(stale)
    assert audit.status_code == 200
    assert audit.json()["capture_outcome"]["observation_count"] == 114

    store_missing = create_store(tmp_path / "underived")
    _commit_mentions_attempt_only(
        store_missing, "b1" * 32, authorized_at="2026-08-20T18:00:00.000000Z"
    )
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, SEARCH_MENTIONS_RECIPE)
        select_provider_recipe(
            connection, MENTIONS_ADAPTER_CONTRACT, SEARCH_MENTIONS_RECIPE_ID
        )
    with _app(store_missing, postgres_dsn) as client:
        missing = _outcomes(client)
    _assert_outcomes_409(missing)

    zero_store = create_store(tmp_path / "zero")
    _zero_attempt, zero_capture = _commit_mentions_no_response(
        zero_store,
        "b2" * 32,
        started="2026-08-20T18:01:01.100000Z",
        authorized_at="2026-08-20T18:01:00.000000Z",
    )
    with connect(postgres_dsn) as connection:
        derive_search_mentions(zero_store, connection)
        connection.execute(
            """
            UPDATE outcomes
            SET classification = 'observation_admitted', observation_count = 0
            WHERE capture_id = %s
            """,
            (zero_capture,),
        )
    with _app(zero_store, postgres_dsn) as client:
        zero_admitted = _outcomes(client)
    _assert_outcomes_409(zero_admitted)

    store_two = create_store(tmp_path / "two")
    two_attempt, two_capture = _commit_mentions(
        store_two, _body(), "c2" * 32, started="2026-08-20T17:36:01.100000Z"
    )
    committed = store_two.capture_path(two_capture) / "COMMITTED"
    hidden = committed.with_name("COMMITTED.hidden")
    committed.rename(hidden)
    parent = store_two.read_attempt(two_attempt)
    assert parent is not None
    store_two.commit_capture(
        mentions_http_capture_document(
            attempt=parent,
            request_started_at="2026-08-20T17:36:02.100000Z",
            transport_ended_at="2026-08-20T17:36:02.400000Z",
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
        derive_search_mentions(store_two, connection)
        select_provider_recipe(
            connection, MENTIONS_ADAPTER_CONTRACT, SEARCH_MENTIONS_RECIPE_ID
        )
    with _app(store_two, postgres_dsn) as client:
        two = _outcomes(client)
    _assert_outcomes_409(two)

    orphan = create_store(tmp_path / "orphan")
    orphan_attempt, _orphan_capture = _commit_mentions(
        orphan,
        _body(),
        "c3" * 32,
        started="2026-08-20T18:02:01.100000Z",
        authorized_at="2026-08-20T18:02:00.000000Z",
    )
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, NULL, %s, 'authorized_unresolved', 0)
            """,
            (orphan_attempt, SEARCH_MENTIONS_RECIPE_ID),
        )
    with _app(orphan, postgres_dsn) as client:
        missing_capture = _outcomes(client)
    _assert_outcomes_409(missing_capture)


def test_search_mentions_outcomes_does_not_mutate(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare_frozen(tmp_path, postgres_dsn)
    before_ops = list(store.recorded_ops)
    before_pg = _xmin_snapshot(postgres_dsn)
    with _app(store, postgres_dsn) as client:
        assert _outcomes(client).status_code == 200
        assert _history(client).status_code == 200
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


def test_search_mentions_outcomes_tie_break(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "tie")
    authorized = "2026-08-20T18:00:00.000000Z"
    first = _commit_mentions_attempt_only(store, "aa" * 32, authorized_at=authorized)
    second = _commit_mentions_attempt_only(store, "bb" * 32, authorized_at=authorized)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        select_provider_recipe(
            connection, MENTIONS_ADAPTER_CONTRACT, SEARCH_MENTIONS_RECIPE_ID
        )
    expected = sorted((first, second))
    with _app(store, postgres_dsn) as client:
        ascending = _outcomes(client, order="asc")
        descending = _outcomes(client, order="desc", limit=1)
    assert ascending.status_code == 200
    assert [item["attempt_id"] for item in ascending.json()["outcomes"]] == expected
    assert descending.status_code == 200
    _assert_outcomes_envelope(
        descending.json(), total_matching=2, returned_count=1, limit=1, order="desc"
    )
    assert descending.json()["outcomes"][0]["attempt_id"] == expected[-1]


def test_search_mentions_outcomes_remediation_409s(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_frozen(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE provider_recipes
            SET provider = 'acme'
            WHERE derivation_version_id = %s
            """,
            (SEARCH_MENTIONS_RECIPE_ID,),
        )
    with _app(store, postgres_dsn) as client:
        wrong_provider = _outcomes(client, "not-measured")
    _assert_outcomes_409(wrong_provider)

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE provider_recipes
            SET provider = 'dataforseo'
            WHERE derivation_version_id = %s
            """,
            (SEARCH_MENTIONS_RECIPE_ID,),
        )
        connection.execute(
            """
            UPDATE observation_envelopes
            SET attempt_id = %s
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            ("aa" * 32, capture_id, SEARCH_MENTIONS_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        envelope_attempt = _outcomes(client)
    _assert_outcomes_409(envelope_attempt)

    _damage_attempt_manifest(store, attempt_id)
    with _app(store, postgres_dsn) as client:
        drifted = _outcomes(client)
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


def test_search_mentions_holdings_empty_closed_query_and_openapi(tmp_path: Path) -> None:
    store = create_store(tmp_path / "empty")
    with _holdings_app(store) as client:
        empty = _holdings(client)
        extra = _holdings(client, requested_keyword=KEYWORD)
        pin = _holdings(client, derivation_version_id="ab" * 32)
        extra_offset = _holdings(client, offset=0)
        extra_cursor = _holdings(client, cursor="next")
        bad_limit = _holdings(client, limit=0)
        high_limit = _holdings(client, limit=101)
        bad_order = _holdings(client, order="sideways")
        spec = client.get("/api/v1/openapi.json").json()
    assert empty.status_code == 200
    _assert_holdings_envelope(empty.json(), total_matching=0, returned_count=0)
    for response in (extra, pin, extra_offset, extra_cursor, bad_limit, high_limit, bad_order):
        assert response.status_code == 422
        assert "holdings" not in response.json()
    envelope, item_schema, request_schema = _holdings_route_schemas(spec, HOLDINGS)
    env_props = envelope["properties"]
    item_props = item_schema["properties"]
    assert env_props["total_matching"]["minimum"] == 0
    assert env_props["returned_count"]["minimum"] == 0
    assert env_props["limit"]["minimum"] == 1
    assert env_props["limit"]["maximum"] == 100
    assert item_props["attempt_count"]["minimum"] == 1
    assert item_props["capture_count"]["minimum"] == 0
    assert item_props["unresolved_count"]["minimum"] == 0
    assert "minimum" in str(item_props["first_authorized_at"].get("description", "")).lower()
    assert "maximum" in str(item_props["last_authorized_at"].get("description", "")).lower()
    started = str(item_props["first_request_started_at"].get("description", "")).lower()
    assert "null" in started and "capture_count" in started
    unresolved = str(item_props["unresolved_count"].get("description", "")).lower()
    assert "not definitely unsent" in unresolved
    empty = str(env_props["total_matching"].get("description", "")).lower()
    assert "unselected" in empty or "recipe" in empty
    request_text = json.dumps(request_schema).lower()
    assert (
        "not holdings list pagination" in request_text
        or "not an outcomes cursor" in request_text
    )
    assert "search_after_token" in request_text
    assert set(request_schema["required"]) == MENTIONS_HOLDINGS_REQUEST_KEYS
    item_text = json.dumps(item_schema).lower()
    assert "search_after_token" in item_text
    scoped = json.dumps({"envelope": envelope, "item": item_schema}).lower()
    assert "strategy" in scoped and "cadence" in scoped


def test_search_mentions_holdings_grouping_scope_order_and_token(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path / "inventory")
    first = _commit_mentions_keyword(
        store, "a1" * 32, keyword=KEYWORD, authorized_at="2026-08-20T17:36:00.000000Z"
    )
    _commit_mentions_no_response(
        store,
        "a2" * 32,
        started="2026-08-20T17:37:01.100000Z",
        authorized_at="2026-08-20T17:37:00.000000Z",
    )
    later = _commit_mentions_keyword(
        store, "a3" * 32, keyword="alpha mention", authorized_at="2026-08-20T17:38:00.000000Z"
    )
    assert first
    assert later
    with _holdings_app(store) as client:
        response = _holdings(client, order="asc")
        limited = _holdings(client, limit=1, order="desc")
    assert response.status_code == 200
    body = response.json()
    items = body["holdings"]
    assert isinstance(items, list)
    assert [item["requested_keyword"] for item in items] == ["alpha mention", KEYWORD]
    grouped = items[1]
    assert grouped["request"]["keyword"] == KEYWORD
    assert grouped["request"]["limit"] == 5
    assert grouped["request"]["offset"] == 0
    assert grouped["request"]["search_scope"] == ["answer"]
    assert set(grouped["request"]) == MENTIONS_HOLDINGS_REQUEST_KEYS
    assert grouped["attempt_count"] == 2
    assert grouped["capture_count"] == 1
    assert grouped["unresolved_count"] == 1
    assert "search_after_token" not in grouped
    _assert_holdings_envelope(body, total_matching=2, returned_count=2)
    _assert_holdings_envelope(
        limited.json(), total_matching=2, returned_count=1, limit=1, order="desc"
    )

    def _split_scope(document: dict[str, object], attempt_id: str) -> dict[str, object]:
        raw = document["parameters"]
        assert isinstance(raw, Mapping)
        parameters = dict(raw)
        targets = parameters["target"]
        assert isinstance(targets, list)
        first_target = targets[0]
        assert isinstance(first_target, Mapping)
        target = dict(first_target)
        target["search_scope"] = ["answer"] if attempt_id == first else ["question"]
        parameters["target"] = [target]
        return {**document, "parameters": parameters}

    scoped = _OverrideAttemptStore(store, _split_scope)
    with _holdings_app(scoped) as client:
        ordered = _holdings(client, order="asc")
        reversed_page = _holdings(client, order="desc", limit=1)
    assert ordered.status_code == 200
    scopes = [
        tuple(item["request"]["search_scope"])
        for item in ordered.json()["holdings"]
        if item["requested_keyword"] == KEYWORD
    ]
    assert scopes == [("answer",), ("question",)]
    assert reversed_page.json()["holdings"][0]["request"]["search_scope"] == ["question"]


def test_search_mentions_holdings_integrity_and_dsn(tmp_path: Path) -> None:
    store = create_store(tmp_path / "integrity")
    _commit_mentions_attempt_only(
        store, "b1" * 32, authorized_at="2026-08-20T17:36:00.000000Z"
    )
    sandbox = _commit_sandbox(store)
    _damage_attempt_manifest(store, sandbox)
    with _holdings_app(store) as client:
        _assert_holdings_409(_holdings(client, limit=1))

    clean = create_store(tmp_path / "clean")
    attempt_id = _commit_mentions_attempt_only(
        clean, "b2" * 32, authorized_at="2026-08-20T17:36:00.000000Z"
    )
    with _holdings_app(clean, "postgresql://127.0.0.1:1/observatory_holdings_missing") as down:
        healthy = _holdings(down)
    assert healthy.status_code == 200
    assert healthy.json()["total_matching"] == 1
    wrong = _OverrideAttemptStore(
        clean, lambda document, _id: {**document, "provider": "acme"}
    )
    with _holdings_app(wrong) as client:
        _assert_holdings_409(_holdings(client))
    def _empty_target(document: dict[str, object], _id: str) -> dict[str, object]:
        raw = document["parameters"]
        assert isinstance(raw, Mapping)
        return {**document, "parameters": {**dict(raw), "target": []}}

    malformed = _OverrideAttemptStore(clean, _empty_target)
    with _holdings_app(malformed) as client:
        _assert_holdings_409(_holdings(client))
    stored = clean.read_attempt(attempt_id)
    assert stored is not None
    copied = clean.attempt_path(
        str(stored["request_fingerprint"]),
        "2026-08-20T17:36:00.000000Z",
        attempt_id,
    )
    shutil.copytree(
        copied,
        clean.root
        / "attempts"
        / "v1"
        / "ff"
        / "ff"
        / ("ff" * 32)
        / "2026"
        / "08"
        / "20"
        / attempt_id,
    )
    with _holdings_app(clean) as client:
        _assert_holdings_409(_holdings(client, limit=1))

    two = create_store(tmp_path / "two")
    two_attempt, two_capture = _commit_mentions_no_response(
        two,
        "c1" * 32,
        started="2026-08-20T17:36:01.100000Z",
        authorized_at="2026-08-20T17:36:00.000000Z",
    )
    committed = two.capture_path(two_capture) / "COMMITTED"
    hidden = committed.with_name("COMMITTED.hidden")
    committed.rename(hidden)
    parent = two.read_attempt(two_attempt)
    assert parent is not None
    two.commit_capture(
        mentions_http_capture_document(
            attempt=parent,
            request_started_at="2026-08-20T17:36:02.100000Z",
            transport_ended_at="2026-08-20T17:36:02.400000Z",
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
        _assert_holdings_409(_holdings(client, limit=1))

    parent_store = create_store(tmp_path / "parent")
    _parent_attempt, parent_capture = _commit_mentions_no_response(
        parent_store,
        "d1" * 32,
        started="2026-08-20T17:36:01.100000Z",
        authorized_at="2026-08-20T17:36:00.000000Z",
    )
    path = parent_store.capture_path(parent_capture) / "capture.json"
    raw = bytearray(path.read_bytes())
    raw[0] ^= 0x01
    path.write_bytes(bytes(raw))
    with _holdings_app(parent_store) as client:
        _assert_holdings_409(_holdings(client, limit=1))


def test_search_mentions_holdings_token_bearing_capture_is_not_followed(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path / "token")
    body = _body()
    assert b"search_after_token" in body
    _commit_mentions(
        store, body, "c1" * 32, started="2026-08-20T17:36:01.100000Z"
    )
    before = list(store.recorded_ops)
    with _holdings_app(store) as client:
        response = _holdings(client)
    assert response.status_code == 200
    payload = response.json()
    dumped = json.dumps(payload)
    assert "search_after_token" not in dumped
    _assert_holdings_envelope(payload, total_matching=1, returned_count=1)
    item = payload["holdings"][0]
    assert item["request"]["limit"] == 5
    assert item["request"]["offset"] == 0
    assert item["capture_count"] == 1
    assert store.recorded_ops == before


def test_search_mentions_holdings_missing_search_scope_is_409(tmp_path: Path) -> None:
    store = create_store(tmp_path / "scope")
    _commit_mentions_attempt_only(
        store, "c2" * 32, authorized_at="2026-08-20T17:36:00.000000Z"
    )

    def _drop_scope(document: dict[str, object], _id: str) -> dict[str, object]:
        raw = document["parameters"]
        assert isinstance(raw, Mapping)
        parameters = dict(raw)
        targets = parameters["target"]
        assert isinstance(targets, list)
        first_target = targets[0]
        assert isinstance(first_target, Mapping)
        target = dict(first_target)
        del target["search_scope"]
        parameters["target"] = [target]
        return {**document, "parameters": parameters}

    wrapped = _OverrideAttemptStore(store, _drop_scope)
    with _holdings_app(wrapped) as client:
        _assert_holdings_409(_holdings(client))
