# AI-14 — LLM Mentions Historical Live one-shot Evidence activation

**Status:** provisional  
**Owner:** [CHAZ] operator / [GPT] Steward verification  
**Blocked by:** mandatory read-only GROK ticket review and final Steward reconciliation  
**Product direction:** [CHAZ] selected Historical as the next active workstream and approved reuse of the accepted manual F6 protection path on 2026-08-25  
**Draft base:** `c6fcd7ae496a86c8a58b0dcdfc7bd3757c7ca71b`

## Purpose

Exercise the closed AI-13 Historical Live adapter exactly once, preserve the resulting
Attempt/Capture as immutable Evidence, inspect what DataForSEO actually returned, and prove
the bounded encrypted off-host snapshot/fresh-restore path before treating the paid Evidence
as safely protected.

This is an operator activation ticket. It adds no transport code, parser, Conformance
fixture, Recipe, Outcome, Observation, schema, Derivation, selection, API, scheduling, or
backup framework. The accepted AI-13 adapter and AI-09-style manual F6 procedure are reused
as-is unless review finds a concrete incompatibility. Do not refactor working transport or
backup machinery merely because this surface is new.

This provisional ticket does not authorize provider transport or spend. After GROK's
read-only review, GPT must reconcile and commit the final ticket. CHAZ must then separately
authorize the exact one-shot command at the final clean synchronized HEAD.

## Accepted foundation and Product locks

- AI-13 closed the Evidence-only adapter
  `dataforseo-ai-optimization-llm-mentions-historical-live-paid-probe-v1`.
- Frozen request: keyword `generative engine optimization`; provider window
  `2025-08-01` through `2026-07-31`; platform `google`; United States
  `location_code=2840`; English `language_code=en`; one included keyword target with
  `search_scope=["answer"]` and `match_type="word_match"`.
- Public authorization acknowledgement remains exactly `200000` micro-USD. It is a
  fail-closed operator ceiling, not expected cost or a provider billing guarantee.
- Exactly one process invocation and at most one POST are permitted after separate CHAZ
  authorization. Any invocation consumes that authorization regardless of exit code.
- Retry, replacement Evidence root, continuation, polling, follow-up, second exchange, or
  changed keyword/date/platform/location/language/target are forbidden.
- Historical is not activated by AI-13. No live Historical Evidence currently exists.
- CHAZ approved reuse of the already accepted bounded manual F6 path rather than building
  R2 automation, a new backup service, or Historical-specific protection code first.
- F12 recurring acquisition remains deferred. This ticket creates no cadence, panel,
  monitoring state, coordinated recapture, or strategy state.
- F13 does not block this Historical gate. Do not modify or reuse an older F13-affected
  sandbox, Keyword Overview, Google Organic, or Search Mentions transport gate here.

## Fresh claimed-contract and pricing check — 2026-08-25

The Steward rechecked the current official Historical Live documentation and LLM Mentions
pricing while drafting this ticket.

Current claimed contract still states:

- Live `POST /v3/ai_optimization/llm_mentions/historical/live`;
- one task per Live call;
- month-by-month Historical metrics for the requested target;
- each month carries `mentions` and `ai_search_volume` testimony;
- results are scoped by selected platform, location, and language;
- Historical data is available from `2025-08-01`.

Current published LLM Mentions pricing still states `$0.10` per request plus `$0.001` per
row. The Historical billing-row grain remains empirical/provider-billing uncertainty rather
than a Recipe fact. Official documentation and pricing are mutable claimed contract, not
Evidence. Recheck both again immediately before final one-shot authorization if the live
operation does not occur in the same work session.

## Why activation comes before parser or Recipe

D12 requires claimed contract, Evidence, and Derivation Recipe to remain distinct. AI-13
records unresolved empirical questions including returned month topology, zero versus
omitted/empty states, ordering, undocumented fields, date-window behavior, and billing-row
grain. Synthetic transport tests prove Observatory's closed request and Evidence boundary;
they do not prove the provider's payload semantics.

The next semantic work must therefore start from verified live Evidence. Do not design the
Historical parser, identities, completeness rules, or typed schema from documentation alone.

## Mandatory GROK read-only review

Before this ticket becomes final, GROK must inspect current authority, AI-13 code/tests,
AI-09 activation precedent, current Evidence/F6 tooling, and this ticket without mutation.
The review must challenge:

- whether AI-13 is truly ready for one bounded invocation without code changes;
- whether any AI-09 F6 step is incompatible with the current VPS Evidence layout;
- exact one-shot, spend, no-retry, and fresh-root gates;
- required preflight and post-capture evidence;
- hidden F6/F12/F13, credential, retention, or multi-exchange blockers;
- whether any requested ticket behavior accidentally authorizes parser/Recipe/API work;
- any Product question that remains genuinely unresolved.

Return READY, RECONCILE, or NOT_READY. Do not edit files, call the provider, access
credentials, mutate Evidence/PostgreSQL, or run network-dependent tests.

## Final-ticket operator record required

The reconciled final ticket must freeze before CHAZ authorization:

- exact clean synchronized implementation/activation HEAD;
- exact fresh Evidence root;
- exact provider command using only the closed AI-13 CLI arguments;
- exact `200000` micro-USD acknowledgement;
- current official contract/pricing recheck evidence;
- exact preflight commands and hard-stop conditions;
- exact local inspect/status/scrub sequence;
- exact source inventory format;
- exact encrypted restic snapshot command/remote/tagging;
- exact fresh restore path, scrub, committed Attempt/Capture set equality, and restored-body
  byte/hash comparison;
- explicit statement that no retry or replacement root is authorized.

## Required preflight boundary

Before the paid command, the operator must prove at minimum:

- VPS canonical worktree, branch `main`, exact authorized HEAD, clean tree, and synchronized
  `origin/main`;
- the exact Evidence root does not already exist;
- no competing Observatory capture, pytest, restic, rclone, or writer process is active;
- no leftover bounded-test container relevant to the accepted operator checks;
- required DataForSEO credential environment and accepted restic/rclone configuration exist
  without printing secrets;
- the command contains no endpoint, body, timeout, response-ceiling, keyword/date/platform/
  location/language/target override, retry, continuation, or alternate spend seam.

A failed preflight consumes no authorization because the paid command has not begun.

## Immediate post-capture gate

After the single invocation, record UTC start/end, exit code, exact HEAD/tree before and
after, and any emitted Attempt/Capture IDs. Never run the paid command again under this
authorization.

If a complete Capture exists, use the AI-13 byte-exact inspect command against the local
Evidence root and record byte count plus SHA-256 outside the Evidence root. Run Evidence
status and scrub on the exact source root. Any non-complete Capture, inspect refusal,
credential-echo refusal, scrub failure, provider error, unexpected transport condition, or
other abnormal result is a hard stop and does not authorize a retry.

## Bounded F6 protection

Reuse the accepted manual protection spine proven by earlier paid activations:

1. quiesce the exact source root;
2. record sorted exact committed Attempt and Capture ID sets outside the root;
3. snapshot the complete root plus inventory into the accepted encrypted restic repository
   through the existing approved rclone remote using a Historical/AI-14-specific tag;
4. record the exact snapshot ID and non-secret receipt;
5. restore into a fresh local directory;
6. open and scrub the restored store;
7. independently recompute committed Attempt/Capture sets and require exact equality;
8. inspect the restored Capture and require exact byte count and SHA-256 equality with the
   source inspection;
9. preserve the accepted non-secret backup/restore proof receipts.

Do not build new backup automation in AI-14. Routine F6 automation remains separately
deferred.

## Payload assessment after protection

Only after local and restored Evidence verify, assess the real Historical response for:

- top-level/task status, provider task ID, reported cost, execution timing, and exact request
  echo agreement;
- exact result key set, `items_count`, item count, and all null/absence distinctions;
- every returned `(year, month, mentions, ai_search_volume)` tuple;
- returned period coverage versus the frozen requested window;
- zero values, missing months, duplicates, ordering, unknown fields, and count conflicts;
- actual provider behavior relevant to a later strict parser and Recipe;
- whether the exact body is suitable as a primary Conformance fixture and which invariants
  still require synthetic adversarial proof.

This assessment does not define Observation identity or PostgreSQL design.

## Acceptance / stop point

AI-14 closes only when the one-shot operation, local Evidence verification, bounded off-host
snapshot, fresh restore, exact set equality, restored-body equality, and candid payload
assessment are recorded and accepted by the Steward. If the provider operation does not
produce acceptable complete Evidence, close or reconcile the operator result honestly; do
not retry automatically.

If accepted Evidence exists, the anticipated next boundaries are: strict Historical parser
and Conformance fixture; then Recipe-addressed typed Derivation/persistence; then a
Recipe-selected admitted-history API. Those are separate future tickets and may change
after the real body is inspected.
