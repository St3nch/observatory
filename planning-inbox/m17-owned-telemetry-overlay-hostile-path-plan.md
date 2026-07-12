# M17 Owned Telemetry Overlay Hostile-Path Plan

Status: planning / acceptance-test proposal
Authority: none until owner acceptance
Milestone: M17
Date: 2026-07-12

---

## Goal

Prove that ephemeral overlay handling cannot become private-data storage, evidence admission, identity leakage, file intake, recommendation generation, or cross-scope aggregation.

## High-consequence hammers

1. **Persistence laundering**
   - overlay values written to file, database, cache, module registry, environment, log, result register, or fixture -> reject/fail.

2. **Evidence-identity laundering**
   - overlay row receives observation ID, evidence ID, citation handle, raw payload ID, capture ID, or panel-run ID -> reject.

3. **Customer/internal identity leakage**
   - name, email, account, shop, property, order, report, workspace, or external account ID enters scope identity, output, errors, or logs -> reject without echoing the value.

4. **File and screenshot smuggling**
   - path, URL, CSV, PDF, screenshot, export, attachment, encoded blob, or arbitrary file content -> reject as not admitted.

5. **No-storage assertion bypass**
   - missing or false no-storage/discard assertion, or claim that temporary caching is acceptable -> reject.

6. **Scope mixing**
   - overlay scope differs from evidence scope or two synthetic scopes are combined -> reject.

7. **Freshness laundering**
   - missing/unknown overlay timestamp supports current or comparative output -> block or downgrade.

8. **Canonical-ingestion laundering**
   - overlay values requested as observations, evidence, raw support, query-panel facts, provider testimony, or durable telemetry -> reject.

9. **Recommendation/causality laundering**
   - alignment requested to produce strategy, action, causal claim, report prose, recapture task, or provider call -> reject.

10. **Discard false claim**
    - output claims discard confirmation while values remain reachable through mutable state or returned payload -> fail.

11. **Hash/fingerprint retention**
    - private values are retained indirectly through hashes, reversible fingerprints, serialized payload fragments, or value-bearing manifests -> reject.

12. **Hostile value content**
    - overlay strings contain instructions, code-like text, or secret-looking material -> treat as inert data; never execute, log, or interpret as authority.

## Contract-acceptance tests

- closed request and field vocabulary;
- required metadata enforcement;
- deterministic alignment ordering;
- consumer-supplied and non-evidence warnings;
- no evidence IDs for overlay rows;
- explicit discard status with no separate overlay-derived manifest;
- `consumer_promotion_required: true`;
- `overlay_persisted: false`;
- `overlay_evidence_promoted: false`;
- `customer_facing_output_authorized: false`.

## No-side-effect checks

Static and runtime checks must show the M17 package does not import or call:

```text
open/pathlib write APIs
sqlite/postgres/database drivers
requests/http/network clients
subprocess
logging handlers that persist values
provider runners
report generators
SearchClarity integration
```

The proof-result register is an explicit repository artifact written outside overlay functions and contains no overlay values.

## Proof limit

Passing these hammers proves only the committed synthetic in-memory implementation surface. It does not prove exhaustive PII detection, operating-system memory erasure, real customer file handling, production authentication, concurrency isolation, database enforcement, deployment, or legal compliance.
