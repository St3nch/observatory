# DB-2 Physical Data-Contract Freeze Specification

Status: candidate under DB-2 recovery reconciliation; not accepted
Candidate version: 0.2.1
Date: 2026-07-13
Milestone: DB-2 active for reconciliation and owner review only
Recovery authority: `decisions/2026-07-13-database-phase-recovery-to-db1.md`

## Purpose and authority boundary

Candidate v0.2.0 failed independent steward review. This v0.2.1 revision is the
single reconciled logical physical-data-contract candidate for DB-2. It
defines what later physical design would have to preserve. It defines no table,
column, foreign key, index, role, SQL, DDL, migration, database, artifact store,
provider integration, or persistence implementation.

Authority order is: accepted decisions; `02-boundaries.md`; current-state authority;
accepted contracts; accepted hammer policy; this candidate. Planning-inbox status
does not promote this file to authority. Candidate version 0.2.1 is not accepted,
DB-2 is not closed, and DB-3 is not active. Candidate v0.2.0 and its rejected review
remain failed historical working-tree states, not proof.

This candidate does not authorize PostgreSQL, roles, credentials, SQL/DDL,
migrations, database tools, synthetic or real persistence, providers, paid pulls,
capture, governed artifact storage, customer/private data, recurring work,
production, or strategy/recommendation/conclusion/report-state persistence.

## Accepted DB-1 input reconciliation

| Accepted input | Source and controlling clause | DB-2 satisfaction | Result / correction |
|---|---|---|---|
| Telescope doctrine and consumer promotion | `02-boundaries.md` Core Boundary; `contracts/consumer-promotion.md` | Observation, testimony, and transition facts are separated from derived meaning; conclusions promote out | Fully represented; forbidden register expanded |
| Scope | `contracts/scope-rights-retention.md` R1-R7 | Scope and scope class are durable governed context; customer identity is prohibited | Fully represented |
| Rights | same, R8-R12, R19; H2 | Versioned vocabulary, assignment, assignment history, and derived effective state are separate | Corrected C-08 and broadened target coverage |
| Retention | same, R12-R15, R19; H3 | Versioned vocabulary, assignment, deadline/purge posture, history, and derived effective state are separate | Corrected C-09 and broadened target coverage |
| Evidence identity | `contracts/evidence-id-citation.md` R1-R14 | Capture, attempt, provider, raw, observation, evidence, citation, and report-safe identities stay distinct | Completed identity register |
| Citation handles | same R2-R5; OR-A4 / OR-D3 | Internal handle is durable, non-enumerable, status-aware; `blocked` is a lifecycle/read state | Corrected C-12 |
| CapturePackage | `contracts/capturepackage-v0-1.md`; H6 | Immutable envelope facts, append-only transitions, and derived current state are separate | Compound classification removed; H14 panel binding added |
| Capture events/attempts | same; `contracts/evidence-id-citation.md` `capture_id`; H7/H20/H21 | `capture_id` identifies the accepted capture event/attempt and groups its zero-to-many observations; it is distinct from `capture_package_id` | Corrected rejected v0.2.0 identity conflict |
| Query panels and runs | `contracts/query-panel.md` R1-R20; H14 | Panel definitions are versioned; used versions immutable; runs are append-only and bind exact version | `panel_run_id` and cardinalities made explicit |
| Candidate observations | C2 plan; evidence contract | Bounded durable internal-review record, never evidence/citable/raw/strategy/rejected-evidence storage | Corrected C-02 restrictions |
| Observation admission and promotion | evidence contract R5/R10/R14; H15/H19/H21 | Admitted observation facts are immutable; admission and later states are transitions; evidence identity follows admission | Fully represented |
| Provider testimony | `contracts/provider-testimony.md`; H8 | Provider output remains attributed testimony with its own identity and time/context | Fully represented |
| Provider cross-check/disagreement | `decisions/2026-07-12-m16-provider-cross-check-contract-and-rulings.md` OR-A1/M16-R1-R7 | Computed at read time; no ledger, winner, average, consensus, or score persists | Fully represented |
| Raw artifact and drift | `contracts/raw-archive-provider-drift.md`; OR-C2/OR-C4; H12/H13 | Manifest facts, artifact identity, opaque pointer, conditional content, fingerprint facts, and transition histories are distinct | Corrected C-03/C-05/C-06 and raw ownership terminology |
| Freshness and volatility | `contracts/freshness-staleness-volatility.md` R1-R15; H9 | Vocabularies/assignments are distinct from read-time age, freshness, fitness, warnings, and blocks | Previously combined concept split |
| Claim safety | `contracts/claim-safety.md` R1-R13; H5/H9/H10/H15-H18 | Claim inputs and intent are ephemeral; support, warnings, and promotion requirements are derived; predictive, causal, recommendation, and accepted-conclusion persistence is forbidden | Every accepted claim type and warning is explicit below |
| M10 logical responsibilities | `planning-inbox/m10-logical-schema-plan-c2.md` accepted C2 responsibilities | Observed artifact reference, validation result/status, validation-failure vocabulary, and bounded rejection reason are separate concepts | Previously omitted responsibilities made explicit below |
| Typed-read exposure | OR-D1-D5; `contracts/typed-read-api-mcp-v0-1.md` v0.1.1 | Safe evidence fields only; raw locators, credentials, private data, and blocked evidence never exposed | Fully represented |
| Report-safe references | `decisions/2026-07-12-m15-searchclarity-contract-and-consumer-boundary-rulings.md` OR-E1 | Consumer-owned, artifact-local, opaque mapping; no public resolution or workflow state | Fully represented |
| Customer/owned overlays | M17 accepted ruling 1-8 | Ephemeral request input; no identifiers, values, hashes, summaries, logs, or manifests persist | Fully represented |
| Audit events | V9/N4; OR-D5; H21 | Append-only, `audit_first`, same consequential transaction; ordinary reads create none | Corrected C-10 |
| Security/access logging | OR-D5; H1/H3/H17/H21 | Separate append-only operational log, retention-gated, security-only, no credentials/private payload/LLM reasoning | Corrected C-11 and H3 added |
| Fail-closed admission | scope contract; acceptance policy v0.2 | Missing/unknown scope, rights, retention, identity, provenance, panel binding, or authority blocks admission/use | Full register below |
| Hammer policy | `hammers/hammer-matrix-v0-2.md`; `hammers/acceptance-gate-policy-v0-2.md` | Every H1-H22 is mapped to exact candidate concepts and a pass/fail-closed condition | Full audit below; mappings are `defined_only` |

No accepted DB-1 input is absent or contradicted. Open source/provider/capture and
future capability rulings remain fail-closed and do not block this logical freeze.

## Classification vocabulary

Each concept has exactly one primary classification:

| Classification | Meaning |
|---|---|
| `durable` | Canonical state may persist only under later accepted rights, retention, and implementation gates |
| `append_only` | Historical fact/event that is never silently overwritten |
| `versioned` | Governed versions preserve prior versions |
| `derived` | Computed from canonical inputs; not canonical stored meaning |
| `ephemeral` | Request/process-bound and prohibited from persistence |
| `external` | Owned outside Observatory; at most a bounded non-secret reference is retained |
| `forbidden` | Must not exist in canonical, cache, scratch, raw metadata, log, or side storage |
| `unresolved` | Owner decision is required and affected behavior fails closed |

`audit_first`, `governed`, `internal_only`, `non_evidence`, `rights_gated`,
`retention_gated`, and `operationally_separate` are qualifiers, never classes.

## Concept register: identity, classification, lifecycle, and ownership

`None` under open ruling means the logical concept is resolved; future execution
authority may still be absent.

