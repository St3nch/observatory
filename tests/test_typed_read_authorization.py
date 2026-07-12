import unittest

from observatory_typed_read_prototype import ReadError, evidence_lookup
from observatory_typed_read_prototype.fixtures import SCOPE_A, SCOPE_B


class TypedReadAuthorizationTests(unittest.TestCase):
    def test_cross_scope_lookup_is_indistinguishable_from_missing(self) -> None:
        for evidence_id in ("ev_4dd93f71", "ev_missing"):
            with self.subTest(evidence_id=evidence_id):
                with self.assertRaises(ReadError) as ctx:
                    evidence_lookup(caller_class="kaizen", scope_id=SCOPE_A, evidence_id=evidence_id, claim_intent="historical_observation")
                self.assertEqual(ctx.exception.code, "not_found")

    def test_caller_cannot_self_widen_scope(self) -> None:
        with self.assertRaises(ReadError) as ctx:
            evidence_lookup(caller_class="kaizen", scope_id=SCOPE_B, evidence_id="ev_4dd93f71", claim_intent="historical_observation")
        self.assertEqual(ctx.exception.code, "blocked_scope")

    def test_unknown_caller_blocks_authentication(self) -> None:
        with self.assertRaises(ReadError) as ctx:
            evidence_lookup(caller_class="unknown", scope_id=SCOPE_A, evidence_id="ev_f19b6e40", claim_intent="historical_observation")
        self.assertEqual(ctx.exception.code, "blocked_authentication")


if __name__ == "__main__":
    unittest.main()
