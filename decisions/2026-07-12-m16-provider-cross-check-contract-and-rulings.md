# Decision - M16 Provider Cross-Check Contract and Rulings

Status: accepted decision
Authority: owner-approved M16 contract and ruling decision
Date: 2026-07-12
Milestone: M16 - Provider Cross-Check Proof

---

## Decision

Accept `contracts/provider-cross-check-proof-v0-1.md` as the binding M16 provider cross-check proof contract within its declared scope.

Accept the following rulings:

### OR-A1 - Compute-on-read disagreement only

M16 disagreement output is computed at read time.

No persistent Disagreement Ledger, comparison table, summary cache, materialized disagreement record, or durable provider-comparison score is admitted.

Any later persistence proposal requires the V6 materialization test, explicit owner ruling, schema authority, rights/retention review, and proof that persistence adds value beyond deterministic recomputation.

### M16-R1 - Comparability threshold

Strong comparison requires alignment of subject, metric family, scope, surface, and material context dimensions.

Missing or materially mismatched dimensions downgrade to `partially_comparable`, `unresolved_incomparability`, or a blocked disposition.

Same-looking labels are not sufficient.

### M16-R2 - Proprietary metrics

Cross-provider proprietary scores are incomparable by default when definitions or scales are unknown.

Values may appear side by side as provider-attributed testimony, but M16 must not calculate differences as though unknown scales were equivalent.

### M16-R3 - Time-distance and freshness

Each provider side retains its own `captured_at`, provider-reported time, freshness, and volatility state.

Non-synchronous evidence requires deterministic warning behavior. Material time separation downgrades or blocks current-state comparison.

M16 does not invent a universal production time threshold.

### M16-R4 - No truth or consensus derivation

M16 produces no truth value, winner provider, average, consensus, blended metric, trust score, or composite score.

Majority-vote and closest-to-average adjudication are forbidden.

### M16-R5 - No ground-truth adjudication

M16 does not implement ground-truth adjudication.

Future verified external evidence may be admitted only as another governed evidence source under separate methodology, source-admission, and owner decisions.

### M16-R6 - Provider profile notes

Provider profile or methodology notes are allowed only as cited, versioned, caveated metadata.

They may explain coverage, source/index boundaries, update cadence, or known method limits. They may not rank quality, predict accuracy, crown a provider, or recommend a purchase.

### M16-R7 - Cross-scope comparison blocked

Cross-scope provider comparisons remain blocked.

The first bounded proof must use isolated synthetic scopes and reject attempts to combine them.

### M16-R8 - Bounded proof eligibility only

M16 is eligible for one exact local fixture-backed proof after separate authorization.

The eligible proof must remain local-only, in-memory, deterministic, no-network, no-provider-call, no-credential, no-purchase, no-customer-data, no-overlay, no-report, no-database, no-persistence, and no-production-integration.

This decision does not authorize implementation.

---

## Accepted contract

```text
contracts/provider-cross-check-proof-v0-1.md
```

The contract is accepted only within its declared proof and planning scope.

---

## Explicit non-authorizations

This decision does not authorize:

```text
M16 proof implementation
live provider calls
DataForSEO requests
Ahrefs or Semrush purchases or credentials
recurring cross-provider capture
persistent Disagreement Ledger
truth-provider logic
provider winner logic
averaged or blended metrics
consensus or composite scores
ground-truth adjudication
customer data
customer reports
real overlays
Postgres
schema or migrations
production API/MCP
production integrations
strategy or recommendation storage
```

---

## Next gate

The next gate is separate exact authorization of:

```text
planning-inbox/m16-provider-cross-check-fixture-proof-task-proposal.md
```

No implementation authority is inferred from this decision.
