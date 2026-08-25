"""Read-side assembly for DataForSEO Search Mentions API history."""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Any, Final, Literal

from psycopg import Connection, sql

from observatory.capture_event import MENTIONS_ADAPTER_CONTRACT
from observatory.dataforseo_ai_optimization_search_mentions import (
    ITEM_KIND,
    MONTHLY_KIND,
    SOURCE_KIND,
)
from observatory.evidence_store import EvidenceStore, IntegrityError
from observatory.provider_history import history_list_response
from observatory.provider_holdings import (
    HoldingsAttempt,
    assert_unique_holdings_groups,
    holdings_item,
    holdings_list_response,
)
from observatory.provider_outcomes import (
    load_validated_outcomes_recipe,
    load_verified_store_events,
    outcomes_list_response,
    project_matched_attempt,
)
from observatory.provider_recipe_selection import (
    ResolvedProviderRecipe,
    resolve_provider_recipe,
)

HISTORY_PROVIDER: Final[str] = "dataforseo"
HISTORY_ADAPTER: Final[str] = MENTIONS_ADAPTER_CONTRACT
_KIND_TABLES: Final[dict[str, str]] = {
    ITEM_KIND: "search_mentions_items",
    MONTHLY_KIND: "search_mentions_monthly_search_volume",
    SOURCE_KIND: "search_mentions_sources",
}
_OCCURRENCE_TABLES: Final[tuple[str, ...]] = (
    "search_mentions_item_occurrences",
    "search_mentions_monthly_occurrences",
    "search_mentions_source_occurrences",
)
_PARENT_OCCURRENCE: Final[tuple[tuple[str, str], ...]] = (
    ("search_mentions_items", "search_mentions_item_occurrences"),
    (
        "search_mentions_monthly_search_volume",
        "search_mentions_monthly_occurrences",
    ),
    ("search_mentions_sources", "search_mentions_source_occurrences"),
)


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
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    raise TypeError(f"unsupported provider field type: {type(value)!r}")


def _as_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


def _as_str_list(value: object, name: str) -> list[str]:
    if isinstance(value, (list, tuple)) and all(isinstance(item, str) for item in value):
        return [str(item) for item in value]
    raise IntegrityError(f"verified {name} is missing or wrong-typed")


def _require_text(document: Mapping[str, object], key: str) -> str:
    value = document.get(key)
    if not isinstance(value, str) or value == "":
        raise IntegrityError(f"verified document is missing {key}")
    return value


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
        raise IntegrityError("resolved recipe is not registered")
    document = json.loads(bytes(row[0]).decode("utf-8"))
    kinds = document.get("observation_kinds")
    if not isinstance(kinds, list) or not all(isinstance(item, str) for item in kinds):
        raise IntegrityError("resolved recipe has no observation kinds")
    return tuple(kinds)


def _parameters(attempt: Mapping[str, object]) -> Mapping[str, object]:
    parameters = attempt.get("parameters")
    if not isinstance(parameters, Mapping):
        raise IntegrityError("verified Attempt is missing parameters")
    return parameters


def _target(parameters: Mapping[str, object]) -> Mapping[str, object]:
    target = parameters.get("target")
    if not isinstance(target, list) or len(target) != 1:
        raise IntegrityError("verified Attempt target is missing")
    first = target[0]
    if not isinstance(first, Mapping):
        raise IntegrityError("verified Attempt target is missing")
    return first


