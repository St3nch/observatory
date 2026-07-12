import unittest

from observatory_provider_cross_check import build_cross_check_request, build_provider_cross_check
from observatory_provider_cross_check.fixtures import SIDES, SCOPE_A


class ProviderCrossCheckContractTests(unittest.TestCase):
    def test_success_envelope_and_no_truth_flags(self):
        request = build_cross_check_request(request_id="req_contract", scope_id=SCOPE_A, side_ids=["rank_a", "rank_b"])
        result = build_provider_cross_check(request, SIDES)
        self.assertEqual(result["comparison_disposition"], "comparable_with_caveat")
        self.assertTrue(result["consumer_promotion_required"])
        self.assertFalse(result["truth_value_produced"])
        self.assertFalse(result["winner_selected"])
        self.assertFalse(result["composite_score_produced"])
        self.assertEqual(len(result["provider_sides"]), 2)
        self.assertIn("rank_position_difference", result["disagreement_types"])


if __name__ == "__main__":
    unittest.main()
