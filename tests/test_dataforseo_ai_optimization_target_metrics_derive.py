"""AI-11: Target Metrics provider Derivation into real PostgreSQL."""

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

from observatory.capture_event import (
    MENTIONS_ADAPTER_CONTRACT,
    ORGANIC_ADAPTER_CONTRACT,
    PAID_ADAPTER_CONTRACT,
    TARGET_METRICS_ADAPTER_CONTRACT,
    body_ref,
    target_metrics_http_attempt_document,
    target_metrics_http_capture_document,
)
from observatory.dataforseo_ai_optimization_search_mentions import (
    SEARCH_MENTIONS_RECIPE,
    SEARCH_MENTIONS_RECIPE_ID,
)
from observatory.dataforseo_ai_optimization_target_metrics import (
    SOURCE_DOMAIN_KIND,
    TOTAL_KIND,
    parse_target_metrics,
)
from observatory.dataforseo_ai_optimization_target_metrics_paid_probe import (
    closed_target_metrics_parameters,
    target_metrics_request_body_bytes,
)
from observatory.dataforseo_google_organic import (
    FEATURE_PRESENCE_KIND,
    GOOGLE_ORGANIC_RECIPE,
    GOOGLE_ORGANIC_RECIPE_ID,
)
from observatory.dataforseo_keyword_overview import CORE_RECIPE, CORE_RECIPE_ID, COVERAGE_KIND
from observatory.derive import DEFAULT_VERSION, DerivationError, derive
from observatory.evidence_store import EvidenceStore, create_store
from observatory.migrate import (
    PRE_AI05_SCHEMA_STATEMENTS,
    PRE_AI11_SCHEMA_STATEMENTS,
    PRE_AI16_SCHEMA_STATEMENTS,
    PRE_PF12_SCHEMA_STATEMENTS,
    PRE_RK04_SCHEMA_STATEMENTS,
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
    recipe_derivation_version_id,
    register_provider_recipe,
    validate_recipe,
    write_observation_envelope,
)
from observatory.target_metrics_derive import (
    TARGET_METRICS_RECIPE,
    TARGET_METRICS_RECIPE_BYTES,
    TARGET_METRICS_RECIPE_ID,
    derive_target_metrics,
    plan_target_metrics_capture,
    target_metrics_recipe,
)

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_ai_optimization_target_metrics_ai09.json"
)
KEYWORD = "generative engine optimization"
OTHER_KEYWORD = "other keyword"
AI09_BODY_BYTES = 1775
AI09_BODY_SHA256 = "7b6974704f73cff9687986a83ab14ba8ec942ccdbfde359ec7e8fde6bea8eee2"
ACCEPTED_RECIPE_ID = "b6addc49c60eff18de7aaf5dc6c35ebffa93e242649d5e2ddd009822b12e5104"
ACCEPTED_RECIPE_BYTES = 1586
ACCEPTED_ORGANIC = "338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde"
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
SOURCE_MENTION_SUM = 4415
SOURCE_VOLUME_SUM = 3187610
IJSON_MAX = 9007199254740991
AI11_TABLES = (
    "target_metrics_totals",
    "target_metrics_source_domains",
    "target_metrics_result_context",
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


def _attempt(nonce: str, *, keyword: str = KEYWORD) -> dict[str, object]:
    return target_metrics_http_attempt_document(
        parameters=_parameters(keyword=keyword),
        attempt_nonce=nonce,
        authorized_at="2026-08-24T03:09:00.000000Z",
        observatory_version="ai11-test-v1",
    )


def _complete_capture(
    attempt: dict[str, object], body: bytes, *, suffix: str = "1"
) -> dict[str, object]:
    return target_metrics_http_capture_document(
        attempt=attempt,
        request_started_at=f"2026-08-24T03:09:0{suffix}.100000Z",
        transport_ended_at=f"2026-08-24T03:09:0{suffix}.400000Z",
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
        response_headers_at=f"2026-08-24T03:09:0{suffix}.200000Z",
        response_body_ended_at=f"2026-08-24T03:09:0{suffix}.300000Z",
    )


def _commit_complete(
    store: Any, body: bytes, nonce: str, *, keyword: str = KEYWORD
) -> tuple[str, str]:
    attempt = _attempt(nonce, keyword=keyword)
    request = target_metrics_request_body_bytes(_parameters(keyword=keyword))
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


def _agg(document: dict[str, Any]) -> dict[str, Any]:
    metrics = _result(document)["aggregated_metrics"]
    assert isinstance(metrics, dict)
    return metrics


def _row(key: object, mentions: int = 1, volume: int = 2) -> dict[str, object]:
    return {"key": key, "mentions": mentions, "ai_search_volume": volume}


def _complete_capture_dict() -> dict[str, object]:
    return {
        "transport_state": "response_complete",
        "response": {"completeness": "complete"},
    }


def _kind_counts(planned: Any) -> dict[str, int]:
    counts = {TOTAL_KIND: 0, SOURCE_DOMAIN_KIND: 0}
    for envelope in planned.envelopes:
        counts[envelope.observation_kind] += 1
    return counts


def _second_recipe() -> dict[str, object]:
    document = copy.deepcopy(TARGET_METRICS_RECIPE)
    document["reconciliation"] = {"rule": "attempt_grouping_key_singleton_v2"}
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


def _tm_catalog(connection: Any) -> tuple[tuple[Any, ...], ...]:
    constraints = connection.execute(
        """
        SELECT c.relname, con.conname, con.contype, pg_get_constraintdef(con.oid)
        FROM pg_constraint AS con
        JOIN pg_class AS c ON c.oid = con.conrelid
        JOIN pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname = current_schema()
          AND c.relname LIKE 'target_metrics_%'
        ORDER BY 1, 2, 4
        """
    ).fetchall()
    columns = connection.execute(
        """
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name LIKE 'target_metrics_%'
        ORDER BY 1, 2
        """
    ).fetchall()
    return tuple(constraints), tuple(columns)


def _semantic_identity(kind: str, axes: dict[str, object]) -> str:
    return observation_identity(
        {
            "axes": axes,
            "observation_kind": kind,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        TARGET_METRICS_RECIPE,
    )


def _expected_frozen_rows(
    attempt_id: str, capture_id: str, parsed: Any
) -> dict[str, list[dict[str, object]]]:
    request = parsed.request
    keyword = request.keyword
    recipe_id = TARGET_METRICS_RECIPE_ID
    metrics = parsed.aggregated_metrics
    assert metrics is not None
    totals = [
        {
            "capture_id": capture_id,
            "derivation_version_id": recipe_id,
            "within_capture_identity": _semantic_identity(
                TOTAL_KIND, {"requested_keyword": keyword}
            ),
            "observation_kind": TOTAL_KIND,
            "requested_keyword": keyword,
            "mentions": metrics.total.mentions,
            "ai_search_volume": metrics.total.ai_search_volume,
        }
    ]
    sources = [
        {
            "capture_id": capture_id,
            "derivation_version_id": recipe_id,
            "within_capture_identity": _semantic_identity(
                SOURCE_DOMAIN_KIND,
                {"domain": row.key, "requested_keyword": keyword},
            ),
            "observation_kind": SOURCE_DOMAIN_KIND,
            "requested_keyword": keyword,
            "domain": row.key,
            "mentions": row.mentions,
            "ai_search_volume": row.ai_search_volume,
            "provider_array_index": row.provider_array_index,
        }
        for row in metrics.sources_domain
    ]
    location = metrics.location[0]
    language = metrics.language[0]
    platform = metrics.platform[0]

    def optional_count(field: Any) -> tuple[int | None, str]:
        if field.state.value == "stated":
            return len(field.value), field.state.value
        return None, str(field.state.value)

    search_count, search_state = optional_count(metrics.search_results_domain)
    title_count, title_state = optional_count(metrics.brand_entities_title)
    category_count, category_state = optional_count(metrics.brand_entities_category)
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
            "internal_list_limit": request.internal_list_limit,
            "total_count": parsed.total_count,
            "result_offset": parsed.offset,
            "items_count": parsed.items_count,
            "items_state": parsed.items.state.value,
            "location_key": location.key,
            "location_mentions": location.mentions,
            "location_ai_search_volume": location.ai_search_volume,
            "location_provider_array_index": location.provider_array_index,
            "location_row_count": len(metrics.location),
            "language_key": language.key,
            "language_mentions": language.mentions,
            "language_ai_search_volume": language.ai_search_volume,
            "language_provider_array_index": language.provider_array_index,
            "language_row_count": len(metrics.language),
            "platform_key": platform.key,
            "platform_mentions": platform.mentions,
            "platform_ai_search_volume": platform.ai_search_volume,
            "platform_provider_array_index": platform.provider_array_index,
            "platform_row_count": len(metrics.platform),
            "sources_domain_count": len(metrics.sources_domain),
            "search_results_domain_count": search_count,
            "search_results_domain_state": search_state,
            "brand_entities_title_count": title_count,
            "brand_entities_title_state": title_state,
            "brand_entities_category_count": category_count,
            "brand_entities_category_state": category_state,
        }
    ]
    return {
        "target_metrics_totals": totals,
        "target_metrics_source_domains": sources,
        "target_metrics_result_context": context,
    }


