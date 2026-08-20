"""Derive DataForSEO Search Mentions Outcomes and Observations from Evidence."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from psycopg import Connection, sql

from observatory.capture_event import MENTIONS_ADAPTER_CONTRACT
from observatory.dataforseo_ai_optimization_search_mentions import (
    ITEM_KIND,
    MONTHLY_KIND,
    PROVIDER,
    SEARCH_MENTIONS_RECIPE,
    SEARCH_MENTIONS_RECIPE_ID,
    SOURCE_KIND,
    ItemOccurrence,
    SearchMentionsIR,
    SearchMentionsParseError,
    SourceOccurrence,
    parse_search_mentions,
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
RECONCILIATION_CODES: Final[frozenset[str]] = frozenset(
    {"context_mismatch", "offset_mismatch"}
)

ITEMS_TABLE: Final[str] = "search_mentions_items"
ITEM_OCCURRENCES_TABLE: Final[str] = "search_mentions_item_occurrences"
MONTHLY_TABLE: Final[str] = "search_mentions_monthly_search_volume"
MONTHLY_OCCURRENCES_TABLE: Final[str] = "search_mentions_monthly_occurrences"
SOURCES_TABLE: Final[str] = "search_mentions_sources"
SOURCE_OCCURRENCES_TABLE: Final[str] = "search_mentions_source_occurrences"
CONTEXT_TABLE: Final[str] = "search_mentions_result_context"

_ITEM_CONTENT: Final[tuple[str, ...]] = (
    "requested_keyword",
    "platform",
    "model_name",
    "location_code",
    "language_code",
    "question",
    "answer",
    "ai_search_volume",
    "is_web_search_based",
    "first_response_at",
    "last_response_at",
    "search_results_state",
    "brand_entities_state",
    "fan_out_queries_state",
)
_MONTHLY_CONTENT: Final[tuple[str, ...]] = (
    "requested_keyword",
    "model_name",
    "question",
    "year",
    "month",
    "search_volume",
)
_SOURCE_CONTENT: Final[tuple[str, ...]] = (
    "requested_keyword",
    "model_name",
    "question",
    "url",
    "title",
    "domain",
    "source_name",
    "snippet",
    "publication_date",
    "publication_date_state",
    "thumbnail",
    "thumbnail_state",
    "markdown",
    "markdown_state",
)
_DETAIL_CONTENT: Final[dict[str, tuple[str, ...]]] = {
    ITEMS_TABLE: _ITEM_CONTENT,
    MONTHLY_TABLE: _MONTHLY_CONTENT,
    SOURCES_TABLE: _SOURCE_CONTENT,
}
_ITEM_OCCURRENCE_IDENTITY: Final[tuple[str, ...]] = (
    "capture_id",
    "derivation_version_id",
    "within_capture_identity",
    "observation_kind",
    "item_index",
)
_SOURCE_OCCURRENCE_IDENTITY: Final[tuple[str, ...]] = (
    "capture_id",
    "derivation_version_id",
    "within_capture_identity",
    "observation_kind",
    "item_index",
    "rank",
)
_CONTEXT_CONTENT: Final[tuple[str, ...]] = (
    "attempt_id",
    "requested_keyword",
    "match_type",
    "search_filter",
    "search_scope",
    "platform",
    "location_code",
    "language_code",
    "request_limit",
    "request_offset",
    "total_count",
    "result_offset",
    "items_count",
    "search_after_token",
    "search_after_token_state",
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
    source_occurrences: tuple[dict[str, object], ...]
    context: dict[str, object] | None
    diagnostics: tuple[DerivationDiagnostic, ...]


class SemanticDisagreement(Exception):
    """Same semantic identity carries conflicting field testimony."""


def derive_search_mentions(
    store: EvidenceStore,
    connection: Connection[Any],
) -> ProviderDeriveSummary:
    """Derive paid Search Mentions Evidence under the accepted AI-05 recipe."""

    if type(store) is not EvidenceStore:
        raise TypeError("Search Mentions derive requires the concrete EvidenceStore")
    apply_schema(connection)
    registered = register_provider_recipe(connection, SEARCH_MENTIONS_RECIPE)
    if registered.derivation_version_id != SEARCH_MENTIONS_RECIPE_ID:
        raise DerivationError("recipe identity does not match the accepted digest")
    attempt_written = 0
    integrity_failures = 0
    for attempt_id in store.list_committed_ids("attempts"):
        try:
            attempt = store.read_attempt(attempt_id)
        except IntegrityError:
            integrity_failures += 1
            continue
        if attempt is None or attempt.get("adapter_contract") != MENTIONS_ADAPTER_CONTRACT:
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
        if capture is None or capture.get("adapter_contract") != MENTIONS_ADAPTER_CONTRACT:
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
        if attempt is None or attempt.get("adapter_contract") != MENTIONS_ADAPTER_CONTRACT:
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
        planned = plan_search_mentions_capture(cited, capture_id, capture, parameters, body)
        _write_capture_unit(connection, cited, capture_id, planned)
        capture_written += 1
        observation_written += len(planned.envelopes)
        diagnostic_written += len(planned.diagnostics)
    return ProviderDeriveSummary(
        derivation_version_id=SEARCH_MENTIONS_RECIPE_ID,
        attempt_outcomes=attempt_written,
        capture_outcomes=capture_written,
        observations=observation_written,
        diagnostics=diagnostic_written,
        integrity_failures=integrity_failures,
    )


def plan_search_mentions_capture(
    attempt_id: str,
    capture_id: str,
    capture: Mapping[str, object],
    parameters: Mapping[str, object],
    body: bytes | None,
) -> PlannedCapture:
    """Classify one Capture and plan its rebuildable Search Mentions rows."""

    classification, parsed = _classify_capture(capture, parameters, body)
    empty = {table: () for table in _DETAIL_CONTENT}
    if parsed is None:
        return PlannedCapture(
            classification=classification,
            envelopes=(),
            details=empty,
            item_occurrences=(),
            monthly_occurrences=(),
            source_occurrences=(),
            context=None,
            diagnostics=(),
        )
    if classification != "observation_admitted":
        return PlannedCapture(
            classification=classification,
            envelopes=(),
            details=empty,
            item_occurrences=(),
            monthly_occurrences=(),
            source_occurrences=(),
            context=None,
            diagnostics=(),
        )
    try:
        return _plan_admitted(attempt_id, capture_id, parsed)
    except SemanticDisagreement:
        return PlannedCapture(
            classification="provider_envelope_rejected",
            envelopes=(),
            details=empty,
            item_occurrences=(),
            monthly_occurrences=(),
            source_occurrences=(),
            context=None,
            diagnostics=(),
        )


def _classify_capture(
    capture: Mapping[str, object],
    parameters: Mapping[str, object],
    body: bytes | None,
) -> tuple[str, SearchMentionsIR | None]:
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
        parsed = parse_search_mentions(body, parameters)
    except SearchMentionsParseError as exc:
        if exc.code in RECONCILIATION_CODES:
            return "reconciliation_failed", None
        return "provider_envelope_rejected", None
    if parsed.outcome is ParseClassification.PROVIDER_ERROR:
        return "provider_error", parsed
    return "observation_admitted", parsed


def _plan_admitted(
    attempt_id: str, capture_id: str, parsed: SearchMentionsIR
) -> PlannedCapture:
    keyword = parsed.request.keyword
    envelopes: list[ObservationEnvelope] = []
    details = _empty_details()
    item_occurrences: list[dict[str, object]] = []
    monthly_occurrences: list[dict[str, object]] = []
    source_occurrences: list[dict[str, object]] = []
    grouped_items: dict[tuple[str, str], list[tuple[int, ItemOccurrence]]] = {}
    for index, item in enumerate(parsed.items):
        _require_identity_text(item.model_name)
        _require_identity_text(item.question)
        grouped_items.setdefault((item.model_name, item.question), []).append(
            (index, item)
        )
    for (model_name, question), item_rows in grouped_items.items():
        first_item = item_rows[0][1]
        testimony = _item_testimony(first_item)
        if any(_item_testimony(item) != testimony for _index, item in item_rows[1:]):
            raise SemanticDisagreement
        identity = _identity(
            ITEM_KIND,
            {
                "model_name": model_name,
                "question": question,
                "requested_keyword": keyword,
            },
        )
        envelopes.append(_envelope(capture_id, attempt_id, ITEM_KIND, identity))
        details[ITEMS_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": SEARCH_MENTIONS_RECIPE_ID,
                "within_capture_identity": identity,
                "observation_kind": ITEM_KIND,
                "requested_keyword": keyword,
                "platform": first_item.platform,
                "model_name": model_name,
                "location_code": first_item.location_code,
                "language_code": first_item.language_code,
                "question": question,
                "answer": first_item.answer,
                "ai_search_volume": first_item.ai_search_volume,
                "is_web_search_based": first_item.is_web_search_based,
                "first_response_at": first_item.first_response_at,
                "last_response_at": first_item.last_response_at,
                "search_results_state": first_item.search_results.state.value,
                "brand_entities_state": first_item.brand_entities.state.value,
                "fan_out_queries_state": first_item.fan_out_queries.state.value,
            }
        )
        for index, _item in item_rows:
            item_occurrences.append(
                {
                    "capture_id": capture_id,
                    "derivation_version_id": SEARCH_MENTIONS_RECIPE_ID,
                    "within_capture_identity": identity,
                    "observation_kind": ITEM_KIND,
                    "item_index": index,
                }
            )
    monthly_groups: dict[tuple[str, str, int, int], list[tuple[int, int]]] = {}
    for index, item in enumerate(parsed.items):
        for point in item.monthly_searches:
            key = (item.model_name, item.question, point.year, point.month)
            monthly_groups.setdefault(key, []).append((index, point.search_volume))
    for (model_name, question, year, month), monthly_rows in monthly_groups.items():
        volume = monthly_rows[0][1]
        if any(item_volume != volume for _index, item_volume in monthly_rows[1:]):
            raise SemanticDisagreement
        identity = _identity(
            MONTHLY_KIND,
            {
                "model_name": model_name,
                "month": month,
                "question": question,
                "requested_keyword": keyword,
                "year": year,
            },
        )
        envelopes.append(_envelope(capture_id, attempt_id, MONTHLY_KIND, identity))
        details[MONTHLY_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": SEARCH_MENTIONS_RECIPE_ID,
                "within_capture_identity": identity,
                "observation_kind": MONTHLY_KIND,
                "requested_keyword": keyword,
                "model_name": model_name,
                "question": question,
                "year": year,
                "month": month,
                "search_volume": volume,
            }
        )
        seen_indexes: set[int] = set()
        for index, _volume in monthly_rows:
            if index in seen_indexes:
                continue
            seen_indexes.add(index)
            monthly_occurrences.append(
                {
                    "capture_id": capture_id,
                    "derivation_version_id": SEARCH_MENTIONS_RECIPE_ID,
                    "within_capture_identity": identity,
                    "observation_kind": MONTHLY_KIND,
                    "item_index": index,
                }
            )
    source_groups: dict[tuple[str, str, str], list[tuple[int, SourceOccurrence]]] = {}
    for index, item in enumerate(parsed.items):
        for source in item.sources:
            source_groups.setdefault((item.model_name, item.question, source.url), []).append(
                (index, source)
            )
    for (model_name, question, url), source_rows in source_groups.items():
        first_source = source_rows[0][1]
        source_testimony = _source_testimony(first_source)
        if any(_source_testimony(source) != source_testimony for _index, source in source_rows[1:]):
            raise SemanticDisagreement
        identity = _identity(
            SOURCE_KIND,
            {
                "model_name": model_name,
                "question": question,
                "requested_keyword": keyword,
                "url": url,
            },
        )
        publication, publication_state = _field_pair(first_source.publication_date)
        thumbnail, thumbnail_state = _field_pair(first_source.thumbnail)
        markdown, markdown_state = _field_pair(first_source.markdown)
        envelopes.append(_envelope(capture_id, attempt_id, SOURCE_KIND, identity))
        details[SOURCES_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": SEARCH_MENTIONS_RECIPE_ID,
                "within_capture_identity": identity,
                "observation_kind": SOURCE_KIND,
                "requested_keyword": keyword,
                "model_name": model_name,
                "question": question,
                "url": url,
                "title": first_source.title,
                "domain": first_source.domain,
                "source_name": first_source.source_name,
                "snippet": first_source.snippet,
                "publication_date": publication,
                "publication_date_state": publication_state,
                "thumbnail": thumbnail,
                "thumbnail_state": thumbnail_state,
                "markdown": markdown,
                "markdown_state": markdown_state,
            }
        )
        for index, source in source_rows:
            source_occurrences.append(
                {
                    "capture_id": capture_id,
                    "derivation_version_id": SEARCH_MENTIONS_RECIPE_ID,
                    "within_capture_identity": identity,
                    "observation_kind": SOURCE_KIND,
                    "item_index": index,
                    "rank": source.rank,
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
        item_occurrences=tuple(item_occurrences),
        monthly_occurrences=tuple(monthly_occurrences),
        source_occurrences=tuple(source_occurrences),
        context=_context_row(attempt_id, capture_id, parsed),
        diagnostics=(),
    )


def _require_identity_text(value: str) -> None:
    if value == "":
        raise SemanticDisagreement


def _item_testimony(item: ItemOccurrence) -> tuple[object, ...]:
    return (
        item.platform,
        item.location_code,
        item.language_code,
        item.answer,
        item.ai_search_volume,
        item.is_web_search_based,
        item.first_response_at,
        item.last_response_at,
        item.search_results.state.value,
        item.brand_entities.state.value,
        item.fan_out_queries.state.value,
    )


def _source_testimony(source: SourceOccurrence) -> tuple[object, ...]:
    return (
        source.title,
        source.domain,
        source.source_name,
        source.snippet,
        _field_pair(source.publication_date),
        _field_pair(source.thumbnail),
        _field_pair(source.markdown),
    )


def _context_row(
    attempt_id: str, capture_id: str, parsed: SearchMentionsIR
) -> dict[str, object]:
    token, token_state = _optional_token(parsed.search_after_token)
    request = parsed.request
    if parsed.total_count is None or parsed.offset is None or parsed.items_count is None:
        raise SemanticDisagreement
    return {
        "capture_id": capture_id,
        "derivation_version_id": SEARCH_MENTIONS_RECIPE_ID,
        "attempt_id": attempt_id,
        "requested_keyword": request.keyword,
        "match_type": request.match_type,
        "search_filter": request.search_filter,
        "search_scope": list(request.search_scope),
        "platform": request.platform,
        "location_code": request.location_code,
        "language_code": request.language_code,
        "request_limit": request.limit,
        "request_offset": request.offset,
        "total_count": parsed.total_count,
        "result_offset": parsed.offset,
        "items_count": parsed.items_count,
        "search_after_token": token,
        "search_after_token_state": token_state,
    }


def _optional_token(field: Field[str] | None) -> tuple[object, str]:
    if field is None:
        raise SemanticDisagreement
    return _field_pair(field)


def _envelope(
    capture_id: str, attempt_id: str, kind: str, identity: str
) -> ObservationEnvelope:
    return ObservationEnvelope(
        capture_id=capture_id,
        attempt_id=attempt_id,
        derivation_version_id=SEARCH_MENTIONS_RECIPE_ID,
        provider=PROVIDER,
        adapter_contract=MENTIONS_ADAPTER_CONTRACT,
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
        SEARCH_MENTIONS_RECIPE,
    )


def _field_pair(field: Field[Any]) -> tuple[object, str]:
    if field.state is FieldState.STATED:
        return field.value, field.state.value
    return None, field.state.value


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
        for row in planned.item_occurrences:
            _write_closed_row(
                connection,
                table=ITEM_OCCURRENCES_TABLE,
                identity={key: row[key] for key in _ITEM_OCCURRENCE_IDENTITY},
                content={},
            )
        for row in planned.monthly_occurrences:
            _write_closed_row(
                connection,
                table=MONTHLY_OCCURRENCES_TABLE,
                identity={key: row[key] for key in _ITEM_OCCURRENCE_IDENTITY},
                content={},
            )
        for row in planned.source_occurrences:
            _write_closed_row(
                connection,
                table=SOURCE_OCCURRENCES_TABLE,
                identity={key: row[key] for key in _SOURCE_OCCURRENCE_IDENTITY},
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
        (SEARCH_MENTIONS_RECIPE_ID, attempt_id, capture_id),
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
                SEARCH_MENTIONS_RECIPE_ID,
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
    recipe = SEARCH_MENTIONS_RECIPE_ID
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
    stored_items = connection.execute(
        """
        SELECT within_capture_identity, item_index
        FROM search_mentions_item_occurrences
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (recipe, capture_id),
    ).fetchall()
    intended_items = {
        (row["within_capture_identity"], row["item_index"])
        for row in planned.item_occurrences
    }
    if set(stored_items) != intended_items or len(stored_items) != len(
        planned.item_occurrences
    ):
        raise DerivationError("complete-set mismatch: item occurrences")
    stored_monthly = connection.execute(
        """
        SELECT within_capture_identity, item_index
        FROM search_mentions_monthly_occurrences
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (recipe, capture_id),
    ).fetchall()
    intended_monthly = {
        (row["within_capture_identity"], row["item_index"])
        for row in planned.monthly_occurrences
    }
    if set(stored_monthly) != intended_monthly or len(stored_monthly) != len(
        planned.monthly_occurrences
    ):
        raise DerivationError("complete-set mismatch: monthly occurrences")
    stored_sources = connection.execute(
        """
        SELECT within_capture_identity, item_index, rank
        FROM search_mentions_source_occurrences
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (recipe, capture_id),
    ).fetchall()
    intended_sources = {
        (row["within_capture_identity"], row["item_index"], row["rank"])
        for row in planned.source_occurrences
    }
    if set(stored_sources) != intended_sources or len(stored_sources) != len(
        planned.source_occurrences
    ):
        raise DerivationError("complete-set mismatch: source occurrences")
    stored_context = connection.execute(
        """
        SELECT capture_id
        FROM search_mentions_result_context
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
        prog="observatory.search_mentions_derive",
        description="Derive DataForSEO Search Mentions rows from Evidence.",
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
        summary = derive_search_mentions(store, connection)
    sys.stdout.write(f"derivation_version {summary.derivation_version_id}\n")
    sys.stdout.write(f"attempt_outcomes {summary.attempt_outcomes}\n")
    sys.stdout.write(f"capture_outcomes {summary.capture_outcomes}\n")
    sys.stdout.write(f"observations {summary.observations}\n")
    sys.stdout.write(f"diagnostics {summary.diagnostics}\n")
    sys.stdout.write(f"integrity_failures {summary.integrity_failures}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
