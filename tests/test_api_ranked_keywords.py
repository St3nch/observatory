"""RANK-06: Ranked Keywords Recipe selection and admitted-history API.

Most adversarial proofs run on a small synthetic Capture so the PostgreSQL loop stays
bounded. The frozen RANK-03/RANK-04 fixture is reserved for the golden content proof, where
its rich provider testimony is what is being proved.

The golden proof projects persisted PostgreSQL rows plus verified Evidence into expected
JSON through this module's own independent projector, which discovers relations from
`information_schema` rather than from the production reader's column tuples. The production
assembler is never used to build the expected value.

Damage that PostgreSQL foreign keys would refuse is planted with
`SET session_replication_role = replica`, which disables referential triggers while leaving
CHECK constraints active. That is a test construction seam only.
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
    RANKED_KEYWORDS_ADAPTER_CONTRACT,
    RELATED_KEYWORDS_ADAPTER_CONTRACT,
    body_ref,
    ranked_keywords_http_attempt_document,
    ranked_keywords_http_capture_document,
    related_keywords_http_attempt_document,
    related_keywords_http_capture_document,
)
from observatory.dataforseo_google_ranked_keywords import (
    CORPUS_METRICS_KIND,
    KEYWORD_DATA_KIND,
    MONTHLY_KIND,
    RANKED_RESULT_KIND,
)
from observatory.dataforseo_google_ranked_keywords_paid_probe import (
    closed_ranked_keywords_parameters,
    ranked_keywords_request_body_bytes,
)
from observatory.dataforseo_google_related_keywords import (
    RELATED_KEYWORDS_RECIPE,
    RELATED_KEYWORDS_RECIPE_ID,
)
from observatory.dataforseo_google_related_keywords_paid_probe import (
    closed_related_keywords_parameters,
    related_keywords_request_body_bytes,
)
from observatory.evidence_store import EvidenceStore, create_store
from observatory.google_ranked_keywords_derive import (
    BACKLINKS_TABLE,
    CONTEXT_TABLE,
    CORPUS_METRICS_TABLE,
    INTENT_TABLE,
    ITEM_OCCURRENCES_TABLE,
    KEYWORD_DATA_TABLE,
    KEYWORD_INFO_TABLE,
    KEYWORD_SERP_TABLE,
    MONTHLY_OCCURRENCES_TABLE,
    MONTHLY_TABLE,
    PROPERTIES_TABLE,
    RANK05_TABLES,
    RANKED_KEYWORDS_RECIPE,
    RANKED_KEYWORDS_RECIPE_ID,
    RANKED_RESULTS_TABLE,
    derive_google_ranked_keywords,
)
from observatory.google_related_keywords_derive import derive_google_related_keywords
from observatory.migrate import apply_migrations, connect
from observatory.provider_recipe import (
    IDENTITY_SCHEMA,
    IDENTITY_VERSION,
    observation_identity,
    recipe_bytes,
    recipe_derivation_version_id,
    register_provider_recipe,
    validate_recipe,
)
from observatory.provider_recipe_selection import (
    NOT_SELECTED_SIGNAL,
    select_provider_recipe,
)
from observatory.ranked_keywords_read import (
    BACKLINKS_COLUMNS,
    CORPUS_METRICS_COLUMNS,
    INTENT_COLUMNS,
    ITEM_OCCURRENCE_COLUMNS,
    KEYWORD_DATA_COLUMNS,
    KEYWORD_INFO_COLUMNS,
    KEYWORD_SERP_COLUMNS,
    MONTHLY_COLUMNS,
    MONTHLY_OCCURRENCE_COLUMNS,
    PROPERTIES_COLUMNS,
    RANKED_RESULT_COLUMNS,
    RankedKeywordsCorpusMetricsFact,
    RankedKeywordsDecimalField,
    RankedKeywordsHistoryEnvelope,
    RankedKeywordsRankChanges,
    RankedKeywordsTextField,
)
from observatory.settings import Settings

HISTORY = "/v1/providers/dataforseo/google/ranked-keywords/history"
RELATED_HISTORY = "/v1/providers/dataforseo/google/related-keywords/history"
INTEGRITY_SIGNAL = "evidence_integrity_failure"
TARGET = "theconspiratory.com"
OTHER_TARGET = "unmeasured-target.com"

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_google_ranked_keywords_rank03.json"
)
FIXTURE_BYTES = 390955
FIXTURE_SHA256 = "5b0e7cb6a03a921039a2845c62bd6a91eba9d61e2b54240e9af15414ba1fbc84"

# Frozen-Capture consequences of the accepted RANK-05 model. Golden test facts only; the
# production reader must never treat them as provider invariants.
GOLDEN_CORPUS = 10
GOLDEN_RANKED_RESULTS = 100
GOLDEN_KEYWORD_DATA = 100
GOLDEN_MONTHLY = 1200
GOLDEN_ENVELOPES = 1410
GOLDEN_ITEM_OCCURRENCES = 100
GOLDEN_MONTHLY_OCCURRENCES = 1200
GOLDEN_TOTAL_COUNT = 248
GOLDEN_ITEMS_COUNT = 100
GOLDEN_UNIQUE_URLS = 57

BUCKET_NAMES = (
    "pos_1",
    "pos_2_3",
    "pos_4_10",
    "pos_11_20",
    "pos_21_30",
    "pos_31_40",
    "pos_41_50",
    "pos_51_60",
    "pos_61_70",
    "pos_71_80",
    "pos_81_90",
    "pos_91_100",
)
MOVEMENT_NAMES = ("is_new", "is_up", "is_down", "is_lost")
CLICKSTREAM_AGGREGATE_NAMES = (
    "clickstream_etv",
    "clickstream_gender_distribution",
    "clickstream_age_distribution",
)
AGGREGATE_FAMILIES = (
    "organic",
    "paid",
    "featured_snippet",
    "local_pack",
    "ai_overview_reference",
)
RANK_SYSTEMS = ("rank_group", "rank_absolute")
CORPUS_COMBINATIONS = {
    (family, system) for family in AGGREGATE_FAMILIES for system in RANK_SYSTEMS
}

CLOCK = "2026-08-31 12:00:00 +00:00"
PREVIOUS_CLOCK = "2026-07-31 12:00:00 +00:00"
KEYWORD_SERP_CLOCK = "2026-08-30 09:15:00 +00:00"
YEAR_ONE_CLOCK = "0001-01-01 00:00:00 +00:00"

HISTORY_KEYS = {
    "provider",
    "adapter_contract",
    "requested_target",
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
    "corpus_metrics",
    "ranked_results",
    "keyword_data",
    "monthly_search_volume",
    "item_occurrences",
}
REQUEST_KEYS = {
    "target",
    "location_code",
    "language_code",
    "item_types",
    "ignore_synonyms",
    "include_clickstream_data",
    "limit",
    "offset",
    "load_rank_absolute",
    "historical_serp_mode",
    "order_by",
}
RESULT_CONTEXT_KEYS = {
    "target",
    "location_code",
    "language_code",
    "se_type",
    "total_count",
    "items_count",
}
READONLY_TABLES = (
    "provider_recipes",
    "provider_recipe_selections",
    "outcomes",
    "observation_envelopes",
    *RANK05_TABLES,
)
_IDENTITY_COLUMNS = frozenset(
    {"capture_id", "derivation_version_id", "within_capture_identity", "observation_kind"}
)
# Enclosing keyword-data state column -> (API key, child relation).
_ENCLOSING: dict[str, tuple[str, str]] = {
    "keyword_info_state": ("keyword_info", KEYWORD_INFO_TABLE),
    "keyword_properties_state": ("keyword_properties", PROPERTIES_TABLE),
    "avg_backlinks_state": ("avg_backlinks", BACKLINKS_TABLE),
    "search_intent_state": ("search_intent", INTENT_TABLE),
    "keyword_serp_info_state": ("keyword_serp_info", KEYWORD_SERP_TABLE),
}
_RANKED_FACT_LEVEL = {
    "requested_target",
    "keyword",
    "serp_item_type",
    "rank_group",
    "rank_absolute",
}
_FAMILY_RANK = {family: index for index, family in enumerate(AGGREGATE_FAMILIES)}
_SYSTEM_RANK = {system: index for index, system in enumerate(RANK_SYSTEMS)}

OMIT: Any = object()


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


def buckets(**overrides: Any) -> dict[str, Any]:
    values: dict[str, Any] = {name: 0 for name in BUCKET_NAMES}
    values.update(overrides)
    return values


def metrics_family(**overrides: Any) -> dict[str, Any]:
    family: dict[str, Any] = {
        **buckets(),
        **{name: 0 for name in MOVEMENT_NAMES},
        **{name: None for name in CLICKSTREAM_AGGREGATE_NAMES},
        "count": 0,
        "etv": 0,
        "estimated_paid_traffic_cost": 0,
    }
    family.update(overrides)
    return family


def metrics_absolute_family(**overrides: Any) -> dict[str, Any]:
    family: dict[str, Any] = {
        **buckets(),
        **{name: 0 for name in MOVEMENT_NAMES},
        **{name: None for name in CLICKSTREAM_AGGREGATE_NAMES},
    }
    family.update(overrides)
    return family


def all_metrics(**per_family: Any) -> dict[str, Any]:
    return {name: per_family.get(name, metrics_family()) for name in AGGREGATE_FAMILIES}


def all_metrics_absolute(**per_family: Any) -> dict[str, Any]:
    return {
        name: per_family.get(name, metrics_absolute_family())
        for name in AGGREGATE_FAMILIES
    }


def serp_item(**overrides: Any) -> dict[str, Any]:
    item: dict[str, Any] = {
        "type": "organic",
        "rank_group": 1,
        "rank_absolute": 1,
        "url": "https://theconspiratory.com/a",
        "se_type": "google",
        "position": "left",
        "xpath": "/html[1]/body[1]/div[1]",
        "domain": "theconspiratory.com",
        "main_domain": "theconspiratory.com",
        "website_name": "The Conspiratory",
        "relative_url": "/a",
        "breadcrumb": "https://theconspiratory.com > a",
        "title": "A title",
        "description": "A description",
        "pre_snippet": "Aug 1, 2026",
        "highlighted": ["a"],
        "is_image": False,
        "is_video": False,
        "is_featured_snippet": False,
        "is_malicious": False,
        "amp_version": False,
        "etv": 1.5,
        "estimated_paid_traffic_cost": 2.5,
        "clickstream_etv": None,
        "rank_changes": {
            "is_new": False,
            "is_up": False,
            "is_down": True,
            "previous_rank_absolute": 3,
        },
        "rank_info": {"page_rank": 7, "main_domain_rank": 11},
        "about_this_result": None,
        "backlinks_info": None,
        "extended_snippet": None,
        "links": None,
        "rating": None,
    }
    item.update(overrides)
    return {key: value for key, value in item.items() if value is not OMIT}


def ranked_serp_element(**overrides: Any) -> dict[str, Any]:
    element: dict[str, Any] = {
        "se_type": "google",
        "check_url": "https://www.google.com/search?q=alpha",
        "se_results_count": 1234,
        "keyword_difficulty": 30,
        "is_lost": False,
        "last_updated_time": CLOCK,
        "previous_updated_time": PREVIOUS_CLOCK,
        "serp_item_types": ["organic", "organic", "ai_overview"],
        "serp_item": serp_item(),
    }
    element.update(overrides)
    return {key: value for key, value in element.items() if value is not OMIT}


def keyword_info(**overrides: Any) -> dict[str, Any]:
    info: dict[str, Any] = {
        "se_type": "google",
        "last_updated_time": CLOCK,
        "competition": 0.25,
        "competition_level": "LOW",
        "cpc": 1.5,
        "search_volume": 100,
        "low_top_of_page_bid": 0.5,
        "high_top_of_page_bid": 2.5,
        "categories": [10013, 10013, 10106],
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
        "last_updated_time": PREVIOUS_CLOCK,
    }
    document.update(overrides)
    return {key: value for key, value in document.items() if value is not OMIT}


def intent(**overrides: Any) -> dict[str, Any]:
    document: dict[str, Any] = {
        "se_type": "google",
        "main_intent": "informational",
        "foreign_intent": ["commercial", "commercial"],
        "last_updated_time": YEAR_ONE_CLOCK,
    }
    document.update(overrides)
    return {key: value for key, value in document.items() if value is not OMIT}


def keyword_serp_info(**overrides: Any) -> dict[str, Any]:
    document: dict[str, Any] = {
        "se_type": "google",
        "check_url": "https://www.google.com/search?q=alpha-keyword-path",
        "serp_item_types": ["organic", "people_also_ask"],
        "se_results_count": 4321,
        "last_updated_time": KEYWORD_SERP_CLOCK,
        "previous_updated_time": YEAR_ONE_CLOCK,
    }
    document.update(overrides)
    return {key: value for key, value in document.items() if value is not OMIT}


def keyword_data(keyword: str, **overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {"keyword": keyword}
    data.update(overrides)
    return {key: value for key, value in data.items() if value is not OMIT}


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
        "serp_info": keyword_serp_info(),
    }
    document.update(overrides)
    return {key: value for key, value in document.items() if value is not OMIT}


def item(
    keyword: str = "alpha",
    *,
    data: Any = None,
    element: Any = None,
    se_type: str = "google",
) -> dict[str, Any]:
    return {
        "se_type": se_type,
        "keyword_data": keyword_data(keyword) if data is None else data,
        "ranked_serp_element": ranked_serp_element() if element is None else element,
    }


def result_document(
    items: list[dict[str, Any]],
    *,
    target: str = TARGET,
    total_count: int | None = None,
    metrics: dict[str, Any] | None = None,
    metrics_absolute: dict[str, Any] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "se_type": "google",
        "target": target,
        "location_code": 2840,
        "language_code": "en",
        "items": items,
        "items_count": len(items),
        "total_count": len(items) if total_count is None else total_count,
        "metrics": all_metrics() if metrics is None else metrics,
        "metrics_absolute": (
            all_metrics_absolute() if metrics_absolute is None else metrics_absolute
        ),
    }
    if extra:
        result.update(extra)
    return result


def synthetic_body(result: dict[str, Any] | None) -> bytes:
    results = [] if result is None else [result]
    document: dict[str, Any] = {
        "version": "0.1.20260101",
        "status_code": 20000,
        "status_message": "Ok.",
        "time": "0.5 sec.",
        "cost": 0.05,
        "tasks_count": 1,
        "tasks_error": 0,
        "tasks": [
            {
                "id": "task-1",
                "status_code": 20000,
                "status_message": "Ok.",
                "time": "0.5 sec.",
                "cost": 0.05,
                "result_count": len(results),
                "path": ["v3", "dataforseo_labs", "google", "ranked_keywords", "live"],
                "data": {
                    "api": "dataforseo_labs",
                    "function": "ranked_keywords",
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
    """One small admitted Capture exercising every projected Ranked structure.

    Item 0 is fully enriched. Item 1 keeps only a stated `keyword_info` with a JSON-null
    `search_volume_trend` and a stated-but-empty `monthly_searches`, so its trend members
    stay `inapplicable` and it contributes zero monthly facts. Item 2 repeats item 0's exact
    keyword enrichment at a different placement, so one keyword-data parent and one monthly
    parent legitimately carry two returned-item occurrences.
    """

    duplicate_element = ranked_serp_element(
        serp_item=serp_item(rank_group=3, rank_absolute=3, url="https://theconspiratory.com/c")
    )
    sparse_element = ranked_serp_element(
        check_url=None,
        keyword_difficulty=OMIT,
        serp_item=serp_item(
            rank_group=2,
            rank_absolute=2,
            url="https://theconspiratory.com/b",
            position=None,
            title=OMIT,
            breadcrumb=None,
            pre_snippet=OMIT,
            highlighted=OMIT,
            etv=OMIT,
            rank_changes=None,
            rank_info=OMIT,
        ),
    )
    return simple_body(
        [
            item("alpha", data=rich_keyword_data("alpha")),
            item(
                "beta",
                data=keyword_data(
                    "beta",
                    keyword_info=keyword_info(
                        monthly_searches=[],
                        search_volume_trend=None,
                        categories=None,
                        competition=OMIT,
                    ),
                ),
                element=sparse_element,
            ),
            item("alpha", data=rich_keyword_data("alpha"), element=duplicate_element),
        ],
        total_count=248,
    )


# Consequences of `default_body()`, recomputed by the envelope assertions below.
SMALL_CORPUS = 10
SMALL_RANKED = 3
SMALL_KEYWORDS = 2
SMALL_MONTHLY = 1
SMALL_ENVELOPES = SMALL_CORPUS + SMALL_RANKED + SMALL_KEYWORDS + SMALL_MONTHLY
SMALL_ITEMS = 3


# --------------------------------------------------------------------------------------
# Evidence and application helpers
# --------------------------------------------------------------------------------------


def _params(target: str = TARGET) -> dict[str, object]:
    return closed_ranked_keywords_parameters(target=target)


def _attempt_document(nonce: str, target: str) -> dict[str, object]:
    return ranked_keywords_http_attempt_document(
        parameters=_params(target),
        attempt_nonce=nonce,
        authorized_at="2026-09-01T10:00:00.000000Z",
        observatory_version="rank06-test-v1",
    )


def _commit(
    store: EvidenceStore,
    body: bytes,
    nonce: str,
    *,
    target: str = TARGET,
    suffix: str = "1",
) -> tuple[str, str]:
    attempt = _attempt_document(nonce, target)
    attempt_id = store.commit_attempt(
        attempt, request_body=ranked_keywords_request_body_bytes(_params(target))
    )
    capture = ranked_keywords_http_capture_document(
        attempt=attempt,
        request_started_at=f"2026-09-01T10:00:0{suffix}.100000Z",
        transport_ended_at=f"2026-09-01T10:00:0{suffix}.400000Z",
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
        response_headers_at=f"2026-09-01T10:00:0{suffix}.200000Z",
        response_body_ended_at=f"2026-09-01T10:00:0{suffix}.300000Z",
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


def _history(client: TestClient, target: str = TARGET, **query: object) -> Any:
    params = {"requested_target": target, **query}
    return client.get(HISTORY + "?" + urlencode(params, doseq=True))


def _prepare(
    tmp_path: Path,
    postgres_dsn: str,
    *,
    body: bytes | None = None,
    nonce: str = "11" * 32,
    target: str = TARGET,
    select: bool = True,
    derive: bool = True,
) -> tuple[EvidenceStore, str, str]:
    store = create_store(tmp_path / f"evidence-{nonce[:8]}")
    attempt_id, capture_id = _commit(
        store, body if body is not None else default_body(), nonce, target=target
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        if derive:
            derive_google_ranked_keywords(store, connection)
        else:
            register_provider_recipe(connection, RANKED_KEYWORDS_RECIPE)
        if select:
            select_provider_recipe(
                connection, RANKED_KEYWORDS_ADAPTER_CONTRACT, RANKED_KEYWORDS_RECIPE_ID
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
    target: str = TARGET,
) -> list[dict[str, Any]]:
    assert set(body) == HISTORY_KEYS
    assert "requested_keyword" not in body
    assert body["provider"] == "dataforseo"
    assert body["adapter_contract"] == RANKED_KEYWORDS_ADAPTER_CONTRACT
    assert body["requested_target"] == target
    assert body["derivation_version_id"] == RANKED_KEYWORDS_RECIPE_ID
    assert body["recipe_resolution"] == resolution
    assert body["observation_kinds"] == [
        CORPUS_METRICS_KIND,
        KEYWORD_DATA_KIND,
        MONTHLY_KIND,
        RANKED_RESULT_KIND,
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


def _one_capture(client: TestClient, target: str = TARGET, **query: object) -> dict[str, Any]:
    response = _history(client, target, **query)
    assert response.status_code == 200, response.text
    captures = _assert_envelope(
        response.json(), total_matching=1, returned_count=1, target=target
    )
    return captures[0]


# --------------------------------------------------------------------------------------
# Independent expected-JSON projection.
#
# Relations are discovered from information_schema, not from the reader's column tuples,
# and value/state pairs are grouped by column naming alone. The grouping rules below are
# this module's own restatement of the accepted RANK-06 shape. The production reader and
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
    statement = sql.SQL(
        "SELECT {} FROM {} WHERE derivation_version_id = %s AND capture_id = %s"
    )
    rows = connection.execute(
        statement.format(
            sql.SQL(", ").join(sql.Identifier(column) for column in columns),
            sql.Identifier(table),
        ),
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
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


def _expected_corpus(connection: Any, capture_id: str) -> list[dict[str, Any]]:
    columns = _content_columns(connection, CORPUS_METRICS_TABLE)
    facts: list[dict[str, Any]] = []
    for row in _fetch(connection, CORPUS_METRICS_TABLE, capture_id):
        payload = _project(columns, row)
        position_buckets = {name: payload.pop(name) for name in BUCKET_NAMES}
        movement_counts = {name: payload.pop(name) for name in MOVEMENT_NAMES}
        facts.append(
            {
                "observation_kind": str(row["observation_kind"]),
                "within_capture_identity": str(row["within_capture_identity"]),
                **payload,
                "position_buckets": position_buckets,
                "movement_counts": movement_counts,
            }
        )
    facts.sort(
        key=lambda fact: (
            _FAMILY_RANK[fact["aggregate_family"]],
            _SYSTEM_RANK[fact["rank_system"]],
            fact["within_capture_identity"],
        )
    )
    return facts


def _expected_ranked(connection: Any, capture_id: str) -> list[dict[str, Any]]:
    columns = _content_columns(connection, RANKED_RESULTS_TABLE)
    facts: list[dict[str, Any]] = []
    for row in _fetch(connection, RANKED_RESULTS_TABLE, capture_id):
        payload = _project(columns, row)
        element = {
            key[len("ranked_element_") :]: payload.pop(key)
            for key in list(payload)
            if key.startswith("ranked_element_")
        }
        rank_changes = {"state": payload.pop("rank_changes_state")}
        for member in ("is_new", "is_up", "is_down", "previous_rank_absolute"):
            rank_changes[member] = payload.pop(f"rank_changes_{member}")
        rank_info = {"state": payload.pop("rank_info_state")}
        for member in ("page_rank", "main_domain_rank"):
            rank_info[member] = payload.pop(f"rank_info_{member}")
        fact_level = {key: payload.pop(key) for key in sorted(_RANKED_FACT_LEVEL)}
        serp = {
            ("se_type" if key == "serp_item_se_type" else key): value
            for key, value in payload.items()
        }
        serp["rank_changes"] = rank_changes
        serp["rank_info"] = rank_info
        facts.append(
            {
                "observation_kind": str(row["observation_kind"]),
                "within_capture_identity": str(row["within_capture_identity"]),
                **fact_level,
                "ranked_element": element,
                "serp_item": serp,
            }
        )
    facts.sort(
        key=lambda fact: (
            fact["keyword"],
            fact["serp_item_type"],
            fact["rank_group"],
            fact["rank_absolute"],
            fact["within_capture_identity"],
        )
    )
    return facts


def _expected_keyword_info(columns: Sequence[str], row: Mapping[str, Any]) -> dict[str, Any]:
    payload = _project(columns, row)
    trend: dict[str, Any] = {"state": payload.pop("search_volume_trend_state")}
    for member in ("monthly", "quarterly", "yearly"):
        trend[member] = payload.pop(f"trend_{member}")
    payload["search_volume_trend"] = trend
    return payload


def _expected_keyword_data(connection: Any, capture_id: str) -> list[dict[str, Any]]:
    parent_columns = _content_columns(connection, KEYWORD_DATA_TABLE)
    children = {
        table: {
            str(row["within_capture_identity"]): row
            for row in _fetch(connection, table, capture_id)
        }
        for _name, table in _ENCLOSING.values()
    }
    facts: list[dict[str, Any]] = []
    for row in _fetch(connection, KEYWORD_DATA_TABLE, capture_id):
        identity = str(row["within_capture_identity"])
        payload = _project(parent_columns, row)
        for state_column, (name, table) in _ENCLOSING.items():
            state = payload.pop(state_column)
            child = children[table].get(identity)
            if state == "stated" and child is not None:
                child_columns = _content_columns(connection, table)
                value = (
                    _expected_keyword_info(child_columns, child)
                    if name == "keyword_info"
                    else _project(child_columns, child)
                )
            else:
                value = None
            payload[name] = {"state": state, "value": value}
        facts.append(
            {
                "observation_kind": str(row["observation_kind"]),
                "within_capture_identity": identity,
                **payload,
            }
        )
    facts.sort(key=lambda fact: (fact["keyword"], fact["within_capture_identity"]))
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
            fact["keyword"],
            fact["data_period"]["year"],
            fact["data_period"]["month"],
            fact["within_capture_identity"],
        )
    )
    return facts


def _expected_item_occurrences(connection: Any, capture_id: str) -> list[dict[str, Any]]:
    columns = _content_columns(connection, ITEM_OCCURRENCES_TABLE)
    rows = [
        _project(columns, row)
        for row in _fetch(connection, ITEM_OCCURRENCES_TABLE, capture_id)
    ]
    rows.sort(key=lambda entry: entry["item_index"])
    return rows


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
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    ).fetchone()
    assert outcome is not None
    return {
        "attempt_id": attempt_id,
        "capture_id": capture_id,
        "provider": "dataforseo",
        "adapter_contract": RANKED_KEYWORDS_ADAPTER_CONTRACT,
        "derivation_version_id": RANKED_KEYWORDS_RECIPE_ID,
        "authorized_at": attempt["authorized_at"],
        "request_started_at": capture["request_started_at"],
        "transport_ended_at": capture["transport_ended_at"],
        "request": {key: parameters[key] for key in REQUEST_KEYS},
        "capture_outcome": {
            "classification": str(outcome[0]),
            "observation_count": int(outcome[1]),
        },
        "result_context": {
            "target": {
                "state": context["result_target_state"],
                "value": context["result_target"],
            },
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
        },
        "corpus_metrics": _expected_corpus(connection, capture_id),
        "ranked_results": _expected_ranked(connection, capture_id),
        "keyword_data": _expected_keyword_data(connection, capture_id),
        "monthly_search_volume": _expected_monthly(connection, capture_id),
        "item_occurrences": _expected_item_occurrences(connection, capture_id),
    }


def _second_ranked_keywords_recipe() -> dict[str, object]:
    """A registered non-v1 Recipe for the exact same adapter."""

    document = copy.deepcopy(RANKED_KEYWORDS_RECIPE)
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
    assert capture["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": SMALL_ENVELOPES,
    }
    assert len(capture["corpus_metrics"]) == SMALL_CORPUS
    assert len(capture["ranked_results"]) == SMALL_RANKED
    assert len(capture["keyword_data"]) == SMALL_KEYWORDS
    assert len(capture["monthly_search_volume"]) == SMALL_MONTHLY
    assert len(capture["item_occurrences"]) == SMALL_ITEMS


def test_small_capture_matches_the_independent_projection(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, store, _attempt_id, capture_id = ready
    capture = _one_capture(client)
    with connect(postgres_dsn) as connection:
        expected = _expected_capture(connection, store, capture_id)
    assert capture == expected


def test_explicit_pin_reports_pinned_resolution(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn, select=False)
    with _app(store, postgres_dsn) as client:
        response = _history(client, derivation_version_id=RANKED_KEYWORDS_RECIPE_ID)
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


@pytest.mark.parametrize("pin", ["not-a-digest", "AB" * 32, "f" * 64, ""])
def test_malformed_or_unknown_pin_is_404(
    ready: tuple[TestClient, EvidenceStore, str, str], pin: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    response = _history(client, derivation_version_id=pin)
    assert response.status_code == 404


def test_wrong_adapter_pin_is_404(tmp_path: Path, postgres_dsn: str) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, RELATED_KEYWORDS_RECIPE)
    with _app(store, postgres_dsn) as client:
        response = _history(client, derivation_version_id=RELATED_KEYWORDS_RECIPE_ID)
    assert response.status_code == 404


def test_registered_non_v1_ranked_recipe_pin_is_404(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    other = _second_ranked_keywords_recipe()
    with connect(postgres_dsn) as connection:
        registered = register_provider_recipe(connection, other)
    assert registered.derivation_version_id != RANKED_KEYWORDS_RECIPE_ID
    with _app(store, postgres_dsn) as client:
        response = _history(
            client, derivation_version_id=registered.derivation_version_id
        )
    assert response.status_code == 404


def test_selecting_a_non_v1_recipe_for_this_adapter_is_404(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    other = _second_ranked_keywords_recipe()
    with connect(postgres_dsn) as connection:
        registered = register_provider_recipe(connection, other)
        select_provider_recipe(
            connection,
            RANKED_KEYWORDS_ADAPTER_CONTRACT,
            registered.derivation_version_id,
        )
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    assert response.status_code == 404


def test_non_canonical_recipe_bytes_are_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    padded = b" " + json.dumps(RANKED_KEYWORDS_RECIPE).encode("utf-8")
    _damage(
        postgres_dsn,
        "UPDATE provider_recipes SET recipe_canonical_bytes = %s"
        " WHERE derivation_version_id = %s",
        (padded, RANKED_KEYWORDS_RECIPE_ID),
    )
    _assert_409(_history(client))


def test_recipe_bytes_that_are_not_a_closed_recipe_are_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    _damage(
        postgres_dsn,
        "UPDATE provider_recipes SET recipe_canonical_bytes = %s"
        " WHERE derivation_version_id = %s",
        (b"{}", RANKED_KEYWORDS_RECIPE_ID),
    )
    _assert_409(_history(client))


def test_recipe_kind_list_damage_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    document = copy.deepcopy(RANKED_KEYWORDS_RECIPE)
    kinds = document["observation_kinds"]
    assert isinstance(kinds, list)
    document["observation_kinds"] = list(reversed(kinds))
    _damage(
        postgres_dsn,
        "UPDATE provider_recipes SET recipe_canonical_bytes = %s"
        " WHERE derivation_version_id = %s",
        (json.dumps(document).encode("utf-8"), RANKED_KEYWORDS_RECIPE_ID),
    )
    _assert_409(_history(client))


def test_recipe_capture_taxonomy_damage_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    document = copy.deepcopy(RANKED_KEYWORDS_RECIPE)
    admission = document["admission"]
    assert isinstance(admission, dict)
    admission["capture_outcomes"] = [
        *admission["capture_outcomes"],
        "observation_admitted_empty",
    ]
    _damage(
        postgres_dsn,
        "UPDATE provider_recipes SET recipe_canonical_bytes = %s"
        " WHERE derivation_version_id = %s",
        (json.dumps(document).encode("utf-8"), RANKED_KEYWORDS_RECIPE_ID),
    )
    _assert_409(_history(client))


def test_recipe_provider_column_damage_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    _damage(
        postgres_dsn,
        "UPDATE provider_recipes SET provider = %s WHERE derivation_version_id = %s",
        ("other", RANKED_KEYWORDS_RECIPE_ID),
    )
    _assert_409(_history(client))


def test_selected_accepted_v1_adapter_metadata_damage_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    """Damaged accepted-v1 adapter metadata is integrity failure, never a selection miss."""

    client, _store, _attempt_id, _capture_id = ready
    _damage(
        postgres_dsn,
        "UPDATE provider_recipes SET adapter_contract = %s"
        " WHERE derivation_version_id = %s",
        ("other-adapter", RANKED_KEYWORDS_RECIPE_ID),
    )
    _assert_409(_history(client))


def test_pinned_accepted_v1_adapter_metadata_damage_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    """The pinned path reaches the same guard with no current selection at all."""

    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn, select=False)
    _damage(
        postgres_dsn,
        "UPDATE provider_recipes SET adapter_contract = %s"
        " WHERE derivation_version_id = %s",
        ("other-adapter", RANKED_KEYWORDS_RECIPE_ID),
    )
    with _app(store, postgres_dsn) as client:
        _assert_409(
            _history(client, derivation_version_id=RANKED_KEYWORDS_RECIPE_ID)
        )


def test_adapter_metadata_guard_is_scoped_to_the_exact_accepted_digest(
    tmp_path: Path, postgres_dsn: str
) -> None:
    """Another registered Recipe keeps its generic 404 even beside the damaged row."""

    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, RELATED_KEYWORDS_RECIPE)
    _damage(
        postgres_dsn,
        "UPDATE provider_recipes SET adapter_contract = %s"
        " WHERE derivation_version_id = %s",
        ("other-adapter", RANKED_KEYWORDS_RECIPE_ID),
    )
    with _app(store, postgres_dsn) as client:
        wrong_adapter = _history(
            client, derivation_version_id=RELATED_KEYWORDS_RECIPE_ID
        )
        unknown = _history(client, derivation_version_id="f" * 64)
    assert wrong_adapter.status_code == 404
    assert unknown.status_code == 404


def test_true_no_selection_is_still_503_with_an_undamaged_registration(
    tmp_path: Path, postgres_dsn: str
) -> None:
    """The guard must not turn a genuine missing selection into integrity failure."""

    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn, select=False)
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    assert response.status_code == 503
    assert response.json() == {"detail": NOT_SELECTED_SIGNAL}


def test_derive_registers_the_recipe_without_selecting_it(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn, select=False)
    with connect(postgres_dsn) as connection:
        registered = connection.execute(
            "SELECT count(*) FROM provider_recipes WHERE derivation_version_id = %s",
            (RANKED_KEYWORDS_RECIPE_ID,),
        ).fetchone()
        selected = connection.execute(
            "SELECT count(*) FROM provider_recipe_selections WHERE adapter_contract = %s",
            (RANKED_KEYWORDS_ADAPTER_CONTRACT,),
        ).fetchone()
    assert registered is not None and int(registered[0]) == 1
    assert selected is not None and int(selected[0]) == 0
    with _app(store, postgres_dsn) as client:
        assert _history(client).status_code == 503


def test_selection_isolation_between_adapters(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, RELATED_KEYWORDS_RECIPE)
        select_provider_recipe(
            connection, RELATED_KEYWORDS_ADAPTER_CONTRACT, RELATED_KEYWORDS_RECIPE_ID
        )
    assert _history(client).status_code == 200
    with connect(postgres_dsn) as connection:
        row = connection.execute(
            "SELECT derivation_version_id FROM provider_recipe_selections"
            " WHERE adapter_contract = %s",
            (RANKED_KEYWORDS_ADAPTER_CONTRACT,),
        ).fetchone()
    assert row is not None and str(row[0]) == RANKED_KEYWORDS_RECIPE_ID


# --------------------------------------------------------------------------------------
# Route and query contract
# --------------------------------------------------------------------------------------


def test_missing_requested_target_is_422(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    assert client.get(HISTORY).status_code == 422


def test_requested_keyword_is_not_the_ranked_subject(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    response = client.get(HISTORY + "?" + urlencode({"requested_keyword": TARGET}))
    assert response.status_code == 422


def test_empty_requested_target_is_422(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    assert _history(client, "").status_code == 422


@pytest.mark.parametrize(
    "subject",
    [
        "THECONSPIRATORY.COM",
        "www.theconspiratory.com",
        "https://theconspiratory.com",
        "theconspiratory.com/path",
        "a.b.c.d",
        "not a domain at all",
        "x" * 300,
    ],
)
def test_impossible_subjects_are_empty_history_not_422(
    ready: tuple[TestClient, EvidenceStore, str, str], subject: str
) -> None:
    """The acquisition-time target grammar is not a read-query validation rule."""

    client, _store, _attempt_id, _capture_id = ready
    response = _history(client, subject)
    assert response.status_code == 200, response.text
    _assert_envelope(
        response.json(), total_matching=0, returned_count=0, target=subject
    )


def test_unmeasured_subject_is_empty_history(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    response = _history(client, OTHER_TARGET)
    assert response.status_code == 200
    captures = _assert_envelope(
        response.json(), total_matching=0, returned_count=0, target=OTHER_TARGET
    )
    assert captures == []


@pytest.mark.parametrize("limit", [0, -1, 101, 1000])
def test_limit_outside_the_outer_bound_is_422(
    ready: tuple[TestClient, EvidenceStore, str, str], limit: int
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    assert _history(client, limit=limit).status_code == 422


def test_unknown_order_is_422(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    assert _history(client, order="sideways").status_code == 422


# --------------------------------------------------------------------------------------
# Outer Capture-history list
# --------------------------------------------------------------------------------------


def _prepare_two(
    tmp_path: Path, postgres_dsn: str
) -> tuple[EvidenceStore, tuple[str, str], tuple[str, str]]:
    store = create_store(tmp_path / "evidence-two")
    first = _commit(store, default_body(), "21" * 32, suffix="1")
    second = _commit(store, simple_body([item("gamma")]), "22" * 32, suffix="5")
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_ranked_keywords(store, connection)
        select_provider_recipe(
            connection, RANKED_KEYWORDS_ADAPTER_CONTRACT, RANKED_KEYWORDS_RECIPE_ID
        )
    return store, first, second


def test_two_captures_order_limit_and_has_more(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, first, second = _prepare_two(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        ascending = _history(client)
        assert ascending.status_code == 200, ascending.text
        captures = _assert_envelope(
            ascending.json(), total_matching=2, returned_count=2
        )
        assert [capture["capture_id"] for capture in captures] == [first[1], second[1]]

        descending = _history(client, order="desc")
        captures = _assert_envelope(
            descending.json(), total_matching=2, returned_count=2, order="desc"
        )
        assert [capture["capture_id"] for capture in captures] == [second[1], first[1]]

        limited = _history(client, limit=1)
        captures = _assert_envelope(
            limited.json(), total_matching=2, returned_count=1, limit=1
        )
        assert captures[0]["capture_id"] == first[1]
        assert limited.json()["has_more"] is True


def test_damage_outside_the_limit_still_fails_the_whole_read(
    tmp_path: Path, postgres_dsn: str
) -> None:
    """The excluded tail is verified before sorting, so its damage still fails the read."""

    store, _first, second = _prepare_two(tmp_path, postgres_dsn)
    _damage(
        postgres_dsn,
        "DELETE FROM observation_envelopes"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (RANKED_KEYWORDS_RECIPE_ID, second[1]),
    )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client, limit=1))


def test_outer_desc_never_reverses_inner_collections(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _first, _second = _prepare_two(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        ascending = _history(client).json()["captures"][0]
        descending = _history(client, order="desc").json()["captures"][-1]
    assert ascending == descending


# --------------------------------------------------------------------------------------
# Outcome and Evidence integrity
# --------------------------------------------------------------------------------------


def test_missing_outcome_behind_a_matching_context_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        "DELETE FROM outcomes WHERE derivation_version_id = %s AND capture_id = %s",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
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
        ("e" * 64, RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_second_capture_outcome_under_a_foreign_attempt_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    """`outcomes_identity` is unique per Attempt, so a duplicate Capture Outcome is legal SQL."""

    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        "INSERT INTO outcomes (attempt_id, capture_id, derivation_version_id,"
        " classification, observation_count) VALUES (%s, %s, %s, %s, %s)",
        ("e" * 64, capture_id, RANKED_KEYWORDS_RECIPE_ID, "observation_admitted", 0),
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
        "observation_admitted_empty",
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
        (classification, RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_wrong_observation_count_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        "UPDATE outcomes SET observation_count = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (SMALL_ENVELOPES + 1, RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_missing_capture_evidence_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, store, _attempt_id, capture_id = ready
    (store.capture_path(capture_id) / "capture.json").unlink()
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
        store, simple_body([item("delta")]), "33" * 32, target=OTHER_TARGET, suffix="2"
    )
    for table in ("outcomes", CONTEXT_TABLE):
        _damage(
            postgres_dsn,
            f"UPDATE {table} SET attempt_id = %s"
            " WHERE derivation_version_id = %s AND capture_id = %s",
            (foreign_attempt_id, RANKED_KEYWORDS_RECIPE_ID, capture_id),
        )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def _repoint(
    dsn: str,
    *,
    old_capture: str,
    new_capture: str,
    old_attempt: str,
    new_attempt: str,
) -> None:
    """Move every persisted Ranked row for one Capture onto foreign Evidence identities."""

    with connect(dsn) as connection:
        connection.execute("SET session_replication_role = replica")
        for table in ("outcomes", "observation_envelopes", *RANK05_TABLES):
            connection.execute(
                sql.SQL("UPDATE {} SET capture_id = %s WHERE capture_id = %s").format(
                    sql.Identifier(table)
                ),
                (new_capture, old_capture),
            )
        for table in ("outcomes", "observation_envelopes", CONTEXT_TABLE):
            connection.execute(
                sql.SQL("UPDATE {} SET attempt_id = %s WHERE attempt_id = %s").format(
                    sql.Identifier(table)
                ),
                (new_attempt, old_attempt),
            )


def test_foreign_adapter_evidence_behind_a_complete_row_set_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    """Every relational check passes; only the verified Evidence adapter refuses."""

    store, attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    foreign_params = closed_related_keywords_parameters(keyword="unrelated seed")
    foreign_attempt = related_keywords_http_attempt_document(
        parameters=foreign_params,
        attempt_nonce="55" * 32,
        authorized_at="2026-09-01T11:00:00.000000Z",
        observatory_version="rank06-test-v1",
    )
    foreign_attempt_id = store.commit_attempt(
        foreign_attempt,
        request_body=related_keywords_request_body_bytes(foreign_params),
    )
    foreign_body = b'{"foreign": true}'
    foreign_capture_id = store.commit_capture(
        related_keywords_http_capture_document(
            attempt=foreign_attempt,
            request_started_at="2026-09-01T11:00:01.100000Z",
            transport_ended_at="2026-09-01T11:00:01.400000Z",
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
            response_headers_at="2026-09-01T11:00:01.200000Z",
            response_body_ended_at="2026-09-01T11:00:01.300000Z",
        ),
        response_body=foreign_body,
    )
    _repoint(
        postgres_dsn,
        old_capture=capture_id,
        new_capture=foreign_capture_id,
        old_attempt=attempt_id,
        new_attempt=foreign_attempt_id,
    )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("request_location_code", 2841),
        ("request_language_code", "de"),
        ("request_limit", 50),
        ("request_offset", 100),
        ("request_ignore_synonyms", True),
        ("request_include_clickstream_data", True),
        ("request_load_rank_absolute", False),
        ("request_historical_serp_mode", "live"),
    ],
)
def test_request_context_disagreement_with_the_attempt_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    column: str,
    value: object,
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {CONTEXT_TABLE} SET {column} = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (value, RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("request_item_types", ["organic"]),
        (
            "request_item_types",
            ["paid", "organic", "featured_snippet", "local_pack", "ai_overview_reference"],
        ),
        ("request_order_by", ["ranked_serp_element.serp_item.rank_absolute,asc"]),
    ],
)
def test_request_context_array_disagreement_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    column: str,
    value: list[str],
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {CONTEXT_TABLE} SET {column} = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (value, RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_deleted_result_context_row_is_409_not_silent_shrinkage(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    """Nothing in PostgreSQL references the context row, so the reverse probe must catch it."""

    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"DELETE FROM {CONTEXT_TABLE}"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_deleted_context_of_one_of_two_captures_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _first, second = _prepare_two(tmp_path, postgres_dsn)
    _damage(
        postgres_dsn,
        f"DELETE FROM {CONTEXT_TABLE}"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (RANKED_KEYWORDS_RECIPE_ID, second[1]),
    )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))
        _assert_409(_history(client, limit=1))


# --------------------------------------------------------------------------------------
# Observation envelopes, semantic parents, and identity anchoring
# --------------------------------------------------------------------------------------


def _identity(kind: str, axes: Mapping[str, object]) -> str:
    return observation_identity(
        {
            "axes": dict(axes),
            "observation_kind": kind,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        RANKED_KEYWORDS_RECIPE,
    )


def _scalar(dsn: str, statement: str, params: Sequence[object] = ()) -> Any:
    with connect(dsn) as connection:
        row = connection.execute(statement, tuple(params)).fetchone()
    assert row is not None
    return row[0]


def _corpus_identity(dsn: str, capture_id: str, family: str, system: str) -> str:
    return str(
        _scalar(
            dsn,
            f"SELECT within_capture_identity FROM {CORPUS_METRICS_TABLE}"
            " WHERE derivation_version_id = %s AND capture_id = %s"
            " AND aggregate_family = %s AND rank_system = %s",
            (RANKED_KEYWORDS_RECIPE_ID, capture_id, family, system),
        )
    )


def _any_identity(dsn: str, table: str, capture_id: str) -> str:
    return str(
        _scalar(
            dsn,
            f"SELECT within_capture_identity FROM {table}"
            " WHERE derivation_version_id = %s AND capture_id = %s"
            " ORDER BY within_capture_identity LIMIT 1",
            (RANKED_KEYWORDS_RECIPE_ID, capture_id),
        )
    )


def test_missing_envelope_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    identity = _any_identity(postgres_dsn, MONTHLY_TABLE, capture_id)
    _damage(
        postgres_dsn,
        "DELETE FROM observation_envelopes WHERE derivation_version_id = %s"
        " AND capture_id = %s AND within_capture_identity = %s",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
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
            RANKED_KEYWORDS_RECIPE_ID,
            "dataforseo",
            RANKED_KEYWORDS_ADAPTER_CONTRACT,
            MONTHLY_KIND,
            "a" * 64,
        ),
    )
    _assert_409(_history(client))


def test_unknown_kind_envelope_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    identity = _any_identity(postgres_dsn, MONTHLY_TABLE, capture_id)
    _damage(
        postgres_dsn,
        "UPDATE observation_envelopes SET observation_kind = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        ("dataforseo.google.ranked_keywords.invented.v1", RANKED_KEYWORDS_RECIPE_ID,
         capture_id, identity),
    )
    _assert_409(_history(client))


def test_wrong_kind_envelope_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    identity = _any_identity(postgres_dsn, MONTHLY_TABLE, capture_id)
    _damage(
        postgres_dsn,
        "UPDATE observation_envelopes SET observation_kind = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        (CORPUS_METRICS_KIND, RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("attempt_id", "e" * 64),
        ("provider", "ahrefs"),
        ("adapter_contract", "some-other-adapter-v1"),
    ],
)
def test_foreign_provenance_envelope_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    column: str,
    value: str,
) -> None:
    """No foreign key constrains envelope attempt_id, provider, or adapter_contract."""

    client, _store, _attempt_id, capture_id = ready
    identity = _any_identity(postgres_dsn, CORPUS_METRICS_TABLE, capture_id)
    _damage(
        postgres_dsn,
        f"UPDATE observation_envelopes SET {column} = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        (value, RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    "table",
    [CORPUS_METRICS_TABLE, RANKED_RESULTS_TABLE, KEYWORD_DATA_TABLE, MONTHLY_TABLE],
)
def test_missing_semantic_parent_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str, table: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    identity = _any_identity(postgres_dsn, table, capture_id)
    _damage(
        postgres_dsn,
        f"DELETE FROM {table} WHERE derivation_version_id = %s"
        " AND capture_id = %s AND within_capture_identity = %s",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    ("table", "column", "value"),
    [
        (RANKED_RESULTS_TABLE, "keyword", "tampered"),
        (RANKED_RESULTS_TABLE, "serp_item_type", "paid"),
        (RANKED_RESULTS_TABLE, "rank_group", 99),
        (RANKED_RESULTS_TABLE, "rank_absolute", 99),
        (KEYWORD_DATA_TABLE, "keyword", "tampered"),
        (MONTHLY_TABLE, "keyword", "tampered"),
        (MONTHLY_TABLE, "year", 2020),
        (MONTHLY_TABLE, "month", 3),
        (CORPUS_METRICS_TABLE, "aggregate_family", "paid"),
    ],
)
def test_identity_axis_tamper_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    table: str,
    column: str,
    value: object,
) -> None:
    client, _store, _attempt_id, capture_id = ready
    identity = _any_identity(postgres_dsn, table, capture_id)
    _damage(
        postgres_dsn,
        f"UPDATE {table} SET {column} = %s WHERE derivation_version_id = %s"
        " AND capture_id = %s AND within_capture_identity = %s",
        (value, RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
    )
    _assert_409(_history(client))


def test_self_consistent_target_substitution_is_still_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    """Identity is recomputed from the verified Attempt target, never a row's own claim.

    Rewriting both the stored `requested_target` and the stored identity keeps the row
    internally consistent, so a reader that recomputed from the row's own axes would return
    a green. The Attempt is the only subject authority.
    """

    client, _store, _attempt_id, capture_id = ready
    fake = "substituted-target.com"
    keyword = str(
        _scalar(
            postgres_dsn,
            f"SELECT keyword FROM {KEYWORD_DATA_TABLE}"
            " WHERE derivation_version_id = %s AND capture_id = %s"
            " ORDER BY keyword LIMIT 1",
            (RANKED_KEYWORDS_RECIPE_ID, capture_id),
        )
    )
    old = _identity(KEYWORD_DATA_KIND, {"keyword": keyword, "requested_target": TARGET})
    new = _identity(KEYWORD_DATA_KIND, {"keyword": keyword, "requested_target": fake})
    assert old != new
    _damage(
        postgres_dsn,
        f"UPDATE {KEYWORD_DATA_TABLE} SET requested_target = %s,"
        " within_capture_identity = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        (fake, new, RANKED_KEYWORDS_RECIPE_ID, capture_id, old),
    )
    _damage(
        postgres_dsn,
        "UPDATE observation_envelopes SET within_capture_identity = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        (new, RANKED_KEYWORDS_RECIPE_ID, capture_id, old),
    )
    _assert_409(_history(client))


def test_self_consistent_corpus_target_substitution_is_still_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    fake = "substituted-target.com"
    old = _corpus_identity(postgres_dsn, capture_id, "organic", "rank_group")
    new = _identity(
        CORPUS_METRICS_KIND,
        {
            "aggregate_family": "organic",
            "rank_system": "rank_group",
            "requested_target": fake,
        },
    )
    _damage(
        postgres_dsn,
        f"UPDATE {CORPUS_METRICS_TABLE} SET requested_target = %s,"
        " within_capture_identity = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        (fake, new, RANKED_KEYWORDS_RECIPE_ID, capture_id, old),
    )
    _damage(
        postgres_dsn,
        "UPDATE observation_envelopes SET within_capture_identity = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        (new, RANKED_KEYWORDS_RECIPE_ID, capture_id, old),
    )
    _assert_409(_history(client))


# --------------------------------------------------------------------------------------
# Corpus cross-product and rank-system applicability
# --------------------------------------------------------------------------------------


def test_corpus_is_the_exact_ten_element_cross_product(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    facts = capture["corpus_metrics"]
    assert len(facts) == 10
    assert {
        (fact["aggregate_family"], fact["rank_system"]) for fact in facts
    } == CORPUS_COMBINATIONS


def test_missing_corpus_combination_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    """Everything else is left consistent, so only the cross-product check can fire."""

    client, _store, _attempt_id, capture_id = ready
    identity = _corpus_identity(postgres_dsn, capture_id, "local_pack", "rank_absolute")
    _damage(
        postgres_dsn,
        f"DELETE FROM {CORPUS_METRICS_TABLE} WHERE derivation_version_id = %s"
        " AND capture_id = %s AND within_capture_identity = %s",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
    )
    _damage(
        postgres_dsn,
        "DELETE FROM observation_envelopes WHERE derivation_version_id = %s"
        " AND capture_id = %s AND within_capture_identity = %s",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
    )
    _damage(
        postgres_dsn,
        "UPDATE outcomes SET observation_count = observation_count - 1"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_corpus_rank_system_tamper_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    """Relabelling rank_absolute as rank_group keeps every CHECK satisfied."""

    client, _store, _attempt_id, capture_id = ready
    identity = _corpus_identity(postgres_dsn, capture_id, "organic", "rank_absolute")
    _damage(
        postgres_dsn,
        f"UPDATE {CORPUS_METRICS_TABLE} SET rank_system = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        ("rank_group", RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
    )
    _assert_409(_history(client))


def _clone_semantic_row(
    dsn: str, table: str, capture_id: str, identity: str, new_identity: str
) -> None:
    """Copy one semantic parent row under a fabricated within-Capture identity."""

    with connect(dsn) as connection:
        connection.execute("SET session_replication_role = replica")
        columns = _table_columns(connection, table)
        selected = sql.SQL(", ").join(
            sql.SQL("%s")
            if column == "within_capture_identity"
            else sql.Identifier(column)
            for column in columns
        )
        connection.execute(
            sql.SQL("INSERT INTO {} ({}) SELECT {} FROM {}").format(
                sql.Identifier(table),
                sql.SQL(", ").join(sql.Identifier(column) for column in columns),
                selected,
                sql.Identifier(table),
            )
            + sql.SQL(
                " WHERE derivation_version_id = %s AND capture_id = %s"
                " AND within_capture_identity = %s"
            ),
            (new_identity, RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
        )


def test_extra_corpus_parent_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, attempt_id, capture_id = ready
    identity = _corpus_identity(postgres_dsn, capture_id, "paid", "rank_group")
    _clone_semantic_row(
        postgres_dsn, CORPUS_METRICS_TABLE, capture_id, identity, "b" * 64
    )
    _damage(
        postgres_dsn,
        "INSERT INTO observation_envelopes (capture_id, attempt_id,"
        " derivation_version_id, provider, adapter_contract, observation_kind,"
        " within_capture_identity) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (
            capture_id,
            attempt_id,
            RANKED_KEYWORDS_RECIPE_ID,
            "dataforseo",
            RANKED_KEYWORDS_ADAPTER_CONTRACT,
            CORPUS_METRICS_KIND,
            "b" * 64,
        ),
    )
    _damage(
        postgres_dsn,
        "UPDATE outcomes SET observation_count = observation_count + 1"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    ("column", "state"),
    [
        ("count", "json_null"),
        ("count", "absent"),
        ("count", "inapplicable"),
        ("etv", "inapplicable"),
        ("etv", "not_requested"),
        ("estimated_paid_traffic_cost", "inapplicable"),
        ("estimated_paid_traffic_cost", "not_requested"),
    ],
)
def test_rank_group_state_outside_its_recipe_domain_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    column: str,
    state: str,
) -> None:
    """The schema CHECK constrains only the rank-absolute direction of applicability."""

    client, _store, _attempt_id, capture_id = ready
    identity = _corpus_identity(postgres_dsn, capture_id, "organic", "rank_group")
    _damage(
        postgres_dsn,
        f"UPDATE {CORPUS_METRICS_TABLE} SET {column} = NULL, {column}_state = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        (state, RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
    )
    _assert_409(_history(client))


def test_rank_absolute_applicability_is_refused_by_postgresql(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    """`rank05_corpus_absolute_locus` already blocks the rank-absolute direction."""

    _client, _store, _attempt_id, capture_id = ready
    identity = _corpus_identity(postgres_dsn, capture_id, "organic", "rank_absolute")
    with pytest.raises(Exception, match="rank05_corpus_absolute_locus"):
        _damage(
            postgres_dsn,
            f"UPDATE {CORPUS_METRICS_TABLE} SET count = 5, count_state = 'stated'"
            " WHERE derivation_version_id = %s AND capture_id = %s"
            " AND within_capture_identity = %s",
            (RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
        )


def test_rank_systems_stay_independent_answers(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    by_key = {
        (fact["aggregate_family"], fact["rank_system"]): fact
        for fact in capture["corpus_metrics"]
    }
    group = by_key[("organic", "rank_group")]
    absolute = by_key[("organic", "rank_absolute")]
    assert group["count"]["state"] == "stated"
    assert absolute["count"] == {"state": "inapplicable", "value": None}
    assert absolute["etv"] == {"state": "inapplicable", "value": None}
    assert absolute["estimated_paid_traffic_cost"] == {
        "state": "inapplicable",
        "value": None,
    }
    # Ten aggregate facts and three returned rows are unrelated answers.
    assert capture["result_context"]["items_count"] == SMALL_ITEMS
    assert capture["result_context"]["total_count"] == GOLDEN_TOTAL_COUNT


# --------------------------------------------------------------------------------------
# Ranked-local keyword children
# --------------------------------------------------------------------------------------


def _keyword_identity(dsn: str, capture_id: str, keyword: str) -> str:
    return str(
        _scalar(
            dsn,
            f"SELECT within_capture_identity FROM {KEYWORD_DATA_TABLE}"
            " WHERE derivation_version_id = %s AND capture_id = %s AND keyword = %s",
            (RANKED_KEYWORDS_RECIPE_ID, capture_id, keyword),
        )
    )


@pytest.mark.parametrize(
    "table",
    [
        KEYWORD_INFO_TABLE,
        PROPERTIES_TABLE,
        BACKLINKS_TABLE,
        INTENT_TABLE,
        KEYWORD_SERP_TABLE,
    ],
)
def test_missing_child_row_for_a_stated_state_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str, table: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    identity = _keyword_identity(postgres_dsn, capture_id, "alpha")
    _damage(
        postgres_dsn,
        f"DELETE FROM {table} WHERE derivation_version_id = %s"
        " AND capture_id = %s AND within_capture_identity = %s",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    "table",
    [PROPERTIES_TABLE, BACKLINKS_TABLE, INTENT_TABLE, KEYWORD_SERP_TABLE],
)
def test_unexpected_child_row_for_a_non_stated_state_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str, table: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    alpha = _keyword_identity(postgres_dsn, capture_id, "alpha")
    beta = _keyword_identity(postgres_dsn, capture_id, "beta")
    _clone_semantic_row(postgres_dsn, table, capture_id, alpha, beta)
    _assert_409(_history(client))


@pytest.mark.parametrize(
    ("column", "state"),
    [
        ("keyword_info_state", "json_null"),
        ("keyword_properties_state", "stated"),
        ("avg_backlinks_state", "stated"),
        ("search_intent_state", "stated"),
        ("keyword_serp_info_state", "stated"),
    ],
)
def test_enclosing_state_disagreement_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    column: str,
    state: str,
) -> None:
    client, _store, _attempt_id, capture_id = ready
    identity = _keyword_identity(postgres_dsn, capture_id, "beta")
    _damage(
        postgres_dsn,
        f"UPDATE {KEYWORD_DATA_TABLE} SET {column} = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        (state, RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
    )
    _assert_409(_history(client))


# --------------------------------------------------------------------------------------
# Returned-item occurrence bridge
# --------------------------------------------------------------------------------------


def test_item_occurrences_carry_provider_order_and_both_parents(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    occurrences = capture["item_occurrences"]
    assert [entry["item_index"] for entry in occurrences] == [0, 1, 2]
    placements = {
        fact["within_capture_identity"]: fact for fact in capture["ranked_results"]
    }
    keywords = {
        fact["within_capture_identity"]: fact for fact in capture["keyword_data"]
    }
    for entry in occurrences:
        assert entry["item_se_type"] == "google"
        assert entry["ranked_result_kind"] == RANKED_RESULT_KIND
        assert entry["keyword_data_kind"] == KEYWORD_DATA_KIND
        placement = placements[entry["ranked_result_identity"]]
        keyword_fact = keywords[entry["keyword_data_identity"]]
        assert placement["keyword"] == keyword_fact["keyword"]
    # The duplicate returned keyword collapses to one keyword-data fact with two placements.
    assert sorted(
        entry["keyword_data_identity"] for entry in occurrences
    ) == sorted(
        [keywords[_by_keyword(capture["keyword_data"], "alpha")[0][
            "within_capture_identity"
        ]]["within_capture_identity"]] * 2
        + [
            _by_keyword(capture["keyword_data"], "beta")[0][
                "within_capture_identity"
            ]
        ]
    )


def _by_keyword(
    facts: Sequence[Mapping[str, Any]], keyword: str
) -> list[dict[str, Any]]:
    return [dict(fact) for fact in facts if fact["keyword"] == keyword]


def test_missing_item_occurrence_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"DELETE FROM {ITEM_OCCURRENCES_TABLE} WHERE derivation_version_id = %s"
        " AND capture_id = %s AND item_index = %s",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id, 1),
    )
    _assert_409(_history(client))


def test_extra_item_occurrence_disagrees_with_items_count(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"INSERT INTO {ITEM_OCCURRENCES_TABLE} (capture_id, derivation_version_id,"
        " item_index, ranked_result_identity, ranked_result_kind,"
        " keyword_data_identity, keyword_data_kind, item_se_type)"
        f" SELECT capture_id, derivation_version_id, 3, ranked_result_identity,"
        " ranked_result_kind, keyword_data_identity, keyword_data_kind, item_se_type"
        f" FROM {ITEM_OCCURRENCES_TABLE} WHERE derivation_version_id = %s"
        " AND capture_id = %s AND item_index = 0",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_non_dense_item_indexes_are_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {ITEM_OCCURRENCES_TABLE} SET item_index = 9"
        " WHERE derivation_version_id = %s AND capture_id = %s AND item_index = 2",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_items_count_disagreement_with_occurrences_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {CONTEXT_TABLE} SET items_count = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (2, RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_item_occurrence_pointing_at_the_wrong_placement_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    target_identity = str(
        _scalar(
            postgres_dsn,
            f"SELECT ranked_result_identity FROM {ITEM_OCCURRENCES_TABLE}"
            " WHERE derivation_version_id = %s AND capture_id = %s AND item_index = 0",
            (RANKED_KEYWORDS_RECIPE_ID, capture_id),
        )
    )
    _damage(
        postgres_dsn,
        f"UPDATE {ITEM_OCCURRENCES_TABLE} SET ranked_result_identity = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s AND item_index = 1",
        (target_identity, RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_item_occurrence_linking_parents_with_different_keywords_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    """Both parents keep an occurrence, so only the keyword-agreement check can fire."""

    client, _store, _attempt_id, capture_id = ready
    beta = _keyword_identity(postgres_dsn, capture_id, "beta")
    _damage(
        postgres_dsn,
        f"UPDATE {ITEM_OCCURRENCES_TABLE} SET keyword_data_identity = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s AND item_index = 2",
        (beta, RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_item_se_type_outside_the_closed_vocabulary_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    """The persisted column has no SQL enum CHECK."""

    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {ITEM_OCCURRENCES_TABLE} SET item_se_type = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s AND item_index = 0",
        ("bing", RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    ("table", "column"),
    [
        (RANKED_RESULTS_TABLE, "ranked_element_se_type"),
        (RANKED_RESULTS_TABLE, "serp_item_se_type"),
        (KEYWORD_DATA_TABLE, "se_type"),
        (KEYWORD_INFO_TABLE, "se_type"),
        (PROPERTIES_TABLE, "se_type"),
        (BACKLINKS_TABLE, "se_type"),
        (INTENT_TABLE, "se_type"),
        (KEYWORD_SERP_TABLE, "se_type"),
        (CONTEXT_TABLE, "result_se_type"),
    ],
)
def test_stated_se_type_outside_the_closed_vocabulary_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    table: str,
    column: str,
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {table} SET {column} = %s WHERE derivation_version_id = %s"
        f" AND capture_id = %s AND {column} IS NOT NULL",
        ("bing", RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


# --------------------------------------------------------------------------------------
# Monthly Data Period binding
# --------------------------------------------------------------------------------------


def test_monthly_facts_keep_every_duplicate_occurrence(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    assert len(capture["monthly_search_volume"]) == 1
    fact = capture["monthly_search_volume"][0]
    assert fact["keyword"] == "alpha"
    assert fact["data_period"] == {"year": 2026, "month": 7}
    assert fact["search_volume"] == 90
    assert [entry["item_index"] for entry in fact["occurrences"]] == [0, 2]


def test_stated_empty_monthly_searches_yields_no_monthly_fact(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    """A stated provider `monthly_searches: []` is valid Recipe v1 testimony."""

    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    beta = _by_keyword(capture["keyword_data"], "beta")[0]
    assert beta["keyword_info"]["state"] == "stated"
    assert beta["keyword_info"]["value"]["monthly_searches_state"] == "stated"
    assert not _by_keyword(capture["monthly_search_volume"], "beta")


def test_missing_monthly_occurrence_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"DELETE FROM {MONTHLY_OCCURRENCES_TABLE}"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_monthly_occurrence_without_a_returned_item_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {MONTHLY_OCCURRENCES_TABLE} SET item_index = 9"
        " WHERE derivation_version_id = %s AND capture_id = %s AND item_index = 0",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_monthly_occurrence_must_cite_its_own_returned_keyword(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {MONTHLY_OCCURRENCES_TABLE} SET item_index = 1"
        " WHERE derivation_version_id = %s AND capture_id = %s AND item_index = 0",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


def test_orphan_monthly_occurrence_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"INSERT INTO {MONTHLY_OCCURRENCES_TABLE} (capture_id, derivation_version_id,"
        " within_capture_identity, observation_kind, item_index)"
        " VALUES (%s, %s, %s, %s, %s)",
        (capture_id, RANKED_KEYWORDS_RECIPE_ID, "c" * 64, MONTHLY_KIND, 0),
    )
    _assert_409(_history(client))


def test_monthly_fact_without_a_matching_keyword_data_parent_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    identity = _identity(
        MONTHLY_KIND,
        {"keyword": "ghost", "month": 7, "requested_target": TARGET, "year": 2026},
    )
    old = _any_identity(postgres_dsn, MONTHLY_TABLE, capture_id)
    _damage(
        postgres_dsn,
        f"UPDATE {MONTHLY_TABLE} SET keyword = %s, within_capture_identity = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        ("ghost", identity, RANKED_KEYWORDS_RECIPE_ID, capture_id, old),
    )
    _damage(
        postgres_dsn,
        "UPDATE observation_envelopes SET within_capture_identity = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        (identity, RANKED_KEYWORDS_RECIPE_ID, capture_id, old),
    )
    _damage(
        postgres_dsn,
        f"UPDATE {MONTHLY_OCCURRENCES_TABLE} SET within_capture_identity = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        (identity, RANKED_KEYWORDS_RECIPE_ID, capture_id, old),
    )
    _assert_409(_history(client))


def test_monthly_fact_under_a_non_stated_monthly_searches_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    identity = _keyword_identity(postgres_dsn, capture_id, "alpha")
    _damage(
        postgres_dsn,
        f"UPDATE {KEYWORD_INFO_TABLE} SET monthly_searches_state = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        ("json_null", RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
    )
    _assert_409(_history(client))


def test_monthly_fact_under_a_non_stated_keyword_info_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    identity = _keyword_identity(postgres_dsn, capture_id, "alpha")
    _damage(
        postgres_dsn,
        f"DELETE FROM {KEYWORD_INFO_TABLE} WHERE derivation_version_id = %s"
        " AND capture_id = %s AND within_capture_identity = %s",
        (RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
    )
    _damage(
        postgres_dsn,
        f"UPDATE {KEYWORD_DATA_TABLE} SET keyword_info_state = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        ("json_null", RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
    )
    _assert_409(_history(client))


# --------------------------------------------------------------------------------------
# Applicable Recipe-v1 field-state domains
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("table", "column", "state", "clear_value"),
    [
        (RANKED_RESULTS_TABLE, "title", "not_requested", True),
        (RANKED_RESULTS_TABLE, "title", "inapplicable", True),
        (RANKED_RESULTS_TABLE, "domain", "not_requested", True),
        (RANKED_RESULTS_TABLE, "ranked_element_check_url", "inapplicable", True),
        (KEYWORD_INFO_TABLE, "cpc", "not_requested", True),
        (BACKLINKS_TABLE, "backlinks", "inapplicable", True),
        (CONTEXT_TABLE, "result_language_code", "not_requested", True),
    ],
)
def test_optional_field_state_outside_its_domain_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    table: str,
    column: str,
    state: str,
    clear_value: bool,
) -> None:
    client, _store, _attempt_id, capture_id = ready
    assert clear_value
    _damage(
        postgres_dsn,
        f"UPDATE {table} SET {column} = NULL, {column}_state = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (state, RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    ("table", "column", "state"),
    [
        (RANKED_RESULTS_TABLE, "breadcrumb_state", "not_requested"),
        (RANKED_RESULTS_TABLE, "pre_snippet_state", "inapplicable"),
        (RANKED_RESULTS_TABLE, "highlighted_state", "not_requested"),
        (RANKED_RESULTS_TABLE, "about_this_result_state", "stated"),
        (RANKED_RESULTS_TABLE, "backlinks_info_state", "not_requested"),
        (RANKED_RESULTS_TABLE, "extended_snippet_state", "stated"),
        (RANKED_RESULTS_TABLE, "links_state", "inapplicable"),
        (RANKED_RESULTS_TABLE, "rating_state", "stated"),
        (RANKED_RESULTS_TABLE, "clickstream_etv_state", "absent"),
        (RANKED_RESULTS_TABLE, "clickstream_etv_state", "json_null"),
        (KEYWORD_DATA_TABLE, "bing_normalized_state", "stated"),
        (KEYWORD_DATA_TABLE, "bing_normalized_state", "not_requested"),
        (KEYWORD_DATA_TABLE, "clickstream_normalized_state", "absent"),
        (KEYWORD_DATA_TABLE, "clickstream_keyword_info_state", "json_null"),
        (CORPUS_METRICS_TABLE, "clickstream_etv_state", "absent"),
        (CORPUS_METRICS_TABLE, "clickstream_gender_distribution_state", "json_null"),
        (CORPUS_METRICS_TABLE, "clickstream_age_distribution_state", "stated"),
        (KEYWORD_INFO_TABLE, "monthly_searches_state", "not_requested"),
    ],
)
def test_state_only_column_outside_its_domain_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    table: str,
    column: str,
    state: str,
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {table} SET {column} = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        (state, RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    ("keyword", "column", "state"),
    [
        # alpha states rank_changes and rank_info, so members must not be inapplicable.
        ("alpha", "rank_changes_is_new", "inapplicable"),
        ("alpha", "rank_changes_previous_rank_absolute", "inapplicable"),
        ("alpha", "rank_info_page_rank", "inapplicable"),
        # beta leaves both objects unstated, so members must stay inapplicable.
        ("beta", "rank_changes_is_up", "absent"),
        ("beta", "rank_changes_is_down", "json_null"),
        ("beta", "rank_info_main_domain_rank", "absent"),
    ],
)
def test_inline_member_state_coupling_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    keyword: str,
    column: str,
    state: str,
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {RANKED_RESULTS_TABLE} SET {column} = NULL, {column}_state = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s AND keyword = %s",
        (state, RANKED_KEYWORDS_RECIPE_ID, capture_id, keyword),
    )
    _assert_409(_history(client))


@pytest.mark.parametrize(
    ("keyword", "column", "state"),
    [
        ("alpha", "trend_monthly", "inapplicable"),
        ("beta", "trend_quarterly", "absent"),
        ("beta", "trend_yearly", "json_null"),
    ],
)
def test_search_volume_trend_member_coupling_is_409(
    ready: tuple[TestClient, EvidenceStore, str, str],
    postgres_dsn: str,
    keyword: str,
    column: str,
    state: str,
) -> None:
    client, _store, _attempt_id, capture_id = ready
    identity = _keyword_identity(postgres_dsn, capture_id, keyword)
    _damage(
        postgres_dsn,
        f"UPDATE {KEYWORD_INFO_TABLE} SET {column} = NULL, {column}_state = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s"
        " AND within_capture_identity = %s",
        (state, RANKED_KEYWORDS_RECIPE_ID, capture_id, identity),
    )
    _assert_409(_history(client))


def test_unstated_inline_objects_expose_inapplicable_members(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    beta = _by_keyword(capture["ranked_results"], "beta")[0]
    assert beta["serp_item"]["rank_changes"]["state"] == "json_null"
    for member in ("is_new", "is_up", "is_down", "previous_rank_absolute"):
        assert beta["serp_item"]["rank_changes"][member] == {
            "state": "inapplicable",
            "value": None,
        }
    assert beta["serp_item"]["rank_info"]["state"] == "absent"
    for member in ("page_rank", "main_domain_rank"):
        assert beta["serp_item"]["rank_info"][member] == {
            "state": "inapplicable",
            "value": None,
        }
    beta_keyword = _by_keyword(capture["keyword_data"], "beta")[0]
    trend = beta_keyword["keyword_info"]["value"]["search_volume_trend"]
    assert trend["state"] == "json_null"
    for member in ("monthly", "quarterly", "yearly"):
        assert trend[member] == {"state": "inapplicable", "value": None}


def test_prose_states_survive_without_their_values(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    """[CHAZ] Product Option 1: state is served, the provider text stays Evidence-only."""

    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    alpha = _by_keyword(capture["ranked_results"], "alpha")[0]
    beta = _by_keyword(capture["ranked_results"], "beta")[0]
    assert alpha["serp_item"]["breadcrumb_state"] == "stated"
    assert alpha["serp_item"]["pre_snippet_state"] == "stated"
    assert alpha["serp_item"]["highlighted_state"] == "stated"
    assert beta["serp_item"]["breadcrumb_state"] == "json_null"
    assert beta["serp_item"]["pre_snippet_state"] == "absent"
    assert beta["serp_item"]["highlighted_state"] == "absent"
    serialized = json.dumps(capture)
    assert "https://theconspiratory.com > a" not in serialized
    assert "Aug 1, 2026" not in serialized


def test_unsupported_children_expose_state_only(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    alpha = _by_keyword(_one_capture(client)["ranked_results"], "alpha")[0]
    for column in (
        "about_this_result_state",
        "backlinks_info_state",
        "extended_snippet_state",
        "links_state",
        "rating_state",
    ):
        assert alpha["serp_item"][column] == "json_null"


def test_clickstream_loci_are_request_disabled_everywhere(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    assert capture["request"]["include_clickstream_data"] is False
    for fact in capture["corpus_metrics"]:
        assert fact["clickstream_etv_state"] == "not_requested"
        assert fact["clickstream_gender_distribution_state"] == "not_requested"
        assert fact["clickstream_age_distribution_state"] == "not_requested"
    for placement in capture["ranked_results"]:
        assert placement["serp_item"]["clickstream_etv_state"] == "not_requested"
    for keyword_fact in capture["keyword_data"]:
        assert keyword_fact["clickstream_normalized_state"] == "not_requested"
        assert keyword_fact["clickstream_keyword_info_state"] == "not_requested"
        assert keyword_fact["bing_normalized_state"] in {"absent", "json_null"}


# --------------------------------------------------------------------------------------
# Deterministic presentation and preserved provider testimony
# --------------------------------------------------------------------------------------


def test_ranked_result_presentation_is_keyword_first_not_provider_order(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    presented = [
        (fact["keyword"], fact["rank_group"]) for fact in capture["ranked_results"]
    ]
    assert presented == [("alpha", 1), ("alpha", 3), ("beta", 2)]
    provider_order = sorted(presented, key=lambda entry: entry[1])
    assert provider_order == [("alpha", 1), ("beta", 2), ("alpha", 3)]
    assert presented != provider_order
    assert capture["request"]["order_by"] == [
        "ranked_serp_element.serp_item.rank_group,asc"
    ]


def test_corpus_presentation_follows_the_accepted_family_and_system_order(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    assert [
        (fact["aggregate_family"], fact["rank_system"])
        for fact in capture["corpus_metrics"]
    ] == [(family, system) for family in AGGREGATE_FAMILIES for system in RANK_SYSTEMS]


def test_decimal_values_never_round_trip_through_binary_float(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    alpha = _by_keyword(capture["ranked_results"], "alpha")[0]
    assert alpha["serp_item"]["etv"] == {"state": "stated", "value": "1.5"}
    assert alpha["serp_item"]["estimated_paid_traffic_cost"] == {
        "state": "stated",
        "value": "2.5",
    }
    keyword_fact = _by_keyword(capture["keyword_data"], "alpha")[0]
    backlinks_value = keyword_fact["avg_backlinks"]["value"]
    assert backlinks_value["backlinks"] == {"state": "stated", "value": "1234.5678"}
    assert backlinks_value["referring_main_domains"] == {
        "state": "stated",
        "value": "80.0625",
    }
    assert keyword_fact["keyword_info"]["value"]["competition"] == {
        "state": "stated",
        "value": "0.25",
    }


def test_ordered_duplicate_arrays_survive(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    alpha_placement = _by_keyword(capture["ranked_results"], "alpha")[0]
    assert alpha_placement["ranked_element"]["serp_item_types"] == {
        "state": "stated",
        "value": ["organic", "organic", "ai_overview"],
    }
    alpha_keyword = _by_keyword(capture["keyword_data"], "alpha")[0]
    assert alpha_keyword["keyword_info"]["value"]["categories"] == {
        "state": "stated",
        "value": [10013, 10013, 10106],
    }
    assert alpha_keyword["search_intent"]["value"]["foreign_intent"] == {
        "state": "stated",
        "value": ["commercial", "commercial"],
    }
    assert capture["request"]["item_types"] == list(AGGREGATE_FAMILIES)


def test_source_local_clocks_stay_independent(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    placement = _by_keyword(capture["ranked_results"], "alpha")[0]
    keyword_fact = _by_keyword(capture["keyword_data"], "alpha")[0]
    element = placement["ranked_element"]
    serp = keyword_fact["keyword_serp_info"]["value"]
    assert element["last_updated_time"] == {"state": "stated", "value": CLOCK}
    assert element["previous_updated_time"] == {
        "state": "stated",
        "value": PREVIOUS_CLOCK,
    }
    assert serp["keyword_serp_last_updated_time"] == {
        "state": "stated",
        "value": KEYWORD_SERP_CLOCK,
    }
    assert serp["keyword_serp_previous_updated_time"] == {
        "state": "stated",
        "value": YEAR_ONE_CLOCK,
    }
    # Four independent enrichment clocks; disagreement is testimony, not reconciliation.
    assert keyword_fact["keyword_info"]["value"]["keyword_info_last_updated_time"] == {
        "state": "stated",
        "value": CLOCK,
    }
    assert keyword_fact["avg_backlinks"]["value"]["avg_backlinks_last_updated_time"] == {
        "state": "stated",
        "value": PREVIOUS_CLOCK,
    }
    assert keyword_fact["search_intent"]["value"]["search_intent_last_updated_time"] == {
        "state": "stated",
        "value": YEAR_ONE_CLOCK,
    }
    assert element["last_updated_time"]["value"] != (
        serp["keyword_serp_last_updated_time"]["value"]
    )
    assert "last_updated" not in json.dumps(sorted(capture))
    assert "provider_update_time" not in json.dumps(capture)


def test_current_search_volume_is_not_the_newest_monthly_point(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    capture = _one_capture(client)
    alpha = _by_keyword(capture["keyword_data"], "alpha")[0]
    current = alpha["keyword_info"]["value"]["search_volume"]
    newest = capture["monthly_search_volume"][0]
    assert current == {"state": "stated", "value": 100}
    assert newest["search_volume"] == 90
    assert current["value"] != newest["search_volume"]


def test_url_is_content_not_identity(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    """Exact URL is placement content, so rewriting it changes no identity and still reads.

    Same-identity URL contradiction is a RANK-05 derive-time whole-unit rejection, and
    comparing URLs across Captures is downstream analysis. Neither is a read-time check.
    """

    client, _store, _attempt_id, capture_id = ready
    before = _one_capture(client)
    _damage(
        postgres_dsn,
        f"UPDATE {RANKED_RESULTS_TABLE} SET url = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s AND rank_group = 1",
        ("https://theconspiratory.com/rewritten", RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    after = _one_capture(client)
    changed = _by_keyword(after["ranked_results"], "alpha")[0]
    assert changed["serp_item"]["url"] == "https://theconspiratory.com/rewritten"
    assert changed["within_capture_identity"] == (
        _by_keyword(before["ranked_results"], "alpha")[0]["within_capture_identity"]
    )


def test_result_echo_disagreement_stays_visible_testimony(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, _store, _attempt_id, capture_id = ready
    _damage(
        postgres_dsn,
        f"UPDATE {CONTEXT_TABLE} SET result_target = %s, result_location_code = %s"
        " WHERE derivation_version_id = %s AND capture_id = %s",
        ("echoed-other.com", 9999, RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    capture = _one_capture(client)
    assert capture["result_context"]["target"] == {
        "state": "stated",
        "value": "echoed-other.com",
    }
    assert capture["result_context"]["location_code"] == {
        "state": "stated",
        "value": 9999,
    }
    assert capture["request"]["target"] == TARGET
    assert capture["request"]["location_code"] == 2840


def test_result_context_states_no_completeness_claim(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    context = _one_capture(client)["result_context"]
    assert set(context) == RESULT_CONTEXT_KEYS
    for forbidden in (
        "complete",
        "truncated",
        "first_page",
        "coverage_percent",
        "corpus_exhausted",
        "has_more",
    ):
        assert forbidden not in context


# --------------------------------------------------------------------------------------
# Zero-item admitted success
# --------------------------------------------------------------------------------------


def test_zero_item_success_is_admitted_with_ten_corpus_facts(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare(
        tmp_path,
        postgres_dsn,
        body=simple_body([], total_count=0),
        nonce="77" * 32,
    )
    with _app(store, postgres_dsn) as client:
        capture = _one_capture(client)
    assert capture["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": 10,
    }
    assert len(capture["corpus_metrics"]) == 10
    assert capture["ranked_results"] == []
    assert capture["keyword_data"] == []
    assert capture["monthly_search_volume"] == []
    assert capture["item_occurrences"] == []
    assert capture["result_context"]["items_count"] == 0
    assert capture["result_context"]["total_count"] == 0


def test_zero_item_success_is_not_empty_outer_history(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare(
        tmp_path,
        postgres_dsn,
        body=simple_body([], total_count=0),
        nonce="78" * 32,
    )
    with _app(store, postgres_dsn) as client:
        measured = _history(client).json()
        unmeasured = _history(client, OTHER_TARGET).json()
    assert measured["total_matching"] == 1
    assert unmeasured["total_matching"] == 0
    assert measured["captures"][0]["capture_outcome"]["classification"] == (
        "observation_admitted"
    )


# --------------------------------------------------------------------------------------
# Provider Attempt audit routing
# --------------------------------------------------------------------------------------


def _attempt_resource(client: TestClient, attempt_id: str, **query: object) -> Any:
    path = f"/v1/attempts/{attempt_id}"
    if query:
        path += "?" + urlencode(query)
    return client.get(path)


def test_ranked_attempt_routes_to_the_provider_attempt_reader(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, attempt_id, capture_id = ready
    response = _attempt_resource(client, attempt_id)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["attempt_id"] == attempt_id
    assert body["provider"] == "dataforseo"
    assert body["adapter_contract"] == RANKED_KEYWORDS_ADAPTER_CONTRACT
    assert body["derivation_version_id"] == RANKED_KEYWORDS_RECIPE_ID
    assert body["recipe_resolution"] == "selected"
    assert body["attempt_outcome"]["classification"] == "authorized_unresolved"
    assert body["capture_outcome"]["capture_id"] == capture_id
    assert body["capture_outcome"]["classification"] == "observation_admitted"


def test_ranked_attempt_audit_without_a_selection_is_503(
    tmp_path: Path, postgres_dsn: str
) -> None:
    """Observable RANK-06 routing change: the fixture fall-through no longer applies."""

    store, attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn, select=False)
    with _app(store, postgres_dsn) as client:
        response = _attempt_resource(client, attempt_id)
    assert response.status_code == 503
    assert response.json() == {"detail": NOT_SELECTED_SIGNAL}


def test_ranked_attempt_audit_honours_an_explicit_pin(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn, select=False)
    with _app(store, postgres_dsn) as client:
        response = _attempt_resource(
            client, attempt_id, derivation_version_id=RANKED_KEYWORDS_RECIPE_ID
        )
    assert response.status_code == 200, response.text
    assert response.json()["recipe_resolution"] == "pinned"


def test_unknown_attempt_identity_is_404(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    assert _attempt_resource(client, "d" * 64).status_code == 404


def test_unrelated_ranked_attempt_never_supplies_another_captures_provenance(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence-isolation")
    _first_attempt, first_capture = _commit(store, default_body(), "88" * 32, suffix="1")
    second_attempt, _second_capture = _commit(
        store,
        simple_body([item("gamma")], target=OTHER_TARGET),
        "89" * 32,
        target=OTHER_TARGET,
        suffix="2",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_ranked_keywords(store, connection)
        select_provider_recipe(
            connection, RANKED_KEYWORDS_ADAPTER_CONTRACT, RANKED_KEYWORDS_RECIPE_ID
        )
    with _app(store, postgres_dsn) as client:
        first = _one_capture(client)
        other = _one_capture(client, OTHER_TARGET)
    assert first["capture_id"] == first_capture
    assert first["request"]["target"] == TARGET
    assert other["attempt_id"] == second_attempt
    assert other["request"]["target"] == OTHER_TARGET
    assert first["attempt_id"] != other["attempt_id"]


# --------------------------------------------------------------------------------------
# Read-only boundary and rebuild equivalence
# --------------------------------------------------------------------------------------


def _snapshot(dsn: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    with connect(dsn) as connection:
        for table in READONLY_TABLES:
            row = connection.execute(
                sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table))
            ).fetchone()
            assert row is not None
            counts[table] = int(row[0])
    return counts


def test_reads_preserve_postgresql_and_evidence(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    client, store, _attempt_id, _capture_id = ready
    before = _snapshot(postgres_dsn)
    before_attempts = set(store.list_committed_ids("attempts"))
    before_captures = set(store.list_committed_ids("captures"))
    for _ in range(3):
        assert _history(client).status_code == 200
        assert _history(client, OTHER_TARGET).status_code == 200
        assert _history(client, order="desc", limit=1).status_code == 200
    assert _snapshot(postgres_dsn) == before
    assert set(store.list_committed_ids("attempts")) == before_attempts
    assert set(store.list_committed_ids("captures")) == before_captures


def test_two_independently_derived_databases_return_equal_history(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence-rebuild")
    _commit(store, default_body(), "99" * 32)
    payloads: list[Any] = []
    for dsn in (postgres_dsn, postgres_second_dsn):
        apply_migrations(dsn)
        with connect(dsn) as connection:
            derive_google_ranked_keywords(store, connection)
            select_provider_recipe(
                connection, RANKED_KEYWORDS_ADAPTER_CONTRACT, RANKED_KEYWORDS_RECIPE_ID
            )
        with _app(store, dsn) as client:
            response = _history(client)
            assert response.status_code == 200, response.text
            payloads.append(response.json())
    assert payloads[0] == payloads[1]


# --------------------------------------------------------------------------------------
# Column completeness
# --------------------------------------------------------------------------------------


def test_reader_projects_every_persisted_rank05_column(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    """No persisted RANK-05 content column may be silently dropped from the projection."""

    expected = {
        CORPUS_METRICS_TABLE: CORPUS_METRICS_COLUMNS,
        RANKED_RESULTS_TABLE: RANKED_RESULT_COLUMNS,
        KEYWORD_DATA_TABLE: KEYWORD_DATA_COLUMNS,
        KEYWORD_INFO_TABLE: KEYWORD_INFO_COLUMNS,
        PROPERTIES_TABLE: PROPERTIES_COLUMNS,
        BACKLINKS_TABLE: BACKLINKS_COLUMNS,
        INTENT_TABLE: INTENT_COLUMNS,
        KEYWORD_SERP_TABLE: KEYWORD_SERP_COLUMNS,
        MONTHLY_TABLE: MONTHLY_COLUMNS,
        MONTHLY_OCCURRENCES_TABLE: MONTHLY_OCCURRENCE_COLUMNS,
        ITEM_OCCURRENCES_TABLE: ITEM_OCCURRENCE_COLUMNS,
    }
    assert len(expected) + 1 == len(RANK05_TABLES)
    with connect(postgres_dsn) as connection:
        for table, columns in expected.items():
            persisted = set(_table_columns(connection, table))
            assert persisted - {"capture_id", "derivation_version_id"} == set(columns), table
        context = set(_table_columns(connection, CONTEXT_TABLE))
    request_columns = {column for column in context if column.startswith("request_")}
    result_columns = {
        "result_target",
        "result_target_state",
        "result_location_code",
        "result_location_code_state",
        "result_language_code",
        "result_language_code_state",
        "result_se_type",
        "result_se_type_state",
        "total_count",
        "items_count",
    }
    # The closed allowance for validated-but-not-redundantly-surfaced relational and
    # provenance columns. There is no open-ended escape hatch.
    provenance = {"capture_id", "derivation_version_id", "attempt_id", "requested_target"}
    assert context == request_columns | result_columns | provenance
    assert request_columns == {
        f"request_{key}" for key in REQUEST_KEYS if key != "target"
    }


def _json_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, member in value.items():
            keys.add(str(key))
            keys |= _json_keys(member)
    elif isinstance(value, list):
        for member in value:
            keys |= _json_keys(member)
    return keys


# The documented RANK-06 grouping rules, restated here so the response can be checked
# against schema testimony rather than against the reader's own tuples.
_GROUPED_STATE_ONLY = {
    "rank_changes_state": "rank_changes",
    "rank_info_state": "rank_info",
    "search_volume_trend_state": "search_volume_trend",
    **{column: name for column, (name, _table) in _ENCLOSING.items()},
}
_GROUP_PREFIXES = ("ranked_element_", "rank_changes_", "rank_info_", "trend_")


def _expected_leaf(column: str, names: set[str]) -> str:
    if column in _GROUPED_STATE_ONLY:
        return _GROUPED_STATE_ONLY[column]
    base = column
    if base.endswith("_state") and base[: -len("_state")] in names:
        base = base[: -len("_state")]
    for prefix in _GROUP_PREFIXES:
        if base.startswith(prefix):
            base = base[len(prefix) :]
            break
    return "se_type" if base == "serp_item_se_type" else base


def test_every_projected_column_reaches_the_response(
    ready: tuple[TestClient, EvidenceStore, str, str], postgres_dsn: str
) -> None:
    """Every persisted content column, discovered from information_schema, has a leaf key."""

    client, _store, _attempt_id, _capture_id = ready
    served = _json_keys(_one_capture(client))
    with connect(postgres_dsn) as connection:
        for table in RANK05_TABLES:
            if table == CONTEXT_TABLE:
                continue
            columns = set(_content_columns(connection, table))
            for column in sorted(columns):
                assert _expected_leaf(column, columns) in served, f"{table}.{column}"
        context = set(_content_columns(connection, CONTEXT_TABLE))
    stripped: dict[str, str] = {}
    for column in context:
        # The two provenance keys are validated but never redundantly surfaced.
        if column in {"attempt_id", "requested_target"}:
            continue
        leaf = column
        for prefix in ("request_", "result_"):
            if leaf.startswith(prefix):
                leaf = leaf[len(prefix) :]
                break
        stripped[column] = leaf
    names = set(stripped.values())
    for column, leaf in sorted(stripped.items()):
        assert _expected_leaf(leaf, names) in served, column


# --------------------------------------------------------------------------------------
# Typed OpenAPI
# --------------------------------------------------------------------------------------


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


def _closed(schema: dict[str, Any], keys: set[str]) -> dict[str, Any]:
    assert schema.get("additionalProperties") is False, schema.get("title")
    assert set(schema["required"]) == keys, schema.get("title")
    assert set(schema["properties"]) == keys, schema.get("title")
    properties = schema["properties"]
    assert isinstance(properties, dict)
    return properties


def _response_schema(spec: dict[str, Any]) -> dict[str, Any]:
    route = spec["paths"][HISTORY]["get"]
    schema = route["responses"]["200"]["content"]["application/json"]["schema"]
    return _resolve(spec, schema)


def _descriptions(spec: dict[str, Any]) -> str:
    return json.dumps(spec["components"]["schemas"]) + json.dumps(
        spec["paths"][HISTORY]
    )


def test_generated_openapi_declares_the_exact_query_contract(tmp_path: Path) -> None:
    spec = _spec(tmp_path)
    assert HISTORY in spec["paths"]
    assert "/v1/providers/dataforseo/google/ranked-keywords/outcomes" not in spec["paths"]
    assert "/v1/providers/dataforseo/google/ranked-keywords/holdings" not in spec["paths"]
    route = spec["paths"][HISTORY]["get"]
    params = {entry["name"]: entry for entry in route["parameters"]}
    assert set(params) == {
        "requested_target",
        "derivation_version_id",
        "limit",
        "order",
    }
    assert "requested_keyword" not in params
    subject = _resolve(spec, params["requested_target"]["schema"])
    assert params["requested_target"]["required"] is True
    assert subject.get("minLength") == 1
    assert "maxLength" not in subject
    assert "pattern" not in subject
    assert params["derivation_version_id"].get("required") in {None, False}
    limit = _resolve(spec, params["limit"]["schema"])
    assert limit.get("minimum") == 1
    assert limit.get("maximum") == 100
    assert limit.get("default") == 20
    order = _resolve(spec, params["order"]["schema"])
    assert set(order.get("enum", [])) == {"asc", "desc"}


def test_generated_openapi_is_fully_typed_and_closed(tmp_path: Path) -> None:
    spec = _spec(tmp_path)
    envelope = _closed(_response_schema(spec), HISTORY_KEYS)
    assert envelope["requested_target"].get("minLength") == 1
    kinds = _resolve(spec, envelope["observation_kinds"])
    assert kinds["prefixItems"] == [
        {"type": "string", "const": CORPUS_METRICS_KIND},
        {"type": "string", "const": KEYWORD_DATA_KIND},
        {"type": "string", "const": MONTHLY_KIND},
        {"type": "string", "const": RANKED_RESULT_KIND},
    ]
    capture = _resolve(spec, _resolve(spec, envelope["captures"])["items"])
    properties = _closed(capture, CAPTURE_KEYS)
    assert _resolve(spec, properties["derivation_version_id"])["const"] == (
        RANKED_KEYWORDS_RECIPE_ID
    )
    assert _resolve(spec, properties["adapter_contract"])["const"] == (
        RANKED_KEYWORDS_ADAPTER_CONTRACT
    )
    request = _closed(_resolve(spec, properties["request"]), REQUEST_KEYS)
    assert _resolve(spec, request["location_code"])["const"] == 2840
    assert _resolve(spec, request["include_clickstream_data"])["const"] is False
    assert _resolve(spec, request["load_rank_absolute"])["const"] is True
    context = _closed(_resolve(spec, properties["result_context"]), RESULT_CONTEXT_KEYS)
    assert set(context) == RESULT_CONTEXT_KEYS
    corpus_items = _resolve(spec, properties["corpus_metrics"])
    assert corpus_items["minItems"] == 10
    assert corpus_items["maxItems"] == 10
    corpus = _closed(
        _resolve(spec, corpus_items["items"]),
        {
            "observation_kind",
            "within_capture_identity",
            "requested_target",
            "aggregate_family",
            "rank_system",
            "position_buckets",
            "movement_counts",
            "count",
            "etv",
            "estimated_paid_traffic_cost",
            "clickstream_etv_state",
            "clickstream_gender_distribution_state",
            "clickstream_age_distribution_state",
        },
    )
    assert set(_resolve(spec, corpus["rank_system"])["enum"]) == set(RANK_SYSTEMS)
    _closed(_resolve(spec, corpus["position_buckets"]), set(BUCKET_NAMES))
    _closed(_resolve(spec, corpus["movement_counts"]), set(MOVEMENT_NAMES))
    placement = _closed(
        _resolve(spec, _resolve(spec, properties["ranked_results"])["items"]),
        {
            "observation_kind",
            "within_capture_identity",
            "requested_target",
            "keyword",
            "serp_item_type",
            "rank_group",
            "rank_absolute",
            "ranked_element",
            "serp_item",
        },
    )
    _closed(
        _resolve(spec, placement["ranked_element"]),
        {
            "se_type",
            "check_url",
            "se_results_count",
            "keyword_difficulty",
            "is_lost",
            "serp_item_types",
            "last_updated_time",
            "previous_updated_time",
        },
    )
    serp = _closed(
        _resolve(spec, placement["serp_item"]),
        {
            "se_type",
            "url",
            "position",
            "xpath",
            "domain",
            "main_domain",
            "website_name",
            "relative_url",
            "title",
            "description",
            "breadcrumb_state",
            "pre_snippet_state",
            "highlighted_state",
            "is_image",
            "is_video",
            "is_featured_snippet",
            "is_malicious",
            "amp_version",
            "etv",
            "estimated_paid_traffic_cost",
            "clickstream_etv_state",
            "rank_changes",
            "rank_info",
            "about_this_result_state",
            "backlinks_info_state",
            "extended_snippet_state",
            "links_state",
            "rating_state",
        },
    )
    _closed(
        _resolve(spec, serp["rank_changes"]),
        {"state", "is_new", "is_up", "is_down", "previous_rank_absolute"},
    )
    _closed(
        _resolve(spec, serp["rank_info"]), {"state", "page_rank", "main_domain_rank"}
    )
    keyword_fact = _closed(
        _resolve(spec, _resolve(spec, properties["keyword_data"])["items"]),
        {
            "observation_kind",
            "within_capture_identity",
            "requested_target",
            "keyword",
            "location_code",
            "language_code",
            "se_type",
            "keyword_info",
            "keyword_properties",
            "avg_backlinks",
            "search_intent",
            "keyword_serp_info",
            "bing_normalized_state",
            "clickstream_normalized_state",
            "clickstream_keyword_info_state",
        },
    )
    info_value = [
        option
        for option in _options(spec, _closed(
            _resolve(spec, keyword_fact["keyword_info"]), {"state", "value"}
        )["value"])
        if option.get("type") != "null"
    ][0]
    info = _closed(
        info_value,
        {
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
            "search_volume_trend",
        },
    )
    _closed(
        _resolve(spec, info["search_volume_trend"]),
        {"state", "monthly", "quarterly", "yearly"},
    )
    monthly = _closed(
        _resolve(spec, _resolve(spec, properties["monthly_search_volume"])["items"]),
        {
            "observation_kind",
            "within_capture_identity",
            "requested_target",
            "keyword",
            "data_period",
            "search_volume",
            "occurrences",
        },
    )
    _closed(_resolve(spec, monthly["data_period"]), {"year", "month"})
    _closed(
        _resolve(spec, _resolve(spec, properties["item_occurrences"])["items"]),
        {
            "item_index",
            "ranked_result_identity",
            "ranked_result_kind",
            "keyword_data_identity",
            "keyword_data_kind",
            "item_se_type",
        },
    )


def test_generated_openapi_teaches_the_required_distinctions(tmp_path: Path) -> None:
    text = _descriptions(_spec(tmp_path))
    for phrase in (
        "whole Capture documents",
        "corpus the returned item prefix does not sample",
        "two independently stated provider answers",
        "placement content, not identity",
        "canonical Page",
        "Evidence-only",
        "Data Period",
        "never inherits Capture time",
        "not a fifth Observation kind",
        "zero-item result is ordinary",
        "request-disabled",
        "never measured",
        "no Ranked Measurement Outcomes and no Ranked Holdings",
        "not the frozen provider order_by",
        "unreturned corpus rows are unknown",
        "never derived from, replaced by, or checked against the newest monthly point",
    ):
        assert phrase in text, phrase


def test_openapi_adds_exactly_one_ranked_keywords_path(tmp_path: Path) -> None:
    paths = set(_spec(tmp_path)["paths"])
    assert HISTORY in paths
    assert {path for path in paths if "ranked-keywords" in path} == {HISTORY}
    assert "/v1/attempts/{attempt_id}" in paths


SIBLING_HISTORY_ROUTES = (
    "/v1/providers/dataforseo/google/keyword-overview/history",
    "/v1/providers/dataforseo/google/organic/history",
    "/v1/providers/dataforseo/google/ai-optimization/search-mentions/history",
    "/v1/providers/dataforseo/google/ai-optimization/target-metrics/history",
    "/v1/providers/dataforseo/google/ai-optimization/llm-mentions-historical/history",
    RELATED_HISTORY,
)


def test_sibling_provider_surfaces_remain_unselected_and_isolated(
    ready: tuple[TestClient, EvidenceStore, str, str],
) -> None:
    client, _store, _attempt_id, _capture_id = ready
    assert _history(client).status_code == 200
    for route in SIBLING_HISTORY_ROUTES:
        response = client.get(route + "?" + urlencode({"requested_keyword": TARGET}))
        assert response.status_code == 503, route
        assert response.json() == {"detail": NOT_SELECTED_SIGNAL}, route


def test_selecting_a_sibling_surface_does_not_disturb_ranked(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_related_keywords(store, connection)
        select_provider_recipe(
            connection, RELATED_KEYWORDS_ADAPTER_CONTRACT, RELATED_KEYWORDS_RECIPE_ID
        )
    with _app(store, postgres_dsn) as client:
        assert _history(client).status_code == 200
        related = client.get(
            RELATED_HISTORY + "?" + urlencode({"requested_keyword": "anything"})
        )
    assert related.status_code == 200
    assert related.json()["total_matching"] == 0


# --------------------------------------------------------------------------------------
# Envelope and field model unit proofs
# --------------------------------------------------------------------------------------


def _minimal_envelope() -> dict[str, Any]:
    return {
        "provider": "dataforseo",
        "adapter_contract": RANKED_KEYWORDS_ADAPTER_CONTRACT,
        "requested_target": TARGET,
        "derivation_version_id": RANKED_KEYWORDS_RECIPE_ID,
        "recipe_resolution": "selected",
        "observation_kinds": [
            CORPUS_METRICS_KIND,
            KEYWORD_DATA_KIND,
            MONTHLY_KIND,
            RANKED_RESULT_KIND,
        ],
        "captures": [],
        "total_matching": 0,
        "returned_count": 0,
        "limit": 20,
        "order": "asc",
        "has_more": False,
    }


def test_minimal_envelope_validates() -> None:
    assert RankedKeywordsHistoryEnvelope.model_validate(
        _minimal_envelope()
    ).requested_target == TARGET


@pytest.mark.parametrize(
    "overrides",
    [
        {"requested_target": ""},
        {"provider": "ahrefs"},
        {"derivation_version_id": "a" * 64},
        {"observation_kinds": [CORPUS_METRICS_KIND]},
        {
            "observation_kinds": [
                KEYWORD_DATA_KIND,
                CORPUS_METRICS_KIND,
                MONTHLY_KIND,
                RANKED_RESULT_KIND,
            ]
        },
        {"recipe_resolution": "guessed"},
        {"limit": 101},
        {"limit": 0},
        {"order": "sideways"},
        {"requested_keyword": TARGET},
    ],
)
def test_malformed_envelope_projection_fails_closed(overrides: dict[str, Any]) -> None:
    payload = {**_minimal_envelope(), **overrides}
    with pytest.raises(ValidationError):
        RankedKeywordsHistoryEnvelope.model_validate(payload)


@pytest.mark.parametrize(
    "payload",
    [
        {"state": "stated", "value": None},
        {"state": "absent", "value": "text"},
        {"state": "json_null", "value": "text"},
    ],
)
def test_state_value_disagreement_fails_closed(payload: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        RankedKeywordsTextField.model_validate(payload)


def test_decimal_fields_never_accept_binary_floats() -> None:
    with pytest.raises(ValidationError):
        RankedKeywordsDecimalField.model_validate({"state": "stated", "value": 1.5})
    assert RankedKeywordsDecimalField.model_validate(
        {"state": "stated", "value": "1.5"}
    ).value == "1.5"


def _corpus_fact(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "observation_kind": CORPUS_METRICS_KIND,
        "within_capture_identity": "a" * 64,
        "requested_target": TARGET,
        "aggregate_family": "organic",
        "rank_system": "rank_group",
        "position_buckets": {name: 0 for name in BUCKET_NAMES},
        "movement_counts": {name: 0 for name in MOVEMENT_NAMES},
        "count": {"state": "stated", "value": 0},
        "etv": {"state": "stated", "value": "0"},
        "estimated_paid_traffic_cost": {"state": "stated", "value": "0"},
        "clickstream_etv_state": "not_requested",
        "clickstream_gender_distribution_state": "not_requested",
        "clickstream_age_distribution_state": "not_requested",
    }
    payload.update(overrides)
    return payload


@pytest.mark.parametrize(
    "overrides",
    [
        {"count": {"state": "inapplicable", "value": None}},
        {"etv": {"state": "inapplicable", "value": None}},
        {"estimated_paid_traffic_cost": {"state": "inapplicable", "value": None}},
    ],
)
def test_rank_group_corpus_applicability_fails_closed(
    overrides: dict[str, Any],
) -> None:
    with pytest.raises(ValidationError):
        RankedKeywordsCorpusMetricsFact.model_validate(_corpus_fact(**overrides))


def test_rank_absolute_corpus_applicability_fails_closed() -> None:
    absolute = _corpus_fact(
        rank_system="rank_absolute",
        count={"state": "inapplicable", "value": None},
        etv={"state": "inapplicable", "value": None},
        estimated_paid_traffic_cost={"state": "inapplicable", "value": None},
    )
    assert RankedKeywordsCorpusMetricsFact.model_validate(absolute).rank_system == (
        "rank_absolute"
    )
    with pytest.raises(ValidationError):
        RankedKeywordsCorpusMetricsFact.model_validate(
            {**absolute, "count": {"state": "stated", "value": 3}}
        )


def test_inline_rank_changes_member_coupling_fails_closed() -> None:
    stated = {
        "state": "stated",
        "is_new": {"state": "stated", "value": False},
        "is_up": {"state": "stated", "value": False},
        "is_down": {"state": "stated", "value": True},
        "previous_rank_absolute": {"state": "stated", "value": 3},
    }
    assert RankedKeywordsRankChanges.model_validate(stated).state == "stated"
    with pytest.raises(ValidationError):
        RankedKeywordsRankChanges.model_validate(
            {**stated, "is_new": {"state": "inapplicable", "value": None}}
        )
    unstated = {
        "state": "json_null",
        **{
            member: {"state": "inapplicable", "value": None}
            for member in ("is_new", "is_up", "is_down", "previous_rank_absolute")
        },
    }
    assert RankedKeywordsRankChanges.model_validate(unstated).state == "json_null"
    with pytest.raises(ValidationError):
        RankedKeywordsRankChanges.model_validate(
            {**unstated, "is_up": {"state": "absent", "value": None}}
        )


# --------------------------------------------------------------------------------------
# Golden RANK-03 content proof
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
    capture: Mapping[str, Any], keyword: str
) -> dict[str, Any] | None:
    points = [
        fact
        for fact in capture["monthly_search_volume"]
        if fact["keyword"] == keyword
    ]
    if not points:
        return None
    newest = max(
        points,
        key=lambda fact: (fact["data_period"]["year"], fact["data_period"]["month"]),
    )
    return dict(newest)


def test_golden_rank03_capture_matches_persisted_state_and_evidence(
    golden: tuple[TestClient, EvidenceStore, str], postgres_dsn: str
) -> None:
    client, store, capture_id = golden
    capture = _one_capture(client)
    with connect(postgres_dsn) as connection:
        expected = _expected_capture(connection, store, capture_id)
    assert capture == expected

    assert len(capture["corpus_metrics"]) == GOLDEN_CORPUS
    assert len(capture["ranked_results"]) == GOLDEN_RANKED_RESULTS
    assert len(capture["keyword_data"]) == GOLDEN_KEYWORD_DATA
    assert len(capture["monthly_search_volume"]) == GOLDEN_MONTHLY
    assert len(capture["item_occurrences"]) == GOLDEN_ITEM_OCCURRENCES
    assert sum(
        len(fact["occurrences"]) for fact in capture["monthly_search_volume"]
    ) == GOLDEN_MONTHLY_OCCURRENCES
    assert capture["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": GOLDEN_ENVELOPES,
    }
    assert (
        GOLDEN_CORPUS + GOLDEN_RANKED_RESULTS + GOLDEN_KEYWORD_DATA + GOLDEN_MONTHLY
        == GOLDEN_ENVELOPES
    )

    context = capture["result_context"]
    assert context["items_count"] == GOLDEN_ITEMS_COUNT
    assert context["total_count"] == GOLDEN_TOTAL_COUNT
    assert context["items_count"] != context["total_count"]
    assert capture["request"]["limit"] == 100
    assert capture["request"]["offset"] == 0
    assert capture["request"]["order_by"] == [
        "ranked_serp_element.serp_item.rank_group,asc"
    ]
    assert capture["request"]["target"] == TARGET


def test_golden_rank_systems_disagree_without_reconciliation(
    golden: tuple[TestClient, EvidenceStore, str],
) -> None:
    """The frozen 248-versus-244 organic bucket behaviour is valid provider testimony."""

    client, _store, _capture_id = golden
    capture = _one_capture(client)
    by_key = {
        (fact["aggregate_family"], fact["rank_system"]): fact
        for fact in capture["corpus_metrics"]
    }
    group = by_key[("organic", "rank_group")]
    absolute = by_key[("organic", "rank_absolute")]
    group_total = sum(group["position_buckets"].values())
    absolute_total = sum(absolute["position_buckets"].values())
    assert group_total != absolute_total
    assert group["count"] == {"state": "stated", "value": GOLDEN_TOTAL_COUNT}
    assert group_total == GOLDEN_TOTAL_COUNT
    assert absolute_total == 244
    assert absolute["count"] == {"state": "inapplicable", "value": None}
    # None of those numbers relates to the returned prefix.
    assert capture["result_context"]["items_count"] == GOLDEN_ITEMS_COUNT


def test_golden_urls_are_repeated_content_not_identity(
    golden: tuple[TestClient, EvidenceStore, str],
) -> None:
    client, _store, _capture_id = golden
    capture = _one_capture(client)
    urls = [fact["serp_item"]["url"] for fact in capture["ranked_results"]]
    assert len(urls) == GOLDEN_RANKED_RESULTS
    assert len(set(urls)) == GOLDEN_UNIQUE_URLS
    identities = {fact["within_capture_identity"] for fact in capture["ranked_results"]}
    assert len(identities) == GOLDEN_RANKED_RESULTS


def test_golden_current_and_monthly_volumes_disagree(
    golden: tuple[TestClient, EvidenceStore, str],
) -> None:
    client, _store, _capture_id = golden
    capture = _one_capture(client)
    disagreements = 0
    for fact in capture["keyword_data"]:
        info = fact["keyword_info"]
        if info["state"] != "stated":
            continue
        current = info["value"]["search_volume"]
        newest = _newest_monthly(capture, fact["keyword"])
        if current["state"] != "stated" or newest is None:
            continue
        if current["value"] != newest["search_volume"]:
            disagreements += 1
    assert disagreements > 0


def test_golden_element_and_keyword_serp_clocks_stay_separate_columns(
    golden: tuple[TestClient, EvidenceStore, str],
) -> None:
    client, _store, _capture_id = golden
    capture = _one_capture(client)
    element_clocks = {
        fact["ranked_element"]["last_updated_time"]["value"]
        for fact in capture["ranked_results"]
    }
    keyword_clocks = {
        fact["keyword_serp_info"]["value"]["keyword_serp_last_updated_time"]["value"]
        for fact in capture["keyword_data"]
        if fact["keyword_serp_info"]["state"] == "stated"
    }
    assert element_clocks and keyword_clocks
    serialized = json.dumps(capture)
    assert '"provider_update_time"' not in serialized
    assert '"last_updated"' not in serialized


def test_golden_every_placement_and_keyword_is_reachable_from_an_occurrence(
    golden: tuple[TestClient, EvidenceStore, str],
) -> None:
    client, _store, _capture_id = golden
    capture = _one_capture(client)
    occurrences = capture["item_occurrences"]
    assert [entry["item_index"] for entry in occurrences] == list(
        range(GOLDEN_ITEMS_COUNT)
    )
    placements = {entry["ranked_result_identity"] for entry in occurrences}
    keywords = {entry["keyword_data_identity"] for entry in occurrences}
    assert placements == {
        fact["within_capture_identity"] for fact in capture["ranked_results"]
    }
    assert keywords == {
        fact["within_capture_identity"] for fact in capture["keyword_data"]
    }
    assert all(entry["item_se_type"] == "google" for entry in occurrences)


def test_golden_read_leaves_evidence_and_postgresql_untouched(
    golden: tuple[TestClient, EvidenceStore, str], postgres_dsn: str
) -> None:
    client, store, _capture_id = golden
    before = _snapshot(postgres_dsn)
    before_ids = (
        set(store.list_committed_ids("attempts")),
        set(store.list_committed_ids("captures")),
    )
    assert _history(client).status_code == 200
    assert _snapshot(postgres_dsn) == before
    assert (
        set(store.list_committed_ids("attempts")),
        set(store.list_committed_ids("captures")),
    ) == before_ids


# --------------------------------------------------------------------------------------
# Recipe literals and the zero-network boundary
# --------------------------------------------------------------------------------------


def test_recipe_v1_literal_identity_kinds_and_taxonomy() -> None:
    """RANK-06 reads the accepted Recipe from the derive module, never the parser module."""

    assert RANKED_KEYWORDS_RECIPE_ID == (
        "c7573695db7ecaa0f5dfdc2fc3658e84b1673eec005a0d8003093e57408294a8"
    )
    assert len(recipe_bytes(RANKED_KEYWORDS_RECIPE)) == 2825
    assert recipe_derivation_version_id(RANKED_KEYWORDS_RECIPE) == (
        RANKED_KEYWORDS_RECIPE_ID
    )
    assert RANKED_KEYWORDS_RECIPE["observation_kinds"] == [
        CORPUS_METRICS_KIND,
        KEYWORD_DATA_KIND,
        MONTHLY_KIND,
        RANKED_RESULT_KIND,
    ]
    admission = RANKED_KEYWORDS_RECIPE["admission"]
    assert isinstance(admission, Mapping)
    assert admission["capture_outcomes"] == [
        "no_response",
        "observation_admitted",
        "provider_envelope_rejected",
        "provider_error",
        "response_partial",
        "transport_complete_non_admissible",
    ]
    # The identity section orders its kinds differently inside the same document.
    identity_section = RANKED_KEYWORDS_RECIPE["observation_identity"]
    assert isinstance(identity_section, Mapping)
    kinds = identity_section["kinds"]
    assert isinstance(kinds, list)
    assert [entry["observation_kind"] for entry in kinds] != list(
        RANKED_KEYWORDS_RECIPE["observation_kinds"]
    )


def test_reader_module_reads_the_recipe_from_the_derive_module() -> None:
    import observatory.ranked_keywords_read as reader

    source = Path(reader.__file__).read_text(encoding="utf-8")
    assert "from observatory.google_ranked_keywords_derive import (" in source
    assert "RANKED_KEYWORDS_RECIPE," in source
    assert "observation_identity.kinds" in source


def test_autouse_guard_blocks_public_network() -> None:
    with pytest.raises(AssertionError, match="public-network request forbidden"):
        socket.create_connection(("api.dataforseo.com", 443))


def test_no_credentials_in_environment() -> None:
    import os

    assert os.environ.get("OBSERVATORY_DATAFORSEO_LOGIN") is None
    assert os.environ.get("OBSERVATORY_DATAFORSEO_PASSWORD") is None
