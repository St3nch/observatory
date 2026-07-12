# M13 SERP Usage Sheet Reconciliation Specification

Status: planning specification
Authority: accepted under M13-D2 for read-only workbook reconciliation tooling; not provider execution authority
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-12
Input witness: owner-uploaded `serp-usage.xlsx`

---

## Purpose

Define how The Observatory reconciles DataForSEO provider usage rows against local campaign manifests and response-reported cost fields.

The usage sheet is a provider/account witness.

It is not:

```text
the raw response
the Observatory observation record
the sole cost authority
a customer report
a provider-truth ledger
```

---

## Initial Workbook Inspection

The workbook uploaded on 2026-07-12 contains one worksheet:

```text
Main
```

The sheet is empty except for these headers:

| Column | Header |
|---:|---|
| A | ID |
| B | Search Engine |
| C | Keyword |
| D | Location Code |
| E | Language Code |
| F | Task set |
| G | Task complete |
| H | Turnaround time |
| I | Cost |
| J | IP |

This establishes the baseline:

```text
zero populated usage rows before the M13 campaign
```

The workbook must be hashed when each version is reviewed so later uploads can be compared to a known baseline.

---

## Read-Only Rule

Default behavior:

```text
read workbook
inspect rows
hash workbook
compare with prior upload
produce a separate sanitized reconciliation report
never overwrite the owner's provider usage workbook
```

A modified workbook may be created only if the owner explicitly requests one.

The original uploaded workbook must never be committed to the public repo if it contains account-specific IP addresses or other private account metadata.

---

## Workbook-Level Evidence

For every uploaded version, record:

```text
source_file_name
source_file_sha256
source_file_bytes
uploaded_at
reviewed_at
worksheet_names
header_fingerprint
populated_row_count
new_row_count
changed_row_count
removed_row_count
contains_ip_values
review_actor
```

The sanitized repo note may record only:

```text
file hash
row counts
match/reconciliation results
cost totals
anomaly summaries
```

Do not commit raw IP values.

---

## Row Normalization

Each populated row should be normalized into a local transient structure:

```text
usage_row_number
usage_id
search_engine
keyword
location_code
language_code
task_set_at
task_completed_at
turnaround_time
cost
ip_present
row_fingerprint
```

Normalization rules:

- preserve the original displayed values separately from parsed values;
- parse dates/times only when the workbook value is unambiguous;
- parse cost as decimal currency, never binary floating point in durable evidence;
- trim incidental surrounding whitespace from text for matching;
- do not lowercase or otherwise alter keyword content in the source witness;
- record whether IP is present, but redact its value from repo-safe output;
- hash the canonical sanitized row for change detection.

---

## Campaign Match Keys

A usage row should be matched against a local campaign manifest using the strongest available evidence in this order:

### Tier 1 — Direct identifiers

```text
provider task ID == usage ID
```

If direct identifiers match, other fields still undergo consistency checks.

### Tier 2 — Recipe and context match

```text
search engine
keyword
location code
language code
task-set timestamp window
provider-reported cost
```

### Tier 3 — Temporal/cost inference

Only when the provider usage ID cannot be linked directly:

```text
single unmatched local request
single new usage row
compatible timestamp interval
compatible endpoint/search engine
compatible keyword/location/language
compatible cost
```

Tier 3 matches must be labeled:

```text
inferred_match
```

They may not be presented as direct task-ID proof.

---

## Match Status Vocabulary

```text
direct_match
inferred_match
ambiguous_match
usage_row_without_local_manifest
local_manifest_without_usage_row
field_mismatch
cost_mismatch
duplicate_usage_row
changed_historical_row
removed_historical_row
```

Every new row receives exactly one primary status and zero or more anomaly flags.

---

## Cost Reconciliation

For each campaign pull compare:

```text
provider response top-level cost
provider task-level cost
usage-sheet row cost
local preflight maximum expected cost
campaign cumulative spend
stage cumulative spend
```

Cost disposition:

```text
reconciled_exact
reconciled_with_rounding
response_internal_disagreement
usage_response_disagreement
missing_usage_cost
missing_response_cost
above_preflight_ceiling
above_stage_ceiling
above_campaign_ceiling
```

