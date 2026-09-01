"""Derive DataForSEO Google Ranked Keywords Outcomes and Observations from Evidence.

RANK-05 turns one verified Ranked Keywords Capture into four semantic Observation kinds —
target corpus metrics, returned rank placements, Ranked-local keyword enrichment, and
monthly Data-Period search volume — plus subordinate provider occurrence and result-context
testimony.

Four boundaries are load-bearing and deliberately not simplified:

1. the returned 100-row prefix is not the provider's 248-row corpus, and no persisted column
   claims completeness;
2. `metrics` and `metrics_absolute` are two independently stated rank systems that are never
   reconciled with each other, with `total_count`, with `items_count`, or with returned rows;
3. embedded Ranked keyword enrichment is Ranked-local testimony, never Keyword Overview or
   Related Keywords semantic identity;
4. exact URLs, hosts, and domains stay provider strings — there is no canonical Page
   identity, no URL normalization, and no apex/`www` collapse.

Time stays four-pillar. Capture/acquisition time is Evidence provenance and never reaches a
provider clock or a Data Period; monthly `(year, month)` is a Data Period; the Ranked-element
and keyword-`serp_info` SERP clocks stay source-local even where the fixture makes them
agree; and each enrichment clock belongs only to the structure that stated it. No relation
here exposes a universal `last_updated` or `provider_update_time`.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from decimal import Decimal
from pathlib import Path
from typing import Any, Final

from psycopg import Connection, sql

from observatory.capture_event import (
    RANKED_KEYWORDS_ADAPTER_CONTRACT,
    DocumentError,
    validate_ranked_keywords_http_parameters,
)
from observatory.dataforseo_google_ranked_keywords import (
    CORPUS_METRICS_KIND,
    KEYWORD_DATA_KIND,
    MONTHLY_KIND,
    PARSER_CONTRACT,
    PROVIDER,
    RANK_SYSTEM_GROUP,
    RANK_SYSTEMS,
    RANKED_RESULT_KIND,
    REQUESTED_ITEM_TYPES,
    KeywordData,
    MetricsAbsoluteFamily,
    MetricsFamily,
    PositionBuckets,
    RankedKeywordsIR,
    RankedKeywordsParseError,
    RankedSerpElement,
    parse_ranked_keywords,
)
from observatory.dataforseo_keyword_overview import Field, FieldState, ParseClassification
from observatory.derive import DerivationError
from observatory.evidence_store import EvidenceStore, IntegrityError, open_store
from observatory.migrate import apply_schema, connect, resolve_database_url
from observatory.provider_recipe import (
    IDENTITY_SCHEMA,
    IDENTITY_VERSION,
    SCHEMA,
    SCHEMA_VERSION,
    DerivationDiagnostic,
    ObservationEnvelope,
    observation_identity,
    recipe_bytes,
    recipe_derivation_version_id,
    register_provider_recipe,
    validate_recipe,
    write_derivation_diagnostic,
    write_observation_envelope,
)

ATTEMPT_CLASSIFICATION: Final[str] = "authorized_unresolved"
IJSON_MAX: Final[int] = 9007199254740991

CORPUS_METRICS_TABLE: Final[str] = "ranked_keywords_corpus_metrics"
RANKED_RESULTS_TABLE: Final[str] = "ranked_keywords_ranked_results"
KEYWORD_DATA_TABLE: Final[str] = "ranked_keywords_keyword_data"
KEYWORD_INFO_TABLE: Final[str] = "ranked_keywords_keyword_info"
PROPERTIES_TABLE: Final[str] = "ranked_keywords_keyword_properties"
BACKLINKS_TABLE: Final[str] = "ranked_keywords_avg_backlinks"
INTENT_TABLE: Final[str] = "ranked_keywords_search_intent"
KEYWORD_SERP_TABLE: Final[str] = "ranked_keywords_keyword_serp_info"
MONTHLY_TABLE: Final[str] = "ranked_keywords_monthly_search_volume"
ITEM_OCCURRENCES_TABLE: Final[str] = "ranked_keywords_item_occurrences"
MONTHLY_OCCURRENCES_TABLE: Final[str] = "ranked_keywords_monthly_item_occurrences"
CONTEXT_TABLE: Final[str] = "ranked_keywords_result_context"

RANK05_TABLES: Final[tuple[str, ...]] = (
    CORPUS_METRICS_TABLE,
    RANKED_RESULTS_TABLE,
    KEYWORD_DATA_TABLE,
    KEYWORD_INFO_TABLE,
    PROPERTIES_TABLE,
    BACKLINKS_TABLE,
    INTENT_TABLE,
    KEYWORD_SERP_TABLE,
    MONTHLY_TABLE,
    ITEM_OCCURRENCES_TABLE,
    MONTHLY_OCCURRENCES_TABLE,
    CONTEXT_TABLE,
)

# Relations 1, 2, 3 and 9 are kind-bound semantic parents carrying a generic Observation
# envelope. The five keyword child relations exist only when their enclosing provider object
# is STATED and hang off the exact keyword-data parent, never off an arbitrary envelope.
_KEYWORD_CHILD_TABLES: Final[tuple[str, ...]] = (
    KEYWORD_INFO_TABLE,
    PROPERTIES_TABLE,
    BACKLINKS_TABLE,
    INTENT_TABLE,
    KEYWORD_SERP_TABLE,
)
_DETAIL_TABLES: Final[tuple[str, ...]] = (
    CORPUS_METRICS_TABLE,
    RANKED_RESULTS_TABLE,
    KEYWORD_DATA_TABLE,
    *_KEYWORD_CHILD_TABLES,
    MONTHLY_TABLE,
)

_BUCKET_COLUMNS: Final[tuple[str, ...]] = (
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
_MOVEMENT_COLUMNS: Final[tuple[str, ...]] = ("is_new", "is_up", "is_down", "is_lost")
_CLICKSTREAM_AGGREGATE_STATES: Final[tuple[str, ...]] = (
    "clickstream_etv_state",
    "clickstream_gender_distribution_state",
    "clickstream_age_distribution_state",
)

_CORPUS_METRICS_CONTENT: Final[tuple[str, ...]] = (
    "requested_target",
    "aggregate_family",
    "rank_system",
    *_BUCKET_COLUMNS,
    *_MOVEMENT_COLUMNS,
    "count",
    "count_state",
    "etv",
    "etv_state",
    "estimated_paid_traffic_cost",
    "estimated_paid_traffic_cost_state",
    *_CLICKSTREAM_AGGREGATE_STATES,
)

# Ranked-element members keep source-local `ranked_element_*` names so they stay
# distinguishable from the overlapping keyword-`serp_info` child columns. The two loci agree
# in the frozen fixture; that agreement is testimony and is never reconciled.
_RANKED_ELEMENT_COLUMNS: Final[tuple[str, ...]] = (
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
# [CHAZ] Product Option 1: `breadcrumb`, `pre_snippet`, and `highlighted` contribute their
# Field state only. Their text stays Evidence-only under Recipe v1 so parser retention is
# never mistaken for semantic promotion or redistribution permission. `xpath` is layout
# testimony rather than prose and keeps a typed value.
_PROSE_STATE_ONLY_COLUMNS: Final[tuple[str, ...]] = (
    "breadcrumb_state",
    "pre_snippet_state",
    "highlighted_state",
)
# Parser-v1 null-only unsupported SERP children. State only: no value column, no invented
# Organic-compatible child schema. A populated value cannot reach Recipe v1 because RANK-04
# rejects it as an unsupported shape.
_UNSUPPORTED_CHILD_COLUMNS: Final[tuple[str, ...]] = (
    "about_this_result_state",
    "backlinks_info_state",
    "extended_snippet_state",
    "links_state",
    "rating_state",
)
_SERP_ITEM_COLUMNS: Final[tuple[str, ...]] = (
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
    *_PROSE_STATE_ONLY_COLUMNS,
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
    *_UNSUPPORTED_CHILD_COLUMNS,
)
_RANKED_RESULT_IDENTITY_COLUMNS: Final[tuple[str, ...]] = (
    "requested_target",
    "keyword",
    "serp_item_type",
    "rank_group",
    "rank_absolute",
)
_RANKED_RESULT_CONTENT: Final[tuple[str, ...]] = (
    *_RANKED_RESULT_IDENTITY_COLUMNS,
    *_RANKED_ELEMENT_COLUMNS,
    *_SERP_ITEM_COLUMNS,
)

_KEYWORD_DATA_CONTENT: Final[tuple[str, ...]] = (
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
_KEYWORD_INFO_CONTENT: Final[tuple[str, ...]] = (
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
_PROPERTIES_CONTENT: Final[tuple[str, ...]] = (
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
_BACKLINKS_CONTENT: Final[tuple[str, ...]] = (
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
_INTENT_CONTENT: Final[tuple[str, ...]] = (
    "se_type",
    "se_type_state",
    "main_intent",
    "main_intent_state",
    "foreign_intent",
    "foreign_intent_state",
    "search_intent_last_updated_time",
    "search_intent_last_updated_time_state",
)
_KEYWORD_SERP_CONTENT: Final[tuple[str, ...]] = (
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
_MONTHLY_CONTENT: Final[tuple[str, ...]] = (
    "requested_target",
    "keyword",
    "year",
    "month",
    "search_volume",
)
_DETAIL_CONTENT: Final[dict[str, tuple[str, ...]]] = {
    CORPUS_METRICS_TABLE: _CORPUS_METRICS_CONTENT,
    RANKED_RESULTS_TABLE: _RANKED_RESULT_CONTENT,
    KEYWORD_DATA_TABLE: _KEYWORD_DATA_CONTENT,
    KEYWORD_INFO_TABLE: _KEYWORD_INFO_CONTENT,
    PROPERTIES_TABLE: _PROPERTIES_CONTENT,
    BACKLINKS_TABLE: _BACKLINKS_CONTENT,
    INTENT_TABLE: _INTENT_CONTENT,
    KEYWORD_SERP_TABLE: _KEYWORD_SERP_CONTENT,
    MONTHLY_TABLE: _MONTHLY_CONTENT,
}

# One provider returned item connects two independent semantic testimonies. Binding both
# parents on the occurrence row is exactly how that link survives without the provider array
# index ever becoming part of either semantic identity.
_ITEM_OCCURRENCE_IDENTITY: Final[tuple[str, ...]] = (
    "capture_id",
    "derivation_version_id",
    "item_index",
)
_ITEM_OCCURRENCE_CONTENT: Final[tuple[str, ...]] = (
    "ranked_result_identity",
    "ranked_result_kind",
    "keyword_data_identity",
    "keyword_data_kind",
    "item_se_type",
)
_MONTHLY_OCCURRENCE_IDENTITY: Final[tuple[str, ...]] = (
    "capture_id",
    "derivation_version_id",
    "within_capture_identity",
    "observation_kind",
    "item_index",
)
_CONTEXT_CONTENT: Final[tuple[str, ...]] = (
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


def ranked_keywords_recipe() -> dict[str, object]:
    """Return the first Ranked Keywords Derivation Recipe document.

    Recipe v1 fixes exactly four Observation kinds. `rank_system` is a corpus-metrics
    identity axis because `metrics` and `metrics_absolute` are two independently stated
    provider answers about the same target and family, not two shapes of one fact.

    `ranked_result.v1` uses placement identity: target + keyword + open SERP item type +
    both rank axes. Exact URL is content, so two legitimate same-keyword/same-URL rows at
    different ranks stay two placement facts instead of a false conflict, while a differing
    URL under identical placement axes is a real same-identity contradiction.

    Admission declares exactly six Capture-stage classes. `reconciliation_failed` has no
    reachable path — there is one requested target and one result, and result/echo
    disagreement is typed testimony — and `observation_admitted_empty` has none either,
    because every parser-success carries the required aggregate objects and therefore emits
    ten corpus-metric Observations.
    """

    kinds = [
        {
            "axes": {
                "aggregate_family": "string",
                "rank_system": "string",
                "requested_target": "string",
            },
            "observation_kind": CORPUS_METRICS_KIND,
        },
        {
            "axes": {
                "keyword": "string",
                "rank_absolute": "integer",
                "rank_group": "integer",
                "requested_target": "string",
                "serp_item_type": "string",
            },
            "observation_kind": RANKED_RESULT_KIND,
        },
        {
            "axes": {"keyword": "string", "requested_target": "string"},
            "observation_kind": KEYWORD_DATA_KIND,
        },
        {
            "axes": {
                "keyword": "string",
                "month": "integer",
                "requested_target": "string",
                "year": "integer",
            },
            "observation_kind": MONTHLY_KIND,
        },
    ]
    return validate_recipe(
        {
            "adapter_contract": RANKED_KEYWORDS_ADAPTER_CONTRACT,
            "admission": {
                "capture_outcomes": [
                    "no_response",
                    "observation_admitted",
                    "provider_envelope_rejected",
                    "provider_error",
                    "response_partial",
                    "transport_complete_non_admissible",
                ],
                "rule": "recipe_closed_classifications",
            },
            "data_period": {
                "inheritance": "never_from_capture",
                "rule": "provider_stated_year_month_1_9999",
            },
            "extension_policy": {
                "closed_objects": [
                    "/",
                    "/tasks",
                    "/tasks/data",
                    "/tasks/result",
                    "/tasks/result/metrics",
                    "/tasks/result/metrics_absolute",
                    "/tasks/result/items",
                    "/tasks/result/items/keyword_data",
                    "/tasks/result/items/keyword_data/keyword_info",
                    "/tasks/result/items/keyword_data/keyword_info/monthly_searches",
                    (
                        "/tasks/result/items/keyword_data/keyword_info/"
                        "search_volume_trend"
                    ),
                    "/tasks/result/items/keyword_data/keyword_properties",
                    "/tasks/result/items/keyword_data/avg_backlinks_info",
                    "/tasks/result/items/keyword_data/search_intent_info",
                    "/tasks/result/items/keyword_data/serp_info",
                    "/tasks/result/items/ranked_serp_element",
                    "/tasks/result/items/ranked_serp_element/serp_item",
                    "/tasks/result/items/ranked_serp_element/serp_item/rank_changes",
                    "/tasks/result/items/ranked_serp_element/serp_item/rank_info",
                ],
                "extension_permitted_objects": [],
                "unknown_closed_field": "fail_closed",
                "unknown_extension_field": "fail_closed",
            },
            "field_state": {
                "states": [
                    "absent",
                    "inapplicable",
                    "json_null",
                    "not_requested",
                    "stated",
                ]
            },
            "numeric": {"normalization": "exact_decimal"},
            "observation_identity": {
                "document_schema": IDENTITY_SCHEMA,
                "document_version": IDENTITY_VERSION,
                "kinds": kinds,
            },
            "observation_kinds": [
                CORPUS_METRICS_KIND,
                KEYWORD_DATA_KIND,
                MONTHLY_KIND,
                RANKED_RESULT_KIND,
            ],
            "parser_contract": PARSER_CONTRACT,
            "provider": PROVIDER,
            "provider_update_time": {
                "inheritance": "never_from_capture_or_sibling",
                "rule": "structure_local_clocks_no_universal_update_time",
            },
            "reconciliation": {
                "rule": "verified_attempt_authority_result_echo_is_testimony"
            },
            "schema": SCHEMA,
            "version": SCHEMA_VERSION,
        }
    )


RANKED_KEYWORDS_RECIPE: Final[dict[str, object]] = ranked_keywords_recipe()
RANKED_KEYWORDS_RECIPE_BYTES: Final[bytes] = recipe_bytes(RANKED_KEYWORDS_RECIPE)
RANKED_KEYWORDS_RECIPE_ID: Final[str] = recipe_derivation_version_id(
    RANKED_KEYWORDS_RECIPE
)


@dataclass(frozen=True)
class ProviderDeriveSummary:
    derivation_version_id: str
    attempt_outcomes: int
    capture_outcomes: int
    observations: int
    diagnostics: int
    integrity_failures: int


@dataclass(frozen=True)
class PlannedCapture:
    classification: str
    envelopes: tuple[ObservationEnvelope, ...]
    details: Mapping[str, Sequence[Mapping[str, object]]]
    item_occurrences: tuple[dict[str, object], ...]
    monthly_occurrences: tuple[dict[str, object], ...]
    context: dict[str, object] | None
    diagnostics: tuple[DerivationDiagnostic, ...]


class SemanticDisagreement(Exception):
    """Same semantic identity carries conflicting testimony, or content is inadmissible."""


def derive_google_ranked_keywords(
    store: EvidenceStore,
    connection: Connection[Any],
) -> ProviderDeriveSummary:
    """Derive paid Ranked Keywords Evidence under the accepted RANK-05 recipe."""

    if type(store) is not EvidenceStore:
        raise TypeError("Ranked Keywords derive requires the concrete EvidenceStore")
    apply_schema(connection)
    registered = register_provider_recipe(connection, RANKED_KEYWORDS_RECIPE)
    if registered.derivation_version_id != RANKED_KEYWORDS_RECIPE_ID:
        raise DerivationError("recipe identity does not match the accepted digest")
    attempt_written = 0
    integrity_failures = 0
    for attempt_id in store.list_committed_ids("attempts"):
        try:
            attempt = store.read_attempt(attempt_id)
        except IntegrityError:
            integrity_failures += 1
            continue
        if (
            attempt is None
            or attempt.get("adapter_contract") != RANKED_KEYWORDS_ADAPTER_CONTRACT
        ):
            continue
        _write_attempt_outcome(connection, attempt_id)
        attempt_written += 1
    capture_written = 0
    observation_written = 0
    diagnostic_written = 0
    for capture_id in store.list_committed_ids("captures"):
        try:
            capture = store.read_capture(capture_id)
        except IntegrityError:
            integrity_failures += 1
            continue
        if (
            capture is None
            or capture.get("adapter_contract") != RANKED_KEYWORDS_ADAPTER_CONTRACT
        ):
            continue
        # The Capture cites exactly one Attempt. No other Ranked Attempt in the same store
        # may supply parameters for this Capture, however valid that other Attempt is.
        cited = capture.get("attempt_id")
        if not isinstance(cited, str):
            integrity_failures += 1
            continue
        try:
            attempt = store.read_attempt(cited)
        except IntegrityError:
            integrity_failures += 1
            continue
        if (
            attempt is None
            or attempt.get("adapter_contract") != RANKED_KEYWORDS_ADAPTER_CONTRACT
        ):
            integrity_failures += 1
            continue
        parameters = attempt.get("parameters")
        if not isinstance(parameters, Mapping):
            integrity_failures += 1
            continue
        try:
            closed = validate_ranked_keywords_http_parameters(parameters)
        except DocumentError:
            integrity_failures += 1
            continue
        body: bytes | None = None
        if capture.get("transport_state") != "no_response":
            try:
                body = store.read_capture_body(capture_id)
            except IntegrityError:
                integrity_failures += 1
                continue
        planned = plan_ranked_keywords_capture(cited, capture_id, capture, closed, body)
        if planned is None:
            integrity_failures += 1
            continue
        _write_capture_unit(connection, cited, capture_id, planned)
        capture_written += 1
        observation_written += len(planned.envelopes)
        diagnostic_written += len(planned.diagnostics)
    return ProviderDeriveSummary(
        derivation_version_id=RANKED_KEYWORDS_RECIPE_ID,
        attempt_outcomes=attempt_written,
        capture_outcomes=capture_written,
        observations=observation_written,
        diagnostics=diagnostic_written,
        integrity_failures=integrity_failures,
    )


def plan_ranked_keywords_capture(
    attempt_id: str,
    capture_id: str,
    capture: Mapping[str, object],
    parameters: Mapping[str, object],
    body: bytes | None,
) -> PlannedCapture | None:
    """Classify one Capture and plan its rebuildable rows, or None for integrity failure."""

    classification, parsed = _classify_capture(capture, parameters, body)
    if classification == "integrity_failure":
        return None
    if parsed is None or classification != "parser_success":
        return _empty_plan(classification)
    try:
        return _plan_admitted(attempt_id, capture_id, parsed)
    except SemanticDisagreement:
        return _empty_plan("provider_envelope_rejected")


def _empty_plan(classification: str) -> PlannedCapture:
    return PlannedCapture(
        classification=classification,
        envelopes=(),
        details={table: () for table in _DETAIL_TABLES},
        item_occurrences=(),
        monthly_occurrences=(),
        context=None,
        diagnostics=(),
    )


def _classify_capture(
    capture: Mapping[str, object],
    parameters: Mapping[str, object],
    body: bytes | None,
) -> tuple[str, RankedKeywordsIR | None]:
    state = capture.get("transport_state")
    if state == "no_response":
        return "no_response", None
    if state == "response_partial":
        return "response_partial", None
    if state != "response_complete":
        return "transport_complete_non_admissible", None
    response = capture.get("response")
    if not isinstance(response, Mapping) or response.get("completeness") != "complete":
        return "transport_complete_non_admissible", None
    if body is None or len(body) == 0:
        return "transport_complete_non_admissible", None
    try:
        parsed = parse_ranked_keywords(body, parameters)
    except RankedKeywordsParseError as exc:
        # The trusted capture_event validator already accepted these Attempt parameters, so
        # a residual `/attempt` failure is validator divergence or Evidence damage — never a
        # verdict about the provider's body, which has not been read at that point.
        if exc.path == "/attempt" or exc.path.startswith("/attempt/"):
            return "integrity_failure", None
        return "provider_envelope_rejected", None
    if parsed.outcome is ParseClassification.PROVIDER_ERROR:
        return "provider_error", parsed
    return "parser_success", parsed


@dataclass
class _KeywordDataGroup:
    payload: dict[str, dict[str, object]]
    monthly: dict[tuple[int, int], int] = dataclass_field(default_factory=dict)
    monthly_occurrences: dict[tuple[int, int], list[int]] = dataclass_field(
        default_factory=dict
    )


# Exact requested target + keyword + open SERP item type + both rank axes.
_PlacementKey = tuple[str, str, int, int]


def _plan_admitted(
    attempt_id: str, capture_id: str, parsed: RankedKeywordsIR
) -> PlannedCapture:
    result = parsed.result
    if result is None:
        raise SemanticDisagreement
    target = _require_identity_text(parsed.request.target)

    envelopes: list[ObservationEnvelope] = []
    details: dict[str, list[dict[str, object]]] = {table: [] for table in _DETAIL_TABLES}

    # Every Recipe-admitted successful result emits five families under two rank systems,
    # including provider-stated zero families. Zero is a stated aggregate, not absence.
    for family in REQUESTED_ITEM_TYPES:
        group_family: MetricsFamily = getattr(result.metrics, family)
        absolute_family: MetricsAbsoluteFamily = getattr(result.metrics_absolute, family)
        for rank_system in RANK_SYSTEMS:
            if rank_system == RANK_SYSTEM_GROUP:
                payload = _corpus_group_payload(group_family)
            else:
                payload = _corpus_absolute_payload(absolute_family)
            identity = _identity(
                CORPUS_METRICS_KIND,
                {
                    "aggregate_family": family,
                    "rank_system": rank_system,
                    "requested_target": target,
                },
            )
            envelopes.append(
                _envelope(capture_id, attempt_id, CORPUS_METRICS_KIND, identity)
            )
            details[CORPUS_METRICS_TABLE].append(
                _detail_row(
                    capture_id,
                    identity,
                    CORPUS_METRICS_KIND,
                    {
                        "requested_target": target,
                        "aggregate_family": family,
                        "rank_system": rank_system,
                        **payload,
                    },
                )
            )

    placements: dict[_PlacementKey, dict[str, object]] = {}
    keywords: dict[str, _KeywordDataGroup] = {}
    occurrence_rows: list[tuple[_PlacementKey, str, int, str]] = []

    for index, item in enumerate(result.items):
        # RANK-04 already requires both member names, so item-level ABSENT is unreachable.
        # JSON null is reachable and cannot form either accepted identity, so it rejects the
        # whole Capture-stage unit rather than silently dropping one malformed returned row
        # while keeping the corpus metrics.
        if item.keyword_data.state is not FieldState.STATED:
            raise SemanticDisagreement
        if item.ranked_serp_element.state is not FieldState.STATED:
            raise SemanticDisagreement
        data = _require_stated(item.keyword_data)
        element = _require_stated(item.ranked_serp_element)
        serp = element.serp_item
        keyword = _require_identity_text(data.keyword)
        item_type = _require_identity_text(serp.type)
        _require_ijson(serp.rank_group)
        _require_ijson(serp.rank_absolute)
        _require_ijson(index)
        key: _PlacementKey = (keyword, item_type, serp.rank_group, serp.rank_absolute)
        payload = _ranked_result_payload(element)
        existing = placements.get(key)
        if existing is None:
            placements[key] = payload
        elif _comparable(existing) != _comparable(payload):
            # Identical placement axes with a different URL or any other differing semantic
            # detail is a same-placement contradiction, never a first/last-wins choice.
            raise SemanticDisagreement
        _merge_keyword_data(keywords, keyword, data, item_index=index)
        occurrence_rows.append((key, keyword, index, _require_text(item.se_type)))

    placement_identities: dict[_PlacementKey, str] = {}
    for key, payload in placements.items():
        keyword, item_type, rank_group, rank_absolute = key
        identity = _identity(
            RANKED_RESULT_KIND,
            {
                "keyword": keyword,
                "rank_absolute": rank_absolute,
                "rank_group": rank_group,
                "requested_target": target,
                "serp_item_type": item_type,
            },
        )
        placement_identities[key] = identity
        envelopes.append(_envelope(capture_id, attempt_id, RANKED_RESULT_KIND, identity))
        details[RANKED_RESULTS_TABLE].append(
            _detail_row(
                capture_id,
                identity,
                RANKED_RESULT_KIND,
                {
                    "requested_target": target,
                    "keyword": keyword,
                    "serp_item_type": item_type,
                    "rank_group": rank_group,
                    "rank_absolute": rank_absolute,
                    **payload,
                },
            )
        )

    keyword_identities: dict[str, str] = {}
    for keyword, group in keywords.items():
        identity = _identity(
            KEYWORD_DATA_KIND, {"keyword": keyword, "requested_target": target}
        )
        keyword_identities[keyword] = identity
        envelopes.append(_envelope(capture_id, attempt_id, KEYWORD_DATA_KIND, identity))
        parent = dict(group.payload[KEYWORD_DATA_TABLE])
        parent.update({"requested_target": target, "keyword": keyword})
        details[KEYWORD_DATA_TABLE].append(
            _detail_row(capture_id, identity, KEYWORD_DATA_KIND, parent)
        )
        for table in _KEYWORD_CHILD_TABLES:
            child = group.payload.get(table)
            if child is not None:
                details[table].append(
                    _detail_row(capture_id, identity, KEYWORD_DATA_KIND, child)
                )

    monthly_occurrences: list[dict[str, object]] = []
    for keyword, group in keywords.items():
        for (year, month), volume in group.monthly.items():
            identity = _identity(
                MONTHLY_KIND,
                {
                    "keyword": keyword,
                    "month": month,
                    "requested_target": target,
                    "year": year,
                },
            )
            envelopes.append(_envelope(capture_id, attempt_id, MONTHLY_KIND, identity))
            details[MONTHLY_TABLE].append(
                _detail_row(
                    capture_id,
                    identity,
                    MONTHLY_KIND,
                    {
                        "requested_target": target,
                        "keyword": keyword,
                        "year": year,
                        "month": month,
                        "search_volume": volume,
                    },
                )
            )
            for index in sorted(set(group.monthly_occurrences.get((year, month), ()))):
                monthly_occurrences.append(
                    {
                        "capture_id": capture_id,
                        "derivation_version_id": RANKED_KEYWORDS_RECIPE_ID,
                        "within_capture_identity": identity,
                        "observation_kind": MONTHLY_KIND,
                        "item_index": index,
                    }
                )

    item_occurrences: list[dict[str, object]] = []
    for key, keyword, index, item_se_type in occurrence_rows:
        item_occurrences.append(
            {
                "capture_id": capture_id,
                "derivation_version_id": RANKED_KEYWORDS_RECIPE_ID,
                "item_index": index,
                "ranked_result_identity": placement_identities[key],
                "ranked_result_kind": RANKED_RESULT_KIND,
                "keyword_data_identity": keyword_identities[keyword],
                "keyword_data_kind": KEYWORD_DATA_KIND,
                "item_se_type": item_se_type,
            }
        )

    # A successful zero-item result still carries the five required aggregate objects, so it
    # is an ordinary `observation_admitted` with ten corpus-metric Observations. Recipe v1
    # declares no `observation_admitted_empty` because that branch is unreachable.
    return PlannedCapture(
        classification="observation_admitted",
        envelopes=tuple(envelopes),
        details={table: tuple(rows) for table, rows in details.items()},
        item_occurrences=tuple(item_occurrences),
        monthly_occurrences=tuple(monthly_occurrences),
        context=_context_row(attempt_id, capture_id, parsed),
        diagnostics=(),
    )


def _buckets(positions: PositionBuckets) -> dict[str, object]:
    values = {column: getattr(positions, column) for column in _BUCKET_COLUMNS}
    for value in values.values():
        _require_ijson(int(value))
    return dict(values)


def _corpus_group_payload(family: MetricsFamily) -> dict[str, object]:
    """`metrics.<family>` — the rank-group locus, with provider count, ETV, and cost."""

    for value in (family.is_new, family.is_up, family.is_down, family.is_lost):
        _require_ijson(value)
    _require_ijson(family.count)
    etv, etv_state = _decimal_pair(family.etv)
    cost, cost_state = _decimal_pair(family.estimated_paid_traffic_cost)
    return {
        **_buckets(family.positions),
        "is_new": family.is_new,
        "is_up": family.is_up,
        "is_down": family.is_down,
        "is_lost": family.is_lost,
        "count": family.count,
        "count_state": FieldState.STATED.value,
        "etv": etv,
        "etv_state": etv_state,
        "estimated_paid_traffic_cost": cost,
        "estimated_paid_traffic_cost_state": cost_state,
        "clickstream_etv_state": family.clickstream_etv.state.value,
        "clickstream_gender_distribution_state": (
            family.clickstream_gender_distribution.state.value
        ),
        "clickstream_age_distribution_state": (
            family.clickstream_age_distribution.state.value
        ),
    }


def _corpus_absolute_payload(family: MetricsAbsoluteFamily) -> dict[str, object]:
    """`metrics_absolute.<family>` — the absolute-rank locus.

    The provider does not state count, ETV, or estimated paid traffic cost on this locus.
    Recipe-defined `INAPPLICABLE` plus SQL NULL records that structural absence exactly; it
    is not JSON null, and nothing is synthesized from the rank-group sibling.
    """

    for value in (family.is_new, family.is_up, family.is_down, family.is_lost):
        _require_ijson(value)
    inapplicable = FieldState.INAPPLICABLE.value
    return {
        **_buckets(family.positions),
        "is_new": family.is_new,
        "is_up": family.is_up,
        "is_down": family.is_down,
        "is_lost": family.is_lost,
        "count": None,
        "count_state": inapplicable,
        "etv": None,
        "etv_state": inapplicable,
        "estimated_paid_traffic_cost": None,
        "estimated_paid_traffic_cost_state": inapplicable,
        "clickstream_etv_state": family.clickstream_etv.state.value,
        "clickstream_gender_distribution_state": (
            family.clickstream_gender_distribution.state.value
        ),
        "clickstream_age_distribution_state": (
            family.clickstream_age_distribution.state.value
        ),
    }


def _ranked_result_payload(element: RankedSerpElement) -> dict[str, object]:
    """Ranked-element and SERP-item testimony for one admitted placement.

    Both share the admitted placement grain, so they stay on one wide row rather than a
    thirteenth relation. Ranked-element members keep `ranked_element_*` names; the keyword
    `serp_info` child restates six of them on its own path and is never reconciled here.
    """

    serp = element.serp_item
    payload: dict[str, object] = {}
    payload.update(
        _columns("ranked_element_se_type", _text_pair(element.se_type))
        | _columns("ranked_element_check_url", _text_pair(element.check_url))
        | _columns(
            "ranked_element_se_results_count", _int_pair(element.se_results_count)
        )
        | _columns(
            "ranked_element_keyword_difficulty", _int_pair(element.keyword_difficulty)
        )
        | _columns("ranked_element_is_lost", _bool_pair(element.is_lost))
        | _columns(
            "ranked_element_serp_item_types", _text_array_pair(element.serp_item_types)
        )
        | _columns(
            "ranked_element_last_updated_time", _text_pair(element.last_updated_time)
        )
        | _columns(
            "ranked_element_previous_updated_time",
            _text_pair(element.previous_updated_time),
        )
    )
    payload.update(
        _columns("serp_item_se_type", _text_pair(serp.se_type))
        | {"url": _require_text(serp.url)}
        | _columns("position", _text_pair(serp.position))
        | _columns("xpath", _text_pair(serp.xpath))
        | _columns("domain", _text_pair(serp.domain))
        | _columns("main_domain", _text_pair(serp.main_domain))
        | _columns("website_name", _text_pair(serp.website_name))
        | _columns("relative_url", _text_pair(serp.relative_url))
        | _columns("title", _text_pair(serp.title))
        | _columns("description", _text_pair(serp.description))
    )
    # Option 1: state only. The values are deliberately not read here, so hostile prose in a
    # Product-held field cannot reject a unit through a boundary it never crosses.
    payload["breadcrumb_state"] = serp.breadcrumb.state.value
    payload["pre_snippet_state"] = serp.pre_snippet.state.value
    payload["highlighted_state"] = serp.highlighted.state.value
    payload.update(
        _columns("is_image", _bool_pair(serp.is_image))
        | _columns("is_video", _bool_pair(serp.is_video))
        | _columns("is_featured_snippet", _bool_pair(serp.is_featured_snippet))
        | _columns("is_malicious", _bool_pair(serp.is_malicious))
        | _columns("amp_version", _bool_pair(serp.amp_version))
        | _columns("etv", _decimal_pair(serp.etv))
        | _columns(
            "estimated_paid_traffic_cost",
            _decimal_pair(serp.estimated_paid_traffic_cost),
        )
    )
    payload["clickstream_etv_state"] = serp.clickstream_etv.state.value

    payload["rank_changes_state"] = serp.rank_changes.state.value
    if serp.rank_changes.state is FieldState.STATED:
        changes = _require_stated(serp.rank_changes)
        payload.update(
            _columns("rank_changes_is_new", _bool_pair(changes.is_new))
            | _columns("rank_changes_is_up", _bool_pair(changes.is_up))
            | _columns("rank_changes_is_down", _bool_pair(changes.is_down))
            | _columns(
                "rank_changes_previous_rank_absolute",
                _int_pair(changes.previous_rank_absolute),
            )
        )
    else:
        # The enclosing object is not stated, so its members have no state of their own.
        for name in (
            "rank_changes_is_new",
            "rank_changes_is_up",
            "rank_changes_is_down",
            "rank_changes_previous_rank_absolute",
        ):
            payload.update(_columns(name, _inapplicable()))

    payload["rank_info_state"] = serp.rank_info.state.value
    if serp.rank_info.state is FieldState.STATED:
        info = _require_stated(serp.rank_info)
        payload.update(
            _columns("rank_info_page_rank", _int_pair(info.page_rank))
            # Provider page/domain scores for this placement. `main_domain_rank` here is a
            # different provider fact from `avg_backlinks_info.main_domain_rank`.
            | _columns("rank_info_main_domain_rank", _int_pair(info.main_domain_rank))
        )
    else:
        for name in ("rank_info_page_rank", "rank_info_main_domain_rank"):
            payload.update(_columns(name, _inapplicable()))

    payload["about_this_result_state"] = serp.about_this_result.state.value
    payload["backlinks_info_state"] = serp.backlinks_info.state.value
    payload["extended_snippet_state"] = serp.extended_snippet.state.value
    payload["links_state"] = serp.links.state.value
    payload["rating_state"] = serp.rating.state.value
    return payload


def _merge_keyword_data(
    keywords: dict[str, _KeywordDataGroup],
    keyword: str,
    data: KeywordData,
    *,
    item_index: int,
) -> None:
    """Fold one provider occurrence into its semantic keyword-data identity.

    The comparison key is the exact set of rows this occurrence would persist. Monthly
    points are therefore excluded structurally — they live in the separate monthly kind —
    while `monthly_searches_state` stays inside the compared keyword-info row, so a
    STATED-vs-null series disagreement is still a real same-identity conflict.
    """

    payload = _keyword_data_payload(data)
    existing = keywords.get(keyword)
    if existing is None:
        existing = _KeywordDataGroup(payload=payload)
        keywords[keyword] = existing
    elif _comparable(existing.payload) != _comparable(payload):
        raise SemanticDisagreement
    for year, month, volume in _monthly_points(data):
        period = (year, month)
        seen = existing.monthly.get(period)
        if seen is not None and seen != volume:
            raise SemanticDisagreement
        existing.monthly[period] = volume
        existing.monthly_occurrences.setdefault(period, []).append(item_index)


def _monthly_points(data: KeywordData) -> tuple[tuple[int, int, int], ...]:
    if data.keyword_info.state is not FieldState.STATED:
        return ()
    info = _require_stated(data.keyword_info)
    if info.monthly_searches.state is not FieldState.STATED:
        return ()
    points: list[tuple[int, int, int]] = []
    for point in _require_stated(info.monthly_searches):
        _require_ijson(point.search_volume)
        points.append((point.year, point.month, point.search_volume))
    return tuple(points)


def _keyword_data_payload(data: KeywordData) -> dict[str, dict[str, object]]:
    payload: dict[str, dict[str, object]] = {
        KEYWORD_DATA_TABLE: {
            **_columns("location_code", _int_pair(data.location_code)),
            **_columns("language_code", _text_pair(data.language_code)),
            **_columns("se_type", _text_pair(data.se_type)),
            "keyword_info_state": data.keyword_info.state.value,
            "keyword_properties_state": data.keyword_properties.state.value,
            "avg_backlinks_state": data.avg_backlinks_info.state.value,
            "search_intent_state": data.search_intent_info.state.value,
            "keyword_serp_info_state": data.serp_info.state.value,
            # Bing normalization is independent from clickstream: it keeps its own
            # ABSENT/JSON_NULL state semantics under the frozen request flag.
            "bing_normalized_state": (
                data.keyword_info_normalized_with_bing.state.value
            ),
            "clickstream_normalized_state": (
                data.keyword_info_normalized_with_clickstream.state.value
            ),
            "clickstream_keyword_info_state": (
                data.clickstream_keyword_info.state.value
            ),
        }
    }
    if data.keyword_info.state is FieldState.STATED:
        info = _require_stated(data.keyword_info)
        trend_state = info.search_volume_trend.state
        if trend_state is FieldState.STATED:
            trend = _require_stated(info.search_volume_trend)
            monthly_trend = _int_pair(trend.monthly)
            quarterly_trend = _int_pair(trend.quarterly)
            yearly_trend = _int_pair(trend.yearly)
        else:
            monthly_trend = _inapplicable()
            quarterly_trend = _inapplicable()
            yearly_trend = _inapplicable()
        payload[KEYWORD_INFO_TABLE] = {
            **_columns("se_type", _text_pair(info.se_type)),
            **_columns(
                "keyword_info_last_updated_time", _text_pair(info.last_updated_time)
            ),
            **_columns("competition", _decimal_pair(info.competition)),
            **_columns("competition_level", _text_pair(info.competition_level)),
            **_columns("cpc", _decimal_pair(info.cpc)),
            # Current demand is an independent provider fact; it is never derived from, or
            # checked against, the newest monthly point.
            **_columns("search_volume", _int_pair(info.search_volume)),
            **_columns(
                "low_top_of_page_bid", _decimal_pair(info.low_top_of_page_bid)
            ),
            **_columns(
                "high_top_of_page_bid", _decimal_pair(info.high_top_of_page_bid)
            ),
            **_columns("categories", _int_array_pair(info.categories)),
            "monthly_searches_state": info.monthly_searches.state.value,
            "search_volume_trend_state": trend_state.value,
            **_columns("trend_monthly", monthly_trend),
            **_columns("trend_quarterly", quarterly_trend),
            **_columns("trend_yearly", yearly_trend),
        }
    if data.keyword_properties.state is FieldState.STATED:
        properties = _require_stated(data.keyword_properties)
        payload[PROPERTIES_TABLE] = {
            **_columns("se_type", _text_pair(properties.se_type)),
            # Plain provider testimony. No foreign key, no canonical keyword identity.
            **_columns("core_keyword", _text_pair(properties.core_keyword)),
            **_columns(
                "synonym_clustering_algorithm",
                _text_pair(properties.synonym_clustering_algorithm),
            ),
            **_columns(
                "keyword_difficulty", _int_pair(properties.keyword_difficulty)
            ),
            **_columns("detected_language", _text_pair(properties.detected_language)),
            **_columns(
                "is_another_language", _bool_pair(properties.is_another_language)
            ),
        }
    if data.avg_backlinks_info.state is FieldState.STATED:
        backlinks = _require_stated(data.avg_backlinks_info)
        payload[BACKLINKS_TABLE] = {
            **_columns("se_type", _text_pair(backlinks.se_type)),
            **_columns("backlinks", _decimal_pair(backlinks.backlinks)),
            **_columns("dofollow", _decimal_pair(backlinks.dofollow)),
            **_columns("referring_pages", _decimal_pair(backlinks.referring_pages)),
            **_columns("referring_domains", _decimal_pair(backlinks.referring_domains)),
            **_columns(
                "referring_main_domains",
                _decimal_pair(backlinks.referring_main_domains),
            ),
            **_columns("rank", _decimal_pair(backlinks.rank)),
            **_columns("main_domain_rank", _decimal_pair(backlinks.main_domain_rank)),
            **_columns(
                "avg_backlinks_last_updated_time",
                _text_pair(backlinks.last_updated_time),
            ),
        }
    if data.search_intent_info.state is FieldState.STATED:
        intent = _require_stated(data.search_intent_info)
        payload[INTENT_TABLE] = {
            **_columns("se_type", _text_pair(intent.se_type)),
            **_columns("main_intent", _text_pair(intent.main_intent)),
            **_columns("foreign_intent", _text_array_pair(intent.foreign_intent)),
            **_columns(
                "search_intent_last_updated_time",
                _text_pair(intent.last_updated_time),
            ),
        }
    if data.serp_info.state is FieldState.STATED:
        serp = _require_stated(data.serp_info)
        payload[KEYWORD_SERP_TABLE] = {
            **_columns("se_type", _text_pair(serp.se_type)),
            **_columns("check_url", _text_pair(serp.check_url)),
            **_columns("serp_item_types", _text_array_pair(serp.serp_item_types)),
            **_columns("se_results_count", _int_pair(serp.se_results_count)),
            **_columns(
                "keyword_serp_last_updated_time", _text_pair(serp.last_updated_time)
            ),
            **_columns(
                "keyword_serp_previous_updated_time",
                _text_pair(serp.previous_updated_time),
            ),
        }
    return payload


def _context_row(
    attempt_id: str, capture_id: str, parsed: RankedKeywordsIR
) -> dict[str, object]:
    """One typed result-context row per admitted Capture + Recipe.

    Attempt parameters are request authority; provider result restatements are typed
    testimony beside them. `total_count` and `items_count` are independent provider facts.
    The factual combination limit=100, offset=0, items_count=100, total_count=248 is never
    turned into a completeness, truncation, first-page, or coverage claim.
    """

    result = parsed.result
    if result is None:
        raise SemanticDisagreement
    request = parsed.request
    for value in (
        request.location_code,
        request.limit,
        request.offset,
        result.total_count,
        result.items_count,
    ):
        _require_ijson(value)
    return {
        "capture_id": capture_id,
        "derivation_version_id": RANKED_KEYWORDS_RECIPE_ID,
        "attempt_id": attempt_id,
        "requested_target": _require_identity_text(request.target),
        "request_location_code": request.location_code,
        "request_language_code": _require_text(request.language_code),
        "request_item_types": [_require_text(item) for item in request.item_types],
        "request_ignore_synonyms": request.ignore_synonyms,
        "request_include_clickstream_data": request.include_clickstream_data,
        "request_limit": request.limit,
        "request_offset": request.offset,
        "request_load_rank_absolute": request.load_rank_absolute,
        "request_historical_serp_mode": _require_text(request.historical_serp_mode),
        "request_order_by": [_require_text(item) for item in request.order_by],
        **_columns("result_target", _text_pair(result.target)),
        **_columns("result_location_code", _int_pair(result.location_code)),
        **_columns("result_language_code", _text_pair(result.language_code)),
        **_columns("result_se_type", _text_pair(result.se_type)),
        "total_count": result.total_count,
        "items_count": result.items_count,
    }


def _detail_row(
    capture_id: str, identity: str, kind: str, content: Mapping[str, object]
) -> dict[str, object]:
    return {
        "capture_id": capture_id,
        "derivation_version_id": RANKED_KEYWORDS_RECIPE_ID,
        "within_capture_identity": identity,
        "observation_kind": kind,
        **dict(content),
    }


def _comparable(value: object) -> object:
    if isinstance(value, dict):
        return tuple(sorted((key, _comparable(item)) for key, item in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_comparable(item) for item in value)
    return value


def _require_stated[T](field: Field[T]) -> T:
    """Return the value of a field the caller has already proven STATED."""

    value = field.value
    if field.state is not FieldState.STATED or value is None:
        raise SemanticDisagreement
    return value


def _require_text(value: str) -> str:
    """Reject provider text that JCS or PostgreSQL TEXT cannot carry.

    The RANK-02 adapter constrains only the target. Returned keywords, SERP item types,
    URLs, hosts, and every other persisted string are unrequested provider text, so this is
    the boundary that keeps a hostile string a clean `provider_envelope_rejected` instead of
    an escaping JCS or psycopg exception reaching classification behaviour.

    Two distinct boundaries are enforced in one pass:

    - PostgreSQL `TEXT` cannot store U+0000. Canonical JSON accepts it, so this is the wider
      of the two rules for that one code point.
    - Observatory's accepted canonical-I-JSON boundary in `capture_event` rejects surrogates
      and Unicode noncharacters (U+FDD0..U+FDEF and any code point whose low 16 bits are
      0xFFFE or 0xFFFF). Those reach JCS through `observation_identity`, so they must fail
      closed here.

    The noncharacter predicate is duplicated deliberately rather than imported: it is three
    comparisons, and reaching into a private `capture_event` helper would create a seam this
    ticket does not authorize. `test_require_text_matches_the_canonical_ijson_boundary` pins
    the duplicate against the real `canonical_json` behaviour so the two cannot drift.
    """

    for character in value:
        code = ord(character)
        if code == 0:
            raise SemanticDisagreement
        if 0xD800 <= code <= 0xDFFF:
            raise SemanticDisagreement
        if 0xFDD0 <= code <= 0xFDEF or code & 0xFFFE == 0xFFFE:
            raise SemanticDisagreement
    return value


def _require_identity_text(value: str) -> str:
    """Identity-bearing text additionally forbids emptiness.

    Permitted empty non-identity testimony — an empty title or website name, say — is
    ordinary provider content and stays admissible.
    """

    if value == "":
        raise SemanticDisagreement
    return _require_text(value)


def _require_ijson(value: int) -> None:
    if value < -IJSON_MAX or value > IJSON_MAX:
        raise SemanticDisagreement


def _columns[T](name: str, pair: tuple[T | None, str]) -> dict[str, object]:
    return {name: pair[0], f"{name}_state": pair[1]}


def _inapplicable() -> tuple[None, str]:
    return None, FieldState.INAPPLICABLE.value


def _pair[T](field: Field[T]) -> tuple[T | None, str]:
    """Split one parser Field into its persisted (value, state) column pair.

    `Field[T].value` is `T | None` for every state. A STATED field carrying `None` would be
    a parser invariant violation; it fails closed as a rejected unit rather than reaching
    SQL.
    """

    if field.state is not FieldState.STATED:
        return None, field.state.value
    value = field.value
    if value is None:
        raise SemanticDisagreement
    return value, field.state.value


def _text_pair(field: Field[str]) -> tuple[str | None, str]:
    pair = _pair(field)
    value = pair[0]
    return (None if value is None else _require_text(value)), pair[1]


def _int_pair(field: Field[int]) -> tuple[int | None, str]:
    pair = _pair(field)
    value = pair[0]
    if value is not None:
        _require_ijson(value)
    return value, pair[1]


def _decimal_pair(field: Field[Decimal]) -> tuple[Decimal | None, str]:
    return _pair(field)


def _bool_pair(field: Field[bool]) -> tuple[bool | None, str]:
    return _pair(field)


def _int_array_pair(field: Field[tuple[int, ...]]) -> tuple[list[int] | None, str]:
    pair = _pair(field)
    value = pair[0]
    if value is None:
        return None, pair[1]
    for member in value:
        _require_ijson(member)
    return list(value), pair[1]


def _text_array_pair(field: Field[tuple[str, ...]]) -> tuple[list[str] | None, str]:
    pair = _pair(field)
    value = pair[0]
    if value is None:
        return None, pair[1]
    return [_require_text(member) for member in value], pair[1]


def _envelope(
    capture_id: str, attempt_id: str, kind: str, identity: str
) -> ObservationEnvelope:
    return ObservationEnvelope(
        capture_id=capture_id,
        attempt_id=attempt_id,
        derivation_version_id=RANKED_KEYWORDS_RECIPE_ID,
        provider=PROVIDER,
        adapter_contract=RANKED_KEYWORDS_ADAPTER_CONTRACT,
        observation_kind=kind,
        within_capture_identity=identity,
    )


def _identity(kind: str, axes: Mapping[str, object]) -> str:
    return observation_identity(
        {
            "axes": dict(axes),
            "observation_kind": kind,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        RANKED_KEYWORDS_RECIPE,
    )


def _write_attempt_outcome(connection: Connection[Any], attempt_id: str) -> None:
    _write_outcome(
        connection,
        attempt_id=attempt_id,
        capture_id=None,
        classification=ATTEMPT_CLASSIFICATION,
        observation_count=0,
    )


def _write_capture_unit(
    connection: Connection[Any],
    attempt_id: str,
    capture_id: str,
    planned: PlannedCapture,
) -> None:
    with connection.transaction():
        _write_outcome(
            connection,
            attempt_id=attempt_id,
            capture_id=capture_id,
            classification=planned.classification,
            observation_count=len(planned.envelopes),
        )
        for envelope in planned.envelopes:
            write_observation_envelope(connection, envelope)
        for table in _DETAIL_TABLES:
            content_keys = _DETAIL_CONTENT[table]
            for row in planned.details[table]:
                _write_closed_row(
                    connection,
                    table=table,
                    identity=_detail_identity(row),
                    content={key: row[key] for key in content_keys},
                )
        for row in planned.item_occurrences:
            _write_closed_row(
                connection,
                table=ITEM_OCCURRENCES_TABLE,
                identity={key: row[key] for key in _ITEM_OCCURRENCE_IDENTITY},
                content={key: row[key] for key in _ITEM_OCCURRENCE_CONTENT},
            )
        for row in planned.monthly_occurrences:
            _write_closed_row(
                connection,
                table=MONTHLY_OCCURRENCES_TABLE,
                identity={key: row[key] for key in _MONTHLY_OCCURRENCE_IDENTITY},
                content={},
            )
        if planned.context is not None:
            context = planned.context
            _write_closed_row(
                connection,
                table=CONTEXT_TABLE,
                identity={
                    "capture_id": context["capture_id"],
                    "derivation_version_id": context["derivation_version_id"],
                },
                content={key: context[key] for key in _CONTEXT_CONTENT},
            )
        for diagnostic in planned.diagnostics:
            write_derivation_diagnostic(connection, diagnostic)
        _assert_complete_set(connection, attempt_id, capture_id, planned)


def _detail_identity(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "capture_id": row["capture_id"],
        "derivation_version_id": row["derivation_version_id"],
        "within_capture_identity": row["within_capture_identity"],
        "observation_kind": row["observation_kind"],
    }


def _write_outcome(
    connection: Connection[Any],
    *,
    attempt_id: str,
    capture_id: str | None,
    classification: str,
    observation_count: int,
) -> None:
    existing = connection.execute(
        """
        SELECT classification, observation_count
        FROM outcomes
        WHERE derivation_version_id IS NOT DISTINCT FROM %s
          AND attempt_id IS NOT DISTINCT FROM %s
          AND capture_id IS NOT DISTINCT FROM %s
        """,
        (RANKED_KEYWORDS_RECIPE_ID, attempt_id, capture_id),
    ).fetchone()
    if existing is None:
        connection.execute(
            """
            INSERT INTO outcomes (
                attempt_id, capture_id, derivation_version_id,
                classification, observation_count
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                attempt_id,
                capture_id,
                RANKED_KEYWORDS_RECIPE_ID,
                classification,
                observation_count,
            ),
        )
        return
    if existing[0] != classification or int(existing[1]) != observation_count:
        raise DerivationError("conflicting provider outcome")


