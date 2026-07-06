# The Observatory — Working Notes

Status: living notes  
Authority: none  
Purpose: preserve current planning ideas before roadmap/spec promotion  
Created: 2026-07-06  
Path: `C:\dev\observatory\planning-inbox\observatory-working-notes.md`

---

## 1. Role of This Note

This note is a non-authority planning inbox for The Observatory.

It exists so current ideas do not become vague, lost in chat history, or prematurely promoted into doctrine.

This file may collect:

- working architecture decisions
- doctrine phrases
- open questions
- roadmap candidates
- Claude review items
- deep research topics
- capture-runner ideas
- provider-risk notes
- strategy-layer boundary notes
- Neon Ronin / SearchClarity / Kaizen relationship notes

This file does not authorize implementation, provider spending, schema creation, API creation, MCP tools, customer-data ingestion, or roadmap closure.

---

## 2. Current High-Level Understanding

The Observatory is a standalone evidence database project at:

```text
C:\dev\observatory
```

It is related to Kaizen, Neon Ronin, SearchClarity, and the old Veda/V Ecosystem work, but it is not a subsystem of any one of them.

The Observatory exists to make a connected LLM dangerous at SEO, GEO, SERP, ranking, keyword, page-visibility, and AI-answer-surface work by giving it clean historical evidence.

The Observatory is the telescope.

The connected LLM is the astronomer.

The Observatory stores observations.

The connected LLM interprets.

The database must never become the strategy brain.

---

## 3. Core Observatory Doctrine

Current doctrine lines:

```text
The Observatory is evidence-only.
```

```text
The Observatory stores what was observed, when, by whom or by what provider, under what settings, with what rights, for what scope.
```

```text
The Observatory does not store strategy, recommendations, opportunity scores, business decisions, report conclusions, or execution plans.
```

```text
The Observatory does not store customers.
It stores observations made for, about, or around a scoped engagement.
```

```text
The database itself never forms an opinion.
The connected LLM is the interpretation layer.
```

```text
The Observatory makes the astronomer dangerous.
It never becomes the astronomer.
```

```text
Scars are cheaper than subscriptions.
But hammers are cheaper than production bugs.
```

---

## 4. LLM-First Database Direction

The Observatory should be designed LLM-first, but not by giving the LLM direct database power.

The LLM must never receive:

- direct PostgreSQL credentials
- raw SQL access
- arbitrary query tools
- direct table CRUD access
- schema mutation tools
- provider-spend tools without human approval
- direct write access to observation tables
- direct access to customer/business systems

Access chain:

```text
LLM
  -> MCP tools
  -> Observatory API
  -> validation / authorization / rights / provenance layer
  -> PostgreSQL
```

MCP tools are not database clients.

The API owns database access.

The MCP layer exposes carefully shaped, LLM-readable tool contracts.

The LLM should receive evidence packs, not raw mystery rows.

A good response to the LLM should include:

- evidence IDs
- scope
- source/provider
- capture time
- freshness/staleness status
- rights class
- retention class
- capture method
- operator intent when applicable
- fact/estimate/observation label
- comparison windows
- missing-data warnings
- provider-disagreement warnings
- blind spots
- safe citation handles

---

## 5. API/MCP Direction

The Observatory API is the authoritative access layer.

It should own:

- database connections
- schema access
- validation
- authorization
- scope isolation
- rights enforcement
- retention enforcement
- provenance enforcement
- capture package validation
- provider job accounting
- cost tracking
- audit/event recording
- typed response shaping

The MCP surface is LLM-facing and should expose bounded questions/workflows, not arbitrary database operations.

Candidate MCP/API read-tool families:

### Scope context tools

- `get_scope_summary`
- `get_scope_observation_coverage`
- `get_scope_rights_posture`
- `get_scope_query_panels`

### Evidence retrieval tools

- `get_evidence_pack`
- `get_observation_by_id`
- `get_serp_snapshot_evidence`
- `get_ai_surface_evidence`
- `get_page_snapshot_evidence`
- `get_keyword_demand_evidence`
- `get_provider_job_evidence`

### Comparison tools

