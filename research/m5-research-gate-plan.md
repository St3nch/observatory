# M5 Research Gate Plan

Status: research gate plan
Authority: planning input; not research execution; not implementation approval
Purpose: define M6 research gates before contracts, schema, provider admission, API/MCP work, or implementation
Date: 2026-07-07

---

## Scope

This document closes the first major M5 deliverable: defining the research gates that M6 may execute.

M5 is planning only.

This plan does not authorize:

- web research execution;
- provider purchases;
- paid provider pulls;
- schema design;
- migrations;
- API/MCP implementation;
- dashboard work;
- customer-data handling;
- strategy/recommendation storage.

---

## Governing boundaries

Every research gate must preserve M4 boundary law:

- Observatory stores observations, not conclusions.
- Strategy / IMI is read-time/process only, not Observatory storage.
- Customer records and customer first-party analytics stay outside Observatory.
- Customer first-party series are read-time overlays only unless future owner ruling changes the law.
- Provider scores are provider-attributed observations, not facts about the web.
- Provider disagreement remains first-class evidence.
- Workspace-derived or sanitized operational signals do not become Observatory evidence.
- Cross-scope aggregate analysis is forbidden by default unless owner ruling creates a governed exception.
- Hidden candidate caches, scratch schemas, or session-note tables are forbidden if they preserve interpretive outputs.
- No direct SQL or credentials for LLMs/agents.
- Hammer tests remain a hard gate before implementation acceptance.

---

## Source priority rules

Research gates should follow this source order:

1. Live Observatory authority docs.
2. Planning-inbox reconciliation notes.
3. Local ancestor/sibling repo source docs named by `repo-first-research-triage.md`.
4. Current official/provider/legal/platform docs where facts may have changed.
5. Current reputable third-party sources only where official docs are insufficient.

Research must cite sources and distinguish:

- source fact;
- local doctrine;
- steward interpretation;
- open assumption;
- owner ruling required.

---

## Gate template

Each M6 research output must include:

```text
Gate ID:
Name:
Status:
Question:
Why it matters:
Required local sources:
Required current external sources:
Output doc:
Completion rule:
Boundary constraints:
Owner rulings likely needed:
Feeds milestone:
```

---

## M6 execution order

M6 should execute gates in this order unless an owner ruling changes priority:

1. RG1 — DataForSEO Rights / Retention / Cost Gate
2. RG2 — Scope / Rights / Retention Model Gate
3. RG3 — Evidence ID / Citation Model Gate
4. RG4 — Query Panel Model Gate
5. RG5 — Freshness / Staleness / Volatility Gate
6. RG6 — GEO / AI Citation Methodology Gate
7. RG7 — Marketplace Evidence Ceiling Gate
8. RG8 — Claim Safety / Report Language Gate
9. RG9 — Provider Cross-Check & Disagreement Model Gate
10. RG10 — CapturePackage v0.1 Inputs Gate
11. RG11 — Raw Archive / Provider Drift Gate
12. RG12 — Consumer Contract Inputs Gate
13. RG13 — Hammer Matrix Inputs Gate

Rationale:

- RG1 blocks provider spend and validates whether DataForSEO can be safely used.
- RG2/RG3/RG4 define the core evidence contract spine before methodology details.
- RG5/RG6/RG7 define honest measurement limits.
- RG8 protects customer-facing claims.
- RG9 preserves provider disagreement before multi-provider contracts.
- RG10/RG11 prepare capture and raw payload handling without implementing them.
- RG12/RG13 feed M7 contracts and M8 hammers.

---

## RG1 — DataForSEO Rights / Retention / Cost Gate

Question:
What are the current DataForSEO rights, retention, storage, reuse, pricing, endpoint, and stop-condition requirements for Observatory use?

Why it matters:
No paid pull, provider admission, raw archive, or recurring capture can happen until the project knows what DataForSEO allows, costs, and returns now.

Required local sources:

- `planning-inbox/repo-first-research-triage.md`
- `planning-inbox/observatory-working-notes.md`
- local Veda / transition-steward DataForSEO docs named in the triage note
- prior DataForSEO payload inventories, as historical inheritance only

Required current external sources:

- official DataForSEO pricing docs
- official DataForSEO API docs for candidate endpoints
- official DataForSEO terms / data usage / retention / acceptable-use docs

Output doc:
`research/rg1-dataforseo-rights-retention-cost.md`

Completion rule:
Complete when the doc states allowed storage posture, retention caveats, endpoint list, cost model for a tiny validation pull, stop conditions, and unresolved blockers.

Boundary constraints:
No account purchase or paid pull during RG1 unless a later owner ruling explicitly authorizes it. Historical Veda samples are not fresh Observatory truth.

Owner rulings likely needed:
Whether the reserved validation budget may be used later, and under what recipe/ceiling.

Feeds milestone:
M6, M7 provider testimony contract, M13 provider admission.

---

## RG2 — Scope / Rights / Retention Model Gate

Question:
What exact scope, rights_class, and retention_class model should govern observations before schema planning?

Why it matters:
Scope, rights, and retention are the wall between evidence and customer-data contamination.

Required local sources:

- `02-boundaries.md`
- `01-harvest-register.md`
- `planning-inbox/repo-first-research-triage.md`
- SearchClarity records/consent and data-source docs named by the triage note
- Veda evidence/provenance and data-boundary docs named by the triage note

Required current external sources:
Only if current platform/provider/legal rules are needed for a specific rights class.

Output doc:
`research/rg2-scope-rights-retention-model.md`

Completion rule:
Complete when the doc proposes vocabularies, non-goals, unresolved owner rulings, and examples for internal, customer_engagement, and market_watch scopes.

Boundary constraints:
Must not admit customer records or customer first-party analytics storage.

Owner rulings likely needed:
Any cross-customer reuse rule, any retention exception, and any owned first-party storage beyond current boundary law.

Feeds milestone:
M7 scope/rights/retention contract, M8 fail-closed hammers, M10 schema planning.

---

## RG3 — Evidence ID / Citation Model Gate

Question:
What ID and citation-handle model lets Observatory evidence be stable, human-citable, raw-payload-linked, and safe for LLM evidence packs?

Why it matters:
Evidence IDs are hard to retrofit and every later report, contract, and hammer depends on them.

Required local sources:

- `planning-inbox/repo-first-research-triage.md`
- Kaizen Hermes evidence/intake docs named in triage
- Veda evidence access contract named in triage
- SearchClarity QC/report docs named in triage

Required current external sources:
None unless a current citation or audit standard is needed.

Output doc:
`research/rg3-evidence-id-citation-model.md`

Completion rule:
Complete when the doc distinguishes capture IDs, provider job IDs, observation IDs, evidence IDs, citation handles, raw payload pointers, and report-safe handles.

Boundary constraints:
IDs must not encode private customer identity and must survive family/schema evolution.

Owner rulings likely needed:
Whether report-safe handles differ from internal evidence IDs.

Feeds milestone:
M7 evidence ID/citation contract, M8 citation hammers, M14 read API/MCP contract.

---

## RG4 — Query Panel Model Gate

Question:
What query panel model should define longitudinal observation sets by scope, version, surface, locale, device, language, and intent?

Why it matters:
Query panels are the backbone for recurring observation, cost control, and honest before/after comparison.

Required local sources:

- `01-harvest-register.md`
- `planning-inbox/repo-first-research-triage.md`
- SearchClarity source-sample/service docs named in triage
- DataForSEO payload inventories named in triage

Required current external sources:
Current GEO/AI measurement conventions only if needed to define AI-surface panels.

Output doc:
`research/rg4-query-panel-model.md`

Completion rule:
Complete when the doc proposes query panel fields, versioning rules, examples by scope_class, and no-nonsense checks.

Boundary constraints:
A query panel is a measurement program, not a strategy recommendation store.

