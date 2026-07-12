# M15 SearchClarity Hostile-Path and Acceptance Plan

Status: planning / proof design
Authority: none until owner acceptance
Milestone: M15
Date: 2026-07-12

---

## Purpose

Define the high-consequence hostile paths and ordinary contract-acceptance checks required before any bounded SearchClarity proof implementation.

Only high-consequence boundary attacks are classified as hammers. Response-shape, vocabulary, and warning-order checks remain contract-acceptance or semantic-safety tests.

---

## Proof taxonomy

Every proof result must name:

```text
proof_class
execution_surface
proof_strength
limitations
```

Allowed proof classes:

```text
consumer_boundary_hammer
overlay_boundary_hammer
citation_boundary_hammer
claim_safety_hammer
contract_acceptance
semantic_safety
static_conformance
unit
```

First proof execution surface:

```text
fixture_in_memory_local
```

No result may claim database, transaction, production authentication, network/MCP, deployment, real customer-data, or report-delivery enforcement.

---

## High-consequence hostile-path hammers

### M15-H1 — Customer identity laundering

Attempts:

- customer name/email/shop/account as `scope_id`;
- order/report/gig/invoice ID as evidence identity;
- customer identifier hidden in a label, purpose field, or reference;
- synthetic request body self-asserting a wider caller identity.

Required result:

- hard failure;
- no identity stored or echoed;
- no existence leak;
- no partial evidence response.

### M15-H2 — Customer/private content exfiltration or storage

Attempts:

- GSC/GA4/Etsy/Shopify/YouTube private values;
- customer messages;
- screenshots, CSV/PDF paths, file contents, or private URLs;
- consent records or signatures;
- private values embedded in free text.

Required result:

- `blocked_private_data` or `blocked_not_admitted`;
- no logging of private values;
- no evidence ID, raw-support record, cache, or output echo;
- no fallback to silent stripping and partial success.

### M15-H3 — Report/recommendation laundering

Attempts:

- recommendation disguised as claim intent;
- report paragraph disguised as evidence context;
- strategy or priority disguised as metadata;
- request to approve, publish, deliver, or revise a report;
- prompt injection asking the system to mark output customer-ready.

Required result:

- blocked request or evidence-only response;
- `consumer_promotion_required: true`;
- `customer_facing_output_authorized: false`;
- no prose, recommendation, task, or workflow state created.

### M15-H4 — Caveat detachment

Attempts:

- projection excluding warnings;
- token budget that retains values but drops caveats;
- report-safe reference returned without status/freshness/claim warnings;
- caller preference asking for “clean” output.

Required result:

- mandatory caveats remain attached;
- whole-unit truncation only;
- block if caveats cannot travel;
- deterministic warning order.

### M15-H5 — Report-safe reference enumeration and cross-scope resolution

Attempts:

- sequential reference guessing;
- neighboring reference walking;
- resolving another synthetic scope's reference;
- using internal evidence handles as customer-facing references;
- tampered artifact-local mapping.

Required result:

- uniform `not_found` for unauthorized/nonexistent references;
- no internal handle disclosure;
- no scope name or count leak;
- no public resolution path.

### M15-H6 — Claim-status bypass

Attempts:

- current claim from stale or unknown evidence;
- active claim from withdrawn, invalidated, rights-blocked, or retention-expired evidence;
- absence claim without sample context;
- provider metric without provider attribution;
- AI/GEO claim presented as endorsement/influence;
- marketplace claim from an unadmitted source family.

Required result:

- deterministic blocking or historical-only downgrade per contract;
- no caller override;
- no report-support approval.

### M15-H7 — Overlay smuggling

Attempts:

- private analytics passed as request metadata;
- screenshot/file path labeled as public evidence;
- overlay values hidden inside evidence-family filters;
- no-storage assertion used to bypass actual overlay deferral;
- request to cache values “temporarily.”

Required result:

- real overlays remain blocked;
- no storage, cache, evidence identity, logging, or output echo;
- no comparison output;
- no trigger of capture, spend, task, or report.

### M15-H8 — Cross-customer aggregation

Attempts:

- multiple engagement scopes in one request;
- wildcard scope;
- aggregate benchmark request using customer-linked scopes;
- repeated reads designed to reconstruct cross-scope corpus.

Required result:

- single-scope enforcement;
- bounded read ceilings;
- no aggregate output;
- no record-count or scope-discovery leak.

### M15-H9 — No-side-effect consumer boundary

Static and runtime checks must prove report-support reads do not:

- write files;
- mutate fixtures;
- call provider code;
- create report artifacts;
- create tasks or recommendations;
- persist handoff records;
- import database drivers;
- invoke network or subprocess paths;
- persist overlays or customer state.

---

## Contract-acceptance checks

These are not hammers unless they exercise a high-consequence boundary:

- exact request vocabulary;
- required response envelope;
- report-support disposition vocabulary;
- mandatory `consumer_promotion_required` and `customer_facing_output_authorized` fields;
- deterministic ordering;
- synthetic report-safe reference format;
- provider-attribution adjacency;
- sampled-absence warning shape;
- AI/GEO sample-bound warning shape;
- marketplace blocked-state shape;
- coverage/blind-spot output;
- whole-unit context truncation.

---

## DR9 and DR10 routing

### DR9 — Customer-facing report language

M15 proof does not generate final customer wording. DR9 remains required before SearchClarity launch or customer-facing report templates are accepted.

The bounded proof may verify that evidence-side warning codes and support dispositions are sufficient inputs for a human-reviewed consumer workflow.

### DR10 — Customer first-party overlays

Real overlay implementation remains deferred to M17 under the proposed OR-F1 ruling.

M15 proves only that overlay-shaped/private inputs fail closed and do not leak or persist.

---

## Machine-readable result requirements

A later implementation proof register must include:

```text
result_id
contract_version
implementation_commit
proof_class
execution_surface
proof_strength
test_command
result
executed_at
evidence_path
limitations
```

Required limitations:

```text
synthetic customer-clean fixtures
fixture-backed
in-memory
no customer-data proof
no overlay-discard proof
no report-generation proof
no SearchClarity integration proof
no database or transaction proof
no production-auth proof
no network/MCP proof
no deployment proof
```

---

## Entry gate

No proof implementation until:

- `contracts/searchclarity-proof-workflow-v0-1.md` is accepted;
- OR-E1 through OR-E5 are ruled;
- OR-F1 is ruled;
- consent and human-review boundaries are ruled;
- this plan is accepted;
- an exact task is separately authorized.

---

## Non-authorization

This plan does not authorize customer data, overlays, report generation, customer-facing references, SearchClarity integration, Postgres, schema, provider calls, production API/MCP, or implementation.
