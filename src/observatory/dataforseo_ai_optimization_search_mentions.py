"""Strict DataForSEO Search Mentions parser and typed in-memory IR."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Final
from urllib.parse import urlparse

from observatory.capture_event import MENTIONS_ADAPTER_CONTRACT
from observatory.dataforseo_keyword_overview import Field, ParseClassification
from observatory.provider_recipe import (
    IDENTITY_SCHEMA,
    IDENTITY_VERSION,
    SCHEMA,
    SCHEMA_VERSION,
    recipe_bytes,
    recipe_derivation_version_id,
    validate_recipe,
)

SUCCESS_STATUS: Final[int] = 20000
YEAR_MIN: Final[int] = 1
YEAR_MAX: Final[int] = 9999
PROVIDER: Final[str] = "dataforseo"
PARSER_CONTRACT: Final[str] = (
    "dataforseo-ai-optimization-search-mentions-live-parser-v1"
)
ITEM_KIND: Final[str] = "dataforseo.google.ai_optimization.search_mentions.item.v1"
MONTHLY_KIND: Final[str] = (
    "dataforseo.google.ai_optimization.search_mentions.monthly_search_volume.v1"
)
SOURCE_KIND: Final[str] = "dataforseo.google.ai_optimization.search_mentions.source.v1"
_PROVIDER_TIME_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} \+00:00$"
)
_PROVIDER_TIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S +00:00"

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
        "language_code",
        "limit",
        "location_code",
        "offset",
        "platform",
        "target",
    }
)
_ECHO_TARGET_KEYS: Final[frozenset[str]] = frozenset(
    {"keyword", "match_type", "search_filter", "search_scope"}
)
_RESULT_KEYS: Final[frozenset[str]] = frozenset(
    {"items", "items_count", "offset", "search_after_token", "total_count"}
)
_ITEM_KEYS: Final[frozenset[str]] = frozenset(
    {
        "ai_search_volume",
        "answer",
        "brand_entities",
        "fan_out_queries",
        "first_response_at",
        "is_web_search_based",
        "language_code",
        "last_response_at",
        "location_code",
        "model_name",
        "monthly_searches",
        "platform",
        "question",
        "search_results",
        "sources",
    }
)
_SOURCE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "domain",
        "markdown",
        "publication_date",
        "rank",
        "snippet",
        "source_name",
        "thumbnail",
        "title",
        "url",
    }
)
_MONTHLY_KEYS: Final[frozenset[str]] = frozenset({"month", "search_volume", "year"})
_PARAMETER_KEYS: Final[frozenset[str]] = frozenset(
    {
        "contract",
        "language_code",
        "limit",
        "location_code",
        "offset",
        "platform",
        "target",
    }
)
_GOOGLE_NULL_ITEM_FIELDS: Final[tuple[str, ...]] = (
    "search_results",
    "brand_entities",
    "fan_out_queries",
)


class SearchMentionsParseError(Exception):
    """Strict Search Mentions parse or reconciliation failed."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        super().__init__(f"{code} at {path}: {message}")


@dataclass(frozen=True)
class RequestContext:
    keyword: str
    match_type: str
    search_filter: str
    search_scope: tuple[str, ...]
    platform: str
    location_code: int
    language_code: str
    limit: int
    offset: int


@dataclass(frozen=True)
class EchoTarget:
    keyword: str
    match_type: str
    search_filter: str
    search_scope: tuple[str, ...]


@dataclass(frozen=True)
class ProviderEcho:
    api: str
    function: str
    language_code: str
    limit: int
    location_code: int
    offset: int
    platform: str
    target: tuple[EchoTarget, ...]


@dataclass(frozen=True)
class MonthlyPoint:
    year: int
    month: int
    search_volume: int


@dataclass(frozen=True)
class SourceOccurrence:
    rank: int
    title: str
    url: str
    domain: str
    source_name: str
    snippet: str
    publication_date: Field[str]
    thumbnail: Field[str]
    markdown: Field[str]


