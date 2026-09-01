"""RANK-05: Ranked Keywords provider Derivation into real PostgreSQL.

Most adversarial proofs use small synthetic bodies. The frozen RANK-03 fixture and the
disposable PostgreSQL loop are reserved for the golden and rebuild proofs that genuinely
need them. Every golden count is recomputed from the committed fixture here rather than
copied from production code, and none of them is a provider invariant.
"""

from __future__ import annotations

import copy
import json
import socket
from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from psycopg import sql
from psycopg.errors import CheckViolation, ForeignKeyViolation

from observatory.capture_event import (
    RANKED_KEYWORDS_ADAPTER_CONTRACT,
    DocumentError,
    body_ref,
    canonical_json,
    ranked_keywords_http_attempt_document,
    ranked_keywords_http_capture_document,
)
from observatory.dataforseo_google_ranked_keywords import (
    CORPUS_METRICS_KIND,
    KEYWORD_DATA_KIND,
    MONTHLY_KIND,
    PARSER_CONTRACT,
    PROVIDER,
    RANK_SYSTEM_ABSOLUTE,
    RANK_SYSTEM_GROUP,
    RANK_SYSTEMS,
    RANKED_RESULT_KIND,
    REQUESTED_ITEM_TYPES,
)
from observatory.dataforseo_google_ranked_keywords_paid_probe import (
    closed_ranked_keywords_parameters,
    ranked_keywords_request_body_bytes,
)
from observatory.dataforseo_keyword_overview import CORE_RECIPE_ID
from observatory.derive import DerivationError
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
    RANKED_KEYWORDS_RECIPE_BYTES,
    RANKED_KEYWORDS_RECIPE_ID,
    RANKED_RESULTS_TABLE,
    SemanticDisagreement,
    _require_text,
    derive_google_ranked_keywords,
    plan_ranked_keywords_capture,
    ranked_keywords_recipe,
)
from observatory.migrate import (
    PRE_RANK05_SCHEMA_STATEMENTS,
    PRE_RK04_SCHEMA_STATEMENTS,
    RANK05_SCHEMA_STATEMENTS,
    RANKED_KEYWORDS_CORPUS_METRICS_KIND,
    RANKED_KEYWORDS_KEYWORD_DATA_KIND,
    RANKED_KEYWORDS_MONTHLY_KIND,
    RANKED_KEYWORDS_RANKED_RESULT_KIND,
    SCHEMA_STATEMENTS,
    apply_migrations,
    connect,
)
from observatory.provider_recipe import recipe_bytes, recipe_derivation_version_id

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_google_ranked_keywords_rank03.json"
)
TARGET = "theconspiratory.com"
FIXTURE_BYTES = 390955
FIXTURE_SHA256 = "5b0e7cb6a03a921039a2845c62bd6a91eba9d61e2b54240e9af15414ba1fbc84"

# Frozen-Capture consequences of the accepted model. These are fixture facts, never provider
# invariants, and never production constants: every one is recomputed from the committed
# body by `test_golden_counts_are_independently_derived_from_the_fixture`.
GOLDEN_CORPUS_METRICS = 10
GOLDEN_RANKED_RESULTS = 100
GOLDEN_KEYWORD_DATA = 100
GOLDEN_MONTHLY = 1200
GOLDEN_ENVELOPES = 1410
GOLDEN_ITEM_OCCURRENCES = 100
GOLDEN_MONTHLY_OCCURRENCES = 1200
GOLDEN_UNIQUE_URLS = 57
GOLDEN_TOTAL_COUNT = 248
GOLDEN_ITEMS_COUNT = 100

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
UNSUPPORTED_CHILD_STATES = (
    "about_this_result_state",
    "backlinks_info_state",
    "extended_snippet_state",
    "links_state",
    "rating_state",
)
PROSE_STATE_ONLY = ("breadcrumb_state", "pre_snippet_state", "highlighted_state")
# The four time pillars, as they land in column names. No relation may add a universal
# provider clock beside them.
SOURCE_LOCAL_CLOCKS = (
    "ranked_element_last_updated_time",
    "ranked_element_previous_updated_time",
    "keyword_serp_last_updated_time",
    "keyword_serp_previous_updated_time",
    "keyword_info_last_updated_time",
    "avg_backlinks_last_updated_time",
    "search_intent_last_updated_time",
)

CLOCK = "2026-08-31 12:00:00 +00:00"
PREVIOUS_CLOCK = "2026-07-31 12:00:00 +00:00"
# Deliberately hostile persisted text, written as escapes: a NUL PostgreSQL TEXT cannot
# store, a lone surrogate, and two Unicode noncharacters the canonical-I-JSON boundary
# rejects.
NUL = "\x00"
LONE_SURROGATE = "\ud800"
NONCHARACTER_FDD0 = "\ufdd0"
NONCHARACTER_FFFF = "\uffff"
NONCHARACTER_FFFE = "\ufffe"
HOSTILE_TEXT = (NUL, LONE_SURROGATE, NONCHARACTER_FDD0, NONCHARACTER_FFFF)
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


def _fixture_body() -> bytes:
    return FIXTURE.read_bytes()


def _fixture_document() -> dict[str, Any]:
    document = json.loads(_fixture_body())
    assert isinstance(document, dict)
    return document


def _fixture_items() -> list[dict[str, Any]]:
    items = _fixture_document()["tasks"][0]["result"][0]["items"]
    assert isinstance(items, list)
    return items


def _params(target: str = TARGET) -> dict[str, object]:
    return closed_ranked_keywords_parameters(target=target)


def _complete_capture_dict() -> dict[str, object]:
    return {
        "transport_state": "response_complete",
        "response": {"completeness": "complete"},
    }


def _plan(
    body: bytes | None,
    parameters: dict[str, object] | None = None,
    capture: dict[str, object] | None = None,
) -> Any:
    return plan_ranked_keywords_capture(
        "a" * 64,
        "b" * 64,
        capture if capture is not None else _complete_capture_dict(),
        parameters if parameters is not None else _params(),
        body,
    )


def _golden_plan() -> Any:
    planned = _plan(_fixture_body())
    assert planned is not None
    return planned


def _rows(planned: Any, table: str) -> list[dict[str, Any]]:
    return [dict(row) for row in planned.details[table]]


