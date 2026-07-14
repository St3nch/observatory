# Next Session Handoff - The Observatory

Status: authority
Authority: fresh-session handoff pointer; `ACTIVE_CONTEXT.md` owns current phase truth
Purpose: preserve the accepted DB-2 checkpoint and fresh DB-3 planning-only posture
Last updated: 2026-07-14

---

## Current State

The Observatory v1 bounded proof system remains accepted.

Database-phase authority is now:

```text
DB-1 — trusted and complete
DB-2 — trusted, accepted, and complete
DB-3 — active for fresh planning and specification only
DB-4 — inactive; no active or authoritative artifact
DB-5 through DB-10 — planned / inactive
```

Current authority:

```text
decisions/2026-07-14-db2-freeze-acceptance-and-db3-planning-authorization.md
```

The owner accepted the exact DB-2 freeze v0.2.1 at SHA-256
`7c24d38ea8e7634dea8cf52cd7b85b49eda18b8ecde5a00c74b6303809c17891`,
closed DB-2 successfully, and authorized fresh DB-3 planning. The five untrusted
DB-3/DB-4 artifacts remain permanently retired and must not be restored, salvaged,
reused, copied, paraphrased, or reconstructed from memory.

---

## Active Milestone

```text
DB-3 — Postgres Operational Boundary and Physical Schema Specification
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

## DB-3 Fresh Planning Read Path

Before DB-3 planning, also read:

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
15. `POST_V1_DATABASE_ROADMAP.md`

Read `planning-inbox/README.md` before treating any planning-inbox file as context. Planning material is not authority.

---

## Required Synchronization Proof

Before proposing or making nontrivial changes, report:

- repository root;
- files read;
- last trusted completed milestone;
- active recovery milestone;
- allowed work;
- forbidden work;
- missing files;
- contradictions;
- whether implementation may proceed.

Run:

```powershell
python tools/check_authority_sync.py
```

A failing authority check blocks mutation until the conflict is reconciled.

---

## Current Task

Prepare to begin DB-3 fresh from accepted authority:

1. define the DB-3 planning approach and ordered specification work;
2. derive only from trusted DB-1 and the exact accepted DB-2 freeze;
3. preserve identity, lifecycle, provenance, scope, rights, retention, relationships,
   exposure, fail-closed behavior, forbidden persistence, and H1-H22 implications;
4. do not create executable DDL, migrations, SQL, database tooling, or any database;
5. do not restore or reconstruct any retired DB-3/DB-4 artifact.

DB-3 planning authority exists, but no DB-3 artifact has yet been created. DB-4 is
inactive and implementation remains unauthorized.

---

## Tool Discipline

- Use only the custom `ob-dev` MCP for local repository inspection, bounded mutation, Git, and fixed validation profiles.
- Generic shell, PowerShell, Python, SQL, and arbitrary Git execution remain disabled.
- `chatgpt_mcp` is a read-only Git reference; local staging and commits are limited to `ob_dev` and `observatory`.
- Do not implement, register, or activate database tools during DB-3.
- Tool availability and credentials never create authority.
- Do not retry the same failing mutation repeatedly.
- For edits: read, mutate once with optimistic SHA-256 control, inspect the complete diff, run checks, then stage exact reviewed paths.

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
- Candidate, draft, and planning documents do not become authority by claiming acceptance.

---

## Do Not Start

```text
PostgreSQL creation
PostgreSQL startup
database creation
roles or credentials
SQL or DDL
migration files or execution
disposable database lifecycle
real PostgreSQL hammers
database-control-plane expansion
database-tool implementation or activation
synthetic or real persistence
provider calls or paid pulls
customer or private data
raw capture
production API/MCP
recurring capture
strategy/recommendation/conclusion/report-state persistence
```

The project is back on rails. This time the rails get a continuity tester.
