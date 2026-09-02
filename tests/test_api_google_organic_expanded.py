"""PF-18: expanded Google Organic read API, integrity, and OpenAPI documentation.

Every proof here is zero-network. An API-only consumer must be able to answer the
four MVP questions without direct PostgreSQL or Evidence access, and pinned v1 must
keep returning exactly the accepted v1 document.
"""

from __future__ import annotations

import copy
import json
import socket
from collections import Counter
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from observatory import google_organic_read
from observatory.api import create_app
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
    GOOGLE_ORGANIC_EXPANDED_RECIPE_ID,
    GOOGLE_ORGANIC_RECIPE_ID,
    ORGANIC_PLACEMENT_KIND,
    ORGANIC_PLACEMENT_V2_KIND,
    ORGANIC_SITELINK_KIND,
    RELATED_QUERY_KIND,
    RELATED_QUESTION_KIND,
    TOP_STORY_RESULT_KIND,
    VIDEO_RESULT_KIND,
)
from observatory.dataforseo_google_organic_paid_probe import (
    closed_organic_parameters,
    organic_request_body_bytes,
)
from observatory.derive import DEFAULT_VERSION
from observatory.evidence_store import EvidenceStore, create_store
from observatory.google_organic_derive import (
    derive_google_organic,
    derive_google_organic_expanded,
)
from observatory.google_organic_read import (
    GoogleOrganicItemTimestamp,
    GoogleOrganicLinksFamily,
    GoogleOrganicOrdinaryTextField,
    GoogleOrganicTextField,
)
from observatory.migrate import apply_migrations, connect
from observatory.provider_recipe_selection import select_provider_recipe
from observatory.settings import Settings

FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_google_organic_pf10.json"
)
KEYWORD = "conspiracy theories"
HISTORY = "/v1/providers/dataforseo/google/organic/history"
OPENAPI = "/api/v1/openapi.json"
WIKI_URL = "https://en.wikipedia.org/wiki/Conspiracy_theory"
CLARION_URL = (
    "https://www.clarionledger.com/story/entertainment/2026/08/18/"
    "conspiracy-theories-are-debunked-in-history-of-huey-longs-assassination/"
    "91286800007/"
)

