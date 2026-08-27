# OPS-04 — GitHub queue and draft-PR control plane

**Status:** review
**Owner:** [GROK] implementation / [GPT] Steward review
**Kind:** development-workflow tooling; not Observatory acquisition/runtime behavior
**Blocked by:** implementation unblocked — OPS-03 dispatcher is closed and live-smoke proven; live GitHub commissioning remains separate
**Approved by:** [CHAZ] to proceed with the next Bootie Factory control-plane layer
**Start commit:** 4a1ff6e2f49ba60542015ff94eaf0760b3ae9df7

## Purpose

Replace routine phone copy/paste dispatch with the smallest durable GitHub event-bus layer
that can request an already-authorized Writer run on the VPS and publish its result for
review.

The control plane does **not** create implementation authority. A GitHub event may request
work only when it resolves to a finally accepted repository ticket and an exact Steward
start commit that is present on canonical `origin/main`. The OPS-03 dispatcher remains the
execution gate and one-Writer authority.

The intended minimum useful flow is:

```text
accepted ticket + exact Steward start commit on origin/main
  -> command comment in one dedicated GitHub queue issue
  -> VPS controller validates actor / command / remote-main ancestry
  -> OPS-03 dispatcher implement or resume
  -> successful bounded Writer commit
  -> controller publishes only that ticket branch
  -> controller creates or updates one draft PR to main
  -> controller posts bounded result state back to the queue issue
  -> Steward review / Product merge-push gates remain separate
```

No webhook, inbound VPS listener, GitHub Actions runner, autonomous reviewer swarm,
automatic merge, or automatic `main` push belongs in this ticket.

## Why this shape

The VPS already has the useful execution substrate: canonical repository, authenticated
Grok Build session, isolated dispatcher worktrees, same-session resume, fail-closed
completion checks, and a real installed-CLI smoke. The next bottleneck is coordination,
not another agent framework.

Polling one dedicated GitHub issue keeps GitHub as a durable, inspectable event log without
opening a public service on the VPS or duplicating repository tickets into GitHub issues.
Repository ticket files remain authority; the queue issue contains operational commands and
results only.

Draft PR publication makes the Writer result durable and reviewable without allowing the
Writer itself to use GitHub or weakening OPS-03's push/network denies.

## Proposed command contract

One repository-owned GitHub issue is configured as the Bootie Factory queue. A command is a
new issue comment by an explicitly allowlisted GitHub actor using exactly one of:

```text
/bootie implement tickets/<ticket>.md <40-hex-start-sha>
/bootie resume tickets/<ticket>.md <40-hex-start-sha>
```

Initial production actor allowlist is the repository owner `St3nch` only. The technical
review must verify the actual GitHub owner/auth identity before final acceptance rather than
assuming the display name or local Git identity is equivalent.

The comment's GitHub immutable comment ID is the event identity. Re-polling the same comment
must never dispatch it twice.

Labels, issue title, notification delivery, PR state, or a queue comment by themselves are
never implementation authority.

## Proposed controller behavior

The implementation is a small controller under `tools/` that reuses the accepted OPS-03
dispatcher instead of reimplementing Writer execution.

For each unprocessed command comment, the controller must fail closed unless all of these
hold before dispatch:

1. repository identity is exactly Observatory;
2. queue issue repository/number matches configured production values;
3. comment actor is allowlisted;
4. command grammar is exact and contains no shell fragments or caller-supplied argv;
5. ticket path is a normalized `tickets/<file>.md` path;
6. start value is an exact lowercase/normalized 40-hex commit;
7. a fresh read-only `git fetch origin` succeeds;
8. start commit exists locally and is an ancestor of `origin/main`;
9. the ticket object at that exact start commit is `Status: accepted`;
10. local canonical `main` is clean;
11. OPS-03 dispatcher state permits the requested `implement` or `resume` operation.

The controller then calls/imports the OPS-03 dispatcher with the exact ticket, start SHA,
mode, and a stable Writer identity derived from the ticket/event. It must not directly
invoke Grok around the dispatcher.

## GitHub publication boundary

GitHub mutation happens only **after** the dispatcher reports a successful implementation
postcondition.

