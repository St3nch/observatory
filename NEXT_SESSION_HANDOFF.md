# Next Session Handoff - The Observatory

Status: authority
Authority: fresh-session handoff pointer; `ACTIVE_CONTEXT.md` owns current phase truth
Purpose: preserve the accepted Observatory v1 bounded proof-system state
Last updated: 2026-07-13

---

## Current State

The Observatory is accepted at the bounded v1 proof-system ceiling, and the post-v1 database roadmap is active.

Closed milestones:

```text
M0, M0.1, M1 through M20, DB-1, and DB-2
```

Active milestone:

```text
DB-3 — Postgres Operational Boundary and Physical Schema Specification
```

The owner accepted the DB-2 v0.1.1 classification corrections, closed DB-2, and activated DB-3 specification-only work through `decisions/2026-07-13-db2-closure-and-db3-activation.md`. The accepted v1 system remains local, evidence-only, bounded, and not production-ready or feature-complete.

Current authority:

```text
decisions/2026-07-12-observatory-v1-acceptance.md
decisions/2026-07-12-post-v1-audit-acceptance-and-db-roadmap-activation.md
decisions/2026-07-12-db1-contract-corrections-and-database-boundary-rulings.md
decisions/2026-07-13-db1-closure-and-db2-activation.md
decisions/2026-07-13-db2-closure-and-db3-activation.md
POST_V1_DATABASE_ROADMAP.md
```

---

## Active Read Path

Fresh sessions must read:

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
11. `contracts/README.md`
12. `hammers/README.md`
13. `hammers/hammer-matrix-v0-1.md`
14. `hammers/acceptance-gate-policy-v0-1.md`
15. `decisions/2026-07-10-m9-first-slice-closure.md`
16. `planning-inbox/m10-logical-schema-plan-c2.md`
17. `planning-inbox/m10-schema-plan-review.md`
18. `decisions/2026-07-10-m10-schema-planning-closure.md`
19. `planning-inbox/m11-implementation-foundation-spec.md`
20. `planning-inbox/m11-foundation-readiness-review.md`
21. `decisions/2026-07-10-m11-foundation-closure.md`
22. `planning-inbox/m12-local-test-evidence-2026-07-10.md`
23. `planning-inbox/m12-first-slice-closure-readiness-review.md`
24. `decisions/2026-07-10-m12-first-slice-closure.md`
25. `research/rg1-dataforseo-rights-retention-cost.md`
26. `research/rg10-capturepackage-v0-1-inputs.md`
27. `research/rg11-raw-archive-provider-drift.md`
28. `planning-inbox/owner-ruling-tracker.md`

For planning notes, read `planning-inbox/README.md` first.

---

## Tool Discipline

When using `ob-dev`:

- Do not retry the exact same failed tool call more than once.
- Do not repeat a mutation call when SHA or diff evidence shows no meaningful change.
- If a mutation returns no diff, stop mutating and inspect with read, status, or diff tools.
- If a safety block occurs, do not hammer the same call. Try one safe read/status/diff check, then report the blocker.
- For edits, use this sequence: read -> one mutation -> diff -> diff_check -> stage exact paths -> commit.

---

## Boundaries to Preserve

- Observatory stores observations, not conclusions.
- Strategy is compute-on-read by the connected LLM, not stored in Observatory.
- Customer records are out.
- Customer first-party data is out.
- Customer overlays are read-time only unless a future explicit owner ruling changes the law.
- Provider disagreement is preserved as first-class evidence.
- Proprietary provider scores are observations of provider model output, not facts about the web.
- Rights and retention fail closed.
- LLMs and agents get no direct SQL access or credentials.
- Future access is through typed API / MCP tools only.
- Hammer tests are a hard gate.
- VEDA Brain and other killed ancestor concepts stay killed.
- Internal first-party telemetry requires explicit internal-scope handling before any storage.

---

## Roadmap State

```text
M0, M0.1, M1 through M20, DB-1, and DB-2: closed
DB-3 — Postgres Operational Boundary and Physical Schema Specification: active
DB-4 through DB-10: planned and inactive
```

The governing sequence is `POST_V1_DATABASE_ROADMAP.md`. No database milestone implies the next milestone.

Accepted DB-2 closure state:

- physical data-contract freeze v0.1.1 classification corrections accepted;
- singular primary classifications now bind DB-3;
- DB-2 closed by `decisions/2026-07-13-db2-closure-and-db3-activation.md`;
- DB-3 activated for specification work only.

---

## Immediate Next Steps

DB-3 is ready for owner decision:

1. review `planning-inbox/db3-postgres-operational-boundary-specification.md`;
2. review `planning-inbox/db3-physical-schema-specification.md`;
3. review `planning-inbox/db3-specification-readiness-review.md`;
4. accept or revise the DB-3 specifications;
5. close DB-3 or return it for revision;
6. separately activate DB-4 disposable proof work or leave it inactive.

Do not create the governed database, governed roles or credentials, or execute governed migrations. DB-4 remains separately gated.

---

## Open Questions

Open items must be read from `planning-inbox/owner-ruling-tracker.md`; do not resurrect already ruled items from stale prose.

Key current posture:

- OR-A1 is ruled compute-on-read only.
- OR-B1 and OR-B2 are ruled by the DB-1 database-boundary decision.
- OR-B3 is ruled for the accepted M15 consumer scope.
- OR-C2 and OR-C4 are ruled for fail-closed source-family retention and hybrid manifest/opaque-pointer layout.
- OR-A2, OR-A3, and other tracker rows still marked open remain fail-closed.
- No ruling authorizes capture, PostgreSQL work, production, customer-private storage, or strategy persistence.

---

## Do Not Start Yet

Do not start:

- PostgreSQL database creation
- role or credential creation
- physical schema or DDL
- migration files or migration execution
- disposable database lifecycle or real-Postgres hammers
- synthetic or real evidence persistence
- provider calls or new paid pulls
- marketplace scraping or browser-extension capture
- production API/MCP exposure
- dashboard/operator console work
- customer/private data handling
- customer-facing report work
- strategy/recommendation/conclusion storage
- recurring capture
- DB-2 activation without a separate owner decision

The project now has rails. Stay on them. No schema goblin jazz.
