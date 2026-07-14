# Next Session Handoff - The Observatory

Status: authority
Authority: fresh-session handoff pointer; `ACTIVE_CONTEXT.md` owns current phase truth
Purpose: preserve the accepted DB-4 package and phased implementation posture
Last updated: 2026-07-14

---

## Current State

The Observatory v1 bounded proof system remains accepted.

Database-phase authority is now:

```text
DB-1 — trusted and complete
DB-2 — trusted, accepted, and complete
DB-3 — trusted, accepted, and complete
DB-4 — active for exact phased implementation and disposable PostgreSQL proof
DB-5 through DB-10 — planned / inactive
```

Current authority:

```text
decisions/2026-07-14-db4-package-acceptance-and-phased-implementation-authorization.md
```

The owner accepted the exact DB-4 planning package committed at `90e6cecec19a8ed3e4bd241b37ff575b55a826b1` and authorized only its exact phased implementation. DB-4 is not closed. DB-5 remains inactive.

---

## Active Milestone

```text
DB-4 — Database Hammer Harness and Migration Specification
```

---

## Mandatory Root Read Path

Fresh sessions must read, in order:

1. `README.md`
2. `LLM_START_HERE.md`
3. `ACTIVE_CONTEXT.md`
4. `ROADMAP.md`
5. `ROADMAP_RULES.md`
6. `REPO_MAP.md`
7. `00-project-overview.md`
8. `01-harvest-register.md`
9. `02-boundaries.md`
10. `NEXT_SESSION_HANDOFF.md`

If any required file is missing or disagrees about active authority, stop and report the conflict.

---

## DB-4 Implementation Read Path

Read `planning-inbox/README.md` before any planning-inbox artifact.

Then read the full DB-1 through DB-3 lineage listed there, followed by:

1. `planning-inbox/db4-dormant-postgres-gap-and-disposition-matrix.md`
2. `planning-inbox/db4-exact-ob-dev-implementation-package-specification.md`
3. `planning-inbox/db4-migration-harness-and-proof-package-specification.md`
4. `planning-inbox/db4-security-credentials-restart-and-owner-action-runbook.md`
5. `planning-inbox/db4-owner-readiness-review.md`
6. `decisions/2026-07-14-db4-package-acceptance-and-phased-implementation-authorization.md`
7. `POST_V1_DATABASE_ROADMAP.md`

The five accepted DB-4 planning artifacts are immutable and bind the exact implementation manifests, phases, controls, and stop conditions.

---

## Required Synchronization Proof

Before nontrivial changes, report:

- repository root;
- branch, HEAD, upstream, and ahead/behind;
- files read;
- last trusted completed milestone;
- active milestone;
- allowed and forbidden work;
- missing files and contradictions;
- implementation authorization;
- staged, unstaged, and untracked paths.

Run the fixed `authority_sync` profile. A failing check blocks mutation until the conflict is reconciled.

---

## Current Task

Execute the exact accepted DB-4 package in phases:

1. exact 17-path `ob_dev` implementation;
2. version `0.5.0`, exact 28-tool expansion, expected 60-tool registry;
3. complete `ob_dev` validation and separate commit;
4. owner restart and connector refresh;
5. exact 46-path Observatory migration/harness implementation;
6. complete Observatory validation and separate commit;
7. owner credential and PostgreSQL service actions under the accepted runbook;
8. exact disposable `observatory_test_` migration, rollback, hammer, backup/restore, cleanup, and proof sequence;
9. later DB-4 closure review only after every accepted proof gate passes.

Stop on the first failed phase or manifest mismatch.

---

## Authorized Scope

Authorized only as named by the accepted package:

- package-defined `ob_dev` source/test changes and tool registration;
- package-defined Observatory migration, rollback, fixture, profile, validator, and test paths;
- owner-controlled credentials, PostgreSQL service actions, restart, and connector refresh;
- one protected and marked disposable PostgreSQL database using the `observatory_test_` prefix;
- exact-path and expected-SHA migration/rollback execution;
- package-defined hammer, role, concurrency, backup, restore, cleanup, and proof profiles;
- separate exact-manifest commits and manual pushes.

---

## Continuing Prohibitions

```text
governed database observatory
governed or production roles and migrations
production or production-like deployment
real evidence persistence
synthetic persistence outside exact disposable fixtures
providers, paid pulls, ingestion, capture, or raw provider payloads
customer records, customer first-party analytics, or private data
recurring capture or recurring work
autonomous spend
public API/MCP exposure
dashboards
strategy, recommendation, conclusion, score-as-truth, or report-state persistence
paths, tools, dependencies, databases, profiles, or capabilities outside the accepted package
DB-5 planning, activation, implementation, or execution
```

---

## Tool Discipline

- Use only the custom `ob-dev` MCP for local repository inspection, bounded mutation, Git, and fixed validation profiles.
- Generic shell, PowerShell, Python, SQL, and arbitrary Git execution remain disabled.
- `chatgpt_mcp` is a read-only Git reference; local staging and commits are limited to `ob_dev` and `observatory`.
- Owner actions remain owner actions.
- Use optimistic SHA control, complete diff review, fixed validation, exact staging, and manifest-locked commits.
- Never push; provide manual push commands after successful commits.

---

## Final Boundary

The Observatory stores observations, not conclusions. The connected LLM interprets at read time. Accepted conclusions promote out to the owning consumer.

Passing disposable proof does not create the governed database and does not activate DB-5.