| Concept | Exact definition / accepted authority | Class | Qualifiers | Identity owner and namespace | Lifecycle; immutable facts; events/history; derived or mutable current state | Open ruling |
|---|---|---|---|---|---|---|
| Scope | Observatory-local observation partition; scope contract | `durable` | governed | Observatory, `scope_id` | Facts: ID/class/creation basis. Events: activation/block/retirement. Current status derived; no direct mutable status required | New class is OR-G3 |
| Scope-class vocabulary | Allowed scope classes and meanings | `versioned` | governed | Governance, `scope_class_version_id` | Version facts immutable; supersession history append-only; effective version derived | OR-G3 for additions |
| Source family | Governed category controlling capture/raw posture | `versioned` | governed | Governance, `source_family_id` | Version facts immutable; admission/retirement transitions append-only; current posture derived | New family requires ruling |
| Source-family assignment | Binding of a target/source to one family version | `append_only` | audit_first | Governance, `source_family_assignment_id` | Assignment facts immutable; reassignment/revocation events append; effective assignment derived | None |
| Capture instrument/source identity | Admitted provider/API/manual method identity, not permission by existence | `versioned` | governed | Governance, `capture_instrument_id` | Identity/version facts immutable; admission/block/retirement history append-only; current posture derived | Source-specific admission |
| Query panel | Named measurement program and immutable used versions | `versioned` | governed | Observatory, `query_panel_id`, `query_panel_version_id` | Definition/version facts immutable after use; supersession/retirement events append; active version derived | Execution separately gated |
| Panel run | One attempt against exactly one panel version | `append_only` | audit_first | Observatory, `panel_run_id` | Run facts/events immutable; start/complete/fail/block transitions append; current run state derived | Execution separately gated |
| CapturePackage | Admission envelope binding scope, panel/run when applicable, source, method, authority, ceilings, stop conditions, rights, retention, and intent | `durable` | governed; non_payload | Observatory, `capture_package_id` only | Envelope facts immutable after submission; package transitions append through `capture_package_transition_id`; current package state derived | None |
| Capture event/attempt | One accepted capture event or attempt under one package; explains zero, one, or many observations | `append_only` | audit_first | Observatory, `capture_id` | Event/attempt facts immutable; start/succeed/fail/block/duplicate/cancel transitions append through `capture_transition_id`; current capture state derived | Execution separately gated |
| Proposed `capture_attempt_id` rename/alias | A possible future alternate name for accepted `capture_id`; no accepted authority currently establishes it | `unresolved` | fail_closed; not_active | No active namespace; owner ruling required | No facts, transitions, aliases, or reads may use it; any occurrence outside this unresolved disposition blocks the package | Owner ruling required before use |
| Provider identity | Identity of attributed provider, distinct from instrument version and job | `versioned` | governed | Governance, `provider_id` | Provider identity/version facts preserved; admission/retirement history append; current posture derived | Provider admission separately gated |
| Provider job identity | Provider-owned task/job/request identifier | `external` | provider_attributed | Provider namespace, `provider_job_id` | External lifecycle; Observatory retains bounded copied reference with provider/attempt context | None |
| Provider testimony | Provider-attributed returned observation/metric, never web truth | `append_only` | evidence_candidate | Observatory, `provider_testimony_id` | Returned value/context immutable; support/withdrawal transitions append; current usability derived | None |
| Provider cross-check/disagreement | Side-by-side comparison of attributed testimony | `derived` | compute_on_read | Read layer; no durable ID | No persisted lifecycle/history/current record; recomputed with per-side context | Persistence forbidden under OR-A1 |
| Candidate observation | Bounded internal pre-admission record | `durable` | non_evidence; non_citable; retention_gated | Observatory, `candidate_observation_id` | Candidate facts immutable; validation/admit/reject/expire transitions append; current review state derived | None |
| Admitted observation | Immutable historical fact of what was observed | `append_only` | evidence_fact | Observatory, `observation_id` | Facts immutable; supersede/withdraw/rights-block/retention-expire/invalidate events append; current usability derived | None |
| Evidence promotion/admission decision | Decision that a candidate becomes evidence, or is rejected/blocked | `append_only` | audit_first | Observatory, `admission_transition_id` | Decision facts immutable; corrections supersede; current admission state derived | None |
| Evidence identity | Stable logical resolver minted after admission | `durable` | status_aware | Observatory, `evidence_id` | Identity/binding facts immutable; status transitions append; current resolvability derived | None |
| Internal citation handle | Non-enumerable internal mapping to evidence identity | `durable` | internal_only | Observatory, `citation_handle` | Mapping immutable; deprecate/block transitions append; current state active/deprecated/blocked derived | Public resolution forbidden |
| Report-safe reference | Artifact-local consumer-owned opaque mapping | `external` | non_enumerable | Consumer artifact namespace, `report_safe_reference` | Consumer lifecycle; Observatory owns no report/reference workflow state | Production/public resolution not authorized |
| External consumer reference | Bounded locator to consumer context, never customer identity/FK | `external` | internal_only | Consumer namespace, `external_consumer_reference` | Consumer-owned lifecycle; only bounded kind/value reference where authorized | None |
| Raw artifact manifest | Immutable metadata describing support content and integrity | `durable` | rights_gated; retention_gated | Observatory, `raw_manifest_id` | Manifest facts immutable; support/parser/purge/review transitions append separately; current status derived | Artifact implementation not authorized |
| Raw payload identity | Observatory identity for governed raw support, distinct from content and pointer | `durable` | internal_only | Observatory, `raw_payload_id` | Identity and manifest binding immutable; support/purge transitions append; current availability derived | None |
| Opaque artifact pointer token | Internal opaque token resolving through future governed boundary | `durable` | internal_only; non_locator | Observatory artifact boundary, `raw_artifact_pointer_id` | Token/binding facts immutable; missing/purge/invalidate transitions append; current resolvability derived | Artifact implementation not authorized |
| Governed retained artifact content | Bytes retained by Observatory only if a later source-family/artifact-store gate authorizes it | `durable` | conditional; rights_gated; retention_gated | Observatory artifact boundary, content addressed by `raw_payload_id`, not path | Content immutable; purge/support-loss events append; availability derived | Current persistence unauthorized |
| Consumer-owned external content | Content actually owned outside Observatory with only bounded reference retained | `external` | consumer_owned | External owner namespace | External lifecycle; no Observatory copy | None |
| Relational raw payload bytes | Raw bytes embedded in ordinary relational evidence storage | `forbidden` | none | None | No lifecycle; reject/purge if detected | None |
| Underlying storage locator | Filesystem path, URI, bucket/key, connection detail, or credential-bearing locator exposed as data | `forbidden` | secret_boundary | None | Never stored in typed-readable concepts or exposed | None |
| Shape fingerprint | Immutable observed canonical shape fingerprint | `append_only` | shape_metadata | Observatory, `shape_fingerprint_id` | Observed fingerprint facts immutable; recognition/review/break/retire transitions append separately; current recognition derived | None |
| Parser implementation reference | Bounded reference to external implementation release/commit | `external` | versioned_reference | Implementation repo, `parser_version_id` | External lifecycle; Observatory retains exact bounded reference only | None |
| Provider drift event | Immutable fact that shapes differed in a bounded context | `append_only` | audit_first | Observatory, `drift_event_id` | Detection facts immutable; no resolved flag mutation | None |
| Drift review history | Review/accept/block/resolve transitions for drift | `append_only` | audit_first | Observatory, `drift_review_transition_id` | All transitions immutable; current drift posture derived | None |
| Rights vocabulary | Governed meanings for rights classes | `versioned` | governed | Governance, `rights_vocabulary_version_id` | Version facts immutable; supersession history append; effective version derived | None |
| Rights assignment | Binding of one target to one vocabulary entry and basis | `durable` | rights_gated | Governance, `rights_assignment_id` | Assignment facts immutable; lifecycle transitions in separate history; effective assignment derived | None |
| Rights-assignment history | Assign/revise/revoke/expire/block transitions | `append_only` | audit_first | Governance, `rights_assignment_transition_id` | Transition facts immutable; no in-place history mutation | None |
| Effective rights state | Current target rights computed from assignment/history/time | `derived` | fail_closed | Read/admission layer; no durable ID | Recomputed; no persistence as independent truth | None |
| Retention vocabulary | Governed retention meanings | `versioned` | governed | Governance, `retention_vocabulary_version_id` | Version facts immutable; supersession history append; effective version derived | None |
| Retention assignment | Binding of one target to posture/basis | `durable` | retention_gated | Governance, `retention_assignment_id` | Assignment facts immutable; transitions separate; effective assignment derived | None |
| Retention deadline/purge posture | Deadline, no-storage, manifest-only, purge, or retain posture attached to assignment | `durable` | retention_gated | Owned by `retention_assignment_id`; no competing ID | Deadline/posture facts immutable for that assignment; changes create new assignment/transition; current due state derived | None |
| Retention-assignment history | Assign/revise/expire/purge-due/purge-complete transitions | `append_only` | audit_first | Governance, `retention_assignment_transition_id` | Transition facts immutable | None |
| Effective retention state | Current permitted retention/use computed from assignment/history/time | `derived` | fail_closed | Read/admission layer; no durable ID | Recomputed | None |
| Audit event | Consequential-change audit fact in same governed transaction | `append_only` | audit_first | Observatory, `audit_event_id` | Immutable; correction creates superseding event | None |
| Security/access log | Authentication/authorization/enumeration/rate/ceiling operational event | `append_only` | operationally_separate; retention_gated | Security subsystem, `security_access_log_id` | Immutable events; no customer activity profile/current state | None |
| Freshness vocabulary/policy | Governed freshness statuses and family policy | `versioned` | governed | Governance, `freshness_policy_version_id` | Version facts immutable; supersession append; effective version derived | Threshold changes require governance |
| Freshness assignment | Binding of evidence family/target to policy version | `durable` | governed | Governance, `freshness_assignment_id` | Assignment facts immutable; changes create new assignment; effective binding derived | None |
| Volatility vocabulary/policy | Governed volatility classes and policy | `versioned` | governed | Governance, `volatility_policy_version_id` | Version facts immutable; supersession append; effective version derived | None |
| Volatility assignment | Binding of evidence family/target to volatility policy entry | `durable` | governed | Governance, `volatility_assignment_id` | Assignment facts immutable; changes create new assignment; effective binding derived | None |
| Current observation age | Elapsed age at read time | `derived` | read_time | No durable ID | Recomputed from trusted time inputs | None |
| Current freshness | Fitness status for a proposed use | `derived` | read_time | No durable ID | Recomputed; stale evidence remains historical evidence | None |
| Current claim fitness | Whether exact evidence may support exact claim intent | `derived` | read_time; non_conclusion | No durable ID | Recomputed; never a recommendation or final claim | None |
| Warning/fail-closed read state | Required caveat, historical-only downgrade, or blocked output | `derived` | read_time | No durable ID | Recomputed from rights/retention/status/freshness/support/context | None |
| Raw support-loss/purge transition | Immutable support missing/purge due/purged/unavailable transition | `append_only` | audit_first | Observatory, `raw_support_transition_id` | Transition immutable; current support state derived | None |
| Customer/owned first-party overlay | Request-bound private series or intervention context | `ephemeral` | no_storage | Supplying consumer, request-only `external_overlay_reference` | Exists only during call; discarded; no Observatory identity/history/current state | Real inputs remain unauthorized |
| Strategy/recommendation/conclusion/report state/LLM reasoning | Interpretive or consumer workflow meaning | `forbidden` | none | External owning consumer only | No Observatory lifecycle | Doctrine change required |

