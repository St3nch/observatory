# RK-02 — DataForSEO Google Related Keywords Live one-shot Evidence activation

**Status:** provisional  
**Owner:** [CHAZ] operator / [GPT] Steward verification  
**Blocked by:** RK-01 closed Evidence-only adapter; [CLAUDE] read-only review; final Steward reconciliation; separate explicit [CHAZ] one-shot authorization  
**Draft base:** `00308c64a6cd0e60b73deda37986aebf70bdaf3f`  
**Reviewer:** [CLAUDE] read-only technical review

## Purpose

Exercise the closed RK-01 DataForSEO Labs Google Related Keywords Live adapter exactly once,
preserve the resulting Attempt/Capture as immutable Evidence, inspect what DataForSEO actually
returned for the frozen seed and request context, and complete the accepted bounded encrypted
off-host snapshot plus fresh-restore proof before treating any paid Evidence as safely protected.

This is an operator activation ticket. It adds no transport code, parser, Conformance fixture,
Derivation Recipe, Outcome, Observation, PostgreSQL schema, Derivation, Recipe selection, API,
Holdings, Measurement Outcomes, Ranked Keywords work, Strategy behavior, pagination,
acquisition cadence, or backup framework.

This provisional ticket authorizes only read-only review and Steward ticket work. It does
**not** authorize provider transport, credentials, spend, Evidence creation, or the capture
command. After [CLAUDE]'s review, [GPT] must reconcile and commit the final operator boundary.
[CHAZ] must then separately authorize the exact one-shot command from the exact final clean HEAD.

## Accepted RK-01 foundation

RK-01 closed the Evidence-only adapter:

`dataforseo-labs-google-related-keywords-live-paid-probe-v1`

Accepted implementation:

`d23abce3374219fb1ce10459b4790d5f51d00fb5`

RK-01 closure/current pre-RK-02 base:

`372f33ab7030625526674523d86e19edb5e1ae48`

The adapter is hardened with closure-owned transport authority. RK-02 reuses it as-is unless
the read-only review finds a concrete blocker. Do not refactor working transport merely
because this is the first live Related Keywords activation.

The activation candidate freezes:

- seed keyword: exact `conspiracy theories`;
- `location_code=2840`;
- `language_code="en"`;
- `depth=3`;
- `limit=1000`;
- `offset=0`;
- `order_by=["keyword_data.keyword_info.search_volume,desc"]`;
- `include_seed_keyword=true`;
- `include_serp_info=true`;
- `include_clickstream_data=false`;
- `ignore_synonyms=false`;
- `replace_with_core_keyword=false`;
- `filters` absent;
- `tag` absent;
- exact authorization acknowledgement `200000` micro-USD.

Exactly one capture-process invocation and at most one provider POST are permitted only after
a later explicit [CHAZ] authorization. First invocation of the paid capture process consumes
that human authorization regardless of exit code or provider/transport result.

Retry, replacement Evidence root, offset-following, pagination, continuation, polling,
follow-up, second provider exchange, or changed seed/request shape are forbidden under that
authorization.

F3 broad rollout and F12 recurring acquisition remain unfired. This ticket creates no panel,
cadence, monitoring state, Strategy state, or automatic follow-up acquisition.

## Fresh claimed-contract and pricing check — 2026-08-31

The Steward rechecked the current official Related Keywords Live documentation and DataForSEO
Labs Google pricing while preparing RK-02.

Official claimed-contract documentation:

<https://docs.dataforseo.com/v3/dataforseo_labs-google-related_keywords-live/>

Official pricing:

<https://dataforseo.com/pricing/dataforseo-labs/dataforseo-google-api>

Current official documentation still claims:

- Live endpoint `POST https://api.dataforseo.com/v3/dataforseo_labs/google/related_keywords/live`;
- one task per Live API call;
- `depth` accepts `0..4`, with approximate maxima `1 / 8 / 72 / 584 / 4680`;
- `include_seed_keyword`, `include_serp_info`, `include_clickstream_data`,
  `ignore_synonyms`, and `replace_with_core_keyword` remain accepted request fields;
- the Related Keywords page still gives no useful endpoint-local description for
  `include_clickstream_data` or `ignore_synonyms`;
- default ordering remains `["keyword_data.keyword_info.search_volume,desc"]`;
- `limit` maximum remains `1000`;
- `offset` default remains `0`;
- result context still documents seed, location/language, total/item counts, and items;
- returned items still document keyword data, traversal depth, and related-keyword testimony.

Current official Labs Google pricing lists the applicable "all other endpoints" rate as
`$0.012` per task plus `$0.00012` per returned item. A full 1000-item response is therefore
approximately `$0.132` under the published schedule. The pricing page explicitly states that
`include_clickstream_data=true` multiplies request cost by two. RK-01 fixes clickstream to
`false`. The current pricing page does not state a separate `include_serp_info=true` surcharge.

