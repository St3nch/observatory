"""PF-08: provider Attempt audit and Keyword Overview history API."""

from __future__ import annotations

import copy
import json
import secrets
import socket
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient

from observatory.api import create_app
from observatory.capture import FixtureCaptureInputs, capture_fixture
from observatory.capture_event import (
    body_ref,
    paid_http_attempt_document,
    paid_http_capture_document,
)
from observatory.dataforseo_keyword_overview import (
    BACKLINKS_KIND,
    CORE_RECIPE_ID,
    COVERAGE_KIND,
    EXTENDED_RECIPE,
    EXTENDED_RECIPE_ID,
    INTENT_KIND,
    METRICS_KIND,
    MONTHLY_KIND,
    PROPERTIES_KIND,
    TREND_KIND,
)
from observatory.dataforseo_paid_probe import closed_paid_parameters, paid_request_body_bytes
from observatory.derive import DEFAULT_VERSION, derive
from observatory.evidence_store import EvidenceStore, create_store
from observatory.keyword_overview_derive import (
    derive_keyword_overview,
    derive_keyword_overview_extended,
)
from observatory.migrate import apply_migrations, connect
from observatory.provider_recipe import (
    IDENTITY_SCHEMA,
    IDENTITY_VERSION,
    TEST_RECIPE,
    TEST_RECIPE_ID,
    observation_identity,
    register_provider_recipe,
)
from observatory.provider_recipe_selection import (
    NOT_SELECTED_SIGNAL,
    select_provider_recipe,
)
from observatory.settings import Settings

SHARED_TIMES = {
    "authorized_at": "2026-08-11T20:15:30.123456Z",
    "observatory_version": "conformance-v1",
    "request_started_at": "2026-08-11T20:15:30.200000Z",
    "transport_ended_at": "2026-08-11T20:15:31.000000Z",
}


def _fixture_inputs() -> FixtureCaptureInputs:
    return FixtureCaptureInputs(
        scenario="admitted_results",
        panel_id="panel-alpha",
        subject_key="subject-one",
        depth=2,
        attempt_nonce=secrets.token_hex(32),
        response_headers_at="2026-08-11T20:15:30.900000Z",
        response_body_ended_at="2026-08-11T20:15:30.950000Z",
        **SHARED_TIMES,
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
HISTORY = "/v1/providers/dataforseo/google/keyword-overview/history"
INTEGRITY_SIGNAL = "evidence_integrity_failure"


@pytest.fixture(autouse=True)
def _no_public_network(monkeypatch: pytest.MonkeyPatch) -> None:
    real = socket.create_connection

    def guarded(address: Any, *args: Any, **kwargs: Any) -> socket.socket:
        host = address[0] if isinstance(address, tuple) else address
        if host not in {"127.0.0.1", "::1", "localhost"}:
            raise AssertionError(f"public-network request forbidden: {host}")
        return real(address, *args, **kwargs)

    monkeypatch.setattr(socket, "create_connection", guarded)
PROVIDER_TABLES = (
    "provider_recipes",
    "provider_recipe_selections",
    "outcomes",
    "observation_envelopes",
    "keyword_overview_coverage",
    "keyword_overview_metrics",
    "keyword_overview_monthly_search_volume",
    "keyword_overview_search_volume_trend",
    "keyword_overview_properties",
    "keyword_overview_avg_backlinks",
    "keyword_overview_search_intent",
)


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


def _commit_paid(
    store: EvidenceStore,
    body: bytes,
    nonce: str,
    *,
    started: str,
    authorized_at: str = "2026-08-16T21:37:00.000000Z",
    keywords: tuple[str, ...] = KEYWORDS,
) -> tuple[str, str]:
    parameters = closed_paid_parameters(keywords=list(keywords))
    attempt = paid_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at=authorized_at,
        observatory_version="pf08-test-v1",
    )
    attempt_id = store.commit_attempt(
        attempt, request_body=paid_request_body_bytes(parameters)
    )
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


