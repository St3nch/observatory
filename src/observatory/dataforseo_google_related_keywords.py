"""Strict DataForSEO Google Related Keywords parser and typed in-memory IR.

RK-03 interprets one complete Related Keywords response body against its verified Attempt
parameters. It preserves provider testimony — returned rows, relationship occurrences,
enrichment, field states, order, and independent clocks — without deciding Observation
identity, canonical keyword identity, graph node identity, completeness, or Strategy
meaning. Those belong to RK-04 or later.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Final

from observatory.capture_event import RELATED_KEYWORDS_ADAPTER_CONTRACT
from observatory.dataforseo_keyword_overview import Field, FieldState, ParseClassification

SUCCESS_STATUS: Final[int] = 20000
PROVIDER: Final[str] = "dataforseo"
PARSER_CONTRACT: Final[str] = "dataforseo-labs-google-related-keywords-live-parser-v1"
SE_TYPE: Final[str] = "google"

# Calendar bound for monthly Data Periods and provider clocks. Keyword Overview's
# 2000..2100 window is a Recipe rule for its own monthly series and is not imported here.
YEAR_MIN: Final[int] = 1
YEAR_MAX: Final[int] = 9999

# Claimed-contract traversal bound. A returned depth 4 stays parseable even though the
# frozen RK-01 Attempt requests depth 3; request/depth disagreement is RK-04 work.
DEPTH_MIN: Final[int] = 0
DEPTH_MAX: Final[int] = 4

# Frozen RK-01 adapter values. Only the bounded operator seed varies.
_FROZEN_LOCATION_CODE: Final[int] = 2840
_FROZEN_LANGUAGE_CODE: Final[str] = "en"
_FROZEN_DEPTH: Final[int] = 3
_FROZEN_LIMIT: Final[int] = 1000
_FROZEN_OFFSET: Final[int] = 0
_FROZEN_ORDER_BY: Final[str] = "keyword_data.keyword_info.search_volume,desc"

# Duplicated from the RK-01 adapter grammar rather than shared, so this parser adds no
# capture_event seam. `match` mirrors the adapter exactly; a parser that rejected a seed
# the adapter accepted would refuse verified Evidence.
_SEED_MAX_CHARS: Final[int] = 80
_SEED_MAX_WORDS: Final[int] = 10
_SEED_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9 &'()+,./:-]*[A-Za-z0-9])?$"
)

_PROVIDER_TIME_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} \+00:00$"
)
_PROVIDER_TIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

_ROOT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "cost",
        "status_code",
        "status_message",
        "tasks",
        "tasks_count",
        "tasks_error",
        "time",
        "version",
    }
)
_TASK_KEYS: Final[frozenset[str]] = frozenset(
    {
        "cost",
        "data",
        "id",
        "path",
        "result",
        "result_count",
        "status_code",
        "status_message",
        "time",
    }
)
_ECHO_KEYS: Final[frozenset[str]] = frozenset(
    {
        "api",
        "depth",
        "function",
        "ignore_synonyms",
        "include_clickstream_data",
        "include_seed_keyword",
        "include_serp_info",
        "keyword",
        "language_code",
        "limit",
        "location_code",
        "offset",
        "order_by",
        "replace_with_core_keyword",
        "se_type",
    }
)
_PARAMETER_KEYS: Final[frozenset[str]] = frozenset(
    {
        "contract",
        "depth",
        "ignore_synonyms",
        "include_clickstream_data",
        "include_seed_keyword",
        "include_serp_info",
        "keyword",
        "language_code",
        "limit",
        "location_code",
        "offset",
        "order_by",
        "replace_with_core_keyword",
    }
)
_RESULT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "items",
        "items_count",
        "language_code",
        "location_code",
        "se_type",
        "seed_keyword",
        "seed_keyword_data",
        "total_count",
    }
)
_ITEM_KEYS: Final[frozenset[str]] = frozenset(
    {"depth", "keyword_data", "related_keywords", "se_type"}
)
_KEYWORD_DATA_KEYS: Final[frozenset[str]] = frozenset(
    {
        "avg_backlinks_info",
        "clickstream_keyword_info",
        "keyword",
        "keyword_info",
        "keyword_info_normalized_with_bing",
        "keyword_info_normalized_with_clickstream",
        "keyword_properties",
        "language_code",
        "location_code",
        "se_type",
        "search_intent_info",
        "serp_info",
    }
)
_KEYWORD_INFO_KEYS: Final[frozenset[str]] = frozenset(
    {
        "categories",
        "competition",
        "competition_level",
        "cpc",
        "high_top_of_page_bid",
        "last_updated_time",
        "low_top_of_page_bid",
        "monthly_searches",
        "se_type",
        "search_volume",
        "search_volume_trend",
    }
)
_MONTHLY_KEYS: Final[frozenset[str]] = frozenset({"month", "search_volume", "year"})
_TREND_KEYS: Final[frozenset[str]] = frozenset({"monthly", "quarterly", "yearly"})
_PROPERTIES_KEYS: Final[frozenset[str]] = frozenset(
    {
        "core_keyword",
        "detected_language",
        "is_another_language",
        "keyword_difficulty",
        "se_type",
        "synonym_clustering_algorithm",
    }
)
_BACKLINKS_KEYS: Final[frozenset[str]] = frozenset(
    {
        "backlinks",
        "dofollow",
        "last_updated_time",
        "main_domain_rank",
        "rank",
        "referring_domains",
        "referring_main_domains",
        "referring_pages",
        "se_type",
    }
)
_INTENT_KEYS: Final[frozenset[str]] = frozenset(
    {"foreign_intent", "last_updated_time", "main_intent", "se_type"}
)
_SERP_KEYS: Final[frozenset[str]] = frozenset(
    {
        "check_url",
        "last_updated_time",
        "previous_updated_time",
        "se_results_count",
        "se_type",
        "serp_item_types",
    }
)


class RelatedKeywordsParseError(Exception):
    """Strict Related Keywords parse failed."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        super().__init__(f"{code} at {path}: {message}")


