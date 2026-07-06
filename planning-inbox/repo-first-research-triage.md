# The Observatory — Repo-First Research Triage

Status: living triage note  
Authority: none  
Purpose: identify which research questions are already partly answered by local repos before later deep research  
Created: 2026-07-06  
Path: `C:\dev\observatory\planning-inbox\repo-first-research-triage.md`

---

## 1. Purpose

This note records a first repo-grounded triage pass across the local project roots.

The goal is to avoid wasting future deep research on obvious questions that have already been answered in ancestor or adjacent project docs.

This is the same principle as the planned fresh DataForSEO pulls: do not build or research from vibes when local evidence already exists.

This note is not complete authority. It is a focus tool.

---

## 2. Roots Checked

The following local roots were present and searched/read in this first pass:

```text
C:\dev\observatory
C:\dev\v-ecosystem-docs
C:\dev\kaizen-docs
C:\dev\neon-ronin
C:\dev\searchclarity
```

Primary files/areas touched or searched included:

```text
C:\dev\observatory\00-project-overview.md
C:\dev\observatory\01-harvest-register.md
C:\dev\observatory\planning-inbox\observatory-working-notes.md

C:\dev\v-ecosystem-docs\veda\providers\dataforseo-ai-optimization.md
C:\dev\v-ecosystem-docs\transition-steward\dataforseo-capture-plan.md
C:\dev\v-ecosystem-docs\transition-steward\batch-h-dataforseo-surface-inventory.md
C:\dev\v-ecosystem-docs\transition-steward\batch-h-dataforseo-confidence-layer.md
C:\dev\v-ecosystem-docs\transition-steward\dataforseo-research-tracker.md
C:\dev\v-ecosystem-docs\transition-steward\dataforseo-json\README.md
C:\dev\v-ecosystem-docs\transition-steward\dataforseo-json\*-inventory.md

C:\dev\kaizen-docs\01-project-standard\internet-marketing-intelligence-vision.md
C:\dev\kaizen-docs\03-research-results\506-packet-030b-observatory-parking-lot-deferral-and-030a-definition-supersedence.md

C:\dev\neon-ronin\docs\core\06-review-queue.md
C:\dev\neon-ronin\docs\core\19-hammer-testing-doctrine.md
C:\dev\neon-ronin\docs\core\18-external-integration-contract.md
C:\dev\neon-ronin\docs\core\11-data-boundaries.md
C:\dev\neon-ronin\research-docs\r10-observatory-and-strategy-layer.md

C:\dev\searchclarity\docs\operations\data-sources\agent-data-acquisition-strategy.md
C:\dev\searchclarity\docs\operations\quality-control\outcome-guarantee-language-policy.md
C:\dev\searchclarity\docs\r05-client-report-history-and-market-signal-capture.md
```

Some files were only searched/snippet-read in this pass. Later deep research should re-read the exact source docs relevant to the topic being researched.

---

## 3. Major Result of This Pass

Several Observatory research topics are not blank slates.

A lot is already partly answered by:

- Observatory's own overview and harvest register;
- Veda's provider, evidence, provenance, and DataForSEO payload work;
- Kaizen's Internet Marketing Intelligence vision and later Observatory deferral;
- Neon Ronin's review queue, integration, data-boundary, and hammer doctrine;
- SearchClarity's data acquisition, claim-safety, consent, report, and customer-workflow docs.

Future deep research should start from these inherited answers, then focus only on gaps, conflicts, stale assumptions, and current external facts.

---

## 4. Topic Triage

## A. Scope / Rights / Retention Model

### Already partly answered

Observatory already selected a flat scope direction:

```text
scope + scope_class
```

Known `scope_class` values from current Observatory planning:

```text
internal
customer_engagement
market_watch
```

The harvest register says the old Veda thin Project partition becomes flat scope + scope-class, and that scope-class drives consent/retention behavior.

Current working doctrine:

```text
The Observatory does not store customers.
It stores observations made for, about, or around a scoped engagement.
```

Kaizen's Internet Marketing Intelligence vision already says cross-project reuse is desirable only when licensing, freshness, and operational rules permit.

SearchClarity docs already establish that seller-private/customer-private material requires consent and retention rules.

### Still open

