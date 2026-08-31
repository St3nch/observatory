# RK-02 — DataForSEO Google Related Keywords Live one-shot Evidence activation

**Status:** review — accepted complete Evidence; closure authorization pending  
**Owner:** [CHAZ] operator / [GPT] Steward verification  
**Blocked by:** explicit [CHAZ] authorization to close RK-02  
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

## Steward live Evidence and payload assessment — 2026-08-31

[CHAZ] performed exactly one authorized RK-02 capture-process invocation from clean,
synchronized `main` at activation HEAD
`6bec2a9cc8c6aa04ff9081435f06a58a3d98bb36`. The process started at
`2026-08-31T19:58:12Z`, ended at `2026-08-31T19:58:13Z`, exited `0`, emitted one Attempt
and one Capture, and left the repository clean at the activation HEAD. The one-shot
authorization is consumed. No retry, replacement root, pagination, continuation, polling,
follow-up, changed seed, or second provider exchange occurred or is authorized.

Committed live Evidence:

- Attempt `d41ba58d56a4adfa297c832175b9efe21606af3b4a1b78b1f05119700364e7fb`;
- Capture `774ab90603bd32c906023290f2c10acab69ff0dbfd95a87d928278d9a1322d63`;
- exact Evidence root
  `$HOME/.local/share/observatory/rk02-related-keywords-conspiracy-theories-2026-08-31`;
- source Evidence status `format-2 ok` and source scrub clean;
- exact inspected body `177120` bytes;
- body SHA-256
  `e128f2f81d51479237f1bd7e51feee3dfffcae4596558ebff67365f03cd1decb`;
- independently recorded source inventory contains exactly the one Attempt and one Capture
  above and has SHA-256
  `6d6b229b2f5e1084c9bf753550364db226d7ab92c032a72da1fdf37809e23801`.

### Accepted bounded F6 proof

The existing encrypted restic repository `52a88583` through `vedaops-drive:` created
snapshot
`5839e6fb2ab9bd05a2efe32c9f3d7936f190e1c1bf42daed425c9f617e9cf382`, tagged
`observatory-evidence-store` and `f6-paid-rk02`. A fresh restore into
`/tmp/rk02-related-keywords-restore.25iEZh` opened as format 2 and scrubbed clean.

Source inventory, snapshot-restored inventory, and independently recomputed restored
inventory were byte-identical and all had the same inventory SHA-256 above. The restored
Capture inspected successfully as exactly `177120` bytes with the same body SHA-256 as the
source, and the source/restored body files were byte-identical.

Non-secret receipt files were copied to the accepted off-host `receipts/` and
`restore-proofs/` folders and downloaded again to fresh local files. Each remote round trip
was byte-identical:

- `rk02-related-keywords-backup-5839e6fb.ok.json` SHA-256
  `93b11ffb12cb25c6668fe9ea6f28d20b00f2faad6d1bed56c0c3850eae556f61`;
- `rk02-related-keywords-restore-5839e6fb.ok.json` SHA-256
  `4ecd35cce98df37efb79263143dd875f741df2ee9443520bc39bdb783f946415`.

This satisfies the accepted bounded manual F6 protection requirement for this RK-02 paid
Evidence root. It does not complete routine F6 automation.

### Verified provider payload findings

After the initial bounded assessment, independent read-only [CLAUDE] and [GROK] reviews plus
a separate Steward-local full-body analysis all rechecked the same exact `177120`-byte body.
They independently converged on the corrections and additional findings below. This
reconciliation changes only the recorded interpretation of already accepted Evidence; it
does not alter the Capture, authorize another provider exchange, or freeze RK-03/RK-04
semantics prematurely.

- The envelope version is `0.1.20260831`. Top-level and task statuses are `20000` / `Ok.`;
  `tasks_count=1`, `tasks_error=0`, and task `result_count=1`. No duplicate JSON object member
  names were observed in the exact body.
