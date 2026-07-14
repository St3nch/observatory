# DB-3 Fresh PostgreSQL Design Specification

Status: planning candidate; not authority
Version: 0.1
Date: 2026-07-14
Milestone: DB-3 — Postgres Operational Boundary and Physical Schema Specification
Implementation authority: none

## Purpose

Specify how a future local PostgreSQL database would physically preserve the exact
accepted DB-2 logical contract while keeping The Observatory an evidence system,
not an interpretation system.

This document combines:

- local PostgreSQL operational boundary;
- database-class and role model;
- physical namespace and relation responsibilities;
- identity, constraint, index, append-only, audit-first, and scope mechanisms;
- raw-manifest and opaque-pointer boundary;
- non-executable migration and rollback planning;
- H1-H22 enforcement mapping.

It does not create PostgreSQL, databases, roles, credentials, schemas, tables,
functions, triggers, policies, indexes, extensions, SQL, migrations, backups,
artifacts, or execution authority.

## Accepted foundation

Normative logical input:

- planning-inbox/db2-physical-data-contract-freeze-specification.md
- version 0.2.1
- SHA-256 7c24d38ea8e7634dea8cf52cd7b85b49eda18b8ecde5a00c74b6303809c17891

Decision authority:

- decisions/2026-07-14-db2-freeze-acceptance-and-db3-planning-authorization.md
- decisions/2026-07-12-db1-contract-corrections-and-database-boundary-rulings.md
- hammers/hammer-matrix-v0-2.md
- hammers/acceptance-gate-policy-v0-2.md
- hammers/per-hammer-result-register-v0-1.md
- 02-boundaries.md
- POST_V1_DATABASE_ROADMAP.md

Traceability companion:

- planning-inbox/db3-accepted-input-traceability-matrix.md

The permanently retired DB-3/DB-4 artifacts are not inputs.

## Design laws

1. Facts are immutable.
2. Change is represented by append-only transitions.
3. Current state is derived.
4. Every scope-bound fact has an enforceable scope relationship.
5. Rights and retention fail closed before capture, admission, use, and exposure.
6. Consequential writes require an audit fact in the same transaction.
7. Identity layers remain distinct.
8. Provider testimony remains attributed testimony.
9. Raw content never lives in ordinary relational evidence structures.
10. Typed reads expose shaped evidence, never SQL, credentials, or storage locators.
11. Ephemeral overlays and claim inputs never persist.
12. Forbidden meaning has no table, column, cache, JSON escape hatch, or log payload.
13. Tool existence, credentials, service state, and successful tests never create authority.

## Operational boundary

### Instance ownership and version posture

Proposed future development posture:

| Item | DB-3 specification |
|---|---|
| PostgreSQL major family | PostgreSQL 18 |
| Exact minor/build | Must be inspected and recorded before DB-4 execution; no silent change during one proof campaign |
| Instance class | Owner-controlled local development instance only |
| Service lifecycle | Owner-controlled; DB-3 does not start, stop, or reconfigure it |
| Bind posture | Localhost-only unless a later explicit decision changes it |
| Encoding | UTF-8 |
| Database time posture | UTC for database/session defaults; all stored instants use timezone-aware semantics |
| Production classification | Absent and unauthorized |
| Extension posture | None assumed; every extension requires explicit specification and proof |
| Upgrade posture | Major upgrade requires a later migration/recovery decision and H22 proof |

PostgreSQL 18 is a planning target, not an installation or startup instruction. DB-4
must inspect the actual server and block on an unexpected major version.

### Database classes and protected names

| Class | Purpose | Mutation posture |
|---|---|---|
| protected_system | postgres, template0, template1 and any owner-added protected name | Never create/drop/reset through Observatory tools |
| disposable_postgres | DB-4 hammer and migration proof only | May be created/reset/dropped only after DB-4 authority and marker proof |
| governed_local | Future durable local Observatory database | Must not exist before DB-5 owner authorization |
| production | Future placeholder | Unsupported and forbidden |

Proposed governed name: observatory.

