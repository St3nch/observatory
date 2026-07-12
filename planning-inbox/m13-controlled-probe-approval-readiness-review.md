# M13 Controlled Probe Approval Readiness Review

Status: planning review
Authority: none — advisory review only; not owner approval, funding approval, implementation approval, or request authorization
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-11
Reviewed decision proposal: `decisions/2026-07-11-m13-dataforseo-controlled-probe-approval.md`
Reviewed CLI requirements: `planning-inbox/m13-dataforseo-probe-cli-requirements.md`
Reviewed official verification: `planning-inbox/m13-dataforseo-official-verification-2026-07-11.md`

---

## Purpose

This review evaluates whether the M13 controlled DataForSEO probe planning package is coherent enough for owner ruling.

It reviews the package as a set:

```text
probe plan
-> probe-plan review
-> proposed owner decision
-> CLI requirements
```

It answers:

```text
What is complete enough for owner review?
What still requires fresh external verification?
What authority is still absent?
What happens after the owner accepts, amends, or rejects the proposal?
```

This review does not authorize:

```text
credits
use of existing credits
CLI implementation
provider calls
paid pulls
raw payload capture
Postgres
schema
migrations
```

---

## Package Reviewed

- `planning-inbox/m13-dataforseo-admission-and-probe-plan.md`
- `planning-inbox/m13-dataforseo-probe-plan-review.md`
- `decisions/2026-07-11-m13-dataforseo-controlled-probe-approval.md`
- `planning-inbox/m13-dataforseo-probe-cli-requirements.md`
- `research/rg1-dataforseo-rights-retention-cost.md`
- `research/rg10-capturepackage-v0-1-inputs.md`
- `research/rg11-raw-archive-provider-drift.md`
- applicable M7 contracts and M8 hammer policy

---

## Review Disposition

```text
The M13 planning package is ready for owner review and ruling.
It is not ready for execution.
```

The package now contains:

- a narrow probe purpose;
- explicit non-authorizations;
- one proposed endpoint and request recipe;
- proposed funding, task, request, retry, polling, repeat, and cost ceilings;
- duplicate-prevention requirements;
- credential and secret boundaries;
- proposed local capture-and-purge posture;
- required manifest, field summary, shape fingerprint, and purge evidence;
- preflight and post-pull review gates;
- a bounded CLI requirements specification;
- explicit hammer expectations;
- no Postgres, schema, migration, API/MCP, dashboard, customer, recurring, or strategy scope.

Fresh official verification on 2026-07-11 confirmed the endpoint, one-live-request shape, proposed request fields, current $50 minimum payment, duplicate-task warning, provider-side 365-day retention statement, and relevant SERP usage restriction.

One material pre-submit blocker remains: the exact current price for the exact proposed request was not reliably exposed in retrievable official page text. Per the owner's 2026-07-12 timing ruling, price confirmation may occur after credits are added, but the official calculator or authenticated account interface must still confirm the request cannot exceed the proposed $0.10 ceiling before submission.

---

## What Is Ready for Owner Ruling

### 1. Decision scope

The proposal is narrow enough to rule on without accidentally admitting DataForSEO broadly.

It applies to one payload-inspection probe only and rejects inherited authority for any second request.

### 2. Proposed request recipe

The proposal names concrete fields rather than leaving implementation to invent them:

```text
provider
endpoint
request mode
keyword
location code
language code
device
operating system
depth
```

These remain proposals until acceptance.

### 3. Spend and request controls

The proposal distinguishes:

```text
funded account balance
actual probe spend ceiling
billable task ceiling
API request ceiling
retry ceiling
polling ceiling
repeat ceiling
```

That prevents the usual nonsense where “one task” quietly becomes several network calls and a small billing surprise.

### 4. Raw evidence posture

The proposal uses a conservative planning posture:

```text
capture_and_purge_raw
local only
Git-ignored
no cloud upload
no database write
seven-day maximum retention
sanitized manifest/summary only after review
```

Unknown rights or retention still block execution.

### 5. CLI safety boundary

The CLI requirements describe a one-shot safety cage rather than a general integration.

They block arbitrary endpoints, arbitrary payload flags, retries, polling, recurring modes, database writes, serving, API/MCP exposure, and broad provider abstractions.

### 6. Audit and hostile-path expectations

The package requires preflight evidence, exact request hashing, duplicate prevention, append-only audit events, response classification, raw hash verification, safe purge, and post-pull review.

M12 fixture proof is correctly not treated as automatic provider-probe acceptance.

---

## What Still Requires Fresh Verification

The following are not responsibly frozen by repo planning alone because they may change externally.

### Official endpoint and request fields

Verify from current official DataForSEO documentation:

- endpoint path still exists;
- live advanced remains a one-request flow;
- every proposed field is accepted;
- no unnamed required field exists;
- location and language codes retain intended meanings;
- device/OS pairing remains valid;
- depth behavior remains as expected;
- response format still exposes needed status/cost metadata.

