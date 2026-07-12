# Contract - Freshness / Staleness / Volatility

Status: accepted — contract set v0.1 by `decisions/2026-07-12-m14-contract-and-read-boundary-rulings.md`
Authority: contract (binds only when accepted; subordinate to `02-boundaries.md`)
Version: 0.1
Date: 2026-07-10
Milestone: M7 - Core Contract Planning
Source research: `research/rg5-freshness-staleness-volatility.md`; supporting inputs from `research/rg6-geo-ai-citation-methodology.md`, `research/rg7-marketplace-evidence-ceiling.md`, `research/rg8-claim-safety-report-language.md`, `research/rg10-capturepackage-v0-1-inputs.md`, `research/rg12-consumer-contract-inputs.md`, `contracts/scope-rights-retention.md`, `contracts/evidence-id-citation.md`, `02-boundaries.md`, `01-harvest-register.md`
Supersedes / superseded by: none

---

## Purpose

This contract governs how Observatory evidence describes age, staleness, volatility, update-window risk, and recapture needs before any schema, capture runner, provider pull, typed API/MCP tool, or consumer workflow is designed.

Freshness is not truth. Freshness is evidence fitness for a proposed use.

A historically valid observation may be too old, too volatile, or too poorly timestamped to support a current-state claim. This contract ensures every evidence pack can tell downstream readers when evidence was observed, how fast the observed surface can change, what kind of claim it can safely support, and when recapture is recommended or required.

---

## Governing boundaries

This contract operationalizes these Observatory rules:

```text
The Observatory stores observations, not conclusions.
The connected LLM interprets at read time.
Accepted conclusions promote out to the owning consumer.
Rights and retention fail closed.
Provider data is observed testimony, not truth.
Customer first-party data is not stored in Observatory.
LLMs and agents get shaped evidence packs, not raw SQL or credentials.
```

Freshness labels, volatility labels, age bands, and recapture warnings are observation metadata and read-tool caveats. They are not strategy recommendations, opportunity scores, customer conclusions, or task decisions.

On conflict, `02-boundaries.md` wins.

---

## Definitions

### `captured_at`

The Observatory-side time when an observation or capture package was created, received, or accepted, depending on the admitted capture method.

Rules:

- Required for any observation that can support evidence.
- Must not be inferred from provider data when absent.
- Unknown `captured_at` fails closed for current claims.

---

### `provider_reported_time`

A provider-side timestamp, data date, crawl date, index date, or reporting-period timestamp supplied by the source/provider.

Rules:

- Preserved when available.
- Distinct from `captured_at`.
- May show that provider data was already old when Observatory captured it.
- Must remain provider-attributed.

---

### `observation_age`

The elapsed time between the relevant read/use time and `captured_at`, or between the read/use time and a provider-side data timestamp when the evidence family requires provider-side age awareness.

Rules:

- The age calculation belongs to read-time behavior.
- The underlying timestamps belong to evidence metadata.
- Age may be unknown when required timestamps are missing.

---

### `age_band`

A coarse label describing observation age.

Candidate labels:

```text
0-24h
1-7d
8-30d
31-90d
90d+
unknown
```

These bands are provisional M7 contract defaults. They are not product promises and not final family-specific thresholds.

---

### `freshness_status`

A label describing whether evidence is fit for the proposed claim/use.

Candidate labels:

```text
fresh_for_current_claims
usable_with_caveat
historical_only
recapture_recommended
recapture_required_for_claim
stale_unknown
```

Freshness depends on:

- evidence family;
- claim intent;
- captured_at;
- provider_reported_time when available;
- volatility_class;
- update-window status;
- rights and retention validity;
- source-specific contract rules.

---

### `volatility_class`

A label describing how quickly or unpredictably the observed surface tends to change.

Candidate labels:

```text
low
medium
high
update_window
unknown
```

Volatility is a caution label, not a claim about exact decay rate.

---

### `update_window`

A known active, recent, or relevant rollout, ranking update, incident, provider change, product change, or platform behavior change that affects interpretation.

Examples:

```text
Google core or spam update window
AI answer-surface rollout
SERP feature rollout/removal
provider endpoint behavior change
marketplace ranking/system change
provider payload shape drift
```

Update-window awareness is not implementation-approved by this contract. This contract only requires that, when known, update-window risk must be represented and exposed.

---

### `claim_intent`

The proposed use of evidence, used to decide freshness requirements.

Candidate claim intents imported from RG8/RG12:

```text
historical_observation_claim
current_state_claim
comparative_claim
absence_claim
provider_metric_claim
report_support_request
```

Freshness rules evaluate whether evidence can support a claim intent. They do not create the claim.

---

### `recapture_recommendation`

A warning that newer evidence would improve safety or usefulness for a proposed use.

`recapture_recommended` is advisory and belongs in read output.

It is not approval to run a capture.

---

### `recapture_required_for_claim`

A blocking status saying the proposed claim cannot be supported without fresh evidence.

It is not approval to run a capture. Any actual recapture remains subject to source admission, provider/capture admission, rights, retention, cost, and owner approval.

---

## Contract rules

### R1 - Every evidence pack must expose freshness context

Every future evidence pack or read-tool response that returns Observatory evidence must include or be able to resolve:

```text
captured_at
provider_reported_time if available
observation_age or age_band when calculable
freshness_status
volatility_class
freshness_reason
claim_use_warning
recapture_recommendation or recapture_required_for_claim when applicable
```

This is a contract-level requirement, not a schema design.

---

### R2 - Unknown timestamps fail closed for current claims

If `captured_at` is missing, invalid, ambiguous, or not trustworthy, evidence must not support a `current_state_claim`.

Default behavior:

```text
freshness_status: stale_unknown
claim_use_warning: current claims blocked until timestamp/capture provenance is resolved or evidence is recaptured
```

Historical handling may remain possible only if the evidence contract can still prove what was observed and when it was valid enough to cite historically.

---

### R3 - Provider-reported time does not replace Observatory capture time

A provider timestamp cannot silently stand in for `captured_at`.

Correct behavior:

```text
captured_at: Observatory/capture-side timestamp
provider_reported_time: provider-attributed timestamp if available
freshness_reason: explain both if they differ materially
```

If a provider reports stale data during a fresh Observatory capture, the evidence must carry a provider-freshness caveat.

---

### R4 - Freshness is evaluated against claim intent

The same evidence may be acceptable for a historical observation and unacceptable for a current-state claim.

Examples:

```text
historical_observation_claim -> allowed if evidence is valid under rights/retention and provenance
current_state_claim -> may require fresh_for_current_claims or usable_with_caveat
absence_claim -> must be sampled/context-bound and freshness-aware
comparative_claim -> requires comparable timestamps, panels, and caveats
provider_metric_claim -> must remain provider-attributed and timestamped
```

Freshness labels must not be treated as universal truth labels.

---

### R5 - Volatility class must travel with evidence

Every observation family must have a volatility class before it can support claim-safe read output.

Default behavior:

```text
new or unclassified evidence family -> volatility_class: unknown
unknown volatility -> current claims require caveat or recapture
```

---

### R6 - High-volatility evidence defaults to point-in-time

Evidence from high-volatility surfaces defaults to point-in-time historical observation unless fresh enough for the proposed use and caveated.

High-volatility examples:

```text
AI answer-surface mentions/citations
local/mobile SERPs
competitive SERPs
marketplace search results
public marketplace listing/search observations
```

Strong current claims from high-volatility evidence usually require very recent evidence or recapture.

---

### R7 - Update-window evidence must be marked

If evidence was captured during or near a known relevant update window, read output must expose that caveat.

Candidate behavior:

```text
volatility_class: update_window
freshness_status: usable_with_caveat or recapture_recommended depending on claim intent
claim_use_warning: observation occurred during/near a relevant update or rollout window
```

If the purpose is to observe the update window itself, historical use may be valid. If the purpose is a stable current-state claim, recapture after the window may be required.

---

### R8 - Stale evidence can remain citable history

Staleness does not automatically invalidate evidence.

Stale evidence may still support:

```text
historical observation claims
trend/context review
before/after evidence packs with proper caveats
archival citations if rights/retention remain valid
```

Stale evidence must not be quietly upgraded into current evidence.

---

### R9 - Recapture warnings are not capture approval

A read output may say recapture is recommended or required for a claim.

That output does not authorize:

```text
provider spend
paid pull
manual capture
browser-extension capture
capture runner implementation
recurring capture
platform automation
```

Any recapture action must pass the relevant source/capture/provider admission gates.

---

### R10 - Freshness cannot override rights or retention

Evidence that is fresh but blocked by rights, retention, source admission, customer/private-data boundary, or invalid capture method must remain blocked.

Freshness is subordinate to:

```text
source_admission_status
rights_class
retention_class
evidence status
customer/private-data boundary
capture validity
```

---

### R11 - Comparative evidence must expose non-synchronous timing

When observations are compared, read output must expose whether capture times and provider-reported times are meaningfully comparable.

If not comparable, the comparison must include one of:

```text
non_synchronous_comparison_warning
unresolved_incomparability
recapture_required_for_claim
```

The system must not hide timing differences to make a comparison look stronger.

---

### R12 - Absence claims are freshness-bound and sample-bound

A not-observed claim must include the exact sampled context and freshness caveat.

Allowed pattern:

```text
Not observed in this sampled provider/surface/query/prompt/location/device/time/depth/run.
```

Forbidden pattern:

```text
not present anywhere
not ranking
not cited by AI generally
not visible to customers
```

Stale absence evidence is especially weak for current absence claims.

---

### R13 - Customer/private overlays carry consumer-supplied freshness only

Customer first-party overlays are not stored in Observatory and do not receive Observatory evidence IDs under current law.

If a future read tool accepts an overlay, the consumer must supply overlay freshness metadata. Observatory may use that metadata at read time and must discard the overlay.

Forbidden behavior:

```text
persist overlay series
assign Observatory evidence IDs to private overlay rows
promote overlay freshness into Observatory observations
store customer analytics as freshness evidence
```

---

### R14 - Age bands are provisional and must not become product guarantees

The initial age bands and family defaults in this contract are M7 contract defaults for hammers and later schema planning.

They must not be sold or exposed as guaranteed product methodology until later consumer/report contracts approve them.

---

### R15 - Freshness warnings must be plain enough for downstream consumers

Future read tools should return machine-readable labels and plain-language warnings.

Example plain-language warning:

```text
Observed on 2026-07-07 for Google desktop US. Search results may differ by date, location, device, personalization, and active ranking updates.
```

The warning must not overclaim or turn into a recommendation.

---

## Required fields / shapes

These are contract-level requirements. They are not schema.

### Minimum freshness shape

```text
evidence_id
observation_ids
captured_at
provider_reported_time if available
observation_age or age_band
freshness_status
volatility_class
freshness_reason
claim_intent if evaluating a proposed use
claim_use_warning
recapture_recommendation
recapture_required_for_claim when applicable
rights_retention_warning if applicable
source_admission_warning if applicable
```

### Query/panel-linked freshness shape

When evidence is tied to query/prompt/panel observations, read output should also resolve:

```text
query_panel_id
query_panel_version_id
panel_run_id
surface_family
locale/location/language/device if applicable
sample_depth or run context when applicable
```

### Comparative freshness shape

For comparisons:

```text
comparison_context_id if available
left_evidence_id
right_evidence_id or comparison evidence set
captured_at values
provider_reported_times if available
freshness_statuses
volatility_classes
non_synchronous_comparison_warning
update_window_warning if applicable
claim_use_warning
```

### Overlay freshness shape

For future read-time overlays:

```text
overlay_source_type
overlay_supplied_by_consumer
overlay_timestamp
overlay_freshness_status supplied by consumer
overlay_no_storage_assertion
overlay_discard_required
```

Overlay metadata is read-time input, not Observatory persistence approval.

---

## Freshness statuses

