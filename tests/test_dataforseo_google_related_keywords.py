"""RK-03: Related Keywords strict parser and RK-02 conformance fixture."""

from __future__ import annotations

import collections
import copy
import hashlib
import json
import os
import socket
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from observatory.capture_event import (
    HISTORICAL_ADAPTER_CONTRACT,
    MENTIONS_ADAPTER_CONTRACT,
    ORGANIC_ADAPTER_CONTRACT,
    PAID_ADAPTER_CONTRACT,
    RELATED_KEYWORDS_ADAPTER_CONTRACT,
    TARGET_METRICS_ADAPTER_CONTRACT,
)
from observatory.dataforseo_ai_optimization_llm_mentions_historical import parse_historical
from observatory.dataforseo_ai_optimization_search_mentions import parse_search_mentions
from observatory.dataforseo_ai_optimization_target_metrics import parse_target_metrics
from observatory.dataforseo_google_organic import parse_google_organic
from observatory.dataforseo_google_related_keywords import (
    KeywordData,
    RelatedKeywordsIR,
    RelatedKeywordsParseError,
    RelatedKeywordsResult,
    parse_related_keywords,
)
from observatory.dataforseo_keyword_overview import (
    FieldState,
    ParseClassification,
    parse_keyword_overview,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
FIXTURE_PATH = FIXTURES / "dataforseo_google_related_keywords_rk02.json"

RK02_BODY_BYTES = 177120
RK02_BODY_SHA256 = "e128f2f81d51479237f1bd7e51feee3dfffcae4596558ebff67365f03cd1decb"

PRIOR_FIXTURES: dict[str, str] = {
    "dataforseo_keyword_overview_pf03.json": (
        "d91fdc7ab8acf429f0ff9c00bd7cdb725be1ba9585481af35d14f7c4e79a6d1c"
    ),
    "dataforseo_google_organic_pf10.json": (
        "7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f"
    ),
    "dataforseo_ai_optimization_search_mentions_ai03.json": (
        "8b3cd0fb0c9fa23c102696bfe6b7212396c0f7c110e9ca8ca5b8ee5af182e80a"
    ),
    "dataforseo_ai_optimization_target_metrics_ai09.json": (
        "7b6974704f73cff9687986a83ab14ba8ec942ccdbfde359ec7e8fde6bea8eee2"
    ),
    "dataforseo_ai_optimization_llm_mentions_historical_ai14.json": (
        "4419daf0b7076625129ab18c6bf3c83905b998c3b3332f2ba6d42c8879b50781"
    ),
}

SEED = "conspiracy theories"
ORDER_BY = "keyword_data.keyword_info.search_volume,desc"

PARAMETERS: dict[str, object] = {
    "contract": RELATED_KEYWORDS_ADAPTER_CONTRACT,
    "depth": 3,
    "ignore_synonyms": False,
    "include_clickstream_data": False,
    "include_seed_keyword": True,
    "include_serp_info": True,
    "keyword": SEED,
    "language_code": "en",
    "limit": 1000,
    "location_code": 2840,
    "offset": 0,
    "order_by": [ORDER_BY],
    "replace_with_core_keyword": False,
}

YEAR_ONE = "0001-01-01 00:00:00 +00:00"
HOLLOW_SERP_KEYWORDS = ("conspiracy theories in science", "conspiracy theories meaning in hindi")
OBSERVED_PERIODS = (
    (2026, 7),
    (2026, 6),
    (2026, 5),
    (2026, 4),
    (2026, 3),
    (2026, 2),
    (2026, 1),
    (2025, 12),
    (2025, 11),
    (2025, 10),
    (2025, 9),
    (2025, 8),
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
    # The operator shell legitimately carries provider credentials. Remove them for every
    # test in this module so the parser's credential independence is proved by execution
    # rather than by asserting something about the operator environment. AI-15 precedent.
    monkeypatch.delenv("OBSERVATORY_DATAFORSEO_LOGIN", raising=False)
    monkeypatch.delenv("OBSERVATORY_DATAFORSEO_PASSWORD", raising=False)


def _fixture() -> bytes:
    return FIXTURE_PATH.read_bytes()


def _parse(
    body: bytes | None = None, parameters: dict[str, object] | None = None
) -> RelatedKeywordsIR:
    return parse_related_keywords(
        body if body is not None else _fixture(), parameters or PARAMETERS
    )


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


def _task(document: dict[str, Any]) -> dict[str, Any]:
    task = document["tasks"][0]
    assert isinstance(task, dict)
    return task


def _result_obj(document: dict[str, Any]) -> dict[str, Any]:
    result = _task(document)["result"][0]
    assert isinstance(result, dict)
    return result


def _items(document: dict[str, Any]) -> list[Any]:
    items = _result_obj(document)["items"]
    assert isinstance(items, list)
    return items


def _first_item(document: dict[str, Any]) -> dict[str, Any]:
    item = _items(document)[0]
    assert isinstance(item, dict)
    return item


def _first_keyword_data(document: dict[str, Any]) -> dict[str, Any]:
    data = _first_item(document)["keyword_data"]
    assert isinstance(data, dict)
    return data


def _one_item_document(item: dict[str, Any]) -> dict[str, Any]:
    """A minimal single-item success document built from the fixture envelope."""

    document = _decoded()
    result = _result_obj(document)
    result["items"] = [item]
    result["items_count"] = 1
    return document


def _template_item() -> dict[str, Any]:
    document = _decoded()
    item = _first_item(document)
    assert isinstance(item, dict)
    return copy.deepcopy(item)


def _require_result(ir: RelatedKeywordsIR) -> RelatedKeywordsResult:
    result = ir.result
    assert result is not None
    return result


def _require_keyword_data(ir: RelatedKeywordsIR, index: int = 0) -> KeywordData:
    data = _require_result(ir).items[index].keyword_data
    assert data.state is FieldState.STATED
    assert data.value is not None
    return data.value


def _parse_error(body: bytes, parameters: dict[str, object] | None = None) -> str:
    with pytest.raises(RelatedKeywordsParseError) as excinfo:
        _parse(body, parameters)
    return excinfo.value.code


# --------------------------------------------------------------------------------------
# Fixture identity and test isolation
# --------------------------------------------------------------------------------------


def test_frozen_fixture_independent_sha256_and_length() -> None:
    raw = _fixture()
    assert len(raw) == RK02_BODY_BYTES
    assert hashlib.sha256(raw).hexdigest() == RK02_BODY_SHA256


def test_existing_fixtures_remain_byte_identical() -> None:
    for name, digest in PRIOR_FIXTURES.items():
        assert hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest() == digest


def test_existing_provider_parsers_still_read_their_own_fixtures() -> None:
    """RK-03 reuses the shared Field/ParseClassification vocabulary; prove no regression."""

    ai_target = {
        "keyword": "generative engine optimization",
        "match_type": "word_match",
        "search_filter": "include",
        "search_scope": ["answer"],
    }
    ko = parse_keyword_overview(
        (FIXTURES / "dataforseo_keyword_overview_pf03.json").read_bytes(),
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
        (FIXTURES / "dataforseo_google_organic_pf10.json").read_bytes(),
        {
            "contract": ORGANIC_ADAPTER_CONTRACT,
            "depth": 100,
            "device": "desktop",
            "group_organic_results": True,
            "keyword": SEED,
            "language_code": "en",
            "load_async_ai_overview": True,
            "location_code": 2840,
            "os": "windows",
        },
    )
    assert organic.status_code.value == 20000

    mentions = parse_search_mentions(
        (FIXTURES / "dataforseo_ai_optimization_search_mentions_ai03.json").read_bytes(),
        {
            "contract": MENTIONS_ADAPTER_CONTRACT,
            "language_code": "en",
            "limit": 5,
            "location_code": 2840,
            "offset": 0,
            "platform": "google",
            "target": [ai_target],
        },
    )
    assert mentions.outcome is ParseClassification.ADMITTED

    metrics = parse_target_metrics(
        (FIXTURES / "dataforseo_ai_optimization_target_metrics_ai09.json").read_bytes(),
        {
            "contract": TARGET_METRICS_ADAPTER_CONTRACT,
            "internal_list_limit": 10,
            "language_code": "en",
            "location_code": 2840,
            "platform": "google",
            "target": [ai_target],
        },
    )
    assert metrics.outcome is ParseClassification.ADMITTED

    historical = parse_historical(
        (
            FIXTURES / "dataforseo_ai_optimization_llm_mentions_historical_ai14.json"
        ).read_bytes(),
        {
            "contract": HISTORICAL_ADAPTER_CONTRACT,
            "date_from": "2025-08-01",
            "date_to": "2026-07-31",
            "language_code": "en",
            "location_code": 2840,
            "platform": "google",
            "target": [ai_target],
        },
    )
    assert historical.outcome is ParseClassification.ADMITTED


def test_ordinary_tests_read_only_the_committed_fixture() -> None:
    # Tokens are assembled so this assertion cannot match its own source text.
    forbidden = ("/" + "tmp", ".local/" + "share/observatory", "evidence" + "_root")
    sources = (
        Path(__file__).read_text(encoding="utf-8"),
        (
            Path(__file__).resolve().parents[1]
            / "src"
            / "observatory"
            / "dataforseo_google_related_keywords.py"
        ).read_text(encoding="utf-8"),
    )
    for text in sources:
        for token in forbidden:
            assert token not in text
    # The only body this module reads is the committed conformance fixture.
    assert FIXTURE_PATH.parent == FIXTURES
    assert FIXTURES.parent == Path(__file__).resolve().parent


def test_autouse_guard_blocks_public_network() -> None:
    with pytest.raises(AssertionError):
        socket.create_connection(("api.dataforseo.com", 443))


def test_no_credentials_in_environment() -> None:
    assert os.environ.get("OBSERVATORY_DATAFORSEO_LOGIN") is None
    assert os.environ.get("OBSERVATORY_DATAFORSEO_PASSWORD") is None


# --------------------------------------------------------------------------------------
# Golden envelope, echo, request, and result context
# --------------------------------------------------------------------------------------


def test_golden_envelope_and_task_testimony() -> None:
    ir = _parse()
    assert ir.outcome is ParseClassification.ADMITTED
    assert ir.version == "0.1.20260831"
    assert ir.status_code == 20000
    assert ir.status_message == "Ok."
    assert ir.duration == "0.2494 sec."
    assert ir.cost == Decimal("0.0216")
    assert isinstance(ir.cost, Decimal)
    assert ir.tasks_count == 1
    assert ir.tasks_error == 0
    assert ir.task_id == "08311958-1463-0387-0000-415a20bd3cc6"
    assert ir.task_status_code == 20000
    assert ir.task_status_message == "Ok."
    assert ir.task_duration == "0.1849 sec."
    assert ir.task_cost == Decimal("0.0216")
    assert isinstance(ir.task_cost, Decimal)
    assert ir.task_path == ("v3", "dataforseo_labs", "google", "related_keywords", "live")
    assert ir.result_count == 1


def test_golden_attempt_context_is_the_frozen_contract() -> None:
    request = _parse().request
    assert request.contract == RELATED_KEYWORDS_ADAPTER_CONTRACT
    assert request.keyword == SEED
    assert request.location_code == 2840
    assert request.language_code == "en"
    assert request.depth == 3
    assert request.limit == 1000
    assert request.offset == 0
    assert request.order_by == (ORDER_BY,)
    assert request.include_seed_keyword is True
    assert request.include_serp_info is True
    assert request.include_clickstream_data is False
    assert request.ignore_synonyms is False
    assert request.replace_with_core_keyword is False


def test_golden_provider_echo_is_typed_independently() -> None:
    echo = _parse().echo
    assert echo.api.value == "dataforseo_labs"
    assert echo.function.value == "related_keywords"
    assert echo.se_type.value == "google"
    assert echo.keyword.value == SEED
    assert echo.location_code.value == 2840
    assert echo.language_code.value == "en"
    assert echo.depth.value == 3
    assert echo.limit.value == 1000
    assert echo.offset.value == 0
    assert echo.order_by.value == (ORDER_BY,)
    assert echo.include_seed_keyword.value is True
    assert echo.include_serp_info.value is True
    assert echo.include_clickstream_data.value is False
    assert echo.ignore_synonyms.value is False
    assert echo.replace_with_core_keyword.value is False


def test_golden_result_context() -> None:
    result = _require_result(_parse())
    assert result.seed_keyword == SEED
    assert result.location_code.value == 2840
    assert result.language_code.value == "en"
    assert result.se_type.value == "google"
    assert result.total_count == 80
    assert result.items_count == 80
    assert len(result.items) == 80


# --------------------------------------------------------------------------------------
# Golden returned rows, order, and depth
# --------------------------------------------------------------------------------------


def test_golden_item_order_and_provider_indexes() -> None:
    result = _require_result(_parse())
    decoded = [item["keyword_data"]["keyword"] for item in _items(_decoded())]
    parsed = [_require_keyword_data(_parse(), index).keyword for index in range(3)]
    assert parsed == decoded[:3]
    assert [item.provider_array_index for item in result.items] == list(range(80))
    keywords = [
        item.keyword_data.value.keyword
        for item in result.items
        if item.keyword_data.value is not None
    ]
    assert keywords == decoded
    assert keywords[0] == SEED
    assert keywords[-1] == "intelligence and conspiracy theories"


def test_golden_depth_distribution_and_no_recomputation() -> None:
    result = _require_result(_parse())
    assert collections.Counter(item.depth for item in result.items) == {
        3: 41,
        2: 30,
        1: 8,
        0: 1,
    }
    assert result.items[0].depth == 0
    # Depth is row testimony: the array is search-volume ordered, not depth ordered.
    assert result.items[1].depth == 3


def test_golden_seed_path_is_retained_separately_from_depth_zero_item() -> None:
    result = _require_result(_parse())
    seed_data = result.seed_keyword_data
    assert seed_data.state is FieldState.STATED
    assert seed_data.value is not None
    depth_zero = result.items[0]
    assert depth_zero.depth == 0
    assert depth_zero.keyword_data.value is not None
    # Two independently parsed provider paths that happen to agree in this Capture.
    assert seed_data.value is not depth_zero.keyword_data.value
    assert seed_data.value == depth_zero.keyword_data.value
    assert seed_data.value.keyword == SEED


# --------------------------------------------------------------------------------------
# Golden relationship testimony
# --------------------------------------------------------------------------------------


def _references(ir: RelatedKeywordsIR) -> list[tuple[str, int, int, str]]:
    rows: list[tuple[str, int, int, str]] = []
    for item in _require_result(ir).items:
        data = item.keyword_data.value
        assert data is not None
        if item.related_keywords.state is not FieldState.STATED:
            continue
        assert item.related_keywords.value is not None
        for reference in item.related_keywords.value:
            rows.append(
                (data.keyword, item.depth, reference.provider_array_index, reference.target)
            )
    return rows


def test_golden_related_keyword_states_and_occurrences() -> None:
    result = _require_result(_parse())
    states = collections.Counter(item.related_keywords.state for item in result.items)
    assert states[FieldState.STATED] == 60
    assert states[FieldState.JSON_NULL] == 20
    assert states[FieldState.ABSENT] == 0
    lengths = collections.Counter(
        len(item.related_keywords.value or ())
        for item in result.items
        if item.related_keywords.state is FieldState.STATED
    )
    assert lengths == {8: 59, 5: 1}
    assert len(_references(_parse())) == 477


def test_golden_null_related_keywords_span_depth_two_and_three() -> None:
    result = _require_result(_parse())
    depths = collections.Counter(
        item.depth
        for item in result.items
        if item.related_keywords.state is FieldState.JSON_NULL
    )
    # Null is not a depth-boundary artefact: it appears inside the requested depth too.
    assert depths == {2: 10, 3: 10}


def test_golden_distinct_and_frontier_targets() -> None:
    references = _references(_parse())
    returned = {
        item.keyword_data.value.keyword
        for item in _require_result(_parse()).items
        if item.keyword_data.value is not None
    }
    targets = {row[3] for row in references}
    assert len(targets) == 246
    assert len(targets - returned) == 167


def test_golden_depth_delta_distribution() -> None:
    result = _require_result(_parse())
    depth_by_keyword = {
        item.keyword_data.value.keyword: item.depth
        for item in result.items
        if item.keyword_data.value is not None
    }
    deltas = collections.Counter(
        depth_by_keyword[target] - source_depth
        for _source, source_depth, _index, target in _references(_parse())
        if target in depth_by_keyword
    )
    assert deltas == {1: 96, 0: 96, -1: 69, -2: 21}


def test_golden_incoming_reference_counts_are_recomputable_not_stored() -> None:
    counts = collections.Counter(row[3] for row in _references(_parse()))
    assert sum(1 for value in counts.values() if value > 1) == 67
    assert max(counts.values()) == 26
    reference = _require_result(_parse()).items[0].related_keywords.value
    assert reference is not None
    assert not hasattr(reference[0], "in_degree")
    assert not hasattr(reference[0], "importance")


def test_golden_pinned_relationship_frontier_and_core_only_strings() -> None:
    result = _require_result(_parse())
    seed_item = result.items[0]
    assert seed_item.related_keywords.value is not None
    assert [
        (reference.provider_array_index, reference.target)
        for reference in seed_item.related_keywords.value
    ] == [
        (0, "conspiracy theories examples"),
        (1, "funny conspiracy theories"),
        (2, "list of conspiracy theories pdf"),
        (3, "conspiracy theories to talk about"),
        (4, "conspiracy theories podcast"),
        (5, "historical conspiracy theories"),
        (6, "fun harmless conspiracy theories"),
        (7, "the psychology of conspiracy theories"),
    ]

    references = _references(_parse())
    returned = {
        item.keyword_data.value.keyword
        for item in result.items
        if item.keyword_data.value is not None
    }
    # A frontier target named by a source below the requested depth boundary.
    assert (
        "conspiracy theories podcast",
        1,
        0,
        "conspiracy theories podcast - youtube",
    ) in references
    assert "conspiracy theories podcast - youtube" not in returned

    cores = {
        item.keyword_data.value.keyword_properties.value.core_keyword.value
        for item in result.items
        if item.keyword_data.value is not None
        and item.keyword_data.value.keyword_properties.value is not None
    }
    targets = {row[3] for row in references}
    core_only = {core for core in cores if core is not None} - returned - targets
    assert len(core_only) == 16
    assert "best conspiracy website" in core_only


# --------------------------------------------------------------------------------------
# Golden keyword-data testimony
# --------------------------------------------------------------------------------------


def _keyword_data_rows(ir: RelatedKeywordsIR) -> list[KeywordData]:
    rows: list[KeywordData] = []
    for item in _require_result(ir).items:
        assert item.keyword_data.value is not None
        rows.append(item.keyword_data.value)
    return rows


def test_golden_core_keyword_is_a_reference_layer_only() -> None:
    rows = _keyword_data_rows(_parse())
    cores = [
        row.keyword_properties.value.core_keyword
        for row in rows
        if row.keyword_properties.value is not None
    ]
    states = collections.Counter(core.state for core in cores)
    assert states[FieldState.STATED] == 21
    assert states[FieldState.JSON_NULL] == 59
    assert len({core.value for core in cores if core.state is FieldState.STATED}) == 20
    # No canonicalization: the item keyword is never replaced by its core keyword.
    for row in rows:
        properties = row.keyword_properties.value
        assert properties is not None
        if properties.core_keyword.state is FieldState.STATED:
            assert properties.core_keyword.value != row.keyword


def test_golden_synonym_algorithm_is_independent_of_core_keyword() -> None:
    rows = _keyword_data_rows(_parse())
    pairs = collections.Counter(
        (
            row.keyword_properties.value.core_keyword.state,
            row.keyword_properties.value.synonym_clustering_algorithm.state,
        )
        for row in rows
        if row.keyword_properties.value is not None
    )
    assert pairs[(FieldState.JSON_NULL, FieldState.STATED)] == 20
    assert pairs[(FieldState.STATED, FieldState.STATED)] == 21
    assert pairs[(FieldState.JSON_NULL, FieldState.JSON_NULL)] == 39


def test_golden_serp_has_three_structural_states() -> None:
    rows = _keyword_data_rows(_parse())
    null_serp = [row for row in rows if row.serp_info.state is FieldState.JSON_NULL]
    stated = [row for row in rows if row.serp_info.state is FieldState.STATED]
    hollow = [
        row
        for row in stated
        if row.serp_info.value is not None
        and row.serp_info.value.last_updated_time.value == YEAR_ONE
    ]
    assert len(null_serp) == 18
    assert len(stated) == 62
    assert len(hollow) == 2
    assert len(stated) - len(hollow) == 60


def test_golden_hollow_serp_objects_are_exact_and_stated() -> None:
    rows = {row.keyword: row for row in _keyword_data_rows(_parse())}
    for keyword in HOLLOW_SERP_KEYWORDS:
        serp = rows[keyword].serp_info
        assert serp.state is FieldState.STATED
        assert serp.value is not None
        assert serp.value.se_type.value == "google"
        assert serp.value.last_updated_time.state is FieldState.STATED
        assert serp.value.last_updated_time.value == YEAR_ONE
        assert serp.value.check_url.state is FieldState.JSON_NULL
        assert serp.value.serp_item_types.state is FieldState.JSON_NULL
        assert serp.value.se_results_count.state is FieldState.JSON_NULL
        assert serp.value.previous_updated_time.state is FieldState.JSON_NULL
        # A hollow SERP row still carries independent non-SERP testimony.
        assert rows[keyword].keyword_properties.value is not None


def test_golden_serp_item_types_stay_ordered_provider_vocabulary() -> None:
    rows = _keyword_data_rows(_parse())
    counts: collections.Counter[str] = collections.Counter()
    for row in rows:
        serp = row.serp_info.value
        if serp is None or serp.serp_item_types.state is not FieldState.STATED:
            continue
        assert serp.serp_item_types.value is not None
        counts.update(serp.serp_item_types.value)
    assert counts["organic"] == 60
    assert counts["related_searches"] == 51
    assert counts["ai_overview"] == 48
    assert counts["people_also_ask"] == 43
    assert counts["video"] == 21
    assert counts["images"] == 14
    assert counts["discussions_and_forums"] == 8
    seed_serp = rows[0].serp_info.value
    assert seed_serp is not None
    assert seed_serp.serp_item_types.value == ("ai_overview", "organic")
    assert seed_serp.check_url.value == (
        "https://www.google.com/search?q=conspiracy%20theories&hl=en&gl=US&ie=UTF-8"
        "&uule=w+CAIQIFISCQs2MuSEtepUEUK33kOSuTsc"
    )


def test_golden_backlinks_and_intent_testimony() -> None:
    rows = _keyword_data_rows(_parse())
    backlinks = collections.Counter(row.avg_backlinks_info.state for row in rows)
    assert backlinks[FieldState.STATED] == 59
    assert backlinks[FieldState.JSON_NULL] == 21
    intents = collections.Counter(
        row.search_intent_info.value.main_intent.value
        for row in rows
        if row.search_intent_info.value is not None
    )
    assert intents == {"informational": 78, "commercial": 2}
    foreign = [
        row.search_intent_info.value.foreign_intent
        for row in rows
        if row.search_intent_info.value is not None
    ]
    assert sum(1 for field in foreign if field.state is FieldState.STATED) == 4
    assert sum(1 for field in foreign if field.state is FieldState.JSON_NULL) == 76


def test_golden_monthly_history_and_independent_current_volume() -> None:
    rows = _keyword_data_rows(_parse())
    assert all(row.keyword_info.state is FieldState.STATED for row in rows)
    total_rows = 0
    zeros = 0
    diverging = 0
    for row in rows:
        info = row.keyword_info.value
        assert info is not None
        monthly = info.monthly_searches.value
        assert monthly is not None
        assert tuple((point.year, point.month) for point in monthly) == OBSERVED_PERIODS
        assert [point.provider_array_index for point in monthly] == list(range(12))
        total_rows += len(monthly)
        zeros += sum(1 for point in monthly if point.search_volume == 0)
        if info.search_volume.value != monthly[0].search_volume:
            diverging += 1
    assert total_rows == 960
    assert zeros == 50
    assert diverging == 63

    # The separately retained seed path contributes its own twelve rows.
    seed_data = _require_result(_parse()).seed_keyword_data.value
    assert seed_data is not None
    seed_info = seed_data.keyword_info.value
    assert seed_info is not None
    assert seed_info.monthly_searches.value is not None
    assert len(seed_info.monthly_searches.value) == 12


def test_golden_categories_preserve_provider_order_and_duplicates() -> None:
    rows = _keyword_data_rows(_parse())
    with_duplicates = 0
    for row in rows:
        info = row.keyword_info.value
        assert info is not None
        if info.categories.state is not FieldState.STATED:
            continue
        assert info.categories.value is not None
        if len(info.categories.value) != len(set(info.categories.value)):
            with_duplicates += 1
    assert with_duplicates == 11
    nulls = sum(
        1
        for row in rows
        if row.keyword_info.value is not None
        and row.keyword_info.value.categories.state is FieldState.JSON_NULL
    )
    assert nulls == 4


def test_golden_clickstream_and_bing_states_are_distinguishable() -> None:
    rows = _keyword_data_rows(_parse())
    for row in rows:
        assert row.clickstream_keyword_info.state is FieldState.NOT_REQUESTED
        assert row.keyword_info_normalized_with_clickstream.state is FieldState.NOT_REQUESTED
        assert row.keyword_info_normalized_with_bing.state is FieldState.JSON_NULL


def test_golden_structure_local_clocks_stay_independent() -> None:
    rows = _keyword_data_rows(_parse())
    same = 0
    for row in rows:
        info = row.keyword_info.value
        intent = row.search_intent_info.value
        assert info is not None
        assert intent is not None
        assert info.last_updated_time.state is FieldState.STATED
        assert intent.last_updated_time.state is FieldState.STATED
        if info.last_updated_time.value == intent.last_updated_time.value:
            same += 1
    assert same == 0
    # SERP and backlink clocks are separate structures that sometimes agree and often
    # do not; neither is derived from the other or from Capture time.
    both = [
        row
        for row in rows
        if row.serp_info.value is not None and row.avg_backlinks_info.value is not None
    ]
    differing = [
        row
        for row in both
        if row.serp_info.value is not None
        and row.avg_backlinks_info.value is not None
        and row.serp_info.value.last_updated_time.value
        != row.avg_backlinks_info.value.last_updated_time.value
    ]
    assert len(both) == 59
    assert len(differing) == 50
    # The year-1 value lives only on the SERP structure that stated it.
    serp_clocks = {
        row.serp_info.value.last_updated_time.value
        for row in rows
        if row.serp_info.value is not None
    }
    other_clocks = {
        row.keyword_info.value.last_updated_time.value
        for row in rows
        if row.keyword_info.value is not None
    } | {
        row.search_intent_info.value.last_updated_time.value
        for row in rows
        if row.search_intent_info.value is not None
    } | {
        row.avg_backlinks_info.value.last_updated_time.value
        for row in rows
        if row.avg_backlinks_info.value is not None
    }
    assert YEAR_ONE in serp_clocks
    assert YEAR_ONE not in other_clocks


def test_golden_search_volume_trend_values_may_be_negative() -> None:
    rows = _keyword_data_rows(_parse())
    values = [
        row.keyword_info.value.search_volume_trend.value.monthly.value
        for row in rows
        if row.keyword_info.value is not None
        and row.keyword_info.value.search_volume_trend.value is not None
    ]
    assert any(value is not None and value < 0 for value in values)
    yearly_nulls = sum(
        1
        for row in rows
        if row.keyword_info.value is not None
        and row.keyword_info.value.search_volume_trend.value is not None
        and row.keyword_info.value.search_volume_trend.value.yearly.state
        is FieldState.JSON_NULL
    )
    assert yearly_nulls == 11


def test_golden_stated_zero_and_null_remain_distinguishable() -> None:
    rows = _keyword_data_rows(_parse())
    difficulties = [
        row.keyword_properties.value.keyword_difficulty
        for row in rows
        if row.keyword_properties.value is not None
    ]
    assert sum(1 for field in difficulties if field.state is FieldState.JSON_NULL) == 18
    assert sum(1 for field in difficulties if field.value == 0) == 9
    competitions = [
        row.keyword_info.value.competition
        for row in rows
        if row.keyword_info.value is not None
    ]
    assert sum(1 for field in competitions if field.state is FieldState.JSON_NULL) == 1
    assert sum(1 for field in competitions if field.value == Decimal(0)) == 37


# --------------------------------------------------------------------------------------
# Adversarial: decode, numerics, and schema drift
# --------------------------------------------------------------------------------------


def test_decode_rejects_bom_bad_utf8_trailing_and_invalid_json() -> None:
    assert _parse_error(b"\xef\xbb\xbf" + _fixture()) == "utf8_bom"
    assert _parse_error(b"\xff\xfe\x00") == "invalid_utf8"
    assert _parse_error(_fixture() + b" {}") == "trailing_data"
    assert _parse_error(b"{oops}") == "invalid_json"


def test_decode_rejects_duplicate_object_members() -> None:
    body = _fixture()
    tampered = body.replace(b'"tasks_count":1', b'"tasks_count":1,"tasks_count":1', 1)
    assert tampered != body
    assert _parse_error(tampered) == "duplicate_member"


@pytest.mark.parametrize("literal", [b"NaN", b"Infinity", b"-Infinity"])
def test_decode_rejects_non_finite_numbers(literal: bytes) -> None:
    body = _fixture().replace(b'"cost":0.0216', b'"cost":' + literal, 1)
    assert _parse_error(body) == "non_finite_number"


@pytest.mark.parametrize(
    ("literal", "expected"),
    [
        (b"7", Decimal("7")),
        (b"0.1", Decimal("0.1")),
        (b"1e-3", Decimal("1e-3")),
        (b"0.12345678901234567890123", Decimal("0.12345678901234567890123")),
    ],
)
def test_decimal_forms_survive_without_binary_float_round_trip(
    literal: bytes, expected: Decimal
) -> None:
    body = _fixture().replace(b'"cost":0.0216', b'"cost":' + literal, 1)
    ir = _parse(body)
    assert isinstance(ir.cost, Decimal)
    assert ir.cost == expected


@pytest.mark.parametrize("value", [True, "1", Decimal("1.5")])
def test_structural_integers_reject_booleans_strings_and_decimals(value: object) -> None:
    document = _decoded()
    document["tasks_count"] = value
    assert _parse_error(_encode(document)) == "wrong_type"


@pytest.mark.parametrize(
    ("pointer", "key"),
    [
        ((), "surprise"),
        (("tasks", 0), "surprise"),
        (("tasks", 0, "data"), "surprise"),
        (("tasks", 0, "result", 0), "surprise"),
        (("tasks", 0, "result", 0, "items", 0), "surprise"),
        (("tasks", 0, "result", 0, "items", 0, "keyword_data"), "surprise"),
        (("tasks", 0, "result", 0, "items", 0, "keyword_data"), "search_partners"),
        (("tasks", 0, "result", 0, "items", 0, "keyword_data", "keyword_info"), "surprise"),
        (
            (
                "tasks",
                0,
                "result",
                0,
                "items",
                0,
                "keyword_data",
                "keyword_info",
                "monthly_searches",
                0,
            ),
            "surprise",
        ),
        (
            (
                "tasks",
                0,
                "result",
                0,
                "items",
                0,
                "keyword_data",
                "keyword_info",
                "search_volume_trend",
            ),
            "surprise",
        ),
        (
            ("tasks", 0, "result", 0, "items", 0, "keyword_data", "keyword_properties"),
            "surprise",
        ),
        (
            ("tasks", 0, "result", 0, "items", 0, "keyword_data", "avg_backlinks_info"),
            "surprise",
        ),
        (
            ("tasks", 0, "result", 0, "items", 0, "keyword_data", "search_intent_info"),
            "surprise",
        ),
        (("tasks", 0, "result", 0, "items", 0, "keyword_data", "serp_info"), "surprise"),
        (("tasks", 0, "result", 0, "seed_keyword_data"), "surprise"),
    ],
)
def test_unknown_members_fail_at_every_closed_layer(
    pointer: tuple[object, ...], key: str
) -> None:
    document = _decoded()
    node: Any = document
    for step in pointer:
        node = node[step]
    node[key] = 1
    assert _parse_error(_encode(document)) == "unknown_field"


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("keyword_info", "competition_level"), "ULTRA"),
        (("keyword_properties", "synonym_clustering_algorithm"), "brand_new_algorithm"),
        (("search_intent_info", "main_intent"), "speculative"),
    ],
)
def test_open_provider_vocabulary_values_stay_parseable(
    path: tuple[str, str], value: str
) -> None:
    document = _decoded()
    _first_keyword_data(document)[path[0]][path[1]] = value
    ir = _parse(_encode(document))
    assert ir.outcome is ParseClassification.ADMITTED


