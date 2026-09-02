"""Read-side assembly for DataForSEO Google Organic API history."""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Any, Final, Literal

from psycopg import Connection, sql
from pydantic import BaseModel, ConfigDict, Field, field_validator

from observatory.capture_event import ORGANIC_ADAPTER_CONTRACT
from observatory.dataforseo_google_organic import (
    AIO_PRESENCE_KIND,
    AIO_SOURCE_KIND,
    FEATURE_PRESENCE_KIND,
    GOOGLE_ORGANIC_EXPANDED_RECIPE_ID,
    ORGANIC_PLACEMENT_KIND,
    ORGANIC_PLACEMENT_V2_KIND,
    ORGANIC_SITELINK_KIND,
    RELATED_QUERY_KIND,
    RELATED_QUESTION_KIND,
    TOP_STORY_RESULT_KIND,
    VIDEO_RESULT_KIND,
)
from observatory.evidence_store import EvidenceStore, IntegrityError
from observatory.google_organic_derive import (
    RANKED_V2_TABLE,
    SITELINK_OCCURRENCES_TABLE,
    SITELINKS_TABLE,
    TOP_STORY_OCCURRENCES_TABLE,
    TOP_STORY_TABLE,
    VIDEO_OCCURRENCES_TABLE,
    VIDEO_TABLE,
    plan_google_organic_expanded_capture,
)
from observatory.provider_history import HISTORY_LIMIT_MAX, history_list_response
from observatory.provider_holdings import (
    HoldingsAttempt,
    assert_unique_holdings_groups,
    holdings_item,
    holdings_list_response,
)
from observatory.provider_outcomes import (
    load_validated_outcomes_recipe,
    load_verified_store_events,
    outcomes_list_response,
    project_matched_attempt,
)
from observatory.provider_recipe_selection import (
    ResolvedProviderRecipe,
    resolve_provider_recipe,
)

HISTORY_PROVIDER: Final[str] = "dataforseo"
HISTORY_ADAPTER: Final[str] = ORGANIC_ADAPTER_CONTRACT
_KIND_TABLES: Final[dict[str, str]] = {
    FEATURE_PRESENCE_KIND: "google_organic_serp_features",
    ORGANIC_PLACEMENT_KIND: "google_organic_ranked_results",
    AIO_PRESENCE_KIND: "google_organic_aio_presence",
    AIO_SOURCE_KIND: "google_organic_aio_sources",
    RELATED_QUESTION_KIND: "google_organic_related_questions",
    RELATED_QUERY_KIND: "google_organic_related_queries",
    ORGANIC_PLACEMENT_V2_KIND: "google_organic_ranked_results_v2",
    TOP_STORY_RESULT_KIND: "google_organic_top_story_results",
    VIDEO_RESULT_KIND: "google_organic_video_results",
    ORGANIC_SITELINK_KIND: "google_organic_sitelinks",
}
EXPANDED_OBSERVATION_KINDS: Final[tuple[str, ...]] = (
    FEATURE_PRESENCE_KIND,
    ORGANIC_PLACEMENT_V2_KIND,
    AIO_PRESENCE_KIND,
    AIO_SOURCE_KIND,
    RELATED_QUESTION_KIND,
    RELATED_QUERY_KIND,
    TOP_STORY_RESULT_KIND,
    VIDEO_RESULT_KIND,
    ORGANIC_SITELINK_KIND,
)
# Every semantic child of the expanded Recipe must keep at least one structurally
# bound occurrence row. A parent with none is integrity damage, not an empty list.
_CHILD_OCCURRENCE_FAMILIES: Final[tuple[tuple[str, str, str], ...]] = (
    (
        TOP_STORY_TABLE,
        TOP_STORY_OCCURRENCES_TABLE,
        "Top Stories child has no subordinate occurrences",
    ),
    (
        VIDEO_TABLE,
        VIDEO_OCCURRENCES_TABLE,
        "Video child has no subordinate occurrences",
    ),
    (
        SITELINKS_TABLE,
        SITELINK_OCCURRENCES_TABLE,
        "organic sitelink has no subordinate occurrences",
    ),
)
# Read-side complete-set agreement for ranked-result v2 and the three PF-18 child
# families is proved against the strongest authority Observatory has: the verified
# Evidence body itself. Envelope/typed-key membership cannot refuse a legal but false
# ranked-v2 timestamp, links family, URL, or childless placement; "at least one bound
# occurrence" cannot refuse a spurious extra child_index; and an identity-only parent
# citation cannot refuse a falsified parent axis. Rebuilding the exact intended rows
# from the verified Capture body and requiring set equality refuses all of those,
# before the outer limit.
_CHILD_OCCURRENCE_COLUMNS: Final[tuple[str, ...]] = (
    "within_capture_identity",
    "observation_kind",
    "child_index",
)
_RANKED_V2_COLUMNS: Final[tuple[str, ...]] = (
    "within_capture_identity",
    "observation_kind",
    "requested_keyword",
    "page",
    "position",
    "rank_group",
    "rank_absolute",
    "url",
    "domain",
    "title",
    "description",
    "description_state",
    "website_name",
    "website_name_state",
    "organic_item_timestamp",
    "organic_item_timestamp_state",
    "links_state",
    "links_count",
)
_TOP_STORY_CHILD_COLUMNS: Final[tuple[str, ...]] = (
    "within_capture_identity",
    "observation_kind",
    "requested_keyword",
    "parent_item_type",
    "parent_within_capture_identity",
    "parent_page",
    "parent_position",
    "parent_rank_group",
    "parent_rank_absolute",
    "child_url",
    "source",
    "domain",
    "title",
    "top_story_item_timestamp",
    "top_story_item_timestamp_state",
)
_VIDEO_CHILD_COLUMNS: Final[tuple[str, ...]] = (
    "within_capture_identity",
    "observation_kind",
    "requested_keyword",
    "parent_item_type",
    "parent_within_capture_identity",
    "parent_page",
    "parent_position",
    "parent_rank_group",
    "parent_rank_absolute",
    "child_url",
    "source",
    "title",
    "video_item_timestamp",
    "video_item_timestamp_state",
)
_SITELINK_CHILD_COLUMNS: Final[tuple[str, ...]] = (
    "within_capture_identity",
    "observation_kind",
    "requested_keyword",
    "parent_within_capture_identity",
    "parent_page",
    "parent_position",
    "parent_rank_group",
    "parent_rank_absolute",
    "child_url",
    "title",
    "domain",
    "description",
    "description_state",
)


# --------------------------------------------------------------------------------------
# PF-18 expanded Google Organic history models
#
# These are typed strongly enough that generated OpenAPI attaches every time, state,
# identity, and completeness description to the exact property it governs, rather than
# leaving the expanded Capture as an untyped pass-through mapping.
# --------------------------------------------------------------------------------------

_FIELD_STATES = Literal["stated", "json_null", "absent", "not_requested", "inapplicable"]
# PF-18 introduced ordinary provider fields whose applicable domain is narrower than the
# repository-wide five-token one. Accepted v1 fields keep the wide domain; only the newly
# introduced PF-18 ordinary fields use this one.
_ORDINARY_FIELD_STATES = Literal["stated", "json_null", "absent"]

