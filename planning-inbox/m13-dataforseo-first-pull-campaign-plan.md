# M13 DataForSEO First-Pull Campaign Plan

Status: accepted planning input under M13-D2
Authority: campaign sequence and review plan; individual live calls still require per-request owner confirmation
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-12
Budget ceiling: $50.00 total provider spend

---

## Purpose

Use the funded DataForSEO account to learn what the provider actually returns, how it bills, how endpoint families differ, and what evidence The Observatory can safely preserve.

The campaign is not a data-hoarding exercise.

Each pull must answer at least one of these questions:

```text
What request shape does this endpoint accept?
What response envelope and nested result types does it return?
What does DataForSEO report as the cost?
How does the provider usage sheet represent the same task?
Which fields are testimony, estimates, scores, or direct result attributes?
Which fields are stable enough to promote later?
Which fields should remain raw-support-only?
What rights, retention, and claim-safety caveats attach to the endpoint?
What changed across device, engine, surface, or query type?
```

---

## Campaign Method

```text
calibrate -> compare -> widen -> review -> preserve only what is justified
```

The campaign begins in strict one-request review mode.

For the first three successful pulls:

1. Run one immutable recipe.
2. Capture and hash the response.
3. Record top-level and task-level cost.
4. Export or upload the latest provider usage sheet.
5. Reconcile task ID, timestamps, keyword, location, language, cost, and IP witness.
6. Classify the response shape.
7. Produce a field-path summary and shape fingerprint.
8. Review unexpected fields, errors, sensitive content, and schema implications.
9. Purge raw response according to the accepted posture.
10. Promote or reject the next candidate recipe.

No campaign stage advances merely because the previous request returned HTTP 200.

---

## Budget Strategy

The campaign ceiling is `$50.00`.

The budget is deliberately allocated by learning objective, not by a guessed number of calls.

| Stage | Learning objective | Stage ceiling | Exit condition |
|---|---|---:|---|
| 0 | Prove billing, usage-sheet, raw evidence, cost, and purge reconciliation | $2.00 | One fully reconciled Google Organic sentinel |
| 1 | Compare core public search surfaces | $8.00 | Google desktop/mobile, Bing, YouTube shapes reviewed |
| 2 | Test device, location, and result-family variance | $8.00 | Variance evidence sufficient to define recipe dimensions |
| 3 | Inspect keyword/provider metric families | $10.00 | Metric provenance and field semantics reviewed |
| 4 | Inspect AI/GEO answer and mention surfaces | $10.00 | Citation/answer evidence ceiling documented |
| 5 | Inspect local/video/merchant/marketplace candidates | $7.00 | Admissible surface candidates ranked |
| Reserve | Handle provider drift, malformed payloads, justified repeats, or a high-value missing comparison | $5.00 | Owner-directed use only |

A stage ceiling is a hard stop, not a suggestion.

---

# Stage 0 — Billing Sentinel

## Recipe C00

```text
recipe_id: c00-google-organic-desktop-sentinel
provider: DataForSEO
endpoint: /v3/serp/google/organic/live/advanced
method: POST
keyword: observatory test page
location_code: 2840
language_code: en
device: desktop
os: windows
depth: 10
```

### Questions answered

- Does the immutable request execute as one task and one API call?
- What exact cost appears at top level and task level?
- What row appears in `serp-usage.xlsx`?
- Does the provider usage ID map to the returned task ID?
- What timestamps and turnaround values are returned?
- What top-level and item-type fields exist?
- Does the current raw/hash/summary/purge lifecycle work with real data?

### Promotion gate

Do not proceed to C01 until:

```text
response cost reconciled
usage sheet row reconciled
request/task count confirmed
shape fingerprint created
raw handling reviewed
no credential leakage
raw purge plan confirmed
```

---

# Stage 1 — Core Surface Matrix

Stage 1 remains one-request-at-a-time until three total successful reconciled campaign pulls exist.

## Recipe C01 — Google organic mobile

```text
endpoint: /v3/serp/google/organic/live/advanced
keyword: observatory test page
location_code: 2840
language_code: en
device: mobile
os: android
depth: 10
```

Purpose:

- compare desktop and mobile envelope stability;
- identify device-specific item types and rank fields;
- determine whether request dimensions belong in later structured evidence.

## Recipe C02 — Bing organic desktop

```text
endpoint: /v3/serp/bing/organic/live/advanced
keyword: observatory test page
location_code: 2840
language_code: en
device: desktop
os: windows
depth: 10
```

Purpose:

- compare provider normalization across search engines;
- identify engine-specific fields and item types;
- test whether a common observation contract is possible without flattening engine differences.

## Recipe C03 — YouTube organic

```text
endpoint: /v3/serp/youtube/organic/live/advanced
keyword: what is an observatory
location_code: 2840
language_code: en
device: desktop
```

Purpose:

- inspect YouTube search-result payload shape;
- identify video/channel/result attributes and provider estimates;
- compare YouTube-native visibility evidence with Google video-result evidence later.

### Stage 1 review output

Create a comparison matrix covering:

```text
common envelope fields
engine/surface-specific fields
item type taxonomy
rank position semantics
timestamps
cost fields
request dimensions
provider-attributed metrics
raw-only fields
candidate structured fields
```

---

# Stage 2 — Variance and Result Families

These candidates are promoted only after Stage 1 review.

## Recipe C04 — Google Maps

```text
endpoint: /v3/serp/google/maps/live/advanced
keyword: public library
location_code: 2840
language_code: en
device: desktop
```

Questions:

- How are place, rating, address, category, coordinate, and rank fields represented?
- Which fields are provider-normalized versus direct result attributes?
- Does national location code produce meaningful local output, or is a city/coordinate recipe required?

## Recipe C05 — Google AI Mode

```text
endpoint: /v3/serp/google/ai_mode/live/advanced
keyword: what is an observatory
location_code: 2840
language_code: en
device: desktop
```

Questions:

- What answer blocks, references, sources, citations, and follow-up structures are returned?
- Which citation handles are stable enough to preserve?
- What claim-safety warning is required for a single generated answer sample?

## Later Stage 2 candidates

Only if the first five pulls justify widening:

```text
Google organic with a local city location
Google organic with a second language
Google News Live Advanced
Google Images Live Advanced
Google Autocomplete Live
Google Local Finder Live Advanced
```

These are comparison candidates, not an automatic checklist.

---

# Stage 3 — Keyword and Provider Metric Families

Keyword endpoints are admitted only after core SERP cost and evidence handling are understood.

## Recipe C06 — DataForSEO Labs Keyword Overview

```text
endpoint: /v3/dataforseo_labs/google/keyword_overview/live
keywords:
  - observatory
location_code: 2840
language_code: en
```

Questions:

- Which search-volume, competition, CPC, difficulty, intent, and trend fields appear?
- What are the field-level provider/model provenance requirements?
- Which values are estimates versus classifications versus observed result attributes?

## Recipe C07 — DataForSEO Labs Keyword Ideas

```text
endpoint: /v3/dataforseo_labs/google/keyword_ideas/live
keywords:
  - observatory
location_code: 2840
language_code: en
limit: 10
```

Questions:

- What seed-to-suggestion relationship is represented?
- Which metrics repeat from Keyword Overview?
- How are categories, intent, and result counts represented?
- What fields can support later read-time keyword interpretation without storing recommendations?

## Later Stage 3 candidates

```text
Related Keywords
Keyword Suggestions
Search Intent
Bulk Keyword Difficulty
Keywords For Site using a neutral public domain only after a separate recipe review
Google Ads Search Volume for one neutral keyword set
Bing Ads Search Volume comparison
```

Do not feed customer or SearchClarity domains into these probes.

---

# Stage 4 — AI/GEO Surfaces

AI/GEO endpoints may be more expensive and semantically dangerous. They are promoted only after exact cost is visible in the account and the core evidence pipeline is proven.

Candidate families:

```text
Google AI Mode Live Advanced
ChatGPT LLM Responses Live
Claude LLM Responses Live
Gemini LLM Responses Live
Perplexity LLM Responses Live
LLM Mentions Search
LLM Mentions target/domain metrics
AI Keyword Data search volume
```

The campaign should not attempt every model merely because the endpoint exists.

First AI/GEO comparison question:

```text
Can one neutral factual query be represented across two answer surfaces with source/citation provenance, model identity, request context, cost, and sampling caveats intact?
```

AI/GEO stop conditions:

- model price is unclear or unexpectedly high;
- citations are absent or non-reproducible;
- response cannot be retained under the accepted posture;
- output invites unsupported sentiment, authority, or visibility scoring;
- endpoint requires a multi-call workflow not yet admitted.

---

# Stage 5 — Local, Video, Merchant, and Marketplace Candidates

This stage exists to identify future instruments, not to authorize marketplace scraping.

Candidate order:

```text
YouTube organic
YouTube video info for a public neutral video ID
Google Maps
Google Local Finder
Google Shopping products
Amazon Labs keyword or product metrics
Pinterest Business Data if current official terms and endpoint behavior support it
```

Etsy and Fiverr remain blocked unless official access or explicit permission resolves the current evidence ceiling.

---

## Per-Pull Evidence Package

Every live campaign pull must produce:

```text
campaign_id
stage_id
recipe_id
approval reference
request SHA-256
duplicate key
provider task ID
usage-sheet row identifier
submitted/completed timestamps
HTTP/API request count
provider billable task count
provider top-level cost
provider task-level cost
usage-sheet cost
cost reconciliation status
response class
raw pointer/hash/bytes/media type
shape fingerprint
field-path count
field summary
rights/retention class
claim-use warning
review disposition
purge proof
```

---

## Usage Sheet Workflow

After each calibration pull, the owner uploads the latest `serp-usage.xlsx`.

The reconciliation process must:

1. Read the workbook without editing it.
2. Identify new rows since the previous upload.
3. Match rows to campaign recipes using ID, search engine, keyword, location/language, task times, and cost.
4. Compare usage-sheet cost with response cost fields.
5. Flag missing, duplicate, or ambiguous matches.
6. Record the workbook file hash and upload timestamp.
7. Never copy IP values into committed repo evidence unless specifically required and reviewed.

---

## Decision Rules After Each Pull

Each pull receives one disposition:

```text
accept shape evidence
accept with caveats
repeat justified due to malformed/incomplete evidence
promote next recipe
hold campaign
reject endpoint family
seek provider clarification
```

A repeat is not automatic. It requires a stated reason and a new request confirmation.

---

## Campaign Completion

M13 exploratory campaign work is complete when either:

```text
A. the $50 ceiling is reached and all pulls are reconciled/reviewed;
B. the owner concludes sufficient provider knowledge has been obtained before the ceiling;
C. provider behavior, rights, cost, or evidence handling makes further pulls unjustified.
```

Completion does not automatically admit recurring capture, create schema authority, or activate M14.

---

## Final Rule

```text
Pull the smallest sample that answers the next architecture question.
Review it while the context is fresh.
Spend wider only after the evidence earns it.
```
