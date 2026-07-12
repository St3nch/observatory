# Contract — Claim Safety

Status: accepted — contract set v0.1 by `decisions/2026-07-12-m14-contract-and-read-boundary-rulings.md`
Authority: contract (binds only when accepted; subordinate to `02-boundaries.md`)
Version: 0.1
Date: 2026-07-10
Milestone: M7 — Core Contract Planning
Source research: `research/rg8-claim-safety-report-language.md`, with supporting inputs from `research/rg5-freshness-staleness-volatility.md`, `research/rg6-geo-ai-citation-methodology.md`, `research/rg7-marketplace-evidence-ceiling.md`, `research/rg9-provider-cross-check-disagreement-model.md`, `research/rg10-capturepackage-v0-1-inputs.md`, `research/rg12-consumer-contract-inputs.md`, `planning-inbox/research/research-review-summary.md`, `02-boundaries.md`
Supersedes / superseded by: none

---

## Purpose

This contract governs what kinds of claims Observatory evidence may support, what caveats must travel with that support, and what claim shapes are forbidden inside Observatory.

It exists before schema or implementation so the project does not accidentally persist conclusions, recommendations, strategy, guarantees, causal claims, AI trust claims, provider-truth claims, or universal rank claims as if they were observations.

This contract absorbs negative-evidence / absence rules and adds the explicit `predictive_claim` class called out by the 2026-07-07 audits.

---

## Governing boundaries

This contract operationalizes these boundary rules:

- Observatory stores observations, not conclusions.
- The connected LLM interprets at read time.
- Accepted conclusions promote out to the owning consumer.
- Provider data is observed testimony, not truth.
- Provider scores and proprietary metrics are provider model output, not facts about the web.
- Provider disagreement is preserved and must not be averaged into fake truth.
- Customer records and customer first-party analytics stay outside Observatory.
- Customer overlays are read-time only unless future owner ruling changes project law.
- Rights and retention fail closed.
- Freshness and volatility determine claim-use fitness.
- Recommendations, strategy, opportunity verdicts, and customer-facing conclusions belong outside Observatory.

On conflict, `02-boundaries.md` wins.

---

## Definitions

### `claim`

A statement that uses one or more observations as support.

A claim may be safe, caveated, unsupported, or forbidden depending on evidence context, source, freshness, volatility, rights, and wording.

---

### `claim_intent`

The purpose or shape of a requested statement.

Claim intent helps future read tools decide what evidence and warnings are required. It does not authorize Observatory to store the claim.

---

### `claim_support`

A contract-level assessment of whether a set of evidence can support a claim shape.

Claim support is not an accepted conclusion. It is a read-time safety classification.

---

### `historical_observation_claim`

A statement about what was observed at a known time, surface, provider, and context.

Allowed shape:

```text
Observed on [date/time] in [surface/provider/context], [evidence] showed [observation].
```

This is the safest claim class.

---

### `current_state_claim`

A statement about what is true now.

This requires evidence fresh enough for the source family, volatility class, and proposed wording.

Current-state claims fail closed when capture time, provider-reported time, freshness, source context, rights, or retention are unknown or invalid.

---

### `comparative_claim`

A statement comparing two or more observations.

Examples:

- one provider reported one value while another provider reported another;
- one sampled panel run observed a URL more often than another;
- one historical capture differs from another.

Comparative claims require comparable context or explicit incomparability warnings.

---

### `absence_claim`

A statement that something was not observed.

Allowed shape:

```text
No [entity/citation/listing/result] was observed in this sampled [surface/provider/query/prompt/panel/run/context]. This does not prove universal absence.
```

Absence claims are always scoped to the exact capture context.

---

### `provider_metric_claim`

A statement about a provider-reported score, estimate, difficulty, authority-like value, confidence value, volume, rank, or proprietary metric.

Allowed shape:

```text
[Provider] reported [metric] as [value] for [target/context] on [date]. Treat this as provider model output or provider testimony, not a fact about the web.
```

---

### `ai_geo_claim`

