"""Read-side assembly for DataForSEO Google Keyword Overview API resources."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Final, Literal

from psycopg import Connection

from observatory.capture_event import PAID_ADAPTER_CONTRACT
from observatory.dataforseo_keyword_overview import (
    BACKLINKS_KIND,
    COVERAGE_KIND,
    INTENT_KIND,
    METRICS_KIND,
    MONTHLY_KIND,
    PROPERTIES_KIND,
    TREND_KIND,
)
from observatory.evidence_store import EvidenceStore, IntegrityError
from observatory.provider_recipe_selection import (
    ResolvedProviderRecipe,
    resolve_provider_recipe,
)

HISTORY_PROVIDER: Final[str] = "dataforseo"
HISTORY_ADAPTER: Final[str] = PAID_ADAPTER_CONTRACT
HISTORY_LIMIT_DEFAULT: Final[int] = 20
HISTORY_LIMIT_MAX: Final[int] = 100



class ProviderAttemptNotFound(Exception):
    """No provider Outcome exists for this Attempt under the resolved recipe."""


@dataclass(frozen=True)
class ProviderOutcomeView:
    attempt_id: str
    capture_id: str | None
    derivation_version_id: str
    classification: str
    observation_count: int

    def as_json(self) -> dict[str, object]:
        return {
            "attempt_id": self.attempt_id,
            "capture_id": self.capture_id,
            "derivation_version_id": self.derivation_version_id,
            "classification": self.classification,
            "observation_count": self.observation_count,
        }


@dataclass(frozen=True)
class ProviderAttemptView:
    attempt_id: str
    provider: str
    adapter_contract: str
    derivation_version_id: str
    recipe_resolution: Literal["selected", "pinned"]
    attempt_outcome: ProviderOutcomeView
    capture_outcome: ProviderOutcomeView | None

    def as_json(self) -> dict[str, object]:
        return {
            "attempt_id": self.attempt_id,
            "provider": self.provider,
            "adapter_contract": self.adapter_contract,
            "derivation_version_id": self.derivation_version_id,
            "recipe_resolution": self.recipe_resolution,
            "attempt_outcome": self.attempt_outcome.as_json(),
            "capture_outcome": (
                None if self.capture_outcome is None else self.capture_outcome.as_json()
            ),
        }


def _json_field(state: object, value: object) -> dict[str, object]:
    return {"state": str(state), "value": _json_value(value)}


def _json_value(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    raise TypeError(f"unsupported provider field type: {type(value)!r}")


def _as_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


def _as_list(value: object) -> list[object] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    raise TypeError(f"unsupported array field type: {type(value)!r}")


def _require_text(document: Mapping[str, object], key: str) -> str:
    value = document.get(key)
    if not isinstance(value, str) or value == "":
        raise IntegrityError(f"verified document is missing {key}")
    return value


def _parameters(attempt: Mapping[str, object]) -> Mapping[str, object]:
    parameters = attempt.get("parameters")
    if not isinstance(parameters, Mapping):
        raise IntegrityError("verified Attempt is missing parameters")
    return parameters


def _request_context(attempt: Mapping[str, object]) -> dict[str, object]:
    parameters = _parameters(attempt)
    location = parameters.get("location_code")
    language = parameters.get("language_code")
    serp = parameters.get("include_serp_info")
    clickstream = parameters.get("include_clickstream_data")
    if type(location) is not int:
        raise IntegrityError("verified Attempt location_code is missing")
    if not isinstance(language, str):
        raise IntegrityError("verified Attempt language_code is missing")
    if type(serp) is not bool or type(clickstream) is not bool:
        raise IntegrityError("verified Attempt enrichment flags are missing")
    return {
        "location_code": location,
        "language_code": language,
        "include_serp_info": serp,
        "include_clickstream_data": clickstream,
    }


def _recipe_kinds(
    connection: Connection[Any], derivation_version_id: str
) -> tuple[str, ...]:
    row = connection.execute(
        """
        SELECT recipe_canonical_bytes
        FROM provider_recipes
        WHERE derivation_version_id = %s
        """,
        (derivation_version_id,),
    ).fetchone()
    if row is None:
        raise ProviderAttemptNotFound("resolved recipe is not registered")
    document = json.loads(bytes(row[0]).decode("utf-8"))
    kinds = document.get("observation_kinds")
    if not isinstance(kinds, list) or not all(isinstance(item, str) for item in kinds):
        raise ProviderAttemptNotFound("resolved recipe has no observation kinds")
    return tuple(kinds)


def _outcome_view(row: tuple[object, ...]) -> ProviderOutcomeView:
    capture_id = row[1]
    return ProviderOutcomeView(
        attempt_id=str(row[0]),
        capture_id=None if capture_id is None else str(capture_id),
        derivation_version_id=str(row[2]),
        classification=str(row[3]),
        observation_count=_as_int(row[4], "observation_count"),
    )


def load_provider_attempt(
    store: EvidenceStore,
    connection: Connection[Any],
    attempt: Mapping[str, object],
    attempt_id: str,
    pinned_version: str | None,
) -> ProviderAttemptView:
    """Assemble the provider Attempt audit resource from verified Evidence."""

    adapter = _require_text(attempt, "adapter_contract")
    provider = _require_text(attempt, "provider")
    if adapter != HISTORY_ADAPTER:
        raise ProviderAttemptNotFound("Attempt is not the Keyword Overview adapter")
    resolved = resolve_provider_recipe(connection, adapter, pinned_version)
    rows = connection.execute(
        """
        SELECT attempt_id, capture_id, derivation_version_id,
               classification, observation_count
        FROM outcomes
        WHERE attempt_id = %s AND derivation_version_id = %s
        ORDER BY capture_id NULLS FIRST
        """,
        (attempt_id, resolved.derivation_version_id),
    ).fetchall()
    attempt_stage: ProviderOutcomeView | None = None
    capture_stage: ProviderOutcomeView | None = None
    capture_ids: set[str] = set()
    for row in rows:
        envelope = _outcome_view(row)
        if envelope.capture_id is None:
            attempt_stage = envelope
        else:
            capture_stage = envelope
            capture_ids.add(envelope.capture_id)
    if attempt_stage is None:
        raise ProviderAttemptNotFound("no provider Outcome for this recipe")
    _verify_captures(store, attempt_id, capture_ids)
    return ProviderAttemptView(
        attempt_id=attempt_id,
        provider=provider,
        adapter_contract=adapter,
        derivation_version_id=resolved.derivation_version_id,
        recipe_resolution=resolved.resolution,
        attempt_outcome=attempt_stage,
        capture_outcome=capture_stage,
    )


def _verify_captures(
    store: EvidenceStore, attempt_id: str, capture_ids: set[str]
) -> dict[str, dict[str, object]]:
    verified: dict[str, dict[str, object]] = {}
    for capture_id in sorted(capture_ids):
        capture = store.read_capture(capture_id)
        if capture is None:
            raise IntegrityError("derived Capture Evidence is missing")
        parent = capture.get("attempt_id")
        if parent != attempt_id:
            raise IntegrityError("Capture parent does not match derived provenance")
        if capture.get("adapter_contract") != HISTORY_ADAPTER:
            raise IntegrityError("Capture adapter does not match this route")
        verified[capture_id] = capture
    return verified


def load_keyword_overview_history(
    store: EvidenceStore,
    connection: Connection[Any],
    *,
    requested_keyword: str,
    pinned_version: str | None,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble surface-explicit Keyword Overview history for one requested keyword."""

    resolved = resolve_provider_recipe(connection, HISTORY_ADAPTER, pinned_version)
    kinds = _recipe_kinds(connection, resolved.derivation_version_id)
    rows = connection.execute(
        """
        SELECT c.capture_id, e.attempt_id, o.classification, o.observation_count
        FROM keyword_overview_coverage AS c
        JOIN observation_envelopes AS e
          ON e.capture_id = c.capture_id
         AND e.derivation_version_id = c.derivation_version_id
         AND e.within_capture_identity = c.within_capture_identity
        JOIN outcomes AS o
          ON o.capture_id = c.capture_id
         AND o.derivation_version_id = c.derivation_version_id
         AND o.attempt_id = e.attempt_id
        WHERE c.requested_keyword = %s
          AND c.derivation_version_id = %s
        """,
        (requested_keyword, resolved.derivation_version_id),
    ).fetchall()
    candidates: list[
        tuple[str, str, str, str, int, dict[str, object], dict[str, object]]
    ] = []
    for row in rows:
        capture_id = str(row[0])
        attempt_id = str(row[1])
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
            or attempt.get("provider") != HISTORY_PROVIDER
        ):
            raise IntegrityError("derived Evidence is not Keyword Overview")
        candidates.append(
            (
                _require_text(capture, "request_started_at"),
                capture_id,
                attempt_id,
                str(row[2]),
                _as_int(row[3], "observation_count"),
                attempt,
                capture,
            )
        )
    reverse = order == "desc"
    candidates.sort(key=lambda item: (item[0], item[1]), reverse=reverse)
    selected = candidates[:limit]
    captures = [
        _capture_group(
            connection,
            requested_keyword=requested_keyword,
            recipe=resolved,
            kinds=kinds,
            capture_id=capture_id,
            attempt_id=attempt_id,
            classification=classification,
            observation_count=observation_count,
            attempt=attempt,
            capture=capture,
        )
        for (
            _started,
            capture_id,
            attempt_id,
            classification,
            observation_count,
            attempt,
            capture,
        ) in selected
    ]
    return {
        "provider": HISTORY_PROVIDER,
        "adapter_contract": HISTORY_ADAPTER,
        "requested_keyword": requested_keyword,
        "derivation_version_id": resolved.derivation_version_id,
        "recipe_resolution": resolved.resolution,
        "observation_kinds": list(kinds),
        "captures": captures,
    }


