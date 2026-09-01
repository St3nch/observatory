"""RANK-04: Ranked Keywords strict parser and the RANK-03 conformance fixture.

Golden assertions pin one Capture's observed testimony. They are fixture facts, not parser
invariants, except where the accepted RANK-04 Steward reconciliation explicitly locks a rule.
Synthetic assertions prove parser behaviour and never claim provider occurrence.
"""

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
    RANKED_KEYWORDS_ADAPTER_CONTRACT,
    RELATED_KEYWORDS_ADAPTER_CONTRACT,
    TARGET_METRICS_ADAPTER_CONTRACT,
    DocumentError,
    validate_ranked_keywords_http_parameters,
)
from observatory.dataforseo_ai_optimization_llm_mentions_historical import parse_historical
from observatory.dataforseo_ai_optimization_search_mentions import parse_search_mentions
from observatory.dataforseo_ai_optimization_target_metrics import parse_target_metrics
from observatory.dataforseo_google_organic import parse_google_organic
from observatory.dataforseo_google_ranked_keywords import (
    REQUESTED_ITEM_TYPES,
    KeywordData,
    KeywordInfo,
    RankedKeywordsIR,
    RankedKeywordsItem,
    RankedKeywordsParseError,
    RankedKeywordsResult,
    RankedSerpElement,
    SerpItem,
    parse_ranked_keywords,
)
from observatory.dataforseo_google_related_keywords import parse_related_keywords
from observatory.dataforseo_keyword_overview import (
    FieldState,
    ParseClassification,
    parse_keyword_overview,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
FIXTURE_PATH = FIXTURES / "dataforseo_google_ranked_keywords_rank03.json"

RANK03_BODY_BYTES = 390955
RANK03_BODY_SHA256 = "5b0e7cb6a03a921039a2845c62bd6a91eba9d61e2b54240e9af15414ba1fbc84"

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
    "dataforseo_google_related_keywords_rk02.json": (
        "e128f2f81d51479237f1bd7e51feee3dfffcae4596558ebff67365f03cd1decb"
    ),
}

TARGET = "theconspiratory.com"
ORDER_BY = "ranked_serp_element.serp_item.rank_group,asc"
ITEM_TYPES = ["organic", "paid", "featured_snippet", "local_pack", "ai_overview_reference"]

PARAMETERS: dict[str, object] = {
    "contract": RANKED_KEYWORDS_ADAPTER_CONTRACT,
    "historical_serp_mode": "all",
    "ignore_synonyms": False,
    "include_clickstream_data": False,
    "item_types": list(ITEM_TYPES),
    "language_code": "en",
    "limit": 100,
    "load_rank_absolute": True,
    "location_code": 2840,
    "offset": 0,
    "order_by": [ORDER_BY],
    "target": TARGET,
}

APEX = "theconspiratory.com"
WWW = "www.theconspiratory.com"
MIXED_HOST_PATHS = ("/theory/atlantis", "/theory/denver-airport")

METRICS_ORGANIC_BUCKETS = (0, 0, 0, 9, 18, 43, 59, 51, 37, 14, 14, 3)
METRICS_ABSOLUTE_ORGANIC_BUCKETS = (0, 0, 0, 4, 17, 15, 42, 52, 49, 35, 19, 11)
BUCKET_NAMES = (
    "pos_1",
    "pos_2_3",
    "pos_4_10",
    "pos_11_20",
    "pos_21_30",
    "pos_31_40",
    "pos_41_50",
    "pos_51_60",
    "pos_61_70",
    "pos_71_80",
    "pos_81_90",
    "pos_91_100",
)

