# RG5 — Freshness / Staleness / Volatility

Status: research output
Authority: source-grounded research input; not doctrine by itself; not schema approval
Milestone: M6 — Research Gate Execution
Date: 2026-07-07

---

## Gate question

What freshness and volatility classes should read tools report by evidence family before any customer-facing or strategy-adjacent interpretation?

---

## Sources checked

Local/current sources checked during RG5:

- `01-harvest-register.md`
- `02-boundaries.md`
- `research/m5-research-gate-plan.md`
- `planning-inbox/repo-first-research-triage.md`
- `research/rg1-dataforseo-rights-retention-cost.md`
- `research/rg2-scope-rights-retention-model.md`
- `research/rg3-evidence-id-citation-model.md`
- `research/rg4-query-panel-model.md`

Current external sources checked during RG5:

- Google Search Status Dashboard — Ranking history: `https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history`
- Google blog — Expanding AI Overviews and introducing AI Mode: `https://blog.google/products/search/ai-mode-search/`
- ArXiv — Measuring Google AI Overviews: Activation, Source Quality, Claim Fidelity, and Publisher Impact: `https://arxiv.org/abs/2605.14021`
- ArXiv — How Generative AI Disrupts Search: An Empirical Study of Google Search, Gemini, and AI Overviews: `https://arxiv.org/abs/2604.27790`

External-source use is narrow: these sources support volatility posture, not implementation or provider admission.

---

## Current source-grounded findings

### F1 — Freshness/staleness self-description is already planned as day-one behavior

The harvest register names freshness/staleness self-description as a planned capability:

```text
Freshness/staleness self-description: every read-tool response declares observation age and volatility class.
```

Implication:

- Freshness is not optional UI decoration.
- Every evidence pack must say how old the observations are and how volatile the observed surface is expected to be.
- Read tools should expose caveats by default, not only when asked.

---

### F2 — Search ranking surfaces change over multi-day update windows

The Google Search Status Dashboard reports ranking incidents and updates with durations ranging from hours to many days. Recent examples include 2026 ranking updates such as a June 2026 spam update, May 2026 core update, March 2026 core update, and February 2026 Discover update.

Implication:

- SERP/ranking evidence can be historically true but unsafe for current claims.
- Evidence captured during a ranking update window should carry a volatility caveat.
- Recapture may be required before customer-facing claims when major updates are active or recently completed.

---

### F3 — AI answer surfaces are changing and should be treated as high volatility

Google's March 2025 Search blog says AI Overviews were expanding and that AI Mode uses query fan-out across related searches and multiple data sources.

Current 2026 academic measurement papers report that AI Overviews and generative search can differ from traditional ranking results, can vary by query form or surface, and can be inconsistent under repeated or slightly edited queries.

Implication:

- AI answer-surface evidence should default to high volatility unless later RG6 methodology proves a tighter class.
- AI citation absence is not absolute absence.
- AI citation presence is an observation at capture time, not a durable ranking position.

---

### F4 — Query panel versioning and freshness are separate concepts

RG4 says panel versions should not change merely because results change or evidence is stale.

Implication:

- A panel version defines what is observed.
- Freshness describes when the evidence was observed and how safe it is to reuse.
- Stale evidence does not automatically mean the panel is stale.

---

### F5 — Provider-reported timestamps and Observatory capture timestamps both matter

`02-boundaries.md` says provider evidence should preserve capture time and provider-reported timestamps when available.

Implication:

- Read tools must distinguish `captured_at` from provider-side reported time.
- Provider data may be stale before Observatory captures it.
- Freshness classification should consider both provider freshness and Observatory observation age where available.

---

## Proposed freshness vocabulary

This section proposes M7 contract inputs. It is not schema approval.

