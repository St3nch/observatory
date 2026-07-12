# M9 First-Slice Candidate Comparison

Status: planning / candidate comparison
Authority: none — advisory M9 planning input; roadmap and decisions remain authority
Purpose: compare first evidence slice candidates against the M8 hammer gate policy before schema planning
Date: 2026-07-10
Reviewer: ChatGPT / Observatory Steward

---

## Review Question

Which first evidence slice should Observatory select for M9 so M10 can plan schema without guessing, while avoiding early provider spend, customer data, marketplace ambiguity, dashboard/API/MCP implementation, and strategy storage?

---

## Source Files Reviewed

- `ROADMAP.md`
- `ACTIVE_CONTEXT.md`
- `02-boundaries.md`
- `contracts/README.md`
- `hammers/hammer-matrix-v0-1.md`
- `hammers/acceptance-gate-policy-v0-1.md`
- `planning-inbox/m8-hammer-planning-review.md`
- `planning-inbox/owner-ruling-tracker.md`
- M6 research corpus by index where relevant

---

## M9 Boundary

M9 is allowed to choose a first slice and name gates.

M9 is not allowed to:

```text
schema design
migrations
implementation
provider purchases
paid provider pulls
provider admission
API/MCP implementation
dashboard work
customer data handling
capture runner implementation
automated recurring capture
strategy/recommendation storage
accepting any hammer as passed
```

This document does not choose schema, create tables, design migrations, implement tests, or authorize provider calls.

---

## Candidate Filter Used

A strong first slice should:

- avoid customer private data;
- avoid paid provider pulls;
- avoid marketplace capture ambiguity;
- avoid dashboard/API/MCP dependency;
- exercise scope, rights, retention, provenance, evidence IDs, and observation/conclusion separation;
- produce enough shape for M10 schema planning and M12 hammer execution.

A risky first slice requires one or more of:

- DataForSEO or other paid provider calls before M13;
- customer GSC/GA4/Etsy/Shopify/private analytics;
- marketplace scraping or browser-extension capture;
- SearchClarity customer report workflow;
- direct SQL/API/MCP read tooling;
- strategy or recommendation persistence;
- recurring capture.

---

## Candidate Summary

| Candidate | Summary | M9 Fit | Primary Problem |
|---|---|---:|---|
| C1 DataForSEO SERP/keyword observation sample | First slice centered on DataForSEO provider observation | medium | Pulls provider admission/spend concerns too early unless fixture-only |
| C2 Manual/public page snapshot package | Public/manual observation fixture with raw support and evidence ID | high | Needs clear manual-capture boundary but can avoid provider spend/customer data |
| C3 Provider-response raw archive plus metadata | Fixture provider response stored as raw support with hash/pointer | medium-high | Strong raw/drift proof, but risks becoming provider-admission-shaped too early |
| C4 Query panel plus evidence ID output | Versioned query panel with observation/evidence ID output using fixtures | high | May be too abstract unless paired with an observed artifact |
| C5 Provider disagreement mini-proof using controlled fixture data | Compares two attributed provider-like fixture observations | medium | OR-A1 ledger persistence and provider-truth issues make it better for M16 |

---

## Candidate C1 — DataForSEO SERP / Keyword Observation Sample

### Description

A first slice that models a DataForSEO-style SERP or keyword observation as the initial evidence path.

### Strengths

- Relevant to Observatory's long-term SEO/SERP evidence purpose.
- Exercises provider testimony, source attribution, request context, cost awareness, raw payload support, and freshness.
- Helps later M13 provider admission planning.

### Risks

- Real DataForSEO pulls are not allowed until provider admission and spend gates.
- Even planning around DataForSEO too early could blur M9 into M13.
- Provider-specific payload shape could overfit M10 schema planning to a provider before admission.
- Cost ceilings, duplicate task checks, endpoint recipes, and stop conditions remain future gates.

### Applicable Hammers

