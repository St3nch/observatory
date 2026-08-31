# RK-02 — DataForSEO Google Related Keywords Live one-shot Evidence activation

**Status:** authorized — one-shot invocation not yet consumed  
**Owner:** [CHAZ] operator / [GPT] Steward verification  
**Blocked by:** synchronization of this authorization record and final no-spend preflight  
**Draft/review base:** `5d45137845820035137e07bb566f296bebcc158a`  
**Reviewer:** [CLAUDE] read-only technical review  
**Review result:** `RECONCILE` at `5d45137845820035137e07bb566f296bebcc158a`; Steward reconciled the technical findings and [CHAZ] resolved the remaining Product choice on 2026-08-31

## Purpose

Exercise the closed RK-01 DataForSEO Labs Google Related Keywords Live adapter exactly once,
preserve the resulting Attempt/Capture as immutable Evidence, inspect what DataForSEO actually
returned for the frozen seed and request context, and complete the accepted bounded encrypted
off-host snapshot plus fresh-restore proof before treating any paid Evidence as safely protected.

This is an operator activation ticket. It adds no transport code, parser, Conformance fixture,
Derivation Recipe, Outcome, Observation, PostgreSQL schema, Derivation, Recipe selection, API,
Holdings, Measurement Outcomes, Ranked Keywords work, Strategy behavior, pagination,
acquisition cadence, or backup framework.

This accepted ticket freezes the operator boundary. [CLAUDE]'s required read-only review and
Steward reconciliation are complete. On 2026-08-31 [CHAZ] separately authorized exactly one
live provider invocation under the frozen RK-02 contract. That authorization is not consumed
by this ticket edit, commit, push, or final no-spend preflight; it is consumed only when the
paid capture process is invoked from the clean synchronized authorization-record HEAD.

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

F7 remains unfired because RK-02 uses one fresh Evidence root and one operator process. F13
does not block this activation: RK-01 was hardened from birth with closure-owned transport
authority and is not one of F13's older affected gates.

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
approximately `$0.132` under the published schedule. This is a deliberately conservative
upper-bound calculation using the configured `limit=1000`, not the expected charge; the same
claimed contract documents an approximate depth-3 maximum near 584 items. The pricing page
explicitly states that `include_clickstream_data=true` multiplies request cost by two. RK-01
fixes clickstream to `false`. The current pricing page does not state a separate
`include_serp_info=true` surcharge.

The `200000` micro-USD acknowledgement remains a conservative fail-closed operator ceiling
with headroom. It is not expected cost, a provider-enforced billing cap, an invoice guarantee,
or permission for a retry.

The committed Attempt continues to record RK-01's frozen
`pricing_basis="dataforseo-labs-google-related-keywords-live-2026-08-28"`. The 2026-08-31
recheck is later operator claimed-contract review and deliberately does not rewrite that
closed RK-01 constant.

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

## Steward reconciliation of [CLAUDE] review

[CLAUDE] returned `RECONCILE`. GPT independently verified the load-bearing findings against
the live RK-01 adapter and Evidence CLI. The technical corrections below are accepted:

- credential echo is rejected before Capture commit, so a paid Attempt can exist without a
  Capture and the provider response bytes are not retained;
- non-zero capture exit may print no Attempt/Capture IDs, so the operator boundary needs an
  explicit read-only committed-ID recovery step;
- missing credentials fail before root creation, but a later post-create/pre-Attempt failure
  can still leave a FORMAT-only root;
- Attempt-without-Capture is authorized/unresolved and cannot be treated as definitely unsent
  or definitely uncharged;
- Evidence `status`/`scrub` must always carry the exact `--evidence-root`;
- successful Related Keywords inspect proves the adapter contract and complete nonempty
  transport testimony, not provider semantic success;
- F7 and F13 do not block this gate;
- the missing RK-01 module entrypoint is added to `AGENTS.md` by Steward authority maintenance.

[CHAZ] resolved the remaining Product choice on 2026-08-31: **hard stop, no pre-authorized
retry**. If the single authorized invocation commits a paid Attempt but yields no fixture-
quality Capture/body, RK-02 stops. Preserve and protect all committed paid Evidence, record the
honest result, and require a new later Steward/Product boundary before any replacement root or
second provider exchange. No failure class in RK-02 carries an automatic retry entitlement.

## [CHAZ] live one-shot authorization — 2026-08-31

[CHAZ] explicitly authorizes exactly one RK-02 DataForSEO Labs Google Related Keywords Live
provider request under the accepted closed adapter contract, with:

- exact seed `conspiracy theories`;
- exact acknowledgement `200000` micro-USD;
- exact frozen RK-01 request dimensions and endpoint;
- exactly one capture-process invocation and at most one provider POST;
- no retry;
- no replacement Evidence root;
- no pagination, continuation, polling, follow-up, changed seed, or second exchange.

The authorization was issued while `main` was clean and synchronized at
`cb235400b05a9c1136d95689023f3409874df21c`. It becomes runnable only after this durable
authorization record itself is committed and synchronized to `origin/main`, and after the
final no-spend preflight proves the repository is still clean/synchronized, the exact RK-02
Evidence root is absent, the required credential environment values are present in that same
operator shell without disclosure, F6 prerequisites remain available, and no conflicting
writer/backup process is active.

