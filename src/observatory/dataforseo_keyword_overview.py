"""Strict DataForSEO Keyword Overview parser, typed IR, and core recipe."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Final

from observatory.capture_event import PAID_ADAPTER_CONTRACT
from observatory.provider_recipe import (
    IDENTITY_SCHEMA,
    IDENTITY_VERSION,
    SCHEMA,
    SCHEMA_VERSION,
    recipe_bytes,
    recipe_derivation_version_id,
    validate_recipe,
)

PARSER_CONTRACT: Final[str] = (
    "dataforseo-labs-google-keyword-overview-live-paid-probe-parser-v1"
)
PROVIDER: Final[str] = "dataforseo"
COVERAGE_KIND: Final[str] = "dataforseo.google.keyword_overview.coverage.v1"
METRICS_KIND: Final[str] = "dataforseo.google.keyword_overview.metrics.v1"
SUCCESS_STATUS: Final[int] = 20000
YEAR_MIN: Final[int] = 2000
YEAR_MAX: Final[int] = 2100
_PROVIDER_TIME_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} \+00:00$"
)
_SE_TYPE: Final[str] = "google"
_COMPETITION_LEVELS: Final[frozenset[str]] = frozenset({"HIGH", "LOW", "MEDIUM"})
_INTENTS: Final[frozenset[str]] = frozenset(
    {"commercial", "informational", "navigational", "transactional"}
)
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
_RESULT_KEYS: Final[frozenset[str]] = frozenset(
    {"items", "items_count", "language_code", "location_code", "se_type"}
)
_ITEM_KEYS: Final[frozenset[str]] = frozenset(
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
        "search_partners",
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
_TREND_KEYS: Final[frozenset[str]] = frozenset({"monthly", "quarterly", "yearly"})
_MONTHLY_KEYS: Final[frozenset[str]] = frozenset({"month", "search_volume", "year"})

class FieldState(StrEnum):
    STATED = "stated"
    JSON_NULL = "json_null"
    ABSENT = "absent"
    NOT_REQUESTED = "not_requested"
    INAPPLICABLE = "inapplicable"


class ParseClassification(StrEnum):
    ADMITTED = "observation_admitted"
    PROVIDER_ERROR = "provider_error"


class KeywordOverviewParseError(Exception):
    """Strict Keyword Overview parse or reconciliation failed."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        super().__init__(f"{code} at {path}: {message}")


@dataclass(frozen=True)
class Field[T]:
    state: FieldState
    value: T | None = None

    @classmethod
    def stated(cls, value: T) -> Field[T]:
        return cls(FieldState.STATED, value)

    @classmethod
    def json_null(cls) -> Field[T]:
        return cls(FieldState.JSON_NULL)

    @classmethod
    def absent(cls) -> Field[T]:
        return cls(FieldState.ABSENT)

    @classmethod
    def not_requested(cls) -> Field[T]:
        return cls(FieldState.NOT_REQUESTED)


@dataclass(frozen=True)
class ParseDiagnostic:
    code: str
    path: str


@dataclass(frozen=True)
class MonthlySearch:
    year: int
    month: int
    search_volume: int


@dataclass(frozen=True)
class SearchVolumeTrend:
    monthly: Field[int]
    quarterly: Field[int]
    yearly: Field[int]


@dataclass(frozen=True)
class KeywordInfo:
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
    core_keyword: Field[str]
    synonym_clustering_algorithm: Field[str]
    keyword_difficulty: Field[int]
    detected_language: Field[str]
    is_another_language: Field[bool]


@dataclass(frozen=True)
class AvgBacklinksInfo:
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
    main_intent: Field[str]
    foreign_intent: Field[tuple[str, ...]]
    last_updated_time: Field[str]


@dataclass(frozen=True)
class ReconciledKeyword:
    requested_keyword: str
    returned_keyword: Field[str]
    covered: bool
    location_code: Field[int]
    language_code: Field[str]
    search_partners: Field[bool]
    keyword_info: Field[KeywordInfo]
    keyword_properties: Field[KeywordProperties]
    avg_backlinks_info: Field[AvgBacklinksInfo]
    search_intent_info: Field[SearchIntentInfo]
    keyword_info_normalized_with_bing: Field[None]
    keyword_info_normalized_with_clickstream: Field[None]
    clickstream_keyword_info: Field[None]
    serp_info: Field[None]


