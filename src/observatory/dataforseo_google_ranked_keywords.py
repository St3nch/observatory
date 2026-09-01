"""Strict DataForSEO Google Ranked Keywords parser and typed in-memory IR.

RANK-04 interprets one complete Ranked Keywords response body against its verified Attempt
parameters. It preserves provider testimony — returned occurrences, corpus and absolute-rank
aggregates, page/host/keyword strings, field states, provider order, SERP composition, keyword
enrichment, and independent structure-local clocks — without deciding Observation admission,
subject identity, canonical page identity, completeness, cross-Capture change, or Strategy
meaning. Those belong to a later separately reviewed boundary.

The parser accepts only response-body bytes plus the verified Attempt parameter mapping. It
touches no HTTP status or header, transport state, Capture classification, Evidence path,
credential, client, endpoint, network, PostgreSQL, Recipe, or API seam.

Reuse is deliberately narrow. Only `RANKED_KEYWORDS_ADAPTER_CONTRACT` and the shared
`Field`/`FieldState`/`ParseClassification` vocabulary are imported; every Ranked key set,
dataclass, grammar, and decode/type/timestamp helper is duplicated locally so this surface can
drift without dragging Keyword Overview, Related Keywords, or Google Organic with it.

PF-11 Google Organic is a structural **negative** precedent here. RANK-03 contains repeated
`rank_group` and `rank_absolute` values, exact near-duplicate keywords, open SERP-feature and
layout vocabularies, and real apex/`www` host divergence, all of which Organic's closed enums,
placement uniqueness, and keyword/text normalization would reject or silently collapse.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Final
from urllib.parse import urlsplit

from observatory.capture_event import RANKED_KEYWORDS_ADAPTER_CONTRACT
from observatory.dataforseo_keyword_overview import Field, FieldState, ParseClassification

SUCCESS_STATUS: Final[int] = 20000
PROVIDER: Final[str] = "dataforseo"
PARSER_CONTRACT: Final[str] = (
    "dataforseo-labs-google-ranked-keywords-live-paid-probe-parser-v1"
)
SE_TYPE: Final[str] = "google"

# RANK-05 Recipe-v1 Observation kinds. They are declared here beside the parser contract
# they interpret, but this module builds no Recipe document, computes no identity, and
# touches no persistence: the RANK-05 Derivation owns all of that.
CORPUS_METRICS_KIND: Final[str] = (
    "dataforseo.google.ranked_keywords.corpus_metrics.v1"
)
RANKED_RESULT_KIND: Final[str] = "dataforseo.google.ranked_keywords.ranked_result.v1"
KEYWORD_DATA_KIND: Final[str] = "dataforseo.google.ranked_keywords.keyword_data.v1"
MONTHLY_KIND: Final[str] = (
    "dataforseo.google.ranked_keywords.monthly_search_volume.v1"
)

# The two independently stated rank-system loci. `metrics` and `metrics_absolute` answer on
# different rank systems and are never reconciled against each other, so the locus is an
# identity axis of the corpus-metrics kind rather than two sibling structures in one row.
RANK_SYSTEM_GROUP: Final[str] = "rank_group"
RANK_SYSTEM_ABSOLUTE: Final[str] = "rank_absolute"
RANK_SYSTEMS: Final[tuple[str, ...]] = (RANK_SYSTEM_GROUP, RANK_SYSTEM_ABSOLUTE)

# Calendar bound for provider clocks and monthly Data Periods. Keyword Overview's narrower
# 2000..2100 window is that surface's own Recipe rule and is not imported here.
YEAR_MIN: Final[int] = 1
YEAR_MAX: Final[int] = 9999
MONTH_MIN: Final[int] = 1
MONTH_MAX: Final[int] = 12

# The five aggregate loci this frozen Attempt requests. `metrics` and `metrics_absolute` are
# required to expose exactly these because the verified request asks for exactly these and the
# reviewed v1 result contract answers on exactly these — not because one Capture proves a
# universal provider invariant.
REQUESTED_ITEM_TYPES: Final[tuple[str, ...]] = (
    "organic",
    "paid",
    "featured_snippet",
    "local_pack",
    "ai_overview_reference",
)

# Frozen RANK-02 adapter values. Only the bounded operator `target` varies.
_FROZEN_LOCATION_CODE: Final[int] = 2840
_FROZEN_LANGUAGE_CODE: Final[str] = "en"
_FROZEN_LIMIT: Final[int] = 100
_FROZEN_OFFSET: Final[int] = 0
_FROZEN_HISTORICAL_SERP_MODE: Final[str] = "all"
_FROZEN_ORDER_BY: Final[str] = "ranked_serp_element.serp_item.rank_group,asc"

# Duplicated from the RANK-02 adapter grammar rather than shared, so parser failures use
# parser-local deterministic error semantics and this module adds no capture_event seam. The
# `\A...\Z` anchors are exact: Python's `\Z` is absolute end of string, so a trailing newline
# is rejected. A parser that accepted a target the adapter refuses would invent request
# authority; a parser that refused one the adapter accepted would refuse verified Evidence.
_TARGET_RE: Final[re.Pattern[str]] = re.compile(
    r"\A[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.[a-z](?:[a-z0-9-]{0,61}[a-z0-9])?\Z"
)
_TARGET_LABEL_MAX: Final[int] = 63
_TARGET_EXCLUDED_FIRST_LABEL: Final[str] = "www"
_TARGET_PUNYCODE_PREFIX: Final[str] = "xn--"

# The Attempt target grammar is deliberately NOT applied to provider `domain`; doing so would
# reject the 25 real `www.theconspiratory.com` rows RANK-03 actually returned.
_URL_SCHEMES: Final[frozenset[str]] = frozenset({"http", "https"})

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
        "function",
        "historical_serp_mode",
        "ignore_synonyms",
        "include_clickstream_data",
        "item_types",
        "language_code",
        "limit",
        "load_rank_absolute",
        "location_code",
        "offset",
        "order_by",
        "se_type",
        "target",
    }
)
_PARAMETER_KEYS: Final[frozenset[str]] = frozenset(
    {
        "contract",
        "historical_serp_mode",
        "ignore_synonyms",
        "include_clickstream_data",
        "item_types",
        "language_code",
        "limit",
        "load_rank_absolute",
        "location_code",
        "offset",
        "order_by",
        "target",
    }
)
_RESULT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "items",
        "items_count",
        "language_code",
        "location_code",
        "metrics",
        "metrics_absolute",
        "se_type",
        "target",
        "total_count",
    }
)
_ITEM_KEYS: Final[frozenset[str]] = frozenset(
    {"keyword_data", "ranked_serp_element", "se_type"}
)
_RANKED_SERP_ELEMENT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "check_url",
        "is_lost",
        "keyword_difficulty",
        "last_updated_time",
        "previous_updated_time",
        "se_results_count",
        "se_type",
        "serp_item",
        "serp_item_types",
    }
)
_SERP_ITEM_KEYS: Final[frozenset[str]] = frozenset(
    {
        "about_this_result",
        "amp_version",
        "backlinks_info",
        "breadcrumb",
        "clickstream_etv",
        "description",
        "domain",
        "estimated_paid_traffic_cost",
        "etv",
        "extended_snippet",
        "highlighted",
        "is_featured_snippet",
        "is_image",
        "is_malicious",
        "is_video",
        "links",
        "main_domain",
        "position",
        "pre_snippet",
        "rank_absolute",
        "rank_changes",
        "rank_group",
        "rank_info",
        "rating",
        "relative_url",
        "se_type",
        "title",
        "type",
        "url",
        "website_name",
        "xpath",
    }
)
_RANK_CHANGES_KEYS: Final[frozenset[str]] = frozenset(
    {"is_down", "is_new", "is_up", "previous_rank_absolute"}
)
_RANK_INFO_KEYS: Final[frozenset[str]] = frozenset({"main_domain_rank", "page_rank"})
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
        "search_intent_info",
        "se_type",
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
        "search_volume",
        "search_volume_trend",
        "se_type",
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
_SERP_INFO_KEYS: Final[frozenset[str]] = frozenset(
    {
        "check_url",
        "last_updated_time",
        "previous_updated_time",
        "se_results_count",
        "se_type",
        "serp_item_types",
    }
)
_POSITION_BUCKET_KEYS: Final[tuple[str, ...]] = (
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
_MOVEMENT_KEYS: Final[tuple[str, ...]] = ("is_new", "is_up", "is_down", "is_lost")
_CLICKSTREAM_AGGREGATE_KEYS: Final[tuple[str, ...]] = (
    "clickstream_etv",
    "clickstream_gender_distribution",
    "clickstream_age_distribution",
)
# 22 members. `metrics` states full-corpus counts, ETV, and estimated paid traffic cost.
_METRICS_FAMILY_KEYS: Final[frozenset[str]] = frozenset(
    (
        *_POSITION_BUCKET_KEYS,
        *_MOVEMENT_KEYS,
        *_CLICKSTREAM_AGGREGATE_KEYS,
        "count",
        "etv",
        "estimated_paid_traffic_cost",
    )
)
# 19 members. `metrics_absolute` deliberately never gains `count`, `etv`, or
# `estimated_paid_traffic_cost`: RANK-03 Evidence does not state them and a mutable docs
# example showing them on some family is not this contract.
_METRICS_ABSOLUTE_FAMILY_KEYS: Final[frozenset[str]] = frozenset(
    (*_POSITION_BUCKET_KEYS, *_MOVEMENT_KEYS, *_CLICKSTREAM_AGGREGATE_KEYS)
)
_AGGREGATE_FAMILY_KEYS: Final[frozenset[str]] = frozenset(REQUESTED_ITEM_TYPES)

# Structural spine members whose absence makes the containing object uninterpretable Ranked
# testimony. Every other known member keeps an explicit Field state, so absence is recorded
# rather than silently defaulted.
_REQUIRED_ROOT_KEYS: Final[frozenset[str]] = _ROOT_KEYS
_REQUIRED_TASK_KEYS: Final[frozenset[str]] = frozenset(
    {
        "cost",
        "data",
        "id",
        "path",
        "result_count",
        "status_code",
        "status_message",
        "time",
    }
)
_REQUIRED_RESULT_KEYS: Final[frozenset[str]] = frozenset(
    {"items", "items_count", "metrics", "metrics_absolute", "total_count"}
)
_REQUIRED_ITEM_KEYS: Final[frozenset[str]] = _ITEM_KEYS
_REQUIRED_SERP_ITEM_KEYS: Final[frozenset[str]] = frozenset(
    {"rank_absolute", "rank_group", "type", "url"}
)


class RankedKeywordsParseError(Exception):
    """Strict Ranked Keywords parse failed."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        super().__init__(f"{code} at {path}: {message}")


