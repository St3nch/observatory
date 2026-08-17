"""PF-06: Keyword Overview CORE provider Derivation into real PostgreSQL."""

from __future__ import annotations

import copy
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from psycopg.errors import CheckViolation, ForeignKeyViolation

from observatory.capture_event import (
    PAID_ADAPTER_CONTRACT,
    body_ref,
    paid_http_attempt_document,
    paid_http_capture_document,
)
from observatory.dataforseo_keyword_overview import (
    CORE_RECIPE,
    CORE_RECIPE_ID,
    COVERAGE_KIND,
    METRICS_KIND,
    FieldState,
)
from observatory.dataforseo_paid_probe import closed_paid_parameters, paid_request_body_bytes
from observatory.derive import DEFAULT_VERSION, DerivationError, derive
from observatory.evidence_store import create_store
from observatory.keyword_overview_derive import derive_keyword_overview
from observatory.migrate import (
    KEYWORD_OVERVIEW_COVERAGE_KIND,
    KEYWORD_OVERVIEW_METRICS_KIND,
    apply_migrations,
    connect,
)
from observatory.provider_recipe import (
    IDENTITY_SCHEMA,
    IDENTITY_VERSION,
    observation_identity,
    register_provider_recipe,
)

FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_keyword_overview_pf03.json"
)
KEYWORDS = (
    "seo api",
    "keyword research",
    "local seo",
    "generative engine optimization",
    "ai search optimization",
)
ACCEPTED_RECIPE_ID = "319af798f3e0b3e5fe4579539442c4ca5d384b683e1f4bce0f7a1b3e26cd5908"


def _body() -> bytes:
    return FIXTURE.read_bytes()


def _parameters() -> dict[str, object]:
    return closed_paid_parameters(keywords=list(KEYWORDS))