## Additional accepted concept dossiers

The following concepts were accepted before DB-2 but were missing or only grouped in
v0.2.0. Each row is a complete logical dossier. A field embedded in another concept
still receives a classification and ownership rule; physical storage shape remains
future work.

### M10 artifact, validation, and rejection concepts

| Concept | Definition and authority | Class / qualifiers / identity | Facts, transitions, current state | Provenance; scope; rights; retention | Relationships; write; read exposure | Loss/failure/hammers/forbidden/open ruling |
|---|---|---|---|---|---|---|
| Observed artifact reference (`observed_artifact_reference`) | Identifies the public or controlled artifact actually observed; M10 `Observed Artifact Reference`, raw contract | `durable`; public_reference; Observatory `observed_artifact_reference_id` | Immutable kind, bounded reference, access posture, observation time; correction/supersession uses `observed_artifact_reference_transition_id`; current usability derived | Capture/package provenance required; exactly one scope; rights/retention assignments required before admission | Package 1:N references; capture/admission path writes; ordinary reads expose only rights-safe public reference fields, never internal storage locators | Support loss blocks raw/current claims but preserves permitted history; H1-H5/H12/H15/H18-H22; no private URL, dashboard path, recommendation target; source admission remains gated |
| Validation-failure vocabulary | Governed classes for missing/invalid scope, rights, retention, provenance, hash, shape, identity, panel, authority, or forbidden content; M10 validation and CapturePackage R17 | `versioned`; governed; Governance `validation_failure_vocabulary_version_id` | Immutable version members; supersession is version history; effective version derived | Decision/contract provenance; vocabulary is scope-neutral; use inherits target rights/retention | One version 1:N validation results; governance writes; specialized reads expose codes/definitions | Unknown code fails closed; H1-H7/H12-H18/H21; must not contain rejected private payload or strategy; additions require governance |
| Validation result | Immutable result of validating one package/capture/candidate/observation/raw support item | `append_only`; audit_first; Observatory `validation_result_id` | Facts: target, vocabulary version/code, time, validator class, bounded reason; revalidation creates a new result; current `validation_status` derived | Target provenance/scope/rights/retention inherited; result retention cannot outlive permitted audit posture | Target 1:N results; validation boundary appends; internal governed reads, safe status only in typed output | Missing result blocks admission; H1-H7/H12-H18/H20/H21; no payload echo or conclusion; none |
| Validation status (`validation_status`) | Current `pending / valid / invalid / blocked` posture derived from validation results and target state | `derived`; fail_closed; no durable ID | No base facts or own history; recomputed from append-only results | Inherits target provenance/scope/rights/retention | One derived state per target/use; read layer computes; safe status/warning only | Unknown/missing becomes blocked; H2/H3/H6/H12/H13/H18/H21; never directly mutable; none |
| Rejection reason (`rejection_reason`) | Bounded reason attached to a rejected/blocked validation or admission transition | `append_only`; audit_first; no independent ID because owned by `validation_result_id` or `admission_transition_id` | Reason code/version and safe explanation immutable; correction creates superseding result/transition; current rejection posture derived | Target provenance/scope/rights/retention inherited | Exactly one primary reason and 0:N secondary codes per rejecting result; validator/admission authority writes; internal reads, safe code only externally | Purged with governing result only when retention requires; missing reason blocks consequential rejection; H3-H6/H15/H18/H21; no rejected payload, customer data, strategy, or LLM reasoning; none |

### Freshness and volatility concepts

| Concept | Definition and authority | Class / qualifiers / identity | Facts, transitions, current state | Provenance; scope; rights; retention | Relationships; write; read exposure | Loss/failure/hammers/forbidden/open ruling |
|---|---|---|---|---|---|---|
| `captured_at` | Observatory-side time an accepted capture/observation occurred; freshness contract | `append_only`; immutable_timestamp; no independent ID, owned by `capture_id` and observation | Immutable fact; corrections require superseding capture/observation; age/current fitness derived | Capture clock/provenance required; target scope/rights/retention inherited | Exactly one required value per capture and admitted observation; capture/admission writes; ordinary reads expose it | Missing/untrusted time blocks current claims and normally admission; H6/H9/H15/H19/H21/H22; never backdated or overwritten; none |
| `provider_reported_time` | Provider-attributed data/crawl/report time distinct from `captured_at`; freshness/provider contracts | `append_only`; provider_attributed; no independent ID, owned by testimony/observation | Immutable reported fact; provider correction is new testimony; current age effect derived | Provider response provenance; testimony scope/rights/retention inherited | Testimony 0:N typed reported times; ingestion writes; typed reads expose label/value with attribution | Missing is allowed only with warning; mismatch never replaces `captured_at`; H8/H9/H13/H15/H19; no invented timestamp; none |
| Observation age (`observation_age`) | Elapsed duration at exact read/use time | `derived`; read_time; no durable ID | Inputs immutable timestamps; no history; recomputed | Evidence provenance and target constraints inherited | One value per evidence/read-time pair; read layer computes; ordinary typed reads may expose | Missing trusted time yields unknown/block; H9/H15; no persistence as current truth; none |
| Age-band vocabulary | Governed labels such as `0-24h`, `1-7d`, `8-30d`, `31-90d`, `90d+`, `unknown` | `versioned`; governed; Governance `age_band_vocabulary_version_id` | Version members immutable; version supersession preserved; effective version derived | Contract/decision provenance; scope-neutral; use inherits evidence rights/retention | Version 1:N derived age-band results; governance writes; definitions specialized, label ordinary | Unknown policy produces `unknown`; H9/H21/H22; not a product guarantee; threshold change requires governance |
| `age_band` | Label selected from the governed age-band vocabulary for an observation age | `derived`; read_time; no durable ID | No base facts/history; recomputed with vocabulary version | Inherits evidence provenance/scope/rights/retention | One result per evidence/read-time/policy tuple; read layer computes; ordinary typed reads expose label/version | Unknown becomes caveat/block; H9/H15; never stored as immutable observation fact; none |
| `freshness_status` | Fitness label for exact evidence and claim intent | `derived`; read_time; no durable ID | No base facts/history; recomputed from times, policy, volatility, update window, status, rights, retention | All input provenance retained; scope/right/retention failures dominate | One result per evidence/claim-intent/read-time tuple; read layer computes; ordinary reads must expose with reasons | Unknown/stale blocks or downgrades; H2/H3/H9/H10/H15/H16; no task/priority/recommendation persistence; none |
| `volatility_class` | Effective volatility label for an evidence family/target under a governed policy | `derived`; read_time; no durable ID | Policy/assignment facts and histories separate; current label recomputed | Assignment provenance and target constraints inherited | Target 0:N assignments over time, one effective result; read layer computes; ordinary reads expose label/version | Missing becomes `unknown`; H9/H10/H15; no certainty/quality score; none |
| Update-window input (`update_window`) | Known rollout/incident/provider/platform change relevant to interpretation | `ephemeral`; optional_read_input; request-only `update_window_reference` | No Observatory base fact/history/current state unless later admitted as its own observation under another source contract | Caller/source provenance required; request scope; no persistence, rights/retention inherited only for the call | Request 0:N inputs, evidence read consumes; authorized caller supplies; read output exposes bounded caveat, not locator | Missing relevant input yields unknown/caveated state; H8-H10/H13/H16-H18; no invented cadence, feed, task, or durable window record; feed admission unresolved |

### Claim-safety vocabulary, inputs, results, and warnings

The accepted claim-intent vocabulary has these members. The first seven describe
ephemeral proposed claim inputs. Predictive, causal, recommendation, and accepted
conclusion content is forbidden in Observatory persistence. None is an observation.