- Exact `scope` record shape.
- Exact `rights_class` vocabulary.
- Exact `retention_class` vocabulary.
- Cross-customer reuse rules.
- What customer-scoped SEO observations can be generalized later, if anything.
- How customer private first-party analytics should be represented: permanent Observatory observation, SearchClarity-owned record, or read-time overlay.
- Whether customer-provided screenshots/exports ever enter Observatory or only SearchClarity.

### Focused research needed later

Repo-first research should re-read:

```text
observatory/00-project-overview.md
observatory/01-harvest-register.md
v-ecosystem-docs/veda/data-boundaries.md
v-ecosystem-docs/veda/evidence-and-source-provenance.md
kaizen-docs/01-project-standard/internet-marketing-intelligence-vision.md
searchclarity/docs/operations/records-and-consent/*
searchclarity/docs/operations/data-sources/*
```

External research only needed for provider/license/customer data handling that is not settled locally.

---

## B. Evidence ID / Citation Model

### Already partly answered

Kaizen's Hermes work has strong precedent for evidence IDs, evidence indexes, and claim-to-evidence linking.

V Ecosystem docs contain an evidence access contract with required response fields such as:

- `evidence_id`
- `gathered_at`
- `source_provider`
- `source_url`
- `freshness_status`
- `freshness_window_end`
- `trust_classification`

Observatory working notes already require evidence IDs and safe citation handles in LLM-readable evidence packs.

SearchClarity report and QC docs require claims to be supportable and customer-facing reports to avoid unsupported claims.

### Still open

- Exact Observatory ID format.
- Whether IDs are human-readable, UUID-based, prefix-based, or both.
- Difference between capture ID, observation ID, evidence ID, provider job ID, citation handle, and report-safe reference.
- Whether customer reports cite raw observation IDs or stable report evidence handles.
- How evidence IDs survive schema family changes.
- How evidence IDs point to raw payload archives and structured observations.

### Focused research needed later

Repo-first research should re-read:

```text
kaizen-docs/03-research-results/442-packet-027b-hermes-draft-output-intake-contract-v0-1.md
kaizen-docs/03-research-results/443-packet-027c-hermes-draft-output-intake-contract-manual-review.md
v-ecosystem-docs/interfaces/v-forge-evidence-access-contract.md
searchclarity/docs/operations/quality-control/*
```

---

## C. Query Panel Design

### Already partly answered

Observatory harvest register already identifies query panels as planned day-one capability:

```text
Query panels: named, versioned query sets observed consistently per scope - the longitudinal backbone.
```

SearchClarity already uses concepts like customer keyword panels, service category, competitor listings, report package tier, and source-sample needs.

DataForSEO payload inventories show that query/keyword choice strongly affects returned SERP feature families, AI Overview presence, Labs metrics, and ranked keyword visibility.

### Still open

- Exact query panel object shape.
- Panel versioning rules.
- Keyword/query grouping rules.
- How query panels differ for websites, marketplace listings, local SEO, AI citation/GEO, and market-watch scopes.
- Device/location/language/market dimensions.
- Refresh cadence.
- How many queries are needed per report tier.
- How to prevent query panels from measuring nonsense with confidence.

### Focused research needed later

Repo-first research should re-read:

```text
observatory/01-harvest-register.md
searchclarity/docs/operations/data-sources/source-sample-inventory.md
searchclarity/docs/operations/data-sources/source-sample-action-plan.md
searchclarity/docs/operations/services/etsy-listing-visibility-audit-offer-spec.md
v-ecosystem-docs/transition-steward/dataforseo-json/*inventory.md
```

External research may be needed for current GEO/AI measurement conventions and current marketplace SEO research norms.

---

## D. Freshness / Staleness / Volatility Rules

### Already partly answered

Observatory harvest register already plans freshness/staleness self-description in every read-tool response.

Kaizen IMI vision emphasizes freshness, provenance, confidence warnings, and acceptable reuse windows.

V Ecosystem audits repeatedly identify missing staleness thresholds as a real gap. That is useful scar tissue: the concept exists, but thresholds were not codified enough.

SearchClarity docs acknowledge that competitor/pricing/gig-market research gets stale and must be verified before launch.

### Still open

- Freshness windows by evidence family.
- Volatility classes by family.
- When LLM tools must say evidence is stale.
- When recapture is required before customer-facing claims.
- Whether DataForSEO provider timestamps and Observatory capture timestamps both participate in freshness.
- Difference between historical fact and current actionable evidence.

### Focused research needed later