@dataclass(frozen=True)
class RequestContext:
    """The exact verified Attempt parameters for the closed RK-01 adapter."""

    contract: str
    keyword: str
    location_code: int
    language_code: str
    depth: int
    limit: int
    offset: int
    order_by: tuple[str, ...]
    include_seed_keyword: bool
    include_serp_info: bool
    include_clickstream_data: bool
    ignore_synonyms: bool
    replace_with_core_keyword: bool


@dataclass(frozen=True)
class ProviderEcho:
    """Provider restatement of the request. Typed, never value-reconciled here."""

    api: Field[str]
    function: Field[str]
    se_type: Field[str]
    keyword: Field[str]
    location_code: Field[int]
    language_code: Field[str]
    depth: Field[int]
    limit: Field[int]
    offset: Field[int]
    order_by: Field[tuple[str, ...]]
    include_seed_keyword: Field[bool]
    include_serp_info: Field[bool]
    include_clickstream_data: Field[bool]
    ignore_synonyms: Field[bool]
    replace_with_core_keyword: Field[bool]


@dataclass(frozen=True)
class MonthlySearch:
    """One provider monthly Data Period point, keyed by (year, month)."""

    year: int
    month: int
    search_volume: int
    provider_array_index: int


@dataclass(frozen=True)
class SearchVolumeTrend:
    """Provider-stated signed trend integers. No trend is computed here."""

    monthly: Field[int]
    quarterly: Field[int]
    yearly: Field[int]


@dataclass(frozen=True)
class KeywordInfo:
    se_type: Field[str]
    last_updated_time: Field[str]
    competition: Field[Decimal]
    competition_level: Field[str]
    cpc: Field[Decimal]
    search_volume: Field[int]
    low_top_of_page_bid: Field[Decimal]
    high_top_of_page_bid: Field[Decimal]
    categories: Field[tuple[int, ...]]
    monthly_searches: Field[tuple[MonthlySearch, ...]]
    search_volume_trend: Field[SearchVolumeTrend]


@dataclass(frozen=True)
class KeywordProperties:
    se_type: Field[str]
    core_keyword: Field[str]
    synonym_clustering_algorithm: Field[str]
    keyword_difficulty: Field[int]
    detected_language: Field[str]
    is_another_language: Field[bool]


@dataclass(frozen=True)
class AvgBacklinksInfo:
    se_type: Field[str]
    backlinks: Field[Decimal]
    dofollow: Field[Decimal]
    referring_pages: Field[Decimal]
    referring_domains: Field[Decimal]
    referring_main_domains: Field[Decimal]
    rank: Field[Decimal]
    main_domain_rank: Field[Decimal]
    last_updated_time: Field[str]


@dataclass(frozen=True)
class SearchIntentInfo:
    se_type: Field[str]
    main_intent: Field[str]
    foreign_intent: Field[tuple[str, ...]]
    last_updated_time: Field[str]


@dataclass(frozen=True)
class SerpInfo:
    """SERP enrichment. A present object whose fields are null stays STATED and distinct
    from a JSON-null `serp_info`; its `0001-...` clock is exact string testimony only."""

    se_type: Field[str]
    check_url: Field[str]
    serp_item_types: Field[tuple[str, ...]]
    se_results_count: Field[int]
    last_updated_time: Field[str]
    previous_updated_time: Field[str]


@dataclass(frozen=True)
class KeywordData:
    keyword: str
    location_code: Field[int]
    language_code: Field[str]
    se_type: Field[str]
    keyword_info: Field[KeywordInfo]
    keyword_properties: Field[KeywordProperties]
    avg_backlinks_info: Field[AvgBacklinksInfo]
    search_intent_info: Field[SearchIntentInfo]
    serp_info: Field[SerpInfo]
    keyword_info_normalized_with_bing: Field[None]
    keyword_info_normalized_with_clickstream: Field[None]
    clickstream_keyword_info: Field[None]


@dataclass(frozen=True)
class RelatedKeywordReference:
    """One ordered relationship occurrence inside one source item's provider array."""

    target: str
    provider_array_index: int


@dataclass(frozen=True)
class RelatedKeywordsItem:
    provider_array_index: int
    depth: int
    se_type: str
    keyword_data: Field[KeywordData]
    related_keywords: Field[tuple[RelatedKeywordReference, ...]]


