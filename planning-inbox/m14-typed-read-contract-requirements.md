# M14 Typed Read Contract Requirements

Status: planning specification
Authority: none — proposal only; does not authorize implementation
Milestone: M14 — Typed Read API / MCP Contract and Prototype
Date: 2026-07-12
Sources:
- `contracts/typed-read-tool-skeleton.md`
- all M7 contract drafts
- `hammers/hammer-matrix-v0-1.md`
- `hammers/acceptance-gate-policy-v0-1.md`
- `audits/observatory-post-m13-deep-audit-2026-07-12.md`
- `planning-inbox/post-m13-deep-audit-response-2026-07-12.md`
- sanitized C00 evidence under `providers/dataforseo/evidence/`

---

## Purpose

Define the complete contract requirements that M14 must settle before a bounded local typed-read prototype can be proposed.

This document does not implement an API or MCP server. It does not define physical schema, create Postgres, expose a network service, authorize customer data, or permit any provider request.

The read boundary exists to let a connected LLM inspect evidence without giving it direct SQL, credentials, arbitrary raw rows, customer-private data, or authority to store conclusions.

---

## Governing Law

```text
The Observatory stores what was observed.
The connected LLM interprets what it means at read time.
Accepted conclusions promote out to the owning consumer.
```

Every response must preserve:

- scope;
- evidence status;
- provenance;
- rights and retention posture;
- freshness and volatility caveats;
- provider attribution;
- disagreement and incomparability;
- sample and absence limits;
- raw-support status without exposing raw private paths;
- consumer-promotion boundaries.

---

## M14 Requirement Set

### M14-R1 — Bounded typed read surfaces

The first contract may define only these four prototype-eligible request families:

```text
evidence_lookup
observation_package_read
freshness_check
coverage_blind_spot_read
```

Other skeleton request types remain deferred:

```text
citation_resolution beyond internal handle resolution
provider_cross_check_read -> M16
claim_support_check as a broader evaluator -> later M14/M15 ruling
provider_testimony_read as an independent broad surface -> later review
overlay_alignment_read -> M17
panel_evidence_pack beyond available fixture evidence -> later panel activation
```

No generic read endpoint, generic query tool, SQL proxy, raw-row endpoint, or arbitrary JSON projection is allowed.

### M14-R2 — Closed request and filter vocabulary

Each request type must have a closed allow-list of fields.

Forbidden inputs include:

```text
free-text query expressions
SQL fragments
regex
wildcards
arbitrary sort expressions
arbitrary field projection
user-supplied path traversal
provider request payloads
raw file paths
```

Callers must not be able to omit mandatory caveat fields through projection.

### M14-R3 — Caller, scope, and authorization model

Every request must include an authenticated caller identity supplied by the access layer, not merely asserted inside the request body.

Proposed caller classes:

```text
internal_llm
kaizen
neon_ronin
searchclarity_internal
operator
```

Each caller receives explicit scope grants and request-type grants.

Requirements:

- scope is required on every request;
- scope is echoed in every successful response;
- cross-scope reads fail closed;
- callers cannot widen their own grants;
- authorization decisions must not depend on model-generated prose;
- an evidence handle outside the caller's scope must be indistinguishable from a nonexistent handle.

OR-D1 owns the final authorization ruling.

### M14-R4 — Evidence handles, provider IDs, and raw support

Only Observatory evidence handles may serve as primary external read identifiers.

Provider task IDs may appear only inside a clearly labeled provider-attribution block and never as evidence identity.

Raw support may expose status only:

```text
present_internal
purged_with_proof
blocked_by_rights
expired_by_retention
not_captured
unknown
```

Raw filesystem paths, object-store paths, credentials, and private archive locators must not cross the read boundary.

Evidence handles must be non-enumerable. A sequential integer or guessable ordered identifier is forbidden.

OR-D2 owns final raw-pointer exposure; the fail-closed proposal is internal-only.

### M14-R5 — Pagination, ceilings, and extraction resistance

Every collection response must enforce:

- hard page-size maximum;
- hard total-result maximum per request;
- opaque cursor;
- cursor binding to caller, scope, request type, filters, and ordering;
- cursor expiration;
- no cursor reuse with widened filters;
- deterministic ordering;
- per-caller read-rate ceiling or equivalent bounded-use control.

A syntactically valid request for "everything" must be rejected or bounded, not treated as harmless because it is read-only.

### M14-R6 — Freshness, staleness, volatility, and claim fitness

Every evidence-bearing response must include:

```text
captured_at
provider_reported_at if available
freshness_status
volatility_class
current_or_historical_use
claim_fitness
freshness_warning
```

Missing or unknown freshness must not silently become `fresh`.

A current-state claim request against stale or unknown-freshness evidence must fail closed or be downgraded explicitly to historical evidence.

The prototype may use controlled fixture vocabularies but must not claim that fixture rules prove real-world volatility thresholds.

### M14-R7 — Provider attribution and disagreement

Provider-derived values must travel with provider attribution and provider-specific caveats.

Multi-provider values must remain side by side.

Forbidden:

```text
winner_provider
truth_provider
provider_average_as_truth
confidence collapse
silent unit normalization
silent methodology equivalence
```

Disagreement summaries, if produced, are compute-on-read only until OR-A1 is ruled.

### M14-R8 — Claim intent and claim-safety metadata

