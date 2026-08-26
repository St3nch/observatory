"""AI-17: Historical Recipe selection and admitted-history API."""

from __future__ import annotations

import copy
import hashlib
import json
import socket
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient

from observatory.api import create_app
from observatory.capture_event import (
    HISTORICAL_ADAPTER_CONTRACT,
    MENTIONS_ADAPTER_CONTRACT,
    body_ref,
    historical_http_attempt_document,
    historical_http_capture_document,
)
from observatory.dataforseo_ai_optimization_llm_mentions_historical import MONTHLY_KIND
from observatory.dataforseo_ai_optimization_llm_mentions_historical_paid_probe import (
    closed_historical_parameters,
    historical_request_body_bytes,
)
from observatory.dataforseo_keyword_overview import CORE_RECIPE, CORE_RECIPE_ID
from observatory.evidence_store import EvidenceStore, create_store
from observatory.llm_mentions_historical_derive import (
    HISTORICAL_RECIPE,
    HISTORICAL_RECIPE_ID,
    MONTHLY_TABLE,
    UNRETURNED_TABLE,
    derive_llm_mentions_historical,
)
from observatory.llm_mentions_historical_read import (
    CANDIDATE_SQL,
    requested_periods,
)
from observatory.migrate import apply_migrations, connect
from observatory.provider_recipe import (
    IDENTITY_SCHEMA,
    IDENTITY_VERSION,
    TEST_RECIPE,
    TEST_RECIPE_ID,
    observation_identity,
    register_provider_recipe,
    validate_recipe,
)
from observatory.provider_recipe_selection import NOT_SELECTED_SIGNAL, select_provider_recipe
from observatory.settings import Settings

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_ai_optimization_llm_mentions_historical_ai14.json"
)
TM_FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_ai_optimization_target_metrics_ai09.json"
)
KEYWORD = "generative engine optimization"
OTHER_KEYWORD = "other keyword"
DATE_FROM = "2025-08-01"
DATE_TO = "2026-07-31"
HISTORY = "/v1/providers/dataforseo/google/ai-optimization/llm-mentions-historical/history"
OUTCOMES = "/v1/providers/dataforseo/google/ai-optimization/llm-mentions-historical/outcomes"
HOLDINGS = "/v1/providers/dataforseo/google/ai-optimization/llm-mentions-historical/holdings"
INTEGRITY_SIGNAL = "evidence_integrity_failure"
AI14_BODY_SHA256 = "4419daf0b7076625129ab18c6bf3c83905b998c3b3332f2ba6d42c8879b50781"
TM_BODY_SHA256 = "7b6974704f73cff9687986a83ab14ba8ec942ccdbfde359ec7e8fde6bea8eee2"
POINTS: tuple[tuple[int, int, int, int], ...] = (
    (2026, 7, 1353, 428820),
    (2026, 6, 481, 358010),
    (2026, 5, 1449, 1086150),
    (2026, 4, 576, 122950),
    (2026, 3, 1019, 1114570),
    (2026, 2, 418, 178650),
    (2026, 1, 224, 471440),
    (2025, 12, 350, 312600),
    (2025, 11, 202, 43360),
    (2025, 10, 122, 51700),
    (2025, 9, 114, 27770),
    (2025, 8, 75, 23150),
)
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
    "monthly",
}
REQUEST_KEYS = {
    "keyword",
    "match_type",
    "search_filter",
    "search_scope",
    "platform",
    "location_code",
    "language_code",
    "date_from",
    "date_to",
}
IJSON_MAX = 9007199254740991
HEX64_PATTERN = r"^[0-9a-f]{64}$"
READONLY_TABLES = (
    "outcomes",
    "observation_envelopes",
    MONTHLY_TABLE,
    "llm_mentions_historical_result_context",
    UNRETURNED_TABLE,
    "provider_recipe_selections",
    "provider_recipes",
)


@pytest.fixture(autouse=True)
def _no_public_network(monkeypatch: pytest.MonkeyPatch) -> None:
    real = socket.create_connection

    def guarded(address: Any, *args: Any, **kwargs: Any) -> socket.socket:
        host = address[0] if isinstance(address, tuple) else address
        if host not in {"127.0.0.1", "::1", "localhost"}:
            raise AssertionError(f"public-network request forbidden: {host}")
        return real(address, *args, **kwargs)

    monkeypatch.setattr(socket, "create_connection", guarded)
    monkeypatch.delenv("OBSERVATORY_DATAFORSEO_LOGIN", raising=False)
    monkeypatch.delenv("OBSERVATORY_DATAFORSEO_PASSWORD", raising=False)


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


def _items(document: dict[str, Any]) -> list[Any]:
    rows = _result(document)["items"]
    assert isinstance(rows, list)
    return rows


def _commit_complete(
    store: EvidenceStore,
    body: bytes,
    nonce: str,
    *,
    started: str = "2026-08-25T18:32:01.100000Z",
) -> tuple[str, str]:
    parameters = closed_historical_parameters()
    attempt = historical_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at="2026-08-25T18:32:00.000000Z",
        observatory_version="ai17-test-v1",
    )
    attempt_id = store.commit_attempt(
        attempt, request_body=historical_request_body_bytes(parameters)
    )
    ended = started[:20] + "4" + started[21:]
    capture_id = store.commit_capture(
        historical_http_capture_document(
            attempt=attempt,
            request_started_at=started,
            transport_ended_at=ended,
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
            response_headers_at=started[:20] + "2" + started[21:],
            response_body_ended_at=started[:20] + "3" + started[21:],
        ),
        response_body=body,
    )
    return attempt_id, capture_id


def _app(store: EvidenceStore, dsn: str) -> TestClient:
    settings = Settings(
        environment="test",
        database_url=dsn,
        evidence_root=store.root,
        derivation_version_id="unused-fixture-label",
    )
    return TestClient(create_app(settings, store=store))


