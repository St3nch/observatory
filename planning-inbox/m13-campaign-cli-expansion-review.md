# M13 Campaign CLI Expansion Review

Status: implementation-planning review
Authority: accepted under M13-D2 for fixture-only campaign catalog and reconciliation tooling; live execution remains separately gated
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-12

---

## Purpose

Review how the existing one-shot DataForSEO safety cage should expand to support a staged exploratory campaign without becoming a generic provider platform or an unattended spending machine.

---

## Current Implementation

The existing module:

```text
src/observatory_dataforseo_probe/
```

already proves:

- immutable Google Organic sentinel recipe;
- request hashing;
- duplicate-key construction;
- authority and price blockers;
- local evidence-root checks;
- credential presence/redaction boundaries;
- response classification;
- field-path fingerprinting;
- raw hash and purge proof;
- permanent no-network fixture posture;
- 67 owner-local tests passing.

The next expansion should preserve those controls while allowing reviewed candidate recipes to be represented and tested.

---

## Recommended Shape

Add a provider-specific campaign catalog, not a generic provider framework.

Candidate implementation paths:

```text
src/observatory_dataforseo_probe/campaign.py
tests/test_dataforseo_campaign.py
```

The campaign layer should provide:

```text
immutable recipe definitions
stage definitions
budget ceilings
promotion states
request hashing
per-recipe duplicate keys
campaign cumulative-cost calculations
usage-sheet reconciliation inputs
no-network campaign previews
```

It should not provide:

```text
a generic HTTP client
arbitrary endpoint flags
arbitrary JSON payload entry
a scheduler
parallel execution
a retry queue
a provider registry
a database adapter
a recurring capture runner
```

---

## Recipe Model

Each recipe should include:

```text
recipe_id
stage_id
family
provider
endpoint
method
request_payload
question_answered
conservative_request_ceiling
requires_prior_recipe
source_documentation
rights_class
retention_class
claim_use_warning
live_status
```

Allowed `live_status` values:

```text
candidate
promoted_for_preflight
executed
reviewed
held
rejected
```

No status change to `promoted_for_preflight` should occur automatically.

---

## Stage Model

Each stage should include:

```text
stage_id
name
learning_objective
spend_ceiling
review_mode
entry_requirements
exit_requirements
```

The implementation must enforce:

- total stage ceilings sum to no more than `$50.00`;
- campaign spend cannot exceed `$50.00`;
- calibration stage is one request at a time;
- the first three successful requests remain one-request review mode;
- later bounded batches contain at most three recipes and a `$2.00` conservative ceiling;
- reserve spend requires an explicit justification field.

---

## Initial Catalog

The first implemented catalog should contain candidates only:

```text
C00 Google Organic desktop sentinel
C01 Google Organic mobile comparison
C02 Bing Organic desktop comparison
C03 YouTube Organic search comparison
C04 Google Maps local-result shape
C05 Google AI Mode answer/citation shape
C06 DataForSEO Labs Keyword Overview
C07 DataForSEO Labs Keyword Ideas
```

C00 may be marked `promoted_for_preflight` only after the owner completes the credential and account-control setup and reviews the exact preflight.

C01–C07 remain `candidate` until prior pull review.

---

## CLI Commands

Fixture-only campaign commands:

```text
python -m observatory_dataforseo_probe.cli campaign-list
python -m observatory_dataforseo_probe.cli campaign-show --recipe-id C00
python -m observatory_dataforseo_probe.cli campaign-budget
python -m observatory_dataforseo_probe.cli campaign-validate
```

Future commands after implementation review:

```text
campaign-preflight --recipe-id C00
usage-inspect --workbook <path>
usage-reconcile --workbook <path> --manifest-root <path>
```

No command may execute a live request until a separate code and owner ruling changes the network boundary.

---

## Required Tests

The campaign catalog implementation must prove:

```text
recipe IDs are unique
stage IDs are valid
all endpoints use HTTPS-relative API v3 paths
all methods are POST for the initial catalog
request payloads are immutable defensive copies
no recipe contains credentials
no recipe contains customer/private markers
C00 matches the accepted sentinel recipe
C01 changes only the reviewed mobile dimensions
C02 uses the verified Bing endpoint
C03 uses the verified YouTube endpoint
C04 uses the verified Google Maps endpoint
C05 uses the verified Google AI Mode endpoint
C06 uses the verified Keyword Overview endpoint
C07 uses the verified Keyword Ideas endpoint
campaign budget totals exactly $50.00
no stage exceeds the campaign ceiling
candidate recipes cannot be executed
campaign listing is deterministic
request hashes are stable
per-recipe duplicate keys differ
unknown recipe IDs fail closed
batch size above three fails
batch conservative cost above $2.00 fails
calibration batch above one recipe fails
```

---

## Usage Workbook Boundary

The uploaded workbook should remain outside the repo and outside source fixtures because it may later contain IP and account-specific data.

For fixture tests, create synthetic workbooks containing the same header schema and fake rows.

The CLI must default to redacting IP values and emitting only:

```text
ip_present: true/false
```

---

## Implementation Sequence

Recommended bounded batch:

1. Add immutable campaign catalog and stage definitions.
2. Add catalog validation and budget calculations.
3. Add CLI list/show/budget/validate commands.
4. Add synthetic usage-sheet parser/reconciliation utilities.
5. Add fixture tests.
6. Run full unittest suite locally.
7. Record implementation evidence.
8. Prepare C00 credential/account setup instructions.
9. Generate C00 preflight.
10. Stop for explicit one-request owner confirmation.

Steps 1–7 require no provider calls.

---

## Review Disposition

```text
Campaign CLI expansion is justified.
Provider-specific immutable catalog is preferred.
Generic provider framework remains forbidden.
Usage-sheet integration must be read-only and privacy-safe.
Live execution remains disabled until separate acceptance.
```

---

## Final Rule

```text
The CLI may know the campaign.
It may explain the next pull.
It may prove the budget and blockers.
It may not decide to spend.
```