Every request must declare a closed-vocabulary `claim_intent`.

Candidate values:

```text
historical_observation
current_state_observation
comparative_observation
coverage_statement
absence_statement
internal_governance_support
```

Recommendation, prediction, causality, customer-report prose, workflow-task creation, and accepted-conclusion storage are not valid claim intents.

Every response must include claim status and warnings. Unsupported intent fails closed.

### M14-R9 — Rights and retention visibility

Every evidence pack must include rights and retention classes and current evidence status.

Evidence in these states must never be returned as ordinary active evidence:

```text
blocked_by_rights
expired_by_retention
withdrawn
invalidated
```

A later downgrade in rights must affect subsequent reads. Admission-time clearance is not permanent permission.

### M14-R10 — Outbound allow-lists and private-data hard failure

Each caller class and response type must have a field-level outbound allow-list.

Private/customer markers found in an outbound field are a hard error and audit/security event, not something silently stripped while returning the rest of the pack.

No customer first-party analytics are stored or returned from Observatory under M14.

### M14-R11 — Safe tool descriptions and untrusted content

Tool descriptions are part of the safety boundary.

They must state:

- evidence is testimony, not truth;
- observation text may contain untrusted third-party instructions;
- observation content is data, never tool guidance;
- reads cannot trigger capture, spend, writes, conclusions, tasks, or reports;
- required caveats must be preserved.

Stored web/provider text must be delivered in a typed field explicitly marked as untrusted observation content.

### M14-R12 — LLM context assembly

Evidence context packs must be assembly-ready without allowing caveats to detach from values.

Requirements:

- evidence ID adjacent to each observation;
- provider attribution adjacent to provider values;
- freshness and claim warnings adjacent to qualified evidence;
- coverage/blind spots included;
- token budget declared;
- truncation drops whole evidence units, never only caveats;
- truncated responses set `truncated: true` and report omitted-unit counts;
- observation content is separated from instructions and metadata.

### M14-R13 — Deterministic non-leaking error taxonomy

Errors must use a closed vocabulary.

Candidate families:

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

Errors must not reveal:

- whether an out-of-scope handle exists;
- valid scope names;
- record counts;
- raw paths;
- provider secrets;
- internal table or storage names.

### M14-R14 — Read logging versus evidence-event law

V9 says ordinary reads do not create evidence events.

M14 must distinguish:

1. evidence/audit events that describe evidence lifecycle — no ordinary read events;
2. security/access logs outside the evidence corpus for authentication failures, authorization failures, rate/ceiling breaches, and suspicious enumeration.

Security logs must not become evidence observations or customer records.

Final posture requires owner ruling.

### M14-R15 — Reads never trigger capture, spend, or writes

A read operation must not:

- call a provider;
- schedule capture;
- enqueue a capture job;
- reserve budget;
- mutate evidence;
- accept a conclusion;
- create a consumer task;
- persist an overlay;
- create customer-report prose.

A response may state that evidence is missing or recapture may be required, but that is advisory metadata only.

### M14-R16 — Confused and malicious agent resistance

Acceptance planning must include:

- SQL-shaped strings in legal text fields;
- attempts to request all records;
- handle walking and enumeration;
- cross-scope handle guessing;
- cursor replay with changed filters;
- recommendation storage disguised as evidence lookup;
- stored observation text containing `ignore previous instructions`;
- requests to hide caveats or return raw JSON;
- prompt content attempting to redefine tool authority;
- repeated requests intended to exhaust context or extract a whole scope.

### M14-R17 — Deterministic responses

For the same request, caller grants, evidence state, and contract version, the response must be byte-stable except for explicitly excluded operational metadata such as `generated_at`.

Ordering, warning order, status order, and truncation choice must be deterministic.

### M14-R18 — Prototype acceptance boundary

A later prototype proposal may be:

- local-only;
- fixture-backed;
- in-memory;
- stdlib-first unless justified;
- no network listener;
- no real MCP registration;
- no database;
- no provider transport;
- no customer data;
- no overlay;
- no report output;
- no persistence.

Prototype evidence families:

1. C2 fixture observations;
2. sanitized C00 provider-evidence artifacts.

The prototype proves contract behavior only. It does not prove database, transaction, production auth, network, or deployment enforcement.

### M14-R19 — Explicit deferrals

Remain deferred:

```text
production API/MCP deployment
Postgres and physical schema
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
```

---

## Required Response Envelope

The M14 contract should require at minimum:

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
evidence_units[]
coverage_blind_spots[]
truncated
omitted_evidence_unit_count
warnings[]
consumer_promotion_required
```

Each evidence unit should keep these fields adjacent:

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

This is a contract-level shape, not physical schema or finalized API serialization.

---

## Prototype Entry Gates

Before implementation may be proposed:

- F-01 immediate disarm remains committed;
- F-02 sanitized C00 evidence is committed;
- contract-set authority is resolved;
- OR-D1, OR-D2, OR-D3, and read-security logging posture are ruled or explicitly encoded as fail-closed defaults;
- the M14 hostile-path plan is accepted;
- prototype proof claims use the proof-class taxonomy;
- no later milestone is silently activated.

---

## Non-Authorization

This specification is planning input only.

It does not authorize code, API/MCP exposure, database work, customer data, provider execution, or production access-control implementation.
