from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORWARD = ["001_identity_namespaces.sql","002_governance_scope.sql","003_capture_provider.sql","004_evidence_identity.sql","005_raw_support.sql","006_audit_append_only.sql","007_scope_rls_roles.sql","008_typed_read.sql","010_recovery_verification.sql"]
FIXTURES = ["009_missing_scope_boundary.sql","009_mutable_evidence.sql","009_missing_audit_pair.sql","009_excess_role_privilege.sql","009_unbounded_raw_locator.sql","009_dirty_constraint_seed.sql","009_partial_migration_failure.sql","009_schema_version_divergence.sql"]
PROFILES = ["db4_invariants_v1.json","db4_migration_v1.json","db4_roles_v1.json","db4_concurrency_v1.json","db4_restore_verification_v1.json"]


def expected_paths() -> set[str]:
    paths = {"database/README.md","database/migrations/README.md","database/rollbacks/README.md","database/hammer-fixtures/README.md","database/hammer-profiles/README.md","tests/postgres/README.md","tools/check_database_package.py","tests/test_database_package.py","tests/postgres/conftest.py","tests/postgres/test_db4_invariants.py","tests/postgres/test_db4_migrations.py","tests/postgres/test_db4_roles.py","tests/postgres/test_db4_concurrency.py","tests/postgres/test_db4_restore.py",".gitignore"}
    paths |= {f"database/migrations/{name}" for name in FORWARD}
    paths |= {f"database/rollbacks/{name}" for name in FORWARD}
    paths |= {f"database/hammer-fixtures/{name}" for name in FIXTURES}
    paths |= {f"database/hammer-profiles/{name}" for name in PROFILES}
    return paths


def _metadata(path: Path) -> dict[str, object]:
    first = path.read_text(encoding="utf-8").splitlines()[0]
    prefix = "-- observatory-db4: "
    if not first.startswith(prefix):
        raise ValueError(f"missing metadata: {path}")
    data = json.loads(first.removeprefix(prefix))
    required = {"version","direction","responsibility","paired_path","required_prior","resulting_version","database_class","transaction","proof_class","authority","namespaces","destructive"}
    if set(data) != required:
        raise ValueError(f"metadata keys mismatch: {path}")
    return data


def check() -> list[str]:
    errors: list[str] = []
    for rel in sorted(expected_paths()):
        if not (ROOT / rel).is_file():
            errors.append(f"missing:{rel}")
    for name in FORWARD:
        forward = ROOT / "database/migrations" / name
        rollback = ROOT / "database/rollbacks" / name
        if not forward.is_file() or not rollback.is_file():
            continue
        try:
            fmeta, rmeta = _metadata(forward), _metadata(rollback)
            if fmeta["direction"] != "forward" or rmeta["direction"] != "rollback":
                errors.append(f"direction:{name}")
            if fmeta["version"] != rmeta["version"] or fmeta["responsibility"] != rmeta["responsibility"]:
                errors.append(f"pair:{name}")
            if fmeta["database_class"] != "disposable_postgres" or rmeta["database_class"] != "disposable_postgres":
                errors.append(f"class:{name}")
            if "observatory_test_" not in (ROOT / "database/README.md").read_text(encoding="utf-8"):
                errors.append("prefix-boundary")
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
    mapped: set[str] = set()
    for name in PROFILES:
        path = ROOT / "database/hammer-profiles" / name
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            forbidden = {"sql","command","password","credential","host","port","executable"}
            if set(data) & forbidden:
                errors.append(f"forbidden-profile-key:{name}")
            if data.get("database_class") != "disposable_postgres" or data.get("target_prefix") != "observatory_test_":
                errors.append(f"profile-boundary:{name}")
            mapped.update(data.get("hammer_ids", []))
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(f"profile:{name}:{exc}")
    missing = {f"H{i}" for i in range(1, 23)} - mapped
    if missing:
        errors.append("missing-hammers:" + ",".join(sorted(missing)))
    if ".database-proof/" not in (ROOT / ".gitignore").read_text(encoding="utf-8"):
        errors.append("proof-root-not-ignored")
    return errors


if __name__ == "__main__":
    failures = check()
    if failures:
        raise SystemExit("\n".join(failures))
    print("database package check passed")
