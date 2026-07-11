# Contract - Query Panel

Status: draft
Authority: contract (binds only when accepted; subordinate to `02-boundaries.md`)
Version: 0.1
Date: 2026-07-10
Milestone: M7 - Core Contract Planning
Source research: `research/rg4-query-panel-model.md`, supported by `research/rg2-scope-rights-retention-model.md`, `research/rg3-evidence-id-citation-model.md`, `research/rg5-freshness-staleness-volatility.md`, `research/rg6-geo-ai-citation-methodology.md`, `research/rg7-marketplace-evidence-ceiling.md`, `research/rg8-claim-safety-report-language.md`, `research/rg10-capturepackage-v0-1-inputs.md`, and root boundary law
Supersedes / superseded by: none

---

## Purpose

This contract defines query panels as named, versioned measurement programs that tell Observatory what to observe consistently for a scope.

A query panel exists to preserve repeatable observation context across SERP, marketplace, AI/GEO, public-page, listing, and provider-metric surfaces. It is not keyword strategy, a content plan, a report recommendation, a provider-pull approval, a scheduler, a customer record, or an accepted conclusion.

M7 needs this contract before schema or implementation because a future observation without panel/version context cannot support safe longitudinal comparison, absence claims, freshness warnings, provider disagreement, or report-safe evidence packs.

---

## Governing boundaries

This contract operationalizes these root rules:

- Observatory stores observations, not conclusions.
- Query panels define measurement context, not strategy.
- Customer records, orders, reports, private analytics, and workflow state stay outside Observatory.
- Customer first-party data is read-time overlay only unless a future owner ruling changes law.
- Provider selection, provider admission, provider spend, and capture execution are separate later gates.
- Rights and retention fail closed.
- Evidence IDs cite observations, not panel intent or downstream conclusions.
- Provider disagreement and absence must remain context-bound.
- LLMs and agents receive shaped evidence through future typed read tools, not direct SQL or raw credentials.

On conflict, `02-boundaries.md` and accepted higher-order contracts win.

---

## Definitions

### Query panel

A named measurement program bound to one Observatory scope and scope_class. It defines what should be observed consistently.

A query panel is not executable by itself.

### Query panel version

An immutable version of a panel's measurement definition. Once a version has produced observations, it must not be edited in a way that changes what was measured.

### Panel item

A query, prompt, URL, listing target, entity, marketplace search, page snapshot target, or other item included in a panel version.

### Panel run

A future execution record showing that a specific panel version was observed through an admitted provider or capture instrument at a time.

M7 does not authorize panel runs. This contract defines the concept so later milestones can avoid inventing it from vibes.

### Surface family

The surface or evidence family a panel item is intended to observe, such as `google_serp`, `bing_serp`, `marketplace_search`, `ai_answer_surface`, `public_page_snapshot`, `public_listing_snapshot`, or `provider_labs_metric`.

### Intent label

A descriptive label for what the item is meant to measure, such as informational, commercial, local, branded, category, competitor, marketplace, or AI/GEO visibility.

Intent labels are not strategy conclusions.

### Priority

An ordering or sampling hint inside a measurement program. It is not strategic importance as truth, keyword value, opportunity score, content priority, or customer recommendation.

### Coverage gap / blind spot

A disclosed limitation in what the panel observes. A blind spot may support future collection planning, but does not become a recommendation or automatic capture request.

---

## Contract rules

### R1. Panels are measurement programs only

A query panel defines what to observe. It must not store what to do about the observation.

Allowed:

```text
Panel P measures Google desktop US results for these ten query items.
```

Forbidden:

```text
Panel P says these are the best keywords to target.
```

### R2. Every panel must bind to a scope

Every query panel must carry:

```text
scope_id
scope_class
```

The scope and scope_class contract controls whether the panel is `internal`, `customer_engagement`, or `market_watch`.

A panel must not use consumer project IDs, customer names, order IDs, report IDs, private analytics IDs, or external workflow IDs as Observatory identity.

### R3. Panel purpose must describe observation intent

`panel_purpose` must describe what the panel is intended to observe, not a strategy or recommendation.

Allowed:

```text
Observe sampled Google SERP visibility for owner-owned service terms.
```

Forbidden:

```text
Find winning keywords and recommend title changes.
```