def _assert_no_facts(connection: Any) -> None:
    totals = connection.execute("SELECT count(*) FROM target_metrics_totals").fetchone()
    sources = connection.execute(
        "SELECT count(*) FROM target_metrics_source_domains"
    ).fetchone()
    context = connection.execute(
        "SELECT count(*) FROM target_metrics_result_context"
    ).fetchone()
    assert totals == (0,)
    assert sources == (0,)
    assert context == (0,)


def test_accepted_recipe_and_fixture_identities_remain_unchanged() -> None:
    assert TARGET_METRICS_RECIPE_ID == ACCEPTED_RECIPE_ID
    assert len(TARGET_METRICS_RECIPE_BYTES) == ACCEPTED_RECIPE_BYTES
    assert hashlib.sha256(TARGET_METRICS_RECIPE_BYTES).hexdigest() == ACCEPTED_RECIPE_ID
    assert recipe_derivation_version_id(target_metrics_recipe()) == ACCEPTED_RECIPE_ID
    assert target_metrics_recipe() == TARGET_METRICS_RECIPE
    admission = TARGET_METRICS_RECIPE["admission"]
    assert isinstance(admission, dict)
    outcomes = admission["capture_outcomes"]
    assert isinstance(outcomes, list)
    assert "observation_admitted_empty" not in outcomes
    assert TARGET_METRICS_RECIPE["observation_kinds"] == [TOTAL_KIND, SOURCE_DOMAIN_KIND]
    raw = _body()
    assert len(raw) == AI09_BODY_BYTES
    assert hashlib.sha256(raw).hexdigest() == AI09_BODY_SHA256
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert not raw.endswith(b"\n")
    assert CORE_RECIPE_ID == "319af798f3e0b3e5fe4579539442c4ca5d384b683e1f4bce0f7a1b3e26cd5908"
    assert GOOGLE_ORGANIC_RECIPE_ID == ACCEPTED_ORGANIC
    assert SEARCH_MENTIONS_RECIPE_ID == (
        "bd3dfbf87eba83df35dc7ae6eecd25c223a89ad72d910db346d8ebafb61933e0"
    )
    assert Path("/home/chaz/.local/share/observatory").as_posix() not in str(FIXTURE)


