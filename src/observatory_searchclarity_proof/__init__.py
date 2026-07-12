"""Local-only synthetic M15 SearchClarity evidence-support proof."""

from .errors import SearchClarityProofError
from .models import ReportSupportRequest
from .references import map_synthetic_report_safe_references, resolve_synthetic_reference
from .report_support import (
    build_report_support_pack,
    build_report_support_request,
    classify_report_support_disposition,
    serialize_report_support_pack,
    validate_customer_clean_request,
)

__all__ = [
    "ReportSupportRequest",
    "SearchClarityProofError",
    "build_report_support_pack",
    "build_report_support_request",
    "classify_report_support_disposition",
    "map_synthetic_report_safe_references",
    "resolve_synthetic_reference",
    "serialize_report_support_pack",
    "validate_customer_clean_request",
]
