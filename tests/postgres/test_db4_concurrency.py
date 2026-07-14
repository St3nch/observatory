from __future__ import annotations

import json
from pathlib import Path


def test_concurrency_profile_has_fixed_ceilings(database_root: Path) -> None:
    data = json.loads((database_root / "hammer-profiles/db4_concurrency_v1.json").read_text(encoding="utf-8"))
    assert data["max_workers"] == 2
    assert data["max_attempts"] == 2
    assert data["max_databases"] == 1
