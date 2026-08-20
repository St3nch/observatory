"""AI-04: Search Mentions strict parser and AI-03 conformance fixture."""

from __future__ import annotations

import copy
import hashlib
import inspect
import json
import socket
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from observatory.capture_event import (
    MENTIONS_ADAPTER_CONTRACT,
    ORGANIC_ADAPTER_CONTRACT,
    PAID_ADAPTER_CONTRACT,
)
from observatory.dataforseo_ai_optimization_search_mentions import (
    SearchMentionsParseError,
    parse_search_mentions,
)
from observatory.dataforseo_google_organic import parse_google_organic
from observatory.dataforseo_keyword_overview import (
    FieldState,
    ParseClassification,
    parse_keyword_overview,
)

FIXTURE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_ai_optimization_search_mentions_ai03.json"
)
KO_FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_keyword_overview_pf03.json"
)
ORGANIC_FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_google_organic_pf10.json"
)
AI03_BODY_BYTES = 48466
AI03_BODY_SHA256 = "8b3cd0fb0c9fa23c102696bfe6b7212396c0f7c110e9ca8ca5b8ee5af182e80a"
KO_BODY_SHA256 = "d91fdc7ab8acf429f0ff9c00bd7cdb725be1ba9585481af35d14f7c4e79a6d1c"
ORGANIC_BODY_SHA256 = "7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f"

KEYWORD = "generative engine optimization"
QUESTIONS = (
    "enception",
    "mathematical artificial intelligence",
    "search engine optimized",
    "seos",
    "engine optimization service",
)
VOLUMES = (368000, 201000, 135000, 110000, 110000)
SOURCE_COUNTS = (7, 14, 13, 4, 10)
DISAGREEING_ITEMS = (2, 3, 4)