def test_new_serp_item_type_and_foreign_intent_values_stay_parseable() -> None:
    document = _decoded()
    data = _first_keyword_data(document)
    data["serp_info"]["serp_item_types"] = ["brand_new_block", "organic", "organic"]
    data["search_intent_info"]["foreign_intent"] = ["speculative"]
    serp = _require_keyword_data(_parse(_encode(document))).serp_info.value
    assert serp is not None
    assert serp.serp_item_types.value == ("brand_new_block", "organic", "organic")


# --------------------------------------------------------------------------------------
# Adversarial: envelope, echo, and result topology
# --------------------------------------------------------------------------------------


def test_tasks_count_and_task_array_topology() -> None:
    document = _decoded()
    document["tasks_count"] = 2
    assert _parse_error(_encode(document)) == "count_mismatch"

    document = _decoded()
    document["tasks"] = [_task(_decoded()), _task(_decoded())]
    document["tasks_count"] = 2
    assert _parse_error(_encode(document)) == "tasks_length"


def test_tasks_error_must_match_success_topology() -> None:
    document = _decoded()
    document["tasks_error"] = 1
    assert _parse_error(_encode(document)) == "count_mismatch"

    document = _decoded()
    _task(document)["status_code"] = 40501
    document["status_code"] = 40501
    document["tasks_error"] = 0
    assert _parse_error(_encode(document)) == "count_mismatch"


