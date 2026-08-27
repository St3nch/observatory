# OPS-03 — Headless Grok Build dispatcher bootstrap

**Status:** accepted
**Owner:** [GROK] implementation / [GPT] Steward review
**Kind:** development-workflow tooling; not Observatory capture/acquisition behavior
**Blocked by:** none — read-only review reconciled by Steward
**Approved by:** [CHAZ] to bootstrap GitHub-gated headless Grok Build development
**Start commit:** pending final Steward acceptance

## Purpose

Build the smallest local dispatcher that can turn one finally accepted Observatory ticket
and exact Steward-issued start commit into one isolated, resumable headless Grok Build
Writer session on the VPS.

This is developer automation only. It does not authorize provider transport, acquisition,
spend, DNS, production credentials, Evidence mutation, PostgreSQL production mutation,
GitHub merge, or another deferred Product boundary.

The MVP proves the execution seam before any unattended GitHub trigger is added:

accepted ticket + exact start SHA
→ isolated branch/worktree
→ one named Grok Build Writer session
→ bounded implementation prompt
→ ticket-scoped checks
→ one reviewable implementation commit / PR-ready branch
→ stop for independent review

GitHub-triggered polling/routines, multi-ticket scheduling, automatic reviewer launch, and
automatic PR creation are later layers unless this ticket's review proves one is necessary
for the minimum end-to-end proof.

## Confirmed external runtime facts

Current xAI Grok Build supports headless `grok -p`, named/resumable sessions, `--cwd`,
`--worktree`, `--ref`, machine-readable output, per-run allow/deny permission rules,
sandbox profiles, and read-only subagents/workflows. The already-authenticated VPS session
has separately proved a harmless headless invocation with `XAI_API_KEY` unset.

These runtime facts are implementation inputs, not Observatory Product authority. If the
installed CLI differs, stop and report rather than silently changing the workflow.

## Required behavior

1. Dispatcher input is explicit and closed: repository root, ticket path, exact 40-hex
   start commit, execution mode `implement` or `resume`, and a Writer/session identity.
2. Before any Grok Build implementation run, fail closed unless:
   - repository identity is Observatory;
   - the named start commit exists;
   - the selected ticket exists at that start commit;
   - the base checkout is clean;
   - no existing active Writer owns the same ticket;
   - the requested branch/worktree is not another ticket's live worktree.
3. Create or reuse one isolated ticket branch/worktree rooted at the exact start commit.
   Never perform implementation in `main`'s working tree.
4. Start one headless Grok Build Writer in that worktree. The prompt must require:
   - authority read in `AGENTS.md` order;
   - the exact accepted ticket;
   - ticket changed-path allowlist;
   - project-local skills only, with absolute `SKILL.md` paths reported;
   - one Writer only;
   - no authority widening;
   - no provider/live/DNS/credential/spend activity unless the ticket separately authorizes it;
   - implementation Status=`review`, never `done`;
   - one reviewable commit and implementation report.
5. Persist enough non-secret run state to resume the **same Writer** after bounded
   remediation: ticket, start commit, branch/worktree, Grok session ID, current implementation
   commit if any, timestamps/state, and last process outcome. Do not persist auth tokens,
   provider credentials, secrets, prompt-injected secret values, or Evidence.
6. Resume mode must target the same stored Grok session and worktree. A remediation request
   must not silently start a new Writer.
7. Headless execution must use bounded permissions/sandbox behavior. It must not use an
   unqualified catch-all permission grant as the workflow's security model. Git push, merge,
   provider/network tooling, secret paths, and destructive filesystem commands remain denied
   unless separately and explicitly enabled by a later accepted boundary.
8. Capture Grok's machine-readable stdout/stderr/result metadata into a non-authoritative
   local run log suitable for operator diagnosis. Logs are not project authority and must
   not contain credentials.
9. The dispatcher itself does not merge, force-push, mark tickets `done`, modify authority,
   or declare Steward/Product acceptance.
10. A failed/expired Grok authentication state, dirty base, invalid ticket/start SHA,
    duplicate Writer, tool refusal, nonzero child exit, or red required check fails closed
    with a clear operator-visible state and does not invent success.

## Steward reconciliation — locked bootstrap decisions

The required read-only review returned `READY_AFTER_TICKET_RECONCILIATION`. The following
choices are now part of this accepted ticket and remove implementation discretion on the
load-bearing execution seams.

### Exact start commit and accepted-ticket gate

- `implement` reads the ticket from the supplied Git object (`git show
  <start-sha>:tickets/<ticket>` or an equivalent object read), never from the live working
  tree, and requires that object to contain `**Status:** accepted`.
- `implement` creates the ticket worktree at the exact start SHA and verifies its initial
  `HEAD` equals that SHA.
- `resume` never resets the worktree. It requires the recorded start SHA to remain an
  ancestor of current worktree `HEAD`, and requires the recorded branch and worktree path
  to match.
- The canonical bootstrap repository is `/home/chaz/projects/vedaops/observatory` with
  `origin` equal to `ssh://github.com/St3nch/observatory.git`. A different repository
  identity refuses.
