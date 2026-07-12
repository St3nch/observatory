import unittest

from observatory_searchclarity_proof import SearchClarityProofError, map_synthetic_report_safe_references, resolve_synthetic_reference
from observatory_searchclarity_proof.fixtures import ISOLATED_SCOPE, SEARCHCLARITY_SCOPE


class SearchClarityReferenceBoundaryTests(unittest.TestCase):
    def test_reference_is_separate_from_internal_handle(self):
        mapping = map_synthetic_report_safe_references(scope_id=SEARCHCLARITY_SCOPE, evidence_ids=["ev_f19b6e40"])[0]
        self.assertTrue(mapping["reference"].startswith("rsf_"))
        self.assertNotIn("ev_f19b6e40", mapping["reference"])

    def test_cross_scope_reference_does_not_resolve(self):
        ref = map_synthetic_report_safe_references(scope_id=SEARCHCLARITY_SCOPE, evidence_ids=["ev_f19b6e40"])[0]["reference"]
        with self.assertRaises(SearchClarityProofError) as ctx:
            resolve_synthetic_reference(scope_id=ISOLATED_SCOPE, reference=ref, evidence_ids=["ev_f19b6e40"])
        self.assertEqual(ctx.exception.code, "not_found")


if __name__ == "__main__":
    unittest.main()
