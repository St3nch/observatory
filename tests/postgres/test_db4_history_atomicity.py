from __future__ import annotations

import json
from pathlib import Path


def test_history_profile_declares_atomic_failure_and_rewrite_checks(database_root: Path) -> None:
    data = json.loads((database_root / "hammer-profiles/db4-migration-history.json").read_text(encoding="utf-8"))
    check_ids = {check["check_id"] for check in data["checks"]}
    assert {
        "FORWARD_HISTORY_ATOMIC",
        "FAILED_CANDIDATE_NO_HISTORY",
        "DUPLICATE_VERSION_CHANGED_SHA_DENIED",
        "ROLLBACK_HISTORY_EXPLICIT",
    } <= check_ids
    assert data["proof_class"] == "real_postgres_disposable_pass"


def test_history_table_is_append_only_and_runner_owned(database_root: Path) -> None:
    migration = (database_root / "migrations/001_identity_namespaces.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE obs_meta.schema_migration" in migration
    assert "CREATE TRIGGER schema_migration_append_only" in migration
    assert "FOR EACH ROW EXECUTE FUNCTION obs_meta.reject_mutation()" in migration
    assert "BEGIN;" not in migration and "COMMIT;" not in migration