@dataclass(frozen=True)
class RelatedKeywordsResult:
    seed_keyword: str
    seed_keyword_data: Field[KeywordData]
    location_code: Field[int]
    language_code: Field[str]
    se_type: Field[str]
    total_count: int
    items_count: int
    items: tuple[RelatedKeywordsItem, ...]


@dataclass(frozen=True)
class RelatedKeywordsIR:
    """Parser-only IR. `outcome` is a parser label, never a repository Outcome."""

    outcome: ParseClassification
    request: RequestContext
    echo: ProviderEcho
    version: str
    status_code: int
    status_message: str
    duration: str
    cost: Decimal
    tasks_count: int
    tasks_error: int
    task_id: str
    task_status_code: int
    task_status_message: str
    task_duration: str
    task_cost: Decimal
    task_path: tuple[str, ...]
    result_count: int
    result: RelatedKeywordsResult | None


def parse_related_keywords(
    body: bytes, parameters: Mapping[str, object]
) -> RelatedKeywordsIR:
    """Parse Related Keywords body bytes against verified Attempt parameters."""

    request = _request_context(parameters)
    document = _decode_json(body)
    root = _object(document, "")
    _reject_unknown(root, _ROOT_KEYS, "")
    version = _require_str(root.get("version"), "/version")
    status = _require_int(root.get("status_code"), "/status_code")
    status_message = _require_str(root.get("status_message"), "/status_message")
    duration = _require_str(root.get("time"), "/time")
    cost = _require_decimal(root.get("cost"), "/cost")
    tasks_count = _require_nonneg_int(root.get("tasks_count"), "/tasks_count")
    tasks_error = _require_nonneg_int(root.get("tasks_error"), "/tasks_error")
    task_list = _require_array(root.get("tasks"), "/tasks")
    if tasks_count != len(task_list):
        raise RelatedKeywordsParseError(
            "count_mismatch", "/tasks_count", "tasks_count does not match tasks length"
        )
    if len(task_list) != 1:
        raise RelatedKeywordsParseError(
            "tasks_length", "/tasks", "exactly one task is required"
        )
    task = _object(task_list[0], "/tasks/0")
    _reject_unknown(task, _TASK_KEYS, "/tasks/0")
    task_status = _require_int(task.get("status_code"), "/tasks/0/status_code")
    task_message = _require_str(task.get("status_message"), "/tasks/0/status_message")
    task_duration = _require_str(task.get("time"), "/tasks/0/time")
    task_cost = _require_decimal(task.get("cost"), "/tasks/0/cost")
    task_id = _require_str(task.get("id"), "/tasks/0/id")
    task_path = _string_tuple(task.get("path"), "/tasks/0/path")
    echo = _parse_echo(task.get("data"), "/tasks/0/data")
    result_count = _require_nonneg_int(task.get("result_count"), "/tasks/0/result_count")

    root_success = status == SUCCESS_STATUS
    task_success = task_status == SUCCESS_STATUS
    if root_success != task_success:
        raise RelatedKeywordsParseError(
            "inconsistent_status",
            "/status_code",
            "top-level and task status are inconsistent",
        )
    expected_tasks_error = 0 if task_success else 1
    if tasks_error != expected_tasks_error:
        raise RelatedKeywordsParseError(
            "count_mismatch",
            "/tasks_error",
            "tasks_error does not match the number of non-success tasks",
        )

    result: RelatedKeywordsResult | None = None
    outcome = ParseClassification.PROVIDER_ERROR
    if task_success:
        outcome = ParseClassification.ADMITTED
        result = _parse_result(task, result_count, request)

    return RelatedKeywordsIR(
        outcome=outcome,
        request=request,
        echo=echo,
        version=version,
        status_code=status,
        status_message=status_message,
        duration=duration,
        cost=cost,
        tasks_count=tasks_count,
        tasks_error=tasks_error,
        task_id=task_id,
        task_status_code=task_status,
        task_status_message=task_message,
        task_duration=task_duration,
        task_cost=task_cost,
        task_path=task_path,
        result_count=result_count,
        result=result,
    )


def _request_context(parameters: Mapping[str, object]) -> RequestContext:
    obj = _object(dict(parameters), "/attempt")
    _reject_unknown(obj, _PARAMETER_KEYS, "/attempt")
    contract = _require_str(obj.get("contract"), "/attempt/contract")
    if contract != RELATED_KEYWORDS_ADAPTER_CONTRACT:
        raise RelatedKeywordsParseError(
            "unknown_enum", "/attempt/contract", "adapter_contract is not Related Keywords"
        )
    order_by = _string_tuple(obj.get("order_by"), "/attempt/order_by")
    if order_by != (_FROZEN_ORDER_BY,):
        raise RelatedKeywordsParseError(
            "frozen_parameter",
            "/attempt/order_by",
            "order_by is not the closed Related Keywords ordering",
        )
    return RequestContext(
        contract=contract,
        keyword=_require_seed(obj.get("keyword"), "/attempt/keyword"),
        location_code=_exact_int(
            obj.get("location_code"), _FROZEN_LOCATION_CODE, "/attempt/location_code"
        ),
        language_code=_exact_str(
            obj.get("language_code"), _FROZEN_LANGUAGE_CODE, "/attempt/language_code"
        ),
        depth=_exact_int(obj.get("depth"), _FROZEN_DEPTH, "/attempt/depth"),
        limit=_exact_int(obj.get("limit"), _FROZEN_LIMIT, "/attempt/limit"),
        offset=_exact_int(obj.get("offset"), _FROZEN_OFFSET, "/attempt/offset"),
        order_by=order_by,
        include_seed_keyword=_exact_bool(
            obj.get("include_seed_keyword"), True, "/attempt/include_seed_keyword"
        ),
        include_serp_info=_exact_bool(
            obj.get("include_serp_info"), True, "/attempt/include_serp_info"
        ),
        include_clickstream_data=_exact_bool(
            obj.get("include_clickstream_data"), False, "/attempt/include_clickstream_data"
        ),
        ignore_synonyms=_exact_bool(
            obj.get("ignore_synonyms"), False, "/attempt/ignore_synonyms"
        ),
        replace_with_core_keyword=_exact_bool(
            obj.get("replace_with_core_keyword"), False, "/attempt/replace_with_core_keyword"
        ),
    )


