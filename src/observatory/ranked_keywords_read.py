"""Read-side assembly for DataForSEO Google Ranked Keywords admitted history.

RANK-06 turns the rebuildable RANK-05 state for one verified Capture back into one
subject-bound Capture document: verified Attempt request testimony, provider result
context, four semantic Observation families, and the returned-item occurrence bridge that
connects one provider item to both a placement fact and a Ranked-local keyword-data fact.

It invents nothing. Target corpus aggregates describe a provider corpus the returned prefix
does not sample. `rank_group` and `rank_absolute` are two independently stated provider
answers and are never reconciled with each other, with `total_count`, or with returned rows.
Exact URLs are placement content, never canonical Page identity. Ranked-local keyword
enrichment is not Keyword Overview or Related Keywords identity. Monthly `(year, month)` is a
Data Period, never an acquisition time or a provider clock. Provider movement, `is_lost`,
previous rank, and every structure-local clock are provider comparison testimony, never
Observatory Capture-to-Capture change.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Final, Literal, Self

from psycopg import Connection, sql
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from observatory.capture_event import (
    RANKED_KEYWORDS_ADAPTER_CONTRACT,
    DocumentError,
    canonical_json,
    content_digest,
    validate_ranked_keywords_http_parameters,
)
from observatory.dataforseo_google_ranked_keywords import (
    CORPUS_METRICS_KIND,
    KEYWORD_DATA_KIND,
    MONTHLY_KIND,
    PROVIDER,
    RANK_SYSTEM_ABSOLUTE,
    RANK_SYSTEMS,
    RANKED_RESULT_KIND,
    REQUESTED_ITEM_TYPES,
    SE_TYPE,
)
from observatory.evidence_store import EvidenceStore, IntegrityError
from observatory.google_ranked_keywords_derive import (
    BACKLINKS_TABLE,
    CONTEXT_TABLE,
    CORPUS_METRICS_TABLE,
    INTENT_TABLE,
    ITEM_OCCURRENCES_TABLE,
    KEYWORD_DATA_TABLE,
    KEYWORD_INFO_TABLE,
    KEYWORD_SERP_TABLE,
    MONTHLY_OCCURRENCES_TABLE,
    MONTHLY_TABLE,
    PROPERTIES_TABLE,
    RANKED_KEYWORDS_RECIPE,
    RANKED_KEYWORDS_RECIPE_ID,
    RANKED_RESULTS_TABLE,
)
from observatory.provider_history import HISTORY_LIMIT_MAX
from observatory.provider_recipe import (
    IDENTITY_SCHEMA,
    IDENTITY_VERSION,
    observation_identity,
    validate_recipe,
)
from observatory.provider_recipe_selection import (
    ProviderRecipeSelectionError,
    ResolvedProviderRecipe,
    resolve_provider_recipe,
)

HISTORY_PROVIDER: Final[str] = PROVIDER
HISTORY_ADAPTER: Final[str] = RANKED_KEYWORDS_ADAPTER_CONTRACT
IJSON_MAX: Final[int] = 9007199254740991

# Exact ordered Recipe v1 `observation_kinds`. This is deliberately not
# `observation_identity.kinds`, whose order differs inside the same accepted document.
V1_KINDS: Final[tuple[str, str, str, str]] = (
    CORPUS_METRICS_KIND,
    KEYWORD_DATA_KIND,
    MONTHLY_KIND,
    RANKED_RESULT_KIND,
)

# Exact stored Recipe v1 Capture classification vocabulary, in its stored order. Ranked v1
# declares no `observation_admitted_empty` and no `reconciliation_failed`.
V1_CAPTURE_OUTCOMES: Final[tuple[str, ...]] = (
    "no_response",
    "observation_admitted",
    "provider_envelope_rejected",
    "provider_error",
    "response_partial",
    "transport_complete_non_admissible",
)
ADMITTED_CLASSIFICATIONS: Final[frozenset[str]] = frozenset({"observation_admitted"})

# The Recipe's global field-state vocabulary is five tokens, but no single RANK-05 column
# permits all five. Each domain below is the exact applicable subset RANK-03 can produce and
# RANK-05 can persist for that structure. A token outside its own domain is Recipe-v1 damage
# even though the generic SQL field-state CHECK accepts it.
OPTIONAL_FIELD_STATES: Final[frozenset[str]] = frozenset(
    {"absent", "json_null", "stated"}
)
MEMBER_FIELD_STATES: Final[frozenset[str]] = frozenset(
    {"absent", "inapplicable", "json_null", "stated"}
)
CORPUS_COUNT_STATES: Final[frozenset[str]] = frozenset({"inapplicable", "stated"})
CORPUS_DECIMAL_STATES: Final[frozenset[str]] = frozenset(
    {"absent", "inapplicable", "json_null", "stated"}
)
UNSUPPORTED_CHILD_STATES: Final[frozenset[str]] = frozenset({"absent", "json_null"})
BING_STATES: Final[frozenset[str]] = frozenset({"absent", "json_null"})
CLICKSTREAM_STATES: Final[frozenset[str]] = frozenset({"not_requested"})

AGGREGATE_FAMILIES: Final[tuple[str, ...]] = REQUESTED_ITEM_TYPES
# Presentation rank only. Lexical family order would reorder provider-significant request
# testimony, so the accepted family sequence is explicit and is never identity.
FAMILY_RANK: Final[dict[str, int]] = {
    family: index for index, family in enumerate(AGGREGATE_FAMILIES)
}
RANK_SYSTEM_RANK: Final[dict[str, int]] = {
    system: index for index, system in enumerate(RANK_SYSTEMS)
}
# Recipe v1 emits this exact ten-element cross-product for every admitted Capture, including
# all-zero families and a successful zero-returned-item result.
CORPUS_COMBINATIONS: Final[frozenset[tuple[str, str]]] = frozenset(
    (family, system) for family in AGGREGATE_FAMILIES for system in RANK_SYSTEMS
)

_SEMANTIC_KEY_COLUMNS: Final[tuple[str, ...]] = (
    "within_capture_identity",
    "observation_kind",
)
BUCKET_COLUMNS: Final[tuple[str, ...]] = (
    "pos_1",
    "pos_2_3",
    "pos_4_10",
    "pos_11_20",
    "pos_21_30",
    "pos_31_40",
    "pos_41_50",
    "pos_51_60",
    "pos_61_70",
    "pos_71_80",
    "pos_81_90",
    "pos_91_100",
)
MOVEMENT_COLUMNS: Final[tuple[str, ...]] = ("is_new", "is_up", "is_down", "is_lost")

# Every persisted RANK-05 content column is projected. `tests/test_api_ranked_keywords.py`
# pins these tuples against information_schema so a future column cannot be silently dropped
# from consumer-visible testimony.
CORPUS_METRICS_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "requested_target",
    "aggregate_family",
    "rank_system",
    *BUCKET_COLUMNS,
    *MOVEMENT_COLUMNS,
    "count",
    "count_state",
    "etv",
    "etv_state",
    "estimated_paid_traffic_cost",
    "estimated_paid_traffic_cost_state",
    "clickstream_etv_state",
    "clickstream_gender_distribution_state",
    "clickstream_age_distribution_state",
)
RANKED_ELEMENT_COLUMNS: Final[tuple[str, ...]] = (
    "ranked_element_se_type",
    "ranked_element_se_type_state",
    "ranked_element_check_url",
    "ranked_element_check_url_state",
    "ranked_element_se_results_count",
    "ranked_element_se_results_count_state",
    "ranked_element_keyword_difficulty",
    "ranked_element_keyword_difficulty_state",
    "ranked_element_is_lost",
    "ranked_element_is_lost_state",
    "ranked_element_serp_item_types",
    "ranked_element_serp_item_types_state",
    "ranked_element_last_updated_time",
    "ranked_element_last_updated_time_state",
    "ranked_element_previous_updated_time",
    "ranked_element_previous_updated_time_state",
)
SERP_ITEM_COLUMNS: Final[tuple[str, ...]] = (
    "serp_item_se_type",
    "serp_item_se_type_state",
    "url",
    "position",
    "position_state",
    "xpath",
    "xpath_state",
    "domain",
    "domain_state",
    "main_domain",
    "main_domain_state",
    "website_name",
    "website_name_state",
    "relative_url",
    "relative_url_state",
    "title",
    "title_state",
    "description",
    "description_state",
    "breadcrumb_state",
    "pre_snippet_state",
    "highlighted_state",
    "is_image",
    "is_image_state",
    "is_video",
    "is_video_state",
    "is_featured_snippet",
    "is_featured_snippet_state",
    "is_malicious",
    "is_malicious_state",
    "amp_version",
    "amp_version_state",
    "etv",
    "etv_state",
    "estimated_paid_traffic_cost",
    "estimated_paid_traffic_cost_state",
    "clickstream_etv_state",
    "rank_changes_state",
    "rank_changes_is_new",
    "rank_changes_is_new_state",
    "rank_changes_is_up",
    "rank_changes_is_up_state",
    "rank_changes_is_down",
    "rank_changes_is_down_state",
    "rank_changes_previous_rank_absolute",
    "rank_changes_previous_rank_absolute_state",
    "rank_info_state",
    "rank_info_page_rank",
    "rank_info_page_rank_state",
    "rank_info_main_domain_rank",
    "rank_info_main_domain_rank_state",
    "about_this_result_state",
    "backlinks_info_state",
    "extended_snippet_state",
    "links_state",
    "rating_state",
)
RANKED_RESULT_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "requested_target",
    "keyword",
    "serp_item_type",
    "rank_group",
    "rank_absolute",
    *RANKED_ELEMENT_COLUMNS,
    *SERP_ITEM_COLUMNS,
)
KEYWORD_DATA_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "requested_target",
    "keyword",
    "location_code",
    "location_code_state",
    "language_code",
    "language_code_state",
    "se_type",
    "se_type_state",
    "keyword_info_state",
    "keyword_properties_state",
    "avg_backlinks_state",
    "search_intent_state",
    "keyword_serp_info_state",
    "bing_normalized_state",
    "clickstream_normalized_state",
    "clickstream_keyword_info_state",
)
KEYWORD_INFO_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "se_type",
    "se_type_state",
    "keyword_info_last_updated_time",
    "keyword_info_last_updated_time_state",
    "competition",
    "competition_state",
    "competition_level",
    "competition_level_state",
    "cpc",
    "cpc_state",
    "search_volume",
    "search_volume_state",
    "low_top_of_page_bid",
    "low_top_of_page_bid_state",
    "high_top_of_page_bid",
    "high_top_of_page_bid_state",
    "categories",
    "categories_state",
    "monthly_searches_state",
    "search_volume_trend_state",
    "trend_monthly",
    "trend_monthly_state",
    "trend_quarterly",
    "trend_quarterly_state",
    "trend_yearly",
    "trend_yearly_state",
)
PROPERTIES_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "se_type",
    "se_type_state",
    "core_keyword",
    "core_keyword_state",
    "synonym_clustering_algorithm",
    "synonym_clustering_algorithm_state",
    "keyword_difficulty",
    "keyword_difficulty_state",
    "detected_language",
    "detected_language_state",
    "is_another_language",
    "is_another_language_state",
)
BACKLINKS_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "se_type",
    "se_type_state",
    "backlinks",
    "backlinks_state",
    "dofollow",
    "dofollow_state",
    "referring_pages",
    "referring_pages_state",
    "referring_domains",
    "referring_domains_state",
    "referring_main_domains",
    "referring_main_domains_state",
    "rank",
    "rank_state",
    "main_domain_rank",
    "main_domain_rank_state",
    "avg_backlinks_last_updated_time",
    "avg_backlinks_last_updated_time_state",
)
INTENT_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "se_type",
    "se_type_state",
    "main_intent",
    "main_intent_state",
    "foreign_intent",
    "foreign_intent_state",
    "search_intent_last_updated_time",
    "search_intent_last_updated_time_state",
)
KEYWORD_SERP_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "se_type",
    "se_type_state",
    "check_url",
    "check_url_state",
    "serp_item_types",
    "serp_item_types_state",
    "se_results_count",
    "se_results_count_state",
    "keyword_serp_last_updated_time",
    "keyword_serp_last_updated_time_state",
    "keyword_serp_previous_updated_time",
    "keyword_serp_previous_updated_time_state",
)
MONTHLY_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "requested_target",
    "keyword",
    "year",
    "month",
    "search_volume",
)
# The occurrence bridge is keyed by provider item index and carries no Observation envelope
# of its own: it names both semantic parents instead.
ITEM_OCCURRENCE_COLUMNS: Final[tuple[str, ...]] = (
    "item_index",
    "ranked_result_identity",
    "ranked_result_kind",
    "keyword_data_identity",
    "keyword_data_kind",
    "item_se_type",
)
MONTHLY_OCCURRENCE_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "item_index",
)
CONTEXT_COLUMNS: Final[tuple[str, ...]] = (
    "attempt_id",
    "requested_target",
    "request_location_code",
    "request_language_code",
    "request_item_types",
    "request_ignore_synonyms",
    "request_include_clickstream_data",
    "request_limit",
    "request_offset",
    "request_load_rank_absolute",
    "request_historical_serp_mode",
    "request_order_by",
    "result_target",
    "result_target_state",
    "result_location_code",
    "result_location_code_state",
    "result_language_code",
    "result_language_code_state",
    "result_se_type",
    "result_se_type_state",
    "total_count",
    "items_count",
)

# Membership is context-anchored, not envelope-anchored. The Outcome is LEFT JOINed on the
# full (derivation_version_id, attempt_id, capture_id) tuple so a missing or foreign-Attempt
# Outcome behind a matching context surfaces as integrity damage instead of vanishing.
CANDIDATE_COLUMNS: Final[tuple[str, ...]] = ("capture_id", *CONTEXT_COLUMNS)
CANDIDATE_ROW_KEYS: Final[tuple[str, ...]] = (
    *CANDIDATE_COLUMNS,
    "classification",
    "observation_count",
)
CANDIDATE_SQL: Final[str] = (
    "SELECT "
    + ", ".join(f"c.{column}" for column in CANDIDATE_COLUMNS)
    + ", o.classification, o.observation_count"
    + f" FROM {CONTEXT_TABLE} AS c"
    + " LEFT JOIN outcomes AS o"
    + " ON o.derivation_version_id = c.derivation_version_id"
    + " AND o.attempt_id = c.attempt_id"
    + " AND o.capture_id = c.capture_id"
    + " WHERE c.requested_target = %s AND c.derivation_version_id = %s"
)

# Reverse subject-membership probe. Context anchoring alone cannot see a Capture whose only
# missing row is the result context, because nothing in PostgreSQL references that row.
SUBJECT_PARENT_TABLES: Final[tuple[str, ...]] = (
    CORPUS_METRICS_TABLE,
    RANKED_RESULTS_TABLE,
    KEYWORD_DATA_TABLE,
    MONTHLY_TABLE,
)

_CHILD_TABLES: Final[tuple[tuple[str, str, str, tuple[str, ...]], ...]] = (
    ("keyword_info", KEYWORD_INFO_TABLE, "keyword_info_state", KEYWORD_INFO_COLUMNS),
    (
        "keyword_properties",
        PROPERTIES_TABLE,
        "keyword_properties_state",
        PROPERTIES_COLUMNS,
    ),
    ("avg_backlinks", BACKLINKS_TABLE, "avg_backlinks_state", BACKLINKS_COLUMNS),
    ("search_intent", INTENT_TABLE, "search_intent_state", INTENT_COLUMNS),
    (
        "keyword_serp_info",
        KEYWORD_SERP_TABLE,
        "keyword_serp_info_state",
        KEYWORD_SERP_COLUMNS,
    ),
)

RANKED_OUTER_HISTORY_KEYS: Final[frozenset[str]] = frozenset(
    {
        "provider",
        "adapter_contract",
        "requested_target",
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
_CAPTURE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "attempt_id",
        "capture_id",
        "provider",
        "adapter_contract",
        "derivation_version_id",
        "authorized_at",
        "request_started_at",
        "transport_ended_at",
        "request",
        "capture_outcome",
        "result_context",
        "corpus_metrics",
        "ranked_results",
        "keyword_data",
        "monthly_search_volume",
        "item_occurrences",
    }
)
_REQUEST_KEYS: Final[frozenset[str]] = frozenset(
    {
        "target",
        "location_code",
        "language_code",
        "item_types",
        "ignore_synonyms",
        "include_clickstream_data",
        "limit",
        "offset",
        "load_rank_absolute",
        "historical_serp_mode",
        "order_by",
    }
)
_RESULT_CONTEXT_KEYS: Final[frozenset[str]] = frozenset(
    {"target", "location_code", "language_code", "se_type", "total_count", "items_count"}
)

_GRAIN: Final[str] = (
    "Admitted, subject-bound Ranked Keywords Capture-document history under Recipe v1. "
    "This list grain is whole Capture documents, not Observation envelopes, corpus "
    "aggregate facts, ranked placements, Ranked-local keyword facts, monthly Data Period "
    "facts, returned-item occurrences, provider total_count, or provider items_count."
)
_EMPTY: Final[str] = (
    "Empty admitted history (total_matching 0, captures empty) means only that no matching "
    "admitted Capture document exists under this exact route, requested_target, and "
    "Recipe v1. It does not mean never measured, failed, refused, unresolved, "
    "provider-rejected, 'the target ranks for nothing', or absence from a provider corpus. "
    "RANK-06 exposes no Ranked Measurement Outcomes and no Ranked Holdings, so an API-only "
    "consumer cannot distinguish those states from this route."
)
_ORDER: Final[str] = (
    "Echo of the validated query order. Deterministic outer ordering is "
    "(request_started_at, capture_id); descending reverses that complete key before "
    "limiting. This is not provider item order and never reorders inner collections."
)
_HAS_MORE: Final[str] = (
    "True when total_matching exceeds returned_count. Discloses an omitted outer "
    "Capture-history tail. It is not pagination, a cursor, authorization to fetch another "
    "page, or a statement about unreturned provider corpus rows."
)
_COUNT: Final[str] = (
    "Semantic Observation envelopes admitted for this Capture: ten corpus facts plus the "
    "distinct ranked-result, Ranked-local keyword-data, and monthly semantic parents. It "
    "does not count provider items, returned-item occurrences, monthly occurrences, "
    "provider items_count, provider total_count, URLs, keywords, or rank buckets."
)
_PROVIDER_COUNTS: Final[str] = (
    "Exact provider result testimony. total_count is the provider's own corpus claim for "
    "this target and items_count is the number of rows this one closed exchange returned. "
    "They are independent: the returned rows are a bounded prefix of the closed request "
    "(limit/offset below), not a sample, and unreturned corpus rows are unknown rather than "
    "absent, unranked, or lost. No completeness, truncation, coverage percentage, or "
    "continuation is stated or implied."
)
_CORPUS: Final[str] = (
    "Provider target-level aggregate testimony about a corpus the returned item prefix does "
    "not sample. It is never the returned item set, and no arithmetic reconciles it with "
    "total_count, items_count, returned rows, or the sibling rank system."
)
_RANK_SYSTEM: Final[str] = (
    "Which provider rank system stated this aggregate: rank_group is provider "
    "metrics.<family>, rank_absolute is provider metrics_absolute.<family>. They are two "
    "independently stated provider answers about the same target and family and may "
    "disagree arithmetically. Observatory never reconciles them."
)
_MOVEMENT: Final[str] = (
    "Provider movement counts. Their names do not make them booleans, and they are provider "
    "comparison testimony against the provider's own prior state, never an Observatory "
    "Capture-to-Capture delta."
)
_PLACEMENT: Final[str] = (
    "One provider ranking placement for this requested target: keyword, open SERP item "
    "type, and both rank axes. Exact URL is placement content, not identity, so the same "
    "URL at two accepted placements is two facts. No canonical Page, domain entity, URL "
    "normalization, apex/www equivalence, or cross-surface join is applied."
)
_URL: Final[str] = (
    "Exact provider URL string. Not normalized, resolved, fetched, deduplicated, or treated "
    "as a canonical Page identity."
)
_KEYWORD_ENRICHMENT: Final[str] = (
    "Ranked-local provider keyword testimony returned because this target ranked for the "
    "keyword. The requested target is testimony scope, not a claim that search volume, CPC, "
    "or intent intrinsically depends on the target. It is not Keyword Overview or Related "
    "Keywords identity even where the nested provider JSON looks similar."
)
_OCCURRENCE: Final[str] = (
    "Provider occurrence/order testimony from the returned items array. The provider item "
    "index preserves what the provider returned and where; it is never part of any semantic "
    "identity and never a rank."
)
_BRIDGE: Final[str] = (
    "One returned provider item. It links exactly one ranked placement fact and exactly one "
    "Ranked-local keyword-data fact, which is why it is a sibling collection rather than a "
    "child of either family. " + _OCCURRENCE
)
_PERIOD: Final[str] = (
    "Provider-stated calendar Data Period. It is not a Capture time, a provider update "
    "clock, a recurrence, or current search demand."
)
_MONTHLY_VOLUME: Final[str] = (
    "Exact provider monthly search volume for this Data Period. A stated zero is a stated "
    "provider value, never absence."
)
_CURRENT_VOLUME: Final[str] = (
    "Current provider search demand for this keyword. It is an independent provider fact "
    "and is never derived from, replaced by, or checked against the newest monthly point; "
    "the two legitimately disagree."
)
_CLOCKS: Final[str] = (
    "Structure-local provider update clock. It belongs only to the provider structure that "
    "stated it, never fills or is filled by a sibling clock, and never inherits Capture "
    "time. There is no universal last_updated or provider_update_time in this contract."
)
_TIME: Final[str] = (
    "Observatory acquisition provenance from verified Evidence. It is not a provider update "
    "clock and not a Data Period."
)
_STATE: Final[str] = (
    "Exact lower-case Recipe v1 field state for this persisted column, with value non-null "
    "exactly when state is stated. Missing, provider JSON null, request-disabled, and "
    "recipe-inapplicable never collapse into one another or into a silent null."
)
_STATE_ONLY: Final[str] = (
    "Field state only. Recipe v1 persists no value for this column, so none is invented."
)
_MEMBER_STATE: Final[str] = (
    "Member of an inline provider object. When the enclosing object is not stated, this "
    "member carries the Recipe-v1 state 'inapplicable' rather than a collapsed absence. "
    + _STATE
)
_ENCLOSING_STATE: Final[str] = (
    "State of the enclosing provider object. The typed child is present exactly when the "
    "state is stated."
)
_SE_TYPE_STATE: Final[str] = (
    "Structure-local provider se_type. Recipe v1 admits only the exact value 'google'. "
    + _STATE
)
_PROSE: Final[str] = (
    "Field state only. Under the accepted Product Option 1 boundary this provider prose "
    "keeps its ABSENT/JSON_NULL/STATED distinction while the text value stays Evidence-only "
    "and is never served here. Promoting the value requires a new Recipe identity plus an "
    "explicit retention, terms, and redistribution decision."
)
_UNSUPPORTED: Final[str] = (
    "Field state only for a provider child the accepted parser has never observed populated. "
    "It is exactly absent or json_null; a populated shape is parser-version drift and is "
    "rejected before derivation rather than guessed."
)
_CLICKSTREAM: Final[str] = (
    "Request-disabled clickstream locus. The closed adapter freezes "
    "include_clickstream_data to false, so this is exactly not_requested: it is neither a "
    "provider failure nor an absence."
)
_ECHO: Final[str] = (
    "Provider result-level restatement. Verified Attempt parameters remain request "
    "authority; a disagreement here is preserved provider testimony and is never repaired, "
    "and it never decides history membership."
)
_REQUEST_AUTHORITY: Final[str] = (
    "Exact verified Attempt request testimony for this closed one-exchange adapter. It is "
    "the request authority the persisted result context is checked against."
)
_IDENTITY: Final[str] = (
    "Recipe-v1 identity digest recomputed from the verified Attempt target plus this row's "
    "remaining persisted axes. Within-Capture only; it is not cross-Capture identity."
)


class UnsupportedRankedKeywordsRecipe(ProviderRecipeSelectionError):
    """Resolved Recipe is not the accepted Ranked Keywords v1 identity."""


OptionalStateToken = Literal["absent", "json_null", "stated"]
MemberStateToken = Literal["absent", "inapplicable", "json_null", "stated"]
CorpusCountStateToken = Literal["inapplicable", "stated"]
CorpusDecimalStateToken = Literal["absent", "inapplicable", "json_null", "stated"]
UnsupportedStateToken = Literal["absent", "json_null"]
ClickstreamStateToken = Literal["not_requested"]


def _agree(state: str, value: object) -> None:
    if (value is None) == (state == "stated"):
        raise ValueError("value is present exactly when state is stated")


# --------------------------------------------------------------------------------------
# Value/state pair models
# --------------------------------------------------------------------------------------


class RankedKeywordsTextField(BaseModel):
    """Provider text testimony persisted as a value/state column pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_STATE)
    value: str | None = Field(description=_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsCountField(BaseModel):
    """Non-negative provider integer testimony as a value/state pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_STATE)
    value: int | None = Field(ge=0, le=IJSON_MAX, description=_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsBoolField(BaseModel):
    """Provider boolean testimony as a value/state pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_STATE)
    value: bool | None = Field(description=_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsDecimalField(BaseModel):
    """Decimal-capable provider NUMERIC testimony as a value/state pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_STATE)
    value: str | None = Field(
        description=(
            "Exact stored decimal rendered as a plain decimal string with no exponent and "
            "no binary-float round trip. " + _STATE
        )
    )

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsSeTypeField(BaseModel):
    """Closed provider se_type testimony as a value/state pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_SE_TYPE_STATE)
    value: Literal["google"] | None = Field(description=_SE_TYPE_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsIntArrayField(BaseModel):
    """Ordered provider integer array testimony as a value/state pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_STATE)
    value: list[int] | None = Field(
        description=(
            "Exact ordered provider array preserving duplicates. A stated-empty array is "
            "an empty list, never null. " + _STATE
        )
    )

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsTextArrayField(BaseModel):
    """Ordered provider string array testimony as a value/state pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_STATE)
    value: list[str] | None = Field(
        description=(
            "Exact ordered provider array preserving duplicates. A stated-empty array is "
            "an empty list, never null. " + _STATE
        )
    )

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsMemberCountField(BaseModel):
    """Non-negative inline-object member as a value/state pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: MemberStateToken = Field(description=_MEMBER_STATE)
    value: int | None = Field(ge=0, le=IJSON_MAX, description=_MEMBER_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsMemberSignedField(BaseModel):
    """Signed inline-object member as a value/state pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: MemberStateToken = Field(description=_MEMBER_STATE)
    value: int | None = Field(ge=-IJSON_MAX, le=IJSON_MAX, description=_MEMBER_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsMemberBoolField(BaseModel):
    """Boolean inline-object member as a value/state pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: MemberStateToken = Field(description=_MEMBER_STATE)
    value: bool | None = Field(description=_MEMBER_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsCorpusCountField(BaseModel):
    """Provider corpus count. Stated on rank_group, inapplicable on rank_absolute."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: CorpusCountStateToken = Field(
        description=(
            "Exactly 'stated' under rank_group and exactly 'inapplicable' under "
            "rank_absolute, where the provider states no count. Inapplicable is a "
            "recipe-defined structural absence, not provider JSON null. " + _CORPUS
        )
    )
    value: int | None = Field(ge=0, le=IJSON_MAX, description=_CORPUS)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsCorpusDecimalField(BaseModel):
    """Provider corpus decimal. Inapplicable exactly under rank_absolute."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: CorpusDecimalStateToken = Field(
        description=(
            "Ordinary provider states under rank_group and exactly 'inapplicable' under "
            "rank_absolute. Nothing is ever synthesized from the sibling rank system. "
            + _CORPUS
        )
    )
    value: str | None = Field(
        description=(
            "Exact stored decimal rendered as a plain decimal string with no exponent and "
            "no binary-float round trip. " + _CORPUS
        )
    )

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


# --------------------------------------------------------------------------------------
# Corpus aggregate testimony
# --------------------------------------------------------------------------------------


class RankedKeywordsPositionBuckets(BaseModel):
    """Twelve provider position buckets for one aggregate family and rank system."""

    model_config = ConfigDict(extra="forbid", strict=True)

    pos_1: int = Field(ge=0, le=IJSON_MAX, description=_CORPUS)
    pos_2_3: int = Field(ge=0, le=IJSON_MAX, description=_CORPUS)
    pos_4_10: int = Field(ge=0, le=IJSON_MAX, description=_CORPUS)
    pos_11_20: int = Field(ge=0, le=IJSON_MAX, description=_CORPUS)
    pos_21_30: int = Field(ge=0, le=IJSON_MAX, description=_CORPUS)
    pos_31_40: int = Field(ge=0, le=IJSON_MAX, description=_CORPUS)
    pos_41_50: int = Field(ge=0, le=IJSON_MAX, description=_CORPUS)
    pos_51_60: int = Field(ge=0, le=IJSON_MAX, description=_CORPUS)
    pos_61_70: int = Field(ge=0, le=IJSON_MAX, description=_CORPUS)
    pos_71_80: int = Field(ge=0, le=IJSON_MAX, description=_CORPUS)
    pos_81_90: int = Field(ge=0, le=IJSON_MAX, description=_CORPUS)
    pos_91_100: int = Field(ge=0, le=IJSON_MAX, description=_CORPUS)


class RankedKeywordsMovementCounts(BaseModel):
    """Provider aggregate movement counts for one family and rank system."""

    model_config = ConfigDict(extra="forbid", strict=True)

    is_new: int = Field(ge=0, le=IJSON_MAX, description=_MOVEMENT)
    is_up: int = Field(ge=0, le=IJSON_MAX, description=_MOVEMENT)
    is_down: int = Field(ge=0, le=IJSON_MAX, description=_MOVEMENT)
    is_lost: int = Field(ge=0, le=IJSON_MAX, description=_MOVEMENT)


class RankedKeywordsCorpusMetricsFact(BaseModel):
    """One target corpus aggregate Observation for one family and rank system."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal["dataforseo.google.ranked_keywords.corpus_metrics.v1"]
    within_capture_identity: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$", description=_IDENTITY
    )
    requested_target: str = Field(min_length=1, description=_REQUEST_AUTHORITY)
    aggregate_family: Literal[
        "organic", "paid", "featured_snippet", "local_pack", "ai_overview_reference"
    ] = Field(
        description=(
            "Exact requested aggregate family. Recipe v1 emits all five families under both "
            "rank systems for every admitted Capture, including all-zero families. "
            + _CORPUS
        )
    )
    rank_system: Literal["rank_group", "rank_absolute"] = Field(description=_RANK_SYSTEM)
    position_buckets: RankedKeywordsPositionBuckets
    movement_counts: RankedKeywordsMovementCounts
    count: RankedKeywordsCorpusCountField
    etv: RankedKeywordsCorpusDecimalField
    estimated_paid_traffic_cost: RankedKeywordsCorpusDecimalField
    clickstream_etv_state: ClickstreamStateToken = Field(
        description=_CLICKSTREAM + " " + _STATE_ONLY
    )
    clickstream_gender_distribution_state: ClickstreamStateToken = Field(
        description=_CLICKSTREAM + " " + _STATE_ONLY
    )
    clickstream_age_distribution_state: ClickstreamStateToken = Field(
        description=_CLICKSTREAM + " " + _STATE_ONLY
    )

    @model_validator(mode="after")
    def _require_rank_system_applicability(self) -> Self:
        decimals = (self.etv, self.estimated_paid_traffic_cost)
        if self.rank_system == RANK_SYSTEM_ABSOLUTE:
            if self.count.state != "inapplicable" or any(
                field.state != "inapplicable" for field in decimals
            ):
                raise ValueError(
                    "rank_absolute count, etv, and cost are exactly inapplicable"
                )
        else:
            if self.count.state != "stated":
                raise ValueError("rank_group count is exactly stated")
            if any(field.state == "inapplicable" for field in decimals):
                raise ValueError("rank_group etv and cost are never inapplicable")
        return self


