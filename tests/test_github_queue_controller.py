"""OPS-04 GitHub queue / draft-PR control plane. Fake GitHub and dispatcher only."""

from __future__ import annotations

import fcntl
import json
import os
import socket
import subprocess
import sys
import urllib.request
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, field
from http.client import HTTPSConnection
from pathlib import Path
from typing import Any, cast

import pytest

_TOOLS = Path(__file__).resolve().parents[1] / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import github_queue_controller as gqc  # noqa: E402
import grok_dispatcher as gd  # noqa: E402

CANONICAL_ORIGIN = "ssh://github.com/St3nch/observatory.git"
TICKET = "tickets/TEST-04-control-plane.md"
TICKET_ID = "TEST-04-control-plane"
BRANCH = f"dispatcher/{TICKET_ID}"
WRITER = f"bootie/{TICKET_ID}"
REPO_ID = 42424242
ISSUE_NUMBER = 7
ACTOR_ID = 54292644
STAMP = "2026-08-27T12:00:00Z"
_GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "controller-test",
    "GIT_AUTHOR_EMAIL": "controller-test@observatory.local",
    "GIT_COMMITTER_NAME": "controller-test",
    "GIT_COMMITTER_EMAIL": "controller-test@observatory.local",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_OPTIONAL_LOCKS": "0",
}


def _review_ticket(start: str) -> str:
    return (
        "# TEST-04 — Control plane fixture ticket\n\n"
        f"**Status:** review\n\n"
        f"**Start commit:** {start}\n\n"
        "## Implementation report\n\n"
        "- End commit: test\n"
    )


ACCEPTED_TICKET = """# TEST-04 — Control plane fixture ticket

**Status:** accepted

## Changed-path allowlist

- one small GitHub control-plane module under `tools/`
"""
DRAFT_TICKET = """# TEST-04 — Control plane fixture ticket

**Status:** draft
"""


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


def _real_git(repo: Path, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        env=_GIT_ENV,
    )


def _is_forbidden_cmd(cmd: object) -> bool:
    if not isinstance(cmd, (list, tuple)) or not cmd:
        return False
    exe = str(Path(str(cmd[0])).name)
    if exe in {"gh", "grok", "curl", "wget", "ssh", "scp"}:
        return True
    blob = " ".join(str(part) for part in cmd)
    if exe != "git":
        return "github.com" in blob or "api.github.com" in blob or "x.ai" in blob
    args = [str(part) for part in cmd[1:]]
    if len(args) >= 2 and args[0] == "-C":
        args = args[2:]
    if not args:
        return False
    if args[0] in {"fetch", "push", "ls-remote", "clone", "pull"}:
        return "github.com" in blob or "api.github.com" in blob or "x.ai" in blob
    return False


@pytest.fixture(autouse=True)
def _bomb_external(monkeypatch: pytest.MonkeyPatch) -> None:
    def _bomb_grok(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("real grok/xAI child invoked")

    monkeypatch.setattr(gd, "invoke_real_grok", _bomb_grok)
    original_run = subprocess.run
    original_popen = subprocess.Popen
    original_https = HTTPSConnection.__init__
    original_getaddrinfo = socket.getaddrinfo

    def guarded_run(*args: Any, **kwargs: Any) -> Any:
        cmd = args[0] if args else kwargs.get("args")
        if _is_forbidden_cmd(cmd):
            raise AssertionError(f"forbidden command invoked: {cmd}")
        return original_run(*args, **kwargs)

    def guarded_popen(*args: Any, **kwargs: Any) -> Any:
        cmd = args[0] if args else kwargs.get("args")
        if _is_forbidden_cmd(cmd):
            raise AssertionError(f"forbidden command invoked: {cmd}")
        return original_popen(*args, **kwargs)

    def guarded_urlopen(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("urllib GitHub/HTTP invoked")

    def guarded_https(self: HTTPSConnection, host: str, *args: Any, **kwargs: Any) -> None:
        if "github" in host or "x.ai" in host:
            raise AssertionError(f"HTTPS to {host}")
        original_https(self, host, *args, **kwargs)

    blocked = {"github.com", "api.github.com", "www.github.com", "x.ai", "api.x.ai"}

    def guarded_dns(host: bytes | str | None, *args: Any, **kwargs: Any) -> Any:
        hostname = host.decode() if isinstance(host, bytes) else str(host)
        if hostname in blocked or hostname.endswith(".github.com"):
            raise AssertionError(f"DNS lookup to {hostname}")
        return original_getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", guarded_run)
    monkeypatch.setattr(subprocess, "Popen", guarded_popen)
    monkeypatch.setattr(urllib.request, "urlopen", guarded_urlopen)
    monkeypatch.setattr(HTTPSConnection, "__init__", guarded_https)
    monkeypatch.setattr(socket, "getaddrinfo", guarded_dns)
    monkeypatch.setattr("github_queue_controller.subprocess.run", guarded_run)
    monkeypatch.setattr("github_queue_controller.subprocess.Popen", guarded_popen)


def _init_repo(root: Path, body: str = ACCEPTED_TICKET) -> str:
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "init", "-b", "main", str(root)],
        check=True,
        capture_output=True,
        text=True,
        env=_GIT_ENV,
    )
    _git(root, "config", "user.name", "controller-test")
    _git(root, "config", "user.email", "controller-test@observatory.local")
    _git(root, "config", "commit.gpgsign", "false")
    _git(root, "remote", "add", "origin", CANONICAL_ORIGIN)
    path = root / TICKET
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    _git(root, "add", TICKET)
    _git(root, "commit", "-m", "add fixture ticket")
    return _git(root, "rev-parse", "HEAD")


def _clone_bare(repo: Path, bare: Path) -> None:
    subprocess.run(
        ["git", "clone", "--bare", str(repo), str(bare)],
        check=True,
        capture_output=True,
        text=True,
        env=_GIT_ENV,
    )


def _command(start: str, mode: str = "implement") -> str:
    return f"/bootie {mode} {TICKET} {start}"


