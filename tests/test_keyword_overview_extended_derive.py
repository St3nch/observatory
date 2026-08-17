"""PF-07: extended Keyword Overview Derivation into real PostgreSQL."""

from __future__ import annotations

import copy
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from psycopg.errors import CheckViolation, ForeignKeyViolation

from observatory.capture_event import (
    body_ref,
    paid_http_attempt_document,
    paid_http_capture_document,
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
    parse_keyword_overview,
)
from observatory.dataforseo_paid_probe import closed_paid_parameters, paid_request_body_bytes
from observatory.derive import DEFAULT_VERSION, DerivationError, derive
from observatory.evidence_store import create_store
from observatory.keyword_overview_derive import (
    derive_keyword_overview,
    derive_keyword_overview_extended,
)
from observatory.migrate import (
    KEYWORD_OVERVIEW_BACKLINKS_KIND,
    KEYWORD_OVERVIEW_INTENT_KIND,
    KEYWORD_OVERVIEW_MONTHLY_KIND,
    KEYWORD_OVERVIEW_PROPERTIES_KIND,
    KEYWORD_OVERVIEW_TREND_KIND,
    apply_migrations,
    connect,
)
from observatory.provider_recipe import (
    IDENTITY_SCHEMA,
    IDENTITY_VERSION,
    observation_identity,
)

FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_keyword_overview_pf03.json"
)
CORE_RECIPE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_keyword_overview_core_recipe.jcs"
)
EXTENDED_RECIPE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_keyword_overview_extended_recipe.jcs"
)
KEYWORDS = (
    "seo api",
    "keyword research",
    "local seo",
    "generative engine optimization",
    "ai search optimization",
)
ACCEPTED_CORE_ID = "319af798f3e0b3e5fe4579539442c4ca5d384b683e1f4bce0f7a1b3e26cd5908"
ACCEPTED_EXTENDED_ID = "cade41cb916bc5595f62ac8ea4ef73d6c688974a1ee5caad0c9d8f95f51664c7"
MONTHLY_COUNTS = {
    "ai search optimization": 85,
    "generative engine optimization": 78,
    "keyword research": 93,
    "local seo": 93,
    "seo api": 92,
}


def _body() -> bytes:
    return FIXTURE.read_bytes()


def _parameters() -> dict[str, object]:
    return closed_paid_parameters(keywords=list(KEYWORDS))


def _attempt(nonce: str) -> dict[str, object]:
    return paid_http_attempt_document(
        parameters=_parameters(),
        attempt_nonce=nonce,
        authorized_at="2026-08-16T21:37:00.000000Z",
        observatory_version="pf07-test-v1",
    )


def _complete_capture(
    attempt: dict[str, object], body: bytes, *, suffix: str = "1"
) -> dict[str, object]:
    return paid_http_capture_document(
        attempt=attempt,
        request_started_at=f"2026-08-16T21:37:0{suffix}.100000Z",
        transport_ended_at=f"2026-08-16T21:37:0{suffix}.400000Z",
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
        response_headers_at=f"2026-08-16T21:37:0{suffix}.200000Z",
        response_body_ended_at=f"2026-08-16T21:37:0{suffix}.300000Z",
    )


def _commit_complete(store: Any, body: bytes, nonce: str) -> tuple[str, str]:
    attempt = _attempt(nonce)
    request = paid_request_body_bytes(_parameters())
    attempt_id = store.commit_attempt(attempt, request_body=request)
    capture_id = store.commit_capture(_complete_capture(attempt, body), response_body=body)
    return attempt_id, capture_id


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


def _count(row: Any) -> int:
    assert row is not None
    return int(row[0])