- Publish only the dispatcher-owned ticket branch for the requested ticket.
- Never push `main`, another ticket branch, tags, or arbitrary refs.
- Initial publication is an ordinary non-force branch push.
- A successful same-Writer remediation may require replacing the already-published ticket
  commit because OPS-03 requires exactly one implementation commit from the fixed start.
  If technical review confirms this is necessary, the controller may use
  **`--force-with-lease` only for that exact ticket branch and only when the expected remote
  old SHA equals the controller's recorded prior published SHA**. Plain `--force` is
  forbidden.
- Create at most one open **draft** PR for the ticket branch targeting `main`; later resume
  updates that same PR/branch rather than opening duplicates.
- The controller never marks the PR ready, approves it, merges it, closes it as accepted,
  or pushes a Steward closure commit.
- PR title/body are generated from trusted local ticket/event fields; issue comment text is
  not forwarded as arbitrary Markdown or command text.

The queue issue receives one bounded result comment containing ticket, start SHA, mode,
dispatcher state, implementation commit when known, branch, PR number/URL when known, and a
short non-secret diagnostic. Do not post raw Grok text, tool inputs, environment, logs, or
credentials.

## GitHub/auth boundary

The controller may use the already-authenticated local `gh` CLI or an equivalently narrow
GitHub client only for the exact queue-read, result-comment, branch/PR publication actions
accepted by this ticket. It must not read or persist the underlying GitHub token.

Grok Writer children remain unable to use `gh`, Git network operations, or GitHub tokens;
OPS-03 environment stripping and deny rules remain unchanged.

Ordinary tests use a fake GitHub boundary and fake dispatcher boundary. They must be unable
to contact GitHub or invoke real Grok.

## State and crash behavior

Controller state lives outside the repository under a dedicated subdirectory of
`~/.local/share/vedaops/observatory/`, separate from Evidence and from OPS-03 Writer state.

Persist only bounded operational state needed for idempotency and recovery, including:

- immutable GitHub comment/event ID;
- ticket and start SHA;
- requested mode;
- processing state;
- dispatcher result identity/session reference when available;
- last successfully published branch SHA;
- draft PR number when known;
- bounded timestamps/diagnostic.

Crash/restart must not silently launch a second Writer or create a second PR. An event that
is ambiguous after a crash is reconciled from local dispatcher state plus GitHub branch/PR
state before any repeat mutation.

The technical review must challenge whether event state needs an explicit operator retry
or whether replaying the same exact command comment can safely mean resume. Do not guess
this in implementation.

## Polling/runtime boundary

This ticket implements and proves the controller's deterministic **single poll/once** seam
and the GitHub/dispatcher/publication state machine. A persistent systemd service/timer is
not required unless technical review shows that omitting it would make the control-plane
proof meaningless.

If service installation remains deferred, the next OPS ticket may install the proven
controller as a VPS user service with a modest polling cadence. Do not add inbound network
listeners merely to avoid that later ticket.

## Changed-path allowlist

Expected implementation footprint:

- one small GitHub control-plane module/entrypoint under `tools/`;
- one focused test module under `tests/`;
- this ticket for implementer Start commit, Status=`review`, and Implementation report.

Do not modify `src/observatory/`, migrations, Evidence code, API code, provider adapters,
authority files, existing tickets, `.github/`, CI, `pyproject.toml`, or OPS-03 dispatcher
semantics unless the pre-implementation review identifies a concrete blocker and the
Steward reconciles the ticket first.

## Required deterministic proofs

Zero-network tests must prove at minimum:

- non-allowlisted actor refuses before dispatcher/GitHub mutation;
- malformed command/ticket/SHA refuses;
- duplicate GitHub comment ID is idempotent and never launches a second Writer;
- start not reachable from freshly represented `origin/main` refuses;
- ticket not accepted at the exact start object refuses;
- controller passes the exact ticket/start/mode into the OPS-03 dispatcher seam;
- dispatcher non-success/cancelled/failed result never pushes or opens a PR;
- successful implementation publishes only the exact ticket branch;
- initial publication never force-pushes;
- remediation publication, if accepted after review, uses force-with-lease with the exact
  recorded expected old SHA and refuses mismatch;
- one ticket has at most one open draft PR and resume updates/reuses it;
- controller cannot push `main`, merge, approve, mark-ready, or close the ticket as done;
- result comments are bounded and redact/reject secret-like data;
- crash/restart reconciliation cannot silently duplicate dispatch or PR creation;
- tests cannot invoke real `gh`, GitHub network, Grok/xAI, provider transport, DNS,
  production PostgreSQL, or Evidence mutation;
- Ruff and touched-path mypy pass.