# --------------------------------------------------------------------------------------
# Ranked placement testimony
# --------------------------------------------------------------------------------------


class RankedKeywordsRankedElement(BaseModel):
    """Provider ranked_serp_element testimony for one admitted placement.

    These six members are restated on the keyword `serp_info` path. They are separate
    provider paths and are never reconciled with it.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    se_type: RankedKeywordsSeTypeField
    check_url: RankedKeywordsTextField = Field(description=_URL)
    se_results_count: RankedKeywordsCountField = Field(
        description=(
            "Exact provider search-engine result count for the keyword's SERP. Not an "
            "Observatory count, corpus size, or completeness claim."
        )
    )
    keyword_difficulty: RankedKeywordsCountField = Field(
        description=(
            "Ranked-element provider keyword difficulty. It is a different provider fact "
            "from keyword_properties.keyword_difficulty and is never reconciled with it."
        )
    )
    is_lost: RankedKeywordsBoolField = Field(
        description=(
            "Provider loss testimony against the provider's own prior state. It is not an "
            "Observatory Capture-to-Capture change and implies no history."
        )
    )
    serp_item_types: RankedKeywordsTextArrayField = Field(
        description=(
            "Exact ordered provider array of SERP composition types, duplicates preserved. "
            "SERP composition is not a claim that this target participated in every listed "
            "type."
        )
    )
    last_updated_time: RankedKeywordsTextField = Field(description=_CLOCKS)
    previous_updated_time: RankedKeywordsTextField = Field(description=_CLOCKS)


class RankedKeywordsRankChanges(BaseModel):
    """Inline provider rank_changes object state plus its persisted members."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_ENCLOSING_STATE)
    is_new: RankedKeywordsMemberBoolField = Field(description=_MOVEMENT)
    is_up: RankedKeywordsMemberBoolField = Field(description=_MOVEMENT)
    is_down: RankedKeywordsMemberBoolField = Field(description=_MOVEMENT)
    previous_rank_absolute: RankedKeywordsMemberCountField = Field(
        description=(
            "Provider-stated previous absolute rank. Provider comparison testimony only, "
            "never an Observatory Capture-to-Capture delta or a second placement fact."
        )
    )

    @model_validator(mode="after")
    def _require_member_applicability(self) -> Self:
        _require_inline_members(
            self.state,
            (
                self.is_new.state,
                self.is_up.state,
                self.is_down.state,
                self.previous_rank_absolute.state,
            ),
            "rank_changes",
        )
        return self