Rules:

- top-level and task-level response cost disagreement is never silently resolved;
- a usage-sheet cost mismatch is retained as provider-witness disagreement;
- cumulative spend uses the most conservative credible value until disagreement is resolved;
- the campaign stops if conservative cumulative spend could exceed `$50.00`;
- the first successful pull must be reconciled before a second live pull.

---

## Baseline and Delta Logic

The empty 2026-07-12 workbook is the initial baseline.

For each later upload:

1. Hash the entire workbook.
2. Confirm the expected `Main` sheet and header fingerprint.
3. Count populated rows.
4. Normalize and fingerprint each populated row.
5. Compare usage IDs and row fingerprints with the prior upload.
6. Identify new, changed, missing, and duplicate rows.
7. Match new rows to local manifests.
8. Recompute reconciled and conservative cumulative spend.
9. Produce a sanitized reconciliation result.
10. Hold further pulls if any calibration row is ambiguous or mismatched.

A historical row changing after it was previously reconciled is a material anomaly.

---

## Sanitized Reconciliation Output

Recommended local output:

```text
probe-evidence/dataforseo/reconciliation/<timestamp>/usage-reconciliation.json
probe-evidence/dataforseo/reconciliation/<timestamp>/usage-reconciliation.md
```

Recommended repo-safe summary after review:

```text
planning-inbox/m13-dataforseo-usage-reconciliation-YYYY-MM-DD.md
```

A repo-safe summary may contain:

```text
workbook SHA-256
row counts
new usage IDs if not sensitive
recipe IDs
match statuses
response costs
usage costs
cumulative spend
anomaly descriptions
next-pull disposition
```

It must not contain:

```text
credentials
authentication headers
raw provider payloads
raw IP addresses
payment details
private account identifiers beyond reviewed task IDs
```

---

## CLI Requirements

The campaign CLI should eventually expose fixture-only commands:

```text
usage inspect --workbook <path>
usage baseline --workbook <path>
usage reconcile --workbook <path> --manifest-root <path>
usage diff --previous <path> --current <path>
```

Until network execution is separately enabled, these commands operate only on local files and manifests.

Required behavior:

- reject missing or reordered required headers unless explicitly versioned;
- tolerate empty baseline workbooks;
- reject malformed cost/date values with row-specific evidence;
- never print raw IP values by default;
- support an explicit sanitized JSON output;
- compute workbook and row fingerprints;
- preserve direct versus inferred match confidence;
- fail closed on ambiguous calibration matches.

---

## Required Fixture Tests

At minimum:

```text
empty workbook baseline accepted
expected headers fingerprinted
missing header rejected
renamed header rejected
extra unrelated sheet tolerated and reported
one new row detected
multiple new rows detected
changed historical row detected
removed row detected
duplicate usage ID detected
exact direct task-ID match
inferred temporal match
ambiguous match blocks
response/usage exact cost reconciliation
rounding-only reconciliation
cost mismatch blocks calibration progression
missing response cost flagged
missing usage cost flagged
IP present but redacted
workbook hash stable for identical bytes
row fingerprint stable for equivalent normalized values
```

Tests must use synthetic workbooks or sanitized fixtures only.

---

## First Live Reconciliation Gate

After campaign recipe C00 executes, the owner uploads the populated workbook.

The first reconciliation must answer:

```text
Did exactly one new usage row appear?
Does its ID match the provider task ID?
Do engine, keyword, location, and language match the immutable recipe?
Do task-set and task-complete times align with the local manifest?
Does usage-sheet cost match top-level and task-level response cost?
Does the IP column contain a value that must remain private?
What is the conservative cumulative campaign spend?
May recipe C01 be promoted?
```

No second live request proceeds until this gate has a recorded disposition.

---

## Final Rule

```text
The usage sheet tells us what the account says happened.
The response tells us what the API says happened.
The local manifest tells us what we intended and recorded.
The Observatory keeps all three witnesses distinct and reconciles their disagreement.
```
