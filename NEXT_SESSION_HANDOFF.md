# Next Session Handoff - The Observatory

Status: authority
Authority: fresh-session handoff pointer; `ACTIVE_CONTEXT.md` owns current phase truth
Purpose: preserve the trusted DB-1 checkpoint and DB-2 recovery posture
Last updated: 2026-07-13

---

## Current State

The Observatory v1 bounded proof system remains accepted.

Database-phase trust is reset to:

```text
DB-1 — closed and trusted
DB-2 — active for reconciliation and owner review only
DB-3 — suspended / inactive
DB-4 — suspended / inactive
DB-5 through DB-10 — planned / inactive
```

Recovery authority:

```text
decisions/2026-07-13-database-phase-recovery-to-db1.md
```

The canonical DB-2 freeze was declared accepted without actually incorporating all v0.1.1 corrections. Later DB-3 and DB-4 claims therefore cannot be trusted until DB-2 is repaired and reviewed again.

---

## Active Milestone

```text
DB-2 — Physical Data-Contract Freeze Reconciliation
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

## DB-2 Recovery Read Path

Before DB-2 work, also read:

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
12. `planning-inbox/owner-ruling-tracker.md`

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

## Current Recovery Task

1. reconcile the canonical DB-2 freeze with the v0.1.1 correction package;
2. review each correction from the trusted DB-1 contracts and boundaries;
3. enforce exactly one primary classification per concept;
4. preserve all fail-closed and forbidden-persistence rules;
5. produce a fresh DB-2 readiness review;
6. request a new explicit owner decision.

Existing DB-3 documents may be read as untrusted candidates only after the DB-2 contract is coherent. They must not be used to smuggle physical design backward into DB-2.

---

## Tool Discipline

- Codex native local tools own ordinary PowerShell, filesystem, Git, tests, and code work.
- Use the desktop app's built-in Git review and commit controls.
- Do not use old `ob-dev` Git tools.
- `ob-dev-mcp` remains bounded to its current file-oriented surface during recovery.
- Do not add database tools to `ob-dev-mcp` during DB-2.
- Tool availability and credentials never create authority.
- Do not retry the same failing mutation repeatedly.
- For edits: read, mutate once, inspect diff, run checks, then stage exact files.

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
roles or credentials
SQL or DDL
migration files or execution
disposable database lifecycle
real PostgreSQL hammers
database-control-plane expansion
synthetic or real persistence
provider calls or paid pulls
customer or private data
raw capture
production API/MCP
recurring capture
strategy/recommendation/conclusion/report-state persistence
```

The project is back on rails. This time the rails get a continuity tester.
