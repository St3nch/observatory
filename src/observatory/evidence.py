"""Evidence Store status and report-only scrub CLIs."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from observatory.evidence_store import (
    EvidenceStore,
    FormatError,
    IntegrityError,
    StoreError,
    inspect_store,
    open_store,
)
from observatory.settings import get_settings


def resolve_evidence_root(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    configured = get_settings().evidence_root
    if configured is not None:
        return configured
    raise ValueError("evidence root is required (--evidence-root or OBSERVATORY_EVIDENCE_ROOT)")


def report_path(root: Path, candidate: Path) -> str:
    """Return a POSIX path relative to the Evidence root."""

    try:
        return candidate.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return candidate.resolve().as_posix()


def scrub_store(store: EvidenceStore) -> list[Path]:
    """Verify every commitment-claiming directory at its exact marker parent."""

    failed: list[Path] = []
    for bundle in store.list_commitment_claiming_directories("attempts"):
        try:
            store.verify_attempt_directory(bundle)
        except (IntegrityError, StoreError):
            failed.append(bundle)
    for bundle in store.list_commitment_claiming_directories("captures"):
        try:
            store.verify_capture_directory(bundle)
        except (IntegrityError, StoreError):
            failed.append(bundle)
    return failed


def status_command(root: Path) -> int:
    try:
        open_store(root)
    except FormatError as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    sys.stdout.write("format-2 ok\n")
    return 0


def scrub_command(root: Path) -> int:
    try:
        store = inspect_store(root)
    except FormatError as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    failed = scrub_store(store)
    for bundle in failed:
        sys.stdout.write(f"{report_path(store.root, bundle)}\n")
    return 1 if failed else 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="observatory.evidence",
        description="Evidence Store status and report-only scrub.",
    )
    parser.add_argument("command", choices=("status", "scrub"))
    parser.add_argument("--evidence-root", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        root = resolve_evidence_root(args.evidence_root)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    if args.command == "status":
        return status_command(root)
    return scrub_command(root)


if __name__ == "__main__":
    raise SystemExit(main())
