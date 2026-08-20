"""PF-12: Google Organic provider Derivation into real PostgreSQL."""

from __future__ import annotations

import copy
import hashlib
import json
import socket
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from psycopg.errors import CheckViolation, ForeignKeyViolation, UniqueViolation

from observatory.capture_event import (
    ORGANIC_ADAPTER_CONTRACT,
    body_ref,
    organic_http_attempt_document,
    organic_http_capture_document,
)
from observatory.dataforseo_google_organic import (
    AIO_PRESENCE_KIND,
    AIO_SOURCE_KIND,
    FEATURE_PRESENCE_KIND,
    GOOGLE_ORGANIC_RECIPE_ID,
    ORGANIC_PLACEMENT_KIND,
    RELATED_QUERY_KIND,
    RELATED_QUESTION_KIND,
)
from observatory.dataforseo_google_organic_paid_probe import (
    closed_organic_parameters,
    organic_request_body_bytes,
)
from observatory.dataforseo_keyword_overview import CORE_RECIPE_ID, EXTENDED_RECIPE_ID
from observatory.derive import DEFAULT_VERSION, DerivationError, derive
from observatory.evidence_store import create_store
from observatory.google_organic_derive import (
    derive_google_organic,
    plan_google_organic_capture,
)
from observatory.migrate import apply_migrations, apply_schema, connect
from observatory.provider_recipe import register_provider_recipe

FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_google_organic_pf10.json"
)
KEYWORD = "conspiracy theories"
ACCEPTED_RECIPE_ID = "338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde"
ACCEPTED_KO_CORE = "319af798f3e0b3e5fe4579539442c4ca5d384b683e1f4bce0f7a1b3e26cd5908"
WIKI_URL = "https://en.wikipedia.org/wiki/Conspiracy_theory"
PBS_URL = "https://www.pbs.org/video/why-do-conspiracy-theories-spread-so-quickly-43q4k3/"


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
    return closed_organic_parameters(keyword=KEYWORD)


def _attempt(nonce: str) -> dict[str, object]:
    return organic_http_attempt_document(
        parameters=_parameters(),
        attempt_nonce=nonce,
        authorized_at="2026-08-18T17:37:00.000000Z",
        observatory_version="pf12-test-v1",
    )


def _complete_capture(
    attempt: dict[str, object], body: bytes, *, suffix: str = "1"
) -> dict[str, object]:
    return organic_http_capture_document(
        attempt=attempt,
        request_started_at=f"2026-08-18T17:37:0{suffix}.100000Z",
        transport_ended_at=f"2026-08-18T17:37:0{suffix}.400000Z",
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
        response_headers_at=f"2026-08-18T17:37:0{suffix}.200000Z",
        response_body_ended_at=f"2026-08-18T17:37:0{suffix}.300000Z",
    )


def _commit_complete(store: Any, body: bytes, nonce: str) -> tuple[str, str]:
    attempt = _attempt(nonce)
    request = organic_request_body_bytes(_parameters())
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


def _items(document: dict[str, Any]) -> list[Any]:
    items = document["tasks"][0]["result"][0]["items"]
    assert isinstance(items, list)
    return items


def _set_items(document: dict[str, Any], items: list[Any]) -> None:
    document["tasks"][0]["result"][0]["items"] = items
    document["tasks"][0]["result"][0]["items_count"] = len(items)


def _complete_capture_dict() -> dict[str, object]:
    return {
        "transport_state": "response_complete",
        "response": {"completeness": "complete"},
    }


def test_accepted_recipe_and_ko_identities_remain_unchanged() -> None:
    assert GOOGLE_ORGANIC_RECIPE_ID == ACCEPTED_RECIPE_ID
    assert CORE_RECIPE_ID == ACCEPTED_KO_CORE
    assert EXTENDED_RECIPE_ID != ACCEPTED_RECIPE_ID
    raw = FIXTURE.read_bytes()
    assert len(raw) == 135722
    assert hashlib.sha256(raw).hexdigest() == (
        "7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f"
    )