PARAMETERS: dict[str, object] = {
    "contract": MENTIONS_ADAPTER_CONTRACT,
    "language_code": "en",
    "limit": 5,
    "location_code": 2840,
    "offset": 0,
    "platform": "google",
    "target": [
        {
            "keyword": KEYWORD,
            "match_type": "word_match",
            "search_filter": "include",
            "search_scope": ["answer"],
        }
    ],
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


def _fixture() -> bytes:
    return FIXTURE_PATH.read_bytes()


def _parse(body: bytes | None = None, parameters: dict[str, object] | None = None) -> Any:
    return parse_search_mentions(body if body is not None else _fixture(), parameters or PARAMETERS)


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
    if isinstance(value, float):
        return repr(value).encode()
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


def test_frozen_fixture_independent_sha256_and_length() -> None:
    raw = _fixture()
    assert len(raw) == AI03_BODY_BYTES
    assert hashlib.sha256(raw).hexdigest() == AI03_BODY_SHA256
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert not raw.endswith(b"\n")


def test_parser_signature_has_no_http_or_transport_input() -> None:
    names = tuple(inspect.signature(parse_search_mentions).parameters)
    assert names == ("body", "parameters")


def test_golden_parse_preserves_request_result_distinction() -> None:
    parsed = _parse()
    assert parsed.outcome is ParseClassification.ADMITTED
    assert parsed.request.keyword == KEYWORD
    assert parsed.request.match_type == "word_match"
    assert parsed.request.search_filter == "include"
    assert parsed.request.search_scope == ("answer",)
    assert parsed.request.platform == "google"
    assert parsed.request.location_code == 2840
    assert parsed.request.language_code == "en"
    assert parsed.request.limit == 5
    assert parsed.request.offset == 0
    assert parsed.status_code == 20000
    assert parsed.task_status_code == 20000
    assert parsed.cost == Decimal("0.105")
    assert parsed.task_cost == Decimal("0.105")
    assert isinstance(parsed.cost, Decimal)
    assert parsed.total_count == 3055
    assert parsed.offset == 0
    assert parsed.items_count == 5
    assert len(parsed.items) == 5
    assert parsed.search_after_token is not None
    assert parsed.search_after_token.state is FieldState.STATED
    token = parsed.search_after_token.value
    assert isinstance(token, str)
    assert len(token) == 628
    assert token == _result(_decoded())["search_after_token"]
    assert parsed.echo is not None
    assert parsed.echo.api == "ai_optimization"
    assert parsed.echo.function == "search_mentions"
    assert [item.question for item in parsed.items] == list(QUESTIONS)
    assert KEYWORD not in parsed.items[0].question
    assert all(item.question != KEYWORD for item in parsed.items)
    assert [item.ai_search_volume for item in parsed.items] == list(VOLUMES)
    assert tuple(len(item.sources) for item in parsed.items) == SOURCE_COUNTS
    assert sum(len(item.sources) for item in parsed.items) == 48
    assert all(len(item.monthly_searches) == 12 for item in parsed.items)
    for index in DISAGREEING_ITEMS:
        newest = parsed.items[index].monthly_searches[0].search_volume
        assert parsed.items[index].ai_search_volume != newest
    for item in parsed.items:
        assert item.search_results.state is FieldState.JSON_NULL
        assert item.brand_entities.state is FieldState.JSON_NULL
        assert item.fan_out_queries.state is FieldState.JSON_NULL
        assert item.platform == "google"
        assert item.model_name == "google_ai_overview"
        assert item.location_code == 2840
        assert item.language_code == "en"
        assert item.is_web_search_based is True
        assert "ő" in parsed.items[1].answer or "—" in parsed.items[1].answer
        for source in item.sources:
            assert source.publication_date.state is FieldState.JSON_NULL
            assert source.thumbnail.state is FieldState.JSON_NULL
            assert source.markdown.state is FieldState.JSON_NULL
    urls = [source.url for item in parsed.items for source in item.sources]
    fixture_urls = [
        source["url"]
        for item in _result(_decoded())["items"]
        for source in item["sources"]
    ]
    assert urls == fixture_urls
    assert len(urls) == 48
    assert len(set(urls)) == 48
    assert any("#" in url for url in urls)
    assert [source.rank for source in parsed.items[0].sources] == list(range(1, 8))
    assert all(item.sources[0].rank == 1 for item in parsed.items)
    windows = [
        (item.monthly_searches[0].year, item.monthly_searches[0].month)
        for item in parsed.items
    ]
    assert len(set(windows)) > 1
    assert parsed.duration.endswith("sec.")
    assert parsed.task_duration is not None and parsed.task_duration.endswith("sec.")


def test_questions_are_answer_scope_hits_not_merely_unequal_to_keyword() -> None:
    parsed = _parse()
    words = KEYWORD.split()
    assert all(word in parsed.items[0].answer.lower() for word in words)
    assert not any(word in parsed.items[0].question.lower() for word in words)
    assert parsed.request.keyword == KEYWORD


def test_source_reorder_preserves_url_rank_pairs() -> None:
    parsed = _parse()
    original = [(source.url, source.rank) for source in parsed.items[0].sources]
    indexed = [
        (source.url, index + 1) for index, source in enumerate(parsed.items[0].sources)
    ]
    assert original == indexed
    document = _decoded()
    sources = _result(document)["items"][0]["sources"]
    _result(document)["items"][0]["sources"] = list(reversed(sources))
    reordered = _parse(_encode(document))
    pairs = [(source.url, source.rank) for source in reordered.items[0].sources]
    assert pairs == list(reversed(original))
    reindexed = [
        (source.url, index + 1) for index, source in enumerate(reordered.items[0].sources)
    ]
    assert pairs != reindexed


def test_markdown_links_do_not_become_sources() -> None:
    parsed = _parse()
    original_urls = [source.url for source in parsed.items[0].sources]
    document = _decoded()
    item = _result(document)["items"][0]
    extra = "https://api.dataforseo.com/llm_m/cdn/i/not-a-source"
    item["answer"] = item["answer"] + f" [x]({extra})"
    mutated = _parse(_encode(document))
    assert [source.url for source in mutated.items[0].sources] == original_urls
    assert extra not in [source.url for source in mutated.items[0].sources]
    assert extra in mutated.items[0].answer


@pytest.mark.parametrize("form", [b"0.105", b"0.1050", b"1.05e-1"])
def test_cost_decimal_value_ignores_numeral_spelling(form: bytes) -> None:
    raw = _fixture()
    mutated = raw.replace(b'"cost":0.105', b'"cost":' + form, 2)
    parsed = _parse(mutated)
    assert parsed.cost == Decimal("0.105")
    assert parsed.task_cost == Decimal("0.105")
    assert type(parsed.cost) is Decimal


def test_integer_json_cost_is_decimal() -> None:
    parsed = _parse(_fixture().replace(b'"cost":0.105', b'"cost":1', 1))
    assert parsed.cost == Decimal(1)
    assert type(parsed.cost) is Decimal


def test_high_precision_cost_does_not_use_binary_float() -> None:
    raw = _fixture().replace(b'"cost":0.105', b'"cost":0.10500000000000001', 1)
    parsed = _parse(raw)
    assert parsed.cost != Decimal("0.105")
    assert type(parsed.cost) is Decimal


def test_echo_disagreement_does_not_replace_attempt_context() -> None:
    document = _decoded()
    document["tasks"][0]["data"]["language_code"] = "de"
    document["tasks"][0]["data"]["target"][0]["keyword"] = "other keyword"
    parsed = _parse(_encode(document))
    assert parsed.request.keyword == KEYWORD
    assert parsed.request.language_code == "en"
    assert parsed.echo is not None
    assert parsed.echo.language_code == "de"
    assert parsed.echo.target[0].keyword == "other keyword"
    assert [item.question for item in parsed.items] == list(QUESTIONS)


def test_duplicate_questions_and_urls_remain_distinct() -> None:
    document = _decoded()
    items = _result(document)["items"]
    clone = copy.deepcopy(items[0])
    clone["sources"][1]["url"] = clone["sources"][0]["url"]
    items.append(clone)
    _result(document)["items_count"] = 6
    _result(document)["total_count"] = 3055
    parsed = _parse(_encode(document))
    assert len(parsed.items) == 6
    assert parsed.items[0].question == parsed.items[5].question == QUESTIONS[0]
    assert parsed.items[0] is not parsed.items[5]
    urls = [source.url for source in parsed.items[5].sources]
    assert urls[0] == urls[1]
    assert len(parsed.items[5].sources) == 7


def test_empty_items_with_zero_count_is_admitted() -> None:
    document = _decoded()
    _result(document)["items"] = []
    _result(document)["items_count"] = 0
    _result(document)["total_count"] = 0
    zero = _parse(_encode(document))
    assert zero.outcome is ParseClassification.ADMITTED
    assert zero.items == ()
    assert zero.items_count == 0
    document = _decoded()
    _result(document)["items"] = []
    _result(document)["items_count"] = 0
    _result(document)["total_count"] = 12
    truncated = _parse(_encode(document))
    assert truncated.outcome is ParseClassification.ADMITTED
    assert truncated.total_count == 12
    assert truncated.items == ()


def test_empty_monthly_array_is_stated_empty_series() -> None:
    document = _decoded()
    _result(document)["items"][0]["monthly_searches"] = []
    parsed = _parse(_encode(document))
    assert parsed.items[0].monthly_searches == ()


def test_unknown_result_and_item_fields_fail_closed() -> None:
    document = _decoded()
    _result(document)["current_offset"] = 0
    with pytest.raises(SearchMentionsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    del _result(document)["offset"]
    _result(document)["current_offset"] = 0
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][0]["extra"] = True
    with pytest.raises(SearchMentionsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    document["unexpected"] = 1
    with pytest.raises(SearchMentionsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["unexpected"] = 1
    with pytest.raises(SearchMentionsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["data"]["unexpected"] = 1
    with pytest.raises(
        SearchMentionsParseError, match="unknown_field at /tasks/0/data/unexpected"
    ):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["data"]["target"][0]["unexpected"] = 1
    with pytest.raises(
        SearchMentionsParseError,
        match="unknown_field at /tasks/0/data/target/0/unexpected",
    ):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][0]["sources"][0]["unexpected"] = 1
    with pytest.raises(SearchMentionsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][0]["monthly_searches"][0]["unexpected"] = 1
    with pytest.raises(SearchMentionsParseError, match="unknown_field"):
        _parse(_encode(document))


def test_duplicate_json_member_invalid_utf8_bom_trailing_and_nonfinite() -> None:
    raw = _fixture()
    duplicated = raw.replace(b'"status_code":20000', b'"status_code":20000,"status_code":20000', 1)
    with pytest.raises(SearchMentionsParseError, match="duplicate_member"):
        _parse(duplicated)
    with pytest.raises(SearchMentionsParseError, match="invalid_utf8"):
        _parse(b"\xff\xfe{" + raw)
    with pytest.raises(SearchMentionsParseError, match="utf8_bom"):
        _parse(b"\xef\xbb\xbf" + raw)
    with pytest.raises(SearchMentionsParseError, match="trailing_data"):
        _parse(raw + b"  true")
    with pytest.raises(SearchMentionsParseError, match="non_finite"):
        _parse(raw.replace(b'"cost":0.105', b'"cost":NaN', 1))
    with pytest.raises(SearchMentionsParseError, match="non_finite"):
        _parse(raw.replace(b'"cost":0.105', b'"cost":Infinity', 1))


def test_missing_known_fields_fail() -> None:
    document = _decoded()
    del document["status_code"]
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))
    document = _decoded()
    del _result(document)["items"]
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))
    document = _decoded()
    del _result(document)["search_after_token"]
    with pytest.raises(SearchMentionsParseError, match="missing_field"):
        _parse(_encode(document))
    document = _decoded()
    del _result(document)["items"][0]["question"]
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))
    document = _decoded()
    del _result(document)["items"][0]["sources"][0]["url"]
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))


