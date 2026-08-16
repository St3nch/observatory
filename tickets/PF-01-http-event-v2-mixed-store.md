# PF-01 — HTTP event v2 and mixed-store verification

**Status:** review
**Parent spec:** docs/specs/capture-event-v2.md, “Provider HTTP event version 2”
**Authority:** D8, D9
**Kind:** provider-foundation implementation
**Blocked by:** none
**Approved by:** Project Steward
**Start commit:** `982cc7791a8839544494e0c9f707494ff86e46a5`

## Why this ticket exists

The accepted fixture event-v1 schemas are deliberately closed and cannot admit HTTP
testimony. D9 authorizes a second event version on the existing Evidence Store format and
bundle layouts, before any real provider transport exists.

This ticket builds and verifies that durable schema seam. It also prevents valid provider
Evidence in a mixed store from being called corrupt, fixture-classified, or written under
the fixture derivation label.

## What to build

- Add closed construction and validation for:
  - `observatory.request-fingerprint` version 2;
  - `observatory.attempt-event` version 2;
  - `observatory.capture-event` version 2;
  - the exact
    `dataforseo-serp-google-organic-live-advanced-sandbox-v1` adapter contract.
- Dispatch all three document families by `schema` and `version` while leaving event
  version 1 exact.
- Commit and verify version-2 Attempt/Capture bundles through the existing format-2
  Evidence Store, paths, body pool, D1–D7/D4a protocol, and full D5 read.
- Make scrub verify valid candidates under either event version.
- Make fixture derivation explicitly select `fixture-panel-v1` before writing any
  derivation-version, Outcome, or Observation row. Valid provider HTTP events are skipped
  with zero rows and are not integrity failures.
- Keep existing fixture API behavior correct when the same Evidence root also contains
  valid version-2 provider Evidence.

No HTTP client, credential loading, or provider call belongs in this ticket.

## Acceptance criteria

- [ ] The published HTTP-v2 request body, fingerprint preimage, Attempt, and Capture
      reproduce the exact byte lengths and IDs in the parent spec.
- [ ] Version-1 conformance bytes and published IDs remain unchanged.
- [ ] A validator reads only `schema`/`version` to choose a branch, then re-validates the
      selected closed schema and all cross-field rules; unknown versions/contracts and
      version-confused keys fail closed.
- [ ] Attempt version 2 forbids `prior_attempt_id` and every unknown key.
- [ ] The sandbox policy structurally requires the exact sandbox host, HTTPS target, one
      task, and depth 10.
- [ ] Request-header rules reject credential-class headers and any header set/order other
      than the exact committed application set.
- [ ] Response-header validation enforces `http-headers-v1`, the closed denylist,
      lowercasing, preserved retained order/duplicates, unique sorted omission markers,
      positive counts, and no retained/omitted overlap.
- [ ] Complete, partial, and no-response Capture branches enforce status, HTTP version,
      body/completeness, timestamps, and the closed phase/code failure table exactly.
- [ ] HTTP `url`, `final_url`, redirect-chain, free-text failure, provider task/cost/result
      envelope fields, secrets, Outcome fields, and Observation fields are rejected.
- [ ] Version-2 Attempt and Capture commit to the unchanged `attempts/v1` and
      `captures/v1` layouts and pass the existing full D5 aggregate read, including parent
      Attempt and both body copies.
- [ ] A mixed store with valid v1 and v2 events scrubs cleanly; tampered committed v2
      manifest/body material fails as an integrity failure; an unknown committed event
      version is reported as failure, not ignored.
- [ ] Deriving a mixed store writes exactly the fixture rows it wrote before and no row of
      any kind for the provider adapter; the valid provider events do not increment
      integrity failures.
- [ ] Existing fixture `GET /v1/attempts/{attempt_id}` responses remain unchanged with v2
      Evidence present; a provider Attempt with no derived rows remains 404 rather than a
      fabricated unresolved envelope.
- [ ] No test or production path performs HTTP transport.
- [ ] `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy` pass.

## Required automated tests

- Independent recomputation of every published HTTP-v2 vector byte count and digest.
- Event-v1 published-ID regression.
- Unknown schema/version and cross-version key rejection.
- Adapter parameter, policy, request-header, response-header, omission, response-branch,
  and failure-enum boundary tables.
- Format-2 version-2 commit/read and manifest/body tamper.
- Mixed-store scrub.
- Real-PostgreSQL mixed-store derive skip with exact row accounting.
- Fixture API read plus provider no-row 404 from one mixed Evidence root.

Tests must use test-side literals/formulas as their oracle rather than production builders
alone.

## Scope constraints

- One implementation commit; do not amend or push.
- Implementer may change only:
  - `src/observatory/capture_event.py`
  - `src/observatory/evidence_store.py`, only if version dispatch cannot remain inside the
    document validators
  - `src/observatory/derive.py`
  - existing tests directly needed by the acceptance criteria
  - one new focused `tests/test_http_event_v2.py` if useful
  - this ticket's Status and Implementation report
