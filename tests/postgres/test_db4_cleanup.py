from __future__ import annotations

import json
from pathlib import Path


def test_every_cleanup_reference_resolves(database_root: Path) -> None:
    profiles = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (database_root / "hammer-profiles").glob("db4-*.json")
    ]
    cleanup_ids = {
        check["check_id"]
        for profile in profiles
        for check in profile["checks"]
        if check["operation_class"] == "cleanup"
    }
    references = {
        check["cleanup_check_id"]
        for profile in profiles
        for check in profile["checks"]
        if check.get("cleanup_check_id") is not None
    }
    assert references <= cleanup_ids


def test_cleanup_profile_covers_real_spine_and_migration_probes(database_root: Path) -> None:
    data = json.loads((database_root / "hammer-profiles/db4-cleanup.json").read_text(encoding="utf-8"))
    ids = {check["check_id"] for check in data["checks"]}
    assert {
        "CLEANUP_ROLE_RLS_PROBE",
        "CLEANUP_ADMISSION_PROBE",
        "CLEANUP_EVIDENCE_PROBE",
        "CLEANUP_APPEND_ONLY_PROBE",
        "CLEANUP_CONCURRENCY_PROBE",
        "CLEANUP_MIGRATION_PROBE",
    } <= ids
