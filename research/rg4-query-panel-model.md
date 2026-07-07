# RG4 — Query Panel Model

Status: research output
Authority: source-grounded research input; not doctrine by itself; not schema approval
Milestone: M6 — Research Gate Execution
Date: 2026-07-07

---

## Gate question

What query panel model should define longitudinal observation sets by scope, version, surface, locale, device, language, and intent?

---

## Sources checked

Local/current sources checked during RG4:

- `01-harvest-register.md`
- `02-boundaries.md`
- `research/m5-research-gate-plan.md`
- `planning-inbox/repo-first-research-triage.md`
- `research/rg1-dataforseo-rights-retention-cost.md`
- `research/rg2-scope-rights-retention-model.md`
- `research/rg3-evidence-id-citation-model.md`

No current external source was required for RG4 because this gate defines the internal query-panel contract model. Current GEO/AI measurement conventions may be needed later in RG6, and current marketplace/platform rules may be needed later in RG7.

---

## Current source-grounded findings

### F1 — Query panels are already planned as the longitudinal backbone

The harvest register names query panels as planned day-one capability:

```text
Query panels: named, versioned query sets observed consistently per scope — the longitudinal backbone.
```

Implication:

- Query panels are not strategy lists.
- Query panels are governed measurement programs.
- Versioning is mandatory because changing the query set changes what the time series means.

---

### F2 — Query panels must attach to scope and preserve customer boundaries

RG2 defines `scope`, `scope_class`, rights, and retention as the pre-contract wall against customer-data contamination.

Implication:

- Every query panel must belong to a `scope_id` and `scope_class`.
- A customer engagement panel cannot store customer records or private first-party analytics.
- A market-watch panel cannot become cross-customer leakage.
- Internal panels do not automatically admit first-party telemetry.

---

### F3 — Query panels must connect to evidence IDs and read tools

RG3 defines evidence IDs as the durable handles downstream claims cite.

Implication:

- Query panel runs produce observations and evidence handles.
- Evidence packs should be able to explain which panel/version produced them.
- Reports should cite evidence, not the panel as a conclusion.

---

### F4 — Provider selection is separate from query panel definition

RG1 says DataForSEO remains plausible but not admitted, and no paid pull is authorized.

Implication:

- Query panels can be designed before provider admission.
- Provider-specific endpoint recipes remain later M13 work.
- A panel may name candidate source families, but it must not authorize provider spend.

---

### F5 — Query panels need no-nonsense checks

The repo-first triage warns that query choice strongly affects SERP features, AI Overview presence, Labs metrics, and ranked keyword visibility.

Implication:

- A panel must state what it is intended to observe.
- A panel must avoid measuring nonsense with fake confidence.
- Panels must include caveats about blind spots, sample size, volatility, surface coverage, and intent mismatch.

---

## Proposed query panel concept

A query panel is a named, versioned measurement set that defines what will be observed consistently for a scope.

A query panel is not:

- keyword strategy;
- recommendation storage;
- a content plan;
- an accepted action plan;
- a provider pull authorization;
- a recurring scheduler approval;
- a customer record.

Correct pattern:

```text
scope -> query_panel -> query_panel_version -> panel_items -> capture/run later -> observations -> evidence IDs
```

Forbidden pattern:

```text
query_panel -> recommendations / opportunity scores / accepted strategy
```

---

## Proposed query panel fields

This section proposes M7 contract inputs. It is not schema approval.

### Panel identity

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
- `scope_id` links to the RG2 scope model.
- `panel_purpose` must describe observation intent, not strategy recommendation.
- `notes` must not store customer private data.

---

### Panel version

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

Recommended statuses:

```text
draft
active
superseded
retired
blocked
```

Rules:

- A panel version is immutable once used for observations.
- Adding/removing/changing query items creates a new version.
- Device/location/language/surface changes create a new version unless the change is explicitly modeled as a run parameter.
- Historical observations remain tied to the version that produced them.

---

### Panel item

```text
query_panel_item_id
query_panel_version_id
item_kind
query_text
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
status
```

Candidate `item_kind` values:

```text
search_query
brand_query
category_query
competitor_query
marketplace_search
ai_prompt_probe
page_url_snapshot_target
listing_url_snapshot_target
```

Candidate `surface_family` values:

```text
google_serp
bing_serp
marketplace_search
ai_answer_surface
public_page_snapshot
public_listing_snapshot
provider_labs_metric
```

Rules:

- `query_text` is not a recommendation.
- `include_reason` must explain why the item belongs in the measurement set.
- `intent_label` is descriptive, not strategic truth.
- If a query item requires a provider/capture method that is not admitted, it remains planned/deferred, not executable.

---

## Required dimensions

A query panel should explicitly define or defer these dimensions:

| Dimension | Purpose | Notes |
|---|---|---|
| `scope_id` | binds panel to scope | Required |
| `scope_class` | applies boundary posture | Required |
| `surface_family` | what surface is observed | Required |
| `query_text` / target | what is measured | Required for query-like panels |
| `locale` | market/region context | Required when provider supports it |
| `language` | language context | Required when relevant |
| `device` | desktop/mobile/etc. | Required for SERP where device affects results |
| `location` | geo target | Required for local/SERP panels when relevant |
| `intent_label` | informational/commercial/local/etc. | Descriptive only |
| `frequency_expectation` | later capture cadence candidate | Planning only, not scheduler approval |
| `source_family` | candidate provider/capture source | Does not admit provider |
| `rights_class` | inherited/planned from RG2/source | Must fail closed |
| `retention_class` | inherited/planned from RG2/source | Must fail closed |

---

## Panel run concept

A future panel run records that a panel version was observed at a time through an admitted provider/capture method.

Candidate run fields:

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