def test_plan_frozen_fixture_has_exact_semantic_counts() -> None:
    parsed = parse_target_metrics(_body(), _parameters())
    planned = plan_target_metrics_capture(
        "a" * 64,
        "b" * 64,
        _complete_capture_dict(),
        _parameters(),
        _body(),
    )
    assert parsed.aggregated_metrics is not None
    expected = 1 + len(parsed.aggregated_metrics.sources_domain)
    assert planned.classification == "observation_admitted"
    assert planned.classification != "observation_admitted_empty"
    assert len(planned.envelopes) == expected == 11
    assert _kind_counts(planned) == {TOTAL_KIND: 1, SOURCE_DOMAIN_KIND: 10}
    assert planned.context is not None
    assert planned.context["sources_domain_count"] == 10
    assert planned.context["internal_list_limit"] == 10
    assert planned.context["location_key"] == 2840
    assert planned.context["location_mentions"] == TOTAL_MENTIONS
    assert planned.context["language_key"] == "en"
    assert planned.context["platform_key"] == "google"
    assert planned.context["items_state"] == "stated"
    assert planned.context["search_results_domain_state"] == "stated"
    assert planned.context["search_results_domain_count"] == 0
    assert "cost" not in planned.context
    assert "task_id" not in planned.context
    assert "echo" not in planned.context
    assert "truncated" not in planned.context
    totals = planned.details["target_metrics_totals"]
    assert totals[0]["mentions"] == TOTAL_MENTIONS
    assert totals[0]["ai_search_volume"] == TOTAL_VOLUME
    domains: list[tuple[str, int, int]] = []
    for row in planned.details["target_metrics_source_domains"]:
        mentions = row["mentions"]
        volume = row["ai_search_volume"]
        assert isinstance(mentions, int)
        assert isinstance(volume, int)
        domains.append((str(row["domain"]), mentions, volume))
    assert tuple(domains) == SOURCE_DOMAINS
    mention_sum = sum(row[1] for row in domains)
    volume_sum = sum(row[2] for row in domains)
    assert mention_sum == SOURCE_MENTION_SUM
    assert volume_sum == SOURCE_VOLUME_SUM
    assert mention_sum > TOTAL_MENTIONS
    assert volume_sum > TOTAL_VOLUME


def test_plan_does_not_copy_parser_outcome_value() -> None:
    document = _decoded()
    _agg(document)["location"][0]["key"] = 2841
    planned = plan_target_metrics_capture(
        "a" * 64,
        "b" * 64,
        _complete_capture_dict(),
        _parameters(),
        _encode(document),
    )
    parsed = parse_target_metrics(_encode(document), _parameters())
    assert parsed.outcome.value == "observation_admitted"
    assert planned.classification == "reconciliation_failed"
    assert planned.envelopes == ()
    assert planned.context is None


def test_plan_grouping_disagreement_with_total_is_admitted() -> None:
    document = _decoded()
    _agg(document)["location"][0]["mentions"] = 1
    _agg(document)["language"][0]["ai_search_volume"] = 2
    _agg(document)["platform"][0]["mentions"] = 3
    planned = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(document)
    )
    assert planned.classification == "observation_admitted"
    assert planned.context is not None
    assert planned.context["location_mentions"] == 1
    assert planned.context["language_ai_search_volume"] == 2
    assert planned.context["platform_mentions"] == 3
    assert planned.details["target_metrics_totals"][0]["mentions"] == TOTAL_MENTIONS


def test_plan_echo_and_path_disagreement_do_not_reject() -> None:
    document = _decoded()
    document["tasks"][0]["data"]["language_code"] = "de"
    document["tasks"][0]["data"]["platform"] = "chat_gpt"
    document["tasks"][0]["data"]["internal_list_limit"] = 3
    document["tasks"][0]["data"]["target"][0]["keyword"] = OTHER_KEYWORD
    document["tasks"][0]["path"] = ["v3", "other"]
    planned = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(document)
    )
    assert planned.classification == "observation_admitted"
    assert planned.context is not None
    assert planned.context["requested_keyword"] == KEYWORD
    assert planned.context["language_code"] == "en"
    assert planned.context["platform"] == "google"
    assert planned.context["internal_list_limit"] == 10


def test_plan_source_count_below_equal_above_limit_is_admitted() -> None:
    parsed = parse_target_metrics(_body(), _parameters())
    assert parsed.aggregated_metrics is not None
    equal = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _body()
    )
    assert len(equal.envelopes) == 1 + len(parsed.aggregated_metrics.sources_domain)
    document = _decoded()
    _agg(document)["sources_domain"] = _agg(document)["sources_domain"][:3]
    below = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(document)
    )
    assert below.classification == "observation_admitted"
    assert len(below.envelopes) == 1 + 3
    assert below.context is not None
    assert below.context["sources_domain_count"] == 3
    assert below.context["internal_list_limit"] == 10
    assert "truncated" not in below.context
    document = _decoded()
    rows = list(_agg(document)["sources_domain"])
    rows.append(_row("above-limit.example", 1, 1))
    _agg(document)["sources_domain"] = rows
    above = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(document)
    )
    assert above.classification == "observation_admitted"
    assert len(above.envelopes) == 1 + 11
    assert above.context is not None
    assert above.context["sources_domain_count"] == 11
    assert above.context["internal_list_limit"] == 10


def test_plan_empty_extra_or_wrong_grouping_is_reconciliation_failed() -> None:
    empty = _decoded()
    _agg(empty)["location"] = []
    planned_empty = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(empty)
    )
    assert planned_empty.classification == "reconciliation_failed"
    extra = _decoded()
    _agg(extra)["language"].append(_row("de", 1, 1))
    planned_extra = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(extra)
    )
    assert planned_extra.classification == "reconciliation_failed"
    wrong = _decoded()
    _agg(wrong)["platform"][0]["key"] = "chat_gpt"
    planned_wrong = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(wrong)
    )
    assert planned_wrong.classification == "reconciliation_failed"
    assert planned_empty.context is planned_extra.context is planned_wrong.context is None


@pytest.mark.parametrize(
    ("family", "key"),
    [
        ("search_results_domain", "results.example"),
        ("brand_entities_title", "Example Brand"),
        ("brand_entities_category", "Software"),
    ],
)
def test_plan_nonempty_optional_family_rejects_whole_unit(
    family: str, key: str
) -> None:
    document = _decoded()
    _agg(document)[family] = [_row(key, 1, 1)]
    planned = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(document)
    )
    assert planned.classification == "provider_envelope_rejected"
    assert planned.envelopes == ()
    assert planned.context is None
    assert planned.details["target_metrics_totals"] == ()
    assert planned.details["target_metrics_source_domains"] == ()