@dataclass(frozen=True)
class ItemOccurrence:
    platform: str
    model_name: str
    location_code: int
    language_code: str
    question: str
    answer: str
    ai_search_volume: int
    is_web_search_based: bool
    first_response_at: str
    last_response_at: str
    search_results: Field[object]
    brand_entities: Field[object]
    fan_out_queries: Field[object]
    monthly_searches: tuple[MonthlyPoint, ...]
    sources: tuple[SourceOccurrence, ...]


@dataclass(frozen=True)
class SearchMentionsIR:
    outcome: ParseClassification
    request: RequestContext
    echo: ProviderEcho | None
    version: str
    status_code: int
    status_message: str
    duration: str
    cost: Decimal
    tasks_count: int
    tasks_error: int
    task_id: str | None
    task_status_code: int | None
    task_status_message: str | None
    task_duration: str | None
    task_cost: Decimal | None
    task_path: tuple[str, ...] | None
    result_count: int | None
    total_count: int | None
    offset: int | None
    items_count: int | None
    search_after_token: Field[str] | None
    items: tuple[ItemOccurrence, ...]


def parse_search_mentions(
    body: bytes, parameters: Mapping[str, object]
) -> SearchMentionsIR:
    """Parse Search Mentions body bytes against verified Attempt parameters."""

    request = _request_context(parameters)
    document = _decode_json(body)
    root = _object(document, "")
    _reject_unknown(root, _ROOT_KEYS, "")
    version = _require_str(root.get("version"), "/version")
    status = _require_int(root.get("status_code"), "/status_code")
    status_message = _require_str(root.get("status_message"), "/status_message")
    duration = _require_str(root.get("time"), "/time")
    cost = _require_decimal(root.get("cost"), "/cost")
    tasks_count = _require_int(root.get("tasks_count"), "/tasks_count")
    tasks_error = _require_int(root.get("tasks_error"), "/tasks_error")
    if tasks_count < 0:
        raise SearchMentionsParseError(
            "invalid_number", "/tasks_count", "counts must not be negative"
        )
    if tasks_error < 0:
        raise SearchMentionsParseError(
            "invalid_number", "/tasks_error", "counts must not be negative"
        )
    task_list = _require_array(root.get("tasks"), "/tasks")
    if tasks_count != len(task_list):
        raise SearchMentionsParseError(
            "count_mismatch", "/tasks_count", "tasks_count does not match tasks length"
        )
    if len(task_list) != 1:
        raise SearchMentionsParseError("tasks_length", "/tasks", "exactly one task is required")
    task = _object(task_list[0], "/tasks/0")
    _reject_unknown(task, _TASK_KEYS, "/tasks/0")
    task_status = _require_int(task.get("status_code"), "/tasks/0/status_code")
    task_message = _require_str(task.get("status_message"), "/tasks/0/status_message")
    task_duration = _require_str(task.get("time"), "/tasks/0/time")
    task_cost = _require_decimal(task.get("cost"), "/tasks/0/cost")
    task_id = _require_str(task.get("id"), "/tasks/0/id")
    path = _string_tuple(task.get("path"), "/tasks/0/path")
    echo = _parse_echo(task.get("data"), "/tasks/0/data")
    result_count = _require_int(task.get("result_count"), "/tasks/0/result_count")
    if result_count < 0:
        raise SearchMentionsParseError(
            "invalid_number",
            "/tasks/0/result_count",
            "counts must not be negative",
        )
    expected_tasks_error = 0 if task_status == SUCCESS_STATUS else 1
    if tasks_error != expected_tasks_error:
        raise SearchMentionsParseError(
            "count_mismatch",
            "/tasks_error",
            "tasks_error does not match the number of non-success tasks",
        )
    if status == SUCCESS_STATUS and task_status != SUCCESS_STATUS:
        return _error_ir(
            request=request,
            echo=echo,
            version=version,
            status=status,
            status_message=status_message,
            duration=duration,
            cost=cost,
            tasks_count=tasks_count,
            tasks_error=tasks_error,
            task_id=task_id,
            task_status=task_status,
            task_message=task_message,
            task_duration=task_duration,
            task_cost=task_cost,
            task_path=path,
            result_count=result_count,
        )
    if status != SUCCESS_STATUS and task_status == SUCCESS_STATUS:
        raise SearchMentionsParseError(
            "inconsistent_status",
            "/status_code",
            "top-level and task status are inconsistent",
        )
    if status != SUCCESS_STATUS:
        return _error_ir(
            request=request,
            echo=echo,
            version=version,
            status=status,
            status_message=status_message,
            duration=duration,
            cost=cost,
            tasks_count=tasks_count,
            tasks_error=tasks_error,
            task_id=task_id,
            task_status=task_status,
            task_message=task_message,
            task_duration=task_duration,
            task_cost=task_cost,
            task_path=path,
            result_count=result_count,
        )
    result_list = _require_array(task.get("result"), "/tasks/0/result")
    if result_count != len(result_list):
        raise SearchMentionsParseError(
            "count_mismatch",
            "/tasks/0/result_count",
            "result_count does not match result length",
        )
    if len(result_list) != 1:
        raise SearchMentionsParseError(
            "result_length", "/tasks/0/result", "exactly one result is required"
        )
    result = _object(result_list[0], "/tasks/0/result/0")
    _reject_unknown(result, _RESULT_KEYS, "/tasks/0/result/0")
    total_count = _require_int(result.get("total_count"), "/tasks/0/result/0/total_count")
    offset = _require_int(result.get("offset"), "/tasks/0/result/0/offset")
    items_count = _require_int(result.get("items_count"), "/tasks/0/result/0/items_count")
    if total_count < 0 or offset < 0 or items_count < 0:
        raise SearchMentionsParseError(
            "invalid_number", "/tasks/0/result/0/total_count", "counts must not be negative"
        )
    if offset != request.offset:
        raise SearchMentionsParseError(
            "offset_mismatch",
            "/tasks/0/result/0/offset",
            "result offset does not match Attempt offset",
        )
    if "search_after_token" not in result:
        raise SearchMentionsParseError(
            "missing_field",
            "/tasks/0/result/0/search_after_token",
            "search_after_token missing",
        )
    token = _continuation(result.get("search_after_token"), "/tasks/0/result/0/search_after_token")
    items_value = result.get("items")
    if "items" not in result:
        raise SearchMentionsParseError("missing_field", "/tasks/0/result/0/items", "items missing")
    if items_value is None:
        raise SearchMentionsParseError(
            "wrong_type", "/tasks/0/result/0/items", "items must not be JSON null"
        )
    items_list = _require_array(items_value, "/tasks/0/result/0/items")
    if items_count != len(items_list):
        raise SearchMentionsParseError(
            "count_mismatch",
            "/tasks/0/result/0/items_count",
            "items_count does not match items length",
        )
    if total_count < items_count:
        raise SearchMentionsParseError(
            "count_mismatch",
            "/tasks/0/result/0/total_count",
            "total_count is less than items_count",
        )
    items = tuple(
        _parse_item(item, f"/tasks/0/result/0/items/{index}", request)
        for index, item in enumerate(items_list)
    )
    return SearchMentionsIR(
        outcome=ParseClassification.ADMITTED,
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
        task_path=path,
        result_count=result_count,
        total_count=total_count,
        offset=offset,
        items_count=items_count,
        search_after_token=token,
        items=items,
    )