### Pricing and account funding

Verify from current official sources:

- current minimum account payment;
- current endpoint pricing;
- whether the exact proposed request could exceed the proposed spend ceiling;
- whether any account-level budget or usage controls are available;
- whether taxes, fees, minimums, or pricing modes alter the proposal.

### Terms, allowed use, and raw retention

Verify current official terms and related materials for:

- internal payload-shape inspection;
- temporary local raw-response retention;
- retaining a sanitized manifest after purge;
- retaining a sanitized field-path summary;
- using shape evidence to inform later internal planning;
- any restrictions on raw SERP data storage or redistribution.

If official materials do not clearly support the proposed posture, the decision must be amended to a stricter posture or blocked pending clarification.

### Credential mechanism

Verify the actual account authentication mechanism and define local environment-variable names without storing values in the repo.

This does not mean requesting credentials now.

---

## Owner Choices Available Now

### Option A — Accept after fresh verification

The owner may accept the decision only after fresh official verification confirms the binding values or the decision is amended to match verified truth.

Acceptance would authorize only the narrow planning scope explicitly stated in the decision. CLI implementation would still require a separate roadmap or owner gate if the accepted wording preserves that separation.

### Option B — Amend the proposal

The owner may change:

- endpoint;
- query;
- location/language/device;
- spend ceiling;
- task/request ceilings;
- raw-retention posture;
- purge deadline;
- required outputs;
- stop conditions.

Any material change must be recorded in the decision before acceptance.

### Option C — Reject or defer

The owner may reject the probe or defer it without harming M12 proof.

If deferred, M13 cannot pretend provider admission occurred. The roadmap must explicitly record whether M13 remains active, closes without a live probe, or is blocked.

---

## Authority Still Missing

At review time, all of the following remain absent:

```text
accepted owner decision
funding authority
existing-credit-use authority
CLI implementation authority
credential-use authority
network-request authority
raw-capture authority
provider admission beyond planning
Postgres authority
schema authority
migration authority
```

The presence of an exact endpoint or request body in a proposed file does not create any of these authorities.

---

## Required Sequence After Owner Acceptance

If the owner accepts an amended or verified decision, the safe sequence is:

```text
1. Record accepted decision and exact binding values.
2. Record fresh official verification evidence.
3. Create a bounded CLI implementation task/spec naming exact files and tests.
4. Implement locally without provider calls.
5. Run automated and owner-local hostile-path tests.
6. Review implementation readiness.
7. Add minimum credits only when the accepted decision and tested CLI require them.
8. Run exact preflight.
9. Owner confirms the exact paid request.
10. Send one request.
11. Produce manifest, hash, field summary, and shape fingerprint.
12. Stop M13 execution work.
13. Review the result before any second request or persistence planning.
14. Purge raw response by the accepted deadline.
```

No step should be skipped because the endpoint appears cheap. Cheap mistakes are still mistakes; they just have worse receipts.

---

## Required Sequence If Owner Does Not Accept

If the decision remains proposed, is rejected, or is deferred:

```text
No credits.
No CLI implementation unless separately authorized as a no-network fixture-only proof.
No credentials.
No request.
No raw payload.
No provider admission claim.
```

The roadmap and active context should continue to show M13 planning, blocked status, or another explicit owner-chosen disposition.

---

## M13 Closure Readiness

M13 is not yet ready to close solely because the planning package exists.

Current M13 exit criteria include provider admission approval, a pull recipe, ceilings, stop conditions, explicit raw handling, and correct next-milestone pointers.

At least one of these must happen before closure:

```text
A. The owner accepts the controlled-probe decision and the approved M13 path is completed and reviewed.
B. The owner explicitly closes M13 without execution and records what is deferred or blocked.
C. The owner rejects DataForSEO admission and records a replacement provider or roadmap amendment.
```

A proposed decision is not provider admission approval.

---

## Index and Tracker Actions

This batch should index:

- the M13 probe-plan review;
- the M13 CLI requirements;
- this approval-readiness review;
- the proposed M13-D1 decision.

The owner-ruling tracker should link OR-C1 and related raw-retention rows to the proposed decision while leaving them open until owner acceptance.

---

## Review Conclusion

### Complete enough now

```text
M13 planning package
concrete proposed owner gate
one-shot CLI requirements
cost/request/duplicate controls
raw capture-and-purge proposal
preflight and post-pull gates
owner review choices
```

### Not complete now

```text
fresh official verification
owner acceptance
implementation authority
tested CLI
funding
request execution
post-pull evidence
raw purge proof
M13 closure
```

---

## Final Rule

```text
The paperwork is now sharp enough for a real owner ruling.
The provider machine is still off.
Next authority comes from the owner and fresh official verification, not from momentum.
```
