"""PF-13: Google Organic Attempt dispatch and history API."""

from __future__ import annotations

import copy
import json
import secrets
import socket
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from observatory.api import create_app
from observatory.capture import FixtureCaptureInputs, capture_fixture
from observatory.capture_event import (
    ORGANIC_ADAPTER_CONTRACT,
    PAID_ADAPTER_CONTRACT,
    body_ref,
    http_attempt_document,
    organic_http_attempt_document,
    organic_http_capture_document,
    paid_http_attempt_document,
    paid_http_capture_document,
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
from observatory.dataforseo_keyword_overview import (
    CORE_RECIPE,
    CORE_RECIPE_ID,
    EXTENDED_RECIPE_ID,
)
from observatory.dataforseo_paid_probe import closed_paid_parameters, paid_request_body_bytes
from observatory.dataforseo_sandbox import closed_sandbox_parameters, request_body_bytes
from observatory.derive import DEFAULT_VERSION, derive
from observatory.evidence_store import EvidenceStore, create_store
from observatory.google_organic_derive import derive_google_organic
from observatory.keyword_overview_derive import derive_keyword_overview_extended
from observatory.migrate import apply_migrations, connect
from observatory.provider_recipe import TEST_RECIPE, TEST_RECIPE_ID, register_provider_recipe
from observatory.provider_recipe_selection import NOT_SELECTED_SIGNAL, select_provider_recipe
from observatory.settings import Settings

FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_google_organic_pf10.json"
)
KO_FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_keyword_overview_pf03.json"
)
KEYWORD = "conspiracy theories"
HISTORY = "/v1/providers/dataforseo/google/organic/history"
RELATED_QUERIES = (
    "List of conspiracy theories PDF",
    "Conspiracy theories to talk about with friends",
    "Historical conspiracy theories",
    "Fun harmless conspiracy theories",
    "Ancient history conspiracy theories",
    "Lighthearted conspiracy theories",
    "The Psychology of conspiracy theories",
    "Why do people believe in conspiracy theories",
    "Conspiracy theories Podcast",
)
PAA_TITLES = (
    "What are some of the most popular theories?",
    "What are some controversial conspiracy theories?",
    "What are some famous conspiracy cases?",
    "What are some ancient conspiracy theories?",
)
HISTORY_KEYS = {
    "provider",
    "adapter_contract",
    "requested_keyword",
    "derivation_version_id",
    "recipe_resolution",
    "observation_kinds",
    "captures",
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
    "serp_features",
    "ranked_results",
    "ai_overview_presence",
    "ai_overview_sources",
    "related_questions",
    "related_queries",
}
CONTEXT_KEYS = {
    "requested_keyword",
    "returned_keyword",
    "se_domain",
    "provider_result_time",
    "se_results_count",
    "pages_count",
    "items_count",
    "item_types",
}
FEATURE_KEYS = {
    "observation_kind",
    "within_capture_identity",
    "item_type",
    "page",
    "position",
    "rank_group",
    "rank_absolute",
}
RANKED_KEYS = {
    "observation_kind",
    "within_capture_identity",
    "url",
    "domain",
    "title",
    "description",
    "website_name",
    "page",
    "position",
    "rank_group",
    "rank_absolute",
}
AIO_PRESENCE_KEYS = {
    "observation_kind",
    "within_capture_identity",
    "asynchronous_ai_overview",
    "page",
    "position",
    "rank_group",
    "rank_absolute",
}
AIO_SOURCE_KEYS = {
    "observation_kind",
    "within_capture_identity",
    "locus",
    "url",
    "domain",
    "title",
    "source",
    "occurrences",
}
AIO_OCCURRENCE_KEYS = {"locus", "element_index", "reference_index"}
QUESTION_KEYS = {
    "observation_kind",
    "within_capture_identity",
    "title",
    "occurrences",
}
PAA_OCCURRENCE_KEYS = {
    "page",
    "position",
    "rank_group",
    "rank_absolute",
    "question_index",
}
QUERY_KEYS = {"observation_kind", "within_capture_identity", "query"}
KO_HISTORY = "/v1/providers/dataforseo/google/keyword-overview/history"
ORGANIC_TABLES = (
    "google_organic_result_context",
    "google_organic_serp_features",
    "google_organic_ranked_results",
    "google_organic_aio_presence",
    "google_organic_aio_sources",
    "google_organic_aio_source_occurrences",
    "google_organic_related_questions",
    "google_organic_related_question_occurrences",
    "google_organic_related_queries",
)
READONLY_TABLES = (
    "provider_recipes",
    "provider_recipe_selections",
    "outcomes",
    "observation_envelopes",
    *ORGANIC_TABLES,
)
ORGANIC_KINDS = [
    FEATURE_PRESENCE_KIND,
    ORGANIC_PLACEMENT_KIND,
    AIO_PRESENCE_KIND,
    AIO_SOURCE_KIND,
    RELATED_QUESTION_KIND,
    RELATED_QUERY_KIND,
]


@pytest.fixture(autouse=True)
def _no_public_network(monkeypatch: pytest.MonkeyPatch) -> None:
    real = socket.create_connection

    def guarded(address: Any, *args: Any, **kwargs: Any) -> socket.socket:
        host = address[0] if isinstance(address, tuple) else address
        if host not in {"127.0.0.1", "::1", "localhost"}:
            raise AssertionError(f"public-network request forbidden: {host}")
        return real(address, *args, **kwargs)

    monkeypatch.setattr(socket, "create_connection", guarded)