def _comment(
    start: str,
    *,
    comment_id: int = 1001,
    mode: str = "implement",
    body: str | None = None,
    user_id: int = ACTOR_ID,
    login: str = "St3nch",
    user_type: str = "User",
    created_at: str = STAMP,
    updated_at: str | None = None,
) -> gqc.IssueComment:
    return gqc.IssueComment(
        comment_id=comment_id,
        user_id=user_id,
        user_login=login,
        user_type=user_type,
        body=_command(start, mode) if body is None else body,
        created_at=created_at,
        updated_at=created_at if updated_at is None else updated_at,
    )


def _failed_result(request: gd.DispatchRequest, diagnostic: str = "failed") -> gd.DispatchResult:
    return gd.DispatchResult(
        child_completed=False,
        run_state="failed",
        ticket=request.ticket,
        start_commit=request.start_commit,
        writer=request.writer,
        session_id=None,
        worktree=None,
        branch=None,
        implementation_commit=None,
        grok_exit_code=1,
        stop_reason=None,
        diagnostic=diagnostic,
    )


def _success_result(
    request: gd.DispatchRequest,
    *,
    worktree: Path,
    implementation_commit: str,
    run_state: str = "completed",
) -> gd.DispatchResult:
    return gd.DispatchResult(
        child_completed=True,
        run_state=run_state,
        ticket=request.ticket,
        start_commit=request.start_commit,
        writer=request.writer,
        session_id="01test-session",
        worktree=str(worktree),
        branch=BRANCH,
        implementation_commit=implementation_commit,
        grok_exit_code=0,
        stop_reason="end_turn",
        diagnostic="Grok child completed with a successful stop reason",
    )


