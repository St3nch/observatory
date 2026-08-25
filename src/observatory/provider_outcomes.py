"""Shared typing and math for provider Measurement Outcomes lists."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final, Literal

from psycopg import Connection
from pydantic import BaseModel, ConfigDict, Field

from observatory.capture_event import DocumentError, canonical_json, content_digest
from observatory.evidence_store import EvidenceStore, IntegrityError
from observatory.provider_history import HISTORY_LIMIT_DEFAULT, HISTORY_LIMIT_MAX
from observatory.provider_recipe import validate_recipe

OUTCOMES_LIMIT_DEFAULT: Final[int] = HISTORY_LIMIT_DEFAULT
OUTCOMES_LIMIT_MAX: Final[int] = HISTORY_LIMIT_MAX
OUTCOMES_ORDER: Final[tuple[str, str]] = ("asc", "desc")

ATTEMPT_CLASSIFICATION: Final[str] = "authorized_unresolved"
CAPTURE_CLASSIFICATIONS: Final[frozenset[str]] = frozenset(
    {
        "no_response",
        "observation_admitted",
        "observation_admitted_empty",
        "provider_envelope_rejected",
        "provider_error",
        "reconciliation_failed",
        "response_partial",
        "transport_complete_non_admissible",
    }
)
ADMITTED_EMPTY_OR_NON_ADMITTED: Final[frozenset[str]] = CAPTURE_CLASSIFICATIONS - {
    "observation_admitted"
}

OUTER_OUTCOMES_KEYS: Final[frozenset[str]] = frozenset(
    {
        "provider",
        "adapter_contract",
        "requested_keyword",
        "derivation_version_id",
        "recipe_resolution",
        "observation_kinds",
        "total_matching",
        "returned_count",
        "limit",
        "order",
        "has_more",
        "outcomes",
    }
)
ITEM_KEYS: Final[frozenset[str]] = frozenset(
    {
        "attempt_id",
        "capture_id",
        "provider",
        "adapter_contract",
        "derivation_version_id",
        "authorized_at",
        "request_started_at",
        "transport_ended_at",
        "transport_state",
        "request",
        "attempt_outcome",
        "capture_outcome",
    }
)
STAGE_KEYS: Final[frozenset[str]] = frozenset({"classification", "observation_count"})

AttemptClassification = Literal["authorized_unresolved"]
CaptureClassification = Literal[
    "no_response",
    "response_partial",
    "transport_complete_non_admissible",
    "provider_envelope_rejected",
    "provider_error",
    "reconciliation_failed",
    "observation_admitted",
    "observation_admitted_empty",
]

_GRAIN: Final[str] = (
    "One list item is one verified Attempt/exchange under one resolved Recipe, "
    "not one Outcome stage row, requested keyword, Observation envelope, typed fact, "
    "or provider corpus/item/page count."
)
_ORDER_DESCRIPTION: Final[str] = (
    "Echo of the validated query order. Deterministic outer ordering is "
    "(authorized_at, attempt_id); descending reverses that complete key before "
    "limiting. This is not Capture request time or provider item order."
)
_HAS_MORE_DESCRIPTION: Final[str] = (
    "True when total_matching exceeds returned_count. Discloses an omitted "
    "Attempt-document tail. This is not pagination, a cursor, or authorization to "
    "fetch another page."
)
_EMPTY_DESCRIPTION: Final[str] = (
    "Empty Outcomes (total_matching 0, outcomes empty) means no verified "
    "subject-matching Attempt Evidence under this route's provider/adapter. "
    "A matching Attempt with missing resolved-Recipe Outcome state is HTTP 409, "
    "not empty. Empty does not mean the provider reported absence, failure, "
    "unimportance, or that another surface or Recipe holds nothing."
)
_UNRESOLVED_DESCRIPTION: Final[str] = (
    "Attempt-stage classification authorized_unresolved is lifecycle vocabulary. "
    "It is not definitely unsent and is not a combined current status. "
    "capture_outcome=null means no verified Capture is held."
)
_COUNT_DESCRIPTION: Final[str] = (
    "observation_count is Observation-envelope cardinality for the exact Capture "
    "and Recipe, not provider result/corpus counts. observation_admitted requires "
    "a positive envelope count."
)
_AVAILABILITY_DESCRIPTION: Final[str] = (
    "Unrelated unreadable committed Evidence in the same root makes this route "
    "fail HTTP 409. Successfully verified foreign adapters are excluded after verify."
)


class AttemptOutcomeView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    classification: AttemptClassification = Field(description=_UNRESOLVED_DESCRIPTION)
    observation_count: int = Field(description=_COUNT_DESCRIPTION)


class CaptureOutcomeView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    classification: CaptureClassification = Field(
        description=(
            "Derived, Recipe-addressed Capture-stage Outcome. Closed set: "
            "no_response, response_partial, transport_complete_non_admissible, "
            "provider_envelope_rejected, provider_error, reconciliation_failed, "
            "observation_admitted, observation_admitted_empty. "
            + _COUNT_DESCRIPTION
        )
    )
    observation_count: int = Field(description=_COUNT_DESCRIPTION)


class KeywordOverviewOutcomeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keywords: list[str] = Field(
        description=(
            "Exact ordered 1..5 Attempt parameters.keywords. Filter membership is "
            "exact string membership, not keyword normalization or coverage."
        )
    )
    location_code: int
    language_code: str
    include_serp_info: bool
    include_clickstream_data: bool


class GoogleOrganicOutcomeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keyword: str = Field(description="Exact Attempt parameters.keyword.")
    location_code: int
    language_code: str
    depth: int
    device: str
    os: str
    group_organic_results: bool
    load_async_ai_overview: bool


class SearchMentionsOutcomeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keyword: str = Field(description="Exact Attempt parameters.target[0].keyword.")
    match_type: str = Field(description="Exact Attempt parameters.target[0].match_type.")
    search_filter: str = Field(
        description="Exact Attempt parameters.target[0].search_filter."
    )
    search_scope: list[str] = Field(
        description="Exact Attempt parameters.target[0].search_scope."
    )
    platform: str
    location_code: int
    language_code: str
    limit: int = Field(
        description="Closed Attempt request limit. Not Outcomes list pagination."
    )
    offset: int = Field(
        description=(
            "Closed Attempt request offset. Not an Outcomes cursor and not Search "
            "Mentions continuation."
        )
    )


class _OutcomeItemBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    attempt_id: str = Field(description=_GRAIN)
    capture_id: str | None
    provider: str
    adapter_contract: str
    derivation_version_id: str
    authorized_at: str
    request_started_at: str | None
    transport_ended_at: str | None
    transport_state: str | None
    attempt_outcome: AttemptOutcomeView
    capture_outcome: CaptureOutcomeView | None = Field(description=_UNRESOLVED_DESCRIPTION)


class KeywordOverviewOutcomeItem(_OutcomeItemBase):
    request: KeywordOverviewOutcomeRequest = Field(
        description="Verified Keyword Overview Attempt request testimony. No Observation facts."
    )


class GoogleOrganicOutcomeItem(_OutcomeItemBase):
    request: GoogleOrganicOutcomeRequest = Field(
        description="Verified Google Organic Attempt request testimony. No Observation facts."
    )


class SearchMentionsOutcomeItem(_OutcomeItemBase):
    request: SearchMentionsOutcomeRequest = Field(
        description=(
            "Verified Search Mentions Attempt request testimony from parameters.target[0] "
            "and sibling scalars. Items contain no Observation facts and do not follow "
            "search_after_token."
        )
    )


class _OutcomesEnvelopeBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str = Field(description=_GRAIN + " " + _EMPTY_DESCRIPTION)
    adapter_contract: str
    requested_keyword: str = Field(description=_EMPTY_DESCRIPTION)
    derivation_version_id: str
    recipe_resolution: Literal["selected", "pinned"]
    observation_kinds: list[str]
    total_matching: int = Field(
        description=(
            "Unique verified matching Attempt documents after Evidence and PostgreSQL "
            "lifecycle checks and before the output limit. Not Outcome rows, keywords, "
            "Observation envelopes, or provider corpus/item counts. "
            + _EMPTY_DESCRIPTION
            + " "
            + _AVAILABILITY_DESCRIPTION
        )
    )
    returned_count: int = Field(
        description="Number of Attempt documents in outcomes. Equals len(outcomes)."
    )
    limit: int = Field(
        description="Validated applied outer Outcomes limit. Maximum 100."
    )
    order: Literal["asc", "desc"] = Field(description=_ORDER_DESCRIPTION)
    has_more: bool = Field(description=_HAS_MORE_DESCRIPTION)


class KeywordOverviewOutcomesEnvelope(_OutcomesEnvelopeBase):
    outcomes: list[KeywordOverviewOutcomeItem] = Field(description=_GRAIN)


class GoogleOrganicOutcomesEnvelope(_OutcomesEnvelopeBase):
    outcomes: list[GoogleOrganicOutcomeItem] = Field(description=_GRAIN)


class SearchMentionsOutcomesEnvelope(_OutcomesEnvelopeBase):
    outcomes: list[SearchMentionsOutcomeItem] = Field(description=_GRAIN)


@dataclass(frozen=True)
class VerifiedStoreEvents:
    attempts: dict[str, dict[str, object]]
    captures: dict[str, dict[str, object]]
    capture_ids_by_attempt: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class StageOutcome:
    classification: str
    observation_count: int
    capture_id: str | None


@dataclass(frozen=True)
class ValidatedOutcomesRecipe:
    derivation_version_id: str
    provider: str
    adapter_contract: str
    observation_kinds: tuple[str, ...]


def _as_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


def _require_text(document: Mapping[str, object], key: str) -> str:
    value = document.get(key)
    if not isinstance(value, str) or value == "":
        raise IntegrityError(f"verified document is missing {key}")
    return value


def load_verified_store_events(store: EvidenceStore) -> VerifiedStoreEvents:
    """Verify every committed Attempt and Capture, then index Captures by parent."""

    attempt_ids = store.list_committed_ids("attempts")
    if len(attempt_ids) != len(set(attempt_ids)):
        raise IntegrityError("duplicate committed Attempt identity")
    attempts: dict[str, dict[str, object]] = {}
    for attempt_id in attempt_ids:
        attempt = store.read_attempt(attempt_id)
        if attempt is None:
            raise IntegrityError("committed Attempt Evidence is missing")
        attempts[attempt_id] = attempt

    capture_ids = store.list_committed_ids("captures")
    if len(capture_ids) != len(set(capture_ids)):
        raise IntegrityError("duplicate committed Capture identity")
    captures: dict[str, dict[str, object]] = {}
    by_attempt: dict[str, list[str]] = {}
    for capture_id in capture_ids:
        capture = store.read_capture(capture_id)
        if capture is None:
            raise IntegrityError("committed Capture Evidence is missing")
        parent = capture.get("attempt_id")
        if not isinstance(parent, str) or parent == "":
            raise IntegrityError("Capture parent is missing")
        captures[capture_id] = capture
        by_attempt.setdefault(parent, []).append(capture_id)

    for parent, ids in by_attempt.items():
        if len(ids) > 1:
            raise IntegrityError("Attempt has more than one Capture")
        if parent not in attempts:
            raise IntegrityError("Capture parent Attempt is not committed")
    return VerifiedStoreEvents(
        attempts=attempts,
        captures=captures,
        capture_ids_by_attempt={key: tuple(value) for key, value in by_attempt.items()},
    )


def load_validated_outcomes_recipe(
    connection: Connection[Any],
    *,
    derivation_version_id: str,
    resolved_provider: str,
    resolved_adapter: str,
    expected_provider: str,
    expected_adapter: str,
) -> ValidatedOutcomesRecipe:
    """Load and verify Recipe identity before any Outcomes success envelope."""

    if resolved_provider != expected_provider or resolved_adapter != expected_adapter:
        raise IntegrityError("resolved Recipe does not match this route")
    row = connection.execute(
        """
        SELECT provider, adapter_contract, recipe_canonical_bytes
        FROM provider_recipes
        WHERE derivation_version_id = %s
        """,
        (derivation_version_id,),
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
    if digest != derivation_version_id:
        raise IntegrityError("Recipe digest disagrees with derivation_version_id")
    document_provider = str(validated["provider"])
    document_adapter = str(validated["adapter_contract"])
    if len({expected_provider, resolved_provider, column_provider, document_provider}) != 1:
        raise IntegrityError("Recipe provider metadata disagrees")
    if len({expected_adapter, resolved_adapter, column_adapter, document_adapter}) != 1:
        raise IntegrityError("Recipe adapter metadata disagrees")
    kinds = validated["observation_kinds"]
    if not isinstance(kinds, list) or not all(isinstance(item, str) for item in kinds):
        raise IntegrityError("resolved recipe has no observation kinds")
    return ValidatedOutcomesRecipe(
        derivation_version_id=derivation_version_id,
        provider=document_provider,
        adapter_contract=document_adapter,
        observation_kinds=tuple(kinds),
    )


def load_stage_outcome_rows(
    connection: Connection[Any],
    *,
    attempt_id: str,
    derivation_version_id: str,
) -> list[tuple[object, ...]]:
    return list(
        connection.execute(
            """
            SELECT attempt_id, capture_id, derivation_version_id,
                   classification, observation_count
            FROM outcomes
            WHERE attempt_id = %s AND derivation_version_id = %s
            ORDER BY capture_id NULLS FIRST
            """,
            (attempt_id, derivation_version_id),
        ).fetchall()
    )


def pair_stage_outcomes(
    rows: Sequence[tuple[object, ...]],
    *,
    attempt_id: str,
    evidence_capture_id: str | None,
) -> tuple[StageOutcome, StageOutcome | None]:
    attempt_rows: list[StageOutcome] = []
    capture_rows: list[StageOutcome] = []
    for row in rows:
        if str(row[0]) != attempt_id:
            raise IntegrityError("Outcome attempt_id disagrees with Evidence")
        capture_id = row[1]
        classification = str(row[3])
        count = _as_int(row[4], "observation_count")
        if capture_id is None:
            attempt_rows.append(
                StageOutcome(
                    classification=classification,
                    observation_count=count,
                    capture_id=None,
                )
            )
            continue
        capture_rows.append(
            StageOutcome(
                classification=classification,
                observation_count=count,
                capture_id=str(capture_id),
            )
        )
    if len(attempt_rows) != 1:
        raise IntegrityError("Attempt-stage Outcome is missing or duplicated")
    attempt_stage = attempt_rows[0]
    if attempt_stage.classification != ATTEMPT_CLASSIFICATION:
        raise IntegrityError("Attempt-stage classification is not authorized_unresolved")
    if attempt_stage.observation_count != 0:
        raise IntegrityError("Attempt-stage observation_count must be zero")
    if evidence_capture_id is None:
        if capture_rows:
            raise IntegrityError("Capture-stage Outcome exists without Capture Evidence")
        return attempt_stage, None
    if len(capture_rows) != 1:
        raise IntegrityError("Capture-stage Outcome is missing or duplicated")
    capture_stage = capture_rows[0]
    if capture_stage.capture_id != evidence_capture_id:
        raise IntegrityError("Capture-stage capture_id disagrees with Evidence")
    if capture_stage.classification not in CAPTURE_CLASSIFICATIONS:
        raise IntegrityError("Capture-stage classification is not closed")
    return attempt_stage, capture_stage


def load_observation_envelope_rows(
    connection: Connection[Any],
    *,
    capture_id: str,
    derivation_version_id: str,
) -> list[tuple[object, ...]]:
    return list(
        connection.execute(
            """
            SELECT attempt_id, provider, adapter_contract, observation_kind
            FROM observation_envelopes
            WHERE capture_id = %s AND derivation_version_id = %s
            """,
            (capture_id, derivation_version_id),
        ).fetchall()
    )


def assert_capture_envelopes(
    connection: Connection[Any],
    capture_stage: StageOutcome,
    *,
    attempt_id: str,
    derivation_version_id: str,
    expected_provider: str,
    expected_adapter: str,
    observation_kinds: Sequence[str],
) -> None:
    if capture_stage.capture_id is None:
        raise IntegrityError("Capture-stage Outcome has a null Capture ID")
    rows = load_observation_envelope_rows(
        connection,
        capture_id=capture_stage.capture_id,
        derivation_version_id=derivation_version_id,
    )
    declared = set(observation_kinds)
    for row in rows:
        if str(row[0]) != attempt_id:
            raise IntegrityError("envelope attempt_id disagrees with Evidence")
        if str(row[1]) != expected_provider:
            raise IntegrityError("envelope provider disagrees with Recipe")
        if str(row[2]) != expected_adapter:
            raise IntegrityError("envelope adapter disagrees with Recipe")
        if str(row[3]) not in declared:
            raise IntegrityError("envelope observation_kind is not declared by Recipe")
    cardinality = len(rows)
    if capture_stage.classification == "observation_admitted":
        if capture_stage.observation_count < 1 or capture_stage.observation_count != cardinality:
            raise IntegrityError("admitted observation_count disagrees with envelopes")
        return
    if capture_stage.classification in ADMITTED_EMPTY_OR_NON_ADMITTED:
        if capture_stage.observation_count != 0 or cardinality != 0:
            raise IntegrityError("non-admitted observation_count must be zero")
        return
    raise IntegrityError("Capture-stage classification is not closed")


def stage_view(stage: StageOutcome) -> dict[str, object]:
    payload = {
        "classification": stage.classification,
        "observation_count": stage.observation_count,
    }
    if set(payload) != STAGE_KEYS:
        raise ValueError("stage view keys are not the accepted set")
    return payload


def project_matched_attempt(
    connection: Connection[Any],
    events: VerifiedStoreEvents,
    *,
    attempt_id: str,
    attempt: Mapping[str, object],
    recipe: ValidatedOutcomesRecipe,
    request: Mapping[str, object],
) -> dict[str, object]:
    capture_ids = events.capture_ids_by_attempt.get(attempt_id, ())
    evidence_capture_id = capture_ids[0] if capture_ids else None
    capture = (
        None if evidence_capture_id is None else events.captures[evidence_capture_id]
    )
    rows = load_stage_outcome_rows(
        connection,
        attempt_id=attempt_id,
        derivation_version_id=recipe.derivation_version_id,
    )
    attempt_stage, capture_stage = pair_stage_outcomes(
        rows,
        attempt_id=attempt_id,
        evidence_capture_id=evidence_capture_id,
    )
    if capture_stage is not None:
        assert_capture_envelopes(
            connection,
            capture_stage,
            attempt_id=attempt_id,
            derivation_version_id=recipe.derivation_version_id,
            expected_provider=recipe.provider,
            expected_adapter=recipe.adapter_contract,
            observation_kinds=recipe.observation_kinds,
        )
    return outcome_item(
        attempt_id=attempt_id,
        attempt=attempt,
        capture_id=evidence_capture_id,
        capture=capture,
        derivation_version_id=recipe.derivation_version_id,
        request=request,
        attempt_stage=attempt_stage,
        capture_stage=capture_stage,
    )


def outcome_item(
    *,
    attempt_id: str,
    attempt: Mapping[str, object],
    capture_id: str | None,
    capture: Mapping[str, object] | None,
    derivation_version_id: str,
    request: Mapping[str, object],
    attempt_stage: StageOutcome,
    capture_stage: StageOutcome | None,
) -> dict[str, object]:
    if capture_id is None:
        if capture is not None or capture_stage is not None:
            raise IntegrityError("unresolved item has Capture state")
        request_started_at = None
        transport_ended_at = None
        transport_state = None
    else:
        if capture is None or capture_stage is None:
            raise IntegrityError("Capture Evidence is missing for a captured item")
        request_started_at = _require_text(capture, "request_started_at")
        transport_ended_at = _require_text(capture, "transport_ended_at")
        transport_state = _require_text(capture, "transport_state")
        if capture.get("attempt_id") != attempt_id:
            raise IntegrityError("Capture parent does not match this Attempt")
        if capture.get("adapter_contract") != attempt.get("adapter_contract"):
            raise IntegrityError("Capture adapter does not match this Attempt")
        if capture.get("provider") != attempt.get("provider"):
            raise IntegrityError("Capture provider does not match this Attempt")
    payload: dict[str, object] = {
        "attempt_id": attempt_id,
        "capture_id": capture_id,
        "provider": _require_text(attempt, "provider"),
        "adapter_contract": _require_text(attempt, "adapter_contract"),
        "derivation_version_id": derivation_version_id,
        "authorized_at": _require_text(attempt, "authorized_at"),
        "request_started_at": request_started_at,
        "transport_ended_at": transport_ended_at,
        "transport_state": transport_state,
        "request": dict(request),
        "attempt_outcome": stage_view(attempt_stage),
        "capture_outcome": None if capture_stage is None else stage_view(capture_stage),
    }
    if set(payload) != ITEM_KEYS:
        raise ValueError("outcome item keys are not the accepted set")
    return payload


def outcomes_list_response(
    *,
    provider: str,
    adapter_contract: str,
    requested_keyword: str,
    derivation_version_id: str,
    recipe_resolution: Literal["selected", "pinned"],
    observation_kinds: Sequence[str],
    outcomes: Sequence[Mapping[str, object]],
    total_matching: int,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble outer Outcomes metadata around already-projected Attempt items."""

    if type(total_matching) is not int or isinstance(total_matching, bool):
        raise TypeError("total_matching must be an integer")
    if type(limit) is not int or isinstance(limit, bool):
        raise TypeError("limit must be an integer")
    if total_matching < 0:
        raise ValueError("total_matching must not be negative")
    if limit < 1 or limit > OUTCOMES_LIMIT_MAX:
        raise ValueError("limit is outside the accepted outer Outcomes bound")
    if order not in OUTCOMES_ORDER:
        raise ValueError("order must be asc or desc")
    projected = list(outcomes)
    returned_count = len(projected)
    if returned_count > total_matching:
        raise ValueError("returned_count exceeds total_matching")
    if returned_count > limit:
        raise ValueError("returned_count exceeds applied limit")
    payload: dict[str, object] = {
        "provider": provider,
        "adapter_contract": adapter_contract,
        "requested_keyword": requested_keyword,
        "derivation_version_id": derivation_version_id,
        "recipe_resolution": recipe_resolution,
        "observation_kinds": list(observation_kinds),
        "outcomes": projected,
        "total_matching": total_matching,
        "returned_count": returned_count,
        "limit": limit,
        "order": order,
        "has_more": total_matching > returned_count,
    }
    if set(payload) != OUTER_OUTCOMES_KEYS:
        raise ValueError("outcomes envelope keys are not the accepted 12-key set")
    return payload
