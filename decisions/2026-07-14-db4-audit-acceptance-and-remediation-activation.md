# Decision — DB-4 Audit Acceptance and Remediation Activation

Date: 2026-07-14
Status: accepted
Authority: owner ruling
Related milestone: DB-4 remediation

## Decision

The owner accepts `audits/observatory-db1-through-db4-full-independent-audit.md` as authoritative review input for DB-4 remediation.

The audit does not replace accepted project doctrine, DB-2, or DB-3. It does establish that the current DB-4 implementation and disposable proof are not closure-grade.

DB-1 remains trusted and complete.
DB-2 remains trusted, accepted, and complete.
DB-3 remains trusted, accepted, and complete as the physical-design authority.
DB-4 remains active and is returned to remediation.
DB-5 remains inactive.

## Current DB-4 implementation disposition

The current nine migration candidates, hammers, fixtures, profiles, and disposable PostgreSQL runs are classified as diagnostic implementation evidence only.

They do not satisfy DB-4 closure because:

- the migration candidates do not faithfully implement the accepted DB-3 physical design;
- migration history is mutable and not atomic with migration execution;
- mandatory hammer IDs are not consistently mapped to their accepted hostile claims;
- role and RLS claims were not proven under bounded non-superuser execution;
- broken candidates did not traverse the real migration admission path;
- durable per-hammer result-register records do not exist;
- proof cleanup, failure retention, and reviewability are incomplete.

No prior disposable run may be promoted into closure evidence without a fresh accepted remediation package and re-execution.

## Audit findings disposition

All Claude findings must be considered during remediation except that the MCP tool-count finding is not a primary technical blocker.

The two additional bounded tools — broken-candidate proof and bounded test-role cleanup — are useful capabilities. Their documentation and authority must be reconciled, but remediation priority belongs to schema fidelity, migration integrity, hammer realism, proof durability, security, and operational safety.

The accepted disposition matrix is defined in:

```text
planning-inbox/db4-audit-remediation-program-v0-1.md
```

## Activated work

This decision authorizes DB-4 remediation planning and exact implementation-package preparation only.

Authorized now:

- reconcile every accepted audit finding;
- create a DB-3-to-migration-to-hammer traceability matrix;
- redesign the DB-4 migration/history mechanism;
- redesign mandatory hammers as behavioral hostile tests;
- design durable result-register emission and validation;
- design bounded role/RLS proof;
- design broken-candidate execution through the real migration admission path;
- design marker hardening, authority binding, redaction, and network-exposure controls;
- design data-driven hammer profiles and restart-reduction measures;
- update current-state, roadmap, handoff, indexes, and stale authority text;
- prepare exact bounded remediation manifests and stop conditions for later owner review.

Not authorized by this decision:

- creation of the governed `observatory` database;
- DB-5 planning or implementation;
- provider calls, ingestion, capture, customer/private data, recurring work, or production;
- broad unbounded rewrites;
- treating the current schema as an accepted DB-5 migration set;
- new PostgreSQL execution before an exact remediation execution package is separately accepted;
- weakening fixed roots, bounded tools, authority gates, or no-arbitrary-SQL/no-shell rules.

## Required remediation sequence

1. Freeze the current DB-4 proof campaign as diagnostic only.
2. Reconcile authority and stale roadmap/current-state text.
3. Produce the exact DB-3 responsibility traceability matrix.
4. Repair migration/history architecture before expanding schema candidates.
5. rebuild the candidate schema to match accepted DB-3 responsibilities.
6. rebuild hammers as behavioral tests with sabotage/mutation verification.
7. implement durable immutable result-register records and validation.
8. harden role/RLS, marker identity, authority binding, redaction, and remote-access posture.
9. implement data-driven profiles to reduce MCP restart churn.
10. prepare and obtain a separate owner gate for real disposable re-execution.
11. re-run the complete proof campaign from a clean disposable substrate.
12. consider DB-4 closure only after every accepted gate passes.

## Continuing boundaries

The Observatory remains the telescope, not the astronomer.

No customer records, customer first-party analytics, strategy, recommendations, conclusions, score-as-truth, report state, provider-as-truth, or arbitrary LLM SQL/credentials may enter Observatory durable storage.

No milestone implies the next milestone.
