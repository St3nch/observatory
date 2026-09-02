"""PF-18: expanded Google Organic Derivation into real PostgreSQL 18.

Zero provider network activity: every Capture is committed from the frozen PF-10
Conformance body or a bounded synthetic mutation of it.
"""

from __future__ import annotations

import copy
import json
import socket
from collections import Counter
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from psycopg.errors import CheckViolation, ForeignKeyViolation

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
    GOOGLE_ORGANIC_EXPANDED_RECIPE_BYTES,
    GOOGLE_ORGANIC_EXPANDED_RECIPE_ID,
    GOOGLE_ORGANIC_RECIPE_BYTES,
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
from observatory.derive import DerivationError
from observatory.evidence_store import create_store
from observatory.google_organic_derive import (
    derive_google_organic,
    derive_google_organic_expanded,
    plan_google_organic_expanded_capture,
)
from observatory.migrate import (
    PF18_SCHEMA_STATEMENTS,
    PF18_TABLES,
    apply_migrations,
    connect,
)
from observatory.provider_recipe_selection import (
    ProviderRecipeNotSelected,
    resolve_provider_recipe,
    select_provider_recipe,
)

FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_google_organic_pf10.json"
)
KEYWORD = "conspiracy theories"
EXPECTED_EXPANDED_OBSERVATIONS = 248
EXPECTED_V1_OBSERVATIONS = 237
WIKI_URL = "https://en.wikipedia.org/wiki/Conspiracy_theory"
CLARION_URL = (
    "https://www.clarionledger.com/story/entertainment/2026/08/18/"
    "conspiracy-theories-are-debunked-in-history-of-huey-longs-assassination/"
    "91286800007/"
)