def _app(store: EvidenceStore, dsn: str) -> TestClient:
    settings = Settings(
        environment="test",
        database_url=dsn,
        evidence_root=store.root,
        derivation_version_id=DEFAULT_VERSION,
    )
    return TestClient(create_app(settings, store=store))


def _prepare_pf03(
    tmp_path: Path,
    postgres_dsn: str,
    *,
    extended: bool = True,
    core: bool = True,
    select: bool = True,
) -> tuple[EvidenceStore, str, str]:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_paid(
        store, _body(), "21" * 32, started="2026-08-16T21:37:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        if core:
            derive_keyword_overview(store, connection)
        if extended:
            derive_keyword_overview_extended(store, connection)
        if select and extended:
            select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
        elif select and core:
            select_provider_recipe(connection, store_adapter(), CORE_RECIPE_ID)
    return store, attempt_id, capture_id


def store_adapter() -> str:
    return "dataforseo-labs-google-keyword-overview-live-paid-probe-v1"


def _history(
    client: TestClient,
    keyword: str,
    **params: object,
) -> Any:
    query = {"requested_keyword": keyword, **params}
    return client.get(HISTORY + "?" + urlencode(query, doseq=True))


def _xmin_snapshot(dsn: str) -> dict[str, list[tuple[object, ...]]]:
    snapshot: dict[str, list[tuple[object, ...]]] = {}
    with connect(dsn) as connection:
        for table in PROVIDER_TABLES:
            rows = connection.execute(f"SELECT xmin::text, * FROM {table}").fetchall()
            snapshot[table] = sorted(
                rows, key=lambda row: tuple(str(item) for item in row[1:])
            )
    return snapshot


def test_fixture_attempt_json_is_unchanged_when_provider_rows_exist(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt_id, _capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    fixture = capture_fixture(store, _fixture_inputs())
    with connect(postgres_dsn) as connection:
        derive(store, connection, DEFAULT_VERSION)
    with _app(store, postgres_dsn) as client:
        response = client.get(f"/v1/attempts/{fixture.attempt_id}")
    body = response.json()
    assert response.status_code == 200
    assert set(body) == {
        "attempt_id",
        "derivation_version_id",
        "attempt_outcome",
        "capture_outcome",
        "observations",
    }
    assert "recipe_resolution" not in body
    assert "adapter_contract" not in body
    assert body["derivation_version_id"] == DEFAULT_VERSION
    assert body["observations"][0]["panel_id"] == "panel-alpha"
    assert body["observations"][0]["score"] == 999


def test_provider_attempt_selected_and_pinned_recipes(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        selected = client.get(f"/v1/attempts/{attempt_id}")
        pinned = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={CORE_RECIPE_ID}"
        )
    assert selected.status_code == 200
    selected_body = selected.json()
    assert selected_body["attempt_id"] == attempt_id
    assert selected_body["provider"] == "dataforseo"
    assert selected_body["adapter_contract"] == store_adapter()
    assert selected_body["derivation_version_id"] == EXTENDED_RECIPE_ID
    assert selected_body["recipe_resolution"] == "selected"
    assert selected_body["attempt_outcome"]["classification"] == "authorized_unresolved"
    assert selected_body["capture_outcome"]["capture_id"] == capture_id
    assert selected_body["capture_outcome"]["observation_count"] == 471
    assert "observations" not in selected_body
    assert "panel_id" not in selected_body
    assert pinned.status_code == 200
    pinned_body = pinned.json()
    assert pinned_body["derivation_version_id"] == CORE_RECIPE_ID
    assert pinned_body["recipe_resolution"] == "pinned"
    assert pinned_body["capture_outcome"]["observation_count"] == 10
    with connect(postgres_dsn) as connection:
        select_provider_recipe(connection, store_adapter(), CORE_RECIPE_ID)
        extended_count = connection.execute(
            """
            SELECT observation_count FROM outcomes
            WHERE attempt_id = %s AND capture_id = %s
              AND derivation_version_id = %s
            """,
            (attempt_id, capture_id, EXTENDED_RECIPE_ID),
        ).fetchone()
    with _app(store, postgres_dsn) as client:
        after = client.get(f"/v1/attempts/{attempt_id}")
    assert after.json()["derivation_version_id"] == CORE_RECIPE_ID
    assert after.json()["capture_outcome"]["observation_count"] == 10
    assert extended_count == (471,)


def test_provider_attempt_http_errors(tmp_path: Path, postgres_dsn: str) -> None:
    store, attempt_id, _capture_id = _prepare_pf03(
        tmp_path, postgres_dsn, extended=False, select=False
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, TEST_RECIPE)
        register_provider_recipe(connection, EXTENDED_RECIPE)
    with _app(store, postgres_dsn) as client:
        missing_selection = client.get(f"/v1/attempts/{attempt_id}")
        unselected_history = _history(client, "ai search optimization")
        unknown = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={'ab' * 32}"
        )
        wrong = client.get(
            f"/v1/attempts/{attempt_id}?derivation_version_id={TEST_RECIPE_ID}"
        )
    assert missing_selection.status_code == 503
    assert missing_selection.json()["detail"] == NOT_SELECTED_SIGNAL
    assert unselected_history.status_code == 503
    assert unselected_history.json()["detail"] == NOT_SELECTED_SIGNAL
    assert unknown.status_code == 404
    assert wrong.status_code == 404
    with connect(postgres_dsn) as connection:
        select_provider_recipe(connection, store_adapter(), CORE_RECIPE_ID)
    with _app(store, postgres_dsn) as client:
        empty = _history(client, "not-a-requested-keyword")
        only_core = _history(
            client, "ai search optimization", derivation_version_id=EXTENDED_RECIPE_ID
        )
    assert empty.status_code == 200
    assert empty.json()["captures"] == []
    assert empty.json()["derivation_version_id"] == CORE_RECIPE_ID
    assert only_core.status_code == 200
    assert only_core.json()["captures"] == []
    assert only_core.json()["derivation_version_id"] == EXTENDED_RECIPE_ID
    assert only_core.json()["observation_kinds"] == [
        COVERAGE_KIND,
        METRICS_KIND,
        MONTHLY_KIND,
        TREND_KIND,
        PROPERTIES_KIND,
        BACKLINKS_KIND,
        INTENT_KIND,
    ]


def test_history_core_and_extended_shapes(tmp_path: Path, postgres_dsn: str) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        extended = _history(client, "ai search optimization")
        core = _history(
            client,
            "ai search optimization",
            derivation_version_id=CORE_RECIPE_ID,
        )
    assert extended.status_code == 200
    body = extended.json()
    assert body["provider"] == "dataforseo"
    assert body["adapter_contract"] == store_adapter()
    assert body["requested_keyword"] == "ai search optimization"
    assert body["derivation_version_id"] == EXTENDED_RECIPE_ID
    assert body["recipe_resolution"] == "selected"
    assert body["observation_kinds"] == [
        COVERAGE_KIND,
        METRICS_KIND,
        MONTHLY_KIND,
        TREND_KIND,
        PROPERTIES_KIND,
        BACKLINKS_KIND,
        INTENT_KIND,
    ]
    assert len(body["captures"]) == 1
    group = body["captures"][0]
    assert group["attempt_id"] == attempt_id
    assert group["capture_id"] == capture_id
    assert group["request"] == {
        "location_code": 2840,
        "language_code": "en",
        "include_serp_info": False,
        "include_clickstream_data": False,
    }
    assert group["coverage"]["observation_kind"] == COVERAGE_KIND
    assert group["metrics"]["observation_kind"] == METRICS_KIND
    assert group["capture_outcome"]["observation_count"] == 471
    assert len(group["monthly_search_volume"]) == 85
    assert group["capture_outcome"]["observation_count"] != len(
        group["monthly_search_volume"]
    )
    assert group["search_volume_trend"]["observation_kind"] == TREND_KIND
    assert group["properties"]["observation_kind"] == PROPERTIES_KIND
    assert group["avg_backlinks"]["observation_kind"] == BACKLINKS_KIND
    assert group["search_intent"]["observation_kind"] == INTENT_KIND
    assert "score" not in group
    assert "value" not in group
    core_body = core.json()
    assert core.status_code == 200
    assert core_body["derivation_version_id"] == CORE_RECIPE_ID
    assert core_body["recipe_resolution"] == "pinned"
    assert core_body["observation_kinds"] == [COVERAGE_KIND, METRICS_KIND]
    core_group = core_body["captures"][0]
    assert "monthly_search_volume" not in core_group
    assert "search_volume_trend" not in core_group
    assert "properties" not in core_group
    assert "avg_backlinks" not in core_group
    assert "search_intent" not in core_group
    assert core_group["metrics"] is not None
    assert core_group["capture_outcome"]["observation_count"] == 10


def test_history_ignores_foreign_attempt_outcome_for_same_capture(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    foreign_attempt = "ab" * 32
    assert foreign_attempt != attempt_id
    with connect(postgres_dsn) as connection:
        valid = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE attempt_id = %s AND capture_id = %s
              AND derivation_version_id = %s
            """,
            (attempt_id, capture_id, EXTENDED_RECIPE_ID),
        ).fetchone()
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (foreign_attempt, capture_id, EXTENDED_RECIPE_ID, "provider_error", 0),
        )
    assert valid == ("observation_admitted", 471)
    with _app(store, postgres_dsn) as client:
        response = _history(client, "ai search optimization")
    assert response.status_code == 200
    captures = response.json()["captures"]
    assert [item["capture_id"] for item in captures] == [capture_id]
    assert captures[0]["attempt_id"] == attempt_id
    assert captures[0]["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": 471,
    }
    assert all(item["attempt_id"] != foreign_attempt for item in captures)
    assert all(
        item["capture_outcome"]["classification"] != "provider_error"
        for item in captures
    )


def test_historical_revision_is_visible_through_history_api(
    tmp_path: Path, postgres_dsn: str
) -> None:
    original = _body()
    document = _decoded(original)
    target = next(
        item
        for item in document["tasks"][0]["result"][0]["items"]
        if item["keyword"] == "ai search optimization"
    )
    point = next(
        item
        for item in target["keyword_info"]["monthly_searches"]
        if item["year"] == 2019 and item["month"] == 6
    )
    assert point["search_volume"] == 0
    point["search_volume"] = 7
    store = create_store(tmp_path / "evidence")
    first_attempt, first_capture = _commit_paid(
        store,
        original,
        "31" * 32,
        started="2026-08-16T21:37:01.100000Z",
        authorized_at="2026-08-16T21:37:00.000000Z",
    )
    later_attempt, later_capture = _commit_paid(
        store,
        _encode(document),
        "32" * 32,
        started="2026-08-16T21:38:01.100000Z",
        authorized_at="2026-08-16T21:38:00.000000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
    expected_identity = observation_identity(
        {
            "axes": {
                "requested_keyword": "ai search optimization",
                "year": 2019,
                "month": 6,
            },
            "observation_kind": MONTHLY_KIND,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        EXTENDED_RECIPE,
    )
    with _app(store, postgres_dsn) as client:
        ascending = _history(client, "ai search optimization", order="asc")
        descending = _history(client, "ai search optimization", order="desc", limit=2)
        limited = _history(client, "ai search optimization", order="asc", limit=1)
    assert ascending.status_code == 200
    captures = ascending.json()["captures"]
    assert [item["capture_id"] for item in captures] == [first_capture, later_capture]
    assert [item["attempt_id"] for item in captures] == [first_attempt, later_attempt]
    assert captures[0]["request_started_at"] < captures[1]["request_started_at"]
    first_month = next(
        item
        for item in captures[0]["monthly_search_volume"]
        if item["data_period"] == {"year": 2019, "month": 6}
    )
    later_month = next(
        item
        for item in captures[1]["monthly_search_volume"]
        if item["data_period"] == {"year": 2019, "month": 6}
    )
    assert first_month["search_volume"] == {"state": "stated", "value": 0}
    assert later_month["search_volume"] == {"state": "stated", "value": 7}
    assert first_month["within_capture_identity"] == later_month["within_capture_identity"]
    assert first_month["within_capture_identity"] == expected_identity
    assert first_month["data_period"] != captures[0]["request_started_at"]
    assert descending.json()["captures"][0]["capture_id"] == later_capture
    assert descending.json()["captures"][1]["capture_id"] == first_capture
    assert [item["capture_id"] for item in limited.json()["captures"]] == [first_capture]
    assert len(limited.json()["captures"][0]["monthly_search_volume"]) == 85


def test_field_states_clocks_and_decimals(tmp_path: Path, postgres_dsn: str) -> None:
    document = _decoded()
    items = document["tasks"][0]["result"][0]["items"]
    seo = next(item for item in items if item["keyword"] == "seo api")
    seo["keyword_info"]["categories"] = []
    ai_item = next(item for item in items if item["keyword"] == "ai search optimization")
    ai_item["keyword_info"]["cpc"] = Decimal("1.234567890123456789")
    omitted = copy.deepcopy(document)
    omitted["tasks"][0]["result"][0]["items"] = [
        item for item in items if item["keyword"] != "local seo"
    ]
    omitted["tasks"][0]["result"][0]["items_count"] = 4
    store = create_store(tmp_path / "states")
    _commit_paid(
        store,
        _encode(document),
        "41" * 32,
        started="2026-08-16T21:37:01.100000Z",
    )
    _commit_paid(
        store,
        _encode(omitted),
        "42" * 32,
        started="2026-08-16T21:37:02.100000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
    with _app(store, postgres_dsn) as client:
        ai = _history(client, "ai search optimization", limit=1, order="asc").json()[
            "captures"
        ][0]
        seo_api = _history(client, "seo api", limit=1, order="asc").json()["captures"][0]
        research = _history(client, "keyword research", limit=1, order="asc").json()[
            "captures"
        ][0]
        local = _history(client, "local seo", order="desc").json()["captures"]
    month = next(
        item
        for item in ai["monthly_search_volume"]
        if item["data_period"] == {"year": 2019, "month": 6}
    )
    assert month["search_volume"] == {"state": "stated", "value": 0}
    assert ai["metrics"]["search_partners"] == {"state": "stated", "value": False}
    assert seo_api["metrics"]["categories"] == {"state": "stated", "value": []}
    assert seo_api["properties"]["core_keyword"] == {"state": "json_null", "value": None}
    absent = local[0]
    assert absent["coverage"]["covered"] is False
    assert absent["coverage"]["returned_keyword"] == {"state": "absent", "value": None}
    assert absent["metrics"] is None
    assert "provider_update_time" not in month
    assert "provider_update_time" not in ai["search_volume_trend"]
    assert "provider_update_time" not in ai["properties"]
    assert ai["metrics"]["provider_update_time"]["value"] == "2026-07-16 07:54:24 +00:00"
    assert ai["avg_backlinks"]["provider_update_time"]["value"] == (
        "2026-08-01 07:28:00 +00:00"
    )
    assert ai["search_intent"]["provider_update_time"]["value"] == (
        "2026-04-29 01:54:23 +00:00"
    )
    assert ai["metrics"]["provider_update_time"] != ai["avg_backlinks"]["provider_update_time"]
    assert ai["metrics"]["provider_update_time"] != ai["search_intent"]["provider_update_time"]
    assert (
        ai["avg_backlinks"]["provider_update_time"]
        != ai["search_intent"]["provider_update_time"]
    )
    assert ai["avg_backlinks"]["backlinks"] == {"state": "stated", "value": "1571.3"}
    assert research["search_intent"]["foreign_intent"]["state"] == "json_null"
    assert ai["metrics"]["cpc"] == {
        "state": "stated",
        "value": "1.234567890123456789",
    }
    assert ai["metrics"]["cpc"]["value"] != str(float("1.234567890123456789"))


def test_provider_damage_returns_409(tmp_path: Path, postgres_dsn: str) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    attempt = store.read_attempt(attempt_id)
    assert attempt is not None
    fingerprint = attempt["request_fingerprint"]
    authorized_at = attempt["authorized_at"]
    assert isinstance(fingerprint, str)
    assert isinstance(authorized_at, str)

    def assert_409(client: TestClient) -> None:
        history = _history(client, "ai search optimization")
        resource = client.get(f"/v1/attempts/{attempt_id}")
        assert history.status_code == 409
        assert "evidence_integrity_failure" in history.text
        assert "captures" not in history.json()
        assert resource.status_code == 409
        assert "evidence_integrity_failure" in resource.text
        assert "capture_outcome" not in resource.json()

    body_path = store.capture_path(capture_id) / "response.body"
    payload = bytearray(body_path.read_bytes())
    payload[0] ^= 0x01
    body_path.write_bytes(bytes(payload))
    with _app(store, postgres_dsn) as client:
        assert_409(client)
    body_path.write_bytes(bytes(bytearray(payload[0] ^ 0x01) + payload[1:]))

    manifest = store.capture_path(capture_id) / "capture.json"
    raw = bytearray(manifest.read_bytes())
    raw[0] ^= 0x01
    manifest.write_bytes(bytes(raw))
    with _app(store, postgres_dsn) as client:
        assert_409(client)
    manifest.write_bytes(bytes(bytearray(raw[0] ^ 0x01) + raw[1:]))

    attempt_manifest = (
        store.attempt_path(fingerprint, authorized_at, attempt_id) / "attempt.json"
    )
    attempt_raw = bytearray(attempt_manifest.read_bytes())
    attempt_raw[0] ^= 0x01
    attempt_manifest.write_bytes(bytes(attempt_raw))
    with _app(store, postgres_dsn) as client:
        resource = client.get(f"/v1/attempts/{attempt_id}")
        history = _history(client, "ai search optimization")
    assert resource.status_code == 409
    assert "evidence_integrity_failure" in resource.text
    assert history.status_code == 409
    assert "captures" not in history.json()
    attempt_manifest.write_bytes(bytes(bytearray(attempt_raw[0] ^ 0x01) + attempt_raw[1:]))
    committed = store.attempt_path(fingerprint, authorized_at, attempt_id) / "COMMITTED"
    committed.unlink()
    with _app(store, postgres_dsn) as client:
        missing = client.get(f"/v1/attempts/{attempt_id}")
        missing_history = _history(client, "ai search optimization")
    assert missing.status_code == 409
    assert "evidence_integrity_failure" in missing.text
    assert missing_history.status_code == 409
    assert "captures" not in missing_history.json()


def test_api_reads_do_not_mutate_provider_state(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, _capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    before_ops = list(store.recorded_ops)
    before_pg = _xmin_snapshot(postgres_dsn)
    with _app(store, postgres_dsn) as client:
        assert client.get(f"/v1/attempts/{attempt_id}").status_code == 200
        assert _history(client, "ai search optimization").status_code == 200
    assert store.recorded_ops == before_ops
    assert _xmin_snapshot(postgres_dsn) == before_pg


def test_two_databases_return_equal_history(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_paid(store, _body(), "51" * 32, started="2026-08-16T21:37:01.100000Z")
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)
    for dsn in (postgres_dsn, postgres_second_dsn):
        with connect(dsn) as connection:
            derive_keyword_overview_extended(store, connection)
            select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
    with (
        _app(store, postgres_dsn) as left,
        _app(store, postgres_second_dsn) as right,
    ):
        left_body = _history(left, "keyword research")
        right_body = _history(right, "keyword research")
    assert left_body.status_code == 200
    assert right_body.status_code == 200
    assert left_body.json() == right_body.json()


def test_selector_isolation_does_not_leak(tmp_path: Path, postgres_dsn: str) -> None:
    store, attempt_id, _capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    other = str(TEST_RECIPE["adapter_contract"])
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, TEST_RECIPE)
        select_provider_recipe(connection, other, TEST_RECIPE_ID)
    with _app(store, postgres_dsn) as client:
        body = client.get(f"/v1/attempts/{attempt_id}").json()
        history = _history(client, "seo api").json()
    assert body["derivation_version_id"] == EXTENDED_RECIPE_ID
    assert history["derivation_version_id"] == EXTENDED_RECIPE_ID
    with connect(postgres_dsn) as connection:
        other_current = connection.execute(
            """
            SELECT derivation_version_id
            FROM provider_recipe_selections
            WHERE adapter_contract = %s
            """,
            (other,),
        ).fetchone()
    assert other_current == (TEST_RECIPE_ID,)


def test_history_excludes_non_admitted_sibling_and_keeps_healthy_capture(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    healthy_attempt, healthy_capture = _commit_paid(
        store, _body(), "61" * 32, started="2026-08-16T21:37:01.100000Z"
    )
    planted_attempt, planted_capture = _commit_paid(
        store, _body(), "62" * 32, started="2026-08-16T21:38:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
        connection.execute(
            """
            UPDATE outcomes
            SET classification = 'provider_error'
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (planted_capture, EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        response = _history(client, "ai search optimization")
    assert response.status_code == 200
    captures = response.json()["captures"]
    assert [item["capture_id"] for item in captures] == [healthy_capture]
    assert captures[0]["attempt_id"] == healthy_attempt
    assert captures[0]["capture_outcome"]["classification"] == "observation_admitted"
    assert planted_attempt not in {item["attempt_id"] for item in captures}


def test_history_missing_typed_row_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        deleted = connection.execute(
            """
            DELETE FROM keyword_overview_metrics
            WHERE capture_id = %s AND derivation_version_id = %s
              AND requested_keyword = 'seo api'
            RETURNING within_capture_identity
            """,
            (capture_id, EXTENDED_RECIPE_ID),
        ).fetchone()
        assert deleted is not None
    before_ops = list(store.recorded_ops)
    before_pg = _xmin_snapshot(postgres_dsn)
    with _app(store, postgres_dsn) as client:
        missing = _history(client, "keyword research")
        attempt = client.get(f"/v1/attempts/{attempt_id}")
    assert missing.status_code == 409
    assert missing.json()["detail"] == INTEGRITY_SIGNAL
    assert "captures" not in missing.json()
    assert attempt.status_code == 200
    assert attempt.json()["capture_outcome"]["observation_count"] == 471
    assert store.recorded_ops == before_ops
    assert _xmin_snapshot(postgres_dsn) == before_pg


def test_history_wrong_outcome_count_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare_pf03(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE outcomes
            SET observation_count = observation_count + 1
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, EXTENDED_RECIPE_ID),
        )
    before_ops = list(store.recorded_ops)
    before_pg = _xmin_snapshot(postgres_dsn)
    with _app(store, postgres_dsn) as client:
        wrong_count = _history(client, "keyword research")
        attempt = client.get(f"/v1/attempts/{attempt_id}")
    assert wrong_count.status_code == 409
    assert wrong_count.json()["detail"] == INTEGRITY_SIGNAL
    assert attempt.status_code == 200
    assert attempt.json()["capture_outcome"]["observation_count"] == 472
    assert store.recorded_ops == before_ops
    assert _xmin_snapshot(postgres_dsn) == before_pg


def test_history_consistency_damage_outside_limit_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_paid(store, _body(), "81" * 32, started="2026-08-16T21:37:01.100000Z")
    later_attempt, later_capture = _commit_paid(
        store, _body(), "82" * 32, started="2026-08-16T21:38:01.100000Z"
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview_extended(store, connection)
        select_provider_recipe(connection, store_adapter(), EXTENDED_RECIPE_ID)
        connection.execute(
            """
            DELETE FROM keyword_overview_metrics
            WHERE capture_id = %s AND derivation_version_id = %s
              AND requested_keyword = 'seo api'
            """,
            (later_capture, EXTENDED_RECIPE_ID),
        )
    with _app(store, postgres_dsn) as client:
        limited = _history(client, "keyword research", limit=1, order="asc")
        later = client.get(f"/v1/attempts/{later_attempt}")
    assert limited.status_code == 409
    assert limited.json()["detail"] == INTEGRITY_SIGNAL
    assert "captures" not in limited.json()
    assert later.status_code == 200