def _capture_group(
    connection: Connection[Any],
    *,
    requested_keyword: str,
    recipe: ResolvedProviderRecipe,
    kinds: Sequence[str],
    capture_id: str,
    attempt_id: str,
    classification: str,
    observation_count: int,
    attempt: Mapping[str, object],
    capture: Mapping[str, object],
) -> dict[str, object]:
    kind_set = set(kinds)
    group: dict[str, object] = {
        "attempt_id": attempt_id,
        "capture_id": capture_id,
        "provider": HISTORY_PROVIDER,
        "adapter_contract": HISTORY_ADAPTER,
        "derivation_version_id": recipe.derivation_version_id,
        "authorized_at": _require_text(attempt, "authorized_at"),
        "request_started_at": _require_text(capture, "request_started_at"),
        "transport_ended_at": _require_text(capture, "transport_ended_at"),
        "request": _request_context(attempt),
        "capture_outcome": {
            "classification": classification,
            "observation_count": observation_count,
        },
        "coverage": _one_row(
            connection,
            """
            SELECT within_capture_identity, covered, returned_keyword,
                   returned_keyword_state
            FROM keyword_overview_coverage
            WHERE capture_id = %s AND derivation_version_id = %s
              AND requested_keyword = %s
            """,
            (capture_id, recipe.derivation_version_id, requested_keyword),
            _coverage_json,
        ),
    }
    if METRICS_KIND in kind_set:
        group["metrics"] = _one_row(
            connection,
            """
            SELECT within_capture_identity, returned_keyword,
                   search_partners, search_partners_state,
                   search_volume, search_volume_state,
                   competition, competition_state,
                   competition_level, competition_level_state,
                   cpc, cpc_state,
                   low_top_of_page_bid, low_top_of_page_bid_state,
                   high_top_of_page_bid, high_top_of_page_bid_state,
                   categories, categories_state,
                   provider_update_time, provider_update_time_state
            FROM keyword_overview_metrics
            WHERE capture_id = %s AND derivation_version_id = %s
              AND requested_keyword = %s
            """,
            (capture_id, recipe.derivation_version_id, requested_keyword),
            _metrics_json,
        )
    if MONTHLY_KIND in kind_set:
        monthly_rows = connection.execute(
            """
            SELECT within_capture_identity, year, month,
                   search_volume, search_volume_state
            FROM keyword_overview_monthly_search_volume
            WHERE capture_id = %s AND derivation_version_id = %s
              AND requested_keyword = %s
            ORDER BY year, month
            """,
            (capture_id, recipe.derivation_version_id, requested_keyword),
        ).fetchall()
        group["monthly_search_volume"] = [_monthly_json(row) for row in monthly_rows]
    if TREND_KIND in kind_set:
        group["search_volume_trend"] = _one_row(
            connection,
            """
            SELECT within_capture_identity, monthly, monthly_state,
                   quarterly, quarterly_state, yearly, yearly_state
            FROM keyword_overview_search_volume_trend
            WHERE capture_id = %s AND derivation_version_id = %s
              AND requested_keyword = %s
            """,
            (capture_id, recipe.derivation_version_id, requested_keyword),
            _trend_json,
        )
    if PROPERTIES_KIND in kind_set:
        group["properties"] = _one_row(
            connection,
            """
            SELECT within_capture_identity, core_keyword, core_keyword_state,
                   synonym_clustering_algorithm,
                   synonym_clustering_algorithm_state,
                   keyword_difficulty, keyword_difficulty_state,
                   detected_language, detected_language_state,
                   is_another_language, is_another_language_state
            FROM keyword_overview_properties
            WHERE capture_id = %s AND derivation_version_id = %s
              AND requested_keyword = %s
            """,
            (capture_id, recipe.derivation_version_id, requested_keyword),
            _properties_json,
        )
    if BACKLINKS_KIND in kind_set:
        group["avg_backlinks"] = _one_row(
            connection,
            """
            SELECT within_capture_identity, backlinks, backlinks_state,
                   dofollow, dofollow_state, referring_pages,
                   referring_pages_state, referring_domains,
                   referring_domains_state, referring_main_domains,
                   referring_main_domains_state, rank, rank_state,
                   main_domain_rank, main_domain_rank_state,
                   provider_update_time, provider_update_time_state
            FROM keyword_overview_avg_backlinks
            WHERE capture_id = %s AND derivation_version_id = %s
              AND requested_keyword = %s
            """,
            (capture_id, recipe.derivation_version_id, requested_keyword),
            _backlinks_json,
        )
    if INTENT_KIND in kind_set:
        group["search_intent"] = _one_row(
            connection,
            """
            SELECT within_capture_identity, main_intent, main_intent_state,
                   foreign_intent, foreign_intent_state,
                   provider_update_time, provider_update_time_state
            FROM keyword_overview_search_intent
            WHERE capture_id = %s AND derivation_version_id = %s
              AND requested_keyword = %s
            """,
            (capture_id, recipe.derivation_version_id, requested_keyword),
            _intent_json,
        )
    return group