def _require_seed(value: object, path: str) -> str:
    text = _require_str(value, path)
    if len(text) < 1 or len(text) > _SEED_MAX_CHARS:
        raise RelatedKeywordsParseError(
            "invalid_value", path, "seed keyword must be 1..80 characters"
        )
    if _SEED_RE.match(text) is None:
        raise RelatedKeywordsParseError(
            "invalid_value", path, "seed keyword is not an accepted seed query"
        )
    if len([word for word in text.split(" ") if word]) > _SEED_MAX_WORDS:
        raise RelatedKeywordsParseError(
            "invalid_value", path, "seed keyword must be at most 10 words"
        )
    return text


def _parse_echo(value: object, path: str) -> ProviderEcho:
    obj = _object(value, path)
    _reject_unknown(obj, _ECHO_KEYS, path)
    return ProviderEcho(
        api=_optional_str(obj, "api", f"{path}/api"),
        function=_optional_str(obj, "function", f"{path}/function"),
        se_type=_optional_str(obj, "se_type", f"{path}/se_type"),
        keyword=_optional_str(obj, "keyword", f"{path}/keyword"),
        location_code=_optional_int(obj, "location_code", f"{path}/location_code"),
        language_code=_optional_str(obj, "language_code", f"{path}/language_code"),
        depth=_optional_int(obj, "depth", f"{path}/depth"),
        limit=_optional_int(obj, "limit", f"{path}/limit"),
        offset=_optional_int(obj, "offset", f"{path}/offset"),
        order_by=_optional_str_tuple(obj, "order_by", f"{path}/order_by"),
        include_seed_keyword=_optional_bool(
            obj, "include_seed_keyword", f"{path}/include_seed_keyword"
        ),
        include_serp_info=_optional_bool(
            obj, "include_serp_info", f"{path}/include_serp_info"
        ),
        include_clickstream_data=_optional_bool(
            obj, "include_clickstream_data", f"{path}/include_clickstream_data"
        ),
        ignore_synonyms=_optional_bool(obj, "ignore_synonyms", f"{path}/ignore_synonyms"),
        replace_with_core_keyword=_optional_bool(
            obj, "replace_with_core_keyword", f"{path}/replace_with_core_keyword"
        ),
    )


def _parse_result(
    task: Mapping[str, object], result_count: int, request: RequestContext
) -> RelatedKeywordsResult:
    result_list = _require_array(task.get("result"), "/tasks/0/result")
    if result_count != len(result_list):
        raise RelatedKeywordsParseError(
            "count_mismatch",
            "/tasks/0/result_count",
            "result_count does not match result length",
        )
    if len(result_list) != 1:
        raise RelatedKeywordsParseError(
            "result_length", "/tasks/0/result", "exactly one result is required"
        )
    path = "/tasks/0/result/0"
    result = _object(result_list[0], path)
    _reject_unknown(result, _RESULT_KEYS, path)
    items_list = _require_array(result.get("items"), f"{path}/items")
    items_count = _require_nonneg_int(result.get("items_count"), f"{path}/items_count")
    if items_count != len(items_list):
        raise RelatedKeywordsParseError(
            "count_mismatch",
            f"{path}/items_count",
            "items_count does not match items length",
        )
    total_count = _require_nonneg_int(result.get("total_count"), f"{path}/total_count")
    items = tuple(
        _parse_item(item, f"{path}/items/{index}", index, request)
        for index, item in enumerate(items_list)
    )
    return RelatedKeywordsResult(
        seed_keyword=_require_str(result.get("seed_keyword"), f"{path}/seed_keyword"),
        seed_keyword_data=_parse_keyword_data_field(
            result, "seed_keyword_data", f"{path}/seed_keyword_data", request
        ),
        location_code=_optional_int(result, "location_code", f"{path}/location_code"),
        language_code=_optional_str(result, "language_code", f"{path}/language_code"),
        se_type=_optional_se_type(result, "se_type", f"{path}/se_type"),
        total_count=total_count,
        items_count=items_count,
        items=items,
    )


