# PF-16 — Keyword Overview F13 transport-capability hardening

**Status:** review  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none; F13 trigger is fired for the next Keyword Overview gate reuse  
**Approved by:** [CHAZ] for provisional ticket review only  
**Start commit:** 14037adf252085625b1e7fe5d159951cf81a8ea1

## Purpose

Final Steward reconciliation: ACCEPTED after required read-only ticket review. This final
reconciliation supersedes the provisional-review label in the header above. Implementation
is authorized only from the exact final ticket commit later issued by the Steward as the
start commit. The implementer records that exact Start commit and sets Status=`review` in
the implementation commit, per `AGENTS.md`.

The read-only review returned `READY_AFTER_TICKET_RECONCILIATION`; the required proof locks
are incorporated below. No live-provider, spend, pricing, panel, or activation authorization
is implied by this acceptance.

Harden the existing DataForSEO Labs Google Keyword Overview Live paid-probe transport gate
to satisfy deferred-register item F13 before the gate is invoked, substantively modified,
or reused again.

The existing adapter already commits an HTTP-v2 Attempt before transport, uses the accepted
PF-09 bounded single-exchange HTTP seam, has a closed paid request contract, and commits at
most one Capture on the ordinary path. F13 records a narrower authority defect: the older
gate still treats caller-visible capability fields such as `request_body`, `document`, and
`_used` as transport authority. Deliberate same-process private-seam abuse using
`object.__setattr__` can therefore replace the bytes/document or reset the visible used flag
after issuance.

This ticket changes only that authority boundary. It performs no provider call and changes
no provider contract, published Evidence bytes, parser, Recipe, Derivation, Observation,
PostgreSQL schema, or read API.

## Authority and trigger

`decisions/deferred.md` F13 requires, before the next live operator invocation, substantive
modification, or reuse of Keyword Overview:

- closure-owned issuance and consumption state;
- committed-Attempt revalidation immediately before send; and
- adversarial tests for body replacement, document replacement, used-flag reset, replay,
  and committed-Evidence tamper.

F13 also requires each affected older gate to remain separately bounded so its published
bytes, one-shot rules, and surface-specific transport behavior stay independently
reviewable. Do not introduce a generic transport-capability framework in this ticket.

The question-resolution gate for this provisional cut is complete:

- [GROK] performed a read-only code-first F13 audit of Keyword Overview, Google Organic,
  Search Mentions, and the newer Target Metrics/Historical comparison patterns;
- [GPT] independently verified F13 and the current Keyword Overview/Organic gate shape plus
  the Target Metrics closure-owned pattern; and
- [CHAZ] approved creation of this bounded Keyword Overview remediation ticket.

No live-provider, spend, pricing, panel, or activation authorization is implied.

## Existing contract that must remain unchanged

Adapter/module:

- module: `src/observatory/dataforseo_paid_probe.py`;
- adapter contract: the existing Keyword Overview paid-probe token and HTTP-v2 branch;
- production path: `/v3/dataforseo_labs/google/keyword_overview/live`;
- policy and authorization ceiling remain exactly as currently accepted;
- one JCS task array per exchange;
- 1..5 caller-supplied keywords;
- `location_code=2840`;
- `language_code="en"`;
- `include_serp_info=false`;
- `include_clickstream_data=false`;
- existing timeout, response-body ceiling, loopback-only internal test seam, credential
  injection/echo handling, one-Attempt-per-Evidence-root rule, inspect behavior, and PF-09
  complete/partial/no-response mapping remain unchanged;
- no retry, redirect follow, pagination, polling, continuation, fallback, response-derived
  follow-up, or second provider exchange.

Previously accepted Keyword Overview Attempt/Capture vectors and every neighboring adapter's
published Evidence identities must remain byte-identical.

## Required transport-authority behavior

The exact implementation shape is reviewable engineering detail, but the accepted behavior
is fixed:

1. **Closure-owned issuance record** — bind exact issued capability identity, concrete
   `EvidenceStore`, `attempt_id`, canonical committed Attempt preimage, exact committed
   request-body bytes, and one-exchange consumption state. Capability-visible
   `attempt_id`/`document`/`request_body`/`_used` may remain mirrors but are not authority.
2. **Closure-owned one-exchange consumption** — a genuinely issued capability may reach the
   HTTP seam at most once; consume before pre-send verification/send-capable work; resetting
   visible `_used` cannot authorize replay; failed pre-send revalidation does not make the
   issuance reusable.
