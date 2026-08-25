"""Strict DataForSEO LLM Mentions Historical parser and typed in-memory IR."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Final

from observatory.capture_event import HISTORICAL_ADAPTER_CONTRACT
from observatory.dataforseo_keyword_overview import ParseClassification

SUCCESS_STATUS: Final[int] = 20000
YEAR_MIN: Final[int] = 1
YEAR_MAX: Final[int] = 9999

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
        "date_from",
        "date_to",
        "language_code",
        "location_code",
        "platform",
        "target",
    }
)
_TARGET_KEYS: Final[frozenset[str]] = frozenset(
    {"keyword", "match_type", "search_filter", "search_scope"}
)
_PARAMETER_KEYS: Final[frozenset[str]] = frozenset(
    {
        "contract",
        "date_from",
        "date_to",
        "language_code",
        "location_code",
        "platform",
        "target",
    }
)
_RESULT_KEYS: Final[frozenset[str]] = frozenset({"items", "items_count"})
_ITEM_KEYS: Final[frozenset[str]] = frozenset({"metrics", "month", "year"})
_METRICS_KEYS: Final[frozenset[str]] = frozenset({"ai_search_volume", "mentions"})


class HistoricalParseError(Exception):
    """Strict Historical parse failed."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        super().__init__(f"{code} at {path}: {message}")


@dataclass(frozen=True)
class RequestContext:
    contract: str
    date_from: str
    date_to: str
    keyword: str
    match_type: str
    search_filter: str
    search_scope: tuple[str, ...]
    platform: str
    location_code: int
    language_code: str


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
    date_from: str
    date_to: str
    language_code: str
    location_code: int
    platform: str
    target: tuple[EchoTarget, ...]


@dataclass(frozen=True)
class HistoricalPoint:
    year: int
    month: int
    mentions: int
    ai_search_volume: int
    provider_array_index: int


@dataclass(frozen=True)
class HistoricalIR:
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
    items_count: int | None
    items: tuple[HistoricalPoint, ...] | None