Proposed disposable prefix: observatory_test_ followed by a bounded generated suffix.

A disposable database must carry both:

- an allowed-prefix name; and
- an internal disposable marker bound to the expected database identity.

Name alone is insufficient proof. Every reset/drop operation must refuse:

- the governed name;
- protected system names;
- a missing or mismatched marker;
- an unexpected server identity;
- a caller-selected arbitrary database class.

No generic create/drop database capability is part of the accepted future design.

### Role model

Functional roles are future non-superuser, non-owner roles. No role is created here.

| Proposed role | Future responsibility | Explicitly denied |
|---|---|---|
| observatory_migrator | Apply an exact accepted migration set under a separately authorized gate | Provider calls, ordinary ingestion, typed consumer reads, superuser, arbitrary database creation |
| observatory_ingest | Execute bounded admission/capture transaction interfaces after later gates | Direct table CRUD, schema change, role management, raw locator reads, cross-scope bypass |
| observatory_reader | Execute typed read interfaces and select from explicitly safe shaped views | Base-table writes, raw pointer access, audit/security reads, SQL exposed to LLMs |
| observatory_auditor | Read bounded audit and proof metadata for authorized review | Evidence mutation, secret access, customer/private content, security-administration mutation |
| observatory_security_reader | Read bounded security/access events under separate authorization | Evidence reads, credentials, raw payloads, customer activity profiles |
| observatory_backup | Execute later allowlisted backup/restore interfaces only | Ordinary query, ingestion, schema change, cloud upload |
| operator_login | Owner-controlled authenticated login mapped to approved functional role for one task | Standing superuser use by application, stored repository password, automatic privilege escalation |

Role principles:

- schema objects are owned by a migration owner, never by ingest/read roles;
- functional roles receive least privilege;
- application/typed-read paths never use superuser;
- NOLOGIN group roles are preferred for functional privilege bundles;
- login identity and functional privilege are separate;
- role membership changes are consequential and audit/proof-relevant;
- no PUBLIC create privilege exists on application schemas;
- search path is fixed and cannot resolve attacker-created objects;
- reader and ingest roles cannot disable triggers, row security, or constraints;
- no LLM, agent, consumer, or MCP caller receives a database credential.

### Credential custody

Future credentials must:

- live outside Git and Observatory evidence;
- never appear in tool arguments, logs, result objects, diffs, proof files, or errors;
- be read at call time from an owner-controlled environment/secret boundary;
- use separate credentials per login/database class where practical;
- fail closed when missing;
- never be inferred from a successful prior call;
- never be copied into a connection string returned to a caller;
- be rotated through owner-controlled operations;
- receive a redaction review in every real-substrate proof.

DB-3 does not choose, create, store, request, or test a password.

### Local, disposable, and governed separation

A database identity tuple must include non-secret evidence for:

- server identity;
- host class;
- port;
- database name;
- database class;
- immutable or stable database identity marker;
- schema version;
- capability class.

A tool or proof runner must block if any component disagrees with the expected target.
Disposable and governed classes may not share a name, marker, migration-history
identity, backup path, or capability authorization.

## Physical namespace plan

Proposed application namespaces:

| Namespace | Responsibility | Ordinary typed-read exposure |
|---|---|---|
| obs_meta | Schema/migration identity and bounded database metadata | None |
| obs_governance | Scope, vocabularies, policies, assignments, and governed identities | Safe labels/status through typed interfaces only |
| obs_capture | Panels, packages, attempts, validation, provider testimony, and drift facts | Bounded capture context only |
| obs_evidence | Candidates, admitted observations, evidence identities, and citation mappings | Authorized shaped evidence only |
| obs_raw | Raw manifests, payload identity, opaque tokens, fingerprints, and support transitions | Safe support/hash status only |
| obs_audit | Consequential audit facts | Auditor-only |
| obs_security | Authentication/authorization/abuse events | Security-reader-only |
| obs_read | Security-barrier views and bounded typed-read functions | Reader execution/select only |

Namespace names are candidate physical names. Acceptance of this specification would
freeze their intended responsibility, not create them.