def _one_row(
    connection: Connection[Any],
    statement: str,
    params: tuple[object, ...],
    builder: Callable[[tuple[object, ...]], dict[str, object]],
) -> dict[str, object] | None:
    row = connection.execute(statement, params).fetchone()
    if row is None:
        return None
    return builder(row)


def _coverage_json(row: tuple[object, ...]) -> dict[str, object]:
    return {
        "observation_kind": COVERAGE_KIND,
        "within_capture_identity": str(row[0]),
        "covered": bool(row[1]),
        "returned_keyword": _json_field(row[3], row[2]),
    }


def _metrics_json(row: tuple[object, ...]) -> dict[str, object]:
    return {
        "observation_kind": METRICS_KIND,
        "within_capture_identity": str(row[0]),
        "returned_keyword": str(row[1]),
        "search_partners": _json_field(row[3], row[2]),
        "search_volume": _json_field(row[5], row[4]),
        "competition": _json_field(row[7], row[6]),
        "competition_level": _json_field(row[9], row[8]),
        "cpc": _json_field(row[11], row[10]),
        "low_top_of_page_bid": _json_field(row[13], row[12]),
        "high_top_of_page_bid": _json_field(row[15], row[14]),
        "categories": _json_field(row[17], _as_list(row[16])),
        "provider_update_time": _json_field(row[19], row[18]),
    }


