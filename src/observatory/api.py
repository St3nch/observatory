"""HTTP application boundary."""

from typing import Literal

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

from observatory import __version__
from observatory.settings import Settings, get_settings


class HealthResponse(BaseModel):
    """Stable process-liveness response."""

    status: Literal["ok"]
    service: Literal["observatory"]
    version: str


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create an isolated application instance."""

    runtime = settings or get_settings()
    application = FastAPI(
        title="Observatory",
        version=__version__,
        docs_url=f"{runtime.api_prefix}/docs",
        openapi_url=f"{runtime.api_prefix}/openapi.json",
    )
    operations = APIRouter(tags=["operations"])

    @operations.get("/healthz", response_model=HealthResponse)
    async def health() -> HealthResponse:
        """Report process liveness without claiming dependency health."""

        return HealthResponse(status="ok", service="observatory", version=__version__)

    application.include_router(operations)
    return application


app = create_app()
