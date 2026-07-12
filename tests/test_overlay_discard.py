from __future__ import annotations

import copy
import unittest

from observatory_overlay_proof import build_overlay_alignment_response, build_overlay_request, serialize_overlay_alignment_response


class OverlayDiscardTests(unittest.TestCase):
    def test_request_is_not_mutated_and_values_are_not_returned(self) -> None:
        request = build_overlay_request("owned_aligned")
        before = copy.deepcopy(request)
        response = build_overlay_alignment_response(request)
        self.assertEqual(request, before)
        serialized = serialize_overlay_alignment_response(response)
        for row in request["values"]:
            for value in row.values():
                if isinstance(value, (int, float)):
                    self.assertNotIn(f'"value":{value}', serialized)
        self.assertNotIn("field_manifest", response)
        self.assertEqual(response["overlay_discard_status"], "discarded_after_response_build")

    def test_repeated_calls_do_not_reveal_prior_values(self) -> None:
        first = build_overlay_request("owned_aligned")
        first["values"][0]["value"] = 999999
        build_overlay_alignment_response(first)
        second = build_overlay_alignment_response(build_overlay_request("owned_aligned"))
        self.assertNotIn("999999", serialize_overlay_alignment_response(second))


if __name__ == "__main__":
    unittest.main()