### R4. Provider/capture selection is separate from panel definition

A panel may name candidate source families or surface families, but it must not authorize:

- provider admission;
- provider spend;
- paid pulls;
- API credentials;
- browser automation;
- recurring capture;
- marketplace capture;
- customer private telemetry capture;
- raw archive retention.

Provider and capture execution belong to later milestones and must pass their own contracts.

### R5. Query panel versions are immutable after use

Once a panel version has produced observations, changing any measurement-defining element requires a new version.

Measurement-defining elements include:

- query text;
- prompt text;
- target URL/listing/entity;
- surface family;
- locale;
- language;
- device;
- location;
- item inclusion/exclusion;
- panel purpose;
- rights or retention posture where material;
- provider/capture method if materially part of the measurement definition.

### R6. Results changing do not create a new panel version

A new run, changed result set, stale evidence, provider disagreement, or downstream interpretation does not itself create a new panel version.

The panel version defines what was measured. Observations define what was seen.

### R7. Panel items must preserve observation context

Each panel item must specify or explicitly defer the dimensions required for its surface family.

A panel item that lacks required context is draft or blocked, not executable.

### R8. Panel item reasons must not store strategy

`include_reason` and `exclude_reason` may explain why an item belongs in the measurement set.

They must not store:

- recommendations;
- accepted strategy;
- content plans;
- customer decisions;
- opportunity scores;
- predicted ROI;
- sensitive customer notes.

### R9. Priority is not recommendation

If a panel item carries `priority`, the priority means only measurement ordering, sampling importance, or review convenience inside the panel.

It must not be represented as strategic priority, value, demand, rank importance, or recommended action.

### R10. Panel runs require later admission

A panel run may exist only after the relevant provider/capture path is admitted by later contracts and owner approvals.

M7 does not create run approval.

### R11. Panel runs do not imply recurrence

A panel run is a single future observation attempt against a panel version. It is not a scheduler, watch job, recurrence rule, or recurring capture approval.

Recurring watch panels are deferred to later roadmap work.

### R12. Failed or blocked runs must not invent observations

If a future run is blocked, failed, stopped, or rights/retention-invalid, it may produce audit/provenance/cost evidence where allowed, but it must not create valid observations or evidence IDs as if capture succeeded.

### R13. Query panels must preserve absence context

A not-observed result from a panel is only meaningful within the exact panel/version/run/item context.

Allowed:

```text
No citation was observed in this AI answer-surface panel run.
```

Forbidden:

```text
This brand is absent from AI search.
```

### R14. Query panels must expose blind spots

Panels must preserve enough context for future read tools to disclose what the panel does not cover.

Blind spots include, where applicable:

- unobserved surfaces;
- unobserved locales;
- unobserved devices;
- unobserved languages;
- unobserved query intent classes;
- panel sample-size limits;
- source/capture admission blocks;
- stale or missing runs;
- provider coverage limits.

### R15. Marketplace and AI panels are blocked unless their source family clears

Marketplace and AI/GEO panel definitions may be drafted, but they remain blocked for execution until the relevant methodology, rights, source, provider, or capture-instrument gates clear.

### R16. Customer engagement panels must be customer-clean

A `customer_engagement` panel may describe public evidence to be observed around an engagement, but it must not store customer identity, orders, reports, private analytics, seller dashboards, files, consent records, or delivery/workflow state.

### R17. Market-watch panels must not launder cross-scope aggregation

A `market_watch` panel may observe public niche/market surfaces before any customer or project exists. It must not combine customer engagement data, leak customer-derived signals, or create cross-scope aggregate analysis without future explicit owner ruling.

### R18. Internal panels do not automatically admit internal telemetry

An `internal` panel may observe owner-owned public surfaces or future internal telemetry only after the relevant source family is admitted. Owner-controlled does not mean automatically stored.

### R19. Panel evidence must cite observations, not the panel itself

Panels and panel versions provide context. Evidence IDs and citation handles cite observations produced from admitted captures/runs.

A panel ID is not a report-safe evidence reference by itself.

### R20. Query panels must fail closed

If panel scope, source family, rights, retention, required dimensions, capture method, or source admission is unclear, the panel or affected item remains draft/blocked and cannot support execution or current claims.

---

## Required fields / shapes