def _history(
    client: TestClient,
    requested_keyword: str = KEYWORD,
    **query: object,
) -> Any:
    params = {"requested_keyword": requested_keyword, **query}
    return client.get(HISTORY + "?" + urlencode(params, doseq=True))


def _prepare(
    tmp_path: Path,
    postgres_dsn: str,
    *,
    body: bytes | None = None,
    nonce: str = "11" * 32,
    started: str = "2026-08-25T18:32:01.100000Z",
    select: bool = True,
    derive: bool = True,
) -> tuple[EvidenceStore, str, str]:
    store = create_store(tmp_path / f"evidence-{nonce[:8]}")
    attempt_id, capture_id = _commit_complete(
        store, body or _body(), nonce, started=started
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        if derive:
            derive_llm_mentions_historical(store, connection)
        else:
            register_provider_recipe(connection, HISTORICAL_RECIPE)
        if select:
            select_provider_recipe(
                connection, HISTORICAL_ADAPTER_CONTRACT, HISTORICAL_RECIPE_ID
            )
    return store, attempt_id, capture_id


def _wipe_derived(dsn: str) -> None:
    with connect(dsn) as connection:
        connection.execute(f"DELETE FROM {UNRETURNED_TABLE}")
        connection.execute(f"DELETE FROM {MONTHLY_TABLE}")
        connection.execute("DELETE FROM llm_mentions_historical_result_context")
        connection.execute("DELETE FROM observation_envelopes")
        connection.execute("DELETE FROM outcomes")


def _execute_without_fks(dsn: str, statement: str, params: tuple[object, ...]) -> None:
    with connect(dsn) as connection:
        connection.execute("SET session_replication_role = replica")
        connection.execute(statement, params)


def _attempt_dir(store: EvidenceStore, attempt_id: str) -> Path:
    attempt = store.read_attempt(attempt_id)
    assert attempt is not None
    fingerprint = attempt["request_fingerprint"]
    authorized_at = attempt["authorized_at"]
    assert isinstance(fingerprint, str)
    assert isinstance(authorized_at, str)
    return store.attempt_path(fingerprint, authorized_at, attempt_id)


def _monthly_identity(keyword: str, year: int, month: int) -> str:
    return observation_identity(
        {
            "axes": {"requested_keyword": keyword, "year": year, "month": month},
            "observation_kind": MONTHLY_KIND,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        HISTORICAL_RECIPE,
    )


def _second_recipe() -> dict[str, object]:
    document = copy.deepcopy(HISTORICAL_RECIPE)
    document["reconciliation"] = {"rule": "attempt_window_admit_all_returned_periods_v2"}
    return validate_recipe(document)


def _assert_envelope(
    body: dict[str, object],
    *,
    total_matching: int,
    returned_count: int,
    limit: int = 20,
    order: str = "asc",
    resolution: str = "selected",
) -> None:
    assert set(body) == HISTORY_KEYS
    assert body["provider"] == "dataforseo"
    assert body["adapter_contract"] == HISTORICAL_ADAPTER_CONTRACT
    assert body["derivation_version_id"] == HISTORICAL_RECIPE_ID
    assert body["recipe_resolution"] == resolution
    assert body["observation_kinds"] == [MONTHLY_KIND]
    assert body["total_matching"] == total_matching
    assert body["returned_count"] == returned_count
    assert body["limit"] == limit
    assert body["order"] == order
    assert body["has_more"] is (total_matching > returned_count)
    captures = body["captures"]
    assert isinstance(captures, list)
    assert len(captures) == returned_count


def _assert_409(response: Any) -> None:
    assert response.status_code == 409
    assert response.json() == {"detail": INTEGRITY_SIGNAL}
    assert "captures" not in response.json()
    assert "total_matching" not in response.json()


def _resolve_schema(spec: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    current = schema
    seen: set[str] = set()
    while True:
        ref = current.get("$ref")
        if not isinstance(ref, str):
            return current
        assert ref not in seen
        seen.add(ref)
        current = spec["components"]["schemas"][ref.rsplit("/", 1)[-1]]


def _options(spec: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    resolved = _resolve_schema(spec, schema)
    grouped = resolved.get("anyOf") or resolved.get("oneOf")
    if grouped:
        return [_resolve_schema(spec, option) for option in grouped]
    return [resolved]


def _nonnull(spec: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    options = [option for option in _options(spec, schema) if option.get("type") != "null"]
    assert options, schema
    return options


def _assert_closed(schema: dict[str, Any], keys: set[str]) -> dict[str, Any]:
    assert schema.get("additionalProperties") is False
    assert set(schema["required"]) == keys
    assert set(schema["properties"]) == keys
    return schema["properties"]


def _assert_const(spec: dict[str, Any], schema: dict[str, Any], expected: object) -> None:
    for option in _nonnull(spec, schema):
        if option.get("const") == expected or option.get("enum") == [expected]:
            return
    raise AssertionError(f"expected const {expected!r} in {schema!r}")


def _assert_enum(spec: dict[str, Any], schema: dict[str, Any], expected: set[object]) -> None:
    found: set[object] = set()
    for option in _nonnull(spec, schema):
        if "enum" in option:
            found.update(option["enum"])
        if "const" in option:
            found.add(option["const"])
    assert found == expected, (found, schema)


def _assert_int(
    spec: dict[str, Any],
    schema: dict[str, Any],
    *,
    minimum: int,
    maximum: int | None = None,
) -> None:
    ints = [option for option in _nonnull(spec, schema) if option.get("type") == "integer"]
    assert ints, schema
    for option in ints:
        assert option.get("minimum") == minimum, option
        if maximum is not None:
            assert option.get("maximum") == maximum, option


def _assert_string(
    spec: dict[str, Any],
    schema: dict[str, Any],
    *,
    min_length: int | None = None,
    max_length: int | None = None,
    pattern: str | None = None,
) -> None:
    strings = [option for option in _nonnull(spec, schema) if option.get("type") == "string"]
    assert strings, schema
    for option in strings:
        if min_length is not None:
            assert option.get("minLength") == min_length, option
        if max_length is not None:
            assert option.get("maxLength") == max_length, option
        if pattern is not None:
            assert option.get("pattern") == pattern, option


def _param_schema(spec: dict[str, Any], parameter: dict[str, Any]) -> dict[str, Any]:
    return _resolve_schema(spec, parameter.get("schema") or parameter)


def _hex64(spec: dict[str, Any], schema: dict[str, Any]) -> None:
    _assert_string(spec, schema, min_length=64, max_length=64, pattern=HEX64_PATTERN)


def _assert_history_openapi(spec: dict[str, Any]) -> None:
    paths = spec["paths"]
    assert HISTORY in paths
    assert OUTCOMES not in paths
    assert HOLDINGS not in paths
    route = paths[HISTORY]["get"]
    params = {item["name"]: item for item in route["parameters"]}
    assert set(params) == {"requested_keyword", "derivation_version_id", "limit", "order"}
    keyword = params["requested_keyword"]
    assert keyword.get("required") is True
    _assert_string(spec, _param_schema(spec, keyword), min_length=1)
    pin = params["derivation_version_id"]
    assert pin.get("required") in {None, False}
    limit = params["limit"]
    limit_schema = _param_schema(spec, limit)
    assert (limit_schema.get("default") or limit.get("default")) == 20
    assert limit_schema.get("minimum") == 1
    assert limit_schema.get("maximum") == 100
    order = params["order"]
    order_schema = _param_schema(spec, order)
    assert (order_schema.get("default") or order.get("default")) == "asc"
    _assert_enum(spec, order_schema, {"asc", "desc"})
    envelope = _resolve_schema(
        spec, route["responses"]["200"]["content"]["application/json"]["schema"]
    )
    props = _assert_closed(envelope, HISTORY_KEYS)
    _assert_const(spec, props["provider"], "dataforseo")
    _assert_const(spec, props["adapter_contract"], HISTORICAL_ADAPTER_CONTRACT)
    _assert_const(spec, props["derivation_version_id"], HISTORICAL_RECIPE_ID)
    _assert_enum(spec, props["recipe_resolution"], {"selected", "pinned"})
    _assert_int(spec, props["total_matching"], minimum=0)
    kinds_schema = props["observation_kinds"]
    assert kinds_schema.get("minItems") == 1
    assert kinds_schema.get("maxItems") == 1
    prefix = kinds_schema.get("prefixItems")
    assert isinstance(prefix, list) and len(prefix) == 1
    _assert_const(spec, prefix[0], MONTHLY_KIND)
    capture_schema = _resolve_schema(spec, props["captures"]["items"])
    capture_props = _assert_closed(capture_schema, CAPTURE_KEYS)
    _hex64(spec, capture_props["attempt_id"])
    _hex64(spec, capture_props["capture_id"])
    outcome_schema = _resolve_schema(spec, capture_props["capture_outcome"])
    outcome_props = _assert_closed(outcome_schema, {"classification", "observation_count"})
    _assert_enum(
        spec,
        outcome_props["classification"],
        {"observation_admitted", "observation_admitted_empty"},
    )
    _assert_int(spec, outcome_props["observation_count"], minimum=0, maximum=IJSON_MAX)
    request_schema = _resolve_schema(spec, capture_props["request"])
    request_props = _assert_closed(request_schema, REQUEST_KEYS)
    _assert_const(spec, request_props["match_type"], "word_match")
    _assert_const(spec, request_props["search_filter"], "include")
    _assert_const(spec, request_props["platform"], "google")
    _assert_const(spec, request_props["location_code"], 2840)
    _assert_const(spec, request_props["language_code"], "en")
    _assert_const(spec, request_props["date_from"], DATE_FROM)
    _assert_const(spec, request_props["date_to"], DATE_TO)
    assert "items_count" not in request_props
    context_schema = _resolve_schema(spec, capture_props["result_context"])
    context_props = _assert_closed(
        context_schema, {"items_count", "unreturned_requested_periods"}
    )
    _assert_int(spec, context_props["items_count"], minimum=0, maximum=IJSON_MAX)
    period_schema = _resolve_schema(
        spec, context_props["unreturned_requested_periods"]["items"]
    )
    period_props = _assert_closed(period_schema, {"year", "month"})
    _assert_int(spec, period_props["year"], minimum=1, maximum=9999)
    _assert_int(spec, period_props["month"], minimum=1, maximum=12)
    monthly_schema = _resolve_schema(spec, capture_props["monthly"]["items"])
    monthly_props = _assert_closed(
        monthly_schema,
        {
            "observation_kind",
            "within_capture_identity",
            "requested_keyword",
            "year",
            "month",
            "mentions",
            "ai_search_volume",
        },
    )
    _hex64(spec, monthly_props["within_capture_identity"])
    _assert_int(spec, monthly_props["year"], minimum=1, maximum=9999)
    _assert_int(spec, monthly_props["month"], minimum=1, maximum=12)
    _assert_int(spec, monthly_props["mentions"], minimum=0, maximum=IJSON_MAX)
    _assert_int(spec, monthly_props["ai_search_volume"], minimum=0, maximum=IJSON_MAX)
    assert "provider_array_index" not in monthly_props
    assert "is_extra" not in monthly_props
    assert "is_extra" not in period_props
    text = json.dumps(
        {
            "envelope": envelope,
            "capture": capture_schema,
            "outcome": outcome_schema,
            "request": request_schema,
            "context": context_schema,
            "period": period_schema,
            "monthly": monthly_schema,
        }
    ).lower()
    assert "observation_admitted_empty is valid subject-bearing historical history" in text
    assert "never measured" in text
    assert "is_extra" in text and "no is_extra flag exists" in text
    assert "pagination" in text
    assert "data period" in text
    assert "never emits observation_admitted_empty" not in text


def _xmin_snapshot(dsn: str) -> dict[str, list[tuple[object, ...]]]:
    snapshot: dict[str, list[tuple[object, ...]]] = {}
    with connect(dsn) as connection:
        for table in READONLY_TABLES:
            rows = connection.execute(f"SELECT xmin::text, * FROM {table}").fetchall()
            snapshot[table] = sorted(
                rows, key=lambda row: tuple(str(item) for item in row[1:])
            )
    return snapshot


def test_candidate_sql_has_no_classification_predicate() -> None:
    assert "o.classification IN" not in CANDIDATE_SQL
    assert "o.classification IS NOT NULL" not in CANDIDATE_SQL
    assert "WHERE o.classification" not in CANDIDATE_SQL
    assert "LIMIT" not in CANDIDATE_SQL
    assert "LEFT JOIN outcomes" in CANDIDATE_SQL


def test_requested_periods_are_computed_from_dates() -> None:
    computed = requested_periods(DATE_FROM, DATE_TO)
    assert computed[0] == (2025, 8)
    assert computed[-1] == (2026, 7)
    assert len(computed) == 12
    assert requested_periods("2026-01-01", "2026-01-31") == ((2026, 1),)


def test_unselected_recipe_is_503_and_pin_v1_does_not_require_selection(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare(tmp_path, postgres_dsn, select=False)
    with connect(postgres_dsn) as connection:
        selected = connection.execute("SELECT * FROM provider_recipe_selections").fetchall()
    assert selected == []
    with _app(store, postgres_dsn) as client:
        missing = _history(client)
        pinned = _history(client, derivation_version_id=HISTORICAL_RECIPE_ID)
        attempt = client.get(f"/v1/attempts/{attempt_id}")
        pinned_attempt = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={HISTORICAL_RECIPE_ID}"
        )
    assert missing.status_code == 503
    assert missing.json() == {"detail": NOT_SELECTED_SIGNAL}
    assert "captures" not in missing.json()
    assert pinned.status_code == 200
    body = pinned.json()
    _assert_envelope(body, total_matching=1, returned_count=1, resolution="pinned")
    assert body["captures"][0]["capture_id"] == capture_id
    assert attempt.status_code == 503
    assert pinned_attempt.status_code == 200
    assert pinned_attempt.json()["recipe_resolution"] == "pinned"


def test_wrong_unknown_malformed_and_non_v1_pins_are_404(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    second = _second_recipe()
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, CORE_RECIPE)
        register_provider_recipe(connection, TEST_RECIPE)
        register_provider_recipe(connection, second)
        second_id = connection.execute(
            """
            SELECT derivation_version_id FROM provider_recipes
            WHERE adapter_contract = %s AND derivation_version_id <> %s
            """,
            (HISTORICAL_ADAPTER_CONTRACT, HISTORICAL_RECIPE_ID),
        ).fetchone()
    assert second_id is not None
    with _app(store, postgres_dsn) as client:
        wrong = _history(client, derivation_version_id=CORE_RECIPE_ID)
        unknown = _history(client, derivation_version_id="ab" * 32)
        malformed = _history(client, derivation_version_id="not-a-digest")
        test_recipe = _history(client, derivation_version_id=TEST_RECIPE_ID)
        other = _history(client, derivation_version_id=str(second_id[0]))
        empty = client.get(HISTORY)
        blank = _history(client, requested_keyword="")
        attempt_wrong = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={CORE_RECIPE_ID}"
        )
    assert {wrong.status_code, unknown.status_code, malformed.status_code} == {404}
    assert test_recipe.status_code == 404
    assert other.status_code == 404
    assert wrong.json() == {"detail": "not found"}
    assert empty.status_code == 422
    assert blank.status_code == 422
    assert attempt_wrong.status_code == 404
    with connect(postgres_dsn) as connection:
        select_provider_recipe(
            connection, HISTORICAL_ADAPTER_CONTRACT, str(second_id[0])
        )
    with _app(store, postgres_dsn) as client:
        selected_other = _history(client)
        pinned_v1 = _history(client, derivation_version_id=HISTORICAL_RECIPE_ID)
    assert selected_other.status_code == 404
    assert pinned_v1.status_code == 200


def test_tampered_v1_recipe_bytes_are_409(tmp_path: Path, postgres_dsn: str) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE provider_recipes
            SET recipe_canonical_bytes = %s
            WHERE derivation_version_id = %s
            """,
            (b'{"not":"a-recipe"}', HISTORICAL_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_frozen_ai14_projection_openapi_and_no_mutation(
    tmp_path: Path, postgres_dsn: str
) -> None:
    assert hashlib.sha256(_body()).hexdigest() == AI14_BODY_SHA256
    assert hashlib.sha256(TM_FIXTURE.read_bytes()).hexdigest() == TM_BODY_SHA256
    store, attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    before = _xmin_snapshot(postgres_dsn)
    before_ops = list(store.recorded_ops)
    with _app(store, postgres_dsn) as client:
        response = _history(client)
        spec = client.get("/api/v1/openapi.json")
        outcomes = client.get(OUTCOMES)
        holdings = client.get(HOLDINGS)
        attempt = client.get(f"/v1/attempts/{attempt_id}")
    after = _xmin_snapshot(postgres_dsn)
    assert store.recorded_ops == before_ops
    assert before == after
    assert response.status_code == 200
    body = response.json()
    _assert_envelope(body, total_matching=1, returned_count=1)
    capture = body["captures"][0]
    assert set(capture) == CAPTURE_KEYS
    assert capture["attempt_id"] == attempt_id
    assert capture["capture_id"] == capture_id
    assert capture["request"]["keyword"] == KEYWORD
    assert capture["request"]["date_from"] == DATE_FROM
    assert capture["request"]["date_to"] == DATE_TO
    assert capture["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": len(POINTS),
    }
    assert capture["result_context"]["items_count"] == len(POINTS)
    assert capture["result_context"]["unreturned_requested_periods"] == []
    monthly = capture["monthly"]
    projected = [
        (row["year"], row["month"], row["mentions"], row["ai_search_volume"])
        for row in monthly
    ]
    assert projected == sorted(POINTS)
    ordered = [(row["year"], row["month"]) for row in monthly]
    assert ordered == sorted(ordered)
    assert "provider_array_index" not in monthly[0]
    assert "items_count" not in capture["request"]
    assert outcomes.status_code == 404
    assert holdings.status_code == 404
    assert attempt.status_code == 200
    assert attempt.json()["adapter_contract"] == HISTORICAL_ADAPTER_CONTRACT
    assert "monthly" not in attempt.json()
    _assert_history_openapi(spec.json())
    computed = requested_periods(DATE_FROM, DATE_TO)
    assert len(computed) == len(POINTS)
    assert set(computed) == {(year, month) for year, month, _mentions, _volume in POINTS}


def test_admitted_empty_is_valid_history(tmp_path: Path, postgres_dsn: str) -> None:
    empty_doc = _decoded()
    _result(empty_doc)["items"] = []
    _result(empty_doc)["items_count"] = 0
    store, _attempt_id, _capture_id = _prepare(
        tmp_path, postgres_dsn, body=_encode(empty_doc), nonce="12" * 32
    )
    computed = requested_periods(DATE_FROM, DATE_TO)
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    assert response.status_code == 200
    capture = response.json()["captures"][0]
    assert capture["capture_outcome"] == {
        "classification": "observation_admitted_empty",
        "observation_count": 0,
    }
    assert capture["monthly"] == []
    assert capture["result_context"]["items_count"] == 0
    unreturned = [
        (row["year"], row["month"])
        for row in capture["result_context"]["unreturned_requested_periods"]
    ]
    assert unreturned == list(computed)
    assert unreturned != [(2025, 8)] * 12


def test_zero_extra_mixed_and_shuffle(tmp_path: Path, postgres_dsn: str) -> None:
    zero_doc = _decoded()
    _items(zero_doc)[0]["metrics"]["mentions"] = 0
    _items(zero_doc)[0]["metrics"]["ai_search_volume"] = 0
    extra_doc = _decoded()
    extra = {"year": 2026, "month": 8, "metrics": {"mentions": 1, "ai_search_volume": 2}}
    _items(extra_doc).append(extra)
    _result(extra_doc)["items_count"] = 13
    mixed_doc = _decoded()
    del _items(mixed_doc)[-1]
    _items(mixed_doc).append(extra)
    _result(mixed_doc)["items_count"] = 12
    shuffled_doc = _decoded()
    rows = list(_items(shuffled_doc))
    rows.reverse()
    _result(shuffled_doc)["items"] = rows
    cases = (
        ("zero", zero_doc, "13" * 32),
        ("extra", extra_doc, "14" * 32),
        ("mixed", mixed_doc, "15" * 32),
        ("shuffle", shuffled_doc, "16" * 32),
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, HISTORICAL_RECIPE)
        select_provider_recipe(
            connection, HISTORICAL_ADAPTER_CONTRACT, HISTORICAL_RECIPE_ID
        )
    payloads: dict[str, dict[str, Any]] = {}
    for name, document, nonce in cases:
        store = create_store(tmp_path / name)
        _commit_complete(store, _encode(document), nonce)
        with connect(postgres_dsn) as connection:
            derive_llm_mentions_historical(store, connection)
        with _app(store, postgres_dsn) as client:
            payloads[name] = _history(client).json()["captures"][0]
        with connect(postgres_dsn) as connection:
            connection.execute(f"DELETE FROM {UNRETURNED_TABLE}")
            connection.execute(f"DELETE FROM {MONTHLY_TABLE}")
            connection.execute("DELETE FROM llm_mentions_historical_result_context")
            connection.execute("DELETE FROM observation_envelopes")
            connection.execute("DELETE FROM outcomes")
            connection.commit()
            register_provider_recipe(connection, HISTORICAL_RECIPE)
            select_provider_recipe(
                connection, HISTORICAL_ADAPTER_CONTRACT, HISTORICAL_RECIPE_ID
            )
    zero = payloads["zero"]
    zero_row = next(
        row for row in zero["monthly"] if row["year"] == 2026 and row["month"] == 7
    )
    assert zero_row["mentions"] == 0
    assert zero_row["ai_search_volume"] == 0
    assert zero["capture_outcome"]["classification"] == "observation_admitted"
    assert zero["result_context"]["unreturned_requested_periods"] == []
    extra_capture = payloads["extra"]
    extra_periods = {(row["year"], row["month"]) for row in extra_capture["monthly"]}
    assert (2026, 8) in extra_periods
    assert extra_capture["request"]["date_from"] == DATE_FROM
    assert extra_capture["result_context"]["unreturned_requested_periods"] == []
    mixed = payloads["mixed"]
    mixed_months = {(row["year"], row["month"]) for row in mixed["monthly"]}
    assert (2026, 8) in mixed_months
    assert (2025, 8) not in mixed_months
    assert mixed["result_context"]["unreturned_requested_periods"] == [
        {"year": 2025, "month": 8}
    ]
    shuffled = payloads["shuffle"]
    shuffled_order = [(row["year"], row["month"]) for row in shuffled["monthly"]]
    assert shuffled_order == sorted(shuffled_order)


def test_empty_history_and_other_keyword_are_excluded(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, 'observation_admitted_empty', 0)
            """,
            ("99" * 32, "88" * 32, HISTORICAL_RECIPE_ID),
        )
        connection.execute(
            """
            INSERT INTO llm_mentions_historical_result_context (
                capture_id, derivation_version_id, attempt_id,
                requested_keyword, match_type, search_filter, search_scope,
                platform, location_code, language_code, date_from, date_to, items_count
            )
            VALUES (
                %s, %s, %s, %s, 'word_match', 'include', ARRAY['answer'],
                'google', 2840, 'en', %s, %s, 0
            )
            """,
            ("88" * 32, HISTORICAL_RECIPE_ID, "99" * 32, OTHER_KEYWORD, DATE_FROM, DATE_TO),
        )
    with _app(store, postgres_dsn) as client:
        own = _history(client)
        missing = _history(client, requested_keyword="not-measured")
    assert own.status_code == 200
    assert own.json()["captures"][0]["capture_id"] == capture_id
    assert own.json()["total_matching"] == 1
    assert missing.status_code == 200
    assert missing.json()["captures"] == []
    assert missing.json()["total_matching"] == 0


def test_missing_outcome_and_non_admitted_are_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    _execute_without_fks(
        postgres_dsn,
        "DELETE FROM outcomes WHERE capture_id = %s",
        (capture_id,),
    )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))
    _wipe_derived(postgres_dsn)
    store_b, _attempt_b, capture_b = _prepare(
        tmp_path, postgres_dsn, nonce="21" * 32, started="2026-08-25T18:32:02.100000Z"
    )
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE outcomes
            SET classification = 'provider_error', observation_count = 0
            WHERE capture_id = %s
            """,
            (capture_b,),
        )
    with _app(store_b, postgres_dsn) as client:
        _assert_409(_history(client))


def test_admitted_empty_pairings_are_409(tmp_path: Path, postgres_dsn: str) -> None:
    empty_doc = _decoded()
    _result(empty_doc)["items"] = []
    _result(empty_doc)["items_count"] = 0
    store, _attempt_id, capture_id = _prepare(
        tmp_path, postgres_dsn, body=_encode(empty_doc), nonce="22" * 32
    )
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE outcomes
            SET classification = 'observation_admitted', observation_count = 0
            WHERE capture_id = %s
            """,
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))
    _wipe_derived(postgres_dsn)
    store_b, attempt_b, capture_b = _prepare(
        tmp_path,
        postgres_dsn,
        body=_encode(empty_doc),
        nonce="23" * 32,
        started="2026-08-25T18:32:03.100000Z",
    )
    leftover = "ab" * 32
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            INSERT INTO observation_envelopes (
                capture_id, attempt_id, derivation_version_id, provider,
                adapter_contract, observation_kind, within_capture_identity
            )
            VALUES (%s, %s, %s, 'dataforseo', %s, %s, %s)
            """,
            (
                capture_b,
                attempt_b,
                HISTORICAL_RECIPE_ID,
                HISTORICAL_ADAPTER_CONTRACT,
                MONTHLY_KIND,
                leftover,
            ),
        )
    with _app(store_b, postgres_dsn) as client:
        _assert_409(_history(client))
    _wipe_derived(postgres_dsn)
    store_c, attempt_c, capture_c = _prepare(
        tmp_path,
        postgres_dsn,
        body=_encode(empty_doc),
        nonce="25" * 32,
        started="2026-08-25T18:32:04.100000Z",
    )
    leftover_row = _monthly_identity(KEYWORD, 2025, 8)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            INSERT INTO observation_envelopes (
                capture_id, attempt_id, derivation_version_id, provider,
                adapter_contract, observation_kind, within_capture_identity
            )
            VALUES (%s, %s, %s, 'dataforseo', %s, %s, %s)
            """,
            (
                capture_c,
                attempt_c,
                HISTORICAL_RECIPE_ID,
                HISTORICAL_ADAPTER_CONTRACT,
                MONTHLY_KIND,
                leftover_row,
            ),
        )
        connection.execute(
            f"""
            INSERT INTO {MONTHLY_TABLE} (
                capture_id, derivation_version_id, within_capture_identity,
                observation_kind, requested_keyword, year, month,
                mentions, ai_search_volume
            )
            VALUES (%s, %s, %s, %s, %s, 2025, 8, 0, 0)
            """,
            (
                capture_c,
                HISTORICAL_RECIPE_ID,
                leftover_row,
                MONTHLY_KIND,
                KEYWORD,
            ),
        )
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = 1
            WHERE capture_id = %s
            """,
            (capture_c,),
        )
        connection.execute(
            """
            UPDATE llm_mentions_historical_result_context
            SET items_count = 1
            WHERE capture_id = %s
            """,
            (capture_c,),
        )
        connection.execute(
            f"""
            DELETE FROM {UNRETURNED_TABLE}
            WHERE capture_id = %s AND year = 2025 AND month = 8
            """,
            (capture_c,),
        )
    with _app(store_c, postgres_dsn) as client:
        _assert_409(_history(client))


def test_count_envelope_and_unreturned_integrity(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            "UPDATE outcomes SET observation_count = 11 WHERE capture_id = %s",
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))
    with connect(postgres_dsn) as connection:
        connection.execute(
            "UPDATE outcomes SET observation_count = 12 WHERE capture_id = %s",
            (capture_id,),
        )
        connection.execute(
            """
            UPDATE llm_mentions_historical_result_context
            SET items_count = 11 WHERE capture_id = %s
            """,
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE llm_mentions_historical_result_context
            SET items_count = 12 WHERE capture_id = %s
            """,
            (capture_id,),
        )
        identity = connection.execute(
            f"""
            SELECT within_capture_identity FROM {MONTHLY_TABLE}
            WHERE capture_id = %s LIMIT 1
            """,
            (capture_id,),
        ).fetchone()
        assert identity is not None
        connection.execute(
            f"DELETE FROM {MONTHLY_TABLE} WHERE within_capture_identity = %s",
            (identity[0],),
        )
        connection.execute(
            """
            DELETE FROM observation_envelopes
            WHERE within_capture_identity = %s
            """,
            (identity[0],),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))
    _wipe_derived(postgres_dsn)
    dropped_doc = _decoded()
    del _items(dropped_doc)[-1]
    _result(dropped_doc)["items_count"] = 11
    store_b, _attempt_b, capture_b = _prepare(
        tmp_path,
        postgres_dsn,
        body=_encode(dropped_doc),
        nonce="24" * 32,
        started="2026-08-25T18:32:04.100000Z",
    )
    with connect(postgres_dsn) as connection:
        connection.execute(
            f"""
            DELETE FROM {UNRETURNED_TABLE}
            WHERE capture_id = %s AND year = 2025 AND month = 8
            """,
            (capture_b,),
        )
        connection.execute(
            f"""
            INSERT INTO {UNRETURNED_TABLE}
                (capture_id, derivation_version_id, year, month)
            VALUES (%s, %s, 2025, 9)
            """,
            (capture_b, HISTORICAL_RECIPE_ID),
        )
    with _app(store_b, postgres_dsn) as client:
        _assert_409(_history(client))
    assert attempt_id


