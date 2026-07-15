# DB-4 DB-3 Implementation Traceability Matrix

Status: remediation planning candidate; not implementation authority
Version: 0.1
Date: 2026-07-14
Milestone: DB-4 remediation R1
Authority: `decisions/2026-07-14-db4-audit-acceptance-and-remediation-activation.md`
Source design: `planning-inbox/db3-fresh-postgres-design-specification-v0-1.md`
Source logical freeze: `planning-inbox/db2-physical-data-contract-freeze-specification.md` v0.2.1
Source hammer policy: `hammers/hammer-matrix-v0-2.md`

## Purpose

Prevent another simplified schema from being mistaken for the accepted DB-3 design.

Every accepted DB-2/DB-3 physical responsibility must map to:

```text
source requirement
→ migration responsibility
→ physical relation or mechanism
→ constraints and indexes
→ role/RLS behavior
→ rollback behavior
→ behavioral hammer
→ intentionally broken or sabotaged candidate
→ durable result record
```

A future implementation package may refine filenames or split one responsibility into
multiple migrations, but it may not omit a row or silently weaken the responsibility.

## Global implementation laws

All rows inherit these requirements:

- internal UUID primary keys; stable domain identifiers remain distinct;
- timezone-aware UTC instants;
- bounded identifier grammar and length;
- no unvalidated JSON escape hatch;
- no raw bytes, paths, URIs, keys, credentials, private payloads, strategy, conclusions,
  recommendations, customer records, overlays, report state, prompts, or reasoning;
- append-only facts and transitions where DB-3 classifies them append-only;
- current state derived from transitions;
- consequential writes paired with audit facts in the same transaction;
- direct scope relationships plus forced RLS or equivalent enforcement;
- rights and retention fail closed;
- no application role owns schema objects;
- no PUBLIC CREATE on application schemas;
- exact migration path/SHA, atomic history, before/after fingerprints, and serialized execution;
- structural checks are preconditions, not hammer passes.

## Migration family map

| Family | Required responsibility |
|---|---|
| 001 | database identity, migration history, namespaces, privilege baseline |
| 002 | governance vocabularies, scopes, target anchors, source/instrument admission, policy assignments |
| 003 | query panels, packages, captures, validation, provider testimony, fingerprints, parser support, drift |
| 004 | observed artifacts, candidates, admission, observations, evidence identities, citation handles |
| 005 | raw manifests, payload identities, opaque tokens, integrity observations, support transitions |
| 006 | append-only enforcement, audit-first pairing, audit and security facts |
| 007 | role grants, ownership, forced RLS, scope context, WITH CHECK policies |
| 008 | security-barrier views and bounded typed-read functions |
| 009 | intentionally broken/sabotaged candidates outside accepted migration history |
| 010 | recovery and semantic-restore verification support |

The implementation package must decide whether each family remains one migration or is
split into ordered submigrations. Any split must preserve one traceability row per
responsibility and exact rollback ordering.

## 001 — Metadata, identity, namespaces, and privilege baseline

| Requirement | Physical object/mechanism | Required constraints/indexes | Hammer and sabotage | Rollback/result requirement |
|---|---|---|---|---|
| Exact append-only migration identity | `obs_meta.schema_migration` | unique version; unique path; exact SHA-256; direction; authority; code commit; database class; transaction result; before/after fingerprint; no update/delete | H22: duplicate version/different SHA fails; UPDATE/DELETE fails; migration cannot commit without history | rollback semantics explicit; history never silently rewritten; result contains exact row identity |
| Stable database identity | `obs_meta.database_identity` | one active identity per DB; database name/class/marker/server binding; application roles denied | H22/H17: mismatched marker or current_database fails | disposable teardown may destroy only after result record captures identity |
| Capability history | `obs_meta.capability_history` | append-only transitions; no row implies no authority; authority reference required | H17/H22: missing or conflicting capability blocks operation | preserved in proof until campaign closure |
| Namespace baseline | schemas `obs_meta`, `obs_governance`, `obs_capture`, `obs_evidence`, `obs_raw`, `obs_audit`, `obs_security`, `obs_read` | deterministic owner; PUBLIC CREATE revoked; search path pinned | H17: PUBLIC cannot create; attacker shadow object cannot resolve | reverse order schema teardown only on disposable DB |
| Privilege baseline | migration owner + functional NOLOGIN roles | no superuser; no schema ownership for ingest/read roles; deterministic grants | H17: role cannot alter schema/disable triggers/RLS | create/drop role lifecycle recorded separately |