These are contract-level requirements, not schema approval.

### Query panel shape

```text
query_panel_id
scope_id
scope_class
panel_name
panel_purpose
owning_consumer
status
created_at
created_by
notes
```

Rules:

- `query_panel_id` is Observatory-owned.
- `scope_id` must resolve under the scope contract.
- `scope_class` must match scope posture.
- `owning_consumer` is an allowed consumer label, not a customer identity field.
- `notes` must not contain customer private data or strategy conclusions.

### Query panel statuses

```text
draft
ready_for_review
active
blocked
retired
```

Status rules:

- `draft` means not ready for execution.
- `ready_for_review` means the panel can be reviewed, not run.
- `active` means the panel version can be used where later execution gates allow.
- `blocked` means one or more required conditions fail closed.
- `retired` means no new runs should be created under the panel.

### Query panel version shape

```text
query_panel_version_id
query_panel_id
version_label
version_number
version_status
version_created_at
version_reason
supersedes_version_id
change_summary
```

### Query panel version statuses

```text
draft
active
superseded
retired
blocked
```

Status rules:

- `draft` versions cannot produce observations.
- `active` versions may be eligible for later approved runs.
- `superseded` versions remain resolvable for historical evidence.
- `retired` versions should not receive new runs.
- `blocked` versions cannot be executed until the blocker is resolved.

### Panel item shape

```text
query_panel_item_id
query_panel_version_id
item_kind
query_text
target_locator
entity_or_target
surface_family
locale
language
device
location
intent_label
priority
include_reason
exclude_reason
source_family_candidate
rights_class
retention_class
status
```

`target_locator` may be omitted when not applicable, but should be present for URL/listing/page/entity target panels where allowed.

### Candidate item_kind values

```text
search_query
brand_query
category_query
competitor_query
marketplace_search
ai_prompt_probe
page_url_snapshot_target
listing_url_snapshot_target
entity_visibility_probe
provider_metric_target
```

### Candidate surface_family values

```text
google_serp
bing_serp
marketplace_search
ai_answer_surface
public_page_snapshot
public_listing_snapshot
provider_labs_metric
youtube_search_or_video_surface
local_pack_or_maps_surface
```

Adding new surface families requires source/rights/retention review and may require owner ruling.

### Panel item statuses

```text
included
excluded
candidate
blocked
retired
```

Status rules:

- `included` means part of the measurement set.
- `excluded` means deliberately omitted and can support blind-spot disclosure.
- `candidate` means proposed but not included.
- `blocked` means source, rights, retention, methodology, or context is not cleared.
- `retired` means no longer used in current versions but preserved historically.

### Future panel run shape

```text
panel_run_id
query_panel_version_id
capture_id
provider_or_capture_instrument
run_started_at
run_finished_at
run_status
cost_estimate_or_actual
stop_condition_triggered
observations_created
evidence_ids_created
```

M7 does not authorize this shape for implementation. It is included to prevent later run concepts from bypassing panel/version/evidence rules.

### Future panel run statuses

```text
planned
approved
running
completed
failed
stopped
blocked
```

Caution:
`approved`, `running`, and `completed` require future provider/capture governance. M7 does not define the approval process.

---

## Required dimensions by panel family

### SERP panel item

Required or explicitly deferred:

```text
surface_family
query_text
locale
language
device
location if relevant
intent_label
rights_class
retention_class
```

### AI/GEO panel item

Required or explicitly deferred:

```text
surface_family
prompt_text or query_text
provider_or_surface_candidate
locale/language if applicable
account/session/personalization posture if known
prompt_version posture
sample-bound warning posture
rights_class
retention_class
```

AI/GEO execution remains blocked until methodology/source/capture admission clears.

### Marketplace panel item

Required or explicitly deferred:

```text
marketplace
surface_family
query_text or listing target
public/private surface classification
capture_method_candidate
locale/language/location if applicable
rights_class
retention_class
platform-specific blocker status
```

Marketplace execution remains blocked unless platform/capture rules clear.

### Public snapshot panel item

Required or explicitly deferred:

```text
surface_family
target_locator
capture_method_candidate
artifact retention posture
rights_class
retention_class
freshness posture
```

### Provider metric panel item

Required or explicitly deferred:

```text
provider_candidate
metric_family_candidate
target subject
locale/language if relevant
provider attribution requirement
rights_class
retention_class
provider admission blocker status
```

---

## Fail-closed behavior

### Unknown scope

If `scope_id` or `scope_class` is missing, invalid, or inconsistent, the panel is blocked.

### Unknown source family

If `surface_family` or source family is unknown, the item is blocked until classified.

### Unknown rights or retention

If rights or retention is unknown, the item is blocked for execution and cannot produce observations.

### Missing required dimensions

If required dimensions are missing and not explicitly deferred with reason, the panel item is blocked.

### Unadmitted provider or capture method

If a panel requires a provider, API, browser extension, manual capture method, or marketplace capture method that is not admitted, the item remains planned/blocked.

### Customer-private contamination

If panel text, item text, notes, reasons, or locators contain customer private records or first-party analytics, the panel is rejected or scrubbed and cannot proceed.

### Strategy contamination

If panel text stores recommendations, accepted conclusions, opportunity scores, content plans, or strategy, the panel is rejected or must be rewritten as measurement-only.

### Version ambiguity

If it is unclear which panel version produced an observation, the observation cannot support longitudinal comparison or report-safe evidence.

### Run approval ambiguity

If a future panel run lacks approval evidence, cost ceilings, source admission, or stop conditions where required, it cannot execute.

---

## Forbidden patterns

This contract forbids:

```text
query panel as keyword strategy
query panel as content plan
query panel as customer work order
query panel as report outline
query panel as recommendation store
query priority as opportunity score
query inclusion as proof of importance
panel run as implicit provider spend approval
panel as recurring scheduler
panel as marketplace scraping permission
panel as AI/GEO consumer UI scraping permission
panel as customer private analytics container
panel as cross-customer aggregate leakage path
panel evidence without version identity
absence claim without panel/run/context
```

Fake-mustache variants are also forbidden:

```text
measurement priority = strategic priority
include_reason = recommendation rationale
panel purpose = accepted business goal
planned run = approved pull
market_watch panel = hidden strategy engine
customer_engagement panel = customer database
AI prompt panel = stored AI visibility truth
```

---

## Examples

### Valid example - internal SERP measurement panel

```text
scope_class: internal
panel_purpose: Observe sampled Google SERP visibility for owner-owned service terms.
surface_family: google_serp
query_text: etsy listing visibility audit
locale: US
language: en
device: desktop
intent_label: commercial
status: draft
```

Why valid:

- It describes observation intent.
- It is scoped.
- It does not authorize provider execution.
- It does not store a recommendation.

### Invalid example - strategy disguised as panel

```text
panel_purpose: Find the best keywords to target for higher sales.
priority: high ROI
include_reason: This keyword should be used in the title.
```

Why invalid:

- It stores strategy and recommendation rationale.
- It treats measurement priority as business value.
- It belongs to SearchClarity/strategy/consumer work, not Observatory panel definition.

### Valid example - marketplace panel blocked for execution

```text
scope_class: customer_engagement
surface_family: marketplace_search
query_text: lavender soy candle gift
source_family_candidate: manual_public_observation
rights_class: provider_clarification_required
retention_class: retention_not_cleared
status: blocked
```

Why valid:

- It preserves the measurement idea.
- It fails closed because source/rights/retention are not cleared.
- It does not execute or store marketplace evidence.

### Invalid example - panel as scrape approval

```text
surface_family: marketplace_search
capture_method: browser_extension
status: active
notes: scrape Etsy weekly for these queries
```

Why invalid:

- Marketplace capture is not admitted.
- Recurring capture is not admitted.
- Etsy automation is blocked by source research unless future authorization/ruling changes posture.

### Valid example - AI/GEO prompt panel draft

```text
scope_class: market_watch
surface_family: ai_answer_surface
item_kind: ai_prompt_probe
query_text: what are the best Etsy SEO audit services?
status: draft
include_reason: Observe whether known service categories appear in sampled AI answer surfaces.
```

Why valid:

- It is measurement-only.
- It remains draft until methodology/source/capture gates clear.
- It does not claim AI visibility, trust, or authority.

---

## Owner-ruling candidates

This contract carries these open rulings forward. Until ruled, affected behavior fails closed.

### OR-A5 - NC3/NC5 disposition confirmation

