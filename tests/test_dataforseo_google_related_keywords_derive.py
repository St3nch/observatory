"""RK-04: Related Keywords provider Derivation into real PostgreSQL."""

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
    RELATED_KEYWORDS_ADAPTER_CONTRACT,
    DocumentError,
    body_ref,
    canonical_json,
    related_keywords_http_attempt_document,
    related_keywords_http_capture_document,
)
from observatory.dataforseo_google_related_keywords import (
    KEYWORD_DATA_KIND,
    LOCUS_ITEM,
    LOCUS_SEED,
    MONTHLY_KIND,
    PARSER_CONTRACT,
    PROVIDER,
    RELATED_KEYWORDS_RECIPE,
    RELATED_KEYWORDS_RECIPE_BYTES,
    RELATED_KEYWORDS_RECIPE_ID,
    RELATIONSHIP_KIND,
    related_keywords_recipe,
)
from observatory.dataforseo_google_related_keywords_paid_probe import (
    closed_related_keywords_parameters,
    related_keywords_request_body_bytes,
)
from observatory.dataforseo_keyword_overview import CORE_RECIPE_ID
from observatory.derive import DerivationError
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
    SemanticDisagreement,
    _require_text,
    derive_google_related_keywords,
    plan_related_keywords_capture,
)
from observatory.migrate import (
    PRE_AI16_SCHEMA_STATEMENTS,
    PRE_RK04_SCHEMA_STATEMENTS,
    RELATED_KEYWORDS_KEYWORD_DATA_KIND,
    RELATED_KEYWORDS_MONTHLY_KIND,
    RELATED_KEYWORDS_RELATIONSHIP_KIND,
    RK04_SCHEMA_STATEMENTS,
    SCHEMA_STATEMENTS,
    apply_migrations,
    connect,
)
from observatory.provider_recipe import (
    IDENTITY_SCHEMA,
    IDENTITY_VERSION,
    observation_identity,
    recipe_bytes,
    recipe_derivation_version_id,
)

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_google_related_keywords_rk02.json"
)
SEED = "conspiracy theories"
FIXTURE_BYTES = 177120
FIXTURE_SHA256 = "e128f2f81d51479237f1bd7e51feee3dfffcae4596558ebff67365f03cd1decb"

# Frozen-Capture consequences of the accepted model. These are fixture facts, never provider
# invariants, and never production constants.
GOLDEN_KEYWORD_DATA = 81
GOLDEN_MONTHLY = 972
GOLDEN_RELATIONSHIP = 477
GOLDEN_ENVELOPES = 1530
GOLDEN_ITEM_OCCURRENCES = 80
GOLDEN_MONTHLY_OCCURRENCES = 960
GOLDEN_RELATIONSHIP_OCCURRENCES = 477

FRONTIER_TARGET = "conspiracy theories podcast - youtube"
FRONTIER_SOURCE = "conspiracy theories podcast"
DUPLICATE_CATEGORY_KEYWORD = "funny conspiracy theories"
DUPLICATE_CATEGORIES = [10013, 10013, 10106, 13566]
HOLLOW_SERP_KEYWORDS = (
    "conspiracy theories in science",
    "conspiracy theories meaning in hindi",
)
YEAR_ONE_CLOCK = "0001-01-01 00:00:00 +00:00"
DEPTH_ZERO_CLOCKS = {
    "keyword_info_last_updated_time": "2026-08-28 16:54:38 +00:00",
    "avg_backlinks_last_updated_time": "2026-05-14 19:04:51 +00:00",
    "search_intent_last_updated_time": "2026-04-29 12:24:14 +00:00",
    "serp_last_updated_time": "2026-05-14 19:04:49 +00:00",
    "serp_previous_updated_time": "2026-03-28 15:59:07 +00:00",
}


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