def test_derive_rejects_non_concrete_store_before_schema_or_evidence() -> None:
    class DuckStore:
        def __getattr__(self, name: str) -> object:
            raise AssertionError(f"Evidence read before concrete-store check: {name}")

    class PoisonedConnection:
        def __getattr__(self, name: str) -> object:
            raise AssertionError(f"connection used before concrete-store check: {name}")

    with pytest.raises(TypeError, match="concrete EvidenceStore"):
        derive_target_metrics(DuckStore(), PoisonedConnection())  # type: ignore[arg-type]


def test_plan_empty_identity_and_ijson_overflow_reject() -> None:
    empty_domain = _decoded()
    _agg(empty_domain)["sources_domain"][0]["key"] = ""
    planned_domain = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(empty_domain)
    )
    assert planned_domain.classification == "provider_envelope_rejected"
    overflow = _decoded()
    _agg(overflow)["total"]["mentions"] = IJSON_MAX + 1
    planned_overflow = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(overflow)
    )
    assert planned_overflow.classification == "provider_envelope_rejected"
    empty_keyword = dict(_parameters())
    target = empty_keyword["target"]
    assert isinstance(target, list)
    first_item = target[0]
    assert isinstance(first_item, dict)
    first = dict(first_item)
    first["keyword"] = ""
    empty_keyword["target"] = [first]
    planned_keyword = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), empty_keyword, _body()
    )
    assert planned_keyword.classification == "provider_envelope_rejected"


def test_plan_zero_total_remains_admitted() -> None:
    document = _decoded()
    _agg(document)["total"]["mentions"] = 0
    _agg(document)["total"]["ai_search_volume"] = 0
    planned = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(document)
    )
    assert planned.classification == "observation_admitted"
    assert planned.classification != "observation_admitted_empty"
    assert _kind_counts(planned)[TOTAL_KIND] == 1
    assert planned.details["target_metrics_totals"][0]["mentions"] == 0


def test_plan_optional_and_items_states_are_distinct() -> None:
    absent_items = _decoded()
    del _result(absent_items)["items"]
    planned_absent = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(absent_items)
    )
    null_items = _decoded()
    _result(null_items)["items"] = None
    planned_null = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(null_items)
    )
    assert planned_absent.context is not None
    assert planned_null.context is not None
    assert planned_absent.context["items_state"] == "absent"
    assert planned_null.context["items_state"] == "json_null"
    absent_opt = _decoded()
    del _agg(absent_opt)["brand_entities_title"]
    planned_opt_absent = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(absent_opt)
    )
    null_opt = _decoded()
    _agg(null_opt)["brand_entities_category"] = None
    planned_opt_null = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(null_opt)
    )
    assert planned_opt_absent.context is not None
    assert planned_opt_null.context is not None
    assert planned_opt_absent.context["brand_entities_title_state"] == "absent"
    assert planned_opt_absent.context["brand_entities_title_count"] is None
    assert planned_opt_null.context["brand_entities_category_state"] == "json_null"
    assert planned_opt_null.context["brand_entities_category_count"] is None


def test_plan_source_reorder_preserves_identity_and_changes_index_map() -> None:
    original = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _body()
    )
    original_ids = {
        item.within_capture_identity
        for item in original.envelopes
        if item.observation_kind == SOURCE_DOMAIN_KIND
    }
    original_indexes = {
        row["domain"]: row["provider_array_index"]
        for row in original.details["target_metrics_source_domains"]
    }
    document = _decoded()
    rows = _agg(document)["sources_domain"]
    _agg(document)["sources_domain"] = list(reversed(rows))
    reordered = plan_target_metrics_capture(
        "a" * 64, "b" * 64, _complete_capture_dict(), _parameters(), _encode(document)
    )
    reordered_ids = {
        item.within_capture_identity
        for item in reordered.envelopes
        if item.observation_kind == SOURCE_DOMAIN_KIND
    }
    reordered_indexes = {
        row["domain"]: row["provider_array_index"]
        for row in reordered.details["target_metrics_source_domains"]
    }
    assert original_ids == reordered_ids
    assert original_indexes != reordered_indexes
    assert original_indexes["www.youtube.com"] == 0
    assert reordered_indexes["www.youtube.com"] == 9
    assert reordered_indexes["thriveagency.com"] == 0


def test_derive_ai09_fixture_into_real_postgres(tmp_path: Path, postgres_dsn: str) -> None:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_complete(store, _body(), "11" * 32)
    parsed = parse_target_metrics(_body(), _parameters())
    assert parsed.aggregated_metrics is not None
    expected = _expected_frozen_rows(attempt_id, capture_id, parsed)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_target_metrics(store, connection)
        outcome = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, TARGET_METRICS_RECIPE_ID),
        ).fetchone()
        kinds = connection.execute(
            """
            SELECT observation_kind, count(*)
            FROM observation_envelopes
            WHERE capture_id = %s
            GROUP BY observation_kind
            ORDER BY observation_kind
            """,
            (capture_id,),
        ).fetchall()
        stored: dict[str, list[tuple[object, ...]]] = {}
        for table in AI11_TABLES:
            columns, rows = _fetch_relation(connection, table)
            expected_rows = [
                tuple(_normalize_cell(row[column]) for column in columns)
                for row in expected[table]
            ]
            stored[table] = list(rows)
            assert sorted(rows) == sorted(expected_rows)
    assert summary.observations == 1 + len(parsed.aggregated_metrics.sources_domain)
    assert summary.observations == 11
    assert outcome == ("observation_admitted", 11)
    assert kinds == [(SOURCE_DOMAIN_KIND, 10), (TOTAL_KIND, 1)]
    assert len(stored["target_metrics_result_context"]) == 1