| freshness_status | Meaning | Read-tool posture |
|---|---|---|
| `fresh_for_current_claims` | Evidence is recent enough for cautious current claims for its evidence family | Can support current statements with normal caveats |
| `usable_with_caveat` | Evidence may support current analysis but requires age/volatility caveat | Must display caveat |
| `historical_only` | Evidence is valid history but should not support current-state claims | Use for trend/history only |
| `recapture_recommended` | Evidence is too old or surface too volatile for confident current use | Suggest recapture before customer-facing use |
| `recapture_required_for_claim` | Evidence cannot support the proposed claim without new capture | Block claim support until recaptured |
| `stale_unknown` | Freshness cannot be determined | Fail closed for current claims |

Recommended default:

```text
unknown capture time -> freshness_status: stale_unknown
```

---

## Proposed volatility vocabulary

| volatility_class | Meaning | Examples |
|---|---|---|
| `low` | Surface usually changes slowly enough that older evidence may remain useful with modest caveats | stable public page metadata, static docs, archived source pages |
| `medium` | Surface can change materially over days/weeks | ordinary SERP snapshots, marketplace listing pages, provider Labs estimates |
| `high` | Surface can change materially over hours/days or across query/session variants | AI answer surfaces, competitive SERPs, local/mobile SERPs, marketplace search results |
| `update_window` | Known active/recent system update, incident, rollout, or provider drift window affects interpretation | Google core/spam/Discover update windows, major AI-surface rollout windows |
| `unknown` | Volatility not yet classified | New provider/surface/family until researched |

Recommended default:

```text
new evidence family -> volatility_class: unknown -> current claims require caveat or recapture
```

---

## Proposed evidence-family defaults

These are initial contract-planning defaults. M7/RG6/RG7/M13 may refine them.

| Evidence family | Default volatility | Initial reuse posture |
|---|---|---|
| SERP observation | medium; high during update windows or highly competitive/local panels | Use with dated caveat; recapture before strong current claim |
| Ranking observation | medium/high | Recapture recommended before customer-facing current ranking claim |
| Keyword demand observation | medium | Use with provider/date caveat; recapture before spend/strategy decisions |
| AI answer-surface mention/citation | high | Treat as point-in-time; recapture required for strong current claim |
| Public page snapshot | low/medium depending on page type | Historical snapshot valid; current-page claims require recapture |
| Public marketplace listing observation | high | Use as point-in-time; recapture before current marketplace claim |
| Provider score/difficulty/authority metric | medium; provider-model-dependent | Provider-attributed estimate only; never fact |
| Raw provider payload | mirrors source family; also subject to provider drift | Valid raw history if retention/rights allow |
| Customer first-party overlay | not stored | Freshness supplied by external consumer at read time |
| Internal first-party telemetry | unknown until admitted | Requires internal-scope contract before storage/use |

---

## Suggested age bands

RG5 should not pretend universal age thresholds are scientific. Still, read tools need rough bands before M7 contracts and M8 hammers.

Proposed initial bands:

| Age band | Label | Use |
|---|---|---|
| `0-24h` | very recent | Best for high-volatility surfaces |
| `1-7d` | recent | Generally usable with caveat for many search surfaces |
| `8-30d` | aging | Useful for trends/history; current claims need caution |
| `31-90d` | old | Historical or broad trend only unless low-volatility family |
| `90d+` | archival | Historical evidence; current claims require recapture |
| `unknown` | unknown | Fail closed for current claims |

Rules:

- High-volatility surfaces should often require `0-24h` or `1-7d` evidence for current claims.
- Medium-volatility surfaces may tolerate `1-7d` or sometimes `8-30d` with caveats.
- Low-volatility surfaces may use older evidence if the claim is about historical content or stable source facts.
- These are starting bands for contracts and hammers, not final product promises.

---

## Read-tool output requirements

Every future evidence pack should include:

```text
captured_at
provider_reported_time if available
observation_age
age_band
freshness_status
volatility_class
freshness_reason
recapture_recommendation
claim_use_warning
```

If tied to a query panel, include:

```text
query_panel_id
query_panel_version_id
panel_run_id
surface_family
```

Read-tool warnings should be plain-language, for example:

```text
Observed on 2026-07-07 for Google desktop US. Search results may differ by date, location, device, personalization, and active ranking updates.
```

For AI answer surfaces:

```text
Observed on 2026-07-07 for this prompt/provider/surface. AI answer surfaces are volatile; absence or presence should not be treated as universal.
```

---

## Claim-use matrix

| Proposed claim type | Minimum freshness posture |
|---|---|
| Historical observation claim | evidence exists and is valid under rights/retention |
| Current SERP/ranking claim | `fresh_for_current_claims` or `usable_with_caveat`, with dated caveat |
| Current AI citation/mention claim | very recent evidence; usually recapture required for strong claim |
| Before/after comparison | same panel/version or explicitly comparable versions; caveat update windows |
| Customer-facing recommendation | Observatory evidence can support, but recommendation lives outside Observatory |
| Absolute absence claim | generally forbidden; phrase as absence observed in sampled panel/run |
| Provider score claim | only as provider-attributed estimate with capture date |

---

## Update-window handling

During known ranking/system update windows:

- classify affected SERP/ranking evidence as `volatility_class: update_window`;
- avoid strong current claims unless the purpose is to observe the update window itself;
- require caveats that the observation occurred during or near an update/incident;
- consider recapture after the window closes before customer-facing claims.

Update-window awareness may use official status pages, provider release notes, or source-specific incident/update feeds later.

---

## Relationship to RG4 query panels

Query panels provide the consistent measurement set.

Freshness rules decide whether a panel run is safe for a proposed use.

A panel can be valid while its latest evidence is stale.

A panel version can remain active while recapture is required.

---

## Relationship to RG3 evidence IDs

Evidence IDs should resolve to freshness information.

Evidence may remain citable as historical evidence even if not fresh enough for current claims.

A future evidence status such as `superseded`, `expired_by_retention`, or `blocked_by_rights` is separate from freshness but must be considered together in read tools.

---

## Relationship to customer first-party overlays

Customer first-party overlays remain outside Observatory.

If a read tool receives a customer first-party overlay at read time, the consumer must provide overlay timestamp/freshness metadata.

Observatory may align external observations against that overlay, but should not store the overlay series or assign Observatory evidence IDs to it under current law.

---

## No-nonsense checks

Before evidence supports a current claim, read tools should ask:

1. When was the evidence captured?
2. Does the provider report a different data timestamp?
3. What evidence family is this?
4. What volatility class applies?
5. Was there a known update/incident/rollout window?
6. Is the claim historical, current-state, comparative, or predictive?
7. Is the evidence from the same query panel/version?
8. Are rights/retention still valid?
9. Does the read output need a recapture warning?
10. Is the claim actually too strong for the evidence?

---

## Non-goals

RG5 does not authorize:

- schema design;
- migrations;
- provider admission;
- paid provider pulls;
- recurring capture;
- scheduler implementation;
- API/MCP implementation;
- dashboard work;
- customer data handling;
- strategy/recommendation storage;
- final freshness thresholds for every provider or marketplace.

---

## Owner-ruling candidates

Owner ruling or later contract decision is required before:

- making any freshness class automatically block customer-facing report use;
- deciding final age thresholds by evidence family;
- admitting update-window feeds as a dependency;
- allowing recurring recapture schedules;
- treating AI answer-surface evidence as report-safe without RG6 methodology;
- using customer first-party overlay freshness metadata in customer-facing conclusions.

---

## Blockers carried forward

- M7 must turn freshness and volatility into contract language.
- M8 must hammer stale-evidence warnings, recapture-required blocking, unknown timestamp fail-closed behavior, and update-window caveats.
- RG6 must refine AI answer-surface volatility and methodology.
- RG7 must refine marketplace evidence volatility and platform-specific caveats.
- M14 must expose freshness labels in typed read tools.

---

## Feeds later milestones

- M7 freshness / staleness / volatility contract
- M8 stale-evidence and update-window hammers
- M10 schema planning
- M13 provider/capture admission
- M14 typed read API / MCP contract
- M15 SearchClarity proof workflow

---

## Final RG5 rule

```text
Old evidence can still be true.
That does not make it safe for current claims.
Freshness tells the reader how hard to trust the observation right now.
Volatility tells the reader how quickly that trust decays.
```
