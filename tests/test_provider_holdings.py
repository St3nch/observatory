"""API-03 helper invariants. Not a substitute for route tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from observatory.evidence_store import IntegrityError
from observatory.provider_holdings import (
    HOLDINGS_LIMIT_MAX,
    OUTER_HOLDINGS_KEYS,
    HoldingsAttempt,
    KeywordOverviewHoldingsEnvelope,
    assert_unique_holdings_groups,
    holdings_item,
    holdings_list_response,
)


def test_holdings_envelope_math_and_closed_key_set() -> None:
    empty = holdings_list_response(
        provider="dataforseo",
        adapter_contract="adapter",
        holdings=(),
        total_matching=0,
        limit=20,
        order="asc",
    )
    assert set(empty) == OUTER_HOLDINGS_KEYS
    assert empty["total_matching"] == 0
    assert empty["returned_count"] == 0
    assert empty["has_more"] is False
    assert empty["holdings"] == []
    assert "requested_keyword" not in empty
    assert "derivation_version_id" not in empty

    one = {"requested_keyword": "kw", "request": {"keywords": ["kw"]}}
    truncated = holdings_list_response(
        provider="dataforseo",
        adapter_contract="adapter",
        holdings=(one,),
        total_matching=4,
        limit=1,
        order="desc",
    )
    assert truncated["total_matching"] == 4
    assert truncated["returned_count"] == 1
    assert truncated["has_more"] is True
    projected = truncated["holdings"]
    assert isinstance(projected, list)
    assert projected[0] is one


def test_holdings_item_counts_and_null_request_times() -> None:
    unresolved = holdings_item(
        requested_keyword="kw",
        request={"keywords": ["kw"], "location_code": 2840},
        members=(
            HoldingsAttempt(
                attempt_id="aa" * 32,
                authorized_at="2026-08-16T21:37:00.000000Z",
                request_started_at=None,
            ),
        ),
    )
    assert unresolved["attempt_count"] == 1
    assert unresolved["capture_count"] == 0
    assert unresolved["unresolved_count"] == 1
    assert unresolved["first_request_started_at"] is None
    assert unresolved["last_request_started_at"] is None

    mixed = holdings_item(
        requested_keyword="kw",
        request={"keywords": ["kw"]},
        members=(
            HoldingsAttempt(
                attempt_id="aa" * 32,
                authorized_at="2026-08-16T21:37:00.000000Z",
                request_started_at=None,
            ),
            HoldingsAttempt(
                attempt_id="bb" * 32,
                authorized_at="2026-08-16T21:38:00.000000Z",
                request_started_at="2026-08-16T21:38:01.100000Z",
            ),
        ),
    )
    assert mixed["attempt_count"] == 2
    assert mixed["capture_count"] == 1
    assert mixed["unresolved_count"] == 1
    assert mixed["first_authorized_at"] == "2026-08-16T21:37:00.000000Z"
    assert mixed["last_authorized_at"] == "2026-08-16T21:38:00.000000Z"
    assert mixed["first_request_started_at"] == "2026-08-16T21:38:01.100000Z"
    assert mixed["last_request_started_at"] == "2026-08-16T21:38:01.100000Z"


def test_holdings_order_fails_closed_on_duplicate_group_identity() -> None:
    item = {"requested_keyword": "kw"}
    key = ("kw", ("kw",), 2840)
    with pytest.raises(IntegrityError, match="duplicate Holdings group identity"):
        assert_unique_holdings_groups(((key, item), (key, item)))


def test_holdings_envelope_rejects_impossible_counts() -> None:
    row = {"requested_keyword": "kw"}
    with pytest.raises(ValueError, match="exceeds total_matching"):
        holdings_list_response(
            provider="dataforseo",
            adapter_contract="adapter",
            holdings=(row, row),
            total_matching=1,
            limit=20,
            order="asc",
        )
    with pytest.raises(ValueError, match="exceeds applied limit"):
        holdings_list_response(
            provider="dataforseo",
            adapter_contract="adapter",
            holdings=(row, row),
            total_matching=2,
            limit=1,
            order="asc",
        )
    with pytest.raises(ValueError, match="outside the accepted"):
        holdings_list_response(
            provider="dataforseo",
            adapter_contract="adapter",
            holdings=(),
            total_matching=0,
            limit=HOLDINGS_LIMIT_MAX + 1,
            order="asc",
        )


def test_holdings_envelope_model_forbids_recipe_and_outcome_keys() -> None:
    with pytest.raises(ValidationError):
        KeywordOverviewHoldingsEnvelope.model_validate(
            {
                "provider": "dataforseo",
                "adapter_contract": "adapter",
                "total_matching": 0,
                "returned_count": 0,
                "limit": 20,
                "order": "asc",
                "has_more": False,
                "holdings": [],
                "derivation_version_id": "ab" * 32,
            }
        )


def test_holdings_models_enforce_count_and_time_bounds() -> None:
    empty = {
        "provider": "dataforseo",
        "adapter_contract": "adapter",
        "total_matching": 0,
        "returned_count": 0,
        "limit": 20,
        "order": "asc",
        "has_more": False,
        "holdings": [],
    }
    KeywordOverviewHoldingsEnvelope.model_validate(empty)
    with pytest.raises(ValidationError):
        KeywordOverviewHoldingsEnvelope.model_validate({**empty, "limit": 0})
    with pytest.raises(ValidationError):
        KeywordOverviewHoldingsEnvelope.model_validate({**empty, "limit": 101})
    with pytest.raises(ValidationError):
        KeywordOverviewHoldingsEnvelope.model_validate({**empty, "total_matching": -1})

    item = {
        "requested_keyword": "kw",
        "request": {
            "keywords": ["kw"],
            "location_code": 2840,
            "language_code": "en",
            "include_serp_info": False,
            "include_clickstream_data": False,
        },
        "attempt_count": 1,
        "capture_count": 0,
        "unresolved_count": 1,
        "first_authorized_at": "2026-08-16T21:37:00.000000Z",
        "last_authorized_at": "2026-08-16T21:37:00.000000Z",
        "first_request_started_at": None,
        "last_request_started_at": None,
    }
    KeywordOverviewHoldingsEnvelope.model_validate({**empty, "holdings": [item]})
    with pytest.raises(ValidationError):
        KeywordOverviewHoldingsEnvelope.model_validate(
            {**empty, "holdings": [{**item, "attempt_count": 0}]}
        )
    with pytest.raises(ValidationError):
        KeywordOverviewHoldingsEnvelope.model_validate(
            {**empty, "holdings": [{**item, "attempt_count": 2, "unresolved_count": 0}]}
        )
    with pytest.raises(ValidationError):
        KeywordOverviewHoldingsEnvelope.model_validate(
            {
                **empty,
                "holdings": [
                    {
                        **item,
                        "first_request_started_at": "2026-08-16T21:37:01.100000Z",
                        "last_request_started_at": "2026-08-16T21:37:01.100000Z",
                    }
                ],
            }
        )
