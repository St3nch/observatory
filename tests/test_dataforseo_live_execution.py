from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from observatory_dataforseo_probe import core
from observatory_dataforseo_probe import evidence_package
from observatory_dataforseo_probe import live_execution as live


class LivePreflightTests(unittest.TestCase):
    def env(self):
        return {"DATAFORSEO_LOGIN": "login", "DATAFORSEO_PASSWORD": "password"}

    def test_default_live_authority_is_false(self):
        self.assertFalse(live.LIVE_EXECUTION_AUTHORIZED)

    def test_preflight_blocks_without_owner_confirmation(self):
        result = live.build_live_preflight(
            env=self.env(),
            account_limits_recorded=True,
            evidence_root_ignored=True,
            duplicate_exists=False,
        )
        self.assertIn("owner_paid_request_confirmation_missing", result["blockers"])

    def test_preflight_blocks_without_credentials(self):
        result = live.build_live_preflight(
            env={},
            account_limits_recorded=True,
            evidence_root_ignored=True,
            duplicate_exists=False,
            owner_confirmation=live.OWNER_CONFIRMATION_PHRASE,
        )
        self.assertIn("credentials_missing", result["blockers"])

    def test_preflight_blocks_price_mismatch(self):
        result = live.build_live_preflight(
            env=self.env(),
            exact_price_usd=Decimal("0.003"),
            account_limits_recorded=True,
            evidence_root_ignored=True,
            duplicate_exists=False,
            owner_confirmation=live.OWNER_CONFIRMATION_PHRASE,
        )
        self.assertIn("exact_price_mismatch", result["blockers"])

    def test_preflight_reports_one_request_zero_retry(self):
        result = live.build_live_preflight(
            env=self.env(),
            account_limits_recorded=True,
            evidence_root_ignored=True,
            duplicate_exists=False,
            owner_confirmation=live.OWNER_CONFIRMATION_PHRASE,
        )
        self.assertEqual(result["api_request_ceiling"], 1)
        self.assertEqual(result["retry_ceiling"], 0)


class RegistryTests(unittest.TestCase):
    def test_reservation_blocks_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "probe-evidence" / "dataforseo"
            registry = root / "attempt-registry.json"
            with patch.object(core, "EVIDENCE_ROOT", root), patch.object(live, "EVIDENCE_ROOT", root):
                live.reserve_attempt("probe-one", registry)
                self.assertTrue(live.duplicate_attempt_exists(registry))
                with self.assertRaises(core.ProbeBlocked):
                    live.reserve_attempt("probe-two", registry)

    def test_invalid_registry_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            path.write_text("[]", encoding="utf-8")
            with self.assertRaises(core.ProbeBlocked):
                live.duplicate_attempt_exists(path)


class HttpRequestTests(unittest.TestCase):
    def test_request_is_exact_post_with_basic_auth(self):
        request = live.build_http_request({"DATAFORSEO_LOGIN": "user", "DATAFORSEO_PASSWORD": "pass"})
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.full_url, "https://api.dataforseo.com/v3/serp/google/organic/live/advanced")
        self.assertTrue(request.headers["Authorization"].startswith("Basic "))
        self.assertEqual(json.loads(request.data.decode("utf-8"))[0]["depth"], 10)

    def test_missing_credentials_blocks_request_build(self):
        with self.assertRaises(core.ProbeBlocked):
            live.build_http_request({})


class ExecuteTests(unittest.TestCase):
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
                            "items": [
                                {"type": "organic", "rank_absolute": 1, "url": "https://example.com"},
                                {"type": "people_also_ask", "rank_absolute": 2},
                            ]
                        }
                    ],
                }
            ],
        }

    def test_execution_still_blocks_without_source_authority(self):
        with self.assertRaises(core.ProbeBlocked):
            live.execute_one_c00(
                owner_confirmation=live.OWNER_CONFIRMATION_PHRASE,
                env={"DATAFORSEO_LOGIN": "user", "DATAFORSEO_PASSWORD": "pass"},
                account_limits_recorded=True,
                evidence_root_ignored=True,
            )

    def test_authorized_mock_transport_writes_review_package_once(self):
        calls = []

        def transport(request, timeout):
            calls.append((request, timeout))
            return live.TransportResponse(200, json.dumps(self.payload()).encode("utf-8"), {})

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "probe-evidence" / "dataforseo"
            registry = root / "attempt-registry.json"
            index = root / "campaign-index.json"
            review = root / "campaign-review.md"
            fixed = datetime(2026, 7, 12, 14, 30, tzinfo=timezone.utc)
            with (
                patch.object(core, "EVIDENCE_ROOT", root),
                patch.object(evidence_package, "EVIDENCE_ROOT", root),
                patch.object(evidence_package, "CAMPAIGN_INDEX_PATH", index),
                patch.object(evidence_package, "CAMPAIGN_REVIEW_PATH", review),
                patch.object(live, "EVIDENCE_ROOT", root),
                patch.object(live, "ATTEMPT_REGISTRY_PATH", registry),
                patch.object(live, "LIVE_EXECUTION_AUTHORIZED", True),
            ):
                result = live.execute_one_c00(
                    owner_confirmation=live.OWNER_CONFIRMATION_PHRASE,
                    env={"DATAFORSEO_LOGIN": "user", "DATAFORSEO_PASSWORD": "pass"},
                    account_limits_recorded=True,
                    evidence_root_ignored=True,
                    transport=transport,
                    now=fixed,
                    registry_path=registry,
                )
            self.assertEqual(len(calls), 1)
            self.assertEqual(result["request_count"], 1)
            self.assertEqual(result["retry_count"], 0)
            probe_root = Path(result["probe_root"])
            self.assertTrue((probe_root / "00-request-manifest.json").is_file())
            self.assertTrue((probe_root / "02-raw-response.json").is_file())
            self.assertTrue((probe_root / "07-review-notes.md").is_file())
            self.assertTrue(index.is_file())
            self.assertTrue(review.is_file())

    def test_transport_failure_is_not_retried_and_reservation_remains(self):
        calls = 0

        def transport(_request, _timeout):
            nonlocal calls
            calls += 1
            raise TimeoutError("timed out")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "probe-evidence" / "dataforseo"
            registry = root / "attempt-registry.json"
            with (
                patch.object(core, "EVIDENCE_ROOT", root),
                patch.object(live, "EVIDENCE_ROOT", root),
                patch.object(live, "LIVE_EXECUTION_AUTHORIZED", True),
            ):
                with self.assertRaises(core.ProbeBlocked):
                    live.execute_one_c00(
                        owner_confirmation=live.OWNER_CONFIRMATION_PHRASE,
                        env={"DATAFORSEO_LOGIN": "user", "DATAFORSEO_PASSWORD": "pass"},
                        account_limits_recorded=True,
                        evidence_root_ignored=True,
                        transport=transport,
                        now=datetime(2026, 7, 12, 14, 30, tzinfo=timezone.utc),
                        registry_path=registry,
                    )
                self.assertTrue(live.duplicate_attempt_exists(registry))
            self.assertEqual(calls, 1)


if __name__ == "__main__":
    unittest.main()
