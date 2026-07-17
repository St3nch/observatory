from __future__ import annotations

import json
from pathlib import Path


def test_result_and_campaign_schemas_are_closed(database_root: Path) -> None:
    proof_root = database_root / "proof"
    for name in ("result-register.schema.json", "campaign-register.schema.json", "supersession.schema.json"):
        data = json.loads((proof_root / name).read_text(encoding="utf-8"))
        assert data["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert data["type"] == "object"
        assert data["additionalProperties"] is False
        assert set(data["required"]) <= set(data["properties"])


def test_result_register_requires_execution_identity_and_check_records(database_root: Path) -> None:
    data = json.loads((database_root / "proof/result-register.schema.json").read_text(encoding="utf-8"))
    required = set(data["required"])
    assert {
        "schema_version",
        "execution_id",
        "campaign_id",
        "profile_id",
        "profile_sha256",
        "checks",
        "reviewer_state",
    } <= required
    check_required = set(data["$defs"]["check"]["required"])
    assert {"check_id", "hammer_ids", "result", "expected", "observed", "sqlstate"} <= check_required
