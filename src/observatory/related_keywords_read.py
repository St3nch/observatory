"""Read-side assembly for DataForSEO Google Related Keywords admitted history.

RK-05 turns the rebuildable RK-04 state for one verified Capture back into one
subject-bound Capture document: verified Attempt request testimony, provider result
context, three semantic Observation families, and their provider occurrence testimony.

It invents no graph meaning. `related_keywords` relationship rows are provider relatedness
testimony, never a tree, traversal order, similarity score, canonical identity, importance,
centrality, or a completeness claim. `core_keyword` stays provider field testimony. Current
`search_volume` stays current provider testimony and is never derived from a monthly point.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from decimal import Decimal
from typing import Any, Final, Literal, Self

from psycopg import Connection
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from observatory.capture_event import (
    RELATED_KEYWORDS_ADAPTER_CONTRACT,
    DocumentError,
    canonical_json,
    content_digest,
    validate_related_keywords_http_parameters,
)
from observatory.dataforseo_google_related_keywords import (
    KEYWORD_DATA_KIND,
    LOCUS_ITEM,
    LOCUS_SEED,
    MONTHLY_KIND,
    PROVIDER,
    RELATED_KEYWORDS_RECIPE,
    RELATED_KEYWORDS_RECIPE_ID,
    RELATIONSHIP_KIND,
)
from observatory.evidence_store import EvidenceStore, IntegrityError
from observatory.google_related_keywords_derive import (
    BACKLINKS_TABLE,
    CONTEXT_TABLE,
    INTENT_TABLE,
    ITEM_OCCURRENCES_TABLE,
    KEYWORD_DATA_TABLE,
    KEYWORD_INFO_TABLE,
    MONTHLY_OCCURRENCES_TABLE,
    MONTHLY_TABLE,
    PROPERTIES_TABLE,
    RELATIONSHIP_OCCURRENCES_TABLE,
    RELATIONSHIP_TABLE,
    SERP_TABLE,
)
from observatory.provider_history import HISTORY_LIMIT_MAX, history_list_response
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
HISTORY_ADAPTER: Final[str] = RELATED_KEYWORDS_ADAPTER_CONTRACT
IJSON_MAX: Final[int] = 9007199254740991

# Exact ordered Recipe v1 Observation kinds.
V1_KINDS: Final[tuple[str, str, str]] = (
    KEYWORD_DATA_KIND,
    MONTHLY_KIND,
    RELATIONSHIP_KIND,
)

# Exact stored Recipe v1 Capture classification vocabulary, in its stored order.
V1_CAPTURE_OUTCOMES: Final[tuple[str, ...]] = (
    "no_response",
    "observation_admitted",
    "observation_admitted_empty",
    "provider_envelope_rejected",
    "provider_error",
    "reconciliation_failed",
    "response_partial",
    "transport_complete_non_admissible",
)
ADMITTED_CLASSIFICATIONS: Final[frozenset[str]] = frozenset(
    {"observation_admitted", "observation_admitted_empty"}
)
# The Recipe's global field-state vocabulary is five tokens, but no single RK-04 column
# permits all five. Each read domain below is the exact applicable subset that RK-03 can
# produce and RK-04 can persist for that structure; a token outside its own domain is
# Recipe-v1 damage even though the generic SQL CHECK accepts it.
FIELD_STATES: Final[frozenset[str]] = frozenset(
    {"absent", "inapplicable", "json_null", "not_requested", "stated"}
)
OPTIONAL_FIELD_STATES: Final[frozenset[str]] = frozenset(
    {"absent", "json_null", "stated"}
)
TREND_MEMBER_STATES: Final[frozenset[str]] = frozenset(
    {"absent", "inapplicable", "json_null", "stated"}
)
BING_STATES: Final[frozenset[str]] = frozenset({"absent", "json_null"})
CLICKSTREAM_STATES: Final[frozenset[str]] = frozenset({"not_requested"})
SE_TYPE: Final[str] = "google"

# Presentation rank. Lexical locus ordering would place returned_item before
# seed_keyword_data, so the rank is explicit and is presentation only, never identity.
LOCUS_RANK: Final[dict[str, int]] = {LOCUS_SEED: 0, LOCUS_ITEM: 1}

_SEMANTIC_KEY_COLUMNS: Final[tuple[str, ...]] = (
    "within_capture_identity",
    "observation_kind",
)

# Every persisted RK-04 content column is projected. `tests/test_api_related_keywords.py`
# pins these tuples against information_schema so a future column cannot be silently
# dropped from consumer-visible testimony.
KEYWORD_DATA_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "requested_seed",
    "locus",
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
    "serp_info_state",
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
SERP_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "se_type",
    "se_type_state",
    "check_url",
    "check_url_state",
    "serp_item_types",
    "serp_item_types_state",
    "se_results_count",
    "se_results_count_state",
    "serp_last_updated_time",
    "serp_last_updated_time_state",
    "serp_previous_updated_time",
    "serp_previous_updated_time_state",
)
MONTHLY_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "requested_seed",
    "locus",
    "keyword",
    "year",
    "month",
    "search_volume",
)
RELATIONSHIP_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "requested_seed",
    "source_keyword",
    "target_keyword",
)
ITEM_OCCURRENCE_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "item_index",
    "depth",
    "item_se_type",
    "related_keywords_state",
)
MONTHLY_OCCURRENCE_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "item_index",
)
RELATIONSHIP_OCCURRENCE_COLUMNS: Final[tuple[str, ...]] = (
    *_SEMANTIC_KEY_COLUMNS,
    "source_item_index",
    "target_index",
    "source_depth",
)
CONTEXT_COLUMNS: Final[tuple[str, ...]] = (
    "attempt_id",
    "requested_seed",
    "request_location_code",
    "request_language_code",
    "request_depth",
    "request_limit",
    "request_offset",
    "request_order_by",
    "request_include_seed_keyword",
    "request_include_serp_info",
    "request_include_clickstream_data",
    "request_ignore_synonyms",
    "request_replace_with_core_keyword",
    "result_seed_keyword",
    "result_location_code",
    "result_location_code_state",
    "result_language_code",
    "result_language_code_state",
    "result_se_type",
    "result_se_type_state",
    "total_count",
    "items_count",
    "seed_keyword_data_state",
    "derived_returned_item_count",
    "derived_relationship_occurrence_count",
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
    + " WHERE c.requested_seed = %s AND c.derivation_version_id = %s"
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
    ("serp_info", SERP_TABLE, "serp_info_state", SERP_COLUMNS),
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
        "keyword_data",
        "monthly_search_volume",
        "relationships",
    }
)
_REQUEST_KEYS: Final[frozenset[str]] = frozenset(
    {
        "keyword",
        "location_code",
        "language_code",
        "depth",
        "limit",
        "offset",
        "order_by",
        "include_seed_keyword",
        "include_serp_info",
        "include_clickstream_data",
        "ignore_synonyms",
        "replace_with_core_keyword",
    }
)
_RESULT_CONTEXT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "seed_keyword",
        "location_code",
        "language_code",
        "se_type",
        "total_count",
        "items_count",
        "seed_keyword_data_state",
        "derived_returned_item_count",
        "derived_relationship_occurrence_count",
    }
)

_GRAIN: Final[str] = (
    "Admitted, subject-bound Related Keywords Capture-document history under Recipe v1. "
    "This list grain is whole Capture documents, not Observation envelopes, keyword-data "
    "facts, monthly Data Period facts, relationship facts, provider occurrences, provider "
    "total_count, provider items_count, or graph nodes."
)
_EMPTY: Final[str] = (
    "Empty admitted history (total_matching 0, captures empty) means only that no matching "
    "admitted Capture document exists under this exact route, requested_keyword, and "
    "Recipe v1. It does not mean never measured, failed, refused, unresolved, "
    "'no related keywords', provider zero, or absence from a provider corpus."
)
_ADMITTED_EMPTY: Final[str] = (
    "observation_admitted_empty is valid subject-bearing history: one result context and "
    "zero semantic facts. It is distinct from empty outer history, from failure, and from "
    "never measured. A stated seed KeywordData whose items array is empty is ordinary "
    "observation_admitted testimony, not observation_admitted_empty."
)
_ORDER: Final[str] = (
    "Echo of the validated query order. Deterministic outer ordering is "
    "(request_started_at, capture_id); descending reverses that complete key before "
    "limiting. This is not provider item order, depth order, or relatedness order."
)
_HAS_MORE: Final[str] = (
    "True when total_matching exceeds returned_count. Discloses an omitted outer "
    "Capture-history tail. This is not pagination, a cursor, or authorization to fetch "
    "another provider request."
)
_COUNT: Final[str] = (
    "observation_count is Observation-envelope cardinality only: keyword-data plus "
    "monthly plus relationship semantic identities for this Capture. It is not provider "
    "total_count, provider items_count, returned-item count, monthly point count, "
    "relationship occurrence count, graph node count, or completeness."
)
_PROVIDER_COUNTS: Final[str] = (
    "total_count and items_count are exact provider result testimony. items_count equals "
    "the Observatory-derived returned-item count for admitted Recipe v1 documents. "
    "total_count is neither a completeness claim nor a pagination bound, and equality "
    "between total_count and items_count in any one Capture is testimony, not a rule."
)
_DERIVED_COUNT: Final[str] = (
    "Observatory-derived count recomputed from the parsed Capture, explicitly labelled to "
    "keep it distinct from provider-stated counts."
)
_LOCUS: Final[str] = (
    "locus distinguishes the provider's seed_keyword_data structure from a returned_item "
    "keyword_data structure. It is not depth, rank, item position, or identity across "
    "Captures. The same exact keyword string may appear under both loci as two distinct "
    "semantic identities that may disagree."
)
_OCCURRENCE: Final[str] = (
    "Provider placement testimony for one semantic identity. item_index is the exact "
    "returned-items array position and depth is the provider's stated item depth. Neither "
    "is rank, importance, tree parentage, or keyword identity. Seed-locus facts have no "
    "item occurrence because the seed structure is not an items-array member."
)
_RELATEDNESS: Final[str] = (
    "Provider relatedness testimony from one source item's related_keywords array. It is "
    "not a tree edge, BFS traversal, parent/child link, semantic similarity, topic "
    "membership, canonical identity, centrality, importance, or completeness. A target "
    "keyword needs no keyword-data node: frontier targets legitimately have none."
)
_TARGET_INDEX: Final[str] = (
    "Exact lexical position inside that source item's related_keywords array. Target "
    "indexes are dense per source item occurrence across all relationship parents for that "
    "source, never per semantic relationship parent. Not rank or relevance."
)
_CORE_KEYWORD: Final[str] = (
    "Exact provider keyword_properties.core_keyword field testimony. It is not canonical "
    "identity, a synonym equivalence claim, a normalization target, a relationship edge, "
    "or a substitute for the requested subject."
)
_CURRENT_VOLUME: Final[str] = (
    "Current provider search_volume testimony from keyword_info. It is never computed "
    "from, equal to, or replaceable by a monthly Data Period point, and may legitimately "
    "disagree with the newest monthly point."
)
_PERIOD: Final[str] = (
    "Provider-stated Data Period. It is not Capture time, Attempt time, a structure-local "
    "provider clock, or a recurrence claim beyond the exact stated periods."
)
_CLOCKS: Final[str] = (
    "Structure-local provider clock. Related Keywords states no universal Provider Update "
    "Time: each structure keeps its own clock and they may disagree. Exact lexical "
    "testimony survives, including '0001-01-01 00:00:00 +00:00', which carries no sentinel "
    "meaning here. It is not Capture time."
)
_TIME: Final[str] = (
    "Observatory Attempt and Capture timestamps from verified Evidence. They must not "
    "substitute for Data Period or for any structure-local provider clock."
)
_STATE: Final[str] = (
    "Closed provider field state. Ordinary optional provider testimony carries exactly "
    "absent, json_null, or stated: the field was not present, was present as JSON null, or "
    "carried a value. These are never collapsed into one another. value is non-null exactly "
    "when state is stated; a stated-empty array is {state: 'stated', value: []} and a "
    "stated-empty string is exact testimony, not absence. not_requested and inapplicable "
    "are not applicable to ordinary optional fields under Recipe v1 and are reported as "
    "integrity failure rather than served."
)
_TREND_MEMBER_STATE: Final[str] = (
    "Signed provider trend member. When the enclosing search_volume_trend object is stated "
    "the member carries an ordinary absent, json_null, or stated state. When the enclosing "
    "object is not stated the member has no state of its own and is exactly inapplicable "
    "with a null value; that is not the same as an absent or json_null member inside a "
    "stated trend object."
)
_SE_TYPE_STATE: Final[str] = (
    "Provider search-engine type. RK-03 admits only the exact value 'google' for this "
    "closed adapter, so a stated se_type is exactly 'google'; absent and json_null remain "
    "possible wherever the provider omits or nulls the field. Any other stored value is "
    "integrity failure, not new provider vocabulary."
)
_ENCLOSING_STATE: Final[str] = (
    "Closed provider state of the enclosing provider object. value is the fully typed "
    "child object exactly when state is stated, otherwise null. The absence of a stored "
    "child row is never itself read as a state signal."
)
_STATE_ONLY: Final[str] = (
    "State-only provider testimony exposed as the exact lower-case closed state token. "
    "RK-04 persists no value for this structure, so no value is synthesized."
)
_ECHO: Final[str] = (
    "Provider result echo testimony. It may disagree with the verified Attempt request "
    "block, which remains the request authority. Disagreement is reported, never repaired."
)
_REQUEST_AUTHORITY: Final[str] = (
    "Exact verified Attempt request testimony read from committed Evidence, not from task "
    "echo or result echo. Frozen adapter values are documented as literals, and the "
    "accepted Attempt parameter validator still runs against the Evidence document."
)


class UnsupportedRelatedKeywordsRecipe(ProviderRecipeSelectionError):
    """Resolved Recipe is not the accepted Related Keywords v1 identity."""


OptionalStateToken = Literal["absent", "json_null", "stated"]
TrendMemberStateToken = Literal["absent", "inapplicable", "json_null", "stated"]
BingStateToken = Literal["absent", "json_null"]
ClickstreamStateToken = Literal["not_requested"]


def _agree(state: str, value: object) -> None:
    if (value is None) == (state == "stated"):
        raise ValueError("value is present exactly when state is stated")


class RelatedKeywordsTextField(BaseModel):
    """Provider text testimony persisted as a value/state column pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_STATE)
    value: str | None = Field(description=_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RelatedKeywordsCountField(BaseModel):
    """Non-negative provider integer testimony as a value/state pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_STATE)
    value: int | None = Field(ge=0, le=IJSON_MAX, description=_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RelatedKeywordsTrendMemberField(BaseModel):
    """Signed provider search-volume trend member as a value/state pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: TrendMemberStateToken = Field(description=_TREND_MEMBER_STATE)
    value: int | None = Field(
        ge=-IJSON_MAX, le=IJSON_MAX, description=_TREND_MEMBER_STATE
    )

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RelatedKeywordsSeTypeField(BaseModel):
    """Closed provider se_type testimony as a value/state pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_SE_TYPE_STATE)
    value: Literal["google"] | None = Field(description=_SE_TYPE_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RelatedKeywordsBoolField(BaseModel):
    """Provider boolean testimony as a value/state pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_STATE)
    value: bool | None = Field(description=_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RelatedKeywordsDecimalField(BaseModel):
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


class RelatedKeywordsIntArrayField(BaseModel):
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


class RelatedKeywordsTextArrayField(BaseModel):
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


class RelatedKeywordsKeywordInfo(BaseModel):
    """Exact persisted provider keyword_info testimony for one semantic identity."""

    model_config = ConfigDict(extra="forbid", strict=True)

    se_type: RelatedKeywordsSeTypeField
    keyword_info_last_updated_time: RelatedKeywordsTextField = Field(description=_CLOCKS)
    competition: RelatedKeywordsDecimalField
    competition_level: RelatedKeywordsTextField
    cpc: RelatedKeywordsDecimalField
    search_volume: RelatedKeywordsCountField = Field(description=_CURRENT_VOLUME)
    low_top_of_page_bid: RelatedKeywordsDecimalField
    high_top_of_page_bid: RelatedKeywordsDecimalField
    categories: RelatedKeywordsIntArrayField = Field(
        description=(
            "Exact ordered provider category identifiers, duplicates preserved. Not a "
            "taxonomy, a set, or an Observatory classification."
        )
    )
    monthly_searches_state: OptionalStateToken = Field(
        description=(
            "State of the provider monthly_searches array. The monthly points themselves "
            "are the separate monthly_search_volume Observation family. A stated array may "
            "legitimately be empty, so a stated state with no monthly facts is valid; "
            "monthly facts under a non-stated state are integrity failure. " + _STATE_ONLY
        )
    )
    search_volume_trend_state: OptionalStateToken = Field(
        description=(
            "State of the enclosing provider search_volume_trend object. When it is not "
            "stated its members carry the Recipe-v1 state 'inapplicable' rather than a "
            "collapsed absence. " + _STATE_ONLY
        )
    )
    trend_monthly: RelatedKeywordsTrendMemberField
    trend_quarterly: RelatedKeywordsTrendMemberField
    trend_yearly: RelatedKeywordsTrendMemberField

    @model_validator(mode="after")
    def _require_trend_member_agreement(self) -> Self:
        members = (self.trend_monthly, self.trend_quarterly, self.trend_yearly)
        if self.search_volume_trend_state != "stated":
            if any(member.state != "inapplicable" for member in members):
                raise ValueError(
                    "an unstated search_volume_trend has inapplicable members only"
                )
        elif any(member.state == "inapplicable" for member in members):
            raise ValueError(
                "a stated search_volume_trend has ordinary member states only"
            )
        return self


class RelatedKeywordsKeywordProperties(BaseModel):
    """Exact persisted provider keyword_properties testimony."""

    model_config = ConfigDict(extra="forbid", strict=True)

    se_type: RelatedKeywordsSeTypeField
    core_keyword: RelatedKeywordsTextField = Field(description=_CORE_KEYWORD)
    synonym_clustering_algorithm: RelatedKeywordsTextField = Field(
        description=(
            "Exact provider algorithm label. Observatory performs no synonym clustering "
            "and claims no equivalence. " + _CORE_KEYWORD
        )
    )
    keyword_difficulty: RelatedKeywordsCountField
    detected_language: RelatedKeywordsTextField
    is_another_language: RelatedKeywordsBoolField


class RelatedKeywordsAvgBacklinks(BaseModel):
    """Exact persisted provider avg_backlinks_info testimony."""

    model_config = ConfigDict(extra="forbid", strict=True)

    se_type: RelatedKeywordsSeTypeField
    backlinks: RelatedKeywordsDecimalField
    dofollow: RelatedKeywordsDecimalField
    referring_pages: RelatedKeywordsDecimalField
    referring_domains: RelatedKeywordsDecimalField
    referring_main_domains: RelatedKeywordsDecimalField
    rank: RelatedKeywordsDecimalField = Field(
        description=(
            "Exact provider backlink rank value. It is not a SERP position, an Observatory "
            "ranking, importance, or opportunity."
        )
    )
    main_domain_rank: RelatedKeywordsDecimalField
    avg_backlinks_last_updated_time: RelatedKeywordsTextField = Field(description=_CLOCKS)


class RelatedKeywordsSearchIntent(BaseModel):
    """Exact persisted provider search_intent_info testimony."""

    model_config = ConfigDict(extra="forbid", strict=True)

    se_type: RelatedKeywordsSeTypeField
    main_intent: RelatedKeywordsTextField = Field(
        description="Open provider intent vocabulary. Observatory adds no closed taxonomy."
    )
    foreign_intent: RelatedKeywordsTextArrayField = Field(
        description="Exact ordered provider array, duplicates preserved."
    )
    search_intent_last_updated_time: RelatedKeywordsTextField = Field(description=_CLOCKS)


class RelatedKeywordsSerpInfo(BaseModel):
    """Exact persisted provider serp_info testimony."""

    model_config = ConfigDict(extra="forbid", strict=True)

    se_type: RelatedKeywordsSeTypeField
    check_url: RelatedKeywordsTextField = Field(
        description=(
            "Exact provider check_url string. Not normalized, resolved, fetched, or "
            "interpreted as a Page."
        )
    )
    serp_item_types: RelatedKeywordsTextArrayField = Field(
        description="Exact ordered provider array, duplicates preserved."
    )
    se_results_count: RelatedKeywordsCountField = Field(
        description=(
            "Exact provider search-engine result count testimony. Not an Observatory "
            "count, corpus size, or completeness claim."
        )
    )
    serp_last_updated_time: RelatedKeywordsTextField = Field(description=_CLOCKS)
    serp_previous_updated_time: RelatedKeywordsTextField = Field(description=_CLOCKS)


class RelatedKeywordsKeywordInfoStructure(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_ENCLOSING_STATE)
    value: RelatedKeywordsKeywordInfo | None = Field(description=_ENCLOSING_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RelatedKeywordsPropertiesStructure(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_ENCLOSING_STATE)
    value: RelatedKeywordsKeywordProperties | None = Field(description=_ENCLOSING_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RelatedKeywordsBacklinksStructure(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_ENCLOSING_STATE)
    value: RelatedKeywordsAvgBacklinks | None = Field(description=_ENCLOSING_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RelatedKeywordsIntentStructure(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_ENCLOSING_STATE)
    value: RelatedKeywordsSearchIntent | None = Field(description=_ENCLOSING_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RelatedKeywordsSerpStructure(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    state: OptionalStateToken = Field(description=_ENCLOSING_STATE)
    value: RelatedKeywordsSerpInfo | None = Field(description=_ENCLOSING_STATE)

    @model_validator(mode="after")
    def _require_agreement(self) -> Self:
        _agree(self.state, self.value)
        return self


class RelatedKeywordsItemOccurrence(BaseModel):
    """One returned-items array placement of a keyword-data semantic identity."""

    model_config = ConfigDict(extra="forbid", strict=True)

    item_index: int = Field(ge=0, le=IJSON_MAX, description=_OCCURRENCE)
    depth: int = Field(ge=0, le=4, description=_OCCURRENCE)
    item_se_type: Literal["google"] = Field(
        description=(
            "Exact provider items[].se_type testimony for this placement. RK-03 admits only "
            "the exact value 'google' for a returned item, and this field is required rather "
            "than optional, so it is item-level testimony with a closed vocabulary. It is "
            "still distinct from any structure-local se_type."
        )
    )
    related_keywords_state: OptionalStateToken = Field(
        description=(
            "State of this item's related_keywords array. A non-stated state has zero "
            "relationship occurrences; a stated-empty array also has zero. " + _RELATEDNESS
        )
    )


class RelatedKeywordsMonthlyOccurrence(BaseModel):
    """One returned-items array placement that stated this monthly Data Period fact."""

    model_config = ConfigDict(extra="forbid", strict=True)

    item_index: int = Field(ge=0, le=IJSON_MAX, description=_OCCURRENCE)


class RelatedKeywordsRelationshipOccurrence(BaseModel):
    """One provider array placement of a relatedness pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

    source_item_index: int = Field(ge=0, le=IJSON_MAX, description=_OCCURRENCE)
    source_depth: int = Field(ge=0, le=4, description=_OCCURRENCE)
    target_index: int = Field(ge=0, le=IJSON_MAX, description=_TARGET_INDEX)


class RelatedKeywordsDataPeriod(BaseModel):
    """Provider-stated calendar Data Period."""

    model_config = ConfigDict(extra="forbid", strict=True)

    year: int = Field(ge=1, le=9999, description=_PERIOD)
    month: int = Field(ge=1, le=12, description=_PERIOD)


class RelatedKeywordsKeywordDataFact(BaseModel):
    """One keyword-data semantic Observation and its provider occurrences."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal["dataforseo.google.related_keywords.keyword_data.v1"]
    within_capture_identity: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
        description=(
            "Recipe-v1 identity digest recomputed from the persisted axes requested_seed, "
            "locus, and keyword. Within-Capture only; not cross-Capture identity."
        ),
    )
    requested_seed: str = Field(
        min_length=1,
        description=(
            "Exact verified Attempt seed. The outer query names the same value "
            "requested_keyword; requested_seed is the Recipe identity axis name."
        ),
    )
    locus: Literal["seed_keyword_data", "returned_item"] = Field(description=_LOCUS)
    keyword: str = Field(
        min_length=1,
        description=(
            "Exact provider keyword string for this structure. Not trimmed, case-folded, "
            "normalized, or replaced by core_keyword."
        ),
    )
    location_code: RelatedKeywordsCountField
    language_code: RelatedKeywordsTextField
    se_type: RelatedKeywordsSeTypeField = Field(
        description=(
            "Structure-local provider se_type, distinct from item-level se_type. "
            + _SE_TYPE_STATE
        )
    )
    keyword_info: RelatedKeywordsKeywordInfoStructure
    keyword_properties: RelatedKeywordsPropertiesStructure
    avg_backlinks: RelatedKeywordsBacklinksStructure
    search_intent: RelatedKeywordsIntentStructure
    serp_info: RelatedKeywordsSerpStructure
    bing_normalized_state: BingStateToken = Field(
        description=(
            "State of provider keyword_info_normalized_with_bing. RK-03 does not support a "
            "populated Bing structure, so this is exactly absent or json_null; it is never "
            "stated and never request-disabled. " + _STATE_ONLY
        )
    )
    clickstream_normalized_state: ClickstreamStateToken = Field(
        description=(
            "State of provider keyword_info_normalized_with_clickstream. The closed adapter "
            "freezes include_clickstream_data to false, so this is exactly not_requested: "
            "request-disabled testimony, never a provider failure and never an absence. "
            + _STATE_ONLY
        )
    )
    clickstream_keyword_info_state: ClickstreamStateToken = Field(
        description=(
            "State of provider clickstream_keyword_info. The closed adapter freezes "
            "include_clickstream_data to false, so this is exactly not_requested. "
            + _STATE_ONLY
        )
    )
    occurrences: list[RelatedKeywordsItemOccurrence] = Field(
        description=(
            "Complete ordered returned-item placements for this identity. Empty exactly "
            "for the seed locus. " + _OCCURRENCE
        )
    )


class RelatedKeywordsMonthlyFact(BaseModel):
    """One monthly Data Period semantic Observation and its provider occurrences."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal[
        "dataforseo.google.related_keywords.monthly_search_volume.v1"
    ]
    within_capture_identity: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
        description=(
            "Recipe-v1 identity digest recomputed from requested_seed, locus, keyword, "
            "year, and month."
        ),
    )
    requested_seed: str = Field(min_length=1)
    locus: Literal["seed_keyword_data", "returned_item"] = Field(description=_LOCUS)
    keyword: str = Field(min_length=1)
    data_period: RelatedKeywordsDataPeriod = Field(description=_PERIOD)
    search_volume: int = Field(
        ge=0,
        le=IJSON_MAX,
        description=(
            "Exact provider monthly search volume for this Data Period. A stated zero is "
            "an ordinary fact, not absence. " + _CURRENT_VOLUME
        ),
    )
    occurrences: list[RelatedKeywordsMonthlyOccurrence] = Field(
        description=(
            "Returned-item placements that stated this Data Period. Empty exactly for the "
            "seed locus. " + _OCCURRENCE
        )
    )


class RelatedKeywordsRelationship(BaseModel):
    """One provider relatedness pair and every array placement that stated it."""

    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal["dataforseo.google.related_keywords.relationship.v1"]
    within_capture_identity: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
        description=(
            "Recipe-v1 identity digest recomputed from requested_seed, source_keyword, and "
            "target_keyword."
        ),
    )
    requested_seed: str = Field(min_length=1)
    source_keyword: str = Field(min_length=1, description=_RELATEDNESS)
    target_keyword: str = Field(min_length=1, description=_RELATEDNESS)
    occurrences: list[RelatedKeywordsRelationshipOccurrence] = Field(
        min_length=1, description=_RELATEDNESS + " " + _TARGET_INDEX
    )


class RelatedKeywordsRequest(BaseModel):
    """Closed verified Attempt request block."""

    model_config = ConfigDict(extra="forbid", strict=True)

    keyword: str = Field(min_length=1, description=_REQUEST_AUTHORITY)
    location_code: Literal[2840] = Field(description=_REQUEST_AUTHORITY)
    language_code: Literal["en"] = Field(description=_REQUEST_AUTHORITY)
    depth: Literal[3] = Field(
        description=(
            "Frozen adapter request depth. It bounds what the provider returned; it is not "
            "a tree, traversal guarantee, or completeness claim. " + _REQUEST_AUTHORITY
        )
    )
    limit: Literal[1000] = Field(
        description=(
            "Frozen adapter provider-side request limit. Unrelated to the outer history "
            "limit. " + _REQUEST_AUTHORITY
        )
    )
    offset: Literal[0] = Field(description=_REQUEST_AUTHORITY)
    order_by: list[Literal["keyword_data.keyword_info.search_volume,desc"]] = Field(
        min_length=1,
        max_length=1,
        description=(
            "Frozen ordered adapter sort testimony. It is provider request ordering, not "
            "Observatory presentation order or rank. " + _REQUEST_AUTHORITY
        ),
    )
    include_seed_keyword: Literal[True] = Field(description=_REQUEST_AUTHORITY)
    include_serp_info: Literal[True] = Field(description=_REQUEST_AUTHORITY)
    include_clickstream_data: Literal[False] = Field(
        description=(
            "Frozen adapter flag. Clickstream states in keyword-data testimony are "
            "request-disabled, not provider failures. " + _REQUEST_AUTHORITY
        )
    )
    ignore_synonyms: Literal[False] = Field(description=_REQUEST_AUTHORITY)
    replace_with_core_keyword: Literal[False] = Field(
        description=(
            "Frozen adapter flag. Returned keywords are never replaced by core_keyword. "
            + _CORE_KEYWORD
        )
    )


class RelatedKeywordsCaptureOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    classification: Literal["observation_admitted", "observation_admitted_empty"] = (
        Field(description=_ADMITTED_EMPTY)
    )
    observation_count: int = Field(ge=0, le=IJSON_MAX, description=_COUNT)

    @model_validator(mode="after")
    def _require_classification_agreement(self) -> Self:
        empty = self.classification == "observation_admitted_empty"
        if empty and self.observation_count != 0:
            raise ValueError("observation_admitted_empty requires observation_count 0")
        if not empty and self.observation_count < 1:
            raise ValueError("observation_admitted requires a positive observation_count")
        return self


class RelatedKeywordsResultContext(BaseModel):
    """Provider result-level testimony. The request block remains request authority."""

    model_config = ConfigDict(extra="forbid", strict=True)

    seed_keyword: str = Field(description=_ECHO)
    location_code: RelatedKeywordsCountField = Field(description=_ECHO + " " + _STATE)
    language_code: RelatedKeywordsTextField = Field(description=_ECHO + " " + _STATE)
    se_type: RelatedKeywordsSeTypeField = Field(
        description=_ECHO + " " + _SE_TYPE_STATE
    )
    total_count: int = Field(ge=0, le=IJSON_MAX, description=_PROVIDER_COUNTS)
    items_count: int = Field(ge=0, le=IJSON_MAX, description=_PROVIDER_COUNTS)
    seed_keyword_data_state: OptionalStateToken = Field(
        description=(
            "State of the provider result-level seed_keyword_data structure. A stated seed "
            "structure whose items array is empty is still ordinary admitted testimony. "
            "A stated state requires exactly one seed_keyword_data locus keyword-data fact "
            "and a non-stated state requires none. " + _STATE_ONLY
        )
    )
    derived_returned_item_count: int = Field(
        ge=0, le=IJSON_MAX, description=_DERIVED_COUNT + " " + _PROVIDER_COUNTS
    )
    derived_relationship_occurrence_count: int = Field(
        ge=0,
        le=IJSON_MAX,
        description=(
            _DERIVED_COUNT
            + " Total stored relationship occurrences, not distinct relatedness pairs, "
            "edges of a graph, or Observation envelopes. " + _RELATEDNESS
        ),
    )


class RelatedKeywordsCapture(BaseModel):
    """One admitted Related Keywords Capture document."""

    model_config = ConfigDict(extra="forbid", strict=True)

    attempt_id: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$", description=_GRAIN
    )
    capture_id: str = Field(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")
    provider: Literal["dataforseo"]
    adapter_contract: Literal[
        "dataforseo-labs-google-related-keywords-live-paid-probe-v1"
    ]
    derivation_version_id: Literal[
        "a85abbe1d9780a3a66cc9fe01adc539e8568144a067b0345ec06cec700dc2669"
    ]
    authorized_at: str = Field(description=_TIME)
    request_started_at: str = Field(description=_TIME)
    transport_ended_at: str = Field(description=_TIME)
    request: RelatedKeywordsRequest
    capture_outcome: RelatedKeywordsCaptureOutcome
    result_context: RelatedKeywordsResultContext
    keyword_data: list[RelatedKeywordsKeywordDataFact] = Field(
        description=(
            "Keyword-data semantic Observations, presented seed locus first, then "
            "returned_item, then keyword and identity. Presentation only. " + _LOCUS
        )
    )
    monthly_search_volume: list[RelatedKeywordsMonthlyFact] = Field(
        description=(
            "Monthly Data Period semantic Observations, presented seed locus first, then "
            "returned_item, then keyword, year, month, identity. " + _PERIOD
        )
    )
    relationships: list[RelatedKeywordsRelationship] = Field(
        description=(
            "Provider relatedness Observations, presented by source keyword, target "
            "keyword, identity. " + _RELATEDNESS
        )
    )


class RelatedKeywordsHistoryEnvelope(BaseModel):
    """Closed Related Keywords admitted-history envelope with fully typed Captures."""

    model_config = ConfigDict(extra="forbid", strict=True)

    provider: Literal["dataforseo"] = Field(description=_GRAIN + " " + _EMPTY)
    adapter_contract: Literal[
        "dataforseo-labs-google-related-keywords-live-paid-probe-v1"
    ]
    requested_keyword: str = Field(
        min_length=1,
        description=(
            "Exact requested subject for this history. It is the same value the Recipe "
            "identity axes name requested_seed. It is never a returned keyword, a "
            "relationship target, or core_keyword. " + _EMPTY
        ),
    )
    derivation_version_id: Literal[
        "a85abbe1d9780a3a66cc9fe01adc539e8568144a067b0345ec06cec700dc2669"
    ]
    recipe_resolution: Literal["selected", "pinned"]
    observation_kinds: list[str] = Field(
        min_length=3,
        max_length=3,
        json_schema_extra={
            "minItems": 3,
            "maxItems": 3,
            "prefixItems": [
                {"type": "string", "const": KEYWORD_DATA_KIND},
                {"type": "string", "const": MONTHLY_KIND},
                {"type": "string", "const": RELATIONSHIP_KIND},
            ],
        },
        description=(
            "Exact ordered Recipe v1 Observation kinds: keyword_data, "
            "monthly_search_volume, relationship. They do not change the list grain. "
            + _COUNT
        ),
    )

    @field_validator("observation_kinds")
    @classmethod
    def require_v1_kinds(cls, value: list[str]) -> list[str]:
        if value != list(V1_KINDS):
            raise ValueError("observation_kinds must be the exact Related Keywords v1 list")
        return value

    captures: list[RelatedKeywordsCapture] = Field(
        description=(
            "Whole admitted Capture documents, including observation_admitted_empty. "
            + _ADMITTED_EMPTY
            + " "
            + _EMPTY
        )
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


def _trend_member_field(row: Mapping[str, object], column: str) -> dict[str, object]:
    return {
        "state": _as_state(
            row[f"{column}_state"], f"{column}_state", TREND_MEMBER_STATES
        ),
        "value": _optional_int(row[column], column),
    }


def _require_se_type(value: object, name: str) -> str:
    """Required provider se_type. RK-03 admits only the exact closed value."""

    text = _as_text(value, name)
    if text != SE_TYPE:
        raise IntegrityError(f"{name} is not the closed Recipe v1 se_type")
    return text


def _se_type_field(row: Mapping[str, object], column: str) -> dict[str, object]:
    """Closed provider se_type pair. A stated value is exactly the RK-03 vocabulary."""

    state = _as_state(row[f"{column}_state"], f"{column}_state")
    value = _optional_text(row[column], column)
    if value is not None and value != SE_TYPE:
        raise IntegrityError(f"{column} is not the closed Recipe v1 se_type")
    return {"state": state, "value": value}


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


def _identity(kind: str, axes: Mapping[str, object]) -> str:
    """Recompute a Recipe-v1 within-Capture identity from its persisted axes."""

    return observation_identity(
        {
            "axes": dict(axes),
            "observation_kind": kind,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        RELATED_KEYWORDS_RECIPE,
    )


def _load_validated_v1_recipe(
    connection: Connection[Any], resolved: ResolvedProviderRecipe
) -> ResolvedProviderRecipe:
    """Verify the resolved Recipe really is the accepted Related Keywords v1 document."""

    if resolved.derivation_version_id != RELATED_KEYWORDS_RECIPE_ID:
        raise UnsupportedRelatedKeywordsRecipe(
            "Related Keywords history serves Recipe v1 only"
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
        (RELATED_KEYWORDS_RECIPE_ID,),
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
    if digest != RELATED_KEYWORDS_RECIPE_ID:
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
    if validated["observation_kinds"] != list(V1_KINDS):
        raise IntegrityError("Recipe observation kinds are not Related Keywords v1")
    admission = validated["admission"]
    if not isinstance(admission, Mapping):
        raise IntegrityError("Recipe admission is missing")
    if admission.get("capture_outcomes") != list(V1_CAPTURE_OUTCOMES):
        raise IntegrityError("Recipe classifications are not Related Keywords v1")
    return resolved


def _attempt_request(attempt: Mapping[str, object]) -> dict[str, object]:
    """Project the closed request block from verified Attempt Evidence."""

    parameters = attempt.get("parameters")
    if not isinstance(parameters, Mapping):
        raise IntegrityError("verified Attempt is missing parameters")
    try:
        closed = validate_related_keywords_http_parameters(parameters)
    except DocumentError as exc:
        raise IntegrityError(
            "verified Attempt parameters are not Related Keywords"
        ) from exc
    request: dict[str, object] = {
        "keyword": _as_text(closed.get("keyword"), "keyword"),
        "location_code": _as_int(closed.get("location_code"), "location_code"),
        "language_code": _as_text(closed.get("language_code"), "language_code"),
        "depth": _as_int(closed.get("depth"), "depth"),
        "limit": _as_int(closed.get("limit"), "limit"),
        "offset": _as_int(closed.get("offset"), "offset"),
        "order_by": _as_str_list(closed.get("order_by"), "order_by"),
        "include_seed_keyword": _as_bool(
            closed.get("include_seed_keyword"), "include_seed_keyword"
        ),
        "include_serp_info": _as_bool(
            closed.get("include_serp_info"), "include_serp_info"
        ),
        "include_clickstream_data": _as_bool(
            closed.get("include_clickstream_data"), "include_clickstream_data"
        ),
        "ignore_synonyms": _as_bool(closed.get("ignore_synonyms"), "ignore_synonyms"),
        "replace_with_core_keyword": _as_bool(
            closed.get("replace_with_core_keyword"), "replace_with_core_keyword"
        ),
    }
    if set(request) != _REQUEST_KEYS:
        raise IntegrityError("Attempt request keys are not closed")
    return request


def _rows(
    connection: Connection[Any],
    table: str,
    columns: Sequence[str],
    capture_id: str,
) -> list[dict[str, object]]:
    statement = (
        f"SELECT {', '.join(columns)} FROM {table} "
        "WHERE derivation_version_id = %s AND capture_id = %s"
    )
    fetched = connection.execute(
        statement, (RELATED_KEYWORDS_RECIPE_ID, capture_id)
    ).fetchall()
    return [dict(zip(columns, row, strict=True)) for row in fetched]


def _keyword_info(row: Mapping[str, object]) -> dict[str, object]:
    trend_state = _as_state(
        row["search_volume_trend_state"], "search_volume_trend_state"
    )
    members = {
        column: _trend_member_field(row, column)
        for column in ("trend_monthly", "trend_quarterly", "trend_yearly")
    }
    for column, member in members.items():
        applicable = member["state"] != "inapplicable"
        if applicable != (trend_state == "stated"):
            raise IntegrityError(
                f"{column} state disagrees with search_volume_trend_state"
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
        "search_volume_trend_state": trend_state,
        **members,
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


def _serp_info(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "se_type": _se_type_field(row, "se_type"),
        "check_url": _text_field(row, "check_url"),
        "serp_item_types": _text_array_field(row, "serp_item_types"),
        "se_results_count": _count_field(row, "se_results_count"),
        "serp_last_updated_time": _text_field(row, "serp_last_updated_time"),
        "serp_previous_updated_time": _text_field(row, "serp_previous_updated_time"),
    }


_ChildProjector = Callable[[Mapping[str, object]], dict[str, object]]
_CHILD_PROJECTORS: Final[dict[str, _ChildProjector]] = {
    "keyword_info": _keyword_info,
    "keyword_properties": _keyword_properties,
    "avg_backlinks": _avg_backlinks,
    "search_intent": _search_intent,
    "serp_info": _serp_info,
}


def _envelope_keys(
    connection: Connection[Any], capture_id: str, attempt_id: str
) -> set[tuple[str, str]]:
    rows = connection.execute(
        """
        SELECT within_capture_identity, observation_kind, attempt_id, provider,
               adapter_contract
        FROM observation_envelopes
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (RELATED_KEYWORDS_RECIPE_ID, capture_id),
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


def _capture_families(
    connection: Connection[Any],
    *,
    capture_id: str,
    attempt_id: str,
    seed: str,
    classification: str,
    observation_count: int,
    seed_state: str,
    items_count: int,
    derived_items: int,
    derived_relationship_occurrences: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    """Rebuild and check the complete PostgreSQL state behind one admitted Capture."""

    envelope_keys = _envelope_keys(connection, capture_id, attempt_id)
    if len(envelope_keys) != observation_count:
        raise IntegrityError("envelope cardinality disagrees with observation_count")

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

    item_by_identity: dict[str, list[dict[str, object]]] = {}
    item_by_index: dict[int, tuple[str, int, str]] = {}
    for row in _rows(
        connection, ITEM_OCCURRENCES_TABLE, ITEM_OCCURRENCE_COLUMNS, capture_id
    ):
        identity = _as_text(row["within_capture_identity"], "within_capture_identity")
        if _as_text(row["observation_kind"], "observation_kind") != KEYWORD_DATA_KIND:
            raise IntegrityError("item occurrence has the wrong Observation kind")
        index = _as_int(row["item_index"], "item_index")
        depth = _as_int(row["depth"], "depth")
        edge_state = _as_state(row["related_keywords_state"], "related_keywords_state")
        if index in item_by_index:
            raise IntegrityError("duplicate returned-item occurrence index")
        item_by_index[index] = (identity, depth, edge_state)
        item_by_identity.setdefault(identity, []).append(
            {
                "item_index": index,
                "depth": depth,
                "item_se_type": _require_se_type(row["item_se_type"], "item_se_type"),
                "related_keywords_state": edge_state,
            }
        )
    returned_items = len(item_by_index)
    if set(item_by_index) != set(range(returned_items)):
        raise IntegrityError("returned-item occurrence indexes are not globally dense")
    if returned_items != items_count or returned_items != derived_items:
        raise IntegrityError("returned-item count disagrees with persisted counts")

    keyword_data: list[dict[str, object]] = []
    keyword_data_keys: set[tuple[str, str]] = set()
    # (locus, keyword) -> (keyword_info state, persisted monthly_searches state or None).
    # Monthly facts are only admissible under a stated keyword_info whose monthly_searches
    # array is itself stated, so the monthly family is bound to this index below.
    keyword_data_index: dict[tuple[str, str], tuple[str, str | None]] = {}
    identity_keyword: dict[str, str] = {}
    seed_parents = 0
    for row in _rows(connection, KEYWORD_DATA_TABLE, KEYWORD_DATA_COLUMNS, capture_id):
        identity = _as_text(row["within_capture_identity"], "within_capture_identity")
        if _as_text(row["observation_kind"], "observation_kind") != KEYWORD_DATA_KIND:
            raise IntegrityError("keyword-data row has the wrong Observation kind")
        if _as_text(row["requested_seed"], "requested_seed") != seed:
            raise IntegrityError("keyword-data requested_seed disagrees with the Attempt")
        locus = _as_text(row["locus"], "locus")
        if locus not in LOCUS_RANK:
            raise IntegrityError("keyword-data locus is not a Recipe v1 locus")
        keyword = _as_text(row["keyword"], "keyword")
        recomputed = _identity(
            KEYWORD_DATA_KIND,
            {"keyword": keyword, "locus": locus, "requested_seed": seed},
        )
        if recomputed != identity:
            raise IntegrityError("keyword-data identity axes do not recompute")
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
        if (locus, keyword) in keyword_data_index:
            raise IntegrityError("duplicate keyword-data locus and keyword")
        keyword_data_index[(locus, keyword)] = (info_state, monthly_state)
        identity_keyword[identity] = keyword
        if locus == LOCUS_SEED:
            seed_parents += 1
        occurrences = sorted(
            item_by_identity.pop(identity, []),
            key=lambda item: _as_int(item["item_index"], "item_index"),
        )
        if locus == LOCUS_SEED and occurrences:
            raise IntegrityError("seed locus must have no returned-item occurrence")
        if locus == LOCUS_ITEM and not occurrences:
            raise IntegrityError("returned-item locus must have an item occurrence")
        keyword_data.append(
            {
                "observation_kind": KEYWORD_DATA_KIND,
                "within_capture_identity": identity,
                "requested_seed": seed,
                "locus": locus,
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
                "occurrences": occurrences,
            }
        )
        keyword_data_keys.add((identity, KEYWORD_DATA_KIND))
    if len(keyword_data_keys) != len(keyword_data):
        raise IntegrityError("duplicate keyword-data semantic identity")
    for name, indexed in child_rows.items():
        if indexed:
            raise IntegrityError(f"orphan {name} child row")
    if item_by_identity:
        raise IntegrityError("orphan returned-item occurrence")
    if seed_state == "stated":
        if seed_parents != 1:
            raise IntegrityError(
                "a stated seed_keyword_data requires exactly one seed-locus fact"
            )
    elif seed_parents:
        raise IntegrityError(
            "a non-stated seed_keyword_data requires no seed-locus fact"
        )
    # Which returned keyword each item position actually carries. Occurrence membership
    # alone is not enough: a monthly point or a relatedness edge must cite an item that
    # carries its own semantic keyword, not merely some existing item.
    keyword_by_index: dict[int, str] = {}
    for index, (occurrence_identity, _depth, _edge_state) in item_by_index.items():
        occurrence_keyword = identity_keyword.get(occurrence_identity)
        if occurrence_keyword is None:
            raise IntegrityError("returned-item occurrence has no keyword-data fact")
        keyword_by_index[index] = occurrence_keyword

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
        if _as_text(row["requested_seed"], "requested_seed") != seed:
            raise IntegrityError("monthly requested_seed disagrees with the Attempt")
        locus = _as_text(row["locus"], "locus")
        if locus not in LOCUS_RANK:
            raise IntegrityError("monthly locus is not a Recipe v1 locus")
        keyword = _as_text(row["keyword"], "keyword")
        year = _as_int(row["year"], "year")
        month = _as_int(row["month"], "month")
        recomputed = _identity(
            MONTHLY_KIND,
            {
                "keyword": keyword,
                "locus": locus,
                "month": month,
                "requested_seed": seed,
                "year": year,
            },
        )
        if recomputed != identity:
            raise IntegrityError("monthly identity axes do not recompute")
        parent = keyword_data_index.get((locus, keyword))
        if parent is None:
            raise IntegrityError("monthly fact has no matching keyword-data fact")
        if parent[0] != "stated":
            raise IntegrityError("monthly fact under a non-stated keyword_info")
        if parent[1] != "stated":
            raise IntegrityError("monthly fact under a non-stated monthly_searches")
        indexes = sorted(monthly_occurrences.pop(identity, []))
        if locus == LOCUS_SEED and indexes:
            raise IntegrityError("seed-locus monthly fact must have no occurrence")
        if locus == LOCUS_ITEM and not indexes:
            raise IntegrityError("returned-item monthly fact must have an occurrence")
        for index in indexes:
            if keyword_by_index[index] != keyword:
                raise IntegrityError(
                    "monthly occurrence cites a different returned keyword"
                )
        monthly.append(
            {
                "observation_kind": MONTHLY_KIND,
                "within_capture_identity": identity,
                "requested_seed": seed,
                "locus": locus,
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

    relationship_occurrences: dict[str, list[dict[str, object]]] = {}
    targets_by_source: dict[int, list[int]] = {}
    occurrence_total = 0
    for row in _rows(
        connection,
        RELATIONSHIP_OCCURRENCES_TABLE,
        RELATIONSHIP_OCCURRENCE_COLUMNS,
        capture_id,
    ):
        identity = _as_text(row["within_capture_identity"], "within_capture_identity")
        if _as_text(row["observation_kind"], "observation_kind") != RELATIONSHIP_KIND:
            raise IntegrityError("relationship occurrence has the wrong Observation kind")
        source_index = _as_int(row["source_item_index"], "source_item_index")
        target_index = _as_int(row["target_index"], "target_index")
        source_depth = _as_int(row["source_depth"], "source_depth")
        anchor = item_by_index.get(source_index)
        if anchor is None:
            raise IntegrityError("relationship occurrence has no source item occurrence")
        if source_depth != anchor[1]:
            raise IntegrityError("relationship source_depth disagrees with item depth")
        occurrence_total += 1
        targets_by_source.setdefault(source_index, []).append(target_index)
        relationship_occurrences.setdefault(identity, []).append(
            {
                "source_item_index": source_index,
                "source_depth": source_depth,
                "target_index": target_index,
            }
        )
    if occurrence_total != derived_relationship_occurrences:
        raise IntegrityError("relationship occurrence count disagrees with the context")
    for index, (_identity_text, _depth, edge_state) in item_by_index.items():
        targets = targets_by_source.get(index, [])
        if edge_state != "stated" and targets:
            raise IntegrityError("non-stated related_keywords has edge occurrences")
        if len(set(targets)) != len(targets):
            raise IntegrityError("duplicate relationship target index for one source item")
        if set(targets) != set(range(len(targets))):
            raise IntegrityError("relationship target indexes are not dense per source item")

    relationships: list[dict[str, object]] = []
    relationship_keys: set[tuple[str, str]] = set()
    for row in _rows(connection, RELATIONSHIP_TABLE, RELATIONSHIP_COLUMNS, capture_id):
        identity = _as_text(row["within_capture_identity"], "within_capture_identity")
        if _as_text(row["observation_kind"], "observation_kind") != RELATIONSHIP_KIND:
            raise IntegrityError("relationship row has the wrong Observation kind")
        if _as_text(row["requested_seed"], "requested_seed") != seed:
            raise IntegrityError("relationship requested_seed disagrees with the Attempt")
        source_keyword = _as_text(row["source_keyword"], "source_keyword")
        target_keyword = _as_text(row["target_keyword"], "target_keyword")
        recomputed = _identity(
            RELATIONSHIP_KIND,
            {
                "requested_seed": seed,
                "source_keyword": source_keyword,
                "target_keyword": target_keyword,
            },
        )
        if recomputed != identity:
            raise IntegrityError("relationship identity axes do not recompute")
        occurrences = relationship_occurrences.pop(identity, [])
        if not occurrences:
            raise IntegrityError("relationship parent has no occurrence")
        for occurrence in occurrences:
            source_index = _as_int(
                occurrence["source_item_index"], "source_item_index"
            )
            if keyword_by_index[source_index] != source_keyword:
                raise IntegrityError(
                    "relationship occurrence cites a different returned source keyword"
                )
        occurrences.sort(
            key=lambda item: (
                _as_int(item["source_item_index"], "source_item_index"),
                _as_int(item["target_index"], "target_index"),
            )
        )
        relationships.append(
            {
                "observation_kind": RELATIONSHIP_KIND,
                "within_capture_identity": identity,
                "requested_seed": seed,
                "source_keyword": source_keyword,
                "target_keyword": target_keyword,
                "occurrences": occurrences,
            }
        )
        relationship_keys.add((identity, RELATIONSHIP_KIND))
    if len(relationship_keys) != len(relationships):
        raise IntegrityError("duplicate relationship semantic identity")
    if relationship_occurrences:
        raise IntegrityError("orphan relationship occurrence")

    semantic_keys = keyword_data_keys | monthly_keys | relationship_keys
    total_semantic = len(keyword_data) + len(monthly) + len(relationships)
    if len(semantic_keys) != total_semantic or semantic_keys != envelope_keys:
        raise IntegrityError("semantic parents disagree with the Observation envelopes")

    if classification == "observation_admitted_empty":
        if observation_count != 0 or total_semantic != 0:
            raise IntegrityError("observation_admitted_empty must carry no semantic fact")
        if returned_items != 0 or occurrence_total != 0:
            raise IntegrityError("observation_admitted_empty must carry no occurrence")
    elif observation_count < 1 or total_semantic < 1:
        raise IntegrityError("observation_admitted requires positive semantic testimony")

    keyword_data.sort(
        key=lambda fact: (
            LOCUS_RANK[str(fact["locus"])],
            str(fact["keyword"]),
            str(fact["within_capture_identity"]),
        )
    )
    monthly.sort(
        key=lambda fact: (
            LOCUS_RANK[str(fact["locus"])],
            str(fact["keyword"]),
            _as_int(_period(fact)["year"], "year"),
            _as_int(_period(fact)["month"], "month"),
            str(fact["within_capture_identity"]),
        )
    )
    relationships.sort(
        key=lambda fact: (
            str(fact["source_keyword"]),
            str(fact["target_keyword"]),
            str(fact["within_capture_identity"]),
        )
    )
    return keyword_data, monthly, relationships


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
    """A matching context must carry exactly one Outcome, for exactly its own Attempt."""

    rows = connection.execute(
        """
        SELECT attempt_id, classification, observation_count
        FROM outcomes
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (RELATED_KEYWORDS_RECIPE_ID, capture_id),
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
        ("keyword", "requested_seed"),
        ("location_code", "request_location_code"),
        ("language_code", "request_language_code"),
        ("depth", "request_depth"),
        ("limit", "request_limit"),
        ("offset", "request_offset"),
        ("order_by", "request_order_by"),
        ("include_seed_keyword", "request_include_seed_keyword"),
        ("include_serp_info", "request_include_serp_info"),
        ("include_clickstream_data", "request_include_clickstream_data"),
        ("ignore_synonyms", "request_ignore_synonyms"),
        ("replace_with_core_keyword", "request_replace_with_core_keyword"),
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
        "seed_keyword": _as_any_text(
            context["result_seed_keyword"], "result_seed_keyword"
        ),
        "location_code": _count_field(context, "result_location_code"),
        "language_code": _text_field(context, "result_language_code"),
        "se_type": _se_type_field(context, "result_se_type"),
        "total_count": _as_int(context["total_count"], "total_count"),
        "items_count": _as_int(context["items_count"], "items_count"),
        "seed_keyword_data_state": _as_state(
            context["seed_keyword_data_state"], "seed_keyword_data_state"
        ),
        "derived_returned_item_count": _as_int(
            context["derived_returned_item_count"], "derived_returned_item_count"
        ),
        "derived_relationship_occurrence_count": _as_int(
            context["derived_relationship_occurrence_count"],
            "derived_relationship_occurrence_count",
        ),
    }
    if set(payload) != _RESULT_CONTEXT_KEYS:
        raise IntegrityError("result_context keys are not closed")
    return payload


def _require_text_field(document: Mapping[str, object], key: str) -> str:
    return _as_text(document.get(key), key)


def _verify_capture(
    store: EvidenceStore,
    connection: Connection[Any],
    candidate: Mapping[str, object],
    requested_keyword: str,
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
    if _as_text(candidate["requested_seed"], "requested_seed") != requested_keyword:
        raise IntegrityError("result context seed disagrees with the requested subject")
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
        raise IntegrityError("derived Evidence is not Related Keywords")
    request = _attempt_request(attempt)
    if request["keyword"] != requested_keyword:
        raise IntegrityError("Attempt keyword disagrees with the history subject")
    _require_request_agreement(request, candidate)
    keyword_data, monthly, relationships = _capture_families(
        connection,
        capture_id=capture_id,
        attempt_id=attempt_id,
        seed=requested_keyword,
        classification=token,
        observation_count=observation_count,
        seed_state=_as_state(
            candidate["seed_keyword_data_state"], "seed_keyword_data_state"
        ),
        items_count=_as_int(candidate["items_count"], "items_count"),
        derived_items=_as_int(
            candidate["derived_returned_item_count"], "derived_returned_item_count"
        ),
        derived_relationship_occurrences=_as_int(
            candidate["derived_relationship_occurrence_count"],
            "derived_relationship_occurrence_count",
        ),
    )
    payload: dict[str, object] = {
        "attempt_id": attempt_id,
        "capture_id": capture_id,
        "provider": HISTORY_PROVIDER,
        "adapter_contract": HISTORY_ADAPTER,
        "derivation_version_id": RELATED_KEYWORDS_RECIPE_ID,
        "authorized_at": _require_text_field(attempt, "authorized_at"),
        "request_started_at": _require_text_field(capture, "request_started_at"),
        "transport_ended_at": _require_text_field(capture, "transport_ended_at"),
        "request": request,
        "capture_outcome": {
            "classification": token,
            "observation_count": observation_count,
        },
        "result_context": _result_context(candidate),
        "keyword_data": keyword_data,
        "monthly_search_volume": monthly,
        "relationships": relationships,
    }
    if set(payload) != _CAPTURE_KEYS:
        raise IntegrityError("Capture keys are not closed")
    return payload


def load_related_keywords_history(
    store: EvidenceStore,
    connection: Connection[Any],
    *,
    requested_keyword: str,
    pinned_version: str | None,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble surface-explicit Related Keywords history for one exact requested seed."""

    resolved = resolve_provider_recipe(connection, HISTORY_ADAPTER, pinned_version)
    recipe = _load_validated_v1_recipe(connection, resolved)
    rows = connection.execute(
        CANDIDATE_SQL, (requested_keyword, RELATED_KEYWORDS_RECIPE_ID)
    ).fetchall()
    verified: list[tuple[str, str, dict[str, object]]] = []
    seen: set[str] = set()
    for row in rows:
        candidate = dict(zip(CANDIDATE_ROW_KEYS, row, strict=True))
        capture_id = _as_text(candidate["capture_id"], "capture_id")
        if capture_id in seen:
            raise IntegrityError("duplicate admitted Capture candidate")
        seen.add(capture_id)
        payload = _verify_capture(store, connection, candidate, requested_keyword)
        verified.append((str(payload["request_started_at"]), capture_id, payload))
    verified.sort(key=lambda item: (item[0], item[1]), reverse=order == "desc")
    selected = [item[2] for item in verified[:limit]]
    envelope = history_list_response(
        provider=HISTORY_PROVIDER,
        adapter_contract=HISTORY_ADAPTER,
        requested_keyword=requested_keyword,
        derivation_version_id=recipe.derivation_version_id,
        recipe_resolution=recipe.resolution,
        observation_kinds=list(V1_KINDS),
        captures=selected,
        total_matching=len(verified),
        limit=limit,
        order=order,
    )
    try:
        return RelatedKeywordsHistoryEnvelope.model_validate(envelope).model_dump()
    except ValidationError as exc:
        raise IntegrityError("malformed Related Keywords history projection") from exc
