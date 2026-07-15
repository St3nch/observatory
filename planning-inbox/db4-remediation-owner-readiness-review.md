# DB-4 Remediation Owner Readiness Review

Status: owner-readiness review; no implementation or execution authority
Date: 2026-07-14
Milestone: DB-4 remediation R1/R2/R4 planning checkpoint
Authority: `decisions/2026-07-14-db4-audit-acceptance-and-remediation-activation.md`

## Review question

Is the first DB-4 remediation planning package complete enough to proceed from broad
audit findings into an exact bounded implementation-package specification without
resuming PostgreSQL execution?

## Reviewed artifacts

```text
planning-inbox/db4-audit-remediation-program-v0-1.md
planning-inbox/db4-db3-implementation-traceability-matrix.md
planning-inbox/db4-migration-history-redesign-options.md
planning-inbox/db4-behavioral-hammer-remapping.md
audits/observatory-db1-through-db4-full-independent-audit.md
planning-inbox/db3-fresh-postgres-design-specification-v0-1.md
planning-inbox/db3-accepted-input-traceability-matrix.md
hammers/hammer-matrix-v0-2.md
hammers/acceptance-gate-policy-v0-2.md
hammers/per-hammer-result-register-v0-1.md
```

## Verdict

```text
R1 traceability planning: ready for exact implementation-package derivation
R2 migration/history architecture: ready with Option B selected as recommended design
R3 physical candidate implementation: not yet authorized
R4 behavioral hammer design: ready for exact manifest derivation
R5 result-register implementation design: still required in the next package
R6 security hardening implementation design: still required in the next package
R7 restart-reduction implementation design: partially defined; exact manifest still required
PostgreSQL execution: not authorized
DB-4 closure: not ready
DB-5: inactive
```

## What is now resolved

### 1. Current schema disposition

The current nine migrations are diagnostic harness candidates only. They cannot be
promoted into the DB-4 exit migration set or the DB-5 bootstrap set.

The remediation path will rebuild the candidate set to implement the accepted DB-3
physical relation catalog and enforcement mechanisms.

### 2. Traceability standard

Every accepted DB-2/DB-3 responsibility must map to:

```text
migration
physical object
constraint/index
role/RLS behavior
rollback
behavioral hammer
sabotage candidate
result record
```

No implementation row may claim fidelity through prose alone.

### 3. Migration/history outcome

Required outcome is fixed:

- one backend session;
- one transaction for DDL and history;
- immutable append-only history;
- no `ON CONFLICT DO UPDATE` identity rewrite;
- advisory serialization;
- fixed timeouts;
- pinned search path;
- before/after fingerprints sensitive to enforcement objects;
- rollback represented through append-only execution events.

Recommended implementation is runner-owned single-session execution using a fixed,
deterministic wrapper or equivalent fixed session API. Migration-owned history is the
fallback only if the recommended design cannot be safely proven.

### 4. Hammer meaning

The accepted H1-H22 meanings remain unchanged. The implementation must stop using
hammer IDs for unrelated catalog-count checks.

Mandatory DB-4 hammers are behavioral:

```text
H1 H2 H3 H4 H5 H6 H12 H15 H19 H20 H21 H22
```

Structural checks are preconditions. Passing behavior requires a real permitted or
hostile operation and an observed outcome.

### 5. Broken candidate meaning

Broken candidates must either:

- traverse the real migration admission path; or
- sabotage the exact enforcement mechanism exercised by a behavioral hammer.

Fixture-name and known-column detectors are insufficient.

### 6. Role/RLS proof

Role and scope behavior must be executed through bounded role switching.

Superuser catalog inspection cannot prove RLS or least privilege. FORCE RLS, WITH
CHECK, explicit grants, deterministic ownership, and same/cross-scope behavior must be
mechanically tested.

### 7. Restart reduction

Data-driven exact-path SHA-bound profiles are the preferred redesign. Python remains a
bounded generic executor over a closed action vocabulary. This should allow most
hammer/fixture/check corrections without MCP restart or connector action refresh.

Implementation hot reload remains deferred.

## Audit finding coverage check

| Audit finding group | Planning disposition |
|---|---|
| F-01 durable proof | accepted; exact R5 package still required |
| F-02 tool registry | secondary reconciliation; not central blocker |
| F-03/F-07 hammer mismatch/decorative profiles | behavioral and data-driven redesign defined |
| F-04/F-12/F-25 migration/history | atomic immutable architecture and rollback event model defined |
| F-05/F-13 skeletal schema | DB-3-faithful rebuild required; relabel-only path rejected |
| F-06 role/RLS | FORCE/WITH CHECK/SET ROLE behavior required |
| F-08/F-09 authority/marker | accepted; exact R6 package still required |
| F-10 broken detectors | real admission path and semantic sabotage required |
| F-11 stale authority | corrected in remediation activation commit |
| F-14 concurrency | real project identities and forced overlap required |
| F-15 failure evidence/cleanup | all items retained; cleanup attempted and verified |
| F-16 redaction/config | accepted; exact R6 package still required |
| F-17 validator | metadata chain, pair SHA, symlink, duplicate, forbidden transaction checks required |
| F-18 role residue | one recorded create/use/drop lifecycle required |
| F-19–F-23 lower findings | incorporated in relevant workstreams |
| F-24 remote exposure | mandatory verification/hardening; exact R6 package still required |

