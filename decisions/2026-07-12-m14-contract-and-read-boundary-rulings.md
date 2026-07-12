# Decision — M14 Contract and Read-Boundary Rulings

Status: accepted
Date: 2026-07-12
Milestone: M14 — Typed Read API / MCP Contract and Prototype
Owner authorization: “LRTS DO IT” / proceed with the prepared M14 owner-ruling set

---

## Decision

The owner accepts the following prepared rulings.

### 1. M7 contract set v0.1

The thirteen M7 contract artifacts are accepted as Observatory contract set v0.1 within their declared scopes and limitations:

- `contracts/scope-rights-retention.md`
- `contracts/evidence-id-citation.md`
- `contracts/freshness-staleness-volatility.md`
- `contracts/claim-safety.md`
- `contracts/query-panel.md`
- `contracts/capturepackage-v0-1.md`
- `contracts/raw-archive-provider-drift.md`
- `contracts/provider-testimony.md`
- `contracts/provider-cross-check.md`
- `contracts/consumer-promotion.md`
- `contracts/overlay.md`
- `contracts/searchclarity-consumer-placeholder.md`
- `contracts/typed-read-tool-skeleton.md`

Acceptance does not resolve open ruling candidates inside those contracts. Placeholder and skeleton artifacts remain limited by their own labels and owning milestones.

### 2. OR-D1 — caller authentication and authorization

M14 read access uses authenticated caller classes with explicit scope and request-type grants. Caller identity is supplied by the access layer and cannot be self-asserted or widened by request content. Cross-scope access is forbidden by default.

Initial caller classes:

- `internal_llm`
- `operator`
- `kaizen`
- `neon_ronin`
- `searchclarity_internal`

No public or customer-facing caller is admitted.

### 3. OR-D2 — raw-pointer exposure

Raw payload pointers and archive paths remain internal-only. Typed read outputs may expose raw-support status, but never raw filesystem paths, object-store paths, credentials, or secret-bearing references.

### 4. OR-D3 — status-aware evidence reads

Evidence is never silently overwritten. Current status controls read behavior.

- superseded evidence may be returned only as historical/status-caveated evidence;
- withdrawn, invalidated, blocked-by-rights, and expired-by-retention evidence must not be returned as active evidence;
- later status transitions invalidate stale cursor/cache assumptions.

### 5. OR-D4 — update-window feeds

Update-window feed metadata is optional evidence input, not mandatory for every M14 fixture. Missing relevant feed data fails closed to unknown or caveated freshness/volatility status. No cadence may be invented.

### 6. OR-A4 M14 scope-down

M14 supports internal, non-enumerable, status-aware evidence handles only. Report-safe or customer-facing references remain deferred to M15.

### 7. OR-D5 — read-security logging

Ordinary successful reads do not create Observatory evidence events. Authentication failures, authorization failures, enumeration attempts, and rate/ceiling breaches may create bounded security/access logs outside the evidence corpus.

Those logs are operational/security records, not observations or customer records, and must exclude credentials and private payload content.

### 8. OR-D6 — machine-readable test-result register

M14 may define a committed machine-readable implementation-test result register as repository proof metadata. It is not Observatory business evidence and is not a database requirement.

Every result must name proof class, execution surface, proof strength, commit, result, evidence path, and limitations.

### 9. Bounded prototype eligibility

After the accepted M14 contract and hostile-path gates are satisfied, the steward may prepare one exact local fixture-backed prototype task proposal.

This ruling does not authorize implementation. Any prototype implementation requires a separate exact task decision.

The eligible prototype remains:

- local-only;
- in-memory;
- no network listener;
- no real MCP registration;
- no database;
- no customer data;
- no provider call;
- no persistence;
- no overlay;
- no report output.

---

## Explicit non-authorizations

This decision does not authorize:

- prototype implementation;
- production API or MCP deployment;
- Postgres, physical schema, or migrations;
- direct SQL or credentials for LLMs/agents;
- live provider ingestion or another paid provider request;
- customer data or customer first-party analytics storage;
- recurring capture;
- public/customer-facing callers;
- report-safe references;
- dashboards or customer-facing reports;
- strategy/recommendation storage;
- automatic conclusion promotion.

---

## Unresolved lineage item

The named RG3/RG8 Kaizen Hermes inputs remain unconsumed. This decision does not waive that gap. The exact inputs must be consumed, or a later explicit owner waiver must be recorded, before dependent final contract acceptance claims rely on them.

---

## Consequence

The M7 contract set now binds as v0.1 within its declared scope. M14 may promote its real typed-read contract from planning only after reconciling it against this decision, the hostile-path plan, and the remaining lineage requirement.
