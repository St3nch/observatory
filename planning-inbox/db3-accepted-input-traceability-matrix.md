# DB-3 Accepted-Input Traceability Matrix

Status: planning specification; not authority
Version: 0.1
Date: 2026-07-14
Milestone: DB-3 — Postgres Operational Boundary and Physical Schema Specification
Implementation authority: none

## Purpose

This matrix proves that fresh DB-3 planning derives from accepted authority rather
than from the five permanently retired DB-3/DB-4 artifacts. It maps the exact
accepted DB-2 logical contract, accepted DB-1 policy, and current DB-3 gate to the
physical and operational responsibilities that DB-3 must specify.

This file is not a schema, migration, executable DDL, database, role definition,
credential plan ready for execution, or DB-4 artifact.

## Authority boundary

Controlling authority:

1. decisions/2026-07-14-db2-freeze-acceptance-and-db3-planning-authorization.md
2. exact accepted DB-2 freeze:
   - path: planning-inbox/db2-physical-data-contract-freeze-specification.md
   - version: 0.2.1
   - SHA-256: 7c24d38ea8e7634dea8cf52cd7b85b49eda18b8ecde5a00c74b6303809c17891
3. decisions/2026-07-12-db1-contract-corrections-and-database-boundary-rulings.md
4. hammers/hammer-matrix-v0-2.md
5. hammers/acceptance-gate-policy-v0-2.md
6. hammers/per-hammer-result-register-v0-1.md
7. 02-boundaries.md
8. POST_V1_DATABASE_ROADMAP.md

Historical planning input:

- planning-inbox/db1-ob-dev-database-control-plane-requirements.md
- planning-inbox/m10-logical-schema-plan-c2.md

Historical planning input may clarify lineage but cannot override accepted authority.

## Retired-artifact exclusion

These paths are prohibited inputs and must remain absent:

- decisions/2026-07-13-db2-closure-and-db3-activation.md
- decisions/2026-07-13-db3-closure-and-db4-activation.md
- planning-inbox/db3-postgres-operational-boundary-specification.md
- planning-inbox/db3-physical-schema-specification.md
- planning-inbox/db3-specification-readiness-review.md

No language, structure, decision, or design below was recovered from those artifacts.

## Mapping method

Each accepted DB-2 concept receives:

- one physical responsibility;
- one enforcement posture;
- one lifecycle representation;
- one read/exposure boundary;
- applicable H1-H22 expectations;
- explicit treatment of anything that must remain derived, ephemeral, external,
  forbidden, or unresolved.

The physical specification may describe future structures. It may not create them.

## Classification-to-physical rule

| DB-2 class | DB-3 physical responsibility | Forbidden shortcut |
|---|---|---|
| durable | Describe canonical immutable base facts and governed identity | Mutable current-state row presented as history |
| append_only | Describe insert-only fact/transition/event responsibility | In-place correction, backdating, or destructive replacement |
| versioned | Describe immutable versions plus explicit supersession transitions | Updating a used version in place |
| derived | Describe source facts and deterministic read computation only | Persisting current meaning, score, warning, or conclusion |
| ephemeral | Exclude from durable schema and logs except bounded safe security metadata | Hashing, caching, manifesting, or logging request values |
| external | Retain only an authorized bounded non-secret reference | Foreign key into another system or copied external state |
| forbidden | No table, column, JSON field, cache, log payload, or side store | Renamed or hidden persistence |
| unresolved | Reserve no active namespace or behavior; fail closed | Provisional implementation or alias |

## Identity and lifecycle traceability