| Member concept | Exact meaning / authority | Class | Input/result behavior | Fail-closed and forbidden boundary | Hammers |
|---|---|---|---|---|---|
| Historical observation claim (`historical_observation_claim`) | Says what was observed at a bounded past context/time; claim-safety R2 | `ephemeral` | May be supplied as claim input; support is derived | Requires valid evidence/provenance/rights/retention and dated context; never persists claim prose | H2/H3/H5/H9/H15-H17 |
| Current-state claim (`current_state_claim`) | Says something is currently true; R3 | `ephemeral` | Input only; derived support requires freshness fitness | Stale/unknown/missing caveat blocks; no durable truth | H5/H9/H10/H15/H16 |
| Comparative claim (`comparative_claim`) | Compares bounded evidence sets; R3/R12 | `ephemeral` | Input only; support derived with comparability/time checks | Incomparability/time-distance warning or block; no winner/conclusion persistence | H5/H8/H9/H15/H16 |
| Absence claim (`absence_claim`) | `not observed` within exact sampled context; R4 | `ephemeral` | Input only; support derived | Missing sample/panel/time/depth context blocks; universal absence forbidden | H9-H11/H14-H16 |
| Provider metric claim (`provider_metric_claim`) | Restates a provider metric as testimony; R5 | `ephemeral` | Input only; support derived | Provider attribution/definition/time mandatory; web-truth language forbidden | H8/H9/H13/H15/H16 |
| AI/GEO claim (`ai_geo_claim`) | Sample-bound mention/citation/absence statement; R7 | `ephemeral` | Input only; support derived | Prompt/surface/time/sample warnings mandatory; trust/authority/causality/universal visibility forbidden | H8-H10/H15/H16 |
| Marketplace claim (`marketplace_claim`) | Bounded public marketplace observation; R8 | `ephemeral` | Input only; support derived | Source/method/rights/retention/point-in-time ceiling required; traffic/sales/private inference forbidden | H2-H5/H9/H11/H15/H16 |
| Predictive claim (`predictive_claim`) | Forecast of future state; R9 | `forbidden` | No Observatory input-to-persist or output record | Reject persistence; may be produced only by owning consumer from evidence | H5/H10/H16-H18 |
| Causal claim (`causal_claim`) | Claims evidence caused an outcome; R10 | `forbidden` | No Observatory durable concept | Reject persistence/automatic derivation | H5/H9/H10/H16-H18 |
| Recommendation claim (`recommendation_claim`) | Advises action; R11 | `forbidden` | No Observatory durable concept | Reject; consumer owns any recommendation | H5/H16-H18 |
| Accepted conclusion (`accepted_conclusion`) | Consumer-accepted meaning/decision | `forbidden` | No Observatory durable concept | Promote out; never cache/log/embed as evidence | H4/H5/H16-H18/H21 |

| Concept | Definition and authority | Class / qualifiers / identity | Facts, transitions, current state | Provenance; scope; rights; retention | Relationships; write; read exposure | Loss/failure/hammers/forbidden/open ruling |
|---|---|---|---|---|---|---|
| Claim-intent vocabulary | Governed closed labels above plus exact meanings; freshness and claim-safety contracts | `versioned`; governed; Governance `claim_intent_vocabulary_version_id` | Version facts immutable; supersession preserved; effective version derived | Accepted contract/decision provenance; scope-neutral; use inherits evidence constraints | Version 1:N intent selections; governance writes; definitions specialized, labels allowed in request/response | Unknown label blocks; H5/H9/H10/H16-H18/H21/H22; no semantic strengthening; additions require governance |
| Claim-intent selection (`claim_intent`) | One proposed use selected from an exact vocabulary version for a claim input | `ephemeral`; request_bound; no durable ID | No base facts/history/current state; exists only for the read request | Caller/request provenance; exact scope; evidence rights/retention enforced | Claim input exactly one selection; authenticated caller supplies; request/response exposure only | Discard after request; unknown/ambiguous selection blocks; H1/H5/H9/H10/H16-H18; no durable assignment or silent intent strengthening; none |
| Claim input (`claim`) | Proposed claim type and bounded non-private subject/context supplied for evidence selection | `ephemeral`; request_bound; request-only `claim_input_reference` | No durable facts/history/current state | Authenticated caller, request, scope, evidence constraints; no payload retention | Request exactly one intent and 0:N bounded filters; caller supplies; visible only within authorized read | Discard after request; unknown/private/recommendation content blocks; H1/H4/H5/H16-H18; no report prose/customer identity; none |
| Claim support result (`claim_support`) | Read-time result describing whether evidence supports, caveats, downgrades, or blocks the claim input | `derived`; non_conclusion; no durable ID | No base facts/history; recomputed from evidence and policies | Evidence/caller/request provenance; scope/rights/retention enforced | One result per claim input/evidence set/read time; read layer computes; ordinary response must keep caveats attached | Missing evidence/context yields block; H1-H5/H8-H18; no final wording, truth, recommendation, or durable support record; none |
| Claim-use warning (`claim_use_warning`) | Plain/machine-readable warning for unsafe or bounded use | `derived`; attached_output; no durable ID | Recomputed; no history | Inherits support-result provenance/constraints | Support result 0:N warnings; read layer emits inseparably | Missing mandatory warning blocks response/support; H5/H9/H10/H15-H18; no task; none |
| Freshness warning (`freshness_warning`) | Age/volatility/update-window warning | `derived`; attached_output; no durable ID | Recomputed | Freshness input provenance inherited | Support result 0:N; read layer | Missing when required blocks; H9/H10/H15/H16; no recapture authorization; none |
| Provider-attribution requirement (`provider_attribution_required`) | Requirement that provider identity/method/time/caveats travel with metric testimony | `derived`; attached_requirement; no durable ID | Recomputed | Testimony provenance inherited | Provider-metric result exactly one effective requirement; read layer | Missing attribution blocks; H8/H9/H15-H17; no provider truth; none |
| Sample-bound warning (`sample_bound_warning`) | Warning limiting AI/GEO/absence/marketplace output to sample context | `derived`; attached_output; no durable ID | Recomputed | Panel/run/capture provenance inherited | Applicable result requires one or more context warnings; read layer | Missing sample context blocks; H9-H11/H14-H16; no universalization; none |
| Absence warning (`absence_warning`) | Exact `not observed in this context` limitation | `derived`; attached_output; no durable ID | Recomputed | Panel/run/evidence provenance inherited | Absence result exactly one mandatory warning; read layer | Missing warning blocks absence support; H9/H10/H14-H16; no universal absence; none |
| Incomparability warning (`incomparability_warning`) | Identifies mismatched subject, metric, surface, scope, time, or method | `derived`; attached_output; no durable ID | Recomputed | Per-side provider/evidence provenance retained | Comparative result 0:N dimension warnings; read layer | Material mismatch downgrades/blocks; H8/H9/H15/H16; no average/winner; none |
| Rights/retention warning (`rights_retention_warning`) | Discloses bounded use or block from effective rights/retention | `derived`; fail_closed; no durable ID | Recomputed | Assignment/history provenance retained; exact scope | Support result exactly one effective disposition when constrained; read layer | Missing/expired/unresolved blocks; H2/H3/H12/H15/H16; no legal conclusion; none |
| Consumer-promotion requirement (`consumer_promotion_required`) | Boolean/disposition that meaning-bearing output must promote to owning consumer | `derived`; attached_requirement; no durable ID | Recomputed; no history | Request/evidence/consumer provenance; scope/rights/retention enforced | One result per response; read layer computes; ordinary output exposes it | Missing/false when required blocks handoff; H4/H5/H16/H17/H21; no automatic promotion/workflow state; none |

### Accepted-contract remainder audit

These additional accepted contract concepts are explicit so no identifier, input,
governance fact, or read result is hidden inside a broad group.