def _write_closed_row(
    connection: Connection[Any],
    *,
    table: str,
    identity: Mapping[str, object],
    content: Mapping[str, object],
) -> None:
    """Insert one row, or prove the stored row already carries the exact intended content.

    `ON CONFLICT DO NOTHING` is never used: silently keeping a differing stored row would
    make semantic disagreement invisible instead of failing the rebuild.
    """

    where = sql.SQL(" AND ").join(
        sql.SQL("{} IS NOT DISTINCT FROM {}").format(
            sql.Identifier(key), sql.Placeholder()
        )
        for key in identity
    )
    selected: sql.Composable
    if content:
        selected = sql.SQL(", ").join(sql.Identifier(key) for key in content)
    else:
        selected = sql.SQL("1")
    existing = connection.execute(
        sql.SQL("SELECT {} FROM {} WHERE {}").format(
            selected, sql.Identifier(table), where
        ),
        [identity[key] for key in identity],
    ).fetchone()
    if existing is None:
        values = {**dict(identity), **dict(content)}
        columns = sorted(values)
        connection.execute(
            sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table),
                sql.SQL(", ").join(sql.Identifier(key) for key in columns),
                sql.SQL(", ").join(sql.Placeholder() for _ in columns),
            ),
            [values[key] for key in columns],
        )
        return
    if not content:
        return
    intended = tuple(_normalize_sql_value(content[key]) for key in content)
    found = tuple(_normalize_sql_value(item) for item in existing)
    if found != intended:
        raise DerivationError(f"conflicting {table} row")


