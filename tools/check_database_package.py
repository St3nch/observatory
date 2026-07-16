from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

FORWARD = (
    "001_identity_namespaces.sql",
    "002_governance_scope.sql",
    "003_capture_provider.sql",
    "004_evidence_identity.sql",
    "005_raw_support.sql",
    "006_audit_append_only.sql",
    "007_scope_rls_roles.sql",
    "008_typed_read.sql",
    "010_recovery_verification.sql",
)

FIXTURES = (
    "009_dirty_constraint_seed.sql",
    "009_excess_role_privilege.sql",
    "009_missing_audit_pair.sql",
    "009_missing_scope_boundary.sql",
    "009_mutable_evidence.sql",
    "009_partial_migration_failure.sql",
    "009_schema_version_divergence.sql",
    "009_unbounded_raw_locator.sql",
)

PROFILES = (
    "db4-preconditions.json",
    "db4-behavioral-core.json",
    "db4-broken-candidates.json",
    "db4-role-rls.json",
    "db4-concurrency.json",
    "db4-migration-history.json",
    "db4-cleanup.json",
    "db4-restore-semantic.json",
)

PROOF_PATHS = (
    "database/proof/README.md",
    "database/proof/result-register.schema.json",
    "database/proof/campaign-register.schema.json",
    "database/proof/supersession.schema.json",
    "database/proof/accepted/.gitkeep",
)

FORBIDDEN_PROFILE_KEYS = {
    "sql",
    "query",
    "command",
    "executable",
    "executable_path",
    "password",
    "credential",
    "host",
    "port",
}

TRANSACTION_BOUNDARY = re.compile(r"(?im)^\s*(BEGIN|START\s+TRANSACTION|COMMIT|END|ROLLBACK)\s*;")
DOLLAR_QUOTED_BODY = re.compile(r"(?s)(\$[A-Za-z0-9_]*\$).*?\1")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
HAMMER_ID = re.compile(r"^H[0-9]+$")


def expected_paths() -> set[str]:
    paths = {
        ".gitignore",
        "database/README.md",
        "database/migrations/README.md",
        "database/rollbacks/README.md",
        "database/hammer-fixtures/README.md",
        "database/hammer-profiles/README.md",
        "tests/postgres/README.md",
        "tools/check_database_package.py",
        "tests/test_database_package.py",
        "tests/postgres/conftest.py",
        "tests/postgres/test_db4_invariants.py",
        "tests/postgres/test_db4_migrations.py",
        "tests/postgres/test_db4_roles.py",
        "tests/postgres/test_db4_concurrency.py",
        "tests/postgres/test_db4_restore.py",
        *PROOF_PATHS,
    }
    paths |= {f"database/migrations/{name}" for name in FORWARD}
    paths |= {f"database/rollbacks/{name}" for name in FORWARD}
    paths |= {f"database/hammer-fixtures/{name}" for name in FIXTURES}
    paths |= {f"database/hammer-profiles/{name}" for name in PROFILES}
    return paths


def _metadata(path: Path) -> dict[str, object]:
    first = path.read_text(encoding="utf-8").splitlines()[0]
    prefix = "-- observatory-db4: "
    if not first.startswith(prefix):
        raise ValueError(f"missing metadata:{path.relative_to(ROOT).as_posix()}")
    data = json.loads(first.removeprefix(prefix))
    required = {
        "version",
        "direction",
        "responsibility",
        "paired_path",
        "required_prior",
        "resulting_version",
        "database_class",
        "transaction",
        "proof_class",
        "authority",
        "namespaces",
        "destructive",
    }
    if set(data) != required:
        raise ValueError(f"metadata-keys:{path.relative_to(ROOT).as_posix()}")
    return data