No audit finding other than the deprioritized tool-count issue has been discarded.

## Gaps that block implementation authorization

The following exact planning artifacts still need to be prepared:

```text
planning-inbox/db4-remediated-migration-and-schema-package-specification.md
planning-inbox/db4-result-register-emission-and-review-specification.md
planning-inbox/db4-security-and-operational-hardening-specification.md
planning-inbox/db4-data-driven-profile-and-restart-reduction-specification.md
planning-inbox/db4-exact-remediation-implementation-manifest.md
planning-inbox/db4-exact-remediation-execution-runbook.md
planning-inbox/db4-remediation-implementation-owner-gate.md
```

The implementation manifest must list every exact path to create, replace, retain,
retire, or delete in both Observatory and `ob-dev`.

## Required implementation package boundaries

The next package must explicitly decide:

1. whether existing thin migrations are deleted, archived, or replaced in place;
2. exact new migration split and filenames;
3. exact relation/constraint/index inventory per migration;
4. exact rollback files and destructive-safety rules;
5. exact migration metadata format;
6. exact single-session runner mechanism;
7. exact fingerprint canonicalization algorithm;
8. exact data-driven profile/check manifest schemas;
9. exact closed action vocabulary;
10. exact functional disposable role profiles;
11. exact result-record local and tracked paths;
12. exact failure/supersession/review workflow;
13. exact authority/marker/redaction/network controls;
14. exact test files and integration profiles;
15. exact validation order;
16. expected MCP registry after reconciliation;
17. planned restart count and owner actions;
18. exact clean disposable re-execution sequence.

## Suggested bounded implementation batches

### Batch P1 — Migration substrate and validator

Goal:

- implement single-session migration/history;
- immutable history;
- advisory lock/timeouts/search path;
- strong fingerprints;
- metadata and package validator.

Do not expand the full schema until this substrate passes sabotage tests.

### Batch P2 — Governance and capture spine

Goal:

- implement 001–003 responsibilities from the traceability matrix;
- scopes, vocabularies, assignments, panels, packages, captures, validation,
  providers, fingerprints, parser support, drift.

### Batch P3 — Evidence/raw/audit spine

Goal:

- implement 004–006 responsibilities;
- candidate/admission/observation/evidence/citation identities;
- raw support boundary;
- append-only and audit-first enforcement;
- audit/security relations.

### Batch P4 — Roles, RLS, and typed-read physical boundary

Goal:

- deterministic owners/grants;
- functional NOLOGIN profiles;
- FORCE RLS and WITH CHECK;
- bounded scope context;
- security-barrier views/functions.

### Batch P5 — Data-driven behavioral hammers

Goal:

- implement closed action vocabulary and profile loader;
- remap H1/H2/H3/H4/H5/H6/H12/H15/H19/H20/H21/H22;
- implement semantic sabotage candidates and cleanup verification.

### Batch P6 — Durable proof and security hardening

Goal:

- immutable result records;
- full-envelope redaction;
- authority binding;
- marker identity;
- network/tunnel hardening verification;
- role and disposable cleanup records.

### Batch P7 — One-restart integration and owner gate

Goal:

- complete all code changes before restart;
- validate both repos;
- one owner restart/connector refresh if tool surface or implementation code changed;
- no PostgreSQL mutation yet;
- prepare exact execution decision.

### Batch P8 — Fresh disposable proof

Separately authorized only after P1–P7 are accepted.

## Stop conditions for the next planning/implementation package

Stop if:

- any DB-3 relation responsibility is silently omitted;
- the current thin schema is presented as final;
- migration and history use separate sessions or commits;
- fingerprint excludes enforcement objects;
- hammer IDs remain attached to unrelated catalog checks;
- role/RLS behavior is tested only as superuser;
- broken migrations bypass the real admission path;
- result records can be overwritten or omit failures;
- caller SQL or generic shell is introduced;
- remote mutation exposure remains unreviewed;
- a package requires repeated restart-after-every-detector-edit workflow;
- PostgreSQL execution begins before a separate owner gate.

## Readiness conclusion

The remediation program has enough precision to begin the **next exact planning
package**, not implementation.

The next action is to create the seven missing exact package artifacts named above,
derive a complete path manifest for Observatory and `ob-dev`, validate that package,
and present it for owner acceptance.

No further hostile fixture execution or incremental patching of the old hammer harness
should occur before that gate.
