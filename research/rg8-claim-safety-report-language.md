# RG8 — Claim Safety / Report Language

Status: research output
Authority: source-grounded research input; not doctrine by itself; not schema approval
Milestone: M6 — Research Gate Execution
Date: 2026-07-07

---

## Gate question

What claims can be made from each evidence family, and what caveats are required for reports, audits, and LLM evidence packs?

---

## Sources checked

Local/current sources checked during RG8:

- `02-boundaries.md`
- `01-harvest-register.md`
- `research/m5-research-gate-plan.md`
- `planning-inbox/repo-first-research-triage.md`
- `research/rg3-evidence-id-citation-model.md`
- `research/rg4-query-panel-model.md`
- `research/rg5-freshness-staleness-volatility.md`
- `research/rg6-geo-ai-citation-methodology.md`
- `research/rg7-marketplace-evidence-ceiling.md`

No new current external source was required for RG8 because this gate synthesizes claim-safety rules from already sourced RG5/RG6/RG7 findings and live Observatory boundary law. Future SearchClarity-specific report language may need consumer-side source review in M15.

---

## Current source-grounded findings

### F1 — Observatory evidence supports claims; it does not store accepted claims

`02-boundaries.md` says Observatory stores observations, not conclusions, and accepted conclusions promote out to the owning consumer.

Implication:

- Observatory can return evidence packs, caveats, freshness, and citation handles.
- Observatory must not store final report conclusions, recommendations, opportunity scores, or accepted business decisions.
- Downstream reports can cite Observatory evidence, but report text belongs to SearchClarity or another consumer.

---

### F2 — Freshness determines whether evidence can support current claims

RG5 says old evidence can still be true, but not safe for current claims.

Implication:

- Every customer-facing or strategy-adjacent claim must consider `freshness_status`, `volatility_class`, age band, and update-window context.
- Unknown timestamps fail closed for current claims.
- Current ranking, AI visibility, and marketplace claims often require very recent evidence or recapture.

---

### F3 — AI/GEO claims need special caution

RG6 says AI visibility is sampled evidence: mention is not citation, citation is not influence, and absence is not universal absence.

Implication:

- AI/GEO report language must be sample-bound.
- Universal AI rank, absolute absence, trust/influence, and guaranteed citation claims are forbidden.
- AI visibility metrics can be reported only as observed sample results with surface, prompt/panel, time, and volatility caveats.

---

### F4 — Marketplace claims need platform/capture/rights caveats

RG7 says public marketplace pages are not automatically Observatory evidence, Etsy automation is blocked by default, Fiverr automation is not cleared, and private seller dashboards stay outside Observatory.

Implication:

- Marketplace report language must avoid implying comprehensive platform truth.
- Marketplace observations are point-in-time, surface-specific, and capture-method-bound.
- Private seller stats, traffic, sales, order data, and conversion data cannot be inferred from public marketplace observations.

---

### F5 — Provider metrics are provider-attributed estimates, not web facts

M4 boundary hardening says provider scores, difficulty metrics, authority metrics, confidence scores, and proprietary scoring fields are observations of provider model output.

Implication:

- Claims must say `DataForSEO reported X`, `provider estimate`, or similar.
- Claims must not say `the web difficulty is X` or `authority is X` as fact.
- Provider disagreement must be preserved, not averaged into fake truth.

---

## Claim classes

### `historical_observation_claim`

Meaning:
A statement about what was observed at a known time/context.

Allowed pattern:

```text
Observed on [date/time] in [surface/context], [evidence] showed [observation].
```

Example:

```text
On 2026-07-07, this sampled Google desktop US result set showed the page at position 8 for the query panel item.
```

Required caveats:

- capture time;
- surface/provider;
- query/panel context if applicable;
- evidence/citation handle.

---

### `current_state_claim`

Meaning:
A statement about what is true now.

Allowed only when:

- evidence is fresh enough for current claims;
- volatility class supports use;
- no active/update-window caveat blocks the claim;
- rights/retention permit use.

Allowed pattern:

```text
Based on evidence captured on [date/time], [observation] was current for the sampled context at capture time. Recapture is recommended before treating this as current beyond that context.
```

Forbidden pattern:

```text
You currently rank X everywhere.
```

---

### `comparative_claim`

Meaning:
A statement comparing two or more observations.

Allowed only when:

- evidence uses the same panel/version or explicitly comparable versions;
- surfaces and providers are disclosed;
- timestamps are comparable;
- update-window/volatility caveats are present.

Allowed pattern:

```text
Within the sampled panel, [A] appeared in more sampled results than [B] during this capture window.
```

Forbidden pattern:

```text
Competitor B is definitely beating you online.
```

---

### `absence_claim`

Meaning:
A statement that something was not observed.

Allowed pattern:

```text
No mention/citation/listing was observed in this sampled panel/run.
```

Required caveat:

```text
This does not prove universal absence.
```

Forbidden pattern:

```text
You are absent from AI search / Etsy / Google.
```

---

### `provider_metric_claim`

Meaning:
A statement about a provider score, difficulty, volume, authority, confidence, or proprietary metric.

Allowed pattern:

```text
[Provider] reported [metric] as [value] for [query/entity] on [date]. Treat this as provider model output, not a fact about the web.
```

Forbidden pattern:

```text
Keyword difficulty is 72.
```

Better:

```text
DataForSEO reported a difficulty score of 72 for this query at capture time.
```

---

### `recommendation_claim`

Meaning:
A statement telling someone what to do.

Observatory posture:

- Observatory must not store recommendations.
- Downstream consumers may generate recommendations using Observatory evidence.
- Recommendation text belongs to SearchClarity, Neon Ronin, Kaizen, or another consumer.

