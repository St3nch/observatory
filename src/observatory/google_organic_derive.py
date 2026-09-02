"""Derive DataForSEO Google Organic Outcomes and Observations from Evidence."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from psycopg import Connection, sql

from observatory.capture_event import ORGANIC_ADAPTER_CONTRACT
from observatory.dataforseo_google_organic import (
    AIO_PRESENCE_KIND,
    AIO_SOURCE_KIND,
    FEATURE_PRESENCE_KIND,
    GOOGLE_ORGANIC_EXPANDED_RECIPE,
    GOOGLE_ORGANIC_EXPANDED_RECIPE_ID,
    GOOGLE_ORGANIC_RECIPE,
    GOOGLE_ORGANIC_RECIPE_ID,
    ORGANIC_PLACEMENT_KIND,
    ORGANIC_PLACEMENT_V2_KIND,
    ORGANIC_SITELINK_KIND,
    RELATED_QUERY_KIND,
    RELATED_QUESTION_KIND,
    TOP_STORY_RESULT_KIND,
    VIDEO_RESULT_KIND,
    AiOverviewSource,
    GoogleOrganicExpandedIR,
    GoogleOrganicIR,
    GoogleOrganicParseError,
    OrganicPlacementV2,
    RelatedQuestion,
    TopStoryGroup,
    VideoGroup,
    parse_google_organic,
    parse_google_organic_v2,
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
PROVIDER: Final[str] = "dataforseo"

FEATURES_TABLE: Final[str] = "google_organic_serp_features"
RANKED_TABLE: Final[str] = "google_organic_ranked_results"
AIO_PRESENCE_TABLE: Final[str] = "google_organic_aio_presence"
AIO_SOURCES_TABLE: Final[str] = "google_organic_aio_sources"
AIO_OCCURRENCES_TABLE: Final[str] = "google_organic_aio_source_occurrences"
QUESTIONS_TABLE: Final[str] = "google_organic_related_questions"
QUESTION_OCCURRENCES_TABLE: Final[str] = "google_organic_related_question_occurrences"
QUERIES_TABLE: Final[str] = "google_organic_related_queries"
CONTEXT_TABLE: Final[str] = "google_organic_result_context"

_FEATURE_CONTENT: Final[tuple[str, ...]] = (
    "requested_keyword",
    "item_type",
    "page",
    "position",
    "rank_group",
    "rank_absolute",
)
_RANKED_CONTENT: Final[tuple[str, ...]] = (
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
)
_AIO_PRESENCE_CONTENT: Final[tuple[str, ...]] = (
    "requested_keyword",
    "asynchronous_ai_overview",
    "page",
    "position",
    "rank_group",
    "rank_absolute",
)
_AIO_SOURCE_CONTENT: Final[tuple[str, ...]] = (
    "requested_keyword",
    "locus",
    "url",
    "domain",
    "domain_state",
    "title",
    "title_state",
    "source",
    "source_state",
)
_AIO_OCCURRENCE_CONTENT: Final[tuple[str, ...]] = (
    "locus",
    "element_index",
    "reference_index",
)
_QUESTION_CONTENT: Final[tuple[str, ...]] = (
    "requested_keyword",
    "title",
)
_QUESTION_OCCURRENCE_CONTENT: Final[tuple[str, ...]] = (
    "page",
    "position",
    "rank_group",
    "rank_absolute",
    "question_index",
)
_QUERY_CONTENT: Final[tuple[str, ...]] = (
    "requested_keyword",
    "query",
)
_CONTEXT_CONTENT: Final[tuple[str, ...]] = (
    "attempt_id",
    "requested_keyword",
    "returned_keyword",
    "returned_keyword_state",
    "location_code",
    "language_code",
    "se_domain",
    "se_domain_state",
    "result_datetime",
    "result_datetime_state",
    "se_results_count",
    "se_results_count_state",
    "pages_count",
    "pages_count_state",
    "items_count",
    "item_types",
)
_DETAIL_CONTENT: Final[dict[str, tuple[str, ...]]] = {
    FEATURES_TABLE: _FEATURE_CONTENT,
    RANKED_TABLE: _RANKED_CONTENT,
    AIO_PRESENCE_TABLE: _AIO_PRESENCE_CONTENT,
    AIO_SOURCES_TABLE: _AIO_SOURCE_CONTENT,
    QUESTIONS_TABLE: _QUESTION_CONTENT,
    QUERIES_TABLE: _QUERY_CONTENT,
}
RANKED_V2_TABLE: Final[str] = "google_organic_ranked_results_v2"
TOP_STORY_TABLE: Final[str] = "google_organic_top_story_results"
TOP_STORY_OCCURRENCES_TABLE: Final[str] = (
    "google_organic_top_story_result_occurrences"
)
VIDEO_TABLE: Final[str] = "google_organic_video_results"
VIDEO_OCCURRENCES_TABLE: Final[str] = "google_organic_video_result_occurrences"
SITELINKS_TABLE: Final[str] = "google_organic_sitelinks"
SITELINK_OCCURRENCES_TABLE: Final[str] = "google_organic_sitelink_occurrences"

_RANKED_V2_CONTENT: Final[tuple[str, ...]] = (
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
_TOP_STORY_CONTENT: Final[tuple[str, ...]] = (
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
_VIDEO_CONTENT: Final[tuple[str, ...]] = (
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
_SITELINK_CONTENT: Final[tuple[str, ...]] = (
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

# Ordered so every typed parent row exists before the child rows that reference it.
_EXPANDED_DETAIL_CONTENT: Final[dict[str, tuple[str, ...]]] = {
    FEATURES_TABLE: _FEATURE_CONTENT,
    RANKED_V2_TABLE: _RANKED_V2_CONTENT,
    AIO_PRESENCE_TABLE: _AIO_PRESENCE_CONTENT,
    AIO_SOURCES_TABLE: _AIO_SOURCE_CONTENT,
    QUESTIONS_TABLE: _QUESTION_CONTENT,
    QUERIES_TABLE: _QUERY_CONTENT,
    TOP_STORY_TABLE: _TOP_STORY_CONTENT,
    VIDEO_TABLE: _VIDEO_CONTENT,
    SITELINKS_TABLE: _SITELINK_CONTENT,
}
_EXPANDED_KIND_TABLE: Final[dict[str, str]] = {
    FEATURE_PRESENCE_KIND: FEATURES_TABLE,
    ORGANIC_PLACEMENT_V2_KIND: RANKED_V2_TABLE,
    AIO_PRESENCE_KIND: AIO_PRESENCE_TABLE,
    AIO_SOURCE_KIND: AIO_SOURCES_TABLE,
    RELATED_QUESTION_KIND: QUESTIONS_TABLE,
    RELATED_QUERY_KIND: QUERIES_TABLE,
    TOP_STORY_RESULT_KIND: TOP_STORY_TABLE,
    VIDEO_RESULT_KIND: VIDEO_TABLE,
    ORGANIC_SITELINK_KIND: SITELINKS_TABLE,
}
_CHILD_OCCURRENCE_TABLES: Final[tuple[str, ...]] = (
    TOP_STORY_OCCURRENCES_TABLE,
    VIDEO_OCCURRENCES_TABLE,
    SITELINK_OCCURRENCES_TABLE,
)
_CHILD_OCCURRENCE_IDENTITY: Final[tuple[str, ...]] = (
    "capture_id",
    "derivation_version_id",
    "within_capture_identity",
    "observation_kind",
    "child_index",
)

_OCCURRENCE_IDENTITY: Final[dict[str, tuple[str, ...]]] = {
    AIO_OCCURRENCES_TABLE: (
        "capture_id",
        "derivation_version_id",
        "within_capture_identity",
        "observation_kind",
        "locus",
        "element_index",
        "reference_index",
    ),
    QUESTION_OCCURRENCES_TABLE: (
        "capture_id",
        "derivation_version_id",
        "within_capture_identity",
        "observation_kind",
        "page",
        "position",
        "rank_group",
        "rank_absolute",
        "question_index",
    ),
}


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
    aio_occurrences: tuple[dict[str, object], ...]
    paa_occurrences: tuple[dict[str, object], ...]
    context: dict[str, object] | None
    diagnostics: tuple[DerivationDiagnostic, ...]


@dataclass(frozen=True)
class PlannedExpandedCapture:
    """Rebuildable expanded-Recipe rows for one Capture-stage unit.

    `envelopes` counts semantic Observations only; every occurrence tuple is
    subordinate order testimony and never raises `observation_count`.
    """

    classification: str
    envelopes: tuple[ObservationEnvelope, ...]
    details: Mapping[str, Sequence[Mapping[str, object]]]
    aio_occurrences: tuple[dict[str, object], ...]
    paa_occurrences: tuple[dict[str, object], ...]
    top_story_occurrences: tuple[dict[str, object], ...]
    video_occurrences: tuple[dict[str, object], ...]
    sitelink_occurrences: tuple[dict[str, object], ...]
    context: dict[str, object] | None
    diagnostics: tuple[DerivationDiagnostic, ...]


class AioSourceDisagreement(Exception):
    """Same semantic AIO identity carries conflicting field testimony."""


def derive_google_organic(
    store: EvidenceStore,
    connection: Connection[Any],
) -> ProviderDeriveSummary:
    """Derive paid Google Organic Evidence under the accepted PF-11 recipe."""

    if type(store) is not EvidenceStore:
        raise TypeError("Google Organic derive requires the concrete EvidenceStore")
    apply_schema(connection)
    registered = register_provider_recipe(connection, GOOGLE_ORGANIC_RECIPE)
    if registered.derivation_version_id != GOOGLE_ORGANIC_RECIPE_ID:
        raise DerivationError("recipe identity does not match the accepted digest")
    attempt_written = 0
    integrity_failures = 0
    for attempt_id in store.list_committed_ids("attempts"):
        try:
            attempt = store.read_attempt(attempt_id)
        except IntegrityError:
            integrity_failures += 1
            continue
        if attempt is None or attempt.get("adapter_contract") != ORGANIC_ADAPTER_CONTRACT:
            continue
        _write_attempt_outcome(connection, attempt_id, GOOGLE_ORGANIC_RECIPE_ID)
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
        if capture is None or capture.get("adapter_contract") != ORGANIC_ADAPTER_CONTRACT:
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
        if attempt is None or attempt.get("adapter_contract") != ORGANIC_ADAPTER_CONTRACT:
            integrity_failures += 1
            continue
        parameters = attempt.get("parameters")
        if not isinstance(parameters, Mapping):
            continue
        body: bytes | None = None
        if capture.get("transport_state") != "no_response":
            try:
                body = store.read_capture_body(capture_id)
            except IntegrityError:
                integrity_failures += 1
                continue
        planned = plan_google_organic_capture(cited, capture_id, capture, parameters, body)
        _write_capture_unit(connection, cited, capture_id, planned)
        capture_written += 1
        observation_written += len(planned.envelopes)
        diagnostic_written += len(planned.diagnostics)
    return ProviderDeriveSummary(
        derivation_version_id=GOOGLE_ORGANIC_RECIPE_ID,
        attempt_outcomes=attempt_written,
        capture_outcomes=capture_written,
        observations=observation_written,
        diagnostics=diagnostic_written,
        integrity_failures=integrity_failures,
    )


def plan_google_organic_capture(
    attempt_id: str,
    capture_id: str,
    capture: Mapping[str, object],
    parameters: Mapping[str, object],
    body: bytes | None,
) -> PlannedCapture:
    """Classify one Capture and plan its rebuildable Organic rows."""

    classification, parsed = _classify_capture(capture, parameters, body)
    empty = {table: () for table in _DETAIL_CONTENT}
    if parsed is None:
        return PlannedCapture(
            classification=classification,
            envelopes=(),
            details=empty,
            aio_occurrences=(),
            paa_occurrences=(),
            context=None,
            diagnostics=(),
        )
    diagnostics = tuple(
        _diagnostic(attempt_id, capture_id, item, GOOGLE_ORGANIC_RECIPE_ID)
        for item in parsed.diagnostics
    )
    if classification != "observation_admitted":
        return PlannedCapture(
            classification=classification,
            envelopes=(),
            details=empty,
            aio_occurrences=(),
            paa_occurrences=(),
            context=None,
            diagnostics=diagnostics,
        )
    try:
        return _plan_admitted(attempt_id, capture_id, parsed, diagnostics)
    except AioSourceDisagreement:
        return PlannedCapture(
            classification="provider_envelope_rejected",
            envelopes=(),
            details=empty,
            aio_occurrences=(),
            paa_occurrences=(),
            context=None,
            diagnostics=diagnostics,
        )


def _classify_capture(
    capture: Mapping[str, object],
    parameters: Mapping[str, object],
    body: bytes | None,
) -> tuple[str, GoogleOrganicIR | None]:
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
        parsed = parse_google_organic(body, parameters)
    except GoogleOrganicParseError as exc:
        if exc.code == "reconciliation_failed":
            return "reconciliation_failed", None
        return "provider_envelope_rejected", None
    if parsed.outcome is ParseClassification.PROVIDER_ERROR:
        return "provider_error", parsed
    return "observation_admitted", parsed


def _plan_admitted(
    attempt_id: str,
    capture_id: str,
    parsed: GoogleOrganicIR,
    diagnostics: tuple[DerivationDiagnostic, ...],
) -> PlannedCapture:
    recipe_id = GOOGLE_ORGANIC_RECIPE_ID
    keyword = parsed.requested_keyword
    envelopes: list[ObservationEnvelope] = []
    details = _empty_details()
    aio_occurrences: list[dict[str, object]] = []
    paa_occurrences: list[dict[str, object]] = []
    for feature in parsed.feature_placements:
        identity = _identity(
            FEATURE_PRESENCE_KIND,
            {
                "item_type": feature.item_type,
                "page": feature.page,
                "position": feature.position,
                "rank_absolute": feature.rank_absolute,
                "rank_group": feature.rank_group,
                "requested_keyword": keyword,
            },
        )
        envelopes.append(
            _envelope(capture_id, attempt_id, FEATURE_PRESENCE_KIND, identity)
        )
        details[FEATURES_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": recipe_id,
                "within_capture_identity": identity,
                "observation_kind": FEATURE_PRESENCE_KIND,
                "requested_keyword": keyword,
                "item_type": feature.item_type,
                "page": feature.page,
                "position": feature.position,
                "rank_group": feature.rank_group,
                "rank_absolute": feature.rank_absolute,
            }
        )
    for organic in parsed.organic_placements:
        identity = _identity(
            ORGANIC_PLACEMENT_KIND,
            {
                "page": organic.page,
                "position": organic.position,
                "rank_absolute": organic.rank_absolute,
                "rank_group": organic.rank_group,
                "requested_keyword": keyword,
            },
        )
        envelopes.append(
            _envelope(capture_id, attempt_id, ORGANIC_PLACEMENT_KIND, identity)
        )
        description, description_state = _field_pair(organic.description)
        website, website_state = _field_pair(organic.website_name)
        details[RANKED_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": recipe_id,
                "within_capture_identity": identity,
                "observation_kind": ORGANIC_PLACEMENT_KIND,
                "requested_keyword": keyword,
                "page": organic.page,
                "position": organic.position,
                "rank_group": organic.rank_group,
                "rank_absolute": organic.rank_absolute,
                "url": organic.url,
                "domain": organic.domain,
                "title": organic.title,
                "description": description,
                "description_state": description_state,
                "website_name": website,
                "website_name_state": website_state,
            }
        )
    if parsed.ai_overview is not None:
        aio = parsed.ai_overview
        identity = _identity(AIO_PRESENCE_KIND, {"requested_keyword": keyword})
        envelopes.append(_envelope(capture_id, attempt_id, AIO_PRESENCE_KIND, identity))
        details[AIO_PRESENCE_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": recipe_id,
                "within_capture_identity": identity,
                "observation_kind": AIO_PRESENCE_KIND,
                "requested_keyword": keyword,
                "asynchronous_ai_overview": aio.asynchronous_ai_overview,
                "page": aio.page,
                "position": aio.position,
                "rank_group": aio.rank_group,
                "rank_absolute": aio.rank_absolute,
            }
        )
    grouped = _group_aio_sources(parsed.ai_overview_sources)
    for (locus, url), sources in grouped.items():
        identity = _identity(
            AIO_SOURCE_KIND,
            {"locus": locus, "requested_keyword": keyword, "url": url},
        )
        first = sources[0]
        domain, domain_state = _field_pair(first.domain)
        title, title_state = _field_pair(first.title)
        source, source_state = _field_pair(first.source)
        envelopes.append(_envelope(capture_id, attempt_id, AIO_SOURCE_KIND, identity))
        details[AIO_SOURCES_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": recipe_id,
                "within_capture_identity": identity,
                "observation_kind": AIO_SOURCE_KIND,
                "requested_keyword": keyword,
                "locus": locus,
                "url": url,
                "domain": domain,
                "domain_state": domain_state,
                "title": title,
                "title_state": title_state,
                "source": source,
                "source_state": source_state,
            }
        )
        for item in sources:
            aio_occurrences.append(
                {
                    "capture_id": capture_id,
                    "derivation_version_id": recipe_id,
                    "within_capture_identity": identity,
                    "observation_kind": AIO_SOURCE_KIND,
                    "locus": item.locus,
                    "element_index": item.element_index,
                    "reference_index": item.reference_index,
                }
            )
    questions = _group_paa_questions(parsed.related_questions)
    for title, rows in questions.items():
        identity = _identity(
            RELATED_QUESTION_KIND,
            {"requested_keyword": keyword, "title": title},
        )
        envelopes.append(
            _envelope(capture_id, attempt_id, RELATED_QUESTION_KIND, identity)
        )
        details[QUESTIONS_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": recipe_id,
                "within_capture_identity": identity,
                "observation_kind": RELATED_QUESTION_KIND,
                "requested_keyword": keyword,
                "title": title,
            }
        )
        for row in rows:
            paa_occurrences.append(
                {
                    "capture_id": capture_id,
                    "derivation_version_id": recipe_id,
                    "within_capture_identity": identity,
                    "observation_kind": RELATED_QUESTION_KIND,
                    "page": row.page,
                    "position": row.position,
                    "rank_group": row.rank_group,
                    "rank_absolute": row.rank_absolute,
                    "question_index": row.question_index,
                }
            )
    for query in parsed.related_queries:
        identity = _identity(
            RELATED_QUERY_KIND,
            {"query": query.query, "requested_keyword": keyword},
        )
        envelopes.append(_envelope(capture_id, attempt_id, RELATED_QUERY_KIND, identity))
        details[QUERIES_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": recipe_id,
                "within_capture_identity": identity,
                "observation_kind": RELATED_QUERY_KIND,
                "requested_keyword": keyword,
                "query": query.query,
            }
        )
    frozen_details = {table: tuple(rows) for table, rows in details.items()}
    classification = (
        "observation_admitted_empty" if not envelopes else "observation_admitted"
    )
    return PlannedCapture(
        classification=classification,
        envelopes=tuple(envelopes),
        details=frozen_details,
        aio_occurrences=tuple(aio_occurrences),
        paa_occurrences=tuple(paa_occurrences),
        context=_context_row(attempt_id, capture_id, parsed),
        diagnostics=diagnostics,
    )


def derive_google_organic_expanded(
    store: EvidenceStore,
    connection: Connection[Any],
) -> ProviderDeriveSummary:
    """Derive paid Google Organic Evidence under the PF-18 expanded Recipe.

    This never touches accepted v1 rows and never changes the operator Recipe
    selection: the same verified Capture stays independently derivable under both.
    """

    if type(store) is not EvidenceStore:
        raise TypeError("Google Organic derive requires the concrete EvidenceStore")
    apply_schema(connection)
    registered = register_provider_recipe(connection, GOOGLE_ORGANIC_EXPANDED_RECIPE)
    if registered.derivation_version_id != GOOGLE_ORGANIC_EXPANDED_RECIPE_ID:
        raise DerivationError("recipe identity does not match the accepted digest")
    attempt_written = 0
    integrity_failures = 0
    for attempt_id in store.list_committed_ids("attempts"):
        try:
            attempt = store.read_attempt(attempt_id)
        except IntegrityError:
            integrity_failures += 1
            continue
        if attempt is None or attempt.get("adapter_contract") != ORGANIC_ADAPTER_CONTRACT:
            continue
        _write_attempt_outcome(
            connection, attempt_id, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
        )
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
        if capture is None or capture.get("adapter_contract") != ORGANIC_ADAPTER_CONTRACT:
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
        if attempt is None or attempt.get("adapter_contract") != ORGANIC_ADAPTER_CONTRACT:
            integrity_failures += 1
            continue
        parameters = attempt.get("parameters")
        if not isinstance(parameters, Mapping):
            continue
        body: bytes | None = None
        if capture.get("transport_state") != "no_response":
            try:
                body = store.read_capture_body(capture_id)
            except IntegrityError:
                integrity_failures += 1
                continue
        planned = plan_google_organic_expanded_capture(
            cited, capture_id, capture, parameters, body
        )
        _write_expanded_capture_unit(connection, cited, capture_id, planned)
        capture_written += 1
        observation_written += len(planned.envelopes)
        diagnostic_written += len(planned.diagnostics)
    return ProviderDeriveSummary(
        derivation_version_id=GOOGLE_ORGANIC_EXPANDED_RECIPE_ID,
        attempt_outcomes=attempt_written,
        capture_outcomes=capture_written,
        observations=observation_written,
        diagnostics=diagnostic_written,
        integrity_failures=integrity_failures,
    )


def plan_google_organic_expanded_capture(
    attempt_id: str,
    capture_id: str,
    capture: Mapping[str, object],
    parameters: Mapping[str, object],
    body: bytes | None,
) -> PlannedExpandedCapture:
    """Classify one Capture and plan its rebuildable expanded-Recipe rows."""

    classification, parsed = _classify_expanded_capture(capture, parameters, body)
    empty = _empty_expanded_planned(classification)
    if parsed is None:
        return empty
    diagnostics = tuple(
        _diagnostic(attempt_id, capture_id, item, GOOGLE_ORGANIC_EXPANDED_RECIPE_ID)
        for item in parsed.diagnostics
    )
    if classification != "observation_admitted":
        return _empty_expanded_planned(classification, diagnostics)
    try:
        return _plan_expanded_admitted(attempt_id, capture_id, parsed, diagnostics)
    except AioSourceDisagreement:
        return _empty_expanded_planned("provider_envelope_rejected", diagnostics)


def _empty_expanded_planned(
    classification: str,
    diagnostics: tuple[DerivationDiagnostic, ...] = (),
) -> PlannedExpandedCapture:
    return PlannedExpandedCapture(
        classification=classification,
        envelopes=(),
        details={table: () for table in _EXPANDED_DETAIL_CONTENT},
        aio_occurrences=(),
        paa_occurrences=(),
        top_story_occurrences=(),
        video_occurrences=(),
        sitelink_occurrences=(),
        context=None,
        diagnostics=diagnostics,
    )


def _classify_expanded_capture(
    capture: Mapping[str, object],
    parameters: Mapping[str, object],
    body: bytes | None,
) -> tuple[str, GoogleOrganicExpandedIR | None]:
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
        parsed = parse_google_organic_v2(body, parameters)
    except GoogleOrganicParseError as exc:
        if exc.code == "reconciliation_failed":
            return "reconciliation_failed", None
        return "provider_envelope_rejected", None
    if parsed.outcome is ParseClassification.PROVIDER_ERROR:
        return "provider_error", parsed
    return "observation_admitted", parsed


def _plan_expanded_admitted(
    attempt_id: str,
    capture_id: str,
    parsed: GoogleOrganicExpandedIR,
    diagnostics: tuple[DerivationDiagnostic, ...],
) -> PlannedExpandedCapture:
    recipe_id = GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
    keyword = parsed.requested_keyword
    envelopes: list[ObservationEnvelope] = []
    details: dict[str, list[dict[str, object]]] = {
        table: [] for table in _EXPANDED_DETAIL_CONTENT
    }
    aio_occurrences: list[dict[str, object]] = []
    paa_occurrences: list[dict[str, object]] = []
    top_story_occurrences: list[dict[str, object]] = []
    video_occurrences: list[dict[str, object]] = []
    sitelink_occurrences: list[dict[str, object]] = []
    for feature in parsed.feature_placements:
        identity = _expanded_feature_identity(
            keyword,
            feature.item_type,
            feature.page,
            feature.position,
            feature.rank_group,
            feature.rank_absolute,
        )
        envelopes.append(
            _expanded_envelope(capture_id, attempt_id, FEATURE_PRESENCE_KIND, identity)
        )
        details[FEATURES_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": recipe_id,
                "within_capture_identity": identity,
                "observation_kind": FEATURE_PRESENCE_KIND,
                "requested_keyword": keyword,
                "item_type": feature.item_type,
                "page": feature.page,
                "position": feature.position,
                "rank_group": feature.rank_group,
                "rank_absolute": feature.rank_absolute,
            }
        )
    for organic in parsed.organic_placements:
        identity = _expanded_ranked_identity(
            keyword,
            organic.page,
            organic.position,
            organic.rank_group,
            organic.rank_absolute,
        )
        envelopes.append(
            _expanded_envelope(
                capture_id, attempt_id, ORGANIC_PLACEMENT_V2_KIND, identity
            )
        )
        description, description_state = _field_pair(organic.description)
        website, website_state = _field_pair(organic.website_name)
        item_time, item_time_state = _field_pair(organic.organic_item_timestamp)
        details[RANKED_V2_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": recipe_id,
                "within_capture_identity": identity,
                "observation_kind": ORGANIC_PLACEMENT_V2_KIND,
                "requested_keyword": keyword,
                "page": organic.page,
                "position": organic.position,
                "rank_group": organic.rank_group,
                "rank_absolute": organic.rank_absolute,
                "url": organic.url,
                "domain": organic.domain,
                "title": organic.title,
                "description": description,
                "description_state": description_state,
                "website_name": website,
                "website_name_state": website_state,
                "organic_item_timestamp": item_time,
                "organic_item_timestamp_state": item_time_state,
                "links_state": organic.links_state.value,
                "links_count": organic.links_count,
            }
        )
    if parsed.ai_overview is not None:
        aio = parsed.ai_overview
        identity = _expanded_identity(AIO_PRESENCE_KIND, {"requested_keyword": keyword})
        envelopes.append(
            _expanded_envelope(capture_id, attempt_id, AIO_PRESENCE_KIND, identity)
        )
        details[AIO_PRESENCE_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": recipe_id,
                "within_capture_identity": identity,
                "observation_kind": AIO_PRESENCE_KIND,
                "requested_keyword": keyword,
                "asynchronous_ai_overview": aio.asynchronous_ai_overview,
                "page": aio.page,
                "position": aio.position,
                "rank_group": aio.rank_group,
                "rank_absolute": aio.rank_absolute,
            }
        )
    grouped = _group_aio_sources(parsed.ai_overview_sources)
    for (locus, url), sources in grouped.items():
        identity = _expanded_identity(
            AIO_SOURCE_KIND,
            {"locus": locus, "requested_keyword": keyword, "url": url},
        )
        first = sources[0]
        domain, domain_state = _field_pair(first.domain)
        title, title_state = _field_pair(first.title)
        source, source_state = _field_pair(first.source)
        envelopes.append(
            _expanded_envelope(capture_id, attempt_id, AIO_SOURCE_KIND, identity)
        )
        details[AIO_SOURCES_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": recipe_id,
                "within_capture_identity": identity,
                "observation_kind": AIO_SOURCE_KIND,
                "requested_keyword": keyword,
                "locus": locus,
                "url": url,
                "domain": domain,
                "domain_state": domain_state,
                "title": title,
                "title_state": title_state,
                "source": source,
                "source_state": source_state,
            }
        )
        for item in sources:
            aio_occurrences.append(
                {
                    "capture_id": capture_id,
                    "derivation_version_id": recipe_id,
                    "within_capture_identity": identity,
                    "observation_kind": AIO_SOURCE_KIND,
                    "locus": item.locus,
                    "element_index": item.element_index,
                    "reference_index": item.reference_index,
                }
            )
    questions = _group_paa_questions(parsed.related_questions)
    for title, rows in questions.items():
        identity = _expanded_identity(
            RELATED_QUESTION_KIND,
            {"requested_keyword": keyword, "title": title},
        )
        envelopes.append(
            _expanded_envelope(capture_id, attempt_id, RELATED_QUESTION_KIND, identity)
        )
        details[QUESTIONS_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": recipe_id,
                "within_capture_identity": identity,
                "observation_kind": RELATED_QUESTION_KIND,
                "requested_keyword": keyword,
                "title": title,
            }
        )
        for row in rows:
            paa_occurrences.append(
                {
                    "capture_id": capture_id,
                    "derivation_version_id": recipe_id,
                    "within_capture_identity": identity,
                    "observation_kind": RELATED_QUESTION_KIND,
                    "page": row.page,
                    "position": row.position,
                    "rank_group": row.rank_group,
                    "rank_absolute": row.rank_absolute,
                    "question_index": row.question_index,
                }
            )
    for query in parsed.related_queries:
        identity = _expanded_identity(
            RELATED_QUERY_KIND,
            {"query": query.query, "requested_keyword": keyword},
        )
        envelopes.append(
            _expanded_envelope(capture_id, attempt_id, RELATED_QUERY_KIND, identity)
        )
        details[QUERIES_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": recipe_id,
                "within_capture_identity": identity,
                "observation_kind": RELATED_QUERY_KIND,
                "requested_keyword": keyword,
                "query": query.query,
            }
        )
    for group in parsed.top_story_groups:
        parent_identity = _expanded_feature_identity(
            keyword,
            "top_stories",
            group.page,
            group.position,
            group.rank_group,
            group.rank_absolute,
        )
        for url, children in _group_children(
            group.children, lambda child: child.url
        ).items():
            identity = _expanded_child_identity(
                TOP_STORY_RESULT_KIND, keyword, url, group
            )
            first_child = children[0]
            child_time, child_time_state = _field_pair(
                first_child.top_story_item_timestamp
            )
            envelopes.append(
                _expanded_envelope(
                    capture_id, attempt_id, TOP_STORY_RESULT_KIND, identity
                )
            )
            details[TOP_STORY_TABLE].append(
                {
                    "capture_id": capture_id,
                    "derivation_version_id": recipe_id,
                    "within_capture_identity": identity,
                    "observation_kind": TOP_STORY_RESULT_KIND,
                    "requested_keyword": keyword,
                    "parent_item_type": "top_stories",
                    "parent_within_capture_identity": parent_identity,
                    "parent_page": group.page,
                    "parent_position": group.position,
                    "parent_rank_group": group.rank_group,
                    "parent_rank_absolute": group.rank_absolute,
                    "child_url": url,
                    "source": first_child.source,
                    "domain": first_child.domain,
                    "title": first_child.title,
                    "top_story_item_timestamp": child_time,
                    "top_story_item_timestamp_state": child_time_state,
                }
            )
            for child in children:
                top_story_occurrences.append(
                    _child_occurrence(
                        capture_id,
                        recipe_id,
                        identity,
                        TOP_STORY_RESULT_KIND,
                        child.child_index,
                    )
                )
    for video_group in parsed.video_groups:
        parent_identity = _expanded_feature_identity(
            keyword,
            "video",
            video_group.page,
            video_group.position,
            video_group.rank_group,
            video_group.rank_absolute,
        )
        for url, video_children in _group_children(
            video_group.children, lambda child: child.url
        ).items():
            identity = _expanded_child_identity(
                VIDEO_RESULT_KIND, keyword, url, video_group
            )
            first_video = video_children[0]
            video_time, video_time_state = _field_pair(first_video.video_item_timestamp)
            envelopes.append(
                _expanded_envelope(capture_id, attempt_id, VIDEO_RESULT_KIND, identity)
            )
            details[VIDEO_TABLE].append(
                {
                    "capture_id": capture_id,
                    "derivation_version_id": recipe_id,
                    "within_capture_identity": identity,
                    "observation_kind": VIDEO_RESULT_KIND,
                    "requested_keyword": keyword,
                    "parent_item_type": "video",
                    "parent_within_capture_identity": parent_identity,
                    "parent_page": video_group.page,
                    "parent_position": video_group.position,
                    "parent_rank_group": video_group.rank_group,
                    "parent_rank_absolute": video_group.rank_absolute,
                    "child_url": url,
                    "source": first_video.source,
                    "title": first_video.title,
                    "video_item_timestamp": video_time,
                    "video_item_timestamp_state": video_time_state,
                }
            )
            for video_child in video_children:
                video_occurrences.append(
                    _child_occurrence(
                        capture_id,
                        recipe_id,
                        identity,
                        VIDEO_RESULT_KIND,
                        video_child.child_index,
                    )
                )
    for organic in parsed.organic_placements:
        if not organic.sitelinks:
            continue
        parent_identity = _expanded_ranked_identity(
            keyword,
            organic.page,
            organic.position,
            organic.rank_group,
            organic.rank_absolute,
        )
        for url, links in _group_children(
            organic.sitelinks, lambda child: child.url
        ).items():
            identity = _expanded_child_identity(
                ORGANIC_SITELINK_KIND, keyword, url, organic
            )
            first_link = links[0]
            link_description, link_description_state = _field_pair(
                first_link.description
            )
            envelopes.append(
                _expanded_envelope(
                    capture_id, attempt_id, ORGANIC_SITELINK_KIND, identity
                )
            )
            details[SITELINKS_TABLE].append(
                {
                    "capture_id": capture_id,
                    "derivation_version_id": recipe_id,
                    "within_capture_identity": identity,
                    "observation_kind": ORGANIC_SITELINK_KIND,
                    "requested_keyword": keyword,
                    "parent_within_capture_identity": parent_identity,
                    "parent_page": organic.page,
                    "parent_position": organic.position,
                    "parent_rank_group": organic.rank_group,
                    "parent_rank_absolute": organic.rank_absolute,
                    "child_url": url,
                    "title": first_link.title,
                    "domain": first_link.domain,
                    "description": link_description,
                    "description_state": link_description_state,
                }
            )
            for link_child in links:
                sitelink_occurrences.append(
                    _child_occurrence(
                        capture_id,
                        recipe_id,
                        identity,
                        ORGANIC_SITELINK_KIND,
                        link_child.child_index,
                    )
                )
    frozen_details = {table: tuple(rows) for table, rows in details.items()}
    classification = (
        "observation_admitted_empty" if not envelopes else "observation_admitted"
    )
    return PlannedExpandedCapture(
        classification=classification,
        envelopes=tuple(envelopes),
        details=frozen_details,
        aio_occurrences=tuple(aio_occurrences),
        paa_occurrences=tuple(paa_occurrences),
        top_story_occurrences=tuple(top_story_occurrences),
        video_occurrences=tuple(video_occurrences),
        sitelink_occurrences=tuple(sitelink_occurrences),
        context=_expanded_context_row(attempt_id, capture_id, parsed),
        diagnostics=diagnostics,
    )


def _group_children[T](
    children: Sequence[T], key: Callable[[T], str]
) -> dict[str, list[T]]:
    """Group ordered provider children by the semantic key, preserving order.

    Repeated agreeing children collapse to one semantic fact carrying several
    occurrences. Parser-v2 has already rejected repeats that disagree.
    """

    grouped: dict[str, list[T]] = {}
    for child in children:
        grouped.setdefault(key(child), []).append(child)
    return grouped


def _child_occurrence(
    capture_id: str,
    recipe_id: str,
    identity: str,
    kind: str,
    child_index: int,
) -> dict[str, object]:
    return {
        "capture_id": capture_id,
        "derivation_version_id": recipe_id,
        "within_capture_identity": identity,
        "observation_kind": kind,
        "child_index": child_index,
    }


def _expanded_child_identity(
    kind: str,
    keyword: str,
    child_url: str,
    parent: TopStoryGroup | VideoGroup | OrganicPlacementV2,
) -> str:
    return _expanded_identity(
        kind,
        {
            "child_url": child_url,
            "parent_page": parent.page,
            "parent_position": parent.position,
            "parent_rank_absolute": parent.rank_absolute,
            "parent_rank_group": parent.rank_group,
            "requested_keyword": keyword,
        },
    )


def _expanded_feature_identity(
    keyword: str,
    item_type: str,
    page: int,
    position: str,
    rank_group: int,
    rank_absolute: int,
) -> str:
    return _expanded_identity(
        FEATURE_PRESENCE_KIND,
        {
            "item_type": item_type,
            "page": page,
            "position": position,
            "rank_absolute": rank_absolute,
            "rank_group": rank_group,
            "requested_keyword": keyword,
        },
    )


def _expanded_ranked_identity(
    keyword: str,
    page: int,
    position: str,
    rank_group: int,
    rank_absolute: int,
) -> str:
    return _expanded_identity(
        ORGANIC_PLACEMENT_V2_KIND,
        {
            "page": page,
            "position": position,
            "rank_absolute": rank_absolute,
            "rank_group": rank_group,
            "requested_keyword": keyword,
        },
    )


def _expanded_identity(kind: str, axes: Mapping[str, object]) -> str:
    return observation_identity(
        {
            "axes": dict(axes),
            "observation_kind": kind,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        GOOGLE_ORGANIC_EXPANDED_RECIPE,
    )


def _expanded_envelope(
    capture_id: str, attempt_id: str, kind: str, identity: str
) -> ObservationEnvelope:
    return ObservationEnvelope(
        capture_id=capture_id,
        attempt_id=attempt_id,
        derivation_version_id=GOOGLE_ORGANIC_EXPANDED_RECIPE_ID,
        provider=PROVIDER,
        adapter_contract=ORGANIC_ADAPTER_CONTRACT,
        observation_kind=kind,
        within_capture_identity=identity,
    )


def _expanded_context_row(
    attempt_id: str, capture_id: str, parsed: GoogleOrganicExpandedIR
) -> dict[str, object]:
    returned, returned_state = _field_pair(parsed.returned_keyword)
    se_domain, se_domain_state = _field_pair(parsed.se_domain)
    result_datetime, result_datetime_state = _field_pair(parsed.result_datetime)
    se_results, se_results_state = _field_pair(parsed.se_results_count)
    pages, pages_state = _field_pair(parsed.pages_count)
    return {
        "capture_id": capture_id,
        "derivation_version_id": GOOGLE_ORGANIC_EXPANDED_RECIPE_ID,
        "attempt_id": attempt_id,
        "requested_keyword": parsed.requested_keyword,
        "returned_keyword": returned,
        "returned_keyword_state": returned_state,
        "location_code": parsed.location_code,
        "language_code": parsed.language_code,
        "se_domain": se_domain,
        "se_domain_state": se_domain_state,
        "result_datetime": result_datetime,
        "result_datetime_state": result_datetime_state,
        "se_results_count": se_results,
        "se_results_count_state": se_results_state,
        "pages_count": pages,
        "pages_count_state": pages_state,
        "items_count": parsed.items_count,
        "item_types": list(parsed.item_types),
    }


def _group_aio_sources(
    sources: Sequence[AiOverviewSource],
) -> dict[tuple[str, str], list[AiOverviewSource]]:
    grouped: dict[tuple[str, str], list[AiOverviewSource]] = {}
    for source in sources:
        key = (source.locus, source.url)
        grouped.setdefault(key, []).append(source)
    for rows in grouped.values():
        first = _aio_testimony(rows[0])
        if any(_aio_testimony(row) != first for row in rows[1:]):
            raise AioSourceDisagreement
    return grouped


def _aio_testimony(
    source: AiOverviewSource,
) -> tuple[tuple[object, str], tuple[object, str], tuple[object, str]]:
    return (
        _field_pair(source.domain),
        _field_pair(source.title),
        _field_pair(source.source),
    )


def _group_paa_questions(
    questions: Sequence[RelatedQuestion],
) -> dict[str, list[RelatedQuestion]]:
    grouped: dict[str, list[RelatedQuestion]] = {}
    for question in questions:
        grouped.setdefault(question.title, []).append(question)
    return grouped


def _context_row(
    attempt_id: str, capture_id: str, parsed: GoogleOrganicIR
) -> dict[str, object]:
    returned, returned_state = _field_pair(parsed.returned_keyword)
    se_domain, se_domain_state = _field_pair(parsed.se_domain)
    result_datetime, result_datetime_state = _field_pair(parsed.result_datetime)
    se_results, se_results_state = _field_pair(parsed.se_results_count)
    pages, pages_state = _field_pair(parsed.pages_count)
    return {
        "capture_id": capture_id,
        "derivation_version_id": GOOGLE_ORGANIC_RECIPE_ID,
        "attempt_id": attempt_id,
        "requested_keyword": parsed.requested_keyword,
        "returned_keyword": returned,
        "returned_keyword_state": returned_state,
        "location_code": parsed.location_code,
        "language_code": parsed.language_code,
        "se_domain": se_domain,
        "se_domain_state": se_domain_state,
        "result_datetime": result_datetime,
        "result_datetime_state": result_datetime_state,
        "se_results_count": se_results,
        "se_results_count_state": se_results_state,
        "pages_count": pages,
        "pages_count_state": pages_state,
        "items_count": parsed.items_count,
        "item_types": list(parsed.item_types),
    }


def _envelope(
    capture_id: str, attempt_id: str, kind: str, identity: str
) -> ObservationEnvelope:
    return ObservationEnvelope(
        capture_id=capture_id,
        attempt_id=attempt_id,
        derivation_version_id=GOOGLE_ORGANIC_RECIPE_ID,
        provider=PROVIDER,
        adapter_contract=ORGANIC_ADAPTER_CONTRACT,
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
        GOOGLE_ORGANIC_RECIPE,
    )


def _field_pair(field: Field[Any]) -> tuple[object, str]:
    if field.state is FieldState.STATED:
        return field.value, field.state.value
    return None, field.state.value


def _diagnostic(
    attempt_id: str, capture_id: str, item: Any, recipe_id: str
) -> DerivationDiagnostic:
    return DerivationDiagnostic(
        derivation_version_id=recipe_id,
        attempt_id=attempt_id,
        capture_id=capture_id,
        diagnostic_code=item.code,
        provider_body_path=item.path,
    )


def _empty_details() -> dict[str, list[dict[str, object]]]:
    return {table: [] for table in _DETAIL_CONTENT}


def _write_attempt_outcome(
    connection: Connection[Any], attempt_id: str, recipe_id: str
) -> None:
    _write_outcome(
        connection,
        recipe_id=recipe_id,
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
            recipe_id=GOOGLE_ORGANIC_RECIPE_ID,
            attempt_id=attempt_id,
            capture_id=capture_id,
            classification=planned.classification,
            observation_count=len(planned.envelopes),
        )
        for envelope in planned.envelopes:
            write_observation_envelope(connection, envelope)
        for table, rows in planned.details.items():
            content_keys = _DETAIL_CONTENT[table]
            for row in rows:
                _write_closed_row(
                    connection,
                    table=table,
                    identity=_detail_identity(row),
                    content={key: row[key] for key in content_keys},
                )
        for row in planned.aio_occurrences:
            _write_closed_row(
                connection,
                table=AIO_OCCURRENCES_TABLE,
                identity={key: row[key] for key in _OCCURRENCE_IDENTITY[AIO_OCCURRENCES_TABLE]},
                content={},
            )
        for row in planned.paa_occurrences:
            _write_closed_row(
                connection,
                table=QUESTION_OCCURRENCES_TABLE,
                identity={
                    key: row[key] for key in _OCCURRENCE_IDENTITY[QUESTION_OCCURRENCES_TABLE]
                },
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


def _write_expanded_capture_unit(
    connection: Connection[Any],
    attempt_id: str,
    capture_id: str,
    planned: PlannedExpandedCapture,
) -> None:
    """Write one atomic expanded Capture-stage unit and prove the complete set."""

    with connection.transaction():
        _write_outcome(
            connection,
            recipe_id=GOOGLE_ORGANIC_EXPANDED_RECIPE_ID,
            attempt_id=attempt_id,
            capture_id=capture_id,
            classification=planned.classification,
            observation_count=len(planned.envelopes),
        )
        for envelope in planned.envelopes:
            write_observation_envelope(connection, envelope)
        for table, content_keys in _EXPANDED_DETAIL_CONTENT.items():
            for row in planned.details[table]:
                _write_closed_row(
                    connection,
                    table=table,
                    identity=_detail_identity(row),
                    content={key: row[key] for key in content_keys},
                )
        for row in planned.aio_occurrences:
            _write_closed_row(
                connection,
                table=AIO_OCCURRENCES_TABLE,
                identity={
                    key: row[key] for key in _OCCURRENCE_IDENTITY[AIO_OCCURRENCES_TABLE]
                },
                content={},
            )
        for row in planned.paa_occurrences:
            _write_closed_row(
                connection,
                table=QUESTION_OCCURRENCES_TABLE,
                identity={
                    key: row[key]
                    for key in _OCCURRENCE_IDENTITY[QUESTION_OCCURRENCES_TABLE]
                },
                content={},
            )
        for table, occurrences in (
            (TOP_STORY_OCCURRENCES_TABLE, planned.top_story_occurrences),
            (VIDEO_OCCURRENCES_TABLE, planned.video_occurrences),
            (SITELINK_OCCURRENCES_TABLE, planned.sitelink_occurrences),
        ):
            for row in occurrences:
                _write_closed_row(
                    connection,
                    table=table,
                    identity={key: row[key] for key in _CHILD_OCCURRENCE_IDENTITY},
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
        _assert_expanded_complete_set(connection, attempt_id, capture_id, planned)


def _assert_expanded_complete_set(
    connection: Connection[Any],
    attempt_id: str,
    capture_id: str,
    planned: PlannedExpandedCapture,
) -> None:
    recipe = GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
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
    for table in _EXPANDED_DETAIL_CONTENT:
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
    stored_aio = connection.execute(
        """
        SELECT within_capture_identity, element_index, reference_index
        FROM google_organic_aio_source_occurrences
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (recipe, capture_id),
    ).fetchall()
    intended_aio = {
        (row["within_capture_identity"], row["element_index"], row["reference_index"])
        for row in planned.aio_occurrences
    }
    if set(stored_aio) != intended_aio or len(stored_aio) != len(planned.aio_occurrences):
        raise DerivationError("complete-set mismatch: aio occurrences")
    stored_paa = connection.execute(
        """
        SELECT within_capture_identity, page, position, rank_group, rank_absolute,
               question_index
        FROM google_organic_related_question_occurrences
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (recipe, capture_id),
    ).fetchall()
    intended_paa = {
        (
            row["within_capture_identity"],
            row["page"],
            row["position"],
            row["rank_group"],
            row["rank_absolute"],
            row["question_index"],
        )
        for row in planned.paa_occurrences
    }
    if set(stored_paa) != intended_paa or len(stored_paa) != len(planned.paa_occurrences):
        raise DerivationError("complete-set mismatch: paa occurrences")
    for table, occurrences in (
        (TOP_STORY_OCCURRENCES_TABLE, planned.top_story_occurrences),
        (VIDEO_OCCURRENCES_TABLE, planned.video_occurrences),
        (SITELINK_OCCURRENCES_TABLE, planned.sitelink_occurrences),
    ):
        stored_children = connection.execute(
            sql.SQL(
                """
                SELECT within_capture_identity, child_index
                FROM {}
                WHERE derivation_version_id = %s AND capture_id = %s
                """
            ).format(sql.Identifier(table)),
            (recipe, capture_id),
        ).fetchall()
        intended_children = {
            (row["within_capture_identity"], row["child_index"])
            for row in occurrences
        }
        if set(stored_children) != intended_children or len(stored_children) != len(
            occurrences
        ):
            raise DerivationError(f"complete-set mismatch: {table}")
    _assert_expanded_child_occurrence_coverage(connection, capture_id)
    stored_context = connection.execute(
        """
        SELECT capture_id
        FROM google_organic_result_context
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


_CHILD_PARENT_TABLE: Final[dict[str, str]] = {
    TOP_STORY_OCCURRENCES_TABLE: TOP_STORY_TABLE,
    VIDEO_OCCURRENCES_TABLE: VIDEO_TABLE,
    SITELINK_OCCURRENCES_TABLE: SITELINKS_TABLE,
}


def _assert_expanded_child_occurrence_coverage(
    connection: Connection[Any], capture_id: str
) -> None:
    """Every stored semantic child must keep at least one bound occurrence row."""

    recipe = GOOGLE_ORGANIC_EXPANDED_RECIPE_ID
    for occurrence_table, parent_table in _CHILD_PARENT_TABLE.items():
        orphan = connection.execute(
            sql.SQL(
                """
                SELECT 1
                FROM {} AS parent
                WHERE parent.derivation_version_id = %s
                  AND parent.capture_id = %s
                  AND NOT EXISTS (
                        SELECT 1
                        FROM {} AS child
                        WHERE child.capture_id = parent.capture_id
                          AND child.derivation_version_id
                              = parent.derivation_version_id
                          AND child.within_capture_identity
                              = parent.within_capture_identity
                  )
                LIMIT 1
                """
            ).format(sql.Identifier(parent_table), sql.Identifier(occurrence_table)),
            (recipe, capture_id),
        ).fetchone()
        if orphan is not None:
            raise DerivationError(
                f"complete-set mismatch: {parent_table} has no subordinate occurrences"
            )


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
    recipe_id: str,
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
        (recipe_id, attempt_id, capture_id),
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
                recipe_id,
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
        sql.SQL("{} IS NOT DISTINCT FROM {}").format(sql.Identifier(key), sql.Placeholder())
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
    recipe = GOOGLE_ORGANIC_RECIPE_ID
    stored_outcomes = connection.execute(
        """
        SELECT attempt_id, classification, observation_count
        FROM outcomes
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (recipe, capture_id),
    ).fetchall()
    intended_outcomes = {
        (attempt_id, planned.classification, len(planned.envelopes))
    }
    stored_outcome_set = {
        (row[0], row[1], int(row[2])) for row in stored_outcomes
    }
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
        (item.within_capture_identity, item.observation_kind) for item in planned.envelopes
    }
    if set(stored_envelopes) != intended_envelopes or len(stored_envelopes) != len(
        planned.envelopes
    ):
        raise DerivationError("complete-set mismatch: envelopes")
    if outcome_count != len(stored_envelopes):
        raise DerivationError("complete-set mismatch: observation_count")
    for table, rows in planned.details.items():
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
    stored_aio = connection.execute(
        """
        SELECT within_capture_identity, element_index, reference_index
        FROM google_organic_aio_source_occurrences
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (recipe, capture_id),
    ).fetchall()
    intended_aio = {
        (row["within_capture_identity"], row["element_index"], row["reference_index"])
        for row in planned.aio_occurrences
    }
    if set(stored_aio) != intended_aio or len(stored_aio) != len(planned.aio_occurrences):
        raise DerivationError("complete-set mismatch: aio occurrences")
    stored_paa = connection.execute(
        """
        SELECT within_capture_identity, page, position, rank_group, rank_absolute,
               question_index
        FROM google_organic_related_question_occurrences
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (recipe, capture_id),
    ).fetchall()
    intended_paa = {
        (
            row["within_capture_identity"],
            row["page"],
            row["position"],
            row["rank_group"],
            row["rank_absolute"],
            row["question_index"],
        )
        for row in planned.paa_occurrences
    }
    if set(stored_paa) != intended_paa or len(stored_paa) != len(planned.paa_occurrences):
        raise DerivationError("complete-set mismatch: paa occurrences")
    stored_context = connection.execute(
        """
        SELECT capture_id
        FROM google_organic_result_context
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
    if set(stored_diagnostics) != intended_diagnostics or len(stored_diagnostics) != len(
        planned.diagnostics
    ):
        raise DerivationError("complete-set mismatch: diagnostics")


def _normalize_sql_value(value: object) -> object:
    if isinstance(value, list):
        return tuple(value)
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="observatory.google_organic_derive",
        description="Derive DataForSEO Google Organic rows from Evidence.",
    )
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--database-url", default=None)
    parser.add_argument(
        "--expanded",
        action="store_true",
        help=(
            "derive under the PF-18 expanded recipe instead of the accepted PF-11 "
            "recipe; this never changes the operator recipe selection"
        ),
    )
    args = parser.parse_args(argv)
    try:
        dsn = resolve_database_url(args.database_url)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    store = open_store(args.evidence_root)
    run = derive_google_organic_expanded if args.expanded else derive_google_organic
    with connect(dsn) as connection:
        summary = run(store, connection)
    sys.stdout.write(f"derivation_version {summary.derivation_version_id}\n")
    sys.stdout.write(f"attempt_outcomes {summary.attempt_outcomes}\n")
    sys.stdout.write(f"capture_outcomes {summary.capture_outcomes}\n")
    sys.stdout.write(f"observations {summary.observations}\n")
    sys.stdout.write(f"diagnostics {summary.diagnostics}\n")
    sys.stdout.write(f"integrity_failures {summary.integrity_failures}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
