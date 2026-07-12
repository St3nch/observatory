# Decision - Authorize M15 SearchClarity Fixture-Backed Proof

Status: accepted decision
Date: 2026-07-12
Milestone: M15 - SearchClarity Proof Workflow

## Decision

The owner authorizes the exact implementation task defined in:

```text
planning-inbox/m15-searchclarity-fixture-proof-task-proposal.md
```

This authorization is limited to one local, synthetic, fixture-backed, in-memory proof layered over the accepted M14 typed-read prototype.

## Authorized implementation boundary

Authorized new package:

```text
src/observatory_searchclarity_proof/
```

Authorized tests:

```text
tests/test_searchclarity_report_support_contract.py
tests/test_searchclarity_customer_boundary.py
tests/test_searchclarity_claim_blockers.py
tests/test_searchclarity_reference_boundary.py
tests/test_searchclarity_hostile_paths.py
tests/test_searchclarity_determinism.py
```

Authorized proof metadata:

```text
test-results/m15-searchclarity-proof-result-register.json
planning-inbox/m15-searchclarity-local-test-evidence.md
planning-inbox/m15-searchclarity-proof-closure-readiness-review.md
```

The implementation may amend project metadata only as permitted by the exact task proposal.

## Required behavior

The proof must:

- reuse the accepted M14 typed-read prototype;
- use synthetic, customer-clean request fixtures only;
- preserve evidence caveats and claim-use limits;
- keep internal evidence handles separate from synthetic report-safe references;
- block customer/private fields, report prose, recommendations, overlays, files, and unadmitted source families;
- require consumer promotion and SearchClarity human review;
- always return `customer_facing_output_authorized: false`;
- remain deterministic and side-effect free.

## Explicit non-authorizations

This decision does not authorize:

```text
real customer data
customer records
private analytics
real overlays
screenshots or external files
report generation
report storage
report delivery
recommendations
SearchClarity repository integration
production report-safe references
public/customer reference resolution
provider calls
recurring capture
Postgres
schema or migrations
network listener
real MCP registration
production API/MCP
strategy storage
automatic conclusion promotion
```

## Proof ceiling

A passing result proves only bounded synthetic fixture behavior on a local in-memory execution surface.

It does not prove customer-facing correctness, final report wording, real customer-data rejection completeness, production authentication, database enforcement, network/MCP behavior, overlay discard, SearchClarity integration, concurrency, deployment, or operational durability.

## Stop conditions

Stop rather than widen scope if implementation requires customer/private data, real overlays, report generation, SearchClarity repo access, provider access, a database, network transport, a new external dependency, or a doctrine change.
