"""API-01 helper invariants. Not a substitute for route tests."""

from __future__ import annotations

import pytest

from observatory.provider_history import (
    HISTORY_LIMIT_MAX,
    OUTER_HISTORY_KEYS,
    HistoryListEnvelope,
    history_list_response,
)


def test_envelope_math_and_closed_key_set() -> None:
    empty = history_list_response(
        provider="dataforseo",
        adapter_contract="adapter",
        requested_keyword="kw",
        derivation_version_id="ab" * 32,
        recipe_resolution="selected",
        observation_kinds=("kind.v1",),
        captures=(),
        total_matching=0,
        limit=20,
        order="asc",
    )
    assert set(empty) == OUTER_HISTORY_KEYS
    assert empty["total_matching"] == 0
    assert empty["returned_count"] == 0
    assert empty["has_more"] is False
    assert empty["captures"] == []

    one = {"capture_id": "aa" * 32, "ranked_results": [1, 2, 3]}
    truncated = history_list_response(
        provider="dataforseo",
        adapter_contract="adapter",
        requested_keyword="kw",
        derivation_version_id="ab" * 32,
        recipe_resolution="pinned",
        observation_kinds=("kind.v1",),
        captures=(one,),
        total_matching=4,
        limit=1,
        order="desc",
    )
    assert truncated["total_matching"] == 4
    assert truncated["returned_count"] == 1
    assert truncated["has_more"] is True
    projected = truncated["captures"]
    assert isinstance(projected, list)
    assert projected[0] is one
    assert one["ranked_results"] == [1, 2, 3]


def test_envelope_rejects_impossible_counts() -> None:
    row = {"capture_id": "aa" * 32}
    with pytest.raises(ValueError, match="exceeds total_matching"):
        history_list_response(
            provider="dataforseo",
            adapter_contract="adapter",
            requested_keyword="kw",
            derivation_version_id="ab" * 32,
            recipe_resolution="selected",
            observation_kinds=(),
            captures=(row, row),
            total_matching=1,
            limit=20,
            order="asc",
        )
    with pytest.raises(ValueError, match="exceeds applied limit"):
        history_list_response(
            provider="dataforseo",
            adapter_contract="adapter",
            requested_keyword="kw",
            derivation_version_id="ab" * 32,
            recipe_resolution="selected",
            observation_kinds=(),
            captures=(row, row),
            total_matching=2,
            limit=1,
            order="asc",
        )
    with pytest.raises(ValueError, match="accepted outer history bound"):
        history_list_response(
            provider="dataforseo",
            adapter_contract="adapter",
            requested_keyword="kw",
            derivation_version_id="ab" * 32,
            recipe_resolution="selected",
            observation_kinds=(),
            captures=(),
            total_matching=0,
            limit=HISTORY_LIMIT_MAX + 1,
            order="asc",
        )


def test_typed_model_passes_nested_mapping_through() -> None:
    nested = {
        "capture_id": "aa" * 32,
        "odd_key": True,
        "volume": 3055,
        "child": {"state": "stated", "value": "keep"},
    }
    payload = history_list_response(
        provider="dataforseo",
        adapter_contract="adapter",
        requested_keyword="kw",
        derivation_version_id="ab" * 32,
        recipe_resolution="selected",
        observation_kinds=("kind.v1",),
        captures=(nested,),
        total_matching=1,
        limit=20,
        order="asc",
    )
    dumped = HistoryListEnvelope.model_validate(payload).model_dump()
    assert dumped["captures"][0] == nested
    assert dumped["captures"][0]["odd_key"] is True
    assert dumped["captures"][0]["volume"] == 3055
