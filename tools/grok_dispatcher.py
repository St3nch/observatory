"""Headless Grok Build dispatcher bootstrap (OPS-03). Development orchestration only."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import stat
import subprocess
import sys
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, Protocol, TextIO

CANONICAL_REPO_ROOT = Path("/home/chaz/projects/vedaops/observatory")
CANONICAL_ORIGIN = "ssh://github.com/St3nch/observatory.git"
EQUIVALENT_ORIGINS = frozenset(
    {
        "ssh://github.com/St3nch/observatory.git",
        "ssh://github.com/St3nch/observatory",
        "git@github.com:St3nch/observatory.git",
        "git@github.com:St3nch/observatory",
    }
)
DISPATCHER_HOME = Path.home() / ".local/share/vedaops/observatory/dispatcher"
CHILD_TIMEOUT_SECONDS = 7200
MAX_INSTRUCTION_BYTES = 8192
PRODUCTION_GROK_EXECUTABLE = "grok"

FORBIDDEN_GIT_VERBS = frozenset(
    {
        "push",
        "merge",
        "rebase",
        "reset",
        "clean",
        "pull",
        "fetch",
        "clone",
        "ls-remote",
    }
)
SUCCESS_STOP_REASONS = frozenset({"endturn"})
CANCELLED_STOP_REASONS = frozenset({"cancelled", "canceled"})
SECRET_ENV_MARKERS: tuple[str, ...] = (
    "API_KEY",
    "TOKEN",
    "SECRET",
    "PASSWORD",
    "AUTHORIZATION",
    "CREDENTIAL",
    "DATAFORSEO",
    "GH_TOKEN",
    "GITHUB_TOKEN",
    "XAI_API_KEY",
)
_SECRET_PATH_PATTERNS: tuple[str, ...] = (
    "~/.grok/auth.json",
    ".env",
    "**/.env",
    "**/*secret*",
    "**/*credential*",
    "**/*.pem",
    "**/*.key",
)
STATE_FIELDS = (
    "ticket",
    "start_commit",
    "branch",
    "worktree",
    "writer",
    "session_id",
    "child_pid",
    "state",
    "implementation_commit",
    "grok_exit_code",
    "stop_reason",
    "started_at",
    "updated_at",
    "diagnostic",
)
SECRET_FIELD_MARKERS = ("password", "token", "secret", "api_key", "authorization", "credential")
DENY_RULES: tuple[str, ...] = (
    "Bash(git push *)",
    "Bash(git merge *)",
    "Bash(git rebase *)",
    "Bash(git reset *)",
    "Bash(git clean *)",
    "Bash(git pull *)",
    "Bash(git fetch *)",
    "Bash(git clone *)",
    "Bash(git ls-remote *)",
    "Bash(git checkout main)",
    "Bash(git switch main)",
    "Bash(rm *)",
    "Bash(rm -rf *)",
    "Bash(dd *)",
    "Bash(mkfs *)",
    "Bash(ssh *)",
    "Bash(scp *)",
    "Bash(sudo *)",
    "Bash(gh *)",
    "Bash(curl *)",
    "Bash(wget *)",
    "WebFetch",
    "WebFetch(*)",
    "WebSearch",
    "WebSearch(*)",
    "MCP",
    *tuple(
        f"{action}({pattern})"
        for pattern in _SECRET_PATH_PATTERNS
        for action in ("Read", "Edit", "Write")
    ),
)
FORBIDDEN_ARGV_FLAGS = frozenset(
    {
        "--worktree",
        "--ref",
        "--worktree-ref",
        "--continue",
        "--session-id",
        "--fork-session",
        "--permission-mode",
    }
)
_ACCEPTED_STATUS = re.compile(r"(?m)^\*\*Status:\*\*\s*accepted\s*$")
_REVIEW_STATUS = re.compile(r"(?m)^\*\*Status:\*\*\s*review\s*$")
_DONE_STATUS = re.compile(r"(?m)^\*\*Status:\*\*\s*done\s*$")
_START_COMMIT_FIELD = re.compile(r"(?m)^\*\*Start commit:\*\*\s*(\S+)\s*$")
_SHA = re.compile(r"^[0-9a-fA-F]{40}$")
_REDACT_ASSIGNMENT = re.compile(
    r"(?i)((?:xai_api_key|api[_-]?key|token|secret|password|authorization|bearer|"
    r"dataforseo[^\s=]*)[\"']?\s*[:=]\s*)\S+"
)
_REDACT_SK = re.compile(r"sk-[A-Za-z0-9]{8,}")

class GrokRunner(Protocol):
    def __call__(
        self,
        argv: Sequence[str],
        cwd: str,
        timeout: int,
        record_pid: Callable[[int], None],
    ) -> GrokChildResult: ...


class DispatcherError(Exception):
    """Fail-closed operator-visible dispatcher refusal or run failure."""


@dataclass(frozen=True)
class DispatcherPaths:
    canonical_repo_root: Path
    canonical_origin: str
    dispatcher_home: Path

    @classmethod
    def production(cls) -> DispatcherPaths:
        return cls(
            canonical_repo_root=CANONICAL_REPO_ROOT,
            canonical_origin=CANONICAL_ORIGIN,
            dispatcher_home=DISPATCHER_HOME,
        )

    @property
    def worktrees(self) -> Path:
        return self.dispatcher_home / "worktrees"

    @property
    def state_dir(self) -> Path:
        return self.dispatcher_home / "state"

    @property
    def lock_dir(self) -> Path:
        return self.dispatcher_home / "locks"

    @property
    def log_dir(self) -> Path:
        return self.dispatcher_home / "logs"


@dataclass(frozen=True)
class DispatchRequest:
    repo_root: Path
    ticket: str
    start_commit: str
    mode: Literal["implement", "resume"]
    writer: str
    instruction: str | None = None


@dataclass(frozen=True)
class GrokChildResult:
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False
    pid: int | None = None


@dataclass(frozen=True)
class DispatchResult:
    child_completed: bool
    run_state: str
    ticket: str
    start_commit: str
    writer: str
    session_id: str | None
    worktree: str | None
    branch: str | None
    implementation_commit: str | None
    grok_exit_code: int | None
    stop_reason: str | None
    diagnostic: str


def origin_is_observatory(url: str) -> bool:
    return url.strip().rstrip("/") in EQUIVALENT_ORIGINS


def is_secret_env_name(name: str) -> bool:
    upper = name.upper()
    return any(marker in upper for marker in SECRET_ENV_MARKERS)


def child_environment(source: Mapping[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if source is None else source)
    for key in list(env):
        if is_secret_env_name(key):
            del env[key]
    return env


def forbidden_git_reason(args: Sequence[str]) -> str | None:
    if not args:
        return "empty git command"
    verb = args[0]
    if verb in FORBIDDEN_GIT_VERBS:
        return f"dispatcher refuses git {verb}"
    if verb in {"checkout", "switch"} and "main" in args[1:]:
        return "dispatcher refuses checkout/switch to main"
    return None


def redact_secrets(text: str) -> str:
    redacted = _REDACT_ASSIGNMENT.sub(r"\1[redacted]", text)
    return _REDACT_SK.sub("[redacted]", redacted)


def ticket_id_for(ticket: str) -> str:
    return Path(_normalize_ticket(ticket)).stem


def build_writer_prompt(ticket: str, start_commit: str) -> str:
    return "\n".join(
        [
            f"Act as the sole [GROK] Writer for accepted Observatory ticket {ticket}.",
            f"Exact Steward start commit is {start_commit} and the isolated branch/worktree",
            "is already created from that exact commit.",
            "Read AGENTS.md and authority in required AGENTS.md order, then the accepted ticket.",
            "Load only approved project-local skills needed for implementation and report the",
            "absolute SKILL.md paths of those project-local skills.",
            "Implement the ticket exactly as accepted. Follow the ticket changed-path allowlist.",
            "One Writer only. Do not widen authority. Do not modify authority files,",
            "other tickets,",
            "src/observatory, migrations, provider adapters, Evidence, API, pyproject.toml,",
            ".gitignore, CI, or GitHub workflow files unless the ticket changed-path allowlist",
            "explicitly names them.",
            "Do not make provider, DNS, credential, DataForSEO, production PostgreSQL, GitHub",
            "network, push, merge, or spend activity unless the ticket separately authorizes it.",
            "Do not invoke real Grok/xAI from tests; inject/fake the child boundary when required.",
            "Run ticket-scoped checks required by the ticket. Do not run the repository-wide final",
            "suite; CHAZ owns that final validation.",
            "Finish with exactly one reviewable implementation commit on this branch.",
            "Set ticket Status=review, never done. Record the exact start commit and a candid",
            "Implementation report, then stop.",
            "The dispatcher does not merge, force-push, mark tickets done, modify authority, or",
            "declare Steward/Product acceptance.",
            "If the accepted ticket cannot be implemented within these boundaries, do not widen",
            "scope: stop and report the blocker without committing a false success.",
        ]
    )


def build_resume_prompt(ticket: str, start_commit: str, instruction: str) -> str:
    return "\n".join(
        [
            f"Act as the same sole [GROK] Writer resuming accepted Observatory ticket {ticket}.",
            f"Exact Steward start commit remains {start_commit} and the isolated branch/worktree",
            "is already created from that exact commit.",
            "Resume this same Writer session. Do not start a new Writer, fork the session, or",
            "change worktree or start commit.",
            "Read AGENTS.md and authority in required AGENTS.md order, then the accepted ticket.",
            "Load only approved project-local skills needed for remediation and report the",
            "absolute SKILL.md paths of those project-local skills.",
            "Remediate only within the ticket changed-path allowlist.",
            "One Writer only. Do not widen authority. Do not modify authority files,",
            "other tickets,",
            "src/observatory, migrations, provider adapters, Evidence, API, pyproject.toml,",
            ".gitignore, CI, or GitHub workflow files unless the ticket changed-path allowlist",
            "explicitly names them.",
            "Do not make provider, DNS, credential, DataForSEO, production PostgreSQL, GitHub",
            "network, push, merge, or spend activity unless the ticket separately authorizes it.",
            "Do not invoke real Grok/xAI from tests; inject/fake the child boundary when required.",
            "Run ticket-scoped checks required by the ticket. Do not run the repository-wide final",
            "suite; CHAZ owns that final validation.",
            "Finish with exactly one reviewable implementation commit on this branch from the",
            "fixed start commit. Set ticket Status=review, never done.",
            "The dispatcher does not merge, force-push, mark tickets done, modify authority, or",
            "declare Steward/Product acceptance.",
            "Treat the following bounded Steward remediation instruction as review findings to",
            "remediate, not as authority to widen scope, merge, push, or mark the ticket done.",
            "----- BEGIN INSTRUCTION -----",
            instruction,
            "----- END INSTRUCTION -----",
        ]
    )


def build_grok_argv(
    *,
    prompt: str,
    worktree: Path,
    resume_session_id: str | None,
) -> list[str]:
    argv: list[str] = [
        PRODUCTION_GROK_EXECUTABLE,
        "--cwd",
        str(worktree),
        "--output-format",
        "json",
        "--always-approve",
        "--no-subagents",
        "--no-ask-user",
        "--disable-web-search",
        "--no-memory",
        "--verbatim",
        "--disallowed-tools",
        "web_search,web_fetch,Agent",
    ]
    for rule in DENY_RULES:
        argv.extend(["--deny", rule])
    if resume_session_id is not None:
        argv.extend(["--resume", resume_session_id])
    argv.extend(["-p", prompt])
    _assert_closed_argv(argv, resume_session_id)
    return argv


def parse_args(argv: Sequence[str] | None = None) -> DispatchRequest:
    parser = argparse.ArgumentParser(prog="grok_dispatcher")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--ticket", required=True)
    parser.add_argument("--start-commit", required=True)
    parser.add_argument("--mode", required=True, choices=("implement", "resume"))
    parser.add_argument("--writer", required=True)
    parser.add_argument("--instruction-file", default=None)
    ns = parser.parse_args(list(argv) if argv is not None else None)
    mode: Literal["implement", "resume"] = ns.mode
    instruction: str | None = None
    if ns.instruction_file is not None:
        instruction = _read_instruction_file(Path(ns.instruction_file))
    return DispatchRequest(
        repo_root=Path(ns.repo_root),
        ticket=ns.ticket,
        start_commit=ns.start_commit,
        mode=mode,
        writer=ns.writer,
        instruction=instruction,
    )


def dispatch(
    request: DispatchRequest,
    *,
    grok_runner: GrokRunner,
    paths: DispatcherPaths,
) -> DispatchResult:
    ticket = _normalize_ticket(request.ticket)
    start = _normalize_sha(request.start_commit)
    writer = request.writer.strip()
    if writer == "":
        raise DispatcherError("writer identity is required")
    if request.instruction is not None and request.mode == "implement":
        raise DispatcherError("implement refuses a remediation instruction")
    if request.instruction is not None and request.instruction.strip() == "":
        raise DispatcherError("resume instruction is empty")
    repo = _require_observatory_repo(request.repo_root, paths)
    _require_clean_primary(repo)
    _require_commit(repo, start)
    _require_accepted_ticket(repo, start, ticket)
    ticket_id = Path(ticket).stem
    with _ticket_lock(paths, ticket_id):
        if request.mode == "implement":
            return _implement(
                request=DispatchRequest(
                    repo_root=repo,
                    ticket=ticket,
                    start_commit=start,
                    mode="implement",
                    writer=writer,
                    instruction=None,
                ),
                grok_runner=grok_runner,
                paths=paths,
                ticket_id=ticket_id,
            )
        return _resume(
            request=DispatchRequest(
                repo_root=repo,
                ticket=ticket,
                start_commit=start,
                mode="resume",
                writer=writer,
                instruction=request.instruction,
            ),
            grok_runner=grok_runner,
            paths=paths,
            ticket_id=ticket_id,
        )


def invoke_real_grok(
    argv: Sequence[str],
    cwd: str,
    timeout: int,
    record_pid: Callable[[int], None],
) -> GrokChildResult:
    if not argv or argv[0] != PRODUCTION_GROK_EXECUTABLE:
        raise DispatcherError("refusing to invoke a non-grok child executable")
    proc = subprocess.Popen(
        list(argv),
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=child_environment(),
    )
    record_pid(proc.pid)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        return GrokChildResult(
            exit_code=proc.returncode if proc.returncode is not None else 124,
            stdout=stdout or "",
            stderr=stderr or "",
            timed_out=True,
            pid=proc.pid,
        )
    return GrokChildResult(
        exit_code=0 if proc.returncode is None else proc.returncode,
        stdout=stdout or "",
        stderr=stderr or "",
        timed_out=False,
        pid=proc.pid,
    )


def main(
    argv: Sequence[str] | None = None,
    *,
    grok_runner: GrokRunner | None = None,
    paths: DispatcherPaths | None = None,
) -> int:
    try:
        request = parse_args(argv)
        result = dispatch(
            request,
            grok_runner=grok_runner or invoke_real_grok,
            paths=paths or DispatcherPaths.production(),
        )
    except DispatcherError as exc:
        print(f"dispatcher: {exc}", file=sys.stderr)
        return 1
    payload = {
        "child_completed": result.child_completed,
        "run_state": result.run_state,
        "ticket": result.ticket,
        "start_commit": result.start_commit,
        "writer": result.writer,
        "session_id": result.session_id,
        "worktree": result.worktree,
        "branch": result.branch,
        "implementation_commit": result.implementation_commit,
        "grok_exit_code": result.grok_exit_code,
        "stop_reason": result.stop_reason,
        "diagnostic": result.diagnostic,
    }
    print(json.dumps(payload, sort_keys=True))
    return 0 if result.child_completed else 1


def _normalize_ticket(ticket: str) -> str:
    raw = ticket.strip().replace("\\", "/")
    if raw.startswith("/") or ".." in Path(raw).parts:
        raise DispatcherError("ticket path must be a repository-relative tickets/ path")
    normalized = raw.lstrip("./")
    parts = Path(normalized).parts
    if len(parts) != 2 or parts[0] != "tickets" or not parts[1].endswith(".md"):
        raise DispatcherError("ticket path must be tickets/<file>.md")
    return f"tickets/{parts[1]}"


def _normalize_sha(value: str) -> str:
    sha = value.strip().lower()
    if _SHA.fullmatch(sha) is None:
        raise DispatcherError("start commit must be a 40-hex SHA-1")
    return sha


def _require_observatory_repo(repo_root: Path, paths: DispatcherPaths) -> Path:
    repo = repo_root.resolve()
    if repo != paths.canonical_repo_root.resolve():
        raise DispatcherError("repository identity is not Observatory")
    toplevel = _run_git(repo, ["rev-parse", "--show-toplevel"])
    if toplevel.returncode != 0:
        raise DispatcherError("repository identity is not Observatory")
    if Path(toplevel.stdout.strip()).resolve() != paths.canonical_repo_root.resolve():
        raise DispatcherError("repository identity is not Observatory")
    origin = _run_git(repo, ["remote", "get-url", "origin"])
    if origin.returncode != 0 or not origin_is_observatory(origin.stdout.strip()):
        raise DispatcherError("repository identity is not Observatory")
    if not origin_is_observatory(paths.canonical_origin):
        raise DispatcherError("repository identity is not Observatory")
    return repo


def _require_clean_primary(repo: Path) -> None:
    status = _run_git(repo, ["status", "--porcelain"])
    if status.returncode != 0:
        raise DispatcherError("unable to read primary checkout status")
    if status.stdout.strip() != "":
        raise DispatcherError("primary checkout is dirty")


def _require_commit(repo: Path, sha: str) -> None:
    result = _run_git(repo, ["cat-file", "-t", sha])
    if result.returncode != 0 or result.stdout.strip() != "commit":
        raise DispatcherError(f"start commit {sha} does not exist")


def _require_accepted_ticket(repo: Path, sha: str, ticket: str) -> str:
    result = _run_git(repo, ["show", f"{sha}:{ticket}"])
    if result.returncode != 0:
        raise DispatcherError(f"ticket {ticket} does not exist at {sha}")
    body = result.stdout
    if _ACCEPTED_STATUS.search(body) is None:
        raise DispatcherError(f"ticket {ticket} is not accepted at {sha}")
    return body


def _run_git(repo: Path, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    reason = forbidden_git_reason(args)
    if reason is not None:
        raise DispatcherError(reason)
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )


@contextmanager
def _ticket_lock(paths: DispatcherPaths, ticket_id: str) -> Iterator[None]:
    paths.lock_dir.mkdir(parents=True, exist_ok=True)
    handle: TextIO = (paths.lock_dir / f"{ticket_id}.lock").open("a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        handle.close()
        raise DispatcherError(f"active Writer already owns ticket {ticket_id}") from exc
    try:
        yield
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def _state_path(paths: DispatcherPaths, ticket_id: str) -> Path:
    return paths.state_dir / f"{ticket_id}.json"


def _load_state(paths: DispatcherPaths, ticket_id: str) -> dict[str, object] | None:
    path = _state_path(paths, ticket_id)
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DispatcherError(f"run state for {ticket_id} is unreadable") from exc
    if not isinstance(payload, dict):
        raise DispatcherError(f"run state for {ticket_id} is unreadable")
    return payload


def _write_state(paths: DispatcherPaths, ticket_id: str, payload: Mapping[str, object]) -> None:
    for key in payload:
        lowered = str(key).lower()
        if any(marker in lowered for marker in SECRET_FIELD_MARKERS):
            raise DispatcherError(f"refusing to persist secret-like state field {key}")
    closed = {field: payload.get(field) for field in STATE_FIELDS}
    diagnostic = closed.get("diagnostic")
    if isinstance(diagnostic, str):
        closed["diagnostic"] = redact_secrets(diagnostic)[:500]
    paths.state_dir.mkdir(parents=True, exist_ok=True)
    path = _state_path(paths, ticket_id)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(closed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def _write_log(paths: DispatcherPaths, ticket_id: str, payload: Mapping[str, object]) -> None:
    redacted = {key: _redact_value(value) for key, value in payload.items()}
    directory = paths.log_dir / ticket_id
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    path = directory / f"{stamp}.json"
    path.write_text(json.dumps(redacted, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _redact_value(value: object) -> object:
    if isinstance(value, str):
        return redact_secrets(value)
    return value


def _pid_alive(pid: object) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _read_instruction_file(path: Path) -> str:
    try:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
    except FileNotFoundError as exc:
        raise DispatcherError("instruction file does not exist") from exc
    except OSError as exc:
        raise DispatcherError("instruction file is unreadable") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise DispatcherError("instruction file must be a regular file")
        if info.st_size > MAX_INSTRUCTION_BYTES:
            raise DispatcherError(
                f"instruction file exceeds {MAX_INSTRUCTION_BYTES} bytes"
            )
        raw = os.read(fd, MAX_INSTRUCTION_BYTES + 1)
    finally:
        os.close(fd)
    if len(raw) > MAX_INSTRUCTION_BYTES:
        raise DispatcherError(f"instruction file exceeds {MAX_INSTRUCTION_BYTES} bytes")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DispatcherError("instruction file must be UTF-8") from exc
    if "\x00" in text:
        raise DispatcherError("instruction file contains a NUL byte")
    if any(ord(char) < 32 and char not in "\t\n\r" for char in text):
        raise DispatcherError("instruction file contains a control character")
    stripped = text.strip()
    if stripped == "":
        raise DispatcherError("resume instruction is empty")
    return stripped


def _assert_closed_argv(argv: Sequence[str], resume_session_id: str | None) -> None:
    if argv[0] != PRODUCTION_GROK_EXECUTABLE:
        raise DispatcherError("child argv must start with grok")
    if "--always-approve" not in argv:
        raise DispatcherError("child argv must pass --always-approve")
    if "dontAsk" in argv:
        raise DispatcherError("child argv must not use dontAsk")
    for flag in FORBIDDEN_ARGV_FLAGS:
        if flag in argv:
            raise DispatcherError(f"child argv must not include {flag}")
    if resume_session_id is None and "--resume" in argv:
        raise DispatcherError("implement argv must not resume a session")
    if resume_session_id is not None:
        try:
            index = list(argv).index("--resume")
        except ValueError as exc:
            raise DispatcherError("resume argv must include --resume") from exc
        if index + 1 >= len(argv) or argv[index + 1] != resume_session_id:
            raise DispatcherError("resume argv must reuse the recorded session id")


def _parse_grok_json(stdout: str) -> dict[str, object]:
    text = stdout.strip()
    candidates = [text]
    for line in reversed(text.splitlines()):
        stripped = line.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            candidates.append(stripped)
            break
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start : end + 1])
    for raw in candidates:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return {}


def _session_id_from(payload: Mapping[str, object]) -> str | None:
    for key in ("sessionId", "session_id"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip() != "":
            return value.strip()
    return None


def _stop_reason_from(payload: Mapping[str, object]) -> str | None:
    for key in ("stopReason", "stop_reason"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip() != "":
            return value.strip()
    return None


def _normalize_stop_reason(value: str) -> str:
    return "".join(ch for ch in value.strip().lower() if ch.isalnum())


def _classify_run(
    child: GrokChildResult,
    payload: Mapping[str, object],
    stop_reason: str | None,
) -> tuple[bool, str, str]:
    if child.timed_out:
        return False, "interrupted", "Grok child timed out after 7200 seconds"
    blob = f"{child.stdout}\n{child.stderr}".lower()
    if child.exit_code != 0 and "auth" in blob and any(
        token in blob for token in ("expir", "unauthor", "unauthenticated", "login")
    ):
        return False, "failed", "Grok authentication failed"
    if child.exit_code in {130, 143}:
        return False, "interrupted", f"Grok child interrupted (exit {child.exit_code})"
    if child.exit_code != 0:
        return False, "failed", f"Grok child failed (exit {child.exit_code})"
    if payload.get("is_error") is True:
        return False, "failed", "Grok JSON result is_error=true"
    if stop_reason is None:
        return False, "failed", "Grok JSON result omitted stopReason"
    normalized = _normalize_stop_reason(stop_reason)
    if normalized in CANCELLED_STOP_REASONS:
        return False, "cancelled", 'Grok JSON stopReason="cancelled" is not success'
    if normalized in SUCCESS_STOP_REASONS:
        return True, "completed", "Grok child completed with a successful stop reason"
    return False, "failed", f"Grok JSON stopReason={stop_reason!r} is not success"


def _worktree_path(paths: DispatcherPaths, ticket_id: str) -> Path:
    return (paths.worktrees / ticket_id).resolve()


def _branch_name(ticket_id: str) -> str:
    return f"dispatcher/{ticket_id}"


def _refuse_if_active(state: Mapping[str, object] | None, ticket_id: str) -> None:
    if state is None:
        return
    if state.get("state") == "running":
        raise DispatcherError(f"ticket {ticket_id} already has a running Writer")
    if _pid_alive(state.get("child_pid")):
        raise DispatcherError(f"ticket {ticket_id} already has a live Writer process")


def _refuse_foreign_worktree(
    paths: DispatcherPaths,
    ticket_id: str,
    worktree: Path,
    branch: str,
) -> None:
    if not paths.state_dir.is_dir():
        return
    for path in paths.state_dir.glob("*.json"):
        if path.stem == ticket_id:
            continue
        other = _load_state(paths, path.stem)
        if other is None:
            continue
        live = other.get("state") == "running" or _pid_alive(other.get("child_pid"))
        if not live:
            continue
        other_tree = other.get("worktree")
        other_branch = other.get("branch")
        if other_tree == str(worktree) or other_branch == branch:
            raise DispatcherError("requested branch/worktree is another ticket's live worktree")


def _head_sha(repo: Path) -> str | None:
    result = _run_git(repo, ["rev-parse", "HEAD"])
    if result.returncode != 0:
        return None
    sha = result.stdout.strip().lower()
    if _SHA.fullmatch(sha) is None:
        return None
    return sha


def _current_branch(repo: Path) -> str | None:
    result = _run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])
    if result.returncode != 0:
        return None
    name = result.stdout.strip()
    return name if name != "" else None


def _is_ancestor(repo: Path, start: str) -> bool:
    result = _run_git(repo, ["merge-base", "--is-ancestor", start, "HEAD"])
    return result.returncode == 0


def _implementation_postcondition_failure(worktree: Path, start: str, ticket: str) -> str | None:
    head = _head_sha(worktree)
    if head is None:
        return "unable to read worktree HEAD after Grok"
    if head == start:
        return "Grok produced no implementation commit"
    status = _run_git(worktree, ["status", "--porcelain"])
    if status.returncode != 0:
        return "unable to read worktree status after Grok"
    if status.stdout.strip() != "":
        return "worktree is dirty after Grok"
    counted = _run_git(worktree, ["rev-list", "--count", f"{start}..HEAD"])
    if counted.returncode != 0:
        return "unable to count commits from start to HEAD"
    try:
        commit_count = int(counted.stdout.strip())
    except ValueError:
        return "unable to count commits from start to HEAD"
    if commit_count != 1:
        return (
            f"start..HEAD contains {commit_count} commits, "
            "expected exactly one implementation commit"
        )
    shown = _run_git(worktree, ["show", f"HEAD:{ticket}"])
    if shown.returncode != 0:
        return f"ticket {ticket} is missing at implementation HEAD"
    body = shown.stdout
    if _DONE_STATUS.search(body) is not None:
        return "ticket Status is done; dispatcher success requires Status=review, never done"
    if _REVIEW_STATUS.search(body) is None:
        return "ticket Status is not review at implementation HEAD"
    match = _START_COMMIT_FIELD.search(body)
    if match is None:
        return "ticket Start commit is missing at implementation HEAD"
    recorded = match.group(1).strip().lower()
    if recorded != start:
        return "ticket Start commit does not match the recorded start SHA"
    return None


def _finalize_launch(
    *,
    request: DispatchRequest,
    paths: DispatcherPaths,
    ticket_id: str,
    worktree: Path,
    branch: str,
    started_at: str,
    session_id: str | None,
    child_completed: bool,
    run_state: str,
    diagnostic: str,
    grok_exit_code: int | None,
    stop_reason: str | None,
    timed_out: bool,
    stderr: str,
) -> DispatchResult:
    implementation_commit = _head_sha(worktree)
    final_state: dict[str, object] = {
        "ticket": request.ticket,
        "start_commit": request.start_commit,
        "branch": branch,
        "worktree": str(worktree),
        "writer": request.writer,
        "session_id": session_id,
        "child_pid": None,
        "state": run_state,
        "implementation_commit": implementation_commit,
        "grok_exit_code": grok_exit_code,
        "stop_reason": stop_reason,
        "started_at": started_at,
        "updated_at": _now(),
        "diagnostic": diagnostic,
    }
    _write_state(paths, ticket_id, final_state)
    _write_log(
        paths,
        ticket_id,
        {
            "ticket": request.ticket,
            "mode": request.mode,
            "run_state": run_state,
            "session_id": session_id,
            "grok_exit_code": grok_exit_code,
            "stop_reason": stop_reason,
            "timed_out": timed_out,
            "diagnostic": diagnostic,
            "stderr": redact_secrets(stderr)[:500],
        },
    )
    return DispatchResult(
        child_completed=child_completed,
        run_state=run_state,
        ticket=request.ticket,
        start_commit=request.start_commit,
        writer=request.writer,
        session_id=session_id,
        worktree=str(worktree),
        branch=branch,
        implementation_commit=implementation_commit,
        grok_exit_code=grok_exit_code,
        stop_reason=stop_reason,
        diagnostic=diagnostic,
    )


def _create_worktree(repo: Path, worktree: Path, branch: str, start: str) -> None:
    try:
        worktree.resolve().relative_to(repo.resolve())
    except ValueError:
        pass
    else:
        raise DispatcherError("worktree must not be created inside the primary checkout")
    if worktree.exists():
        raise DispatcherError(f"worktree path already exists: {worktree}")
    worktree.parent.mkdir(parents=True, exist_ok=True)
    added = _run_git(repo, ["worktree", "add", "-b", branch, str(worktree), start])
    if added.returncode != 0:
        detail = (added.stderr or added.stdout).strip()
        raise DispatcherError(f"failed to create ticket worktree: {detail}")
    head = _head_sha(worktree)
    if head != start:
        raise DispatcherError("worktree HEAD does not equal the exact start commit")


def _launch(
    *,
    request: DispatchRequest,
    grok_runner: GrokRunner,
    paths: DispatcherPaths,
    ticket_id: str,
    worktree: Path,
    branch: str,
    resume_session_id: str | None,
    existing: Mapping[str, object] | None,
) -> DispatchResult:
    if request.mode == "resume" and request.instruction is not None:
        prompt = build_resume_prompt(
            request.ticket, request.start_commit, request.instruction
        )
    else:
        prompt = build_writer_prompt(request.ticket, request.start_commit)
    argv = build_grok_argv(
        prompt=prompt,
        worktree=worktree,
        resume_session_id=resume_session_id,
    )
    started_at = existing.get("started_at") if existing is not None else _now()
    if not isinstance(started_at, str) or started_at == "":
        started_at = _now()
    base_state: dict[str, object] = {
        "ticket": request.ticket,
        "start_commit": request.start_commit,
        "branch": branch,
        "worktree": str(worktree),
        "writer": request.writer,
        "session_id": resume_session_id,
        "child_pid": None,
        "state": "running",
        "implementation_commit": existing.get("implementation_commit") if existing else None,
        "grok_exit_code": None,
        "stop_reason": None,
        "started_at": started_at,
        "updated_at": _now(),
        "diagnostic": "Grok child running",
    }
    _write_state(paths, ticket_id, base_state)

    def record_pid(pid: int) -> None:
        current = dict(base_state)
        current["child_pid"] = pid
        current["updated_at"] = _now()
        _write_state(paths, ticket_id, current)

    try:
        child = grok_runner(argv, str(worktree), CHILD_TIMEOUT_SECONDS, record_pid)
    except subprocess.TimeoutExpired:
        return _finalize_launch(
            request=request,
            paths=paths,
            ticket_id=ticket_id,
            worktree=worktree,
            branch=branch,
            started_at=started_at,
            session_id=resume_session_id,
            child_completed=False,
            run_state="interrupted",
            diagnostic="Grok child timed out after 7200 seconds",
            grok_exit_code=124,
            stop_reason=None,
            timed_out=True,
            stderr="",
        )
    except Exception as exc:
        diagnostic = redact_secrets(f"Grok child raised {type(exc).__name__}: {exc}")[:500]
        return _finalize_launch(
            request=request,
            paths=paths,
            ticket_id=ticket_id,
            worktree=worktree,
            branch=branch,
            started_at=started_at,
            session_id=resume_session_id,
            child_completed=False,
            run_state="failed",
            diagnostic=diagnostic,
            grok_exit_code=None,
            stop_reason=None,
            timed_out=False,
            stderr="",
        )
    payload = _parse_grok_json(child.stdout)
    session_id = _session_id_from(payload)
    if resume_session_id is not None:
        session_id = resume_session_id
    stop_reason = _stop_reason_from(payload)
    child_completed, run_state, diagnostic = _classify_run(child, payload, stop_reason)
    if request.mode == "implement" and session_id is None:
        child_completed = False
        if run_state == "completed":
            run_state = "failed"
        diagnostic = "Grok returned no sessionId"
    if child_completed:
        postcondition = _implementation_postcondition_failure(
            worktree, request.start_commit, request.ticket
        )
        if postcondition is not None:
            child_completed = False
            run_state = "failed"
            diagnostic = postcondition
    return _finalize_launch(
        request=request,
        paths=paths,
        ticket_id=ticket_id,
        worktree=worktree,
        branch=branch,
        started_at=started_at,
        session_id=session_id,
        child_completed=child_completed,
        run_state=run_state,
        diagnostic=diagnostic,
        grok_exit_code=child.exit_code,
        stop_reason=stop_reason,
        timed_out=child.timed_out,
        stderr=child.stderr,
    )


def _implement(
    *,
    request: DispatchRequest,
    grok_runner: GrokRunner,
    paths: DispatcherPaths,
    ticket_id: str,
) -> DispatchResult:
    state = _load_state(paths, ticket_id)
    _refuse_if_active(state, ticket_id)
    if state is not None:
        raise DispatcherError(f"ticket {ticket_id} already has a Writer record; use resume")
    worktree = _worktree_path(paths, ticket_id)
    branch = _branch_name(ticket_id)
    _refuse_foreign_worktree(paths, ticket_id, worktree, branch)
    _create_worktree(request.repo_root, worktree, branch, request.start_commit)
    return _launch(
        request=request,
        grok_runner=grok_runner,
        paths=paths,
        ticket_id=ticket_id,
        worktree=worktree,
        branch=branch,
        resume_session_id=None,
        existing=None,
    )


def _resume(
    *,
    request: DispatchRequest,
    grok_runner: GrokRunner,
    paths: DispatcherPaths,
    ticket_id: str,
) -> DispatchResult:
    state = _load_state(paths, ticket_id)
    if state is None:
        raise DispatcherError(f"ticket {ticket_id} has no Writer record to resume")
    _refuse_if_active(state, ticket_id)
    recorded_start = state.get("start_commit")
    recorded_branch = state.get("branch")
    recorded_worktree = state.get("worktree")
    recorded_writer = state.get("writer")
    recorded_session = state.get("session_id")
    if recorded_start != request.start_commit:
        raise DispatcherError("resume start commit does not match the recorded start commit")
    if recorded_writer != request.writer:
        raise DispatcherError("resume writer identity does not match the recorded Writer")
    if not isinstance(recorded_branch, str) or recorded_branch == "":
        raise DispatcherError("recorded branch is missing")
    if not isinstance(recorded_worktree, str) or recorded_worktree == "":
        raise DispatcherError("recorded worktree is missing")
    if not isinstance(recorded_session, str) or recorded_session.strip() == "":
        raise DispatcherError("recorded Grok session id is missing; resume refuses a new Writer")
    worktree = Path(recorded_worktree)
    expected = _worktree_path(paths, ticket_id)
    if worktree.resolve() != expected:
        raise DispatcherError("recorded worktree path does not match this ticket")
    if not worktree.is_dir():
        raise DispatcherError("recorded worktree path does not exist")
    branch = _current_branch(worktree)
    if branch != recorded_branch:
        raise DispatcherError("recorded branch does not match worktree HEAD")
    if not _is_ancestor(worktree, request.start_commit):
        raise DispatcherError("recorded start commit is not an ancestor of worktree HEAD")
    return _launch(
        request=request,
        grok_runner=grok_runner,
        paths=paths,
        ticket_id=ticket_id,
        worktree=worktree,
        branch=recorded_branch,
        resume_session_id=recorded_session.strip(),
        existing=state,
    )


if __name__ == "__main__":
    raise SystemExit(main())
