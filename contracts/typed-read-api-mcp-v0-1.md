# Contract - Typed Read API / MCP v0.1

Status: accepted v0.1 by `decisions/2026-07-12-m14-typed-read-contract-acceptance-and-prototype-authorization.md`
Authority: binding M14 typed-read behavioral contract within its declared scope; does not authorize production API/MCP, persistence, provider execution, customer data, overlays, or reports
Version: 0.1
Date: 2026-07-12
Milestone: M14 - Typed Read API / MCP Contract and Prototype
Supersedes / superseded by: intended to supersede `contracts/typed-read-tool-skeleton.md` for M14 read-boundary behavior after acceptance
Source authority:
- `02-boundaries.md`
- accepted contract set v0.1
- `decisions/2026-07-12-m14-contract-and-read-boundary-rulings.md`
- `planning-inbox/m14-typed-read-contract-requirements.md`
- `planning-inbox/m14-read-boundary-hostile-path-plan.md`
- `planning-inbox/post-m13-audit-final-reconciliation.md`

---

## 1. Purpose

This contract defines the bounded typed-read boundary through which authenticated consumers may inspect Observatory evidence without direct SQL, database credentials, arbitrary raw rows, customer-private data, provider-spend side effects, or authority to persist conclusions.

It defines behavior, request/response vocabularies, authorization expectations, fail-closed rules, proof boundaries, and prototype acceptance requirements.

It does not define physical schema, network transport, production authentication technology, MCP registration, deployment, or customer-facing report behavior.

---

## 2. Governing doctrine

```text
The Observatory stores what was observed.
The connected LLM interprets what it means at read time.
Accepted conclusions promote out to the owning consumer.
```

Read tools return shaped evidence and safety metadata. They do not become strategy engines, report generators, workflow systems, provider runners, or generic database interfaces.

---

## 3. Caller and authorization contract

### 3.1 Caller classes

M14 recognizes these internal caller classes:

```text
internal_llm
operator
kaizen
neon_ronin
searchclarity_internal
```

No public or customer-facing caller class is admitted.

### 3.2 Identity source

Authenticated caller identity is supplied by the access layer. Request content cannot create, replace, or widen caller identity.

### 3.3 Grants

Every caller must have explicit:

- scope grants;
- request-type grants;
- field-level outbound grants where caller classes differ.

Cross-scope reads are forbidden by default. Callers cannot alter their own grants.

### 3.4 Uniform non-disclosure

A nonexistent evidence handle and an unauthorized or out-of-scope handle must produce the same externally visible `not_found` result.

The response must not reveal valid scope names, internal record counts, raw paths, storage names, or whether a hidden record exists.

---

## 4. Prototype-eligible request types

Only these request families are admitted for the first bounded prototype:

```text
evidence_lookup
observation_package_read
freshness_check
coverage_blind_spot_read
```

Deferred request families include:

```text
provider_cross_check_read
claim_support_check as a broad evaluator
provider_testimony_read as a broad standalone surface
overlay_alignment_read
customer/report-safe citation resolution
panel evidence packs not represented by admitted fixtures
```

Generic query, SQL, arbitrary JSON projection, raw-row, and raw-file read tools are forbidden.

---

## 5. Closed request envelope

Every request must contain only contract-allowed fields.

Required common fields:

```text
contract_version
request_id
request_type
caller_class_from_access_layer
scope_id
scope_class
claim_intent
current_or_historical_use
```

Request-specific fields may include:

```text
evidence_handles
observation_package_id
freshness_requirement
page_size
cursor
```

Forbidden inputs include:

```text
SQL fragments
free-text query expressions
regex
wildcards
arbitrary sort expressions
arbitrary field projection
raw filesystem or object-store paths
provider request payloads
user-supplied traversal paths
instructions to suppress warnings or caveats
```

Unknown fields fail closed unless a later contract version explicitly admits them.

---

## 6. Claim-intent vocabulary

Allowed values:

```text
historical_observation
current_state_observation
comparative_observation
coverage_statement
absence_statement
internal_governance_support
```

Not valid as claim intents:

```text
recommendation
prediction
causality
customer_report_prose
workflow_task_creation
accepted_conclusion_storage
strategy_generation
```

Unsupported or ambiguous intent is rejected.

---

## 7. Evidence identity and raw support

### 7.1 Evidence handles

