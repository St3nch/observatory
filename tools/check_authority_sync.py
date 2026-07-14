"""Fail when Observatory current-state authority drifts out of sync."""

from __future__ import annotations

import argparse
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
RETIRED_UNTRUSTED_ARTIFACTS = (
    "decisions/2026-07-13-db2-closure-and-db3-activation.md",
    "decisions/2026-07-13-db3-closure-and-db4-activation.md",
    "planning-inbox/db3-postgres-operational-boundary-specification.md",
    "planning-inbox/db3-physical-schema-specification.md",
    "planning-inbox/db3-specification-readiness-review.md",
)
CANDIDATE_FILES = (
    "planning-inbox/db2-physical-data-contract-freeze-specification.md",
    "planning-inbox/db2-freeze-v0-1-1-classification-corrections.md",
)
EXPECTED_PROJECT_STATUS = "db2-reconciliation-last-trusted-db1"
EXPECTED_LATER_DATABASE_MILESTONES = (
    "db3-db4-inactive-no-artifacts-fresh-db3-requires-db2-owner-gate"
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

    future_placeholder_claims = (
        "Future roadmap placeholder only. No present DB-3 authority or artifact exists.",
        "Future roadmap placeholder only. No present DB-4 authority or artifact exists.",
    )
    for claim in future_placeholder_claims:
        if claim not in post_roadmap:
            errors.append(f"post-v1 roadmap lacks future-only authority guard: {claim}")

    recovery_text = _read(root, RECOVERY_DECISION, errors)
    if recovery_text and "ESTABLISH DB-1 AS THE LAST TRUSTED" not in recovery_text:
        errors.append("recovery decision lacks the trusted DB-1 ruling")
    if recovery_text and "ANY FUTURE DB-3 WORK MUST BE CREATED FRESH" not in recovery_text:
        errors.append("recovery decision lacks the fresh future DB-3 gate")

    for relative_path in RETIRED_UNTRUSTED_ARTIFACTS:
        if (root / relative_path).exists():
            errors.append(f"retired untrusted artifact exists: {relative_path}")

    for relative_path in CANDIDATE_FILES:
        text = _read(root, relative_path, errors)
        if text and "Status:" in text and "candidate" not in text.splitlines()[2].lower():
            errors.append(f"recovery candidate has an authoritative status: {relative_path}")

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
                    "pyproject project status disagrees with recovery authority: "
                    f"{status!r}"
                )
            if later_database_milestones != EXPECTED_LATER_DATABASE_MILESTONES:
                errors.append(
                    "pyproject later-database posture disagrees with recovery authority: "
                    f"{later_database_milestones!r}"
                )

    stale_current_claims = (
        "DB-4 — Database Hammer Harness and Migration Specification",
        "No later database milestone is active. DB-2 requires a separate owner decision.",
        "Their artifacts remain candidate material",
        "Existing DB-3 documents may be read as untrusted candidates",
    )
    for source, text in (
        ("ACTIVE_CONTEXT.md", active_context),
        ("NEXT_SESSION_HANDOFF.md", handoff),
    ):
        for stale in stale_current_claims:
            if stale in text:
                errors.append(f"stale current-state claim in {source}: {stale}")

    for forbidden_path in ("migrations", "sql"):
        if (root / forbidden_path).exists():
            errors.append(
                f"unauthorized database implementation path exists during recovery: {forbidden_path}"
            )

    notes.append("DB-1 is the last trusted completed database milestone.")
    notes.append("DB-2 is reconciliation-only; implementation remains unauthorized.")
    notes.append("DB-3 and DB-4 are inactive with no active or authoritative artifacts.")
    notes.append("A passing sync check is not an implementation gate.")

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
