# M13 DataForSEO Official Verification — 2026-07-11

Status: planning verification note
Authority: none — source-grounded M13 input only; not owner acceptance, funding approval, CLI implementation approval, provider-call authority, or provider admission
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date checked: 2026-07-11
Decision reviewed: `decisions/2026-07-11-m13-dataforseo-controlled-probe-approval.md`

---

## Purpose

Verify the proposed one-request DataForSEO probe against current official DataForSEO documentation, pricing, terms, and privacy materials before the owner decides whether to accept, amend, or reject the proposed decision.

This note verifies proposal fields only.

It does not authorize:

```text
credits
use of existing credits
CLI implementation
provider calls
raw payload capture
Postgres
schema
migrations
```

---

## Official Sources Checked

- DataForSEO API documentation — Live Google Organic SERP Advanced:
  `https://docs.dataforseo.com/v3/serp/google/organic/live/advanced/`
- DataForSEO general pricing:
  `https://dataforseo.com/pricing`
- DataForSEO SERP API pricing:
  `https://dataforseo.com/pricing/serp`
- DataForSEO Terms of Service:
  `https://dataforseo.com/terms-of-service`
- DataForSEO Privacy Policy:
  `https://dataforseo.com/privacy-policy`

---

## Verification Summary

```text
Endpoint existence: verified
One-live-request shape: verified
One task per live call: verified
Proposed keyword field: valid
Proposed location_code field: valid
Proposed location_code 2840 example: present in official docs
Proposed language_code en: valid
Proposed device desktop: valid
Proposed os windows with desktop: valid
Proposed depth 10: valid and default-cost boundary
General minimum payment $50: verified
Duplicate-task risk and account controls: verified
Provider-side API task retention 365 days: verified
SERP usage restriction: verified
Exact current request price: not conclusively verified from retrievable official page text
Owner acceptance readiness: blocked until exact current price is confirmed through official calculator/account interface
```

---

## Endpoint Verification

The official API documentation currently identifies:

```text
POST https://api.dataforseo.com/v3/serp/google/organic/live/advanced
```

The documentation states that each Live SERP API call can contain only one task and that the account is charged for each request.

Disposition:

```text
The proposed endpoint is current and suitable for the one-request/no-polling probe shape.
```

No endpoint substitution is permitted without amending the proposed decision.

---

## Request-Field Verification

### keyword

Official status:

```text
required string field
```

The proposed value:

```text
observatory test page
```

contains none of the special search operators that the official docs warn may multiply the charge.

Disposition:

```text
valid proposal field
```

### location_code

Official status:

```text
integer field; required when location_name or location_coordinate is not supplied
```

The official endpoint documentation uses:

```text
2840
```

as an example and returns it in the documented United States-style Google context.

Disposition:

```text
valid proposal field
```

Before execution, the accepted preflight must still confirm from the official location list or calculator that `2840` remains the intended United States location.

That verification must not be performed through a paid endpoint merely to validate the proposal unless separately authorized. Prefer official documentation, calculator, account UI, or a documented free location source.

### language_code

Official status:

```text
en is a documented example value
```

Disposition:

```text
valid proposal field
```

### depth

Official status:

```text
optional integer
default: 10
maximum: 200
billing applies per SERP containing up to 10 results
values above 10 may create additional charges
```

Proposed value:

```text
10
```

Disposition:

```text
valid and appropriately bounded
```

The proposal must not increase depth above 10.

### device

Official status:

```text
optional string
allowed: desktop, mobile
default: desktop
```

Proposed value:

```text
desktop
```

Disposition:

```text
valid proposal field
```

### os

Official status:

```text
optional string
for desktop: windows or macos
default for desktop: windows
```

Proposed value:

```text
windows
```

Disposition:

```text
valid proposal field
```

Explicitly setting the value is preferable to silently relying on a default.

### Optional cost-bearing fields

The official documentation identifies optional fields that can create additional charges, including asynchronous AI Overview loading, People Also Ask clicks, additional crawl pages, deeper result depth, or target-based crawling behavior.

Disposition:

```text
All optional cost-bearing or scope-expanding fields must be omitted.
```

The proposed request must not set:

```text
load_async_ai_overview
people_also_ask_click_depth
max_crawl_pages
stop_crawl_on_match
search operators that multiply task cost
or any other unnamed cost-bearing option
```

---

## Response-Evidence Verification

The official endpoint response shape documents:

```text
version
status_code
status_message
time
cost
tasks_count
tasks_error
tasks[].id
tasks[].status_code
tasks[].status_message
tasks[].time
tasks[].cost
tasks[].result_count
tasks[].path
tasks[].data
tasks[].result
```

Disposition:

```text
The proposed manifest and field-summary requirements correctly target the official envelope fields needed for cost, status, error, task, request-context, and payload-shape evidence.
```

