from __future__ import annotations


class OverlayProofError(ValueError):
    """Closed, non-echoing error for the synthetic M17 overlay proof."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)
