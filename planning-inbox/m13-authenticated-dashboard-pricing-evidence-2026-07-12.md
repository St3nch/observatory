# M13 Authenticated DataForSEO Dashboard Pricing Evidence — 2026-07-12

Status: authenticated account evidence note
Authority: evidence only; does not authorize unattended or bulk execution
Milestone: M13 — Provider Admission and Controlled Pull Plan
Source: owner-uploaded saved HTML from the authenticated DataForSEO API Dashboard

---

## Account State Observed

The saved dashboard shows:

```text
account balance: $50.289579
expenses summary period: 2026-06-12 through 2026-07-12
expenses summary: $0.0000
estimated days to go: approximately 9999 days
```

This supports the owner's statement that the account is funded and unused before the first Observatory pull.

No credential values were copied into this note.

---

## Authenticated SERP Pricing Evidence

The dashboard pricing grid shows the following SERP API prices:

| Endpoint label | Pricing unit | Normal priority | High priority |
|---|---|---:|---:|
| `live/advanced` | first page | $0.0020 | $0.0020 |
| `live/advanced` | second and later pages | $0.0015 | $0.0015 |
| `live/regular` | first page | $0.0020 | $0.0020 |
| `live/html` | first page | $0.0020 | $0.0020 |
| `task_post` | first page | $0.0006 | $0.0012 |
| `screenshot` | per result | $0.0040 | $0.0040 |
| `ai_summary` | per result | $0.0100 | $0.0100 |

For C00, the immutable request uses:

```text
/v3/serp/google/organic/live/advanced
depth: 10
one task
first page only
```

Therefore the authenticated expected base request price is:

```text
$0.0020
```

The existing $0.10 C00 ceiling remains a fail-closed maximum, not the expected price. Any provider-reported or usage-sheet cost above $0.0020 requires review; any cost above $0.10 blocks the campaign.

---

## Account Controls and Navigation Observed

The saved dashboard exposes authenticated navigation to:

```text
API Access
Usage
Errors
Playground
Settings
Documentation
Payments
```

The dashboard also states:

- API credentials are available through the API Access section;
- a graphical API Playground can make real API calls;
- a free Sandbox feature exists for testing and larger request-volume configuration;
- Postman examples and official documentation are available.

The owner additionally confirmed the duplicate-task account control currently permits a maximum of 10 duplicate tasks within one hour. Duplicate tasks above that threshold return DataForSEO error `40205`.

For the calibration phase, the recommended account setting is:

```text
maximum duplicate tasks per hour: 1
```

This is defense in depth only. The Observatory CLI must still refuse an already-recorded duplicate key before any network call.

This is useful for setup and independent verification, but Observatory execution should use its bounded CLI rather than the graphical Playground so request hashing, local manifests, duplicate controls, and raw evidence handling remain deterministic.

---

## Preflight Consequence

C00 no longer has an unresolved exact-price blocker.

The remaining pre-submit blockers are:

```text
credential-safe local environment setup
confirmation that probe-evidence/ is Git-ignored
account Settings review for available request/spend limits
fresh C00 request hash confirmation
explicit one-request owner confirmation
```

---

## Privacy Note

The uploaded dashboard contains account-identifying material. This repo note preserves only the minimum operational evidence needed for M13:

```text
balance
zero-expense baseline
pricing rows
available account control/navigation surfaces
```

It does not preserve credentials, authorization headers, private API passwords, or full dashboard HTML.