def _error_ir(
    *,
    request: RequestContext,
    echo: ProviderEcho | None,
    version: str,
    status: int,
    status_message: str,
    duration: str,
    cost: Decimal,
    tasks_count: int,
    tasks_error: int,
    task_id: str | None,
    task_status: int | None,
    task_message: str | None,
    task_duration: str | None,
    task_cost: Decimal | None,
    task_path: tuple[str, ...] | None,
    result_count: int | None,
) -> SearchMentionsIR:
    return SearchMentionsIR(
        outcome=ParseClassification.PROVIDER_ERROR,
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
        total_count=None,
        offset=None,
        items_count=None,
        search_after_token=None,
        items=(),
    )


def _request_context(parameters: Mapping[str, object]) -> RequestContext:
    obj = _object(dict(parameters), "/attempt")
    _reject_unknown(obj, _PARAMETER_KEYS, "/attempt")
    contract = _require_str(obj.get("contract"), "/attempt/contract")
    if contract != MENTIONS_ADAPTER_CONTRACT:
        raise SearchMentionsParseError(
            "unknown_enum", "/attempt/contract", "adapter_contract is not Search Mentions"
        )
    target_list = _require_array(obj.get("target"), "/attempt/target")
    if len(target_list) != 1:
        raise SearchMentionsParseError(
            "target_length", "/attempt/target", "exactly one target is required"
        )
    target = _object(target_list[0], "/attempt/target/0")
    _reject_unknown(target, _ECHO_TARGET_KEYS, "/attempt/target/0")
    scope = _string_tuple(target.get("search_scope"), "/attempt/target/0/search_scope")
    return RequestContext(
        keyword=_require_str(target.get("keyword"), "/attempt/target/0/keyword"),
        match_type=_require_str(target.get("match_type"), "/attempt/target/0/match_type"),
        search_filter=_require_str(
            target.get("search_filter"), "/attempt/target/0/search_filter"
        ),
        search_scope=scope,
        platform=_require_str(obj.get("platform"), "/attempt/platform"),
        location_code=_require_int(obj.get("location_code"), "/attempt/location_code"),
        language_code=_require_str(obj.get("language_code"), "/attempt/language_code"),
        limit=_require_int(obj.get("limit"), "/attempt/limit"),
        offset=_require_int(obj.get("offset"), "/attempt/offset"),
    )


