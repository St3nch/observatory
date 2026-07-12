# Contract - Typed Read Tool Skeleton

Status: accepted skeleton — contract set v0.1 by `decisions/2026-07-12-m14-contract-and-read-boundary-rulings.md`; M14 still owns the real typed-read contract
Authority: skeleton contract (does not authorize API/MCP implementation; subordinate to `02-boundaries.md` and future M14 acceptance)
Version: 0.1
Date: 2026-07-10
Milestone: M7 - Core Contract Planning
Source research: `research/rg3-evidence-id-citation-model.md`, `research/rg5-freshness-staleness-volatility.md`, `research/rg8-claim-safety-report-language.md`, `research/rg12-consumer-contract-inputs.md`; supporting inputs from all prior M7 contract drafts and root boundary law
Supersedes / superseded by: none

---

## Purpose

This skeleton defines the contract-level expectations for future typed read tools that return shaped evidence packs from Observatory without exposing raw SQL, raw mystery rows, credentials, customer private data, strategy, recommendations, or accepted conclusions.

It is intentionally a skeleton. M14 owns the real typed read API/MCP contract and prototype. M7 only preserves the evidence-pack shape, required warnings, blind-spot output expectations, and forbidden access patterns so later implementation cannot bypass the contracts drafted here.

---

## Governing boundaries

This skeleton operationalizes these rules:

- Observatory stores observations, not conclusions.
- The connected LLM interprets at read time.
- Accepted conclusions promote out to the owning consumer.
- LLMs and agents receive shaped evidence packs, not direct database access.
- Customer first-party data is overlay-only unless future owner ruling changes law.
- Provider data is observed testimony, not truth.
- Evidence IDs/citation handles must resolve to status-aware evidence packs.
- Freshness, volatility, provider attribution, sample-bound, absence, rights/retention, raw-support, and consumer-promotion warnings must travel with evidence.

On conflict, `02-boundaries.md` and accepted contracts win.

---

## Definitions

### Typed read tool

A future API/MCP/read interface that accepts bounded, typed requests and returns shaped evidence packs.

A typed read tool is not a general SQL interface, report generator, strategy engine, provider runner, capture runner, customer database, or workflow tool.

### Evidence pack

A structured response containing evidence IDs, observation context, source/provenance, freshness, rights/retention posture, caveats, and claim-use warnings needed for safe downstream interpretation.

### Shaped evidence

Evidence returned in a controlled output format that excludes forbidden data and includes required caveats.

### Coverage/blind-spot output

A read-tool output section that states what evidence was not covered, which surfaces/panels/providers were not observed, what source/capture paths remain blocked, and what claim limitations follow.

Coverage/blind-spot output does not authorize capture expansion or strategy.

---

## Contract rules

### R1. Read tools return evidence, not conclusions

Typed read tools may return evidence packs and warning labels.

They must not return stored recommendations, accepted conclusions, customer report paragraphs, strategy verdicts, workflow tasks, or action plans as Observatory records.

### R2. Direct SQL is forbidden

LLMs, agents, consumers, and downstream tools must not receive direct SQL/database access through this skeleton.

Future M14 work may design controlled read tools only.

### R3. Raw mystery rows are forbidden

Read tools must not dump arbitrary database rows, raw provider payloads, raw JSON blobs, or unfiltered table records.

They must return shaped evidence with explicit status/caveat fields.

### R4. Evidence lookup must be status-aware

Any evidence ID or citation handle resolution must respect evidence status:

```text
active
superseded
withdrawn
expired_by_retention
blocked_by_rights
invalidated
```

Blocked, withdrawn, expired, or invalidated evidence must not be returned as normal active evidence.

### R5. Read tools must preserve scope

Every response must include scope context and must not cross scopes unless a future owner ruling and accepted contract permit it.

### R6. Read tools must preserve provider attribution

Provider metrics, scores, results, confidence values, estimates, rankings, citations, and payload-derived values must remain provider-attributed.

Read tools must not crown a truth-provider or average provider disagreement into fake truth.

### R7. Read tools must return claim-use warnings

Any read response that could support a claim must include claim-use status and caveats from claim-safety and freshness contracts.

### R8. Read tools must expose coverage gaps and blind spots

Responses must state known limits where relevant:

```text
unobserved surfaces
unobserved providers
unobserved query panels
unobserved locales/devices/languages
stale or missing panel runs
blocked source families
blocked capture instruments
missing overlay context
sample-size limits
unresolved provider incomparability
```