## 002 — Governance, scope, targets, and policy assignments

| DB-3 relation/responsibility | Physical requirements | Required behavioral proof | Broken/sabotaged candidate |
|---|---|---|---|
| `scope` | internal UUID PK; unique bounded `scope_id`; scope-class vocabulary/version binding; no customer identity fields | H1 same-scope permitted, cross-scope denied; H4 customer/private field rejected | scope table without direct scope key/RLS; added customer identity column |
| `scope_transition` | append-only ordered transitions; one base scope | H19 UPDATE/DELETE rejected; invalid transition order blocked | mutable status column or no append-only trigger |
| governed vocabulary family/version/entry | distinct family, immutable version, unique code per version, authority binding | H2/H3/H18 unknown or inactive vocabulary entry blocks assignments | free-text rights/retention value; mutable used vocabulary version |
| vocabulary transitions | append-only submit/activate/supersede/block/retire | H19 mutation rejected; active version derived | mutable `is_active` flag |
| source family + transitions | versioned identity and admission state; unknown family denied | H11 unknown/unadmitted family blocks capture/admission | source family accepted by mere row existence |
| capture instrument + transitions | versioned method/provider/manual instrument identity; admission separate from existence | H11 unadmitted instrument blocks package/capture | instrument with no admission transition accepted |
| governed target | internal anchor only; cannot become evidence identity | H15 target ID cannot resolve as observation/evidence/citation | polymorphic target used as public evidence ID |
| governed target binding | exactly one typed domain binding; unique typed target; no locator text | H15 ambiguous/multiple binding blocked | free-form target type/id pair without FK |
| source-family assignment | append-only exact target+version+basis | H11 missing/incompatible assignment blocks | mutable current assignment row |
| rights assignment + transitions | immutable assignment and append-only lifecycle; unknown/missing/revoked blocks | H2 capture, admission, raw use, and read fail closed | no rights assignment; expired/revoked assignment still accepted |
| retention assignment + transitions | posture/version, basis, deadline when required, purge lifecycle | H3 missing deadline or expired posture blocks; purge due behavior enforced | applicable posture without deadline; mutable purge flag |
| freshness assignment + transitions | exact policy version; effective assignment derived | H9 stored current freshness prohibited; warning derived | persisted `is_fresh` truth column |
| volatility assignment + transitions | exact policy version; effective assignment derived | H9 volatility claim derived only | persisted volatility score-as-truth |

Required indexes:

- scope stable identifier;
- target typed-binding uniqueness;
- transition target + occurred_at + transition ID;
- assignment target + policy dimension + effective-time inputs;
- no customer/private/strategy indexes.

## 003 — Capture, validation, provider testimony, fingerprints, and drift