def _kinds(planned: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for envelope in planned.envelopes:
        counts[envelope.observation_kind] = counts.get(envelope.observation_kind, 0) + 1
    return counts


# --------------------------------------------------------------------------------------
# Synthetic body builders
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
    return {
        name: per_family.get(name, metrics_family()) for name in REQUESTED_ITEM_TYPES
    }


def all_metrics_absolute(**per_family: Any) -> dict[str, Any]:
    return {
        name: per_family.get(name, metrics_absolute_family())
        for name in REQUESTED_ITEM_TYPES
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
        "serp_item_types": ["organic", "ai_overview"],
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


def keyword_data(keyword: str, **overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {"keyword": keyword}
    data.update(overrides)
    return {key: value for key, value in data.items() if value is not OMIT}


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


def synthetic_body(
    result: dict[str, Any] | None,
    *,
    status_code: int = 20000,
    status_message: str = "Ok.",
    result_count: int | None = None,
) -> bytes:
    results = [] if result is None else [result]
    document: dict[str, Any] = {
        "version": "0.1.20260101",
        "status_code": status_code,
        "status_message": status_message,
        "time": "0.5 sec.",
        "cost": 0.05,
        "tasks_count": 1,
        "tasks_error": 0 if status_code == 20000 else 1,
        "tasks": [
            {
                "id": "task-1",
                "status_code": status_code,
                "status_message": status_message,
                "time": "0.5 sec.",
                "cost": 0.05,
                "result_count": len(results) if result_count is None else result_count,
                "path": [
                    "v3",
                    "dataforseo_labs",
                    "google",
                    "ranked_keywords",
                    "live",
                ],
                "data": {
                    "api": "dataforseo_labs",
                    "function": "ranked_keywords",
                    "se_type": "google",
                },
                "result": results,
            }
        ],
    }
    if status_code != 20000:
        document["tasks"][0]["result"] = None
    # ensure_ascii keeps a deliberately hostile lone surrogate expressible as a \uXXXX
    # escape, which is exactly how a provider could deliver one.
    return json.dumps(document, ensure_ascii=True).encode("utf-8")


def simple_body(items: list[dict[str, Any]], **kwargs: Any) -> bytes:
    return synthetic_body(result_document(items, **kwargs))


# --------------------------------------------------------------------------------------
# Evidence helpers
# --------------------------------------------------------------------------------------


def _attempt(nonce: str, target: str = TARGET) -> dict[str, object]:
    return ranked_keywords_http_attempt_document(
        parameters=_params(target),
        attempt_nonce=nonce,
        authorized_at="2026-08-31T10:00:00.000000Z",
        observatory_version="rank05-test-v1",
    )


def _capture_document(
    attempt: dict[str, object],
    body: bytes | None,
    *,
    suffix: str = "1",
    transport_state: str = "response_complete",
    completeness: str = "complete",
) -> dict[str, object]:
    response: dict[str, object] | None
    if body is None:
        response = None
    else:
        response = {
            "status": 200,
            "http_version": "HTTP/1.1",
            "header_policy": "http-headers-v1",
            "headers": [["content-type", "application/json"]],
            "omitted_headers": [],
            "body": {"state": "present_nonempty", "body": body_ref(body)},
            "completeness": completeness,
        }
    return ranked_keywords_http_capture_document(
        attempt=attempt,
        request_started_at=f"2026-08-31T10:00:0{suffix}.100000Z",
        transport_ended_at=f"2026-08-31T10:00:0{suffix}.400000Z",
        transport_state=transport_state,
        response=response,
        transport_failure=(
            None
            if transport_state != "no_response"
            else {"kind": "connect_error", "detail": "synthetic"}
        ),
        response_headers_at=(
            None if body is None else f"2026-08-31T10:00:0{suffix}.200000Z"
        ),
        response_body_ended_at=(
            None if body is None else f"2026-08-31T10:00:0{suffix}.300000Z"
        ),
    )


def _commit(
    store: EvidenceStore,
    body: bytes | None,
    nonce: str,
    *,
    target: str = TARGET,
    suffix: str = "1",
    transport_state: str = "response_complete",
    completeness: str = "complete",
) -> tuple[str, str]:
    attempt = _attempt(nonce, target)
    attempt_id = store.commit_attempt(
        attempt, request_body=ranked_keywords_request_body_bytes(_params(target))
    )
    capture_id = store.commit_capture(
        _capture_document(
            attempt,
            body,
            suffix=suffix,
            transport_state=transport_state,
            completeness=completeness,
        ),
        response_body=body,
    )
    return attempt_id, capture_id


def _count(connection: Any, table: str) -> int:
    row = connection.execute(
        sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table))
    ).fetchone()
    return int(row[0])


def _all_rank05_counts(connection: Any) -> dict[str, int]:
    return {table: _count(connection, table) for table in RANK05_TABLES}


def _fetch_relation(
    connection: Any, table: str
) -> tuple[tuple[str, ...], tuple[Any, ...]]:
    columns = tuple(
        str(row[0])
        for row in connection.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = current_schema() AND table_name = %s
            ORDER BY column_name
            """,
            (table,),
        ).fetchall()
    )
    if not columns:
        return (), ()
    ordered = sql.SQL(", ").join(sql.Identifier(name) for name in columns)
    rows = connection.execute(
        sql.SQL("SELECT {} FROM {} ORDER BY {}").format(
            ordered, sql.Identifier(table), ordered
        )
    ).fetchall()
    return columns, tuple(tuple(row) for row in rows)


@pytest.fixture
def derived(
    tmp_path: Path, postgres_dsn: str
) -> Iterator[tuple[Any, EvidenceStore, str, str]]:
    """One committed synthetic Capture derived into a migrated database."""

    store = create_store(tmp_path / "rank05")
    body = simple_body(
        [
            item("alpha", data=keyword_data("alpha", keyword_info=keyword_info())),
            item(
                "beta",
                element=ranked_serp_element(
                    serp_item=serp_item(rank_group=2, rank_absolute=2)
                ),
            ),
        ]
    )
    attempt_id, capture_id = _commit(store, body, "11" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_ranked_keywords(store, connection)
        connection.commit()
        yield connection, store, attempt_id, capture_id


# --------------------------------------------------------------------------------------
# Guards
# --------------------------------------------------------------------------------------


def test_autouse_guard_blocks_public_network() -> None:
    with pytest.raises(AssertionError):
        socket.create_connection(("api.dataforseo.com", 443))


def test_no_credentials_in_environment() -> None:
    import os

    assert os.environ.get("OBSERVATORY_DATAFORSEO_LOGIN") is None
    assert os.environ.get("OBSERVATORY_DATAFORSEO_PASSWORD") is None


def test_derive_module_opens_no_provider_or_credential_seam() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "observatory"
        / "google_ranked_keywords_derive.py"
    ).read_text(encoding="utf-8")
    for token in ("httpx", "paid_probe", "DATAFORSEO_LOGIN", "observatory.api"):
        assert token not in source


# --------------------------------------------------------------------------------------
# Recipe identity and closure
# --------------------------------------------------------------------------------------


def test_recipe_is_content_addressed_and_stable() -> None:
    rebuilt = ranked_keywords_recipe()
    assert rebuilt == RANKED_KEYWORDS_RECIPE
    assert recipe_bytes(rebuilt) == RANKED_KEYWORDS_RECIPE_BYTES
    assert recipe_derivation_version_id(rebuilt) == RANKED_KEYWORDS_RECIPE_ID
    assert len(RANKED_KEYWORDS_RECIPE_ID) == 64
    assert RANKED_KEYWORDS_RECIPE_ID != CORE_RECIPE_ID


def test_recipe_declares_exactly_four_observation_kinds() -> None:
    assert RANKED_KEYWORDS_RECIPE["observation_kinds"] == [
        CORPUS_METRICS_KIND,
        KEYWORD_DATA_KIND,
        MONTHLY_KIND,
        RANKED_RESULT_KIND,
    ]
    assert CORPUS_METRICS_KIND == "dataforseo.google.ranked_keywords.corpus_metrics.v1"
    assert RANKED_RESULT_KIND == "dataforseo.google.ranked_keywords.ranked_result.v1"
    assert KEYWORD_DATA_KIND == "dataforseo.google.ranked_keywords.keyword_data.v1"
    assert MONTHLY_KIND == (
        "dataforseo.google.ranked_keywords.monthly_search_volume.v1"
    )


def test_recipe_kind_identity_axes_are_the_accepted_ones() -> None:
    section = RANKED_KEYWORDS_RECIPE["observation_identity"]
    assert isinstance(section, dict)
    entries = section["kinds"]
    assert isinstance(entries, list)
    axes = {entry["observation_kind"]: entry["axes"] for entry in entries}
    assert axes[CORPUS_METRICS_KIND] == {
        "aggregate_family": "string",
        "rank_system": "string",
        "requested_target": "string",
    }
    # Placement identity A. Exact URL is content, never identity, and the provider array
    # index appears nowhere.
    assert axes[RANKED_RESULT_KIND] == {
        "keyword": "string",
        "rank_absolute": "integer",
        "rank_group": "integer",
        "requested_target": "string",
        "serp_item_type": "string",
    }
    assert axes[KEYWORD_DATA_KIND] == {
        "keyword": "string",
        "requested_target": "string",
    }
    assert axes[MONTHLY_KIND] == {
        "keyword": "string",
        "month": "integer",
        "requested_target": "string",
        "year": "integer",
    }
    for definition in axes.values():
        for forbidden in (
            "url",
            "provider_array_index",
            "position",
            "domain",
            "main_domain",
            "is_lost",
        ):
            assert forbidden not in definition


def test_recipe_declares_exactly_six_capture_outcomes() -> None:
    admission = RANKED_KEYWORDS_RECIPE["admission"]
    assert isinstance(admission, dict)
    assert admission["capture_outcomes"] == [
        "no_response",
        "observation_admitted",
        "provider_envelope_rejected",
        "provider_error",
        "response_partial",
        "transport_complete_non_admissible",
    ]
    # Neither has a reachable RANK-05 v1 path, so neither is declared.
    assert "reconciliation_failed" not in admission["capture_outcomes"]
    assert "observation_admitted_empty" not in admission["capture_outcomes"]


def test_recipe_binds_the_ranked_parser_and_adapter() -> None:
    assert RANKED_KEYWORDS_RECIPE["parser_contract"] == PARSER_CONTRACT
    assert RANKED_KEYWORDS_RECIPE["provider"] == PROVIDER
    assert RANKED_KEYWORDS_RECIPE["adapter_contract"] == (
        RANKED_KEYWORDS_ADAPTER_CONTRACT
    )
    provider_time = RANKED_KEYWORDS_RECIPE["provider_update_time"]
    assert isinstance(provider_time, dict)
    assert provider_time["inheritance"] == "never_from_capture_or_sibling"
    assert provider_time["rule"] == (
        "structure_local_clocks_no_universal_update_time"
    )
    data_period = RANKED_KEYWORDS_RECIPE["data_period"]
    assert isinstance(data_period, dict)
    assert data_period["inheritance"] == "never_from_capture"


def test_migrate_kind_constants_match_the_parser_module() -> None:
    assert RANKED_KEYWORDS_CORPUS_METRICS_KIND == CORPUS_METRICS_KIND
    assert RANKED_KEYWORDS_RANKED_RESULT_KIND == RANKED_RESULT_KIND
    assert RANKED_KEYWORDS_KEYWORD_DATA_KIND == KEYWORD_DATA_KIND
    assert RANKED_KEYWORDS_MONTHLY_KIND == MONTHLY_KIND


def test_rank_systems_are_exactly_two() -> None:
    assert RANK_SYSTEMS == (RANK_SYSTEM_GROUP, RANK_SYSTEM_ABSOLUTE)
    assert RANK_SYSTEM_GROUP == "rank_group"
    assert RANK_SYSTEM_ABSOLUTE == "rank_absolute"


# --------------------------------------------------------------------------------------
# Migration layering
# --------------------------------------------------------------------------------------


def test_pre_rank05_layering_is_additive_and_preserves_the_rk04_delta() -> None:
    historical = [
        statement
        for statement in PRE_RANK05_SCHEMA_STATEMENTS
        if statement not in PRE_RK04_SCHEMA_STATEMENTS
    ]
    assert len(historical) == 12
    assert "ranked_keywords_" not in "\n".join(PRE_RANK05_SCHEMA_STATEMENTS)
    added = [
        statement
        for statement in SCHEMA_STATEMENTS
        if statement not in PRE_RANK05_SCHEMA_STATEMENTS
    ]
    assert added == list(RANK05_SCHEMA_STATEMENTS)
    assert len(added) == 12
    assert len(RANK05_TABLES) == 12
    for table in RANK05_TABLES:
        assert any(f"CREATE TABLE IF NOT EXISTS {table} (" in item for item in added)


def test_rank05_relation_names_are_exactly_the_accepted_twelve() -> None:
    assert RANK05_TABLES == (
        "ranked_keywords_corpus_metrics",
        "ranked_keywords_ranked_results",
        "ranked_keywords_keyword_data",
        "ranked_keywords_keyword_info",
        "ranked_keywords_keyword_properties",
        "ranked_keywords_avg_backlinks",
        "ranked_keywords_search_intent",
        "ranked_keywords_keyword_serp_info",
        "ranked_keywords_monthly_search_volume",
        "ranked_keywords_item_occurrences",
        "ranked_keywords_monthly_item_occurrences",
        "ranked_keywords_result_context",
    )


def test_no_rank05_relation_exposes_a_universal_provider_clock() -> None:
    joined = "\n".join(RANK05_SCHEMA_STATEMENTS)
    assert "provider_update_time" not in joined
    # A bare `last_updated` would be exactly the universal clock the four-pillar model
    # forbids; every real clock column is prefixed by the structure that stated it.
    assert "last_updated " not in joined
    assert "last_updated," not in joined
    for column in SOURCE_LOCAL_CLOCKS:
        assert column in joined


def test_no_rank05_relation_persists_a_completeness_claim() -> None:
    joined = "\n".join(RANK05_SCHEMA_STATEMENTS)
    for forbidden in (
        "complete",
        "truncated",
        "first_page",
        "coverage_percent",
        "corpus_exhausted",
    ):
        assert forbidden not in joined
    # Nor a JSONB provider dump, a Page/domain entity, or a cross-surface foreign key.
    assert "JSONB" not in joined
    assert "REFERENCES related_keywords" not in joined
    assert "REFERENCES google_organic" not in joined
    assert "REFERENCES keyword_overview" not in joined


def test_prose_and_unsupported_children_have_no_value_columns() -> None:
    joined = "\n".join(RANK05_SCHEMA_STATEMENTS)
    for column in (*PROSE_STATE_ONLY, *UNSUPPORTED_CHILD_STATES):
        assert column in joined
        bare = column.removesuffix("_state")
        assert f"\n    {bare} TEXT" not in joined
        assert f"\n    {bare} BOOLEAN" not in joined
        assert f"\n    {bare} TEXT[]" not in joined


# --------------------------------------------------------------------------------------
# Golden planning from the frozen RANK-03 fixture
# --------------------------------------------------------------------------------------


def test_frozen_fixture_identity_is_unchanged() -> None:
    import hashlib

    raw = _fixture_body()
    assert len(raw) == FIXTURE_BYTES
    assert hashlib.sha256(raw).hexdigest() == FIXTURE_SHA256


def test_golden_counts_are_independently_derived_from_the_fixture() -> None:
    """Recompute every golden count from the committed body, not from production code."""

    items = _fixture_items()
    keywords = {row["keyword_data"]["keyword"] for row in items}
    placements = {
        (
            row["keyword_data"]["keyword"],
            row["ranked_serp_element"]["serp_item"]["type"],
            row["ranked_serp_element"]["serp_item"]["rank_group"],
            row["ranked_serp_element"]["serp_item"]["rank_absolute"],
        )
        for row in items
    }
    periods = {
        (row["keyword_data"]["keyword"], point["year"], point["month"])
        for row in items
        for point in row["keyword_data"]["keyword_info"]["monthly_searches"]
    }
    expected_corpus = len(REQUESTED_ITEM_TYPES) * len(RANK_SYSTEMS)
    expected_envelopes = expected_corpus + len(placements) + len(keywords) + len(periods)
    assert (expected_corpus, len(placements), len(keywords), len(periods)) == (
        GOLDEN_CORPUS_METRICS,
        GOLDEN_RANKED_RESULTS,
        GOLDEN_KEYWORD_DATA,
        GOLDEN_MONTHLY,
    )
    assert expected_envelopes == GOLDEN_ENVELOPES

    planned = _golden_plan()
    assert planned.classification == "observation_admitted"
    assert len(planned.envelopes) == expected_envelopes
    assert _kinds(planned) == {
        CORPUS_METRICS_KIND: expected_corpus,
        RANKED_RESULT_KIND: len(placements),
        KEYWORD_DATA_KIND: len(keywords),
        MONTHLY_KIND: len(periods),
    }
    assert len(planned.item_occurrences) == len(items) == GOLDEN_ITEM_OCCURRENCES
    monthly_points = sum(
        len(row["keyword_data"]["keyword_info"]["monthly_searches"]) for row in items
    )
    assert len(planned.monthly_occurrences) == monthly_points
    assert monthly_points == GOLDEN_MONTHLY_OCCURRENCES
    assert planned.context is not None


def test_golden_five_families_times_two_rank_systems() -> None:
    rows = _rows(_golden_plan(), CORPUS_METRICS_TABLE)
    seen = {(row["aggregate_family"], row["rank_system"]) for row in rows}
    assert seen == {
        (family, system) for family in REQUESTED_ITEM_TYPES for system in RANK_SYSTEMS
    }
    assert len(rows) == GOLDEN_CORPUS_METRICS
    for row in rows:
        assert row["requested_target"] == TARGET


def test_golden_four_zero_families_remain_stated_not_absent() -> None:
    rows = {
        (row["aggregate_family"], row["rank_system"]): row
        for row in _rows(_golden_plan(), CORPUS_METRICS_TABLE)
    }
    zero_families = [name for name in REQUESTED_ITEM_TYPES if name != "organic"]
    assert len(zero_families) == 4
    for family in zero_families:
        group = rows[(family, RANK_SYSTEM_GROUP)]
        assert group["count"] == 0
        assert group["count_state"] == "stated"
        assert all(group[name] == 0 for name in BUCKET_NAMES)
        assert group["etv_state"] == "stated"


def test_golden_organic_248_versus_absolute_244_is_unreconciled_testimony() -> None:
    rows = {
        (row["aggregate_family"], row["rank_system"]): row
        for row in _rows(_golden_plan(), CORPUS_METRICS_TABLE)
    }
    group = rows[("organic", RANK_SYSTEM_GROUP)]
    absolute = rows[("organic", RANK_SYSTEM_ABSOLUTE)]
    assert group["count"] == GOLDEN_TOTAL_COUNT == 248
    assert sum(group[name] for name in BUCKET_NAMES) == 248
    assert sum(absolute[name] for name in BUCKET_NAMES) == 244
    # Both are stored as stated. The Recipe derives, checks, and repairs neither.
    assert group["count"] != sum(absolute[name] for name in BUCKET_NAMES)


def test_golden_absolute_locus_is_inapplicable_not_json_null() -> None:
    for row in _rows(_golden_plan(), CORPUS_METRICS_TABLE):
        if row["rank_system"] != RANK_SYSTEM_ABSOLUTE:
            continue
        for column in ("count", "etv", "estimated_paid_traffic_cost"):
            assert row[column] is None
            assert row[f"{column}_state"] == "inapplicable"
            assert row[f"{column}_state"] != "json_null"


def test_golden_every_aggregate_clickstream_locus_is_not_requested() -> None:
    for row in _rows(_golden_plan(), CORPUS_METRICS_TABLE):
        for name in CLICKSTREAM_AGGREGATE_NAMES:
            assert row[f"{name}_state"] == "not_requested"


def test_golden_prefix_boundary_is_not_a_completeness_claim() -> None:
    context = _golden_plan().context
    assert context is not None
    assert context["request_limit"] == 100
    assert context["request_offset"] == 0
    assert context["items_count"] == GOLDEN_ITEMS_COUNT
    assert context["total_count"] == GOLDEN_TOTAL_COUNT
    assert context["items_count"] < context["total_count"]
    for forbidden in (
        "complete",
        "truncated",
        "first_page",
        "coverage_percent",
        "corpus_exhausted",
    ):
        assert forbidden not in context


def test_golden_context_preserves_request_authority_and_result_testimony() -> None:
    context = _golden_plan().context
    assert context is not None
    assert context["requested_target"] == TARGET
    assert context["request_location_code"] == 2840
    assert context["request_language_code"] == "en"
    assert context["request_item_types"] == list(REQUESTED_ITEM_TYPES)
    assert context["request_ignore_synonyms"] is False
    assert context["request_include_clickstream_data"] is False
    assert context["request_load_rank_absolute"] is True
    assert context["request_historical_serp_mode"] == "all"
    assert context["request_order_by"] == [
        "ranked_serp_element.serp_item.rank_group,asc"
    ]
    assert context["result_target"] == TARGET
    assert context["result_target_state"] == "stated"
    assert context["result_se_type"] == "google"


def test_golden_one_hundred_unique_keywords_and_placements() -> None:
    planned = _golden_plan()
    keyword_rows = _rows(planned, KEYWORD_DATA_TABLE)
    assert len({row["keyword"] for row in keyword_rows}) == GOLDEN_KEYWORD_DATA
    placement_rows = _rows(planned, RANKED_RESULTS_TABLE)
    assert len(placement_rows) == GOLDEN_RANKED_RESULTS
    assert {row["serp_item_type"] for row in placement_rows} == {"organic"}


def test_golden_fifty_seven_unique_urls_repeat_across_distinct_placements() -> None:
    rows = _rows(_golden_plan(), RANKED_RESULTS_TABLE)
    urls = [row["url"] for row in rows]
    assert len(set(urls)) == GOLDEN_UNIQUE_URLS
    assert len(urls) == GOLDEN_RANKED_RESULTS
    # A repeated URL is legitimate: it is content, not identity, so distinct keyword and
    # rank placements never collide on it.
    repeated = [url for url in set(urls) if urls.count(url) > 1]
    assert repeated
    for url in repeated:
        keys = {
            (row["keyword"], row["rank_group"], row["rank_absolute"])
            for row in rows
            if row["url"] == url
        }
        assert len(keys) == urls.count(url)


def test_golden_apex_and_www_remain_exact_distinct_testimony() -> None:
    rows = _rows(_golden_plan(), RANKED_RESULTS_TABLE)
    domains = {row["domain"] for row in rows}
    assert "theconspiratory.com" in domains
    assert "www.theconspiratory.com" in domains
    apex = sum(1 for row in rows if row["domain"] == "theconspiratory.com")
    www = sum(1 for row in rows if row["domain"] == "www.theconspiratory.com")
    assert apex + www == GOLDEN_RANKED_RESULTS
    assert apex and www


def test_golden_duplicate_rank_values_stay_distinct_placements() -> None:
    rows = _rows(_golden_plan(), RANKED_RESULTS_TABLE)
    groups = [row["rank_group"] for row in rows]
    absolutes = [row["rank_absolute"] for row in rows]
    assert len(set(groups)) < len(groups)
    assert len(set(absolutes)) < len(absolutes)
    identities = {
        (row["keyword"], row["serp_item_type"], row["rank_group"], row["rank_absolute"])
        for row in rows
    }
    assert len(identities) == len(rows)


def test_golden_serp_composition_is_not_target_participation() -> None:
    """AI Overview and featured snippets appear in composition, not in the aggregate."""

    items = _fixture_items()
    composition: dict[str, int] = {}
    for row in items:
        for name in row["ranked_serp_element"]["serp_item_types"]:
            composition[name] = composition.get(name, 0) + 1
    assert composition["ai_overview"] > 0
    assert composition["featured_snippet"] > 0

    planned = _golden_plan()
    rows = {
        (row["aggregate_family"], row["rank_system"]): row
        for row in _rows(planned, CORPUS_METRICS_TABLE)
    }
    assert rows[("ai_overview_reference", RANK_SYSTEM_GROUP)]["count"] == 0
    assert rows[("featured_snippet", RANK_SYSTEM_GROUP)]["count"] == 0
    # The composition testimony still survives, unreconciled, on the placement rows.
    placements = _rows(planned, RANKED_RESULTS_TABLE)
    with_aio = [
        row
        for row in placements
        if "ai_overview" in (row["ranked_element_serp_item_types"] or [])
    ]
    assert len(with_aio) == composition["ai_overview"]


def test_golden_two_serp_loci_agree_but_stay_independent_columns() -> None:
    planned = _golden_plan()
    placements = _rows(planned, RANKED_RESULTS_TABLE)
    keyword_serp = _rows(planned, KEYWORD_SERP_TABLE)
    assert len(placements) == GOLDEN_RANKED_RESULTS
    assert len(keyword_serp) == GOLDEN_KEYWORD_DATA
    element_clocks = {row["ranked_element_last_updated_time"] for row in placements}
    keyword_clocks = {row["keyword_serp_last_updated_time"] for row in keyword_serp}
    # Agreement in this Capture is testimony, never reconciliation: the two provider paths
    # keep separate source-local columns and are stored twice.
    assert element_clocks == keyword_clocks
    assert "ranked_element_last_updated_time" not in keyword_serp[0]
    assert "keyword_serp_last_updated_time" not in placements[0]


def test_golden_two_monthly_windows_and_current_newest_disagreement() -> None:
    items = _fixture_items()
    windows = {
        (
            row["keyword_data"]["keyword_info"]["monthly_searches"][0]["year"],
            row["keyword_data"]["keyword_info"]["monthly_searches"][0]["month"],
        )
        for row in items
    }
    assert len(windows) == 2
    disagreeing = [
        row
        for row in items
        if row["keyword_data"]["keyword_info"]["monthly_searches"][0]["search_volume"]
        != row["keyword_data"]["keyword_info"]["search_volume"]
    ]
    assert disagreeing

    planned = _golden_plan()
    monthly = _rows(planned, MONTHLY_TABLE)
    assert len(monthly) == GOLDEN_MONTHLY
    info = {
        row["within_capture_identity"]: row
        for row in _rows(planned, KEYWORD_INFO_TABLE)
    }
    keywords = {
        row["within_capture_identity"]: row["keyword"]
        for row in _rows(planned, KEYWORD_DATA_TABLE)
    }
    by_keyword = {keywords[identity]: row for identity, row in info.items()}
    sample = disagreeing[0]["keyword_data"]
    newest = sample["keyword_info"]["monthly_searches"][0]
    stored_current = by_keyword[sample["keyword"]]["search_volume"]
    stored_newest = [
        row["search_volume"]
        for row in monthly
        if row["keyword"] == sample["keyword"]
        and row["year"] == newest["year"]
        and row["month"] == newest["month"]
    ]
    assert stored_current == sample["keyword_info"]["search_volume"]
    assert stored_newest == [newest["search_volume"]]
    assert stored_current != stored_newest[0]


def test_golden_negative_trends_and_duplicate_categories_survive_exactly() -> None:
    info = _rows(_golden_plan(), KEYWORD_INFO_TABLE)
    assert any(
        row["trend_monthly"] is not None and row["trend_monthly"] < 0 for row in info
    )
    duplicated = [
        row["categories"]
        for row in info
        if row["categories"] and len(row["categories"]) != len(set(row["categories"]))
    ]
    assert duplicated
    fixture_categories = [
        row["keyword_data"]["keyword_info"].get("categories")
        for row in _fixture_items()
    ]
    with_duplicates = [
        value
        for value in fixture_categories
        if value and len(value) != len(set(value))
    ]
    assert len(duplicated) == len(with_duplicates)
    # Order and multiplicity are preserved exactly, never sorted or de-duplicated.
    assert duplicated[0] == with_duplicates[0]


def test_golden_open_vocabularies_are_not_closed_enums() -> None:
    planned = _golden_plan()
    properties = _rows(planned, PROPERTIES_TABLE)
    intent = _rows(planned, INTENT_TABLE)
    languages = {row["detected_language"] for row in properties}
    algorithms = {row["synonym_clustering_algorithm"] for row in properties}
    intents = {row["main_intent"] for row in intent}
    assert len(languages) > 1
    assert len(algorithms) > 1
    assert None in algorithms  # a provider-stated null clustering algorithm
    assert len(intents) > 1
    foreign = {member for row in intent for member in (row["foreign_intent"] or [])}
    assert foreign


def test_golden_rank_info_is_independent_from_backlink_main_domain_rank() -> None:
    planned = _golden_plan()
    placements = _rows(planned, RANKED_RESULTS_TABLE)
    backlinks = _rows(planned, BACKLINKS_TABLE)
    assert all("rank_info_main_domain_rank" in row for row in placements)
    assert all("main_domain_rank" in row for row in backlinks)
    assert {row["rank_info_main_domain_rank"] for row in placements} != {
        row["main_domain_rank"] for row in backlinks
    }


def test_golden_movement_testimony_is_not_observatory_change() -> None:
    planned = _golden_plan()
    placements = _rows(planned, RANKED_RESULTS_TABLE)
    for row in placements:
        assert row["rank_changes_state"] in {"stated", "json_null", "absent"}
        assert "capture_to_capture" not in row
        assert "rank_delta" not in row
        assert "previous_capture_id" not in row
    # `previous_rank_absolute` and the previous clock are provider comparison testimony,
    # kept beside the current values without any derived relation between them.
    assert any(row["ranked_element_previous_updated_time"] for row in placements)


def test_golden_option_one_prose_keeps_state_without_value() -> None:
    rows = _rows(_golden_plan(), RANKED_RESULTS_TABLE)
    for row in rows:
        for column in PROSE_STATE_ONLY:
            assert row[column] in {"stated", "json_null", "absent"}
        for bare in ("breadcrumb", "pre_snippet", "highlighted"):
            assert bare not in row
        # `title` and `description` keep exact typed values; `xpath` is layout testimony.
        assert "title" in row
        assert "description" in row
        assert "xpath" in row
    assert any(row["breadcrumb_state"] == "stated" for row in rows)


def test_golden_unsupported_children_keep_state_only() -> None:
    for row in _rows(_golden_plan(), RANKED_RESULTS_TABLE):
        for column in UNSUPPORTED_CHILD_STATES:
            assert row[column] in {"json_null", "absent"}
            assert column.removesuffix("_state") not in row


def test_golden_item_occurrences_bind_both_semantic_parents() -> None:
    planned = _golden_plan()
    placements = {
        row["within_capture_identity"] for row in _rows(planned, RANKED_RESULTS_TABLE)
    }
    keywords = {
        row["within_capture_identity"] for row in _rows(planned, KEYWORD_DATA_TABLE)
    }
    indexes = [row["item_index"] for row in planned.item_occurrences]
    assert indexes == list(range(GOLDEN_ITEM_OCCURRENCES))
    for row in planned.item_occurrences:
        assert row["ranked_result_identity"] in placements
        assert row["keyword_data_identity"] in keywords
        assert row["ranked_result_kind"] == RANKED_RESULT_KIND
        assert row["keyword_data_kind"] == KEYWORD_DATA_KIND
        assert row["item_se_type"] == "google"


def test_golden_clickstream_loci_are_not_requested_and_bing_is_independent() -> None:
    planned = _golden_plan()
    for row in _rows(planned, KEYWORD_DATA_TABLE):
        assert row["clickstream_normalized_state"] == "not_requested"
        assert row["clickstream_keyword_info_state"] == "not_requested"
        # Bing normalization is not clickstream-controlled and keeps its own state.
        assert row["bing_normalized_state"] in {"json_null", "absent"}
        assert row["bing_normalized_state"] != "not_requested"
    for row in _rows(planned, RANKED_RESULTS_TABLE):
        assert row["clickstream_etv_state"] == "not_requested"


# --------------------------------------------------------------------------------------
# Placement identity, conflict, and occurrence semantics
# --------------------------------------------------------------------------------------


def test_same_keyword_same_url_different_rank_is_two_placements() -> None:
    body = simple_body(
        [
            item("alpha"),
            item(
                "alpha",
                element=ranked_serp_element(
                    serp_item=serp_item(rank_group=4, rank_absolute=4)
                ),
            ),
        ]
    )
    planned = _plan(body)
    assert planned.classification == "observation_admitted"
    rows = _rows(planned, RANKED_RESULTS_TABLE)
    assert len(rows) == 2
    assert {row["url"] for row in rows} == {"https://theconspiratory.com/a"}
    assert {(row["rank_group"], row["rank_absolute"]) for row in rows} == {
        (1, 1),
        (4, 4),
    }
    # One keyword, two placements, two occurrences. A URL-based identity would have
    # falsely rejected this as a conflict.
    assert len(_rows(planned, KEYWORD_DATA_TABLE)) == 1
    assert len(planned.item_occurrences) == 2


def test_identical_duplicate_placement_collapses_and_keeps_both_occurrences() -> None:
    planned = _plan(simple_body([item("alpha"), item("alpha")]))
    assert planned.classification == "observation_admitted"
    assert len(_rows(planned, RANKED_RESULTS_TABLE)) == 1
    assert len(_rows(planned, KEYWORD_DATA_TABLE)) == 1
    assert [row["item_index"] for row in planned.item_occurrences] == [0, 1]
    assert len({row["ranked_result_identity"] for row in planned.item_occurrences}) == 1


def test_same_placement_axes_with_a_different_url_rejects_the_whole_unit() -> None:
    body = simple_body(
        [
            item("alpha"),
            item(
                "alpha",
                element=ranked_serp_element(
                    serp_item=serp_item(url="https://theconspiratory.com/b")
                ),
            ),
        ]
    )
    planned = _plan(body)
    assert planned.classification == "provider_envelope_rejected"
    assert planned.envelopes == ()
    assert planned.context is None
    for table in RANK05_TABLES[:9]:
        assert planned.details[table] == ()
    assert planned.item_occurrences == ()
    assert planned.monthly_occurrences == ()


def test_same_placement_axes_with_a_different_element_detail_rejects() -> None:
    body = simple_body(
        [item("alpha"), item("alpha", element=ranked_serp_element(is_lost=True))]
    )
    assert _plan(body).classification == "provider_envelope_rejected"


def test_open_serp_item_type_is_an_identity_axis() -> None:
    body = simple_body(
        [
            item("alpha"),
            item(
                "alpha",
                element=ranked_serp_element(
                    serp_item=serp_item(type="featured_snippet")
                ),
            ),
        ]
    )
    rows = _rows(_plan(body), RANKED_RESULTS_TABLE)
    assert {row["serp_item_type"] for row in rows} == {"organic", "featured_snippet"}


def test_reorder_changes_occurrence_indexes_not_the_semantic_identity_set() -> None:
    first = item("alpha")
    second = item(
        "beta",
        element=ranked_serp_element(serp_item=serp_item(rank_group=2, rank_absolute=2)),
    )
    forward = _plan(simple_body([first, second]))
    backward = _plan(simple_body([second, first]))
    assert {
        (envelope.observation_kind, envelope.within_capture_identity)
        for envelope in forward.envelopes
    } == {
        (envelope.observation_kind, envelope.within_capture_identity)
        for envelope in backward.envelopes
    }
    forward_map = {
        row["ranked_result_identity"]: row["item_index"]
        for row in forward.item_occurrences
    }
    backward_map = {
        row["ranked_result_identity"]: row["item_index"]
        for row in backward.item_occurrences
    }
    assert forward_map != backward_map
    assert set(forward_map) == set(backward_map)


def test_provider_array_index_is_never_part_of_a_semantic_identity() -> None:
    planned = _plan(simple_body([item("alpha"), item("alpha")]))
    for table in (RANKED_RESULTS_TABLE, KEYWORD_DATA_TABLE, MONTHLY_TABLE):
        for row in _rows(planned, table):
            assert "item_index" not in row
            assert "provider_array_index" not in row


def test_lost_placement_stays_representable_testimony() -> None:
    """A synthetic all-lost row is admissible; `is_lost` is content, not identity."""

    planned = _plan(
        simple_body([item("alpha", element=ranked_serp_element(is_lost=True))])
    )
    assert planned.classification == "observation_admitted"
    row = _rows(planned, RANKED_RESULTS_TABLE)[0]
    assert row["ranked_element_is_lost"] is True
    assert row["ranked_element_is_lost_state"] == "stated"


# --------------------------------------------------------------------------------------
# Keyword-data duplicate reconciliation
# --------------------------------------------------------------------------------------


def test_identical_duplicate_keyword_enrichment_collapses() -> None:
    data = keyword_data("alpha", keyword_info=keyword_info())
    body = simple_body(
        [
            item("alpha", data=copy.deepcopy(data)),
            item(
                "alpha",
                data=copy.deepcopy(data),
                element=ranked_serp_element(
                    serp_item=serp_item(rank_group=2, rank_absolute=2)
                ),
            ),
        ]
    )
    planned = _plan(body)
    assert planned.classification == "observation_admitted"
    assert len(_rows(planned, KEYWORD_DATA_TABLE)) == 1
    assert len(_rows(planned, KEYWORD_INFO_TABLE)) == 1
    assert len(_rows(planned, RANKED_RESULTS_TABLE)) == 2
    assert len(planned.item_occurrences) == 2


def test_conflicting_duplicate_keyword_enrichment_rejects_the_whole_unit() -> None:
    body = simple_body(
        [
            item("alpha", data=keyword_data("alpha", keyword_info=keyword_info())),
            item(
                "alpha",
                data=keyword_data(
                    "alpha", keyword_info=keyword_info(competition_level="HIGH")
                ),
                element=ranked_serp_element(
                    serp_item=serp_item(rank_group=2, rank_absolute=2)
                ),
            ),
        ]
    )
    planned = _plan(body)
    assert planned.classification == "provider_envelope_rejected"
    assert planned.envelopes == ()


def test_differing_monthly_values_alone_do_not_conflict_the_keyword_row() -> None:
    """Monthly values are excluded structurally from the keyword-data comparison."""

    body = simple_body(
        [
            _monthly_item("alpha", [{"year": 2026, "month": 7, "search_volume": 90}]),
            _monthly_item(
                "alpha",
                [{"year": 2026, "month": 6, "search_volume": 80}],
                element=ranked_serp_element(
                    serp_item=serp_item(rank_group=2, rank_absolute=2)
                ),
            ),
        ]
    )
    planned = _plan(body)
    assert planned.classification == "observation_admitted"
    assert len(_rows(planned, KEYWORD_DATA_TABLE)) == 1


def test_monthly_searches_state_disagreement_is_a_same_identity_conflict() -> None:
    """The series state stays inside the compared keyword-info row."""

    body = simple_body(
        [
            item("alpha", data=keyword_data("alpha", keyword_info=keyword_info())),
            item(
                "alpha",
                data=keyword_data(
                    "alpha", keyword_info=keyword_info(monthly_searches=None)
                ),
                element=ranked_serp_element(
                    serp_item=serp_item(rank_group=2, rank_absolute=2)
                ),
            ),
        ]
    )
    assert _plan(body).classification == "provider_envelope_rejected"


def test_keyword_serp_info_is_a_child_and_never_reconciled_with_the_element() -> None:
    """A synthetic disagreement between the two SERP loci stays admissible testimony."""

    data = keyword_data(
        "alpha",
        keyword_info=keyword_info(),
        serp_info={
            "se_type": "google",
            "check_url": "https://www.google.com/search?q=alpha&different=1",
            "serp_item_types": ["organic"],
            "se_results_count": 999,
            "last_updated_time": "2020-01-01 00:00:00 +00:00",
            "previous_updated_time": "2019-01-01 00:00:00 +00:00",
        },
    )
    planned = _plan(simple_body([item("alpha", data=data)]))
    assert planned.classification == "observation_admitted"
    child = _rows(planned, KEYWORD_SERP_TABLE)[0]
    placement = _rows(planned, RANKED_RESULTS_TABLE)[0]
    assert child["check_url"] != placement["ranked_element_check_url"]
    assert child["se_results_count"] != placement["ranked_element_se_results_count"]
    assert (
        child["keyword_serp_last_updated_time"]
        != placement["ranked_element_last_updated_time"]
    )


def test_absent_keyword_children_persist_no_child_rows_but_keep_states() -> None:
    planned = _plan(simple_body([item("alpha", data=keyword_data("alpha"))]))
    assert planned.classification == "observation_admitted"
    parent = _rows(planned, KEYWORD_DATA_TABLE)[0]
    assert parent["keyword_info_state"] == "absent"
    assert parent["keyword_properties_state"] == "absent"
    assert parent["keyword_serp_info_state"] == "absent"
    for table in (
        KEYWORD_INFO_TABLE,
        PROPERTIES_TABLE,
        BACKLINKS_TABLE,
        INTENT_TABLE,
        KEYWORD_SERP_TABLE,
    ):
        assert planned.details[table] == ()


def test_unstated_inline_objects_make_their_members_inapplicable() -> None:
    body = simple_body(
        [
            item(
                "alpha",
                data=keyword_data(
                    "alpha", keyword_info=keyword_info(search_volume_trend=None)
                ),
                element=ranked_serp_element(
                    serp_item=serp_item(rank_changes=None, rank_info=OMIT)
                ),
            )
        ]
    )
    planned = _plan(body)
    assert planned.classification == "observation_admitted"
    placement = _rows(planned, RANKED_RESULTS_TABLE)[0]
    assert placement["rank_changes_state"] == "json_null"
    assert placement["rank_changes_is_new_state"] == "inapplicable"
    assert placement["rank_changes_is_new"] is None
    assert placement["rank_info_state"] == "absent"
    assert placement["rank_info_page_rank_state"] == "inapplicable"
    info = _rows(planned, KEYWORD_INFO_TABLE)[0]
    assert info["search_volume_trend_state"] == "json_null"
    assert info["trend_monthly_state"] == "inapplicable"


# --------------------------------------------------------------------------------------
# Monthly reconciliation
# --------------------------------------------------------------------------------------


def _monthly_item(
    keyword: str, points: list[dict[str, int]], **kwargs: Any
) -> dict[str, Any]:
    return item(
        keyword,
        data=keyword_data(keyword, keyword_info=keyword_info(monthly_searches=points)),
        **kwargs,
    )


def test_equal_overlapping_monthly_periods_collapse_and_keep_occurrences() -> None:
    points = [
        {"year": 2026, "month": 7, "search_volume": 90},
        {"year": 2026, "month": 6, "search_volume": 80},
    ]
    body = simple_body(
        [
            _monthly_item("alpha", copy.deepcopy(points)),
            _monthly_item(
                "alpha",
                copy.deepcopy(points),
                element=ranked_serp_element(
                    serp_item=serp_item(rank_group=2, rank_absolute=2)
                ),
            ),
        ]
    )
    planned = _plan(body)
    assert planned.classification == "observation_admitted"
    assert len(_rows(planned, MONTHLY_TABLE)) == 2
    # Both periods collapse; every returned-item occurrence survives.
    assert len(planned.monthly_occurrences) == 4
    assert sorted(row["item_index"] for row in planned.monthly_occurrences) == [
        0,
        0,
        1,
        1,
    ]


def test_conflicting_overlapping_monthly_values_reject_the_whole_unit() -> None:
    body = simple_body(
        [
            _monthly_item("alpha", [{"year": 2026, "month": 7, "search_volume": 90}]),
            _monthly_item(
                "alpha",
                [{"year": 2026, "month": 7, "search_volume": 91}],
                element=ranked_serp_element(
                    serp_item=serp_item(rank_group=2, rank_absolute=2)
                ),
            ),
        ]
    )
    planned = _plan(body)
    assert planned.classification == "provider_envelope_rejected"
    assert planned.envelopes == ()


def test_non_overlapping_monthly_windows_union() -> None:
    body = simple_body(
        [
            _monthly_item("alpha", [{"year": 2026, "month": 7, "search_volume": 90}]),
            _monthly_item(
                "alpha",
                [{"year": 2026, "month": 6, "search_volume": 80}],
                element=ranked_serp_element(
                    serp_item=serp_item(rank_group=2, rank_absolute=2)
                ),
            ),
        ]
    )
    planned = _plan(body)
    assert planned.classification == "observation_admitted"
    rows = _rows(planned, MONTHLY_TABLE)
    assert {(row["year"], row["month"], row["search_volume"]) for row in rows} == {
        (2026, 7, 90),
        (2026, 6, 80),
    }
    assert len(planned.monthly_occurrences) == 2


def test_monthly_array_position_is_occurrence_not_identity() -> None:
    forward = _plan(
        simple_body(
            [
                _monthly_item(
                    "alpha",
                    [
                        {"year": 2026, "month": 7, "search_volume": 90},
                        {"year": 2026, "month": 6, "search_volume": 80},
                    ],
                )
            ]
        )
    )
    backward = _plan(
        simple_body(
            [
                _monthly_item(
                    "alpha",
                    [
                        {"year": 2026, "month": 6, "search_volume": 80},
                        {"year": 2026, "month": 7, "search_volume": 90},
                    ],
                )
            ]
        )
    )
    assert {
        envelope.within_capture_identity
        for envelope in forward.envelopes
        if envelope.observation_kind == MONTHLY_KIND
    } == {
        envelope.within_capture_identity
        for envelope in backward.envelopes
        if envelope.observation_kind == MONTHLY_KIND
    }


def test_current_search_volume_is_never_derived_from_the_newest_month() -> None:
    planned = _plan(
        simple_body(
            [_monthly_item("alpha", [{"year": 2026, "month": 7, "search_volume": 90}])]
        )
    )
    assert _rows(planned, KEYWORD_INFO_TABLE)[0]["search_volume"] == 100
    assert _rows(planned, MONTHLY_TABLE)[0]["search_volume"] == 90


def test_monthly_period_is_a_data_period_not_a_clock() -> None:
    planned = _plan(
        simple_body(
            [_monthly_item("alpha", [{"year": 2026, "month": 7, "search_volume": 90}])]
        )
    )
    row = _rows(planned, MONTHLY_TABLE)[0]
    assert row["year"] == 2026
    assert row["month"] == 7
    for column in row:
        assert "updated_time" not in column
        assert "captured" not in column


# --------------------------------------------------------------------------------------
# Item reachability and admission
# --------------------------------------------------------------------------------------


def test_json_null_keyword_data_rejects_the_whole_unit() -> None:
    row = item("alpha")
    row["keyword_data"] = None
    planned = _plan(simple_body([row]))
    assert planned.classification == "provider_envelope_rejected"
    # The corpus metrics are not retained while the malformed returned row is dropped.
    assert planned.details[CORPUS_METRICS_TABLE] == ()
    assert planned.envelopes == ()


def test_json_null_ranked_serp_element_rejects_the_whole_unit() -> None:
    row = item("alpha")
    row["ranked_serp_element"] = None
    planned = _plan(simple_body([row]))
    assert planned.classification == "provider_envelope_rejected"
    assert planned.details[CORPUS_METRICS_TABLE] == ()
    assert planned.envelopes == ()


def test_missing_item_member_stays_a_parser_failure_not_a_recipe_state() -> None:
    for member in ("keyword_data", "ranked_serp_element", "se_type"):
        row = item("alpha")
        del row[member]
        # RANK-04 requires the member name, so the body never reaches a Recipe ABSENT
        # branch: the parser refuses it and the whole unit is rejected.
        assert _plan(simple_body([row])).classification == (
            "provider_envelope_rejected"
        )


def test_item_se_type_must_be_google() -> None:
    assert _plan(simple_body([item("alpha", se_type="bing")])).classification == (
        "provider_envelope_rejected"
    )


def test_zero_item_success_still_emits_ten_corpus_observations() -> None:
    planned = _plan(simple_body([], total_count=0))
    assert planned.classification == "observation_admitted"
    assert planned.classification != "observation_admitted_empty"
    assert len(planned.envelopes) == 10
    assert len(_rows(planned, CORPUS_METRICS_TABLE)) == 10
    assert planned.details[RANKED_RESULTS_TABLE] == ()
    assert planned.details[KEYWORD_DATA_TABLE] == ()
    assert planned.details[MONTHLY_TABLE] == ()
    assert planned.item_occurrences == ()
    assert planned.monthly_occurrences == ()
    assert planned.context is not None
    assert planned.context["items_count"] == 0


def test_zero_item_success_with_a_nonzero_corpus_is_not_a_completeness_claim() -> None:
    planned = _plan(
        simple_body(
            [],
            total_count=248,
            metrics=all_metrics(organic=metrics_family(count=248, pos_1=248)),
        )
    )
    assert planned.classification == "observation_admitted"
    assert planned.context is not None
    assert planned.context["total_count"] == 248
    assert planned.context["items_count"] == 0
    organic = [
        row
        for row in _rows(planned, CORPUS_METRICS_TABLE)
        if row["aggregate_family"] == "organic"
        and row["rank_system"] == RANK_SYSTEM_GROUP
    ]
    assert organic[0]["count"] == 248


# --------------------------------------------------------------------------------------
# Capture classification boundaries
# --------------------------------------------------------------------------------------


def test_transport_classifications() -> None:
    assert _plan(
        None, capture={"transport_state": "no_response"}
    ).classification == "no_response"
    assert _plan(
        b"{}", capture={"transport_state": "response_partial"}
    ).classification == "response_partial"
    assert _plan(
        b"{}",
        capture={
            "transport_state": "response_complete",
            "response": {"completeness": "truncated"},
        },
    ).classification == "transport_complete_non_admissible"
    assert _plan(b"").classification == "transport_complete_non_admissible"


def test_provider_error_becomes_a_repository_provider_error() -> None:
    planned = _plan(synthetic_body(None, status_code=40501, status_message="Nope."))
    assert planned.classification == "provider_error"
    assert planned.envelopes == ()
    assert planned.context is None


def test_body_drift_becomes_provider_envelope_rejected() -> None:
    assert _plan(b"not json").classification == "provider_envelope_rejected"
    document = json.loads(simple_body([item("alpha")]))
    document["tasks"][0]["result"][0]["surprise"] = 1
    assert _plan(
        json.dumps(document).encode("utf-8")
    ).classification == "provider_envelope_rejected"


def test_attempt_path_parser_failure_is_an_integrity_failure() -> None:
    parameters = dict(_params())
    parameters["limit"] = 50
    assert _plan(simple_body([item("alpha")]), parameters=parameters) is None


def test_result_echo_disagreement_stays_typed_testimony() -> None:
    planned = _plan(simple_body([item("alpha")], target="other-domain.com"))
    assert planned.classification == "observation_admitted"
    assert planned.context is not None
    # The Attempt remains request authority; the result restatement is stored beside it.
    assert planned.context["requested_target"] == TARGET
    assert planned.context["result_target"] == "other-domain.com"


# --------------------------------------------------------------------------------------
# String / JCS / PostgreSQL safety
# --------------------------------------------------------------------------------------


def test_require_text_matches_the_canonical_ijson_boundary() -> None:
    for hostile in (LONE_SURROGATE, NONCHARACTER_FDD0, NONCHARACTER_FFFF,
                    NONCHARACTER_FFFE):
        with pytest.raises(DocumentError):
            canonical_json({"k": hostile})
        with pytest.raises(SemanticDisagreement):
            _require_text(hostile)
    # U+0000 is accepted by canonical JSON but cannot reach PostgreSQL TEXT, so this
    # boundary is deliberately the wider of the two for that one code point.
    canonical_json({"k": NUL})
    with pytest.raises(SemanticDisagreement):
        _require_text(NUL)
    assert _require_text("ordinary text") == "ordinary text"


@pytest.mark.parametrize("hostile", list(HOSTILE_TEXT))
def test_hostile_identity_keyword_rejects_cleanly(hostile: str) -> None:
    planned = _plan(simple_body([item(f"alpha{hostile}")]))
    assert planned.classification == "provider_envelope_rejected"


def test_empty_identity_strings_reject_cleanly() -> None:
    assert _plan(simple_body([item("")])).classification == (
        "provider_envelope_rejected"
    )
    body = simple_body(
        [item("alpha", element=ranked_serp_element(serp_item=serp_item(type="")))]
    )
    assert _plan(body).classification == "provider_envelope_rejected"


def test_permitted_empty_non_identity_testimony_stays_admissible() -> None:
    body = simple_body(
        [
            item(
                "alpha",
                element=ranked_serp_element(
                    serp_item=serp_item(title="", website_name="", description="")
                ),
            )
        ]
    )
    planned = _plan(body)
    assert planned.classification == "observation_admitted"
    row = _rows(planned, RANKED_RESULTS_TABLE)[0]
    assert row["title"] == ""
    assert row["title_state"] == "stated"
    assert row["website_name"] == ""


def test_hostile_persisted_url_and_array_members_reject_cleanly() -> None:
    hostile_url = _plan(
        simple_body(
            [
                item(
                    "alpha",
                    element=ranked_serp_element(
                        serp_item=serp_item(url=f"https://a.test/{LONE_SURROGATE}")
                    ),
                )
            ]
        )
    )
    assert hostile_url.classification == "provider_envelope_rejected"
    hostile_array = _plan(
        simple_body(
            [
                item(
                    "alpha",
                    element=ranked_serp_element(
                        serp_item_types=["organic", LONE_SURROGATE]
                    ),
                )
            ]
        )
    )
    assert hostile_array.classification == "provider_envelope_rejected"
    hostile_intent = _plan(
        simple_body(
            [
                item(
                    "alpha",
                    data=keyword_data(
                        "alpha",
                        search_intent_info={
                            "se_type": "google",
                            "main_intent": "informational",
                            "foreign_intent": [NONCHARACTER_FDD0],
                            "last_updated_time": CLOCK,
                        },
                    ),
                )
            ]
        )
    )
    assert hostile_intent.classification == "provider_envelope_rejected"


def test_product_held_prose_values_never_cross_the_persistence_boundary() -> None:
    """Option 1 keeps the state without reading the value, so hostile prose is inert."""

    planned = _plan(
        simple_body(
            [
                item(
                    "alpha",
                    element=ranked_serp_element(
                        serp_item=serp_item(
                            breadcrumb=LONE_SURROGATE,
                            highlighted=[NONCHARACTER_FDD0],
                        )
                    ),
                )
            ]
        )
    )
    assert planned.classification == "observation_admitted"
    row = _rows(planned, RANKED_RESULTS_TABLE)[0]
    assert row["breadcrumb_state"] == "stated"
    assert row["highlighted_state"] == "stated"
    assert "breadcrumb" not in row
    assert "highlighted" not in row


# --------------------------------------------------------------------------------------
# PostgreSQL derivation and complete-set proofs
# --------------------------------------------------------------------------------------


def test_derive_writes_outcomes_envelopes_and_context(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, _store, attempt_id, capture_id = derived
    outcomes = connection.execute(
        """
        SELECT attempt_id, capture_id, classification, observation_count
        FROM outcomes
        WHERE derivation_version_id = %s
        ORDER BY capture_id NULLS FIRST
        """,
        (RANKED_KEYWORDS_RECIPE_ID,),
    ).fetchall()
    assert outcomes[0] == (attempt_id, None, "authorized_unresolved", 0)
    assert outcomes[1][0] == attempt_id
    assert outcomes[1][1] == capture_id
    assert outcomes[1][2] == "observation_admitted"
    assert int(outcomes[1][3]) == _count(connection, "observation_envelopes")
    counts = _all_rank05_counts(connection)
    assert counts[CORPUS_METRICS_TABLE] == 10
    assert counts[RANKED_RESULTS_TABLE] == 2
    assert counts[KEYWORD_DATA_TABLE] == 2
    assert counts[ITEM_OCCURRENCES_TABLE] == 2
    assert counts[CONTEXT_TABLE] == 1


def test_derive_is_idempotent_for_the_same_evidence(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, store, _attempt_id, _capture_id = derived
    before = _all_rank05_counts(connection)
    snapshot = {table: _fetch_relation(connection, table) for table in RANK05_TABLES}
    derive_google_ranked_keywords(store, connection)
    connection.commit()
    assert _all_rank05_counts(connection) == before
    assert {
        table: _fetch_relation(connection, table) for table in RANK05_TABLES
    } == snapshot


def test_stored_outcome_count_equals_envelope_cardinality(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, _store, _attempt_id, capture_id = derived
    stored = connection.execute(
        """
        SELECT observation_count FROM outcomes
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    ).fetchone()
    envelopes = connection.execute(
        """
        SELECT count(*) FROM observation_envelopes
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    ).fetchone()
    assert int(stored[0]) == int(envelopes[0])


def test_missing_rebuildable_rows_restore_to_exactly_the_intended_set(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, store, _attempt_id, capture_id = derived
    snapshot = {table: _fetch_relation(connection, table) for table in RANK05_TABLES}
    for table in (MONTHLY_OCCURRENCES_TABLE, KEYWORD_INFO_TABLE, CONTEXT_TABLE):
        connection.execute(
            sql.SQL("DELETE FROM {} WHERE capture_id = %s").format(
                sql.Identifier(table)
            ),
            (capture_id,),
        )
    connection.commit()
    derive_google_ranked_keywords(store, connection)
    connection.commit()
    assert {
        table: _fetch_relation(connection, table) for table in RANK05_TABLES
    } == snapshot


def test_planted_extra_semantic_envelope_fails_the_complete_set(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, store, attempt_id, capture_id = derived
    connection.execute(
        """
        INSERT INTO observation_envelopes (
            capture_id, attempt_id, derivation_version_id, provider,
            adapter_contract, observation_kind, within_capture_identity
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            capture_id,
            attempt_id,
            RANKED_KEYWORDS_RECIPE_ID,
            PROVIDER,
            RANKED_KEYWORDS_ADAPTER_CONTRACT,
            MONTHLY_KIND,
            "c" * 64,
        ),
    )
    connection.commit()
    with pytest.raises(DerivationError, match="complete-set mismatch"):
        derive_google_ranked_keywords(store, connection)
    connection.rollback()


def test_planted_extra_semantic_detail_fails_the_complete_set(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, store, attempt_id, capture_id = derived
    planted = "e" * 64
    connection.execute(
        """
        INSERT INTO observation_envelopes (
            capture_id, attempt_id, derivation_version_id, provider,
            adapter_contract, observation_kind, within_capture_identity
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            capture_id,
            attempt_id,
            RANKED_KEYWORDS_RECIPE_ID,
            PROVIDER,
            RANKED_KEYWORDS_ADAPTER_CONTRACT,
            MONTHLY_KIND,
            planted,
        ),
    )
    connection.execute(
        sql.SQL(
            """
            INSERT INTO {} (
                capture_id, derivation_version_id, within_capture_identity,
                observation_kind, requested_target, keyword, year, month,
                search_volume
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        ).format(sql.Identifier(MONTHLY_TABLE)),
        (
            capture_id,
            RANKED_KEYWORDS_RECIPE_ID,
            planted,
            MONTHLY_KIND,
            TARGET,
            "planted",
            2026,
            1,
            5,
        ),
    )
    connection.commit()
    with pytest.raises(DerivationError, match="complete-set mismatch"):
        derive_google_ranked_keywords(store, connection)
    connection.rollback()


def test_planted_extra_item_occurrence_fails_the_complete_set(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, store, _attempt_id, capture_id = derived
    row = connection.execute(
        sql.SQL(
            """
            SELECT ranked_result_identity, keyword_data_identity, item_se_type
            FROM {} LIMIT 1
            """
        ).format(sql.Identifier(ITEM_OCCURRENCES_TABLE))
    ).fetchone()
    assert row is not None
    connection.execute(
        sql.SQL(
            """
            INSERT INTO {} (
                capture_id, derivation_version_id, item_index,
                ranked_result_identity, ranked_result_kind,
                keyword_data_identity, keyword_data_kind, item_se_type
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
        ).format(sql.Identifier(ITEM_OCCURRENCES_TABLE)),
        (
            capture_id,
            RANKED_KEYWORDS_RECIPE_ID,
            9999,
            row[0],
            RANKED_RESULT_KIND,
            row[1],
            KEYWORD_DATA_KIND,
            row[2],
        ),
    )
    connection.commit()
    with pytest.raises(DerivationError, match="complete-set mismatch"):
        derive_google_ranked_keywords(store, connection)
    connection.rollback()


def test_planted_extra_monthly_occurrence_fails_the_complete_set(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, store, _attempt_id, capture_id = derived
    row = connection.execute(
        sql.SQL("SELECT within_capture_identity FROM {} LIMIT 1").format(
            sql.Identifier(MONTHLY_OCCURRENCES_TABLE)
        )
    ).fetchone()
    assert row is not None
    connection.execute(
        sql.SQL(
            """
            INSERT INTO {} (
                capture_id, derivation_version_id, within_capture_identity,
                observation_kind, item_index
            ) VALUES (%s, %s, %s, %s, %s)
            """
        ).format(sql.Identifier(MONTHLY_OCCURRENCES_TABLE)),
        (capture_id, RANKED_KEYWORDS_RECIPE_ID, row[0], MONTHLY_KIND, 4242),
    )
    connection.commit()
    with pytest.raises(DerivationError, match="complete-set mismatch"):
        derive_google_ranked_keywords(store, connection)
    connection.rollback()


def test_conflicting_stored_detail_content_fails(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, store, _attempt_id, capture_id = derived
    connection.execute(
        sql.SQL("UPDATE {} SET url = %s WHERE capture_id = %s").format(
            sql.Identifier(RANKED_RESULTS_TABLE)
        ),
        ("https://tampered.test/x", capture_id),
    )
    connection.commit()
    with pytest.raises(DerivationError, match="conflicting"):
        derive_google_ranked_keywords(store, connection)
    connection.rollback()


def test_conflicting_stored_context_content_fails(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, store, _attempt_id, capture_id = derived
    connection.execute(
        sql.SQL("UPDATE {} SET total_count = %s WHERE capture_id = %s").format(
            sql.Identifier(CONTEXT_TABLE)
        ),
        (999, capture_id),
    )
    connection.commit()
    with pytest.raises(DerivationError, match="conflicting"):
        derive_google_ranked_keywords(store, connection)
    connection.rollback()


def test_conflicting_stored_outcome_fails(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, store, _attempt_id, capture_id = derived
    connection.execute(
        """
        UPDATE outcomes SET classification = 'provider_error'
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    )
    connection.commit()
    with pytest.raises(DerivationError, match="conflicting provider outcome"):
        derive_google_ranked_keywords(store, connection)
    connection.rollback()


def test_rejected_unit_leaves_no_partial_rows_and_no_planted_context(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "rejected")
    body = simple_body(
        [
            item("alpha"),
            item(
                "alpha",
                element=ranked_serp_element(
                    serp_item=serp_item(url="https://theconspiratory.com/b")
                ),
            ),
        ]
    )
    attempt_id, capture_id = _commit(store, body, "22" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_ranked_keywords(store, connection)
        connection.commit()
        assert connection.execute(
            """
            SELECT classification, observation_count FROM outcomes
            WHERE derivation_version_id = %s AND capture_id = %s
            """,
            (RANKED_KEYWORDS_RECIPE_ID, capture_id),
        ).fetchone() == ("provider_envelope_rejected", 0)
        for table in RANK05_TABLES:
            assert _count(connection, table) == 0
        assert _count(connection, "observation_envelopes") == 0

        # A context row planted onto a rejected unit is an extra the complete set refuses.
        connection.execute(
            sql.SQL(
                """
                INSERT INTO {} (
                    capture_id, derivation_version_id, attempt_id, requested_target,
                    request_location_code, request_language_code, request_item_types,
                    request_ignore_synonyms, request_include_clickstream_data,
                    request_limit, request_offset, request_load_rank_absolute,
                    request_historical_serp_mode, request_order_by,
                    result_target_state, result_location_code_state,
                    result_language_code_state, result_se_type_state,
                    total_count, items_count
                ) VALUES (
                    %s, %s, %s, %s, 2840, 'en', %s, false, false, 100, 0, true,
                    'all', %s, 'absent', 'absent', 'absent', 'absent', 0, 0
                )
                """
            ).format(sql.Identifier(CONTEXT_TABLE)),
            (
                capture_id,
                RANKED_KEYWORDS_RECIPE_ID,
                attempt_id,
                TARGET,
                list(REQUESTED_ITEM_TYPES),
                ["ranked_serp_element.serp_item.rank_group,asc"],
            ),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch: context"):
            derive_google_ranked_keywords(store, connection)
        connection.rollback()


def test_unrelated_attempt_never_influences_a_capture_citing_another(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "isolation")
    # An unrelated but perfectly valid Ranked Attempt for a different target.
    other = _attempt("33" * 32, "example.com")
    store.commit_attempt(
        other, request_body=ranked_keywords_request_body_bytes(_params("example.com"))
    )
    attempt_id, capture_id = _commit(
        store, simple_body([item("alpha")]), "44" * 32, suffix="2"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_google_ranked_keywords(store, connection)
        connection.commit()
        assert summary.integrity_failures == 0
        assert summary.attempt_outcomes == 2
        assert summary.capture_outcomes == 1
        assert connection.execute(
            sql.SQL(
                "SELECT attempt_id, requested_target FROM {} WHERE capture_id = %s"
            ).format(sql.Identifier(CONTEXT_TABLE)),
            (capture_id,),
        ).fetchone() == (attempt_id, TARGET)


def test_no_rank05_relation_has_a_universal_provider_clock_column(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, _store, _attempt_id, _capture_id = derived
    assert connection.execute(
        """
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = ANY(%s)
          AND column_name IN ('provider_update_time', 'last_updated')
        """,
        (list(RANK05_TABLES),),
    ).fetchall() == []


def test_four_time_pillars_are_separate_columns_in_postgresql(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, _store, _attempt_id, _capture_id = derived
    clocks = {
        (str(row[0]), str(row[1]))
        for row in connection.execute(
            """
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = ANY(%s)
              AND column_name LIKE '%%updated_time'
            """,
            (list(RANK05_TABLES),),
        ).fetchall()
    }
    names = {column for _table, column in clocks}
    assert names == set(SOURCE_LOCAL_CLOCKS)
    # Pillar 2 is a Data Period, not a clock: the monthly relation carries none.
    assert not [table for table, _column in clocks if table == MONTHLY_TABLE]


def test_child_rows_require_their_exact_keyword_parent(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, _store, _attempt_id, capture_id = derived
    with pytest.raises(ForeignKeyViolation):
        connection.execute(
            sql.SQL(
                """
                INSERT INTO {} (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, se_type_state, core_keyword_state,
                    synonym_clustering_algorithm_state, keyword_difficulty_state,
                    detected_language_state, is_another_language_state
                ) VALUES (%s, %s, %s, %s, 'absent', 'absent', 'absent', 'absent',
                          'absent', 'absent')
                """
            ).format(sql.Identifier(PROPERTIES_TABLE)),
            (capture_id, RANKED_KEYWORDS_RECIPE_ID, "d" * 64, KEYWORD_DATA_KIND),
        )
    connection.rollback()


def test_item_occurrence_requires_both_semantic_parents(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, _store, _attempt_id, capture_id = derived
    row = connection.execute(
        sql.SQL("SELECT keyword_data_identity FROM {} LIMIT 1").format(
            sql.Identifier(ITEM_OCCURRENCES_TABLE)
        )
    ).fetchone()
    assert row is not None
    with pytest.raises(ForeignKeyViolation):
        connection.execute(
            sql.SQL(
                """
                INSERT INTO {} (
                    capture_id, derivation_version_id, item_index,
                    ranked_result_identity, ranked_result_kind,
                    keyword_data_identity, keyword_data_kind, item_se_type
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'google')
                """
            ).format(sql.Identifier(ITEM_OCCURRENCES_TABLE)),
            (
                capture_id,
                RANKED_KEYWORDS_RECIPE_ID,
                7777,
                "f" * 64,
                RANKED_RESULT_KIND,
                row[0],
                KEYWORD_DATA_KIND,
            ),
        )
    connection.rollback()


def test_corpus_absolute_locus_check_forbids_a_synthesized_count(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, _store, _attempt_id, capture_id = derived
    with pytest.raises(CheckViolation):
        connection.execute(
            sql.SQL(
                """
                UPDATE {} SET count = 5, count_state = 'stated'
                WHERE capture_id = %s AND rank_system = 'rank_absolute'
                """
            ).format(sql.Identifier(CORPUS_METRICS_TABLE)),
            (capture_id,),
        )
    connection.rollback()


# --------------------------------------------------------------------------------------
# Frozen-fixture PostgreSQL golden and two-database rebuild
# --------------------------------------------------------------------------------------


def test_frozen_fixture_derives_the_golden_set_and_rebuilds_equivalently(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "golden")
    _attempt_id, capture_id = _commit(store, _fixture_body(), "55" * 32)
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)
    with connect(postgres_dsn) as first:
        summary = derive_google_ranked_keywords(store, first)
        first.commit()
        assert summary.integrity_failures == 0
        assert summary.observations == GOLDEN_ENVELOPES
        assert first.execute(
            """
            SELECT classification, observation_count FROM outcomes
            WHERE derivation_version_id = %s AND capture_id = %s
            """,
            (RANKED_KEYWORDS_RECIPE_ID, capture_id),
        ).fetchone() == ("observation_admitted", GOLDEN_ENVELOPES)
        counts = _all_rank05_counts(first)
        assert counts[CORPUS_METRICS_TABLE] == GOLDEN_CORPUS_METRICS
        assert counts[RANKED_RESULTS_TABLE] == GOLDEN_RANKED_RESULTS
        assert counts[KEYWORD_DATA_TABLE] == GOLDEN_KEYWORD_DATA
        assert counts[MONTHLY_TABLE] == GOLDEN_MONTHLY
        assert counts[ITEM_OCCURRENCES_TABLE] == GOLDEN_ITEM_OCCURRENCES
        assert counts[MONTHLY_OCCURRENCES_TABLE] == GOLDEN_MONTHLY_OCCURRENCES
        assert counts[CONTEXT_TABLE] == 1
        assert _count(first, "observation_envelopes") == GOLDEN_ENVELOPES
        first_snapshot = {
            table: _fetch_relation(first, table) for table in RANK05_TABLES
        }
    with connect(postgres_second_dsn) as second:
        derive_google_ranked_keywords(store, second)
        second.commit()
        second_snapshot = {
            table: _fetch_relation(second, table) for table in RANK05_TABLES
        }
    # Two fresh databases rebuilt from the same Evidence and Recipe are logically
    # equivalent across every RANK-05 relation.
    assert first_snapshot == second_snapshot


def test_frozen_fixture_decimal_values_survive_exactly(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "decimal")
    _commit(store, _fixture_body(), "66" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_ranked_keywords(store, connection)
        connection.commit()
        etv = connection.execute(
            sql.SQL(
                """
                SELECT etv FROM {}
                WHERE aggregate_family = 'organic' AND rank_system = 'rank_group'
                """
            ).format(sql.Identifier(CORPUS_METRICS_TABLE))
        ).fetchone()
        assert etv is not None
        assert isinstance(etv[0], Decimal)
        expected = Decimal(
            str(_fixture_document()["tasks"][0]["result"][0]["metrics"]["organic"]["etv"])
        )
        assert etv[0] == expected


def test_populated_pre_rank05_schema_then_ranked_keywords_derive(
    tmp_path: Path, postgres_dsn: str
) -> None:
    joined = "\n".join(PRE_RANK05_SCHEMA_STATEMENTS)
    assert "related_keywords_result_context" in joined
    assert "llm_mentions_historical_result_context" in joined
    assert "ranked_keywords_" not in joined
    with connect(postgres_dsn) as connection:
        for statement in PRE_RANK05_SCHEMA_STATEMENTS:
            connection.execute(statement)
        connection.commit()
    apply_migrations(postgres_dsn)
    store = create_store(tmp_path / "upgraded")
    _commit(store, simple_body([item("alpha")]), "77" * 32)
    with connect(postgres_dsn) as connection:
        summary = derive_google_ranked_keywords(store, connection)
        connection.commit()
        assert summary.integrity_failures == 0
        assert summary.observations == 12
        assert _count(connection, CORPUS_METRICS_TABLE) == 10
        assert _count(connection, RANKED_RESULTS_TABLE) == 1
        assert _count(connection, KEYWORD_DATA_TABLE) == 1
