# M13 Funding and Pre-Submit Owner Checklist

Status: owner action checklist
Authority: none — checklist only; not funding approval, credential approval, provider execution approval, or M13 closure
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-12

---

## Purpose

Provide one bounded checklist for the next owner-controlled M13 actions after fixture-only implementation and hostile-path tests pass.

This checklist does not authorize any action by itself.

## Gate A — Before Funding

Confirm:

```text
[ ] Fixture-only implementation commit is pushed.
[ ] Dynamic evidence-root fix commit is pushed.
[ ] M13 local test evidence records 67 tests passed.
[ ] DataForSEO minimum payment is freshly rechecked in the official interface.
[ ] Owner explicitly approves adding only the current official minimum payment.
[ ] No provider request will be sent during account setup or funding.
[ ] No credentials will be pasted into chat, Git, planning files, or MCP output.
```

If any box is false:

```text
Do not fund yet.
```

## Gate B — Immediately After Funding, Before Credentials Are Used by the CLI

Record without exposing secrets:

```text
funding date and local time
amount funded
currency
official interface used
minimum-payment value shown
owner confirmation
```

Do not record:

```text
card details
billing address
account password
API password
login email if unnecessary
account identifiers beyond what is required locally
```

## Gate C — Exact Pricing Verification

Using the official DataForSEO calculator or authenticated account interface, verify the exact immutable request:

```text
endpoint: /v3/serp/google/organic/live/advanced
keyword: observatory test page
location_code: 2840
language_code: en
device: desktop
os: windows
depth: 10
optional cost-bearing fields: none
```

Record:

```text
[ ] Exact calculated price is shown.
[ ] Exact price is at or below $0.10.
[ ] No depth-above-10 surcharge applies.
[ ] No AI Overview loading surcharge applies.
[ ] No People Also Ask click surcharge applies.
[ ] No extra crawl-page surcharge applies.
[ ] No search-operator multiplier applies.
[ ] One live request is sufficient.
```

If the exact price is unclear or exceeds `$0.10`:

```text
Stop. Do not submit. Amend the decision or seek provider clarification.
```

## Gate D — Account Controls

Inspect the account interface for available controls and record whether each exists:

```text
repetitive-task limit
spend/budget limit
API usage limit
alerting or low-balance notification
credential rotation/revocation controls
```

Enable the narrowest useful controls available without expanding scope.

If no account-level controls exist, record that fact. The CLI ceilings remain mandatory.

## Gate E — Credential Setup

Use only local environment variables:

```text
DATAFORSEO_LOGIN
DATAFORSEO_PASSWORD
```

Confirm:

```text
[ ] Values exist only in the local environment or ignored local configuration.
[ ] Values are not committed.
[ ] Values are not pasted into chat.
[ ] Values are not written to command output, logs, manifests, or screenshots.
[ ] The owner knows how to revoke or rotate them after the probe.
```

## Gate F — Preflight

Run the bounded preflight only after funding, pricing, account controls, and credentials are ready.

The preflight must remain blocked unless all required inputs are present.

Expected immutable request hash:

```text
f0b5410c5cc490b64ec4bb471a92c24647dccf432962fcd952c4070b03b2c4c9
```

Expected duplicate-prevention key:

```text
ba0ecb2b81b3bfb4cc90a3311a285ca02fc17e165ff58ea49ae6768f7b96970d
```

A mismatch means:

```text
Stop. Do not submit.
```

## Gate G — Separate Execution Ruling

Even after a clean preflight, the paid request remains blocked until the owner explicitly authorizes:

```text
one paid request
one billable task
maximum expected cost $0.10
exact immutable request hash
temporary local capture-and-purge posture
```

Funding is not execution approval.

Credentials are not execution approval.

A passing preflight is not execution approval.

## Final Rule

```text
Fund once, verify price, configure limits, protect credentials, run preflight, then stop for the one-request owner confirmation.
No box checked by momentum.
```