| Concept | Definition / authority | Class and identity | Facts/history/current state | Bindings, relationships, authority, exposure | Failure/loss, hammers, forbidden/open ruling |
|---|---|---|---|---|---|
| Source-admission status | Effective permission posture for a source family/instrument; scope contract | `derived`; no durable ID | Derived from source/instrument versions and transitions; no own history | Applies before package/capture/admission; governance supplies facts, admission/read layer computes; safe status exposed | Unknown/not-reviewed blocks; H2/H6-H8/H11/H13/H21; tool/credential existence cannot admit; source-specific rulings remain open |
| Rights basis | Exact terms/decision/review basis for a rights assignment | `append_only`; no independent ID, owned by `rights_assignment_id` | Immutable basis reference/facts; change requires new assignment/history; effective basis derived | Target/scope provenance, rights-governance write, specialized read; ordinary output only bounded summary | Missing/stale basis blocks; H2/H11/H12/H19/H21/H22; no legal conclusion/private payload; none |
| Retention basis | Exact decision/source-family basis for a retention assignment | `append_only`; owned by `retention_assignment_id` | Immutable; change requires new assignment/history; effective basis derived | Target/scope provenance, retention-governance write, specialized read | Missing/stale blocks; H3/H12/H19/H21/H22; no silent extension; none |
| Retention expiry/deadline | Exact expiry or purge-due fact for one retention assignment | `durable`; owned by `retention_assignment_id` | Immutable per assignment; new assignment changes it; due/expired derived | Target rights/scope inherited; governance writes; safe deadline/status only where authorized | Missing for expiring posture blocks; H3/H12/H19/H21/H22; no direct mutation; none |
| Owning consumer label | Boundary label naming system that owns downstream meaning/workflow | `external`; consumer namespace, no Observatory durable consumer ID | External lifecycle; bounded label/reference only | Scope/request may reference; consumer owns writes; internal/safe read only | Unknown consumer blocks; H1/H4/H16/H17; no customer identity/FK; none |
| Capture method reference | Exact admitted manual/API/provider method version used by a capture | `external`; versioned_reference; method owner namespace | Immutable reference on `capture_id`; method versions external; current support derived from instrument status | Package/capture provenance, scope/rights/retention inherited; capture path writes; safe attribution exposed | Missing/unadmitted blocks; H2/H6/H7/H11/H13/H15; no implementation code/credential; admission separately gated |
| Operator intent | Measurement-only reason for a package/capture | `append_only`; owned by `capture_package_id` | Immutable envelope fact; correction requires new/superseding package; no current mutable state | Package provenance/scope, rights/retention inherited; preflight writes; internal bounded read | Strategy/recommendation content rejects package; H5/H6/H18/H19/H21; none |
| Approval reference | Bounded reference to exact accepted authority for gated capture/spend | `external`; decision namespace `approval_reference` | Immutable package fact; authority lifecycle external; validity derived | Package 0:1 or required 1:1 when gated; preflight copies; internal operational read | Missing/mismatched/consumed authority blocks; H6/H7/H15/H18/H20/H21; no permission inference; none |
| Cost/task ceilings | Immutable maximum spend/call/task/retry bounds on a package | `durable`; owned by `capture_package_id` | Envelope facts immutable; consumption events append under captures; remaining allowance derived | Exact approval/package provenance; preflight writes; operational-only read | Missing/exhausted blocks before spend; H6/H7/H18/H20/H21; no autonomous budget expansion; execution unauthorized |
| Stop conditions | Immutable conditions that end further capture attempts | `durable`; owned by `capture_package_id` | Envelope facts immutable; trigger facts append on `capture_transition_id`; stopped state derived | Authority/package provenance; preflight writes, runner evaluates; operational read | Missing where required or triggered blocks; H6/H7/H18/H20/H21; no scheduler/action plan; execution unauthorized |
| Raw-support status | Current support posture (`retained`, manifest-only, purged, missing, blocked, expired, mismatch) | `derived`; no durable ID | Derived from manifest/payload/token/support transitions and effective rights/retention | Evidence/raw relationships; read layer computes; typed reads expose safe status/caveat only | Unknown/inconsistent blocks raw-supported claim; H2/H3/H12/H13/H15/H17/H22; never expose token/locator; none |
| Query-panel item | One measurement item inside an exact panel version | `versioned`; Observatory `query_panel_item_id` under `query_panel_version_id` | Immutable within used version; change creates new panel version; effective inclusion derived from version/status | Panel scope/source/rights/retention; panel governance writes; safe measurement context exposed | Missing dimensions/source posture blocks run; H1-H6/H9-H11/H14/H18-H21; no strategy/priority-as-value; execution gated |
| Provider endpoint/surface recipe reference | Exact provider surface/method recipe used for testimony | `external`; versioned_reference, provider/implementation namespace | Immutable reference on capture/testimony; external version history; support derived | Provider/package provenance; capture path copies; internal attribution exposure | Missing/out-of-authority blocks; H6-H8/H11-H13/H15/H18; no credentials/request secret; provider execution gated |
| Provider metric/model-output fact | Exact provider-returned value/label/definition context | `append_only`; owned by `provider_testimony_id` | Immutable testimony fact; correction is new testimony/transition; current usability derived | Provider/capture/scope/rights/retention/times required; ingestion writes; attributed typed read | Missing definition/attribution blocks; H8/H9/H13/H15/H19/H21; no web truth/normalization; none |
| Comparison context | Subject, metric, scope, surface, method, and per-side timing for cross-check | `ephemeral`; request-bound `comparison_context_reference` | No durable facts/history/current state | Authenticated request and evidence provenance; read layer constructs; returned with derived comparison | Missing/mismatch downgrades or blocks; H1/H8/H9/H15-H18; no cross-scope or persistent ledger; none |
| Disagreement type | Derived label such as value, presence/absence, direction, or unresolved incomparability | `derived`; no durable ID | Recomputed from testimony/context; no history | Per-side constraints retained; read layer computes/exposes with attribution | Unknown/incomparable yields unresolved warning; H8/H9/H15/H16; no truth/winner/average; OR-A1 forbids persistence |
| Comparison disposition | Derived comparable/partial/incomparable/blocked posture | `derived`; no durable ID | Recomputed; no history | Same as comparison context; read layer | Missing context or rights/retention blocks; H1-H3/H8/H9/H15-H17; no durable result; none |
| Consumer request | Typed authenticated evidence request, not customer/workflow record | `ephemeral`; access-layer request ID only | Exists for one request; no Observatory history/current state | Caller/grant/scope/claim intent provenance; caller writes, read boundary validates; request-private | Discard; invalid/private/cross-scope blocks and may create safe security log; H1/H4/H5/H16-H18; no customer/order/report state; none |
| Evidence pack | Shaped response of observations, attribution, statuses, warnings, and coverage | `ephemeral`; response-bound, no durable ID | Deterministically assembled per read; no history | Evidence/request provenance and constraints; read layer writes response; authorized typed exposure | Missing mandatory caveat blocks response; H1-H5/H8-H18; no conclusion/report/raw locator; none |
| Coverage/blind-spot result | What the bounded evidence set does not cover | `derived`; no durable ID | Recomputed per request/panel/evidence set | Request/evidence provenance; read layer computes/exposes with promotion requirement | Missing coverage context blocks strong absence/completeness claims; H5/H9/H10/H14-H18; no collection task/strategy; none |
| Caller-class vocabulary | Closed authenticated caller classes and meanings; OR-D1 | `versioned`; governed access policy `caller_class_policy_version_id` | Version facts immutable; supersession preserved; effective class supplied externally | Access-layer provenance; not scope identity; security governance writes; specialized read only | Unknown/self-asserted caller blocks; H1/H4/H17/H18/H21/H22; no public/customer caller inferred; changes require ruling |
| Authorization grant | Access-layer-owned scope/request-type permission | `external`; access-layer grant reference, not Observatory evidence ID | External lifecycle; request validity derived; no customer credential copied | Caller/request/scope relation; access layer owns writes; never ordinary evidence output | Missing/expired/widened grant blocks and security-logs safely; H1/H4/H17/H18/H21; no credentials/direct SQL; none |
| Cursor | Bound, signed, expiring continuation state for one typed request | `ephemeral`; opaque request token, no durable Observatory ID | Exists until expiry; no durable history/current record | Caller/scope/request/filter/contract version binding; read layer emits/validates; opaque to caller | Invalid/expired/mismatched blocks uniformly; H1/H15/H17/H18/H20; no credential/raw locator; managed-secret gate remains future |
| Pagination/truncation result | Deterministic page metadata, ceiling disclosure, and omitted count | `derived`; no durable ID | Recomputed from authorized visible evidence; no history | Request/evidence provenance; read layer computes/exposes | Silent partial view forbidden; missing accurate disclosure blocks; H1/H15/H17/H18; no hidden rows/count leakage; none |
| Overlay freshness metadata | Consumer-supplied timestamp/status for ephemeral overlay | `ephemeral`; request-bound, no durable ID | Exists only in request; no history | Consumer/request provenance; overlay has no Observatory scope/evidence identity; caller supplies | Missing blocks current/comparative overlay use; H3/H4/H9/H16-H18; no logging/hash/manifest; real overlay unauthorized |
| Overlay discard status | Response assertion that overlay values were not retained | `derived`; no durable ID | Computed for bounded request; no history | Request/overlay provenance; read layer emits; safe status only | Failure/uncertainty blocks result; H3/H4/H16-H18; not production memory-erasure proof; none |

### Explicit lifecycle-transition concepts

Every changing-state concept below has immutable/versioned base facts, a named
`append_only` transition concept, and derived current state. No mutable current-state
record is authorized. Each transition has its own Observatory identifier because it
is independently auditable and orderable.

