from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def database_root() -> Path:
    return Path(__file__).resolve().parents[2] / "database"