def _monthly_identity(keyword: str, year: int, month: int) -> str:
    return observation_identity(
        {
            "axes": {"requested_keyword": keyword, "year": year, "month": month},
            "observation_kind": MONTHLY_KIND,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        EXTENDED_RECIPE,
    )


def _core_snapshot(connection: Any) -> tuple[object, ...]:
    return (
        connection.execute(
            """
            SELECT derivation_version_id, provider, adapter_contract,
                   recipe_canonical_bytes
            FROM provider_recipes
            WHERE derivation_version_id = %s
            """,
            (CORE_RECIPE_ID,),
        ).fetchall(),
        connection.execute(
            """
            SELECT attempt_id, capture_id, derivation_version_id,
                   classification, observation_count
            FROM outcomes
            WHERE derivation_version_id = %s
            ORDER BY attempt_id, capture_id NULLS FIRST
            """,
            (CORE_RECIPE_ID,),
        ).fetchall(),
        connection.execute(
            """
            SELECT capture_id, derivation_version_id, within_capture_identity,
                   observation_kind
            FROM observation_envelopes
            WHERE derivation_version_id = %s
            ORDER BY observation_kind, within_capture_identity
            """,
            (CORE_RECIPE_ID,),
        ).fetchall(),
        connection.execute(
            """
            SELECT capture_id, requested_keyword, covered,
                   returned_keyword, returned_keyword_state
            FROM keyword_overview_coverage
            WHERE derivation_version_id = %s
            ORDER BY requested_keyword
            """,
            (CORE_RECIPE_ID,),
        ).fetchall(),
        connection.execute(
            """
            SELECT capture_id, requested_keyword, search_volume, cpc,
                   provider_update_time
            FROM keyword_overview_metrics
            WHERE derivation_version_id = %s
            ORDER BY requested_keyword
            """,
            (CORE_RECIPE_ID,),
        ).fetchall(),
    )


def test_extended_recipe_is_not_the_core_recipe() -> None:
    assert CORE_RECIPE_ID == ACCEPTED_CORE_ID
    assert EXTENDED_RECIPE_ID == ACCEPTED_EXTENDED_ID
    assert EXTENDED_RECIPE_ID != CORE_RECIPE_ID
    from observatory.provider_recipe import recipe_bytes

    assert recipe_bytes(CORE_RECIPE) == CORE_RECIPE_PATH.read_bytes()
    assert len(CORE_RECIPE_PATH.read_bytes()) == 1662
    assert len(EXTENDED_RECIPE_PATH.read_bytes()) == 2554
    assert KEYWORD_OVERVIEW_MONTHLY_KIND == MONTHLY_KIND
    assert KEYWORD_OVERVIEW_TREND_KIND == TREND_KIND
    assert KEYWORD_OVERVIEW_PROPERTIES_KIND == PROPERTIES_KIND
    assert KEYWORD_OVERVIEW_BACKLINKS_KIND == BACKLINKS_KIND
    assert KEYWORD_OVERVIEW_INTENT_KIND == INTENT_KIND


def test_extended_derive_pf03_counts_and_zero_point(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_complete(store, _body(), "11" * 32)
    apply_migrations(postgres_dsn)
    parsed = parse_keyword_overview(_body(), _parameters())
    expected_monthly = {}
    for item in parsed.items:
        if not item.covered:
            continue
        info = item.keyword_info.value
        assert info is not None
        monthly = info.monthly_searches.value
        assert monthly is not None
        expected_monthly[item.requested_keyword] = len(monthly)
    assert expected_monthly == MONTHLY_COUNTS
    expected_total = 5 + 5 + sum(MONTHLY_COUNTS.values()) + 5 + 5 + 5 + 5
    with connect(postgres_dsn) as connection:
        summary = derive_keyword_overview_extended(store, connection)
        capture = connection.execute(
            """
            SELECT classification, observation_count, derivation_version_id
            FROM outcomes
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, EXTENDED_RECIPE_ID),
        ).fetchone()
        attempt = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE attempt_id = %s AND capture_id IS NULL
              AND derivation_version_id = %s
            """,
            (attempt_id, EXTENDED_RECIPE_ID),
        ).fetchone()
        counts = {
            kind: _count(
                connection.execute(
                    "SELECT count(*) FROM observation_envelopes WHERE observation_kind = %s",
                    (kind,),
                ).fetchone()
            )
            for kind in (
                COVERAGE_KIND,
                METRICS_KIND,
                MONTHLY_KIND,
                TREND_KIND,
                PROPERTIES_KIND,
                BACKLINKS_KIND,
                INTENT_KIND,
            )
        }
        monthly_by_keyword = connection.execute(
            """
            SELECT requested_keyword, count(*)
            FROM keyword_overview_monthly_search_volume
            GROUP BY requested_keyword
            ORDER BY requested_keyword
            """
        ).fetchall()
        zero = connection.execute(
            """
            SELECT search_volume, search_volume_state, year, month
            FROM keyword_overview_monthly_search_volume
            WHERE requested_keyword = 'ai search optimization'
              AND year = 2019 AND month = 6
            """
        ).fetchone()
        fixture_obs = connection.execute("SELECT count(*) FROM observations").fetchone()
    assert summary.derivation_version_id == ACCEPTED_EXTENDED_ID
    assert attempt == ("authorized_unresolved", 0)
    assert capture == ("observation_admitted", expected_total, EXTENDED_RECIPE_ID)
    assert summary.observations == expected_total
    assert counts == {
        COVERAGE_KIND: 5,
        METRICS_KIND: 5,
        MONTHLY_KIND: 441,
        TREND_KIND: 5,
        PROPERTIES_KIND: 5,
        BACKLINKS_KIND: 5,
        INTENT_KIND: 5,
    }
    assert dict(monthly_by_keyword) == MONTHLY_COUNTS
    assert zero == (0, "stated", 2019, 6)
    assert fixture_obs == (0,)


def test_monthly_identity_is_semantic_not_positional(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "22" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        row = connection.execute(
            """
            SELECT within_capture_identity
            FROM keyword_overview_monthly_search_volume
            WHERE requested_keyword = 'ai search optimization'
              AND year = 2019 AND month = 6
            """
        ).fetchone()
    assert row is not None
    assert row[0] == _monthly_identity("ai search optimization", 2019, 6)
    first = _monthly_identity("seo api", 2024, 1)
    second = _monthly_identity("seo api", 2024, 2)
    assert first != second
    assert first == _monthly_identity("seo api", 2024, 1)


def test_historical_revision_creates_second_capture_row(
    tmp_path: Path, postgres_dsn: str
) -> None:
    original = _body()
    document = _decoded(original)
    items = document["tasks"][0]["result"][0]["items"]
    target = next(item for item in items if item["keyword"] == "ai search optimization")
    revised_point = next(
        point
        for point in target["keyword_info"]["monthly_searches"]
        if point["year"] == 2019 and point["month"] == 6
    )
    assert revised_point["search_volume"] == 0
    revised_point["search_volume"] = 7
    later = _encode(document)
    first_store = create_store(tmp_path / "first")
    second_store = create_store(tmp_path / "second")
    first_attempt, first_capture = _commit_complete(first_store, original, "31" * 32)
    later_attempt, later_capture = _commit_complete(second_store, later, "32" * 32)
    assert first_capture != later_capture
    assert first_attempt != later_attempt
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(first_store, connection)
        derive_keyword_overview_extended(second_store, connection)
        rows = connection.execute(
            """
            SELECT capture_id, search_volume, within_capture_identity
            FROM keyword_overview_monthly_search_volume
            WHERE requested_keyword = 'ai search optimization'
              AND year = 2019 AND month = 6
            ORDER BY capture_id
            """
        ).fetchall()
    assert len(rows) == 2
    by_capture = {row[0]: row for row in rows}
    assert by_capture[first_capture][1] == 0
    assert by_capture[later_capture][1] == 7
    assert by_capture[first_capture][2] == by_capture[later_capture][2]
    assert by_capture[first_capture][2] == _monthly_identity(
        "ai search optimization", 2019, 6
    )


def test_trend_properties_backlinks_intent_and_independent_clocks(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "41" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        trend = connection.execute(
            """
            SELECT monthly, monthly_state, quarterly, quarterly_state,
                   yearly, yearly_state
            FROM keyword_overview_search_volume_trend
            WHERE requested_keyword = 'ai search optimization'
            """
        ).fetchone()
        props_seo = connection.execute(
            """
            SELECT detected_language, detected_language_state,
                   core_keyword, core_keyword_state, is_another_language
            FROM keyword_overview_properties
            WHERE requested_keyword = 'seo api'
            """
        ).fetchone()
        props_research = connection.execute(
            """
            SELECT core_keyword, core_keyword_state
            FROM keyword_overview_properties
            WHERE requested_keyword = 'keyword research'
            """
        ).fetchone()
        backlinks = connection.execute(
            """
            SELECT backlinks, dofollow, provider_update_time,
                   provider_update_time_state
            FROM keyword_overview_avg_backlinks
            WHERE requested_keyword = 'ai search optimization'
            """
        ).fetchone()
        intent_seo = connection.execute(
            """
            SELECT main_intent, foreign_intent, foreign_intent_state,
                   provider_update_time
            FROM keyword_overview_search_intent
            WHERE requested_keyword = 'seo api'
            """
        ).fetchone()
        intent_research = connection.execute(
            """
            SELECT foreign_intent, foreign_intent_state
            FROM keyword_overview_search_intent
            WHERE requested_keyword = 'keyword research'
            """
        ).fetchone()
        intent_ai = connection.execute(
            """
            SELECT provider_update_time
            FROM keyword_overview_search_intent
            WHERE requested_keyword = 'ai search optimization'
            """
        ).fetchone()
        metrics_put = connection.execute(
            """
            SELECT provider_update_time
            FROM keyword_overview_metrics
            WHERE requested_keyword = 'ai search optimization'
              AND derivation_version_id = %s
            """,
            (EXTENDED_RECIPE_ID,),
        ).fetchone()
    assert trend == (23, "stated", 0, "stated", 82, "stated")
    assert props_seo == ("id", "stated", None, "json_null", True)
    assert props_research == (None, "json_null")
    assert backlinks == (
        Decimal("1571.3"),
        Decimal("839.7"),
        "2026-08-01 07:28:00 +00:00",
        "stated",
    )
    assert intent_seo is not None
    assert intent_seo[0] == "commercial"
    assert list(intent_seo[1]) == ["informational"]
    assert intent_seo[2] == "stated"
    assert intent_research == (None, "json_null")
    assert intent_ai == ("2026-04-29 01:54:23 +00:00",)
    assert metrics_put == ("2026-07-16 07:54:24 +00:00",)
    assert metrics_put != backlinks[2:3]
    assert metrics_put != intent_ai
    assert backlinks[2:3] != intent_ai


def test_core_rows_remain_unchanged_after_extended_derive(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "51" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        core = derive_keyword_overview(store, connection)
        before = _core_snapshot(connection)
        extended = derive_keyword_overview_extended(store, connection)
        after = _core_snapshot(connection)
        recipes = {
            row[0]
            for row in connection.execute(
                "SELECT derivation_version_id FROM provider_recipes"
            ).fetchall()
        }
        core_outcome = connection.execute(
            """
            SELECT observation_count FROM outcomes
            WHERE capture_id IS NOT NULL AND derivation_version_id = %s
            """,
            (CORE_RECIPE_ID,),
        ).fetchone()
        extended_outcome = connection.execute(
            """
            SELECT observation_count FROM outcomes
            WHERE capture_id IS NOT NULL AND derivation_version_id = %s
            """,
            (EXTENDED_RECIPE_ID,),
        ).fetchone()
        extended_coverage = connection.execute(
            """
            SELECT count(*) FROM keyword_overview_coverage
            WHERE derivation_version_id = %s
            """,
            (EXTENDED_RECIPE_ID,),
        ).fetchone()
        extended_metrics = connection.execute(
            """
            SELECT count(*) FROM keyword_overview_metrics
            WHERE derivation_version_id = %s
            """,
            (EXTENDED_RECIPE_ID,),
        ).fetchone()
    assert core.derivation_version_id == ACCEPTED_CORE_ID
    assert extended.derivation_version_id == ACCEPTED_EXTENDED_ID
    assert before == after
    assert recipes == {CORE_RECIPE_ID, EXTENDED_RECIPE_ID}
    assert core_outcome == (10,)
    assert extended_outcome == (471,)
    assert extended_coverage == (5,)
    assert extended_metrics == (5,)
    assert core.observations == 10
    assert extended.observations == 471


def test_exact_content_idempotent_and_monthly_conflict(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "61" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        first = derive_keyword_overview_extended(store, connection)
        second = derive_keyword_overview_extended(store, connection)
        assert first == second
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE keyword_overview_monthly_search_volume
            SET search_volume = 99
            WHERE requested_keyword = 'ai search optimization'
              AND year = 2019 AND month = 6
            """
        )
        connection.commit()
        with pytest.raises(DerivationError, match="monthly"):
            derive_keyword_overview_extended(store, connection)


def test_wrong_kind_and_state_value_contradictions(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "71" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        coverage = connection.execute(
            """
            SELECT capture_id, derivation_version_id,
                   within_capture_identity, observation_kind
            FROM observation_envelopes
            WHERE observation_kind = %s
            LIMIT 1
            """,
            (COVERAGE_KIND,),
        ).fetchone()
        metrics = connection.execute(
            """
            SELECT capture_id, derivation_version_id,
                   within_capture_identity, observation_kind
            FROM observation_envelopes
            WHERE observation_kind = %s
            LIMIT 1
            """,
            (METRICS_KIND,),
        ).fetchone()
        assert coverage is not None and metrics is not None
        with pytest.raises((CheckViolation, ForeignKeyViolation)), connection.transaction():
            connection.execute(
                """
                INSERT INTO keyword_overview_monthly_search_volume (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, requested_keyword, year, month,
                    search_volume, search_volume_state
                )
                VALUES (%s, %s, %s, %s, 'seo api', 2024, 1, 1, 'stated')
                """,
                coverage,
            )
        with pytest.raises((CheckViolation, ForeignKeyViolation)), connection.transaction():
            connection.execute(
                """
                INSERT INTO keyword_overview_search_volume_trend (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, requested_keyword,
                    monthly, monthly_state, quarterly, quarterly_state,
                    yearly, yearly_state
                )
                VALUES (%s, %s, %s, %s, 'seo api', 1, 'stated', 1, 'stated', 1, 'stated')
                """,
                metrics,
            )
        with pytest.raises(CheckViolation), connection.transaction():
            connection.execute(
                """
                UPDATE keyword_overview_monthly_search_volume
                SET search_volume = NULL, search_volume_state = 'stated'
                WHERE requested_keyword = 'ai search optimization'
                  AND year = 2019 AND month = 6
                """
            )
        with pytest.raises(CheckViolation), connection.transaction():
            connection.execute(
                """
                UPDATE keyword_overview_monthly_search_volume
                SET search_volume = 1, search_volume_state = 'absent'
                WHERE requested_keyword = 'ai search optimization'
                  AND year = 2019 AND month = 6
                """
            )
        with pytest.raises(CheckViolation), connection.transaction():
            connection.execute(
                """
                UPDATE keyword_overview_properties
                SET core_keyword = NULL, core_keyword_state = 'stated'
                WHERE requested_keyword = 'local seo'
                """
            )
        with pytest.raises(CheckViolation), connection.transaction():
            connection.execute(
                """
                UPDATE keyword_overview_search_intent
                SET foreign_intent = ARRAY['informational'],
                    foreign_intent_state = 'json_null'
                WHERE requested_keyword = 'keyword research'
                """
            )
        connection.execute(
            """
            UPDATE keyword_overview_search_volume_trend
            SET monthly = -3, monthly_state = 'stated'
            WHERE requested_keyword = 'seo api'
            """
        )
        connection.execute(
            """
            UPDATE keyword_overview_search_intent
            SET foreign_intent = '{}', foreign_intent_state = 'stated'
            WHERE requested_keyword = 'local seo'
            """
        )
        trend = connection.execute(
            """
            SELECT monthly, monthly_state
            FROM keyword_overview_search_volume_trend
            WHERE requested_keyword = 'seo api'
            """
        ).fetchone()
        empty_intent = connection.execute(
            """
            SELECT foreign_intent, foreign_intent_state
            FROM keyword_overview_search_intent
            WHERE requested_keyword = 'local seo'
            """
        ).fetchone()
    assert trend == (-3, "stated")
    assert empty_intent is not None
    assert list(empty_intent[0]) == []
    assert empty_intent[1] == "stated"


def test_two_databases_are_logically_equivalent(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "81" * 32)
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)

    def snapshot(dsn: str) -> tuple[object, ...]:
        with connect(dsn) as connection:
            derive_keyword_overview_extended(store, connection)
            return (
                connection.execute(
                    """
                    SELECT derivation_version_id, classification, observation_count
                    FROM outcomes
                    ORDER BY derivation_version_id, capture_id NULLS FIRST
                    """
                ).fetchall(),
                connection.execute(
                    """
                    SELECT observation_kind, count(*)
                    FROM observation_envelopes
                    GROUP BY 1
                    ORDER BY 1
                    """
                ).fetchall(),
                connection.execute(
                    """
                    SELECT requested_keyword, year, month, search_volume
                    FROM keyword_overview_monthly_search_volume
                    ORDER BY requested_keyword, year, month
                    """
                ).fetchall(),
                connection.execute(
                    """
                    SELECT requested_keyword, monthly, quarterly, yearly
                    FROM keyword_overview_search_volume_trend
                    ORDER BY requested_keyword
                    """
                ).fetchall(),
                connection.execute(
                    """
                    SELECT requested_keyword, core_keyword, detected_language
                    FROM keyword_overview_properties
                    ORDER BY requested_keyword
                    """
                ).fetchall(),
                connection.execute(
                    """
                    SELECT requested_keyword, backlinks, provider_update_time
                    FROM keyword_overview_avg_backlinks
                    ORDER BY requested_keyword
                    """
                ).fetchall(),
                connection.execute(
                    """
                    SELECT requested_keyword, main_intent, foreign_intent,
                           provider_update_time
                    FROM keyword_overview_search_intent
                    ORDER BY requested_keyword
                    """
                ).fetchall(),
            )

    assert snapshot(postgres_dsn) == snapshot(postgres_second_dsn)


def test_backlink_integer_and_decimal_lexical_forms(
    tmp_path: Path, postgres_dsn: str
) -> None:
    as_int = _body().replace(b'"backlinks":1571.3', b'"backlinks":1571', 1)
    as_decimal = _body().replace(b'"backlinks":1571.3', b'"backlinks":1571.0', 1)
    apply_migrations(postgres_dsn)
    first = create_store(tmp_path / "int")
    second = create_store(tmp_path / "dec")
    _commit_complete(first, as_int, "b1" * 32)
    _commit_complete(second, as_decimal, "b2" * 32)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(first, connection)
        integer_value = connection.execute(
            """
            SELECT backlinks FROM keyword_overview_avg_backlinks
            WHERE requested_keyword = 'ai search optimization'
            """
        ).fetchone()
        connection.execute("DELETE FROM keyword_overview_search_intent")
        connection.execute("DELETE FROM keyword_overview_avg_backlinks")
        connection.execute("DELETE FROM keyword_overview_properties")
        connection.execute("DELETE FROM keyword_overview_search_volume_trend")
        connection.execute("DELETE FROM keyword_overview_monthly_search_volume")
        connection.execute("DELETE FROM keyword_overview_metrics")
        connection.execute("DELETE FROM keyword_overview_coverage")
        connection.execute("DELETE FROM observation_envelopes")
        connection.execute("DELETE FROM derivation_diagnostics")
        connection.execute("DELETE FROM outcomes")
        connection.commit()
        derive_keyword_overview_extended(second, connection)
        decimal_value = connection.execute(
            """
            SELECT backlinks FROM keyword_overview_avg_backlinks
            WHERE requested_keyword = 'ai search optimization'
            """
        ).fetchone()
    assert integer_value is not None and decimal_value is not None
    assert integer_value[0] == Decimal(1571)
    assert decimal_value[0] == Decimal("1571.0")
    assert integer_value[0] == decimal_value[0]


def test_extended_failure_and_damage_paths(
    tmp_path: Path, postgres_dsn: str
) -> None:
    apply_migrations(postgres_dsn)
    error_doc = _decoded()
    error_doc["tasks"][0]["status_code"] = 40102
    store = create_store(tmp_path / "error")
    _commit_complete(store, _encode(error_doc), "91" * 32)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        row = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE capture_id IS NOT NULL AND derivation_version_id = %s
            """,
            (EXTENDED_RECIPE_ID,),
        ).fetchone()
        envelopes = connection.execute(
            "SELECT count(*) FROM observation_envelopes WHERE derivation_version_id = %s",
            (EXTENDED_RECIPE_ID,),
        ).fetchone()
        connection.execute("DELETE FROM keyword_overview_search_intent")
        connection.execute("DELETE FROM keyword_overview_avg_backlinks")
        connection.execute("DELETE FROM keyword_overview_properties")
        connection.execute("DELETE FROM keyword_overview_search_volume_trend")
        connection.execute("DELETE FROM keyword_overview_monthly_search_volume")
        connection.execute("DELETE FROM keyword_overview_metrics")
        connection.execute("DELETE FROM keyword_overview_coverage")
        connection.execute("DELETE FROM observation_envelopes")
        connection.execute("DELETE FROM derivation_diagnostics")
        connection.execute("DELETE FROM outcomes")
        connection.commit()
    assert row == ("provider_error", 0)
    assert envelopes == (0,)

    rejected = _body().replace(b'"cost":0.0126', b'"cost":NaN', 1)
    reject_store = create_store(tmp_path / "rejected")
    _commit_complete(reject_store, rejected, "93" * 32)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(reject_store, connection)
        rejected_row = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE capture_id IS NOT NULL AND derivation_version_id = %s
            """,
            (EXTENDED_RECIPE_ID,),
        ).fetchone()
        connection.execute("DELETE FROM derivation_diagnostics")
        connection.execute("DELETE FROM outcomes")
        connection.commit()
    assert rejected_row == ("provider_envelope_rejected", 0)

    collision = _decoded()
    collision["tasks"][0]["result"][0]["items"].append(
        copy.deepcopy(collision["tasks"][0]["result"][0]["items"][0])
    )
    collision["tasks"][0]["result"][0]["items_count"] = 6
    collide_store = create_store(tmp_path / "collide")
    _commit_complete(collide_store, _encode(collision), "94" * 32)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(collide_store, connection)
        collide_row = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE capture_id IS NOT NULL AND derivation_version_id = %s
            """,
            (EXTENDED_RECIPE_ID,),
        ).fetchone()
        connection.execute("DELETE FROM derivation_diagnostics")
        connection.execute("DELETE FROM outcomes")
        connection.commit()
    assert collide_row == ("reconciliation_failed", 0)

    none_store = create_store(tmp_path / "none")
    none_attempt = _attempt("95" * 32)
    none_store.commit_attempt(none_attempt, request_body=paid_request_body_bytes(_parameters()))
    none_store.commit_capture(
        paid_http_capture_document(
            attempt=none_attempt,
            request_started_at="2026-08-16T21:37:01.100000Z",
            transport_ended_at="2026-08-16T21:37:01.400000Z",
            transport_state="no_response",
            response=None,
            transport_failure={"phase": "connect", "code": "timeout"},
            response_headers_at=None,
            response_body_ended_at=None,
        ),
        response_body=None,
    )
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(none_store, connection)
        none_row = connection.execute(
            """
            SELECT classification FROM outcomes
            WHERE capture_id IS NOT NULL AND derivation_version_id = %s
            """,
            (EXTENDED_RECIPE_ID,),
        ).fetchone()
        connection.execute("DELETE FROM outcomes")
        connection.commit()
    assert none_row == ("no_response",)

    damaged = create_store(tmp_path / "damaged")
    attempt_id, capture_id = _commit_complete(damaged, _body(), "92" * 32)
    manifest = damaged.capture_path(capture_id) / "capture.json"
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    with connect(postgres_dsn) as connection:
        summary = derive_keyword_overview_extended(damaged, connection)
        attempt_row = connection.execute(
            """
            SELECT classification FROM outcomes
            WHERE attempt_id = %s AND capture_id IS NULL
              AND derivation_version_id = %s
            """,
            (attempt_id, EXTENDED_RECIPE_ID),
        ).fetchone()
        capture_rows = connection.execute(
            "SELECT count(*) FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchone()
        envelopes = connection.execute("SELECT count(*) FROM observation_envelopes").fetchone()
    assert attempt_row == ("authorized_unresolved",)
    assert capture_rows == (0,)
    assert envelopes == (0,)
    assert summary.integrity_failures >= 1


def test_fixture_derive_still_skips_provider_rows(
    tmp_path: Path, postgres_dsn: str
) -> None:
    from observatory.capture import PUBLISHED_AR_INPUTS, capture_admitted_results

    store = create_store(tmp_path / "mixed")
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    _commit_complete(store, _body(), "a1" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
        assert connection.execute("SELECT count(*) FROM observation_envelopes").fetchone() == (
            0,
        )
        assert connection.execute(
            "SELECT count(*) FROM keyword_overview_monthly_search_volume"
        ).fetchone() == (0,)
        assert connection.execute("SELECT count(*) FROM observations").fetchone() == (2,)


def test_pf03_operator_evidence_readonly_when_present(postgres_dsn: str) -> None:
    root = Path("/home/chaz/.local/share/vedaops/observatory/pf03-paid-20260816T213724Z")
    if not root.is_dir():
        return
    from observatory.evidence_store import open_store

    store = open_store(root)
    attempt = store.read_attempt(
        "c0da493c3a44f1f60bc21d7afaab290e852dadafa8157386b79bd58ebec07462"
    )
    capture = store.read_capture(
        "b4fc36a7799b497d0d183a88449bf0a770ce741ec1f0d8eaade2d75c930154d5"
    )
    body = store.read_capture_body(
        "b4fc36a7799b497d0d183a88449bf0a770ce741ec1f0d8eaade2d75c930154d5"
    )
    assert attempt is not None and capture is not None and body is not None
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_keyword_overview_extended(store, connection)
        capture_row = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (
                "b4fc36a7799b497d0d183a88449bf0a770ce741ec1f0d8eaade2d75c930154d5",
                EXTENDED_RECIPE_ID,
            ),
        ).fetchone()
        counts = {
            name: _count(connection.execute(f"SELECT count(*) FROM {name}").fetchone())
            for name in (
                "keyword_overview_coverage",
                "keyword_overview_metrics",
                "keyword_overview_monthly_search_volume",
                "keyword_overview_search_volume_trend",
                "keyword_overview_properties",
                "keyword_overview_avg_backlinks",
                "keyword_overview_search_intent",
            )
        }
        monthly = dict(
            connection.execute(
                """
                SELECT requested_keyword, count(*)
                FROM keyword_overview_monthly_search_volume
                GROUP BY requested_keyword
                """
            ).fetchall()
        )
    assert summary.integrity_failures == 0
    assert capture_row == ("observation_admitted", 471)
    assert counts == {
        "keyword_overview_coverage": 5,
        "keyword_overview_metrics": 5,
        "keyword_overview_monthly_search_volume": 441,
        "keyword_overview_search_volume_trend": 5,
        "keyword_overview_properties": 5,
        "keyword_overview_avg_backlinks": 5,
        "keyword_overview_search_intent": 5,
    }
    assert monthly == MONTHLY_COUNTS