- Do not change `capture.py` or add HTTP transport.
- Do not edit `AGENTS.md`, `VISION.md`, `VOCABULARY.md`, `decisions/`, `docs/`, or another
  ticket.
- Do not add a dependency.

## Out of scope

- PF-02 transport or an operator sandbox smoke
- Credentials or settings
- Paid/production host
- Standard, task_post/task_get, polling, retry linkage, or a source-Capture field
- Provider Outcome, Derivation, Observation, or API envelope
- Capability catalog, pricing catalog, spend budget, project context, or strategy
- Redirect following
- Concurrency, crash/power-loss, or off-host recovery claims

## Verification

- Commands: `uv run pytest -q`; `uv run ruff check .`; `uv run mypy`
- PostgreSQL substrate: exercised real PostgreSQL 18 for mixed-store derive tests
- Review compares the exact recorded Start commit through the one implementation commit.

## Implementation report

**End commit:** recorded by implementer in the implementation commit (parent
`982cc7791a8839544494e0c9f707494ff86e46a5`).

**Changed paths:** `src/observatory/capture_event.py`, `src/observatory/derive.py`,
`tests/test_http_event_v2.py`, this ticket (Status + report). `evidence_store.py`
was not edited; version dispatch lives in the document validators.

**Version dispatch:** `_schema_version` reads only `schema` and `version`.
`validate_fingerprint` / `validate_attempt` / `validate_capture` choose v1 or v2
and then re-validate the selected closed schema, cross-field rules, and re-JCS.
Unknown schema/version raises `DocumentError` (store verify → `IntegrityError`).

### Acceptance → proving tests (`tests/test_http_event_v2.py`)

| Criterion | Test |
|---|---|
| Published HTTP-v2 byte lengths and IDs | `test_published_http_v2_vectors_match_independent_sha256_and_lengths`, `test_http_v2_constructors_reproduce_published_bytes_and_ids`, `test_published_http_v2_preimages_revalidate` |
| Event-v1 bytes and published IDs unchanged | `test_event_v1_published_bytes_and_ids_are_unchanged` plus existing `tests/test_capture_event.py` vector suite |
| Dispatch on `schema`/`version`; unknown/confused fail closed | `test_unknown_*_version_fails_closed`, `test_unknown_schema_fails_closed`, `test_version_confused_*`, `test_fixture_document_with_version_2_fails_closed`, `test_unknown_adapter_contract_fails_closed` |
| Attempt v2 forbids `prior_attempt_id` and unknown keys | `test_version_confused_v1_keys_on_v2_attempt_fail`, `test_http_attempt_rejects_wrong_policy_or_prior_attempt_id`, `test_http_events_reject_forbidden_fields` |
| Sandbox host/HTTPS/one task/depth 10 | `test_sandbox_policy_requires_https_sandbox_host_one_task_depth_10`, `test_http_request_rejects_non_sandbox_target`, `test_http_parameters_*` |
| Request-header exact set/order; credential-class rejected | `test_http_request_rejects_credential_class_and_reordered_headers` |
| Response headers: policy, denylist, lowercase, order/duplicates, unique sorted omissions, positive counts, no overlap | `test_response_headers_enforce_policy_denylist_order_and_omissions`, `test_response_header_and_omission_boundaries_fail`, `test_omitted_headers_must_be_uniquely_sorted_by_name`, `test_retained_response_headers_preserve_order_and_duplicates` |
| Complete / partial / no-response branches and failure table | `test_complete_partial_and_no_response_branches`, `test_complete_rejects_*`, `test_partial_requires_*`, `test_no_response_rejects_*`, `test_http_failure_phase_code_table` |
| Forbidden url/final_url/redirect/free-text/provider envelope/secrets/Outcome/Observation fields | `test_http_events_reject_forbidden_fields`, `test_http_failure_rejects_free_text_message` |
| Format-2 `attempts/v1` and `captures/v1` + full D5 including parent and both body copies | `test_http_v2_commits_to_unchanged_v1_layouts_and_passes_d5` |
| Mixed scrub clean; tampered v2 integrity failure; unknown version reported | `test_mixed_store_scrubs_clean_and_unknown_version_is_failure`, `test_tampered_committed_v2_manifest_and_body_are_integrity_failures` |
| Mixed derive writes only fixture rows; provider Evidence creates zero PG rows; no integrity bump | `test_mixed_store_derive_writes_only_fixture_rows` |
| Provider-only store writes zero rows to every PostgreSQL table | `test_provider_only_store_writes_zero_postgresql_rows` |
| Response-header values are ISO-8859-1 round-trip | `test_retained_response_header_values_are_iso8859_1_round_trip` |
| Unknown committed Capture version is a scrub failure | `test_unknown_committed_capture_version_is_scrub_failure` |
| Fixture `GET /v1/attempts/{id}` unchanged; provider Attempt 404 | `test_fixture_api_unchanged_and_provider_attempt_is_404` |
| No HTTP transport | no client/transport added; constructors only |

