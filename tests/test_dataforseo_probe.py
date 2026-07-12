from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from observatory_dataforseo_probe import core
from observatory_dataforseo_probe.cli import main


class RecipeTests(unittest.TestCase):
    def test_recipe_is_one_task(self):
        self.assertEqual(len(core.canonical_request()), 1)

    def test_recipe_is_defensive_copy(self):
        first = core.canonical_request()
        first[0]["keyword"] = "mutated"
        self.assertEqual(core.canonical_request()[0]["keyword"], "observatory test page")

    def test_endpoint_is_exact(self):
        self.assertEqual(core.ENDPOINT, "/v3/serp/google/organic/live/advanced")

    def test_request_hash_is_stable(self):
        self.assertEqual(core.request_sha256(), core.request_sha256())

    def test_duplicate_key_is_stable(self):
        self.assertEqual(core.duplicate_key(), core.duplicate_key())

    def test_network_authority_is_false(self):
        self.assertFalse(core.NETWORK_EXECUTION_AUTHORIZED)

    def test_execute_always_blocks(self):
        with self.assertRaises(core.ProbeBlocked):
            core.execute_request(core.canonical_request())

    def test_extra_field_blocks(self):
        candidate = core.canonical_request()
        candidate[0]["load_async_ai_overview"] = True
        with self.assertRaises(core.ProbeBlocked):
            core.validate_request(candidate)

    def test_missing_field_blocks(self):
        candidate = core.canonical_request()
        del candidate[0]["depth"]
        with self.assertRaises(core.ProbeBlocked):
            core.validate_request(candidate)

    def test_mutated_field_blocks(self):
        candidate = core.canonical_request()
        candidate[0]["depth"] = 20
        with self.assertRaises(core.ProbeBlocked):
            core.validate_request(candidate)

    def test_multiple_tasks_block(self):
        with self.assertRaises(core.ProbeBlocked):
            core.validate_request(core.canonical_request() * 2)

    def test_non_list_blocks(self):
        with self.assertRaises(core.ProbeBlocked):
            core.validate_request({})


class PreflightTests(unittest.TestCase):
    def base(self, **overrides):
        values = dict(
            decision_accepted=True,
            implementation_authorized=True,
            funding_authorized=True,
            network_authorized=True,
            exact_price=0.05,
            account_limits_recorded=True,
            duplicate_exists=False,
            evidence_root_ignored=True,
            credentials_present=True,
        )
        values.update(overrides)
        return core.PreflightInputs(**values)

    def assert_blocker(self, blocker, **overrides):
        result = core.build_preflight(self.base(**overrides))
        self.assertIn(blocker, result["blockers"])
        self.assertEqual(result["status"], "blocked")

    def test_fixture_authority_blocks_network_even_when_other_inputs_pass(self):
        self.assert_blocker("network_execution_not_authorized")

    def test_decision_missing_blocks(self):
        self.assert_blocker("decision_not_accepted", decision_accepted=False)

    def test_implementation_missing_blocks(self):
        self.assert_blocker("implementation_not_authorized", implementation_authorized=False)

    def test_funding_missing_blocks(self):
        self.assert_blocker("funding_not_authorized", funding_authorized=False)

    def test_network_flag_missing_blocks(self):
        self.assert_blocker("network_execution_not_authorized", network_authorized=False)

    def test_price_missing_blocks(self):
        self.assert_blocker("exact_price_missing", exact_price=None)

    def test_price_above_ceiling_blocks(self):
        self.assert_blocker("price_ceiling_exceeded", exact_price=0.11)

    def test_negative_price_blocks(self):
        self.assert_blocker("invalid_negative_price", exact_price=-0.01)

    def test_account_limits_missing_blocks(self):
        self.assert_blocker("account_limits_not_recorded", account_limits_recorded=False)

    def test_duplicate_blocks(self):
        self.assert_blocker("duplicate_request_detected", duplicate_exists=True)

    def test_gitignore_missing_blocks(self):
        self.assert_blocker("evidence_root_not_git_ignored", evidence_root_ignored=False)

    def test_credentials_missing_blocks(self):
        self.assert_blocker("credentials_missing", credentials_present=False)

    def test_request_count_blocks(self):
        self.assert_blocker("api_request_count_invalid", request_count=2)

    def test_task_count_blocks(self):
        self.assert_blocker("billable_task_count_invalid", billable_task_count=2)

    def test_retry_blocks(self):
        self.assert_blocker("retry_count_invalid", retries=1)

    def test_polling_blocks(self):
        self.assert_blocker("polling_count_invalid", polling_requests=1)

    def test_assert_ready_blocks_blocked_record(self):
        with self.assertRaises(core.ProbeBlocked):
            core.assert_preflight_ready({"status": "blocked", "blockers": ["x"]})


class CredentialTests(unittest.TestCase):
    def test_missing_credentials_false(self):
        self.assertFalse(core.credentials_present({}))

    def test_partial_credentials_false(self):
        self.assertFalse(core.credentials_present({"DATAFORSEO_LOGIN": "x"}))

    def test_both_credentials_true(self):
        self.assertTrue(core.credentials_present({"DATAFORSEO_LOGIN": "x", "DATAFORSEO_PASSWORD": "y"}))

    def test_redaction_removes_secrets(self):
        with patch.dict(os.environ, {"DATAFORSEO_LOGIN": "login-secret", "DATAFORSEO_PASSWORD": "pass-secret"}, clear=False):
            value = core.redact_text("login-secret pass-secret")
        self.assertNotIn("login-secret", value)
        self.assertNotIn("pass-secret", value)