Allowed Observatory support pattern:

```text
Evidence pack supports downstream review; no recommendation stored in Observatory.
```

Forbidden Observatory pattern:

```text
Store recommendation: change title to X because query panel says Y.
```

---

## Evidence-family claim matrix

| Evidence family | Allowed claim | Required caveat | Forbidden claim |
|---|---|---|---|
| SERP observation | Result/page was observed in sampled SERP context | date, provider, query, locale/device, volatility | universal rank, guaranteed rank, causal improvement |
| Ranking observation | Rank/position observed in specific sample | point-in-time, panel/run, update-window if relevant | `you rank X everywhere` |
| Keyword demand / volume | Provider reported demand/volume estimate | provider-attributed estimate, capture date | actual traffic/sales guarantee |
| Provider score/difficulty | Provider reported proprietary score | provider model output, not fact | true difficulty/authority as web fact |
| AI answer mention | Entity was mentioned in sampled AI response(s) | prompt/panel, sample size, surface, volatility | universal AI visibility/rank |
| AI citation | URL/domain was cited in sampled response(s) | citation is not influence; sample-bound | citation caused answer; AI trusts source |
| AI absence | Entity/citation was not observed in sampled run | sampled absence only | absent from AI search |
| Public page snapshot | Page content was observed at capture time | current-page claims require recapture | page currently says X if stale |
| Public marketplace observation | Listing/search result observed in specific public context | platform, date, capture method, rights posture, volatility | marketplace-wide rank, traffic/sales inference |
| Customer first-party overlay | Consumer-supplied overlay used at read time | not stored; consumer supplies freshness | Observatory stored/verified private analytics |
| Internal telemetry | Only after future admission | internal-scope contract required | admitted merely because owner-controlled |
| Raw provider payload | Raw response existed and hashed if retention allows | rights/retention/pointer/hash caveats | raw payload is strategy truth |

---

## Report-safe phrase patterns

### Observation pattern

```text
Observation: On [date/time], [source/surface] showed [observation] for [query/panel/context].
```

### Provider metric pattern

```text
Provider estimate: [Provider] reported [metric/value] for [query/entity] on [date]. Provider metrics are model output and may differ from other tools.
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

### Recommendation handoff pattern

```text
Downstream recommendation, if any, must be created and stored by the owning consumer. Observatory only supplies the cited evidence and caveats.
```

---

## Forbidden language list

The following phrases or claim shapes are forbidden unless later doctrine explicitly changes them:

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
Observatory recommends...
Observatory decided...
```

---

## Claim-support checklist

Before a claim is allowed into a downstream report or evidence pack, answer:

1. What exact evidence ID(s) support it?
2. What was observed, and when?
3. Which source/provider/surface produced it?
4. What query panel/version/run applies?
5. What scope and scope_class apply?
6. Are rights and retention valid?
7. What freshness_status applies?
8. What volatility_class applies?
9. Is the claim historical, current, comparative, predictive, absent, or recommendation-like?
10. Does the wording overstate the evidence?
11. Does the wording imply causality without proof?
12. Does the wording imply universal visibility from a sample?
13. Does the wording turn provider output into fact?
14. Does the wording store strategy or recommendation inside Observatory?
15. Is a recapture warning required?

If the answer is unclear, the claim must be caveated, downgraded, or blocked.

---

## Suggested claim statuses

These are M7/M8 contract candidates:

| claim_status | Meaning |
|---|---|
| `supported_with_caveat` | Evidence can support the claim only with specified caveats |
| `historical_only` | Evidence supports only a historical observation claim |
| `recapture_required` | Claim requires fresh evidence before use |
| `unsupported` | Evidence does not support the claim |
| `forbidden_overclaim` | Claim form is disallowed regardless of evidence |
| `consumer_owned_recommendation` | Claim is actually a recommendation and belongs outside Observatory |

---

## Relationship to read tools

Future read tools should not merely return evidence. They should return evidence plus claim-use warnings.

Minimum read-tool claim-safety fields:

```text
evidence_ids
claim_use_warning
freshness_status
volatility_class
recapture_recommendation
provider_attribution_required
sample_bound_warning
absence_warning
rights_retention_warning
consumer_promotion_required
```

Read tools should never return:

```text
accepted conclusion
stored recommendation
opportunity score as truth
rank guarantee
AI visibility guarantee
```

---

## Non-goals

RG8 does not authorize:

- schema design;
- migrations;
- provider admission;
- paid provider pulls;
- dashboard/report automation;
- customer data handling;
- final SearchClarity report templates;
- strategy/recommendation storage;
- customer-facing guarantees.

---

## Owner-ruling candidates

Owner ruling or later contract decision is required before:

- making any claim status automatically block a downstream report;
- approving final SearchClarity customer-facing language;
- allowing report-safe AI visibility metrics;
- allowing marketplace evidence in customer reports;
- defining report-safe evidence handles;
- converting these patterns into contract/hammers.

---

## Blockers carried forward

- M7 must turn this into a claim-safety contract or matrix.
- M8 must hammer forbidden overclaims, sampled-absence wording, stale-evidence blocking, provider-attribution language, and no recommendation storage.
- M14 read tools must expose claim-use warnings.
- M15 SearchClarity proof workflow must decide customer-facing report language.

---

## Feeds later milestones

- M7 claim-safety contract
- M8 claim-language hammers
- M14 typed read API / MCP contract
- M15 SearchClarity proof workflow

---

## Final RG8 rule

```text
Evidence may support a claim.
Evidence does not become the claim.
The stronger the claim, the fresher, narrower, and more caveated the evidence must be.
Recommendations live outside Observatory.
```