Need a dedicated doc:

```text
freshness-staleness-volatility-model.md
```

It should start from local docs, then use current SEO/GEO volatility research only where needed.

---

## E. Report Claim Safety Model

### Already partly answered

SearchClarity has strong claim-safety language.

The outcome/guarantee language policy says customer-facing language should not guarantee rankings, traffic, sales, revenue, citations, or AI-search inclusion. It frames recommendations as diagnostic, human-reviewed, evidence-based, and recommendations to test.

SearchClarity report recommendation language should use:

```text
Observation:
Why it matters:
Recommendation:
How to implement:
Caveat:
```

SearchClarity data-source docs distinguish source-derived observations from report claims.

Kaizen/Hermes docs establish claim-to-evidence linking and caveats.

### Still open

- Exact allowed/forbidden claim matrix by Observatory evidence family.
- How customer reports cite Observatory evidence.
- How old or partial evidence must be caveated.
- How to phrase AI citation / GEO claims safely.
- How to distinguish absence observed vs absolute absence.
- How Citation/Audit Agent validates every claim.

### Focused research needed later

Repo-first research should re-read:

```text
searchclarity/docs/operations/quality-control/outcome-guarantee-language-policy.md
searchclarity/docs/operations/quality-control/qc-checklist.md
searchclarity/docs/operations/report-templates/*
kaizen-docs/03-research-results/442-447 Hermes intake contract docs
```

---

## F. Strategy Recommendation Object Shape

### Already partly answered

Kaizen IMI vision already defines reviewable opportunity candidates and strategy hypotheses grounded in traceable evidence.

It explicitly warns that Kaizen must show evidence and uncertainty and must not silently convert correlation, model output, or a single provider observation into accepted strategy.

Kaizen Result 506 separates Observatory evidence from SEO strategy layer, SearchClarity, Neon Ronin, customer work, and project-improvement logic.

SearchClarity r05 says generalized signals/scoring belong in a Neon Ronin strategy layer, not in paid-report workflow.

Neon Ronin r10 likely contains important older strategy-layer thinking, but it must be treated as ancestor/prior-art, not automatically authoritative for new Observatory.

### Still open

- Exact strategy candidate object shape.
- Whether Strategy/IMI Layer is a standalone service, workflow library, or consumer-specific adapter set.
- Which fields are common across Kaizen, Neon Ronin, SearchClarity.
- How recommendations are reviewed/promoted.
- How to store accepted outputs in the owning consumer without duplicating raw evidence.

### Focused research needed later

Repo-first research should re-read:

```text
kaizen-docs/01-project-standard/internet-marketing-intelligence-vision.md
kaizen-docs/03-research-results/506-*.md
neon-ronin/research-docs/r10-observatory-and-strategy-layer.md
searchclarity/docs/r05-client-report-history-and-market-signal-capture.md
```

---

## G. Intervention Timeline Overlay

### Already partly answered

Kaizen IMI vision wants to connect public-market evidence to project-specific goals and outcomes, and to learn from approved experiments.

SearchClarity r05 deals with report history, recommendations, outcomes, and market signal capture.

Current Observatory working notes already define the rule: Observatory can compare before/after observations against external timelines, but should not own the action records.

### Still open

- Exact overlay input shape.
- Who owns intervention records: SearchClarity, Kaizen, Neon Ronin, or project repo.
- How before/after windows are selected.
- How to avoid false causality claims.
- How to represent inconclusive results.

### Focused research needed later

Start with SearchClarity r05, Kaizen implementation-return docs, and Neon Ronin workflow/review queue docs.

---

## H. Raw Archive / Blob Storage Policy

### Already partly answered

Veda DataForSEO payload work says raw JSON must be preserved untouched and interpreted in paired inventory files.

Neon Ronin data-boundary / audit material warns against JSON sludge: provider payload snapshots must not become unbounded semantic truth.

Veda DataForSEO inventories show why raw archive is mandatory: provider payloads are deep, polymorphic, and change over time.

Current Observatory working notes say first Capture Runner target should be file-based:

```text
API pull -> raw files + metadata + hashes
```

before:

```text
raw files -> validator -> Observatory API ingest -> Postgres
```

### Still open