@pytest.mark.parametrize(
    ("root_status", "task_status"), [(20000, 40501), (40501, 20000)]
)
def test_root_and_task_success_disagreement_fails(
    root_status: int, task_status: int
) -> None:
    document = _decoded()
    document["status_code"] = root_status
    _task(document)["status_code"] = task_status
    document["tasks_error"] = 0 if task_status == 20000 else 1
    assert _parse_error(_encode(document)) == "inconsistent_status"


def test_consistent_provider_error_preserves_envelope_without_reading_result() -> None:
    document = _decoded()
    document["status_code"] = 40501
    document["status_message"] = "Invalid Field: 'keyword'."
    document["tasks_error"] = 1
    task = _task(document)
    task["status_code"] = 40501
    task["status_message"] = "Invalid Field: 'keyword'."
    task["result_count"] = 0
    # Poisoned result material must never be interpreted on the error branch.
    task["result"] = [{"totally": "unparseable"}]
    ir = _parse(_encode(document))
    assert ir.outcome is ParseClassification.PROVIDER_ERROR
    assert ir.result is None
    assert ir.result_count == 0
    assert ir.status_code == 40501
    assert ir.task_status_code == 40501
    assert ir.task_path == ("v3", "dataforseo_labs", "google", "related_keywords", "live")
    assert ir.echo.keyword.value == SEED
    assert ir.request.keyword == SEED
    assert ir.cost == Decimal("0.0216")