class RankedKeywordsRankInfo(BaseModel):
    """Inline provider rank_info object state plus its persisted members."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_ENCLOSING_STATE)
    page_rank: RankedKeywordsMemberCountField
    main_domain_rank: RankedKeywordsMemberCountField = Field(
        description=(
            "Provider placement-level main domain rank. It is a different provider fact "
            "from avg_backlinks_info.main_domain_rank and is never reconciled with it."
        )
    )

    @model_validator(mode="after")
    def _require_member_applicability(self) -> Self:
        _require_inline_members(
            self.state,
            (self.page_rank.state, self.main_domain_rank.state),
            "rank_info",
        )
        return self


class RankedKeywordsSerpItem(BaseModel):
    """Provider serp_item testimony for one admitted placement."""

    model_config = ConfigDict(extra="forbid", strict=True)

    se_type: RankedKeywordsSeTypeField
    url: str = Field(min_length=1, description=_URL + " " + _PLACEMENT)
    position: RankedKeywordsTextField = Field(
        description=(
            "Exact provider layout position string, such as a column label. It is not a "
            "rank; rank_group and rank_absolute are the rank axes."
        )
    )
    xpath: RankedKeywordsTextField = Field(
        description="Exact provider layout XPath testimony."
    )
    domain: RankedKeywordsTextField = Field(description=_URL)
    main_domain: RankedKeywordsTextField = Field(description=_URL)
    website_name: RankedKeywordsTextField = Field(
        description="Exact provider website-name string. Not a brand or entity identity."
    )
    relative_url: RankedKeywordsTextField = Field(description=_URL)
    title: RankedKeywordsTextField
    description: RankedKeywordsTextField
    breadcrumb_state: OptionalStateToken = Field(description=_PROSE)
    pre_snippet_state: OptionalStateToken = Field(
        description=(
            "Field state of provider pre_snippet. The value is arbitrary provider text even "
            "when it looks like a date, and it is never parsed as a clock. " + _PROSE
        )
    )
    highlighted_state: OptionalStateToken = Field(description=_PROSE)
    is_image: RankedKeywordsBoolField
    is_video: RankedKeywordsBoolField
    is_featured_snippet: RankedKeywordsBoolField
    is_malicious: RankedKeywordsBoolField
    amp_version: RankedKeywordsBoolField
    etv: RankedKeywordsDecimalField = Field(
        description="Provider estimated traffic value for this placement."
    )
    estimated_paid_traffic_cost: RankedKeywordsDecimalField
    clickstream_etv_state: ClickstreamStateToken = Field(
        description=_CLICKSTREAM + " " + _STATE_ONLY
    )
    rank_changes: RankedKeywordsRankChanges
    rank_info: RankedKeywordsRankInfo
    about_this_result_state: UnsupportedStateToken = Field(description=_UNSUPPORTED)
    backlinks_info_state: UnsupportedStateToken = Field(description=_UNSUPPORTED)
    extended_snippet_state: UnsupportedStateToken = Field(description=_UNSUPPORTED)
    links_state: UnsupportedStateToken = Field(description=_UNSUPPORTED)
    rating_state: UnsupportedStateToken = Field(description=_UNSUPPORTED)


class RankedKeywordsRankedResultFact(BaseModel):
    """One ranked placement semantic Observation."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal["dataforseo.google.ranked_keywords.ranked_result.v1"]
    within_capture_identity: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$", description=_IDENTITY
    )
    requested_target: str = Field(min_length=1, description=_REQUEST_AUTHORITY)
    keyword: str = Field(
        min_length=1,
        description=(
            "Exact provider keyword for this placement. Not trimmed, case-folded, "
            "normalized, or replaced by core_keyword."
        ),
    )
    serp_item_type: str = Field(
        min_length=1,
        description=(
            "Exact open provider SERP item type. Observatory imposes no closed vocabulary "
            "here and does not import Google Organic's item-type set."
        ),
    )
    rank_group: int = Field(ge=0, le=IJSON_MAX, description=_PLACEMENT)
    rank_absolute: int = Field(ge=0, le=IJSON_MAX, description=_PLACEMENT)
    ranked_element: RankedKeywordsRankedElement
    serp_item: RankedKeywordsSerpItem


# --------------------------------------------------------------------------------------
# Ranked-local keyword enrichment testimony
# --------------------------------------------------------------------------------------