_EXPANDED_RECIPE_NOTE: Final[str] = (
    "This document is served only under the PF-18 expanded Google Organic Recipe. "
    "The accepted v1 Recipe remains separately pinnable and returns the unchanged "
    "six-kind v1 document without ranked-result v2, Top Stories children, Video "
    "children, or sitelinks."
)
_ITEM_TIME_NOTE: Final[str] = (
    "Exact provider-stated structure-local item/result timestamp testimony. It is NOT "
    "Capture time (request_started_at/transport_ended_at), NOT the result retrieval "
    "datetime (result_context.provider_result_time), NOT Provider Update Time, and NOT "
    "a Data Period. Observatory does not certify it as an independent publication "
    "instant. It never inherits from result datetime, Capture provenance, a Top Stories "
    "relative date string, an organic pre_snippet, a sibling field, or another row."
)
_ITEM_TIME_STATE_NOTE: Final[str] = (
    "state distinguishes a provider-stated value from provider JSON null and from a "
    "permitted absent key. Those three are never collapsed and an unstated time is "
    "never filled in."
)
_CHILD_URL_NOTE: Final[str] = (
    "Exact provider URL testimony for this child. It is NOT a canonical Page, Site, "
    "Video, Brand, or entity identity, is never normalized or redirect-resolved, and "
    "the same URL under another parent placement or another Observation kind stays a "
    "distinct semantic fact."
)
_PARENT_PLACEMENT_NOTE: Final[str] = (
    "Exact parent SERP placement that returned this child. Parent placement is the "
    "semantic scope of the child fact; it is not the child's own rank and not a child "
    "occurrence."
)
_OCCURRENCE_NOTE: Final[str] = (
    "Subordinate returned-occurrence testimony for one semantic child. child_index is "
    "the provider array position, never a rank, importance, score, or identity. "
    "Repeated agreeing children collapse to one semantic fact carrying several "
    "occurrences; occurrence rows never raise capture_outcome.observation_count."
)
_ORDINARY_STATE_NOTE: Final[str] = (
    "The applicable states for this ordinary provider field are exactly stated, "
    "provider JSON null, and permitted absence. The expanded Recipe never disables this "
    "dimension per request and never declares it recipe-inapplicable, so not_requested "
    "and inapplicable are impossible here: persistence and this contract refuse them "
    "instead of serving them as testimony."
)
_CHILD_COMPLETENESS_NOTE: Final[str] = (
    "Returned child count and order are exactly what this Capture returned. They do "
    "not prove provider or corpus completeness, and they are not a page size."
)


class GoogleOrganicTextField(BaseModel):
    """Provider text testimony with explicit field state."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: _FIELD_STATES = Field(
        description=(
            "Provider field state. stated, provider JSON null, permitted absence, "
            "request-disabled, and recipe-inapplicable are never collapsed."
        )
    )
    value: str | None = Field(
        description="Exact provider string when state is stated; otherwise null."
    )


class GoogleOrganicIntField(BaseModel):
    """Provider integer testimony with explicit field state."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: _FIELD_STATES = Field(
        description=(
            "Provider field state. A stated numeric zero is never collapsed with "
            "provider JSON null or absence."
        )
    )
    value: int | None = Field(
        description="Exact provider integer when state is stated; otherwise null."
    )


class GoogleOrganicItemTimestamp(BaseModel):
    """Provider-stated structure-local item/result timestamp testimony."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: _ORDINARY_FIELD_STATES = Field(
        description=_ITEM_TIME_STATE_NOTE + " " + _ORDINARY_STATE_NOTE
    )
    value: str | None = Field(
        description=(
            "Exact provider timestamp string when state is stated; otherwise null. "
            + _ITEM_TIME_NOTE
        )
    )


class GoogleOrganicLinksFamily(BaseModel):
    """Parent `links` family state, kept independent of any child rows."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: _ORDINARY_FIELD_STATES = Field(
        description=(
            "Parent links-family state. absent (no key), json_null (key stated null), "
            "and stated (an actual array) stay distinct. A stated empty array and a "
            "stated populated array are both state=stated and are separated by "
            "returned_child_count, so 'no sitelink rows' can never stand in for the "
            "four distinct provider families. " + _ORDINARY_STATE_NOTE
        )
    )
    returned_child_count: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Number of link_element children the provider actually returned under this "
            "placement: 0 for a stated empty array, N for a stated populated array, and "
            "null whenever links was absent or JSON null. "
            + _CHILD_COMPLETENESS_NOTE
        ),
    )


class GoogleOrganicOrdinaryTextField(BaseModel):
    """PF-18 ordinary provider text testimony with a narrowed field-state domain."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: _ORDINARY_FIELD_STATES = Field(description=_ORDINARY_STATE_NOTE)
    value: str | None = Field(
        description="Exact provider string when state is stated; otherwise null."
    )


class GoogleOrganicChildOccurrence(BaseModel):
    """One returned occurrence of a semantic child."""

    model_config = ConfigDict(extra="forbid", strict=True)

    child_index: int = Field(ge=0, description=_OCCURRENCE_NOTE)


class GoogleOrganicRequest(BaseModel):
    """Exact verified Attempt request context."""

    model_config = ConfigDict(extra="forbid", strict=True)

    location_code: int
    language_code: str = Field(min_length=1)
    depth: int = Field(
        description=(
            "Exact requested Attempt depth. Depth bounds what the provider could "
            "return; it does not prove provider-corpus completeness."
        )
    )
    device: str = Field(min_length=1)
    os: str = Field(min_length=1)
    group_organic_results: bool
    load_async_ai_overview: bool


class GoogleOrganicCaptureOutcome(BaseModel):
    """Derived Capture classification for this Recipe."""

    model_config = ConfigDict(extra="forbid", strict=True)

    classification: Literal["observation_admitted", "observation_admitted_empty"] = Field(
        description=(
            "Admitted Capture classification under this Recipe. Failed, partial, "
            "no-response, unresolved, and rejected paths never appear as Observations "
            "in this history document."
        )
    )
    observation_count: int = Field(
        ge=0,
        description=(
            "Semantic Observation envelopes derived from this Capture under this "
            "Recipe. Subordinate occurrence rows are never counted here, so the "
            "expanded count is one envelope per semantic child, not per occurrence."
        ),
    )


class GoogleOrganicResultContext(BaseModel):
    """Provider result-level context for one admitted Capture."""

    model_config = ConfigDict(extra="forbid", strict=True)

    requested_keyword: str = Field(min_length=1)
    returned_keyword: GoogleOrganicTextField
    se_domain: GoogleOrganicTextField
    provider_result_time: GoogleOrganicTextField = Field(
        description=(
            "Exact provider result-level retrieval datetime. This is the result clock, "
            "not an item timestamp: it must never be read as, or substituted for, any "
            "organic, Top Stories, or Video item timestamp, and it is not Capture time, "
            "Provider Update Time, or a Data Period."
        )
    )
    se_results_count: GoogleOrganicIntField = Field(
        description=(
            "Provider-stated result-count claim. It is provider testimony, not an "
            "Observatory completeness guarantee and not a count of returned rows."
        )
    )
    pages_count: GoogleOrganicIntField = Field(
        description=(
            "Provider-stated page-count claim. It does not prove corpus completeness "
            "and is not an authorization to fetch further pages."
        )
    )
    items_count: int = Field(
        ge=0,
        description=(
            "Provider-stated returned item count for this one Capture. Not a corpus "
            "total and not the Observation count."
        ),
    )
    item_types: list[str] = Field(
        description="Exact provider-declared item types returned in this result."
    )


class GoogleOrganicSerpFeature(BaseModel):
    """One returned SERP feature placement."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal["dataforseo.google.organic.serp_feature_presence.v1"]
    within_capture_identity: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$"
    )
    item_type: str = Field(min_length=1)
    page: int = Field(ge=1)
    position: Literal["left", "right"]
    rank_group: int = Field(ge=1)
    rank_absolute: int = Field(ge=1)


class GoogleOrganicRankedResultV2(BaseModel):
    """One organic ranked placement under ranked_result.v2."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal["dataforseo.google.organic.ranked_result.v2"] = Field(
        description=(
            "Ranked-result v2 keeps the accepted v1 placement identity axes exactly. "
            "The added item timestamp and links-family state are content, never "
            "identity, and the URL is not part of placement identity. "
            + _EXPANDED_RECIPE_NOTE
        )
    )
    within_capture_identity: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$"
    )
    url: str = Field(
        min_length=1,
        description=(
            "Exact provider URL testimony for this placement. Not a canonical Page "
            "identity, never normalized or redirect-resolved."
        ),
    )
    domain: str = Field(min_length=1)
    title: str
    description: GoogleOrganicTextField
    website_name: GoogleOrganicTextField
    page: int = Field(ge=1)
    position: Literal["left", "right"]
    rank_group: int = Field(ge=1)
    rank_absolute: int = Field(ge=1)
    organic_item_timestamp: GoogleOrganicItemTimestamp = Field(
        description=(
            "Exact provider-stated organic item/result timestamp for this placement. "
            + _ITEM_TIME_NOTE
        )
    )
    links: GoogleOrganicLinksFamily = Field(
        description=(
            "Parent links-family testimony for this placement, persisted independently "
            "of the sitelinks list so absent, JSON null, stated-empty, and "
            "stated-populated never collapse into one 'no child row' representation. "
            "The child rows themselves are in the Capture-level sitelinks family."
        )
    )


class GoogleOrganicAiOverviewPresence(BaseModel):
    """AI Overview presence placement."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal["dataforseo.google.organic.ai_overview_presence.v1"]
    within_capture_identity: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$"
    )
    asynchronous_ai_overview: bool
    page: int = Field(ge=1)
    position: Literal["left", "right"]
    rank_group: int = Field(ge=1)
    rank_absolute: int = Field(ge=1)


