import unittest

from observatory_searchclarity_proof import classify_report_support_disposition


class SearchClarityClaimBlockerTests(unittest.TestCase):
    def test_unadmitted_marketplace_family_blocks(self):
        disposition, blockers = classify_report_support_disposition(
            evidence_units=[],
            claim_intent="historical_observation",
            requested_evidence_families=("marketplace_private_dashboard",),
        )
        self.assertEqual(disposition, "blocked")
        self.assertIn("source_family_not_admitted", blockers)

    def test_current_state_stale_blocks(self):
        unit = {
            "evidence_status": "active",
            "source_family": "controlled_public_manual",
            "provider_attribution": "operator",
            "freshness_status": "stale",
            "claim_use_warning": "warning",
            "sample_bound_warning": "sample",
            "absence_warning": "absence",
            "incomparability_warning": "incomparable",
        }
        disposition, blockers = classify_report_support_disposition(
            evidence_units=[unit],
            claim_intent="current_state_observation",
            requested_evidence_families=("controlled_public_manual",),
        )
        self.assertEqual(disposition, "blocked")
        self.assertIn("blocked_freshness_for_current_use", blockers)

    def test_historical_stale_is_historical_only(self):
        unit = {
            "evidence_status": "superseded",
            "source_family": "controlled_public_manual",
            "provider_attribution": "operator",
            "freshness_status": "stale",
            "claim_use_warning": "warning",
            "sample_bound_warning": "sample",
            "absence_warning": "absence",
            "incomparability_warning": "incomparable",
        }
        disposition, blockers = classify_report_support_disposition(
            evidence_units=[unit],
            claim_intent="historical_observation",
            requested_evidence_families=("controlled_public_manual",),
        )
        self.assertEqual(disposition, "historical_support_only")
        self.assertEqual(blockers, [])


if __name__ == "__main__":
    unittest.main()
