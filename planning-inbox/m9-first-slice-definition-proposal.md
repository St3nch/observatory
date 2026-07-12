# M9 First-Slice Definition Proposal

Status: planning / proposed first-slice definition
Authority: none — advisory proposal only; becomes binding only through an owner decision or M9 closure record
Purpose: define the recommended M9 first evidence slice in enough detail for owner review and later M10 schema planning
Date: 2026-07-10
Reviewer: ChatGPT / Observatory Steward

---

## Proposal Question

Should M9 select the Controlled Public Manual Observation Package as the first evidence slice for Observatory?

---

## Source Inputs

- `ROADMAP.md`
- `ACTIVE_CONTEXT.md`
- `02-boundaries.md`
- `contracts/README.md`
- all thirteen M7 contract drafts by index coverage
- `hammers/hammer-matrix-v0-1.md`
- `hammers/acceptance-gate-policy-v0-1.md`
- `planning-inbox/m8-hammer-planning-review.md`
- `planning-inbox/m9-first-slice-candidate-comparison.md`
- `planning-inbox/owner-ruling-tracker.md`

---

## M9 Boundary

This proposal does not authorize:

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

This proposal defines a candidate slice only.

---

## Proposed First Slice

```text
Controlled Public Manual Observation Package
```

### Short Description

A bounded first evidence slice that represents one controlled public/manual observation package as Observatory evidence.

The slice starts with a manually supplied public artifact fixture and tracks it through the core evidence spine:

```text
observed public artifact
-> observation envelope
-> provenance / scope / rights / retention labels
-> raw support pointer/hash if included
-> candidate observation
-> admitted observation concept
-> evidence ID concept
-> claim-use / freshness warning concept
```

The slice is designed to prove the Observatory spine before introducing providers, customer data, marketplace capture, read APIs, dashboards, recurring capture, or strategy workflows.

---

## Proposed Positive Path

The positive path should contain one controlled public/manual observation package with these conceptual elements:

| Element | Purpose | Notes |
|---|---|---|
| Scope context | Prove every observation belongs to an explicit allowed scope | Use non-customer/private fixture identity |
| Scope class | Prove scope classification exists before admission | Prefer `internal` or non-customer fixture context for first slice |
| Source family | Identify the type of surface observed | Generic public web / controlled public fixture only |
| Capture method label | Distinguish manual controlled fixture from scraping/crawling/provider capture | Must not imply production capture runner |
| Operator intent | Record why the observation was captured | Observation purpose only; no strategy |
| Observed artifact reference | Identify the public artifact observed | No private dashboard, customer account, or marketplace ambiguity |
| Captured timestamp | Preserve point-in-time nature | Required for freshness and claim-use warnings |
| Rights class | Fail closed on unclear rights | Must be present before admission |
| Retention class | Fail closed on unclear retention | Must be present before admission |
| Raw support pointer/hash | Prove raw support integrity if raw support is included | Pointer/hash requirement only; no raw retention assumption |
| Candidate observation | Represent the parsed observation candidate | Candidate is not admitted evidence until validated |
| Admitted observation concept | Represent validated observation | Planning concept only until M12 implementation |
| Evidence ID concept | Preserve stable evidence identity | Not a report-safe customer handle |
| Freshness / claim-use warning | Prevent overclaiming point-in-time evidence | Historical/point-in-time caveat |
| Boundary rejection metadata | Show why rejected inputs are rejected | No strategy/customer/private/provider-spend bypass |

---

## Positive-Path Wording Constraints

The slice may say:

```text
A controlled public artifact was observed at time T under scope S, with rights class R, retention class K, and evidence identity E.
```

The slice must not say:

```text
This page should be optimized.
This keyword should be targeted.
This provider is correct.
This evidence proves current ranking forever.
This artifact is customer report-safe.
This manual capture method is now approved for production collection.
```

---

## Explicit Exclusions

The selected first slice must exclude:

```text
paid provider pulls
DataForSEO live calls
Ahrefs/Semrush work
provider admission
marketplace scraping
browser-extension capture
customer GSC/GA4/Etsy/Shopify/private analytics
customer records
SearchClarity reports
report delivery state
strategy recommendations
content recommendations
recurring capture
scheduler behavior
dashboard/operator console
API/MCP implementation
LLM direct SQL access
```

---

## Recommended Fixture Boundaries

The first slice should use a fixture artifact that is:

- public or controlled by the owner;
- non-customer-private;
- non-marketplace unless later explicitly approved;
- not a provider response;
- not a customer dashboard export;
- not a search-console/private analytics export;
- not a report or recommendation artifact;
- safe to discuss as a manual fixture without implying scraping/crawling approval.

Preferred examples:

```text
owner-controlled public test page fixture
static public HTML fixture created for Observatory tests later
small public-page metadata fixture with no private/customer data
```

Avoid for first slice:

```text
real customer page from a paid engagement
Etsy/Fiverr/marketplace listing
SERP scrape
AI answer-surface capture
DataForSEO response
GSC/GA4/Etsy Stats/Shopify analytics export
```

---

## Applicable Hammers

The proposed slice should carry these hammers forward into M10/M12 planning:

| Hammer | Applies? | Why |
|---|---:|---|
| H1 Scope isolation | yes | Every observation needs a safe scope and no customer identity leakage |
| H2 Rights fail-closed | yes | Missing/unclear rights must block admission |
| H3 Retention enforcement | yes | Missing/forbidden retention must block persistence or raw support |
| H5 No strategy/recommendation storage | yes | Public artifact observations must not store recommendations |
| H6 CapturePackage validation / observation envelope validation | yes | The package must not become a payload dump |
| H9 Freshness / claim-use warning | yes | Point-in-time evidence must not support overstrong current claims |
| H12 Raw archive integrity | yes if raw support included | Pointer/hash behavior must be planned if raw support exists |
| H15 Evidence ID / citation integrity | yes | Evidence IDs must not be confused with raw IDs/report-safe handles |
| H18 Hostile weird input | yes | Bad URLs, malformed payloads, huge payloads, hidden strategy text must reject |
| H19 Append-only observations | yes | Admitted observations must not be overwritten/backdated |
| H21 Audit-first enforcement | yes | Consequential admission/purge/supersession later needs audit-first proof |
| H22 Rollback/recovery expectations | planning impact | M10 must avoid schema designs that block restore/rollback proof |

---

## Deferred Hammers

| Hammer | Deferred posture | Reason |
|---|---|---|
| H4 Customer-private rejection | include rejection fixtures later; not positive path | First slice avoids customer/private data |
| H7 Provider spend / duplicate tasks | deferred | No paid provider task in first slice |
| H8 Provider attribution / disagreement | deferred | No provider comparison in first slice |
| H10 AI/GEO overclaim | deferred | No AI answer-surface evidence in first slice |
| H11 Marketplace evidence ceiling | deferred | First slice avoids marketplace surfaces |
| H13 Provider drift / parser safety | deferred | No provider payload in first slice |
| H14 Query panel immutability | optional | Include only if minimal panel context is needed |
| H16 Consumer request / overlay | deferred | No consumer workflow or overlay in first slice |
| H17 LLM / agent access | deferred | Read API/MCP is M14 |
| H20 Concurrency safety | later execution if writes can race | M9 can note it; M12/M13 prove it where relevant |

---

## Optional Companion: Minimal Query / Panel Context

The first slice may include a minimal C4-style context wrapper only if needed to explain measurement intent:

```text
query_panel_id concept
query_panel_version concept
one panel item concept
one panel run concept
```

Rules:

- The panel must not become a keyword strategy list.
- The panel must not imply recurring capture.
- The panel must not require provider calls.
- The panel must not store recommendations or priorities.
- The panel is optional; the core first slice is the observation package.

If including panel context makes the first slice too abstract or broad, defer H14 to M10/M12 planning.