- `compare_visibility_since`
- `compare_rank_movement`
- `compare_keyword_demand_since`
- `compare_ai_surface_presence_since`
- `compare_page_snapshot_changes`
- `compare_competitor_presence_since`

### Freshness / blind-spot tools

- `find_observation_blind_spots`
- `find_stale_observations`
- `report_query_panel_gaps`
- `estimate_capture_needed_for_question`
- `get_freshness_status`

### Gap-hunting tools

These return observable gaps, not stored strategy:

- `find_keyword_visibility_gaps`
- `find_weak_serp_competition`
- `find_ai_citation_absence_gaps`
- `find_competitor_coverage_gaps`
- `find_demand_without_presence`

### External overlay tools

- `align_observations_with_intervention_timeline`
- `compare_before_after_intervention`
- `align_first_party_series_with_observatory_series`

---

## 6. Strategy Layer / IMI Direction

A separate SEO/GEO/SERP strategy layer is probably needed.

This layer may also be called:

- Internet Marketing Intelligence Layer
- Search Strategy Layer
- Visibility Strategy Layer
- SEO/GEO Strategy Layer
- Evidence-to-Strategy Layer

Current preferred framing:

```text
Observatory = evidence layer
Strategy / IMI Layer = interpretation/action-candidate layer
SearchClarity / Kaizen / Neon Ronin = consumers that store, review, use, and execute accepted outputs
```

The Strategy Layer may produce:

- findings
- opportunity candidates
- keyword recommendations
- page/listing suggestions
- competitor gap interpretations
- report sections
- experiment ideas
- evidence-backed strategy drafts

The Strategy Layer must not own:

- raw evidence truth
- customer records
- final customer report delivery records
- agent execution authority
- direct provider spend authority
- direct database mutation authority

Core rule:

```text
The Strategy Layer may interpret Observatory evidence.
The Observatory may never become the Strategy Layer.
```

Temporary reasoning may live only in the LLM session.

Accepted outputs should be promoted into the appropriate consumer:

- SearchClarity for customer reports, recommendations, engagements, deliverables
- Kaizen for decisions, improvement candidates, implementation returns, governance records
- Neon Ronin for workspace tasks, agent workflows, review queues, execution coordination

---

## 7. Neon Ronin Relationship

Neon Ronin is planned as the multi-agent orchestration and multi-project management system.

Neon Ronin will manage many projects/workspaces, not only SearchClarity.

SearchClarity is expected to be one of the first major managed workspaces/services.

Neon Ronin should be above the Strategy Layer operationally, but not the owner of strategy truth or Observatory evidence.

Working stack:

```text
Neon Ronin
  = who asks, routes, approves, schedules, assigns, executes

Strategy / IMI Layer
  = what the evidence suggests

Observatory
  = what was observed

Kaizen
  = what gets governed, accepted, remembered, improved
```

Neon Ronin agents may use the Strategy Layer.

Neon Ronin agents must not directly:

- query raw Observatory SQL
- spend DataForSEO credits freely
- capture marketplace data without admitted capture rules
- store strategy inside Observatory
- auto-publish recommendations
- auto-deliver customer reports
- auto-change customer/customer-facing pages

Neon Ronin should route agent work through:

- workspace permissions
- review queues
- cost gates
- scope constraints
- human approvals
- external integration contracts

---

## 8. SearchClarity Relationship

SearchClarity is a customer-facing SEO/GEO/SERP visibility service/business.

It may use Observatory evidence and Strategy Layer outputs for:

- customer SEO audits
- marketplace visibility audits
- keyword opportunity reports
- competitor visibility analysis
- AI citation / GEO visibility reports
- before/after improvement proof
- report-grade evidence citations

SearchClarity owns:

- customer
- engagement
- order
- deliverable
- report
- customer consent
- private customer files
- private first-party analytics inputs when applicable
- report delivery history

The Observatory does not store customer records.

Customer SEO/GEO/SERP observations may be stored in Observatory when properly scoped, rights-labeled, provenance-complete, and captured through approved methods.

Allowed customer-scoped observations may include:

- SERP snapshots for customer target queries
- ranking observations
- AI-surface mention/citation observations
- keyword demand observations
- competitor observations
- public page snapshots
- public marketplace listing observations
- visibility observations over time
- provider job metadata
- capture timestamps
- rights/provenance labels