class RankedKeywordsSearchVolumeTrend(BaseModel):
    """Inline provider search_volume_trend object state plus its persisted members."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_ENCLOSING_STATE)
    monthly: RankedKeywordsMemberSignedField
    quarterly: RankedKeywordsMemberSignedField
    yearly: RankedKeywordsMemberSignedField

    @model_validator(mode="after")
    def _require_member_applicability(self) -> Self:
        _require_inline_members(
            self.state,
            (self.monthly.state, self.quarterly.state, self.yearly.state),
            "search_volume_trend",
        )
        return self


class RankedKeywordsKeywordInfo(BaseModel):
    """Exact persisted provider keyword_info testimony."""

    model_config = ConfigDict(extra="forbid", strict=True)

    se_type: RankedKeywordsSeTypeField
    keyword_info_last_updated_time: RankedKeywordsTextField = Field(description=_CLOCKS)
    competition: RankedKeywordsDecimalField
    competition_level: RankedKeywordsTextField
    cpc: RankedKeywordsDecimalField
    search_volume: RankedKeywordsCountField = Field(description=_CURRENT_VOLUME)
    low_top_of_page_bid: RankedKeywordsDecimalField
    high_top_of_page_bid: RankedKeywordsDecimalField
    categories: RankedKeywordsIntArrayField = Field(
        description=(
            "Exact ordered provider category identifiers, duplicates preserved. Not a "
            "taxonomy, a set, or an Observatory classification."
        )
    )
    monthly_searches_state: OptionalStateToken = Field(
        description=(
            "State of the provider monthly_searches array. The points themselves are the "
            "separate monthly_search_volume Observation family. A stated array may "
            "legitimately be empty, so a stated state with no monthly facts is valid; "
            "monthly facts under a non-stated state are integrity failure. " + _STATE_ONLY
        )
    )
    search_volume_trend: RankedKeywordsSearchVolumeTrend


class RankedKeywordsKeywordProperties(BaseModel):
    """Exact persisted provider keyword_properties testimony."""

    model_config = ConfigDict(extra="forbid", strict=True)

    se_type: RankedKeywordsSeTypeField
    core_keyword: RankedKeywordsTextField = Field(
        description=(
            "Exact provider core_keyword string. Plain provider testimony, never a "
            "canonical keyword identity, foreign key, or equivalence claim."
        )
    )
    synonym_clustering_algorithm: RankedKeywordsTextField = Field(
        description=(
            "Exact provider algorithm label. Observatory performs no synonym clustering "
            "and claims no equivalence."
        )
    )
    keyword_difficulty: RankedKeywordsCountField = Field(
        description=(
            "Keyword-properties provider difficulty. It is a different provider fact from "
            "ranked_element.keyword_difficulty and is never reconciled with it."
        )
    )
    detected_language: RankedKeywordsTextField
    is_another_language: RankedKeywordsBoolField


class RankedKeywordsAvgBacklinks(BaseModel):
    """Exact persisted provider avg_backlinks_info testimony."""

    model_config = ConfigDict(extra="forbid", strict=True)

    se_type: RankedKeywordsSeTypeField
    backlinks: RankedKeywordsDecimalField
    dofollow: RankedKeywordsDecimalField
    referring_pages: RankedKeywordsDecimalField
    referring_domains: RankedKeywordsDecimalField
    referring_main_domains: RankedKeywordsDecimalField
    rank: RankedKeywordsDecimalField = Field(
        description=(
            "Exact provider backlink rank value. It is not a SERP position, an Observatory "
            "ranking, importance, or opportunity."
        )
    )
    main_domain_rank: RankedKeywordsDecimalField = Field(
        description=(
            "Backlink-average provider main domain rank. It is a different provider fact "
            "from rank_info.main_domain_rank."
        )
    )
    avg_backlinks_last_updated_time: RankedKeywordsTextField = Field(description=_CLOCKS)


class RankedKeywordsSearchIntent(BaseModel):
    """Exact persisted provider search_intent_info testimony."""

    model_config = ConfigDict(extra="forbid", strict=True)

    se_type: RankedKeywordsSeTypeField
    main_intent: RankedKeywordsTextField = Field(
        description="Open provider intent vocabulary. Observatory adds no closed taxonomy."
    )
    foreign_intent: RankedKeywordsTextArrayField = Field(
        description="Exact ordered provider array, duplicates preserved."
    )
    search_intent_last_updated_time: RankedKeywordsTextField = Field(description=_CLOCKS)


class RankedKeywordsKeywordSerpInfo(BaseModel):
    """Exact persisted keyword-local provider serp_info testimony.

    Six of these members are restated by `ranked_element`. They are separate provider paths
    that may disagree; equality in one Capture is testimony, never reconciliation.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    se_type: RankedKeywordsSeTypeField
    check_url: RankedKeywordsTextField = Field(description=_URL)
    serp_item_types: RankedKeywordsTextArrayField = Field(
        description="Exact ordered provider array, duplicates preserved."
    )
    se_results_count: RankedKeywordsCountField
    keyword_serp_last_updated_time: RankedKeywordsTextField = Field(description=_CLOCKS)
    keyword_serp_previous_updated_time: RankedKeywordsTextField = Field(
        description=_CLOCKS
    )


class RankedKeywordsKeywordInfoStructure(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_ENCLOSING_STATE)
    value: RankedKeywordsKeywordInfo | None = Field(description=_ENCLOSING_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsPropertiesStructure(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_ENCLOSING_STATE)
    value: RankedKeywordsKeywordProperties | None = Field(description=_ENCLOSING_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsBacklinksStructure(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_ENCLOSING_STATE)
    value: RankedKeywordsAvgBacklinks | None = Field(description=_ENCLOSING_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsIntentStructure(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_ENCLOSING_STATE)
    value: RankedKeywordsSearchIntent | None = Field(description=_ENCLOSING_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsSerpStructure(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_ENCLOSING_STATE)
    value: RankedKeywordsKeywordSerpInfo | None = Field(description=_ENCLOSING_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RankedKeywordsKeywordDataFact(BaseModel):
    """One Ranked-local keyword-data semantic Observation."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal["dataforseo.google.ranked_keywords.keyword_data.v1"]
    within_capture_identity: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$", description=_IDENTITY
    )
    requested_target: str = Field(min_length=1, description=_KEYWORD_ENRICHMENT)
    keyword: str = Field(
        min_length=1,
        description=(
            "Exact provider keyword string. Not trimmed, case-folded, normalized, or "
            "replaced by core_keyword."
        ),
    )
    location_code: RankedKeywordsCountField
    language_code: RankedKeywordsTextField
    se_type: RankedKeywordsSeTypeField
    keyword_info: RankedKeywordsKeywordInfoStructure
    keyword_properties: RankedKeywordsPropertiesStructure
    avg_backlinks: RankedKeywordsBacklinksStructure
    search_intent: RankedKeywordsIntentStructure
    keyword_serp_info: RankedKeywordsSerpStructure
    bing_normalized_state: UnsupportedStateToken = Field(
        description=(
            "State of provider keyword_info_normalized_with_bing. It is independent of the "
            "clickstream request flag and is exactly absent or json_null under the accepted "
            "parser. " + _STATE_ONLY
        )
    )
    clickstream_normalized_state: ClickstreamStateToken = Field(
        description=_CLICKSTREAM + " " + _STATE_ONLY
    )
    clickstream_keyword_info_state: ClickstreamStateToken = Field(
        description=_CLICKSTREAM + " " + _STATE_ONLY
    )


# --------------------------------------------------------------------------------------
# Monthly Data Period testimony and the returned-item bridge
# --------------------------------------------------------------------------------------


class RankedKeywordsDataPeriod(BaseModel):
    """Provider-stated calendar Data Period."""

    model_config = ConfigDict(extra="forbid", strict=True)

    year: int = Field(ge=1, le=9999, description=_PERIOD)
    month: int = Field(ge=1, le=12, description=_PERIOD)


class RankedKeywordsMonthlyOccurrence(BaseModel):
    """One returned-items array placement that stated this monthly Data Period fact."""

    model_config = ConfigDict(extra="forbid", strict=True)

    item_index: int = Field(ge=0, le=IJSON_MAX, description=_OCCURRENCE)


class RankedKeywordsMonthlyFact(BaseModel):
    """One monthly Data Period semantic Observation and its provider occurrences."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal[
        "dataforseo.google.ranked_keywords.monthly_search_volume.v1"
    ]
    within_capture_identity: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$", description=_IDENTITY
    )
    requested_target: str = Field(min_length=1, description=_KEYWORD_ENRICHMENT)
    keyword: str = Field(min_length=1)
    data_period: RankedKeywordsDataPeriod = Field(description=_PERIOD)
    search_volume: int = Field(ge=0, le=IJSON_MAX, description=_MONTHLY_VOLUME)
    occurrences: list[RankedKeywordsMonthlyOccurrence] = Field(
        min_length=1,
        description=(
            "Returned-item placements that stated this Data Period. Equal duplicate "
            "provider testimony collapses to one semantic fact while every occurrence "
            "survives here. " + _OCCURRENCE
        ),
    )


class RankedKeywordsItemOccurrence(BaseModel):
    """One returned provider item, bridging a placement fact and a keyword-data fact."""

    model_config = ConfigDict(extra="forbid", strict=True)

    item_index: int = Field(ge=0, le=IJSON_MAX, description=_BRIDGE)
    ranked_result_identity: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
        description=(
            "within_capture_identity of the ranked placement fact this item stated. "
            + _BRIDGE
        ),
    )
    ranked_result_kind: Literal["dataforseo.google.ranked_keywords.ranked_result.v1"]
    keyword_data_identity: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
        description=(
            "within_capture_identity of the Ranked-local keyword-data fact this item "
            "stated. Both linked parents carry the same exact keyword. " + _BRIDGE
        ),
    )
    keyword_data_kind: Literal["dataforseo.google.ranked_keywords.keyword_data.v1"]
    item_se_type: Literal["google"] = Field(
        description=(
            "Exact provider items[].se_type testimony for this returned item. Recipe v1 "
            "admits only 'google'. It is item-level testimony, distinct from any "
            "structure-local se_type, and is not a cross-surface engine identity."
        )
    )


# --------------------------------------------------------------------------------------
# Capture document and outer envelope
# --------------------------------------------------------------------------------------


class RankedKeywordsRequest(BaseModel):
    """Closed verified Attempt request block."""

    model_config = ConfigDict(extra="forbid", strict=True)

    target: str = Field(
        min_length=1,
        description=(
            "Exact requested target from verified Attempt Evidence. It is the history "
            "subject and is never the provider result echo, a returned URL, domain, main "
            "domain, website name, keyword, canonical site, or Page. " + _REQUEST_AUTHORITY
        ),
    )
    location_code: Literal[2840] = Field(description=_REQUEST_AUTHORITY)
    language_code: Literal["en"] = Field(description=_REQUEST_AUTHORITY)
    item_types: list[
        Literal[
            "organic", "paid", "featured_snippet", "local_pack", "ai_overview_reference"
        ]
    ] = Field(
        min_length=5,
        max_length=5,
        description=(
            "Frozen ordered adapter item-type request. Provider documentation states that "
            "requested array order affects returned ordering, so the sequence is exact "
            "request testimony, not a set. " + _REQUEST_AUTHORITY
        ),
    )
    ignore_synonyms: Literal[False] = Field(description=_REQUEST_AUTHORITY)
    include_clickstream_data: Literal[False] = Field(
        description=(
            "Frozen adapter flag. Every clickstream state in this document is "
            "request-disabled, not a provider failure. " + _REQUEST_AUTHORITY
        )
    )
    limit: Literal[100] = Field(
        description=(
            "Frozen adapter provider-side request limit. It bounds the returned prefix and "
            "is unrelated to the outer history limit. " + _REQUEST_AUTHORITY
        )
    )
    offset: Literal[0] = Field(
        description=(
            "Frozen adapter provider-side request offset. No second page was requested and "
            "none is authorized. " + _REQUEST_AUTHORITY
        )
    )
    load_rank_absolute: Literal[True] = Field(
        description=(
            "Frozen adapter flag that caused the provider to state the absolute-rank "
            "aggregate locus beside the rank-group locus. " + _REQUEST_AUTHORITY
        )
    )
    historical_serp_mode: Literal["all"] = Field(description=_REQUEST_AUTHORITY)
    order_by: list[Literal["ranked_serp_element.serp_item.rank_group,asc"]] = Field(
        min_length=1,
        max_length=1,
        description=(
            "Frozen ordered adapter sort testimony. It is provider request ordering, not "
            "Observatory presentation order; the ranked_results presentation below is "
            "deliberately keyword-first so the two are visibly different. "
            + _REQUEST_AUTHORITY
        ),
    )


class RankedKeywordsCaptureOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    classification: Literal["observation_admitted"] = Field(
        description=(
            "Recipe v1 declares no observation_admitted_empty: every parser-success carries "
            "the required aggregate objects, so a successful zero-item result is ordinary "
            "observation_admitted testimony with exactly ten corpus facts."
        )
    )
    observation_count: int = Field(ge=10, le=IJSON_MAX, description=_COUNT)


class RankedKeywordsResultContext(BaseModel):
    """Provider result-level testimony. The request block remains request authority."""

    model_config = ConfigDict(extra="forbid", strict=True)

    target: RankedKeywordsTextField = Field(description=_ECHO + " " + _STATE)
    location_code: RankedKeywordsCountField = Field(description=_ECHO + " " + _STATE)
    language_code: RankedKeywordsTextField = Field(description=_ECHO + " " + _STATE)
    se_type: RankedKeywordsSeTypeField = Field(description=_ECHO + " " + _SE_TYPE_STATE)
    total_count: int = Field(ge=0, le=IJSON_MAX, description=_PROVIDER_COUNTS)
    items_count: int = Field(ge=0, le=IJSON_MAX, description=_PROVIDER_COUNTS)


class RankedKeywordsCapture(BaseModel):
    """One admitted Ranked Keywords Capture document."""

    model_config = ConfigDict(extra="forbid", strict=True)

    attempt_id: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$", description=_GRAIN
    )
    capture_id: str = Field(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")
    provider: Literal["dataforseo"]
    adapter_contract: Literal[
        "dataforseo-labs-google-ranked-keywords-live-paid-probe-v1"
    ]
    derivation_version_id: Literal[
        "c7573695db7ecaa0f5dfdc2fc3658e84b1673eec005a0d8003093e57408294a8"
    ]
    authorized_at: str = Field(description=_TIME)
    request_started_at: str = Field(description=_TIME)
    transport_ended_at: str = Field(description=_TIME)
    request: RankedKeywordsRequest
    capture_outcome: RankedKeywordsCaptureOutcome
    result_context: RankedKeywordsResultContext
    corpus_metrics: list[RankedKeywordsCorpusMetricsFact] = Field(
        min_length=10,
        max_length=10,
        description=(
            "Exactly ten target corpus aggregate Observations: five requested families "
            "under two rank systems. Presented in the accepted family order, then "
            "rank_group before rank_absolute. Presentation only. " + _CORPUS
        ),
    )
    ranked_results: list[RankedKeywordsRankedResultFact] = Field(
        description=(
            "Ranked placement Observations, presented by keyword, SERP item type, "
            "rank_group, rank_absolute, identity. This presentation is deliberately not the "
            "frozen provider order_by; provider array order survives only in "
            "item_occurrences. " + _PLACEMENT
        )
    )
    keyword_data: list[RankedKeywordsKeywordDataFact] = Field(
        description=(
            "Ranked-local keyword enrichment Observations, presented by keyword and "
            "identity. Identical duplicate provider testimony collapses to one semantic "
            "fact while every returned-item occurrence survives in item_occurrences. "
            + _KEYWORD_ENRICHMENT
        )
    )
    monthly_search_volume: list[RankedKeywordsMonthlyFact] = Field(
        description=(
            "Monthly Data Period Observations, presented by keyword, year, month, identity. "
            + _PERIOD
        )
    )
    item_occurrences: list[RankedKeywordsItemOccurrence] = Field(
        description=(
            "Returned-item occurrence bridge in provider item_index order. Indexes are "
            "globally dense 0..n-1 where n equals result_context.items_count. This is "
            "subordinate provider testimony, not a fifth Observation kind. " + _BRIDGE
        )
    )


class RankedKeywordsHistoryEnvelope(BaseModel):
    """Closed Ranked Keywords admitted-history envelope with fully typed Captures."""

    model_config = ConfigDict(extra="forbid", strict=True)

    provider: Literal["dataforseo"] = Field(description=_GRAIN + " " + _EMPTY)
    adapter_contract: Literal[
        "dataforseo-labs-google-ranked-keywords-live-paid-probe-v1"
    ]
    requested_target: str = Field(
        min_length=1,
        description=(
            "Exact requested subject for this history. It is the same value the Recipe "
            "identity axes name requested_target and the verified Attempt names target. It "
            "is never a provider result echo, a returned URL, domain, main domain, website "
            "name, keyword, canonical site, Page, or Strategy entity. " + _EMPTY
        ),
    )
    derivation_version_id: Literal[
        "c7573695db7ecaa0f5dfdc2fc3658e84b1673eec005a0d8003093e57408294a8"
    ]
    recipe_resolution: Literal["selected", "pinned"]
    observation_kinds: list[str] = Field(
        min_length=4,
        max_length=4,
        json_schema_extra={
            "minItems": 4,
            "maxItems": 4,
            "prefixItems": [
                {"type": "string", "const": CORPUS_METRICS_KIND},
                {"type": "string", "const": KEYWORD_DATA_KIND},
                {"type": "string", "const": MONTHLY_KIND},
                {"type": "string", "const": RANKED_RESULT_KIND},
            ],
        },
        description=(
            "Exact ordered Recipe v1 Observation kinds: corpus_metrics, keyword_data, "
            "monthly_search_volume, ranked_result. They do not change the list grain. "
            + _COUNT
        ),
    )

    @field_validator("observation_kinds")
    @classmethod
    def require_v1_kinds(cls, value: list[str]) -> list[str]:
        if value != list(V1_KINDS):
            raise ValueError("observation_kinds must be the exact Ranked Keywords v1 list")
        return value

    captures: list[RankedKeywordsCapture] = Field(
        description="Whole admitted Capture documents for this subject. " + _EMPTY
    )
    total_matching: int = Field(ge=0, description=_GRAIN + " " + _EMPTY)
    returned_count: int = Field(
        ge=0, description="Number of whole Capture documents in captures."
    )
    limit: int = Field(
        ge=1,
        le=HISTORY_LIMIT_MAX,
        description=(
            "Validated applied outer history limit. Maximum 100. Not a provider page size "
            "and unrelated to the frozen provider request limit."
        ),
    )
    order: Literal["asc", "desc"] = Field(description=_ORDER)
    has_more: bool = Field(description=_HAS_MORE)


# --------------------------------------------------------------------------------------
# Stored-row coercion
# --------------------------------------------------------------------------------------


def _as_int(value: object, name: str) -> int:
    if isinstance(value, bool) or type(value) is not int:
        raise IntegrityError(f"{name} must be an integer")
    return value


def _as_text(value: object, name: str) -> str:
    if not isinstance(value, str) or value == "":
        raise IntegrityError(f"{name} is missing")
    return value


def _as_any_text(value: object, name: str) -> str:
    """Exact stored text, including a permitted stated-empty provider string."""

    if not isinstance(value, str):
        raise IntegrityError(f"{name} is missing")
    return value


def _as_bool(value: object, name: str) -> bool:
    if not isinstance(value, bool):
        raise IntegrityError(f"{name} must be a boolean")
    return value


def _as_state(
    value: object, name: str, domain: frozenset[str] = OPTIONAL_FIELD_STATES
) -> str:
    """Validate one stored state token against its own applicable Recipe-v1 domain."""

    if not isinstance(value, str) or value not in domain:
        raise IntegrityError(f"{name} is not an applicable Recipe v1 field state")
    return value


def _as_str_list(value: object, name: str) -> list[str]:
    if isinstance(value, (list, tuple)) and all(isinstance(item, str) for item in value):
        return [str(item) for item in value]
    raise IntegrityError(f"{name} is missing or wrong-typed")


def _optional_text(value: object, name: str) -> str | None:
    return None if value is None else _as_any_text(value, name)


def _optional_int(value: object, name: str) -> int | None:
    return None if value is None else _as_int(value, name)


def _optional_bool(value: object, name: str) -> bool | None:
    return None if value is None else _as_bool(value, name)


def _optional_decimal(value: object, name: str) -> str | None:
    """Render an exact stored NUMERIC without any binary-float round trip."""

    if value is None:
        return None
    if not isinstance(value, Decimal):
        raise IntegrityError(f"{name} must be an exact decimal")
    return format(value, "f")


def _optional_int_list(value: object, name: str) -> list[int] | None:
    if value is None:
        return None
    if not isinstance(value, (list, tuple)):
        raise IntegrityError(f"{name} must be an array")
    return [_as_int(item, name) for item in value]


def _optional_text_list(value: object, name: str) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, (list, tuple)):
        raise IntegrityError(f"{name} must be an array")
    return [_as_any_text(item, name) for item in value]


