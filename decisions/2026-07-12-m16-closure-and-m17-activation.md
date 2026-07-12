# Decision — Close M16 and Activate M17 Planning

Status: accepted
Date: 2026-07-12
Milestones: M16 → M17

## Decision

Close M16 — Provider Cross-Check Proof and activate M17 — Owned Telemetry Overlay Proof for planning only.

## Accepted M16 evidence

- accepted provider cross-check proof contract and owner rulings;
- authorized local synthetic fixture-backed implementation;
- implementation commit `0e8421d924c8dce33f538e065bcdfd25af77f419`;
- owner-local full-suite result: 167 tests passed;
- closure-readiness review at `planning-inbox/m16-provider-cross-check-closure-readiness-review.md`.

The accepted proof demonstrates within its bounded local in-memory surface that provider disagreement remains attributed evidence, comparability fails closed, caveats remain visible, cross-scope mixing is blocked, and no truth, winner, average, consensus, composite, recommendation, or persistence behavior is produced.

## Proof ceiling

M16 did not prove or authorize live provider comparisons, purchases, credentials, recurring capture, persistent disagreement storage, customer-facing report language, database enforcement, production API/MCP behavior, integration, or deployment.

## M17 activation boundary

M17 is active for planning only. It may reconcile the accepted overlay, scope-rights-retention, claim-safety, typed-read, SearchClarity, and no-persistence boundaries; define ephemeral overlay input and alignment behavior; define hostile-path tests; and propose one exact bounded synthetic proof task.

M17 does not authorize:

```text
real customer first-party analytics
owned/private telemetry intake
screenshots, CSVs, PDFs, exports, or external files
customer identity or account records
overlay persistence, caching, logging, or evidence promotion
private analytics ingestion as canonical Observatory data
production SearchClarity, Neon Ronin, or Kaizen integration
provider calls or recurring capture
Postgres, schema, or migrations
production API/MCP
report generation or delivery
strategy, recommendation, or conclusion storage
```

## Next step

Produce the M17 planning package from live repo authority before any proof implementation.
