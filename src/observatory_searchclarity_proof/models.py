from __future__ import annotations

from dataclasses import dataclass
from typing import Any

CONTRACT_VERSION = "0.1.1"
REQUEST_TYPES = {
    "report_support_evidence_lookup",
    "report_support_observation_package",
    "report_support_freshness_check",
    "report_support_coverage_check",
}
CLAIM_INTENTS = {
    "historical_observation",
    "current_state_observation",
    "comparative_observation",
    "absence_statement",
    "provider_metric_statement",
    "ai_geo_sampled_observation",
}
ALLOWED_OUTPUT_USE = "searchclarity_internal_evidence_support_only"


@dataclass(frozen=True)
class ReportSupportRequest:
    contract_version: str
    request_id: str
    request_type: str
    scope_id: str
    claim_intent: str
    current_or_historical_use: str
    requested_evidence_families: tuple[str, ...]
    freshness_requirement: str
    report_support_purpose_code: str
    allowed_output_use: str
    evidence_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "request_id": self.request_id,
            "request_type": self.request_type,
            "scope_id": self.scope_id,
            "claim_intent": self.claim_intent,
            "current_or_historical_use": self.current_or_historical_use,
            "requested_evidence_families": list(self.requested_evidence_families),
            "freshness_requirement": self.freshness_requirement,
            "report_support_purpose_code": self.report_support_purpose_code,
            "allowed_output_use": self.allowed_output_use,
            "evidence_id": self.evidence_id,
        }
