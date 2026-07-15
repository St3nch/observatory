# DB-4 Behavioral Hammer Remapping

Status: remediation planning candidate; not execution authority
Version: 0.1
Date: 2026-07-14
Milestone: DB-4 remediation R4 planning
Authority: `decisions/2026-07-14-db4-audit-acceptance-and-remediation-activation.md`
Hammer authority: `hammers/hammer-matrix-v0-2.md`

## Purpose

Replace catalog-count checks and fixture-specific detectors with behavioral hostile
proof that maps exactly to accepted hammer meanings.

A structural catalog query may establish a precondition. It cannot earn a hammer pass
unless the accepted hostile claim is itself structural.

## Execution model

Each hammer definition must declare:

```text
hammer_id
contract_revision
applicability
database class
required role
setup profile
permitted operation
hostile operation
expected SQLSTATE or bounded result
cleanup profile
sabotage profile
proof class
result-record schema version
```

Execution rules:

- load definitions from exact-path SHA-bound repository manifests at call time;
- no caller SQL;
- use one generic bounded executor for approved statement/action types;
- execute all checks in a profile even after one fails where safety permits;
- preserve every pass/fail/blocked item;
- always attempt cleanup and verify cleanup;
- record role, backend identity, database identity, migration set, and authority;
- a hammer must fail when its enforcement mechanism is deliberately sabotaged;
- expected failure must be classified by SQLSTATE or fixed bounded result, not fragile
  stdout line matching.

## Structural precheck class

Examples that remain useful but are not hammer passes:

- relation exists;
- constraint exists;
- RLS enabled/forced flag exists;
- policy exists;
- trigger exists and is enabled;
- role/grant exists;
- index exists;
- migration-history row count;
- schema fingerprint matches expected.

Every behavioral hammer may require these prechecks, but its pass is earned by actual
allowed/denied behavior.

## H1 — Scope isolation

### Accepted hostile claim

Scope-bound facts cannot be read, written, linked, or resolved across scope boundaries.

### Required setup

- two scopes A and B;
- scope-bound capture/candidate/observation/evidence fixtures in each;
- bounded reader and ingest role profiles;
- FORCE RLS and WITH CHECK policies active;
- transaction-local scope context set through bounded interface.

### Required actions

1. reader scoped to A reads A evidence successfully;
2. reader scoped to A cannot see B evidence;
3. reader scoped to A receives uniform blocked/not-found result for B handle;
4. ingest scoped to A cannot insert/update a row bound to B;
5. cross-scope lineage FK/composite check rejects A candidate linked to B capture;
6. owner/superuser execution is not accepted as role proof.

### Sabotage

- remove FORCE RLS;
- change policy to `USING (true)`;
- remove WITH CHECK;
- remove composite scope constraint.

Each sabotage must cause the hammer or mutation-test suite to fail.

## H2 — Rights fail-closed

### Accepted hostile claim

Missing, unknown, blocked, revoked, expired, or incompatible rights prevent capture,
candidate creation, admission, raw use, evidence resolution, and typed read.

### Required actions

- complete active assignment permits the bounded action;
- missing assignment blocks;
- unknown vocabulary entry blocks;
- revoked/expired transition blocks;
- assignment for wrong target/source family blocks;
- stale cached/current boolean cannot bypass transition-derived state.

### Expected evidence

Specific blocked result plus zero consequential rows and zero evidence mint.

### Sabotage

Remove the rights gate from one bounded transaction interface; hammer must fail.

## H3 — Retention enforcement

### Accepted hostile claim

Retention posture and deadlines fail closed, and purge lifecycle is represented by
authorized transitions rather than casual deletion.

### Required actions

- active posture with valid required deadline permits;
- applicable posture without deadline rejects;
- expired/purge-due state blocks new use/admission/read as defined;
- purge transition removes support through approved path while retaining only allowed
  append-only proof;
- direct DELETE by application role rejects;
- contradictory transitions reject.

### Sabotage

- make deadline nullable without conditional check;
- bypass retention gate;
- grant DELETE.

## H4 — Customer-private rejection

### Accepted hostile claim

Customer records, customer first-party analytics, private payloads, credentials, and
private dashboard/storage locators cannot enter Observatory structures or error/proof
records.

### Required actions

- schema/package validator rejects forbidden customer/private field candidates;
- bounded write rejects private-field key/value classes;
- validation failure does not echo rejected payload;
- result envelope redaction removes URI credentials and secret patterns;
- no hash of private overlay/customer value is stored as workaround.

### Sabotage

Add a customer email/account/private analytics column or permit raw exception payload;
validator/hammer must fail.