3. **Visible-field mismatch fails closed** — immediately before committed-Evidence
   revalidation/send, issued visible identity/document/body must equal the closure record;
   `object.__setattr__` replacement fails before transport; sent bytes come from closure-owned
   issuance state.
4. **Committed Attempt revalidation immediately before send** — re-read the exact committed
   Attempt by closure-owned `attempt_id`; verify its committed directory; require canonical
   preimage/content-digest equality; read exact committed `request.body`; revalidate the
   existing closed Keyword Overview target/parameters; recompute the closed JCS request body;
   require exact equality across recomputed, committed, and closure-owned bytes; any mismatch
   fails before transport.
5. **No widening of transport authority** — production URL, loopback test override,
   authorization ceiling, credentials, timeout/body ceiling, client seam, and request
   contract remain under their existing boundaries. No provider request is permitted as
   proof.

## Acceptance criteria

- [ ] A genuine issued Keyword Overview capability is backed by closure-owned issuance state
      binding capability identity, concrete Evidence Store, Attempt identity, canonical
      committed document preimage, exact committed request bytes, and consumed state.
- [ ] Exchange authorization and replay prevention use closure-owned state; visible `_used`
      is not transport authority.
- [ ] The issuance is consumed before pre-send verification/send-capable work so failed
      verification cannot be retried by reusing the same capability.
- [ ] Immediately before the only HTTP exchange, the gate verifies issued visible fields
      against the closure record, re-reads and integrity-verifies committed Attempt Evidence,
      verifies canonical identity/preimage, reads exact `request.body`, revalidates the closed
      Keyword Overview contract, recomputes exact JCS bytes, and requires equality across
      committed and closure-owned bytes.
- [ ] `object.__setattr__` replacement of an issued capability's `request_body` cannot reach
      the HTTP handler or change authorized bytes.
- [ ] `object.__setattr__` replacement of an issued capability's `document` with a different
      valid-looking document cannot reach the HTTP handler.
- [ ] After one successful local/mock exchange, resetting visible `_used` to `False` cannot
      cause a second exchange; observed request count remains exactly one.
- [ ] Committed Attempt manifest/object-pool tamper is detected immediately before send and
      reaches zero HTTP handler calls.
- [ ] Committed `request.body` tamper is detected immediately before send and reaches zero
      HTTP handler calls.
- [ ] Evidence-tamper tests exercise actual committed store/bundle paths and prove the
      verifier/re-read path, not merely visible-field comparison.
- [ ] Existing forged/unissued/subclass/cross-store/one-shot/credential/transport tests
      remain green and continue proving their original boundaries.
- [ ] Existing production request body, fingerprint, Attempt/Capture identities, closed
      parameters, one-Attempt-per-root rule, Capture mapping, inspect surface, and neighboring
      adapter identities remain unchanged.
- [ ] No parser, Recipe, Derivation, Outcome, Observation, migration, PostgreSQL, API, F6,
      F7, F12, activation, panel, pricing, or provider-semantic behavior changes.
- [ ] Targeted PF-16 tests pass and `uv run ruff check .` passes. PF-16-touched source/test
      paths typecheck clean. Repo-wide `uv run mypy` must introduce no new errors relative
      to start commit `14037adf252085625b1e7fe5d159951cf81a8ea1`; pre-existing unrelated
      baseline errors are not part of this ticket. Final full-suite verification is [CHAZ]-run.
- [ ] Ordinary tests perform zero DataForSEO/API-host/DNS/public-network activity, use no
      real credentials, create no live provider Evidence, and spend no credits.

### Final reconciled F13 proof locks

These locks are mandatory and narrow the looser acceptance bullets above where needed:

- After issued-capability identity/issuance lookup succeeds, closure-owned consumption is
  set before visible-field comparison, committed-Evidence revalidation, or
  `perform_bounded_http_exchange`. Visible `_used` may mirror state but is not authority.
- Preserve the pre-PF-16 credential and endpoint-failure boundary: after issued-capability
  lookup and replay refusal, `credentials.require_nonempty()` and `_resolved_exchange_url`
  run before closure-owned consumption. A credential-validation or endpoint-validation
  failure therefore leaves the issuance reusable, as at the start commit. Consumption then
  occurs before visible-field comparison and committed-Evidence revalidation.
- If pre-send committed-Evidence revalidation fails, a second `_exchange` attempt using the
  same issued capability must fail one-exchange protection and the HTTP handler count must
  remain exactly zero.
- Revalidation of verified Attempt parameters uses the Keyword Overview-local
  `validate_paid_http_parameters`, and exact body recomputation uses
  `paid_request_body_bytes`. Equality is required across recomputed bytes, the committed
  Attempt bundle `request.body`, and closure-owned issued bytes. Do not use Target Metrics
  or Historical validators/constructors.
