# M13 Probe Implementation Preparation Review

Status: planning review
Authority: none — not owner acceptance, implementation approval, funding approval, or provider-call authority
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-12

---

## Purpose

Review the M13 implementation-preparation package as a coherent set and determine what is ready, what remains gated, and when credits are actually needed.

Reviewed:

- `planning-inbox/m13-dataforseo-probe-implementation-task-proposal.md`
- `planning-inbox/m13-dataforseo-probe-hostile-path-test-plan.md`
- `planning-inbox/m13-dataforseo-probe-preflight-record-template.md`
- `planning-inbox/m13-dataforseo-probe-post-pull-and-purge-template.md`
- prior M13 plan, review, proposed decision, CLI requirements, and official verification

---

## Disposition

```text
The no-network implementation-preparation package is complete enough for owner review.
Implementation is not yet authorized.
Credits are not needed yet.
```

The package now defines the full lifecycle:

```text
accepted narrow decision
-> bounded no-network implementation
-> hostile-path proof
-> implementation-readiness review
-> credits added by owner
-> exact price verified in account/calculator
-> exact preflight
-> owner confirms request hash
-> one request
-> summarize
-> review
-> purge
-> stop
```

---

## What Is Ready

### Exact implementation boundary

The implementation proposal names a small provider-specific module rather than a generic provider platform.

It explicitly excludes:

```text
Postgres
schema
migrations
provider framework
scheduler
recurring capture
API/MCP
web server
dashboard
customer workflow
```

### Immutable recipe enforcement

The proposal requires decision-bound constants and rejects arbitrary CLI endpoint/payload overrides.

### Credential boundary

Environment-only credential access, no persistence, redaction, and fail-before-network behavior are specified.

### One-request network boundary

Exactly one transport function, one request, zero retry, zero polling, and no alternate endpoint flow are specified.

### Evidence lifecycle

The package covers:

- preflight evidence;
- sanitized request hash;
- duplicate key;
- local Git-ignored raw handling;
- manifest;
- response classification;
- field summary;
- shape fingerprint;
- raw hash verification;
- purge proof.

### Hostile-path coverage

Forty-two hostile cases cover authority, payload mutation, pricing, cost-bearing options, duplicate races, secret leaks, path escape, raw tampering, provider errors, cost disagreement, customer/private contamination, scope creep, second execution, and purge integrity.

### Templates

Preflight and post-pull templates prevent execution/review evidence from being invented after the fact.

---

## What Remains Gated

### Owner acceptance

The controlling probe decision remains proposed.

The owner must explicitly accept or amend:

- funding;
- narrow provider admission;
- exact recipe;
- task/request ceilings;
- `$0.10` maximum cost;
- temporary capture-and-purge posture;
- no-network CLI implementation authority;
- later one-request execution authority subject to preflight.

### Implementation authority

No source or test files may be created until the owner explicitly opens the implementation gate.

### Credits

Credits are not needed to implement or test the CLI with fixtures.

Credits become necessary only after:

```text
accepted decision
implemented CLI
all hostile-path tests pass
implementation-readiness review passes
```

Then the owner adds the minimum credits, and exact request pricing is verified before submission.

### Credentials

Real credentials are not needed for fixture implementation/testing.

They become necessary only for final preflight and the single provider request.

### Execution

Even after implementation and funding, the request remains blocked until:

- exact price is verified at or below `$0.10`;
- account controls are recorded;
- preflight passes;
- duplicate state is clean;
- owner confirms the exact request SHA-256.

---

## Recommended Owner Decision Shape

The owner can efficiently unlock the next batch by accepting the proposed decision with this additional explicit statement:

```text
Authorize implementation and fixture-only testing of the bounded DataForSEO one-shot probe CLI under the committed implementation task proposal and hostile-path test plan.

Do not authorize network execution during implementation or testing.

Authorize adding the minimum DataForSEO credits only after implementation-readiness passes.

Require exact price verification after funding but before submission.

Require a separate exact preflight and owner confirmation before the one paid request.
```

This would allow a useful implementation batch without prematurely turning on the provider machine.

---

## Batch Size Recommendation

Once implementation is authorized, the next batch should include together:

```text
source implementation
tests
Git-ignore update for probe-evidence/
local test execution
test evidence note
implementation-readiness review
index updates
```

Do not split this into tiny commits unless a safety failure forces a stop.

Do not include funding or a provider call in the implementation batch.

---

## Credits Timing

Current answer:

```text
Do not add credits yet.
```

Tell the owner credits are needed only after the no-network implementation and hostile-path proof pass.

At that point, credits are needed to:

- access authenticated pricing/account controls if necessary;
- perform final price verification;
- send the one approved request.

Credits are not needed for more paperwork, code construction, fixtures, or tests.

---

## Current Non-Authorizations

```text
No credits.
No source implementation.
No credentials.
No provider request.
No raw provider payload.
No Postgres.
No schema.
No migrations.
No second request.
```

---

## Review Result

```text
Planning package: complete enough for owner ruling
Implementation preparation: complete
Implementation authority: absent
Funding authority: absent
Execution authority: absent
Credits needed now: no
Next meaningful gate: owner accepts/amends narrow decision and explicitly authorizes no-network implementation
```

---

## Final Rule

```text
The runway is built.
The plane is not cleared for takeoff.
Next, the owner opens the no-network build gate—not the API floodgates.
```
