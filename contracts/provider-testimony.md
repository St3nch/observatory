# Contract - Provider Testimony

Status: accepted — contract set v0.1 by `decisions/2026-07-12-m14-contract-and-read-boundary-rulings.md`
Authority: contract (binds only when accepted; subordinate to `02-boundaries.md`)
Version: 0.1
Date: 2026-07-10
Milestone: M7 - Core Contract Planning
Source research: `research/rg1-dataforseo-rights-retention-cost.md`, `research/rg9-provider-cross-check-disagreement-model.md`; supported by `research/rg5-freshness-staleness-volatility.md`, `research/rg8-claim-safety-report-language.md`, `research/rg10-capturepackage-v0-1-inputs.md`, `research/rg11-raw-archive-provider-drift.md`, existing M7 contracts, and root boundary law
Supersedes / superseded by: none

---

## Purpose

This contract defines how Observatory treats provider-supplied data, metrics, scores, rankings, payload fields, estimates, and API outputs as provider-attributed testimony.

It exists before schema, provider admission, paid pulls, API/MCP implementation, or customer-facing reports so provider output does not become hidden truth, strategy, recommendation, or an unreviewed raw data lake.

This is a skeleton-level M7 contract. Provider-specific bindings remain M13 work. It does not admit DataForSEO, Ahrefs, Semrush, GSC, Bing Webmaster Tools, YouTube APIs, marketplace tools, AI/GEO tools, browser backends, or any other provider.

---

## Governing boundaries

This contract operationalizes these Observatory rules:

- Observatory stores observations, not conclusions.
- Provider data is observed testimony, not truth.
- Provider scores, estimates, and proprietary metrics remain provider model output.
- Provider disagreement must be preserved and not averaged into fake truth.
- Rights and retention fail closed.
- Provider admission is separate from provider testimony modeling.
- Provider cost, credentials, endpoint recipes, raw retention, and stop conditions require later gates.
- Customer records and customer first-party data stay outside Observatory storage.
- LLMs and agents receive shaped evidence packs and caveats, not direct provider credentials or raw mystery data.

On conflict, `02-boundaries.md` and accepted higher-order contracts win.

---

## Definitions

### Provider

An external or first-party source system, API, tool, platform, report source, browser/capture instrument, or service that reports data about a surface, metric, page, listing, query, prompt, keyword, entity, domain, URL, video, local result, marketplace item, AI answer surface, or other observed target.

Provider examples may include DataForSEO, Ahrefs, Semrush, Google Search Console, Bing Webmaster Tools, YouTube APIs, marketplace SEO tools, public page snapshot tools, browser capture instruments, and AI/GEO visibility tools.

Named examples are not admitted providers.

### Provider testimony

A provider-attributed statement or output observed from a provider under known capture context.

Examples:

```text
DataForSEO reported position 8 for this sampled Google SERP query.
Provider X reported keyword volume 1200 for this keyword/locale/date.
Provider Y returned an AI citation observation for this prompt/run.
Provider Z returned an error payload for this endpoint/task.
```

Provider testimony is not truth about the web.

### Provider observation

A structured observation extracted from provider testimony after scope, rights, retention, provenance, CapturePackage, raw support, and parser safety checks pass.

### Provider metric

A provider-reported score, estimate, ranking, difficulty, authority-like score, volume, confidence, visibility score, citation count, mention count, index count, or proprietary value.

Provider metrics remain provider-attributed and must not be stored or exposed as objective facts.

### Provider model output

Any provider-derived value generated from the provider's own model, index, crawler, sampling method, data pipeline, scoring algorithm, or proprietary methodology.

### Provider admission

A later decision and contract binding that permits a provider, endpoint family, source family, cost posture, raw retention posture, and capture recipe to be used.

This contract does not admit providers.

### Provider endpoint / surface recipe

A provider-specific recipe, defined later, that states exact endpoint or surface, request parameters, task/call ceiling, spend ceiling, duplicate prevention, stop conditions, raw support handling, retention, rights, and expected payload behavior.

