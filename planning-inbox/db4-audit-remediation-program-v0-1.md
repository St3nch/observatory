# DB-4 Audit Remediation Program v0.1

Status: accepted remediation plan
Authority: `decisions/2026-07-14-db4-audit-acceptance-and-remediation-activation.md`
Milestone: DB-4 remediation
Source audit: `audits/observatory-db1-through-db4-full-independent-audit.md`

## Purpose

Turn the independent DB-1 through DB-4 audit into an exact, governed remediation sequence.

This plan does not close DB-4 and does not activate DB-5. It replaces the previous happy-path closure campaign with a traceable remediation program.

## Baseline rulings

- DB-1 remains trusted and complete.
- DB-2 remains trusted, accepted, and complete.
- DB-3 remains trusted, accepted, and complete as the physical-design authority.
- DB-4 remains active and is returned to remediation.
- DB-5 remains inactive.
- The current nine migrations are diagnostic harness candidates, not an accepted governed-bootstrap set.
- Prior disposable PostgreSQL output is diagnostic evidence, not closure evidence.
- All audit findings are considered except that MCP tool count is secondary and must not distract from technical correctness.

## Where this plan disagrees with or narrows the audit

### D-1 — MCP tool count is not a primary closure blocker

The audit is correct that documentation, tests, and accepted registry text drifted from 28/60 to 30/62. The plan does not treat the existence of the two additional bounded tools as a critical technical defect.

Required action:

- reconcile the accepted registry, README, tests, and authority text;
- retain useful bounded broken-candidate and role-cleanup capabilities unless later design removes them;
- never allow tool-count reconciliation to substitute for schema, hammer, or proof repairs.

### D-2 — Do not merely relabel the thin schema and defer the real design to DB-5

The audit offered relabeling the current migrations as harness-only as one bounded option. This plan rejects that as the final DB-4 path.

DB-4 is the Database Hammer Harness and Migration Specification milestone. Before closure, it must produce migration candidates that faithfully implement the accepted DB-3 physical responsibilities at the level required for later governed bootstrap.

The current thin set may be retained temporarily as test scaffolding, but it cannot be the DB-4 exit migration set.

### D-3 — Atomicity is mandatory; the exact implementation mechanism remains open until design review

The audit recommends that each migration file own its history INSERT as its final statement. The plan accepts the required outcome but does not yet mandate that exact mechanism.

Accepted requirement:

- DDL and history recording must occur in one database session and one transaction;
- no applied-without-history or history-without-application state may be possible;
- duplicate version or changed SHA must fail closed;
- history must be append-only.

The remediation design must compare migration-owned history, runner-owned single-session history, and other bounded approaches before selecting one.

### D-4 — Result records are mandatory; storage path and promotion flow require design

The audit recommends ignored local proof followed by committed redacted copies. This plan accepts durable immutable reviewable records but does not preselect the exact local/tracked path or promotion mechanism.

The design must guarantee:

- no secrets;
- immutable execution identity;
- failed and blocked results are preserved;
- corrections supersede rather than overwrite;
- owner review state is explicit;
- tracked records remain compact and reviewable.

### D-5 — Data-driven profiles are preferred; implementation hot reload is deferred

The audit’s data-driven profile recommendation is accepted and prioritized.

A reloadable implementation worker or `importlib.reload` action is not accepted yet. It adds runtime and safety complexity. Consider it only after data-driven profiles and restart batching are proven insufficient and after a separate security review.

### D-6 — Public ngrok exposure is a serious risk hypothesis that must be verified, not assumed

The audit’s security concern is valid. The exact claim that the endpoint is publicly reachable and unauthenticated must be verified against the actual connector/tunnel configuration.

Until verified, the operational rule is fail closed:

- elevated PostgreSQL capability and password exist only during owner-supervised proof windows;
- the tunnel is active only when needed;
- authentication or access restriction must be designed before future mutation-capable use;
- no closure claim may ignore this review.

