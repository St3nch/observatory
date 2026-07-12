class CrossCheckError(ValueError):
    """Closed, non-echoing M16 provider cross-check error."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code
