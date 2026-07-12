from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

CONTRACT_VERSION = "0.1.1"
REQUEST_TYPES = {
    "evidence_lookup", "observation_package_read", "freshness_check",
    "coverage_blind_spot_read",
}
CLAIM_INTENTS = {
    "historical_observation", "current_state_observation",
    "comparative_observation", "coverage_statement", "absence_statement",
    "internal_governance_support",
}


@dataclass(frozen=True)
class CallerGrant:
    caller_class: str
    scopes: frozenset[str]
    request_types: frozenset[str]


@dataclass(frozen=True)
class EvidenceUnit:
    evidence_id: str
    observation_id: str
    scope_id: str
    scope_class: str
    evidence_status: str
    source_family: str
    provider_or_capture_instrument: str
    captured_at: str
    provider_reported_at: str | None
    provider_attribution: str
    observed_content_untrusted: Any
    freshness_status: str
    volatility_class: str
    rights_class: str
    retention_class: str
    raw_support_status: str
    claim_status: str
    claim_use_warning: str
    sample_bound_warning: str
    absence_warning: str
    incomparability_warning: str
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "observation_id": self.observation_id,
            "evidence_status": self.evidence_status,
            "source_family": self.source_family,
            "provider_or_capture_instrument": self.provider_or_capture_instrument,
            "captured_at": self.captured_at,
            "provider_reported_at": self.provider_reported_at,
            "provider_attribution": self.provider_attribution,
            "observed_content_untrusted": self.observed_content_untrusted,
            "freshness_status": self.freshness_status,
            "volatility_class": self.volatility_class,
            "rights_class": self.rights_class,
            "retention_class": self.retention_class,
            "raw_support_status": self.raw_support_status,
            "claim_status": self.claim_status,
            "claim_use_warning": self.claim_use_warning,
            "sample_bound_warning": self.sample_bound_warning,
            "absence_warning": self.absence_warning,
            "incomparability_warning": self.incomparability_warning,
            "warnings": sorted(set(self.warnings)),
        }
