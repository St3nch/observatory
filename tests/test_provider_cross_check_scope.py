import unittest

from observatory_provider_cross_check import CrossCheckError, build_cross_check_request, build_provider_cross_check
from observatory_provider_cross_check.fixtures import SIDES, SCOPE_A


class ProviderCrossCheckScopeTests(unittest.TestCase):
    def test_cross_scope_comparison_is_blocked(self):
        request = build_cross_check_request(request_id="req_scope", scope_id=SCOPE_A, side_ids=["rank_a", "scope_b"])
        with self.assertRaisesRegex(CrossCheckError, "blocked_cross_scope"):
            build_provider_cross_check(request, SIDES)

    def test_missing_side_is_not_found_without_echo(self):
        request = build_cross_check_request(request_id="req_missing", scope_id=SCOPE_A, side_ids=["rank_a", "secret-side-value"])
        with self.assertRaisesRegex(CrossCheckError, "^not_found$"):
            build_provider_cross_check(request, SIDES)


if __name__ == "__main__":
    unittest.main()