class RecordingGit:
    def __init__(self, bare: Path) -> None:
        self.bare = bare
        self.calls: list[list[str]] = []
        self.fetch_error: str | None = None
        self.push_error: str | None = None

    def run(self, repo: Path, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
        argv = [str(part) for part in args]
        self.calls.append(argv)
        if argv[:1] == ["fetch"]:
            if self.fetch_error is not None:
                return subprocess.CompletedProcess(["git", *argv], 1, "", self.fetch_error)
            if argv != ["fetch", "origin", "refs/heads/main:refs/remotes/origin/main"]:
                return subprocess.CompletedProcess(["git", *argv], 1, "", "unexpected fetch argv")
            return _real_git(repo, ["fetch", str(self.bare), argv[2]])
        if argv[:1] == ["push"]:
            if self.push_error is not None:
                return subprocess.CompletedProcess(["git", *argv], 1, "", self.push_error)
            redirected = [str(self.bare) if part == "origin" else part for part in argv]
            return _real_git(repo, redirected)
        if argv[:2] == ["ls-remote", "origin"]:
            redirected = [str(self.bare) if part == "origin" else part for part in argv]
            return _real_git(repo, redirected)
        return _real_git(repo, argv)

    def push_calls(self) -> list[list[str]]:
        return [call for call in self.calls if call[:1] == ["push"]]

    def fetch_calls(self) -> list[list[str]]:
        return [call for call in self.calls if call[:1] == ["fetch"]]


class FakeGitHub:
    def __init__(
        self,
        *,
        comments: list[gqc.IssueComment] | None = None,
        repository_id: int = REPO_ID,
        issue_number: int = ISSUE_NUMBER,
    ) -> None:
        self.comments = list(comments or [])
        self.repository_id = repository_id
        self.issue_number = issue_number
        self.pulls: list[gqc.PullRequestInfo] = []
        self.calls: list[tuple[object, ...]] = []
        self.posted: list[str] = []
        self.created_prs: list[gqc.PullRequestInfo] = []
        self._next_comment_id = 9000
        self._next_pr = 11

    def get_repository(self) -> gqc.RepositoryInfo:
        self.calls.append(("get_repository",))
        return gqc.RepositoryInfo(
            repository_id=self.repository_id,
            owner="St3nch",
            name="observatory",
        )

    def get_issue(self, issue_number: int) -> gqc.IssueInfo:
        self.calls.append(("get_issue", issue_number))
        return gqc.IssueInfo(number=self.issue_number, repository_id=self.repository_id)

    def list_issue_comments(self, issue_number: int) -> list[gqc.IssueComment]:
        self.calls.append(("list_issue_comments", issue_number))
        if issue_number != self.issue_number:
            raise AssertionError("GitHub issue number was not the commissioned queue")
        return list(self.comments)

    def post_issue_comment(self, issue_number: int, body: str) -> gqc.PostedComment:
        self.calls.append(("post_issue_comment", issue_number, body))
        self.posted.append(body)
        self._next_comment_id += 1
        return gqc.PostedComment(comment_id=self._next_comment_id)

    def get_pull_request(self, number: int) -> gqc.PullRequestInfo:
        self.calls.append(("get_pull_request", number))
        for pull in self.pulls:
            if pull.number == number:
                return pull
        raise gqc.ControllerError(f"pull request {number} does not exist")

    def list_open_pulls_for_head(self, head: str) -> list[gqc.PullRequestInfo]:
        self.calls.append(("list_open_pulls_for_head", head))
        return [
            pull
            for pull in self.pulls
            if pull.state == "open"
            and f"{pull.head_owner}:{pull.head_ref}" == head
        ]

    def create_draft_pull_request(
        self,
        *,
        title: str,
        body: str,
        head: str,
        base: str,
    ) -> gqc.PullRequestInfo:
        self.calls.append(("create_draft_pull_request", title, body, head, base))
        if base != "main":
            raise AssertionError("PR base is not main")
        pull = _pr(number=self._next_pr, head_ref=head)
        self._next_pr += 1
        self.pulls.append(pull)
        self.created_prs.append(pull)
        return pull


def _pr(
    *,
    number: int = 11,
    state: str = "open",
    draft: bool = True,
    merged: bool = False,
    head_ref: str = BRANCH,
    head_owner: str = "St3nch",
    head_name: str = "observatory",
    head_repository_id: int = REPO_ID,
    head_is_fork: bool = False,
    base_ref: str = "main",
    base_owner: str = "St3nch",
    base_name: str = "observatory",
    base_repository_id: int = REPO_ID,
) -> gqc.PullRequestInfo:
    return gqc.PullRequestInfo(
        number=number,
        state=state,
        draft=draft,
        merged=merged,
        html_url=f"https://github.com/St3nch/observatory/pull/{number}",
        base_ref=base_ref,
        base_owner=base_owner,
        base_name=base_name,
        base_repository_id=base_repository_id,
        head_ref=head_ref,
        head_owner=head_owner,
        head_name=head_name,
        head_repository_id=head_repository_id,
        head_is_fork=head_is_fork,
    )


class FakeDispatcher:
    def __init__(self) -> None:
        self.calls: list[gd.DispatchRequest] = []
        self.queue: list[
            gd.DispatchResult | BaseException | Callable[[gd.DispatchRequest], gd.DispatchResult]
        ] = []
        self.state: dict[str, object] | None = None
        self.live_pid = False

    def enqueue(
        self,
        item: gd.DispatchResult | BaseException | Callable[[gd.DispatchRequest], gd.DispatchResult],
    ) -> None:
        self.queue.append(item)

    def dispatch(self, request: gd.DispatchRequest) -> gd.DispatchResult:
        self.calls.append(request)
        if not self.queue:
            return _failed_result(request, "fake dispatcher has no queued result")
        item = self.queue.pop(0)
        if isinstance(item, BaseException):
            raise item
        if callable(item):
            return item(request)
        return item

    def load_ticket_state(self, ticket_id: str) -> dict[str, object] | None:
        if self.state is None:
            return None
        if self.state.get("ticket_id", ticket_id) != ticket_id and "ticket" in self.state:
            pass
        return dict(self.state)

    def pid_alive(self, pid: object) -> bool:
        return bool(self.live_pid and isinstance(pid, int) and pid > 0)


@dataclass
class Harness:
    repo: Path
    start: str
    paths: gqc.ControllerPaths
    git: RecordingGit
    github: FakeGitHub
    dispatcher: FakeDispatcher
    worktree: Path | None = None
    impl_sha: str | None = None
    comments: list[gqc.IssueComment] = field(default_factory=list)

    def add_comment(self, comment: gqc.IssueComment) -> None:
        self.github.comments.append(comment)

    def poll(self) -> gqc.PollResult:
        return gqc.poll_once(
            paths=self.paths,
            github=self.github,
            dispatcher=self.dispatcher,
            git=self.git,
        )

    def event(self, comment_id: int = 1001) -> dict[str, Any]:
        path = self.paths.events_dir / f"{comment_id}.json"
        return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))

    def write_queue_config(self) -> None:
        self.paths.controller_home.mkdir(parents=True, exist_ok=True)
        (self.paths.controller_home / "queue.json").write_text(
            json.dumps(
                {
                    "github_repository_id": REPO_ID,
                    "queue_issue_number": ISSUE_NUMBER,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def make_implementation(self) -> tuple[Path, str]:
        worktree = self.paths.controller_home.parent / "worktrees" / TICKET_ID
        if worktree.exists():
            head = _git(worktree, "rev-parse", "HEAD")
            return worktree, head
        _git(self.repo, "worktree", "add", "-b", BRANCH, str(worktree), self.start)
        (worktree / TICKET).write_text(_review_ticket(self.start), encoding="utf-8")
        _git(worktree, "add", TICKET)
        _git(worktree, "commit", "-m", "implement TEST-04")
        sha = _git(worktree, "rev-parse", "HEAD")
        self.worktree = worktree
        self.impl_sha = sha
        return worktree, sha

    def enqueue_success(self) -> tuple[Path, str]:
        worktree, sha = self.make_implementation()

        def _succeed(request: gd.DispatchRequest) -> gd.DispatchResult:
            return _success_result(request, worktree=worktree, implementation_commit=sha)

        self.dispatcher.enqueue(_succeed)
        return worktree, sha


@pytest.fixture
def harness(tmp_path: Path) -> Iterator[Harness]:
    repo = tmp_path / "observatory"
    start = _init_repo(repo)
    bare = tmp_path / "origin.git"
    _clone_bare(repo, bare)
    paths = gqc.ControllerPaths(
        canonical_repo_root=repo,
        canonical_origin=CANONICAL_ORIGIN,
        controller_home=tmp_path / "bootie-factory",
        dispatcher_home=tmp_path / "dispatcher-home",
    )
    item = Harness(
        repo=repo,
        start=start,
        paths=paths,
        git=RecordingGit(bare),
        github=FakeGitHub(),
        dispatcher=FakeDispatcher(),
    )
    item.write_queue_config()
    yield item


def test_controller_does_not_import_observatory_runtime() -> None:
    source = Path(gqc.__file__).read_text(encoding="utf-8")
    assert "from observatory" not in source
    assert "import observatory" not in source
    assert "observatory.evidence" not in source


def test_missing_queue_config_refuses_without_dispatcher_or_github(tmp_path: Path) -> None:
    repo = tmp_path / "observatory"
    _init_repo(repo)
    paths = gqc.ControllerPaths(
        canonical_repo_root=repo,
        canonical_origin=CANONICAL_ORIGIN,
        controller_home=tmp_path / "bootie-factory",
        dispatcher_home=tmp_path / "dispatcher-home",
    )
    github = FakeGitHub()
    dispatcher = FakeDispatcher()
    git = RecordingGit(tmp_path / "missing.git")
    with pytest.raises(gqc.ControllerError, match="commissioned"):
        gqc.poll_once(paths=paths, github=github, dispatcher=dispatcher, git=git)
    assert github.calls == []
    assert dispatcher.calls == []


@pytest.mark.parametrize(
    ("user_id", "login", "user_type"),
    [
        (1, "St3nch", "User"),
        (ACTOR_ID, "other", "User"),
        (ACTOR_ID, "St3nch", "Bot"),
        (ACTOR_ID, "St3nch", "Organization"),
    ],
)
def test_non_allowlisted_actor_refuses_before_dispatcher_or_repo_mutation(
    harness: Harness,
    user_id: int,
    login: str,
    user_type: str,
) -> None:
    harness.add_comment(
        _comment(
            harness.start,
            user_id=user_id,
            login=login,
            user_type=user_type,
        )
    )
    result = harness.poll()
    assert result.dispatched is False
    assert result.published is False
    assert harness.dispatcher.calls == []
    assert harness.git.push_calls() == []
    assert harness.github.created_prs == []
    assert harness.github.posted == []
    assert all(call[0] != "post_issue_comment" for call in harness.github.calls)
    assert all(call[0] != "create_draft_pull_request" for call in harness.github.calls)
    assert "allowlist" in result.diagnostic.lower() or "actor" in result.diagnostic.lower()


@pytest.mark.parametrize(
    "body",
    [
        "/bootie implement tickets/TEST-04-control-plane.md {sha} please",
        '"/bootie implement tickets/TEST-04-control-plane.md {sha}"',
        "/bootie implement tickets/TEST-04-control-plane.md {sha}<br>",
        "/bootie implement tickets/TEST-04-control-plane.md {sha} @St3nch",
        "/bootie implement tickets/TEST-04-control-plane.md {upper}",
        "/bootie implement tickets/TEST-04-control-plane.md {short}",
        "/bootie implement ./tickets/TEST-04-control-plane.md {sha}",
        "/bootie implement tickets/../secrets.md {sha}",
        (
            "/bootie implement tickets/TEST-04-control-plane.md {sha}\n"
            "/bootie resume tickets/TEST-04-control-plane.md {sha}"
        ),
        "please /bootie implement tickets/TEST-04-control-plane.md {sha}",
    ],
)
def test_malformed_command_refuses_before_dispatch(harness: Harness, body: str) -> None:
    filled = body.format(sha=harness.start, upper=harness.start.upper(), short=harness.start[:39])
    harness.add_comment(_comment(harness.start, body=filled))
    result = harness.poll()
    assert result.dispatched is False
    assert harness.dispatcher.calls == []
    assert harness.git.push_calls() == []
    assert harness.github.created_prs == []


def test_edited_at_ingest_refuses_before_dispatch(harness: Harness) -> None:
    harness.add_comment(_comment(harness.start, updated_at="2026-08-27T12:00:01Z"))
    result = harness.poll()
    assert result.dispatched is False
    assert harness.dispatcher.calls == []
    assert "edited" in result.diagnostic.lower()


def test_claimed_body_hash_mismatch_refuses_before_dispatch(harness: Harness) -> None:
    comment = _comment(harness.start)
    harness.add_comment(comment)
    claimed = {
        "comment_id": comment.comment_id,
        "ticket": TICKET,
        "start_commit": harness.start,
        "mode": "implement",
        "writer": WRITER,
        "processing_state": "claimed",
        "body_sha256": "0" * 64,
        "created_at": STAMP,
        "actor_id": ACTOR_ID,
        "actor_login": "St3nch",
        "dispatcher_run_state": None,
        "dispatcher_session_id": None,
        "child_completed": None,
        "implementation_commit": None,
        "worktree": None,
        "branch": None,
        "published_sha": None,
        "pr_number": None,
        "result_comment_id": None,
        "diagnostic": "",
        "claimed_at": STAMP,
        "updated_at": STAMP,
    }
    harness.paths.events_dir.mkdir(parents=True, exist_ok=True)
    (harness.paths.events_dir / f"{comment.comment_id}.json").write_text(
        json.dumps(claimed, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    result = harness.poll()
    assert result.dispatched is False
    assert harness.dispatcher.calls == []
    assert "hash" in result.diagnostic.lower() or "mismatch" in result.diagnostic.lower()


def test_claimed_event_edited_to_non_command_prose_is_refused_not_skipped(
    harness: Harness,
) -> None:
    original = _comment(harness.start, comment_id=1001)
    claimed = {
        "comment_id": original.comment_id,
        "ticket": TICKET,
        "start_commit": harness.start,
        "mode": "implement",
        "writer": WRITER,
        "processing_state": "claimed",
        "body_sha256": gqc.body_sha256(gqc.normalize_comment_body(original.body)),
        "created_at": STAMP,
        "actor_id": ACTOR_ID,
        "actor_login": "St3nch",
        "dispatcher_run_state": None,
        "dispatcher_session_id": None,
        "child_completed": None,
        "implementation_commit": None,
        "worktree": None,
        "branch": None,
        "published_sha": None,
        "pr_number": None,
        "result_comment_id": None,
        "diagnostic": "",
        "claimed_at": STAMP,
        "updated_at": STAMP,
    }
    harness.paths.events_dir.mkdir(parents=True, exist_ok=True)
    (harness.paths.events_dir / f"{original.comment_id}.json").write_text(
        json.dumps(claimed, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    harness.add_comment(
        _comment(
            harness.start,
            comment_id=original.comment_id,
            body="never mind, this is ordinary prose",
            updated_at="2026-08-27T12:05:00Z",
        )
    )
    result = harness.poll()
    assert result.processed is True
    assert result.comment_id == original.comment_id
    assert result.dispatched is False
    assert result.published is False
    assert harness.dispatcher.calls == []
    assert harness.git.push_calls() == []
    assert harness.github.created_prs == []
    assert "hash" in result.diagnostic.lower() or "mismatch" in result.diagnostic.lower()
    assert harness.event(original.comment_id)["processing_state"] == "done"


def test_duplicate_comment_id_is_idempotent_and_never_rediscovers_writer(harness: Harness) -> None:
    harness.add_comment(_comment(harness.start))
    harness.enqueue_success()
    first = harness.poll()
    assert first.dispatched is True
    assert first.published is True
    assert len(harness.dispatcher.calls) == 1
    second = harness.poll()
    assert second.dispatched is False or second.state == "done"
    assert len(harness.dispatcher.calls) == 1
    assert len(harness.github.created_prs) == 1
    assert len(harness.git.push_calls()) == 1


def test_start_not_on_origin_main_refuses(harness: Harness) -> None:
    (harness.repo / "local-only.txt").write_text("only local\n", encoding="utf-8")
    _git(harness.repo, "add", "local-only.txt")
    _git(harness.repo, "commit", "-m", "local only")
    local_only = _git(harness.repo, "rev-parse", "HEAD")
    harness.add_comment(_comment(local_only))
    result = harness.poll()
    assert result.dispatched is False
    assert harness.dispatcher.calls == []
    assert "origin/main" in result.diagnostic or "ancestor" in result.diagnostic.lower()
    assert harness.git.fetch_calls() == [
        ["fetch", "origin", "refs/heads/main:refs/remotes/origin/main"]
    ]


def test_fetch_failure_refuses_and_does_not_use_stale_local_main(harness: Harness) -> None:
    harness.add_comment(_comment(harness.start))
    harness.git.fetch_error = "network exploded"
    result = harness.poll()
    assert result.dispatched is False
    assert harness.dispatcher.calls == []
    assert "fetch" in result.diagnostic.lower()


def test_dirty_primary_refuses_before_dispatch(harness: Harness) -> None:
    (harness.repo / "dirt.txt").write_text("dirt\n", encoding="utf-8")
    harness.add_comment(_comment(harness.start))
    result = harness.poll()
    assert result.dispatched is False
    assert harness.dispatcher.calls == []
    assert harness.git.push_calls() == []
    assert "dirty" in result.diagnostic.lower()


def test_unaccepted_ticket_at_start_object_refuses(harness: Harness) -> None:
    draft_root = harness.repo.parent / "draft-repo"
    draft_start = _init_repo(draft_root, DRAFT_TICKET)
    bare = harness.repo.parent / "draft-origin.git"
    _clone_bare(draft_root, bare)
    paths = gqc.ControllerPaths(
        canonical_repo_root=draft_root,
        canonical_origin=CANONICAL_ORIGIN,
        controller_home=harness.paths.controller_home.parent / "draft-bootie",
        dispatcher_home=harness.paths.dispatcher_home.parent / "draft-dispatcher",
    )
    draft = Harness(
        repo=draft_root,
        start=draft_start,
        paths=paths,
        git=RecordingGit(bare),
        github=FakeGitHub(),
        dispatcher=FakeDispatcher(),
    )
    draft.write_queue_config()
    (draft.repo / TICKET).write_text(ACCEPTED_TICKET, encoding="utf-8")
    _git(draft.repo, "add", TICKET)
    _git(draft.repo, "commit", "-m", "later accepted copy")
    draft.add_comment(_comment(draft_start))
    result = draft.poll()
    assert result.dispatched is False
    assert draft.dispatcher.calls == []
    assert "accepted" in result.diagnostic.lower()


def test_passes_exact_ticket_start_mode_and_ticket_stable_writer(harness: Harness) -> None:
    harness.add_comment(_comment(harness.start))
    harness.enqueue_success()
    harness.poll()
    assert len(harness.dispatcher.calls) == 1
    request = harness.dispatcher.calls[0]
    assert request.ticket == TICKET
    assert request.start_commit == harness.start
    assert request.mode == "implement"
    assert request.writer == WRITER
    assert "1001" not in request.writer


@pytest.mark.parametrize("run_state", ["failed", "cancelled", "interrupted"])
def test_dispatcher_non_success_never_pushes_or_opens_pr(harness: Harness, run_state: str) -> None:
    harness.add_comment(_comment(harness.start))

    def _fail(request: gd.DispatchRequest) -> gd.DispatchResult:
        return gd.DispatchResult(
            child_completed=False,
            run_state=run_state,
            ticket=request.ticket,
            start_commit=request.start_commit,
            writer=request.writer,
            session_id="sess",
            worktree=None,
            branch=None,
            implementation_commit=None,
            grok_exit_code=1,
            stop_reason=run_state,
            diagnostic=run_state,
        )

    harness.dispatcher.enqueue(_fail)
    result = harness.poll()
    assert result.dispatched is True
    assert result.published is False
    assert harness.git.push_calls() == []
    assert harness.github.created_prs == []
    assert result.state == "done"
    assert harness.github.posted


def test_stuck_dispatcher_is_reported_without_repair_or_relaunch(harness: Harness) -> None:
    harness.add_comment(_comment(harness.start))
    harness.dispatcher.state = {
        "ticket": TICKET,
        "start_commit": harness.start,
        "state": "running",
        "child_pid": 999999,
        "session_id": "sess",
    }
    harness.dispatcher.live_pid = False
    result = harness.poll()
    assert result.dispatched is False
    assert harness.dispatcher.calls == []
    assert harness.git.push_calls() == []
    assert "stuck" in result.diagnostic.lower()
    assert harness.dispatcher.state["state"] == "running"
    assert harness.dispatcher.state["child_pid"] == 999999


def test_successful_implement_publishes_only_ticket_branch_without_force(harness: Harness) -> None:
    harness.add_comment(_comment(harness.start))
    _worktree, sha = harness.enqueue_success()
    result = harness.poll()
    assert result.published is True
    assert result.implementation_commit == sha
    pushes = harness.git.push_calls()
    assert pushes == [
        ["push", "origin", f"refs/heads/{BRANCH}:refs/heads/{BRANCH}"]
    ]
    assert all("--force" not in arg and not arg.startswith("--force") for arg in pushes[0])
    assert all("refs/heads/main" not in arg for arg in pushes[0])
    assert len(harness.github.created_prs) == 1
    created = harness.github.created_prs[0]
    assert created.draft is True
    create_call = [c for c in harness.github.calls if c[0] == "create_draft_pull_request"][0]
    assert create_call[3] == BRANCH
    assert create_call[4] == "main"
    remote_sha = _git(harness.git.bare, "rev-parse", BRANCH)
    assert remote_sha == sha
    assert _git(harness.git.bare, "rev-parse", "main") == harness.start


def test_resume_force_with_lease_uses_recorded_sha_and_mismatch_refuses(harness: Harness) -> None:
    first = _comment(harness.start, comment_id=1001)
    harness.add_comment(first)
    worktree, sha1 = harness.enqueue_success()
    first_result = harness.poll()
    assert first_result.published is True
    assert harness.event(1001)["published_sha"] == sha1
    (worktree / "extra.txt").write_text("remediation\n", encoding="utf-8")
    _git(worktree, "add", "extra.txt")
    _git(worktree, "commit", "--amend", "-m", "implement TEST-04 remediated")
    sha2 = _git(worktree, "rev-parse", "HEAD")
    assert sha2 != sha1
    harness.add_comment(_comment(harness.start, comment_id=1002, mode="resume"))

    def _resume_ok(request: gd.DispatchRequest) -> gd.DispatchResult:
        assert request.mode == "resume"
        assert request.writer == WRITER
        return _success_result(request, worktree=worktree, implementation_commit=sha2)

    harness.dispatcher.enqueue(_resume_ok)
    second = harness.poll()
    assert second.published is True
    lease = [
        call
        for call in harness.git.push_calls()
        if any(part.startswith("--force-with-lease=") for part in call)
    ]
    assert lease == [
        [
            "push",
            f"--force-with-lease=refs/heads/{BRANCH}:{sha1}",
            "origin",
            f"refs/heads/{BRANCH}:refs/heads/{BRANCH}",
        ]
    ]
    assert all(part != "--force" for part in lease[0])
    assert len(harness.github.created_prs) == 1
    assert second.pr_number == first_result.pr_number

    _init_repo(harness.repo.parent / "other")
    _git(harness.git.bare, "fetch", str(harness.repo.parent / "other"), f"+main:{BRANCH}")
    foreign = _git(harness.git.bare, "rev-parse", BRANCH)
    assert foreign != sha2
    harness.add_comment(_comment(harness.start, comment_id=1003, mode="resume"))
    harness.dispatcher.enqueue(_resume_ok)
    before = list(harness.git.push_calls())
    mismatch = harness.poll()
    assert mismatch.published is False
    blob = mismatch.diagnostic.lower()
    assert "push" in blob or "lease" in blob or "failed" in blob
    new_lease = harness.git.push_calls()[len(before) :]
    assert new_lease
    assert all(part != "--force" for part in new_lease[0])
    assert all(not part.startswith("--force=") for part in new_lease[0])


def test_one_ticket_reuses_open_draft_pr_and_rejects_foreign_state(harness: Harness) -> None:
    harness.add_comment(_comment(harness.start))
    harness.enqueue_success()
    first = harness.poll()
    assert first.pr_number == 11
    harness.add_comment(_comment(harness.start, comment_id=2002, mode="resume"))
    worktree, sha = harness.make_implementation()
    harness.dispatcher.enqueue(
        lambda request: _success_result(request, worktree=worktree, implementation_commit=sha)
    )
    second = harness.poll()
    assert second.pr_number == 11
    assert len(harness.github.created_prs) == 1

    harness.add_comment(_comment(harness.start, comment_id=2003, mode="resume"))
    harness.dispatcher.enqueue(
        lambda request: _success_result(request, worktree=worktree, implementation_commit=sha)
    )
    harness.github.pulls[0] = _pr(number=11, draft=False)
    ready = harness.poll()
    diagnostic = ready.diagnostic.lower()
    assert ready.published is False or "draft" in diagnostic or "ready" in diagnostic
    assert len(harness.github.created_prs) == 1

    for index, bad in enumerate(
        (
            _pr(number=11, state="closed"),
            _pr(number=11, merged=True, state="closed"),
            _pr(number=11, base_ref="develop"),
            _pr(number=11, head_owner="other"),
            _pr(number=11, head_is_fork=True),
            _pr(number=11, base_repository_id=1),
        )
    ):
        other_id = 4001 + index
        harness.add_comment(_comment(harness.start, comment_id=other_id, mode="resume"))

        def _resume_success(
            request: gd.DispatchRequest,
            *,
            worktree: Path = worktree,
            sha: str = sha,
        ) -> gd.DispatchResult:
            return _success_result(request, worktree=worktree, implementation_commit=sha)

        harness.dispatcher.enqueue(_resume_success)
        harness.github.pulls[0] = bad
        result = harness.poll()
        assert len(harness.github.created_prs) == 1
        assert result.pr_number in {None, 11}


def test_controller_cannot_push_main_merge_approve_mark_ready_or_close_done(
    harness: Harness,
) -> None:
    with pytest.raises(gqc.ControllerError):
        gqc.assert_safe_push_args(["push", "origin", "refs/heads/main"], TICKET_ID)
    with pytest.raises(gqc.ControllerError):
        gqc.assert_safe_push_args(
            ["push", "--force", "origin", f"refs/heads/{BRANCH}:refs/heads/{BRANCH}"],
            TICKET_ID,
        )
    args = gqc.build_push_args(TICKET_ID)
    assert "refs/heads/main" not in " ".join(args)
    assert "--force" not in args
    harness.add_comment(_comment(harness.start))
    harness.enqueue_success()
    harness.poll()
    methods = [call[0] for call in harness.github.calls]
    assert "merge" not in methods
    assert "approve" not in methods
    assert "mark_ready" not in methods
    assert "close" not in methods
    assert all("gh pr" not in str(call) for call in harness.github.calls)
    body = (harness.repo / TICKET).read_text(encoding="utf-8")
    assert "**Status:** done" not in body


def test_result_comments_are_bounded_and_redact_secrets(harness: Harness) -> None:
    harness.add_comment(_comment(harness.start))

    def _leaky(request: gd.DispatchRequest) -> gd.DispatchResult:
        return _failed_result(
            request,
            "XAI_API_KEY=sk-secretvalue GH_TOKEN=gho_secret DATAFORSEO_PASSWORD=hunter2",
        )

    harness.dispatcher.enqueue(_leaky)
    harness.poll()
    assert harness.github.posted
    posted = harness.github.posted[0]
    assert "sk-secretvalue" not in posted
    assert "gho_secret" not in posted
    assert "hunter2" not in posted
    assert "[redacted]" in posted
    assert TICKET in posted
    assert harness.start in posted
    assert "event_comment_id: 1001" in posted
    assert "/bootie" not in posted
    assert "XAI_API_KEY=sk-secretvalue" not in posted
    assert len(posted) < 4000


def test_once_processes_oldest_command_like_event_only(harness: Harness) -> None:
    harness.add_comment(_comment(harness.start, comment_id=1, created_at="2026-08-27T10:00:00Z"))
    harness.add_comment(_comment(harness.start, comment_id=2, created_at="2026-08-27T11:00:00Z"))
    harness.enqueue_success()
    result = harness.poll()
    assert result.comment_id == 1
    assert len(harness.dispatcher.calls) == 1
    assert harness.event(1)["processing_state"] == "done"
    assert not (harness.paths.events_dir / "2.json").exists()


def test_same_comment_never_rediscovers_only_new_resume_event_calls_dispatcher(
    harness: Harness,
) -> None:
    harness.add_comment(_comment(harness.start, comment_id=11))
    worktree, sha = harness.enqueue_success()
    harness.poll()
    harness.poll()
    assert len(harness.dispatcher.calls) == 1
    harness.add_comment(_comment(harness.start, comment_id=12, mode="resume"))
    harness.dispatcher.enqueue(
        lambda request: _success_result(request, worktree=worktree, implementation_commit=sha)
    )
    resumed = harness.poll()
    assert resumed.comment_id == 12
    assert len(harness.dispatcher.calls) == 2
    assert harness.dispatcher.calls[1].mode == "resume"
    assert harness.dispatcher.calls[1].writer == WRITER


def test_crash_after_dispatching_does_not_relaunch_or_duplicate_pr(harness: Harness) -> None:
    comment = _comment(harness.start)
    harness.add_comment(comment)
    worktree, sha = harness.make_implementation()
    _git(worktree, "push", str(harness.git.bare), f"{BRANCH}:{BRANCH}")
    harness.github.pulls.append(_pr(number=21))
    dispatching = {
        "comment_id": comment.comment_id,
        "ticket": TICKET,
        "start_commit": harness.start,
        "mode": "implement",
        "writer": WRITER,
        "processing_state": "dispatching",
        "body_sha256": gqc.body_sha256(gqc.normalize_comment_body(comment.body)),
        "created_at": STAMP,
        "actor_id": ACTOR_ID,
        "actor_login": "St3nch",
        "dispatcher_run_state": None,
        "dispatcher_session_id": None,
        "child_completed": None,
        "implementation_commit": None,
        "worktree": str(worktree),
        "branch": BRANCH,
        "published_sha": None,
        "pr_number": None,
        "result_comment_id": None,
        "diagnostic": "dispatching",
        "claimed_at": STAMP,
        "updated_at": STAMP,
    }
    harness.paths.events_dir.mkdir(parents=True, exist_ok=True)
    (harness.paths.events_dir / f"{comment.comment_id}.json").write_text(
        json.dumps(dispatching, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    harness.dispatcher.state = {
        "ticket": TICKET,
        "start_commit": harness.start,
        "state": "completed",
        "child_pid": None,
        "session_id": "01test-session",
        "implementation_commit": sha,
        "worktree": str(worktree),
        "branch": BRANCH,
        "writer": WRITER,
    }
    result = harness.poll()
    assert harness.dispatcher.calls == []
    assert len(harness.github.created_prs) == 0
    assert result.state == "done"
    assert harness.event()["published_sha"] == sha
    assert harness.event()["pr_number"] == 21


def test_crash_dispatching_without_dispatcher_record_is_stuck_not_relaunched(
    harness: Harness,
) -> None:
    comment = _comment(harness.start)
    harness.add_comment(comment)
    payload = {
        "comment_id": comment.comment_id,
        "ticket": TICKET,
        "start_commit": harness.start,
        "mode": "implement",
        "writer": WRITER,
        "processing_state": "dispatching",
        "body_sha256": gqc.body_sha256(gqc.normalize_comment_body(comment.body)),
        "created_at": STAMP,
        "actor_id": ACTOR_ID,
        "actor_login": "St3nch",
        "dispatcher_run_state": None,
        "dispatcher_session_id": None,
        "child_completed": None,
        "implementation_commit": None,
        "worktree": None,
        "branch": None,
        "published_sha": None,
        "pr_number": None,
        "result_comment_id": None,
        "diagnostic": "dispatching",
        "claimed_at": STAMP,
        "updated_at": STAMP,
    }
    harness.paths.events_dir.mkdir(parents=True, exist_ok=True)
    (harness.paths.events_dir / f"{comment.comment_id}.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    result = harness.poll()
    assert harness.dispatcher.calls == []
    assert harness.git.push_calls() == []
    assert harness.github.created_prs == []
    assert harness.github.posted == []
    assert "stuck" in result.diagnostic.lower()
    assert result.state == "dispatching"
    assert harness.event()["processing_state"] == "dispatching"
    second = harness.poll()
    assert harness.dispatcher.calls == []
    assert harness.git.push_calls() == []
    assert harness.github.posted == []
    assert second.state == "dispatching"
    assert harness.event()["processing_state"] == "dispatching"
    assert second.dispatched is False
    assert second.published is False


def test_publication_refuses_if_branch_moved_after_dispatcher_result(harness: Harness) -> None:
    harness.add_comment(_comment(harness.start))
    worktree, sha = harness.enqueue_success()
    (worktree / "tamper.txt").write_text("moved after dispatcher\n", encoding="utf-8")
    _git(worktree, "add", "tamper.txt")
    _git(worktree, "commit", "-m", "tamper after dispatcher result")
    moved = _git(worktree, "rev-parse", "HEAD")
    assert moved != sha
    result = harness.poll()
    assert result.dispatched is True
    assert result.published is False
    assert harness.git.push_calls() == []
    assert harness.github.created_prs == []
    diagnostic = result.diagnostic.lower()
    assert "implementation commit" in diagnostic or "worktree" in diagnostic
    assert _git(harness.git.bare, "rev-parse", "main") == harness.start
    missing = _real_git(harness.git.bare, ["rev-parse", BRANCH])
    assert missing.returncode != 0


def _production_pull_payload(
    *,
    merged: bool | None = None,
    merged_at: str | None = None,
    include_merged: bool = True,
    include_merged_at: bool = True,
    state: str = "open",
    draft: bool = True,
) -> dict[str, object]:
    repo = {
        "id": REPO_ID,
        "name": "observatory",
        "fork": False,
        "owner": {"login": "St3nch"},
    }
    payload: dict[str, object] = {
        "number": 11,
        "state": state,
        "draft": draft,
        "html_url": "https://github.com/St3nch/observatory/pull/11",
        "base": {"ref": "main", "user": {"login": "St3nch"}, "repo": repo},
        "head": {
            "ref": BRANCH,
            "user": {"login": "St3nch"},
            "repo": repo,
        },
    }
    if include_merged:
        payload["merged"] = merged
    if include_merged_at:
        payload["merged_at"] = merged_at
    return payload


def test_pull_from_api_accepts_get_and_list_production_shapes() -> None:
    listed = gqc._pull_from_api(
        _production_pull_payload(include_merged=False, include_merged_at=True, merged_at=None)
    )
    assert listed.merged is False
    assert listed.draft is True
    get_open = gqc._pull_from_api(
        _production_pull_payload(
            merged=False,
            merged_at=None,
            include_merged=True,
            include_merged_at=True,
        )
    )
    assert get_open.merged is False
    merged_list = gqc._pull_from_api(
        _production_pull_payload(
            include_merged=False,
            include_merged_at=True,
            merged_at="2026-08-27T12:00:00Z",
            state="closed",
            draft=False,
        )
    )
    assert merged_list.merged is True
    get_merged = gqc._pull_from_api(
        _production_pull_payload(
            merged=True,
            merged_at="2026-08-27T12:00:00Z",
            state="closed",
            draft=False,
        )
    )
    assert get_merged.merged is True


def test_pull_from_api_refuses_missing_or_contradictory_merged_fields() -> None:
    with pytest.raises(gqc.ControllerError, match="unreadable"):
        gqc._pull_from_api(_production_pull_payload(include_merged=False, include_merged_at=False))
    with pytest.raises(gqc.ControllerError, match="disagree|unreadable"):
        gqc._pull_from_api(
            _production_pull_payload(merged=False, merged_at="2026-08-27T12:00:00Z")
        )
    bad = _production_pull_payload(include_merged_at=False)
    bad["merged"] = "yes"
    with pytest.raises(gqc.ControllerError, match="unreadable"):
        gqc._pull_from_api(bad)


def test_pull_from_api_refuses_missing_or_non_boolean_head_fork() -> None:
    listed = _production_pull_payload(include_merged=False, merged_at=None)
    assert gqc._pull_from_api(listed).head_is_fork is False
    forked = _production_pull_payload(include_merged=False, merged_at=None)
    head = dict(cast(dict[str, object], forked["head"]))
    repo = dict(cast(dict[str, object], head["repo"]))
    repo["fork"] = True
    head["repo"] = repo
    forked["head"] = head
    assert gqc._pull_from_api(forked).head_is_fork is True
    missing_fork = _production_pull_payload(include_merged=False, merged_at=None)
    missing_head = dict(cast(dict[str, object], missing_fork["head"]))
    missing_repo = dict(cast(dict[str, object], missing_head["repo"]))
    missing_repo.pop("fork")
    missing_head["repo"] = missing_repo
    missing_fork["head"] = missing_head
    with pytest.raises(gqc.ControllerError, match="unreadable"):
        gqc._pull_from_api(missing_fork)
    malformed = _production_pull_payload(include_merged=False, merged_at=None)
    malformed_head = dict(cast(dict[str, object], malformed["head"]))
    malformed_repo = dict(cast(dict[str, object], malformed_head["repo"]))
    malformed_repo["fork"] = "no"
    malformed_head["repo"] = malformed_repo
    malformed["head"] = malformed_head
    with pytest.raises(gqc.ControllerError, match="unreadable"):
        gqc._pull_from_api(malformed)


def test_controller_flock_prevents_concurrent_once(harness: Harness) -> None:
    harness.add_comment(_comment(harness.start))
    harness.paths.lock_dir.mkdir(parents=True, exist_ok=True)
    handle = (harness.paths.lock_dir / "controller.lock").open("a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(gqc.ControllerError, match="already running"):
            harness.poll()
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()
    assert harness.dispatcher.calls == []


def test_fetch_argv_is_main_only_and_push_argv_builders_reject_main() -> None:
    assert gqc.build_fetch_args() == ["fetch", "origin", "refs/heads/main:refs/remotes/origin/main"]
    args = gqc.build_push_args(TICKET_ID, lease_sha="a" * 40)
    assert args[0] == "push"
    assert args[1] == f"--force-with-lease=refs/heads/{BRANCH}:{'a' * 40}"
    assert "main" not in args


def test_crlf_and_whitespace_command_is_accepted(harness: Harness) -> None:
    body = f"\r\n/bootie implement {TICKET} {harness.start}\r\n"
    harness.add_comment(_comment(harness.start, body=body))
    harness.enqueue_success()
    result = harness.poll()
    assert result.dispatched is True
    assert harness.dispatcher.calls[0].mode == "implement"


def test_gh_api_argv_never_uses_pr_create_or_auth_token() -> None:
    argv = gqc.build_gh_api_argv("repos/St3nch/observatory/issues/7/comments")
    joined = " ".join(argv)
    assert argv[0] == "gh"
    assert "auth" not in argv
    assert "token" not in argv
    assert "pr" not in argv
    assert "gh pr create" not in joined
    with pytest.raises(gqc.ControllerError):
        gqc.build_gh_api_argv("user")
    with pytest.raises(gqc.ControllerError):
        gqc.build_gh_api_argv("repos/other/observatory/issues/7/comments")


def test_cli_once_is_required(harness: Harness) -> None:
    code = gqc.main(
        [],
        paths=harness.paths,
        github=harness.github,
        dispatcher=harness.dispatcher,
        git=harness.git,
    )
    assert code == 1
    harness.add_comment(_comment(harness.start))
    harness.enqueue_success()
    code = gqc.main(
        ["--once"],
        paths=harness.paths,
        github=harness.github,
        dispatcher=harness.dispatcher,
        git=harness.git,
    )
    assert code == 0
