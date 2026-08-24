# AI-09 — Target Metrics Live one-shot Evidence activation

**Status:** authorized  
**Owner:** [CHAZ] operator / [GPT] Steward verification  
**Blocked by:** AI-08 — Target Metrics Live paid-probe adapter (`done`)  
**Approved by:** Project Steward  
**Start commit:** `b5271d72cfa945b52d8c843c46fdd93b6de7bc8e`  
**Product Owner direction:** [CHAZ] authorized AI-09 ticket creation and the exact
one-shot live operation recorded below on 2026-08-24.

## Purpose

Exercise the closed AI-08 Target Metrics Live adapter exactly once, preserve the resulting
Attempt/Capture as immutable Evidence, inspect the provider's actual aggregate testimony,
and complete the accepted bounded encrypted off-host snapshot and fresh-restore proof before
this activation closes.

This is an operator activation ticket. It changes no working code, parser, fixture,
Derivation Recipe, schema, Derivation, selection, API, or acquisition schedule. Recording
this ticket does not authorize the paid command.

## Accepted foundation

AI-07 selected and AI-08 implemented, independently reviewed, remediated, closed, and pushed
the exact Evidence-only adapter:

`dataforseo-ai-optimization-llm-mentions-target-metrics-live-paid-probe-v1`

Accepted implementation: `78f4db32c6d492e88ef305578432563ebb90785d`.  
Accepted remediation: `342a86a99ebf0603dbbc0db417c174dc902a3223`.  
AI-08 Steward closure: `b5271d72cfa945b52d8c843c46fdd93b6de7bc8e`.

The Target Metrics gate uses closure-owned issuance and consumption authority and
revalidates the committed Attempt and exact request body immediately before transport.
F13 therefore does not block this activation; F13 remains the before-next-use trigger for
the four older affected transport gates.

The accepted bounded F6 mechanism remains the encrypted restic repository transported
through the configured `vedaops-drive` rclone remote. This acceptance applies to one fresh
AI-09 Evidence root only. It does not complete routine F6 automation or authorize recurring
capture.

## Fresh contract and price review — 2026-08-24

The Steward rechecked the official Target Metrics Live contract and current pricing before
cutting this ticket.

Official endpoint documentation:

<https://docs.dataforseo.com/v3/ai_optimization/llm_mentions/target_metrics/live/>

Verified claimed contract:

- exact POST path
  `/v3/ai_optimization/llm_mentions/target_metrics/live`;
- Live retrieval in one POST, with exactly one task permitted per call;
- documented execution time up to 120 seconds;
- Target Metrics returns `aggregated_metrics` rather than Search Mentions result rows;
- the documented result has `total_count=0`, `offset=0`, `items_count=0`, and
  `items=null` even when useful aggregate testimony exists;
- `internal_list_limit` governs `sources_domain` and `search_results_domain` arrays,
  with minimum `1`, maximum `10`, and default `10`;
- `platform` supports `google` and `chat_gpt`; this activation fixes `google`;
- the accepted request explicitly fixes United States `location_code=2840`, English
  `language_code=en`, one included keyword target, `search_scope=["answer"]`,
  `match_type="word_match"`, and `internal_list_limit=10`.

Official pricing:

<https://dataforseo.com/pricing/ai-optimization/llm-mentions>

The published pricing currently lists `$0.10` per request plus `$0.001` per returned row.
The current price export supplied by [CHAZ] independently lists
`ai_optimization / llm_mentions/target_metrics/live` at `0.1` per normal/high request and
`0.001` per result. The exact adapter acknowledgement remains `200000` micro-USD
(`$0.20`) as a fail-closed ceiling, not an expected charge, invoice guarantee, or
permission for a second request.

Mutable provider documentation and pricing can change. This review authorizes no call by
itself. Recheck both official pages again immediately before the final authorization if the
operator run does not occur in this work session.

## Exact one-shot operation

Frozen inputs:

- adapter:
  `dataforseo-ai-optimization-llm-mentions-target-metrics-live-paid-probe-v1`;
