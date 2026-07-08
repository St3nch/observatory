# RG9 — Provider Cross-Check & Disagreement Model

Status: research output
Authority: source-grounded research input; not doctrine by itself; not schema approval
Milestone: M6 — Research Gate Execution
Date: 2026-07-07

---

## Gate question

How should Observatory represent provider disagreement without selecting a truth-provider or averaging disagreement into fake truth?

---

## Sources checked

Local/current sources checked during RG9:

- `02-boundaries.md`
- `01-harvest-register.md`
- `research/m5-research-gate-plan.md`
- `planning-inbox/knowledgebase-reconciliation.md`
- `planning-inbox/m4-boundary-reconciliation.md`
- `planning-inbox/repo-first-research-triage.md`
- `research/rg1-dataforseo-rights-retention-cost.md`
- `research/rg5-freshness-staleness-volatility.md`
- `research/rg6-geo-ai-citation-methodology.md`
- `research/rg8-claim-safety-report-language.md`

No new current external source was required for RG9 because this gate defines the internal disagreement model. Current provider documentation will be needed later only when comparing specific metrics/surfaces from admitted providers.

---

## Current source-grounded findings

### F1 — Provider data is observed testimony, not truth

`02-boundaries.md` says provider data is observed testimony, not truth. Provider scores, difficulty metrics, authority metrics, confidence scores, and proprietary scoring fields are observations of provider model output.

Implication:

- Provider metrics must remain provider-attributed.
- Provider fields are not facts about the web.
- Read tools may compare provider outputs, but must not crown a truth-provider.

---

### F2 — Provider disagreement must be preserved

`02-boundaries.md` explicitly says provider disagreement must be preserved and not averaged into fake truth.

Implication:

- Disagreement is signal, not cleanup noise.
- Divergence may reveal model differences, index coverage differences, freshness differences, endpoint differences, or unstable surfaces.
- The system should show the disagreement and caveats without resolving it into false certainty.

---

### F3 — Provider admission is separate from provider comparison

RG1 says DataForSEO remains plausible but not admitted, and no paid pull is authorized.

Implication:

- RG9 defines the future model only.
- RG9 does not admit DataForSEO, Ahrefs, Semrush, GSC, Bing Webmaster Tools, marketplace tools, or any other provider.
- Live cross-checks require later provider admission and rights/retention handling.

---

### F4 — Claim safety requires provider-attributed language

RG8 says provider scores and estimates must be phrased as provider-reported output.

Implication:

- `Provider A reported X; Provider B reported Y` is valid if both observations are valid.
- `The truth is the average of X and Y` is forbidden.
- Provider disagreement should carry claim-use warnings.

---

## Proposed model

A provider cross-check groups comparable provider observations and describes how they differ.

It is not:

- a truth score;
- a confidence winner;
- a recommendation;
- a provider ranking;
- an averaged metric;
- a customer report conclusion.

Correct pattern:

```text
provider observations -> comparison context -> disagreement summary with caveats -> downstream consumer interprets
```

Forbidden pattern:

```text
provider observations -> averaged truth score -> stored recommendation
```

---

## Model layers

### `provider_observation`

A single provider-attributed value, payload, metric, result, citation, rank, or score observed at a time.

Candidate fields:

```text
provider_observation_id
provider_name
provider_family
endpoint_or_surface
provider_metric_name
provider_metric_value
provider_metric_unit
captured_at
provider_reported_time
scope_id
scope_class
query_panel_id
query_panel_version_id
observation_id
evidence_id
rights_class
retention_class
freshness_status
volatility_class
raw_payload_id or pointer if permitted
```

Rule:
Provider identity must never be dropped.

---

### `comparison_context`

Defines why observations are being compared.

Candidate fields:

```text
comparison_context_id
comparison_subject_type
comparison_subject_value
query_or_panel_item
surface_family
locale
language
device
capture_window_start
capture_window_end
comparison_purpose
```

Examples of `comparison_subject_type`:

```text
keyword
url
domain
listing
brand_entity
ai_prompt
marketplace_query
```

Rule:
Observations are comparable only when their dimensions are meaningfully aligned or the mismatch is disclosed.

---

### `disagreement_summary`

Describes the difference between provider observations without resolving it into truth.

Candidate fields:

```text
disagreement_summary_id
comparison_context_id
providers_compared
metrics_compared
disagreement_type
disagreement_magnitude
directionality
freshness_notes
coverage_notes
methodology_notes
caveats
claim_use_warning
```

Rule:
A disagreement summary says what differs and possible reasons. It does not decide who is correct.

---

## Disagreement types

