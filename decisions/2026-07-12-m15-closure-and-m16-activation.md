# Decision - M15 Closure and M16 Planning Activation

Status: accepted decision
Authority: owner-approved milestone transition
Date: 2026-07-12
Milestone: closes M15; activates M16 planning only

---

## Decision

M15 - SearchClarity Proof Workflow is closed.

M16 - Provider Cross-Check Proof is activated for planning only.

---

## M15 closure basis

M15 closure is supported by:

- accepted `contracts/searchclarity-proof-workflow-v0-1.md`;
- accepted consumer-boundary rulings in `decisions/2026-07-12-m15-searchclarity-contract-and-consumer-boundary-rulings.md`;
- exact proof authorization in `decisions/2026-07-12-m15-searchclarity-fixture-proof-authorization.md`;
- local synthetic fixture-backed implementation in `src/observatory_searchclarity_proof/`;
- full owner-local suite result: 156 tests passed;
- machine-readable result register at `test-results/m15-searchclarity-proof-result-register.json`;
- closure-readiness review at `planning-inbox/m15-searchclarity-proof-closure-readiness-review.md`.

The accepted proof class is:

```text
proof_class: mixed_suite
execution_surface: synthetic_fixture_in_memory_local
proof_strength: bounded_enforcement_proof
```

M15 proved, within the committed synthetic local surface, that SearchClarity evidence support can preserve claim-safety, caveats, scope, report-safe reference separation, customer/private rejection, human-review requirements, and consumer promotion without turning Observatory into a customer database, report system, recommendation store, overlay store, or production integration.

---

## M15 limits preserved

M15 closure does not claim:

- exhaustive real customer-data detection;
- final customer-facing report language correctness;
- real SearchClarity repository or production integration;
- real overlay discard or no-storage enforcement;
- production report-safe reference design;
- database, transaction, production-auth, network, MCP, deployment, or operational proof;
- provider execution or recurring capture.

Those limits remain explicit and are not converted into accepted capability.

---

## M16 active boundary

M16 may plan:

- provider cross-check and disagreement proof requirements;
- comparability and incomparability classification;
- capture-time-distance and context-alignment warnings;
- provider-attributed side-by-side evidence output;
- proprietary metric labels and methodology caveats;
- disagreement evidence read shapes;
- hostile-path tests for winner logic, averaging, composite scores, and truth-provider claims;
- one exact bounded fixture-backed proof proposal after contract and ruling gates.

M16 may use only committed admitted fixtures or sanitized structural/provider-testimony evidence unless a later separate owner decision authorizes any real provider work.

---

## M16 non-authorizations

M16 planning activation does not authorize:

```text
new provider calls
DataForSEO requests
Ahrefs or Semrush purchases
provider credentials
recurring cross-provider capture
truth scores
provider winner logic
provider averaging into truth
composite authority or opportunity scores
customer data
customer reports
real overlays
Postgres
schema or migrations
production API/MCP
production integrations
strategy or recommendation storage
automatic conclusion promotion
```

---

## Current law

```text
Provider disagreement is evidence.
No provider becomes truth.
No winner, average, or composite may erase disagreement.
Meaning remains a consumer-side interpretation.
```

---

## Next task

Begin M16 with repo-first reconciliation of the accepted provider-testimony, provider-cross-check, freshness, claim-safety, typed-read, and SearchClarity consumer contracts.

No proof implementation is authorized by this decision.
