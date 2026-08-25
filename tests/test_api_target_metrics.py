"""AI-12: Target Metrics Recipe selection and admitted-history API."""

from __future__ import annotations

import copy
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
    MENTIONS_ADAPTER_CONTRACT,
    TARGET_METRICS_ADAPTER_CONTRACT,
    body_ref,
    target_metrics_http_attempt_document,
    target_metrics_http_capture_document,
)
from observatory.dataforseo_ai_optimization_target_metrics import (
    SOURCE_DOMAIN_KIND,
    TOTAL_KIND,
)
from observatory.dataforseo_ai_optimization_target_metrics_paid_probe import (
    closed_target_metrics_parameters,
    target_metrics_request_body_bytes,
)
from observatory.dataforseo_keyword_overview import CORE_RECIPE, CORE_RECIPE_ID
from observatory.evidence_store import EvidenceStore, create_store
from observatory.migrate import apply_migrations, connect
from observatory.provider_recipe import (
    TEST_RECIPE,
    TEST_RECIPE_ID,
    register_provider_recipe,
    validate_recipe,
)
from observatory.provider_recipe_selection import NOT_SELECTED_SIGNAL, select_provider_recipe
from observatory.settings import Settings
from observatory.target_metrics_derive import (
    TARGET_METRICS_RECIPE,
    TARGET_METRICS_RECIPE_ID,
    derive_target_metrics,
)

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_ai_optimization_target_metrics_ai09.json"
)
KEYWORD = "generative engine optimization"
HISTORY = "/v1/providers/dataforseo/google/ai-optimization/target-metrics/history"
OUTCOMES = "/v1/providers/dataforseo/google/ai-optimization/target-metrics/outcomes"
HOLDINGS = "/v1/providers/dataforseo/google/ai-optimization/target-metrics/holdings"
INTEGRITY_SIGNAL = "evidence_integrity_failure"
SOURCE_DOMAINS: tuple[tuple[str, int, int], ...] = (
    ("www.youtube.com", 1641, 1182010),
    ("www.reddit.com", 750, 326780),
    ("www.linkedin.com", 395, 445730),
    ("www.coursera.org", 308, 80860),
    ("www.semrush.com", 262, 280590),
    ("digitalmarketinginstitute.com", 249, 49930),
    ("clutch.co", 234, 222900),
    ("en.wikipedia.org", 217, 245010),
    ("firstpagesage.com", 195, 256380),
    ("thriveagency.com", 164, 97420),
)
TOTAL_MENTIONS = 3061
TOTAL_VOLUME = 2336840
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
    "total",
    "source_domains",
}
REQUEST_KEYS = {
    "keyword",
    "match_type",
    "search_filter",
    "search_scope",
    "platform",
    "location_code",
    "language_code",
    "internal_list_limit",
}
CONTEXT_KEYS = {
    "total_count",
    "result_offset",
    "items_count",
    "items_state",
    "location",
    "language",
    "platform",
    "sources_domain_count",
    "search_results_domain",
    "brand_entities_title",
    "brand_entities_category",
}
GROUPING_KEYS = {
    "key",
    "mentions",
    "ai_search_volume",
    "provider_array_index",
    "row_count",
}
FAMILY_KEYS = {"state", "count"}
FIELD_STATES = {"absent", "json_null", "stated"}
IJSON_MAX = 9007199254740991
HEX64_PATTERN = r"^[0-9a-f]{64}$"
TOTAL_FACT_KEYS = {
    "observation_kind",
    "within_capture_identity",
    "requested_keyword",
    "mentions",
    "ai_search_volume",
}
SOURCE_FACT_KEYS = {
    "observation_kind",
    "within_capture_identity",
    "requested_keyword",
    "domain",
    "mentions",
    "ai_search_volume",
    "provider_array_index",
}
READONLY_TABLES = (
    "outcomes",
    "observation_envelopes",
    "target_metrics_totals",
    "target_metrics_source_domains",
    "target_metrics_result_context",
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


def _body() -> bytes:
    return FIXTURE.read_bytes()


def _parameters(*, keyword: str = KEYWORD) -> dict[str, object]:
    return closed_target_metrics_parameters(keyword=keyword)


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


def _agg(document: dict[str, Any]) -> dict[str, Any]:
    metrics = _result(document)["aggregated_metrics"]
    assert isinstance(metrics, dict)
    return metrics


def _row(key: object, mentions: int = 1, volume: int = 2) -> dict[str, object]:
    return {"key": key, "mentions": mentions, "ai_search_volume": volume}


def _commit_complete(
    store: EvidenceStore,
    body: bytes,
    nonce: str,
    *,
    keyword: str = KEYWORD,
    started: str = "2026-08-24T03:09:01.100000Z",
) -> tuple[str, str]:
    parameters = _parameters(keyword=keyword)
    attempt = target_metrics_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at="2026-08-24T03:09:00.000000Z",
        observatory_version="ai12-test-v1",
    )
    attempt_id = store.commit_attempt(
        attempt, request_body=target_metrics_request_body_bytes(parameters)
    )
    ended = started[:20] + "4" + started[21:]
    capture_id = store.commit_capture(
        target_metrics_http_capture_document(
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
    started: str = "2026-08-24T03:09:01.100000Z",
    keyword: str = KEYWORD,
    select: bool = True,
    derive: bool = True,
) -> tuple[EvidenceStore, str, str]:
    store = create_store(tmp_path / f"evidence-{nonce[:8]}")
    attempt_id, capture_id = _commit_complete(
        store, body or _body(), nonce, keyword=keyword, started=started
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        if derive:
            derive_target_metrics(store, connection)
        else:
            register_provider_recipe(connection, TARGET_METRICS_RECIPE)
        if select:
            select_provider_recipe(
                connection, TARGET_METRICS_ADAPTER_CONTRACT, TARGET_METRICS_RECIPE_ID
            )
    return store, attempt_id, capture_id


def _second_recipe() -> dict[str, object]:
    document = copy.deepcopy(TARGET_METRICS_RECIPE)
    document["reconciliation"] = {"rule": "attempt_grouping_key_singleton_v2"}
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
    assert body["adapter_contract"] == TARGET_METRICS_ADAPTER_CONTRACT
    assert body["derivation_version_id"] == TARGET_METRICS_RECIPE_ID
    assert body["recipe_resolution"] == resolution
    assert body["observation_kinds"] == [TOTAL_KIND, SOURCE_DOMAIN_KIND]
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
    assert "returned_count" not in response.json()
    assert "has_more" not in response.json()


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


def _assert_nullable_int(
    spec: dict[str, Any],
    schema: dict[str, Any],
    *,
    minimum: int,
    maximum: int,
) -> None:
    options = _options(spec, schema)
    types = {option.get("type") for option in options}
    assert "null" in types, schema
    ints = [option for option in options if option.get("type") == "integer"]
    assert ints, schema
    for option in ints:
        assert option.get("minimum") == minimum, option
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
    assert limit.get("required") in {None, False}
    limit_schema = _param_schema(spec, limit)
    assert (limit_schema.get("default") or limit.get("default")) == 20
    assert limit_schema.get("minimum") == 1
    assert limit_schema.get("maximum") == 100
    order = params["order"]
    assert order.get("required") in {None, False}
    order_schema = _param_schema(spec, order)
    assert (order_schema.get("default") or order.get("default")) == "asc"
    _assert_enum(spec, order_schema, {"asc", "desc"})

    envelope = _resolve_schema(
        spec,
        route["responses"]["200"]["content"]["application/json"]["schema"],
    )
    props = _assert_closed(envelope, HISTORY_KEYS)
    _assert_const(spec, props["provider"], "dataforseo")
    _assert_const(spec, props["adapter_contract"], TARGET_METRICS_ADAPTER_CONTRACT)
    _assert_const(spec, props["derivation_version_id"], TARGET_METRICS_RECIPE_ID)
    _assert_enum(spec, props["recipe_resolution"], {"selected", "pinned"})
    _assert_int(spec, props["total_matching"], minimum=0)
    _assert_int(spec, props["returned_count"], minimum=0)
    _assert_int(spec, props["limit"], minimum=1, maximum=100)
    _assert_enum(spec, props["order"], {"asc", "desc"})
    kinds_schema = props["observation_kinds"]
    assert kinds_schema.get("minItems") == 2
    assert kinds_schema.get("maxItems") == 2
    prefix = kinds_schema.get("prefixItems")
    assert isinstance(prefix, list) and len(prefix) == 2
    _assert_const(spec, prefix[0], TOTAL_KIND)
    _assert_const(spec, prefix[1], SOURCE_DOMAIN_KIND)
    text = json.dumps({"envelope": envelope, "components": spec["components"]}).lower()
    assert "admitted" in text and "capture" in text
    assert "never measured" in text
    assert "failed" in text
    assert "observation envelope" in text or "observation envelopes" in text
    assert "pagination" in text
    assert "truncation" in text or "truncated" in text
    assert "integrity" in text
    assert "provider update" in text or "data period" in text
    assert "observation_admitted_empty" in text

    capture_schema = _resolve_schema(spec, props["captures"]["items"])
    capture_props = _assert_closed(capture_schema, CAPTURE_KEYS)
    _assert_const(spec, capture_props["provider"], "dataforseo")
    _assert_const(spec, capture_props["adapter_contract"], TARGET_METRICS_ADAPTER_CONTRACT)
    _assert_const(spec, capture_props["derivation_version_id"], TARGET_METRICS_RECIPE_ID)
    _hex64(spec, capture_props["attempt_id"])
    _hex64(spec, capture_props["capture_id"])
    outcome_schema = _resolve_schema(spec, capture_props["capture_outcome"])
    outcome_props = _assert_closed(outcome_schema, {"classification", "observation_count"})
    _assert_const(spec, outcome_props["classification"], "observation_admitted")
    _assert_int(spec, outcome_props["observation_count"], minimum=1, maximum=IJSON_MAX)

    request_schema = _resolve_schema(spec, capture_props["request"])
    request_props = _assert_closed(request_schema, REQUEST_KEYS)
    _assert_string(spec, request_props["keyword"], min_length=1)
    for name, value in (
        ("match_type", "word_match"),
        ("search_filter", "include"),
        ("platform", "google"),
        ("location_code", 2840),
        ("language_code", "en"),
        ("internal_list_limit", 10),
    ):
        _assert_const(spec, request_props[name], value)
    scope_schema = request_props["search_scope"]
    assert scope_schema.get("minItems") == 1
    assert scope_schema.get("maxItems") == 1
    items = scope_schema.get("items")
    if items is None:
        prefix_items = scope_schema.get("prefixItems")
        assert isinstance(prefix_items, list) and prefix_items
        items = prefix_items[0]
    _assert_const(spec, items, "answer")

    context_schema = _resolve_schema(spec, capture_props["result_context"])
    context_props = _assert_closed(context_schema, CONTEXT_KEYS)
    for zero_name in ("total_count", "result_offset", "items_count"):
        _assert_const(spec, context_props[zero_name], 0)
    _assert_enum(spec, context_props["items_state"], FIELD_STATES)
    _assert_int(spec, context_props["sources_domain_count"], minimum=0, maximum=IJSON_MAX)
    location_schema = _resolve_schema(spec, context_props["location"])
    location_props = _assert_closed(location_schema, GROUPING_KEYS)
    _assert_int(spec, location_props["key"], minimum=0, maximum=IJSON_MAX)
    for grouping_name in ("location", "language", "platform"):
        grouping = _resolve_schema(spec, context_props[grouping_name])
        grouping_props = _assert_closed(grouping, GROUPING_KEYS)
        _assert_const(spec, grouping_props["provider_array_index"], 0)
        _assert_const(spec, grouping_props["row_count"], 1)
        _assert_int(spec, grouping_props["mentions"], minimum=0, maximum=IJSON_MAX)
        _assert_int(spec, grouping_props["ai_search_volume"], minimum=0, maximum=IJSON_MAX)
    for name in ("language", "platform"):
        grouping = _resolve_schema(spec, context_props[name])
        _assert_string(spec, grouping["properties"]["key"], min_length=1)
    for family_name in (
        "search_results_domain",
        "brand_entities_title",
        "brand_entities_category",
    ):
        family_schema = _resolve_schema(spec, context_props[family_name])
        family_props = _assert_closed(family_schema, FAMILY_KEYS)
        _assert_enum(spec, family_props["state"], FIELD_STATES)
        _assert_nullable_int(spec, family_props["count"], minimum=0, maximum=IJSON_MAX)

    total_schema = _resolve_schema(spec, capture_props["total"])
    total_props = _assert_closed(total_schema, TOTAL_FACT_KEYS)
    _assert_const(spec, total_props["observation_kind"], TOTAL_KIND)
    _hex64(spec, total_props["within_capture_identity"])
    _assert_string(spec, total_props["requested_keyword"], min_length=1)
    for metric in ("mentions", "ai_search_volume"):
        _assert_int(spec, total_props[metric], minimum=0, maximum=IJSON_MAX)
    source_schema = _resolve_schema(spec, capture_props["source_domains"]["items"])
    source_props = _assert_closed(source_schema, SOURCE_FACT_KEYS)
    _assert_const(spec, source_props["observation_kind"], SOURCE_DOMAIN_KIND)
    _hex64(spec, source_props["within_capture_identity"])
    _assert_string(spec, source_props["requested_keyword"], min_length=1)
    _assert_string(spec, source_props["domain"], min_length=1)
    for metric in ("mentions", "ai_search_volume", "provider_array_index"):
        _assert_int(spec, source_props[metric], minimum=0, maximum=IJSON_MAX)



def _xmin_snapshot(dsn: str) -> dict[str, list[tuple[object, ...]]]:
    snapshot: dict[str, list[tuple[object, ...]]] = {}
    with connect(dsn) as connection:
        for table in READONLY_TABLES:
            rows = connection.execute(f"SELECT xmin::text, * FROM {table}").fetchall()
            snapshot[table] = sorted(
                rows, key=lambda row: tuple(str(item) for item in row[1:])
            )
    return snapshot


def test_unselected_recipe_is_503_and_pin_v1_does_not_require_selection(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare(tmp_path, postgres_dsn, select=False)
    with connect(postgres_dsn) as connection:
        selected = connection.execute("SELECT * FROM provider_recipe_selections").fetchall()
    assert selected == []
    with _app(store, postgres_dsn) as client:
        missing = _history(client)
        pinned = _history(client, derivation_version_id=TARGET_METRICS_RECIPE_ID)
        attempt = client.get(f"/v1/attempts/{attempt_id}")
        pinned_attempt = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={TARGET_METRICS_RECIPE_ID}"
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
    assert pinned_attempt.json()["adapter_contract"] == TARGET_METRICS_ADAPTER_CONTRACT
    assert "observations" not in pinned_attempt.json()
    assert "total" not in pinned_attempt.json()


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
            (TARGET_METRICS_ADAPTER_CONTRACT, TARGET_METRICS_RECIPE_ID),
        ).fetchone()
    assert second_id is not None
    with _app(store, postgres_dsn) as client:
        wrong = _history(client, derivation_version_id=CORE_RECIPE_ID)
        unknown = _history(client, derivation_version_id="ab" * 32)
        malformed = _history(client, derivation_version_id="not-a-digest")
        test_recipe = _history(client, derivation_version_id=TEST_RECIPE_ID)
        other_tm = _history(client, derivation_version_id=str(second_id[0]))
        empty = client.get(HISTORY)
        blank = _history(client, requested_keyword="")
        limit0 = _history(client, limit=0)
        limit101 = _history(client, limit=101)
        bad_order = _history(client, order="sideways")
        attempt_wrong = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={CORE_RECIPE_ID}"
        )
    assert wrong.status_code == 404
    assert unknown.status_code == 404
    assert malformed.status_code == 404
    assert test_recipe.status_code == 404
    assert other_tm.status_code == 404
    assert wrong.json() == {"detail": "not found"}
    assert empty.status_code == 422
    assert blank.status_code == 422
    assert limit0.status_code == 422
    assert limit101.status_code == 422
    assert bad_order.status_code == 422
    assert attempt_wrong.status_code == 404
    with connect(postgres_dsn) as connection:
        select_provider_recipe(
            connection, TARGET_METRICS_ADAPTER_CONTRACT, str(second_id[0])
        )
    with _app(store, postgres_dsn) as client:
        selected_other = _history(client)
        pinned_v1 = _history(client, derivation_version_id=TARGET_METRICS_RECIPE_ID)
    assert selected_other.status_code == 404
    assert selected_other.json() == {"detail": "not found"}
    assert pinned_v1.status_code == 200
    assert pinned_v1.json()["recipe_resolution"] == "pinned"


def test_tampered_v1_recipe_bytes_are_409(tmp_path: Path, postgres_dsn: str) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE provider_recipes
            SET recipe_canonical_bytes = %s
            WHERE derivation_version_id = %s
            """,
            (b'{"not":"a-recipe"}', TARGET_METRICS_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_frozen_ai09_projection_openapi_and_no_mutation(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    before = _xmin_snapshot(postgres_dsn)
    before_ops = list(store.recorded_ops)
    with _app(store, postgres_dsn) as client:
        response = _history(client)
        pinned = _history(client, derivation_version_id=TARGET_METRICS_RECIPE_ID)
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
    assert pinned.status_code == 200
    assert pinned.json()["recipe_resolution"] == "pinned"
    capture = body["captures"][0]
    assert set(capture) == CAPTURE_KEYS
    assert capture["attempt_id"] == attempt_id
    assert capture["capture_id"] == capture_id
    assert capture["provider"] == body["provider"] == "dataforseo"
    assert capture["adapter_contract"] == body["adapter_contract"]
    assert capture["derivation_version_id"] == body["derivation_version_id"]
    assert set(capture["request"]) == REQUEST_KEYS
    assert capture["request"]["keyword"] == KEYWORD
    assert capture["request"]["match_type"] == "word_match"
    assert capture["request"]["search_filter"] == "include"
    assert capture["request"]["search_scope"] == ["answer"]
    assert capture["request"]["platform"] == "google"
    assert capture["request"]["location_code"] == 2840
    assert capture["request"]["language_code"] == "en"
    assert capture["request"]["internal_list_limit"] == 10
    assert capture["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": 11,
    }
    context = capture["result_context"]
    assert set(context) == CONTEXT_KEYS
    assert context["total_count"] == 0
    assert context["result_offset"] == 0
    assert context["items_count"] == 0
    assert context["items_state"] == "stated"
    assert context["sources_domain_count"] == 10
    assert context["sources_domain_count"] == len(capture["source_domains"])
    assert capture["capture_outcome"]["observation_count"] == 1 + len(
        capture["source_domains"]
    )
    for name, key in (("location", 2840), ("language", "en"), ("platform", "google")):
        group = context[name]
        assert set(group) == GROUPING_KEYS
        assert group["key"] == key
        assert group["mentions"] == TOTAL_MENTIONS
        assert group["ai_search_volume"] == TOTAL_VOLUME
        assert group["provider_array_index"] == 0
        assert group["row_count"] == 1
    for family in (
        "search_results_domain",
        "brand_entities_title",
        "brand_entities_category",
    ):
        assert set(context[family]) == FAMILY_KEYS
        assert context[family] == {"state": "stated", "count": 0}
    assert capture["total"]["observation_kind"] == TOTAL_KIND
    assert capture["total"]["requested_keyword"] == KEYWORD
    assert capture["total"]["mentions"] == TOTAL_MENTIONS
    assert capture["total"]["ai_search_volume"] == TOTAL_VOLUME
    domains = capture["source_domains"]
    assert len(domains) == 10
    mention_sum = 0
    volume_sum = 0
    for index, (domain, mentions, volume) in enumerate(SOURCE_DOMAINS):
        item = domains[index]
        assert item["observation_kind"] == SOURCE_DOMAIN_KIND
        assert item["requested_keyword"] == KEYWORD
        assert item["domain"] == domain
        assert item["mentions"] == mentions
        assert item["ai_search_volume"] == volume
        assert item["provider_array_index"] == index
        mention_sum += mentions
        volume_sum += volume
    assert mention_sum == 4415
    assert volume_sum == 3187610
    assert mention_sum != TOTAL_MENTIONS
    assert "truncated" not in json.dumps(body)
    assert "rank" not in json.dumps(capture["source_domains"])
    assert outcomes.status_code == 404
    assert holdings.status_code == 404
    assert attempt.status_code == 200
    assert attempt.json()["adapter_contract"] == TARGET_METRICS_ADAPTER_CONTRACT
    assert attempt.json()["capture_outcome"]["observation_count"] == 11
    assert "source_domains" not in attempt.json()
    schema = spec.json()
    assert spec.status_code == 200
    _assert_history_openapi(schema)


def test_empty_history_is_not_failure_or_never_measured(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        response = _history(client, requested_keyword="not-measured")
    assert response.status_code == 200
    body = response.json()
    _assert_envelope(body, total_matching=0, returned_count=0)
    assert body["captures"] == []
    assert body["requested_keyword"] == "not-measured"


def test_zero_metrics_empty_domains_limit_counts_and_field_states(
    tmp_path: Path, postgres_dsn: str
) -> None:
    zero_doc = _decoded()
    _agg(zero_doc)["total"]["mentions"] = 0
    _agg(zero_doc)["total"]["ai_search_volume"] = 0
    empty_doc = _decoded()
    _agg(empty_doc)["sources_domain"] = []
    below_doc = _decoded()
    _agg(below_doc)["sources_domain"] = _agg(below_doc)["sources_domain"][:3]
    above_doc = _decoded()
    rows = list(_agg(above_doc)["sources_domain"])
    rows.append(_row("above-limit.example", 1, 1))
    _agg(above_doc)["sources_domain"] = rows
    unicode_doc = _decoded()
    _agg(unicode_doc)["sources_domain"][0]["key"] = " www.例子.com "
    disagree_doc = _decoded()
    _agg(disagree_doc)["location"][0]["mentions"] = 1
    absent_doc = _decoded()
    del _result(absent_doc)["items"]
    del _agg(absent_doc)["brand_entities_title"]
    null_doc = _decoded()
    _result(null_doc)["items"] = None
    _agg(null_doc)["brand_entities_category"] = None
    cases = (
        ("zero", _encode(zero_doc), "21" * 32, "2026-08-24T03:09:01.100000Z"),
        ("empty", _encode(empty_doc), "22" * 32, "2026-08-24T03:09:02.100000Z"),
        ("below", _encode(below_doc), "23" * 32, "2026-08-24T03:09:03.100000Z"),
        ("above", _encode(above_doc), "24" * 32, "2026-08-24T03:09:04.100000Z"),
        ("unicode", _encode(unicode_doc), "25" * 32, "2026-08-24T03:09:05.100000Z"),
        ("disagree", _encode(disagree_doc), "26" * 32, "2026-08-24T03:09:06.100000Z"),
        ("absent", _encode(absent_doc), "27" * 32, "2026-08-24T03:09:07.100000Z"),
        ("null", _encode(null_doc), "28" * 32, "2026-08-24T03:09:08.100000Z"),
    )
    store = create_store(tmp_path / "variants")
    ids: dict[str, str] = {}
    for name, body, nonce, started in cases:
        _attempt, capture_id = _commit_complete(store, body, nonce, started=started)
        ids[name] = capture_id
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_target_metrics(store, connection)
        select_provider_recipe(
            connection, TARGET_METRICS_ADAPTER_CONTRACT, TARGET_METRICS_RECIPE_ID
        )
    with _app(store, postgres_dsn) as client:
        body = _history(client, limit=100).json()
        limited = _history(client, limit=1).json()
        descending = _history(client, order="desc", limit=1).json()
    _assert_envelope(body, total_matching=8, returned_count=8, limit=100)
    captures = {item["capture_id"]: item for item in body["captures"]}
    zero = captures[ids["zero"]]
    assert zero["total"]["mentions"] == 0
    assert zero["total"]["ai_search_volume"] == 0
    assert zero["capture_outcome"]["classification"] == "observation_admitted"
    assert zero["capture_outcome"]["observation_count"] == 11
    empty = captures[ids["empty"]]
    assert empty["source_domains"] == []
    assert empty["result_context"]["sources_domain_count"] == 0
    assert empty["capture_outcome"]["observation_count"] == 1
    below = captures[ids["below"]]
    assert len(below["source_domains"]) == 3
    assert below["result_context"]["sources_domain_count"] == 3
    assert below["request"]["internal_list_limit"] == 10
    assert below["capture_outcome"]["observation_count"] == 4
    above = captures[ids["above"]]
    assert len(above["source_domains"]) == 11
    assert above["result_context"]["sources_domain_count"] == 11
    assert above["request"]["internal_list_limit"] == 10
    unicode_capture = captures[ids["unicode"]]
    assert unicode_capture["source_domains"][0]["domain"] == " www.例子.com "
    disagree = captures[ids["disagree"]]
    assert disagree["result_context"]["location"]["mentions"] == 1
    assert disagree["total"]["mentions"] == TOTAL_MENTIONS
    absent = captures[ids["absent"]]
    assert absent["result_context"]["items_state"] == "absent"
    assert absent["result_context"]["brand_entities_title"] == {
        "state": "absent",
        "count": None,
    }
    null = captures[ids["null"]]
    assert null["result_context"]["items_state"] == "json_null"
    assert null["result_context"]["brand_entities_category"] == {
        "state": "json_null",
        "count": None,
    }
    started = [item["request_started_at"] for item in body["captures"]]
    assert started == sorted(started)
    _assert_envelope(limited, total_matching=8, returned_count=1, limit=1)
    assert limited["has_more"] is True
    assert limited["captures"][0]["capture_id"] == body["captures"][0]["capture_id"]
    _assert_envelope(descending, total_matching=8, returned_count=1, limit=1, order="desc")
    assert descending["captures"][0]["capture_id"] == body["captures"][-1]["capture_id"]


def test_non_admitted_matching_context_is_409_even_outside_limit(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, first_capture = _prepare(
        tmp_path, postgres_dsn, nonce="31" * 32, started="2026-08-24T03:09:01.100000Z"
    )
    _commit_complete(store, _body(), "32" * 32, started="2026-08-24T03:09:02.100000Z")
    with connect(postgres_dsn) as connection:
        derive_target_metrics(store, connection)
        connection.execute(
            """
            UPDATE outcomes
            SET classification = 'provider_error'
            WHERE capture_id = %s
            """,
            (first_capture,),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client, limit=1))
        other = _history(client, requested_keyword="other keyword")
    assert other.status_code == 200
    assert other.json()["total_matching"] == 0


def test_source_count_mismatch_extra_envelope_and_missing_total_are_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE target_metrics_result_context
            SET sources_domain_count = sources_domain_count + 1
            WHERE capture_id = %s
            """,
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE target_metrics_result_context
            SET sources_domain_count = 10
            WHERE capture_id = %s
            """,
            (capture_id,),
        )
        connection.execute(
            """
            UPDATE target_metrics_result_context
            SET sources_domain_count = sources_domain_count - 1
            WHERE capture_id = %s
            """,
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client, limit=1))
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE target_metrics_result_context
            SET sources_domain_count = 10
            WHERE capture_id = %s
            """,
            (capture_id,),
        )
        connection.execute(
            """
            INSERT INTO observation_envelopes (
                capture_id, attempt_id, derivation_version_id, provider,
                adapter_contract, observation_kind, within_capture_identity
            )
            SELECT capture_id, attempt_id, derivation_version_id, provider,
                   adapter_contract, observation_kind, repeat('ab', 32)
            FROM observation_envelopes
            WHERE capture_id = %s
            LIMIT 1
            """,
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_missing_total_row_is_409(tmp_path: Path, postgres_dsn: str) -> None:
    store, _attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            "DELETE FROM target_metrics_totals WHERE capture_id = %s",
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_request_disagreement_is_409(tmp_path: Path, postgres_dsn: str) -> None:
    store, _attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE target_metrics_result_context
            SET language_code = 'de'
            WHERE capture_id = %s
            """,
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_matching_evidence_damage_outside_limit_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, first_capture = _prepare(
        tmp_path, postgres_dsn, nonce="41" * 32, started="2026-08-24T03:09:01.100000Z"
    )
    _commit_complete(store, _body(), "42" * 32, started="2026-08-24T03:09:02.100000Z")
    with connect(postgres_dsn) as connection:
        derive_target_metrics(store, connection)
    later = None
    with connect(postgres_dsn) as connection:
        row = connection.execute(
            """
            SELECT capture_id FROM target_metrics_result_context
            WHERE capture_id <> %s
            """,
            (first_capture,),
        ).fetchone()
        assert row is not None
        later = str(row[0])
    manifest = store.capture_path(later) / "capture.json"
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client, limit=1, order="asc"))


def test_cross_linked_envelope_attempt_id_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, first_attempt, first_capture = _prepare(
        tmp_path, postgres_dsn, nonce="51" * 32, started="2026-08-24T03:09:01.100000Z"
    )
    second_attempt, _second_capture = _commit_complete(
        store, _body(), "52" * 32, started="2026-08-24T03:09:02.100000Z"
    )
    with connect(postgres_dsn) as connection:
        derive_target_metrics(store, connection)
        connection.execute(
            """
            UPDATE observation_envelopes
            SET attempt_id = %s
            WHERE capture_id = %s
            """,
            (second_attempt, first_capture),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client, limit=1))
    assert first_attempt != second_attempt
    assert len(first_attempt) == 64
    assert len(second_attempt) == 64


def test_non_dense_source_index_and_nonzero_grouping_index_are_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE target_metrics_source_domains
            SET provider_array_index = 11
            WHERE capture_id = %s AND provider_array_index = 9
            """,
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE target_metrics_source_domains
            SET provider_array_index = 9
            WHERE capture_id = %s AND provider_array_index = 11
            """,
            (capture_id,),
        )
        connection.execute(
            """
            UPDATE target_metrics_result_context
            SET location_provider_array_index = 1
            WHERE capture_id = %s
            """,
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_wrong_observation_count_is_409(tmp_path: Path, postgres_dsn: str) -> None:
    store, _attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = 10
            WHERE capture_id = %s
            """,
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_missing_envelope_is_409(tmp_path: Path, postgres_dsn: str) -> None:
    store, _attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        identity = connection.execute(
            """
            SELECT within_capture_identity
            FROM target_metrics_source_domains
            WHERE capture_id = %s
            LIMIT 1
            """,
            (capture_id,),
        ).fetchone()
        assert identity is not None
        connection.execute(
            """
            DELETE FROM target_metrics_source_domains
            WHERE capture_id = %s AND within_capture_identity = %s
            """,
            (capture_id, identity[0]),
        )
        connection.execute(
            """
            DELETE FROM observation_envelopes
            WHERE capture_id = %s AND within_capture_identity = %s
            """,
            (capture_id, identity[0]),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_unknown_kind_extra_envelope_is_409(tmp_path: Path, postgres_dsn: str) -> None:
    store, _attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            INSERT INTO observation_envelopes (
                capture_id, attempt_id, derivation_version_id, provider,
                adapter_contract, observation_kind, within_capture_identity
            )
            SELECT capture_id, attempt_id, derivation_version_id, provider,
                   adapter_contract,
                   'dataforseo.google.ai_optimization.target_metrics.unknown.v1',
                   repeat('cd', 32)
            FROM observation_envelopes
            WHERE capture_id = %s
            LIMIT 1
            """,
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_malformed_projection_missing_count_is_409(
    tmp_path: Path, postgres_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)

    def omit_count(state: object, count: object, name: str) -> dict[str, object]:
        return {"state": "stated"}

    monkeypatch.setattr("observatory.target_metrics_read._optional_family", omit_count)
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_malformed_projection_wrong_observation_kinds_is_409(
    tmp_path: Path, postgres_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    from observatory.target_metrics_read import history_list_response as real_history

    def twisted_kinds(**kwargs: Any) -> dict[str, object]:
        payload = real_history(**kwargs)
        payload["observation_kinds"] = [SOURCE_DOMAIN_KIND, TOTAL_KIND]
        return payload

    monkeypatch.setattr(
        "observatory.target_metrics_read.history_list_response", twisted_kinds
    )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_adapter_disagreement_is_409(
    tmp_path: Path, postgres_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    real_capture = store.read_capture

    def wrong_adapter(capture_id: str) -> dict[str, object] | None:
        capture = real_capture(capture_id)
        if capture is None:
            return None
        changed = dict(capture)
        changed["adapter_contract"] = MENTIONS_ADAPTER_CONTRACT
        return changed

    store.read_capture = wrong_adapter  # type: ignore[method-assign, assignment]
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


@pytest.mark.parametrize(
    ("statement", "value"),
    (
        (
            "UPDATE observation_envelopes SET provider = %s WHERE capture_id = %s",
            "other-provider",
        ),
        (
            "UPDATE observation_envelopes SET adapter_contract = %s WHERE capture_id = %s",
            MENTIONS_ADAPTER_CONTRACT,
        ),
    ),
)
def test_envelope_provider_adapter_disagreement_is_409(
    tmp_path: Path,
    postgres_dsn: str,
    statement: str,
    value: str,
) -> None:
    store, _attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(statement, (value, capture_id))
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))
