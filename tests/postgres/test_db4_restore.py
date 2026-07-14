from __future__ import annotations

import json
from pathlib import Path


def test_restore_profile_requires_semantic_verification(database_root: Path) -> None:
    data = json.loads((database_root / "hammer-profiles/db4_restore_verification_v1.json").read_text(encoding="utf-8"))
    assert data["hammer_ids"] == ["restore-schema","restore-history","restore-semantic"]
    assert data["database_class"] == "disposable_postgres"
