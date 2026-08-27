# OPS-03 — Headless Grok Build dispatcher bootstrap

**Status:** provisional-review
**Owner:** [GROK] implementation / [GPT] Steward review
**Kind:** development-workflow tooling; not Observatory capture/acquisition behavior
**Blocked by:** required read-only ticket review and Steward reconciliation
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

- No implementation starts from this provisional ticket.
- [GPT] owns authority/ticket reconciliation; [GROK] writes implementation/tests only after
  final acceptance and exact start commit.
- No automatic merge or push to `main`.
- No provider, DNS, paid, production credential, Evidence capture, or production database activity.
- No generic multi-agent framework.
- No unattended GitHub trigger in this bootstrap ticket unless the read-only review proves
  it is required for the minimum dispatcher proof.
- No change to Observatory service behavior.

## Next boundary

After read-only review, [GPT] reconciles findings and the agent-workflow authority update,
commits the final accepted ticket, and issues its exact start commit. The first implementation
run is then launched manually through the already-proved headless Grok Build session. Only
after the dispatcher itself is independently reviewed and closed do we add GitHub-triggered
queue/PR automation.
