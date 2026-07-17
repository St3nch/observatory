from __future__ import annotations

import hashlib
import json
from pathlib import Path


def test_concrete_fixture_manifest_is_complete(database_root: Path) -> None:
    manifest = json.loads((database_root / "db4-remediation-conformance-manifest.json").read_text(encoding="utf-8"))
    rows = manifest["concrete_fixture_manifest"]
    fixtures = {path.name for path in (database_root / "hammer-fixtures").glob("009_*.sql")}
    assert {row["fixture"] for row in rows} == fixtures
    assert len(fixtures) == 16
    assert manifest["counts"]["hostile_candidate_obligations"] == 23
    assert manifest["counts"]["folded_behavioral_obligations"] == 7


def test_executor_bound_fixtures_are_sha_locked(database_root: Path) -> None:
    profile = json.loads((database_root / "hammer-profiles/db4-broken-candidates.json").read_text(encoding="utf-8"))
    assert len(profile["checks"]) == 8
    for check in profile["checks"]:
        path = database_root.parent / check["fixture_path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == check["fixture_sha256"]


def test_every_fixture_declares_rejection_and_cleanup_contract(database_root: Path) -> None:
    for path in (database_root / "hammer-fixtures").glob("009_*.sql"):
        text = path.read_text(encoding="utf-8")
        for field in (
            "fixture_id",
            "violated_invariant",
            "rejection_class",
            "rejection_point",
            "expected_sqlstate",
            "residue_relation",
            "history_expectation",
            "cleanup_expectation",
        ):
            assert f"-- {field}:" in text