def _parse_item(
    value: object, path: str, index: int, request: RequestContext
) -> RelatedKeywordsItem:
    item = _object(value, path)
    _reject_unknown(item, _ITEM_KEYS, path)
    depth = _require_int(item.get("depth"), f"{path}/depth")
    if depth < DEPTH_MIN or depth > DEPTH_MAX:
        raise RelatedKeywordsParseError(
            "invalid_depth", f"{path}/depth", "depth is outside the claimed contract 0..4"
        )
    se_type = _require_str(item.get("se_type"), f"{path}/se_type")
    if se_type != SE_TYPE:
        raise RelatedKeywordsParseError(
            "unknown_enum", f"{path}/se_type", "se_type must be google"
        )
    return RelatedKeywordsItem(
        provider_array_index=index,
        depth=depth,
        se_type=se_type,
        keyword_data=_parse_keyword_data_field(
            item, "keyword_data", f"{path}/keyword_data", request
        ),
        related_keywords=_parse_related_keywords_field(
            item, "related_keywords", f"{path}/related_keywords"
        ),
    )


def _parse_related_keywords_field(
    obj: Mapping[str, object], key: str, path: str
) -> Field[tuple[RelatedKeywordReference, ...]]:
    if key not in obj:
        return Field[tuple[RelatedKeywordReference, ...]].absent()
    value = obj[key]
    if value is None:
        return Field[tuple[RelatedKeywordReference, ...]].json_null()
    rows = _require_array(value, path)
    # Occurrences, not a keyed set: duplicate, repeated, and self-referencing targets all
    # survive with their provider index. No dedup, no tree, no depth inference.
    return Field[tuple[RelatedKeywordReference, ...]].stated(
        tuple(
            RelatedKeywordReference(
                target=_require_str(target, f"{path}/{index}"),
                provider_array_index=index,
            )
            for index, target in enumerate(rows)
        )
    )


def _parse_keyword_data_field(
    obj: Mapping[str, object], key: str, path: str, request: RequestContext
) -> Field[KeywordData]:
    if key not in obj:
        return Field[KeywordData].absent()
    value = obj[key]
    if value is None:
        return Field[KeywordData].json_null()
    data = _object(value, path)
    _reject_unknown(data, _KEYWORD_DATA_KEYS, path)
    return Field[KeywordData].stated(
        KeywordData(
            keyword=_require_str(data.get("keyword"), f"{path}/keyword"),
            location_code=_optional_int(data, "location_code", f"{path}/location_code"),
            language_code=_optional_str(data, "language_code", f"{path}/language_code"),
            se_type=_optional_se_type(data, "se_type", f"{path}/se_type"),
            keyword_info=_parse_keyword_info(data, f"{path}/keyword_info"),
            keyword_properties=_parse_properties(data, f"{path}/keyword_properties"),
            avg_backlinks_info=_parse_backlinks(data, f"{path}/avg_backlinks_info"),
            search_intent_info=_parse_intent(data, f"{path}/search_intent_info"),
            serp_info=_parse_serp(data, f"{path}/serp_info"),
            keyword_info_normalized_with_bing=_unsupported_null(
                data,
                "keyword_info_normalized_with_bing",
                f"{path}/keyword_info_normalized_with_bing",
            ),
            keyword_info_normalized_with_clickstream=_request_disabled_null(
                data,
                "keyword_info_normalized_with_clickstream",
                f"{path}/keyword_info_normalized_with_clickstream",
                include_clickstream=request.include_clickstream_data,
            ),
            clickstream_keyword_info=_request_disabled_null(
                data,
                "clickstream_keyword_info",
                f"{path}/clickstream_keyword_info",
                include_clickstream=request.include_clickstream_data,
            ),
        )
    )


def _parse_keyword_info(obj: Mapping[str, object], path: str) -> Field[KeywordInfo]:
    info = _optional_object(obj, "keyword_info", path, _KEYWORD_INFO_KEYS)
    if info is None:
        return _propagate_state(obj, "keyword_info")
    return Field[KeywordInfo].stated(
        KeywordInfo(
            se_type=_optional_se_type(info, "se_type", f"{path}/se_type"),
            last_updated_time=_optional_timestamp(
                info, "last_updated_time", f"{path}/last_updated_time"
            ),
            competition=_optional_decimal(info, "competition", f"{path}/competition"),
            competition_level=_optional_str(
                info, "competition_level", f"{path}/competition_level"
            ),
            cpc=_optional_decimal(info, "cpc", f"{path}/cpc"),
            search_volume=_optional_nonneg_int(
                info, "search_volume", f"{path}/search_volume"
            ),
            low_top_of_page_bid=_optional_decimal(
                info, "low_top_of_page_bid", f"{path}/low_top_of_page_bid"
            ),
            high_top_of_page_bid=_optional_decimal(
                info, "high_top_of_page_bid", f"{path}/high_top_of_page_bid"
            ),
            categories=_optional_int_tuple(info, "categories", f"{path}/categories"),
            monthly_searches=_parse_monthly(
                info, "monthly_searches", f"{path}/monthly_searches"
            ),
            search_volume_trend=_parse_trend(
                info, "search_volume_trend", f"{path}/search_volume_trend"
            ),
        )
    )


