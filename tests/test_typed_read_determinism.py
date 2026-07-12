import json
import unittest

from observatory_typed_read_prototype import coverage_blind_spot_read, evidence_lookup
from observatory_typed_read_prototype.fixtures import SCOPE_A


class TypedReadDeterminismTests(unittest.TestCase):
    def test_same_request_is_byte_stable(self) -> None:
        first = evidence_lookup(caller_class="internal_llm", scope_id=SCOPE_A, evidence_id="ev_a7f3c9d2", claim_intent="historical_observation")
        second = evidence_lookup(caller_class="internal_llm", scope_id=SCOPE_A, evidence_id="ev_a7f3c9d2", claim_intent="historical_observation")
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_warning_and_coverage_order_is_stable(self) -> None:
        first = coverage_blind_spot_read(caller_class="internal_llm", scope_id=SCOPE_A, claim_intent="coverage_statement")
        second = coverage_blind_spot_read(caller_class="internal_llm", scope_id=SCOPE_A, claim_intent="coverage_statement")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
