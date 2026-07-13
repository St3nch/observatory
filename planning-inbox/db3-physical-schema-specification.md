# DB-3 Physical Schema Specification

Status: DB-3 specification draft; no DDL or execution authority
Date: 2026-07-13
Milestone: DB-3 — Postgres Operational Boundary and Physical Schema Specification
Normative input: accepted DB-2 physical data-contract freeze v0.1.1

## Purpose

Derive a physical PostgreSQL schema specification from the accepted logical freeze without writing SQL, creating objects, or authorizing migration execution.

This document defines schema families, table responsibilities, key and relationship strategy, append-only and audit-first mechanisms, index/constraint intentions, exposure boundaries, and migration implications.

## Non-authorization boundary

```text
No SQL or DDL files.
No migration files or execution.
No PostgreSQL database or role creation.
No disposable database lifecycle.
No PostgreSQL hammer execution.
No persistence or ingestion.
No customer/private data.
No raw capture or production.
```

## Schema-family boundary

The future governed database should use explicit schema families rather than one unrestricted namespace.

| Schema family | Purpose | Ordinary application exposure |
|---|---|---|
| `obs_core` | Scope, source, panel, capture, candidate, observation, evidence, raw-manifest metadata | Controlled write paths; no direct LLM access |
| `obs_governance` | Rights, retention, vocabulary versions, admission authority references | Governed administration only |
| `obs_audit` | Consequential audit events and immutable transition history | Auditor/internal only |
| `obs_ops` | Migration history, operational attempt metadata, security-access logs | Operations/internal only |
| `obs_read` | Approved read views or bounded read functions for typed evidence access | Read-only role only |

Names are specification candidates. DB-4 migration files must use the accepted names exactly or return to owner review.

## Identity strategy

### Logical identifiers

All Observatory identities remain application-visible stable logical identifiers. They are not direct row addresses and do not encode customer identity, strategy, conclusion, provider truth, or workflow state.

Required identity classes include:

```text
scope_id
source_family_id
capture_instrument_id
query_panel_id
query_panel_version_id
capture_package_id
capture_attempt_id
candidate_observation_id
observation_id
evidence_id
citation_handle_id
raw_manifest_id
raw_artifact_pointer_id
shape_fingerprint_id
drift_event_id
audit_event_id
security_access_log_id
```

### Surrogate row keys

A future physical design may use internal numeric or UUID row keys for join efficiency, but they must never replace or leak as evidence identity. Every externally meaningful concept retains its stable logical ID with a uniqueness constraint.

### External identifiers

Provider job IDs, consumer references, report-safe references, parser commits, and overlay references remain typed external values attached to their owning context. They never serve as primary Observatory evidence keys.

## Core table responsibility map

These are physical responsibilities, not DDL.

| Table responsibility | Schema | Primary classification | Key relationships | Write posture |
|---|---|---|---|---|
| scope registry | `obs_core` | durable | owns capture packages and scoped observations | governed administration |
| source-family vocabulary/version | `obs_governance` | versioned | referenced by instruments, packages, manifests | governance only |
| capture-instrument vocabulary/version | `obs_governance` | versioned | belongs to source family | governance only |
| query-panel definition | `obs_core` | versioned | owns immutable panel versions | governed panel path |
| query-panel version | `obs_core` | versioned | immutable after use | governed panel path |
| capture package | `obs_core` | append_only | scope, source family, instrument, optional panel version | capture preflight |
| capture attempt | `obs_core` | append_only | belongs to package | capture runner only |
| provider job context | `obs_core` | external context | belongs to attempt | copied from admitted provider response |
| candidate observation | `obs_core` | durable, non-evidence | belongs to attempt/package | bounded extraction path |
| admitted observation | `obs_core` | append_only | sourced from candidate; scoped | admission transaction |
| observation status history | `obs_core` | append_only | belongs to observation | governed status transition |
| evidence identity | `obs_core` | durable | resolves to admitted observation bundle | minted during admission |
| evidence-observation link | `obs_core` | append_only | many-to-many only when bounded bundle justified | admission transaction |
| internal citation mapping | `obs_core` | durable | resolves to evidence identity | controlled evidence mapping |
| raw manifest | `obs_core` | append_only | belongs to attempt/package; optional pointer | bounded raw-support path |
| opaque artifact pointer | `obs_core` | durable internal locator | belongs to raw manifest | bounded artifact boundary |
| shape fingerprint | `obs_core` | append_only | attempt, source family, parser version | parser path |
| parser implementation reference | `obs_core` | external version reference | referenced by fingerprints and candidates | release lineage registration |
| drift event | `obs_core` | append_only | prior/new fingerprints | drift detection path |
| rights vocabulary/version | `obs_governance` | versioned | referenced by assignment history | governance only |
| rights assignment history | `obs_governance` | append_only | binds source/scope/evidence context | governed review path |
| retention vocabulary/version | `obs_governance` | versioned | referenced by assignment history | governance only |
| retention assignment history | `obs_governance` | append_only | binds source/scope/evidence/raw context | governed review path |
| audit event | `obs_audit` | append_only | entity type/id and transaction correlation | same transaction as change |
| security access log | `obs_ops` | append_only operational | caller/request/scope result | API/MCP boundary |
| migration history | `obs_ops` | append_only operational | migration version/hash/commit | migrator only |

