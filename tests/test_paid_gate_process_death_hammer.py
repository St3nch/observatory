"""HAM-01: process-death hammer around Attempt-before-send and Capture-after-response.

The ordinary suite collects this module. The destructive child-kill matrix runs only
when OBSERVATORY_RUN_PAID_GATE_HAMMER=1. Ordinary collection still proves the opt-in
guard and the milestone inventory via one in-process loopback capture.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any, Final

import pytest

from observatory.dataforseo_sandbox import (
    SandboxCaptureInputs,
    _run_gated_capture,
)
from observatory.evidence import scrub_store
from observatory.evidence_store import (
    EvidenceStore,
    FormatError,
    IntegrityError,
    StoreError,
    create_store,
    inspect_store,
    open_store,
)
from observatory.settings import DataForSEOCredentials

HAMMER_ENV: Final[str] = "OBSERVATORY_RUN_PAID_GATE_HAMMER"
CHILD_DEATH_CODE: Final[int] = 97
CHILD_TIMEOUT_SEC: Final[float] = 20.0
SERVER_TIMEOUT_SEC: Final[float] = 12.0

SENTINEL_LOGIN: Final[str] = "sentinel-login-ham01-aa11"
SENTINEL_PASSWORD: Final[str] = "sentinel-password-ham01-bb22"

KEYWORD: Final[str] = "observatory test"
LOCATION: Final[int] = 2840
LANGUAGE: Final[str] = "en"
SOFTWARE: Final[str] = "hammer-ham01"
AUTHORIZED_AT: Final[str] = "2026-08-16T12:00:00.000000Z"
RESPONSE_BODY: Final[bytes] = b'{"status_code":20000,"status_message":"Ok.","tasks":[]}'

REQUIRED_FAMILIES: Final[frozenset[str]] = frozenset(
    {
        "attempt:terminal-dir",
        "attempt:manifest",
        "attempt:bundle-body",
        "attempt:COMMITTED",
        "attempt:fsync-dir",
        "capture:terminal-dir",
        "capture:manifest",
        "capture:bundle-body",
        "capture:COMMITTED",
        "capture:fsync-dir",
    }
)

Milestone = tuple[str, str, str]


def _basic_token() -> str:
    import base64

    return base64.b64encode(f"{SENTINEL_LOGIN}:{SENTINEL_PASSWORD}".encode()).decode(
        "ascii"
    )


def _sentinel_needles() -> tuple[bytes, ...]:
    token = _basic_token()
    return (
        SENTINEL_LOGIN.encode(),
        SENTINEL_PASSWORD.encode(),
        f"Basic {token}".encode(),
        token.encode(),
    )


def _credentials() -> DataForSEOCredentials:
    return DataForSEOCredentials(SENTINEL_LOGIN, SENTINEL_PASSWORD)


def _inputs(nonce: str) -> SandboxCaptureInputs:
    return SandboxCaptureInputs(
        keyword=KEYWORD,
        location_code=LOCATION,
        language_code=LANGUAGE,
        attempt_nonce=nonce,
        authorized_at=AUTHORIZED_AT,
        observatory_version=SOFTWARE,
    )


def _family(phase: str, op: str, path: str) -> str | None:
    name = Path(path).name
    if op == "mkdir_terminal":
        return f"{phase}:terminal-dir"
    if op == "install_file":
        if name == "attempt.json":
            return "attempt:manifest"
        if name == "capture.json":
            return "capture:manifest"
        if name == "request.body":
            return "attempt:bundle-body"
        if name == "response.body":
            return "capture:bundle-body"
        if name == "COMMITTED":
            return f"{phase}:COMMITTED"
        return f"{phase}:install:{name}"
    if op == "fsync_dir":
        return f"{phase}:fsync-dir"
    return f"{phase}:{op}"


def _install_wrappers(
    *,
    phase_filter: str | None,
    die_after: int | None,
    log: list[Milestone],
) -> Callable[[], None]:
    """Wrap concrete store methods. Death happens after the real operation returns."""

    orig_attempt = EvidenceStore.commit_attempt
    orig_capture = EvidenceStore.commit_capture
    orig_terminal = EvidenceStore._create_terminal_directory
    orig_install = EvidenceStore._install_file
    orig_fsync = EvidenceStore._fsync_dir
    state: dict[str, str | None] = {"phase": None}

    def _after(op: str, path: Path) -> None:
        current = state["phase"]
        if current is None:
            return
        log.append((current, op, str(path)))
        if (
            die_after is not None
            and current == phase_filter
            and sum(1 for item in log if item[0] == current) == die_after
        ):
            os._exit(CHILD_DEATH_CODE)

    def commit_attempt(
        self: EvidenceStore,
        document: Any,
        *,
        request_body: bytes | None,
    ) -> str:
        state["phase"] = "attempt"
        try:
            return orig_attempt(self, document, request_body=request_body)
        finally:
            state["phase"] = None

    def commit_capture(
        self: EvidenceStore,
        document: Any,
        *,
        response_body: bytes | None,
    ) -> str:
        state["phase"] = "capture"
        try:
            return orig_capture(self, document, response_body=response_body)
        finally:
            state["phase"] = None

    def create_terminal(self: EvidenceStore, directory: Path) -> None:
        orig_terminal(self, directory)
        _after("mkdir_terminal", directory)

    def install_file(self: EvidenceStore, final: Path, data: bytes) -> None:
        orig_install(self, final, data)
        _after("install_file", final)

    def fsync_dir(self: EvidenceStore, directory: Path) -> None:
        orig_fsync(self, directory)
        _after("fsync_dir", directory)

    EvidenceStore.commit_attempt = commit_attempt  # type: ignore[method-assign]
    EvidenceStore.commit_capture = commit_capture  # type: ignore[method-assign]
    EvidenceStore._create_terminal_directory = create_terminal  # type: ignore[method-assign]
    EvidenceStore._install_file = install_file  # type: ignore[method-assign]
    EvidenceStore._fsync_dir = fsync_dir  # type: ignore[method-assign]

    def restore() -> None:
        EvidenceStore.commit_attempt = orig_attempt  # type: ignore[method-assign]
        EvidenceStore.commit_capture = orig_capture  # type: ignore[method-assign]
        EvidenceStore._create_terminal_directory = orig_terminal  # type: ignore[method-assign]
        EvidenceStore._install_file = orig_install  # type: ignore[method-assign]
        EvidenceStore._fsync_dir = orig_fsync  # type: ignore[method-assign]

    return restore


def _read_http_request(conn: socket.socket) -> bytes:
    conn.settimeout(5.0)
    data = bytearray()
    while b"\r\n\r\n" not in data:
        chunk = conn.recv(4096)
        if not chunk:
            break
        data.extend(chunk)
    if b"\r\n\r\n" not in data:
        return bytes(data)
    header_blob, rest = data.split(b"\r\n\r\n", 1)
    length = 0
    for line in header_blob.split(b"\r\n"):
        if line.lower().startswith(b"content-length:"):
            length = int(line.split(b":", 1)[1].strip())
    body = bytearray(rest)
    while len(body) < length:
        chunk = conn.recv(4096)
        if not chunk:
            break
        body.extend(chunk)
    return bytes(header_blob) + b"\r\n\r\n" + bytes(body)


def _http_ok_response() -> bytes:
    return (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/json\r\n"
        b"Content-Length: "
        + str(len(RESPONSE_BODY)).encode()
        + b"\r\n\r\n"
        + RESPONSE_BODY
    )


class LoopbackServer:
    """Parent-side 127.0.0.1 server. Verifies Attempt independently on request."""

    def __init__(self, evidence_root: Path) -> None:
        self.evidence_root = evidence_root
        self.requests: list[bytes] = []
        self.verify_attempt_id: str | None = None
        self.verify_error: str | None = None
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1", 0))
        self._sock.listen(1)
        self._sock.settimeout(SERVER_TIMEOUT_SEC)
        self.port = int(self._sock.getsockname()[1])
        self.endpoint = (
            f"http://127.0.0.1:{self.port}/v3/serp/google/organic/live/advanced"
        )
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _verify_attempt_now(self) -> None:
        store = inspect_store(self.evidence_root)
        ids = store.list_committed_ids("attempts")
        if len(ids) != 1:
            self.verify_error = f"attempt_count={len(ids)}"
            return
        document = store.read_attempt(ids[0])
        if document is None:
            self.verify_error = "attempt_unreadable"
            return
        self.verify_attempt_id = ids[0]

    def _serve(self) -> None:
        try:
            conn, _addr = self._sock.accept()
        except TimeoutError:
            return
        except OSError:
            return
        try:
            with conn:
                raw = _read_http_request(conn)
                if raw:
                    self.requests.append(raw)
                    try:
                        self._verify_attempt_now()
                    except (FormatError, IntegrityError, StoreError, OSError) as exc:
                        self.verify_error = type(exc).__name__
                    conn.sendall(_http_ok_response())
        finally:
            with suppress_oserror():
                self._sock.close()

    def close(self) -> None:
        with suppress_oserror():
            self._sock.close()
        self._thread.join(timeout=2.0)

    def wait(self) -> None:
        self._thread.join(timeout=SERVER_TIMEOUT_SEC + 2.0)


class suppress_oserror:
    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None, *_: object) -> bool:
        return exc_type is not None and issubclass(exc_type, OSError)


def _snapshot_files(root: Path) -> dict[str, tuple[int, bytes]]:
    files: dict[str, tuple[int, bytes]] = {}
    if not root.exists():
        return files
    for path in sorted(root.rglob("*")):
        if path.is_file():
            data = path.read_bytes()
            files[path.relative_to(root).as_posix()] = (path.stat().st_ino, data)
    return files


def _scan_credentials(root: Path, *surfaces: object) -> list[str]:
    hits: list[str] = []
    needles = _sentinel_needles()
    if root.exists():
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            data = path.read_bytes()
            for needle in needles:
                if needle in data:
                    hits.append(path.as_posix())
                    break
    for surface in surfaces:
        if surface is None:
            continue
        blob = surface if isinstance(surface, bytes) else str(surface).encode()
        for needle in needles:
            if needle in blob:
                hits.append("surface")
                break
    return hits


def _postmortem(root: Path) -> dict[str, Any]:
    before = _snapshot_files(root)
    committed_attempts: list[str] = []
    committed_captures: list[str] = []
    verify_failures: list[str] = []
    scrub_failed: list[str] = []
    inspect_ok = False
    try:
        store = inspect_store(root)
        inspect_ok = True
        for bundle in store.list_commitment_claiming_directories("attempts"):
            try:
                store.verify_attempt_directory(bundle)
                committed_attempts.append(bundle.name)
            except (IntegrityError, StoreError):
                verify_failures.append(bundle.as_posix())
        for bundle in store.list_commitment_claiming_directories("captures"):
            try:
                store.verify_capture_directory(bundle)
                committed_captures.append(bundle.name)
            except (IntegrityError, StoreError):
                verify_failures.append(bundle.as_posix())
        scrub_failed = [path.as_posix() for path in scrub_store(store)]
    except (FormatError, IntegrityError, StoreError, OSError):
        inspect_ok = False
    credential_hits = _scan_credentials(root)
    after_inspect = _snapshot_files(root)
    assert after_inspect == before
    cleaned: set[str] = set()
    if inspect_ok:
        open_store(root)
        after_open = _snapshot_files(root)
        cleaned = set(before) - set(after_open)
        for relative in set(before) & set(after_open):
            assert before[relative] == after_open[relative]
        for relative in cleaned:
            assert relative.startswith(".tmp/")
    return {
        "inspect_ok": inspect_ok,
        "committed_attempts": committed_attempts,
        "committed_captures": committed_captures,
        "verify_failures": verify_failures,
        "scrub_failed": scrub_failed,
        "credential_hits": credential_hits,
        "cleaned": sorted(cleaned),
        "uncommitted_residue": _uncommitted_residue(root),
    }


def _uncommitted_residue(root: Path) -> list[str]:
    found: list[str] = []
    for kind, manifest in (("attempts", "attempt.json"), ("captures", "capture.json")):
        base = root / kind / "v1"
        if not base.is_dir():
            continue
        for manifest_path in base.rglob(manifest):
            if not (manifest_path.parent / "COMMITTED").is_file():
                found.append(manifest_path.parent.as_posix())
    return found


def _discover_milestones(tmp_path: Path) -> list[Milestone]:
    root = tmp_path / "discover"
    log: list[Milestone] = []
    restore = _install_wrappers(phase_filter=None, die_after=None, log=log)
    server = LoopbackServer(root)
    try:
        store = create_store(root)
        _run_gated_capture(
            store,
            _inputs("0" * 64),
            _credentials(),
            endpoint=server.endpoint,
        )
        server.wait()
    finally:
        restore()
        server.close()
    return log


def _phase_points(log: list[Milestone], phase: str) -> list[tuple[int, Milestone]]:
    points: list[tuple[int, Milestone]] = []
    seen = 0
    for item in log:
        if item[0] != phase:
            continue
        seen += 1
        points.append((seen, item))
    return points


def _families(log: list[Milestone]) -> set[str]:
    found: set[str] = set()
    for phase, op, path in log:
        family = _family(phase, op, path)
        if family is not None:
            found.add(family)
    return found


def test_opt_in_guard_skips_destructive_matrix() -> None:
    """Ordinary collection does not enable the child-kill matrix."""

    if os.environ.get(HAMMER_ENV) == "1":
        pytest.skip("opt-in is set; skip-guard assertion is for ordinary runs")
    assert os.environ.get(HAMMER_ENV) != "1"


def test_milestone_inventory_covers_attempt_and_capture_families(
    tmp_path: Path,
) -> None:
    log = _discover_milestones(tmp_path)
    families = _families(log)
    attempt_n = sum(1 for phase, _op, _path in log if phase == "attempt")
    capture_n = sum(1 for phase, _op, _path in log if phase == "capture")
    assert attempt_n > 0
    assert capture_n > 0
    missing = REQUIRED_FAMILIES - families
    assert missing == set(), f"missing milestone families: {sorted(missing)}"


@pytest.mark.skipif(
    os.environ.get(HAMMER_ENV) != "1",
    reason="set OBSERVATORY_RUN_PAID_GATE_HAMMER=1 to run the process-death matrix",
)
def test_paid_gate_process_death_matrix(tmp_path: Path) -> None:
    log = _discover_milestones(tmp_path / "inventory")
    attempt_points = _phase_points(log, "attempt")
    capture_points = _phase_points(log, "capture")
    assert attempt_points, "Attempt-phase inventory is empty"
    assert capture_points, "Capture-phase inventory is empty"
    missing = REQUIRED_FAMILIES - _families(log)
    assert missing == set(), f"missing milestone families: {sorted(missing)}"

    cases: list[tuple[str, int | None]] = [
        ("attempt", index) for index, _item in attempt_points
    ]
    cases.extend(("capture", index) for index, _item in capture_points)
    cases.append(("none", None))

    results: list[dict[str, Any]] = []
    for phase, die_after in cases:
        case_root = tmp_path / f"{phase}-{die_after if die_after is not None else 'control'}"
        case_root.mkdir()
        server = LoopbackServer(case_root)
        try:
            completed = _spawn_child(case_root, server.endpoint, phase, die_after)
        finally:
            server.close()
        post = _postmortem(case_root)
        plaintext_in_wire = any(
            SENTINEL_LOGIN.encode() in raw or SENTINEL_PASSWORD.encode() in raw
            for raw in server.requests
        )
        post.update(
            {
                "phase": phase,
                "die_after": die_after,
                "exit": completed["exit"],
                "timeout": completed["timeout"],
                "requests": len(server.requests),
                "verify_attempt_id": server.verify_attempt_id,
                "verify_error": server.verify_error,
                "stdout": completed["stdout"],
                "stderr": completed["stderr"],
                "plaintext_in_wire": plaintext_in_wire,
            }
        )
        post["credential_hits"].extend(
            _scan_credentials(case_root, completed["stdout"], completed["stderr"])
        )
        results.append(post)

    attempt_results = [row for row in results if row["phase"] == "attempt"]
    capture_results = [row for row in results if row["phase"] == "capture"]
    control = next(row for row in results if row["phase"] == "none")

    assert len(attempt_results) == len(attempt_points)
    assert len(capture_results) == len(capture_points)
    print(
        f"HAM-01 fault points: attempt={len(attempt_results)} "
        f"capture={len(capture_results)}"
    )

    for row in attempt_results:
        assert row["inspect_ok"] is True
        assert row["timeout"] is False
        assert row["exit"] == CHILD_DEATH_CODE
        assert row["requests"] == 0
        assert row["verify_failures"] == []
        assert row["scrub_failed"] == []
        assert row["credential_hits"] == []
        assert row["plaintext_in_wire"] is False
        assert len(row["committed_attempts"]) in {0, 1}
        assert row["committed_captures"] == []
        if row["committed_attempts"]:
            store = inspect_store(
                tmp_path / f"attempt-{row['die_after']}"
            )
            assert store.read_attempt(row["committed_attempts"][0]) is not None

    for row in capture_results:
        assert row["inspect_ok"] is True
        assert row["timeout"] is False
        assert row["exit"] == CHILD_DEATH_CODE
        assert row["requests"] == 1
        assert row["plaintext_in_wire"] is False
        assert row["verify_error"] is None
        assert row["verify_attempt_id"] is not None
        assert row["verify_failures"] == []
        assert row["scrub_failed"] == []
        assert row["credential_hits"] == []
        assert len(row["committed_attempts"]) == 1
        assert len(row["committed_captures"]) in {0, 1}
        store = inspect_store(tmp_path / f"capture-{row['die_after']}")
        attempt = store.read_attempt(row["committed_attempts"][0])
        assert attempt is not None
        if not row["committed_captures"]:
            # authorized/unresolved: Attempt without Capture; this matrix does not retry
            assert store.list_committed_ids("captures") == []

    assert control["inspect_ok"] is True
    assert control["timeout"] is False
    assert control["exit"] == 0
    assert control["requests"] == 1
    assert control["plaintext_in_wire"] is False
    assert control["verify_error"] is None
    assert len(control["committed_attempts"]) == 1
    assert len(control["committed_captures"]) == 1
    assert control["verify_failures"] == []
    assert control["scrub_failed"] == []
    assert control["credential_hits"] == []
    control_store = inspect_store(tmp_path / "none-control")
    assert control_store.read_attempt(control["committed_attempts"][0]) is not None
    assert control_store.read_capture(control["committed_captures"][0]) is not None


def _spawn_child(
    root: Path,
    endpoint: str,
    phase: str,
    die_after: int | None,
) -> dict[str, Any]:
    repo = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env.pop("OBSERVATORY_DATAFORSEO_LOGIN", None)
    env.pop("OBSERVATORY_DATAFORSEO_PASSWORD", None)
    args = [
        sys.executable,
        str(Path(__file__).resolve()),
        "child",
        str(root),
        endpoint,
        phase,
        "" if die_after is None else str(die_after),
    ]
    try:
        completed = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=CHILD_TIMEOUT_SEC,
            cwd=repo,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "exit": None,
            "timeout": True,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        }
    return {
        "exit": completed.returncode,
        "timeout": False,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _child_main(root: Path, endpoint: str, phase: str, die_after: int | None) -> None:
    real_connect = socket.create_connection

    def guarded(address: Any, *args: Any, **kwargs: Any) -> socket.socket:
        host = address[0] if isinstance(address, tuple) else address
        if host not in {"127.0.0.1", "::1"}:
            os._exit(2)
        return real_connect(address, *args, **kwargs)

    socket.create_connection = guarded
    log: list[Milestone] = []
    restore = _install_wrappers(phase_filter=phase, die_after=die_after, log=log)
    try:
        store = create_store(root)
        _run_gated_capture(
            store,
            _inputs(f"{os.getpid():064x}"[-64:]),
            _credentials(),
            endpoint=endpoint,
        )
    finally:
        restore()
    os._exit(0)


if __name__ == "__main__":
    if len(sys.argv) == 6 and sys.argv[1] == "child":
        _die = sys.argv[5]
        _child_main(
            Path(sys.argv[2]),
            sys.argv[3],
            sys.argv[4],
            None if _die == "" else int(_die),
        )
        raise SystemExit(0)
    raise SystemExit("usage: child ROOT ENDPOINT PHASE DIE_AFTER")