Rules:

- A run is not a scheduler.
- A run does not imply recurring capture approval.
- A failed run may produce cost/provenance records but may produce no observations.
- Duplicate-run prevention is mandatory before paid providers are admitted.

---

## Examples by scope_class

### Example 1 — `internal` owned-site SERP visibility panel

Purpose:
Observe owner-controlled site visibility for a small set of core queries.

```text
scope_class: internal
surface_family: google_serp
queries:
  - search clarity etsy seo audit
  - etsy listing visibility audit
  - marketplace seo audit
locale: US
device: desktop/mobile split if needed
language: en
```

Allowed posture:
Planning only until provider/capture admission.

Forbidden:
Turning query results into stored keyword recommendations.

---

### Example 2 — `customer_engagement` public listing panel

Purpose:
Observe public search/marketplace visibility around a customer engagement without storing customer records.

```text
scope_class: customer_engagement
surface_family: marketplace_search
queries:
  - handmade soy candle
  - lavender soy candle gift
  - personalized candle gift
```

Allowed posture:
Public observations only, if platform/capture rules allow.

Forbidden:
Storing seller dashboard metrics, customer identity, order records, private conversion data, or report workflow state.

---

### Example 3 — `market_watch` niche panel

Purpose:
Watch a public niche before any customer or project exists.

```text
scope_class: market_watch
surface_family: google_serp / ai_answer_surface
queries:
  - best laundry detergent for construction workers
  - masculine laundry detergent
  - heavy duty laundry odor remover
```

Allowed posture:
Market evidence planning only.

Forbidden:
Cross-scope aggregate analysis that leaks customer engagement data, or strategy/recommendation storage.

---

### Example 4 — AI answer-surface panel

Purpose:
Observe whether entities, pages, or brands appear in AI answer surfaces for a controlled prompt set.

```text
scope_class: internal or market_watch
surface_family: ai_answer_surface
item_kind: ai_prompt_probe
queries/prompts:
  - what are the best Etsy SEO audit services?
  - how do I improve Etsy listing visibility?
```

Allowed posture:
Planning only until RG6 methodology and provider/capture rules clear.

Forbidden:
Claiming universal AI visibility from a tiny volatile sample.

---

## Versioning rules

Create a new panel version when:

- query text changes;
- items are added or removed;
- target surface changes;
- locale/location changes;
- device split changes;
- provider/capture method materially changes;
- intent grouping changes;
- the panel's purpose changes;
- rights/retention posture changes materially.

Do not create a new panel version merely because:

- a new run occurs under the same version;
- results change;
- evidence is stale;
- a downstream consumer interprets the observations differently.

Historical observations must always resolve back to the exact panel version that produced them.

---

## No-nonsense checks

Before a panel is eligible for execution later, it should answer:

1. What exact thing is this panel trying to observe?
2. Which scope owns it?
3. Which scope_class boundary applies?
4. Which surface_family is measured?
5. Why are these queries/items included?
6. What is intentionally excluded?
7. What provider/capture method would be required later?
8. Are rights and retention clear?
9. Could this panel accidentally measure private/customer data?
10. Does the panel sample support the claim someone wants to make?
11. What blind spots must read tools disclose?
12. What makes a new version necessary?
13. What stop condition prevents cost or capture sprawl?

If these cannot be answered, the panel remains draft/blocked.

---

## Relationship to evidence and read tools

Read tools should be able to report:

```text
panel_id
panel_version_id
panel_run_id
query/item context
observation_ids
evidence_ids
captured_at
freshness_status
surface_family
coverage gaps
blind spots
caveats
```

Read tools should not return:

```text
strategy recommendation
keyword priority as truth
content plan
accepted conclusion
customer private overlay data
```

---

## Relationship to provider cost control

Panels are one of the main tools for cost discipline.

A future provider-admission/capture plan should use panels to define:

- exact query count;
- exact surface family;
- exact endpoint family;
- exact locale/device/language dimensions;
- maximum run count;
- duplicate prevention;
- stop conditions;
- expected maximum spend.

RG4 does not authorize spend.

---

## Candidate statuses

### Query panel statuses

```text
draft
ready_for_review
active
blocked
retired
```

### Query panel version statuses

```text
draft
active
superseded
retired
blocked
```

### Panel item statuses

```text
included
excluded
candidate
blocked
retired
```

### Panel run statuses

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
`approved` run status should not exist until a later provider/capture governance contract defines what approval means.

---

## Non-goals

RG4 does not authorize:

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
- cross-scope aggregate exceptions.

---

## Owner-ruling candidates

Owner ruling or later contract decision is required before:

- allowing market_watch panels to execute before provider validation spend is approved;
- permitting any recurring panel schedule;
- admitting AI answer-surface probe panels for execution;
- admitting marketplace panels for Etsy/Fiverr/other platforms;
- allowing cross-scope aggregate reads over multiple panels;
- treating any panel-derived output as report-safe evidence.

---

## Blockers carried forward

- M7 must turn query panels into a contract before schema planning.
- M8 must hammer panel version immutability, scope isolation, rights fail-closed, duplicate-run prevention, and no strategy/recommendation storage.
- RG6 must refine AI answer-surface panel methodology.
- RG7 must refine marketplace panel ceilings and platform-specific restrictions.
- M13 must define provider-specific endpoint recipes before any paid run.

---

## Feeds later milestones

- M7 query panel contract
- M8 panel/version/cost hammers
- M9 first evidence slice selection
- M10 schema planning
- M13 provider admission and controlled pull plan
- M14 typed read API / MCP contract
- M15 SearchClarity proof workflow

---

## Final RG4 rule

```text
A query panel is a measurement program.
It defines what to observe consistently.
It does not define what to do about what was observed.
```