| Accepted concept group | Required future physical responsibility | Lifecycle and current-state rule | Exposure boundary | Hammers |
|---|---|---|---|---|
| Scope and scope-class vocabulary | Separate scope identity, immutable class binding, and append-only scope transitions | Effective status is derived from transitions | Safe scope label only under authorization; no customer identity | H1, H4, H15, H19-H22 |
| Source family and assignments | Immutable family versions, append-only assignment and transition facts | Effective family posture is derived | Governed/internal reads; safe family label where required | H2, H3, H7, H11-H13, H19-H22 |
| Capture instrument | Immutable admitted instrument versions and append-only status transitions | Admission/block/retirement is derived | Internal governance; attribution may be shaped safely | H2, H6-H8, H11, H13, H19-H22 |
| Query panel, version, and item | Stable panel identity with immutable used versions and version-bound items | Active version derived; used versions never change | Measurement context and blind spots only | H1, H5, H6, H9-H11, H14, H19-H22 |
| Panel run | Append-only run fact plus append-only transitions | Planned/running/completed/failed state derived | Internal operational context; safe bounded measurement context | H6, H7, H14, H19-H21 |
| CapturePackage | Immutable admission envelope plus append-only package transitions | No mutable package status | Internal governance/operations; safe capture context only | H1-H7, H14, H18-H21 |
| Capture event/attempt | Stable capture_id, append-only attempt fact and transitions | Zero-to-many observations remain explainable; status derived | Internal operations; bounded provenance only | H6, H7, H13, H19-H21 |
| Provider identity and testimony | Versioned provider identity; append-only attributed testimony | Withdrawal/block/expiry/invalidation append transitions | Attribution and caveats inseparable | H2, H3, H7-H10, H13, H15, H19-H22 |
| Candidate observation | Immutable bounded internal candidate with append-only validation/admission lifecycle | Pending/valid/rejected/admitted/expired/purged derived | Never ordinary evidence, never citable | H1-H6, H13, H15, H18-H21 |
| Admitted observation | Insert-only observation fact with append-only status transitions | Active/historical/blocked/expired status derived | Ordinary typed reads only when current rights/retention/status permit | H1-H5, H8, H9, H12, H13, H15, H19-H22 |
| Admission decision | Append-only accept/reject/block fact in the same consequential transaction as required audit | No mutable decision result | Internal governance; safe evidence status only | H5, H6, H15, H19-H21 |
| Evidence identity | Stable post-admission identity distinct from observation and raw identity | Resolution status derived from transitions | Status-aware typed resolution | H1-H5, H12, H15-H22 |
| Citation handle | Non-enumerable internal mapping plus append-only transitions | Active/deprecated/blocked derived | Internal only; uniform blocked/not-found behavior | H3, H15, H17, H19, H21, H22 |
| Report-safe reference | No Observatory-owned durable workflow structure | Consumer-owned lifecycle | External consumer artifact only | H4, H5, H15-H17 |
| Observed artifact reference | Immutable bounded public/controlled reference plus transitions | Current usability derived | Rights-safe public fields only; never storage locators | H1-H5, H12, H15, H18-H22 |
| Validation vocabulary/result/reason | Versioned codes and append-only bounded results | Validation status derived | Safe code/status only; no rejected payload | H1-H7, H12-H18, H20, H21 |
| Rights vocabulary/assignment/history | Immutable vocabulary versions, assignment facts, and append-only history | Effective rights derived at action/read time | Safe class/warning; basis/history specialized | H2, H3, H11, H12, H19, H21, H22 |
| Retention vocabulary/assignment/history | Immutable policy versions, assignment/deadline facts, append-only purge history | Effective retention and due state derived | Safe posture/status; deadlines/history specialized | H2, H3, H12, H19, H21, H22 |
| Freshness and volatility policies | Versioned policies and immutable assignments | Age, band, freshness, volatility, and fitness derived at read time | Mandatory warnings remain attached to shaped output | H3, H8-H10, H15-H17, H19, H21, H22 |
| Raw manifest and payload identity | Immutable manifest facts and distinct raw identity | Support/purge/mismatch state derived from append-only transitions | Safe status/hash only where authorized | H2, H3, H12, H13, H15, H17-H22 |
| Opaque artifact pointer | Internal non-locator token only | Missing/purged/invalid state derived | Never exposed through ordinary typed reads | H3, H12, H15, H17-H22 |
| Shape fingerprint and parser reference | Append-only observed fingerprints and external bounded parser reference | Recognition/support/drift posture derived | Specialized internal reads | H12, H13, H19, H21, H22 |
| Drift event and review history | Append-only detection and review transitions | Current posture derived | Internal operational/governance context | H12, H13, H19-H22 |
| Audit event | Append-only same-transaction consequential audit fact | No update/delete lifecycle | Operational only, excluded from ordinary evidence reads | H19-H22 |
| Security/access log | Operationally separate append-only security fact | Retention-governed; no customer profile | Security-only access | H1, H3, H17-H22 |

