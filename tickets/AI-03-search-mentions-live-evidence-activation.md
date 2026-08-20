# AI-03 — Search Mentions Live one-shot Evidence activation

**Status:** closed  
**Owner:** [CHAZ] operator / [GPT] Steward verification  
**Blocked by:** none  
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
uv run python -m observatory.evidence \
  --evidence-root "$HOME/.local/share/observatory/ai03-search-mentions-generative-engine-optimization-2026-08-20" \
  status

uv run python -m observatory.evidence \
  --evidence-root "$HOME/.local/share/observatory/ai03-search-mentions-generative-engine-optimization-2026-08-20" \
  scrub
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


## Steward live closure — 2026-08-20

[CHAZ] performed exactly one authorized process invocation and the adapter performed exactly
one provider exchange. The invocation started at `2026-08-20T17:36:58Z`, ended at
`2026-08-20T17:37:00Z`, exited `0`, and left the repository clean at exact authorized HEAD
`8d0a5ee7a2b8437bb70aeb55f25f2ec58200a626`.

Committed live Evidence:

- Attempt `2a363a7bb07c27e55301d604afb1d06fda817760635943c68bcb4b567f9f7d03`;
- Capture `bea666f9b982054df287da253fb49b0e0a9c1022b461c111a483b43d8606d4db`;
- transport state: complete response;
- inspected byte-exact body: `48466` bytes;
- inspected body SHA-256:
  `8b3cd0fb0c9fa23c102696bfe6b7212396c0f7c110e9ca8ca5b8ee5af182e80a`;
- source status: `format-2 ok`;
- source scrub: clean.

The independently recorded source inventory contains exactly that Attempt and Capture. Its
SHA-256 is `e2302f202834d01a0889aa57edfae36a223daaa9922b9763a6616f50dfc7e169`.

The accepted encrypted repository `52a88583` created snapshot
`b1f163145728e061c649cad174b2d8ca2de3e6af21e98e7312853a0a2cfb9724`, tagged
`observatory-evidence-store` and `f6-paid-ai03`. A fresh restore opened as `format-2`,
scrubbed clean, and independently reproduced the exact Attempt/Capture set. Source,
snapshot-restored, and independently recomputed inventories all had the same SHA-256 above.
The restored inspected body was also exactly `48466` bytes with the same body SHA-256.

Non-secret receipt files were copied to the accepted off-host `receipts/` and
`restore-proofs/` folders and verified byte-for-byte after upload:

- `ai03-search-mentions-backup-b1f16314.ok.json` SHA-256
  `a54d4423fe0da9e771ccf97abc1cdcfe3bd8547a98596197836291df476616d4`;
- `ai03-search-mentions-restore-b1f16314.ok.json` SHA-256
  `f33fd3c73e2620d16eca9e67f4a13e61ff0f9441d6ca0a6b3b2c3e71252d7063`.

### Verified payload findings

- Envelope version `0.1.20260806`; top-level and task status `20000` / `Ok.`;
  `tasks_count=1`, `tasks_error=0`, task `result_count=1`.
- Top-level and task cost both equal `0.105`; reported times are `0.9244 sec.` and
  `0.8885 sec.`. Task ID is `08201736-1463-0650-0000-9c9cdd333257`.
- Task data repeats the exact requested platform, location, language, limit, offset, and
  nested target. The result object itself contains only `items`, `items_count`, `offset`,
  `search_after_token`, and `total_count`.
- The real result uses `offset=0`; there is no `current_offset` field. It reports
  `total_count=3055`, `items_count=5`, and exactly five items. A non-null continuation token
  is present and remains opaque, unconsumed testimony.
- Returned questions, in provider order, are `enception`,
  `mathematical artificial intelligence`, `search engine optimized`, `seos`, and
  `engine optimization service`. They are loose word-match results, not the requested
  phrase, and must not be replaced by the requested keyword.
- The five `ai_search_volume` values are `368000`, `201000`, `135000`, `110000`, and
  `110000`. Every item is Google / `google_ai_overview`, United States `2840`, English,
  web-search-based, and has a nonempty answer.
- The items contain `7`, `14`, `13`, `4`, and `10` sources: `48` total. Source ranks are
  contiguous one-based integers within each item. All 48 URL strings are nonempty and unique
  in this fixture. Absence of a duplicate is not proof that later duplicate URLs may be
  collapsed.
- Every source has the same nine keys: `rank`, `title`, `url`, `domain`, `source_name`,
  `snippet`, `publication_date`, `thumbnail`, and `markdown`. The first six are populated
  with the expected integer/string types; the last three are null in all 48 occurrences.
- Every item has exactly 12 descending, unique `(year, month)` monthly-search points: 60
  total. `ai_search_volume` disagrees with the newest monthly value for three of five items,
  so those are distinct testimony and cannot be derived from each other.
- `first_response_at` and `last_response_at` use provider lexical form
  `YYYY-MM-DD HH:MM:SS +00:00`, not RFC 3339. Two items span multiple observations; the
  others have equal first/last timestamps.
- `search_results`, `brand_entities`, and `fan_out_queries` are null on all five items.
  Those null-only observations do not establish the shape of future non-null values.

This live body is sufficient to freeze an exact AI-04 primary conformance fixture: five
items, 48 ranked sources, 60 monthly points, large Markdown answers, independent clocks and
volumes, and opaque continuation testimony. It is not evidence for non-null optional-field
shapes, duplicate-URL absence as an invariant, complete pagination, or a persistence
identity. AI-04 must preserve the observed testimony, test bounded adversarial variants, and
fail closed on unsupported shapes without another provider call.

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