def test_wrong_envelope_provider_adapter_attempt_kind_are_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, second_attempt, _second_capture = _prepare(
        tmp_path, postgres_dsn, nonce="31" * 32, started="2026-08-25T18:32:05.100000Z"
    )
    store_b, _first_attempt, first_capture = _prepare(
        tmp_path, postgres_dsn, nonce="32" * 32, started="2026-08-25T18:32:01.100000Z"
    )
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE observation_envelopes SET provider = 'other'
            WHERE capture_id = %s
            """,
            (first_capture,),
        )
    with _app(store_b, postgres_dsn) as client:
        _assert_409(_history(client))
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE observation_envelopes SET provider = 'dataforseo'
            WHERE capture_id = %s
            """,
            (first_capture,),
        )
        connection.execute(
            """
            UPDATE observation_envelopes SET adapter_contract = %s
            WHERE capture_id = %s
            """,
            (MENTIONS_ADAPTER_CONTRACT, first_capture),
        )
    with _app(store_b, postgres_dsn) as client:
        _assert_409(_history(client))
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE observation_envelopes SET adapter_contract = %s
            WHERE capture_id = %s
            """,
            (HISTORICAL_ADAPTER_CONTRACT, first_capture),
        )
        connection.execute(
            """
            UPDATE observation_envelopes SET attempt_id = %s
            WHERE capture_id = %s
            """,
            (second_attempt, first_capture),
        )
    with _app(store_b, postgres_dsn) as client:
        _assert_409(_history(client))
    _wipe_derived(postgres_dsn)
    store_c, _attempt_c, capture_c = _prepare(
        tmp_path, postgres_dsn, nonce="33" * 32, started="2026-08-25T18:32:06.100000Z"
    )
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            INSERT INTO observation_envelopes (
                capture_id, attempt_id, derivation_version_id, provider,
                adapter_contract, observation_kind, within_capture_identity
            )
            SELECT capture_id, attempt_id, derivation_version_id, provider,
                   adapter_contract,
                   'dataforseo.google.ai_optimization.llm_mentions_historical.unknown.v1',
                   repeat('ee', 32)
            FROM observation_envelopes
            WHERE capture_id = %s
            LIMIT 1
            """,
            (capture_c,),
        )
    with _app(store_c, postgres_dsn) as client:
        _assert_409(_history(client))
    _wipe_derived(postgres_dsn)
    store_d, _attempt_d, capture_d = _prepare(
        tmp_path, postgres_dsn, nonce="34" * 32, started="2026-08-25T18:32:07.100000Z"
    )
    with connect(postgres_dsn) as connection:
        row = connection.execute(
            f"""
            SELECT within_capture_identity FROM {MONTHLY_TABLE}
            WHERE capture_id = %s LIMIT 1
            """,
            (capture_d,),
        ).fetchone()
        assert row is not None
        old_identity = str(row[0])
    _execute_without_fks(
        postgres_dsn,
        """
        UPDATE observation_envelopes
        SET within_capture_identity = repeat('aa', 32)
        WHERE capture_id = %s AND within_capture_identity = %s
        """,
        (capture_d, old_identity),
    )
    _execute_without_fks(
        postgres_dsn,
        f"""
        UPDATE {MONTHLY_TABLE}
        SET within_capture_identity = repeat('aa', 32)
        WHERE capture_id = %s AND within_capture_identity = %s
        """,
        (capture_d, old_identity),
    )
    with _app(store_d, postgres_dsn) as client:
        _assert_409(_history(client))
    _wipe_derived(postgres_dsn)
    store_e, _attempt_e, capture_e = _prepare(
        tmp_path, postgres_dsn, nonce="35" * 32, started="2026-08-25T18:32:08.100000Z"
    )
    with connect(postgres_dsn) as connection:
        connection.execute(
            f"""
            UPDATE {MONTHLY_TABLE}
            SET requested_keyword = %s
            WHERE capture_id = %s
            """,
            (OTHER_KEYWORD, capture_e),
        )
    with _app(store_e, postgres_dsn) as client:
        _assert_409(_history(client))
    _wipe_derived(postgres_dsn)
    store_f, _attempt_f, capture_f = _prepare(
        tmp_path, postgres_dsn, nonce="36" * 32, started="2026-08-25T18:32:09.100000Z"
    )
    identity = None
    with connect(postgres_dsn) as connection:
        row = connection.execute(
            f"""
            SELECT within_capture_identity FROM {MONTHLY_TABLE}
            WHERE capture_id = %s LIMIT 1
            """,
            (capture_f,),
        ).fetchone()
        assert row is not None
        identity = str(row[0])
    _execute_without_fks(
        postgres_dsn,
        """
        DELETE FROM observation_envelopes
        WHERE capture_id = %s AND within_capture_identity = %s
        """,
        (capture_f, identity),
    )
    with _app(store_f, postgres_dsn) as client:
        _assert_409(_history(client))
    assert store is not None


