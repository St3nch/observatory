"""Derive DataForSEO Google Related Keywords Outcomes and Observations from Evidence.

RK-04 turns one verified Related Keywords Capture into three semantic Observation kinds —
keyword-data, monthly search volume, and relationship — plus subordinate occurrence and
result-context testimony. It invents no graph meaning, no canonical keyword identity, and no
cross-surface equivalence with Keyword Overview.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Final

from psycopg import Connection, sql

from observatory.capture_event import (
    RELATED_KEYWORDS_ADAPTER_CONTRACT,
    DocumentError,
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
    KeywordData,
    RelatedKeywordsIR,
    RelatedKeywordsParseError,
    parse_related_keywords,
)
from observatory.dataforseo_keyword_overview import Field, FieldState, ParseClassification
from observatory.derive import DerivationError
from observatory.evidence_store import EvidenceStore, IntegrityError, open_store
from observatory.migrate import apply_schema, connect, resolve_database_url
from observatory.provider_recipe import (
    IDENTITY_SCHEMA,
    IDENTITY_VERSION,
    DerivationDiagnostic,
    ObservationEnvelope,
    observation_identity,
    register_provider_recipe,
    write_derivation_diagnostic,
    write_observation_envelope,
)

ATTEMPT_CLASSIFICATION: Final[str] = "authorized_unresolved"
IJSON_MAX: Final[int] = 9007199254740991

KEYWORD_DATA_TABLE: Final[str] = "related_keywords_keyword_data"
KEYWORD_INFO_TABLE: Final[str] = "related_keywords_keyword_info"
PROPERTIES_TABLE: Final[str] = "related_keywords_keyword_properties"
BACKLINKS_TABLE: Final[str] = "related_keywords_avg_backlinks"
INTENT_TABLE: Final[str] = "related_keywords_search_intent"
SERP_TABLE: Final[str] = "related_keywords_serp_info"
MONTHLY_TABLE: Final[str] = "related_keywords_monthly_search_volume"
RELATIONSHIP_TABLE: Final[str] = "related_keywords_relationship"
ITEM_OCCURRENCES_TABLE: Final[str] = "related_keywords_keyword_data_item_occurrences"
MONTHLY_OCCURRENCES_TABLE: Final[str] = "related_keywords_monthly_item_occurrences"
RELATIONSHIP_OCCURRENCES_TABLE: Final[str] = "related_keywords_relationship_occurrences"
CONTEXT_TABLE: Final[str] = "related_keywords_result_context"

RK04_TABLES: Final[tuple[str, ...]] = (
    KEYWORD_DATA_TABLE,
    KEYWORD_INFO_TABLE,
    PROPERTIES_TABLE,
    BACKLINKS_TABLE,
    INTENT_TABLE,
    SERP_TABLE,
    MONTHLY_TABLE,
    RELATIONSHIP_TABLE,
    ITEM_OCCURRENCES_TABLE,
    MONTHLY_OCCURRENCES_TABLE,
    RELATIONSHIP_OCCURRENCES_TABLE,
    CONTEXT_TABLE,
)

# Kind-bound semantic parents carry a generic Observation envelope. The five keyword-data
# child relations exist only when their enclosing provider object is STATED and hang off the
# keyword-data parent, never off an arbitrary envelope.
_ENVELOPE_TABLES: Final[tuple[str, ...]] = (
    KEYWORD_DATA_TABLE,
    MONTHLY_TABLE,
    RELATIONSHIP_TABLE,
)
_KEYWORD_DATA_CHILD_TABLES: Final[tuple[str, ...]] = (
    KEYWORD_INFO_TABLE,
    PROPERTIES_TABLE,
    BACKLINKS_TABLE,
    INTENT_TABLE,
    SERP_TABLE,
)
_DETAIL_TABLES: Final[tuple[str, ...]] = (
    KEYWORD_DATA_TABLE,
    *_KEYWORD_DATA_CHILD_TABLES,
    MONTHLY_TABLE,
    RELATIONSHIP_TABLE,
)

_KEYWORD_DATA_CONTENT: Final[tuple[str, ...]] = (
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
_SERP_CONTENT: Final[tuple[str, ...]] = (
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
_MONTHLY_CONTENT: Final[tuple[str, ...]] = (
    "requested_seed",
    "locus",
    "keyword",
    "year",
    "month",
    "search_volume",
)
_RELATIONSHIP_CONTENT: Final[tuple[str, ...]] = (
    "requested_seed",
    "source_keyword",
    "target_keyword",
)
_DETAIL_CONTENT: Final[dict[str, tuple[str, ...]]] = {
    KEYWORD_DATA_TABLE: _KEYWORD_DATA_CONTENT,
    KEYWORD_INFO_TABLE: _KEYWORD_INFO_CONTENT,
    PROPERTIES_TABLE: _PROPERTIES_CONTENT,
    BACKLINKS_TABLE: _BACKLINKS_CONTENT,
    INTENT_TABLE: _INTENT_CONTENT,
    SERP_TABLE: _SERP_CONTENT,
    MONTHLY_TABLE: _MONTHLY_CONTENT,
    RELATIONSHIP_TABLE: _RELATIONSHIP_CONTENT,
}

_ITEM_OCCURRENCE_IDENTITY: Final[tuple[str, ...]] = (
    "capture_id",
    "derivation_version_id",
    "within_capture_identity",
    "observation_kind",
    "item_index",
)
_ITEM_OCCURRENCE_CONTENT: Final[tuple[str, ...]] = (
    "depth",
    "item_se_type",
    "related_keywords_state",
)
_MONTHLY_OCCURRENCE_IDENTITY: Final[tuple[str, ...]] = _ITEM_OCCURRENCE_IDENTITY
_RELATIONSHIP_OCCURRENCE_IDENTITY: Final[tuple[str, ...]] = (
    "capture_id",
    "derivation_version_id",
    "within_capture_identity",
    "observation_kind",
    "source_item_index",
    "target_index",
)
_RELATIONSHIP_OCCURRENCE_CONTENT: Final[tuple[str, ...]] = ("source_depth",)
_CONTEXT_CONTENT: Final[tuple[str, ...]] = (
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
    relationship_occurrences: tuple[dict[str, object], ...]
    context: dict[str, object] | None
    diagnostics: tuple[DerivationDiagnostic, ...]


class SemanticDisagreement(Exception):
    """Same semantic identity carries conflicting testimony, or content is inadmissible."""


def derive_google_related_keywords(
    store: EvidenceStore,
    connection: Connection[Any],
) -> ProviderDeriveSummary:
    """Derive paid Related Keywords Evidence under the accepted RK-04 recipe."""

    if type(store) is not EvidenceStore:
        raise TypeError("Related Keywords derive requires the concrete EvidenceStore")
    apply_schema(connection)
    registered = register_provider_recipe(connection, RELATED_KEYWORDS_RECIPE)
    if registered.derivation_version_id != RELATED_KEYWORDS_RECIPE_ID:
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
            or attempt.get("adapter_contract") != RELATED_KEYWORDS_ADAPTER_CONTRACT
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
            or capture.get("adapter_contract") != RELATED_KEYWORDS_ADAPTER_CONTRACT
        ):
            continue
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
            or attempt.get("adapter_contract") != RELATED_KEYWORDS_ADAPTER_CONTRACT
        ):
            integrity_failures += 1
            continue
        parameters = attempt.get("parameters")
        if not isinstance(parameters, Mapping):
            integrity_failures += 1
            continue
        try:
            closed = validate_related_keywords_http_parameters(parameters)
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
        planned = plan_related_keywords_capture(cited, capture_id, capture, closed, body)
        if planned is None:
            integrity_failures += 1
            continue
        _write_capture_unit(connection, cited, capture_id, planned)
        capture_written += 1
        observation_written += len(planned.envelopes)
        diagnostic_written += len(planned.diagnostics)
    return ProviderDeriveSummary(
        derivation_version_id=RELATED_KEYWORDS_RECIPE_ID,
        attempt_outcomes=attempt_written,
        capture_outcomes=capture_written,
        observations=observation_written,
        diagnostics=diagnostic_written,
        integrity_failures=integrity_failures,
    )


def plan_related_keywords_capture(
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
        relationship_occurrences=(),
        context=None,
        diagnostics=(),
    )


def _classify_capture(
    capture: Mapping[str, object],
    parameters: Mapping[str, object],
    body: bytes | None,
) -> tuple[str, RelatedKeywordsIR | None]:
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
        parsed = parse_related_keywords(body, parameters)
    except RelatedKeywordsParseError as exc:
        # The trusted capture_event validator already accepted these Attempt parameters, so a
        # residual `/attempt` failure is validator divergence or Evidence damage — never a
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
    monthly: dict[tuple[int, int], int]
    monthly_occurrences: dict[tuple[int, int], list[int]]


def _plan_admitted(
    attempt_id: str, capture_id: str, parsed: RelatedKeywordsIR
) -> PlannedCapture:
    result = parsed.result
    if result is None:
        raise SemanticDisagreement
    seed = _require_identity_text(parsed.request.keyword)
    groups: dict[tuple[str, str], _KeywordDataGroup] = {}
    item_occurrence_rows: list[tuple[tuple[str, str], int, int, str, str]] = []

    if result.seed_keyword_data.state is FieldState.STATED:
        seed_data = _require_stated(result.seed_keyword_data)
        key = (LOCUS_SEED, _require_identity_text(seed_data.keyword))
        _merge_keyword_data(groups, key, seed_data, item_index=None)

    for index, item in enumerate(result.items):
        if item.keyword_data.state is not FieldState.STATED:
            # A returned item without stated keyword_data cannot form the required semantic
            # identity. It is rejected as a whole unit, never silently dropped.
            raise SemanticDisagreement
        data = _require_stated(item.keyword_data)
        key = (LOCUS_ITEM, _require_identity_text(data.keyword))
        _require_ijson(index)
        _merge_keyword_data(groups, key, data, item_index=index)
        item_occurrence_rows.append(
            (
                key,
                index,
                item.depth,
                _require_text(item.se_type),
                item.related_keywords.state.value,
            )
        )

    envelopes: list[ObservationEnvelope] = []
    details: dict[str, list[dict[str, object]]] = {table: [] for table in _DETAIL_TABLES}
    identities: dict[tuple[str, str], str] = {}
    monthly_identities: dict[tuple[str, str, int, int], str] = {}

    for (locus, keyword), group in groups.items():
        identity = _identity(
            KEYWORD_DATA_KIND,
            {"keyword": keyword, "locus": locus, "requested_seed": seed},
        )
        identities[(locus, keyword)] = identity
        envelopes.append(_envelope(capture_id, attempt_id, KEYWORD_DATA_KIND, identity))
        parent = dict(group.payload[KEYWORD_DATA_TABLE])
        parent.update({"requested_seed": seed, "locus": locus, "keyword": keyword})
        details[KEYWORD_DATA_TABLE].append(
            _detail_row(capture_id, identity, KEYWORD_DATA_KIND, parent)
        )
        for table in _KEYWORD_DATA_CHILD_TABLES:
            child = group.payload.get(table)
            if child is not None:
                details[table].append(
                    _detail_row(capture_id, identity, KEYWORD_DATA_KIND, child)
                )

    monthly_occurrences: list[dict[str, object]] = []
    for (locus, keyword), group in groups.items():
        for (year, month), volume in group.monthly.items():
            identity = _identity(
                MONTHLY_KIND,
                {
                    "keyword": keyword,
                    "locus": locus,
                    "month": month,
                    "requested_seed": seed,
                    "year": year,
                },
            )
            monthly_identities[(locus, keyword, year, month)] = identity
            envelopes.append(_envelope(capture_id, attempt_id, MONTHLY_KIND, identity))
            details[MONTHLY_TABLE].append(
                _detail_row(
                    capture_id,
                    identity,
                    MONTHLY_KIND,
                    {
                        "requested_seed": seed,
                        "locus": locus,
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
                        "derivation_version_id": RELATED_KEYWORDS_RECIPE_ID,
                        "within_capture_identity": identity,
                        "observation_kind": MONTHLY_KIND,
                        "item_index": index,
                    }
                )

    relationships: dict[tuple[str, str], list[tuple[int, int, int]]] = {}
    for index, item in enumerate(result.items):
        source = _require_stated(item.keyword_data).keyword
        if item.related_keywords.state is not FieldState.STATED:
            continue
        for reference in _require_stated(item.related_keywords):
            target = _require_identity_text(reference.target)
            _require_ijson(reference.provider_array_index)
            relationships.setdefault((source, target), []).append(
                (index, item.depth, reference.provider_array_index)
            )

    relationship_occurrences: list[dict[str, object]] = []
    for (source, target), occurrences in relationships.items():
        identity = _identity(
            RELATIONSHIP_KIND,
            {
                "requested_seed": seed,
                "source_keyword": source,
                "target_keyword": target,
            },
        )
        envelopes.append(_envelope(capture_id, attempt_id, RELATIONSHIP_KIND, identity))
        details[RELATIONSHIP_TABLE].append(
            _detail_row(
                capture_id,
                identity,
                RELATIONSHIP_KIND,
                {
                    "requested_seed": seed,
                    "source_keyword": source,
                    "target_keyword": target,
                },
            )
        )
        for item_index, depth, target_index in occurrences:
            relationship_occurrences.append(
                {
                    "capture_id": capture_id,
                    "derivation_version_id": RELATED_KEYWORDS_RECIPE_ID,
                    "within_capture_identity": identity,
                    "observation_kind": RELATIONSHIP_KIND,
                    "source_item_index": item_index,
                    "target_index": target_index,
                    "source_depth": depth,
                }
            )

    item_occurrences: list[dict[str, object]] = []
    for key, index, depth, se_type, edge_state in item_occurrence_rows:
        item_occurrences.append(
            {
                "capture_id": capture_id,
                "derivation_version_id": RELATED_KEYWORDS_RECIPE_ID,
                "within_capture_identity": identities[key],
                "observation_kind": KEYWORD_DATA_KIND,
                "item_index": index,
                "depth": depth,
                "item_se_type": se_type,
                "related_keywords_state": edge_state,
            }
        )

    classification = (
        "observation_admitted_empty" if not envelopes else "observation_admitted"
    )
    return PlannedCapture(
        classification=classification,
        envelopes=tuple(envelopes),
        details={table: tuple(rows) for table, rows in details.items()},
        item_occurrences=tuple(item_occurrences),
        monthly_occurrences=tuple(monthly_occurrences),
        relationship_occurrences=tuple(relationship_occurrences),
        context=_context_row(
            attempt_id,
            capture_id,
            parsed,
            derived_items=len(result.items),
            derived_relationships=len(relationship_occurrences),
        ),
        diagnostics=(),
    )


def _merge_keyword_data(
    groups: dict[tuple[str, str], _KeywordDataGroup],
    key: tuple[str, str],
    data: KeywordData,
    *,
    item_index: int | None,
) -> None:
    """Fold one provider occurrence into its semantic keyword-data identity.

    The comparison key is the exact set of rows this occurrence would persist. Monthly points
    are therefore excluded structurally — they live in the separate monthly kind — while
    `monthly_searches_state` stays inside the compared keyword-info row, so a STATED-vs-null
    series disagreement is still a real same-identity conflict.
    """

    payload = _keyword_data_payload(data)
    existing = groups.get(key)
    if existing is None:
        existing = _KeywordDataGroup(payload=payload, monthly={}, monthly_occurrences={})
        groups[key] = existing
    elif _comparable(existing.payload) != _comparable(payload):
        raise SemanticDisagreement
    for year, month, volume in _monthly_points(data):
        period = (year, month)
        seen = existing.monthly.get(period)
        if seen is not None and seen != volume:
            raise SemanticDisagreement
        existing.monthly[period] = volume
        if item_index is not None:
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
    location_code, location_state = _int_pair(data.location_code)
    language_code, language_state = _text_pair(data.language_code)
    se_type, se_type_state = _text_pair(data.se_type)
    payload: dict[str, dict[str, object]] = {
        KEYWORD_DATA_TABLE: {
            "location_code": location_code,
            "location_code_state": location_state,
            "language_code": language_code,
            "language_code_state": language_state,
            "se_type": se_type,
            "se_type_state": se_type_state,
            "keyword_info_state": data.keyword_info.state.value,
            "keyword_properties_state": data.keyword_properties.state.value,
            "avg_backlinks_state": data.avg_backlinks_info.state.value,
            "search_intent_state": data.search_intent_info.state.value,
            "serp_info_state": data.serp_info.state.value,
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
            monthly_trend = _signed_pair(trend.monthly)
            quarterly_trend = _signed_pair(trend.quarterly)
            yearly_trend = _signed_pair(trend.yearly)
        else:
            # The trend object itself is not stated, so its members have no state of their
            # own. `inapplicable` is the recipe-defined state for exactly that case.
            inapplicable: tuple[None, str] = (None, FieldState.INAPPLICABLE.value)
            monthly_trend = inapplicable
            quarterly_trend = inapplicable
            yearly_trend = inapplicable
        info_se_type, info_se_state = _text_pair(info.se_type)
        clock, clock_state = _text_pair(info.last_updated_time)
        competition, competition_state = _decimal_pair(info.competition)
        level, level_state = _text_pair(info.competition_level)
        cpc, cpc_state = _decimal_pair(info.cpc)
        volume, volume_state = _int_pair(info.search_volume)
        low_bid, low_state = _decimal_pair(info.low_top_of_page_bid)
        high_bid, high_state = _decimal_pair(info.high_top_of_page_bid)
        categories, categories_state = _int_array_pair(info.categories)
        payload[KEYWORD_INFO_TABLE] = {
            "se_type": info_se_type,
            "se_type_state": info_se_state,
            "keyword_info_last_updated_time": clock,
            "keyword_info_last_updated_time_state": clock_state,
            "competition": competition,
            "competition_state": competition_state,
            "competition_level": level,
            "competition_level_state": level_state,
            "cpc": cpc,
            "cpc_state": cpc_state,
            "search_volume": volume,
            "search_volume_state": volume_state,
            "low_top_of_page_bid": low_bid,
            "low_top_of_page_bid_state": low_state,
            "high_top_of_page_bid": high_bid,
            "high_top_of_page_bid_state": high_state,
            "categories": categories,
            "categories_state": categories_state,
            "monthly_searches_state": info.monthly_searches.state.value,
            "search_volume_trend_state": trend_state.value,
            "trend_monthly": monthly_trend[0],
            "trend_monthly_state": monthly_trend[1],
            "trend_quarterly": quarterly_trend[0],
            "trend_quarterly_state": quarterly_trend[1],
            "trend_yearly": yearly_trend[0],
            "trend_yearly_state": yearly_trend[1],
        }
    if data.keyword_properties.state is FieldState.STATED:
        properties = _require_stated(data.keyword_properties)
        prop_se_type, prop_se_state = _text_pair(properties.se_type)
        core, core_state = _text_pair(properties.core_keyword)
        algorithm, algorithm_state = _text_pair(properties.synonym_clustering_algorithm)
        difficulty, difficulty_state = _int_pair(properties.keyword_difficulty)
        language, language_detected_state = _text_pair(properties.detected_language)
        another, another_state = _bool_pair(properties.is_another_language)
        payload[PROPERTIES_TABLE] = {
            "se_type": prop_se_type,
            "se_type_state": prop_se_state,
            "core_keyword": core,
            "core_keyword_state": core_state,
            "synonym_clustering_algorithm": algorithm,
            "synonym_clustering_algorithm_state": algorithm_state,
            "keyword_difficulty": difficulty,
            "keyword_difficulty_state": difficulty_state,
            "detected_language": language,
            "detected_language_state": language_detected_state,
            "is_another_language": another,
            "is_another_language_state": another_state,
        }
    if data.avg_backlinks_info.state is FieldState.STATED:
        backlinks = _require_stated(data.avg_backlinks_info)
        bl_se_type, bl_se_state = _text_pair(backlinks.se_type)
        clock, clock_state = _text_pair(backlinks.last_updated_time)
        payload[BACKLINKS_TABLE] = {
            "se_type": bl_se_type,
            "se_type_state": bl_se_state,
            **_decimal_columns("backlinks", backlinks.backlinks),
            **_decimal_columns("dofollow", backlinks.dofollow),
            **_decimal_columns("referring_pages", backlinks.referring_pages),
            **_decimal_columns("referring_domains", backlinks.referring_domains),
            **_decimal_columns(
                "referring_main_domains", backlinks.referring_main_domains
            ),
            **_decimal_columns("rank", backlinks.rank),
            **_decimal_columns("main_domain_rank", backlinks.main_domain_rank),
            "avg_backlinks_last_updated_time": clock,
            "avg_backlinks_last_updated_time_state": clock_state,
        }
    if data.search_intent_info.state is FieldState.STATED:
        intent = _require_stated(data.search_intent_info)
        intent_se_type, intent_se_state = _text_pair(intent.se_type)
        main_intent, main_intent_state = _text_pair(intent.main_intent)
        foreign, foreign_state = _text_array_pair(intent.foreign_intent)
        clock, clock_state = _text_pair(intent.last_updated_time)
        payload[INTENT_TABLE] = {
            "se_type": intent_se_type,
            "se_type_state": intent_se_state,
            "main_intent": main_intent,
            "main_intent_state": main_intent_state,
            "foreign_intent": foreign,
            "foreign_intent_state": foreign_state,
            "search_intent_last_updated_time": clock,
            "search_intent_last_updated_time_state": clock_state,
        }
    if data.serp_info.state is FieldState.STATED:
        serp = _require_stated(data.serp_info)
        serp_se_type, serp_se_state = _text_pair(serp.se_type)
        check_url, check_url_state = _text_pair(serp.check_url)
        item_types, item_types_state = _text_array_pair(serp.serp_item_types)
        results_count, results_count_state = _int_pair(serp.se_results_count)
        last_clock, last_clock_state = _text_pair(serp.last_updated_time)
        previous_clock, previous_clock_state = _text_pair(serp.previous_updated_time)
        payload[SERP_TABLE] = {
            "se_type": serp_se_type,
            "se_type_state": serp_se_state,
            "check_url": check_url,
            "check_url_state": check_url_state,
            "serp_item_types": item_types,
            "serp_item_types_state": item_types_state,
            "se_results_count": results_count,
            "se_results_count_state": results_count_state,
            "serp_last_updated_time": last_clock,
            "serp_last_updated_time_state": last_clock_state,
            "serp_previous_updated_time": previous_clock,
            "serp_previous_updated_time_state": previous_clock_state,
        }
    return payload


def _decimal_columns(name: str, field: Field[Decimal]) -> dict[str, object]:
    value, state = _decimal_pair(field)
    return {name: value, f"{name}_state": state}


def _context_row(
    attempt_id: str,
    capture_id: str,
    parsed: RelatedKeywordsIR,
    *,
    derived_items: int,
    derived_relationships: int,
) -> dict[str, object]:
    result = parsed.result
    if result is None:
        raise SemanticDisagreement
    request = parsed.request
    location, location_state = _int_pair(result.location_code)
    language, language_state = _text_pair(result.language_code)
    se_type, se_type_state = _text_pair(result.se_type)
    for value in (request.location_code, request.depth, request.limit, request.offset):
        _require_ijson(value)
    _require_ijson(result.total_count)
    _require_ijson(result.items_count)
    _require_ijson(derived_items)
    _require_ijson(derived_relationships)
    return {
        "capture_id": capture_id,
        "derivation_version_id": RELATED_KEYWORDS_RECIPE_ID,
        "attempt_id": attempt_id,
        "requested_seed": _require_identity_text(request.keyword),
        "request_location_code": request.location_code,
        "request_language_code": _require_text(request.language_code),
        "request_depth": request.depth,
        "request_limit": request.limit,
        "request_offset": request.offset,
        "request_order_by": [_require_text(item) for item in request.order_by],
        "request_include_seed_keyword": request.include_seed_keyword,
        "request_include_serp_info": request.include_serp_info,
        "request_include_clickstream_data": request.include_clickstream_data,
        "request_ignore_synonyms": request.ignore_synonyms,
        "request_replace_with_core_keyword": request.replace_with_core_keyword,
        "result_seed_keyword": _require_text(result.seed_keyword),
        "result_location_code": location,
        "result_location_code_state": location_state,
        "result_language_code": language,
        "result_language_code_state": language_state,
        "result_se_type": se_type,
        "result_se_type_state": se_type_state,
        "total_count": result.total_count,
        "items_count": result.items_count,
        "seed_keyword_data_state": result.seed_keyword_data.state.value,
        "derived_returned_item_count": derived_items,
        "derived_relationship_occurrence_count": derived_relationships,
    }


def _detail_row(
    capture_id: str, identity: str, kind: str, content: Mapping[str, object]
) -> dict[str, object]:
    return {
        "capture_id": capture_id,
        "derivation_version_id": RELATED_KEYWORDS_RECIPE_ID,
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

    The RK-01 adapter constrains only the seed. Returned keywords and relationship targets are
    unrequested provider strings, so this is the boundary that keeps a hostile string a clean
    `provider_envelope_rejected` instead of an escaping JCS or psycopg exception.

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
    if value == "":
        raise SemanticDisagreement
    return _require_text(value)


def _require_ijson(value: int) -> None:
    if value < -IJSON_MAX or value > IJSON_MAX:
        raise SemanticDisagreement


def _pair[T](field: Field[T]) -> tuple[T | None, str]:
    """Split one parser Field into its persisted (value, state) column pair.

    `Field[T].value` is `T | None` for every state. A STATED field carrying `None` would be a
    parser invariant violation; it fails closed as a rejected unit rather than reaching SQL.
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


