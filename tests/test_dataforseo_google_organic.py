"""PF-11: DataForSEO Google Organic strict parser and PF-10 conformance fixture."""

from __future__ import annotations

import copy
import hashlib
import json
import socket
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from observatory.capture_event import ORGANIC_ADAPTER_CONTRACT
from observatory.dataforseo_google_organic import (
    AIO_PRESENCE_KIND,
    AIO_SOURCE_KIND,
    FEATURE_PRESENCE_KIND,
    GOOGLE_ORGANIC_RECIPE,
    GOOGLE_ORGANIC_RECIPE_ID,
    ORGANIC_PLACEMENT_KIND,
    PARSER_CONTRACT,
    RELATED_QUERY_KIND,
    RELATED_QUESTION_KIND,
    GoogleOrganicParseError,
    google_organic_recipe,
    parse_google_organic,
)
from observatory.dataforseo_keyword_overview import (
    CORE_RECIPE_ID,
    FieldState,
    ParseClassification,
)
from observatory.provider_recipe import (
    IDENTITY_SCHEMA,
    IDENTITY_VERSION,
    observation_identity,
    recipe_bytes,
    recipe_derivation_version_id,
    validate_recipe,
)

FIXTURE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_google_organic_pf10.json"
)
RECIPE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_google_organic_recipe.jcs"
)
PF10_BODY_SHA256 = "7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f"
PF10_BODY_BYTES = 135722
ORGANIC_RECIPE_SHA256 = "338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde"
ORGANIC_RECIPE_BYTE_LENGTH = 2487
ACCEPTED_KO_CORE_ID = "319af798f3e0b3e5fe4579539442c4ca5d384b683e1f4bce0f7a1b3e26cd5908"

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

PBS_URL = "https://www.pbs.org/video/why-do-conspiracy-theories-spread-so-quickly-43q4k3/"
WIKI_URL = "https://en.wikipedia.org/wiki/Conspiracy_theory"
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


def _parse(body: bytes | None = None, parameters: dict[str, object] | None = None) -> Any:
    payload = body if body is not None else _fixture()
    return parse_google_organic(payload, parameters or PARAMETERS)


def _decoded() -> dict[str, Any]:
    decoder = json.JSONDecoder(parse_int=int, parse_float=Decimal)
    value, _end = decoder.raw_decode(_fixture().decode("utf-8"))
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


