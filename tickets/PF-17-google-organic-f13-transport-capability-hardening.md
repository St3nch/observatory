# PF-17 - Google Organic F13 transport-capability hardening

**Status:** done
**Owner:** [CLAUDE] implementation / [GPT] Steward review
**Blocked by:** none
**Approved by:** [CHAZ] for bounded Organic F13 preparation; [CLAUDE] designated Writer
**Start commit:** 3aaef614af807b7697541a46bf3687e634243f1d

## Purpose

Final Steward reconciliation: **ACCEPTED** after the required read-only ticket review
returned `READY_AFTER_TICKET_RECONCILIATION`. The proof and scope locks from that review
are incorporated below. This acceptance authorizes implementation only from the exact final
ticket commit issued by the Steward; the implementer records that commit as `Start commit`,
sets `Status=review`, and records the Implementation report in the implementation commit.

Harden only the existing DataForSEO Google Organic Live Advanced paid-probe transport
capability boundary required by deferred item F13 before Organic is reused.

PF-16 is closed and names Organic as the next separately bounded F13 remediation.
This does not override F13's Search Mentions clause; Search Mentions remains separately
F13-gated if later reused.

No provider call, spend, panel execution, activation, parser, Recipe, Derivation,
Observation, PostgreSQL, API, or Strategy work is authorized.

## Reconciled audit facts

At baseline, `_exchange` uses caller-visible `_VerifiedAttempt` state as authority:
issued identity -> visible `_used` replay check -> credentials -> endpoint -> visible
`_used=True` -> visible `document` target check -> authorization header -> Organic
response ceiling -> PF-09 with `bytes(attempt.request_body)`.

There is no closure-owned issuance record, no closure-owned consumed bit, no immediate
committed-Attempt reread, and no committed `request.body` recomputation before send.

Current private-seam consequences include:
- replacing visible `request_body` can change POST bytes;
- resetting visible `_used=False` can authorize replay;
- replacing visible `document` with a different valid Organic document can reach transport;
- document-only replacement can send the original body but later parent Capture from the
  replaced visible document;
- committed object-pool or bundle `request.body` tamper after issue is not reread pre-send;
- replacing visible `attempt_id` does not affect transport or inspect, but can desync the
  returned Outcome `attempt_id`.

## Organic contract that must remain unchanged

- module: `src/observatory/dataforseo_google_organic_paid_probe.py`
- path: `/v3/serp/google/organic/live/advanced`
- authorization ceiling: 30000 micro-USD
- one keyword; depth=100; desktop/windows; en; location_code=2840
- `group_organic_results=true`; `load_async_ai_overview=true`
- timeout: connect 30 / read 120 / write 30 / pool 30 seconds
- response ceiling: 33,554,432 bytes (32 MiB)
- existing internal `max_response_body_bytes` test seam
- Organic-only one-shot rule and exact loopback-path restriction
- existing credentials, Capture, inspect, CLI/public function, and PF-09 behavior

Published Organic vector remains byte-identical:
- request body length: 179 bytes
- body SHA-256: `0ea1022be28baf54e8a68f49002c963ada85f78082dec843030db28458498e2b`
- fingerprint: `9ab79d6031d2a82a9aec4d9c6c5399bd540fcbbea80fca8a0216911333cedb02`
- Attempt: `b577bc1fb75f4ba7576a96c1328fbe74df9d975f3bd03f6c01d7441dfed1a1be`
- sample complete Capture conformance vector: `ab94c98e528e776317c459a2dc2f8010b33b8ce142bab52d4e699fb5599d41c4`

## Required behavior

1. Add an Organic-local closure-owned issuance record binding capability identity,
   concrete EvidenceStore, committed attempt_id, canonical committed Attempt preimage,
   exact committed request bytes, and consumed state.
2. Replay prevention uses closure-owned consumed state; visible `_used` is mirror only.
3. Preserve current/PF-16-corrected ordering: after issuance lookup and replay refusal,
   credentials and endpoint validation run before consumption. Their failure leaves the
   issuance reusable.
