from __future__ import annotations


class SearchClarityProofError(Exception):
    """Closed-vocabulary M15 proof error."""

    ALLOWED = {
        "blocked_request_type",
        "blocked_claim_intent",
        "blocked_customer_data",
        "blocked_private_data",
        "blocked_not_admitted",
        "blocked_report_content",
        "blocked_recommendation",
        "blocked_scope",
        "blocked_reference",
        "blocked_claim_support",
        "not_found",
    }

    def __init__(self, code: str) -> None:
        if code not in self.ALLOWED:
            raise ValueError(f"unsupported error code: {code}")
        self.code = code
        super().__init__(code)

    def as_dict(self) -> dict[str, str]:
        return {"error": self.code}
