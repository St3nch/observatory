"""Local-only, fixture-backed M14 typed-read contract prototype."""

from .context_pack import assemble_context_pack
from .errors import ReadError
from .reader import (
    coverage_blind_spot_read,
    evidence_lookup,
    freshness_check,
    make_cursor,
    observation_package_read,
)

__all__ = [
    "ReadError",
    "assemble_context_pack",
    "coverage_blind_spot_read",
    "evidence_lookup",
    "freshness_check",
    "make_cursor",
    "observation_package_read",
]
