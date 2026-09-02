"""HTTP application boundary: read-only fixture/dev API."""

from __future__ import annotations

import re
from typing import Any, Final, Literal

import psycopg
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel

from observatory import __version__
from observatory.capture_event import (
    HISTORICAL_ADAPTER_CONTRACT,
    MENTIONS_ADAPTER_CONTRACT,
    ORGANIC_ADAPTER_CONTRACT,
    RANKED_KEYWORDS_ADAPTER_CONTRACT,
    RELATED_KEYWORDS_ADAPTER_CONTRACT,
    TARGET_METRICS_ADAPTER_CONTRACT,
)
from observatory.dataforseo_google_organic import (
    GOOGLE_ORGANIC_EXPANDED_RECIPE_ID,
)
from observatory.evidence_store import EvidenceStore, IntegrityError, open_store
from observatory.google_organic_read import (
    GoogleOrganicExpandedHistoryEnvelope,
    load_google_organic_history,
    load_google_organic_holdings,
    load_google_organic_outcomes,
)
from observatory.keyword_overview_read import (
    HISTORY_ADAPTER,
    ProviderAttemptNotFound,
    load_keyword_overview_history,
    load_keyword_overview_holdings,
    load_keyword_overview_outcomes,
    load_provider_attempt,
)
from observatory.llm_mentions_historical_read import (
    HistoricalHistoryEnvelope,
    load_llm_mentions_historical_history,
)
from observatory.provider_history import (
    HISTORY_LIMIT_DEFAULT,
    HISTORY_LIMIT_MAX,
    HistoryListEnvelope,
)
from observatory.provider_holdings import (
    HOLDINGS_QUERY_KEYS,
    GoogleOrganicHoldingsEnvelope,
    KeywordOverviewHoldingsEnvelope,
    SearchMentionsHoldingsEnvelope,
)
from observatory.provider_outcomes import (
    GoogleOrganicOutcomesEnvelope,
    KeywordOverviewOutcomesEnvelope,
    SearchMentionsOutcomesEnvelope,
)
from observatory.provider_recipe_selection import (
    NOT_SELECTED_SIGNAL,
    ProviderRecipeNotSelected,
    ProviderRecipeSelectionError,
)
from observatory.ranked_keywords_read import (
    RankedKeywordsHistoryEnvelope,
    load_ranked_keywords_history,
)
from observatory.related_keywords_read import (
    RelatedKeywordsHistoryEnvelope,
    load_related_keywords_history,
)
from observatory.search_mentions_read import (
    load_search_mentions_history,
    load_search_mentions_holdings,
    load_search_mentions_outcomes,
)
from observatory.settings import Settings, get_settings
from observatory.target_metrics_read import (
    TargetMetricsHistoryEnvelope,
    load_target_metrics_history,
)

_HEX64: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_PROVIDER_ATTEMPT_ADAPTERS: Final[frozenset[str]] = frozenset(
    {
        HISTORY_ADAPTER,
        ORGANIC_ADAPTER_CONTRACT,
        MENTIONS_ADAPTER_CONTRACT,
        TARGET_METRICS_ADAPTER_CONTRACT,
        HISTORICAL_ADAPTER_CONTRACT,
        RELATED_KEYWORDS_ADAPTER_CONTRACT,
        RANKED_KEYWORDS_ADAPTER_CONTRACT,
    }
)
_FIXTURE_ADAPTER: Final[str] = "fixture-panel-v1"
_FIXTURE_PROVIDER: Final[str] = "fixture"
INTEGRITY_SIGNAL: Final[str] = "evidence_integrity_failure"


class HealthResponse(BaseModel):
    """Process-liveness payload used by the pre-existing /healthz route."""

    status: Literal["ok"]
    service: Literal["observatory"]
    version: str


class OutcomeEnvelope(BaseModel):
    attempt_id: str
    capture_id: str | None
    derivation_version_id: str
    classification: str
    observation_count: int


class ObservationEnvelope(BaseModel):
    capture_id: str
    derivation_version_id: str
    within_capture_result_id: str
    attempt_id: str
    provider: str
    panel_id: str
    subject_key: str
    result_index: int
    label: str
    score: int


class AttemptResource(BaseModel):
    attempt_id: str
    derivation_version_id: str
    attempt_outcome: OutcomeEnvelope
    capture_outcome: OutcomeEnvelope | None
    observations: list[ObservationEnvelope]


