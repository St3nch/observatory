from __future__ import annotations

from observatory_typed_read_prototype.fixtures import SCOPE_A, SCOPE_B

SEARCHCLARITY_SCOPE = SCOPE_A
ISOLATED_SCOPE = SCOPE_B

ADMITTED_SOURCE_FAMILIES = {
    "controlled_public_manual",
    "provider_sanitized_structure",
}

SYNTHETIC_CASES = {
    "historical_public": {
        "evidence_id": "ev_a7f3c9d2",
        "claim_intent": "historical_observation",
        "family": "provider_sanitized_structure",
    },
    "fresh_public": {
        "evidence_id": "ev_f19b6e40",
        "claim_intent": "current_state_observation",
        "family": "controlled_public_manual",
    },
    "superseded_historical": {
        "evidence_id": "ev_82c1d4aa",
        "claim_intent": "historical_observation",
        "family": "controlled_public_manual",
    },
    "rights_blocked": {
        "evidence_id": "ev_739a1bce",
        "claim_intent": "historical_observation",
        "family": "controlled_public_manual",
    },
    "cross_scope": {
        "evidence_id": "ev_4dd93f71",
        "claim_intent": "historical_observation",
        "family": "controlled_public_manual",
    },
}

REQUIRED_CAVEAT_FIELDS = (
    "claim_use_warning",
    "sample_bound_warning",
    "absence_warning",
    "incomparability_warning",
)

PRIVATE_OR_CUSTOMER_FIELDS = {
    "customer_name",
    "customer_email",
    "customer_company",
    "shop_id",
    "account_id",
    "order_id",
    "report_id",
    "gig_id",
    "invoice_id",
    "payment_id",
    "delivery_id",
    "revision_id",
    "private_analytics",
    "screenshot_path",
    "csv_path",
    "pdf_path",
    "file_contents",
    "consent_record",
    "signature",
    "overlay_values",
    "overlay_no_storage_assertion",
}

REPORT_OR_RECOMMENDATION_FIELDS = {
    "report_paragraph",
    "report_prose",
    "recommendation",
    "recommended_action",
    "strategy",
    "customer_facing_text",
}
