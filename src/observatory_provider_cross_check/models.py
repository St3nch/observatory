from __future__ import annotations

from dataclasses import dataclass
from typing import Any

CONTRACT_VERSION = "0.1"
REQUEST_TYPES = {"provider_cross_check"}
FORBIDDEN_REQUEST_FLAGS = {
    "produce_truth": "blocked_truth_request",
    "select_winner": "blocked_winner_request",
    "compute_average": "blocked_average_or_consensus",
    "compute_consensus": "blocked_average_or_consensus",
    "compute_composite": "blocked_composite_request",
    "recommend_provider": "blocked_recommendation",
    "persist_result": "blocked_persistence",
}


@dataclass(frozen=True)
class ProviderSide:
    side_id: str
    scope_id: str
    provider_name: str
    provider_family: str
    endpoint_or_surface: str
    metric_name: str
    metric_value: Any
    metric_unit: str | None
    metric_definition: str | None
    metric_posture: str
    captured_at: str
    provider_reported_time: str | None
    freshness_status: str
    volatility_class: str
    rights_class: str
    retention_class: str
    source_admission_status: str
    evidence_status: str
    evidence_handle: str
    context: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "side_id": self.side_id,
            "provider_name": self.provider_name,
            "provider_family": self.provider_family,
            "endpoint_or_surface": self.endpoint_or_surface,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "metric_unit": self.metric_unit,
            "metric_definition": self.metric_definition,
            "metric_posture": self.metric_posture,
            "captured_at": self.captured_at,
            "provider_reported_time": self.provider_reported_time,
            "freshness_status": self.freshness_status,
            "volatility_class": self.volatility_class,
            "rights_class": self.rights_class,
            "retention_class": self.retention_class,
            "source_admission_status": self.source_admission_status,
            "evidence_status": self.evidence_status,
            "evidence_handle": self.evidence_handle,
            "context": dict(sorted(self.context.items())),
        }
