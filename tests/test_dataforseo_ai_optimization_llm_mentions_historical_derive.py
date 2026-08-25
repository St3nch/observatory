"""AI-16: Historical provider Derivation into real PostgreSQL."""

from __future__ import annotations

import copy
import hashlib
import json
import socket
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from psycopg import sql
from psycopg.errors import CheckViolation, ForeignKeyViolation, UniqueViolation

from observatory.capture import PUBLISHED_AR_INPUTS, capture_fixture
from observatory.capture_event import (
    MENTIONS_ADAPTER_CONTRACT,
    ORGANIC_ADAPTER_CONTRACT,
    PAID_ADAPTER_CONTRACT,
    body_ref,
    historical_http_attempt_document,
    historical_http_capture_document,
)
from observatory.dataforseo_ai_optimization_llm_mentions_historical import (
    MONTHLY_KIND,
    PARSER_CONTRACT,
    PROVIDER,
    parse_historical,
)
from observatory.dataforseo_ai_optimization_llm_mentions_historical_paid_probe import (
    closed_historical_parameters,
    historical_request_body_bytes,
)
from observatory.dataforseo_ai_optimization_search_mentions import (
    SEARCH_MENTIONS_RECIPE,
    SEARCH_MENTIONS_RECIPE_ID,
)
from observatory.dataforseo_google_organic import (
    FEATURE_PRESENCE_KIND,
    GOOGLE_ORGANIC_RECIPE,
    GOOGLE_ORGANIC_RECIPE_ID,
)
from observatory.dataforseo_keyword_overview import CORE_RECIPE, CORE_RECIPE_ID, COVERAGE_KIND
from observatory.derive import DEFAULT_VERSION, DerivationError, derive
from observatory.evidence_store import EvidenceStore, create_store
from observatory.google_organic_derive import derive_google_organic
from observatory.keyword_overview_derive import derive_keyword_overview
from observatory.llm_mentions_historical_derive import (
    CONTEXT_TABLE,
    HISTORICAL_RECIPE,
    HISTORICAL_RECIPE_BYTES,
    HISTORICAL_RECIPE_ID,
    MONTHLY_TABLE,
    UNRETURNED_TABLE,
    derive_llm_mentions_historical,
    historical_recipe,
    plan_historical_capture,
)
from observatory.migrate import (
    PRE_AI05_SCHEMA_STATEMENTS,
    PRE_AI11_SCHEMA_STATEMENTS,
    PRE_AI16_SCHEMA_STATEMENTS,
    PRE_PF12_SCHEMA_STATEMENTS,
    SCHEMA_STATEMENTS,
    WIDEN_IJSON_COLUMNS_SQL,
    apply_migrations,
    apply_schema,
    connect,
)
from observatory.provider_recipe import (
    IDENTITY_SCHEMA,
    IDENTITY_VERSION,
    ObservationEnvelope,
    ProviderRecipeError,
    observation_identity,
    recipe_bytes,
    recipe_derivation_version_id,
    register_provider_recipe,
    validate_recipe,
    write_observation_envelope,
)
from observatory.search_mentions_derive import derive_search_mentions
from observatory.target_metrics_derive import (
    TARGET_METRICS_RECIPE,
    TARGET_METRICS_RECIPE_ID,
    derive_target_metrics,
)

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
MENTIONS_FIXTURE = (
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
DATE_FROM = "2025-08-01"
DATE_TO = "2026-07-31"
AI14_BODY_BYTES = 5246
AI14_BODY_SHA256 = "4419daf0b7076625129ab18c6bf3c83905b998c3b3332f2ba6d42c8879b50781"
TM_BODY_SHA256 = "7b6974704f73cff9687986a83ab14ba8ec942ccdbfde359ec7e8fde6bea8eee2"
MENTIONS_BODY_SHA256 = "8b3cd0fb0c9fa23c102696bfe6b7212396c0f7c110e9ca8ca5b8ee5af182e80a"
KO_BODY_SHA256 = "d91fdc7ab8acf429f0ff9c00bd7cdb725be1ba9585481af35d14f7c4e79a6d1c"
ORGANIC_BODY_SHA256 = "7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f"
IJSON_MAX = 9007199254740991
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
REQUESTED_PERIODS: tuple[tuple[int, int], ...] = (
    (2025, 8),
    (2025, 9),
    (2025, 10),
    (2025, 11),
    (2025, 12),
    (2026, 1),
    (2026, 2),
    (2026, 3),
    (2026, 4),
    (2026, 5),
    (2026, 6),
    (2026, 7),
)
AI16_TABLES = (
    MONTHLY_TABLE,
    CONTEXT_TABLE,
    UNRETURNED_TABLE,
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


def _parameters() -> dict[str, object]:
    return closed_historical_parameters()


def _attempt(nonce: str) -> dict[str, object]:
    return historical_http_attempt_document(
        parameters=_parameters(),
        attempt_nonce=nonce,
        authorized_at="2026-08-25T18:32:00.000000Z",
        observatory_version="ai16-test-v1",
    )


def _complete_capture(
    attempt: dict[str, object], body: bytes, *, suffix: str = "1"
) -> dict[str, object]:
    return historical_http_capture_document(
        attempt=attempt,
        request_started_at=f"2026-08-25T18:32:0{suffix}.100000Z",
        transport_ended_at=f"2026-08-25T18:32:0{suffix}.400000Z",
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
        response_headers_at=f"2026-08-25T18:32:0{suffix}.200000Z",
        response_body_ended_at=f"2026-08-25T18:32:0{suffix}.300000Z",
    )


def _commit_complete(
    store: Any, body: bytes, nonce: str
) -> tuple[str, str]:
    attempt = _attempt(nonce)
    request = historical_request_body_bytes(_parameters())
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


def _result(document: dict[str, Any]) -> dict[str, Any]:
    result = document["tasks"][0]["result"][0]
    assert isinstance(result, dict)
    return result


def _items(document: dict[str, Any]) -> list[Any]:
    rows = _result(document)["items"]
    assert isinstance(rows, list)
    return rows


def _complete_capture_dict() -> dict[str, object]:
    return {
        "transport_state": "response_complete",
        "response": {"completeness": "complete"},
    }


def _plan(body: bytes, parameters: dict[str, object] | None = None) -> Any:
    return plan_historical_capture(
        "a" * 64,
        "b" * 64,
        _complete_capture_dict(),
        parameters or _parameters(),
        body,
    )


def _second_recipe() -> dict[str, object]:
    document = copy.deepcopy(HISTORICAL_RECIPE)
    document["reconciliation"] = {"rule": "attempt_window_admit_all_returned_periods_v2"}
    return validate_recipe(document)


def _catalog_columns(connection: Any, table: str) -> tuple[str, ...]:
    rows = connection.execute(
        """
        SELECT a.attname
        FROM pg_attribute AS a
        JOIN pg_class AS c ON c.oid = a.attrelid
        JOIN pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname = current_schema()
          AND c.relname = %s
          AND a.attnum > 0
          AND NOT a.attisdropped
        ORDER BY a.attnum
        """,
        (table,),
    ).fetchall()
    return tuple(str(row[0]) for row in rows)


def _normalize_cell(value: object) -> object:
    if isinstance(value, list):
        return tuple(value)
    return value


def _fetch_relation(
    connection: Any, table: str
) -> tuple[tuple[str, ...], tuple[tuple[object, ...], ...]]:
    columns = _catalog_columns(connection, table)
    assert columns
    query = sql.SQL("SELECT {} FROM {} ORDER BY {}").format(
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
        sql.Identifier(table),
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
    )
    cursor = connection.execute(query)
    fetched = tuple(item[0] for item in cursor.description or ())
    assert fetched == columns
    rows = tuple(
        tuple(_normalize_cell(value) for value in row) for row in cursor.fetchall()
    )
    return columns, rows


def _historical_catalog(connection: Any) -> tuple[tuple[Any, ...], ...]:
    constraints = connection.execute(
        """
        SELECT c.relname, con.conname, con.contype, pg_get_constraintdef(con.oid)
        FROM pg_constraint AS con
        JOIN pg_class AS c ON c.oid = con.conrelid
        JOIN pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname = current_schema()
          AND c.relname LIKE 'llm_mentions_historical_%'
        ORDER BY 1, 2, 4
        """
    ).fetchall()
    columns = connection.execute(
        """
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name LIKE 'llm_mentions_historical_%'
        ORDER BY 1, 2
        """
    ).fetchall()
    return tuple(constraints), tuple(columns)


def _assert_no_facts(connection: Any) -> None:
    monthly = connection.execute(f"SELECT count(*) FROM {MONTHLY_TABLE}").fetchone()
    context = connection.execute(f"SELECT count(*) FROM {CONTEXT_TABLE}").fetchone()
    unreturned = connection.execute(f"SELECT count(*) FROM {UNRETURNED_TABLE}").fetchone()
    assert monthly == (0,)
    assert context == (0,)
    assert unreturned == (0,)


def test_accepted_recipe_and_fixture_identities_remain_unchanged() -> None:
    assert PROVIDER == "dataforseo"
    assert PARSER_CONTRACT == (
        "dataforseo-ai-optimization-llm-mentions-historical-live-parser-v1"
    )
    assert MONTHLY_KIND == (
        "dataforseo.google.ai_optimization.llm_mentions_historical.monthly.v1"
    )
    assert historical_recipe() == HISTORICAL_RECIPE
    assert recipe_bytes(historical_recipe()) == HISTORICAL_RECIPE_BYTES
    assert hashlib.sha256(HISTORICAL_RECIPE_BYTES).hexdigest() == HISTORICAL_RECIPE_ID
    assert recipe_derivation_version_id(historical_recipe()) == HISTORICAL_RECIPE_ID
    admission = HISTORICAL_RECIPE["admission"]
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
    assert HISTORICAL_RECIPE["reconciliation"] == {
        "rule": "attempt_window_admit_all_returned_periods"
    }
    assert HISTORICAL_RECIPE["observation_kinds"] == [MONTHLY_KIND]
    extension = HISTORICAL_RECIPE["extension_policy"]
    assert isinstance(extension, dict)
    assert extension["closed_objects"] == [
        "/",
        "/items",
        "/metrics",
        "/result",
        "/tasks",
        "/tasks/data",
    ]
    raw = _body()
    assert len(raw) == AI14_BODY_BYTES
    assert hashlib.sha256(raw).hexdigest() == AI14_BODY_SHA256
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert not raw.endswith(b"\n")
    assert hashlib.sha256(TM_FIXTURE.read_bytes()).hexdigest() == TM_BODY_SHA256
    assert hashlib.sha256(MENTIONS_FIXTURE.read_bytes()).hexdigest() == MENTIONS_BODY_SHA256
    assert hashlib.sha256(KO_FIXTURE.read_bytes()).hexdigest() == KO_BODY_SHA256
    assert hashlib.sha256(ORGANIC_FIXTURE.read_bytes()).hexdigest() == ORGANIC_BODY_SHA256
    assert Path("/home/chaz/.local/share/observatory").as_posix() not in str(FIXTURE)


def test_conflicting_recipe_bytes_are_refused(postgres_dsn: str) -> None:
    apply_migrations(postgres_dsn)
    conflicting = copy.deepcopy(HISTORICAL_RECIPE)
    conflicting["reconciliation"] = {"rule": "attempt_window_admit_all_returned_periods"}
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, HISTORICAL_RECIPE)
        connection.execute(
            """
            UPDATE provider_recipes
            SET recipe_canonical_bytes = %s
            WHERE derivation_version_id = %s
            """,
            (b"not-the-recipe", HISTORICAL_RECIPE_ID),
        )
        with pytest.raises(ProviderRecipeError, match="conflicting canonical bytes"):
            register_provider_recipe(connection, HISTORICAL_RECIPE)


def test_plan_frozen_fixture_has_exact_semantic_counts() -> None:
    parsed = parse_historical(_body(), _parameters())
    planned = _plan(_body())
    assert parsed.items is not None
    expected = len(parsed.items)
    assert planned.classification == "observation_admitted"
    assert planned.classification != "observation_admitted_empty"
    assert len(planned.envelopes) == expected
    assert expected == len(POINTS)
    assert planned.context is not None
    assert planned.context["items_count"] == expected
    assert planned.context["date_from"] == DATE_FROM
    assert planned.context["date_to"] == DATE_TO
    assert planned.context["requested_keyword"] == KEYWORD
    assert planned.unreturned == ()
    rows = planned.details[MONTHLY_TABLE]
    projected = [
        (row["year"], row["month"], row["mentions"], row["ai_search_volume"])
        for row in rows
    ]
    assert projected == list(POINTS)
    assert "provider_array_index" not in rows[0]
    assert "cost" not in planned.context
    assert "echo" not in planned.context


def test_plan_extra_dropped_mixed_empty_zero_and_dates() -> None:
    extra_doc = _decoded()
    extra = {"year": 2026, "month": 8, "metrics": {"mentions": 1, "ai_search_volume": 2}}
    _items(extra_doc).append(extra)
    _result(extra_doc)["items_count"] = 13
    extra_planned = _plan(_encode(extra_doc))
    assert extra_planned.classification == "observation_admitted"
    assert extra_planned.context is not None
    assert extra_planned.context["items_count"] == 13
    assert extra_planned.context["date_from"] == DATE_FROM
    assert extra_planned.context["date_to"] == DATE_TO
    assert extra_planned.unreturned == ()
    assert len(extra_planned.envelopes) == 13

    dropped_doc = _decoded()
    del _items(dropped_doc)[-1]
    _result(dropped_doc)["items_count"] = 11
    dropped_planned = _plan(_encode(dropped_doc))
    assert dropped_planned.classification == "observation_admitted"
    assert len(dropped_planned.envelopes) == 11
    assert {(row["year"], row["month"]) for row in dropped_planned.unreturned} == {(2025, 8)}

    mixed_doc = _decoded()
    del _items(mixed_doc)[-1]
    _items(mixed_doc).append(extra)
    _result(mixed_doc)["items_count"] = 12
    mixed_planned = _plan(_encode(mixed_doc))
    assert mixed_planned.classification == "observation_admitted"
    assert mixed_planned.context is not None
    assert mixed_planned.context["items_count"] == 12
    assert len(mixed_planned.envelopes) == 12
    assert {(row["year"], row["month"]) for row in mixed_planned.unreturned} == {(2025, 8)}
    mixed_periods = {(row["year"], row["month"]) for row in mixed_planned.details[MONTHLY_TABLE]}
    assert (2026, 8) in mixed_periods
    assert (2025, 8) not in mixed_periods

    empty_doc = _decoded()
    _result(empty_doc)["items"] = []
    _result(empty_doc)["items_count"] = 0
    empty_planned = _plan(_encode(empty_doc))
    assert empty_planned.classification == "observation_admitted_empty"
    assert empty_planned.envelopes == ()
    assert empty_planned.details[MONTHLY_TABLE] == ()
    assert empty_planned.context is not None
    assert empty_planned.context["items_count"] == 0
    assert {(row["year"], row["month"]) for row in empty_planned.unreturned} == set(
        REQUESTED_PERIODS
    )
    assert len(empty_planned.unreturned) == len(REQUESTED_PERIODS)

    zero_doc = _decoded()
    _items(zero_doc)[0]["metrics"]["mentions"] = 0
    _items(zero_doc)[0]["metrics"]["ai_search_volume"] = 0
    zero_planned = _plan(_encode(zero_doc))
    assert zero_planned.classification == "observation_admitted"
    assert zero_planned.unreturned == ()
    assert zero_planned.details[MONTHLY_TABLE][0]["mentions"] == 0
    assert zero_planned.details[MONTHLY_TABLE][0]["ai_search_volume"] == 0

    shuffled_doc = _decoded()
    rows = list(_items(shuffled_doc))
    rows.reverse()
    _result(shuffled_doc)["items"] = rows
    shuffled = _plan(_encode(shuffled_doc))
    original_ids = {item.within_capture_identity for item in extra_planned.envelopes}
    frozen_ids = {item.within_capture_identity for item in _plan(_body()).envelopes}
    shuffled_ids = {item.within_capture_identity for item in shuffled.envelopes}
    assert shuffled_ids == frozen_ids
    assert original_ids != frozen_ids
    shuffled_points = {
        (row["year"], row["month"], row["mentions"], row["ai_search_volume"])
        for row in shuffled.details[MONTHLY_TABLE]
    }
    assert shuffled_points == set(POINTS)

    inverted = dict(_parameters())
    inverted["date_from"] = "2026-07-31"
    inverted["date_to"] = "2025-08-01"
    assert _plan(_body(), inverted).classification == "provider_envelope_rejected"
    bad = dict(_parameters())
    bad["date_from"] = "2025-13-01"
    assert _plan(_body(), bad).classification == "provider_envelope_rejected"
    empty_keyword = dict(_parameters())
    target = empty_keyword["target"]
    assert isinstance(target, list)
    first = dict(target[0])
    first["keyword"] = ""
    empty_keyword["target"] = [first]
    assert _plan(_body(), empty_keyword).classification == "provider_envelope_rejected"
    overflow = _decoded()
    _items(overflow)[0]["metrics"]["mentions"] = IJSON_MAX + 1
    overflow_planned = _plan(_encode(overflow))
    assert overflow_planned.classification == "provider_envelope_rejected"
    assert overflow_planned.context is None
    assert overflow_planned.unreturned == ()


def test_plan_echo_disagreement_keeps_attempt_window() -> None:
    document = _decoded()
    document["tasks"][0]["data"]["date_from"] = "2024-01-01"
    document["tasks"][0]["data"]["date_to"] = "2024-12-31"
    document["tasks"][0]["data"]["target"][0]["keyword"] = "echo keyword"
    planned = _plan(_encode(document))
    assert planned.classification == "observation_admitted"
    assert planned.context is not None
    assert planned.context["requested_keyword"] == KEYWORD
    assert planned.context["date_from"] == DATE_FROM
    assert planned.context["date_to"] == DATE_TO


def test_derive_rejects_non_concrete_store_before_schema_or_evidence() -> None:
    class DuckStore:
        def __getattr__(self, name: str) -> object:
            raise AssertionError(f"Evidence read before concrete-store check: {name}")

    class PoisonedConnection:
        def __getattr__(self, name: str) -> object:
            raise AssertionError(f"connection used before concrete-store check: {name}")

    with pytest.raises(TypeError, match="concrete EvidenceStore"):
        derive_llm_mentions_historical(DuckStore(), PoisonedConnection())  # type: ignore[arg-type]


def test_derive_ai14_fixture_into_real_postgres(tmp_path: Path, postgres_dsn: str) -> None:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_complete(store, _body(), "11" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_llm_mentions_historical(store, connection)
        outcome = connection.execute(
            """
            SELECT classification, observation_count, attempt_id
            FROM outcomes WHERE capture_id = %s
            """,
            (capture_id,),
        ).fetchone()
        envelopes = connection.execute(
            "SELECT count(*) FROM observation_envelopes WHERE capture_id = %s",
            (capture_id,),
        ).fetchone()
        monthly = connection.execute(
            f"""
            SELECT year, month, mentions, ai_search_volume
            FROM {MONTHLY_TABLE}
            ORDER BY year DESC, month DESC
            """
        ).fetchall()
        context = connection.execute(
            f"""
            SELECT requested_keyword, date_from, date_to, platform, location_code,
                   language_code, match_type, search_filter, search_scope, items_count,
                   attempt_id
            FROM {CONTEXT_TABLE}
            """
        ).fetchone()
        unreturned = connection.execute(f"SELECT count(*) FROM {UNRETURNED_TABLE}").fetchone()
        columns = _catalog_columns(connection, MONTHLY_TABLE)
    assert summary.observations == len(POINTS)
    assert outcome == ("observation_admitted", len(POINTS), attempt_id)
    assert envelopes == (len(POINTS),)
    assert tuple((int(row[0]), int(row[1]), int(row[2]), int(row[3])) for row in monthly) == POINTS
    assert context == (
        KEYWORD,
        DATE_FROM,
        DATE_TO,
        "google",
        2840,
        "en",
        "word_match",
        "include",
        ["answer"],
        12,
        attempt_id,
    )
    assert unreturned == (0,)
    assert "provider_array_index" not in columns
    assert summary.derivation_version_id == HISTORICAL_RECIPE_ID


def test_adversarial_bodies_persist_on_postgres(tmp_path: Path, postgres_dsn: str) -> None:
    apply_migrations(postgres_dsn)
    extra_doc = _decoded()
    extra = {"year": 2026, "month": 8, "metrics": {"mentions": 1, "ai_search_volume": 2}}
    _items(extra_doc).append(extra)
    _result(extra_doc)["items_count"] = 13
    extra_store = create_store(tmp_path / "extra")
    _commit_complete(extra_store, _encode(extra_doc), "12" * 32)

    dropped_doc = _decoded()
    del _items(dropped_doc)[-1]
    _result(dropped_doc)["items_count"] = 11
    dropped_store = create_store(tmp_path / "dropped")
    _commit_complete(dropped_store, _encode(dropped_doc), "13" * 32)

    mixed_doc = _decoded()
    del _items(mixed_doc)[-1]
    _items(mixed_doc).append(extra)
    _result(mixed_doc)["items_count"] = 12
    mixed_store = create_store(tmp_path / "mixed")
    _commit_complete(mixed_store, _encode(mixed_doc), "14" * 32)

    empty_doc = _decoded()
    _result(empty_doc)["items"] = []
    _result(empty_doc)["items_count"] = 0
    empty_store = create_store(tmp_path / "empty")
    _commit_complete(empty_store, _encode(empty_doc), "15" * 32)

    zero_doc = _decoded()
    _items(zero_doc)[0]["metrics"]["mentions"] = 0
    _items(zero_doc)[0]["metrics"]["ai_search_volume"] = 0
    zero_store = create_store(tmp_path / "zero")
    _commit_complete(zero_store, _encode(zero_doc), "16" * 32)

    with connect(postgres_dsn) as connection:
        derive_llm_mentions_historical(extra_store, connection)
        extra_count = connection.execute(f"SELECT count(*) FROM {MONTHLY_TABLE}").fetchone()
        extra_unreturned = connection.execute(f"SELECT count(*) FROM {UNRETURNED_TABLE}").fetchone()
        extra_items = connection.execute(f"SELECT items_count FROM {CONTEXT_TABLE}").fetchone()
        extra_period = connection.execute(
            f"SELECT year, month FROM {MONTHLY_TABLE} WHERE year = 2026 AND month = 8"
        ).fetchone()
        connection.execute(f"DELETE FROM {UNRETURNED_TABLE}")
        connection.execute(f"DELETE FROM {MONTHLY_TABLE}")
        connection.execute(f"DELETE FROM {CONTEXT_TABLE}")
        connection.execute("DELETE FROM observation_envelopes")
        connection.execute("DELETE FROM outcomes")
        connection.commit()

        derive_llm_mentions_historical(dropped_store, connection)
        dropped_unreturned = connection.execute(
            f"SELECT year, month FROM {UNRETURNED_TABLE}"
        ).fetchall()
        dropped_count = connection.execute(f"SELECT count(*) FROM {MONTHLY_TABLE}").fetchone()
        connection.execute(f"DELETE FROM {UNRETURNED_TABLE}")
        connection.execute(f"DELETE FROM {MONTHLY_TABLE}")
        connection.execute(f"DELETE FROM {CONTEXT_TABLE}")
        connection.execute("DELETE FROM observation_envelopes")
        connection.execute("DELETE FROM outcomes")
        connection.commit()

        derive_llm_mentions_historical(mixed_store, connection)
        mixed_unreturned = connection.execute(
            f"SELECT year, month FROM {UNRETURNED_TABLE}"
        ).fetchall()
        mixed_extra = connection.execute(
            f"SELECT count(*) FROM {MONTHLY_TABLE} WHERE year = 2026 AND month = 8"
        ).fetchone()
        mixed_missing = connection.execute(
            f"SELECT count(*) FROM {MONTHLY_TABLE} WHERE year = 2025 AND month = 8"
        ).fetchone()
        connection.execute(f"DELETE FROM {UNRETURNED_TABLE}")
        connection.execute(f"DELETE FROM {MONTHLY_TABLE}")
        connection.execute(f"DELETE FROM {CONTEXT_TABLE}")
        connection.execute("DELETE FROM observation_envelopes")
        connection.execute("DELETE FROM outcomes")
        connection.commit()

        derive_llm_mentions_historical(empty_store, connection)
        empty_outcome = connection.execute(
            "SELECT classification, observation_count FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchone()
        empty_monthly = connection.execute(f"SELECT count(*) FROM {MONTHLY_TABLE}").fetchone()
        empty_unreturned = connection.execute(
            f"SELECT year, month FROM {UNRETURNED_TABLE} ORDER BY year, month"
        ).fetchall()
        connection.execute(f"DELETE FROM {UNRETURNED_TABLE}")
        connection.execute(f"DELETE FROM {MONTHLY_TABLE}")
        connection.execute(f"DELETE FROM {CONTEXT_TABLE}")
        connection.execute("DELETE FROM observation_envelopes")
        connection.execute("DELETE FROM outcomes")
        connection.commit()

        derive_llm_mentions_historical(zero_store, connection)
        zero_row = connection.execute(
            f"""
            SELECT mentions, ai_search_volume FROM {MONTHLY_TABLE}
            WHERE year = 2026 AND month = 7
            """
        ).fetchone()
        zero_unreturned = connection.execute(f"SELECT count(*) FROM {UNRETURNED_TABLE}").fetchone()
    assert extra_count == (13,)
    assert extra_unreturned == (0,)
    assert extra_items == (13,)
    assert extra_period == (2026, 8)
    assert dropped_count == (11,)
    assert dropped_unreturned == [(2025, 8)]
    assert mixed_unreturned == [(2025, 8)]
    assert mixed_extra == (1,)
    assert mixed_missing == (0,)
    assert empty_outcome == ("observation_admitted_empty", 0)
    assert empty_monthly == (0,)
    assert tuple((int(row[0]), int(row[1])) for row in empty_unreturned) == REQUESTED_PERIODS
    assert zero_row == (0, 0)
    assert zero_unreturned == (0,)


def test_transport_parse_and_damage_paths_write_zero_unreturned(
    tmp_path: Path, postgres_dsn: str
) -> None:
    apply_migrations(postgres_dsn)
    request = historical_request_body_bytes(_parameters())
    no_response = create_store(tmp_path / "no-response")
    attempt = _attempt("21" * 32)
    no_response.commit_attempt(attempt, request_body=request)
    no_response.commit_capture(
        historical_http_capture_document(
            attempt=attempt,
            request_started_at="2026-08-25T18:32:01.100000Z",
            transport_ended_at="2026-08-25T18:32:01.400000Z",
            transport_state="no_response",
            response=None,
            transport_failure={"phase": "connect", "code": "timeout"},
            response_headers_at=None,
            response_body_ended_at=None,
        ),
        response_body=None,
    )
    with connect(postgres_dsn) as connection:
        derive_llm_mentions_historical(no_response, connection)
        row = connection.execute(
            "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchone()
        _assert_no_facts(connection)
    assert row == ("no_response",)

    empty_body = create_store(tmp_path / "empty-body")
    empty_attempt = _attempt("22" * 32)
    empty_bytes = b""
    empty_body.commit_attempt(empty_attempt, request_body=request)
    empty_body.commit_capture(
        historical_http_capture_document(
            attempt=empty_attempt,
            request_started_at="2026-08-25T18:32:03.100000Z",
            transport_ended_at="2026-08-25T18:32:03.400000Z",
            transport_state="response_complete",
            response={
                "status": 200,
                "http_version": "HTTP/1.1",
                "header_policy": "http-headers-v1",
                "headers": [["content-type", "application/json"]],
                "omitted_headers": [],
                "body": {"state": "present_zero_bytes", "body": body_ref(empty_bytes)},
                "completeness": "complete",
            },
            transport_failure=None,
            response_headers_at="2026-08-25T18:32:03.200000Z",
            response_body_ended_at="2026-08-25T18:32:03.300000Z",
        ),
        response_body=empty_bytes,
    )
    with connect(postgres_dsn) as connection:
        derive_llm_mentions_historical(empty_body, connection)
        classes = {
            item[0]
            for item in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
        _assert_no_facts(connection)
    assert "transport_complete_non_admissible" in classes

    partial = create_store(tmp_path / "partial")
    partial_attempt = _attempt("23" * 32)
    chunk = _body()[:32]
    partial.commit_attempt(partial_attempt, request_body=request)
    partial.commit_capture(
        historical_http_capture_document(
            attempt=partial_attempt,
            request_started_at="2026-08-25T18:32:02.100000Z",
            transport_ended_at="2026-08-25T18:32:02.400000Z",
            transport_state="response_partial",
            response={
                "status": 200,
                "http_version": "HTTP/1.1",
                "header_policy": "http-headers-v1",
                "headers": [["content-type", "application/json"]],
                "omitted_headers": [],
                "body": {"state": "present_nonempty", "body": body_ref(chunk)},
                "completeness": "partial",
            },
            transport_failure={"phase": "receive_body", "code": "timeout"},
            response_headers_at="2026-08-25T18:32:02.200000Z",
            response_body_ended_at="2026-08-25T18:32:02.300000Z",
        ),
        response_body=chunk,
    )
    with connect(postgres_dsn) as connection:
        derive_llm_mentions_historical(partial, connection)
        classes = {
            item[0]
            for item in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
        _assert_no_facts(connection)
    assert "response_partial" in classes

    error_doc = _decoded()
    error_doc["status_code"] = 40100
    error_doc["tasks"][0]["status_code"] = 40100
    error_doc["tasks_error"] = 1
    error_doc["tasks"][0]["result_count"] = 9
    error_doc["tasks"][0]["result"] = [{"items": None, "strange": True}]
    error_store = create_store(tmp_path / "provider-error")
    _commit_complete(error_store, _encode(error_doc), "25" * 32)
    with connect(postgres_dsn) as connection:
        derive_llm_mentions_historical(error_store, connection)
        classes = {
            row[0]
            for row in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
        _assert_no_facts(connection)
    assert "provider_error" in classes

    bad_doc = _decoded()
    _result(bad_doc)["unknown"] = True
    bad_store = create_store(tmp_path / "envelope")
    _commit_complete(bad_store, _encode(bad_doc), "26" * 32)
    with connect(postgres_dsn) as connection:
        derive_llm_mentions_historical(bad_store, connection)
        classes = {
            row[0]
            for row in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
        _assert_no_facts(connection)
    assert "provider_envelope_rejected" in classes

    overflow = _decoded()
    _items(overflow)[0]["metrics"]["mentions"] = IJSON_MAX + 1
    overflow_store = create_store(tmp_path / "overflow")
    _commit_complete(overflow_store, _encode(overflow), "27" * 32)
    with connect(postgres_dsn) as connection:
        derive_llm_mentions_historical(overflow_store, connection)
        classes = {
            row[0]
            for row in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
        _assert_no_facts(connection)
    assert "provider_envelope_rejected" in classes

    damaged = create_store(tmp_path / "damaged")
    attempt_id, capture_id = _commit_complete(damaged, _body(), "28" * 32)
    body_path = damaged.capture_path(capture_id) / "response.body"
    flipped = bytearray(body_path.read_bytes())
    flipped[0] ^= 0x01
    body_path.write_bytes(bytes(flipped))
    with connect(postgres_dsn) as connection:
        summary = derive_llm_mentions_historical(damaged, connection)
        attempt_row = connection.execute(
            """
            SELECT classification FROM outcomes
            WHERE attempt_id = %s AND capture_id IS NULL
            """,
            (attempt_id,),
        ).fetchone()
        capture_rows = connection.execute(
            "SELECT count(*) FROM outcomes WHERE capture_id = %s",
            (capture_id,),
        ).fetchone()
        _assert_no_facts(connection)
    assert attempt_row == ("authorized_unresolved",)
    assert capture_rows == (0,)
    assert summary.integrity_failures >= 1


def test_production_uses_cited_attempt_not_sibling(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "two-attempts")
    attempt_a = _attempt("31" * 32)
    attempt_b = _attempt("32" * 32)
    request = historical_request_body_bytes(_parameters())
    id_a = store.commit_attempt(attempt_a, request_body=request)
    id_b = store.commit_attempt(attempt_b, request_body=request)
    store.commit_capture(_complete_capture(attempt_a, _body()), response_body=_body())
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_llm_mentions_historical(store, connection)
        context = connection.execute(
            f"SELECT requested_keyword, attempt_id FROM {CONTEXT_TABLE}"
        ).fetchone()
        attempts = connection.execute(
            """
            SELECT attempt_id FROM outcomes
            WHERE capture_id IS NULL ORDER BY attempt_id
            """
        ).fetchall()
        capture_attempt = connection.execute(
            "SELECT attempt_id FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchone()
    assert summary.observations == len(POINTS)
    assert context == (KEYWORD, id_a)
    assert (id_a,) in attempts
    assert (id_b,) in attempts
    assert capture_attempt == (id_a,)


def test_validator_non_mapping_and_changed_keyword_are_integrity_failures(
    tmp_path: Path, postgres_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    apply_migrations(postgres_dsn)
    store = create_store(tmp_path / "integrity")
    attempt_id, capture_id = _commit_complete(store, _body(), "33" * 32)
    original = store.read_attempt

    def mutated_keyword(attempt_key: str) -> dict[str, object] | None:
        document = original(attempt_key)
        assert document is not None
        copied = dict(document)
        raw_params = copied["parameters"]
        assert isinstance(raw_params, dict)
        params = dict(raw_params)
        target = list(params["target"])
        first = dict(target[0])
        first["keyword"] = "other keyword"
        params["target"] = [first]
        copied["parameters"] = params
        return copied

    monkeypatch.setattr(store, "read_attempt", mutated_keyword)
    with connect(postgres_dsn) as connection:
        summary = derive_llm_mentions_historical(store, connection)
        capture_rows = connection.execute(
            "SELECT count(*) FROM outcomes WHERE capture_id = %s",
            (capture_id,),
        ).fetchone()
        _assert_no_facts(connection)
    assert summary.integrity_failures >= 1
    assert capture_rows == (0,)

    def mutated_empty_keyword(attempt_key: str) -> dict[str, object] | None:
        document = original(attempt_key)
        assert document is not None
        copied = dict(document)
        raw_params = copied["parameters"]
        assert isinstance(raw_params, dict)
        params = dict(raw_params)
        target = list(params["target"])
        first = dict(target[0])
        first["keyword"] = ""
        params["target"] = [first]
        copied["parameters"] = params
        return copied

    monkeypatch.setattr(store, "read_attempt", mutated_empty_keyword)
    with connect(postgres_dsn) as connection:
        summary = derive_llm_mentions_historical(store, connection)
        capture_rows = connection.execute(
            "SELECT count(*) FROM outcomes WHERE capture_id = %s",
            (capture_id,),
        ).fetchone()
        _assert_no_facts(connection)
    assert summary.integrity_failures >= 1
    assert capture_rows == (0,)

    def mutated_mapping(attempt_key: str) -> dict[str, object] | None:
        document = original(attempt_key)
        assert document is not None
        copied = dict(document)
        copied["parameters"] = "not-a-mapping"
        return copied

    monkeypatch.setattr(store, "read_attempt", mutated_mapping)
    with connect(postgres_dsn) as connection:
        summary = derive_llm_mentions_historical(store, connection)
        capture_rows = connection.execute(
            "SELECT count(*) FROM outcomes WHERE capture_id = %s",
            (capture_id,),
        ).fetchone()
        _assert_no_facts(connection)
    assert summary.integrity_failures >= 1
    assert capture_rows == (0,)

    def mutated_adapter(attempt_key: str) -> dict[str, object] | None:
        document = original(attempt_key)
        assert document is not None
        copied = dict(document)
        copied["adapter_contract"] = MENTIONS_ADAPTER_CONTRACT
        return copied

    monkeypatch.setattr(store, "read_attempt", mutated_adapter)
    with connect(postgres_dsn) as connection:
        summary = derive_llm_mentions_historical(store, connection)
        capture_rows = connection.execute(
            "SELECT count(*) FROM outcomes WHERE capture_id = %s",
            (capture_id,),
        ).fetchone()
        _assert_no_facts(connection)
    assert type(store) is EvidenceStore
    assert summary.integrity_failures >= 1
    assert capture_rows == (0,)
    assert attempt_id


def test_exact_content_extra_rows_missing_restore_and_wrong_unreturned(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_complete(store, _body(), "34" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        first = derive_llm_mentions_historical(store, connection)
        second = derive_llm_mentions_historical(store, connection)
        assert first == second
        original = connection.execute(
            f"SELECT mentions FROM {MONTHLY_TABLE} WHERE year = 2026 AND month = 7"
        ).fetchone()
        assert original is not None
        connection.execute(
            f"UPDATE {MONTHLY_TABLE} SET mentions = 1 WHERE year = 2026 AND month = 7"
        )
        connection.commit()
        with pytest.raises(DerivationError, match="conflicting"):
            derive_llm_mentions_historical(store, connection)
        connection.rollback()
        connection.execute(
            f"UPDATE {MONTHLY_TABLE} SET mentions = %s WHERE year = 2026 AND month = 7",
            (original[0],),
        )
        connection.commit()
        extra_identity = "ab" * 32
        connection.execute(
            """
            INSERT INTO observation_envelopes (
                capture_id, attempt_id, derivation_version_id, provider,
                adapter_contract, observation_kind, within_capture_identity
            )
            SELECT capture_id, attempt_id, derivation_version_id, provider,
                   adapter_contract, observation_kind, %s
            FROM observation_envelopes
            LIMIT 1
            """,
            (extra_identity,),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch"):
            derive_llm_mentions_historical(store, connection)
        connection.rollback()
        connection.execute(
            "DELETE FROM observation_envelopes WHERE within_capture_identity = %s",
            (extra_identity,),
        )
        connection.commit()
        connection.execute(f"DELETE FROM {MONTHLY_TABLE} WHERE year = 2025 AND month = 8")
        connection.execute(
            "DELETE FROM observation_envelopes WHERE within_capture_identity = %s",
            (
                observation_identity(
                    {
                        "axes": {
                            "requested_keyword": KEYWORD,
                            "year": 2025,
                            "month": 8,
                        },
                        "observation_kind": MONTHLY_KIND,
                        "schema": IDENTITY_SCHEMA,
                        "version": IDENTITY_VERSION,
                    },
                    HISTORICAL_RECIPE,
                ),
            ),
        )
        connection.commit()
        restored = derive_llm_mentions_historical(store, connection)
        restored_count = connection.execute(f"SELECT count(*) FROM {MONTHLY_TABLE}").fetchone()
        connection.execute(
            f"""
            INSERT INTO {UNRETURNED_TABLE} (capture_id, derivation_version_id, year, month)
            VALUES (%s, %s, 2024, 1)
            """,
            (capture_id, HISTORICAL_RECIPE_ID),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch: unreturned"):
            derive_llm_mentions_historical(store, connection)
        connection.rollback()
        connection.execute(
            f"DELETE FROM {UNRETURNED_TABLE} WHERE year = 2024 AND month = 1"
        )
        connection.commit()
        dropped_doc = _decoded()
        del _items(dropped_doc)[-1]
        _result(dropped_doc)["items_count"] = 11
        dropped_store = create_store(tmp_path / "swap")
        dropped_attempt, dropped_capture = _commit_complete(
            dropped_store, _encode(dropped_doc), "35" * 32
        )
        derive_llm_mentions_historical(dropped_store, connection)
        connection.execute(
            f"""
            DELETE FROM {UNRETURNED_TABLE}
            WHERE capture_id = %s AND year = 2025 AND month = 8
            """,
            (dropped_capture,),
        )
        connection.execute(
            f"""
            INSERT INTO {UNRETURNED_TABLE} (capture_id, derivation_version_id, year, month)
            VALUES (%s, %s, 2025, 9)
            """,
            (dropped_capture, HISTORICAL_RECIPE_ID),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch: unreturned"):
            derive_llm_mentions_historical(dropped_store, connection)
        connection.rollback()
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, 'observation_admitted', 12)
            """,
            ("cd" * 32, capture_id, HISTORICAL_RECIPE_ID),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch"):
            derive_llm_mentions_historical(store, connection)
        connection.rollback()
    assert restored.observations == len(POINTS)
    assert restored_count == (len(POINTS),)
    assert dropped_attempt
    assert attempt_id


def test_wrong_outcome_count_and_extra_diagnostic_fail_closed(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "wrong-count")
    attempt_id, capture_id = _commit_complete(store, _body(), "36" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_llm_mentions_historical(store, connection)
        connection.commit()
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = 0
            WHERE capture_id = %s
              AND attempt_id = %s
              AND derivation_version_id = %s
            """,
            (capture_id, attempt_id, HISTORICAL_RECIPE_ID),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="conflicting provider outcome"):
            derive_llm_mentions_historical(store, connection)
        connection.rollback()
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = %s
            WHERE capture_id = %s
              AND attempt_id = %s
              AND derivation_version_id = %s
            """,
            (len(POINTS), capture_id, attempt_id, HISTORICAL_RECIPE_ID),
        )
        connection.commit()
        connection.execute(
            """
            INSERT INTO derivation_diagnostics (
                derivation_version_id, attempt_id, capture_id,
                diagnostic_code, provider_body_path
            )
            VALUES (%s, %s, %s, 'planted_extra', '/planted')
            """,
            (HISTORICAL_RECIPE_ID, attempt_id, capture_id),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch: diagnostics"):
            derive_llm_mentions_historical(store, connection)
        connection.rollback()


def test_second_recipe_coexists_for_the_same_capture(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "coexist")
    attempt_id, capture_id = _commit_complete(store, _body(), "37" * 32)
    apply_migrations(postgres_dsn)
    second = _second_recipe()
    with connect(postgres_dsn) as connection:
        derive_llm_mentions_historical(store, connection)
        registered = register_provider_recipe(connection, second)
        assert registered.derivation_version_id != HISTORICAL_RECIPE_ID
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, 'observation_admitted_empty', 0)
            """,
            (attempt_id, capture_id, registered.derivation_version_id),
        )
        connection.execute(
            f"""
            INSERT INTO {CONTEXT_TABLE} (
                capture_id, derivation_version_id, attempt_id,
                requested_keyword, match_type, search_filter, search_scope,
                platform, location_code, language_code, date_from, date_to, items_count
            )
            VALUES (
                %s, %s, %s, %s, 'word_match', 'include', ARRAY['answer'],
                'google', 2840, 'en', %s, %s, 0
            )
            """,
            (
                capture_id,
                registered.derivation_version_id,
                attempt_id,
                KEYWORD,
                DATE_FROM,
                DATE_TO,
            ),
        )
        connection.execute(
            f"""
            INSERT INTO {UNRETURNED_TABLE} (capture_id, derivation_version_id, year, month)
            VALUES (%s, %s, 2025, 8)
            """,
            (capture_id, registered.derivation_version_id),
        )
        connection.commit()
        rerun = derive_llm_mentions_historical(store, connection)
        outcomes = connection.execute(
            """
            SELECT derivation_version_id, observation_count
            FROM outcomes WHERE capture_id = %s
            ORDER BY derivation_version_id
            """,
            (capture_id,),
        ).fetchall()
        first_monthly = connection.execute(
            f"SELECT count(*) FROM {MONTHLY_TABLE} WHERE derivation_version_id = %s",
            (HISTORICAL_RECIPE_ID,),
        ).fetchone()
        second_unreturned = connection.execute(
            f"SELECT count(*) FROM {UNRETURNED_TABLE} WHERE derivation_version_id = %s",
            (registered.derivation_version_id,),
        ).fetchone()
        first_unreturned = connection.execute(
            f"SELECT count(*) FROM {UNRETURNED_TABLE} WHERE derivation_version_id = %s",
            (HISTORICAL_RECIPE_ID,),
        ).fetchone()
    assert rerun.observations == len(POINTS)
    assert (HISTORICAL_RECIPE_ID, len(POINTS)) in outcomes
    assert (registered.derivation_version_id, 0) in outcomes
    assert first_monthly == (len(POINTS),)
    assert second_unreturned == (1,)
    assert first_unreturned == (0,)


def test_constraints_reject_wrong_kind_orphan_and_invalid_keys(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "constraints")
    _commit_complete(store, _body(), "13" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_llm_mentions_historical(store, connection)
        connection.commit()
        monthly = connection.execute(
            f"""
            SELECT capture_id, derivation_version_id, within_capture_identity
            FROM {MONTHLY_TABLE} LIMIT 1
            """
        ).fetchone()
        assert monthly is not None
        with pytest.raises(CheckViolation):
            connection.execute(
                f"UPDATE {MONTHLY_TABLE} SET observation_kind = 'not.historical.kind.v1'"
            )
        connection.rollback()
        with pytest.raises(ForeignKeyViolation):
            connection.execute(
                f"""
                INSERT INTO {MONTHLY_TABLE} (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, requested_keyword, year, month, mentions,
                    ai_search_volume
                )
                VALUES (%s, %s, %s, %s, %s, 2024, 1, 1, 1)
                """,
                (monthly[0], monthly[1], "cc" * 32, MONTHLY_KIND, KEYWORD),
            )
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute(f"UPDATE {MONTHLY_TABLE} SET month = 13")
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute(f"UPDATE {MONTHLY_TABLE} SET year = 0")
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute(f"UPDATE {MONTHLY_TABLE} SET mentions = -1")
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute(
                f"UPDATE {MONTHLY_TABLE} SET ai_search_volume = %s",
                (IJSON_MAX + 1,),
            )
        connection.rollback()
        extra_identity = "ab" * 32
        connection.execute(
            """
            INSERT INTO observation_envelopes (
                capture_id, attempt_id, derivation_version_id, provider,
                adapter_contract, observation_kind, within_capture_identity
            )
            SELECT capture_id, attempt_id, derivation_version_id, provider,
                   adapter_contract, observation_kind, %s
            FROM observation_envelopes
            LIMIT 1
            """,
            (extra_identity,),
        )
        with pytest.raises(UniqueViolation):
            connection.execute(
                f"""
                INSERT INTO {MONTHLY_TABLE} (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, requested_keyword, year, month, mentions,
                    ai_search_volume
                )
                VALUES (%s, %s, %s, %s, %s, 2025, 8, 2, 2)
                """,
                (monthly[0], monthly[1], extra_identity, MONTHLY_KIND, KEYWORD),
            )
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute(f"UPDATE {MONTHLY_TABLE} SET requested_keyword = ''")
        connection.rollback()


def test_result_context_requires_matching_outcome(postgres_dsn: str) -> None:
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, HISTORICAL_RECIPE)
        connection.commit()
        with pytest.raises(ForeignKeyViolation):
            connection.execute(
                f"""
                INSERT INTO {CONTEXT_TABLE} (
                    capture_id, derivation_version_id, attempt_id,
                    requested_keyword, match_type, search_filter, search_scope,
                    platform, location_code, language_code, date_from, date_to, items_count
                )
                VALUES (
                    %s, %s, %s, %s, 'word_match', 'include', ARRAY['answer'],
                    'google', 2840, 'en', %s, %s, 0
                )
                """,
                ("ab" * 32, HISTORICAL_RECIPE_ID, "cd" * 32, KEYWORD, DATE_FROM, DATE_TO),
            )


def test_populated_pre_ai16_schema_then_historical_derive(
    tmp_path: Path, postgres_dsn: str
) -> None:
    joined_pre = "\n".join(PRE_AI16_SCHEMA_STATEMENTS)
    assert "target_metrics_result_context" in joined_pre
    assert "search_mentions_result_context" in joined_pre
    assert "llm_mentions_historical_" not in joined_pre
    historical_statements = [
        statement
        for statement in SCHEMA_STATEMENTS
        if statement not in PRE_AI16_SCHEMA_STATEMENTS
    ]
    assert len(historical_statements) == 3
    assert any(MONTHLY_TABLE in item for item in historical_statements)
    assert any(CONTEXT_TABLE in item for item in historical_statements)
    assert any(UNRETURNED_TABLE in item for item in historical_statements)
    tm_statements = [
        statement
        for statement in PRE_AI16_SCHEMA_STATEMENTS
        if statement not in PRE_AI11_SCHEMA_STATEMENTS
    ]
    assert len(tm_statements) == 3
    assert len(PRE_AI11_SCHEMA_STATEMENTS) - len(PRE_AI05_SCHEMA_STATEMENTS) == 7
    assert len(PRE_AI05_SCHEMA_STATEMENTS) - len(PRE_PF12_SCHEMA_STATEMENTS) == 10

    attempt_id = "aa" * 32
    capture_id = "bb" * 32
    coverage_id = observation_identity(
        {
            "axes": {"requested_keyword": "seo api"},
            "observation_kind": COVERAGE_KIND,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        CORE_RECIPE,
    )
    feature_id = observation_identity(
        {
            "axes": {
                "item_type": "organic",
                "page": 1,
                "position": "left",
                "rank_absolute": 1,
                "rank_group": 1,
                "requested_keyword": "conspiracy theories",
            },
            "observation_kind": FEATURE_PRESENCE_KIND,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        GOOGLE_ORGANIC_RECIPE,
    )
    with connect(postgres_dsn) as connection:
        for statement in PRE_AI16_SCHEMA_STATEMENTS:
            connection.execute(statement)
        for statement in WIDEN_IJSON_COLUMNS_SQL:
            connection.execute(statement)
        register_provider_recipe(connection, CORE_RECIPE)
        register_provider_recipe(connection, GOOGLE_ORGANIC_RECIPE)
        connection.execute(
            """
            INSERT INTO derivation_versions (
                derivation_version_id, adapter_contract, registered_at
            )
            VALUES ('fixture-panel-v1', 'fixture-panel-v1', TIMESTAMPTZ '2026-08-14T00:00:00Z')
            """
        )
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES
                (%s, NULL, %s, 'authorized_unresolved', 0),
                (%s, %s, %s, 'observation_admitted', 1),
                (%s, %s, %s, 'observation_admitted', 1),
                ('ff' || %s, %s, 'fixture-panel-v1', 'observation_admitted', 1)
            """,
            (
                attempt_id,
                CORE_RECIPE_ID,
                attempt_id,
                capture_id,
                CORE_RECIPE_ID,
                "cc" * 32,
                "dd" * 32,
                GOOGLE_ORGANIC_RECIPE_ID,
                "ee" * 31,
                "11" * 32,
            ),
        )
        write_observation_envelope(
            connection,
            ObservationEnvelope(
                capture_id=capture_id,
                attempt_id=attempt_id,
                derivation_version_id=CORE_RECIPE_ID,
                provider="dataforseo",
                adapter_contract=PAID_ADAPTER_CONTRACT,
                observation_kind=COVERAGE_KIND,
                within_capture_identity=coverage_id,
            ),
        )
        connection.execute(
            """
            INSERT INTO keyword_overview_coverage (
                capture_id, derivation_version_id, within_capture_identity,
                observation_kind, requested_keyword, covered,
                returned_keyword, returned_keyword_state
            )
            VALUES (%s, %s, %s, %s, 'seo api', TRUE, 'seo api', 'stated')
            """,
            (capture_id, CORE_RECIPE_ID, coverage_id, COVERAGE_KIND),
        )
        write_observation_envelope(
            connection,
            ObservationEnvelope(
                capture_id="dd" * 32,
                attempt_id="cc" * 32,
                derivation_version_id=GOOGLE_ORGANIC_RECIPE_ID,
                provider="dataforseo",
                adapter_contract=ORGANIC_ADAPTER_CONTRACT,
                observation_kind=FEATURE_PRESENCE_KIND,
                within_capture_identity=feature_id,
            ),
        )
        connection.execute(
            """
            INSERT INTO google_organic_serp_features (
                capture_id, derivation_version_id, within_capture_identity,
                observation_kind, requested_keyword, item_type, page, position,
                rank_group, rank_absolute
            )
            VALUES (%s, %s, %s, %s, 'conspiracy theories', 'organic', 1, 'left', 1, 1)
            """,
            (
                "dd" * 32,
                GOOGLE_ORGANIC_RECIPE_ID,
                feature_id,
                FEATURE_PRESENCE_KIND,
            ),
        )
        connection.execute(
            """
            INSERT INTO observations (
                capture_id, derivation_version_id, within_capture_result_id,
                attempt_id, provider, panel_id, subject_key, result_index,
                label, score
            )
            VALUES (
                %s, 'fixture-panel-v1', 'result:1', %s, 'fixture',
                'panel-alpha', 'subject-one', 1, 'fixture-result-1', 999
            )
            """,
            ("11" * 32, "ff" + "ee" * 31),
        )
        register_provider_recipe(connection, SEARCH_MENTIONS_RECIPE)
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, 'observation_admitted', 0)
            """,
            ("99" * 32, "88" * 32, SEARCH_MENTIONS_RECIPE_ID),
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
                'google', 2840, 'en', 5, 0, 3055, 0, 5, NULL, 'json_null'
            )
            """,
            ("88" * 32, SEARCH_MENTIONS_RECIPE_ID, "99" * 32, KEYWORD),
        )
        register_provider_recipe(connection, TARGET_METRICS_RECIPE)
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, 'observation_admitted', 0)
            """,
            ("77" * 32, "66" * 32, TARGET_METRICS_RECIPE_ID),
        )
        connection.execute(
            """
            INSERT INTO target_metrics_result_context (
                capture_id, derivation_version_id, attempt_id,
                requested_keyword, match_type, search_filter, search_scope,
                platform, location_code, language_code, internal_list_limit,
                total_count, result_offset, items_count, items_state,
                location_key, location_mentions, location_ai_search_volume,
                location_provider_array_index, location_row_count,
                language_key, language_mentions, language_ai_search_volume,
                language_provider_array_index, language_row_count,
                platform_key, platform_mentions, platform_ai_search_volume,
                platform_provider_array_index, platform_row_count,
                sources_domain_count, search_results_domain_count,
                search_results_domain_state, brand_entities_title_count,
                brand_entities_title_state, brand_entities_category_count,
                brand_entities_category_state
            )
            VALUES (
                %s, %s, %s, %s, 'word_match', 'include', ARRAY['answer'],
                'google', 2840, 'en', 10, 0, 0, 0, 'stated',
                2840, 0, 0, 0, 1, 'en', 0, 0, 0, 1, 'google', 0, 0, 0, 1,
                0, 0, 'stated', 0, 'stated', 0, 'stated'
            )
            """,
            ("66" * 32, TARGET_METRICS_RECIPE_ID, "77" * 32, KEYWORD),
        )
        before_coverage = connection.execute(
            "SELECT requested_keyword FROM keyword_overview_coverage"
        ).fetchall()
        before_features = connection.execute(
            "SELECT item_type FROM google_organic_serp_features"
        ).fetchall()
        before_observations = connection.execute("SELECT label FROM observations").fetchall()
        before_mentions = connection.execute(
            "SELECT requested_keyword FROM search_mentions_result_context"
        ).fetchall()
        before_tm = connection.execute(
            "SELECT requested_keyword FROM target_metrics_result_context"
        ).fetchall()
        connection.commit()
        apply_schema(connection)
        after_coverage = connection.execute(
            "SELECT requested_keyword FROM keyword_overview_coverage"
        ).fetchall()
        after_features = connection.execute(
            "SELECT item_type FROM google_organic_serp_features"
        ).fetchall()
        after_observations = connection.execute("SELECT label FROM observations").fetchall()
        after_mentions = connection.execute(
            "SELECT requested_keyword FROM search_mentions_result_context"
        ).fetchall()
        after_tm = connection.execute(
            "SELECT requested_keyword FROM target_metrics_result_context"
        ).fetchall()
        for table in AI16_TABLES:
            connection.execute(f"SELECT 1 FROM {table} LIMIT 0")
    assert before_coverage == after_coverage == [("seo api",)]
    assert before_features == after_features == [("organic",)]
    assert before_observations == after_observations == [("fixture-result-1",)]
    assert before_mentions == after_mentions == [(KEYWORD,)]
    assert before_tm == after_tm == [(KEYWORD,)]

    metrics = create_store(tmp_path / "historical")
    _commit_complete(metrics, _body(), "42" * 32)
    with connect(postgres_dsn) as connection:
        summary = derive_llm_mentions_historical(metrics, connection)
        ko_final = connection.execute(
            "SELECT count(*) FROM keyword_overview_coverage"
        ).fetchone()
        organic_final = connection.execute(
            "SELECT count(*) FROM google_organic_serp_features"
        ).fetchone()
        fixture_final = connection.execute("SELECT count(*) FROM observations").fetchone()
        mentions_final = connection.execute(
            "SELECT requested_keyword FROM search_mentions_result_context"
        ).fetchone()
        tm_final = connection.execute(
            "SELECT requested_keyword FROM target_metrics_result_context"
        ).fetchone()
    assert summary.observations == len(POINTS)
    assert ko_final == (1,)
    assert organic_final == (1,)
    assert fixture_final == (1,)
    assert mentions_final == (KEYWORD,)
    assert tm_final == (KEYWORD,)


def test_fresh_and_upgraded_historical_catalog_match(
    postgres_dsn: str, postgres_second_dsn: str
) -> None:
    with connect(postgres_dsn) as connection:
        for statement in PRE_AI16_SCHEMA_STATEMENTS:
            connection.execute(statement)
        connection.commit()
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)
    with connect(postgres_dsn) as upgraded, connect(postgres_second_dsn) as fresh:
        assert _historical_catalog(upgraded) == _historical_catalog(fresh)
        assert _historical_catalog(upgraded)[0]
        assert _historical_catalog(upgraded)[1]


def test_two_databases_are_logically_equivalent(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "eq")
    _commit_complete(store, _body(), "43" * 32)
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)

    def snapshot(dsn: str) -> tuple[object, ...]:
        with connect(dsn) as connection:
            derive_llm_mentions_historical(store, connection)
            parts: list[object] = []
            catalog: list[tuple[str, tuple[str, ...]]] = []
            for table in AI16_TABLES:
                columns, rows = _fetch_relation(connection, table)
                catalog.append((table, columns))
                parts.append(rows)
            assert tuple(name for name, _columns in catalog) == AI16_TABLES
            assert all(columns for _name, columns in catalog)
        return (tuple(catalog), tuple(parts))

    first = snapshot(postgres_dsn)
    second = snapshot(postgres_second_dsn)
    assert first == second
    catalog_names = first[0]
    assert isinstance(catalog_names, tuple)
    with connect(postgres_dsn) as connection:
        for table, columns in catalog_names:
            assert columns == _catalog_columns(connection, table)


def test_historical_derive_skips_other_adapters_and_others_skip_historical(
    tmp_path: Path, postgres_dsn: str
) -> None:
    historical = create_store(tmp_path / "historical")
    _commit_complete(historical, _body(), "44" * 32)
    mixed = create_store(tmp_path / "mixed")
    fixture = capture_fixture(mixed, PUBLISHED_AR_INPUTS.as_fixture_inputs())
    attempt = _attempt("45" * 32)
    mixed.commit_attempt(attempt, request_body=historical_request_body_bytes(_parameters()))
    mixed.commit_capture(_complete_capture(attempt, _body(), suffix="2"), response_body=_body())
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        fixture_summary = derive(mixed, connection, DEFAULT_VERSION)
        ko_summary = derive_keyword_overview(mixed, connection)
        organic_summary = derive_google_organic(mixed, connection)
        mentions_summary = derive_search_mentions(mixed, connection)
        metrics_summary = derive_target_metrics(mixed, connection)
        historical_facts = connection.execute(
            f"SELECT count(*) FROM {MONTHLY_TABLE}"
        ).fetchone()
        derive_llm_mentions_historical(historical, connection)
        after = connection.execute(f"SELECT count(*) FROM {MONTHLY_TABLE}").fetchone()
        tm_on_historical = derive_target_metrics(historical, connection)
        fixture_attempts = connection.execute(
            "SELECT count(*) FROM outcomes WHERE attempt_id = %s",
            (fixture.attempt_id,),
        ).fetchone()
    assert fixture_summary.integrity_failures == 0
    assert ko_summary.integrity_failures == 0
    assert organic_summary.integrity_failures == 0
    assert mentions_summary.integrity_failures == 0
    assert metrics_summary.integrity_failures == 0
    assert historical_facts == (0,)
    assert after == (len(POINTS),)
    assert tm_on_historical.capture_outcomes == 0
    assert fixture_attempts is not None and fixture_attempts[0] >= 1


def test_parser_module_has_no_recipe_construction() -> None:
    source = Path(
        "src/observatory/dataforseo_ai_optimization_llm_mentions_historical.py"
    ).read_text(encoding="utf-8")
    assert "provider_recipe" not in source
    assert "def historical_recipe" not in source
    assert "PROVIDER" in source
    assert "PARSER_CONTRACT" in source
    assert "MONTHLY_KIND" in source
