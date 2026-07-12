import unittest

from observatory_typed_read_prototype import coverage_blind_spot_read, evidence_lookup
from observatory_typed_read_prototype.fixtures import SCOPE_A


class TypedReadContractTests(unittest.TestCase):
    def test_evidence_lookup_returns_required_envelope(self) -> None:
        result = evidence_lookup(caller_class="internal_llm", scope_id=SCOPE_A, evidence_id="ev_a7f3c9d2", claim_intent="historical_observation")
        for key in ("contract_version", "request_type", "caller_class", "scope_id", "evidence_units", "warnings", "consumer_promotion_required"):
            self.assertIn(key, result)
        unit = result["evidence_units"][0]
        for key in ("evidence_id", "provider_attribution", "observed_content_untrusted", "freshness_status", "rights_class", "retention_class", "raw_support_status", "claim_use_warning"):
            self.assertIn(key, unit)

    def test_coverage_is_sorted_and_evidence_only(self) -> None:
        result = coverage_blind_spot_read(caller_class="internal_llm", scope_id=SCOPE_A, claim_intent="coverage_statement")
        self.assertEqual(result["coverage_blind_spots"], sorted(result["coverage_blind_spots"]))
        self.assertTrue(result["consumer_promotion_required"])
        self.assertEqual(result["evidence_units"], [])


if __name__ == "__main__":
    unittest.main()