def test_provider_error_with_malformed_echo_or_counts_still_fails() -> None:
    document = _decoded()
    document["status_code"] = 40501
    document["tasks_error"] = 1
    task = _task(document)
    task["status_code"] = 40501
    task["data"] = None
    assert _parse_error(_encode(document)) == "wrong_type"

    document = _decoded()
    document["status_code"] = 40501
    document["tasks_error"] = 1
    task = _task(document)
    task["status_code"] = 40501
    task["result_count"] = -1
    assert _parse_error(_encode(document)) == "invalid_number"


@pytest.mark.parametrize("value", [-1, True, "1"])
def test_result_count_rejects_negative_boolean_and_string(value: object) -> None:
    document = _decoded()
    _task(document)["result_count"] = value
    code = _parse_error(_encode(document))
    assert code in {"invalid_number", "wrong_type"}


def test_successful_result_topology_must_be_exactly_one_object() -> None:
    document = _decoded()
    _task(document)["result"] = []
    _task(document)["result_count"] = 0
    assert _parse_error(_encode(document)) == "result_length"

    document = _decoded()
    _task(document)["result"] = [_result_obj(_decoded()), _result_obj(_decoded())]
    _task(document)["result_count"] = 2
    assert _parse_error(_encode(document)) == "result_length"

    document = _decoded()
    _task(document)["result_count"] = 2
    assert _parse_error(_encode(document)) == "count_mismatch"