| Target base concept | Transition concept / identity / target relation | Event vocabulary | Write authority; audit and retention | Derived current state | Hammers |
|---|---|---|---|---|---|
| Scope (`durable`) | Scope transition, `scope_transition_id`, N:1 `scope_id` | activate, block, unblock, retire | Scope governance; audit-first; retain with governed scope history | active/inactive/blocked/retired | H1/H4/H19-H22 |
| Observed artifact reference (`durable`) | Artifact-reference transition, `observed_artifact_reference_transition_id`, N:1 artifact reference | supersede, rights-block, retention-expire, mark-unavailable, invalidate | Admission/governance; audit-first; artifact-reference retention applies | active/superseded/blocked/expired/unavailable/invalid | H1-H4/H12/H15/H19-H22 |
| Source family version (`versioned`) | Source-family transition, `source_family_transition_id`, N:1 `source_family_id` | propose, admit, block, retire, supersede | Source governance; audit-first; retain while referenced | candidate/admitted/blocked/retired | H2/H3/H7/H11-H13/H19/H21/H22 |
| Source-family assignment (`append_only` base assignment fact) | Source-family-assignment transition, `source_family_assignment_transition_id`, N:1 assignment | activate, supersede, revoke, expire | Governance; audit-first; target retention applies | effective assignment or blocked | H2/H3/H19/H21/H22 |
| Capture instrument version (`versioned`) | Instrument transition, `capture_instrument_transition_id`, N:1 instrument | propose, admit, block, retire, supersede | Instrument governance; audit-first; retain while evidence references it | candidate/admitted/blocked/retired | H2/H6-H8/H11/H13/H19-H22 |
| Query panel/version (`versioned`) | Panel transition, `query_panel_transition_id`, N:1 panel/version | submit, activate, block, supersede, retire | Panel governance; audit-first; historical versions retained | draft/active/blocked/superseded/retired | H1/H5/H6/H14/H19-H22 |
| Panel run (`append_only` base run fact) | Panel-run transition, `panel_run_transition_id`, N:1 run | plan, approve, start, complete, fail, stop, block | Future capture runner/governance; audit-first; run retention applies | planned/approved/running/completed/failed/stopped/blocked | H6/H7/H14/H19-H21 |
| CapturePackage (`durable` immutable envelope) | CapturePackage transition, `capture_package_transition_id`, N:1 package | prepare, validate, block, submit, exhaust, complete, reject, cancel | Capture admission; audit-first; package retention applies | prepared/valid/blocked/submitted/exhausted/completed/rejected/cancelled | H1-H7/H14/H18-H21 |
| Capture event/attempt (`append_only` base event) | Capture transition, `capture_transition_id`, N:1 `capture_id` | plan, start, succeed, fail, block, duplicate, cancel | Future capture runner; audit-first; capture retention applies | planned/started/succeeded/failed/blocked/duplicate/cancelled | H6/H7/H13/H19-H21 |
| Provider identity/version (`versioned`) | Provider transition, `provider_transition_id`, N:1 provider | propose, admit, block, retire, supersede | Provider governance; audit-first; retain while testimony references it | candidate/admitted/blocked/retired | H2/H7/H8/H13/H19-H22 |
| Provider testimony (`append_only`) | Testimony transition, `provider_testimony_transition_id`, N:1 testimony | support, supersede, withdraw, rights-block, retention-expire, invalidate | Admission/governance; audit-first; testimony retention applies | active/historical/withdrawn/blocked/expired/invalid | H2/H3/H8/H9/H13/H15/H19-H22 |
| Candidate observation (`durable` immutable candidate facts) | Candidate transition, `candidate_transition_id`, N:1 candidate | create, validate, invalidate, reject, admit, expire, purge | Validation/admission; audit-first; candidate retention applies | pending/valid/invalid/rejected/admitted/expired/purged | H1-H6/H13/H15/H18-H21 |
| Admitted observation (`append_only`) | Observation transition, `observation_transition_id`, N:1 observation | supersede, withdraw, rights-block, retention-expire, invalidate | Evidence governance; audit-first; observation/rights/retention apply | active/superseded/withdrawn/blocked/expired/invalid | H1-H5/H8/H9/H12/H13/H15/H19-H22 |
| Evidence identity (`durable` immutable binding) | Evidence-identity transition, `evidence_identity_transition_id`, N:1 evidence | activate, supersede, withdraw, rights-block, retention-expire, invalidate | Evidence identity service/governance; audit-first; evidence retention applies | active/superseded/withdrawn/blocked/expired/invalid | H1-H5/H12/H15-H22 |
| Citation handle (`durable` immutable mapping) | Citation-handle transition, `citation_handle_transition_id`, N:1 handle | activate, deprecate, block | Evidence identity governance; audit-first; retain while permitted references exist | active/deprecated/blocked | H3/H15/H17/H19/H21/H22 |
| Raw manifest (`durable` immutable manifest facts) | Raw-manifest transition, `raw_manifest_transition_id`, N:1 manifest | verify, support, parser-block, purge-due, purge, unavailable, rights-block, retention-expire | Future raw-support/governance path; audit-first; OR-C2 retention | verified/supported/blocked/purge-due/purged/unavailable/expired | H2/H3/H12/H13/H15/H19-H22 |
| Raw payload identity (`durable` immutable binding) | Raw-payload transition, `raw_payload_transition_id`, N:1 payload identity | bind, verify, purge-due, purge, lose-support, invalidate | Future artifact boundary; audit-first; content/manifest retention | bound/verified/purge-due/purged/unavailable/invalid | H2/H3/H12/H15/H19-H22 |
| Opaque artifact token (`durable` immutable token) | Opaque-token transition, `opaque_token_transition_id`, N:1 token | activate, mark-missing, purge, invalidate | Future artifact boundary; audit-first; no longer than manifest permission | active/missing/purged/invalid | H3/H12/H15/H17-H22 |
| Shape fingerprint (`append_only` observed fact) | Shape-recognition transition, `shape_recognition_transition_id`, N:1 fingerprint | recognize, review, mark-breaking, accept-change, retire | Parser/drift governance; audit-first; retain with supported evidence | observed/recognized/review/unknown/breaking/accepted/retired | H12/H13/H19/H21/H22 |
| Parser implementation reference (`external` base reference) | Parser-support transition, `parser_support_transition_id`, N:1 parser reference | support, block, retire, supersede | Implementation release/governance; audit-first; retain while referenced | active/supported/blocked/retired/superseded | H12/H13/H19/H21/H22 |
| Freshness assignment (`durable` immutable assignment) | Freshness-assignment transition, `freshness_assignment_transition_id`, N:1 assignment | activate, supersede, revoke, expire | Freshness governance; audit-first; retain while evidence policy resolution needs it | effective assignment/unknown/blocked | H3/H9/H15/H19/H21/H22 |
| Volatility assignment (`durable` immutable assignment) | Volatility-assignment transition, `volatility_assignment_transition_id`, N:1 assignment | activate, supersede, revoke, expire | Volatility governance; audit-first; retain while evidence policy resolution needs it | effective assignment/unknown/blocked | H3/H9/H10/H15/H19/H21/H22 |

## Concept bindings, relationships, authority, exposure, and failure behavior

The following table completes the applicable dossier fields for every concept group.
Group membership does not change the singular class in the register above.

