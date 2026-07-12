# Contract - Provider Cross-Check

Status: accepted — contract set v0.1 by `decisions/2026-07-12-m14-contract-and-read-boundary-rulings.md`
Authority: contract (binds only when accepted; subordinate to `02-boundaries.md`)
Version: 0.1
Date: 2026-07-10
Milestone: M7 - Core Contract Planning
Source research: `research/rg9-provider-cross-check-disagreement-model.md`, with supporting inputs from `research/rg1-dataforseo-rights-retention-cost.md`, `research/rg5-freshness-staleness-volatility.md`, `research/rg6-geo-ai-citation-methodology.md`, `research/rg8-claim-safety-report-language.md`, `contracts/provider-testimony.md`, `contracts/claim-safety.md`, `contracts/freshness-staleness-volatility.md`, `contracts/query-panel.md`, `contracts/evidence-id-citation.md`, and root boundary law
Supersedes / superseded by: none

---

## Purpose

This contract governs how Observatory represents cross-provider comparison and disagreement without selecting a truth-provider, averaging disagreement into fake truth, or storing strategy/recommendation conclusions.

Provider Cross-Check exists because multiple instruments may observe the same subject differently. The disagreement is evidence about provider methods, coverage, freshness, source surfaces, definitions, and capture context. It is not a defect to smooth away and not a license to crown a winner.

This is a non-schema contract. It does not admit any provider, authorize paid pulls, create provider comparison tools, approve customer-facing report claims, or persist a Disagreement Ledger implementation.

---

## Governing boundaries

This contract operationalizes these rules:

- Observatory stores observations, not conclusions.
- Provider data is observed testimony, not truth.
- Provider scores and proprietary metrics are provider model output, not facts about the web.
- Provider disagreement must be preserved and not averaged into fake truth.
- Evidence IDs cite observations, not conclusions.
- Freshness, volatility, rights, retention, and source-admission warnings travel with evidence.
- Recommendations, strategy, provider selection advice, and accepted conclusions promote out to the owning consumer.
- Customer/private data and customer first-party analytics stay outside Observatory storage.

On conflict, `02-boundaries.md` and accepted spine contracts win.

---

## Definitions

### Provider Cross-Check

A bounded comparison of two or more provider-attributed observations that are about a stated subject and comparison context.

It describes what each provider reported and whether the observations are comparable, caveated, or incomparably different.

### Provider observation

One provider-attributed value, result, metric, citation, rank, score, estimate, or status observed at a known time under known context.

Provider identity must not be dropped.

### Comparison context

The declared reason and dimensions for comparing provider observations.

Examples:

```text
same keyword / same locale / same device / same time window
same URL / same provider metric family / comparable capture window
same AI prompt / same surface family / same panel version
same marketplace query / same public surface / same time window
```

### Disagreement

A visible difference between provider observations. Disagreement may come from value differences, coverage differences, freshness differences, source definitions, provider model differences, surface differences, parser drift, or unresolved incomparability.

### Disagreement summary

A read-time or contract-level description of differences and caveats. It is not a truth score, recommendation, provider winner, or accepted conclusion.

### Unresolved incomparability

A status indicating that provider observations look similar enough to tempt comparison but lack aligned dimensions or definitions required for safe comparison.

---

## Contract rules

### R1. Provider attribution is mandatory

Every provider value in a cross-check must preserve:

```text
provider_name
provider_family
endpoint_or_surface
metric/result name
captured_at
provider_reported_time if available
evidence_id or observation_id
rights_class
retention_class
freshness_status
volatility_class
```

A provider value without provider attribution cannot participate in a valid cross-check.

---

### R2. Cross-checks compare testimony, not truth

Provider Cross-Check may report:

```text
Provider A reported X.
Provider B reported Y.
These differ by Z under this context.
```

It must not report:

```text
The truth is X.
Provider A is right.
Provider B is wrong.
The average is the truth.
```

---

### R3. No truth-provider or winner-provider fields

The following concepts are forbidden inside Observatory:

```text
truth_provider
winner_provider
best_provider
provider_accuracy_score
provider_trust_score
average_truth_score
blended_rank_truth
blended_keyword_difficulty
blended_authority_truth
```

Any provider-selection recommendation belongs to a consumer layer, not Observatory.

---

