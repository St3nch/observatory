from __future__ import annotations

import json
from pathlib import Path


def test_role_profile_declares_cross_scope_and_privilege_denials(database_root: Path) -> None:
    data = json.loads((database_root / "hammer-profiles/db4-role-rls.json").read_text(encoding="utf-8"))
    check_ids = {check["check_id"] for check in data["checks"]}
    assert {
        "ROLE_PROFILES_EXACT",
        "READER_SAME_SCOPE_ALLOWED",
        "READER_CROSS_SCOPE_DENIED",
        "READER_WRITE_DENIED",
        "INGEST_WITH_CHECK_ENFORCED",
        "OWNER_BYPASS_BLOCKED",
    } <= check_ids


def test_scope_bound_children_force_rls(database_root: Path) -> None:
    migration = (database_root / "migrations/007_scope_rls_roles.sql").read_text(encoding="utf-8")
    relations = (
        "obs_evidence.observed_artifact_reference",
        "obs_evidence.admission_transition",
        "obs_evidence.observation_transition",
        "obs_evidence.evidence_identity",
        "obs_evidence.citation_handle",
        "obs_raw.raw_payload_identity",
        "obs_raw.opaque_artifact_token",
        "obs_raw.raw_integrity_observation",
    )
    for relation in relations:
        assert f"ALTER TABLE {relation} FORCE ROW LEVEL SECURITY;" in migration
    assert "USING (true)" not in migration