| Concepts | Provenance; scope/rights/retention binding | Logical relationships/cardinality | Write authority | Read exposure and restrictions | Deletion/support-loss; fail-closed; hammers; forbidden uses |
|---|---|---|---|---|---|
| Scope and governed vocabularies/assignments | Accepted decision/contract basis; assignments are scope-independent governance but targets are scope-bound where applicable | One vocabulary version to many assignments; one target has one effective assignment per governed dimension | Governance administration only | Specialized governed reads; ordinary reads receive bounded labels, not bases containing sensitive content | Retire/supersede, never erase used history; unknown blocks; H1-H5/H19/H21; no customer identity or strategy in labels/bases |
| Query panel and panel run | Panel purpose/version, scope, source, rights, retention; run binds exact version | One panel to many versions; one version to many items/runs; one run to zero or one CapturePackage; a package for a panel run binds exactly one run | Panel governance; later capture path may append runs | Typed reads may expose measurement context/blind spots; ordinary reads cannot mutate or treat panel as evidence | Retired versions remain historical; missing binding blocks admission; H1-H6/H9-H11/H14/H20/H21; no strategy, scheduler, or implicit spend |
| CapturePackage and capture event/attempt | Authority, scope, panel/run, instrument, method, intent, rights, retention, budget/time | Scope 1:N packages; run 0:1 package; package 1:N capture events identified by `capture_id`; capture 0:1 provider job | Capture admission/preflight; later runner appends capture facts/transitions | Internal governed/operational reads; typed evidence may expose safe capture context only | No deletion outside governed retention; invalid package blocks all downstream records; H1-H7/H13/H14/H18/H20/H21; no payload dump/action plan |
| Provider identity/testimony/cross-check | Provider/instrument/version, endpoint/surface, capture, times, methodology | Provider 1:N testimony; capture 0:N testimony; cross-check consumes 2:N testimony without owning them | Governance admits provider; ingestion appends testimony; read layer derives comparison | Provider attribution/caveats inseparable; ordinary typed reads allowed only when rights/status permit; no proprietary truth | Testimony withdrawal/status via transitions; disagreement never deleted because never stored; H2/H3/H7-H10/H13/H15/H19-H21; no winner/average/consensus |
| Candidate, observation, admission, evidence, handles | Package/capture/parser/manual path/source/scope/rights/retention/time | Capture 0:N candidates; candidate 0:1 admitted observation; admission decision exactly one candidate; observation 1:N evidence bindings only for bounded bundles; citation N:1 evidence | Extraction creates candidate; admission authority appends decision/observation; evidence service mints IDs; consumer owns report reference | Candidate internal only; active evidence in ordinary typed reads; internal handle internal only; report-safe reference only through consumer-owned map | Rejected/expired candidates purge per retention; observations/history preserved while current use blocks; H1-H6/H9/H12/H15-H21; candidate cannot be cited or hide raw/rejected evidence/strategy |
| Raw manifest, identity, pointer, content, fingerprint, parser, drift, support transitions | Source family, package/capture, hash/media/bytes, rights/retention, parser/fingerprint provenance | Capture/testimony 0:N manifests; manifest exactly one raw payload identity when support exists; manifest 0:1 opaque token; payload 0:1 governed content; manifest 1:N fingerprints/support transitions; drift links prior/new fingerprints | Future bounded raw-support path; parser repo owns implementation; drift detector/reviewer append events | Ordinary typed reads: safe status/hash/caveat only when allowed; specialized governed reads: manifest/fingerprint; token/locator/bytes never exposed | Purge content, retain only permitted manifest/history; missing/hash mismatch/unknown parser/breaking shape blocks support/admission; H2/H3/H12/H13/H15/H17-H22; no direct locator, secret, relational bytes, or hidden cache |
| Rights concepts | Decision/terms/review basis and target identity; target remains scope/source bound | Vocabulary 1:N assignments; target 1:N historical assignments, exactly one effective compatible state | Rights governance only; transitions audit-first | Ordinary reads receive current class/warning; full basis/history specialized | Expiry/revocation blocks capture/admission/read; history retained only as permitted; H2/H3/H11/H12/H19/H21; no stale/unknown rights treated as permission |
| Retention concepts | Source-family ruling/decision basis, target, deadline/posture | Vocabulary 1:N assignments; target 1:N history; one effective state; purge transition references assignment/target | Retention governance and authorized purge path | Ordinary reads receive current support/use status; deadlines/history specialized | Expiry blocks use and triggers authorized purge posture, not silent deletion; H2/H3/H12/H19/H21/H22; no retention extension by scope or freshness |
| Freshness/volatility concepts | Trusted capture/provider time, policy versions/assignments, exact claim intent | Policy 1:N assignments; evidence/family 0:N assignments over time; derived values depend on evidence and read time | Governance writes versions/assignments; read layer derives current values | Ordinary typed reads must expose age/status/warnings; no detached caveats; never stored conclusion | Missing time/policy/context blocks or downgrades; H3/H8-H10/H15-H17; no recapture task, priority, or score persistence |
| Audit and security logs | Actor/caller class, action/result, target, authority, time; security excludes credentials/private payload | Consequential transition exactly 1 required audit event in same transaction; request 0:N security events; ordinary successful read creates no evidence event | Audit subsystem/security boundary only | Audit operational-only; security logs security-only; excluded from ordinary evidence reads | Retention-governed purge with required proof; missing audit rolls back change; unauthorized log access blocks/logs; H1/H3/H17-H22; no customer tracking or LLM reasoning |
| Overlays | Consumer-supplied type/freshness within request; no durable scope/rights assignment because persistence forbidden | Request 0:N overlay values; no relationship survives request; may align read-time with evidence | Supplying consumer/request parser only; no Observatory writer | Request-local derived alignment only; values, hashes, inventory, references, or summaries never logged/exposed outside response contract | Discard at request end; missing authorization/freshness blocks comparison; H3/H4/H16-H18; no evidence/capture/raw/citation/scope identity |
| Forbidden interpretation/workflow concepts | External consumer authority only | No Observatory relationships | No Observatory writer | Never exposed from Observatory storage because must not exist | Reject and audit/security-log only bounded violation metadata; H4/H5/H8/H10/H16-H18/H21; no aliases or fake-mustache variants |

## Source-family raw posture

The accepted OR-C2 defaults remain exactly:

| Family | Default |
|---|---|
| Controlled provider API payload | `capture_and_purge_raw` |
| Public manual observation | `retain_manifest_only` |
| Public page snapshot | `no_raw_storage` |
| AI/GEO answer surface | `no_raw_storage` |
| Marketplace surface | `no_raw_storage` |
| Video/YouTube surface | `no_raw_storage` |
| Customer first-party / owned telemetry overlay | `forbidden_no_capture` |
| Unknown or missing family | `forbidden_no_capture` |

These are postures, not capture or persistence authority. `external` applies only to
consumer/provider-owned content. Conditionally retained Observatory artifact content
is `durable` but presently unauthorized. Raw bytes in ordinary relational evidence
storage are `forbidden`.

## Forbidden-persistence register

| Forbidden item | Authority / prohibition | Fail-closed behavior | Hammer | Allowed bounded alternative |
|---|---|---|---|---|
| Strategy, recommendations, action plans, opportunity/tactic verdicts | Boundaries; V6/V20/V21 | Reject storage; do not preserve offending meaning in logs | H5/H18/H21 | Compute at read time; promote to owning consumer |
| Conclusions, report narrative/state/delivery, accepted decisions | Boundaries; consumer contract | Reject Observatory persistence | H4/H5/H16 | Consumer-owned artifact/workflow |
| LLM reasoning, chain-of-thought, prompts/session memory as evidence | Boundaries | Reject/log only bounded violation class | H5/H17/H18 | Ephemeral model processing outside evidence |
| Scores-as-truth, provider winner/average/consensus | Provider and M16 rulings | Block derived truth/winner output | H8-H10 | Attributed side-by-side testimony |
| Hidden customer profiles/records/private or first-party data | Boundaries; M17 | Reject, do not hash/cache/log values | H1/H4/H16-H18 | Ephemeral authorized overlay only |
| Provider claims treated as web truth or resolved disagreement | Provider contracts; OR-A1 | Require attribution; block truth resolution | H8/H9/H15 | Derived comparison with caveats |
| Unrestricted relational raw payload bytes / hidden raw caches | OR-C2/OR-C4 | Block admission; purge only under authorized path | H2/H3/H12/H18/H21 | Manifest plus opaque token; conditional governed content only after gate |
| Credentials, secrets, connection strings | Access boundary | Reject and security-handle without echo | H17/H18 | Managed secret boundary outside evidence |
| Paths, bucket keys, URIs, underlying locators in typed reads | OR-D2/OR-C4 | Block/redact entire unsafe result | H12/H15/H17/H18 | Internal opaque non-resolving token, not exposed |
| Unrestricted rejected evidence/candidate graveyard | Candidate contract | Apply retention; never cite/expose | H3/H5/H6/H15 | Bounded candidate plus rejection transition/reason class |
| Unsupported/blocked citation target | Evidence contract | Return uniform blocked/not-found behavior | H15/H17 | Status-aware internal handle |
| Unresolved/expired rights or retention | Scope contract | Block capture, admission, read, reuse; purge when authorized | H2/H3/H12/H21 | Explicit governed reassignment/transition |
| Data retained past authorized posture | Retention contract | Block use; require authorized purge and audit | H3/H12/H19/H21/H22 | Permitted manifest/history only |
| Cross-scope materialization/customer-derived aggregates | Boundaries; OR-G1 | Block by default | H1/H4/H16 | Separately ruled governed exception only |

## Fail-closed register

| Condition / detection source | Blocked operation | Safe output | Required event/log | Recovery transition | Hammers |
|---|---|---|---|---|---|
| Missing/invalid scope or cross-scope grant | Capture, admission, read | Uniform blocked/not-found | Audit for consequential attempt; security log for access attempt | Governed scope/grant correction | H1/H4/H16/H17 |
| Missing/unknown/expired rights | Capture, admission, current read/reuse | Rights-blocked status without sensitive basis | Audit; security log if access-related | New governed assignment/transition | H2/H11/H12/H21 |
| Missing/unknown/expired retention | Capture, admission, current read/retention | Retention-blocked/purged status | Audit; security log if access-related | New assignment or authorized purge transition | H3/H12/H19/H21/H22 |
| Missing evidence identity or identity-layer mismatch | Citation/read/promotion | Uniform invalid/blocked handle | Audit for mint/admission defect; security log enumeration | Correct admission/identity binding, never alias substitution | H15/H17/H18 |
| Missing provenance | Admission/current evidence use | `blocked_missing_provenance` | Audit | New valid observation/correction path | H6/H8/H15/H21 |
| Provider disagreement/incomparability | Winner/consensus/current comparison | Side-by-side caveat or blocked comparison | No evidence mutation; optional security log only for abuse | New comparable evidence; recompute | H8/H9 |
| Unsupported/purged/missing/hash-mismatched raw support | Raw-supported admission/read claim | Safe support status and caveat | Audit support transition | Authorized recapture/new support; never locator exposure | H3/H12/H13/H15/H21/H22 |
| Unknown parser or unrecognized/breaking shape | Parse/admission | Quarantine/block status, no fake values | Drift and audit events | New reviewed parser reference/shape transition | H12/H13/H18/H21/H22 |
| Blocked/deprecated/unresolved citation handle | Active resolution/citation | Uniform blocked/not-found | Security log on enumeration/abuse | Governed handle transition/new handle | H15/H17 |
| Stale/unknown evidence for current claim | Current-state/absence/strong comparison support | Historical-only, warning, or claim block | No evidence event | New authorized evidence; recompute | H9/H10/H15 |
| Unfit claim or missing mandatory caveat | Meaning-bearing support | Evidence-only response with block/warnings | No evidence event | Narrow claim intent or new evidence | H5/H9/H10/H16 |
| Missing ordinary-read authorization | Read | Uniform blocked/not-found | Security/access log | Correct external grant | H1/H17/H18 |
| Unauthorized security-log access | Operational read | Block with no log payload | Security/access event without credentials/private content | Security grant | H1/H3/H17/H18 |
| Incomplete panel/run binding | Capture/admission/comparison | Blocked panel context | Audit for attempted consequential action | New exact run/package binding | H6/H14/H15/H20/H21 |
| Invalid CapturePackage/duplicate/budget/authority state | Attempt/admission/spend | Exact blocked class, no execution | Audit/security as applicable | New authorized immutable package or transition | H2/H3/H6/H7/H18/H20/H21 |
| Audit write failure | Consequential mutation | Whole operation fails | No partial state | Retry only through governed transaction | H19/H20/H21 |
| Overlay authorization/freshness/discard failure | Overlay comparison/output | Block without retaining values | Security log without values | New valid request; discard | H3/H4/H16-H18 |

