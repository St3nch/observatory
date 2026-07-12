# M16 Provider Cross-Check Fixture-Backed Proof Task Proposal

Status: authorized exact implementation task
Authority: `decisions/2026-07-12-m16-provider-cross-check-fixture-proof-authorization.md`; implementation remains bounded to this exact task
Milestone: M16 - Provider Cross-Check Proof
Date: 2026-07-12

---

## Goal

Implement one bounded local fixture-backed proof that demonstrates provider disagreement, comparability, attribution, time-distance warnings, and fail-closed behavior without provider calls, purchases, credentials, recurring capture, persistence, customer data, reports, overlays, Postgres, or production integration.

---

## Exact implementation boundary

Allowed package:

```text
src/observatory_provider_cross_check/
  __init__.py
  models.py
  fixtures.py
  compare.py
  errors.py
  cli.py
```

Allowed tests:

```text
tests/test_provider_cross_check_contract.py
tests/test_provider_cross_check_comparability.py
tests/test_provider_cross_check_hostile_paths.py
tests/test_provider_cross_check_scope.py
tests/test_provider_cross_check_determinism.py
tests/test_provider_cross_check_no_side_effects.py
```

Allowed proof metadata:

```text
test-results/m16-provider-cross-check-result-register.json
planning-inbox/m16-provider-cross-check-local-test-evidence.md
planning-inbox/m16-provider-cross-check-closure-readiness-review.md
```

No provider, SearchClarity, Neon Ronin, or Kaizen repository integration is authorized.

---

## Dependencies and reuse

Reuse accepted M14 typed-read fixture concepts and existing admitted/sanitized provider testimony where structurally useful.

Do not call the M13 provider runner, network code, subprocess, database driver, or external filesystem.

---

## Required fixtures

- aligned rank-position difference;
- aligned provider-estimate value difference;
- same-looking proprietary scores with unknown definitions;
- materially separated capture times;
- fresh versus stale testimony;
- sampled presence/absence disagreement;
- rights-blocked or retention-expired side;
- unadmitted source family;
- provider-error or drift-blocked side;
- two isolated synthetic scopes.

Provider labels must be synthetic unless using sanitized DataForSEO structural testimony already committed. No Ahrefs/Semrush data may be invented as factual provider output; synthetic fixtures must be labeled synthetic.

---

## Implement exactly

```text
build_cross_check_request
validate_cross_check_request
classify_comparability
classify_disagreement_types
build_provider_cross_check
serialize_provider_cross_check
```

Do not implement:

```text
choose_provider
compute_truth
compute_average
compute_consensus
compute_composite_score
recommend_provider
persist_disagreement
call_provider
capture_provider_data
network_listener
MCP registration
report generation
```

---

## Response requirements

Every successful response contains:

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

Provider sides retain independent attribution, metric definition posture, timestamps, freshness, volatility, rights, retention, source admission, evidence status, and evidence handle.

---

## Closed errors

```text
blocked_request_type
blocked_scope
blocked_cross_scope
blocked_missing_attribution
blocked_missing_context
blocked_rights_or_retention
blocked_source_not_admitted
blocked_status_or_drift
blocked_truth_request
blocked_winner_request
blocked_average_or_consensus
blocked_composite_request
blocked_recommendation
blocked_persistence
not_found
```

No private or hidden values may be echoed.

---

## No-side-effect proof

Static/runtime checks must prove the package does not:

- write files during comparison reads;
- mutate fixtures;
- call provider/network/subprocess code;
- import database drivers;
- access credentials or environment secrets;
- generate reports, recommendations, tasks, purchases, or captures;
- persist comparison output.

The result register is written only as an explicit repository proof-recording step outside read functions.

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

- M16 contract and owner rulings are accepted;
- hostile-path plan is accepted;
- this exact task is separately authorized;
- all existing and new tests pass;
- diff check passes;
- no real provider data beyond already admitted sanitized evidence is added;
- no credentials, customer/private data, raw provider payload, report prose, or external file is staged;
- proof classification and limitations are recorded honestly.

---

## Explicit non-authorizations

```text
provider calls or purchases
DataForSEO requests
Ahrefs or Semrush execution
credentials
recurring capture
persistent Disagreement Ledger
truth/winner/average/consensus/composite logic
customer data or overlays
report generation
Postgres
schema or migrations
production API/MCP
production integration
```

---

## Proposed owner authorization phrase

```text
APPROVE M16 PROVIDER CROSS-CHECK FIXTURE-BACKED PROOF TASK
```
