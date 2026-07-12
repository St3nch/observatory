from __future__ import annotations

from dataclasses import dataclass

ERROR_CODES = {
    "blocked_authentication", "blocked_authorization", "blocked_scope",
    "blocked_request_type", "blocked_filter", "blocked_rights",
    "blocked_retention", "blocked_freshness", "blocked_claim_intent",
    "blocked_result_ceiling", "blocked_private_data",
    "blocked_not_implemented", "not_found",
}


@dataclass(frozen=True)
class ReadError(Exception):
    code: str
    message: str = "Request blocked."

    def __post_init__(self) -> None:
        if self.code not in ERROR_CODES:
            raise ValueError(f"unknown error code: {self.code}")

    def as_payload(self) -> dict[str, str]:
        return {"error": self.code, "message": self.message}
