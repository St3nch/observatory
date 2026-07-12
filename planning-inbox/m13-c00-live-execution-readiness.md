# M13 C00 Live Execution Readiness

Status: implementation review
Authority: implementation only; does not authorize the paid C00 request
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-12

---

## Purpose

Record the bounded credential-aware C00 execution path implemented after owner approval to proceed with execution preparation.

This implementation keeps the final paid-submit authority separate.

## Implemented Boundary

The live execution module is limited to:

```text
recipe: C00
provider: DataForSEO
endpoint: /v3/serp/google/organic/live/advanced
method: POST
request count: exactly 1
billable task count: exactly 1
retry count: 0
polling count: 0
timeout: 30 seconds
expected price: $0.002
conservative request ceiling: $0.10
```

No other campaign recipe is executable through this path.

## Credential Handling

Credentials are read only from:

```text
DATAFORSEO_LOGIN
DATAFORSEO_PASSWORD
```

The implementation:

```text
constructs Basic Auth in memory
never prints credential values
never writes Authorization headers to evidence
never stores login or password in manifests
redacts environment credential values from surfaced provider/transport errors
```

## Duplicate and Retry Posture

Before the network transport is invoked, the CLI writes an attempt reservation containing:

```text
probe ID
recipe ID
request hash
duplicate-prevention key
reservation timestamp
retry_permitted: false
```

A matching reservation blocks another C00 attempt.

The reservation remains after a timeout or transport failure. This is intentional because M13 authorizes no automatic retry and does not assume an ambiguous transport failure was unbilled.

## Response Handling

A successful HTTP JSON response is immediately converted into the paid-evidence review package:

```text
00-request-manifest.json
02-raw-response.json
03-response-summary.json
04-field-inventory.json
05-item-type-summary.json
06-cost-reconciliation.json
07-review-notes.md
campaign-index.json
campaign-review.md
```

The response remains provider testimony, not truth.

Raw retention and purge requirements are unchanged.

## Fail-Closed Authority

The source currently preserves:

```text
LIVE_EXECUTION_IMPLEMENTED = True
LIVE_EXECUTION_AUTHORIZED = False
```

Therefore:

```text
live-preflight can inspect local readiness and credentials
live-execute remains blocked before transport
no paid request can occur from this commit
```

A later explicit owner ruling is required before changing the authorization constant and presenting the exact paid-submit command.

## Required Verification

Run the full local test suite:

```powershell
cd C:\dev\observatory
$env:PYTHONPATH = (Join-Path $PWD "src")
python -m unittest discover -s tests
```

Then run credential-aware preflight without the paid confirmation phrase:

```powershell
python -m observatory_dataforseo_probe.cli live-preflight `
  --exact-price 0.002 `
  --account-limits-recorded `
  --evidence-root-ignored
```

Expected remaining blockers before final owner approval:

```text
owner_paid_request_confirmation_missing
network_execution_not_authorized
```

If the current PowerShell session does not contain credentials, `credentials_missing` will also appear.

## Non-Authority

This implementation does not authorize:

```text
the paid C00 request
a second request
a retry
another recipe
unattended execution
recurring capture
schema or Postgres work
cross-project export
raw retention beyond the accepted posture
```