@pytest.mark.parametrize("mutation", ["null", "omitted", "object"])
def test_successful_result_null_omitted_or_wrong_type_fails(mutation: str) -> None:
    document = _decoded()
    task = _task(document)
    if mutation == "null":
        task["result"] = None
    elif mutation == "omitted":
        del task["result"]
    else:
        task["result"] = {"items": []}
    assert _parse_error(_encode(document)) == "wrong_type"


def test_items_count_must_equal_actual_item_array_length() -> None:
    document = _decoded()
    _result_obj(document)["items_count"] = 79
    assert _parse_error(_encode(document)) == "count_mismatch"


@pytest.mark.parametrize("total", [0, 5, 79, 81, 5000])
def test_total_count_is_independent_of_items_count(total: int) -> None:
    document = _decoded()
    _result_obj(document)["total_count"] = total
    result = _require_result(_parse(_encode(document)))
    assert result.total_count == total
    assert result.items_count == 80


def test_negative_total_count_fails() -> None:
    document = _decoded()
    _result_obj(document)["total_count"] = -1
    assert _parse_error(_encode(document)) == "invalid_number"


@pytest.mark.parametrize("value", [None, 5, "items", {"0": {}}])
def test_items_must_be_an_array(value: object) -> None:
    document = _decoded()
    _result_obj(document)["items"] = value
    assert _parse_error(_encode(document)) == "wrong_type"


@pytest.mark.parametrize("value", [None, 5, ["seed"]])
def test_result_seed_keyword_must_be_a_string(value: object) -> None:
    document = _decoded()
    _result_obj(document)["seed_keyword"] = value
    assert _parse_error(_encode(document)) == "wrong_type"


@pytest.mark.parametrize(
    "key",
    [
        "keyword_info",
        "keyword_properties",
        "avg_backlinks_info",
        "search_intent_info",
        "serp_info",
    ],
)
def test_enrichment_scalars_are_not_accepted_as_objects(key: str) -> None:
    item = _template_item()
    item["keyword_data"][key] = 5
    assert _parse_error(_encode(_one_item_document(item))) == "wrong_type"


@pytest.mark.parametrize("value", [None, 5, "data", ["data"]])
def test_seed_keyword_data_wrong_container_is_rejected_or_null(value: object) -> None:
    document = _decoded()
    _result_obj(document)["seed_keyword_data"] = value
    if value is None:
        assert (
            _require_result(_parse(_encode(document))).seed_keyword_data.state
            is FieldState.JSON_NULL
        )
    else:
        assert _parse_error(_encode(document)) == "wrong_type"


def test_empty_items_parses_as_empty_parser_ir_only() -> None:
    document = _decoded()
    result = _result_obj(document)
    result["items"] = []
    result["items_count"] = 0
    ir = _parse(_encode(document))
    assert ir.outcome is ParseClassification.ADMITTED
    parsed = _require_result(ir)
    assert parsed.items == ()
    assert parsed.items_count == 0
    assert parsed.seed_keyword == SEED
    assert parsed.seed_keyword_data.state is FieldState.STATED


# --------------------------------------------------------------------------------------
# Adversarial: verified Attempt parameter contract
# --------------------------------------------------------------------------------------


def test_attempt_parameter_key_set_is_closed() -> None:
    parameters = dict(PARAMETERS)
    parameters["tag"] = "extra"
    with pytest.raises(RelatedKeywordsParseError) as excinfo:
        _parse(None, parameters)
    assert excinfo.value.code == "unknown_field"

    parameters = dict(PARAMETERS)
    del parameters["offset"]
    with pytest.raises(RelatedKeywordsParseError) as excinfo:
        _parse(None, parameters)
    assert excinfo.value.code == "wrong_type"


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("contract", PAID_ADAPTER_CONTRACT),
        ("location_code", 2826),
        ("language_code", "de"),
        ("depth", 4),
        ("limit", 999),
        ("offset", 10),
        ("order_by", ["keyword_data.keyword_info.search_volume,asc"]),
        ("include_seed_keyword", False),
        ("include_serp_info", False),
        ("include_clickstream_data", True),
        ("ignore_synonyms", True),
        ("replace_with_core_keyword", True),
    ],
)
def test_every_frozen_attempt_value_is_enforced(key: str, value: object) -> None:
    parameters = dict(PARAMETERS)
    parameters[key] = value
    with pytest.raises(RelatedKeywordsParseError) as excinfo:
        _parse(None, parameters)
    assert excinfo.value.code in {"frozen_parameter", "unknown_enum"}