def _request_context(
    attempt: Mapping[str, object],
    *,
    requested_keyword: str,
    match_type: str,
    search_filter: str,
    search_scope: object,
    platform: str,
    location_code: int,
    language_code: str,
    request_limit: int,
    request_offset: int,
) -> dict[str, object]:
    parameters = _parameters(attempt)
    target = _target(parameters)
    keyword = target.get("keyword")
    attempt_match = target.get("match_type")
    attempt_filter = target.get("search_filter")
    attempt_scope = target.get("search_scope")
    attempt_platform = parameters.get("platform")
    location = parameters.get("location_code")
    language = parameters.get("language_code")
    limit = parameters.get("limit")
    offset = parameters.get("offset")
    if not isinstance(keyword, str) or keyword == "":
        raise IntegrityError("verified Attempt keyword is missing")
    if not isinstance(attempt_match, str) or attempt_match == "":
        raise IntegrityError("verified Attempt match_type is missing")
    if not isinstance(attempt_filter, str) or attempt_filter == "":
        raise IntegrityError("verified Attempt search_filter is missing")
    scope = _as_str_list(attempt_scope, "Attempt search_scope")
    if not isinstance(attempt_platform, str) or attempt_platform == "":
        raise IntegrityError("verified Attempt platform is missing")
    if type(location) is not int:
        raise IntegrityError("verified Attempt location_code is missing")
    if not isinstance(language, str) or language == "":
        raise IntegrityError("verified Attempt language_code is missing")
    if type(limit) is not int:
        raise IntegrityError("verified Attempt limit is missing")
    if type(offset) is not int:
        raise IntegrityError("verified Attempt offset is missing")
    context_scope = _as_str_list(search_scope, "result context search_scope")
    if (
        keyword != requested_keyword
        or attempt_match != match_type
        or attempt_filter != search_filter
        or scope != context_scope
        or attempt_platform != platform
        or location != location_code
        or language != language_code
        or limit != request_limit
        or offset != request_offset
    ):
        raise IntegrityError("Attempt request context disagrees with result context")
    return {
        "match_type": attempt_match,
        "search_filter": attempt_filter,
        "search_scope": scope,
        "platform": attempt_platform,
        "location_code": location,
        "language_code": language,
        "limit": limit,
        "offset": offset,
    }


def _assert_history_candidates_consistent(
    connection: Connection[Any],
    candidates: Sequence[tuple[str, str, int]],
    derivation_version_id: str,
    kinds: Sequence[str],
) -> None:
    if not candidates:
        return
    capture_ids = [
        capture_id for capture_id, _classification, _count in candidates
    ]
    envelope_rows = connection.execute(
        """
        SELECT capture_id, within_capture_identity, observation_kind
        FROM observation_envelopes
        WHERE derivation_version_id = %s AND capture_id = ANY(%s)
        """,
        (derivation_version_id, capture_ids),
    ).fetchall()
    envelopes: dict[str, set[tuple[str, str]]] = {
        capture_id: set() for capture_id in capture_ids
    }
    for row in envelope_rows:
        envelopes[str(row[0])].add((str(row[1]), str(row[2])))
    typed: dict[str, set[tuple[str, str]]] = {
        capture_id: set() for capture_id in capture_ids
    }
    for kind in kinds:
        table = _KIND_TABLES.get(kind)
        if table is None:
            raise IntegrityError("resolved recipe names an unknown Observation kind")
        rows = connection.execute(
            sql.SQL(
                """
                SELECT capture_id, within_capture_identity, observation_kind
                FROM {}
                WHERE derivation_version_id = %s AND capture_id = ANY(%s)
                """
            ).format(sql.Identifier(table)),
            (derivation_version_id, capture_ids),
        ).fetchall()
        for row in rows:
            typed[str(row[0])].add((str(row[1]), str(row[2])))
    empty_ids = [
        capture_id
        for capture_id, classification, _count in candidates
        if classification == "observation_admitted_empty"
    ]
    for capture_id, classification, expected_count in candidates:
        keys = envelopes[capture_id]
        typed_keys = typed[capture_id]
        if classification == "observation_admitted_empty":
            if expected_count != 0 or keys or typed_keys:
                raise IntegrityError(
                    "admitted-empty Outcome disagrees with envelope emptiness"
                )
        elif classification == "observation_admitted":
            if expected_count <= 0:
                raise IntegrityError("admitted Outcome has empty observation_count")
            if len(keys) != expected_count:
                raise IntegrityError(
                    "envelope set disagrees with Outcome observation_count"
                )
            if typed_keys != keys:
                raise IntegrityError("typed Observation keys disagree with envelopes")
        else:
            raise IntegrityError("history candidate has unexpected classification")
    if empty_ids:
        for table in _OCCURRENCE_TABLES:
            leftover = connection.execute(
                sql.SQL(
                    """
                    SELECT 1 FROM {}
                    WHERE derivation_version_id = %s AND capture_id = ANY(%s)
                    LIMIT 1
                    """
                ).format(sql.Identifier(table)),
                (derivation_version_id, empty_ids),
            ).fetchone()
            if leftover is not None:
                raise IntegrityError("admitted-empty Capture has occurrences")
    for parent, occurrences in _PARENT_OCCURRENCE:
        orphan = connection.execute(
            sql.SQL(
                """
                SELECT 1
                FROM {} AS parent
                WHERE parent.derivation_version_id = %s
                  AND parent.capture_id = ANY(%s)
                  AND NOT EXISTS (
                        SELECT 1
                        FROM {} AS occ
                        WHERE occ.capture_id = parent.capture_id
                          AND occ.derivation_version_id = parent.derivation_version_id
                          AND occ.within_capture_identity = parent.within_capture_identity
                          AND occ.observation_kind = parent.observation_kind
                  )
                LIMIT 1
                """
            ).format(sql.Identifier(parent), sql.Identifier(occurrences)),
            (derivation_version_id, capture_ids),
        ).fetchone()
        if orphan is not None:
            raise IntegrityError("typed parent has no subordinate occurrences")