def _parse_echo(value: object, path: str) -> ProviderEcho:
    obj = _object(value, path)
    _reject_unknown(obj, _ECHO_KEYS, path)
    target_list = _require_array(obj.get("target"), f"{path}/target")
    targets: list[EchoTarget] = []
    for index, item in enumerate(target_list):
        entry = _object(item, f"{path}/target/{index}")
        _reject_unknown(entry, _ECHO_TARGET_KEYS, f"{path}/target/{index}")
        targets.append(
            EchoTarget(
                keyword=_require_str(entry.get("keyword"), f"{path}/target/{index}/keyword"),
                match_type=_require_str(
                    entry.get("match_type"), f"{path}/target/{index}/match_type"
                ),
                search_filter=_require_str(
                    entry.get("search_filter"), f"{path}/target/{index}/search_filter"
                ),
                search_scope=_string_tuple(
                    entry.get("search_scope"), f"{path}/target/{index}/search_scope"
                ),
            )
        )
    return ProviderEcho(
        api=_require_str(obj.get("api"), f"{path}/api"),
        function=_require_str(obj.get("function"), f"{path}/function"),
        language_code=_require_str(obj.get("language_code"), f"{path}/language_code"),
        limit=_require_int(obj.get("limit"), f"{path}/limit"),
        location_code=_require_int(obj.get("location_code"), f"{path}/location_code"),
        offset=_require_int(obj.get("offset"), f"{path}/offset"),
        platform=_require_str(obj.get("platform"), f"{path}/platform"),
        target=tuple(targets),
    )