NC5 coverage/blind-spot reporting is treated here as a required read-tool/panel-output concern. It does not authorize capture expansion or strategy storage.

### Market-watch execution before provider validation spend

Open ruling:
Can market_watch panels execute before provider validation spend is separately approved?

Default:
No. Panels may be drafted, not executed.

### Recurring panel schedule

Open ruling:
Can any panel run on a recurring schedule?

Default:
No. Recurring capture is deferred.

### AI answer-surface probe panel execution

Open ruling:
Can AI prompt panels execute, and through which admitted source/capture path?

Default:
Draft only until RG6 methodology and provider/capture rules clear.

### Marketplace panel execution

Open ruling:
Can Etsy, Fiverr, YouTube, Pinterest, Shopify, or other marketplace/video panels execute as Observatory evidence?

Default:
Draft/blocked unless source-specific rights and capture admission clear.

### Cross-scope aggregate panel reads

Open ruling:
Can read tools compare panel observations across scopes?

Default:
No cross-scope aggregate reads without explicit future owner ruling.

### Panel-derived report-safe output

Open ruling:
Can panel-derived outputs appear in customer-facing reports?

Default:
Only evidence IDs/citation handles can support reports after M15/report-safe contracts. Panel IDs alone are not report-safe proof.

---

## Deeper-research blockers

This contract depends on later deeper work for execution-specific behavior:

- DR4 - GEO / AI citation measurement methodology.
- DR5 - Google AI Overview / AI Mode capture and visibility limits.
- DR6 - Marketplace platform evidence limits: Etsy.
- DR7 - Marketplace platform evidence limits: Fiverr.
- DR8 - Manual capture and browser-extension capture admissibility.
- DR12 - Query panel sampling and recapture cadence.
- DR14 - Evidence ID, citation handle, and report-safe reference finalization.
- DR15 - Hammer matrix hostile-path expansion.
- DR16 - Consumer authentication / authorization model.
- DR17 - Provider credential and secret handling posture.

Execution remains blocked until the relevant downstream milestone activates and resolves the applicable blocker.

---

## Hammer expectations

M8+ hammers must prove this contract against hostile paths.

### Required hammer categories

- H1 - Scope isolation.
- H2 - Rights fail-closed.
- H3 - Retention fail-closed.
- H4 - Customer/private data rejection.
- H5 - No recommendation/strategy storage.
- H6 - CapturePackage validation for future runs.
- H7 - Cost/duplicate prevention for future paid runs.
- H9 - Freshness/volatility warnings.
- H10 - AI/GEO overclaim rejection.
- H11 - Marketplace restriction enforcement.
- H14 - Panel immutability.
- H15 - Evidence/citation integrity.
- H16 - Overlay no-storage where panel reads align overlays later.
- H17 - LLM/agent access boundary.
- H19 - Append-only/no silent overwrite for observations created from panel runs.
- H20 - Concurrency behavior for duplicate runs and version changes.
- H21 - Audit-record-required for consequential future panel/run changes.

### Specific hostile paths

M8 should test at least:

```text
Edit used panel version without creating new version -> reject.
Use panel priority as recommendation -> reject.
Run panel with unadmitted provider -> reject.
Run marketplace panel with blocked source posture -> reject.
Run AI prompt panel and claim universal AI absence -> reject.
Store customer private analytics in panel notes -> reject.
Create customer_engagement panel with customer order/report identity -> reject.
Use panel ID as report-safe evidence citation -> reject.
Create current claim from stale panel run without freshness warning -> reject.
Create recurring schedule from panel status alone -> reject.
Create cross-scope aggregate panel read without owner ruling -> reject.
Produce observations from failed/blocked run -> reject.
Duplicate paid panel run without duplicate/cost controls -> reject.
```

---

## Feeds milestones

This contract feeds:

- M8 - Hammer Matrix and Acceptance Gates.
- M9 - First Evidence Slice Definition.
- M10 - Schema Planning Only.
- M13 - Provider Admission and Controlled Pull Plan.
- M14 - Typed Read API / MCP Contract and Prototype.
- M15 - SearchClarity Proof Workflow.
- M18 - Recurring Watch Panel Planning.

---

## Change log

```text
0.1 - 2026-07-10 - initial draft from RG4 and supporting M6 contract inputs
```