The exact clean synchronized commit containing this authorization record is the activation
HEAD for the one-shot run. Record that concrete HEAD in the operator output before invocation
and later in RK-02 closure. Any repository mutation after that synchronization invalidates the
preflight and requires reconciliation before the paid process starts.

This authorization is **not consumed** by recording/committing/pushing it or by a failed
preflight before process start. First invocation of the frozen paid capture command consumes
it regardless of exit code or transport/provider result. After process start, no failure class
authorizes a retry or replacement root.

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

Accepted F6 identifiers to carry into the final record are rclone remote `vedaops-drive:`,
restic repository path `VedaOps Backups/Observatory/evidence-store/repository`, restic
password file `$HOME/.config/restic/observatory-password`, and tags
`observatory-evidence-store` plus `f6-paid-rk02`.

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
Missing credentials therefore fail before this adapter creates the root. However, once
credentials load, `_open_or_create` can create FORMAT before later keyword/Attempt validation.
A post-create, pre-Attempt failure may therefore leave a FORMAT-only root. Do not delete that
root and rerun under the same authorization; stop for Steward/[CHAZ] reconciliation.

If an Attempt is committed but no Capture is committed, the result is **authorized/unresolved**.
It must not be treated as definitely unsent, definitely uncharged, or safe to retry. Process
death after Attempt commit, credential-echo rejection after transport, or Capture-commit/read-
back failure can leave this state. Credential echo specifically rejects before Capture commit;
the paid provider response bytes are then not retained by Observatory.

A failed preflight before process start consumes no Product authorization. Once the capture
process is invoked, the one-shot Product authorization is consumed regardless of exit code or
provider/transport result. The HTTP client has phase-specific timeouts (`connect=30`,
`read=120`, `write=30`, `pool=30` seconds); `read=120` is not a total wall-clock deadline.
Do not manually interrupt merely because 120 seconds passes. If the process is still running
after five minutes, report the live state to the Steward before any intervention; that
five-minute point is an operator escalation threshold, not permission to kill or retry.

## Final capture shape — separately gated

```bash
cd /home/chaz/projects/vedaops/observatory

uv run python -m observatory.dataforseo_google_related_keywords_paid_probe capture \
  --evidence-root "$HOME/.local/share/observatory/rk02-related-keywords-conspiracy-theories-2026-08-31" \
  --keyword "conspiracy theories" \
  --authorize-max-micro-usd 200000
```

This frozen command is covered by the 2026-08-31 [CHAZ] one-shot provider/spend authorization above. It may run exactly once only after this authorization record is committed and synchronized and the final no-spend preflight passes from that exact clean activation HEAD.

## Immediate post-capture gate

After the single later-authorized invocation:

1. record UTC start/end, exit code, repository HEAD/tree, and any emitted IDs;
2. never rerun the paid command under the same authorization;
3. on any non-zero exit, remember the CLI may print no IDs. If the exact Evidence root exists,
   recover the committed-ID inventory read-only from COMMITTED marker parent directories
   before drawing any sent/unsent conclusion;
4. run status and scrub with the exact explicit Evidence root;
5. if complete nonempty Capture Evidence exists, use the RK-01 byte-exact inspector and
   record body byte count and SHA-256 outside the Evidence root;
6. preserve every committed paid Attempt even if fixture-quality complete Evidence does not result.

Exact source committed-ID recovery/inventory command:

```bash
EVIDENCE_ROOT="$HOME/.local/share/observatory/rk02-related-keywords-conspiracy-theories-2026-08-31"
INVENTORY="/tmp/rk02-related-keywords-source-inventory.txt"

: > "$INVENTORY"
for kind in attempts captures; do
  base="$EVIDENCE_ROOT/$kind/v1"
  if [ -d "$base" ]; then
    find "$base" -type f -name COMMITTED -printf '%h\n' \
      | sed 's#.*/##' \
      | LC_ALL=C sort \
      | sed "s/^/${kind%s} /" >> "$INVENTORY"
  fi
done

cat "$INVENTORY"
sha256sum "$INVENTORY"
```

Exact local Evidence checks:

```bash
uv run python -m observatory.evidence status --evidence-root "$EVIDENCE_ROOT"
uv run python -m observatory.evidence scrub --evidence-root "$EVIDENCE_ROOT"
```

`status` proves only that the format-2 store opens. `scrub` verifies commitment-claiming
directories it discovers. Neither is a Capture-completeness or provider-success witness.

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
the adapter-level witness that the cited Capture is for
`dataforseo-labs-google-related-keywords-live-paid-probe-v1`, is verified HTTP event version
2, has `transport_state=response_complete`, response completeness `complete`, and a present
nonempty body. Inspect proves complete transport testimony, **not** that the provider body is
semantically successful; a complete provider-error envelope may still inspect successfully.

Partial/no-response, inspect refusal, credential-echo refusal, scrub failure, provider error,
unexpected transport/provider result, or other abnormal result is a hard stop and does not
authorize retry.

If any paid Related Keywords Attempt was committed, protect it through bounded F6 even if no
fixture-quality complete body exists. On credential-echo rejection specifically, the Attempt
must still be inventoried and protected even though no Capture exists and the response bytes
were discarded before Capture commit.

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