CLICKSTREAM_AGGREGATE_FIELDS = (
    "clickstream_etv",
    "clickstream_gender_distribution",
    "clickstream_age_distribution",
)
UNSUPPORTED_SERP_CHILDREN = (
    "about_this_result",
    "backlinks_info",
    "extended_snippet",
    "links",
    "rating",
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


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------


def _fixture() -> bytes:
    return FIXTURE_PATH.read_bytes()


def _parse(
    body: bytes | None = None, parameters: dict[str, object] | None = None
) -> RankedKeywordsIR:
    return parse_ranked_keywords(
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


def _first_serp_item(document: dict[str, Any]) -> dict[str, Any]:
    serp = _first_item(document)["ranked_serp_element"]["serp_item"]
    assert isinstance(serp, dict)
    return serp


def _first_keyword_info(document: dict[str, Any]) -> dict[str, Any]:
    info = _first_item(document)["keyword_data"]["keyword_info"]
    assert isinstance(info, dict)
    return info


def _template_item() -> dict[str, Any]:
    return copy.deepcopy(_first_item(_decoded()))


def _one_item_document(item: dict[str, Any]) -> dict[str, Any]:
    """A single-item success document built from the real fixture envelope."""

    document = _decoded()
    result = _result_obj(document)
    result["items"] = [item]
    result["items_count"] = 1
    return document


def _require_result(ir: RankedKeywordsIR) -> RankedKeywordsResult:
    result = ir.result
    assert result is not None
    return result


def _elements(ir: RankedKeywordsIR) -> tuple[RankedSerpElement, ...]:
    out: list[RankedSerpElement] = []
    for item in _require_result(ir).items:
        assert item.ranked_serp_element.state is FieldState.STATED
        assert item.ranked_serp_element.value is not None
        out.append(item.ranked_serp_element.value)
    return tuple(out)


def _serp_items(ir: RankedKeywordsIR) -> tuple[SerpItem, ...]:
    return tuple(element.serp_item for element in _elements(ir))


def _keyword_datas(ir: RankedKeywordsIR) -> tuple[KeywordData, ...]:
    out: list[KeywordData] = []
    for item in _require_result(ir).items:
        assert item.keyword_data.state is FieldState.STATED
        assert item.keyword_data.value is not None
        out.append(item.keyword_data.value)
    return tuple(out)


def _keyword_infos(ir: RankedKeywordsIR) -> tuple[KeywordInfo, ...]:
    out: list[KeywordInfo] = []
    for data in _keyword_datas(ir):
        assert data.keyword_info.state is FieldState.STATED
        assert data.keyword_info.value is not None
        out.append(data.keyword_info.value)
    return tuple(out)


def _only_item(ir: RankedKeywordsIR) -> RankedKeywordsItem:
    result = _require_result(ir)
    assert len(result.items) == 1
    return result.items[0]


def _only_serp_item(ir: RankedKeywordsIR) -> SerpItem:
    element = _only_item(ir).ranked_serp_element
    assert element.value is not None
    return element.value.serp_item


def _only_keyword_data(ir: RankedKeywordsIR) -> KeywordData:
    data = _only_item(ir).keyword_data
    assert data.value is not None
    return data.value


def _parse_error(body: bytes, parameters: dict[str, object] | None = None) -> str:
    with pytest.raises(RankedKeywordsParseError) as excinfo:
        _parse(body, parameters)
    return excinfo.value.code


def _buckets_tuple(buckets: Any) -> tuple[int, ...]:
    return tuple(getattr(buckets, name) for name in BUCKET_NAMES)


# --------------------------------------------------------------------------------------
# Fixture identity and test isolation
# --------------------------------------------------------------------------------------


def test_frozen_fixture_independent_sha256_and_length() -> None:
    raw = _fixture()
    assert len(raw) == RANK03_BODY_BYTES
    assert hashlib.sha256(raw).hexdigest() == RANK03_BODY_SHA256


def test_existing_fixtures_remain_byte_identical() -> None:
    for name, digest in PRIOR_FIXTURES.items():
        assert hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest() == digest


def test_existing_provider_parsers_still_read_their_own_fixtures() -> None:
    """RANK-04 shares only the Field/ParseClassification vocabulary; prove no regression."""

    ai_target = {
        "keyword": "generative engine optimization",
        "match_type": "word_match",
        "search_filter": "include",
        "search_scope": ["answer"],
    }
    keyword_overview = parse_keyword_overview(
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
    assert keyword_overview.outcome is ParseClassification.ADMITTED

    organic = parse_google_organic(
        (FIXTURES / "dataforseo_google_organic_pf10.json").read_bytes(),
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

    target_metrics = parse_target_metrics(
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
    assert target_metrics.outcome is ParseClassification.ADMITTED

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

    related = parse_related_keywords(
        (FIXTURES / "dataforseo_google_related_keywords_rk02.json").read_bytes(),
        {
            "contract": RELATED_KEYWORDS_ADAPTER_CONTRACT,
            "depth": 3,
            "ignore_synonyms": False,
            "include_clickstream_data": False,
            "include_seed_keyword": True,
            "include_serp_info": True,
            "keyword": "conspiracy theories",
            "language_code": "en",
            "limit": 1000,
            "location_code": 2840,
            "offset": 0,
            "order_by": ["keyword_data.keyword_info.search_volume,desc"],
            "replace_with_core_keyword": False,
        },
    )
    assert related.outcome is ParseClassification.ADMITTED


def test_ordinary_tests_read_only_the_committed_fixture() -> None:
    # Tokens are assembled so this assertion cannot match its own source text.
    forbidden = ("/" + "tmp", ".local/" + "share/observatory", "evidence" + "_root")
    sources = (
        Path(__file__).read_text(encoding="utf-8"),
        (
            Path(__file__).resolve().parents[1]
            / "src"
            / "observatory"
            / "dataforseo_google_ranked_keywords.py"
        ).read_text(encoding="utf-8"),
    )
    for text in sources:
        for token in forbidden:
            assert token not in text
    assert FIXTURE_PATH.parent == FIXTURES
    assert FIXTURES.parent == Path(__file__).resolve().parent


def test_autouse_guard_blocks_public_network() -> None:
    with pytest.raises(AssertionError):
        socket.create_connection(("api.dataforseo.com", 443))


def test_no_credentials_in_environment() -> None:
    assert os.environ.get("OBSERVATORY_DATAFORSEO_LOGIN") is None
    assert os.environ.get("OBSERVATORY_DATAFORSEO_PASSWORD") is None


def test_parser_module_imports_no_postgresql_or_recipe_seam() -> None:
    """The parser is a pure body/parameters function: no storage, Recipe, or API seam."""

    source = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "observatory"
        / "dataforseo_google_ranked_keywords.py"
    ).read_text(encoding="utf-8")
    for token in ("psycopg", "provider_recipe", "httpx", "observatory.api", "evidence"):
        assert token not in source
    # Exactly the three permitted imports from other Observatory modules.
    assert source.count("from observatory.") == 2
    assert "from observatory.capture_event import RANKED_KEYWORDS_ADAPTER_CONTRACT" in source
    assert (
        "from observatory.dataforseo_keyword_overview import "
        "Field, FieldState, ParseClassification" in source
    )


# --------------------------------------------------------------------------------------
# Golden envelope, Attempt, echo, and result context
# --------------------------------------------------------------------------------------


def test_golden_envelope_and_task_testimony() -> None:
    ir = _parse()
    assert ir.outcome is ParseClassification.ADMITTED
    assert ir.version == "0.1.20260831"
    assert ir.status_code == 20000
    assert ir.status_message == "Ok."
    assert ir.duration == "1.4853 sec."
    assert ir.cost == Decimal("0.024")
    assert isinstance(ir.cost, Decimal)
    assert ir.tasks_count == 1
    assert ir.tasks_error == 0
    assert ir.task_id == "09010532-1463-0381-0000-8f2c825ce89d"
    assert ir.task_status_code == 20000
    assert ir.task_status_message == "Ok."
    assert ir.task_duration == "1.4599 sec."
    assert ir.task_cost == Decimal("0.024")
    assert isinstance(ir.task_cost, Decimal)
    assert ir.task_path == ("v3", "dataforseo_labs", "google", "ranked_keywords", "live")
    assert ir.result_count == 1


def test_golden_attempt_context_is_the_frozen_contract() -> None:
    request = _parse().request
    assert request.contract == RANKED_KEYWORDS_ADAPTER_CONTRACT
    assert request.target == TARGET
    assert request.location_code == 2840
    assert request.language_code == "en"
    assert request.item_types == REQUESTED_ITEM_TYPES
    assert request.ignore_synonyms is False
    assert request.include_clickstream_data is False
    assert request.limit == 100
    assert request.offset == 0
    assert request.load_rank_absolute is True
    assert request.historical_serp_mode == "all"
    assert request.order_by == (ORDER_BY,)


def test_golden_provider_echo_is_typed_testimony() -> None:
    echo = _parse().echo
    assert echo.api.value == "dataforseo_labs"
    assert echo.function.value == "ranked_keywords"
    assert echo.se_type.value == "google"
    assert echo.target.value == TARGET
    assert echo.location_code.value == 2840
    assert echo.language_code.value == "en"
    assert echo.item_types.value == REQUESTED_ITEM_TYPES
    assert echo.ignore_synonyms.value is False
    assert echo.include_clickstream_data.value is False
    assert echo.limit.value == 100
    assert echo.offset.value == 0
    assert echo.load_rank_absolute.value is True
    assert echo.historical_serp_mode.value == "all"
    assert echo.order_by.value == (ORDER_BY,)


def test_golden_result_context_and_returned_prefix_topology() -> None:
    result = _require_result(_parse())
    assert result.se_type.value == "google"
    assert result.target.value == TARGET
    assert result.location_code.value == 2840
    assert result.language_code.value == "en"
    # 100 returned rows out of a 248-match corpus: a bounded prefix, not the corpus.
    assert result.total_count == 248
    assert result.items_count == 100
    assert len(result.items) == 100
    assert result.total_count != result.items_count
    assert tuple(item.provider_array_index for item in result.items) == tuple(range(100))
    assert all(item.se_type == "google" for item in result.items)


# --------------------------------------------------------------------------------------
# Golden aggregates
# --------------------------------------------------------------------------------------


def test_golden_metrics_organic_full_corpus_aggregate() -> None:
    organic = _require_result(_parse()).metrics.organic
    assert _buckets_tuple(organic.positions) == METRICS_ORGANIC_BUCKETS
    assert organic.count == 248
    assert organic.etv.value == Decimal("50.1299999281764")
    assert isinstance(organic.etv.value, Decimal)
    assert organic.estimated_paid_traffic_cost.value == Decimal("4.540859959553927")
    assert isinstance(organic.estimated_paid_traffic_cost.value, Decimal)
    assert (organic.is_new, organic.is_up, organic.is_down, organic.is_lost) == (
        248,
        0,
        0,
        0,
    )


def test_golden_metrics_absolute_organic_has_a_different_shape_and_sum() -> None:
    result = _require_result(_parse())
    absolute = result.metrics_absolute.organic
    assert _buckets_tuple(absolute.positions) == METRICS_ABSOLUTE_ORGANIC_BUCKETS
    assert (absolute.is_new, absolute.is_up, absolute.is_down, absolute.is_lost) == (
        248,
        0,
        0,
        0,
    )
    # The distinct shape is structural: metrics_absolute never states these three.
    assert not hasattr(absolute, "count")
    assert not hasattr(absolute, "etv")
    assert not hasattr(absolute, "estimated_paid_traffic_cost")


def test_golden_248_versus_244_arithmetic_is_fixture_testimony_only() -> None:
    """The parser imposes no bucket-sum equation; these are one-Capture observations."""

    result = _require_result(_parse())
    assert sum(METRICS_ORGANIC_BUCKETS) == 248
    assert sum(_buckets_tuple(result.metrics.organic.positions)) == 248
    assert sum(_buckets_tuple(result.metrics_absolute.organic.positions)) == 244
    assert sum(_buckets_tuple(result.metrics.organic.positions)) != sum(
        _buckets_tuple(result.metrics_absolute.organic.positions)
    )
    assert result.metrics.organic.count == result.total_count
    # ... and yet the absolute buckets disagree with that same count by four.
    assert sum(_buckets_tuple(result.metrics_absolute.organic.positions)) == 244


def test_golden_returned_prefix_covers_the_corpus_rank_group_buckets() -> None:
    result = _require_result(_parse())
    returned: collections.Counter[str] = collections.Counter()
    for serp in _serp_items(_parse()):
        group = serp.rank_group
        if 11 <= group <= 20:
            returned["pos_11_20"] += 1
        elif 21 <= group <= 30:
            returned["pos_21_30"] += 1
        elif 31 <= group <= 40:
            returned["pos_31_40"] += 1
        elif 41 <= group <= 50:
            returned["pos_41_50"] += 1
    buckets = result.metrics.organic.positions
    assert returned["pos_11_20"] == buckets.pos_11_20 == 9
    assert returned["pos_21_30"] == buckets.pos_21_30 == 18
    assert returned["pos_31_40"] == buckets.pos_31_40 == 43
    # The prefix stops mid-bucket: 30 of the corpus 59 rows in 41..50 were returned.
    assert returned["pos_41_50"] == 30
    assert buckets.pos_41_50 == 59


def test_golden_all_five_requested_families_present_zero_is_not_absence() -> None:
    result = _require_result(_parse())
    for name in REQUESTED_ITEM_TYPES:
        assert getattr(result.metrics, name) is not None
        assert getattr(result.metrics_absolute, name) is not None
    for name in ("paid", "featured_snippet", "local_pack", "ai_overview_reference"):
        family = getattr(result.metrics, name)
        assert family.count == 0
        assert family.etv.state is FieldState.STATED
        assert family.etv.value == Decimal(0)
        assert family.estimated_paid_traffic_cost.value == Decimal(0)
        assert _buckets_tuple(family.positions) == (0,) * 12
        assert (family.is_new, family.is_up, family.is_down, family.is_lost) == (0,) * 4
        absolute = getattr(result.metrics_absolute, name)
        assert _buckets_tuple(absolute.positions) == (0,) * 12


def test_golden_every_aggregate_clickstream_locus_is_not_requested() -> None:
    result = _require_result(_parse())
    for name in REQUESTED_ITEM_TYPES:
        for holder in (getattr(result.metrics, name), getattr(result.metrics_absolute, name)):
            for field_name in CLICKSTREAM_AGGREGATE_FIELDS:
                field = getattr(holder, field_name)
                assert field.state is FieldState.NOT_REQUESTED
                assert field.value is None


# --------------------------------------------------------------------------------------
# Golden ranked occurrence, rank, and movement testimony
# --------------------------------------------------------------------------------------


def test_golden_ranked_occurrence_ranks_and_open_vocabularies() -> None:
    serps = _serp_items(_parse())
    assert len(serps) == 100
    groups = tuple(serp.rank_group for serp in serps)
    absolutes = tuple(serp.rank_absolute for serp in serps)
    assert (min(groups), max(groups)) == (14, 46)
    assert (min(absolutes), max(absolutes)) == (18, 57)
    # Provider order: rank_group is nondecreasing here, rank_absolute is not. Neither is a
    # parser ordering rule.
    assert all(groups[i] <= groups[i + 1] for i in range(99))
    assert not all(absolutes[i] <= absolutes[i + 1] for i in range(99))
    assert all(serp.type == "organic" for serp in serps)
    assert all(serp.position.value == "left" for serp in serps)
    assert all(serp.rank_group < serp.rank_absolute for serp in serps)


def test_golden_duplicate_rank_values_remain_distinct_occurrences() -> None:
    serps = _serp_items(_parse())
    groups = collections.Counter(serp.rank_group for serp in serps)
    absolutes = collections.Counter(serp.rank_absolute for serp in serps)
    assert len(groups) < 100
    assert len(absolutes) < 100
    assert max(groups.values()) > 1
    assert max(absolutes.values()) > 1
    # No collapsing: every returned row is still its own occurrence with its own index.
    assert sum(groups.values()) == 100


def test_golden_rank_info_is_separate_from_backlink_main_domain_rank() -> None:
    ir = _parse()
    serps = _serp_items(ir)
    page_ranks: collections.Counter[int | None] = collections.Counter()
    main_ranks: collections.Counter[int | None] = collections.Counter()
    for serp in serps:
        assert serp.rank_info.state is FieldState.STATED
        assert serp.rank_info.value is not None
        page_ranks[serp.rank_info.value.page_rank.value] += 1
        main_ranks[serp.rank_info.value.main_domain_rank.value] += 1
    assert page_ranks == collections.Counter({0: 100})
    assert main_ranks == collections.Counter({0: 99, 36: 1})
    # `rank_info.main_domain_rank` is not `avg_backlinks_info.main_domain_rank`.
    backlink_ranks = []
    for data in _keyword_datas(ir):
        assert data.avg_backlinks_info.value is not None
        backlink_ranks.append(data.avg_backlinks_info.value.main_domain_rank.value)
    assert all(isinstance(value, Decimal) for value in backlink_ranks)
    assert all(value is not None and value > 100 for value in backlink_ranks)


def test_golden_movement_paths_are_contradictory_and_unreconciled() -> None:
    ir = _parse()
    for element in _elements(ir):
        assert element.is_lost.value is False
        changes = element.serp_item.rank_changes
        assert changes.state is FieldState.STATED
        assert changes.value is not None
        assert changes.value.is_new.value is True
        assert changes.value.is_up.value is False
        assert changes.value.is_down.value is False
        assert changes.value.previous_rank_absolute.state is FieldState.JSON_NULL
        # ... while every row nevertheless states a previous SERP clock.
        assert element.previous_updated_time.state is FieldState.STATED
    organic = _require_result(ir).metrics.organic
    assert (organic.is_new, organic.is_up, organic.is_down, organic.is_lost) == (
        248,
        0,
        0,
        0,
    )


# --------------------------------------------------------------------------------------
# Golden URL, host, and exact-text testimony
# --------------------------------------------------------------------------------------


def test_golden_apex_and_www_hosts_stay_distinct_provider_strings() -> None:
    serps = _serp_items(_parse())
    domains = collections.Counter(serp.domain.value for serp in serps)
    assert domains == collections.Counter({APEX: 75, WWW: 25})
    assert {serp.main_domain.value for serp in serps} == {APEX}
    # Every www-domain row still names the apex website_name; three separate strings.
    www_names = {serp.website_name.value for serp in serps if serp.domain.value == WWW}
    assert www_names == {APEX}
    assert sum(1 for serp in serps if serp.domain.value == WWW) == 25


def test_golden_url_and_relative_url_multiplicity() -> None:
    serps = _serp_items(_parse())
    urls = collections.Counter(serp.url for serp in serps)
    relatives = collections.Counter(serp.relative_url.value for serp in serps)
    assert len(urls) == 57
    assert len(relatives) == 55
    # Recomputable from IR without the parser storing any cluster or importance score.
    assert max(urls.values()) == 9
    assert urls["https://theconspiratory.com/theory/elisa-lam"] == 9


def test_golden_mixed_host_paths_stay_two_host_specific_url_occurrences() -> None:
    serps = _serp_items(_parse())
    for path in MIXED_HOST_PATHS:
        hosts = {serp.domain.value for serp in serps if serp.relative_url.value == path}
        assert hosts == {APEX, WWW}
        urls = {serp.url for serp in serps if serp.relative_url.value == path}
        assert urls == {
            f"https://{APEX}{path}",
            f"https://{WWW}{path}",
        }
    assert len(MIXED_HOST_PATHS) == 2


def test_golden_exact_text_fields_are_never_normalized() -> None:
    serps = _serp_items(_parse())
    first = serps[0]
    assert first.url == "https://theconspiratory.com/theory/elisa-lam"
    assert first.relative_url.value == "/theory/elisa-lam"
    assert first.title.value == "Elisa Lam's 2013 death at the Cecil Hotel was a murder or ..."
    assert first.breadcrumb.value == "https://theconspiratory.com › Case files"
    assert first.xpath.value is not None
    assert first.xpath.value.startswith("/html[1]/body[1]/")
    assert first.description.value is not None
    # Em dash and non-breaking space survive byte-exactly.
    assert "—" in first.description.value
    assert " " in first.description.value
    assert first.highlighted.value == ("Elisa Lam", "a 21-year-old student from Vancouver")


def test_golden_pre_snippet_is_free_text_never_a_clock() -> None:
    serps = _serp_items(_parse())
    stated: list[str] = [
        serp.pre_snippet.value for serp in serps if serp.pre_snippet.value is not None
    ]
    nulls = [serp for serp in serps if serp.pre_snippet.state is FieldState.JSON_NULL]
    assert len(nulls) == 19
    assert any(value.endswith("days ago") for value in stated)
    # A date-looking provider string is retained as text, not parsed as a timestamp.
    assert "07/08/2026 00:00:00" in stated


# --------------------------------------------------------------------------------------
# Golden SERP composition versus target participation
# --------------------------------------------------------------------------------------


def test_golden_serp_composition_is_not_target_participation() -> None:
    ir = _parse()
    elements = _elements(ir)
    compositions = [element.serp_item_types.value for element in elements]
    assert all(composition is not None for composition in compositions)
    ai_overview = sum(1 for row in compositions if row is not None and "ai_overview" in row)
    featured = sum(1 for row in compositions if row is not None and "featured_snippet" in row)
    assert ai_overview == 80
    assert featured == 4
    result = _require_result(ir)
    # Target-level participation for both loci is a present, structural zero.
    assert result.metrics.ai_overview_reference.count == 0
    assert result.metrics.featured_snippet.count == 0
    # ... and the four featured-snippet composition rows are still organic non-snippet rows.
    for element in elements:
        types = element.serp_item_types.value
        if types is not None and "featured_snippet" in types:
            assert element.serp_item.is_featured_snippet.value is False
            assert element.serp_item.type == "organic"
    assert all(serp.is_featured_snippet.value is False for serp in _serp_items(ir))


def test_golden_serp_item_types_preserve_provider_order_and_open_vocabulary() -> None:
    elements = _elements(_parse())
    assert elements[0].serp_item_types.value == (
        "ai_overview",
        "organic",
        "video",
        "people_also_ask",
        "related_searches",
        "images",
    )
    vocabulary = {
        name
        for element in elements
        if element.serp_item_types.value is not None
        for name in element.serp_item_types.value
    }
    # Fifteen observed SERP feature strings; the parser closes none of them.
    assert len(vocabulary) == 15
    assert {"knowledge_graph", "perspectives", "scholarly_articles"} <= vocabulary


# --------------------------------------------------------------------------------------
# Golden duplicated provider paths
# --------------------------------------------------------------------------------------


def test_golden_six_duplicated_paths_are_independently_retained() -> None:
    """They agree 100/100 here. Agreement is testimony, never a parser requirement."""

    ir = _parse()
    elements = _elements(ir)
    datas = _keyword_datas(ir)
    agreements = 0
    for element, data in zip(elements, datas, strict=True):
        assert data.serp_info.state is FieldState.STATED
        serp_info = data.serp_info.value
        assert serp_info is not None
        assert element.check_url.value == serp_info.check_url.value
        assert element.se_results_count.value == serp_info.se_results_count.value
        assert element.last_updated_time.value == serp_info.last_updated_time.value
        assert element.previous_updated_time.value == serp_info.previous_updated_time.value
        assert element.serp_item_types.value == serp_info.serp_item_types.value
        assert element.se_type.value == serp_info.se_type.value
        agreements += 1
    assert agreements == 100


def test_golden_duplicated_keyword_difficulty_paths_are_separate() -> None:
    ir = _parse()
    pairs = 0
    for element, data in zip(_elements(ir), _keyword_datas(ir), strict=True):
        assert data.keyword_properties.value is not None
        assert (
            element.keyword_difficulty.value
            == data.keyword_properties.value.keyword_difficulty.value
        )
        assert element.keyword_difficulty.state is FieldState.STATED
        pairs += 1
    assert pairs == 100


# --------------------------------------------------------------------------------------
# Golden keyword enrichment, monthly Data Periods, and clocks
# --------------------------------------------------------------------------------------


def test_golden_keyword_strings_are_exact_and_never_normalized() -> None:
    keywords = [data.keyword for data in _keyword_datas(_parse())]
    assert len(keywords) == 100
    assert len(set(keywords)) == 100
    # Exact near-duplicate spelling/hyphenation pairs survive as different keywords.
    for left, right in (
        ("tb test lam elisa", "tb test lam-elisa"),
        ("project sea spray", "project sea-spray"),
    ):
        assert left in keywords
        assert right in keywords
        assert left != right


def test_golden_categories_preserve_order_and_duplicates() -> None:
    ir = _parse()
    found = None
    for data, info in zip(_keyword_datas(ir), _keyword_infos(ir), strict=True):
        if data.keyword == "yuba county 5 map":
            found = info.categories.value
    assert found == (10007, 10108, 10108, 10756, 10756, 11500, 13418, 13600, 13600, 13601)
    nulls = sum(
        1 for info in _keyword_infos(ir) if info.categories.state is FieldState.JSON_NULL
    )
    assert nulls == 6


def test_golden_keyword_info_scalar_states_and_decimal_typing() -> None:
    infos = _keyword_infos(_parse())
    assert all(info.competition_level.value == "LOW" for info in infos)
    competitions = [info.competition.value for info in infos]
    assert all(isinstance(value, Decimal) for value in competitions)
    # Real numeric zero competition coexists with a "LOW" competition level.
    assert sum(1 for value in competitions if value == Decimal(0)) == 79
    assert Decimal("0.20000000298023224") in competitions


def test_golden_cpc_and_bid_nullability_are_independent() -> None:
    infos = _keyword_infos(_parse())
    combinations: collections.Counter[tuple[bool, bool]] = collections.Counter()
    for info in infos:
        has_cpc = info.cpc.state is FieldState.STATED
        has_bids = (
            info.low_top_of_page_bid.state is FieldState.STATED
            and info.high_top_of_page_bid.state is FieldState.STATED
        )
        combinations[(has_cpc, has_bids)] += 1
    assert combinations[(True, False)] == 6
    assert combinations[(False, True)] == 2
    assert combinations[(True, True)] == 2
    assert combinations[(False, False)] == 90


def test_golden_monthly_rows_and_two_distinct_windows() -> None:
    infos = _keyword_infos(_parse())
    rows = 0
    windows: collections.Counter[tuple[tuple[int, int], tuple[int, int]]] = (
        collections.Counter()
    )
    for info in infos:
        assert info.monthly_searches.state is FieldState.STATED
        series = info.monthly_searches.value
        assert series is not None
        rows += len(series)
        assert tuple(point.provider_array_index for point in series) == tuple(
            range(len(series))
        )
        windows[
            ((series[0].year, series[0].month), (series[-1].year, series[-1].month))
        ] += 1
    assert rows == 1200
    # No honest Capture-global 12-month Data Period: two row-local windows coexist.
    assert windows == collections.Counter(
        {((2026, 7), (2025, 8)): 62, ((2026, 6), (2025, 7)): 38}
    )


def test_golden_current_volume_is_independent_from_the_newest_monthly_point() -> None:
    disagreements = 0
    for info in _keyword_infos(_parse()):
        series = info.monthly_searches.value
        assert series is not None
        if info.search_volume.value != series[0].search_volume:
            disagreements += 1
    assert disagreements == 81


def test_golden_search_volume_trend_preserves_real_negative_values() -> None:
    negatives: collections.Counter[str] = collections.Counter()
    for info in _keyword_infos(_parse()):
        assert info.search_volume_trend.state is FieldState.STATED
        trend = info.search_volume_trend.value
        assert trend is not None
        for name in ("monthly", "quarterly", "yearly"):
            value = getattr(trend, name).value
            if value is not None and value < 0:
                negatives[name] += 1
    assert negatives == collections.Counter({"quarterly": 64, "yearly": 55, "monthly": 46})


def test_golden_keyword_properties_clustering_and_detected_language() -> None:
    clustering: collections.Counter[str | None] = collections.Counter()
    languages: collections.Counter[str | None] = collections.Counter()
    core_keywords = 0
    for data in _keyword_datas(_parse()):
        props = data.keyword_properties.value
        assert props is not None
        clustering[props.synonym_clustering_algorithm.value] += 1
        languages[props.detected_language.value] += 1
        if props.core_keyword.state is FieldState.STATED:
            core_keywords += 1
    assert clustering == collections.Counter(
        {"text_processing": 55, None: 44, "keyword_metrics": 1}
    )
    # Detected language disagrees with the requested English locale on six rows.
    assert languages == collections.Counter({"en": 94, "nl": 3, "hu": 1, "de": 1, "es": 1})
    assert core_keywords == 35


def test_golden_core_keyword_and_clustering_are_independent() -> None:
    combinations: collections.Counter[tuple[bool, bool]] = collections.Counter()
    for data in _keyword_datas(_parse()):
        props = data.keyword_properties.value
        assert props is not None
        combinations[
            (
                props.core_keyword.state is FieldState.STATED,
                props.synonym_clustering_algorithm.state is FieldState.STATED,
            )
        ] += 1
    # Both fields vary, and neither state determines the other in a shared 2x2 table.
    assert len(combinations) >= 2
    assert sum(combinations.values()) == 100


def test_golden_search_intent_distribution_and_foreign_intent_states() -> None:
    intents: collections.Counter[str | None] = collections.Counter()
    foreign_states: collections.Counter[FieldState] = collections.Counter()
    for data in _keyword_datas(_parse()):
        intent = data.search_intent_info.value
        assert intent is not None
        intents[intent.main_intent.value] += 1
        foreign_states[intent.foreign_intent.state] += 1
    assert intents == collections.Counter(
        {"informational": 89, "navigational": 9, "transactional": 1, "commercial": 1}
    )
    assert foreign_states[FieldState.JSON_NULL] == 86
    assert foreign_states[FieldState.STATED] == 14


def _stated_clocks(values: list[str | None]) -> list[str]:
    assert all(value is not None for value in values)
    return [value for value in values if value is not None]


def test_golden_structure_local_clocks_stay_on_their_own_structures() -> None:
    ir = _parse()
    element_last = _stated_clocks(
        [element.last_updated_time.value for element in _elements(ir)]
    )
    element_prev = _stated_clocks(
        [element.previous_updated_time.value for element in _elements(ir)]
    )
    info_last = _stated_clocks(
        [info.last_updated_time.value for info in _keyword_infos(ir)]
    )
    intent_raw: list[str | None] = []
    backlinks_raw: list[str | None] = []
    serp_info_last: list[str | None] = []
    serp_info_prev: list[str | None] = []
    for data in _keyword_datas(ir):
        assert data.search_intent_info.value is not None
        assert data.avg_backlinks_info.value is not None
        assert data.serp_info.value is not None
        intent_raw.append(data.search_intent_info.value.last_updated_time.value)
        backlinks_raw.append(data.avg_backlinks_info.value.last_updated_time.value)
        serp_info_last.append(data.serp_info.value.last_updated_time.value)
        serp_info_prev.append(data.serp_info.value.previous_updated_time.value)
    intent_last = _stated_clocks(intent_raw)
    backlinks_last = _stated_clocks(backlinks_raw)
    assert (min(element_last), max(element_last)) == (
        "2026-07-10 21:54:27 +00:00",
        "2026-07-19 00:10:39 +00:00",
    )
    assert (min(element_prev), max(element_prev)) == (
        "2026-04-09 19:30:12 +00:00",
        "2026-06-02 02:24:49 +00:00",
    )
    assert (min(info_last), max(info_last)) == (
        "2026-07-10 17:48:53 +00:00",
        "2026-08-26 08:34:03 +00:00",
    )
    assert (min(intent_last), max(intent_last)) == (
        "2026-04-24 22:18:46 +00:00",
        "2026-05-08 06:10:49 +00:00",
    )
    assert (min(backlinks_last), max(backlinks_last)) == (
        "2026-07-10 21:54:31 +00:00",
        "2026-07-19 00:10:40 +00:00",
    )
    # Six axes, six different windows. Capture time (2026-09-01) appears on none of them.
    assert _stated_clocks(serp_info_last) == element_last
    assert _stated_clocks(serp_info_prev) == element_prev
    for values in (element_last, element_prev, info_last, intent_last, backlinks_last):
        assert all(not value.startswith("2026-09-01") for value in values)


def test_golden_provider_durations_are_strings_not_clocks() -> None:
    ir = _parse()
    assert ir.duration.endswith(" sec.")
    assert ir.task_duration.endswith(" sec.")


# --------------------------------------------------------------------------------------
# Golden clickstream, Bing, and unsupported null-only children
# --------------------------------------------------------------------------------------


def test_golden_every_keyword_clickstream_locus_is_not_requested() -> None:
    for data in _keyword_datas(_parse()):
        assert data.clickstream_keyword_info.state is FieldState.NOT_REQUESTED
        assert data.keyword_info_normalized_with_clickstream.state is (
            FieldState.NOT_REQUESTED
        )
    for serp in _serp_items(_parse()):
        assert serp.clickstream_etv.state is FieldState.NOT_REQUESTED


def test_golden_bing_normalization_is_json_null_not_not_requested() -> None:
    """Bing is not clickstream-controlled: its null is a different state entirely."""

    states = {
        (data.keyword_info_normalized_with_bing.state, data.clickstream_keyword_info.state)
        for data in _keyword_datas(_parse())
    }
    # One pair, and the two states in it differ: Bing null is not clickstream absence.
    assert states == {(FieldState.JSON_NULL, FieldState.NOT_REQUESTED)}


def test_golden_unsupported_null_only_serp_children() -> None:
    for serp in _serp_items(_parse()):
        for name in UNSUPPORTED_SERP_CHILDREN:
            field = getattr(serp, name)
            assert field.state is FieldState.JSON_NULL
            assert field.value is None
        # A same-named sibling elsewhere is not the same fact: avg_backlinks_info is
        # populated on all 100 rows while serp_item.backlinks_info is null on all 100.
        assert serp.backlinks_info.state is FieldState.JSON_NULL
    for data in _keyword_datas(_parse()):
        assert data.avg_backlinks_info.state is FieldState.STATED


def test_golden_serp_item_boolean_and_decimal_fields() -> None:
    serps = _serp_items(_parse())
    assert all(serp.amp_version.value is False for serp in serps)
    assert all(serp.is_image.value is False for serp in serps)
    assert all(serp.is_video.value is False for serp in serps)
    assert all(serp.is_malicious.value is False for serp in serps)
    assert all(isinstance(serp.etv.value, Decimal) for serp in serps)
    costs: collections.Counter[FieldState] = collections.Counter(
        serp.estimated_paid_traffic_cost.state for serp in serps
    )
    assert costs[FieldState.JSON_NULL] == 92
    assert costs[FieldState.STATED] == 8


# --------------------------------------------------------------------------------------
# Synthetic: strict decoding and numerics
# --------------------------------------------------------------------------------------


def test_synthetic_utf8_bom_is_rejected() -> None:
    assert _parse_error(b"\xef\xbb\xbf" + _fixture()) == "utf8_bom"


def test_synthetic_invalid_utf8_is_rejected() -> None:
    assert _parse_error(b'{"version": "\xff\xfe"}') == "invalid_utf8"


def test_synthetic_trailing_non_whitespace_is_rejected() -> None:
    assert _parse_error(_fixture() + b" trailing") == "trailing_data"
    # Trailing whitespace alone is not trailing data.
    assert _parse(_fixture() + b"\n \t\r\n").outcome is ParseClassification.ADMITTED


def test_synthetic_invalid_json_is_rejected() -> None:
    assert _parse_error(b"{not json") == "invalid_json"
    assert _parse_error(b"") == "invalid_json"


def test_synthetic_duplicate_object_member_is_rejected() -> None:
    body = _fixture().replace(b'"tasks_count":1', b'"tasks_count":1,"tasks_count":1', 1)
    assert _parse_error(body) == "duplicate_member"


@pytest.mark.parametrize("constant", [b"NaN", b"Infinity", b"-Infinity"])
def test_synthetic_non_finite_constants_are_rejected(constant: bytes) -> None:
    body = b'{"cost": ' + constant + b"}"
    assert _parse_error(body) == "non_finite_number"


def test_synthetic_root_must_be_an_object() -> None:
    assert _parse_error(b"[]") == "wrong_type"
    assert _parse_error(b'"text"') == "wrong_type"


@pytest.mark.parametrize(
    "literal",
    [b"0.024", b"24E-3", b"0.02400000000000000000000000001", b"0"],
)
def test_synthetic_decimal_forms_never_round_trip_through_binary_float(
    literal: bytes,
) -> None:
    document = _decoded()
    body = _encode(document).replace(b'"cost":0.024', b'"cost":' + literal, 1)
    ir = _parse(body)
    assert isinstance(ir.cost, Decimal)
    assert ir.cost == Decimal(literal.decode())


def test_synthetic_high_precision_decimal_is_preserved_exactly() -> None:
    document = _decoded()
    _result_obj(document)["metrics"]["organic"]["etv"] = Decimal(
        "1.00000000000000000000000000001"
    )
    ir = _parse(_encode(document))
    organic = _require_result(ir).metrics.organic
    assert organic.etv.value == Decimal("1.00000000000000000000000000001")
    assert organic.etv.value != Decimal(1)


@pytest.mark.parametrize("value", [True, False, "3", Decimal("3.5")])
def test_synthetic_structural_integers_reject_booleans_and_non_integers(
    value: object,
) -> None:
    document = _decoded()
    _first_serp_item(document)["rank_group"] = value
    assert _parse_error(_encode(_one_item_document(_first_item(document)))) == "wrong_type"


def test_synthetic_decimal_fields_reject_booleans() -> None:
    document = _decoded()
    _result_obj(document)["metrics"]["organic"]["etv"] = True
    assert _parse_error(_encode(document)) == "wrong_type"


# --------------------------------------------------------------------------------------
# Synthetic: unknown members at every closed layer
# --------------------------------------------------------------------------------------


def _mutate(path: list[str], mutator: Any) -> bytes:
    document = _decoded()
    node: Any = document
    for step in path:
        node = node[int(step)] if isinstance(node, list) else node[step]
    mutator(node)
    return _encode(document)


@pytest.mark.parametrize(
    "path",
    [
        [],
        ["tasks", "0"],
        ["tasks", "0", "data"],
        ["tasks", "0", "result", "0"],
        ["tasks", "0", "result", "0", "metrics"],
        ["tasks", "0", "result", "0", "metrics", "organic"],
        ["tasks", "0", "result", "0", "metrics_absolute"],
        ["tasks", "0", "result", "0", "metrics_absolute", "organic"],
        ["tasks", "0", "result", "0", "items", "0"],
        ["tasks", "0", "result", "0", "items", "0", "ranked_serp_element"],
        ["tasks", "0", "result", "0", "items", "0", "ranked_serp_element", "serp_item"],
        [
            "tasks",
            "0",
            "result",
            "0",
            "items",
            "0",
            "ranked_serp_element",
            "serp_item",
            "rank_changes",
        ],
        [
            "tasks",
            "0",
            "result",
            "0",
            "items",
            "0",
            "ranked_serp_element",
            "serp_item",
            "rank_info",
        ],
        ["tasks", "0", "result", "0", "items", "0", "keyword_data"],
        ["tasks", "0", "result", "0", "items", "0", "keyword_data", "keyword_info"],
        [
            "tasks",
            "0",
            "result",
            "0",
            "items",
            "0",
            "keyword_data",
            "keyword_info",
            "monthly_searches",
            "0",
        ],
        [
            "tasks",
            "0",
            "result",
            "0",
            "items",
            "0",
            "keyword_data",
            "keyword_info",
            "search_volume_trend",
        ],
        ["tasks", "0", "result", "0", "items", "0", "keyword_data", "keyword_properties"],
        ["tasks", "0", "result", "0", "items", "0", "keyword_data", "avg_backlinks_info"],
        ["tasks", "0", "result", "0", "items", "0", "keyword_data", "search_intent_info"],
        ["tasks", "0", "result", "0", "items", "0", "keyword_data", "serp_info"],
    ],
)
def test_synthetic_unknown_member_fails_closed_at_every_layer(path: list[str]) -> None:
    def add(node: dict[str, Any]) -> None:
        node["observatory_unknown_v2"] = 1

    assert _parse_error(_mutate(path, add)) == "unknown_field"


def test_synthetic_a_sixth_aggregate_family_fails_closed() -> None:
    document = _decoded()
    result = _result_obj(document)
    result["metrics"]["local_services"] = copy.deepcopy(result["metrics"]["paid"])
    assert _parse_error(_encode(document)) == "unknown_field"


def test_synthetic_a_missing_aggregate_family_fails_closed() -> None:
    for holder in ("metrics", "metrics_absolute"):
        for family in REQUESTED_ITEM_TYPES:
            document = _decoded()
            del _result_obj(document)[holder][family]
            assert _parse_error(_encode(document)) == "missing_field"


def test_synthetic_metrics_absolute_never_gains_count_etv_or_cost() -> None:
    for extra in ("count", "etv", "estimated_paid_traffic_cost"):
        document = _decoded()
        _result_obj(document)["metrics_absolute"]["organic"][extra] = 1
        assert _parse_error(_encode(document)) == "unknown_field"


def test_synthetic_missing_metrics_or_metrics_absolute_fails_closed() -> None:
    for holder in ("metrics", "metrics_absolute"):
        document = _decoded()
        del _result_obj(document)[holder]
        assert _parse_error(_encode(document)) == "missing_field"


def test_synthetic_missing_metrics_family_member_fails_closed() -> None:
    document = _decoded()
    del _result_obj(document)["metrics"]["organic"]["pos_41_50"]
    assert _parse_error(_encode(document)) == "missing_field"
    document = _decoded()
    del _result_obj(document)["metrics_absolute"]["organic"]["is_lost"]
    assert _parse_error(_encode(document)) == "missing_field"


# --------------------------------------------------------------------------------------
# Synthetic: open provider string vocabularies stay open
# --------------------------------------------------------------------------------------


def test_synthetic_new_open_provider_string_values_parse() -> None:
    document = _decoded()
    item = _template_item()
    serp = item["ranked_serp_element"]["serp_item"]
    serp["type"] = "ai_overview_reference"
    serp["position"] = "center_rail"
    item["ranked_serp_element"]["serp_item_types"] = [
        "ai_overview",
        "brand_new_feature_2027",
    ]
    item["keyword_data"]["keyword_properties"]["synonym_clustering_algorithm"] = "hybrid_v3"
    item["keyword_data"]["keyword_properties"]["detected_language"] = "sv"
    item["keyword_data"]["keyword_info"]["competition_level"] = "EXTREME"
    item["keyword_data"]["search_intent_info"]["main_intent"] = "speculative"
    document = _one_item_document(item)
    ir = _parse(_encode(document))
    parsed = _only_serp_item(ir)
    assert parsed.type == "ai_overview_reference"
    assert parsed.position.value == "center_rail"
    element = _only_item(ir).ranked_serp_element.value
    assert element is not None
    # `serp_item.type` and SERP composition remain different fields: no cross-inference.
    assert element.serp_item_types.value == ("ai_overview", "brand_new_feature_2027")
    data = _only_keyword_data(ir)
    assert data.keyword_properties.value is not None
    assert data.keyword_properties.value.synonym_clustering_algorithm.value == "hybrid_v3"
    assert data.keyword_properties.value.detected_language.value == "sv"
    assert data.keyword_info.value is not None
    assert data.keyword_info.value.competition_level.value == "EXTREME"
    assert data.search_intent_info.value is not None
    assert data.search_intent_info.value.main_intent.value == "speculative"


def test_synthetic_se_type_stays_closed_to_google() -> None:
    document = _decoded()
    _first_serp_item(document)["se_type"] = "bing"
    assert _parse_error(_encode(document)) == "unknown_enum"


# --------------------------------------------------------------------------------------
# Synthetic: verified Attempt contract
# --------------------------------------------------------------------------------------


def test_synthetic_attempt_key_set_is_closed_and_complete() -> None:
    extra = dict(PARAMETERS)
    extra["tag"] = "observatory"
    assert _parse_error(_fixture(), extra) == "unknown_field"
    for key in PARAMETERS:
        missing = dict(PARAMETERS)
        del missing[key]
        assert _parse_error(_fixture(), missing) == "missing_field"


@pytest.mark.parametrize(
    ("key", "value", "code"),
    [
        ("contract", "dataforseo-labs-google-related-keywords-live-v1", "unknown_enum"),
        ("location_code", 2826, "frozen_parameter"),
        ("language_code", "de", "frozen_parameter"),
        ("limit", 1000, "frozen_parameter"),
        ("offset", 100, "frozen_parameter"),
        ("historical_serp_mode", "live", "frozen_parameter"),
        ("ignore_synonyms", True, "frozen_parameter"),
        ("include_clickstream_data", True, "frozen_parameter"),
        ("load_rank_absolute", False, "frozen_parameter"),
        ("order_by", ["ranked_serp_element.serp_item.rank_absolute,asc"], "frozen_parameter"),
        ("order_by", [ORDER_BY, ORDER_BY], "frozen_parameter"),
        ("item_types", ["organic"], "frozen_parameter"),
        (
            "item_types",
            ["paid", "organic", "featured_snippet", "local_pack", "ai_overview_reference"],
            "frozen_parameter",
        ),
        ("limit", True, "wrong_type"),
        ("ignore_synonyms", "false", "wrong_type"),
    ],
)
def test_synthetic_frozen_attempt_values_are_enforced(
    key: str, value: object, code: str
) -> None:
    parameters = dict(PARAMETERS)
    parameters[key] = value
    assert _parse_error(_fixture(), parameters) == code


@pytest.mark.parametrize(
    "target",
    [
        "www.theconspiratory.com",
        "theconspiratory.com\n",
        "\ntheconspiratory.com",
        "theconspiratory.com ",
        "TheConspiratory.com",
        "theconspiratory",
        "a.b.theconspiratory.com",
        "xn--80ak6aa92e.com",
        "theconspiratory.xn--p1ai",
        "https://theconspiratory.com",
        "theconspiratory.com/theory",
        "theconspiratory.4com",
        "-theconspiratory.com",
        "theconspiratory-.com",
        "",
    ],
)
def test_synthetic_attempt_target_grammar_matches_rank02(target: str) -> None:
    parameters = dict(PARAMETERS)
    parameters["target"] = target
    assert _parse_error(_fixture(), parameters) == "invalid_value"


def test_synthetic_www_first_label_rule_is_reachable_and_load_bearing() -> None:
    """`www.theconspiratory.com` is already refused by the two-label shape.

    A two-label `www.com` is the input that actually reaches the RANK-02 `www` first-label
    rule, so this pins the rule itself rather than the arity check that shadows it.
    """

    parameters = dict(PARAMETERS)
    parameters["target"] = "www.com"
    assert _parse_error(_fixture(), parameters) == "invalid_value"
    # Same shape, non-www first label: accepted, proving the refusal is the www rule.
    parameters["target"] = "wwx.com"
    assert _parse(_fixture(), parameters).request.target == "wwx.com"


def test_synthetic_punycode_rule_is_reachable_in_both_labels() -> None:
    for target, sibling in (
        ("xn--80ak6aa92e.com", "xy--80ak6aa92e.com"),
        ("theconspiratory.xn--p1ai", "theconspiratory.xy--p1ai"),
    ):
        parameters = dict(PARAMETERS)
        parameters["target"] = target
        assert _parse_error(_fixture(), parameters) == "invalid_value"
        parameters["target"] = sibling
        assert _parse(_fixture(), parameters).request.target == sibling


TARGET_GRAMMAR_CORPUS = (
    "theconspiratory.com",
    "example.com",
    "a1.co",
    "my-site.io",
    "wwx.com",
    "x.io",
    "0-0.dev",
    ("a" * 63) + ".com",
    ("a" * 64) + ".com",
    "example." + ("b" * 63),
    "example." + ("b" * 64),
    "www.com",
    "www.theconspiratory.com",
    "xn--80ak6aa92e.com",
    "theconspiratory.xn--p1ai",
    "xy--80ak6aa92e.com",
    "TheConspiratory.com",
    "theconspiratory",
    "a.b.theconspiratory.com",
    "theconspiratory.com\n",
    "\ntheconspiratory.com",
    "theconspiratory.com ",
    " theconspiratory.com",
    "theconspiratory.com.",
    ".theconspiratory.com",
    "theconspiratory..com",
    "theconspiratory.4com",
    "-theconspiratory.com",
    "theconspiratory-.com",
    "theconspiratory.c",
    "theconspiratory.co-",
    "https://theconspiratory.com",
    "theconspiratory.com/theory",
    "the_conspiratory.com",
    "",
)


def test_synthetic_local_target_grammar_agrees_with_the_rank02_adapter() -> None:
    """Differential proof, not parser logic.

    The parser deliberately duplicates the RANK-02 target grammar so its failures stay
    parser-local and deterministic. Duplication only stays honest if the two agree, so
    this test — and nothing in the parser — calls the adapter validator, over a corpus
    that reaches the arity, case, label-shape, length, `www`, and punycode branches.
    """

    disagreements: list[tuple[str, bool, bool]] = []
    for target in TARGET_GRAMMAR_CORPUS:
        adapter_document = dict(PARAMETERS)
        adapter_document["target"] = target
        try:
            validate_ranked_keywords_http_parameters(adapter_document)
            adapter_accepts = True
        except DocumentError:
            adapter_accepts = False
        parameters = dict(PARAMETERS)
        parameters["target"] = target
        try:
            parsed = _parse(_fixture(), parameters)
            parser_accepts = parsed.request.target == target
        except RankedKeywordsParseError:
            parser_accepts = False
        if adapter_accepts != parser_accepts:
            disagreements.append((target, adapter_accepts, parser_accepts))
    assert disagreements == []
    # The corpus must actually exercise both verdicts, or agreement is vacuous.
    accepted = [
        target
        for target in TARGET_GRAMMAR_CORPUS
        if _accepts_target(target)
    ]
    assert len(accepted) >= 8
    assert len(accepted) < len(TARGET_GRAMMAR_CORPUS)


def _accepts_target(target: str) -> bool:
    parameters = dict(PARAMETERS)
    parameters["target"] = target
    try:
        return _parse(_fixture(), parameters).request.target == target
    except RankedKeywordsParseError:
        return False


def test_synthetic_attempt_target_must_be_a_string() -> None:
    parameters = dict(PARAMETERS)
    parameters["target"] = 42
    assert _parse_error(_fixture(), parameters) == "wrong_type"


def test_synthetic_label_length_bound_matches_rank02() -> None:
    """63 characters is the longest accepted label; 64 is refused.

    As in RANK-02 the explicit 1..63 length check is defensive: the grammar itself already
    caps a label at 63 characters. Both bounds are duplicated so the two stay aligned.
    """

    parameters = dict(PARAMETERS)
    parameters["target"] = ("a" * 63) + ".com"
    assert _parse(_fixture(), parameters).request.target == ("a" * 63) + ".com"
    parameters["target"] = ("a" * 64) + ".com"
    assert _parse_error(_fixture(), parameters) == "invalid_value"
    parameters["target"] = "example." + ("b" * 63)
    assert _parse(_fixture(), parameters).request.target == "example." + ("b" * 63)
    parameters["target"] = "example." + ("b" * 64)
    assert _parse_error(_fixture(), parameters) == "invalid_value"


def test_synthetic_other_adapter_valid_targets_are_accepted() -> None:
    document = _decoded()
    for target in ("example.com", "a1.co", "my-site.io"):
        parameters = dict(PARAMETERS)
        parameters["target"] = target
        ir = _parse(_encode(document), parameters)
        assert ir.request.target == target
        # Provider echo/result target testimony is not overwritten by the Attempt.
        assert ir.echo.target.value == TARGET
        assert _require_result(ir).target.value == TARGET


def test_synthetic_returned_www_domain_is_valid_provider_testimony() -> None:
    """The Attempt grammar rejects a www target; provider `domain` is a different contract."""

    parameters = dict(PARAMETERS)
    parameters["target"] = WWW
    assert _parse_error(_fixture(), parameters) == "invalid_value"
    item = _template_item()
    item["ranked_serp_element"]["serp_item"]["domain"] = WWW
    item["ranked_serp_element"]["serp_item"]["url"] = f"https://{WWW}/theory/atlantis"
    ir = _parse(_encode(_one_item_document(item)))
    serp = _only_serp_item(ir)
    assert serp.domain.value == WWW
    assert serp.url == f"https://{WWW}/theory/atlantis"


def test_synthetic_attempt_target_grammar_is_never_applied_to_provider_domain() -> None:
    item = _template_item()
    serp = item["ranked_serp_element"]["serp_item"]
    # An uppercase, multi-label, punycode domain the Attempt grammar would refuse.
    serp["domain"] = "News.XN--P1AI.Example.COM"
    serp["main_domain"] = "example.co.uk"
    serp["website_name"] = "Totally Different Brand"
    serp["url"] = "https://elsewhere.example.org/a"
    ir = _parse(_encode(_one_item_document(item)))
    parsed = _only_serp_item(ir)
    assert parsed.domain.value == "News.XN--P1AI.Example.COM"
    assert parsed.main_domain.value == "example.co.uk"
    assert parsed.website_name.value == "Totally Different Brand"
    # URL host need not match domain, main_domain, or the Attempt target.
    assert parsed.url == "https://elsewhere.example.org/a"


# --------------------------------------------------------------------------------------
# Synthetic: envelope, status, and result topology
# --------------------------------------------------------------------------------------


def test_synthetic_tasks_count_must_match_the_task_array() -> None:
    document = _decoded()
    document["tasks_count"] = 2
    assert _parse_error(_encode(document)) == "count_mismatch"


def test_synthetic_two_tasks_cannot_be_rescued_by_tasks_error_two() -> None:
    document = _decoded()
    second = copy.deepcopy(_task(document))
    second["status_code"] = 40501
    second["status_message"] = "Invalid Field."
    document["tasks"] = [_task(document), second]
    document["tasks_count"] = 2
    document["tasks_error"] = 2
    assert _parse_error(_encode(document)) == "tasks_length"


def test_synthetic_zero_tasks_fails() -> None:
    document = _decoded()
    document["tasks"] = []
    document["tasks_count"] = 0
    document["tasks_error"] = 0
    assert _parse_error(_encode(document)) == "tasks_length"


def test_synthetic_root_and_task_status_disagreement_fails() -> None:
    document = _decoded()
    document["status_code"] = 40000
    assert _parse_error(_encode(document)) == "inconsistent_status"
    document = _decoded()
    _task(document)["status_code"] = 40501
    assert _parse_error(_encode(document)) == "inconsistent_status"


def test_synthetic_tasks_error_must_reconcile_with_the_single_task_status() -> None:
    document = _decoded()
    document["tasks_error"] = 1
    assert _parse_error(_encode(document)) == "count_mismatch"


def test_synthetic_provider_error_branch_returns_parser_local_provider_error() -> None:
    document = _decoded()
    document["status_code"] = 40501
    document["status_message"] = "Invalid Field."
    document["tasks_error"] = 1
    task = _task(document)
    task["status_code"] = 40501
    task["status_message"] = "Invalid Field."
    task["result"] = None
    task["result_count"] = 0
    ir = _parse(_encode(document))
    assert ir.outcome is ParseClassification.PROVIDER_ERROR
    assert ir.result is None
    # Attempt, echo, envelope, task, and result_count testimony are still typed.
    assert ir.request.target == TARGET
    assert ir.echo.function.value == "ranked_keywords"
    assert ir.status_code == 40501
    assert ir.task_status_message == "Invalid Field."
    assert ir.result_count == 0
    assert ir.task_path == ("v3", "dataforseo_labs", "google", "ranked_keywords", "live")


def test_synthetic_provider_error_branch_does_not_inspect_ranked_result() -> None:
    """A structurally impossible result is never parsed on the provider-error branch."""

    document = _decoded()
    document["status_code"] = 40501
    document["tasks_error"] = 1
    task = _task(document)
    task["status_code"] = 40501
    task["result"] = ["this is not a Ranked result object"]
    task["result_count"] = 1
    ir = _parse(_encode(document))
    assert ir.outcome is ParseClassification.PROVIDER_ERROR
    assert ir.result is None


def test_synthetic_provider_error_still_requires_well_typed_counts_and_echo() -> None:
    document = _decoded()
    document["status_code"] = 40501
    document["tasks_error"] = 1
    task = _task(document)
    task["status_code"] = 40501
    task["result_count"] = -1
    assert _parse_error(_encode(document)) == "invalid_number"

    document = _decoded()
    document["status_code"] = 40501
    document["tasks_error"] = 1
    task = _task(document)
    task["status_code"] = 40501
    task["result_count"] = True
    assert _parse_error(_encode(document)) == "wrong_type"

    document = _decoded()
    document["status_code"] = 40501
    document["tasks_error"] = 1
    task = _task(document)
    task["status_code"] = 40501
    task["data"] = {"unexpected_echo_member": 1}
    assert _parse_error(_encode(document)) == "unknown_field"


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        (None, "wrong_type"),
        ([], "count_mismatch"),
        ([{}, {}], "count_mismatch"),
        ("not-an-array", "wrong_type"),
    ],
)
def test_synthetic_successful_result_topology(mutation: object, code: str) -> None:
    document = _decoded()
    _task(document)["result"] = mutation
    assert _parse_error(_encode(document)) == code


def test_synthetic_successful_result_absent_fails() -> None:
    document = _decoded()
    del _task(document)["result"]
    assert _parse_error(_encode(document)) == "missing_field"


def test_synthetic_two_results_fail_even_with_matching_result_count() -> None:
    document = _decoded()
    task = _task(document)
    task["result"] = [_result_obj(document), copy.deepcopy(_result_obj(document))]
    task["result_count"] = 2
    assert _parse_error(_encode(document)) == "result_length"


def test_synthetic_result_count_must_match_the_result_array() -> None:
    document = _decoded()
    _task(document)["result_count"] = 2
    assert _parse_error(_encode(document)) == "count_mismatch"


def test_synthetic_successful_null_items_fails_closed_in_v1() -> None:
    document = _decoded()
    result = _result_obj(document)
    result["items"] = None
    result["items_count"] = 0
    assert _parse_error(_encode(document)) == "wrong_type"


def test_synthetic_successful_absent_items_fails_closed_in_v1() -> None:
    document = _decoded()
    result = _result_obj(document)
    del result["items"]
    result["items_count"] = 0
    assert _parse_error(_encode(document)) == "missing_field"


def test_synthetic_items_count_mismatch_fails() -> None:
    document = _decoded()
    _result_obj(document)["items_count"] = 99
    assert _parse_error(_encode(document)) == "count_mismatch"


def test_synthetic_successful_empty_items_is_empty_parser_ir_only() -> None:
    document = _decoded()
    result = _result_obj(document)
    result["items"] = []
    result["items_count"] = 0
    ir = _parse(_encode(document))
    # No admitted-empty Observation semantics is created here.
    assert ir.outcome is ParseClassification.ADMITTED
    parsed = _require_result(ir)
    assert parsed.items == ()
    assert parsed.items_count == 0
    assert parsed.total_count == 248


@pytest.mark.parametrize("total", [0, 1, 99, 100, 101, 248, 100000])
def test_synthetic_total_count_is_independent_of_items_count(total: int) -> None:
    """RANK-04 deliberately imposes no `total_count >= items_count` equation."""

    document = _decoded()
    _result_obj(document)["total_count"] = total
    ir = _parse(_encode(document))
    assert _require_result(ir).total_count == total
    assert _require_result(ir).items_count == 100


def test_synthetic_negative_or_boolean_counts_fail() -> None:
    document = _decoded()
    _result_obj(document)["total_count"] = -1
    assert _parse_error(_encode(document)) == "invalid_number"
    document = _decoded()
    _result_obj(document)["total_count"] = True
    assert _parse_error(_encode(document)) == "wrong_type"


# --------------------------------------------------------------------------------------
# Synthetic: aggregates without arithmetic reconciliation
# --------------------------------------------------------------------------------------


def test_synthetic_arbitrary_aggregate_arithmetic_disagreement_parses() -> None:
    document = _decoded()
    result = _result_obj(document)
    organic = result["metrics"]["organic"]
    organic["pos_1"] = 7
    organic["count"] = 3
    organic["is_new"] = 999
    result["metrics_absolute"]["organic"]["pos_1"] = 4242
    result["total_count"] = 5
    ir = _parse(_encode(document))
    parsed = _require_result(ir)
    # No bucket-sum, count, movement, or total_count equation exists in parser logic.
    assert parsed.metrics.organic.positions.pos_1 == 7
    assert parsed.metrics.organic.count == 3
    assert parsed.metrics.organic.is_new == 999
    assert parsed.metrics_absolute.organic.positions.pos_1 == 4242
    assert parsed.total_count == 5


def test_synthetic_aggregate_zero_and_null_remain_distinct() -> None:
    document = _decoded()
    organic = _result_obj(document)["metrics"]["organic"]
    organic["etv"] = 0
    organic["estimated_paid_traffic_cost"] = None
    parsed = _require_result(_parse(_encode(document))).metrics.organic
    assert parsed.etv.state is FieldState.STATED
    assert parsed.etv.value == Decimal(0)
    assert parsed.estimated_paid_traffic_cost.state is FieldState.JSON_NULL
    assert parsed.estimated_paid_traffic_cost.value is None


def test_synthetic_negative_aggregate_bucket_fails() -> None:
    document = _decoded()
    _result_obj(document)["metrics"]["organic"]["pos_1"] = -1
    assert _parse_error(_encode(document)) == "invalid_number"


def test_synthetic_populated_aggregate_clickstream_locus_fails() -> None:
    for holder in ("metrics", "metrics_absolute"):
        for field in CLICKSTREAM_AGGREGATE_FIELDS:
            document = _decoded()
            _result_obj(document)[holder]["organic"][field] = (
                {"male": 10, "female": 90} if "distribution" in field else 1
            )
            assert _parse_error(_encode(document)) == "request_disabled_populated"


# --------------------------------------------------------------------------------------
# Synthetic: occurrence preservation, rank typing, and ordering
# --------------------------------------------------------------------------------------


def test_synthetic_shuffled_item_order_is_preserved_and_reindexed() -> None:
    document = _decoded()
    items = _items(document)
    reversed_items = list(reversed(copy.deepcopy(items)))
    _result_obj(document)["items"] = reversed_items
    ir = _parse(_encode(document))
    parsed = _require_result(ir)
    assert tuple(item.provider_array_index for item in parsed.items) == tuple(range(100))
    groups = tuple(serp.rank_group for serp in _serp_items(ir))
    # Never resorted: reversed provider order yields nonincreasing rank_group here.
    assert all(groups[i] >= groups[i + 1] for i in range(99))
    original = tuple(serp.rank_group for serp in _serp_items(_parse()))
    assert groups == tuple(reversed(original))


def test_synthetic_duplicate_keywords_and_urls_stay_separate_occurrences() -> None:
    document = _decoded()
    first = copy.deepcopy(_first_item(document))
    second = copy.deepcopy(first)
    third = copy.deepcopy(first)
    third["ranked_serp_element"]["serp_item"]["rank_group"] = 90
    result = _result_obj(document)
    result["items"] = [first, second, third]
    result["items_count"] = 3
    ir = _parse(_encode(document))
    parsed = _require_result(ir)
    assert len(parsed.items) == 3
    assert tuple(item.provider_array_index for item in parsed.items) == (0, 1, 2)
    keywords = [data.keyword for data in _keyword_datas(ir)]
    urls = [serp.url for serp in _serp_items(ir)]
    assert len(set(keywords)) == 1
    assert len(set(urls)) == 1
    assert len(keywords) == len(urls) == 3
    ranks = [serp.rank_group for serp in _serp_items(ir)]
    assert ranks == [14, 14, 90]


@pytest.mark.parametrize(
    ("rank_group", "rank_absolute"),
    [(0, 0), (1, 1), (57, 18), (100, 100), (0, 999)],
)
def test_synthetic_rank_values_may_equal_or_reverse_without_a_correlation_rule(
    rank_group: int, rank_absolute: int
) -> None:
    item = _template_item()
    item["ranked_serp_element"]["serp_item"]["rank_group"] = rank_group
    item["ranked_serp_element"]["serp_item"]["rank_absolute"] = rank_absolute
    serp = _only_serp_item(_parse(_encode(_one_item_document(item))))
    assert serp.rank_group == rank_group
    assert serp.rank_absolute == rank_absolute


@pytest.mark.parametrize("field", ["rank_group", "rank_absolute"])
def test_synthetic_negative_rank_fails(field: str) -> None:
    item = _template_item()
    item["ranked_serp_element"]["serp_item"][field] = -1
    assert _parse_error(_encode(_one_item_document(item))) == "invalid_number"


def test_synthetic_rank_info_and_previous_rank_zero_are_valid() -> None:
    item = _template_item()
    serp = item["ranked_serp_element"]["serp_item"]
    serp["rank_info"] = {"page_rank": 0, "main_domain_rank": 0}
    serp["rank_changes"] = {
        "is_new": False,
        "is_up": True,
        "is_down": True,
        "previous_rank_absolute": 0,
    }
    parsed = _only_serp_item(_parse(_encode(_one_item_document(item))))
    assert parsed.rank_info.value is not None
    assert parsed.rank_info.value.page_rank.value == 0
    assert parsed.rank_info.value.main_domain_rank.value == 0
    changes = parsed.rank_changes.value
    assert changes is not None
    # A contradictory is_up/is_down combination the fixture never shows stays parseable.
    assert changes.is_new.value is False
    assert changes.is_up.value is True
    assert changes.is_down.value is True
    assert changes.previous_rank_absolute.value == 0


def test_synthetic_negative_rank_info_or_previous_rank_fails() -> None:
    item = _template_item()
    item["ranked_serp_element"]["serp_item"]["rank_info"]["page_rank"] = -1
    assert _parse_error(_encode(_one_item_document(item))) == "invalid_number"
    item = _template_item()
    item["ranked_serp_element"]["serp_item"]["rank_changes"][
        "previous_rank_absolute"
    ] = -5
    assert _parse_error(_encode(_one_item_document(item))) == "invalid_number"


def test_synthetic_lost_row_with_previous_rank_and_clock_remains_representable() -> None:
    item = _template_item()
    element = item["ranked_serp_element"]
    element["is_lost"] = True
    element["previous_updated_time"] = None
    element["serp_item"]["rank_changes"] = {
        "is_new": False,
        "is_up": False,
        "is_down": True,
        "previous_rank_absolute": 12,
    }
    ir = _parse(_encode(_one_item_document(item)))
    parsed_element = _only_item(ir).ranked_serp_element.value
    assert parsed_element is not None
    assert parsed_element.is_lost.value is True
    # Previous clock and previous rank are independent: null clock, stated rank.
    assert parsed_element.previous_updated_time.state is FieldState.JSON_NULL
    changes = parsed_element.serp_item.rank_changes.value
    assert changes is not None
    assert changes.previous_rank_absolute.value == 12


# --------------------------------------------------------------------------------------
# Synthetic: URL, host, and SERP composition preservation
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "url",
    [
        "https://theconspiratory.com/theory/atlantis?utm_source=x&b=1",
        "https://theconspiratory.com/theory/atlantis#section-2",
        "https://theconspiratory.com/theory/atlantis/",
        "http://theconspiratory.com/Theory/Atlantis",
        "HTTPS://WWW.THECONSPIRATORY.COM/A",
        "https://theconspiratory.com:8443/a",
        "https://user:pw@theconspiratory.com/a",
        "https://theconspiratory.com/a%20b",
        "https://xn--80ak6aa92e.com/a",
    ],
)
def test_synthetic_exact_url_text_survives_without_canonicalization(url: str) -> None:
    item = _template_item()
    item["ranked_serp_element"]["serp_item"]["url"] = url
    assert _only_serp_item(_parse(_encode(_one_item_document(item)))).url == url


@pytest.mark.parametrize(
    "url",
    [
        "ftp://theconspiratory.com/a",
        "theconspiratory.com/a",
        "/theory/atlantis",
        "https:///a",
        "https://theconspiratory.com/a b",
        "https://the conspiratory.com/a",
        "",
    ],
)
def test_synthetic_invalid_serp_url_fails(url: str) -> None:
    item = _template_item()
    item["ranked_serp_element"]["serp_item"]["url"] = url
    assert _parse_error(_encode(_one_item_document(item))) == "invalid_url"


@pytest.mark.parametrize("field", ["type", "rank_group", "rank_absolute"])
def test_synthetic_missing_serp_item_spine_member_fails(field: str) -> None:
    item = _template_item()
    del item["ranked_serp_element"]["serp_item"][field]
    assert _parse_error(_encode(_one_item_document(item))) == "missing_field"


def test_synthetic_serp_url_must_be_present_and_a_string() -> None:
    item = _template_item()
    del item["ranked_serp_element"]["serp_item"]["url"]
    assert _parse_error(_encode(_one_item_document(item))) == "missing_field"
    item = _template_item()
    item["ranked_serp_element"]["serp_item"]["url"] = None
    assert _parse_error(_encode(_one_item_document(item))) == "wrong_type"


def test_synthetic_breadcrumb_and_other_text_are_never_url_validated() -> None:
    item = _template_item()
    serp = item["ranked_serp_element"]["serp_item"]
    serp["breadcrumb"] = "theconspiratory.com › Case files › Deep dives"
    serp["relative_url"] = "not a url at all"
    serp["website_name"] = "ftp://nonsense value"
    serp["xpath"] = "/html[1]/body[1]/div[3]"
    parsed = _only_serp_item(_parse(_encode(_one_item_document(item))))
    assert parsed.breadcrumb.value == "theconspiratory.com › Case files › Deep dives"
    assert parsed.relative_url.value == "not a url at all"
    assert parsed.website_name.value == "ftp://nonsense value"
    assert parsed.xpath.value == "/html[1]/body[1]/div[3]"


def test_synthetic_apex_and_www_urls_are_two_occurrences_not_one() -> None:
    document = _decoded()
    apex = copy.deepcopy(_first_item(document))
    apex["ranked_serp_element"]["serp_item"]["url"] = f"https://{APEX}/theory/atlantis"
    apex["ranked_serp_element"]["serp_item"]["domain"] = APEX
    www = copy.deepcopy(apex)
    www["ranked_serp_element"]["serp_item"]["url"] = f"https://{WWW}/theory/atlantis"
    www["ranked_serp_element"]["serp_item"]["domain"] = WWW
    result = _result_obj(document)
    result["items"] = [apex, www]
    result["items_count"] = 2
    ir = _parse(_encode(document))
    serps = _serp_items(ir)
    assert len(serps) == 2
    assert serps[0].url != serps[1].url
    assert serps[0].domain.value != serps[1].domain.value
    assert serps[0].relative_url.value == serps[1].relative_url.value


@pytest.mark.parametrize(
    "types",
    [
        [],
        ["organic"],
        ["organic", "organic", "ai_overview"],
        ["ai_overview", "organic"],
        ["organic", "ai_overview"],
        ["totally_new_serp_feature"],
    ],
)
def test_synthetic_serp_item_types_preserve_order_multiplicity_and_novelty(
    types: list[str],
) -> None:
    item = _template_item()
    item["ranked_serp_element"]["serp_item_types"] = list(types)
    element = _only_item(_parse(_encode(_one_item_document(item)))).ranked_serp_element
    assert element.value is not None
    assert element.value.serp_item_types.value == tuple(types)


def test_synthetic_serp_item_types_null_and_absent_stay_distinct() -> None:
    item = _template_item()
    item["ranked_serp_element"]["serp_item_types"] = None
    element = _only_item(_parse(_encode(_one_item_document(item)))).ranked_serp_element
    assert element.value is not None
    assert element.value.serp_item_types.state is FieldState.JSON_NULL
    item = _template_item()
    del item["ranked_serp_element"]["serp_item_types"]
    element = _only_item(_parse(_encode(_one_item_document(item)))).ranked_serp_element
    assert element.value is not None
    assert element.value.serp_item_types.state is FieldState.ABSENT


def test_synthetic_serp_composition_never_implies_target_participation() -> None:
    item = _template_item()
    item["ranked_serp_element"]["serp_item_types"] = ["ai_overview", "featured_snippet"]
    item["ranked_serp_element"]["serp_item"]["is_featured_snippet"] = False
    document = _one_item_document(item)
    for family in ("ai_overview_reference", "featured_snippet"):
        _result_obj(document)["metrics"][family]["count"] = 0
    ir = _parse(_encode(document))
    element = _only_item(ir).ranked_serp_element.value
    assert element is not None
    assert element.serp_item_types.value == ("ai_overview", "featured_snippet")
    assert element.serp_item.is_featured_snippet.value is False
    assert _require_result(ir).metrics.ai_overview_reference.count == 0
    assert _require_result(ir).metrics.featured_snippet.count == 0


def test_synthetic_duplicated_provider_paths_may_disagree_and_both_survive() -> None:
    item = _template_item()
    element = item["ranked_serp_element"]
    serp_info = item["keyword_data"]["serp_info"]
    element["check_url"] = "https://www.google.com/search?q=element"
    serp_info["check_url"] = "https://www.google.com/search?q=serpinfo"
    element["se_results_count"] = 11
    serp_info["se_results_count"] = 22
    element["last_updated_time"] = "2026-01-02 03:04:05 +00:00"
    serp_info["last_updated_time"] = "2025-12-31 23:59:59 +00:00"
    element["previous_updated_time"] = "2025-01-02 03:04:05 +00:00"
    serp_info["previous_updated_time"] = None
    element["serp_item_types"] = ["organic"]
    serp_info["serp_item_types"] = ["organic", "ai_overview"]
    element["keyword_difficulty"] = 5
    item["keyword_data"]["keyword_properties"]["keyword_difficulty"] = 95
    ir = _parse(_encode(_one_item_document(item)))
    parsed_item = _only_item(ir)
    parsed_element = parsed_item.ranked_serp_element.value
    parsed_data = parsed_item.keyword_data.value
    assert parsed_element is not None
    assert parsed_data is not None
    parsed_serp_info = parsed_data.serp_info.value
    parsed_props = parsed_data.keyword_properties.value
    assert parsed_serp_info is not None
    assert parsed_props is not None
    assert parsed_element.check_url.value == "https://www.google.com/search?q=element"
    assert parsed_serp_info.check_url.value == "https://www.google.com/search?q=serpinfo"
    assert parsed_element.se_results_count.value == 11
    assert parsed_serp_info.se_results_count.value == 22
    assert parsed_element.last_updated_time.value == "2026-01-02 03:04:05 +00:00"
    assert parsed_serp_info.last_updated_time.value == "2025-12-31 23:59:59 +00:00"
    assert parsed_element.previous_updated_time.value == "2025-01-02 03:04:05 +00:00"
    assert parsed_serp_info.previous_updated_time.state is FieldState.JSON_NULL
    assert parsed_element.serp_item_types.value == ("organic",)
    assert parsed_serp_info.serp_item_types.value == ("organic", "ai_overview")
    assert parsed_element.keyword_difficulty.value == 5
    assert parsed_props.keyword_difficulty.value == 95


@pytest.mark.parametrize("name", list(UNSUPPORTED_SERP_CHILDREN))
def test_synthetic_populated_null_only_serp_child_fails(name: str) -> None:
    item = _template_item()
    item["ranked_serp_element"]["serp_item"][name] = {"anything": 1}
    assert _parse_error(_encode(_one_item_document(item))) == "unsupported_shape"


@pytest.mark.parametrize("name", list(UNSUPPORTED_SERP_CHILDREN))
def test_synthetic_absent_null_only_serp_child_is_absent_not_null(name: str) -> None:
    item = _template_item()
    del item["ranked_serp_element"]["serp_item"][name]
    serp = _only_serp_item(_parse(_encode(_one_item_document(item))))
    assert getattr(serp, name).state is FieldState.ABSENT
    item = _template_item()
    item["ranked_serp_element"]["serp_item"][name] = None
    serp = _only_serp_item(_parse(_encode(_one_item_document(item))))
    assert getattr(serp, name).state is FieldState.JSON_NULL


# --------------------------------------------------------------------------------------
# Synthetic: keyword enrichment, monthly Data Periods, clocks, and clickstream
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rows",
    [
        [],
        [{"year": 2026, "month": 7, "search_volume": 10}],
        [
            {"year": 2020, "month": 1, "search_volume": 0},
            {"year": 2021, "month": 2, "search_volume": 5},
            {"year": 2019, "month": 12, "search_volume": 7},
        ],
    ],
)
def test_synthetic_monthly_series_needs_no_length_window_or_order(
    rows: list[dict[str, int]],
) -> None:
    item = _template_item()
    item["keyword_data"]["keyword_info"]["monthly_searches"] = copy.deepcopy(rows)
    data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.keyword_info.value is not None
    series = data.keyword_info.value.monthly_searches.value
    assert series is not None
    assert len(series) == len(rows)
    assert [(point.year, point.month) for point in series] == [
        (row["year"], row["month"]) for row in rows
    ]
    assert [point.provider_array_index for point in series] == list(range(len(rows)))


