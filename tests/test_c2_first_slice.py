from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from observatory_c2 import (  # noqa: E402
    CandidateObservation,
    ObservationPackage,
    RawSupportManifest,
    ScopeContext,
    admit_candidate_observation,
    recovery_snapshot_digest,
    validate_observation_package,
    validate_recovery_snapshot_digest,
)
from observatory_c2.c2 import (  # noqa: E402
    supersede_observation,
    validate_candidate_observation,
    validate_no_external_markers,
)


CAPTURED_AT = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)


def valid_package() -> ObservationPackage:
    return ObservationPackage(
        observation_package_id="pkg_fixture_valid",
        scope=ScopeContext(
            scope_id="scope_internal_fixture",
            scope_class="internal_fixture",
            scope_label="owner controlled public manual fixture",
        ),
        source_family="controlled_public_fixture",
        capture_method="manual_controlled_fixture",
        operator_intent="observe public fixture metadata only",
        artifact_reference="fixtures/public/manual/page-a.html",
        captured_at=CAPTURED_AT,
        rights_class="expressly_permitted",
        rights_basis="owner-controlled public fixture for local tests",
        retention_class="retain_project_evidence",
        retention_basis="non-customer fixture evidence",
        claim_use_warning="Point-in-time observation only; not current truth.",
    )


def valid_candidate() -> CandidateObservation:
    return CandidateObservation(
        candidate_observation_id="cand_fixture_valid",
        observation_package_id="pkg_fixture_valid",
        candidate_type="public_page_metadata",
        observed_text="Fixture page title: Observatory C2 public manual page.",
    )


def raw_support(text: str, *, digest: str | None = None) -> RawSupportManifest:
    return RawSupportManifest(
        raw_support_id="raw_fixture_valid",
        raw_pointer="fixtures/public/manual/page-a.html",
        raw_sha256=digest or sha256(text.encode("utf-8")).hexdigest(),
        raw_bytes=len(text.encode("utf-8")),
        raw_media_type="text/html",
        retention_class="retain_project_evidence",
    ).verify_text(text)


