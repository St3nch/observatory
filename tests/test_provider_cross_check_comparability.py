import unittest

from observatory_provider_cross_check import build_cross_check_request, build_provider_cross_check
from observatory_provider_cross_check.fixtures import SIDES, SCOPE_A


class ProviderCrossCheckComparabilityTests(unittest.TestCase):
    def _result(self, side_ids):
        request = build_cross_check_request(request_id="req_compare", scope_id=SCOPE_A, side_ids=side_ids)
        return build_provider_cross_check(request, SIDES)

    def test_unknown_proprietary_scores_are_incomparable(self):
        result = self._result(["difficulty_a", "difficulty_b"])
        self.assertEqual(result["comparison_disposition"], "unresolved_incomparability")
        self.assertIn("metric_definition", result["misaligned_dimensions"])

    def test_non_synchronous_fresh_stale_pair_is_downgraded(self):
        result = self._result(["rank_a", "late_b"])
        self.assertEqual(result["comparison_disposition"], "partially_comparable")
        self.assertGreater(result["capture_time_distance"], 0)
        self.assertIn("freshness_difference", result["disagreement_types"])

    def test_sampled_presence_absence_is_scoped(self):
        result = self._result(["presence_a", "absence_b"])
        self.assertIn("presence_absence_difference", result["disagreement_types"])
        self.assertTrue(any("not universal" in caveat for caveat in result["required_caveats"]))


if __name__ == "__main__":
    unittest.main()