def test_synthetic_long_monthly_series_parses() -> None:
    rows = [
        {"year": 2020 + index // 12, "month": (index % 12) + 1, "search_volume": index}
        for index in range(48)
    ]
    item = _template_item()
    item["keyword_data"]["keyword_info"]["monthly_searches"] = rows
    data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.keyword_info.value is not None
    series = data.keyword_info.value.monthly_searches.value
    assert series is not None
    assert len(series) == 48


def test_synthetic_duplicate_monthly_period_fails() -> None:
    item = _template_item()
    item["keyword_data"]["keyword_info"]["monthly_searches"] = [
        {"year": 2026, "month": 7, "search_volume": 10},
        {"year": 2026, "month": 7, "search_volume": 11},
    ]
    assert _parse_error(_encode(_one_item_document(item))) == "duplicate_period"


@pytest.mark.parametrize(
    ("year", "month"),
    [(2026, 0), (2026, 13), (2026, -1), (0, 7), (10000, 7)],
)
def test_synthetic_invalid_monthly_period_fails(year: int, month: int) -> None:
    item = _template_item()
    item["keyword_data"]["keyword_info"]["monthly_searches"] = [
        {"year": year, "month": month, "search_volume": 10}
    ]
    assert _parse_error(_encode(_one_item_document(item))) == "invalid_period"


def test_synthetic_negative_search_volume_fails() -> None:
    item = _template_item()
    item["keyword_data"]["keyword_info"]["monthly_searches"] = [
        {"year": 2026, "month": 7, "search_volume": -1}
    ]
    assert _parse_error(_encode(_one_item_document(item))) == "invalid_number"
    item = _template_item()
    item["keyword_data"]["keyword_info"]["search_volume"] = -1
    assert _parse_error(_encode(_one_item_document(item))) == "invalid_number"


def test_synthetic_monthly_and_current_zero_remain_zero_testimony() -> None:
    item = _template_item()
    info = item["keyword_data"]["keyword_info"]
    info["search_volume"] = 0
    info["monthly_searches"] = [{"year": 2026, "month": 7, "search_volume": 0}]
    data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.keyword_info.value is not None
    assert data.keyword_info.value.search_volume.state is FieldState.STATED
    assert data.keyword_info.value.search_volume.value == 0
    series = data.keyword_info.value.monthly_searches.value
    assert series is not None
    assert series[0].search_volume == 0


def test_synthetic_current_volume_is_never_checked_against_monthly_rows() -> None:
    item = _template_item()
    info = item["keyword_data"]["keyword_info"]
    info["search_volume"] = 1_000_000
    info["monthly_searches"] = [{"year": 2026, "month": 7, "search_volume": 1}]
    data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.keyword_info.value is not None
    assert data.keyword_info.value.search_volume.value == 1_000_000
    series = data.keyword_info.value.monthly_searches.value
    assert series is not None
    assert series[0].search_volume == 1


def test_synthetic_monthly_states_absent_null_and_stated_are_distinct() -> None:
    item = _template_item()
    del item["keyword_data"]["keyword_info"]["monthly_searches"]
    data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.keyword_info.value is not None
    assert data.keyword_info.value.monthly_searches.state is FieldState.ABSENT
    item = _template_item()
    item["keyword_data"]["keyword_info"]["monthly_searches"] = None
    data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.keyword_info.value is not None
    assert data.keyword_info.value.monthly_searches.state is FieldState.JSON_NULL


def test_synthetic_signed_search_volume_trend_parses() -> None:
    item = _template_item()
    item["keyword_data"]["keyword_info"]["search_volume_trend"] = {
        "monthly": -50,
        "quarterly": 0,
        "yearly": None,
    }
    data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.keyword_info.value is not None
    trend = data.keyword_info.value.search_volume_trend.value
    assert trend is not None
    assert trend.monthly.value == -50
    assert trend.quarterly.value == 0
    assert trend.yearly.state is FieldState.JSON_NULL


@pytest.mark.parametrize(
    ("categories", "expected_state", "expected_value"),
    [
        (None, FieldState.JSON_NULL, None),
        ([], FieldState.STATED, ()),
        ([13600, 13600, 10007], FieldState.STATED, (13600, 13600, 10007)),
        ([10007, 13600, 13600], FieldState.STATED, (10007, 13600, 13600)),
    ],
)
def test_synthetic_categories_states_order_and_duplicates(
    categories: object, expected_state: FieldState, expected_value: object
) -> None:
    item = _template_item()
    item["keyword_data"]["keyword_info"]["categories"] = categories
    data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.keyword_info.value is not None
    field = data.keyword_info.value.categories
    assert field.state is expected_state
    assert field.value == expected_value


@pytest.mark.parametrize(
    ("foreign_intent", "expected_state", "expected_value"),
    [
        (None, FieldState.JSON_NULL, None),
        ([], FieldState.STATED, ()),
        (
            ["commercial", "commercial", "navigational"],
            FieldState.STATED,
            ("commercial", "commercial", "navigational"),
        ),
    ],
)
def test_synthetic_foreign_intent_states_order_and_duplicates(
    foreign_intent: object, expected_state: FieldState, expected_value: object
) -> None:
    item = _template_item()
    item["keyword_data"]["search_intent_info"]["foreign_intent"] = foreign_intent
    data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.search_intent_info.value is not None
    field = data.search_intent_info.value.foreign_intent
    assert field.state is expected_state
    assert field.value == expected_value


def test_synthetic_highlighted_preserves_order_and_duplicates() -> None:
    item = _template_item()
    item["ranked_serp_element"]["serp_item"]["highlighted"] = ["b", "a", "b"]
    serp = _only_serp_item(_parse(_encode(_one_item_document(item))))
    assert serp.highlighted.value == ("b", "a", "b")


def test_synthetic_core_keyword_and_clustering_states_are_independent() -> None:
    item = _template_item()
    props = item["keyword_data"]["keyword_properties"]
    props["core_keyword"] = "elisa lam"
    props["synonym_clustering_algorithm"] = None
    data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.keyword_properties.value is not None
    assert data.keyword_properties.value.core_keyword.value == "elisa lam"
    assert data.keyword_properties.value.synonym_clustering_algorithm.state is (
        FieldState.JSON_NULL
    )
    item = _template_item()
    props = item["keyword_data"]["keyword_properties"]
    props["core_keyword"] = None
    props["synonym_clustering_algorithm"] = "text_processing"
    data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.keyword_properties.value is not None
    assert data.keyword_properties.value.core_keyword.state is FieldState.JSON_NULL
    assert (
        data.keyword_properties.value.synonym_clustering_algorithm.value
        == "text_processing"
    )


def test_synthetic_detected_language_may_disagree_with_the_request() -> None:
    item = _template_item()
    item["keyword_data"]["keyword_properties"]["detected_language"] = "ja"
    item["keyword_data"]["keyword_properties"]["is_another_language"] = True
    item["keyword_data"]["language_code"] = "ja"
    ir = _parse(_encode(_one_item_document(item)))
    data = _only_keyword_data(ir)
    assert data.keyword_properties.value is not None
    assert data.keyword_properties.value.detected_language.value == "ja"
    assert data.keyword_properties.value.is_another_language.value is True
    assert data.language_code.value == "ja"
    # The verified Attempt is untouched by provider language testimony.
    assert ir.request.language_code == "en"


def test_synthetic_keyword_data_absent_and_null_stay_distinct() -> None:
    item = _template_item()
    item["keyword_data"] = None
    assert _only_item(_parse(_encode(_one_item_document(item)))).keyword_data.state is (
        FieldState.JSON_NULL
    )
    item = _template_item()
    del item["keyword_data"]
    assert _parse_error(_encode(_one_item_document(item))) == "missing_field"


def test_synthetic_nested_enrichment_absent_null_and_stated_are_distinct() -> None:
    for name in (
        "keyword_info",
        "keyword_properties",
        "avg_backlinks_info",
        "search_intent_info",
        "serp_info",
    ):
        item = _template_item()
        item["keyword_data"][name] = None
        data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
        assert getattr(data, name).state is FieldState.JSON_NULL
        item = _template_item()
        del item["keyword_data"][name]
        data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
        assert getattr(data, name).state is FieldState.ABSENT


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-07-10T21:54:27+00:00",
        "2026-07-10 21:54:27",
        "2026-07-10 21:54:27 +01:00",
        "2026-13-10 21:54:27 +00:00",
        "2026-02-30 21:54:27 +00:00",
        "2026-07-10 25:54:27 +00:00",
        "10 days ago",
        "07/08/2026 00:00:00",
        "2026-07-10 21:54:27 +00:00 ",
    ],
)
def test_synthetic_invalid_provider_timestamps_are_rejected(timestamp: str) -> None:
    item = _template_item()
    item["ranked_serp_element"]["last_updated_time"] = timestamp
    assert _parse_error(_encode(_one_item_document(item))) == "invalid_timestamp"


