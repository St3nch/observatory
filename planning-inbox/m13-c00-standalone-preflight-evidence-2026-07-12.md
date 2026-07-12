# M13 C00 Standalone Preflight Evidence — 2026-07-12

Status: owner-local execution evidence
Authority: evidence only — not provider execution approval and not M13 closure
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-12

---

## Command

```powershell
cd C:\dev\observatory
$env:PYTHONPATH = (Join-Path $PWD "src")
python -m observatory_dataforseo_probe.cli preflight `
  --exact-price 0.002 `
  --account-limits-recorded `
  --evidence-root-ignored
```

## Owner-Reported Result

```text
status: blocked
exact_price_usd: 0.002
maximum_expected_cost_usd: 0.1
network_execution_authorized: false
```

Remaining blockers:

```text
funding_not_authorized
network_execution_not_authorized
credentials_missing
```

Resolved inputs confirmed by the standalone run:

```text
exact price recorded
account limits recorded
evidence root treated as Git-ignored
request payload hash matched
duplicate prevention key matched
```

Immutable request hash:

```text
f0b5410c5cc490b64ec4bb471a92c24647dccf432962fcd952c4070b03b2c4c9
```

Duplicate-prevention key:

```text
ba0ecb2b81b3bfb4cc90a3311a285ca02fc17e165ff58ea49ae6768f7b96970d
```

Generated-at value reported by the CLI:

```text
2026-07-12T14:09:52.367023+00:00
```

## Interpretation

The standalone preflight behaved exactly as designed for the current fixture-only authority boundary.

The `credentials_missing` blocker does not prove that owner credentials are absent. The current CLI intentionally hardcodes `credentials_present=False` and does not inspect environment variables yet.

The `funding_not_authorized` blocker reflects the current fixture-only CLI input wiring, even though authenticated funding evidence is preserved separately.

The `network_execution_not_authorized` blocker is the decisive execution boundary. No provider request was sent.

## Disposition

```text
C00 request shape: confirmed
C00 exact expected price: confirmed
Account controls: confirmed separately and represented in preflight
Evidence-root gate: passed
Duplicate key: confirmed
Network execution: blocked
Provider request: not sent
Next step: implement a separately authorized credential-aware, one-request execution path without weakening the existing safety cage
```
