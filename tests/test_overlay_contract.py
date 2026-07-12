from __future__ import annotations

import unittest

from observatory_overlay_proof import build_overlay_alignment_response, build_overlay_request


class OverlayContractTests(unittest.TestCase):
    def test_success_response_has_closed_safety_flags(self) -> None:
        response = build_overlay_alignment_response(build_overlay_request("owned_aligned"))
        self.assertEqual(response["contract_version"], "0.1")
        self.assertEqual(response["alignment_disposition"], "aligned_with_caveat")
        self.assertFalse(response["overlay_persisted"])
        self.assertFalse(response["overlay_cached"])
        self.assertFalse(response["overlay_logged"])
        self.assertFalse(response["overlay_evidence_promoted"])
        self.assertFalse(response["overlay_values_returned"])
        self.assertTrue(response["consumer_promotion_required"])
        self.assertFalse(response["customer_facing_output_authorized"])

    def test_timeline_is_temporal_only(self) -> None:
        response = build_overlay_alignment_response(build_overlay_request("timeline"))
        self.assertTrue(response["alignment_summary"]["temporal_alignment_only"])
        self.assertIn("alignment does not establish causality or authorize recommendations", response["required_caveats"])


if __name__ == "__main__":
    unittest.main()