- The primary checkout must be clean under porcelain status including untracked files. A
  resumed ticket worktree may be dirty because interrupted Grok work is not rolled back.

### Worktree ownership

- The **dispatcher** owns worktree creation using ordinary `git worktree add -b ...
  <path> <start-sha>`.
- Grok is launched with `--cwd <that-path>` and never with Grok Build `--worktree` / `--ref`
  for this bootstrap.
- Ticket worktrees live below
  `~/.local/share/vedaops/observatory/dispatcher/worktrees/` and are not created inside the
  primary `main` checkout.
- Resume uses the exact same recorded path. No fresh worktree is created for remediation.

### One Writer and resume identity

- One exclusive filesystem lock exists per ticket. The key is the ticket, not
  `(ticket,start_sha)`.
- `implement` refuses when the ticket lock is held, a recorded child PID is still live, or
  state is `running`. There is no timeout that silently releases Writer ownership.
- A crashed/abandoned run is explicitly resumed or explicitly abandoned by a later operator
  boundary; it never silently starts a second Writer.
- New headless execution uses JSON output and records the actual returned Grok `sessionId`.
  The dispatcher must not invent or pre-fill a fake session UUID.
- Resume uses `--resume <recorded-session-id>` with the same `--cwd`; it never uses
  `--continue`, `--session-id` to reuse an existing session, `--fork-session`, or
  `--worktree`.

### Closed headless argv and permissions

- Every implementation and resume run explicitly selects an unattended automation
  permission mode rather than inheriting user config. For OPS-03 the accepted mode is
  explicit `--always-approve` **plus a substantive deny set**, because live commissioning
  proved that `dontAsk` with a narrowly enumerated Bash allowlist can cancel otherwise-safe
  implementation work before producing a commit.
- The deny set includes Git push/merge/rebase/reset/clean/checkout-or-switch to `main`,
  destructive filesystem commands, provider/network clients, GitHub mutation/network
  commands, and access to known auth/secret/credential paths or DataForSEO credential
  variables. Ordinary local repository inspection and test/build commands are permitted.
- This is not an OS security boundary and is not permission to widen scope. The Writer is
  still confined by the accepted changed-path allowlist, isolated worktree, prompt,
  no-subagent rule, and independent review.
- Every run also carries `--no-subagents`, `--no-ask-user`, `--disable-web-search`, and
  memory disabled. WebFetch/MCP/provider/network tooling is not available to the Writer.
- The prompt is delivered verbatim (`--verbatim` or an exact prompt file), so the tested
  closed prompt is the prompt actually supplied to Grok.
- Project-local-skill-only use remains a prompt/governance rule, not a claimed CLI security
  boundary. Bundled/user skills existing on disk are an explicit unproven limit.

**Commissioning evidence:** the first OPS-03 Writer session
`01a0447d-7539-7be2-b3c5-e092dfbb0737` twice returned process exit `0` with JSON
`stopReason = "cancelled"` while the worktree remained clean at the exact start commit.
The dispatcher must therefore judge the Grok JSON result as well as the child process exit
code; process exit `0` alone is never implementation success.

### Sandbox boundary for OPS-03

The built-in Grok `workspace` sandbox is **not** required in this bootstrap implementation.
With a dispatcher-owned Git worktree, Git ref/object metadata needed by `git commit` lives
outside the worktree CWD; the installed sandbox can therefore make the required commit
infeasible or can warn/fall back without proving enforcement. OPS-03 instead relies on the
closed `dontAsk` permission set plus isolated worktree and explicit denials above.

A later ticket may add a host-proved custom sandbox profile that permits only the required
Git metadata writes and fails closed when enforcement is unavailable. OPS-03 must not claim
OS-level sandbox enforcement.

### State, logs, timeout, and exit state

- Dispatcher state, lock files, and logs live under
  `~/.local/share/vedaops/observatory/dispatcher/`, never in the repository, Evidence Store,
  or Grok auth files.
- Persist only the bounded run record: ticket, start SHA, branch, worktree, Grok session ID,
  child PID while live, timestamps/state, implementation commit when known, exit/stop
  result, and a bounded non-secret diagnostic.
- Use one final JSON result rather than streaming tool payload logs. Do not persist raw tool
  inputs or file contents.
- Child timeout is **7200 seconds**. Exit `0` means the Grok process completed; exit `1`,
  `130`, `143`, timeout, auth expiry, or any other nonzero result is recorded as failure or
  interrupted/resumable state, never implementation success.

### Tooling/test seam

- Keep implementation under `tools/` plus one focused test module. Do not change
  `pyproject.toml` merely to package the dispatcher.
- Tests import/execute the tool through a test-local seam or subprocess entrypoint; normal
  project packaging remains unchanged.
- Because repository mypy configuration does not include `tools/`, implementation
  validation explicitly invokes mypy on the touched dispatcher path and its focused test.
- Ordinary tests inject/fake the Grok child boundary and must be incapable of accidentally
  invoking the real `grok` executable.
- The manual installed-CLI smoke remains a separately authorized post-review proof. Fake
  child tests do not prove real auth, resume, permissions, Git metadata writes, or host
  sandbox behavior.