def test_foreign_attempt_and_evidence_damage_are_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "two")
    first_attempt, first_capture = _commit_complete(
        store, _body(), "41" * 32, started="2026-08-25T18:32:01.100000Z"
    )
    second_attempt, _second_capture = _commit_complete(
        store, _body(), "42" * 32, started="2026-08-25T18:32:02.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_llm_mentions_historical(store, connection)
        select_provider_recipe(
            connection, HISTORICAL_ADAPTER_CONTRACT, HISTORICAL_RECIPE_ID
        )
        connection.execute("SET session_replication_role = replica")
        connection.execute(
            """
            UPDATE llm_mentions_historical_result_context
            SET attempt_id = %s WHERE capture_id = %s
            """,
            (second_attempt, first_capture),
        )
        connection.execute(
            """
            UPDATE outcomes SET attempt_id = %s WHERE capture_id = %s
            """,
            (second_attempt, first_capture),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client, limit=100))
    _wipe_derived(postgres_dsn)
    store_b, attempt_b, capture_b = _prepare(
        tmp_path, postgres_dsn, nonce="43" * 32, started="2026-08-25T18:33:01.100000Z"
    )
    body_path = store_b.capture_path(capture_b) / "response.body"
    flipped = bytearray(body_path.read_bytes())
    flipped[0] ^= 0x01
    body_path.write_bytes(bytes(flipped))
    with _app(store_b, postgres_dsn) as client:
        _assert_409(_history(client))
    _wipe_derived(postgres_dsn)
    store_c, attempt_c, capture_c = _prepare(
        tmp_path, postgres_dsn, nonce="44" * 32, started="2026-08-25T18:34:01.100000Z"
    )
    manifest = store_c.capture_path(capture_c) / "capture.json"
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    with _app(store_c, postgres_dsn) as client:
        _assert_409(_history(client, limit=1))
    _wipe_derived(postgres_dsn)
    store_d, attempt_d, capture_d = _prepare(
        tmp_path, postgres_dsn, nonce="45" * 32, started="2026-08-25T18:35:01.100000Z"
    )
    (store_d.capture_path(capture_d) / "COMMITTED").unlink()
    with _app(store_d, postgres_dsn) as client:
        _assert_409(_history(client))
    _wipe_derived(postgres_dsn)
    store_e, attempt_e, _capture_e = _prepare(
        tmp_path, postgres_dsn, nonce="46" * 32, started="2026-08-25T18:36:01.100000Z"
    )
    attempt_manifest = _attempt_dir(store_e, attempt_e) / "attempt.json"
    attempt_raw = bytearray(attempt_manifest.read_bytes())
    attempt_raw[0] ^= 0x01
    attempt_manifest.write_bytes(bytes(attempt_raw))
    with _app(store_e, postgres_dsn) as client:
        _assert_409(_history(client))
    _wipe_derived(postgres_dsn)
    store_f, attempt_f, _capture_f = _prepare(
        tmp_path, postgres_dsn, nonce="47" * 32, started="2026-08-25T18:37:01.100000Z"
    )
    (_attempt_dir(store_f, attempt_f) / "COMMITTED").unlink()
    with _app(store_f, postgres_dsn) as client:
        _assert_409(_history(client))
    assert first_attempt != second_attempt
    assert attempt_b
    assert attempt_c
    assert attempt_d
    assert attempt_e
    assert attempt_f