Private first-party customer analytics require stricter handling and may sometimes be read-time overlays rather than permanent Observatory storage.

Examples of private first-party data:

- Google Search Console exports
- GA4 exports
- Etsy Stats
- Shopify analytics
- seller dashboard screenshots
- private conversion data

Possible handling requirements:

- `customer_engagement` scope
- explicit consent
- retention class
- access restrictions
- no cross-customer reuse
- clear separation from generalized market intelligence
- read-time overlay when appropriate

---

## 9. SearchClarity Variables vs Website Variables

SearchClarity engagements have variables that differ from a normal website project.

SearchClarity customer engagement variables may include:

- customer engagement ID
- marketplace platform
- gig/listing URL
- package tier
- audit depth
- allowed data sources
- customer-provided screenshots/exports
- report deadline
- competitor listings
- service category
- keyword panel
- delivery format
- consent/retention rules

A normal website project may include:

- domain
- page set
- GSC data
- GA4 data
- target keywords
- competitors
- content changes
- technical SEO checks
- locality
- schema
- backlinks
- AI citations

The likely solution is a workspace/project adapter pattern.

Each managed project has its own variables, but they translate into shared Strategy Layer requests.

Examples:

```text
SearchClarity adapter:
  customer engagement -> SEO audit strategy request

Website project adapter:
  domain/page set -> website visibility strategy request

Marketplace project adapter:
  listing/shop -> marketplace visibility strategy request

Market-watch project adapter:
  product/service market -> market-watch strategy request
```

---

## 10. DataForSEO Inheritance from Veda

The old Veda / transition-steward folders contain useful DataForSEO planning and sample payload evidence.

Important paths:

```text
C:\dev\v-ecosystem-docs\veda
C:\dev\v-ecosystem-docs\veda\providers
C:\dev\v-ecosystem-docs\transition-steward
C:\dev\v-ecosystem-docs\transition-steward\dataforseo-json
```

Important inherited docs inspected:

- `veda/providers/dataforseo-ai-optimization.md`
- `transition-steward/dataforseo-capture-plan.md`
- `transition-steward/batch-h-dataforseo-surface-inventory.md`
- `transition-steward/batch-h-dataforseo-confidence-layer.md`
- `transition-steward/dataforseo-research-tracker.md`
- `transition-steward/dataforseo-json/README.md`
- representative inventory notes in `transition-steward/dataforseo-json`

Inheritance posture:

```text
The old Veda dataforseo-json corpus is inheritance evidence, not fresh Observatory truth.
```

Use it for:

- schema intuition
- endpoint awareness
- known gotchas
- capture planning
- field-shape expectations
- confidence-layer doctrine
- cost-aware sampling rules

Do not use it as:

- production Observatory truth
- current endpoint proof
- current pricing proof
- current model behavior proof
- fresh customer/project evidence

At the correct roadmap point, Observatory should spend fresh DataForSEO credits through controlled API pulls, not random Playground use.

---

## 11. DataForSEO Payload Corpus Findings

Representative Veda-era payload inventories show that DataForSEO surfaces are structurally rich and should not be flattened.

### SERP Google Organic Advanced

Observed as a polymorphic typed-item stream, not a flat result list.

Observed item families include:

- `organic`
- `ai_overview`
- `people_also_ask`
- `people_also_search`
- `perspectives`
- `discussions_and_forums`
- `related_searches`
- `top_stories`

Implication:

```text
Do not build one caveman serp_results table and cram every SERP feature into nullable columns.
```

### AI Overview

AI Overview is a first-class evidence family.

It may include:

- presence/absence
- rank placement
- asynchronous flag
- markdown/text
- child elements
- references/citations
- top-level references
- element-local references

Important capture setting:

```text
load_async_ai_overview = true
```

If AI Overview observability matters, capture config must explicitly control async AI Overview loading.

### ChatGPT LLM Responses

The ChatGPT LLM Responses payload is answer-behavior evidence, not only citation data.

It may include:

- requested prompt
- requested model
- system-message presence
- requested web_search
- actual returned web_search
- resolved model
- token counts
- money_spent
- typed response items
- typed sections
- reasoning summary item
- message item
- fan_out_queries presence/absence