def test_adversarial_bodies_persist_on_postgres(tmp_path: Path, postgres_dsn: str) -> None:
    apply_migrations(postgres_dsn)
    echo_doc = _decoded()
    echo_doc["tasks"][0]["data"]["target"][0]["keyword"] = OTHER_KEYWORD
    echo_doc["tasks"][0]["data"]["language_code"] = "de"
    echo_doc["tasks"][0]["path"] = ["v3", "other"]
    echo_store = create_store(tmp_path / "echo")
    _, echo_capture = _commit_complete(echo_store, _encode(echo_doc), "51" * 32)
    below_doc = _decoded()
    _agg(below_doc)["sources_domain"] = _agg(below_doc)["sources_domain"][:3]
    below_store = create_store(tmp_path / "below")
    _, below_capture = _commit_complete(below_store, _encode(below_doc), "52" * 32)
    above_doc = _decoded()
    rows = list(_agg(above_doc)["sources_domain"])
    rows.append(_row("above-limit.example", 1, 1))
    _agg(above_doc)["sources_domain"] = rows
    above_store = create_store(tmp_path / "above")
    _, above_capture = _commit_complete(above_store, _encode(above_doc), "53" * 32)
    items_null = _decoded()
    _result(items_null)["items"] = None
    del _agg(items_null)["brand_entities_title"]
    _agg(items_null)["brand_entities_category"] = None
    states_store = create_store(tmp_path / "states")
    _, states_capture = _commit_complete(states_store, _encode(items_null), "54" * 32)
    items_absent = _decoded()
    del _result(items_absent)["items"]
    absent_store = create_store(tmp_path / "items-absent")
    _, absent_capture = _commit_complete(absent_store, _encode(items_absent), "57" * 32)
    nonempty = _decoded()
    _agg(nonempty)["search_results_domain"] = [_row("example.com", 1, 1)]
    nonempty_store = create_store(tmp_path / "nonempty")
    _, nonempty_capture = _commit_complete(nonempty_store, _encode(nonempty), "55" * 32)
    zero_domain = _decoded()
    _agg(zero_domain)["sources_domain"][0]["mentions"] = 0
    _agg(zero_domain)["sources_domain"][0]["ai_search_volume"] = 0
    zero_store = create_store(tmp_path / "zero-domain")
    _, zero_capture = _commit_complete(zero_store, _encode(zero_domain), "56" * 32)
    with connect(postgres_dsn) as connection:
        derive_target_metrics(echo_store, connection)
        echo_row = connection.execute(
            """
            SELECT requested_keyword, language_code, classification, observation_count
            FROM target_metrics_result_context AS c
            JOIN outcomes AS o USING (capture_id, derivation_version_id, attempt_id)
            WHERE c.capture_id = %s
            """,
            (echo_capture,),
        ).fetchone()
        derive_target_metrics(below_store, connection)
        below_row = connection.execute(
            """
            SELECT sources_domain_count, observation_count
            FROM target_metrics_result_context AS c
            JOIN outcomes AS o USING (capture_id, derivation_version_id)
            WHERE c.capture_id = %s
            """,
            (below_capture,),
        ).fetchone()
        derive_target_metrics(above_store, connection)
        above_row = connection.execute(
            """
            SELECT sources_domain_count, observation_count, internal_list_limit
            FROM target_metrics_result_context AS c
            JOIN outcomes AS o USING (capture_id, derivation_version_id)
            WHERE c.capture_id = %s
            """,
            (above_capture,),
        ).fetchone()
        derive_target_metrics(states_store, connection)
        derive_target_metrics(absent_store, connection)
        states_row = connection.execute(
            """
            SELECT items_state, brand_entities_title_state, brand_entities_title_count,
                   brand_entities_category_state, brand_entities_category_count,
                   search_results_domain_state, search_results_domain_count
            FROM target_metrics_result_context WHERE capture_id = %s
            """,
            (states_capture,),
        ).fetchone()
        absent_row = connection.execute(
            "SELECT items_state FROM target_metrics_result_context WHERE capture_id = %s",
            (absent_capture,),
        ).fetchone()
        derive_target_metrics(nonempty_store, connection)
        nonempty_outcome = connection.execute(
            """
            SELECT classification, observation_count FROM outcomes
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (nonempty_capture, TARGET_METRICS_RECIPE_ID),
        ).fetchone()
        nonempty_context = connection.execute(
            "SELECT count(*) FROM target_metrics_result_context WHERE capture_id = %s",
            (nonempty_capture,),
        ).fetchone()
        derive_target_metrics(zero_store, connection)
        zero_row = connection.execute(
            """
            SELECT mentions, ai_search_volume FROM target_metrics_source_domains
            WHERE capture_id = %s AND domain = 'www.youtube.com'
            """,
            (zero_capture,),
        ).fetchone()
    assert echo_row == (KEYWORD, "en", "observation_admitted", 11)
    assert below_row == (3, 4)
    assert above_row == (11, 12, 10)
    assert states_row == ("json_null", "absent", None, "json_null", None, "stated", 0)
    assert absent_row == ("absent",)
    assert nonempty_outcome == ("provider_envelope_rejected", 0)
    assert nonempty_context == (0,)
    assert zero_row == (0, 0)


def test_zero_total_writes_admitted_outcome(tmp_path: Path, postgres_dsn: str) -> None:
    document = _decoded()
    _agg(document)["total"]["mentions"] = 0
    _agg(document)["total"]["ai_search_volume"] = 0
    store = create_store(tmp_path / "zero")
    _commit_complete(store, _encode(document), "12" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_target_metrics(store, connection)
        outcome = connection.execute(
            "SELECT classification, observation_count FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchone()
        mentions = connection.execute(
            "SELECT mentions FROM target_metrics_totals"
        ).fetchone()
    assert summary.observations == 11
    assert outcome == ("observation_admitted", 11)
    assert mentions == (0,)


def test_constraints_reject_wrong_kind_orphan_index_and_state(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "constraints")
    _commit_complete(store, _body(), "13" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_target_metrics(store, connection)
        connection.commit()
        total = connection.execute(
            """
            SELECT capture_id, derivation_version_id, within_capture_identity
            FROM target_metrics_totals LIMIT 1
            """
        ).fetchone()
        assert total is not None
        with pytest.raises((CheckViolation, ForeignKeyViolation)):
            connection.execute(
                """
                INSERT INTO target_metrics_totals (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, requested_keyword, mentions, ai_search_volume
                )
                VALUES (%s, %s, %s, %s, 'x', 0, 0)
                """,
                (*total, SOURCE_DOMAIN_KIND),
            )
        connection.rollback()
        with pytest.raises(ForeignKeyViolation):
            connection.execute(
                """
                INSERT INTO target_metrics_source_domains (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, requested_keyword, domain, mentions,
                    ai_search_volume, provider_array_index
                )
                VALUES (%s, %s, %s, %s, 'kw', 'example.com', 1, 1, 99)
                """,
                (*total, SOURCE_DOMAIN_KIND),
            )
        connection.rollback()
        source = connection.execute(
            """
            SELECT capture_id, derivation_version_id, provider_array_index
            FROM target_metrics_source_domains LIMIT 1
            """
        ).fetchone()
        assert source is not None
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
            (extra_identity, SOURCE_DOMAIN_KIND),
        )
        with pytest.raises(UniqueViolation):
            connection.execute(
                """
                INSERT INTO target_metrics_source_domains (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, requested_keyword, domain, mentions,
                    ai_search_volume, provider_array_index
                )
                VALUES (%s, %s, %s, %s, 'kw', 'dup.example', 1, 1, %s)
                """,
                (source[0], source[1], extra_identity, SOURCE_DOMAIN_KIND, source[2]),
            )
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute(
                "UPDATE target_metrics_totals SET mentions = %s",
                (IJSON_MAX + 1,),
            )
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute("UPDATE target_metrics_totals SET mentions = -1")
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute(
                """
                UPDATE target_metrics_result_context
                SET search_results_domain_count = NULL,
                    search_results_domain_state = 'stated'
                """
            )
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute("UPDATE target_metrics_totals SET requested_keyword = ''")
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute("UPDATE target_metrics_source_domains SET domain = ''")


def test_result_context_requires_matching_outcome(postgres_dsn: str) -> None:
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, TARGET_METRICS_RECIPE)
        connection.commit()
        with pytest.raises(ForeignKeyViolation):
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
                    %s, %s, %s, 'generative engine optimization', 'word_match',
                    'include', ARRAY['answer'], 'google', 2840, 'en', 10,
                    0, 0, 0, 'stated', 2840, 0, 0, 0, 1,
                    'en', 0, 0, 0, 1, 'google', 0, 0, 0, 1,
                    0, 0, 'stated', 0, 'stated', 0, 'stated'
                )
                """,
                ("ab" * 32, TARGET_METRICS_RECIPE_ID, "cd" * 32),
            )


