"""Tests for the HTTP application boundary."""

import asyncio

import httpx
import pytest

from observatory.api import create_app
from observatory.serve import bind_host
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


def test_v1_health_is_process_liveness_only() -> None:
    from fastapi.testclient import TestClient

    app = create_app(Settings(environment="test", database_url=None, evidence_root=None))
    with TestClient(app) as client:
        response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_v1_routes_require_no_authentication() -> None:
    from fastapi.testclient import TestClient

    app = create_app(Settings(environment="test"))
    with TestClient(app) as client:
        response = client.get("/v1/health")
    assert response.status_code == 200
    assert "authorization" not in {key.lower() for key in response.request.headers}


def test_configured_bind_is_loopback() -> None:
    settings = Settings(environment="test")
    assert settings.host == "127.0.0.1"
    assert bind_host(settings.host) == "127.0.0.1"
    with pytest.raises(ValueError, match="loopback"):
        bind_host("0.0.0.0")
    with pytest.raises(ValueError, match="loopback"):
        bind_host("192.168.1.10")
