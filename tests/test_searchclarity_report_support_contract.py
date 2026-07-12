import unittest

from observatory_searchclarity_proof import build_report_support_pack, build_report_support_request
from observatory_searchclarity_proof.fixtures import SEARCHCLARITY_SCOPE
from observatory_searchclarity_proof.models import ALLOWED_OUTPUT_USE, CONTRACT_VERSION


class SearchClarityReportSupportContractTests(unittest.TestCase):
    def _request(self, **overrides):
        payload = dict(
            contract_version=CONTRACT_VERSION,
            request_id="req_m15_contract",
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
        payload.update(overrides)
        return build_report_support_request(**payload)

    def test_successful_pack_preserves_boundary_flags(self):
        pack = build_report_support_pack(self._request())
        self.assertTrue(pack["consumer_promotion_required"])
        self.assertFalse(pack["customer_facing_output_authorized"])
        self.assertTrue(pack["human_review_required"])
        self.assertEqual(pack["reference_mode"], "synthetic_report_safe_fixture")
        self.assertNotIn("report_prose", pack)
        self.assertNotIn("recommendation", pack)

    def test_required_caveats_are_present(self):
        pack = build_report_support_pack(self._request())
        self.assertGreaterEqual(len(pack["required_caveats"]), 4)
        self.assertEqual(pack["report_support_disposition"], "supportable_with_caveats")


if __name__ == "__main__":
    unittest.main()