CHILD_RELATIONS = (
    ("google_organic_top_story_results", "google_organic_top_story_result_occurrences"),
    ("google_organic_video_results", "google_organic_video_result_occurrences"),
    ("google_organic_sitelinks", "google_organic_sitelink_occurrences"),
)
EXPANDED_RELATIONS = (
    "google_organic_result_context",
    "google_organic_serp_features",
    "google_organic_ranked_results_v2",
    "google_organic_aio_presence",
    "google_organic_aio_sources",
    "google_organic_aio_source_occurrences",
    "google_organic_related_questions",
    "google_organic_related_question_occurrences",
    "google_organic_related_queries",
    "google_organic_top_story_results",
    "google_organic_top_story_result_occurrences",
    "google_organic_video_results",
    "google_organic_video_result_occurrences",
    "google_organic_sitelinks",
    "google_organic_sitelink_occurrences",
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
    return closed_organic_parameters(keyword=KEYWORD)


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


def _organic_at(document: dict[str, Any], rank_absolute: int) -> dict[str, Any]:
    for item in _items(document):
        if item["type"] == "organic" and item["rank_absolute"] == rank_absolute:
            assert isinstance(item, dict)
            return item
    raise AssertionError(f"no organic item at rank_absolute {rank_absolute}")


def _complete_capture_dict() -> dict[str, object]:
    return {
        "transport_state": "response_complete",
        "response": {"completeness": "complete"},
    }


def _commit(store: Any, body: bytes, nonce: str, *, suffix: str = "1") -> tuple[str, str]:
    parameters = _parameters()
    attempt = organic_http_attempt_document(
        parameters=parameters,
        attempt_nonce=nonce,
        authorized_at="2026-08-18T17:37:00.000000Z",
        observatory_version="pf18-test-v1",
    )
    attempt_id = store.commit_attempt(
        attempt, request_body=organic_request_body_bytes(parameters)
    )
    capture_id = store.commit_capture(
        organic_http_capture_document(
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
        ),
        response_body=body,
    )
    return attempt_id, capture_id


def _plan(body: bytes | None = None) -> Any:
    return plan_google_organic_expanded_capture(
        "a" * 64,
        "b" * 64,
        _complete_capture_dict(),
        _parameters(),
        body if body is not None else _body(),
    )


def _counts(connection: Any, version: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table in EXPANDED_RELATIONS:
        row = connection.execute(
            f"SELECT count(*) FROM {table} WHERE derivation_version_id = %s", (version,)
        ).fetchone()
        assert row is not None
        counts[table] = int(row[0])
    return counts


def _logical_snapshot(dsn: str, version: str) -> dict[str, list[tuple[Any, ...]]]:
    snapshot: dict[str, list[tuple[Any, ...]]] = {}
    with connect(dsn) as connection:
        for table in EXPANDED_RELATIONS:
            rows = connection.execute(
                f"SELECT * FROM {table} WHERE derivation_version_id = %s", (version,)
            ).fetchall()
            snapshot[table] = sorted(
                tuple(str(item) for item in row) for row in rows
            )
        for table in ("outcomes", "observation_envelopes", "derivation_diagnostics"):
            rows = connection.execute(
                f"SELECT * FROM {table} WHERE derivation_version_id = %s", (version,)
            ).fetchall()
            snapshot[table] = sorted(
                tuple(str(item) for item in row) for row in rows
            )
    return snapshot


# --------------------------------------------------------------------------------------
# Migration layering
# --------------------------------------------------------------------------------------


def test_pf18_adds_exactly_seven_google_organic_local_relations() -> None:
    assert PF18_TABLES == (
        "google_organic_ranked_results_v2",
        "google_organic_top_story_results",
        "google_organic_top_story_result_occurrences",
        "google_organic_video_results",
        "google_organic_video_result_occurrences",
        "google_organic_sitelinks",
        "google_organic_sitelink_occurrences",
    )
    joined = "\n".join(PF18_SCHEMA_STATEMENTS)
    for table in PF18_TABLES:
        assert f"CREATE TABLE IF NOT EXISTS {table} (" in joined
    # The accepted v1 ranked relation is never reshaped into a second v1 form.
    assert "ALTER TABLE google_organic_ranked_results" not in joined
    assert "DROP" not in joined
    # No Page identity, no cross-surface joins, no universal provider clock.
    assert "page_id" not in joined
    assert "provider_update_time" not in joined
    assert "REFERENCES ranked_keywords" not in joined
    assert "REFERENCES related_keywords" not in joined
    assert "REFERENCES keyword_overview" not in joined


def test_pf18_child_relations_bind_to_their_exact_typed_parents() -> None:
    joined = "\n".join(PF18_SCHEMA_STATEMENTS)
    assert "REFERENCES google_organic_serp_features (" in joined
    assert "REFERENCES google_organic_ranked_results_v2 (" in joined
    assert "parent_item_type = 'top_stories'" in joined
    assert "parent_item_type = 'video'" in joined
    for parent, occurrence in CHILD_RELATIONS:
        assert f"REFERENCES {parent} (" in joined
        assert f"CREATE TABLE IF NOT EXISTS {occurrence} (" in joined


# --------------------------------------------------------------------------------------
# Exact PF-10 expanded planning
# --------------------------------------------------------------------------------------


def test_plan_frozen_fixture_has_the_exact_expanded_semantic_counts() -> None:
    planned = _plan()
    assert planned.classification == "observation_admitted"
    assert len(planned.envelopes) == EXPECTED_EXPANDED_OBSERVATIONS
    by_kind = Counter(item.observation_kind for item in planned.envelopes)
    assert by_kind == Counter(
        {
            FEATURE_PRESENCE_KIND: 111,
            ORGANIC_PLACEMENT_V2_KIND: 97,
            AIO_PRESENCE_KIND: 1,
            AIO_SOURCE_KIND: 15,
            RELATED_QUESTION_KIND: 4,
            RELATED_QUERY_KIND: 9,
            TOP_STORY_RESULT_KIND: 4,
            VIDEO_RESULT_KIND: 3,
            ORGANIC_SITELINK_KIND: 4,
        }
    )
    assert ORGANIC_PLACEMENT_KIND not in by_kind
    assert EXPECTED_EXPANDED_OBSERVATIONS == 237 - 97 + 97 + 4 + 3 + 4
    # Occurrence rows are subordinate testimony and never raise observation_count.
    assert len(planned.top_story_occurrences) == 4
    assert len(planned.video_occurrences) == 3
    assert len(planned.sitelink_occurrences) == 4
    assert all(
        envelope.derivation_version_id == GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
        for envelope in planned.envelopes
    )


def test_plan_states_the_exact_pf10_timestamp_and_links_families() -> None:
    planned = _plan()
    ranked = planned.details["google_organic_ranked_results_v2"]
    assert len(ranked) == 97
    timestamps = Counter(row["organic_item_timestamp_state"] for row in ranked)
    assert timestamps == Counter({"stated": 58, "json_null": 39})
    assert timestamps["absent"] == 0
    links = Counter(row["links_state"] for row in ranked)
    assert links == Counter({"json_null": 96, "stated": 1})
    populated = [row for row in ranked if row["links_state"] == "stated"]
    assert len(populated) == 1
    assert populated[0]["links_count"] == 4
    assert populated[0]["url"] == WIKI_URL
    assert all(row["links_count"] is None for row in ranked if row["links_state"] != "stated")
    stories = planned.details["google_organic_top_story_results"]
    assert len(stories) == 4
    assert {row["parent_rank_absolute"] for row in stories} == {6}
    assert all(row["parent_item_type"] == "top_stories" for row in stories)
    assert all(row["top_story_item_timestamp_state"] == "stated" for row in stories)
    videos = planned.details["google_organic_video_results"]
    assert len(videos) == 3
    assert {row["parent_rank_absolute"] for row in videos} == {7}
    assert all(row["parent_item_type"] == "video" for row in videos)
    assert all("domain" not in row for row in videos)
    sitelinks = planned.details["google_organic_sitelinks"]
    assert len(sitelinks) == 4
    assert {row["parent_rank_absolute"] for row in sitelinks} == {2}
    assert all(row["description_state"] == "json_null" for row in sitelinks)


def test_child_identity_scopes_by_parent_placement_not_by_url_alone() -> None:
    document = _decoded()
    stories = _first(document, "top_stories")
    clone = copy.deepcopy(stories)
    clone["position"] = "right"
    clone["rank_group"] = 1
    clone["rank_absolute"] = 1
    clone["items"] = [copy.deepcopy(stories["items"][0])]
    _set_items(document, [*_items(document), clone])
    planned = _plan(_encode(document))
    rows = planned.details["google_organic_top_story_results"]
    same_url = [row for row in rows if row["child_url"] == CLARION_URL]
    assert len(same_url) == 2
    identities = {row["within_capture_identity"] for row in same_url}
    assert len(identities) == 2
    assert {row["parent_position"] for row in same_url} == {"left", "right"}
    # Parent envelopes differ too, so the DB binding cannot confuse them.
    assert len({row["parent_within_capture_identity"] for row in same_url}) == 2


def test_the_same_url_in_two_kinds_never_collapses_to_one_observation() -> None:
    document = _decoded()
    _first(document, "top_stories")["items"][0]["url"] = WIKI_URL
    planned = _plan(_encode(document))
    story = next(
        row
        for row in planned.details["google_organic_top_story_results"]
        if row["child_url"] == WIKI_URL
    )
    ranked = next(
        row
        for row in planned.details["google_organic_ranked_results_v2"]
        if row["url"] == WIKI_URL
    )
    assert story["observation_kind"] == TOP_STORY_RESULT_KIND
    assert ranked["observation_kind"] == ORGANIC_PLACEMENT_V2_KIND
    assert story["within_capture_identity"] != ranked["within_capture_identity"]
    assert len(planned.envelopes) == EXPECTED_EXPANDED_OBSERVATIONS


def test_agreeing_duplicate_children_collapse_to_one_row_with_two_occurrences() -> None:
    document = _decoded()
    stories = _first(document, "top_stories")
    stories["items"].append(copy.deepcopy(stories["items"][0]))
    planned = _plan(_encode(document))
    rows = planned.details["google_organic_top_story_results"]
    assert len(rows) == 4
    repeated = next(row for row in rows if row["child_url"] == CLARION_URL)
    occurrences = [
        row
        for row in planned.top_story_occurrences
        if row["within_capture_identity"] == repeated["within_capture_identity"]
    ]
    assert sorted(int(row["child_index"]) for row in occurrences) == [0, 4]
    assert len(planned.top_story_occurrences) == 5
    # One extra occurrence, not one extra Observation.
    assert len(planned.envelopes) == EXPECTED_EXPANDED_OBSERVATIONS


def test_child_reorder_preserves_identities_and_follows_provider_order() -> None:
    baseline = _plan()
    document = _decoded()
    stories = _first(document, "top_stories")
    stories["items"] = list(reversed(stories["items"]))
    videos = _first(document, "video")
    videos["items"] = list(reversed(videos["items"]))
    reordered = _plan(_encode(document))
    for table, occurrences in (
        ("google_organic_top_story_results", "top_story_occurrences"),
        ("google_organic_video_results", "video_occurrences"),
    ):
        before = {row["within_capture_identity"] for row in baseline.details[table]}
        after = {row["within_capture_identity"] for row in reordered.details[table]}
        assert before == after
        old_index = {
            row["within_capture_identity"]: row["child_index"]
            for row in getattr(baseline, occurrences)
        }
        new_index = {
            row["within_capture_identity"]: row["child_index"]
            for row in getattr(reordered, occurrences)
        }
        assert old_index != new_index
        assert sorted(old_index.values()) == sorted(new_index.values())
    assert len(reordered.envelopes) == EXPECTED_EXPANDED_OBSERVATIONS


def test_conflicting_duplicate_child_rejects_the_whole_expanded_unit() -> None:
    document = _decoded()
    stories = _first(document, "top_stories")
    clone = copy.deepcopy(stories["items"][0])
    clone["source"] = "A different newsroom"
    stories["items"].append(clone)
    planned = _plan(_encode(document))
    assert planned.classification == "provider_envelope_rejected"
    assert planned.envelopes == ()
    assert planned.context is None
    assert all(rows == () for rows in planned.details.values())
    assert planned.top_story_occurrences == ()
    assert planned.video_occurrences == ()
    assert planned.sitelink_occurrences == ()


def test_populated_related_result_rejects_the_whole_expanded_unit() -> None:
    document = _decoded()
    _organic_at(document, 2)["related_result"] = [{"type": "organic"}]
    planned = _plan(_encode(document))
    assert planned.classification == "provider_envelope_rejected"
    assert planned.envelopes == ()


# --------------------------------------------------------------------------------------
# Real PostgreSQL persistence
# --------------------------------------------------------------------------------------


def test_expanded_derivation_persists_the_exact_pf10_relations(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    attempt_id, capture_id = _commit(store, _body(), "11" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        summary = derive_google_organic_expanded(store, connection)
        assert summary.derivation_version_id == GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
        assert summary.observations == EXPECTED_EXPANDED_OBSERVATIONS
        assert summary.integrity_failures == 0
        counts = _counts(connection, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID)
        assert counts["google_organic_ranked_results_v2"] == 97
        assert counts["google_organic_top_story_results"] == 4
        assert counts["google_organic_top_story_result_occurrences"] == 4
        assert counts["google_organic_video_results"] == 3
        assert counts["google_organic_video_result_occurrences"] == 3
        assert counts["google_organic_sitelinks"] == 4
        assert counts["google_organic_sitelink_occurrences"] == 4
        assert counts["google_organic_serp_features"] == 111
        outcome = connection.execute(
            """
            SELECT classification, observation_count
            FROM outcomes
            WHERE derivation_version_id = %s AND capture_id = %s
            """,
            (GOOGLE_ORGANIC_EXPANDED_RECIPE_ID, capture_id),
        ).fetchone()
        assert outcome == ("observation_admitted", EXPECTED_EXPANDED_OBSERVATIONS)
        attempt_outcome = connection.execute(
            """
            SELECT classification FROM outcomes
            WHERE derivation_version_id = %s AND attempt_id = %s AND capture_id IS NULL
            """,
            (GOOGLE_ORGANIC_EXPANDED_RECIPE_ID, attempt_id),
        ).fetchone()
        assert attempt_outcome == ("authorized_unresolved",)
        states = connection.execute(
            """
            SELECT organic_item_timestamp_state, count(*)
            FROM google_organic_ranked_results_v2
            WHERE derivation_version_id = %s
            GROUP BY 1 ORDER BY 1
            """,
            (GOOGLE_ORGANIC_EXPANDED_RECIPE_ID,),
        ).fetchall()
        assert states == [("json_null", 39), ("stated", 58)]
        links = connection.execute(
            """
            SELECT links_state, links_count, count(*)
            FROM google_organic_ranked_results_v2
            WHERE derivation_version_id = %s
            GROUP BY 1, 2 ORDER BY 1
            """,
            (GOOGLE_ORGANIC_EXPANDED_RECIPE_ID,),
        ).fetchall()
        assert links == [("json_null", None, 96), ("stated", 4, 1)]


def test_expanded_and_v1_recipes_coexist_and_stay_independently_derivable(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit(store, _body(), "12" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        first = derive_google_organic(store, connection)
        expanded = derive_google_organic_expanded(store, connection)
        second = derive_google_organic(store, connection)
        assert first.observations == EXPECTED_V1_OBSERVATIONS
        assert expanded.observations == EXPECTED_EXPANDED_OBSERVATIONS
        assert second.observations == EXPECTED_V1_OBSERVATIONS
        v1_counts = _counts(connection, GOOGLE_ORGANIC_RECIPE_ID)
        assert v1_counts["google_organic_ranked_results_v2"] == 0
        assert v1_counts["google_organic_top_story_results"] == 0
        assert v1_counts["google_organic_video_results"] == 0
        assert v1_counts["google_organic_sitelinks"] == 0
        assert v1_counts["google_organic_serp_features"] == 111
        legacy = connection.execute(
            """
            SELECT count(*) FROM google_organic_ranked_results
            WHERE derivation_version_id = %s
            """,
            (GOOGLE_ORGANIC_RECIPE_ID,),
        ).fetchone()
        assert legacy == (97,)
        no_v2_rows_in_v1_table = connection.execute(
            """
            SELECT count(*) FROM google_organic_ranked_results
            WHERE derivation_version_id = %s
            """,
            (GOOGLE_ORGANIC_EXPANDED_RECIPE_ID,),
        ).fetchone()
        assert no_v2_rows_in_v1_table == (0,)


def test_v1_recipe_bytes_rows_and_counts_are_unchanged_after_expansion(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit(store, _body(), "13" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic(store, connection)
        connection.commit()
        before = _logical_snapshot(postgres_dsn, GOOGLE_ORGANIC_RECIPE_ID)
        v1_bytes = connection.execute(
            "SELECT recipe_canonical_bytes FROM provider_recipes WHERE derivation_version_id = %s",
            (GOOGLE_ORGANIC_RECIPE_ID,),
        ).fetchone()
        assert v1_bytes is not None
        stored_v1 = bytes(v1_bytes[0])
        derive_google_organic_expanded(store, connection)
        connection.commit()
    after = _logical_snapshot(postgres_dsn, GOOGLE_ORGANIC_RECIPE_ID)
    assert after == before
    with connect(postgres_dsn) as connection:
        row = connection.execute(
            "SELECT recipe_canonical_bytes FROM provider_recipes WHERE derivation_version_id = %s",
            (GOOGLE_ORGANIC_RECIPE_ID,),
        ).fetchone()
        assert row is not None
        assert bytes(row[0]) == stored_v1
        assert bytes(row[0]) == GOOGLE_ORGANIC_RECIPE_BYTES
        assert len(bytes(row[0])) == 2487
        expanded_row = connection.execute(
            "SELECT recipe_canonical_bytes FROM provider_recipes WHERE derivation_version_id = %s",
            (GOOGLE_ORGANIC_EXPANDED_RECIPE_ID,),
        ).fetchone()
        assert expanded_row is not None
        assert bytes(expanded_row[0]) == GOOGLE_ORGANIC_EXPANDED_RECIPE_BYTES
        counts = connection.execute(
            """
            SELECT observation_count FROM outcomes
            WHERE derivation_version_id = %s AND capture_id IS NOT NULL
            """,
            (GOOGLE_ORGANIC_RECIPE_ID,),
        ).fetchall()
        assert counts == [(EXPECTED_V1_OBSERVATIONS,)]


def test_registering_or_deriving_the_expanded_recipe_never_changes_selection(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit(store, _body(), "14" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic(store, connection)
        with pytest.raises(ProviderRecipeNotSelected):
            resolve_provider_recipe(connection, ORGANIC_ADAPTER_CONTRACT)
        select_provider_recipe(
            connection, ORGANIC_ADAPTER_CONTRACT, GOOGLE_ORGANIC_RECIPE_ID
        )
        derive_google_organic_expanded(store, connection)
        resolved = resolve_provider_recipe(connection, ORGANIC_ADAPTER_CONTRACT)
        assert resolved.derivation_version_id == GOOGLE_ORGANIC_RECIPE_ID
        assert resolved.resolution == "selected"
        # Changing it stays a separate explicit operator action.
        select_provider_recipe(
            connection, ORGANIC_ADAPTER_CONTRACT, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
        )
        moved = resolve_provider_recipe(connection, ORGANIC_ADAPTER_CONTRACT)
        assert moved.derivation_version_id == GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
        derive_google_organic(store, connection)
        assert (
            resolve_provider_recipe(
                connection, ORGANIC_ADAPTER_CONTRACT
            ).derivation_version_id
            == GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
        )


def test_same_recipe_rerun_restores_a_missing_rebuildable_child_row(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit(store, _body(), "15" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic_expanded(store, connection)
        connection.execute(
            "DELETE FROM google_organic_top_story_result_occurrences WHERE child_index = 2"
        )
        connection.execute(
            """
            DELETE FROM google_organic_top_story_results
            WHERE within_capture_identity NOT IN (
                SELECT within_capture_identity
                FROM google_organic_top_story_result_occurrences
            )
            """
        )
        connection.commit()
        restored = derive_google_organic_expanded(store, connection)
        assert restored.observations == EXPECTED_EXPANDED_OBSERVATIONS
        counts = _counts(connection, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID)
        assert counts["google_organic_top_story_results"] == 4
        assert counts["google_organic_top_story_result_occurrences"] == 4


def test_an_extra_child_occurrence_fails_the_complete_set_closed(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit(store, _body(), "16" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic_expanded(store, connection)
        connection.execute(
            """
            INSERT INTO google_organic_video_result_occurrences (
                capture_id, derivation_version_id, within_capture_identity,
                observation_kind, child_index
            )
            SELECT capture_id, derivation_version_id, within_capture_identity,
                   observation_kind, 99
            FROM google_organic_video_results
            LIMIT 1
            """
        )
        connection.commit()
        with pytest.raises(DerivationError) as excinfo:
            derive_google_organic_expanded(store, connection)
        assert "complete-set mismatch" in str(excinfo.value)


def test_an_extra_typed_child_row_without_an_envelope_cannot_be_inserted(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit(store, _body(), "17" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic_expanded(store, connection)
        connection.commit()
        with pytest.raises(ForeignKeyViolation):
            connection.execute(
                """
                INSERT INTO google_organic_sitelinks (
                    capture_id, derivation_version_id, within_capture_identity,
                    observation_kind, requested_keyword,
                    parent_within_capture_identity, parent_page, parent_position,
                    parent_rank_group, parent_rank_absolute,
                    child_url, title, domain, description, description_state
                )
                SELECT capture_id, derivation_version_id, %s, observation_kind,
                       requested_keyword, parent_within_capture_identity,
                       parent_page, parent_position, parent_rank_group,
                       parent_rank_absolute, 'https://example.test/extra',
                       'Extra', 'example.test', NULL, 'json_null'
                FROM google_organic_sitelinks
                LIMIT 1
                """,
                ("cd" * 32,),
            )
        connection.rollback()


def test_an_extra_envelope_without_a_typed_row_fails_the_complete_set(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _, capture_id = _commit(store, _body(), "18" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic_expanded(store, connection)
        connection.execute(
            """
            INSERT INTO observation_envelopes (
                capture_id, derivation_version_id, within_capture_identity,
                attempt_id, provider, adapter_contract, observation_kind
            )
            SELECT capture_id, derivation_version_id, %s, attempt_id, provider,
                   adapter_contract, observation_kind
            FROM observation_envelopes
            WHERE derivation_version_id = %s AND capture_id = %s
              AND observation_kind = %s
            LIMIT 1
            """,
            (
                "ef" * 32,
                GOOGLE_ORGANIC_EXPANDED_RECIPE_ID,
                capture_id,
                VIDEO_RESULT_KIND,
            ),
        )
        connection.commit()
        with pytest.raises(DerivationError) as excinfo:
            derive_google_organic_expanded(store, connection)
        assert "complete-set mismatch" in str(excinfo.value)


def test_an_orphan_semantic_child_without_occurrences_fails_closed(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit(store, _body(), "19" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic_expanded(store, connection)
        connection.execute("DELETE FROM google_organic_sitelink_occurrences")
        connection.commit()
        # The rebuildable occurrence rows come back and the coverage gate is satisfied.
        assert (
            derive_google_organic_expanded(store, connection).observations
            == EXPECTED_EXPANDED_OBSERVATIONS
        )
        counts = _counts(connection, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID)
        assert counts["google_organic_sitelink_occurrences"] == 4


def test_a_sitelink_cannot_bind_to_a_missing_ranked_v2_parent(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit(store, _body(), "1a" * 32)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_google_organic_expanded(store, connection)
        connection.commit()
        with pytest.raises(ForeignKeyViolation):
            connection.execute(
                """
                UPDATE google_organic_sitelinks
                SET parent_within_capture_identity = %s
                """,
                ("ab" * 32,),
            )
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute(
                "UPDATE google_organic_video_results SET parent_item_type = 'top_stories'"
            )
        connection.rollback()
        with pytest.raises(CheckViolation):
            connection.execute(
                """
                UPDATE google_organic_ranked_results_v2
                SET links_state = 'json_null'
                WHERE links_state = 'stated'
                """
            )
        connection.rollback()


def test_two_fresh_postgres_rebuilds_are_logically_equivalent(
    tmp_path: Path, postgres_dsn: str, postgres_second_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    _commit(store, _body(), "1b" * 32)
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_second_dsn)
    for dsn in (postgres_dsn, postgres_second_dsn):
        with connect(dsn) as connection:
            summary = derive_google_organic_expanded(store, connection)
            assert summary.observations == EXPECTED_EXPANDED_OBSERVATIONS
    first = _logical_snapshot(postgres_dsn, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID)
    second = _logical_snapshot(postgres_second_dsn, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID)
    assert set(first) == set(second)
    for table in first:
        assert first[table] == second[table], table
    assert first["google_organic_top_story_results"]
    assert first["google_organic_sitelink_occurrences"]