## Required pre-implementation review

Before final acceptance, [GROK] performs a read-only code-first review of this provisional
ticket plus current `AGENTS.md`, closed OPS-03, `tools/grok_dispatcher.py`, relevant tests,
the actual installed `gh` CLI help/auth status, and read-only repository GitHub metadata.

Read-only GitHub inspection is permitted for this review; no issue/comment/label/branch/PR
mutation, no credential display, and no repository edit.

The review must challenge:

- whether one dedicated issue + comment commands is the smallest durable event bus;
- exact authenticated GitHub actor/owner identity and least privilege available on VPS;
- polling versus webhook/Actions/self-hosted-runner tradeoffs for this VPS;
- whether `origin/main` freshness/ancestry can false-green;
- whether import-versus-subprocess reuse of OPS-03 preserves its gates;
- command/event parser injection and replay risks;
- crash windows around dispatch, branch push, PR create, and result comment;
- whether remediation really requires force-with-lease and how to bind its expected SHA;
- whether GitHub branch/PR lookup can accidentally operate on a foreign ticket/ref;
- whether one `--once` controller is enough for OPS-04 and systemd belongs next;
- whether the changed-path footprint is sufficient;
- any way credentials, raw Grok output, or arbitrary issue text could leak to GitHub.

Return exactly one: `READY`, `READY_AFTER_TICKET_RECONCILIATION`, or `NOT_READY`.
Do not implement or mutate GitHub/repository state during review.

## Hard boundaries

- GitHub is operational relay/state, never ticket/Steward/Product authority.
- Exact finally accepted ticket + exact Steward start SHA on canonical remote main remain
  mandatory before dispatch.
- Exactly one [GROK] Writer per accepted ticket; same Writer owns remediation.
- No automatic merge, `main` push, Steward closure, or Product acceptance.
- No provider, DNS, Evidence, paid, production credential, or production PostgreSQL work.
- No generic multi-agent framework, webhook server, or GitHub Actions runner in this slice.
- No real GitHub mutations from ordinary tests.

## Pre-implementation review reconciliation

The read-only review at provisional commit
`7afc1f2602aca9f311bf6a08360ca33eb855875f` returned
`READY_AFTER_TICKET_RECONCILIATION`. The rules below are normative and supersede any
earlier provisional wording in this ticket where there is conflict.

### Queue and actor identity

- The production queue is one exact `(repository_id, issue_number)` pair recorded during a
  one-time operator commissioning step outside the repository. Production refuses without
  that record. Repository or issue identity is not a per-run CLI argument, and issue-title
  search is not an identity mechanism.
- The production actor is GitHub numeric user id `54292644`, login `St3nch`,
  `user.type=User`. Numeric id is primary. Local Git identity, display name, authenticated
  host account, bots, and login-only matches are not actor authority.
- A comment id is an event handle, not immutable content. Accept only comments whose first
  observed `updated_at == created_at`, persist the exact normalized body SHA-256 when
  claimed, and refuse any later body-hash mismatch.

### Exact command and remote-main gate

- After CRLF normalization and outer whitespace stripping, the entire body must match
  `^/bootie (implement|resume) tickets/[A-Za-z0-9._-]+\.md [0-9a-f]{40}$`.
  Added prose, quotes, HTML, mentions, shell fragments, and non-lowercase/non-40-hex SHA
  syntax refuse.
- Reuse OPS-03 ticket/SHA normalization before dispatch. Never shell-interpolate comment
  text; every subprocess uses a closed argv list.
- Recheck Observatory origin identity, then fetch only
  `refs/heads/main:refs/remotes/origin/main`. Generic `git fetch origin`, pull, or stale
  remote-main fallback is forbidden.
- The start commit must be an ancestor of freshly updated `refs/remotes/origin/main`, not
  merely local `main`, and `git show <start>:<ticket>` must be accepted before dispatch.
- Controller Git fetch/push is separate from OPS-03 because OPS-03 deliberately forbids
  those verbs. Grok execution still goes only through OPS-03 `dispatch()` /
  `invoke_real_grok` or its closed-argv CLI equivalent.
- Writer identity is ticket-stable: `bootie/<ticket-id>`. Comment/event id is never part of
  Writer identity.

### Idempotency and crash state

- One exclusive controller flock prevents overlapping `--once` dispatch.
- Persist event state before side effects and move monotonically through
  `claimed -> dispatching -> dispatched -> branch_pushed -> pr_ensured -> result_posted -> done`.
  Writes are atomic/fail-closed.