def _parse_item(value: object, path: str, request: RequestContext) -> ItemOccurrence:
    item = _object(value, path)
    _reject_unknown(item, _ITEM_KEYS, path)
    platform = _require_str(item.get("platform"), f"{path}/platform")
    location = _require_int(item.get("location_code"), f"{path}/location_code")
    language = _require_str(item.get("language_code"), f"{path}/language_code")
    if platform != request.platform:
        raise SearchMentionsParseError(
            "context_mismatch", f"{path}/platform", "item platform does not match Attempt"
        )
    if location != request.location_code:
        raise SearchMentionsParseError(
            "context_mismatch",
            f"{path}/location_code",
            "item location does not match Attempt",
        )
    if language != request.language_code:
        raise SearchMentionsParseError(
            "context_mismatch",
            f"{path}/language_code",
            "item language does not match Attempt",
        )
    first_text = _require_str(item.get("first_response_at"), f"{path}/first_response_at")
    last_text = _require_str(item.get("last_response_at"), f"{path}/last_response_at")
    first = _provider_clock(first_text, f"{path}/first_response_at")
    last = _provider_clock(last_text, f"{path}/last_response_at")
    if last < first:
        raise SearchMentionsParseError(
            "invalid_time",
            f"{path}/last_response_at",
            "last_response_at is before first_response_at",
        )
    if "monthly_searches" not in item:
        raise SearchMentionsParseError(
            "missing_field", f"{path}/monthly_searches", "monthly_searches missing"
        )
    monthly = _parse_monthly(item.get("monthly_searches"), f"{path}/monthly_searches")
    if "sources" not in item:
        raise SearchMentionsParseError("missing_field", f"{path}/sources", "sources missing")
    sources = _parse_sources(item.get("sources"), f"{path}/sources")
    google_nulls = {
        name: _require_google_null(item, name, f"{path}/{name}")
        for name in _GOOGLE_NULL_ITEM_FIELDS
    }
    volume = _require_int(item.get("ai_search_volume"), f"{path}/ai_search_volume")
    if volume < 0:
        raise SearchMentionsParseError(
            "invalid_number",
            f"{path}/ai_search_volume",
            "ai_search_volume must not be negative",
        )
    return ItemOccurrence(
        platform=platform,
        model_name=_require_str(item.get("model_name"), f"{path}/model_name"),
        location_code=location,
        language_code=language,
        question=_require_str(item.get("question"), f"{path}/question"),
        answer=_require_str(item.get("answer"), f"{path}/answer"),
        ai_search_volume=volume,
        is_web_search_based=_require_bool(
            item.get("is_web_search_based"), f"{path}/is_web_search_based"
        ),
        first_response_at=first_text,
        last_response_at=last_text,
        search_results=google_nulls["search_results"],
        brand_entities=google_nulls["brand_entities"],
        fan_out_queries=google_nulls["fan_out_queries"],
        monthly_searches=monthly,
        sources=sources,
    )


def _parse_sources(value: object, path: str) -> tuple[SourceOccurrence, ...]:
    if value is None:
        raise SearchMentionsParseError("wrong_type", path, "sources must not be JSON null")
    rows = _require_array(value, path)
    sources: list[SourceOccurrence] = []
    ranks: list[int] = []
    for index, item in enumerate(rows):
        source_path = f"{path}/{index}"
        obj = _object(item, source_path)
        _reject_unknown(obj, _SOURCE_KEYS, source_path)
        rank = _require_int(obj.get("rank"), f"{source_path}/rank")
        if rank < 1:
            raise SearchMentionsParseError(
                "invalid_number", f"{source_path}/rank", "rank must be a positive integer"
            )
        ranks.append(rank)
        sources.append(
            SourceOccurrence(
                rank=rank,
                title=_require_str(obj.get("title"), f"{source_path}/title"),
                url=_require_url(obj.get("url"), f"{source_path}/url"),
                domain=_require_str(obj.get("domain"), f"{source_path}/domain"),
                source_name=_require_str(obj.get("source_name"), f"{source_path}/source_name"),
                snippet=_require_str(obj.get("snippet"), f"{source_path}/snippet"),
                publication_date=_null_or_str(
                    obj, "publication_date", f"{source_path}/publication_date"
                ),
                thumbnail=_null_or_str(obj, "thumbnail", f"{source_path}/thumbnail"),
                markdown=_null_or_str(obj, "markdown", f"{source_path}/markdown"),
            )
        )
    expected = list(range(1, len(sources) + 1))
    if sorted(ranks) != expected:
        raise SearchMentionsParseError(
            "invalid_rank",
            path,
            "source ranks must be unique, positive, and contiguous from 1",
        )
    return tuple(sources)


