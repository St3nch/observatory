"""Fail when Observatory current-state authority drifts out of sync."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_ROOT_FILES = (
    "README.md",
    "LLM_START_HERE.md",
    "ACTIVE_CONTEXT.md",
    "ROADMAP.md",
    "ROADMAP_RULES.md",
    "REPO_MAP.md",
    "00-project-overview.md",
    "01-harvest-register.md",
    "02-boundaries.md",
    "NEXT_SESSION_HANDOFF.md",
)

RECOVERY_DECISION = "decisions/2026-07-13-database-phase-recovery-to-db1.md"
DB2_ACCEPTANCE_DB3_PLANNING_DECISION = (
    "decisions/2026-07-14-db2-freeze-acceptance-and-db3-planning-authorization.md"
)
DB3_ACCEPTANCE_DB4_PACKAGE_DECISION = (
    "decisions/2026-07-14-db3-acceptance-closure-and-db4-package-preparation.md"
)
DB4_PACKAGE_IMPLEMENTATION_DECISION = (
    "decisions/2026-07-14-db4-package-acceptance-and-phased-implementation-authorization.md"
)
DB4_AUDIT_REMEDIATION_DECISION = (
    "decisions/2026-07-14-db4-audit-acceptance-and-remediation-activation.md"
)
DB4_REMEDIATION_IMPLEMENTATION_DECISION = (
    "decisions/2026-07-14-db4-remediation-implementation-authorization.md"
)
DB4_AUDIT_REMEDIATION_PLAN = "planning-inbox/db4-audit-remediation-program-v0-1.md"
AUTHORIZED_DB4_REMEDIATION_ARTIFACTS = (
    "planning-inbox/db4-db3-implementation-traceability-matrix.md",
    "planning-inbox/db4-migration-history-redesign-options.md",
    "planning-inbox/db4-behavioral-hammer-remapping.md",
    "planning-inbox/db4-remediation-owner-readiness-review.md",
    "planning-inbox/db4-remediation-exact-implementation-manifest-v0-1.md",
    "planning-inbox/db4-proof-security-and-operations-package-v0-1.md",
    "planning-inbox/db4-one-restart-implementation-and-validation-plan-v0-1.md",
    "planning-inbox/db4-remediation-implementation-package-readiness-review.md",
)
RETIRED_UNTRUSTED_ARTIFACTS = (
    "decisions/2026-07-13-db2-closure-and-db3-activation.md",
    "decisions/2026-07-13-db3-closure-and-db4-activation.md",
    "planning-inbox/db3-postgres-operational-boundary-specification.md",
    "planning-inbox/db3-physical-schema-specification.md",
    "planning-inbox/db3-specification-readiness-review.md",
)
AUTHORIZED_DB3_PLANNING_ARTIFACTS = (
    "planning-inbox/db3-accepted-input-traceability-matrix.md",
    "planning-inbox/db3-fresh-postgres-design-specification-v0-1.md",
    "planning-inbox/db3-future-ob-dev-control-plane-contract-v0-1.md",
    "planning-inbox/db3-owner-readiness-review.md",
)
EXPECTED_DB3_ARTIFACT_SHA256 = {
    "planning-inbox/db3-accepted-input-traceability-matrix.md": (
        "db2ae41552aa4fc2c88b450f86f8070fb8e3cc023fb93fc7e7a39ab625aadc98"
    ),
    "planning-inbox/db3-fresh-postgres-design-specification-v0-1.md": (
        "9b79f0551fac9bbea11bc6e5afbececf48e216e47f41c3554e5806903f666e5e"
    ),
    "planning-inbox/db3-future-ob-dev-control-plane-contract-v0-1.md": (
        "d13e83b8fd74fd4c427a3ede92c70e24a252458b80c8abc6531cb5bd92ac2dec"
    ),
}
AUTHORIZED_DB4_PLANNING_ARTIFACTS = (
    "planning-inbox/db4-dormant-postgres-gap-and-disposition-matrix.md",
    "planning-inbox/db4-exact-ob-dev-implementation-package-specification.md",
    "planning-inbox/db4-migration-harness-and-proof-package-specification.md",
    "planning-inbox/db4-security-credentials-restart-and-owner-action-runbook.md",
    "planning-inbox/db4-owner-readiness-review.md",
)
EXPECTED_DB4_PLANNING_SHA256 = {
    "planning-inbox/db4-dormant-postgres-gap-and-disposition-matrix.md": (
        "a65919ace9da12c16b7dcc3aa7b8262c1150f2acbc2dc521c91ca7c2ee055a2a"
    ),
    "planning-inbox/db4-exact-ob-dev-implementation-package-specification.md": (
        "b44711fe80a1967ddf3d5413ce150fcc5d56ca7f61ddb5d8f42747c63d9ce14a"
    ),
    "planning-inbox/db4-migration-harness-and-proof-package-specification.md": (
        "9aff671e31fe94dabe5acca6a6631b14f8197a7c85ad55115caced354c7dad2e"
    ),
    "planning-inbox/db4-security-credentials-restart-and-owner-action-runbook.md": (
        "8c08648051a2b88c58d5999f861596c79e8a479f68f02e6061586111edb86b7f"
    ),
    "planning-inbox/db4-owner-readiness-review.md": (
        "1a2cfd0ff9f30be9ca793fc386a218deb3710860cd83f36ae294a354fd431c92"
    ),
}
DB2_CANONICAL_CANDIDATE = (
    "planning-inbox/db2-physical-data-contract-freeze-specification.md"
)
DB2_FRESH_READINESS_REVIEW = (
    "planning-inbox/db2-reconciled-candidate-v0-2-1-readiness-review.md"
)
DB2_CORRECTION_DISPOSITION = (
    "planning-inbox/db2-freeze-v0-1-1-classification-corrections.md"
)
REJECTED_DB2_READINESS_REVIEW = (
    "planning-inbox/db2-reconciled-candidate-v0-2-0-readiness-review.md"
)
EXPECTED_DB2_CANDIDATE_STATUS = (
    "Status: candidate under DB-2 recovery reconciliation; not accepted"
)
EXPECTED_DB2_REVIEW_STATUS = (
    "Status: replacement planning review after independent rejection; "
    "not acceptance, closure, or DB-3 authority"
)
EXPECTED_DB2_CORRECTION_STATUS = (
    "Status: historical correction-disposition record; not authority"
)
EXPECTED_DB2_CANDIDATE_VERSION = "0.2.1"
EXPECTED_DB2_CANDIDATE_SHA256 = (
    "7c24d38ea8e7634dea8cf52cd7b85b49eda18b8ecde5a00c74b6303809c17891"
)
EXPECTED_ACTIVE_MILESTONE = (
    "DB-4 — Database Hammer Harness and Migration Specification"
)
EXPECTED_DB2_CONCEPT_CLASSIFICATIONS = {
    "Observed artifact reference (`observed_artifact_reference`)": "durable",
    "Validation-failure vocabulary": "versioned",
    "Validation result": "append_only",
    "Validation status (`validation_status`)": "derived",
    "Rejection reason (`rejection_reason`)": "append_only",
    "`captured_at`": "append_only",
    "`provider_reported_time`": "append_only",
    "Observation age (`observation_age`)": "derived",
    "Age-band vocabulary": "versioned",
    "`age_band`": "derived",
    "`freshness_status`": "derived",
    "`volatility_class`": "derived",
    "Update-window input (`update_window`)": "ephemeral",
    "Historical observation claim (`historical_observation_claim`)": "ephemeral",
    "Current-state claim (`current_state_claim`)": "ephemeral",
    "Comparative claim (`comparative_claim`)": "ephemeral",
    "Absence claim (`absence_claim`)": "ephemeral",
    "Provider metric claim (`provider_metric_claim`)": "ephemeral",
    "AI/GEO claim (`ai_geo_claim`)": "ephemeral",
    "Marketplace claim (`marketplace_claim`)": "ephemeral",
    "Predictive claim (`predictive_claim`)": "forbidden",
    "Causal claim (`causal_claim`)": "forbidden",
    "Recommendation claim (`recommendation_claim`)": "forbidden",
    "Accepted conclusion (`accepted_conclusion`)": "forbidden",
    "Claim-intent vocabulary": "versioned",
    "Claim-intent selection (`claim_intent`)": "ephemeral",
    "Claim input (`claim`)": "ephemeral",
    "Claim support result (`claim_support`)": "derived",
    "Claim-use warning (`claim_use_warning`)": "derived",
    "Freshness warning (`freshness_warning`)": "derived",
    "Provider-attribution requirement (`provider_attribution_required`)": "derived",
    "Sample-bound warning (`sample_bound_warning`)": "derived",
    "Absence warning (`absence_warning`)": "derived",
    "Incomparability warning (`incomparability_warning`)": "derived",
    "Rights/retention warning (`rights_retention_warning`)": "derived",
    "Consumer-promotion requirement (`consumer_promotion_required`)": "derived",
}
EXPECTED_PROJECT_STATUS = "db4-remediation-last-trusted-db3"
EXPECTED_LATER_DATABASE_MILESTONES = (
    "db5-inactive-db4-remediation-separate-implementation-execution-gate-required"
)


@dataclass(frozen=True)
class CheckResult:
    root: str
    active_milestone: str | None
    errors: tuple[str, ...]
    notes: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict[str, object]:
        return {
            "root": self.root,
            "active_milestone": self.active_milestone,
            "passed": self.passed,
            "errors": list(self.errors),
            "notes": list(self.notes),
        }


def _read(root: Path, relative_path: str, errors: list[str]) -> str:
    path = root / relative_path
    if not path.is_file():
        errors.append(f"missing required file: {relative_path}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read {relative_path}: {exc}")
        return ""


def _section(text: str, heading: str) -> str | None:
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        return None
    content_start = start + len(marker)
    next_heading = text.find("\n## ", content_start)
    if next_heading < 0:
        next_heading = len(text)
    return text[content_start:next_heading]


def _fenced_value(text: str, heading: str) -> str | None:
    section = _section(text, heading)
    if section is None:
        return None
    match = re.search(r"\`\`\`text\s*\n(.*?)\n\`\`\`", section, re.DOTALL)
    if not match:
        return None
    return " ".join(match.group(1).split())


def _post_roadmap_active(text: str) -> str | None:
    match = re.search(r"^Active milestone:\s*(.+?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _status_line(text: str) -> str | None:
    match = re.search(r"^Status:.*$", text, re.MULTILINE)
    return match.group(0).strip() if match else None


def _table_primary_classifications(text: str) -> dict[str, str]:
    classifications: dict[str, str] = {}
    allowed = {
        "durable",
        "append_only",
        "versioned",
        "derived",
        "ephemeral",
        "external",
        "forbidden",
        "unresolved",
    }
    for line in text.splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        match = re.match(r"^`([^`]+)`", cells[2])
        if match and match.group(1) in allowed:
            classifications[cells[0]] = match.group(1)
    return classifications


def _table_compound_classification_rows(text: str) -> tuple[str, ...]:
    allowed = (
        "durable",
        "append_only",
        "versioned",
        "derived",
        "ephemeral",
        "external",
        "forbidden",
        "unresolved",
    )
    violations: list[str] = []
    for line in text.splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3 or not re.match(r"^`[^`]+`", cells[2]):
            continue
        class_tokens = re.findall(r"`([^`]+)`", cells[2])
        first_token = class_tokens[0]
        if first_token not in allowed:
            if any(first_token.startswith(classification) for classification in allowed):
                violations.append(cells[0])
            continue
        if sum(token in allowed for token in class_tokens) != 1:
            violations.append(cells[0])
    return tuple(violations)


def _unauthorized_later_artifacts(root: Path) -> tuple[str, ...]:
    allowed_paths = {
        DB2_ACCEPTANCE_DB3_PLANNING_DECISION,
        DB3_ACCEPTANCE_DB4_PACKAGE_DECISION,
        DB4_PACKAGE_IMPLEMENTATION_DECISION,
        DB4_AUDIT_REMEDIATION_DECISION,
        DB4_REMEDIATION_IMPLEMENTATION_DECISION,
        DB4_AUDIT_REMEDIATION_PLAN,
        *AUTHORIZED_DB4_REMEDIATION_ARTIFACTS,
        *AUTHORIZED_DB3_PLANNING_ARTIFACTS,
        *AUTHORIZED_DB4_PLANNING_ARTIFACTS,
    }
    return tuple(
        sorted(
            relative_path
            for folder in (root / "planning-inbox", root / "decisions")
            if folder.is_dir()
            for path in folder.iterdir()
            if path.is_file()
            for relative_path in (str(path.relative_to(root)).replace("\\", "/"),)
            if ("db3" in path.name.lower() or "db4" in path.name.lower())
            and relative_path not in allowed_paths
        )
    )


def check_repository(root: Path = ROOT) -> CheckResult:
    root = root.resolve()
    errors: list[str] = []
    notes: list[str] = []

    for relative_path in REQUIRED_ROOT_FILES:
        _read(root, relative_path, errors)

    active_context = _read(root, "ACTIVE_CONTEXT.md", errors)
    roadmap = _read(root, "ROADMAP.md", errors)
    post_roadmap = _read(root, "POST_V1_DATABASE_ROADMAP.md", errors)
    handoff = _read(root, "NEXT_SESSION_HANDOFF.md", errors)
    planning_index = _read(root, "planning-inbox/README.md", errors)
    owner_tracker = _read(root, "planning-inbox/owner-ruling-tracker.md", errors)
    decision_index = _read(root, "decisions/README.md", errors)

    active_values = {
        "ACTIVE_CONTEXT.md": _fenced_value(active_context, "Active Milestone"),
        "ROADMAP.md": _fenced_value(roadmap, "Active Milestone"),
        "NEXT_SESSION_HANDOFF.md": _fenced_value(handoff, "Active Milestone"),
        "POST_V1_DATABASE_ROADMAP.md": _post_roadmap_active(post_roadmap),
    }

    for source, value in active_values.items():
        if value is None:
            errors.append(f"cannot determine active milestone from {source}")

    present_values = {value for value in active_values.values() if value is not None}
    if len(present_values) > 1:
        rendered = ", ".join(
            f"{source}={value!r}" for source, value in active_values.items()
        )
        errors.append(f"active milestone disagreement: {rendered}")

    active_milestone = next(iter(present_values), None)
    if active_milestone != EXPECTED_ACTIVE_MILESTONE:
        errors.append(
            "active milestone is not the accepted DB-4 remediation gate: "
            f"{active_milestone!r}"
        )

    db3_closed_claim = "DB-3 was accepted and closed by"
    if db3_closed_claim not in post_roadmap:
        errors.append("post-v1 roadmap lacks the closed DB-3 gate")
    db4_active_claim = "Status: active in remediation and exact implementation-package preparation under"
    if db4_active_claim not in post_roadmap:
        errors.append("post-v1 roadmap lacks the active DB-4 remediation gate")
    if "New PostgreSQL execution under the prior campaign: not authorized" not in post_roadmap:
        errors.append("post-v1 roadmap lacks the DB-4 remediation non-execution guard")

    recovery_text = _read(root, RECOVERY_DECISION, errors)
    if recovery_text and "ESTABLISH DB-1 AS THE LAST TRUSTED" not in recovery_text:
        errors.append("recovery decision lacks the trusted DB-1 ruling")
    if recovery_text and "ANY FUTURE DB-3 WORK MUST BE CREATED FRESH" not in recovery_text:
        errors.append("recovery decision lacks the fresh future DB-3 gate")

    decision_text = _read(root, DB2_ACCEPTANCE_DB3_PLANNING_DECISION, errors)
    required_decision_claims = (
        "Status: accepted decision",
        "Date: 2026-07-14",
        "### OR-H1 — accept the exact DB-2 freeze",
        f"path: {DB2_CANONICAL_CANDIDATE}",
        f"version: {EXPECTED_DB2_CANDIDATE_VERSION}",
        f"sha256: {EXPECTED_DB2_CANDIDATE_SHA256}",
        "### OR-H2 — close DB-2",
        "DB-2 is trusted, accepted, complete, and is now the last trusted completed database milestone.",
        "### OR-H3 — authorize fresh DB-3 planning",
        "DB-3 — Postgres Operational Boundary and Physical Schema Specification",
        "DB-3 authority is planning and specification only.",
        "DB-4 remains inactive.",
        "implementation authority: no",
    )
    for claim in required_decision_claims:
        if decision_text and claim not in decision_text:
            errors.append(f"DB-2 closure decision lacks required claim: {claim!r}")
    decision_filename = Path(DB2_ACCEPTANCE_DB3_PLANNING_DECISION).name
    if decision_filename not in decision_index:
        errors.append("decisions index lacks the DB-2 closure / DB-3 planning decision")

    db3_decision_text = _read(root, DB3_ACCEPTANCE_DB4_PACKAGE_DECISION, errors)
    required_db3_decision_claims = (
        "Status: accepted decision",
        "Date: 2026-07-14",
        "### OR-I1 — accept the exact DB-3 planning package",
        "### OR-I2 — close DB-3 successfully",
        "DB-3 is trusted, accepted, complete, and becomes the last trusted",
        "### OR-I3 — authorize preparation of an exact DB-4 implementation package",
        EXPECTED_ACTIVE_MILESTONE,
        "DB-4 authority is limited to preparing an exact, reviewable implementation package.",
        "DB-4 implementation authority: no",
        "database authority: no",
        "execution authority: no",
    )
    for claim in required_db3_decision_claims:
        if db3_decision_text and claim not in db3_decision_text:
            errors.append(f"DB-3 closure decision lacks required claim: {claim!r}")
    for relative_path, expected_sha256 in EXPECTED_DB3_ARTIFACT_SHA256.items():
        if db3_decision_text:
            if f"path: {relative_path}" not in db3_decision_text:
                errors.append(
                    f"DB-3 closure decision lacks accepted path: {relative_path}"
                )
            if f"sha256: {expected_sha256}" not in db3_decision_text:
                errors.append(
                    f"DB-3 closure decision lacks accepted SHA-256: {relative_path}"
                )
        artifact_path = root / relative_path
        if not artifact_path.is_file():
            errors.append(f"missing accepted DB-3 artifact: {relative_path}")
        else:
            actual_sha256 = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
            if actual_sha256 != expected_sha256:
                errors.append(
                    "accepted DB-3 artifact SHA-256 mismatch: "
                    f"{relative_path} is {actual_sha256}"
                )
    db3_decision_filename = Path(DB3_ACCEPTANCE_DB4_PACKAGE_DECISION).name
    if db3_decision_filename not in decision_index:
        errors.append("decisions index lacks the DB-3 closure / DB-4 preparation decision")

    db4_artifact_texts: dict[str, str] = {}
    executable_sql = re.compile(
        r"^(CREATE|ALTER|DROP|GRANT|REVOKE|INSERT|UPDATE|DELETE|TRUNCATE)\s+",
        re.MULTILINE,
    )
    for relative_path, expected_sha256 in EXPECTED_DB4_PLANNING_SHA256.items():
        artifact_path = root / relative_path
        artifact_text = _read(root, relative_path, errors)
        db4_artifact_texts[relative_path] = artifact_text
        if artifact_path.is_file():
            actual_sha256 = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
            if actual_sha256 != expected_sha256:
                errors.append(
                    "DB-4 planning artifact SHA-256 mismatch: "
                    f"{relative_path} is {actual_sha256}"
                )
        if Path(relative_path).name not in planning_index:
            errors.append(f"planning index lacks DB-4 artifact: {relative_path}")
        if executable_sql.search(artifact_text):
            errors.append(
                f"DB-4 planning artifact contains executable SQL: {relative_path}"
            )

    readiness_path = "planning-inbox/db4-owner-readiness-review.md"
    readiness_text = db4_artifact_texts.get(readiness_path, "")
    for relative_path, expected_sha256 in EXPECTED_DB4_PLANNING_SHA256.items():
        if relative_path == readiness_path:
            continue
        if relative_path not in readiness_text or expected_sha256 not in readiness_text:
            errors.append(
                "DB-4 readiness review is not bound to the exact package artifact: "
                f"{relative_path}"
            )

    for relative_path in RETIRED_UNTRUSTED_ARTIFACTS:
        if (root / relative_path).exists():
            errors.append(f"retired untrusted artifact exists: {relative_path}")

    unauthorized_later_artifacts = _unauthorized_later_artifacts(root)
    if unauthorized_later_artifacts:
        errors.append(
            "unauthorized DB-3/DB-4 artifact exists during DB-4 package preparation: "
            + ", ".join(unauthorized_later_artifacts)
        )

    canonical_path = root / DB2_CANONICAL_CANDIDATE
    canonical_text = _read(root, DB2_CANONICAL_CANDIDATE, errors)
    review_text = _read(root, DB2_FRESH_READINESS_REVIEW, errors)
    correction_text = _read(root, DB2_CORRECTION_DISPOSITION, errors)
    expected_statuses = (
        (
            DB2_CANONICAL_CANDIDATE,
            canonical_text,
            EXPECTED_DB2_CANDIDATE_STATUS,
        ),
        (DB2_FRESH_READINESS_REVIEW, review_text, EXPECTED_DB2_REVIEW_STATUS),
        (
            DB2_CORRECTION_DISPOSITION,
            correction_text,
            EXPECTED_DB2_CORRECTION_STATUS,
        ),
    )
    for relative_path, text, expected_status in expected_statuses:
        if text and _status_line(text) != expected_status:
            errors.append(
                f"unexpected exact status for {relative_path}: "
                f"{_status_line(text)!r}; expected {expected_status!r}"
            )

    if (root / REJECTED_DB2_READINESS_REVIEW).exists():
        errors.append(
            "rejected v0.2.0 readiness review reappeared as a current file: "
            f"{REJECTED_DB2_READINESS_REVIEW}"
        )

    if canonical_text:
        version_line = f"Candidate version: {EXPECTED_DB2_CANDIDATE_VERSION}"
        if canonical_text.count(version_line) != 1:
            errors.append(
                "canonical DB-2 candidate version disagrees with the owner-review gate"
            )
        candidate_sha = hashlib.sha256(canonical_path.read_bytes()).hexdigest()
        if candidate_sha != EXPECTED_DB2_CANDIDATE_SHA256:
            errors.append(
                "canonical DB-2 candidate SHA-256 disagrees with the owner-review gate: "
                f"{candidate_sha}"
            )
        capture_package_marker = "Observatory, `capture_package_id` only"
        capture_id_marker = "Observatory, `capture_id`"
        unresolved_attempt_marker = "Proposed `capture_attempt_id` rename/alias"
        for marker in (
            capture_package_marker,
            capture_id_marker,
            unresolved_attempt_marker,
        ):
            if marker not in canonical_text:
                errors.append(f"canonical DB-2 capture identity is incomplete: {marker}")
        forbidden_capture_aliases = (
            "capture_id is an alias",
            "alias to `capture_package_id`",
            "`capture_attempt_id` | One bounded attempt",
        )
        for forbidden_alias in forbidden_capture_aliases:
            if forbidden_alias in canonical_text:
                errors.append(
                    "canonical DB-2 capture identity contradicts accepted contracts: "
                    f"{forbidden_alias}"
                )
        actual_classifications = _table_primary_classifications(canonical_text)
        compound_rows = _table_compound_classification_rows(canonical_text)
        if compound_rows:
            errors.append(
                "canonical DB-2 dossier has compound primary classifications: "
                + ", ".join(compound_rows)
            )
        for concept, expected_classification in (
            EXPECTED_DB2_CONCEPT_CLASSIFICATIONS.items()
        ):
            actual_classification = actual_classifications.get(concept)
            if actual_classification != expected_classification:
                errors.append(
                    "canonical DB-2 concept classification disagrees with the "
                    f"reconciled dossier: {concept!r} is {actual_classification!r}; "
                    f"expected {expected_classification!r}"
                )
    if review_text:
        for expected_value in (
            DB2_CANONICAL_CANDIDATE,
            EXPECTED_DB2_CANDIDATE_VERSION,
            EXPECTED_DB2_CANDIDATE_SHA256,
        ):
            if expected_value not in review_text:
                errors.append(
                    "fresh DB-2 readiness review is not bound to the exact candidate: "
                    f"missing {expected_value!r}"
                )

    accepted_heading = "Accepted DB-2 artifact:"
    if post_roadmap.count(accepted_heading) != 1:
        errors.append(
            "post-v1 roadmap must contain exactly one accepted DB-2 artifact block: "
            f"found {post_roadmap.count(accepted_heading)}"
        )
    if "Current reconciled review target:" in post_roadmap:
        errors.append("post-v1 roadmap retains the obsolete DB-2 review-target block")
    for expected_value in (
        DB2_CANONICAL_CANDIDATE,
        f"version {EXPECTED_DB2_CANDIDATE_VERSION}",
        f"sha256 {EXPECTED_DB2_CANDIDATE_SHA256}",
        f"decision: {DB2_ACCEPTANCE_DB3_PLANNING_DECISION}",
    ):
        if expected_value not in post_roadmap:
            errors.append(
                "post-v1 roadmap is not bound to the exact accepted DB-2 artifact: "
                f"missing {expected_value!r}"
            )

    pyproject_text = _read(root, "pyproject.toml", errors)
    if pyproject_text:
        try:
            data = tomllib.loads(pyproject_text)
            observatory_status = data["tool"]["observatory"]
            status = observatory_status["status"]
            later_database_milestones = observatory_status[
                "later_database_milestones"
            ]
        except (tomllib.TOMLDecodeError, KeyError, TypeError) as exc:
            errors.append(f"cannot read tool.observatory.status: {exc}")
        else:
            if status != EXPECTED_PROJECT_STATUS:
                errors.append(
                    "pyproject project status disagrees with DB-4 package-preparation authority: "
                    f"{status!r}"
                )
            if later_database_milestones != EXPECTED_LATER_DATABASE_MILESTONES:
                errors.append(
                    "pyproject later-database posture disagrees with DB-4 package-preparation authority: "
                    f"{later_database_milestones!r}"
                )

    required_current_claims = {
        "ACTIVE_CONTEXT.md": (
            "DB-4 is active in remediation.",
            "DB-5 is inactive.",
            DB4_REMEDIATION_IMPLEMENTATION_DECISION,
            DB4_AUDIT_REMEDIATION_PLAN,
            "bounded Observatory and ob-dev implementation",
            "PostgreSQL execution remains separately prohibited",
        ),
        "ROADMAP.md": (
            "DB-3 remains the accepted",
            "physical-design authority",
            "diagnostic evidence only",
            "and DB-5\nremain prohibited.",
        ),
        "POST_V1_DATABASE_ROADMAP.md": (
            "Last trusted database milestone: DB-3 — trusted, accepted, and complete",
            f"Active milestone: {EXPECTED_ACTIVE_MILESTONE}",
            "DB-4 state: exact bounded remediation implementation; PostgreSQL execution separately prohibited",
            "New PostgreSQL execution under the prior campaign: not authorized",
            DB4_REMEDIATION_IMPLEMENTATION_DECISION,
        ),
        "NEXT_SESSION_HANDOFF.md": (
            "DB-3 — trusted, accepted, and complete as physical-design authority",
            EXPECTED_ACTIVE_MILESTONE,
            DB4_REMEDIATION_IMPLEMENTATION_DECISION,
            DB4_AUDIT_REMEDIATION_PLAN,
            "PostgreSQL execution separately prohibited",
        ),
    }
    current_texts = {
        "ACTIVE_CONTEXT.md": active_context,
        "ROADMAP.md": roadmap,
        "POST_V1_DATABASE_ROADMAP.md": post_roadmap,
        "NEXT_SESSION_HANDOFF.md": handoff,
    }
    for source, claims in required_current_claims.items():
        for claim in claims:
            if claim not in current_texts[source]:
                errors.append(f"current authority claim missing from {source}: {claim}")

    stale_current_claims = (
        "DB-1 is the last trusted completed database milestone",
        "DB-2 is active for reconciliation",
        "DB-2 closure remains unaccepted",
        "candidate version 0.2.1 - not accepted",
        "DB-3 and DB-4 are inactive",
        "DB-3 — inactive; no active or authoritative artifact",
        "No present DB-3 authority or artifact exists",
        "Any future DB-3 work must be created fresh after an explicit DB-2 owner gate",
        "DB-3 is active for fresh planning and specification only.",
        "DB-4 remains inactive.",
        "DB-4: inactive; no active or authoritative artifact",
        "Future roadmap placeholder only. No present DB-4 authority or artifact exists.",
    )
    for source, text in (
        ("ACTIVE_CONTEXT.md", active_context),
        ("ROADMAP.md", roadmap),
        ("POST_V1_DATABASE_ROADMAP.md", post_roadmap),
        ("NEXT_SESSION_HANDOFF.md", handoff),
        ("planning-inbox/README.md", planning_index),
        ("planning-inbox/owner-ruling-tracker.md", owner_tracker),
    ):
        for stale in stale_current_claims:
            if stale in text:
                errors.append(f"stale current-state claim in {source}: {stale}")

    tracker_h = _section(owner_tracker, "Group H — Completed DB-2 owner gate")
    if tracker_h is None:
        errors.append("owner-ruling tracker lacks completed Group H")
    else:
        for ruling_id in ("OR-H1", "OR-H2", "OR-H3"):
            matching_rows = [
                line
                for line in tracker_h.splitlines()
                if line.startswith(f"| {ruling_id} |")
            ]
            if len(matching_rows) != 1 or "ruled —" not in matching_rows[0]:
                errors.append(f"{ruling_id} is not exactly ruled in owner tracker")
            if matching_rows and DB2_ACCEPTANCE_DB3_PLANNING_DECISION not in matching_rows[0]:
                errors.append(f"{ruling_id} is not bound to the DB-2 closure decision")

    tracker_i = _section(
        owner_tracker, "Group I — DB-3 acceptance and DB-4 package-preparation gate"
    )
    if tracker_i is None:
        errors.append("owner-ruling tracker lacks Group I")
    else:
        for ruling_id in ("OR-I1", "OR-I2", "OR-I3"):
            matching_rows = [
                line
                for line in tracker_i.splitlines()
                if line.startswith(f"| {ruling_id} |")
            ]
            if len(matching_rows) != 1 or "ruled —" not in matching_rows[0]:
                errors.append(f"{ruling_id} is not exactly ruled in owner tracker")
            if matching_rows and DB3_ACCEPTANCE_DB4_PACKAGE_DECISION not in matching_rows[0]:
                errors.append(f"{ruling_id} is not bound to the DB-3 closure decision")

    for forbidden_path in ("migrations", "sql"):
        if (root / forbidden_path).exists():
            errors.append(
                "unauthorized database implementation path exists during "
                f"DB-4 package preparation: {forbidden_path}"
            )

    notes.append("DB-1 remains trusted and complete.")
    notes.append("DB-2 remains trusted, accepted, and complete.")
    notes.append("DB-3 is trusted, accepted, complete, and remains the physical-design authority.")
    notes.append("DB-4 is active in remediation and exact implementation-package preparation.")
    notes.append("Prior disposable proof is diagnostic only; new PostgreSQL execution requires a separate owner gate.")
    notes.append("Governed/production databases, providers, customer/private data, recurring work, and DB-5 remain unauthorized.")
    notes.append("A passing sync check does not close DB-4 or activate DB-5.")

    return CheckResult(
        root=str(root),
        active_milestone=active_milestone,
        errors=tuple(errors),
        notes=tuple(notes),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = check_repository(args.root)
    if args.json:
        print(json.dumps(result.as_dict(), indent=2))
    else:
        print(f"root: {result.root}")
        print(f"active milestone: {result.active_milestone or 'unknown'}")
        print(f"authority sync: {'PASS' if result.passed else 'FAIL'}")
        for note in result.notes:
            print(f"note: {note}")
        for error in result.errors:
            print(f"error: {error}", file=sys.stderr)

    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
