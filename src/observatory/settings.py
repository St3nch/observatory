"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

import base64
import os
from functools import lru_cache
from pathlib import Path
from typing import Final, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DATAFORSEO_LOGIN_ENV: Final[str] = "OBSERVATORY_DATAFORSEO_LOGIN"
DATAFORSEO_PASSWORD_ENV: Final[str] = "OBSERVATORY_DATAFORSEO_PASSWORD"


class CredentialError(ValueError):
    """Required DataForSEO sandbox credentials are missing or empty."""


class DataForSEOCredentials:
    """Memory-only sandbox credentials. Values never appear in repr or str."""

    __slots__ = ("_login", "_password")
    _login: str
    _password: str

    def __init__(self, login: str, password: str) -> None:
        object.__setattr__(self, "_login", login)
        object.__setattr__(self, "_password", password)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("credentials are immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("credentials are immutable")

    def __repr__(self) -> str:
        return "DataForSEOCredentials(<redacted>)"

    def __str__(self) -> str:
        return "DataForSEOCredentials(<redacted>)"

    def basic_authorization_header(self) -> str:
        token = base64.b64encode(f"{self._login}:{self._password}".encode()).decode(
            "ascii"
        )
        return f"Basic {token}"


def load_dataforseo_credentials() -> DataForSEOCredentials:
    """Load sandbox credentials from the two named environment variables."""

    login = os.environ.get(DATAFORSEO_LOGIN_ENV, "")
    password = os.environ.get(DATAFORSEO_PASSWORD_ENV, "")
    if login == "" or password == "":
        raise CredentialError(
            "OBSERVATORY_DATAFORSEO_LOGIN and OBSERVATORY_DATAFORSEO_PASSWORD "
            "are required and must be non-empty"
        )
    return DataForSEOCredentials(login, password)


class Settings(BaseSettings):
    """Validated process configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="OBSERVATORY_",
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"
    host: str = "127.0.0.1"
    port: int = Field(default=8080, ge=1, le=65535)
    log_level: Literal["critical", "error", "warning", "info", "debug", "trace"] = "info"
    database_url: str | None = None
    evidence_root: Path | None = None
    derivation_version_id: str = Field(
        default="fixture-panel-v1-derive-v1",
        pattern=r"^[A-Za-z0-9._+:-]{1,128}$",
    )
    api_prefix: str = "/api/v1"


@lru_cache
def get_settings() -> Settings:
    """Return one validated settings object per process."""

    return Settings()