| Status | Meaning | Behavior |
|---|---|---|
| `fresh_for_current_claims` | Evidence is recent enough for cautious current claims for its family/use | Can support current statements with normal caveats |
| `usable_with_caveat` | Evidence may support current analysis but needs age/volatility warning | Must display caveat |
| `historical_only` | Evidence is valid history but not safe for current-state claims | Current claims blocked; historical use allowed if rights/retention valid |
| `recapture_recommended` | Evidence is aging or volatile enough that newer evidence is recommended | Advisory warning; no capture approval |
| `recapture_required_for_claim` | Proposed claim cannot be supported without fresh evidence | Block claim support; no capture approval |
| `stale_unknown` | Freshness cannot be determined | Fail closed for current claims |

---

## Volatility classes

| Class | Meaning | Examples |
|---|---|---|
| `low` | Surface usually changes slowly enough that older evidence can remain useful with caveats | stable public page metadata, static docs, archived source pages |
| `medium` | Surface can change materially over days/weeks | ordinary SERP snapshots, provider estimates, public page snapshots depending on page type |
| `high` | Surface can change materially over hours/days or across query/session variants | AI answer surfaces, competitive SERPs, local/mobile SERPs, marketplace search results |
| `update_window` | Known update, incident, rollout, or provider drift window affects interpretation | Google ranking update, AI rollout, provider endpoint behavior shift |
| `unknown` | Volatility not classified | new provider/surface/family |

---

## Initial age bands

| Age band | Label | Starting use |
|---|---|---|
| `0-24h` | very recent | Best for high-volatility surfaces |
| `1-7d` | recent | Usually usable with caveat for many search surfaces |
| `8-30d` | aging | Useful for trends/history; current claims need caution |
| `31-90d` | old | Historical or broad trend only unless low-volatility family |
| `90d+` | archival | Historical evidence; current claims require recapture |
| `unknown` | unknown | Fail closed for current claims |

Rules:

- These bands are starting defaults.
- Family-specific thresholds remain future contract/admission work.
- High-volatility surfaces may require `0-24h` or `1-7d` evidence for current claims.
- Low-volatility surfaces may support longer reuse when the claim is historical or about stable facts.

---

## Initial evidence-family defaults

| Evidence family | Default volatility | Initial reuse posture |
|---|---|---|
| SERP observation | `medium`; `high` during local/competitive/update windows | Use with dated caveat; recapture before strong current claim |
| Ranking observation | `medium` / `high` | Recapture recommended before customer-facing current rank claim |
| Keyword demand observation | `medium` | Provider/date caveat; never exact demand truth |
| AI answer-surface mention/citation | `high` | Point-in-time; recapture required for strong current claim |
| Public page snapshot | `low` / `medium` depending on page type | Historical snapshot valid; current page claims may need recapture |
| Public marketplace listing/search observation | `high` | Point-in-time; recapture before current marketplace claim |
| Provider score/difficulty/authority metric | `medium`; provider-model-dependent | Provider-attributed estimate only |
| Raw provider payload | Mirrors source family and provider drift status | Valid raw history only if rights/retention allow |
| Customer first-party overlay | not stored | Consumer supplies freshness at read time |
| Internal first-party telemetry | `unknown` until admitted | Requires internal-scope contract before storage/use |

---

## Claim-use matrix

| Claim intent | Minimum freshness posture |
|---|---|
| `historical_observation_claim` | Valid evidence under source, rights, retention, provenance, and evidence-status rules |
| `current_state_claim` | `fresh_for_current_claims` or `usable_with_caveat` with dated caveat; stronger claims may require recapture |
| `comparative_claim` | Comparable timestamps/panels/surfaces, non-synchronous warning if applicable, volatility caveats |
| `absence_claim` | Fresh, sample-bound, context-bound; stale absence usually weak or blocked for current claims |
| `provider_metric_claim` | Provider-attributed, timestamped, freshness/cadence caveated |
| `report_support_request` | Evidence plus caveats only; final report language belongs to consumer |
| predictive/recommendation-like use | Observatory must not store; consumer-owned interpretation only |

---

## Fail-closed behavior

### F1 - Missing `captured_at`

If `captured_at` is missing:

```text
freshness_status: stale_unknown
current_state_claim: blocked
historical_observation_claim: blocked unless another accepted contract proves valid time context
```

---

### F2 - Unknown volatility

If volatility is unknown:

```text
volatility_class: unknown
current_state_claim: usable only with caveat or blocked depending on claim strength
strong current claim: recapture_required_for_claim
```

---

### F3 - Provider timestamp mismatch

If provider-reported time is materially older than `captured_at`:

```text
freshness_reason must disclose provider-side age
provider_metric_claim must say provider-reported / provider-dated
current_state_claim may require caveat or recapture
```

---

### F4 - Known update window

If an update window is known and relevant:

```text
volatility_class: update_window
claim_use_warning required
strong stable-current claim: recapture_recommended or recapture_required_for_claim
```

---

### F5 - Rights/retention conflict

If rights or retention are invalid, unclear, expired, or blocked:

```text
freshness does not matter
read/citation use is blocked or limited by scope-rights-retention contract
```

---

### F6 - Customer/private overlay missing freshness metadata

If a read-time overlay lacks required freshness metadata:

```text
overlay comparison cannot support current or comparative claim
read output must warn that overlay freshness was not supplied
no overlay values may be persisted
```

---

## Forbidden patterns

This contract forbids:

```text
using stale evidence as current without warning
using unknown timestamp evidence for current claims
treating provider_reported_time as Observatory captured_at
hiding non-synchronous provider comparisons
treating recapture_required as capture approval
turning recapture warnings into agent tasks inside Observatory
turning freshness_status into strategy priority
storing recommendation/opportunity/task records from freshness warnings
using stale absence as universal absence
using fresh-but-rights-blocked evidence anyway
storing customer overlay freshness or private analytics in Observatory
selling provisional age bands as final product promises
```

Fake-mustache variants are also forbidden:

```text
stale_strategy_cache
recapture_task_queue
freshness_opportunity_score
priority_to_recapture table
customer_overlay_freshness_history
AI_visibility_current_score from old samples
provider_truth_freshness_rollup
```

Any persisted derived freshness aggregate beyond basic observation/evidence metadata requires the V6 materialization test plus explicit owner ruling.

---

## Examples

### Valid example - historical SERP observation

```text
evidence_id: ev_market_serp_20260707_d83a10
captured_at: 2026-07-07T14:05:00Z
surface_family: google_organic_serp
age_band at read time: 8-30d
volatility_class: medium
freshness_status: historical_only
claim_intent: historical_observation_claim
claim_use_warning: This supports what was observed at capture time, not a current ranking claim.
```

Why valid:
The evidence is used as historical observation, not current rank truth.

---

### Invalid example - stale SERP used as current rank

```text
claim: This page currently ranks #4 on Google.
evidence captured_at: 2026-04-01T12:00:00Z
read time: 2026-07-10T12:00:00Z
volatility_class: medium
freshness_status: historical_only
```

Why invalid:
Old SERP evidence can be historically true but cannot support a current rank claim without recapture.

---

### Valid example - AI citation sample caveated

```text
evidence_id: ev_market_ai_surface_20260710_f22b8c
captured_at: 2026-07-10T13:00:00Z
surface_family: ai_answer_surface
volatility_class: high
freshness_status: usable_with_caveat
claim_intent: historical_observation_claim
claim_use_warning: Citation was observed in this sampled prompt/surface/time context only; citation is not trust, influence, or universal AI visibility.
```

Why valid:
The language remains sample-bound and point-in-time.

---

### Invalid example - single AI absence as universal absence

```text
claim: The brand is absent from AI search.
evidence: one prompt run with no citation observed
volatility_class: high
freshness_status: usable_with_caveat
```

Why invalid:
Absence is limited to the sampled context and cannot become universal absence.

---

### Valid example - provider metric with provider-side age caveat

```text
provider: DataForSEO
evidence_id: ev_market_keyword_20260710_a88b10
captured_at: 2026-07-10T10:00:00Z
provider_reported_time: 2026-06-01
metric: keyword volume estimate
freshness_status: usable_with_caveat
claim_use_warning: DataForSEO reported this estimate; provider data date differs from Observatory capture time.
```