def _text_field(row: Mapping[str, object], column: str) -> dict[str, object]:
    return {
        "state": _as_state(row[f"{column}_state"], f"{column}_state"),
        "value": _optional_text(row[column], column),
    }


def _count_field(row: Mapping[str, object], column: str) -> dict[str, object]:
    return {
        "state": _as_state(row[f"{column}_state"], f"{column}_state"),
        "value": _optional_int(row[column], column),
    }


def _bool_field(row: Mapping[str, object], column: str) -> dict[str, object]:
    return {
        "state": _as_state(row[f"{column}_state"], f"{column}_state"),
        "value": _optional_bool(row[column], column),
    }


def _decimal_field(row: Mapping[str, object], column: str) -> dict[str, object]:
    return {
        "state": _as_state(row[f"{column}_state"], f"{column}_state"),
        "value": _optional_decimal(row[column], column),
    }


def _int_array_field(row: Mapping[str, object], column: str) -> dict[str, object]:
    return {
        "state": _as_state(row[f"{column}_state"], f"{column}_state"),
        "value": _optional_int_list(row[column], column),
    }


def _text_array_field(row: Mapping[str, object], column: str) -> dict[str, object]:
    return {
        "state": _as_state(row[f"{column}_state"], f"{column}_state"),
        "value": _optional_text_list(row[column], column),
    }


def _se_type_field(row: Mapping[str, object], column: str) -> dict[str, object]:
    """Closed provider se_type pair. A stated value is exactly the Recipe v1 vocabulary."""

    state = _as_state(row[f"{column}_state"], f"{column}_state")
    value = _optional_text(row[column], column)
    if value is not None and value != SE_TYPE:
        raise IntegrityError(f"{column} is not the closed Recipe v1 se_type")
    return {"state": state, "value": value}


def _require_se_type(value: object, name: str) -> str:
    """Required provider se_type. Recipe v1 admits only the exact closed value."""

    text = _as_text(value, name)
    if text != SE_TYPE:
        raise IntegrityError(f"{name} is not the closed Recipe v1 se_type")
    return text


def _member_field(
    row: Mapping[str, object],
    column: str,
    reader: Callable[[object, str], object],
) -> dict[str, object]:
    return {
        "state": _as_state(row[f"{column}_state"], f"{column}_state", MEMBER_FIELD_STATES),
        "value": reader(row[column], column),
    }


def _require_inline_members(
    state: str, member_states: Sequence[str], name: str
) -> None:
    """An inline provider object's members are inapplicable exactly when it is unstated."""

    stated = state == "stated"
    for member_state in member_states:
        if (member_state != "inapplicable") != stated:
            raise ValueError(f"{name} member state disagrees with its enclosing state")


def _require_inline_member_rows(
    state: str, members: Sequence[Mapping[str, object]], name: str
) -> None:
    stated = state == "stated"
    for member in members:
        if (member["state"] != "inapplicable") != stated:
            raise IntegrityError(f"{name} member state disagrees with its enclosing state")


def _identity(kind: str, axes: Mapping[str, object]) -> str:
    """Recompute a Recipe-v1 within-Capture identity from verified axes."""

    return observation_identity(
        {
            "axes": dict(axes),
            "observation_kind": kind,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        RANKED_KEYWORDS_RECIPE,
    )


def _rows(
    connection: Connection[Any],
    table: str,
    columns: Sequence[str],
    capture_id: str,
) -> list[dict[str, object]]:
    statement = sql.SQL("SELECT {} FROM {} WHERE derivation_version_id = %s AND capture_id = %s")
    fetched = connection.execute(
        statement.format(
            sql.SQL(", ").join(sql.Identifier(column) for column in columns),
            sql.Identifier(table),
        ),
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    ).fetchall()
    return [dict(zip(columns, row, strict=True)) for row in fetched]


# --------------------------------------------------------------------------------------
# Recipe resolution
# --------------------------------------------------------------------------------------


def _load_validated_v1_recipe(
    connection: Connection[Any], resolved: ResolvedProviderRecipe
) -> ResolvedProviderRecipe:
    """Verify the resolved Recipe really is the accepted Ranked Keywords v1 document."""

    if resolved.derivation_version_id != RANKED_KEYWORDS_RECIPE_ID:
        raise UnsupportedRankedKeywordsRecipe(
            "Ranked Keywords history serves Recipe v1 only"
        )
    if (
        resolved.provider != HISTORY_PROVIDER
        or resolved.adapter_contract != HISTORY_ADAPTER
    ):
        raise IntegrityError("resolved Recipe does not match this route")
    row = connection.execute(
        """
        SELECT provider, adapter_contract, recipe_canonical_bytes
        FROM provider_recipes
        WHERE derivation_version_id = %s
        """,
        (RANKED_KEYWORDS_RECIPE_ID,),
    ).fetchone()
    if row is None:
        raise IntegrityError("resolved recipe is not registered")
    column_provider = str(row[0])
    column_adapter = str(row[1])
    raw = bytes(row[2])
    try:
        parsed: object = json.loads(raw.decode("utf-8"))
        validated = validate_recipe(parsed)
        canonical = canonical_json(validated)
        digest = content_digest(raw)
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        DocumentError,
        TypeError,
        ValueError,
    ) as exc:
        raise IntegrityError("resolved Recipe bytes are not a closed Recipe") from exc
    if canonical != raw:
        raise IntegrityError("resolved Recipe bytes are not exact JCS")
    if digest != RANKED_KEYWORDS_RECIPE_ID:
        raise IntegrityError("Recipe digest disagrees with derivation_version_id")
    providers = {
        HISTORY_PROVIDER,
        resolved.provider,
        column_provider,
        str(validated["provider"]),
    }
    adapters = {
        HISTORY_ADAPTER,
        resolved.adapter_contract,
        column_adapter,
        str(validated["adapter_contract"]),
    }
    if providers != {HISTORY_PROVIDER}:
        raise IntegrityError("Recipe provider metadata disagrees")
    if adapters != {HISTORY_ADAPTER}:
        raise IntegrityError("Recipe adapter metadata disagrees")
    # `observation_kinds`, deliberately not `observation_identity.kinds`, whose order
    # differs inside this same accepted document.
    if validated["observation_kinds"] != list(V1_KINDS):
        raise IntegrityError("Recipe observation kinds are not Ranked Keywords v1")
    admission = validated["admission"]
    if not isinstance(admission, Mapping):
        raise IntegrityError("Recipe admission is missing")
    if admission.get("capture_outcomes") != list(V1_CAPTURE_OUTCOMES):
        raise IntegrityError("Recipe classifications are not Ranked Keywords v1")
    return resolved


def _attempt_request(attempt: Mapping[str, object]) -> dict[str, object]:
    """Project the closed request block from verified Attempt Evidence."""

    parameters = attempt.get("parameters")
    if not isinstance(parameters, Mapping):
        raise IntegrityError("verified Attempt is missing parameters")
    try:
        closed = validate_ranked_keywords_http_parameters(parameters)
    except DocumentError as exc:
        raise IntegrityError(
            "verified Attempt parameters are not Ranked Keywords"
        ) from exc
    request: dict[str, object] = {
        "target": _as_text(closed.get("target"), "target"),
        "location_code": _as_int(closed.get("location_code"), "location_code"),
        "language_code": _as_text(closed.get("language_code"), "language_code"),
        "item_types": _as_str_list(closed.get("item_types"), "item_types"),
        "ignore_synonyms": _as_bool(closed.get("ignore_synonyms"), "ignore_synonyms"),
        "include_clickstream_data": _as_bool(
            closed.get("include_clickstream_data"), "include_clickstream_data"
        ),
        "limit": _as_int(closed.get("limit"), "limit"),
        "offset": _as_int(closed.get("offset"), "offset"),
        "load_rank_absolute": _as_bool(
            closed.get("load_rank_absolute"), "load_rank_absolute"
        ),
        "historical_serp_mode": _as_text(
            closed.get("historical_serp_mode"), "historical_serp_mode"
        ),
        "order_by": _as_str_list(closed.get("order_by"), "order_by"),
    }
    if set(request) != _REQUEST_KEYS:
        raise IntegrityError("Attempt request keys are not closed")
    return request


