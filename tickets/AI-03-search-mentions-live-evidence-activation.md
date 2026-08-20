# AI-03 — Search Mentions Live one-shot Evidence activation

**Status:** ready  
**Owner:** [CHAZ] operator / [GPT] Steward verification  
**Blocked by:** clean synchronized preflight and the authorized operator execution  
**Approved by:** Project Steward  
**Start commit:** `17300a87cda821e338b6c4dd5a551f3a7f564a09`  

## Purpose

Exercise the closed AI-02 Search Mentions Live adapter exactly once, preserve the resulting
Attempt/Capture as immutable Evidence, inspect what the provider actually returned, and
complete the accepted bounded manual off-host protection and restore proof before this
activation closes.

This is an operator activation ticket. It changes no working code, parser, fixture, Recipe,
schema, Derivation, selection, API, or acquisition schedule.

## Accepted foundation

AI-01 selected Search Mentions Live as the first AI Optimization foundation. AI-02 built,
reviewed, closed, and pushed the exact Evidence-only adapter:

`dataforseo-ai-optimization-llm-mentions-search-mentions-live-paid-probe-v1`

The current repository gate is clean synchronized `main` at:

`17300a87cda821e338b6c4dd5a551f3a7f564a09`

The accepted manual F6 mechanism remains the existing encrypted restic repository transported
through the configured `vedaops-drive` rclone remote. This acceptance is bounded to this one
fresh Evidence root. It does not complete routine F6 automation or authorize recurring
capture.

## Fresh contract and price review — 2026-08-20

The Steward rechecked the official Search Mentions Live endpoint and pricing immediately
before cutting this ticket.

Official endpoint documentation:

<https://docs.dataforseo.com/v3/ai_optimization/llm_mentions/search_mentions/live/>

Verified claimed contract:

- exactly one Live task per call;
- exact POST path `/v3/ai_optimization/llm_mentions/search_mentions/live`;
- execution may take up to 120 seconds;
- Google is an explicit platform;
- response testimony includes task cost/status, total/current/returned counts, continuation,
  question, answer, sources, AI search volume, monthly searches, and provider timestamps.

Official pricing:

<https://dataforseo.com/pricing/ai-optimization/llm-mentions>

The published calculator currently states `$0.10` per request plus `$0.001` per returned
row. With `limit=5`, the expected maximum successful five-row charge is approximately
`$0.105`. The exact adapter acknowledgment remains `200000` micro-USD (`$0.20`) as a
fail-closed ceiling, not an expected charge or permission for another request.

Mutable provider documentation and pricing can change. This review authorizes no call by
itself.

## Exact one-shot operation

Frozen inputs:

- keyword: `generative engine optimization`
- platform: `google`
- location: United States, `location_code=2840`
- language: English, `language_code=en`
- target behavior: one included keyword, `search_scope=["answer"]`,
  `match_type="word_match"`
- offset: `0`
- limit: `5`
- continuation: forbidden
- retries/follow-ups: forbidden
- authorization acknowledgment: `200000` micro-USD
- Evidence root:
  `$HOME/.local/share/observatory/ai03-search-mentions-generative-engine-optimization-2026-08-20`

Exact paid command:

```bash
cd /home/chaz/projects/vedaops/observatory

uv run python -m observatory.dataforseo_ai_optimization_search_mentions_paid_probe capture \
  --evidence-root "$HOME/.local/share/observatory/ai03-search-mentions-generative-engine-optimization-2026-08-20" \
  --keyword "generative engine optimization" \
  --authorize-max-micro-usd 200000
```

This command is recorded but not authorized until [CHAZ] explicitly approves it after seeing
this exact ticket and command.

Authorization, once given, covers exactly one process invocation and at most one provider
exchange. A nonzero exit, unresolved Attempt, missing Capture, `response_partial`,
`no_response`, credential-echo refusal, provider error testimony, unexpected charge, or any
other abnormal result is a hard stop. Do not retry and do not create a replacement Evidence
root without a new Steward/[CHAZ] decision.

## Steward one-shot authorization — 2026-08-20

After reviewing the exact AI-03 ticket and command at synchronized commit
`e31c8609c71db33605edd4149faa5c422d6be7bd`, [CHAZ] explicitly authorized exactly one
AI-03 paid operator invocation for:

- adapter:
  `dataforseo-ai-optimization-llm-mentions-search-mentions-live-paid-probe-v1`;
- keyword: `generative engine optimization`;
- exact Evidence root:
  `$HOME/.local/share/observatory/ai03-search-mentions-generative-engine-optimization-2026-08-20`;
- exact authorization acknowledgment: `200000` micro-USD;
- one process invocation and at most one POST;
- no retry, continuation, follow-up, replacement root, or second provider exchange.

