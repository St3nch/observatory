"""Read-side assembly for DataForSEO LLM Mentions Historical admitted history."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any, Final, Literal

from psycopg import Connection
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from observatory.capture_event import (
    HISTORICAL_ADAPTER_CONTRACT,
    DocumentError,
    canonical_json,
    content_digest,
    validate_historical_http_parameters,
)
from observatory.dataforseo_ai_optimization_llm_mentions_historical import (
    MONTHLY_KIND,
    PROVIDER,
)
from observatory.evidence_store import EvidenceStore, IntegrityError
from observatory.llm_mentions_historical_derive import (
    HISTORICAL_RECIPE,
    HISTORICAL_RECIPE_ID,
    MONTHLY_TABLE,
    UNRETURNED_TABLE,
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
HISTORY_ADAPTER: Final[str] = HISTORICAL_ADAPTER_CONTRACT
IJSON_MAX: Final[int] = 9007199254740991
V1_KINDS: Final[tuple[str, ...]] = (MONTHLY_KIND,)
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
_DATE_RE: Final[re.Pattern[str]] = re.compile(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})$")
CANDIDATE_SQL: Final[str] = """
SELECT
    c.capture_id,
    c.attempt_id,
    o.classification,
    o.observation_count,
    c.requested_keyword,
    c.match_type,
    c.search_filter,
    c.search_scope,
    c.platform,
    c.location_code,
    c.language_code,
    c.date_from,
    c.date_to,
    c.items_count
FROM llm_mentions_historical_result_context AS c
LEFT JOIN outcomes AS o
  ON o.derivation_version_id = c.derivation_version_id
 AND o.attempt_id = c.attempt_id
 AND o.capture_id = c.capture_id
WHERE c.requested_keyword = %s
  AND c.derivation_version_id = %s
