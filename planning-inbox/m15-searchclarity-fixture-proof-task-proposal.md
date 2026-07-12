# M15 SearchClarity Fixture-Backed Proof Task Proposal

Status: exact implementation task proposal; not implementation authority
Authority: none until owner explicitly approves this exact task after contract and ruling gates
Milestone: M15 - SearchClarity Proof Workflow
Date: 2026-07-12

---

## Goal

Implement one bounded local fixture-backed proof that demonstrates SearchClarity report-support boundary behavior on top of the accepted M14 typed-read prototype without customer data, report generation, overlays, external files, production integration, provider calls, or persistence.

The proof demonstrates evidence-side support dispositions, caveat preservation, synthetic report-safe reference separation, consumer-promotion behavior, and hostile-input rejection.

It does not prove final report wording, customer-facing correctness, SearchClarity production integration, real overlay discard, database enforcement, network/MCP behavior, or deployment.

---

## Exact implementation boundary

Allowed new package:

```text
src/observatory_searchclarity_proof/
  __init__.py
  models.py
  fixtures.py
  report_support.py
  references.py
  errors.py
  cli.py
```

Allowed tests:

```text
tests/test_searchclarity_report_support_contract.py
tests/test_searchclarity_customer_boundary.py
tests/test_searchclarity_claim_blockers.py
tests/test_searchclarity_reference_boundary.py
tests/test_searchclarity_hostile_paths.py
tests/test_searchclarity_determinism.py
```

Allowed proof metadata:

```text
test-results/m15-searchclarity-proof-result-register.json
planning-inbox/m15-searchclarity-local-test-evidence.md
planning-inbox/m15-searchclarity-proof-closure-readiness-review.md
```

Existing files may be amended only when required to:

- register project status in `pyproject.toml`;
- export explicitly admitted package symbols;
- index proof evidence;
- record owner-local test execution.

No SearchClarity repository edits or integration are authorized.

---

## Dependencies and reuse

The proof must reuse the accepted M14 package:

```text
src/observatory_typed_read_prototype/
```

It must not duplicate or weaken M14 scope, authorization, status, freshness, cursor, caveat, or no-side-effect rules.

The M15 package is a consumer-boundary adapter over successful typed-read responses, not a new database, API, report generator, or provider client.

---

## Fixture boundary

Allowed inputs:

- committed synthetic Observatory evidence fixtures;
- committed sanitized C00 structural/provider-testimony evidence;
- synthetic SearchClarity request fixtures containing no customer identity, order/report ID, private analytics, report prose, recommendations, screenshots, files, URLs, or overlay values.

Required synthetic cases:

- one supportable historical public observation;
- one current-state request blocked or downgraded by freshness;
- one sampled-absence case with required warning;
- one provider metric case with attribution;
- one unadmitted marketplace case;
- one AI/GEO single-run case limited to sampled observation;
- one rights-blocked or retention-expired case;
- two isolated synthetic scopes for cross-scope tests.

No real SearchClarity customer, client, shop, order, report, or engagement identifier may appear.

---

## Implemented functions

Implement exactly:

```text
build_report_support_request
build_report_support_pack
classify_report_support_disposition
map_synthetic_report_safe_references
validate_customer_clean_request
```

Optional pure helper:

```text
serialize_report_support_pack
```

Do not implement:

```text
write_report
generate_report_prose
recommend_strategy
approve_report
publish_report
deliver_report
store_customer
store_order
store_consent
accept_overlay
read_file_or_screenshot
call_searchclarity_repo
call_provider
network_listener
MCP registration
persistence
```

---

## Request behavior

Admit only the closed request types from the proposed M15 contract:

```text
report_support_evidence_lookup
report_support_observation_package
report_support_freshness_check
report_support_coverage_check
```

Caller is fixed to authenticated `searchclarity_internal` supplied separately from request data.

Request must contain:

```text
contract_version
request_id
request_type
scope_id
claim_intent
current_or_historical_use
requested_evidence_families
freshness_requirement
report_support_purpose_code
allowed_output_use
```

No arbitrary free-text report context or field projection.

---

## Response behavior

Every successful response must contain:

```text
contract_version
request_id
response_id
scope_id
claim_intent
report_support_disposition
evidence_units
required_caveats
coverage_blind_spots
reference_mode
report_support_references
consumer_promotion_required: true
customer_facing_output_authorized: false
truncated
omitted_evidence_unit_count
```

Mandatory caveats remain attached to evidence units. The adapter must not convert evidence into customer report prose.

---

## Synthetic report-safe references

The proof may generate deterministic opaque artifact-local fixture references.

Requirements:

- separate from internal evidence handles;
- non-sequential and non-enumerable in the fixture design;
- bound to one synthetic scope and one evidence unit;
- no provider ID or raw pointer material;
- no public/customer lookup endpoint;
- unauthorized and nonexistent references return the same external `not_found` result;
- clearly labeled `synthetic_report_safe_fixture`.

The proof must state that this does not establish the production format or public resolution design.

---

## Automatic blockers

Implement the owner-ruled blocker set exactly after acceptance:

```text
blocked_by_rights
expired_by_retention
withdrawn
invalidated
blocked_private_data
missing_provider_attribution
missing_absence_sample_context
blocked_freshness_for_current_use
missing_mandatory_caveats
source_family_not_admitted
```

Superseded evidence may support historical-only use with status warning.

Stale/unknown evidence may support historical-only use when claim intent permits; it never silently supports current-state use.

---

## Customer/private rejection

The validator must fail hard on representative markers and structural fields for:

- customer names/emails/company/shop/account IDs;
- order, report, gig, invoice, payment, delivery, revision IDs;
- private analytics values;
- screenshots, CSV/PDF paths, external file contents;
- consent records/signatures;
- report paragraphs and recommendations;
- overlay values or no-storage assertions attempting to bypass overlay deferral.

Structural closed-field validation is primary. Marker tests are supplemental and must not be presented as complete PII detection.

No private values may be echoed in errors or proof logs.

---

## Claim-safety behavior

Tests must prove:

- historical observation support preserves time/context;
- current-state claims block/downgrade on stale or unknown freshness;
- sampled absence cannot become universal absence;
- provider metrics require provider attribution;
- AI/GEO single-run evidence cannot become endorsement, influence, authority, recommendation, or durable score;
- marketplace evidence stays blocked when the source family is not admitted;
- provider disagreement cannot create a winner, average, or composite score;
- final report wording remains outside Observatory.

---

## Overlay behavior

Real overlays are not implemented.

Any overlay-shaped request, private analytics field, screenshot/file reference, or customer export must fail with:

```text
blocked_not_admitted
```

or:

```text
blocked_private_data
```

The proof must show no cache, storage, evidence ID, comparison result, logging of values, or downstream action.

---

## No-side-effect proof

Static and runtime checks must prove the M15 package does not:

- write files during report-support reads;
- mutate M14 fixtures;
- call provider code;
- import database drivers;
- invoke network or subprocess functions;
- generate report artifacts;
- create recommendations/tasks;
- persist handoff data;
- accept overlays;
- access the SearchClarity repository.

Writing the test-result register remains an explicit proof-recording step outside read functions.

---

## Test classification

High-consequence hammers:

- customer identity laundering;
- customer/private input rejection;
- report/recommendation laundering;
- caveat detachment;
- report-safe reference enumeration/cross-scope access;
- claim-status bypass;
- overlay smuggling;
- cross-scope aggregation;
- no-side-effect consumer boundary.

Contract-acceptance tests:

- request/response envelope;
- support-disposition vocabulary;
- mandatory promotion/customer-facing block flags;
- deterministic ordering;
- warning shapes;
- synthetic reference mapping;
- context-pack whole-unit truncation.

Unit/static tests:

- model validation;
- serialization;
- fixed vocabulary;
- fixture containment;
- forbidden import/path checks.

---

## Required test command

```powershell
cd C:\dev\observatory
$env:PYTHONPATH = (Join-Path $PWD "src")
python -m unittest discover -s tests
```

No test may access network resources.

---

## Acceptance criteria

Implementation return is reviewable only when:

- the full M15 contract is accepted;
- OR-E1 through OR-E5 and OR-F1 are ruled;
- the hostile-path plan is accepted;
- this exact task is separately authorized;
- all existing and new tests pass;
- Git diff has no whitespace/conflict errors;
- no customer/private data, report prose, external file, overlay, raw provider payload, or ignored evidence is staged;
- the result register states proof class, surface, strength, and limitations;
- closure review distinguishes synthetic fixture proof from customer-facing/production proof.

---

## Explicit non-authorizations

```text
customer data
customer records
private analytics
real overlays
screenshot/file intake
report generation
report storage
report delivery
recommendations
SearchClarity repository integration
production report-safe references
public/customer resolution
Postgres
schema or migrations
provider calls
recurring capture
production API/MCP
strategy storage
automatic conclusion promotion
```

---

## Proposed owner authorization phrase

```text
APPROVE M15 SEARCHCLARITY FIXTURE-BACKED PROOF TASK
```

This phrase would authorize only the exact implementation boundary in this document after all contract and ruling gates are satisfied.