The response's top-level and task-level `cost` fields must both be captured and compared.

---

## Funding Verification

The official general pricing page currently states:

```text
minimum payment amount: $50
```

Disposition:

```text
The proposed $50 expected minimum funding value is current as of 2026-07-11.
```

This is verification only.

It does not authorize adding credits.

If funding occurs on a later date, the minimum must be checked again immediately before the owner performs the funding action.

---

## Exact Probe Price Verification

The official endpoint documentation states that the account is charged for each request and directs users to the pricing page/calculator.

The retrievable official SERP pricing page did not expose a sufficiently reliable exact current price for the proposed Google Organic Live Advanced request in its static text during this verification pass.

The endpoint documentation includes an example response with a historical/example cost value, but an example response is not reliable authority for the current price.

Disposition:

```text
Exact current request price remains unresolved.
```

Owner timing ruling recorded 2026-07-12:

```text
Exact request pricing may be verified after the owner adds credits, using the authenticated account interface or official calculator, but it must still be confirmed before any paid request is sent.
```

This timing ruling does not itself authorize funding, use of existing credits, CLI implementation, credentials, or a provider request.

The verification record must preserve:

```text
verification date and time
official interface used
endpoint/mode
request fields entered
calculated unit price or maximum expected charge
proof that optional surcharges are absent
operator
```

A screenshot or owner-authored verification note may be used if it contains no credentials, account identifiers, payment data, or private account details.

If the calculator/account cannot provide a clear price:

```text
Do not accept for execution.
Do not fund for this probe.
Seek provider clarification or amend the plan.
```

---

## Duplicate and Account-Control Verification

The current Terms of Service state that identical API tasks are a user-side error and note that the account dashboard provides options to limit repetitive task setting.

Disposition:

```text
The proposed no-repeat duplicate key and account-level limit requirement remain necessary and source-supported.
```

No refund assumption may be used as a safety control.

---

## Rights and Usage Verification

The current Terms of Service restrict use of SERP data in ways that compete with or adversely affect the business interests of the originating search engine providers.

Disposition:

```text
The proposed internal payload-shape inspection purpose remains narrower and safer than republication, resale, search-engine substitution, or broad SERP-database use.
```

This note does not provide legal advice or broad usage clearance.

The accepted decision, if any, must preserve:

```text
one internal probe only
no republication
no customer-facing output
no broad SERP archive
no recurring capture
no provider-as-truth treatment
```

---

## Provider-Side Retention Verification

The current Privacy Policy states that DataForSEO stores API task data for 365 days and deletes stored data older than 365 days.

Disposition:

```text
Provider-side retention is verified.
Observatory-side raw retention rights remain a separate decision.
```

The provider's 365-day retention does not authorize Observatory to retain raw payloads for 365 days.

The proposed Observatory posture remains:

```text
capture_and_purge_raw
local only
Git-ignored
no cloud upload
maximum seven calendar days
purge sooner once the summary is accepted
```

That posture remains proposed, not approved.

---

## Proposal Corrections Required

No endpoint or request-field correction is required based on the current official endpoint documentation.

One pre-submit blocker must remain explicit:

```text
Exact current price for the exact proposed request must be verified through the official calculator or authenticated account interface after funding if necessary, but before any request is sent.
```

Recommended clarification for later decision acceptance:

```text
All unnamed optional fields are omitted.
No optional cost-bearing feature is enabled.
Top-level and task-level response cost fields are both recorded.
```

---

## Readiness Result

### Ready for owner review

```text
endpoint
one-live-request mode
one-task shape
keyword
location_code proposal
language_code
device
os
depth 10
$50 current minimum payment evidence
duplicate-task controls
response status/cost manifest fields
provider-side 365-day retention evidence
narrow internal-use posture
```

### Still unresolved before funding or execution

```text
owner acceptance of funding and the narrow probe decision
exact current calculated price for the exact proposed request before submission
confirmation that location_code 2840 remains the intended United States context at execution time
account-level repetitive-task/spend-control configuration
owner acceptance of the temporary local capture-and-purge posture
```

### Still forbidden

```text
adding credits
using existing credits
CLI implementation
provider request
raw response capture
Postgres
schema
migrations
```

---

## Recommended Next Step

The next safe action is owner review of the proposed decision and this verification note.

Before accepting the proposed decision for execution, the owner must either:

```text
A. provide/record official calculator or account-interface price confirmation within the $0.10 ceiling; or
B. leave the decision proposed and keep the provider machine off.
```

No implementation work should begin merely because the endpoint and fields were verified.

---

## Final Rule

```text
The endpoint is real.
The request fields are valid.
The $50 minimum is current.
The exact request price is not yet pinned down.
No price proof, no acceptance for execution.
No acceptance, no credits, no code, no call.
```
