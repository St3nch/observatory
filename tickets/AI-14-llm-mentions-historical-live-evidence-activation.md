# AI-14 — LLM Mentions Historical Live one-shot Evidence activation

**Status:** provisional  
**Owner:** [CHAZ] operator / [GPT] Steward verification  
**Blocked by:** mandatory read-only GROK ticket review and final Steward reconciliation  
**Product direction:** [CHAZ] selected Historical as the next active workstream and approved reuse of the accepted manual F6 protection path on 2026-08-25  
**Draft base:** `c6fcd7ae496a86c8a58b0dcdfc7bd3757c7ca71b`

**Effective status after mandatory review:** accepted, awaiting final ticket push/synchronization and separate explicit [CHAZ] one-shot operator authorization.  
**Review result:** GROK `RECONCILE` at `e3f98cd12712a19d7714452f314777d70c48d1d5`; Steward reconciliation is recorded in the final section below and supersedes the provisional operator wording above.  

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

## Steward reconciliation — supersedes provisional operator details above

GROK completed the mandatory read-only review at
`e3f98cd12712a19d7714452f314777d70c48d1d5` and returned **RECONCILE**. GPT independently
verified the material findings against the closed AI-13 implementation, AI-09 activation
precedent, current authority, and the current official Historical Live claimed contract and
pricing. No Product question remains. This section is the final operator boundary and
supersedes any less-specific provisional wording above.

### Frozen operator record

- Evidence root:
  `$HOME/.local/share/observatory/ai14-historical-generative-engine-optimization-2026-08-25`;
- adapter:
  `dataforseo-ai-optimization-llm-mentions-historical-live-paid-probe-v1`;
- authorization acknowledgement: exact integer `200000` micro-USD;
- rclone remote: `vedaops-drive:`;
- restic password file: `$HOME/.config/restic/observatory-password`;
- snapshot tags: `observatory-evidence-store` and `f6-paid-ai14`;
- source inspect file: `/tmp/ai14-historical-response.body`;
- no retry, replacement Evidence root, continuation, polling, follow-up, or second provider
  exchange is authorized.

Exact capture command, valid only after a later durable [CHAZ] one-shot authorization record
is committed on clean synchronized `main`:

```bash
cd /home/chaz/projects/vedaops/observatory
uv run python -m observatory.dataforseo_ai_optimization_llm_mentions_historical_paid_probe capture \
  --evidence-root "$HOME/.local/share/observatory/ai14-historical-generative-engine-optimization-2026-08-25" \
  --authorize-max-micro-usd 200000
```

The public capture CLI has only those two caller arguments. The frozen keyword, dates,
platform, location, language, target, endpoint, timeout, and response ceiling remain inside
the closed AI-13 adapter.

Exact inspect template after a Capture ID exists:

```bash
uv run python -m observatory.dataforseo_ai_optimization_llm_mentions_historical_paid_probe inspect \
  --evidence-root "$HOME/.local/share/observatory/ai14-historical-generative-engine-optimization-2026-08-25" \
  --capture-id "<CAPTURE_ID>" \
  > /tmp/ai14-historical-response.body
wc -c /tmp/ai14-historical-response.body
sha256sum /tmp/ai14-historical-response.body
```

The inspect file is exact raw provider bytes. Do not pretty-print, normalize, edit, paste
unredacted unexpected prose/personal data into the ticket, or add the file to Git.

### Corrected activation semantics

- Capture CLI exit `0` means a Capture document was committed; it does **not** prove
  `response_complete`. Successful byte-exact inspect is the completeness witness because the
  inspector verifies the Capture is this adapter, HTTP event version 2,
  `transport_state=response_complete`, response completeness `complete`, and a nonempty body.
- `observatory.evidence status` proves the format-2 store opens; it does not report
  `transport_state` and is not a completeness witness.
- The CLI opens or creates the Evidence root before loading DataForSEO credentials. Therefore
  credential presence is a load-bearing preflight. If the capture process starts and exits
  for missing credentials, a FORMAT-only root may remain. The one-shot provider Attempt is
  not necessarily committed, but the human one-shot authorization is consumed; do not delete
  the root and retry without a new Steward/[CHAZ] decision.
- Do not interrupt a started process. The accepted adapter read timeout is 120 seconds;
  process death after Attempt commit can leave honest authorized/unresolved Evidence and still
  consumes the one-shot authorization.
- Provider error testimony is not permission to skip protection. If any paid Historical
  Attempt was committed, protect that Evidence through the bounded F6 path even when the
  Capture is partial/no-response, inspect refuses, or the complete body contains a provider
  error. Such a result may block fixture-quality activation closure, but it never authorizes
  another provider exchange.

### Exact preflight facts to prove before later authorization/run

Before the paid command: branch `main`; exact later authorized HEAD; clean tree; synchronized
`origin/main`; exact root absent; no competing pytest/capture/restic/rclone writer; no
`observatory-ce05-*` container; `observatory-postgres-1` does not need to be stopped; both
`OBSERVATORY_DATAFORSEO_LOGIN` and `OBSERVATORY_DATAFORSEO_PASSWORD` are nonempty in the same
shell that will execute capture without printing their values; the restic password file
exists; and local rclone configuration exposes exactly the accepted `vedaops-drive:` remote.
No caller-supplied endpoint, body, timeout, response ceiling, keyword/date/platform/location/
language/target option, retry, continuation, or alternate spend value is permitted.

A failed preflight before capture-process start consumes no authorization. First invocation
of the capture process consumes the later explicit one-shot authorization regardless of exit
code or transport/provider result.

### F6 reuse lock

Reuse the AI-09 manual procedure, not new code: quiesce; write sorted exact committed Attempt
and Capture ID sets to an inventory outside the source root and hash that inventory; snapshot
the complete root plus inventory into the accepted encrypted restic repository via
`vedaops-drive:` with tags `observatory-evidence-store` and `f6-paid-ai14`; record the
snapshot ID and non-secret receipt; restore into a fresh local directory; open and scrub the
restore; independently recompute committed ID sets and require exact equality; when a
complete body exists, inspect the restored Capture and require byte count and SHA-256 equality
with the raw source inspect file; preserve the accepted non-secret receipt/restore-proof
artifacts and verify uploaded bytes. Exact snapshot/restore command lines are issued only
after live IDs exist, as in AI-09; an unknown future snapshot ID cannot be frozen in advance.

Routine R2/F6 automation, parser, Conformance fixture promotion, Recipe, schema, Derivation,
API, Outcomes/Holdings, F12 orchestration, F13 hardening of older gates, and any other LLM
Mentions surface remain outside AI-14.