## H5 — No strategy or recommendation storage

### Accepted hostile claim

No strategy, recommendation, conclusion, priority, provider-winner, score-as-truth,
claim prose, report state, or LLM reasoning persistence exists through columns,
relations, JSON, logs, or proof metadata.

### Required actions

- package/schema allowlist rejects forbidden semantic names and responsibilities;
- bounded JSON schemas reject forbidden keys;
- attempt to insert strategy/recommendation key through allowed metadata field rejects;
- provider testimony remains attributed and cannot be promoted to truth field/table.

### Sabotage

Add `recommended_action`, `priority_score`, `winner_provider`, `conclusion`, or generic
unbounded JSON escape hatch; hammer must fail.

## H6 — CapturePackage and admission-envelope validation

### Accepted hostile claim

No capture or admission proceeds with an incomplete, inconsistent, unauthorized, or
exhausted envelope.

### Required actions

- complete valid package permits one bounded capture;
- missing scope/source/instrument/authority/rights/retention/ceiling/stop condition
  rejects;
- package not in valid transition state rejects;
- exhausted/cancelled/blocked package rejects;
- candidate admission without successful validation and required provenance rejects;
- rejected transaction leaves no partial candidate/observation/evidence/audit rows.

### Sabotage

Drop one NOT NULL/FK/check or bypass transaction validator; hammer must fail.

## H12 — Raw archive/manifest integrity

### Accepted hostile claim

Raw support identity, manifest facts, hash, bytes, media type, parser/support state,
rights/retention, and opaque token remain distinct and valid; raw bytes and locators
cannot enter ordinary relational storage or typed reads.

### Required actions

- valid manifest/support fixture passes;
- invalid hash grammar or algorithm mismatch rejects;
- negative/mismatched byte count rejects;
- path, URI, drive letter, bucket/key, signed URL, or connection string in token/fields
  rejects;
- raw bytes/blob field candidate rejects;
- reader cannot access opaque token;
- purged/unavailable/rights-blocked support is not presented active.

### Sabotage

Rename locator field to evade name matching; semantic detector must still reject based
on value/type/responsibility contract.

## H15 — Evidence identity and citation integrity

### Accepted hostile claim

Scope, target, capture, candidate, observation, evidence, raw, provider, and citation
identities remain distinct; evidence/citation exists only after valid admission and
resolves safely.

### Required actions

- candidate ID cannot resolve as evidence/citation;
- observation ID cannot be accepted as citation handle;
- governed target cannot substitute for evidence identity;
- pre-admission evidence mint rejects;
- duplicate evidence mint race yields one accepted identity;
- citation handle meets entropy/grammar/length requirements;
- handle resolution applies scope/status/rights/retention checks;
- deprecated/blocked handle does not resolve active evidence.

### Sabotage

Use a polymorphic resolver or shared identifier column; hammer must fail.

## H19 — Append-only observations and history

### Accepted hostile claim

Immutable and append-only facts cannot be updated or deleted directly or indirectly.
Corrections use superseding facts/transitions.

### Required actions

Under bounded non-owner roles, attempt UPDATE and DELETE on:

- observation;
- candidate/admission transition;
- evidence identity transition;
- raw integrity observation;
- audit event;
- migration history.

All reject with expected bounded error/SQLSTATE. A valid superseding transition insert
must succeed.

### Sabotage

- disable trigger;
- replace trigger body with permissive return;
- grant UPDATE/DELETE;
- expose mutable current-status interface.

## H20 — Concurrency safety

### Accepted hostile claim

Concurrent duplicate capture, admission, evidence mint, and effective policy assignment
produce one deterministic accepted outcome, no fork, and retry-safe classification.

### Required actions

- force actual overlap with worker A holding transaction/lock;
- worker B attempts same duplicate-prevention key;
- exactly one capture outcome accepted;
- exactly one admission outcome per candidate;
- exactly one evidence mint for accepted binding;
- conflicting terminal transition rejects;
- advisory/row lock timeout is classified, not mistaken for success;
- no control-plane probe table substitutes for project relations.

### Required evidence

Per-worker start, overlap marker, backend/session ID, result/SQLSTATE, final row set,
and cleanup.

### Sabotage

Remove unique constraint or expected-prior/locking mechanism; race test must produce a
fork and therefore fail.

## H21 — Audit-first same-transaction enforcement

### Accepted hostile claim

Every consequential write has its required audit event before commit in the same
transaction; missing or failed audit rolls back all consequential facts.

### Required actions

- paired valid consequential transition + audit commits;
- same transition without audit fails at commit;
- audit insert failure rolls back base/transition write;
- mismatched target/action/pairing key fails;
- after-commit application log does not satisfy the database check;
- audit event UPDATE/DELETE rejects.

