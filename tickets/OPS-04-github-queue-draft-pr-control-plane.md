# OPS-04 — GitHub queue and draft-PR control plane

**Status:** provisional
**Owner:** [GROK] implementation / [GPT] Steward review
**Kind:** development-workflow tooling; not Observatory acquisition/runtime behavior
**Blocked by:** none — OPS-03 dispatcher is closed and live-smoke proven
**Approved by:** [CHAZ] to proceed with the next Bootie Factory control-plane layer
**Start commit:** pending final Steward acceptance

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

## Implementation report

<!-- implement fills; may set Status: review; never Status: done -->

## Closure

<!-- Project Steward only -->
