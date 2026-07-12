# M13 Funding and Pre-Submit Owner Checklist

Status: owner action checklist
Authority: none — checklist only; not funding approval, credential approval, provider execution approval, or M13 closure
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-12

---

## Purpose

Provide one bounded checklist for the next owner-controlled M13 actions after fixture-only implementation and hostile-path tests pass.

This checklist does not authorize any action by itself.

## Gate A — Funding Status

Authenticated dashboard evidence supplied by the owner confirms:

```text
[x] Fixture-only implementation commit is pushed.
[x] Dynamic evidence-root fix commit is pushed.
[x] M13 local test evidence records 67 tests passed.
[x] DataForSEO account is funded.
[x] Current balance observed: $50.289579.
[x] Expenses observed for 2026-06-12 through 2026-07-12: $0.0000.
[x] No provider request was sent during setup or funding.
[x] No credentials were preserved in the repo evidence note.
```

Evidence:

```text
planning-inbox/m13-authenticated-dashboard-pricing-evidence-2026-07-12.md
```

## Gate B — Funding Evidence Preserved

The repo preserves only:

```text
authenticated balance
zero-expense baseline
pricing evidence
available account navigation/control surfaces
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

Authenticated dashboard pricing evidence now resolves the C00 base price:

```text
endpoint: /v3/serp/google/organic/live/advanced
pricing row: live/advanced
pricing unit: first page
normal priority: $0.0020
high priority: $0.0020
C00 depth: 10
expected pages: one
expected base request price: $0.0020
```

Confirmed:

```text
[x] Authenticated exact endpoint-family price is shown.
[x] Expected price is below the $0.10 hard ceiling.
[x] No second-page charge is expected at depth 10.
[x] No optional AI summary or screenshot feature is present.
[x] No extra click or crawl feature is present.
[x] No search-operator multiplier is present.
[x] One live request is sufficient.
```

Pre-submit rule:

```text
Expected cost: $0.0020.
Any higher provider or usage-sheet cost requires review.
Any cost above $0.10 blocks the campaign.
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
