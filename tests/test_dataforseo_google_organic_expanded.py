"""PF-18: Google Organic parser-v2 and the expanded Derivation Recipe.

Every proof here is zero-network and reads only the frozen PF-10 Conformance body
plus bounded synthetic mutations of it. Parser-v1 and the accepted v1 Recipe must
survive this file byte-for-byte.
"""

from __future__ import annotations

import copy
import hashlib
import json
import socket
from collections import Counter
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from observatory.capture_event import ORGANIC_ADAPTER_CONTRACT
from observatory.dataforseo_google_organic import (
    AIO_PRESENCE_KIND,
    AIO_SOURCE_KIND,
    FEATURE_PRESENCE_KIND,
    GOOGLE_ORGANIC_EXPANDED_RECIPE,
    GOOGLE_ORGANIC_EXPANDED_RECIPE_BYTES,
    GOOGLE_ORGANIC_EXPANDED_RECIPE_ID,
    GOOGLE_ORGANIC_RECIPE,
    GOOGLE_ORGANIC_RECIPE_BYTES,
    GOOGLE_ORGANIC_RECIPE_ID,
    ORGANIC_PLACEMENT_KIND,
    ORGANIC_PLACEMENT_V2_KIND,
    ORGANIC_SITELINK_KIND,
    PARSER_CONTRACT,
    PARSER_CONTRACT_V2,
    RELATED_QUERY_KIND,
    RELATED_QUESTION_KIND,
    TOP_STORY_RESULT_KIND,
    VIDEO_RESULT_KIND,
    GoogleOrganicParseError,
    google_organic_expanded_recipe,
    parse_google_organic,
    parse_google_organic_v2,
)
from observatory.dataforseo_keyword_overview import FieldState, ParseClassification
from observatory.provider_recipe import (
    recipe_bytes,
    recipe_derivation_version_id,
    validate_recipe,
)

FIXTURE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_google_organic_pf10.json"
)
EXPANDED_RECIPE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_google_organic_expanded_recipe.jcs"
)
PF10_BODY_SHA256 = "7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f"
PF10_BODY_BYTES = 135722
ACCEPTED_V1_RECIPE_SHA256 = (
    "338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde"
)
ACCEPTED_V1_RECIPE_BYTE_LENGTH = 2487
EXPANDED_RECIPE_SHA256 = (
    "2704ff82a175be7bacfd601cf7f0e684ca1cc85f9e8cfc93f520b603bcb29d04"
)
EXPANDED_RECIPE_BYTE_LENGTH = 3405

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

PARAMETERS: dict[str, object] = {
    "contract": ORGANIC_ADAPTER_CONTRACT,
    "depth": 100,
    "device": "desktop",
    "group_organic_results": True,
    "keyword": "conspiracy theories",
    "language_code": "en",
    "load_async_ai_overview": True,
    "location_code": 2840,
    "os": "windows",
}

