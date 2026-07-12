import unittest

from observatory_provider_cross_check import build_cross_check_request, build_provider_cross_check, serialize_provider_cross_check
from observatory_provider_cross_check.fixtures import SIDES, SCOPE_A


class ProviderCrossCheckDeterminismTests(unittest.TestCase):
    def test_serialization_is_deterministic(self):
        request = build_cross_check_request(request_id="req_determinism", scope_id=SCOPE_A, side_ids=["estimate_b", "estimate_a"])
        first = serialize_provider_cross_check(build_provider_cross_check(request, SIDES))
        second = serialize_provider_cross_check(build_provider_cross_check(request, SIDES))
        self.assertEqual(first, second)
        self.assertLess(first.index("estimate_a"), first.index("estimate_b"))


if __name__ == "__main__":
    unittest.main()