class ResponseTests(unittest.TestCase):
    def normal(self):
        return {
            "status_code": 20000,
            "status_message": "Ok.",
            "cost": 0.002,
            "tasks": [{"status_code": 20000, "status_message": "Ok.", "cost": 0.002, "result": [{"type": "organic"}]}],
        }

    def test_normal_response_class(self):
        self.assertEqual(core.classify_response(self.normal()), "normal_provider_response")

    def test_auth_error_class(self):
        self.assertEqual(core.classify_response({"status_code": 40100, "status_message": "Authentication error"}), "provider_authentication_error")

    def test_throttle_class(self):
        self.assertEqual(core.classify_response({"status_code": 40200, "status_message": "Limit exceeded"}), "provider_throttle_or_limit")

    def test_request_error_class(self):
        self.assertEqual(core.classify_response({"status_code": 40500, "status_message": "Bad request"}), "provider_request_error")

    def test_missing_tasks_is_error_shape(self):
        self.assertEqual(core.classify_response({"status_code": 20000}), "provider_error_shape")

    def test_missing_result_is_unknown(self):
        payload = {"status_code": 20000, "tasks": [{"status_code": 20000}]}
        self.assertEqual(core.classify_response(payload), "unknown_shape")

    def test_non_dict_is_unknown(self):
        self.assertEqual(core.classify_response([]), "unknown_shape")

    def test_summary_preserves_costs(self):
        summary = core.summarize_payload(self.normal())
        self.assertEqual(summary["provider_top_level_cost"], 0.002)
        self.assertEqual(summary["provider_task_level_cost"], 0.002)

    def test_error_payload_not_summarized(self):
        with self.assertRaises(core.ProbeBlocked):
            core.summarize_payload({"status_code": 40500})

    def test_shape_fingerprint_stable(self):
        payload = self.normal()
        self.assertEqual(core.shape_fingerprint(payload)["field_path_set_sha256"], core.shape_fingerprint(payload)["field_path_set_sha256"])


class EvidenceTests(unittest.TestCase):
    def test_outside_root_write_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(core.ProbeBlocked):
                core.write_json(Path(tmp) / "outside.json", {"x": 1})

    def test_outside_root_purge_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw.json"
            path.write_text("{}", encoding="utf-8")
            with self.assertRaises(core.ProbeBlocked):
                core.purge_raw_payload(path, "probe", "tester")

    def test_purge_records_hash_and_deletes(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(core, "EVIDENCE_ROOT", Path(tmp) / "probe-evidence"):
                path = core.EVIDENCE_ROOT / "probe-1" / "raw-response.json"
                path.parent.mkdir(parents=True)
                path.write_text('{"ok": true}', encoding="utf-8")
                proof = core.purge_raw_payload(path, "probe-1", "tester")
                self.assertFalse(path.exists())
                self.assertEqual(len(proof["pre_purge_sha256"]), 64)

    def test_package_purge_requires_matching_hash_and_writes_08_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence_root = Path(tmp) / "probe-evidence"
            root = evidence_root / "probe-1"
            raw = root / "02-raw-response.json"
            root.mkdir(parents=True)
            raw.write_text('{"ok": true}', encoding="utf-8")
            expected_hash = core.hash_file(raw)
            with (
                patch.object(core, "EVIDENCE_ROOT", evidence_root),
                patch("observatory_dataforseo_probe.cli.EVIDENCE_ROOT", evidence_root),
            ):
                result = main([
                    "package-purge",
                    "--probe-id", "probe-1",
                    "--actor", "tester",
                    "--confirm-raw-sha256", expected_hash,
                ])
            self.assertEqual(result, 0)
            self.assertFalse(raw.exists())
            self.assertTrue((root / "08-purge-proof.json").is_file())

    def test_package_purge_wrong_hash_preserves_raw(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence_root = Path(tmp) / "probe-evidence"
            root = evidence_root / "probe-1"
            raw = root / "02-raw-response.json"
            root.mkdir(parents=True)
            raw.write_text('{"ok": true}', encoding="utf-8")
            with (
                patch.object(core, "EVIDENCE_ROOT", evidence_root),
                patch("observatory_dataforseo_probe.cli.EVIDENCE_ROOT", evidence_root),
            ):
                result = main([
                    "package-purge",
                    "--probe-id", "probe-1",
                    "--actor", "tester",
                    "--confirm-raw-sha256", "0" * 64,
                ])
            self.assertEqual(result, 2)
            self.assertTrue(raw.is_file())
            self.assertFalse((root / "08-purge-proof.json").exists())

    def test_naive_retention_timestamp_blocks(self):
        with self.assertRaises(core.ProbeBlocked):
            core.retention_deadline(datetime.now())

    def test_retention_is_seven_days(self):
        start = datetime(2026, 7, 12, tzinfo=timezone.utc)
        self.assertEqual((core.retention_deadline(start) - start).days, 7)

    def test_unknown_response_class_blocks(self):
        with self.assertRaises(core.ProbeBlocked):
            core.validate_response_class("made_up")


class CliTests(unittest.TestCase):
    def test_show_recipe_succeeds(self):
        self.assertEqual(main(["show-recipe"]), 0)

    def test_preflight_is_blocked(self):
        self.assertEqual(main(["preflight"]), 2)

    def test_execute_wrong_hash_blocks(self):
        self.assertEqual(main(["execute", "--confirm-paid-request", "bad"]), 2)

    def test_execute_correct_hash_still_blocks_network(self):
        self.assertEqual(main(["execute", "--confirm-paid-request", core.request_sha256()]), 2)

    def test_invalid_probe_id_blocks(self):
        self.assertEqual(main(["summarize", "--probe-id", "../escape"]), 2)


if __name__ == "__main__":
    unittest.main()