@dataclass(frozen=True)
class _ParsedItem:
    keyword: str
    location_code: Field[int]
    language_code: Field[str]
    search_partners: Field[bool]
    keyword_info: Field[KeywordInfo]
    keyword_properties: Field[KeywordProperties]
    avg_backlinks_info: Field[AvgBacklinksInfo]
    search_intent_info: Field[SearchIntentInfo]
    keyword_info_normalized_with_bing: Field[None]
    keyword_info_normalized_with_clickstream: Field[None]
    clickstream_keyword_info: Field[None]
    serp_info: Field[None]


@dataclass(frozen=True)
class KeywordOverviewIR:
    outcome: ParseClassification
    requested_keywords: tuple[str, ...]
    location_code: int
    language_code: str
    include_serp_info: bool
    include_clickstream_data: bool
    items: tuple[ReconciledKeyword, ...]
    diagnostics: tuple[ParseDiagnostic, ...]
    status_code: Field[int]
    task_status_code: Field[int]
    execution_time: Field[str]
    task_execution_time: Field[str]
    cost: Field[Decimal]


def normalize_keyword(value: str) -> str:
    """Recipe normalization used only for request/result matching."""

    return " ".join(value.casefold().split())


def parse_keyword_overview(
    body: bytes,
    parameters: Mapping[str, object],
) -> KeywordOverviewIR:
    """Parse exact Keyword Overview body bytes against verified Attempt parameters."""

    requested = _requested_keywords(parameters)
    location = _require_int(parameters.get("location_code"), "/attempt/location_code")
    language = _require_str(parameters.get("language_code"), "/attempt/language_code")
    include_serp = _require_bool(parameters.get("include_serp_info"), "/attempt/include_serp_info")
    include_clickstream = _require_bool(
        parameters.get("include_clickstream_data"),
        "/attempt/include_clickstream_data",
    )
    document = _decode_json(body)
    root = _object(document, "")
    diagnostics: list[ParseDiagnostic] = []
    _collect_unknown(root, _ROOT_KEYS, "", diagnostics)
    status = _require_stated_int(root, "status_code", "/status_code")
    task_list = _require_array(root.get("tasks"), "/tasks")
    tasks_count = _require_stated_int(root, "tasks_count", "/tasks_count")
    if tasks_count.value != len(task_list):
        raise KeywordOverviewParseError(
            "count_mismatch", "/tasks_count", "tasks_count does not match tasks length"
        )
    _require_stated_int(root, "tasks_error", "/tasks_error")
    if len(task_list) != 1:
        raise KeywordOverviewParseError("tasks_length", "/tasks", "exactly one task is required")
    task = _object(task_list[0], "/tasks/0")
    _collect_unknown(task, _TASK_KEYS, "/tasks/0", diagnostics)
    task_status = _require_stated_int(task, "status_code", "/tasks/0/status_code")
    if status.value == SUCCESS_STATUS and task_status.value != SUCCESS_STATUS:
        return KeywordOverviewIR(
            outcome=ParseClassification.PROVIDER_ERROR,
            requested_keywords=requested,
            location_code=location,
            language_code=language,
            include_serp_info=include_serp,
            include_clickstream_data=include_clickstream,
            items=(),
            diagnostics=tuple(diagnostics),
            status_code=status,
            task_status_code=task_status,
            execution_time=_optional_duration(root, "time", "/time"),
            task_execution_time=_optional_duration(task, "time", "/tasks/0/time"),
            cost=_optional_decimal(root, "cost", "/cost"),
        )
    if status.value != SUCCESS_STATUS and task_status.value == SUCCESS_STATUS:
        raise KeywordOverviewParseError(
            "inconsistent_status",
            "/status_code",
            "top-level and task status are inconsistent",
        )
    if status.value != SUCCESS_STATUS:
        return KeywordOverviewIR(
            outcome=ParseClassification.PROVIDER_ERROR,
            requested_keywords=requested,
            location_code=location,
            language_code=language,
            include_serp_info=include_serp,
            include_clickstream_data=include_clickstream,
            items=(),
            diagnostics=tuple(diagnostics),
            status_code=status,
            task_status_code=task_status,
            execution_time=_optional_duration(root, "time", "/time"),
            task_execution_time=_optional_duration(task, "time", "/tasks/0/time"),
            cost=_optional_decimal(root, "cost", "/cost"),
        )
    result_value = task.get("result")
    result_list = _require_array(result_value, "/tasks/0/result")
    result_count = _require_stated_int(task, "result_count", "/tasks/0/result_count")
    if result_count.value != len(result_list):
        raise KeywordOverviewParseError(
            "count_mismatch",
            "/tasks/0/result_count",
            "result_count does not match result length",
        )
    if len(result_list) != 1:
        raise KeywordOverviewParseError(
            "result_length", "/tasks/0/result", "exactly one result is required"
        )
    result = _object(result_list[0], "/tasks/0/result/0")
    _collect_unknown(result, _RESULT_KEYS, "/tasks/0/result/0", diagnostics)
    _require_se_type(result.get("se_type"), "/tasks/0/result/0/se_type")
    items_value = result.get("items")
    if "items" not in result:
        raise KeywordOverviewParseError("missing_field", "/tasks/0/result/0/items", "items missing")
    if items_value is None:
        raise KeywordOverviewParseError(
            "wrong_type", "/tasks/0/result/0/items", "items must not be JSON null"
        )
    items_list = _require_array(items_value, "/tasks/0/result/0/items")
    items_count = _require_stated_int(result, "items_count", "/tasks/0/result/0/items_count")
    if items_count.value != len(items_list):
        raise KeywordOverviewParseError(
            "count_mismatch",
            "/tasks/0/result/0/items_count",
            "items_count does not match items length",
        )
    parsed_items = [
        _parse_item(
            item,
            f"/tasks/0/result/0/items/{index}",
            include_serp=include_serp,
            include_clickstream=include_clickstream,
            diagnostics=diagnostics,
        )
        for index, item in enumerate(items_list)
    ]
    reconciled = _reconcile(
        requested,
        parsed_items,
        include_serp=include_serp,
        include_clickstream=include_clickstream,
    )
    return KeywordOverviewIR(
        outcome=ParseClassification.ADMITTED,
        requested_keywords=requested,
        location_code=location,
        language_code=language,
        include_serp_info=include_serp,
        include_clickstream_data=include_clickstream,
        items=reconciled,
        diagnostics=tuple(diagnostics),
        status_code=status,
        task_status_code=task_status,
        execution_time=_optional_duration(root, "time", "/time"),
        task_execution_time=_optional_duration(task, "time", "/tasks/0/time"),
        cost=_optional_decimal(root, "cost", "/cost"),
    )


