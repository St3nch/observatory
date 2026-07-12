# Contract - Provider Cross-Check Proof v0.1

Status: ready for owner acceptance
Authority: proposed M16 proof contract; does not authorize provider execution, purchases, recurring capture, persistence, customer reports, production integration, Postgres, schema, migrations, or production API/MCP
Version: 0.1
Date: 2026-07-12
Milestone: M16 - Provider Cross-Check Proof

---

## Purpose

Define the bounded read-time proof behavior for comparing provider-attributed observations without choosing a truth-provider, averaging unlike testimony, creating consensus or composite scores, hiding disagreement, or storing downstream interpretation.

Core rule:

```text
Compare testimony.
Preserve disagreement.
Expose comparability limits.
Never manufacture truth.
```

---

## Governing boundary

M16 may compare committed synthetic fixtures and already-admitted sanitized provider evidence only.

M16 does not admit a new provider, endpoint, account, purchase, credential, task, pull, recurring capture program, raw archive, database, report workflow, or production integration.

Each provider observation remains independently governed by source admission, rights, retention, freshness, volatility, status, parser/drift state, and provider attribution.

---

## Definitions

### Provider comparison request

A bounded request to evaluate whether two or more provider-attributed observations can be described side by side under one declared comparison context.

It is not a request to select a provider, compute truth, recommend a tool, rank providers, or create strategy.

### Comparison dimensions

The explicit attributes that determine whether observations are aligned enough for comparison:

```text
subject type and value
metric family and metric definition
surface or endpoint
query/prompt/panel item and version
locale, language, location, device
capture time window
provider-reported data time
scope
rights, retention, freshness, volatility, status
```

### Comparison disposition

A deterministic read-time result stating how the observations may be used:

```text
comparable_with_caveat
partially_comparable
unresolved_incomparability
blocked_missing_attribution
blocked_missing_context
blocked_rights_or_retention
blocked_source_not_admitted
blocked_status_or_drift
historical_only
```

### Disagreement type

A provider-attributed description of how the testimony differs:

```text
value_difference
presence_absence_difference
rank_position_difference
coverage_difference
definition_difference
freshness_difference
surface_difference
provider_model_difference
provider_time_difference
raw_shape_or_parser_difference
provider_error_difference
```

---

## Contract rules

### R1. Provider attribution is mandatory

Every side must retain provider name, family, endpoint/surface, metric/result name, evidence reference, captured time, provider-reported time if available, rights, retention, freshness, volatility, and status.

Missing attribution blocks the affected side.

### R2. Comparison context must be explicit

Strong comparison is blocked when subject, metric family, surface, scope, or other material dimensions are unknown.

### R3. Same-looking proprietary metrics are incomparable by default

Keyword difficulty, authority-like metrics, AI visibility scores, confidence scores, and other proprietary metrics from different providers remain `unresolved_incomparability` unless definitions and scales are sufficiently aligned by later accepted methodology.

### R4. No truth, winner, consensus, average, or composite

Forbidden outputs include:

```text
truth_provider
winner_provider
best_provider
consensus_value
average_truth
blended_rank
blended_difficulty
blended_authority
provider_accuracy_score
provider_trust_score
```

### R5. Each provider keeps its own time and freshness state

The proof must not collapse capture times, provider-reported times, freshness, or volatility into one shared status.

Material time distance requires a warning and may force partial comparability or unresolved incomparability.

### R6. Rights, retention, admission, status, and drift apply per side

A blocked, expired, withdrawn, invalidated, unadmitted, drift-blocked, parser-blocked, or provider-error observation cannot silently participate as normal testimony.

### R7. Presence/absence remains sampled and contextual

One provider observing a result while another does not may be described only within the compared provider, surface, query/prompt, time, and sampling contexts.

It does not prove universal presence or absence.

### R8. Provider disagreement is read-time by default

M16 cross-check results are derived read outputs. No persistent Disagreement Ledger, summary cache, comparison table, materialized score, or stored interpretation is authorized.

### R9. Provider personality/profile notes are testimony metadata only

Stable provider-method notes may be attached only as cited, versioned, caveated provider-method context. They must not become trust rankings or provider-selection advice.

### R10. Consumer promotion remains required

Any provider choice, tool-purchase advice, strategy, recommendation, report conclusion, task, or accepted interpretation belongs to the owning consumer.

---

## Request shape

```text
contract_version
request_id
request_type: provider_cross_check
scope_id
comparison_subject_type
comparison_subject_value
comparison_purpose
claim_intent
provider_evidence_handles
comparison_dimensions
allowed_output_use: evidence_support_only
```

Requests are closed-field and customer-clean. No arbitrary prose, provider credentials, account data, report text, recommendations, or overlay values.

---

## Response shape

```text
contract_version
request_id
response_id
scope_id
comparison_context
provider_sides
comparison_disposition
disagreement_types
aligned_dimensions
misaligned_dimensions
capture_time_distance
provider_time_distance
required_caveats
claim_use_warning
consumer_promotion_required: true
truth_value_produced: false
winner_selected: false
composite_score_produced: false
```

Each provider side retains its own attribution, status, freshness, rights, retention, and evidence reference.

---

## Fail-closed behavior

Block or downgrade when:

- provider identity or evidence reference is missing;
- subject or metric family differs;
- proprietary definitions are unknown;
- surface, locale, device, language, panel, or scope materially differs;
- capture/provider times are materially separated without safe interpretation;
- rights, retention, source admission, status, parser, or drift blocks either side;
- one side is provider error output;
- request asks for winner, truth, average, consensus, composite, recommendation, purchase advice, or report conclusion;
- cross-scope comparison is attempted;
- disagreement is removed or caveats are suppressed.

---

## Allowed first proof

One local, in-memory, fixture-backed proof may later be separately authorized using:

- committed synthetic provider observations;
- sanitized C00 provider testimony for structural attribution only;
- two isolated synthetic scopes;
- no live provider calls, credentials, purchases, reports, customer data, overlays, network listener, database, or persistence.

Required fixture cases:

- aligned rank-position difference;
- aligned provider-estimate value difference;
- proprietary metric definitions unknown;
- capture-time-distance warning;
- fresh versus stale testimony;
- presence/absence disagreement;
- rights- or retention-blocked side;
- provider-error or drift-blocked side;
- cross-scope attempt;
- winner/average/composite hostile requests.

---

## Explicit non-authorizations

```text
provider calls
DataForSEO requests
Ahrefs or Semrush purchases
provider credentials
recurring capture
persistent Disagreement Ledger
comparison cache or table
truth score
winner logic
average or consensus value
composite score
provider recommendation
customer report generation
customer data or overlays
Postgres
schema or migrations
production API/MCP
production integration
```

---

## Change log

```text
0.1 - 2026-07-12 - M16 proof contract drafted from accepted provider testimony, cross-check, freshness, claim-safety, typed-read, and consumer contracts
```