| DB-3 relation/responsibility | Physical requirements | Behavioral hammer | Broken/sabotaged candidate |
|---|---|---|---|
| query panel | scope-bound stable measurement-program identity; no strategy/priority | H14 used panel definition cannot mutate; H5 no strategy column | mutable panel definition; priority/recommendation field |
| query panel version/item/transition | immutable versions/items; exact item dimensions; lifecycle append-only | H14 used version update/delete rejected; package bound to exact version | package references panel without version |
| panel run + transition | immutable run attempt; exact panel version; append-only lifecycle | H6/H20 conflicting run state rejected | mutable current status or two terminal outcomes |
| capture package | complete immutable envelope: scope, run/source/instrument, authority, ceilings, stop conditions, rights, retention, intent; no payload bytes/strategy | H6 incomplete package rejected; H7 exhausted/unauthorized package blocks capture | nullable authority/rights/retention/ceilings; strategy JSON |
| capture package transition | prepare/validate/block/submit/exhaust/complete/reject/cancel append-only | H6 invalid state progression rejected | direct status update |
| capture event | immutable `capture_id`; package FK; unique duplicate/idempotency key in exact authority/recipe context | H7/H20 duplicate race yields one accepted outcome and retry-safe classification | no unique duplicate key; generic control-table race |
| capture transition | plan/start/succeed/fail/block/duplicate/cancel append-only | H20 one terminal outcome; conflicting transition rolls back | two successful terminal transitions |
| validation vocabulary/version | closed immutable reason definitions | H18 unknown reason blocked | free-text unbounded rejection reason |
| validation result | append-only target/validator/result/reason/time; rejected payload prohibited | H4/H18 rejected private/hostile payload not echoed | stores rejected payload or exception dump |
| provider + transition | versioned provider identity; admission separate from existence | H8/H11 unadmitted/blocked provider testimony rejected | provider row alone treated as admitted |
| provider testimony + transition | provider, capture, time, metric/fact, bounded context inseparable; attributed testimony only | H8 detached testimony query blocked; no provider-winner table | testimony without provider/capture/time; truth score |
| shape fingerprint + transition | immutable algorithm/hash/context; recognition lifecycle | H13 unknown/breaking fingerprint blocks parser/admission | fingerprint row auto-accepted |
| parser reference + support transition | exact release/commit external reference; no code/blob/credential | H13 unsupported parser blocks | mutable supported boolean |
| drift event + review transition | prior/new fingerprint facts; review lifecycle | H13 changed shape quarantined until accepted | parser continues despite breaking drift |

Required indexes:

- panel version + item/run identity;
- capture package + capture ID;
- duplicate prevention key scoped to authority/recipe/package;
- provider + testimony time/metric identity;
- fingerprint by source/instrument/parser context.

## 004 — Artifact, candidate, admission, observation, evidence, and citation identity

| DB-3 relation/responsibility | Physical requirements | Behavioral hammer | Broken/sabotaged candidate |
|---|---|---|---|
| observed artifact reference + transition | bounded public/controlled reference; no private/dashboard/storage locator; append-only lifecycle | H4/H12 locator/private field rejected; H19 mutation rejected | filesystem path/URI/private dashboard reference |
| candidate observation + transition | bounded pre-admission fact; non-evidence, non-citable, retention-gated | H15 candidate ID cannot resolve as evidence/citation; H2/H3 missing policy blocks | candidate directly assigned evidence handle |
| admission transition | exact candidate, decision, bounded reason, audit pair; one outcome | H6/H20 one admission outcome; unpaired admission rolls back | two accepts; admission without audit |
| observation + transition | immutable historical fact; scope/provenance/rights/retention mandatory; supersession through transition | H1/H2/H3/H19 direct update/delete and cross-scope access rejected | mutable observation; missing scope/policy provenance |
| evidence identity + transition | minted only after accepted admission; stable resolver; lifecycle append-only | H15 pre-admission mint blocked; duplicate mint race yields one | evidence FK directly to candidate without admission |
| citation handle + transition | non-enumerable >=128-bit opaque handle; maps only to evidence identity; internal | H15 guessable/short handle rejected; target/observation/candidate ID not accepted as handle | sequential handle; polymorphic resolver |

Required lineage:

```text
capture_event → candidate_observation → admission_transition → observation → evidence_identity → citation_handle
```

Required cardinality and uniqueness:

- candidate 0:1 admitted observation;
- one accepted admission outcome per candidate;
- normal observation:evidence identity is 1:1 unless a later bounded contract permits 1:N;
- evidence identity 1:N citation handles over time;
- all identity namespaces are non-aliasing and separately constrained.

Required indexes:

- candidate/admission/observation/evidence lineage;
- unique stable IDs;
- exact citation-handle lookup;
- scope + captured_at for bounded reads.

## 005 — Raw support boundary