RESULT_DATETIME = "2026-08-18 17:37:36 +00:00"
WIKI_URL = "https://en.wikipedia.org/wiki/Conspiracy_theory"
CLARION_URL = (
    "https://www.clarionledger.com/story/entertainment/2026/08/18/"
    "conspiracy-theories-are-debunked-in-history-of-huey-longs-assassination/"
    "91286800007/"
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


def _fixture() -> bytes:
    return FIXTURE_PATH.read_bytes()


def _decoded(body: bytes | None = None) -> dict[str, Any]:
    decoder = json.JSONDecoder(parse_int=int, parse_float=Decimal)
    value, _end = decoder.raw_decode((body or _fixture()).decode("utf-8"))
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


def _parse_v2(document: dict[str, Any]) -> Any:
    return parse_google_organic_v2(_encode(document), PARAMETERS)


def _parse_v2_error(document: dict[str, Any]) -> GoogleOrganicParseError:
    with pytest.raises(GoogleOrganicParseError) as excinfo:
        _parse_v2(document)
    return excinfo.value


# --------------------------------------------------------------------------------------
# Frozen Evidence and Recipe identity
# --------------------------------------------------------------------------------------


def test_pf10_fixture_bytes_and_hash_are_untouched_by_pf18() -> None:
    raw = _fixture()
    assert not raw.endswith(b"\n")
    assert len(raw) == PF10_BODY_BYTES
    assert hashlib.sha256(raw).hexdigest() == PF10_BODY_SHA256


def test_accepted_v1_recipe_bytes_and_digest_are_unchanged() -> None:
    assert len(GOOGLE_ORGANIC_RECIPE_BYTES) == ACCEPTED_V1_RECIPE_BYTE_LENGTH
    assert GOOGLE_ORGANIC_RECIPE_ID == ACCEPTED_V1_RECIPE_SHA256
    document = validate_recipe(GOOGLE_ORGANIC_RECIPE)
    assert document["parser_contract"] == PARSER_CONTRACT
    assert document["observation_kinds"] == [
        FEATURE_PRESENCE_KIND,
        ORGANIC_PLACEMENT_KIND,
        AIO_PRESENCE_KIND,
        AIO_SOURCE_KIND,
        RELATED_QUESTION_KIND,
        RELATED_QUERY_KIND,
    ]


def test_expanded_recipe_is_frozen_content_addressed_and_distinct() -> None:
    published = EXPANDED_RECIPE_PATH.read_bytes()
    assert not published.endswith(b"\n")
    assert len(published) == EXPANDED_RECIPE_BYTE_LENGTH
    assert hashlib.sha256(published).hexdigest() == EXPANDED_RECIPE_SHA256
    assert published == GOOGLE_ORGANIC_EXPANDED_RECIPE_BYTES
    assert GOOGLE_ORGANIC_EXPANDED_RECIPE_ID == EXPANDED_RECIPE_SHA256
    assert recipe_bytes(google_organic_expanded_recipe()) == published
    assert recipe_derivation_version_id(GOOGLE_ORGANIC_EXPANDED_RECIPE) == (
        EXPANDED_RECIPE_SHA256
    )
    assert GOOGLE_ORGANIC_EXPANDED_RECIPE_ID != GOOGLE_ORGANIC_RECIPE_ID
    assert GOOGLE_ORGANIC_EXPANDED_RECIPE_BYTES != GOOGLE_ORGANIC_RECIPE_BYTES


def test_expanded_recipe_declares_the_exact_ordered_nine_kinds() -> None:
    document = validate_recipe(GOOGLE_ORGANIC_EXPANDED_RECIPE)
    assert document["provider"] == "dataforseo"
    assert document["adapter_contract"] == ORGANIC_ADAPTER_CONTRACT
    assert document["parser_contract"] == PARSER_CONTRACT_V2
    assert PARSER_CONTRACT_V2 != PARSER_CONTRACT
    assert document["observation_kinds"] == EXPANDED_KINDS
    assert ORGANIC_PLACEMENT_KIND not in EXPANDED_KINDS


def test_expanded_recipe_identity_axes_are_the_frozen_semantic_axes() -> None:
    document = validate_recipe(GOOGLE_ORGANIC_EXPANDED_RECIPE)
    identity = document["observation_identity"]
    assert isinstance(identity, dict)
    rows = identity["kinds"]
    assert isinstance(rows, list)
    axes = {row["observation_kind"]: row["axes"] for row in rows if isinstance(row, dict)}
    child_axes = {
        "child_url": "string",
        "parent_page": "integer",
        "parent_position": "string",
        "parent_rank_absolute": "integer",
        "parent_rank_group": "integer",
        "requested_keyword": "string",
    }
    assert axes[TOP_STORY_RESULT_KIND] == child_axes
    assert axes[VIDEO_RESULT_KIND] == child_axes
    assert axes[ORGANIC_SITELINK_KIND] == child_axes
    # Ranked-result v2 keeps the accepted v1 placement identity exactly; URL, the item
    # timestamp, and the links family are content, never identity.
    v1_document = validate_recipe(GOOGLE_ORGANIC_RECIPE)
    v1_identity = v1_document["observation_identity"]
    assert isinstance(v1_identity, dict)
    v1_rows = v1_identity["kinds"]
    assert isinstance(v1_rows, list)
    v1_axes = {
        row["observation_kind"]: row["axes"] for row in v1_rows if isinstance(row, dict)
    }
    assert axes[ORGANIC_PLACEMENT_V2_KIND] == v1_axes[ORGANIC_PLACEMENT_KIND]
    assert "url" not in axes[ORGANIC_PLACEMENT_V2_KIND]
    assert "timestamp" not in axes[ORGANIC_PLACEMENT_V2_KIND]
    assert "links" not in axes[ORGANIC_PLACEMENT_V2_KIND]
    assert "child_index" not in json.dumps(axes)
    for kind in (
        FEATURE_PRESENCE_KIND,
        AIO_PRESENCE_KIND,
        AIO_SOURCE_KIND,
        RELATED_QUESTION_KIND,
        RELATED_QUERY_KIND,
    ):
        assert axes[kind] == v1_axes[kind]


def test_expanded_recipe_permits_the_new_child_objects_as_extensions() -> None:
    document = validate_recipe(GOOGLE_ORGANIC_EXPANDED_RECIPE)
    policy = document["extension_policy"]
    assert isinstance(policy, dict)
    assert policy["extension_permitted_objects"] == [
        "/",
        "/ai_overview_element",
        "/ai_overview_reference",
        "/items",
        "/link_element",
        "/people_also_ask_element",
        "/result",
        "/tasks",
        "/top_stories_element",
        "/video_element",
    ]
    assert policy["unknown_extension_field"] == "diagnostic"
    assert policy["unknown_closed_field"] == "fail_closed"


# --------------------------------------------------------------------------------------
# Exact PF-10 expanded testimony
# --------------------------------------------------------------------------------------


def test_pf10_expanded_parse_reproduces_the_exact_child_inventory() -> None:
    parsed = parse_google_organic_v2(_fixture(), PARAMETERS)
    assert parsed.outcome is ParseClassification.ADMITTED
    assert parsed.requested_keyword == "conspiracy theories"
    assert parsed.items_count == 111
    assert len(parsed.feature_placements) == 111
    assert len(parsed.organic_placements) == 97
    assert parsed.diagnostics == ()

    assert len(parsed.top_story_groups) == 1
    stories = parsed.top_story_groups[0]
    assert (
        stories.page,
        stories.position,
        stories.rank_group,
        stories.rank_absolute,
    ) == (1, "left", 1, 6)
    assert len(stories.children) == 4
    assert [child.child_index for child in stories.children] == [0, 1, 2, 3]
    for child in stories.children:
        assert child.source
        assert child.domain
        assert child.title
        assert child.url.startswith("https://")
        assert child.top_story_item_timestamp.state is FieldState.STATED
    assert stories.children[0].url == CLARION_URL
    assert stories.children[0].source == "The Clarion-Ledger"
    assert stories.children[0].domain == "www.clarionledger.com"
    assert stories.children[0].top_story_item_timestamp.value == (
        "2026-08-18 09:37:26 +00:00"
    )

    assert len(parsed.video_groups) == 1
    videos = parsed.video_groups[0]
    assert (
        videos.page,
        videos.position,
        videos.rank_group,
        videos.rank_absolute,
    ) == (1, "left", 1, 7)
    assert len(videos.children) == 3
    assert [child.child_index for child in videos.children] == [0, 1, 2]
    for video_child in videos.children:
        assert video_child.source
        assert video_child.title
        assert video_child.url.startswith("https://")
        assert video_child.video_item_timestamp.state is FieldState.STATED
        # PF-10 states no video-child domain; PF-18 must not invent one.
        assert not hasattr(video_child, "domain")
    assert videos.children[0].source == "Facebook · Josh Johnson"


def test_pf10_organic_timestamp_and_links_states_are_exactly_preserved() -> None:
    parsed = parse_google_organic_v2(_fixture(), PARAMETERS)
    timestamps = Counter(
        placement.organic_item_timestamp.state for placement in parsed.organic_placements
    )
    assert timestamps == Counter(
        {FieldState.STATED: 58, FieldState.JSON_NULL: 39}
    )
    assert timestamps[FieldState.ABSENT] == 0
    links = Counter(placement.links_state for placement in parsed.organic_placements)
    assert links == Counter({FieldState.JSON_NULL: 96, FieldState.STATED: 1})
    stated = [
        placement
        for placement in parsed.organic_placements
        if placement.links_state is FieldState.STATED
    ]
    assert len(stated) == 1
    assert stated[0].links_count == 4
    assert stated[0].rank_absolute == 2
    assert stated[0].url == WIKI_URL
    assert [child.child_index for child in stated[0].sitelinks] == [0, 1, 2, 3]
    for link in stated[0].sitelinks:
        assert link.title
        assert link.domain == "en.wikipedia.org"
        assert link.description.state is FieldState.JSON_NULL
        assert link.description.value is None
    unstated = [
        placement
        for placement in parsed.organic_placements
        if placement.links_state is not FieldState.STATED
    ]
    assert all(placement.links_count is None for placement in unstated)
    assert all(placement.sitelinks == () for placement in unstated)


def test_pf10_carries_both_midnight_and_timed_organic_item_timestamps() -> None:
    parsed = parse_google_organic_v2(_fixture(), PARAMETERS)
    stated = [
        placement.organic_item_timestamp.value
        for placement in parsed.organic_placements
        if placement.organic_item_timestamp.state is FieldState.STATED
    ]
    midnight = [value for value in stated if value is not None and "00:00:00" in value]
    timed = [value for value in stated if value is not None and "00:00:00" not in value]
    assert len(midnight) == 39
    assert len(timed) == 19
    assert len(midnight) + len(timed) == 58
    # Midnight is a provider-stated clock value, never an absence marker.
    assert all(len(value) == 26 for value in stated if value is not None)


# --------------------------------------------------------------------------------------
# Time semantics: no inheritance, no synthesis
# --------------------------------------------------------------------------------------


def test_organic_item_timestamp_never_inherits_the_result_datetime() -> None:
    parsed = parse_google_organic_v2(_fixture(), PARAMETERS)
    assert parsed.result_datetime.state is FieldState.STATED
    assert parsed.result_datetime.value == RESULT_DATETIME
    unstated = [
        placement
        for placement in parsed.organic_placements
        if placement.organic_item_timestamp.state is not FieldState.STATED
    ]
    assert len(unstated) == 39
    for placement in unstated:
        assert placement.organic_item_timestamp.value is None
    stated_values = {
        placement.organic_item_timestamp.value
        for placement in parsed.organic_placements
        if placement.organic_item_timestamp.state is FieldState.STATED
    }
    assert RESULT_DATETIME not in stated_values


def test_null_organic_timestamp_is_not_synthesised_from_pre_snippet() -> None:
    document = _decoded()
    placement = _organic_at(document, 4)
    assert placement["timestamp"] is None
    placement["pre_snippet"] = "Jan 1, 2020"
    parsed = _parse_v2(document)
    target = next(
        item for item in parsed.organic_placements if item.rank_absolute == 4
    )
    assert target.organic_item_timestamp.state is FieldState.JSON_NULL
    assert target.organic_item_timestamp.value is None


def test_top_story_timestamp_is_not_synthesised_from_the_relative_date() -> None:
    document = _decoded()
    stories = _first(document, "top_stories")
    child = stories["items"][0]
    assert child["date"] == "8 hours ago"
    del child["timestamp"]
    parsed = _parse_v2(document)
    first_child = parsed.top_story_groups[0].children[0]
    assert first_child.top_story_item_timestamp.state is FieldState.ABSENT
    assert first_child.top_story_item_timestamp.value is None
    # The relative date string stays raw under PF-18 and is never promoted to a clock.
    assert not hasattr(first_child, "date")


def test_absent_and_null_item_timestamps_stay_distinct_in_every_family() -> None:
    document = _decoded()
    absent_placement = _organic_at(document, 9)
    assert isinstance(absent_placement["timestamp"], str)
    del absent_placement["timestamp"]
    stories = _first(document, "top_stories")
    stories["items"][1]["timestamp"] = None
    videos = _first(document, "video")
    del videos["items"][2]["timestamp"]
    parsed = _parse_v2(document)
    states = Counter(
        placement.organic_item_timestamp.state
        for placement in parsed.organic_placements
    )
    assert states[FieldState.ABSENT] == 1
    assert states[FieldState.JSON_NULL] == 39
    assert states[FieldState.STATED] == 57
    assert parsed.top_story_groups[0].children[1].top_story_item_timestamp.state is (
        FieldState.JSON_NULL
    )
    assert parsed.video_groups[0].children[2].video_item_timestamp.state is (
        FieldState.ABSENT
    )


def test_every_item_timestamp_family_rejects_a_malformed_lexical_form() -> None:
    cases = (
        ("organic", "invalid_organic_item_timestamp"),
        ("top_stories", "invalid_top_story_item_timestamp"),
        ("video", "invalid_video_item_timestamp"),
    )
    for family, code in cases:
        document = _decoded()
        if family == "organic":
            _organic_at(document, 2)["timestamp"] = "2026-08-18T09:37:26Z"
        else:
            _first(document, family)["items"][0]["timestamp"] = "2026-08-18T09:37:26Z"
        error = _parse_v2_error(document)
        assert error.code == code
    # A syntactically valid but impossible calendar instant also fails closed.
    document = _decoded()
    _organic_at(document, 2)["timestamp"] = "2026-02-30 00:00:00 +00:00"
    assert _parse_v2_error(document).code == "invalid_organic_item_timestamp"


# --------------------------------------------------------------------------------------
# links family: absent vs json_null vs stated-empty vs stated-populated
# --------------------------------------------------------------------------------------


def test_links_absent_null_empty_and_populated_are_four_distinct_states() -> None:
    document = _decoded()
    del _organic_at(document, 8)["links"]
    _organic_at(document, 4)["links"] = []
    parsed = _parse_v2(document)
    by_rank = {
        placement.rank_absolute: placement for placement in parsed.organic_placements
    }
    assert by_rank[8].links_state is FieldState.ABSENT
    assert by_rank[8].links_count is None
    assert by_rank[8].sitelinks == ()
    assert by_rank[4].links_state is FieldState.STATED
    assert by_rank[4].links_count == 0
    assert by_rank[4].sitelinks == ()
    assert by_rank[5].links_state is FieldState.JSON_NULL
    assert by_rank[5].links_count is None
    assert by_rank[2].links_state is FieldState.STATED
    assert by_rank[2].links_count == 4
    # No-child-rows is never enough: three of these four have no sitelinks at all.
    childless = [
        placement
        for placement in (by_rank[8], by_rank[4], by_rank[5])
        if not placement.sitelinks
    ]
    assert len(childless) == 3
    assert len({placement.links_state for placement in childless}) == 3


def test_sitelink_child_requires_title_url_and_domain() -> None:
    for key, code in (
        ("title", "wrong_type"),
        ("url", "wrong_type"),
        ("domain", "wrong_type"),
    ):
        document = _decoded()
        del _organic_at(document, 2)["links"][0][key]
        assert _parse_v2_error(document).code == code
    document = _decoded()
    _organic_at(document, 2)["links"][0]["url"] = "not-a-url"
    assert _parse_v2_error(document).code == "invalid_url"
    document = _decoded()
    _organic_at(document, 2)["links"][0]["type"] = "sitelink_element"
    assert _parse_v2_error(document).code == "unknown_enum"


def test_sitelink_description_null_is_not_an_empty_string() -> None:
    document = _decoded()
    _organic_at(document, 2)["links"][1]["description"] = ""
    parsed = _parse_v2(document)
    stated = next(
        placement
        for placement in parsed.organic_placements
        if placement.rank_absolute == 2
    )
    assert stated.sitelinks[0].description.state is FieldState.JSON_NULL
    assert stated.sitelinks[0].description.value is None
    assert stated.sitelinks[1].description.state is FieldState.STATED
    assert stated.sitelinks[1].description.value == ""


# --------------------------------------------------------------------------------------
# Reorder, duplicates, and parent scoping
# --------------------------------------------------------------------------------------


def test_top_story_reorder_keeps_identity_and_moves_occurrence_indexes() -> None:
    baseline = parse_google_organic_v2(_fixture(), PARAMETERS)
    original = baseline.top_story_groups[0].children
    document = _decoded()
    stories = _first(document, "top_stories")
    stories["items"] = list(reversed(stories["items"]))
    parsed = _parse_v2(document)
    reordered = parsed.top_story_groups[0].children
    assert {child.url for child in reordered} == {child.url for child in original}
    assert [child.child_index for child in reordered] == [0, 1, 2, 3]
    assert reordered[0].url == original[3].url
    assert reordered[3].url == original[0].url
    # The parent placement, which is the semantic scope, is untouched by child order.
    assert parsed.top_story_groups[0].rank_absolute == 6


def test_video_reorder_keeps_identity_and_moves_occurrence_indexes() -> None:
    baseline = parse_google_organic_v2(_fixture(), PARAMETERS)
    original = baseline.video_groups[0].children
    document = _decoded()
    videos = _first(document, "video")
    videos["items"] = [videos["items"][2], videos["items"][0], videos["items"][1]]
    parsed = _parse_v2(document)
    reordered = parsed.video_groups[0].children
    assert {child.url for child in reordered} == {child.url for child in original}
    assert [child.child_index for child in reordered] == [0, 1, 2]
    assert reordered[0].url == original[2].url
    assert parsed.video_groups[0].rank_absolute == 7


def test_agreeing_duplicate_child_urls_survive_as_separate_occurrences() -> None:
    document = _decoded()
    stories = _first(document, "top_stories")
    stories["items"].append(copy.deepcopy(stories["items"][0]))
    parsed = _parse_v2(document)
    children = parsed.top_story_groups[0].children
    assert len(children) == 5
    repeated = [child for child in children if child.url == CLARION_URL]
    assert [child.child_index for child in repeated] == [0, 4]
    assert repeated[0].source == repeated[1].source
    assert repeated[0].top_story_item_timestamp == repeated[1].top_story_item_timestamp


@pytest.mark.parametrize(
    ("family", "mutate"),
    (
        ("top_stories", "source"),
        ("top_stories", "domain"),
        ("top_stories", "title"),
        ("top_stories", "timestamp"),
        ("video", "source"),
        ("video", "title"),
        ("video", "timestamp"),
    ),
)
def test_conflicting_duplicate_child_content_fails_the_whole_parse(
    family: str, mutate: str
) -> None:
    document = _decoded()
    parent = _first(document, family)
    clone = copy.deepcopy(parent["items"][0])
    clone[mutate] = (
        "2010-01-01 00:00:00 +00:00" if mutate == "timestamp" else "conflicting"
    )
    parent["items"].append(clone)
    error = _parse_v2_error(document)
    assert error.code == "duplicate_child_disagreement"


def test_conflicting_duplicate_sitelink_content_fails_the_whole_parse() -> None:
    document = _decoded()
    placement = _organic_at(document, 2)
    clone = copy.deepcopy(placement["links"][0])
    clone["title"] = "Conflicting anchor"
    placement["links"].append(clone)
    assert _parse_v2_error(document).code == "duplicate_child_disagreement"


def test_a_second_top_stories_parent_scopes_its_children_independently() -> None:
    document = _decoded()
    stories = _first(document, "top_stories")
    clone = copy.deepcopy(stories)
    clone["position"] = "right"
    clone["rank_group"] = 1
    clone["rank_absolute"] = 1
    clone["items"] = [copy.deepcopy(stories["items"][0])]
    _set_items(document, [*_items(document), clone])
    parsed = _parse_v2(document)
    assert len(parsed.top_story_groups) == 2
    left = next(group for group in parsed.top_story_groups if group.position == "left")
    right = next(group for group in parsed.top_story_groups if group.position == "right")
    assert len(left.children) == 4
    assert len(right.children) == 1
    # The same child URL under two parents is two distinct semantic facts.
    assert right.children[0].url == left.children[0].url
    assert (left.page, left.rank_absolute) != (right.page, right.rank_absolute)


def test_a_second_video_parent_scopes_its_children_independently() -> None:
    document = _decoded()
    videos = _first(document, "video")
    clone = copy.deepcopy(videos)
    clone["position"] = "right"
    clone["rank_group"] = 1
    clone["rank_absolute"] = 1
    clone["items"] = [copy.deepcopy(videos["items"][1])]
    _set_items(document, [*_items(document), clone])
    parsed = _parse_v2(document)
    assert len(parsed.video_groups) == 2
    right = next(group for group in parsed.video_groups if group.position == "right")
    assert len(right.children) == 1
    assert right.children[0].url == videos["items"][1]["url"]


def test_the_same_url_under_top_stories_and_an_organic_result_stays_separate() -> None:
    document = _decoded()
    stories = _first(document, "top_stories")
    stories["items"][0]["url"] = WIKI_URL
    parsed = _parse_v2(document)
    organic = next(
        placement
        for placement in parsed.organic_placements
        if placement.rank_absolute == 2
    )
    assert organic.url == WIKI_URL
    assert parsed.top_story_groups[0].children[0].url == WIKI_URL
    # Different kinds, different parents; no cross-kind collapse happens in the IR.
    assert organic.page == parsed.top_story_groups[0].page
    assert organic.rank_absolute != parsed.top_story_groups[0].rank_absolute


# --------------------------------------------------------------------------------------
# Parser-v2 fail-closed behaviour
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("family", ("top_stories", "video"))
def test_child_array_null_or_absent_fails_closed(family: str) -> None:
    document = _decoded()
    _first(document, family)["items"] = None
    assert _parse_v2_error(document).code == "wrong_type"
    document = _decoded()
    del _first(document, family)["items"]
    assert _parse_v2_error(document).code == "missing_field"
    document = _decoded()
    _first(document, family)["items"] = {"type": "bogus"}
    assert _parse_v2_error(document).code == "wrong_type"


@pytest.mark.parametrize(
    ("family", "wrong_type"),
    (("top_stories", "video_element"), ("video", "top_stories_element")),
)
def test_wrong_child_element_type_fails_closed(family: str, wrong_type: str) -> None:
    document = _decoded()
    _first(document, family)["items"][0]["type"] = wrong_type
    assert _parse_v2_error(document).code == "unknown_enum"


def test_top_story_child_requires_source_domain_title_and_url() -> None:
    for key in ("source", "domain", "title"):
        document = _decoded()
        del _first(document, "top_stories")["items"][0][key]
        assert _parse_v2_error(document).code == "wrong_type"
    document = _decoded()
    _first(document, "top_stories")["items"][0]["url"] = "javascript:alert(1)"
    assert _parse_v2_error(document).code == "invalid_url"


def test_video_child_requires_source_title_and_url() -> None:
    for key in ("source", "title"):
        document = _decoded()
        del _first(document, "video")["items"][0][key]
        assert _parse_v2_error(document).code == "wrong_type"
    document = _decoded()
    _first(document, "video")["items"][0]["url"] = "ftp://example.test/clip"
    assert _parse_v2_error(document).code == "invalid_url"


def test_populated_related_result_is_known_parser_version_drift() -> None:
    document = _decoded()
    _organic_at(document, 2)["related_result"] = [{"type": "organic"}]
    error = _parse_v2_error(document)
    assert error.code == "parser_version_drift"
    assert error.path.endswith("/related_result")
    # Parser-v1 keeps its accepted behaviour for exactly the same bytes.
    parsed_v1 = parse_google_organic(_encode(document), PARAMETERS)
    assert parsed_v1.outcome is ParseClassification.ADMITTED
    assert len(parsed_v1.organic_placements) == 97


def test_json_null_related_result_stays_admitted() -> None:
    parsed = parse_google_organic_v2(_fixture(), PARAMETERS)
    assert parsed.outcome is ParseClassification.ADMITTED


def test_unknown_child_fields_are_diagnostics_not_failures() -> None:
    document = _decoded()
    _first(document, "top_stories")["items"][0]["publisher_rank"] = 3
    _first(document, "video")["items"][0]["domain"] = "www.facebook.com"
    _organic_at(document, 2)["links"][0]["tracking_id"] = "abc"
    parsed = _parse_v2(document)
    assert parsed.outcome is ParseClassification.ADMITTED
    codes = {item.code for item in parsed.diagnostics}
    assert codes == {"unknown_extension_field"}
    paths = {item.path for item in parsed.diagnostics}
    assert any(path.endswith("/publisher_rank") for path in paths)
    assert any(path.endswith("/domain") for path in paths)
    assert any(path.endswith("/tracking_id") for path in paths)
    # An additive provider `domain` on a video child is recorded, never modelled.
    video_child = parsed.video_groups[0].children[0]
    assert not hasattr(video_child, "domain")


def test_v2_keeps_every_accepted_v1_envelope_and_reconciliation_rule() -> None:
    document = _decoded()
    document["tasks"][0]["result"][0]["keyword"] = "unrelated subject"
    assert _parse_v2_error(document).code == "reconciliation_failed"
    document = _decoded()
    document["tasks"][0]["result"][0]["items_count"] = 110
    assert _parse_v2_error(document).code == "count_mismatch"
    document = _decoded()
    document["tasks"][0]["result"][0]["location_code"] = 2826
    assert _parse_v2_error(document).code == "reconciliation_failed"


def test_v1_and_v2_agree_on_every_shared_family_for_the_frozen_body() -> None:
    first = parse_google_organic(_fixture(), PARAMETERS)
    second = parse_google_organic_v2(_fixture(), PARAMETERS)
    assert first.feature_placements == second.feature_placements
    assert first.ai_overview == second.ai_overview
    assert first.ai_overview_sources == second.ai_overview_sources
    assert first.related_questions == second.related_questions
    assert first.related_queries == second.related_queries
    assert first.item_types == second.item_types
    assert first.result_datetime == second.result_datetime
    assert first.items_count == second.items_count
    assert len(first.organic_placements) == len(second.organic_placements)
    for old, new in zip(first.organic_placements, second.organic_placements, strict=True):
        assert (old.url, old.domain, old.title) == (new.url, new.domain, new.title)
        assert (old.page, old.position, old.rank_group, old.rank_absolute) == (
            new.page,
            new.position,
            new.rank_group,
            new.rank_absolute,
        )
        assert old.description == new.description
        assert old.website_name == new.website_name
        # Only v2 carries the item timestamp and links-family testimony.
        assert not hasattr(old, "organic_item_timestamp")
        assert not hasattr(old, "links_state")
