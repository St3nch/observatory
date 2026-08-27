"""OPS-03 dispatcher proofs. Fake Grok child only; never invoke real grok/xAI."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

import pytest

_TOOLS = Path(__file__).resolve().parents[1] / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import grok_dispatcher as gd  # noqa: E402

CANONICAL_ORIGIN = "ssh://github.com/St3nch/observatory.git"
TICKET = "tickets/TEST-01-dispatcher-fixture.md"
ACCEPTED_TICKET = """# TEST-01 — Dispatcher fixture ticket

**Status:** accepted

## Changed-path allowlist

- one small dispatcher module under `tools/`
"""
DRAFT_TICKET = """# TEST-01 — Dispatcher fixture ticket

**Status:** draft
"""
_GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "dispatcher-test",
    "GIT_AUTHOR_EMAIL": "dispatcher-test@observatory.local",
    "GIT_COMMITTER_NAME": "dispatcher-test",
    "GIT_COMMITTER_EMAIL": "dispatcher-test@observatory.local",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_OPTIONAL_LOCKS": "0",
}


def _review_ticket(start: str, status: str = "review") -> str:
    return (
        "# TEST-01 — Dispatcher fixture ticket\n\n"
        f"**Status:** {status}\n\n"
        f"**Start commit:** {start}\n\n"
        "## Changed-path allowlist\n\n"
        "- one small dispatcher module under `tools/`\n\n"
        "## Implementation report\n\n"
        "- End commit: test\n"
    )


def _commit_ticket(
    worktree: Path,
    body: str,
    message: str,
    extra: dict[str, str] | None = None,
) -> None:
    path = worktree / TICKET
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    _git(worktree, "add", TICKET)
    if extra is not None:
        for rel, content in extra.items():
            target = worktree / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            _git(worktree, "add", rel)
    _git(worktree, "commit", "-m", message)


@dataclass
class FakeGrok:
    session_id: str = "01test-session-from-child"
    stop_reason: str = "end_turn"
    exit_code: int = 0
    stdout_extra: str = ""
    stderr: str = ""
    timed_out: bool = False
    work: str = "none"
    error: Exception | None = None
    start_commit: str = ""
    calls: list[dict[str, Any]] = field(default_factory=list)

    def __call__(
        self,
        argv: Sequence[str],
        cwd: str,
        timeout: int,
        record_pid: Callable[[int], None],
    ) -> gd.GrokChildResult:
        self.calls.append({"argv": list(argv), "cwd": cwd, "timeout": timeout})
        record_pid(os.getpid())
        if self.error is not None:
            raise self.error
        if self.timed_out:
            return gd.GrokChildResult(
                exit_code=124,
                stdout="",
                stderr=self.stderr,
                timed_out=True,
                pid=os.getpid(),
            )
        worktree = Path(cwd)
        start = self.start_commit or _git(worktree, "rev-parse", "HEAD")
        if self.work == "valid":
            _commit_ticket(worktree, _review_ticket(start), "implement TEST-01")
        elif self.work == "two":
            _commit_ticket(worktree, _review_ticket(start), "first")
            _commit_ticket(
                worktree,
                _review_ticket(start),
                "second",
                extra={"extra.txt": "two\n"},
            )
        elif self.work == "dirty":
            _commit_ticket(worktree, _review_ticket(start), "implement TEST-01")
            (worktree / "unstaged.txt").write_text("dirt\n", encoding="utf-8")
        elif self.work == "accepted":
            _commit_ticket(worktree, _review_ticket(start, "accepted"), "implement TEST-01")
        elif self.work == "done":
            _commit_ticket(worktree, _review_ticket(start, "done"), "implement TEST-01")
        elif self.work == "wrong-start":
            _commit_ticket(worktree, _review_ticket("0" * 40), "implement TEST-01")
        payload = {
            "sessionId": self.session_id,
            "stopReason": self.stop_reason,
            "text": self.stdout_extra,
        }
        return gd.GrokChildResult(
            exit_code=self.exit_code,
            stdout=json.dumps(payload),
            stderr=self.stderr,
            timed_out=False,
            pid=os.getpid(),
        )


@pytest.fixture(autouse=True)
def _never_invoke_real_grok(monkeypatch: pytest.MonkeyPatch) -> None:
    def _bomb(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("real grok/xAI child invoked")

    monkeypatch.setattr(gd, "invoke_real_grok", _bomb)
    dispatcher_subprocess = gd.subprocess  # type: ignore[attr-defined]
    original_run = dispatcher_subprocess.run
    original_popen = dispatcher_subprocess.Popen

    def guarded_run(cmd: object, *args: object, **kwargs: object) -> object:
        if _is_grok_cmd(cmd):
            raise AssertionError("real grok executable invoked")
        return original_run(cmd, *args, **kwargs)

    def guarded_popen(cmd: object, *args: object, **kwargs: object) -> object:
        if _is_grok_cmd(cmd):
            raise AssertionError("real grok executable invoked")
        return original_popen(cmd, *args, **kwargs)

    monkeypatch.setattr(dispatcher_subprocess, "run", guarded_run)
    monkeypatch.setattr(dispatcher_subprocess, "Popen", guarded_popen)


def _is_grok_cmd(cmd: object) -> bool:
    return isinstance(cmd, (list, tuple)) and len(cmd) > 0 and str(cmd[0]) == "grok"


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        env=_GIT_ENV,
    )
    if result.returncode != 0:
        raise AssertionError(f"git {args} failed: {result.stderr}")
    return result.stdout.strip()


def _init_repo(root: Path, body: str = ACCEPTED_TICKET) -> str:
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "init", "-b", "main", str(root)],
        check=True,
        capture_output=True,
        text=True,
        env=_GIT_ENV,
    )
    _git(root, "config", "user.name", "dispatcher-test")
    _git(root, "config", "user.email", "dispatcher-test@observatory.local")
    _git(root, "config", "commit.gpgsign", "false")
    _git(root, "remote", "add", "origin", CANONICAL_ORIGIN)
    path = root / TICKET
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    _git(root, "add", TICKET)
    _git(root, "commit", "-m", "add fixture ticket")
    return _git(root, "rev-parse", "HEAD")


@dataclass
class Harness:
    repo: Path
    start: str
    paths: Any
    grok: FakeGrok
    writer: str = "writer-1"

    def __post_init__(self) -> None:
        if self.grok.start_commit == "":
            self.grok.start_commit = self.start

    def request(self, mode: Literal["implement", "resume"] = "implement") -> Any:
        return gd.DispatchRequest(
            repo_root=self.repo,
            ticket=TICKET,
            start_commit=self.start,
            mode=mode,
            writer=self.writer,
        )

    def run(self, mode: Literal["implement", "resume"] = "implement") -> Any:
        return gd.dispatch(self.request(mode), grok_runner=self.grok, paths=self.paths)

    def state(self) -> dict[str, Any]:
        ticket_id = Path(TICKET).stem
        path = self.paths.state_dir / f"{ticket_id}.json"
        return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))

    def logs(self) -> list[dict[str, Any]]:
        directory = self.paths.log_dir / Path(TICKET).stem
        if not directory.is_dir():
            return []
        payloads = []
        for path in sorted(directory.glob("*.json")):
            payloads.append(json.loads(path.read_text(encoding="utf-8")))
        return payloads


@pytest.fixture
def harness(tmp_path: Path) -> Iterator[Harness]:
    repo = tmp_path / "observatory"
    start = _init_repo(repo)
    paths = gd.DispatcherPaths(
        canonical_repo_root=repo,
        canonical_origin=CANONICAL_ORIGIN,
        dispatcher_home=tmp_path / "dispatcher-home",
    )
    yield Harness(repo=repo, start=start, paths=paths, grok=FakeGrok())


def test_production_paths_are_canonical() -> None:
    paths = gd.DispatcherPaths.production()
    assert paths.canonical_repo_root == Path("/home/chaz/projects/vedaops/observatory")
    assert paths.canonical_origin == "ssh://github.com/St3nch/observatory.git"
    assert paths.dispatcher_home == Path.home() / ".local/share/vedaops/observatory/dispatcher"
    assert paths.worktrees == paths.dispatcher_home / "worktrees"


def test_origin_identity_accepts_equivalent_ssh_forms_only() -> None:
    assert gd.origin_is_observatory("ssh://github.com/St3nch/observatory.git")
    assert gd.origin_is_observatory("git@github.com:St3nch/observatory.git")
    assert not gd.origin_is_observatory("https://github.com/St3nch/observatory.git")
    assert not gd.origin_is_observatory("git@github.com:other/observatory.git")


def test_missing_ticket_refuses_before_grok(harness: Harness) -> None:
    request = gd.DispatchRequest(
        repo_root=harness.repo,
        ticket="tickets/missing-ticket.md",
        start_commit=harness.start,
        mode="implement",
        writer="writer-1",
    )
    with pytest.raises(gd.DispatcherError, match="does not exist"):
        gd.dispatch(request, grok_runner=harness.grok, paths=harness.paths)
    assert harness.grok.calls == []


def test_unaccepted_start_commit_object_refuses_despite_later_accepted_head(
    harness: Harness,
) -> None:
    draft = tmp_harness(harness, "draft-object", DRAFT_TICKET)
    (draft.repo / TICKET).write_text(ACCEPTED_TICKET, encoding="utf-8")
    _git(draft.repo, "add", TICKET)
    _git(draft.repo, "commit", "-m", "later accepted copy on HEAD")
    request = gd.DispatchRequest(
        repo_root=draft.repo,
        ticket=TICKET,
        start_commit=draft.start,
        mode="implement",
        writer="writer-1",
    )
    with pytest.raises(gd.DispatcherError, match="not accepted"):
        gd.dispatch(request, grok_runner=draft.grok, paths=draft.paths)
    assert draft.grok.calls == []


def test_accepted_start_commit_object_is_used_not_later_head_file(harness: Harness) -> None:
    (harness.repo / TICKET).write_text(DRAFT_TICKET, encoding="utf-8")
    _git(harness.repo, "add", TICKET)
    _git(harness.repo, "commit", "-m", "later draft on HEAD")
    result = harness.run("implement")
    assert len(harness.grok.calls) == 1
    assert result.session_id == "01test-session-from-child"


def test_invalid_start_commit_refuses_before_grok(harness: Harness) -> None:
    request = gd.DispatchRequest(
        repo_root=harness.repo,
        ticket=TICKET,
        start_commit="0" * 40,
        mode="implement",
        writer="writer-1",
    )
    with pytest.raises(gd.DispatcherError, match="does not exist"):
        gd.dispatch(request, grok_runner=harness.grok, paths=harness.paths)
    assert harness.grok.calls == []


def test_malformed_start_commit_refuses_before_grok(harness: Harness) -> None:
    request = gd.DispatchRequest(
        repo_root=harness.repo,
        ticket=TICKET,
        start_commit="not-a-sha",
        mode="implement",
        writer="writer-1",
    )
    with pytest.raises(gd.DispatcherError, match="40-hex"):
        gd.dispatch(request, grok_runner=harness.grok, paths=harness.paths)
    assert harness.grok.calls == []


def test_dirty_base_refuses_before_grok(harness: Harness) -> None:
    (harness.repo / "untracked.txt").write_text("dirt\n", encoding="utf-8")
    with pytest.raises(gd.DispatcherError, match="dirty"):
        harness.run("implement")
    assert harness.grok.calls == []


def test_wrong_origin_refuses_before_grok(harness: Harness) -> None:
    _git(harness.repo, "remote", "set-url", "origin", "git@github.com:other/observatory.git")
    with pytest.raises(gd.DispatcherError, match="repository identity"):
        harness.run("implement")
    assert harness.grok.calls == []


def test_worktree_head_equals_exact_start_commit(harness: Harness) -> None:
    result = harness.run("implement")
    assert result.worktree is not None
    assert result.child_completed is False
    worktree = Path(result.worktree)
    assert worktree.is_dir()
    assert _git(worktree, "rev-parse", "HEAD") == harness.start
    assert worktree == harness.paths.worktrees / Path(TICKET).stem
    try:
        worktree.relative_to(harness.repo)
        raise AssertionError("worktree was created inside the primary checkout")
    except ValueError:
        pass
    argv = harness.grok.calls[0]["argv"]
    assert "--cwd" in argv
    assert argv[argv.index("--cwd") + 1] == str(worktree)
    assert "--worktree" not in argv
    assert "--ref" not in argv


def test_duplicate_active_writer_refuses(harness: Harness) -> None:
    first = harness.run("implement")
    assert first.session_id == "01test-session-from-child"
    with pytest.raises(gd.DispatcherError, match="already has a Writer"):
        harness.run("implement")
    assert len(harness.grok.calls) == 1


def test_other_ticket_live_worktree_refuses_before_grok(harness: Harness) -> None:
    ticket_id = Path(TICKET).stem
    intended = (harness.paths.worktrees / ticket_id).resolve()
    harness.paths.state_dir.mkdir(parents=True, exist_ok=True)
    foreign = {
        "ticket": "tickets/OTHER-01-live.md",
        "start_commit": harness.start,
        "branch": f"dispatcher/{ticket_id}",
        "worktree": str(intended),
        "writer": "other-writer",
        "session_id": "other-session",
        "child_pid": os.getpid(),
        "state": "running",
        "implementation_commit": None,
        "grok_exit_code": None,
        "stop_reason": None,
        "started_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
        "diagnostic": "running",
    }
    (harness.paths.state_dir / "OTHER-01-live.json").write_text(
        json.dumps(foreign), encoding="utf-8"
    )
    with pytest.raises(gd.DispatcherError, match="another ticket's live worktree"):
        harness.run("implement")
    assert harness.grok.calls == []


def test_running_state_with_live_pid_refuses_second_writer(harness: Harness) -> None:
    harness.run("implement")
    state_path = harness.paths.state_dir / f"{Path(TICKET).stem}.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload["state"] = "running"
    payload["child_pid"] = os.getpid()
    state_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(gd.DispatcherError, match="running Writer|live Writer"):
        harness.run("resume")
    assert len(harness.grok.calls) == 1


def test_prompt_contains_ticket_start_commit_and_hard_boundaries(harness: Harness) -> None:
    harness.run("implement")
    argv = harness.grok.calls[0]["argv"]
    prompt = argv[argv.index("-p") + 1]
    assert TICKET in prompt
    assert harness.start in prompt
    assert "AGENTS.md" in prompt
    assert "changed-path allowlist" in prompt
    assert "SKILL.md" in prompt
    assert "project-local" in prompt
    assert "One Writer only" in prompt
    assert "Status=review" in prompt
    assert "never done" in prompt
    assert "provider" in prompt
    assert "Implementation report" in prompt


def test_implement_records_child_session_id_and_always_approve_denies(
    harness: Harness,
) -> None:
    result = harness.run("implement")
    assert result.session_id == "01test-session-from-child"
    assert result.stop_reason == "end_turn"
    argv = harness.grok.calls[0]["argv"]
    assert argv[0] == "grok"
    assert "--always-approve" in argv
    assert "dontAsk" not in argv
    assert "--permission-mode" not in argv
    assert "--no-subagents" in argv
    assert "--no-ask-user" in argv
    assert "--disable-web-search" in argv
    assert "--no-memory" in argv
    assert "--verbatim" in argv
    assert "--output-format" in argv
    assert argv[argv.index("--output-format") + 1] == "json"
    assert "--resume" not in argv
    assert "--session-id" not in argv
    assert "--continue" not in argv
    assert "--fork-session" not in argv
    for rule in gd.DENY_RULES:
        assert rule in argv
    assert harness.grok.calls[0]["timeout"] == 7200
    assert harness.state()["session_id"] == "01test-session-from-child"


def test_resume_reuses_same_session_id_and_worktree(harness: Harness) -> None:
    first = harness.run("implement")
    worktree = Path(cast(str, first.worktree))
    (worktree / "note.txt").write_text("interrupted work\n", encoding="utf-8")
    _git(worktree, "add", "note.txt")
    _git(worktree, "commit", "-m", "writer progress")
    progressed = _git(worktree, "rev-parse", "HEAD")
    second = harness.run("resume")
    assert second.session_id == first.session_id
    assert second.worktree == first.worktree
    argv = harness.grok.calls[1]["argv"]
    assert "--resume" in argv
    assert argv[argv.index("--resume") + 1] == first.session_id
    assert argv[argv.index("--cwd") + 1] == first.worktree
    assert "--session-id" not in argv
    assert "--continue" not in argv
    assert "--fork-session" not in argv
    assert "--worktree" not in argv
    assert _git(worktree, "rev-parse", "HEAD") == progressed
    assert harness.state()["session_id"] == first.session_id


def test_nonzero_timeout_and_auth_failure_are_not_success(harness: Harness) -> None:
    harness.grok.exit_code = 1
    harness.grok.stop_reason = "error"
    failed = harness.run("implement")
    assert failed.child_completed is False
    assert failed.run_state == "failed"
    other = tmp_harness(harness, "auth")
    other.grok.exit_code = 1
    other.grok.stderr = "Grok authentication expired"
    other.grok.stop_reason = "error"
    auth = other.run("implement")
    assert auth.child_completed is False
    assert auth.diagnostic == "Grok authentication failed"
    timed = tmp_harness(harness, "timeout")
    timed.grok.timed_out = True
    interrupted = timed.run("implement")
    assert interrupted.child_completed is False
    assert interrupted.run_state == "interrupted"


def test_exit_zero_with_cancelled_stop_reason_is_not_success(harness: Harness) -> None:
    harness.grok.exit_code = 0
    harness.grok.stop_reason = "cancelled"
    result = harness.run("implement")
    assert result.child_completed is False
    assert result.run_state == "cancelled"
    assert result.session_id == "01test-session-from-child"
    assert result.grok_exit_code == 0
    assert "cancelled" in result.diagnostic
    assert harness.state()["state"] == "cancelled"
    resumed = harness.run("resume")
    assert resumed.session_id == result.session_id
    assert len(harness.grok.calls) == 2


def test_logs_and_state_redact_secret_like_inputs(harness: Harness) -> None:
    harness.grok.stdout_extra = "XAI_API_KEY=sk-secretvalue DATAFORSEO_PASSWORD=hunter2"
    harness.grok.stderr = "token=abcd1234secret"
    result = harness.run("implement")
    assert result.session_id == "01test-session-from-child"
    blob = json.dumps(harness.state()) + json.dumps(harness.logs())
    assert "sk-secretvalue" not in blob
    assert "hunter2" not in blob
    assert "abcd1234secret" not in blob
    assert "[redacted]" in json.dumps(harness.logs())


def test_dispatcher_cannot_merge_main_or_mark_ticket_done(harness: Harness) -> None:
    assert gd.forbidden_git_reason(["merge", "main"]) is not None
    assert gd.forbidden_git_reason(["push", "origin", "main"]) is not None
    assert gd.forbidden_git_reason(["checkout", "main"]) is not None
    assert gd.forbidden_git_reason(["switch", "main"]) is not None
    assert gd.forbidden_git_reason(["merge-base", "--is-ancestor", "a", "b"]) is None
    before = (harness.repo / TICKET).read_text(encoding="utf-8")
    result = harness.run("implement")
    after_primary = (harness.repo / TICKET).read_text(encoding="utf-8")
    after_worktree = (Path(cast(str, result.worktree)) / TICKET).read_text(encoding="utf-8")
    assert after_primary == before
    assert "**Status:** done" not in after_worktree
    argv = harness.grok.calls[0]["argv"]
    assert "Bash(git merge *)" in argv
    assert "Bash(git push *)" in argv
    prompt = argv[argv.index("-p") + 1]
    assert "never done" in prompt
    assert "does not merge" in prompt


def test_cli_exit_nonzero_on_cancelled_json_result(harness: Harness) -> None:
    harness.grok.stop_reason = "cancelled"
    code = gd.main(
        [
            "--repo-root",
            str(harness.repo),
            "--ticket",
            TICKET,
            "--start-commit",
            harness.start,
            "--mode",
            "implement",
            "--writer",
            "writer-1",
        ],
        grok_runner=harness.grok,
        paths=harness.paths,
    )
    assert code == 1


def test_end_turn_without_commit_is_not_success(harness: Harness) -> None:
    result = harness.run("implement")
    assert result.stop_reason == "end_turn"
    assert result.grok_exit_code == 0
    assert result.child_completed is False
    assert result.run_state == "failed"
    assert "no implementation commit" in result.diagnostic
    assert harness.state()["state"] == "failed"
    assert _git(Path(cast(str, result.worktree)), "rev-parse", "HEAD") == harness.start


def test_multiple_commits_is_not_success(harness: Harness) -> None:
    harness.grok.work = "two"
    result = harness.run("implement")
    assert result.child_completed is False
    assert result.run_state == "failed"
    assert "expected exactly one implementation commit" in result.diagnostic


def test_dirty_worktree_after_grok_is_not_success(harness: Harness) -> None:
    harness.grok.work = "dirty"
    result = harness.run("implement")
    assert result.child_completed is False
    assert result.run_state == "failed"
    assert "dirty" in result.diagnostic


def test_wrong_ticket_status_or_done_is_not_success(harness: Harness) -> None:
    harness.grok.work = "accepted"
    accepted = harness.run("implement")
    assert accepted.child_completed is False
    assert "not review" in accepted.diagnostic
    done = tmp_harness(harness, "done-status")
    done.grok.work = "done"
    done_result = done.run("implement")
    assert done_result.child_completed is False
    assert "never done" in done_result.diagnostic
    wrong = tmp_harness(harness, "wrong-start")
    wrong.grok.work = "wrong-start"
    wrong_result = wrong.run("implement")
    assert wrong_result.child_completed is False
    assert "Start commit" in wrong_result.diagnostic


def test_valid_single_commit_completion_succeeds(harness: Harness) -> None:
    harness.grok.work = "valid"
    result = harness.run("implement")
    assert result.child_completed is True
    assert result.run_state == "completed"
    worktree = Path(cast(str, result.worktree))
    head = _git(worktree, "rev-parse", "HEAD")
    assert head != harness.start
    assert _git(worktree, "rev-list", "--count", f"{harness.start}..HEAD") == "1"
    assert _git(worktree, "status", "--porcelain") == ""
    body = _git(worktree, "show", f"HEAD:{TICKET}")
    assert "**Status:** review" in body
    assert "**Status:** done" not in body
    assert harness.start in body
    assert result.implementation_commit == head


def test_child_environment_strips_secret_bearing_names() -> None:
    source = {
        "PATH": "/usr/bin",
        "HOME": "/home/chaz",
        "SAFE_VALUE": "ok",
        "XAI_API_KEY": "xai-secret",
        "GH_TOKEN": "gh",
        "GITHUB_TOKEN": "gho",
        "OBSERVATORY_DATAFORSEO_PASSWORD": "pw",
        "MY_API_KEY": "k",
        "SERVICE_TOKEN": "t",
        "DB_SECRET": "s",
        "AUTHORIZATION": "Bearer abc",
        "CREDENTIAL_FILE": "x",
    }
    env = gd.child_environment(source)
    assert env == {"PATH": "/usr/bin", "HOME": "/home/chaz", "SAFE_VALUE": "ok"}
    persisted = json.dumps(env)
    assert "xai-secret" not in persisted
    assert "gho" not in persisted


def test_deny_rules_cover_network_and_secret_path_writes(harness: Harness) -> None:
    harness.run("implement")
    argv = harness.grok.calls[0]["argv"]
    for rule in (
        "Bash(git pull *)",
        "Bash(git fetch *)",
        "Bash(git clone *)",
        "Bash(git ls-remote *)",
        "Bash(ssh *)",
        "Bash(scp *)",
        "Bash(sudo *)",
        "Read(~/.grok/auth.json)",
        "Edit(~/.grok/auth.json)",
        "Write(~/.grok/auth.json)",
        "Read(.env)",
        "Edit(.env)",
        "Write(.env)",
        "Write(**/*.pem)",
        "Edit(**/*credential*)",
        "Write(**/*.key)",
    ):
        assert rule in argv
    assert gd.forbidden_git_reason(["pull", "origin"]) is not None
    assert gd.forbidden_git_reason(["fetch", "origin"]) is not None
    assert gd.forbidden_git_reason(["clone", "url"]) is not None
    assert gd.forbidden_git_reason(["ls-remote", "origin"]) is not None


def test_grok_runner_exception_is_failed_not_running(harness: Harness) -> None:
    boom = tmp_harness(harness, "boom")
    boom.grok.error = RuntimeError("XAI_API_KEY=sk-leaked boom")
    result = boom.run("implement")
    assert result.child_completed is False
    assert result.run_state == "failed"
    state = boom.state()
    assert state["state"] == "failed"
    assert state["child_pid"] is None
    assert "sk-leaked" not in json.dumps(state)
    assert "sk-leaked" not in result.diagnostic
    assert "RuntimeError" in result.diagnostic
    cli = tmp_harness(harness, "boom-cli")
    cli.grok.error = RuntimeError("XAI_API_KEY=sk-leaked boom")
    code = gd.main(
        [
            "--repo-root",
            str(cli.repo),
            "--ticket",
            TICKET,
            "--start-commit",
            cli.start,
            "--mode",
            "implement",
            "--writer",
            "writer-1",
        ],
        grok_runner=cli.grok,
        paths=cli.paths,
    )
    assert code == 1
    assert cli.state()["state"] == "failed"
    assert cli.state()["child_pid"] is None


def tmp_harness(base: Harness, suffix: str, body: str = ACCEPTED_TICKET) -> Harness:
    repo = base.paths.dispatcher_home.parent / f"repo-{suffix}"
    start = _init_repo(repo, body)
    paths = gd.DispatcherPaths(
        canonical_repo_root=repo,
        canonical_origin=CANONICAL_ORIGIN,
        dispatcher_home=base.paths.dispatcher_home.parent / f"home-{suffix}",
    )
    return Harness(repo=repo, start=start, paths=paths, grok=FakeGrok())
