from __future__ import annotations

import unittest

from observatory_overlay_proof import build_overlay_alignment_response, build_overlay_request, serialize_overlay_alignment_response


class OverlayDeterminismTests(unittest.TestCase):
    def test_serialization_is_deterministic(self) -> None:
        first = serialize_overlay_alignment_response(build_overlay_alignment_response(build_overlay_request("owned_aligned")))
        second = serialize_overlay_alignment_response(build_overlay_alignment_response(build_overlay_request("owned_aligned")))
        self.assertEqual(first, second)

    def test_aligned_evidence_is_sorted(self) -> None:
        response = build_overlay_alignment_response(build_overlay_request("owned_aligned"))
        ids = [unit["evidence_id"] for unit in response["aligned_evidence_units"]]
        self.assertEqual(ids, sorted(ids))


if __name__ == "__main__":
    unittest.main()