def _signed_pair(field: Field[int]) -> tuple[int | None, str]:
    return _int_pair(field)


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
        derivation_version_id=RELATED_KEYWORDS_RECIPE_ID,
        provider=PROVIDER,
        adapter_contract=RELATED_KEYWORDS_ADAPTER_CONTRACT,
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
        RELATED_KEYWORDS_RECIPE,
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
        for row in planned.relationship_occurrences:
            _write_closed_row(
                connection,
                table=RELATIONSHIP_OCCURRENCES_TABLE,
                identity={key: row[key] for key in _RELATIONSHIP_OCCURRENCE_IDENTITY},
                content={key: row[key] for key in _RELATIONSHIP_OCCURRENCE_CONTENT},
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
        (RELATED_KEYWORDS_RECIPE_ID, attempt_id, capture_id),
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
                RELATED_KEYWORDS_RECIPE_ID,
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
    recipe = RELATED_KEYWORDS_RECIPE_ID
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
        columns=("within_capture_identity", "item_index"),
        planned_rows=planned.item_occurrences,
    )
    _assert_occurrences(
        connection,
        capture_id,
        table=MONTHLY_OCCURRENCES_TABLE,
        columns=("within_capture_identity", "item_index"),
        planned_rows=planned.monthly_occurrences,
    )
    _assert_occurrences(
        connection,
        capture_id,
        table=RELATIONSHIP_OCCURRENCES_TABLE,
        columns=("within_capture_identity", "source_item_index", "target_index"),
        planned_rows=planned.relationship_occurrences,
    )
    stored_context = connection.execute(
        """
        SELECT capture_id
        FROM related_keywords_result_context
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
        (RELATED_KEYWORDS_RECIPE_ID, capture_id),
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
        prog="observatory.google_related_keywords_derive",
        description="Derive DataForSEO Google Related Keywords rows from Evidence.",
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
        summary = derive_google_related_keywords(store, connection)
    sys.stdout.write(f"derivation_version {summary.derivation_version_id}\n")
    sys.stdout.write(f"attempt_outcomes {summary.attempt_outcomes}\n")
    sys.stdout.write(f"capture_outcomes {summary.capture_outcomes}\n")
    sys.stdout.write(f"observations {summary.observations}\n")
    sys.stdout.write(f"diagnostics {summary.diagnostics}\n")
    sys.stdout.write(f"integrity_failures {summary.integrity_failures}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
