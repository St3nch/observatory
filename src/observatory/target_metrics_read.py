"""Read-side assembly for DataForSEO Target Metrics admitted history."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, Final, Literal

from psycopg import Connection
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from observatory.capture_event import (
    TARGET_METRICS_ADAPTER_CONTRACT,
    DocumentError,
    canonical_json,
    content_digest,
    validate_target_metrics_http_parameters,
)
from observatory.dataforseo_ai_optimization_target_metrics import (
    PROVIDER,
    SOURCE_DOMAIN_KIND,
    TOTAL_KIND,
)
from observatory.evidence_store import EvidenceStore, IntegrityError
from observatory.provider_history import (
    HISTORY_LIMIT_MAX,
    history_list_response,
)
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
from observatory.target_metrics_derive import TARGET_METRICS_RECIPE, TARGET_METRICS_RECIPE_ID

HISTORY_PROVIDER: Final[str] = PROVIDER
HISTORY_ADAPTER: Final[str] = TARGET_METRICS_ADAPTER_CONTRACT
IJSON_MAX: Final[int] = 9007199254740991
V1_KINDS: Final[tuple[str, str]] = (TOTAL_KIND, SOURCE_DOMAIN_KIND)
V1_CAPTURE_OUTCOMES: Final[tuple[str, ...]] = (
    "no_response",
    "observation_admitted",
    "provider_envelope_rejected",
    "provider_error",
    "reconciliation_failed",
    "response_partial",
    "transport_complete_non_admissible",
)
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
        "total",
        "source_domains",
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
        "internal_list_limit",
    }
)
_CONTEXT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "total_count",
        "result_offset",
        "items_count",
        "items_state",
        "location",
        "language",
        "platform",
        "sources_domain_count",
        "search_results_domain",
        "brand_entities_title",
        "brand_entities_category",
    }
)
_FIELD_STATES: Final[frozenset[str]] = frozenset({"absent", "json_null", "stated"})

_GRAIN: Final[str] = (
    "Admitted, subject-bound Target Metrics Capture-document history under Recipe v1. "
    "This list grain is Capture documents, not Observation envelopes, typed facts, "
    "raw source-domain rows, mention totals, or provider corpus/item counts."
)
_EMPTY: Final[str] = (
    "Empty admitted history (total_matching 0, captures empty) means no matching "
    "admitted Capture documents under this route, keyword, and Recipe v1. It does not "
    "distinguish failed measurement from never measured, unresolved authorization, "
    "provider zero, or absence from a provider corpus."
)
_ORDER: Final[str] = (
    "Echo of the validated query order. Deterministic outer ordering is "
    "(request_started_at, capture_id); descending reverses that complete key "
    "before limiting. This is not provider item order, rank, or source-domain order."
)
_HAS_MORE: Final[str] = (
    "True when total_matching exceeds returned_count. Discloses an omitted outer "
    "Capture-history tail. This is not pagination, a cursor, or authorization to "
    "fetch another page."
)
_COUNT_GRAIN: Final[str] = (
    "observation_count is Observation-envelope cardinality: one total plus one "
    "source-domain Observation per distinct exact domain. For every admitted Recipe v1 "
    "Capture it equals 1 + len(source_domains) and 1 + sources_domain_count. "
    "sources_domain_count is the persisted raw parsed sources_domain array length. "
    "The two grains are equal on admitted v1 documents; any inequality is integrity "
    "failure, not truncation, completeness, or collapsed-duplicate history. "
    "Neither count is mention volume, rank, share, or partition."
)
_INDEX: Final[str] = (
    "provider_array_index is the exact unique lexical array position for this admitted "
    "Recipe v1 source-domain identity. It is not rank, importance, share, or "
    "cross-Capture identity."
)
_LIMIT: Final[str] = (
    "internal_list_limit is closed Attempt request testimony. Reaching this value, "
    "including ten returned source-domain rows, does not prove truncation or "
    "completeness."
)
_ZERO: Final[str] = (
    "Valid zero mentions or ai_search_volume remain stated observation_admitted facts. "
    "Recipe v1 never emits observation_admitted_empty. Structural total_count, "
    "result_offset, and items_count zeros are this contract's result topology, not an "
    "empty measurement, empty corpus, or failure."
)
_GROUPING: Final[str] = (
    "Location, language, and platform are request-constrained result context, not "
    "Observation families or independently queryable slices. Their metrics may disagree "
    "with total. row_count is fixed to 1 for admitted Recipe v1."
)
_TIME: Final[str] = (
    "authorized_at, request_started_at, and transport_ended_at are Observatory Capture "
    "and Attempt timestamps. Target Metrics states no Provider Update Time or Data "
    "Period; Capture time must not substitute for those unstated axes."
)


class UnsupportedTargetMetricsRecipe(ProviderRecipeSelectionError):
    """Resolved Recipe is not the accepted Target Metrics v1 identity."""


class TargetMetricsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    keyword: str = Field(
        min_length=1,
        description=(
            "Exact verified Attempt target keyword. Not trimmed, case-folded, "
            "normalized, or replaced by task.data echo."
        ),
    )
    match_type: str
    search_filter: str
    search_scope: list[str] = Field(
        description=(
            "Exact ordered Attempt search_scope array. Frozen constants remain scope testimony."
        )
    )
    platform: str
    location_code: int = Field(ge=0, le=IJSON_MAX)
    language_code: str
    internal_list_limit: int = Field(ge=0, le=IJSON_MAX, description=_LIMIT)


class TargetMetricsCaptureOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    classification: Literal["observation_admitted"] = Field(
        description=(
            "Capture-stage Outcome for admitted history. Recipe v1 never emits "
            "observation_admitted_empty. " + _ZERO
        )
    )
    observation_count: int = Field(ge=1, le=IJSON_MAX, description=_COUNT_GRAIN)


class TargetMetricsGrouping(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    key: int | str
    mentions: int = Field(ge=0, le=IJSON_MAX)
    ai_search_volume: int = Field(ge=0, le=IJSON_MAX)
    provider_array_index: int = Field(ge=0, le=IJSON_MAX, description=_INDEX)
    row_count: Literal[1] = Field(description=_GROUPING)


class TargetMetricsLocationGrouping(TargetMetricsGrouping):
    key: int = Field(ge=0, le=IJSON_MAX, description=_GROUPING)


class TargetMetricsStringGrouping(TargetMetricsGrouping):
    key: str = Field(min_length=1, description=_GROUPING)


class TargetMetricsOptionalFamily(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    state: Literal["absent", "json_null", "stated"] = Field(
        description=(
            "Closed field state. nonempty optional grouping families fail closed in "
            "Recipe v1, so stated count is zero. count is null when state is absent or json_null."
        )
    )
    count: int | None = Field(ge=0, le=IJSON_MAX, default=None)


class TargetMetricsResultContext(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    total_count: int = Field(ge=0, le=IJSON_MAX, description=_ZERO)
    result_offset: int = Field(ge=0, le=IJSON_MAX, description=_ZERO)
    items_count: int = Field(ge=0, le=IJSON_MAX, description=_ZERO)
    items_state: Literal["absent", "json_null", "stated"]
    location: TargetMetricsLocationGrouping
    language: TargetMetricsStringGrouping
    platform: TargetMetricsStringGrouping
    sources_domain_count: int = Field(ge=0, le=IJSON_MAX, description=_COUNT_GRAIN)
    search_results_domain: TargetMetricsOptionalFamily
    brand_entities_title: TargetMetricsOptionalFamily
    brand_entities_category: TargetMetricsOptionalFamily


class TargetMetricsTotal(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal["dataforseo.google.ai_optimization.target_metrics.total.v1"]
    within_capture_identity: str = Field(min_length=64, max_length=64)
    requested_keyword: str = Field(min_length=1)
    mentions: int = Field(ge=0, le=IJSON_MAX, description=_ZERO)
    ai_search_volume: int = Field(ge=0, le=IJSON_MAX, description=_ZERO)


class TargetMetricsSourceDomain(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    observation_kind: Literal[
        "dataforseo.google.ai_optimization.target_metrics.source_domain.v1"
    ]
    within_capture_identity: str = Field(min_length=64, max_length=64)
    requested_keyword: str = Field(min_length=1)
    domain: str = Field(
        min_length=1,
        description=(
            "Exact raw provider domain key. Not hostname-normalized, www-collapsed, "
            "a Brand, a Page, rank, or a join to Search Mentions sources."
        ),
    )
    mentions: int = Field(ge=0, le=IJSON_MAX, description=_ZERO)
    ai_search_volume: int = Field(ge=0, le=IJSON_MAX, description=_ZERO)
    provider_array_index: int = Field(ge=0, le=IJSON_MAX, description=_INDEX)


class TargetMetricsCapture(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    attempt_id: str = Field(min_length=64, max_length=64, description=_GRAIN)
    capture_id: str = Field(min_length=64, max_length=64)
    provider: Literal["dataforseo"]
    adapter_contract: Literal[
        "dataforseo-ai-optimization-llm-mentions-target-metrics-live-paid-probe-v1"
    ]
    derivation_version_id: Literal[
        "b6addc49c60eff18de7aaf5dc6c35ebffa93e242649d5e2ddd009822b12e5104"
    ]
    authorized_at: str = Field(description=_TIME)
    request_started_at: str = Field(description=_TIME)
    transport_ended_at: str = Field(description=_TIME)
    request: TargetMetricsRequest
    capture_outcome: TargetMetricsCaptureOutcome
    result_context: TargetMetricsResultContext
    total: TargetMetricsTotal
    source_domains: list[TargetMetricsSourceDomain] = Field(description=_COUNT_GRAIN)


class TargetMetricsHistoryEnvelope(BaseModel):
    """Closed Target Metrics admitted-history envelope. Nested Captures are fully typed."""

    model_config = ConfigDict(extra="forbid", strict=True)

    provider: Literal["dataforseo"] = Field(description=_GRAIN + " " + _EMPTY)
    adapter_contract: Literal[
        "dataforseo-ai-optimization-llm-mentions-target-metrics-live-paid-probe-v1"
    ]
    requested_keyword: str = Field(min_length=1, description=_EMPTY)
    derivation_version_id: Literal[
        "b6addc49c60eff18de7aaf5dc6c35ebffa93e242649d5e2ddd009822b12e5104"
    ]
    recipe_resolution: Literal["selected", "pinned"]
    observation_kinds: list[str] = Field(
        description=(
            "Recipe v1 Observation kinds in Recipe order: total then source_domain. "
            "They do not change the list grain. " + _COUNT_GRAIN
        )
    )
    captures: list[TargetMetricsCapture] = Field(
        description=(
            "Whole admitted Capture documents. Fully typed Target Metrics fact bodies, "
            "not one universal provider schema. " + _EMPTY
        )
    )
    total_matching: int = Field(ge=0, description=_GRAIN + " " + _EMPTY)
    returned_count: int = Field(ge=0, description="Number of whole Capture documents in captures.")
    limit: int = Field(
        ge=1,
        le=HISTORY_LIMIT_MAX,
        description="Validated applied outer history limit. Maximum 100. Not a provider page size.",
    )
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


def _identity(kind: str, axes: Mapping[str, object]) -> str:
    return observation_identity(
        {
            "axes": dict(axes),
            "observation_kind": kind,
            "schema": IDENTITY_SCHEMA,
            "version": IDENTITY_VERSION,
        },
        TARGET_METRICS_RECIPE,
    )


def _load_validated_v1_recipe(
    connection: Connection[Any], resolved: ResolvedProviderRecipe
) -> ResolvedProviderRecipe:
    if resolved.derivation_version_id != TARGET_METRICS_RECIPE_ID:
        raise UnsupportedTargetMetricsRecipe(
            "Target Metrics history serves Recipe v1 only"
        )
    if resolved.provider != HISTORY_PROVIDER or resolved.adapter_contract != HISTORY_ADAPTER:
        raise IntegrityError("resolved Recipe does not match this route")
    row = connection.execute(
        """
        SELECT provider, adapter_contract, recipe_canonical_bytes
        FROM provider_recipes
        WHERE derivation_version_id = %s
        """,
        (TARGET_METRICS_RECIPE_ID,),
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
    if digest != TARGET_METRICS_RECIPE_ID:
        raise IntegrityError("Recipe digest disagrees with derivation_version_id")
    document_provider = str(validated["provider"])
    document_adapter = str(validated["adapter_contract"])
    identities = {
        HISTORY_PROVIDER,
        resolved.provider,
        column_provider,
        document_provider,
    }
    adapters = {
        HISTORY_ADAPTER,
        resolved.adapter_contract,
        column_adapter,
        document_adapter,
    }
    if identities != {HISTORY_PROVIDER}:
        raise IntegrityError("Recipe provider metadata disagrees")
    if adapters != {HISTORY_ADAPTER}:
        raise IntegrityError("Recipe adapter metadata disagrees")
    kinds = validated["observation_kinds"]
    if kinds != list(V1_KINDS):
        raise IntegrityError("Recipe observation kinds are not Target Metrics v1")
    admission = validated["admission"]
    if not isinstance(admission, Mapping):
        raise IntegrityError("Recipe admission is missing")
    outcomes = admission.get("capture_outcomes")
    if outcomes != list(V1_CAPTURE_OUTCOMES):
        raise IntegrityError("Recipe classifications are not Target Metrics v1")
    if "observation_admitted_empty" in outcomes:
        raise IntegrityError("Recipe v1 forbids observation_admitted_empty")
    return resolved


def _optional_family(state: object, count: object, name: str) -> dict[str, object]:
    token = _as_text(state, f"{name}_state")
    if token not in _FIELD_STATES:
        raise IntegrityError(f"{name}_state is not a closed field state")
    if token == "stated":
        value = _as_int(count, f"{name}_count")
        if value != 0:
            raise IntegrityError(f"{name} stated count must be zero under Recipe v1")
        return {"state": "stated", "count": 0}
    if count is not None:
        raise IntegrityError(f"{name}_count must be null when state is {token}")
    return {"state": token, "count": None}


def _grouping(
    *,
    key: object,
    mentions: object,
    volume: object,
    index: object,
    row_count: object,
    integer_key: bool,
    name: str,
) -> dict[str, object]:
    count = _as_int(row_count, f"{name}_row_count")
    if count != 1:
        raise IntegrityError(f"{name} row_count must be 1")
    parsed_key: int | str = (
        _as_int(key, f"{name}_key") if integer_key else _as_text(key, f"{name}_key")
    )
    return {
        "key": parsed_key,
        "mentions": _as_int(mentions, f"{name}_mentions"),
        "ai_search_volume": _as_int(volume, f"{name}_ai_search_volume"),
        "provider_array_index": _as_int(index, f"{name}_provider_array_index"),
        "row_count": 1,
    }


def _attempt_request(attempt: Mapping[str, object]) -> dict[str, object]:
    parameters = attempt.get("parameters")
    if not isinstance(parameters, Mapping):
        raise IntegrityError("verified Attempt is missing parameters")
    try:
        closed = validate_target_metrics_http_parameters(parameters)
    except DocumentError as exc:
        raise IntegrityError("verified Attempt parameters are not Target Metrics") from exc
    target = closed["target"]
    if not isinstance(target, list) or len(target) != 1 or not isinstance(target[0], Mapping):
        raise IntegrityError("verified Attempt target is missing")
    first = target[0]
    keyword = first.get("keyword")
    match_type = first.get("match_type")
    search_filter = first.get("search_filter")
    search_scope = first.get("search_scope")
    if not isinstance(keyword, str) or keyword == "":
        raise IntegrityError("verified Attempt keyword is missing")
    request = {
        "keyword": keyword,
        "match_type": _as_text(match_type, "match_type"),
        "search_filter": _as_text(search_filter, "search_filter"),
        "search_scope": _as_str_list(search_scope, "search_scope"),
        "platform": _as_text(closed.get("platform"), "platform"),
        "location_code": _as_int(closed.get("location_code"), "location_code"),
        "language_code": _as_text(closed.get("language_code"), "language_code"),
        "internal_list_limit": _as_int(
            closed.get("internal_list_limit"), "internal_list_limit"
        ),
    }
    if set(request) != _REQUEST_KEYS:
        raise IntegrityError("Attempt request keys are not closed")
    return request


def _require_request_agreement(
    request: Mapping[str, object],
    *,
    keyword: str,
    match_type: str,
    search_filter: str,
    search_scope: list[str],
    platform: str,
    location_code: int,
    language_code: str,
    internal_list_limit: int,
    location_key: int,
    language_key: str,
    platform_key: str,
) -> None:
    if (
        request["keyword"] != keyword
        or request["match_type"] != match_type
        or request["search_filter"] != search_filter
        or request["search_scope"] != search_scope
        or request["platform"] != platform
        or request["location_code"] != location_code
        or request["language_code"] != language_code
        or request["internal_list_limit"] != internal_list_limit
        or location_key != location_code
        or language_key != language_code
        or platform_key != platform
    ):
        raise IntegrityError("Attempt request disagrees with result context")


def _load_typed_facts(
    connection: Connection[Any],
    capture_id: str,
    keyword: str,
    observation_count: int,
    sources_domain_count: int,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    envelopes = connection.execute(
        """
        SELECT within_capture_identity, observation_kind, attempt_id, provider,
               adapter_contract
        FROM observation_envelopes
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (TARGET_METRICS_RECIPE_ID, capture_id),
    ).fetchall()
    envelope_keys: set[tuple[str, str]] = set()
    for row in envelopes:
        kind = str(row[1])
        if kind not in V1_KINDS:
            raise IntegrityError("unknown Observation kind")
        if str(row[3]) != HISTORY_PROVIDER or str(row[4]) != HISTORY_ADAPTER:
            raise IntegrityError("envelope provider or adapter disagrees")
        envelope_keys.add((str(row[0]), kind))
    totals = connection.execute(
        """
        SELECT within_capture_identity, observation_kind, requested_keyword,
               mentions, ai_search_volume
        FROM target_metrics_totals
        WHERE derivation_version_id = %s AND capture_id = %s
        """,
        (TARGET_METRICS_RECIPE_ID, capture_id),
    ).fetchall()
    domains = connection.execute(
        """
        SELECT within_capture_identity, observation_kind, requested_keyword,
               domain, mentions, ai_search_volume, provider_array_index
        FROM target_metrics_source_domains
        WHERE derivation_version_id = %s AND capture_id = %s
        ORDER BY provider_array_index, within_capture_identity
        """,
        (TARGET_METRICS_RECIPE_ID, capture_id),
    ).fetchall()
    if len(totals) != 1:
        raise IntegrityError("admitted Capture must have exactly one total")
    total_row = totals[0]
    total_identity = _identity(TOTAL_KIND, {"requested_keyword": keyword})
    if (
        str(total_row[0]) != total_identity
        or str(total_row[1]) != TOTAL_KIND
        or str(total_row[2]) != keyword
    ):
        raise IntegrityError("total identity disagrees")
    typed_keys: set[tuple[str, str]] = {(str(total_row[0]), str(total_row[1]))}
    source_payload: list[dict[str, object]] = []
    seen_domains: set[str] = set()
    for row in domains:
        domain = _as_text(row[3], "domain")
        if domain in seen_domains:
            raise IntegrityError("duplicate source-domain identity")
        seen_domains.add(domain)
        identity = _identity(
            SOURCE_DOMAIN_KIND, {"domain": domain, "requested_keyword": keyword}
        )
        if (
            str(row[0]) != identity
            or str(row[1]) != SOURCE_DOMAIN_KIND
            or str(row[2]) != keyword
        ):
            raise IntegrityError("source-domain identity disagrees")
        typed_keys.add((str(row[0]), str(row[1])))
        source_payload.append(
            {
                "observation_kind": SOURCE_DOMAIN_KIND,
                "within_capture_identity": identity,
                "requested_keyword": keyword,
                "domain": domain,
                "mentions": _as_int(row[4], "mentions"),
                "ai_search_volume": _as_int(row[5], "ai_search_volume"),
                "provider_array_index": _as_int(row[6], "provider_array_index"),
            }
        )
    if typed_keys != envelope_keys:
        raise IntegrityError("typed Observation keys disagree with envelopes")
    if observation_count != len(envelope_keys):
        raise IntegrityError("envelope set disagrees with Outcome observation_count")
    if observation_count != 1 + len(source_payload):
        raise IntegrityError("observation_count disagrees with distinct source domains")
    if sources_domain_count != len(source_payload):
        raise IntegrityError("sources_domain_count disagrees with typed source domains")
    if observation_count != 1 + sources_domain_count:
        raise IntegrityError("observation_count disagrees with sources_domain_count")
    total = {
        "observation_kind": TOTAL_KIND,
        "within_capture_identity": total_identity,
        "requested_keyword": keyword,
        "mentions": _as_int(total_row[3], "mentions"),
        "ai_search_volume": _as_int(total_row[4], "ai_search_volume"),
    }
    return total, source_payload