class GoogleOrganicAiOverviewSourceOccurrence(BaseModel):
    """One returned occurrence of an AI Overview source."""

    model_config = ConfigDict(extra="forbid", strict=True)

    locus: Literal["top_level", "element"]
    element_index: int | None = Field(default=None, ge=0)
    reference_index: int = Field(ge=0, description=_OCCURRENCE_NOTE)


class GoogleOrganicAiOverviewSource(BaseModel):
    """One semantic AI Overview source with its occurrences."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal["dataforseo.google.organic.ai_overview_source.v1"]
    within_capture_identity: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$"
    )
    locus: Literal["top_level", "element"]
    url: str = Field(min_length=1)
    domain: GoogleOrganicTextField
    title: GoogleOrganicTextField
    source: GoogleOrganicTextField
    occurrences: list[GoogleOrganicAiOverviewSourceOccurrence]


class GoogleOrganicRelatedQuestionOccurrence(BaseModel):
    """One returned occurrence of a related question."""

    model_config = ConfigDict(extra="forbid", strict=True)

    page: int = Field(ge=1)
    position: Literal["left", "right"]
    rank_group: int = Field(ge=1)
    rank_absolute: int = Field(ge=1)
    question_index: int = Field(ge=0, description=_OCCURRENCE_NOTE)


class GoogleOrganicRelatedQuestion(BaseModel):
    """One semantic related question with its occurrences."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal["dataforseo.google.organic.related_question.v1"]
    within_capture_identity: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$"
    )
    title: str
    occurrences: list[GoogleOrganicRelatedQuestionOccurrence]


class GoogleOrganicRelatedQuery(BaseModel):
    """One returned related query."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal["dataforseo.google.organic.related_query.v1"]
    within_capture_identity: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$"
    )
    query: str


class GoogleOrganicTopStoryResult(BaseModel):
    """One semantic Top Stories child result under its exact parent placement."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal["dataforseo.google.organic.top_story_result.v1"] = Field(
        description=(
            "Semantic identity is the exact requested keyword, the exact parent SERP "
            "placement, and the exact child URL. Source, domain, title, and timestamp "
            "are content. " + _EXPANDED_RECIPE_NOTE
        )
    )
    within_capture_identity: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$"
    )
    parent_within_capture_identity: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
        description=(
            "Identity of the top_stories SERP feature placement envelope that returned "
            "this child. " + _PARENT_PLACEMENT_NOTE
        ),
    )
    parent_page: int = Field(ge=1, description=_PARENT_PLACEMENT_NOTE)
    parent_position: Literal["left", "right"] = Field(description=_PARENT_PLACEMENT_NOTE)
    parent_rank_group: int = Field(ge=1, description=_PARENT_PLACEMENT_NOTE)
    parent_rank_absolute: int = Field(ge=1, description=_PARENT_PLACEMENT_NOTE)
    child_url: str = Field(min_length=1, description=_CHILD_URL_NOTE)
    source: str = Field(
        description="Exact provider-stated source string. Not a canonical publisher entity."
    )
    domain: str = Field(
        description="Exact provider-stated child domain. Not a canonical Site identity."
    )
    title: str
    top_story_item_timestamp: GoogleOrganicItemTimestamp = Field(
        description=(
            "Exact provider-stated Top Stories child item timestamp. "
            + _ITEM_TIME_NOTE
            + " In particular it is never derived from the sibling relative date string, "
            "which PF-18 leaves raw."
        )
    )
    occurrences: list[GoogleOrganicChildOccurrence] = Field(
        min_length=1,
        description=_OCCURRENCE_NOTE + " " + _CHILD_COMPLETENESS_NOTE,
    )


class GoogleOrganicVideoResult(BaseModel):
    """One semantic Video child result under its exact parent placement."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal["dataforseo.google.organic.video_result.v1"] = Field(
        description=(
            "Semantic identity is the exact requested keyword, the exact parent SERP "
            "placement, and the exact child URL. This Google SERP video item is not a "
            "YouTube Organic result and carries no canonical video identity. "
            + _EXPANDED_RECIPE_NOTE
        )
    )
    within_capture_identity: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$"
    )
    parent_within_capture_identity: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
        description=(
            "Identity of the video SERP feature placement envelope that returned this "
            "child. " + _PARENT_PLACEMENT_NOTE
        ),
    )
    parent_page: int = Field(ge=1, description=_PARENT_PLACEMENT_NOTE)
    parent_position: Literal["left", "right"] = Field(description=_PARENT_PLACEMENT_NOTE)
    parent_rank_group: int = Field(ge=1, description=_PARENT_PLACEMENT_NOTE)
    parent_rank_absolute: int = Field(ge=1, description=_PARENT_PLACEMENT_NOTE)
    child_url: str = Field(min_length=1, description=_CHILD_URL_NOTE)
    source: str = Field(
        description=(
            "Exact composite provider source string as returned. It is not split into "
            "platform and channel, and no child domain is exposed because the provider "
            "states none; PF-18 never derives one from the URL."
        )
    )
    title: str
    video_item_timestamp: GoogleOrganicItemTimestamp = Field(
        description=(
            "Exact provider-stated Video child item timestamp. " + _ITEM_TIME_NOTE
        )
    )
    occurrences: list[GoogleOrganicChildOccurrence] = Field(
        min_length=1,
        description=_OCCURRENCE_NOTE + " " + _CHILD_COMPLETENESS_NOTE,
    )


class GoogleOrganicSitelink(BaseModel):
    """One semantic sitelink child under its exact organic ranked placement."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal["dataforseo.google.organic.organic_sitelink.v1"] = Field(
        description=(
            "Semantic identity is the exact requested keyword, the exact parent organic "
            "placement, and the exact child URL. Title, domain, and description state "
            "are content. " + _EXPANDED_RECIPE_NOTE
        )
    )
    within_capture_identity: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$"
    )
    parent_within_capture_identity: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
        description=(
            "Identity of the ranked_result.v2 envelope that returned this sitelink. "
            + _PARENT_PLACEMENT_NOTE
        ),
    )
    parent_page: int = Field(ge=1, description=_PARENT_PLACEMENT_NOTE)
    parent_position: Literal["left", "right"] = Field(description=_PARENT_PLACEMENT_NOTE)
    parent_rank_group: int = Field(ge=1, description=_PARENT_PLACEMENT_NOTE)
    parent_rank_absolute: int = Field(ge=1, description=_PARENT_PLACEMENT_NOTE)
    child_url: str = Field(min_length=1, description=_CHILD_URL_NOTE)
    title: str
    domain: str = Field(
        description="Exact provider-stated child domain. Not a canonical Site identity."
    )
    description: GoogleOrganicOrdinaryTextField = Field(
        description=(
            "Sitelink description testimony. A provider JSON null description is not an "
            "empty string and not an absent key; the state carries that distinction. "
            "This is an ordinary provider field introduced by PF-18, not an inherited v1 "
            "field, so it never carries request-disabled or recipe-inapplicable "
            "semantics."
        )
    )
    occurrences: list[GoogleOrganicChildOccurrence] = Field(
        min_length=1,
        description=_OCCURRENCE_NOTE + " " + _CHILD_COMPLETENESS_NOTE,
    )