### R4. Same-looking labels are not enough

A cross-check must not assume two metrics are comparable merely because names look similar.

Examples of non-comparable-by-default metric families:

```text
keyword difficulty scores from different providers
authority-like domain scores
AI visibility scores
provider confidence scores
SERP feature labels with different definitions
marketplace visibility estimates
```

If definitions are unknown, the comparison status must be `unresolved_incomparability` or heavily caveated.

---

### R5. Comparison dimensions must be explicit

A comparison context must declare relevant dimensions, such as:

```text
comparison_subject_type
comparison_subject_value
query_or_panel_item
query_panel_id
query_panel_version_id
surface_family
locale
language
device
location
capture_window_start
capture_window_end
provider_reported_time values
```

Missing dimensions block strong comparison claims.

---

### R6. Non-synchronous evidence must be disclosed

If capture times or provider-reported data times differ materially, the cross-check must carry a non-synchronous comparison warning.

If timing differences make the comparison unsafe, status must be `unresolved_incomparability` or `recapture_required_for_claim`.

---

### R7. Freshness and volatility travel with each side

Each provider observation keeps its own freshness and volatility metadata.

A cross-check must not hide that one provider value is fresh while another is stale, provider-dated, update-window affected, or historical-only.

---

### R8. Rights and retention apply per provider observation

A cross-check is only as usable as the rights and retention of each included observation.

If one provider observation is blocked by rights, retention, or source admission, the cross-check must either exclude that observation or mark the comparison blocked/partial.

---

### R9. Provider admission is separate from cross-check modeling

This contract defines how provider disagreement will be represented later. It does not admit DataForSEO, Ahrefs, Semrush, GSC, Bing Webmaster Tools, marketplace tools, GEO tools, AI tools, or any other provider.

Live provider comparisons require M13 provider admission and applicable source/capture contracts.

---

### R10. Cross-checks must not create recommendations

Cross-check output must not store:

```text
recommended provider
provider purchasing advice
which source to trust
keyword opportunity
content action
SEO strategy
customer report conclusion
agent task
```

Downstream interpretation belongs to SearchClarity, Neon Ronin, Kaizen, or another owning consumer.

---

### R11. Provider error and drift contexts must be visible

If disagreement may be caused by provider error payloads, parser failures, raw shape drift, provider endpoint changes, missing fields, or semantic drift, the cross-check must expose that caveat.

It must not silently compare corrupted or drift-blocked observations.

---

### R12. Absence/presence disagreement is scoped only

If one provider observes a result and another does not, the output may say presence/absence differed in the compared provider contexts.

It must not say the target is universally present or absent.

---

### R13. Cross-scope aggregate comparisons are blocked by default

Provider Cross-Check must not compare across customer scopes or mix customer engagement evidence into market-watch aggregate analysis without explicit future owner ruling.

---

### R14. Disagreement Ledger persistence is not presumed

A future system may need a persistent Disagreement Ledger, but this contract does not approve one.

Default posture:

```text
provider disagreement summaries are read-time output unless V6 materialization test plus owner ruling admits persistence
```

---

## Required fields / shapes

These are contract-level requirements, not schema.

### Provider observation shape

```text
provider_observation_id
provider_name
provider_family
endpoint_or_surface
provider_metric_name
provider_metric_value
provider_metric_unit
provider_metric_definition if available
captured_at
provider_reported_time
scope_id
scope_class
query_panel_id
query_panel_version_id
panel_run_id if applicable
observation_id
evidence_id
rights_class
retention_class
freshness_status
volatility_class
raw_payload_id if permitted
raw_support_status
```

### Comparison context shape

```text
comparison_context_id
comparison_subject_type
comparison_subject_value
query_or_panel_item
surface_family
locale
language
device
location
capture_window_start
capture_window_end
comparison_purpose
claim_intent if applicable
```

### Cross-check output shape

```text
comparison_context
provider_values
provider_definitions if available
capture_times
provider_reported_times
freshness_statuses
volatility_classes
disagreement_types
comparison_status
caveats
claim_use_warning
non_synchronous_comparison_warning
incomparability_warning
rights_retention_warning
consumer_promotion_required when output approaches recommendation
```

---

## Disagreement types

Candidate values:

```text
value_difference
presence_absence_difference
rank_position_difference
coverage_difference
definition_difference
freshness_difference
surface_difference
provider_model_difference
raw_shape_or_parser_difference
provider_error_difference
unresolved_incomparability
```

---

## Comparison statuses

Candidate statuses:

```text
comparable_with_caveat
partially_comparable
unresolved_incomparability
blocked_by_missing_context
blocked_by_rights_or_retention
blocked_by_source_admission
blocked_by_provider_drift
historical_only
consumer_interpretation_required
```

Status meanings:

- `comparable_with_caveat` means dimensions align enough for a caveated comparison.
- `partially_comparable` means some dimensions align, but limitations must be visible.
- `unresolved_incomparability` means comparison is unsafe without more definition/context.
- `consumer_interpretation_required` means the output is approaching strategy or recommendation and must promote out.

---

## Comparable vs non-comparable defaults

### Comparable only with caveats

```text
rank position for the same query/surface/location/device/time window
keyword volume estimate for the same keyword/locale/time window
AI mention/citation presence for the same prompt/panel/surface/time window
marketplace public listing presence for the same marketplace/search context/time window
provider-reported raw status for the same endpoint/capture context
```

### Non-comparable by default

```text
keyword difficulty scores from different providers
domain authority or authority-like proprietary scores
AI visibility scores from different tools
SERP feature results from different device/location contexts
marketplace ranks from personalized/account-influenced contexts
provider confidence scores with unknown definitions
fresh observations compared against stale provider-reported datasets
```

---

## Fail-closed behavior

A cross-check must fail closed or downgrade when:

- provider identity is missing;
- metric definition is unknown for a strong comparison;
- comparison subject differs;
- query/prompt/panel dimensions differ without caveat;
- locale/location/device/language differ without caveat;
- capture times or provider-reported times are non-synchronous;
- one evidence item is stale or update-window affected;
- rights or retention blocks either observation;
- provider source is not admitted;
- raw shape drift or parser status blocks observation trust;
- the requested output tries to choose a winner/provider truth;
- the requested output tries to create recommendation or strategy.

Fail-closed means the system does not return the strongest comparison wording.

---

## Forbidden patterns

This contract forbids:

```text
provider winner logic
truth-provider fields
averaged truth scores
blended proprietary metrics
provider trust scores
provider ranking recommendations
single blended rank from multiple providers
single blended keyword difficulty from multiple providers
single blended authority from multiple providers
provider output treated as objective web fact
provider disagreement hidden to simplify report language
non-synchronous comparisons without warning
cross-scope customer-derived aggregate comparisons
customer report conclusion stored as disagreement summary
agent task generated from provider disagreement inside Observatory
```

Fake-mustache variants are also forbidden:

```text
disagreement_confidence_score
provider_truth_rollup
best_source_hint
recommended_provider_id
consensus_rank
consensus_authority
market_truth_score
strategy_disagreement_summary
```

---

## Examples

### Valid example - provider-attributed difference

```text
comparison_subject_type: keyword
comparison_subject_value: etsy listing visibility audit
provider_values:
  - provider: Provider A
    metric: volume_estimate
    value: 90
    captured_at: 2026-07-10
  - provider: Provider B
    metric: volume_estimate
    value: 140
    captured_at: 2026-07-10
comparison_status: comparable_with_caveat
disagreement_type: value_difference
claim_use_warning: Provider values are estimates/model outputs and may differ by source coverage, methodology, and freshness.
```

Why valid:
Provider attribution remains visible and no truth value is created.

---

### Invalid example - averaged truth

```text
metric: true_keyword_volume
value: 115
basis: average of Provider A and Provider B
```

Why invalid:
The output averages provider estimates into fake truth.

---

### Valid example - unresolved incomparability

```text
metric: keyword_difficulty
provider_a_definition: proprietary / unknown
provider_b_definition: proprietary / unknown
comparison_status: unresolved_incomparability
claim_use_warning: Same-looking difficulty scores are not safely comparable without definitions.
```

Why valid:
The system refuses fake comparison when metric definitions are unknown.

---

### Invalid example - provider winner

```text
winner_provider: Provider A
reason: closer to average
```

Why invalid:
Observatory does not crown truth providers.

---

### Valid example - presence/absence difference

