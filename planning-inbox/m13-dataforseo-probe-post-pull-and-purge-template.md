# M13 DataForSEO Probe Post-Pull and Purge Template

Status: template
Authority: none — does not authorize a provider request, second pull, persistence, or M13 closure
Milestone: M13 — Provider Admission and Controlled Pull Plan

---

## Purpose

Record the result of the single authorized probe, classify the response, verify cost and evidence handling, and prove raw purge.

This template is used only after a lawful one-request execution.

---

## Probe Identity

```text
probe_id:
recipe_id: m13-dataforseo-serp-probe-v0-1
approval_reference:
approval_commit:
implementation_commit:
preflight_id:
operator:
submitted_at:
completed_at:
```

---

## Request Proof

```text
endpoint:
normalized_request_payload_sha256:
duplicate_prevention_key:
API_requests_used:
billable_tasks_used:
retries_used: 0
polling_requests_used: 0
request_matched_accepted_recipe: yes/no
```

Required:

```text
API_requests_used: 1
billable_tasks_used: 1 or provider-documented non-billable failure state
request_matched_accepted_recipe: yes
```

Any mismatch is a control breach and blocks further provider work.

---

## Cost Proof

```text
maximum_allowed_cost: 0.10 USD
preflight_expected_cost:
provider_top_level_cost:
provider_task_level_cost:
cost_fields_agree: yes/no/not_applicable
actual_cost_within_ceiling: yes/no
```

If the cost exceeds the ceiling, record the breach and stop. Do not retry or attempt to compensate with another request.

---

## Response Classification

Choose exactly one:

```text
normal_provider_response
provider_authentication_error
provider_request_error
provider_throttle_or_limit
provider_error_shape
unknown_shape
local_transport_failure
local_evidence_failure
```

```text
response_class:
provider_status_code:
provider_status_message:
task_status_code:
task_status_message:
HTTP_status_if_available:
```

Only `normal_provider_response` may proceed to field summarization.

No class may produce admitted Observatory observations during M13.

---

## Raw Evidence Proof

```text
raw_payload_pointer:
raw_payload_sha256:
raw_payload_bytes:
raw_payload_media_type:
raw_written_at:
hash_verified_after_write: yes/no
raw_path_inside_approved_root: yes/no
raw_path_git_ignored: yes/no
raw_path_cloud_synced: no
```

A failed hash or unsafe path blocks summarization and triggers controlled purge/recovery.

---

## Sensitive-Content Review

```text
credentials_present: yes/no
customer_private_data_present: yes/no
customer_identity_present: yes/no
payment_or_account_details_present: yes/no
unexpected_sensitive_content_present: yes/no
review_notes:
```

If any prohibited content is present:

```text
quarantine locally
produce no committable summary containing that content
purge under the accepted emergency posture
record only the minimal permitted incident note
```

---

## Shape Fingerprint

```text
shape_fingerprint_version:
shape_fingerprint:
field_path_set_hash:
field_type_set_hash:
top_level_keys:
field_path_count:
required_field_presence:
provider_error_fields:
provider_cost_fields:
provider_timestamp_fields:
provider_url_fields:
```

Classification:

```text
known_shape
new_shape_seen
compatible_extension
breaking_change
semantic_change_suspected
provider_error_shape
unknown_unclassified
```

```text
drift_status:
```

One sample cannot establish long-term stability.

---

## Field Summary Questions

Answer without copying unnecessary raw result content:

1. What top-level keys were returned?
2. What status, error, task, and cost fields were returned?
3. What nested result paths were returned?
4. Which timestamps appeared, and what did they seem to represent?
5. Which fields were provider estimates, scores, or model outputs?
6. Which fields appeared stable identity/provenance fields?
7. Which fields appeared volatile, optional, or result-specific?
8. Which fields might deserve later structured promotion?
9. Which fields should remain raw-support-only?
10. Were undocumented or unexpected fields present?
11. Did the payload suggest parser or schema risk?
12. Did any field threaten customer/private-data boundaries?

Reminder:

```text
This is payload-shape evidence, not schema approval.
```

---

## Boundary Review

```text
provider_output_remained_attributed: yes/no
strategy_or_recommendation_created: no
database_write_occurred: no
observation_ingestion_occurred: no
API_or_MCP_exposure_occurred: no
customer_facing_output_created: no
recurring_capture_created: no
second_request_sent: no
```

Any forbidden `yes` is a boundary breach.

---

## Stop-Condition Result

```text
stop_condition_triggered: yes/no
stop_condition_name:
stop_condition_time:
response_handling_after_stop:
```

No stop condition may cause an automatic retry.

---

## Post-Pull Review

```text
actual cost stayed within ceiling: yes/no
request count stayed within ceiling: yes/no
exact accepted request executed: yes/no
response classified safely: yes/no
raw handling complied: yes/no
sensitive-content review passed: yes/no
hash/manifest/summary/fingerprint produced: yes/no
provider testimony remained provider-attributed: yes/no
schema decision avoided: yes/no
second request avoided: yes/no
```

```text
reviewer:
reviewed_at:
review_result: pass/block/further_review_required
```

A `pass` means the single probe was handled correctly. It does not authorize another probe.

---

## Purge Proof

Raw response must be purged by the accepted deadline.

Before purge:

```text
pre_purge_raw_sha256:
pre_purge_bytes:
purge_due_at:
```

Purge action:

```text
purged_at:
purge_actor:
purge_reason:
purge_command_or_method:
raw_file_absent_after_purge: yes/no
path_containment_check_passed: yes/no
```

Manifest survival:

```text
sanitized_manifest_retained: yes/no
sanitized_field_summary_retained: yes/no
shape_fingerprint_retained: yes/no
retention_basis:
```

No retained artifact may contain credentials, account identifiers, raw result content, customer/private data, or disallowed provider content.

---

## Second-Pull Decision

```text
second_pull_authorized: no
```

Possible recommendation for owner review:

```text
stop M13 provider execution work
amend decision for a distinct second probe
reject further provider work
proceed to M13 closure review if exit criteria are met
```

```text
recommended_disposition:
reason:
```

The recommendation is not authority.

---

## M13 Closure Input

Record whether the probe produced enough evidence to review M13 closure:

```text
provider admission scope proven:
pull recipe proven:
cost controls proven:
stop conditions proven:
raw handling and purge proven:
no-customer/no-recurring/no-API/no-schema boundaries held:
remaining blockers:
```

M13 closes only through an explicit accepted closure decision and authority-file updates.

---

## Final Rule

```text
One request means one request.
A clean probe earns review, not momentum-based permission.
Hash it, summarize it, purge it, stop.
```
