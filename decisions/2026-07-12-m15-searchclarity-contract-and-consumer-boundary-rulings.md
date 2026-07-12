# Decision - M15 SearchClarity Contract and Consumer-Boundary Rulings

Status: accepted decision
Authority: owner decision recorded from the instruction to proceed with the prepared M15 ruling and contract acceptance pass
Date: 2026-07-12
Milestone: M15 - SearchClarity Proof Workflow

---

## Decision

Accept `contracts/searchclarity-proof-workflow-v0-1.md` as the binding M15 SearchClarity evidence-support contract within its declared scope.

Accept the following M15 rulings:

### OR-E1 - Report-safe references

M15 uses a separate report-safe reference class rather than exposing internal Observatory evidence handles.

For the first bounded proof, report-safe references must be synthetic, opaque, non-enumerable, artifact-local, and non-resolving outside the internal SearchClarity support path. They must not expose internal evidence handles, provider task IDs, raw pointers, paths, database identity, customer identifiers, or other scopes.

No production reference service, customer-facing lookup, or public resolution is authorized.

### OR-E2 - Marketplace evidence

Marketplace report support remains blocked until the exact platform, surface, public/private posture, capture method, rights, retention, and claim ceiling are separately admitted.

Public visibility alone does not admit a source. Scraping, private dashboard inference, traffic/sales inference, and customer-behavior inference remain forbidden.

### OR-E3 - AI/GEO report support

M15 does not create a durable AI visibility score, universal presence claim, or universal absence claim.

A single observation may support only sampled point-in-time evidence with prompt or panel, surface, context, capture time, and sample limitations preserved. Repeated-sampling thresholds remain a separate methodology decision and are not invented by M15.

Citation or mention must not be represented as trust, endorsement, authority, recommendation, or influence.

### OR-E4 - Provider disagreement

SearchClarity may later show provider-attributed testimony side by side. Observatory must not select a winner, average values into truth, or create a composite score.

Provider methodology and incomparability caveats are mandatory. M15 does not authorize customer-facing prose.

### OR-E5 - Automatic report-support blockers

The following conditions block report support for the affected claim:

```text
blocked_by_rights
expired_by_retention
withdrawn
invalidated
blocked_private_data
missing provider attribution for provider metrics
missing sampled context for absence claims
stale or unknown freshness for current-state claims
missing mandatory caveats
source or capture family not admitted
```

`superseded` evidence may support historical-only use with an explicit warning.

`stale` or `unknown` evidence may support historical-only use only when the claim intent permits it. They cannot silently support a current-state claim.

These are evidence-support dispositions, not approval or rejection of final SearchClarity wording.

### OR-F1 - Overlay posture during M15

Real customer first-party overlays remain deferred to M17.

M15 may define interfaces, blocked-path behavior, and hostile-path criteria only. Real overlay values, screenshots, CSV files, PDFs, exports, private files, and customer identifiers remain blocked.

No overlay cache, value logging, comparison output, or discard implementation is authorized.

### Consent boundary

Customer consent remains a SearchClarity business record and must not be stored in Observatory.

A future admitted request may contain only a minimal non-private consumer-side authorization assertion for an already admitted input class. Customer identity, signature, consent document, account ID, and private file remain outside Observatory.

### Human review and customer-facing output

No Observatory report-support disposition authorizes customer-facing delivery.

SearchClarity owns human review, caveat translation, final wording, recommendations, acceptance, delivery, and revision state.

The first bounded proof must always preserve:

```text
consumer_promotion_required: true
customer_facing_output_authorized: false
```

### Bounded proof eligibility

One local synthetic fixture-backed M15 proof may be separately authorized after this decision.

Eligible proof scope is limited to:

- accepted M14 typed-read prototype behavior;
- committed synthetic Observatory evidence fixtures;
- sanitized provider evidence already admitted for structural/provider-testimony use;
- synthetic SearchClarity requests and handoff fixtures containing no real customer identity, private analytics, report prose, external files, or overlay values.

This decision establishes proof eligibility only. It does not authorize implementation.

---

## Contract effect

`contracts/searchclarity-proof-workflow-v0-1.md` supersedes `contracts/searchclarity-consumer-placeholder.md` for M15 behavior.

The placeholder remains useful as historical M7 planning context but no longer controls M15 behavior where the accepted full contract applies.

---

## Explicit non-authorizations

This decision does not authorize:

```text
M15 proof implementation
customer data
customer-private analytics
real overlays
screenshots or file intake
report generation
report delivery
customer-facing prose
production SearchClarity integration
production report-safe references
public reference resolution
marketplace source admission
AI/GEO scoring methodology
provider calls
recurring capture
Postgres
schema
migrations
production API or MCP
strategy or recommendation storage
automatic conclusion promotion
```

A separate exact owner authorization is required before implementing `planning-inbox/m15-searchclarity-fixture-proof-task-proposal.md`.