def _monthly_json(row: tuple[object, ...]) -> dict[str, object]:
    return {
        "observation_kind": MONTHLY_KIND,
        "within_capture_identity": str(row[0]),
        "data_period": {
            "year": _as_int(row[1], "year"),
            "month": _as_int(row[2], "month"),
        },
        "search_volume": _json_field(row[4], row[3]),
    }


def _trend_json(row: tuple[object, ...]) -> dict[str, object]:
    return {
        "observation_kind": TREND_KIND,
        "within_capture_identity": str(row[0]),
        "monthly": _json_field(row[2], row[1]),
        "quarterly": _json_field(row[4], row[3]),
        "yearly": _json_field(row[6], row[5]),
    }


def _properties_json(row: tuple[object, ...]) -> dict[str, object]:
    return {
        "observation_kind": PROPERTIES_KIND,
        "within_capture_identity": str(row[0]),
        "core_keyword": _json_field(row[2], row[1]),
        "synonym_clustering_algorithm": _json_field(row[4], row[3]),
        "keyword_difficulty": _json_field(row[6], row[5]),
        "detected_language": _json_field(row[8], row[7]),
        "is_another_language": _json_field(row[10], row[9]),
    }


def _backlinks_json(row: tuple[object, ...]) -> dict[str, object]:
    return {
        "observation_kind": BACKLINKS_KIND,
        "within_capture_identity": str(row[0]),
        "backlinks": _json_field(row[2], row[1]),
        "dofollow": _json_field(row[4], row[3]),
        "referring_pages": _json_field(row[6], row[5]),
        "referring_domains": _json_field(row[8], row[7]),
        "referring_main_domains": _json_field(row[10], row[9]),
        "rank": _json_field(row[12], row[11]),
        "main_domain_rank": _json_field(row[14], row[13]),
        "provider_update_time": _json_field(row[16], row[15]),
    }


def _intent_json(row: tuple[object, ...]) -> dict[str, object]:
    foreign = row[3]
    return {
        "observation_kind": INTENT_KIND,
        "within_capture_identity": str(row[0]),
        "main_intent": _json_field(row[2], row[1]),
        "foreign_intent": _json_field(row[4], _as_list(foreign)),
        "provider_update_time": _json_field(row[6], row[5]),
    }