def test_plan_frozen_fixture_has_exact_semantic_counts() -> None:
    planned = plan_google_organic_capture(
        "a" * 64,
        "b" * 64,
        _complete_capture_dict(),
        _parameters(),
        _body(),
    )
    assert planned.classification == "observation_admitted"
    assert len(planned.envelopes) == 237
    by_kind = {kind: 0 for kind in (
        FEATURE_PRESENCE_KIND,
        ORGANIC_PLACEMENT_KIND,
        AIO_PRESENCE_KIND,
        AIO_SOURCE_KIND,
        RELATED_QUESTION_KIND,
        RELATED_QUERY_KIND,
    )}
    for envelope in planned.envelopes:
        by_kind[envelope.observation_kind] += 1
    assert by_kind == {
        FEATURE_PRESENCE_KIND: 111,
        ORGANIC_PLACEMENT_KIND: 97,
        AIO_PRESENCE_KIND: 1,
        AIO_SOURCE_KIND: 15,
        RELATED_QUESTION_KIND: 4,
        RELATED_QUERY_KIND: 9,
    }
    assert len(planned.aio_occurrences) == 18
    assert sum(1 for row in planned.aio_occurrences if row["element_index"] is None) == 7
    assert sum(1 for row in planned.aio_occurrences if row["element_index"] is not None) == 11
    assert len(planned.paa_occurrences) == 4
    assert planned.context is not None
    assert planned.context["items_count"] == 111
    assert "cost" not in planned.context
    assert "check_url" not in planned.context


