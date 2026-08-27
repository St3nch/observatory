"""GitHub queue and draft-PR control plane (OPS-04). Development orchestration only."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, Protocol, TextIO, cast

import grok_dispatcher as gd

ALLOWED_ACTOR_ID = 54292644
ALLOWED_ACTOR_LOGIN = "St3nch"
ALLOWED_ACTOR_TYPE = "User"
GITHUB_OWNER = "St3nch"
GITHUB_REPO = "observatory"
QUEUE_CONFIG_NAME = "queue.json"
CHILD_COMPLETED_STATES = frozenset({"completed"})
PROCESSING_STATES = (
    "claimed",
    "dispatching",
    "dispatched",
    "branch_pushed",
    "pr_ensured",
    "result_posted",
    "done",
)
EVENT_FIELDS = (
    "comment_id",
    "ticket",
    "start_commit",
    "mode",
    "writer",
    "processing_state",
    "body_sha256",
    "created_at",
    "actor_id",
    "actor_login",
    "dispatcher_run_state",
    "dispatcher_session_id",
    "child_completed",
    "implementation_commit",
    "worktree",
    "branch",
    "published_sha",
    "pr_number",
    "result_comment_id",
    "diagnostic",
    "claimed_at",
    "updated_at",
)
RESULT_FIELDS = (
    "ticket",
    "start_commit",
    "mode",
    "writer",
    "dispatcher_state",
    "implementation_commit",
    "branch",
    "pr_number",
    "pr_url",
    "event_comment_id",
    "diagnostic",
)
COMMAND_RE = re.compile(
    r"^/bootie (implement|resume) tickets/([A-Za-z0-9._-]+)\.md ([0-9a-f]{40})$"
)
_ACCEPTED_STATUS = re.compile(r"(?m)^\*\*Status:\*\*\s*accepted\s*$")
_SHA = re.compile(r"^[0-9a-f]{40}$")
_TICKET_ID = re.compile(r"^[A-Za-z0-9._-]+$")
_GH_ENDPOINTS = (
    re.compile(r"^repos/St3nch/observatory$"),
    re.compile(r"^repos/St3nch/observatory/issues/[0-9]+$"),
    re.compile(r"^repos/St3nch/observatory/issues/[0-9]+/comments(?:\?per_page=100&page=[0-9]+)?$"),
    re.compile(r"^repos/St3nch/observatory/pulls$"),
    re.compile(r"^repos/St3nch/observatory/pulls/[0-9]+$"),
    re.compile(
        r"^repos/St3nch/observatory/pulls\?head=St3nch:dispatcher/[A-Za-z0-9._-]+&state=open$"
    ),
)


class ControllerError(Exception):
    """Fail-closed operator-visible controller refusal or run failure."""


class UnauthorizedActorError(ControllerError):
    """Allowlisted-actor failure: refuse with no GitHub mutation."""


class StuckDispatchError(ControllerError):
    """Dispatching crash/stuck: do not redispatch and do not mark the event done."""


@dataclass(frozen=True)
class ControllerPaths:
    canonical_repo_root: Path
    canonical_origin: str
    controller_home: Path
    dispatcher_home: Path

    @classmethod
    def production(cls) -> ControllerPaths:
        return cls(
            canonical_repo_root=gd.CANONICAL_REPO_ROOT,
            canonical_origin=gd.CANONICAL_ORIGIN,
            controller_home=Path.home() / ".local/share/vedaops/observatory/bootie-factory",
            dispatcher_home=gd.DISPATCHER_HOME,
        )

    @property
    def events_dir(self) -> Path:
        return self.controller_home / "events"

    @property
    def lock_dir(self) -> Path:
        return self.controller_home / "locks"

    @property
    def tickets_dir(self) -> Path:
        return self.controller_home / "tickets"


@dataclass(frozen=True)
class QueueConfig:
    github_repository_id: int
    queue_issue_number: int


@dataclass(frozen=True)
class RepositoryInfo:
    repository_id: int
    owner: str
    name: str


@dataclass(frozen=True)
class IssueInfo:
    number: int
    repository_id: int


@dataclass(frozen=True)
class IssueComment:
    comment_id: int
    user_id: int
    user_login: str
    user_type: str
    body: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class PostedComment:
    comment_id: int


@dataclass(frozen=True)
class PullRequestInfo:
    number: int
    state: str
    draft: bool
    merged: bool
    html_url: str
    base_ref: str
    base_owner: str
    base_name: str
    base_repository_id: int
    head_ref: str
    head_owner: str
    head_name: str
    head_repository_id: int
    head_is_fork: bool


@dataclass(frozen=True)
class PollResult:
    processed: bool
    comment_id: int | None
    state: str | None
    diagnostic: str
    dispatched: bool
    published: bool
    implementation_commit: str | None = None
    pr_number: int | None = None


class GitRunner(Protocol):
    def run(self, repo: Path, args: Sequence[str]) -> subprocess.CompletedProcess[str]: ...


class GitHubClient(Protocol):
    def get_repository(self) -> RepositoryInfo: ...

    def get_issue(self, issue_number: int) -> IssueInfo: ...

    def list_issue_comments(self, issue_number: int) -> list[IssueComment]: ...

    def post_issue_comment(self, issue_number: int, body: str) -> PostedComment: ...

    def get_pull_request(self, number: int) -> PullRequestInfo: ...

    def list_open_pulls_for_head(self, head: str) -> list[PullRequestInfo]: ...

    def create_draft_pull_request(
        self,
        *,
        title: str,
        body: str,
        head: str,
        base: str,
    ) -> PullRequestInfo: ...


class DispatcherSeam(Protocol):
    def dispatch(self, request: gd.DispatchRequest) -> gd.DispatchResult: ...

    def load_ticket_state(self, ticket_id: str) -> dict[str, object] | None: ...

    def pid_alive(self, pid: object) -> bool: ...


class SubprocessGit:
    def run(self, repo: Path, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            check=False,
            capture_output=True,
            text=True,
        )


class ProductionDispatcher:
    def __init__(self, paths: ControllerPaths) -> None:
        self._paths = paths
        self._dispatcher_paths = gd.DispatcherPaths(
            canonical_repo_root=paths.canonical_repo_root,
            canonical_origin=paths.canonical_origin,
            dispatcher_home=paths.dispatcher_home,
        )

    def dispatch(self, request: gd.DispatchRequest) -> gd.DispatchResult:
        return gd.dispatch(
            request,
            grok_runner=gd.invoke_real_grok,
            paths=self._dispatcher_paths,
        )

    def load_ticket_state(self, ticket_id: str) -> dict[str, object] | None:
        path = self._paths.dispatcher_home / "state" / f"{ticket_id}.json"
        if not path.is_file():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ControllerError(f"dispatcher state for {ticket_id} is unreadable") from exc
        if not isinstance(payload, dict):
            raise ControllerError(f"dispatcher state for {ticket_id} is unreadable")
        return payload

    def pid_alive(self, pid: object) -> bool:
        if not isinstance(pid, int) or pid <= 0:
            return False
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True


class GhApiClient:
    def get_repository(self) -> RepositoryInfo:
        payload = self._api("repos/St3nch/observatory")
        return _repository_from_api(payload)

    def get_issue(self, issue_number: int) -> IssueInfo:
        repo = self.get_repository()
        payload = self._api(f"repos/St3nch/observatory/issues/{issue_number}")
        number = payload.get("number") if isinstance(payload, dict) else None
        if not isinstance(number, int):
            raise ControllerError("queue issue payload is unreadable")
        return IssueInfo(number=number, repository_id=repo.repository_id)

    def list_issue_comments(self, issue_number: int) -> list[IssueComment]:
        comments: list[IssueComment] = []
        page = 1
        while True:
            endpoint = (
                f"repos/St3nch/observatory/issues/{issue_number}/comments?per_page=100&page={page}"
            )
            payload = self._api(endpoint)
            if not isinstance(payload, list) or not payload:
                break
            for item in payload:
                comments.append(_comment_from_api(item))
            if len(payload) < 100:
                break
            page += 1
        return comments

    def post_issue_comment(self, issue_number: int, body: str) -> PostedComment:
        payload = self._api(
            f"repos/St3nch/observatory/issues/{issue_number}/comments",
            method="POST",
            data={"body": body},
        )
        comment_id = payload.get("id") if isinstance(payload, dict) else None
        if not isinstance(comment_id, int):
            raise ControllerError("result comment payload is unreadable")
        return PostedComment(comment_id=comment_id)

    def get_pull_request(self, number: int) -> PullRequestInfo:
        payload = self._api(f"repos/St3nch/observatory/pulls/{number}")
        return _pull_from_api(payload)

    def list_open_pulls_for_head(self, head: str) -> list[PullRequestInfo]:
        if not re.fullmatch(r"St3nch:dispatcher/[A-Za-z0-9._-]+", head):
            raise ControllerError("refusing GitHub pull-head lookup")
        payload = self._api(f"repos/St3nch/observatory/pulls?head={head}&state=open")
        if not isinstance(payload, list):
            raise ControllerError("pull request list is unreadable")
        return [_pull_from_api(item) for item in payload]

    def create_draft_pull_request(
        self,
        *,
        title: str,
        body: str,
        head: str,
        base: str,
    ) -> PullRequestInfo:
        if base != "main":
            raise ControllerError("refusing pull request base other than main")
        if not re.fullmatch(r"dispatcher/[A-Za-z0-9._-]+", head):
            raise ControllerError("refusing pull request head other than the ticket branch")
        payload = self._api(
            "repos/St3nch/observatory/pulls",
            method="POST",
            data={
                "title": title,
                "body": body,
                "head": head,
                "base": base,
                "draft": True,
            },
        )
        return _pull_from_api(payload)

    def _api(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        data: Mapping[str, object] | None = None,
    ) -> object:
        argv = build_gh_api_argv(endpoint, method=method)
        stdin = None if data is None else json.dumps(dict(data), sort_keys=True)
        result = subprocess.run(
            argv,
            check=False,
            capture_output=True,
            text=True,
            input=stdin,
        )
        if result.returncode != 0:
            detail = gd.redact_secrets((result.stderr or result.stdout).strip())[:200]
            raise ControllerError(f"GitHub API failed: {detail}")
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ControllerError("GitHub API payload is unreadable") from exc


def normalize_comment_body(body: str) -> str:
    return body.replace("\r\n", "\n").replace("\r", "\n").strip()


def body_sha256(normalized: str) -> str:
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def is_command_like(body: str) -> bool:
    return normalize_comment_body(body).startswith("/bootie ")


def parse_bootie_command(normalized: str) -> tuple[Literal["implement", "resume"], str, str]:
    match = COMMAND_RE.fullmatch(normalized)
    if match is None:
        raise ControllerError("command grammar refused")
    mode_raw, ticket_name, sha = match.group(1), match.group(2), match.group(3)
    try:
        ticket = gd._normalize_ticket(f"tickets/{ticket_name}.md")
        start = gd._normalize_sha(sha)
    except gd.DispatcherError as exc:
        raise ControllerError(str(exc)) from exc
    if mode_raw not in {"implement", "resume"}:
        raise ControllerError("command grammar refused")
    return cast(Literal["implement", "resume"], mode_raw), ticket, start


def build_fetch_args() -> list[str]:
    return ["fetch", "origin", "refs/heads/main:refs/remotes/origin/main"]


def build_push_args(ticket_id: str, *, lease_sha: str | None = None) -> list[str]:
    _require_ticket_id(ticket_id)
    dest = f"refs/heads/dispatcher/{ticket_id}"
    args = ["push"]
    if lease_sha is not None:
        try:
            sha = gd._normalize_sha(lease_sha)
        except gd.DispatcherError as exc:
            raise ControllerError(str(exc)) from exc
        args.append(f"--force-with-lease={dest}:{sha}")
    args.extend(["origin", f"{dest}:{dest}"])
    assert_safe_push_args(args, ticket_id)
    return args


def assert_safe_push_args(args: Sequence[str], ticket_id: str) -> None:
    _require_ticket_id(ticket_id)
    expected = f"refs/heads/dispatcher/{ticket_id}:refs/heads/dispatcher/{ticket_id}"
    if not args or args[0] != "push":
        raise ControllerError("push argv must start with push")
    if "origin" not in args:
        raise ControllerError("push argv must target origin")
    if expected not in args:
        raise ControllerError("push argv must use the exact ticket-branch refspec")
    if any(part == "main" or part == "refs/heads/main" for part in args):
        raise ControllerError("push argv names main")
    for part in args:
        if part == "--force" or part.startswith("--force="):
            raise ControllerError("plain --force is forbidden")
        if "refs/heads/main" in part.split(":"):
            raise ControllerError("push argv names main")
        if part.startswith("--force-with-lease=") and not part.startswith(
            f"--force-with-lease=refs/heads/dispatcher/{ticket_id}:"
        ):
            raise ControllerError("force-with-lease must name the exact ticket branch")


def build_gh_api_argv(endpoint: str, *, method: str = "GET") -> list[str]:
    if method not in {"GET", "POST"}:
        raise ControllerError("unsupported GitHub method")
    if any(pattern.fullmatch(endpoint) for pattern in _GH_ENDPOINTS) is False:
        raise ControllerError("refusing GitHub endpoint")
    argv = ["gh", "api", "-H", "Accept: application/vnd.github+json"]
    if method != "GET":
        argv.extend(["--method", method, "--input", "-"])
    argv.append(endpoint)
    if "auth" in argv or "token" in argv or "pr" in argv:
        raise ControllerError("refusing gh auth, token, or pr subcommand")
    return argv


def build_result_comment(event: Mapping[str, object]) -> str:
    diagnostic = gd.redact_secrets(str(event.get("diagnostic") or ""))[:500]
    pr_number = event.get("pr_number")
    pr_url = "none"
    if isinstance(pr_number, int):
        pr_url = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/pull/{pr_number}"
    values: dict[str, object] = {
        "ticket": event.get("ticket") or "none",
        "start_commit": event.get("start_commit") or "none",
        "mode": event.get("mode") or "none",
        "writer": event.get("writer") or "none",
        "dispatcher_state": event.get("dispatcher_run_state") or "none",
        "implementation_commit": event.get("implementation_commit") or "none",
        "branch": event.get("branch") or "none",
        "pr_number": pr_number if isinstance(pr_number, int) else "none",
        "pr_url": pr_url,
        "event_comment_id": event.get("comment_id") or "none",
        "diagnostic": diagnostic,
    }
    return "\n".join(f"{key}: {values[key]}" for key in RESULT_FIELDS)


def load_queue_config(paths: ControllerPaths) -> QueueConfig:
    path = paths.controller_home / QUEUE_CONFIG_NAME
    if not path.is_file():
        raise ControllerError("production queue identity is not commissioned")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ControllerError("queue identity is unreadable") from exc
    if not isinstance(payload, dict):
        raise ControllerError("queue identity is unreadable")
    allowed = {"github_repository_id", "queue_issue_number"}
    if set(payload) - allowed:
        raise ControllerError("queue identity has unsupported fields")
    for key in payload:
        lowered = str(key).lower()
        if any(marker in lowered for marker in gd.SECRET_FIELD_MARKERS):
            raise ControllerError("refusing secret-like queue identity field")
    repo_id = payload.get("github_repository_id")
    issue = payload.get("queue_issue_number")
    if isinstance(repo_id, bool) or not isinstance(repo_id, int) or repo_id <= 0:
        raise ControllerError("github_repository_id is invalid")
    if isinstance(issue, bool) or not isinstance(issue, int) or issue <= 0:
        raise ControllerError("queue_issue_number is invalid")
    return QueueConfig(github_repository_id=repo_id, queue_issue_number=issue)


def poll_once(
    *,
    paths: ControllerPaths,
    github: GitHubClient,
    dispatcher: DispatcherSeam,
    git: GitRunner,
) -> PollResult:
    with _controller_lock(paths):
        config = load_queue_config(paths)
        repo = _require_observatory_repo(paths, git)
        _require_github_queue(github, config)
        comments = github.list_issue_comments(config.queue_issue_number)
        chosen = _oldest_unprocessed(comments, paths)
        if chosen is None:
            return PollResult(
                processed=False,
                comment_id=None,
                state=None,
                diagnostic="no unprocessed command-like events",
                dispatched=False,
                published=False,
            )
        return _process_comment(
            chosen,
            paths=paths,
            github=github,
            dispatcher=dispatcher,
            git=git,
            config=config,
            repo=repo,
        )


def main(
    argv: Sequence[str] | None = None,
    *,
    paths: ControllerPaths | None = None,
    github: GitHubClient | None = None,
    dispatcher: DispatcherSeam | None = None,
    git: GitRunner | None = None,
) -> int:
    parser = argparse.ArgumentParser(prog="github_queue_controller")
    parser.add_argument("--once", action="store_true")
    ns = parser.parse_args(list(argv) if argv is not None else None)
    if not ns.once:
        print("controller: only --once is supported", file=sys.stderr)
        return 1
    try:
        used_paths = paths or ControllerPaths.production()
        poll_once(
            paths=used_paths,
            github=github or GhApiClient(),
            dispatcher=dispatcher or ProductionDispatcher(used_paths),
            git=git or SubprocessGit(),
        )
    except ControllerError as exc:
        print(f"controller: {exc}", file=sys.stderr)
        return 1
    return 0


def _process_comment(
    comment: IssueComment,
    *,
    paths: ControllerPaths,
    github: GitHubClient,
    dispatcher: DispatcherSeam,
    git: GitRunner,
    config: QueueConfig,
    repo: Path,
) -> PollResult:
    called_dispatch = False
    event: dict[str, object] | None = None
    try:
        event = _claim_event(comment, paths)
        if str(event.get("processing_state")) == "done":
            return _poll_from_event(event, dispatched=False, published=_is_published(event))
        while str(event.get("processing_state")) != "done":
            state = str(event.get("processing_state"))
            if state == "claimed":
                event, called_dispatch = _step_dispatch(
                    event,
                    paths=paths,
                    dispatcher=dispatcher,
                    git=git,
                    repo=repo,
                    called_dispatch=called_dispatch,
                )
            elif state == "dispatching":
                event = _step_reconcile_dispatch(event, paths=paths, dispatcher=dispatcher)
            elif state == "dispatched":
                if event.get("child_completed") is True:
                    event = _step_push(event, paths=paths, git=git, repo=repo)
                else:
                    event = _step_result(event, paths=paths, github=github, config=config)
            elif state == "branch_pushed":
                event = _step_pr(event, paths=paths, github=github, config=config)
            elif state == "pr_ensured":
                event = _step_result(event, paths=paths, github=github, config=config)
            elif state == "result_posted":
                event = _step_done(event, paths)
            else:
                raise ControllerError(f"unknown processing state {state}")
    except UnauthorizedActorError as exc:
        diagnostic = gd.redact_secrets(str(exc))[:500]
        if event is None:
            event = _claim_event_for_failure(comment, paths, diagnostic)
        return _finish_unauthorized(event, diagnostic, paths=paths)
    except StuckDispatchError as exc:
        diagnostic = gd.redact_secrets(str(exc))[:500]
        if event is None:
            event = _claim_event_for_failure(comment, paths, diagnostic)
        return _hold_stuck(event, diagnostic, paths=paths)
    except (ControllerError, gd.DispatcherError) as exc:
        diagnostic = gd.redact_secrets(str(exc))[:500]
        if event is None:
            event = _claim_event_for_failure(comment, paths, diagnostic)
        return _finish_refusal(
            event,
            diagnostic,
            paths=paths,
            github=github,
            config=config,
            dispatched=called_dispatch or _already_dispatched(event),
        )
    return _poll_from_event(
        event,
        dispatched=called_dispatch or _already_dispatched(event),
        published=_is_published(event),
    )


def _step_dispatch(
    event: dict[str, object],
    *,
    paths: ControllerPaths,
    dispatcher: DispatcherSeam,
    git: GitRunner,
    repo: Path,
    called_dispatch: bool,
) -> tuple[dict[str, object], bool]:
    ticket = _required_str(event, "ticket")
    start = _required_str(event, "start_commit")
    mode = _required_str(event, "mode")
    writer = _required_str(event, "writer")
    if mode not in {"implement", "resume"}:
        raise ControllerError("command grammar refused")
    ticket_id = gd.ticket_id_for(ticket)
    _require_clean(repo, git)
    _fetch_main(repo, git)
    _require_start_on_origin_main(repo, git, start)
    _require_accepted_ticket(repo, git, start, ticket)
    _refuse_stuck_or_live(dispatcher, ticket_id)
    _set_state(event, "dispatching")
    event["diagnostic"] = "dispatching"
    _write_event(paths, event)
    request = gd.DispatchRequest(
        repo_root=repo,
        ticket=ticket,
        start_commit=start,
        mode=cast(Literal["implement", "resume"], mode),
        writer=writer,
    )
    try:
        result = dispatcher.dispatch(request)
    except gd.DispatcherError as exc:
        event["child_completed"] = False
        event["dispatcher_run_state"] = "refused"
        event["diagnostic"] = gd.redact_secrets(str(exc))[:500]
        _set_state(event, "dispatched")
        _write_event(paths, event)
        return event, True
    _apply_dispatch_result(event, result)
    _set_state(event, "dispatched")
    _write_event(paths, event)
    return event, True


def _step_reconcile_dispatch(
    event: dict[str, object],
    *,
    paths: ControllerPaths,
    dispatcher: DispatcherSeam,
) -> dict[str, object]:
    ticket = _required_str(event, "ticket")
    ticket_id = gd.ticket_id_for(ticket)
    state = dispatcher.load_ticket_state(ticket_id)
    if state is None:
        raise StuckDispatchError("dispatcher record is stuck after dispatching with no state")
    run_state = state.get("state")
    if run_state == "running":
        if dispatcher.pid_alive(state.get("child_pid")):
            raise StuckDispatchError("dispatcher already has a live Writer")
        raise StuckDispatchError("dispatcher record is stuck (running with no live PID)")
    event["dispatcher_run_state"] = run_state
    event["dispatcher_session_id"] = state.get("session_id")
    event["implementation_commit"] = state.get("implementation_commit")
    event["worktree"] = state.get("worktree")
    event["branch"] = state.get("branch")
    event["child_completed"] = run_state in CHILD_COMPLETED_STATES
    event["diagnostic"] = gd.redact_secrets(str(state.get("diagnostic") or run_state))[:500]
    _set_state(event, "dispatched")
    _write_event(paths, event)
    return event


def _step_push(
    event: dict[str, object],
    *,
    paths: ControllerPaths,
    git: GitRunner,
    repo: Path,
) -> dict[str, object]:
    ticket = _required_str(event, "ticket")
    ticket_id = gd.ticket_id_for(ticket)
    worktree_raw = event.get("worktree")
    impl = event.get("implementation_commit")
    branch = event.get("branch")
    if not isinstance(worktree_raw, str) or worktree_raw == "":
        raise ControllerError("dispatcher result omitted worktree")
    if not isinstance(impl, str) or _SHA.fullmatch(impl) is None:
        raise ControllerError("dispatcher result omitted implementation commit")
    expected_branch = f"dispatcher/{ticket_id}"
    if branch != expected_branch:
        raise ControllerError("refusing to publish a non-ticket branch")
    worktree = Path(worktree_raw)
    _require_publication_worktree(git, worktree, expected_branch, impl)
    remote_sha = _remote_branch_sha(git, repo, ticket_id)
    if remote_sha == impl:
        event["published_sha"] = impl
        event["diagnostic"] = "ticket branch already published"
        _set_state(event, "branch_pushed")
        _write_event(paths, event)
        _write_publication(paths, ticket_id, event)
        return event
    recorded = _recorded_published_sha(event, paths, ticket_id)
    if recorded is None and remote_sha is not None:
        raise ControllerError("refusing initial publish over an existing ticket branch")
    args = build_push_args(ticket_id, lease_sha=recorded)
    result = git.run(worktree, args)
    if result.returncode != 0:
        detail = gd.redact_secrets((result.stderr or result.stdout).strip())[:200]
        raise ControllerError(f"ticket branch push failed: {detail}")
    event["published_sha"] = impl
    event["diagnostic"] = "ticket branch published"
    _set_state(event, "branch_pushed")
    _write_event(paths, event)
    _write_publication(paths, ticket_id, event)
    return event


def _step_pr(
    event: dict[str, object],
    *,
    paths: ControllerPaths,
    github: GitHubClient,
    config: QueueConfig,
) -> dict[str, object]:
    ticket = _required_str(event, "ticket")
    ticket_id = gd.ticket_id_for(ticket)
    head = f"{GITHUB_OWNER}:dispatcher/{ticket_id}"
    number = _recorded_pr_number(event, paths, ticket_id)
    if isinstance(number, int):
        pull = github.get_pull_request(number)
    else:
        existing = github.list_open_pulls_for_head(head)
        if len(existing) > 1:
            raise ControllerError("multiple open pull requests for ticket branch")
        if len(existing) == 1:
            pull = existing[0]
        else:
            pull = github.create_draft_pull_request(
                title=f"{ticket_id}: {ticket}",
                body=_pr_body(event),
                head=f"dispatcher/{ticket_id}",
                base="main",
            )
    _require_valid_pr(pull, ticket_id, config)
    event["pr_number"] = pull.number
    event["diagnostic"] = "draft pull request ensured"
    _set_state(event, "pr_ensured")
    _write_event(paths, event)
    _write_publication(paths, ticket_id, event)
    return event


def _step_result(
    event: dict[str, object],
    *,
    paths: ControllerPaths,
    github: GitHubClient,
    config: QueueConfig,
) -> dict[str, object]:
    body = build_result_comment(event)
    posted = github.post_issue_comment(config.queue_issue_number, body)
    event["result_comment_id"] = posted.comment_id
    _set_state(event, "result_posted")
    _write_event(paths, event)
    return event


def _step_done(event: dict[str, object], paths: ControllerPaths) -> dict[str, object]:
    _set_state(event, "done")
    _write_event(paths, event)
    return event


def _finish_unauthorized(
    event: dict[str, object],
    diagnostic: str,
    *,
    paths: ControllerPaths,
) -> PollResult:
    event["diagnostic"] = diagnostic
    if str(event.get("processing_state")) != "done":
        _set_state(event, "done")
        _write_event(paths, event)
    return _poll_from_event(event, dispatched=False, published=False)


def _hold_stuck(
    event: dict[str, object],
    diagnostic: str,
    *,
    paths: ControllerPaths,
) -> PollResult:
    event["diagnostic"] = diagnostic
    event["updated_at"] = _now()
    _write_event(paths, event)
    return _poll_from_event(event, dispatched=False, published=False)


def _finish_refusal(
    event: dict[str, object],
    diagnostic: str,
    *,
    paths: ControllerPaths,
    github: GitHubClient,
    config: QueueConfig,
    dispatched: bool,
) -> PollResult:
    event["diagnostic"] = diagnostic
    if str(event.get("processing_state")) not in {"result_posted", "done"}:
        try:
            posted = github.post_issue_comment(
                config.queue_issue_number,
                build_result_comment(event),
            )
            event["result_comment_id"] = posted.comment_id
            _set_state(event, "result_posted")
            _write_event(paths, event)
        except ControllerError:
            _write_event(paths, event)
            raise
    if str(event.get("processing_state")) != "done":
        _set_state(event, "done")
        _write_event(paths, event)
    return _poll_from_event(event, dispatched=dispatched, published=_is_published(event))


def _claim_event(comment: IssueComment, paths: ControllerPaths) -> dict[str, object]:
    existing = _load_event(paths, comment.comment_id)
    if existing is not None:
        if str(existing.get("processing_state")) != "done":
            actual = body_sha256(normalize_comment_body(comment.body))
            if actual != existing.get("body_sha256"):
                raise ControllerError("claimed body hash mismatch")
        return existing
    normalized = normalize_comment_body(comment.body)
    event = _empty_event(comment, body_sha256(normalized))
    if comment.updated_at != comment.created_at:
        event["diagnostic"] = "comment was edited at ingest"
        _write_event(paths, event)
        raise ControllerError("comment was edited at ingest")
    if (
        comment.user_type != ALLOWED_ACTOR_TYPE
        or comment.user_id != ALLOWED_ACTOR_ID
        or comment.user_login != ALLOWED_ACTOR_LOGIN
    ):
        event["diagnostic"] = "actor is not allowlisted"
        _write_event(paths, event)
        raise UnauthorizedActorError("actor is not allowlisted")
    try:
        mode, ticket, start = parse_bootie_command(normalized)
    except ControllerError as exc:
        event["diagnostic"] = gd.redact_secrets(str(exc))[:500]
        _write_event(paths, event)
        raise
    event["mode"] = mode
    event["ticket"] = ticket
    event["start_commit"] = start
    event["writer"] = f"bootie/{gd.ticket_id_for(ticket)}"
    _write_event(paths, event)
    return event


def _claim_event_for_failure(
    comment: IssueComment,
    paths: ControllerPaths,
    diagnostic: str,
) -> dict[str, object]:
    existing = _load_event(paths, comment.comment_id)
    if existing is not None:
        existing["diagnostic"] = diagnostic
        return existing
    event = _empty_event(comment, body_sha256(normalize_comment_body(comment.body)))
    event["diagnostic"] = diagnostic
    _write_event(paths, event)
    return event


def _empty_event(comment: IssueComment, digest: str) -> dict[str, object]:
    now = _now()
    return {
        "comment_id": comment.comment_id,
        "ticket": None,
        "start_commit": None,
        "mode": None,
        "writer": None,
        "processing_state": "claimed",
        "body_sha256": digest,
        "created_at": comment.created_at,
        "actor_id": comment.user_id,
        "actor_login": comment.user_login,
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
        "claimed_at": now,
        "updated_at": now,
    }


def _apply_dispatch_result(event: dict[str, object], result: gd.DispatchResult) -> None:
    event["child_completed"] = result.child_completed
    event["dispatcher_run_state"] = result.run_state
    event["dispatcher_session_id"] = result.session_id
    event["implementation_commit"] = result.implementation_commit
    event["worktree"] = result.worktree
    event["branch"] = result.branch
    event["diagnostic"] = gd.redact_secrets(result.diagnostic)[:500]


def _oldest_unprocessed(
    comments: Sequence[IssueComment],
    paths: ControllerPaths,
) -> IssueComment | None:
    candidates: list[IssueComment] = []
    for comment in comments:
        existing = _load_event(paths, comment.comment_id)
        if existing is not None and str(existing.get("processing_state")) == "done":
            continue
        if existing is None and not is_command_like(comment.body):
            continue
        candidates.append(comment)
    if not candidates:
        return None
    return min(candidates, key=lambda item: (item.created_at, item.comment_id))


def _require_observatory_repo(paths: ControllerPaths, git: GitRunner) -> Path:
    repo = paths.canonical_repo_root.resolve()
    toplevel = git.run(repo, ["rev-parse", "--show-toplevel"])
    if toplevel.returncode != 0:
        raise ControllerError("repository identity is not Observatory")
    if Path(toplevel.stdout.strip()).resolve() != repo:
        raise ControllerError("repository identity is not Observatory")
    origin = git.run(repo, ["remote", "get-url", "origin"])
    if origin.returncode != 0 or not gd.origin_is_observatory(origin.stdout.strip()):
        raise ControllerError("repository identity is not Observatory")
    if not gd.origin_is_observatory(paths.canonical_origin):
        raise ControllerError("repository identity is not Observatory")
    return repo


def _require_github_queue(github: GitHubClient, config: QueueConfig) -> None:
    repo = github.get_repository()
    if repo.owner != GITHUB_OWNER or repo.name != GITHUB_REPO:
        raise ControllerError("GitHub repository identity is not Observatory")
    if repo.repository_id != config.github_repository_id:
        raise ControllerError("GitHub repository id does not match commissioned queue")
    issue = github.get_issue(config.queue_issue_number)
    if issue.number != config.queue_issue_number:
        raise ControllerError("queue issue does not match commissioned identity")
    if issue.repository_id != config.github_repository_id:
        raise ControllerError("queue issue does not match commissioned identity")


def _require_clean(repo: Path, git: GitRunner) -> None:
    status = git.run(repo, ["status", "--porcelain"])
    if status.returncode != 0:
        raise ControllerError("unable to read primary checkout status")
    if status.stdout.strip() != "":
        raise ControllerError("primary checkout is dirty")


def _fetch_main(repo: Path, git: GitRunner) -> None:
    args = build_fetch_args()
    result = git.run(repo, args)
    if result.returncode != 0:
        detail = gd.redact_secrets((result.stderr or result.stdout).strip())[:200]
        raise ControllerError(f"narrow origin/main fetch failed: {detail}")


def _require_start_on_origin_main(repo: Path, git: GitRunner, start: str) -> None:
    exists = git.run(repo, ["cat-file", "-t", start])
    if exists.returncode != 0 or exists.stdout.strip() != "commit":
        raise ControllerError(f"start commit {start} does not exist")
    ancestor = git.run(repo, ["merge-base", "--is-ancestor", start, "refs/remotes/origin/main"])
    if ancestor.returncode != 0:
        raise ControllerError("start commit is not an ancestor of origin/main")


def _require_accepted_ticket(repo: Path, git: GitRunner, start: str, ticket: str) -> None:
    shown = git.run(repo, ["show", f"{start}:{ticket}"])
    if shown.returncode != 0:
        raise ControllerError(f"ticket {ticket} does not exist at {start}")
    if _ACCEPTED_STATUS.search(shown.stdout) is None:
        raise ControllerError(f"ticket {ticket} is not accepted at {start}")


def _refuse_stuck_or_live(dispatcher: DispatcherSeam, ticket_id: str) -> None:
    state = dispatcher.load_ticket_state(ticket_id)
    if state is None:
        return
    if state.get("state") == "running":
        if dispatcher.pid_alive(state.get("child_pid")):
            raise ControllerError("dispatcher already has a live Writer")
        raise ControllerError("dispatcher record is stuck (running with no live PID)")


def _require_publication_worktree(
    git: GitRunner,
    worktree: Path,
    expected_branch: str,
    implementation_commit: str,
) -> None:
    if not worktree.is_dir():
        raise ControllerError("recorded worktree path does not exist")
    branch = git.run(worktree, ["rev-parse", "--abbrev-ref", "HEAD"])
    if branch.returncode != 0 or branch.stdout.strip() != expected_branch:
        raise ControllerError("publication worktree is not on the ticket branch")
    head = git.run(worktree, ["rev-parse", "HEAD"])
    sha = head.stdout.strip().lower()
    if head.returncode != 0 or _SHA.fullmatch(sha) is None or sha != implementation_commit:
        raise ControllerError("publication worktree HEAD does not match implementation commit")
    status = git.run(worktree, ["status", "--porcelain"])
    if status.returncode != 0:
        raise ControllerError("unable to read publication worktree status")
    if status.stdout.strip() != "":
        raise ControllerError("publication worktree is dirty")


def _remote_branch_sha(git: GitRunner, repo: Path, ticket_id: str) -> str | None:
    ref = f"refs/heads/dispatcher/{ticket_id}"
    result = git.run(repo, ["ls-remote", "origin", ref])
    if result.returncode != 0:
        detail = gd.redact_secrets((result.stderr or result.stdout).strip())[:200]
        raise ControllerError(f"ticket branch lookup failed: {detail}")
    line = result.stdout.strip().splitlines()
    if not line:
        return None
    sha = line[0].split()[0].lower()
    if _SHA.fullmatch(sha) is None:
        raise ControllerError("ticket branch lookup returned a malformed SHA")
    return sha


def _recorded_published_sha(
    event: Mapping[str, object],
    paths: ControllerPaths,
    ticket_id: str,
) -> str | None:
    value = event.get("published_sha")
    if isinstance(value, str) and _SHA.fullmatch(value) is not None:
        return value
    publication = _load_publication(paths, ticket_id)
    if publication is None:
        return None
    recorded = publication.get("published_sha")
    if isinstance(recorded, str) and _SHA.fullmatch(recorded) is not None:
        return recorded
    return None


def _recorded_pr_number(
    event: Mapping[str, object],
    paths: ControllerPaths,
    ticket_id: str,
) -> int | None:
    value = event.get("pr_number")
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    publication = _load_publication(paths, ticket_id)
    if publication is None:
        return None
    recorded = publication.get("pr_number")
    if isinstance(recorded, int) and not isinstance(recorded, bool) and recorded > 0:
        return recorded
    return None


def _require_valid_pr(pull: PullRequestInfo, ticket_id: str, config: QueueConfig) -> None:
    if pull.state != "open":
        raise ControllerError("stored pull request is closed")
    if pull.merged:
        raise ControllerError("stored pull request is merged")
    if not pull.draft:
        raise ControllerError("stored pull request is not a draft")
    if pull.base_ref != "main" or pull.base_owner != GITHUB_OWNER or pull.base_name != GITHUB_REPO:
        raise ControllerError("stored pull request base is not Observatory main")
    if pull.head_owner != GITHUB_OWNER or pull.head_ref != f"dispatcher/{ticket_id}":
        raise ControllerError("stored pull request head is not the ticket branch")
    if pull.head_name != GITHUB_REPO:
        raise ControllerError("stored pull request head is not Observatory")
    if pull.head_is_fork:
        raise ControllerError("stored pull request head is a fork")
    if (
        pull.base_repository_id != config.github_repository_id
        or pull.head_repository_id != config.github_repository_id
    ):
        raise ControllerError("stored pull request is not the commissioned Observatory repository")
    expected_url = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/pull/{pull.number}"
    if pull.html_url != expected_url:
        raise ControllerError("stored pull request URL is not Observatory")


def _pr_body(event: Mapping[str, object]) -> str:
    return "\n".join(
        [
            f"ticket: {event.get('ticket') or 'none'}",
            f"start_commit: {event.get('start_commit') or 'none'}",
            f"mode: {event.get('mode') or 'none'}",
            f"writer: {event.get('writer') or 'none'}",
            f"implementation_commit: {event.get('implementation_commit') or 'none'}",
            f"event_comment_id: {event.get('comment_id') or 'none'}",
        ]
    )


def _poll_from_event(
    event: Mapping[str, object],
    *,
    dispatched: bool,
    published: bool,
) -> PollResult:
    comment_id = event.get("comment_id")
    pr_number = event.get("pr_number")
    impl = event.get("implementation_commit")
    return PollResult(
        processed=True,
        comment_id=comment_id if isinstance(comment_id, int) else None,
        state=str(event.get("processing_state")),
        diagnostic=str(event.get("diagnostic") or ""),
        dispatched=dispatched,
        published=published,
        implementation_commit=impl if isinstance(impl, str) else None,
        pr_number=pr_number if isinstance(pr_number, int) else None,
    )


def _already_dispatched(event: Mapping[str, object]) -> bool:
    state = str(event.get("processing_state"))
    if state not in PROCESSING_STATES:
        return False
    return PROCESSING_STATES.index(state) >= PROCESSING_STATES.index("dispatched")


def _is_published(event: Mapping[str, object]) -> bool:
    state = str(event.get("processing_state"))
    if state not in PROCESSING_STATES:
        return False
    if PROCESSING_STATES.index(state) < PROCESSING_STATES.index("branch_pushed"):
        return False
    return event.get("child_completed") is True and isinstance(event.get("published_sha"), str)


def _required_str(event: Mapping[str, object], field: str) -> str:
    value = event.get(field)
    if not isinstance(value, str) or value.strip() == "":
        raise ControllerError(f"{field} is missing")
    return value


def _require_ticket_id(ticket_id: str) -> None:
    if _TICKET_ID.fullmatch(ticket_id) is None:
        raise ControllerError("ticket id is not a safe branch suffix")


def _set_state(event: dict[str, object], new_state: str) -> None:
    old = str(event.get("processing_state") or "claimed")
    if old not in PROCESSING_STATES or new_state not in PROCESSING_STATES:
        raise ControllerError("unknown processing state")
    if PROCESSING_STATES.index(new_state) < PROCESSING_STATES.index(old):
        raise ControllerError("state must move monotonically")
    event["processing_state"] = new_state
    event["updated_at"] = _now()


def _event_path(paths: ControllerPaths, comment_id: int) -> Path:
    return paths.events_dir / f"{comment_id}.json"


def _publication_path(paths: ControllerPaths, ticket_id: str) -> Path:
    return paths.tickets_dir / f"{ticket_id}.json"


def _load_event(paths: ControllerPaths, comment_id: int) -> dict[str, object] | None:
    path = _event_path(paths, comment_id)
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ControllerError(f"event {comment_id} is unreadable") from exc
    if not isinstance(payload, dict):
        raise ControllerError(f"event {comment_id} is unreadable")
    return payload


def _load_publication(paths: ControllerPaths, ticket_id: str) -> dict[str, object] | None:
    path = _publication_path(paths, ticket_id)
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ControllerError(f"publication state for {ticket_id} is unreadable") from exc
    if not isinstance(payload, dict):
        raise ControllerError(f"publication state for {ticket_id} is unreadable")
    return payload


def _write_event(paths: ControllerPaths, event: Mapping[str, object]) -> None:
    _refuse_secret_fields(event)
    closed = {field: event.get(field) for field in EVENT_FIELDS}
    diagnostic = closed.get("diagnostic")
    if isinstance(diagnostic, str):
        closed["diagnostic"] = gd.redact_secrets(diagnostic)[:500]
    _atomic_write(_event_path(paths, int(cast(int, closed["comment_id"]))), closed)


def _write_publication(paths: ControllerPaths, ticket_id: str, event: Mapping[str, object]) -> None:
    existing = _load_publication(paths, ticket_id) or {}
    published_sha = event.get("published_sha")
    if not isinstance(published_sha, str) or _SHA.fullmatch(published_sha) is None:
        published_sha = existing.get("published_sha")
    pr_number = event.get("pr_number")
    if not isinstance(pr_number, int) or isinstance(pr_number, bool) or pr_number <= 0:
        pr_number = existing.get("pr_number")
    payload = {
        "ticket": event.get("ticket") or existing.get("ticket"),
        "published_sha": published_sha,
        "pr_number": pr_number,
        "updated_at": _now(),
    }
    _refuse_secret_fields(payload)
    _atomic_write(_publication_path(paths, ticket_id), payload)


def _refuse_secret_fields(payload: Mapping[str, object]) -> None:
    for key in payload:
        lowered = str(key).lower()
        if any(marker in lowered for marker in gd.SECRET_FIELD_MARKERS):
            raise ControllerError(f"refusing to persist secret-like state field {key}")


def _atomic_write(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def _now() -> str:
    return datetime.now(UTC).isoformat()


@contextmanager
def _controller_lock(paths: ControllerPaths) -> Iterator[None]:
    paths.lock_dir.mkdir(parents=True, exist_ok=True)
    handle: TextIO = (paths.lock_dir / "controller.lock").open("a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        handle.close()
        raise ControllerError("controller --once is already running") from exc
    try:
        yield
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def _repository_from_api(payload: object) -> RepositoryInfo:
    if not isinstance(payload, dict):
        raise ControllerError("GitHub repository payload is unreadable")
    repo_id = payload.get("id")
    name = payload.get("name")
    owner_obj = payload.get("owner")
    login = owner_obj.get("login") if isinstance(owner_obj, dict) else None
    if not isinstance(repo_id, int) or not isinstance(name, str) or not isinstance(login, str):
        raise ControllerError("GitHub repository payload is unreadable")
    return RepositoryInfo(repository_id=repo_id, owner=login, name=name)


def _comment_from_api(payload: object) -> IssueComment:
    if not isinstance(payload, dict):
        raise ControllerError("GitHub comment payload is unreadable")
    comment_id = payload.get("id")
    body = payload.get("body")
    created = payload.get("created_at")
    updated = payload.get("updated_at")
    user = payload.get("user")
    if not isinstance(user, dict):
        raise ControllerError("GitHub comment payload is unreadable")
    user_id = user.get("id")
    login = user.get("login")
    user_type = user.get("type")
    if (
        not isinstance(comment_id, int)
        or not isinstance(body, str)
        or not isinstance(created, str)
        or not isinstance(updated, str)
        or not isinstance(user_id, int)
        or not isinstance(login, str)
        or not isinstance(user_type, str)
    ):
        raise ControllerError("GitHub comment payload is unreadable")
    return IssueComment(
        comment_id=comment_id,
        user_id=user_id,
        user_login=login,
        user_type=user_type,
        body=body,
        created_at=created,
        updated_at=updated,
    )


def _merged_from_api(payload: Mapping[str, object]) -> bool:
    has_merged = "merged" in payload
    has_merged_at = "merged_at" in payload
    if not has_merged and not has_merged_at:
        raise ControllerError("GitHub pull request payload is unreadable")
    merged = payload.get("merged") if has_merged else None
    merged_at = payload.get("merged_at") if has_merged_at else None
    merged_at_set = isinstance(merged_at, str) and merged_at.strip() != ""
    if has_merged:
        if not isinstance(merged, bool):
            raise ControllerError("GitHub pull request payload is unreadable")
        if merged:
            return True
        if merged_at_set:
            raise ControllerError("GitHub pull request merged fields disagree")
        if merged_at is not None and not isinstance(merged_at, str):
            raise ControllerError("GitHub pull request payload is unreadable")
        return False
    if merged_at is None:
        return False
    if merged_at_set:
        return True
    raise ControllerError("GitHub pull request payload is unreadable")


def _pull_from_api(payload: object) -> PullRequestInfo:
    if not isinstance(payload, dict):
        raise ControllerError("GitHub pull request payload is unreadable")
    number = payload.get("number")
    state = payload.get("state")
    draft = payload.get("draft")
    html_url = payload.get("html_url")
    base = payload.get("base")
    head = payload.get("head")
    if not isinstance(base, dict) or not isinstance(head, dict):
        raise ControllerError("GitHub pull request payload is unreadable")
    if (
        not isinstance(number, int)
        or not isinstance(state, str)
        or not isinstance(draft, bool)
        or not isinstance(html_url, str)
    ):
        raise ControllerError("GitHub pull request payload is unreadable")
    return PullRequestInfo(
        number=number,
        state=state,
        draft=draft,
        merged=_merged_from_api(payload),
        html_url=html_url,
        base_ref=_repo_ref(base, "ref"),
        base_owner=_nested_login(base),
        base_name=_nested_repo_name(base),
        base_repository_id=_nested_repo_id(base),
        head_ref=_repo_ref(head, "ref"),
        head_owner=_nested_login(head),
        head_name=_nested_repo_name(head),
        head_repository_id=_nested_repo_id(head),
        head_is_fork=_nested_fork(head),
    )


def _repo_ref(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise ControllerError("GitHub pull request payload is unreadable")
    return value


def _nested_login(payload: Mapping[str, object]) -> str:
    user = payload.get("user")
    if isinstance(user, dict) and isinstance(user.get("login"), str):
        return str(user["login"])
    repo = payload.get("repo")
    if isinstance(repo, dict):
        owner = repo.get("owner")
        if isinstance(owner, dict) and isinstance(owner.get("login"), str):
            return str(owner["login"])
    raise ControllerError("GitHub pull request payload is unreadable")


def _nested_repo_name(payload: Mapping[str, object]) -> str:
    repo = payload.get("repo")
    if isinstance(repo, dict) and isinstance(repo.get("name"), str):
        return str(repo["name"])
    raise ControllerError("GitHub pull request payload is unreadable")


def _nested_repo_id(payload: Mapping[str, object]) -> int:
    repo = payload.get("repo")
    repo_id = repo.get("id") if isinstance(repo, dict) else None
    if isinstance(repo_id, int) and not isinstance(repo_id, bool):
        return repo_id
    raise ControllerError("GitHub pull request payload is unreadable")


def _nested_fork(payload: Mapping[str, object]) -> bool:
    repo = payload.get("repo")
    if not isinstance(repo, dict) or "fork" not in repo:
        raise ControllerError("GitHub pull request payload is unreadable")
    fork = repo.get("fork")
    if not isinstance(fork, bool):
        raise ControllerError("GitHub pull request payload is unreadable")
    return fork


if __name__ == "__main__":
    raise SystemExit(main())
