# DB-2 Physical Data-Contract Freeze Specification

Status: accepted DB-2 logical data-contract freeze
Date: 2026-07-13
Accepted by: `decisions/2026-07-13-db1-closure-and-db2-activation.md`
Active milestone: DB-2 — Physical Data-Contract Freeze

## Purpose

Define the exact logical data contract that DB-2 must freeze before DB-3 may derive any physical PostgreSQL schema.

This document consolidates accepted Observatory doctrine, contracts, DB-1 rulings, the C2 logical schema plan, and database-phase hammer expectations into one normative candidate.

It is not DDL. It is not a migration plan. It is not database authority.

## Authority and conflict order

This candidate remains subordinate to:

1. accepted decisions;
2. `02-boundaries.md`;
3. `ACTIVE_CONTEXT.md`;
4. `POST_V1_DATABASE_ROADMAP.md`;
5. accepted contracts;
6. this planning candidate.

If this file conflicts with higher authority, the higher authority wins and the conflict must be corrected before DB-2 activation.

## Non-authorization boundary

This document does not authorize:

```text
DB-2 activation
PostgreSQL database creation
role or credential creation
physical table, column, index, trigger, function, or schema design
DDL
migration files
migration execution
disposable database creation
real PostgreSQL hammers
synthetic or real persistence
provider calls or paid pulls
raw capture or artifact-store creation
customer/private data
production API/MCP
strategy, recommendation, or conclusion persistence
```

## Freeze classification vocabulary

Every concept in the accepted DB-2 freeze must receive exactly one primary classification:

| Classification | Meaning |
|---|---|
| `durable` | Canonical state may persist under accepted rights, retention, and lifecycle rules |
| `append_only` | Durable historical record that cannot be silently overwritten |
| `versioned` | New versions supersede prior versions while preserving history |
| `derived` | Computed at read time or rebuilt from canonical observations; not canonical stored meaning |
| `ephemeral` | May exist only during one bounded process or request and must not persist |
| `external` | Owned outside Observatory; only a bounded locator or reference may exist |
| `forbidden` | Must not exist in Observatory durable or hidden storage |
| `unresolved` | Cannot proceed until an explicit decision resolves the concept; fails closed |

A concept may carry a secondary behavioral qualifier such as `audit_first`, `rights_gated`, or `retention_gated`, but the primary classification must remain singular.

## Identity layers

The freeze must preserve distinct identities for:

```text
scope_id
source_family_id or accepted vocabulary identity
capture_instrument_id
query_panel_id
query_panel_version_id
capture_package_id
capture_attempt_id
provider_job_id
candidate_observation_id
observation_id
evidence_id
raw_manifest_id
raw_artifact_pointer_id
shape_fingerprint_id
parser_version_id
drift_event_id
audit_event_id
security_access_log_id
external_consumer_reference
report_safe_reference
external_overlay_reference
```

No physical design may collapse these layers merely because a generic `id` column is convenient.

Provider job IDs, raw IDs, database row IDs, customer IDs, report IDs, and workflow IDs must never impersonate `evidence_id`.

## Consolidated concept register

### 1. Scope

```text
classification: durable
identity owner: Observatory
lifecycle: active / inactive / blocked
required provenance: creation authority and scope-class assignment basis
scope relationship: owns all admitted observation context
rights relationship: scope does not override source rights
retention relationship: scope status cannot silently extend evidence retention
write authority: governed Observatory administration path only
read exposure: bounded scope identity and class; no customer-private identity
hammer implications: H1, H4, H5, H16
```

Allowed initial `scope_class` vocabulary:

```text
internal
customer_engagement
market_watch
```

A scope must not contain or encode customer name, email, order, report, seller-account, private analytics, or consumer workflow identity.

### 2. External consumer reference

```text
classification: external
identity owner: owning consumer
lifecycle: consumer-owned
required provenance: consumer class and bounded locator kind
scope relationship: may locate external context but cannot define Observatory identity
rights/retention: consumer-owned; must not import private payload
write authority: bounded registration only
read exposure: internal locator only where authorized
hammer implications: H1, H4, H16
```

It is not a cross-system foreign key and must not create customer-record ownership inside Observatory.

### 3. Source family