Why valid:
Provider identity and timestamp context are preserved.

---

### Invalid example - freshness warning turned into Observatory task

```text
freshness_status: recapture_required_for_claim
stored record: task_type=recapture_this_query
owner=Observatory
```

Why invalid:
Recapture warnings do not authorize tasks, capture runners, provider spend, or workflow storage inside Observatory.

---

## Owner-ruling candidates

Open rulings remain tracked in `planning-inbox/owner-ruling-tracker.md`.

This contract especially touches:

```text
OR-A6 - Minimum M7 contract set for closure
future freshness auto-block ruling - whether any freshness class automatically blocks customer-facing report use
future update-window dependency ruling - whether official update/status feeds become admitted freshness inputs
future recapture cadence ruling - no recurring capture until later milestones
```

Default posture until ruled:

```text
Freshness classes may block evidence support for claim intents.
Freshness classes do not trigger capture.
Freshness classes do not create tasks.
Freshness classes do not authorize customer-facing language.
```

---

## Deeper-research blockers

This contract is enough for M7 contract planning and M8 hammer input. It does not settle later methodology.

Relevant blockers:

```text
DR4 - GEO / AI citation measurement methodology
DR5 - Google AI Overview / AI Mode capture and visibility limits
DR6 - Marketplace platform evidence limits: Etsy
DR7 - Marketplace platform evidence limits: Fiverr
DR8 - Manual capture and browser-extension capture admissibility
DR9 - SearchClarity customer-facing report language validation
DR10 - Customer first-party overlay contract
DR11 - Owned internal first-party telemetry
DR12 - Query panel sampling and recapture cadence
DR13 - Raw archive layout and provider drift fingerprints
DR14 - Evidence ID, citation handle, and report-safe reference finalization
DR15 - Hammer matrix hostile-path expansion
```

Provider-specific cadence, freshness, retention, update-window, and endpoint behavior remain M13+ work.

Customer-facing freshness language remains M15 work.

Recurring capture cadence remains M18 planning.

---

## Hammer expectations

M8 must define hostile-path tests for this contract.

Primary RG13 hammer categories:

```text
H2 - Rights fail-closed
H3 - Retention fail-closed
H8 - Provider attribution and disagreement
H9 - Freshness / volatility / stale evidence
H10 - AI/GEO overclaim rejection
H11 - Marketplace restriction handling
H15 - Evidence/citation integrity
H16 - Overlay no-storage
H17 - LLM/agent access boundary
H19 - Append-only / no silent overwrite
H20 - Concurrency
H21 - Audit-first enforcement
```

Specific hostile paths:

```text
current claim from stale SERP evidence must be blocked or caveated
current claim from unknown timestamp must fail closed
AI absence from one stale sample must not become universal absence
provider metric with old provider_reported_time must carry caveat
non-synchronous provider comparison must warn or block
fresh evidence blocked by rights/retention must remain blocked
recapture_required must not create Observatory task/action/spend
customer overlay without freshness metadata must not support current claim
customer overlay freshness must not persist
update-window evidence must expose update-window warning when known
```

---

## Feeds milestones

This contract feeds:

```text
M8 - Hammer Matrix and Acceptance Gates
M9 - First Evidence Slice Definition
M10 - Schema Planning Only
M12 - First Evidence Slice Build
M13 - Provider Admission and Controlled Pull Plan
M14 - Typed Read API / MCP Contract and Prototype
M15 - SearchClarity Proof Workflow
M17 - Owned Telemetry Overlay Proof
M18 - Recurring Watch Panel Planning
```

---

## Non-authorizations

This contract does not authorize:

```text
schema design
migrations
provider pulls
provider purchases
provider admission
capture runner implementation
manual capture admission
browser extension admission
recurring capture
update-feed integration
API/MCP implementation
customer data handling
customer-facing report claims
strategy/recommendation storage
recapture task queues
```

---

## Change log

```text
0.1 - 2026-07-10 - initial draft from RG5 with supporting RG6/RG7/RG8/RG10/RG12 and existing M7 spine contracts
```