class GoogleOrganicExpandedCapture(BaseModel):
    """One admitted Capture document under the PF-18 expanded Recipe."""

    model_config = ConfigDict(extra="forbid", strict=True)

    attempt_id: str = Field(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")
    capture_id: str = Field(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")
    provider: Literal["dataforseo"]
    adapter_contract: Literal[
        "dataforseo-serp-google-organic-live-advanced-paid-probe-v1"
    ]
    derivation_version_id: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
        description=_EXPANDED_RECIPE_NOTE,
    )
    authorized_at: str = Field(
        description=(
            "Observatory Attempt authorization time from verified Evidence. It is "
            "Observatory provenance and must never substitute for any provider item "
            "timestamp or result datetime."
        )
    )
    request_started_at: str = Field(
        description=(
            "Observatory Capture transport start time from verified Evidence. This is "
            "Capture time, not a provider item timestamp."
        )
    )
    transport_ended_at: str = Field(
        description=(
            "Observatory Capture transport end time from verified Evidence. This is "
            "Capture time, not a provider item timestamp."
        )
    )
    request: GoogleOrganicRequest
    capture_outcome: GoogleOrganicCaptureOutcome
    result_context: GoogleOrganicResultContext
    serp_features: list[GoogleOrganicSerpFeature]
    ranked_results: list[GoogleOrganicRankedResultV2]
    ai_overview_presence: GoogleOrganicAiOverviewPresence | None
    ai_overview_sources: list[GoogleOrganicAiOverviewSource]
    related_questions: list[GoogleOrganicRelatedQuestion]
    related_queries: list[GoogleOrganicRelatedQuery]
    top_story_results: list[GoogleOrganicTopStoryResult] = Field(
        description=(
            "Every Top Stories child this Capture returned, scoped to its exact parent "
            "placement. An empty list means this Capture returned no Top Stories child "
            "under this Recipe; it does not mean the provider has none. "
            + _CHILD_COMPLETENESS_NOTE
        )
    )
    video_results: list[GoogleOrganicVideoResult] = Field(
        description=(
            "Every Video child this Capture returned, scoped to its exact parent "
            "placement. " + _CHILD_COMPLETENESS_NOTE
        )
    )
    sitelinks: list[GoogleOrganicSitelink] = Field(
        description=(
            "Every sitelink child this Capture returned, scoped to its exact parent "
            "organic ranked placement. An empty list never distinguishes the four "
            "parent links families; read ranked_results[].links.state for that."
        )
    )


class GoogleOrganicExpandedHistoryEnvelope(BaseModel):
    """Closed expanded Google Organic admitted-history envelope."""

    model_config = ConfigDict(extra="forbid", strict=True)

    provider: Literal["dataforseo"] = Field(
        description=(
            "Admitted, subject-bound Capture-document history under the resolved "
            "Recipe. The list grain is Capture documents, not Observation envelopes, "
            "typed facts, child occurrences, or provider corpus counts."
        )
    )
    adapter_contract: Literal[
        "dataforseo-serp-google-organic-live-advanced-paid-probe-v1"
    ]
    requested_keyword: str = Field(
        min_length=1,
        description=(
            "Requested subject for this history. An empty admitted history does not "
            "distinguish failed measurement from never measured."
        ),
    )
    derivation_version_id: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
        description=_EXPANDED_RECIPE_NOTE,
    )
    recipe_resolution: Literal["selected", "pinned"] = Field(
        description=(
            "How this Recipe was resolved. Pinning the accepted v1 Recipe returns the "
            "unchanged v1 document instead of this expanded one; deriving or "
            "registering the expanded Recipe never changes the operator selection."
        )
    )
    observation_kinds: list[str] = Field(
        min_length=9,
        max_length=9,
        description=(
            "Exact ordered expanded-Recipe Observation kinds. They do not change the "
            "list grain: the list still counts admitted Capture documents."
        ),
    )
    captures: list[GoogleOrganicExpandedCapture]
    total_matching: int = Field(
        ge=0,
        description=(
            "Unique verified matching admitted Capture documents after Evidence and "
            "PostgreSQL consistency checks and before the output limit. Not Observation "
            "envelopes, typed facts, child occurrences, or provider corpus counts."
        ),
    )
    returned_count: int = Field(
        ge=0, description="Number of whole Capture documents in captures."
    )
    limit: int = Field(
        ge=1,
        le=HISTORY_LIMIT_MAX,
        description=(
            "Validated applied outer history limit. It is not a provider page size and "
            "it never hides corruption: every matching candidate Capture is integrity "
            "checked before the limit is applied."
        ),
    )
    order: Literal["asc", "desc"] = Field(
        description=(
            "Echo of the validated query order over (request_started_at, capture_id). "
            "This is not provider item order and not child occurrence order."
        )
    )
    has_more: bool = Field(
        description=(
            "True when total_matching exceeds returned_count. It discloses an omitted "
            "outer Capture-history tail; it is not pagination or a cursor."
        )
    )

    @field_validator("observation_kinds")
    @classmethod
    def require_expanded_kinds(cls, value: list[str]) -> list[str]:
        if value != list(EXPANDED_OBSERVATION_KINDS):
            raise ValueError(
                "observation_kinds must be the exact ordered expanded Recipe kinds"
            )
        return value


def _json_field(state: object, value: object) -> dict[str, object]:
    return {"state": str(state), "value": _json_value(value)}


