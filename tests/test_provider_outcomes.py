"""API-02 helper invariants. Not a substitute for route tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from observatory.provider_outcomes import (
    OUTCOMES_LIMIT_MAX,
    OUTER_OUTCOMES_KEYS,
    KeywordOverviewOutcomesEnvelope,
    outcomes_list_response,
)


def test_outcomes_envelope_math_and_closed_key_set() -> None:
    empty = outcomes_list_response(
        provider="dataforseo",
        adapter_contract="adapter",
        requested_keyword="kw",
        derivation_version_id="ab" * 32,
        recipe_resolution="selected",
        observation_kinds=("kind.v1",),
        outcomes=(),
        total_matching=0,
        limit=20,
        order="asc",
    )
    assert set(empty) == OUTER_OUTCOMES_KEYS
    assert empty["total_matching"] == 0
    assert empty["returned_count"] == 0
    assert empty["has_more"] is False
    assert empty["outcomes"] == []

    one = {"attempt_id": "aa" * 32, "request": {"keywords": ["kw"]}}
    truncated = outcomes_list_response(
        provider="dataforseo",
        adapter_contract="adapter",
        requested_keyword="kw",
        derivation_version_id="ab" * 32,
        recipe_resolution="pinned",
        observation_kinds=("kind.v1",),
        outcomes=(one,),
        total_matching=4,
        limit=1,
        order="desc",
    )
    assert truncated["total_matching"] == 4
    assert truncated["returned_count"] == 1
    assert truncated["has_more"] is True
    projected = truncated["outcomes"]
    assert isinstance(projected, list)
    assert projected[0] is one
    assert one["request"] == {"keywords": ["kw"]}


def test_outcomes_envelope_rejects_impossible_counts() -> None:
    row = {"attempt_id": "aa" * 32}
    with pytest.raises(ValueError, match="exceeds total_matching"):
        outcomes_list_response(
            provider="dataforseo",
            adapter_contract="adapter",
            requested_keyword="kw",
            derivation_version_id="ab" * 32,
            recipe_resolution="selected",
            observation_kinds=(),
            outcomes=(row, row),
            total_matching=1,
            limit=20,
            order="asc",
        )
    with pytest.raises(ValueError, match="exceeds applied limit"):
        outcomes_list_response(
            provider="dataforseo",
            adapter_contract="adapter",
            requested_keyword="kw",
            derivation_version_id="ab" * 32,
            recipe_resolution="selected",
            observation_kinds=(),
            outcomes=(row, row),
            total_matching=2,
            limit=1,
            order="asc",
        )
    with pytest.raises(ValueError, match="outside the accepted"):
        outcomes_list_response(
            provider="dataforseo",
            adapter_contract="adapter",
            requested_keyword="kw",
            derivation_version_id="ab" * 32,
            recipe_resolution="selected",
            observation_kinds=(),
            outcomes=(),
            total_matching=0,
            limit=OUTCOMES_LIMIT_MAX + 1,
            order="asc",
        )


def test_keyword_overview_envelope_model_forbids_extra_item_keys() -> None:
    with pytest.raises(ValidationError):
        KeywordOverviewOutcomesEnvelope.model_validate(
            {
                "provider": "dataforseo",
                "adapter_contract": "adapter",
                "requested_keyword": "kw",
                "derivation_version_id": "ab" * 32,
                "recipe_resolution": "selected",
                "observation_kinds": [],
                "total_matching": 0,
                "returned_count": 0,
                "limit": 20,
                "order": "asc",
                "has_more": False,
                "outcomes": [],
                "captures": [],
            }
        )
