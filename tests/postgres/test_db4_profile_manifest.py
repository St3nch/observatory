from __future__ import annotations

import json
from pathlib import Path


ACTIVE = {
    "db4-preconditions.json",
    "db4-behavioral-core.json",
    "db4-broken-candidates.json",
    "db4-role-rls.json",
    "db4-concurrency.json",
    "db4-migration-history.json",
    "db4-cleanup.json",
    "db4-restore-semantic.json",
}


def test_only_current_profiles_exist(database_root: Path) -> None:
    actual = {path.name for path in (database_root / "hammer-profiles").glob("*.json")}
    assert actual == ACTIVE
    assert not any(name.endswith("_v1.json") for name in actual)


def test_current_profiles_are_closed_and_disposable(database_root: Path) -> None:
    for name in ACTIVE:
        data = json.loads((database_root / "hammer-profiles" / name).read_text(encoding="utf-8"))
        assert data["schema_version"] == "1"
        assert data["database_class"] == "disposable_postgres"
        assert data["proof_class"] in {"fixture_contract_pass", "real_postgres_disposable_pass"}
        assert data["checks"]