- keyword: `generative engine optimization`;
- target: exactly one included keyword with `search_scope=["answer"]` and
  `match_type="word_match"`;
- platform: `google`;
- location: United States, `location_code=2840`;
- language: English, `language_code=en`;
- `internal_list_limit=10`;
- retries, continuation, polling, follow-ups, and second exchange: forbidden;
- authorization acknowledgement: `200000` micro-USD;
- Evidence root:
  `$HOME/.local/share/observatory/ai09-target-metrics-generative-engine-optimization-2026-08-24`.

Exact paid command:

```bash
cd /home/chaz/projects/vedaops/observatory

uv run python -m observatory.dataforseo_ai_optimization_target_metrics_paid_probe capture \
  --evidence-root "$HOME/.local/share/observatory/ai09-target-metrics-generative-engine-optimization-2026-08-24" \
  --keyword "generative engine optimization" \
  --authorize-max-micro-usd 200000
```

This command is authorized only under the exact one-shot record below and becomes valid
only from clean, synchronized `main` containing that durable record after every preflight
passes.

A nonzero exit, unresolved Attempt, missing Capture, `response_partial`, `no_response`,
credential-echo refusal, provider error testimony, unexpected charge, or any other abnormal
result is a hard stop. Do not retry and do not create a replacement Evidence root without a
new Steward/[CHAZ] decision.

## Steward one-shot authorization — 2026-08-24

After reviewing the exact ticket and command at synchronized commit
`c876c4678634246e6c4981bc24063225434e456f`, [CHAZ] explicitly authorized exactly one
AI-09 paid operator invocation for:

- adapter:
  `dataforseo-ai-optimization-llm-mentions-target-metrics-live-paid-probe-v1`;
- keyword: `generative engine optimization`;
- exact Evidence root:
  `$HOME/.local/share/observatory/ai09-target-metrics-generative-engine-optimization-2026-08-24`;
- exact authorization acknowledgement: `200000` micro-USD;
- one process invocation and at most one POST;
- no retry, follow-up, replacement root, or second provider exchange.

Authorization is valid only from a clean `main` containing this durable record and
synchronized with `origin/main`, after every preflight below passes. The paid command is
a hard stop after its first process invocation regardless of exit code or
transport/provider outcome. A failed preflight consumes no authorization because the paid
command has not begun; any invocation of the paid command consumes the authorization.

## Preflight required before the command

The operator must prove:

- branch `main`, the exact subsequently authorized HEAD, and a clean tree;
- `main` synchronized with `origin/main`;
- the exact Evidence root does not exist;
- no pytest, capture, restic, rclone, or competing Observatory writer is active;
- no leftover `observatory-ce05-*` container;
- required DataForSEO credential environment values are present without printing them;
- the accepted restic password file and `vedaops-drive` configuration are present without
  printing secrets;
- no endpoint, client, timeout, body-limit, task JSON, platform, location, language,
  target option, list-limit option, retry, or alternate spend argument is supplied.

If any preflight fails, stop before the provider command.

## Immediate post-capture gate

Record stdout, exit code, UTC start/end, exact HEAD, repository status before/after, and the
emitted Attempt and Capture IDs. Never run the paid command again.

For a complete Capture, run the read-only inspector exactly once against local Evidence and
redirect the byte-exact body outside the Evidence root:

```bash
uv run python -m observatory.dataforseo_ai_optimization_target_metrics_paid_probe inspect \
  --evidence-root "$HOME/.local/share/observatory/ai09-target-metrics-generative-engine-optimization-2026-08-24" \
  --capture-id "<CAPTURE_ID>" \
  > /tmp/ai09-target-metrics-response.body

wc -c /tmp/ai09-target-metrics-response.body
sha256sum /tmp/ai09-target-metrics-response.body
```

Inspection is local and read-only. Do not pretty-print, normalize, or overwrite the
retained body.

