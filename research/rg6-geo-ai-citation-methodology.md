# RG6 — GEO / AI Citation Methodology

Status: research output
Authority: source-grounded research input; not doctrine by itself; not schema approval
Milestone: M6 — Research Gate Execution
Date: 2026-07-07

---

## Gate question

How should Observatory measure AI answer-surface mentions, citations, fan-out, volatility, and absence without overclaiming?

---

## Sources checked

Local/current sources checked during RG6:

- `01-harvest-register.md`
- `02-boundaries.md`
- `research/m5-research-gate-plan.md`
- `planning-inbox/deep-research-danger-agenda.md`
- `planning-inbox/strategy-layer-dangerous-design.md`
- `research/rg1-dataforseo-rights-retention-cost.md`
- `research/rg3-evidence-id-citation-model.md`
- `research/rg4-query-panel-model.md`
- `research/rg5-freshness-staleness-volatility.md`

Current external sources checked during RG6:

- DataForSEO AI Optimization Data API — `https://dataforseo.com/apis/ai-optimization-api`
- DataForSEO AI Optimization API pricing/family list — `https://dataforseo.com/pricing/ai-optimization`
- Google Search blog: Expanding AI Overviews and introducing AI Mode — `https://blog.google/products/search/ai-mode-search/`
- Google Search Status Dashboard ranking history — `https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history`
- ArXiv: From Citation Selection to Citation Absorption — `https://arxiv.org/abs/2604.25707`
- ArXiv: Don't Measure Once: Measuring Visibility in AI Search (GEO) — `https://arxiv.org/abs/2604.07585`
- ArXiv: Quantifying Uncertainty in AI Visibility — `https://arxiv.org/abs/2603.08924`
- ArXiv: What Gets Cited: Competitive GEO in AI Answer Engines — `https://arxiv.org/abs/2605.25517`

External-source use is narrow: these sources support AI/GEO methodology posture, not provider admission or spend approval.

---

## Current source-grounded findings

### F1 — AI answer-surface evidence is a distinct evidence family, not generic SERP evidence

The harvest register carries forward distinct AI/LLM evidence families such as mentions, citations, fan-out queries, brand entity, and AI Overview.

Implication:

- AI visibility must not be collapsed into generic rank tracking.
- AI answer-surface observations need their own evidence family, caveats, and hammers.
- AI mention, citation, source attribution, and answer influence are different observations.

---

### F2 — DataForSEO is relevant but not admitted

DataForSEO's current AI Optimization Data API page describes a data suite for generative engine optimization and AI search visibility monitoring, including structured LLM response data, AI keyword metrics, and brand/domain mentions and citations across platforms such as ChatGPT, Gemini, Google AI Overview, Claude, and Perplexity.

Its AI Optimization pricing page names endpoint families including:

- LLM Mentions
- AI Keyword Search Volume
- LLM Responses
- LLM Scraper

Implication:

- DataForSEO remains a plausible candidate provider for AI visibility evidence.
- RG6 does not admit DataForSEO.
- RG6 does not authorize paid pulls, validation pulls, recurring capture, raw retention, or provider-specific implementation.

---

### F3 — Google AI Mode / AI Overviews use query fan-out and multi-source behavior

Google says AI Mode uses a query fan-out technique, issuing multiple related searches across subtopics and data sources, then bringing results together.

Implication:

- The observed answer may depend on generated subqueries that are not visible in the user's original prompt.
- Measurement should capture provider/surface, prompt, visible answer, citations/sources, and any available query fan-out or source metadata.
- If fan-out internals are unavailable, the evidence pack must say so.

---

### F4 — One-off AI visibility measurements are unsafe

Current AI search measurement research argues that AI answer visibility varies across runs, prompt variants, platforms, and time, and that single-run point estimates can be misleading.

Implication:

- AI visibility should be measured as a sampled distribution where possible, not a one-shot truth.
- Reports should distinguish `observed in this sample` from `generally visible`.
- Read tools should preserve sample size, prompt set, platform, model/surface if available, and capture dates.

---

### F5 — Citation count and citation influence are not the same thing

Current GEO measurement research distinguishes citation selection from citation absorption: a source can be cited without materially influencing the generated answer, and influence can vary by platform.

Implication:

- Observatory should not treat citation count as the whole GEO story.
- At minimum, the methodology should separate mention, citation, citation position/prominence, cited URL/domain, and answer-text relationship.
- Deeper citation absorption scoring may remain deferred unless a later methodology gate admits it.

---

### F6 — Absence must be phrased as sampled absence

Given AI answer volatility and platform variance, absence in one run or one prompt should not be treated as universal absence.

Implication:

- Forbidden phrase: `Brand X is absent from AI search.`
- Safer phrase: `Brand X was not observed in the sampled responses for this panel/run.`
- Stronger absence claims require repeated sampling, prompt coverage, surface coverage, and time-window disclosure.

---

## Proposed AI answer-surface evidence families

This section proposes M7 contract inputs. It is not schema approval.

### `ai_prompt_observation`

What it records:

- prompt/query submitted;
- surface/provider;
- locale/language/device/account context if known;
- capture time;
- model/surface label if available;
- response text or structured response pointer if retention allows.

Purpose:
Baseline record of what was asked and what response was observed.

---

### `ai_entity_mention_observation`

What it records:

- entity/brand/domain/person/product mentioned;
- mention text span if retention allows;
- mention position or section if available;
- sentiment/tone only if source/provider supplies it or downstream consumer computes it outside Observatory.

Purpose:
Track whether and how an entity appears in answer text.

Caution:
Sentiment or tone can become interpretation. If stored, it must be provider-attributed or mechanically derived under a later contract.

---

### `ai_citation_observation`

What it records:

- cited URL;
- cited domain;
- citation position/order;
- citation anchor/context if available;
- whether the citation appears in AI Overview, AI Mode, LLM response, or another surface.

Purpose:
Track source attribution.

Caution:
Citation means source attribution in the observed answer. It does not automatically mean the cited source caused the answer or influenced the answer materially.

---

### `ai_answer_presence_observation`

What it records:

- whether an AI answer/snapshot/overview appeared at all for a prompt/surface;
- absence/presence of AI module;
- result context.

Purpose:
Track AI answer-surface triggering.

Caution:
Absence is sampled absence only.

---

### `ai_fanout_observation`

What it records:

- visible or provider-reported fan-out queries/subqueries where available;
- related searches/subtopics where available;
- provider/source metadata explaining how response was assembled.

Purpose:
Capture query expansion behavior where observable.

Caution:
If fan-out is not exposed, do not infer hidden fan-out as fact.

---

### `ai_visibility_sample_summary`

What it records:

- sample count;
- prompt set/panel version;
- observed mention count;
- observed citation count;
- surface coverage;
- time window;
- confidence/caveat labels.

Purpose:
Summarize a sample/run for read tools without pretending it is universal truth.

Caution:
This is an aggregate read model candidate. It must not become strategy, recommendation, or provider-winner logic.

---

## Minimum fields for AI observations

Every AI answer-surface observation should preserve:

```text
observation_id
evidence_id
scope_id
scope_class
query_panel_id
query_panel_version_id
panel_run_id
surface_family
provider_or_capture_instrument
model_or_surface_label if available
prompt_text or prompt_hash/pointer
prompt_language
prompt_locale
prompt_device_or_context if applicable
captured_at
provider_reported_time if available
rights_class
retention_class
freshness_status
volatility_class
raw_payload_id or raw_payload_pointer if permitted
```

For citations:

```text
cited_url
cited_domain
citation_position
citation_context if permitted
source_rank_or_position if provider exposes it
```

For mentions:

```text
entity_name
entity_kind
mention_present
mention_position
mention_context if permitted
```

For absence:

```text
absence_type
sample_size
prompt_set_id
surface_count
capture_window
```

---

## Methodology rules

### Rule 1 — Treat AI visibility as sampled observation, not truth

Correct:

```text
Observed in 3 of 10 sampled responses for this panel/run.
```

Forbidden:

```text
The brand ranks #3 in AI search.
```

---

### Rule 2 — Separate mention, citation, source, and influence

At minimum, distinguish:

```text
mentioned in answer
cited as source
citation position
cited URL/domain
answer text relation to source
```

Do not equate these without a separate methodology.

---

### Rule 3 — Preserve prompt/panel context

AI visibility cannot be understood without prompt and panel context.

Read tools must show:

```text
prompt/panel version
surface/provider
capture date/time
sample count
language/locale
known limitations
```

---

### Rule 4 — Use repeated sampling for stronger claims

Single-run evidence can support only point-in-time observations.

Stronger claims require:

- multiple prompts;
- repeated runs;
- defined capture window;
- same panel version;
- surface/provider disclosure;
- volatility warning.

---

### Rule 5 — Absence requires especially careful wording

Allowed:

```text
No mention was observed in this sampled run.
```

Forbidden:

```text
This brand is not visible in AI search.
```

---

### Rule 6 — Provider output remains provider testimony

DataForSEO, Google, Perplexity, ChatGPT, Gemini, Claude, or any other provider output remains observed testimony.

Provider scores, summaries, citations, response objects, or visibility metrics are observations of provider output, not facts about the web.

---

## Proposed AI visibility metrics

These are read-tool output candidates, not stored strategy conclusions.

