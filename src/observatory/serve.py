"""Fixture/dev HTTP entry point. Loopback only; no production bind."""

from __future__ import annotations

from typing import Final

import uvicorn

from observatory.api import create_app
from observatory.settings import get_settings

LOOPBACK_HOSTS: Final[frozenset[str]] = frozenset({"127.0.0.1", "::1", "localhost"})


def bind_host(host: str) -> str:
    """Return *host* if it is loopback. Refuse any other bind address."""

    if host not in LOOPBACK_HOSTS:
        raise ValueError("fixture/dev API binds only to loopback (127.0.0.1)")
    return host


def main() -> None:
    """Run Observatory's read-only HTTP service on loopback."""

    settings = get_settings()
    host = bind_host(settings.host)
    if settings.database_url is None or settings.evidence_root is None:
        raise SystemExit(
            "OBSERVATORY_DATABASE_URL and OBSERVATORY_EVIDENCE_ROOT are required"
        )
    application = create_app(settings)
    uvicorn.run(
        application,
        host=host,
        port=settings.port,
        log_level=settings.log_level,
    )


if __name__ == "__main__":
    main()