def test_plan_zero_item_serp_is_admitted_empty() -> None:
    document = _decoded()
    _set_items(document, [])
    planned = plan_google_organic_capture(
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


def _plant_aio_wiki_disagreement(document: dict[str, Any]) -> None:
    aio = next(item for item in _items(document) if item["type"] == "ai_overview")
    changed = False
    for element in aio["items"]:
        refs = element.get("references")
        if not isinstance(refs, list):
            continue
        for ref in refs:
            if ref.get("url") == WIKI_URL:
                ref["title"] = "planted disagreement"
                changed = True
                break
        if changed:
            break
    assert changed


def test_plan_aio_disagreement_rejects_whole_unit() -> None:
    document = _decoded()
    _plant_aio_wiki_disagreement(document)
    planned = plan_google_organic_capture(
        "a" * 64,
        "b" * 64,
        _complete_capture_dict(),
        _parameters(),
        _encode(document),
    )
    assert planned.classification == "provider_envelope_rejected"
    assert planned.envelopes == ()
    assert planned.aio_occurrences == ()
    assert planned.paa_occurrences == ()
    assert planned.context is None


def test_derive_pf10_fixture_into_real_postgres(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_complete(store, _body(), "11" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_google_organic(store, connection)
        outcome = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE capture_id = %s
            """,
            (capture_id,),
        ).fetchone()
        attempt_row = connection.execute(
            """
            SELECT classification
            FROM outcomes
            WHERE attempt_id = %s AND capture_id IS NULL
            """,
            (attempt_id,),
        ).fetchone()
        features = connection.execute(
            "SELECT count(*) FROM google_organic_serp_features"
        ).fetchone()
        ranked = connection.execute(
            "SELECT count(*), count(DISTINCT url) FROM google_organic_ranked_results"
        ).fetchone()
        aio_sources = connection.execute(
            "SELECT count(*) FROM google_organic_aio_sources"
        ).fetchone()
        aio_occ = connection.execute(
            """
            SELECT count(*),
                   count(*) FILTER (WHERE element_index IS NULL),
                   count(*) FILTER (WHERE element_index IS NOT NULL)
            FROM google_organic_aio_source_occurrences
            """
        ).fetchone()
        questions = connection.execute(
            "SELECT count(*) FROM google_organic_related_questions"
        ).fetchone()
        paa_occ = connection.execute(
            "SELECT count(*) FROM google_organic_related_question_occurrences"
        ).fetchone()
        queries = connection.execute(
            "SELECT count(*) FROM google_organic_related_queries"
        ).fetchone()
        context = connection.execute(
            """
            SELECT items_count, result_datetime, result_datetime_state, item_types
            FROM google_organic_result_context
            """
        ).fetchone()
    assert summary.observations == 237
    assert summary.integrity_failures == 0
    assert attempt_row == ("authorized_unresolved",)
    assert outcome == ("observation_admitted", 237)
    assert features == (111,)
    assert ranked == (97, 87)
    assert aio_sources == (15,)
    assert aio_occ == (18, 7, 11)
    assert questions == (4,)
    assert paa_occ == (4,)
    assert queries == (9,)
    assert context is not None
    assert context[0] == 111
    assert context[1] == "2026-08-18 17:37:36 +00:00"
    assert context[2] == "stated"
    assert context[3][0] == "ai_overview"
    assert context[1] != "2026-08-18T17:37:01.400000Z"


def test_zero_item_serp_writes_admitted_empty_outcome(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    _set_items(document, [])
    store = create_store(tmp_path / "empty")
    _attempt_id, capture_id = _commit_complete(store, _encode(document), "26" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_google_organic(store, connection)
        outcome = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes WHERE capture_id = %s
            """,
            (capture_id,),
        ).fetchone()
        envelopes = connection.execute(
            "SELECT count(*) FROM observation_envelopes"
        ).fetchone()
        context = connection.execute(
            "SELECT items_count FROM google_organic_result_context"
        ).fetchone()
    assert summary.observations == 0
    assert outcome == ("observation_admitted_empty", 0)
    assert envelopes == (0,)
    assert context == (0,)


def test_duplicate_urls_keep_distinct_placement_identities(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "12" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic(store, connection)
        rows = connection.execute(
            """
            SELECT page, rank_group, rank_absolute
            FROM google_organic_ranked_results
            WHERE url = %s
            ORDER BY page, rank_absolute
            """,
            (PBS_URL,),
        ).fetchall()
    assert rows == [(2, 17, 22), (3, 27, 33)]


def test_aio_disagreement_writes_rejected_outcome_and_zero_rows(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    _plant_aio_wiki_disagreement(document)
    store = create_store(tmp_path / "evidence")
    _attempt_id, capture_id = _commit_complete(store, _encode(document), "13" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_google_organic(store, connection)
        outcome = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes WHERE capture_id = %s
            """,
            (capture_id,),
        ).fetchone()
        envelopes = connection.execute(
            "SELECT count(*) FROM observation_envelopes"
        ).fetchone()
        context = connection.execute(
            "SELECT count(*) FROM google_organic_result_context"
        ).fetchone()
        occurrences = connection.execute(
            "SELECT count(*) FROM google_organic_aio_source_occurrences"
        ).fetchone()
    assert summary.observations == 0
    assert outcome == ("provider_envelope_rejected", 0)
    assert envelopes == (0,)
    assert context == (0,)
    assert occurrences == (0,)


def test_top_level_aio_occurrence_uniqueness_is_null_safe(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "14" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic(store, connection)
        row = connection.execute(
            """
            SELECT capture_id, derivation_version_id, within_capture_identity,
                   observation_kind, locus, reference_index
            FROM google_organic_aio_source_occurrences
            WHERE element_index IS NULL
            LIMIT 1
            """
        ).fetchone()
        assert row is not None
        with pytest.raises(UniqueViolation):
            connection.execute(
                """
                INSERT INTO google_organic_aio_source_occurrences (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, locus, element_index, reference_index
                )
                VALUES (%s, %s, %s, %s, %s, NULL, %s)
                """,
                row,
            )


def test_wrong_kind_and_occurrence_shape_are_rejected(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "15" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic(store, connection)
        connection.commit()
        source = connection.execute(
            """
            SELECT capture_id, derivation_version_id, within_capture_identity, locus
            FROM google_organic_aio_sources
            WHERE locus = 'top_level'
            LIMIT 1
            """
        ).fetchone()
        assert source is not None
        with pytest.raises(CheckViolation):
            connection.execute(
                """
                INSERT INTO google_organic_aio_source_occurrences (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, locus, element_index, reference_index
                )
                VALUES (%s, %s, %s, %s, 'top_level', 0, 0)
                """,
                (source[0], source[1], source[2], AIO_SOURCE_KIND),
            )
        connection.rollback()
        with pytest.raises(ForeignKeyViolation):
            connection.execute(
                """
                INSERT INTO google_organic_aio_source_occurrences (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, locus, element_index, reference_index
                )
                VALUES (%s, %s, %s, %s, 'element', 0, 0)
                """,
                (source[0], source[1], source[2], AIO_SOURCE_KIND),
            )
        connection.rollback()
        ranked = connection.execute(
            """
            SELECT capture_id, derivation_version_id, within_capture_identity
            FROM google_organic_ranked_results
            LIMIT 1
            """
        ).fetchone()
        assert ranked is not None
        with pytest.raises((CheckViolation, ForeignKeyViolation)):
            connection.execute(
                """
                INSERT INTO google_organic_aio_sources (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, requested_keyword, locus, url,
                    domain, domain_state, title, title_state, source, source_state
                )
                VALUES (
                    %s, %s, %s, %s, %s, 'top_level', 'https://example.com/',
                    NULL, 'absent', NULL, 'absent', NULL, 'absent'
                )
                """,
                (*ranked, AIO_SOURCE_KIND, KEYWORD),
            )


def test_paa_second_block_keeps_four_questions_and_eight_occurrences(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    items = _items(document)
    paa = next(item for item in items if item["type"] == "people_also_ask")
    second = copy.deepcopy(paa)
    second["rank_group"] = 2
    second["rank_absolute"] = 112
    items.append(second)
    _set_items(document, items)
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _encode(document), "16" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic(store, connection)
        questions = connection.execute(
            "SELECT count(*) FROM google_organic_related_questions"
        ).fetchone()
        occurrences = connection.execute(
            """
            SELECT rank_absolute, count(*)
            FROM google_organic_related_question_occurrences
            GROUP BY rank_absolute
            ORDER BY rank_absolute
            """
        ).fetchall()
    assert questions == (4,)
    assert occurrences == [(3, 4), (112, 4)]


def test_transport_parse_reconciliation_and_damage_paths(
    tmp_path: Path, postgres_dsn: str
) -> None:
    apply_migrations(postgres_dsn)
    no_response = create_store(tmp_path / "no-response")
    attempt = _attempt("21" * 32)
    request = organic_request_body_bytes(_parameters())
    no_response.commit_attempt(attempt, request_body=request)
    no_response.commit_capture(
        organic_http_capture_document(
            attempt=attempt,
            request_started_at="2026-08-18T17:37:01.100000Z",
            transport_ended_at="2026-08-18T17:37:01.400000Z",
            transport_state="no_response",
            response=None,
            transport_failure={"phase": "connect", "code": "timeout"},
            response_headers_at=None,
            response_body_ended_at=None,
        ),
        response_body=None,
    )
    with connect(postgres_dsn) as connection:
        summary = derive_google_organic(no_response, connection)
        row = connection.execute(
            "SELECT classification, observation_count FROM outcomes WHERE capture_id IS NOT NULL"
        ).fetchone()
    assert summary.observations == 0
    assert row == ("no_response", 0)

    empty_body = create_store(tmp_path / "empty-body")
    empty_attempt = _attempt("28" * 32)
    empty_bytes = b""
    empty_body.commit_attempt(empty_attempt, request_body=request)
    empty_body.commit_capture(
        organic_http_capture_document(
            attempt=empty_attempt,
            request_started_at="2026-08-18T17:37:03.100000Z",
            transport_ended_at="2026-08-18T17:37:03.400000Z",
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
            response_headers_at="2026-08-18T17:37:03.200000Z",
            response_body_ended_at="2026-08-18T17:37:03.300000Z",
        ),
        response_body=empty_bytes,
    )
    with connect(postgres_dsn) as connection:
        empty_summary = derive_google_organic(empty_body, connection)
        empty_row = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE capture_id IS NOT NULL
            ORDER BY attempt_id
            """
        ).fetchall()
        empty_envelopes = connection.execute(
            "SELECT count(*) FROM observation_envelopes"
        ).fetchone()
        empty_context = connection.execute(
            "SELECT count(*) FROM google_organic_result_context"
        ).fetchone()
        empty_occ = connection.execute(
            "SELECT count(*) FROM google_organic_aio_source_occurrences"
        ).fetchone()
    assert empty_summary.observations == 0
    assert ("transport_complete_non_admissible", 0) in empty_row
    assert empty_envelopes == (0,)
    assert empty_context == (0,)
    assert empty_occ == (0,)

    partial = create_store(tmp_path / "partial")
    partial_attempt = _attempt("27" * 32)
    chunk = _body()[:32]
    partial.commit_attempt(partial_attempt, request_body=request)
    partial.commit_capture(
        organic_http_capture_document(
            attempt=partial_attempt,
            request_started_at="2026-08-18T17:37:02.100000Z",
            transport_ended_at="2026-08-18T17:37:02.400000Z",
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
            response_headers_at="2026-08-18T17:37:02.200000Z",
            response_body_ended_at="2026-08-18T17:37:02.300000Z",
        ),
        response_body=chunk,
    )
    with connect(postgres_dsn) as connection:
        derive_google_organic(partial, connection)
        classes = {
            item[0]
            for item in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
    assert "response_partial" in classes

    document = _decoded()
    document["tasks"][0]["result"][0]["keyword"] = "unrelated subject"
    recon = create_store(tmp_path / "recon")
    _commit_complete(recon, _encode(document), "22" * 32)
    with connect(postgres_dsn) as connection:
        derive_google_organic(recon, connection)
        row = connection.execute(
            """
            SELECT classification
            FROM outcomes
            WHERE capture_id IS NOT NULL
            ORDER BY attempt_id
            """
        ).fetchall()
    assert ("reconciliation_failed",) in row

    error_doc = _decoded()
    error_doc["status_code"] = 40102
    error_doc["tasks"][0]["status_code"] = 40102
    error_store = create_store(tmp_path / "provider-error")
    _commit_complete(error_store, _encode(error_doc), "24" * 32)
    with connect(postgres_dsn) as connection:
        derive_google_organic(error_store, connection)
        classes = {
            row[0]
            for row in connection.execute(
                "SELECT classification FROM outcomes WHERE capture_id IS NOT NULL"
            ).fetchall()
        }
    assert "provider_error" in classes

    bad_doc = _decoded()
    bad_doc["tasks"][0]["result"][0]["items_count"] = 110
    bad_store = create_store(tmp_path / "envelope")
    _commit_complete(bad_store, _encode(bad_doc), "25" * 32)
    with connect(postgres_dsn) as connection:
        derive_google_organic(bad_store, connection)
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
        summary = derive_google_organic(damaged, connection)
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


def test_exact_content_extra_rows_and_missing_restore(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "17" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        first = derive_google_organic(store, connection)
        second = derive_google_organic(store, connection)
        assert first == second
        original_title = connection.execute(
            """
            SELECT title FROM google_organic_ranked_results
            WHERE url = %s AND page = 2
            """,
            (PBS_URL,),
        ).fetchone()
        assert original_title is not None
        connection.execute(
            """
            UPDATE google_organic_ranked_results
            SET title = 'planted conflict'
            WHERE url = %s AND page = 2
            """,
            (PBS_URL,),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="conflicting"):
            derive_google_organic(store, connection)
        connection.rollback()
        connection.execute(
            """
            UPDATE google_organic_ranked_results
            SET title = %s
            WHERE url = %s AND page = 2
            """,
            (original_title[0], PBS_URL),
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
            (extra_identity, RELATED_QUERY_KIND),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch"):
            derive_google_organic(store, connection)
        connection.rollback()
        connection.execute(
            """
            DELETE FROM observation_envelopes
            WHERE within_capture_identity = %s
            """,
            (extra_identity,),
        )
        connection.commit()
        extra_occ = connection.execute(
            """
            SELECT capture_id, derivation_version_id, within_capture_identity,
                   observation_kind, locus
            FROM google_organic_aio_source_occurrences
            WHERE element_index IS NULL
            LIMIT 1
            """
        ).fetchone()
        assert extra_occ is not None
        connection.execute(
            """
            INSERT INTO google_organic_aio_source_occurrences (
                capture_id, derivation_version_id, within_capture_identity,
                observation_kind, locus, element_index, reference_index
            )
            VALUES (%s, %s, %s, %s, %s, NULL, 99)
            """,
            extra_occ,
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch"):
            derive_google_organic(store, connection)
        connection.rollback()
        connection.execute(
            """
            DELETE FROM google_organic_aio_source_occurrences
            WHERE reference_index = 99 AND element_index IS NULL
            """
        )
        connection.commit()
        paa_occ = connection.execute(
            """
            SELECT capture_id, derivation_version_id, within_capture_identity,
                   observation_kind, page, position, rank_group, rank_absolute
            FROM google_organic_related_question_occurrences
            LIMIT 1
            """
        ).fetchone()
        assert paa_occ is not None
        connection.execute(
            """
            INSERT INTO google_organic_related_question_occurrences (
                capture_id, derivation_version_id, within_capture_identity,
                observation_kind, page, position, rank_group, rank_absolute,
                question_index
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 99)
            """,
            paa_occ,
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch"):
            derive_google_organic(store, connection)
        connection.rollback()
        connection.execute(
            """
            DELETE FROM google_organic_related_question_occurrences
            WHERE question_index = 99
            """
        )
        connection.commit()
        connection.execute(
            """
            INSERT INTO derivation_diagnostics (
                derivation_version_id, attempt_id, capture_id,
                diagnostic_code, provider_body_path
            )
            SELECT derivation_version_id, attempt_id, capture_id,
                   'unknown_extension', '/planted'
            FROM observation_envelopes
            LIMIT 1
            """
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch"):
            derive_google_organic(store, connection)
        connection.rollback()
        connection.execute(
            """
            DELETE FROM derivation_diagnostics
            WHERE provider_body_path = '/planted'
            """
        )
        connection.commit()
        query = connection.execute(
            """
            SELECT capture_id, derivation_version_id, within_capture_identity
            FROM google_organic_related_queries
            LIMIT 1
            """
        ).fetchone()
        assert query is not None
        connection.execute(
            """
            DELETE FROM google_organic_related_queries
            WHERE within_capture_identity = %s
            """,
            (query[2],),
        )
        connection.execute(
            """
            DELETE FROM observation_envelopes
            WHERE within_capture_identity = %s
            """,
            (query[2],),
        )
        connection.commit()
        restored = derive_google_organic(store, connection)
        count = connection.execute(
            "SELECT count(*) FROM google_organic_related_queries"
        ).fetchone()
    assert restored.observations == 237
    assert count == (9,)


def test_foreign_attempt_outcome_is_complete_set_mismatch(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_complete(store, _body(), "41" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic(store, connection)
        connection.commit()
        accepted = connection.execute(
            """
            SELECT attempt_id, classification, observation_count
            FROM outcomes
            WHERE capture_id = %s
            """,
            (capture_id,),
        ).fetchall()
        ranked_before = connection.execute(
            "SELECT count(*) FROM google_organic_ranked_results"
        ).fetchone()
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, 'observation_admitted', 237)
            """,
            ("cd" * 32, capture_id, GOOGLE_ORGANIC_RECIPE_ID),
        )
        connection.commit()
        with pytest.raises(DerivationError, match="complete-set mismatch"):
            derive_google_organic(store, connection)
        connection.rollback()
        after = connection.execute(
            """
            SELECT attempt_id, classification, observation_count
            FROM outcomes
            WHERE capture_id = %s
            ORDER BY attempt_id
            """,
            (capture_id,),
        ).fetchall()
        ranked_after = connection.execute(
            "SELECT count(*) FROM google_organic_ranked_results"
        ).fetchone()
    assert accepted == [(attempt_id, "observation_admitted", 237)]
    assert (attempt_id, "observation_admitted", 237) in after
    assert ("cd" * 32, "observation_admitted", 237) in after
    assert ranked_before == (97,)
    assert ranked_after == (97,)


def test_result_context_requires_matching_outcome(postgres_dsn: str) -> None:
    from observatory.dataforseo_google_organic import GOOGLE_ORGANIC_RECIPE

    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, GOOGLE_ORGANIC_RECIPE)
        connection.commit()
        with pytest.raises(ForeignKeyViolation):
            connection.execute(
                """
                INSERT INTO google_organic_result_context (
                    capture_id, derivation_version_id, attempt_id,
                    requested_keyword, returned_keyword, returned_keyword_state,
                    location_code, language_code, se_domain, se_domain_state,
                    result_datetime, result_datetime_state,
                    se_results_count, se_results_count_state,
                    pages_count, pages_count_state, items_count, item_types
                )
                VALUES (
                    %s, %s, %s, %s, NULL, 'absent',
                    2840, 'en', NULL, 'absent',
                    NULL, 'absent', NULL, 'absent',
                    NULL, 'absent', 0, ARRAY[]::TEXT[]
                )
                """,
                ("ab" * 32, GOOGLE_ORGANIC_RECIPE_ID, "cd" * 32, KEYWORD),
            )


def test_result_context_field_state_constraints(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "42" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic(store, connection)
        connection.commit()
        with pytest.raises(CheckViolation):
            connection.execute(
                """
                UPDATE google_organic_result_context
                SET result_datetime = NULL
                WHERE result_datetime_state = 'stated'
                """
            )
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute(
                """
                UPDATE google_organic_result_context
                SET result_datetime_state = 'absent'
                WHERE result_datetime IS NOT NULL
                """
            )
        connection.rollback()
        remaining = connection.execute(
            """
            SELECT result_datetime, result_datetime_state
            FROM google_organic_result_context
            """
        ).fetchone()
    assert remaining == ("2026-08-18 17:37:36 +00:00", "stated")


def test_populated_pf08_schema_then_organic_derive(
    tmp_path: Path, postgres_dsn: str
) -> None:
    from observatory.capture_event import PAID_ADAPTER_CONTRACT
    from observatory.dataforseo_keyword_overview import CORE_RECIPE, COVERAGE_KIND
    from observatory.migrate import (
        PRE_AI05_SCHEMA_STATEMENTS,
        PRE_PF12_SCHEMA_STATEMENTS,
        WIDEN_IJSON_COLUMNS_SQL,
    )
    from observatory.provider_recipe import (
        IDENTITY_SCHEMA,
        IDENTITY_VERSION,
        ObservationEnvelope,
        observation_identity,
        write_observation_envelope,
    )

    joined_pre = "\n".join(PRE_PF12_SCHEMA_STATEMENTS)
    assert "provider_recipe_selections" in joined_pre
    assert "keyword_overview_coverage" in joined_pre
    assert "keyword_overview_search_intent" in joined_pre
    assert "google_organic_" not in joined_pre
    organic_statements = [
        statement
        for statement in PRE_AI05_SCHEMA_STATEMENTS
        if statement not in PRE_PF12_SCHEMA_STATEMENTS
    ]
    assert len(organic_statements) == 10
    assert any("google_organic_serp_features" in item for item in organic_statements)
    assert any("google_organic_result_context" in item for item in organic_statements)

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
    with connect(postgres_dsn) as connection:
        for statement in PRE_PF12_SCHEMA_STATEMENTS:
            connection.execute(statement)
        for statement in WIDEN_IJSON_COLUMNS_SQL:
            connection.execute(statement)
        registered = register_provider_recipe(connection, CORE_RECIPE)
        assert registered.derivation_version_id == CORE_RECIPE_ID
        connection.execute(
            """
            INSERT INTO provider_recipe_selections (
                adapter_contract, derivation_version_id
            )
            VALUES (%s, %s)
            """,
            (PAID_ADAPTER_CONTRACT, CORE_RECIPE_ID),
        )
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, NULL, %s, 'authorized_unresolved', 0),
                   (%s, %s, %s, 'observation_admitted', 1)
            """,
            (attempt_id, CORE_RECIPE_ID, attempt_id, capture_id, CORE_RECIPE_ID),
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
        before = connection.execute(
            """
            SELECT adapter_contract, derivation_version_id
            FROM provider_recipe_selections
            """
        ).fetchall()
        before_outcomes = connection.execute(
            """
            SELECT attempt_id, capture_id, classification, observation_count
            FROM outcomes
            ORDER BY capture_id NULLS FIRST
            """
        ).fetchall()
        before_coverage = connection.execute(
            """
            SELECT requested_keyword, covered, returned_keyword
            FROM keyword_overview_coverage
            """
        ).fetchall()
        connection.commit()
        apply_schema(connection)
        after = connection.execute(
            """
            SELECT adapter_contract, derivation_version_id
            FROM provider_recipe_selections
            """
        ).fetchall()
        after_outcomes = connection.execute(
            """
            SELECT attempt_id, capture_id, classification, observation_count
            FROM outcomes
            ORDER BY capture_id NULLS FIRST
            """
        ).fetchall()
        after_coverage = connection.execute(
            """
            SELECT requested_keyword, covered, returned_keyword
            FROM keyword_overview_coverage
            """
        ).fetchall()
        for table in (
            "google_organic_serp_features",
            "google_organic_ranked_results",
            "google_organic_aio_presence",
            "google_organic_aio_sources",
            "google_organic_aio_source_occurrences",
            "google_organic_related_questions",
            "google_organic_related_question_occurrences",
            "google_organic_related_queries",
            "google_organic_result_context",
        ):
            connection.execute(f"SELECT 1 FROM {table} LIMIT 0")
    assert before == after == [(PAID_ADAPTER_CONTRACT, CORE_RECIPE_ID)]
    assert before_outcomes == after_outcomes
    assert before_coverage == after_coverage == [("seo api", True, "seo api")]

    organic = create_store(tmp_path / "organic")
    _commit_complete(organic, _body(), "32" * 32)
    with connect(postgres_dsn) as connection:
        organic_summary = derive_google_organic(organic, connection)
        ko_final = connection.execute(
            "SELECT count(*) FROM keyword_overview_coverage"
        ).fetchone()
        organic_final = connection.execute(
            "SELECT count(*) FROM google_organic_ranked_results"
        ).fetchone()
        selection = connection.execute(
            "SELECT count(*) FROM provider_recipe_selections"
        ).fetchone()
    assert organic_summary.observations == 237
    assert ko_final == (1,)
    assert organic_final == (97,)
    assert selection == (1,)


def test_two_databases_are_logically_equivalent(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "18" * 32)
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)

    def snapshot(dsn: str) -> tuple[object, ...]:
        with connect(dsn) as connection:
            derive_google_organic(store, connection)
            outcomes = connection.execute(
                """
                SELECT classification, observation_count
                FROM outcomes
                WHERE capture_id IS NOT NULL
                """
            ).fetchall()
            envelopes = connection.execute(
                """
                SELECT observation_kind, count(*)
                FROM observation_envelopes
                GROUP BY observation_kind
                ORDER BY observation_kind
                """
            ).fetchall()
            ranked = connection.execute(
                """
                SELECT page, rank_absolute, url
                FROM google_organic_ranked_results
                ORDER BY page, rank_absolute, url
                """
            ).fetchall()
            aio = connection.execute(
                """
                SELECT locus, url
                FROM google_organic_aio_sources
                ORDER BY locus, url
                """
            ).fetchall()
            occ = connection.execute(
                """
                SELECT locus, element_index, reference_index
                FROM google_organic_aio_source_occurrences
                ORDER BY locus, element_index NULLS FIRST, reference_index
                """
            ).fetchall()
            context = connection.execute(
                """
                SELECT items_count, result_datetime, item_types
                FROM google_organic_result_context
                """
            ).fetchall()
            features = connection.execute(
                """
                SELECT item_type, count(*)
                FROM google_organic_serp_features
                GROUP BY item_type
                ORDER BY item_type
                """
            ).fetchall()
            presence = connection.execute(
                "SELECT asynchronous_ai_overview FROM google_organic_aio_presence"
            ).fetchall()
            questions = connection.execute(
                "SELECT title FROM google_organic_related_questions ORDER BY title"
            ).fetchall()
            paa = connection.execute(
                """
                SELECT rank_absolute, question_index
                FROM google_organic_related_question_occurrences
                ORDER BY rank_absolute, question_index
                """
            ).fetchall()
            queries = connection.execute(
                "SELECT query FROM google_organic_related_queries ORDER BY query"
            ).fetchall()
        return (
            outcomes,
            envelopes,
            ranked,
            aio,
            occ,
            context,
            features,
            presence,
            questions,
            paa,
            queries,
        )

    assert snapshot(postgres_dsn) == snapshot(postgres_second_dsn)


def test_fixture_derive_skips_organic_and_organic_skips_fixture(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_complete(store, _body(), "19" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        fixture_summary = derive(store, connection, derivation_version_id=DEFAULT_VERSION)
        organic_before = connection.execute(
            "SELECT count(*) FROM google_organic_ranked_results"
        ).fetchone()
        derive_google_organic(store, connection)
        organic_after = connection.execute(
            "SELECT count(*) FROM google_organic_ranked_results"
        ).fetchone()
    assert fixture_summary.observations == 0
    assert organic_before == (0,)
    assert organic_after == (97,)


def test_provider_rows_cannot_use_fixture_label(postgres_dsn: str) -> None:
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, __import__(
            "observatory.dataforseo_google_organic", fromlist=["GOOGLE_ORGANIC_RECIPE"]
        ).GOOGLE_ORGANIC_RECIPE)
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
                    ORGANIC_ADAPTER_CONTRACT,
                    FEATURE_PRESENCE_KIND,
                    "c" * 64,
                ),
            )
