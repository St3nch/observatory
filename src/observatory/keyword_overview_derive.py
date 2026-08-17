"""Derive Keyword Overview CORE Outcomes and Observations from verified Evidence."""

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
    CORE_RECIPE,
    CORE_RECIPE_ID,
    COVERAGE_KIND,
    METRICS_KIND,
    Field,
    FieldState,
    KeywordInfo,
    KeywordOverviewIR,
    KeywordOverviewParseError,
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

    if type(store) is not EvidenceStore:
        raise TypeError("derive_keyword_overview requires the concrete EvidenceStore")
    apply_schema(connection)
    registered = register_provider_recipe(connection, CORE_RECIPE)
    if registered.derivation_version_id != CORE_RECIPE_ID:
        raise DerivationError("CORE recipe identity does not match the accepted digest")
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
            cited, capture_id, parameters, parsed
        )
        if classification == "observation_admitted" and not envelopes:
            classification = "observation_admitted_empty"
        _write_capture_unit(
            connection,
            attempt_id=cited,
            capture_id=capture_id,
            classification=classification,
            envelopes=envelopes,
            coverage_rows=details[0],
            metrics_rows=details[1],
            diagnostics=diagnostics,
        )
        capture_written += 1
        observation_written += len(envelopes)
        diagnostic_written += len(diagnostics)
    return ProviderDeriveSummary(
        derivation_version_id=CORE_RECIPE_ID,
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
) -> tuple[
    list[ObservationEnvelope],
    tuple[list[dict[str, object]], list[dict[str, object]]],
    list[DerivationDiagnostic],
]:
    if parsed is None or parsed.outcome is not ParseClassification.ADMITTED:
        diagnostics = []
        if parsed is not None:
            diagnostics = [
                _diagnostic(attempt_id, capture_id, item) for item in parsed.diagnostics
            ]
        return [], ([], []), diagnostics
    envelopes: list[ObservationEnvelope] = []
    coverage_rows: list[dict[str, object]] = []
    metrics_rows: list[dict[str, object]] = []
    for item in parsed.items:
        coverage_id = _identity(COVERAGE_KIND, item.requested_keyword)
        envelopes.append(
            ObservationEnvelope(
                capture_id=capture_id,
                attempt_id=attempt_id,
                derivation_version_id=CORE_RECIPE_ID,
                provider="dataforseo",
                adapter_contract=PAID_ADAPTER_CONTRACT,
                observation_kind=COVERAGE_KIND,
                within_capture_identity=coverage_id,
            )
        )
        coverage_rows.append(_coverage_content(item, coverage_id, capture_id))
        if item.covered:
            metrics_id = _identity(METRICS_KIND, item.requested_keyword)
            envelopes.append(
                ObservationEnvelope(
                    capture_id=capture_id,
                    attempt_id=attempt_id,
                    derivation_version_id=CORE_RECIPE_ID,
                    provider="dataforseo",
                    adapter_contract=PAID_ADAPTER_CONTRACT,
                    observation_kind=METRICS_KIND,
                    within_capture_identity=metrics_id,
                )
            )
            metrics_rows.append(_metrics_content(item, metrics_id, capture_id, parameters))
    diagnostics = [_diagnostic(attempt_id, capture_id, item) for item in parsed.diagnostics]
    return envelopes, (coverage_rows, metrics_rows), diagnostics


def _identity(kind: str, requested_keyword: str) -> str:
    return observation_identity(
        {
            "axes": {"requested_keyword": requested_keyword},
            "observation_kind": kind,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        CORE_RECIPE,
    )


def _coverage_content(
    item: ReconciledKeyword, identity: str, capture_id: str
) -> dict[str, object]:
    if item.covered:
        returned = item.returned_keyword.value
        returned_state = FieldState.STATED.value
    else:
        returned = None
        returned_state = item.returned_keyword.state.value
    return {
        "capture_id": capture_id,
        "derivation_version_id": CORE_RECIPE_ID,
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
        "derivation_version_id": CORE_RECIPE_ID,
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


def _diagnostic(
    attempt_id: str, capture_id: str, item: ParseDiagnostic
) -> DerivationDiagnostic:
    return DerivationDiagnostic(
        derivation_version_id=CORE_RECIPE_ID,
        attempt_id=attempt_id,
        capture_id=capture_id,
        diagnostic_code=item.code,
        provider_body_path=item.path,
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
    *,
    attempt_id: str,
    capture_id: str,
    classification: str,
    envelopes: Sequence[ObservationEnvelope],
    coverage_rows: Sequence[Mapping[str, object]],
    metrics_rows: Sequence[Mapping[str, object]],
    diagnostics: Sequence[DerivationDiagnostic],
) -> None:
    with connection.transaction():
        _write_outcome(
            connection,
            attempt_id=attempt_id,
            capture_id=capture_id,
            classification=classification,
            observation_count=len(envelopes),
        )
        for envelope in envelopes:
            write_observation_envelope(connection, envelope)
        for row in coverage_rows:
            _write_closed_row(
                connection,
                table="keyword_overview_coverage",
                identity=_identity_keys(row),
                content={key: row[key] for key in _COVERAGE_CONTENT},
            )
        for row in metrics_rows:
            _write_closed_row(
                connection,
                table="keyword_overview_metrics",
                identity=_identity_keys(row),
                content={key: row[key] for key in _METRICS_CONTENT},
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
        (CORE_RECIPE_ID, attempt_id, capture_id),
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
            (attempt_id, capture_id, CORE_RECIPE_ID, classification, observation_count),
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
    allowed = {
        "keyword_overview_coverage": _COVERAGE_CONTENT,
        "keyword_overview_metrics": _METRICS_CONTENT,
    }
    expected = allowed.get(table)
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
        description="Derive DataForSEO Keyword Overview CORE rows from Evidence.",
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
        summary = derive_keyword_overview(store, connection)
    sys.stdout.write(f"derivation_version {summary.derivation_version_id}\n")
    sys.stdout.write(f"attempt_outcomes {summary.attempt_outcomes}\n")
    sys.stdout.write(f"capture_outcomes {summary.capture_outcomes}\n")
    sys.stdout.write(f"observations {summary.observations}\n")
    sys.stdout.write(f"diagnostics {summary.diagnostics}\n")
    sys.stdout.write(f"integrity_failures {summary.integrity_failures}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