## Common physical conventions

### Identifiers

- Every canonical row uses an internal UUID primary key generated by a trusted
  application or accepted database mechanism.
- Stable domain identifiers remain separate: scope_id, capture_package_id,
  capture_id, provider_id, observation_id, evidence_id, raw_payload_id,
  raw_manifest_id, citation_handle, and every transition ID never alias each other.
- Citation handles and any externally carried opaque reference require at least
  128 bits of unpredictable entropy.
- Human-readable names are not primary keys.
- Provider-owned identifiers are stored only with provider identity and bounded
  context.
- capture_attempt_id has no active namespace, alias, column, or compatibility view.

### Time

- Stored instants use timezone-aware UTC semantics.
- captured_at and transition occurrence times are immutable facts.
- provider-reported time is distinct, optional, attributed, and never replaces
  captured_at.
- Database receive time, event occurrence time, and provider time remain separate.
- Current age, freshness, deadlines-due, and lifecycle state are derived at use time.
- Backdating an immutable fact is rejected; a correction creates a superseding fact
  or transition.

### Text and bounded values

- Identifiers follow strict bounded grammar and length.
- Controlled labels come from versioned vocabulary entries, not free text or
  database enum types that erase policy history.
- Free text is allowed only for narrowly defined bounded evidence fields.
- Rejection/audit/security text never echoes forbidden content, secrets, private
  payloads, prompts, or LLM reasoning.
- Canonical evidence does not use unvalidated JSON as a substitute for governed
  columns. Any future JSON field requires an accepted schema/version, size ceiling,
  key allowlist, and hostile-path proof.
- Binary raw payload content is prohibited from ordinary relational tables.

### Provenance

Every admitted or support-bearing fact must reach, directly or through enforced
relationships:

- scope;
- source family and instrument;
- CapturePackage and capture event where applicable;
- capture method;
- captured_at;
- provider identity when provider testimony;
- rights assignment;
- retention assignment;
- validation/admission decision;
- audit event for consequential mutation.

Missing required provenance blocks admission and current use.

## Physical relation catalog

The catalog describes future relation responsibilities. It is not executable DDL.

### obs_meta

| Relation | Class | Responsibility | Key constraints |
|---|---|---|---|
| schema_migration | append_only | Exact migration version, path, SHA-256, direction, transaction result, and authority reference | Unique version/path/hash; no update/delete |
| database_identity | durable | Non-secret database class/marker/server binding | One active identity per database; protected from application roles |
| capability_history | append_only | Accepted capability-class transitions for proof context | No implicit current permission; effective class derived |

### obs_governance

| Relation | Class | Responsibility | Key constraints |
|---|---|---|---|
| scope | durable | Scope identity, class-version binding, creation basis | No customer identity fields; unique scope_id |
| scope_transition | append_only | Activate, block, unblock, retire | N:1 scope; ordered immutable transition |
| governed_vocabulary | durable | Identity of one governed vocabulary family | Unique vocabulary kind/name |
| governed_vocabulary_version | versioned | Immutable vocabulary version and governing authority | Unique version per vocabulary; used version immutable |
| governed_vocabulary_entry | versioned | Entry code and bounded meaning inside one version | Unique code within version |
| vocabulary_transition | append_only | Submit, activate, supersede, block, retire version | N:1 version; current effective version derived |
| source_family | versioned | Source-family identity/version and raw-posture entry | Unknown family never permitted |
| source_family_transition | append_only | Propose, admit, block, retire, supersede | N:1 source family version |
| capture_instrument | versioned | Admitted method/provider/API/manual instrument identity/version | Existence is not admission |
| capture_instrument_transition | append_only | Propose, admit, block, retire, supersede | N:1 instrument version |
| governed_target | durable | Internal physical enforcement anchor for policy assignments | Never exposed as evidence identity; exactly one accepted domain binding |
| governed_target_binding | append_only | Binds internal target anchor to one exact typed domain identity | Unique typed target; no polymorphic free-form locator |
| source_family_assignment | append_only | Binds target to exact source-family version and basis | One effective compatible assignment derived |
| rights_assignment | durable | Immutable rights entry, target, basis, and assignment time | Missing/unknown entry blocks |
| rights_assignment_transition | append_only | Assign, revise, revoke, expire, block | N:1 assignment |
| retention_assignment | durable | Immutable posture, target, basis, deadline where required | Missing posture/deadline blocks |
| retention_assignment_transition | append_only | Assign, revise, expire, purge-due, purge-complete | N:1 assignment |
| freshness_assignment | durable | Target to exact freshness-policy version | One effective assignment derived |
| freshness_assignment_transition | append_only | Activate, supersede, revoke, expire | N:1 assignment |
| volatility_assignment | durable | Target to exact volatility-policy version | One effective assignment derived |
| volatility_assignment_transition | append_only | Activate, supersede, revoke, expire | N:1 assignment |