"""
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
        "monthly",
    }
)
_REQUEST_KEYS: Final[frozenset[str]] = frozenset(
    {
        "keyword",
        "match_type",
        "search_filter",
        "search_scope",
        "platform",
        "location_code",
        "language_code",
        "date_from",
        "date_to",
    }
)
_CONTEXT_KEYS: Final[frozenset[str]] = frozenset(
    {"items_count", "unreturned_requested_periods"}
)

_GRAIN: Final[str] = (
    "Admitted, subject-bound Historical Capture-document history under Recipe v1. "
    "This list grain is Capture documents, not Observation envelopes, monthly facts, "
    "unreturned requested periods, or provider corpus counts."
)
_EMPTY: Final[str] = (
    "Empty admitted history (total_matching 0, captures empty) means no matching "
    "admitted Capture documents under this route, keyword, and Recipe v1. It does not "
    "distinguish failed measurement from never measured, unresolved authorization, "
    "provider zero, or absence from a provider corpus."
)
_ADMITTED_EMPTY: Final[str] = (
    "observation_admitted_empty is valid subject-bearing Historical history. It means "
    "this Capture returned zero monthly Observation facts for the closed request. "
    "It is not failure, never measured, or a synthesized zero metric. "
    "unreturned_requested_periods then lists every computed requested Data Period."
)
_ORDER: Final[str] = (
    "Echo of the validated query order. Deterministic outer ordering is "
    "(request_started_at, capture_id); descending reverses that complete key "
    "before limiting. This is not provider item order, rank, or monthly Data Period order."
)
_HAS_MORE: Final[str] = (
    "True when total_matching exceeds returned_count. Discloses an omitted outer "
    "Capture-history tail. This is not pagination, a cursor, or authorization to "
    "fetch another page."
)
_COUNT: Final[str] = (
    "observation_count is Observation-envelope cardinality and equals len(monthly) "
    "and result_context.items_count under Recipe v1. It is not requested-window "
    "completeness, mention volume, or provider corpus size. observation_admitted "
    "requires count >= 1. observation_admitted_empty requires count 0."
)
_ZERO: Final[str] = (
    "A returned month with mentions 0 and ai_search_volume 0 remains an ordinary "
    "observation_admitted monthly fact. An unreturned requested month is listed only "
    "in unreturned_requested_periods and is not a synthesized zero Observation. "
    "An extra out-of-window returned month remains an ordinary monthly fact; compare "
    "year/month to request.date_from and request.date_to. No is_extra flag exists."
)
_PERIOD: Final[str] = (
    "year and month are the provider Data Period. They are not Capture time, "
    "Provider Update Time, YYYY-MM strings, or event time."
)
_TIME: Final[str] = (
    "authorized_at, request_started_at, and transport_ended_at are Observatory Attempt "
    "and Capture timestamps from verified Evidence. They must not substitute for Data Period."
)


class UnsupportedHistoricalRecipe(ProviderRecipeSelectionError):
    """Resolved Recipe is not the accepted Historical v1 identity."""


class HistoricalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    keyword: str = Field(
        min_length=1,
        description=(
            "Exact verified Attempt target keyword. Not trimmed, case-folded, "
            "normalized, or replaced by task.data echo."
        ),
    )
    match_type: Literal["word_match"]
    search_filter: Literal["include"]
    search_scope: list[Literal["answer"]] = Field(min_length=1, max_length=1)
    platform: Literal["google"]
    location_code: Literal[2840]
    language_code: Literal["en"]
    date_from: Literal["2025-08-01"] = Field(
        description="Exact Attempt date_from string. " + _PERIOD
    )
    date_to: Literal["2026-07-31"] = Field(
        description="Exact Attempt date_to string. " + _PERIOD
    )


class HistoricalCaptureOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    classification: Literal["observation_admitted", "observation_admitted_empty"] = Field(
        description=_ADMITTED_EMPTY + " " + _COUNT
    )
    observation_count: int = Field(ge=0, le=IJSON_MAX, description=_COUNT)


class HistoricalMonthlyFact(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal[
        "dataforseo.google.ai_optimization.llm_mentions_historical.monthly.v1"
    ]
    within_capture_identity: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$"
    )
    requested_keyword: str = Field(min_length=1)
    year: int = Field(ge=1, le=9999, description=_PERIOD)
    month: int = Field(ge=1, le=12, description=_PERIOD)
    mentions: int = Field(ge=0, le=IJSON_MAX, description=_ZERO)
    ai_search_volume: int = Field(ge=0, le=IJSON_MAX, description=_ZERO)


class HistoricalUnreturnedPeriod(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    year: int = Field(ge=1, le=9999, description=_PERIOD + " " + _ZERO)
    month: int = Field(ge=1, le=12, description=_PERIOD + " " + _ZERO)


class HistoricalResultContext(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    items_count: int = Field(ge=0, le=IJSON_MAX, description=_COUNT)
    unreturned_requested_periods: list[HistoricalUnreturnedPeriod] = Field(
        description=(
            "Requested Data Periods absent from returned in-window monthly facts. "
            "Not Observations, zero metrics, failures, or extra returned months. "
            + _ZERO
        )
    )


class HistoricalCapture(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    attempt_id: str = Field(
        min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$", description=_GRAIN
    )
    capture_id: str = Field(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")
    provider: Literal["dataforseo"]
    adapter_contract: Literal[
        "dataforseo-ai-optimization-llm-mentions-historical-live-paid-probe-v1"
    ]
    derivation_version_id: Literal[
        "fe3e105f3f90c667df0294a2af12e5a27492bfe6eb63a0664b5326619f62d385"
    ]
    authorized_at: str = Field(description=_TIME)
    request_started_at: str = Field(description=_TIME)
    transport_ended_at: str = Field(description=_TIME)
    request: HistoricalRequest
    capture_outcome: HistoricalCaptureOutcome
    result_context: HistoricalResultContext
    monthly: list[HistoricalMonthlyFact] = Field(description=_ZERO + " " + _PERIOD)


class HistoricalHistoryEnvelope(BaseModel):
    """Closed Historical admitted-history envelope. Nested Captures are fully typed."""

    model_config = ConfigDict(extra="forbid", strict=True)

    provider: Literal["dataforseo"] = Field(description=_GRAIN + " " + _EMPTY)
    adapter_contract: Literal[
        "dataforseo-ai-optimization-llm-mentions-historical-live-paid-probe-v1"
    ]
    requested_keyword: str = Field(min_length=1, description=_EMPTY)
    derivation_version_id: Literal[
        "fe3e105f3f90c667df0294a2af12e5a27492bfe6eb63a0664b5326619f62d385"
    ]
    recipe_resolution: Literal["selected", "pinned"]
    observation_kinds: list[str] = Field(
        min_length=1,
        max_length=1,
        json_schema_extra={
            "minItems": 1,
            "maxItems": 1,
            "prefixItems": [{"type": "string", "const": MONTHLY_KIND}],
        },
        description=(
            "Exact ordered Recipe v1 Observation kinds: one monthly kind. "
            "They do not change the list grain. " + _COUNT
        ),
    )

    @field_validator("observation_kinds")
    @classmethod
    def require_v1_kinds(cls, value: list[str]) -> list[str]:
        if value != [MONTHLY_KIND]:
            raise ValueError("observation_kinds must be the exact Historical v1 kind")
        return value

    captures: list[HistoricalCapture] = Field(
        description=(
            "Whole admitted Capture documents, including observation_admitted_empty. "
            + _ADMITTED_EMPTY
            + " "
            + _EMPTY
        )
    )
    total_matching: int = Field(ge=0, description=_GRAIN + " " + _EMPTY)
    returned_count: int = Field(ge=0)
    limit: int = Field(ge=1, le=HISTORY_LIMIT_MAX, description=_HAS_MORE)
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


def _as_str_list(value: object, name: str) -> list[str]:
    if isinstance(value, (list, tuple)) and all(isinstance(item, str) for item in value):
        return [str(item) for item in value]
    raise IntegrityError(f"{name} is missing or wrong-typed")


def _require_text(document: Mapping[str, object], key: str) -> str:
    return _as_text(document.get(key), key)


def _identity(keyword: str, year: int, month: int) -> str:
    return observation_identity(
        {
            "axes": {"requested_keyword": keyword, "year": year, "month": month},
            "observation_kind": MONTHLY_KIND,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        HISTORICAL_RECIPE,
    )


def _endpoint_month(value: str) -> tuple[int, int]:
    matched = _DATE_RE.fullmatch(value)
    if matched is None:
        raise IntegrityError("Attempt date is not YYYY-MM-DD")
    year = int(matched.group(1))
    month = int(matched.group(2))
    day = int(matched.group(3))
    try:
        date(year, month, day)
    except ValueError as exc:
        raise IntegrityError("Attempt date is not a valid calendar date") from exc
    return year, month


def requested_periods(date_from: str, date_to: str) -> tuple[tuple[int, int], ...]:
    """Inclusive calendar-month set of Attempt date_from through date_to."""

    start = _endpoint_month(date_from)
    end = _endpoint_month(date_to)
    if start > end:
        raise IntegrityError("Attempt date range is inverted")
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


def _load_validated_v1_recipe(
    connection: Connection[Any], resolved: ResolvedProviderRecipe
) -> ResolvedProviderRecipe:
    if resolved.derivation_version_id != HISTORICAL_RECIPE_ID:
        raise UnsupportedHistoricalRecipe("Historical history serves Recipe v1 only")
    if resolved.provider != HISTORY_PROVIDER or resolved.adapter_contract != HISTORY_ADAPTER:
        raise IntegrityError("resolved Recipe does not match this route")
    row = connection.execute(
        """
        SELECT provider, adapter_contract, recipe_canonical_bytes
        FROM provider_recipes
        WHERE derivation_version_id = %s
        """,
        (HISTORICAL_RECIPE_ID,),
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
    if digest != HISTORICAL_RECIPE_ID:
        raise IntegrityError("Recipe digest disagrees with derivation_version_id")
    identities = {
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
    if identities != {HISTORY_PROVIDER}:
        raise IntegrityError("Recipe provider metadata disagrees")
    if adapters != {HISTORY_ADAPTER}:
        raise IntegrityError("Recipe adapter metadata disagrees")
    if validated["observation_kinds"] != list(V1_KINDS):
        raise IntegrityError("Recipe observation kinds are not Historical v1")
    admission = validated["admission"]
    if not isinstance(admission, Mapping):
        raise IntegrityError("Recipe admission is missing")
    if admission.get("capture_outcomes") != list(V1_CAPTURE_OUTCOMES):
        raise IntegrityError("Recipe classifications are not Historical v1")
    if "observation_admitted_empty" not in admission["capture_outcomes"]:
        raise IntegrityError("Historical Recipe v1 must admit observation_admitted_empty")
    return resolved


def _attempt_request(attempt: Mapping[str, object]) -> dict[str, object]:
    parameters = attempt.get("parameters")
    if not isinstance(parameters, Mapping):
        raise IntegrityError("verified Attempt is missing parameters")
    try:
        closed = validate_historical_http_parameters(parameters)
    except DocumentError as exc:
        raise IntegrityError("verified Attempt parameters are not Historical") from exc
    target = closed["target"]
    if not isinstance(target, list) or len(target) != 1 or not isinstance(target[0], Mapping):
        raise IntegrityError("verified Attempt target is missing")
    first = target[0]
    keyword = first.get("keyword")
    if not isinstance(keyword, str) or keyword == "":
        raise IntegrityError("verified Attempt keyword is missing")
    request = {
        "keyword": keyword,
        "match_type": _as_text(first.get("match_type"), "match_type"),
        "search_filter": _as_text(first.get("search_filter"), "search_filter"),
        "search_scope": _as_str_list(first.get("search_scope"), "search_scope"),
        "platform": _as_text(closed.get("platform"), "platform"),
        "location_code": _as_int(closed.get("location_code"), "location_code"),
        "language_code": _as_text(closed.get("language_code"), "language_code"),
        "date_from": _as_text(closed.get("date_from"), "date_from"),
        "date_to": _as_text(closed.get("date_to"), "date_to"),
    }
    if set(request) != _REQUEST_KEYS:
        raise IntegrityError("Attempt request keys are not closed")
    return request


def _load_monthly(
    connection: Connection[Any],
    capture_id: str,
    attempt_id: str,
    keyword: str,
) -> list[dict[str, object]]:
    envelopes = connection.execute(
        """
        SELECT within_capture_identity, observation_kind, attempt_id, provider,
               adapter_contract
        FROM observation_envelopes
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (HISTORICAL_RECIPE_ID, capture_id),
    ).fetchall()
    envelope_keys: set[tuple[str, str]] = set()
    for row in envelopes:
        kind = str(row[1])
        if kind != MONTHLY_KIND:
            raise IntegrityError("unknown Observation kind")
        if str(row[2]) != attempt_id:
            raise IntegrityError("envelope attempt_id disagrees with verified Attempt")
        if str(row[3]) != HISTORY_PROVIDER or str(row[4]) != HISTORY_ADAPTER:
            raise IntegrityError("envelope provider or adapter disagrees")
        envelope_keys.add((str(row[0]), kind))
    rows = connection.execute(
        f"""
        SELECT within_capture_identity, observation_kind, requested_keyword,
               year, month, mentions, ai_search_volume
        FROM {MONTHLY_TABLE}
        WHERE derivation_version_id = %s AND capture_id = %s
        ORDER BY year, month, within_capture_identity
        """,
        (HISTORICAL_RECIPE_ID, capture_id),
    ).fetchall()
    monthly: list[dict[str, object]] = []
    typed_keys: set[tuple[str, str]] = set()
    seen_periods: set[tuple[int, int]] = set()
    for row in rows:
        year = _as_int(row[3], "year")
        month = _as_int(row[4], "month")
        period = (year, month)
        if period in seen_periods:
            raise IntegrityError("duplicate monthly period")
        seen_periods.add(period)
        identity = _identity(keyword, year, month)
        if (
            str(row[0]) != identity
            or str(row[1]) != MONTHLY_KIND
            or str(row[2]) != keyword
        ):
            raise IntegrityError("monthly identity disagrees")
        typed_keys.add((str(row[0]), str(row[1])))
        monthly.append(
            {
                "observation_kind": MONTHLY_KIND,
                "within_capture_identity": identity,
                "requested_keyword": keyword,
                "year": year,
                "month": month,
                "mentions": _as_int(row[5], "mentions"),
                "ai_search_volume": _as_int(row[6], "ai_search_volume"),
            }
        )
    if typed_keys != envelope_keys:
        raise IntegrityError("typed Observation keys disagree with envelopes")
    return monthly