- Replaying one comment id may continue only that event's already-recorded publication or
  result work and must never call OPS-03 a second time. `resume` requires a new exact
  `/bootie resume ...` comment.
- A dispatcher record that is `running` with no live PID is reported as stuck. OPS-04 does
  not clear, abandon, reset, or silently relaunch it.
- `--once` processes the single oldest unprocessed command-like event per invocation; it
  does not drain an arbitrary backlog. Persistent systemd polling remains a later ticket.

### Branch and draft-PR publication

- Repository mutation happens only after `child_completed=true`. Failure, refusal,
  cancelled, and stuck outcomes may post a bounded queue result but never push or create a
  PR.
- Ticket branch identity is exactly `dispatcher/<ticket-id>`. Initial publication uses an
  explicit non-force source/destination refspec for that branch only. Bare `git push`, any
  argv naming `main`, tags, another branch, or an arbitrary ref refuses.
- Remediation replacement is allowed only with
  `--force-with-lease=refs/heads/dispatcher/<id>:<recorded_published_sha>` plus the exact
  ticket-branch source/destination refspec. The expected SHA comes from controller state,
  never a remote-tracking ref. Remote mismatch refuses. Plain `--force` is forbidden.
- PR identity is persisted by numeric PR number. All GitHub calls are bound to
  `St3nch/observatory`; the PR must be open, draft, unmerged, same-repo, base `main`, and
  head `St3nch:dispatcher/<id>`. Closed, merged, ready, fork, foreign-head/base, or other
  mismatch refuses rather than opening a replacement. Do not search by title.
- The controller pushes the branch itself before PR creation. Production PR creation uses
  a narrow GitHub API call or equivalent that cannot opportunistically push the current
  checkout; `gh pr create` is not the production publication primitive.
- Result comments use a closed field set plus event comment id and bounded redacted
  diagnostic. Never post raw Grok output, arbitrary original comment text, tool inputs,
  environment, logs, or credentials. A duplicate result comment is tolerated only for the
  crash window after GitHub accepted the post but before local `result_posted` persisted.

### Commissioning boundary

The review found `gh` is not currently installed and no authenticated GitHub CLI session
exists on the VPS. Deterministic implementation and zero-network review may proceed.
Live commissioning is separately authorized later and must first install/verify the chosen
GitHub client, authenticate without exposing token material, create the dedicated queue
issue, record its exact numeric repository id + issue number, and verify least-privilege
access. The controller must never call `gh auth token` or display/log/persist token
material. No live queue comment, branch push, or PR creation is authorized by this
implementation ticket alone.

### Additional mandatory proofs

In addition to the proof list above, zero-network tests must prove:

- edited-at-ingest and claimed-body-hash mismatch refuse before dispatch;
- actor validation uses numeric id + login + `type=User`; bots and login-only matches refuse;
- exact full-body grammar rejects extra text/quotes/HTML/mentions;
- narrow main-only fetch is used; fetch failure and local-main-only ancestry refuse;
- controller flock prevents concurrent `--once` double-dispatch;
- same comment id never redispatches; only a new resume event may call OPS-03 resume;
- exact ticket/start/mode and ticket-stable Writer identity reach the dispatcher seam;
- stuck dispatcher state is reported without state repair or relaunch;
- push argv is explicit and `main` is impossible;
- first publish is non-force; remediation lease uses exactly the recorded prior SHA and
  mismatch refuses;
- stored PR-number validation rejects foreign/fork/wrong-base/closed/merged/ready state;
- failure/cancelled/refused/stuck results cannot mutate repository refs or PRs;
- crash/restart state-machine recovery cannot duplicate dispatch or PR creation;
- tests bomb real `gh`, GitHub HTTP, Grok/xAI, provider, DNS, Evidence, and production DB
  access; Ruff and touched-path mypy pass.

## Implementation report

<!-- implement fills; may set Status: review; never Status: done -->

- End commit: supplied in the implementer handoff (a commit cannot embed its own final hash).
- Skills loaded:
  - `/home/chaz/.local/share/vedaops/observatory/dispatcher/worktrees/OPS-04-github-queue-draft-pr-control-plane/.grok/skills/implement/SKILL.md`
  - `/home/chaz/.local/share/vedaops/observatory/dispatcher/worktrees/OPS-04-github-queue-draft-pr-control-plane/.grok/skills/tdd/SKILL.md`
  - `/home/chaz/.local/share/vedaops/observatory/dispatcher/worktrees/OPS-04-github-queue-draft-pr-control-plane/.grok/skills/code-review/SKILL.md`
