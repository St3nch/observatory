# M13 DataForSEO Probe Preflight Record Template

Status: template
Authority: none — no funding, implementation, credential, or request authority
Milestone: M13 — Provider Admission and Controlled Pull Plan

---

## Use

Complete this record only after the controlling decision is accepted and a tested implementation exists.

A completed preflight record is evidence that submission gates were checked. It is not a substitute for owner confirmation of the exact paid request.

---

## Identity

```text
preflight_id:
probe_id:
recipe_id: m13-dataforseo-serp-probe-v0-1
created_at:
operator:
repository_commit:
implementation_commit:
approval_reference:
approval_commit:
approval_status:
```

Required:

```text
approval_status: accepted
```

Anything else blocks execution.

---

## Exact Recipe

```text
provider: DataForSEO
method: POST
endpoint: /v3/serp/google/organic/live/advanced
keyword: observatory test page
location_code: 2840
language_code: en
device: desktop
os: windows
depth: 10
unnamed_optional_fields_present: false
```

Sanitized request body:

```json
[
  {
    "keyword": "observatory test page",
    "location_code": 2840,
    "language_code": "en",
    "device": "desktop",
    "os": "windows",
    "depth": 10
  }
]
```

```text
normalized_request_payload_sha256:
duplicate_prevention_key:
recipe_matches_accepted_decision: yes/no
```

Any mismatch blocks execution.

---

## Funding and Pricing

```text
account_funded: yes/no
funding_authority_reference:
funding_date:
current_minimum_payment_verified:
official_price_interface_used:
price_verification_at:
exact_request_price_or_maximum_expected_charge:
currency: USD
maximum_allowed_charge: 0.10
optional_surcharges_absent: yes/no
price_within_ceiling: yes/no
```

Attach only a sanitized pointer or owner-authored note. Do not store payment details, account identifiers, screenshots containing private account information, or credentials.

If exact price is unclear or above `$0.10`:

```text
STOP — do not submit.
```

---

## Request Ceilings

```text
billable_task_ceiling: 1
expected_billable_tasks: 1
API_request_ceiling: 1
expected_API_requests: 1
retry_ceiling: 0
polling_ceiling: 0
repeat_ceiling: 0
second_request_authority: none
```

```text
all_ceilings_pass: yes/no
```

---

## Account Controls

```text
account_level_spend_limit_available: yes/no/unknown
account_level_spend_limit_configured:
repetitive_task_limit_available: yes/no/unknown
repetitive_task_limit_configured:
control_evidence_pointer:
```

Unavailable account controls do not relax CLI ceilings. Record unavailability honestly.

---

## Credentials

```text
credential_source: environment/local ignored config
DATAFORSEO_LOGIN_present: yes/no
DATAFORSEO_PASSWORD_present: yes/no
credential_values_printed: no
credential_values_persisted: no
redaction_check_passed: yes/no
```

Never place credential values in this record.

---

## Duplicate Check

```text
duplicate_registry_checked: yes/no
matching_duplicate_key_found: yes/no
execution_lease_available: yes/no
prior_submission_marker_found: yes/no
```

Required result:

```text
matching_duplicate_key_found: no
execution_lease_available: yes
prior_submission_marker_found: no
```

Uncertain duplicate state blocks execution.

---

## Evidence Root and Retention

```text
evidence_root:
evidence_root_is_local: yes/no
evidence_root_is_git_ignored: yes/no
evidence_root_is_not_cloud_synced: yes/no
raw_posture: capture_and_purge_raw
retention_deadline:
purge_command_available_and_tested: yes/no
path_escape_check_passed: yes/no
```

Any `no` blocks execution.

---

## Rights and Scope

```text
rights_class: provider_limited_internal_probe
allowed_use: internal payload-shape inspection only
customer_data_present: no
customer_private_markers_present: no
marketplace_target_present: no
recommendation_intent_present: no
recurring_capture_present: no
```

Any prohibited scope blocks execution.

---

## Implementation Proof

```text
implementation_readiness_review:
full_test_command:
full_test_result:
focused_hostile_test_result:
network_interception_or_fake_transport_proof:
secret_redaction_proof:
one-request-proof:
duplicate-block-proof:
raw-hash-and-purge-proof:
```

All must be current for the implementation commit named above.

---

## Stop-Condition Checklist

Mark each `clear` or `triggered`:

```text
decision_not_accepted:
recipe_mismatch:
endpoint_changed:
price_unverified:
price_above_ceiling:
optional_cost_field_present:
task_ceiling_exceeded:
request_ceiling_exceeded:
retry_or_polling_required:
credentials_missing:
duplicate_state_uncertain:
duplicate_found:
evidence_root_not_ignored:
rights_or_retention_unclear:
customer_or_private_marker_present:
implementation_tests_not_current:
```

Required:

```text
all stop conditions: clear
```

---

## Operator Attestation

```text
I verified that this preflight matches the accepted owner decision and tested implementation.
I verified the exact request price is at or below $0.10.
I verified one request is sufficient and no retry or polling will occur.
I verified no customer/private data is involved.
I verified the local raw destination is Git-ignored and governed by the purge deadline.
I understand this preflight permits no second request.
```

```text
operator_name:
operator_confirmation_at:
```

---

## Final Paid-Request Confirmation

The execute command must display:

```text
approval reference
endpoint
sanitized request
request SHA-256
maximum allowed charge
verified expected charge
task/request ceilings
raw retention deadline
all stop conditions clear
```

Required exact confirmation input:

```text
--confirm-paid-request <normalized_request_payload_sha256>
```

A preflight record without matching explicit confirmation does not authorize the request.

---

## Result

```text
preflight_result: pass/block
block_reason:
preflight_completed_at:
```

---

## Final Rule

```text
No accepted decision, no pass.
No exact price, no pass.
No exact hash, no pass.
No clean duplicate state, no pass.
No pass, no request.
```