| Metric | Meaning | Caveat |
|---|---|---|
| `mention_presence_rate` | share of sampled responses where entity was mentioned | sample-dependent |
| `citation_presence_rate` | share of sampled responses where URL/domain was cited | sample-dependent |
| `citation_count` | number of citation observations | not equal to influence |
| `citation_position` | visible order/prominence where available | platform-specific |
| `domain_share_in_sample` | share of citations held by a domain within the sample | not market-wide truth |
| `answer_surface_trigger_rate` | share of prompts where AI answer appeared | surface and time dependent |
| `sample_absence` | entity/citation not observed in sampled panel/run | not universal absence |
| `prompt_coverage` | how much of intended prompt panel was sampled | completeness caveat |

Forbidden metrics unless later owner ruling admits methodology:

```text
AI authority score
universal AI rank
guaranteed AI visibility score
AI opportunity score as truth
provider winner score
```

---

## Claim-safe language patterns

Allowed:

```text
The brand was mentioned in 4 of 12 sampled AI responses captured on 2026-07-07 across this panel.
```

```text
No citation to the domain was observed in this sampled run. This does not prove universal absence.
```

```text
The cited sources for this AI response were observed as provider-returned attribution at capture time.
```

Forbidden:

```text
You rank fourth in AI.
```

```text
Google AI trusts your competitor more.
```

```text
Your brand is absent from AI search.
```

```text
This citation caused the answer.
```

```text
You will gain AI citations by doing X.
```

---

## Relationship to query panels

RG4 query panels define what to ask consistently.

RG6 AI methodology defines how to interpret AI answer-surface observations produced by those panels.

An AI query panel should include:

```text
prompt text
prompt category
surface/provider
locale/language
sample count target
capture window
entity/domain targets
competitor/entity comparison set if applicable
```

But it should not include:

```text
recommendation
opportunity score
content strategy
accepted conclusion
```

---

## Relationship to freshness / volatility

RG5 should treat AI answer-surface evidence as high volatility by default.

AI visibility read tools should usually include:

```text
freshness_status
volatility_class: high
sample_size
capture_window
recapture_recommendation
```

Strong current claims should usually require very recent sampling or recapture.

---

## Relationship to provider admission

RG6 does not admit any provider.

Later provider-admission work must decide:

- whether DataForSEO AI Optimization is admitted;
- whether Google AI Mode / AI Overview SERP capture is admitted;
- whether manual LLM probe capture remains allowed;
- whether any direct model/API probing is killed, deferred, or admitted;
- how raw payloads and responses may be retained.

---

## No-nonsense checks

Before an AI visibility claim is supported, the evidence pack should answer:

1. Which surface/provider was observed?
2. Which prompt or panel version was used?
3. How many samples were captured?
4. Across what time window?
5. Was the entity mentioned?
6. Was the entity cited, or only mentioned?
7. Was a URL/domain cited?
8. Was citation position captured?
9. Was answer text influenced by the source, or merely cited?
10. Is absence only sampled absence?
11. Does the claim overstate the sample?
12. Are rights and retention valid?
13. Is recapture required because of volatility?

If these cannot be answered, the output must use a caveat or block the claim.

---

## Non-goals

RG6 does not authorize:

- schema design;
- migrations;
- provider admission;
- DataForSEO spend;
- Google/LLM probing infrastructure;
- recurring AI monitoring;
- dashboard work;
- customer data handling;
- strategy/recommendation storage;
- AI visibility scoring as truth;
- customer-facing guarantees.

---

## Owner-ruling candidates

Owner ruling or later contract decision is required before:

- admitting DataForSEO AI Optimization as a provider;
- approving any AI Optimization validation spend;
- using direct manual probes beyond occasional observation-point-in-time captures;
- storing raw AI responses long term;
- making AI visibility metrics report-safe;
- adopting repeated-sampling thresholds;
- admitting citation-absorption or influence scoring;
- adding AI answer-surface monitoring to recurring capture.

---

## Blockers carried forward

- M7 must turn AI observation families and claim-safe language into contracts.
- M8 must hammer sampled-absence language, high-volatility warnings, no universal AI-rank claims, and no strategy storage.
- RG8 must convert this methodology into a broader claim-safety matrix.
- M13 must decide provider/capture admission before any paid pull or repeatable capture.
- M15 must decide SearchClarity report-safe AI visibility language.

---

## Feeds later milestones

- M7 AI answer-surface contract inputs
- M8 AI claim-safety and volatility hammers
- M10 schema planning
- M13 provider/capture admission
- M14 typed read API / MCP contract
- M15 SearchClarity proof workflow

---

## Final RG6 rule

```text
AI visibility is sampled evidence.
Mention is not citation.
Citation is not influence.
Absence is not universal absence.
No AI answer-surface observation becomes strategy inside Observatory.
```
