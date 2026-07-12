from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from observatory_dataforseo_probe import evidence_package as package
from observatory_dataforseo_probe import core


class EvidencePackageTests(unittest.TestCase):
    def payload(self):
        return {
            "status_code": 20000,
            "status_message": "Ok.",
            "cost": 0.002,
            "tasks": [
                {
                    "status_code": 20000,
                    "status_message": "Ok.",
                    "cost": 0.002,
                    "result": [
                        {
                            "keyword": "observatory test page",
                            "items": [
                                {"type": "organic", "rank_group": 1, "url": "https://example.com"},
                                {"type": "video", "rank_group": 2, "url": "https://example.com/video"},
                                {"rank_group": 3},
                            ],
                        }
                    ],
                }
            ],
        }

    def test_manifest_is_stable_and_descriptive(self):
        captured = datetime(2026, 7, 12, 14, 0, tzinfo=timezone.utc)
        manifest = package.build_request_manifest("C00", captured, Decimal("0.0020"), "abc123")
        self.assertEqual(manifest["probe_id"], "2026-07-12_C00_abc123")
        self.assertEqual(manifest["expected_price_usd"], "0.0020")
        self.assertEqual(len(manifest["request_sha256"]), 64)

    def test_naive_manifest_time_blocks(self):
        with self.assertRaises(core.ProbeBlocked):
            package.build_request_manifest("C00", datetime(2026, 7, 12), Decimal("0.0020"), "abc")

    def test_unsafe_empty_suffix_blocks(self):
        with self.assertRaises(core.ProbeBlocked):
            package.build_request_manifest("C00", datetime.now(timezone.utc), Decimal("0.0020"), "../")

    def test_field_inventory_groups_sections(self):
        inventory = package.build_field_inventory(self.payload())
        self.assertIn("response", inventory["sections"])
        self.assertIn("task", inventory["sections"])
        self.assertIn("result", inventory["sections"])
        self.assertIn("items", inventory["sections"])
        self.assertEqual(len(inventory["all_field_path_set_sha256"]), 64)

    def test_item_type_summary_counts_unknown(self):
        summary = package.build_item_type_summary(self.payload())
        self.assertEqual(summary["item_count"], 3)
        self.assertEqual(summary["item_type_counts"]["organic"], 1)
        self.assertEqual(summary["item_type_counts"]["video"], 1)
        self.assertEqual(summary["unknown_item_type_count"], 1)

    def test_cost_reconciles(self):
        summary = package.build_cost_reconciliation(Decimal("0.002"), self.payload(), Decimal("0.002"))
        self.assertEqual(summary["reconciliation_status"], "reconciled")
        self.assertEqual(summary["conservative_cost_usd"], "0.002")

    def test_cost_disagreement_requires_review(self):
        summary = package.build_cost_reconciliation(Decimal("0.002"), self.payload(), Decimal("0.003"))
        self.assertEqual(summary["reconciliation_status"], "review_required")
        self.assertEqual(summary["conservative_cost_usd"], "0.003")

    def test_create_review_package_writes_expected_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence_root = Path(tmp) / "probe-evidence" / "dataforseo"
            captured = datetime(2026, 7, 12, 14, 0, tzinfo=timezone.utc)
            with patch.object(core, "EVIDENCE_ROOT", evidence_root), patch.object(package, "EVIDENCE_ROOT", evidence_root):
                result = package.create_review_package("C00", self.payload(), captured, Decimal("0.002"), "abc")
                root = evidence_root / result["probe_id"]
                for name in result["files_written"]:
                    self.assertTrue((root / name).is_file(), name)
                notes = (root / "07-review-notes.md").read_text(encoding="utf-8")
                self.assertIn("Promotion decision", notes)

    def test_campaign_index_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence_root = Path(tmp) / "probe-evidence" / "dataforseo"
            index = evidence_root / "campaign-index.json"
            review = evidence_root / "campaign-review.md"
            entry = {
                "probe_id": "2026-07-12_C00_abc",
                "recipe_id": "C00",
                "endpoint": "/v3/serp/google/organic/live/advanced",
                "captured_at": "2026-07-12T14:00:00+00:00",
                "status": "complete",
                "cost_usd": "0.002",
                "raw_state": "captured",
                "review_status": "pending",
            }
            with patch.object(core, "EVIDENCE_ROOT", evidence_root), patch.object(package, "EVIDENCE_ROOT", evidence_root):
                package.update_campaign_index(entry, index, review)
                package.update_campaign_index(entry, index, review)
                saved = json.loads(index.read_text(encoding="utf-8"))
                self.assertEqual(len(saved["pulls"]), 1)
                self.assertIn("2026-07-12_C00_abc", review.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