def keyword_overview_core_recipe() -> dict[str, object]:
    """Return the production Keyword Overview core recipe document."""

    return validate_recipe(
        {
            "adapter_contract": PAID_ADAPTER_CONTRACT,
            "admission": {
                "capture_outcomes": [
                    "no_response",
                    "observation_admitted",
                    "observation_admitted_empty",
                    "provider_envelope_rejected",
                    "provider_error",
                    "reconciliation_failed",
                    "response_partial",
                    "transport_complete_non_admissible",
                ],
                "rule": "recipe_closed_classifications",
            },
            "data_period": {
                "inheritance": "never_from_capture",
                "rule": "provider_stated_year_month_2000_2100",
            },
            "extension_policy": {
                "closed_objects": ["/monthly_search_point", "/search_volume_trend"],
                "extension_permitted_objects": [
                    "/",
                    "/avg_backlinks_info",
                    "/items",
                    "/keyword_info",
                    "/keyword_properties",
                    "/result",
                    "/search_intent_info",
                    "/tasks",
                ],
                "unknown_closed_field": "fail_closed",
                "unknown_extension_field": "diagnostic",
            },
            "field_state": {
                "states": [
                    "absent",
                    "inapplicable",
                    "json_null",
                    "not_requested",
                    "stated",
                ]
            },
            "numeric": {"normalization": "exact_decimal"},
            "observation_identity": {
                "document_schema": IDENTITY_SCHEMA,
                "document_version": IDENTITY_VERSION,
                "kinds": [
                    {
                        "axes": {"requested_keyword": "string"},
                        "observation_kind": COVERAGE_KIND,
                    },
                    {
                        "axes": {"requested_keyword": "string"},
                        "observation_kind": METRICS_KIND,
                    },
                ],
            },
            "observation_kinds": [COVERAGE_KIND, METRICS_KIND],
            "parser_contract": PARSER_CONTRACT,
            "provider": PROVIDER,
            "provider_update_time": {
                "inheritance": "never_from_capture_or_sibling",
                "rule": "structure_stated_or_unstated",
            },
            "reconciliation": {"rule": "exact_requested_subject_normalized"},
            "schema": SCHEMA,
            "version": SCHEMA_VERSION,
        }
    )