## Deliberately absent tables

No table or hidden store may represent:

```text
customer records or customer identity
customer first-party analytics
customer reports or delivery state
strategy
recommendations
action plans
accepted conclusions
provider winner/composite truth
persistent disagreement summaries
persistent freshness/claim-use conclusions
LLM reasoning or scratch memory
Neon Ronin operational state
Kaizen governance state
SearchClarity workflow state
raw bytes in ordinary relational rows
credentials or connection strings
```

## Relationship and cardinality specification

### Scope and capture

- One scope may own many capture packages.
- Every capture package belongs to exactly one scope.
- A capture package references exactly one source-family version and one capture-instrument version.
- A package may reference one query-panel version where applicable.
- A package may have many attempts.

### Candidate and admission

- An attempt may produce zero or many candidates.
- Every candidate belongs to exactly one package and one attempt or an explicitly accepted manual extraction context.
- A candidate may produce at most one admitted observation.
- Rejection does not delete candidate history when retention permits metadata retention.

### Evidence

- Every admitted observation may belong to one or more evidence bundles only when the bundle contract is explicit.
- Every evidence identity resolves to at least one admitted observation.
- Evidence identity cannot exist before admission.
- Citation handles map to one evidence identity and never to raw/provider/customer identity.

### Raw support

- An attempt may have zero or many raw manifests.
- A raw manifest may have zero or one opaque artifact pointer.
- Missing/purged/unavailable raw bytes remain represented by manifest status where retention allows the manifest.
- Raw bytes remain outside ordinary relational evidence records.

### Drift

- A shape fingerprint belongs to one attempt/source context and references one parser implementation version.
- A drift event references prior and new fingerprints where available.
- Drift status does not encode provider quality conclusions.

## Lifecycle-state representation

Current state and historical transitions must be separated where silent overwrite would destroy evidence.

Use append-only history responsibilities for:

```text
observation status
rights assignment
retention assignment
raw support/purge status
source/instrument admission posture
scope blocking/inactivation where consequential
evidence status
drift review status
```

A current-state projection may be derived through approved views, but the historical events remain canonical.

## Append-only enforcement specification

DB-4 migration/hammer work must select mechanisms that prove:

1. admitted observation content cannot be updated or deleted by ingest/read roles;
2. capture attempts, audit events, migration history, fingerprints, and drift events cannot be silently rewritten;
3. status changes append history rather than mutate historical facts;
4. corrections create superseding observations or status records;
5. governed deletion, where ever later allowed, requires a dedicated procedure, audit event, and retention/rights authority.

Candidate physical mechanisms for later proof:

- privilege denial on direct update/delete;
- narrowly scoped security-definer operations only if justified and hammerable;
- immutable-row triggers only where privilege boundaries alone cannot enforce the invariant;
- current-state views derived from append-only histories.

DB-3 does not choose SQL syntax. DB-4 must prove the selected mechanisms can fail under hostile roles.

## Audit-first same-transaction specification

Every consequential write must either commit its audit event in the same database transaction or not commit at all.

Consequential operations include:

```text
observation admission
candidate rejection with retained metadata
evidence identity minting
evidence supersession/withdrawal/invalidation
rights or retention assignment change
raw manifest verification/purge/status change
scope block/inactivation
source/instrument posture change
migration application or rollback
```

Audit events record:

```text
audit_event_id
event_type
entity_type
entity_logical_id
actor_class
authority_reference
reason_code
transaction_correlation_id
event_time
before_state_reference where permitted
after_state_reference where permitted
```

Audit rows must not contain credentials, raw payload bytes, strategy, conclusions, or customer/private data.

## Constraint strategy

### Required database-enforced constraints

- non-null logical identity and required provenance keys;
- uniqueness of every stable logical ID;
- uniqueness of provider job ID only within provider/endpoint context, not globally;
- allowed status/vocabulary references through versioned governance records;
- evidence identity requires at least one admitted-observation link before exposure;
- citation handle maps to exactly one evidence identity;
- candidate-to-observation maximum one admitted observation;
- raw pointer requires a raw manifest;
- `raw_retained` status requires a valid pointer and verified hash state;
- capture-and-purge posture requires a purge deadline;
- no-storage/forbidden retention cannot coexist with a retained raw pointer;
- captured/admitted timestamps use UTC-aware values;
- package source/instrument versions must be admitted for the intended context before later execution;
- migration history version and hash pairs are unique and immutable.

### Application-plus-database constraints

Some rules require both typed application validation and database proof:

- customer/private-data rejection;
- strategy/recommendation/conclusion rejection;
- scope authorization;
- rights/retention fail-closed behavior;
- source-family-specific raw posture;
- claim-use and freshness warnings;
- cross-scope read prohibition.

Database constraints must catch structurally representable violations; typed boundaries catch semantic hostile input. Neither substitutes for the other.

