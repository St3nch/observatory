# DB-2 Classification-Correction Disposition Record

Status: historical correction-disposition record; not authority
Date: 2026-07-13
Canonical candidate: `planning-inbox/db2-physical-data-contract-freeze-specification.md`
Recovery authority: `decisions/2026-07-13-database-phase-recovery-to-db1.md`

## Purpose

Preserve the disposition of the twelve v0.1.1 correction findings without acting as
a competing freeze, stale acceptance gate, or claim that DB-2 is closed. Candidate
Candidate v0.2.1 preserves each defensible C-01 through C-12 result while correcting
the separate conflicts found by independent review of rejected candidate v0.2.0.

## Edit classification

```text
roadmap edit class: clarification
scope change: no
doctrine change: no
new persistence authority: no
physical design authority: no
implementation authority: no
```

## Final dispositions

| ID | Topic | Disposition | Incorporated v0.2.1 rule |
|---|---|---|---|
| C-01 | Source family | accept | `versioned`; `governed` is a qualifier |
| C-02 | Candidate observation | accept with restrictions | `durable`, non-evidence, non-citable, retention-gated; cannot hide raw, strategy, or rejected evidence |
| C-03 | Raw manifest | revise | Manifest facts are `durable`; support/purge/parser/review changes are separate `append_only` transitions; current state is derived |
| C-04 | Opaque artifact pointer | accept | `durable`, internal-only opaque token; never an underlying path/key/URI/credential |
| C-05 | Raw payload bytes | revise | Conditionally governed Observatory artifact content is `durable` but unauthorized; consumer-owned content is `external`; relational raw bytes are `forbidden` |
| C-06 | Shape fingerprint | revise | Observed fingerprints are `append_only`; recognition/review/break/retire transitions are separate; current recognition is derived |
| C-07 | Parser version | accept | `external` versioned implementation reference; source/releases do not become evidence data |
| C-08 | Rights | revise | Versioned vocabulary, durable assignment, append-only assignment history, and derived effective state; targets are not limited to source family |
| C-09 | Retention | revise | Versioned vocabulary, durable assignment/deadline posture, append-only history, and derived effective state across all applicable targets |
| C-10 | Audit event | accept | `append_only`; `audit_first` is a qualifier |
| C-11 | Security/access log | accept with completion | `append_only`, operationally separate, retention-gated, security-only; H3 applies; ordinary evidence reads exclude it |
| C-12 | Citation-handle lifecycle | accept | `active / deprecated / blocked`; unresolved references fail closed to blocked |

## Superseded proposals

The former v0.1.1 acceptance/DB-2 closure/DB-3 activation phrase is obsolete and
must not be used. Candidate v0.2.0 and its readiness review failed independent
steward review and are not current review targets. The only current owner gate is
the three-decision gate in candidate v0.2.1 and its fresh readiness review.
Historical DB-2 reviews remain historical.

## Independent-review corrections beyond C-01 through C-12

| Finding | v0.2.1 disposition |
|---|---|
| Capture identity conflict | `capture_package_id` remains the package identity; accepted `capture_id` identifies the capture event/attempt; `capture_attempt_id` is an inactive `unresolved` rename/alias proposal that fails closed pending owner ruling |
| Accepted-concept omissions | Observed artifact, validation/rejection, freshness inputs/results, claim inputs/intents/results/warnings, and consumer-promotion concepts now have explicit dossiers |
| Lifecycle underspecification | Named append-only transition concepts, identifiers, target relations, event vocabularies, authorities, audit/retention rules, derived states, and hammer mappings are explicit |
| Roadmap duplication | Duplicate current-review-target block removed; one v0.2.1 block remains |
| Authority guard weakness | Checker uses exact status classes, exact version/hash, capture-identity assertions, concept assertions, duplicate-block guard, and rejected-review absence guard |

## Preserved non-authorizations

No disposition here authorizes PostgreSQL, roles, credentials, physical schema,
SQL/DDL, migrations, database tools, persistence, artifact storage, providers,
capture, customer/private data, production, DB-2 closure, or DB-3 activation.

## Final rule

One concept, one primary classification. Facts, transitions, and current derived
state stay separate. A correction record does not accept its target candidate.