def _parse_monthly(
    obj: Mapping[str, object], key: str, path: str
) -> Field[tuple[MonthlySearch, ...]]:
    if key not in obj:
        return Field[tuple[MonthlySearch, ...]].absent()
    value = obj[key]
    if value is None:
        return Field[tuple[MonthlySearch, ...]].json_null()
    rows = _require_array(value, path)
    points: list[MonthlySearch] = []
    seen: set[tuple[int, int]] = set()
    for index, item in enumerate(rows):
        point_path = f"{path}/{index}"
        row = _object(item, point_path)
        _reject_unknown(row, _MONTHLY_KEYS, point_path)
        year = _require_int(row.get("year"), f"{point_path}/year")
        month = _require_int(row.get("month"), f"{point_path}/month")
        volume = _require_nonneg_int(row.get("search_volume"), f"{point_path}/search_volume")
        if year < YEAR_MIN or year > YEAR_MAX:
            raise RelatedKeywordsParseError(
                "invalid_period", f"{point_path}/year", "year is outside calendar bounds"
            )
        if month < 1 or month > 12:
            raise RelatedKeywordsParseError(
                "invalid_period", f"{point_path}/month", "month must be 1..12"
            )
        period = (year, month)
        # A monthly series is a keyed Data Period series, not an occurrence list.
        if period in seen:
            raise RelatedKeywordsParseError(
                "duplicate_period", point_path, "duplicate historical year/month"
            )
        seen.add(period)
        points.append(
            MonthlySearch(
                year=year,
                month=month,
                search_volume=volume,
                provider_array_index=index,
            )
        )
    return Field[tuple[MonthlySearch, ...]].stated(tuple(points))


def _parse_trend(
    obj: Mapping[str, object], key: str, path: str
) -> Field[SearchVolumeTrend]:
    trend = _optional_object(obj, key, path, _TREND_KEYS)
    if trend is None:
        return _propagate_state(obj, key)
    return Field[SearchVolumeTrend].stated(
        SearchVolumeTrend(
            monthly=_optional_int(trend, "monthly", f"{path}/monthly"),
            quarterly=_optional_int(trend, "quarterly", f"{path}/quarterly"),
            yearly=_optional_int(trend, "yearly", f"{path}/yearly"),
        )
    )


def _parse_properties(
    obj: Mapping[str, object], path: str
) -> Field[KeywordProperties]:
    props = _optional_object(obj, "keyword_properties", path, _PROPERTIES_KEYS)
    if props is None:
        return _propagate_state(obj, "keyword_properties")
    return Field[KeywordProperties].stated(
        KeywordProperties(
            se_type=_optional_se_type(props, "se_type", f"{path}/se_type"),
            core_keyword=_optional_str(props, "core_keyword", f"{path}/core_keyword"),
            synonym_clustering_algorithm=_optional_str(
                props, "synonym_clustering_algorithm", f"{path}/synonym_clustering_algorithm"
            ),
            keyword_difficulty=_optional_nonneg_int(
                props, "keyword_difficulty", f"{path}/keyword_difficulty"
            ),
            detected_language=_optional_str(
                props, "detected_language", f"{path}/detected_language"
            ),
            is_another_language=_optional_bool(
                props, "is_another_language", f"{path}/is_another_language"
            ),
        )
    )


def _parse_backlinks(obj: Mapping[str, object], path: str) -> Field[AvgBacklinksInfo]:
    links = _optional_object(obj, "avg_backlinks_info", path, _BACKLINKS_KEYS)
    if links is None:
        return _propagate_state(obj, "avg_backlinks_info")
    return Field[AvgBacklinksInfo].stated(
        AvgBacklinksInfo(
            se_type=_optional_se_type(links, "se_type", f"{path}/se_type"),
            backlinks=_optional_decimal(links, "backlinks", f"{path}/backlinks"),
            dofollow=_optional_decimal(links, "dofollow", f"{path}/dofollow"),
            referring_pages=_optional_decimal(
                links, "referring_pages", f"{path}/referring_pages"
            ),
            referring_domains=_optional_decimal(
                links, "referring_domains", f"{path}/referring_domains"
            ),
            referring_main_domains=_optional_decimal(
                links, "referring_main_domains", f"{path}/referring_main_domains"
            ),
            rank=_optional_decimal(links, "rank", f"{path}/rank"),
            main_domain_rank=_optional_decimal(
                links, "main_domain_rank", f"{path}/main_domain_rank"
            ),
            last_updated_time=_optional_timestamp(
                links, "last_updated_time", f"{path}/last_updated_time"
            ),
        )
    )


def _parse_intent(obj: Mapping[str, object], path: str) -> Field[SearchIntentInfo]:
    intent = _optional_object(obj, "search_intent_info", path, _INTENT_KEYS)
    if intent is None:
        return _propagate_state(obj, "search_intent_info")
    return Field[SearchIntentInfo].stated(
        SearchIntentInfo(
            se_type=_optional_se_type(intent, "se_type", f"{path}/se_type"),
            main_intent=_optional_str(intent, "main_intent", f"{path}/main_intent"),
            foreign_intent=_optional_str_tuple(
                intent, "foreign_intent", f"{path}/foreign_intent"
            ),
            last_updated_time=_optional_timestamp(
                intent, "last_updated_time", f"{path}/last_updated_time"
            ),
        )
    )


