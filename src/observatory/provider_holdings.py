"""Shared typing and math for provider Holdings discovery lists."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

from observatory.evidence_store import IntegrityError
from observatory.provider_history import HISTORY_LIMIT_DEFAULT, HISTORY_LIMIT_MAX

HOLDINGS_LIMIT_DEFAULT: Final[int] = HISTORY_LIMIT_DEFAULT
HOLDINGS_LIMIT_MAX: Final[int] = HISTORY_LIMIT_MAX
HOLDINGS_ORDER: Final[tuple[str, str]] = ("asc", "desc")
HOLDINGS_QUERY_KEYS: Final[frozenset[str]] = frozenset({"limit", "order"})

OUTER_HOLDINGS_KEYS: Final[frozenset[str]] = frozenset(
    {
        "provider",
        "adapter_contract",
        "total_matching",
        "returned_count",
        "limit",
        "order",
        "has_more",
        "holdings",
    }
)
ITEM_KEYS: Final[frozenset[str]] = frozenset(
    {
        "requested_keyword",
        "request",
        "attempt_count",
        "capture_count",
        "unresolved_count",
        "first_authorized_at",
        "last_authorized_at",
        "first_request_started_at",
        "last_request_started_at",
    }
)

_GRAIN: Final[str] = (
    "Evidence-backed Holdings catalog item: one exact requested subject plus the "
    "complete surface-local request scope. Not one Attempt, Capture, Observation, "
    "provider item, Outcome classification, or desired measurement."
)
_EMPTY_DESCRIPTION: Final[str] = (
    "Empty Holdings (total_matching 0, holdings empty) means no verified Attempt "
    "Evidence is held for this route's exact provider/adapter after a successful "
    "store-wide Evidence verification. It is not provider-zero, failure, "
    "unimportance, an unselected Recipe, admitted-history absence, or corpus emptiness."
)
_COUNT_DESCRIPTION: Final[str] = (
    "Evidence inventory for this exact subject-plus-request group. Not Observation "
    "counts, admitted counts, ranks, mentions, volume, provider corpus/item counts, "
    "panels, or cadence."
)
_UNRESOLVED_DESCRIPTION: Final[str] = (
    "Number of verified Attempts in this group with no Capture. Authorized/unresolved "
    "lifecycle vocabulary only. Not definitely unsent, queued, retryable, or current status."
)
_TIME_DESCRIPTION: Final[str] = (
    "Canonical Evidence timestamps. last_authorized_at is the maximum Attempt "
    "authorized_at in this group, not last monitored, a cadence, or current status."
)
_HAS_MORE_DESCRIPTION: Final[str] = (
    "True when total_matching exceeds returned_count. Discloses an omitted Holdings "
    "catalog tail. Not pagination, a cursor, or authority to fetch another page. A tail "
    "beyond the maximum limit of 100 remains known but unavailable."
)
_ORDER_DESCRIPTION: Final[str] = (
    "Echo of the validated query order. Deterministic catalog order is the complete "
    "exact subject-plus-request grouping identity; descending reverses that complete "
    "key before limiting. Not recency, provider item order, importance, or strategy rank."
)
_KO_EXPANSION: Final[str] = (
    "A Keyword Overview Attempt with N keywords (1..5) appears as N Holdings items "
    "that share this request.keywords bundle and the same Attempt/Capture inventory "
    "counts and timestamps. This does not prove N measurements or N independent exchanges."
)


class KeywordOverviewHoldingsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keywords: list[str] = Field(description=_KO_EXPANSION)
    location_code: int
    language_code: str
    include_serp_info: bool
    include_clickstream_data: bool


class GoogleOrganicHoldingsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keyword: str = Field(
        description=(
            "Exact Attempt parameters.keyword. The same subject under a different "
            "location, language, device, depth, OS, or enrichment flag is a different holding."
        )
    )
    location_code: int
    language_code: str
    depth: int
    device: str
    os: str
    group_organic_results: bool
    load_async_ai_overview: bool


class SearchMentionsHoldingsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keyword: str = Field(description="Exact Attempt parameters.target[0].keyword.")
    match_type: str = Field(description="Exact Attempt parameters.target[0].match_type.")
    search_filter: str = Field(
        description="Exact Attempt parameters.target[0].search_filter."
    )
    search_scope: list[str] = Field(
        description="Exact Attempt parameters.target[0].search_scope order. Not sorted."
    )
    platform: str
    location_code: int
    language_code: str
    limit: int = Field(
        description="Closed Attempt request limit. Not Holdings list pagination."
    )
    offset: int = Field(
        description=(
            "Closed Attempt request offset. Not a Holdings cursor and not Search "
            "Mentions continuation. search_after_token is not followed."
        )
    )


class _HoldingsItemBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requested_keyword: str = Field(description=_GRAIN)
    attempt_count: int = Field(description=_COUNT_DESCRIPTION)
    capture_count: int = Field(
        description=(
            _COUNT_DESCRIPTION
            + " Multiple Captures prove multiple historical measurements, not a "
            "monitoring program."
        )
    )
    unresolved_count: int = Field(description=_UNRESOLVED_DESCRIPTION)
    first_authorized_at: str = Field(description=_TIME_DESCRIPTION)
    last_authorized_at: str = Field(description=_TIME_DESCRIPTION)
    first_request_started_at: str | None = Field(description=_TIME_DESCRIPTION)
    last_request_started_at: str | None = Field(description=_TIME_DESCRIPTION)


class KeywordOverviewHoldingsItem(_HoldingsItemBase):
    request: KeywordOverviewHoldingsRequest = Field(description=_KO_EXPANSION)


class GoogleOrganicHoldingsItem(_HoldingsItemBase):
    request: GoogleOrganicHoldingsRequest


class SearchMentionsHoldingsItem(_HoldingsItemBase):
    request: SearchMentionsHoldingsRequest = Field(
        description=(
            "Verified Search Mentions Attempt request testimony. request.limit and "
            "request.offset are Attempt fields. search_after_token is not followed."
        )
    )


class _HoldingsEnvelopeBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str = Field(description=_GRAIN + " " + _EMPTY_DESCRIPTION)
    adapter_contract: str
    total_matching: int = Field(
        description=(
            "Unique subject-plus-exact-request groups after store-wide Evidence "
            "verification and before the output limit. Not Attempts, Captures, Outcome "
            "rows, Observation envelopes, facts, provider result items, corpus totals, "
            "or independent Keyword Overview exchanges. "
            + _EMPTY_DESCRIPTION
        )
    )
    returned_count: int = Field(
        description="Number of Holdings items in holdings. Equals len(holdings)."
    )
    limit: int = Field(
        description="Validated applied outer Holdings limit. Maximum 100. Not a provider page size."
    )
    order: Literal["asc", "desc"] = Field(description=_ORDER_DESCRIPTION)
    has_more: bool = Field(description=_HAS_MORE_DESCRIPTION)


class KeywordOverviewHoldingsEnvelope(_HoldingsEnvelopeBase):
    holdings: list[KeywordOverviewHoldingsItem] = Field(description=_GRAIN + " " + _KO_EXPANSION)


class GoogleOrganicHoldingsEnvelope(_HoldingsEnvelopeBase):
    holdings: list[GoogleOrganicHoldingsItem] = Field(description=_GRAIN)


class SearchMentionsHoldingsEnvelope(_HoldingsEnvelopeBase):
    holdings: list[SearchMentionsHoldingsItem] = Field(description=_GRAIN)


@dataclass(frozen=True)
class HoldingsAttempt:
    attempt_id: str
    authorized_at: str
    request_started_at: str | None


def holdings_item(
    *,
    requested_keyword: str,
    request: Mapping[str, object],
    members: Sequence[HoldingsAttempt],
) -> dict[str, object]:
    """Project one Holdings group from already-verified Attempt members."""

    if not members:
        raise IntegrityError("Holdings group has no Attempts")
    seen: set[str] = set()
    authorized: list[str] = []
    started: list[str] = []
    for member in members:
        if member.attempt_id in seen:
            raise IntegrityError("duplicate Attempt in Holdings group")
        seen.add(member.attempt_id)
        if member.authorized_at == "":
            raise IntegrityError("verified Attempt is missing authorized_at")
        authorized.append(member.authorized_at)
        if member.request_started_at is not None:
            if member.request_started_at == "":
                raise IntegrityError("verified Capture is missing request_started_at")
            started.append(member.request_started_at)
    attempt_count = len(seen)
    capture_count = len(started)
    unresolved_count = attempt_count - capture_count
    if unresolved_count < 0:
        raise IntegrityError("Holdings capture_count exceeds attempt_count")
    payload: dict[str, object] = {
        "requested_keyword": requested_keyword,
        "request": dict(request),
        "attempt_count": attempt_count,
        "capture_count": capture_count,
        "unresolved_count": unresolved_count,
        "first_authorized_at": min(authorized),
        "last_authorized_at": max(authorized),
        "first_request_started_at": None if not started else min(started),
        "last_request_started_at": None if not started else max(started),
    }
    if capture_count == 0:
        if (
            payload["first_request_started_at"] is not None
            or payload["last_request_started_at"] is not None
        ):
            raise IntegrityError("unresolved Holdings group has Capture time")
    elif (
        payload["first_request_started_at"] is None
        or payload["last_request_started_at"] is None
    ):
        raise IntegrityError("captured Holdings group is missing request time")
    if set(payload) != ITEM_KEYS:
        raise ValueError("holdings item keys are not the accepted set")
    return payload


def assert_unique_holdings_groups(
    catalog: Sequence[tuple[tuple[object, ...], Mapping[str, object]]],
) -> None:
    """Fail closed if grouped catalog identities are not unique."""

    keys = [item[0] for item in catalog]
    if len(keys) != len(set(keys)):
        raise IntegrityError("duplicate Holdings group identity")


def holdings_list_response(
    *,
    provider: str,
    adapter_contract: str,
    holdings: Sequence[Mapping[str, object]],
    total_matching: int,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble outer Holdings metadata around already-projected catalog items."""

    if type(total_matching) is not int or isinstance(total_matching, bool):
        raise TypeError("total_matching must be an integer")
    if type(limit) is not int or isinstance(limit, bool):
        raise TypeError("limit must be an integer")
    if total_matching < 0:
        raise ValueError("total_matching must not be negative")
    if limit < 1 or limit > HOLDINGS_LIMIT_MAX:
        raise ValueError("limit is outside the accepted outer Holdings bound")
    if order not in HOLDINGS_ORDER:
        raise ValueError("order must be asc or desc")
    projected = list(holdings)
    returned_count = len(projected)
    if returned_count > total_matching:
        raise ValueError("returned_count exceeds total_matching")
    if returned_count > limit:
        raise ValueError("returned_count exceeds applied limit")
    payload: dict[str, object] = {
        "provider": provider,
        "adapter_contract": adapter_contract,
        "holdings": projected,
        "total_matching": total_matching,
        "returned_count": returned_count,
        "limit": limit,
        "order": order,
        "has_more": total_matching > returned_count,
    }
    if set(payload) != OUTER_HOLDINGS_KEYS:
        raise ValueError("holdings envelope keys are not the accepted 8-key set")
    return payload