def _parse_monthly(value: object, path: str) -> tuple[MonthlyPoint, ...]:
    if value is None:
        raise SearchMentionsParseError(
            "wrong_type", path, "monthly_searches must not be JSON null"
        )
    rows = _require_array(value, path)
    points: list[MonthlyPoint] = []
    seen: set[tuple[int, int]] = set()
    for index, item in enumerate(rows):
        point_path = f"{path}/{index}"
        obj = _object(item, point_path)
        _reject_unknown(obj, _MONTHLY_KEYS, point_path)
        year = _require_int(obj.get("year"), f"{point_path}/year")
        month = _require_int(obj.get("month"), f"{point_path}/month")
        volume = _require_int(obj.get("search_volume"), f"{point_path}/search_volume")
        if year < YEAR_MIN or year > YEAR_MAX:
            raise SearchMentionsParseError(
                "invalid_period", f"{point_path}/year", "year is outside calendar bounds"
            )
        if month < 1 or month > 12:
            raise SearchMentionsParseError(
                "invalid_period", f"{point_path}/month", "month must be 1..12"
            )
        if volume < 0:
            raise SearchMentionsParseError(
                "invalid_number",
                f"{point_path}/search_volume",
                "monthly search volume must not be negative",
            )
        period = (year, month)
        if period in seen:
            raise SearchMentionsParseError(
                "duplicate_period", point_path, "duplicate historical year/month"
            )
        seen.add(period)
        points.append(MonthlyPoint(year=year, month=month, search_volume=volume))
    return tuple(points)


def _continuation(value: object, path: str) -> Field[str]:
    if value is None:
        return Field[str].json_null()
    if not isinstance(value, str):
        raise SearchMentionsParseError("wrong_type", path, "must be JSON null or a string")
    if value == "":
        raise SearchMentionsParseError(
            "invalid_value", path, "continuation token must not be empty"
        )
    return Field[str].stated(value)


def _require_google_null(obj: Mapping[str, object], key: str, path: str) -> Field[object]:
    if key not in obj:
        raise SearchMentionsParseError("missing_field", path, f"{key} is required")
    if obj[key] is not None:
        raise SearchMentionsParseError(
            "google_null_drift",
            path,
            f"{key} must be JSON null on the Google adapter",
        )
    return Field[object].json_null()


def _null_or_str(obj: Mapping[str, object], key: str, path: str) -> Field[str]:
    if key not in obj:
        raise SearchMentionsParseError("missing_field", path, f"{key} is required")
    value = obj[key]
    if value is None:
        return Field[str].json_null()
    if not isinstance(value, str):
        raise SearchMentionsParseError("wrong_type", path, "must be JSON null or a string")
    return Field[str].stated(value)


def _provider_clock(value: object, path: str) -> datetime:
    text = _require_str(value, path)
    if _PROVIDER_TIME_RE.fullmatch(text) is None:
        raise SearchMentionsParseError(
            "invalid_time", path, "provider clock is not YYYY-MM-DD HH:MM:SS +00:00"
        )
    try:
        return datetime.strptime(text, _PROVIDER_TIME_FORMAT)
    except ValueError as exc:
        raise SearchMentionsParseError(
            "invalid_time", path, "provider clock is not a valid calendar time"
        ) from exc


def _require_url(value: object, path: str) -> str:
    text = _require_str(value, path)
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"} or parsed.netloc == "" or " " in text:
        raise SearchMentionsParseError(
            "invalid_url", path, "absolute http(s) URL required"
        )
    return text


def _string_tuple(value: object, path: str) -> tuple[str, ...]:
    rows = _require_array(value, path)
    return tuple(_require_str(item, f"{path}/{index}") for index, item in enumerate(rows))


def _decode_json(raw: bytes) -> object:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise SearchMentionsParseError("utf8_bom", "", "UTF-8 BOM is forbidden")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SearchMentionsParseError("invalid_utf8", "", "body is not strict UTF-8") from exc
    decoder = json.JSONDecoder(
        parse_int=int,
        parse_float=Decimal,
        parse_constant=_reject_constant,
        object_pairs_hook=_object_pairs,
    )
    try:
        value, end = decoder.raw_decode(text)
    except json.JSONDecodeError as exc:
        raise SearchMentionsParseError("invalid_json", "", "body is not valid JSON") from exc
    if text[end:].strip() != "":
        raise SearchMentionsParseError(
            "trailing_data", "", "non-whitespace data follows the JSON document"
        )
    return value


