"""PF-05: DataForSEO Keyword Overview strict parser and PF-03 conformance fixture."""

from __future__ import annotations

import copy
import hashlib
import json
import socket
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from observatory.capture_event import PAID_ADAPTER_CONTRACT
from observatory.dataforseo_keyword_overview import (
    CORE_RECIPE,
    CORE_RECIPE_ID,
    COVERAGE_KIND,
    METRICS_KIND,
    FieldState,
    KeywordOverviewParseError,
    ParseClassification,
    keyword_overview_core_recipe,
    parse_keyword_overview,
)
from observatory.provider_recipe import (
    recipe_bytes,
    recipe_derivation_version_id,
    validate_recipe,
)

FIXTURE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_keyword_overview_pf03.json"
)
RECIPE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_keyword_overview_core_recipe.jcs"
)
PF03_BODY_SHA256 = "d91fdc7ab8acf429f0ff9c00bd7cdb725be1ba9585481af35d14f7c4e79a6d1c"
PF03_BODY_BYTES = 26270
CORE_RECIPE_SHA256 = "319af798f3e0b3e5fe4579539442c4ca5d384b683e1f4bce0f7a1b3e26cd5908"
CORE_RECIPE_BYTE_LENGTH = 1662

REQUESTED = (
    "seo api",
    "keyword research",
    "local seo",
    "generative engine optimization",
    "ai search optimization",
)
PARAMETERS: dict[str, object] = {
    "contract": PAID_ADAPTER_CONTRACT,
    "include_clickstream_data": False,
    "include_serp_info": False,
    "keywords": list(REQUESTED),
    "language_code": "en",
    "location_code": 2840,
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
    payload = body if body is not None else _fixture()
    return parse_keyword_overview(payload, parameters or PARAMETERS)


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


def _by_keyword(parsed: Any) -> dict[str, Any]:
    return {row.requested_keyword: row for row in parsed.items}


def test_frozen_fixture_independent_sha256_and_length() -> None:
    raw = _fixture()
    assert not raw.endswith(b"\n") or raw[-2:] != b"\n\n"
    assert len(raw) == PF03_BODY_BYTES
    assert hashlib.sha256(raw).hexdigest() == PF03_BODY_SHA256


def test_pf03_parses_all_requested_keywords_independent_of_item_order() -> None:
    parsed = _parse()
    assert parsed.outcome is ParseClassification.ADMITTED
    assert parsed.requested_keywords == REQUESTED
    assert [row.requested_keyword for row in parsed.items] == list(REQUESTED)
    assert [row.returned_keyword.value for row in parsed.items] == list(REQUESTED)
    assert all(row.covered for row in parsed.items)
    reordered = _decoded()
    items = reordered["tasks"][0]["result"][0]["items"]
    reordered["tasks"][0]["result"][0]["items"] = list(reversed(items))
    again = _parse(_encode(reordered))
    first = _by_keyword(parsed)
    second = _by_keyword(again)
    assert first.keys() == second.keys()
    for keyword in REQUESTED:
        assert first[keyword].keyword_info.value.search_volume.value == (
            second[keyword].keyword_info.value.search_volume.value
        )


def test_pf03_preserves_quirks_decimals_times_and_monthly_counts() -> None:
    parsed = _parse()
    rows = _by_keyword(parsed)
    seo = rows["seo api"]
    local = rows["local seo"]
    ai = rows["ai search optimization"]
    assert seo.keyword_info.value.search_volume.value == 480
    assert seo.keyword_info.value.high_top_of_page_bid.value == Decimal(39)
    assert seo.keyword_info.value.cpc.value == Decimal("52.05")
    assert seo.keyword_properties.value.detected_language.value == "id"
    assert seo.keyword_properties.value.is_another_language.value is True
    assert parsed.language_code == "en"
    assert seo.keyword_properties.value.detected_language.value != parsed.language_code
    assert seo.search_intent_info.value.foreign_intent.state is FieldState.STATED
    assert seo.search_intent_info.value.foreign_intent.value == ("informational",)
    assert local.keyword_properties.value.detected_language.value == "id"
    assert local.keyword_properties.value.core_keyword.value == "localized seo"
    assert ai.keyword_info.value.search_volume.value == 1300
    assert ai.keyword_info.value.competition.value == Decimal("0.43")
    assert ai.keyword_info.value.search_volume_trend.value.monthly.value == 23
    assert ai.keyword_info.value.search_volume_trend.value.quarterly.value == 0
    assert ai.keyword_info.value.search_volume_trend.value.yearly.value == 82
    assert ai.avg_backlinks_info.value.backlinks.value == Decimal("1571.3")
    assert ai.avg_backlinks_info.value.dofollow.value == Decimal("839.7")
    assert ai.keyword_info.value.last_updated_time.value == "2026-07-16 07:54:24 +00:00"
    assert ai.avg_backlinks_info.value.last_updated_time.value == "2026-08-01 07:28:00 +00:00"
    assert ai.search_intent_info.value.last_updated_time.value == "2026-04-29 01:54:23 +00:00"
    assert parsed.execution_time.value == "0.0897 sec."
    assert parsed.task_execution_time.value == "0.0503 sec."
    assert parsed.cost.value == Decimal("0.0126")
    counts = {
        keyword: len(row.keyword_info.value.monthly_searches.value)
        for keyword, row in rows.items()
    }
    assert counts == {
        "ai search optimization": 85,
        "generative engine optimization": 78,
        "keyword research": 93,
        "local seo": 93,
        "seo api": 92,
    }
    zeros = [
        point
        for point in ai.keyword_info.value.monthly_searches.value
        if point.search_volume == 0
    ]
    assert zeros
    assert (2019, 6, 0) in {(p.year, p.month, p.search_volume) for p in zeros}
    assert seo.serp_info.state is FieldState.NOT_REQUESTED
    assert seo.clickstream_keyword_info.state is FieldState.NOT_REQUESTED
    assert seo.keyword_info_normalized_with_clickstream.state is FieldState.NOT_REQUESTED
    assert seo.keyword_info_normalized_with_bing.state is FieldState.JSON_NULL
    research = rows["keyword research"]
    assert research.keyword_properties.value.core_keyword.state is FieldState.JSON_NULL
    assert rows["keyword research"].search_intent_info.value.foreign_intent.state is (
        FieldState.JSON_NULL
    )


def test_duplicate_unrequested_and_omitted_reconciliation() -> None:
    document = _decoded()
    items = document["tasks"][0]["result"][0]["items"]
    items.append(copy.deepcopy(items[0]))
    document["tasks"][0]["result"][0]["items_count"] = len(items)
    with pytest.raises(KeywordOverviewParseError, match="duplicate"):
        _parse(_encode(document))

    document = _decoded()
    extra = copy.deepcopy(document["tasks"][0]["result"][0]["items"][0])
    extra["keyword"] = "unrequested keyword"
    document["tasks"][0]["result"][0]["items"].append(extra)
    document["tasks"][0]["result"][0]["items_count"] = 6
    with pytest.raises(KeywordOverviewParseError, match="unrequested"):
        _parse(_encode(document))

    document = _decoded()
    remaining = [
        item
        for item in document["tasks"][0]["result"][0]["items"]
        if item["keyword"] != "local seo"
    ]
    document["tasks"][0]["result"][0]["items"] = remaining
    document["tasks"][0]["result"][0]["items_count"] = 4
    parsed = _parse(_encode(document))
    omitted = _by_keyword(parsed)["local seo"]
    assert omitted.covered is False
    assert omitted.returned_keyword.state is FieldState.ABSENT


def test_synthetic_normalization_collision_fails() -> None:
    document = _decoded()
    document["tasks"][0]["result"][0]["items"] = [
        copy.deepcopy(document["tasks"][0]["result"][0]["items"][0])
    ]
    document["tasks"][0]["result"][0]["items"][0]["keyword"] = "seo api"
    document["tasks"][0]["result"][0]["items_count"] = 1
    parameters = dict(PARAMETERS)
    parameters["keywords"] = ["seo api", "SEO API"]
    with pytest.raises(KeywordOverviewParseError, match="collision"):
        _parse(_encode(document), parameters)


def test_count_and_shape_failures() -> None:
    document = _decoded()
    document["tasks"][0]["result"][0]["items_count"] = 4
    with pytest.raises(KeywordOverviewParseError, match="items_count"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result_count"] = 2
    with pytest.raises(KeywordOverviewParseError, match="result_count"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"].append(copy.deepcopy(document["tasks"][0]))
    document["tasks_count"] = 2
    with pytest.raises(KeywordOverviewParseError, match="exactly one task"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result"].append(copy.deepcopy(document["tasks"][0]["result"][0]))
    document["tasks"][0]["result_count"] = 2
    with pytest.raises(KeywordOverviewParseError, match="exactly one result"):
        _parse(_encode(document))


def test_items_missing_null_and_empty_no_data() -> None:
    document = _decoded()
    del document["tasks"][0]["result"][0]["items"]
    with pytest.raises(KeywordOverviewParseError, match="items missing"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result"][0]["items"] = None
    with pytest.raises(KeywordOverviewParseError, match="JSON null"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result"][0]["items"] = []
    document["tasks"][0]["result"][0]["items_count"] = 0
    parsed = _parse(_encode(document))
    assert parsed.outcome is ParseClassification.ADMITTED
    assert all(row.covered is False for row in parsed.items)
    assert len(parsed.items) == 5


def test_status_combinations() -> None:
    document = _decoded()
    document["tasks"][0]["status_code"] = 40102
    parsed = _parse(_encode(document))
    assert parsed.outcome is ParseClassification.PROVIDER_ERROR
    assert parsed.items == ()
    document = _decoded()
    document["status_code"] = 40102
    with pytest.raises(KeywordOverviewParseError, match="inconsistent"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = 40102
    document["tasks"][0]["status_code"] = 40102
    parsed = _parse(_encode(document))
    assert parsed.outcome is ParseClassification.PROVIDER_ERROR


def test_required_envelope_status_and_counts_fail_when_missing_or_null() -> None:
    document = _decoded()
    del document["status_code"]
    with pytest.raises(KeywordOverviewParseError, match="status_code"):
        _parse(_encode(document))
    document = _decoded()
    document["status_code"] = None
    with pytest.raises(KeywordOverviewParseError, match="status_code"):
        _parse(_encode(document))
    document = _decoded()
    del document["tasks"][0]["status_code"]
    with pytest.raises(KeywordOverviewParseError, match="status_code"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["status_code"] = None
    with pytest.raises(KeywordOverviewParseError, match="status_code"):
        _parse(_encode(document))
    document = _decoded()
    del document["tasks_count"]
    with pytest.raises(KeywordOverviewParseError, match="tasks_count"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks_error"] = None
    with pytest.raises(KeywordOverviewParseError, match="tasks_error"):
        _parse(_encode(document))
    document = _decoded()
    del document["tasks"][0]["result_count"]
    with pytest.raises(KeywordOverviewParseError, match="result_count"):
        _parse(_encode(document))
    document = _decoded()
    del document["tasks"][0]["result"][0]["items_count"]
    with pytest.raises(KeywordOverviewParseError, match="items_count"):
        _parse(_encode(document))


def test_duplicate_member_nonfinite_utf8_bom_and_trailing() -> None:
    raw = _fixture()
    mutated = raw.replace(b'"se_type":"google"', b'"se_type":"google","se_type":"bing"', 1)
    with pytest.raises(KeywordOverviewParseError, match="duplicate"):
        _parse(mutated)
    mutated = raw.replace(b'"cost":0.0126', b'"cost":NaN', 1)
    with pytest.raises(KeywordOverviewParseError, match="finite"):
        _parse(mutated)
    mutated = raw.replace(b'"cost":0.0126', b'"cost":Infinity', 1)
    with pytest.raises(KeywordOverviewParseError, match="finite"):
        _parse(mutated)
    mutated = raw.replace(b'"cost":0.0126', b'"cost":-Infinity', 1)
    with pytest.raises(KeywordOverviewParseError, match="finite"):
        _parse(mutated)
    with pytest.raises(KeywordOverviewParseError, match="BOM"):
        _parse(b"\xef\xbb\xbf" + raw)
    with pytest.raises(KeywordOverviewParseError, match="UTF-8"):
        _parse(raw[:20] + b"\xff" + raw[21:])
    with pytest.raises(KeywordOverviewParseError, match="follows"):
        _parse(raw + b"  trailing")


def test_decimal_lexical_forms_and_high_precision() -> None:
    raw = _fixture()
    as_int = raw.replace(b'"cpc":60.62', b'"cpc":1300', 1)
    as_decimal = raw.replace(b'"cpc":60.62', b'"cpc":1300.0', 1)
    precise = raw.replace(b'"cpc":60.62', b'"cpc":1.234567890123456789', 1)
    first = _by_keyword(_parse(as_int))["ai search optimization"]
    second = _by_keyword(_parse(as_decimal))["ai search optimization"]
    third = _by_keyword(_parse(precise))["ai search optimization"]
    assert first.keyword_info.value.cpc.value == Decimal(1300)
    assert second.keyword_info.value.cpc.value == Decimal("1300.0")
    assert first.keyword_info.value.cpc.value == second.keyword_info.value.cpc.value
    assert third.keyword_info.value.cpc.value == Decimal("1.234567890123456789")
    assert third.keyword_info.value.cpc.value != Decimal(str(float("1.234567890123456789")))


def test_timestamp_and_period_failures() -> None:
    raw = _fixture()
    with pytest.raises(KeywordOverviewParseError, match="timestamp"):
        _parse(raw.replace(b"2026-07-16 07:54:24 +00:00", b"2026-07-16T07:54:24Z", 1))
    with pytest.raises(KeywordOverviewParseError, match="timestamp"):
        _parse(raw.replace(b"2026-07-16 07:54:24 +00:00", b"2026-99-99 99:99:99 +00:00", 1))
    with pytest.raises(KeywordOverviewParseError, match="timestamp"):
        _parse(raw.replace(b"2026-07-16 07:54:24 +00:00", b"2026-02-30 07:54:24 +00:00", 1))
    with pytest.raises(KeywordOverviewParseError, match="timestamp"):
        _parse(raw.replace(b"2026-07-16 07:54:24 +00:00", b"2026-07-16 24:00:00 +00:00", 1))
    document = _decoded()
    point = document["tasks"][0]["result"][0]["items"][0]["keyword_info"]["monthly_searches"][0]
    point["month"] = 0
    with pytest.raises(KeywordOverviewParseError, match="month"):
        _parse(_encode(document))
    document = _decoded()
    point = document["tasks"][0]["result"][0]["items"][0]["keyword_info"]["monthly_searches"][0]
    point["month"] = 13
    with pytest.raises(KeywordOverviewParseError, match="month"):
        _parse(_encode(document))
    document = _decoded()
    point = document["tasks"][0]["result"][0]["items"][0]["keyword_info"]["monthly_searches"][0]
    point["year"] = 1999
    with pytest.raises(KeywordOverviewParseError, match="year"):
        _parse(_encode(document))
    document = _decoded()
    series = document["tasks"][0]["result"][0]["items"][0]["keyword_info"]["monthly_searches"]
    series.append(copy.deepcopy(series[0]))
    with pytest.raises(KeywordOverviewParseError, match="duplicate"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result"][0]["items"][0]["keyword_info"]["monthly_searches"][0][
        "search_volume"
    ] = -1
    with pytest.raises(KeywordOverviewParseError, match="negative"):
        _parse(_encode(document))


def test_null_absent_timestamp_and_unknown_fields() -> None:
    document = _decoded()
    document["tasks"][0]["result"][0]["items"][0]["keyword_info"]["last_updated_time"] = None
    parsed = _parse(_encode(document))
    field = _by_keyword(parsed)["ai search optimization"].keyword_info.value.last_updated_time
    assert field.state is FieldState.JSON_NULL
    document = _decoded()
    del document["tasks"][0]["result"][0]["items"][0]["keyword_info"]["last_updated_time"]
    parsed = _parse(_encode(document))
    field = _by_keyword(parsed)["ai search optimization"].keyword_info.value.last_updated_time
    assert field.state is FieldState.ABSENT
    document = _decoded()
    document["tasks"][0]["result"][0]["items"][0]["keyword_info"]["unexpected"] = 1
    parsed = _parse(_encode(document))
    assert any(item.code == "unknown_extension_field" for item in parsed.diagnostics)
    volume = _by_keyword(parsed)["ai search optimization"].keyword_info.value.search_volume.value
    assert volume == 1300
    document = _decoded()
    document["tasks"][0]["result"][0]["items"][0]["keyword_info"]["monthly_searches"][0][
        "unexpected"
    ] = 1
    with pytest.raises(KeywordOverviewParseError, match="closed"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result"][0]["items"][0]["keyword_info"]["search_volume_trend"][
        "unexpected"
    ] = 1
    with pytest.raises(KeywordOverviewParseError, match="closed"):
        _parse(_encode(document))


def test_known_field_type_drift_fails() -> None:
    raw = _fixture()
    with pytest.raises(KeywordOverviewParseError, match="integer"):
        _parse(raw.replace(b'"search_volume":1300', b'"search_volume":"1300"', 1))


def test_unknown_enum_and_populated_disabled_enrichment() -> None:
    document = _decoded()
    document["tasks"][0]["result"][0]["items"][0]["keyword_info"]["competition_level"] = "EXTREME"
    with pytest.raises(KeywordOverviewParseError, match="enum"):
        _parse(_encode(document))
    document = _decoded()
    document["tasks"][0]["result"][0]["items"][0]["serp_info"] = {"se_type": "google"}
    with pytest.raises(KeywordOverviewParseError, match="request-disabled"):
        _parse(_encode(document))


def test_core_recipe_published_digest_and_kinds() -> None:
    published = RECIPE_PATH.read_bytes()
    assert not published.endswith(b"\n")
    assert len(published) == CORE_RECIPE_BYTE_LENGTH
    independent = hashlib.sha256(published).hexdigest()
    assert independent == CORE_RECIPE_SHA256
    assert CORE_RECIPE_ID == CORE_RECIPE_SHA256
    assert recipe_bytes(keyword_overview_core_recipe()) == published
    assert recipe_derivation_version_id(CORE_RECIPE) == CORE_RECIPE_SHA256
    admission = validate_recipe(CORE_RECIPE)["admission"]
    assert isinstance(admission, dict)
    outcomes = admission["capture_outcomes"]
    assert isinstance(outcomes, list)
    assert "observation_admitted_empty" in outcomes
    assert validate_recipe(CORE_RECIPE)["observation_kinds"] == [COVERAGE_KIND, METRICS_KIND]
    identity = validate_recipe(CORE_RECIPE)["observation_identity"]
    assert isinstance(identity, dict)
    kind_rows = identity["kinds"]
    assert isinstance(kind_rows, list)
    kinds = {
        item["observation_kind"] for item in kind_rows if isinstance(item, dict)
    }
    assert kinds == {COVERAGE_KIND, METRICS_KIND}
    assert "dataforseo.google.keyword_overview.monthly_search_volume.v1" not in kinds
    assert CORE_RECIPE["provider"] == "dataforseo"
    assert CORE_RECIPE["adapter_contract"] == PAID_ADAPTER_CONTRACT
