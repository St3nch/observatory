"""Read-side assembly for DataForSEO Google Organic API history."""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Any, Final, Literal

from psycopg import Connection, sql

from observatory.capture_event import ORGANIC_ADAPTER_CONTRACT
from observatory.dataforseo_google_organic import (
    AIO_PRESENCE_KIND,
    AIO_SOURCE_KIND,
    FEATURE_PRESENCE_KIND,
    ORGANIC_PLACEMENT_KIND,
    RELATED_QUERY_KIND,
    RELATED_QUESTION_KIND,
)
from observatory.evidence_store import EvidenceStore, IntegrityError
from observatory.provider_history import history_list_response
from observatory.provider_outcomes import (
    load_verified_store_events,
    outcomes_list_response,
    project_matched_attempt,
    recipe_observation_kinds,
)
from observatory.provider_recipe_selection import (
    ResolvedProviderRecipe,
    resolve_provider_recipe,
)

HISTORY_PROVIDER: Final[str] = "dataforseo"
HISTORY_ADAPTER: Final[str] = ORGANIC_ADAPTER_CONTRACT
_KIND_TABLES: Final[dict[str, str]] = {
    FEATURE_PRESENCE_KIND: "google_organic_serp_features",
    ORGANIC_PLACEMENT_KIND: "google_organic_ranked_results",
    AIO_PRESENCE_KIND: "google_organic_aio_presence",
    AIO_SOURCE_KIND: "google_organic_aio_sources",
    RELATED_QUESTION_KIND: "google_organic_related_questions",
    RELATED_QUERY_KIND: "google_organic_related_queries",
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
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    raise TypeError(f"unsupported provider field type: {type(value)!r}")


def _as_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


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


def _request_context(
    attempt: Mapping[str, object],
    *,
    context_location: int,
    context_language: str,
) -> dict[str, object]:
    parameters = _parameters(attempt)
    location = parameters.get("location_code")
    language = parameters.get("language_code")
    depth = parameters.get("depth")
    device = parameters.get("device")
    operating_system = parameters.get("os")
    group = parameters.get("group_organic_results")
    load_async = parameters.get("load_async_ai_overview")
    if type(location) is not int:
        raise IntegrityError("verified Attempt location_code is missing")
    if not isinstance(language, str) or language == "":
        raise IntegrityError("verified Attempt language_code is missing")
    if type(depth) is not int:
        raise IntegrityError("verified Attempt depth is missing")
    if not isinstance(device, str) or device == "":
        raise IntegrityError("verified Attempt device is missing")
    if not isinstance(operating_system, str) or operating_system == "":
        raise IntegrityError("verified Attempt os is missing")
    if type(group) is not bool or type(load_async) is not bool:
        raise IntegrityError("verified Attempt organic flags are missing")
    if location != context_location or language != context_language:
        raise IntegrityError("Attempt request context disagrees with result context")
    return {
        "location_code": location,
        "language_code": language,
        "depth": depth,
        "device": device,
        "os": operating_system,
        "group_organic_results": group,
        "load_async_ai_overview": load_async,
    }


def _assert_history_candidates_consistent(
    connection: Connection[Any],
    candidates: Sequence[tuple[str, int]],
    derivation_version_id: str,
    kinds: Sequence[str],
) -> None:
    if not candidates:
        return
    capture_ids = [capture_id for capture_id, _count in candidates]
    expected_counts = {capture_id: count for capture_id, count in candidates}
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
    for capture_id, expected_count in expected_counts.items():
        keys = envelopes[capture_id]
        if len(keys) != expected_count:
            raise IntegrityError("envelope set disagrees with Outcome observation_count")
        if typed[capture_id] != keys:
            raise IntegrityError("typed Observation keys disagree with envelopes")
    orphan_sources = connection.execute(
        """
        SELECT 1
        FROM google_organic_aio_sources AS s
        WHERE s.derivation_version_id = %s
          AND s.capture_id = ANY(%s)
          AND NOT EXISTS (
                SELECT 1
                FROM google_organic_aio_source_occurrences AS o
                WHERE o.capture_id = s.capture_id
                  AND o.derivation_version_id = s.derivation_version_id
                  AND o.within_capture_identity = s.within_capture_identity
          )
        LIMIT 1
        """,
        (derivation_version_id, capture_ids),
    ).fetchone()
    if orphan_sources is not None:
        raise IntegrityError("AIO source has no subordinate occurrences")
    orphan_questions = connection.execute(
        """
        SELECT 1
        FROM google_organic_related_questions AS q
        WHERE q.derivation_version_id = %s
          AND q.capture_id = ANY(%s)
          AND NOT EXISTS (
                SELECT 1
                FROM google_organic_related_question_occurrences AS o
                WHERE o.capture_id = q.capture_id
                  AND o.derivation_version_id = q.derivation_version_id
                  AND o.within_capture_identity = q.within_capture_identity
          )
        LIMIT 1
        """,
        (derivation_version_id, capture_ids),
    ).fetchone()
    if orphan_questions is not None:
        raise IntegrityError("related-question parent has no subordinate occurrences")


def load_google_organic_history(
    store: EvidenceStore,
    connection: Connection[Any],
    *,
    requested_keyword: str,
    pinned_version: str | None,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble surface-explicit Google Organic history for one requested keyword."""

    resolved = resolve_provider_recipe(connection, HISTORY_ADAPTER, pinned_version)
    kinds = _recipe_kinds(connection, resolved.derivation_version_id)
    rows = connection.execute(
        """
        SELECT
            c.capture_id,
            c.attempt_id,
            o.classification,
            o.observation_count,
            c.location_code,
            c.language_code,
            c.requested_keyword,
            c.returned_keyword,
            c.returned_keyword_state,
            c.se_domain,
            c.se_domain_state,
            c.result_datetime,
            c.result_datetime_state,
            c.se_results_count,
            c.se_results_count_state,
            c.pages_count,
            c.pages_count_state,
            c.items_count,
            c.item_types
        FROM google_organic_result_context AS c
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
            or attempt.get("provider") != HISTORY_PROVIDER
        ):
            raise IntegrityError("derived Evidence is not Google Organic")
        request = _request_context(
            attempt,
            context_location=_as_int(row[4], "location_code"),
            context_language=str(row[5]),
        )
        result_context = {
            "requested_keyword": str(row[6]),
            "returned_keyword": _json_field(row[8], row[7]),
            "se_domain": _json_field(row[10], row[9]),
            "provider_result_time": _json_field(row[12], row[11]),
            "se_results_count": _json_field(row[14], row[13]),
            "pages_count": _json_field(row[16], row[15]),
            "items_count": _as_int(row[17], "items_count"),
            "item_types": _json_value(row[18]),
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
            (capture_id, observation_count)
            for (
                _started,
                capture_id,
                _attempt_id,
                _classification,
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
        "serp_features": _serp_features(
            connection, capture_id, recipe.derivation_version_id
        ),
        "ranked_results": _ranked_results(
            connection, capture_id, recipe.derivation_version_id
        ),
        "ai_overview_presence": _aio_presence(
            connection, capture_id, recipe.derivation_version_id
        ),
        "ai_overview_sources": _aio_sources(
            connection, capture_id, recipe.derivation_version_id
        ),
        "related_questions": _related_questions(
            connection, capture_id, recipe.derivation_version_id
        ),
        "related_queries": _related_queries(
            connection, capture_id, recipe.derivation_version_id
        ),
    }


def _serp_features(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT within_capture_identity, item_type, page, position,
               rank_group, rank_absolute
        FROM google_organic_serp_features
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY page, position, rank_absolute, rank_group,
                 within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    return [
        {
            "observation_kind": FEATURE_PRESENCE_KIND,
            "within_capture_identity": str(row[0]),
            "item_type": str(row[1]),
            "page": _as_int(row[2], "page"),
            "position": str(row[3]),
            "rank_group": _as_int(row[4], "rank_group"),
            "rank_absolute": _as_int(row[5], "rank_absolute"),
        }
        for row in rows
    ]


def _ranked_results(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT within_capture_identity, url, domain, title,
               description, description_state, website_name, website_name_state,
               page, position, rank_group, rank_absolute
        FROM google_organic_ranked_results
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY page, position, rank_absolute, rank_group,
                 within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    return [
        {
            "observation_kind": ORGANIC_PLACEMENT_KIND,
            "within_capture_identity": str(row[0]),
            "url": str(row[1]),
            "domain": str(row[2]),
            "title": str(row[3]),
            "description": _json_field(row[5], row[4]),
            "website_name": _json_field(row[7], row[6]),
            "page": _as_int(row[8], "page"),
            "position": str(row[9]),
            "rank_group": _as_int(row[10], "rank_group"),
            "rank_absolute": _as_int(row[11], "rank_absolute"),
        }
        for row in rows
    ]


def _aio_presence(
    connection: Connection[Any], capture_id: str, version: str
) -> dict[str, object] | None:
    row = connection.execute(
        """
        SELECT within_capture_identity, asynchronous_ai_overview,
               page, position, rank_group, rank_absolute
        FROM google_organic_aio_presence
        WHERE capture_id = %s AND derivation_version_id = %s
        """,
        (capture_id, version),
    ).fetchone()
    if row is None:
        return None
    return {
        "observation_kind": AIO_PRESENCE_KIND,
        "within_capture_identity": str(row[0]),
        "asynchronous_ai_overview": bool(row[1]),
        "page": _as_int(row[2], "page"),
        "position": str(row[3]),
        "rank_group": _as_int(row[4], "rank_group"),
        "rank_absolute": _as_int(row[5], "rank_absolute"),
    }


def _aio_sources(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    source_rows = connection.execute(
        """
        SELECT within_capture_identity, locus, url,
               domain, domain_state, title, title_state, source, source_state
        FROM google_organic_aio_sources
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY locus, url, within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    occurrence_rows = connection.execute(
        """
        SELECT within_capture_identity, locus, element_index, reference_index
        FROM google_organic_aio_source_occurrences
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY locus, element_index NULLS FIRST, reference_index
        """,
        (capture_id, version),
    ).fetchall()
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrence_rows:
        grouped[str(row[0])].append(
            {
                "locus": str(row[1]),
                "element_index": None if row[2] is None else _as_int(row[2], "element_index"),
                "reference_index": _as_int(row[3], "reference_index"),
            }
        )
    return [
        {
            "observation_kind": AIO_SOURCE_KIND,
            "within_capture_identity": str(row[0]),
            "locus": str(row[1]),
            "url": str(row[2]),
            "domain": _json_field(row[4], row[3]),
            "title": _json_field(row[6], row[5]),
            "source": _json_field(row[8], row[7]),
            "occurrences": grouped[str(row[0])],
        }
        for row in source_rows
    ]


def _related_questions(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    question_rows = connection.execute(
        """
        SELECT within_capture_identity, title
        FROM google_organic_related_questions
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY title, within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    occurrence_rows = connection.execute(
        """
        SELECT within_capture_identity, page, position,
               rank_group, rank_absolute, question_index
        FROM google_organic_related_question_occurrences
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY page, position, rank_absolute, rank_group, question_index
        """,
        (capture_id, version),
    ).fetchall()
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrence_rows:
        grouped[str(row[0])].append(
            {
                "page": _as_int(row[1], "page"),
                "position": str(row[2]),
                "rank_group": _as_int(row[3], "rank_group"),
                "rank_absolute": _as_int(row[4], "rank_absolute"),
                "question_index": _as_int(row[5], "question_index"),
            }
        )
    return [
        {
            "observation_kind": RELATED_QUESTION_KIND,
            "within_capture_identity": str(row[0]),
            "title": str(row[1]),
            "occurrences": grouped[str(row[0])],
        }
        for row in question_rows
    ]


def _related_queries(
    connection: Connection[Any], capture_id: str, version: str
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT within_capture_identity, query
        FROM google_organic_related_queries
        WHERE capture_id = %s AND derivation_version_id = %s
        ORDER BY query, within_capture_identity
        """,
        (capture_id, version),
    ).fetchall()
    return [
        {
            "observation_kind": RELATED_QUERY_KIND,
            "within_capture_identity": str(row[0]),
            "query": str(row[1]),
        }
        for row in rows
    ]


def _outcomes_request(attempt: Mapping[str, object]) -> dict[str, object]:
    parameters = _parameters(attempt)
    keyword = parameters.get("keyword")
    location = parameters.get("location_code")
    language = parameters.get("language_code")
    depth = parameters.get("depth")
    device = parameters.get("device")
    operating_system = parameters.get("os")
    group = parameters.get("group_organic_results")
    load_async = parameters.get("load_async_ai_overview")
    if not isinstance(keyword, str) or keyword == "":
        raise IntegrityError("verified Attempt keyword is missing")
    if type(location) is not int:
        raise IntegrityError("verified Attempt location_code is missing")
    if not isinstance(language, str) or language == "":
        raise IntegrityError("verified Attempt language_code is missing")
    if type(depth) is not int:
        raise IntegrityError("verified Attempt depth is missing")
    if not isinstance(device, str) or device == "":
        raise IntegrityError("verified Attempt device is missing")
    if not isinstance(operating_system, str) or operating_system == "":
        raise IntegrityError("verified Attempt os is missing")
    if type(group) is not bool or type(load_async) is not bool:
        raise IntegrityError("verified Attempt organic flags are missing")
    return {
        "keyword": keyword,
        "location_code": location,
        "language_code": language,
        "depth": depth,
        "device": device,
        "os": operating_system,
        "group_organic_results": group,
        "load_async_ai_overview": load_async,
    }


def load_google_organic_outcomes(
    store: EvidenceStore,
    connection: Connection[Any],
    *,
    requested_keyword: str,
    pinned_version: str | None,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble subject-filtered Google Organic Measurement Outcomes."""

    resolved = resolve_provider_recipe(connection, HISTORY_ADAPTER, pinned_version)
    kinds = recipe_observation_kinds(connection, resolved.derivation_version_id)
    events = load_verified_store_events(store)
    matched: list[tuple[str, dict[str, object], dict[str, object]]] = []
    for attempt_id, attempt in events.attempts.items():
        if attempt.get("adapter_contract") != HISTORY_ADAPTER:
            continue
        if attempt.get("provider") != HISTORY_PROVIDER:
            raise IntegrityError("derived Evidence is not Google Organic")
        request = _outcomes_request(attempt)
        if request["keyword"] != requested_keyword:
            continue
        matched.append((attempt_id, attempt, request))
    if not matched:
        return outcomes_list_response(
            provider=HISTORY_PROVIDER,
            adapter_contract=HISTORY_ADAPTER,
            requested_keyword=requested_keyword,
            derivation_version_id=resolved.derivation_version_id,
            recipe_resolution=resolved.resolution,
            observation_kinds=list(kinds),
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
                    derivation_version_id=resolved.derivation_version_id,
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
        derivation_version_id=resolved.derivation_version_id,
        recipe_resolution=resolved.resolution,
        observation_kinds=list(kinds),
        outcomes=[item[2] for item in selected],
        total_matching=len(projected),
        limit=limit,
        order=order,
    )