@dataclass(frozen=True)
class RequestContext:
    """The exact verified Attempt parameters for the closed RANK-02 adapter."""

    contract: str
    target: str
    location_code: int
    language_code: str
    item_types: tuple[str, ...]
    ignore_synonyms: bool
    include_clickstream_data: bool
    limit: int
    offset: int
    load_rank_absolute: bool
    historical_serp_mode: str
    order_by: tuple[str, ...]


@dataclass(frozen=True)
class ProviderEcho:
    """Provider restatement of the request. Typed, never value-reconciled here."""

    api: Field[str]
    function: Field[str]
    se_type: Field[str]
    target: Field[str]
    location_code: Field[int]
    language_code: Field[str]
    item_types: Field[tuple[str, ...]]
    ignore_synonyms: Field[bool]
    include_clickstream_data: Field[bool]
    limit: Field[int]
    offset: Field[int]
    load_rank_absolute: Field[bool]
    historical_serp_mode: Field[str]
    order_by: Field[tuple[str, ...]]


@dataclass(frozen=True)
class PositionBuckets:
    """Twelve provider rank-position buckets. No sum is reconciled with anything."""

    pos_1: int
    pos_2_3: int
    pos_4_10: int
    pos_11_20: int
    pos_21_30: int
    pos_31_40: int
    pos_41_50: int
    pos_51_60: int
    pos_61_70: int
    pos_71_80: int
    pos_81_90: int
    pos_91_100: int


@dataclass(frozen=True)
class MetricsFamily:
    """One `metrics.<requested_type>` full-corpus aggregate locus (22 members)."""

    positions: PositionBuckets
    count: int
    etv: Field[Decimal]
    estimated_paid_traffic_cost: Field[Decimal]
    is_new: int
    is_up: int
    is_down: int
    is_lost: int
    clickstream_etv: Field[None]
    clickstream_gender_distribution: Field[None]
    clickstream_age_distribution: Field[None]