def _replace_dbname(dsn: str, dbname: str) -> str:
    info = conninfo_to_dict(dsn)
    info["dbname"] = dbname
    return make_conninfo("", **info)


def _body() -> bytes:
    return FIXTURE.read_bytes()


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


def _parameters() -> dict[str, object]:
    return closed_organic_parameters(keyword=KEYWORD)


def _commit_organic(
    store: EvidenceStore,
    body: bytes,
    nonce: str,
    *,
    started: str,
    authorized_at: str = "2026-08-18T17:37:00.000000Z",
) -> tuple[str, str]:
    parameters = _parameters()
    attempt = organic_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at=authorized_at,
        observatory_version="pf13-test-v1",
    )
    attempt_id = store.commit_attempt(
        attempt, request_body=organic_request_body_bytes(parameters)
    )
    capture_id = store.commit_capture(
        organic_http_capture_document(
            attempt=attempt,
            request_started_at=started,
            transport_ended_at=started.replace(".100000Z", ".400000Z"),
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
            response_headers_at=started.replace(".100000Z", ".200000Z"),
            response_body_ended_at=started.replace(".100000Z", ".300000Z"),
        ),
        response_body=body,
    )
    return attempt_id, capture_id


def _commit_ko(store: EvidenceStore, nonce: str, started: str) -> tuple[str, str]:
    parameters = closed_paid_parameters(
        keywords=["keyword research", "ai search optimization"]
    )
    attempt = paid_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at="2026-08-16T21:37:00.000000Z",
        observatory_version="pf13-ko-v1",
    )
    attempt_id = store.commit_attempt(
        attempt, request_body=paid_request_body_bytes(parameters)
    )
    body = KO_FIXTURE.read_bytes()
    capture_id = store.commit_capture(
        paid_http_capture_document(
            attempt=attempt,
            request_started_at=started,
            transport_ended_at=started.replace(".100000Z", ".400000Z"),
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
            response_headers_at=started.replace(".100000Z", ".200000Z"),
            response_body_ended_at=started.replace(".100000Z", ".300000Z"),
        ),
        response_body=body,
    )
    return attempt_id, capture_id


def _commit_sandbox(store: EvidenceStore) -> str:
    parameters = closed_sandbox_parameters(
        keyword="observatory test", location_code=2840, language_code="en"
    )
    attempt = http_attempt_document(
        parameters=parameters,
        attempt_nonce="33" * 32,
        authorized_at="2026-08-14T20:00:00.000000Z",
        observatory_version="pf13-sandbox-v1",
    )
    return store.commit_attempt(attempt, request_body=request_body_bytes(parameters))


def _app(store: EvidenceStore, dsn: str) -> TestClient:
    settings = Settings(
        environment="test",
        database_url=dsn,
        evidence_root=store.root,
        derivation_version_id=DEFAULT_VERSION,
    )
    return TestClient(create_app(settings, store=store))


def _history(client: TestClient, keyword: str = KEYWORD, **params: object) -> Any:
    query = {"requested_keyword": keyword, **params}
    return client.get(HISTORY + "?" + urlencode(query, doseq=True))


