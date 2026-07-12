# M13 Paid Evidence Review Package

Status: implemented fixture-only evidence organization layer
Authority: organization and derived-evidence handling only; no network execution authority
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-12

---

## Purpose

Preserve paid provider evidence in a form that remains understandable, comparable, and reusable for future Observatory-supported projects without treating one provider response as database schema or truth.

The package is designed around this rule:

```text
Paid raw evidence may be temporary.
Its provenance, shape, costs, review notes, and derived structural evidence must remain organized.
```

## Per-Pull Package

Each reviewed pull receives a stable folder:

```text
probe-evidence/dataforseo/YYYY-MM-DD_<recipe-id>_<safe-suffix>/
```

Generated files:

```text
00-request-manifest.json
02-raw-response.json
03-response-summary.json
04-field-inventory.json
05-item-type-summary.json
06-cost-reconciliation.json
07-review-notes.md
```

The existing purge command will later preserve deletion proof. A future integration step will standardize the final filename as:

```text
08-purge-proof.json
```

## Durable Review Value

The package preserves:

```text
campaign, stage, and recipe identity
provider, endpoint, method, and immutable request
request hash and duplicate-prevention key
capture timestamp and expected price
rights, retention, and claim-use warnings
provider and task status
result count and item-type counts
grouped field inventory and stable shape hash
provider, task, and usage-sheet cost witnesses
conservative cost and disagreement status
human-readable review prompts and promotion gate
```

## Field Organization

Fields are grouped into four review sections:

```text
response
task
result
items
```

Array indexes are normalized to `[]` for structural comparison, while only the first 25 array members are inspected for bounded evidence generation.

This produces a durable field-set hash without claiming that one payload proves a physical schema.

## Cost Reconciliation

The evidence package compares:

```text
expected authenticated price
provider top-level cost
provider task-level cost
usage workbook cost when supplied
```

Status is:

```text
reconciled
review_required
missing_cost_witness
```

The higher credible witness is retained as the conservative observed cost.

## Campaign Index

The package can maintain:

```text
probe-evidence/dataforseo/campaign-index.json
probe-evidence/dataforseo/campaign-review.md
```

Index updates are idempotent by `probe_id`. The Markdown review provides a compact table of recipe, endpoint, status, cost, raw state, and review state.

## CLI Additions

Fixture-only commands:

```text
package-review
campaign-index-add
```

`package-review` accepts only a raw JSON file already inside the approved evidence root. It performs no network request.

`campaign-index-add` updates only derived campaign evidence inside the approved evidence root.

## Boundary

This implementation does not authorize:

```text
provider calls
retries or repeated pulls
unattended capture
Postgres or schema design
customer data
cross-project data export
customer-facing claims
indefinite raw retention
```

Future reuse means a connected LLM or approved consumer may examine preserved evidence later. It does not mean raw provider data is automatically licensed, promoted, copied, or exposed to another system.
