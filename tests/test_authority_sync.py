from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from tools.check_authority_sync import (
    AUTHORIZED_DB3_PLANNING_ARTIFACTS,
    DB2_ACCEPTANCE_DB3_PLANNING_DECISION,
    DB2_CORRECTION_DISPOSITION,
    DB2_CANONICAL_CANDIDATE,
    DB2_FRESH_READINESS_REVIEW,
    EXPECTED_DB2_CANDIDATE_STATUS,
    EXPECTED_DB2_CANDIDATE_SHA256,
    EXPECTED_DB2_CANDIDATE_VERSION,
    EXPECTED_DB2_CONCEPT_CLASSIFICATIONS,
    EXPECTED_DB2_CORRECTION_STATUS,
    EXPECTED_DB2_REVIEW_STATUS,
    EXPECTED_ACTIVE_MILESTONE,
    REJECTED_DB2_READINESS_REVIEW,
    RETIRED_UNTRUSTED_ARTIFACTS,
    ROOT,
    _status_line,
    _unauthorized_later_artifacts,
    _table_compound_classification_rows,
    _table_primary_classifications,
    check_repository,
)


class AuthoritySyncTests(unittest.TestCase):
    @staticmethod
    def _classification_row(classification_cell: str) -> str:
        return (
            "| Synthetic concept | Definition | "
            f"{classification_cell} | Lifecycle |\n"
        )

    def test_current_authority_is_synchronized(self) -> None:
        result = check_repository(ROOT)
        self.assertTrue(result.passed, "\n".join(result.errors))
        self.assertEqual(EXPECTED_ACTIVE_MILESTONE, result.active_milestone)

    def test_accepted_db2_freeze_bytes_are_exact(self) -> None:
        candidate = ROOT / DB2_CANONICAL_CANDIDATE
        candidate_text = candidate.read_text(encoding="utf-8")
        self.assertEqual(
            1,
            candidate_text.splitlines().count(
                f"Candidate version: {EXPECTED_DB2_CANDIDATE_VERSION}"
            ),
        )
        self.assertEqual(
            EXPECTED_DB2_CANDIDATE_SHA256,
            hashlib.sha256(candidate.read_bytes()).hexdigest(),
        )

    def test_db2_package_uses_exact_non_authoritative_statuses(self) -> None:
        expected = (
            (DB2_CANONICAL_CANDIDATE, EXPECTED_DB2_CANDIDATE_STATUS),
            (DB2_FRESH_READINESS_REVIEW, EXPECTED_DB2_REVIEW_STATUS),
            (DB2_CORRECTION_DISPOSITION, EXPECTED_DB2_CORRECTION_STATUS),
        )
        for relative_path, expected_status in expected:
            with self.subTest(path=relative_path):
                text = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertEqual(expected_status, _status_line(text))
        self.assertNotEqual(
            EXPECTED_DB2_CANDIDATE_STATUS,
            _status_line("Status: authority with stray candidate wording"),
        )

    def test_db2_closure_decision_binds_exact_artifact_and_db3_gate(self) -> None:
        decision_path = ROOT / DB2_ACCEPTANCE_DB3_PLANNING_DECISION
        self.assertTrue(decision_path.is_file())
        decision = decision_path.read_text(encoding="utf-8")
        for exact_claim in (
            f"path: {DB2_CANONICAL_CANDIDATE}",
            f"version: {EXPECTED_DB2_CANDIDATE_VERSION}",
            f"sha256: {EXPECTED_DB2_CANDIDATE_SHA256}",
            "### OR-H1 — accept the exact DB-2 freeze",
            "### OR-H2 — close DB-2",
            "### OR-H3 — authorize fresh DB-3 planning",
            EXPECTED_ACTIVE_MILESTONE,
            "DB-3 authority is planning and specification only.",
            "DB-4 remains inactive.",
            "implementation authority: no",
        ):
            with self.subTest(claim=exact_claim):
                self.assertIn(exact_claim, decision)

    def test_db2_is_last_trusted_completed_database_milestone(self) -> None:
        active_context = (ROOT / "ACTIVE_CONTEXT.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        self.assertIn(
            "DB-2 is now the last trusted completed database milestone.",
            active_context,
        )
        self.assertIn(
            "DB-2 is now the last trusted completed database milestone",
            roadmap,
        )

    def test_or_h_owner_gate_is_fully_ruled(self) -> None:
        tracker = (ROOT / "planning-inbox/owner-ruling-tracker.md").read_text(
            encoding="utf-8"
        )
        for ruling_id in ("OR-H1", "OR-H2", "OR-H3"):
            rows = [
                line
                for line in tracker.splitlines()
                if line.startswith(f"| {ruling_id} |")
            ]
            self.assertEqual(1, len(rows), ruling_id)
            self.assertIn("ruled —", rows[0])
            self.assertIn(DB2_ACCEPTANCE_DB3_PLANNING_DECISION, rows[0])

    def test_capture_identity_matches_accepted_contracts(self) -> None:
        text = (ROOT / DB2_CANONICAL_CANDIDATE).read_text(encoding="utf-8")
        rows = {}
        for line in text.splitlines():
            if line.startswith("| "):
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                rows[cells[0]] = cells
        package = rows["CapturePackage"]
        capture = rows["Capture event/attempt"]
        unresolved = rows["Proposed `capture_attempt_id` rename/alias"]
        self.assertEqual("Observatory, `capture_package_id` only", package[4])
        self.assertEqual("`durable`", package[2])
        self.assertEqual("Observatory, `capture_id`", capture[4])
        self.assertEqual("`append_only`", capture[2])
        self.assertEqual(
            "One accepted capture event or attempt under one package; explains "
            "zero, one, or many observations",
            capture[1],
        )
        self.assertEqual("`unresolved`", unresolved[2])
        self.assertEqual("No active namespace; owner ruling required", unresolved[4])
        self.assertNotIn("alias to `capture_package_id`", text)
        self.assertEqual(1, text.count("capture_attempt_id"))

    def test_reconciled_concepts_have_exact_primary_classifications(self) -> None:
        text = (ROOT / DB2_CANONICAL_CANDIDATE).read_text(encoding="utf-8")
        self.assertEqual((), _table_compound_classification_rows(text))
        classifications = _table_primary_classifications(text)
        for concept, expected in EXPECTED_DB2_CONCEPT_CLASSIFICATIONS.items():
            with self.subTest(concept=concept):
                self.assertEqual(expected, classifications.get(concept))

    def test_singular_classification_is_valid(self) -> None:
        text = self._classification_row("`append_only`")
        self.assertEqual((), _table_compound_classification_rows(text))

    def test_singular_classification_with_plain_qualifier_is_valid(self) -> None:
        text = self._classification_row("`append_only`; audit_first")
        self.assertEqual((), _table_compound_classification_rows(text))

    def test_backticked_nonclassification_qualifier_is_not_a_second_class(self) -> None:
        text = self._classification_row("`append_only`; `audit_first`")
        self.assertEqual((), _table_compound_classification_rows(text))

    def test_separately_backticked_primary_classifications_are_invalid(self) -> None:
        text = self._classification_row("`append_only`; `durable`")
        self.assertEqual(
            ("Synthetic concept",),
            _table_compound_classification_rows(text),
        )

    def test_compound_classification_with_qualifier_inside_code_span_is_invalid(
        self,
    ) -> None:
        text = self._classification_row("`append_only audit_first`")
        self.assertEqual(
            ("Synthetic concept",),
            _table_compound_classification_rows(text),
        )

    def test_two_classifications_inside_one_code_span_are_invalid(self) -> None:
        text = self._classification_row("`append_only durable`")
        self.assertEqual(
            ("Synthetic concept",),
            _table_compound_classification_rows(text),
        )

    def test_punctuation_separated_classifications_are_invalid(self) -> None:
        for classification_cell in (
            "`append_only/derived`",
            "`append_only, durable`",
        ):
            with self.subTest(classification_cell=classification_cell):
                text = self._classification_row(classification_cell)
                self.assertEqual(
                    ("Synthetic concept",),
                    _table_compound_classification_rows(text),
                )

    def test_accepted_artifact_record_is_unique_and_rejected_review_is_absent(
        self,
    ) -> None:
        roadmap = (ROOT / "POST_V1_DATABASE_ROADMAP.md").read_text(
            encoding="utf-8"
        )
        self.assertEqual(1, roadmap.count("Accepted DB-2 artifact:"))
        self.assertNotIn("Current reconciled review target:", roadmap)
        self.assertEqual(
            1,
            roadmap.splitlines().count(
                f"version {EXPECTED_DB2_CANDIDATE_VERSION}"
            ),
        )
        self.assertEqual(
            1,
            roadmap.splitlines().count(
                f"sha256 {EXPECTED_DB2_CANDIDATE_SHA256}"
            ),
        )
        self.assertIn(DB2_ACCEPTANCE_DB3_PLANNING_DECISION, roadmap)
        self.assertFalse((ROOT / REJECTED_DB2_READINESS_REVIEW).exists())

    def test_db3_planning_artifact_allowlist_is_exact(self) -> None:
        self.assertEqual(
            {
                "planning-inbox/db3-accepted-input-traceability-matrix.md",
                "planning-inbox/db3-fresh-postgres-design-specification-v0-1.md",
                "planning-inbox/db3-future-ob-dev-control-plane-contract-v0-1.md",
                "planning-inbox/db3-owner-readiness-review.md",
            },
            set(AUTHORIZED_DB3_PLANNING_ARTIFACTS),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "planning-inbox").mkdir()
            (root / "decisions").mkdir()
            for relative_path in AUTHORIZED_DB3_PLANNING_ARTIFACTS:
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("allowed\n", encoding="utf-8")
            decision = root / DB2_ACCEPTANCE_DB3_PLANNING_DECISION
            decision.write_text("allowed\n", encoding="utf-8")

            unexpected = {
                "planning-inbox/db3-surprise-specification.md",
                "decisions/2026-07-14-db4-surprise-activation.md",
            }
            for relative_path in unexpected:
                path = root / relative_path
                path.write_text("unexpected\n", encoding="utf-8")

            self.assertEqual(
                unexpected,
                set(_unauthorized_later_artifacts(root)),
            )

    def test_db4_and_retired_artifacts_remain_absent(self) -> None:
        self.assertEqual(5, len(RETIRED_UNTRUSTED_ARTIFACTS))
        for relative_path in RETIRED_UNTRUSTED_ARTIFACTS:
            with self.subTest(path=relative_path):
                self.assertFalse((ROOT / relative_path).exists())
        post_roadmap = (ROOT / "POST_V1_DATABASE_ROADMAP.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "Future roadmap placeholder only. No present DB-4 authority or artifact exists.",
            post_roadmap,
        )

    def test_no_database_implementation_paths_exist(self) -> None:
        self.assertFalse((ROOT / "migrations").exists())
        self.assertFalse((ROOT / "sql").exists())


if __name__ == "__main__":
    unittest.main()