Owner rulings likely needed:
Whether market_watch panels are allowed before provider validation spend.

Feeds milestone:
M7 query panel contract, M9 first evidence slice, M13 capture recipes.

---

## RG5 — Freshness / Staleness / Volatility Gate

Question:
What freshness and volatility classes should read tools report by evidence family before any customer-facing or strategy-adjacent interpretation?

Why it matters:
Old evidence can still be historical truth while being unsafe for current claims.

Required local sources:

- `01-harvest-register.md`
- `02-boundaries.md`
- `planning-inbox/repo-first-research-triage.md`
- Kaizen IMI and SearchClarity staleness/claim-safety docs named in triage

Required current external sources:
Current SEO/GEO volatility research where needed, especially for AI surfaces and SERP churn.

Output doc:
`research/rg5-freshness-staleness-volatility.md`

Completion rule:
Complete when the doc defines initial classes, family-specific uncertainty, recapture warnings, and read-tool language requirements.

Boundary constraints:
Freshness labels are evidence caveats, not strategy scores.

Owner rulings likely needed:
Whether any freshness class blocks customer-facing use automatically.

Feeds milestone:
M7 freshness contract, M8 staleness hammers, M14 evidence-pack output.

---

## RG6 — GEO / AI Citation Methodology Gate

Question:
How should Observatory measure AI answer-surface mentions, citations, fan-out, volatility, and absence without overclaiming?

Why it matters:
GEO/AI citation evidence is valuable but volatile, provider-mediated, and easy to overstate.

Required local sources:

- `planning-inbox/deep-research-danger-agenda.md`
- `planning-inbox/strategy-layer-dangerous-design.md`
- DataForSEO AI Optimization inheritance docs named in triage
- SearchClarity claim-safety docs named in triage

Required current external sources:
Current official/provider docs for AI-surface endpoints and current reputable methodology sources for AI search measurement.

Output doc:
`research/rg6-geo-ai-citation-methodology.md`

Completion rule:
Complete when the doc defines measurable surfaces, absence language, volatility cautions, provider limitations, and claim-safe report wording requirements.

Boundary constraints:
AI citation recommendations remain read-time candidates/promoted consumer outputs, not Observatory data.

Owner rulings likely needed:
Which AI providers/surfaces are acceptable for first evidence slice research.

Feeds milestone:
M7 AI-surface contract inputs, M8 absence/claim hammers, M15 SearchClarity proof.

---

## RG7 — Marketplace Evidence Ceiling Gate

Question:
What marketplace public evidence can Observatory safely observe for Etsy/Fiverr/etc. without storing customer-private data or violating platform ceilings?

Why it matters:
SearchClarity revenue depends on marketplace visibility, but platform ToS and private dashboard boundaries matter.

Required local sources:

- `02-boundaries.md`
- SearchClarity Etsy/Fiverr/service/data-source docs named in triage
- `planning-inbox/repo-first-research-triage.md`
- browser extension/manual capture notes in harvest/register if applicable

Required current external sources:
Current marketplace official API docs, platform rules, and public-data access terms for each candidate marketplace.

Output doc:
`research/rg7-marketplace-evidence-ceiling.md`

Completion rule:
Complete when the doc classifies per-marketplace evidence as allowed public observation, customer-private overlay only, forbidden, or owner-ruling required.

Boundary constraints:
No customer seller dashboard data enters Observatory. No crawler/admission decision happens in this gate.

Owner rulings likely needed:
Whether any manual or extension-based capture family should remain deferred or be killed.

Feeds milestone:
M7 capture/package contracts, M13 provider/capture admission, M15 SearchClarity proof.

---

## RG8 — Claim Safety / Report Language Gate

Question:
What claims can be made from each evidence family, and what caveats are required for reports, audits, and LLM evidence packs?

Why it matters:
Evidence is only useful if it cannot be inflated into ranking guarantees, fake causality, or unsupported GEO claims.

Required local sources:

- SearchClarity outcome/guarantee policy and QC docs named in triage
- Kaizen Hermes claim/evidence docs named in triage
- `02-boundaries.md`
- M4 boundary outputs

Required current external sources:
Only if current platform/provider language is needed for claim safety.

Output doc:
`research/rg8-claim-safety-report-language.md`

Completion rule:
Complete when the doc provides an allowed/forbidden claim matrix by evidence family and standard caveat patterns.

Boundary constraints:
Claim wording is downstream guidance, not Observatory strategy storage.

Owner rulings likely needed:
Whether SearchClarity report wording rules should become a consumer contract later.

Feeds milestone:
M7 claim language matrix, M15 SearchClarity proof.

---

## RG9 — Provider Cross-Check & Disagreement Model Gate

Question:
How should Observatory represent provider disagreement without selecting a truth-provider or averaging disagreement into fake truth?

Why it matters:
Provider disagreement is a core edge and future contract candidate.

Required local sources:

- `02-boundaries.md`
- `planning-inbox/knowledgebase-reconciliation.md`
- `planning-inbox/m4-boundary-reconciliation.md`
- DataForSEO inheritance docs
- prior owner notes on Ahrefs/Semrush/DataForSEO comparison posture

Required current external sources:
Current provider documentation only as needed to understand comparable surfaces and score definitions.

Output doc:
`research/rg9-provider-cross-check-disagreement-model.md`

Completion rule:
Complete when the doc defines disagreement entities, comparison warnings, provider personality/proprietary-score treatment, and read-tool output expectations.

Boundary constraints:
No provider winner logic. No truth score. No provider purchase.

Owner rulings likely needed:
Whether Provider Cross-Check gets its own standalone contract in M7.

Feeds milestone:
M7 Provider Cross-Check contract, M16 proof.

---

## RG10 — CapturePackage v0.1 Inputs Gate

Question:
What fields must every future capture package contain before raw payloads or observations can be admitted?

Why it matters:
CapturePackage is the bridge between source/payload/cost/rights/provenance and later storage or read tools.

Required local sources:

- `02-boundaries.md`
- `01-harvest-register.md`
- `planning-inbox/repo-first-research-triage.md`
- DataForSEO capture inheritance docs
- SearchClarity data acquisition docs

Required current external sources:
Only when needed for provider/platform-specific required fields.

Output doc:
`research/rg10-capturepackage-v0-1-inputs.md`

Completion rule:
Complete when the doc defines required fields, invalid examples, rights fail-closed behavior, raw pointer/hash expectations, and human approval hooks.

Boundary constraints:
No capture runner implementation. No provider call.

Owner rulings likely needed:
Whether tactic/manual captures are in scope later.

Feeds milestone:
M7 CapturePackage contract, M8 hammers, M13 provider admission.

---

## RG11 — Raw Archive / Provider Drift Gate

Question:
How should raw payloads be archived, hashed, inventoried, and compared over time so provider drift becomes evidence instead of breakage?

Why it matters:
Provider payloads are polymorphic and change. Raw preservation and drift fingerprints protect future contracts.

Required local sources:

- Veda DataForSEO raw payload and inventory docs named in triage
- `planning-inbox/repo-first-research-triage.md`
- `02-boundaries.md`
- backup/restore doctrine if needed later

Required current external sources:
Only if current provider payload docs changed materially.

Output doc:
`research/rg11-raw-archive-provider-drift.md`

Completion rule:
Complete when the doc proposes raw archive layout, hash/manifest expectations, shape fingerprint approach, and drift classification vocabulary.

Boundary constraints:
No raw provider payloads are pulled in this gate.

Owner rulings likely needed:
Whether raw archive should be filesystem-first, object-storage-first, or hybrid later.

Feeds milestone:
M7 raw archive/payload pointer contract, M8 drift hammers, M12 first slice.

---

## RG12 — Consumer Contract Inputs Gate

Question:
What must SearchClarity, Neon Ronin, Kaizen, and future project consumers receive from Observatory, and what must remain outside Observatory?