def _reject_constant(value: str) -> None:
    raise SearchMentionsParseError("non_finite_number", "", f"{value} is not a finite number")


def _object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise SearchMentionsParseError(
                "duplicate_member", f"/{_escape(key)}", "duplicate object member name"
            )
        result[key] = value
    return result


def _reject_unknown(obj: Mapping[str, object], allowed: frozenset[str], path: str) -> None:
    extra = [key for key in obj if key not in allowed]
    if extra:
        pointer = f"{path}/{_escape(extra[0])}" if path else f"/{_escape(extra[0])}"
        raise SearchMentionsParseError(
            "unknown_field", pointer, "unknown field on a closed object"
        )


def _object(value: object, path: str) -> dict[str, object]:
    if isinstance(value, Mapping) and not isinstance(value, (str, bytes, bytearray)):
        return {str(key): item for key, item in value.items()}
    raise SearchMentionsParseError("wrong_type", path or "/", "must be an object")


def _require_array(value: object, path: str) -> list[object]:
    if not isinstance(value, list) or isinstance(value, (str, bytes, bytearray)):
        raise SearchMentionsParseError("wrong_type", path, "must be an array")
    return list(value)


def _require_str(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise SearchMentionsParseError("wrong_type", path, "must be a string")
    return value


def _require_int(value: object, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SearchMentionsParseError("wrong_type", path, "must be a JSON integer")
    return value


def _require_bool(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise SearchMentionsParseError("wrong_type", path, "must be a JSON boolean")
    return value


def _require_decimal(value: object, path: str) -> Decimal:
    if isinstance(value, bool):
        raise SearchMentionsParseError("wrong_type", path, "must be a decimal-capable number")
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, Decimal):
        return value
    raise SearchMentionsParseError("wrong_type", path, "must be a decimal-capable number")


def _escape(key: str) -> str:
    return key.replace("~", "~0").replace("/", "~1")


def search_mentions_recipe() -> dict[str, object]:
    """Return the first Search Mentions Derivation Recipe document."""

    kinds = [
        {
            "axes": {
                "model_name": "string",
                "question": "string",
                "requested_keyword": "string",
            },
            "observation_kind": ITEM_KIND,
        },
        {
            "axes": {
                "model_name": "string",
                "month": "integer",
                "question": "string",
                "requested_keyword": "string",
                "year": "integer",
            },
            "observation_kind": MONTHLY_KIND,
        },
        {
            "axes": {
                "model_name": "string",
                "question": "string",
                "requested_keyword": "string",
                "url": "string",
            },
            "observation_kind": SOURCE_KIND,
        },
    ]
    return validate_recipe(
        {
            "adapter_contract": MENTIONS_ADAPTER_CONTRACT,
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
                "rule": "provider_stated_year_month_1_9999",
            },
            "extension_policy": {
                "closed_objects": [
                    "/",
                    "/items",
                    "/monthly_searches",
                    "/result",
                    "/sources",
                    "/tasks",
                    "/tasks/data",
                ],
                "extension_permitted_objects": [],
                "unknown_closed_field": "fail_closed",
                "unknown_extension_field": "fail_closed",
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
                "kinds": kinds,
            },
            "observation_kinds": [ITEM_KIND, MONTHLY_KIND, SOURCE_KIND],
            "parser_contract": PARSER_CONTRACT,
            "provider": PROVIDER,
            "provider_update_time": {
                "inheritance": "never_from_capture_or_sibling",
                "rule": "structure_stated_or_unstated",
            },
            "reconciliation": {"rule": "attempt_parameters_item_context"},
            "schema": SCHEMA,
            "version": SCHEMA_VERSION,
        }
    )


SEARCH_MENTIONS_RECIPE: Final[dict[str, object]] = search_mentions_recipe()
SEARCH_MENTIONS_RECIPE_BYTES: Final[bytes] = recipe_bytes(SEARCH_MENTIONS_RECIPE)
SEARCH_MENTIONS_RECIPE_ID: Final[str] = recipe_derivation_version_id(
    SEARCH_MENTIONS_RECIPE
)
