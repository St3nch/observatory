"""Shared outer metadata for admitted provider-history lists."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field

HISTORY_LIMIT_DEFAULT: Final[int] = 20
HISTORY_LIMIT_MAX: Final[int] = 100
HISTORY_ORDER: Final[tuple[str, str]] = ("asc", "desc")

OUTER_HISTORY_KEYS: Final[frozenset[str]] = frozenset(
    {
        "provider",
        "adapter_contract",
        "requested_keyword",
        "derivation_version_id",
        "recipe_resolution",
        "observation_kinds",
        "captures",
        "total_matching",
        "returned_count",
        "limit",
        "order",
        "has_more",
    }
)

_GRAIN: Final[str] = (
    "Admitted, subject-bound Capture-document history under one resolved Recipe. "
    "This list grain is Capture documents, not Observation envelopes, typed facts, "
    "or provider corpus/item/page counts."
)
_ORDER_DESCRIPTION: Final[str] = (
    "Echo of the validated query order. Deterministic outer ordering is "
    "(request_started_at, capture_id); descending reverses that complete key "
    "before limiting. This is not provider item order."
)
_HAS_MORE_DESCRIPTION: Final[str] = (
    "True when total_matching exceeds returned_count. Discloses an omitted outer "
    "Capture-history tail. This is not pagination, a cursor, or authorization to "
    "fetch another page."
)
_EMPTY_DESCRIPTION: Final[str] = (
    "Empty admitted history (total_matching 0, captures empty) means no matching "
    "admitted Capture documents under this route, keyword, and Recipe. It does not "
    "distinguish failed measurement from never measured."
)


class HistoryListEnvelope(BaseModel):
    """Typed outer history list. Nested Capture mappings pass through uncoerced."""

    model_config = ConfigDict(extra="forbid")

    provider: str = Field(description=_GRAIN)
    adapter_contract: str = Field(
        description=(
            "Surface adapter contract for this admitted Capture-document list "
            "under one resolved Recipe."
        )
    )
    requested_keyword: str = Field(
        description=(
            "Requested subject for this admitted, subject-bound Capture history. "
            + _EMPTY_DESCRIPTION
        )
    )
    derivation_version_id: str = Field(
        description="Resolved Recipe identity for this admitted Capture-document list."
    )
    recipe_resolution: Literal["selected", "pinned"] = Field(
        description="How the Recipe was resolved for this admitted Capture history."
    )
    observation_kinds: list[str] = Field(
        description=(
            "Recipe Observation kinds. These do not change the list grain: the "
            "list counts admitted Capture documents, not Observation envelopes."
        )
    )
    captures: list[dict[str, Any]] = Field(
        description=(
            "Whole admitted Capture documents for this surface. Nested mappings "
            "are surface-specific pass-through objects, not one universal fact schema."
        )
    )
    total_matching: int = Field(
        description=(
            "Unique verified matching admitted Capture documents after Evidence and "
            "PostgreSQL consistency checks and before the output limit. Not Observation "
            "envelopes, typed facts, ranked results, monthly points, source occurrences, "
            "or provider corpus/item counts such as Search Mentions total_count or "
            "Organic se_results_count. "
            + _EMPTY_DESCRIPTION
        )
    )
    returned_count: int = Field(
        description=(
            "Number of whole Capture documents in captures. Equals len(captures). "
            "Does not count nested Observation or provider facts."
        )
    )
    limit: int = Field(
        description="Validated applied outer history limit. Maximum 100. Not a provider page size."
    )
    order: Literal["asc", "desc"] = Field(description=_ORDER_DESCRIPTION)
    has_more: bool = Field(description=_HAS_MORE_DESCRIPTION)


def history_list_response(
    *,
    provider: str,
    adapter_contract: str,
    requested_keyword: str,
    derivation_version_id: str,
    recipe_resolution: Literal["selected", "pinned"],
    observation_kinds: Sequence[str],
    captures: Sequence[Mapping[str, object]],
    total_matching: int,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble outer history metadata around already-projected Capture groups."""

    if type(total_matching) is not int or isinstance(total_matching, bool):
        raise TypeError("total_matching must be an integer")
    if type(limit) is not int or isinstance(limit, bool):
        raise TypeError("limit must be an integer")
    if total_matching < 0:
        raise ValueError("total_matching must not be negative")
    if limit < 1 or limit > HISTORY_LIMIT_MAX:
        raise ValueError("limit is outside the accepted outer history bound")
    if order not in HISTORY_ORDER:
        raise ValueError("order must be asc or desc")
    projected = list(captures)
    returned_count = len(projected)
    if returned_count > total_matching:
        raise ValueError("returned_count exceeds total_matching")
    if returned_count > limit:
        raise ValueError("returned_count exceeds applied limit")
    payload: dict[str, object] = {
        "provider": provider,
        "adapter_contract": adapter_contract,
        "requested_keyword": requested_keyword,
        "derivation_version_id": derivation_version_id,
        "recipe_resolution": recipe_resolution,
        "observation_kinds": list(observation_kinds),
        "captures": projected,
        "total_matching": total_matching,
        "returned_count": returned_count,
        "limit": limit,
        "order": order,
        "has_more": total_matching > returned_count,
    }
    if set(payload) != OUTER_HISTORY_KEYS:
        raise ValueError("history envelope keys are not the accepted 12-key set")
    return payload