### GitHub remains the next layer

No GitHub polling, labels, webhooks, Actions, PR creation, automatic reviewer launch, or
merge automation is added by OPS-03. Closing this local dispatcher proof is the prerequisite
for that Bootie Factory control-plane layer.

## Recommended implementation shape

Keep this tooling outside `src/observatory/`; it is development orchestration, not service
runtime behavior. Prefer one small importable tool module plus ordinary tests and a thin
operator entrypoint. Do not revive the deferred OPS-01 hook framework or add a generic agent
platform.

The exact file names are reviewable engineering detail, but the expected footprint is a
small `tools/` implementation plus one focused test module and this ticket's implementer
fields/report.

## Required proofs

Ordinary zero-provider tests must prove at minimum:

- invalid/missing ticket refuses before Grok invocation;
- invalid/missing start commit refuses;
- dirty base refuses;
- worktree/branch is based on the exact supplied start commit;
- duplicate active Writer for one ticket refuses;
- prompt contains exact ticket/start commit and the hard boundaries above;
- new implementation uses one recorded session ID;
- resume reuses the exact same session ID/worktree;
- child nonzero/timeout/auth failure is recorded as failure, not success;
- logs/state redact or reject known secret-like inputs;
- no test invokes real Grok/xAI, DataForSEO, DNS, GitHub mutation, provider transport, or
  production PostgreSQL;
- dispatcher cannot merge `main` or mark a ticket `done`;
- deterministic tests mock/process-fake the Grok child boundary;
- Ruff and touched-path mypy pass.

A separately authorized manual smoke after code review may run one harmless headless Grok
task in a disposable test worktree to prove the installed CLI/session seam. That smoke must
not modify Observatory product code, invoke providers, push, or merge.

## GitHub control-plane boundary

This ticket intentionally stops one layer short of unattended GitHub dispatch.

The next layer may use GitHub issue/PR/project state as the durable event bus, but only after
this dispatcher proves:

- exact ticket/start-SHA gating;
- isolated worktree;
- same-Writer resume;
- bounded execution;
- honest failure state.

No label, webhook, routine, or GitHub notification by itself is implementation authority.
A future trigger must resolve to a finally accepted ticket and exact Steward start commit
before this dispatcher can run.

## Changed-path allowlist

Expected implementation paths:

- one small dispatcher module/entrypoint under `tools/`;
- one focused dispatcher test module under `tests/`;
- this ticket for implementer Start commit, Status=`review`, and Implementation report.

If implementation requires changing `src/observatory/`, migrations, provider adapters,
Evidence Store, API code, authority files, existing tickets, or CI/GitHub workflow files,
stop and report before widening.

## Validation boundary

[GROK] runs the dispatcher-focused tests, Ruff, and touched-path mypy. [CHAZ] runs any final
repository-wide validation required for closure. [GPT] performs independent diff/code/test
review and does not execute repository tests through MCP.

## Required pre-implementation review

Before final acceptance, [GROK] performs a read-only code-first review of this ticket plus
current `AGENTS.md`, the deferred OPS-01 history, installed project-local Grok skills, and
the actual installed Grok Build CLI help/inspect output.

The review must challenge:

- whether a smaller bootstrap can prove the same useful execution seam;
- whether any requirement accidentally revives OPS-01 or builds a general orchestration platform;
- whether session/worktree ownership is fail-closed and resume really preserves one Writer;
- whether permission/sandbox requirements are supported by the installed CLI/account;
- whether logs/state can leak credentials;
- whether worktree/base validation can false-green;
- whether the expected changed paths are sufficient;
- whether GitHub triggering is correctly deferred until the local dispatcher is proven.

Return exactly one: `READY`, `READY_AFTER_TICKET_RECONCILIATION`, or `NOT_READY`.
Do not edit, commit, push, invoke providers, or use real credentials during review.

## Hard boundaries

- Implementation starts only from this accepted ticket and an exact Steward-issued start commit.
- [GPT] owns authority/ticket reconciliation; [GROK] writes implementation/tests only after
  final acceptance and exact start commit.
- No automatic merge or push to `main`.
- No provider, DNS, paid, production credential, Evidence capture, or production database activity.
- No generic multi-agent framework.
- No unattended GitHub trigger in this bootstrap ticket unless the read-only review proves
  it is required for the minimum dispatcher proof.
- No change to Observatory service behavior.

## Next boundary

The read-only review and Steward reconciliation are complete. The first implementation run
is launched manually from the exact Steward-issued start commit through the already-proved
headless Grok Build session. Only after the dispatcher itself is independently reviewed and
closed do we add GitHub-triggered queue/PR automation.

## Commissioning clarification

Live OPS-03 commissioning supersedes any stale sentence above that still describes this
bootstrap as relying on a closed `dontAsk` allowlist. The accepted unattended mode is
explicit `--always-approve` with substantive denies, isolated worktree, no subagents,
no ask-user, disabled web search, and the unchanged scope boundaries. Dispatcher success
requires both child process exit `0` and a successful Grok JSON stop reason; exit `0` with
`stopReason="cancelled"` is non-success/resumable and must be tested.