- Exact folder layout.
- Hashing algorithm and manifest format.
- Raw payload immutability rule.
- Blob pointer format in Postgres.
- Backup/restore rule for raw archives.
- Whether screenshots/page snapshots are stored alongside JSON or separately.
- Whether large provider payloads stay in filesystem/object storage while hot-path fields go to Postgres.

### Focused research needed later

Repo-first research should re-read:

```text
v-ecosystem-docs/transition-steward/dataforseo-json/README.md
v-ecosystem-docs/veda/schema-reference.md
v-ecosystem-docs/veda/evidence-and-source-provenance.md
neon-ronin/docs/core/11-data-boundaries.md
kaizen backup/restore retention docs if Observatory needs durability planning
```

---

## I. Hammer Test Matrix

### Already partly answered

Observatory harvest register explicitly imports Veda hammer doctrine near-wholesale.

Neon Ronin hammer doctrine states that if the system claims a boundary, lifecycle rule, permission rule, audit rule, review gate, or ownership rule, future implementation must prove it under real execution.

Neon Ronin doctrine also includes a no-fake-coverage rule.

Observatory's likely hammer categories are already named:

- persistence
- contract
- append-only
- scope isolation
- provenance
- boundary / anti-VEDA-Brain
- derivation
- rights fail-closed
- retention enforcement

### Still open

- Exact Observatory hammer matrix.
- Which hammers block capture runner v0.1.
- Which hammers block API/MCP read tools.
- Which hammers block Postgres ingest.
- Which hammers block DataForSEO provider spend.
- How provider drift detection is hammered.

### Focused research needed later

Start with:

```text
observatory/01-harvest-register.md
v-ecosystem-docs/ecosystem/decisions/ADR-006-hammer-doctrine-is-ecosystem-law.md
neon-ronin/docs/core/19-hammer-testing-doctrine.md
kaizen-docs/04-design-decisions/0006-hammer-tests-are-a-hard-gate.md
```

---

## J. Consumer Contracts

### Already partly answered

Kaizen Result 506 already names the consumer split:

- Observatory DB = evidence database
- Internet Marketing Intelligence layer = interpretation/analysis layer
- SEO strategy layer = recommendations, opportunity hypotheses, content/listing/marketplace strategy, experiments
- SearchClarity = downstream customer-facing business/service lane
- Neon Ronin = downstream business/agent operating system
- Kaizen Core DB = governance/workflow/audit/operational records

Neon Ronin docs define review queue, human approvals, permission scopes, and no autonomous publishing/spending patterns.

SearchClarity docs define customer-facing reports, customer data, data acquisition, report safety, and human approval before delivery.

### Still open

- Exact request/response contract for each consumer.
- Which read tools each consumer may call.
- Which Strategy Layer outputs each consumer may accept.
- How consumer-specific variables map to Observatory scopes and query panels.
- How accepted outputs are promoted without duplicating raw evidence.
- How Neon Ronin agents are permissioned to request analysis/capture.

### Focused research needed later

Separate future packets:

```text
searchclarity-consumer-contract.md
neon-ronin-consumer-contract.md
kaizen-consumer-contract.md
```

---

## K. DataForSEO Provider Adaptation

### Already partly answered

This is the most answered topic so far.

Veda/transition-steward already contains:

- provider posture for DataForSEO AI Optimization
- capture plan
- endpoint/surface inventory
- confidence layer
- research tracker
- real sample payloads
- paired inventories

Payload-confirmed old surfaces include:

- Google Organic SERP
- Google Organic SERP with AI Overview
- ChatGPT LLM Responses
- Keywords For Site
- Keyword Overview
- Search Intent
- Ranked Keywords
- Historical Rank Overview
- Keywords For Categories

Critical inherited rules:

- raw JSON preserved as pulled
- inventory notes separate from raw JSON
- filename must match actual payload
- provider fields are observatory inputs, not strategy conclusions
- Playground UI can mislead; validate payload path/function
- ChatGPT LLM Responses is not LLM Mentions
- docs-confirmed-only shapes must stay provisional until sampled

### Still open

- Fresh Observatory-native pulls.
- Current pricing/cost and current endpoint behavior.
- Current DataForSEO rights/storage terms.
- New AI Optimization changes since old Veda samples.
- Capture recipes.
- First provider validation milestone.
- Capture Runner implementation plan.

### Focused research needed later

This should become:

```text
05-dataforseo-provider-adaptation-plan.md
```

with first controlled pull recipes and stop conditions.

---

## L. Browser Extension / Manual Capture