4. After credential/endpoint validation, consume before visible-field comparison,
   committed-Evidence revalidation, authorization-header construction, or PF-09 send.
5. Visible attempt_id/document/body must match closure state before revalidation.
6. Immediately pre-send, reread the exact Attempt by closure attempt_id, integrity-verify
   it and its directory, verify canonical preimage/content identity, read bundle
   `request.body`, validate with Organic-specific `validate_organic_http_parameters`,
   recompute with Organic-local `organic_request_body_bytes`, and require equality across
   recomputed, committed, and closure-owned bytes. Re-run `_require_organic_target`.
7. Construct the existing authorization header and send only closure-owned bytes through
   the unchanged PF-09 seam with Organic HTTP_HEADERS, timeout, 32 MiB default,
   `max_response_body_bytes`, and client seam.
8. No shared/generic capability framework and no foreign adapter validators/constructors.

### Final reconciled scope locks

- PF-17 closes the **pre-send transport-authority window** only. Post-exchange mutation of
  visible capability fields before Capture commit / Outcome construction remains unchanged
  and outside this ticket, at PF-16 parity; do not widen PF-17 to change Capture or Outcome
  behavior.
- Preserve existing externally asserted error-message substrings `verified committed Attempt`
  for forged/unissued capability refusal and `one-exchange` for replay refusal.
- The required document-only adversary proves pre-send refusal by asserting exactly zero
  HTTP handler calls. It does not require constructing a second committed Attempt or proving
  downstream mis-parented Capture behavior.

## Required proofs

All new tests stay in `tests/test_dataforseo_google_organic_paid_probe.py`, use sentinel
credentials and mock/loopback transport, and assert zero handler calls on pre-send refusal.

Prove separately:
- valid-Organic request-body replacement;
- valid-Organic document-only replacement with original body retained;
- valid-Organic document plus matching-body replacement;
- `_used=False` reset after one success cannot replay;
- object-pool tamper with inode-distinct / bundle-unchanged proof;
- independent bundle `request.body` tamper;
- failed committed-Evidence verification consumes issuance and cannot replay;
- endpoint-validation failure after issue leaves issuance reusable;
- credential-validation failure after issue leaves issuance reusable.

Do not false-green with KO/sandbox/invalid-Organic replacements that today's gate already
rejects for unrelated reasons.

## Changed-path allowlist

Implementation may change only:
- `src/observatory/dataforseo_google_organic_paid_probe.py`
- `tests/test_dataforseo_google_organic_paid_probe.py`
- this ticket for implementer Start commit, Status=`review`, and Implementation report

If another path is required, stop and report before widening.

Do not change PF-09, Evidence Store, capture-event constructors, KO, sandbox,
Search Mentions, Target Metrics, Historical, Organic parser/derive/read, migrations,
PostgreSQL, API, Recipe, settings/credentials, authority docs, or Strategy.

## Validation boundary

Implementer runs targeted Organic tests, Ruff, touched-path mypy, and reports repo-wide
mypy relative to the final start baseline. Final full-suite `uv run pytest -q` is [CHAZ]-run.
Ordinary tests use zero provider/API-host/DNS activity, zero real credentials, zero live
provider Evidence, and zero spend.

## Required ticket review

Completed by the designated [CLAUDE] implementer at provisional ticket commit
`5582628f47fb6c4fe66d989a63b25702ebd30e0c`. Verdict:
`READY_AFTER_TICKET_RECONCILIATION`. The Steward independently checked and accepted the
material findings now incorporated into this ticket.

## Hard boundaries

Implementation begins only from the exact final accepted ticket commit issued by [GPT]. No push is authorized.
[CLAUDE] is the designated writer of `src/` and `tests/` for PF-17; [GPT] owns this ticket
except permitted implementer Start/Status/report fields. The implementer sets Status=`review`, never `done`.

