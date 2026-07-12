# Decision — M14 Closure and M15 Planning Activation

Status: accepted
Date: 2026-07-12
Decision class: milestone closure / next-boundary activation
Owner authorization: owner instructed project steward to proceed after M14 closure readiness was verified and pushed

---

## Decision

Close:

```text
M14 — Typed Read API / MCP Contract and Prototype
```

Activate for planning only:

```text
M15 — SearchClarity Proof Workflow
```

---

## M14 Closure Basis

M14 is closed on the following bounded evidence:

- accepted M14 typed-read contract v0.1;
- resolved RG3/RG8 Hermes research-lineage input;
- authorized fixture-backed local prototype;
- implementation commit `5421c2d18417beaf6513b7b48a16a7531de0b023`;
- owner-local full-suite result: `Ran 141 tests in 0.157s` / `OK`;
- machine-readable result register with honest proof classification;
- closure-readiness review preserving substrate limitations;
- clean and synced repository after proof commit `14d230083cb48652f78b2dd66b4bf7b106e07566`.

M14 proves bounded typed-read contract behavior on a local fixture-backed in-memory execution surface.

M14 does not prove:

```text
database enforcement
transaction behavior
concurrency behavior
production authentication
network API behavior
real MCP behavior
deployment security
customer-data handling
overlay handling
production pagination/rate limiting
```

Those limitations remain explicit and are not closure blockers because they were outside the authorized M14 prototype boundary.

---

## M14 Outputs Accepted for Downstream Planning

- `contracts/typed-read-api-mcp-v0-1.md`
- `src/observatory_typed_read_prototype/`
- `test-results/m14-typed-read-result-register.json`
- `planning-inbox/m14-hermes-lineage-review-2026-07-12.md`
- `planning-inbox/m14-fixture-read-prototype-closure-readiness-review.md`

The prototype remains proof code, not production infrastructure.

---

## M15 Active Boundary

M15 may now plan and define how SearchClarity can consume Observatory evidence without turning Observatory into a customer database, report system, CRM, strategy engine, or workflow store.

Allowed M15 planning work:

- reconcile the accepted SearchClarity consumer placeholder with the accepted typed-read contract;
- define an evidence-pack-to-report-support workflow;
- define claim-safety use at the consumer boundary;
- define public-observation scope handling for SearchClarity-style work;
- define report-safe reference requirements without exposing raw paths or internal handles to customers;
- define customer/private first-party overlay requirements as no-storage read-time inputs only, if needed;
- define promotion/handoff of interpretations, recommendations, and accepted conclusions out to SearchClarity;
- define hostile-path and acceptance criteria for a later bounded proof task;
- identify deeper research or owner rulings required before customer-facing proof.

---

## M15 Non-Authorizations

This decision does not authorize:

```text
customer records in Observatory
customer private analytics storage
customer first-party persistence
report delivery records in Observatory
customer-facing report generation
SearchClarity production integration
real overlay implementation
Postgres
schema or migrations
production API/MCP
network listener
provider calls
additional paid requests
recurring capture
marketplace scraping
browser-extension capture
strategy storage
recommendation storage
automatic conclusion promotion
```

M15 begins with repo-first planning and contract reconciliation only.

---

## Governing Boundary

```text
Observatory supplies evidence.
SearchClarity owns the customer, engagement, interpretation, recommendation, report, and delivery record.
Customer/private inputs do not become Observatory evidence.
```

---

## Next Required Output

Prepare an M15 planning package that includes:

1. SearchClarity consumer-boundary reconciliation;
2. evidence-pack-to-report-support contract requirements;
3. report-safe reference boundary;
4. no-storage overlay decision points;
5. claim-safety and caveat propagation rules;
6. hostile-path acceptance plan;
7. exact bounded proof-task proposal, without implementation authority.
