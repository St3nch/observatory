import unittest

from observatory_searchclarity_proof import SearchClarityProofError, build_report_support_request
from observatory_searchclarity_proof.fixtures import SEARCHCLARITY_SCOPE
from observatory_searchclarity_proof.models import ALLOWED_OUTPUT_USE, CONTRACT_VERSION


BASE = dict(
    contract_version=CONTRACT_VERSION,
    request_id="req_boundary",
    request_type="report_support_evidence_lookup",
    scope_id=SEARCHCLARITY_SCOPE,
    claim_intent="historical_observation",
    current_or_historical_use="historical",
    requested_evidence_families=("controlled_public_manual",),
    freshness_requirement="fixture_contract_only",
    report_support_purpose_code="synthetic_contract_proof",
    allowed_output_use=ALLOWED_OUTPUT_USE,
    evidence_id="ev_f19b6e40",
)


class SearchClarityCustomerBoundaryTests(unittest.TestCase):
    def assert_blocked(self, field, value, code):
        payload = dict(BASE)
        payload[field] = value
        with self.assertRaises(SearchClarityProofError) as ctx:
            build_report_support_request(**payload)
        self.assertEqual(ctx.exception.code, code)

    def test_customer_identity_is_rejected(self):
        self.assert_blocked("customer_email", "private@example.invalid", "blocked_private_data")

    def test_report_prose_is_rejected(self):
        self.assert_blocked("report_paragraph", "Customer-facing claim", "blocked_report_content")

    def test_recommendation_is_rejected(self):
        self.assert_blocked("recommendation", "Rewrite the title", "blocked_recommendation")

    def test_overlay_smuggling_is_rejected(self):
        self.assert_blocked("overlay_values", {"clicks": 10}, "blocked_not_admitted")


if __name__ == "__main__":
    unittest.main()