```text
classification: versioned vocabulary
identity owner: Observatory governance
lifecycle: candidate / admitted / blocked / retired
required provenance: decision or contract that established posture
rights relationship: binds source-family rights and raw-retention defaults
retention relationship: unknown family fails closed to forbidden_no_capture
write authority: owner-approved governance path
read exposure: provider/source attribution and current posture
hammer implications: H2, H3, H7, H8, H11, H12, H13
```

Accepted DB-1 raw-retention defaults:

| Source family | Default raw posture |
|---|---|
| controlled provider API payload | `capture_and_purge_raw` |
| public manual observation | `retain_manifest_only` |
| public page snapshot | `no_raw_storage` |
| AI/GEO answer surface | `no_raw_storage` |
| marketplace surface | `no_raw_storage` |
| video/YouTube surface | `no_raw_storage` |
| customer first-party / owned telemetry overlay | `forbidden_no_capture` |
| unknown or missing family | `forbidden_no_capture` |

These defaults do not authorize capture.

### 4. Provider or capture instrument

```text
classification: versioned
identity owner: Observatory governance
lifecycle: candidate / admitted / blocked / retired
required provenance: admission decision, exact surface/endpoint/method, terms review
scope relationship: usable only within authorized scope classes
rights/retention: cannot widen family posture
write authority: explicit admission process
read exposure: provider/instrument attribution
hammer implications: H2, H6, H7, H8, H11, H13, H20
```

Tool or credential existence is not admission.

### 5. Query panel definition

```text
classification: versioned
identity owner: Observatory
lifecycle: draft / active / retired
required provenance: panel purpose and bounded observation intent
scope relationship: bound to allowed scope or scope class
rights/retention: panel does not authorize capture
write authority: governed panel-definition path
read exposure: definition and version metadata where allowed
hammer implications: H5, H6, H14, H20
```

A used version is immutable. Changes create a new version.

### 6. CapturePackage

```text
classification: append_only admission envelope
identity owner: Observatory
lifecycle: prepared / blocked / submitted / completed / rejected / exhausted
required provenance: scope, source family, instrument, method, operator intent, authority reference, timestamps
rights/retention: required before any capture or admission
write authority: bounded capture-preflight path
read exposure: internal proof and audit metadata
hammer implications: H1, H2, H3, H5, H6, H7, H18, H20, H21
```

A CapturePackage is not provider payload storage and not an action plan. `operator_intent` must remain observational.

### 7. Capture attempt

```text
classification: append_only
identity owner: Observatory
lifecycle: planned / started / succeeded / failed / blocked / duplicate / cancelled
required provenance: CapturePackage, attempt identity, instrument, timestamps, authority and budget state
rights/retention: cannot exist as evidence by itself
write authority: bounded capture runner when later authorized
read exposure: operational proof only
hammer implications: H6, H7, H13, H20, H21
```

Zero-result and failed attempts remain valid historical attempt records when later authorized.

### 8. Provider job ID

```text
classification: external
identity owner: provider
lifecycle: provider-defined
required provenance: provider, endpoint/surface, attempt, capture time
write authority: copied from admitted provider response only
read exposure: internal reconciliation only
hammer implications: H7, H8, H15
```

It is never an Observatory evidence identity.

### 9. Candidate observation

```text
classification: durable but non-evidence, retention-bounded
identity owner: Observatory
lifecycle: pending / valid / invalid / rejected / admitted / expired
required provenance: CapturePackage, attempt, parser/manual extraction path, source context
scope relationship: required
rights/retention: candidate persistence must remain bounded and cannot bypass source posture
write authority: bounded parse/extraction path
read exposure: internal review only
hammer implications: H1, H2, H3, H5, H6, H13, H15, H18, H20, H21
```

A candidate is not evidence and cannot be cited. Rejected candidates must not become a hidden evidence or strategy cache.

### 10. Admitted observation

```text
classification: append_only
identity owner: Observatory
lifecycle: active / superseded / withdrawn / expired_by_retention / blocked_by_rights / invalidated
required provenance: source, capture, scope, rights, retention, parser/manual method, timestamps
write authority: governed admission transaction only
read exposure: through typed evidence reads
hammer implications: H1, H2, H3, H5, H8, H9, H12, H13, H15, H19, H20, H21
```

Corrections create supersession or status history. They do not rewrite what was observed.

### 11. Evidence identity