### Provider attribution

The requirement that provider name, provider family, endpoint/surface, metric name, capture time, provider-reported time if available, and caveats remain attached to provider testimony.

### Testimony status

A contract status describing whether a provider output is usable as provider-attributed evidence.

Candidate statuses:

```text
candidate
captured_pending_validation
validated_provider_testimony
blocked_by_rights
blocked_by_retention
blocked_by_source_admission
blocked_by_cost_or_approval
blocked_by_payload_drift
blocked_by_parser_validation
blocked_customer_private_data
invalid_provider_error
withdrawn
```

---

## Contract rules

### R1. Provider output is testimony, not truth

Every provider-reported value must remain provider-attributed.

Allowed:

```text
Provider X reported keyword difficulty 72 for this keyword on this date.
```

Forbidden:

```text
The keyword difficulty is 72.
```

### R2. Naming a provider does not admit the provider

A provider may be discussed, researched, modeled, or listed as a candidate without being admitted for capture, spend, storage, or use.

Candidate providers must default to blocked for execution until later provider-admission work clears them.

### R3. Provider-specific bindings are deferred to M13

This contract defines generic testimony behavior only.

The following remain M13 or later work:

```text
provider account funding
provider credential handling
endpoint family admission
request recipe
raw payload retention
cost ceiling
task/call ceiling
duplicate prevention
stop conditions
provider-specific rights binding
provider-specific parser expectations
provider-specific display/report rules
```

### R4. Provider attribution must travel with evidence

A provider observation must preserve:

```text
provider_name
provider_family
endpoint_or_surface
provider_metric_name when applicable
provider_metric_definition if known
captured_at
provider_reported_time if available
capture_package_id
rights_class
retention_class
freshness_status
volatility_class
raw_support_status
```

If any required attribution is missing, provider testimony cannot support strong claims.

### R5. Provider metrics must not be normalized into fake truth

Provider metrics must not be silently converted into generic cross-provider values.

Forbidden examples:

```text
true_keyword_difficulty
true_domain_authority
average_authority
blended_rank
visibility_truth_score
provider_confidence_truth
```

### R6. Provider disagreement must be preserved

When provider observations disagree, Observatory must preserve disagreement rather than selecting a winner or averaging values into a single truth.

Allowed:

```text
Provider A reported X; Provider B reported Y; the values differ and may reflect methodology, freshness, coverage, endpoint, or surface differences.
```

Forbidden:

```text
Provider A is correct.
The average of both is the truth.
Provider B is the winner.
```

### R7. Same-looking metric names are not enough

Two providers using similar metric labels does not make their values directly comparable.

Provider comparison requires aligned subject, query/prompt/panel, surface, locale, device, language, capture window, provider-reported time, and metric definition, or must be marked as caveated/incomparable.

### R8. Provider output must pass source, rights, retention, and CapturePackage gates

Provider testimony may become candidate evidence only after it passes:

```text
scope-rights-retention contract
CapturePackage validation
raw archive / provider drift contract where raw support applies
freshness/staleness contract
claim-safety contract
provider-specific admission when required
```

### R9. Provider error payloads are not normal observations

Provider errors, throttles, invalid requests, timeout responses, malformed payloads, or empty/error shapes must not be parsed as successful observations.

They may be audit/cost/provenance evidence where allowed.

### R10. Provider timestamps must remain distinct

Provider-reported dates, crawl dates, index dates, task dates, or data-period dates must remain distinct from Observatory `captured_at`.

If provider data is old at time of capture, read output must disclose provider-side age.

### R11. Provider cost controls are mandatory before paid use

Any paid provider capture requires later approval with:

```text
approval_reference
endpoint_or_surface recipe
cost_ceiling
call_or_task_ceiling
duplicate-task prevention
stop_conditions
actual_cost tracking where available
post-pull review before expansion
```

This contract does not authorize spend.