def _attempt(nonce: str) -> dict[str, object]:
    return paid_http_attempt_document(
        parameters=_parameters(),
        attempt_nonce=nonce,
        authorized_at="2026-08-16T21:37:00.000000Z",
        observatory_version="pf06-test-v1",
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


def _decoded(body: bytes | None = None) -> dict[str, Any]:
    decoder = json.JSONDecoder(parse_int=int, parse_float=Decimal)
    value, _end = decoder.raw_decode((body or _body()).decode("utf-8"))
    assert isinstance(value, dict)
    return value


def _identity(kind: str, keyword: str) -> str:
    return observation_identity(
        {
            "axes": {"requested_keyword": keyword},
            "observation_kind": kind,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        CORE_RECIPE,
    )


def test_accepted_core_recipe_id_is_unchanged() -> None:
    assert CORE_RECIPE_ID == ACCEPTED_RECIPE_ID
    kinds = CORE_RECIPE["observation_kinds"]
    assert isinstance(kinds, list)
    assert kinds == [COVERAGE_KIND, METRICS_KIND]
    assert KEYWORD_OVERVIEW_COVERAGE_KIND == COVERAGE_KIND
    assert KEYWORD_OVERVIEW_METRICS_KIND == METRICS_KIND


def test_provider_derive_pf03_fixture_into_real_postgres(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_complete(store, _body(), "11" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_keyword_overview(store, connection)
        attempt = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE attempt_id = %s AND capture_id IS NULL
            """,
            (attempt_id,),
        ).fetchone()
        capture = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE capture_id = %s
            """,
            (capture_id,),
        ).fetchone()
        coverage = connection.execute(
            """
            SELECT requested_keyword, covered, returned_keyword, returned_keyword_state
            FROM keyword_overview_coverage
            ORDER BY requested_keyword
            """
        ).fetchall()
        metrics = connection.execute(
            """
            SELECT requested_keyword, search_volume, cpc, high_top_of_page_bid,
                   provider_update_time, competition_level, location_code,
                   language_code, search_partners, categories
            FROM keyword_overview_metrics
            ORDER BY requested_keyword
            """
        ).fetchall()
        kinds = connection.execute(
            "SELECT observation_kind, count(*) FROM observation_envelopes GROUP BY 1"
        ).fetchall()
        fixture_obs = connection.execute("SELECT count(*) FROM observations").fetchone()
    assert CORE_RECIPE_ID == ACCEPTED_RECIPE_ID
    assert summary.derivation_version_id == ACCEPTED_RECIPE_ID
    assert attempt == ("authorized_unresolved", 0)
    assert capture == ("observation_admitted", 10)
    assert summary.observations == 10
    assert coverage == [
        ("ai search optimization", True, "ai search optimization", "stated"),
        ("generative engine optimization", True, "generative engine optimization", "stated"),
        ("keyword research", True, "keyword research", "stated"),
        ("local seo", True, "local seo", "stated"),
        ("seo api", True, "seo api", "stated"),
    ]
    by_keyword = {row[0]: row for row in metrics}
    assert by_keyword["seo api"][1] == 480
    assert by_keyword["seo api"][2] == Decimal("52.05")
    assert by_keyword["seo api"][3] == Decimal(39)
    assert by_keyword["ai search optimization"][4] == "2026-07-16 07:54:24 +00:00"
    assert by_keyword["local seo"][5] == "LOW"
    assert by_keyword["seo api"][6] == 2840
    assert by_keyword["seo api"][7] == "en"
    assert by_keyword["seo api"][8] is False
    assert list(by_keyword["seo api"][9]) == [10004, 10276, 11088, 12376, 13152]
    assert dict(kinds) == {COVERAGE_KIND: 5, METRICS_KIND: 5}
    assert fixture_obs == (0,)


def test_item_reorder_does_not_change_identities_or_values(
    tmp_path: Path, postgres_dsn: str
) -> None:
    original = _body()
    document = _decoded(original)
    items = document["tasks"][0]["result"][0]["items"]
    document["tasks"][0]["result"][0]["items"] = list(reversed(items))
    reordered = _encode(document)
    first = create_store(tmp_path / "a")
    second = create_store(tmp_path / "b")
    _commit_complete(first, original, "22" * 32)
    _commit_complete(second, reordered, "33" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview(first, connection)
        first_ids = connection.execute(
            """
            SELECT observation_kind, requested_keyword, within_capture_identity
            FROM observation_envelopes
            JOIN keyword_overview_coverage USING (
                capture_id, derivation_version_id,
                within_capture_identity, observation_kind
            )
            """
        ).fetchall()
        first_metrics = connection.execute(
            """
            SELECT requested_keyword, search_volume, cpc
            FROM keyword_overview_metrics
            ORDER BY requested_keyword
            """
        ).fetchall()
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute("DELETE FROM keyword_overview_metrics")
        connection.execute("DELETE FROM keyword_overview_coverage")
        connection.execute("DELETE FROM observation_envelopes")
        connection.execute("DELETE FROM derivation_diagnostics")
        connection.execute("DELETE FROM outcomes")
        connection.commit()
    second_dsn = postgres_dsn
    # Use a second database for a clean rebuild of the reordered store.
    # The same DSN was emptied above only if we stay on one DB; create a fresh
    # comparison by deriving the reordered store into a new connection after
    # schema still exists.
    with connect(second_dsn) as connection:
        derive_keyword_overview(second, connection)
        second_ids = {
            (row[0], row[1], row[2])
            for row in connection.execute(
                """
                SELECT observation_kind, requested_keyword, within_capture_identity
                FROM observation_envelopes
                JOIN keyword_overview_coverage USING (
                    capture_id, derivation_version_id,
                    within_capture_identity, observation_kind
                )
                """
            ).fetchall()
        }
        second_metrics = connection.execute(
            """
            SELECT requested_keyword, search_volume, cpc
            FROM keyword_overview_metrics
            ORDER BY requested_keyword
            """
        ).fetchall()
    expected = {
        (COVERAGE_KIND, keyword, _identity(COVERAGE_KIND, keyword)) for keyword in KEYWORDS
    }
    assert {(row[0], row[1], row[2]) for row in first_ids} == expected
    assert second_ids == expected
    assert first_metrics == second_metrics
    assert _identity(COVERAGE_KIND, "seo api") != _identity(METRICS_KIND, "seo api")


def test_omitted_keyword_is_coverage_without_metrics(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    document["tasks"][0]["result"][0]["items"] = [
        item
        for item in document["tasks"][0]["result"][0]["items"]
        if item["keyword"] != "local seo"
    ]
    document["tasks"][0]["result"][0]["items_count"] = 4
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _encode(document), "44" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_keyword_overview(store, connection)
        omitted = connection.execute(
            """
            SELECT covered, returned_keyword, returned_keyword_state
            FROM keyword_overview_coverage
            WHERE requested_keyword = 'local seo'
            """
        ).fetchone()
        metrics = connection.execute(
            "SELECT count(*) FROM keyword_overview_metrics"
        ).fetchone()
        capture = connection.execute(
            "SELECT classification, observation_count FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchone()
    assert omitted == (False, None, FieldState.ABSENT.value)
    assert metrics == (4,)
    assert capture == ("observation_admitted", 9)
    assert summary.observations == 9


def test_all_omitted_emits_coverage_not_empty_outcome(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    document["tasks"][0]["result"][0]["items"] = []
    document["tasks"][0]["result"][0]["items_count"] = 0
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _encode(document), "16" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_keyword_overview(store, connection)
        capture = connection.execute(
            "SELECT classification, observation_count FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchone()
        coverage = connection.execute("SELECT count(*) FROM keyword_overview_coverage").fetchone()
        metrics = connection.execute("SELECT count(*) FROM keyword_overview_metrics").fetchone()
    assert capture == ("observation_admitted", 5)
    assert coverage == (5,)
    assert metrics == (0,)
    assert summary.observations == 5


def test_unstated_provider_update_time_does_not_inherit_capture_time(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    document["tasks"][0]["result"][0]["items"][0]["keyword_info"]["last_updated_time"] = None
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _encode(document), "17" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview(store, connection)
        row = connection.execute(
            """
            SELECT provider_update_time, provider_update_time_state
            FROM keyword_overview_metrics
            WHERE requested_keyword = 'ai search optimization'
            """
        ).fetchone()
    assert row == (None, FieldState.JSON_NULL.value)


def test_provider_error_envelope_and_reconciliation_write_zero_observations(
    tmp_path: Path, postgres_dsn: str
) -> None:
    apply_migrations(postgres_dsn)
    error_doc = _decoded()
    error_doc["tasks"][0]["status_code"] = 40102
    rejected = _body().replace(b'"cost":0.0126', b'"cost":NaN', 1)
    collision = _decoded()
    collision["tasks"][0]["result"][0]["items"].append(
        copy.deepcopy(collision["tasks"][0]["result"][0]["items"][0])
    )
    collision["tasks"][0]["result"][0]["items_count"] = 6
    cases = [
        (_encode(error_doc), "aa" * 32, "provider_error"),
        (rejected, "bb" * 32, "provider_envelope_rejected"),
        (_encode(collision), "cc" * 32, "reconciliation_failed"),
    ]
    for body, nonce, expected in cases:
        store = create_store(tmp_path / nonce)
        _commit_complete(store, body, nonce)
        with connect(postgres_dsn) as connection:
            derive_keyword_overview(store, connection)
            row = connection.execute(
                """
                SELECT classification, observation_count
                FROM outcomes
                WHERE capture_id IS NOT NULL
                ORDER BY classification
                """
            ).fetchall()
            envelopes = connection.execute(
                "SELECT count(*) FROM observation_envelopes"
            ).fetchone()
            connection.execute("DELETE FROM keyword_overview_metrics")
            connection.execute("DELETE FROM keyword_overview_coverage")
            connection.execute("DELETE FROM observation_envelopes")
            connection.execute("DELETE FROM derivation_diagnostics")
            connection.execute("DELETE FROM outcomes")
            connection.commit()
        assert (expected, 0) in row
        assert envelopes == (0,)


def test_transport_states_and_damaged_capture(
    tmp_path: Path, postgres_dsn: str
) -> None:
    apply_migrations(postgres_dsn)
    request = paid_request_body_bytes(_parameters())
    none_store = create_store(tmp_path / "none")
    attempt = _attempt("dd" * 32)
    none_store.commit_attempt(attempt, request_body=request)
    none_store.commit_capture(
        paid_http_capture_document(
            attempt=attempt,
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
        derive_keyword_overview(none_store, connection)
        none_row = connection.execute(
            "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchone()
        connection.execute("DELETE FROM outcomes")
        connection.commit()
    assert none_row == ("no_response",)

    partial_store = create_store(tmp_path / "partial")
    partial_attempt = _attempt("ee" * 32)
    chunk = _body()[:32]
    partial_store.commit_attempt(partial_attempt, request_body=request)
    partial_store.commit_capture(
        paid_http_capture_document(
            attempt=partial_attempt,
            request_started_at="2026-08-16T21:37:02.100000Z",
            transport_ended_at="2026-08-16T21:37:02.400000Z",
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
            response_headers_at="2026-08-16T21:37:02.200000Z",
            response_body_ended_at="2026-08-16T21:37:02.300000Z",
        ),
        response_body=chunk,
    )
    with connect(postgres_dsn) as connection:
        derive_keyword_overview(partial_store, connection)
        partial_row = connection.execute(
            "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchone()
        connection.execute("DELETE FROM outcomes")
        connection.commit()
    assert partial_row == ("response_partial",)

    damaged = create_store(tmp_path / "damaged")
    attempt_id, capture_id = _commit_complete(damaged, _body(), "ff" * 32)
    manifest = damaged.capture_path(capture_id) / "capture.json"
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    with connect(postgres_dsn) as connection:
        summary = derive_keyword_overview(damaged, connection)
        attempt_row = connection.execute(
            """
            SELECT classification FROM outcomes
            WHERE attempt_id = %s AND capture_id IS NULL
            """,
            (attempt_id,),
        ).fetchone()
        capture_rows = connection.execute(
            "SELECT count(*) FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchone()
        envelopes = connection.execute("SELECT count(*) FROM observation_envelopes").fetchone()
    assert attempt_row == ("authorized_unresolved",)
    assert capture_rows == (0,)
    assert envelopes == (0,)
    assert summary.integrity_failures >= 1

    empty = create_store(tmp_path / "empty")
    empty_attempt = _attempt("18" * 32)
    empty.commit_attempt(empty_attempt, request_body=request)
    empty.commit_capture(
        paid_http_capture_document(
            attempt=empty_attempt,
            request_started_at="2026-08-16T21:37:03.100000Z",
            transport_ended_at="2026-08-16T21:37:03.400000Z",
            transport_state="response_complete",
            response={
                "status": 200,
                "http_version": "HTTP/1.1",
                "header_policy": "http-headers-v1",
                "headers": [["content-type", "application/json"]],
                "omitted_headers": [],
                "body": {"state": "present_zero_bytes", "body": body_ref(b"")},
                "completeness": "complete",
            },
            transport_failure=None,
            response_headers_at="2026-08-16T21:37:03.200000Z",
            response_body_ended_at="2026-08-16T21:37:03.300000Z",
        ),
        response_body=b"",
    )
    with connect(postgres_dsn) as connection:
        connection.execute("DELETE FROM outcomes")
        connection.commit()
        derive_keyword_overview(empty, connection)
        empty_row = connection.execute(
            "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchone()
        connection.execute("DELETE FROM outcomes")
        connection.commit()
    assert empty_row == ("transport_complete_non_admissible",)

    body_damaged = create_store(tmp_path / "body-damaged")
    body_attempt, body_capture = _commit_complete(body_damaged, _body(), "19" * 32)
    body_path = body_damaged.capture_path(body_capture) / "response.body"
    damaged_bytes = bytearray(body_path.read_bytes())
    damaged_bytes[0] ^= 0x01
    body_path.write_bytes(bytes(damaged_bytes))
    with connect(postgres_dsn) as connection:
        body_summary = derive_keyword_overview(body_damaged, connection)
        body_attempt_row = connection.execute(
            """
            SELECT classification FROM outcomes
            WHERE attempt_id = %s AND capture_id IS NULL
            """,
            (body_attempt,),
        ).fetchone()
        body_capture_rows = connection.execute(
            "SELECT count(*) FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchone()
    assert body_attempt_row == ("authorized_unresolved",)
    assert body_capture_rows == (0,)
    assert body_summary.integrity_failures >= 1


def test_exact_content_idempotent_and_conflict_refusal(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "12" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        first = derive_keyword_overview(store, connection)
        second = derive_keyword_overview(store, connection)
        assert first == second
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE outcomes
            SET classification = 'provider_error'
            WHERE capture_id IS NOT NULL
            """
        )
        connection.commit()
        with pytest.raises(DerivationError, match="outcome"):
            derive_keyword_overview(store, connection)
        connection.execute(
            """
            UPDATE outcomes
            SET classification = 'observation_admitted'
            WHERE capture_id IS NOT NULL
            """
        )
        connection.commit()
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE observation_envelopes
            SET provider = 'other-provider'
            WHERE observation_kind = %s
            """,
            (COVERAGE_KIND,),
        )
        connection.commit()
        with pytest.raises(Exception, match="adapter metadata|conflicting"):
            derive_keyword_overview(store, connection)
        connection.execute(
            """
            UPDATE observation_envelopes
            SET provider = 'dataforseo'
            WHERE observation_kind = %s
            """,
            (COVERAGE_KIND,),
        )
        connection.commit()
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE keyword_overview_coverage
            SET covered = FALSE, returned_keyword = NULL,
                returned_keyword_state = 'absent'
            WHERE requested_keyword = 'seo api'
            """
        )
        connection.commit()
        with pytest.raises(DerivationError, match="coverage"):
            derive_keyword_overview(store, connection)
        connection.execute(
            """
            UPDATE keyword_overview_coverage
            SET covered = TRUE, returned_keyword = 'seo api',
                returned_keyword_state = 'stated'
            WHERE requested_keyword = 'seo api'
            """
        )
        connection.commit()
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE keyword_overview_metrics
            SET search_volume = 1
            WHERE requested_keyword = 'seo api'
            """
        )
        connection.commit()
        with pytest.raises(DerivationError, match="metrics"):
            derive_keyword_overview(store, connection)


def test_high_precision_decimal_round_trip(
    tmp_path: Path, postgres_dsn: str
) -> None:
    precise = _body().replace(b'"cpc":60.62', b'"cpc":1.234567890123456789', 1)
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, precise, "13" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview(store, connection)
        value = connection.execute(
            """
            SELECT cpc FROM keyword_overview_metrics
            WHERE requested_keyword = 'ai search optimization'
            """
        ).fetchone()
    assert value is not None
    assert value[0] == Decimal("1.234567890123456789")
    assert value[0] != Decimal(str(float("1.234567890123456789")))


def test_two_databases_are_logically_equivalent(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "14" * 32)
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)

    def snapshot(dsn: str) -> tuple[object, ...]:
        with connect(dsn) as connection:
            derive_keyword_overview(store, connection)
            outcomes = connection.execute(
                """
                SELECT attempt_id, capture_id, derivation_version_id,
                       classification, observation_count
                FROM outcomes
                ORDER BY attempt_id, capture_id NULLS FIRST
                """
            ).fetchall()
            envelopes = connection.execute(
                """
                SELECT capture_id, derivation_version_id, within_capture_identity,
                       provider, adapter_contract, observation_kind
                FROM observation_envelopes
                ORDER BY observation_kind, within_capture_identity
                """
            ).fetchall()
            coverage = connection.execute(
                """
                SELECT requested_keyword, covered, returned_keyword, returned_keyword_state
                FROM keyword_overview_coverage
                ORDER BY requested_keyword
                """
            ).fetchall()
            metrics = connection.execute(
                """
                SELECT requested_keyword, search_volume, competition, cpc,
                       high_top_of_page_bid, provider_update_time
                FROM keyword_overview_metrics
                ORDER BY requested_keyword
                """
            ).fetchall()
        return outcomes, envelopes, coverage, metrics

    assert snapshot(postgres_dsn) == snapshot(postgres_second_dsn)


def test_fixture_derive_still_skips_provider_rows(
    tmp_path: Path, postgres_dsn: str
) -> None:
    from observatory.capture import PUBLISHED_AR_INPUTS, capture_admitted_results

    store = create_store(tmp_path / "mixed")
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    _commit_complete(store, _body(), "15" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
        provider_envelopes = connection.execute(
            "SELECT count(*) FROM observation_envelopes"
        ).fetchone()
        recipes = connection.execute("SELECT count(*) FROM provider_recipes").fetchone()
        coverage = connection.execute(
            "SELECT count(*) FROM keyword_overview_coverage"
        ).fetchone()
        fixture_obs = connection.execute("SELECT count(*) FROM observations").fetchone()
    assert provider_envelopes == (0,)
    assert recipes == (0,)
    assert coverage == (0,)
    assert fixture_obs == (2,)
    from fastapi.testclient import TestClient

    from observatory.api import create_app
    from observatory.capture import PUBLISHED_AR_ATTEMPT_ID
    from observatory.settings import Settings

    client = TestClient(
        create_app(
            Settings(
                environment="test",
                database_url=postgres_dsn,
                evidence_root=store.root,
                derivation_version_id=DEFAULT_VERSION,
            ),
            store=store,
        )
    )
    response = client.get(f"/v1/attempts/{PUBLISHED_AR_ATTEMPT_ID}")
    assert response.status_code == 200
    body = response.json()
    assert body["derivation_version_id"] == DEFAULT_VERSION
    assert len(body["observations"]) == 2


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
    assert len(body) == 26270
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_keyword_overview(store, connection)
        capture_row = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE capture_id = %s
            """,
            ("b4fc36a7799b497d0d183a88449bf0a770ce741ec1f0d8eaade2d75c930154d5",),
        ).fetchone()
        coverage = connection.execute(
            "SELECT count(*) FROM keyword_overview_coverage"
        ).fetchone()
        metrics = connection.execute(
            "SELECT count(*) FROM keyword_overview_metrics"
        ).fetchone()
    assert summary.integrity_failures == 0
    assert capture_row == ("observation_admitted", 10)
    assert coverage == (5,)
    assert metrics == (5,)


def test_provider_rows_cannot_use_fixture_label(
    tmp_path: Path, postgres_dsn: str
) -> None:
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, CORE_RECIPE)
        with pytest.raises((CheckViolation, ForeignKeyViolation)):
            connection.execute(
                """
                INSERT INTO observation_envelopes (
                    capture_id, attempt_id, derivation_version_id, provider,
                    adapter_contract, observation_kind, within_capture_identity
                )
                VALUES (%s, %s, %s, 'dataforseo', %s, %s, %s)
                """,
                (
                    "a" * 64,
                    "b" * 64,
                    DEFAULT_VERSION,
                    PAID_ADAPTER_CONTRACT,
                    COVERAGE_KIND,
                    "c" * 64,
                ),
            )


_METRICS_STATE_COLUMNS: tuple[str, ...] = (
    "location_code",
    "language_code",
    "search_partners",
    "search_volume",
    "competition",
    "competition_level",
    "cpc",
    "low_top_of_page_bid",
    "high_top_of_page_bid",
    "categories",
    "provider_update_time",
)
_NON_NULL_SAMPLES: dict[str, object] = {
    "location_code": 2840,
    "language_code": "en",
    "search_partners": False,
    "search_volume": 0,
    "competition": Decimal("0"),
    "competition_level": "LOW",
    "cpc": Decimal("0"),
    "low_top_of_page_bid": Decimal("0"),
    "high_top_of_page_bid": Decimal("0"),
    "categories": [],
    "provider_update_time": "2026-07-16 07:54:24 +00:00",
}


def _derive_pf03(tmp_path: Path, postgres_dsn: str) -> Any:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "21" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_keyword_overview(store, connection)
    assert summary.observations == 10
    return store


def _envelope(connection: Any, kind: str) -> tuple[str, str, str, str]:
    row = connection.execute(
        """
        SELECT capture_id, derivation_version_id,
               within_capture_identity, observation_kind
        FROM observation_envelopes
        WHERE observation_kind = %s
        LIMIT 1
        """,
        (kind,),
    ).fetchone()
    assert row is not None
    return (str(row[0]), str(row[1]), str(row[2]), str(row[3]))


def _insert_metrics(connection: Any, envelope: tuple[str, str, str, str]) -> None:
    connection.execute(
        """
        INSERT INTO keyword_overview_metrics (
            capture_id, derivation_version_id, within_capture_identity,
            observation_kind, requested_keyword, returned_keyword,
            location_code, location_code_state,
            language_code, language_code_state,
            search_partners, search_partners_state,
            search_volume, search_volume_state,
            competition, competition_state,
            competition_level, competition_level_state,
            cpc, cpc_state,
            low_top_of_page_bid, low_top_of_page_bid_state,
            high_top_of_page_bid, high_top_of_page_bid_state,
            categories, categories_state,
            provider_update_time, provider_update_time_state
        )
        VALUES (
            %s, %s, %s, %s, 'seo api', 'seo api',
            2840, 'stated', 'en', 'stated', FALSE, 'stated',
            0, 'stated', 0, 'stated', 'LOW', 'stated',
            0, 'stated', 0, 'stated', 0, 'stated',
            '{}', 'stated', '2026-07-16 07:54:24 +00:00', 'stated'
        )
        """,
        envelope,
    )


def _insert_coverage(connection: Any, envelope: tuple[str, str, str, str]) -> None:
    connection.execute(
        """
        INSERT INTO keyword_overview_coverage (
            capture_id, derivation_version_id, within_capture_identity,
            observation_kind, requested_keyword, covered,
            returned_keyword, returned_keyword_state
        )
        VALUES (%s, %s, %s, %s, 'seo api', TRUE, 'seo api', 'stated')
        """,
        envelope,
    )


def test_detail_rows_are_structurally_bound_to_observation_kind(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = _derive_pf03(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        coverage_env = _envelope(connection, COVERAGE_KIND)
        metrics_env = _envelope(connection, METRICS_KIND)
        assert coverage_env[3] == COVERAGE_KIND
        assert metrics_env[3] == METRICS_KIND
        with pytest.raises((CheckViolation, ForeignKeyViolation)), connection.transaction():
            _insert_metrics(connection, coverage_env)
        with pytest.raises((CheckViolation, ForeignKeyViolation)), connection.transaction():
            _insert_coverage(connection, metrics_env)
        with pytest.raises((CheckViolation, ForeignKeyViolation)), connection.transaction():
            _insert_metrics(
                connection,
                (coverage_env[0], coverage_env[1], coverage_env[2], METRICS_KIND),
            )
        with pytest.raises((CheckViolation, ForeignKeyViolation)), connection.transaction():
            _insert_coverage(
                connection,
                (metrics_env[0], metrics_env[1], metrics_env[2], COVERAGE_KIND),
            )
        kinds = dict(
            connection.execute(
                "SELECT observation_kind, count(*) FROM observation_envelopes GROUP BY 1"
            ).fetchall()
        )
        coverage = connection.execute("SELECT count(*) FROM keyword_overview_coverage").fetchone()
        metrics = connection.execute("SELECT count(*) FROM keyword_overview_metrics").fetchone()
        capture = connection.execute(
            "SELECT classification, observation_count FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchone()
    assert kinds == {COVERAGE_KIND: 5, METRICS_KIND: 5}
    assert coverage == (5,)
    assert metrics == (5,)
    assert capture == ("observation_admitted", 10)
    with connect(postgres_dsn) as connection:
        again = derive_keyword_overview(store, connection)
    assert again.observations == 10


def test_metrics_field_state_value_consistency_is_enforced(
    tmp_path: Path, postgres_dsn: str
) -> None:
    _derive_pf03(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        for column in _METRICS_STATE_COLUMNS:
            with pytest.raises(CheckViolation), connection.transaction():
                connection.execute(
                    f"""
                    UPDATE keyword_overview_metrics
                    SET {column} = NULL, {column}_state = 'stated'
                    """
                )
            with pytest.raises(CheckViolation), connection.transaction():
                connection.execute(
                    f"""
                    UPDATE keyword_overview_metrics
                    SET {column} = %s, {column}_state = 'absent'
                    """,
                    (_NON_NULL_SAMPLES[column],),
                )
        connection.execute(
            """
            UPDATE keyword_overview_metrics
            SET search_volume = 0, search_volume_state = 'stated',
                search_partners = FALSE, search_partners_state = 'stated',
                categories = '{}', categories_state = 'stated',
                provider_update_time = NULL,
                provider_update_time_state = 'json_null',
                competition_level = NULL,
                competition_level_state = 'absent',
                cpc = NULL, cpc_state = 'not_requested',
                competition = NULL, competition_state = 'inapplicable'
            WHERE requested_keyword = 'seo api'
            """
        )
        row = connection.execute(
            """
            SELECT search_volume, search_volume_state,
                   search_partners, search_partners_state,
                   categories, categories_state,
                   provider_update_time, provider_update_time_state,
                   competition_level, competition_level_state,
                   cpc, cpc_state, competition, competition_state
            FROM keyword_overview_metrics
            WHERE requested_keyword = 'seo api'
            """
        ).fetchone()
    assert row is not None
    assert row[0] == 0
    assert row[1] == "stated"
    assert row[2] is False
    assert row[3] == "stated"
    assert list(row[4]) == []
    assert row[5] == "stated"
    assert row[6] is None
    assert row[7] == "json_null"
    assert row[8] is None
    assert row[9] == "absent"
    assert row[10] is None
    assert row[11] == "not_requested"
    assert row[12] is None
    assert row[13] == "inapplicable"


def test_coverage_returned_keyword_cannot_contradict_covered(
    tmp_path: Path, postgres_dsn: str
) -> None:
    _derive_pf03(tmp_path, postgres_dsn)
    rejected = (
        "SET covered = TRUE, returned_keyword = NULL, returned_keyword_state = 'stated'",
        "SET covered = TRUE, returned_keyword = 'seo api', "
        "returned_keyword_state = 'absent'",
        "SET covered = FALSE, returned_keyword = 'seo api', "
        "returned_keyword_state = 'stated'",
        "SET covered = FALSE, returned_keyword = NULL, returned_keyword_state = 'stated'",
        "SET covered = FALSE, returned_keyword = NULL, "
        "returned_keyword_state = 'json_null'",
        "SET covered = FALSE, returned_keyword = NULL, "
        "returned_keyword_state = 'not_requested'",
        "SET covered = FALSE, returned_keyword = NULL, "
        "returned_keyword_state = 'inapplicable'",
    )
    with connect(postgres_dsn) as connection:
        for assignment in rejected:
            with pytest.raises(CheckViolation), connection.transaction():
                connection.execute(
                    f"""
                    UPDATE keyword_overview_coverage
                    {assignment}
                    WHERE requested_keyword = 'seo api'
                    """
                )
        connection.execute(
            """
            UPDATE keyword_overview_coverage
            SET covered = FALSE, returned_keyword = NULL,
                returned_keyword_state = 'absent'
            WHERE requested_keyword = 'local seo'
            """
        )
        omitted = connection.execute(
            """
            SELECT covered, returned_keyword, returned_keyword_state
            FROM keyword_overview_coverage
            WHERE requested_keyword = 'local seo'
            """
        ).fetchone()
        connection.execute(
            """
            UPDATE keyword_overview_coverage
            SET covered = TRUE, returned_keyword = 'seo api',
                returned_keyword_state = 'stated'
            WHERE requested_keyword = 'seo api'
            """
        )
        covered = connection.execute(
            """
            SELECT covered, returned_keyword, returned_keyword_state
            FROM keyword_overview_coverage
            WHERE requested_keyword = 'seo api'
            """
        ).fetchone()
    assert omitted == (False, None, "absent")
    assert covered == (True, "seo api", "stated")