def _read_connect(dsn: str) -> psycopg.Connection[Any]:
    return psycopg.connect(dsn, options="-c default_transaction_read_only=on")


def _as_int(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    return value


def _outcome_envelope(row: tuple[object, ...]) -> OutcomeEnvelope:
    capture_id = row[1]
    return OutcomeEnvelope(
        attempt_id=str(row[0]),
        capture_id=None if capture_id is None else str(capture_id),
        derivation_version_id=str(row[2]),
        classification=str(row[3]),
        observation_count=_as_int(row[4], "observation_count"),
    )


def _observation_envelope(row: tuple[object, ...]) -> ObservationEnvelope:
    return ObservationEnvelope(
        capture_id=str(row[0]),
        derivation_version_id=str(row[1]),
        within_capture_result_id=str(row[2]),
        attempt_id=str(row[3]),
        provider=str(row[4]),
        panel_id=str(row[5]),
        subject_key=str(row[6]),
        result_index=_as_int(row[7], "result_index"),
        label=str(row[8]),
        score=_as_int(row[9], "score"),
    )


def _require_store(request: Request) -> EvidenceStore:
    store = getattr(request.app.state, "store", None)
    if isinstance(store, EvidenceStore):
        return store
    raise HTTPException(status_code=503, detail="evidence store is not configured")


def _require_dsn(settings: Settings) -> str:
    if settings.database_url is None:
        raise HTTPException(status_code=503, detail="database URL is not configured")
    return settings.database_url


def _reject_undeclared_holdings_query(request: Request) -> None:
    extras = [key for key in request.query_params if key not in HOLDINGS_QUERY_KEYS]
    if extras:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "type": "extra_forbidden",
                    "loc": ["query", extras[0]],
                    "msg": "Query keys other than limit and order are not permitted",
                    "input": request.query_params.get(extras[0]),
                }
            ],
        )


def _recipe_http_error(exc: ProviderRecipeSelectionError) -> HTTPException:
    if isinstance(exc, ProviderRecipeNotSelected):
        return HTTPException(status_code=503, detail=NOT_SELECTED_SIGNAL)
    return HTTPException(status_code=404, detail="not found")


def _verify_backing(
    store: EvidenceStore, attempt_id: str, capture_ids: set[str]
) -> None:
    try:
        attempt = store.read_attempt(attempt_id)
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc
    if attempt is None:
        raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL)
    if (
        attempt.get("provider") != _FIXTURE_PROVIDER
        or attempt.get("adapter_contract") != _FIXTURE_ADAPTER
    ):
        raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL)
    for capture_id in sorted(capture_ids):
        try:
            capture = store.read_capture(capture_id)
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc
        if capture is None:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL)
        if capture.get("attempt_id") != attempt_id:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL)
        if (
            capture.get("provider") != _FIXTURE_PROVIDER
            or capture.get("adapter_contract") != _FIXTURE_ADAPTER
        ):
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL)