## Finding disposition

| Finding | Disposition | Remediation batch |
|---|---|---|
| F-01 durable proof absent | accept | R5 |
| F-02 tool registry mismatch | accept as secondary governance drift | R0/R7 |
| F-03 mislabeled structural hammers | accept | R4 |
| F-04 mutable/non-atomic migration history | accept | R2 |
| F-05 skeletal schema | accept; require real DB-3 fidelity before closure | R3 |
| F-06 superuser-only RLS/role proof | accept | R3/R4 |
| F-07 decorative profile JSON | accept | R4/R7 |
| F-08 weak authority/digest semantics | accept | R6 |
| F-09 marker enforcement/identity gaps | accept | R6 |
| F-10 fixture-specific detectors | accept | R4 |
| F-11 stale authority text | accept | R0 |
| F-12 locking/timeouts/search_path/fingerprint gaps | accept | R2 |
| F-13 schema quality gaps | accept | R3 |
| F-14 weak concurrency test | accept | R4 |
| F-15 failure evidence/residue gaps | accept | R4/R5 |
| F-16 redaction/config drift | accept | R6 |
| F-17 shallow validator/tests | accept | R2/R4 |
| F-18 cluster role lifecycle | accept | R6 |
| F-19 annotation/capability inconsistencies | accept | R6/R7 |
| F-20 exact-count fragility | accept | R4 |
| F-21 weak restore semantics | accept; DB-4 scope to be defined honestly | R5/R6 |
| F-22 unknown database classification | accept | R6 |
| F-23 execution-order/cleanup caveats | accept | R4 |
| F-24 remote unauthenticated exposure | accept as mandatory verification and hardening item | R6 |
| F-25 rollback/history semantics | accept | R2 |

## Remediation workstreams

### R0 — Authority reconciliation and campaign freeze

Goal:
Make repository truth unambiguous before technical remediation.

Outputs:

- audit acceptance/remediation decision;
- roadmap, active-context, handoff, indexes, and post-v1 roadmap updates;
- current proof campaign labeled diagnostic only;
- current migrations prohibited from DB-5 promotion;
- tool registry drift recorded as secondary reconciliation;
- uncommitted `ob-dev` detector work either committed as diagnostic code or deliberately reverted in a separately reviewed action.

Exit criteria:

- all current-state files agree;
- `authority_sync` passes;
- no document says DB-4 is on the old closure path;
- no PostgreSQL execution is authorized by this planning batch.

### R1 — Exact DB-3 implementation traceability

Goal:
Prevent another simplified schema from being mistaken for the accepted design.

Required matrix columns:

```text
DB-2/DB-3 requirement
source path and section
physical responsibility
migration version/path
schema object
columns and types
constraints
indexes
role/RLS behavior
rollback behavior
behavioral hammer
broken/sabotaged candidate
result-record requirement
deferred justification, if any
```

Required coverage includes at minimum:

- scope classes and scope identity;
- rights and retention assignments;
- target anchors;
- provider registry/testimony boundaries;
- query panels and capture packages;
- capture events and validation;
- candidate/admission lifecycle;
- observation/evidence/citation identity separation;
- raw support manifests, payload/token boundaries, hashes, and bounded locators;
- provider drift/fingerprints where accepted;
- append-only evidence and audit behavior;
- consequential audit pairing;
- typed-read objects;
- migration/recovery metadata;
- accepted role profiles;
- all DB-4 hammer families.

Exit criteria:

- every accepted responsibility is implemented or explicitly deferred by owner ruling;
- no mapping row claims an object that does not exist;
- the matrix passes independent review before SQL replacement begins.

### R2 — Migration and history integrity redesign

Goal:
Create a migration substrate worthy of all later schema work.

Requirements:

- exact path and SHA validation;
- one-session/one-transaction DDL plus history;
- immutable append-only history;
- duplicate version and changed SHA rejection;
- before and after schema fingerprints;
- fingerprints sensitive to schemas, tables, columns, constraints, indexes, triggers, policies, functions, and ownership-relevant state;
- advisory serialization for migration execution;
- explicit lock timeout and statement timeout;
- pinned safe search path;
- deterministic object ownership;
- rollback-history semantics defined;
- partial failure and process interruption tests;
- metadata pair-SHA and version-chain validation;
- symlink/path escape checks;
- no `ON CONFLICT DO UPDATE` for accepted migration identity.

Exit criteria:

- sabotage tests prove history cannot be rewritten or split from schema state;
- migration validator and real PostgreSQL integration tests pass;
- exact design is reviewed before schema expansion.

### R3 — DB-3-faithful physical candidate rebuild

Goal:
Replace the skeletal migration set with an exact DB-3-derived candidate set.

Requirements:

- implement the accepted traceability matrix;
- include identifier grammar and bounded lengths where required;
- represent rights, retention, lifecycle, and identity responsibilities mechanically;
- use UTC-aware timestamps consistently;
- constrain JSONB responsibilities and avoid hidden interpretation/strategy fields;
- implement deterministic keys and idempotency constraints;
- implement accepted indexes without speculative over-indexing;
- implement FORCE RLS, WITH CHECK, grants, ownership, and bounded NOLOGIN role profiles;
- implement append-only evidence/audit mechanisms;
- implement audit-first same-transaction pairing where required;
- preserve telescope-not-astronomer doctrine.

Exit criteria:

- every migration/rollback pair maps truthfully to R1;
- schema review finds no missing accepted responsibility;
- no governed database is created.

### R4 — Behavioral hammer and hostile-candidate rebuild

Goal:
Make every claimed hammer prove the actual hostile contract.

Rules:

- structural catalog checks are preconditions, not hammer passes;
- each mandatory hammer performs a permitted or forbidden operation and verifies behavior;
- tests run under the intended role using `SET ROLE` or equivalent bounded role switching;
- RLS tests prove permitted same-scope reads, denied cross-scope reads, and denied writes;
- append-only tests execute UPDATE and DELETE and verify PostgreSQL rejection;
- audit-first tests attempt an unpaired consequential write and verify rejection;
- identity tests race real project identity/admission constraints, not a control-table PK;
- concurrency tests force overlap and verify one success plus a specific rejected outcome;
- broken candidates traverse the real migration admission path;
- detectors are semantic, not fixture-name or column-name matchers;
- all checks run and all results are retained even when some fail;
- cleanup is attempted and verified on every path;
- sabotage/mutation tests prove each hammer fails when its enforcement is weakened.

Exit criteria:

- hammer IDs exactly match accepted definitions;
- every mandatory family has positive and negative behavioral evidence;
- profile manifests and executed coverage cannot drift.

### R5 — Durable proof and closure evidence

Goal:
Implement the accepted per-hammer result-register contract.

Requirements:

- one immutable record per execution;
- exact code commit and dirty-tree status;
- exact database class and bounded identity;
- exact authority reference;
- exact migration paths and SHA values;
- exact profile/check identifiers;
- start/finish timestamps;
- expected and observed behavior;
- full failed/blocked/pass item set;
- secret-exposure review;
- evidence paths;
- owner/steward review state;
- supersession lineage rather than edits;
- validator that rejects incomplete or inflated proof;
- compact tracked closure package after secret review.

Exit criteria:

- every mandatory DB-4 family has reviewable `real_postgres_disposable_pass` evidence;
- failures from the campaign are preserved;
- no chat transcript is required to establish closure facts.

### R6 — Security and operational hardening

Goal:
Make DB-4 operations fail closed in real use.

Requirements:

- authority file exists and is bound to the startup environment;
- operation class must match explicit authority;
- confirmation digest documented as accident protection, not authorization;
- marker verified on every proof/mutation path;
- marker binds current database identity and creation authority;
- unknown database classification is unauthorized, not production;
- role creation/drop is one recorded lifecycle;
- redaction covers the entire result envelope and URI credentials;
- no credential or secret enters Git, tool output, or logs;
- network/tunnel authentication and reachability are verified and hardened;
- elevated capability/password windows are temporary and owner-supervised;
- backup/restore semantics are labeled honestly and separately gated where needed.

Exit criteria:

- security review passes;
- remote mutation surface is not unauthenticated;
- all test roles and disposable substrates are cleaned and recorded.

### R7 — Data-driven profiles and restart reduction

Goal:
Reduce owner restart pain without weakening safety.

Requirements:

- freeze the accepted tool surface after reconciliation;
- load profile/check definitions from exact-path, SHA-bound repository files at call time;
- fail on manifest/profile/check-ID drift;
- keep Python tools generic and bounded rather than encoding each hammer iteration;
- batch all code changes before one validated restart;
- add an owner-controlled restart command/script that validates first and starts only on green;
- do not add arbitrary shell, self-modifying behavior, or automatic code reload;
- consider reloadable workers only after separate review if data-driven execution is insufficient.

Exit criteria:

- hammer/profile corrections normally require no MCP tool-surface refresh;
- one implementation batch requires at most one planned restart;
- fixed-root and authority controls remain intact.

### R8 — Fresh disposable re-execution and closure review

Goal:
Generate closure-grade DB-4 evidence from a clean substrate.

Prerequisites:

- R0 through R7 accepted and implemented as applicable;
- exact execution manifest and authority decision;
- clean repositories and immutable commits;
- PostgreSQL environment identity verified;
- no governed database exists.

Campaign:

1. create marked identity-bound disposable database;
2. create bounded role profiles;
3. run forward migrations with atomic history;
4. verify full schema fingerprint/history;
5. run all behavioral passing hammers;
6. run all sabotaged/broken candidates through the real path;
7. run forced-overlap concurrency tests;
8. run reverse rollback and failure-recovery proof;
9. run bounded backup/restore only if DB-4 authority still requires it;
10. verify cleanup and cluster role removal;
11. validate and review result records;
12. prepare DB-4 closure proposal.

Exit criteria:

- every accepted DB-4 closure condition passes;
- no proof claim exceeds its recorded substrate;
- DB-5 remains inactive until a separate owner decision.

## Batch order

```text
R0 authority reconciliation
→ R1 traceability
→ R2 migration/history integrity
→ R3 physical schema rebuild
→ R4 behavioral hammers
→ R5 durable proof
→ R6 security hardening
→ R7 restart reduction
→ exact execution-package owner gate
→ R8 clean re-execution
→ DB-4 closure review
```

R2 and R7 may be designed in parallel after R1, but implementation order must preserve migration integrity before schema expansion and profile loading before repeated hammer iteration.

## Stop conditions

Stop on any:

- deviation from DB-2/DB-3 without explicit owner ruling;
- schema object with no traceability row;
- hammer ID that does not match its hostile claim;
- structural precheck labeled as behavioral pass;
- migration/history split transaction;
- mutable accepted history;
- superuser-only proof of role/RLS behavior;
- fixture-name detector presented as semantic rejection;
- missing or overwritten failure record;
- secret exposure;
- unverified marker or database identity;
- unauthenticated remote mutation surface;
- restart-heavy code iteration where data-driven behavior is feasible;
- governed database, provider, customer/private data, production, recurring work, or DB-5 activity.

## Immediate next work

Prepare R1 as one exact reviewable planning package:

```text
planning-inbox/db4-db3-implementation-traceability-matrix.md
planning-inbox/db4-migration-history-redesign-options.md
planning-inbox/db4-behavioral-hammer-remapping.md
planning-inbox/db4-remediation-owner-readiness-review.md
```

No PostgreSQL execution begins until those artifacts produce an exact implementation manifest and a separate owner gate.