@pytest.mark.parametrize("value", [True, 1, "true"])
def test_attempt_booleans_reject_non_boolean_values(value: object) -> None:
    parameters = dict(PARAMETERS)
    parameters["include_clickstream_data"] = value
    with pytest.raises(RelatedKeywordsParseError) as excinfo:
        _parse(None, parameters)
    assert excinfo.value.code in {"wrong_type", "frozen_parameter"}


def test_attempt_integers_reject_booleans() -> None:
    parameters = dict(PARAMETERS)
    parameters["depth"] = True
    with pytest.raises(RelatedKeywordsParseError) as excinfo:
        _parse(None, parameters)
    assert excinfo.value.code == "wrong_type"


@pytest.mark.parametrize(
    "seed",
    [
        "",
        "a" * 81,
        "seo <script>",
        "one two three four five six seven eight nine ten eleven",
    ],
)
def test_seed_grammar_rejects_out_of_contract_seeds(seed: str) -> None:
    parameters = dict(PARAMETERS)
    parameters["keyword"] = seed
    with pytest.raises(RelatedKeywordsParseError) as excinfo:
        _parse(None, parameters)
    assert excinfo.value.code == "invalid_value"


def test_seed_must_be_a_string() -> None:
    parameters = dict(PARAMETERS)
    parameters["keyword"] = 7
    with pytest.raises(RelatedKeywordsParseError) as excinfo:
        _parse(None, parameters)
    assert excinfo.value.code == "wrong_type"


def test_echo_and_result_disagreement_stays_visible_without_overwriting_attempt() -> None:
    document = _decoded()
    _task(document)["data"]["keyword"] = "something else"
    _task(document)["data"]["location_code"] = 2826
    _task(document)["data"]["depth"] = 1
    result = _result_obj(document)
    result["seed_keyword"] = "provider rewrote the seed"
    result["location_code"] = 2826
    result["language_code"] = "de"
    ir = _parse(_encode(document))
    assert ir.request.keyword == SEED
    assert ir.request.location_code == 2840
    assert ir.echo.keyword.value == "something else"
    assert ir.echo.location_code.value == 2826
    assert ir.echo.depth.value == 1
    parsed = _require_result(ir)
    assert parsed.seed_keyword == "provider rewrote the seed"
    assert parsed.location_code.value == 2826
    assert parsed.language_code.value == "de"


def test_result_se_type_must_stay_google() -> None:
    document = _decoded()
    _result_obj(document)["se_type"] = "bing"
    assert _parse_error(_encode(document)) == "unknown_enum"


# --------------------------------------------------------------------------------------
# Adversarial: returned rows and relationship preservation
# --------------------------------------------------------------------------------------


def test_shuffled_item_order_is_preserved_with_synthetic_indexes() -> None:
    document = _decoded()
    items = _items(document)
    reversed_items = list(reversed(items))
    _result_obj(document)["items"] = reversed_items
    result = _require_result(_parse(_encode(document)))
    keywords = [
        item.keyword_data.value.keyword
        for item in result.items
        if item.keyword_data.value is not None
    ]
    assert keywords[0] == "intelligence and conspiracy theories"
    assert keywords[-1] == SEED
    assert [item.provider_array_index for item in result.items] == list(range(80))
    assert result.items[-1].depth == 0


def test_duplicate_returned_keywords_remain_separate_occurrences() -> None:
    document = _decoded()
    duplicate = copy.deepcopy(_first_item(document))
    _result_obj(document)["items"] = [_first_item(_decoded()), duplicate]
    _result_obj(document)["items_count"] = 2
    result = _require_result(_parse(_encode(document)))
    assert len(result.items) == 2
    assert result.items[0].provider_array_index == 0
    assert result.items[1].provider_array_index == 1
    assert result.items[0].keyword_data.value is not None
    assert result.items[1].keyword_data.value is not None
    assert result.items[0].keyword_data.value.keyword == (
        result.items[1].keyword_data.value.keyword
    )


@pytest.mark.parametrize("depth", [0, 1, 2, 3, 4])
def test_claimed_contract_depth_range_parses(depth: int) -> None:
    item = _template_item()
    item["depth"] = depth
    ir = _parse(_encode(_one_item_document(item)))
    assert _require_result(ir).items[0].depth == depth


@pytest.mark.parametrize("depth", [-1, 5, 100])
def test_depth_outside_claimed_contract_fails(depth: int) -> None:
    item = _template_item()
    item["depth"] = depth
    assert _parse_error(_encode(_one_item_document(item))) == "invalid_depth"


@pytest.mark.parametrize("depth", [True, "3", Decimal("3.0")])
def test_depth_rejects_non_integers(depth: object) -> None:
    item = _template_item()
    item["depth"] = depth
    assert _parse_error(_encode(_one_item_document(item))) == "wrong_type"


def test_related_keywords_absent_null_and_empty_remain_distinct() -> None:
    absent = _template_item()
    del absent["related_keywords"]
    field = _require_result(_parse(_encode(_one_item_document(absent)))).items[0]
    assert field.related_keywords.state is FieldState.ABSENT

    nulled = _template_item()
    nulled["related_keywords"] = None
    field = _require_result(_parse(_encode(_one_item_document(nulled)))).items[0]
    assert field.related_keywords.state is FieldState.JSON_NULL

    empty = _template_item()
    empty["related_keywords"] = []
    field = _require_result(_parse(_encode(_one_item_document(empty)))).items[0]
    assert field.related_keywords.state is FieldState.STATED
    assert field.related_keywords.value == ()


def test_duplicate_repeated_and_self_referencing_targets_survive_in_order() -> None:
    item = _template_item()
    item["related_keywords"] = [SEED, "alpha", "alpha", "beta", "alpha"]
    references = _require_result(
        _parse(_encode(_one_item_document(item)))
    ).items[0].related_keywords.value
    assert references is not None
    assert [(ref.provider_array_index, ref.target) for ref in references] == [
        (0, SEED),
        (1, "alpha"),
        (2, "alpha"),
        (3, "beta"),
        (4, "alpha"),
    ]


@pytest.mark.parametrize("target", [1, None, True, ["nested"], {"k": "v"}])
def test_wrong_typed_related_target_fails(target: object) -> None:
    item = _template_item()
    item["related_keywords"] = ["ok", target]
    assert _parse_error(_encode(_one_item_document(item))) == "wrong_type"


def test_related_keywords_wrong_container_fails() -> None:
    item = _template_item()
    item["related_keywords"] = {"target": "alpha"}
    assert _parse_error(_encode(_one_item_document(item))) == "wrong_type"


def test_seed_keyword_data_states_and_disagreement_stay_visible() -> None:
    document = _decoded()
    del _result_obj(document)["seed_keyword_data"]
    assert (
        _require_result(_parse(_encode(document))).seed_keyword_data.state
        is FieldState.ABSENT
    )

    document = _decoded()
    _result_obj(document)["seed_keyword_data"] = None
    assert (
        _require_result(_parse(_encode(document))).seed_keyword_data.state
        is FieldState.JSON_NULL
    )

    document = _decoded()
    _result_obj(document)["seed_keyword_data"]["keyword"] = "a different seed string"
    result = _require_result(_parse(_encode(document)))
    assert result.seed_keyword_data.value is not None
    assert result.seed_keyword_data.value.keyword == "a different seed string"
    assert result.items[0].keyword_data.value is not None
    assert result.items[0].keyword_data.value.keyword == SEED


def test_missing_depth_zero_row_is_visible_not_a_parse_failure() -> None:
    document = _decoded()
    items = [item for item in _items(document) if item["depth"] != 0]
    _result_obj(document)["items"] = items
    _result_obj(document)["items_count"] = len(items)
    result = _require_result(_parse(_encode(document)))
    assert all(item.depth != 0 for item in result.items)
    assert result.seed_keyword == SEED


def test_item_location_and_language_disagreement_is_visible() -> None:
    item = _template_item()
    item["keyword_data"]["location_code"] = 2826
    item["keyword_data"]["language_code"] = "de"
    data = _require_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.location_code.value == 2826
    assert data.language_code.value == "de"


