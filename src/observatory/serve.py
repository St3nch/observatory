"""Development and production HTTP entry point."""

import uvicorn

from observatory.settings import get_settings


def main() -> None:
    """Run Observatory's HTTP service."""

    settings = get_settings()
    uvicorn.run(
        "observatory.api:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
    )


if __name__ == "__main__":
    main()