def test_verify_before_limit_and_outer_order(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "order")
    _commit_complete(store, _body(), "51" * 32, started="2026-08-25T18:32:01.100000Z")
    later_attempt, later_capture = _commit_complete(
        store, _body(), "52" * 32, started="2026-08-25T18:32:02.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_llm_mentions_historical(store, connection)
        select_provider_recipe(
            connection, HISTORICAL_ADAPTER_CONTRACT, HISTORICAL_RECIPE_ID
        )
    with _app(store, postgres_dsn) as client:
        full = _history(client, limit=100).json()
        limited = _history(client, limit=1, order="asc").json()
        descending = _history(client, limit=1, order="desc").json()
    _assert_envelope(full, total_matching=2, returned_count=2, limit=100)
    started = [item["request_started_at"] for item in full["captures"]]
    assert started == sorted(started)
    monthly = full["captures"][1]["monthly"]
    assert [(row["year"], row["month"]) for row in monthly] == sorted(
        (row["year"], row["month"]) for row in monthly
    )
    _assert_envelope(limited, total_matching=2, returned_count=1, limit=1)
    _assert_envelope(descending, total_matching=2, returned_count=1, limit=1, order="desc")
    assert descending["captures"][0]["request_started_at"] >= limited["captures"][0][
        "request_started_at"
    ]
    desc_monthly = descending["captures"][0]["monthly"]
    assert [(row["year"], row["month"]) for row in desc_monthly] == sorted(
        (row["year"], row["month"]) for row in desc_monthly
    )
    manifest = store.capture_path(later_capture) / "capture.json"
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client, limit=1, order="asc"))
    assert later_attempt


def test_request_context_disagreement_is_409(tmp_path: Path, postgres_dsn: str) -> None:
    store, _attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE llm_mentions_historical_result_context
            SET date_from = '2024-01-01'
            WHERE capture_id = %s
            """,
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))
