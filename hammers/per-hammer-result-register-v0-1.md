# Per-Hammer Result Register Contract v0.1

Status: accepted
Authority: repository proof-metadata contract accepted by `decisions/2026-07-13-db1-closure-and-db2-activation.md`; not Observatory evidence
Milestone: accepted at DB-1 closure; governs database-phase hammer proof records

## Purpose

Define one deterministic record shape for every future hammer execution so proof strength, substrate, authority, evidence, and review status cannot be blurred together.

The register is committed repository proof metadata. It is not an Observatory database table, observation family, audit-event substitute, or production telemetry system.

## Core rule

```text
One hammer execution produces one immutable result record.
Corrections create a new record that supersedes the old record.
No result is silently edited from fail or blocked into pass.
```

## Required record shape

```yaml
result_record_version: "0.1"
result_id: "stable repository-unique identifier"
hammer_id: "H1-H22 or later accepted hammer ID"
hammer_version: "accepted hammer definition version"
gate_id: "DB-1 through DB-10 or later accepted gate"
result: "pass | fail | blocked_not_implemented | blocked_contract_missing | blocked_owner_ruling_required | blocked_authority_missing | blocked_required_surface_missing | blocked_manual_review_required | not_applicable_with_reason"
proof_class: "defined_only | fixture_contract_pass | in_memory_behavior_pass | owner_local_process_pass | real_postgres_disposable_pass | real_local_database_pass | production_surface_pass"
required_proof_class: "proof class required by the gate"
execution_surface: "precise human-readable surface"
database_class: "none | disposable_postgres | governed_local | production"
database_identity: "non-secret bounded identifier or null"
code_repository: "repository name"
code_commit: "full immutable commit SHA"
contract_or_policy_versions:
  - "path@version-or-sha"
authority_reference: "decision path or null when execution is planning-only"
started_at: "UTC timestamp or null for defined_only"
finished_at: "UTC timestamp or null for defined_only"
runner: "bounded tool/profile/operator class"
inputs:
  fixture_ids: []
  migration_paths_and_sha256: []
  profile_ids: []
expected_behavior: "exact hostile claim under test"
observed_behavior: "bounded factual result summary"
evidence_paths: []
secret_exposure_review: "pass | fail | not_applicable"
result_integrity_review: "pending | accepted | rejected"
reviewer: "owner/steward identifier or null"
reviewed_at: "UTC timestamp or null"
supersedes_result_id: null
notes: "bounded caveats; no strategy or recommendation content"
```

## Field rules

### Identity

- `result_id` must be repository-unique and immutable.
- `hammer_id` must refer to an accepted hammer definition.
- `gate_id` must identify the milestone whose closure or entry the result informs.
- `supersedes_result_id` is used only for correction or rerun lineage.

### Result and proof class

- `pass` is invalid when `proof_class` is weaker than `required_proof_class`.
- `defined_only` may never use `result: pass` for an executed-behavior claim.
- fixture/mock/in-memory results cannot claim database, transaction, role, migration, concurrency, backup, restore, or production enforcement.
- a failed or blocked execution remains recorded even after a later pass.

### Execution surface

`execution_surface` must identify what actually ran, such as:

```text
local Python fixture suite
in-memory prototype handler
owner-local process against repository fixtures
disposable PostgreSQL 18 using accepted migration SHA
governed local Observatory database under read-only role
future production API/MCP surface
```

Vague values such as `real`, `local`, `integration`, or `works` are invalid.

### Database metadata

- `database_class` is mandatory.
- `database_identity` must never contain credentials, connection strings, filesystem secrets, or arbitrary locator data.
- `disposable_postgres` requires proof that the target belongs to the accepted disposable class.
- `governed_local` requires a decision-linked authority reference.

### Commit and contract binding

- `code_commit` must be a full SHA.
- dirty-tree execution must be explicitly recorded in `notes` and cannot be accepted for a governed migration or database-phase closure unless the applicable policy explicitly permits it.
- every executed migration must record exact repository-relative path and SHA-256.
- policy and contract versions must be bound by version, SHA, or immutable commit.

### Authority

- mutation, migration, provider, capture, governed-database, and production results require an exact `authority_reference`.
- missing authority produces `blocked_authority_missing`; it never produces pass.
- tool availability, credentials, prior approvals, and existing databases are not authority references.

### Evidence

`evidence_paths` must point to bounded repository or approved artifact-root records containing enough information to review the claim without exposing secrets.

Evidence should include, where applicable:

- structured runner output;
- relevant test profile result;
- migration SHA and transaction outcome;
- before/after schema or constraint inventory;
- failing-candidate proof;
- concurrency attempt summary;
- backup hash and restore verification;
- exact exception or error class.

Test count without hostile-case identity is insufficient.

### Review

- execution does not equal acceptance.
- `result_integrity_review: accepted` means the record accurately represents the execution and required proof class.
- a reviewer cannot upgrade proof class without new execution.
- rejected records remain preserved with their rejection reason.

## File organization

Recommended future layout:

```text
hammers/results/<gate-id>/<result-id>.yaml
```

A machine-readable index may summarize result IDs and statuses, but the individual immutable record remains authoritative.

The results folder is not earned merely by this contract. It should be created when the first authorized execution result needs to be committed.

## Validation requirements

A future register validator must reject:

- unknown hammer IDs;
- unknown proof classes or result values;
- pass below required proof class;
- missing commit SHA;
- missing authority for gated execution;
- missing migration SHA for migration execution;
- credential-like or connection-string fields;
- mutable overwrite of an existing result record;
- `not_applicable_with_reason` without an exact reason and reviewer;
- timestamps where finish precedes start;
- database proof with `database_class: none`;
- production proof without a separately accepted production gate.

## Example: bounded existing proof

```yaml
result_record_version: "0.1"
result_id: "db1-typed-read-corrections-attempt-2"
hammer_id: "H18"
hammer_version: "0.1"
gate_id: "DB-1"
result: "pass"
proof_class: "owner_local_process_pass"
required_proof_class: "owner_local_process_pass"
execution_surface: "owner-local Python fixture/in-memory suite"
database_class: "none"
database_identity: null
code_repository: "observatory"
code_commit: "commit recorded by the accepted proof artifact"
contract_or_policy_versions:
  - "contracts/typed-read-api-mcp-v0-1.md@0.1.1"
authority_reference: "decisions/2026-07-12-db1-contract-corrections-and-database-boundary-rulings.md"
started_at: null
finished_at: null
runner: "owner-local process"
inputs:
  fixture_ids: []
  migration_paths_and_sha256: []
  profile_ids: []
expected_behavior: "bounded hostile typed-read correction behavior"
observed_behavior: "188 tests passed; contract/prototype behavior only"
evidence_paths:
  - "planning-inbox/db1-typed-read-correction-proof.md"
secret_exposure_review: "not_applicable"
result_integrity_review: "accepted"
reviewer: "owner"
reviewed_at: null
supersedes_result_id: null
notes: "Not database, transaction, role, migration, persistence, network, concurrency, or production proof."
```

The example is illustrative. It does not retroactively create a machine-readable result file or broaden the accepted proof.

## Non-authorizations

```text
No database table or schema for hammer results.
No results directory creation before an authorized execution needs it.
No PostgreSQL execution.
No migrations.
No provider calls.
No production telemetry.
No strategy or recommendation storage.
```

## Final rule

```text
Proof must be harder to exaggerate than to record honestly.
```