## Derived-only traceability

The following remain compute-on-read and receive no canonical physical table,
materialized cache, current-state column family, or durable identifier:

| Derived result | Canonical inputs | Required failure posture |
|---|---|---|
| Effective rights | Rights assignment and transition history plus time | Unknown/expired blocks capture, admission, read, and reuse |
| Effective retention | Retention assignment/history/deadline plus time | Unknown/expired blocks use and requires authorized purge posture |
| Observation age and age band | Trusted capture/provider times and governed policy version | Missing trusted time yields unknown or blocked use |
| Freshness status | Age, policy, volatility, status, rights, retention, claim intent | Warning, historical-only downgrade, or block |
| Current claim fitness/support | Exact evidence set, ephemeral claim intent, policies, and read time | Evidence-only output with inseparable warnings or block |
| Provider disagreement | Attributed testimony plus ephemeral comparison context | Side-by-side result or incomparable/blocked; no winner |
| Coverage/blind spots | Query panel/run and authorized visible evidence set | No universal absence/completeness claim |
| Consumer-promotion requirement | Meaning-bearing response conditions | Promotion flag required; no automatic workflow action |
| Current lifecycle status | Immutable base facts plus applicable transition history | Unknown or contradictory history blocks consequential use |
| Raw-support status | Manifest, payload/token, hash, rights, retention, support transitions | Block raw-supported claims; never reveal locator |

## Ephemeral and external traceability

| Concept | Physical disposition |
|---|---|
| Claim input and claim-intent selection | Request memory only; discard after response |
| Comparison context | Request memory only; no disagreement ledger |
| Customer/owned telemetry overlay | Request memory only; values, hashes, summaries, manifests, and logs prohibited |
| Overlay freshness and discard status | Input ephemeral; discard result derived |
| Consumer request | Access-layer request only; no customer/order/report record |
| Evidence pack | Response object only; no report-state persistence |
| Cursor | Signed, bound, expiring access-layer token; no canonical evidence record |
| Authorization grant | External access-layer reference; no copied credential |
| Provider job ID | Bounded provider-attributed external reference |
| Parser implementation version | Bounded repository/release reference |
| Owning consumer label/reference | Bounded external system reference; never customer identity |
| Report-safe reference | Consumer-owned artifact mapping; no public Observatory resolver |

## Forbidden-persistence traceability

DB-3 must provide no physical home for:

- strategy, recommendations, opportunity scores, tactics, or action plans;
- conclusions, report narrative/state/delivery, or accepted business decisions;
- LLM reasoning, prompts, session memory, or chain-of-thought;
- provider winner, average, consensus, composite truth, or disagreement ledger;
- customer identity, orders, private files, first-party analytics, or hidden profiles;
- overlay values, hashes, inventories, summaries, or manifests;
- raw payload bytes in ordinary relational evidence structures;
- credentials, secrets, connection strings, filesystem paths, bucket keys, or URIs;
- rejected-evidence graveyards beyond the bounded retention-gated candidate contract;
- cross-scope materializations or customer-derived aggregates;
- mutable current-state substitutes for append-only history;
- collection priorities, recapture tasks, schedules, or autonomous-spend state;
- capture_attempt_id as an active alias or namespace.

Detection of any forbidden family must block the consequential write and record only
bounded non-sensitive violation metadata where accepted audit/security rules require it.

## Raw-posture traceability

| Source family | Accepted default | DB-3 consequence |
|---|---|---|
| Controlled provider API payload | capture_and_purge_raw | Specify manifest/purge lifecycle; do not authorize capture or artifact storage |
| Public manual observation | retain_manifest_only | Manifest facts only; no payload bytes |
| Public page snapshot | no_raw_storage | No raw identity/content/pointer creation |
| AI/GEO answer surface | no_raw_storage | No raw identity/content/pointer creation |
| Marketplace surface | no_raw_storage | No raw identity/content/pointer creation |
| Video/YouTube surface | no_raw_storage | No raw identity/content/pointer creation |
| Customer first-party/owned overlay | forbidden_no_capture | No durable target, manifest, hash, or log value |
| Unknown/missing source family | forbidden_no_capture | Fail before capture/admission |

## H1-H22 physical expectation matrix