def test_synthetic_structure_local_clocks_may_disagree() -> None:
    item = _template_item()
    item["ranked_serp_element"]["last_updated_time"] = "2020-01-01 00:00:00 +00:00"
    item["keyword_data"]["keyword_info"]["last_updated_time"] = "2001-02-03 04:05:06 +00:00"
    item["keyword_data"]["search_intent_info"]["last_updated_time"] = (
        "1999-12-31 23:59:59 +00:00"
    )
    item["keyword_data"]["avg_backlinks_info"]["last_updated_time"] = (
        "0001-01-01 00:00:00 +00:00"
    )
    ir = _parse(_encode(_one_item_document(item)))
    element = _only_item(ir).ranked_serp_element.value
    data = _only_keyword_data(ir)
    assert element is not None
    assert data.keyword_info.value is not None
    assert data.search_intent_info.value is not None
    assert data.avg_backlinks_info.value is not None
    assert element.last_updated_time.value == "2020-01-01 00:00:00 +00:00"
    assert data.keyword_info.value.last_updated_time.value == "2001-02-03 04:05:06 +00:00"
    assert (
        data.search_intent_info.value.last_updated_time.value == "1999-12-31 23:59:59 +00:00"
    )
    # Year 1 is a real calendar datetime and stays exact string testimony.
    assert (
        data.avg_backlinks_info.value.last_updated_time.value == "0001-01-01 00:00:00 +00:00"
    )


