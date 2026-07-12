from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal

from observatory_dataforseo_probe import campaign, core
from observatory_dataforseo_probe.cli import main


class CampaignCatalogTests(unittest.TestCase):
    def test_catalog_valid(self):
        result = campaign.validate_catalog()
        self.assertTrue(result["valid"], result["errors"])

    def test_campaign_budget_is_fifty(self):
        self.assertEqual(campaign.CAMPAIGN_BUDGET_USD, Decimal("50.00"))

    def test_stage_budget_balances(self):
        total = sum((stage.spend_ceiling_usd for stage in campaign.STAGES), Decimal("0.00"))
        self.assertEqual(total, campaign.CAMPAIGN_BUDGET_USD)

    def test_stage_ids_unique(self):
        ids = [stage.stage_id for stage in campaign.STAGES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_recipe_ids_unique(self):
        ids = [recipe.recipe_id for recipe in campaign.RECIPES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_initial_recipe_count(self):
        self.assertEqual(len(campaign.RECIPES), 8)

    def test_all_recipe_stages_exist(self):
        stages = campaign.stage_map()
        self.assertTrue(all(recipe.stage_id in stages for recipe in campaign.RECIPES))

    def test_all_endpoints_are_v3_relative(self):
        self.assertTrue(all(recipe.endpoint.startswith("/v3/") for recipe in campaign.RECIPES))

    def test_all_initial_methods_are_post(self):
        self.assertTrue(all(recipe.method == "POST" for recipe in campaign.RECIPES))

    def test_only_c00_promoted(self):
        statuses = {recipe.recipe_id: recipe.live_status for recipe in campaign.RECIPES}
        self.assertEqual(statuses["C00"], "promoted_for_preflight")
        self.assertTrue(all(status == "candidate" for key, status in statuses.items() if key != "C00"))

    def test_c00_matches_original_recipe(self):
        recipe = campaign.get_recipe("C00")
        self.assertEqual(recipe.endpoint, core.ENDPOINT)
        self.assertEqual(recipe.request(), core.canonical_request())
        self.assertEqual(recipe.request_sha256(), core.request_sha256())

    def test_c01_changes_device_dimensions(self):
        desktop = campaign.get_recipe("C00").request()[0]
        mobile = campaign.get_recipe("C01").request()[0]
        common_keys = {"keyword", "location_code", "language_code", "depth"}
        for key in common_keys:
            self.assertEqual(desktop[key], mobile[key])
        self.assertEqual(mobile["device"], "mobile")
        self.assertEqual(mobile["os"], "android")

    def test_verified_endpoint_catalog(self):
        expected = {
            "C00": "/v3/serp/google/organic/live/advanced",
            "C01": "/v3/serp/google/organic/live/advanced",
            "C02": "/v3/serp/bing/organic/live/advanced",
            "C03": "/v3/serp/youtube/organic/live/advanced",
            "C04": "/v3/serp/google/maps/live/advanced",
            "C05": "/v3/serp/google/ai_mode/live/advanced",
            "C06": "/v3/dataforseo_labs/google/keyword_overview/live",
            "C07": "/v3/dataforseo_labs/google/keyword_ideas/live",
        }
        self.assertEqual({recipe.recipe_id: recipe.endpoint for recipe in campaign.RECIPES}, expected)

    def test_request_returns_defensive_copy(self):
        recipe = campaign.get_recipe("C07")
        first = recipe.request()
        first[0]["keywords"].append("mutated")
        self.assertEqual(recipe.request()[0]["keywords"], ["observatory"])

    def test_request_hash_stable(self):
        recipe = campaign.get_recipe("C05")
        self.assertEqual(recipe.request_sha256(), recipe.request_sha256())

    def test_duplicate_keys_differ(self):
        keys = [recipe.duplicate_key() for recipe in campaign.RECIPES]
        self.assertEqual(len(keys), len(set(keys)))

    def test_unknown_recipe_blocks(self):
        with self.assertRaises(core.ProbeBlocked):
            campaign.get_recipe("C99")

    def test_summaries_keep_network_disabled(self):
        self.assertTrue(all(not item["network_execution_authorized"] for item in campaign.list_recipes()))

    def test_no_customer_or_secret_markers_in_payloads(self):
        serialized = json.dumps([recipe.request() for recipe in campaign.RECIPES]).lower()
        for marker in ("customer", "searchclarity", "password", "credential", "secret"):
            self.assertNotIn(marker, serialized)

    def test_prior_recipe_chain_exists(self):
        recipe_ids = {recipe.recipe_id for recipe in campaign.RECIPES}
        for recipe in campaign.RECIPES:
            if recipe.requires_prior_recipe:
                self.assertIn(recipe.requires_prior_recipe, recipe_ids)


class CampaignBatchTests(unittest.TestCase):
    def test_calibration_allows_one_recipe(self):
        campaign.validate_batch(["C00"], 0, Decimal("0.10"))

    def test_calibration_blocks_multiple_recipes(self):
        with self.assertRaises(core.ProbeBlocked):
            campaign.validate_batch(["C00", "C01"], 0, Decimal("0.35"))

    def test_later_batch_allows_three(self):
        campaign.validate_batch(["C01", "C02", "C03"], 3, Decimal("1.00"))

    def test_later_batch_blocks_four(self):
        with self.assertRaises(core.ProbeBlocked):
            campaign.validate_batch(["C01", "C02", "C03", "C04"], 3, Decimal("1.50"))

    def test_later_batch_blocks_above_two_dollars(self):
        with self.assertRaises(core.ProbeBlocked):
            campaign.validate_batch(["C01", "C02"], 3, Decimal("2.01"))

    def test_empty_batch_blocks(self):
        with self.assertRaises(core.ProbeBlocked):
            campaign.validate_batch([], 3, Decimal("1.00"))

    def test_duplicate_recipe_in_batch_blocks(self):
        with self.assertRaises(core.ProbeBlocked):
            campaign.validate_batch(["C01", "C01"], 3, Decimal("0.50"))

    def test_non_positive_batch_cost_blocks(self):
        with self.assertRaises(core.ProbeBlocked):
            campaign.validate_batch(["C01"], 3, Decimal("0.00"))

    def test_unknown_batch_recipe_blocks(self):
        with self.assertRaises(core.ProbeBlocked):
            campaign.validate_batch(["C99"], 3, Decimal("0.10"))


class CampaignSpendTests(unittest.TestCase):
    def test_conservative_spend_uses_larger_witness(self):
        total = campaign.conservative_spend(
            [Decimal("0.10"), Decimal("0.20")],
            [Decimal("0.11"), Decimal("0.19")],
        )
        self.assertEqual(total, Decimal("0.31"))

    def test_cost_witness_count_mismatch_blocks(self):
        with self.assertRaises(core.ProbeBlocked):
            campaign.conservative_spend([Decimal("0.10")], [])

    def test_negative_cost_blocks(self):
        with self.assertRaises(core.ProbeBlocked):
            campaign.conservative_spend([Decimal("-0.01")], [Decimal("0.01")])

    def test_over_campaign_budget_blocks(self):
        with self.assertRaises(core.ProbeBlocked):
            campaign.conservative_spend([Decimal("50.01")], [Decimal("50.00")])


class CampaignCliTests(unittest.TestCase):
    def run_cli(self, argv: list[str]):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_campaign_validate_cli(self):
        code, output, error = self.run_cli(["campaign-validate"])
        self.assertEqual(code, 0, error)
        self.assertTrue(json.loads(output)["valid"])

    def test_campaign_budget_cli(self):
        code, output, error = self.run_cli(["campaign-budget"])
        self.assertEqual(code, 0, error)
        payload = json.loads(output)
        self.assertEqual(payload["campaign_budget_usd"], "50.00")
        self.assertTrue(payload["budget_balanced"])
        self.assertFalse(payload["network_execution_authorized"])

    def test_campaign_list_cli(self):
        code, output, error = self.run_cli(["campaign-list"])
        self.assertEqual(code, 0, error)
        payload = json.loads(output)
        self.assertEqual(len(payload), 8)

    def test_campaign_show_cli(self):
        code, output, error = self.run_cli(["campaign-show", "--recipe-id", "C00"])
        self.assertEqual(code, 0, error)
        payload = json.loads(output)
        self.assertEqual(payload["recipe_id"], "C00")
        self.assertFalse(payload["network_execution_authorized"])

    def test_campaign_show_unknown_blocks(self):
        code, _, error = self.run_cli(["campaign-show", "--recipe-id", "C99"])
        self.assertEqual(code, 2)
        self.assertIn("unknown campaign recipe", error)


if __name__ == "__main__":
    unittest.main()
