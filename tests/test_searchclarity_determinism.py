import unittest

from observatory_searchclarity_proof import build_report_support_pack, build_report_support_request, serialize_report_support_pack
from observatory_searchclarity_proof.fixtures import SEARCHCLARITY_SCOPE
from observatory_searchclarity_proof.models import ALLOWED_OUTPUT_USE, CONTRACT_VERSION


class SearchClarityDeterminismTests(unittest.TestCase):
    def test_same_request_is_byte_stable(self):
        request = build_report_support_request(
            contract_version=CONTRACT_VERSION,
            request_id="req_deterministic",
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
        first = serialize_report_support_pack(build_report_support_pack(request))
        second = serialize_report_support_pack(build_report_support_pack(request))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