```text
Provider A observed target URL in the sampled SERP result set.
Provider B did not observe the target URL in its sampled SERP result set.
comparison_status: partially_comparable
disagreement_type: presence_absence_difference
caveat: This is provider/surface/context-bound and does not prove universal presence or absence.
```

Why valid:
Presence/absence is scoped and caveated.

---

### Invalid example - recommendation hidden in cross-check

```text
summary: Provider A is more reliable, so use Provider A for future SearchClarity reports.
```

Why invalid:
Provider choice and recommendation belong outside Observatory.

---

## Owner-ruling candidates

Open rulings carried forward:

- Whether a persistent Disagreement Ledger is ever allowed.
- Whether provider disagreement can be shown in SearchClarity customer-facing reports.
- Whether any ground-truth adjudication workflow is allowed when an external verified source exists.
- Whether any cross-provider comparison score is ever allowed. Default: no.
- Whether cross-scope aggregate provider disagreement analysis is allowed. Default: no.
- Whether provider comparison output can be materialized. Default: read-time only unless V6 materialization test plus owner ruling.

Until ruled, affected behavior fails closed.

---

## Deeper-research blockers

This contract remains blocked from live/provider-specific operation by:

- DR1 - DataForSEO endpoint-by-endpoint payload behavior.
- DR3 - DataForSEO / Ahrefs / Semrush metric comparison methodology.
- DR4 - GEO / AI citation measurement methodology.
- DR6 - Marketplace platform evidence limits: Etsy.
- DR7 - Marketplace platform evidence limits: Fiverr.
- DR13 - Raw archive layout and provider drift fingerprints.
- DR14 - Evidence ID, citation handle, and report-safe reference finalization.
- DR15 - Hammer matrix hostile-path expansion.

M13 must admit providers before live cross-check use. M14 must define read-tool shape. M15 must decide customer-facing report safety.

---

## Hammer expectations

M8+ must prove this contract with hostile-path hammers.

Required hammer categories:

```text
H1 - Scope isolation
H2 - Rights fail-closed
H3 - Retention fail-closed
H5 - No recommendation/strategy storage
H8 - Provider attribution and disagreement
H9 - Freshness / volatility / non-synchronous comparison
H10 - AI/GEO overclaim rejection
H11 - Marketplace boundary enforcement
H12 - Raw archive / parser drift integrity
H15 - Evidence / citation integrity
H16 - Overlay no-storage
H17 - LLM / agent access boundary
H18 - Hostile input
H19 - Append-only / no silent overwrite
H21 - Audit-first enforcement
```

Specific hostile paths:

```text
Provider value without provider_name -> reject.
Provider score returned as truth -> reject.
Two unknown proprietary metrics compared as comparable -> reject or unresolved_incomparability.
Provider disagreement averaged into truth -> reject.
winner_provider field returned -> reject.
Non-synchronous provider captures compared without warning -> reject.
Rights-blocked provider value included in comparison -> reject or partial/block.
Drift-blocked raw payload parsed into comparison -> reject.
Provider disagreement summary stores recommendation -> reject.
Cross-scope customer-derived comparison without owner ruling -> reject.
AI citation provider disagreement becomes AI trust claim -> reject.
Marketplace provider disagreement becomes traffic/sales claim -> reject.
```

---

## Feeds milestones

This contract feeds:

- M8 - Hammer Matrix and Acceptance Gates.
- M10 - Schema Planning Only.
- M13 - Provider Admission and Controlled Pull Plan.
- M14 - Typed Read API / MCP Contract and Prototype.
- M15 - SearchClarity Proof Workflow.
- M16 - Provider Cross-Check Proof.

---

## Non-authorizations

This contract does not authorize:

```text
schema design
migrations
provider admission
provider purchases
paid pulls
capture runners
raw archive implementation
provider comparison implementation
Disagreement Ledger persistence
API/MCP implementation
customer-facing report claims
provider recommendations
strategy storage
cross-scope aggregate analysis
```

---

## Final rule

```text
Provider disagreement is evidence.
Show it, attribute it, caveat it.
Do not average it into fake truth.
Do not crown a truth-provider.
Do not store the downstream interpretation.
```

---

## Change log

```text
0.1 - 2026-07-10 - initial draft from RG9 with supporting provider-testimony and claim-safety contracts
```