def parse_historical(body: bytes, parameters: Mapping[str, object]) -> HistoricalIR:
    """Parse Historical body bytes against verified Attempt parameters."""

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
        raise HistoricalParseError(
            "count_mismatch", "/tasks_count", "tasks_count does not match tasks length"
        )
    if len(task_list) != 1:
        raise HistoricalParseError("tasks_length", "/tasks", "exactly one task is required")
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
        raise HistoricalParseError(
            "count_mismatch",
            "/tasks_error",
            "tasks_error does not match the number of non-success tasks",
        )
    if (status == SUCCESS_STATUS) != (task_status == SUCCESS_STATUS):
        raise HistoricalParseError(
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
        raise HistoricalParseError(
            "count_mismatch",
            "/tasks/0/result_count",
            "result_count does not match result length",
        )
    if len(result_list) != 1:
        raise HistoricalParseError(
            "result_length", "/tasks/0/result", "exactly one result is required"
        )
    result = _object(result_list[0], "/tasks/0/result/0")
    _reject_unknown(result, _RESULT_KEYS, "/tasks/0/result/0")
    items = _parse_items(result, "/tasks/0/result/0")
    items_count = _require_nonneg_int(result.get("items_count"), "/tasks/0/result/0/items_count")
    if items_count != len(items):
        raise HistoricalParseError(
            "count_mismatch",
            "/tasks/0/result/0/items_count",
            "items_count does not match items length",
        )
    return HistoricalIR(
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
        items_count=items_count,
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
) -> HistoricalIR:
    return HistoricalIR(
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
        items_count=None,
        items=None,
    )


def _request_context(parameters: Mapping[str, object]) -> RequestContext:
    obj = _object(dict(parameters), "/attempt")
    _reject_unknown(obj, _PARAMETER_KEYS, "/attempt")
    contract = _require_str(obj.get("contract"), "/attempt/contract")
    if contract != HISTORICAL_ADAPTER_CONTRACT:
        raise HistoricalParseError(
            "unknown_enum", "/attempt/contract", "adapter_contract is not Historical"
        )
    target_list = _require_array(obj.get("target"), "/attempt/target")
    if len(target_list) != 1:
        raise HistoricalParseError(
            "target_length", "/attempt/target", "exactly one target is required"
        )
    target = _object(target_list[0], "/attempt/target/0")
    _reject_unknown(target, _TARGET_KEYS, "/attempt/target/0")
    return RequestContext(
        contract=contract,
        date_from=_require_str(obj.get("date_from"), "/attempt/date_from"),
        date_to=_require_str(obj.get("date_to"), "/attempt/date_to"),
        keyword=_require_str(target.get("keyword"), "/attempt/target/0/keyword"),
        match_type=_require_str(target.get("match_type"), "/attempt/target/0/match_type"),
        search_filter=_require_str(
            target.get("search_filter"), "/attempt/target/0/search_filter"
        ),
        search_scope=_string_tuple(
            target.get("search_scope"), "/attempt/target/0/search_scope"
        ),
        platform=_require_str(obj.get("platform"), "/attempt/platform"),
        location_code=_require_int(obj.get("location_code"), "/attempt/location_code"),
        language_code=_require_str(obj.get("language_code"), "/attempt/language_code"),
    )


def _parse_echo(value: object, path: str) -> ProviderEcho:
    obj = _object(value, path)
    _reject_unknown(obj, _ECHO_KEYS, path)
    target_list = _require_array(obj.get("target"), f"{path}/target")
    targets: list[EchoTarget] = []
    for index, item in enumerate(target_list):
        entry = _object(item, f"{path}/target/{index}")
        _reject_unknown(entry, _TARGET_KEYS, f"{path}/target/{index}")
        targets.append(
            EchoTarget(
                keyword=_require_str(
                    entry.get("keyword"), f"{path}/target/{index}/keyword"
                ),
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
        date_from=_require_str(obj.get("date_from"), f"{path}/date_from"),
        date_to=_require_str(obj.get("date_to"), f"{path}/date_to"),
        language_code=_require_str(obj.get("language_code"), f"{path}/language_code"),
        location_code=_require_int(obj.get("location_code"), f"{path}/location_code"),
        platform=_require_str(obj.get("platform"), f"{path}/platform"),
        target=tuple(targets),
    )


def _parse_items(result: Mapping[str, object], path: str) -> tuple[HistoricalPoint, ...]:
    if "items" not in result:
        raise HistoricalParseError("missing_field", f"{path}/items", "items missing")
    value = result["items"]
    if value is None:
        raise HistoricalParseError("wrong_type", f"{path}/items", "items must not be JSON null")
    rows = _require_array(value, f"{path}/items")
    points: list[HistoricalPoint] = []
    seen: set[tuple[int, int]] = set()
    for index, item in enumerate(rows):
        item_path = f"{path}/items/{index}"
        obj = _object(item, item_path)
        _reject_unknown(obj, _ITEM_KEYS, item_path)
        year = _require_int(obj.get("year"), f"{item_path}/year")
        month = _require_int(obj.get("month"), f"{item_path}/month")
        if year < YEAR_MIN or year > YEAR_MAX:
            raise HistoricalParseError(
                "invalid_period", f"{item_path}/year", "year is outside calendar bounds"
            )
        if month < 1 or month > 12:
            raise HistoricalParseError(
                "invalid_period", f"{item_path}/month", "month must be 1..12"
            )
        if "metrics" not in obj:
            raise HistoricalParseError(
                "missing_field", f"{item_path}/metrics", "metrics missing"
            )
        metrics = _object(obj.get("metrics"), f"{item_path}/metrics")
        _reject_unknown(metrics, _METRICS_KEYS, f"{item_path}/metrics")
        mentions = _require_nonneg_int(
            metrics.get("mentions"), f"{item_path}/metrics/mentions"
        )
        volume = _require_nonneg_int(
            metrics.get("ai_search_volume"), f"{item_path}/metrics/ai_search_volume"
        )
        period = (year, month)
        if period in seen:
            raise HistoricalParseError(
                "duplicate_period", item_path, "duplicate historical year/month"
            )
        seen.add(period)
        points.append(
            HistoricalPoint(
                year=year,
                month=month,
                mentions=mentions,
                ai_search_volume=volume,
                provider_array_index=index,
            )
        )
    return tuple(points)


def _string_tuple(value: object, path: str) -> tuple[str, ...]:
    rows = _require_array(value, path)
    return tuple(_require_str(item, f"{path}/{index}") for index, item in enumerate(rows))


def _decode_json(raw: bytes) -> object:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise HistoricalParseError("utf8_bom", "", "UTF-8 BOM is forbidden")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HistoricalParseError("invalid_utf8", "", "body is not strict UTF-8") from exc
    decoder = json.JSONDecoder(
        parse_int=int,
        parse_float=Decimal,
        parse_constant=_reject_constant,
        object_pairs_hook=_object_pairs,
    )
    try:
        value, end = decoder.raw_decode(text)
    except json.JSONDecodeError as exc:
        raise HistoricalParseError("invalid_json", "", "body is not valid JSON") from exc
    if text[end:].strip() != "":
        raise HistoricalParseError(
            "trailing_data", "", "non-whitespace data follows the JSON document"
        )
    return value


def _reject_constant(value: str) -> None:
    raise HistoricalParseError("non_finite_number", "", f"{value} is not a finite number")


def _object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise HistoricalParseError(
                "duplicate_member", f"/{_escape(key)}", "duplicate object member name"
            )
        result[key] = value
    return result


def _reject_unknown(obj: Mapping[str, object], allowed: frozenset[str], path: str) -> None:
    extra = [key for key in obj if key not in allowed]
    if extra:
        pointer = f"{path}/{_escape(extra[0])}" if path else f"/{_escape(extra[0])}"
        raise HistoricalParseError(
            "unknown_field", pointer, "unknown field on a closed object"
        )


def _object(value: object, path: str) -> dict[str, object]:
    if isinstance(value, Mapping) and not isinstance(value, (str, bytes, bytearray)):
        return {str(key): item for key, item in value.items()}
    raise HistoricalParseError("wrong_type", path or "/", "must be an object")


def _require_array(value: object, path: str) -> list[object]:
    if not isinstance(value, list) or isinstance(value, (str, bytes, bytearray)):
        raise HistoricalParseError("wrong_type", path, "must be an array")
    return list(value)


def _require_str(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise HistoricalParseError("wrong_type", path, "must be a string")
    return value


def _require_int(value: object, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise HistoricalParseError("wrong_type", path, "must be a JSON integer")
    return value


def _require_nonneg_int(value: object, path: str) -> int:
    number = _require_int(value, path)
    if number < 0:
        raise HistoricalParseError(
            "invalid_number", path, "counts must not be negative"
        )
    return number


def _require_decimal(value: object, path: str) -> Decimal:
    if isinstance(value, bool):
        raise HistoricalParseError("wrong_type", path, "must be a decimal-capable number")
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, Decimal):
        return value
    raise HistoricalParseError("wrong_type", path, "must be a decimal-capable number")


def _escape(key: str) -> str:
    return key.replace("~", "~0").replace("/", "~1")