```text
classification: durable logical identity
identity owner: Observatory
lifecycle: active / superseded / withdrawn / expired_by_retention / blocked_by_rights / invalidated
required provenance: resolves to one or more admitted observations
rights/retention: current exposure fails closed when either blocks use
write authority: minted only after admission
read exposure: stable internal evidence handle
hammer implications: H1, H3, H4, H5, H12, H15, H16, H19, H21
```

Evidence identity must survive physical schema evolution.

### 12. Internal citation handle

```text
classification: durable mapping
identity owner: Observatory
lifecycle: active / deprecated / unresolved
required provenance: resolves to evidence_id
read exposure: internal bounded tools only
hammer implications: H15, H17
```

It must not expose database row identity, raw paths, provider job IDs, or customer identity.

### 13. Report-safe reference

```text
classification: external
identity owner: consumer artifact
lifecycle: consumer-owned
required provenance: consumer-owned evidence map resolving to evidence_id
write authority: consumer system only
Observatory persistence: forbidden as customer/report workflow state
hammer implications: H4, H15, H16
```

Observatory may resolve an approved reference through typed boundaries but must not own the report artifact or delivery state.

### 14. Raw manifest

```text
classification: durable or append_only metadata, source-family gated
identity owner: Observatory
lifecycle: prepared / verified / purged / unavailable / blocked / expired
required provenance: source family, CapturePackage, attempt, media type, bytes, hash, shape/parser context
rights/retention: mandatory and fail closed
write authority: bounded raw-support path when later authorized
read exposure: status and safe metadata only
hammer implications: H2, H3, H12, H13, H15, H18, H19, H21, H22
```

Required logical content when applicable:

```text
raw_manifest_id
source_family
media_type
byte_count
sha256
raw_support_status
rights_class
retention_class
retention_or_purge_deadline
shape_fingerprint
parser_status
opaque_artifact_pointer
purge_status
```

### 15. Opaque artifact pointer

```text
classification: durable internal locator
identity owner: Observatory artifact boundary
lifecycle: active / missing / purged / invalid
required provenance: raw manifest and pointer verification
read exposure: never exposed as arbitrary path, bucket key, or storage locator
hammer implications: H12, H15, H17, H18, H22
```

Raw bytes live outside ordinary relational evidence records when a future source family is separately authorized. Cloud/object storage is not authorized by this freeze.

### 16. Raw payload bytes

```text
classification: external artifact, source-family gated
identity owner: governed artifact store when later authorized
lifecycle: retained / purge_due / purged / unavailable
Observatory relational persistence: forbidden
hammer implications: H2, H3, H12, H18, H22
```

Payload bytes must never be embedded as a generic relational evidence column merely because PostgreSQL can hold them.

### 17. Shape fingerprint

```text
classification: append_only metadata
identity owner: Observatory
lifecycle: observed / recognized / unknown / breaking / retired
required provenance: source family, endpoint/surface, capture attempt, canonicalization version
write authority: bounded ingestion/parser path
read exposure: internal drift and support status
hammer implications: H12, H13, H21, H22
```

### 18. Parser version

```text
classification: versioned external implementation reference
identity owner: Observatory implementation repository
lifecycle: active / retired / blocked
required provenance: exact implementation version or commit
write authority: implementation release process
read exposure: parser lineage metadata
hammer implications: H13, H21, H22
```

Parser source code does not become database content.

### 19. Provider drift event

```text
classification: append_only
identity owner: Observatory
lifecycle: detected / reviewed / resolved / accepted-change / blocked
required provenance: prior and new fingerprints, source family, capture attempt, parser status
write authority: drift-detection path
read exposure: warning and audit context
hammer implications: H13, H21, H22
```

A drift event records observed shape change. It does not store an interpretation of provider quality.

### 20. Rights vocabulary and assignment

```text
classification: versioned vocabulary plus append_only assignment history
identity owner: Observatory governance
required provenance: source terms, decision, or review basis
write authority: governed rights-review path
read exposure: current class and basis summary
hammer implications: H2, H11, H12, H21
```

Unknown, missing, ambiguous, or stale rights fail closed.

### 21. Retention vocabulary and assignment

```text
classification: versioned vocabulary plus append_only assignment history
identity owner: Observatory governance
required provenance: source-family ruling and decision basis
write authority: governed retention-review path
read exposure: current class, deadline, and support status
hammer implications: H3, H12, H19, H21, H22
```