def _assert_complete_set(
    connection: Connection[Any],
    attempt_id: str,
    capture_id: str,
    planned: PlannedCapture,
) -> None:
    recipe = RANKED_KEYWORDS_RECIPE_ID
    stored_outcomes = connection.execute(
        """
        SELECT attempt_id, classification, observation_count
        FROM outcomes
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (recipe, capture_id),
    ).fetchall()
    intended_outcomes = {(attempt_id, planned.classification, len(planned.envelopes))}
    stored_outcome_set = {(row[0], row[1], int(row[2])) for row in stored_outcomes}
    if stored_outcome_set != intended_outcomes or len(stored_outcomes) != 1:
        raise DerivationError("complete-set mismatch: outcome")
    outcome_count = int(stored_outcomes[0][2])
    stored_envelopes = connection.execute(
        """
        SELECT within_capture_identity, observation_kind
        FROM observation_envelopes
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (recipe, capture_id),
    ).fetchall()
    intended_envelopes = {
        (item.within_capture_identity, item.observation_kind)
        for item in planned.envelopes
    }
    if set(stored_envelopes) != intended_envelopes or len(stored_envelopes) != len(
        planned.envelopes
    ):
        raise DerivationError("complete-set mismatch: envelopes")
    if outcome_count != len(stored_envelopes):
        raise DerivationError("complete-set mismatch: observation_count")
    for table in _DETAIL_TABLES:
        rows = planned.details[table]
        stored = connection.execute(
            sql.SQL(
                """
                SELECT within_capture_identity
                FROM {}
                WHERE derivation_version_id = %s AND capture_id = %s
                """
            ).format(sql.Identifier(table)),
            (recipe, capture_id),
        ).fetchall()
        intended = {row["within_capture_identity"] for row in rows}
        if {item[0] for item in stored} != intended or len(stored) != len(rows):
            raise DerivationError(f"complete-set mismatch: {table}")
    _assert_occurrences(
        connection,
        capture_id,
        table=ITEM_OCCURRENCES_TABLE,
        columns=("item_index", "ranked_result_identity", "keyword_data_identity"),
        planned_rows=planned.item_occurrences,
    )
    _assert_occurrences(
        connection,
        capture_id,
        table=MONTHLY_OCCURRENCES_TABLE,
        columns=("within_capture_identity", "item_index"),
        planned_rows=planned.monthly_occurrences,
    )
    stored_context = connection.execute(
        """
        SELECT capture_id
        FROM ranked_keywords_result_context
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (recipe, capture_id),
    ).fetchall()
    intended_context = 1 if planned.context is not None else 0
    if len(stored_context) != intended_context:
        raise DerivationError("complete-set mismatch: context")
    stored_diagnostics = connection.execute(
        """
        SELECT diagnostic_code, provider_body_path
        FROM derivation_diagnostics
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (recipe, capture_id),
    ).fetchall()
    intended_diagnostics = {
        (item.diagnostic_code, item.provider_body_path) for item in planned.diagnostics
    }
    if set(stored_diagnostics) != intended_diagnostics or len(
        stored_diagnostics
    ) != len(planned.diagnostics):
        raise DerivationError("complete-set mismatch: diagnostics")