## Complete H1-H22 audit

All results below are logical `defined_only` mappings, not executed hammer passes.

| Hammer | Applicability and exact concepts/invariants | Expected pass | Expected fail-closed |
|---|---|---|---|
| H1 Scope isolation | Scope, panels/runs, packages, testimony, evidence, assignments, reads/logs | Every target/read binds one authorized scope; no customer identity/cross-scope path | Reject/block uniformly; security log without leakage |
| H2 Rights fail-closed | Source family, package, candidate, observation/evidence, raw, assignments | Effective rights resolved and permitted at capture/admission/use | Block capture/admission/read/raw support |
| H3 Retention enforcement | All durable/append-only data including security logs, raw, candidates, evidence | Effective posture/deadline enforced; permitted history only | Block use; authorized purge plus audit; no over-retention |
| H4 Customer-private rejection | Scope, packages, candidates/raw, overlays, logs, consumer refs | No customer/private content or identity persists | Reject without hashing/logging private value |
| H5 No strategy/recommendation storage | All metadata, panels, candidates, evidence, warnings, audit/logs | Only observations/governance facts persist | Reject interpretive/workflow content |
| H6 CapturePackage validation | Package, panel/run binding, attempts, candidates, admission | Complete immutable envelope precedes attempt/admission | No attempt/evidence; exact block/audit |
| H7 Provider spend/duplicates | Package/authority/budget, attempts, provider jobs | Exact authority/ceiling/recipe/duplicate controls | No request/spend; append blocked attempt where allowed |
| H8 Provider attribution/disagreement | Provider identity/testimony, cross-check, evidence reads | Attribution/caveats inseparable; disagreement derived | Block truth/winner/average/incomparable comparison |
| H9 Freshness/volatility/claim use | Policies/assignments, age/freshness/fitness/warnings | Exact timestamps/context and safe claim disposition | Historical-only/warning/block; no recapture task |
| H10 AI/GEO overclaim | AI testimony/panel context, claim fitness | Sample/time/surface/prompt limits preserved | Block universal trust/visibility/causality claims |
| H11 Marketplace ceiling | Source family/instrument/rights/package/testimony | Exact platform/surface/method admission and bounded caveat | Block capture/admission/report support |
| H12 Raw integrity | Manifest, payload identity/content, pointer, hash, retention, evidence | Permitted manifest/hash/pointer/support consistent | Block admission/support; purge/audit; never expose locator |
| H13 Drift/parser safety | Fingerprint, parser ref, drift/review history, attempts/testimony | Known supported shape/parser with preserved lineage | Quarantine/block, drift/audit transition, no fake values |
| H14 Panel immutability | Panel versions, runs, CapturePackage binding | Used version immutable; run/package binds exact version | Reject mutation/missing version/ambiguous binding |
| H15 Evidence/citation integrity | All identity layers, status transitions, handles/raw context | Distinct stable IDs and status-aware resolution | Reject mismatch/blocked target uniformly |
| H16 Consumer/overlay boundary | Consumer/report refs, overlays, derived warnings/promotion | Overlay discarded; meaning/report state remains consumer-owned | Block persistence/private context/automatic promotion |
| H17 LLM/agent access | Typed reads, handles, raw boundary, security logs | Authorized shaped reads only; no SQL/CRUD/credentials/locators | Block and security-log without leakage |
| H18 Hostile input | All ingestion/read/governance inputs | Bounded validated encoding/size/shape/IDs; no nested forbidden meaning | Reject without persisting unsafe content |
| H19 Append-only behavior | Observations, testimony, transitions, histories, audit/logs | Immutable facts; changes append; current state derived | Reject overwrite/backdate/delete outside governance |
| H20 Concurrency | Runs/packages/attempts/admission/assignments/purge/audit | One logical outcome; no duplicate spend/admission or forked version | Roll back/block conflicting operation |
| H21 Audit-first | Admission/rejection metadata, rights/retention, support/purge, supersession/withdrawal | Required audit event in same consequential transaction | Entire change rolls back; ordinary reads create no evidence event |
| H22 Migration/recovery implications | Every durable/append-only identity/history/raw/audit invariant | Future migration/restore preserves identity, hash, history, scope, state derivability | Future migration/restore gate blocks on any discontinuity |

No missing DB-2 definition remains for H1-H22. Execution, database mechanisms, and
proof classes above `defined_only` belong to later, separately authorized gates.

## Correction dispositions C-01 through C-12

| ID | Final disposition | Applied resolution |
|---|---|---|
| C-01 | accept | Source family is `versioned`; governed is a qualifier |
| C-02 | accept with restrictions | Candidate is `durable`, non-evidence/non-citable/retention-gated and cannot hide raw, strategy, or rejected evidence |
| C-03 | revise | Manifest is `durable` immutable facts; support/purge/parser/review changes are separate `append_only` transitions; current state derived |
| C-04 | accept | Opaque pointer token is `durable`, internal-only, and explicitly not an underlying locator |
| C-05 | revise | Conditional Observatory artifact content is `durable`; consumer-owned content is `external`; relational bytes are `forbidden` |
| C-06 | revise | Fingerprint facts are `append_only`; recognition/review transitions are separate; current state derived |
| C-07 | accept | Parser implementation reference is `external` with versioned-reference qualifier |
| C-08 | revise | Rights vocabulary, assignment, history, and derived effective state are four concepts covering all applicable targets |
| C-09 | revise | Retention vocabulary, assignment, deadline/posture, history, and derived effective state are separate concepts |
| C-10 | accept | Audit event is `append_only`; `audit_first` is a qualifier |
| C-11 | accept with completion | Security log is `append_only`, operationally separate, retention-gated, security-only; H3 applies |
| C-12 | accept | Citation lifecycle/read state is active/deprecated/blocked; unresolved references fail closed to blocked |

## Exact candidate and owner gate

Candidate under review:

```text
file: planning-inbox/db2-physical-data-contract-freeze-specification.md
version: 0.2.1
status: candidate; not accepted
```

The fresh readiness review records the candidate SHA-256 after this file is finalized.
Only the owner may answer these three independent questions:

1. Accept or reject the exact DB-2 freeze candidate identified by file, version, and SHA-256.
2. Close or continue DB-2.
3. Authorize or refuse preparation of fresh DB-3 planning.

Acceptance of the freeze does not automatically close DB-2 or activate DB-3. None
of those decisions authorize DB-4, PostgreSQL, schemas, SQL/DDL, migrations,
database tools, implementation, persistence, providers, capture, customer data,
raw storage, recurring work, or production.

Proposed owner gate (not answered here):

```text
DECISION 1 - DB-2 FREEZE
ACCEPT OR REJECT THE EXACT CANDIDATE:
planning-inbox/db2-physical-data-contract-freeze-specification.md
VERSION 0.2.1, SHA-256 AS RECORDED IN THE FRESH READINESS REVIEW.

DECISION 2 - DB-2 MILESTONE
CLOSE OR CONTINUE DB-2.

DECISION 3 - FUTURE DB-3 PLANNING
AUTHORIZE OR REFUSE PREPARATION OF FRESH DB-3 PLANNING.

NO DECISION ABOVE AUTHORIZES POSTGRESQL, DATABASES, ROLES, CREDENTIALS,
SCHEMA, SQL/DDL, MIGRATIONS, DATABASE TOOLS, IMPLEMENTATION, PERSISTENCE,
PROVIDERS, CAPTURE, CUSTOMER DATA, RAW STORAGE, DB-4, OR PRODUCTION.
```

## Final rule

Freeze what the telescope may remember. Keep changing state in explicit history,
derive current state, and keep the astronomer's meaning outside Observatory.