A statement about AI answer-surface mention, citation, source visibility, prompt/panel visibility, or absence.

AI/GEO claims are sample-bound, prompt-bound, surface-bound, time-bound, and volatile.

Citation is not authority. Mention is not recommendation. Absence is not universal absence. Citation is not proof of influence.

---

### `marketplace_claim`

A statement about public marketplace observation such as listing presence, sampled marketplace search result position, public shop/listing content, or provider-estimated marketplace visibility.

Marketplace claims require platform, surface, capture method, public/private classification, rights posture, retention posture, and volatility caveats.

---

### `predictive_claim`

A statement about what will happen in the future.

Examples:

```text
This change will improve rank.
This keyword will increase traffic.
This listing will get more sales.
This page will be cited by AI.
```

Observatory does not store predictive claims. Predictive language belongs to consumer-side interpretation, with consumer-owned caveats and responsibility.

---

### `causal_claim`

A statement that one event caused another.

Examples:

```text
This title change caused rankings to improve.
This citation caused the AI answer.
This backlink caused traffic growth.
```

Observatory evidence may support temporal alignment or before/after comparison. It does not store causality conclusions.

---

### `recommendation_claim`

A statement telling a consumer, customer, agent, or operator what to do.

Examples:

```text
Change this title.
Target this keyword.
Buy this provider.
Pursue this opportunity.
```

Recommendations belong to SearchClarity, Neon Ronin, Kaizen, or another owning consumer, not Observatory.

---

### `accepted_conclusion`

A durable conclusion accepted by an owning consumer or governance system.

Accepted conclusions promote out to the owning consumer. Observatory may expose supporting evidence IDs, citation handles, and warnings, but must not become the conclusion store.

---

## Contract rules

### R1 — Evidence can support claims; evidence does not become the claim

Observatory may preserve observations and may return evidence with claim-use warnings.

Observatory must not persist the final claim, interpretation, recommendation, strategy, or accepted conclusion as an Observatory fact.

---

### R2 — Historical observation claims are allowed when evidence is valid

A historical observation claim is allowed only when the evidence preserves:

```text
evidence_id or valid citation handle
source/provider/surface
captured_at
context envelope
scope_id / scope_class
rights_class
retention_class
freshness metadata
```

If any required support is missing, the claim must be blocked or downgraded.

---

### R3 — Current-state claims require freshness fitness

A current-state claim requires evidence with a freshness status that supports current use for the evidence family and volatility class.

If evidence is stale, historical-only, unknown, update-window affected, rights-blocked, or retention-expired, the current-state claim must be blocked or downgraded.

---

### R4 — Absence means not observed in a specific context only

`not_observed` means only:

```text
not observed in this provider/surface/query/location/device/language/account-state/depth/time/panel/run/context
```

It never means:

```text
not present anywhere
not ranking anywhere
not cited by AI generally
not visible to customers
not important
```

---

### R5 — Provider metrics must stay provider-attributed

Provider scores, estimates, authority metrics, difficulty metrics, volume estimates, confidence scores, and proprietary values must be stated as provider-reported output.

They must not be stored or reported as objective truth.

---

### R6 — Provider disagreement must not be averaged into fake truth

When providers disagree, the disagreement must remain visible as provider-attributed evidence.

Forbidden outputs include:

```text
truth_provider
winner_provider
average_truth_score
single blended rank
single blended difficulty
single blended authority
```

---

### R7 — AI/GEO claims are sample-bound and volatile

AI answer-surface evidence may support only prompt/context/time-bound claims unless a later accepted methodology explicitly allows more.

AI citations must not be converted into trust, authority, influence, or endorsement claims.

AI absence must not be converted into universal absence.

---

### R8 — Marketplace claims require platform/capture/rights caveats

Marketplace evidence can support only point-in-time, platform-specific, public-surface claims unless a later source admission contract allows more.

Marketplace observations must not infer seller traffic, sales, conversion rate, private analytics, order volume, or customer behavior.

---

### R9 — Predictive claims are outside Observatory

