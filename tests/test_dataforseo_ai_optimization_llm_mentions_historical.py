"""AI-15: Historical strict parser and AI-14 conformance fixture."""

from __future__ import annotations

import copy
import hashlib
import inspect
import json
import os
import socket
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from observatory.capture_event import (
    HISTORICAL_ADAPTER_CONTRACT,
    TARGET_METRICS_ADAPTER_CONTRACT,
)
from observatory.dataforseo_ai_optimization_llm_mentions_historical import (
    HistoricalParseError,
    parse_historical,
)
from observatory.dataforseo_keyword_overview import ParseClassification

FIXTURE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_ai_optimization_llm_mentions_historical_ai14.json"
)
TM_FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dataforseo_ai_optimization_target_metrics_ai09.json"
)
MENTIONS_FIXTURE = (
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
AI14_BODY_BYTES = 5246
AI14_BODY_SHA256 = "4419daf0b7076625129ab18c6bf3c83905b998c3b3332f2ba6d42c8879b50781"
TM_BODY_SHA256 = "7b6974704f73cff9687986a83ab14ba8ec942ccdbfde359ec7e8fde6bea8eee2"
MENTIONS_BODY_SHA256 = "8b3cd0fb0c9fa23c102696bfe6b7212396c0f7c110e9ca8ca5b8ee5af182e80a"
KO_BODY_SHA256 = "d91fdc7ab8acf429f0ff9c00bd7cdb725be1ba9585481af35d14f7c4e79a6d1c"
ORGANIC_BODY_SHA256 = "7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f"

KEYWORD = "generative engine optimization"
DATE_FROM = "2025-08-01"
DATE_TO = "2026-07-31"
POINTS: tuple[tuple[int, int, int, int], ...] = (
    (2026, 7, 1353, 428820),
    (2026, 6, 481, 358010),
    (2026, 5, 1449, 1086150),
    (2026, 4, 576, 122950),
    (2026, 3, 1019, 1114570),
    (2026, 2, 418, 178650),
    (2026, 1, 224, 471440),
    (2025, 12, 350, 312600),
    (2025, 11, 202, 43360),
    (2025, 10, 122, 51700),
    (2025, 9, 114, 27770),
    (2025, 8, 75, 23150),
)
PARAMETERS: dict[str, object] = {
    "contract": HISTORICAL_ADAPTER_CONTRACT,
    "date_from": DATE_FROM,
    "date_to": DATE_TO,
    "language_code": "en",
    "location_code": 2840,
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
    monkeypatch.delenv("OBSERVATORY_DATAFORSEO_LOGIN", raising=False)
    monkeypatch.delenv("OBSERVATORY_DATAFORSEO_PASSWORD", raising=False)


def _fixture() -> bytes:
    return FIXTURE_PATH.read_bytes()


def _parse(body: bytes | None = None, parameters: dict[str, object] | None = None) -> Any:
    return parse_historical(body if body is not None else _fixture(), parameters or PARAMETERS)


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


def _items(document: dict[str, Any]) -> list[Any]:
    rows = _result(document)["items"]
    assert isinstance(rows, list)
    return rows


def _point_tuple(point: Any) -> tuple[int, int, int, int]:
    return (point.year, point.month, point.mentions, point.ai_search_volume)


def test_frozen_fixture_independent_sha256_and_length() -> None:
    raw = _fixture()
    assert len(raw) == AI14_BODY_BYTES
    assert hashlib.sha256(raw).hexdigest() == AI14_BODY_SHA256
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert not raw.endswith(b"\n")
    assert Path("/home/chaz/.local/share/observatory").as_posix() not in str(FIXTURE_PATH)


def test_parser_signature_has_no_http_or_transport_input() -> None:
    names = tuple(inspect.signature(parse_historical).parameters)
    assert names == ("body", "parameters")


def test_golden_parse_preserves_request_echo_and_monthly_points() -> None:
    parsed = _parse()
    assert parsed.outcome is ParseClassification.ADMITTED
    assert parsed.outcome.value == "observation_admitted"
    assert parsed.outcome.value != "observation_admitted_empty"
    assert parsed.request.contract == HISTORICAL_ADAPTER_CONTRACT
    assert parsed.request.keyword == KEYWORD
    assert parsed.request.date_from == DATE_FROM
    assert parsed.request.date_to == DATE_TO
    assert parsed.request.match_type == "word_match"
    assert parsed.request.search_filter == "include"
    assert parsed.request.search_scope == ("answer",)
    assert parsed.request.platform == "google"
    assert parsed.request.location_code == 2840
    assert parsed.request.language_code == "en"
    assert parsed.version == "0.1.20260806"
    assert parsed.status_code == 20000
    assert parsed.status_message == "Ok."
    assert parsed.duration == "0.8682 sec."
    assert parsed.cost == Decimal("0.101")
    assert type(parsed.cost) is Decimal
    assert parsed.tasks_count == 1
    assert parsed.tasks_error == 0
    assert parsed.task_id == "08251832-1463-0662-0000-194ae8326094"
    assert parsed.task_status_code == 20000
    assert parsed.task_status_message == "Ok."
    assert parsed.task_duration == "0.7831 sec."
    assert parsed.task_cost == Decimal("0.101")
    assert parsed.task_path == (
        "v3",
        "ai_optimization",
        "llm_mentions",
        "historical",
        "live",
    )
    assert parsed.result_count == 1
    assert parsed.items_count == 12
    assert parsed.items is not None
    assert len(parsed.items) == 12
    assert parsed.echo is not None
    assert parsed.echo.api == "ai_optimization"
    assert parsed.echo.function == "historical"
    assert parsed.echo.date_from == DATE_FROM
    assert parsed.echo.date_to == DATE_TO
    assert parsed.echo.language_code == "en"
    assert parsed.echo.location_code == 2840
    assert parsed.echo.platform == "google"
    assert parsed.echo.target[0].keyword == KEYWORD
    assert parsed.echo.target[0].match_type == "word_match"
    assert parsed.echo.target[0].search_filter == "include"
    assert parsed.echo.target[0].search_scope == ("answer",)
    for index, expected in enumerate(POINTS):
        point = parsed.items[index]
        assert _point_tuple(point) == expected
        assert point.provider_array_index == index
    assert "date" not in parsed.__dataclass_fields__
    assert "provider_update_time" not in parsed.__dataclass_fields__


def test_echo_disagreement_does_not_replace_attempt_context() -> None:
    document = _decoded()
    document["tasks"][0]["data"]["language_code"] = "de"
    document["tasks"][0]["data"]["platform"] = "chat_gpt"
    document["tasks"][0]["data"]["date_from"] = "2024-01-01"
    document["tasks"][0]["data"]["date_to"] = "2024-12-31"
    document["tasks"][0]["data"]["target"][0]["keyword"] = "other keyword"
    parsed = _parse(_encode(document))
    assert parsed.request.keyword == KEYWORD
    assert parsed.request.language_code == "en"
    assert parsed.request.platform == "google"
    assert parsed.request.date_from == DATE_FROM
    assert parsed.request.date_to == DATE_TO
    assert parsed.echo is not None
    assert parsed.echo.language_code == "de"
    assert parsed.echo.platform == "chat_gpt"
    assert parsed.echo.date_from == "2024-01-01"
    assert parsed.echo.date_to == "2024-12-31"
    assert parsed.echo.target[0].keyword == "other keyword"
    assert parsed.items_count == 12
    assert parsed.items is not None
    assert _point_tuple(parsed.items[0]) == POINTS[0]


def test_empty_items_parses_as_empty_parser_ir_only() -> None:
    document = _decoded()
    _result(document)["items"] = []
    _result(document)["items_count"] = 0
    parsed = _parse(_encode(document))
    assert parsed.outcome is ParseClassification.ADMITTED
    assert parsed.outcome.value != "observation_admitted_empty"
    assert parsed.items_count == 0
    assert parsed.items == ()


def test_omitted_null_and_wrong_typed_items_fail() -> None:
    document = _decoded()
    del _result(document)["items"]
    with pytest.raises(HistoricalParseError, match="missing_field"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"] = None
    with pytest.raises(HistoricalParseError, match="wrong_type"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"] = {}
    with pytest.raises(HistoricalParseError, match="wrong_type"):
        _parse(_encode(document))


def test_items_count_mismatch_fails() -> None:
    document = _decoded()
    _result(document)["items_count"] = 11
    with pytest.raises(HistoricalParseError, match="count_mismatch"):
        _parse(_encode(document))


def test_shuffled_order_recomputes_only_provider_indexes() -> None:
    document = _decoded()
    rows = list(_items(document))
    rows.reverse()
    _result(document)["items"] = rows
    parsed = _parse(_encode(document))
    assert parsed.items is not None
    expected = tuple(reversed(POINTS))
    assert tuple(_point_tuple(point) for point in parsed.items) == expected
    assert [point.provider_array_index for point in parsed.items] == list(range(12))
    assert parsed.request.date_from == DATE_FROM
    assert parsed.request.date_to == DATE_TO


def test_dropped_in_window_month_keeps_request_window() -> None:
    document = _decoded()
    rows = _items(document)
    del rows[-1]
    _result(document)["items_count"] = 11
    parsed = _parse(_encode(document))
    assert parsed.items_count == 11
    assert parsed.items is not None
    assert tuple(_point_tuple(point) for point in parsed.items) == POINTS[:-1]
    assert [point.provider_array_index for point in parsed.items] == list(range(11))
    assert parsed.request.date_from == DATE_FROM
    assert parsed.request.date_to == DATE_TO


def test_added_out_of_window_month_keeps_request_window() -> None:
    document = _decoded()
    extra = {
        "year": 2026,
        "month": 8,
        "metrics": {"mentions": 1, "ai_search_volume": 2},
    }
    _items(document).append(extra)
    _result(document)["items_count"] = 13
    parsed = _parse(_encode(document))
    assert parsed.items_count == 13
    assert parsed.items is not None
    assert len(parsed.items) == 13
    assert tuple(_point_tuple(point) for point in parsed.items[:12]) == POINTS
    assert _point_tuple(parsed.items[12]) == (2026, 8, 1, 2)
    assert [point.provider_array_index for point in parsed.items] == list(range(13))
    assert parsed.request.date_from == DATE_FROM
    assert parsed.request.date_to == DATE_TO
    assert parsed.request.keyword == KEYWORD


def test_duplicate_period_fails_even_when_metrics_agree() -> None:
    document = _decoded()
    clone = copy.deepcopy(_items(document)[0])
    _items(document).append(clone)
    _result(document)["items_count"] = 13
    with pytest.raises(HistoricalParseError, match="duplicate_period"):
        _parse(_encode(document))
    document = _decoded()
    clone = copy.deepcopy(_items(document)[0])
    clone["metrics"]["mentions"] = 1
    clone["metrics"]["ai_search_volume"] = 1
    _items(document).append(clone)
    _result(document)["items_count"] = 13
    with pytest.raises(HistoricalParseError, match="duplicate_period"):
        _parse(_encode(document))


def test_zero_metrics_parse_as_stated_zero() -> None:
    document = _decoded()
    _items(document)[0]["metrics"]["mentions"] = 0
    _items(document)[0]["metrics"]["ai_search_volume"] = 0
    parsed = _parse(_encode(document))
    assert parsed.items is not None
    assert parsed.items[0].mentions == 0
    assert parsed.items[0].ai_search_volume == 0
    assert parsed.outcome is ParseClassification.ADMITTED


@pytest.mark.parametrize("month", [0, 13, -1])
def test_invalid_month_fails(month: int) -> None:
    document = _decoded()
    _items(document)[0]["month"] = month
    with pytest.raises(HistoricalParseError, match="invalid_period"):
        _parse(_encode(document))


@pytest.mark.parametrize("year", [0, 10000])
def test_year_outside_calendar_bounds_fails(year: int) -> None:
    document = _decoded()
    _items(document)[0]["year"] = year
    with pytest.raises(HistoricalParseError, match="invalid_period"):
        _parse(_encode(document))


def test_missing_metrics_and_metric_fields_fail() -> None:
    document = _decoded()
    del _items(document)[0]["metrics"]
    with pytest.raises(HistoricalParseError):
        _parse(_encode(document))
    document = _decoded()
    del _items(document)[0]["metrics"]["mentions"]
    with pytest.raises(HistoricalParseError):
        _parse(_encode(document))
    document = _decoded()
    del _items(document)[0]["metrics"]["ai_search_volume"]
    with pytest.raises(HistoricalParseError):
        _parse(_encode(document))
    document = _decoded()
    _items(document)[0]["metrics"] = []
    with pytest.raises(HistoricalParseError, match="wrong_type"):
        _parse(_encode(document))


@pytest.mark.parametrize("form", [b"0.101", b"0.1010", b"1.01e-1"])
def test_cost_decimal_value_ignores_numeral_spelling(form: bytes) -> None:
    raw = _fixture()
    mutated = raw.replace(b'"cost": 0.101', b'"cost": ' + form, 2)
    parsed = _parse(mutated)
    assert parsed.cost == Decimal("0.101")
    assert parsed.task_cost == Decimal("0.101")
    assert type(parsed.cost) is Decimal


def test_integer_json_cost_is_decimal() -> None:
    parsed = _parse(_fixture().replace(b'"cost": 0.101', b'"cost": 1', 1))
    assert parsed.cost == Decimal(1)
    assert type(parsed.cost) is Decimal


def test_high_precision_cost_does_not_use_binary_float() -> None:
    raw = _fixture().replace(b'"cost": 0.101', b'"cost": 0.10100000000000001', 1)
    parsed = _parse(raw)
    assert parsed.cost != Decimal("0.101")
    assert type(parsed.cost) is Decimal


def test_duplicate_json_member_invalid_utf8_bom_trailing_and_nonfinite() -> None:
    raw = _fixture()
    duplicated = raw.replace(
        b'"status_code": 20000', b'"status_code": 20000,"status_code": 20000', 1
    )
    with pytest.raises(HistoricalParseError, match="duplicate_member"):
        _parse(duplicated)
    with pytest.raises(HistoricalParseError, match="invalid_utf8"):
        _parse(b"\xff\xfe{" + raw)
    with pytest.raises(HistoricalParseError, match="utf8_bom"):
        _parse(b"\xef\xbb\xbf" + raw)
    with pytest.raises(HistoricalParseError, match="trailing_data"):
        _parse(raw + b"  true")
    with pytest.raises(HistoricalParseError, match="non_finite"):
        _parse(raw.replace(b'"cost": 0.101', b'"cost": NaN', 1))
    with pytest.raises(HistoricalParseError, match="non_finite"):
        _parse(raw.replace(b'"cost": 0.101', b'"cost": Infinity', 1))
    with pytest.raises(HistoricalParseError, match="invalid_json"):
        _parse(b"{")


def test_unknown_fields_fail_at_every_closed_object_layer() -> None:
    document = _decoded()
    document["unexpected"] = 1
    with pytest.raises(HistoricalParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["unexpected"] = 1
    with pytest.raises(HistoricalParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["data"]["unexpected"] = 1
    with pytest.raises(
        HistoricalParseError, match="unknown_field at /tasks/0/data/unexpected"
    ):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["data"]["target"][0]["unexpected"] = 1
    with pytest.raises(
        HistoricalParseError,
        match="unknown_field at /tasks/0/data/target/0/unexpected",
    ):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["unexpected"] = 1
    with pytest.raises(HistoricalParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    _items(document)[0]["unexpected"] = 1
    with pytest.raises(HistoricalParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    _items(document)[0]["metrics"]["unexpected"] = 1
    with pytest.raises(HistoricalParseError, match="unknown_field"):
        _parse(_encode(document))
    extra = dict(PARAMETERS)
    extra["unexpected"] = 1
    with pytest.raises(HistoricalParseError, match="unknown_field"):
        _parse(parameters=extra)
    extra_target = copy.deepcopy(PARAMETERS)
    target = extra_target["target"]
    assert isinstance(target, list)
    first = target[0]
    assert isinstance(first, dict)
    first["unexpected"] = 1
    with pytest.raises(HistoricalParseError, match="unknown_field"):
        _parse(parameters=extra_target)


def test_unknown_attempt_parameter_fails_before_parse() -> None:
    extra = dict(PARAMETERS)
    extra["internal_list_limit"] = 10
    with pytest.raises(HistoricalParseError, match="unknown_field"):
        _parse(parameters=extra)
    wrong_contract = dict(PARAMETERS)
    wrong_contract["contract"] = TARGET_METRICS_ADAPTER_CONTRACT
    with pytest.raises(HistoricalParseError, match="unknown_enum"):
        _parse(parameters=wrong_contract)
    missing = dict(PARAMETERS)
    del missing["date_from"]
    with pytest.raises(HistoricalParseError):
        _parse(parameters=missing)


def test_missing_or_wrong_typed_echo_fields_fail() -> None:
    document = _decoded()
    del document["tasks"][0]["data"]["function"]
    with pytest.raises(HistoricalParseError):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["data"]["api"] = 1
    with pytest.raises(HistoricalParseError, match="wrong_type"):
        _parse(_encode(document))
    document = _decoded()
    del document["tasks"][0]["data"]["date_from"]
    with pytest.raises(HistoricalParseError):
        _parse(_encode(document))


def test_provider_error_preserves_echo_and_result_count() -> None:
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 1
    error = _parse(_encode(document))
    assert error.outcome is ParseClassification.PROVIDER_ERROR
    assert error.items_count is None
    assert error.items is None
    assert error.result_count == 1
    assert error.echo is not None
    assert error.echo.function == "historical"
    assert error.request.keyword == KEYWORD
    assert error.tasks_error == 1


def test_mixed_root_task_success_fails_deterministically() -> None:
    document = _decoded()
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 1
    with pytest.raises(HistoricalParseError, match="inconsistent_status"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = 40100
    with pytest.raises(HistoricalParseError, match="inconsistent_status"):
        _parse(_encode(document))


def test_provider_error_does_not_read_result_array() -> None:
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 1
    _result(document)["unexpected"] = 1
    _result(document)["items"] = None
    _result(document)["items_count"] = 99
    error = _parse(_encode(document))
    assert error.outcome is ParseClassification.PROVIDER_ERROR
    assert error.echo is not None
    assert error.echo.function == "historical"
    assert error.result_count == 1
    assert error.items_count is None
    assert error.items is None


def test_wrong_tasks_error_fails_on_success_and_provider_error() -> None:
    document = _decoded()
    document["tasks_error"] = 1
    with pytest.raises(HistoricalParseError, match="count_mismatch"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 0
    with pytest.raises(HistoricalParseError, match="count_mismatch"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 2
    with pytest.raises(HistoricalParseError, match="count_mismatch"):
        _parse(_encode(document))


def test_result_count_fails_on_success_and_provider_error() -> None:
    document = _decoded()
    document["tasks"][0]["result_count"] = -1
    with pytest.raises(HistoricalParseError, match="invalid_number"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 1
    document["tasks"][0]["result_count"] = -1
    with pytest.raises(HistoricalParseError, match="invalid_number"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result_count"] = True
    with pytest.raises(HistoricalParseError, match="wrong_type"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 1
    document["tasks"][0]["result_count"] = 1.0
    with pytest.raises(HistoricalParseError, match="wrong_type"):
        _parse(_encode(document))


def test_task_and_result_topology_errors() -> None:
    document = _decoded()
    document["tasks"].append(copy.deepcopy(document["tasks"][0]))
    document["tasks_count"] = 2
    with pytest.raises(HistoricalParseError, match="tasks_length"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result"].append(copy.deepcopy(_result(document)))
    document["tasks"][0]["result_count"] = 2
    with pytest.raises(HistoricalParseError, match="result_length"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks_count"] = 2
    with pytest.raises(HistoricalParseError, match="count_mismatch"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result"] = []
    document["tasks"][0]["result_count"] = 0
    with pytest.raises(HistoricalParseError, match="result_length"):
        _parse(_encode(document))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("year", True),
        ("year", "2026"),
        ("year", 2026.0),
        ("month", True),
        ("month", "7"),
        ("mentions", True),
        ("mentions", "1353"),
        ("mentions", 1.5),
        ("mentions", -1),
        ("ai_search_volume", True),
        ("ai_search_volume", "1"),
        ("ai_search_volume", -1),
    ],
)
def test_point_fields_reject_bool_float_string_negative(field: str, value: object) -> None:
    document = _decoded()
    if field in {"mentions", "ai_search_volume"}:
        _items(document)[0]["metrics"][field] = value
    else:
        _items(document)[0][field] = value
    with pytest.raises(HistoricalParseError):
        _parse(_encode(document))


@pytest.mark.parametrize("value", [True, "12", 12.0, -1])
def test_items_count_rejects_non_nonneg_int(value: object) -> None:
    document = _decoded()
    _result(document)["items_count"] = value
    with pytest.raises(HistoricalParseError):
        _parse(_encode(document))


def test_existing_fixtures_remain_byte_identical() -> None:
    assert hashlib.sha256(TM_FIXTURE.read_bytes()).hexdigest() == TM_BODY_SHA256
    assert hashlib.sha256(MENTIONS_FIXTURE.read_bytes()).hexdigest() == MENTIONS_BODY_SHA256
    assert hashlib.sha256(KO_FIXTURE.read_bytes()).hexdigest() == KO_BODY_SHA256
    assert hashlib.sha256(ORGANIC_FIXTURE.read_bytes()).hexdigest() == ORGANIC_BODY_SHA256


def test_no_credentials_in_environment() -> None:
    assert os.environ.get("OBSERVATORY_DATAFORSEO_LOGIN") is None
    assert os.environ.get("OBSERVATORY_DATAFORSEO_PASSWORD") is None