### R12. Repeated paid tasks must be rejected or blocked before execution

Duplicate provider task risk is a first-class hostile path. A future capture runner must not submit repeated identical paid tasks without explicit allowed reason and stop controls.

### R13. Raw provider payloads require rights-cleared retention

Provider raw payloads may be retained only when raw retention is allowed by the source, provider-specific contract, rights class, retention class, CapturePackage, and raw archive contract.

Unknown raw retention fails closed.

### R14. Provider output cannot launder customer private data

Provider testimony must not be used to import customer first-party data, customer account exports, seller dashboards, private analytics, customer records, or customer workflow state into Observatory.

Customer first-party provider outputs remain overlay-only unless future law changes.

### R15. Provider testimony is not report-safe by default

Provider-attributed evidence may support later reports only after evidence ID/citation and consumer/report contracts allow it.

Provider job IDs, raw payload IDs, raw pointers, and provider account details are not customer-facing citations.

### R16. Provider summaries are read-time unless materialization is explicitly accepted

Provider summaries, disagreement explanations, visibility summaries, AI/GEO summaries, and provider coverage summaries should be computed at read time by default.

Persisting derived provider summaries requires the V6 materialization test plus explicit owner ruling.

### R17. Provider testimony must not become recommendation storage

Provider evidence must not store recommendations, strategy, action items, opportunity scores, provider selection advice, customer deliverables, or agent tasks.

### R18. Provider withdrawal, correction, or drift must not silently rewrite history

If provider output is later corrected, invalidated, withdrawn, or affected by parser/provider drift, old evidence must remain status-aware rather than silently mutated into a new truth.

### R19. Provider admission can be narrow

A provider may be admitted for one endpoint family, source family, use case, cost ceiling, or retention posture without being admitted broadly.

No contract or code may treat provider admission as global unless an explicit owner decision says so.

### R20. Provider-specific laws override generic testimony rules

If provider-specific terms, platform limits, endpoint constraints, or rights/retention restrictions are stricter than this generic contract, the stricter provider/source rule wins.

---

## Required fields / shapes

These are contract-level requirements, not schema.

### Provider testimony shape

```text
provider_testimony_id
provider_name
provider_family
provider_admission_status
endpoint_or_surface
request_context_reference
capture_package_id
capture_id
provider_job_id if available
raw_payload_id if allowed
provider_metric_name if applicable
provider_metric_value if applicable
provider_metric_unit if applicable
provider_metric_definition if known
provider_reported_time if available
captured_at
scope_id
scope_class
query_panel_id if applicable
query_panel_version_id if applicable
panel_run_id if applicable
rights_class
retention_class
freshness_status
volatility_class
raw_support_status
testimony_status
claim_use_warning
```

### Provider admission statuses

```text
not_yet_reviewed
candidate
blocked
owner_ruling_required
provider_clarification_required
legal_review_required
admitted_limited
admitted
suspended
withdrawn
```

Default:

```text
not_yet_reviewed or candidate -> blocked for execution
```

### Provider testimony statuses

```text
candidate
captured_pending_validation
validated_provider_testimony
blocked_by_rights
blocked_by_retention
blocked_by_source_admission
blocked_by_cost_or_approval
blocked_by_payload_drift
blocked_by_parser_validation
blocked_customer_private_data
invalid_provider_error
withdrawn
```

### Provider metric posture values

```text
provider_reported_value
provider_estimate
provider_model_output
provider_sampled_observation
provider_error_or_status
unknown_definition
not_comparable
```

### Provider-use warning values

```text
provider_attribution_required
provider_metric_definition_unknown
provider_freshness_unknown
provider_recap_needed_for_current_claim
provider_disagreement_present
provider_comparison_incomparable
provider_rights_or_retention_blocked
provider_not_admitted
provider_output_not_report_safe
```

---

## Fail-closed behavior

### Missing provider identity

If provider name/family/source cannot be identified, provider testimony is blocked.

### Missing admission status