def test_transport_parse_reconciliation_and_damage_paths(
    tmp_path: Path, postgres_dsn: str
) -> None:
    apply_migrations(postgres_dsn)
    request = target_metrics_request_body_bytes(_parameters())
    no_response = create_store(tmp_path / "no-response")
    attempt = _attempt("21" * 32)
    no_response.commit_attempt(attempt, request_body=request)
    no_response.commit_capture(
        target_metrics_http_capture_document(
            attempt=attempt,
            request_started_at="2026-08-24T03:09:01.100000Z",
            transport_ended_at="2026-08-24T03:09:01.400000Z",
            transport_state="no_response",
            response=None,
            transport_failure={"phase": "connect", "code": "timeout"},
            response_headers_at=None,
            response_body_ended_at=None,
        ),
        response_body=None,
    )
    with connect(postgres_dsn) as connection:
        derive_target_metrics(no_response, connection)
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
        target_metrics_http_capture_document(
            attempt=empty_attempt,
            request_started_at="2026-08-24T03:09:03.100000Z",
            transport_ended_at="2026-08-24T03:09:03.400000Z",
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
            response_headers_at="2026-08-24T03:09:03.200000Z",
            response_body_ended_at="2026-08-24T03:09:03.300000Z",
        ),
        response_body=empty_bytes,
    )
    with connect(postgres_dsn) as connection:
        derive_target_metrics(empty_body, connection)
        classes = {
            item[0]
            for item in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
    assert "transport_complete_non_admissible" in classes

    partial = create_store(tmp_path / "partial")
    partial_attempt = _attempt("23" * 32)
    chunk = _body()[:32]
    partial.commit_attempt(partial_attempt, request_body=request)
    partial.commit_capture(
        target_metrics_http_capture_document(
            attempt=partial_attempt,
            request_started_at="2026-08-24T03:09:02.100000Z",
            transport_ended_at="2026-08-24T03:09:02.400000Z",
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
            response_headers_at="2026-08-24T03:09:02.200000Z",
            response_body_ended_at="2026-08-24T03:09:02.300000Z",
        ),
        response_body=chunk,
    )
    with connect(postgres_dsn) as connection:
        derive_target_metrics(partial, connection)
        classes = {
            item[0]
            for item in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
    assert "response_partial" in classes

    recon_doc = _decoded()
    _agg(recon_doc)["location"][0]["key"] = 2841
    recon = create_store(tmp_path / "recon")
    _commit_complete(recon, _encode(recon_doc), "24" * 32)
    with connect(postgres_dsn) as connection:
        derive_target_metrics(recon, connection)
        classes = {
            row[0]
            for row in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
        _assert_no_facts(connection)
    assert "reconciliation_failed" in classes

    error_doc = _decoded()
    error_doc["status_code"] = 40100
    error_doc["tasks"][0]["status_code"] = 40100
    error_doc["tasks_error"] = 1
    error_doc["tasks"][0]["result_count"] = 9
    error_doc["tasks"][0]["result"] = [{"strange": True}]
    error_store = create_store(tmp_path / "provider-error")
    _commit_complete(error_store, _encode(error_doc), "25" * 32)
    with connect(postgres_dsn) as connection:
        derive_target_metrics(error_store, connection)
        classes = {
            row[0]
            for row in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
        _assert_no_facts(connection)
    assert "provider_error" in classes

    bad_doc = _decoded()
    _result(bad_doc)["total_count"] = 1
    bad_store = create_store(tmp_path / "envelope")
    _commit_complete(bad_store, _encode(bad_doc), "26" * 32)
    with connect(postgres_dsn) as connection:
        derive_target_metrics(bad_store, connection)
        classes = {
            row[0]
            for row in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
    assert "provider_envelope_rejected" in classes

    damaged = create_store(tmp_path / "damaged")
    attempt_id, capture_id = _commit_complete(damaged, _body(), "27" * 32)
    body_path = damaged.capture_path(capture_id) / "response.body"
    flipped = bytearray(body_path.read_bytes())
    flipped[0] ^= 0x01
    body_path.write_bytes(bytes(flipped))
    with connect(postgres_dsn) as connection:
        summary = derive_target_metrics(damaged, connection)
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
    attempt_a = _attempt("31" * 32, keyword=KEYWORD)
    attempt_b = _attempt("32" * 32, keyword=OTHER_KEYWORD)
    request_a = target_metrics_request_body_bytes(_parameters(keyword=KEYWORD))
    request_b = target_metrics_request_body_bytes(_parameters(keyword=OTHER_KEYWORD))
    id_a = store.commit_attempt(attempt_a, request_body=request_a)
    id_b = store.commit_attempt(attempt_b, request_body=request_b)
    store.commit_capture(_complete_capture(attempt_a, _body()), response_body=_body())
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_target_metrics(store, connection)
        keywords = connection.execute(
            "SELECT DISTINCT requested_keyword FROM target_metrics_totals"
        ).fetchall()
        context = connection.execute(
            "SELECT requested_keyword, attempt_id FROM target_metrics_result_context"
        ).fetchone()
        attempts = connection.execute(
            """
            SELECT attempt_id FROM outcomes
            WHERE capture_id IS NULL ORDER BY attempt_id
            """
        ).fetchall()
    assert summary.observations == 11
    assert keywords == [(KEYWORD,)]
    assert context == (KEYWORD, id_a)
    assert (id_a,) in attempts
    assert (id_b,) in attempts


def test_validator_non_mapping_and_adapter_mismatch_are_integrity_failures(
    tmp_path: Path, postgres_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    apply_migrations(postgres_dsn)
    store = create_store(tmp_path / "integrity")
    attempt_id, capture_id = _commit_complete(store, _body(), "33" * 32)
    original = store.read_attempt

    def mutated_limit(attempt_key: str) -> dict[str, object] | None:
        document = original(attempt_key)
        assert document is not None
        copied = dict(document)
        raw_params = copied["parameters"]
        assert isinstance(raw_params, dict)
        params = dict(raw_params)
        params["internal_list_limit"] = 9
        copied["parameters"] = params
        return copied

    monkeypatch.setattr(store, "read_attempt", mutated_limit)
    with connect(postgres_dsn) as connection:
        summary = derive_target_metrics(store, connection)
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
        summary = derive_target_metrics(store, connection)
        capture_rows = connection.execute(
            "SELECT count(*) FROM outcomes WHERE capture_id = %s",
            (capture_id,),
        ).fetchone()
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
        summary = derive_target_metrics(store, connection)
        capture_rows = connection.execute(
            "SELECT count(*) FROM outcomes WHERE capture_id = %s",
            (capture_id,),
        ).fetchone()
    assert type(store) is EvidenceStore
    assert summary.integrity_failures >= 1
    assert capture_rows == (0,)
    assert attempt_id


def test_exact_content_extra_rows_missing_restore_and_foreign_attempt(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_complete(store, _body(), "34" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        first = derive_target_metrics(store, connection)
        second = derive_target_metrics(store, connection)
        assert first == second
        original = connection.execute(
            "SELECT mentions FROM target_metrics_totals"
        ).fetchone()
        assert original is not None
        connection.execute("UPDATE target_metrics_totals SET mentions = 1")
        connection.commit()
        with pytest.raises(DerivationError, match="conflicting"):
            derive_target_metrics(store, connection)
        connection.rollback()
        connection.execute(
            "UPDATE target_metrics_totals SET mentions = %s",
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
            WHERE observation_kind = %s
            LIMIT 1
            """,
            (extra_identity, TOTAL_KIND),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch"):
            derive_target_metrics(store, connection)
        connection.rollback()
        connection.execute(
            "DELETE FROM observation_envelopes WHERE within_capture_identity = %s",
            (extra_identity,),
        )
        connection.commit()
        connection.execute(
            """
            DELETE FROM target_metrics_source_domains
            WHERE domain = 'thriveagency.com'
            """
        )
        connection.commit()
        restored = derive_target_metrics(store, connection)
        source_count = connection.execute(
            "SELECT count(*) FROM target_metrics_source_domains"
        ).fetchone()
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, 'observation_admitted', 11)
            """,
            ("cd" * 32, capture_id, TARGET_METRICS_RECIPE_ID),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch"):
            derive_target_metrics(store, connection)
        connection.rollback()
        after = connection.execute(
            """
            SELECT attempt_id FROM outcomes WHERE capture_id = %s ORDER BY attempt_id
            """,
            (capture_id,),
        ).fetchall()
    assert restored.observations == 11
    assert source_count == (10,)
    assert (attempt_id,) in after
    assert ("cd" * 32,) in after


def test_wrong_outcome_count_and_extra_diagnostic_fail_closed(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "wrong-count")
    attempt_id, capture_id = _commit_complete(store, _body(), "35" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_target_metrics(store, connection)
        connection.commit()
        before_totals = connection.execute(
            "SELECT count(*) FROM target_metrics_totals"
        ).fetchone()
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = 0
            WHERE capture_id = %s
              AND attempt_id = %s
              AND derivation_version_id = %s
            """,
            (capture_id, attempt_id, TARGET_METRICS_RECIPE_ID),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="conflicting provider outcome"):
            derive_target_metrics(store, connection)
        connection.rollback()
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = 11
            WHERE capture_id = %s
              AND attempt_id = %s
              AND derivation_version_id = %s
            """,
            (capture_id, attempt_id, TARGET_METRICS_RECIPE_ID),
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
            (TARGET_METRICS_RECIPE_ID, attempt_id, capture_id),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch: diagnostics"):
            derive_target_metrics(store, connection)
        connection.rollback()
        leftover = connection.execute(
            """
            SELECT diagnostic_code FROM derivation_diagnostics
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, TARGET_METRICS_RECIPE_ID),
        ).fetchall()
        restored_count = connection.execute(
            """
            SELECT observation_count FROM outcomes
            WHERE capture_id = %s AND attempt_id = %s AND derivation_version_id = %s
            """,
            (capture_id, attempt_id, TARGET_METRICS_RECIPE_ID),
        ).fetchone()
    assert leftover == [("planted_extra",)]
    assert restored_count == (11,)
    assert before_totals == (1,)


def test_second_recipe_coexists_for_the_same_capture(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "coexist")
    attempt_id, capture_id = _commit_complete(store, _body(), "36" * 32)
    apply_migrations(postgres_dsn)
    second = _second_recipe()
    with connect(postgres_dsn) as connection:
        derive_target_metrics(store, connection)
        registered = register_provider_recipe(connection, second)
        assert registered.derivation_version_id != TARGET_METRICS_RECIPE_ID
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
                2840, 9, 9, 0, 1, 'en', 9, 9, 0, 1, 'google', 9, 9, 0, 1,
                0, 0, 'stated', 0, 'stated', 0, 'stated'
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
                adapter_contract=TARGET_METRICS_ADAPTER_CONTRACT,
                observation_kind=TOTAL_KIND,
                within_capture_identity=extra_identity,
            ),
        )
        connection.commit()
        rerun = derive_target_metrics(store, connection)
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
            SELECT derivation_version_id, location_mentions
            FROM target_metrics_result_context
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
            (TARGET_METRICS_RECIPE_ID,),
        ).fetchone()
    assert rerun.observations == 11
    assert (TARGET_METRICS_RECIPE_ID, 11) in outcomes
    assert (registered.derivation_version_id, 1) in outcomes
    assert second_envelopes == (1,)
    assert first_envelopes == (11,)
    mentions = {row[0]: row[1] for row in contexts}
    assert mentions[registered.derivation_version_id] == 9
    assert mentions[TARGET_METRICS_RECIPE_ID] == TOTAL_MENTIONS


def test_populated_current_schema_then_target_metrics_derive(
    tmp_path: Path, postgres_dsn: str
) -> None:
    joined_pre = "\n".join(PRE_AI11_SCHEMA_STATEMENTS)
    assert "search_mentions_result_context" in joined_pre
    assert "google_organic_result_context" in joined_pre
    assert "keyword_overview_coverage" in joined_pre
    assert "target_metrics_" not in joined_pre
    assert "llm_mentions_historical_" not in "\n".join(PRE_AI16_SCHEMA_STATEMENTS)
    tm_statements = [
        statement
        for statement in PRE_AI16_SCHEMA_STATEMENTS
        if statement not in PRE_AI11_SCHEMA_STATEMENTS
    ]
    assert len(tm_statements) == 3
    assert any("target_metrics_totals" in item for item in tm_statements)
    assert any("target_metrics_result_context" in item for item in tm_statements)
    historical_statements = [
        statement
        for statement in PRE_RK04_SCHEMA_STATEMENTS
        if statement not in PRE_AI16_SCHEMA_STATEMENTS
    ]
    assert len(historical_statements) == 3
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
        for statement in PRE_AI11_SCHEMA_STATEMENTS:
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
        for table in AI11_TABLES:
            connection.execute(f"SELECT 1 FROM {table} LIMIT 0")
    assert before_coverage == after_coverage == [("seo api",)]
    assert before_features == after_features == [("organic",)]
    assert before_observations == after_observations == [("fixture-result-1",)]
    assert before_mentions == after_mentions == [(KEYWORD,)]

    metrics = create_store(tmp_path / "metrics")
    _commit_complete(metrics, _body(), "42" * 32)
    with connect(postgres_dsn) as connection:
        summary = derive_target_metrics(metrics, connection)
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
    assert summary.observations == 11
    assert ko_final == (1,)
    assert organic_final == (1,)
    assert fixture_final == (1,)
    assert mentions_final == (KEYWORD,)


def test_fresh_and_upgraded_target_metrics_catalog_match(
    postgres_dsn: str, postgres_second_dsn: str
) -> None:
    with connect(postgres_dsn) as connection:
        for statement in PRE_AI11_SCHEMA_STATEMENTS:
            connection.execute(statement)
        connection.commit()
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)
    with connect(postgres_dsn) as upgraded, connect(postgres_second_dsn) as fresh:
        assert _tm_catalog(upgraded) == _tm_catalog(fresh)
        assert _tm_catalog(upgraded)[0]
        assert _tm_catalog(upgraded)[1]


def test_same_named_decoy_does_not_suppress_target_constraints(postgres_dsn: str) -> None:
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS decoy_target_metrics_totals (
                dummy TEXT,
                CONSTRAINT target_metrics_totals_kind CHECK (dummy IS NOT NULL)
            )
            """
        )
        connection.commit()
        apply_schema(connection)
        row = connection.execute(
            """
            SELECT pg_get_constraintdef(con.oid)
            FROM pg_constraint AS con
            JOIN pg_class AS c ON c.oid = con.conrelid
            JOIN pg_namespace AS n ON n.oid = c.relnamespace
            WHERE n.nspname = current_schema()
              AND c.relname = 'target_metrics_totals'
              AND con.conname = 'target_metrics_totals_kind'
            """
        ).fetchone()
    assert row is not None
    assert "dataforseo.google.ai_optimization.target_metrics.total.v1" in row[0]


def test_two_databases_are_logically_equivalent(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "43" * 32)
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)

    def snapshot(dsn: str) -> tuple[object, ...]:
        with connect(dsn) as connection:
            derive_target_metrics(store, connection)
            parts: list[object] = []
            catalog: list[tuple[str, tuple[str, ...]]] = []
            for table in AI11_TABLES:
                columns, rows = _fetch_relation(connection, table)
                catalog.append((table, columns))
                parts.append(rows)
            assert tuple(name for name, _columns in catalog) == AI11_TABLES
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


def test_fixture_derive_skips_target_metrics_and_target_metrics_skips_fixture(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "44" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        fixture_summary = derive(store, connection, derivation_version_id=DEFAULT_VERSION)
        before = connection.execute("SELECT count(*) FROM target_metrics_totals").fetchone()
        derive_target_metrics(store, connection)
        after = connection.execute("SELECT count(*) FROM target_metrics_totals").fetchone()
    assert fixture_summary.observations == 0
    assert before == (0,)
    assert after == (1,)
