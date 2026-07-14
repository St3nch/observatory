from __future__ import annotations

import json
from pathlib import Path


def test_invariant_profile_maps_h1_through_h22(database_root: Path) -> None:
    data = json.loads((database_root / "hammer-profiles/db4_invariants_v1.json").read_text(encoding="utf-8"))
    assert set(data["hammer_ids"]) == {f"H{i}" for i in range(1, 23)}
    assert data["target_prefix"] == "observatory_test_"