def test_item_keyword_data_absent_and_null_states() -> None:
    absent = _template_item()
    del absent["keyword_data"]
    assert (
        _require_result(_parse(_encode(_one_item_document(absent)))).items[0].keyword_data.state
        is FieldState.ABSENT
    )
    nulled = _template_item()
    nulled["keyword_data"] = None
    assert (
        _require_result(_parse(_encode(_one_item_document(nulled)))).items[0].keyword_data.state
        is FieldState.JSON_NULL
    )


@pytest.mark.parametrize(
    "path",
    [
        ("keyword_data", "se_type"),
        ("keyword_data", "keyword_info", "se_type"),
        ("keyword_data", "keyword_properties", "se_type"),
        ("keyword_data", "avg_backlinks_info", "se_type"),
        ("keyword_data", "search_intent_info", "se_type"),
        ("keyword_data", "serp_info", "se_type"),
    ],
)
def test_nested_stated_se_type_must_be_google(path: tuple[str, ...]) -> None:
    item = _template_item()
    node: Any = item
    for step in path[:-1]:
        node = node[step]
    node[path[-1]] = "bing"
    assert _parse_error(_encode(_one_item_document(item))) == "unknown_enum"


def test_item_se_type_is_required_and_typed() -> None:
    item = _template_item()
    item["se_type"] = "bing"
    assert _parse_error(_encode(_one_item_document(item))) == "unknown_enum"
    item = _template_item()
    item["se_type"] = None
    assert _parse_error(_encode(_one_item_document(item))) == "wrong_type"


# --------------------------------------------------------------------------------------
# Adversarial: keyword data, monthly periods, and SERP states
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "key",
    [
        "keyword_info",
        "keyword_properties",
        "avg_backlinks_info",
        "search_intent_info",
        "serp_info",
    ],
)
def test_enrichment_object_absent_null_and_stated_states_stay_distinct(key: str) -> None:
    absent = _template_item()
    del absent["keyword_data"][key]
    data = _require_keyword_data(_parse(_encode(_one_item_document(absent))))
    assert getattr(data, key).state is FieldState.ABSENT

    nulled = _template_item()
    nulled["keyword_data"][key] = None
    data = _require_keyword_data(_parse(_encode(_one_item_document(nulled))))
    assert getattr(data, key).state is FieldState.JSON_NULL

    data = _require_keyword_data(_parse())
    assert getattr(data, key).state is FieldState.STATED


@pytest.mark.parametrize("core", [SEED, "conspiracy theories examples", "never seen anywhere"])
def test_core_keyword_may_name_any_string_without_replacement(core: str) -> None:
    item = _template_item()
    item["keyword_data"]["keyword_properties"]["core_keyword"] = core
    data = _require_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.keyword_properties.value is not None
    assert data.keyword_properties.value.core_keyword.value == core
    assert data.keyword == SEED


def test_core_keyword_and_synonym_algorithm_states_are_independent() -> None:
    item = _template_item()
    item["keyword_data"]["keyword_properties"]["core_keyword"] = None
    item["keyword_data"]["keyword_properties"]["synonym_clustering_algorithm"] = "text_processing"
    data = _require_keyword_data(_parse(_encode(_one_item_document(item))))
    properties = data.keyword_properties.value
    assert properties is not None
    assert properties.core_keyword.state is FieldState.JSON_NULL
    assert properties.synonym_clustering_algorithm.value == "text_processing"

    item = _template_item()
    item["keyword_data"]["keyword_properties"]["core_keyword"] = "some core"
    item["keyword_data"]["keyword_properties"]["synonym_clustering_algorithm"] = None
    data = _require_keyword_data(_parse(_encode(_one_item_document(item))))
    properties = data.keyword_properties.value
    assert properties is not None
    assert properties.core_keyword.value == "some core"
    assert properties.synonym_clustering_algorithm.state is FieldState.JSON_NULL


def _monthly_item(rows: list[dict[str, object]] | None) -> dict[str, Any]:
    item = _template_item()
    item["keyword_data"]["keyword_info"]["monthly_searches"] = rows
    return item


def test_monthly_arrays_may_be_empty_shorter_longer_or_shuffled() -> None:
    empty = _monthly_item([])
    info = _require_keyword_data(_parse(_encode(_one_item_document(empty)))).keyword_info.value
    assert info is not None
    assert info.monthly_searches.value == ()

    shuffled = _monthly_item(
        [
            {"year": 2025, "month": 3, "search_volume": 10},
            {"year": 2026, "month": 7, "search_volume": 20},
            {"year": 1999, "month": 12, "search_volume": 0},
        ]
    )
    info = _require_keyword_data(
        _parse(_encode(_one_item_document(shuffled)))
    ).keyword_info.value
    assert info is not None
    monthly = info.monthly_searches.value
    assert monthly is not None
    assert [(point.year, point.month, point.provider_array_index) for point in monthly] == [
        (2025, 3, 0),
        (2026, 7, 1),
        (1999, 12, 2),
    ]
    assert monthly[2].search_volume == 0


def test_monthly_absent_and_null_states_stay_distinct() -> None:
    absent = _template_item()
    del absent["keyword_data"]["keyword_info"]["monthly_searches"]
    info = _require_keyword_data(_parse(_encode(_one_item_document(absent)))).keyword_info.value
    assert info is not None
    assert info.monthly_searches.state is FieldState.ABSENT

    nulled = _monthly_item(None)
    info = _require_keyword_data(_parse(_encode(_one_item_document(nulled)))).keyword_info.value
    assert info is not None
    assert info.monthly_searches.state is FieldState.JSON_NULL


def test_duplicate_monthly_period_fails_closed() -> None:
    item = _monthly_item(
        [
            {"year": 2026, "month": 7, "search_volume": 10},
            {"year": 2026, "month": 6, "search_volume": 20},
            {"year": 2026, "month": 7, "search_volume": 30},
        ]
    )
    with pytest.raises(RelatedKeywordsParseError) as excinfo:
        _parse(_encode(_one_item_document(item)))
    assert excinfo.value.code == "duplicate_period"
    assert excinfo.value.path.endswith("/monthly_searches/2")


@pytest.mark.parametrize(
    ("year", "month"), [(2026, 0), (2026, 13), (0, 6), (10000, 6), (-1, 6)]
)
def test_invalid_monthly_period_fails(year: int, month: int) -> None:
    item = _monthly_item([{"year": year, "month": month, "search_volume": 10}])
    assert _parse_error(_encode(_one_item_document(item))) == "invalid_period"


def test_negative_monthly_search_volume_fails() -> None:
    item = _monthly_item([{"year": 2026, "month": 7, "search_volume": -1}])
    assert _parse_error(_encode(_one_item_document(item))) == "invalid_number"


@pytest.mark.parametrize(
    ("container", "key"),
    [
        ("keyword_info", "search_volume"),
        ("keyword_properties", "keyword_difficulty"),
        ("serp_info", "se_results_count"),
    ],
)
def test_negative_nonnegative_metrics_fail(container: str, key: str) -> None:
    item = _template_item()
    item["keyword_data"][container][key] = -1
    assert _parse_error(_encode(_one_item_document(item))) == "invalid_number"


@pytest.mark.parametrize("key", ["monthly", "quarterly", "yearly"])
def test_search_volume_trend_accepts_negative_values(key: str) -> None:
    item = _template_item()
    item["keyword_data"]["keyword_info"]["search_volume_trend"][key] = -100
    info = _require_keyword_data(_parse(_encode(_one_item_document(item)))).keyword_info.value
    assert info is not None
    trend = info.search_volume_trend.value
    assert trend is not None
    assert getattr(trend, key).value == -100


def test_zero_and_null_metric_states_remain_distinguishable() -> None:
    zeroed = _template_item()
    zeroed["keyword_data"]["keyword_info"]["competition"] = 0
    zeroed["keyword_data"]["keyword_properties"]["keyword_difficulty"] = 0
    data = _require_keyword_data(_parse(_encode(_one_item_document(zeroed))))
    assert data.keyword_info.value is not None
    assert data.keyword_properties.value is not None
    assert data.keyword_info.value.competition.state is FieldState.STATED
    assert data.keyword_info.value.competition.value == Decimal(0)
    assert data.keyword_properties.value.keyword_difficulty.value == 0

    nulled = _template_item()
    nulled["keyword_data"]["keyword_info"]["competition"] = None
    nulled["keyword_data"]["keyword_properties"]["keyword_difficulty"] = None
    data = _require_keyword_data(_parse(_encode(_one_item_document(nulled))))
    assert data.keyword_info.value is not None
    assert data.keyword_properties.value is not None
    assert data.keyword_info.value.competition.state is FieldState.JSON_NULL
    assert data.keyword_properties.value.keyword_difficulty.state is FieldState.JSON_NULL