The governed_target anchor is an internal integrity mechanism only. It does not merge
domain identities. A typed binding must reference exactly one accepted domain row,
and H15 must prove that target anchors cannot substitute for observation, evidence,
capture, provider, raw, or citation identities.

### obs_capture

| Relation | Class | Responsibility | Key constraints |
|---|---|---|---|
| query_panel | durable | Stable named measurement program | Scope-bound; no strategy/priority field |
| query_panel_version | versioned | Immutable panel definition version | Used version cannot change |
| query_panel_item | versioned | Exact item/dimensions within one panel version | Unique item identity/version binding |
| query_panel_transition | append_only | Submit, activate, block, supersede, retire | N:1 panel/version |
| panel_run | append_only | One run attempt against one exact panel version | Immutable version binding |
| panel_run_transition | append_only | Plan, approve, start, complete, fail, stop, block | N:1 run |
| capture_package | durable | Immutable envelope: scope, run, source, method, authority, ceilings, stop conditions, rights, retention, intent | Complete before attempt; no payload bytes or strategy |
| capture_package_transition | append_only | Prepare, validate, block, submit, exhaust, complete, reject, cancel | N:1 package |
| capture_event | append_only | One event/attempt identified by capture_id under one package | Package 1:N captures; duplicate/idempotency key unique within accepted boundary |
| capture_transition | append_only | Plan, start, succeed, fail, block, duplicate, cancel | N:1 capture |
| validation_failure_vocabulary_version | versioned | Closed validation reason definitions | Immutable version |
| validation_result | append_only | Target, validator class, bounded result/reason, time | Never stores rejected payload |
| provider | versioned | Provider identity/version separate from instrument | Unique provider_id |
| provider_transition | append_only | Propose, admit, block, retire, supersede | N:1 provider |
| provider_testimony | append_only | Provider-attributed metric/fact and bounded context | Provider/capture/time inseparable; never truth |
| provider_testimony_transition | append_only | Support, supersede, withdraw, rights-block, retention-expire, invalidate | N:1 testimony |
| shape_fingerprint | append_only | Observed canonical response shape fingerprint | Immutable hash/algorithm/context |
| shape_recognition_transition | append_only | Recognize, review, breaking, accept-change, retire | N:1 fingerprint |
| parser_reference | durable external reference | Exact implementation release/commit reference | No code/blob/credential |
| parser_support_transition | append_only | Support, block, retire, supersede | N:1 parser reference |
| drift_event | append_only | Fact that bounded shapes differ | References prior/new fingerprints |
| drift_review_transition | append_only | Review, accept, block, resolve | N:1 drift event |

Provider cross-check, disagreement type, comparison disposition, coverage, and
blind-spot results are absent from this catalog because they remain derived.

### obs_evidence

