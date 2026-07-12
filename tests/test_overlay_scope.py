from __future__ import annotations

import unittest

from observatory_overlay_proof import OverlayProofError, build_overlay_alignment_response, build_overlay_request


class OverlayScopeTests(unittest.TestCase):
    def test_cross_scope_context_is_blocked(self) -> None:
        request = build_overlay_request("owned_aligned")
        request["overlay_scope_context"] = "scope_market_watch_beta"
        with self.assertRaises(OverlayProofError) as ctx:
            build_overlay_alignment_response(request)
        self.assertEqual(ctx.exception.code, "blocked_cross_scope")

    def test_scope_b_only_returns_scope_b_evidence(self) -> None:
        response = build_overlay_alignment_response(build_overlay_request("scope_b"))
        ids = {unit["evidence_id"] for unit in response["aligned_evidence_units"]}
        self.assertEqual(ids, {"ev_overlay_b_01"})


if __name__ == "__main__":
    unittest.main()
