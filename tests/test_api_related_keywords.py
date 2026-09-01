"""RK-05: Related Keywords Recipe selection and admitted-history API.

Most adversarial proofs run on small synthetic Captures so the PostgreSQL loop stays
bounded. The full RK-02 fixture is reserved for the golden content proof, where its rich
provider testimony is what is being proved.

The golden proof projects persisted PostgreSQL rows plus verified Evidence into expected
JSON through this module's own independent projector, which discovers relations from
`information_schema` rather than from the production reader's column tuples. The production
assembler is never used to build the expected value.
"""

from __future__ import annotations

import copy
import hashlib
import json
import socket
from collections.abc import Iterator, Mapping, Sequence
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient
from psycopg import sql
from pydantic import ValidationError

from observatory.api import create_app
from observatory.capture_event import (
    HISTORICAL_ADAPTER_CONTRACT,
    RELATED_KEYWORDS_ADAPTER_CONTRACT,
    body_ref,
    historical_http_attempt_document,
    historical_http_capture_document,
    related_keywords_http_attempt_document,
    related_keywords_http_capture_document,
)
from observatory.dataforseo_ai_optimization_llm_mentions_historical_paid_probe import (
    closed_historical_parameters,
    historical_request_body_bytes,
)
from observatory.dataforseo_google_related_keywords import (
    KEYWORD_DATA_KIND,
    LOCUS_ITEM,
    LOCUS_SEED,
    MONTHLY_KIND,
    RELATED_KEYWORDS_RECIPE,
    RELATED_KEYWORDS_RECIPE_ID,
    RELATIONSHIP_KIND,
)
from observatory.dataforseo_google_related_keywords_paid_probe import (
    closed_related_keywords_parameters,
    related_keywords_request_body_bytes,
)
from observatory.dataforseo_keyword_overview import CORE_RECIPE, CORE_RECIPE_ID
from observatory.evidence_store import EvidenceStore, create_store
from observatory.google_related_keywords_derive import (
    BACKLINKS_TABLE,
    CONTEXT_TABLE,
    INTENT_TABLE,
    ITEM_OCCURRENCES_TABLE,
    KEYWORD_DATA_TABLE,
    KEYWORD_INFO_TABLE,
    MONTHLY_OCCURRENCES_TABLE,
    MONTHLY_TABLE,
    PROPERTIES_TABLE,
    RELATIONSHIP_OCCURRENCES_TABLE,
    RELATIONSHIP_TABLE,
    RK04_TABLES,
    SERP_TABLE,
    derive_google_related_keywords,
)
from observatory.migrate import apply_migrations, connect
from observatory.provider_recipe import (
    recipe_bytes,
    register_provider_recipe,
    validate_recipe,
)
from observatory.provider_recipe_selection import (
    NOT_SELECTED_SIGNAL,
    select_provider_recipe,
)
from observatory.related_keywords_read import (
    BACKLINKS_COLUMNS,
    INTENT_COLUMNS,
    ITEM_OCCURRENCE_COLUMNS,
    KEYWORD_DATA_COLUMNS,
    KEYWORD_INFO_COLUMNS,
    MONTHLY_COLUMNS,
    MONTHLY_OCCURRENCE_COLUMNS,
    PROPERTIES_COLUMNS,
    RELATIONSHIP_COLUMNS,
    RELATIONSHIP_OCCURRENCE_COLUMNS,
    SERP_COLUMNS,
    RelatedKeywordsCaptureOutcome,
    RelatedKeywordsDecimalField,
    RelatedKeywordsHistoryEnvelope,
    RelatedKeywordsTextField,
)
from observatory.settings import Settings

HISTORY = "/v1/providers/dataforseo/google/related-keywords/history"
KEYWORD_OVERVIEW_HISTORY = "/v1/providers/dataforseo/google/keyword-overview/history"
INTEGRITY_SIGNAL = "evidence_integrity_failure"
SEED = "conspiracy theories"
OTHER_SEED = "unmeasured seed"
IJSON_MAX = 9007199254740991
HEX64_PATTERN = r"^[0-9a-f]{64}$"

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_google_related_keywords_rk02.json"
)
FIXTURE_BYTES = 177120
FIXTURE_SHA256 = "e128f2f81d51479237f1bd7e51feee3dfffcae4596558ebff67365f03cd1decb"

# Frozen-Capture consequences of the accepted RK-04 model. Golden test facts only; the
# production reader must never treat them as provider invariants.
GOLDEN_KEYWORD_DATA = 81
GOLDEN_MONTHLY = 972
GOLDEN_RELATIONSHIP = 477
GOLDEN_ENVELOPES = 1530
GOLDEN_ITEM_OCCURRENCES = 80
GOLDEN_MONTHLY_OCCURRENCES = 960
GOLDEN_RELATIONSHIP_OCCURRENCES = 477
GOLDEN_CHILD_ROWS = {
    KEYWORD_INFO_TABLE: 81,
    PROPERTIES_TABLE: 81,
    BACKLINKS_TABLE: 60,
    INTENT_TABLE: 81,
    SERP_TABLE: 63,
}
FRONTIER_TARGET = "conspiracy theories podcast - youtube"
DUPLICATE_CATEGORY_KEYWORD = "funny conspiracy theories"
DUPLICATE_CATEGORIES = [10013, 10013, 10106, 13566]
YEAR_ONE_CLOCK = "0001-01-01 00:00:00 +00:00"
DEPTH_ZERO_CLOCKS = {
    "keyword_info_last_updated_time": "2026-08-28 16:54:38 +00:00",
    "avg_backlinks_last_updated_time": "2026-05-14 19:04:51 +00:00",
    "search_intent_last_updated_time": "2026-04-29 12:24:14 +00:00",
    "serp_last_updated_time": "2026-05-14 19:04:49 +00:00",
    "serp_previous_updated_time": "2026-03-28 15:59:07 +00:00",
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
    "keyword_data",
    "monthly_search_volume",
    "relationships",
}
REQUEST_KEYS = {
    "keyword",
    "location_code",
    "language_code",
    "depth",
    "limit",
    "offset",
    "order_by",
    "include_seed_keyword",
    "include_serp_info",
    "include_clickstream_data",
    "ignore_synonyms",
    "replace_with_core_keyword",
}
RESULT_CONTEXT_KEYS = {
    "seed_keyword",
    "location_code",
    "language_code",
    "se_type",
    "total_count",
    "items_count",
    "seed_keyword_data_state",
    "derived_returned_item_count",
    "derived_relationship_occurrence_count",
}
READONLY_TABLES = (
    "provider_recipes",
    "provider_recipe_selections",
    "outcomes",
    "observation_envelopes",
    *RK04_TABLES,
)
_IDENTITY_COLUMNS = frozenset(
    {"capture_id", "derivation_version_id", "within_capture_identity", "observation_kind"}
)
_ENCLOSING: dict[str, tuple[str, str]] = {
    "keyword_info_state": ("keyword_info", KEYWORD_INFO_TABLE),
    "keyword_properties_state": ("keyword_properties", PROPERTIES_TABLE),
    "avg_backlinks_state": ("avg_backlinks", BACKLINKS_TABLE),
    "search_intent_state": ("search_intent", INTENT_TABLE),
    "serp_info_state": ("serp_info", SERP_TABLE),
}
_LOCUS_RANK = {LOCUS_SEED: 0, LOCUS_ITEM: 1}


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


# --------------------------------------------------------------------------------------
# Synthetic provider bodies
# --------------------------------------------------------------------------------------

OMIT = object()