| disagreement_type | Meaning |
|---|---|
| `value_difference` | Same-ish metric, different values |
| `presence_absence_difference` | One provider observes something another does not |
| `rank_position_difference` | Rank/position differs |
| `coverage_difference` | Provider indexes/surfaces differ |
| `definition_difference` | Similar labels use different definitions |
| `freshness_difference` | Capture or provider-reported times differ |
| `surface_difference` | Device/location/surface/prompt differs |
| `provider_model_difference` | Proprietary modeling differs |
| `unresolved_incomparability` | Data should not be compared directly |

---

## Comparable vs non-comparable by default

Comparable only with caveats:

```text
rank position for same query/surface/location/device/time window
keyword volume estimate for same keyword/locale/time window
AI mention/citation presence for same prompt/panel/surface/time window
marketplace public listing presence for same marketplace/search context/time window
```

Non-comparable by default:

```text
keyword difficulty scores from different providers
domain authority or authority-like proprietary scores
AI visibility scores from different providers
SERP features from different device/location contexts
marketplace ranks from personalized/account-influenced contexts
provider confidence scores with unknown definitions
```

Rule:
Same-looking labels are not enough. Metric definitions matter.

---

## Read-tool output requirements

A Provider Cross-Check read tool should return:

```text
comparison_context
provider_values
provider_definitions if available
capture_times
provider_reported_times
freshness_statuses
volatility_classes
disagreement_types
caveats
claim_use_warning
```

It should never return:

```text
truth_provider
winner_provider
average_truth_score
single blended rank
single blended difficulty
recommendation
accepted conclusion
```

---

## Relationship to query panels

Provider disagreement comparisons should usually be anchored to RG4 query panel context.

This keeps comparisons aligned across:

- query or prompt;
- panel version;
- surface family;
- locale/location/device;
- capture window.

If these differ, the output should mark the difference rather than pretend clean comparison.

---

## Relationship to claim safety

RG8 claim rules apply directly.

Allowed claim shape:

```text
Provider A reported X while Provider B reported Y. This disagreement is preserved because provider metrics are estimates or model outputs and may differ by methodology, index coverage, and freshness.
```

Forbidden claim shape:

```text
Provider A is right and Provider B is wrong.
```

unless a separate verified ground-truth source exists and a later contract admits adjudication.

---

## No-nonsense checks

Before a provider disagreement is shown as meaningful, read tools should ask:

1. Are providers measuring the same subject?
2. Are query/prompt/panel dimensions aligned?
3. Are locale/location/device/language dimensions aligned?
4. Are metric definitions known?
5. Are capture times comparable?
6. Are provider-reported data times comparable?
7. Are rights and retention valid for each observation?
8. Is one value stale or update-window affected?
9. Is the disagreement actually a surface mismatch?
10. Is the output trying to pick a winner without proof?
11. Is the output averaging proprietary scores into fake truth?
12. Does the claim language preserve provider attribution?

If these cannot be answered, mark the comparison as `unresolved_incomparability` or caveat heavily.

---

## Non-goals

RG9 does not authorize:

- schema design;
- migrations;
- provider admission;
- paid provider pulls;
- provider purchases;
- direct GSC/Bing connection;
- cross-provider scoring;
- provider winner logic;
- strategy/recommendation storage;
- customer-facing claims without RG8/M15 handling.

---

## Owner-ruling candidates

Owner ruling or later contract decision is required before:

- making Provider Cross-Check a standalone M7 contract;
- admitting any provider to cross-check comparisons;
- showing provider disagreement in customer-facing reports;
- defining any ground-truth adjudication workflow;
- defining any cross-provider comparison score;
- allowing cross-scope aggregate disagreement analysis.

---

## Blockers carried forward

- M7 must decide whether Provider Cross-Check gets its own contract.
- M8 must hammer provider attribution, no averaging, no winner logic, no hidden strategy storage, and incomparability warnings.
- M13 must admit providers before live cross-check capture/use.
- M14 read tools must expose disagreement caveats clearly.
- M15 must decide if provider disagreement is report-safe for SearchClarity.

---

## Feeds later milestones

- M7 Provider Cross-Check contract or provider testimony contract
- M8 disagreement hammers
- M10 schema planning
- M13 provider admission
- M14 typed read API / MCP contract
- M15 SearchClarity proof workflow
- M16 Provider Cross-Check proof

---

## Final RG9 rule

```text
Provider disagreement is not a bug.
It is evidence about providers, surfaces, definitions, freshness, and coverage.
Show the disagreement.
Do not average it into fake truth.
Do not crown a truth-provider.
```