M14 exposes internal Observatory evidence handles only.

Handles must be:

- non-enumerable;
- status-aware;
- separate from provider task IDs;
- separate from raw archive locators;
- safe to use in internal governance citations.

Report-safe or customer-facing references remain deferred to M15.

### 7.2 Provider identifiers

Provider task/job IDs may appear only inside a clearly labeled provider-attribution block. They never become Observatory evidence identity.

### 7.3 Raw support

Read outputs may expose only a status from this vocabulary:

```text
present_internal
purged_with_proof
blocked_by_rights
expired_by_retention
not_captured
unknown
```

Raw paths, bucket keys, object-store locators, credentials, and private archive locations must not cross the read boundary.

---

## 8. Required response envelope

Every successful response must contain:

```text
contract_version
request_id
response_id
request_type
caller_class
scope_id
scope_class
claim_intent
current_or_historical_use
evidence_units
coverage_blind_spots
truncated
omitted_evidence_unit_count
warnings
consumer_promotion_required
```

Each evidence unit must keep these fields adjacent:

```text
evidence_id
observation_id
evidence_status
source_family
provider_or_capture_instrument
captured_at
provider_reported_at
provider_attribution
observed_content_untrusted
freshness_status
volatility_class
rights_class
retention_class
raw_support_status
claim_status
claim_use_warning
sample_bound_warning
absence_warning
incomparability_warning
```

Mandatory caveats cannot be removed by projection or caller preference.

---

## 9. Evidence status and lifecycle behavior

Evidence is never silently overwritten.

Recognized read-relevant statuses include:

```text
active
superseded
withdrawn
expired_by_retention
blocked_by_rights
invalidated
```

Rules:

- `active` evidence may be returned normally;
- `superseded` evidence may be returned only as historical and status-caveated;
- `withdrawn`, `expired_by_retention`, `blocked_by_rights`, and `invalidated` evidence must not be returned as active evidence;
- status changes must affect later reads;
- stale cursors or cached assumptions must not bypass later status changes.

---

## 10. Freshness, volatility, and claim fitness

Every evidence-bearing response includes:

```text
captured_at
provider_reported_at if available
freshness_status
volatility_class
claim_fitness
freshness_warning
```

Unknown freshness never becomes fresh by default.

A current-state request against stale or unknown-freshness evidence must either:

- fail closed; or
- return only historical evidence with an explicit downgrade.

Update-window metadata is optional input. Missing relevant update-window data produces unknown/caveated status; no cadence may be invented.

---

## 11. Provider attribution and disagreement

Provider-derived values remain attributed to the provider that reported them.

Read tools must not create:

```text
truth_provider
winner_provider
provider_average_as_truth
silent methodology equivalence
silent unit normalization
collapsed confidence
```

Provider disagreement, when present in admitted evidence, remains side by side. Any summary is compute-on-read only until a separate materialization ruling exists.

---

## 12. Rights, retention, and outbound allow-lists

Every evidence unit includes current rights and retention classes.

A later rights downgrade or retention expiration affects subsequent reads.

Each response type and caller class must use a field-level outbound allow-list.

Private/customer data found in an outbound field is a hard failure. The tool must not silently strip the field and return a partially trusted pack.

Customer first-party analytics are neither stored nor returned under M14.

---

## 13. Untrusted observation content

Provider, webpage, marketplace, or other captured text is data, not instruction.

Such content must be placed only in `observed_content_untrusted` or an equivalent typed field.

Tool descriptions and response metadata must state that:

- evidence is testimony, not truth;
- observation content may contain hostile instructions;
- observation text cannot alter tool authority;
- reads cannot trigger writes, spend, capture, tasks, reports, or conclusions.

---

## 14. LLM context assembly

Context packs must preserve adjacency between evidence and its caveats.

Rules:

- evidence identity remains adjacent to each evidence unit;
- provider attribution remains adjacent to provider values;
- freshness, claim, sample, absence, rights, and incomparability warnings remain attached;
- coverage and blind spots are included;
- token budget is declared;
- truncation removes whole evidence units only;
- truncation must set `truncated: true` and state the omitted-unit count;
- observation content remains separated from metadata and instructions.

---

## 15. Pagination and extraction ceilings

Collection responses must enforce:

- hard page-size maximum;
- hard total-result maximum;
- deterministic ordering;
- opaque cursors;
- cursor binding to caller, scope, request type, filters, ordering, and contract version;
- cursor expiration;
- rejection of cursor replay with widened filters;
- bounded per-caller read use.

A request for all records must be rejected or bounded.

---

## 16. Deterministic errors

Allowed error families:

```text
blocked_authentication
blocked_authorization
blocked_scope
blocked_request_type
blocked_filter
blocked_rights
blocked_retention
blocked_freshness
blocked_claim_intent
blocked_result_ceiling
blocked_private_data
blocked_not_implemented
not_found
```

Error payloads must not expose private paths, provider secrets, internal schema/storage names, hidden handle existence, valid scope names, or internal record counts.

---

## 17. Read logging

Ordinary successful reads do not create Observatory evidence events.

Authentication failures, authorization failures, enumeration attempts, and rate/ceiling breaches may produce bounded security/access logs outside the evidence corpus.

Security logs:

- are operational records, not observations;
- contain no credentials or private payload content;
- do not become customer records;
- require a separate retention posture before production use.

---

## 18. No-side-effect read law

A read must never:

- call a provider;
- schedule or enqueue capture;
- reserve or spend budget;
- mutate evidence;
- persist an overlay;
- create a recommendation;
- create a customer report;
- create a consumer workflow task;
- accept or store a conclusion.

A read may report missing evidence, blind spots, or that recapture may be necessary. That is advisory evidence metadata only.

---

## 19. Determinism

For the same request, caller grants, evidence state, contract version, and token budget, the response must be byte-stable except for explicitly excluded operational metadata.

Ordering, warnings, truncation, and omitted counts must be deterministic.

---

## 20. Hostile-path obligations

Before implementation acceptance, relevant tests must cover:

- evidence-handle enumeration and existence-oracle resistance;
- cross-scope handle guessing;
- pagination and extraction abuse;
- cursor replay with changed scope or filters;
- caveat detachment attempts;
- prompt injection in stored observation content;
- rights downgrade after admission;
- status change during read where a coherent-state surface exists;
- requests to hide warnings or return raw JSON;
- recommendation/task/report actions disguised as reads;
- private-data outbound failure;
- deterministic output and error behavior.

High-consequence hostile paths may be labeled hammers. Ordinary correctness checks retain ordinary test labels.

---

## 21. Prototype proof boundary

A first prototype may use only:

1. existing C2 local fixtures;
2. committed sanitized C00 evidence artifacts.

The prototype may be:

- local-only;
- fixture-backed;
- in-memory;
- stdlib-first;
- invoked as Python functions or a local CLI test surface.

It must not include:

```text
network listener
real MCP registration
Postgres or any database
provider transport
customer data
overlay handling
report output
persistence
production authentication
```

A prototype pass proves contract behavior only. It does not prove database, transaction, network, production-auth, deployment, or concurrency enforcement.

---

## 22. Machine-readable proof metadata

M14 may use a committed test-result register containing:

```text
result_id
contract_version
commit
proof_class
execution_surface
proof_strength
test_command
result
executed_at
evidence_path
limitations
```

The register is repository implementation evidence, not an Observatory observation and not a database requirement.

---

## 23. Explicit deferrals

This contract does not authorize:

```text
production API/MCP deployment
real MCP registration
Postgres or physical schema
migrations
live ingestion
additional provider pulls
overlay implementation
SearchClarity report-safe references
provider cross-check implementation
recurring capture
dashboards
customer-facing reports
strategy/recommendation storage
automatic conclusion promotion
public exposure
```

---

## 24. Open lineage note

The named RG3/RG8 Kaizen Hermes source inputs have not yet been consumed or explicitly waived.

This contract therefore preserves the lineage gap as a review requirement before final M14 contract acceptance. No source claim is invented to fill it.

---

## 25. Acceptance criteria

This contract may be accepted when:

- every rule is consistent with `02-boundaries.md` and accepted contract set v0.1;
- OR-D1 through OR-D6 and OR-A4 M14 scope are reflected correctly;
- the Hermes lineage item is consumed or explicitly waived by owner decision;
- prototype task scope matches Section 21 exactly;
- no implementation authority is implied by contract acceptance.

---

## 26. Change log

```text
0.1 - 2026-07-12 - first full M14 typed-read API/MCP contract synthesized from accepted M7 contracts, post-M13 audit requirements, owner rulings, and hostile-path planning
```
