from __future__ import annotations

import json
from pathlib import Path


def test_role_profile_is_closed_and_disposable(database_root: Path) -> None:
    data = json.loads((database_root / "hammer-profiles/db4_roles_v1.json").read_text(encoding="utf-8"))
    assert data["database_class"] == "disposable_postgres"
    assert data["role_profiles"] == ["db4_minimal_migration_roles_v1","db4_scope_isolation_roles_v1","db4_typed_read_roles_v1"]
    assert not ({"sql","command","password","credential"} & set(data))