### Sabotage

Disable deferred constraint trigger/pairing check; hammer must detect unpaired commit.

## H22 — Migration forward, rollback, failure, and recovery

### Accepted hostile claim

Exact SHA-bound migrations execute atomically, serialize, record immutable history,
produce meaningful fingerprints, roll back according to policy, and recover from
failure without partial accepted state.

### Required actions

- valid forward commits DDL and history together;
- failure after DDL leaves neither DDL nor history;
- history insertion failure leaves no DDL;
- duplicate version/same SHA follows explicit reapply policy;
- duplicate version/different SHA rejects;
- history UPDATE/DELETE rejects;
- concurrent migration is serialized;
- search-path hijack fails;
- before/after fingerprint changes correctly;
- dropping trigger/policy/FK changes fingerprint;
- valid disposable rollback inserts immutable rollback event and reverses intended
  objects only;
- unsafe rollback with dependencies fails without partial teardown;
- semantic recovery verification checks more than schema count.

### Sabotage

Every audit-listed migration/history defect becomes a named broken candidate.

## Secondary/future hammer mapping preserved by DB-4 schema

DB-4 must preserve physical support for these later hammers without claiming a full
DB-4 pass where the required surface belongs later:

| Hammer | DB-4 physical responsibility | Later primary gate |
|---|---|---|
| H7 | authority/ceilings/stop/duplicate structures | DB-9 |
| H8 | provider attribution and no disagreement truth | DB-7/DB-9 |
| H9 | policy assignments; freshness/volatility derived | DB-7/DB-9 |
| H10 | context and overclaim-safe read support | DB-7/DB-9 |
| H11 | source/instrument admission and marketplace ceiling | DB-9 |
| H13 | fingerprints/parser/drift quarantine | DB-9 |
| H14 | immutable panel versions/run binding | DB-6/DB-9 |
| H16 | no overlay/report persistence; request-only inputs | DB-7 |
| H17 | role and typed-read access boundary | DB-4 mechanical subset, DB-5/DB-7 full |
| H18 | identifier/size/grammar/safe-error enforcement | DB-6/DB-7/DB-9 |

Any deferred result requires `not_applicable_with_reason` or the correct blocked status,
not pass.

## Broken-candidate architecture

### Candidate classes

1. `migration_admission_reject` — candidate must be refused before execution/history;
2. `transaction_failure` — PostgreSQL executes but transaction aborts with no residue;
3. `semantic_invariant_failure` — syntactically valid schema change is applied only in
   isolated sabotage substrate and the named behavioral hammer must fail;
4. `role_security_failure` — privilege/RLS sabotage must be detected under SET ROLE;
5. `result_security_failure` — secret/private/error payload must be redacted/rejected.

### Isolation

Preferred:

- one fresh/reset disposable database per destructive candidate class; or
- one transaction/savepoint only when rollback reliably removes every object and
  cleanup is verified.

No fixture may contaminate a later result silently.

### Real admission path

Migration candidates must use the same:

- path/SHA metadata validation;
- authority binding;
- database marker verification;
- single-session transaction;
- advisory lock;
- history rules;
- result emission;

as valid migrations. A special direct `psql -f` route does not prove migration
admission behavior.

## Result aggregation

A profile result must include all items:

```text
precheck results
behavioral action results
sabotage/mutation results
cleanup results
blocked/not-applicable reasons
overall status
```

The executor must not discard already-completed items when a later item fails.

## Data-driven manifest design

Repository manifests should define bounded actions using a closed vocabulary such as:

```text
catalog_assert
transaction_insert
transaction_update_expect_reject
transaction_delete_expect_reject
set_role_read
set_role_write_expect_reject
function_call_expect_result
migration_apply_expect_success
migration_apply_expect_reject
concurrent_action_profile
cleanup_action
```

The Python executor maps these fixed action types to fixed templates. Manifests may
supply only validated identifiers, fixture IDs, expected SQLSTATE/result, and exact
paths/SHA values. They may not supply arbitrary SQL.

This permits hammer corrections without MCP restart while preserving the no-arbitrary-
SQL boundary.

## R4 planning exit

R4 is owner-ready when:

- every mandatory DB-4 hammer above has exact positive, negative, sabotage, and
  cleanup behavior;
- role identity and expected SQLSTATE/result are specified;
- no object-count check is presented as the hammer pass;
- broken candidates traverse the real path;
- data-driven action vocabulary is closed and safe;
- result aggregation and immutable record requirements are exact;
- implementation and real PostgreSQL execution remain separately gated.