- Provider-reported top-level and task cost both equal `0.0216`; reported times are
  `0.2494 sec.` and `0.1849 sec.`. Task ID is
  `08311958-1463-0387-0000-415a20bd3cc6`, and task path is exactly
  `["v3", "dataforseo_labs", "google", "related_keywords", "live"]`.
- The task request echo agrees with the frozen RK-01 request: API `dataforseo_labs`, function
  `related_keywords`, `se_type=google`, exact seed `conspiracy theories`, United States
  `location_code=2840`, English `language_code=en`, `depth=3`, `limit=1000`, `offset=0`,
  requested search-volume-descending `order_by`, seed inclusion true, SERP inclusion true,
  clickstream inclusion false, synonyms not ignored, and core-keyword replacement false.
- The observed cost `0.0216` exactly matches the freshly reviewed published calculation for
  one task plus 80 returned items (`0.012 + 80 * 0.00012`) for this Capture. That agreement is
  testimony for this request only, not proof of a universal billing formula.
- The result has exactly the keys `items`, `items_count`, `language_code`, `location_code`,
  `se_type`, `seed_keyword`, `seed_keyword_data`, and `total_count`. It echoes the exact seed,
  location, and language, reports `total_count=80` and `items_count=80`, and contains exactly
  80 item objects. The configured `limit=1000` therefore did not bind on this Capture.
- All 80 returned item keywords are unique in this body. The numeric search-volume testimony
  is observed in non-increasing order across the returned item array, consistent with the
  requested ordering. One Capture does not prove stable ordering, tie-break behavior, or a
  future provider invariant.
- Traversal depths are observed across the full requested range: one item at depth `0`, eight
  at depth `1`, thirty at depth `2`, and forty-one at depth `3`. The exact seed is returned as
  the depth-0 item.
- Every item has exactly `depth`, `keyword_data`, `related_keywords`, and `se_type`. Every
  item `keyword_data` object has the same twelve keys observed in `seed_keyword_data`:
  `avg_backlinks_info`, `clickstream_keyword_info`, `keyword`, `keyword_info`,
  `keyword_info_normalized_with_bing`, `keyword_info_normalized_with_clickstream`,
  `keyword_properties`, `language_code`, `location_code`, `se_type`, `search_intent_info`,
  and `serp_info`. `seed_keyword_data` is value-identical to the depth-0 item's
  `keyword_data` in this Capture. RK-03 must preserve both provider paths and synthetic-test
  disagreement rather than silently double-counting or deduplicating them by assumption.
- `related_keywords` is an array on 60 items and null on 20; no absent or empty-array branch
  is observed. Fifty-nine arrays contain eight targets and one contains five, for 477 total
  references to 246 distinct target strings. No array contains a duplicate target, and no
  self-reference is observed. The 20 nulls occur at both depth `2` (10) and depth `3` (10),
  so null is not evidenced as a depth-boundary or graph-leaf state.
- The provider's related-keyword testimony is a relatedness neighborhood, not a parent-child
  tree or breadth-first edge set. Among references whose target is also one of the 80 returned
  items, target-depth minus source-depth is observed as `+1` on 96 edges, `0` on 96, `-1` on
  69, and `-2` on 21. Sixty-seven distinct targets have more than one incoming reference;
  maximum observed in-degree is 26. Provider-stated `depth` must therefore remain testimony
  attached to the returned item rather than being recomputed from the relationship set.
- The returned 80 items do not close the relationship neighborhood: 167 distinct related
  targets are not returned as enriched item keywords. Fourteen distinct frontier targets
  occur on 18 references from depth-1 or depth-2 sources even though `depth=3` was requested
  and `limit=1000` did not bind. The reason those targets lack enriched returned items is
  unstated; they must not be labeled as merely beyond depth or truncated by limit. Later
  modeling must preserve the exact source-to-target testimony without inventing enriched-node
  facts for those frontier strings.