@dataclass(frozen=True)
class MetricsAbsoluteFamily:
    """One `metrics_absolute.<requested_type>` locus (19 members). Distinct shape."""

    positions: PositionBuckets
    is_new: int
    is_up: int
    is_down: int
    is_lost: int
    clickstream_etv: Field[None]
    clickstream_gender_distribution: Field[None]
    clickstream_age_distribution: Field[None]


@dataclass(frozen=True)
class AggregateMetrics:
    organic: MetricsFamily
    paid: MetricsFamily
    featured_snippet: MetricsFamily
    local_pack: MetricsFamily
    ai_overview_reference: MetricsFamily


@dataclass(frozen=True)
class AggregateMetricsAbsolute:
    organic: MetricsAbsoluteFamily
    paid: MetricsAbsoluteFamily
    featured_snippet: MetricsAbsoluteFamily
    local_pack: MetricsAbsoluteFamily
    ai_overview_reference: MetricsAbsoluteFamily


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
    """Keyword-corpus backlink averages. Not the target page's `serp_item.backlinks_info`,
    and its `main_domain_rank` is not `rank_info.main_domain_rank`."""

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
    """Keyword-local SERP enrichment. Six of its members restate `ranked_serp_element`
    values; both paths stay independently addressable and may disagree."""

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
class RankChanges:
    """Provider-internal comparison testimony. Not Observatory Capture-to-Capture change."""

    is_new: Field[bool]
    is_up: Field[bool]
    is_down: Field[bool]
    previous_rank_absolute: Field[int]


@dataclass(frozen=True)
class RankInfo:
    page_rank: Field[int]
    main_domain_rank: Field[int]


@dataclass(frozen=True)
class SerpItem:
    """One returned SERP occurrence (31 known members).

    `type` and `position` are open provider strings, never closed Organic enums. Only `url`
    receives a narrow HTTP(S) syntax check; every other URL-like or text member is exact
    provider testimony with no host, case, path, query, fragment, or trailing-slash
    normalization.
    """

    se_type: Field[str]
    type: str
    rank_group: int
    rank_absolute: int
    position: Field[str]
    xpath: Field[str]
    domain: Field[str]
    main_domain: Field[str]
    website_name: Field[str]
    relative_url: Field[str]
    url: str
    breadcrumb: Field[str]
    title: Field[str]
    description: Field[str]
    pre_snippet: Field[str]
    highlighted: Field[tuple[str, ...]]
    is_image: Field[bool]
    is_video: Field[bool]
    is_featured_snippet: Field[bool]
    is_malicious: Field[bool]
    amp_version: Field[bool]
    etv: Field[Decimal]
    estimated_paid_traffic_cost: Field[Decimal]
    clickstream_etv: Field[None]
    rank_changes: Field[RankChanges]
    rank_info: Field[RankInfo]
    about_this_result: Field[None]
    backlinks_info: Field[None]
    extended_snippet: Field[None]
    links: Field[None]
    rating: Field[None]


@dataclass(frozen=True)
class RankedSerpElement:
    check_url: Field[str]
    se_results_count: Field[int]
    keyword_difficulty: Field[int]
    is_lost: Field[bool]
    last_updated_time: Field[str]
    previous_updated_time: Field[str]
    serp_item_types: Field[tuple[str, ...]]
    se_type: Field[str]
    serp_item: SerpItem


@dataclass(frozen=True)
class RankedKeywordsItem:
    """One returned ranked occurrence. Never deduplicated by keyword, URL, path, host, or
    rank; the zero-based provider array index is retained and never resorted."""

    provider_array_index: int
    se_type: str
    keyword_data: Field[KeywordData]
    ranked_serp_element: Field[RankedSerpElement]


@dataclass(frozen=True)
class RankedKeywordsResult:
    se_type: Field[str]
    target: Field[str]
    location_code: Field[int]
    language_code: Field[str]
    total_count: int
    items_count: int
    metrics: AggregateMetrics
    metrics_absolute: AggregateMetricsAbsolute
    items: tuple[RankedKeywordsItem, ...]


@dataclass(frozen=True)
class RankedKeywordsIR:
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
    result: RankedKeywordsResult | None


