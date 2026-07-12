import unittest

from observatory_provider_cross_check import CrossCheckError, build_cross_check_request, build_provider_cross_check
from observatory_provider_cross_check.fixtures import SIDES, SCOPE_A


class ProviderCrossCheckHostilePathTests(unittest.TestCase):
    def test_forbidden_output_requests_fail_closed(self):
        cases = {
            "produce_truth": "blocked_truth_request",
            "select_winner": "blocked_winner_request",
            "compute_average": "blocked_average_or_consensus",
            "compute_consensus": "blocked_average_or_consensus",
            "compute_composite": "blocked_composite_request",
            "recommend_provider": "blocked_recommendation",
            "persist_result": "blocked_persistence",
        }
        for flag, expected in cases.items():
            with self.subTest(flag=flag):
                request = build_cross_check_request(request_id="req_hostile", scope_id=SCOPE_A, side_ids=["rank_a", "rank_b"])
                request[flag] = True
                with self.assertRaisesRegex(CrossCheckError, expected):
                    build_provider_cross_check(request, SIDES)

    def test_rights_source_and_drift_blocks(self):
        cases = {
            "rights_blocked": "blocked_rights_or_retention",
            "unadmitted": "blocked_source_not_admitted",
            "drift_blocked": "blocked_status_or_drift",
        }
        for side_id, expected in cases.items():
            with self.subTest(side_id=side_id):
                request = build_cross_check_request(request_id="req_block", scope_id=SCOPE_A, side_ids=["rank_a", side_id])
                with self.assertRaisesRegex(CrossCheckError, expected):
                    build_provider_cross_check(request, SIDES)


if __name__ == "__main__":
    unittest.main()