## Next boundary

Commit this final accepted ticket and issue that exact commit as the implementation start
commit. Only then may the designated [CLAUDE] implementer modify the allowlisted code/tests.

## Implementation report

**Start commit:** `3aaef614af807b7697541a46bf3687e634243f1d`
**Writer:** [CLAUDE] (designated under `AGENTS.md` §Agent lanes)

### Validation

- `uv run pytest tests/test_dataforseo_google_organic_paid_probe.py -q` — **43 passed**
  (9 new PF-17 proofs, 34 pre-existing).
- Sibling suites importing the Organic gate, run to protect the changed-path boundary:
  `search_mentions_paid_probe`, `target_metrics_paid_probe`,
  `llm_mentions_historical_paid_probe`, `google_organic_derive`, `api_google_organic`,
  `dataforseo_paid_probe`, `dataforseo_sandbox` — **386 passed**.
- `uv run ruff check .` — **All checks passed**.
- Touched-path `uv run mypy src/observatory/dataforseo_google_organic_paid_probe.py
  tests/test_dataforseo_google_organic_paid_probe.py` — **Success, no issues**.
- Repo-wide `uv run mypy` — **14 errors in 5 files (80 checked)**, an error set byte-identical
  to the same command at start commit `3aaef61`. No error is in a PF-17 touched path; the
  baseline errors are the known `tools/` module-search omission and pre-existing
  Target Metrics / Historical API test typing.
- Full-suite `uv run pytest -q` deliberately **not** run; final full-suite validation is
  [CHAZ]-run per the Validation boundary.
- Zero DataForSEO/provider calls, zero API-host/DNS/public-network activity, zero real
  credentials, zero live provider Evidence, zero spend. Tests use sentinel credentials,
  `httpx.MockTransport`, `tmp_path` stores, and the file's autouse `_no_public_network`
  guard. The session PostgreSQL substrate from `tests/conftest.py` is ordinary local test
  infrastructure and was not used by any PF-17 proof.

### Strongest part

Transport authority is now closure-owned end to end. `_Issuance` binds capability identity,
concrete `EvidenceStore`, `attempt_id`, canonical committed preimage, exact committed bytes,
and a `consumed` flag that no caller can reach — not even through `object.__setattr__`, which
is the exact private seam F13 named. The pre-send revalidation is genuinely independent of
the capability: it re-reads the Attempt by closure identity, verifies the exact bundle
directory, reads committed `request.body`, revalidates the closed Organic parameter contract,
recomputes the request bytes with the Organic constructor, and requires three-way equality
across recomputed, committed, and issued bytes before `_require_organic_target` re-runs.
Only closure-owned bytes reach the unchanged PF-09 seam.

### Weakest / most fragile part

`_issuance_for` is a linear scan over a closure list that never shrinks; an issuance record
(including its 179-byte committed body and preimage) lives for the life of the process. That
is correct and bounded for a one-shot adapter but would need revisiting if a gate ever issued
many capabilities. Second: `_require_visible_fields_match` compares the *visible* document by
re-canonicalizing it, so it depends on `canonical_json` raising `DocumentError` rather than
silently coercing an exotic substitute; that behavior is verified but is a coupling to
canonicalization strictness rather than to a type check.

### Possible false greens

- The nine proofs assert the **specific** guard message (`closure-owned issuance record`,
  `verify-on-read`, `one-exchange`) rather than bare `StoreError`, so a refusal from an
  unrelated pre-existing gate would not satisfy them. Every adversary is a *valid* Organic
  document/body built from `closed_organic_parameters(keyword="website comparison")`, not a
  KO/sandbox/malformed input.
- Honest disclosure: the endpoint- and credential-reusability proofs **already passed against
  the unhardened gate** at start commit, because the current ordering was already correct.
  They are regression locks on PF-16-corrected ordering, not evidence of new behavior. The
  other seven failed before this change and pass after.