Blind spots are evidence limitations, not capture instructions.

### R9. Read tools must not trigger capture or spend

A read output may say recapture is recommended or required for a claim.

It must not execute or schedule provider pulls, manual capture, browser capture, recurring watches, or spend.

### R10. Overlay paths must be no-storage

If a future typed read tool accepts overlays, the output must prove/read-state:

```text
overlay_used
overlay_source_type
external_overlay_reference
overlay_no_storage_warning
overlay_discard_required
overlay_freshness_warning
```

M7 does not implement overlay acceptance.

### R11. Consumer promotion must be explicit

If evidence approaches recommendation, prediction, causality, report language, workflow state, or accepted conclusion, the read tool must set `consumer_promotion_required` or equivalent.

### R12. Read tools must not expose credentials or raw private paths

Responses must not include credentials, provider secrets, private file paths, local raw archive paths, customer private identifiers, or hidden workflow references.

### R13. Typed inputs must be narrow

Future read requests must specify allowed request type, scope, evidence IDs or query/panel context, claim intent, and output use. Free-form broad data pulls are forbidden by default.

### R14. Unknown request intent fails closed

If request intent is unclear or asks for recommendation/report/task/prediction/causality storage, the tool must reject or return evidence-only support with promotion warning.

### R15. This skeleton does not authorize implementation

No API, MCP, schema, migration, auth system, dashboard, provider integration, capture runner, overlay path, or consumer integration is authorized by this skeleton.

---

## Required fields / shapes

These are contract-level skeleton expectations, not API schema.

### Future read request shape

```text
read_request_id
consumer_name or caller_class
request_type
scope_id or permitted scope_request
scope_class
claim_intent
current_or_historical_use
evidence_ids if direct lookup
citation_handles if applicable
query_panel_id if applicable
query_panel_version_id if applicable
panel_run_id if applicable
requested_evidence_families
freshness_requirement
overlay_supplied
overlay_type if applicable
allowed_output_use
```

### Future evidence-pack response shape

```text
read_response_id
evidence_pack_id if applicable
request_type
scope_id
scope_class
evidence_ids
citation_handles if available
report_safe_reference if later admitted
observation_ids
source_families
provider_or_capture_instruments
capture_methods
query_panel_id if applicable
query_panel_version_id if applicable
panel_run_id if applicable
captured_at values
provider_reported_times if available
freshness_status
volatility_class
evidence_statuses
rights_class
retention_class
raw_support_status
claim_status
claim_use_warning
freshness_warning
provider_attribution_required
sample_bound_warning
absence_warning
incomparability_warning
rights_retention_warning
coverage_blind_spots
consumer_promotion_required
overlay_warnings if applicable
```

### Read request types

```text
evidence_lookup
citation_resolution
panel_evidence_pack
claim_support_check
provider_testimony_read
provider_cross_check_read
freshness_check
overlay_alignment_read_future_only
coverage_blind_spot_read
```

### Forbidden request types

```text
run_capture
schedule_capture
spend_provider_budget
store_recommendation
write_customer_report
create_workflow_task
accept_conclusion
export_raw_database
query_sql
store_overlay
```

---

## Fail-closed behavior

- Missing scope blocks read.
- Unknown request type blocks read.
- Rights/retention-blocked evidence cannot be exposed as active.
- Expired/withdrawn/invalidated evidence must be blocked or status-caveated.
- Missing freshness blocks strong current claim support.
- Missing provider attribution blocks provider metric output.
- Missing panel/run context blocks longitudinal/absence claims.
- Missing overlay no-storage metadata blocks overlay use.
- Request for recommendation/report/task/prediction/causality storage is rejected or redirected to consumer.
- Request for direct SQL/raw rows is rejected.
- Request crossing scopes without owner ruling is rejected.

---

## Forbidden patterns

This skeleton forbids:

```text
generic SQL MCP tool over Observatory
raw table dump to LLM
raw provider JSON returned by default
customer private overlay cached in tool memory
read tool creating recommendations
read tool creating report paragraphs as Observatory records
read tool creating Neon Ronin tasks
read tool accepting Kaizen decisions
read tool triggering provider pulls
read tool scheduling recurring capture
read tool exposing credentials
read tool hiding caveats
read tool averaging providers into truth
read tool using stale evidence as current without warning
```

Fake-mustache variants are also forbidden:

```text
smart_read_strategy_tool
evidence_to_action_endpoint
truth_summary_read
raw_debug_read_for_llm
customer_report_generator_read
recapture_now_flag
agent_task_from_evidence
```

---

## Examples

### Valid future request - evidence lookup

```text
request_type: evidence_lookup
consumer_name: kaizen
evidence_ids:
  - ev_market_serp_20260710_d83a10
claim_intent: historical_observation_claim
allowed_output_use: governance_doc_support
```

Why valid:

- It asks for evidence support.
- It uses evidence IDs.
- It does not request a recommendation or raw database access.

### Invalid request - direct SQL

```text
request_type: query_sql
sql: select * from observations
```

Why invalid:

- Direct SQL/raw mystery rows are forbidden.
- LLMs and agents get shaped evidence packs only.

### Valid future request - provider cross-check read

```text
request_type: provider_cross_check_read
comparison_subject_type: keyword
query_panel_id: qp_market_001
claim_intent: comparative_claim
```

Why valid as a future shape:

- It requests a caveated comparison.
- It does not ask for truth-provider or winner logic.

### Invalid request - recommendation creation

```text
request_type: store_recommendation
recommendation: Target this keyword in the title.
```

Why invalid:

- Recommendations belong to the owning consumer.
- Observatory stores evidence, not strategy.

### Valid future coverage/blind-spot output

```text
coverage_blind_spots:
  - AI answer surfaces not observed
  - mobile SERP not observed
  - customer overlay not supplied
  - evidence older than requested freshness window
```

Why valid:

- It exposes limits.
- It does not create a capture task or strategy recommendation.

---

## Owner-ruling candidates

M14 or owner ruling must decide:

- final typed read request/response shape;
- authentication/authorization and consumer/caller classes;
- whether citation handles are global or artifact-local in read outputs;
- whether report-safe references appear in read outputs before M15;
- whether any coverage/blind-spot summaries may be persisted;
- whether overlay alignment reads are admitted;
- whether provider cross-check disagreement summaries are computed only at read time or can persist after owner ruling;
- whether any read-tool output is allowed for SearchClarity customer-facing workflows.

Default until ruled:

```text
Skeleton only.
No implementation.
No API/MCP tool.
No direct SQL.
No raw row access.
No customer-facing report-safe exposure.
No overlay handling.
```

---

## Deeper-research blockers

Relevant blockers:

- DR9 - SearchClarity customer-facing report language validation.
- DR10 - Customer first-party overlay contract.
- DR14 - Evidence ID, citation handle, and report-safe reference finalization.
- DR16 - Consumer authentication / authorization model.
- DR17 - Provider credential and secret handling posture.
- DR15 - Hammer matrix hostile-path expansion.

M14 owns the real typed read API/MCP contract.

---

## Hammer expectations

M8/M14 hammers must prove:

- no direct SQL access;
- no raw mystery rows;
- evidence statuses are respected;
- rights/retention blocked evidence does not leak;
- customer/private data is rejected;
- overlay no-storage is enforced before any overlay path;
- provider attribution is preserved;
- provider disagreement is not averaged into truth;
- stale evidence cannot support current claims without warning/block;
- coverage/blind-spot output does not trigger capture or strategy;
- recommendations, reports, tasks, predictions, and accepted conclusions promote out;
- credentials and raw private paths are never exposed;
- cross-scope reads fail closed by default.

Relevant categories:

```text
H1 scope isolation
H2 rights fail-closed
H3 retention enforcement
H4 customer-private rejection
H5 no recommendation storage
H8 provider attribution and disagreement
H9 freshness / volatility
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

This skeleton feeds:

- M8 - read-tool hostile-path hammers.
- M10 - schema planning constraints for read shapes.
- M14 - typed read API / MCP contract and prototype.
- M15 - SearchClarity proof workflow.
- M16 - provider cross-check proof.
- M17 - overlay/internal telemetry proof.

---

## Non-authorizations

This skeleton does not authorize:

```text
API implementation
MCP implementation
schema design
migrations
dashboard work
provider pulls
provider admission
capture runner work
overlay handling
customer-facing reports
SearchClarity integration
Neon Ronin workflow integration
Kaizen decision integration
agent direct database access
```

---

## Change log

```text
0.1 - 2026-07-10 - initial skeleton from RG3/RG5/RG8/RG12 and completed M7 draft contracts; final read-tool contract deferred to M14
```
