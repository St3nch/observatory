# DB-2 Physical Data-Contract Freeze v0.1.1 Classification Corrections

Status: accepted DB-2 clarification
Date: 2026-07-13
Canonical freeze: `planning-inbox/db2-physical-data-contract-freeze-specification.md`
Accepted by: `decisions/2026-07-13-db2-closure-and-db3-activation.md`

## Purpose

Correct classification-shape inconsistencies discovered during DB-2 reconciliation without changing project scope, admitting new persistence, or beginning physical design.

The accepted freeze requires every concept to receive exactly one primary classification from:

```text
durable
append_only
versioned
derived
ephemeral
external
forbidden
unresolved
```

Several entries currently combine a primary classification with descriptive qualifiers or combine two separately governed concepts in one line. This proposal normalizes those entries so DB-3 receives an unambiguous logical contract.

## Correction class

```text
roadmap edit class: clarification
scope change: no
doctrine change: no
new persistence authority: no
physical design authority: no
```

## Proposed corrections

### C-01 Source family

Current:

```text
classification: versioned vocabulary
```

Corrected:

```text
classification: versioned
qualifier: governed vocabulary
```

### C-02 Candidate observation

Current:

```text
classification: durable but non-evidence, retention-bounded
```

Corrected:

```text
classification: durable
qualifiers: non-evidence; retention_gated
```

This does not require candidate persistence in every implementation. It states only that, when the accepted contract permits candidate records, their canonical logical classification is durable and retention-bounded rather than evidence.

### C-03 Raw manifest

Current:

```text
classification: durable or append_only metadata, source-family gated
```

Corrected:

```text
classification: append_only
qualifiers: source_family_gated; rights_gated; retention_gated
```

Raw-support status changes must preserve history rather than silently overwrite the manifest's prior support state.

### C-04 Opaque artifact pointer

Current:

```text
classification: durable internal locator
```

Corrected:

```text
classification: durable
qualifier: internal opaque locator
```

### C-05 Raw payload bytes

Current:

```text
classification: external artifact, source-family gated
```

Corrected:

```text
classification: external
qualifiers: source_family_gated; rights_gated; retention_gated
```

Raw bytes remain outside ordinary relational evidence records.

### C-06 Shape fingerprint

Current:

```text
classification: append_only metadata
```

Corrected:

```text
classification: append_only
qualifier: shape metadata
```

### C-07 Parser version

Current:

```text
classification: versioned external implementation reference
```

Corrected:

```text
classification: external
qualifier: versioned implementation reference
```

The implementation repository owns parser source and release identity. Observatory may retain a bounded reference but does not own parser source code as database content.

### C-08 Rights vocabulary and assignment

Current combines two concepts:

```text
classification: versioned vocabulary plus append_only assignment history
```

Corrected split:

```text
rights vocabulary
classification: versioned
qualifier: governed vocabulary

rights assignment history
classification: append_only
qualifiers: audit_first; source_family_gated
```

### C-09 Retention vocabulary and assignment

Current combines two concepts:

```text
classification: versioned vocabulary plus append_only assignment history
```

Corrected split:

```text
retention vocabulary
classification: versioned
qualifier: governed vocabulary

retention assignment history
classification: append_only
qualifiers: audit_first; source_family_gated
```

### C-10 Audit event

Current:

```text
classification: append_only, audit_first
```

Corrected:

```text
classification: append_only
qualifier: audit_first
```

### C-11 Security/access log

Current:

```text
classification: append_only operational record, separate from evidence corpus
```

Corrected:

```text
classification: append_only
qualifiers: operational record; separate from evidence corpus; retention_gated
```

### C-12 Internal citation handle lifecycle

Current lifecycle includes `unresolved`, which is a freeze classification rather than a useful handle lifecycle state:

```text
lifecycle: active / deprecated / unresolved
```

Corrected:

```text
lifecycle: active / deprecated / blocked
```

An unresolved design question fails closed to `blocked`; it does not become a durable lifecycle state.

## Classification register after correction

| Concept | Primary classification |
|---|---|
| Scope | durable |
| External consumer reference | external |
| Source family | versioned |
| Provider/capture instrument | versioned |
| Query panel definition | versioned |
| CapturePackage | append_only |
| Capture attempt | append_only |
| Provider job ID | external |
| Candidate observation | durable |
| Admitted observation | append_only |
| Evidence identity | durable |
| Internal citation handle | durable |
| Report-safe reference | external |
| Raw manifest | append_only |
| Opaque artifact pointer | durable |
| Raw payload bytes | external |
| Shape fingerprint | append_only |
| Parser version | external |
| Provider drift event | append_only |
| Rights vocabulary | versioned |
| Rights assignment history | append_only |
| Retention vocabulary | versioned |
| Retention assignment history | append_only |
| Freshness/volatility current status | derived |
| Provider disagreement | derived |
| Claim-use/evidence-pack warnings | derived |
| Audit event | append_only |
| Security/access log | append_only |
| Customer/owned first-party overlay | ephemeral |
| Strategy/recommendation/conclusion/report state | forbidden |

No concept remains primarily `unresolved`. Open capability questions remain fail-closed outside the freeze and require separate decisions.

## Preserved boundaries

These corrections do not authorize:

```text
PostgreSQL creation
roles or credentials
tables, columns, indexes, constraints, triggers, functions, or SQL
migration files or execution
disposable databases or real PostgreSQL hammers
synthetic or real persistence
provider calls, paid pulls, or ingestion
raw capture or artifact-store creation
customer/private data
production API/MCP
strategy, recommendation, conclusion, or report-state persistence
DB-3 activation
```

## Exact owner gate candidate

```text
ACCEPT DB-2 PHYSICAL DATA-CONTRACT FREEZE v0.1.1 CLASSIFICATION CORRECTIONS

CLOSE DB-2 — PHYSICAL DATA-CONTRACT FREEZE

ACTIVATE DB-3 — POSTGRES OPERATIONAL BOUNDARY AND PHYSICAL SCHEMA SPECIFICATION

AUTHORIZE SPECIFICATION WORK ONLY.
DO NOT AUTHORIZE DATABASE CREATION, ROLES, CREDENTIALS, DDL,
MIGRATION FILES, MIGRATION EXECUTION, DISPOSABLE DATABASES,
POSTGRES HAMMERS, SYNTHETIC OR REAL PERSISTENCE, PROVIDER CALLS,
CUSTOMER DATA, RAW CAPTURE, OR PRODUCTION.
```

This phrase is a proposal until explicitly accepted by the owner and recorded in `decisions/`.

## Final rule

```text
One concept, one primary classification.
Qualifiers may sharpen behavior but must never blur authority.
```