def _identity(kind: str, axes: dict[str, object]) -> str:
    return observation_identity(
        {
            "axes": axes,
            "observation_kind": kind,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        GOOGLE_ORGANIC_RECIPE,
    )


def _aio_source_identity(parsed: Any, source: Any) -> str:
    return _identity(
        AIO_SOURCE_KIND,
        {
            "locus": source.locus,
            "requested_keyword": parsed.requested_keyword,
            "url": source.url,
        },
    )


def _paa_identity(parsed: Any, question: Any) -> str:
    return _identity(
        RELATED_QUESTION_KIND,
        {
            "requested_keyword": parsed.requested_keyword,
            "title": question.title,
        },
    )


def _recipe_identity_axes() -> dict[str, object]:
    document = validate_recipe(GOOGLE_ORGANIC_RECIPE)
    identity = document["observation_identity"]
    assert isinstance(identity, dict)
    kind_rows = identity["kinds"]
    assert isinstance(kind_rows, list)
    return {
        item["observation_kind"]: item["axes"]
        for item in kind_rows
        if isinstance(item, dict)
    }


def test_frozen_fixture_independent_sha256_and_length() -> None:
    raw = _fixture()
    assert not raw.endswith(b"\n")
    assert len(raw) == PF10_BODY_BYTES
    assert hashlib.sha256(raw).hexdigest() == PF10_BODY_SHA256


def test_pf10_reproduces_observed_cardinalities_and_rank_axes() -> None:
    parsed = _parse()
    assert parsed.outcome is ParseClassification.ADMITTED
    assert parsed.requested_keyword == "conspiracy theories"
    assert parsed.returned_keyword.state is FieldState.STATED
    assert parsed.returned_keyword.value == "conspiracy theories"
    assert parsed.location_code == 2840
    assert parsed.language_code == "en"
    assert parsed.pages_count.state is FieldState.STATED
    assert parsed.pages_count.value == 10
    assert parsed.items_count == 111
    assert parsed.se_results_count.value == 45_000_000
    assert parsed.item_types == (
        "ai_overview",
        "organic",
        "people_also_ask",
        "top_stories",
        "video",
        "related_searches",
    )
    assert len(parsed.feature_placements) == 111
    by_type: dict[str, int] = {}
    for placement in parsed.feature_placements:
        by_type[placement.item_type] = by_type.get(placement.item_type, 0) + 1
        assert placement.page >= 1
        assert placement.position in {"left", "right"}
        assert placement.rank_group >= 1
        assert placement.rank_absolute >= 1
        assert not hasattr(placement, "google_position")
    assert by_type == {
        "ai_overview": 1,
        "organic": 97,
        "people_also_ask": 1,
        "top_stories": 1,
        "video": 1,
        "related_searches": 10,
    }
    assert len(parsed.organic_placements) == 97
    first = parsed.organic_placements[0]
    assert first.url == WIKI_URL
    assert first.domain == "en.wikipedia.org"
    assert first.title == "Conspiracy theory"
    assert first.page == 1
    assert first.position == "left"
    assert first.rank_group == 1
    assert first.rank_absolute == 2
    aio = parsed.feature_placements[0]
    assert aio.item_type == "ai_overview"
    assert aio.rank_group == 1
    assert aio.rank_absolute == 1
    assert first.rank_group == aio.rank_group
    assert first.rank_absolute != aio.rank_absolute
    assert parsed.ai_overview is not None
    assert parsed.ai_overview.asynchronous_ai_overview is False
    assert parsed.ai_overview.rank_absolute == 1
    assert parsed.result_datetime.value == "2026-08-18 17:37:36 +00:00"
    assert parsed.cost.value == Decimal("0.0155")


def test_duplicate_exact_urls_remain_distinct_placements() -> None:
    parsed = _parse()
    matches = [row for row in parsed.organic_placements if row.url == PBS_URL]
    assert len(matches) == 2
    first, second = matches
    assert first.page == 2
    assert first.rank_group == 17
    assert first.rank_absolute == 22
    assert second.page == 3
    assert second.rank_group == 27
    assert second.rank_absolute == 33
    assert (first.page, first.rank_group, first.rank_absolute) != (
        second.page,
        second.rank_group,
        second.rank_absolute,
    )
    urls = [row.url for row in parsed.organic_placements]
    assert len(urls) == 97
    assert len(set(urls)) == 87


def test_aio_top_level_and_element_loci_remain_distinct() -> None:
    parsed = _parse()
    assert parsed.ai_overview is not None
    assert len(parsed.ai_overview_sources) == 18
    top = [row for row in parsed.ai_overview_sources if row.locus == "top_level"]
    element = [row for row in parsed.ai_overview_sources if row.locus == "element"]
    assert len(top) == 7
    assert len(element) == 11
    assert all(row.element_index is None for row in top)
    assert all(row.element_index is not None for row in element)
    wiki_loci = {
        (row.locus, row.element_index)
        for row in parsed.ai_overview_sources
        if row.url == WIKI_URL
    }
    assert wiki_loci == {("top_level", None), ("element", 0), ("element", 2)}
    reddit = [
        row
        for row in parsed.ai_overview_sources
        if "reddit.com/r/AskHistory" in row.url
    ]
    assert {row.locus for row in reddit} == {"top_level", "element"}
    assert not hasattr(parsed, "markdown")
    assert not hasattr(parsed.ai_overview, "markdown")
    assert not any(hasattr(row, "text") for row in parsed.ai_overview_sources)


def test_pf10_aio_sources_map_to_fifteen_semantic_identities() -> None:
    parsed = _parse()
    assert len(parsed.ai_overview_sources) == 18
    identities = [_aio_source_identity(parsed, source) for source in parsed.ai_overview_sources]
    assert all(len(item) == 64 for item in identities)
    assert len(set(identities)) == 15
    axes = _recipe_identity_axes()[AIO_SOURCE_KIND]
    assert axes == {
        "locus": "string",
        "requested_keyword": "string",
        "url": "string",
    }
    assert "element_index" not in axes
    assert "reference_index" not in axes


def test_aio_source_identities_distinguish_locus_and_collapse_same_locus_url() -> None:
    parsed = _parse()
    wiki = [row for row in parsed.ai_overview_sources if row.url == WIKI_URL]
    assert {row.locus for row in wiki} == {"top_level", "element"}
    top_wiki = next(row for row in wiki if row.locus == "top_level")
    element_wiki = [row for row in wiki if row.locus == "element"]
    assert len(element_wiki) == 2
    top_id = _aio_source_identity(parsed, top_wiki)
    element_ids = {_aio_source_identity(parsed, row) for row in element_wiki}
    assert len(element_ids) == 1
    assert top_id not in element_ids
    britannica = [
        row
        for row in parsed.ai_overview_sources
        if row.url == "https://www.britannica.com/topic/conspiracy-theory"
        and row.locus == "element"
    ]
    youtube = [
        row
        for row in parsed.ai_overview_sources
        if row.url == "https://www.youtube.com/watch?v=cv_TKD9UHOo&vl=en&t=625"
        and row.locus == "element"
    ]
    assert len(britannica) == 2
    assert len(youtube) == 2
    assert len({_aio_source_identity(parsed, row) for row in britannica}) == 1
    assert len({_aio_source_identity(parsed, row) for row in youtube}) == 1
    top_level = [row for row in parsed.ai_overview_sources if row.locus == "top_level"]
    element_level = [row for row in parsed.ai_overview_sources if row.locus == "element"]
    assert all(row.element_index is None for row in top_level)
    assert all(row.element_index is not None for row in element_level)
    assert all(isinstance(row.reference_index, int) for row in parsed.ai_overview_sources)


def test_reordered_aio_reference_arrays_keep_semantic_identity_set() -> None:
    parsed = _parse()
    original = {_aio_source_identity(parsed, source) for source in parsed.ai_overview_sources}
    document = _decoded()
    aio = next(item for item in _items(document) if item["type"] == "ai_overview")
    aio["references"] = list(reversed(aio["references"]))
    for element in aio["items"]:
        refs = element.get("references")
        if isinstance(refs, list):
            element["references"] = list(reversed(refs))
    reordered = _parse(_encode(document))
    assert len(reordered.ai_overview_sources) == 18
    reordered_ids = {
        _aio_source_identity(reordered, source) for source in reordered.ai_overview_sources
    }
    assert reordered_ids == original
    original_order = [(source.locus, source.url) for source in parsed.ai_overview_sources]
    reordered_order = [(source.locus, source.url) for source in reordered.ai_overview_sources]
    assert reordered_order != original_order


def test_paa_types_visible_questions_and_ignores_expansion_shells() -> None:
    parsed = _parse()
    assert [row.title for row in parsed.related_questions] == list(PAA_TITLES)
    assert [row.question_index for row in parsed.related_questions] == [0, 1, 2, 3]
    parent = (1, "left", 1, 3)
    assert [
        (row.page, row.position, row.rank_group, row.rank_absolute)
        for row in parsed.related_questions
    ] == [parent] * 4
    assert all(not hasattr(row, "expanded_element") for row in parsed.related_questions)
    document = _decoded()
    paa = next(item for item in _items(document) if item["type"] == "people_also_ask")
    for question in paa["items"]:
        question["expanded_element"] = [
            {
                "type": "people_also_ask_ai_overview_expanded_element",
                "items": [{"title": "fabricated answer"}],
                "references": [],
                "asynchronous_ai_overview": False,
            }
        ]
    populated = _parse(_encode(document))
    assert [row.title for row in populated.related_questions] == list(PAA_TITLES)
    document = _decoded()
    paa = next(item for item in _items(document) if item["type"] == "people_also_ask")
    for question in paa["items"]:
        question["expanded_element"] = None
    nulled = _parse(_encode(document))
    assert [row.title for row in nulled.related_questions] == list(PAA_TITLES)
    document = _decoded()
    paa = next(item for item in _items(document) if item["type"] == "people_also_ask")
    for question in paa["items"]:
        del question["expanded_element"]
    omitted = _parse(_encode(document))
    assert [row.title for row in omitted.related_questions] == list(PAA_TITLES)
    assert omitted.diagnostics == ()


def test_pf10_paa_titles_have_four_semantic_identities() -> None:
    parsed = _parse()
    assert [row.title for row in parsed.related_questions] == list(PAA_TITLES)
    assert [row.question_index for row in parsed.related_questions] == [0, 1, 2, 3]
    identities = [_paa_identity(parsed, question) for question in parsed.related_questions]
    assert all(len(item) == 64 for item in identities)
    assert len(set(identities)) == 4
    axes = _recipe_identity_axes()[RELATED_QUESTION_KIND]
    assert axes == {
        "requested_keyword": "string",
        "title": "string",
    }
    assert "question_index" not in axes


def test_paa_identity_survives_reorder_and_second_block_with_repeated_titles() -> None:
    parsed = _parse()
    original = {_paa_identity(parsed, question) for question in parsed.related_questions}
    assert len(original) == 4
    document = _decoded()
    paa = next(item for item in _items(document) if item["type"] == "people_also_ask")
    paa["items"] = list(reversed(paa["items"]))
    reordered = _parse(_encode(document))
    assert [row.title for row in reordered.related_questions] == list(reversed(PAA_TITLES))
    assert [row.question_index for row in reordered.related_questions] == [0, 1, 2, 3]
    assert all(row.rank_absolute == 3 for row in reordered.related_questions)
    reordered_ids = {
        _paa_identity(reordered, question) for question in reordered.related_questions
    }
    assert reordered_ids == original

    document = _decoded()
    items = _items(document)
    paa = next(item for item in items if item["type"] == "people_also_ask")
    second = copy.deepcopy(paa)
    second["rank_group"] = 2
    second["rank_absolute"] = 112
    items.append(second)
    _set_items(document, items)
    doubled = _parse(_encode(document))
    assert len(doubled.related_questions) == 8
    assert [row.question_index for row in doubled.related_questions] == [0, 1, 2, 3, 0, 1, 2, 3]
    assert [row.title for row in doubled.related_questions] == list(PAA_TITLES) + list(PAA_TITLES)
    assert [row.rank_absolute for row in doubled.related_questions] == [
        3,
        3,
        3,
        3,
        112,
        112,
        112,
        112,
    ]
    assert [row.rank_group for row in doubled.related_questions] == [1, 1, 1, 1, 2, 2, 2, 2]
    identities = [_paa_identity(doubled, question) for question in doubled.related_questions]
    assert set(identities) == original
    assert len(identities) == 8
    paa_features = [
        row for row in doubled.feature_placements if row.item_type == "people_also_ask"
    ]
    assert len(paa_features) == 2
    assert {(row.rank_group, row.rank_absolute) for row in paa_features} == {(1, 3), (2, 112)}


def test_related_search_strings_dedupe_by_exact_text_first_seen() -> None:
    parsed = _parse()
    assert tuple(row.query for row in parsed.related_queries) == RELATED_QUERIES
    assert len(parsed.related_queries) == 9
    document = _decoded()
    related = [item for item in _items(document) if item["type"] == "related_searches"]
    assert len(related) == 10
    assert sum(len(item["items"]) for item in related) == 80


def test_requested_keyword_remains_subject_when_returned_differs_only_by_form() -> None:
    parameters = dict(PARAMETERS)
    parameters["keyword"] = "Conspiracy   THEORIES"
    parsed = _parse(parameters=parameters)
    assert parsed.requested_keyword == "Conspiracy   THEORIES"
    assert parsed.returned_keyword.value == "conspiracy theories"
    document = _decoded()
    document["tasks"][0]["result"][0]["keyword"] = "unrelated subject"
    with pytest.raises(GoogleOrganicParseError, match="reconciliation"):
        _parse(_encode(document))


def test_duplicate_member_unknown_field_and_missing_required() -> None:
    raw = _fixture()
    mutated = raw.replace(
        b'"se_domain":"google.com"',
        b'"se_domain":"google.com","se_domain":"bing.com"',
        1,
    )
    with pytest.raises(GoogleOrganicParseError, match="duplicate"):
        _parse(mutated)
    with pytest.raises(GoogleOrganicParseError, match="BOM"):
        _parse(b"\xef\xbb\xbf" + raw)
    with pytest.raises(GoogleOrganicParseError, match="finite"):
        _parse(raw.replace(b'"cost":0.0155', b'"cost":NaN', 1))
    document = _decoded()
    document["tasks"][0]["result"][0]["unexpected_additive"] = "x"
    parsed = _parse(_encode(document))
    assert parsed.outcome is ParseClassification.ADMITTED
    assert any(item.code == "unknown_extension_field" for item in parsed.diagnostics)
    assert parsed.items_count == 111
    document = _decoded()
    del document["tasks"][0]["result"][0]["items"][1]["rank_group"]
    with pytest.raises(GoogleOrganicParseError, match="integer"):
        _parse(_encode(document))
    document = _decoded()
    del document["tasks"][0]["result"][0]["items_count"]
    with pytest.raises(GoogleOrganicParseError, match="items_count"):
        _parse(_encode(document))


def test_wrong_rank_type_unknown_item_type_and_duplicate_ranks() -> None:
    raw = _fixture()
    with pytest.raises(GoogleOrganicParseError, match="integer"):
        _parse(raw.replace(b'"rank_absolute":2,', b'"rank_absolute":"2",', 1))
    document = _decoded()
    document["tasks"][0]["result"][0]["items"][1]["type"] = "featured_snippet"
    with pytest.raises(GoogleOrganicParseError, match="enum"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result"][0]["item_types"].append("shopping")
    with pytest.raises(GoogleOrganicParseError, match="enum"):
        _parse(_encode(document))
    document = _decoded()
    items = _items(document)
    items[2]["rank_absolute"] = items[1]["rank_absolute"]
    items[2]["position"] = items[1]["position"]
    with pytest.raises(GoogleOrganicParseError, match="duplicate"):
        _parse(_encode(document))
    document = _decoded()
    items = _items(document)
    organics = [item for item in items if item["type"] == "organic"]
    organics[1]["rank_group"] = organics[0]["rank_group"]
    organics[1]["position"] = organics[0]["position"]
    with pytest.raises(GoogleOrganicParseError, match="duplicate"):
        _parse(_encode(document))


def test_reordered_items_keep_provider_ranks_and_do_not_use_array_index() -> None:
    original = _parse()
    document = _decoded()
    items = _items(document)
    _set_items(document, list(reversed(items)))
    reordered = _parse(_encode(document))
    original_keys = {
        (
            row.item_type,
            row.page,
            row.position,
            row.rank_group,
            row.rank_absolute,
        )
        for row in original.feature_placements
    }
    reordered_keys = {
        (
            row.item_type,
            row.page,
            row.position,
            row.rank_group,
            row.rank_absolute,
        )
        for row in reordered.feature_placements
    }
    assert original_keys == reordered_keys
    wiki = next(row for row in reordered.organic_placements if row.url == WIKI_URL)
    assert wiki.rank_absolute == 2
    assert wiki.rank_group == 1
    assert reordered.feature_placements[0].item_type == "related_searches"
    assert reordered.feature_placements[0].rank_absolute == 111


def test_malformed_required_url_and_result_datetime() -> None:
    document = _decoded()
    document["tasks"][0]["result"][0]["items"][1]["url"] = "en.wikipedia.org/wiki/Conspiracy_theory"
    with pytest.raises(GoogleOrganicParseError, match="url"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result"][0]["datetime"] = "2026-08-18T17:37:36Z"
    with pytest.raises(GoogleOrganicParseError, match="timestamp"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result"][0]["datetime"] = "2026-02-30 17:37:36 +00:00"
    with pytest.raises(GoogleOrganicParseError, match="timestamp"):
        _parse(_encode(document))


def test_task_error_and_cardinality_disagreement() -> None:
    document = _decoded()
    document["tasks"][0]["status_code"] = 40102
    parsed = _parse(_encode(document))
    assert parsed.outcome is ParseClassification.PROVIDER_ERROR
    assert parsed.organic_placements == ()
    assert parsed.ai_overview is None
    document = _decoded()
    document["status_code"] = 40102
    with pytest.raises(GoogleOrganicParseError, match="inconsistent"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = 40102
    document["tasks"][0]["status_code"] = 40102
    parsed = _parse(_encode(document))
    assert parsed.outcome is ParseClassification.PROVIDER_ERROR
    document = _decoded()
    document["tasks"][0]["result"][0]["items_count"] = 110
    with pytest.raises(GoogleOrganicParseError, match="items_count"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result_count"] = 2
    with pytest.raises(GoogleOrganicParseError, match="result_count"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"].append(copy.deepcopy(document["tasks"][0]))
    document["tasks_count"] = 2
    with pytest.raises(GoogleOrganicParseError, match="exactly one task"):
        _parse(_encode(document))


def test_aio_source_locus_inconsistency_fails_closed() -> None:
    document = _decoded()
    aio = next(item for item in _items(document) if item["type"] == "ai_overview")
    aio["items"][0]["type"] = "ai_overview_reference"
    with pytest.raises(GoogleOrganicParseError, match="enum"):
        _parse(_encode(document))
    document = _decoded()
    aio = next(item for item in _items(document) if item["type"] == "ai_overview")
    aio["references"][0]["type"] = "organic"
    with pytest.raises(GoogleOrganicParseError, match="enum"):
        _parse(_encode(document))
    document = _decoded()
    aio = next(item for item in _items(document) if item["type"] == "ai_overview")
    del aio["references"]
    with pytest.raises(GoogleOrganicParseError, match="references"):
        _parse(_encode(document))
    document = _decoded()
    aio = next(item for item in _items(document) if item["type"] == "ai_overview")
    aio["references"] = None
    with pytest.raises(GoogleOrganicParseError, match="array"):
        _parse(_encode(document))
    document = _decoded()
    aio = next(item for item in _items(document) if item["type"] == "ai_overview")
    aio["items"] = None
    with pytest.raises(GoogleOrganicParseError, match="array"):
        _parse(_encode(document))
    document = _decoded()
    aio = next(item for item in _items(document) if item["type"] == "ai_overview")
    aio["references"] = []
    top_only_removed = _parse(_encode(document))
    assert all(row.locus == "element" for row in top_only_removed.ai_overview_sources)
    assert all(row.element_index is not None for row in top_only_removed.ai_overview_sources)
    document = _decoded()
    aio = next(item for item in _items(document) if item["type"] == "ai_overview")
    for element in aio["items"]:
        element["references"] = []
    element_removed = _parse(_encode(document))
    assert all(row.locus == "top_level" for row in element_removed.ai_overview_sources)
    assert all(row.element_index is None for row in element_removed.ai_overview_sources)
    assert len(element_removed.ai_overview_sources) == 7


def test_null_absence_and_decimal_variants() -> None:
    parsed = _parse()
    youtube = next(
        row
        for row in parsed.organic_placements
        if row.url == "https://www.youtube.com/watch?v=AfVjtAXg4e8"
    )
    assert youtube.description.state is FieldState.JSON_NULL
    document = _decoded()
    target = next(
        item
        for item in _items(document)
        if item.get("url") == "https://www.youtube.com/watch?v=AfVjtAXg4e8"
    )
    del target["description"]
    omitted = _parse(_encode(document))
    omitted_row = next(
        row
        for row in omitted.organic_placements
        if row.url == "https://www.youtube.com/watch?v=AfVjtAXg4e8"
    )
    assert omitted_row.description.state is FieldState.ABSENT
    document = _decoded()
    target = next(
        item
        for item in _items(document)
        if item.get("url") == WIKI_URL and item["type"] == "organic"
    )
    target["website_name"] = None
    nulled = _parse(_encode(document))
    wiki = next(row for row in nulled.organic_placements if row.url == WIKI_URL)
    assert wiki.website_name.state is FieldState.JSON_NULL
    raw = _fixture()
    precise = raw.replace(b'"cost":0.0155', b'"cost":0.015500000000000001', 1)
    high = _parse(precise)
    assert high.cost.value == Decimal("0.015500000000000001")
    assert high.cost.value != Decimal(str(float("0.015500000000000001")))


def test_context_reconciliation_does_not_substitute_attempt_subject() -> None:
    document = _decoded()
    document["tasks"][0]["result"][0]["location_code"] = 2826
    with pytest.raises(GoogleOrganicParseError, match="location_code"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result"][0]["language_code"] = "de"
    with pytest.raises(GoogleOrganicParseError, match="language_code"):
        _parse(_encode(document))


def test_google_organic_recipe_published_digest_and_kinds() -> None:
    published = RECIPE_PATH.read_bytes()
    assert not published.endswith(b"\n")
    assert len(published) == ORGANIC_RECIPE_BYTE_LENGTH
    independent = hashlib.sha256(published).hexdigest()
    assert independent == ORGANIC_RECIPE_SHA256
    assert GOOGLE_ORGANIC_RECIPE_ID == ORGANIC_RECIPE_SHA256
    assert recipe_bytes(google_organic_recipe()) == published
    assert recipe_derivation_version_id(GOOGLE_ORGANIC_RECIPE) == ORGANIC_RECIPE_SHA256
    document = validate_recipe(GOOGLE_ORGANIC_RECIPE)
    assert document["provider"] == "dataforseo"
    assert document["adapter_contract"] == ORGANIC_ADAPTER_CONTRACT
    assert document["parser_contract"] == PARSER_CONTRACT
    assert document["observation_kinds"] == [
        FEATURE_PRESENCE_KIND,
        ORGANIC_PLACEMENT_KIND,
        AIO_PRESENCE_KIND,
        AIO_SOURCE_KIND,
        RELATED_QUESTION_KIND,
        RELATED_QUERY_KIND,
    ]
    identity = document["observation_identity"]
    assert isinstance(identity, dict)
    kind_rows = identity["kinds"]
    assert isinstance(kind_rows, list)
    by_kind = {
        item["observation_kind"]: item["axes"]
        for item in kind_rows
        if isinstance(item, dict)
    }
    assert by_kind[FEATURE_PRESENCE_KIND] == {
        "item_type": "string",
        "page": "integer",
        "position": "string",
        "rank_absolute": "integer",
        "rank_group": "integer",
        "requested_keyword": "string",
    }
    assert by_kind[ORGANIC_PLACEMENT_KIND] == {
        "page": "integer",
        "position": "string",
        "rank_absolute": "integer",
        "rank_group": "integer",
        "requested_keyword": "string",
    }
    assert "url" not in by_kind[ORGANIC_PLACEMENT_KIND]
    assert by_kind[AIO_SOURCE_KIND] == {
        "locus": "string",
        "requested_keyword": "string",
        "url": "string",
    }
    assert "element_index" not in by_kind[AIO_SOURCE_KIND]
    assert "reference_index" not in by_kind[AIO_SOURCE_KIND]
    assert by_kind[RELATED_QUESTION_KIND] == {
        "requested_keyword": "string",
        "title": "string",
    }
    assert "question_index" not in by_kind[RELATED_QUESTION_KIND]
    mutated = dict(GOOGLE_ORGANIC_RECIPE)
    mutated["parser_contract"] = "dataforseo-serp-google-organic-changed-parser-v1"
    assert recipe_derivation_version_id(mutated) != ORGANIC_RECIPE_SHA256


def test_keyword_overview_identities_remain_unchanged() -> None:
    assert CORE_RECIPE_ID == ACCEPTED_KO_CORE_ID
    assert GOOGLE_ORGANIC_RECIPE_ID != ACCEPTED_KO_CORE_ID
