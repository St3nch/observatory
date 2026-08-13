"""Format-2 Evidence Store: durable install, commit, and verify-on-read."""

from __future__ import annotations

import os
import secrets
from collections.abc import Mapping
from pathlib import Path
from typing import Final

from observatory.capture_event import (
    DocumentError,
    canonical_json,
    content_digest,
    validate_attempt,
    validate_capture,
)

FORMAT_BYTES: Final[bytes] = (
    b'{"attempt_bundle_layout":"v1","body_addressing":"sha256-content",'
    b'"bundle_body_materialization":"fixed-names-v1","canonical_json":"rfc8785-jcs",'
    b'"capture_bundle_layout":"v1","committed_marker":"event-id-newline",'
    b'"durability_profile":"local-posix-fsync-v1",'
    b'"event_id_encoding":"lowercase-hex-sha256","hash_algorithm":"sha256",'
    b'"path_sharding":"sha256-aa-bb","schema":"observatory.evidence-store-format",'
    b'"store_format":2,"timestamp_encoding":"utc-six-fractional-digits-z"}'
)
FORMAT_DIGEST: Final[str] = (
    "67fb338d3237a22a29f50110c705e552cd9af29f830c1bfffa9ee1cafa876c7e"
)

_HEX64: Final[str] = "0123456789abcdef"

__all__ = [
    "FORMAT_BYTES",
    "FORMAT_DIGEST",
    "EvidenceStore",
    "FormatError",
    "IntegrityError",
    "StoreError",
    "create_store",
    "open_store",
]


class StoreError(Exception):
    """Evidence Store protocol failure."""


class FormatError(StoreError):
    """FORMAT.json is missing, malformed, or not an Observatory store."""


class IntegrityError(StoreError):
    """A committed event failed verify-on-read."""