def _prepare_frozen(
    tmp_path: Path,
    postgres_dsn: str,
    *,
    select: bool = True,
    derive: bool = True,
) -> tuple[EvidenceStore, str, str]:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_organic(
        store, _body(), "11" * 32, started="2026-08-18T17:37:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        if derive:
            derive_google_organic(store, connection)
        else:
            from observatory.dataforseo_google_organic import GOOGLE_ORGANIC_RECIPE

            register_provider_recipe(connection, GOOGLE_ORGANIC_RECIPE)
        if select:
            select_provider_recipe(
                connection, ORGANIC_ADAPTER_CONTRACT, GOOGLE_ORGANIC_RECIPE_ID
            )
    return store, attempt_id, capture_id


def _xmin_snapshot(dsn: str) -> dict[str, list[tuple[object, ...]]]:
    snapshot: dict[str, list[tuple[object, ...]]] = {}
    with connect(dsn) as connection:
        for table in READONLY_TABLES:
            rows = connection.execute(f"SELECT xmin::text, * FROM {table}").fetchall()
            snapshot[table] = sorted(
                rows, key=lambda row: tuple(str(item) for item in row[1:])
            )
    return snapshot


def _as_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


def _state_value(state: object, value: object) -> dict[str, object]:
    if isinstance(value, tuple):
        value = list(value)
    return {"state": str(state), "value": value}


def _persisted_projection(
    dsn: str, capture_id: str
) -> dict[str, Any]:
    """Map accepted PF-12 rows to the PF-13 response shape without product helpers."""

    with connect(dsn) as connection:
        context = connection.execute(
            """
            SELECT requested_keyword, returned_keyword, returned_keyword_state,
                   se_domain, se_domain_state, result_datetime,
                   result_datetime_state, se_results_count,
                   se_results_count_state, pages_count, pages_count_state,
                   items_count, item_types
            FROM google_organic_result_context
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, GOOGLE_ORGANIC_RECIPE_ID),
        ).fetchone()
        features = connection.execute(
            """
            SELECT within_capture_identity, observation_kind, item_type,
                   page, position, rank_group, rank_absolute
            FROM google_organic_serp_features
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY page, position, rank_absolute, rank_group,
                     within_capture_identity
            """,
            (capture_id, GOOGLE_ORGANIC_RECIPE_ID),
        ).fetchall()
        ranked = connection.execute(
            """
            SELECT within_capture_identity, observation_kind, url, domain, title,
                   description, description_state, website_name,
                   website_name_state, page, position, rank_group, rank_absolute
            FROM google_organic_ranked_results
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY page, position, rank_absolute, rank_group,
                     within_capture_identity
            """,
            (capture_id, GOOGLE_ORGANIC_RECIPE_ID),
        ).fetchall()
        presence = connection.execute(
            """
            SELECT within_capture_identity, observation_kind,
                   asynchronous_ai_overview, page, position, rank_group,
                   rank_absolute
            FROM google_organic_aio_presence
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, GOOGLE_ORGANIC_RECIPE_ID),
        ).fetchone()
        sources = connection.execute(
            """
            SELECT within_capture_identity, observation_kind, locus, url,
                   domain, domain_state, title, title_state, source, source_state
            FROM google_organic_aio_sources
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY locus, url, within_capture_identity
            """,
            (capture_id, GOOGLE_ORGANIC_RECIPE_ID),
        ).fetchall()
        aio_occurrences = connection.execute(
            """
            SELECT within_capture_identity, locus, element_index, reference_index
            FROM google_organic_aio_source_occurrences
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY locus, element_index NULLS FIRST, reference_index
            """,
            (capture_id, GOOGLE_ORGANIC_RECIPE_ID),
        ).fetchall()
        questions = connection.execute(
            """
            SELECT within_capture_identity, observation_kind, title
            FROM google_organic_related_questions
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY title, within_capture_identity
            """,
            (capture_id, GOOGLE_ORGANIC_RECIPE_ID),
        ).fetchall()
        paa_occurrences = connection.execute(
            """
            SELECT within_capture_identity, page, position, rank_group,
                   rank_absolute, question_index
            FROM google_organic_related_question_occurrences
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY page, position, rank_absolute, rank_group, question_index
            """,
            (capture_id, GOOGLE_ORGANIC_RECIPE_ID),
        ).fetchall()
        queries = connection.execute(
            """
            SELECT within_capture_identity, observation_kind, query
            FROM google_organic_related_queries
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY query, within_capture_identity
            """,
            (capture_id, GOOGLE_ORGANIC_RECIPE_ID),
        ).fetchall()
    assert context is not None
    item_types = context[12]
    if isinstance(item_types, tuple):
        item_types = list(item_types)
    aio_by_parent: dict[str, list[dict[str, object]]] = {}
    for row in aio_occurrences:
        identity = str(row[0])
        aio_by_parent.setdefault(identity, []).append(
            {
                "locus": str(row[1]),
                "element_index": (
                    None if row[2] is None else _as_int(row[2], "element_index")
                ),
                "reference_index": _as_int(row[3], "reference_index"),
            }
        )
    paa_by_parent: dict[str, list[dict[str, object]]] = {}
    for row in paa_occurrences:
        identity = str(row[0])
        paa_by_parent.setdefault(identity, []).append(
            {
                "page": _as_int(row[1], "page"),
                "position": str(row[2]),
                "rank_group": _as_int(row[3], "rank_group"),
                "rank_absolute": _as_int(row[4], "rank_absolute"),
                "question_index": _as_int(row[5], "question_index"),
            }
        )
    presence_json: dict[str, object] | None = None
    if presence is not None:
        presence_json = {
            "observation_kind": str(presence[1]),
            "within_capture_identity": str(presence[0]),
            "asynchronous_ai_overview": bool(presence[2]),
            "page": _as_int(presence[3], "page"),
            "position": str(presence[4]),
            "rank_group": _as_int(presence[5], "rank_group"),
            "rank_absolute": _as_int(presence[6], "rank_absolute"),
        }
    return {
        "result_context": {
            "requested_keyword": str(context[0]),
            "returned_keyword": _state_value(context[2], context[1]),
            "se_domain": _state_value(context[4], context[3]),
            "provider_result_time": _state_value(context[6], context[5]),
            "se_results_count": _state_value(context[8], context[7]),
            "pages_count": _state_value(context[10], context[9]),
            "items_count": _as_int(context[11], "items_count"),
            "item_types": item_types,
        },
        "serp_features": [
            {
                "observation_kind": str(row[1]),
                "within_capture_identity": str(row[0]),
                "item_type": str(row[2]),
                "page": _as_int(row[3], "page"),
                "position": str(row[4]),
                "rank_group": _as_int(row[5], "rank_group"),
                "rank_absolute": _as_int(row[6], "rank_absolute"),
            }
            for row in features
        ],
        "ranked_results": [
            {
                "observation_kind": str(row[1]),
                "within_capture_identity": str(row[0]),
                "url": str(row[2]),
                "domain": str(row[3]),
                "title": str(row[4]),
                "description": _state_value(row[6], row[5]),
                "website_name": _state_value(row[8], row[7]),
                "page": _as_int(row[9], "page"),
                "position": str(row[10]),
                "rank_group": _as_int(row[11], "rank_group"),
                "rank_absolute": _as_int(row[12], "rank_absolute"),
            }
            for row in ranked
        ],
        "ai_overview_presence": presence_json,
        "ai_overview_sources": [
            {
                "observation_kind": str(row[1]),
                "within_capture_identity": str(row[0]),
                "locus": str(row[2]),
                "url": str(row[3]),
                "domain": _state_value(row[5], row[4]),
                "title": _state_value(row[7], row[6]),
                "source": _state_value(row[9], row[8]),
                "occurrences": aio_by_parent.get(str(row[0]), []),
            }
            for row in sources
        ],
        "related_questions": [
            {
                "observation_kind": str(row[1]),
                "within_capture_identity": str(row[0]),
                "title": str(row[2]),
                "occurrences": paa_by_parent.get(str(row[0]), []),
            }
            for row in questions
        ],
        "related_queries": [
            {
                "observation_kind": str(row[1]),
                "within_capture_identity": str(row[0]),
                "query": str(row[2]),
            }
            for row in queries
        ],
    }