# --------------------------------------------------------------------------------------
# Typed projection of persisted rows
# --------------------------------------------------------------------------------------


def _corpus_metrics_fact(
    row: Mapping[str, object], target: str, identity: str
) -> dict[str, object]:
    family = _as_text(row["aggregate_family"], "aggregate_family")
    system = _as_text(row["rank_system"], "rank_system")
    count = {
        "state": _as_state(row["count_state"], "count_state", CORPUS_COUNT_STATES),
        "value": _optional_int(row["count"], "count"),
    }
    etv = {
        "state": _as_state(row["etv_state"], "etv_state", CORPUS_DECIMAL_STATES),
        "value": _optional_decimal(row["etv"], "etv"),
    }
    cost = {
        "state": _as_state(
            row["estimated_paid_traffic_cost_state"],
            "estimated_paid_traffic_cost_state",
            CORPUS_DECIMAL_STATES,
        ),
        "value": _optional_decimal(
            row["estimated_paid_traffic_cost"], "estimated_paid_traffic_cost"
        ),
    }
    # The schema CHECK enforces only the rank-absolute direction. Recipe v1 also fixes the
    # rank-group converse, so the reader rejects an SQL-legal but Recipe-illegal combination.
    if system == RANK_SYSTEM_ABSOLUTE:
        if any(field["state"] != "inapplicable" for field in (count, etv, cost)):
            raise IntegrityError(
                "rank_absolute corpus count, ETV, and cost must be inapplicable"
            )
    else:
        if count["state"] != "stated":
            raise IntegrityError("rank_group corpus count must be stated")
        if any(field["state"] == "inapplicable" for field in (etv, cost)):
            raise IntegrityError("rank_group corpus ETV and cost are never inapplicable")
    return {
        "observation_kind": CORPUS_METRICS_KIND,
        "within_capture_identity": identity,
        "requested_target": target,
        "aggregate_family": family,
        "rank_system": system,
        "position_buckets": {
            column: _as_int(row[column], column) for column in BUCKET_COLUMNS
        },
        "movement_counts": {
            column: _as_int(row[column], column) for column in MOVEMENT_COLUMNS
        },
        "count": count,
        "etv": etv,
        "estimated_paid_traffic_cost": cost,
        "clickstream_etv_state": _as_state(
            row["clickstream_etv_state"], "clickstream_etv_state", CLICKSTREAM_STATES
        ),
        "clickstream_gender_distribution_state": _as_state(
            row["clickstream_gender_distribution_state"],
            "clickstream_gender_distribution_state",
            CLICKSTREAM_STATES,
        ),
        "clickstream_age_distribution_state": _as_state(
            row["clickstream_age_distribution_state"],
            "clickstream_age_distribution_state",
            CLICKSTREAM_STATES,
        ),
    }


def _ranked_element(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "se_type": _se_type_field(row, "ranked_element_se_type"),
        "check_url": _text_field(row, "ranked_element_check_url"),
        "se_results_count": _count_field(row, "ranked_element_se_results_count"),
        "keyword_difficulty": _count_field(row, "ranked_element_keyword_difficulty"),
        "is_lost": _bool_field(row, "ranked_element_is_lost"),
        "serp_item_types": _text_array_field(row, "ranked_element_serp_item_types"),
        "last_updated_time": _text_field(row, "ranked_element_last_updated_time"),
        "previous_updated_time": _text_field(
            row, "ranked_element_previous_updated_time"
        ),
    }


def _rank_changes(row: Mapping[str, object]) -> dict[str, object]:
    state = _as_state(row["rank_changes_state"], "rank_changes_state")
    members = {
        "is_new": _member_field(row, "rank_changes_is_new", _optional_bool),
        "is_up": _member_field(row, "rank_changes_is_up", _optional_bool),
        "is_down": _member_field(row, "rank_changes_is_down", _optional_bool),
        "previous_rank_absolute": _member_field(
            row, "rank_changes_previous_rank_absolute", _optional_int
        ),
    }
    _require_inline_member_rows(state, list(members.values()), "rank_changes")
    return {"state": state, **members}


def _rank_info(row: Mapping[str, object]) -> dict[str, object]:
    state = _as_state(row["rank_info_state"], "rank_info_state")
    members = {
        "page_rank": _member_field(row, "rank_info_page_rank", _optional_int),
        "main_domain_rank": _member_field(
            row, "rank_info_main_domain_rank", _optional_int
        ),
    }
    _require_inline_member_rows(state, list(members.values()), "rank_info")
    return {"state": state, **members}


def _serp_item(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "se_type": _se_type_field(row, "serp_item_se_type"),
        "url": _as_text(row["url"], "url"),
        "position": _text_field(row, "position"),
        "xpath": _text_field(row, "xpath"),
        "domain": _text_field(row, "domain"),
        "main_domain": _text_field(row, "main_domain"),
        "website_name": _text_field(row, "website_name"),
        "relative_url": _text_field(row, "relative_url"),
        "title": _text_field(row, "title"),
        "description": _text_field(row, "description"),
        "breadcrumb_state": _as_state(row["breadcrumb_state"], "breadcrumb_state"),
        "pre_snippet_state": _as_state(row["pre_snippet_state"], "pre_snippet_state"),
        "highlighted_state": _as_state(row["highlighted_state"], "highlighted_state"),
        "is_image": _bool_field(row, "is_image"),
        "is_video": _bool_field(row, "is_video"),
        "is_featured_snippet": _bool_field(row, "is_featured_snippet"),
        "is_malicious": _bool_field(row, "is_malicious"),
        "amp_version": _bool_field(row, "amp_version"),
        "etv": _decimal_field(row, "etv"),
        "estimated_paid_traffic_cost": _decimal_field(
            row, "estimated_paid_traffic_cost"
        ),
        "clickstream_etv_state": _as_state(
            row["clickstream_etv_state"], "clickstream_etv_state", CLICKSTREAM_STATES
        ),
        "rank_changes": _rank_changes(row),
        "rank_info": _rank_info(row),
        "about_this_result_state": _as_state(
            row["about_this_result_state"],
            "about_this_result_state",
            UNSUPPORTED_CHILD_STATES,
        ),
        "backlinks_info_state": _as_state(
            row["backlinks_info_state"], "backlinks_info_state", UNSUPPORTED_CHILD_STATES
        ),
        "extended_snippet_state": _as_state(
            row["extended_snippet_state"],
            "extended_snippet_state",
            UNSUPPORTED_CHILD_STATES,
        ),
        "links_state": _as_state(
            row["links_state"], "links_state", UNSUPPORTED_CHILD_STATES
        ),
        "rating_state": _as_state(
            row["rating_state"], "rating_state", UNSUPPORTED_CHILD_STATES
        ),
    }


def _keyword_info(row: Mapping[str, object]) -> dict[str, object]:
    trend_state = _as_state(
        row["search_volume_trend_state"], "search_volume_trend_state"
    )
    trend_members = {
        "monthly": _member_field(row, "trend_monthly", _optional_int),
        "quarterly": _member_field(row, "trend_quarterly", _optional_int),
        "yearly": _member_field(row, "trend_yearly", _optional_int),
    }
    _require_inline_member_rows(
        trend_state, list(trend_members.values()), "search_volume_trend"
    )
    return {
        "se_type": _se_type_field(row, "se_type"),
        "keyword_info_last_updated_time": _text_field(
            row, "keyword_info_last_updated_time"
        ),
        "competition": _decimal_field(row, "competition"),
        "competition_level": _text_field(row, "competition_level"),
        "cpc": _decimal_field(row, "cpc"),
        "search_volume": _count_field(row, "search_volume"),
        "low_top_of_page_bid": _decimal_field(row, "low_top_of_page_bid"),
        "high_top_of_page_bid": _decimal_field(row, "high_top_of_page_bid"),
        "categories": _int_array_field(row, "categories"),
        "monthly_searches_state": _as_state(
            row["monthly_searches_state"], "monthly_searches_state"
        ),
        "search_volume_trend": {"state": trend_state, **trend_members},
    }


def _keyword_properties(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "se_type": _se_type_field(row, "se_type"),
        "core_keyword": _text_field(row, "core_keyword"),
        "synonym_clustering_algorithm": _text_field(
            row, "synonym_clustering_algorithm"
        ),
        "keyword_difficulty": _count_field(row, "keyword_difficulty"),
        "detected_language": _text_field(row, "detected_language"),
        "is_another_language": _bool_field(row, "is_another_language"),
    }


def _avg_backlinks(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "se_type": _se_type_field(row, "se_type"),
        "backlinks": _decimal_field(row, "backlinks"),
        "dofollow": _decimal_field(row, "dofollow"),
        "referring_pages": _decimal_field(row, "referring_pages"),
        "referring_domains": _decimal_field(row, "referring_domains"),
        "referring_main_domains": _decimal_field(row, "referring_main_domains"),
        "rank": _decimal_field(row, "rank"),
        "main_domain_rank": _decimal_field(row, "main_domain_rank"),
        "avg_backlinks_last_updated_time": _text_field(
            row, "avg_backlinks_last_updated_time"
        ),
    }


def _search_intent(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "se_type": _se_type_field(row, "se_type"),
        "main_intent": _text_field(row, "main_intent"),
        "foreign_intent": _text_array_field(row, "foreign_intent"),
        "search_intent_last_updated_time": _text_field(
            row, "search_intent_last_updated_time"
        ),
    }


def _keyword_serp_info(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "se_type": _se_type_field(row, "se_type"),
        "check_url": _text_field(row, "check_url"),
        "serp_item_types": _text_array_field(row, "serp_item_types"),
        "se_results_count": _count_field(row, "se_results_count"),
        "keyword_serp_last_updated_time": _text_field(
            row, "keyword_serp_last_updated_time"
        ),
        "keyword_serp_previous_updated_time": _text_field(
            row, "keyword_serp_previous_updated_time"
        ),
    }


_ChildProjector = Callable[[Mapping[str, object]], dict[str, object]]
_CHILD_PROJECTORS: Final[dict[str, _ChildProjector]] = {
    "keyword_info": _keyword_info,
    "keyword_properties": _keyword_properties,
    "avg_backlinks": _avg_backlinks,
    "search_intent": _search_intent,
    "keyword_serp_info": _keyword_serp_info,
}


# --------------------------------------------------------------------------------------
# Complete-set verification for one Capture
# --------------------------------------------------------------------------------------