def test_synthetic_pre_snippet_is_never_timestamp_validated() -> None:
    for text in ("07/08/2026 00:00:00", "4 days ago", "2026-07-10 21:54:27", ""):
        item = _template_item()
        item["ranked_serp_element"]["serp_item"]["pre_snippet"] = text
        serp = _only_serp_item(_parse(_encode(_one_item_document(item))))
        assert serp.pre_snippet.value == text


@pytest.mark.parametrize(
    "locus",
    ["clickstream_keyword_info", "keyword_info_normalized_with_clickstream"],
)
def test_synthetic_populated_keyword_clickstream_locus_fails(locus: str) -> None:
    item = _template_item()
    item["keyword_data"][locus] = {"search_volume": 10}
    assert _parse_error(_encode(_one_item_document(item))) == "request_disabled_populated"


def test_synthetic_populated_serp_item_clickstream_etv_fails() -> None:
    item = _template_item()
    item["ranked_serp_element"]["serp_item"]["clickstream_etv"] = 1
    assert _parse_error(_encode(_one_item_document(item))) == "request_disabled_populated"


@pytest.mark.parametrize(
    "locus",
    ["clickstream_keyword_info", "keyword_info_normalized_with_clickstream"],
)
def test_synthetic_absent_clickstream_locus_is_still_not_requested(locus: str) -> None:
    item = _template_item()
    del item["keyword_data"][locus]
    data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
    assert getattr(data, locus).state is FieldState.NOT_REQUESTED