### Already partly answered

Observatory harvest register records owner rulings:

- Chrome extension is a candidate capture instrument.
- It requires admission.
- It should be per-marketplace reviewed.
- Fiverr may be cleaner.
- Etsy should be cautious/manual/API-first.
- Firecrawl-like tools are fallback for off-marketplace public pages.

SearchClarity docs already warn about seller-private data, screenshots, consent, and data acquisition boundaries.

### Still open

- Exact browser extension permission model.
- Per-marketplace ToS posture.
- Visible-page capture fields.
- Screenshot/hash policy.
- How extension emits CapturePackage v0.1.
- How to prevent crawler behavior.

### Focused research needed later

External research is necessary here for current Chrome extension rules and current marketplace ToS.

---

## M. Provider Drift / Payload Fingerprinting

### Already partly answered

Not much is directly implemented, but the need is clear from Veda payload experience.

The old payload corpus demonstrates that DataForSEO payloads are polymorphic and may change by endpoint, flags, query, and time.

Current Observatory working doctrine says provider payloads are themselves observed over time.

### Still open

- Shape fingerprint algorithm.
- How to classify drift.
- How to compare nested JSON schemas without over-alerting on values.
- Drift report format.
- Breaking vs non-breaking changes.
- What new fields do before schema admission.

### Focused research needed later

This research can use prior JSON samples as local fixtures before spending fresh credits.

---

## 5. Immediate Research Queue Refinement

Based on this repo-first pass, the later research queue should be reframed.

Do not ask:

```text
What should Observatory be?
```

That is already mostly answered.

Ask:

```text
What has local doctrine already settled, what conflicts remain, and what exact implementation contract follows?
```

Recommended next planning/research docs in order:

1. `02-boundaries.md`
2. `03-llm-first-api-and-mcp-access-plan.md`
3. `04-strategy-layer-consumer-boundary.md`
4. `05-dataforseo-provider-adaptation-plan.md`
5. `06-capturepackage-v0.1.md`
6. `07-scope-rights-retention-model.md`
7. `08-evidence-id-and-citation-model.md`
8. `09-query-panel-model.md`
9. `10-freshness-staleness-volatility-model.md`
10. `11-claim-safety-model.md`
11. `12-capture-runner-v0.1-plan.md`
12. `13-provider-drift-detection-plan.md`
13. `14-hammer-matrix.md`

This is not the final roadmap. It is the obvious-question reduction pass.

---

## 6. Key Open Conflict / Nuance to Preserve

Kaizen Result 506 narrowed the parked Observatory definition and excluded customer/gig/order/report/strategy records from Observatory.

The current standalone Observatory planning has reopened the question with a clarified distinction:

```text
Customer records are excluded.
Customer SEO/GEO/SERP observations may be included when scoped, rights-labeled, provenance-complete, and governed.
```

This is not automatically a contradiction, but it must be handled explicitly.

The future boundary doc should say:

```text
Result 506 was a Kaizen parking-lot deferral, not final standalone Observatory doctrine.
Its caution survives: Observatory must not become a customer/business operations database.
The clarified standalone rule is that customer records remain outside Observatory, while customer-scoped search observations may enter under strict scope/rights/provenance controls.
```

This is important enough to keep visible.

---

## 7. Blunt Summary

The repos already answer a lot.

The biggest already-settled points:

- Observatory is evidence-only.
- Strategy belongs above/outside Observatory.
- LLM access should be shaped through tools/API, not raw DB access.
- DataForSEO is provider-observed evidence, not strategy.
- Old Veda DataForSEO payloads are useful inheritance evidence but not fresh Observatory truth.
- SearchClarity owns customer/service/report records.
- Neon Ronin owns orchestration, permissions, review queues, and agent workflow routing.
- Kaizen owns governance/decisions/improvement records.
- Raw payload preservation is mandatory.
- Provider metrics are observations, not recommendations.
- Hammers must prove boundaries under real execution.
- Paid pulls require human approval, cost ceilings, stop conditions, and clear purpose.

The biggest real research gaps:

- exact scope/rights/retention model
- exact evidence ID/citation model
- query panel model
- freshness/staleness thresholds
- claim safety matrix
- CapturePackage v0.1
- capture runner recipes
- provider drift fingerprinting
- consumer contracts

Do not research from scratch.

Harvest first. Then research the gaps.
