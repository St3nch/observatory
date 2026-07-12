# Decision M13-D2 — DataForSEO Exploratory Campaign Budget and Review Gates

Status: accepted
Date: 2026-07-12
Owner ruling: accepted from explicit owner direction in project chat
Related milestone: M13 — Provider Admission and Controlled Pull Plan
Related files:

- `decisions/2026-07-11-m13-dataforseo-controlled-probe-approval.md`
- `planning-inbox/m13-dataforseo-first-pull-campaign-plan.md`
- `planning-inbox/m13-serp-usage-sheet-reconciliation-spec.md`
- `planning-inbox/m13-campaign-cli-expansion-review.md`
- `planning-inbox/m13-dataforseo-probe-post-pull-and-purge-template.md`

---

## Decision

```text
Reserve the available $50 DataForSEO balance as an exploratory provider-validation budget for The Observatory.

Use the balance to learn DataForSEO endpoint behavior, response shapes, costs, field variability, provider-attributed metrics, error envelopes, and evidence-handling requirements.

Build and fixture-test a campaign-capable CLI that knows a reviewed catalog of immutable candidate recipes.

Begin with one Google Organic Live Advanced billing sentinel, reconcile its provider usage row and response-reported costs, review the payload, and then decide which next campaign recipe to execute.

Do not treat the $50 budget as permission to fire every endpoint automatically.

Each live recipe requires its own completed preflight and explicit owner confirmation immediately before submission.

Review actual data, cost, and shape after every pull during calibration and after each later bounded batch.
```

---

## Budget Authority

Accepted research budget envelope:

```text
Maximum total provider spend: $50.00
```

This is a campaign ceiling, not a spending target and not automatic execution authority.

The provider-reported cumulative cost and the uploaded provider usage sheet are both required witnesses. Any disagreement must be recorded rather than silently reconciled.

Proposed allocation guardrails:

| Stage | Purpose | Maximum stage spend |
|---|---|---:|
| 0 | Billing sentinel and evidence-pipeline calibration | $2.00 |
| 1 | Core SERP surface shape matrix | $8.00 |
| 2 | Device/location/result-family variance | $8.00 |
| 3 | Keyword and provider-metric datasets | $10.00 |
| 4 | AI/GEO answer and mention surfaces | $10.00 |
| 5 | Video, local, merchant, and marketplace candidates | $7.00 |
| Reserve | Repeats justified by provider drift, errors, or missing evidence | $5.00 |
| **Total ceiling** |  | **$50.00** |

Unused stage budget may move only through a recorded review. A stage may stop early.

---

## Execution Authority

This decision authorizes:

```text
campaign planning
immutable recipe catalog implementation
fixture/mock tests
usage-sheet reconciliation tooling
preflight generation
post-pull review tooling
```

This decision does not authorize unattended or bulk execution.

For each live request, the owner must see and confirm:

```text
recipe_id
endpoint
sanitized payload
request SHA-256
current cumulative spend
stage ceiling and remaining budget
exact or conservative maximum expected request cost
no-duplicate result
credential presence without values
local ignored evidence destination
raw-retention deadline
```

The first live request remains the already planned Google Organic Live Advanced sentinel.

---

## Review Cadence

### Calibration mode

For the first three successful provider requests:

```text
one request
then stop
then reconcile usage and costs
then inspect payload and evidence
then choose the next request
```

### Bounded batch mode

After three successful reconciled pulls, the owner may approve a batch containing at most:

```text
3 immutable recipes
$2.00 conservative batch ceiling
zero retries
zero silent substitutions
```

Batch mode may be revoked immediately if cost, usage rows, response shape, rights, retention, or evidence handling differs from expectations.

---

## First-Pull Order

The accepted starting order is:

```text
1. Google Organic Live Advanced desktop billing sentinel.
2. Google Organic Live Advanced mobile comparison.
3. Bing Organic Live Advanced desktop comparison.
4. YouTube Organic Live response-shape comparison.
5. Google Maps Live local-result shape.
6. Google AI Mode Live Advanced answer/citation shape.
7. DataForSEO Labs Google Keyword Overview.
8. DataForSEO Labs Google Keyword Ideas.
```

Only item 1 is the immediate execution candidate. Later items remain campaign candidates until the prior review promotes them.

---

## Data Selection Rule

Early probes use neutral, non-customer, public-interest inputs chosen to exercise the endpoint rather than produce customer intelligence.

The initial vocabulary may include:

```text
observatory test page
what is an observatory
public library
observatory
```

No customer domain, private analytics, customer keyword list, or SearchClarity engagement data may enter M13 exploratory pulls.

---

## Usage-Sheet Rule

The owner-provided `serp-usage.xlsx` currently contains only these headers:

```text
ID
Search Engine
Keyword
Location Code
Language Code
Task set
Task complete
Turnaround time
Cost
IP
```

The workbook is a provider-usage witness. It is not the Observatory manifest and must not become the only record.

For every pull, reconcile:

```text
provider usage ID
recipe_id
request SHA-256
provider task ID
provider top-level cost
provider task-level cost
usage-sheet cost
submitted/completed timestamps
response class
raw payload SHA-256
```

The owner may upload later versions of the workbook. Imports must be read-only unless the owner explicitly asks for a modified copy.

---

## Stop Conditions

Stop campaign execution if:

- cumulative provider-reported spend reaches `$50.00`;
- a proposed request could breach its stage or campaign ceiling;
- the usage sheet and response-reported cost disagree without explanation;
- a duplicate task appears;
- credentials leak into output;
- a recipe changes without review;
- a response contains customer/private data;
- raw evidence cannot be hashed or purged safely;
- provider terms or allowed use become unclear;
- one request triggers more than one billable task unexpectedly;
- a retry, poll, or second call would be required but is not explicitly approved.

---

## Scope

This decision applies to:

- DataForSEO exploratory provider validation;
- the available `$50` account balance;
- immutable candidate-recipe CLI expansion;
- per-pull and bounded-batch review gates;
- provider usage-sheet reconciliation;
- response-shape and cost evidence.

This decision does not apply to:

- recurring capture;
- production monitoring;
- customer data;
- broad provider admission;
- schema creation from provider payloads;
- Postgres or migrations;
- dashboard or API/MCP exposure;
- strategy or recommendation storage;
- customer-facing claims;
- automatic spending of the full balance.

---

## Anti-Drift Notes

Future agents must not infer:

- `$50 available` means `spend $50 immediately`;
- campaign candidates are approved live calls;
- a recipe catalog is a generic provider framework;
- one successful payload authorizes persistence design;
- provider usage cost is the only cost witness;
- response cost fields may be ignored;
- batch mode permits retries or substitutions;
- early neutral inputs may be replaced with customer inputs;
- DataForSEO output is truth.

---

## Final Rule

```text
Use the credits to buy knowledge, not noise.
Every pull must answer a named question.
Every cost must have at least two witnesses where available.
Every payload gets reviewed before the campaign widens.
```