| Relation | Class | Responsibility | Key constraints |
|---|---|---|---|
| observed_artifact_reference | durable | Bounded public/controlled artifact reference | No private/dashboard/storage locator |
| observed_artifact_transition | append_only | Supersede, rights-block, retention-expire, unavailable, invalidate | N:1 reference |
| candidate_observation | durable | Bounded internal pre-admission fact | Non-evidence, non-citable, retention-gated |
| candidate_transition | append_only | Create, validate, invalidate, reject, admit, expire, purge | N:1 candidate |
| admission_transition | append_only | Accept/reject/block decision and bounded reason | Same consequential transaction as required audit |
| observation | append_only | Immutable historical fact of what was observed | Scope/provenance/rights/retention required |
| observation_transition | append_only | Supersede, withdraw, rights-block, retention-expire, invalidate | N:1 observation |
| evidence_identity | durable | Stable post-admission resolver | Minted only after valid admission |
| evidence_identity_transition | append_only | Activate, supersede, withdraw, rights-block, retention-expire, invalidate | N:1 evidence |
| citation_handle | durable | Non-enumerable internal mapping to evidence identity | Unique opaque handle; internal only |
| citation_handle_transition | append_only | Activate, deprecate, block | N:1 handle |

No relation stores:

- claim input or prose;
- claim support/current fitness;
- provider disagreement;
- report-safe consumer references;
- customer/report workflow state;
- strategy or recommendations;
- overlay data;
- LLM reasoning.

### obs_raw

| Relation | Class | Responsibility | Key constraints |
|---|---|---|---|
| raw_manifest | durable | Hash, byte count, media type, rights/retention, parser/support metadata | No content bytes or locator |
| raw_manifest_transition | append_only | Verify, support, parser-block, purge-due, purge, unavailable, rights-block, expire | N:1 manifest |
| raw_payload_identity | durable | Raw support identity distinct from manifest, evidence, and observation | Unique raw_payload_id |
| raw_payload_transition | append_only | Bind, verify, purge-due, purge, lose-support, invalidate | N:1 payload identity |
| opaque_artifact_token | durable | Internal non-locator token for a future governed artifact boundary | Never exposed; cannot contain path/URI/key |
| opaque_token_transition | append_only | Activate, missing, purge, invalidate | N:1 token |
| raw_integrity_observation | append_only | Bounded hash-verification fact | Algorithm/hash/time/actor class; no bytes |

Governed retained artifact content is outside ordinary relational storage and remains
unauthorized. This namespace does not create an artifact store.

### obs_audit

| Relation | Class | Responsibility | Key constraints |
|---|---|---|---|
| audit_event | append_only | Consequential action, actor/caller class, authority, target, result, time, bounded metadata | Same transaction; no private payload, secret, strategy, or LLM reasoning |
| audit_supersession | append_only | Corrects an audit fact without overwriting it | References prior event and correction authority |

Ordinary successful reads create no evidence audit event.

### obs_security

| Relation | Class | Responsibility | Key constraints |
|---|---|---|---|
| security_access_event | append_only | Authentication, authorization, enumeration, rate, ceiling, and abuse event | Operationally separate and retention-gated |
| security_event_transition | append_only | Bounded retention/purge or review transition | No mutable resolved flag |

Security events cannot become customer activity profiles and cannot contain
credentials, overlay values, raw payloads, prompts, or reasoning.

### obs_read

Future security-barrier views and bounded functions may expose:

- evidence lookup;
- observation package read;
- safe provider attribution;
- current rights/retention/freshness disposition;
- attached warnings and caveats;
- safe raw-support status;
- bounded coverage/blind-spot result.

They must not expose:

- arbitrary base-table selection;
- SQL text or query plans;
- credentials;
- internal opaque artifact tokens;
- underlying paths/keys/URIs;
- private/customer data;
- blocked or expired evidence as active;
- detached provider metrics;
- report workflow, recommendations, or conclusions.

## Relationship and cardinality rules

1. Scope 1:N scope-bound panels, packages, observations, evidence, and policy targets.
2. Query panel 1:N immutable versions; version 1:N items and runs.
3. Panel run 0:1 CapturePackage when panel-based capture applies.
4. CapturePackage 1:N capture events.
5. Capture event 0:N candidates, provider testimony, validation results, and raw manifests.
6. Candidate 0:1 admitted observation.
7. Admission transition references exactly one candidate and, on admission, exactly
   one admitted observation.
8. Observation 1:N evidence identities only where a bounded evidence bundle contract
   explicitly permits; the normal case is 1:1.