- Under `include_serp_info=true`, `serp_info` has three empirically distinct states in this
  Capture: 60 metrics-bearing objects, 18 JSON nulls, and 2 present objects whose SERP payload
  fields are null while `last_updated_time` is the sentinel-shaped exact string
  `0001-01-01 00:00:00 +00:00`. No absent branch is observed. The two sentinel-shaped objects
  must not be silently promoted to ordinary Provider Update Times; the exact provider value
  is testimony while its semantic meaning remains a later Recipe decision. Existing Keyword
  Overview timestamp validation would accept year 1 syntactically, so RK-03 must not reuse
  that helper without an explicit Related Keywords rule.
- In this one Capture, all 60 items with a `related_keywords` array also have metrics-bearing
  `serp_info`, while the 20 null-edge items have either null SERP (18) or the sentinel-shaped
  object (2). This exact correlation is testimony, not an invariant or proof of what null
  means. Nine of the 60 edge-bearing items do not list `related_searches` among
  `serp_item_types`, so the relationship array must not be modeled as a copy of that SERP
  feature.
- `avg_backlinks_info` is an object on 59 items and null on 21. `keyword_info`,
  `keyword_properties`, and `search_intent_info` are objects on all 80 items. Provider
  `main_intent` is `informational` on 78 items and `commercial` on 2; this is attributed
  classification testimony for this Capture, not a Strategy conclusion.
- `keyword_properties.core_keyword` is stated on 21 items, naming 20 distinct strings; 16 of
  those strings appear in neither the 80 returned keyword strings nor the 246 distinct
  `related_keywords` targets. Across returned keywords, relationship targets, and stated
  core keywords, this body names 263 distinct strings. `core_keyword` is therefore a
  separate provider keyword-reference layer that RK-03 must preserve distinctly from
  discovery edges; its identity/canonicalization meaning belongs to RK-04 or a later Recipe.
  `synonym_clustering_algorithm` is independently stated on 41 items and null on 39, so it
  must not be presence-coupled to `core_keyword`.
- Metrics-bearing SERP objects preserve provider-native `serp_item_types`; in this Capture
  all 60 include `organic`, while observed counts include `related_searches` 51,
  `ai_overview` 48, `people_also_ask` 43, `video` 21, `images` 14, and
  `discussions_and_forums` 8, plus smaller provider-native categories. These are exact
  one-Capture SERP-composition facts, not general Google prevalence claims or Strategy
  conclusions.
- With `include_clickstream_data=false`, `clickstream_keyword_info` and
  `keyword_info_normalized_with_clickstream` are null on all 80 items. The separate
  `keyword_info_normalized_with_bing` field is also null on all 80 items even though the
  clickstream request flag does not itself define Bing-normalized semantics. This Capture
  does not establish any of their non-null shapes.
- Related Keywords enriched node structures overlap strongly with existing Keyword Overview
  value shapes (`keyword_info`, monthly searches/trend, properties, backlinks, and intent),
  but semantic interchangeability is **not** proven. RK result/item shape, discovered-subject
  grain, SERP testimony, absent `search_partners`, relationship context, and sentinel-clock
  behavior differ materially. Shared low-level parsing helpers may later be appropriate;
  reusing Keyword Overview reconciliation, Observation kinds, or subject identity would make
  an unsupported semantic claim.
- Full-body reconciliation proves that all 80 returned items carry exactly 12
  `monthly_searches` rows over the identical descending Data Period sequence July 2026 through
  August 2025: 960 provider-stated monthly points in this Capture. Fifty monthly points state
  numeric zero. Current `keyword_info.search_volume` differs from the newest monthly value on
  63 of 80 items, so current search volume and monthly-series testimony must remain separate
  facts rather than one being derived from the other. Twelve-row coverage is proven for this
  Capture only, not as a future provider invariant.
- Provider clocks are independently stated by structure: `keyword_info.last_updated_time` on
  all 80 items, `search_intent_info.last_updated_time` on all 80, real
  `avg_backlinks_info.last_updated_time` on 59, and SERP `last_updated_time`/
  `previous_updated_time` according to the SERP states above. Capture/acquisition time,
  structure-local Provider Update Times, and monthly Data Periods are distinct axes and must
  never inherit from one another.

