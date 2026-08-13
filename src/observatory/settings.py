"""Runtime configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