Important finding:

```text
Requested web_search and actual web_search can diverge.
```

Both must be preserved.

Fan-out query absence is itself meaningful evidence.

### Keyword Overview

Keyword Overview is a compact keyword-centric provider metric surface.

It may include:

- search volume
- monthly searches
- search volume trend
- competition
- CPC
- keyword difficulty
- SERP info
- average backlink context
- search intent info
- categories

Important cautions:

- long monthly history should not be flattened too early
- provider keyword difficulty is an observation, not strategy truth
- `ai_search_volume` and normal `search_volume` must remain distinct if/when both appear

### Ranked Keywords

Ranked Keywords is a strong domain visibility surface.

It may include:

- domain-level aggregate rank-bucket metrics
- per-keyword provider context
- target-domain ranked SERP element
- rank group
- rank absolute
- URL/domain/title
- ETV
- estimated paid traffic cost
- rank changes
- rank info
- search intent
- SERP feature signature

This is not just keyword discovery.

It is domain visibility state by keyword.

### Historical Rank Overview

Historical Rank Overview is a monthly aggregate domain visibility time-series surface.

It may include:

- monthly rank bucket counts
- historical ETV
- estimated paid traffic cost
- movement-state counts
- organic/paid metric families

It does not provide row-level keyword/page detail.

Working distinction:

```text
Ranked Keywords = current/detail visibility
Historical Rank Overview = aggregate/monthly visibility trend
```

---

## 12. DataForSEO Confidence Layer

The Veda-era work separated provider understanding into confidence levels.

This should be carried forward.

### Payload-confirmed

Grounded in actual saved JSON payloads.

Currently payload-confirmed in the old corpus:

- Google Organic SERP
- Google Organic SERP with AI Overview
- ChatGPT LLM Responses
- Keywords For Site
- Keyword Overview
- Search Intent
- Ranked Keywords
- Historical Rank Overview
- Keywords For Categories

### Docs-confirmed only / unsampled

Grounded in documentation or planning, but not actual saved payloads in the old corpus.

Examples:

- LLM Mentions
- LLM Scraper
- Gemini LLM Responses
- Claude LLM Responses
- Perplexity LLM Responses
- AI Keyword Data
- AI Mention Cluster family

Doctrine:

```text
Do not fully canonize unsampled provider shapes.
Mark them deferred-but-owned or provisional until payload-confirmed.
```

---

## 13. DataForSEO Credits / Spend Posture

User has approximately $50 reserved and waiting for the right Observatory milestone.

This should be treated as provider-validation fuel, not random exploration money.

Wrong posture:

```text
I have $50. Let us see what explodes.
```

Correct posture:

```text
I have $50 reserved for the first Observatory provider-validation milestone.
```

Before spending, Observatory should have:

- boundaries
- LLM-first API/MCP plan
- Strategy Layer boundary
- CapturePackage v0.1
- DataForSEO provider adaptation plan
- cost-control rules
- raw archive format
- inventory format
- hammer matrix
- capture recipes
- controlled capture runner

Only then should the first fresh Observatory DataForSEO pulls happen.

---

## 14. Capture Runner Direction

The DataForSEO Playground is useful for exploration, but Observatory should not rely on manual dropdown selection for real captures.

A small controlled app should be built eventually.

Working names:

- `observatory-capture-runner`
- `dataforseo-capture-console`
- `DataForSEO Capture Runner`

Purpose:

```text
The Capture Runner exists so Observatory never receives mystery data.
```

It should use approved capture recipes instead of manual dropdown choices.

It should:

- choose approved recipe
- fill known-safe DataForSEO settings
- allow only approved variables
- estimate or record cost
- show warning/approval gate
- run API pull
- save raw JSON untouched
- save request JSON
- save metadata JSON
- hash files
- create inventory/review stub
- emit CapturePackage v0.1

Initial version should not write directly to Postgres.

Preferred first target:

```text
API pull -> raw files + metadata + hashes
```

Later target:

```text
raw files -> validator -> Observatory API ingest -> Postgres
```

---

## 15. Capture Recipe Doctrine

Every provider pull must be recipe-driven.

A recipe should answer:

- What are we pulling?
- Why are we pulling it?
- Which endpoint is it from?
- Which settings are locked?
- Which variables are allowed?
- What will this cost or cost ceiling be?
- What observation families might this feed?
- What should stay raw only?
- What must not be inferred from it?

Example recipe fields:

```yaml
recipe_id: dataforseo_labs_keyword_overview_v1
provider: dataforseo
endpoint_family: labs_keyword_overview
purpose: Capture provider keyword metrics for one keyword.

locked_settings:
  search_engine: google
  location_code: 2840
  language_code: en
  include_serp_info: true
  include_clickstream_data: false

requires:
  - keyword
  - scope_id
  - operator_intent

feeds_observation_families:
  - keyword_metric_observation
  - keyword_monthly_search_observation
  - keyword_serp_feature_signature
  - provider_intent_observation
  - keyword_authority_context_observation

raw_archive_required: true

not_strategy:
  - opportunity_score
  - keyword_priority
  - recommendation
  - report_claim
```

Doctrine line:

```text
Every provider pull must be recipe-driven, scope-labeled, cost-aware, rights-labeled, provenance-complete, raw-archived, hashable, and mappable to known observation families before it can become structured evidence.
```

---

## 16. CapturePackage v0.1 Direction

CapturePackage v0.1 should become the shared contract between:

- DataForSEO pulls
- browser extension/manual capture
- possible Firecrawl-like extraction
- API ingest
- MCP read tools
- hammers
- future Postgres schema

Candidate required fields:

- `capture_package_version`
- `capture_id`
- `recipe_id`
- `provider`
- `endpoint_family`
- `scope_id`
- `scope_class`
- `operator`
- `operator_intent`
- `requested_at`
- `captured_at`
- `request_config`
- `estimated_cost_usd`
- `actual_cost_usd`
- `rights_class`
- `retention_class`
- `raw_payload_pointer`
- `request_hash`
- `response_hash`
- `status`

The raw JSON says:

```text
Here is exactly what the provider returned.
```

The CapturePackage says:

```text
Here is what this capture means operationally.
```

---

## 17. Provider Drift Detection

DataForSEO endpoints can change over time.

Possible changes:

- new fields appear
- old fields disappear
- nested structures change
- null behavior changes
- endpoint names shift
- model lists change
- pricing/cost behavior changes
- SERP feature types expand
- AI Overview shape changes
- LLM response surfaces change
- fan-out query behavior changes
- rate limits / async behavior change

Therefore, the Capture Runner should eventually become a provider drift detector.

Doctrine:

```text
The Observatory does not assume provider endpoints are stable.
```

```text
Provider payloads are themselves observed over time.
The Capture Runner must preserve raw responses, fingerprint payload shape, compare against prior baselines, and flag drift before new structures are admitted into canonical observation families.
```

Provider drift detection should not automatically update the DB schema.

It should create a review signal:

```text
Provider drift found
  -> raw archive preserved
  -> inventory required
  -> mapping review
  -> human accepts / defers / kills
  -> schema/API/tool update only if justified
```

Possible drift report sections:

- recipe
- endpoint
- compared against
- new fields
- missing fields
- changed types
- new item types
- cost delta
- runtime delta
- mapping impact
- recommended action

Example drift status:

```text
New SERP item type observed: ai_overview_video_carousel
Status: raw archived; not yet mapped to canonical observation family
Action: inventory required before structured ingest
```

---

## 18. Chrome Extension / Manual Capture Direction

A browser extension is a possible capture instrument.

It should be operator-witnessed capture, not a crawler.

Allowed posture:

- user invokes capture on current page
- captures current URL
- captures visible text / selected structured fields
- captures title and platform
- may capture screenshot/hash if approved
- records timestamp
- records operator
- records operator intent
- records scope
- records rights/retention

Must not:

- autonomously browse
- mass-harvest pages
- evade rate limits
- bypass access controls
- scrape paid dashboards without approval
- capture logged-in private data without explicit consent and retention rules

Marketplace capture requires per-platform admission and ToS review.

Fiverr may be cleaner.
Etsy likely needs caution; Etsy API or manual evidence may be safer.
Firecrawl-like tools may be fallback for public/off-marketplace pages, not private marketplace/dashboard capture.

