"""Derive Keyword Overview CORE and EXTENDED Outcomes and Observations from Evidence."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Final

from psycopg import Connection, sql

from observatory.capture_event import PAID_ADAPTER_CONTRACT
from observatory.dataforseo_keyword_overview import (
    BACKLINKS_KIND,
    CORE_RECIPE,
    CORE_RECIPE_ID,
    COVERAGE_KIND,
    EXTENDED_RECIPE,
    EXTENDED_RECIPE_ID,
    INTENT_KIND,
    METRICS_KIND,
    MONTHLY_KIND,
    PROPERTIES_KIND,
    TREND_KIND,
    Field,
    FieldState,
    KeywordInfo,
    KeywordOverviewIR,
    KeywordOverviewParseError,
    MonthlySearch,
    ParseClassification,
    ParseDiagnostic,
    ReconciledKeyword,
    parse_keyword_overview,
)
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

_COVERAGE_CONTENT: Final[tuple[str, ...]] = (
    "requested_keyword",
    "covered",
    "returned_keyword",
    "returned_keyword_state",
)
_METRICS_CONTENT: Final[tuple[str, ...]] = (
    "requested_keyword",
    "returned_keyword",
    "location_code",
    "location_code_state",
    "language_code",
    "language_code_state",
    "search_partners",
    "search_partners_state",
    "search_volume",
    "search_volume_state",
    "competition",
    "competition_state",
    "competition_level",
    "competition_level_state",
    "cpc",
    "cpc_state",
    "low_top_of_page_bid",
    "low_top_of_page_bid_state",
    "high_top_of_page_bid",
    "high_top_of_page_bid_state",
    "categories",
    "categories_state",
    "provider_update_time",
    "provider_update_time_state",
)
_MONTHLY_CONTENT: Final[tuple[str, ...]] = (
    "requested_keyword",
    "year",
    "month",
    "search_volume",
    "search_volume_state",
)
_TREND_CONTENT: Final[tuple[str, ...]] = (
    "requested_keyword",
    "monthly",
    "monthly_state",
    "quarterly",
    "quarterly_state",
    "yearly",
    "yearly_state",
)
_PROPERTIES_CONTENT: Final[tuple[str, ...]] = (
    "requested_keyword",
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
    "requested_keyword",
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
    "provider_update_time",
    "provider_update_time_state",
)
_INTENT_CONTENT: Final[tuple[str, ...]] = (
    "requested_keyword",
    "main_intent",
    "main_intent_state",
    "foreign_intent",
    "foreign_intent_state",
    "provider_update_time",
    "provider_update_time_state",
)
_TABLE_CONTENT: Final[dict[str, tuple[str, ...]]] = {
    "keyword_overview_coverage": _COVERAGE_CONTENT,
    "keyword_overview_metrics": _METRICS_CONTENT,
    "keyword_overview_monthly_search_volume": _MONTHLY_CONTENT,
    "keyword_overview_search_volume_trend": _TREND_CONTENT,
    "keyword_overview_properties": _PROPERTIES_CONTENT,
    "keyword_overview_avg_backlinks": _BACKLINKS_CONTENT,
    "keyword_overview_search_intent": _INTENT_CONTENT,
}


@dataclass(frozen=True)
class ProviderDeriveSummary:
    derivation_version_id: str
    attempt_outcomes: int
    capture_outcomes: int
    observations: int
    diagnostics: int
    integrity_failures: int


def derive_keyword_overview(
    store: EvidenceStore,
    connection: Connection[Any],
) -> ProviderDeriveSummary:
    """Derive paid Keyword Overview Evidence under the accepted CORE recipe."""

    return _derive_keyword_overview(store, connection, CORE_RECIPE, CORE_RECIPE_ID)


def derive_keyword_overview_extended(
    store: EvidenceStore,
    connection: Connection[Any],
) -> ProviderDeriveSummary:
    """Derive paid Keyword Overview Evidence under the PF-07 extended recipe."""

    return _derive_keyword_overview(
        store, connection, EXTENDED_RECIPE, EXTENDED_RECIPE_ID
    )


def _derive_keyword_overview(
    store: EvidenceStore,
    connection: Connection[Any],
    recipe: Mapping[str, object],
    recipe_id: str,
) -> ProviderDeriveSummary:
    if type(store) is not EvidenceStore:
        raise TypeError("Keyword Overview derive requires the concrete EvidenceStore")
    apply_schema(connection)
    registered = register_provider_recipe(connection, recipe)
    if registered.derivation_version_id != recipe_id:
        raise DerivationError("recipe identity does not match the accepted digest")
    attempt_written = 0
    integrity_failures = 0
    for attempt_id in store.list_committed_ids("attempts"):
        try:
            attempt = store.read_attempt(attempt_id)
        except IntegrityError:
            integrity_failures += 1
            continue
        if attempt is None or attempt.get("adapter_contract") != PAID_ADAPTER_CONTRACT:
            continue
        _write_attempt_outcome(connection, attempt_id, recipe_id)
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
        if capture is None or capture.get("adapter_contract") != PAID_ADAPTER_CONTRACT:
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
        if attempt is None or attempt.get("adapter_contract") != PAID_ADAPTER_CONTRACT:
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
        classification, parsed = _classify_capture(capture, parameters, body)
        envelopes, details, diagnostics = _planned_rows(
            cited, capture_id, parameters, parsed, recipe, recipe_id
        )
        if classification == "observation_admitted" and not envelopes:
            classification = "observation_admitted_empty"
        _write_capture_unit(
            connection,
            recipe_id=recipe_id,
            attempt_id=cited,
            capture_id=capture_id,
            classification=classification,
            envelopes=envelopes,
            details=details,
            diagnostics=diagnostics,
        )
        capture_written += 1
        observation_written += len(envelopes)
        diagnostic_written += len(diagnostics)
    return ProviderDeriveSummary(
        derivation_version_id=recipe_id,
        attempt_outcomes=attempt_written,
        capture_outcomes=capture_written,
        observations=observation_written,
        diagnostics=diagnostic_written,
        integrity_failures=integrity_failures,
    )


def _classify_capture(
    capture: Mapping[str, object],
    parameters: Mapping[str, object],
    body: bytes | None,
) -> tuple[str, KeywordOverviewIR | None]:
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
        parsed = parse_keyword_overview(body, parameters)
    except KeywordOverviewParseError as exc:
        if exc.code == "reconciliation_failed":
            return "reconciliation_failed", None
        return "provider_envelope_rejected", None
    if parsed.outcome is ParseClassification.PROVIDER_ERROR:
        return "provider_error", parsed
    return "observation_admitted", parsed


def _planned_rows(
    attempt_id: str,
    capture_id: str,
    parameters: Mapping[str, object],
    parsed: KeywordOverviewIR | None,
    recipe: Mapping[str, object],
    recipe_id: str,
) -> tuple[
    list[ObservationEnvelope],
    dict[str, list[dict[str, object]]],
    list[DerivationDiagnostic],
]:
    empty: dict[str, list[dict[str, object]]] = {table: [] for table in _TABLE_CONTENT}
    if parsed is None or parsed.outcome is not ParseClassification.ADMITTED:
        diagnostics = []
        if parsed is not None:
            diagnostics = [
                _diagnostic(attempt_id, capture_id, item, recipe_id)
                for item in parsed.diagnostics
            ]
        return [], empty, diagnostics
    envelopes: list[ObservationEnvelope] = []
    details: dict[str, list[dict[str, object]]] = {table: [] for table in _TABLE_CONTENT}
    extended = recipe_id == EXTENDED_RECIPE_ID
    for item in parsed.items:
        coverage_id = _identity(
            recipe, COVERAGE_KIND, {"requested_keyword": item.requested_keyword}
        )
        envelopes.append(
            _envelope(capture_id, attempt_id, recipe_id, COVERAGE_KIND, coverage_id)
        )
        details["keyword_overview_coverage"].append(
            _coverage_content(item, coverage_id, capture_id, recipe_id)
        )
        if not item.covered:
            continue
        metrics_id = _identity(recipe, METRICS_KIND, {"requested_keyword": item.requested_keyword})
        envelopes.append(
            _envelope(capture_id, attempt_id, recipe_id, METRICS_KIND, metrics_id)
        )
        details["keyword_overview_metrics"].append(
            _metrics_content(item, metrics_id, capture_id, parameters, recipe_id)
        )
        if not extended:
            continue
        details, envelopes = _plan_extended_kinds(
            item, capture_id, attempt_id, recipe, recipe_id, details, envelopes
        )
    diagnostics = [
        _diagnostic(attempt_id, capture_id, item, recipe_id) for item in parsed.diagnostics
    ]
    return envelopes, details, diagnostics


def _plan_extended_kinds(
    item: ReconciledKeyword,
    capture_id: str,
    attempt_id: str,
    recipe: Mapping[str, object],
    recipe_id: str,
    details: dict[str, list[dict[str, object]]],
    envelopes: list[ObservationEnvelope],
) -> tuple[dict[str, list[dict[str, object]]], list[ObservationEnvelope]]:
    keyword = item.requested_keyword
    for point in _monthly_points(item):
        monthly_id = _identity(
            recipe,
            MONTHLY_KIND,
            {"requested_keyword": keyword, "year": point.year, "month": point.month},
        )
        envelopes.append(
            _envelope(capture_id, attempt_id, recipe_id, MONTHLY_KIND, monthly_id)
        )
        details["keyword_overview_monthly_search_volume"].append(
            _monthly_content(keyword, point, monthly_id, capture_id, recipe_id)
        )
    for kind, table, builder in (
        (TREND_KIND, "keyword_overview_search_volume_trend", _trend_content),
        (PROPERTIES_KIND, "keyword_overview_properties", _properties_content),
        (BACKLINKS_KIND, "keyword_overview_avg_backlinks", _backlinks_content),
        (INTENT_KIND, "keyword_overview_search_intent", _intent_content),
    ):
        identity = _identity(recipe, kind, {"requested_keyword": keyword})
        envelopes.append(_envelope(capture_id, attempt_id, recipe_id, kind, identity))
        details[table].append(builder(item, identity, capture_id, recipe_id))
    return details, envelopes


def _envelope(
    capture_id: str,
    attempt_id: str,
    recipe_id: str,
    kind: str,
    identity: str,
) -> ObservationEnvelope:
    return ObservationEnvelope(
        capture_id=capture_id,
        attempt_id=attempt_id,
        derivation_version_id=recipe_id,
        provider="dataforseo",
        adapter_contract=PAID_ADAPTER_CONTRACT,
        observation_kind=kind,
        within_capture_identity=identity,
    )


def _identity(
    recipe: Mapping[str, object], kind: str, axes: Mapping[str, object]
) -> str:
    return observation_identity(
        {
            "axes": dict(axes),
            "observation_kind": kind,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        recipe,
    )


def _coverage_content(
    item: ReconciledKeyword, identity: str, capture_id: str, recipe_id: str
) -> dict[str, object]:
    if item.covered:
        returned = item.returned_keyword.value
        returned_state = FieldState.STATED.value
    else:
        returned = None
        returned_state = item.returned_keyword.state.value
    return {
        "capture_id": capture_id,
        "derivation_version_id": recipe_id,
        "within_capture_identity": identity,
        "observation_kind": COVERAGE_KIND,
        "requested_keyword": item.requested_keyword,
        "covered": item.covered,
        "returned_keyword": returned,
        "returned_keyword_state": returned_state,
    }


def _metrics_content(
    item: ReconciledKeyword,
    identity: str,
    capture_id: str,
    parameters: Mapping[str, object],
    recipe_id: str,
) -> dict[str, object]:
    info = item.keyword_info
    keyword_info = info.value if info.state is FieldState.STATED else None
    location_code = parameters.get("location_code")
    language_code = parameters.get("language_code")
    if not isinstance(location_code, int) or isinstance(location_code, bool):
        raise DerivationError("Attempt location_code is required request context")
    if not isinstance(language_code, str):
        raise DerivationError("Attempt language_code is required request context")
    return {
        "capture_id": capture_id,
        "derivation_version_id": recipe_id,
        "within_capture_identity": identity,
        "observation_kind": METRICS_KIND,
        "requested_keyword": item.requested_keyword,
        "returned_keyword": item.returned_keyword.value,
        "location_code": location_code,
        "location_code_state": FieldState.STATED.value,
        "language_code": language_code,
        "language_code_state": FieldState.STATED.value,
        "search_partners": _field_pair(item.search_partners)[0],
        "search_partners_state": _field_pair(item.search_partners)[1],
        "search_volume": _info_int(keyword_info, "search_volume")[0],
        "search_volume_state": _info_int(keyword_info, "search_volume")[1],
        "competition": _info_decimal(keyword_info, "competition")[0],
        "competition_state": _info_decimal(keyword_info, "competition")[1],
        "competition_level": _info_text(keyword_info, "competition_level")[0],
        "competition_level_state": _info_text(keyword_info, "competition_level")[1],
        "cpc": _info_decimal(keyword_info, "cpc")[0],
        "cpc_state": _info_decimal(keyword_info, "cpc")[1],
        "low_top_of_page_bid": _info_decimal(keyword_info, "low_top_of_page_bid")[0],
        "low_top_of_page_bid_state": _info_decimal(keyword_info, "low_top_of_page_bid")[1],
        "high_top_of_page_bid": _info_decimal(keyword_info, "high_top_of_page_bid")[0],
        "high_top_of_page_bid_state": _info_decimal(keyword_info, "high_top_of_page_bid")[1],
        "categories": _info_categories(keyword_info)[0],
        "categories_state": _info_categories(keyword_info)[1],
        "provider_update_time": _info_text(keyword_info, "last_updated_time")[0],
        "provider_update_time_state": _info_text(keyword_info, "last_updated_time")[1],
    }


def _info_int(info: KeywordInfo | None, name: str) -> tuple[object, str]:
    if info is None:
        return None, FieldState.ABSENT.value
    return _field_pair(getattr(info, name))


def _info_decimal(info: KeywordInfo | None, name: str) -> tuple[object, str]:
    if info is None:
        return None, FieldState.ABSENT.value
    return _field_pair(getattr(info, name))


def _info_text(info: KeywordInfo | None, name: str) -> tuple[object, str]:
    if info is None:
        return None, FieldState.ABSENT.value
    return _field_pair(getattr(info, name))


def _info_categories(info: KeywordInfo | None) -> tuple[object, str]:
    if info is None:
        return None, FieldState.ABSENT.value
    value, state = _field_pair(info.categories)
    if isinstance(value, tuple):
        return list(value), state
    return value, state


def _field_pair(field: Field[Any]) -> tuple[object, str]:
    if field.state is FieldState.STATED:
        return field.value, field.state.value
    return None, field.state.value


def _array_pair(field: Field[Any]) -> tuple[object, str]:
    value, state = _field_pair(field)
    if isinstance(value, tuple):
        return list(value), state
    return value, state


def _monthly_points(item: ReconciledKeyword) -> tuple[MonthlySearch, ...]:
    info = item.keyword_info
    if info.state is not FieldState.STATED or info.value is None:
        return ()
    monthly = info.value.monthly_searches
    if monthly.state is not FieldState.STATED or monthly.value is None:
        return ()
    return monthly.value


def _monthly_content(
    keyword: str,
    point: MonthlySearch,
    identity: str,
    capture_id: str,
    recipe_id: str,
) -> dict[str, object]:
    return {
        "capture_id": capture_id,
        "derivation_version_id": recipe_id,
        "within_capture_identity": identity,
        "observation_kind": MONTHLY_KIND,
        "requested_keyword": keyword,
        "year": point.year,
        "month": point.month,
        "search_volume": point.search_volume,
        "search_volume_state": FieldState.STATED.value,
    }


def _nested_field(parent: Field[Any], name: str) -> Field[Any]:
    if parent.state is not FieldState.STATED or parent.value is None:
        return Field(parent.state)
    nested = getattr(parent.value, name)
    if not isinstance(nested, Field):
        raise DerivationError(f"typed IR field {name} is missing")
    return nested


def _trend_content(
    item: ReconciledKeyword, identity: str, capture_id: str, recipe_id: str
) -> dict[str, object]:
    trend = _nested_field(item.keyword_info, "search_volume_trend")
    monthly = _nested_field(trend, "monthly")
    quarterly = _nested_field(trend, "quarterly")
    yearly = _nested_field(trend, "yearly")
    return {
        "capture_id": capture_id,
        "derivation_version_id": recipe_id,
        "within_capture_identity": identity,
        "observation_kind": TREND_KIND,
        "requested_keyword": item.requested_keyword,
        "monthly": _field_pair(monthly)[0],
        "monthly_state": _field_pair(monthly)[1],
        "quarterly": _field_pair(quarterly)[0],
        "quarterly_state": _field_pair(quarterly)[1],
        "yearly": _field_pair(yearly)[0],
        "yearly_state": _field_pair(yearly)[1],
    }


def _properties_content(
    item: ReconciledKeyword, identity: str, capture_id: str, recipe_id: str
) -> dict[str, object]:
    props = item.keyword_properties
    return {
        "capture_id": capture_id,
        "derivation_version_id": recipe_id,
        "within_capture_identity": identity,
        "observation_kind": PROPERTIES_KIND,
        "requested_keyword": item.requested_keyword,
        "core_keyword": _field_pair(_nested_field(props, "core_keyword"))[0],
        "core_keyword_state": _field_pair(_nested_field(props, "core_keyword"))[1],
        "synonym_clustering_algorithm": _field_pair(
            _nested_field(props, "synonym_clustering_algorithm")
        )[0],
        "synonym_clustering_algorithm_state": _field_pair(
            _nested_field(props, "synonym_clustering_algorithm")
        )[1],
        "keyword_difficulty": _field_pair(_nested_field(props, "keyword_difficulty"))[0],
        "keyword_difficulty_state": _field_pair(_nested_field(props, "keyword_difficulty"))[1],
        "detected_language": _field_pair(_nested_field(props, "detected_language"))[0],
        "detected_language_state": _field_pair(_nested_field(props, "detected_language"))[1],
        "is_another_language": _field_pair(_nested_field(props, "is_another_language"))[0],
        "is_another_language_state": _field_pair(
            _nested_field(props, "is_another_language")
        )[1],
    }


def _backlinks_content(
    item: ReconciledKeyword, identity: str, capture_id: str, recipe_id: str
) -> dict[str, object]:
    info = item.avg_backlinks_info
    return {
        "capture_id": capture_id,
        "derivation_version_id": recipe_id,
        "within_capture_identity": identity,
        "observation_kind": BACKLINKS_KIND,
        "requested_keyword": item.requested_keyword,
        "backlinks": _field_pair(_nested_field(info, "backlinks"))[0],
        "backlinks_state": _field_pair(_nested_field(info, "backlinks"))[1],
        "dofollow": _field_pair(_nested_field(info, "dofollow"))[0],
        "dofollow_state": _field_pair(_nested_field(info, "dofollow"))[1],
        "referring_pages": _field_pair(_nested_field(info, "referring_pages"))[0],
        "referring_pages_state": _field_pair(_nested_field(info, "referring_pages"))[1],
        "referring_domains": _field_pair(_nested_field(info, "referring_domains"))[0],
        "referring_domains_state": _field_pair(_nested_field(info, "referring_domains"))[1],
        "referring_main_domains": _field_pair(_nested_field(info, "referring_main_domains"))[0],
        "referring_main_domains_state": _field_pair(
            _nested_field(info, "referring_main_domains")
        )[1],
        "rank": _field_pair(_nested_field(info, "rank"))[0],
        "rank_state": _field_pair(_nested_field(info, "rank"))[1],
        "main_domain_rank": _field_pair(_nested_field(info, "main_domain_rank"))[0],
        "main_domain_rank_state": _field_pair(_nested_field(info, "main_domain_rank"))[1],
        "provider_update_time": _field_pair(_nested_field(info, "last_updated_time"))[0],
        "provider_update_time_state": _field_pair(
            _nested_field(info, "last_updated_time")
        )[1],
    }


def _intent_content(
    item: ReconciledKeyword, identity: str, capture_id: str, recipe_id: str
) -> dict[str, object]:
    info = item.search_intent_info
    foreign = _array_pair(_nested_field(info, "foreign_intent"))
    return {
        "capture_id": capture_id,
        "derivation_version_id": recipe_id,
        "within_capture_identity": identity,
        "observation_kind": INTENT_KIND,
        "requested_keyword": item.requested_keyword,
        "main_intent": _field_pair(_nested_field(info, "main_intent"))[0],
        "main_intent_state": _field_pair(_nested_field(info, "main_intent"))[1],
        "foreign_intent": foreign[0],
        "foreign_intent_state": foreign[1],
        "provider_update_time": _field_pair(_nested_field(info, "last_updated_time"))[0],
        "provider_update_time_state": _field_pair(
            _nested_field(info, "last_updated_time")
        )[1],
    }


def _diagnostic(
    attempt_id: str, capture_id: str, item: ParseDiagnostic, recipe_id: str
) -> DerivationDiagnostic:
    return DerivationDiagnostic(
        derivation_version_id=recipe_id,
        attempt_id=attempt_id,
        capture_id=capture_id,
        diagnostic_code=item.code,
        provider_body_path=item.path,
    )


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
    *,
    recipe_id: str,
    attempt_id: str,
    capture_id: str,
    classification: str,
    envelopes: Sequence[ObservationEnvelope],
    details: Mapping[str, Sequence[Mapping[str, object]]],
    diagnostics: Sequence[DerivationDiagnostic],
) -> None:
    with connection.transaction():
        _write_outcome(
            connection,
            recipe_id=recipe_id,
            attempt_id=attempt_id,
            capture_id=capture_id,
            classification=classification,
            observation_count=len(envelopes),
        )
        for envelope in envelopes:
            write_observation_envelope(connection, envelope)
        for table, rows in details.items():
            content_keys = _TABLE_CONTENT[table]
            for row in rows:
                _write_closed_row(
                    connection,
                    table=table,
                    identity=_identity_keys(row),
                    content={key: row[key] for key in content_keys},
                )
        for diagnostic in diagnostics:
            write_derivation_diagnostic(connection, diagnostic)


def _identity_keys(row: Mapping[str, object]) -> dict[str, object]:
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
            (attempt_id, capture_id, recipe_id, classification, observation_count),
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
    expected = _TABLE_CONTENT.get(table)
    if expected is None or set(content) != set(expected):
        raise DerivationError(f"closed {table} content columns are fixed")
    identity_keys = (
        "capture_id",
        "derivation_version_id",
        "within_capture_identity",
        "observation_kind",
    )
    if set(identity) != set(identity_keys):
        raise DerivationError(f"closed {table} identity columns are fixed")
    where = sql.SQL(" AND ").join(
        sql.SQL("{} IS NOT DISTINCT FROM {}").format(sql.Identifier(key), sql.Placeholder())
        for key in identity_keys
    )
    selected = sql.SQL(", ").join(sql.Identifier(key) for key in expected)
    existing = connection.execute(
        sql.SQL("SELECT {} FROM {} WHERE {}").format(
            selected, sql.Identifier(table), where
        ),
        [identity[key] for key in identity_keys],
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
    intended = tuple(_normalize_sql_value(content[key]) for key in expected)
    found = tuple(_normalize_sql_value(item) for item in existing)
    if found != intended:
        raise DerivationError(f"conflicting {table} row")


def _normalize_sql_value(value: object) -> object:
    if isinstance(value, list):
        return tuple(value)
    if isinstance(value, Decimal):
        return value
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="observatory.keyword_overview_derive",
        description="Derive DataForSEO Keyword Overview rows from Evidence.",
    )
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--database-url", default=None)
    parser.add_argument(
        "--extended",
        action="store_true",
        help="derive under the PF-07 extended recipe instead of the CORE recipe",
    )
    args = parser.parse_args(argv)
    try:
        dsn = resolve_database_url(args.database_url)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    store = open_store(args.evidence_root)
    derive = derive_keyword_overview_extended if args.extended else derive_keyword_overview
    with connect(dsn) as connection:
        summary = derive(store, connection)
    sys.stdout.write(f"derivation_version {summary.derivation_version_id}\n")
    sys.stdout.write(f"attempt_outcomes {summary.attempt_outcomes}\n")
    sys.stdout.write(f"capture_outcomes {summary.capture_outcomes}\n")
    sys.stdout.write(f"observations {summary.observations}\n")
    sys.stdout.write(f"diagnostics {summary.diagnostics}\n")
    sys.stdout.write(f"integrity_failures {summary.integrity_failures}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
