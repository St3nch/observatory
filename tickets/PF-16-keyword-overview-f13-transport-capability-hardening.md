# PF-16 — Keyword Overview F13 transport-capability hardening

**Status:** provisional — read-only pre-implementation review required  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none; F13 trigger is fired for the next Keyword Overview gate reuse  
**Approved by:** [CHAZ] for provisional ticket review only  
**Start commit:** not assigned — implementation is not authorized

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
- [ ] Targeted tests pass, then `uv run ruff check .` and `uv run mypy` pass. Full-suite
      verification is reserved for the Steward review boundary under `AGENTS.md`.
- [ ] Ordinary tests perform zero DataForSEO/API-host/DNS/public-network activity, use no
      real credentials, create no live provider Evidence, and spend no credits.

### Final reconciled F13 proof locks

These locks are mandatory and narrow the looser acceptance bullets above where needed:

- After issued-capability identity/issuance lookup succeeds, closure-owned consumption is
  set before visible-field comparison, committed-Evidence revalidation, or
  `perform_bounded_http_exchange`. Visible `_used` may mirror state but is not authority.
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