def _params(keyword: str = SEED) -> dict[str, object]:
    return closed_related_keywords_parameters(keyword=keyword)


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
    return plan_related_keywords_capture(
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


# --------------------------------------------------------------------------------------
# Synthetic body builders. Most adversarial proofs use these rather than the 80-item
# fixture, so the PostgreSQL loop stays bounded.
# --------------------------------------------------------------------------------------


def keyword_data(keyword: str, **overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {"keyword": keyword}
    data.update(overrides)
    return data


OMIT = object()


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
        "time": "0.1 sec.",
        "cost": 0.0216,
        "tasks_count": 1,
        "tasks_error": 0 if status_code == 20000 else 1,
        "tasks": [
            {
                "id": "task-1",
                "status_code": status_code,
                "status_message": status_message,
                "time": "0.1 sec.",
                "cost": 0.0216,
                "result_count": len(results) if result_count is None else result_count,
                "path": [
                    "v3",
                    "dataforseo_labs",
                    "google",
                    "related_keywords",
                    "live",
                ],
                "data": {
                    "api": "dataforseo_labs",
                    "function": "related_keywords",
                    "se_type": "google",
                },
                "result": results,
            }
        ],
    }
    if status_code != 20000:
        del document["tasks"][0]["result"]
        document["tasks"][0]["result"] = None
    # ensure_ascii keeps a deliberately hostile lone surrogate expressible as a \uXXXX
    # escape, which is exactly how a provider could deliver one.
    return json.dumps(document, ensure_ascii=True).encode("utf-8")


def simple_body(items: list[dict[str, Any]], **kwargs: Any) -> bytes:
    return synthetic_body(result_document(items, **kwargs))


# --------------------------------------------------------------------------------------
# Evidence helpers
# --------------------------------------------------------------------------------------


def _attempt(nonce: str, keyword: str = SEED) -> dict[str, object]:
    return related_keywords_http_attempt_document(
        parameters=_params(keyword),
        attempt_nonce=nonce,
        authorized_at="2026-08-31T10:00:00.000000Z",
        observatory_version="rk04-test-v1",
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
    return related_keywords_http_capture_document(
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
    body: bytes,
    nonce: str,
    *,
    keyword: str = SEED,
    suffix: str = "1",
) -> tuple[str, str]:
    attempt = _attempt(nonce, keyword)
    attempt_id = store.commit_attempt(
        attempt, request_body=related_keywords_request_body_bytes(_params(keyword))
    )
    capture_id = store.commit_capture(
        _capture_document(attempt, body, suffix=suffix), response_body=body
    )
    return attempt_id, capture_id


@pytest.fixture
def derived(
    tmp_path: Path, postgres_dsn: str
) -> Iterator[tuple[Any, EvidenceStore, str, str]]:
    """One committed synthetic Capture derived into a migrated database."""

    store = create_store(tmp_path / "rk04")
    body = simple_body(
        [
            item("alpha", data=keyword_data("alpha", keyword_info=keyword_info())),
            item("beta", related=["alpha", "gamma"]),
        ]
    )
    attempt_id, capture_id = _commit(store, body, "11" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_related_keywords(store, connection)
        connection.commit()
        yield connection, store, attempt_id, capture_id


def _count(connection: Any, table: str) -> int:
    row = connection.execute(
        sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table))
    ).fetchone()
    return int(row[0])


def _all_rk04_counts(connection: Any) -> dict[str, int]:
    return {table: _count(connection, table) for table in RK04_TABLES}


def _fetch_relation(connection: Any, table: str) -> tuple[tuple[str, ...], tuple[Any, ...]]:
    columns = tuple(
        str(row[0])
        for row in connection.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = current_schema() AND table_name = %s
            ORDER BY ordinal_position
            """,
            (table,),
        ).fetchall()
    )
    rows = connection.execute(
        sql.SQL("SELECT {} FROM {} ORDER BY {}").format(
            sql.SQL(", ").join(sql.Identifier(key) for key in columns),
            sql.Identifier(table),
            sql.SQL(", ").join(sql.Identifier(key) for key in columns),
        )
    ).fetchall()
    return columns, tuple(tuple(row) for row in rows)


# --------------------------------------------------------------------------------------
# Recipe identity and declarations
# --------------------------------------------------------------------------------------


def test_recipe_bytes_and_digest_recompute_independently() -> None:
    import hashlib

    assert len(RELATED_KEYWORDS_RECIPE_BYTES) == 2398
    assert not RELATED_KEYWORDS_RECIPE_BYTES.endswith(b"\n")
    assert hashlib.sha256(RELATED_KEYWORDS_RECIPE_BYTES).hexdigest() == (
        RELATED_KEYWORDS_RECIPE_ID
    )
    assert recipe_bytes(RELATED_KEYWORDS_RECIPE) == RELATED_KEYWORDS_RECIPE_BYTES
    assert recipe_derivation_version_id(RELATED_KEYWORDS_RECIPE) == (
        RELATED_KEYWORDS_RECIPE_ID
    )
    assert related_keywords_recipe() == RELATED_KEYWORDS_RECIPE
    assert RELATED_KEYWORDS_RECIPE_ID != CORE_RECIPE_ID


def test_recipe_declares_exactly_three_kinds_with_locus_axes() -> None:
    assert RELATED_KEYWORDS_RECIPE["observation_kinds"] == [
        KEYWORD_DATA_KIND,
        MONTHLY_KIND,
        RELATIONSHIP_KIND,
    ]
    identity = RELATED_KEYWORDS_RECIPE["observation_identity"]
    assert isinstance(identity, dict)
    declared = identity["kinds"]
    assert isinstance(declared, list)
    axes = {entry["observation_kind"]: entry["axes"] for entry in declared}
    assert axes[KEYWORD_DATA_KIND] == {
        "keyword": "string",
        "locus": "string",
        "requested_seed": "string",
    }
    assert axes[MONTHLY_KIND] == {
        "keyword": "string",
        "locus": "string",
        "month": "integer",
        "requested_seed": "string",
        "year": "integer",
    }
    # `related_keywords` exists only on returned items, so relationship identity carries no
    # locus axis.
    assert axes[RELATIONSHIP_KIND] == {
        "requested_seed": "string",
        "source_keyword": "string",
        "target_keyword": "string",
    }


def test_recipe_is_related_keywords_specific_and_not_keyword_overview() -> None:
    assert RELATED_KEYWORDS_RECIPE["adapter_contract"] == RELATED_KEYWORDS_ADAPTER_CONTRACT
    assert RELATED_KEYWORDS_RECIPE["parser_contract"] == PARSER_CONTRACT
    assert RELATED_KEYWORDS_RECIPE["provider"] == PROVIDER
    text = RELATED_KEYWORDS_RECIPE_BYTES.decode("utf-8")
    assert "keyword_overview" not in text
    assert RELATED_KEYWORDS_RECIPE["data_period"] == {
        "inheritance": "never_from_capture",
        "rule": "provider_stated_year_month_1_9999",
    }
    assert RELATED_KEYWORDS_RECIPE["provider_update_time"] == {
        "inheritance": "never_from_capture_or_sibling",
        "rule": "structure_local_clocks_no_universal_update_time",
    }
    assert RELATED_KEYWORDS_RECIPE["numeric"] == {"normalization": "exact_decimal"}
    extension = RELATED_KEYWORDS_RECIPE["extension_policy"]
    assert isinstance(extension, dict)
    assert extension["extension_permitted_objects"] == []
    assert extension["unknown_closed_field"] == "fail_closed"


def test_recipe_declares_the_closed_capture_outcome_taxonomy() -> None:
    admission = RELATED_KEYWORDS_RECIPE["admission"]
    assert isinstance(admission, dict)
    assert admission["capture_outcomes"] == [
        "no_response",
        "observation_admitted",
        "observation_admitted_empty",
        "provider_envelope_rejected",
        "provider_error",
        "reconciliation_failed",
        "response_partial",
        "transport_complete_non_admissible",
    ]


def test_migrate_kind_constants_match_the_parser_module() -> None:
    assert RELATED_KEYWORDS_KEYWORD_DATA_KIND == KEYWORD_DATA_KIND
    assert RELATED_KEYWORDS_MONTHLY_KIND == MONTHLY_KIND
    assert RELATED_KEYWORDS_RELATIONSHIP_KIND == RELATIONSHIP_KIND


# --------------------------------------------------------------------------------------
# Migration layering
# --------------------------------------------------------------------------------------


def test_pre_rk04_layering_is_additive_and_preserves_the_historical_delta() -> None:
    historical = [
        statement
        for statement in PRE_RK04_SCHEMA_STATEMENTS
        if statement not in PRE_AI16_SCHEMA_STATEMENTS
    ]
    assert len(historical) == 3
    assert "related_keywords_" not in "\n".join(PRE_RK04_SCHEMA_STATEMENTS)
    added = [
        statement
        for statement in SCHEMA_STATEMENTS
        if statement not in PRE_RK04_SCHEMA_STATEMENTS
    ]
    assert added == list(RK04_SCHEMA_STATEMENTS)
    assert len(added) == 12
    assert len(RK04_TABLES) == 12
    for table in RK04_TABLES:
        assert any(f"CREATE TABLE IF NOT EXISTS {table} (" in item for item in added)


def test_no_rk04_relation_exposes_a_generic_provider_update_time() -> None:
    joined = "\n".join(RK04_SCHEMA_STATEMENTS)
    assert "provider_update_time" not in joined
    for column in DEPTH_ZERO_CLOCKS:
        assert column in joined


# --------------------------------------------------------------------------------------
# Golden planning from the frozen RK-02 fixture
# --------------------------------------------------------------------------------------


def test_frozen_fixture_identity_is_unchanged() -> None:
    import hashlib

    raw = _fixture_body()
    assert len(raw) == FIXTURE_BYTES
    assert hashlib.sha256(raw).hexdigest() == FIXTURE_SHA256


def test_golden_counts_are_independently_derived_from_the_fixture() -> None:
    planned = _golden_plan()
    assert planned.classification == "observation_admitted"
    by_kind: dict[str, int] = {}
    for envelope in planned.envelopes:
        by_kind[envelope.observation_kind] = by_kind.get(envelope.observation_kind, 0) + 1
    assert by_kind[KEYWORD_DATA_KIND] == GOLDEN_KEYWORD_DATA
    assert by_kind[MONTHLY_KIND] == GOLDEN_MONTHLY
    assert by_kind[RELATIONSHIP_KIND] == GOLDEN_RELATIONSHIP
    assert (
        by_kind[KEYWORD_DATA_KIND] + by_kind[MONTHLY_KIND] + by_kind[RELATIONSHIP_KIND]
        == GOLDEN_ENVELOPES
    )
    assert len(planned.envelopes) == GOLDEN_ENVELOPES
    assert len({envelope.within_capture_identity for envelope in planned.envelopes}) == (
        GOLDEN_ENVELOPES
    )
    assert len(planned.item_occurrences) == GOLDEN_ITEM_OCCURRENCES
    assert len(planned.monthly_occurrences) == GOLDEN_MONTHLY_OCCURRENCES
    assert len(planned.relationship_occurrences) == GOLDEN_RELATIONSHIP_OCCURRENCES


def test_golden_seed_and_returned_loci_are_distinct_identities_for_one_keyword() -> None:
    planned = _golden_plan()
    rows = [
        row
        for row in planned.details[KEYWORD_DATA_TABLE]
        if row["keyword"] == SEED
    ]
    assert {row["locus"] for row in rows} == {LOCUS_SEED, LOCUS_ITEM}
    assert len(rows) == 2
    identities = {row["locus"]: row["within_capture_identity"] for row in rows}
    assert identities[LOCUS_SEED] != identities[LOCUS_ITEM]
    # The digests must be exactly the recipe's identity documents, not incidental values.
    for locus, identity in identities.items():
        assert identity == observation_identity(
            {
                "axes": {"keyword": SEED, "locus": locus, "requested_seed": SEED},
                "observation_kind": KEYWORD_DATA_KIND,
                "schema": IDENTITY_SCHEMA,
                "version": IDENTITY_VERSION,
            },
            RELATED_KEYWORDS_RECIPE,
        )
    monthly = [
        row for row in planned.details[MONTHLY_TABLE] if row["keyword"] == SEED
    ]
    assert len(monthly) == 24
    assert sum(1 for row in monthly if row["locus"] == LOCUS_SEED) == 12
    assert sum(1 for row in monthly if row["locus"] == LOCUS_ITEM) == 12
    # The seed locus is not an item-array occurrence, so it contributes no occurrence row.
    seed_identity = identities[LOCUS_SEED]
    assert not [
        row
        for row in planned.item_occurrences
        if row["within_capture_identity"] == seed_identity
    ]


def test_golden_frontier_target_is_an_edge_without_an_invented_keyword_data_row() -> None:
    planned = _golden_plan()
    edges = [
        row
        for row in planned.details[RELATIONSHIP_TABLE]
        if row["target_keyword"] == FRONTIER_TARGET
    ]
    assert len(edges) == 1
    assert edges[0]["source_keyword"] == FRONTIER_SOURCE
    assert edges[0]["requested_seed"] == SEED
    keywords = {row["keyword"] for row in planned.details[KEYWORD_DATA_TABLE]}
    assert FRONTIER_TARGET not in keywords
    assert not [
        row for row in planned.details[MONTHLY_TABLE] if row["keyword"] == FRONTIER_TARGET
    ]
    occurrences = [
        row
        for row in planned.relationship_occurrences
        if row["within_capture_identity"] == edges[0]["within_capture_identity"]
    ]
    assert len(occurrences) == 1
    assert occurrences[0]["target_index"] == 0
    assert occurrences[0]["source_depth"] == 1
    targets = {row["target_keyword"] for row in planned.details[RELATIONSHIP_TABLE]}
    assert len(targets) == 246
    assert len(targets - keywords) == 167


def test_golden_depth_zero_clocks_stay_structure_specific_and_independent() -> None:
    planned = _golden_plan()
    identity = _identity_for(planned, LOCUS_ITEM, SEED)
    info = _child_row(planned, KEYWORD_INFO_TABLE, identity)
    backlinks = _child_row(planned, BACKLINKS_TABLE, identity)
    intent = _child_row(planned, INTENT_TABLE, identity)
    serp = _child_row(planned, SERP_TABLE, identity)
    observed = {
        "keyword_info_last_updated_time": info["keyword_info_last_updated_time"],
        "avg_backlinks_last_updated_time": backlinks["avg_backlinks_last_updated_time"],
        "search_intent_last_updated_time": intent["search_intent_last_updated_time"],
        "serp_last_updated_time": serp["serp_last_updated_time"],
        "serp_previous_updated_time": serp["serp_previous_updated_time"],
    }
    assert observed == DEPTH_ZERO_CLOCKS
    assert len(set(observed.values())) == 5


def test_golden_hollow_serp_keeps_the_year_one_string_as_stated_text() -> None:
    planned = _golden_plan()
    for keyword in HOLLOW_SERP_KEYWORDS:
        identity = _identity_for(planned, LOCUS_ITEM, keyword)
        parent = _detail_row(planned, KEYWORD_DATA_TABLE, identity)
        assert parent["serp_info_state"] == "stated"
        serp = _child_row(planned, SERP_TABLE, identity)
        assert serp["serp_last_updated_time"] == YEAR_ONE_CLOCK
        assert serp["serp_last_updated_time_state"] == "stated"
        # No sentinel: every other SERP member is exactly the provider's JSON null.
        assert serp["serp_previous_updated_time"] is None
        assert serp["serp_previous_updated_time_state"] == "json_null"
        assert serp["check_url"] is None
        assert serp["check_url_state"] == "json_null"
        assert serp["serp_item_types"] is None
        assert serp["se_results_count"] is None


def test_golden_categories_preserve_provider_order_and_duplicates() -> None:
    planned = _golden_plan()
    identity = _identity_for(planned, LOCUS_ITEM, DUPLICATE_CATEGORY_KEYWORD)
    info = _child_row(planned, KEYWORD_INFO_TABLE, identity)
    assert info["categories"] == DUPLICATE_CATEGORIES
    assert info["categories_state"] == "stated"
    seed_info = _child_row(planned, KEYWORD_INFO_TABLE, _identity_for(planned, LOCUS_ITEM, SEED))
    assert seed_info["categories"] is None
    assert seed_info["categories_state"] == "json_null"


def test_golden_current_volume_is_never_derived_from_monthly_testimony() -> None:
    planned = _golden_plan()
    divergent = 0
    for row in planned.details[KEYWORD_DATA_TABLE]:
        if row["locus"] != LOCUS_ITEM:
            continue
        identity = row["within_capture_identity"]
        info = _child_row(planned, KEYWORD_INFO_TABLE, identity)
        monthly = [
            item
            for item in planned.details[MONTHLY_TABLE]
            if item["keyword"] == row["keyword"] and item["locus"] == LOCUS_ITEM
        ]
        newest = max(monthly, key=lambda point: (point["year"], point["month"]))
        if info["search_volume"] != newest["search_volume"]:
            divergent += 1
    assert divergent == 63


def test_golden_core_keyword_stays_properties_testimony() -> None:
    planned = _golden_plan()
    items = [
        _child_row(planned, PROPERTIES_TABLE, row["within_capture_identity"])
        for row in planned.details[KEYWORD_DATA_TABLE]
        if row["locus"] == LOCUS_ITEM
    ]
    stated = [row for row in items if row["core_keyword_state"] == "stated"]
    assert len(stated) == 21
    assert len({row["core_keyword"] for row in stated}) == 20
    assert sum(1 for row in items if row["core_keyword_state"] == "json_null") == 59
    # No fourth Observation kind and no canonicalization.
    assert {envelope.observation_kind for envelope in planned.envelopes} == {
        KEYWORD_DATA_KIND,
        MONTHLY_KIND,
        RELATIONSHIP_KIND,
    }


def test_golden_enrichment_state_counts_match_the_capture() -> None:
    planned = _golden_plan()
    rows = [
        row for row in planned.details[KEYWORD_DATA_TABLE] if row["locus"] == LOCUS_ITEM
    ]
    assert sum(1 for row in rows if row["avg_backlinks_state"] == "stated") == 59
    assert sum(1 for row in rows if row["avg_backlinks_state"] == "json_null") == 21
    assert sum(1 for row in rows if row["serp_info_state"] == "stated") == 62
    assert sum(1 for row in rows if row["serp_info_state"] == "json_null") == 18
    assert all(row["keyword_info_state"] == "stated" for row in rows)
    assert all(row["bing_normalized_state"] == "json_null" for row in rows)
    assert all(row["clickstream_normalized_state"] == "not_requested" for row in rows)
    assert all(row["clickstream_keyword_info_state"] == "not_requested" for row in rows)


def test_golden_related_keywords_state_lives_on_the_item_occurrence() -> None:
    planned = _golden_plan()
    states = [row["related_keywords_state"] for row in planned.item_occurrences]
    assert states.count("stated") == 60
    assert states.count("json_null") == 20
    assert len(states) == 80
    depths = sorted(row["depth"] for row in planned.item_occurrences)
    assert depths.count(0) == 1
    assert depths.count(1) == 8
    assert depths.count(2) == 30
    assert depths.count(3) == 41
    assert {row["item_se_type"] for row in planned.item_occurrences} == {"google"}
    assert sorted(row["item_index"] for row in planned.item_occurrences) == list(range(80))


def test_golden_context_records_attempt_authority_and_derived_counts() -> None:
    planned = _golden_plan()
    context = planned.context
    assert context["requested_seed"] == SEED
    assert context["result_seed_keyword"] == SEED
    assert context["request_depth"] == 3
    assert context["request_limit"] == 1000
    assert context["request_offset"] == 0
    assert context["request_order_by"] == [
        "keyword_data.keyword_info.search_volume,desc"
    ]
    assert context["request_include_seed_keyword"] is True
    assert context["request_include_clickstream_data"] is False
    assert context["total_count"] == 80
    assert context["items_count"] == 80
    assert context["seed_keyword_data_state"] == "stated"
    assert context["derived_returned_item_count"] == 80
    assert context["derived_relationship_occurrence_count"] == 477


def _identity_for(planned: Any, locus: str, keyword: str) -> str:
    for row in planned.details[KEYWORD_DATA_TABLE]:
        if row["locus"] == locus and row["keyword"] == keyword:
            return str(row["within_capture_identity"])
    raise AssertionError(f"no keyword-data row for {locus}/{keyword}")


def _detail_row(planned: Any, table: str, identity: str) -> Any:
    for row in planned.details[table]:
        if row["within_capture_identity"] == identity:
            return row
    raise AssertionError(f"no {table} row for {identity}")


def _child_row(planned: Any, table: str, identity: str) -> Any:
    return _detail_row(planned, table, identity)


# --------------------------------------------------------------------------------------
# Duplicate semantic identity: collapse with surviving occurrences, or reject
# --------------------------------------------------------------------------------------


def test_identical_duplicate_returned_keyword_collapses_with_both_occurrences() -> None:
    data = keyword_data("alpha", keyword_info=keyword_info())
    planned = _plan(
        simple_body(
            [
                item("alpha", depth=1, data=copy.deepcopy(data)),
                item("alpha", depth=2, data=copy.deepcopy(data)),
            ]
        )
    )
    assert planned is not None
    assert planned.classification == "observation_admitted"
    parents = planned.details[KEYWORD_DATA_TABLE]
    assert len(parents) == 1
    assert parents[0]["keyword"] == "alpha"
    occurrences = sorted(row["item_index"] for row in planned.item_occurrences)
    assert occurrences == [0, 1]
    assert sorted(row["depth"] for row in planned.item_occurrences) == [1, 2]
    # One monthly Observation, both item occurrences preserved.
    assert len(planned.details[MONTHLY_TABLE]) == 1
    assert sorted(row["item_index"] for row in planned.monthly_occurrences) == [0, 1]


def test_conflicting_duplicate_enrichment_rejects_the_whole_unit() -> None:
    first = keyword_data("alpha", keyword_info=keyword_info(competition_level="LOW"))
    second = keyword_data("alpha", keyword_info=keyword_info(competition_level="HIGH"))
    planned = _plan(
        simple_body(
            [
                item("alpha", data=first),
                item("alpha", data=second),
                item("beta", related=["alpha"]),
            ]
        )
    )
    assert planned is not None
    assert planned.classification == "provider_envelope_rejected"
    assert planned.envelopes == ()
    assert planned.context is None
    assert planned.item_occurrences == ()
    assert planned.relationship_occurrences == ()
    for table in _detail_tables():
        assert planned.details[table] == ()


def test_occurrence_only_differences_do_not_conflict() -> None:
    data = keyword_data("alpha", keyword_info=keyword_info())
    planned = _plan(
        simple_body(
            [
                item("alpha", depth=1, data=copy.deepcopy(data), related=["t1"]),
                item("alpha", depth=3, data=copy.deepcopy(data), related=None),
                item("alpha", depth=2, data=copy.deepcopy(data)),
            ]
        )
    )
    assert planned is not None
    assert planned.classification == "observation_admitted"
    assert len(planned.details[KEYWORD_DATA_TABLE]) == 1
    states = {
        row["item_index"]: row["related_keywords_state"]
        for row in planned.item_occurrences
    }
    # Array index, depth, and neighbourhood state are occurrence testimony only.
    assert states == {0: "stated", 1: "json_null", 2: "absent"}
    assert len(planned.details[RELATIONSHIP_TABLE]) == 1


def test_state_disagreement_on_the_monthly_array_still_conflicts() -> None:
    stated = keyword_data("alpha", keyword_info=keyword_info())
    absent = keyword_data("alpha", keyword_info=keyword_info(monthly_searches=None))
    planned = _plan(simple_body([item("alpha", data=stated), item("alpha", data=absent)]))
    assert planned is not None
    assert planned.classification == "provider_envelope_rejected"


def test_equal_overlapping_monthly_periods_collapse() -> None:
    points = [{"year": 2026, "month": 7, "search_volume": 90}]
    planned = _plan(
        simple_body(
            [
                item(
                    "alpha",
                    data=keyword_data(
                        "alpha", keyword_info=keyword_info(monthly_searches=points)
                    ),
                ),
                item(
                    "alpha",
                    data=keyword_data(
                        "alpha",
                        keyword_info=keyword_info(monthly_searches=copy.deepcopy(points)),
                    ),
                ),
            ]
        )
    )
    assert planned is not None
    assert planned.classification == "observation_admitted"
    assert len(planned.details[MONTHLY_TABLE]) == 1
    assert planned.details[MONTHLY_TABLE][0]["search_volume"] == 90
    assert sorted(row["item_index"] for row in planned.monthly_occurrences) == [0, 1]


def test_conflicting_overlapping_monthly_volumes_reject_the_unit() -> None:
    planned = _plan(
        simple_body(
            [
                item(
                    "alpha",
                    data=keyword_data(
                        "alpha",
                        keyword_info=keyword_info(
                            monthly_searches=[
                                {"year": 2026, "month": 7, "search_volume": 90}
                            ]
                        ),
                    ),
                ),
                item(
                    "alpha",
                    data=keyword_data(
                        "alpha",
                        keyword_info=keyword_info(
                            monthly_searches=[
                                {"year": 2026, "month": 7, "search_volume": 91}
                            ]
                        ),
                    ),
                ),
            ]
        )
    )
    assert planned is not None
    assert planned.classification == "provider_envelope_rejected"
    assert planned.envelopes == ()


def test_non_overlapping_monthly_windows_union_when_overlaps_agree() -> None:
    left = [
        {"year": 2026, "month": 7, "search_volume": 90},
        {"year": 2026, "month": 6, "search_volume": 80},
    ]
    right = [
        {"year": 2026, "month": 6, "search_volume": 80},
        {"year": 2026, "month": 5, "search_volume": 70},
    ]
    planned = _plan(
        simple_body(
            [
                item(
                    "alpha",
                    data=keyword_data(
                        "alpha", keyword_info=keyword_info(monthly_searches=left)
                    ),
                ),
                item(
                    "alpha",
                    data=keyword_data(
                        "alpha", keyword_info=keyword_info(monthly_searches=right)
                    ),
                ),
            ]
        )
    )
    assert planned is not None
    assert planned.classification == "observation_admitted"
    periods = sorted(
        (row["year"], row["month"], row["search_volume"])
        for row in planned.details[MONTHLY_TABLE]
    )
    assert periods == [(2026, 5, 70), (2026, 6, 80), (2026, 7, 90)]
    shared = [
        row
        for row in planned.details[MONTHLY_TABLE]
        if (row["year"], row["month"]) == (2026, 6)
    ][0]
    occurrences = sorted(
        row["item_index"]
        for row in planned.monthly_occurrences
        if row["within_capture_identity"] == shared["within_capture_identity"]
    )
    assert occurrences == [0, 1]


def test_duplicate_target_in_one_source_array_keeps_every_occurrence() -> None:
    planned = _plan(simple_body([item("alpha", related=["t", "u", "t"])]))
    assert planned is not None
    edges = planned.details[RELATIONSHIP_TABLE]
    assert len(edges) == 2
    duplicate = [row for row in edges if row["target_keyword"] == "t"][0]
    occurrences = sorted(
        row["target_index"]
        for row in planned.relationship_occurrences
        if row["within_capture_identity"] == duplicate["within_capture_identity"]
    )
    assert occurrences == [0, 2]
    assert len(planned.relationship_occurrences) == 3


def test_repeated_edge_across_duplicate_sources_collapses_with_occurrences() -> None:
    data = keyword_data("alpha", keyword_info=keyword_info())
    planned = _plan(
        simple_body(
            [
                item("alpha", depth=1, data=copy.deepcopy(data), related=["t"]),
                item("alpha", depth=2, data=copy.deepcopy(data), related=["t"]),
            ]
        )
    )
    assert planned is not None
    assert len(planned.details[RELATIONSHIP_TABLE]) == 1
    occurrences = sorted(
        (row["source_item_index"], row["target_index"], row["source_depth"])
        for row in planned.relationship_occurrences
    )
    assert occurrences == [(0, 0, 1), (1, 0, 2)]


def test_self_and_backward_references_remain_admissible_occurrences() -> None:
    planned = _plan(
        simple_body(
            [
                item("alpha", depth=2, related=["alpha", "beta"]),
                item("beta", depth=1, related=["alpha"]),
            ]
        )
    )
    assert planned is not None
    pairs = sorted(
        (row["source_keyword"], row["target_keyword"])
        for row in planned.details[RELATIONSHIP_TABLE]
    )
    assert pairs == [("alpha", "alpha"), ("alpha", "beta"), ("beta", "alpha")]


# --------------------------------------------------------------------------------------
# Field-state branches the frozen Capture never exhibits
# --------------------------------------------------------------------------------------


def test_related_keywords_absent_null_and_empty_stay_distinct_with_zero_edges() -> None:
    planned = _plan(
        simple_body(
            [
                item("a"),
                item("b", related=None),
                item("c", related=[]),
            ]
        )
    )
    assert planned is not None
    assert planned.classification == "observation_admitted"
    assert planned.details[RELATIONSHIP_TABLE] == ()
    assert planned.relationship_occurrences == ()
    states = {
        row["item_index"]: row["related_keywords_state"]
        for row in planned.item_occurrences
    }
    assert states == {0: "absent", 1: "json_null", 2: "stated"}
    assert planned.context["derived_relationship_occurrence_count"] == 0


def test_monthly_absent_null_empty_and_stated_zero_stay_distinct() -> None:
    planned = _plan(
        simple_body(
            [
                item(
                    "a",
                    data=keyword_data(
                        "a", keyword_info=keyword_info(monthly_searches=OMIT)
                    ),
                ),
                item(
                    "b",
                    data=keyword_data(
                        "b", keyword_info=keyword_info(monthly_searches=None)
                    ),
                ),
                item(
                    "c",
                    data=keyword_data(
                        "c", keyword_info=keyword_info(monthly_searches=[])
                    ),
                ),
                item(
                    "d",
                    data=keyword_data(
                        "d",
                        keyword_info=keyword_info(
                            monthly_searches=[
                                {"year": 2026, "month": 7, "search_volume": 0}
                            ]
                        ),
                    ),
                ),
            ]
        )
    )
    assert planned is not None
    states = {}
    for row in planned.details[KEYWORD_DATA_TABLE]:
        info = _child_row(planned, KEYWORD_INFO_TABLE, row["within_capture_identity"])
        states[row["keyword"]] = info["monthly_searches_state"]
    assert states == {
        "a": "absent",
        "b": "json_null",
        "c": "stated",
        "d": "stated",
    }
    # Absent, null, and stated-empty emit no monthly Observation; a stated zero does.
    monthly = planned.details[MONTHLY_TABLE]
    assert len(monthly) == 1
    assert monthly[0]["keyword"] == "d"
    assert monthly[0]["search_volume"] == 0


def test_search_volume_trend_absent_marks_members_inapplicable() -> None:
    planned = _plan(
        simple_body(
            [
                item(
                    "a",
                    data=keyword_data(
                        "a", keyword_info=keyword_info(search_volume_trend=OMIT)
                    ),
                ),
                item(
                    "b",
                    data=keyword_data(
                        "b", keyword_info=keyword_info(search_volume_trend=None)
                    ),
                ),
                item("c", data=keyword_data("c", keyword_info=keyword_info())),
            ]
        )
    )
    assert planned is not None
    observed = {}
    for row in planned.details[KEYWORD_DATA_TABLE]:
        info = _child_row(planned, KEYWORD_INFO_TABLE, row["within_capture_identity"])
        observed[row["keyword"]] = (
            info["search_volume_trend_state"],
            info["trend_monthly"],
            info["trend_monthly_state"],
        )
    assert observed["a"] == ("absent", None, "inapplicable")
    assert observed["b"] == ("json_null", None, "inapplicable")
    assert observed["c"] == ("stated", -5, "stated")


def test_enrichment_objects_absent_null_and_stated_emit_child_rows_only_when_stated() -> None:
    planned = _plan(
        simple_body(
            [
                item("a"),
                item(
                    "b",
                    data=keyword_data(
                        "b",
                        keyword_info=None,
                        keyword_properties=None,
                        avg_backlinks_info=None,
                        search_intent_info=None,
                        serp_info=None,
                    ),
                ),
                item(
                    "c",
                    data=keyword_data(
                        "c",
                        keyword_info=keyword_info(),
                        keyword_properties={"core_keyword": "core c"},
                        avg_backlinks_info={"backlinks": 5},
                        search_intent_info={"main_intent": "informational"},
                        serp_info={"check_url": "https://example.test/serp"},
                    ),
                ),
            ]
        )
    )
    assert planned is not None
    parents = {row["keyword"]: row for row in planned.details[KEYWORD_DATA_TABLE]}
    assert parents["a"]["keyword_info_state"] == "absent"
    assert parents["a"]["serp_info_state"] == "absent"
    assert parents["b"]["keyword_info_state"] == "json_null"
    assert parents["b"]["avg_backlinks_state"] == "json_null"
    assert parents["c"]["search_intent_state"] == "stated"
    for table in (
        KEYWORD_INFO_TABLE,
        PROPERTIES_TABLE,
        BACKLINKS_TABLE,
        INTENT_TABLE,
        SERP_TABLE,
    ):
        keywords = {
            row["within_capture_identity"] for row in planned.details[table]
        }
        assert keywords == {parents["c"]["within_capture_identity"]}


def test_array_states_and_duplicates_survive_for_intent_and_serp() -> None:
    planned = _plan(
        simple_body(
            [
                item(
                    "a",
                    data=keyword_data(
                        "a",
                        search_intent_info={"foreign_intent": None},
                        serp_info={"serp_item_types": []},
                    ),
                ),
                item(
                    "b",
                    data=keyword_data(
                        "b",
                        search_intent_info={"foreign_intent": ["commercial", "commercial"]},
                        serp_info={
                            "serp_item_types": ["organic", "organic", "ai_overview"]
                        },
                    ),
                ),
                item(
                    "c",
                    data=keyword_data(
                        "c",
                        search_intent_info={"main_intent": "informational"},
                        serp_info={"check_url": "https://example.test/c"},
                    ),
                ),
            ]
        )
    )
    assert planned is not None
    by_keyword = {
        row["keyword"]: row["within_capture_identity"]
        for row in planned.details[KEYWORD_DATA_TABLE]
    }
    a_intent = _child_row(planned, INTENT_TABLE, by_keyword["a"])
    assert a_intent["foreign_intent"] is None
    assert a_intent["foreign_intent_state"] == "json_null"
    a_serp = _child_row(planned, SERP_TABLE, by_keyword["a"])
    assert a_serp["serp_item_types"] == []
    assert a_serp["serp_item_types_state"] == "stated"
    b_intent = _child_row(planned, INTENT_TABLE, by_keyword["b"])
    assert b_intent["foreign_intent"] == ["commercial", "commercial"]
    b_serp = _child_row(planned, SERP_TABLE, by_keyword["b"])
    assert b_serp["serp_item_types"] == ["organic", "organic", "ai_overview"]
    c_intent = _child_row(planned, INTENT_TABLE, by_keyword["c"])
    assert c_intent["foreign_intent"] is None
    assert c_intent["foreign_intent_state"] == "absent"


def test_seed_disagreement_with_depth_zero_item_is_two_valid_identities() -> None:
    planned = _plan(
        simple_body(
            [item(SEED, depth=0, data=keyword_data(SEED, keyword_info=keyword_info()))],
            seed_data=keyword_data(
                SEED, keyword_info=keyword_info(search_volume=999, competition_level="HIGH")
            ),
        )
    )
    assert planned is not None
    assert planned.classification == "observation_admitted"
    rows = {row["locus"]: row for row in planned.details[KEYWORD_DATA_TABLE]}
    assert set(rows) == {LOCUS_SEED, LOCUS_ITEM}
    seed_info = _child_row(
        planned, KEYWORD_INFO_TABLE, rows[LOCUS_SEED]["within_capture_identity"]
    )
    item_info = _child_row(
        planned, KEYWORD_INFO_TABLE, rows[LOCUS_ITEM]["within_capture_identity"]
    )
    assert seed_info["search_volume"] == 999
    assert item_info["search_volume"] == 100
    assert len(planned.item_occurrences) == 1


def test_missing_depth_zero_item_is_valid_testimony() -> None:
    planned = _plan(simple_body([item("alpha", depth=2), item("beta", depth=3)]))
    assert planned is not None
    assert planned.classification == "observation_admitted"
    assert {row["depth"] for row in planned.item_occurrences} == {2, 3}


def test_missing_or_null_seed_keyword_data_does_not_reject() -> None:
    for seed_state, expected in (("omit", "absent"), (None, "json_null")):
        planned = _plan(simple_body([item("alpha")], seed_data=seed_state))
        assert planned is not None
        assert planned.classification == "observation_admitted"
        assert planned.context["seed_keyword_data_state"] == expected
        assert {row["locus"] for row in planned.details[KEYWORD_DATA_TABLE]} == {
            LOCUS_ITEM
        }


# --------------------------------------------------------------------------------------
# Whole-unit rejection: identity and inadmissible provider text
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("missing", ["omit", None])
def test_item_without_stated_keyword_data_rejects_the_whole_unit(missing: Any) -> None:
    row: dict[str, Any] = {"depth": 1, "se_type": "google"}
    if missing is None:
        row["keyword_data"] = None
    planned = _plan(simple_body([item("alpha", related=["t"]), row]))
    assert planned is not None
    assert planned.classification == "provider_envelope_rejected"
    assert planned.envelopes == ()
    assert planned.context is None


# Every string a provider can put in an identity axis or a persisted column. The two
# noncharacter classes are the exact canonical-I-JSON boundary that `capture_event` enforces
# inside `canonical_json`: U+FDD0..U+FDEF, and any code point whose low 16 bits are 0xFFFE or
# 0xFFFF. Before RK-04 remediation these parsed cleanly through RK-03 and `_require_text`, then
# escaped the derive run as an uncaught `DocumentError` from `observation_identity`.
INADMISSIBLE_TEXT: tuple[tuple[str, str], ...] = (
    ("nul", "bad\x00value"),
    ("lone_surrogate", "lone\ud800value"),
    ("noncharacter_fdd0", "bad\ufdd0value"),
    ("noncharacter_fdef", "bad\ufdefvalue"),
    ("noncharacter_fffe", "bad\ufffevalue"),
    ("noncharacter_ffff", "bad\uffffvalue"),
    ("noncharacter_supplementary", "bad\U0001fffevalue"),
)
_INADMISSIBLE_IDS = [name for name, _value in INADMISSIBLE_TEXT]
_INADMISSIBLE_VALUES = [value for _name, value in INADMISSIBLE_TEXT]


def _assert_rejected_with_no_rows(planned: Any) -> None:
    assert planned is not None
    assert planned.classification == "provider_envelope_rejected"
    assert planned.envelopes == ()
    assert planned.context is None
    assert planned.item_occurrences == ()
    assert planned.monthly_occurrences == ()
    assert planned.relationship_occurrences == ()
    for table in _detail_tables():
        assert planned.details[table] == ()


@pytest.mark.parametrize(
    "keyword", ["", *_INADMISSIBLE_VALUES], ids=["empty", *_INADMISSIBLE_IDS]
)
def test_inadmissible_identity_keyword_rejects_without_a_crash(keyword: str) -> None:
    _assert_rejected_with_no_rows(_plan(simple_body([item(keyword)])))


@pytest.mark.parametrize(
    "target", ["", *_INADMISSIBLE_VALUES], ids=["empty", *_INADMISSIBLE_IDS]
)
def test_inadmissible_relationship_target_rejects_without_a_crash(target: str) -> None:
    _assert_rejected_with_no_rows(_plan(simple_body([item("alpha", related=[target])])))


@pytest.mark.parametrize("value", _INADMISSIBLE_VALUES, ids=_INADMISSIBLE_IDS)
def test_inadmissible_seed_locus_keyword_rejects_without_a_crash(value: str) -> None:
    _assert_rejected_with_no_rows(
        _plan(simple_body([item("alpha")], seed_data=keyword_data(value)))
    )


def test_require_text_matches_the_canonical_ijson_boundary() -> None:
    """Pin the duplicated noncharacter predicate against real `canonical_json` behaviour.

    `_require_text` restates capture_event's rule rather than importing a private helper. This
    walks the whole boundary so the duplicate cannot drift: every code point canonical_json
    refuses must be refused here, and admissible neighbours must still pass.
    """

    boundary = [
        0xFDCF, 0xFDD0, 0xFDD1, 0xFDEE, 0xFDEF, 0xFDF0,
        0xFFFD, 0xFFFE, 0xFFFF,
        0x1FFFD, 0x1FFFE, 0x1FFFF, 0x20000,
        0x10FFFE, 0x10FFFF,
        0xD7FF, 0xE000,
    ]
    for code in boundary:
        text = chr(code)
        try:
            canonical_json({"k": text})
        except DocumentError:
            jcs_admits = False
        else:
            jcs_admits = True
        try:
            _require_text(text)
        except SemanticDisagreement:
            rk04_admits = False
        else:
            rk04_admits = True
        assert rk04_admits == jcs_admits, f"U+{code:04X} disagrees with canonical_json"
    # U+0000 is the one deliberate asymmetry: canonical JSON escapes it, PostgreSQL TEXT
    # cannot store it, so RK-04 is stricter than JCS for exactly that code point.
    canonical_json({"k": "\x00"})
    with pytest.raises(SemanticDisagreement):
        _require_text("\x00")


@pytest.mark.parametrize("value", _INADMISSIBLE_VALUES, ids=_INADMISSIBLE_IDS)
def test_inadmissible_non_identity_check_url_also_rejects(value: str) -> None:
    _assert_rejected_with_no_rows(
        _plan(
            simple_body(
                [
                    item(
                        "alpha",
                        data=keyword_data(
                            "alpha", serp_info={"check_url": f"https://example.test/{value}"}
                        ),
                    )
                ]
            )
        )
    )


@pytest.mark.parametrize("value", _INADMISSIBLE_VALUES, ids=_INADMISSIBLE_IDS)
def test_inadmissible_non_identity_array_member_also_rejects(value: str) -> None:
    _assert_rejected_with_no_rows(
        _plan(
            simple_body(
                [
                    item(
                        "alpha",
                        data=keyword_data(
                            "alpha", search_intent_info={"foreign_intent": ["ok", value]}
                        ),
                    )
                ]
            )
        )
    )


def test_empty_core_keyword_remains_exact_non_identity_testimony() -> None:
    planned = _plan(
        simple_body(
            [item("alpha", data=keyword_data("alpha", keyword_properties={"core_keyword": ""}))]
        )
    )
    assert planned is not None
    assert planned.classification == "observation_admitted"
    properties = planned.details[PROPERTIES_TABLE][0]
    assert properties["core_keyword"] == ""
    assert properties["core_keyword_state"] == "stated"


# --------------------------------------------------------------------------------------
# Classification boundaries
# --------------------------------------------------------------------------------------


def test_empty_result_without_seed_data_is_admitted_empty_with_context() -> None:
    planned = _plan(simple_body([], total_count=0))
    assert planned is not None
    assert planned.classification == "observation_admitted_empty"
    assert planned.envelopes == ()
    assert planned.item_occurrences == ()
    for table in _detail_tables():
        assert planned.details[table] == ()
    assert planned.context is not None
    assert planned.context["requested_seed"] == SEED
    assert planned.context["items_count"] == 0
    assert planned.context["seed_keyword_data_state"] == "absent"


def test_stated_seed_data_with_empty_items_is_ordinary_admitted_testimony() -> None:
    planned = _plan(
        simple_body(
            [],
            total_count=0,
            seed_data=keyword_data(SEED, keyword_info=keyword_info()),
        )
    )
    assert planned is not None
    assert planned.classification == "observation_admitted"
    assert len(planned.details[KEYWORD_DATA_TABLE]) == 1
    assert planned.details[KEYWORD_DATA_TABLE][0]["locus"] == LOCUS_SEED
    assert len(planned.details[MONTHLY_TABLE]) == 1
    assert planned.item_occurrences == ()
    assert planned.monthly_occurrences == ()


def test_provider_error_becomes_repository_provider_error_with_zero_rows() -> None:
    planned = _plan(
        synthetic_body(None, status_code=40501, status_message="Invalid Field", result_count=0)
    )
    assert planned is not None
    assert planned.classification == "provider_error"
    assert planned.envelopes == ()
    assert planned.context is None


def test_body_parse_failure_is_provider_envelope_rejected() -> None:
    assert _plan(b"{not json").classification == "provider_envelope_rejected"
    assert _plan(b"\xef\xbb\xbf{}").classification == "provider_envelope_rejected"
    unknown = json.loads(simple_body([item("alpha")]))
    unknown["tasks"][0]["result"][0]["items"][0]["keyword_data"]["search_partners"] = True
    rejected = _plan(json.dumps(unknown).encode())
    assert rejected.classification == "provider_envelope_rejected"


@pytest.mark.parametrize(
    "mutate",
    [
        {"depth": 4},
        {"limit": 999},
        {"include_serp_info": False},
        {"contract": "dataforseo-labs-google-organic-live-paid-probe-v1"},
        {"unexpected": 1},
    ],
)
def test_residual_attempt_parser_failure_is_integrity_not_provider_fault(
    mutate: dict[str, object]
) -> None:
    # The trusted capture_event validator has already accepted the Attempt by this point, so
    # a residual `/attempt` parser failure is validator divergence or Evidence damage, never a
    # verdict about a body the parser has not even decoded yet.
    parameters = dict(_params())
    parameters.update(mutate)
    assert _plan(simple_body([item("alpha")]), parameters=parameters) is None


def test_result_echo_disagreement_stays_testimony_and_never_reconciliation_failed() -> None:
    planned = _plan(
        simple_body(
            [item("alpha")],
            seed_keyword="a different provider seed",
            extra={"location_code": 9999, "language_code": "de"},
        )
    )
    assert planned is not None
    assert planned.classification == "observation_admitted"
    context = planned.context
    # The verified Attempt stays request authority; the provider echo is preserved beside it.
    assert context["requested_seed"] == SEED
    assert context["request_location_code"] == 2840
    assert context["request_language_code"] == "en"
    assert context["result_seed_keyword"] == "a different provider seed"
    assert context["result_location_code"] == 9999
    assert context["result_language_code"] == "de"
    assert planned.details[KEYWORD_DATA_TABLE][0]["requested_seed"] == SEED


@pytest.mark.parametrize(
    ("capture", "expected"),
    [
        ({"transport_state": "no_response"}, "no_response"),
        (
            {"transport_state": "response_partial", "response": {"completeness": "partial"}},
            "response_partial",
        ),
        (
            {"transport_state": "weird", "response": {"completeness": "complete"}},
            "transport_complete_non_admissible",
        ),
        (
            {"transport_state": "response_complete", "response": {"completeness": "partial"}},
            "transport_complete_non_admissible",
        ),
    ],
)
def test_transport_states_keep_their_existing_classifications(
    capture: dict[str, object], expected: str
) -> None:
    planned = _plan(simple_body([item("alpha")]), capture=capture)
    assert planned is not None
    assert planned.classification == expected
    assert planned.envelopes == ()
    assert planned.context is None


def test_complete_transport_with_empty_body_is_non_admissible() -> None:
    planned = _plan(b"")
    assert planned is not None
    assert planned.classification == "transport_complete_non_admissible"


def _detail_tables() -> tuple[str, ...]:
    return (
        KEYWORD_DATA_TABLE,
        KEYWORD_INFO_TABLE,
        PROPERTIES_TABLE,
        BACKLINKS_TABLE,
        INTENT_TABLE,
        SERP_TABLE,
        MONTHLY_TABLE,
        RELATIONSHIP_TABLE,
    )


# --------------------------------------------------------------------------------------
# Real PostgreSQL: schema, atomicity, complete set, rebuild equivalence
# --------------------------------------------------------------------------------------


def test_derive_rk02_fixture_into_real_postgres(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "golden")
    attempt_id, capture_id = _commit(store, _fixture_body(), "21" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_google_related_keywords(store, connection)
        connection.commit()
        assert summary.derivation_version_id == RELATED_KEYWORDS_RECIPE_ID
        assert summary.attempt_outcomes == 1
        assert summary.capture_outcomes == 1
        assert summary.observations == GOLDEN_ENVELOPES
        assert summary.integrity_failures == 0
        assert summary.diagnostics == 0

        counts = _all_rk04_counts(connection)
        assert counts == {
            KEYWORD_DATA_TABLE: GOLDEN_KEYWORD_DATA,
            KEYWORD_INFO_TABLE: 81,
            PROPERTIES_TABLE: 81,
            BACKLINKS_TABLE: 60,
            INTENT_TABLE: 81,
            SERP_TABLE: 63,
            MONTHLY_TABLE: GOLDEN_MONTHLY,
            RELATIONSHIP_TABLE: GOLDEN_RELATIONSHIP,
            ITEM_OCCURRENCES_TABLE: GOLDEN_ITEM_OCCURRENCES,
            MONTHLY_OCCURRENCES_TABLE: GOLDEN_MONTHLY_OCCURRENCES,
            RELATIONSHIP_OCCURRENCES_TABLE: GOLDEN_RELATIONSHIP_OCCURRENCES,
            CONTEXT_TABLE: 1,
        }

        outcomes = connection.execute(
            """
            SELECT attempt_id, capture_id, classification, observation_count
            FROM outcomes WHERE derivation_version_id = %s
            ORDER BY capture_id NULLS FIRST
            """,
            (RELATED_KEYWORDS_RECIPE_ID,),
        ).fetchall()
        assert outcomes == [
            (attempt_id, None, "authorized_unresolved", 0),
            (attempt_id, capture_id, "observation_admitted", GOLDEN_ENVELOPES),
        ]

        by_kind = dict(
            connection.execute(
                """
                SELECT observation_kind, count(*)
                FROM observation_envelopes WHERE derivation_version_id = %s
                GROUP BY observation_kind
                """,
                (RELATED_KEYWORDS_RECIPE_ID,),
            ).fetchall()
        )
        assert by_kind == {
            KEYWORD_DATA_KIND: GOLDEN_KEYWORD_DATA,
            MONTHLY_KIND: GOLDEN_MONTHLY,
            RELATIONSHIP_KIND: GOLDEN_RELATIONSHIP,
        }

        # Seed and returned loci persist as two rows for the identical keyword string.
        loci = connection.execute(
            "SELECT locus, within_capture_identity FROM related_keywords_keyword_data"
            " WHERE keyword = %s ORDER BY locus",
            (SEED,),
        ).fetchall()
        assert [row[0] for row in loci] == [LOCUS_ITEM, LOCUS_SEED]
        assert loci[0][1] != loci[1][1]

        # The frontier target is an edge with no invented keyword-data node.
        assert connection.execute(
            "SELECT count(*) FROM related_keywords_relationship WHERE target_keyword = %s",
            (FRONTIER_TARGET,),
        ).fetchone() == (1,)
        assert connection.execute(
            "SELECT count(*) FROM related_keywords_keyword_data WHERE keyword = %s",
            (FRONTIER_TARGET,),
        ).fetchone() == (0,)

        # Independent depth-0 clocks survive under structure-specific column names.
        clocks = connection.execute(
            """
            SELECT ki.keyword_info_last_updated_time,
                   bl.avg_backlinks_last_updated_time,
                   si.search_intent_last_updated_time,
                   sp.serp_last_updated_time,
                   sp.serp_previous_updated_time
            FROM related_keywords_keyword_data AS kd
            JOIN related_keywords_keyword_info AS ki
              USING (capture_id, derivation_version_id, within_capture_identity)
            JOIN related_keywords_avg_backlinks AS bl
              USING (capture_id, derivation_version_id, within_capture_identity)
            JOIN related_keywords_search_intent AS si
              USING (capture_id, derivation_version_id, within_capture_identity)
            JOIN related_keywords_serp_info AS sp
              USING (capture_id, derivation_version_id, within_capture_identity)
            WHERE kd.keyword = %s AND kd.locus = %s
            """,
            (SEED, LOCUS_ITEM),
        ).fetchone()
        assert clocks is not None
        assert list(clocks) == [
            DEPTH_ZERO_CLOCKS["keyword_info_last_updated_time"],
            DEPTH_ZERO_CLOCKS["avg_backlinks_last_updated_time"],
            DEPTH_ZERO_CLOCKS["search_intent_last_updated_time"],
            DEPTH_ZERO_CLOCKS["serp_last_updated_time"],
            DEPTH_ZERO_CLOCKS["serp_previous_updated_time"],
        ]

        # The year-1 SERP clock keeps its exact stated text with no sentinel meaning.
        hollow = connection.execute(
            """
            SELECT kd.keyword, sp.serp_last_updated_time, sp.serp_last_updated_time_state,
                   sp.check_url_state
            FROM related_keywords_keyword_data AS kd
            JOIN related_keywords_serp_info AS sp
              USING (capture_id, derivation_version_id, within_capture_identity)
            WHERE sp.serp_last_updated_time = %s
            ORDER BY kd.keyword
            """,
            (YEAR_ONE_CLOCK,),
        ).fetchall()
        assert [row[0] for row in hollow] == sorted(HOLLOW_SERP_KEYWORDS)
        assert all(row[1] == YEAR_ONE_CLOCK for row in hollow)
        assert all(row[2] == "stated" for row in hollow)
        assert all(row[3] == "json_null" for row in hollow)

        # Duplicate category IDs survive in provider order.
        categories = connection.execute(
            """
            SELECT ki.categories
            FROM related_keywords_keyword_data AS kd
            JOIN related_keywords_keyword_info AS ki
              USING (capture_id, derivation_version_id, within_capture_identity)
            WHERE kd.keyword = %s AND kd.locus = %s
            """,
            (DUPLICATE_CATEGORY_KEYWORD, LOCUS_ITEM),
        ).fetchone()
        assert categories is not None
        assert categories[0] == DUPLICATE_CATEGORIES

        # Decimal-capable metrics keep exact NUMERIC values, never binary float.
        competition = connection.execute(
            """
            SELECT ki.competition, ki.cpc
            FROM related_keywords_keyword_data AS kd
            JOIN related_keywords_keyword_info AS ki
              USING (capture_id, derivation_version_id, within_capture_identity)
            WHERE kd.keyword = %s AND kd.locus = %s
            """,
            (SEED, LOCUS_ITEM),
        ).fetchone()
        assert competition is not None
        assert isinstance(competition[0], Decimal)
        assert isinstance(competition[1], Decimal)

        context = connection.execute(
            """
            SELECT requested_seed, result_seed_keyword, total_count, items_count,
                   seed_keyword_data_state, derived_returned_item_count,
                   derived_relationship_occurrence_count, attempt_id
            FROM related_keywords_result_context
            """
        ).fetchone()
        assert context == (SEED, SEED, 80, 80, "stated", 80, 477, attempt_id)


def test_rederiving_the_same_capture_is_exact_content_idempotent(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "idempotent")
    _commit(store, _fixture_body(), "22" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        first = derive_google_related_keywords(store, connection)
        connection.commit()
        before = _all_rk04_counts(connection)
        second = derive_google_related_keywords(store, connection)
        connection.commit()
        assert first == second
        assert _all_rk04_counts(connection) == before
        assert before[KEYWORD_DATA_TABLE] == GOLDEN_KEYWORD_DATA


def test_two_databases_are_logically_equivalent_across_all_twelve_relations(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "equivalence")
    _commit(store, _fixture_body(), "23" * 32)
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)

    def snapshot(dsn: str) -> tuple[Any, ...]:
        with connect(dsn) as connection:
            derive_google_related_keywords(store, connection)
            connection.commit()
            catalog: list[tuple[str, tuple[str, ...]]] = []
            parts: list[Any] = []
            for table in RK04_TABLES:
                columns, rows = _fetch_relation(connection, table)
                catalog.append((table, columns))
                parts.append(rows)
            assert tuple(name for name, _columns in catalog) == RK04_TABLES
            assert all(columns for _name, columns in catalog)
            assert all(rows for rows in parts)
        return (tuple(catalog), tuple(parts))

    assert snapshot(postgres_dsn) == snapshot(postgres_second_dsn)


def test_attempt_stage_outcome_exists_without_a_capture(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "unresolved")
    attempt = _attempt("24" * 32)
    attempt_id = store.commit_attempt(
        attempt, request_body=related_keywords_request_body_bytes(_params())
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_google_related_keywords(store, connection)
        connection.commit()
        assert summary.attempt_outcomes == 1
        assert summary.capture_outcomes == 0
        assert connection.execute(
            "SELECT attempt_id, capture_id, classification FROM outcomes"
        ).fetchall() == [(attempt_id, None, "authorized_unresolved")]
        assert _all_rk04_counts(connection) == dict.fromkeys(RK04_TABLES, 0)


def test_rejected_unit_leaves_zero_rows_in_every_rk04_relation(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "rejected")
    good = keyword_data("alpha", keyword_info=keyword_info(competition_level="LOW"))
    bad = keyword_data("alpha", keyword_info=keyword_info(competition_level="HIGH"))
    body = simple_body(
        [
            item("alpha", data=good),
            item("alpha", data=bad),
            item("beta", related=["alpha", "gamma"]),
        ]
    )
    _attempt_id, capture_id = _commit(store, body, "25" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_google_related_keywords(store, connection)
        connection.commit()
        assert summary.observations == 0
        assert connection.execute(
            "SELECT classification, observation_count FROM outcomes WHERE capture_id = %s",
            (capture_id,),
        ).fetchone() == ("provider_envelope_rejected", 0)
        assert _all_rk04_counts(connection) == dict.fromkeys(RK04_TABLES, 0)
        assert _count(connection, "observation_envelopes") == 0


def test_admitted_empty_writes_subject_bearing_context_and_nothing_else(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "empty")
    _attempt_id, capture_id = _commit(store, simple_body([], total_count=0), "26" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_related_keywords(store, connection)
        connection.commit()
        assert connection.execute(
            "SELECT classification, observation_count FROM outcomes WHERE capture_id = %s",
            (capture_id,),
        ).fetchone() == ("observation_admitted_empty", 0)
        counts = _all_rk04_counts(connection)
        assert counts[CONTEXT_TABLE] == 1
        assert all(
            counts[table] == 0 for table in RK04_TABLES if table != CONTEXT_TABLE
        )
        assert connection.execute(
            "SELECT requested_seed, items_count, seed_keyword_data_state"
            " FROM related_keywords_result_context"
        ).fetchone() == (SEED, 0, "absent")


@pytest.mark.parametrize(
    ("table", "extra"),
    [
        (
            ITEM_OCCURRENCES_TABLE,
            {"item_index": 99, "depth": 1, "item_se_type": "google",
             "related_keywords_state": "absent"},
        ),
        (MONTHLY_OCCURRENCES_TABLE, {"item_index": 99}),
        (
            RELATIONSHIP_OCCURRENCES_TABLE,
            {"source_item_index": 99, "target_index": 99, "source_depth": 1},
        ),
    ],
)
def test_planted_extra_occurrence_rows_fail_complete_set(
    derived: tuple[Any, EvidenceStore, str, str],
    table: str,
    extra: dict[str, object],
) -> None:
    connection, store, _attempt_id, capture_id = derived
    parent_table = {
        ITEM_OCCURRENCES_TABLE: KEYWORD_DATA_TABLE,
        MONTHLY_OCCURRENCES_TABLE: MONTHLY_TABLE,
        RELATIONSHIP_OCCURRENCES_TABLE: RELATIONSHIP_TABLE,
    }[table]
    identity, kind = connection.execute(
        sql.SQL(
            "SELECT within_capture_identity, observation_kind FROM {} LIMIT 1"
        ).format(sql.Identifier(parent_table))
    ).fetchone()
    values: dict[str, object] = {
        "capture_id": capture_id,
        "derivation_version_id": RELATED_KEYWORDS_RECIPE_ID,
        "within_capture_identity": identity,
        "observation_kind": kind,
        **extra,
    }
    columns = sorted(values)
    connection.execute(
        sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table),
            sql.SQL(", ").join(sql.Identifier(key) for key in columns),
            sql.SQL(", ").join(sql.Placeholder() for _ in columns),
        ),
        [values[key] for key in columns],
    )
    connection.commit()
    with pytest.raises(DerivationError, match="complete-set mismatch"):
        derive_google_related_keywords(store, connection)


def test_planted_extra_envelope_fails_complete_set(
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
            RELATED_KEYWORDS_RECIPE_ID,
            PROVIDER,
            RELATED_KEYWORDS_ADAPTER_CONTRACT,
            RELATIONSHIP_KIND,
            "cc" * 32,
        ),
    )
    connection.commit()
    with pytest.raises(DerivationError, match="complete-set mismatch: envelopes"):
        derive_google_related_keywords(store, connection)


def test_planted_foreign_attempt_outcome_fails_complete_set(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    """A second Outcome for this Capture and Recipe under a foreign Attempt is not valid.

    The complete-set contract is scoped to `(capture_id, derivation_version_id)`, so an extra
    Outcome row must fail even though it collides with nothing: `outcomes_identity` is UNIQUE
    on `(derivation_version_id, attempt_id, capture_id)` and a foreign `attempt_id` is a
    different key. Only the scoped complete-set assertion catches this.
    """

    connection, store, attempt_id, capture_id = derived
    foreign_attempt = "fe" * 32
    assert foreign_attempt != attempt_id
    accepted = connection.execute(
        """
        SELECT attempt_id, classification, observation_count FROM outcomes
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (RELATED_KEYWORDS_RECIPE_ID, capture_id),
    ).fetchall()
    assert len(accepted) == 1
    assert accepted[0][0] == attempt_id
    assert accepted[0][1] == "observation_admitted"
    admitted_count = int(accepted[0][2])
    assert admitted_count > 0

    # The planted row is a perfect copy apart from the Attempt, so nothing but the scoped
    # complete-set assertion can distinguish it.
    connection.execute(
        """
        INSERT INTO outcomes (
            attempt_id, capture_id, derivation_version_id,
            classification, observation_count
        ) VALUES (%s, %s, %s, %s, %s)
        """,
        (
            foreign_attempt,
            capture_id,
            RELATED_KEYWORDS_RECIPE_ID,
            "observation_admitted",
            admitted_count,
        ),
    )
    connection.commit()

    with pytest.raises(DerivationError, match="complete-set mismatch: outcome"):
        derive_google_related_keywords(store, connection)
    connection.rollback()

    # The planted row is not silently accepted: the contaminated set survives for the operator
    # to resolve, and the derivation refuses to certify it.
    after = connection.execute(
        """
        SELECT attempt_id FROM outcomes
        WHERE derivation_version_id = %s AND capture_id = %s
        ORDER BY attempt_id
        """,
        (RELATED_KEYWORDS_RECIPE_ID, capture_id),
    ).fetchall()
    assert sorted(row[0] for row in after) == sorted([attempt_id, foreign_attempt])

    # Removing the foreign Outcome restores an exactly-equal accepted set.
    connection.execute(
        "DELETE FROM outcomes WHERE derivation_version_id = %s AND capture_id = %s"
        " AND attempt_id = %s",
        (RELATED_KEYWORDS_RECIPE_ID, capture_id, foreign_attempt),
    )
    connection.commit()
    derive_google_related_keywords(store, connection)
    connection.commit()
    assert connection.execute(
        """
        SELECT attempt_id, classification, observation_count FROM outcomes
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (RELATED_KEYWORDS_RECIPE_ID, capture_id),
    ).fetchall() == accepted


def test_conflicting_stored_outcome_classification_fails_closed(
    derived: tuple[Any, EvidenceStore, str, str],
) -> None:
    connection, store, attempt_id, capture_id = derived
    connection.execute(
        "UPDATE outcomes SET classification = 'provider_error'"
        " WHERE derivation_version_id = %s AND capture_id = %s AND attempt_id = %s",
        (RELATED_KEYWORDS_RECIPE_ID, capture_id, attempt_id),
    )
    connection.commit()
    with pytest.raises(DerivationError, match="conflicting provider outcome"):
        derive_google_related_keywords(store, connection)
    connection.rollback()


def test_conflicting_stored_detail_content_fails_closed(
    derived: tuple[Any, EvidenceStore, str, str]
) -> None:
    connection, store, _attempt_id, _capture_id = derived
    connection.execute(
        "UPDATE related_keywords_keyword_info SET competition_level = 'TAMPERED'"
        " WHERE competition_level IS NOT NULL"
    )
    connection.commit()
    with pytest.raises(DerivationError, match="conflicting related_keywords_keyword_info"):
        derive_google_related_keywords(store, connection)


def test_missing_rebuildable_rows_are_restored_exactly(
    derived: tuple[Any, EvidenceStore, str, str]
) -> None:
    connection, store, _attempt_id, _capture_id = derived
    before = _all_rk04_counts(connection)
    connection.execute("DELETE FROM related_keywords_relationship_occurrences")
    connection.execute("DELETE FROM related_keywords_monthly_item_occurrences")
    connection.commit()
    derive_google_related_keywords(store, connection)
    connection.commit()
    assert _all_rk04_counts(connection) == before


def test_wrong_kind_child_rows_are_refused_by_postgresql(
    derived: tuple[Any, EvidenceStore, str, str]
) -> None:
    connection, store, _attempt_id, capture_id = derived
    identity = connection.execute(
        "SELECT within_capture_identity FROM related_keywords_keyword_data LIMIT 1"
    ).fetchone()[0]
    with pytest.raises(CheckViolation):
        connection.execute(
            """
            INSERT INTO related_keywords_keyword_info (
                capture_id, derivation_version_id, within_capture_identity,
                observation_kind, se_type_state,
                keyword_info_last_updated_time_state, competition_state,
                competition_level_state, cpc_state, search_volume_state,
                low_top_of_page_bid_state, high_top_of_page_bid_state,
                categories_state, monthly_searches_state, search_volume_trend_state,
                trend_monthly_state, trend_quarterly_state, trend_yearly_state
            ) VALUES (%s, %s, %s, %s, 'absent', 'absent', 'absent', 'absent',
                      'absent', 'absent', 'absent', 'absent', 'absent', 'absent',
                      'absent', 'absent', 'absent', 'absent')
            """,
            (capture_id, RELATED_KEYWORDS_RECIPE_ID, identity, MONTHLY_KIND),
        )
    connection.rollback()


def test_orphan_child_rows_are_refused_by_postgresql(
    derived: tuple[Any, EvidenceStore, str, str]
) -> None:
    connection, store, _attempt_id, capture_id = derived
    with pytest.raises(ForeignKeyViolation):
        connection.execute(
            """
            INSERT INTO related_keywords_keyword_properties (
                capture_id, derivation_version_id, within_capture_identity,
                observation_kind, se_type_state, core_keyword_state,
                synonym_clustering_algorithm_state, keyword_difficulty_state,
                detected_language_state, is_another_language_state
            ) VALUES (%s, %s, %s, %s, 'absent', 'absent', 'absent', 'absent',
                      'absent', 'absent')
            """,
            (capture_id, RELATED_KEYWORDS_RECIPE_ID, "dd" * 32, KEYWORD_DATA_KIND),
        )
    connection.rollback()


def test_state_value_consistency_is_enforced_by_postgresql(
    derived: tuple[Any, EvidenceStore, str, str]
) -> None:
    connection, store, _attempt_id, _capture_id = derived
    with pytest.raises(CheckViolation):
        connection.execute(
            "UPDATE related_keywords_keyword_info"
            " SET competition_level_state = 'json_null'"
            " WHERE competition_level IS NOT NULL"
        )
    connection.rollback()


def test_monthly_year_bound_is_the_parser_range_not_keyword_overview(
    derived: tuple[Any, EvidenceStore, str, str]
) -> None:
    connection, store, _attempt_id, _capture_id = derived
    definition = connection.execute(
        """
        SELECT pg_get_constraintdef(oid) FROM pg_constraint
        WHERE conrelid = 'related_keywords_monthly_search_volume'::regclass
          AND contype = 'c' AND pg_get_constraintdef(oid) LIKE '%%year%%'
        """
    ).fetchone()
    assert "9999" in definition[0]
    assert "2000" not in definition[0]
    assert "2100" not in definition[0]


def test_no_rk04_column_is_named_provider_update_time(
    derived: tuple[Any, EvidenceStore, str, str]
) -> None:
    connection, store, _attempt_id, _capture_id = derived
    columns = connection.execute(
        """
        SELECT table_name, column_name FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = ANY(%s)
          AND column_name = 'provider_update_time'
        """,
        (list(RK04_TABLES),),
    ).fetchall()
    assert columns == []


def test_populated_pre_rk04_schema_then_related_keywords_derive(
    tmp_path: Path, postgres_dsn: str
) -> None:
    joined = "\n".join(PRE_RK04_SCHEMA_STATEMENTS)
    assert "llm_mentions_historical_result_context" in joined
    assert "target_metrics_result_context" in joined
    assert "related_keywords_" not in joined
    with connect(postgres_dsn) as connection:
        for statement in PRE_RK04_SCHEMA_STATEMENTS:
            connection.execute(statement)
        connection.commit()
    apply_migrations(postgres_dsn)
    store = create_store(tmp_path / "upgraded")
    _commit(
        store,
        simple_body(
            [
                item(
                    "alpha",
                    data=keyword_data("alpha", keyword_info=keyword_info()),
                    related=["beta"],
                )
            ]
        ),
        "27" * 32,
    )
    with connect(postgres_dsn) as connection:
        summary = derive_google_related_keywords(store, connection)
        connection.commit()
        # one keyword-data + one monthly Data Period + one relationship
        assert summary.observations == 3
        assert _count(connection, KEYWORD_DATA_TABLE) == 1
        assert _count(connection, MONTHLY_TABLE) == 1
        assert _count(connection, RELATIONSHIP_TABLE) == 1


def test_unrelated_attempt_cannot_influence_another_captures_subject(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "two-subjects")
    first_attempt, first_capture = _commit(
        store, simple_body([item("alpha")]), "28" * 32, keyword=SEED, suffix="1"
    )
    second_attempt, second_capture = _commit(
        store,
        simple_body([item("beta")], seed_keyword="moon landing"),
        "29" * 32,
        keyword="moon landing",
        suffix="2",
    )
    assert first_attempt != second_attempt
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_google_related_keywords(store, connection)
        connection.commit()
        assert summary.attempt_outcomes == 2
        assert summary.capture_outcomes == 2
        assert summary.integrity_failures == 0
        rows = dict(
            connection.execute(
                "SELECT capture_id, requested_seed FROM related_keywords_result_context"
            ).fetchall()
        )
        assert rows == {first_capture: SEED, second_capture: "moon landing"}
        subjects = dict(
            connection.execute(
                "SELECT keyword, requested_seed FROM related_keywords_keyword_data"
            ).fetchall()
        )
        assert subjects == {"alpha": SEED, "beta": "moon landing"}
        provenance = connection.execute(
            "SELECT DISTINCT attempt_id FROM related_keywords_result_context"
            " WHERE capture_id = %s",
            (second_capture,),
        ).fetchall()
        assert provenance == [(second_attempt,)]


def test_attempt_validation_document_error_is_an_integrity_failure(
    tmp_path: Path, postgres_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = create_store(tmp_path / "bad-attempt")
    _commit(store, simple_body([item("alpha")]), "31" * 32)
    apply_migrations(postgres_dsn)

    def refuse(_value: object) -> dict[str, object]:
        raise DocumentError("synthetic attempt damage")

    monkeypatch.setattr(
        "observatory.google_related_keywords_derive."
        "validate_related_keywords_http_parameters",
        refuse,
    )
    with connect(postgres_dsn) as connection:
        summary = derive_google_related_keywords(store, connection)
        connection.commit()
        assert summary.integrity_failures == 1
        assert summary.capture_outcomes == 0
        assert summary.observations == 0
        # A separately verified Attempt-stage Outcome remains valid.
        assert summary.attempt_outcomes == 1
        assert _all_rk04_counts(connection) == dict.fromkeys(RK04_TABLES, 0)
        assert connection.execute(
            "SELECT classification FROM outcomes WHERE derivation_version_id = %s",
            (RELATED_KEYWORDS_RECIPE_ID,),
        ).fetchall() == [("authorized_unresolved",)]


def test_other_provider_adapters_are_skipped(tmp_path: Path, postgres_dsn: str) -> None:
    from observatory.capture import PUBLISHED_AR_INPUTS, capture_fixture

    store = create_store(tmp_path / "mixed")
    capture_fixture(store, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    _commit(store, simple_body([item("alpha")]), "32" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_google_related_keywords(store, connection)
        connection.commit()
        assert summary.attempt_outcomes == 1
        assert summary.capture_outcomes == 1
        assert summary.integrity_failures == 0
        assert _count(connection, KEYWORD_DATA_TABLE) == 1


def test_derive_requires_the_concrete_evidence_store(
    tmp_path: Path, postgres_dsn: str
) -> None:
    class Subclass(EvidenceStore):
        pass

    apply_migrations(postgres_dsn)
    store = create_store(tmp_path / "subclass")
    fake = Subclass.__new__(Subclass)
    fake.__dict__.update(store.__dict__)
    with (
        connect(postgres_dsn) as connection,
        pytest.raises(TypeError, match="concrete EvidenceStore"),
    ):
        derive_google_related_keywords(fake, connection)