Why it matters:
The Observatory is useful only if consumers can cite evidence without contaminating storage boundaries.

Required local sources:

- SearchClarity docs named in triage
- Neon Ronin review queue/integration/boundary docs named in triage
- Kaizen governance/evidence docs named in triage
- `02-boundaries.md`
- M4 boundary outputs

Required current external sources:
None unless a consumer's external platform dependency requires current checks.

Output doc:
`research/rg12-consumer-contract-inputs.md`

Completion rule:
Complete when the doc defines consumer request/response needs, ownership boundaries, allowed outputs, and promotion/citation expectations.

Boundary constraints:
No customer records, workflow state, or accepted decisions move into Observatory.

Owner rulings likely needed:
Whether SearchClarity should be the first consumer proof in M15.

Feeds milestone:
M7 consumer contracts, M14 read API/MCP contract, M15 proof workflow.

---

## RG13 — Hammer Matrix Inputs Gate

Question:
What hostile-path tests must exist before Observatory accepts implementation, provider capture, read tools, or customer-adjacent evidence support?

Why it matters:
Boundaries are only real if hostile paths fail under execution.

Required local sources:

- `02-boundaries.md`
- `01-harvest-register.md`
- Neon Ronin hammer doctrine named in triage
- Kaizen hammer decisions named in triage
- M4 boundary outputs

Required current external sources:
None unless a platform/provider requirement changes hammer expectations.

Output doc:
`research/rg13-hammer-matrix-inputs.md`

Completion rule:
Complete when the doc maps boundary claims to required hammers and names which later milestone each hammer blocks.

Boundary constraints:
No test implementation yet unless a later milestone explicitly authorizes it.

Owner rulings likely needed:
Whether hammers become a standalone `hammers/` folder at M8 as planned.

Feeds milestone:
M8 hammer matrix and acceptance gates.

---

## M5 completion checklist

M5 can close when:

- this gate plan exists;
- `research/README.md` indexes it;
- each M6 gate has question, output doc, source plan, completion rule, and boundary constraints;
- M6 execution order is explicit;
- `ACTIVE_CONTEXT.md` and `NEXT_SESSION_HANDOFF.md` can point to M6;
- changes are committed.

---

## M7 audit addendum (2026-07-07) — planned topics to executed gates mapping

ROADMAP's planned-M5 section listed 12 research gate topics; this plan defined 13 gates cut differently. So future stewards do not think topics were silently dropped, the mapping is:

| ROADMAP M5 topic | Where it landed |
|---|---|
| DataForSEO rights / retention / cost | RG1 |
| marketplace evidence ceiling | RG7 |
| GEO / AI citation methodology | RG6 |
| Provider Cross-Check & Disagreement Model | RG9 |
| provider personality profiles / proprietary score treatment | folded into RG9 (and RG8 provider-metric claim rules) |
| freshness / staleness / volatility | RG5 |
| claim-safety language | RG8 |
| negative evidence / absence rules | folded into RG6 (absence methodology) + RG8 (absence claim class); M7 folds the absence-rules contract into the claim-safety contract |
| surface coverage / blind spots | NOT given a dedicated gate. Passing mentions in RG4/RG5 read-tool output lists only. Disposition per M7 audits: NC5 coverage/blind-spot output fields belong in the typed read-tool contract skeleton (ruling OR-A5 in the owner-ruling tracker) |
| owned property telemetry boundary | folded into RG2 (internal scope) + RG12 (internal consumer) + DR11 (deferred deep research) |
| CapturePackage v0.1 inputs | RG10 |
| evidence ID / citation model needs | RG3 |

Gates added beyond the original 12 topics: RG2 (scope/rights/retention model), RG4 (query panel model), RG11 (raw archive / provider drift), RG12 (consumer contract inputs), RG13 (hammer matrix inputs). RG13 later gained an M7 addendum adding H19–H22.

---

## Final rule

```text
M5 plans the hunt.
M6 does the hunting.
Nothing gets bought, pulled, migrated, or built in M5.
```