---

## 19. Planned Deep Research Topics

These are research lanes to prepare before schema or implementation hardens.

### A. DataForSEO provider adaptation research

Goal:
Adapt Veda-era DataForSEO work into Observatory.

Questions:

- Which old payload-confirmed surfaces should inform first Observatory provider families?
- Which surfaces are stale/provisional and need fresh pull validation?
- Which endpoint families are first-slice vs deferred?
- What request settings must be controlled by recipes?
- What cost gates are needed?
- What rights/provenance fields are mandatory?

Output:

- `05-dataforseo-provider-adaptation-plan.md`
- first controlled pull list
- recipe candidates
- deferred/provisional surfaces
- open questions for DataForSEO support/docs

### B. CapturePackage v0.1 contract research

Questions:

- What fields must every capture package include?
- How do provider captures, browser captures, manual captures, screenshots, and future extraction tools share one contract?
- How are raw payloads hashed?
- How are blobs/pointers represented?
- How are scope, rights, retention, cost, and operator intent represented?
- What are valid/invalid examples?

Output:

- CapturePackage v0.1 JSON schema draft
- examples
- invalid examples
- hammer tests
- glossary

### C. LLM-first API/MCP tool design research

Questions:

- What are best practices for MCP tool schema design for LLMs?
- How should structured outputs be shaped?
- How should tools report uncertainty, freshness, evidence IDs, and missing data?
- How should MCP tools avoid direct database access?
- What should be API vs MCP?

Output:

- tool naming rules
- input schema rules
- structured output patterns
- evidence-pack examples
- answerability envelope examples
- human-in-the-loop rules
- security rules
- anti-patterns

### D. SEO/GEO/SERP Strategy Layer research

Questions:

- What strategy workflows should consume Observatory evidence?
- How do SEO/GEO tools produce recommendations from evidence?
- How should LLM-generated recommendations be reviewed?
- What belongs in SearchClarity vs Neon Ronin vs Kaizen?
- How do AI citation/GEO workflows differ from traditional SEO?

Output:

- strategy workflow families
- recommendation object shape
- evidence citation requirements
- review queue needs
- SearchClarity variables
- website project variables
- Neon Ronin orchestration hooks
- Kaizen promotion hooks

### E. Browser extension/manual capture research

Questions:

- Can a user-invoked browser extension capture visible page data safely?
- How should it use Chrome permissions?
- What are Chrome Web Store policy concerns?
- What are Fiverr/Etsy marketplace ToS risks?
- What data should be captured vs avoided?
- How do we avoid it becoming a crawler?

Output:

- permission model
- allowed capture style
- forbidden capture style
- per-marketplace risk table
- CapturePackage fields
- screenshot/html/text/hash handling
- operator-witnessed capture rules

### F. GEO / AI citation measurement research

Questions:

- How do current tools measure AI Overview, LLM mentions, and citation presence?
- What dimensions matter: prompt, model, location, personalization, time, source URL?
- How volatile are AI answers?
- How should we avoid overclaiming?
- What can DataForSEO measure versus what remains manual?

Output:

- AI-surface observation families
- dimensions
- volatility labels
- citation evidence shape
- query panel design
- report caveat language
- DataForSEO mapping
- manual capture fallback

### G. Provider drift / payload fingerprinting research

Questions:

- How should JSON payload shape be fingerprinted?
- How should endpoint changes be detected across captures?
- What counts as breaking vs non-breaking drift?
- How are new fields held raw-only until reviewed?
- How are drift reports generated?

Output:

- payload shape fingerprint model
- drift report template
- breaking/non-breaking classification
- sample comparison flow
- hammer tests

---

## 20. Roadmap Candidates

No full roadmap is being created yet.

When ready, roadmap should likely include milestones around:

1. Current doctrine and boundaries
2. LLM-first API/MCP access plan
3. Strategy Layer / IMI boundary
4. CapturePackage v0.1
5. DataForSEO provider adaptation plan
6. Capture recipes v0.1
7. DataForSEO Capture Runner v0.1
8. Raw archive / metadata / hash format
9. Provider drift detection v0.1
10. Fresh DataForSEO provider validation milestone
11. Inventory note format
12. First schema family design pass
13. API contract v0.1
14. MCP tool contract v0.1
15. Hammer matrix
16. Tiny Postgres proof
17. Read-tool evidence packs
18. Strategy Layer proof workflow
19. SearchClarity pilot workflow
20. Neon Ronin integration planning
21. Kaizen promotion/governance integration planning