def test_categories_and_foreign_intent_array_states_are_preserved() -> None:
    item = _template_item()
    item["keyword_data"]["keyword_info"]["categories"] = [10, 10, 3, 3, 1]
    item["keyword_data"]["search_intent_info"]["foreign_intent"] = []
    data = _require_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.keyword_info.value is not None
    assert data.keyword_info.value.categories.value == (10, 10, 3, 3, 1)
    assert data.search_intent_info.value is not None
    assert data.search_intent_info.value.foreign_intent.state is FieldState.STATED
    assert data.search_intent_info.value.foreign_intent.value == ()

    nulled = _template_item()
    nulled["keyword_data"]["keyword_info"]["categories"] = None
    nulled["keyword_data"]["search_intent_info"]["foreign_intent"] = None
    data = _require_keyword_data(_parse(_encode(_one_item_document(nulled))))
    assert data.keyword_info.value is not None
    assert data.keyword_info.value.categories.state is FieldState.JSON_NULL
    assert data.search_intent_info.value is not None
    assert data.search_intent_info.value.foreign_intent.state is FieldState.JSON_NULL


def test_categories_reject_non_integer_members() -> None:
    item = _template_item()
    item["keyword_data"]["keyword_info"]["categories"] = [10, "13566"]
    assert _parse_error(_encode(_one_item_document(item))) == "wrong_type"


def test_year_one_serp_timestamp_is_preserved_exactly() -> None:
    item = _template_item()
    item["keyword_data"]["serp_info"]["last_updated_time"] = YEAR_ONE
    data = _require_keyword_data(_parse(_encode(_one_item_document(item))))
    serp = data.serp_info.value
    assert serp is not None
    assert serp.last_updated_time.state is FieldState.STATED
    assert serp.last_updated_time.value == YEAR_ONE


@pytest.mark.parametrize(
    "value",
    [
        "2026-08-31T19:58:12+00:00",
        "2026-08-31 19:58:12 +01:00",
        "2026-13-01 00:00:00 +00:00",
        "2026-02-30 00:00:00 +00:00",
        "0000-01-01 00:00:00 +00:00",
        "2026-08-31 19:58:12 +00:00 ",
        "26-08-31 19:58:12 +00:00",
    ],
)
def test_malformed_or_impossible_timestamps_fail(value: str) -> None:
    item = _template_item()
    item["keyword_data"]["keyword_info"]["last_updated_time"] = value
    assert _parse_error(_encode(_one_item_document(item))) == "invalid_timestamp"


def test_serp_states_stay_structurally_distinguishable() -> None:
    nulled = _template_item()
    nulled["keyword_data"]["serp_info"] = None
    data = _require_keyword_data(_parse(_encode(_one_item_document(nulled))))
    assert data.serp_info.state is FieldState.JSON_NULL

    hollow = _template_item()
    hollow["keyword_data"]["serp_info"] = {
        "se_type": "google",
        "check_url": None,
        "serp_item_types": None,
        "se_results_count": None,
        "last_updated_time": YEAR_ONE,
        "previous_updated_time": None,
    }
    data = _require_keyword_data(_parse(_encode(_one_item_document(hollow))))
    assert data.serp_info.state is FieldState.STATED
    serp = data.serp_info.value
    assert serp is not None
    assert serp.check_url.state is FieldState.JSON_NULL
    assert serp.last_updated_time.value == YEAR_ONE

    data = _require_keyword_data(_parse())
    assert data.serp_info.state is FieldState.STATED
    assert data.serp_info.value is not None
    assert data.serp_info.value.check_url.state is FieldState.STATED


@pytest.mark.parametrize(
    "url",
    [
        "not a url at all",
        "https://www.google.com/search?q=x&hl=en",
        "  https://example.test/path?a=b  ",
        "ftp://example.test/",
    ],
)
def test_check_url_is_preserved_text_exactly_without_normalization(url: str) -> None:
    item = _template_item()
    item["keyword_data"]["serp_info"]["check_url"] = url
    data = _require_keyword_data(_parse(_encode(_one_item_document(item))))
    serp = data.serp_info.value
    assert serp is not None
    assert serp.check_url.value == url


def test_serp_item_types_absent_null_and_empty_states() -> None:
    absent = _template_item()
    del absent["keyword_data"]["serp_info"]["serp_item_types"]
    data = _require_keyword_data(_parse(_encode(_one_item_document(absent))))
    assert data.serp_info.value is not None
    assert data.serp_info.value.serp_item_types.state is FieldState.ABSENT

    empty = _template_item()
    empty["keyword_data"]["serp_info"]["serp_item_types"] = []
    data = _require_keyword_data(_parse(_encode(_one_item_document(empty))))
    assert data.serp_info.value is not None
    assert data.serp_info.value.serp_item_types.value == ()


@pytest.mark.parametrize(
    "key", ["clickstream_keyword_info", "keyword_info_normalized_with_clickstream"]
)
def test_request_disabled_clickstream_states(key: str) -> None:
    absent = _template_item()
    del absent["keyword_data"][key]
    data = _require_keyword_data(_parse(_encode(_one_item_document(absent))))
    assert getattr(data, key).state is FieldState.NOT_REQUESTED

    nulled = _template_item()
    nulled["keyword_data"][key] = None
    data = _require_keyword_data(_parse(_encode(_one_item_document(nulled))))
    assert getattr(data, key).state is FieldState.NOT_REQUESTED

    populated = _template_item()
    populated["keyword_data"][key] = {"search_volume": 10}
    assert (
        _parse_error(_encode(_one_item_document(populated))) == "request_disabled_populated"
    )


def test_bing_normalized_states_and_unsupported_shape() -> None:
    absent = _template_item()
    del absent["keyword_data"]["keyword_info_normalized_with_bing"]
    data = _require_keyword_data(_parse(_encode(_one_item_document(absent))))
    assert data.keyword_info_normalized_with_bing.state is FieldState.ABSENT

    nulled = _template_item()
    nulled["keyword_data"]["keyword_info_normalized_with_bing"] = None
    data = _require_keyword_data(_parse(_encode(_one_item_document(nulled))))
    assert data.keyword_info_normalized_with_bing.state is FieldState.JSON_NULL

    populated = _template_item()
    populated["keyword_data"]["keyword_info_normalized_with_bing"] = {"search_volume": 10}
    with pytest.raises(RelatedKeywordsParseError) as excinfo:
        _parse(_encode(_one_item_document(populated)))
    # A distinct code so provider drift here is a review trigger, not a generic type error.
    assert excinfo.value.code == "unsupported_shape"


def test_backlinks_decimal_values_accept_integer_and_fraction_forms() -> None:
    item = _template_item()
    item["keyword_data"]["avg_backlinks_info"]["backlinks"] = 141
    item["keyword_data"]["avg_backlinks_info"]["rank"] = Decimal("190.9")
    data = _require_keyword_data(_parse(_encode(_one_item_document(item))))
    links = data.avg_backlinks_info.value
    assert links is not None
    assert links.backlinks.value == Decimal(141)
    assert links.rank.value == Decimal("190.9")
    assert isinstance(links.rank.value, Decimal)


def test_no_cross_field_inference_between_relationships_and_serp() -> None:
    item = _template_item()
    item["keyword_data"]["serp_info"] = None
    item["related_keywords"] = ["alpha", "beta"]
    parsed = _require_result(_parse(_encode(_one_item_document(item)))).items[0]
    assert parsed.related_keywords.state is FieldState.STATED
    assert parsed.keyword_data.value is not None
    assert parsed.keyword_data.value.serp_info.state is FieldState.JSON_NULL

    item = _template_item()
    item["related_keywords"] = None
    parsed = _require_result(_parse(_encode(_one_item_document(item)))).items[0]
    assert parsed.related_keywords.state is FieldState.JSON_NULL
    assert parsed.keyword_data.value is not None
    assert parsed.keyword_data.value.serp_info.state is FieldState.STATED