### RK-03 fixture and interpretation limits

The exact protected body is sufficient as primary Conformance-fixture material for a later
strict Related Keywords parser; no second provider exchange is justified by this review. The
fixture exercises all requested depth labels, 80 enriched returned terms, 477
ordered relationship references with repeated and frontier targets, the duplicate seed-data
path, a separate `core_keyword` reference space, nullable relationship/backlink/SERP states,
two sentinel-shaped SERP objects, 960 monthly Data Period points, provider intent and SERP
composition, exact decimal-capable metrics, request-disabled clickstream nulls, and multiple
independent structure-local clocks.

RK-03 must preserve provider testimony without deciding later semantic identity: exact
returned strings; item order; stated `depth`; each `related_keywords` source/array-position/
target relationship; frontier strings without invented enrichment; `seed_keyword_data` and
the depth-0 item as distinct provider paths; stated/null `core_keyword`; numeric zero versus
JSON null; SERP null versus sentinel-shaped object versus metrics-bearing object; exact
provider timestamp strings; current metrics separately from monthly Data Period facts; exact
raw `check_url`; and provider-native category/SERP-type values. Mechanical low-level parser
helpers may be shared only where their semantics genuinely match this contract.

This single Capture does **not** prove universal ordering or tie-break rules, graph/tree
structure, traversal completeness, the meaning of `related_keywords=null`, stable fanout,
provider selection rules, complete corpus coverage, fixed depth cardinality, `limit`/offset
pagination behavior, empty or absent `related_keywords`, duplicate/self-edge behavior,
non-null clickstream/Bing-normalized shapes, SERP/backlink absent branches, provider-error
envelopes, future unknown/additive fields, count-conflict behavior, stable field nullability,
zero-date sentinel meaning, or a general billing formula. Those are synthetic-adversarial or
later-contract questions and do not justify another paid call.

RK-03 must also **not** decide canonical keyword identity, cross-Capture graph union,
frontier-node persistence, `core_keyword` canonicalization, relationship centrality or
importance, RK/Keyword Overview Observation equivalence, Strategy topic membership,
semantic similarity, or consumer recommendations. Those questions belong to RK-04, a later
Recipe/API boundary, or the downstream Strategy layer as applicable.

### Downstream capability implications — preserved for later Strategy work

Without making Strategy conclusions inside Observatory, this Capture demonstrates that this
closed Related Keywords contract can provide materially richer source-attributed inputs than a
flat expansion list: query-neighborhood relationships and repeated-reference structure;
enriched node demand metrics plus twelve monthly Data Periods; provider intent and clustering
references; SERP composition including AI Overview/PAA/video/image/forum testimony; backlinks
context; unresolved frontier terms; and independent update clocks. A future Strategy layer
may use admitted Observatory APIs over those facts for neighborhood exploration, demand-change
analysis, intent/SERP mapping, cluster investigation, or other downstream comparisons. Any
importance score, trend calculation, opportunity inference, topic membership, or action
recommendation remains downstream under D3.

The substantial JSON-shape overlap between RK node measurements and Keyword Overview is also
a future acquisition/consumer-design question: RK may eventually satisfy some downstream
measurement needs without redundant KO acquisition, but this Capture does **not** establish
cross-surface semantic interchangeability. That comparison must be made explicitly before
Strategy or acquisition policy treats one surface as a substitute for the other.

The Steward therefore classifies RK-02 as **Accepted complete Evidence** under this ticket's
technical stop point: the one-shot complete/nonempty Capture exists, local Evidence is clean,
bounded F6 snapshot/restore and receipt round-trip proofs are accepted, restored-body equality
is exact, and the payload assessment is sufficient to begin RK-03. Per project closure
discipline, the ticket remains `review` until [CHAZ] explicitly authorizes closure.

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