The accepted source-family raw postures do not replace the broader retention contract; they constrain raw support.

### 22. Freshness and volatility

```text
classification: derived by default
identity owner: Observatory read contract
source inputs: captured_at, provider_reported_time, accepted vocabulary and update-window input
persistence: vocabulary/version metadata may be durable; computed current status is derived unless separately justified
read exposure: warnings and claim-use posture
hammer implications: H9, H10, H15
```

Stale evidence remains historical evidence. Freshness status must not become a stored recommendation.

### 23. Provider disagreement

```text
classification: derived
identity owner: connected LLM/read layer
persistence: forbidden without later V6 materialization proof and explicit owner ruling
source inputs: provider-attributed observations and comparison context
read exposure: side-by-side evidence and caveats
hammer implications: H8, H9, H15
```

No winner, average, composite truth, or persistent disagreement ledger.

### 24. Claim-use and evidence-pack warnings

```text
classification: derived
identity owner: typed read layer
persistence: forbidden as canonical conclusion
source inputs: evidence status, freshness, volatility, rights, retention, raw support, coverage
hammer implications: H5, H9, H10, H16, H17
```

### 25. Audit event

```text
classification: append_only, audit_first
identity owner: Observatory
lifecycle: immutable
required provenance: action, actor class, authority, entity identity, timestamp, reason, transaction correlation
write authority: same governed transaction as consequential change
read exposure: internal audit/reconciliation only
hammer implications: H19, H20, H21, H22
```

Consequential operations include admission, rejection with retained metadata, supersession, withdrawal, rights/retention status change, raw purge, and governed deletion where ever allowed.

### 26. Security/access log

```text
classification: append_only operational record, separate from evidence corpus
identity owner: Observatory operations
lifecycle: retention-governed
required provenance: caller class, request/tool, result class, timestamp, scope authorization result
write authority: API/MCP security boundary
read exposure: security review only
hammer implications: H1, H17, H18, H21
```

Ordinary reads create no evidence events. Security logs must not become customer activity tracking or LLM reasoning storage.

### 27. Customer or owned first-party overlay

```text
classification: ephemeral
identity owner: supplying consumer
lifecycle: request-bound only
required provenance: external overlay reference and declared source type
Observatory persistence: forbidden
Observatory evidence ID: forbidden
write authority: none
read exposure: only inside the authorized read request
hammer implications: H3, H4, H16, H17, H18
```

### 28. Strategy, recommendation, conclusion, and report state

```text
classification: forbidden
identity owner: owning consumer outside Observatory
Observatory persistence: forbidden in canonical, scratch, temporary, cache, notes, JSON, raw metadata, hidden schema, or side store
hammer implications: H4, H5, H16, H17, H18
```

## Forbidden-persistence register

The accepted freeze must explicitly forbid durable or hidden Observatory persistence of:

```text
customer identity, contact, order, engagement, consent-system-of-record, report, or delivery state
customer private files or first-party analytics
customer and owned telemetry overlay payloads
strategy
recommendations
action plans
accepted conclusions
opportunity scores as truth
provider winners, averages, or composite truth scores
persistent disagreement ledger or comparison conclusion
claim-use conclusions or generated report paragraphs
LLM reasoning, chain-of-thought, scratch notes, or session memory
Neon Ronin workspace operational state
Kaizen governance state
SearchClarity business workflow state
agent task decisions or autonomous action state
arbitrary raw filesystem paths, bucket keys, or storage locators
raw bytes in ordinary relational evidence records
credentials, secret values, or connection strings
cross-scope aggregate materializations without later explicit ruling
```

Renaming any forbidden item does not admit it.

## Relationship rules

The freeze must preserve these logical relationships:

```text
scope 1 -> many CapturePackages
source family 1 -> many instruments
query panel 1 -> many immutable versions
CapturePackage 1 -> many capture attempts
capture attempt 0..1 -> provider job context
capture attempt 0..many -> candidate observations
candidate observation 0..1 -> admitted observation
admitted observation many <-> many evidence identities only when bounded bundles are justified
evidence identity -> status-aware observation resolution
capture attempt 0..many -> raw manifests
raw manifest 0..1 -> opaque artifact pointer
raw manifest -> shape fingerprint and parser version
shape change -> drift event
consequential transition -> audit event in same transaction
consumer report-safe reference -> external evidence map -> evidence identity
read request 0..many -> ephemeral overlays, never persisted
```