def parse_ranked_keywords(
    body: bytes, parameters: Mapping[str, object]
) -> RankedKeywordsIR:
    """Parse Ranked Keywords body bytes against verified Attempt parameters."""

    request = _request_context(parameters)
    document = _decode_json(body)
    root = _object(document, "")
    _reject_unknown(root, _ROOT_KEYS, "")
    _require_members(root, _REQUIRED_ROOT_KEYS, "")
    version = _require_str(root.get("version"), "/version")
    status = _require_int(root.get("status_code"), "/status_code")
    status_message = _require_str(root.get("status_message"), "/status_message")
    duration = _require_str(root.get("time"), "/time")
    cost = _require_decimal(root.get("cost"), "/cost")
    tasks_count = _require_nonneg_int(root.get("tasks_count"), "/tasks_count")
    tasks_error = _require_nonneg_int(root.get("tasks_error"), "/tasks_error")
    task_list = _require_array(root.get("tasks"), "/tasks")
    if tasks_count != len(task_list):
        raise RankedKeywordsParseError(
            "count_mismatch", "/tasks_count", "tasks_count does not match tasks length"
        )
    if len(task_list) != 1:
        raise RankedKeywordsParseError(
            "tasks_length", "/tasks", "exactly one task is required"
        )
    task = _object(task_list[0], "/tasks/0")
    _reject_unknown(task, _TASK_KEYS, "/tasks/0")
    _require_members(task, _REQUIRED_TASK_KEYS, "/tasks/0")
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
        raise RankedKeywordsParseError(
            "inconsistent_status",
            "/status_code",
            "top-level and task status are inconsistent",
        )
    # With exactly one task the error count is fully determined. `tasks_error=2` cannot
    # rescue a two-task document, because the two-task shape already failed above.
    expected_tasks_error = 0 if task_success else 1
    if tasks_error != expected_tasks_error:
        raise RankedKeywordsParseError(
            "count_mismatch",
            "/tasks_error",
            "tasks_error does not match the number of non-success tasks",
        )

    result: RankedKeywordsResult | None = None
    outcome = ParseClassification.PROVIDER_ERROR
    if task_success:
        outcome = ParseClassification.ADMITTED
        result = _parse_result(task, result_count, request)

    return RankedKeywordsIR(
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
    _require_members(obj, _PARAMETER_KEYS, "/attempt")
    contract = _require_str(obj.get("contract"), "/attempt/contract")
    if contract != RANKED_KEYWORDS_ADAPTER_CONTRACT:
        raise RankedKeywordsParseError(
            "unknown_enum", "/attempt/contract", "adapter_contract is not Ranked Keywords"
        )
    item_types = _string_tuple(obj.get("item_types"), "/attempt/item_types")
    if item_types != REQUESTED_ITEM_TYPES:
        raise RankedKeywordsParseError(
            "frozen_parameter",
            "/attempt/item_types",
            "item_types is not the closed Ranked Keywords item-type order",
        )
    order_by = _string_tuple(obj.get("order_by"), "/attempt/order_by")
    if order_by != (_FROZEN_ORDER_BY,):
        raise RankedKeywordsParseError(
            "frozen_parameter",
            "/attempt/order_by",
            "order_by is not the closed Ranked Keywords ordering",
        )
    return RequestContext(
        contract=contract,
        target=_require_target(obj.get("target"), "/attempt/target"),
        location_code=_exact_int(
            obj.get("location_code"), _FROZEN_LOCATION_CODE, "/attempt/location_code"
        ),
        language_code=_exact_str(
            obj.get("language_code"), _FROZEN_LANGUAGE_CODE, "/attempt/language_code"
        ),
        item_types=item_types,
        ignore_synonyms=_exact_bool(
            obj.get("ignore_synonyms"), False, "/attempt/ignore_synonyms"
        ),
        include_clickstream_data=_exact_bool(
            obj.get("include_clickstream_data"),
            False,
            "/attempt/include_clickstream_data",
        ),
        limit=_exact_int(obj.get("limit"), _FROZEN_LIMIT, "/attempt/limit"),
        offset=_exact_int(obj.get("offset"), _FROZEN_OFFSET, "/attempt/offset"),
        load_rank_absolute=_exact_bool(
            obj.get("load_rank_absolute"), True, "/attempt/load_rank_absolute"
        ),
        historical_serp_mode=_exact_str(
            obj.get("historical_serp_mode"),
            _FROZEN_HISTORICAL_SERP_MODE,
            "/attempt/historical_serp_mode",
        ),
        order_by=order_by,
    )


def _require_target(value: object, path: str) -> str:
    """Apply the RANK-02 two-label ASCII domain grammar to the verified Attempt target.

    This is request-authority grammar only. Provider `domain` testimony is a different
    contract: `www.theconspiratory.com` fails here and is valid returned testimony there.
    """

    text = _require_str(value, path)
    if _TARGET_RE.match(text) is None:
        raise RankedKeywordsParseError(
            "invalid_value", path, "target is not an accepted two-label ASCII domain"
        )
    first, _, second = text.partition(".")
    if len(first) > _TARGET_LABEL_MAX or len(second) > _TARGET_LABEL_MAX:
        raise RankedKeywordsParseError(
            "invalid_value", path, "target labels must be 1..63 characters"
        )
    if first == _TARGET_EXCLUDED_FIRST_LABEL:
        raise RankedKeywordsParseError(
            "invalid_value", path, "target must not use a www first label"
        )
    if first.startswith(_TARGET_PUNYCODE_PREFIX) or second.startswith(
        _TARGET_PUNYCODE_PREFIX
    ):
        raise RankedKeywordsParseError(
            "invalid_value", path, "target must not use an ASCII punycode label"
        )
    return text


def _parse_echo(value: object, path: str) -> ProviderEcho:
    obj = _object(value, path)
    _reject_unknown(obj, _ECHO_KEYS, path)
    return ProviderEcho(
        api=_optional_str(obj, "api", f"{path}/api"),
        function=_optional_str(obj, "function", f"{path}/function"),
        se_type=_optional_se_type(obj, "se_type", f"{path}/se_type"),
        target=_optional_str(obj, "target", f"{path}/target"),
        location_code=_optional_int(obj, "location_code", f"{path}/location_code"),
        language_code=_optional_str(obj, "language_code", f"{path}/language_code"),
        item_types=_optional_str_tuple(obj, "item_types", f"{path}/item_types"),
        ignore_synonyms=_optional_bool(obj, "ignore_synonyms", f"{path}/ignore_synonyms"),
        include_clickstream_data=_optional_bool(
            obj, "include_clickstream_data", f"{path}/include_clickstream_data"
        ),
        limit=_optional_int(obj, "limit", f"{path}/limit"),
        offset=_optional_int(obj, "offset", f"{path}/offset"),
        load_rank_absolute=_optional_bool(
            obj, "load_rank_absolute", f"{path}/load_rank_absolute"
        ),
        historical_serp_mode=_optional_str(
            obj, "historical_serp_mode", f"{path}/historical_serp_mode"
        ),
        order_by=_optional_str_tuple(obj, "order_by", f"{path}/order_by"),
    )


def _parse_result(
    task: Mapping[str, object], result_count: int, request: RequestContext
) -> RankedKeywordsResult:
    if "result" not in task:
        raise RankedKeywordsParseError(
            "missing_field", "/tasks/0/result", "a successful task must state result"
        )
    result_list = _require_array(task.get("result"), "/tasks/0/result")
    if result_count != len(result_list):
        raise RankedKeywordsParseError(
            "count_mismatch",
            "/tasks/0/result_count",
            "result_count does not match result length",
        )
    if len(result_list) != 1:
        raise RankedKeywordsParseError(
            "result_length", "/tasks/0/result", "exactly one result is required"
        )
    path = "/tasks/0/result/0"
    result = _object(result_list[0], path)
    _reject_unknown(result, _RESULT_KEYS, path)
    _require_members(result, _REQUIRED_RESULT_KEYS, path)
    # v1 fails closed on a successful null/absent `items`: that branch is unobserved and no
    # null-empty semantics is accepted here.
    items_list = _require_array(result.get("items"), f"{path}/items")
    items_count = _require_nonneg_int(result.get("items_count"), f"{path}/items_count")
    if items_count != len(items_list):
        raise RankedKeywordsParseError(
            "count_mismatch",
            f"{path}/items_count",
            "items_count does not match items length",
        )
    # An independent nonnegative provider fact. RANK-04 imposes no relation between
    # `total_count`, `items_count`, returned length, or any aggregate bucket sum.
    total_count = _require_nonneg_int(result.get("total_count"), f"{path}/total_count")
    return RankedKeywordsResult(
        se_type=_optional_se_type(result, "se_type", f"{path}/se_type"),
        target=_optional_str(result, "target", f"{path}/target"),
        location_code=_optional_int(result, "location_code", f"{path}/location_code"),
        language_code=_optional_str(result, "language_code", f"{path}/language_code"),
        total_count=total_count,
        items_count=items_count,
        metrics=_parse_metrics(result.get("metrics"), f"{path}/metrics", request),
        metrics_absolute=_parse_metrics_absolute(
            result.get("metrics_absolute"), f"{path}/metrics_absolute", request
        ),
        items=tuple(
            _parse_item(item, f"{path}/items/{index}", index, request)
            for index, item in enumerate(items_list)
        ),
    )


def _parse_metrics(
    value: object, path: str, request: RequestContext
) -> AggregateMetrics:
    families = _aggregate_families(value, path)
    parsed = {
        name: _parse_metrics_family(families[name], f"{path}/{name}", request)
        for name in REQUESTED_ITEM_TYPES
    }
    return AggregateMetrics(
        organic=parsed["organic"],
        paid=parsed["paid"],
        featured_snippet=parsed["featured_snippet"],
        local_pack=parsed["local_pack"],
        ai_overview_reference=parsed["ai_overview_reference"],
    )


def _parse_metrics_absolute(
    value: object, path: str, request: RequestContext
) -> AggregateMetricsAbsolute:
    families = _aggregate_families(value, path)
    parsed = {
        name: _parse_metrics_absolute_family(families[name], f"{path}/{name}", request)
        for name in REQUESTED_ITEM_TYPES
    }
    return AggregateMetricsAbsolute(
        organic=parsed["organic"],
        paid=parsed["paid"],
        featured_snippet=parsed["featured_snippet"],
        local_pack=parsed["local_pack"],
        ai_overview_reference=parsed["ai_overview_reference"],
    )


def _aggregate_families(value: object, path: str) -> dict[str, object]:
    """Require exactly the five requested aggregate loci. Missing or sixth fails closed."""

    obj = _object(value, path)
    _reject_unknown(obj, _AGGREGATE_FAMILY_KEYS, path)
    _require_members(obj, _AGGREGATE_FAMILY_KEYS, path)
    return obj


def _parse_metrics_family(
    value: object, path: str, request: RequestContext
) -> MetricsFamily:
    obj = _object(value, path)
    _reject_unknown(obj, _METRICS_FAMILY_KEYS, path)
    _require_members(obj, _METRICS_FAMILY_KEYS, path)
    return MetricsFamily(
        positions=_parse_buckets(obj, path),
        count=_require_nonneg_int(obj.get("count"), f"{path}/count"),
        etv=_optional_decimal(obj, "etv", f"{path}/etv"),
        estimated_paid_traffic_cost=_optional_decimal(
            obj, "estimated_paid_traffic_cost", f"{path}/estimated_paid_traffic_cost"
        ),
        is_new=_require_nonneg_int(obj.get("is_new"), f"{path}/is_new"),
        is_up=_require_nonneg_int(obj.get("is_up"), f"{path}/is_up"),
        is_down=_require_nonneg_int(obj.get("is_down"), f"{path}/is_down"),
        is_lost=_require_nonneg_int(obj.get("is_lost"), f"{path}/is_lost"),
        clickstream_etv=_request_disabled_null(
            obj,
            "clickstream_etv",
            f"{path}/clickstream_etv",
            include_clickstream=request.include_clickstream_data,
        ),
        clickstream_gender_distribution=_request_disabled_null(
            obj,
            "clickstream_gender_distribution",
            f"{path}/clickstream_gender_distribution",
            include_clickstream=request.include_clickstream_data,
        ),
        clickstream_age_distribution=_request_disabled_null(
            obj,
            "clickstream_age_distribution",
            f"{path}/clickstream_age_distribution",
            include_clickstream=request.include_clickstream_data,
        ),
    )


def _parse_metrics_absolute_family(
    value: object, path: str, request: RequestContext
) -> MetricsAbsoluteFamily:
    obj = _object(value, path)
    _reject_unknown(obj, _METRICS_ABSOLUTE_FAMILY_KEYS, path)
    _require_members(obj, _METRICS_ABSOLUTE_FAMILY_KEYS, path)
    return MetricsAbsoluteFamily(
        positions=_parse_buckets(obj, path),
        is_new=_require_nonneg_int(obj.get("is_new"), f"{path}/is_new"),
        is_up=_require_nonneg_int(obj.get("is_up"), f"{path}/is_up"),
        is_down=_require_nonneg_int(obj.get("is_down"), f"{path}/is_down"),
        is_lost=_require_nonneg_int(obj.get("is_lost"), f"{path}/is_lost"),
        clickstream_etv=_request_disabled_null(
            obj,
            "clickstream_etv",
            f"{path}/clickstream_etv",
            include_clickstream=request.include_clickstream_data,
        ),
        clickstream_gender_distribution=_request_disabled_null(
            obj,
            "clickstream_gender_distribution",
            f"{path}/clickstream_gender_distribution",
            include_clickstream=request.include_clickstream_data,
        ),
        clickstream_age_distribution=_request_disabled_null(
            obj,
            "clickstream_age_distribution",
            f"{path}/clickstream_age_distribution",
            include_clickstream=request.include_clickstream_data,
        ),
    )


def _parse_buckets(obj: Mapping[str, object], path: str) -> PositionBuckets:
    values = {
        key: _require_nonneg_int(obj.get(key), f"{path}/{key}")
        for key in _POSITION_BUCKET_KEYS
    }
    return PositionBuckets(
        pos_1=values["pos_1"],
        pos_2_3=values["pos_2_3"],
        pos_4_10=values["pos_4_10"],
        pos_11_20=values["pos_11_20"],
        pos_21_30=values["pos_21_30"],
        pos_31_40=values["pos_31_40"],
        pos_41_50=values["pos_41_50"],
        pos_51_60=values["pos_51_60"],
        pos_61_70=values["pos_61_70"],
        pos_71_80=values["pos_71_80"],
        pos_81_90=values["pos_81_90"],
        pos_91_100=values["pos_91_100"],
    )


def _parse_item(
    value: object, path: str, index: int, request: RequestContext
) -> RankedKeywordsItem:
    item = _object(value, path)
    _reject_unknown(item, _ITEM_KEYS, path)
    _require_members(item, _REQUIRED_ITEM_KEYS, path)
    se_type = _require_str(item.get("se_type"), f"{path}/se_type")
    if se_type != SE_TYPE:
        raise RankedKeywordsParseError(
            "unknown_enum", f"{path}/se_type", "se_type must be google"
        )
    return RankedKeywordsItem(
        provider_array_index=index,
        se_type=se_type,
        keyword_data=_parse_keyword_data_field(
            item, "keyword_data", f"{path}/keyword_data", request
        ),
        ranked_serp_element=_parse_ranked_serp_element(
            item, "ranked_serp_element", f"{path}/ranked_serp_element", request
        ),
    )


def _parse_ranked_serp_element(
    obj: Mapping[str, object], key: str, path: str, request: RequestContext
) -> Field[RankedSerpElement]:
    element = _optional_object(obj, key, path, _RANKED_SERP_ELEMENT_KEYS)
    if element is None:
        return _propagate_state(obj, key)
    if "serp_item" not in element:
        raise RankedKeywordsParseError(
            "missing_field", f"{path}/serp_item", "ranked_serp_element must state serp_item"
        )
    return Field[RankedSerpElement].stated(
        RankedSerpElement(
            # These six members restate `keyword_data.serp_info`. They are parsed here on
            # their own path and never reconciled with it.
            check_url=_optional_str(element, "check_url", f"{path}/check_url"),
            se_results_count=_optional_nonneg_int(
                element, "se_results_count", f"{path}/se_results_count"
            ),
            keyword_difficulty=_optional_nonneg_int(
                element, "keyword_difficulty", f"{path}/keyword_difficulty"
            ),
            is_lost=_optional_bool(element, "is_lost", f"{path}/is_lost"),
            last_updated_time=_optional_timestamp(
                element, "last_updated_time", f"{path}/last_updated_time"
            ),
            previous_updated_time=_optional_timestamp(
                element, "previous_updated_time", f"{path}/previous_updated_time"
            ),
            serp_item_types=_optional_str_tuple(
                element, "serp_item_types", f"{path}/serp_item_types"
            ),
            se_type=_optional_se_type(element, "se_type", f"{path}/se_type"),
            serp_item=_parse_serp_item(
                element.get("serp_item"), f"{path}/serp_item", request
            ),
        )
    )


def _parse_serp_item(value: object, path: str, request: RequestContext) -> SerpItem:
    obj = _object(value, path)
    _reject_unknown(obj, _SERP_ITEM_KEYS, path)
    _require_members(obj, _REQUIRED_SERP_ITEM_KEYS, path)
    return SerpItem(
        se_type=_optional_se_type(obj, "se_type", f"{path}/se_type"),
        # Open provider vocabulary. Organic's closed item-type set is not imported.
        type=_require_str(obj.get("type"), f"{path}/type"),
        # Nonnegative, not positive: rank zero stays a well-typed unproven provider branch.
        rank_group=_require_nonneg_int(obj.get("rank_group"), f"{path}/rank_group"),
        rank_absolute=_require_nonneg_int(
            obj.get("rank_absolute"), f"{path}/rank_absolute"
        ),
        # Layout testimony, never parsed as an integer and never a closed {left,right} set.
        position=_optional_str(obj, "position", f"{path}/position"),
        xpath=_optional_str(obj, "xpath", f"{path}/xpath"),
        domain=_optional_str(obj, "domain", f"{path}/domain"),
        main_domain=_optional_str(obj, "main_domain", f"{path}/main_domain"),
        website_name=_optional_str(obj, "website_name", f"{path}/website_name"),
        relative_url=_optional_str(obj, "relative_url", f"{path}/relative_url"),
        url=_require_serp_url(obj.get("url"), f"{path}/url"),
        breadcrumb=_optional_str(obj, "breadcrumb", f"{path}/breadcrumb"),
        title=_optional_str(obj, "title", f"{path}/title"),
        description=_optional_str(obj, "description", f"{path}/description"),
        # Free provider text including relative prose and date-looking strings. Never a clock.
        pre_snippet=_optional_str(obj, "pre_snippet", f"{path}/pre_snippet"),
        highlighted=_optional_str_tuple(obj, "highlighted", f"{path}/highlighted"),
        is_image=_optional_bool(obj, "is_image", f"{path}/is_image"),
        is_video=_optional_bool(obj, "is_video", f"{path}/is_video"),
        is_featured_snippet=_optional_bool(
            obj, "is_featured_snippet", f"{path}/is_featured_snippet"
        ),
        is_malicious=_optional_bool(obj, "is_malicious", f"{path}/is_malicious"),
        amp_version=_optional_bool(obj, "amp_version", f"{path}/amp_version"),
        etv=_optional_decimal(obj, "etv", f"{path}/etv"),
        estimated_paid_traffic_cost=_optional_decimal(
            obj, "estimated_paid_traffic_cost", f"{path}/estimated_paid_traffic_cost"
        ),
        clickstream_etv=_request_disabled_null(
            obj,
            "clickstream_etv",
            f"{path}/clickstream_etv",
            include_clickstream=request.include_clickstream_data,
        ),
        rank_changes=_parse_rank_changes(obj, "rank_changes", f"{path}/rank_changes"),
        rank_info=_parse_rank_info(obj, "rank_info", f"{path}/rank_info"),
        # RANK-03 observes JSON null only on these five. No Ranked-local non-null contract
        # was learned, so a populated value is a named v1 drift trigger, not silent loss.
        about_this_result=_unsupported_null(
            obj, "about_this_result", f"{path}/about_this_result"
        ),
        backlinks_info=_unsupported_null(obj, "backlinks_info", f"{path}/backlinks_info"),
        extended_snippet=_unsupported_null(
            obj, "extended_snippet", f"{path}/extended_snippet"
        ),
        links=_unsupported_null(obj, "links", f"{path}/links"),
        rating=_unsupported_null(obj, "rating", f"{path}/rating"),
    )


def _require_serp_url(value: object, path: str) -> str:
    """Narrow HTTP(S) syntax check on the one URL that receives one. Never canonicalizing.

    The exact provider string is returned unchanged: scheme case, `www`, path, query,
    fragment, and trailing slash all survive, and the URL host is not required to match
    `domain`, `main_domain`, or the Attempt target.
    """

    text = _require_str(value, path)
    if " " in text:
        raise RankedKeywordsParseError(
            "invalid_url", path, "url must not contain an ASCII space"
        )
    try:
        parts = urlsplit(text)
    except ValueError as exc:
        raise RankedKeywordsParseError("invalid_url", path, "url is not parseable") from exc
    if parts.scheme not in _URL_SCHEMES:
        raise RankedKeywordsParseError("invalid_url", path, "url scheme must be http(s)")
    if not parts.netloc:
        raise RankedKeywordsParseError("invalid_url", path, "url must state a netloc")
    return text


def _parse_rank_changes(
    obj: Mapping[str, object], key: str, path: str
) -> Field[RankChanges]:
    changes = _optional_object(obj, key, path, _RANK_CHANGES_KEYS)
    if changes is None:
        return _propagate_state(obj, key)
    # Movement booleans and previous absolute rank are independent paths. A synthetic
    # is_new/is_up/previous-rank combination the fixture never shows stays parseable.
    return Field[RankChanges].stated(
        RankChanges(
            is_new=_optional_bool(changes, "is_new", f"{path}/is_new"),
            is_up=_optional_bool(changes, "is_up", f"{path}/is_up"),
            is_down=_optional_bool(changes, "is_down", f"{path}/is_down"),
            previous_rank_absolute=_optional_nonneg_int(
                changes, "previous_rank_absolute", f"{path}/previous_rank_absolute"
            ),
        )
    )


def _parse_rank_info(obj: Mapping[str, object], key: str, path: str) -> Field[RankInfo]:
    info = _optional_object(obj, key, path, _RANK_INFO_KEYS)
    if info is None:
        return _propagate_state(obj, key)
    # Separately named nonnegative provider scores. Real fixture zero is valid, and
    # `main_domain_rank` here is not `avg_backlinks_info.main_domain_rank`.
    return Field[RankInfo].stated(
        RankInfo(
            page_rank=_optional_nonneg_int(info, "page_rank", f"{path}/page_rank"),
            main_domain_rank=_optional_nonneg_int(
                info, "main_domain_rank", f"{path}/main_domain_rank"
            ),
        )
    )


def _parse_keyword_data_field(
    obj: Mapping[str, object], key: str, path: str, request: RequestContext
) -> Field[KeywordData]:
    data = _optional_object(obj, key, path, _KEYWORD_DATA_KEYS)
    if data is None:
        return _propagate_state(obj, key)
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
            serp_info=_parse_serp_info(data, f"{path}/serp_info"),
            # Bing normalization is NOT controlled by the clickstream request flag: absent
            # and JSON null stay distinguishable states of their own.
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
            # Current volume is an independent fact; it is never checked against the
            # monthly series, whose newest row disagrees on 81 of 100 fixture rows.
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
        _require_members(row, _MONTHLY_KEYS, point_path)
        year = _require_int(row.get("year"), f"{point_path}/year")
        month = _require_int(row.get("month"), f"{point_path}/month")
        volume = _require_nonneg_int(
            row.get("search_volume"), f"{point_path}/search_volume"
        )
        if year < YEAR_MIN or year > YEAR_MAX:
            raise RankedKeywordsParseError(
                "invalid_period", f"{point_path}/year", "year is outside calendar bounds"
            )
        if month < MONTH_MIN or month > MONTH_MAX:
            raise RankedKeywordsParseError(
                "invalid_period", f"{point_path}/month", "month must be 1..12"
            )
        period = (year, month)
        # A monthly series is keyed Data-Period testimony, not an occurrence list. This
        # fail-closed rule implies nothing about duplicate keyword/URL/rank occurrences.
        if period in seen:
            raise RankedKeywordsParseError(
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
    # No 12-row length, newest-first order, or shared-window equation is imposed.
    return Field[tuple[MonthlySearch, ...]].stated(tuple(points))


def _parse_trend(
    obj: Mapping[str, object], key: str, path: str
) -> Field[SearchVolumeTrend]:
    trend = _optional_object(obj, key, path, _TREND_KEYS)
    if trend is None:
        return _propagate_state(obj, key)
    # Signed integers. Real negative fixture values are preserved, never clamped.
    return Field[SearchVolumeTrend].stated(
        SearchVolumeTrend(
            monthly=_optional_int(trend, "monthly", f"{path}/monthly"),
            quarterly=_optional_int(trend, "quarterly", f"{path}/quarterly"),
            yearly=_optional_int(trend, "yearly", f"{path}/yearly"),
        )
    )


def _parse_properties(obj: Mapping[str, object], path: str) -> Field[KeywordProperties]:
    props = _optional_object(obj, "keyword_properties", path, _PROPERTIES_KEYS)
    if props is None:
        return _propagate_state(obj, "keyword_properties")
    return Field[KeywordProperties].stated(
        KeywordProperties(
            se_type=_optional_se_type(props, "se_type", f"{path}/se_type"),
            # A clustering/reference string, not a canonical keyword foreign key, and
            # independent from the clustering algorithm beside it.
            core_keyword=_optional_str(props, "core_keyword", f"{path}/core_keyword"),
            synonym_clustering_algorithm=_optional_str(
                props,
                "synonym_clustering_algorithm",
                f"{path}/synonym_clustering_algorithm",
            ),
            # This difficulty is not `ranked_serp_element.keyword_difficulty`.
            keyword_difficulty=_optional_nonneg_int(
                props, "keyword_difficulty", f"{path}/keyword_difficulty"
            ),
            # May disagree with the requested English locale without reconciliation.
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
            # Open provider vocabulary.
            main_intent=_optional_str(intent, "main_intent", f"{path}/main_intent"),
            foreign_intent=_optional_str_tuple(
                intent, "foreign_intent", f"{path}/foreign_intent"
            ),
            last_updated_time=_optional_timestamp(
                intent, "last_updated_time", f"{path}/last_updated_time"
            ),
        )
    )


def _parse_serp_info(obj: Mapping[str, object], path: str) -> Field[SerpInfo]:
    serp = _optional_object(obj, "serp_info", path, _SERP_INFO_KEYS)
    if serp is None:
        return _propagate_state(obj, "serp_info")
    return Field[SerpInfo].stated(
        SerpInfo(
            se_type=_optional_se_type(serp, "se_type", f"{path}/se_type"),
            check_url=_optional_str(serp, "check_url", f"{path}/check_url"),
            # Ordered, multiplicity-preserving, open SERP composition. Independent from
            # `serp_item.type`, `is_featured_snippet`, and aggregate family participation.
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
    """Clickstream-controlled loci under the request flag verified from the Attempt."""

    if not include_clickstream:
        if key in obj and obj[key] is not None:
            raise RankedKeywordsParseError(
                "request_disabled_populated",
                path,
                "request-disabled clickstream value must not be populated",
            )
        return Field[None].not_requested()
    return _null_or_absent(obj, key, path)


def _unsupported_null(obj: Mapping[str, object], key: str, path: str) -> Field[None]:
    """Null-only provider children with no empirically learned Ranked-local shape."""

    if key not in obj:
        return Field[None].absent()
    if obj[key] is None:
        return Field[None].json_null()
    raise RankedKeywordsParseError(
        "unsupported_shape", path, "populated value is not supported by this parser"
    )


def _null_or_absent(obj: Mapping[str, object], key: str, path: str) -> Field[None]:
    if key not in obj:
        return Field[None].absent()
    if obj[key] is None:
        return Field[None].json_null()
    raise RankedKeywordsParseError(
        "wrong_type", path, "populated value is not accepted here"
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
        raise RankedKeywordsParseError("unknown_enum", path, "se_type must be google")
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
        raise RankedKeywordsParseError("wrong_type", path, "must be a JSON boolean")
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
    # Ordered integer occurrences. Never sorted, never deduplicated.
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
    """Validate lexical form and calendar reality only; the exact string is preserved."""

    if _PROVIDER_TIME_RE.fullmatch(value) is None:
        raise RankedKeywordsParseError(
            "invalid_timestamp",
            path,
            "provider timestamp is not YYYY-MM-DD HH:MM:SS +00:00",
        )
    year = int(value[:4])
    if year < YEAR_MIN or year > YEAR_MAX:
        raise RankedKeywordsParseError(
            "invalid_timestamp", path, "provider timestamp year is outside calendar bounds"
        )
    try:
        datetime.strptime(value.removesuffix(" +00:00"), _PROVIDER_TIME_FORMAT)
    except ValueError as exc:
        raise RankedKeywordsParseError(
            "invalid_timestamp", path, "provider timestamp is not a real UTC datetime"
        ) from exc


def _exact_int(value: object, expected: int, path: str) -> int:
    number = _require_int(value, path)
    if number != expected:
        raise RankedKeywordsParseError(
            "frozen_parameter", path, f"value must be exactly {expected}"
        )
    return number


def _exact_str(value: object, expected: str, path: str) -> str:
    text = _require_str(value, path)
    if text != expected:
        raise RankedKeywordsParseError(
            "frozen_parameter", path, f"value must be exactly {expected!r}"
        )
    return text


def _exact_bool(value: object, expected: bool, path: str) -> bool:
    if not isinstance(value, bool):
        raise RankedKeywordsParseError("wrong_type", path, "must be a JSON boolean")
    if value is not expected:
        raise RankedKeywordsParseError(
            "frozen_parameter", path, f"value must be exactly {expected}"
        )
    return value


def _string_tuple(value: object, path: str) -> tuple[str, ...]:
    rows = _require_array(value, path)
    return tuple(_require_str(item, f"{path}/{index}") for index, item in enumerate(rows))


def _decode_json(raw: bytes) -> object:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise RankedKeywordsParseError("utf8_bom", "", "UTF-8 BOM is forbidden")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RankedKeywordsParseError(
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
        raise RankedKeywordsParseError(
            "invalid_json", "", "body is not valid JSON"
        ) from exc
    if text[end:].strip() != "":
        raise RankedKeywordsParseError(
            "trailing_data", "", "non-whitespace data follows the JSON document"
        )
    return value


def _reject_constant(value: str) -> None:
    raise RankedKeywordsParseError(
        "non_finite_number", "", f"{value} is not a finite number"
    )


def _object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise RankedKeywordsParseError(
                "duplicate_member", f"/{_escape(key)}", "duplicate object member name"
            )
        result[key] = value
    return result


def _reject_unknown(obj: Mapping[str, object], allowed: frozenset[str], path: str) -> None:
    extra = [key for key in obj if key not in allowed]
    if extra:
        pointer = f"{path}/{_escape(extra[0])}" if path else f"/{_escape(extra[0])}"
        raise RankedKeywordsParseError(
            "unknown_field", pointer, "unknown field on a closed object"
        )


def _require_members(
    obj: Mapping[str, object], required: frozenset[str], path: str
) -> None:
    missing = sorted(key for key in required if key not in obj)
    if missing:
        pointer = f"{path}/{_escape(missing[0])}" if path else f"/{_escape(missing[0])}"
        raise RankedKeywordsParseError(
            "missing_field", pointer, "required member is absent"
        )


def _object(value: object, path: str) -> dict[str, object]:
    if isinstance(value, Mapping) and not isinstance(value, (str, bytes, bytearray)):
        return {str(key): item for key, item in value.items()}
    raise RankedKeywordsParseError("wrong_type", path or "/", "must be an object")


def _require_array(value: object, path: str) -> list[object]:
    if not isinstance(value, list) or isinstance(value, (str, bytes, bytearray)):
        raise RankedKeywordsParseError("wrong_type", path, "must be an array")
    return list(value)


def _require_str(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise RankedKeywordsParseError("wrong_type", path, "must be a string")
    return value


def _require_int(value: object, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RankedKeywordsParseError("wrong_type", path, "must be a JSON integer")
    return value


def _require_nonneg_int(value: object, path: str) -> int:
    number = _require_int(value, path)
    if number < 0:
        raise RankedKeywordsParseError(
            "invalid_number", path, "value must not be negative"
        )
    return number


def _require_decimal(value: object, path: str) -> Decimal:
    if isinstance(value, bool):
        raise RankedKeywordsParseError(
            "wrong_type", path, "must be a decimal-capable number"
        )
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, Decimal):
        return value
    raise RankedKeywordsParseError("wrong_type", path, "must be a decimal-capable number")


def _escape(key: str) -> str:
    return key.replace("~", "~0").replace("/", "~1")
