# M17 Owned Telemetry Overlay Fixture-Backed Proof Task Proposal

Status: authorized exact implementation task
Authority: `decisions/2026-07-12-m17-owned-telemetry-overlay-fixture-proof-authorization.md`; implementation remains bounded to this exact task
Milestone: M17 - Owned Telemetry Overlay Proof
Date: 2026-07-12

---

## Goal

Implement one bounded local synthetic fixture-backed proof showing that request-local owned/internal or customer first-party telemetry can be aligned with Observatory evidence and discarded without storage, evidence promotion, identity leakage, file intake, recommendation generation, provider execution, or persistence.

## Exact implementation boundary

Allowed package:

```text
src/observatory_overlay_proof/
  __init__.py
  models.py
  fixtures.py
  align.py
  errors.py
  cli.py
```

Allowed tests:

```text
tests/test_overlay_contract.py
tests/test_overlay_discard.py
tests/test_overlay_hostile_paths.py
tests/test_overlay_scope.py
tests/test_overlay_determinism.py
tests/test_overlay_no_side_effects.py
```

Allowed proof metadata:

```text
test-results/m17-overlay-proof-result-register.json
planning-inbox/m17-overlay-local-test-evidence.md
planning-inbox/m17-overlay-closure-readiness-review.md
```

No external repository integration is authorized.

## Allowed fixtures

Only committed synthetic values embedded in code or test fixtures:

- one synthetic owned/internal time series;
- one synthetic customer-first-party time series with no customer identity;
- one synthetic intervention timeline;
- fresh, stale, unknown, and missing-freshness cases;
- aligned and misaligned evidence windows;
- two isolated synthetic scopes;
- private-field/file/path/screenshot/export hostile cases containing invented placeholders only.

No real analytics, account IDs, URLs, files, screenshots, exports, credentials, or provider data may be added.

## Implement exactly

```text
build_overlay_request
validate_overlay_request
align_overlay_to_evidence
build_overlay_alignment_response
build_discard_status
serialize_overlay_alignment_response
```

Do not implement:

```text
store_overlay
cache_overlay
hash_private_values
assign_evidence_id
promote_overlay_to_observation
read_file_or_screenshot
parse_csv_or_pdf
fetch_provider_data
recommend_strategy
generate_report
trigger_capture
network_listener
MCP registration
persistence
```

## Request requirements

Closed request fields:

```text
contract_version
request_id
caller_class
scope_id
overlay_kind
external_overlay_reference
overlay_supplied_by_consumer
overlay_timestamp
overlay_freshness_status
overlay_scope_context
overlay_no_storage_assertion
overlay_discard_required
overlay_allowed_use
field_manifest
values
alignment_intent
```

Customer identity, account IDs, external files, arbitrary prose, provider credentials, and report context are forbidden.

## Response requirements

Every successful response contains:

```text
contract_version
request_id
response_id
scope_id
external_overlay_reference
overlay_kind
alignment_disposition
aligned_evidence_units
alignment_summary
required_caveats
overlay_discard_status
overlay_persisted: false
overlay_cached: false
overlay_logged: false
overlay_evidence_promoted: false
overlay_values_returned: false
consumer_promotion_required: true
customer_facing_output_authorized: false
```

The alignment summary may contain only bounded comparisons such as direction, count, window overlap, and missing-context warnings. It must not contain overlay values, customer identity, causal claims, recommendations, or report prose.

## Closed errors

```text
blocked_request_type
blocked_scope
blocked_cross_scope
blocked_missing_metadata
blocked_unknown_freshness
blocked_no_storage_not_asserted
blocked_discard_not_required
blocked_private_identity
blocked_file_or_screenshot
blocked_field_overreach
blocked_canonical_ingestion
blocked_evidence_identity
blocked_recommendation_or_causality
blocked_provider_or_capture_action
not_found
```

Errors must not echo rejected values.

## Discard proof

Tests must prove:

- no module-level mutable cache or registry;
- request and fixture inputs remain unmodified;
- returned response contains no overlay values;
- no separate overlay-derived manifest or field inventory is returned or retained;
- no hashes or fingerprints of overlay values are retained;
- repeated calls do not reveal prior values;
- cross-scope calls cannot access other overlay inputs;
- no file/database/network/subprocess/log side effects occur.

This is code-path discard proof only, not secure memory wiping.

## Required test command

```powershell
cd C:\dev\observatory
$env:PYTHONPATH = (Join-Path $PWD "src")
python -m unittest discover -s tests
```

## Acceptance criteria

Implementation return is reviewable only when:

- M17 proof contract and owner rulings are accepted;
- hostile-path plan is accepted;
- this exact task is separately authorized;
- all existing and new tests pass;
- Git diff check passes;
- no real private data, file, screenshot, export, credential, raw provider payload, report prose, or external reference is staged;
- proof limits are recorded honestly.

## Explicit non-authorizations

```text
real customer or owner-private telemetry
customer identity or account records
screenshots/files/CSV/PDF/export intake
overlay storage/cache/logging
canonical ingestion or evidence promotion
provider calls or recurring capture
report generation or recommendation storage
Postgres, schema, or migrations
production API/MCP or integration
```

## Proposed owner authorization phrase

```text
APPROVE M17 OWNED TELEMETRY OVERLAY FIXTURE-BACKED PROOF TASK
```
