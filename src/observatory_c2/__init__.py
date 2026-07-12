"""C2 Controlled Public Manual Observation Package.

This package is intentionally tiny and local-only for M12.
It contains no provider clients, no database code, no API/MCP exposure,
no dashboard code, and no strategy/recommendation storage.
"""

from .c2 import (
    AdmissionResult,
    AuditEvent,
    CandidateObservation,
    EvidenceIdentity,
    ObservationPackage,
    RawSupportManifest,
    ScopeContext,
    ValidationIssue,
    admit_candidate_observation,
    recovery_snapshot_digest,
    validate_observation_package,
    validate_recovery_snapshot_digest,
)

__all__ = [
    "AdmissionResult",
    "AuditEvent",
    "CandidateObservation",
    "EvidenceIdentity",
    "ObservationPackage",
    "RawSupportManifest",
    "ScopeContext",
    "ValidationIssue",
    "admit_candidate_observation",
    "recovery_snapshot_digest",
    "validate_observation_package",
    "validate_recovery_snapshot_digest",
]
