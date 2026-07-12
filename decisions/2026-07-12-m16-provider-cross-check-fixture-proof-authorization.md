# Decision — M16 Provider Cross-Check Fixture-Backed Proof Authorization

Status: accepted
Date: 2026-07-12
Milestone: M16 — Provider Cross-Check Proof

## Decision

Authorize exactly the bounded implementation task in:

```text
planning-inbox/m16-provider-cross-check-fixture-proof-task-proposal.md
```

The authorization is limited to one synthetic, local, deterministic, in-memory provider cross-check proof.

## Allowed

- `src/observatory_provider_cross_check/`
- the six named M16 test files
- the named result register and local-test/closure-review evidence files
- pure comparison, comparability, disagreement, serialization, and closed validation behavior
- committed synthetic fixtures and already committed sanitized structural testimony only

## Required behavior

- preserve provider attribution and per-side evidence state;
- represent disagreement without selecting truth;
- fail closed on missing context, rights/retention, source admission, drift, cross-scope access, and forbidden output requests;
- preserve time-distance and freshness warnings;
- never produce a winner, average, consensus, trust score, or composite;
- remain compute-on-read with no persistence.

## Not authorized

```text
provider calls or purchases
DataForSEO requests
Ahrefs or Semrush execution
credentials
recurring capture
persistent Disagreement Ledger
truth/winner/average/consensus/composite logic
customer data or overlays
report generation
Postgres
schema or migrations
production API/MCP
production integration
```

## Proof status

Implementation does not establish a test pass. Owner-local execution of the complete test suite remains required before proof acceptance or M16 closure.