| DB-3 relation/responsibility | Physical requirements | Behavioral hammer | Broken/sabotaged candidate |
|---|---|---|---|
| raw manifest + transition | hash algorithm/digest, bytes, media type, capture/source/instrument, rights/retention, parser/support metadata; no bytes/locator | H12 wrong hash/bytes/media/token relation rejected; locator columns/values rejected | path/URI/key column; unbounded raw JSON/blob |
| raw payload identity + transition | identity distinct from manifest/evidence/observation; optional 0:1 binding | H15 identity substitution rejected; H12 invalid support transition blocked | raw ID reused as evidence ID |
| opaque artifact token + transition | internal, bounded, non-locator, not reversible; never reader-exposed | H12 path/URI/drive-letter/signed URL patterns rejected; H17 reader cannot select token | token contains path/URL/key; reader grant |
| raw integrity observation | append-only algorithm/hash/time/actor class; no bytes | H12 UPDATE/DELETE rejected; mismatch recorded as fact and blocks support | mutable verified flag |

Required checks:

- byte count non-negative;
- digest length/grammar bound to algorithm;
- media type bounded;
- no locator grammar;
- no content bytes;
- rights and retention required before active support/use.

## 006 — Append-only, audit-first, audit, and security enforcement

| Responsibility | Physical mechanism | Behavioral proof | Sabotage |
|---|---|---|---|
| append-only relations | no UPDATE/DELETE grants plus shared reject-mutation trigger | H19 execute direct and indirect UPDATE/DELETE under application role and expect rejection | trigger body changed to permit; grant UPDATE added |
| audit event | immutable action/actor/authority/target/result/time/bounded metadata | H21 consequential write without matching audit fails at commit | audit table exists but no pairing mechanism |
| audit supersession | append-only correction referencing prior event and correction authority | H19 prior audit cannot be overwritten | UPDATE prior event |
| audit-first pairing | deferred constraint trigger or equivalent same-transaction verification | H21 paired transaction commits; missing audit or failed audit causes full rollback | after-commit application log only |
| security access event + transition | operationally separate; retention-gated; no credentials/private activity profile | H4/H17 secret/private payload rejected; append-only mutation rejected | credential/URI in metadata; mutable resolved flag |

Every consequential relation/transition must be classified as audit-required or
explicitly non-consequential. The implementation package must list exact pairing keys.

## 007 — Role, ownership, RLS, and scope enforcement

Required functional privilege bundles:

```text
observatory_migrator
observatory_ingest
observatory_reader
observatory_auditor
observatory_security_reader
observatory_backup
operator_login mapping
```

DB-4 disposable proof may use bounded test-prefixed equivalents, but semantics must
match the accepted profiles.

Required mechanisms:

- schema objects owned by migration owner;
- functional group roles NOLOGIN;
- no PUBLIC CREATE;
- least privilege grants;
- `ENABLE ROW LEVEL SECURITY` and `FORCE ROW LEVEL SECURITY` on every scope-bound base relation;
- explicit `USING` and `WITH CHECK` policies;
- transaction-local scope context set only through bounded interface;
- composite scope checks on cross-relation lineage;
- reader receives safe view/function access, not arbitrary base-table access;
- ingest cannot disable triggers/RLS/constraints;
- auditor/security reader separation.

Behavioral proof:

- H1 same-scope read succeeds, cross-scope read is invisible/denied, cross-scope write denied;
- H17 reader base-table write denied; raw token/audit/security access denied;
- H15 citation lookup cannot escape scope;
- table owner/superuser bypass is not accepted as proof; use `SET ROLE` to functional role;
- policy changed to `USING (true)` or FORCE removed must make sabotage test fail.

## 008 — Typed-read physical boundary

Required future interfaces:

- evidence lookup;
- observation package read;
- safe provider attribution;
- current rights/retention/freshness disposition;
- attached warnings/caveats;
- safe raw-support status;
- bounded coverage/blind-spot output.

DB-4 responsibility is physical specification and disposable enforcement proof where
mechanically applicable, not product/API completion.

Required mechanisms:

- security-barrier views;
- bounded versioned functions;
- deterministic ordering and keyset/bounded pagination support;
- uniform blocked/not-found semantics;
- no raw token/locator/credential/audit/security exposure;
- attribution and warnings inseparable from provider metrics;
- blocked/expired evidence excluded from active resolution.