Observatory must not store predictive claims.

A future read tool may return a warning that evidence is insufficient for prediction or that prediction belongs to the consumer layer.

Any durable prediction must be owned by SearchClarity, Neon Ronin, Kaizen, or another consumer.

---

### R10 — Causal claims are outside Observatory

Observatory may support before/after alignment as evidence.

Observatory must not store that one intervention caused another outcome.

Language such as `improved after` may be allowed as a temporal observation if evidence supports it. Language such as `improved because of` is a causal conclusion and must promote out.

---

### R11 — Recommendations and strategy must promote out

Any recommendation, opportunity verdict, tactical instruction, report conclusion, customer-facing action, or agent task belongs to the owning consumer.

Observatory may return evidence and warnings that help the consumer reason. It must not persist the recommendation.

---

### R12 — Claim support must preserve caveats by default

If a read tool returns claim support, it must carry all applicable caveats:

```text
freshness warning
volatility warning
provider attribution warning
sample-bound warning
absence warning
rights/retention warning
incomparability warning
recapture warning
consumer-promotion-required warning
```

Caveats must not be optional decoration.

---

### R13 — Customer/private overlays cannot become Observatory claims

Customer first-party overlays may be supplied to read tools only under future overlay contract rules.

Overlay values must not receive Observatory evidence IDs, must not be stored as observations, and must not be transformed into Observatory claims.

---

### R14 — Report-safe language is not admitted by this contract

This contract defines evidence-side claim safety.

It does not approve final SearchClarity customer-facing report language, report-safe citation handles, customer deliverables, or service claims.

M15 owns customer-facing proof language.

---

### R15 — Unknown or ambiguous claim context fails closed

If claim type, source, evidence context, rights, retention, freshness, provider definition, volatility, or sample scope is unknown, the system must block, downgrade, or caveat the claim.

It must not silently choose the strongest wording.

---

## Claim classes

| claim_class | Observatory posture | Required handling |
|---|---|---|
| `historical_observation_claim` | allowed when evidence valid | cite evidence, source, context, time |
| `current_state_claim` | allowed only with freshness fitness | freshness/volatility check required |
| `comparative_claim` | allowed with aligned context or incomparability caveat | disclose provider/surface/time differences |
| `absence_claim` | allowed only as sampled scoped absence | absence warning required |
| `provider_metric_claim` | allowed only as provider testimony | provider attribution required |
| `ai_geo_claim` | allowed only as sampled prompt/surface/time-bound observation | sample/volatility/citation caveats required |
| `marketplace_claim` | allowed only with platform/capture/rights caveats | no private/sales/traffic inference |
| `predictive_claim` | not stored by Observatory | consumer-owned if produced at all |
| `causal_claim` | not stored by Observatory | consumer-owned if produced at all |
| `recommendation_claim` | not stored by Observatory | consumer-owned |
| `accepted_conclusion` | not stored by Observatory | promotes out to owning consumer |

---

## Claim statuses

| claim_status | Meaning |
|---|---|
| `supported_with_caveat` | Evidence can support the claim only with specified caveats |
| `historical_only` | Evidence supports only a historical observation claim |
| `recapture_recommended` | Evidence may be usable but should be refreshed before strong current use |
| `recapture_required_for_claim` | Evidence cannot support the proposed claim without new capture |
| `unsupported` | Evidence does not support the claim |
| `forbidden_overclaim` | Claim form is disallowed regardless of evidence |
| `consumer_owned_recommendation` | Claim is actually a recommendation and belongs outside Observatory |
| `consumer_owned_prediction` | Claim is predictive and belongs outside Observatory |
| `consumer_owned_causal_conclusion` | Claim asserts causality and belongs outside Observatory |
| `blocked_by_rights_or_retention` | Evidence may exist but cannot be used for the claim because rights/retention fail |
| `blocked_by_unknown_context` | Required context is missing or ambiguous |

---

## Required fields / shapes

A future claim-support response must include, at contract level:

```text
claim_intent
claim_class
claim_status
evidence_ids
citation_handles if available
source_provider_surface
scope_id
scope_class
captured_at values
provider_reported_times if available
query_panel_id if applicable
query_panel_version_id if applicable
panel_run_id if applicable
freshness_status
volatility_class
rights_class
retention_class
claim_use_warning
freshness_warning
provider_attribution_required
sample_bound_warning
absence_warning
incomparability_warning
recapture_recommendation
consumer_promotion_required
```

These are behavior requirements, not schema.

---

## Required warnings

### `claim_use_warning`

Required when evidence supports only a limited claim shape or when the requested claim is stronger than the evidence.

---

### `freshness_warning`

Required when evidence is not fresh enough for the requested claim or when evidence age affects use.

---

### `provider_attribution_required`

Required when any provider-reported metric, score, result, confidence value, or estimate appears in the evidence.

---

### `sample_bound_warning`

Required for SERP panels, AI/GEO prompts, marketplace search samples, YouTube search samples, provider samples, and any observation that is not complete-universe evidence.

---

### `absence_warning`

Required for any not-observed statement.

Minimum wording requirement:

```text
This means not observed in this sampled context, not universal absence.
```

---

### `incomparability_warning`

Required when comparing providers, surfaces, captures, time windows, panels, prompts, devices, locations, languages, or metrics that are not fully aligned.

---

### `rights_retention_warning`

Required when rights or retention limit use, display, storage, raw payload access, report use, or current availability.

---

### `consumer_promotion_required`

Required when the requested output approaches recommendation, strategy, prediction, causality, customer report wording, accepted conclusion, or workflow action.

---

## Evidence-family claim matrix

| Evidence family | Allowed claim | Required caveat | Forbidden claim |
|---|---|---|---|
| SERP observation | result/page was observed in sampled SERP context | date, provider, query, locale/device, volatility | universal rank, guaranteed rank, causal improvement |
| Ranking observation | rank/position observed in specific sample | point-in-time, panel/run, update-window if relevant | `you rank X everywhere` |
| Keyword demand / volume | provider reported demand/volume estimate | provider-attributed estimate, capture date | actual traffic/sales guarantee |
| Provider score/difficulty | provider reported proprietary score | provider model output, not fact | true difficulty/authority as web fact |
| AI answer mention | entity was mentioned in sampled AI response(s) | prompt/panel, sample size, surface, volatility | universal AI visibility/rank |
| AI citation | URL/domain was cited in sampled response(s) | citation is not influence; sample-bound | citation caused answer; AI trusts source |
| AI absence | entity/citation was not observed in sampled run | sampled absence only | absent from AI search |
| Public page snapshot | page content was observed at capture time | current-page claims require recapture | page currently says X if stale |
| Public marketplace observation | listing/search result observed in specific public context | platform, date, capture method, rights posture, volatility | marketplace-wide rank, traffic/sales inference |
| Customer first-party overlay | consumer-supplied overlay used at read time | not stored; consumer supplies freshness | Observatory stored/verified private analytics |
| Internal telemetry | only after future admission | internal-scope contract required | admitted merely because owner-controlled |
| Raw provider payload | raw response existed and hashed if retention allows | rights/retention/pointer/hash caveats | raw payload is strategy truth |

---

## Report-safe phrase patterns

These are evidence-side phrase patterns only. They are not final SearchClarity report copy.

### Observation pattern

```text
Observation: On [date/time], [source/surface] showed [observation] for [query/panel/context].
```

### Provider metric pattern

```text
Provider estimate: [Provider] reported [metric/value] for [query/entity] on [date]. Provider metrics are model output or provider testimony and may differ from other tools.
```

### Freshness pattern

```text
Freshness caveat: This evidence was captured [age band] ago and has volatility class [class]. Recapture is recommended before strong current claims.
```

### AI/GEO pattern

```text
AI visibility caveat: This was observed in a sampled AI answer-surface run. Mention, citation, and influence are separate, and absence is not universal absence.
```

### Marketplace pattern