def _parse_serp(obj: Mapping[str, object], path: str) -> Field[SerpInfo]:
    serp = _optional_object(obj, "serp_info", path, _SERP_KEYS)
    if serp is None:
        return _propagate_state(obj, "serp_info")
    return Field[SerpInfo].stated(
        SerpInfo(
            se_type=_optional_se_type(serp, "se_type", f"{path}/se_type"),
            check_url=_optional_str(serp, "check_url", f"{path}/check_url"),
            serp_item_types=_optional_str_tuple(
                serp, "serp_item_types", f"{path}/serp_item_types"
            ),
            se_results_count=_optional_nonneg_int(
                serp, "se_results_count", f"{path}/se_results_count"
            ),
            last_updated_time=_optional_timestamp(
                serp, "last_updated_time", f"{path}/last_updated_time"
            ),
            previous_updated_time=_optional_timestamp(
                serp, "previous_updated_time", f"{path}/previous_updated_time"
            ),
        )
    )


def _optional_object(
    obj: Mapping[str, object], key: str, path: str, allowed: frozenset[str]
) -> dict[str, object] | None:
    """Return the closed nested object, or None when it is absent or JSON null."""

    if key not in obj or obj[key] is None:
        return None
    nested = _object(obj[key], path)
    _reject_unknown(nested, allowed, path)
    return nested


def _propagate_state[T](obj: Mapping[str, object], key: str) -> Field[T]:
    return Field[T].absent() if key not in obj else Field[T].json_null()


def _request_disabled_null(
    obj: Mapping[str, object], key: str, path: str, *, include_clickstream: bool
) -> Field[None]:
    """Clickstream structures under the request flag verified from the Attempt."""

    if not include_clickstream:
        if key in obj and obj[key] is not None:
            raise RelatedKeywordsParseError(
                "request_disabled_populated",
                path,
                "request-disabled clickstream structure must not be populated",
            )
        return Field[None].not_requested()
    return _null_or_absent(obj, key, path)


def _unsupported_null(obj: Mapping[str, object], key: str, path: str) -> Field[None]:
    """Bing-normalized keyword info is not request-controlled and has no known shape."""

    if key not in obj:
        return Field[None].absent()
    if obj[key] is None:
        return Field[None].json_null()
    raise RelatedKeywordsParseError(
        "unsupported_shape",
        path,
        "populated keyword_info_normalized_with_bing is not supported by this parser",
    )


def _null_or_absent(obj: Mapping[str, object], key: str, path: str) -> Field[None]:
    if key not in obj:
        return Field[None].absent()
    if obj[key] is None:
        return Field[None].json_null()
    raise RelatedKeywordsParseError(
        "wrong_type", path, "populated object is not accepted here"
    )


def _optional_str(obj: Mapping[str, object], key: str, path: str) -> Field[str]:
    if key not in obj:
        return Field[str].absent()
    value = obj[key]
    if value is None:
        return Field[str].json_null()
    return Field[str].stated(_require_str(value, path))


def _optional_se_type(obj: Mapping[str, object], key: str, path: str) -> Field[str]:
    field = _optional_str(obj, key, path)
    if field.state is FieldState.STATED and field.value != SE_TYPE:
        raise RelatedKeywordsParseError("unknown_enum", path, "se_type must be google")
    return field


def _optional_int(obj: Mapping[str, object], key: str, path: str) -> Field[int]:
    if key not in obj:
        return Field[int].absent()
    value = obj[key]
    if value is None:
        return Field[int].json_null()
    return Field[int].stated(_require_int(value, path))


def _optional_nonneg_int(obj: Mapping[str, object], key: str, path: str) -> Field[int]:
    if key not in obj:
        return Field[int].absent()
    value = obj[key]
    if value is None:
        return Field[int].json_null()
    return Field[int].stated(_require_nonneg_int(value, path))


def _optional_bool(obj: Mapping[str, object], key: str, path: str) -> Field[bool]:
    if key not in obj:
        return Field[bool].absent()
    value = obj[key]
    if value is None:
        return Field[bool].json_null()
    if not isinstance(value, bool):
        raise RelatedKeywordsParseError("wrong_type", path, "must be a JSON boolean")
    return Field[bool].stated(value)


def _optional_decimal(obj: Mapping[str, object], key: str, path: str) -> Field[Decimal]:
    if key not in obj:
        return Field[Decimal].absent()
    value = obj[key]
    if value is None:
        return Field[Decimal].json_null()
    return Field[Decimal].stated(_require_decimal(value, path))


def _optional_int_tuple(
    obj: Mapping[str, object], key: str, path: str
) -> Field[tuple[int, ...]]:
    if key not in obj:
        return Field[tuple[int, ...]].absent()
    value = obj[key]
    if value is None:
        return Field[tuple[int, ...]].json_null()
    rows = _require_array(value, path)
    # Unkeyed provider array: order and duplicates are testimony. Never sort or dedup.
    return Field[tuple[int, ...]].stated(
        tuple(_require_int(item, f"{path}/{index}") for index, item in enumerate(rows))
    )


def _optional_str_tuple(
    obj: Mapping[str, object], key: str, path: str
) -> Field[tuple[str, ...]]:
    if key not in obj:
        return Field[tuple[str, ...]].absent()
    value = obj[key]
    if value is None:
        return Field[tuple[str, ...]].json_null()
    return Field[tuple[str, ...]].stated(_string_tuple(value, path))