def _assert_occurrences(
    connection: Connection[Any],
    capture_id: str,
    *,
    table: str,
    columns: tuple[str, ...],
    planned_rows: Sequence[Mapping[str, object]],
) -> None:
    stored = connection.execute(
        sql.SQL(
            """
            SELECT {}
            FROM {}
            WHERE derivation_version_id = %s AND capture_id = %s
            """
        ).format(
            sql.SQL(", ").join(sql.Identifier(key) for key in columns),
            sql.Identifier(table),
        ),
        (RANKED_KEYWORDS_RECIPE_ID, capture_id),
    ).fetchall()
    intended = {tuple(row[key] for key in columns) for row in planned_rows}
    if set(stored) != intended or len(stored) != len(planned_rows):
        raise DerivationError(f"complete-set mismatch: {table}")


def _normalize_sql_value(value: object) -> object:
    if isinstance(value, list):
        return tuple(value)
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="observatory.google_ranked_keywords_derive",
        description="Derive DataForSEO Google Ranked Keywords rows from Evidence.",
    )
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--database-url", default=None)
    args = parser.parse_args(argv)
    try:
        dsn = resolve_database_url(args.database_url)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    store = open_store(args.evidence_root)
    with connect(dsn) as connection:
        summary = derive_google_ranked_keywords(store, connection)
    sys.stdout.write(f"derivation_version {summary.derivation_version_id}\n")
    sys.stdout.write(f"attempt_outcomes {summary.attempt_outcomes}\n")
    sys.stdout.write(f"capture_outcomes {summary.capture_outcomes}\n")
    sys.stdout.write(f"observations {summary.observations}\n")
    sys.stdout.write(f"diagnostics {summary.diagnostics}\n")
    sys.stdout.write(f"integrity_failures {summary.integrity_failures}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
