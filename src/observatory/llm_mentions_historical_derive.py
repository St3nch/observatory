"""Derive DataForSEO LLM Mentions Historical Outcomes and Observations."""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Final

from psycopg import Connection, sql

from observatory.capture_event import (
    HISTORICAL_ADAPTER_CONTRACT,
    DocumentError,
    validate_historical_http_parameters,
)
from observatory.dataforseo_ai_optimization_llm_mentions_historical import (
    MONTHLY_KIND,
    PARSER_CONTRACT,
    PROVIDER,
    HistoricalIR,
    HistoricalParseError,
    parse_historical,
)
from observatory.dataforseo_keyword_overview import ParseClassification
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
_DATE_RE: Final[re.Pattern[str]] = re.compile(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})$")


def historical_recipe() -> dict[str, object]:
    """Return the first Historical Derivation Recipe document."""

    kinds = [
        {
            "axes": {
                "requested_keyword": "string",
                "year": "integer",
                "month": "integer",
            },
            "observation_kind": MONTHLY_KIND,
        }
    ]
    return validate_recipe(
        {
            "adapter_contract": HISTORICAL_ADAPTER_CONTRACT,
            "admission": {
                "capture_outcomes": [
                    "no_response",
                    "observation_admitted",
                    "observation_admitted_empty",
                    "provider_envelope_rejected",
                    "provider_error",
                    "reconciliation_failed",
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
                    "/items",
                    "/metrics",
                    "/result",
                    "/tasks",
                    "/tasks/data",
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
            "numeric": {"normalization": "exact_integer"},
            "observation_identity": {
                "document_schema": IDENTITY_SCHEMA,
                "document_version": IDENTITY_VERSION,
                "kinds": kinds,
            },
            "observation_kinds": [MONTHLY_KIND],
            "parser_contract": PARSER_CONTRACT,
            "provider": PROVIDER,
            "provider_update_time": {
                "inheritance": "never_from_capture_or_sibling",
                "rule": "structure_unstated",
            },
            "reconciliation": {"rule": "attempt_window_admit_all_returned_periods"},
            "schema": SCHEMA,
            "version": SCHEMA_VERSION,
        }
    )


HISTORICAL_RECIPE: Final[dict[str, object]] = historical_recipe()
HISTORICAL_RECIPE_BYTES: Final[bytes] = recipe_bytes(HISTORICAL_RECIPE)
HISTORICAL_RECIPE_ID: Final[str] = recipe_derivation_version_id(HISTORICAL_RECIPE)
MONTHLY_TABLE: Final[str] = "llm_mentions_historical_monthly"
CONTEXT_TABLE: Final[str] = "llm_mentions_historical_result_context"
UNRETURNED_TABLE: Final[str] = "llm_mentions_historical_unreturned_requested_periods"

_MONTHLY_CONTENT: Final[tuple[str, ...]] = (
    "requested_keyword",
    "year",
    "month",
    "mentions",
    "ai_search_volume",
)
_DETAIL_CONTENT: Final[dict[str, tuple[str, ...]]] = {MONTHLY_TABLE: _MONTHLY_CONTENT}
_CONTEXT_CONTENT: Final[tuple[str, ...]] = (
    "attempt_id",
    "requested_keyword",
    "match_type",
    "search_filter",
    "search_scope",
    "platform",
    "location_code",
    "language_code",
    "date_from",
    "date_to",
    "items_count",
)
_UNRETURNED_IDENTITY: Final[tuple[str, ...]] = (
    "capture_id",
    "derivation_version_id",
    "year",
    "month",
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
    context: dict[str, object] | None
    unreturned: tuple[Mapping[str, object], ...]
    diagnostics: tuple[DerivationDiagnostic, ...]


class SemanticDisagreement(Exception):
    """Same semantic identity carries conflicting field testimony."""


def derive_llm_mentions_historical(
    store: EvidenceStore,
    connection: Connection[Any],
) -> ProviderDeriveSummary:
    """Derive paid Historical Evidence under the accepted AI-16 recipe."""

    if type(store) is not EvidenceStore:
        raise TypeError("Historical derive requires the concrete EvidenceStore")
    apply_schema(connection)
    registered = register_provider_recipe(connection, HISTORICAL_RECIPE)
    if registered.derivation_version_id != HISTORICAL_RECIPE_ID:
        raise DerivationError("recipe identity does not match the accepted digest")
    attempt_written = 0
    integrity_failures = 0
    for attempt_id in store.list_committed_ids("attempts"):
        try:
            attempt = store.read_attempt(attempt_id)
        except IntegrityError:
            integrity_failures += 1
            continue
        if attempt is None or attempt.get("adapter_contract") != HISTORICAL_ADAPTER_CONTRACT:
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
        if capture is None or capture.get("adapter_contract") != HISTORICAL_ADAPTER_CONTRACT:
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
        if attempt is None or attempt.get("adapter_contract") != HISTORICAL_ADAPTER_CONTRACT:
            integrity_failures += 1
            continue
        parameters = attempt.get("parameters")
        if not isinstance(parameters, Mapping):
            integrity_failures += 1
            continue
        try:
            closed = validate_historical_http_parameters(parameters)
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
        planned = plan_historical_capture(cited, capture_id, capture, closed, body)
        _write_capture_unit(connection, cited, capture_id, planned)
        capture_written += 1
        observation_written += len(planned.envelopes)
        diagnostic_written += len(planned.diagnostics)
    return ProviderDeriveSummary(
        derivation_version_id=HISTORICAL_RECIPE_ID,
        attempt_outcomes=attempt_written,
        capture_outcomes=capture_written,
        observations=observation_written,
        diagnostics=diagnostic_written,
        integrity_failures=integrity_failures,
    )


def plan_historical_capture(
    attempt_id: str,
    capture_id: str,
    capture: Mapping[str, object],
    parameters: Mapping[str, object],
    body: bytes | None,
) -> PlannedCapture:
    """Classify one Capture and plan its rebuildable Historical rows."""

    classification, parsed = _classify_capture(capture, parameters, body)
    empty = {table: () for table in _DETAIL_CONTENT}
    if parsed is None:
        return PlannedCapture(
            classification=classification,
            envelopes=(),
            details=empty,
            context=None,
            unreturned=(),
            diagnostics=(),
        )
    if classification == "provider_error":
        return PlannedCapture(
            classification="provider_error",
            envelopes=(),
            details=empty,
            context=None,
            unreturned=(),
            diagnostics=(),
        )
    if classification != "parser_success":
        return PlannedCapture(
            classification=classification,
            envelopes=(),
            details=empty,
            context=None,
            unreturned=(),
            diagnostics=(),
        )
    try:
        return _plan_admitted(attempt_id, capture_id, parsed)
    except SemanticDisagreement:
        return PlannedCapture(
            classification="provider_envelope_rejected",
            envelopes=(),
            details=empty,
            context=None,
            unreturned=(),
            diagnostics=(),
        )


def _classify_capture(
    capture: Mapping[str, object],
    parameters: Mapping[str, object],
    body: bytes | None,
) -> tuple[str, HistoricalIR | None]:
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
        parsed = parse_historical(body, parameters)
    except HistoricalParseError:
        return "provider_envelope_rejected", None
    if parsed.outcome is ParseClassification.PROVIDER_ERROR:
        return "provider_error", parsed
    return "parser_success", parsed


def _plan_admitted(
    attempt_id: str, capture_id: str, parsed: HistoricalIR
) -> PlannedCapture:
    keyword = parsed.request.keyword
    _require_identity_text(keyword)
    if parsed.items is None or parsed.items_count is None:
        raise SemanticDisagreement
    _require_ijson(parsed.items_count)
    _require_ijson(parsed.request.location_code)
    requested = set(_requested_periods(parsed.request.date_from, parsed.request.date_to))
    envelopes: list[ObservationEnvelope] = []
    details = _empty_details()
    returned_in_window: set[tuple[int, int]] = set()
    for point in parsed.items:
        _require_ijson(point.mentions)
        _require_ijson(point.ai_search_volume)
        period = (point.year, point.month)
        if period in requested:
            returned_in_window.add(period)
        identity = _identity(
            MONTHLY_KIND,
            {
                "requested_keyword": keyword,
                "year": point.year,
                "month": point.month,
            },
        )
        envelopes.append(_envelope(capture_id, attempt_id, MONTHLY_KIND, identity))
        details[MONTHLY_TABLE].append(
            {
                "capture_id": capture_id,
                "derivation_version_id": HISTORICAL_RECIPE_ID,
                "within_capture_identity": identity,
                "observation_kind": MONTHLY_KIND,
                "requested_keyword": keyword,
                "year": point.year,
                "month": point.month,
                "mentions": point.mentions,
                "ai_search_volume": point.ai_search_volume,
            }
        )
    unreturned = tuple(
        {
            "capture_id": capture_id,
            "derivation_version_id": HISTORICAL_RECIPE_ID,
            "year": year,
            "month": month,
        }
        for year, month in sorted(requested - returned_in_window)
    )
    classification = (
        "observation_admitted_empty" if not envelopes else "observation_admitted"
    )
    return PlannedCapture(
        classification=classification,
        envelopes=tuple(envelopes),
        details={table: tuple(rows) for table, rows in details.items()},
        context=_context_row(attempt_id, capture_id, parsed),
        unreturned=unreturned,
        diagnostics=(),
    )


def _requested_periods(date_from: str, date_to: str) -> tuple[tuple[int, int], ...]:
    start = _endpoint_month(date_from)
    end = _endpoint_month(date_to)
    if start > end:
        raise SemanticDisagreement
    periods: list[tuple[int, int]] = []
    year, month = start
    while (year, month) <= end:
        periods.append((year, month))
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    return tuple(periods)


def _endpoint_month(value: str) -> tuple[int, int]:
    matched = _DATE_RE.fullmatch(value)
    if matched is None:
        raise SemanticDisagreement
    year = int(matched.group(1))
    month = int(matched.group(2))
    day = int(matched.group(3))
    try:
        date(year, month, day)
    except ValueError as exc:
        raise SemanticDisagreement from exc
    return year, month


def _require_identity_text(value: str) -> None:
    if value == "":
        raise SemanticDisagreement


def _require_ijson(value: int) -> None:
    if value < 0 or value > IJSON_MAX:
        raise SemanticDisagreement


def _context_row(
    attempt_id: str, capture_id: str, parsed: HistoricalIR
) -> dict[str, object]:
    request = parsed.request
    if parsed.items_count is None:
        raise SemanticDisagreement
    return {
        "capture_id": capture_id,
        "derivation_version_id": HISTORICAL_RECIPE_ID,
        "attempt_id": attempt_id,
        "requested_keyword": request.keyword,
        "match_type": request.match_type,
        "search_filter": request.search_filter,
        "search_scope": list(request.search_scope),
        "platform": request.platform,
        "location_code": request.location_code,
        "language_code": request.language_code,
        "date_from": request.date_from,
        "date_to": request.date_to,
        "items_count": parsed.items_count,
    }


def _envelope(
    capture_id: str, attempt_id: str, kind: str, identity: str
) -> ObservationEnvelope:
    return ObservationEnvelope(
        capture_id=capture_id,
        attempt_id=attempt_id,
        derivation_version_id=HISTORICAL_RECIPE_ID,
        provider=PROVIDER,
        adapter_contract=HISTORICAL_ADAPTER_CONTRACT,
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
        HISTORICAL_RECIPE,
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
        for row in planned.unreturned:
            _write_closed_row(
                connection,
                table=UNRETURNED_TABLE,
                identity={key: row[key] for key in _UNRETURNED_IDENTITY},
                content={},
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
        (HISTORICAL_RECIPE_ID, attempt_id, capture_id),
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
                HISTORICAL_RECIPE_ID,
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
    recipe = HISTORICAL_RECIPE_ID
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
    stored_context = connection.execute(
        """
        SELECT capture_id
        FROM llm_mentions_historical_result_context
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (recipe, capture_id),
    ).fetchall()
    intended_context = 1 if planned.context is not None else 0
    if len(stored_context) != intended_context:
        raise DerivationError("complete-set mismatch: context")
    stored_unreturned = connection.execute(
        """
        SELECT year, month
        FROM llm_mentions_historical_unreturned_requested_periods
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (recipe, capture_id),
    ).fetchall()
    intended_unreturned = {
        (_require_int(row["year"]), _require_int(row["month"])) for row in planned.unreturned
    }
    stored_unreturned_set = {(int(row[0]), int(row[1])) for row in stored_unreturned}
    if stored_unreturned_set != intended_unreturned or len(stored_unreturned) != len(
        planned.unreturned
    ):
        raise DerivationError("complete-set mismatch: unreturned")
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


def _require_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DerivationError("complete-set mismatch: unreturned")
    return value


def _normalize_sql_value(value: object) -> object:
    if isinstance(value, list):
        return tuple(value)
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="observatory.llm_mentions_historical_derive",
        description="Derive DataForSEO LLM Mentions Historical rows from Evidence.",
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
        summary = derive_llm_mentions_historical(store, connection)
    sys.stdout.write(f"derivation_version {summary.derivation_version_id}\n")
    sys.stdout.write(f"attempt_outcomes {summary.attempt_outcomes}\n")
    sys.stdout.write(f"capture_outcomes {summary.capture_outcomes}\n")
    sys.stdout.write(f"observations {summary.observations}\n")
    sys.stdout.write(f"diagnostics {summary.diagnostics}\n")
    sys.stdout.write(f"integrity_failures {summary.integrity_failures}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