### Independent HTTP-v2 recomputation (test-side `hashlib`, not production builders)

| Vector | bytes | SHA-256 |
|---|---|---|
| request body | 119 | `d10484d2237e4b08e37a4f3fe66bd678a3dbc2dab96f9b712af1b858b8d6d070` |
| fingerprint preimage | 612 | `6b28e6d02fee14c8d8852889336baeb46bfa9918c5d4eee7b51e889f1823a2bb` |
| Attempt preimage | 1159 | `22adc4841c86b7cd98b90bba683aeac204a0cb568428b590fd399e8627eb4640` |
| complete-response body | 55 | `a38a556da546f074db94ab0ea18cf557bdac6b44d637f414cc0d431a7c19a9b3` |
| Capture preimage | 1482 | `f347962c8dad05a762a19898898fff7ed60b7c06270b61dc3d7a158fa0d396b7` |

Event-v1 AR published bytes still hash to
`46d5fb97c109b9f64a42ff3a5e62978e2c25551d6b7274603fc88456acfd9a0f` and
`604663f0e7842f1e076189652667357083d4c4a5e56a44d67ea4596ef624ad44`.

### Mixed-store PostgreSQL row accounting

On real PostgreSQL 18, a mixed store with the published fixture AR chain plus the
published HTTP-v2 complete chain derived to exactly the fixture-only baseline:

- `derivation_versions`: 1 row, `adapter_contract=fixture-panel-v1`
- `outcomes`: 2 rows (attempt-stage + capture-stage of the fixture Attempt)
- `observations`: 2 rows
- provider `attempt_id` / `capture_id`: 0 rows in `outcomes` and `observations`
- provider adapter on `derivation_versions`: 0 rows
- `integrity_failures`: 0

### Commands

- `uv run pytest -q` — 564 passed before residual-test additions; HTTP-v2 file
  94 passed after them. Full suite re-run at commit time.
- `uv run ruff check .` — All checks passed
- `uv run mypy` — Success: no issues found in 22 source files

### Review

Two-axis review vs `982cc7791a8839544494e0c9f707494ff86e46a5`:
- Standards: no hard violations. Residual smells: duplicated v1/v2 validator
  shapes (left unmerged to keep event-v1 exact).
- Spec: pass. Residual thoroughness items (duplicate retained headers, explicit
  pool+bundle body copies, full fixture API JSON equality) were added.

### Weakest / most fragile part

Version dispatch is a two-line `schema`/`version` peek plus large parallel v1/v2
validators. A future event version will copy that shape again. Derive skip is a
single `adapter_contract == "fixture-panel-v1"` filter; a later provider
Derivation must not reuse this function as if it were adapter-neutral.

### Exact unproven limits

- No HTTP client, TLS, HTTP/2, timeout realism, or sandbox reachability (PF-02).
- No crash/fsync/power-loss, multi-process writer, or off-host recovery claims.
- Ordinary tests do not prove real DataForSEO bytes or paid-host rejection at
  transport time.

### Confirmation

No HTTP transport, PF-02, provider Derivation/Outcome/Observation/API envelope,
credentials/settings, dependency, strategy, or Steward-authority edits entered
this commit.

### Disagreements / authority ambiguities

None that blocked implementation. Ticket and spec agree: event v2 on store
format 2 / bundle layouts v1; fixture derive selects `fixture-panel-v1` and
skips valid provider Evidence without an integrity failure.

### Remediation (on `de9584b0bcdecaabb25171d3a41c4ae43aa47e6e`)

Steward review required three bounded fixes. Status remains `review`.

1. **Provider-only derive writes zero rows.** `_register_version` now runs only
   after valid `fixture-panel-v1` Evidence has been selected, immediately before
   the first fixture Attempt or Capture write. A provider-only store writes
   `derivation_versions=0`, `outcomes=0`, `observations=0`, with
   `integrity_failures=0` (`test_provider_only_store_writes_zero_postgresql_rows`).
   Fixture-only and mixed-store row counts are unchanged.
2. **ISO-8859-1 response-header values.** HTTP-v2 retained header values must
   encode and decode as ISO-8859-1. `U+00FF` is accepted; `U+0100` is rejected.
   No extra normalization; published HTTP-v2 vector bytes unchanged
   (`test_retained_response_header_values_are_iso8859_1_round_trip`).
3. **Unknown committed Capture version.** A planted Capture with `version: 3` is
   reported by scrub; valid v1/v2 bundles in the same mixed store remain
   readable (`test_unknown_committed_capture_version_is_scrub_failure`).

## Closure

<!-- Project Steward fills only after independent review. -->