def _envelope_keys(
    connection: Connection[Any], capture_id: str, attempt_id: str
) -> set[tuple[str, str]]:
    """Generic envelope rows, including the provenance columns no foreign key constrains."""

    rows = connection.execute(
        """
        SELECT within_capture_identity, observation_kind, attempt_id, provider,
               adapter_contract
        FROM observation_envelopes
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    ).fetchall()
    keys: set[tuple[str, str]] = set()
    for row in rows:
        kind = _as_text(row[1], "observation_kind")
        if kind not in V1_KINDS:
            raise IntegrityError("unknown Observation kind for Recipe v1")
        if _as_text(row[2], "attempt_id") != attempt_id:
            raise IntegrityError("envelope attempt_id disagrees with verified Attempt")
        if (
            _as_text(row[3], "provider") != HISTORY_PROVIDER
            or _as_text(row[4], "adapter_contract") != HISTORY_ADAPTER
        ):
            raise IntegrityError("envelope provider or adapter disagrees")
        keys.add((_as_text(row[0], "within_capture_identity"), kind))
    if len(keys) != len(rows):
        raise IntegrityError("duplicate Observation envelope key")
    return keys


@dataclass(frozen=True)
class _Families:
    """The four typed semantic collections plus the occurrence bridge for one Capture."""

    corpus: list[dict[str, object]]
    ranked: list[dict[str, object]]
    keywords: list[dict[str, object]]
    monthly: list[dict[str, object]]
    occurrences: list[dict[str, object]]


def _capture_families(
    connection: Connection[Any],
    *,
    capture_id: str,
    attempt_id: str,
    target: str,
    observation_count: int,
    items_count: int,
) -> _Families:
    """Rebuild and check the complete PostgreSQL state behind one admitted Capture."""

    envelope_keys = _envelope_keys(connection, capture_id, attempt_id)
    if len(envelope_keys) != observation_count:
        raise IntegrityError("envelope cardinality disagrees with observation_count")

    # --- returned-item occurrence bridge -------------------------------------------------
    item_by_index: dict[int, tuple[str, str]] = {}
    placement_occurrences: dict[str, list[int]] = {}
    keyword_occurrences: dict[str, list[int]] = {}
    occurrences: list[dict[str, object]] = []
    for row in _rows(
        connection, ITEM_OCCURRENCES_TABLE, ITEM_OCCURRENCE_COLUMNS, capture_id
    ):
        index = _as_int(row["item_index"], "item_index")
        if index in item_by_index:
            raise IntegrityError("duplicate returned-item occurrence index")
        placement = _as_text(row["ranked_result_identity"], "ranked_result_identity")
        keyword_identity = _as_text(row["keyword_data_identity"], "keyword_data_identity")
        if _as_text(row["ranked_result_kind"], "ranked_result_kind") != RANKED_RESULT_KIND:
            raise IntegrityError("item occurrence has the wrong placement kind")
        if _as_text(row["keyword_data_kind"], "keyword_data_kind") != KEYWORD_DATA_KIND:
            raise IntegrityError("item occurrence has the wrong keyword-data kind")
        item_by_index[index] = (placement, keyword_identity)
        placement_occurrences.setdefault(placement, []).append(index)
        keyword_occurrences.setdefault(keyword_identity, []).append(index)
        occurrences.append(
            {
                "item_index": index,
                "ranked_result_identity": placement,
                "ranked_result_kind": RANKED_RESULT_KIND,
                "keyword_data_identity": keyword_identity,
                "keyword_data_kind": KEYWORD_DATA_KIND,
                "item_se_type": _require_se_type(row["item_se_type"], "item_se_type"),
            }
        )
    returned_items = len(item_by_index)
    if set(item_by_index) != set(range(returned_items)):
        raise IntegrityError("returned-item occurrence indexes are not globally dense")
    # Recipe v1 writes exactly one occurrence per returned provider item, and the accepted
    # parser already rejects `items_count != len(items)`. This is that persisted-structure
    # invariant only; it states nothing about total_count, buckets, ranks, or fact counts.
    if returned_items != items_count:
        raise IntegrityError("returned-item count disagrees with provider items_count")
    occurrences.sort(key=lambda entry: _as_int(entry["item_index"], "item_index"))

    # --- target corpus aggregates --------------------------------------------------------
    corpus: list[dict[str, object]] = []
    corpus_keys: set[tuple[str, str]] = set()
    combinations: set[tuple[str, str]] = set()
    for row in _rows(connection, CORPUS_METRICS_TABLE, CORPUS_METRICS_COLUMNS, capture_id):
        identity = _as_text(row["within_capture_identity"], "within_capture_identity")
        if _as_text(row["observation_kind"], "observation_kind") != CORPUS_METRICS_KIND:
            raise IntegrityError("corpus row has the wrong Observation kind")
        if _as_text(row["requested_target"], "requested_target") != target:
            raise IntegrityError("corpus requested_target disagrees with the Attempt")
        family = _as_text(row["aggregate_family"], "aggregate_family")
        system = _as_text(row["rank_system"], "rank_system")
        if family not in FAMILY_RANK or system not in RANK_SYSTEM_RANK:
            raise IntegrityError("corpus family or rank system is not Recipe v1")
        recomputed = _identity(
            CORPUS_METRICS_KIND,
            {
                "aggregate_family": family,
                "rank_system": system,
                "requested_target": target,
            },
        )
        if recomputed != identity:
            raise IntegrityError("corpus identity axes do not recompute")
        if (family, system) in combinations:
            raise IntegrityError("duplicate corpus family and rank system")
        combinations.add((family, system))
        corpus.append(_corpus_metrics_fact(row, target, identity))
        corpus_keys.add((identity, CORPUS_METRICS_KIND))
    if combinations != CORPUS_COMBINATIONS:
        raise IntegrityError(
            "corpus metrics are not the exact five-family, two-rank-system cross-product"
        )
    if len(corpus_keys) != len(corpus):
        raise IntegrityError("duplicate corpus semantic identity")

    # --- ranked placements ---------------------------------------------------------------
    ranked: list[dict[str, object]] = []
    ranked_keys: set[tuple[str, str]] = set()
    placement_keyword: dict[str, str] = {}
    for row in _rows(connection, RANKED_RESULTS_TABLE, RANKED_RESULT_COLUMNS, capture_id):
        identity = _as_text(row["within_capture_identity"], "within_capture_identity")
        if _as_text(row["observation_kind"], "observation_kind") != RANKED_RESULT_KIND:
            raise IntegrityError("ranked-result row has the wrong Observation kind")
        if _as_text(row["requested_target"], "requested_target") != target:
            raise IntegrityError(
                "ranked-result requested_target disagrees with the Attempt"
            )
        keyword = _as_text(row["keyword"], "keyword")
        item_type = _as_text(row["serp_item_type"], "serp_item_type")
        rank_group = _as_int(row["rank_group"], "rank_group")
        rank_absolute = _as_int(row["rank_absolute"], "rank_absolute")
        recomputed = _identity(
            RANKED_RESULT_KIND,
            {
                "keyword": keyword,
                "rank_absolute": rank_absolute,
                "rank_group": rank_group,
                "requested_target": target,
                "serp_item_type": item_type,
            },
        )
        if recomputed != identity:
            raise IntegrityError("ranked-result identity axes do not recompute")
        if identity in placement_keyword:
            raise IntegrityError("duplicate ranked-result semantic identity")
        placement_keyword[identity] = keyword
        if not placement_occurrences.pop(identity, []):
            raise IntegrityError("ranked-result parent has no returned-item occurrence")
        ranked.append(
            {
                "observation_kind": RANKED_RESULT_KIND,
                "within_capture_identity": identity,
                "requested_target": target,
                "keyword": keyword,
                "serp_item_type": item_type,
                "rank_group": rank_group,
                "rank_absolute": rank_absolute,
                "ranked_element": _ranked_element(row),
                "serp_item": _serp_item(row),
            }
        )
        ranked_keys.add((identity, RANKED_RESULT_KIND))
    if len(ranked_keys) != len(ranked):
        raise IntegrityError("duplicate ranked-result semantic identity")
    if placement_occurrences:
        raise IntegrityError("returned-item occurrence has no ranked-result fact")

    # --- Ranked-local keyword enrichment -------------------------------------------------
    child_rows: dict[str, dict[str, Mapping[str, object]]] = {}
    for name, table, _state_column, columns in _CHILD_TABLES:
        indexed: dict[str, Mapping[str, object]] = {}
        for row in _rows(connection, table, columns, capture_id):
            identity = _as_text(row["within_capture_identity"], "within_capture_identity")
            if _as_text(row["observation_kind"], "observation_kind") != KEYWORD_DATA_KIND:
                raise IntegrityError(f"{name} child row has the wrong Observation kind")
            if identity in indexed:
                raise IntegrityError(f"duplicate {name} child row")
            indexed[identity] = row
        child_rows[name] = indexed

    keywords: list[dict[str, object]] = []
    keyword_keys: set[tuple[str, str]] = set()
    # keyword -> (keyword_info state, persisted monthly_searches state or None). Monthly
    # facts are admissible only under a stated keyword_info whose monthly_searches array is
    # itself stated, so the monthly family is bound to this index below.
    keyword_index: dict[str, tuple[str, str | None]] = {}
    keyword_identity_keyword: dict[str, str] = {}
    for row in _rows(connection, KEYWORD_DATA_TABLE, KEYWORD_DATA_COLUMNS, capture_id):
        identity = _as_text(row["within_capture_identity"], "within_capture_identity")
        if _as_text(row["observation_kind"], "observation_kind") != KEYWORD_DATA_KIND:
            raise IntegrityError("keyword-data row has the wrong Observation kind")
        if _as_text(row["requested_target"], "requested_target") != target:
            raise IntegrityError("keyword-data requested_target disagrees with the Attempt")
        keyword = _as_text(row["keyword"], "keyword")
        recomputed = _identity(
            KEYWORD_DATA_KIND, {"keyword": keyword, "requested_target": target}
        )
        if recomputed != identity:
            raise IntegrityError("keyword-data identity axes do not recompute")
        if keyword in keyword_index:
            raise IntegrityError("duplicate keyword-data keyword")
        structures: dict[str, object] = {}
        info_child: Mapping[str, object] | None = None
        info_state = _as_state(row["keyword_info_state"], "keyword_info_state")
        for name, _table, state_column, _columns in _CHILD_TABLES:
            state = _as_state(row[state_column], state_column)
            child = child_rows[name].pop(identity, None)
            if state == "stated":
                if child is None:
                    raise IntegrityError(f"stated {name} has no persisted child row")
                structures[name] = {
                    "state": state,
                    "value": _CHILD_PROJECTORS[name](child),
                }
            else:
                if child is not None:
                    raise IntegrityError(f"non-stated {name} has a persisted child row")
                structures[name] = {"state": state, "value": None}
            if name == "keyword_info":
                info_child = child
        monthly_state = (
            None
            if info_child is None
            else _as_state(
                info_child["monthly_searches_state"], "monthly_searches_state"
            )
        )
        keyword_index[keyword] = (info_state, monthly_state)
        keyword_identity_keyword[identity] = keyword
        if not keyword_occurrences.pop(identity, []):
            raise IntegrityError("keyword-data parent has no returned-item occurrence")
        keywords.append(
            {
                "observation_kind": KEYWORD_DATA_KIND,
                "within_capture_identity": identity,
                "requested_target": target,
                "keyword": keyword,
                "location_code": _count_field(row, "location_code"),
                "language_code": _text_field(row, "language_code"),
                "se_type": _se_type_field(row, "se_type"),
                **structures,
                "bing_normalized_state": _as_state(
                    row["bing_normalized_state"], "bing_normalized_state", BING_STATES
                ),
                "clickstream_normalized_state": _as_state(
                    row["clickstream_normalized_state"],
                    "clickstream_normalized_state",
                    CLICKSTREAM_STATES,
                ),
                "clickstream_keyword_info_state": _as_state(
                    row["clickstream_keyword_info_state"],
                    "clickstream_keyword_info_state",
                    CLICKSTREAM_STATES,
                ),
            }
        )
        keyword_keys.add((identity, KEYWORD_DATA_KIND))
    if len(keyword_keys) != len(keywords):
        raise IntegrityError("duplicate keyword-data semantic identity")
    for name, indexed in child_rows.items():
        if indexed:
            raise IntegrityError(f"orphan {name} child row")
    if keyword_occurrences:
        raise IntegrityError("returned-item occurrence has no keyword-data fact")

    # One provider item states one placement and one keyword-data fact. Foreign keys prove
    # both parents exist; nothing in PostgreSQL proves they name the same provider keyword.
    keyword_by_index: dict[int, str] = {}
    for index, (placement, keyword_identity) in item_by_index.items():
        placement_word = placement_keyword[placement]
        keyword_word = keyword_identity_keyword[keyword_identity]
        if placement_word != keyword_word:
            raise IntegrityError(
                "returned-item occurrence links parents with different keywords"
            )
        keyword_by_index[index] = keyword_word

    # --- monthly Data Period facts -------------------------------------------------------
    monthly_occurrences: dict[str, list[int]] = {}
    for row in _rows(
        connection, MONTHLY_OCCURRENCES_TABLE, MONTHLY_OCCURRENCE_COLUMNS, capture_id
    ):
        identity = _as_text(row["within_capture_identity"], "within_capture_identity")
        if _as_text(row["observation_kind"], "observation_kind") != MONTHLY_KIND:
            raise IntegrityError("monthly occurrence has the wrong Observation kind")
        index = _as_int(row["item_index"], "item_index")
        if index not in item_by_index:
            raise IntegrityError("monthly occurrence has no returned-item occurrence")
        monthly_occurrences.setdefault(identity, []).append(index)

    monthly: list[dict[str, object]] = []
    monthly_keys: set[tuple[str, str]] = set()
    for row in _rows(connection, MONTHLY_TABLE, MONTHLY_COLUMNS, capture_id):
        identity = _as_text(row["within_capture_identity"], "within_capture_identity")
        if _as_text(row["observation_kind"], "observation_kind") != MONTHLY_KIND:
            raise IntegrityError("monthly row has the wrong Observation kind")
        if _as_text(row["requested_target"], "requested_target") != target:
            raise IntegrityError("monthly requested_target disagrees with the Attempt")
        keyword = _as_text(row["keyword"], "keyword")
        year = _as_int(row["year"], "year")
        month = _as_int(row["month"], "month")
        recomputed = _identity(
            MONTHLY_KIND,
            {
                "keyword": keyword,
                "month": month,
                "requested_target": target,
                "year": year,
            },
        )
        if recomputed != identity:
            raise IntegrityError("monthly identity axes do not recompute")
        parent = keyword_index.get(keyword)
        if parent is None:
            raise IntegrityError("monthly fact has no matching keyword-data fact")
        if parent[0] != "stated":
            raise IntegrityError("monthly fact under a non-stated keyword_info")
        if parent[1] != "stated":
            raise IntegrityError("monthly fact under a non-stated monthly_searches")
        indexes = sorted(monthly_occurrences.pop(identity, []))
        if not indexes:
            raise IntegrityError("monthly fact has no returned-item occurrence")
        for index in indexes:
            if keyword_by_index[index] != keyword:
                raise IntegrityError(
                    "monthly occurrence cites a different returned keyword"
                )
        monthly.append(
            {
                "observation_kind": MONTHLY_KIND,
                "within_capture_identity": identity,
                "requested_target": target,
                "keyword": keyword,
                "data_period": {"year": year, "month": month},
                "search_volume": _as_int(row["search_volume"], "search_volume"),
                "occurrences": [{"item_index": index} for index in indexes],
            }
        )
        monthly_keys.add((identity, MONTHLY_KIND))
    if len(monthly_keys) != len(monthly):
        raise IntegrityError("duplicate monthly semantic identity")
    if monthly_occurrences:
        raise IntegrityError("orphan monthly occurrence")

    semantic_keys = corpus_keys | ranked_keys | keyword_keys | monthly_keys
    total_semantic = len(corpus) + len(ranked) + len(keywords) + len(monthly)
    if len(semantic_keys) != total_semantic or semantic_keys != envelope_keys:
        raise IntegrityError("semantic parents disagree with the Observation envelopes")

    corpus.sort(
        key=lambda fact: (
            FAMILY_RANK[str(fact["aggregate_family"])],
            RANK_SYSTEM_RANK[str(fact["rank_system"])],
            str(fact["within_capture_identity"]),
        )
    )
    # Keyword-first, so the presentation is visibly not the frozen provider rank_group order.
    ranked.sort(
        key=lambda fact: (
            str(fact["keyword"]),
            str(fact["serp_item_type"]),
            _as_int(fact["rank_group"], "rank_group"),
            _as_int(fact["rank_absolute"], "rank_absolute"),
            str(fact["within_capture_identity"]),
        )
    )
    keywords.sort(
        key=lambda fact: (str(fact["keyword"]), str(fact["within_capture_identity"]))
    )
    monthly.sort(
        key=lambda fact: (
            str(fact["keyword"]),
            _as_int(_period(fact)["year"], "year"),
            _as_int(_period(fact)["month"], "month"),
            str(fact["within_capture_identity"]),
        )
    )
    return _Families(corpus, ranked, keywords, monthly, occurrences)


def _period(fact: Mapping[str, object]) -> Mapping[str, object]:
    period = fact["data_period"]
    if not isinstance(period, Mapping):
        raise IntegrityError("monthly fact is missing its Data Period")
    return period


def _require_single_outcome(
    connection: Connection[Any],
    *,
    capture_id: str,
    attempt_id: str,
    classification: str,
    observation_count: int,
) -> None:
    """A matching context must carry exactly one Outcome, for exactly its own Attempt.

    The context LEFT JOIN cannot prove this: `outcomes_identity` is unique over
    (derivation_version_id, attempt_id, capture_id), so a second Outcome for the same
    Capture under a foreign Attempt identity is SQL-permitted.
    """

    rows = connection.execute(
        """
        SELECT attempt_id, classification, observation_count
        FROM outcomes
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    ).fetchall()
    if len(rows) != 1:
        raise IntegrityError("matching Capture does not have exactly one Outcome")
    row = rows[0]
    if _as_text(row[0], "attempt_id") != attempt_id:
        raise IntegrityError("matching Capture Outcome cites a foreign Attempt")
    if _as_text(row[1], "classification") != classification:
        raise IntegrityError("Capture Outcome classification disagrees")
    if _as_int(row[2], "observation_count") != observation_count:
        raise IntegrityError("Capture Outcome observation_count disagrees")