The `200000` micro-USD acknowledgement remains a conservative fail-closed operator ceiling
with headroom. It is not expected cost, a provider-enforced billing cap, an invoice guarantee,
or permission for a retry.

Official documentation/pricing are mutable claimed contract, not Observatory Evidence.
Recheck them again before final one-shot authorization if the operation does not occur in the
same work session as final ticket acceptance.

## Why activation precedes RK-03

D12 keeps claimed contract, empirical Evidence, and Observatory interpretation separate.
RK-01 deliberately left empirical questions for the live Evidence:

- whether the frozen request is accepted live;
- actual provider envelope/result shape and additive fields;
- actual `total_count`, `items_count`, and item count;
- whether `limit=1000` binds;
- observed traversal depths;
- observed `related_keywords` presence/null/empty/order/duplication behavior;
- observed provider timestamps/update fields;
- actual provider-reported cost and response size;
- actual SERP enrichment under `include_serp_info=true`;
- whether the body is suitable as RK-03's primary Conformance fixture.

Synthetic RK-01 tests prove Observatory's request bytes and one-exchange Evidence boundary.
They do not prove provider response semantics. RK-03 must start from verified RK-02 Evidence.

## Mandatory [CLAUDE] read-only review

Before this ticket becomes final, [CLAUDE] must inspect the current repository without
mutation. No provider call, credential access, Evidence creation, PostgreSQL mutation,
network-dependent test, commit, or push is authorized.

At minimum inspect:

- `AGENTS.md`, `VISION.md`, `VOCABULARY.md`;
- relevant D8-D14 and F3/F6/F7/F12/F13 authority;
- `docs/specs/capture-event-v2.md`;
- RK-01 ticket;
- RK-01 adapter and relevant tests;
- AI-09 and AI-14 activation precedents;
- current Evidence status/scrub and operator tooling this ticket expects to reuse.

Challenge:

1. whether RK-01 is actually ready for one live invocation without code changes;
2. whether the public CLI and implementation ordering are described correctly;
3. whether `conspiracy theories` passes the implemented grammar;
4. whether `200000` remains sound against the dated official pricing;
5. whether provider-contract drift invalidates the frozen request;
6. whether manual F6 remains compatible with current VPS/operator tooling;
7. one-shot, process-start consumption, no-retry, fresh-root, and hard-stop semantics;
8. the capture CLI's credential/root ordering and failure-state consequences;
9. whether successful `inspect` is the proper complete/nonempty Capture witness;
10. whether any committed paid Attempt must still be protected after abnormal results;
11. hidden F3/F6/F7/F12/F13 or multi-exchange blockers;
12. accidental authorization of parser/Recipe/API/Ranked Keywords/Strategy work;
13. any Product question genuinely unresolved.

Return `READY`, `RECONCILE`, or `NOT_READY`, with exact file/code references and concrete
ticket corrections. Do not implement anything.

## Final-ticket operator record required

The final reconciled ticket must freeze before [CHAZ] authorization:

- exact clean activation HEAD and accepted synchronization state;
- exact fresh Evidence root;
- exact seed `conspiracy theories`;
- exact public capture command;
- exact `200000` acknowledgement;
- current official contract/pricing basis;
- exact preflight and hard stops;
- exact local inspect/status/scrub sequence;
- exact source inventory format;
- exact encrypted restic remote/repository and RK-02 tags;
- exact fresh restore path and restored scrub;
- exact Attempt/Capture set equality;
- restored response-body byte-count/SHA-256 equality when complete Evidence exists;
- explicit no retry, replacement root, pagination, continuation, follow-up, or second call.

Candidate final Evidence root:

`$HOME/.local/share/observatory/rk02-related-keywords-conspiracy-theories-2026-08-31`

Candidate source inspect file:

`/tmp/rk02-related-keywords-response.body`

Candidate snapshot tags:

- `observatory-evidence-store`
- `f6-paid-rk02`

## Required preflight boundary

Before the paid process starts, prove at minimum:

- canonical VPS repo `/home/chaz/projects/vedaops/observatory`;
- branch `main`, exact final authorized HEAD, clean tree;
- synchronization state required by the final ticket;
- exact Evidence root absent;
- no competing Observatory capture writer or conflicting restic/rclone operation;
- both DataForSEO credential variables are nonempty in the same shell without printing them;
- accepted restic password/config and rclone remote exist without exposing secrets;
- seed exactly `conspiracy theories`;
- exact integer acknowledgement `200000`;
- no caller endpoint/body/depth/limit/offset/order/location/language/enrichment/timeout/
  response-ceiling/retry/continuation/pagination seam.

The RK-01 CLI loads DataForSEO credentials **before** opening or creating the Evidence root.
Missing credentials therefore fail before this adapter creates the root. Do not copy AI-14's
FORMAT-only-root failure semantics into RK-02.