def _verify_capture(
    store: EvidenceStore,
    connection: Connection[Any],
    row: Sequence[object],
    requested_keyword: str,
) -> dict[str, object]:
    capture_id = _as_text(row[0], "capture_id")
    attempt_id = _as_text(row[1], "attempt_id")
    classification = row[2]
    if classification is None or str(classification) != "observation_admitted":
        raise IntegrityError("matching context is not observation_admitted")
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
    internal_list_limit = _as_int(row[11], "internal_list_limit")
    total_count = _as_int(row[12], "total_count")
    result_offset = _as_int(row[13], "result_offset")
    items_count = _as_int(row[14], "items_count")
    items_state = _as_text(row[15], "items_state")
    if items_state not in _FIELD_STATES:
        raise IntegrityError("items_state is not a closed field state")
    if total_count != 0 or result_offset != 0 or items_count != 0:
        raise IntegrityError("structural Target Metrics counts must be zero")
    location = _grouping(
        key=row[16],
        mentions=row[17],
        volume=row[18],
        index=row[19],
        row_count=row[20],
        integer_key=True,
        name="location",
    )
    language = _grouping(
        key=row[21],
        mentions=row[22],
        volume=row[23],
        index=row[24],
        row_count=row[25],
        integer_key=False,
        name="language",
    )
    platform_group = _grouping(
        key=row[26],
        mentions=row[27],
        volume=row[28],
        index=row[29],
        row_count=row[30],
        integer_key=False,
        name="platform",
    )
    sources_domain_count = _as_int(row[31], "sources_domain_count")
    search_results_domain = _optional_family(row[33], row[32], "search_results_domain")
    brand_entities_title = _optional_family(row[35], row[34], "brand_entities_title")
    brand_entities_category = _optional_family(row[37], row[36], "brand_entities_category")
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
        raise IntegrityError("derived Evidence is not Target Metrics")
    request = _attempt_request(attempt)
    if request["keyword"] != requested_keyword:
        raise IntegrityError("Attempt keyword disagrees with history subject")
    _require_request_agreement(
        request,
        keyword=context_keyword,
        match_type=match_type,
        search_filter=search_filter,
        search_scope=search_scope,
        platform=platform,
        location_code=location_code,
        language_code=language_code,
        internal_list_limit=internal_list_limit,
        location_key=_as_int(location["key"], "location_key"),
        language_key=_as_text(language["key"], "language_key"),
        platform_key=_as_text(platform_group["key"], "platform_key"),
    )
    total, source_domains = _load_typed_facts(
        connection,
        capture_id,
        requested_keyword,
        observation_count,
        sources_domain_count,
    )
    result_context = {
        "total_count": total_count,
        "result_offset": result_offset,
        "items_count": items_count,
        "items_state": items_state,
        "location": location,
        "language": language,
        "platform": platform_group,
        "sources_domain_count": sources_domain_count,
        "search_results_domain": search_results_domain,
        "brand_entities_title": brand_entities_title,
        "brand_entities_category": brand_entities_category,
    }
    if set(result_context) != _CONTEXT_KEYS:
        raise IntegrityError("result_context keys are not closed")
    payload: dict[str, object] = {
        "attempt_id": attempt_id,
        "capture_id": capture_id,
        "provider": HISTORY_PROVIDER,
        "adapter_contract": HISTORY_ADAPTER,
        "derivation_version_id": TARGET_METRICS_RECIPE_ID,
        "authorized_at": _require_text(attempt, "authorized_at"),
        "request_started_at": _require_text(capture, "request_started_at"),
        "transport_ended_at": _require_text(capture, "transport_ended_at"),
        "request": request,
        "capture_outcome": {
            "classification": "observation_admitted",
            "observation_count": observation_count,
        },
        "result_context": result_context,
        "total": total,
        "source_domains": source_domains,
    }
    if set(payload) != _CAPTURE_KEYS:
        raise IntegrityError("Capture keys are not closed")
    return payload