Physical cardinality choices remain DB-3 work, but DB-3 must not violate these semantic separations.

## Lifecycle invariants

1. Candidate is not evidence.
2. Evidence identity is minted only after admission.
3. Admitted observations are append-only.
4. Corrections use supersession or status transitions.
5. Rights and retention may block current use without erasing historical audit context.
6. Purging raw bytes updates manifest/support status and creates audit evidence.
7. A missing or invalid raw pointer cannot remain `raw_retained`.
8. Unknown source family fails closed.
9. Query panel versions used by a run are immutable.
10. Ordinary reads create no evidence mutation or evidence audit event.
11. Consumer conclusions promote outward and never become Observatory state.

## Write-authority classes

DB-3 must derive role and operation boundaries from these logical classes:

```text
governance vocabulary administration
scope administration
capture preflight
capture attempt recording
candidate extraction
observation admission
rights/retention review
raw-manifest and purge handling
evidence identity minting/status management
audit-only append
security logging
read-only typed evidence access
```

No single future application role should automatically own every class merely for convenience.

## Read-exposure classes

Logical read exposure must be classified as:

```text
publicly shapeable evidence field
consumer-authorized evidence field
internal provenance field
internal raw-support metadata
internal operational/audit field
secret/credential field — never exposed
forbidden field — must not exist
```

DB-3 must map every physical field to one exposure class.

## Hammer mapping required at DB-2 exit

The freeze must map concepts to at least:

```text
H1 scope isolation
H2 rights fail-closed
H3 retention enforcement
H4 customer-private rejection
H5 no strategy/recommendation storage
H6 CapturePackage validation
H7 provider spend/duplicate attempts
H8 provider attribution/disagreement
H9 freshness/claim use
H10 AI/GEO overclaim
H11 marketplace ceiling
H12 raw integrity
H13 shape drift/parser safety
H14 panel immutability
H15 evidence identity
H16 consumer/overlay boundary
H17 LLM/agent access
H18 hostile input
H19 append-only behavior
H20 concurrency
H21 audit-first behavior
H22 migration/restore integrity
```

Mapping is not execution proof.

## DB-2 acceptance checklist

DB-2 may be accepted only when the owner confirms that this freeze or its successor:

- classifies every listed concept;
- identifies the owner of each identity layer;
- defines lifecycle/status vocabulary or explicitly defers it fail-closed;
- binds required provenance;
- binds scope, rights, and retention behavior;
- defines write-authority and read-exposure classes;
- separates raw manifests, opaque pointers, and raw bytes;
- preserves evidence-ID stability;
- keeps disagreement, freshness warnings, and claim-use results derived;
- keeps overlays ephemeral;
- includes the forbidden-persistence register;
- maps every concept to applicable hammers;
- contains no table, column, index, trigger, function, SQL, or migration design;
- records that DB-3 requires a separate owner authorization.

## Open items carried forward fail-closed

The following remain outside this freeze unless separately ruled:

```text
new scope classes
cross-scope aggregate persistence
manual public capture admission beyond accepted source-family posture
marketplace capture admission
additional providers or endpoints
internal first-party telemetry persistence
persistent AI visibility summaries
mechanically derived sentiment persistence
production/public report-reference resolution
cloud/object-store selection
recurring capture
production deployment
```

## Exact DB-2 owner gate candidate

```text
ACCEPT DB-2 PHYSICAL DATA-CONTRACT FREEZE v0.1
AUTHORIZE DB-3 OPERATIONAL-BOUNDARY AND PHYSICAL-SCHEMA SPECIFICATION ONLY

DO NOT AUTHORIZE DATABASE CREATION, ROLES, CREDENTIALS, DDL,
MIGRATION FILES, MIGRATION EXECUTION, DISPOSABLE DATABASES,
POSTGRES HAMMERS, SYNTHETIC OR REAL PERSISTENCE, PROVIDER CALLS,
CUSTOMER DATA, RAW CAPTURE, OR PRODUCTION.
```

This phrase is a proposal only until the owner explicitly accepts it through a decision record.

## Final rule

```text
Freeze what the telescope is allowed to remember.
Keep everything it is allowed to infer outside the database.
Physical schema comes later and must obey this contract rather than inventing a new one.
```