```text
Marketplace caveat: This was observed on [marketplace/surface] at [date/time/context]. Marketplace results may vary by time, location, account state, personalization, and platform changes.
```

### Absence pattern

```text
Absence caveat: No [entity/result/citation/listing] was observed in this sampled [surface/context/run]. This does not prove universal absence.
```

### Recommendation handoff pattern

```text
Downstream recommendation, if any, must be created and stored by the owning consumer. Observatory only supplies the cited evidence and caveats.
```

---

## Fail-closed behavior

A claim must be blocked, downgraded, or caveated when:

- claim intent is unknown;
- source/provider/surface is unknown;
- capture context is missing;
- captured_at is missing;
- provider-reported time is required but missing;
- freshness status is unknown for a current claim;
- volatility class is unknown for a strong current claim;
- rights class blocks use;
- retention class blocks use;
- evidence status is withdrawn, invalidated, expired, purged, or unavailable;
- provider metric definition is unknown and a comparative claim is requested;
- provider comparison is non-synchronous or non-comparable;
- absence is being converted into universal absence;
- AI citation is being converted into trust/influence/authority;
- marketplace observation is being converted into traffic/sales/customer behavior;
- evidence would support only consumer-owned recommendation, prediction, or causality.

Fail-closed means the strongest claim must not be returned.

---

## Forbidden patterns

The following are forbidden inside Observatory:

```text
guaranteed rankings
guaranteed traffic
guaranteed sales
guaranteed AI citations
Google trusts you more
AI trusts your competitor more
you rank X everywhere
you are absent from AI search
this source caused the AI answer
this provider score is the truth
keyword difficulty is objectively X
this marketplace listing ranks X globally
this seller gets more traffic than you
this optimization will improve rank
Observatory recommends
Observatory decided
Observatory conclusion
best keyword to target
opportunity score
strategy verdict
action item for customer
agent task created from evidence
average provider truth score
winner provider
```

Also forbidden:

- storing report conclusions in Observatory;
- storing SearchClarity recommendations in Observatory;
- storing Neon Ronin workflow decisions in Observatory;
- storing Kaizen accepted decisions in Observatory;
- storing customer first-party overlays as evidence;
- storing AI/GEO visibility authority scores;
- storing provider score as truth;
- hiding caveats from claim-support output.

---

## Examples

### Valid historical SERP claim

```text
On 2026-07-10, DataForSEO reported the target URL at position 8 for the sampled Google desktop US query-panel item.
```

Why valid:

- source is provider-attributed;
- time and context are explicit;
- claim is historical;
- no universal rank is asserted.

---

### Invalid universal rank claim

```text
You rank #8 on Google.
```

Why invalid:

- omits sample context;
- implies universal/current rank;
- omits provider, query, location, device, and time.

---

### Valid absence claim

```text
No citation for the target domain was observed in this sampled AI answer-surface run for the specified prompt panel on 2026-07-10. This does not prove universal absence.
```

Why valid:

- absence is scoped;
- surface/run/panel/time are named;
- universal absence is disclaimed.

---

### Invalid AI trust claim

```text
The AI does not trust your site because it did not cite you.
```

Why invalid:

- converts absence into trust judgment;
- infers motive/authority;
- exceeds evidence.

---

### Valid provider metric claim

```text
Provider X reported keyword difficulty of 72 for this keyword on 2026-07-10. This is provider model output, not an objective difficulty fact.
```

Why valid:

- provider attribution is explicit;
- metric is caveated as model output;
- no truth-provider is created.

---

### Invalid recommendation storage

```text
Observatory recommends changing the title to include blue widget.
```

Why invalid:

- recommendation belongs to consumer layer;
- Observatory must not store strategy/action.

---

### Valid before/after support language

```text
The evidence pack aligns a title-change date supplied by the consumer with ranking observations before and after that date. The output supports downstream review but does not assert causality.
```

Why valid:

- intervention remains external;
- causality is not asserted;
- consumer owns conclusion.

---

### Invalid causal claim

```text
The title change caused rankings to improve.
```

Why invalid:

- causality is an interpretation;
- evidence may show timing but not prove cause;
- durable causal conclusion must promote out.

---

## Owner-ruling candidates

Open rulings linked to `planning-inbox/owner-ruling-tracker.md`:

- Whether any claim status automatically blocks downstream consumer output.
- Whether any provider-supplied sentiment field is allowed as provider testimony.
- Whether any mechanically derived sentiment is allowed. Default for this draft: no.
- Whether AI visibility sample summaries may ever be persisted. Default for this draft: read-time only unless V6 materialization test plus owner ruling.
- Whether final report-safe citation language belongs in this contract or waits fully for M15. Default for this draft: wait for M15.
- Whether predictive language may be returned by read tools as consumer-owned draft language. Default for this draft: no durable Observatory storage.

Until ruled, affected behavior fails closed.

---

## Deeper-research blockers

This contract is blocked from becoming customer-facing or provider-specific in several areas by:

- DR3 — DataForSEO / Ahrefs / Semrush comparison methodology;
- DR4 — GEO / AI citation measurement methodology;
- DR5 — Google AI Overview / AI Mode capture and visibility limits;
- DR6 — Marketplace platform evidence limits: Etsy;
- DR7 — Marketplace platform evidence limits: Fiverr;
- DR8 — Manual capture and browser-extension capture admissibility;
- DR9 — SearchClarity customer-facing report language validation;
- DR10 — Customer first-party overlay contract;
- DR14 — Evidence ID, citation handle, and report-safe reference finalization.

This draft is enough for M7 claim-safety planning. It is not enough for customer-facing report templates, provider admission, or implementation.

---

## Hammer expectations

M8 must define hammers that prove at least:

- stale evidence cannot support strong current claims without warning or block;
- missing capture context blocks claims;
- provider metrics cannot be returned as truth;
- provider disagreement cannot be averaged into a truth score;
- single SERP snapshots cannot become universal rank claims;
- AI citation cannot become trust, authority, or influence;
- AI absence cannot become universal absence;
- marketplace observation cannot imply traffic, sales, or private analytics;
- predictive claims are blocked or consumer-owned;
- causal claims are blocked or consumer-owned;
- recommendations cannot be stored in Observatory;
- customer overlays cannot become Observatory evidence or claims;
- rights/retention failures block claim support;
- claim-support output includes required caveats.

Relevant RG13 hammer categories:

```text
H2 rights fail-closed
H3 retention fail-closed
H4 customer-private rejection
H5 no recommendation storage
H8 provider attribution and disagreement
H9 freshness and volatility
H10 AI/GEO overclaim rejection
H11 marketplace boundary enforcement
H15 evidence/citation integrity
H16 overlay no-storage
H17 LLM/agent access boundary
H18 hostile input
H19 append-only/no silent overwrite
H21 audit-first enforcement
```

---

## Feeds milestones

This contract feeds:

- M8 — claim-safety hammers;
- M10 — schema planning constraints for evidence and warnings;
- M13 — provider admission caveat requirements;
- M14 — typed read-tool evidence-pack warnings;
- M15 — SearchClarity proof workflow and report language validation;
- M16 — provider cross-check proof;
- M17 — overlay proof.

---

## Non-authorizations

This contract does not authorize:

- schema design;
- migrations;
- provider admission;
- provider pulls;
- paid spend;
- capture runners;
- raw archive implementation;
- API/MCP implementation;
- dashboard work;
- customer-facing reports;
- SearchClarity report templates;
- customer data handling;
- strategy storage;
- recommendation storage;
- recurring capture.

---

## Final rule

```text
Evidence may support a claim.
Evidence does not become the claim.
The stronger the claim, the fresher, narrower, and more caveated the evidence must be.
Predictions, causality, recommendations, and accepted conclusions live outside Observatory.
```

---

## Change log

```text
0.1 — 2026-07-10 — initial draft from RG8 with supporting RG5/RG6/RG7/RG9/RG10/RG12 inputs; absorbs absence/negative-evidence rules and adds predictive_claim class
```