def test_synthetic_populated_bing_normalization_is_unsupported_not_clickstream() -> None:
    item = _template_item()
    item["keyword_data"]["keyword_info_normalized_with_bing"] = {"search_volume": 10}
    assert _parse_error(_encode(_one_item_document(item))) == "unsupported_shape"


def test_synthetic_bing_absent_and_null_stay_independent_states() -> None:
    item = _template_item()
    del item["keyword_data"]["keyword_info_normalized_with_bing"]
    data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.keyword_info_normalized_with_bing.state is FieldState.ABSENT
    assert data.clickstream_keyword_info.state is FieldState.NOT_REQUESTED
    item = _template_item()
    item["keyword_data"]["keyword_info_normalized_with_bing"] = None
    data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.keyword_info_normalized_with_bing.state is FieldState.JSON_NULL


def test_synthetic_keyword_must_be_a_present_string() -> None:
    item = _template_item()
    del item["keyword_data"]["keyword"]
    assert _parse_error(_encode(_one_item_document(item))) == "wrong_type"
    item = _template_item()
    item["keyword_data"]["keyword"] = 5
    assert _parse_error(_encode(_one_item_document(item))) == "wrong_type"


def test_synthetic_ranked_serp_element_absent_null_and_missing_serp_item() -> None:
    item = _template_item()
    item["ranked_serp_element"] = None
    assert _only_item(
        _parse(_encode(_one_item_document(item)))
    ).ranked_serp_element.state is FieldState.JSON_NULL
    item = _template_item()
    del item["ranked_serp_element"]["serp_item"]
    assert _parse_error(_encode(_one_item_document(item))) == "missing_field"


def test_synthetic_backlink_metrics_stay_decimal_capable() -> None:
    item = _template_item()
    links = item["keyword_data"]["avg_backlinks_info"]
    links["backlinks"] = Decimal("1234.5678901234567890")
    links["main_domain_rank"] = 0
    links["rank"] = None
    data = _only_keyword_data(_parse(_encode(_one_item_document(item))))
    assert data.avg_backlinks_info.value is not None
    parsed = data.avg_backlinks_info.value
    assert parsed.backlinks.value == Decimal("1234.5678901234567890")
    assert isinstance(parsed.backlinks.value, Decimal)
    assert parsed.main_domain_rank.value == Decimal(0)
    assert parsed.rank.state is FieldState.JSON_NULL
