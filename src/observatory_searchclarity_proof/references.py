from __future__ import annotations

import hashlib

from .errors import SearchClarityProofError

_REFERENCE_SALT = "observatory-m15-synthetic-report-safe-v0.1"


def map_synthetic_report_safe_references(*, scope_id: str, evidence_ids: list[str]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for evidence_id in sorted(evidence_ids):
        digest = hashlib.sha256(f"{_REFERENCE_SALT}|{scope_id}|{evidence_id}".encode()).hexdigest()[:20]
        refs.append({
            "reference": f"rsf_{digest}",
            "reference_mode": "synthetic_report_safe_fixture",
            "scope_id": scope_id,
        })
    return refs


def resolve_synthetic_reference(*, scope_id: str, reference: str, evidence_ids: list[str]) -> str:
    mappings = map_synthetic_report_safe_references(scope_id=scope_id, evidence_ids=evidence_ids)
    for evidence_id, mapping in zip(sorted(evidence_ids), mappings, strict=True):
        if mapping["reference"] == reference:
            return evidence_id
    raise SearchClarityProofError("not_found")