def _optional_timestamp(obj: Mapping[str, object], key: str, path: str) -> Field[str]:
    field = _optional_str(obj, key, path)
    if field.state is FieldState.STATED:
        assert field.value is not None
        _require_provider_timestamp(field.value, path)
    return field


def _require_provider_timestamp(value: str, path: str) -> None:
    """Validate lexical form and calendar reality only. Year 1 stays exact testimony."""

    if _PROVIDER_TIME_RE.fullmatch(value) is None:
        raise RelatedKeywordsParseError(
            "invalid_timestamp", path, "provider timestamp is not YYYY-MM-DD HH:MM:SS +00:00"
        )
    year = int(value[:4])
    if year < YEAR_MIN or year > YEAR_MAX:
        raise RelatedKeywordsParseError(
            "invalid_timestamp", path, "provider timestamp year is outside calendar bounds"
        )
    try:
        datetime.strptime(value.removesuffix(" +00:00"), _PROVIDER_TIME_FORMAT)
    except ValueError as exc:
        raise RelatedKeywordsParseError(
            "invalid_timestamp", path, "provider timestamp is not a real UTC datetime"
        ) from exc


def _exact_int(value: object, expected: int, path: str) -> int:
    number = _require_int(value, path)
    if number != expected:
        raise RelatedKeywordsParseError(
            "frozen_parameter", path, f"value must be exactly {expected}"
        )
    return number


def _exact_str(value: object, expected: str, path: str) -> str:
    text = _require_str(value, path)
    if text != expected:
        raise RelatedKeywordsParseError(
            "frozen_parameter", path, f"value must be exactly {expected!r}"
        )
    return text


def _exact_bool(value: object, expected: bool, path: str) -> bool:
    if not isinstance(value, bool):
        raise RelatedKeywordsParseError("wrong_type", path, "must be a JSON boolean")
    if value is not expected:
        raise RelatedKeywordsParseError(
            "frozen_parameter", path, f"value must be exactly {expected}"
        )
    return value


def _string_tuple(value: object, path: str) -> tuple[str, ...]:
    rows = _require_array(value, path)
    return tuple(_require_str(item, f"{path}/{index}") for index, item in enumerate(rows))


def _decode_json(raw: bytes) -> object:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise RelatedKeywordsParseError("utf8_bom", "", "UTF-8 BOM is forbidden")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RelatedKeywordsParseError(
            "invalid_utf8", "", "body is not strict UTF-8"
        ) from exc
    decoder = json.JSONDecoder(
        parse_int=int,
        parse_float=Decimal,
        parse_constant=_reject_constant,
        object_pairs_hook=_object_pairs,
    )
    try:
        value, end = decoder.raw_decode(text)
    except json.JSONDecodeError as exc:
        raise RelatedKeywordsParseError("invalid_json", "", "body is not valid JSON") from exc
    if text[end:].strip() != "":
        raise RelatedKeywordsParseError(
            "trailing_data", "", "non-whitespace data follows the JSON document"
        )
    return value


def _reject_constant(value: str) -> None:
    raise RelatedKeywordsParseError(
        "non_finite_number", "", f"{value} is not a finite number"
    )


def _object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise RelatedKeywordsParseError(
                "duplicate_member", f"/{_escape(key)}", "duplicate object member name"
            )
        result[key] = value
    return result


def _reject_unknown(obj: Mapping[str, object], allowed: frozenset[str], path: str) -> None:
    extra = [key for key in obj if key not in allowed]
    if extra:
        pointer = f"{path}/{_escape(extra[0])}" if path else f"/{_escape(extra[0])}"
        raise RelatedKeywordsParseError(
            "unknown_field", pointer, "unknown field on a closed object"
        )


def _object(value: object, path: str) -> dict[str, object]:
    if isinstance(value, Mapping) and not isinstance(value, (str, bytes, bytearray)):
        return {str(key): item for key, item in value.items()}
    raise RelatedKeywordsParseError("wrong_type", path or "/", "must be an object")


def _require_array(value: object, path: str) -> list[object]:
    if not isinstance(value, list) or isinstance(value, (str, bytes, bytearray)):
        raise RelatedKeywordsParseError("wrong_type", path, "must be an array")
    return list(value)


def _require_str(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise RelatedKeywordsParseError("wrong_type", path, "must be a string")
    return value


def _require_int(value: object, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RelatedKeywordsParseError("wrong_type", path, "must be a JSON integer")
    return value


def _require_nonneg_int(value: object, path: str) -> int:
    number = _require_int(value, path)
    if number < 0:
        raise RelatedKeywordsParseError(
            "invalid_number", path, "value must not be negative"
        )
    return number


def _require_decimal(value: object, path: str) -> Decimal:
    if isinstance(value, bool):
        raise RelatedKeywordsParseError(
            "wrong_type", path, "must be a decimal-capable number"
        )
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, Decimal):
        return value
    raise RelatedKeywordsParseError("wrong_type", path, "must be a decimal-capable number")


def _escape(key: str) -> str:
    return key.replace("~", "~0").replace("/", "~1")