class EvidenceStore:
    """A format-2 Evidence Store root implementing local-posix-fsync-v1."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.recorded_ops: list[tuple[str, str]] = []

    def object_path(self, digest: str) -> Path:
        return self.root / "objects" / "sha256" / digest[:2] / digest[2:4] / digest

    def attempt_path(self, fingerprint: str, authorized_at: str, attempt_id: str) -> Path:
        year, month, day = _date_parts(authorized_at)
        return (
            self.root
            / "attempts"
            / "v1"
            / fingerprint[:2]
            / fingerprint[2:4]
            / fingerprint
            / year
            / month
            / day
            / attempt_id
        )

    def capture_path(self, capture_id: str) -> Path:
        return self.root / "captures" / "v1" / capture_id[:2] / capture_id[2:4] / capture_id

    def install_object(self, data: bytes) -> str:
        """Install *data* in the object pool. Recurrence is verified and accepted."""

        digest = content_digest(data)
        final = self.object_path(digest)
        self._ensure_shared_directories(final.parent)
        try:
            self._install_file(final, data)
        except FileExistsError:
            self._verify_pool_object(final, digest, len(data))
        return digest

    def commit_attempt(
        self,
        document: Mapping[str, object],
        *,
        request_body: bytes | None,
    ) -> str:
        """Durably commit an Attempt bundle. Success only after D5 verification."""

        validated = validate_attempt(document)
        manifest = canonical_json(validated)
        attempt_id = content_digest(manifest)
        fingerprint = _require_hex(validated["request_fingerprint"], "request_fingerprint")
        authorized_at = _require_str(validated["authorized_at"], "authorized_at")
        if request_body is not None:
            self._require_body_matches(validated["request"], request_body, "request")
            self.install_object(request_body)
        bundle = self.attempt_path(fingerprint, authorized_at, attempt_id)
        self._create_terminal_directory(bundle)
        self._install_file(bundle / "attempt.json", manifest)
        if request_body is not None:
            self._install_file(bundle / "request.body", request_body)
        self._install_file(bundle / "COMMITTED", f"{attempt_id}\n".encode())
        self._verify_attempt_bundle(bundle, attempt_id)
        return attempt_id

    def _require_verified_parent(self, attempt_id: str) -> dict[str, object]:
        try:
            parent = self.read_attempt(attempt_id)
        except IntegrityError:
            raise
        if parent is None:
            raise StoreError("cited Attempt is missing or uncommitted")
        return parent

    def commit_capture(
        self,
        document: Mapping[str, object],
        *,
        response_body: bytes | None,
    ) -> str:
        """Durably commit a Capture bundle. Success only after D5 verification."""

        preliminary = validate_capture(document)
        parent_id = _require_hex(preliminary["attempt_id"], "attempt_id")
        parent = self._require_verified_parent(parent_id)
        try:
            validated = validate_capture(document, attempt=parent)
        except DocumentError as exc:
            raise StoreError("Capture does not agree with its parent Attempt") from exc
        manifest = canonical_json(validated)
        capture_id = content_digest(manifest)
        if response_body is not None:
            response = validated["response"]
            if not isinstance(response, Mapping):
                raise StoreError("response body supplied but Capture response is null")
            self._require_body_matches(response, response_body, "response")
            self.install_object(response_body)
        bundle = self.capture_path(capture_id)
        self._create_terminal_directory(bundle)
        self._install_file(bundle / "capture.json", manifest)
        if response_body is not None:
            self._install_file(bundle / "response.body", response_body)
        self._install_file(bundle / "COMMITTED", f"{capture_id}\n".encode())
        self._verify_capture_bundle(bundle, capture_id)
        return capture_id

    def read_attempt(self, attempt_id: str) -> dict[str, object] | None:
        """Return a verified Attempt, or None if the bundle is uncommitted (D6)."""

        bundle = self._find_bundle("attempts", attempt_id)
        if bundle is None:
            return None
        committed = bundle / "COMMITTED"
        if not committed.is_file():
            return None
        return self._verify_attempt_bundle(bundle, attempt_id)

    def read_capture(self, capture_id: str) -> dict[str, object] | None:
        """Return a verified Capture, or None if the bundle is uncommitted (D6)."""

        bundle = self._find_bundle("captures", capture_id)
        if bundle is None:
            return None
        committed = bundle / "COMMITTED"
        if not committed.is_file():
            return None
        return self._verify_capture_bundle(bundle, capture_id)

    def _tmp_dir(self) -> Path:
        return self.root / ".tmp"

    def _record(self, op: str, path: Path) -> None:
        self.recorded_ops.append((op, str(path)))

    def _fsync_dir(self, directory: Path) -> None:
        fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        self._record("fsync_dir", directory)

    def _ensure_shared_directories(self, directory: Path) -> None:
        relative = directory.relative_to(self.root)
        current = self.root
        for part in relative.parts:
            child = current / part
            try:
                os.mkdir(child)
            except FileExistsError:
                if not child.is_dir():
                    raise StoreError(
                        f"shared path exists and is not a directory: {child}"
                    ) from None
            else:
                self._record("mkdir", child)
                self._fsync_dir(current)
            current = child

    def _create_terminal_directory(self, directory: Path) -> None:
        self._ensure_shared_directories(directory.parent)
        try:
            os.mkdir(directory)
        except FileExistsError as exc:
            raise StoreError(f"terminal bundle directory exists: {directory}") from exc
        self._record("mkdir_terminal", directory)
        self._fsync_dir(directory.parent)

    def _install_file(self, final: Path, data: bytes) -> None:
        tmp = self._tmp_dir() / f"{os.getpid()}-{secrets.token_hex(16)}"
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        fd = os.open(tmp, flags, 0o644)
        try:
            view = memoryview(data)
            while view:
                written = os.write(fd, view)
                view = view[written:]
            os.fsync(fd)
        except BaseException:
            os.close(fd)
            with suppress_oserror():
                os.unlink(tmp)
            raise
        else:
            os.close(fd)
        self._record("write_fsync", tmp)
        try:
            os.link(tmp, final)
        except FileExistsError:
            with suppress_oserror():
                os.unlink(tmp)
            self._record("unlink_tmp_after_eexist", tmp)
            raise
        self._record("link", final)
        os.unlink(tmp)
        self._record("unlink_tmp", tmp)
        self._fsync_dir(final.parent)

    def _read_verified_bytes(self, path: Path) -> bytes:
        try:
            return path.read_bytes()
        except FileNotFoundError as exc:
            raise IntegrityError(f"missing file {path}") from exc
        except OSError as exc:
            raise IntegrityError(f"unreadable file {path}") from exc

    def _verify_pool_object(self, path: Path, digest: str, size: int) -> None:
        if not path.is_file():
            raise IntegrityError(f"missing pool object {digest}")
        existing = self._read_verified_bytes(path)
        if len(existing) != size or content_digest(existing) != digest:
            raise IntegrityError(f"pool object mismatch at {path}")

    def _require_body_matches(self, envelope: object, data: bytes, name: str) -> None:
        if not isinstance(envelope, Mapping):
            raise StoreError(f"{name} envelope is not an object")
        state = envelope.get("body")
        if not isinstance(state, Mapping):
            raise StoreError(f"{name}.body is not a body_state")
        ref = state.get("body")
        if not isinstance(ref, Mapping):
            raise StoreError(f"{name} body_ref is missing")
        if ref.get("sha256") != content_digest(data) or ref.get("bytes") != len(data):
            raise StoreError(f"{name} body does not match cited body_ref")

    def _cited_refs(
        self,
        document: Mapping[str, object],
        *,
        include_response: bool,
    ) -> list[tuple[str, dict[str, object]]]:
        refs: list[tuple[str, dict[str, object]]] = []
        request = document["request"]
        if isinstance(request, Mapping):
            ref = _body_ref_from_state(request.get("body"))
            if ref is not None:
                refs.append(("request", ref))
        if include_response:
            response = document.get("response")
            if isinstance(response, Mapping):
                ref = _body_ref_from_state(response.get("body"))
                if ref is not None:
                    refs.append(("response", ref))
        return refs

    def _verify_bodies(
        self,
        document: Mapping[str, object],
        bundle: Path,
        *,
        bundle_body_role: str,
        include_response: bool,
    ) -> None:
        for role, ref in self._cited_refs(document, include_response=include_response):
            digest = _require_hex(ref["sha256"], f"{role}.sha256")
            size = ref["bytes"]
            if not isinstance(size, int):
                raise IntegrityError(f"{role} body bytes is not an integer")
            pool = self.object_path(digest)
            self._verify_pool_object(pool, digest, size)
            if role != bundle_body_role:
                continue
            name = "request.body" if role == "request" else "response.body"
            body_path = bundle / name
            if not body_path.is_file():
                raise IntegrityError(f"missing bundle body {name}")
            payload = self._read_verified_bytes(body_path)
            if len(payload) != size or content_digest(payload) != digest:
                raise IntegrityError(f"bundle body mismatch at {body_path}")
            if body_path.stat().st_ino == pool.stat().st_ino:
                raise IntegrityError(f"bundle body shares inode with pool object: {body_path}")

    def _verify_committed_marker(self, bundle: Path, event_id: str) -> None:
        marker = bundle / "COMMITTED"
        if not marker.is_file():
            raise IntegrityError(f"missing COMMITTED in {bundle}")
        if self._read_verified_bytes(marker) != f"{event_id}\n".encode():
            raise IntegrityError(f"COMMITTED does not match {event_id}")

    def _verify_attempt_bundle(self, bundle: Path, attempt_id: str) -> dict[str, object]:
        # D5 / six-step verify-on-read.
        raw = self._read_verified_bytes(bundle / "attempt.json")  # 1
        if content_digest(raw) != attempt_id or bundle.name != attempt_id:  # 2
            raise IntegrityError("attempt identity does not match stored bytes")
        self._verify_committed_marker(bundle, attempt_id)
        try:
            document = validate_attempt(raw)  # 3 schema+re-JCS, 4 cross-field
        except DocumentError as exc:
            raise IntegrityError("attempt schema or re-JCS failed") from exc
        if canonical_json(document) != raw:
            raise IntegrityError("re-JCS does not equal stored Attempt bytes")
        self._verify_bodies(  # 5 both locations
            document,
            bundle,
            bundle_body_role="request",
            include_response=False,
        )
        return document  # 6: any mismatch already raised

    def _verify_capture_bundle(self, bundle: Path, capture_id: str) -> dict[str, object]:
        raw = self._read_verified_bytes(bundle / "capture.json")
        if content_digest(raw) != capture_id or bundle.name != capture_id:
            raise IntegrityError("capture identity does not match stored bytes")
        self._verify_committed_marker(bundle, capture_id)
        try:
            preliminary = validate_capture(raw)
        except DocumentError as exc:
            raise IntegrityError("capture schema or re-JCS failed") from exc
        parent_id = _require_hex(preliminary["attempt_id"], "attempt_id")
        try:
            parent = self.read_attempt(parent_id)
        except IntegrityError:
            raise
        if parent is None:
            raise IntegrityError("cited Attempt is missing or uncommitted")
        try:
            document = validate_capture(raw, attempt=parent)
        except DocumentError as exc:
            raise IntegrityError("Capture does not agree with its parent Attempt") from exc
        if canonical_json(document) != raw:
            raise IntegrityError("re-JCS does not equal stored Capture bytes")
        self._verify_bodies(
            document,
            bundle,
            bundle_body_role="response",
            include_response=True,
        )
        return document

    def _find_bundle(self, kind: str, event_id: str) -> Path | None:
        base = self.root / kind / "v1"
        if not base.is_dir():
            return None
        matches = [path for path in base.rglob(event_id) if path.is_dir() and path.name == event_id]
        if len(matches) > 1:
            raise IntegrityError(f"multiple bundle directories named {event_id}")
        if not matches:
            return None
        return matches[0]

    def _purge_tmp(self) -> None:
        tmp = self._tmp_dir()
        if not tmp.exists():
            tmp.mkdir()
            self._record("mkdir", tmp)
            self._fsync_dir(self.root)
            return
        for child in tmp.iterdir():
            if child.is_file() or child.is_symlink():
                child.unlink()
                self._record("purge_tmp", child)
            elif child.is_dir():
                _rmtree(child)
                self._record("purge_tmp_dir", child)


class suppress_oserror:
    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None, *_: object) -> bool:
        return exc_type is not None and issubclass(exc_type, OSError)


def _date_parts(authorized_at: str) -> tuple[str, str, str]:
    if len(authorized_at) < 10 or authorized_at[4] != "-" or authorized_at[7] != "-":
        raise StoreError("authorized_at is not a timestamp")
    return authorized_at[0:4], authorized_at[5:7], authorized_at[8:10]


def _require_str(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise StoreError(f"{name} must be a string")
    return value


def _require_hex(value: object, name: str) -> str:
    text = _require_str(value, name)
    if len(text) != 64 or any(char not in _HEX64 for char in text):
        raise StoreError(f"{name} must be 64-character lowercase hex")
    return text


def _body_ref_from_state(state: object) -> dict[str, object] | None:
    if not isinstance(state, Mapping):
        return None
    if state.get("state") not in {"present_nonempty", "present_zero_bytes"}:
        return None
    ref = state.get("body")
    if not isinstance(ref, Mapping):
        return None
    return dict(ref)


def _rmtree(path: Path) -> None:
    for child in path.iterdir():
        if child.is_dir() and not child.is_symlink():
            _rmtree(child)
        else:
            child.unlink()
    path.rmdir()


def _read_format(root: Path) -> bytes:
    path = root / "FORMAT.json"
    if not path.is_file():
        raise FormatError("FORMAT.json is missing")
    return path.read_bytes()


def _require_format_bytes(data: bytes) -> None:
    if data != FORMAT_BYTES:
        raise FormatError("FORMAT.json is not the exact format-2 canonical document")
    if content_digest(data) != FORMAT_DIGEST:
        raise FormatError("FORMAT.json digest mismatch")


def create_store(root: Path) -> EvidenceStore:
    """Create a format-2 Evidence Store at *root* (FORMAT written once, D1 then root fsync)."""

    root.mkdir(parents=True, exist_ok=True)
    store = EvidenceStore(root)
    tmp = store._tmp_dir()
    if not tmp.exists():
        os.mkdir(tmp)
        store._record("mkdir", tmp)
        store._fsync_dir(root)
    try:
        store._install_file(root / "FORMAT.json", FORMAT_BYTES)
    except FileExistsError as exc:
        raise FormatError("FORMAT.json already exists") from exc
    store._fsync_dir(root)
    return store


def open_store(root: Path) -> EvidenceStore:
    """Open a format-2 root. FORMAT is validated before any mutation, including `.tmp/` purge."""

    data = _read_format(root)
    _require_format_bytes(data)
    store = EvidenceStore(root)
    store._purge_tmp()
    return store