def load_target_metrics_history(
    store: EvidenceStore,
    connection: Connection[Any],
    *,
    requested_keyword: str,
    pinned_version: str | None,
    limit: int,
    order: Literal["asc", "desc"],
) -> dict[str, object]:
    """Assemble surface-explicit Target Metrics history for one requested keyword."""

    resolved = resolve_provider_recipe(connection, HISTORY_ADAPTER, pinned_version)
    recipe = _load_validated_v1_recipe(connection, resolved)
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
            c.internal_list_limit,
            c.total_count,
            c.result_offset,
            c.items_count,
            c.items_state,
            c.location_key,
            c.location_mentions,
            c.location_ai_search_volume,
            c.location_provider_array_index,
            c.location_row_count,
            c.language_key,
            c.language_mentions,
            c.language_ai_search_volume,
            c.language_provider_array_index,
            c.language_row_count,
            c.platform_key,
            c.platform_mentions,
            c.platform_ai_search_volume,
            c.platform_provider_array_index,
            c.platform_row_count,
            c.sources_domain_count,
            c.search_results_domain_count,
            c.search_results_domain_state,
            c.brand_entities_title_count,
            c.brand_entities_title_state,
            c.brand_entities_category_count,
            c.brand_entities_category_state
        FROM target_metrics_result_context AS c
        LEFT JOIN outcomes AS o
          ON o.derivation_version_id = c.derivation_version_id
         AND o.attempt_id = c.attempt_id
         AND o.capture_id = c.capture_id
        WHERE c.requested_keyword = %s
          AND c.derivation_version_id = %s
        """,
        (requested_keyword, TARGET_METRICS_RECIPE_ID),
    ).fetchall()
    verified: list[tuple[str, str, dict[str, object]]] = []
    seen: set[str] = set()
    for row in rows:
        capture_id = _as_text(row[0], "capture_id")
        if capture_id in seen:
            raise IntegrityError("duplicate admitted Capture candidate")
        seen.add(capture_id)
        payload = _verify_capture(store, connection, row, requested_keyword)
        verified.append(
            (str(payload["request_started_at"]), capture_id, payload)
        )
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
        return TargetMetricsHistoryEnvelope.model_validate(payload).model_dump()
    except ValidationError as exc:
        raise IntegrityError("malformed Target Metrics history projection") from exc