```text
H1  Scope isolation
H2  Rights fail-closed
H5  No strategy/recommendation storage
H6  CapturePackage validation
H7  Provider spend/duplicate tasks
H8  Provider attribution/disagreement
H9  Freshness/claim use
H12 Raw archive integrity
H13 Provider drift/parser safety
H15 Evidence ID/citation integrity
H19 Append-only observations
H20 Concurrency safety if capture tasks exist
H21 Audit-first enforcement
```

### M9 Verdict

```text
Do not choose as real-provider first slice.
Possible only as controlled fixture shaped like provider testimony, with no provider call and no provider admission claim.
```

C1 is useful later, but as the first slice it risks pulling M13 into M9 unless heavily constrained.

---

## Candidate C2 — Manual / Public Page Snapshot Package

### Description

A first slice centered on a manually supplied public-page observation package. The package records an observed public URL/page snapshot or page-derived evidence fixture with provenance, capture context, rights/retention posture, raw support pointer/hash, and evidence ID behavior.

The slice would not scrape, crawl, or automate capture. It would define the observation envelope for a controlled public/manual artifact.

### Strengths

- Avoids paid provider pulls.
- Avoids customer private data.
- Avoids marketplace-specific ambiguity if the source family is constrained to generic public web fixture or owner-controlled/public test page.
- Exercises the core telescope behavior: observed artifact, provenance, scope, rights, retention, raw support, evidence ID, and no conclusion storage.
- Gives M10 enough shape to plan minimal schema around observation/admission/evidence identity without provider-specific overfit.
- Gives M12 a concrete surface for hammers without requiring external providers.

### Risks

- Manual capture family is not fully admitted as a future production capture method.
- Must not turn into arbitrary web scraping or browser-extension capture.
- Must not store page meaning, recommendation, or strategy.
- Needs strict wording: controlled fixture / public manual observation package, not production capture runner.

### Applicable Hammers

```text
H1  Scope isolation
H2  Rights fail-closed
H3  Retention enforcement
H5  No strategy/recommendation storage
H6  CapturePackage validation or equivalent observation envelope
H9  Freshness/claim-use warning for point-in-time evidence
H12 Raw archive integrity
H15 Evidence ID/citation integrity
H18 Hostile weird input
H19 Append-only observations
H21 Audit-first enforcement
H22 Rollback/recovery expectations for M10/M19 planning
```

### Deferred / Non-Applicable Hammers

```text
H4  Customer-private rejection — relevant as a rejection fixture, not core positive path
H7  Provider spend/duplicate tasks — deferred; no paid provider
H8  Provider attribution/disagreement — deferred; no provider comparison
H10 AI/GEO overclaim — deferred unless page is AI-answer surface evidence
H11 Marketplace evidence ceiling — avoid marketplace source family in first slice
H13 Provider drift/parser safety — deferred unless provider-shaped fixture is included
H14 Query panel immutability — optional companion, not required for core page snapshot
H16 Consumer request/overlay — deferred; no consumer workflow
H17 LLM/agent access — later read-tool gate
H20 Concurrency safety — later if capture/admission can race
```

### M9 Verdict

```text
Best candidate if constrained to a controlled public/manual observation fixture and not treated as production capture approval.
```

C2 is the cleanest first slice because it exercises core evidence behavior while avoiding premature provider, customer, marketplace, API/MCP, and dashboard work.

---

## Candidate C3 — Provider-Response Raw Archive Plus Metadata

### Description

A first slice centered on a fixture provider response and raw archive metadata: raw payload pointer/hash, provider-like identity, request context, parser status, and drift status.

### Strengths

- Exercises raw archive integrity strongly.
- Exercises provider testimony concepts without spending money if fixtures are used.
- Helps M10 think about raw support, parser safety, drift quarantine, and evidence IDs.

### Risks

- May bias first schema planning toward provider-specific payload handling before provider admission.
- Can blur fixture provider data with admitted provider evidence.
- Provider drift/parser hammers are important but not necessarily the smallest first proof of Observatory identity.

### Applicable Hammers

