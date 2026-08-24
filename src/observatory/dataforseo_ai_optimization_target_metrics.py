"""Strict DataForSEO Target Metrics parser and typed in-memory IR."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Final

from observatory.capture_event import TARGET_METRICS_ADAPTER_CONTRACT
from observatory.dataforseo_keyword_overview import Field, ParseClassification

SUCCESS_STATUS: Final[int] = 20000
PROVIDER: Final[str] = "dataforseo"
PARSER_CONTRACT: Final[str] = (
    "dataforseo-ai-optimization-target-metrics-live-parser-v1"
)
TOTAL_KIND: Final[str] = "dataforseo.google.ai_optimization.target_metrics.total.v1"
SOURCE_DOMAIN_KIND: Final[str] = (
    "dataforseo.google.ai_optimization.target_metrics.source_domain.v1"
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
_ECHO_KEYS: Final[frozenset[str]] = frozenset(
    {
        "api",
        "function",
        "internal_list_limit",
        "language_code",
        "location_code",
        "platform",
        "target",
    }
)
_ECHO_TARGET_KEYS: Final[frozenset[str]] = frozenset(
    {"keyword", "match_type", "search_filter", "search_scope"}
)
_PARAMETER_KEYS: Final[frozenset[str]] = frozenset(
    {
        "contract",
        "internal_list_limit",
        "language_code",
        "location_code",
        "platform",
        "target",
    }
)
_RESULT_KEYS: Final[frozenset[str]] = frozenset(
    {"aggregated_metrics", "items", "items_count", "offset", "total_count"}
)
_AGG_KEYS: Final[frozenset[str]] = frozenset(
    {
        "brand_entities_category",
        "brand_entities_title",
        "language",
        "location",
        "platform",
        "search_results_domain",
        "sources_domain",
        "total",
    }
)
_ROW_KEYS: Final[frozenset[str]] = frozenset({"ai_search_volume", "key", "mentions"})
_TOTAL_KEYS: Final[frozenset[str]] = frozenset({"ai_search_volume", "mentions"})


class TargetMetricsParseError(Exception):
    """Strict Target Metrics parse or reconciliation failed."""

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
    internal_list_limit: int


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
    internal_list_limit: int
    location_code: int
    platform: str
    target: tuple[EchoTarget, ...]


@dataclass(frozen=True)
class LocationRow:
    key: int
    mentions: int
    ai_search_volume: int
    provider_array_index: int


@dataclass(frozen=True)
class GroupingRow:
    key: str
    mentions: int
    ai_search_volume: int
    provider_array_index: int


@dataclass(frozen=True)
class TotalMetrics:
    mentions: int
    ai_search_volume: int


@dataclass(frozen=True)
class AggregatedMetrics:
    location: tuple[LocationRow, ...]
    language: tuple[GroupingRow, ...]
    platform: tuple[GroupingRow, ...]
    sources_domain: tuple[GroupingRow, ...]
    search_results_domain: Field[tuple[GroupingRow, ...]]
    brand_entities_title: Field[tuple[GroupingRow, ...]]
    brand_entities_category: Field[tuple[GroupingRow, ...]]
    total: TotalMetrics


@dataclass(frozen=True)
class TargetMetricsIR:
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
    items: Field[tuple[object, ...]] | None
    aggregated_metrics: AggregatedMetrics | None


def parse_target_metrics(
    body: bytes, parameters: Mapping[str, object]
) -> TargetMetricsIR:
    """Parse Target Metrics body bytes against verified Attempt parameters."""

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
        raise TargetMetricsParseError(
            "count_mismatch", "/tasks_count", "tasks_count does not match tasks length"
        )
    if len(task_list) != 1:
        raise TargetMetricsParseError("tasks_length", "/tasks", "exactly one task is required")
    task = _object(task_list[0], "/tasks/0")
    _reject_unknown(task, _TASK_KEYS, "/tasks/0")
    task_status = _require_int(task.get("status_code"), "/tasks/0/status_code")
    task_message = _require_str(task.get("status_message"), "/tasks/0/status_message")
    task_duration = _require_str(task.get("time"), "/tasks/0/time")
    task_cost = _require_decimal(task.get("cost"), "/tasks/0/cost")
    task_id = _require_str(task.get("id"), "/tasks/0/id")
    path = _string_tuple(task.get("path"), "/tasks/0/path")
    echo = _parse_echo(task.get("data"), "/tasks/0/data")
    result_count = _require_nonneg_int(task.get("result_count"), "/tasks/0/result_count")
    expected_tasks_error = 0 if task_status == SUCCESS_STATUS else 1
    if tasks_error != expected_tasks_error:
        raise TargetMetricsParseError(
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
        raise TargetMetricsParseError(
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
        raise TargetMetricsParseError(
            "count_mismatch",
            "/tasks/0/result_count",
            "result_count does not match result length",
        )
    if len(result_list) != 1:
        raise TargetMetricsParseError(
            "result_length", "/tasks/0/result", "exactly one result is required"
        )
    result = _object(result_list[0], "/tasks/0/result/0")
    _reject_unknown(result, _RESULT_KEYS, "/tasks/0/result/0")
    items = _parse_items(result, "/tasks/0/result/0")
    total_count = _require_nonneg_int(result.get("total_count"), "/tasks/0/result/0/total_count")
    offset = _require_nonneg_int(result.get("offset"), "/tasks/0/result/0/offset")
    items_count = _require_nonneg_int(result.get("items_count"), "/tasks/0/result/0/items_count")
    if total_count != 0:
        raise TargetMetricsParseError(
            "invalid_count",
            "/tasks/0/result/0/total_count",
            "successful Target Metrics total_count must be 0",
        )
    if offset != 0:
        raise TargetMetricsParseError(
            "invalid_count",
            "/tasks/0/result/0/offset",
            "successful Target Metrics offset must be 0",
        )
    if items_count != 0:
        raise TargetMetricsParseError(
            "invalid_count",
            "/tasks/0/result/0/items_count",
            "successful Target Metrics items_count must be 0",
        )
    if "aggregated_metrics" not in result:
        raise TargetMetricsParseError(
            "missing_field",
            "/tasks/0/result/0/aggregated_metrics",
            "aggregated_metrics missing",
        )
    aggregated = _parse_aggregated(
        result.get("aggregated_metrics"), "/tasks/0/result/0/aggregated_metrics"
    )
    return TargetMetricsIR(
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
        items=items,
        aggregated_metrics=aggregated,
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
) -> TargetMetricsIR:
    return TargetMetricsIR(
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
        items=None,
        aggregated_metrics=None,
    )


def _request_context(parameters: Mapping[str, object]) -> RequestContext:
    obj = _object(dict(parameters), "/attempt")
    _reject_unknown(obj, _PARAMETER_KEYS, "/attempt")
    contract = _require_str(obj.get("contract"), "/attempt/contract")
    if contract != TARGET_METRICS_ADAPTER_CONTRACT:
        raise TargetMetricsParseError(
            "unknown_enum", "/attempt/contract", "adapter_contract is not Target Metrics"
        )
    target_list = _require_array(obj.get("target"), "/attempt/target")
    if len(target_list) != 1:
        raise TargetMetricsParseError(
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
        internal_list_limit=_require_nonneg_int(
            obj.get("internal_list_limit"), "/attempt/internal_list_limit"
        ),
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
        internal_list_limit=_require_nonneg_int(
            obj.get("internal_list_limit"), f"{path}/internal_list_limit"
        ),
        location_code=_require_int(obj.get("location_code"), f"{path}/location_code"),
        platform=_require_str(obj.get("platform"), f"{path}/platform"),
        target=tuple(targets),
    )


def _parse_items(result: Mapping[str, object], path: str) -> Field[tuple[object, ...]]:
    if "items" not in result:
        return Field[tuple[object, ...]].absent()
    value = result["items"]
    if value is None:
        return Field[tuple[object, ...]].json_null()
    rows = _require_array(value, f"{path}/items")
    if len(rows) != 0:
        raise TargetMetricsParseError(
            "unsupported_items",
            f"{path}/items",
            "Target Metrics defines no item-row shape",
        )
    return Field[tuple[object, ...]].stated(())


def _parse_aggregated(value: object, path: str) -> AggregatedMetrics:
    obj = _object(value, path)
    _reject_unknown(obj, _AGG_KEYS, path)
    return AggregatedMetrics(
        location=_required_location_rows(obj, path),
        language=_required_grouping_rows(obj, "language", path),
        platform=_required_grouping_rows(obj, "platform", path),
        sources_domain=_required_grouping_rows(obj, "sources_domain", path),
        search_results_domain=_optional_grouping_rows(obj, "search_results_domain", path),
        brand_entities_title=_optional_grouping_rows(obj, "brand_entities_title", path),
        brand_entities_category=_optional_grouping_rows(obj, "brand_entities_category", path),
        total=_parse_total(obj, path),
    )


def _required_location_rows(obj: Mapping[str, object], path: str) -> tuple[LocationRow, ...]:
    name = "location"
    if name not in obj:
        raise TargetMetricsParseError("missing_field", f"{path}/{name}", f"{name} missing")
    rows = _require_array(obj.get(name), f"{path}/{name}")
    parsed: list[LocationRow] = []
    seen: set[int] = set()
    for index, item in enumerate(rows):
        row_path = f"{path}/{name}/{index}"
        row = _object(item, row_path)
        _reject_unknown(row, _ROW_KEYS, row_path)
        key = _require_int(row.get("key"), f"{row_path}/key")
        if key in seen:
            raise TargetMetricsParseError(
                "duplicate_key", row_path, "duplicate grouping key"
            )
        seen.add(key)
        parsed.append(
            LocationRow(
                key=key,
                mentions=_require_nonneg_int(row.get("mentions"), f"{row_path}/mentions"),
                ai_search_volume=_require_nonneg_int(
                    row.get("ai_search_volume"), f"{row_path}/ai_search_volume"
                ),
                provider_array_index=index,
            )
        )
    return tuple(parsed)


def _required_grouping_rows(
    obj: Mapping[str, object], name: str, path: str
) -> tuple[GroupingRow, ...]:
    if name not in obj:
        raise TargetMetricsParseError("missing_field", f"{path}/{name}", f"{name} missing")
    return _parse_grouping_rows(obj.get(name), f"{path}/{name}")


def _optional_grouping_rows(
    obj: Mapping[str, object], name: str, path: str
) -> Field[tuple[GroupingRow, ...]]:
    if name not in obj:
        return Field[tuple[GroupingRow, ...]].absent()
    value = obj[name]
    if value is None:
        return Field[tuple[GroupingRow, ...]].json_null()
    return Field[tuple[GroupingRow, ...]].stated(_parse_grouping_rows(value, f"{path}/{name}"))


def _parse_grouping_rows(value: object, path: str) -> tuple[GroupingRow, ...]:
    rows = _require_array(value, path)
    parsed: list[GroupingRow] = []
    seen: set[str] = set()
    for index, item in enumerate(rows):
        row_path = f"{path}/{index}"
        row = _object(item, row_path)
        _reject_unknown(row, _ROW_KEYS, row_path)
        key = _require_str(row.get("key"), f"{row_path}/key")
        if key in seen:
            raise TargetMetricsParseError(
                "duplicate_key", row_path, "duplicate grouping key"
            )
        seen.add(key)
        parsed.append(
            GroupingRow(
                key=key,
                mentions=_require_nonneg_int(row.get("mentions"), f"{row_path}/mentions"),
                ai_search_volume=_require_nonneg_int(
                    row.get("ai_search_volume"), f"{row_path}/ai_search_volume"
                ),
                provider_array_index=index,
            )
        )
    return tuple(parsed)


def _parse_total(obj: Mapping[str, object], path: str) -> TotalMetrics:
    if "total" not in obj:
        raise TargetMetricsParseError("missing_field", f"{path}/total", "total missing")
    total = _object(obj.get("total"), f"{path}/total")
    _reject_unknown(total, _TOTAL_KEYS, f"{path}/total")
    return TotalMetrics(
        mentions=_require_nonneg_int(total.get("mentions"), f"{path}/total/mentions"),
        ai_search_volume=_require_nonneg_int(
            total.get("ai_search_volume"), f"{path}/total/ai_search_volume"
        ),
    )


def _string_tuple(value: object, path: str) -> tuple[str, ...]:
    rows = _require_array(value, path)
    return tuple(_require_str(item, f"{path}/{index}") for index, item in enumerate(rows))


def _decode_json(raw: bytes) -> object:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise TargetMetricsParseError("utf8_bom", "", "UTF-8 BOM is forbidden")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TargetMetricsParseError("invalid_utf8", "", "body is not strict UTF-8") from exc
    decoder = json.JSONDecoder(
        parse_int=int,
        parse_float=Decimal,
        parse_constant=_reject_constant,
        object_pairs_hook=_object_pairs,
    )
    try:
        value, end = decoder.raw_decode(text)
    except json.JSONDecodeError as exc:
        raise TargetMetricsParseError("invalid_json", "", "body is not valid JSON") from exc
    if text[end:].strip() != "":
        raise TargetMetricsParseError(
            "trailing_data", "", "non-whitespace data follows the JSON document"
        )
    return value


def _reject_constant(value: str) -> None:
    raise TargetMetricsParseError("non_finite_number", "", f"{value} is not a finite number")


def _object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise TargetMetricsParseError(
                "duplicate_member", f"/{_escape(key)}", "duplicate object member name"
            )
        result[key] = value
    return result


def _reject_unknown(obj: Mapping[str, object], allowed: frozenset[str], path: str) -> None:
    extra = [key for key in obj if key not in allowed]
    if extra:
        pointer = f"{path}/{_escape(extra[0])}" if path else f"/{_escape(extra[0])}"
        raise TargetMetricsParseError(
            "unknown_field", pointer, "unknown field on a closed object"
        )


def _object(value: object, path: str) -> dict[str, object]:
    if isinstance(value, Mapping) and not isinstance(value, (str, bytes, bytearray)):
        return {str(key): item for key, item in value.items()}
    raise TargetMetricsParseError("wrong_type", path or "/", "must be an object")


def _require_array(value: object, path: str) -> list[object]:
    if not isinstance(value, list) or isinstance(value, (str, bytes, bytearray)):
        raise TargetMetricsParseError("wrong_type", path, "must be an array")
    return list(value)


def _require_str(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise TargetMetricsParseError("wrong_type", path, "must be a string")
    return value


def _require_int(value: object, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TargetMetricsParseError("wrong_type", path, "must be a JSON integer")
    return value


def _require_nonneg_int(value: object, path: str) -> int:
    number = _require_int(value, path)
    if number < 0:
        raise TargetMetricsParseError(
            "invalid_number", path, "counts must not be negative"
        )
    return number


def _require_decimal(value: object, path: str) -> Decimal:
    if isinstance(value, bool):
        raise TargetMetricsParseError("wrong_type", path, "must be a decimal-capable number")
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, Decimal):
        return value
    raise TargetMetricsParseError("wrong_type", path, "must be a decimal-capable number")


def _escape(key: str) -> str:
    return key.replace("~", "~0").replace("/", "~1")