A failed preflight before process start consumes no Product authorization. Once the capture
process is invoked, the one-shot Product authorization is consumed regardless of exit code or
provider/transport result. Do not interrupt a started process merely because it takes longer
than expected; the accepted read timeout is 120 seconds.

## Provisional capture shape — not authorized

```bash
cd /home/chaz/projects/vedaops/observatory

uv run python -m observatory.dataforseo_google_related_keywords_paid_probe capture \
  --evidence-root "$HOME/.local/share/observatory/rk02-related-keywords-conspiracy-theories-2026-08-31" \
  --keyword "conspiracy theories" \
  --authorize-max-micro-usd 200000
```

This command is **not authorized** by this provisional ticket.

## Immediate post-capture gate

After the single later-authorized invocation:

1. record UTC start/end, exit code, repository HEAD/tree, and emitted IDs;
2. never rerun the paid command under the same authorization;
3. inspect/open the exact Evidence root and run status/scrub;
4. if complete nonempty Capture Evidence exists, use the RK-01 byte-exact inspector and
   record body byte count and SHA-256 outside the Evidence root;
5. preserve every committed paid Attempt even if fixture-quality complete Evidence does not result.

Inspect shape after a Capture ID exists:

```bash
uv run python -m observatory.dataforseo_google_related_keywords_paid_probe inspect \
  --evidence-root "$HOME/.local/share/observatory/rk02-related-keywords-conspiracy-theories-2026-08-31" \
  --capture-id "<CAPTURE_ID>" \
  > /tmp/rk02-related-keywords-response.body

wc -c /tmp/rk02-related-keywords-response.body
sha256sum /tmp/rk02-related-keywords-response.body
```

Capture CLI exit `0` is not semantic provider-success proof. Successful byte-exact inspect is
the adapter-level witness that the cited Capture is verified HTTP event version 2,
`transport_state=response_complete`, response completeness is `complete`, and the body is
present and nonempty.

Partial/no-response, inspect refusal, credential-echo refusal, scrub failure, provider error,
unexpected transport/provider result, or other abnormal result is a hard stop and does not
authorize retry.

If any paid Related Keywords Attempt was committed, protect it through bounded F6 even if no
fixture-quality complete body exists.

## Bounded F6 protection

Reuse the accepted manual protection spine; build no new backup automation:

1. quiesce the source Evidence root;
2. open/inspect and scrub it;
3. record sorted exact committed Attempt/Capture ID sets outside the root and hash inventory;
4. create an encrypted non-destructive restic snapshot of complete root + inventory through
   the already accepted rclone-backed remote;
5. record snapshot ID and non-secret receipt;
6. restore into a fresh local directory;
7. open and scrub the restored store;
8. recompute restored Attempt/Capture sets and require exact source equality;
9. for a complete body, inspect restored Capture and require exact byte-count/SHA-256 equality;
10. preserve and verify the accepted non-secret backup/restore proof receipts.

Exact snapshot/restore commands and the future snapshot ID are finalized only after live IDs
exist. Routine automated F6 remains deferred.

## Payload assessment after protection

Only after source and restored Evidence verify, assess:

- provider envelope/task statuses, times, IDs, cost, result count/path, and request echo;
- exact result key set and seed/location/language testimony;
- `total_count`, `items_count`, and actual item length;
- limit binding and observed item ordering;
- traversal depths;
- `related_keywords` presence/type/null/empty/duplicates/order;
- keyword-data field states and provider update/data-period testimony;
- SERP enrichment under `include_serp_info=true`;
- clickstream structures under `include_clickstream_data=false`;
- additive/unknown fields;
- exact body byte size/SHA-256 and provider-reported cost;
- suitability as RK-03 primary Conformance fixture;
- unobserved branches needing synthetic adversarial tests rather than another provider call.

One Capture establishes testimony only for this exact exchange. It does not prove provider
ordering, universal nullability, complete corpus coverage, fixed depth cardinality, stable
future fields, or a billing formula.

## Acceptance / stop point

RK-02 closes only with one honest recorded outcome:

1. **Accepted complete Evidence:** one-shot complete/nonempty Capture, clean local Evidence,
   accepted bounded F6 snapshot/restore proof, restored-body equality, and payload assessment;
   or
2. **Honest failed/partial activation:** authorization consumed without fixture-quality
   complete Evidence; all committed paid Evidence preserved/protected as applicable; no retry;
   future action requires a separate Steward/Product boundary.

If accepted complete Evidence exists, the next boundary is RK-03: strict Related Keywords
parser plus exact frozen Conformance fixture and synthetic adversarial mutations. RK-03 does
not silently define the later Recipe, typed discovery graph, API, Outcomes/Holdings, Ranked
Keywords, F12 acquisition, or Strategy behavior.
