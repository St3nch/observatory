# Next Session Handoff - The Observatory

Status: authority
Authority: fresh-session handoff pointer; `ACTIVE_CONTEXT.md` owns current phase truth
Purpose: preserve the accepted DB-3 checkpoint and DB-4 package-preparation-only posture
Last updated: 2026-07-14

---

## Current State

The Observatory v1 bounded proof system remains accepted.

Database-phase authority is now:

```text
DB-1 — trusted and complete
DB-2 — trusted, accepted, and complete
DB-3 — trusted, accepted, and complete
DB-4 — active for exact implementation-package preparation only
DB-5 through DB-10 — planned / inactive
```

Current authority:

```text
decisions/2026-07-14-db3-acceptance-closure-and-db4-package-preparation.md
```

The owner accepted the exact DB-3 planning package, closed DB-3 successfully, and
authorized preparation of an exact DB-4 implementation package. The owner did not
authorize implementation or execution.

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

If any required file is missing or disagrees about active authority, stop and report
the conflict.

---

## DB-4 Package-Preparation Read Path

Read `planning-inbox/README.md` before any planning-inbox artifact.

Then read, in order:

1. `decisions/2026-07-12-post-v1-audit-acceptance-and-db-roadmap-activation.md`
2. `decisions/2026-07-12-db1-contract-corrections-and-database-boundary-rulings.md`
3. `planning-inbox/db1-closure-readiness-review.md`
4. `decisions/2026-07-13-db1-closure-and-db2-activation.md`
5. `decisions/2026-07-13-database-phase-recovery-to-db1.md`
6. `hammers/hammer-matrix-v0-2.md`
7. `hammers/acceptance-gate-policy-v0-2.md`
8. `hammers/per-hammer-result-register-v0-1.md`
9. `planning-inbox/db2-physical-data-contract-freeze-specification.md`
10. `planning-inbox/db2-freeze-v0-1-1-classification-corrections.md`
11. `planning-inbox/db2-closure-readiness-review.md`
12. `planning-inbox/db2-reconciled-candidate-v0-2-1-readiness-review.md`
13. `planning-inbox/owner-ruling-tracker.md`
14. `decisions/2026-07-14-db2-freeze-acceptance-and-db3-planning-authorization.md`
15. `planning-inbox/db3-accepted-input-traceability-matrix.md`
16. `planning-inbox/db3-fresh-postgres-design-specification-v0-1.md`
17. `planning-inbox/db3-future-ob-dev-control-plane-contract-v0-1.md`
18. `planning-inbox/db3-owner-readiness-review.md`
19. `decisions/2026-07-14-db3-acceptance-closure-and-db4-package-preparation.md`
20. `POST_V1_DATABASE_ROADMAP.md`

The accepted DB-3 artifacts are immutable planning specifications. They do not
authorize implementation by themselves.

---

## Required Synchronization Proof

Before proposing or making nontrivial changes, report:

- repository root;
- branch, HEAD, upstream, and ahead/behind;
- files read;
- last trusted completed milestone;
- active milestone or recovery gate;
- allowed and forbidden work;
- missing files and contradictions;
- implementation authorization;
- staged, unstaged, and untracked paths.

Run the fixed `authority_sync` profile. A failing check blocks mutation until the
conflict is reconciled.

---

## Current Task

Prepare one exact DB-4 implementation package proposal:

1. identify every proposed `ob_dev` source and test path;
2. bind the exact 28-tool registry and expected total tool count;
3. define inputs, structured redacted results, capability classes, protected names,
   credential custody, and fixed binary/host/port rules;
4. define non-executable migration/rollback specification inventories with exact
   path/SHA controls;
5. define disposable-database, hammer-profile, proof, backup/restore, restart, and
   connector-recovery plans;
6. define validation and owner action sequences;
7. stop for owner approval before implementation.

No DB-4 implementation-package artifact has yet been approved for creation. Propose
the exact artifact inventory before writing it.

---

## Tool Discipline

- Use only the custom `ob-dev` MCP for local repository inspection, bounded mutation,
  Git, and fixed validation profiles.
- Generic shell, PowerShell, Python, SQL, and arbitrary Git execution remain disabled.
- `chatgpt_mcp` is a read-only Git reference; local staging and commits are limited to
  `ob_dev` and `observatory`.
- Do not implement, register, activate, or restart database tools during package
  preparation.
- Tool availability and credentials never create authority.
- For edits: read, mutate once with optimistic SHA-256 control, inspect the complete
  diff, run checks, then stage only an exact reviewed manifest.

---

## Boundaries to Preserve

- Observatory stores observations, not conclusions.
- Strategy is compute-on-read and promotes out to the owning consumer.
- Customer records and customer first-party data are out.
- Provider disagreement remains first-class evidence.
- Provider scores remain provider-attributed testimony.
- Rights and retention fail closed.
- LLMs receive no SQL access or credentials.
- Hammers are hard gates and proof classes must not be inflated.
- VEDA Brain and other killed concepts stay killed.
- Planning documents do not create implementation authority.

---

## Do Not Start

```text
PostgreSQL startup or control
database or role creation
credentials or secrets
SQL or DDL
executable migration or rollback files
migration execution
disposable database lifecycle
real PostgreSQL hammers
database-control-plane implementation or registration
ob_dev restart or connector refresh
backup or restore execution
synthetic or real persistence
provider calls or paid pulls
customer or private data
raw capture or storage
production API/MCP
recurring capture
strategy/recommendation/conclusion/report-state persistence
DB-5
```

The next artifact is a package proposal, not a database.
