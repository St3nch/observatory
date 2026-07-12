import unittest

from observatory_typed_read_prototype import assemble_context_pack, observation_package_read
from observatory_typed_read_prototype.fixtures import SCOPE_A


class TypedReadContextPackTests(unittest.TestCase):
    def test_whole_unit_truncation_preserves_caveats(self) -> None:
        response = observation_package_read(caller_class="internal_llm", scope_id=SCOPE_A, claim_intent="historical_observation", page_size=2)
        pack = assemble_context_pack(response, max_chars=1500)
        for unit in pack["evidence_units"]:
            self.assertIn("claim_use_warning", unit)
            self.assertIn("freshness_status", unit)
            self.assertIn("provider_attribution", unit)
        self.assertEqual(pack["omitted_evidence_unit_count"], len(response["evidence_units"]) - len(pack["evidence_units"]))

    def test_tiny_budget_drops_entire_unit(self) -> None:
        response = observation_package_read(caller_class="internal_llm", scope_id=SCOPE_A, claim_intent="historical_observation", page_size=2)
        pack = assemble_context_pack(response, max_chars=1)
        self.assertEqual(pack["evidence_units"], [])
        self.assertTrue(pack["truncated"])


if __name__ == "__main__":
    unittest.main()