```text
H1  Scope isolation
H2  Rights fail-closed
H5  No strategy/recommendation storage
H6  CapturePackage validation
H8  Provider attribution/no truth collapse if provider-like fields exist
H12 Raw archive integrity
H13 Provider drift/parser safety
H15 Evidence ID/citation integrity
H19 Append-only observations
H21 Audit-first enforcement
```

### M9 Verdict

```text
Good supporting fixture family, but not the primary first slice unless paired with C2 and explicitly marked fixture-only.
```

C3 should likely become an optional raw-support facet inside the C2 first slice, not the whole first slice by itself.

---

## Candidate C4 — Query Panel Plus Evidence ID Output

### Description

A first slice centered on a versioned query panel, one run, candidate observation, evidence ID, and a shaped evidence output.

### Strengths

- Exercises query-panel immutability and evidence ID behavior.
- Supports later recurring/watch-panel thinking without implementing recurrence.
- Helps bind observation to intent/context without storing strategy.

### Risks

- Can become abstract if there is no concrete observed artifact.
- Query panels are measurement programs, not strategy lists; this must remain explicit.
- If paired with provider pulls, it becomes too early.

### Applicable Hammers

```text
H1  Scope isolation
H2  Rights fail-closed
H5  No strategy/recommendation storage
H6  CapturePackage validation
H9  Freshness/claim-use warning
H14 Query panel immutability
H15 Evidence ID/citation integrity
H19 Append-only observations
H21 Audit-first enforcement
```

### M9 Verdict

```text
Strong companion to C2, but weaker as a standalone first slice.
```

C4 should be used as a context wrapper only if the first slice needs a query/panel context. It should not force early recurring capture or provider workflows.

---

## Candidate C5 — Provider Disagreement Mini-Proof With Controlled Fixtures

### Description

A first slice comparing two attributed provider-like fixture observations and preserving disagreement without averaging into truth.

### Strengths

- Directly proves one of Observatory's important differentiators: provider disagreement as evidence.
- Exercises provider attribution, no winner logic, no fake average, caveats, and claim safety.

### Risks

- OR-A1 remains open for persisted Disagreement Ledger vs compute-on-read only.
- Provider disagreement proof is explicitly M16-shaped.
- It is not the smallest first slice because it requires at least two observation families and comparison behavior.
- Could accidentally store interpretive disagreement summaries if not extremely constrained.

### Applicable Hammers

```text
H5  No strategy/recommendation storage
H8  Provider attribution/disagreement
H9  Freshness/claim-use warning
H15 Evidence ID/citation integrity
H19 Append-only observations
H21 Audit-first enforcement if stored comparison state exists
```

### M9 Verdict

```text
Do not choose as first slice. Preserve for M16 or later fixture proof after the base observation slice exists.
```

C5 is important, but it is second-order. Observatory needs a clean first observation/evidence path before proving cross-provider disagreement.

---

## Recommended First Slice

```text
Controlled Public Manual Observation Package
```

Recommended shape:

```text
A single controlled public/manual observation package containing:

- scope context;
- source family;
- capture method label;
- operator intent limited to observation purpose;
- observed public artifact reference;
- captured_at;
- rights class;
- retention class;
- raw support pointer/hash if raw support is included;
- candidate observation;
- admitted observation concept;
- evidence ID concept;
- claim-use/freshness warning concept;
- explicit no-strategy/no-recommendation boundary.
```

This is closest to the center of Observatory:

```text
observed artifact -> provenance -> rights/retention -> evidence identity -> read-time interpretation boundary
```

---

## Recommended M9 Decision Wording

If accepted later, the decision should say something like:

```text
The M9 first evidence slice is a Controlled Public Manual Observation Package.
It uses controlled fixture/manual-public observation inputs only.
It does not authorize scraping, crawling, browser extension capture, provider pulls, provider admission, customer data, schema design, migrations, API/MCP implementation, dashboard work, or report generation.
```

---

## M10 Schema-Planning Gates for Recommended Slice

M10 should be able to plan schema for this slice against:

```text
H1  Scope isolation
H2  Rights fail-closed
H3  Retention enforcement
H5  No strategy/recommendation storage
H6  CapturePackage validation / observation envelope validation
H9  Freshness / point-in-time claim-use warning
H12 Raw archive integrity if raw support is included
H15 Evidence ID / citation integrity
H19 Append-only observations
H21 Audit-first enforcement
H22 Rollback/recovery expectations
```

M10 should not plan:

```text
provider-admission tables as real provider admission
customer records
dashboard state
strategy/recommendation tables
recurring capture scheduler
SearchClarity reports
LLM direct SQL/API/MCP access
```

---

## M12 Execution Gates for Recommended Slice

M12 should eventually execute hammers for:

```text
missing scope rejected
unknown scope class rejected
customer/private identity rejected
missing rights rejected
unclear rights rejected
missing retention rejected
no-storage retention blocks persistence
strategy/recommendation content rejected
missing required observation-envelope fields rejected
raw hash missing/mismatch rejected if raw support exists
evidence ID stable and not confused with raw/provider IDs
observation mutation rejected
supersession path creates new record, not in-place edit
audit-first behavior for consequential writes
hostile weird input bounded/rejected
```

M12 should not execute provider spend, customer workflow, marketplace scraping, read-tool API/MCP, or recurring capture hammers unless a later milestone explicitly activates those surfaces.

---

## Rejected or Deferred Candidate Families

| Candidate | Status | Reason |
|---|---|---|
| Real DataForSEO provider observation | deferred to M13 | Requires provider admission, spend controls, endpoint recipes, and owner approval |
| Marketplace observation | deferred | Marketplace evidence ceiling and capture posture remain unresolved |
| Customer first-party overlay | deferred to M17 | Customer/private data remains read-time overlay only; not a first storage slice |
| SearchClarity report-support workflow | deferred to M15 | Would pull consumer/report concerns too early |
| Provider disagreement proof | deferred to M16 | Needs base observation path first and OR-A1 fail-closed posture |
| Full typed read API/MCP proof | deferred to M14 | M9 cannot implement or expose read tools |
| Recurring watch panel | deferred to M18 | Requires provider/cost/cadence/duplicate controls |

---

## Owner-Ruling Impact

No new owner ruling is required to compare candidates.

The recommended slice avoids the highest-risk open rulings by default:

- avoids OR-C1 provider funding/spend;
- avoids OR-C5/OR-C6/OR-C7 marketplace capture posture;
- avoids OR-D1 API/MCP authn/authz;
- avoids OR-E1 report-safe customer exposure;
- avoids OR-F1 customer first-party overlays;
- avoids OR-G1 cross-scope aggregation.

Still relevant but not blocking if scoped carefully:

- OR-B1 remains open for mock/stub acceptance; M9 only plans, it does not execute;
- OR-B2 remains open as draft milestone mapping; M9 names applicable hammers for the chosen slice;
- OR-B3 remains open for report-facing freshness; M9 uses freshness/claim warnings but does not generate reports;
- OR-A4 remains open for final report-safe citation behavior; M9 can use evidence ID concept without customer/report-safe handle exposure.

---

## Anti-Drift Notes

Do not infer from this comparison that:

- the first slice is accepted by owner decision;
- schema is authorized;
- implementation is authorized;
- hammers are executed or passed;
- manual capture is admitted as a production capture method;
- public page fixtures authorize crawling or scraping;
- provider-shaped fixtures authorize provider admission;
- raw support means raw payload retention is always allowed;
- evidence IDs are report-safe customer citations;
- customer-facing reports are authorized.

---

## Recommendation

```text
Recommend M9 select C2: Controlled Public Manual Observation Package, optionally with a minimal C4-style query/panel context only if needed for measurement context.
```

The recommended first slice is small, boundary-safe, and useful enough for M10 schema planning.

It proves the Observatory spine before dragging in providers, customers, marketplaces, read tools, dashboards, or recurring capture.