9. Evidence identity 1:N internal citation handles over time.
10. Provider 1:N testimony; testimony is bound to one capture and one provider version.
11. Raw manifest 0:1 raw payload identity and 0:1 opaque token under the accepted
    source-family posture.
12. Every governed assignment references one exact target anchor and one exact policy
    or vocabulary version.
13. Every transition references exactly one base fact/version and has a stable
    transition identity.
14. Every consequential transition has exactly one required audit event in the same
    transaction, with additional audit facts permitted only by a bounded contract.
15. No foreign key crosses into Kaizen, Neon Ronin, SearchClarity, provider databases,
    customer systems, artifact stores, or implementation repositories.

## Constraint strategy

### Database constraints

Future physical enforcement must include:

- primary keys on every canonical identity;
- unique constraints on stable domain identifiers;
- foreign keys for every in-database relationship;
- not-null constraints for mandatory provenance;
- closed checks for structural status/event vocabularies where versioned governance
  is not required;
- versioned vocabulary foreign keys for governed meanings;
- uniqueness preventing duplicate active bindings where accepted;
- byte counts non-negative and hashes bound to declared algorithms;
- deadlines required only for applicable retention postures;
- provider identity required for provider testimony;
- panel run bound to exactly one panel version;
- capture event bound to exactly one package;
- admitted observation bound to a successful admission decision;
- evidence identity unavailable before admission;
- raw token structurally incapable of carrying an underlying locator;
- bounded lengths on every identifier and free-text field.

### Append-only enforcement

Defense in depth:

1. application roles receive no UPDATE or DELETE privilege on immutable and
   append-only relations;
2. bounded write interfaces expose insert/transition operations only;
3. database triggers reject UPDATE and DELETE on protected relations;
4. correction and lifecycle changes insert a new transition;
5. migrator bypass, if technically necessary for an accepted migration, is available
   only under an exact migration authority and must be visible in proof;
6. H19 intentionally attempts direct and indirect mutation.

No mutable current_status column is canonical for a changing concept.

### Audit-first enforcement

A consequential write must occur through one bounded transaction interface that:

1. validates authority, scope, rights, retention, identity, and expected prior state;
2. inserts immutable base/transition facts;
3. inserts the required audit event;
4. uses a deferred database check or constraint-trigger mechanism to prove the
   consequential fact and audit event coexist before commit;
5. rolls back the entire transaction if audit insertion or verification fails.

The audit mechanism cannot be satisfied by an application log written after commit.

### Scope isolation

Future enforcement uses:

- direct scope foreign keys on every scope-bound canonical fact;
- forced row-level security or an equivalently enforceable database policy;
- transaction-local scope context set only by a bounded authenticated interface;
- security-barrier read views/functions;
- composite scope-plus-identity checks on cross-relation joins;
- no cross-scope aggregate view by default;
- uniform blocked/not-found behavior at the typed-read boundary.

RLS is defense in depth, not a substitute for explicit scope joins and authorization.

### Rights and retention

Rights and retention checks occur before:

- capture attempt;
- candidate creation;
- admission;
- evidence resolution;
- raw support use;
- typed read;
- reuse or promotion.

Unknown, missing, incompatible, expired, or contradictory state blocks. Retention
purge is an authorized transition, not casual deletion. Append-only history survives
only to the extent its own accepted retention posture allows.

### Concurrency and idempotency

Future mechanisms include:

- unique duplicate-prevention keys scoped to exact package/recipe/authority context;
- transaction-level serialization or advisory locking on high-risk attempt/admission
  identities;
- expected-prior-transition checks;
- one admission outcome per candidate;
- one evidence mint per accepted binding;
- one effective policy assignment per target and dimension;
- retry-safe result classification;
- rollback on forked or conflicting outcomes.

DB-4 must demonstrate both failing and passing concurrent candidates under H20.

## Index strategy

Indexes are justified by constraints and accepted reads, not dashboard vibes.

Required index families:

- unique stable identifiers for all domain identities;
- transition lookup by target plus occurred_at plus transition identity;
- scope plus captured_at for authorized time-bounded evidence reads;
- capture package plus capture identity;
- panel version plus run/item identity;
- provider plus testimony time/metric identity;
- candidate/admission/observation/evidence lineage;
- citation handle exact lookup;
- rights/retention/freshness/volatility assignment by target and effective-time inputs;
- raw manifest by raw payload identity and exact hash;
- fingerprint by source/instrument/parser context;
- audit by target/action/time and authority reference;
- security events by caller class/result/time under retention limits;
- migration version/path/hash uniqueness.

Forbidden index uses:

- customer identity;
- private overlay values or hashes;
- strategy/recommendation text;
- LLM prompts/reasoning;
- raw storage locators;
- cross-scope aggregate shortcuts;
- provider winner/composite scores.

Every DB-4 candidate index must be justified by an accepted constraint or bounded
read shape and included in migration/rollback proof.

## Raw manifest and artifact boundary

Relational storage may retain only authorized manifest and integrity facts:

- raw_manifest_id;
- raw_payload_id;
- source family/instrument/capture binding;
- hash algorithm and digest;
- byte count;
- media type;
- shape fingerprint and parser reference where applicable;
- rights and retention assignments;
- support/purge status through transitions;
- internal opaque token where separately authorized.

It may not retain:

- raw bytes;
- filesystem paths;
- drive letters;
- URIs;
- bucket names or object keys;
- signed URLs;
- connection strings;
- credentials;
- full private/provider dashboard content.

The opaque token is not a reversible encoding of a locator. Resolution belongs to a
future governed artifact boundary and remains unauthorized.

## Typed-read physical boundary

The reader role receives no generic table access. Future typed reads must execute
bounded, versioned database interfaces that:

- require authenticated caller and exact scope grant;
- bind request type, filters, cursor, and page ceiling;
- apply scope, status, rights, retention, freshness, and raw-support checks;
- return deterministic ordering and bounded pagination;
- disclose truncation and omitted counts honestly;
- keep attribution and warnings attached;
- return uniform not-found/blocked behavior;
- never expose raw tokens, locators, credentials, or security/audit internals.

LLM-facing MCP tools remain API clients, not database clients.

## Migration version policy

DB-3 specifies policy only. No migration file is created.

Future migration identity:

- immutable monotonically ordered version;
- repository-relative exact path;
- SHA-256;
- paired rollback path and SHA-256 when rollback is claimed;
- accepted authority reference;
- code commit;
- required proof class;
- database class;
- transaction outcome;
- before/after schema fingerprint;
- result evidence path.

Rules:

1. migration files live only under a future earned registered path;
2. every execution requires exact path and expected SHA-256;
3. no caller-supplied SQL exists;
4. forward and rollback specifications are reviewed together;
5. one migration executes in one transaction when PostgreSQL permits;
6. non-transactional operations require a separate accepted exception;
7. a failed migration leaves no partial accepted schema state;
8. migration history is append-only;
9. dirty-tree governed execution is rejected;
10. DB-4 uses disposable targets only;
11. DB-5 requires a separate exact owner authorization for governed execution;
12. production remains unsupported.

### Non-executable migration sequence

Proposed future sequence:

| Order | Responsibility |
|---|---|
| 001 | Database identity, migration history, namespaces, and privilege baseline |
| 002 | Governance vocabularies, scopes, target anchors, and assignments |
| 003 | Query panels, packages, captures, validation, providers, fingerprints, and drift |
| 004 | Candidate/admission/observation/evidence/citation identity spine |
| 005 | Raw manifest/payload/token/support structures |
| 006 | Audit-first and append-only enforcement |
| 007 | Scope/RLS and role privilege enforcement |
| 008 | Typed-read safe views/functions and pagination support |
| 009 | Hammer fixtures and intentionally broken disposable candidates, stored outside governed migration history |
| 010 | Recovery/semantic-restore verification support |

Numbers are planning order, not approved filenames or executable migrations.

### Rollback plan

DB-4 candidate rollbacks must:

- target disposable databases;
- be exact-path and SHA-bound;
- refuse the governed name;
- prove reversal of the intended migration only;
- preserve or explicitly classify append-only proof history;
- fail when dependent data/objects make a claimed safe rollback impossible;
- never silently destroy governed evidence;
- record before/after schema fingerprints;
- demonstrate failure recovery through H22.

After governed evidence exists, destructive rollback is not assumed safe. Later
migrations use forward repair, expand/migrate/contract sequencing, backup/restore,
or an explicit owner-approved destructive exception.

## Backup-before-migration rule

For a future governed local database:

1. no governed migration starts without a recent accepted backup;
2. backup identity, hash, database identity, schema version, and migration history
   are recorded without secrets;
3. backup readability/integrity is verified before migration;
4. restore capability must already have been proven in the applicable gate;
5. backup destination remains owner-controlled and bounded;
6. off-machine encrypted proof is required before real evidence under DB-8;
7. no cloud upload is implied;
8. a missing/failed backup blocks migration.

DB-3 creates no backup.

## H1-H22 enforcement summary

| Hammer | Physical mechanisms |
|---|---|
| H1 | Direct scope FKs, composite scope joins, forced RLS/equivalent, safe views |
| H2 | Versioned rights assignments/history and fail-closed transaction/read checks |
| H3 | Retention assignment/deadline/history, purge transitions, log retention |
| H4 | Absent customer schema/fields, bounded validators, no private logging/hash |
| H5 | Forbidden schema register, narrow columns, no canonical JSON escape hatch |
| H6 | Complete immutable CapturePackage and downstream FK checks |
| H7 | Approval/ceilings/stop facts, unique duplicate keys, attempt transitions |
| H8 | Provider/testimony FK, attribution views, no disagreement table |
| H9 | Trusted times and policy assignments; derived warnings only |
| H10 | Sample/surface/prompt context and claim-support read rules |
| H11 | Source-family/instrument admission and rights checks |
| H12 | Manifest/hash/bytes/media/token separation and support transitions |
| H13 | Fingerprints, parser refs, drift/review transitions, quarantine/block |
| H14 | Immutable used panel versions and exact run/package binding |
| H15 | Distinct IDs, unique constraints, lineage FKs, status-aware handle resolution |
| H16 | No overlay/report workflow relations; request-only typed-read inputs |
| H17 | Least-privilege roles, safe views/functions, no SQL/credentials/locators |
| H18 | Identifier grammar, length/size ceilings, enum/version validation, safe errors |
| H19 | Privilege denial, triggers, insert-only transitions, immutable history |
| H20 | Unique keys, expected state, transaction locking, retry-safe outcomes |
| H21 | Same-transaction audit event with deferred commit verification |
| H22 | SHA-bound migrations, schema fingerprints, rollback/failure/restore continuity |

Every result remains defined_only in DB-3.

## DB-3 exit checklist

The specification is owner-ready only when:

- the traceability matrix covers every accepted DB-2 concept;
- operational version, database class, role, credential, backup, and migration
  boundaries are explicit;
- every physical relation has a narrow responsibility and classification;
- derived, ephemeral, external, forbidden, and unresolved concepts are handled
  without accidental persistence;
- identity, scope, rights, retention, append-only, audit-first, raw, and read
  boundaries map to hammers that can fail;
- the future ob-dev control-plane contract is exact;
- no retired artifact was used;
- no SQL, DDL, migration, role, database, credential, tool implementation, or
  execution occurred;
- authority sync and full unit tests pass;
- an exact hash-bound owner review is produced.

## Separate future gates

Acceptance of this specification would not:

- close DB-3 automatically;
- authorize DB-4;
- authorize ob-dev source changes;
- start PostgreSQL;
- create disposable or governed databases;
- create roles or credentials;
- create or execute migrations;
- run real PostgreSQL hammers;
- persist synthetic or real evidence;
- authorize providers, capture, raw storage, customer data, recurring work, or
  production.

## Final rule

The future database must make evidence corruption and boundary drift harder than
honest storage, while leaving interpretation nowhere to hide.