@pytest.fixture(scope="module")
def frozen_pg(postgres_admin_dsn: str, tmp_path_factory: pytest.TempPathFactory) -> Any:
    dbname = "obs_" + uuid.uuid4().hex
    with psycopg.connect(postgres_admin_dsn, autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
    dsn = _replace_dbname(postgres_admin_dsn, dbname)
    store_root = tmp_path_factory.mktemp("frozen-organic")
    store, attempt_id, capture_id = _prepare_frozen(store_root, dsn)
    try:
        yield store, dsn, attempt_id, capture_id
    finally:
        with psycopg.connect(postgres_admin_dsn, autocommit=True) as admin:
            admin.execute(
                sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(
                    sql.Identifier(dbname)
                )
            )


def test_fixture_and_ko_remain_isolated_from_organic_selection(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, organic_attempt, _organic_capture = _prepare_frozen(tmp_path, postgres_dsn)
    ko_attempt, _ko_capture = _commit_ko(
        store, "51" * 32, started="2026-08-16T21:37:01.100000Z"
    )
    fixture = capture_fixture(
        store,
        FixtureCaptureInputs(
            scenario="admitted_results",
            panel_id="panel-alpha",
            subject_key="subject-one",
            depth=2,
            attempt_nonce=secrets.token_hex(32),
            authorized_at="2026-08-11T20:15:30.123456Z",
            observatory_version="conformance-v1",
            request_started_at="2026-08-11T20:15:30.200000Z",
            transport_ended_at="2026-08-11T20:15:31.000000Z",
            response_headers_at="2026-08-11T20:15:30.900000Z",
            response_body_ended_at="2026-08-11T20:15:30.950000Z",
        ),
    )
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
        derive_keyword_overview_extended(store, connection)
        register_provider_recipe(connection, CORE_RECIPE)
        select_provider_recipe(connection, PAID_ADAPTER_CONTRACT, EXTENDED_RECIPE_ID)
        organic_before = connection.execute(
            """
            SELECT derivation_version_id FROM provider_recipe_selections
            WHERE adapter_contract = %s
            """,
            (ORGANIC_ADAPTER_CONTRACT,),
        ).fetchone()
        select_provider_recipe(connection, PAID_ADAPTER_CONTRACT, CORE_RECIPE_ID)
        organic_after = connection.execute(
            """
            SELECT derivation_version_id FROM provider_recipe_selections
            WHERE adapter_contract = %s
            """,
            (ORGANIC_ADAPTER_CONTRACT,),
        ).fetchone()
    assert organic_before == organic_after == (GOOGLE_ORGANIC_RECIPE_ID,)
    sandbox_id = _commit_sandbox(store)
    with _app(store, postgres_dsn) as client:
        fixture_body = client.get(f"/v1/attempts/{fixture.attempt_id}").json()
        ko_body = client.get(
            f"/v1/attempts/{ko_attempt}?derivation_version_id={EXTENDED_RECIPE_ID}"
        ).json()
        organic = client.get(f"/v1/attempts/{organic_attempt}").json()
        sandbox = client.get(f"/v1/attempts/{sandbox_id}")
        ko_history = client.get(
            KO_HISTORY
            + "?"
            + urlencode(
                {
                    "requested_keyword": "keyword research",
                    "derivation_version_id": EXTENDED_RECIPE_ID,
                }
            )
        )
        organic_history = _history(client)
    assert set(fixture_body) == {
        "attempt_id",
        "derivation_version_id",
        "attempt_outcome",
        "capture_outcome",
        "observations",
    }
    assert fixture_body["observations"][0]["panel_id"] == "panel-alpha"
    assert fixture_body["observations"][0]["score"] == 999
    assert ko_body["adapter_contract"] == PAID_ADAPTER_CONTRACT
    assert ko_body["derivation_version_id"] == EXTENDED_RECIPE_ID
    assert ko_body["recipe_resolution"] == "pinned"
    assert "observations" not in ko_body
    assert organic["adapter_contract"] == ORGANIC_ADAPTER_CONTRACT
    assert organic["derivation_version_id"] == GOOGLE_ORGANIC_RECIPE_ID
    assert sandbox.status_code == 404
    assert sandbox.json() == {"detail": "not found"}
    assert ko_history.status_code == 200
    assert ko_history.json()["adapter_contract"] == PAID_ADAPTER_CONTRACT
    assert organic_history.status_code == 200
    assert organic_history.json()["adapter_contract"] == ORGANIC_ADAPTER_CONTRACT
    assert organic_history.json()["derivation_version_id"] == GOOGLE_ORGANIC_RECIPE_ID


def test_organic_attempt_selected_pinned_and_http_errors(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_frozen(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, TEST_RECIPE)
    with _app(store, postgres_dsn) as client:
        selected = client.get(f"/v1/attempts/{attempt_id}")
        pinned = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={GOOGLE_ORGANIC_RECIPE_ID}"
        )
        wrong = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={CORE_RECIPE_ID}"
        )
        unknown = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={'ab' * 32}"
        )
        test_recipe = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={TEST_RECIPE_ID}"
        )
        malformed = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id=not-a-digest"
        )
    assert selected.status_code == 200
    body = selected.json()
    assert body["attempt_id"] == attempt_id
    assert body["provider"] == "dataforseo"
    assert body["adapter_contract"] == ORGANIC_ADAPTER_CONTRACT
    assert body["derivation_version_id"] == GOOGLE_ORGANIC_RECIPE_ID
    assert body["recipe_resolution"] == "selected"
    assert body["attempt_outcome"]["classification"] == "authorized_unresolved"
    assert body["capture_outcome"]["capture_id"] == capture_id
    assert body["capture_outcome"]["observation_count"] == 237
    assert "observations" not in body
    assert "panel_id" not in body
    assert pinned.status_code == 200
    assert pinned.json()["recipe_resolution"] == "pinned"
    assert pinned.json()["derivation_version_id"] == GOOGLE_ORGANIC_RECIPE_ID
    assert wrong.status_code == 404
    assert unknown.status_code == 404
    assert test_recipe.status_code == 404
    assert malformed.status_code == 404
    empty_store = create_store(tmp_path / "empty")
    empty_attempt, _empty_capture = _commit_organic(
        empty_store, _body(), "12" * 32, started="2026-08-18T17:37:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        from observatory.dataforseo_google_organic import GOOGLE_ORGANIC_RECIPE

        register_provider_recipe(connection, GOOGLE_ORGANIC_RECIPE)
        select_provider_recipe(
            connection, ORGANIC_ADAPTER_CONTRACT, GOOGLE_ORGANIC_RECIPE_ID
        )
    with _app(empty_store, postgres_dsn) as client:
        missing_rows = client.get(f"/v1/attempts/{empty_attempt}")
        empty_history = _history(client, "not-a-requested-keyword")
    assert missing_rows.status_code == 404
    assert empty_history.status_code == 200
    assert empty_history.json()["captures"] == []
    unselected = create_store(tmp_path / "unselected")
    unselected_attempt, _cap = _commit_organic(
        unselected, _body(), "13" * 32, started="2026-08-18T17:37:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic(unselected, connection)
        connection.execute(
            "DELETE FROM provider_recipe_selections WHERE adapter_contract = %s",
            (ORGANIC_ADAPTER_CONTRACT,),
        )
    with _app(unselected, postgres_dsn) as client:
        missing_selection = client.get(f"/v1/attempts/{unselected_attempt}")
        unselected_history = _history(client)
    assert missing_selection.status_code == 503
    assert missing_selection.json()["detail"] == NOT_SELECTED_SIGNAL
    assert unselected_history.status_code == 503
    assert unselected_history.json()["detail"] == NOT_SELECTED_SIGNAL


def test_frozen_history_shape_counts_times_and_request_context(frozen_pg: Any) -> None:
    store, dsn, attempt_id, capture_id = frozen_pg
    with _app(store, dsn) as client:
        response = _history(client)
        pinned = _history(client, derivation_version_id=GOOGLE_ORGANIC_RECIPE_ID)
        spec = client.get("/api/v1/openapi.json")
        missing = client.get(HISTORY)
        bad_limit = _history(client, limit=0)
        high_limit = _history(client, limit=101)
        bad_order = _history(client, order="sideways")
    assert response.status_code == 200
    body = response.json()
    expected = _persisted_projection(dsn, capture_id)
    assert set(body) == HISTORY_KEYS
    assert body["provider"] == "dataforseo"
    assert body["adapter_contract"] == ORGANIC_ADAPTER_CONTRACT
    assert body["requested_keyword"] == KEYWORD
    assert body["derivation_version_id"] == GOOGLE_ORGANIC_RECIPE_ID
    assert body["recipe_resolution"] == "selected"
    assert body["observation_kinds"] == ORGANIC_KINDS
    assert len(body["captures"]) == 1
    group = body["captures"][0]
    assert set(group) == CAPTURE_KEYS
    assert group["attempt_id"] == attempt_id
    assert group["capture_id"] == capture_id
    assert group["provider"] == "dataforseo"
    assert group["adapter_contract"] == ORGANIC_ADAPTER_CONTRACT
    assert group["derivation_version_id"] == GOOGLE_ORGANIC_RECIPE_ID
    assert group["authorized_at"] == "2026-08-18T17:37:00.000000Z"
    assert group["request_started_at"] == "2026-08-18T17:37:01.100000Z"
    assert group["transport_ended_at"] == "2026-08-18T17:37:01.400000Z"
    assert group["request"] == {
        "location_code": 2840,
        "language_code": "en",
        "depth": 100,
        "device": "desktop",
        "os": "windows",
        "group_organic_results": True,
        "load_async_ai_overview": True,
    }
    assert group["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": 237,
    }
    context = group["result_context"]
    assert set(context) == CONTEXT_KEYS
    assert context == expected["result_context"]
    assert context["requested_keyword"] == KEYWORD
    assert context["provider_result_time"] == {
        "state": "stated",
        "value": "2026-08-18 17:37:36 +00:00",
    }
    assert context["provider_result_time"]["value"] != group["request_started_at"]
    assert context["provider_result_time"]["value"] != group["transport_ended_at"]
    assert context["items_count"] == 111
    assert context["item_types"] == [
        "ai_overview",
        "organic",
        "people_also_ask",
        "top_stories",
        "video",
        "related_searches",
    ]
    assert context["item_types"] == expected["result_context"]["item_types"]
    assert "cost" not in context
    assert "check_url" not in json.dumps(body)
    assert "task" not in json.dumps(context)
    features = group["serp_features"]
    assert features == expected["serp_features"]
    assert len(features) == 111
    assert all(set(row) == FEATURE_KEYS for row in features)
    assert all(row["observation_kind"] == FEATURE_PRESENCE_KIND for row in features)
    assert all(len(str(row["within_capture_identity"])) == 64 for row in features)
    ranked = group["ranked_results"]
    assert ranked == expected["ranked_results"]
    assert len(ranked) == 97
    assert len({row["url"] for row in ranked}) == 87
    assert all(set(row) == RANKED_KEYS for row in ranked)
    assert all(row["observation_kind"] == ORGANIC_PLACEMENT_KIND for row in ranked)
    assert all(len(str(row["within_capture_identity"])) == 64 for row in ranked)
    presence = group["ai_overview_presence"]
    assert presence == expected["ai_overview_presence"]
    assert presence is not None
    assert set(presence) == AIO_PRESENCE_KEYS
    assert presence["observation_kind"] == AIO_PRESENCE_KIND
    sources = group["ai_overview_sources"]
    expected_sources = expected["ai_overview_sources"]
    assert isinstance(expected_sources, list)
    assert sources == expected_sources
    assert len(sources) == 15
    assert [(row["locus"], row["url"]) for row in sources] == [
        (row["locus"], row["url"]) for row in expected_sources
    ]
    assert len({(row["locus"], row["url"]) for row in sources}) == 15
    assert all(set(row) == AIO_SOURCE_KEYS for row in sources)
    assert all(row["observation_kind"] == AIO_SOURCE_KIND for row in sources)
    assert all(len(str(row["within_capture_identity"])) == 64 for row in sources)
    occurrences = [item for source in sources for item in source["occurrences"]]
    expected_occurrences = [
        item for source in expected_sources for item in source["occurrences"]
    ]
    assert occurrences == expected_occurrences
    assert len(occurrences) == 18
    assert all(set(item) == AIO_OCCURRENCE_KEYS for item in occurrences)
    assert sum(1 for item in occurrences if item["element_index"] is None) == 7
    assert sum(1 for item in occurrences if item["element_index"] is not None) == 11
    attached = [
        (
            source["locus"],
            source["url"],
            item["locus"],
            item["element_index"],
            item["reference_index"],
        )
        for source in sources
        for item in source["occurrences"]
    ]
    expected_attached = [
        (
            source["locus"],
            source["url"],
            item["locus"],
            item["element_index"],
            item["reference_index"],
        )
        for source in expected_sources
        for item in source["occurrences"]
    ]
    assert attached == expected_attached
    assert all(item[0] == item[2] for item in attached)
    questions = group["related_questions"]
    expected_questions = expected["related_questions"]
    assert isinstance(expected_questions, list)
    assert questions == expected_questions
    assert [row["title"] for row in questions] == sorted(PAA_TITLES)
    assert len(questions) == 4
    assert all(set(row) == QUESTION_KEYS for row in questions)
    assert all(row["observation_kind"] == RELATED_QUESTION_KIND for row in questions)
    assert all(len(str(row["within_capture_identity"])) == 64 for row in questions)
    assert all(len(row["occurrences"]) == 1 for row in questions)
    assert all(
        set(item) == PAA_OCCURRENCE_KEYS
        for row in questions
        for item in row["occurrences"]
    )
    queries = group["related_queries"]
    assert queries == expected["related_queries"]
    assert [row["query"] for row in queries] == sorted(RELATED_QUERIES)
    assert all(set(row) == QUERY_KEYS for row in queries)
    assert all(row["observation_kind"] == RELATED_QUERY_KIND for row in queries)
    assert all(len(str(row["within_capture_identity"])) == 64 for row in queries)
    assert pinned.status_code == 200
    assert pinned.json()["recipe_resolution"] == "pinned"
    assert spec.status_code == 200
    assert HISTORY in spec.json()["paths"]
    assert missing.status_code == 422
    assert bad_limit.status_code == 422
    assert high_limit.status_code == 422
    assert bad_order.status_code == 422


def test_admitted_empty_and_non_admitted_context_stay_distinct(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    _set_items(document, [])
    store = create_store(tmp_path / "empty")
    empty_attempt, empty_capture = _commit_organic(
        store, _encode(document), "26" * 32, started="2026-08-18T17:37:02.100000Z"
    )
    frozen_attempt, frozen_capture = _commit_organic(
        store, _body(), "11" * 32, started="2026-08-18T17:37:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic(store, connection)
        select_provider_recipe(
            connection, ORGANIC_ADAPTER_CONTRACT, GOOGLE_ORGANIC_RECIPE_ID
        )
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                "ab" * 32,
                "cd" * 32,
                GOOGLE_ORGANIC_RECIPE_ID,
                "provider_error",
                0,
            ),
        )
        connection.execute(
            """
            INSERT INTO google_organic_result_context (
                capture_id, derivation_version_id, attempt_id, requested_keyword,
                returned_keyword, returned_keyword_state, location_code,
                language_code, se_domain, se_domain_state, result_datetime,
                result_datetime_state, se_results_count, se_results_count_state,
                pages_count, pages_count_state, items_count, item_types
            )
            VALUES (
                %s, %s, %s, %s, NULL, 'absent', 2840, 'en', NULL, 'absent',
                NULL, 'absent', NULL, 'absent', NULL, 'absent', 0, ARRAY[]::TEXT[]
            )
            """,
            ("cd" * 32, GOOGLE_ORGANIC_RECIPE_ID, "ab" * 32, KEYWORD),
        )
        envelopes = connection.execute(
            "SELECT count(*) FROM observation_envelopes WHERE capture_id = %s",
            (empty_capture,),
        ).fetchone()
    assert envelopes == (0,)
    with _app(store, postgres_dsn) as client:
        response = _history(client, order="asc")
    assert response.status_code == 200
    captures = response.json()["captures"]
    assert [item["capture_id"] for item in captures] == [frozen_capture, empty_capture]
    assert captures[0]["attempt_id"] == frozen_attempt
    empty = captures[1]
    assert empty["attempt_id"] == empty_attempt
    assert empty["capture_outcome"] == {
        "classification": "observation_admitted_empty",
        "observation_count": 0,
    }
    assert empty["result_context"]["items_count"] == 0
    assert empty["serp_features"] == []
    assert empty["ranked_results"] == []
    assert empty["ai_overview_presence"] is None
    assert empty["ai_overview_sources"] == []
    assert empty["related_questions"] == []
    assert empty["related_queries"] == []
    assert all(item["capture_id"] != "cd" * 32 for item in captures)


def test_second_capture_paa_block_order_limit_and_tie_break(
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
    organic = next(item for item in items if item.get("type") == "organic")
    organic["title"] = "revised conspiracy theories"
    store = create_store(tmp_path / "two")
    first_attempt, first_capture = _commit_organic(
        store, _body(), "31" * 32, started="2026-08-18T17:37:01.100000Z"
    )
    later_attempt, later_capture = _commit_organic(
        store,
        _encode(document),
        "32" * 32,
        started="2026-08-18T17:38:01.100000Z",
        authorized_at="2026-08-18T17:38:00.000000Z",
    )
    tied_a_attempt, tied_a_capture = _commit_organic(
        store,
        _encode(document),
        "33" * 32,
        started="2026-08-18T17:39:01.100000Z",
        authorized_at="2026-08-18T17:39:00.000000Z",
    )
    tied_b_attempt, tied_b_capture = _commit_organic(
        store,
        _body(),
        "34" * 32,
        started="2026-08-18T17:39:01.100000Z",
        authorized_at="2026-08-18T17:39:00.500000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic(store, connection)
        select_provider_recipe(
            connection, ORGANIC_ADAPTER_CONTRACT, GOOGLE_ORGANIC_RECIPE_ID
        )
    with _app(store, postgres_dsn) as client:
        ascending = _history(client, order="asc")
        descending = _history(client, order="desc", limit=2)
        limited = _history(client, order="asc", limit=1)
    assert ascending.status_code == 200
    captures = ascending.json()["captures"]
    assert [item["capture_id"] for item in captures] == [
        first_capture,
        later_capture,
        *sorted([tied_a_capture, tied_b_capture]),
    ]
    assert captures[0]["attempt_id"] == first_attempt
    assert captures[1]["attempt_id"] == later_attempt
    first_titles = {row["title"] for row in captures[0]["ranked_results"]}
    later_titles = {row["title"] for row in captures[1]["ranked_results"]}
    assert "revised conspiracy theories" not in first_titles
    assert "revised conspiracy theories" in later_titles
    later_questions = captures[1]["related_questions"]
    persisted = _persisted_projection(postgres_dsn, later_capture)
    expected_questions = persisted["related_questions"]
    assert isinstance(expected_questions, list)
    assert later_questions == expected_questions
    assert [row["title"] for row in later_questions] == sorted(PAA_TITLES)
    assert len(later_questions) == 4
    assert all(set(row) == QUESTION_KEYS for row in later_questions)
    assert all(row["observation_kind"] == RELATED_QUESTION_KIND for row in later_questions)
    by_title = {row["title"]: row["occurrences"] for row in later_questions}
    expected_by_title = {row["title"]: row["occurrences"] for row in expected_questions}
    assert set(by_title) == set(PAA_TITLES)
    for index, title in enumerate(PAA_TITLES):
        occurrences = by_title[title]
        expected_occurrences = expected_by_title[title]
        assert occurrences == expected_occurrences
        assert len(occurrences) == 2
        assert all(set(item) == PAA_OCCURRENCE_KEYS for item in occurrences)
        first, second = occurrences
        assert first["rank_absolute"] == 3
        assert first["rank_group"] == 1
        assert second["rank_absolute"] == 112
        assert second["rank_group"] == 2
        assert first["question_index"] == index
        assert second["question_index"] == index
        assert first["page"] == second["page"]
        assert first["position"] == second["position"]
    assert descending.json()["captures"][0]["capture_id"] == max(
        tied_a_capture, tied_b_capture
    )
    assert [item["capture_id"] for item in limited.json()["captures"]] == [first_capture]
    assert len(limited.json()["captures"][0]["ranked_results"]) == 97
    assert {captures[2]["attempt_id"], captures[3]["attempt_id"]} == {
        tied_a_attempt,
        tied_b_attempt,
    }
    assert captures[2]["request_started_at"] == captures[3]["request_started_at"]
    assert captures[2]["capture_id"] < captures[3]["capture_id"]


def test_foreign_attempt_outcome_does_not_supply_history(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_frozen(tmp_path, postgres_dsn)
    foreign_attempt = "ab" * 32
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (foreign_attempt, capture_id, GOOGLE_ORGANIC_RECIPE_ID, "provider_error", 0),
        )
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    assert response.status_code == 200
    captures = response.json()["captures"]
    assert [item["capture_id"] for item in captures] == [capture_id]
    assert captures[0]["attempt_id"] == attempt_id
    assert captures[0]["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": 237,
    }


def test_request_context_integrity_and_damage_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_frozen(tmp_path, postgres_dsn)
    later_attempt, later_capture = _commit_organic(
        store,
        _body(),
        "41" * 32,
        started="2026-08-18T17:38:01.100000Z",
        authorized_at="2026-08-18T17:38:00.000000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic(store, connection)
        select_provider_recipe(
            connection, ORGANIC_ADAPTER_CONTRACT, GOOGLE_ORGANIC_RECIPE_ID
        )
        connection.execute(
            """
            UPDATE google_organic_result_context
            SET location_code = 9999
            WHERE capture_id = %s
            """,
            (capture_id,),
        )
    with _app(store, postgres_dsn) as client:
        disagreed = _history(client)
    assert disagreed.status_code == 409
    assert disagreed.json()["detail"] == "evidence_integrity_failure"
    assert "captures" not in disagreed.json()

    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE google_organic_result_context
            SET location_code = 2840
            WHERE capture_id = %s
            """,
            (capture_id,),
        )

    real_read = EvidenceStore.read_attempt.__get__(store, EvidenceStore)

    def _install_mutator(drop: str | None, mistype: str | None) -> None:
        def mutated(value: str) -> dict[str, object] | None:
            attempt = real_read(value)
            if attempt is None:
                return None
            raw_parameters = attempt["parameters"]
            if not isinstance(raw_parameters, dict):
                raise TypeError("verified Attempt parameters must be an object")
            parameters = dict(raw_parameters)
            if drop is not None:
                parameters.pop(drop, None)
            if mistype is not None:
                parameters[mistype] = "not-an-int"
            changed = dict(attempt)
            changed["parameters"] = parameters
            return changed

        store.read_attempt = mutated  # type: ignore[method-assign, assignment]

    _install_mutator(drop="depth", mistype=None)
    with _app(store, postgres_dsn) as client:
        missing_depth = _history(client)
    _install_mutator(drop=None, mistype="location_code")
    with _app(store, postgres_dsn) as client:
        wrong_type = _history(client)
    store.read_attempt = real_read  # type: ignore[method-assign]
    assert missing_depth.status_code == 409
    assert "captures" not in missing_depth.json()
    assert wrong_type.status_code == 409
    assert "captures" not in wrong_type.json()

    body_path = store.capture_path(later_capture) / "response.body"
    payload = bytearray(body_path.read_bytes())
    payload[0] ^= 0x01
    body_path.write_bytes(bytes(payload))
    with _app(store, postgres_dsn) as client:
        outside = _history(client, limit=1, order="asc")
        resource = client.get(f"/v1/attempts/{later_attempt}")
    assert outside.status_code == 409
    assert "captures" not in outside.json()
    assert resource.status_code == 409
    body_path.write_bytes(bytes(bytearray(payload[0] ^ 0x01) + payload[1:]))

    manifest = store.capture_path(capture_id) / "capture.json"
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    with _app(store, postgres_dsn) as client:
        damaged_capture = _history(client)
    assert damaged_capture.status_code == 409
    assert "captures" not in damaged_capture.json()


def test_api_reads_do_not_mutate_organic_state(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, _capture_id = _prepare_frozen(tmp_path, postgres_dsn)
    before_ops = list(store.recorded_ops)
    before_pg = _xmin_snapshot(postgres_dsn)
    with _app(store, postgres_dsn) as client:
        assert client.get(f"/v1/attempts/{attempt_id}").status_code == 200
        assert _history(client).status_code == 200
    assert store.recorded_ops == before_ops
    assert _xmin_snapshot(postgres_dsn) == before_pg


def test_two_databases_return_equal_organic_history(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_organic(store, _body(), "51" * 32, started="2026-08-18T17:37:01.100000Z")
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)
    for dsn in (postgres_dsn, postgres_second_dsn):
        with connect(dsn) as connection:
            derive_google_organic(store, connection)
            select_provider_recipe(
                connection, ORGANIC_ADAPTER_CONTRACT, GOOGLE_ORGANIC_RECIPE_ID
            )
    with (
        _app(store, postgres_dsn) as left,
        _app(store, postgres_second_dsn) as right,
    ):
        left_body = _history(left)
        right_body = _history(right)
    assert left_body.status_code == 200
    assert right_body.status_code == 200
    assert left_body.json() == right_body.json()
    assert left_body.json()["captures"]
    assert left_body.json()["captures"][0]["capture_outcome"]["observation_count"] == 237