def test_provider_error_and_inconsistent_status() -> None:
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 1
    error = _parse(_encode(document))
    assert error.outcome is ParseClassification.PROVIDER_ERROR
    assert error.items == ()
    assert error.request.keyword == KEYWORD
    assert error.tasks_error == 1
    document = _decoded()
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 1
    mismatch = _parse(_encode(document))
    assert mismatch.outcome is ParseClassification.PROVIDER_ERROR
    assert mismatch.tasks_error == 1
    document = _decoded()
    document["status_code"] = 40100
    with pytest.raises(SearchMentionsParseError, match="inconsistent_status"):
        _parse(_encode(document))


def test_wrong_tasks_error_fails_on_success_and_provider_error() -> None:
    document = _decoded()
    document["tasks_error"] = 1
    with pytest.raises(SearchMentionsParseError, match="count_mismatch"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 0
    with pytest.raises(SearchMentionsParseError, match="count_mismatch"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 2
    with pytest.raises(SearchMentionsParseError, match="count_mismatch"):
        _parse(_encode(document))


def test_negative_result_count_fails_including_provider_error() -> None:
    document = _decoded()
    document["tasks"][0]["result_count"] = -1
    with pytest.raises(SearchMentionsParseError, match="invalid_number"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 1
    document["tasks"][0]["result_count"] = -1
    with pytest.raises(SearchMentionsParseError, match="invalid_number"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result_count"] = True
    with pytest.raises(SearchMentionsParseError, match="wrong_type"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 1
    document["tasks"][0]["result_count"] = 1.0
    with pytest.raises(SearchMentionsParseError, match="wrong_type"):
        _parse(_encode(document))


def test_task_and_result_count_errors() -> None:
    document = _decoded()
    document["tasks"].append(copy.deepcopy(document["tasks"][0]))
    document["tasks_count"] = 2
    with pytest.raises(SearchMentionsParseError, match="tasks_length"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result"].append(copy.deepcopy(_result(document)))
    document["tasks"][0]["result_count"] = 2
    with pytest.raises(SearchMentionsParseError, match="result_length"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks_count"] = 2
    with pytest.raises(SearchMentionsParseError, match="count_mismatch"):
        _parse(_encode(document))


def test_items_null_wrong_type_and_count_mismatches() -> None:
    document = _decoded()
    _result(document)["items"] = None
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"] = {}
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items_count"] = 4
    with pytest.raises(SearchMentionsParseError, match="count_mismatch"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["total_count"] = 3
    with pytest.raises(SearchMentionsParseError, match="count_mismatch"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items_count"] = True
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items_count"] = 5.0
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["offset"] = 1
    with pytest.raises(SearchMentionsParseError, match="offset_mismatch"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["total_count"] = -1
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))


def test_continuation_null_empty_and_wrong_type() -> None:
    document = _decoded()
    _result(document)["search_after_token"] = None
    parsed = _parse(_encode(document))
    assert parsed.search_after_token is not None
    assert parsed.search_after_token.state is FieldState.JSON_NULL
    document = _decoded()
    _result(document)["search_after_token"] = ""
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["search_after_token"] = 12
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))


def test_item_context_mismatch_fails() -> None:
    document = _decoded()
    _result(document)["items"][0]["platform"] = "chat_gpt"
    with pytest.raises(SearchMentionsParseError, match="context_mismatch"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][1]["location_code"] = 2841
    with pytest.raises(SearchMentionsParseError, match="context_mismatch"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][2]["language_code"] = "de"
    with pytest.raises(SearchMentionsParseError, match="context_mismatch"):
        _parse(_encode(document))


@pytest.mark.parametrize("rank", [0, -1, True, 1.5])
def test_invalid_source_ranks_fail(rank: object) -> None:
    document = _decoded()
    _result(document)["items"][0]["sources"][0]["rank"] = rank
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))


def test_duplicate_and_gap_ranks_fail() -> None:
    document = _decoded()
    _result(document)["items"][0]["sources"][1]["rank"] = 1
    with pytest.raises(SearchMentionsParseError, match="invalid_rank"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][0]["sources"][2]["rank"] = 9
    with pytest.raises(SearchMentionsParseError, match="invalid_rank"):
        _parse(_encode(document))


def test_malformed_url_and_query_fragment_preservation() -> None:
    document = _decoded()
    _result(document)["items"][0]["sources"][0]["url"] = "not-a-url"
    with pytest.raises(SearchMentionsParseError, match="invalid_url"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][0]["sources"][0]["url"] = "ftp://host.example/path"
    with pytest.raises(SearchMentionsParseError, match="invalid_url"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][0]["sources"][0]["url"] = "https://example.com/path with space"
    with pytest.raises(SearchMentionsParseError, match="invalid_url"):
        _parse(_encode(document))
    parsed = _parse()
    urls = [source.url for item in parsed.items for source in item.sources]
    assert any("?" in url or "&" in url for url in urls)
    assert any("watch" in url or "shorts" in url for url in urls)
    fixture_urls = [
        source["url"]
        for item in _result(_decoded())["items"]
        for source in item["sources"]
    ]
    assert urls == fixture_urls


def test_google_null_item_fields_reject_non_null() -> None:
    for key in ("search_results", "brand_entities", "fan_out_queries"):
        document = _decoded()
        _result(document)["items"][0][key] = []
        with pytest.raises(SearchMentionsParseError, match="google_null_drift"):
            _parse(_encode(document))


def test_source_optional_fields_null_string_missing_and_wrong_type() -> None:
    document = _decoded()
    _result(document)["items"][0]["sources"][0]["publication_date"] = "not-a-clock"
    parsed = _parse(_encode(document))
    field = parsed.items[0].sources[0].publication_date
    assert field.state is FieldState.STATED
    assert field.value == "not-a-clock"
    document = _decoded()
    del _result(document)["items"][0]["sources"][0]["thumbnail"]
    with pytest.raises(SearchMentionsParseError, match="missing_field"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][0]["sources"][0]["markdown"] = {"x": 1}
    with pytest.raises(SearchMentionsParseError, match="wrong_type"):
        _parse(_encode(document))


def test_monthly_reorder_duplicate_invalid_and_null() -> None:
    parsed = _parse()
    original = [
        (point.year, point.month, point.search_volume)
        for point in parsed.items[1].monthly_searches
    ]
    document = _decoded()
    points = _result(document)["items"][1]["monthly_searches"]
    _result(document)["items"][1]["monthly_searches"] = list(reversed(points))
    reordered = _parse(_encode(document))
    pairs = [
        (point.year, point.month, point.search_volume)
        for point in reordered.items[1].monthly_searches
    ]
    assert pairs == list(reversed(original))
    document = _decoded()
    _result(document)["items"][1]["monthly_searches"][1] = copy.deepcopy(points[0])
    with pytest.raises(SearchMentionsParseError, match="duplicate_period"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][1]["monthly_searches"][0]["month"] = 13
    with pytest.raises(SearchMentionsParseError, match="invalid_period"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][1]["monthly_searches"][0]["month"] = 0
    with pytest.raises(SearchMentionsParseError, match="invalid_period"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][1]["monthly_searches"][0]["search_volume"] = -1
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][1]["monthly_searches"] = None
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))
    document = _decoded()
    del _result(document)["items"][1]["monthly_searches"]
    with pytest.raises(SearchMentionsParseError, match="missing_field"):
        _parse(_encode(document))


def test_current_volume_zero_and_wrong_type() -> None:
    document = _decoded()
    _result(document)["items"][0]["ai_search_volume"] = 0
    parsed = _parse(_encode(document))
    assert parsed.items[0].ai_search_volume == 0
    document = _decoded()
    _result(document)["items"][0]["ai_search_volume"] = True
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))