- Object-pool tamper and Attempt-bundle body tamper are separate adversaries. The pool case
  overwrites `EvidenceStore.object_path(<request-body-sha256>)` while proving the Attempt
  bundle `request.body` remains original and inode-distinct from the pool object; exchange
  must reach exactly zero HTTP handler calls.
- The bundle case overwrites only the committed Attempt bundle
  `attempt_path(...)/request.body`; exchange must reach exactly zero HTTP handler calls.
- Capability-attribute `object.__setattr__` mutation does not count as committed-Evidence
  tamper. The Evidence tests must mutate the actual committed pool/bundle paths consumed by
  verify-on-read, not monkeypatch a reader or alter an irrelevant copy.
- Do not add Target Metrics/Historical-only transport kwargs or seams, including an optional
  `max_response_body_bytes` exchange argument. Keyword Overview's existing body-ceiling
  boundary remains unchanged.

## Expected changed-path allowlist

Implementation is expected to change only:

- `src/observatory/dataforseo_paid_probe.py`;
- `tests/test_dataforseo_paid_probe.py`; and
- this ticket for [GROK]'s permitted Start commit, Status=`review`, and Implementation report.

If implementation requires another production or test path, stop and report the exact need
before widening the ticket.

## Required pre-implementation review

Before this ticket can be finally accepted/committed for implementation, [GROK] must perform
the required read-only adversarial ticket review against current authority and code.

The review must specifically challenge:

- whether the ticket accurately implements every F13 Keyword Overview requirement and no
  unrelated requirement;
- whether closure-owned consumption is placed early enough to prevent retry after failed
  pre-send verification;
- whether committed-Evidence revalidation proves both manifest/object integrity and exact
  `request.body` authority;
- whether proposed tests can false-green by mutating a path the send logic no longer reads
  while failing to tamper authoritative Evidence;
- whether recomputation uses the accepted closed Keyword Overview validator/body constructor
  without changing published bytes;
- whether any criterion accidentally changes one-Attempt-per-root, Capture, credential,
  PF-09, or inspect semantics;
- whether the expected two code/test paths are sufficient; and
- whether Target Metrics/Historical provide a valid pattern without importing their
  surface-specific behavior.

Return `READY`, `READY_AFTER_TICKET_RECONCILIATION`, or `NOT_READY`. Do not edit anything.

Review result: `READY_AFTER_TICKET_RECONCILIATION`. Steward reconciliation accepted the
review's three blocking clarifications: authoritative pool-vs-bundle Evidence tamper proofs,
explicit failed-verification replay consumption, and KO-local validator/body recomputation.
The final locks are recorded in `Final reconciled F13 proof locks` above.

## Required implementation report

If and only if the Steward later accepts and commits this ticket and issues an exact start
commit, implementation must report loaded project-local skill paths; exact parent/child
commits; exact changed paths; acceptance criterion → proving-test map; closure-owned
issuance/consumption mechanism; exact immediate pre-send Evidence revalidation sequence;
each body/document/used-reset/replay/Evidence-tamper adversary and observed HTTP request
count; confirmation that production JCS bytes and existing identities are unchanged;
targeted test/Ruff/mypy results; strongest/weakest proof, possible false greens, remaining
caller influence, and exact unproven limits; and confirmation of zero provider/API-host/DNS
calls, zero real credentials, zero live Evidence, and zero spend.

Use only appropriate project-local skills and report each absolute `SKILL.md` path used.

## Hard boundaries

- The read-only review is complete and reconciled. Implementation begins only from the exact
  final ticket commit explicitly issued by the Steward as the start commit; the ticket-only
  finalization commit itself performs no provider activity.
- [GROK] is the only writer of `src/` and `tests/`; [GPT] owns this ticket and other
  authority files except the implementer's permitted ticket fields/report after an exact
  implementation start is issued.
- Do not commit, amend, or push during the read-only review.
- Do not invoke DataForSEO, DNS, provider credentials, sandbox, or any public network.
- Do not run the public paid capture CLI or create live provider Evidence.
- Do not change the Keyword Overview provider request, location/language, keyword arity,
  `include_serp_info`, `include_clickstream_data`, spend ceiling, timeout, body ceiling,
  endpoint, policy, adapter token, published event bytes, one-Attempt-per-root rule, Capture
  semantics, or inspect semantics.