def _load_unreturned(
    connection: Connection[Any], capture_id: str
) -> list[tuple[int, int]]:
    rows = connection.execute(
        f"""
        SELECT year, month
        FROM {UNRETURNED_TABLE}
        WHERE derivation_version_id = %s AND capture_id = %s
        ORDER BY year, month
        """,
        (HISTORICAL_RECIPE_ID, capture_id),
    ).fetchall()
    periods: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for row in rows:
        period = (_as_int(row[0], "year"), _as_int(row[1], "month"))
        if period in seen:
            raise IntegrityError("duplicate unreturned period")
        seen.add(period)
        periods.append(period)
    return periods


def _verify_capture(
    store: EvidenceStore,
    connection: Connection[Any],
    row: Sequence[object],
    requested_keyword: str,
) -> dict[str, object]:
    capture_id = _as_text(row[0], "capture_id")
    attempt_id = _as_text(row[1], "attempt_id")
    classification = row[2]
    if classification is None:
        raise IntegrityError("matching context is missing Capture Outcome")
    token = str(classification)
    if token not in ADMITTED_CLASSIFICATIONS:
        raise IntegrityError("matching context is not an admitted Historical Outcome")
    observation_count = _as_int(row[3], "observation_count")
    context_keyword = _as_text(row[4], "requested_keyword")
    if context_keyword != requested_keyword:
        raise IntegrityError("result context keyword disagrees")
    match_type = _as_text(row[5], "match_type")
    search_filter = _as_text(row[6], "search_filter")
    search_scope = _as_str_list(row[7], "search_scope")
    platform = _as_text(row[8], "platform")
    location_code = _as_int(row[9], "location_code")
    language_code = _as_text(row[10], "language_code")
    date_from = _as_text(row[11], "date_from")
    date_to = _as_text(row[12], "date_to")
    items_count = _as_int(row[13], "items_count")
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
        raise IntegrityError("derived Evidence is not Historical")
    request = _attempt_request(attempt)
    if request["keyword"] != requested_keyword:
        raise IntegrityError("Attempt keyword disagrees with history subject")
    if (
        request["keyword"] != context_keyword
        or request["match_type"] != match_type
        or request["search_filter"] != search_filter
        or request["search_scope"] != search_scope
        or request["platform"] != platform
        or request["location_code"] != location_code
        or request["language_code"] != language_code
        or request["date_from"] != date_from
        or request["date_to"] != date_to
    ):
        raise IntegrityError("Attempt request disagrees with result context")
    monthly = _load_monthly(connection, capture_id, attempt_id, requested_keyword)
    stored_unreturned = set(_load_unreturned(connection, capture_id))
    requested = set(requested_periods(str(request["date_from"]), str(request["date_to"])))
    returned_in_window = {
        (_as_int(item["year"], "year"), _as_int(item["month"], "month"))
        for item in monthly
        if (_as_int(item["year"], "year"), _as_int(item["month"], "month")) in requested
    }
    expected_unreturned = requested - returned_in_window
    if stored_unreturned != expected_unreturned:
        raise IntegrityError("unreturned period set disagrees")
    if observation_count != len(monthly) or items_count != len(monthly):
        raise IntegrityError("observation_count disagrees with monthly facts")
    if token == "observation_admitted":
        if observation_count < 1 or items_count < 1 or not monthly:
            raise IntegrityError("observation_admitted requires monthly facts")
    else:
        if observation_count != 0 or items_count != 0 or monthly:
            raise IntegrityError("observation_admitted_empty must have zero monthly facts")
        if stored_unreturned != requested:
            raise IntegrityError("admitted-empty unreturned set is incomplete")
    unreturned_payload = [
        {"year": year, "month": month} for year, month in sorted(stored_unreturned)
    ]
    result_context = {
        "items_count": items_count,
        "unreturned_requested_periods": unreturned_payload,
    }
    if set(result_context) != _CONTEXT_KEYS:
        raise IntegrityError("result_context keys are not closed")
    payload: dict[str, object] = {
        "attempt_id": attempt_id,
        "capture_id": capture_id,
        "provider": HISTORY_PROVIDER,
        "adapter_contract": HISTORY_ADAPTER,
        "derivation_version_id": HISTORICAL_RECIPE_ID,
        "authorized_at": _require_text(attempt, "authorized_at"),
        "request_started_at": _require_text(capture, "request_started_at"),
        "transport_ended_at": _require_text(capture, "transport_ended_at"),
        "request": request,
        "capture_outcome": {
            "classification": token,
            "observation_count": observation_count,
        },
        "result_context": result_context,
        "monthly": monthly,
    }
    if set(payload) != _CAPTURE_KEYS:
        raise IntegrityError("Capture keys are not closed")
    return payload


