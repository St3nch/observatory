from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "check_database_package.py"
SPEC = importlib.util.spec_from_file_location("check_database_package", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_exact_database_manifest_has_46_paths() -> None:
    assert len(module.expected_paths()) == 46


def test_database_package_validator_passes() -> None:
    assert module.check() == []


def test_governed_name_is_not_a_migration_target() -> None:
    for rel in module.expected_paths():
        if rel.endswith(".sql"):
            text = (module.ROOT / rel).read_text(encoding="utf-8")
            assert "CREATE DATABASE observatory" not in text
            assert "DROP DATABASE observatory" not in text
