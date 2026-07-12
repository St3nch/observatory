import unittest

from observatory_searchclarity_proof import SearchClarityProofError, build_report_support_request
from observatory_searchclarity_proof.fixtures import SEARCHCLARITY_SCOPE
from observatory_searchclarity_proof.models import ALLOWED_OUTPUT_USE, CONTRACT_VERSION


class SearchClarityHostilePathTests(unittest.TestCase):
    def _base(self):
        return dict(
            contract_version=CONTRACT_VERSION,
            request_id="req_hostile",
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

    def test_unknown_field_cannot_launder_customer_state(self):
        payload = self._base()
        payload["customer_context_scope"] = "hidden-customer"
        with self.assertRaises(SearchClarityProofError) as ctx:
            build_report_support_request(**payload)
        self.assertEqual(ctx.exception.code, "blocked_customer_data")

    def test_output_use_cannot_request_report_generation(self):
        payload = self._base()
        payload["allowed_output_use"] = "generate_customer_report"
        with self.assertRaises(SearchClarityProofError) as ctx:
            build_report_support_request(**payload)
        self.assertEqual(ctx.exception.code, "blocked_report_content")

    def test_file_path_is_rejected_without_echo(self):
        payload = self._base()
        payload["csv_path"] = "C:/private/customer.csv"
        with self.assertRaises(SearchClarityProofError) as ctx:
            build_report_support_request(**payload)
        self.assertEqual(str(ctx.exception), "blocked_private_data")


if __name__ == "__main__":
    unittest.main()
