"""Derive DataForSEO Google Organic Outcomes and Observations from Evidence."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from psycopg import Connection, sql

from observatory.capture_event import ORGANIC_ADAPTER_CONTRACT
from observatory.dataforseo_google_organic import (
    AIO_PRESENCE_KIND,
    AIO_SOURCE_KIND,
    FEATURE_PRESENCE_KIND,
    GOOGLE_ORGANIC_RECIPE,
    GOOGLE_ORGANIC_RECIPE_ID,
    ORGANIC_PLACEMENT_KIND,
    RELATED_QUERY_KIND,
    RELATED_QUESTION_KIND,
    AiOverviewSource,
    GoogleOrganicIR,
    GoogleOrganicParseError,
    RelatedQuestion,
    parse_google_organic,
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
        _diagnostic(attempt_id, capture_id, item) for item in parsed.diagnostics
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
    attempt_id: str, capture_id: str, item: Any
) -> DerivationDiagnostic:
    return DerivationDiagnostic(
        derivation_version_id=GOOGLE_ORGANIC_RECIPE_ID,
        attempt_id=attempt_id,
        capture_id=capture_id,
        diagnostic_code=item.code,
        provider_body_path=item.path,
    )


def _empty_details() -> dict[str, list[dict[str, object]]]:
    return {table: [] for table in _DETAIL_CONTENT}


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
        (GOOGLE_ORGANIC_RECIPE_ID, attempt_id, capture_id),
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
                GOOGLE_ORGANIC_RECIPE_ID,
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
    args = parser.parse_args(argv)
    try:
        dsn = resolve_database_url(args.database_url)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    store = open_store(args.evidence_root)
    with connect(dsn) as connection:
        summary = derive_google_organic(store, connection)
    sys.stdout.write(f"derivation_version {summary.derivation_version_id}\n")
    sys.stdout.write(f"attempt_outcomes {summary.attempt_outcomes}\n")
    sys.stdout.write(f"capture_outcomes {summary.capture_outcomes}\n")
    sys.stdout.write(f"observations {summary.observations}\n")
    sys.stdout.write(f"diagnostics {summary.diagnostics}\n")
    sys.stdout.write(f"integrity_failures {summary.integrity_failures}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