Then run Evidence status and scrub on the exact source root. A non-complete Capture,
inspect refusal, or scrub failure blocks payload analysis and F6 acceptance. It never
authorizes another provider exchange.

## Bounded F6 protection required

Before the paid Evidence is treated as safely protected:

1. quiesce the source Evidence root;
2. record sorted exact committed Attempt and Capture ID sets outside the source root;
3. snapshot the complete Evidence root and recorded inventory into the accepted encrypted
   restic repository through `vedaops-drive`, tagged `observatory-evidence-store` and
   `f6-paid-ai09`;
4. record the exact snapshot ID and a non-secret receipt;
5. restore the snapshot into a fresh local directory;
6. open and scrub the restored Evidence Store;
7. independently recompute the restored Attempt/Capture sets and require exact equality
   with the source inventory;
8. inspect the restored Capture and require byte count and SHA-256 equality with the source
   inspection;
9. copy non-secret backup and restore-proof receipts into the accepted off-host receipt
   locations and verify their uploaded bytes.

The Steward issues the exact protection commands only after the live command returns the
actual IDs. The source Evidence root remains quiescent between inventory and accepted
snapshot.

## Payload assessment

After local and restored Evidence both verify, record:

- top-level/task status, provider task ID, reported cost, and execution times;
- exact request echo and whether all frozen Target Metrics inputs agree;
- top-level/result key sets and all null/absence distinctions;
- whether documented `total_count=0`, `offset=0`, `items_count=0`, and `items=null`
  match actual testimony;
- exact `aggregated_metrics` key set;
- location, language, and platform grouping keys, mention counts, and AI search volumes;
- `sources_domain` ordering, cardinality, keys, counts, and whether ten entries are returned;
- whether `search_results_domain`, `brand_entities_title`, and
  `brand_entities_category` are absent, null, empty, or populated on the Google request;
- total mentions and total AI search volume;
- duplicate keys, zero values, unexpected decimal forms, unknown fields, count conflicts,
  and provider-documentation drift;
- whether the body is sufficient for a frozen primary conformance fixture and which
  invariants still require synthetic adversarial tests.

This assessment does not define semantic identities or database design. Those belong to
later separately accepted parser and Derivation tickets.

## Acceptance

AI-09 closes only after:

- [CHAZ] explicitly authorized the exact recorded one-shot operation;
- exactly one operator invocation and at most one provider exchange occurred;
- exact Attempt/Capture IDs and transport state are recorded;
- a complete response body was inspected byte-exactly;
- source status and scrub are clean;
- encrypted off-host snapshot and fresh restore succeeded;
- source/restored committed Attempt and Capture sets match exactly;
- source/restored inspected-body byte count and SHA-256 match;
- payload findings and exact unproven limits are recorded;
- no retry, follow-up, second exchange, parser, fixture promotion, Recipe, schema,
  Derivation, API, other surface, or unauthorized push occurred.

Only the Project Steward may set this ticket to `done`, after sufficient evidence and
explicit [CHAZ] authorization to close.

## Next boundary

If the verified payload is complete and sufficient, separately cut and accept bounded work
for:

1. strict Target Metrics parser and frozen conformance fixture;
2. Target Metrics Derivation Recipe, identities, typed persistence, and PostgreSQL proof;
3. Target Metrics recipe selection and read/history API.

AI-09 authorizes none of those later steps.

## Hard boundaries

- Operator activation ticket only; no `src/` or `tests/` edits.
- No provider call unless the durable one-shot authorization record remains present and
  every required preflight passes.
- No retry, continuation, follow-up, second root, second list limit, ChatGPT branch, domain
  target, Multi-Target, Historical, Lite, top-list, catalog, account, balance, or User Data
  request.
- No parser, conformance-fixture promotion, Recipe, Derivation, Outcome, Observation,
  migration, PostgreSQL mutation, API, projection, generic framework, scheduler, strategy,
  routine F6 automation, or F7 locking.
- Do not use an older F13-affected gate for this activation.
- Do not push; [CHAZ] performs the push manually.