- Start commit: `4a1ff6e2f49ba60542015ff94eaf0760b3ae9df7`
- Changed paths:
  - `tools/github_queue_controller.py`
  - `tests/test_github_queue_controller.py`
  - this ticket
- Acceptance evidence:
  - `uv run pytest -q tests/test_github_queue_controller.py` — 47 passed
  - `uv run ruff check tools/github_queue_controller.py tests/test_github_queue_controller.py` — clean
  - `MYPYPATH=tools uv run mypy tools/github_queue_controller.py tests/test_github_queue_controller.py` — clean
  - Actor/id/login/`User` with no GitHub mutation: `test_non_allowlisted_actor_refuses_before_dispatcher_or_repo_mutation`
  - Grammar/ticket/SHA: `test_malformed_command_refuses_before_dispatch`, `test_crlf_and_whitespace_command_is_accepted`
  - Edited-at-ingest / body-hash: `test_edited_at_ingest_refuses_before_dispatch`, `test_claimed_body_hash_mismatch_refuses_before_dispatch`, `test_claimed_event_edited_to_non_command_prose_is_refused_not_skipped`
  - Duplicate comment id: `test_duplicate_comment_id_is_idempotent_and_never_rediscovers_writer`
  - origin/main freshness: `test_start_not_on_origin_main_refuses`, `test_fetch_failure_refuses_and_does_not_use_stale_local_main`, `test_fetch_argv_is_main_only_and_push_argv_builders_reject_main`
  - Accepted start object: `test_unaccepted_ticket_at_start_object_refuses`
  - Dirty primary: `test_dirty_primary_refuses_before_dispatch`
  - Dispatcher seam: `test_passes_exact_ticket_start_mode_and_ticket_stable_writer`
  - Non-success never publishes: `test_dispatcher_non_success_never_pushes_or_opens_pr`
  - Stuck dispatcher: `test_stuck_dispatcher_is_reported_without_repair_or_relaunch`
  - Exact ticket-branch publish: `test_successful_implement_publishes_only_ticket_branch_without_force`
  - Remediation lease: `test_resume_force_with_lease_uses_recorded_sha_and_mismatch_refuses`
  - One draft PR / foreign PR refuse: `test_one_ticket_reuses_open_draft_pr_and_rejects_foreign_state`
  - No main/merge/approve/ready/done: `test_controller_cannot_push_main_merge_approve_mark_ready_or_close_done`
  - Bounded redacted results: `test_result_comments_are_bounded_and_redact_secrets`
  - `--once` oldest only: `test_once_processes_oldest_command_like_event_only`
  - Same comment vs new resume: `test_same_comment_never_rediscovers_only_new_resume_event_calls_dispatcher`
  - Crash/restart: `test_crash_after_dispatching_does_not_relaunch_or_duplicate_pr`, `test_crash_dispatching_without_dispatcher_record_is_stuck_not_relaunched`
  - Publication-time worktree revalidation: `test_publication_refuses_if_branch_moved_after_dispatcher_result`
  - Production PR list/get merged shapes: `test_pull_from_api_accepts_get_and_list_production_shapes`, `test_pull_from_api_refuses_missing_or_contradictory_merged_fields`, `test_pull_from_api_refuses_missing_or_non_boolean_head_fork`
  - Flock: `test_controller_flock_prevents_concurrent_once`
  - `gh api` not `gh pr create` / no auth token: `test_gh_api_argv_never_uses_pr_create_or_auth_token`
  - CLI `--once`: `test_cli_once_is_required`
  - No Observatory runtime import: `test_controller_does_not_import_observatory_runtime`
  - Missing queue commission: `test_missing_queue_config_refuses_without_dispatcher_or_github`