- Do not edit Google Organic, Search Mentions, sandbox, Target Metrics, Historical, shared
  HTTP transport, Evidence Store, parser, Derivation, Recipe, migrations, API, or Strategy.
- Do not introduce a shared/generic capability framework.
- Do not perform F6 automation, F7 locking, F12 orchestration, activation, pricing review,
  panel execution, Ranked Keywords, Related Keywords, or another provider surface.

## Next boundary

After [GROK]'s read-only ticket review, [CHAZ] relays the findings to [GPT]. [GPT] reconciles
them, makes any required ticket-only changes, commits the final accepted PF-16 ticket, and
only then issues an exact implementation start commit.

After PF-16 implementation is independently reviewed and closed, Google Organic receives
its own separately bounded F13 remediation ticket before any intended live panel invokes
that gate. Search Mentions remains separately gated by F13 if it is later reused.

## Implementation report

**Parent:** `14037adf252085625b1e7fe5d159951cf81a8ea1`  
**Child:** this implementation commit  
**Status:** `review`  
**PF-16 only:** yes. Nothing pushed. No amend.

Loaded skills:

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

### Changed paths

- `src/observatory/dataforseo_paid_probe.py`
- `tests/test_dataforseo_paid_probe.py`
- this ticket (Start commit, Status=`review`, Implementation report)

No other path.

### Closure-owned issuance / consumption

Keyword Overview `_build_transport_gate` now keeps a KO-local `_Issuance` list. Each genuine
issue binds:

- issued capability identity (`record.capability is attempt`)
- concrete `EvidenceStore`
- `attempt_id`
- canonical committed Attempt preimage
- exact committed request-body bytes
- `consumed`

Visible `attempt_id` / `document` / `request_body` / `_used` remain mirrors. They do not
authorize transport or replay.

After issued-capability identity/issuance lookup succeeds, `_exchange` sets
`record.consumed = True` and mirrors `_used = True` before visible-field comparison,
committed-Evidence revalidation, credentials, URL resolution, or
`perform_bounded_http_exchange`.

### Exact pre-send verification sequence

1. `type(attempt) is _VerifiedAttempt` and issuance lookup by identity
2. refuse if `record.consumed`; else consume
3. compare visible `attempt_id`, document JCS preimage, and `request_body` to the closure record
4. re-read committed Attempt by closure-owned `attempt_id`
5. `verify_attempt_directory` on the committed Attempt path
6. require canonical preimage and content-digest identity
7. read exact Attempt-bundle `request.body`
8. `validate_paid_http_parameters` on verified Attempt parameters
9. recompute with `paid_request_body_bytes`
10. require equality among recomputed bytes, committed bundle `request.body`, and
    closure-owned bytes
11. `_require_paid_target` on the verified Attempt
12. send only `bytes(record.request_body)` through the existing PF-09 seam

No Target Metrics / Historical validator or constructor. No
`max_response_body_bytes` exchange argument. No shared capability framework.

### Acceptance criterion → proving test

| Criterion | Test |
|---|---|
| Closure-owned issuance binds identity, store, attempt_id, preimage, bytes, consumed | gate in `_build_transport_gate`; exercised by every issued-capability test below |
| Replay uses closure-owned consumed, not visible `_used` | `test_closure_owned_replay_protection_ignores_used_attribute` |
| Consume before verify/send-capable work; failed verify cannot retry | `test_failed_pre_send_verification_consumes_issuance` |
| Immediate pre-send visible-field + committed Evidence + KO-local recompute | `test_pre_send_verifies_committed_attempt_and_request_body` plus `_revalidate_committed` |
| `object.__setattr__` `request_body` replacement cannot transport | `test_issued_request_body_replacement_cannot_transport` |
| `object.__setattr__` document replacement cannot transport | `test_issued_document_replacement_cannot_transport` |
| Successful exchange then `_used=False` cannot replay | `test_closure_owned_replay_protection_ignores_used_attribute` |
| Object-pool tamper, inode-distinct, bundle body unchanged, zero HTTP | `test_pre_send_verifies_committed_attempt_and_request_body` (pool case) |
| Bundle `request.body` tamper independently zero HTTP | `test_pre_send_verifies_committed_attempt_and_request_body` (bundle case) |
| Existing forged/unissued/subclass/one-shot/credential/transport tests remain | `tests/test_dataforseo_paid_probe.py` (113 passed) |
| Published request bytes and Attempt/Capture identities unchanged | `test_published_paid_request_vector_remains_byte_identical`, `test_independent_paid_vector_bytes_and_ids`, `test_mock_sent_headers_and_body_equation` |