- `_replacement_organic_document()` reuses the issued nonce/`authorized_at`, so it differs
  only in keyword. That is sufficient (distinct preimage and `attempt_id`) but a future
  reader should not read it as proving nonce-level discrimination.
- Mock transport does not prove real httpx wire behavior; PF-09 is unchanged and separately
  covered.

### Remaining caller influence

A same-process caller can still replace visible `attempt_id`, `document`, `request_body`, and
`_used` via `object.__setattr__` — they remain mirrors. They can no longer influence what is
sent, whether a replay is permitted, or whether Evidence revalidation passes. Per the ticket's
reconciled scope lock, mutation of those mirrors **after** `_exchange` returns still reaches
`_commit_organic_capture` and the returned Outcome; that window is unchanged, at PF-16 parity,
and deliberately out of PF-17.

### Architecture drift / coupling

No generic or shared capability framework was introduced. `_Issuance`,
`_require_visible_fields_match`, and `_revalidate_committed` are private to the Organic
closure. No foreign adapter validator or constructor is used: revalidation calls
`validate_organic_http_parameters` and `organic_request_body_bytes` only. PF-09, the Evidence
Store, capture-event constructors, and every sibling adapter are untouched. The structure
intentionally parallels PF-16 by convergent design, not by shared code.

### Evidence / provider traps

- Pool tamper and independent bundle `request.body` tamper are *different* failures and are
  proven separately; the pool proof asserts inode-distinctness and that the bundle body is
  unchanged, which depends on the store's forbidden-hardlink invariant.
- Revalidation failure consumes the issuance before it can fail, so a tampered store yields a
  refused, non-replayable capability rather than a retry loop — proven explicitly.
- The published Organic vector is unchanged: 179 bytes, body SHA-256
  `0ea1022b…98e2b`, fingerprint `9ab79d60…cedb02`, Attempt `b577bc1f…d1a1be`, and the sample
  conformance Capture `ab94c98e…9d41c4`.

### Closure blockers

None known within PF-17's scope. Closure needs [CHAZ] full-suite validation and [GPT] review
of this committed diff.

### Deferred / out of scope

- Post-exchange mirror mutation before Capture commit / Outcome construction (scope-locked
  above; same window exists in PF-16's Keyword Overview gate).
- F13 remains unfired for the sandbox, Search Mentions, Target Metrics, and Historical gates.
  This ticket hardens Organic only and authorizes no live invocation, spend, or reuse.

### What later provider gates should reuse conceptually

The shape, not the code: a closure-owned issuance record as sole transport authority;
visible attributes demoted to mirrors; credential and endpoint validation before consumption
so their failure leaves the issuance reusable; consumption before any Evidence read so a
verification failure cannot be retried; and pre-send re-read plus adapter-local recomputation
requiring three-way byte equality.

### What should deliberately remain provider-local

The Organic parameter validator and body constructor, the 30000 micro-USD ceiling, the
32 MiB response ceiling and `max_response_body_bytes` seam, the one-shot adapter-contract
rule, the loopback path restriction, and the error-message texts. Each gate must keep its own
published bytes and closed contract independently reviewable; a shared abstraction here would
make one adapter's drift silently change another's authorized request.

## Steward closure

**Implementation commit:** `41b02ad50a8ed0d02e3554c17536e5749c2fe4b3`

[GPT] independently reviewed the exact single-child implementation diff from
`3aaef614af807b7697541a46bf3687e634243f1d` and confirmed that only the three allowlisted
paths changed, the reconciled PF-17 transport-authority ordering is implemented, PF-09 and
neighboring adapters remain untouched, and the required adversarial proofs are present.

[CHAZ] then ran the final authoritative repository-wide suite at the implementation commit:

- `uv run pytest -q` — **1522 passed, 1 skipped, 1 warning** in 474.60s;
- exit code `0`.

PF-17 is accepted and closed. This closure authorizes no provider call, spend, live
Evidence creation, or push.
