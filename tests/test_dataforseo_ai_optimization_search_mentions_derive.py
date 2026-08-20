"""AI-05: Search Mentions provider Derivation into real PostgreSQL."""

from __future__ import annotations

import copy
import hashlib
import json
import socket
from collections.abc import Mapping
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from psycopg import sql
from psycopg.errors import CheckViolation, ForeignKeyViolation, UniqueViolation

from observatory.capture_event import (
    MENTIONS_ADAPTER_CONTRACT,
    ORGANIC_ADAPTER_CONTRACT,
    PAID_ADAPTER_CONTRACT,
    body_ref,
    mentions_http_attempt_document,
    mentions_http_capture_document,
)
from observatory.dataforseo_ai_optimization_search_mentions import (
    ITEM_KIND,
    MONTHLY_KIND,
    SEARCH_MENTIONS_RECIPE,
    SEARCH_MENTIONS_RECIPE_BYTES,
    SEARCH_MENTIONS_RECIPE_ID,
    SOURCE_KIND,
    parse_search_mentions,
    search_mentions_recipe,
)
from observatory.dataforseo_ai_optimization_search_mentions_paid_probe import (
    closed_mentions_parameters,
    mentions_request_body_bytes,
)
from observatory.dataforseo_google_organic import (
    FEATURE_PRESENCE_KIND,
    GOOGLE_ORGANIC_RECIPE,
    GOOGLE_ORGANIC_RECIPE_ID,
)
from observatory.dataforseo_keyword_overview import CORE_RECIPE, CORE_RECIPE_ID, COVERAGE_KIND
from observatory.derive import DEFAULT_VERSION, DerivationError, derive
from observatory.evidence_store import create_store
from observatory.migrate import (
    PRE_AI05_SCHEMA_STATEMENTS,
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
    observation_identity,
    register_provider_recipe,
    validate_recipe,
    write_observation_envelope,
)
from observatory.search_mentions_derive import (
    derive_search_mentions,
    plan_search_mentions_capture,
)

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_ai_optimization_search_mentions_ai03.json"
)
KEYWORD = "generative engine optimization"
AI03_BODY_BYTES = 48466
AI03_BODY_SHA256 = "8b3cd0fb0c9fa23c102696bfe6b7212396c0f7c110e9ca8ca5b8ee5af182e80a"
ACCEPTED_RECIPE_ID = "bd3dfbf87eba83df35dc7ae6eecd25c223a89ad72d910db346d8ebafb61933e0"
ACCEPTED_ORGANIC = "338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde"
VOLUMES = (368000, 201000, 135000, 110000, 110000)
AI05_TABLES = (
    "search_mentions_items",
    "search_mentions_item_occurrences",
    "search_mentions_monthly_search_volume",
    "search_mentions_monthly_occurrences",
    "search_mentions_sources",
    "search_mentions_source_occurrences",
    "search_mentions_result_context",
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


def _parameters() -> dict[str, object]:
    return closed_mentions_parameters(keyword=KEYWORD)


def _attempt(nonce: str) -> dict[str, object]:
    return mentions_http_attempt_document(
        parameters=_parameters(),
        attempt_nonce=nonce,
        authorized_at="2026-08-20T17:36:00.000000Z",
        observatory_version="ai05-test-v1",
    )


def _complete_capture(
    attempt: dict[str, object], body: bytes, *, suffix: str = "1"
) -> dict[str, object]:
    return mentions_http_capture_document(
        attempt=attempt,
        request_started_at=f"2026-08-20T17:36:0{suffix}.100000Z",
        transport_ended_at=f"2026-08-20T17:36:0{suffix}.400000Z",
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
        response_headers_at=f"2026-08-20T17:36:0{suffix}.200000Z",
        response_body_ended_at=f"2026-08-20T17:36:0{suffix}.300000Z",
    )


def _commit_complete(store: Any, body: bytes, nonce: str) -> tuple[str, str]:
    attempt = _attempt(nonce)
    request = mentions_request_body_bytes(_parameters())
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


def _set_items(document: dict[str, Any], items: list[Any]) -> None:
    result = _result(document)
    result["items"] = items
    result["items_count"] = len(items)


def _complete_capture_dict() -> dict[str, object]:
    return {
        "transport_state": "response_complete",
        "response": {"completeness": "complete"},
    }


def _kind_counts(planned: Any) -> dict[str, int]:
    counts = {ITEM_KIND: 0, MONTHLY_KIND: 0, SOURCE_KIND: 0}
    for envelope in planned.envelopes:
        counts[envelope.observation_kind] += 1
    return counts


def _second_recipe() -> dict[str, object]:
    document = copy.deepcopy(SEARCH_MENTIONS_RECIPE)
    document["reconciliation"] = {"rule": "attempt_parameters_item_context_v2"}
    return validate_recipe(document)


def _mentions_catalog(connection: Any) -> tuple[tuple[Any, ...], ...]:
    constraints = connection.execute(
        """
        SELECT c.relname, con.conname, con.contype, pg_get_constraintdef(con.oid)
        FROM pg_constraint AS con
        JOIN pg_class AS c ON c.oid = con.conrelid
        JOIN pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname = current_schema()
          AND c.relname LIKE 'search_mentions_%'
        ORDER BY 1, 2, 4
        """
    ).fetchall()
    columns = connection.execute(
        """
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name LIKE 'search_mentions_%'
        ORDER BY 1, 2
        """
    ).fetchall()
    return tuple(constraints), tuple(columns)


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


def _tuple_in_catalog_order(
    mapping: Mapping[str, object], columns: tuple[str, ...]
) -> tuple[object, ...]:
    return tuple(_normalize_cell(mapping[column]) for column in columns)


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


def _semantic_identity(kind: str, axes: dict[str, object]) -> str:
    return observation_identity(
        {
            "axes": axes,
            "observation_kind": kind,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        SEARCH_MENTIONS_RECIPE,
    )


def _optional_pair(field: Any) -> tuple[object, str]:
    if field.state.value == "stated":
        return field.value, field.state.value
    return None, str(field.state.value)


def _expected_frozen_rows(
    attempt_id: str, capture_id: str, parsed: Any
) -> dict[str, list[dict[str, object]]]:
    """Build persisted-row expectations from the AI-04 IR, not the AI-05 planner."""

    request = parsed.request
    keyword = request.keyword
    recipe_id = SEARCH_MENTIONS_RECIPE_ID
    items: list[dict[str, object]] = []
    item_occ: list[dict[str, object]] = []
    monthly: list[dict[str, object]] = []
    monthly_occ: list[dict[str, object]] = []
    sources: list[dict[str, object]] = []
    source_occ: list[dict[str, object]] = []
    seen_monthly: set[str] = set()
    seen_sources: set[str] = set()
    for index, item in enumerate(parsed.items):
        item_id = _semantic_identity(
            ITEM_KIND,
            {
                "model_name": item.model_name,
                "question": item.question,
                "requested_keyword": keyword,
            },
        )
        items.append(
            {
                "capture_id": capture_id,
                "derivation_version_id": recipe_id,
                "within_capture_identity": item_id,
                "observation_kind": ITEM_KIND,
                "requested_keyword": keyword,
                "platform": item.platform,
                "model_name": item.model_name,
                "location_code": item.location_code,
                "language_code": item.language_code,
                "question": item.question,
                "answer": item.answer,
                "ai_search_volume": item.ai_search_volume,
                "is_web_search_based": item.is_web_search_based,
                "first_response_at": item.first_response_at,
                "last_response_at": item.last_response_at,
                "search_results_state": item.search_results.state.value,
                "brand_entities_state": item.brand_entities.state.value,
                "fan_out_queries_state": item.fan_out_queries.state.value,
            }
        )
        item_occ.append(
            {
                "capture_id": capture_id,
                "derivation_version_id": recipe_id,
                "within_capture_identity": item_id,
                "observation_kind": ITEM_KIND,
                "item_index": index,
            }
        )
        for point in item.monthly_searches:
            monthly_id = _semantic_identity(
                MONTHLY_KIND,
                {
                    "model_name": item.model_name,
                    "month": point.month,
                    "question": item.question,
                    "requested_keyword": keyword,
                    "year": point.year,
                },
            )
            if monthly_id not in seen_monthly:
                seen_monthly.add(monthly_id)
                monthly.append(
                    {
                        "capture_id": capture_id,
                        "derivation_version_id": recipe_id,
                        "within_capture_identity": monthly_id,
                        "observation_kind": MONTHLY_KIND,
                        "requested_keyword": keyword,
                        "model_name": item.model_name,
                        "question": item.question,
                        "year": point.year,
                        "month": point.month,
                        "search_volume": point.search_volume,
                    }
                )
            monthly_occ.append(
                {
                    "capture_id": capture_id,
                    "derivation_version_id": recipe_id,
                    "within_capture_identity": monthly_id,
                    "observation_kind": MONTHLY_KIND,
                    "item_index": index,
                }
            )
        for source in item.sources:
            publication, publication_state = _optional_pair(source.publication_date)
            thumbnail, thumbnail_state = _optional_pair(source.thumbnail)
            markdown, markdown_state = _optional_pair(source.markdown)
            source_id = _semantic_identity(
                SOURCE_KIND,
                {
                    "model_name": item.model_name,
                    "question": item.question,
                    "requested_keyword": keyword,
                    "url": source.url,
                },
            )
            if source_id not in seen_sources:
                seen_sources.add(source_id)
                sources.append(
                    {
                        "capture_id": capture_id,
                        "derivation_version_id": recipe_id,
                        "within_capture_identity": source_id,
                        "observation_kind": SOURCE_KIND,
                        "requested_keyword": keyword,
                        "model_name": item.model_name,
                        "question": item.question,
                        "url": source.url,
                        "title": source.title,
                        "domain": source.domain,
                        "source_name": source.source_name,
                        "snippet": source.snippet,
                        "publication_date": publication,
                        "publication_date_state": publication_state,
                        "thumbnail": thumbnail,
                        "thumbnail_state": thumbnail_state,
                        "markdown": markdown,
                        "markdown_state": markdown_state,
                    }
                )
            source_occ.append(
                {
                    "capture_id": capture_id,
                    "derivation_version_id": recipe_id,
                    "within_capture_identity": source_id,
                    "observation_kind": SOURCE_KIND,
                    "item_index": index,
                    "rank": source.rank,
                }
            )
    token, token_state = _optional_pair(parsed.search_after_token)
    context = [
        {
            "capture_id": capture_id,
            "derivation_version_id": recipe_id,
            "attempt_id": attempt_id,
            "requested_keyword": request.keyword,
            "match_type": request.match_type,
            "search_filter": request.search_filter,
            "search_scope": list(request.search_scope),
            "platform": request.platform,
            "location_code": request.location_code,
            "language_code": request.language_code,
            "request_limit": request.limit,
            "request_offset": request.offset,
            "total_count": parsed.total_count,
            "result_offset": parsed.offset,
            "items_count": parsed.items_count,
            "search_after_token": token,
            "search_after_token_state": token_state,
        }
    ]
    return {
        "search_mentions_items": items,
        "search_mentions_item_occurrences": item_occ,
        "search_mentions_monthly_search_volume": monthly,
        "search_mentions_monthly_occurrences": monthly_occ,
        "search_mentions_sources": sources,
        "search_mentions_source_occurrences": source_occ,
        "search_mentions_result_context": context,
    }


def test_accepted_recipe_and_fixture_identities_remain_unchanged() -> None:
    assert SEARCH_MENTIONS_RECIPE_ID == ACCEPTED_RECIPE_ID
    assert len(SEARCH_MENTIONS_RECIPE_BYTES) == 2021
    assert hashlib.sha256(SEARCH_MENTIONS_RECIPE_BYTES).hexdigest() == ACCEPTED_RECIPE_ID
    assert search_mentions_recipe() == SEARCH_MENTIONS_RECIPE
    raw = _body()
    assert len(raw) == AI03_BODY_BYTES
    assert hashlib.sha256(raw).hexdigest() == AI03_BODY_SHA256
    assert CORE_RECIPE_ID == "319af798f3e0b3e5fe4579539442c4ca5d384b683e1f4bce0f7a1b3e26cd5908"
    assert GOOGLE_ORGANIC_RECIPE_ID == ACCEPTED_ORGANIC


def test_plan_frozen_fixture_has_exact_semantic_counts() -> None:
    planned = plan_search_mentions_capture(
        "a" * 64,
        "b" * 64,
        _complete_capture_dict(),
        _parameters(),
        _body(),
    )
    assert planned.classification == "observation_admitted"
    assert len(planned.envelopes) == 113
    assert _kind_counts(planned) == {
        ITEM_KIND: 5,
        MONTHLY_KIND: 60,
        SOURCE_KIND: 48,
    }
    assert len(planned.item_occurrences) == 5
    assert len(planned.monthly_occurrences) == 60
    assert len(planned.source_occurrences) == 48
    assert planned.context is not None
    assert planned.context["total_count"] == 3055
    assert planned.context["result_offset"] == 0
    assert planned.context["items_count"] == 5
    assert planned.context["search_after_token_state"] == "stated"
    assert isinstance(planned.context["search_after_token"], str)
    assert len(planned.context["search_after_token"]) == 628
    assert "cost" not in planned.context
    assert "task_id" not in planned.context
    assert "echo" not in planned.context
    volumes = [
        row["ai_search_volume"]
        for row in planned.details["search_mentions_items"]
    ]
    assert tuple(volumes) == VOLUMES


def test_plan_empty_page_is_admitted_empty() -> None:
    document = _decoded()
    _set_items(document, [])
    planned = plan_search_mentions_capture(
        "a" * 64,
        "b" * 64,
        _complete_capture_dict(),
        _parameters(),
        _encode(document),
    )
    assert planned.classification == "observation_admitted_empty"
    assert planned.envelopes == ()
    assert planned.context is not None
    assert planned.context["items_count"] == 0
    assert planned.context["total_count"] == 3055


def test_plan_empty_identity_string_rejects_whole_unit() -> None:
    for field in ("question", "model_name"):
        document = _decoded()
        _result(document)["items"][0][field] = ""
        planned = plan_search_mentions_capture(
            "a" * 64,
            "b" * 64,
            _complete_capture_dict(),
            _parameters(),
            _encode(document),
        )
        assert planned.classification == "provider_envelope_rejected"
        assert planned.envelopes == ()
        assert planned.context is None


def test_plan_duplicate_question_recomputes_envelope_count() -> None:
    document = _decoded()
    items = _result(document)["items"]
    items.append(copy.deepcopy(items[0]))
    _set_items(document, items)
    planned = plan_search_mentions_capture(
        "a" * 64,
        "b" * 64,
        _complete_capture_dict(),
        _parameters(),
        _encode(document),
    )
    counts = _kind_counts(planned)
    expected = counts[ITEM_KIND] + counts[MONTHLY_KIND] + counts[SOURCE_KIND]
    assert planned.classification == "observation_admitted"
    assert len(planned.envelopes) == expected
    assert counts[ITEM_KIND] == 5
    assert len(planned.item_occurrences) == 6
    assert counts[MONTHLY_KIND] == 60
    assert len(planned.monthly_occurrences) == 72
    assert counts[SOURCE_KIND] == 48
    assert len(planned.source_occurrences) == 55


def test_plan_conflicting_duplicate_item_rejects_whole_unit() -> None:
    document = _decoded()
    items = _result(document)["items"]
    clone = copy.deepcopy(items[0])
    clone["answer"] = "planted disagreement"
    items.append(clone)
    _set_items(document, items)
    planned = plan_search_mentions_capture(
        "a" * 64,
        "b" * 64,
        _complete_capture_dict(),
        _parameters(),
        _encode(document),
    )
    assert planned.classification == "provider_envelope_rejected"
    assert planned.context is None
    assert planned.envelopes == ()


def test_derive_ai03_fixture_into_real_postgres(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_complete(store, _body(), "11" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_search_mentions(store, connection)
        outcome = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes WHERE capture_id = %s
            """,
            (capture_id,),
        ).fetchone()
        attempt_row = connection.execute(
            """
            SELECT classification FROM outcomes
            WHERE attempt_id = %s AND capture_id IS NULL
            """,
            (attempt_id,),
        ).fetchone()
        items = connection.execute("SELECT count(*) FROM search_mentions_items").fetchone()
        item_occ = connection.execute(
            "SELECT count(*) FROM search_mentions_item_occurrences"
        ).fetchone()
        monthly = connection.execute(
            "SELECT count(*) FROM search_mentions_monthly_search_volume"
        ).fetchone()
        monthly_occ = connection.execute(
            "SELECT count(*) FROM search_mentions_monthly_occurrences"
        ).fetchone()
        sources = connection.execute("SELECT count(*) FROM search_mentions_sources").fetchone()
        source_occ = connection.execute(
            "SELECT count(*) FROM search_mentions_source_occurrences"
        ).fetchone()
        context = connection.execute(
            """
            SELECT total_count, result_offset, items_count,
                   search_after_token_state, length(search_after_token),
                   request_limit, request_offset, search_scope
            FROM search_mentions_result_context
            """
        ).fetchone()
        clocks = connection.execute(
            """
            SELECT first_response_at, last_response_at
            FROM search_mentions_items
            WHERE question = 'enception'
            """
        ).fetchone()
        clock_type = connection.execute(
            """
            SELECT data_type FROM information_schema.columns
            WHERE table_name = 'search_mentions_items'
              AND column_name = 'first_response_at'
            """
        ).fetchone()
        nulls = connection.execute(
            """
            SELECT DISTINCT search_results_state, brand_entities_state,
                   fan_out_queries_state
            FROM search_mentions_items
            """
        ).fetchall()
        volumes = connection.execute(
            """
            SELECT ai_search_volume FROM search_mentions_items
            ORDER BY question
            """
        ).fetchall()
        newest = connection.execute(
            """
            SELECT i.question, i.ai_search_volume, m.search_volume
            FROM search_mentions_items AS i
            JOIN search_mentions_monthly_search_volume AS m
              ON m.capture_id = i.capture_id
             AND m.question = i.question
             AND m.model_name = i.model_name
            WHERE (m.year, m.month) = (
                SELECT year, month
                FROM search_mentions_monthly_search_volume AS inner_m
                WHERE inner_m.question = i.question
                ORDER BY year DESC, month DESC
                LIMIT 1
            )
            ORDER BY i.question
            """
        ).fetchall()
        urls = connection.execute(
            "SELECT url FROM search_mentions_sources ORDER BY url"
        ).fetchall()
    assert summary.observations == 113
    assert summary.integrity_failures == 0
    assert attempt_row == ("authorized_unresolved",)
    assert outcome == ("observation_admitted", 113)
    assert items == (5,)
    assert item_occ == (5,)
    assert monthly == (60,)
    assert monthly_occ == (60,)
    assert sources == (48,)
    assert source_occ == (48,)
    assert context is not None
    assert context[0] == 3055
    assert context[1] == 0
    assert context[2] == 5
    assert context[3] == "stated"
    assert context[4] == 628
    assert context[5] == 5
    assert context[6] == 0
    assert list(context[7]) == ["answer"]
    assert clocks == ("2026-01-27 03:48:11 +00:00", "2026-01-27 03:48:11 +00:00")
    assert clock_type == ("text",)
    assert nulls == [("json_null", "json_null", "json_null")]
    assert {row[0] for row in volumes} == set(VOLUMES)
    disagreements = [row for row in newest if row[1] != row[2]]
    assert len(disagreements) == 3
    fixture_urls = [
        source["url"]
        for item in _result(_decoded())["items"]
        for source in item["sources"]
    ]
    assert [row[0] for row in urls] == sorted(fixture_urls)


def test_frozen_persisted_rows_match_parser_ir(
    tmp_path: Path, postgres_dsn: str
) -> None:
    parsed = parse_search_mentions(_body(), _parameters())
    store = create_store(tmp_path / "exact-ir")
    attempt_id, capture_id = _commit_complete(store, _body(), "41" * 32)
    expected = _expected_frozen_rows(attempt_id, capture_id, parsed)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        for table in AI05_TABLES:
            columns, stored = _fetch_relation(connection, table)
            intended_maps = expected[table]
            assert intended_maps
            for row in intended_maps:
                assert set(row) == set(columns)
            intended = {
                _tuple_in_catalog_order(row, columns) for row in intended_maps
            }
            assert len(stored) == len(intended_maps)
            assert set(stored) == intended
        token = connection.execute(
            "SELECT search_after_token FROM search_mentions_result_context"
        ).fetchone()
        attachments = connection.execute(
            """
            SELECT s.model_name, s.question, s.url, o.rank, o.item_index
            FROM search_mentions_sources AS s
            JOIN search_mentions_source_occurrences AS o
              ON o.capture_id = s.capture_id
             AND o.derivation_version_id = s.derivation_version_id
             AND o.within_capture_identity = s.within_capture_identity
            ORDER BY o.item_index, o.rank
            """
        ).fetchall()
        answers = connection.execute(
            """
            SELECT question, answer, first_response_at, last_response_at
            FROM search_mentions_items
            ORDER BY question
            """
        ).fetchall()
    assert token is not None
    parsed_token = parsed.search_after_token
    assert parsed_token is not None
    assert token[0] == parsed_token.value
    assert len(str(token[0])) == 628
    expected_attachments = [
        (item.model_name, item.question, source.url, source.rank, index)
        for index, item in enumerate(parsed.items)
        for source in item.sources
    ]
    assert attachments == expected_attachments
    expected_answers = sorted(
        (
            item.question,
            item.answer,
            item.first_response_at,
            item.last_response_at,
        )
        for item in parsed.items
    )
    assert list(answers) == expected_answers
    context = expected["search_mentions_result_context"][0]
    assert context["match_type"] == "word_match"
    assert context["search_filter"] == "include"
    assert context["total_count"] == 3055
    assert context["items_count"] == 5
    assert context["result_offset"] == 0
    assert context["request_limit"] == 5
    assert context["request_offset"] == 0
    assert context["attempt_id"] == attempt_id


def test_duplicate_url_keeps_one_source_and_two_occurrences(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    sources = _result(document)["items"][0]["sources"]
    clone = copy.deepcopy(sources[0])
    clone["rank"] = 8
    sources.append(clone)
    store = create_store(tmp_path / "dup-url")
    _commit_complete(store, _encode(document), "12" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        semantic = connection.execute(
            """
            SELECT count(*) FROM search_mentions_sources WHERE url = %s
            """,
            (clone["url"],),
        ).fetchone()
        occ = connection.execute(
            """
            SELECT item_index, rank
            FROM search_mentions_source_occurrences AS o
            JOIN search_mentions_sources AS s
              ON s.within_capture_identity = o.within_capture_identity
             AND s.capture_id = o.capture_id
             AND s.derivation_version_id = o.derivation_version_id
            WHERE s.url = %s
            ORDER BY item_index, rank
            """,
            (clone["url"],),
        ).fetchall()
        envelopes = connection.execute(
            "SELECT count(*) FROM observation_envelopes WHERE observation_kind = %s",
            (SOURCE_KIND,),
        ).fetchone()
    assert semantic == (1,)
    assert occ == [(0, 1), (0, 8)]
    assert envelopes == (48,)


def test_conflicting_source_and_monthly_reject_without_context(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    sources = _result(document)["items"][0]["sources"]
    clone = copy.deepcopy(sources[0])
    clone["rank"] = 8
    clone["title"] = "planted source disagreement"
    sources.append(clone)
    store = create_store(tmp_path / "source-conflict")
    _attempt_id, capture_id = _commit_complete(store, _encode(document), "13" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        outcome = connection.execute(
            "SELECT classification, observation_count FROM outcomes WHERE capture_id = %s",
            (capture_id,),
        ).fetchone()
        context = connection.execute(
            "SELECT count(*) FROM search_mentions_result_context"
        ).fetchone()
        envelopes = connection.execute("SELECT count(*) FROM observation_envelopes").fetchone()
    assert outcome == ("provider_envelope_rejected", 0)
    assert context == (0,)
    assert envelopes == (0,)

    monthly_doc = _decoded()
    items = _result(monthly_doc)["items"]
    clone_item = copy.deepcopy(items[0])
    clone_item["monthly_searches"][0]["search_volume"] = 1
    items.append(clone_item)
    _set_items(monthly_doc, items)
    monthly_store = create_store(tmp_path / "monthly-conflict")
    _attempt_id, monthly_capture = _commit_complete(
        monthly_store, _encode(monthly_doc), "14" * 32
    )
    with connect(postgres_dsn) as connection:
        derive_search_mentions(monthly_store, connection)
        monthly_outcome = connection.execute(
            "SELECT classification FROM outcomes WHERE capture_id = %s",
            (monthly_capture,),
        ).fetchone()
    assert monthly_outcome == ("provider_envelope_rejected",)


def test_unequal_monthly_windows_admit_union(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    items = _result(document)["items"]
    clone = copy.deepcopy(items[0])
    clone["monthly_searches"] = [{"year": 2026, "month": 1, "search_volume": 9}]
    items.append(clone)
    _set_items(document, items)
    store = create_store(tmp_path / "union")
    _commit_complete(store, _encode(document), "15" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        periods = connection.execute(
            """
            SELECT year, month, search_volume
            FROM search_mentions_monthly_search_volume
            WHERE question = 'enception'
            ORDER BY year, month
            """
        ).fetchall()
        occ = connection.execute(
            """
            SELECT m.year, m.month, o.item_index
            FROM search_mentions_monthly_occurrences AS o
            JOIN search_mentions_monthly_search_volume AS m
              ON m.within_capture_identity = o.within_capture_identity
             AND m.capture_id = o.capture_id
             AND m.derivation_version_id = o.derivation_version_id
            WHERE m.question = 'enception'
            ORDER BY m.year, m.month, o.item_index
            """
        ).fetchall()
    assert (2026, 1, 9) in periods
    assert (2025, 12, 368000) in periods
    assert len(periods) == 13
    assert (2026, 1, 5) in occ
    assert (2025, 12, 0) in occ
    assert (2026, 1, 0) not in occ


def test_empty_sources_and_monthly_emit_zero_child_envelopes(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    item = _result(document)["items"][0]
    item["sources"] = []
    item["monthly_searches"] = []
    store = create_store(tmp_path / "empty-children")
    _commit_complete(store, _encode(document), "16" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        sources = connection.execute(
            "SELECT count(*) FROM search_mentions_sources WHERE question = 'enception'"
        ).fetchone()
        monthly = connection.execute(
            """
            SELECT count(*) FROM search_mentions_monthly_search_volume
            WHERE question = 'enception'
            """
        ).fetchone()
        items = connection.execute("SELECT count(*) FROM search_mentions_items").fetchone()
        all_sources = connection.execute("SELECT count(*) FROM search_mentions_sources").fetchone()
        all_monthly = connection.execute(
            "SELECT count(*) FROM search_mentions_monthly_search_volume"
        ).fetchone()
    assert items == (5,)
    assert sources == (0,)
    assert monthly == (0,)
    assert all_sources == (41,)
    assert all_monthly == (48,)


def test_item_and_monthly_reorder_preserve_semantic_identities() -> None:
    document = _decoded()
    items = list(_result(document)["items"])
    original = plan_search_mentions_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(document)
    )
    items.reverse()
    _set_items(document, items)
    reordered_items = plan_search_mentions_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(document)
    )
    original_ids = {
        (item.observation_kind, item.within_capture_identity)
        for item in original.envelopes
    }
    reordered_ids = {
        (item.observation_kind, item.within_capture_identity)
        for item in reordered_items.envelopes
    }
    assert original_ids == reordered_ids
    original_index = {
        row["within_capture_identity"]: row["item_index"]
        for row in original.item_occurrences
    }
    reordered_index = {
        row["within_capture_identity"]: row["item_index"]
        for row in reordered_items.item_occurrences
    }
    assert original_index.keys() == reordered_index.keys()
    assert original_index != reordered_index
    monthly_doc = _decoded()
    monthly_doc["tasks"][0]["result"][0]["items"][0]["monthly_searches"].reverse()
    reordered_months = plan_search_mentions_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(monthly_doc)
    )
    original_monthly = {
        item.within_capture_identity
        for item in original.envelopes
        if item.observation_kind == MONTHLY_KIND
    }
    reordered_monthly = {
        item.within_capture_identity
        for item in reordered_months.envelopes
        if item.observation_kind == MONTHLY_KIND
    }
    assert original_monthly == reordered_monthly


def test_zero_item_page_writes_admitted_empty_outcome(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    _set_items(document, [])
    store = create_store(tmp_path / "empty")
    _attempt_id, capture_id = _commit_complete(store, _encode(document), "17" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_search_mentions(store, connection)
        outcome = connection.execute(
            "SELECT classification, observation_count FROM outcomes WHERE capture_id = %s",
            (capture_id,),
        ).fetchone()
        envelopes = connection.execute("SELECT count(*) FROM observation_envelopes").fetchone()
        context = connection.execute(
            "SELECT items_count, total_count FROM search_mentions_result_context"
        ).fetchone()
    assert summary.observations == 0
    assert outcome == ("observation_admitted_empty", 0)
    assert envelopes == (0,)
    assert context == (0, 3055)


def test_constraints_reject_wrong_kind_orphan_and_invalid_keys(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "constraints")
    _commit_complete(store, _body(), "18" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        connection.commit()
        item = connection.execute(
            """
            SELECT capture_id, derivation_version_id, within_capture_identity
            FROM search_mentions_items LIMIT 1
            """
        ).fetchone()
        assert item is not None
        with pytest.raises(UniqueViolation):
            connection.execute(
                """
                INSERT INTO search_mentions_item_occurrences (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, item_index
                )
                VALUES (%s, %s, %s, %s, 0)
                """,
                (*item, ITEM_KIND),
            )
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute(
                """
                INSERT INTO search_mentions_item_occurrences (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, item_index
                )
                VALUES (%s, %s, %s, %s, -1)
                """,
                (*item, ITEM_KIND),
            )
        connection.rollback()
        source = connection.execute(
            """
            SELECT capture_id, derivation_version_id, within_capture_identity
            FROM search_mentions_sources LIMIT 1
            """
        ).fetchone()
        assert source is not None
        with pytest.raises(ForeignKeyViolation):
            connection.execute(
                """
                INSERT INTO search_mentions_source_occurrences (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, item_index, rank
                )
                VALUES (%s, %s, %s, %s, 0, 1)
                """,
                (*item, SOURCE_KIND),
            )
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute(
                """
                INSERT INTO search_mentions_source_occurrences (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, item_index, rank
                )
                VALUES (%s, %s, %s, %s, 0, 0)
                """,
                (*source, SOURCE_KIND),
            )
        connection.rollback()
        with pytest.raises((CheckViolation, ForeignKeyViolation)):
            connection.execute(
                """
                INSERT INTO search_mentions_items (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, requested_keyword, platform, model_name,
                    location_code, language_code, question, answer,
                    ai_search_volume, is_web_search_based, first_response_at,
                    last_response_at, search_results_state, brand_entities_state,
                    fan_out_queries_state
                )
                VALUES (
                    %s, %s, %s, %s, 'x', 'google', 'google_ai_overview', 2840, 'en',
                    'q', 'a', 0, TRUE, '2026-01-01 00:00:00 +00:00',
                    '2026-01-01 00:00:00 +00:00', 'json_null', 'json_null', 'json_null'
                )
                """,
                (*item, SOURCE_KIND),
            )
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute(
                """
                UPDATE search_mentions_items
                SET search_results_state = 'stated'
                WHERE within_capture_identity = %s
                """,
                (item[2],),
            )
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute(
                """
                UPDATE search_mentions_result_context
                SET search_after_token = NULL, search_after_token_state = 'stated'
                """
            )


def test_result_context_requires_matching_outcome(postgres_dsn: str) -> None:
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, SEARCH_MENTIONS_RECIPE)
        connection.commit()
        with pytest.raises(ForeignKeyViolation):
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
                    %s, %s, %s, 'generative engine optimization', 'word_match',
                    'include', ARRAY['answer'], 'google', 2840, 'en', 5, 0,
                    0, 0, 0, NULL, 'json_null'
                )
                """,
                ("ab" * 32, SEARCH_MENTIONS_RECIPE_ID, "cd" * 32),
            )


def test_transport_parse_reconciliation_and_damage_paths(
    tmp_path: Path, postgres_dsn: str
) -> None:
    apply_migrations(postgres_dsn)
    request = mentions_request_body_bytes(_parameters())
    no_response = create_store(tmp_path / "no-response")
    attempt = _attempt("21" * 32)
    no_response.commit_attempt(attempt, request_body=request)
    no_response.commit_capture(
        mentions_http_capture_document(
            attempt=attempt,
            request_started_at="2026-08-20T17:36:01.100000Z",
            transport_ended_at="2026-08-20T17:36:01.400000Z",
            transport_state="no_response",
            response=None,
            transport_failure={"phase": "connect", "code": "timeout"},
            response_headers_at=None,
            response_body_ended_at=None,
        ),
        response_body=None,
    )
    with connect(postgres_dsn) as connection:
        derive_search_mentions(no_response, connection)
        row = connection.execute(
            "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchone()
    assert row == ("no_response",)

    empty_body = create_store(tmp_path / "empty-body")
    empty_attempt = _attempt("28" * 32)
    empty_bytes = b""
    empty_body.commit_attempt(empty_attempt, request_body=request)
    empty_body.commit_capture(
        mentions_http_capture_document(
            attempt=empty_attempt,
            request_started_at="2026-08-20T17:36:03.100000Z",
            transport_ended_at="2026-08-20T17:36:03.400000Z",
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
            response_headers_at="2026-08-20T17:36:03.200000Z",
            response_body_ended_at="2026-08-20T17:36:03.300000Z",
        ),
        response_body=empty_bytes,
    )
    with connect(postgres_dsn) as connection:
        derive_search_mentions(empty_body, connection)
        classes = {
            item[0]
            for item in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
    assert "transport_complete_non_admissible" in classes

    partial = create_store(tmp_path / "partial")
    partial_attempt = _attempt("27" * 32)
    chunk = _body()[:32]
    partial.commit_attempt(partial_attempt, request_body=request)
    partial.commit_capture(
        mentions_http_capture_document(
            attempt=partial_attempt,
            request_started_at="2026-08-20T17:36:02.100000Z",
            transport_ended_at="2026-08-20T17:36:02.400000Z",
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
            response_headers_at="2026-08-20T17:36:02.200000Z",
            response_body_ended_at="2026-08-20T17:36:02.300000Z",
        ),
        response_body=chunk,
    )
    with connect(postgres_dsn) as connection:
        derive_search_mentions(partial, connection)
        classes = {
            item[0]
            for item in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
    assert "response_partial" in classes

    recon_doc = _decoded()
    _result(recon_doc)["offset"] = 1
    recon = create_store(tmp_path / "recon")
    _commit_complete(recon, _encode(recon_doc), "22" * 32)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(recon, connection)
        classes = {
            row[0]
            for row in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
    assert "reconciliation_failed" in classes

    error_doc = _decoded()
    error_doc["status_code"] = 40100
    error_doc["tasks"][0]["status_code"] = 40100
    error_doc["tasks_error"] = 1
    error_store = create_store(tmp_path / "provider-error")
    _commit_complete(error_store, _encode(error_doc), "24" * 32)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(error_store, connection)
        classes = {
            row[0]
            for row in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
    assert "provider_error" in classes

    bad_doc = _decoded()
    _result(bad_doc)["items_count"] = 4
    bad_store = create_store(tmp_path / "envelope")
    _commit_complete(bad_store, _encode(bad_doc), "25" * 32)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(bad_store, connection)
        classes = {
            row[0]
            for row in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
    assert "provider_envelope_rejected" in classes

    damaged = create_store(tmp_path / "damaged")
    attempt_id, capture_id = _commit_complete(damaged, _body(), "23" * 32)
    body_path = damaged.capture_path(capture_id) / "response.body"
    flipped = bytearray(body_path.read_bytes())
    flipped[0] ^= 0x01
    body_path.write_bytes(bytes(flipped))
    with connect(postgres_dsn) as connection:
        summary = derive_search_mentions(damaged, connection)
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
    assert attempt_row == ("authorized_unresolved",)
    assert capture_rows == (0,)
    assert summary.integrity_failures >= 1


def test_exact_content_extra_rows_missing_restore_and_foreign_attempt(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_complete(store, _body(), "31" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        first = derive_search_mentions(store, connection)
        second = derive_search_mentions(store, connection)
        assert first == second
        original_answer = connection.execute(
            "SELECT answer FROM search_mentions_items WHERE question = 'seos'"
        ).fetchone()
        assert original_answer is not None
        connection.execute(
            "UPDATE search_mentions_items SET answer = 'planted conflict' WHERE question = 'seos'"
        )
        connection.commit()
        with pytest.raises(DerivationError, match="conflicting"):
            derive_search_mentions(store, connection)
        connection.rollback()
        connection.execute(
            "UPDATE search_mentions_items SET answer = %s WHERE question = 'seos'",
            (original_answer[0],),
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
            WHERE observation_kind = %s
            LIMIT 1
            """,
            (extra_identity, ITEM_KIND),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch"):
            derive_search_mentions(store, connection)
        connection.rollback()
        connection.execute(
            "DELETE FROM observation_envelopes WHERE within_capture_identity = %s",
            (extra_identity,),
        )
        connection.commit()
        extra_occ = connection.execute(
            """
            SELECT capture_id, derivation_version_id, within_capture_identity,
                   observation_kind
            FROM search_mentions_item_occurrences LIMIT 1
            """
        ).fetchone()
        assert extra_occ is not None
        connection.execute(
            """
            INSERT INTO search_mentions_item_occurrences (
                capture_id, derivation_version_id, within_capture_identity,
                observation_kind, item_index
            )
            VALUES (%s, %s, %s, %s, 99)
            """,
            extra_occ,
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch"):
            derive_search_mentions(store, connection)
        connection.rollback()
        connection.execute(
            "DELETE FROM search_mentions_item_occurrences WHERE item_index = 99"
        )
        connection.commit()
        connection.execute(
            "DELETE FROM search_mentions_item_occurrences WHERE item_index = 4"
        )
        connection.commit()
        restored = derive_search_mentions(store, connection)
        occ_count = connection.execute(
            "SELECT count(*) FROM search_mentions_item_occurrences"
        ).fetchone()
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, 'observation_admitted', 113)
            """,
            ("cd" * 32, capture_id, SEARCH_MENTIONS_RECIPE_ID),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch"):
            derive_search_mentions(store, connection)
        connection.rollback()
        after = connection.execute(
            """
            SELECT attempt_id FROM outcomes WHERE capture_id = %s ORDER BY attempt_id
            """,
            (capture_id,),
        ).fetchall()
    assert restored.observations == 113
    assert occ_count == (5,)
    assert (attempt_id,) in after
    assert ("cd" * 32,) in after


def test_wrong_outcome_count_and_extra_diagnostic_fail_closed(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "wrong-count")
    attempt_id, capture_id = _commit_complete(store, _body(), "42" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        connection.commit()
        before_items = connection.execute(
            "SELECT count(*) FROM search_mentions_items"
        ).fetchone()
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = 0
            WHERE capture_id = %s
              AND attempt_id = %s
              AND derivation_version_id = %s
            """,
            (capture_id, attempt_id, SEARCH_MENTIONS_RECIPE_ID),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="conflicting provider outcome"):
            derive_search_mentions(store, connection)
        connection.rollback()
        corrupted = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE capture_id = %s AND attempt_id = %s AND derivation_version_id = %s
            """,
            (capture_id, attempt_id, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchone()
        after_items = connection.execute(
            "SELECT count(*) FROM search_mentions_items"
        ).fetchone()
        assert corrupted == ("observation_admitted", 0)
        assert after_items == before_items == (5,)
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = 113
            WHERE capture_id = %s
              AND attempt_id = %s
              AND derivation_version_id = %s
            """,
            (capture_id, attempt_id, SEARCH_MENTIONS_RECIPE_ID),
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
            (SEARCH_MENTIONS_RECIPE_ID, attempt_id, capture_id),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch: diagnostics"):
            derive_search_mentions(store, connection)
        connection.rollback()
        leftover = connection.execute(
            """
            SELECT diagnostic_code FROM derivation_diagnostics
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchall()
        restored_count = connection.execute(
            """
            SELECT observation_count FROM outcomes
            WHERE capture_id = %s AND attempt_id = %s AND derivation_version_id = %s
            """,
            (capture_id, attempt_id, SEARCH_MENTIONS_RECIPE_ID),
        ).fetchone()
    assert leftover == [("planted_extra",)]
    assert restored_count == (113,)


def test_second_recipe_coexists_for_the_same_capture(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "coexist")
    attempt_id, capture_id = _commit_complete(store, _body(), "32" * 32)
    apply_migrations(postgres_dsn)
    second = _second_recipe()
    with connect(postgres_dsn) as connection:
        derive_search_mentions(store, connection)
        registered = register_provider_recipe(connection, second)
        assert registered.derivation_version_id != SEARCH_MENTIONS_RECIPE_ID
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, 'observation_admitted', 1)
            """,
            (attempt_id, capture_id, registered.derivation_version_id),
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
            (capture_id, registered.derivation_version_id, attempt_id, KEYWORD),
        )
        extra_identity = "ef" * 32
        write_observation_envelope(
            connection,
            ObservationEnvelope(
                capture_id=capture_id,
                attempt_id=attempt_id,
                derivation_version_id=registered.derivation_version_id,
                provider="dataforseo",
                adapter_contract=MENTIONS_ADAPTER_CONTRACT,
                observation_kind=ITEM_KIND,
                within_capture_identity=extra_identity,
            ),
        )
        connection.commit()
        rerun = derive_search_mentions(store, connection)
        outcomes = connection.execute(
            """
            SELECT derivation_version_id, observation_count
            FROM outcomes WHERE capture_id = %s
            ORDER BY derivation_version_id
            """,
            (capture_id,),
        ).fetchall()
        contexts = connection.execute(
            """
            SELECT derivation_version_id, search_after_token
            FROM search_mentions_result_context
            ORDER BY derivation_version_id
            """
        ).fetchall()
        second_envelopes = connection.execute(
            """
            SELECT count(*) FROM observation_envelopes
            WHERE derivation_version_id = %s
            """,
            (registered.derivation_version_id,),
        ).fetchone()
        first_envelopes = connection.execute(
            """
            SELECT count(*) FROM observation_envelopes
            WHERE derivation_version_id = %s
            """,
            (SEARCH_MENTIONS_RECIPE_ID,),
        ).fetchone()
    assert rerun.observations == 113
    assert (SEARCH_MENTIONS_RECIPE_ID, 113) in outcomes
    assert (registered.derivation_version_id, 1) in outcomes
    assert second_envelopes == (1,)
    assert first_envelopes == (113,)
    tokens = {row[0]: row[1] for row in contexts}
    assert tokens[registered.derivation_version_id] == "other-token"
    assert tokens[SEARCH_MENTIONS_RECIPE_ID] != "other-token"


def test_populated_pf15_schema_then_mentions_derive(
    tmp_path: Path, postgres_dsn: str
) -> None:
    joined_pre = "\n".join(PRE_AI05_SCHEMA_STATEMENTS)
    assert "google_organic_result_context" in joined_pre
    assert "keyword_overview_coverage" in joined_pre
    assert "search_mentions_" not in joined_pre
    mentions_statements = [
        statement
        for statement in SCHEMA_STATEMENTS
        if statement not in PRE_AI05_SCHEMA_STATEMENTS
    ]
    assert len(mentions_statements) == 7
    assert any("search_mentions_items" in item for item in mentions_statements)
    assert any("search_mentions_result_context" in item for item in mentions_statements)
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
        for statement in PRE_AI05_SCHEMA_STATEMENTS:
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
        before_coverage = connection.execute(
            "SELECT requested_keyword FROM keyword_overview_coverage"
        ).fetchall()
        before_features = connection.execute(
            "SELECT item_type FROM google_organic_serp_features"
        ).fetchall()
        before_observations = connection.execute(
            "SELECT label FROM observations"
        ).fetchall()
        connection.commit()
        apply_schema(connection)
        after_coverage = connection.execute(
            "SELECT requested_keyword FROM keyword_overview_coverage"
        ).fetchall()
        after_features = connection.execute(
            "SELECT item_type FROM google_organic_serp_features"
        ).fetchall()
        after_observations = connection.execute(
            "SELECT label FROM observations"
        ).fetchall()
        for table in (
            "search_mentions_items",
            "search_mentions_item_occurrences",
            "search_mentions_monthly_search_volume",
            "search_mentions_monthly_occurrences",
            "search_mentions_sources",
            "search_mentions_source_occurrences",
            "search_mentions_result_context",
        ):
            connection.execute(f"SELECT 1 FROM {table} LIMIT 0")
    assert before_coverage == after_coverage == [("seo api",)]
    assert before_features == after_features == [("organic",)]
    assert before_observations == after_observations == [("fixture-result-1",)]

    mentions = create_store(tmp_path / "mentions")
    _commit_complete(mentions, _body(), "33" * 32)
    with connect(postgres_dsn) as connection:
        summary = derive_search_mentions(mentions, connection)
        ko_final = connection.execute("SELECT count(*) FROM keyword_overview_coverage").fetchone()
        organic_final = connection.execute(
            "SELECT count(*) FROM google_organic_serp_features"
        ).fetchone()
        fixture_final = connection.execute("SELECT count(*) FROM observations").fetchone()
    assert summary.observations == 113
    assert ko_final == (1,)
    assert organic_final == (1,)
    assert fixture_final == (1,)


def test_fresh_and_upgraded_mentions_catalog_match(
    postgres_dsn: str, postgres_second_dsn: str
) -> None:
    with connect(postgres_dsn) as connection:
        for statement in PRE_AI05_SCHEMA_STATEMENTS:
            connection.execute(statement)
        connection.commit()
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)
    with connect(postgres_dsn) as upgraded, connect(postgres_second_dsn) as fresh:
        assert _mentions_catalog(upgraded) == _mentions_catalog(fresh)
        assert _mentions_catalog(upgraded)[0]
        assert _mentions_catalog(upgraded)[1]


def test_two_databases_are_logically_equivalent(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "34" * 32)
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)

    def snapshot(dsn: str) -> tuple[object, ...]:
        with connect(dsn) as connection:
            derive_search_mentions(store, connection)
            parts: list[object] = []
            catalog: list[tuple[str, tuple[str, ...]]] = []
            for table in AI05_TABLES:
                columns, rows = _fetch_relation(connection, table)
                catalog.append((table, columns))
                parts.append(rows)
            assert tuple(name for name, _columns in catalog) == AI05_TABLES
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
            assert "tableoid" not in columns
            assert "xmin" not in columns
            assert "ctid" not in columns


def test_fixture_derive_skips_mentions_and_mentions_skips_fixture(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "35" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        fixture_summary = derive(store, connection, derivation_version_id=DEFAULT_VERSION)
        before = connection.execute("SELECT count(*) FROM search_mentions_items").fetchone()
        derive_search_mentions(store, connection)
        after = connection.execute("SELECT count(*) FROM search_mentions_items").fetchone()
    assert fixture_summary.observations == 0
    assert before == (0,)
    assert after == (5,)