All DB-3 results remain defined_only. No hammer is executed here.

| Hammer | DB-3 must specify | Future failure must be possible when |
|---|---|---|
| H1 Scope isolation | Scope ownership on every scope-bound fact and role/read policy | Cross-scope relation or unauthorized read is attempted |
| H2 Rights fail-closed | Rights targets, assignments, history, and enforcement checkpoints | Rights are missing, unknown, expired, or incompatible |
| H3 Retention enforcement | Retention assignments, deadlines, transitions, and purge boundary | Data outlives or exceeds its accepted posture |
| H4 Customer-private rejection | No customer/private fields and bounded validation rejection | Private/customer content enters any durable or log structure |
| H5 No strategy storage | Explicit forbidden family and narrow content responsibilities | Interpretive/workflow meaning is submitted |
| H6 CapturePackage validation | Complete immutable envelope and downstream binding rules | Attempt/admission lacks a valid package |
| H7 Spend/duplicates | Attempt identity, approval/ceiling facts, and uniqueness boundary | Duplicate or unauthorized attempt is submitted |
| H8 Provider attribution | Provider/testimony identity and inseparable attribution | Metric is detached, averaged, or treated as web truth |
| H9 Freshness/claim use | Trusted times, policies, assignments, derived warnings | Current/absence/comparative support lacks fitness |
| H10 AI/GEO overclaim | Surface/prompt/sample context preserved | Universal trust, causality, or visibility is claimed |
| H11 Marketplace ceiling | Source/method/rights context and fail-closed admission | Unadmitted marketplace evidence is captured or used |
| H12 Raw integrity | Manifest/hash/byte/media/token separation and support transitions | Hash, identity, pointer, support, or retention conflicts |
| H13 Drift/parser safety | Fingerprints, parser refs, drift/review transitions | Shape/parser is unknown, unsupported, or breaking |
| H14 Panel immutability | Used panel versions immutable and runs exactly bound | Used version changes or run binding is ambiguous |
| H15 Evidence/citation integrity | Distinct identities and status-aware resolution | Identity layers are conflated or blocked evidence resolves active |
| H16 Consumer/overlay boundary | No durable overlay/report workflow structures | Overlay or downstream meaning persists |
| H17 Access boundary | Future roles plus typed-read-only exposure posture | SQL/CRUD/credential/locator path is exposed |
| H18 Hostile input | Bounded identifiers, enums, sizes, formats, and safe errors | Weird/oversized/forbidden input reaches persistence |
| H19 Append-only | Insert-only historical facts and transition responsibilities | Update/delete/backdate attempts target historical facts |
| H20 Concurrency | Uniqueness, transaction, lock, and idempotency expectations | Duplicate/forked outcomes survive concurrent attempts |
| H21 Audit-first | Same-transaction audit dependency for consequential changes | State commits without its required audit fact |
| H22 Migration/recovery | Identity, history, constraints, hashes, versions, and audit continuity | Forward/rollback/restore loses or changes governed meaning |

## Open and separately gated matters

DB-3 may specify fail-closed accommodation but may not decide or activate:

- new scope classes;
- cross-scope aggregates;
- manual/marketplace/browser-extension capture admission;
- new providers or endpoint families;
- internal first-party persistence;
- persistent AI summaries or sentiment;
- public report-reference resolution;
- artifact-store technology or creation;
- recurring capture;
- production deployment;
- capture_attempt_id aliasing.

## Completeness gate

This matrix is complete only if the combined DB-3 design:

- covers every row above;
- contains no executable SQL or migration file;
- defines every physical mechanism as future work;
- maps all required mechanisms to failing H1-H22 expectations;
- keeps database roles and credentials descriptive and uncreated;
- keeps the governed mutation modes disabled;
- preserves the exact DB-2 hash and identity meanings;
- remains independent of retired DB-3/DB-4 artifacts.

## Non-authorizations

No PostgreSQL startup or creation. No database, schema, role, credential, secret,
DDL, migration file, SQL execution, database tool, persistence, provider, capture,
raw storage, customer/private data, recurring work, DB-4, production, strategy,
recommendation, conclusion, report-state, or LLM-reasoning persistence is authorized.

## Final rule

Every accepted logical concept must have one honest future physical responsibility,
and every forbidden or computed concept must have none.
