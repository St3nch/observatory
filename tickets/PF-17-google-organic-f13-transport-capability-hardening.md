# PF-17 - Google Organic F13 transport-capability hardening

**Status:** provisional-review
**Owner:** [CLAUDE] implementation / [GPT] Steward review
**Blocked by:** none after final Steward reconciliation; implementation starts only from the exact final ticket commit issued by the Steward
**Approved by:** [CHAZ] for bounded Organic F13 preparation; [CLAUDE] designated Writer
**Start commit:** pending final Steward acceptance

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