def keyword_data(keyword: str, **overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {"keyword": keyword}
    data.update(overrides)
    return {key: value for key, value in data.items() if value is not OMIT}


def keyword_info(**overrides: Any) -> dict[str, Any]:
    info: dict[str, Any] = {
        "se_type": "google",
        "last_updated_time": "2026-08-28 16:54:38 +00:00",
        "competition": 0.25,
        "competition_level": "LOW",
        "cpc": 1.5,
        "search_volume": 100,
        "low_top_of_page_bid": 0.5,
        "high_top_of_page_bid": 2.5,
        "categories": [10013, 10013],
        "monthly_searches": [{"year": 2026, "month": 7, "search_volume": 90}],
        "search_volume_trend": {"monthly": -5, "quarterly": 0, "yearly": 12},
    }
    info.update(overrides)
    return {key: value for key, value in info.items() if value is not OMIT}


def properties(**overrides: Any) -> dict[str, Any]:
    document: dict[str, Any] = {
        "se_type": "google",
        "core_keyword": "conspiracy",
        "synonym_clustering_algorithm": "keyword_metrics",
        "keyword_difficulty": 41,
        "detected_language": "en",
        "is_another_language": False,
    }
    document.update(overrides)
    return {key: value for key, value in document.items() if value is not OMIT}


def backlinks(**overrides: Any) -> dict[str, Any]:
    document: dict[str, Any] = {
        "se_type": "google",
        "backlinks": 1234.5678,
        "dofollow": 1000.25,
        "referring_pages": 900.5,
        "referring_domains": 88.125,
        "referring_main_domains": 80.0625,
        "rank": 210.75,
        "main_domain_rank": 305.125,
        "last_updated_time": "2026-05-14 19:04:51 +00:00",
    }
    document.update(overrides)
    return {key: value for key, value in document.items() if value is not OMIT}


def intent(**overrides: Any) -> dict[str, Any]:
    document: dict[str, Any] = {
        "se_type": "google",
        "main_intent": "informational",
        "foreign_intent": ["commercial", "commercial"],
        "last_updated_time": "2026-04-29 12:24:14 +00:00",
    }
    document.update(overrides)
    return {key: value for key, value in document.items() if value is not OMIT}


def serp(**overrides: Any) -> dict[str, Any]:
    document: dict[str, Any] = {
        "se_type": "google",
        "check_url": "https://www.google.com/search?q=alpha",
        "serp_item_types": ["organic", "organic", "people_also_ask"],
        "se_results_count": 123456,
        "last_updated_time": "2026-05-14 19:04:49 +00:00",
        "previous_updated_time": YEAR_ONE_CLOCK,
    }
    document.update(overrides)
    return {key: value for key, value in document.items() if value is not OMIT}


def rich_keyword_data(keyword: str, **overrides: Any) -> dict[str, Any]:
    document: dict[str, Any] = {
        "keyword": keyword,
        "location_code": 2840,
        "language_code": "en",
        "se_type": "google",
        "keyword_info": keyword_info(),
        "keyword_properties": properties(),
        "avg_backlinks_info": backlinks(),
        "search_intent_info": intent(),
        "serp_info": serp(),
    }
    document.update(overrides)
    return {key: value for key, value in document.items() if value is not OMIT}


def item(
    keyword: str,
    *,
    depth: int = 1,
    data: dict[str, Any] | None = None,
    related: Any = "omit",
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "depth": depth,
        "se_type": "google",
        "keyword_data": keyword_data(keyword) if data is None else data,
    }
    if related != "omit":
        row["related_keywords"] = related
    return row


def result_document(
    items: list[dict[str, Any]],
    *,
    seed_keyword: str = SEED,
    seed_data: Any = "omit",
    total_count: int | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "seed_keyword": seed_keyword,
        "items": items,
        "items_count": len(items),
        "total_count": len(items) if total_count is None else total_count,
    }
    if seed_data != "omit":
        result["seed_keyword_data"] = seed_data
    if extra:
        result.update(extra)
    return result


def synthetic_body(result: dict[str, Any] | None) -> bytes:
    results = [] if result is None else [result]
    document: dict[str, Any] = {
        "version": "0.1.20260101",
        "status_code": 20000,
        "status_message": "Ok.",
        "time": "0.1 sec.",
        "cost": 0.0216,
        "tasks_count": 1,
        "tasks_error": 0,
        "tasks": [
            {
                "id": "task-1",
                "status_code": 20000,
                "status_message": "Ok.",
                "time": "0.1 sec.",
                "cost": 0.0216,
                "result_count": len(results),
                "path": ["v3", "dataforseo_labs", "google", "related_keywords", "live"],
                "data": {
                    "api": "dataforseo_labs",
                    "function": "related_keywords",
                    "se_type": "google",
                },
                "result": results,
            }
        ],
    }
    return json.dumps(document, ensure_ascii=True).encode("utf-8")


def simple_body(items: list[dict[str, Any]], **kwargs: Any) -> bytes:
    return synthetic_body(result_document(items, **kwargs))


def default_body() -> bytes:
    """One small admitted Capture exercising every projected structure."""

    return simple_body(
        [
            item(
                "alpha",
                depth=0,
                data=rich_keyword_data("alpha"),
                related=["beta", "gamma"],
            ),
            item(
                "beta",
                depth=1,
                data=keyword_data(
                    "beta",
                    keyword_info=keyword_info(
                        search_volume=50,
                        monthly_searches=[
                            {"year": 2026, "month": 7, "search_volume": 0},
                            {"year": 2026, "month": 6, "search_volume": 40},
                        ],
                        search_volume_trend=None,
                    ),
                ),
                related=[],
            ),
        ],
        seed_data=rich_keyword_data(SEED),
    )


# --------------------------------------------------------------------------------------
# Evidence and application helpers
# --------------------------------------------------------------------------------------


def _params(keyword: str = SEED) -> dict[str, object]:
    return closed_related_keywords_parameters(keyword=keyword)


def _attempt_document(nonce: str, keyword: str) -> dict[str, object]:
    return related_keywords_http_attempt_document(
        parameters=_params(keyword),
        attempt_nonce=nonce,
        authorized_at="2026-08-31T10:00:00.000000Z",
        observatory_version="rk05-test-v1",
    )


def _commit(
    store: EvidenceStore,
    body: bytes,
    nonce: str,
    *,
    keyword: str = SEED,
    suffix: str = "1",
) -> tuple[str, str]:
    attempt = _attempt_document(nonce, keyword)
    attempt_id = store.commit_attempt(
        attempt, request_body=related_keywords_request_body_bytes(_params(keyword))
    )
    started = f"2026-08-31T10:00:0{suffix}.100000Z"
    capture = related_keywords_http_capture_document(
        attempt=attempt,
        request_started_at=started,
        transport_ended_at=f"2026-08-31T10:00:0{suffix}.400000Z",
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
        response_headers_at=f"2026-08-31T10:00:0{suffix}.200000Z",
        response_body_ended_at=f"2026-08-31T10:00:0{suffix}.300000Z",
    )
    capture_id = store.commit_capture(capture, response_body=body)
    return attempt_id, capture_id


def _app(store: EvidenceStore, dsn: str) -> TestClient:
    settings = Settings(
        environment="test",
        database_url=dsn,
        evidence_root=store.root,
        derivation_version_id="unused-fixture-label",
    )
    return TestClient(create_app(settings, store=store))


def _history(client: TestClient, keyword: str = SEED, **query: object) -> Any:
    params = {"requested_keyword": keyword, **query}
    return client.get(HISTORY + "?" + urlencode(params, doseq=True))


def _prepare(
    tmp_path: Path,
    postgres_dsn: str,
    *,
    body: bytes | None = None,
    nonce: str = "11" * 32,
    keyword: str = SEED,
    select: bool = True,
    derive: bool = True,
) -> tuple[EvidenceStore, str, str]:
    store = create_store(tmp_path / f"evidence-{nonce[:8]}")
    attempt_id, capture_id = _commit(
        store, body if body is not None else default_body(), nonce, keyword=keyword
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        if derive:
            derive_google_related_keywords(store, connection)
        else:
            register_provider_recipe(connection, RELATED_KEYWORDS_RECIPE)
        if select:
            select_provider_recipe(
                connection, RELATED_KEYWORDS_ADAPTER_CONTRACT, RELATED_KEYWORDS_RECIPE_ID
            )
    return store, attempt_id, capture_id


@pytest.fixture
def ready(
    tmp_path: Path, postgres_dsn: str
) -> Iterator[tuple[TestClient, EvidenceStore, str, str]]:
    store, attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        yield client, store, attempt_id, capture_id


def _damage(dsn: str, statement: str, params: Sequence[object] = ()) -> None:
    """Plant PostgreSQL damage with referential triggers disabled. CHECKs still apply."""

    with connect(dsn) as connection:
        connection.execute("SET session_replication_role = replica")
        connection.execute(statement, tuple(params))


def _assert_409(response: Any) -> None:
    assert response.status_code == 409
    payload = response.json()
    assert payload == {"detail": INTEGRITY_SIGNAL}
    assert "captures" not in payload
    assert "total_matching" not in payload


def _assert_envelope(
    body: Mapping[str, Any],
    *,
    total_matching: int,
    returned_count: int,
    limit: int = 20,
    order: str = "asc",
    resolution: str = "selected",
) -> list[dict[str, Any]]:
    assert set(body) == HISTORY_KEYS
    assert body["provider"] == "dataforseo"
    assert body["adapter_contract"] == RELATED_KEYWORDS_ADAPTER_CONTRACT
    assert body["derivation_version_id"] == RELATED_KEYWORDS_RECIPE_ID
    assert body["recipe_resolution"] == resolution
    assert body["observation_kinds"] == [
        KEYWORD_DATA_KIND,
        MONTHLY_KIND,
        RELATIONSHIP_KIND,
    ]
    assert body["total_matching"] == total_matching
    assert body["returned_count"] == returned_count
    assert body["limit"] == limit
    assert body["order"] == order
    assert body["has_more"] is (total_matching > returned_count)
    captures = body["captures"]
    assert isinstance(captures, list)
    assert len(captures) == returned_count
    for capture in captures:
        assert set(capture) == CAPTURE_KEYS
    return list(captures)


def _one_capture(client: TestClient, keyword: str = SEED, **query: object) -> dict[str, Any]:
    response = _history(client, keyword, **query)
    assert response.status_code == 200, response.text
    captures = _assert_envelope(response.json(), total_matching=1, returned_count=1)
    return captures[0]


# --------------------------------------------------------------------------------------
# Independent expected-JSON projection.
#
# Relations are discovered from information_schema, not from the reader's column tuples,
# and value/state pairs are grouped by column naming alone. The production reader and
# assembler are never called here, so a shared bug cannot manufacture a green.
# --------------------------------------------------------------------------------------


def _table_columns(connection: Any, table: str) -> list[str]:
    rows = connection.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
        """,
        (table,),
    ).fetchall()
    assert rows, table
    return [str(row[0]) for row in rows]


def _content_columns(connection: Any, table: str) -> list[str]:
    return [
        column
        for column in _table_columns(connection, table)
        if column not in _IDENTITY_COLUMNS
    ]


def _fetch(connection: Any, table: str, capture_id: str) -> list[dict[str, Any]]:
    columns = _table_columns(connection, table)
    statement = sql.SQL("SELECT {} FROM {} WHERE derivation_version_id = %s AND capture_id = %s")
    rows = connection.execute(
        statement.format(
            sql.SQL(", ").join(sql.Identifier(column) for column in columns),
            sql.Identifier(table),
        ),
        (RELATED_KEYWORDS_RECIPE_ID, capture_id),
    ).fetchall()
    return [dict(zip(columns, row, strict=True)) for row in rows]


def _convert(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, (list, tuple)):
        return [_convert(member) for member in value]
    return value


def _project(columns: Sequence[str], row: Mapping[str, Any]) -> dict[str, Any]:
    names = set(columns)
    projected: dict[str, Any] = {}
    for column in columns:
        if column.endswith("_state"):
            if column[: -len("_state")] in names:
                continue
            projected[column] = row[column]
        elif f"{column}_state" in names:
            projected[column] = {
                "state": row[f"{column}_state"],
                "value": _convert(row[column]),
            }
        else:
            projected[column] = _convert(row[column])
    return projected


def _expected_keyword_data(connection: Any, capture_id: str) -> list[dict[str, Any]]:
    parent_columns = _content_columns(connection, KEYWORD_DATA_TABLE)
    children = {
        table: {
            str(row["within_capture_identity"]): row
            for row in _fetch(connection, table, capture_id)
        }
        for _name, table in _ENCLOSING.values()
    }
    occurrences: dict[str, list[dict[str, Any]]] = {}
    occurrence_columns = _content_columns(connection, ITEM_OCCURRENCES_TABLE)
    for row in _fetch(connection, ITEM_OCCURRENCES_TABLE, capture_id):
        occurrences.setdefault(str(row["within_capture_identity"]), []).append(
            _project(occurrence_columns, row)
        )
    facts: list[dict[str, Any]] = []
    for row in _fetch(connection, KEYWORD_DATA_TABLE, capture_id):
        identity = str(row["within_capture_identity"])
        payload = _project(parent_columns, row)
        for state_column, (name, table) in _ENCLOSING.items():
            state = payload.pop(state_column)
            child = children[table].get(identity)
            value = (
                _project(_content_columns(connection, table), child)
                if state == "stated" and child is not None
                else None
            )
            payload[name] = {"state": state, "value": value}
        facts.append(
            {
                "observation_kind": str(row["observation_kind"]),
                "within_capture_identity": identity,
                **payload,
                "occurrences": sorted(
                    occurrences.get(identity, []), key=lambda entry: entry["item_index"]
                ),
            }
        )
    facts.sort(
        key=lambda fact: (
            _LOCUS_RANK[fact["locus"]],
            fact["keyword"],
            fact["within_capture_identity"],
        )
    )
    return facts


def _expected_monthly(connection: Any, capture_id: str) -> list[dict[str, Any]]:
    parent_columns = _content_columns(connection, MONTHLY_TABLE)
    occurrence_columns = _content_columns(connection, MONTHLY_OCCURRENCES_TABLE)
    occurrences: dict[str, list[dict[str, Any]]] = {}
    for row in _fetch(connection, MONTHLY_OCCURRENCES_TABLE, capture_id):
        occurrences.setdefault(str(row["within_capture_identity"]), []).append(
            _project(occurrence_columns, row)
        )
    facts: list[dict[str, Any]] = []
    for row in _fetch(connection, MONTHLY_TABLE, capture_id):
        identity = str(row["within_capture_identity"])
        payload = _project(parent_columns, row)
        period = {"year": payload.pop("year"), "month": payload.pop("month")}
        facts.append(
            {
                "observation_kind": str(row["observation_kind"]),
                "within_capture_identity": identity,
                **payload,
                "data_period": period,
                "occurrences": sorted(
                    occurrences.get(identity, []), key=lambda entry: entry["item_index"]
                ),
            }
        )
    facts.sort(
        key=lambda fact: (
            _LOCUS_RANK[fact["locus"]],
            fact["keyword"],
            fact["data_period"]["year"],
            fact["data_period"]["month"],
            fact["within_capture_identity"],
        )
    )
    return facts


def _expected_relationships(connection: Any, capture_id: str) -> list[dict[str, Any]]:
    parent_columns = _content_columns(connection, RELATIONSHIP_TABLE)
    occurrence_columns = _content_columns(connection, RELATIONSHIP_OCCURRENCES_TABLE)
    occurrences: dict[str, list[dict[str, Any]]] = {}
    for row in _fetch(connection, RELATIONSHIP_OCCURRENCES_TABLE, capture_id):
        occurrences.setdefault(str(row["within_capture_identity"]), []).append(
            _project(occurrence_columns, row)
        )
    facts: list[dict[str, Any]] = []
    for row in _fetch(connection, RELATIONSHIP_TABLE, capture_id):
        identity = str(row["within_capture_identity"])
        facts.append(
            {
                "observation_kind": str(row["observation_kind"]),
                "within_capture_identity": identity,
                **_project(parent_columns, row),
                "occurrences": sorted(
                    occurrences.get(identity, []),
                    key=lambda entry: (entry["source_item_index"], entry["target_index"]),
                ),
            }
        )
    facts.sort(
        key=lambda fact: (
            fact["source_keyword"],
            fact["target_keyword"],
            fact["within_capture_identity"],
        )
    )
    return facts


def _expected_capture(
    connection: Any, store: EvidenceStore, capture_id: str
) -> dict[str, Any]:
    context_rows = _fetch(connection, CONTEXT_TABLE, capture_id)
    assert len(context_rows) == 1
    context = context_rows[0]
    attempt_id = str(context["attempt_id"])
    attempt = store.read_attempt(attempt_id)
    capture = store.read_capture(capture_id)
    assert attempt is not None and capture is not None
    parameters = attempt["parameters"]
    assert isinstance(parameters, Mapping)
    outcome = connection.execute(
        """
        SELECT classification, observation_count
        FROM outcomes
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (RELATED_KEYWORDS_RECIPE_ID, capture_id),
    ).fetchone()
    assert outcome is not None
    return {
        "attempt_id": attempt_id,
        "capture_id": capture_id,
        "provider": "dataforseo",
        "adapter_contract": RELATED_KEYWORDS_ADAPTER_CONTRACT,
        "derivation_version_id": RELATED_KEYWORDS_RECIPE_ID,
        "authorized_at": attempt["authorized_at"],
        "request_started_at": capture["request_started_at"],
        "transport_ended_at": capture["transport_ended_at"],
        "request": {key: parameters[key] for key in REQUEST_KEYS},
        "capture_outcome": {
            "classification": str(outcome[0]),
            "observation_count": int(outcome[1]),
        },
        "result_context": {
            "seed_keyword": context["result_seed_keyword"],
            "location_code": {
                "state": context["result_location_code_state"],
                "value": context["result_location_code"],
            },
            "language_code": {
                "state": context["result_language_code_state"],
                "value": context["result_language_code"],
            },
            "se_type": {
                "state": context["result_se_type_state"],
                "value": context["result_se_type"],
            },
            "total_count": int(context["total_count"]),
            "items_count": int(context["items_count"]),
            "seed_keyword_data_state": context["seed_keyword_data_state"],
            "derived_returned_item_count": int(context["derived_returned_item_count"]),
            "derived_relationship_occurrence_count": int(
                context["derived_relationship_occurrence_count"]
            ),
        },
        "keyword_data": _expected_keyword_data(connection, capture_id),
        "monthly_search_volume": _expected_monthly(connection, capture_id),
        "relationships": _expected_relationships(connection, capture_id),
    }


def _second_related_keywords_recipe() -> dict[str, object]:
    """A registered non-v1 Recipe for the exact same adapter."""

    document = copy.deepcopy(RELATED_KEYWORDS_RECIPE)
    document["reconciliation"] = {"rule": "result_echo_is_authority_v2"}
    return validate_recipe(document)


# --------------------------------------------------------------------------------------
# Recipe selection, pinning, and stored-Recipe verification
# --------------------------------------------------------------------------------------


def test_selected_recipe_serves_admitted_history(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, attempt_id, capture_id = ready
    capture = _one_capture(client)
    assert capture["attempt_id"] == attempt_id
    assert capture["capture_id"] == capture_id
    assert capture["capture_outcome"]["classification"] == "observation_admitted"
    assert set(capture["request"]) == REQUEST_KEYS
    assert set(capture["result_context"]) == RESULT_CONTEXT_KEYS


def test_explicit_pin_reports_pinned_resolution(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn, select=False)
    with _app(store, postgres_dsn) as client:
        response = _history(client, derivation_version_id=RELATED_KEYWORDS_RECIPE_ID)
        assert response.status_code == 200, response.text
        _assert_envelope(
            response.json(), total_matching=1, returned_count=1, resolution="pinned"
        )


def test_unselected_adapter_without_pin_is_503(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn, select=False)
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    assert response.status_code == 503
    assert response.json() == {"detail": NOT_SELECTED_SIGNAL}


@pytest.mark.parametrize(
    "pin",
    ["not-a-digest", "", "A" * 64, "0" * 63, "f" * 64],
    ids=["malformed", "empty", "uppercase", "short", "unknown"],
)
def test_malformed_or_unknown_pin_is_404(
    ready: tuple[TestClient, EvidenceStore, str, str], pin: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    response = _history(client, derivation_version_id=pin)
    assert response.status_code == 404
    assert response.json() == {"detail": "not found"}


def test_wrong_adapter_pin_is_404(tmp_path: Path, postgres_dsn: str) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, CORE_RECIPE)
    with _app(store, postgres_dsn) as client:
        response = _history(client, derivation_version_id=CORE_RECIPE_ID)
    assert response.status_code == 404
    assert response.json() == {"detail": "not found"}


def test_registered_non_v1_related_keywords_recipe_pin_is_404(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    second = _second_related_keywords_recipe()
    with connect(postgres_dsn) as connection:
        registered = register_provider_recipe(connection, second)
    assert registered.derivation_version_id != RELATED_KEYWORDS_RECIPE_ID
    with _app(store, postgres_dsn) as client:
        response = _history(client, derivation_version_id=registered.derivation_version_id)
    assert response.status_code == 404
    assert response.json() == {"detail": "not found"}


def test_selecting_a_non_v1_recipe_for_this_adapter_is_404(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    second = _second_related_keywords_recipe()
    with connect(postgres_dsn) as connection:
        registered = register_provider_recipe(connection, second)
        select_provider_recipe(
            connection,
            RELATED_KEYWORDS_ADAPTER_CONTRACT,
            registered.derivation_version_id,
        )
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    assert response.status_code == 404


def test_non_canonical_recipe_bytes_are_409(tmp_path: Path, postgres_dsn: str) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    canonical = recipe_bytes(RELATED_KEYWORDS_RECIPE)
    with connect(postgres_dsn) as connection:
        connection.execute(
            "UPDATE provider_recipes SET recipe_canonical_bytes = %s"
            " WHERE derivation_version_id = %s",
            (b" " + canonical, RELATED_KEYWORDS_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_recipe_bytes_that_are_not_a_closed_recipe_are_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            "UPDATE provider_recipes SET recipe_canonical_bytes = %s"
            " WHERE derivation_version_id = %s",
            (b"{}", RELATED_KEYWORDS_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_recipe_kind_list_damage_is_409(tmp_path: Path, postgres_dsn: str) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    document = copy.deepcopy(RELATED_KEYWORDS_RECIPE)
    kinds = document["observation_kinds"]
    assert isinstance(kinds, list)
    document["observation_kinds"] = [kinds[1], kinds[0], kinds[2]]
    with connect(postgres_dsn) as connection:
        connection.execute(
            "UPDATE provider_recipes SET recipe_canonical_bytes = %s"
            " WHERE derivation_version_id = %s",
            (recipe_bytes(document), RELATED_KEYWORDS_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_recipe_capture_taxonomy_damage_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    document = copy.deepcopy(RELATED_KEYWORDS_RECIPE)
    admission = document["admission"]
    assert isinstance(admission, dict)
    outcomes = admission["capture_outcomes"]
    assert isinstance(outcomes, list)
    # Same members, different stored order: RK-05 validates the exact stored order.
    admission["capture_outcomes"] = [outcomes[1], outcomes[0], *outcomes[2:]]
    with connect(postgres_dsn) as connection:
        connection.execute(
            "UPDATE provider_recipes SET recipe_canonical_bytes = %s"
            " WHERE derivation_version_id = %s",
            (recipe_bytes(document), RELATED_KEYWORDS_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_recipe_adapter_column_damage_serves_no_history(
    tmp_path: Path, postgres_dsn: str
) -> None:
    """Re-registering v1 under a foreign adapter cannot leak history through this route.

    The disagreement is resolved before RK-05 sees it: the selection no longer resolves
    for this adapter (503) and an explicit pin is a wrong-adapter miss (404). Either way
    no history envelope is produced. The reader keeps its own adapter-metadata check as
    defence in depth for a future resolution path.
    """

    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    _damage(
        postgres_dsn,
        "UPDATE provider_recipes SET adapter_contract = %s WHERE derivation_version_id = %s",
        (HISTORICAL_ADAPTER_CONTRACT, RELATED_KEYWORDS_RECIPE_ID),
    )
    with _app(store, postgres_dsn) as client:
        selected = _history(client)
        pinned = _history(client, derivation_version_id=RELATED_KEYWORDS_RECIPE_ID)
    assert selected.status_code == 503
    assert selected.json() == {"detail": NOT_SELECTED_SIGNAL}
    assert pinned.status_code == 404
    assert "captures" not in pinned.json()


def test_recipe_provider_column_damage_is_409(tmp_path: Path, postgres_dsn: str) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    _damage(
        postgres_dsn,
        "UPDATE provider_recipes SET provider = %s WHERE derivation_version_id = %s",
        ("other-provider", RELATED_KEYWORDS_RECIPE_ID),
    )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_selection_isolation_between_adapters(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, CORE_RECIPE)
        rows = connection.execute(
            "SELECT adapter_contract, derivation_version_id"
            " FROM provider_recipe_selections ORDER BY adapter_contract"
        ).fetchall()
    assert rows == [(RELATED_KEYWORDS_ADAPTER_CONTRACT, RELATED_KEYWORDS_RECIPE_ID)]
    with _app(store, postgres_dsn) as client:
        assert _history(client).status_code == 200
        overview = client.get(
            KEYWORD_OVERVIEW_HISTORY + "?" + urlencode({"requested_keyword": SEED})
        )
    assert overview.status_code == 503
    assert overview.json() == {"detail": NOT_SELECTED_SIGNAL}


# --------------------------------------------------------------------------------------
# Query contract
# --------------------------------------------------------------------------------------


def test_missing_requested_keyword_is_422(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    assert client.get(HISTORY).status_code == 422


def test_empty_requested_keyword_is_422(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    assert _history(client, "").status_code == 422


def test_long_operator_subject_is_an_empty_history_miss_not_422(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    """min_length=1 only: RK-01's 80-character operator bound is not a query rule."""

    client, _store, _attempt_id, _capture_id = ready
    impossible = ('"quoted" +operator -exclusion ' * 4) + "x" * 40
    assert len(impossible) > 80
    response = _history(client, impossible)
    assert response.status_code == 200, response.text
    body = response.json()
    _assert_envelope(body, total_matching=0, returned_count=0)
    assert body["requested_keyword"] == impossible


def test_unmeasured_subject_is_empty_history(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    response = _history(client, OTHER_SEED)
    assert response.status_code == 200
    _assert_envelope(response.json(), total_matching=0, returned_count=0)


@pytest.mark.parametrize("limit", ["0", "-1", "101", "abc"])
def test_limit_outside_the_outer_bound_is_422(
    ready: tuple[TestClient, EvidenceStore, str, str], limit: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    assert _history(client, limit=limit).status_code == 422


def test_unknown_order_is_422(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    assert _history(client, order="ascending").status_code == 422


# --------------------------------------------------------------------------------------
# Membership, provenance, and Evidence verification
# --------------------------------------------------------------------------------------


def _query(dsn: str, statement: str, params: Sequence[object] = ()) -> list[Any]:
    with connect(dsn) as connection:
        return list(connection.execute(statement, tuple(params)).fetchall())


def _keyword_identity(dsn: str, keyword: str) -> str:
    rows = _query(
        dsn,
        f"SELECT within_capture_identity FROM {KEYWORD_DATA_TABLE} WHERE keyword = %s",
        (keyword,),
    )
    assert len(rows) == 1, keyword
    return str(rows[0][0])


def _relationship_identity(dsn: str, source: str, target: str) -> str:
    rows = _query(
        dsn,
        f"SELECT within_capture_identity FROM {RELATIONSHIP_TABLE}"
        " WHERE source_keyword = %s AND target_keyword = %s",
        (source, target),
    )
    assert len(rows) == 1, (source, target)
    return str(rows[0][0])


def _prepare_pair(
    tmp_path: Path, postgres_dsn: str
) -> tuple[EvidenceStore, list[tuple[str, str]]]:
    """Two admitted Captures for the same exact subject, in ascending Capture order."""

    store = create_store(tmp_path / "evidence-pair")
    first = _commit(store, default_body(), "21" * 32, suffix="1")
    second = _commit(store, simple_body([item("delta")]), "22" * 32, suffix="2")
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_related_keywords(store, connection)
        select_provider_recipe(
            connection, RELATED_KEYWORDS_ADAPTER_CONTRACT, RELATED_KEYWORDS_RECIPE_ID
        )
    return store, [first, second]


def test_two_captures_order_limit_and_has_more(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, pair = _prepare_pair(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        ascending = _history(client)
        descending = _history(client, order="desc")
        limited = _history(client, limit=1)
    assert ascending.status_code == 200
    captures = _assert_envelope(ascending.json(), total_matching=2, returned_count=2)
    assert [capture["capture_id"] for capture in captures] == [
        pair[0][1],
        pair[1][1],
    ]
    reversed_captures = _assert_envelope(
        descending.json(), total_matching=2, returned_count=2, order="desc"
    )
    assert [capture["capture_id"] for capture in reversed_captures] == [
        pair[1][1],
        pair[0][1],
    ]
    limited_captures = _assert_envelope(
        limited.json(), total_matching=2, returned_count=1, limit=1
    )
    assert limited_captures[0]["capture_id"] == pair[0][1]
    assert limited.json()["has_more"] is True


def test_damage_outside_the_limit_still_fails_the_whole_read(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, pair = _prepare_pair(tmp_path, postgres_dsn)
    _damage(
        postgres_dsn,
        "UPDATE outcomes SET observation_count = observation_count + 1"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (RELATED_KEYWORDS_RECIPE_ID, pair[1][1]),
    )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client, limit=1))
        _assert_409(_history(client))


def test_missing_outcome_behind_a_matching_context_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        "DELETE FROM outcomes WHERE derivation_version_id = %s AND capture_id = %s",
        (RELATED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_foreign_attempt_outcome_behind_a_matching_context_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        "UPDATE outcomes SET attempt_id = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        ("e" * 64, RELATED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    "classification",
    [
        "provider_error",
        "response_partial",
        "no_response",
        "provider_envelope_rejected",
        "transport_complete_non_admissible",
        "reconciliation_failed",
    ],
)
def test_non_admitted_outcome_behind_a_matching_context_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    classification: str,
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        "UPDATE outcomes SET classification = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (classification, RELATED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_missing_capture_evidence_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, store, _attempt_id, capture_id = ready
    bundle = store.capture_path(capture_id)
    (bundle / "capture.json").unlink()
    _assert_409(_history(client))


def test_missing_attempt_evidence_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, store, attempt_id, _capture_id = ready
    attempt = store.read_attempt(attempt_id)
    assert attempt is not None
    bundle = store.attempt_path(
        str(attempt["request_fingerprint"]), str(attempt["authorized_at"]), attempt_id
    )
    (bundle / "attempt.json").unlink()
    _assert_409(_history(client))


def test_cross_linked_attempt_provenance_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    foreign_attempt_id, _foreign_capture_id = _commit(
        store, simple_body([item("delta")]), "33" * 32, keyword=OTHER_SEED, suffix="2"
    )
    for table in ("outcomes", CONTEXT_TABLE):
        _damage(
            postgres_dsn,
            f"UPDATE {table} SET attempt_id = %s"
            " WHERE derivation_version_id = %s AND capture_id = %s",
            (foreign_attempt_id, RELATED_KEYWORDS_RECIPE_ID, capture_id),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_wrong_adapter_capture_evidence_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    """A context row planted over foreign-adapter Evidence never becomes history."""

    store, attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    foreign_body = b'{"foreign": true}'
    foreign_attempt = historical_http_attempt_document(
        parameters=closed_historical_parameters(),
        attempt_nonce="44" * 32,
        authorized_at="2026-08-31T11:00:00.000000Z",
        observatory_version="rk05-test-v1",
    )
    foreign_attempt_id = store.commit_attempt(
        foreign_attempt, request_body=historical_request_body_bytes(
            closed_historical_parameters()
        )
    )
    foreign_capture_id = store.commit_capture(
        historical_http_capture_document(
            attempt=foreign_attempt,
            request_started_at="2026-08-31T11:00:01.100000Z",
            transport_ended_at="2026-08-31T11:00:01.400000Z",
            transport_state="response_complete",
            response={
                "status": 200,
                "http_version": "HTTP/1.1",
                "header_policy": "http-headers-v1",
                "headers": [["content-type", "application/json"]],
                "omitted_headers": [],
                "body": {"state": "present_nonempty", "body": body_ref(foreign_body)},
                "completeness": "complete",
            },
            transport_failure=None,
            response_headers_at="2026-08-31T11:00:01.200000Z",
            response_body_ended_at="2026-08-31T11:00:01.300000Z",
        ),
        response_body=foreign_body,
    )
    _damage(
        postgres_dsn,
        "INSERT INTO outcomes (attempt_id, capture_id, derivation_version_id,"
        " classification, observation_count) VALUES (%s, %s, %s, %s, %s)",
        (
            foreign_attempt_id,
            foreign_capture_id,
            RELATED_KEYWORDS_RECIPE_ID,
            "observation_admitted_empty",
            0,
        ),
    )
    context_columns = (
        "capture_id",
        "derivation_version_id",
        "attempt_id",
        "requested_seed",
        "request_location_code",
        "request_language_code",
        "request_depth",
        "request_limit",
        "request_offset",
        "request_order_by",
        "request_include_seed_keyword",
        "request_include_serp_info",
        "request_include_clickstream_data",
        "request_ignore_synonyms",
        "request_replace_with_core_keyword",
        "result_seed_keyword",
        "result_location_code",
        "result_location_code_state",
        "result_language_code",
        "result_language_code_state",
        "result_se_type",
        "result_se_type_state",
        "total_count",
        "items_count",
        "seed_keyword_data_state",
        "derived_returned_item_count",
        "derived_relationship_occurrence_count",
    )
    selected = ", ".join(
        {
            "capture_id": "%s",
            "attempt_id": "%s",
            "total_count": "0",
            "items_count": "0",
            "derived_returned_item_count": "0",
            "derived_relationship_occurrence_count": "0",
        }.get(column, column)
        for column in context_columns
    )
    _damage(
        postgres_dsn,
        f"INSERT INTO {CONTEXT_TABLE} ({', '.join(context_columns)})"
        f" SELECT {selected} FROM {CONTEXT_TABLE} WHERE derivation_version_id = %s",
        (foreign_capture_id, foreign_attempt_id, RELATED_KEYWORDS_RECIPE_ID),
    )
    assert attempt_id
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


# --------------------------------------------------------------------------------------
# Capture-wide PostgreSQL consistency
# --------------------------------------------------------------------------------------


def test_missing_envelope_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    identity = _keyword_identity(postgres_dsn, "beta")
    _damage(
        postgres_dsn,
        "DELETE FROM observation_envelopes WHERE within_capture_identity = %s",
        (identity,),
    )
    _assert_409(_history(client))


def test_extra_envelope_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        "INSERT INTO observation_envelopes (capture_id, attempt_id,"
        " derivation_version_id, provider, adapter_contract, observation_kind,"
        " within_capture_identity) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (
            capture_id,
            attempt_id,
            RELATED_KEYWORDS_RECIPE_ID,
            "dataforseo",
            RELATED_KEYWORDS_ADAPTER_CONTRACT,
            KEYWORD_DATA_KIND,
            "ab" * 32,
        ),
    )
    _assert_409(_history(client))
    _damage(
        postgres_dsn,
        "UPDATE outcomes SET observation_count = observation_count + 1"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (RELATED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_wrong_kind_envelope_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    identity = _keyword_identity(postgres_dsn, "beta")
    _damage(
        postgres_dsn,
        "UPDATE observation_envelopes SET observation_kind = %s"
        " WHERE within_capture_identity = %s",
        (MONTHLY_KIND, identity),
    )
    _assert_409(_history(client))


def test_unknown_kind_envelope_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    identity = _keyword_identity(postgres_dsn, "beta")
    _damage(
        postgres_dsn,
        "UPDATE observation_envelopes SET observation_kind = %s"
        " WHERE within_capture_identity = %s",
        ("dataforseo.google.keyword_overview.metrics.v1", identity),
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("attempt_id", "c" * 64),
        ("provider", "other-provider"),
        ("adapter_contract", HISTORICAL_ADAPTER_CONTRACT),
    ],
)
def test_cross_linked_envelope_provenance_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    column: str,
    value: str,
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    identity = _keyword_identity(postgres_dsn, "beta")
    _damage(
        postgres_dsn,
        f"UPDATE observation_envelopes SET {column} = %s"
        " WHERE within_capture_identity = %s",
        (value, identity),
    )
    _assert_409(_history(client))


def test_missing_semantic_parent_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    identity = _keyword_identity(postgres_dsn, "beta")
    _damage(
        postgres_dsn,
        f"DELETE FROM {KEYWORD_DATA_TABLE} WHERE within_capture_identity = %s",
        (identity,),
    )
    _assert_409(_history(client))


def test_extra_semantic_parent_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"INSERT INTO {KEYWORD_DATA_TABLE} (capture_id, derivation_version_id,"
        " within_capture_identity, observation_kind, requested_seed, locus, keyword,"
        " location_code_state, language_code_state, se_type_state, keyword_info_state,"
        " keyword_properties_state, avg_backlinks_state, search_intent_state,"
        " serp_info_state, bing_normalized_state, clickstream_normalized_state,"
        " clickstream_keyword_info_state)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s, 'absent', 'absent', 'absent', 'absent',"
        " 'absent', 'absent', 'absent', 'absent', 'absent', 'absent', 'absent')",
        (
            capture_id,
            RELATED_KEYWORDS_RECIPE_ID,
            "cd" * 32,
            KEYWORD_DATA_KIND,
            SEED,
            LOCUS_ITEM,
            "planted",
        ),
    )
    _assert_409(_history(client))


def test_missing_child_row_for_a_stated_state_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    identity = _keyword_identity(postgres_dsn, "alpha")
    _damage(
        postgres_dsn,
        f"DELETE FROM {SERP_TABLE} WHERE within_capture_identity = %s",
        (identity,),
    )
    _assert_409(_history(client))


def test_unexpected_child_row_for_a_non_stated_state_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    identity = _keyword_identity(postgres_dsn, "beta")
    state = _query(
        postgres_dsn,
        f"SELECT serp_info_state FROM {KEYWORD_DATA_TABLE} WHERE within_capture_identity = %s",
        (identity,),
    )
    assert str(state[0][0]) != "stated"
    _damage(
        postgres_dsn,
        f"INSERT INTO {SERP_TABLE} (capture_id, derivation_version_id,"
        " within_capture_identity, observation_kind, se_type_state, check_url_state,"
        " serp_item_types_state, se_results_count_state, serp_last_updated_time_state,"
        " serp_previous_updated_time_state)"
        " VALUES (%s, %s, %s, %s, 'absent', 'absent', 'absent', 'absent', 'absent',"
        " 'absent')",
        (capture_id, RELATED_KEYWORDS_RECIPE_ID, identity, KEYWORD_DATA_KIND),
    )
    _assert_409(_history(client))


def test_missing_item_occurrence_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    _damage(
        postgres_dsn, f"DELETE FROM {ITEM_OCCURRENCES_TABLE} WHERE item_index = 1"
    )
    _assert_409(_history(client))


def test_extra_item_occurrence_breaks_global_density(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    identity = _keyword_identity(postgres_dsn, "alpha")
    _damage(
        postgres_dsn,
        f"INSERT INTO {ITEM_OCCURRENCES_TABLE} (capture_id, derivation_version_id,"
        " within_capture_identity, observation_kind, item_index, depth, item_se_type,"
        " related_keywords_state) VALUES (%s, %s, %s, %s, 5, 0, 'google', 'stated')",
        (capture_id, RELATED_KEYWORDS_RECIPE_ID, identity, KEYWORD_DATA_KIND),
    )
    _assert_409(_history(client))


def test_missing_monthly_occurrence_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    _damage(
        postgres_dsn,
        f"DELETE FROM {MONTHLY_OCCURRENCES_TABLE} WHERE item_index = 1"
        " AND within_capture_identity = ("
        f"SELECT min(within_capture_identity) FROM {MONTHLY_OCCURRENCES_TABLE}"
        " WHERE item_index = 1)",
    )
    _assert_409(_history(client))


def test_monthly_occurrence_without_a_returned_item_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    identity = _query(
        postgres_dsn,
        f"SELECT min(within_capture_identity) FROM {MONTHLY_TABLE} WHERE locus = %s",
        (LOCUS_ITEM,),
    )[0][0]
    _damage(
        postgres_dsn,
        f"INSERT INTO {MONTHLY_OCCURRENCES_TABLE} (capture_id, derivation_version_id,"
        " within_capture_identity, observation_kind, item_index)"
        " VALUES (%s, %s, %s, %s, 9)",
        (capture_id, RELATED_KEYWORDS_RECIPE_ID, str(identity), MONTHLY_KIND),
    )
    _assert_409(_history(client))


def test_missing_relationship_occurrence_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    identity = _relationship_identity(postgres_dsn, "alpha", "gamma")
    _damage(
        postgres_dsn,
        f"DELETE FROM {RELATIONSHIP_OCCURRENCES_TABLE} WHERE within_capture_identity = %s",
        (identity,),
    )
    _assert_409(_history(client))


def test_target_index_density_is_checked_per_source_item(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    identity = _relationship_identity(postgres_dsn, "alpha", "gamma")
    _damage(
        postgres_dsn,
        f"UPDATE {RELATIONSHIP_OCCURRENCES_TABLE} SET target_index = 7"
        " WHERE within_capture_identity = %s",
        (identity,),
    )
    _assert_409(_history(client))


def test_duplicate_target_index_for_one_source_item_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    identity = _relationship_identity(postgres_dsn, "alpha", "gamma")
    _damage(
        postgres_dsn,
        f"UPDATE {RELATIONSHIP_OCCURRENCES_TABLE} SET target_index = 0"
        " WHERE within_capture_identity = %s",
        (identity,),
    )
    _assert_409(_history(client))


def test_non_stated_related_keywords_with_occurrences_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {ITEM_OCCURRENCES_TABLE} SET related_keywords_state = 'absent'"
        " WHERE item_index = 0",
    )
    _assert_409(_history(client))


def test_relationship_source_depth_disagreement_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {RELATIONSHIP_OCCURRENCES_TABLE} SET source_depth = 2"
        " WHERE source_item_index = 0",
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    ("table", "assignment"),
    [
        (KEYWORD_DATA_TABLE, "keyword = 'tampered'"),
        (KEYWORD_DATA_TABLE, "locus = 'seed_keyword_data'"),
        (KEYWORD_DATA_TABLE, "requested_seed = 'tampered seed'"),
        (MONTHLY_TABLE, "year = 2020"),
        (MONTHLY_TABLE, "keyword = 'tampered'"),
        (RELATIONSHIP_TABLE, "target_keyword = 'tampered'"),
        (RELATIONSHIP_TABLE, "source_keyword = 'tampered'"),
    ],
)
def test_identity_axis_tamper_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    table: str,
    assignment: str,
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {table} SET {assignment} WHERE within_capture_identity = ("
        f"SELECT min(within_capture_identity) FROM {table})",
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    "assignment",
    [
        "observation_count = observation_count + 1",
        "observation_count = observation_count - 1",
    ],
)
def test_wrong_observation_count_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    assignment: str,
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE outcomes SET {assignment}"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (RELATED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    "assignment",
    [
        "items_count = items_count + 1",
        "derived_returned_item_count = derived_returned_item_count + 1",
        "derived_relationship_occurrence_count = derived_relationship_occurrence_count + 1",
    ],
)
def test_wrong_derived_or_provider_counts_are_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    assignment: str,
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    _damage(postgres_dsn, f"UPDATE {CONTEXT_TABLE} SET {assignment}")
    _assert_409(_history(client))


def test_total_count_may_disagree_with_items_count(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    """total_count is provider testimony, never a read invariant."""

    client, _store, _attempt_id, _capture_id = ready
    _damage(postgres_dsn, f"UPDATE {CONTEXT_TABLE} SET total_count = 4321")
    capture = _one_capture(client)
    assert capture["result_context"]["total_count"] == 4321
    assert capture["result_context"]["items_count"] == 2


def test_admitted_empty_classification_over_semantic_rows_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        "UPDATE outcomes SET classification = 'observation_admitted_empty',"
        " observation_count = 0 WHERE derivation_version_id = %s AND capture_id = %s",
        (RELATED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    "column",
    [
        "request_location_code",
        "request_depth",
        "request_limit",
        "request_offset",
    ],
)
def test_request_context_disagreement_with_the_attempt_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    column: str,
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    _damage(postgres_dsn, f"UPDATE {CONTEXT_TABLE} SET {column} = {column} + 1")
    _assert_409(_history(client))


def test_request_context_flag_disagreement_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {CONTEXT_TABLE} SET request_ignore_synonyms = true",
    )
    _assert_409(_history(client))


def test_request_order_by_disagreement_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {CONTEXT_TABLE} SET request_order_by = ARRAY['keyword_data.keyword_info"
        ".search_volume,asc']",
    )
    _assert_409(_history(client))


# --------------------------------------------------------------------------------------
# Semantic collapse, occurrences, states, and emptiness
# --------------------------------------------------------------------------------------


def _capture_for(tmp_path: Path, postgres_dsn: str, body: bytes) -> dict[str, Any]:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn, body=body)
    with _app(store, postgres_dsn) as client:
        return _one_capture(client)


def _by_keyword(facts: Sequence[Mapping[str, Any]], keyword: str) -> list[dict[str, Any]]:
    return [dict(fact) for fact in facts if fact["keyword"] == keyword]


def test_duplicate_returned_keyword_collapses_but_keeps_every_occurrence(
    tmp_path: Path, postgres_dsn: str
) -> None:
    body = simple_body(
        [
            item("alpha", depth=1, data=keyword_data("alpha", keyword_info=keyword_info())),
            item("alpha", depth=2, data=keyword_data("alpha", keyword_info=keyword_info())),
        ]
    )
    capture = _capture_for(tmp_path, postgres_dsn, body)
    facts = _by_keyword(capture["keyword_data"], "alpha")
    assert len(facts) == 1
    assert [entry["item_index"] for entry in facts[0]["occurrences"]] == [0, 1]
    assert [entry["depth"] for entry in facts[0]["occurrences"]] == [1, 2]
    monthly = _by_keyword(capture["monthly_search_volume"], "alpha")
    assert len(monthly) == 1
    assert [entry["item_index"] for entry in monthly[0]["occurrences"]] == [0, 1]
    assert capture["result_context"]["items_count"] == 2
    assert capture["result_context"]["derived_returned_item_count"] == 2
    assert capture["capture_outcome"]["observation_count"] == len(
        capture["keyword_data"]
    ) + len(capture["monthly_search_volume"]) + len(capture["relationships"])


def test_duplicate_source_keyword_with_unequal_related_arrays(
    tmp_path: Path, postgres_dsn: str
) -> None:
    body = simple_body(
        [
            item("alpha", depth=1, related=["x", "y"]),
            item("alpha", depth=2, related=["z"]),
        ]
    )
    capture = _capture_for(tmp_path, postgres_dsn, body)
    assert len(_by_keyword(capture["keyword_data"], "alpha")) == 1
    edges = {
        (fact["source_keyword"], fact["target_keyword"]): fact["occurrences"]
        for fact in capture["relationships"]
    }
    assert set(edges) == {("alpha", "x"), ("alpha", "y"), ("alpha", "z")}
    assert edges[("alpha", "x")] == [
        {"source_item_index": 0, "source_depth": 1, "target_index": 0}
    ]
    assert edges[("alpha", "y")] == [
        {"source_item_index": 0, "source_depth": 1, "target_index": 1}
    ]
    assert edges[("alpha", "z")] == [
        {"source_item_index": 1, "source_depth": 2, "target_index": 0}
    ]
    assert capture["result_context"]["derived_relationship_occurrence_count"] == 3


def test_duplicate_target_collapses_but_keeps_every_edge_occurrence(
    tmp_path: Path, postgres_dsn: str
) -> None:
    body = simple_body([item("alpha", related=["t", "t"])])
    capture = _capture_for(tmp_path, postgres_dsn, body)
    assert len(capture["relationships"]) == 1
    edge = capture["relationships"][0]
    assert (edge["source_keyword"], edge["target_keyword"]) == ("alpha", "t")
    assert [entry["target_index"] for entry in edge["occurrences"]] == [0, 1]


def test_frontier_targets_have_no_invented_keyword_data_node(
    tmp_path: Path, postgres_dsn: str
) -> None:
    body = simple_body([item("alpha", related=["frontier target"])])
    capture = _capture_for(tmp_path, postgres_dsn, body)
    keywords = {fact["keyword"] for fact in capture["keyword_data"]}
    assert keywords == {"alpha"}
    assert {fact["keyword"] for fact in capture["monthly_search_volume"]} <= keywords
    assert capture["relationships"][0]["target_keyword"] == "frontier target"


@pytest.mark.parametrize(
    ("related", "expected_state", "expected_edges"),
    [
        ("omit", "absent", 0),
        (None, "json_null", 0),
        ([], "stated", 0),
        (["edge"], "stated", 1),
    ],
    ids=["absent", "json_null", "stated_empty", "stated_nonempty"],
)
def test_related_keywords_states_survive_with_correct_occurrences(
    tmp_path: Path,
    postgres_dsn: str,
    related: Any,
    expected_state: str,
    expected_edges: int,
) -> None:
    body = simple_body([item("alpha", related=related)])
    capture = _capture_for(tmp_path, postgres_dsn, body)
    occurrences = _by_keyword(capture["keyword_data"], "alpha")[0]["occurrences"]
    assert [entry["related_keywords_state"] for entry in occurrences] == [expected_state]
    assert len(capture["relationships"]) == expected_edges
    assert (
        capture["result_context"]["derived_relationship_occurrence_count"]
        == expected_edges
    )


@pytest.mark.parametrize(
    ("monthly", "expected_state", "expected_points"),
    [
        (OMIT, "absent", 0),
        (None, "json_null", 0),
        ([], "stated", 0),
        ([{"year": 2026, "month": 7, "search_volume": 0}], "stated", 1),
    ],
    ids=["absent", "json_null", "stated_empty", "stated_zero"],
)
def test_monthly_states_stay_distinguishable(
    tmp_path: Path,
    postgres_dsn: str,
    monthly: Any,
    expected_state: str,
    expected_points: int,
) -> None:
    body = simple_body(
        [
            item(
                "alpha",
                data=keyword_data(
                    "alpha", keyword_info=keyword_info(monthly_searches=monthly)
                ),
            )
        ]
    )
    capture = _capture_for(tmp_path, postgres_dsn, body)
    info = _by_keyword(capture["keyword_data"], "alpha")[0]["keyword_info"]
    assert info["state"] == "stated"
    assert info["value"]["monthly_searches_state"] == expected_state
    assert len(capture["monthly_search_volume"]) == expected_points
    if expected_points:
        fact = capture["monthly_search_volume"][0]
        assert fact["search_volume"] == 0
        assert fact["data_period"] == {"year": 2026, "month": 7}


def test_unstated_trend_members_stay_inapplicable(
    tmp_path: Path, postgres_dsn: str
) -> None:
    body = simple_body(
        [
            item(
                "alpha",
                data=keyword_data(
                    "alpha", keyword_info=keyword_info(search_volume_trend=None)
                ),
            )
        ]
    )
    capture = _capture_for(tmp_path, postgres_dsn, body)
    info = _by_keyword(capture["keyword_data"], "alpha")[0]["keyword_info"]["value"]
    assert info["search_volume_trend_state"] == "json_null"
    for member in ("trend_monthly", "trend_quarterly", "trend_yearly"):
        assert info[member] == {"state": "inapplicable", "value": None}


def test_seed_and_depth_zero_item_remain_two_disagreeing_histories(
    tmp_path: Path, postgres_dsn: str
) -> None:
    body = simple_body(
        [
            item(
                SEED,
                depth=0,
                data=keyword_data(SEED, keyword_info=keyword_info(search_volume=80)),
            )
        ],
        seed_data=keyword_data(SEED, keyword_info=keyword_info(search_volume=63)),
    )
    capture = _capture_for(tmp_path, postgres_dsn, body)
    facts = _by_keyword(capture["keyword_data"], SEED)
    assert len(facts) == 2
    assert [fact["locus"] for fact in facts] == [LOCUS_SEED, LOCUS_ITEM]
    assert facts[0]["within_capture_identity"] != facts[1]["within_capture_identity"]
    volumes = [
        fact["keyword_info"]["value"]["search_volume"]["value"] for fact in facts
    ]
    assert volumes == [63, 80]
    assert facts[0]["occurrences"] == []
    assert [entry["item_index"] for entry in facts[1]["occurrences"]] == [0]


def test_admitted_empty_capture_is_subject_bearing_and_factless(
    tmp_path: Path, postgres_dsn: str
) -> None:
    capture = _capture_for(tmp_path, postgres_dsn, simple_body([]))
    assert capture["capture_outcome"] == {
        "classification": "observation_admitted_empty",
        "observation_count": 0,
    }
    assert capture["keyword_data"] == []
    assert capture["monthly_search_volume"] == []
    assert capture["relationships"] == []
    assert capture["result_context"]["items_count"] == 0
    assert capture["result_context"]["derived_returned_item_count"] == 0
    assert capture["result_context"]["seed_keyword"] == SEED
    assert capture["result_context"]["seed_keyword_data_state"] == "absent"
    assert capture["request"]["keyword"] == SEED


def test_stated_seed_with_empty_items_is_ordinary_admitted_testimony(
    tmp_path: Path, postgres_dsn: str
) -> None:
    body = simple_body(
        [], seed_data=keyword_data(SEED, keyword_info=keyword_info())
    )
    capture = _capture_for(tmp_path, postgres_dsn, body)
    assert capture["capture_outcome"]["classification"] == "observation_admitted"
    assert [fact["locus"] for fact in capture["keyword_data"]] == [LOCUS_SEED]
    assert capture["result_context"]["seed_keyword_data_state"] == "stated"
    assert capture["result_context"]["derived_returned_item_count"] == 0


def test_presentation_ranks_seed_before_returned_item(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    ordered = [(fact["locus"], fact["keyword"]) for fact in capture["keyword_data"]]
    assert ordered == [(LOCUS_SEED, SEED), (LOCUS_ITEM, "alpha"), (LOCUS_ITEM, "beta")]
    # Lexical locus ordering would place returned_item first; the explicit rank does not.
    assert sorted(ordered) != ordered
    monthly = [
        (fact["locus"], fact["keyword"], fact["data_period"]["year"], fact["data_period"]["month"])
        for fact in capture["monthly_search_volume"]
    ]
    assert monthly[0][0] == LOCUS_SEED
    assert monthly[1:] == [
        (LOCUS_ITEM, "alpha", 2026, 7),
        (LOCUS_ITEM, "beta", 2026, 6),
        (LOCUS_ITEM, "beta", 2026, 7),
    ]


def test_result_echo_disagreement_stays_provider_testimony(
    tmp_path: Path, postgres_dsn: str
) -> None:
    """The provider result echo may disagree with the verified Attempt and still be served."""

    body = simple_body(
        [item("alpha")],
        seed_keyword="echoed subject",
        extra={"location_code": 9999, "language_code": "de", "se_type": "google"},
    )
    capture = _capture_for(tmp_path, postgres_dsn, body)
    assert capture["result_context"]["seed_keyword"] == "echoed subject"
    assert capture["result_context"]["location_code"] == {
        "state": "stated",
        "value": 9999,
    }
    assert capture["result_context"]["language_code"] == {
        "state": "stated",
        "value": "de",
    }
    assert capture["result_context"]["se_type"] == {"state": "stated", "value": "google"}
    assert capture["request"]["keyword"] == SEED
    assert capture["request"]["location_code"] == 2840
    assert capture["request"]["language_code"] == "en"


def test_decimal_values_never_round_trip_through_binary_float(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    alpha = _by_keyword(capture["keyword_data"], "alpha")[0]
    assert alpha["keyword_info"]["value"]["competition"] == {
        "state": "stated",
        "value": "0.25",
    }
    assert alpha["avg_backlinks"]["value"]["backlinks"] == {
        "state": "stated",
        "value": "1234.5678",
    }
    assert alpha["avg_backlinks"]["value"]["referring_main_domains"]["value"] == "80.0625"


def test_ordered_duplicate_arrays_and_year_one_clock_survive(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    alpha = _by_keyword(_one_capture(client)["keyword_data"], "alpha")[0]
    assert alpha["keyword_info"]["value"]["categories"] == {
        "state": "stated",
        "value": [10013, 10013],
    }
    assert alpha["search_intent"]["value"]["foreign_intent"]["value"] == [
        "commercial",
        "commercial",
    ]
    assert alpha["serp_info"]["value"]["serp_item_types"]["value"] == [
        "organic",
        "organic",
        "people_also_ask",
    ]
    assert alpha["serp_info"]["value"]["serp_previous_updated_time"] == {
        "state": "stated",
        "value": YEAR_ONE_CLOCK,
    }
    assert alpha["keyword_properties"]["value"]["core_keyword"] == {
        "state": "stated",
        "value": "conspiracy",
    }


def test_non_stated_structures_expose_state_without_a_value(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    beta = _by_keyword(_one_capture(client)["keyword_data"], "beta")[0]
    for name in ("keyword_properties", "avg_backlinks", "search_intent", "serp_info"):
        assert beta[name] == {"state": "absent", "value": None}
    assert beta["keyword_info"]["state"] == "stated"
    assert beta["clickstream_normalized_state"] in {
        "absent",
        "not_requested",
        "inapplicable",
        "json_null",
    }


# --------------------------------------------------------------------------------------
# Read-only behaviour, isolation, Attempt routing, and rebuild agreement
# --------------------------------------------------------------------------------------


def _row_value(value: Any) -> Any:
    if isinstance(value, memoryview):
        return bytes(value)
    if isinstance(value, Decimal):
        return format(value, "f")
    return value


def _snapshot(dsn: str) -> dict[str, list[str]]:
    """xmin plus complete content for every relation this route may read."""

    taken: dict[str, list[str]] = {}
    with connect(dsn) as connection:
        for table in READONLY_TABLES:
            columns = _table_columns(connection, table)
            rows = connection.execute(
                sql.SQL("SELECT xmin::text, {} FROM {}").format(
                    sql.SQL(", ").join(sql.Identifier(column) for column in columns),
                    sql.Identifier(table),
                )
            ).fetchall()
            taken[table] = sorted(
                repr(tuple(_row_value(value) for value in row)) for row in rows
            )
    return taken


def _evidence_snapshot(store: EvidenceStore) -> dict[str, str]:
    digests: dict[str, str] = {}
    for path in sorted(store.root.rglob("*")):
        if path.is_file():
            digests[str(path.relative_to(store.root))] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return digests


def test_reads_preserve_postgresql_and_evidence(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, store, attempt_id, _capture_id = ready
    before_rows = _snapshot(postgres_dsn)
    before_evidence = _evidence_snapshot(store)
    before_ops = list(store.recorded_ops)
    assert _history(client).status_code == 200
    assert _history(client, order="desc", limit=5).status_code == 200
    assert _history(client, OTHER_SEED).status_code == 200
    assert client.get(f"/v1/attempts/{attempt_id}").status_code == 200
    assert _snapshot(postgres_dsn) == before_rows
    assert _evidence_snapshot(store) == before_evidence
    assert store.recorded_ops == before_ops


def test_related_keywords_attempt_routes_to_the_provider_attempt_reader(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, attempt_id, capture_id = ready
    response = client.get(f"/v1/attempts/{attempt_id}")
    assert response.status_code == 200, response.text
    body = response.json()
    assert set(body) == {
        "attempt_id",
        "provider",
        "adapter_contract",
        "derivation_version_id",
        "recipe_resolution",
        "attempt_outcome",
        "capture_outcome",
    }
    assert "observations" not in body
    assert body["provider"] == "dataforseo"
    assert body["adapter_contract"] == RELATED_KEYWORDS_ADAPTER_CONTRACT
    assert body["derivation_version_id"] == RELATED_KEYWORDS_RECIPE_ID
    assert body["recipe_resolution"] == "selected"
    assert body["attempt_outcome"]["classification"] == "authorized_unresolved"
    assert body["capture_outcome"]["capture_id"] == capture_id
    assert body["capture_outcome"]["classification"] == "observation_admitted"


def test_related_keywords_attempt_audit_honours_pin_and_selection(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn, select=False)
    with _app(store, postgres_dsn) as client:
        unselected = client.get(f"/v1/attempts/{attempt_id}")
        pinned = client.get(
            f"/v1/attempts/{attempt_id}"
            f"?{urlencode({'derivation_version_id': RELATED_KEYWORDS_RECIPE_ID})}"
        )
    assert unselected.status_code == 503
    assert unselected.json() == {"detail": NOT_SELECTED_SIGNAL}
    assert pinned.status_code == 200
    assert pinned.json()["recipe_resolution"] == "pinned"


def test_unknown_attempt_identity_is_404(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    assert client.get("/v1/attempts/" + "0" * 64).status_code == 404
    assert client.get("/v1/attempts/not-a-digest").status_code == 404


def test_two_independently_derived_databases_return_equal_history(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence-rebuild")
    _commit(store, default_body(), "55" * 32)
    payloads: list[Any] = []
    for dsn in (postgres_dsn, postgres_second_dsn):
        apply_migrations(dsn)
        with connect(dsn) as connection:
            derive_google_related_keywords(store, connection)
            select_provider_recipe(
                connection, RELATED_KEYWORDS_ADAPTER_CONTRACT, RELATED_KEYWORDS_RECIPE_ID
            )
        with _app(store, dsn) as client:
            response = _history(client)
            assert response.status_code == 200, response.text
            payloads.append(response.json())
    assert payloads[0]["total_matching"] == 1
    assert payloads[0]["captures"]
    assert payloads[0] == payloads[1]
    assert json.dumps(payloads[0], sort_keys=True) == json.dumps(
        payloads[1], sort_keys=True
    )


def test_reader_projects_every_persisted_rk04_column(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    """No persisted RK-04 content column may be silently dropped from the projection."""

    expected = {
        KEYWORD_DATA_TABLE: KEYWORD_DATA_COLUMNS,
        KEYWORD_INFO_TABLE: KEYWORD_INFO_COLUMNS,
        PROPERTIES_TABLE: PROPERTIES_COLUMNS,
        BACKLINKS_TABLE: BACKLINKS_COLUMNS,
        INTENT_TABLE: INTENT_COLUMNS,
        SERP_TABLE: SERP_COLUMNS,
        MONTHLY_TABLE: MONTHLY_COLUMNS,
        RELATIONSHIP_TABLE: RELATIONSHIP_COLUMNS,
        ITEM_OCCURRENCES_TABLE: ITEM_OCCURRENCE_COLUMNS,
        MONTHLY_OCCURRENCES_TABLE: MONTHLY_OCCURRENCE_COLUMNS,
        RELATIONSHIP_OCCURRENCES_TABLE: RELATIONSHIP_OCCURRENCE_COLUMNS,
    }
    assert len(expected) + 1 == len(RK04_TABLES)
    with connect(postgres_dsn) as connection:
        for table, columns in expected.items():
            persisted = set(_table_columns(connection, table))
            assert persisted - {"capture_id", "derivation_version_id"} == set(columns)
        context = set(_table_columns(connection, CONTEXT_TABLE))
    request_columns = {column for column in context if column.startswith("request_")}
    result_columns = {
        "result_seed_keyword",
        "result_location_code",
        "result_location_code_state",
        "result_language_code",
        "result_language_code_state",
        "result_se_type",
        "result_se_type_state",
        "total_count",
        "items_count",
        "seed_keyword_data_state",
        "derived_returned_item_count",
        "derived_relationship_occurrence_count",
    }
    provenance = {"capture_id", "derivation_version_id", "attempt_id", "requested_seed"}
    assert context == request_columns | result_columns | provenance
    # Every persisted request duplicate is answered by the verified Attempt request block;
    # `requested_seed` is that block's `keyword` under the Recipe identity axis name.
    assert request_columns == {
        f"request_{key}" for key in REQUEST_KEYS if key != "keyword"
    }
    assert result_columns | {"requested_seed"} >= {
        "result_seed_keyword",
        "requested_seed",
    }


# --------------------------------------------------------------------------------------
# Typed OpenAPI
# --------------------------------------------------------------------------------------

KEYWORD_DATA_FACT_KEYS = {
    "observation_kind",
    "within_capture_identity",
    "requested_seed",
    "locus",
    "keyword",
    "location_code",
    "language_code",
    "se_type",
    "keyword_info",
    "keyword_properties",
    "avg_backlinks",
    "search_intent",
    "serp_info",
    "bing_normalized_state",
    "clickstream_normalized_state",
    "clickstream_keyword_info_state",
    "occurrences",
}
MONTHLY_FACT_KEYS = {
    "observation_kind",
    "within_capture_identity",
    "requested_seed",
    "locus",
    "keyword",
    "data_period",
    "search_volume",
    "occurrences",
}
RELATIONSHIP_FACT_KEYS = {
    "observation_kind",
    "within_capture_identity",
    "requested_seed",
    "source_keyword",
    "target_keyword",
    "occurrences",
}
ITEM_OCCURRENCE_KEYS = {"item_index", "depth", "item_se_type", "related_keywords_state"}
MONTHLY_OCCURRENCE_KEYS = {"item_index"}
RELATIONSHIP_OCCURRENCE_KEYS = {"source_item_index", "source_depth", "target_index"}
KEYWORD_INFO_JSON_KEYS = {
    "se_type",
    "keyword_info_last_updated_time",
    "competition",
    "competition_level",
    "cpc",
    "search_volume",
    "low_top_of_page_bid",
    "high_top_of_page_bid",
    "categories",
    "monthly_searches_state",
    "search_volume_trend_state",
    "trend_monthly",
    "trend_quarterly",
    "trend_yearly",
}
PROPERTIES_JSON_KEYS = {
    "se_type",
    "core_keyword",
    "synonym_clustering_algorithm",
    "keyword_difficulty",
    "detected_language",
    "is_another_language",
}
BACKLINKS_JSON_KEYS = {
    "se_type",
    "backlinks",
    "dofollow",
    "referring_pages",
    "referring_domains",
    "referring_main_domains",
    "rank",
    "main_domain_rank",
    "avg_backlinks_last_updated_time",
}
INTENT_JSON_KEYS = {
    "se_type",
    "main_intent",
    "foreign_intent",
    "search_intent_last_updated_time",
}
SERP_JSON_KEYS = {
    "se_type",
    "check_url",
    "serp_item_types",
    "se_results_count",
    "serp_last_updated_time",
    "serp_previous_updated_time",
}
_STRUCTURE_KEYS = {
    "keyword_info": KEYWORD_INFO_JSON_KEYS,
    "keyword_properties": PROPERTIES_JSON_KEYS,
    "avg_backlinks": BACKLINKS_JSON_KEYS,
    "search_intent": INTENT_JSON_KEYS,
    "serp_info": SERP_JSON_KEYS,
}


def _resolve(spec: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
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
    resolved = _resolve(spec, schema)
    grouped = resolved.get("anyOf") or resolved.get("oneOf")
    if grouped:
        return [_resolve(spec, option) for option in grouped]
    return [resolved]


def _nonnull(spec: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    options = [option for option in _options(spec, schema) if option.get("type") != "null"]
    assert options, schema
    return options


def _closed(schema: dict[str, Any], keys: set[str]) -> dict[str, Any]:
    assert schema.get("additionalProperties") is False, schema
    assert set(schema["required"]) == keys, schema.get("title")
    assert set(schema["properties"]) == keys, schema.get("title")
    properties = schema["properties"]
    assert isinstance(properties, dict)
    return properties


def _const(spec: dict[str, Any], schema: dict[str, Any], expected: object) -> None:
    for option in _nonnull(spec, schema):
        if option.get("const") == expected or option.get("enum") == [expected]:
            return
    raise AssertionError(f"expected const {expected!r} in {schema!r}")


def _state_value(
    spec: dict[str, Any], schema: dict[str, Any]
) -> dict[str, Any]:
    resolved = _resolve(spec, schema)
    properties = _closed(resolved, {"state", "value"})
    states = set()
    for option in _nonnull(spec, properties["state"]):
        states.update(option.get("enum", []))
        if "const" in option:
            states.add(option["const"])
    assert states == {"absent", "inapplicable", "json_null", "not_requested", "stated"}
    return properties


def _spec(tmp_path: Path) -> dict[str, Any]:
    store = create_store(tmp_path / "evidence-openapi")
    settings = Settings(
        environment="test",
        database_url="postgresql://unused/unused",
        evidence_root=store.root,
        derivation_version_id="unused-fixture-label",
    )
    with TestClient(create_app(settings, store=store)) as client:
        response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    document = response.json()
    assert isinstance(document, dict)
    return document


def test_generated_openapi_declares_the_exact_query_contract(tmp_path: Path) -> None:
    spec = _spec(tmp_path)
    assert HISTORY in spec["paths"]
    assert "/v1/providers/dataforseo/google/related-keywords/outcomes" not in spec["paths"]
    assert "/v1/providers/dataforseo/google/related-keywords/holdings" not in spec["paths"]
    route = spec["paths"][HISTORY]["get"]
    params = {entry["name"]: entry for entry in route["parameters"]}
    assert set(params) == {"requested_keyword", "derivation_version_id", "limit", "order"}
    keyword = _resolve(spec, params["requested_keyword"]["schema"])
    assert params["requested_keyword"]["required"] is True
    assert keyword.get("minLength") == 1
    assert "maxLength" not in keyword
    assert "pattern" not in keyword
    assert params["derivation_version_id"].get("required") in {None, False}
    limit = _resolve(spec, params["limit"]["schema"])
    assert limit.get("minimum") == 1
    assert limit.get("maximum") == 100
    assert limit.get("default") == 20
    order = _resolve(spec, params["order"]["schema"])
    assert set(order.get("enum", [])) == {"asc", "desc"}


def test_generated_openapi_is_fully_typed_and_closed(tmp_path: Path) -> None:
    spec = _spec(tmp_path)
    route = spec["paths"][HISTORY]["get"]
    envelope = _resolve(
        spec,
        route["responses"]["200"]["content"]["application/json"]["schema"],
    )
    outer = _closed(envelope, HISTORY_KEYS)
    _const(spec, outer["provider"], "dataforseo")
    _const(spec, outer["adapter_contract"], RELATED_KEYWORDS_ADAPTER_CONTRACT)
    _const(spec, outer["derivation_version_id"], RELATED_KEYWORDS_RECIPE_ID)
    kinds = _resolve(spec, outer["observation_kinds"])
    assert kinds["prefixItems"] == [
        {"type": "string", "const": KEYWORD_DATA_KIND},
        {"type": "string", "const": MONTHLY_KIND},
        {"type": "string", "const": RELATIONSHIP_KIND},
    ]
    capture = _resolve(spec, _resolve(spec, outer["captures"])["items"])
    fields = _closed(capture, CAPTURE_KEYS)

    request = _closed(_resolve(spec, fields["request"]), REQUEST_KEYS)
    _const(spec, request["location_code"], 2840)
    _const(spec, request["language_code"], "en")
    _const(spec, request["depth"], 3)
    _const(spec, request["limit"], 1000)
    _const(spec, request["offset"], 0)
    _const(spec, request["include_seed_keyword"], True)
    _const(spec, request["include_clickstream_data"], False)
    _const(spec, request["replace_with_core_keyword"], False)

    outcome = _closed(
        _resolve(spec, fields["capture_outcome"]),
        {"classification", "observation_count"},
    )
    classifications: set[object] = set()
    for option in _nonnull(spec, outcome["classification"]):
        classifications.update(option.get("enum", []))
        if "const" in option:
            classifications.add(option["const"])
    assert classifications == {"observation_admitted", "observation_admitted_empty"}

    context = _closed(_resolve(spec, fields["result_context"]), RESULT_CONTEXT_KEYS)
    for name in ("location_code", "language_code", "se_type"):
        _state_value(spec, context[name])

    keyword_data = _resolve(spec, _resolve(spec, fields["keyword_data"])["items"])
    fact = _closed(keyword_data, KEYWORD_DATA_FACT_KEYS)
    _const(spec, fact["observation_kind"], KEYWORD_DATA_KIND)
    for name in ("location_code", "language_code", "se_type"):
        _state_value(spec, fact[name])
    for name, expected_keys in _STRUCTURE_KEYS.items():
        structure = _state_value(spec, fact[name])
        child = _resolve(spec, _nonnull(spec, structure["value"])[0])
        child_fields = _closed(child, expected_keys)
        assert child.get("type") == "object"
        for child_name, child_schema in child_fields.items():
            if child_name.endswith("_state"):
                continue
            _state_value(spec, child_schema)
    occurrence = _resolve(spec, _resolve(spec, fact["occurrences"])["items"])
    _closed(occurrence, ITEM_OCCURRENCE_KEYS)

    monthly = _resolve(spec, _resolve(spec, fields["monthly_search_volume"])["items"])
    monthly_fields = _closed(monthly, MONTHLY_FACT_KEYS)
    _const(spec, monthly_fields["observation_kind"], MONTHLY_KIND)
    _closed(_resolve(spec, monthly_fields["data_period"]), {"year", "month"})
    _closed(
        _resolve(spec, _resolve(spec, monthly_fields["occurrences"])["items"]),
        MONTHLY_OCCURRENCE_KEYS,
    )

    relationship = _resolve(spec, _resolve(spec, fields["relationships"])["items"])
    relationship_fields = _closed(relationship, RELATIONSHIP_FACT_KEYS)
    _const(spec, relationship_fields["observation_kind"], RELATIONSHIP_KIND)
    _closed(
        _resolve(spec, _resolve(spec, relationship_fields["occurrences"])["items"]),
        RELATIONSHIP_OCCURRENCE_KEYS,
    )


def test_generated_openapi_teaches_the_required_distinctions(tmp_path: Path) -> None:
    spec = _spec(tmp_path)
    text = json.dumps(spec["paths"][HISTORY]) + json.dumps(spec["components"]["schemas"])
    lowered = text.lower()
    for phrase in (
        "capture documents, not observation envelopes",
        "not a tree",
        "frontier targets legitimately have none",
        "never computed",
        "canonical identity",
        "not pagination",
        "stated-empty array",
        "request-disabled",
        "structure-local provider clock",
        "not capture time",
        "never measured",
        "observation_admitted_empty",
        "observatory-derived",
        "requested_seed",
    ):
        assert phrase in lowered, phrase
    # Graph vocabulary appears only inside explicit denials, never as a claim.
    for denial in (
        "not a tree edge, bfs traversal, parent/child link, semantic similarity",
        "centrality, importance, or completeness",
        "not canonical identity",
        "neither is rank, importance, tree parentage, or keyword identity",
    ):
        assert denial in lowered, denial
    assert lowered.count("bfs") == lowered.count(
        "not a tree edge, bfs traversal, parent/child link, semantic similarity"
    )


# --------------------------------------------------------------------------------------
# Malformed projections fail closed
# --------------------------------------------------------------------------------------


def _minimal_envelope(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "provider": "dataforseo",
        "adapter_contract": RELATED_KEYWORDS_ADAPTER_CONTRACT,
        "requested_keyword": SEED,
        "derivation_version_id": RELATED_KEYWORDS_RECIPE_ID,
        "recipe_resolution": "selected",
        "observation_kinds": [KEYWORD_DATA_KIND, MONTHLY_KIND, RELATIONSHIP_KIND],
        "captures": [],
        "total_matching": 0,
        "returned_count": 0,
        "limit": 20,
        "order": "asc",
        "has_more": False,
    }
    payload.update(overrides)
    return payload


def test_minimal_envelope_validates() -> None:
    assert RelatedKeywordsHistoryEnvelope.model_validate(_minimal_envelope())


@pytest.mark.parametrize(
    "overrides",
    [
        {"unexpected": 1},
        {"observation_kinds": [KEYWORD_DATA_KIND, RELATIONSHIP_KIND, MONTHLY_KIND]},
        {"observation_kinds": [KEYWORD_DATA_KIND]},
        {"provider": "other"},
        {"requested_keyword": ""},
        {"total_matching": "0"},
        {"limit": 0},
        {"order": "ascending"},
    ],
)
def test_malformed_envelope_projection_fails_closed(overrides: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        RelatedKeywordsHistoryEnvelope.model_validate(_minimal_envelope(**overrides))


@pytest.mark.parametrize(
    "payload",
    [
        {"state": "stated", "value": None},
        {"state": "absent", "value": "x"},
        {"state": "json_null", "value": ""},
        {"state": "unknown", "value": None},
        {"state": "stated", "value": "x", "extra": 1},
        {"state": "stated"},
    ],
)
def test_state_value_disagreement_fails_closed(payload: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        RelatedKeywordsTextField.model_validate(payload)


@pytest.mark.parametrize(
    "payload",
    [
        {"classification": "observation_admitted", "observation_count": 0},
        {"classification": "observation_admitted_empty", "observation_count": 1},
        {"classification": "provider_error", "observation_count": 0},
    ],
)
def test_capture_outcome_classification_pairing_fails_closed(
    payload: dict[str, Any],
) -> None:
    with pytest.raises(ValidationError):
        RelatedKeywordsCaptureOutcome.model_validate(payload)


def test_decimal_fields_never_accept_binary_floats() -> None:
    with pytest.raises(ValidationError):
        RelatedKeywordsDecimalField.model_validate({"state": "stated", "value": 0.25})


# --------------------------------------------------------------------------------------
# Golden RK-02 content proof
# --------------------------------------------------------------------------------------


@pytest.fixture
def golden(
    tmp_path: Path, postgres_dsn: str
) -> Iterator[tuple[TestClient, EvidenceStore, str]]:
    body = FIXTURE.read_bytes()
    assert len(body) == FIXTURE_BYTES
    assert hashlib.sha256(body).hexdigest() == FIXTURE_SHA256
    store, _attempt_id, capture_id = _prepare(
        tmp_path, postgres_dsn, body=body, nonce="66" * 32
    )
    with _app(store, postgres_dsn) as client:
        yield client, store, capture_id


def _newest_monthly(
    capture: Mapping[str, Any], locus: str, keyword: str
) -> dict[str, Any] | None:
    points: list[dict[str, Any]] = [
        fact
        for fact in capture["monthly_search_volume"]
        if fact["locus"] == locus and fact["keyword"] == keyword
    ]
    if not points:
        return None
    return max(
        points, key=lambda fact: (fact["data_period"]["year"], fact["data_period"]["month"])
    )


def test_golden_rk02_capture_matches_persisted_state_and_evidence(
    golden: tuple[TestClient, EvidenceStore, str], postgres_dsn: str
) -> None:
    client, store, capture_id = golden
    capture = _one_capture(client)
    with connect(postgres_dsn) as connection:
        expected = _expected_capture(connection, store, capture_id)
    assert capture == expected

    assert len(capture["keyword_data"]) == GOLDEN_KEYWORD_DATA
    assert len(capture["monthly_search_volume"]) == GOLDEN_MONTHLY
    assert len(capture["relationships"]) == GOLDEN_RELATIONSHIP
    assert capture["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": GOLDEN_ENVELOPES,
    }
    assert (
        GOLDEN_KEYWORD_DATA + GOLDEN_MONTHLY + GOLDEN_RELATIONSHIP == GOLDEN_ENVELOPES
    )
    assert sum(len(fact["occurrences"]) for fact in capture["keyword_data"]) == (
        GOLDEN_ITEM_OCCURRENCES
    )
    assert sum(
        len(fact["occurrences"]) for fact in capture["monthly_search_volume"]
    ) == GOLDEN_MONTHLY_OCCURRENCES
    assert sum(len(fact["occurrences"]) for fact in capture["relationships"]) == (
        GOLDEN_RELATIONSHIP_OCCURRENCES
    )

    context = capture["result_context"]
    assert context["items_count"] == GOLDEN_ITEM_OCCURRENCES
    assert context["derived_returned_item_count"] == GOLDEN_ITEM_OCCURRENCES
    assert context["derived_relationship_occurrence_count"] == (
        GOLDEN_RELATIONSHIP_OCCURRENCES
    )
    assert context["seed_keyword"] == SEED

    structure_counts = {
        name: sum(
            1 for fact in capture["keyword_data"] if fact[name]["state"] == "stated"
        )
        for name in _STRUCTURE_KEYS
    }
    with connect(postgres_dsn) as connection:
        persisted = {
            table: len(_fetch(connection, table, capture_id))
            for table in GOLDEN_CHILD_ROWS
        }
    assert persisted == GOLDEN_CHILD_ROWS
    assert structure_counts == {
        "keyword_info": GOLDEN_CHILD_ROWS[KEYWORD_INFO_TABLE],
        "keyword_properties": GOLDEN_CHILD_ROWS[PROPERTIES_TABLE],
        "avg_backlinks": GOLDEN_CHILD_ROWS[BACKLINKS_TABLE],
        "search_intent": GOLDEN_CHILD_ROWS[INTENT_TABLE],
        "serp_info": GOLDEN_CHILD_ROWS[SERP_TABLE],
    }

    seed_facts = _by_keyword(capture["keyword_data"], SEED)
    assert [fact["locus"] for fact in seed_facts] == [LOCUS_SEED, LOCUS_ITEM]
    assert seed_facts[0]["within_capture_identity"] != (
        seed_facts[1]["within_capture_identity"]
    )
    assert seed_facts[0]["occurrences"] == []
    assert [entry["depth"] for entry in seed_facts[1]["occurrences"]] == [0]

    keyword_data_keywords = {fact["keyword"] for fact in capture["keyword_data"]}
    targets = {fact["target_keyword"] for fact in capture["relationships"]}
    assert FRONTIER_TARGET in targets
    assert FRONTIER_TARGET not in keyword_data_keywords
    assert not any(
        fact["keyword"] == FRONTIER_TARGET for fact in capture["monthly_search_volume"]
    )
    frontier = sorted(targets - keyword_data_keywords)
    assert FRONTIER_TARGET in frontier

    duplicates = _by_keyword(capture["keyword_data"], DUPLICATE_CATEGORY_KEYWORD)
    assert duplicates
    assert duplicates[0]["keyword_info"]["value"]["categories"]["value"] == (
        DUPLICATE_CATEGORIES
    )

    depth_zero = seed_facts[1]
    assert depth_zero["keyword_info"]["value"]["keyword_info_last_updated_time"] == {
        "state": "stated",
        "value": DEPTH_ZERO_CLOCKS["keyword_info_last_updated_time"],
    }
    assert depth_zero["avg_backlinks"]["value"]["avg_backlinks_last_updated_time"] == {
        "state": "stated",
        "value": DEPTH_ZERO_CLOCKS["avg_backlinks_last_updated_time"],
    }
    assert depth_zero["search_intent"]["value"]["search_intent_last_updated_time"] == {
        "state": "stated",
        "value": DEPTH_ZERO_CLOCKS["search_intent_last_updated_time"],
    }
    assert depth_zero["serp_info"]["value"]["serp_last_updated_time"] == {
        "state": "stated",
        "value": DEPTH_ZERO_CLOCKS["serp_last_updated_time"],
    }
    assert depth_zero["serp_info"]["value"]["serp_previous_updated_time"] == {
        "state": "stated",
        "value": DEPTH_ZERO_CLOCKS["serp_previous_updated_time"],
    }
    year_one = [
        fact["keyword"]
        for fact in capture["keyword_data"]
        if fact["serp_info"]["state"] == "stated"
        and fact["serp_info"]["value"]["serp_last_updated_time"]["value"]
        == YEAR_ONE_CLOCK
    ]
    assert year_one

    returned = [
        fact for fact in capture["keyword_data"] if fact["locus"] == LOCUS_ITEM
    ]
    assert len(returned) == GOLDEN_KEYWORD_DATA - 1
    disagreements = 0
    for fact in returned:
        info = fact["keyword_info"]
        if info["state"] != "stated":
            continue
        current = info["value"]["search_volume"]
        newest = _newest_monthly(capture, LOCUS_ITEM, fact["keyword"])
        if current["state"] != "stated" or newest is None:
            continue
        if current["value"] != newest["search_volume"]:
            disagreements += 1
    assert disagreements == 63


# --------------------------------------------------------------------------------------
# Surface isolation
# --------------------------------------------------------------------------------------

SIBLING_HISTORY_ROUTES = (
    "/v1/providers/dataforseo/google/keyword-overview/history",
    "/v1/providers/dataforseo/google/organic/history",
    "/v1/providers/dataforseo/google/ai-optimization/search-mentions/history",
    "/v1/providers/dataforseo/google/ai-optimization/target-metrics/history",
    "/v1/providers/dataforseo/google/ai-optimization/llm-mentions-historical/history",
)


def test_sibling_provider_surfaces_remain_unselected_and_isolated(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    assert _history(client).status_code == 200
    for route in SIBLING_HISTORY_ROUTES:
        response = client.get(route + "?" + urlencode({"requested_keyword": SEED}))
        assert response.status_code == 503, route
        assert response.json() == {"detail": NOT_SELECTED_SIGNAL}, route


def test_openapi_adds_exactly_one_related_keywords_path(tmp_path: Path) -> None:
    paths = set(_spec(tmp_path)["paths"])
    assert HISTORY in paths
    assert {path for path in paths if "related-keywords" in path} == {HISTORY}
    for route in SIBLING_HISTORY_ROUTES:
        assert route in paths
    assert "/v1/attempts/{attempt_id}" in paths


def test_history_is_bound_to_its_exact_subject(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence-subjects")
    _commit(store, default_body(), "77" * 32, keyword=SEED, suffix="1")
    _commit(store, simple_body([item("delta")]), "78" * 32, keyword=OTHER_SEED, suffix="2")
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_related_keywords(store, connection)
        select_provider_recipe(
            connection, RELATED_KEYWORDS_ADAPTER_CONTRACT, RELATED_KEYWORDS_RECIPE_ID
        )
    with _app(store, postgres_dsn) as client:
        first = _one_capture(client, SEED)
        second = _one_capture(client, OTHER_SEED)
        upper = _history(client, SEED.upper())
    assert first["request"]["keyword"] == SEED
    assert second["request"]["keyword"] == OTHER_SEED
    assert {fact["requested_seed"] for fact in first["keyword_data"]} == {SEED}
    assert {fact["requested_seed"] for fact in second["keyword_data"]} == {OTHER_SEED}
    assert upper.status_code == 200
    _assert_envelope(upper.json(), total_matching=0, returned_count=0)