## Index strategy

Indexes exist to support bounded accepted reads and enforcement, not speculative analytics.

Candidate index families:

- unique logical ID indexes;
- package/attempt lookup by scope and captured/started time;
- candidate lookup by package/attempt/status;
- observation lookup by scope, source family, captured time, and evidence status;
- evidence-to-observation resolution;
- current status-history lookup by entity and effective time;
- rights/retention assignment lookup by target and effective time;
- raw manifest lookup by attempt, hash, support status, and purge due time;
- drift lookup by source family, endpoint/surface, fingerprint, and detected time;
- audit lookup by entity logical ID, event type, transaction correlation, and event time;
- migration history lookup by version and applied time.

Forbidden speculative indexes/materializations:

```text
provider winner
opportunity score
customer aggregate
cross-scope business intelligence
recommendation ranking
persistent disagreement score
```

Index selection must be justified by an accepted query or enforcement path and reviewed for write cost.

## Partitioning posture

No partitioning is required for the initial local database specification.

Reason:

- v1 evidence volume is unproven;
- speculative partitioning increases migration and restore complexity;
- query patterns must be measured before physical partition boundaries are earned.

The schema preserves time/scope/source keys so future partitioning remains possible through a separately accepted migration.

## JSON and extensibility posture

JSON storage is allowed only for bounded provider-attributed or observation-specific fields that cannot yet be normalized without losing source fidelity.

Rules:

- JSON is not a loophole for forbidden persistence;
- required envelope fields remain typed columns/responsibilities;
- JSON shape carries source family and parser/fingerprint lineage;
- JSON content remains rights/retention/scope governed;
- no strategy, recommendations, conclusions, customer data, credentials, or LLM reasoning;
- frequently queried/enforced fields must graduate to typed responsibilities through a reviewed migration.

## Raw artifact boundary

The relational database stores raw manifest metadata and an opaque pointer only when a source-family ruling permits it.

It does not store:

- arbitrary filesystem paths;
- bucket/object keys exposed to readers;
- raw credentials;
- provider payload bytes as generic JSON/blob rows;
- customer/private artifacts.

The pointer resolver belongs to a bounded internal artifact boundary and is not exposed to `observatory_reader`.

## Read-exposure design

`obs_read` exposes only approved typed shapes.

Candidate read surfaces:

```text
evidence resolution
scope-bounded evidence listing
observation provenance summary
freshness/rights/retention warning projection
raw-support status without locator
provider-attributed side-by-side evidence
```

Read surfaces must:

- bind scope authorization;
- provide deterministic pagination and honest truncation;
- hide raw locators, credentials, internal row keys, and unrestricted audit/security fields;
- respect withdrawn, expired, blocked, or invalidated status;
- return provider attribution and caveats;
- remain read-only.

No generic CRUD schema or direct LLM SQL access is specified.

## Migration grouping implications

A likely future migration sequence, subject to DB-4 specification and owner acceptance:

1. schemas, migration history, and base governance vocabularies;
2. scope/source/instrument/panel identities;
3. capture packages and attempts;
4. candidate/admitted observations and status histories;
5. evidence identities and mappings;
6. raw manifests, pointers, fingerprints, parser references, drift;
7. rights/retention histories;
8. audit-first mechanisms and security logs;
9. read-only views/functions and role grants;
10. final constraints/indexes and proof fixtures.

This sequence is a planning order only. It does not authorize migration files.

## Hammer mapping

| Physical mechanism | Hammers |
|---|---|
| Scope keys and scope-bound relationships | H1, H4, H16, H20 |
| Governance vocabularies and assignments | H2, H3, H11, H21 |
| Capture package/attempt constraints | H6, H7, H18, H20, H21 |
| Candidate/admission separation | H5, H6, H15, H19, H21 |
| Evidence identity/mapping | H1, H4, H12, H15, H19, H21 |
| Raw manifest/pointer separation | H2, H3, H12, H15, H17, H22 |
| Fingerprint/parser/drift | H13, H21, H22 |
| Append-only histories | H19, H20, H21, H22 |
| Audit-first transactions | H19, H20, H21, H22 |
| Typed read exposure | H1, H4, H9, H10, H15, H16, H17, H18 |
| Forbidden-persistence absence | H4, H5, H16, H17, H18 |
| Migration history and rollback | H21, H22 |

Mapping is not execution proof.

## DB-3 acceptance criteria for this schema specification

The physical specification is owner-ready when it:

- derives solely from the accepted DB-2 freeze;
- defines schema families and table responsibilities;
- preserves every identity layer;
- defines relationships and lifecycle-history behavior;
- specifies append-only and audit-first enforcement intentions;
- defines constraint and index strategy;
- preserves raw manifest/pointer/bytes separation;
- defines read exposure and role implications;
- explicitly excludes forbidden persistence;
- maps every mechanism to hammers;
- contains no SQL, DDL, migration file, database creation, or execution authority.

## Final rule

```text
The physical design may optimize how observations are stored.
It may not change what the Observatory is allowed to remember.
```
