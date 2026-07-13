from __future__ import annotations

import unittest

from tools.check_authority_sync import ROOT, check_repository


class AuthoritySyncTests(unittest.TestCase):
    def test_current_authority_is_synchronized(self) -> None:
        result = check_repository(ROOT)
        self.assertTrue(result.passed, "\n".join(result.errors))
        self.assertEqual(
            "DB-2 — Physical Data-Contract Freeze Reconciliation",
            result.active_milestone,
        )


if __name__ == "__main__":
    unittest.main()