Important:

The $50 DataForSEO credit should not be spent until the roadmap reaches a provider-validation milestone with recipes, cost gates, capture package format, and raw archive rules.

---

## 21. Claude Review Queue

Items to give Claude when available:

1. Review current Observatory docs:
   - `00-project-overview.md`
   - `01-harvest-register.md`
   - this working note

2. Review LLM-first API/MCP direction:
   - LLM never gets direct DB access
   - MCP calls API
   - API owns DB access
   - evidence packs over raw rows

3. Review Strategy Layer / IMI boundary:
   - Strategy Layer outside Observatory
   - consumers: SearchClarity, Neon Ronin, Kaizen
   - accepted outputs promoted to consumer systems

4. Review DataForSEO inheritance:
   - old Veda samples are inheritance evidence, not fresh Observatory truth
   - fresh pulls should happen later through capture runner/API
   - payload-confirmed vs docs-confirmed confidence layer

5. Review Capture Runner concept:
   - recipe-driven pulls
   - raw archive
   - metadata
   - hashes
   - cost gates
   - CapturePackage v0.1
   - no direct DB ingest in v0.1

6. Review provider drift idea:
   - payload shape fingerprinting
   - drift reports
   - new structures held raw-only until reviewed

7. Suggest first roadmap skeleton, but do not implement.

---

## 22. Not Yet / Do Not Build Yet

Do not build yet:

- Postgres schema
- DataForSEO paid pulls
- DataForSEO capture runner
- Chrome extension
- Firecrawl integration
- MCP tools
- API server
- strategy database
- Neon Ronin integration
- SearchClarity production workflow
- Kaizen M19 reopening
- customer data ingestion
- autonomous provider capture
- autonomous spend
- direct DB access for LLM
- auto-schema updates from provider drift

Current phase is still planning and boundary hardening.

---

## 23. Current Best Summary

The Observatory should be built slowly and cleanly.

The old Veda work gives useful scar tissue, especially around DataForSEO surfaces, provider capture, schema risk, and evidence-only doctrine.

The new Observatory should not blindly inherit old data, but should inherit the lessons.

The core emerging system:

```text
Capture Providers / Instruments
  DataForSEO, browser extension, manual capture, future admitted tools
        ↓
Capture Runner / CapturePackage v0.1
  recipe-driven, scoped, rights-labeled, cost-aware, raw-archived, hashed
        ↓
Observatory API
  validation, authorization, provenance, scope isolation, read shaping
        ↓
Observatory DB
  evidence-only historical SEO/GEO/SERP/visibility observations
        ↓
LLM-first MCP/API evidence tools
  evidence packs, comparisons, freshness, blind spots, citations
        ↓
Strategy / IMI Layer
  interpretation, findings, opportunity candidates, recommendation drafts
        ↓
Consumers
  SearchClarity reports/services
  Neon Ronin multi-project agent orchestration
  Kaizen governance/decisions/improvement records
```

Final working doctrine:

```text
The telescope watches the sky.
But it also watches whether the telescope lens changed.
```

---

## 24. Repo-First Research Triage

A first repo-grounded research triage has been created at:

```text
C:\dev\observatory\planning-inbox\repo-first-research-triage.md
```

Purpose:

```text
Identify which Observatory research questions are already partly answered by local repos before later deep research.
```

Main conclusion:

```text
Do not research Observatory topics from scratch.
Harvest local doctrine first, then research only the remaining gaps.
```

The triage covers:

- scope / rights / retention
- evidence ID / citation model
- query panels
- freshness / staleness / volatility
- report claim safety
- strategy recommendation object shape
- intervention timeline overlays
- raw archive / blob storage
- hammer matrix
- consumer contracts
- DataForSEO provider adaptation
- browser/manual capture
- provider drift / payload fingerprinting

This is not the final roadmap. It is an obvious-question reduction pass.