def test_timestamp_failures() -> None:
    document = _decoded()
    _result(document)["items"][0]["first_response_at"] = "2026-01-27T03:48:11Z"
    with pytest.raises(SearchMentionsParseError, match="invalid_time"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][0]["first_response_at"] = "2026-02-30 03:48:11 +00:00"
    with pytest.raises(SearchMentionsParseError, match="invalid_time"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][0]["last_response_at"] = "2026-01-27 03:48:11 +01:00"
    with pytest.raises(SearchMentionsParseError, match="invalid_time"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"][1]["last_response_at"] = "2025-01-01 00:00:00 +00:00"
    with pytest.raises(SearchMentionsParseError, match="invalid_time"):
        _parse(_encode(document))


def test_web_search_boolean() -> None:
    document = _decoded()
    _result(document)["items"][0]["is_web_search_based"] = False
    parsed = _parse(_encode(document))
    assert parsed.items[0].is_web_search_based is False
    document = _decoded()
    _result(document)["items"][0]["is_web_search_based"] = "true"
    with pytest.raises(SearchMentionsParseError):
        _parse(_encode(document))


def test_existing_fixtures_and_parsers_unchanged() -> None:
    assert hashlib.sha256(KO_FIXTURE.read_bytes()).hexdigest() == KO_BODY_SHA256
    assert hashlib.sha256(ORGANIC_FIXTURE.read_bytes()).hexdigest() == ORGANIC_BODY_SHA256
    ko = parse_keyword_overview(
        KO_FIXTURE.read_bytes(),
        {
            "contract": PAID_ADAPTER_CONTRACT,
            "include_clickstream_data": False,
            "include_serp_info": False,
            "keywords": [
                "seo api",
                "keyword research",
                "local seo",
                "generative engine optimization",
                "ai search optimization",
            ],
            "language_code": "en",
            "location_code": 2840,
        },
    )
    assert ko.outcome is ParseClassification.ADMITTED
    organic = parse_google_organic(
        ORGANIC_FIXTURE.read_bytes(),
        {
            "contract": ORGANIC_ADAPTER_CONTRACT,
            "depth": 100,
            "device": "desktop",
            "group_organic_results": True,
            "keyword": "conspiracy theories",
            "language_code": "en",
            "load_async_ai_overview": True,
            "location_code": 2840,
            "os": "windows",
        },
    )
    assert organic.status_code.value == 20000
    assert "parse_search_mentions" not in Path(
        "src/observatory/dataforseo_keyword_overview.py"
    ).read_text(encoding="utf-8")
    assert "parse_search_mentions" not in Path(
        "src/observatory/dataforseo_google_organic.py"
    ).read_text(encoding="utf-8")