CORE_RECIPE: Final[dict[str, object]] = keyword_overview_core_recipe()
CORE_RECIPE_BYTES: Final[bytes] = recipe_bytes(CORE_RECIPE)
CORE_RECIPE_ID: Final[str] = recipe_derivation_version_id(CORE_RECIPE)


def _decode_json(raw: bytes) -> object:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise KeywordOverviewParseError("utf8_bom", "", "UTF-8 BOM is forbidden")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise KeywordOverviewParseError("invalid_utf8", "", "body is not strict UTF-8") from exc
    decoder = json.JSONDecoder(
        parse_int=int,
        parse_float=Decimal,
        parse_constant=_reject_constant,
        object_pairs_hook=_object_pairs,
    )
    try:
        value, end = decoder.raw_decode(text)
    except json.JSONDecodeError as exc:
        raise KeywordOverviewParseError("invalid_json", "", "body is not valid JSON") from exc
    if text[end:].strip() != "":
        raise KeywordOverviewParseError(
            "trailing_data", "", "non-whitespace data follows the JSON document"
        )
    return value


def _reject_constant(value: str) -> None:
    raise KeywordOverviewParseError("non_finite_number", "", f"{value} is not a finite number")


def _object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise KeywordOverviewParseError(
                "duplicate_member", f"/{_escape(key)}", "duplicate object member name"
            )
        result[key] = value
    return result


def _parse_item(
    value: object,
    path: str,
    *,
    include_serp: bool,
    include_clickstream: bool,
    diagnostics: list[ParseDiagnostic],
) -> _ParsedItem:
    item = _object(value, path)
    _collect_unknown(item, _ITEM_KEYS, path, diagnostics)
    _require_se_type(item.get("se_type"), f"{path}/se_type")
    return _ParsedItem(
        keyword=_require_str(item.get("keyword"), f"{path}/keyword"),
        location_code=_optional_int(item, "location_code", f"{path}/location_code"),
        language_code=_optional_str(item, "language_code", f"{path}/language_code"),
        search_partners=_optional_bool(item, "search_partners", f"{path}/search_partners"),
        keyword_info=_parse_keyword_info(
            item.get("keyword_info"), f"{path}/keyword_info", diagnostics
        )
        if "keyword_info" in item
        else Field[KeywordInfo].absent(),
        keyword_properties=_parse_properties(
            item.get("keyword_properties"), f"{path}/keyword_properties", diagnostics
        )
        if "keyword_properties" in item
        else Field[KeywordProperties].absent(),
        avg_backlinks_info=_parse_backlinks(
            item.get("avg_backlinks_info"), f"{path}/avg_backlinks_info", diagnostics
        )
        if "avg_backlinks_info" in item
        else Field[AvgBacklinksInfo].absent(),
        search_intent_info=_parse_intent(
            item.get("search_intent_info"), f"{path}/search_intent_info", diagnostics
        )
        if "search_intent_info" in item
        else Field[SearchIntentInfo].absent(),
        keyword_info_normalized_with_bing=_null_or_absent(
            item, "keyword_info_normalized_with_bing", f"{path}/keyword_info_normalized_with_bing"
        ),
        keyword_info_normalized_with_clickstream=_disabled_or_null(
            item,
            "keyword_info_normalized_with_clickstream",
            f"{path}/keyword_info_normalized_with_clickstream",
            disabled=include_clickstream is False,
        ),
        clickstream_keyword_info=_disabled_or_null(
            item,
            "clickstream_keyword_info",
            f"{path}/clickstream_keyword_info",
            disabled=include_clickstream is False,
        ),
        serp_info=_disabled_or_null(
            item, "serp_info", f"{path}/serp_info", disabled=include_serp is False
        ),
    )


