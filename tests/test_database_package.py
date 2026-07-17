from __future__ import annotations

import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "check_database_package.py"
SPEC = importlib.util.spec_from_file_location("check_database_package", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_exact_database_manifest_has_73_paths() -> None:
    assert len(module.expected_paths()) == 73


def test_r1_schema_corrections_are_structurally_present() -> None:
    assert module._validate_r1_schema_corrections() == []


def test_r2_behavioral_profiles_target_the_real_spine() -> None:
    assert module._validate_r2_real_spine() == []


def test_reconciliation_manifest_accounts_for_every_current_obligation() -> None:
    manifest = json.loads(module.CONFORMANCE_PATH.read_text(encoding="utf-8"))
    assert manifest["counts"] == {
        "hostile_candidate_obligations": 23,
        "present_concrete_fixtures": 16,
        "required_absent_fixtures": 0,
        "folded_behavioral_obligations": 7,
        "postgres_test_obligations": 6,
        "current_postgres_tests": 6,
        "required_absent_postgres_tests": 0,
        "active_profiles": 8,
        "stale_profiles": 0,
    }
    assert manifest["explicit_deferrals"] == []
    assert module._validate_conformance_manifest() == []


def test_r3_fixture_manifest_classifies_every_concrete_fixture() -> None:
    manifest = json.loads(module.CONFORMANCE_PATH.read_text(encoding="utf-8"))
    rows = manifest["concrete_fixture_manifest"]
    assert {row["fixture"] for row in rows} == set(module.FIXTURES)
    assert {row["rejection_class"] for row in rows} == {"postgresql_native", "runner_detected"}


def test_r4_retires_stale_profiles_and_installs_current_tests() -> None:
    manifest = json.loads(module.CONFORMANCE_PATH.read_text(encoding="utf-8"))
    assert manifest["stale_profiles_pending_r4_retirement"] == []
    assert manifest["required_absent_postgres_tests_for_r4"] == []
    assert len(manifest["current_postgres_tests"]) == 6


def test_g1_g5_corrections_are_complete_but_restart_review_is_pending() -> None:
    manifest = json.loads(module.CONFORMANCE_PATH.read_text(encoding="utf-8"))
    assert manifest["r5_gate_state"] == "compatibility_corrections_committed_restart_pending"
    assert manifest["ob_dev_compatibility_commit"] == "879529c27cad666099cf4f697eb7cbb56dec2279"
    assert manifest["r5_blockers"] == []
    draft = (module.ROOT / manifest["r5_owner_decision_draft"]).read_text(encoding="utf-8")
    assert "Status: draft — not accepted" in draft
    assert "Authorized operation classes: none" in draft


def test_database_package_validator_passes() -> None:
    assert module.check() == []


def test_governed_name_is_not_a_migration_target() -> None:
    for rel in module.expected_paths():
        if rel.endswith(".sql"):
            text = (module.ROOT / rel).read_text(encoding="utf-8")
            assert "CREATE DATABASE observatory" not in text
            assert "DROP DATABASE observatory" not in text


def test_runner_owns_every_transaction_boundary() -> None:
    for name in (*module.FORWARD, *module.FIXTURES):
        directory = "migrations" if name in module.FORWARD else "hammer-fixtures"
        text = (module.ROOT / "database" / directory / name).read_text(encoding="utf-8")
        assert module._has_embedded_transaction(text) is False
    for name in module.FORWARD:
        text = (module.ROOT / "database" / "rollbacks" / name).read_text(encoding="utf-8")
        assert module._has_embedded_transaction(text) is False


def test_broken_candidate_profile_sha_binds_all_sixteen_fixtures() -> None:
    profile = json.loads(
        (module.ROOT / "database/hammer-profiles/db4-broken-candidates.json").read_text(encoding="utf-8")
    )
    fixture_paths = {check["fixture_path"] for check in profile["checks"]}
    assert len(fixture_paths) == 16
    assert fixture_paths == {f"database/hammer-fixtures/{name}" for name in module.FIXTURES}


def test_role_profile_directly_exercises_backup_scope_behavior() -> None:
    profile = json.loads(
        (module.ROOT / "database/hammer-profiles/db4-role-rls.json").read_text(encoding="utf-8")
    )
    check_ids = {check["check_id"] for check in profile["checks"]}
    assert {"BACKUP_SAME_SCOPE_ALLOWED", "BACKUP_CROSS_SCOPE_DENIED"} <= check_ids


def test_proof_schemas_are_closed_draft_2020_12_objects() -> None:
    for rel in module.PROOF_PATHS:
        if not rel.endswith(".schema.json"):
            continue
        schema = json.loads((module.ROOT / rel).read_text(encoding="utf-8"))
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