class C2FirstSliceHammerTests(unittest.TestCase):
    def test_valid_package_admits_candidate_with_internal_evidence_id(self) -> None:
        result = admit_candidate_observation(valid_package(), valid_candidate(), now=CAPTURED_AT)

        self.assertTrue(result.observation_id.startswith("obs_"))
        self.assertTrue(result.evidence.evidence_id.startswith("ev_"))
        self.assertEqual(result.evidence.observation_id, result.observation_id)
        self.assertTrue(result.evidence.citation_handle.startswith("cite:ev_"))
        self.assertEqual(result.package.package_status, "admitted")
        self.assertEqual(result.candidate.candidate_status, "valid")
        self.assertEqual(result.audit_events[0].event_type, "observation_admitted")

    def test_h1_scope_isolation_rejects_customer_like_scope(self) -> None:
        package = valid_package()
        bad_scope = ScopeContext(
            scope_id="scope_bad",
            scope_class="internal_fixture",
            scope_label="customer_email=person@example.com",
        )
        issues = validate_observation_package(package.__class__(**{**package.__dict__, "scope": bad_scope}))

        self.assertIn("customer_private_scope", {issue.code for issue in issues})

    def test_h2_rights_fail_closed_rejects_missing_rights(self) -> None:
        package = valid_package()
        issues = validate_observation_package(package.__class__(**{**package.__dict__, "rights_class": ""}))

        self.assertIn("rights_fail_closed", {issue.code for issue in issues})

    def test_h3_retention_fail_closed_rejects_forbidden_retention(self) -> None:
        package = valid_package()
        issues = validate_observation_package(package.__class__(**{**package.__dict__, "retention_class": "forbidden_no_capture"}))

        self.assertIn("retention_fail_closed", {issue.code for issue in issues})

    def test_h5_strategy_text_is_rejected_before_evidence(self) -> None:
        candidate = CandidateObservation(
            candidate_observation_id="cand_strategy",
            observation_package_id="pkg_fixture_valid",
            candidate_type="public_page_metadata",
            observed_text="Recommendation: this page should optimize for best keyword.",
        )
        issues = validate_candidate_observation(candidate)

        self.assertIn("strategy_text_rejected", {issue.code for issue in issues})
        with self.assertRaises(ValueError):
            admit_candidate_observation(valid_package(), candidate)

    def test_h6_envelope_validation_rejects_missing_captured_at(self) -> None:
        package = valid_package()
        issues = validate_observation_package(package.__class__(**{**package.__dict__, "captured_at": None}))

        self.assertIn("missing_captured_at", {issue.code for issue in issues})

    def test_h9_claim_use_warning_requires_point_in_time_caveat(self) -> None:
        package = valid_package()
        issues = validate_observation_package(package.__class__(**{**package.__dict__, "claim_use_warning": "current truth"}))

        self.assertIn("weak_claim_use_warning", {issue.code for issue in issues})

    def test_h12_raw_support_hash_mismatch_blocks_admission_path(self) -> None:
        manifest = raw_support("<html>actual</html>", digest="0" * 64)
        issues = validate_observation_package(valid_package(), raw_support=manifest)

        self.assertIn("raw_hash_not_verified", {issue.code for issue in issues})

    def test_h15_evidence_id_is_not_minted_for_invalid_candidate(self) -> None:
        candidate = CandidateObservation(
            candidate_observation_id="cand_private",
            observation_package_id="pkg_fixture_valid",
            candidate_type="public_page_metadata",
            observed_text="customer_id=secret-customer should never become evidence",
        )

        with self.assertRaises(ValueError):
            admit_candidate_observation(valid_package(), candidate)

    def test_h18_forbidden_surface_names_are_rejected(self) -> None:
        issues = validate_no_external_markers(
            [
                "src/observatory_c2/provider_client.py",
                "src/observatory_c2/dashboard.py",
                "src/observatory_c2/strategy_store.py",
            ]
        )

        self.assertEqual(len(issues), 3)
        self.assertEqual({issue.code for issue in issues}, {"forbidden_surface_marker"})

    def test_h19_supersession_does_not_mutate_original_admission(self) -> None:
        result = admit_candidate_observation(valid_package(), valid_candidate(), now=CAPTURED_AT)
        superseded, event = supersede_observation(result, reason="fixture correction", now=CAPTURED_AT)

        self.assertEqual(result.evidence.evidence_status, "active")
        self.assertEqual(superseded.evidence.evidence_status, "superseded")
        self.assertEqual(event.event_type, "observation_superseded")
        self.assertEqual(len(result.audit_events), 1)
        self.assertEqual(len(superseded.audit_events), 2)

    def test_h21_audit_event_exists_for_admission(self) -> None:
        result = admit_candidate_observation(valid_package(), valid_candidate(), now=CAPTURED_AT)

        self.assertEqual(result.audit_events[0].entity_type, "observation")
        self.assertEqual(result.audit_events[0].entity_id, result.observation_id)
        self.assertTrue(result.audit_events[0].event_reason)

    def test_h22_recovery_digest_detects_snapshot_tamper(self) -> None:
        result = admit_candidate_observation(valid_package(), valid_candidate(), now=CAPTURED_AT)
        digest = recovery_snapshot_digest(result)

        self.assertEqual(validate_recovery_snapshot_digest(result, digest), ())

        tampered_candidate = CandidateObservation(
            candidate_observation_id=result.candidate.candidate_observation_id,
            observation_package_id=result.candidate.observation_package_id,
            candidate_type=result.candidate.candidate_type,
            observed_text="Fixture page title: tampered text.",
            candidate_status=result.candidate.candidate_status,
            validation_errors=result.candidate.validation_errors,
        )
        tampered_result = result.__class__(**{**result.__dict__, "candidate": tampered_candidate})
        issues = validate_recovery_snapshot_digest(tampered_result, digest)

        self.assertIn("recovery_digest_mismatch", {issue.code for issue in issues})


if __name__ == "__main__":
    unittest.main()
