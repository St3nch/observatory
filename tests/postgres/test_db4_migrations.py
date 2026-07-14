from __future__ import annotations

import json
from pathlib import Path


def test_forward_and_rollback_versions_are_paired(database_root: Path) -> None:
    forwards = sorted((database_root / "migrations").glob("[0-9][0-9][0-9]_*.sql"))
    rollbacks = sorted((database_root / "rollbacks").glob("[0-9][0-9][0-9]_*.sql"))
    assert [path.name for path in forwards] == [path.name for path in rollbacks]
    for forward, rollback in zip(forwards, rollbacks, strict=True):
        fmeta = json.loads(forward.read_text(encoding="utf-8").splitlines()[0].split(": ",1)[1])
        rmeta = json.loads(rollback.read_text(encoding="utf-8").splitlines()[0].split(": ",1)[1])
        assert fmeta["version"] == rmeta["version"]
        assert fmeta["direction"] == "forward"
        assert rmeta["direction"] == "rollback"