- Unproven limits:
  - Ordinary tests inject fake GitHub, fake dispatcher, and a git runner that redirects `origin` fetch/push/ls-remote to a local bare repo. They do not prove live `gh` authentication, draft-PR creation against github.com, or real Grok execution.
  - `_pull_from_api` now has ordinary tests for GET (`merged` bool) and list (`merged_at` only) shapes, contradictory/missing merged fields, and missing/non-boolean `head.repo.fork`. Other nested `base`/`head` fields and live `gh api` bytes remain unproven until commissioning.
  - Queue identity is a local `queue.json` with `github_repository_id` + `queue_issue_number`. No such file is created here; production refuses without it.
  - Live GitHub commissioning (install/verify `gh`, authenticate without exposing token material, create the queue issue, record numeric repo id + issue number, least-privilege check) remains separately authorized.
  - Persistent systemd polling is intentionally unbuilt.
  - Controller fetch/push uses the local `origin` remote. Tests never talk to github.com; production `--once` will.
  - Force-with-lease expected SHA comes from controller event/ticket publication state, never a remote-tracking ref. Remote mismatch is a git non-zero push, not an independent GitHub compare.
  - A `dispatching` crash with no dispatcher record stays `dispatching` (not `done`), posts no queue comment, and cannot redispatch. Later `--once` polls report stuck again. Completing that event still needs a later Steward/operator boundary.
  - Secret redaction reuses OPS-03 name/assignment/`sk-` patterns. Novel secret formats can leak into the bounded diagnostic.
  - Actor allowlist is the closed triple numeric id `54292644` + login `St3nch` + `type=User`. Login-only or bot matches refuse.
  - Unauthorized-actor refusals persist local `done` with no GitHub post/PR/push. Other authorized-event refusals may still post a bounded queue result.
  - Session `tests/conftest.py` may still start throwaway PostgreSQL when this module is collected; this ticket does not use it and cannot change `conftest.py`.
- Strongest part: fail-closed command/actor/origin-main gates run before OPS-03; unauthorized actors cannot post; publication revalidates the local ticket branch/worktree immediately before push; PR merged-state parsing accepts the real list/get shapes without assuming a list `merged` bool.
- Weakest part: the live `gh api` adapter and origin fetch/push remain unproven; a `dispatching` event with no dispatcher record is parked, not operator-repaired; tests still redirect git origin.
- Possible false greens: fake GitHub always returns `St3nch/observatory` and draft PRs unless a test mutates them; fake dispatcher does not enforce OPS-03 postconditions unless the test constructs them; redaction regexes miss novel secrets; `ls-remote` skip-push still trusts the SHA the local git runner returns after worktree revalidation.
- Steward remediation (first amend): unauthorized actors no longer reach result-comment posting; stuck `dispatching` without dispatcher state no longer advances to `done`; `_pull_from_api` no longer requires a `merged` bool on list payloads; `_step_push` revalidates worktree branch, exact HEAD SHA, and cleanliness before any publish.
- Steward remediation (second amend): `_oldest_unprocessed` keeps existing non-done event IDs eligible even when the current GitHub body is no longer command-like, so a claimed `/bootie` comment edited into prose hits body-hash mismatch instead of disappearing; `_nested_fork` refuses missing or non-boolean `head.repo.fork` instead of treating it as non-fork.
- Remaining caller influence: production `main()` constructs `GhApiClient` / `ProductionDispatcher` / `SubprocessGit` only when those seams are not injected. Tests always inject. Writer children still cannot use `gh` or git network; OPS-03 denies are unchanged.
- Architecture: one `--once` controller under `tools/` imports OPS-03 `dispatch()` and does not change dispatcher semantics. Controller-owned git fetch/push is required because OPS-03 forbids those verbs. Grok still goes only through OPS-03.
- What later tickets should reuse: closed `gh api` argv allowlist, ticket-stable `bootie/<ticket-id>` writer identity, per-ticket publication record (`published_sha`, `pr_number`), monotonic event states, exclusive controller flock.
- What should remain duplicated: ticket/SHA grammar in the comment parser (defense in depth before OPS-03 normalize); push argv construction (OPS-03 must not grow push).
- Deferred: systemd timer, live commissioning, webhook/Actions, merge/`main` push, Steward closure, Product acceptance.
- Code-review vs start commit `4a1ff6e2f49ba60542015ff94eaf0760b3ae9df7`:
  - Standards: allowlist held; private OPS-03 `_normalize_ticket` / `_normalize_sha` reuse is the required coupling. Worst remaining: live GitHub JSON beyond the merged-field fixtures.
  - Spec: first- and second-round Steward findings have regressions. systemd/webhook/`gh pr create` remain omitted. Worst residual: live `gh`/GitHub/Grok unproven, as the ticket required.

## Closure

<!-- Project Steward only -->
