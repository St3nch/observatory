"""Tests for the HTTP application boundary."""

import asyncio

import httpx

from observatory.api import create_app
from observatory.settings import Settings


def test_health_contract_reports_process_liveness() -> None:
    """The health route makes only a process-liveness claim."""

    async def request_health() -> httpx.Response:
        app = create_app(Settings(environment="test"))
        transport = httpx.ASGITransport(app=app)

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.get("/healthz")

    response = asyncio.run(request_health())

    assert response.status_code == 200
    assert response.json() == {
        "service": "observatory",
        "status": "ok",
        "version": "0.1.0",
    }