def _require_request_agreement(
    request: Mapping[str, object], context: Mapping[str, object]
) -> None:
    """Persisted request context must agree with the verified Attempt everywhere it
    duplicates request testimony. Result echo is separate provider testimony."""

    duplicated: tuple[tuple[str, str], ...] = (
        ("target", "requested_target"),
        ("location_code", "request_location_code"),
        ("language_code", "request_language_code"),
        ("item_types", "request_item_types"),
        ("ignore_synonyms", "request_ignore_synonyms"),
        ("include_clickstream_data", "request_include_clickstream_data"),
        ("limit", "request_limit"),
        ("offset", "request_offset"),
        ("load_rank_absolute", "request_load_rank_absolute"),
        ("historical_serp_mode", "request_historical_serp_mode"),
        ("order_by", "request_order_by"),
    )
    for request_key, context_column in duplicated:
        stored = context[context_column]
        if isinstance(stored, tuple):
            stored = list(stored)
        if stored != request[request_key]:
            raise IntegrityError(
                f"persisted {context_column} disagrees with the verified Attempt"
            )


def _result_context(context: Mapping[str, object]) -> dict[str, object]:
    payload: dict[str, object] = {
        "target": _text_field(context, "result_target"),
        "location_code": _count_field(context, "result_location_code"),
        "language_code": _text_field(context, "result_language_code"),
        "se_type": _se_type_field(context, "result_se_type"),
        "total_count": _as_int(context["total_count"], "total_count"),
        "items_count": _as_int(context["items_count"], "items_count"),
    }
    if set(payload) != _RESULT_CONTEXT_KEYS:
        raise IntegrityError("result_context keys are not closed")
    return payload


def _require_text_field(document: Mapping[str, object], key: str) -> str:
    return _as_text(document.get(key), key)


def _subject_capture_ids(connection: Connection[Any], target: str) -> set[str]:
    """Captures with subject-bearing semantic parents for this exact requested target.

    Nothing in PostgreSQL references `ranked_keywords_result_context`, so deleting only that
    row would otherwise remove a Capture from context-anchored history and silently shrink
    total_matching while its Outcome, envelopes, parents, and occurrences survive.
    """

    found: set[str] = set()
    for table in SUBJECT_PARENT_TABLES:
        rows = connection.execute(
            sql.SQL(
                "SELECT DISTINCT capture_id FROM {} "
                "WHERE derivation_version_id = %s AND requested_target = %s"
            ).format(sql.Identifier(table)),
            (RANKED_KEYWORDS_RECIPE_ID, target),
        ).fetchall()
        found.update(_as_text(row[0], "capture_id") for row in rows)
    return found


def _verify_capture(
    store: EvidenceStore,
    connection: Connection[Any],
    candidate: Mapping[str, object],
    requested_target: str,
) -> dict[str, object]:
    """Verify one matching candidate completely, before any sort or limit is applied."""

    capture_id = _as_text(candidate["capture_id"], "capture_id")
    attempt_id = _as_text(candidate["attempt_id"], "attempt_id")
    classification = candidate["classification"]
    if classification is None:
        raise IntegrityError("matching context is missing its Capture Outcome")
    token = _as_text(classification, "classification")
    if token not in ADMITTED_CLASSIFICATIONS:
        raise IntegrityError("matching context is not an admitted Recipe v1 Outcome")
    observation_count = _as_int(candidate["observation_count"], "observation_count")
    if _as_text(candidate["requested_target"], "requested_target") != requested_target:
        raise IntegrityError("result context target disagrees with the requested subject")
    _require_single_outcome(
        connection,
        capture_id=capture_id,
        attempt_id=attempt_id,
        classification=token,
        observation_count=observation_count,
    )
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
        or capture.get("provider") != HISTORY_PROVIDER
        or attempt.get("provider") != HISTORY_PROVIDER
    ):
        raise IntegrityError("derived Evidence is not Ranked Keywords")
    request = _attempt_request(attempt)
    # The verified Attempt target, never a semantic row's self-claimed requested_target, is
    # the authority every identity below is recomputed against.
    if request["target"] != requested_target:
        raise IntegrityError("Attempt target disagrees with the history subject")
    _require_request_agreement(request, candidate)
    families = _capture_families(
        connection,
        capture_id=capture_id,
        attempt_id=attempt_id,
        target=requested_target,
        observation_count=observation_count,
        items_count=_as_int(candidate["items_count"], "items_count"),
    )
    payload: dict[str, object] = {
        "attempt_id": attempt_id,
        "capture_id": capture_id,
        "provider": HISTORY_PROVIDER,
        "adapter_contract": HISTORY_ADAPTER,
        "derivation_version_id": RANKED_KEYWORDS_RECIPE_ID,
        "authorized_at": _require_text_field(attempt, "authorized_at"),
        "request_started_at": _require_text_field(capture, "request_started_at"),
        "transport_ended_at": _require_text_field(capture, "transport_ended_at"),
        "request": request,
        "capture_outcome": {
            "classification": token,
            "observation_count": observation_count,
        },
        "result_context": _result_context(candidate),
        "corpus_metrics": families.corpus,
        "ranked_results": families.ranked,
        "keyword_data": families.keywords,
        "monthly_search_volume": families.monthly,
        "item_occurrences": families.occurrences,
    }
    if set(payload) != _CAPTURE_KEYS:
        raise IntegrityError("Capture keys are not closed")
    return payload


def _history_response(
    *,
    requested_target: str,
    derivation_version_id: str,
    recipe_resolution: Literal["selected", "pinned"],
    captures: Sequence[Mapping[str, object]],
    total_matching: int,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble Ranked outer history metadata around projected Capture documents.

    The shared helper hard-codes `requested_keyword`, which would misname a Ranked target,
    so the same outer list math and the same closed-key assertion are kept locally rather
    than renaming an already-published sibling contract.
    """

    if type(total_matching) is not int or isinstance(total_matching, bool):
        raise TypeError("total_matching must be an integer")
    if type(limit) is not int or isinstance(limit, bool):
        raise TypeError("limit must be an integer")
    if total_matching < 0:
        raise ValueError("total_matching must not be negative")
    if limit < 1 or limit > HISTORY_LIMIT_MAX:
        raise ValueError("limit is outside the accepted outer history bound")
    if order not in ("asc", "desc"):
        raise ValueError("order must be asc or desc")
    projected = list(captures)
    returned_count = len(projected)
    if returned_count > total_matching:
        raise ValueError("returned_count exceeds total_matching")
    if returned_count > limit:
        raise ValueError("returned_count exceeds applied limit")
    payload: dict[str, object] = {
        "provider": HISTORY_PROVIDER,
        "adapter_contract": HISTORY_ADAPTER,
        "requested_target": requested_target,
        "derivation_version_id": derivation_version_id,
        "recipe_resolution": recipe_resolution,
        "observation_kinds": list(V1_KINDS),
        "captures": projected,
        "total_matching": total_matching,
        "returned_count": returned_count,
        "limit": limit,
        "order": order,
        "has_more": total_matching > returned_count,
    }
    if set(payload) != RANKED_OUTER_HISTORY_KEYS:
        raise ValueError("Ranked history envelope keys are not the accepted 12-key set")
    return payload


def _require_accepted_v1_registration(
    connection: Connection[Any], pinned_version: str | None
) -> None:
    """Ranked-local integrity guard that must run before generic Recipe resolution.

    `resolve_provider_recipe()` compares the requested adapter against the registration's
    stored `adapter_contract` and refuses a disagreement as a selection miss: 503 on the
    selected path, 404 on an explicit pin. That is correct for an unrelated or genuinely
    wrong-adapter Recipe, but the accepted contract classifies damaged accepted-v1 Recipe
    metadata as rebuildable-state integrity failure, not as absence.

    So when the exact accepted Ranked v1 digest is the thing being resolved -- pinned
    explicitly, or named by this adapter's current selection -- a present registration row
    whose stored adapter disagrees is raised as `IntegrityError` here instead. Every other
    Recipe, a true missing selection, and a missing registration keep their generic
    behaviour. Damaged `provider` metadata already reaches `_load_validated_v1_recipe`
    unchanged and needs no guard.
    """

    if pinned_version is None:
        selected = connection.execute(
            """
            SELECT derivation_version_id
            FROM provider_recipe_selections
            WHERE adapter_contract = %s
            """,
            (HISTORY_ADAPTER,),
        ).fetchone()
        if selected is None:
            return
        referenced = str(selected[0])
    else:
        referenced = pinned_version
    if referenced != RANKED_KEYWORDS_RECIPE_ID:
        return
    row = connection.execute(
        """
        SELECT adapter_contract
        FROM provider_recipes
        WHERE derivation_version_id = %s
        """,
        (RANKED_KEYWORDS_RECIPE_ID,),
    ).fetchone()
    if row is None:
        return
    if str(row[0]) != HISTORY_ADAPTER:
        raise IntegrityError(
            "registered accepted Recipe adapter metadata disagrees with this route"
        )


def load_ranked_keywords_history(
    store: EvidenceStore,
    connection: Connection[Any],
    *,
    requested_target: str,
    pinned_version: str | None,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble surface-explicit Ranked Keywords history for one exact requested target."""

    _require_accepted_v1_registration(connection, pinned_version)
    resolved = resolve_provider_recipe(connection, HISTORY_ADAPTER, pinned_version)
    recipe = _load_validated_v1_recipe(connection, resolved)
    rows = connection.execute(
        CANDIDATE_SQL, (requested_target, RANKED_KEYWORDS_RECIPE_ID)
    ).fetchall()
    candidates: list[dict[str, object]] = []
    seen: set[str] = set()
    for row in rows:
        candidate = dict(zip(CANDIDATE_ROW_KEYS, row, strict=True))
        capture_id = _as_text(candidate["capture_id"], "capture_id")
        if capture_id in seen:
            raise IntegrityError("duplicate admitted Capture candidate")
        seen.add(capture_id)
        candidates.append(candidate)
    if _subject_capture_ids(connection, requested_target) != seen:
        raise IntegrityError(
            "subject-bearing semantic parents disagree with the result-context candidates"
        )
    verified: list[tuple[str, str, dict[str, object]]] = []
    for candidate in candidates:
        payload = _verify_capture(store, connection, candidate, requested_target)
        verified.append(
            (
                str(payload["request_started_at"]),
                _as_text(payload["capture_id"], "capture_id"),
                payload,
            )
        )
    verified.sort(key=lambda item: (item[0], item[1]), reverse=order == "desc")
    selected = [item[2] for item in verified[:limit]]
    envelope = _history_response(
        requested_target=requested_target,
        derivation_version_id=recipe.derivation_version_id,
        recipe_resolution=recipe.resolution,
        captures=selected,
        total_matching=len(verified),
        limit=limit,
        order=order,
    )
    try:
        return RankedKeywordsHistoryEnvelope.model_validate(envelope).model_dump()
    except ValidationError as exc:
        raise IntegrityError("malformed Ranked Keywords history projection") from exc
