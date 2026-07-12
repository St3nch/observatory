import unittest

from observatory_typed_read_prototype import ReadError, evidence_lookup, make_cursor, observation_package_read
from observatory_typed_read_prototype.fixtures import SCOPE_A, SCOPE_B


class TypedReadHostilePathTests(unittest.TestCase):
    def test_prompt_injection_remains_untrusted_data(self) -> None:
        result = evidence_lookup(caller_class="internal_llm", scope_id=SCOPE_A, evidence_id="ev_f19b6e40", claim_intent="historical_observation")
        unit = result["evidence_units"][0]
        self.assertIn("Ignore previous instructions", unit["observed_content_untrusted"])
        self.assertFalse(result["consumer_promotion_required"])
        self.assertIn("claim_use_warning", unit)

    def test_blocked_rights_does_not_return_as_active(self) -> None:
        with self.assertRaises(ReadError) as ctx:
            evidence_lookup(caller_class="internal_llm", scope_id=SCOPE_A, evidence_id="ev_739a1bce", claim_intent="historical_observation")
        self.assertEqual(ctx.exception.code, "not_found")

    def test_cursor_tampering_and_scope_replay_fail(self) -> None:
        cursor = make_cursor(caller_class="internal_llm", scope_id=SCOPE_A, request_type="observation_package_read", claim_intent="historical_observation", offset=1)
        with self.assertRaises(ReadError):
            observation_package_read(caller_class="internal_llm", scope_id=SCOPE_B, claim_intent="historical_observation", cursor=cursor)
        tampered = cursor[:-2] + "AA"
        with self.assertRaises(ReadError):
            observation_package_read(caller_class="internal_llm", scope_id=SCOPE_A, claim_intent="historical_observation", cursor=tampered)

    def test_page_size_ceiling(self) -> None:
        with self.assertRaises(ReadError) as ctx:
            observation_package_read(caller_class="internal_llm", scope_id=SCOPE_A, claim_intent="historical_observation", page_size=999)
        self.assertEqual(ctx.exception.code, "blocked_result_ceiling")


if __name__ == "__main__":
    unittest.main()