def _json_value(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    raise TypeError(f"unsupported provider field type: {type(value)!r}")


def _as_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


def _require_text(document: Mapping[str, object], key: str) -> str:
    value = document.get(key)
    if not isinstance(value, str) or value == "":
        raise IntegrityError(f"verified document is missing {key}")
    return value


def _recipe_kinds(
    connection: Connection[Any], derivation_version_id: str
) -> tuple[str, ...]:
    row = connection.execute(
        """
        SELECT recipe_canonical_bytes
        FROM provider_recipes
        WHERE derivation_version_id = %s
        """,
        (derivation_version_id,),
    ).fetchone()
    if row is None:
        raise IntegrityError("resolved recipe is not registered")
    document = json.loads(bytes(row[0]).decode("utf-8"))
    kinds = document.get("observation_kinds")
    if not isinstance(kinds, list) or not all(isinstance(item, str) for item in kinds):
        raise IntegrityError("resolved recipe has no observation kinds")
    return tuple(kinds)


def _parameters(attempt: Mapping[str, object]) -> Mapping[str, object]:
    parameters = attempt.get("parameters")
    if not isinstance(parameters, Mapping):
        raise IntegrityError("verified Attempt is missing parameters")
    return parameters


def _request_context(
    attempt: Mapping[str, object],
    *,
    context_location: int,
    context_language: str,
) -> dict[str, object]:
    parameters = _parameters(attempt)
    location = parameters.get("location_code")
    language = parameters.get("language_code")
    depth = parameters.get("depth")
    device = parameters.get("device")
    operating_system = parameters.get("os")
    group = parameters.get("group_organic_results")
    load_async = parameters.get("load_async_ai_overview")
    if type(location) is not int:
        raise IntegrityError("verified Attempt location_code is missing")
    if not isinstance(language, str) or language == "":
        raise IntegrityError("verified Attempt language_code is missing")
    if type(depth) is not int:
        raise IntegrityError("verified Attempt depth is missing")
    if not isinstance(device, str) or device == "":
        raise IntegrityError("verified Attempt device is missing")
    if not isinstance(operating_system, str) or operating_system == "":
        raise IntegrityError("verified Attempt os is missing")
    if type(group) is not bool or type(load_async) is not bool:
        raise IntegrityError("verified Attempt organic flags are missing")
    if location != context_location or language != context_language:
        raise IntegrityError("Attempt request context disagrees with result context")
    return {
        "location_code": location,
        "language_code": language,
        "depth": depth,
        "device": device,
        "os": operating_system,
        "group_organic_results": group,
        "load_async_ai_overview": load_async,
    }


def _assert_history_candidates_consistent(
    connection: Connection[Any],
    candidates: Sequence[tuple[str, int]],
    derivation_version_id: str,
    kinds: Sequence[str],
) -> None:
    if not candidates:
        return
    capture_ids = [capture_id for capture_id, _count in candidates]
    expected_counts = {capture_id: count for capture_id, count in candidates}
    envelope_rows = connection.execute(
        """
        SELECT capture_id, within_capture_identity, observation_kind
        FROM observation_envelopes
        WHERE derivation_version_id = %s AND capture_id = ANY(%s)
        """,
        (derivation_version_id, capture_ids),
    ).fetchall()
    envelopes: dict[str, set[tuple[str, str]]] = {
        capture_id: set() for capture_id in capture_ids
    }
    for row in envelope_rows:
        envelopes[str(row[0])].add((str(row[1]), str(row[2])))
    typed: dict[str, set[tuple[str, str]]] = {
        capture_id: set() for capture_id in capture_ids
    }
    for kind in kinds:
        table = _KIND_TABLES.get(kind)
        if table is None:
            raise IntegrityError("resolved recipe names an unknown Observation kind")
        rows = connection.execute(
            sql.SQL(
                """
                SELECT capture_id, within_capture_identity, observation_kind
                FROM {}
                WHERE derivation_version_id = %s AND capture_id = ANY(%s)
                """
            ).format(sql.Identifier(table)),
            (derivation_version_id, capture_ids),
        ).fetchall()
        for row in rows:
            typed[str(row[0])].add((str(row[1]), str(row[2])))
    for capture_id, expected_count in expected_counts.items():
        keys = envelopes[capture_id]
        if len(keys) != expected_count:
            raise IntegrityError("envelope set disagrees with Outcome observation_count")
        if typed[capture_id] != keys:
            raise IntegrityError("typed Observation keys disagree with envelopes")
    orphan_sources = connection.execute(
        """
        SELECT 1
        FROM google_organic_aio_sources AS s
        WHERE s.derivation_version_id = %s
          AND s.capture_id = ANY(%s)
          AND NOT EXISTS (
                SELECT 1
                FROM google_organic_aio_source_occurrences AS o
                WHERE o.capture_id = s.capture_id
                  AND o.derivation_version_id = s.derivation_version_id
                  AND o.within_capture_identity = s.within_capture_identity
          )
        LIMIT 1
        """,
        (derivation_version_id, capture_ids),
    ).fetchone()
    if orphan_sources is not None:
        raise IntegrityError("AIO source has no subordinate occurrences")
    orphan_questions = connection.execute(
        """
        SELECT 1
        FROM google_organic_related_questions AS q
        WHERE q.derivation_version_id = %s
          AND q.capture_id = ANY(%s)
          AND NOT EXISTS (
                SELECT 1
                FROM google_organic_related_question_occurrences AS o
                WHERE o.capture_id = q.capture_id
                  AND o.derivation_version_id = q.derivation_version_id
                  AND o.within_capture_identity = q.within_capture_identity
          )
        LIMIT 1
        """,
        (derivation_version_id, capture_ids),
    ).fetchone()
    if orphan_questions is not None:
        raise IntegrityError("related-question parent has no subordinate occurrences")
    for parent_table, occurrence_table, message in _CHILD_OCCURRENCE_FAMILIES:
        orphan_child = connection.execute(
            sql.SQL(
                """
                SELECT 1
                FROM {} AS parent
                WHERE parent.derivation_version_id = %s
                  AND parent.capture_id = ANY(%s)
                  AND NOT EXISTS (
                        SELECT 1
                        FROM {} AS occurrence
                        WHERE occurrence.capture_id = parent.capture_id
                          AND occurrence.derivation_version_id
                              = parent.derivation_version_id
                          AND occurrence.within_capture_identity
                              = parent.within_capture_identity
                  )
                LIMIT 1
                """
            ).format(sql.Identifier(parent_table), sql.Identifier(occurrence_table)),
            (derivation_version_id, capture_ids),
        ).fetchone()
        if orphan_child is not None:
            raise IntegrityError(message)


def _assert_child_rows_match_evidence(
    connection: Connection[Any],
    table: str,
    capture_id: str,
    columns: Sequence[str],
    intended_rows: Sequence[Mapping[str, object]],
    message: str,
) -> None:
    stored = connection.execute(
        sql.SQL(
            """
            SELECT {}
            FROM {}
            WHERE capture_id = %s AND derivation_version_id = %s
            """
        ).format(
            sql.SQL(", ").join(sql.Identifier(column) for column in columns),
            sql.Identifier(table),
        ),
        (capture_id, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID),
    ).fetchall()
    intended = [tuple(row[column] for column in columns) for row in intended_rows]
    if len(stored) != len(intended):
        raise IntegrityError(message)
    if {tuple(row) for row in stored} != set(intended):
        raise IntegrityError(message)


def _assert_expanded_children_match_evidence(
    connection: Connection[Any],
    store: EvidenceStore,
    candidates: Sequence[
        tuple[str, str, Mapping[str, object], Mapping[str, object]]
    ],
) -> None:
    """Rebuild ranked-result v2 and PF-18 child families from verified Evidence.

    This runs over every matching candidate Capture before the outer history limit, so
    damage hidden in an unreturned tail still fails closed. Missing, extra, and
    content-falsified ranked-result-v2 rows are integrity damage, as are missing,
    extra, orphan, and content-falsified child rows: each persisted set must equal
    the set the verified Capture body actually supports. Only the expanded Recipe is
    reconstructed; pinned v1 behaviour is untouched.
    """

    seen: set[str] = set()
    for capture_id, attempt_id, capture, attempt in candidates:
        if capture_id in seen:
            continue
        seen.add(capture_id)
        parameters = _parameters(attempt)
        body: bytes | None = None
        if capture.get("transport_state") != "no_response":
            body = store.read_capture_body(capture_id)
        planned = plan_google_organic_expanded_capture(
            attempt_id, capture_id, capture, parameters, body
        )
        _assert_child_rows_match_evidence(
            connection,
            RANKED_V2_TABLE,
            capture_id,
            _RANKED_V2_COLUMNS,
            planned.details[RANKED_V2_TABLE],
            f"{RANKED_V2_TABLE} rows disagree with verified Evidence",
        )
        for detail_table, columns, occurrence_table, occurrences in (
            (
                TOP_STORY_TABLE,
                _TOP_STORY_CHILD_COLUMNS,
                TOP_STORY_OCCURRENCES_TABLE,
                planned.top_story_occurrences,
            ),
            (
                VIDEO_TABLE,
                _VIDEO_CHILD_COLUMNS,
                VIDEO_OCCURRENCES_TABLE,
                planned.video_occurrences,
            ),
            (
                SITELINKS_TABLE,
                _SITELINK_CHILD_COLUMNS,
                SITELINK_OCCURRENCES_TABLE,
                planned.sitelink_occurrences,
            ),
        ):
            _assert_child_rows_match_evidence(
                connection,
                detail_table,
                capture_id,
                columns,
                planned.details[detail_table],
                f"{detail_table} rows disagree with verified Evidence",
            )
            _assert_child_rows_match_evidence(
                connection,
                occurrence_table,
                capture_id,
                _CHILD_OCCURRENCE_COLUMNS,
                occurrences,
                f"{occurrence_table} rows disagree with verified Evidence",
            )


def load_google_organic_history(
    store: EvidenceStore,
    connection: Connection[Any],
    *,
    requested_keyword: str,
    pinned_version: str | None,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble surface-explicit Google Organic history for one requested keyword."""

    resolved = resolve_provider_recipe(connection, HISTORY_ADAPTER, pinned_version)
    kinds = _recipe_kinds(connection, resolved.derivation_version_id)
    rows = connection.execute(
        """
        SELECT
            c.capture_id,
            c.attempt_id,
            o.classification,
            o.observation_count,
            c.location_code,
            c.language_code,
            c.requested_keyword,
            c.returned_keyword,
            c.returned_keyword_state,
            c.se_domain,
            c.se_domain_state,
            c.result_datetime,
            c.result_datetime_state,
            c.se_results_count,
            c.se_results_count_state,
            c.pages_count,
            c.pages_count_state,
            c.items_count,
            c.item_types
        FROM google_organic_result_context AS c
        JOIN outcomes AS o
          ON o.derivation_version_id = c.derivation_version_id
         AND o.attempt_id = c.attempt_id
         AND o.capture_id = c.capture_id
        WHERE c.requested_keyword = %s
          AND c.derivation_version_id = %s
          AND o.classification IN (
                'observation_admitted',
                'observation_admitted_empty'
          )
        """,
        (requested_keyword, resolved.derivation_version_id),
    ).fetchall()
    candidates: list[
        tuple[
            str,
            str,
            str,
            str,
            int,
            dict[str, object],
            dict[str, object],
            dict[str, object],
            dict[str, object],
        ]
    ] = []
    for row in rows:
        capture_id = str(row[0])
        attempt_id = str(row[1])
        capture = store.read_capture(capture_id)
        if capture is None:
            raise IntegrityError("derived Capture Evidence is missing")
        attempt = store.read_attempt(attempt_id)
        if attempt is None:
            raise IntegrityError("derived Attempt Evidence is missing")
        if capture.get("attempt_id") != attempt_id:
            raise IntegrityError("Capture parent does not match derived provenance")
        if (
            capture.get("adapter_contract") != HISTORY_ADAPTER
            or attempt.get("adapter_contract") != HISTORY_ADAPTER
            or attempt.get("provider") != HISTORY_PROVIDER
        ):
            raise IntegrityError("derived Evidence is not Google Organic")
        request = _request_context(
            attempt,
            context_location=_as_int(row[4], "location_code"),
            context_language=str(row[5]),
        )
        result_context = {
            "requested_keyword": str(row[6]),
            "returned_keyword": _json_field(row[8], row[7]),
            "se_domain": _json_field(row[10], row[9]),
            "provider_result_time": _json_field(row[12], row[11]),
            "se_results_count": _json_field(row[14], row[13]),
            "pages_count": _json_field(row[16], row[15]),
            "items_count": _as_int(row[17], "items_count"),
            "item_types": _json_value(row[18]),
        }
        candidates.append(
            (
                _require_text(capture, "request_started_at"),
                capture_id,
                attempt_id,
                str(row[2]),
                _as_int(row[3], "observation_count"),
                attempt,
                capture,
                request,
                result_context,
            )
        )
    _assert_history_candidates_consistent(
        connection,
        [
            (capture_id, observation_count)
            for (
                _started,
                capture_id,
                _attempt_id,
                _classification,
                observation_count,
                _attempt,
                _capture,
                _request,
                _result_context,
            ) in candidates
        ],
        resolved.derivation_version_id,
        kinds,
    )
    if resolved.derivation_version_id == GOOGLE_ORGANIC_EXPANDED_RECIPE_ID:
        _assert_expanded_children_match_evidence(
            connection,
            store,
            [
                (capture_id, attempt_id, capture, attempt)
                for (
                    _started,
                    capture_id,
                    attempt_id,
                    _classification,
                    _observation_count,
                    attempt,
                    capture,
                    _request,
                    _result_context,
                ) in candidates
            ],
        )
    unique: list[
        tuple[
            str,
            str,
            str,
            str,
            int,
            dict[str, object],
            dict[str, object],
            dict[str, object],
            dict[str, object],
        ]
    ] = []
    seen: set[str] = set()
    for item in candidates:
        capture_id = item[1]
        if capture_id in seen:
            continue
        seen.add(capture_id)
        unique.append(item)
    total_matching = len(unique)
    reverse = order == "desc"
    unique.sort(key=lambda item: (item[0], item[1]), reverse=reverse)
    selected = unique[:limit]
    build_capture = (
        _expanded_capture_group
        if resolved.derivation_version_id == GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
        else _capture_group
    )
    captures = [
        build_capture(
            connection,
            recipe=resolved,
            capture_id=capture_id,
            attempt_id=attempt_id,
            classification=classification,
            observation_count=observation_count,
            attempt=attempt,
            capture=capture,
            request=request,
            result_context=result_context,
        )
        for (
            _started,
            capture_id,
            attempt_id,
            classification,
            observation_count,
            attempt,
            capture,
            request,
            result_context,
        ) in selected
    ]
    return history_list_response(
        provider=HISTORY_PROVIDER,
        adapter_contract=HISTORY_ADAPTER,
        requested_keyword=requested_keyword,
        derivation_version_id=resolved.derivation_version_id,
        recipe_resolution=resolved.resolution,
        observation_kinds=list(kinds),
        captures=captures,
        total_matching=total_matching,
        limit=limit,
        order=order,
    )


def _capture_group(
    connection: Connection[Any],
    *,
    recipe: ResolvedProviderRecipe,
    capture_id: str,
    attempt_id: str,
    classification: str,
    observation_count: int,
    attempt: Mapping[str, object],
    capture: Mapping[str, object],
    request: Mapping[str, object],
    result_context: Mapping[str, object],
) -> dict[str, object]:
    return {
        "attempt_id": attempt_id,
        "capture_id": capture_id,
        "provider": HISTORY_PROVIDER,
        "adapter_contract": HISTORY_ADAPTER,
        "derivation_version_id": recipe.derivation_version_id,
        "authorized_at": _require_text(attempt, "authorized_at"),
        "request_started_at": _require_text(capture, "request_started_at"),
        "transport_ended_at": _require_text(capture, "transport_ended_at"),
        "request": dict(request),
        "capture_outcome": {
            "classification": classification,
            "observation_count": observation_count,
        },
        "result_context": dict(result_context),
        "serp_features": _serp_features(
            connection, capture_id, recipe.derivation_version_id
        ),
        "ranked_results": _ranked_results(
            connection, capture_id, recipe.derivation_version_id
        ),
        "ai_overview_presence": _aio_presence(
            connection, capture_id, recipe.derivation_version_id
        ),
        "ai_overview_sources": _aio_sources(
            connection, capture_id, recipe.derivation_version_id
        ),
        "related_questions": _related_questions(
            connection, capture_id, recipe.derivation_version_id
        ),
        "related_queries": _related_queries(
            connection, capture_id, recipe.derivation_version_id
        ),
    }


def _expanded_capture_group(
    connection: Connection[Any],
    *,
    recipe: ResolvedProviderRecipe,
    capture_id: str,
    attempt_id: str,
    classification: str,
    observation_count: int,
    attempt: Mapping[str, object],
    capture: Mapping[str, object],
    request: Mapping[str, object],
    result_context: Mapping[str, object],
) -> dict[str, object]:
    """Assemble the PF-18 expanded Capture document.

    Every accepted v1 family keeps its meaning; ranked results become v2 and carry
    item-timestamp and links-family state, and the three MVP child families arrive
    with their exact parent placement and subordinate occurrence testimony.
    """

    version = recipe.derivation_version_id
    return {
        "attempt_id": attempt_id,
        "capture_id": capture_id,
        "provider": HISTORY_PROVIDER,
        "adapter_contract": HISTORY_ADAPTER,
        "derivation_version_id": version,
        "authorized_at": _require_text(attempt, "authorized_at"),
        "request_started_at": _require_text(capture, "request_started_at"),
        "transport_ended_at": _require_text(capture, "transport_ended_at"),
        "request": dict(request),
        "capture_outcome": {
            "classification": classification,
            "observation_count": observation_count,
        },
        "result_context": dict(result_context),
        "serp_features": _serp_features(connection, capture_id, version),
        "ranked_results": _ranked_results_v2(connection, capture_id, version),
        "ai_overview_presence": _aio_presence(connection, capture_id, version),
        "ai_overview_sources": _aio_sources(connection, capture_id, version),
        "related_questions": _related_questions(connection, capture_id, version),
        "related_queries": _related_queries(connection, capture_id, version),
        "top_story_results": _top_story_results(connection, capture_id, version),
        "video_results": _video_results(connection, capture_id, version),
        "sitelinks": _sitelinks(connection, capture_id, version),
    }


def _ranked_results_v2(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT within_capture_identity, url, domain, title,
               description, description_state, website_name, website_name_state,
               page, position, rank_group, rank_absolute,
               organic_item_timestamp, organic_item_timestamp_state,
               links_state, links_count
        FROM google_organic_ranked_results_v2
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY page, position, rank_absolute, rank_group,
                 within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    return [
        {
            "observation_kind": ORGANIC_PLACEMENT_V2_KIND,
            "within_capture_identity": str(row[0]),
            "url": str(row[1]),
            "domain": str(row[2]),
            "title": str(row[3]),
            "description": _json_field(row[5], row[4]),
            "website_name": _json_field(row[7], row[6]),
            "page": _as_int(row[8], "page"),
            "position": str(row[9]),
            "rank_group": _as_int(row[10], "rank_group"),
            "rank_absolute": _as_int(row[11], "rank_absolute"),
            "organic_item_timestamp": _json_field(row[13], row[12]),
            "links": {
                "state": str(row[14]),
                "returned_child_count": (
                    None if row[15] is None else _as_int(row[15], "links_count")
                ),
            },
        }
        for row in rows
    ]


def _child_occurrences(
    connection: Connection[Any], table: str, capture_id: str, version: str
) -> dict[str, list[dict[str, object]]]:
    rows = connection.execute(
        sql.SQL(
            """
            SELECT within_capture_identity, child_index
            FROM {}
            WHERE capture_id = %s AND derivation_version_id = %s
            ORDER BY within_capture_identity, child_index
            """
        ).format(sql.Identifier(table)),
        (capture_id, version),
    ).fetchall()
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[0])].append(
            {"child_index": _as_int(row[1], "child_index")}
        )
    return grouped


def _top_story_results(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT within_capture_identity, parent_within_capture_identity,
               parent_page, parent_position, parent_rank_group, parent_rank_absolute,
               child_url, source, domain, title,
               top_story_item_timestamp, top_story_item_timestamp_state
        FROM google_organic_top_story_results
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY parent_page, parent_position, parent_rank_absolute,
                 parent_rank_group, child_url, within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    grouped = _child_occurrences(
        connection, "google_organic_top_story_result_occurrences", capture_id, version
    )
    return [
        {
            "observation_kind": TOP_STORY_RESULT_KIND,
            "within_capture_identity": str(row[0]),
            "parent_within_capture_identity": str(row[1]),
            "parent_page": _as_int(row[2], "parent_page"),
            "parent_position": str(row[3]),
            "parent_rank_group": _as_int(row[4], "parent_rank_group"),
            "parent_rank_absolute": _as_int(row[5], "parent_rank_absolute"),
            "child_url": str(row[6]),
            "source": str(row[7]),
            "domain": str(row[8]),
            "title": str(row[9]),
            "top_story_item_timestamp": _json_field(row[11], row[10]),
            "occurrences": grouped[str(row[0])],
        }
        for row in rows
    ]


def _video_results(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT within_capture_identity, parent_within_capture_identity,
               parent_page, parent_position, parent_rank_group, parent_rank_absolute,
               child_url, source, title,
               video_item_timestamp, video_item_timestamp_state
        FROM google_organic_video_results
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY parent_page, parent_position, parent_rank_absolute,
                 parent_rank_group, child_url, within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    grouped = _child_occurrences(
        connection, "google_organic_video_result_occurrences", capture_id, version
    )
    return [
        {
            "observation_kind": VIDEO_RESULT_KIND,
            "within_capture_identity": str(row[0]),
            "parent_within_capture_identity": str(row[1]),
            "parent_page": _as_int(row[2], "parent_page"),
            "parent_position": str(row[3]),
            "parent_rank_group": _as_int(row[4], "parent_rank_group"),
            "parent_rank_absolute": _as_int(row[5], "parent_rank_absolute"),
            "child_url": str(row[6]),
            "source": str(row[7]),
            "title": str(row[8]),
            "video_item_timestamp": _json_field(row[10], row[9]),
            "occurrences": grouped[str(row[0])],
        }
        for row in rows
    ]


def _sitelinks(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT within_capture_identity, parent_within_capture_identity,
               parent_page, parent_position, parent_rank_group, parent_rank_absolute,
               child_url, title, domain, description, description_state
        FROM google_organic_sitelinks
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY parent_page, parent_position, parent_rank_absolute,
                 parent_rank_group, child_url, within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    grouped = _child_occurrences(
        connection, "google_organic_sitelink_occurrences", capture_id, version
    )
    return [
        {
            "observation_kind": ORGANIC_SITELINK_KIND,
            "within_capture_identity": str(row[0]),
            "parent_within_capture_identity": str(row[1]),
            "parent_page": _as_int(row[2], "parent_page"),
            "parent_position": str(row[3]),
            "parent_rank_group": _as_int(row[4], "parent_rank_group"),
            "parent_rank_absolute": _as_int(row[5], "parent_rank_absolute"),
            "child_url": str(row[6]),
            "title": str(row[7]),
            "domain": str(row[8]),
            "description": _json_field(row[10], row[9]),
            "occurrences": grouped[str(row[0])],
        }
        for row in rows
    ]


def _serp_features(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT within_capture_identity, item_type, page, position,
               rank_group, rank_absolute
        FROM google_organic_serp_features
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY page, position, rank_absolute, rank_group,
                 within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    return [
        {
            "observation_kind": FEATURE_PRESENCE_KIND,
            "within_capture_identity": str(row[0]),
            "item_type": str(row[1]),
            "page": _as_int(row[2], "page"),
            "position": str(row[3]),
            "rank_group": _as_int(row[4], "rank_group"),
            "rank_absolute": _as_int(row[5], "rank_absolute"),
        }
        for row in rows
    ]


def _ranked_results(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT within_capture_identity, url, domain, title,
               description, description_state, website_name, website_name_state,
               page, position, rank_group, rank_absolute
        FROM google_organic_ranked_results
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY page, position, rank_absolute, rank_group,
                 within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    return [
        {
            "observation_kind": ORGANIC_PLACEMENT_KIND,
            "within_capture_identity": str(row[0]),
            "url": str(row[1]),
            "domain": str(row[2]),
            "title": str(row[3]),
            "description": _json_field(row[5], row[4]),
            "website_name": _json_field(row[7], row[6]),
            "page": _as_int(row[8], "page"),
            "position": str(row[9]),
            "rank_group": _as_int(row[10], "rank_group"),
            "rank_absolute": _as_int(row[11], "rank_absolute"),
        }
        for row in rows
    ]


def _aio_presence(
    connection: Connection[Any], capture_id: str, version: str
) -> dict[str, object] | None:
    row = connection.execute(
        """
        SELECT within_capture_identity, asynchronous_ai_overview,
               page, position, rank_group, rank_absolute
        FROM google_organic_aio_presence
        WHERE capture_id = %s AND derivation_version_id = %s
        """,
        (capture_id, version),
    ).fetchone()
    if row is None:
        return None
    return {
        "observation_kind": AIO_PRESENCE_KIND,
        "within_capture_identity": str(row[0]),
        "asynchronous_ai_overview": bool(row[1]),
        "page": _as_int(row[2], "page"),
        "position": str(row[3]),
        "rank_group": _as_int(row[4], "rank_group"),
        "rank_absolute": _as_int(row[5], "rank_absolute"),
    }


def _aio_sources(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    source_rows = connection.execute(
        """
        SELECT within_capture_identity, locus, url,
               domain, domain_state, title, title_state, source, source_state
        FROM google_organic_aio_sources
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY locus, url, within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    occurrence_rows = connection.execute(
        """
        SELECT within_capture_identity, locus, element_index, reference_index
        FROM google_organic_aio_source_occurrences
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY locus, element_index NULLS FIRST, reference_index
        """,
        (capture_id, version),
    ).fetchall()
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrence_rows:
        grouped[str(row[0])].append(
            {
                "locus": str(row[1]),
                "element_index": None if row[2] is None else _as_int(row[2], "element_index"),
                "reference_index": _as_int(row[3], "reference_index"),
            }
        )
    return [
        {
            "observation_kind": AIO_SOURCE_KIND,
            "within_capture_identity": str(row[0]),
            "locus": str(row[1]),
            "url": str(row[2]),
            "domain": _json_field(row[4], row[3]),
            "title": _json_field(row[6], row[5]),
            "source": _json_field(row[8], row[7]),
            "occurrences": grouped[str(row[0])],
        }
        for row in source_rows
    ]


def _related_questions(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    question_rows = connection.execute(
        """
        SELECT within_capture_identity, title
        FROM google_organic_related_questions
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY title, within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    occurrence_rows = connection.execute(
        """
        SELECT within_capture_identity, page, position,
               rank_group, rank_absolute, question_index
        FROM google_organic_related_question_occurrences
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY page, position, rank_absolute, rank_group, question_index
        """,
        (capture_id, version),
    ).fetchall()
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrence_rows:
        grouped[str(row[0])].append(
            {
                "page": _as_int(row[1], "page"),
                "position": str(row[2]),
                "rank_group": _as_int(row[3], "rank_group"),
                "rank_absolute": _as_int(row[4], "rank_absolute"),
                "question_index": _as_int(row[5], "question_index"),
            }
        )
    return [
        {
            "observation_kind": RELATED_QUESTION_KIND,
            "within_capture_identity": str(row[0]),
            "title": str(row[1]),
            "occurrences": grouped[str(row[0])],
        }
        for row in question_rows
    ]


def _related_queries(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT within_capture_identity, query
        FROM google_organic_related_queries
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY query, within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    return [
        {
            "observation_kind": RELATED_QUERY_KIND,
            "within_capture_identity": str(row[0]),
            "query": str(row[1]),
        }
        for row in rows
    ]


def _outcomes_request(attempt: Mapping[str, object]) -> dict[str, object]:
    parameters = _parameters(attempt)
    keyword = parameters.get("keyword")
    location = parameters.get("location_code")
    language = parameters.get("language_code")
    depth = parameters.get("depth")
    device = parameters.get("device")
    operating_system = parameters.get("os")
    group = parameters.get("group_organic_results")
    load_async = parameters.get("load_async_ai_overview")
    if not isinstance(keyword, str) or keyword == "":
        raise IntegrityError("verified Attempt keyword is missing")
    if type(location) is not int:
        raise IntegrityError("verified Attempt location_code is missing")
    if not isinstance(language, str) or language == "":
        raise IntegrityError("verified Attempt language_code is missing")
    if type(depth) is not int:
        raise IntegrityError("verified Attempt depth is missing")
    if not isinstance(device, str) or device == "":
        raise IntegrityError("verified Attempt device is missing")
    if not isinstance(operating_system, str) or operating_system == "":
        raise IntegrityError("verified Attempt os is missing")
    if type(group) is not bool or type(load_async) is not bool:
        raise IntegrityError("verified Attempt organic flags are missing")
    return {
        "keyword": keyword,
        "location_code": location,
        "language_code": language,
        "depth": depth,
        "device": device,
        "os": operating_system,
        "group_organic_results": group,
        "load_async_ai_overview": load_async,
    }


def load_google_organic_outcomes(
    store: EvidenceStore,
    connection: Connection[Any],
    *,
    requested_keyword: str,
    pinned_version: str | None,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble subject-filtered Google Organic Measurement Outcomes."""

    resolved = resolve_provider_recipe(connection, HISTORY_ADAPTER, pinned_version)
    recipe = load_validated_outcomes_recipe(
        connection,
        derivation_version_id=resolved.derivation_version_id,
        resolved_provider=resolved.provider,
        resolved_adapter=resolved.adapter_contract,
        expected_provider=HISTORY_PROVIDER,
        expected_adapter=HISTORY_ADAPTER,
    )
    events = load_verified_store_events(store)
    matched: list[tuple[str, dict[str, object], dict[str, object]]] = []
    for attempt_id, attempt in events.attempts.items():
        if attempt.get("adapter_contract") != HISTORY_ADAPTER:
            continue
        if attempt.get("provider") != HISTORY_PROVIDER:
            raise IntegrityError("derived Evidence is not Google Organic")
        request = _outcomes_request(attempt)
        if request["keyword"] != requested_keyword:
            continue
        matched.append((attempt_id, attempt, request))
    if not matched:
        return outcomes_list_response(
            provider=HISTORY_PROVIDER,
            adapter_contract=HISTORY_ADAPTER,
            requested_keyword=requested_keyword,
            derivation_version_id=recipe.derivation_version_id,
            recipe_resolution=resolved.resolution,
            observation_kinds=list(recipe.observation_kinds),
            outcomes=(),
            total_matching=0,
            limit=limit,
            order=order,
        )
    projected: list[tuple[str, str, dict[str, object]]] = []
    for attempt_id, attempt, request in matched:
        projected.append(
            (
                _require_text(attempt, "authorized_at"),
                attempt_id,
                project_matched_attempt(
                    connection,
                    events,
                    attempt_id=attempt_id,
                    attempt=attempt,
                    recipe=recipe,
                    request=request,
                ),
            )
        )
    reverse = order == "desc"
    projected.sort(key=lambda item: (item[0], item[1]), reverse=reverse)
    selected = projected[:limit]
    return outcomes_list_response(
        provider=HISTORY_PROVIDER,
        adapter_contract=HISTORY_ADAPTER,
        requested_keyword=requested_keyword,
        derivation_version_id=recipe.derivation_version_id,
        recipe_resolution=resolved.resolution,
        observation_kinds=list(recipe.observation_kinds),
        outcomes=[item[2] for item in selected],
        total_matching=len(projected),
        limit=limit,
        order=order,
    )


def load_google_organic_holdings(
    store: EvidenceStore,
    *,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble Recipe-independent Google Organic Holdings from verified Evidence."""

    events = load_verified_store_events(store)
    groups: dict[tuple[object, ...], dict[str, HoldingsAttempt]] = {}
    for attempt_id, attempt in events.attempts.items():
        if attempt.get("adapter_contract") != HISTORY_ADAPTER:
            continue
        if attempt.get("provider") != HISTORY_PROVIDER:
            raise IntegrityError("verified Evidence is not Google Organic")
        request = _outcomes_request(attempt)
        keyword = request["keyword"]
        if not isinstance(keyword, str) or keyword == "":
            raise IntegrityError("verified Attempt keyword is missing")
        capture_ids = events.capture_ids_by_attempt.get(attempt_id, ())
        started = None
        if capture_ids:
            started = _require_text(events.captures[capture_ids[0]], "request_started_at")
        identity = (
            keyword,
            keyword,
            request["location_code"],
            request["language_code"],
            request["depth"],
            request["device"],
            request["os"],
            request["group_organic_results"],
            request["load_async_ai_overview"],
        )
        bucket = groups.setdefault(identity, {})
        if attempt_id in bucket:
            raise IntegrityError("duplicate Attempt in Holdings group")
        bucket[attempt_id] = HoldingsAttempt(
            attempt_id=attempt_id,
            authorized_at=_require_text(attempt, "authorized_at"),
            request_started_at=started,
        )
    catalog: list[tuple[tuple[object, ...], dict[str, object]]] = []
    for group_key, members in groups.items():
        catalog.append(
            (
                group_key,
                holdings_item(
                    requested_keyword=str(group_key[0]),
                    request={
                        "keyword": group_key[1],
                        "location_code": group_key[2],
                        "language_code": group_key[3],
                        "depth": group_key[4],
                        "device": group_key[5],
                        "os": group_key[6],
                        "group_organic_results": group_key[7],
                        "load_async_ai_overview": group_key[8],
                    },
                    members=tuple(members.values()),
                ),
            )
        )
    assert_unique_holdings_groups(catalog)
    catalog.sort(key=lambda item: item[0], reverse=order == "desc")
    ordered = [item[1] for item in catalog]
    return holdings_list_response(
        provider=HISTORY_PROVIDER,
        adapter_contract=HISTORY_ADAPTER,
        holdings=ordered[:limit],
        total_matching=len(ordered),
        limit=limit,
        order=order,
    )