Behavioral proof maps to H1, H5, H8, H9, H10, H15, H16, H17, and H18, with DB-4
executing only the database-mechanical subset and recording explicit deferred reasons
for DB-7-only behavior.

## 009 — Intentionally broken and sabotaged candidates

Broken candidates must traverse the real migration admission path or the exact
behavioral write/read interface they are intended to challenge.

Minimum candidates:

- duplicate migration version with changed SHA;
- history rewrite/update/delete;
- DDL without history and history without DDL attempt;
- partial migration failure;
- search-path hijack;
- PUBLIC schema CREATE or table privilege;
- owner bypass / FORCE RLS removal;
- `WITH CHECK` removal;
- role membership escalation;
- disabled append-only trigger;
- missing audit pair;
- `NOT VALID` constraint left unvalidated;
- missing direct scope FK/composite scope check;
- cross-scope FK or lineage mismatch;
- missing rights/retention assignment;
- expired/revoked rights/retention accepted;
- evidence mint before admission;
- duplicate concurrent admission/evidence mint;
- raw locator or bytes introduced;
- unsupported parser/breaking fingerprint accepted;
- mutable panel version;
- customer/private or strategy field introduced;
- secret-bearing error/result envelope.

Detectors must be semantic and invariant-based. Object names may identify the target,
but a detector may not pass merely because a known fixture name or column name exists.

## 010 — Recovery verification support

Required verification facts:

- database identity and marker continuity;
- exact migration history rows and SHA values;
- schema fingerprint continuity;
- role/RLS policy continuity;
- append-only trigger and audit-pairing continuity;
- representative evidence/citation resolution where the substrate contains fixtures;
- raw manifest hash/support continuity;
- scope isolation after restore.

A simple schema count is a structural precheck only. DB-4 must explicitly decide which
restore claims belong in DB-4 and which remain DB-8, using honest proof classes.

## Hammer-family coverage matrix

| Hammer | Required DB-4 physical target | Minimum behavioral action |
|---|---|---|
| H1 | direct scope FKs, composite joins, FORCE RLS, scope context | same-scope allowed; cross-scope read/write denied |
| H2 | rights assignments/transitions and transaction/read gates | missing/revoked/unknown rights blocks capture/admission/read |
| H3 | retention assignments/deadlines/transitions | missing deadline/expired posture blocks; purge transition honored |
| H4 | absent customer/private fields and safe validation/errors | private/customer field or payload rejected without echo |
| H5 | forbidden persistence register and narrow schema | strategy/recommendation/conclusion field/table candidate rejected |
| H6 | complete package and admission constraints | incomplete package/admission envelope rejected |
| H12 | raw manifest/hash/bytes/token separation | bad digest/bytes/locator/token exposure rejected |
| H15 | distinct identity namespaces and lineage | pre-admission evidence mint/identity substitution rejected |
| H19 | privilege denial + reject-mutation triggers | UPDATE/DELETE rejected under application role |
| H20 | unique keys, expected state, locking | forced-overlap duplicate capture/admission/mint yields one outcome |
| H21 | same-transaction audit pairing | unpaired consequential write rolls back; paired write commits |
| H22 | atomic SHA-bound migration/history, fingerprint, rollback | forward/rollback/failure/history-rewrite scenarios proven |

## Result-record requirement

Every executed row must produce or reference an immutable result record containing:

- exact requirement/hammer ID;
- exact migration/profile/check path and SHA;
- code commit and dirty-tree state;
- database identity/class/marker;
- authority reference;
- actor/role used;
- expected operation and expected SQLSTATE/outcome;
- observed result;
- cleanup result;
- evidence location;
- proof class;
- review status;
- supersession lineage.

## R1 exit conditions

R1 is ready for owner review only when:

- every DB-3 relation family and enforcement mechanism appears above;
- every mandatory DB-4 hammer has a behavioral action;
- no row maps only to object existence/counting;
- the current thin migrations are explicitly non-promotable;
- R2, R3, R4, and R5 implementation packages can be derived without guessing;
- independent review finds no accepted DB-3 responsibility silently omitted.
