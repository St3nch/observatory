"""AI-10: Target Metrics strict parser and AI-09 conformance fixture."""

from __future__ import annotations

import copy
import hashlib
import inspect
import json
import socket
from dataclasses import fields
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from observatory.capture_event import (
    MENTIONS_ADAPTER_CONTRACT,
    ORGANIC_ADAPTER_CONTRACT,
    PAID_ADAPTER_CONTRACT,
    TARGET_METRICS_ADAPTER_CONTRACT,
)
from observatory.dataforseo_ai_optimization_search_mentions import parse_search_mentions
from observatory.dataforseo_ai_optimization_target_metrics import (
    GroupingRow,
    LocationRow,
    TargetMetricsParseError,
    parse_target_metrics,
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
AI09_BODY_BYTES = 1775
AI09_BODY_SHA256 = "7b6974704f73cff9687986a83ab14ba8ec942ccdbfde359ec7e8fde6bea8eee2"
MENTIONS_BODY_SHA256 = "8b3cd0fb0c9fa23c102696bfe6b7212396c0f7c110e9ca8ca5b8ee5af182e80a"
KO_BODY_SHA256 = "d91fdc7ab8acf429f0ff9c00bd7cdb725be1ba9585481af35d14f7c4e79a6d1c"
ORGANIC_BODY_SHA256 = "7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f"

KEYWORD = "generative engine optimization"
SOURCE_DOMAINS: tuple[tuple[str, int, int], ...] = (
    ("www.youtube.com", 1641, 1182010),
    ("www.reddit.com", 750, 326780),
    ("www.linkedin.com", 395, 445730),
    ("www.coursera.org", 308, 80860),
    ("www.semrush.com", 262, 280590),
    ("digitalmarketinginstitute.com", 249, 49930),
    ("clutch.co", 234, 222900),
    ("en.wikipedia.org", 217, 245010),
    ("firstpagesage.com", 195, 256380),
    ("thriveagency.com", 164, 97420),
)
SOURCE_MENTION_SUM = 4415
SOURCE_VOLUME_SUM = 3187610
TOTAL_MENTIONS = 3061
TOTAL_VOLUME = 2336840

PARAMETERS: dict[str, object] = {
    "contract": TARGET_METRICS_ADAPTER_CONTRACT,
    "internal_list_limit": 10,
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


def _fixture() -> bytes:
    return FIXTURE_PATH.read_bytes()


def _parse(body: bytes | None = None, parameters: dict[str, object] | None = None) -> Any:
    return parse_target_metrics(body if body is not None else _fixture(), parameters or PARAMETERS)


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


def _agg(document: dict[str, Any]) -> dict[str, Any]:
    metrics = _result(document)["aggregated_metrics"]
    assert isinstance(metrics, dict)
    return metrics


def _row(key: object, mentions: int = 1, volume: int = 2) -> dict[str, object]:
    return {"key": key, "mentions": mentions, "ai_search_volume": volume}


def test_frozen_fixture_independent_sha256_and_length() -> None:
    raw = _fixture()
    assert len(raw) == AI09_BODY_BYTES
    assert hashlib.sha256(raw).hexdigest() == AI09_BODY_SHA256
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert not raw.endswith(b"\n")
    assert Path("/home/chaz/.local/share/observatory").as_posix() not in str(FIXTURE_PATH)


def test_parser_signature_has_no_http_or_transport_input() -> None:
    names = tuple(inspect.signature(parse_target_metrics).parameters)
    assert names == ("body", "parameters")


def test_golden_parse_preserves_request_echo_and_aggregates() -> None:
    parsed = _parse()
    assert parsed.outcome is ParseClassification.ADMITTED
    assert parsed.outcome.value != "observation_admitted_empty"
    assert parsed.request.keyword == KEYWORD
    assert parsed.request.match_type == "word_match"
    assert parsed.request.search_filter == "include"
    assert parsed.request.search_scope == ("answer",)
    assert parsed.request.platform == "google"
    assert parsed.request.location_code == 2840
    assert parsed.request.language_code == "en"
    assert parsed.request.internal_list_limit == 10
    assert parsed.version == "0.1.20260806"
    assert parsed.status_code == 20000
    assert parsed.status_message == "Ok."
    assert parsed.task_status_code == 20000
    assert parsed.task_status_message == "Ok."
    assert parsed.task_id == "08240309-1463-0651-0000-7982d3d5ec07"
    assert parsed.task_path == (
        "v3",
        "ai_optimization",
        "llm_mentions",
        "target_metrics",
        "live",
    )
    assert parsed.cost == Decimal("0.101")
    assert parsed.task_cost == Decimal("0.101")
    assert type(parsed.cost) is Decimal
    assert parsed.duration == "0.8758 sec."
    assert parsed.task_duration == "0.8400 sec."
    assert parsed.duration.endswith("sec.")
    assert parsed.task_duration.endswith("sec.")
    assert parsed.tasks_count == 1
    assert parsed.tasks_error == 0
    assert parsed.result_count == 1
    assert parsed.total_count == 0
    assert parsed.offset == 0
    assert parsed.items_count == 0
    assert parsed.items is not None
    assert parsed.items.state is FieldState.STATED
    assert parsed.items.value == ()
    assert parsed.echo is not None
    assert parsed.echo.api == "ai_optimization"
    assert parsed.echo.function == "target_metrics"
    assert parsed.echo.internal_list_limit == 10
    assert parsed.echo.language_code == "en"
    assert parsed.echo.location_code == 2840
    assert parsed.echo.platform == "google"
    assert parsed.echo.target[0].keyword == KEYWORD
    assert parsed.echo.target[0].match_type == "word_match"
    assert parsed.echo.target[0].search_filter == "include"
    assert parsed.echo.target[0].search_scope == ("answer",)
    metrics = parsed.aggregated_metrics
    assert metrics is not None
    assert len(metrics.location) == 1
    assert isinstance(metrics.location[0], LocationRow)
    assert metrics.location[0].key == 2840
    assert metrics.location[0].mentions == TOTAL_MENTIONS
    assert metrics.location[0].ai_search_volume == TOTAL_VOLUME
    assert metrics.location[0].provider_array_index == 0
    assert metrics.language[0].key == "en"
    assert metrics.language[0].mentions == TOTAL_MENTIONS
    assert metrics.language[0].ai_search_volume == TOTAL_VOLUME
    assert metrics.platform[0].key == "google"
    assert metrics.platform[0].mentions == TOTAL_MENTIONS
    assert metrics.platform[0].ai_search_volume == TOTAL_VOLUME
    assert metrics.total.mentions == TOTAL_MENTIONS
    assert metrics.total.ai_search_volume == TOTAL_VOLUME
    assert [
        (row.key, row.mentions, row.ai_search_volume) for row in metrics.sources_domain
    ] == list(SOURCE_DOMAINS)
    assert [row.provider_array_index for row in metrics.sources_domain] == list(range(10))
    assert all(isinstance(row, GroupingRow) for row in metrics.sources_domain)
    assert not hasattr(metrics.sources_domain[0], "rank")
    mention_sum = sum(row.mentions for row in metrics.sources_domain)
    volume_sum = sum(row.ai_search_volume for row in metrics.sources_domain)
    assert mention_sum == SOURCE_MENTION_SUM
    assert volume_sum == SOURCE_VOLUME_SUM
    assert mention_sum > metrics.total.mentions
    assert volume_sum > metrics.total.ai_search_volume
    assert metrics.search_results_domain.state is FieldState.STATED
    assert metrics.search_results_domain.value == ()
    assert metrics.brand_entities_title.state is FieldState.STATED
    assert metrics.brand_entities_title.value == ()
    assert metrics.brand_entities_category.state is FieldState.STATED
    assert metrics.brand_entities_category.value == ()
    assert "truncated" not in {item.name for item in fields(parsed)}
    assert "truncated" not in {item.name for item in fields(metrics)}
    assert "dimensions" not in {item.name for item in fields(metrics)}


def test_echo_disagreement_does_not_replace_attempt_context() -> None:
    document = _decoded()
    document["tasks"][0]["data"]["language_code"] = "de"
    document["tasks"][0]["data"]["platform"] = "chat_gpt"
    document["tasks"][0]["data"]["internal_list_limit"] = 3
    document["tasks"][0]["data"]["target"][0]["keyword"] = "other keyword"
    parsed = _parse(_encode(document))
    assert parsed.request.keyword == KEYWORD
    assert parsed.request.language_code == "en"
    assert parsed.request.platform == "google"
    assert parsed.request.internal_list_limit == 10
    assert parsed.echo is not None
    assert parsed.echo.language_code == "de"
    assert parsed.echo.platform == "chat_gpt"
    assert parsed.echo.internal_list_limit == 3
    assert parsed.echo.target[0].keyword == "other keyword"
    assert parsed.aggregated_metrics is not None
    assert parsed.aggregated_metrics.total.mentions == TOTAL_MENTIONS


def test_grouping_key_disagreement_with_attempt_remains_visible() -> None:
    document = _decoded()
    _agg(document)["location"][0]["key"] = 2841
    _agg(document)["language"][0]["key"] = "de"
    _agg(document)["platform"][0]["key"] = "chat_gpt"
    parsed = _parse(_encode(document))
    assert parsed.request.location_code == 2840
    assert parsed.request.language_code == "en"
    assert parsed.request.platform == "google"
    assert parsed.aggregated_metrics is not None
    assert parsed.aggregated_metrics.location[0].key == 2841
    assert parsed.aggregated_metrics.language[0].key == "de"
    assert parsed.aggregated_metrics.platform[0].key == "chat_gpt"


def test_grouping_value_disagreement_with_total_parses() -> None:
    document = _decoded()
    _agg(document)["location"][0]["mentions"] = 1
    _agg(document)["language"][0]["ai_search_volume"] = 2
    _agg(document)["platform"][0]["mentions"] = 3
    parsed = _parse(_encode(document))
    metrics = parsed.aggregated_metrics
    assert metrics is not None
    assert metrics.location[0].mentions == 1
    assert metrics.language[0].ai_search_volume == 2
    assert metrics.platform[0].mentions == 3
    assert metrics.total.mentions == TOTAL_MENTIONS
    assert metrics.total.ai_search_volume == TOTAL_VOLUME


def test_overlapping_domain_sums_greater_than_total_remain_valid() -> None:
    parsed = _parse()
    metrics = parsed.aggregated_metrics
    assert metrics is not None
    assert sum(row.mentions for row in metrics.sources_domain) == SOURCE_MENTION_SUM
    assert sum(row.ai_search_volume for row in metrics.sources_domain) == SOURCE_VOLUME_SUM
    assert metrics.total.mentions < SOURCE_MENTION_SUM
    assert metrics.total.ai_search_volume < SOURCE_VOLUME_SUM


def test_source_domain_reorder_preserves_key_metrics_and_reindexes() -> None:
    parsed = _parse()
    original = [
        (row.key, row.mentions, row.ai_search_volume, row.provider_array_index)
        for row in parsed.aggregated_metrics.sources_domain
    ]
    assert [index for *_rest, index in original] == list(range(10))
    document = _decoded()
    rows = _agg(document)["sources_domain"]
    _agg(document)["sources_domain"] = list(reversed(rows))
    reordered = _parse(_encode(document))
    pairs = [
        (row.key, row.mentions, row.ai_search_volume)
        for row in reordered.aggregated_metrics.sources_domain
    ]
    assert pairs == list(reversed([item[:3] for item in original]))
    assert [
        row.provider_array_index for row in reordered.aggregated_metrics.sources_domain
    ] == list(range(10))
    assert not hasattr(reordered.aggregated_metrics.sources_domain[0], "rank")


def test_source_count_below_and_equal_to_limit_is_not_truncation() -> None:
    parsed = _parse()
    assert len(parsed.aggregated_metrics.sources_domain) == parsed.request.internal_list_limit
    assert "truncated" not in {item.name for item in fields(parsed)}
    document = _decoded()
    _agg(document)["sources_domain"] = _agg(document)["sources_domain"][:3]
    below = _parse(_encode(document))
    assert len(below.aggregated_metrics.sources_domain) == 3
    assert below.request.internal_list_limit == 10
    assert "truncated" not in {item.name for item in fields(below)}
    assert below.outcome is ParseClassification.ADMITTED
    document = _decoded()
    rows = list(_agg(document)["sources_domain"])
    rows.append(_row("above-limit.example", 1, 1))
    _agg(document)["sources_domain"] = rows
    above = _parse(_encode(document))
    assert len(above.aggregated_metrics.sources_domain) == 11
    assert above.request.internal_list_limit == 10
    assert "truncated" not in {item.name for item in fields(above)}
    assert above.outcome is ParseClassification.ADMITTED


def test_zero_totals_and_zero_metrics_are_stated_values() -> None:
    document = _decoded()
    _agg(document)["total"]["mentions"] = 0
    _agg(document)["total"]["ai_search_volume"] = 0
    _agg(document)["location"][0]["mentions"] = 0
    _agg(document)["location"][0]["ai_search_volume"] = 0
    _agg(document)["sources_domain"][0]["mentions"] = 0
    _agg(document)["sources_domain"][0]["ai_search_volume"] = 0
    parsed = _parse(_encode(document))
    assert parsed.outcome is ParseClassification.ADMITTED
    assert parsed.outcome.value != "observation_admitted_empty"
    assert parsed.aggregated_metrics.total.mentions == 0
    assert parsed.aggregated_metrics.total.ai_search_volume == 0
    assert parsed.aggregated_metrics.location[0].mentions == 0
    assert parsed.aggregated_metrics.sources_domain[0].ai_search_volume == 0
    assert parsed.items.state is FieldState.STATED
    assert parsed.items.value == ()


@pytest.mark.parametrize("form", [b"0.101", b"0.1010", b"1.01e-1"])
def test_cost_decimal_value_ignores_numeral_spelling(form: bytes) -> None:
    raw = _fixture()
    mutated = raw.replace(b'"cost":0.101', b'"cost":' + form, 2)
    parsed = _parse(mutated)
    assert parsed.cost == Decimal("0.101")
    assert parsed.task_cost == Decimal("0.101")
    assert type(parsed.cost) is Decimal


def test_integer_json_cost_is_decimal() -> None:
    parsed = _parse(_fixture().replace(b'"cost":0.101', b'"cost":1', 1))
    assert parsed.cost == Decimal(1)
    assert type(parsed.cost) is Decimal


def test_high_precision_cost_does_not_use_binary_float() -> None:
    raw = _fixture().replace(b'"cost":0.101', b'"cost":0.10100000000000001', 1)
    parsed = _parse(raw)
    assert parsed.cost != Decimal("0.101")
    assert type(parsed.cost) is Decimal


def test_duplicate_json_member_invalid_utf8_bom_trailing_and_nonfinite() -> None:
    raw = _fixture()
    duplicated = raw.replace(
        b'"status_code":20000', b'"status_code":20000,"status_code":20000', 1
    )
    with pytest.raises(TargetMetricsParseError, match="duplicate_member"):
        _parse(duplicated)
    with pytest.raises(TargetMetricsParseError, match="invalid_utf8"):
        _parse(b"\xff\xfe{" + raw)
    with pytest.raises(TargetMetricsParseError, match="utf8_bom"):
        _parse(b"\xef\xbb\xbf" + raw)
    with pytest.raises(TargetMetricsParseError, match="trailing_data"):
        _parse(raw + b"  true")
    with pytest.raises(TargetMetricsParseError, match="non_finite"):
        _parse(raw.replace(b'"cost":0.101', b'"cost":NaN', 1))
    with pytest.raises(TargetMetricsParseError, match="non_finite"):
        _parse(raw.replace(b'"cost":0.101', b'"cost":Infinity', 1))


def test_unknown_fields_fail_at_every_closed_object_layer() -> None:
    document = _decoded()
    document["unexpected"] = 1
    with pytest.raises(TargetMetricsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["unexpected"] = 1
    with pytest.raises(TargetMetricsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["data"]["unexpected"] = 1
    with pytest.raises(
        TargetMetricsParseError, match="unknown_field at /tasks/0/data/unexpected"
    ):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["data"]["target"][0]["unexpected"] = 1
    with pytest.raises(
        TargetMetricsParseError,
        match="unknown_field at /tasks/0/data/target/0/unexpected",
    ):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["unexpected"] = 1
    with pytest.raises(TargetMetricsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["unexpected"] = 1
    with pytest.raises(TargetMetricsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["location"][0]["unexpected"] = 1
    with pytest.raises(TargetMetricsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["language"][0]["unexpected"] = 1
    with pytest.raises(TargetMetricsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["platform"][0]["unexpected"] = 1
    with pytest.raises(TargetMetricsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["sources_domain"][0]["unexpected"] = 1
    with pytest.raises(TargetMetricsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["search_results_domain"] = [_row("example.com")]
    _agg(document)["search_results_domain"][0]["unexpected"] = 1
    with pytest.raises(TargetMetricsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["brand_entities_title"] = [_row("Brand")]
    _agg(document)["brand_entities_title"][0]["unexpected"] = 1
    with pytest.raises(TargetMetricsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["brand_entities_category"] = [_row("Category")]
    _agg(document)["brand_entities_category"][0]["unexpected"] = 1
    with pytest.raises(TargetMetricsParseError, match="unknown_field"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["total"]["unexpected"] = 1
    with pytest.raises(TargetMetricsParseError, match="unknown_field"):
        _parse(_encode(document))
    extra = dict(PARAMETERS)
    extra["unexpected"] = 1
    with pytest.raises(TargetMetricsParseError, match="unknown_field"):
        _parse(parameters=extra)
    extra_target = copy.deepcopy(PARAMETERS)
    target = extra_target["target"]
    assert isinstance(target, list)
    first = target[0]
    assert isinstance(first, dict)
    first["unexpected"] = 1
    with pytest.raises(TargetMetricsParseError, match="unknown_field"):
        _parse(parameters=extra_target)


def test_missing_known_fields_fail() -> None:
    document = _decoded()
    del document["status_code"]
    with pytest.raises(TargetMetricsParseError):
        _parse(_encode(document))
    document = _decoded()
    del document["tasks"][0]["data"]["platform"]
    with pytest.raises(TargetMetricsParseError):
        _parse(_encode(document))
    document = _decoded()
    del document["tasks"][0]["data"]["function"]
    with pytest.raises(TargetMetricsParseError):
        _parse(_encode(document))
    document = _decoded()
    del document["tasks"][0]["data"]["target"][0]["keyword"]
    with pytest.raises(TargetMetricsParseError):
        _parse(_encode(document))
    document = _decoded()
    del document["tasks"][0]["data"]["target"][0]["match_type"]
    with pytest.raises(TargetMetricsParseError):
        _parse(_encode(document))
    document = _decoded()
    del _result(document)["aggregated_metrics"]
    with pytest.raises(TargetMetricsParseError):
        _parse(_encode(document))
    document = _decoded()
    del _agg(document)["total"]
    with pytest.raises(TargetMetricsParseError, match="missing_field"):
        _parse(_encode(document))
    document = _decoded()
    del _agg(document)["sources_domain"]
    with pytest.raises(TargetMetricsParseError, match="missing_field"):
        _parse(_encode(document))
    document = _decoded()
    del _agg(document)["location"]
    with pytest.raises(TargetMetricsParseError, match="missing_field"):
        _parse(_encode(document))
    document = _decoded()
    del _agg(document)["language"]
    with pytest.raises(TargetMetricsParseError, match="missing_field"):
        _parse(_encode(document))
    document = _decoded()
    del _agg(document)["platform"]
    with pytest.raises(TargetMetricsParseError, match="missing_field"):
        _parse(_encode(document))
    document = _decoded()
    del _agg(document)["location"][0]["key"]
    with pytest.raises(TargetMetricsParseError):
        _parse(_encode(document))
    document = _decoded()
    del _agg(document)["language"][0]["mentions"]
    with pytest.raises(TargetMetricsParseError):
        _parse(_encode(document))
    document = _decoded()
    del _agg(document)["sources_domain"][0]["ai_search_volume"]
    with pytest.raises(TargetMetricsParseError):
        _parse(_encode(document))
    document = _decoded()
    del _agg(document)["total"]["mentions"]
    with pytest.raises(TargetMetricsParseError):
        _parse(_encode(document))
    document = _decoded()
    del _agg(document)["total"]["ai_search_volume"]
    with pytest.raises(TargetMetricsParseError):
        _parse(_encode(document))
    missing_limit = dict(PARAMETERS)
    del missing_limit["internal_list_limit"]
    with pytest.raises(TargetMetricsParseError):
        _parse(parameters=missing_limit)


def test_provider_error_and_inconsistent_status() -> None:
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 1
    error = _parse(_encode(document))
    assert error.outcome is ParseClassification.PROVIDER_ERROR
    assert error.aggregated_metrics is None
    assert error.items is None
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
    with pytest.raises(TargetMetricsParseError, match="inconsistent_status"):
        _parse(_encode(document))


def test_wrong_tasks_error_fails_on_success_and_provider_error() -> None:
    document = _decoded()
    document["tasks_error"] = 1
    with pytest.raises(TargetMetricsParseError, match="count_mismatch"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 0
    with pytest.raises(TargetMetricsParseError, match="count_mismatch"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 2
    with pytest.raises(TargetMetricsParseError, match="count_mismatch"):
        _parse(_encode(document))


def test_negative_result_count_fails_including_provider_error() -> None:
    document = _decoded()
    document["tasks"][0]["result_count"] = -1
    with pytest.raises(TargetMetricsParseError, match="invalid_number"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 1
    document["tasks"][0]["result_count"] = -1
    with pytest.raises(TargetMetricsParseError, match="invalid_number"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result_count"] = True
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = 40100
    document["tasks"][0]["status_code"] = 40100
    document["tasks_error"] = 1
    document["tasks"][0]["result_count"] = 1.0
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))


def test_task_and_result_count_errors() -> None:
    document = _decoded()
    document["tasks"].append(copy.deepcopy(document["tasks"][0]))
    document["tasks_count"] = 2
    with pytest.raises(TargetMetricsParseError, match="tasks_length"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result"].append(copy.deepcopy(_result(document)))
    document["tasks"][0]["result_count"] = 2
    with pytest.raises(TargetMetricsParseError, match="result_length"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks_count"] = 2
    with pytest.raises(TargetMetricsParseError, match="count_mismatch"):
        _parse(_encode(document))


@pytest.mark.parametrize("field", ["total_count", "offset", "items_count"])
def test_nonzero_successful_result_counts_fail(field: str) -> None:
    document = _decoded()
    _result(document)[field] = 1
    with pytest.raises(TargetMetricsParseError, match="invalid_count"):
        _parse(_encode(document))


@pytest.mark.parametrize(
    ("value", "count"),
    [
        ([], 0),
        (None, 0),
    ],
)
def test_items_empty_and_null_are_distinct_accepted_states(
    value: object, count: int
) -> None:
    document = _decoded()
    _result(document)["items"] = value
    _result(document)["items_count"] = count
    parsed = _parse(_encode(document))
    assert parsed.items is not None
    if value is None:
        assert parsed.items.state is FieldState.JSON_NULL
        assert parsed.items.value is None
    else:
        assert parsed.items.state is FieldState.STATED
        assert parsed.items.value == ()
    assert parsed.total_count == 0
    assert parsed.items_count == 0


def test_absent_items_is_distinct_from_null_and_empty() -> None:
    document = _decoded()
    del _result(document)["items"]
    parsed = _parse(_encode(document))
    assert parsed.items is not None
    assert parsed.items.state is FieldState.ABSENT
    assert parsed.items.value is None
    assert parsed.items_count == 0


def test_nonempty_and_wrong_typed_items_fail() -> None:
    document = _decoded()
    _result(document)["items"] = [{"unexpected": True}]
    _result(document)["items_count"] = 1
    with pytest.raises(TargetMetricsParseError, match="unsupported_items"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"] = {}
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"] = "[]"
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))
    document = _decoded()
    _result(document)["items"] = True
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))


@pytest.mark.parametrize(
    "name",
    ["search_results_domain", "brand_entities_title", "brand_entities_category"],
)
def test_optional_aggregate_lists_preserve_absent_null_empty_nonempty_and_wrong_type(
    name: str,
) -> None:
    document = _decoded()
    del _agg(document)[name]
    absent = _parse(_encode(document))
    field = getattr(absent.aggregated_metrics, name)
    assert field.state is FieldState.ABSENT
    assert field.value is None

    document = _decoded()
    _agg(document)[name] = None
    null = _parse(_encode(document))
    field = getattr(null.aggregated_metrics, name)
    assert field.state is FieldState.JSON_NULL
    assert field.value is None

    document = _decoded()
    _agg(document)[name] = []
    empty = _parse(_encode(document))
    field = getattr(empty.aggregated_metrics, name)
    assert field.state is FieldState.STATED
    assert field.value == ()

    document = _decoded()
    _agg(document)[name] = [_row("synthetic.example", 4, 5)]
    nonempty = _parse(_encode(document))
    field = getattr(nonempty.aggregated_metrics, name)
    assert field.state is FieldState.STATED
    assert field.value is not None
    assert len(field.value) == 1
    row = field.value[0]
    assert isinstance(row, GroupingRow)
    assert row.key == "synthetic.example"
    assert row.mentions == 4
    assert row.ai_search_volume == 5
    assert row.provider_array_index == 0

    document = _decoded()
    _agg(document)[name] = {}
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)[name] = "empty"
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))


def test_nonempty_optional_rows_are_typed_ir_not_persistence() -> None:
    document = _decoded()
    _agg(document)["search_results_domain"] = [_row("results.example", 8, 9)]
    parsed = _parse(_encode(document))
    rows = parsed.aggregated_metrics.search_results_domain.value
    assert rows is not None
    assert rows[0].key == "results.example"
    source = Path("src/observatory/dataforseo_ai_optimization_target_metrics.py").read_text(
        encoding="utf-8"
    )
    assert "psycopg" not in source
    assert "provider_recipe" not in source
    assert "observation_admitted_empty" not in source


def test_required_total_and_group_arrays_reject_null_and_wrong_shape() -> None:
    document = _decoded()
    _result(document)["aggregated_metrics"] = None
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["total"] = None
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["total"] = []
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["sources_domain"] = None
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["location"] = None
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["language"] = {}
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["platform"] = "google"
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["location"] = []
    parsed = _parse(_encode(document))
    assert parsed.aggregated_metrics.location == ()


@pytest.mark.parametrize("key", ["2840", True, 2840.5])
def test_location_key_must_be_integer(key: object) -> None:
    document = _decoded()
    _agg(document)["location"][0]["key"] = key
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))


@pytest.mark.parametrize("key", [1, True, 1.5, None])
def test_string_grouping_keys_reject_non_strings(key: object) -> None:
    document = _decoded()
    _agg(document)["sources_domain"][0]["key"] = key
    with pytest.raises(TargetMetricsParseError, match="wrong_type"):
        _parse(_encode(document))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("total_count", True),
        ("offset", 0.0),
        ("items_count", "0"),
        ("items_count", -1),
    ],
)
def test_structural_counts_reject_bool_float_string_negative(field: str, value: object) -> None:
    document = _decoded()
    _result(document)[field] = value
    with pytest.raises(TargetMetricsParseError):
        _parse(_encode(document))


@pytest.mark.parametrize("value", [-1, True, 1.5, "1"])
def test_aggregate_metrics_reject_negative_bool_float_string(value: object) -> None:
    document = _decoded()
    _agg(document)["total"]["mentions"] = value
    with pytest.raises(TargetMetricsParseError):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["sources_domain"][0]["ai_search_volume"] = value
    with pytest.raises(TargetMetricsParseError):
        _parse(_encode(document))


def test_duplicate_grouping_keys_fail_even_when_metrics_agree() -> None:
    document = _decoded()
    first = copy.deepcopy(_agg(document)["sources_domain"][0])
    second = copy.deepcopy(first)
    _agg(document)["sources_domain"] = [first, second]
    with pytest.raises(TargetMetricsParseError, match="duplicate_key"):
        _parse(_encode(document))
    document = _decoded()
    first = copy.deepcopy(_agg(document)["sources_domain"][0])
    second = copy.deepcopy(first)
    second["mentions"] = 1
    second["ai_search_volume"] = 1
    _agg(document)["sources_domain"] = [first, second]
    with pytest.raises(TargetMetricsParseError, match="duplicate_key"):
        _parse(_encode(document))
    document = _decoded()
    clone = copy.deepcopy(_agg(document)["location"][0])
    _agg(document)["location"] = [_agg(document)["location"][0], clone]
    with pytest.raises(TargetMetricsParseError, match="duplicate_key"):
        _parse(_encode(document))
    document = _decoded()
    _agg(document)["search_results_domain"] = [
        _row("dup.example", 1, 1),
        _row("dup.example", 1, 1),
    ]
    with pytest.raises(TargetMetricsParseError, match="duplicate_key"):
        _parse(_encode(document))


def test_existing_fixtures_and_parsers_unchanged() -> None:
    assert hashlib.sha256(MENTIONS_FIXTURE.read_bytes()).hexdigest() == MENTIONS_BODY_SHA256
    assert hashlib.sha256(KO_FIXTURE.read_bytes()).hexdigest() == KO_BODY_SHA256
    assert hashlib.sha256(ORGANIC_FIXTURE.read_bytes()).hexdigest() == ORGANIC_BODY_SHA256
    mentions = parse_search_mentions(
        MENTIONS_FIXTURE.read_bytes(),
        {
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
        },
    )
    assert mentions.outcome is ParseClassification.ADMITTED
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
    assert "parse_target_metrics" not in Path(
        "src/observatory/dataforseo_keyword_overview.py"
    ).read_text(encoding="utf-8")
    assert "parse_target_metrics" not in Path(
        "src/observatory/dataforseo_google_organic.py"
    ).read_text(encoding="utf-8")
    assert "parse_target_metrics" not in Path(
        "src/observatory/dataforseo_ai_optimization_search_mentions.py"
    ).read_text(encoding="utf-8")
    assert TARGET_METRICS_ADAPTER_CONTRACT == (
        "dataforseo-ai-optimization-llm-mentions-target-metrics-live-paid-probe-v1"
    )
