from __future__ import annotations

import unittest

from observatory_overlay_proof import OverlayProofError, build_overlay_alignment_response, build_overlay_request


class OverlayHostilePathTests(unittest.TestCase):
    def assert_blocked(self, request: dict, code: str) -> None:
        with self.assertRaises(OverlayProofError) as ctx:
            build_overlay_alignment_response(request)
        self.assertEqual(ctx.exception.code, code)

    def test_missing_no_storage_assertion(self) -> None:
        request = build_overlay_request("owned_aligned")
        request["overlay_no_storage_assertion"] = False
        self.assert_blocked(request, "blocked_no_storage_not_asserted")

    def test_unknown_freshness(self) -> None:
        request = build_overlay_request("owned_aligned")
        request["overlay_freshness_status"] = "unknown"
        self.assert_blocked(request, "blocked_unknown_freshness")

    def test_private_identity_field(self) -> None:
        request = build_overlay_request("owned_aligned")
        request["field_manifest"].append("customer_id")
        request["values"][0]["customer_id"] = "synthetic-customer"
        self.assert_blocked(request, "blocked_field_overreach")

    def test_file_path_smuggling(self) -> None:
        request = build_overlay_request("timeline")
        request["values"][0]["event_kind"] = "C:\\private\\export.csv"
        self.assert_blocked(request, "blocked_file_or_screenshot")

    def test_causality_request(self) -> None:
        request = build_overlay_request("timeline")
        request["alignment_intent"] = "causality"
        self.assert_blocked(request, "blocked_recommendation_or_causality")

    def test_evidence_identity_field(self) -> None:
        request = build_overlay_request("owned_aligned")
        request["field_manifest"].append("evidence_id")
        request["values"][0]["evidence_id"] = "ev_fake"
        self.assert_blocked(request, "blocked_field_overreach")


if __name__ == "__main__":
    unittest.main()