def create_app(settings: Settings | None = None, *, store: EvidenceStore | None = None) -> FastAPI:
    """Create an isolated application instance."""

    runtime = settings or get_settings()
    if store is None and runtime.evidence_root is not None:
        store = open_store(runtime.evidence_root)
    application = FastAPI(
        title="Observatory",
        version=__version__,
        docs_url=f"{runtime.api_prefix}/docs",
        openapi_url=f"{runtime.api_prefix}/openapi.json",
    )
    application.state.settings = runtime
    application.state.store = store

    operations = APIRouter(tags=["operations"])

    @operations.get("/healthz", response_model=HealthResponse)
    async def healthz() -> HealthResponse:
        """Report process liveness without claiming dependency health."""

        return HealthResponse(status="ok", service="observatory", version=__version__)

    application.include_router(operations)

    v1 = APIRouter(tags=["v1"])

    @v1.get("/health")
    async def health() -> dict[str, str]:
        """Process liveness only. Does not inspect PostgreSQL or Evidence."""

        return {"status": "ok"}

    @v1.get("/attempts/{attempt_id}")
    async def get_attempt_resource(
        attempt_id: str,
        request: Request,
        derivation_version_id: str | None = Query(default=None),
    ) -> AttemptResource | dict[str, object]:
        if _HEX64.fullmatch(attempt_id) is None:
            raise HTTPException(status_code=404, detail="not found")
        settings = request.app.state.settings
        if not isinstance(settings, Settings):
            raise HTTPException(status_code=503, detail="settings are not configured")
        evidence = _require_store(request)
        try:
            attempt = evidence.read_attempt(attempt_id)
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc
        if attempt is None:
            dsn = _require_dsn(settings)
            with _read_connect(dsn) as connection:
                derived = connection.execute(
                    "SELECT 1 FROM outcomes WHERE attempt_id = %s LIMIT 1",
                    (attempt_id,),
                ).fetchone()
            if derived is not None:
                raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL)
        elif attempt.get("adapter_contract") in _PROVIDER_ATTEMPT_ADAPTERS:
            return _provider_attempt_resource(
                settings,
                evidence,
                attempt,
                attempt_id,
                derivation_version_id,
            )
        return _fixture_attempt_resource(
            settings, evidence, attempt_id, settings.derivation_version_id
        )

    @v1.get("/providers/dataforseo/google/keyword-overview/history")
    async def get_keyword_overview_history(
        request: Request,
        requested_keyword: str = Query(),
        derivation_version_id: str | None = Query(default=None),
        limit: int = Query(default=HISTORY_LIMIT_DEFAULT, ge=1, le=HISTORY_LIMIT_MAX),
        order: Literal["asc", "desc"] = Query(default="asc"),
    ) -> HistoryListEnvelope:
        settings = request.app.state.settings
        if not isinstance(settings, Settings):
            raise HTTPException(status_code=503, detail="settings are not configured")
        evidence = _require_store(request)
        dsn = _require_dsn(settings)
        try:
            with _read_connect(dsn) as connection:
                return HistoryListEnvelope.model_validate(
                    load_keyword_overview_history(
                        evidence,
                        connection,
                        requested_keyword=requested_keyword,
                        pinned_version=derivation_version_id,
                        limit=limit,
                        order=order,
                    )
                )
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc
        except ProviderRecipeSelectionError as exc:
            raise _recipe_http_error(exc) from exc

    @v1.get("/providers/dataforseo/google/organic/history")
    async def get_google_organic_history(
        request: Request,
        requested_keyword: str = Query(),
        derivation_version_id: str | None = Query(default=None),
        limit: int = Query(default=HISTORY_LIMIT_DEFAULT, ge=1, le=HISTORY_LIMIT_MAX),
        order: Literal["asc", "desc"] = Query(default="asc"),
    ) -> GoogleOrganicExpandedHistoryEnvelope | HistoryListEnvelope:
        """Serve Google Organic history under whichever Recipe resolved.

        The accepted v1 Recipe keeps returning the unchanged v1 document; the PF-18
        expanded Recipe returns the fully typed expanded document.
        """

        settings = request.app.state.settings
        if not isinstance(settings, Settings):
            raise HTTPException(status_code=503, detail="settings are not configured")
        evidence = _require_store(request)
        dsn = _require_dsn(settings)
        try:
            with _read_connect(dsn) as connection:
                document = load_google_organic_history(
                    evidence,
                    connection,
                    requested_keyword=requested_keyword,
                    pinned_version=derivation_version_id,
                    limit=limit,
                    order=order,
                )
            if document.get("derivation_version_id") == GOOGLE_ORGANIC_EXPANDED_RECIPE_ID:
                return GoogleOrganicExpandedHistoryEnvelope.model_validate(document)
            return HistoryListEnvelope.model_validate(document)
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc
        except ProviderRecipeSelectionError as exc:
            raise _recipe_http_error(exc) from exc

    @v1.get("/providers/dataforseo/google/ai-optimization/search-mentions/history")
    async def get_search_mentions_history(
        request: Request,
        requested_keyword: str = Query(),
        derivation_version_id: str | None = Query(default=None),
        limit: int = Query(default=HISTORY_LIMIT_DEFAULT, ge=1, le=HISTORY_LIMIT_MAX),
        order: Literal["asc", "desc"] = Query(default="asc"),
    ) -> HistoryListEnvelope:
        settings = request.app.state.settings
        if not isinstance(settings, Settings):
            raise HTTPException(status_code=503, detail="settings are not configured")
        evidence = _require_store(request)
        dsn = _require_dsn(settings)
        try:
            with _read_connect(dsn) as connection:
                return HistoryListEnvelope.model_validate(
                    load_search_mentions_history(
                        evidence,
                        connection,
                        requested_keyword=requested_keyword,
                        pinned_version=derivation_version_id,
                        limit=limit,
                        order=order,
                    )
                )
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc
        except ProviderRecipeSelectionError as exc:
            raise _recipe_http_error(exc) from exc

    @v1.get("/providers/dataforseo/google/ai-optimization/target-metrics/history")
    async def get_target_metrics_history(
        request: Request,
        requested_keyword: str = Query(min_length=1),
        derivation_version_id: str | None = Query(default=None),
        limit: int = Query(default=HISTORY_LIMIT_DEFAULT, ge=1, le=HISTORY_LIMIT_MAX),
        order: Literal["asc", "desc"] = Query(default="asc"),
    ) -> TargetMetricsHistoryEnvelope:
        settings = request.app.state.settings
        if not isinstance(settings, Settings):
            raise HTTPException(status_code=503, detail="settings are not configured")
        evidence = _require_store(request)
        dsn = _require_dsn(settings)
        try:
            with _read_connect(dsn) as connection:
                return TargetMetricsHistoryEnvelope.model_validate(
                    load_target_metrics_history(
                        evidence,
                        connection,
                        requested_keyword=requested_keyword,
                        pinned_version=derivation_version_id,
                        limit=limit,
                        order=order,
                    )
                )
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc
        except ProviderRecipeSelectionError as exc:
            raise _recipe_http_error(exc) from exc

    @v1.get("/providers/dataforseo/google/ai-optimization/llm-mentions-historical/history")
    async def get_llm_mentions_historical_history(
        request: Request,
        requested_keyword: str = Query(min_length=1),
        derivation_version_id: str | None = Query(default=None),
        limit: int = Query(default=HISTORY_LIMIT_DEFAULT, ge=1, le=HISTORY_LIMIT_MAX),
        order: Literal["asc", "desc"] = Query(default="asc"),
    ) -> HistoricalHistoryEnvelope:
        settings = request.app.state.settings
        if not isinstance(settings, Settings):
            raise HTTPException(status_code=503, detail="settings are not configured")
        evidence = _require_store(request)
        dsn = _require_dsn(settings)
        try:
            with _read_connect(dsn) as connection:
                return HistoricalHistoryEnvelope.model_validate(
                    load_llm_mentions_historical_history(
                        evidence,
                        connection,
                        requested_keyword=requested_keyword,
                        pinned_version=derivation_version_id,
                        limit=limit,
                        order=order,
                    )
                )
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc
        except ProviderRecipeSelectionError as exc:
            raise _recipe_http_error(exc) from exc

    @v1.get("/providers/dataforseo/google/related-keywords/history")
    async def get_related_keywords_history(
        request: Request,
        requested_keyword: str = Query(min_length=1),
        derivation_version_id: str | None = Query(default=None),
        limit: int = Query(default=HISTORY_LIMIT_DEFAULT, ge=1, le=HISTORY_LIMIT_MAX),
        order: Literal["asc", "desc"] = Query(default="asc"),
    ) -> RelatedKeywordsHistoryEnvelope:
        settings = request.app.state.settings
        if not isinstance(settings, Settings):
            raise HTTPException(status_code=503, detail="settings are not configured")
        evidence = _require_store(request)
        dsn = _require_dsn(settings)
        try:
            with _read_connect(dsn) as connection:
                return RelatedKeywordsHistoryEnvelope.model_validate(
                    load_related_keywords_history(
                        evidence,
                        connection,
                        requested_keyword=requested_keyword,
                        pinned_version=derivation_version_id,
                        limit=limit,
                        order=order,
                    )
                )
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc
        except ProviderRecipeSelectionError as exc:
            raise _recipe_http_error(exc) from exc

    @v1.get("/providers/dataforseo/google/ranked-keywords/history")
    async def get_ranked_keywords_history(
        request: Request,
        requested_target: str = Query(min_length=1),
        derivation_version_id: str | None = Query(default=None),
        limit: int = Query(default=HISTORY_LIMIT_DEFAULT, ge=1, le=HISTORY_LIMIT_MAX),
        order: Literal["asc", "desc"] = Query(default="asc"),
    ) -> RankedKeywordsHistoryEnvelope:
        settings = request.app.state.settings
        if not isinstance(settings, Settings):
            raise HTTPException(status_code=503, detail="settings are not configured")
        evidence = _require_store(request)
        dsn = _require_dsn(settings)
        try:
            with _read_connect(dsn) as connection:
                return RankedKeywordsHistoryEnvelope.model_validate(
                    load_ranked_keywords_history(
                        evidence,
                        connection,
                        requested_target=requested_target,
                        pinned_version=derivation_version_id,
                        limit=limit,
                        order=order,
                    )
                )
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc
        except ProviderRecipeSelectionError as exc:
            raise _recipe_http_error(exc) from exc

    @v1.get("/providers/dataforseo/google/keyword-overview/outcomes")
    async def get_keyword_overview_outcomes(
        request: Request,
        requested_keyword: str = Query(),
        derivation_version_id: str | None = Query(default=None),
        limit: int = Query(default=HISTORY_LIMIT_DEFAULT, ge=1, le=HISTORY_LIMIT_MAX),
        order: Literal["asc", "desc"] = Query(default="asc"),
    ) -> KeywordOverviewOutcomesEnvelope:
        settings = request.app.state.settings
        if not isinstance(settings, Settings):
            raise HTTPException(status_code=503, detail="settings are not configured")
        evidence = _require_store(request)
        dsn = _require_dsn(settings)
        try:
            with _read_connect(dsn) as connection:
                return KeywordOverviewOutcomesEnvelope.model_validate(
                    load_keyword_overview_outcomes(
                        evidence,
                        connection,
                        requested_keyword=requested_keyword,
                        pinned_version=derivation_version_id,
                        limit=limit,
                        order=order,
                    )
                )
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc
        except ProviderRecipeSelectionError as exc:
            raise _recipe_http_error(exc) from exc

    @v1.get("/providers/dataforseo/google/organic/outcomes")
    async def get_google_organic_outcomes(
        request: Request,
        requested_keyword: str = Query(),
        derivation_version_id: str | None = Query(default=None),
        limit: int = Query(default=HISTORY_LIMIT_DEFAULT, ge=1, le=HISTORY_LIMIT_MAX),
        order: Literal["asc", "desc"] = Query(default="asc"),
    ) -> GoogleOrganicOutcomesEnvelope:
        settings = request.app.state.settings
        if not isinstance(settings, Settings):
            raise HTTPException(status_code=503, detail="settings are not configured")
        evidence = _require_store(request)
        dsn = _require_dsn(settings)
        try:
            with _read_connect(dsn) as connection:
                return GoogleOrganicOutcomesEnvelope.model_validate(
                    load_google_organic_outcomes(
                        evidence,
                        connection,
                        requested_keyword=requested_keyword,
                        pinned_version=derivation_version_id,
                        limit=limit,
                        order=order,
                    )
                )
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc
        except ProviderRecipeSelectionError as exc:
            raise _recipe_http_error(exc) from exc

    @v1.get(
        "/providers/dataforseo/google/ai-optimization/search-mentions/outcomes"
    )
    async def get_search_mentions_outcomes(
        request: Request,
        requested_keyword: str = Query(),
        derivation_version_id: str | None = Query(default=None),
        limit: int = Query(default=HISTORY_LIMIT_DEFAULT, ge=1, le=HISTORY_LIMIT_MAX),
        order: Literal["asc", "desc"] = Query(default="asc"),
    ) -> SearchMentionsOutcomesEnvelope:
        settings = request.app.state.settings
        if not isinstance(settings, Settings):
            raise HTTPException(status_code=503, detail="settings are not configured")
        evidence = _require_store(request)
        dsn = _require_dsn(settings)
        try:
            with _read_connect(dsn) as connection:
                return SearchMentionsOutcomesEnvelope.model_validate(
                    load_search_mentions_outcomes(
                        evidence,
                        connection,
                        requested_keyword=requested_keyword,
                        pinned_version=derivation_version_id,
                        limit=limit,
                        order=order,
                    )
                )
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc
        except ProviderRecipeSelectionError as exc:
            raise _recipe_http_error(exc) from exc

    @v1.get("/providers/dataforseo/google/keyword-overview/holdings")
    async def get_keyword_overview_holdings(
        request: Request,
        limit: int = Query(default=HISTORY_LIMIT_DEFAULT, ge=1, le=HISTORY_LIMIT_MAX),
        order: Literal["asc", "desc"] = Query(default="asc"),
        _: None = Depends(_reject_undeclared_holdings_query),
    ) -> KeywordOverviewHoldingsEnvelope:
        settings = request.app.state.settings
        if not isinstance(settings, Settings):
            raise HTTPException(status_code=503, detail="settings are not configured")
        evidence = _require_store(request)
        try:
            return KeywordOverviewHoldingsEnvelope.model_validate(
                load_keyword_overview_holdings(evidence, limit=limit, order=order)
            )
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc

    @v1.get("/providers/dataforseo/google/organic/holdings")
    async def get_google_organic_holdings(
        request: Request,
        limit: int = Query(default=HISTORY_LIMIT_DEFAULT, ge=1, le=HISTORY_LIMIT_MAX),
        order: Literal["asc", "desc"] = Query(default="asc"),
        _: None = Depends(_reject_undeclared_holdings_query),
    ) -> GoogleOrganicHoldingsEnvelope:
        settings = request.app.state.settings
        if not isinstance(settings, Settings):
            raise HTTPException(status_code=503, detail="settings are not configured")
        evidence = _require_store(request)
        try:
            return GoogleOrganicHoldingsEnvelope.model_validate(
                load_google_organic_holdings(evidence, limit=limit, order=order)
            )
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc

    @v1.get(
        "/providers/dataforseo/google/ai-optimization/search-mentions/holdings"
    )
    async def get_search_mentions_holdings(
        request: Request,
        limit: int = Query(default=HISTORY_LIMIT_DEFAULT, ge=1, le=HISTORY_LIMIT_MAX),
        order: Literal["asc", "desc"] = Query(default="asc"),
        _: None = Depends(_reject_undeclared_holdings_query),
    ) -> SearchMentionsHoldingsEnvelope:
        settings = request.app.state.settings
        if not isinstance(settings, Settings):
            raise HTTPException(status_code=503, detail="settings are not configured")
        evidence = _require_store(request)
        try:
            return SearchMentionsHoldingsEnvelope.model_validate(
                load_search_mentions_holdings(evidence, limit=limit, order=order)
            )
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc

    application.include_router(v1, prefix="/v1")
    return application