---

## M10 Schema-Planning Gates

If this proposal is accepted, M10 should plan schema only for the selected slice and must account for:

```text
H1  Scope isolation
H2  Rights fail-closed
H3  Retention enforcement
H5  No strategy/recommendation storage
H6  Observation envelope / CapturePackage-style validation
H9  Freshness and point-in-time claim-use warning
H12 Raw support pointer/hash integrity if raw support exists
H15 Evidence ID / citation integrity
H18 Hostile weird input boundary expectations
H19 Append-only observation behavior
H21 Audit-first enforcement for consequential changes
H22 Rollback/recovery expectations
```

M10 must not plan schema for:

```text
provider admission
paid provider task execution
customer records
customer private analytics
SearchClarity report delivery
strategy/recommendation storage
recurring capture
API/MCP tools
dashboard state
cross-scope aggregate analysis
```

---

## M12 Execution Gates

If this proposal is accepted, M12 should eventually execute hammers proving at least:

```text
missing scope rejected
unknown scope class rejected
customer/private identity rejected
missing rights rejected
unclear rights rejected
missing retention rejected
no-storage retention blocks persistence
strategy/recommendation content rejected
missing observation-envelope fields rejected
candidate observation cannot become admitted evidence before validation
raw hash missing/mismatch rejected if raw support exists
evidence ID stable and not confused with raw/provider/report-safe IDs
observation mutation rejected
captured_at/provenance mutation rejected
supersession creates new record, not in-place edit
audit record required for consequential admission/supersession/purge later
hostile weird input is bounded/rejected
```

M12 should not execute provider spend, customer workflow, marketplace capture, full read API/MCP, or recurring capture hammers unless a later milestone explicitly activates those surfaces.

---

## M9 Closure Readiness

This proposal is enough for M9 closure only if the owner accepts or records a decision selecting the Controlled Public Manual Observation Package as the first slice.

Before closure, the project should still record:

- accepted first-slice name;
- rejected/deferred candidate families;
- applicable hammers;
- deferred hammers;
- M10 schema-planning gates;
- M12 execution gates;
- explicit non-authorization boundary.

---

## Open Owner-Ruling Interaction

This proposed slice avoids most open owner rulings by design.

Still relevant:

- OR-B1 remains open: mock/stub hammers may support planning but cannot satisfy implementation acceptance.
- OR-B2 remains open: this proposal names applicable hammers for the slice but does not make all future milestone gates binding by itself.
- OR-B3 remains open: point-in-time freshness warnings apply, but report-facing automatic blocks remain M15+.
- OR-A4 remains open: evidence ID behavior can be planned, but report-safe customer citation behavior remains deferred.

No provider-spend, customer-data, marketplace, or read-tool owner ruling is required for this proposal because the proposed slice avoids those surfaces.

---

## Decision Text Candidate

If the owner accepts this proposal, the future decision/closure text can say:

```text
M9 selects the Controlled Public Manual Observation Package as the first evidence slice.
The selected slice is a controlled fixture/manual-public observation path only.
It does not authorize scraping, crawling, browser-extension capture, provider pulls, provider admission, customer data, schema design, migrations, API/MCP implementation, dashboard work, report generation, or strategy/recommendation storage.
M10 may plan schema only for this selected slice.
```

---

## Anti-Drift Notes

Do not infer from this proposal that:

- M9 is closed;
- the owner has accepted the slice;
- schema is authorized;
- implementation is authorized;
- hammers are passed;
- manual capture is a production capture method;
- public fixture observation authorizes scraping or crawling;
- raw support means raw retention is always allowed;
- evidence IDs are report-safe customer citations;
- read API/MCP work is authorized;
- customer-facing reports are authorized.

---

## Recommendation

```text
Recommend accepting Controlled Public Manual Observation Package as the M9 first evidence slice.
```

This first slice is small enough to avoid provider/customer/marketplace/read-tool complexity and concrete enough to give M10 schema planning a real target.