EXPANDED_KINDS = [
    FEATURE_PRESENCE_KIND,
    ORGANIC_PLACEMENT_V2_KIND,
    AIO_PRESENCE_KIND,
    AIO_SOURCE_KIND,
    RELATED_QUESTION_KIND,
    RELATED_QUERY_KIND,
    TOP_STORY_RESULT_KIND,
    VIDEO_RESULT_KIND,
    ORGANIC_SITELINK_KIND,
]
V1_CAPTURE_KEYS = {
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
EXPANDED_CAPTURE_KEYS = V1_CAPTURE_KEYS | {
    "top_story_results",
    "video_results",
    "sitelinks",
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


def _first(document: dict[str, Any], item_type: str) -> dict[str, Any]:
    for item in _items(document):
        if item["type"] == item_type:
            assert isinstance(item, dict)
            return item
    raise AssertionError(f"no {item_type} item in the fixture")


def _commit_organic(
    store: EvidenceStore,
    body: bytes,
    nonce: str,
    *,
    started: str,
    authorized_at: str = "2026-08-18T17:37:00.000000Z",
) -> tuple[str, str]:
    parameters = closed_organic_parameters(keyword=KEYWORD)
    attempt = organic_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at=authorized_at,
        observatory_version="pf18-api-test-v1",
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


def _app(store: EvidenceStore, dsn: str) -> TestClient:
    settings = Settings(
        environment="test",
        database_url=dsn,
        evidence_root=store.root,
        derivation_version_id=DEFAULT_VERSION,
    )
    return TestClient(create_app(settings, store=store))


def _history(client: TestClient, **params: object) -> Any:
    query = {"requested_keyword": KEYWORD, **params}
    return client.get(HISTORY + "?" + urlencode(query, doseq=True))


def _prepare(
    tmp_path: Path,
    dsn: str,
    *,
    body: bytes | None = None,
    select_expanded: bool = True,
) -> tuple[EvidenceStore, str, str]:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit_organic(
        store, body or _body(), "71" * 32, started="2026-08-18T17:37:01.100000Z"
    )
    apply_migrations(dsn)
    with connect(dsn) as connection:
        derive_google_organic(store, connection)
        derive_google_organic_expanded(store, connection)
        select_provider_recipe(
            connection,
            ORGANIC_ADAPTER_CONTRACT,
            GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
            if select_expanded
            else GOOGLE_ORGANIC_RECIPE_ID,
        )
        connection.commit()
    return store, attempt_id, capture_id


def _assert_409(response: Any) -> None:
    assert response.status_code == 409
    assert response.json() == {"detail": "evidence_integrity_failure"}
    assert "captures" not in response.json()


def _capture(response: Any) -> dict[str, Any]:
    body = response.json()
    captures = body["captures"]
    assert isinstance(captures, list)
    assert len(captures) == 1
    first = captures[0]
    assert isinstance(first, dict)
    return first


# --------------------------------------------------------------------------------------
# The four MVP consumer questions, answered from the API alone
# --------------------------------------------------------------------------------------


def test_expanded_history_answers_the_four_mvp_questions(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, attempt_id, capture_id = _prepare(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    assert response.status_code == 200
    body = response.json()
    assert body["derivation_version_id"] == GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
    assert body["recipe_resolution"] == "selected"
    assert body["observation_kinds"] == EXPANDED_KINDS
    assert body["total_matching"] == 1
    assert body["returned_count"] == 1
    assert body["has_more"] is False
    capture = _capture(response)
    assert set(capture) == EXPANDED_CAPTURE_KEYS
    assert capture["attempt_id"] == attempt_id
    assert capture["capture_id"] == capture_id
    assert capture["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": 248,
    }

    # 1. Which Top Stories children, with source/domain/title/URL/item timestamp?
    stories = capture["top_story_results"]
    assert len(stories) == 4
    for row in stories:
        assert row["observation_kind"] == TOP_STORY_RESULT_KIND
        assert (
            row["parent_page"],
            row["parent_position"],
            row["parent_rank_group"],
            row["parent_rank_absolute"],
        ) == (1, "left", 1, 6)
        assert row["source"]
        assert row["domain"]
        assert row["title"]
        assert row["child_url"].startswith("https://")
        assert row["top_story_item_timestamp"]["state"] == "stated"
        assert len(row["occurrences"]) == 1
    assert sorted(row["occurrences"][0]["child_index"] for row in stories) == [0, 1, 2, 3]
    clarion = next(row for row in stories if row["child_url"] == CLARION_URL)
    assert clarion["source"] == "The Clarion-Ledger"
    assert clarion["domain"] == "www.clarionledger.com"
    assert clarion["top_story_item_timestamp"]["value"] == "2026-08-18 09:37:26 +00:00"

    # 2. Which Video children, with source/title/URL/item timestamp and no invented domain?
    videos = capture["video_results"]
    assert len(videos) == 3
    for row in videos:
        assert row["observation_kind"] == VIDEO_RESULT_KIND
        assert (
            row["parent_page"],
            row["parent_position"],
            row["parent_rank_group"],
            row["parent_rank_absolute"],
        ) == (1, "left", 1, 7)
        assert "domain" not in row
        assert row["video_item_timestamp"]["state"] == "stated"
        assert len(row["occurrences"]) == 1
    assert any(row["source"] == "Facebook · Josh Johnson" for row in videos)

    # 3. Which organic placements stated an item timestamp, and what exactly?
    ranked = capture["ranked_results"]
    assert len(ranked) == 97
    assert all(row["observation_kind"] == ORGANIC_PLACEMENT_V2_KIND for row in ranked)
    states = Counter(row["organic_item_timestamp"]["state"] for row in ranked)
    assert states == Counter({"stated": 58, "json_null": 39})
    assert states["absent"] == 0
    assert all(
        row["organic_item_timestamp"]["value"] is None
        for row in ranked
        if row["organic_item_timestamp"]["state"] != "stated"
    )

    # 4. Which sitelinks, under which exact organic placement, with what testimony?
    sitelinks = capture["sitelinks"]
    assert len(sitelinks) == 4
    for row in sitelinks:
        assert row["observation_kind"] == ORGANIC_SITELINK_KIND
        assert (
            row["parent_page"],
            row["parent_position"],
            row["parent_rank_group"],
            row["parent_rank_absolute"],
        ) == (1, "left", 1, 2)
        assert row["domain"] == "en.wikipedia.org"
        assert row["description"] == {"state": "json_null", "value": None}
        assert len(row["occurrences"]) == 1
    assert sorted(row["occurrences"][0]["child_index"] for row in sitelinks) == [
        0,
        1,
        2,
        3,
    ]
    parent = next(row for row in ranked if row["rank_absolute"] == 2)
    assert parent["url"] == WIKI_URL
    assert parent["links"] == {"state": "stated", "returned_child_count": 4}
    assert all(
        row["parent_within_capture_identity"] == parent["within_capture_identity"]
        for row in sitelinks
    )


def test_links_family_state_is_visible_without_any_child_rows(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    ranks = [
        item["rank_absolute"]
        for item in _items(document)
        if item["type"] == "organic" and item.get("links") is None
    ]
    del next(
        item
        for item in _items(document)
        if item["type"] == "organic" and item["rank_absolute"] == ranks[0]
    )["links"]
    next(
        item
        for item in _items(document)
        if item["type"] == "organic" and item["rank_absolute"] == ranks[1]
    )["links"] = []
    store, _attempt, _capture_id = _prepare(
        tmp_path, postgres_dsn, body=_encode(document)
    )
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    capture = _capture(response)
    by_rank = {row["rank_absolute"]: row for row in capture["ranked_results"]}
    assert by_rank[ranks[0]]["links"] == {"state": "absent", "returned_child_count": None}
    assert by_rank[ranks[1]]["links"] == {"state": "stated", "returned_child_count": 0}
    assert by_rank[ranks[2]]["links"] == {
        "state": "json_null",
        "returned_child_count": None,
    }
    assert by_rank[2]["links"] == {"state": "stated", "returned_child_count": 4}
    # Three different parent families, all with zero sitelink rows.
    assert len(capture["sitelinks"]) == 4
    assert all(row["parent_rank_absolute"] == 2 for row in capture["sitelinks"])


def test_expanded_history_exposes_duplicate_occurrences_not_duplicate_facts(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    stories = _first(document, "top_stories")
    stories["items"].append(copy.deepcopy(stories["items"][0]))
    store, _attempt, _capture_id = _prepare(
        tmp_path, postgres_dsn, body=_encode(document)
    )
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    capture = _capture(response)
    assert capture["capture_outcome"]["observation_count"] == 248
    assert len(capture["top_story_results"]) == 4
    repeated = next(
        row for row in capture["top_story_results"] if row["child_url"] == CLARION_URL
    )
    assert sorted(item["child_index"] for item in repeated["occurrences"]) == [0, 4]


def test_a_second_parent_scopes_children_independently_over_the_api(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    stories = _first(document, "top_stories")
    clone = copy.deepcopy(stories)
    clone["position"] = "right"
    clone["rank_group"] = 1
    clone["rank_absolute"] = 1
    clone["items"] = [copy.deepcopy(stories["items"][0])]
    videos = _first(document, "video")
    video_clone = copy.deepcopy(videos)
    video_clone["position"] = "right"
    video_clone["rank_group"] = 1
    video_clone["rank_absolute"] = 2
    video_clone["items"] = [copy.deepcopy(videos["items"][0])]
    _set_items(document, [*_items(document), clone, video_clone])
    store, _attempt, _capture_id = _prepare(
        tmp_path, postgres_dsn, body=_encode(document)
    )
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    capture = _capture(response)
    stories_rows = capture["top_story_results"]
    assert len(stories_rows) == 5
    repeated = [row for row in stories_rows if row["child_url"] == CLARION_URL]
    assert len(repeated) == 2
    assert {row["parent_position"] for row in repeated} == {"left", "right"}
    assert len({row["within_capture_identity"] for row in repeated}) == 2
    assert len({row["parent_within_capture_identity"] for row in repeated}) == 2
    video_rows = capture["video_results"]
    assert len(video_rows) == 4
    assert {row["parent_position"] for row in video_rows} == {"left", "right"}
    # Two more feature placements, two more semantic children, no occurrence inflation.
    assert capture["capture_outcome"]["observation_count"] == 248 + 2 + 1 + 1


def test_the_same_url_across_kinds_stays_two_facts_over_the_api(
    tmp_path: Path, postgres_dsn: str
) -> None:
    document = _decoded()
    _first(document, "top_stories")["items"][0]["url"] = WIKI_URL
    store, _attempt, _capture_id = _prepare(
        tmp_path, postgres_dsn, body=_encode(document)
    )
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    capture = _capture(response)
    story = next(
        row for row in capture["top_story_results"] if row["child_url"] == WIKI_URL
    )
    ranked = next(row for row in capture["ranked_results"] if row["url"] == WIKI_URL)
    assert story["observation_kind"] != ranked["observation_kind"]
    assert story["within_capture_identity"] != ranked["within_capture_identity"]
    assert capture["capture_outcome"]["observation_count"] == 248


# --------------------------------------------------------------------------------------
# Pinned v1 versus selected expanded
# --------------------------------------------------------------------------------------


def test_pinned_v1_history_is_unchanged_while_expanded_is_selected(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt, _capture_id = _prepare(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        expanded = _history(client)
        pinned = _history(client, derivation_version_id=GOOGLE_ORGANIC_RECIPE_ID)
    assert expanded.status_code == 200
    assert pinned.status_code == 200
    pinned_body = pinned.json()
    assert pinned_body["derivation_version_id"] == GOOGLE_ORGANIC_RECIPE_ID
    assert pinned_body["recipe_resolution"] == "pinned"
    assert pinned_body["observation_kinds"] == [
        FEATURE_PRESENCE_KIND,
        ORGANIC_PLACEMENT_KIND,
        AIO_PRESENCE_KIND,
        AIO_SOURCE_KIND,
        RELATED_QUESTION_KIND,
        RELATED_QUERY_KIND,
    ]
    pinned_capture = _capture(pinned)
    assert set(pinned_capture) == V1_CAPTURE_KEYS
    assert pinned_capture["capture_outcome"] == {
        "classification": "observation_admitted",
        "observation_count": 237,
    }
    ranked = pinned_capture["ranked_results"]
    assert len(ranked) == 97
    assert all(row["observation_kind"] == ORGANIC_PLACEMENT_KIND for row in ranked)
    assert all("organic_item_timestamp" not in row for row in ranked)
    assert all("links" not in row for row in ranked)
    assert set(ranked[0]) == {
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
    # The expanded document and the pinned v1 document differ only as designed.
    expanded_capture = _capture(expanded)
    assert expanded_capture["serp_features"] == pinned_capture["serp_features"]
    assert expanded_capture["related_queries"] == pinned_capture["related_queries"]
    assert expanded_capture["result_context"] == pinned_capture["result_context"]


def test_pinning_the_expanded_recipe_while_v1_is_selected_also_works(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt, _capture_id = _prepare(
        tmp_path, postgres_dsn, select_expanded=False
    )
    with _app(store, postgres_dsn) as client:
        selected = _history(client)
        pinned = _history(client, derivation_version_id=GOOGLE_ORGANIC_EXPANDED_RECIPE_ID)
    assert selected.json()["derivation_version_id"] == GOOGLE_ORGANIC_RECIPE_ID
    assert set(_capture(selected)) == V1_CAPTURE_KEYS
    assert pinned.json()["recipe_resolution"] == "pinned"
    assert set(_capture(pinned)) == EXPANDED_CAPTURE_KEYS
    assert _capture(pinned)["capture_outcome"]["observation_count"] == 248


# --------------------------------------------------------------------------------------
# Read-side integrity
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "table",
    (
        "google_organic_top_story_result_occurrences",
        "google_organic_video_result_occurrences",
        "google_organic_sitelink_occurrences",
    ),
)
def test_a_semantic_child_without_occurrences_is_409(
    tmp_path: Path, postgres_dsn: str, table: str
) -> None:
    store, _attempt, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            f"DELETE FROM {table} WHERE capture_id = %s AND derivation_version_id = %s",
            (capture_id, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID),
        )
        connection.commit()
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    _assert_409(response)


@pytest.mark.parametrize(
    ("table", "occurrence_table"),
    (
        ("google_organic_top_story_results", "google_organic_top_story_result_occurrences"),
        ("google_organic_video_results", "google_organic_video_result_occurrences"),
        ("google_organic_sitelinks", "google_organic_sitelink_occurrences"),
    ),
)
def test_a_missing_typed_child_row_is_409(
    tmp_path: Path, postgres_dsn: str, table: str, occurrence_table: str
) -> None:
    store, _attempt, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        victim = connection.execute(
            f"""
            SELECT within_capture_identity FROM {table}
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY within_capture_identity LIMIT 1
            """,
            (capture_id, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID),
        ).fetchone()
        assert victim is not None
        connection.execute(
            f"DELETE FROM {occurrence_table} WHERE within_capture_identity = %s",
            (victim[0],),
        )
        connection.execute(
            f"DELETE FROM {table} WHERE within_capture_identity = %s", (victim[0],)
        )
        connection.commit()
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    _assert_409(response)


def test_a_missing_ranked_v2_row_is_409(tmp_path: Path, postgres_dsn: str) -> None:
    store, _attempt, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        # Drop a placement that carries no sitelinks, so only the ranked-result row
        # goes missing and the failure cannot be blamed on a child family.
        connection.execute(
            """
            DELETE FROM google_organic_ranked_results_v2
            WHERE ctid IN (
                SELECT ctid FROM google_organic_ranked_results_v2
                WHERE capture_id = %s AND derivation_version_id = %s
                  AND links_state <> 'stated'
                LIMIT 1
            )
            """,
            (capture_id, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID),
        )
        connection.commit()
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    _assert_409(response)


def test_a_wrong_expanded_observation_count_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE outcomes SET observation_count = 247
            WHERE derivation_version_id = %s AND capture_id = %s
            """,
            (GOOGLE_ORGANIC_EXPANDED_RECIPE_ID, capture_id),
        )
        connection.commit()
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    _assert_409(response)


def test_expanded_damage_hidden_beyond_the_outer_limit_is_still_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_organic(store, _body(), "81" * 32, started="2026-08-18T17:37:01.100000Z")
    later_attempt, later_capture = _commit_organic(
        store,
        _body(),
        "82" * 32,
        started="2026-08-18T17:38:01.100000Z",
        authorized_at="2026-08-18T17:38:00.000000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic_expanded(store, connection)
        select_provider_recipe(
            connection, ORGANIC_ADAPTER_CONTRACT, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
        )
        connection.execute(
            """
            DELETE FROM google_organic_video_result_occurrences
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (later_capture, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID),
        )
        connection.commit()
    with _app(store, postgres_dsn) as client:
        limited = _history(client, limit=1, order="asc")
        unlimited = _history(client)
        attempt_audit = client.get(f"/v1/attempts/{later_attempt}")
    # The damaged Capture sorts second and would be hidden by limit=1; it still 409s.
    _assert_409(limited)
    _assert_409(unlimited)
    assert attempt_audit.status_code == 200


def test_undamaged_expanded_history_is_still_limitable(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_organic(store, _body(), "83" * 32, started="2026-08-18T17:37:01.100000Z")
    _commit_organic(
        store,
        _body(),
        "84" * 32,
        started="2026-08-18T17:38:01.100000Z",
        authorized_at="2026-08-18T17:38:00.000000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic_expanded(store, connection)
        select_provider_recipe(
            connection, ORGANIC_ADAPTER_CONTRACT, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
        )
        connection.commit()
    with _app(store, postgres_dsn) as client:
        limited = _history(client, limit=1, order="asc")
    assert limited.status_code == 200
    body = limited.json()
    assert body["total_matching"] == 2
    assert body["returned_count"] == 1
    assert body["has_more"] is True
    assert len(body["captures"][0]["top_story_results"]) == 4


CHILD_OCCURRENCE_FAMILIES = (
    (
        "google_organic_top_story_results",
        "google_organic_top_story_result_occurrences",
    ),
    ("google_organic_video_results", "google_organic_video_result_occurrences"),
    ("google_organic_sitelinks", "google_organic_sitelink_occurrences"),
)
IMPOSSIBLE_PF18_STATES = ("not_requested", "inapplicable")


def _insert_extra_occurrence(
    connection: Any, parent_table: str, occurrence_table: str, capture_id: str
) -> None:
    """Add one more FK-valid child_index under an existing semantic child.

    The parent exists, the envelope exists, the observation_kind agrees and the
    foreign key is satisfied, so nothing but complete-set agreement with verified
    Evidence can refuse this row.
    """

    inserted = connection.execute(
        f"""
        INSERT INTO {occurrence_table} (
            capture_id, derivation_version_id, within_capture_identity,
            observation_kind, child_index
        )
        SELECT capture_id, derivation_version_id, within_capture_identity,
               observation_kind, 99
        FROM {parent_table}
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY within_capture_identity
        LIMIT 1
        """,
        (capture_id, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID),
    ).rowcount
    assert inserted == 1


@pytest.mark.parametrize(("parent_table", "occurrence_table"), CHILD_OCCURRENCE_FAMILIES)
def test_an_extra_child_occurrence_under_a_real_parent_is_409(
    tmp_path: Path, postgres_dsn: str, parent_table: str, occurrence_table: str
) -> None:
    store, _attempt, capture_id = _prepare(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        assert _history(client).status_code == 200
    with connect(postgres_dsn) as connection:
        _insert_extra_occurrence(connection, parent_table, occurrence_table, capture_id)
        connection.commit()
    # Derivation is deliberately NOT rerun: the read path must refuse this on its own.
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    _assert_409(response)


def test_the_extra_occurrence_refusal_comes_from_evidence_reconstruction(
    tmp_path: Path, postgres_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Name the gate that actually refuses the row, so it cannot silently regress.

    The pre-existing envelope/typed-key and at-least-one-occurrence checks pass on a
    spurious extra child_index; only complete-set agreement with the verified Evidence
    body refuses it.
    """

    store, _attempt, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        _insert_extra_occurrence(
            connection,
            "google_organic_video_results",
            "google_organic_video_result_occurrences",
            capture_id,
        )
        connection.commit()
    monkeypatch.setattr(
        google_organic_read,
        "_assert_expanded_children_match_evidence",
        lambda *args, **kwargs: None,
    )
    with _app(store, postgres_dsn) as client:
        assert _history(client).status_code == 200
    monkeypatch.undo()
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_an_extra_child_occurrence_hidden_beyond_the_outer_limit_is_still_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_organic(store, _body(), "85" * 32, started="2026-08-18T17:37:01.100000Z")
    _later_attempt, later_capture = _commit_organic(
        store,
        _body(),
        "86" * 32,
        started="2026-08-18T17:38:01.100000Z",
        authorized_at="2026-08-18T17:38:00.000000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic_expanded(store, connection)
        select_provider_recipe(
            connection, ORGANIC_ADAPTER_CONTRACT, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
        )
        connection.commit()
        _insert_extra_occurrence(
            connection,
            "google_organic_sitelinks",
            "google_organic_sitelink_occurrences",
            later_capture,
        )
        connection.commit()
    with _app(store, postgres_dsn) as client:
        limited = _history(client, limit=1, order="asc")
        unlimited = _history(client)
    # The damaged Capture sorts second and limit=1 would hide it; it still 409s.
    _assert_409(limited)
    _assert_409(unlimited)


@pytest.mark.parametrize(("parent_table", "occurrence_table"), CHILD_OCCURRENCE_FAMILIES)
def test_a_duplicated_semantic_child_occurrence_index_is_409(
    tmp_path: Path, postgres_dsn: str, parent_table: str, occurrence_table: str
) -> None:
    """Moving a real occurrence onto another real semantic child is still damage."""

    store, _attempt, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        identities = connection.execute(
            f"""
            SELECT within_capture_identity FROM {parent_table}
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY within_capture_identity
            """,
            (capture_id, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID),
        ).fetchall()
        assert len(identities) >= 2
        connection.execute(
            f"""
            UPDATE {occurrence_table} SET within_capture_identity = %s
            WHERE within_capture_identity = %s
            """,
            (identities[0][0], identities[1][0]),
        )
        connection.commit()
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    _assert_409(response)


@pytest.mark.parametrize(
    ("table", "constraint", "column", "false_value"),
    (
        (
            "google_organic_top_story_results",
            "google_organic_top_story_results_parent_placement",
            "parent_page",
            2,
        ),
        (
            "google_organic_video_results",
            "google_organic_video_results_parent_placement",
            "parent_rank_absolute",
            99,
        ),
        (
            "google_organic_sitelinks",
            "google_organic_sitelinks_parent_placement",
            "parent_rank_group",
            2,
        ),
    ),
)
def test_a_falsified_parent_axis_is_409_even_without_the_database_constraint(
    tmp_path: Path,
    postgres_dsn: str,
    table: str,
    constraint: str,
    column: str,
    false_value: object,
) -> None:
    """Defence in depth for damage persisted before the composite key existed.

    PostgreSQL now refuses a false parent axis outright. Dropping that constraint
    simulates a database damaged under the previous schema, and proves the read path
    independently refuses to serve contradictory parent-placement testimony.
    """

    store, _attempt, _capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(f"ALTER TABLE {table} DROP CONSTRAINT {constraint}")
        connection.execute(f"UPDATE {table} SET {column} = %s", (false_value,))
        connection.commit()
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    _assert_409(response)


def test_a_falsified_child_content_field_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt, _capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            UPDATE google_organic_top_story_results
            SET source = 'Fabricated Wire Service'
            """
        )
        connection.commit()
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    _assert_409(response)


# --------------------------------------------------------------------------------------
# R4 — ranked_result.v2 rows must agree with verified Evidence
# --------------------------------------------------------------------------------------


def _damage_one_ranked_v2(
    dsn: str,
    capture_id: str,
    set_sql: str,
    *set_params: object,
    where_sql: str = "TRUE",
) -> None:
    """Mutate one otherwise-valid ranked-result-v2 row without rerunning Derivation."""

    with connect(dsn) as connection:
        updated = connection.execute(
            f"""
            UPDATE google_organic_ranked_results_v2
            SET {set_sql}
            WHERE ctid IN (
                SELECT ctid FROM google_organic_ranked_results_v2
                WHERE capture_id = %s AND derivation_version_id = %s
                  AND {where_sql}
                LIMIT 1
            )
            """,
            (*set_params, capture_id, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID),
        ).rowcount
        assert updated == 1
        connection.commit()


def test_ranked_v2_timestamp_state_to_state_damage_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    """json_null → absent is still a legal PF-18 state, but it is not Evidence."""

    store, _attempt, capture_id = _prepare(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        assert _history(client).status_code == 200
    _damage_one_ranked_v2(
        postgres_dsn,
        capture_id,
        "organic_item_timestamp_state = 'absent'",
        where_sql="organic_item_timestamp_state = 'json_null'",
    )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_ranked_v2_stated_timestamp_value_replacement_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt, capture_id = _prepare(tmp_path, postgres_dsn)
    _damage_one_ranked_v2(
        postgres_dsn,
        capture_id,
        "organic_item_timestamp = %s",
        "1999-01-01 00:00:00 +00:00",
        where_sql=(
            "organic_item_timestamp_state = 'stated' "
            "AND organic_item_timestamp <> '1999-01-01 00:00:00 +00:00'"
        ),
    )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_ranked_v2_links_family_damage_with_sitelinks_intact_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt, capture_id = _prepare(tmp_path, postgres_dsn)
    with connect(postgres_dsn) as connection:
        parent = connection.execute(
            """
            SELECT within_capture_identity, links_state, links_count
            FROM google_organic_ranked_results_v2
            WHERE capture_id = %s AND derivation_version_id = %s
              AND links_state = 'stated'
            """,
            (capture_id, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID),
        ).fetchone()
        assert parent is not None
        assert parent[1] == "stated"
        assert parent[2] == 4
        sitelinks_before = connection.execute(
            """
            SELECT COUNT(*) FROM google_organic_sitelinks
            WHERE capture_id = %s AND derivation_version_id = %s
              AND parent_within_capture_identity = %s
            """,
            (capture_id, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID, parent[0]),
        ).fetchone()
        assert sitelinks_before is not None
        assert sitelinks_before[0] == 4
        connection.execute(
            """
            UPDATE google_organic_ranked_results_v2
            SET links_state = 'json_null', links_count = NULL
            WHERE capture_id = %s AND derivation_version_id = %s
              AND within_capture_identity = %s
            """,
            (capture_id, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID, parent[0]),
        )
        sitelinks_after = connection.execute(
            """
            SELECT COUNT(*) FROM google_organic_sitelinks
            WHERE capture_id = %s AND derivation_version_id = %s
              AND parent_within_capture_identity = %s
            """,
            (capture_id, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID, parent[0]),
        ).fetchone()
        assert sitelinks_after is not None
        assert sitelinks_after[0] == 4
        connection.commit()
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_ranked_v2_served_content_damage_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt, capture_id = _prepare(tmp_path, postgres_dsn)
    _damage_one_ranked_v2(
        postgres_dsn,
        capture_id,
        "url = %s, title = %s",
        "https://example.invalid/ranked-v2-tamper",
        "Fabricated ranked-result title",
        where_sql="links_state <> 'stated'",
    )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_ranked_v2_placement_damage_without_sitelinks_is_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt, capture_id = _prepare(tmp_path, postgres_dsn)
    _damage_one_ranked_v2(
        postgres_dsn,
        capture_id,
        "rank_absolute = 999",
        where_sql="links_state <> 'stated'",
    )
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


def test_ranked_v2_damage_hidden_beyond_the_outer_limit_is_still_409(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit_organic(store, _body(), "87" * 32, started="2026-08-18T17:37:01.100000Z")
    _later_attempt, later_capture = _commit_organic(
        store,
        _body(),
        "88" * 32,
        started="2026-08-18T17:38:01.100000Z",
        authorized_at="2026-08-18T17:38:00.000000Z",
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic_expanded(store, connection)
        select_provider_recipe(
            connection, ORGANIC_ADAPTER_CONTRACT, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
        )
        connection.commit()
    _damage_one_ranked_v2(
        postgres_dsn,
        later_capture,
        "organic_item_timestamp_state = 'absent'",
        where_sql="organic_item_timestamp_state = 'json_null'",
    )
    with _app(store, postgres_dsn) as client:
        limited = _history(client, limit=1, order="asc")
        unlimited = _history(client)
    _assert_409(limited)
    _assert_409(unlimited)


def test_undamaged_expanded_history_still_serves_the_pf10_ranked_v2_document(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt, _capture_id = _prepare(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        response = _history(client)
    assert response.status_code == 200
    capture = _capture(response)
    assert capture["capture_outcome"]["observation_count"] == 248
    ranked = capture["ranked_results"]
    assert len(ranked) == 97
    assert all(row["observation_kind"] == ORGANIC_PLACEMENT_V2_KIND for row in ranked)
    timestamps = Counter(row["organic_item_timestamp"]["state"] for row in ranked)
    assert timestamps == Counter({"stated": 58, "json_null": 39})
    links = Counter(row["links"]["state"] for row in ranked)
    assert links == Counter({"json_null": 96, "stated": 1})
    populated = [row for row in ranked if row["links"]["state"] == "stated"]
    assert populated[0]["links"]["returned_child_count"] == 4
    assert len(capture["top_story_results"]) == 4
    assert len(capture["video_results"]) == 3
    assert len(capture["sitelinks"]) == 4


def test_pinned_v1_history_does_not_traverse_ranked_v2_evidence_comparison(
    tmp_path: Path, postgres_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, _attempt, _capture_id = _prepare(tmp_path, postgres_dsn)

    def boom(*_args: object, **_kwargs: object) -> None:
        raise AssertionError(
            "pinned v1 must not reconstruct expanded ranked-result-v2 Evidence"
        )

    monkeypatch.setattr(
        google_organic_read,
        "_assert_expanded_children_match_evidence",
        boom,
    )
    with _app(store, postgres_dsn) as client:
        pinned = _history(client, derivation_version_id=GOOGLE_ORGANIC_RECIPE_ID)
    assert pinned.status_code == 200
    pinned_capture = _capture(pinned)
    assert pinned_capture["capture_outcome"]["observation_count"] == 237
    assert all(
        row["observation_kind"] == ORGANIC_PLACEMENT_KIND
        for row in pinned_capture["ranked_results"]
    )
    assert all("organic_item_timestamp" not in row for row in pinned_capture["ranked_results"])
    assert all("links" not in row for row in pinned_capture["ranked_results"])


def test_ranked_v2_timestamp_refusal_comes_from_evidence_reconstruction(
    tmp_path: Path, postgres_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Name the gate: R3 still allows json_null → absent; only Evidence disagrees."""

    store, _attempt, capture_id = _prepare(tmp_path, postgres_dsn)
    _damage_one_ranked_v2(
        postgres_dsn,
        capture_id,
        "organic_item_timestamp_state = 'absent'",
        where_sql="organic_item_timestamp_state = 'json_null'",
    )
    monkeypatch.setattr(
        google_organic_read,
        "_assert_expanded_children_match_evidence",
        lambda *_args, **_kwargs: None,
    )
    with _app(store, postgres_dsn) as client:
        assert _history(client).status_code == 200
    monkeypatch.undo()
    with _app(store, postgres_dsn) as client:
        _assert_409(_history(client))


# --------------------------------------------------------------------------------------
# PF-18 ordinary field states are exactly stated | json_null | absent
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("impossible", IMPOSSIBLE_PF18_STATES)
def test_pf18_ordinary_models_refuse_impossible_field_states(impossible: str) -> None:
    with pytest.raises(ValidationError):
        GoogleOrganicItemTimestamp.model_validate({"state": impossible, "value": None})
    with pytest.raises(ValidationError):
        GoogleOrganicOrdinaryTextField.model_validate(
            {"state": impossible, "value": None}
        )
    with pytest.raises(ValidationError):
        GoogleOrganicLinksFamily.model_validate(
            {"state": impossible, "returned_child_count": None}
        )
    # The inherited v1 field model keeps its accepted five-token contract.
    assert (
        GoogleOrganicTextField.model_validate({"state": impossible, "value": None}).state
        == impossible
    )


@pytest.mark.parametrize("applicable", ("stated", "json_null", "absent"))
def test_pf18_ordinary_models_accept_their_three_applicable_states(
    applicable: str,
) -> None:
    value = "2026-08-18 09:37:26 +00:00" if applicable == "stated" else None
    assert (
        GoogleOrganicItemTimestamp.model_validate(
            {"state": applicable, "value": value}
        ).state
        == applicable
    )
    assert (
        GoogleOrganicOrdinaryTextField.model_validate(
            {"state": applicable, "value": value}
        ).state
        == applicable
    )
    assert (
        GoogleOrganicLinksFamily.model_validate(
            {
                "state": applicable,
                "returned_child_count": 0 if applicable == "stated" else None,
            }
        ).state
        == applicable
    )


def test_openapi_publishes_the_narrow_domain_only_for_pf18_ordinary_fields(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt, _capture_id = _prepare(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        schemas = _schemas(client)
    ordinary = ["stated", "json_null", "absent"]
    inherited = ordinary + ["not_requested", "inapplicable"]
    for model in (
        "GoogleOrganicItemTimestamp",
        "GoogleOrganicOrdinaryTextField",
        "GoogleOrganicLinksFamily",
    ):
        assert schemas[model]["properties"]["state"]["enum"] == ordinary, model
    for model in ("GoogleOrganicTextField", "GoogleOrganicIntField"):
        assert schemas[model]["properties"]["state"]["enum"] == inherited, model
    # The narrowed state carries its own documentation on the exact properties.
    for model in (
        "GoogleOrganicItemTimestamp",
        "GoogleOrganicOrdinaryTextField",
        "GoogleOrganicLinksFamily",
    ):
        assert "not_requested and inapplicable are impossible" in _description(
            schemas, model, "state"
        )
    assert (
        schemas["GoogleOrganicSitelink"]["properties"]["description"]["$ref"]
        == "#/components/schemas/GoogleOrganicOrdinaryTextField"
    )


# --------------------------------------------------------------------------------------
# Field-specific OpenAPI documentation
# --------------------------------------------------------------------------------------


def _schemas(client: TestClient) -> dict[str, Any]:
    spec = client.get(OPENAPI).json()
    schemas = spec["components"]["schemas"]
    assert isinstance(schemas, dict)
    return schemas


def _description(schemas: dict[str, Any], model: str, field: str) -> str:
    properties = schemas[model]["properties"]
    assert field in properties, f"{model}.{field} is missing from the generated schema"
    description = properties[field].get("description")
    assert isinstance(description, str) and description, (
        f"{model}.{field} carries no OpenAPI description"
    )
    return description


def test_the_history_route_advertises_both_recipe_documents(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt, _capture_id = _prepare(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        spec = client.get(OPENAPI).json()
    schema = spec["paths"][HISTORY]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    refs = {item["$ref"].rsplit("/", 1)[-1] for item in schema["anyOf"]}
    assert refs == {"GoogleOrganicExpandedHistoryEnvelope", "HistoryListEnvelope"}


def test_item_timestamp_descriptions_are_attached_to_the_exact_properties(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt, _capture_id = _prepare(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        schemas = _schemas(client)
    families = (
        ("GoogleOrganicRankedResultV2", "organic_item_timestamp"),
        ("GoogleOrganicTopStoryResult", "top_story_item_timestamp"),
        ("GoogleOrganicVideoResult", "video_item_timestamp"),
    )
    for model, field in families:
        text = _description(schemas, model, field)
        assert "NOT Capture time" in text
        assert "NOT the result retrieval datetime" in text
        assert "NOT Provider Update Time" in text
        assert "NOT a Data Period" in text
        assert "does not certify it as an independent publication instant" in text
        assert "never inherits" in text
    story_text = _description(
        schemas, "GoogleOrganicTopStoryResult", "top_story_item_timestamp"
    )
    assert "relative date string" in story_text
    organic_text = _description(
        schemas, "GoogleOrganicRankedResultV2", "organic_item_timestamp"
    )
    assert "organic item/result timestamp" in organic_text
    # The result clock is documented as a different fact on its own property.
    result_time = _description(
        schemas, "GoogleOrganicResultContext", "provider_result_time"
    )
    assert "not an item timestamp" in result_time
    for field in ("request_started_at", "transport_ended_at"):
        capture_text = _description(schemas, "GoogleOrganicExpandedCapture", field)
        assert "This is Capture time, not a provider item timestamp." in capture_text
    authorized = _description(schemas, "GoogleOrganicExpandedCapture", "authorized_at")
    assert "must never substitute for any provider item timestamp" in authorized


def test_identity_occurrence_and_completeness_descriptions_are_field_specific(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt, _capture_id = _prepare(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        schemas = _schemas(client)
    for model in (
        "GoogleOrganicTopStoryResult",
        "GoogleOrganicVideoResult",
        "GoogleOrganicSitelink",
    ):
        url_text = _description(schemas, model, "child_url")
        assert "NOT a canonical Page" in url_text
        assert "never normalized" in url_text
        for axis in (
            "parent_page",
            "parent_position",
            "parent_rank_group",
            "parent_rank_absolute",
            "parent_within_capture_identity",
        ):
            parent_text = _description(schemas, model, axis)
            assert "not the child's own rank" in parent_text
            assert "not a child occurrence" in parent_text
        occurrence_text = _description(schemas, model, "occurrences")
        assert "never a rank" in occurrence_text
        assert "do not prove provider or corpus completeness" in occurrence_text
    index_text = _description(schemas, "GoogleOrganicChildOccurrence", "child_index")
    assert "never a rank, importance, score, or identity" in index_text
    count_text = _description(
        schemas, "GoogleOrganicCaptureOutcome", "observation_count"
    )
    assert "occurrence rows are never counted here" in count_text.lower()
    video_source = _description(schemas, "GoogleOrganicVideoResult", "source")
    assert "no child domain is exposed" in video_source
    assert "never derives one from the URL" in video_source
    assert "domain" not in schemas["GoogleOrganicVideoResult"]["properties"]


def test_links_family_states_are_documented_on_the_links_properties(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt, _capture_id = _prepare(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        schemas = _schemas(client)
    state_text = _description(schemas, "GoogleOrganicLinksFamily", "state")
    assert "absent (no key)" in state_text
    assert "json_null (key stated null)" in state_text
    assert "stated empty array" in state_text
    assert "stated populated array" in state_text
    assert "can never stand in for the four distinct provider families" in state_text
    count_text = _description(
        schemas, "GoogleOrganicLinksFamily", "returned_child_count"
    )
    assert "0 for a stated empty array" in count_text
    assert "null whenever links was absent or JSON null" in count_text
    parent_text = _description(schemas, "GoogleOrganicRankedResultV2", "links")
    assert "independently of the sitelinks list" in parent_text


def test_recipe_version_behaviour_is_documented_on_the_version_properties(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store, _attempt, _capture_id = _prepare(tmp_path, postgres_dsn)
    with _app(store, postgres_dsn) as client:
        schemas = _schemas(client)
    for model in (
        "GoogleOrganicExpandedHistoryEnvelope",
        "GoogleOrganicExpandedCapture",
    ):
        text = _description(schemas, model, "derivation_version_id")
        assert "accepted v1 Recipe remains separately pinnable" in text
        assert "unchanged six-kind v1 document" in text
    resolution = _description(
        schemas, "GoogleOrganicExpandedHistoryEnvelope", "recipe_resolution"
    )
    assert "never changes the operator selection" in resolution
    kind_text = _description(schemas, "GoogleOrganicRankedResultV2", "observation_kind")
    assert "accepted v1 placement identity axes exactly" in kind_text
    assert "content, never identity" in kind_text
    limit_text = _description(schemas, "GoogleOrganicExpandedHistoryEnvelope", "limit")
    assert "never hides corruption" in limit_text
    total_text = _description(
        schemas, "GoogleOrganicExpandedHistoryEnvelope", "total_matching"
    )
    assert "Not Observation" in total_text
    assert "child occurrences" in total_text