If provider admission status is unknown, it defaults to `not_yet_reviewed` and cannot execute.

### Missing endpoint or surface

If endpoint/surface is unknown, testimony cannot support provider-specific interpretation or comparison.

### Missing metric definition

If a provider metric definition is unknown, the value may be preserved as provider-reported testimony only with a definition warning. It must not be compared as equivalent to other providers' metrics.

### Missing rights or retention

Missing or invalid rights/retention blocks storage/use under the scope-rights-retention contract.

### Missing freshness context

Missing `captured_at` blocks current-state claims. Missing provider-reported time triggers provider freshness caveats where relevant.

### Provider not admitted

Provider testimony from an unadmitted provider may exist only as research/planning or imported historical doc context where rights allow. It cannot trigger live capture, spend, raw archive, report-safe output, or implementation.

### Provider error payload

Provider error/throttle/malformed payloads must not produce normal observations or evidence IDs.

### Provider disagreement without context

If observations differ but comparison context is incomplete, mark as `unresolved_incomparability` or equivalent. Do not choose a winner.

---

## Forbidden patterns

This contract forbids:

```text
provider output as truth
provider score as web fact
provider job ID as evidence ID
provider payload as strategy cache
provider account as provider admission
provider terms later; capture now
provider blob now; rights later
provider metric averaged into truth
provider winner logic
provider confidence as Observatory confidence
provider disagreement hidden from read output
provider task repeated without duplicate controls
provider error payload parsed as normal observation
provider output used to store customer private analytics
provider report-safe citation without M15 approval
provider recommendation stored in Observatory
```

Fake-mustache variants are also forbidden:

```text
truth_provider
best_provider_score
average_provider_truth
authority_truth_score
provider_consensus_rank
provider_confidence_rank
provider_strategy_summary
recommended_provider_action
```

---

## Examples

### Valid planning example - DataForSEO remains candidate

```text
provider_name: DataForSEO
provider_admission_status: candidate
endpoint_or_surface: SERP API candidate
provider_metric_name: organic result position
capture_status: not_approved
rights_class: provider_clarification_required
retention_class: retain_until_review
```

Why valid:

- It is planning-only.
- Provider is not admitted.
- Rights/retention remain cautious.
- It does not authorize a paid pull.

### Invalid example - provider candidate treated as admitted

```text
provider_name: DataForSEO
provider_admission_status: candidate
capture_status: approved_for_capture
cost_ceiling: missing
call_or_task_ceiling: missing
```

Why invalid:

- Candidate is not admission.
- No owner approval or cost/task ceiling exists.
- Paid use remains blocked.

### Valid provider metric language

```text
Provider X reported keyword volume 1200 for keyword K in locale L on date D. Treat this as provider-reported estimate, not exact demand truth.
```

Why valid:

- Provider attribution remains attached.
- Metric is caveated.
- It avoids exact truth language.

### Invalid provider metric language

```text
Keyword K has 1200 searches.
```

Why invalid:

- Drops provider attribution.
- Converts estimate into truth.

### Valid disagreement language

```text
Provider A reported difficulty 42 while Provider B reported difficulty 71. The values are provider model outputs and may not share definitions.
```

Why valid:

- Disagreement is preserved.
- No winner is crowned.
- Metric definitions are caveated.

### Invalid disagreement language

```text
The true difficulty is 56.5 because it averages Provider A and Provider B.
```

Why invalid:

- Averages proprietary metrics into fake truth.

### Invalid customer-private provider import

```text
provider_name: Google Search Console
source_family: customer_gsc_export
retention_class: retain_project_evidence
raw_payload_pointer: customer-query-export.csv
```

Why invalid:

- Customer first-party analytics are not stored in Observatory under current boundary law.

---

## Owner-ruling candidates

Open rulings and future decisions:

- Whether any provider can be admitted before M13. Default: no.
- Whether DataForSEO validation budget may be funded and used. Default: no until owner approval and M13-style plan.
- Whether any provider raw payload may be retained durably. Default: no unless rights/retention and raw archive contract allow.
- Whether provider disagreement can appear in customer-facing reports. Default: M15 decides.
- Whether provider comparison summaries may be persisted. Default: no; read-time unless V6 materialization test plus owner ruling.
- Whether first-party provider sources like GSC/Bing Webmaster can be overlaid in read tools. Default: overlay only, future contract required.
- Whether provider-specific metric definitions must be stored or referenced before comparison. Default: required for strong comparisons.

Until ruled, affected behavior fails closed.

---

## Deeper-research blockers

This contract remains blocked from provider-specific activation by:

- DR1 - DataForSEO endpoint-by-endpoint admission research.
- DR2 - Raw payload retention and allowed-use interpretation.
- DR3 - DataForSEO / Ahrefs / Semrush comparison methodology.
- DR4 - GEO / AI citation measurement methodology.
- DR5 - Google AI Overview / AI Mode capture and visibility limits.
- DR6 - Marketplace platform evidence limits: Etsy.
- DR7 - Marketplace platform evidence limits: Fiverr.
- DR10 - Customer first-party overlay contract.
- DR13 - Raw archive layout and provider drift fingerprints.
- DR16 - Consumer authentication / authorization model.
- DR17 - Provider credential and secret handling posture.

M13 must bind provider-specific endpoint recipes before live provider use.

---

## Hammer expectations

M8+ must prove at least these hostile paths:

```text
provider candidate used as admitted provider -> reject
paid provider capture without approval/cost ceiling/task ceiling -> reject
duplicate provider task without duplicate prevention -> reject
provider metric returned without provider attribution -> reject
provider score stored as truth -> reject
provider disagreement averaged into truth -> reject
provider winner selected without admitted adjudication -> reject
same-looking metrics compared without definition warning -> caveat or reject
provider error payload parsed as observation -> reject
provider job ID used as evidence ID -> reject
provider raw payload retained without rights -> reject
customer first-party provider export stored as evidence -> reject
provider stale data supports current claim without warning -> reject
provider output creates recommendation/action/strategy -> reject
```

Relevant hammer categories:

```text
H2 - rights fail-closed
H3 - retention fail-closed
H4 - customer-private rejection
H5 - no recommendation/strategy storage
H6 - CapturePackage validation
H7 - provider cost and duplicate-task controls
H8 - provider attribution and disagreement
H9 - freshness and volatility
H10 - AI/GEO overclaim rejection
H11 - marketplace restrictions
H12 - raw archive integrity and drift
H15 - evidence/citation integrity
H17 - LLM/agent access boundary
H18 - hostile/weird input handling
H19 - append-only/no silent overwrite
H20 - concurrency and duplicate attempts
H21 - audit-first enforcement
```

---

## Feeds milestones

This contract feeds:

- M8 - Hammer Matrix and Acceptance Gates.
- M10 - Schema Planning Only.
- M13 - Provider Admission and Controlled Pull Plan.
- M14 - Typed Read API / MCP Contract and Prototype.
- M15 - SearchClarity Proof Workflow.
- M16 - Provider Cross-Check Proof.
- M17 - Overlay/Internal Telemetry Proof.

---

## Non-authorizations

This contract does not authorize:

```text
provider admission
DataForSEO funding
paid provider pulls
API credentials
provider account setup
schema design
migrations
raw provider archive implementation
capture runner implementation
browser automation
marketplace capture
AI/GEO consumer UI scraping
API/MCP implementation
customer first-party storage
customer-facing report claims
strategy/recommendation storage
recurring capture
```

---

## Final rule

```text
A provider is a witness.
A provider is not the judge.
A provider metric is testimony.
A provider metric is not truth.
Disagreement is evidence.
Do not crown a winner, hide the caveats, or average testimony into fake certainty.
```

---

## Change log

```text
0.1 - 2026-07-10 - initial draft from RG1 and RG9 with supporting M7 contract inputs
```