Authorization is valid only from a clean `main` containing this durable record and
synchronized with `origin/main`, after every preflight below passes. The command remains a
hard stop after its first invocation regardless of exit code or transport/provider outcome.

## Preflight required before the command

The operator must prove:

- branch `main`, exact HEAD above, and clean tree;
- `main` synchronized with `origin/main`;
- the exact Evidence root does not exist;
- no pytest, capture, restic, rclone, or competing Observatory writer is active;
- no leftover `observatory-ce05-*` container;
- required provider credential environment values are present without printing them;
- the accepted restic password file and `vedaops-drive` configuration are present without
  printing secrets;
- no endpoint, timeout, body-limit, task JSON, or alternative spend argument is supplied.

If any preflight fails, stop before the provider command.

## Immediate post-capture gate

Record stdout, exit code, UTC start/end, exact HEAD, status before/after, and the emitted
Attempt and Capture IDs. Do not run the command again.

For a complete Capture, run the read-only inspect command exactly once against local
Evidence and redirect the byte-exact body outside the Evidence root:

```bash
uv run python -m observatory.dataforseo_ai_optimization_search_mentions_paid_probe inspect \
  --evidence-root "$HOME/.local/share/observatory/ai03-search-mentions-generative-engine-optimization-2026-08-20" \
  --capture-id "<CAPTURE_ID>" \
  > /tmp/ai03-search-mentions-response.body

wc -c /tmp/ai03-search-mentions-response.body
sha256sum /tmp/ai03-search-mentions-response.body
```

Inspection is local and read-only. Do not pretty-print, normalize, or overwrite the retained
body.

Then run:

```bash
uv run python -m observatory.evidence status \
  "$HOME/.local/share/observatory/ai03-search-mentions-generative-engine-optimization-2026-08-20"

uv run python -m observatory.evidence scrub \
  "$HOME/.local/share/observatory/ai03-search-mentions-generative-engine-optimization-2026-08-20"
```

A non-complete Capture, inspect refusal, or scrub failure blocks payload analysis and
protection acceptance. It never authorizes another provider exchange.

## Bounded F6 protection required

Before the paid Evidence is treated as safely protected:

1. quiesce the source store;
2. record a sorted exact Attempt/Capture inventory outside the Evidence root;
3. snapshot the complete Evidence root and inventory into the accepted encrypted restic
   repository through `vedaops-drive`, tagged for `observatory-evidence-store` and
   `f6-paid-ai03`;
4. record the exact restic snapshot ID and a non-secret receipt;
5. restore that snapshot into a fresh local directory;
6. open and scrub the restored Evidence Store;
7. independently recompute restored Attempt/Capture sets and require exact equality with the
   source inventory;
8. inspect the restored Capture and require byte count and SHA-256 equality with the source
   inspection;
9. copy the non-secret backup receipt and restore proof into the accepted off-host receipt
   locations.

The Steward will issue the exact protection commands after the live command returns IDs.
The source Evidence root remains quiescent between inventory and accepted snapshot.

## Payload assessment

After local and restored Evidence both verify, inspect the exact response for technical
planning only. Record:

- top-level and task status, cost, and counts;
- actual `current_offset`/`offset` behavior;
- whether `items_count`, `total_count`, and array length agree;
- continuation presence without following it;
- exact item key sets and null/state variation;
- returned question/answer relationship to the requested keyword;
- Google model/platform/location/language testimony;
- source counts, ranks, duplicate URLs, missing URLs, and repeated sources;
- AI search volume/monthly history shapes;
- provider first/last response timestamps;
- unexpected fields, cardinality, timestamp, numeric, or ordering behavior;
- whether five rows are sufficient to freeze a parser fixture.

This assessment does not create semantic identities or select a database design. Those
belong to the later parser and Derivation tickets after verified real testimony exists.

## Acceptance

AI-03 closes only when:

- exactly one authorized provider exchange occurred;
- exact Attempt/Capture IDs and transport state are recorded;
- the complete response body was inspected byte-exactly;
- source status and scrub are clean;
- encrypted off-host snapshot and fresh restore succeeded;
- source/restored Attempt and Capture sets match exactly;
- source/restored inspected body byte count and SHA-256 match;
- payload findings are recorded;
- no retry, continuation, second exchange, parser, fixture, Recipe, schema, Derivation, API,
  other surface, or push occurred without separate authorization.

## Next ticket boundary

If the real payload is complete and technically sufficient:

1. AI-04 — strict Search Mentions parser and frozen conformance fixture;
2. AI-05 — Derivation Recipe, identities, typed persistence, and PostgreSQL proof;
3. AI-06 — read/history API.

Target Metrics remains the next separate AI Optimization surface review after the Search
Mentions vertical slice. AI-03 does not authorize it.