def load_search_mentions_history(
    store: EvidenceStore,
    connection: Connection[Any],
    *,
    requested_keyword: str,
    pinned_version: str | None,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble surface-explicit Search Mentions history for one requested keyword."""

    resolved = resolve_provider_recipe(connection, HISTORY_ADAPTER, pinned_version)
    kinds = _recipe_kinds(connection, resolved.derivation_version_id)
    rows = connection.execute(
        """
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
            c.request_limit,
            c.request_offset,
            c.total_count,
            c.result_offset,
            c.items_count,
            c.search_after_token,
            c.search_after_token_state
        FROM search_mentions_result_context AS c
        JOIN outcomes AS o
          ON o.derivation_version_id = c.derivation_version_id
         AND o.attempt_id = c.attempt_id
         AND o.capture_id = c.capture_id
        WHERE c.requested_keyword = %s
          AND c.derivation_version_id = %s
          AND o.classification IN (
                'observation_admitted',
                'observation_admitted_empty'
          )
        """,
        (requested_keyword, resolved.derivation_version_id),
    ).fetchall()
    candidates: list[
        tuple[
            str,
            str,
            str,
            str,
            int,
            dict[str, object],
            dict[str, object],
            dict[str, object],
            dict[str, object],
        ]
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
            or capture.get("provider") != HISTORY_PROVIDER
            or attempt.get("provider") != HISTORY_PROVIDER
        ):
            raise IntegrityError("derived Evidence is not Search Mentions")
        request = _request_context(
            attempt,
            requested_keyword=str(row[4]),
            match_type=str(row[5]),
            search_filter=str(row[6]),
            search_scope=row[7],
            platform=str(row[8]),
            location_code=_as_int(row[9], "location_code"),
            language_code=str(row[10]),
            request_limit=_as_int(row[11], "request_limit"),
            request_offset=_as_int(row[12], "request_offset"),
        )
        result_context = {
            "requested_keyword": str(row[4]),
            "total_count": _as_int(row[13], "total_count"),
            "result_offset": _as_int(row[14], "result_offset"),
            "items_count": _as_int(row[15], "items_count"),
            "search_after_token": _json_field(row[17], row[16]),
        }
        candidates.append(
            (
                _require_text(capture, "request_started_at"),
                capture_id,
                attempt_id,
                str(row[2]),
                _as_int(row[3], "observation_count"),
                attempt,
                capture,
                request,
                result_context,
            )
        )
    _assert_history_candidates_consistent(
        connection,
        [
            (capture_id, classification, observation_count)
            for (
                _started,
                capture_id,
                _attempt_id,
                classification,
                observation_count,
                _attempt,
                _capture,
                _request,
                _result_context,
            ) in candidates
        ],
        resolved.derivation_version_id,
        kinds,
    )
    unique: list[
        tuple[
            str,
            str,
            str,
            str,
            int,
            dict[str, object],
            dict[str, object],
            dict[str, object],
            dict[str, object],
        ]
    ] = []
    seen: set[str] = set()
    for item in candidates:
        capture_id = item[1]
        if capture_id in seen:
            continue
        seen.add(capture_id)
        unique.append(item)
    total_matching = len(unique)
    reverse = order == "desc"
    unique.sort(key=lambda item: (item[0], item[1]), reverse=reverse)
    selected = unique[:limit]
    captures = [
        _capture_group(
            connection,
            recipe=resolved,
            capture_id=capture_id,
            attempt_id=attempt_id,
            classification=classification,
            observation_count=observation_count,
            attempt=attempt,
            capture=capture,
            request=request,
            result_context=result_context,
        )
        for (
            _started,
            capture_id,
            attempt_id,
            classification,
            observation_count,
            attempt,
            capture,
            request,
            result_context,
        ) in selected
    ]
    return history_list_response(
        provider=HISTORY_PROVIDER,
        adapter_contract=HISTORY_ADAPTER,
        requested_keyword=requested_keyword,
        derivation_version_id=resolved.derivation_version_id,
        recipe_resolution=resolved.resolution,
        observation_kinds=list(kinds),
        captures=captures,
        total_matching=total_matching,
        limit=limit,
        order=order,
    )


def _capture_group(
    connection: Connection[Any],
    *,
    recipe: ResolvedProviderRecipe,
    capture_id: str,
    attempt_id: str,
    classification: str,
    observation_count: int,
    attempt: Mapping[str, object],
    capture: Mapping[str, object],
    request: Mapping[str, object],
    result_context: Mapping[str, object],
) -> dict[str, object]:
    return {
        "attempt_id": attempt_id,
        "capture_id": capture_id,
        "provider": HISTORY_PROVIDER,
        "adapter_contract": HISTORY_ADAPTER,
        "derivation_version_id": recipe.derivation_version_id,
        "authorized_at": _require_text(attempt, "authorized_at"),
        "request_started_at": _require_text(capture, "request_started_at"),
        "transport_ended_at": _require_text(capture, "transport_ended_at"),
        "request": dict(request),
        "capture_outcome": {
            "classification": classification,
            "observation_count": observation_count,
        },
        "result_context": dict(result_context),
        "search_mention_items": _items(
            connection, capture_id, recipe.derivation_version_id
        ),
        "monthly_search_volume": _monthly(
            connection, capture_id, recipe.derivation_version_id
        ),
        "structured_sources": _sources(
            connection, capture_id, recipe.derivation_version_id
        ),
    }


def _items(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT within_capture_identity, requested_keyword, platform, model_name,
               location_code, language_code, question, answer, ai_search_volume,
               is_web_search_based, first_response_at, last_response_at,
               search_results_state, brand_entities_state, fan_out_queries_state
        FROM search_mentions_items
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY model_name, question, within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    occurrence_rows = connection.execute(
        """
        SELECT within_capture_identity, item_index
        FROM search_mentions_item_occurrences
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY item_index
        """,
        (capture_id, version),
    ).fetchall()
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrence_rows:
        grouped[str(row[0])].append({"item_index": _as_int(row[1], "item_index")})
    return [
        {
            "observation_kind": ITEM_KIND,
            "within_capture_identity": str(row[0]),
            "requested_keyword": str(row[1]),
            "platform": str(row[2]),
            "model_name": str(row[3]),
            "location_code": _as_int(row[4], "location_code"),
            "language_code": str(row[5]),
            "question": str(row[6]),
            "answer": str(row[7]),
            "ai_search_volume": _as_int(row[8], "ai_search_volume"),
            "is_web_search_based": bool(row[9]),
            "first_response_at": str(row[10]),
            "last_response_at": str(row[11]),
            "search_results": _json_field(row[12], None),
            "brand_entities": _json_field(row[13], None),
            "fan_out_queries": _json_field(row[14], None),
            "occurrences": grouped[str(row[0])],
        }
        for row in rows
    ]


def _monthly(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT within_capture_identity, requested_keyword, model_name, question,
               year, month, search_volume
        FROM search_mentions_monthly_search_volume
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY year, month, model_name, question, within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    occurrence_rows = connection.execute(
        """
        SELECT within_capture_identity, item_index
        FROM search_mentions_monthly_occurrences
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY item_index
        """,
        (capture_id, version),
    ).fetchall()
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrence_rows:
        grouped[str(row[0])].append({"item_index": _as_int(row[1], "item_index")})
    return [
        {
            "observation_kind": MONTHLY_KIND,
            "within_capture_identity": str(row[0]),
            "requested_keyword": str(row[1]),
            "model_name": str(row[2]),
            "question": str(row[3]),
            "data_period": {
                "year": _as_int(row[4], "year"),
                "month": _as_int(row[5], "month"),
            },
            "search_volume": _as_int(row[6], "search_volume"),
            "occurrences": grouped[str(row[0])],
        }
        for row in rows
    ]


def _sources(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT within_capture_identity, requested_keyword, model_name, question,
               url, title, domain, source_name, snippet, publication_date,
               publication_date_state, thumbnail, thumbnail_state, markdown,
               markdown_state
        FROM search_mentions_sources
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY model_name, question, url, within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    occurrence_rows = connection.execute(
        """
        SELECT within_capture_identity, item_index, rank
        FROM search_mentions_source_occurrences
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY item_index, rank
        """,
        (capture_id, version),
    ).fetchall()
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrence_rows:
        grouped[str(row[0])].append(
            {
                "item_index": _as_int(row[1], "item_index"),
                "rank": _as_int(row[2], "rank"),
            }
        )
    return [
        {
            "observation_kind": SOURCE_KIND,
            "within_capture_identity": str(row[0]),
            "requested_keyword": str(row[1]),
            "model_name": str(row[2]),
            "question": str(row[3]),
            "url": str(row[4]),
            "title": str(row[5]),
            "domain": str(row[6]),
            "source_name": str(row[7]),
            "snippet": str(row[8]),
            "publication_date": _json_field(row[10], row[9]),
            "thumbnail": _json_field(row[12], row[11]),
            "markdown": _json_field(row[14], row[13]),
            "occurrences": grouped[str(row[0])],
        }
        for row in rows
    ]


def _outcomes_request(attempt: Mapping[str, object]) -> dict[str, object]:
    parameters = _parameters(attempt)
    target = _target(parameters)
    keyword = target.get("keyword")
    match_type = target.get("match_type")
    search_filter = target.get("search_filter")
    search_scope = target.get("search_scope")
    platform = parameters.get("platform")
    location = parameters.get("location_code")
    language = parameters.get("language_code")
    limit = parameters.get("limit")
    offset = parameters.get("offset")
    if not isinstance(keyword, str) or keyword == "":
        raise IntegrityError("verified Attempt keyword is missing")
    if not isinstance(match_type, str) or match_type == "":
        raise IntegrityError("verified Attempt match_type is missing")
    if not isinstance(search_filter, str) or search_filter == "":
        raise IntegrityError("verified Attempt search_filter is missing")
    scope = _as_str_list(search_scope, "Attempt search_scope")
    if not isinstance(platform, str) or platform == "":
        raise IntegrityError("verified Attempt platform is missing")
    if type(location) is not int:
        raise IntegrityError("verified Attempt location_code is missing")
    if not isinstance(language, str) or language == "":
        raise IntegrityError("verified Attempt language_code is missing")
    if type(limit) is not int:
        raise IntegrityError("verified Attempt limit is missing")
    if type(offset) is not int:
        raise IntegrityError("verified Attempt offset is missing")
    return {
        "keyword": keyword,
        "match_type": match_type,
        "search_filter": search_filter,
        "search_scope": scope,
        "platform": platform,
        "location_code": location,
        "language_code": language,
        "limit": limit,
        "offset": offset,
    }


def load_search_mentions_outcomes(
    store: EvidenceStore,
    connection: Connection[Any],
    *,
    requested_keyword: str,
    pinned_version: str | None,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble subject-filtered Search Mentions Measurement Outcomes."""

    resolved = resolve_provider_recipe(connection, HISTORY_ADAPTER, pinned_version)
    recipe = load_validated_outcomes_recipe(
        connection,
        derivation_version_id=resolved.derivation_version_id,
        resolved_provider=resolved.provider,
        resolved_adapter=resolved.adapter_contract,
        expected_provider=HISTORY_PROVIDER,
        expected_adapter=HISTORY_ADAPTER,
    )
    events = load_verified_store_events(store)
    matched: list[tuple[str, dict[str, object], dict[str, object]]] = []
    for attempt_id, attempt in events.attempts.items():
        if attempt.get("adapter_contract") != HISTORY_ADAPTER:
            continue
        if attempt.get("provider") != HISTORY_PROVIDER:
            raise IntegrityError("derived Evidence is not Search Mentions")
        request = _outcomes_request(attempt)
        if request["keyword"] != requested_keyword:
            continue
        matched.append((attempt_id, attempt, request))
    if not matched:
        return outcomes_list_response(
            provider=HISTORY_PROVIDER,
            adapter_contract=HISTORY_ADAPTER,
            requested_keyword=requested_keyword,
            derivation_version_id=recipe.derivation_version_id,
            recipe_resolution=resolved.resolution,
            observation_kinds=list(recipe.observation_kinds),
            outcomes=(),
            total_matching=0,
            limit=limit,
            order=order,
        )
    projected: list[tuple[str, str, dict[str, object]]] = []
    for attempt_id, attempt, request in matched:
        projected.append(
            (
                _require_text(attempt, "authorized_at"),
                attempt_id,
                project_matched_attempt(
                    connection,
                    events,
                    attempt_id=attempt_id,
                    attempt=attempt,
                    recipe=recipe,
                    request=request,
                ),
            )
        )
    reverse = order == "desc"
    projected.sort(key=lambda item: (item[0], item[1]), reverse=reverse)
    selected = projected[:limit]
    return outcomes_list_response(
        provider=HISTORY_PROVIDER,
        adapter_contract=HISTORY_ADAPTER,
        requested_keyword=requested_keyword,
        derivation_version_id=recipe.derivation_version_id,
        recipe_resolution=resolved.resolution,
        observation_kinds=list(recipe.observation_kinds),
        outcomes=[item[2] for item in selected],
        total_matching=len(projected),
        limit=limit,
        order=order,
    )


def load_search_mentions_holdings(
    store: EvidenceStore,
    *,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble Recipe-independent Search Mentions Holdings from verified Evidence."""

    events = load_verified_store_events(store)
    groups: dict[tuple[object, ...], dict[str, HoldingsAttempt]] = {}
    for attempt_id, attempt in events.attempts.items():
        if attempt.get("adapter_contract") != HISTORY_ADAPTER:
            continue
        if attempt.get("provider") != HISTORY_PROVIDER:
            raise IntegrityError("verified Evidence is not Search Mentions")
        request = _outcomes_request(attempt)
        keyword = request["keyword"]
        if not isinstance(keyword, str) or keyword == "":
            raise IntegrityError("verified Attempt keyword is missing")
        scope = request["search_scope"]
        if not isinstance(scope, list):
            raise IntegrityError("verified Attempt search_scope is missing")
        capture_ids = events.capture_ids_by_attempt.get(attempt_id, ())
        started = None
        if capture_ids:
            started = _require_text(events.captures[capture_ids[0]], "request_started_at")
        identity = (
            keyword,
            keyword,
            request["match_type"],
            request["search_filter"],
            tuple(scope),
            request["platform"],
            request["location_code"],
            request["language_code"],
            request["limit"],
            request["offset"],
        )
        bucket = groups.setdefault(identity, {})
        if attempt_id in bucket:
            raise IntegrityError("duplicate Attempt in Holdings group")
        bucket[attempt_id] = HoldingsAttempt(
            attempt_id=attempt_id,
            authorized_at=_require_text(attempt, "authorized_at"),
            request_started_at=started,
        )
    catalog: list[tuple[tuple[object, ...], dict[str, object]]] = []
    for group_key, members in groups.items():
        scope = group_key[4]
        if not isinstance(scope, tuple):
            raise IntegrityError("Holdings search_scope is missing")
        catalog.append(
            (
                group_key,
                holdings_item(
                    requested_keyword=str(group_key[0]),
                    request={
                        "keyword": group_key[1],
                        "match_type": group_key[2],
                        "search_filter": group_key[3],
                        "search_scope": [str(item) for item in scope],
                        "platform": group_key[5],
                        "location_code": group_key[6],
                        "language_code": group_key[7],
                        "limit": group_key[8],
                        "offset": group_key[9],
                    },
                    members=tuple(members.values()),
                ),
            )
        )
    assert_unique_holdings_groups(catalog)
    catalog.sort(key=lambda item: item[0], reverse=order == "desc")
    ordered = [item[1] for item in catalog]
    return holdings_list_response(
        provider=HISTORY_PROVIDER,
        adapter_contract=HISTORY_ADAPTER,
        holdings=ordered[:limit],
        total_matching=len(ordered),
        limit=limit,
        order=order,
    )