def _parse_keyword_info(
    value: object, path: str, diagnostics: list[ParseDiagnostic]
) -> Field[KeywordInfo]:
    if value is None:
        return Field[KeywordInfo].json_null()
    obj = _object(value, path)
    _collect_unknown(obj, _KEYWORD_INFO_KEYS, path, diagnostics)
    _optional_se_type(obj.get("se_type"), f"{path}/se_type")
    monthly = _parse_monthly(obj, "monthly_searches", f"{path}/monthly_searches")
    trend = _parse_trend(obj, "search_volume_trend", f"{path}/search_volume_trend")
    return Field[KeywordInfo].stated(
        KeywordInfo(
            last_updated_time=_optional_timestamp(
                obj, "last_updated_time", f"{path}/last_updated_time"
            ),
            competition=_optional_decimal(obj, "competition", f"{path}/competition"),
            competition_level=_optional_enum(
                obj, "competition_level", f"{path}/competition_level", _COMPETITION_LEVELS
            ),
            cpc=_optional_decimal(obj, "cpc", f"{path}/cpc"),
            search_volume=_optional_int(obj, "search_volume", f"{path}/search_volume"),
            low_top_of_page_bid=_optional_decimal(
                obj, "low_top_of_page_bid", f"{path}/low_top_of_page_bid"
            ),
            high_top_of_page_bid=_optional_decimal(
                obj, "high_top_of_page_bid", f"{path}/high_top_of_page_bid"
            ),
            categories=_optional_int_tuple(obj, "categories", f"{path}/categories"),
            monthly_searches=monthly,
            search_volume_trend=trend,
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
        obj = _object(item, point_path)
        extra = [key for key in obj if key not in _MONTHLY_KEYS]
        if extra:
            raise KeywordOverviewParseError(
                "unknown_field",
                f"{point_path}/{extra[0]}",
                "unknown field on closed monthly_search_point",
            )
        year = _require_int(obj.get("year"), f"{point_path}/year")
        month = _require_int(obj.get("month"), f"{point_path}/month")
        volume = _require_int(obj.get("search_volume"), f"{point_path}/search_volume")
        if year < YEAR_MIN or year > YEAR_MAX:
            raise KeywordOverviewParseError(
                "invalid_period", f"{point_path}/year", "year is outside recipe bounds"
            )
        if month < 1 or month > 12:
            raise KeywordOverviewParseError(
                "invalid_period", f"{point_path}/month", "month must be 1..12"
            )
        if volume < 0:
            raise KeywordOverviewParseError(
                "invalid_number",
                f"{point_path}/search_volume",
                "monthly search volume must not be negative",
            )
        period = (year, month)
        if period in seen:
            raise KeywordOverviewParseError(
                "duplicate_period", point_path, "duplicate historical year/month"
            )
        seen.add(period)
        points.append(MonthlySearch(year=year, month=month, search_volume=volume))
    return Field[tuple[MonthlySearch, ...]].stated(tuple(points))


def _parse_trend(obj: Mapping[str, object], key: str, path: str) -> Field[SearchVolumeTrend]:
    if key not in obj:
        return Field[SearchVolumeTrend].absent()
    value = obj[key]
    if value is None:
        return Field[SearchVolumeTrend].json_null()
    trend_obj = _object(value, path)
    extra = [name for name in trend_obj if name not in _TREND_KEYS]
    if extra:
        raise KeywordOverviewParseError(
            "unknown_field", f"{path}/{extra[0]}", "unknown field on closed search_volume_trend"
        )
    return Field[SearchVolumeTrend].stated(
        SearchVolumeTrend(
            monthly=_optional_int(trend_obj, "monthly", f"{path}/monthly"),
            quarterly=_optional_int(trend_obj, "quarterly", f"{path}/quarterly"),
            yearly=_optional_int(trend_obj, "yearly", f"{path}/yearly"),
        )
    )


def _parse_properties(
    value: object, path: str, diagnostics: list[ParseDiagnostic]
) -> Field[KeywordProperties]:
    if value is None:
        return Field[KeywordProperties].json_null()
    obj = _object(value, path)
    _collect_unknown(obj, _PROPERTIES_KEYS, path, diagnostics)
    _optional_se_type(obj.get("se_type"), f"{path}/se_type")
    return Field[KeywordProperties].stated(
        KeywordProperties(
            core_keyword=_optional_str(obj, "core_keyword", f"{path}/core_keyword"),
            synonym_clustering_algorithm=_optional_str(
                obj,
                "synonym_clustering_algorithm",
                f"{path}/synonym_clustering_algorithm",
            ),
            keyword_difficulty=_optional_int(
                obj, "keyword_difficulty", f"{path}/keyword_difficulty"
            ),
            detected_language=_optional_str(
                obj, "detected_language", f"{path}/detected_language"
            ),
            is_another_language=_optional_bool(
                obj, "is_another_language", f"{path}/is_another_language"
            ),
        )
    )


def _parse_backlinks(
    value: object, path: str, diagnostics: list[ParseDiagnostic]
) -> Field[AvgBacklinksInfo]:
    if value is None:
        return Field[AvgBacklinksInfo].json_null()
    obj = _object(value, path)
    _collect_unknown(obj, _BACKLINKS_KEYS, path, diagnostics)
    _optional_se_type(obj.get("se_type"), f"{path}/se_type")
    return Field[AvgBacklinksInfo].stated(
        AvgBacklinksInfo(
            backlinks=_optional_decimal(obj, "backlinks", f"{path}/backlinks"),
            dofollow=_optional_decimal(obj, "dofollow", f"{path}/dofollow"),
            referring_pages=_optional_decimal(obj, "referring_pages", f"{path}/referring_pages"),
            referring_domains=_optional_decimal(
                obj, "referring_domains", f"{path}/referring_domains"
            ),
            referring_main_domains=_optional_decimal(
                obj, "referring_main_domains", f"{path}/referring_main_domains"
            ),
            rank=_optional_decimal(obj, "rank", f"{path}/rank"),
            main_domain_rank=_optional_decimal(
                obj, "main_domain_rank", f"{path}/main_domain_rank"
            ),
            last_updated_time=_optional_timestamp(
                obj, "last_updated_time", f"{path}/last_updated_time"
            ),
        )
    )


def _parse_intent(
    value: object, path: str, diagnostics: list[ParseDiagnostic]
) -> Field[SearchIntentInfo]:
    if value is None:
        return Field[SearchIntentInfo].json_null()
    obj = _object(value, path)
    _collect_unknown(obj, _INTENT_KEYS, path, diagnostics)
    _optional_se_type(obj.get("se_type"), f"{path}/se_type")
    return Field[SearchIntentInfo].stated(
        SearchIntentInfo(
            main_intent=_optional_enum(obj, "main_intent", f"{path}/main_intent", _INTENTS),
            foreign_intent=_optional_intent_list(obj, "foreign_intent", f"{path}/foreign_intent"),
            last_updated_time=_optional_timestamp(
                obj, "last_updated_time", f"{path}/last_updated_time"
            ),
        )
    )


def _reconcile(
    requested: tuple[str, ...],
    items: list[_ParsedItem],
    *,
    include_serp: bool,
    include_clickstream: bool,
) -> tuple[ReconciledKeyword, ...]:
    by_key: dict[str, _ParsedItem] = {}
    for item in items:
        key = normalize_keyword(item.keyword)
        if key in by_key:
            raise KeywordOverviewParseError(
                "reconciliation_failed",
                "/tasks/0/result/0/items",
                "duplicate returned keyword item",
            )
        by_key[key] = item
    requested_keys: dict[str, list[str]] = {}
    for keyword in requested:
        requested_keys.setdefault(normalize_keyword(keyword), []).append(keyword)
    for key, group in requested_keys.items():
        if len(group) > 1 and key in by_key:
            raise KeywordOverviewParseError(
                "reconciliation_failed",
                "/attempt/keywords",
                "ambiguous normalized keyword collision",
            )
    for key in by_key:
        if key not in requested_keys:
            raise KeywordOverviewParseError(
                "reconciliation_failed",
                "/tasks/0/result/0/items",
                "unrequested returned keyword item",
            )
    reconciled: list[ReconciledKeyword] = []
    for keyword in requested:
        matched = by_key.get(normalize_keyword(keyword))
        if matched is None:
            reconciled.append(
                ReconciledKeyword(
                    requested_keyword=keyword,
                    returned_keyword=Field[str].absent(),
                    covered=False,
                    location_code=Field[int].absent(),
                    language_code=Field[str].absent(),
                    search_partners=Field[bool].absent(),
                    keyword_info=Field[KeywordInfo].absent(),
                    keyword_properties=Field[KeywordProperties].absent(),
                    avg_backlinks_info=Field[AvgBacklinksInfo].absent(),
                    search_intent_info=Field[SearchIntentInfo].absent(),
                    keyword_info_normalized_with_bing=Field[None].absent(),
                    keyword_info_normalized_with_clickstream=(
                        Field[None].not_requested()
                        if include_clickstream is False
                        else Field[None].absent()
                    ),
                    clickstream_keyword_info=(
                        Field[None].not_requested()
                        if include_clickstream is False
                        else Field[None].absent()
                    ),
                    serp_info=(
                        Field[None].not_requested()
                        if include_serp is False
                        else Field[None].absent()
                    ),
                )
            )
            continue
        reconciled.append(
            ReconciledKeyword(
                requested_keyword=keyword,
                returned_keyword=Field[str].stated(matched.keyword),
                covered=True,
                location_code=matched.location_code,
                language_code=matched.language_code,
                search_partners=matched.search_partners,
                keyword_info=matched.keyword_info,
                keyword_properties=matched.keyword_properties,
                avg_backlinks_info=matched.avg_backlinks_info,
                search_intent_info=matched.search_intent_info,
                keyword_info_normalized_with_bing=matched.keyword_info_normalized_with_bing,
                keyword_info_normalized_with_clickstream=(
                    matched.keyword_info_normalized_with_clickstream
                ),
                clickstream_keyword_info=matched.clickstream_keyword_info,
                serp_info=matched.serp_info,
            )
        )
    return tuple(reconciled)


def _requested_keywords(parameters: Mapping[str, object]) -> tuple[str, ...]:
    value = parameters.get("keywords")
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise KeywordOverviewParseError(
            "wrong_type", "/attempt/keywords", "keywords must be an array"
        )
    keywords = [
        _require_str(item, f"/attempt/keywords/{index}") for index, item in enumerate(value)
    ]
    if not keywords:
        raise KeywordOverviewParseError(
            "missing_field", "/attempt/keywords", "keywords must not be empty"
        )
    return tuple(keywords)


def _collect_unknown(
    obj: Mapping[str, object],
    allowed: frozenset[str],
    path: str,
    diagnostics: list[ParseDiagnostic],
) -> None:
    for key in obj:
        if key not in allowed:
            pointer = f"{path}/{_escape(key)}" if path else f"/{_escape(key)}"
            diagnostics.append(ParseDiagnostic(code="unknown_extension_field", path=pointer))


def _object(value: object, path: str) -> dict[str, object]:
    if isinstance(value, Mapping) and not isinstance(value, (str, bytes, bytearray)):
        return {str(key): item for key, item in value.items()}
    raise KeywordOverviewParseError("wrong_type", path or "/", "must be an object")


def _require_array(value: object, path: str) -> list[object]:
    if not isinstance(value, list) or isinstance(value, (str, bytes, bytearray)):
        raise KeywordOverviewParseError("wrong_type", path, "must be an array")
    return list(value)


def _require_str(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise KeywordOverviewParseError("wrong_type", path, "must be a string")
    return value


def _require_int(value: object, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise KeywordOverviewParseError("wrong_type", path, "must be a JSON integer")
    return value


def _require_stated_int(obj: Mapping[str, object], key: str, path: str) -> Field[int]:
    if key not in obj:
        raise KeywordOverviewParseError("missing_field", path, f"{key} is required")
    value = obj[key]
    if value is None:
        raise KeywordOverviewParseError("missing_field", path, f"{key} must not be JSON null")
    return Field[int].stated(_require_int(value, path))


def _require_bool(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise KeywordOverviewParseError("wrong_type", path, "must be a JSON boolean")
    return value


def _optional_int(obj: Mapping[str, object], key: str, path: str) -> Field[int]:
    if key not in obj:
        return Field[int].absent()
    value = obj[key]
    if value is None:
        return Field[int].json_null()
    return Field[int].stated(_require_int(value, path))


def _optional_str(obj: Mapping[str, object], key: str, path: str) -> Field[str]:
    if key not in obj:
        return Field[str].absent()
    value = obj[key]
    if value is None:
        return Field[str].json_null()
    return Field[str].stated(_require_str(value, path))


def _optional_bool(obj: Mapping[str, object], key: str, path: str) -> Field[bool]:
    if key not in obj:
        return Field[bool].absent()
    value = obj[key]
    if value is None:
        return Field[bool].json_null()
    return Field[bool].stated(_require_bool(value, path))


def _optional_decimal(obj: Mapping[str, object], key: str, path: str) -> Field[Decimal]:
    if key not in obj:
        return Field[Decimal].absent()
    value = obj[key]
    if value is None:
        return Field[Decimal].json_null()
    if isinstance(value, bool):
        raise KeywordOverviewParseError("wrong_type", path, "must be a decimal-capable number")
    if isinstance(value, int):
        return Field[Decimal].stated(Decimal(value))
    if isinstance(value, Decimal):
        return Field[Decimal].stated(value)
    raise KeywordOverviewParseError("wrong_type", path, "must be a decimal-capable number")


def _optional_int_tuple(obj: Mapping[str, object], key: str, path: str) -> Field[tuple[int, ...]]:
    if key not in obj:
        return Field[tuple[int, ...]].absent()
    value = obj[key]
    if value is None:
        return Field[tuple[int, ...]].json_null()
    items = _require_array(value, path)
    return Field[tuple[int, ...]].stated(
        tuple(_require_int(item, f"{path}/{index}") for index, item in enumerate(items))
    )


def _optional_enum(
    obj: Mapping[str, object], key: str, path: str, allowed: frozenset[str]
) -> Field[str]:
    field = _optional_str(obj, key, path)
    if field.state is FieldState.STATED and field.value not in allowed:
        raise KeywordOverviewParseError("unknown_enum", path, "closed enum value is not permitted")
    return field


def _optional_intent_list(
    obj: Mapping[str, object], key: str, path: str
) -> Field[tuple[str, ...]]:
    if key not in obj:
        return Field[tuple[str, ...]].absent()
    value = obj[key]
    if value is None:
        return Field[tuple[str, ...]].json_null()
    if isinstance(value, str):
        raise KeywordOverviewParseError(
            "wrong_type", path, "foreign_intent must be an array or JSON null"
        )
    items = _require_array(value, path)
    intents: list[str] = []
    for index, item in enumerate(items):
        text = _require_str(item, f"{path}/{index}")
        if text not in _INTENTS:
            raise KeywordOverviewParseError(
                "unknown_enum", f"{path}/{index}", "closed enum value is not permitted"
            )
        intents.append(text)
    return Field[tuple[str, ...]].stated(tuple(intents))


def _optional_timestamp(obj: Mapping[str, object], key: str, path: str) -> Field[str]:
    field = _optional_str(obj, key, path)
    if field.state is FieldState.STATED:
        assert field.value is not None
        _require_provider_timestamp(field.value, path)
    return field


def _require_provider_timestamp(value: str, path: str) -> None:
    if _PROVIDER_TIME_RE.fullmatch(value) is None:
        raise KeywordOverviewParseError(
            "invalid_timestamp", path, "provider timestamp is malformed"
        )
    if not value.endswith(" +00:00"):
        raise KeywordOverviewParseError(
            "invalid_timestamp", path, "provider timestamp must be exact UTC +00:00"
        )
    try:
        datetime.strptime(value.removesuffix(" +00:00"), "%Y-%m-%d %H:%M:%S")
    except ValueError as exc:
        raise KeywordOverviewParseError(
            "invalid_timestamp", path, "provider timestamp is not a real UTC datetime"
        ) from exc


def _optional_duration(obj: Mapping[str, object], key: str, path: str) -> Field[str]:
    return _optional_str(obj, key, path)


def _optional_se_type(value: object, path: str) -> None:
    if value is None:
        return
    text = _require_str(value, path)
    if text != _SE_TYPE:
        raise KeywordOverviewParseError("unknown_enum", path, "se_type must be google")


def _require_se_type(value: object, path: str) -> None:
    text = _require_str(value, path)
    if text != _SE_TYPE:
        raise KeywordOverviewParseError("unknown_enum", path, "se_type must be google")


def _null_or_absent(obj: Mapping[str, object], key: str, path: str) -> Field[None]:
    if key not in obj:
        return Field[None].absent()
    if obj[key] is None:
        return Field[None].json_null()
    raise KeywordOverviewParseError("wrong_type", path, "populated object is not accepted here")


def _disabled_or_null(
    obj: Mapping[str, object], key: str, path: str, *, disabled: bool
) -> Field[None]:
    if disabled:
        if key in obj and obj[key] is not None:
            raise KeywordOverviewParseError(
                "request_disabled_populated",
                path,
                "request-disabled enrichment must not be populated",
            )
        return Field[None].not_requested()
    return _null_or_absent(obj, key, path)


def _escape(part: str) -> str:
    return part.replace("~", "~0").replace("/", "~1")