def _provider_attempt_resource(
    settings: Settings,
    evidence: EvidenceStore,
    attempt: dict[str, object],
    attempt_id: str,
    pinned_version: str | None,
) -> dict[str, object]:
    dsn = _require_dsn(settings)
    try:
        with _read_connect(dsn) as connection:
            view = load_provider_attempt(
                evidence, connection, attempt, attempt_id, pinned_version
            )
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail=INTEGRITY_SIGNAL) from exc
    except ProviderRecipeSelectionError as exc:
        raise _recipe_http_error(exc) from exc
    except ProviderAttemptNotFound as exc:
        raise HTTPException(status_code=404, detail="not found") from exc
    return view.as_json()


def _fixture_attempt_resource(
    settings: Settings,
    evidence: EvidenceStore,
    attempt_id: str,
    version: str,
) -> AttemptResource:
    dsn = _require_dsn(settings)
    with _read_connect(dsn) as connection:
        outcome_rows = connection.execute(
            """
            SELECT attempt_id, capture_id, derivation_version_id,
                   classification, observation_count
            FROM outcomes
            WHERE attempt_id = %s AND derivation_version_id = %s
            ORDER BY capture_id NULLS FIRST
            """,
            (attempt_id, version),
        ).fetchall()
        if not outcome_rows:
            raise HTTPException(status_code=404, detail="not found")
        observation_rows = connection.execute(
            """
            SELECT
                capture_id,
                derivation_version_id,
                within_capture_result_id,
                attempt_id,
                provider,
                panel_id,
                subject_key,
                result_index,
                label,
                score
            FROM observations
            WHERE attempt_id = %s AND derivation_version_id = %s
            ORDER BY result_index, within_capture_result_id
            """,
            (attempt_id, version),
        ).fetchall()
    attempt_stage: OutcomeEnvelope | None = None
    capture_stage: OutcomeEnvelope | None = None
    capture_ids: set[str] = set()
    for row in outcome_rows:
        envelope = _outcome_envelope(row)
        if envelope.capture_id is None:
            attempt_stage = envelope
        else:
            capture_stage = envelope
            capture_ids.add(envelope.capture_id)
    if attempt_stage is None:
        raise HTTPException(status_code=404, detail="not found")
    observations = [_observation_envelope(row) for row in observation_rows]
    for item in observations:
        capture_ids.add(item.capture_id)
    _verify_backing(evidence, attempt_id, capture_ids)
    return AttemptResource(
        attempt_id=attempt_id,
        derivation_version_id=version,
        attempt_outcome=attempt_stage,
        capture_outcome=capture_stage,
        observations=observations,
    )


app = create_app()