def _contains_forbidden_key(value: object) -> bool:
    if isinstance(value, dict):
        return any(
            str(key).lower() in FORBIDDEN_PROFILE_KEYS or _contains_forbidden_key(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def _profile_errors(name: str, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "profile_id",
        "required_capability",
        "database_class",
        "proof_class",
        "result_schema_version",
        "checks",
    }
    if set(data) != required:
        errors.append(f"profile-keys:{name}")
        return errors
    if data["schema_version"] != "1" or data["result_schema_version"] != "1":
        errors.append(f"profile-version:{name}")
    if data["database_class"] != "disposable_postgres":
        errors.append(f"profile-boundary:{name}")
    if _contains_forbidden_key(data):
        errors.append(f"forbidden-profile-key:{name}")
    checks = data.get("checks")
    if not isinstance(checks, list) or not checks:
        errors.append(f"profile-checks:{name}")
        return errors
    check_ids: set[str] = set()
    for check in checks:
        if not isinstance(check, dict):
            errors.append(f"profile-check-type:{name}")
            continue
        check_id = check.get("check_id")
        if not isinstance(check_id, str) or check_id in check_ids:
            errors.append(f"profile-check-id:{name}:{check_id}")
        else:
            check_ids.add(check_id)
        hammer_ids = check.get("hammer_ids")
        if not isinstance(hammer_ids, list) or not hammer_ids or any(
            not isinstance(item, str) or not HAMMER_ID.fullmatch(item) for item in hammer_ids
        ):
            errors.append(f"profile-hammers:{name}:{check_id}")
        fixture_path = check.get("fixture_path")
        fixture_sha = check.get("fixture_sha256")
        if (fixture_path is None) != (fixture_sha is None):
            errors.append(f"fixture-pair:{name}:{check_id}")
        if fixture_path is not None:
            if not isinstance(fixture_path, str) or not fixture_path.startswith("database/hammer-fixtures/"):
                errors.append(f"fixture-path:{name}:{check_id}")
                continue
            candidate = ROOT / fixture_path
            if not candidate.is_file():
                errors.append(f"fixture-missing:{name}:{check_id}")
            elif not isinstance(fixture_sha, str) or not SHA256.fullmatch(fixture_sha):
                errors.append(f"fixture-sha-format:{name}:{check_id}")
            elif hashlib.sha256(candidate.read_bytes()).hexdigest() != fixture_sha:
                errors.append(f"fixture-sha-mismatch:{name}:{check_id}")
    return errors


def _has_embedded_transaction(text: str) -> bool:
    without_function_bodies = DOLLAR_QUOTED_BODY.sub("", text)
    return TRANSACTION_BOUNDARY.search(without_function_bodies) is not None


def _validate_json_schema_file(path: Path) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(ROOT).as_posix()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"schema-json:{rel}:{exc}"]
    if not isinstance(data, dict) or data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append(f"schema-draft:{rel}")
    if data.get("type") != "object" or data.get("additionalProperties") is not False:
        errors.append(f"schema-closed:{rel}")
    return errors


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
            if fmeta["transaction"] != "runner-owned" or rmeta["transaction"] != "runner-owned":
                errors.append(f"transaction-owner:{name}")
            if _has_embedded_transaction(forward.read_text(encoding="utf-8")):
                errors.append(f"embedded-transaction:forward:{name}")
            if _has_embedded_transaction(rollback.read_text(encoding="utf-8")):
                errors.append(f"embedded-transaction:rollback:{name}")
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))

    mapped: set[str] = set()
    cleanup_ids: set[str] = set()
    cleanup_refs: set[str] = set()
    for name in PROFILES:
        path = ROOT / "database/hammer-profiles" / name
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"profile-json:{name}:{exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"profile-object:{name}")
            continue
        errors.extend(_profile_errors(name, data))
        for check in data.get("checks", []):
            if not isinstance(check, dict):
                continue
            mapped.update(item for item in check.get("hammer_ids", []) if isinstance(item, str))
            if check.get("operation_class") == "cleanup" and isinstance(check.get("check_id"), str):
                cleanup_ids.add(check["check_id"])
            if isinstance(check.get("cleanup_check_id"), str):
                cleanup_refs.add(check["cleanup_check_id"])

    missing_hammers = {f"H{i}" for i in range(1, 23)} - mapped
    if missing_hammers:
        errors.append("missing-hammers:" + ",".join(sorted(missing_hammers)))
    missing_cleanup = cleanup_refs - cleanup_ids
    if missing_cleanup:
        errors.append("missing-cleanup:" + ",".join(sorted(missing_cleanup)))

    for name in FIXTURES:
        path = ROOT / "database/hammer-fixtures" / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if _has_embedded_transaction(text):
            errors.append(f"fixture-embedded-transaction:{name}")
        if not text.startswith("-- db4-broken-fixture: "):
            errors.append(f"fixture-marker:{name}")

    for rel in PROOF_PATHS:
        if rel.endswith(".schema.json") and (ROOT / rel).is_file():
            errors.extend(_validate_json_schema_file(ROOT / rel))

    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if ".database-proof/" not in gitignore:
        errors.append("proof-root-not-ignored")
    database_readme = (ROOT / "database/README.md").read_text(encoding="utf-8")
    if "observatory_test_" not in database_readme:
        errors.append("prefix-boundary")

    return sorted(set(errors))


if __name__ == "__main__":
    failures = check()
    if failures:
        raise SystemExit("\n".join(failures))
    print("database package check passed")
