from __future__ import annotations

from dataclasses import dataclass
from typing import Any

CONTRACT_VERSION = "0.1"
REQUEST_TYPE = "overlay_alignment"
ALLOWED_CALLERS = frozenset({"internal_llm", "operator", "searchclarity_internal"})
ALLOWED_KINDS = frozenset({
    "owned_internal_series",
    "customer_first_party_series",
    "intervention_timeline",
})
ALLOWED_USES = frozenset({"temporal_alignment", "bounded_value_alignment"})
ALLOWED_FRESHNESS = frozenset({"fresh", "stale"})
ALLOWED_FIELDS = frozenset({"timestamp", "value", "event_kind"})
REQUEST_FIELDS = frozenset({
    "contract_version",
    "request_type",
    "request_id",
    "caller_class",
    "scope_id",
    "overlay_kind",
    "external_overlay_reference",
    "overlay_supplied_by_consumer",
    "overlay_timestamp",
    "overlay_freshness_status",
    "overlay_scope_context",
    "overlay_no_storage_assertion",
    "overlay_discard_required",
    "overlay_allowed_use",
    "field_manifest",
    "values",
    "alignment_intent",
})


@dataclass(frozen=True)
class EvidenceWindow:
    evidence_id: str
    scope_id: str
    window_start: str
    window_end: str
    direction: str
    freshness_status: str
    coverage_warning: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "scope_id": self.scope_id,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "direction": self.direction,
            "freshness_status": self.freshness_status,
            "coverage_warning": self.coverage_warning,
        }