def load_llm_mentions_historical_history(
    store: EvidenceStore,
    connection: Connection[Any],
    *,
    requested_keyword: str,
    pinned_version: str | None,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble surface-explicit Historical history for one requested keyword."""

    resolved = resolve_provider_recipe(connection, HISTORY_ADAPTER, pinned_version)
    recipe = _load_validated_v1_recipe(connection, resolved)
    rows = connection.execute(
        CANDIDATE_SQL, (requested_keyword, HISTORICAL_RECIPE_ID)
    ).fetchall()
    verified: list[tuple[str, str, dict[str, object]]] = []
    seen: set[str] = set()
    for row in rows:
        capture_id = _as_text(row[0], "capture_id")
        if capture_id in seen:
            raise IntegrityError("duplicate admitted Capture candidate")
        seen.add(capture_id)
        payload = _verify_capture(store, connection, row, requested_keyword)
        verified.append((str(payload["request_started_at"]), capture_id, payload))
    reverse = order == "desc"
    verified.sort(key=lambda item: (item[0], item[1]), reverse=reverse)
    selected = [item[2] for item in verified[:limit]]
    payload = history_list_response(
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
        return HistoricalHistoryEnvelope.model_validate(payload).model_dump()
    except ValidationError as exc:
        raise IntegrityError("malformed Historical history projection") from exc