### Adversary results / HTTP request counts

- Body replacement: `StoreError`; handler calls `[]` (0 HTTP).
- Document replacement: `StoreError`; handler calls `[]` (0 HTTP).
- Successful mock exchange then `object.__setattr__(_used, False)`: first
  `response_complete` with exactly `[PAID_REQUEST_BODY]`; second `StoreError` matching
  `one-exchange`; observed request count remains 1.
- Object-pool tamper: overwrite `EvidenceStore.object_path(<request-body-sha256>)` after
  proving pool and bundle `request.body` are inode-distinct and the bundle body is still
  `PAID_REQUEST_BODY`; `_exchange` raises `StoreError`; handler calls `[]`.
- Bundle tamper: overwrite only `attempt_path(...)/request.body`; `_exchange` raises
  `StoreError`; handler calls `[]`.
- Failed pre-send verification then second `_exchange` on the same capability, including
  `_used=False` reset: first `StoreError`, second `one-exchange`; handler calls remain `[]`.

### Unchanged published bytes

`paid_request_body_bytes` / `closed_paid_parameters` / `validate_paid_http_parameters` are
the existing KO-local constructors. Independent vector still:

- request body 216 bytes, SHA-256 `3fc7205a55a1a5c464c0ae4ebca21a1e3088c2022565929a670fdf757ab7987b`
- fingerprint `6cc5765911abe752a974d2fba268d927fdc055147c1286fffdfe0ee585cdc610`
- Attempt ID `89904bf8a6812fb3d0d845310e4705962bb4db928b80da3be67342dff5def185`
- Capture ID `dbaaf68a38e54e39d4fc03807d72eda37f8efd9a212220c0a99d270ddcec6917`

Mock send still posts exactly `PAID_REQUEST_BODY`. Production path, 1..5 keywords, US/en,
`include_serp_info=false`, `include_clickstream_data=false`, authorization ceiling 20000,
timeout, 8 MiB response-body ceiling, loopback-only test endpoint, credential behavior,
one-Attempt-per-root, Capture/inspect semantics, and PF-09 one-POST seam are unchanged.

### Checks

- `uv run pytest -q tests/test_dataforseo_paid_probe.py` → 113 passed
- `uv run ruff check .` → All checks passed
- `uv run mypy src/observatory/dataforseo_paid_probe.py tests/test_dataforseo_paid_probe.py`
  → Success: no issues found in 2 source files
- `uv run mypy` (repo-wide) is already red at start commit `14037adf` with 10 errors in
  `tests/test_api_target_metrics.py`, `tests/test_api_llm_mentions_historical.py`, and
  `tests/test_dataforseo_ai_optimization_llm_mentions_historical_paid_probe.py`. PF-16 did
  not add or change those files; fixing them is outside the allowlist.

Full-suite pytest was not run; reserved for Steward/CHAZ review.

### Strongest proof

Failed committed-Evidence revalidation consumes issuance: after an inode-distinct object-pool
overwrite, the first `_exchange` fails with zero HTTP, resetting visible `_used` to `False`
cannot authorize a second `_exchange`, and the handler count remains zero. That is the F13
consume-before-verify lock plus Evidence-path proof, not capability-attribute comparison.

### Weakest proof / possible false greens

- Body/document replacement tests assert `StoreError` without matching the issuance-mismatch
  text; `calls == []` still proves zero HTTP.
- Object-pool mismatch is typically raised by `read_attempt` verify-on-read (which already
  checks the pool object). The later `verify_attempt_directory` line is therefore not
  independently observed on that path. The separate bundle-`request.body` adversary still
  proves the bundle-body/verify-directory path.
- Ordinary tests do not prove Evidence Store crash/fsync/commit, Attempt-authorization
  concurrency, or recovery.
- Same-process mutation of the closure `_Issuance` list itself is not a capability-attribute
  adversary and is unproven.

### Remaining caller influence and unproven limits

Caller-visible capability fields can no longer authorize transport or replay. Remaining
influence is the existing private `_issue_verified_attempt` / `_exchange` test seams and
the process-local issuance list, which is not a public API. This ticket does not authorize
live Keyword Overview invocation, spend, F12, Google Organic/Search Mentions F13, or a
shared capability framework.

### Network / provider boundary

Zero DataForSEO calls, zero sandbox calls, zero provider DNS/network activity, zero real
credentials, zero live Evidence, zero spend. Tests use sentinel credentials, `httpx` mock
transport, and the existing loopback-only override. The public paid capture CLI was not
run against provider credentials. Nothing was pushed.
