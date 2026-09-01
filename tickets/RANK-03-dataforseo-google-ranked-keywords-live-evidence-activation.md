# RANK-03 — DataForSEO Google Ranked Keywords Live one-shot Evidence activation

**Status:** done — one authorized live exchange completed; bounded F6 protection and independent full-body [CLAUDE]/[GROK]/[GPT] reconciliation accepted 2026-09-01  
**Owner:** [CHAZ] operator / [GPT] Steward verification  
**Blocked by:** none; RANK-02 closed at `5a4903b96b46069ceb5738c441622134ce92cc0c`  
**Draft base:** `5a4903b96b46069ceb5738c441622134ce92cc0c`  
**Live authorization:** granted by [CHAZ], consumed by the single capture-process invocation at activation HEAD `eeece3d02d5a2b9c0852dacf466e86c66d1dbb4b`; no retry or second provider exchange occurred or is authorized  

## Purpose

Exercise the closed RANK-02 DataForSEO Labs Google Ranked Keywords Live adapter exactly once,
preserve the resulting Attempt/Capture as immutable Evidence, inspect the exact provider body,
and complete the accepted bounded encrypted off-host snapshot plus fresh-restore proof before
treating any paid Ranked Keywords Evidence as safely protected.

This is an operator activation ticket. It adds no transport code, parser, Conformance fixture,
Derivation Recipe, Observation, schema/migration, PostgreSQL production state, Recipe selection,
history API, Outcomes/Holdings, Strategy behavior, recommendation logic, pagination,
acquisition cadence, or backup framework.

The first empirical purpose is contract learning: determine what DataForSEO actually returns
for the exact `theconspiratory.com` domain request and preserve the entire body so the later
parser/Recipe/API design can be based on claimed contract plus real Evidence rather than docs
alone.

## Accepted RANK-02 foundation

Adapter contract:

`dataforseo-labs-google-ranked-keywords-live-paid-probe-v1`

Accepted implementation commit:

`8f074ce1eb4fbacd0d4a91737459258bda28a01b`

RANK-02 closure commit:

`5a4903b96b46069ceb5738c441622134ce92cc0c`

The adapter is hardened from birth with a Ranked-local closure-owned transport gate and
fail-closed one-shot Evidence-root scan. RANK-03 reuses it as-is unless the read-only review
finds a concrete activation blocker. Do not refactor working transport merely because this is
the first live Ranked Keywords Capture.

The frozen first live candidate is:

- exact target: `theconspiratory.com`;
- `location_code=2840`;
- `language_code="en"`;
- `ignore_synonyms=false`;
- exact `item_types` order:
  `organic`, `paid`, `featured_snippet`, `local_pack`, `ai_overview_reference`;
- `include_clickstream_data=false`;
- `limit=100`;
- `offset=0`;
- `load_rank_absolute=true`;
- `historical_serp_mode="all"`;
- exact `order_by=["ranked_serp_element.serp_item.rank_group,asc"]`;
- filters absent;
- tag absent;
- exact authorization acknowledgement `50000` micro-USD.

The provider response body may contain SERP titles, descriptions/snippets, XPath, and AI
Overview reference text. [CHAZ] already accepted exact response-body Evidence retention in
RANK-01. This permits immutable Evidence preservation only; it does not authorize API
redistribution, semantic promotion, Strategy conclusions, or additional text acquisition.

## Fresh claimed-contract and pricing recheck — 2026-09-01

The Steward rechecked current official public provider documentation while preparing this
ticket.

Official claimed-contract documentation:

<https://docs.dataforseo.com/v3/dataforseo_labs-google-ranked_keywords-live/>

Official pricing:

<https://dataforseo.com/pricing/dataforseo-labs/dataforseo-google-api>

Current documentation still claims:

- Live endpoint `POST https://api.dataforseo.com/v3/dataforseo_labs/google/ranked_keywords/live`;
- exactly one task per Live API call;
- target may be domain/subdomain/webpage, while the accepted adapter deliberately restricts
  this first contract to its narrower two-label ASCII domain grammar;
- omitting location/language requests all available locales, so this contract keeps exact US
  `2840` and English `en`;
- `ignore_synonyms=false` remains accepted;
- documented item types remain `organic`, `paid`, `featured_snippet`, `local_pack`, and
  `ai_overview_reference`, and the first requested item type can affect returned ordering;
- `include_clickstream_data=false` remains accepted and clickstream-enabled requests are
  documented as double price;
- `limit=100` remains the default and `1000` the maximum; `offset=0` remains default;
- `load_rank_absolute=true` requests result-level `metrics_absolute`;
- `historical_serp_mode` still documents `live`, `lost`, and `all`, with `all` returning both
  currently ranking and previously-ranking-but-lost keywords;
- default ordering remains `ranked_serp_element.serp_item.rank_group,asc`;
- Labs data is described as updated weekly while nested structures may expose independent
  provider update times.

Current official Labs Google pricing lists Ranked Keywords under “all other endpoints” at
`$0.012` per Live task plus `$0.00012` per returned item. At the closed `limit=100`, the
published maximum arithmetic is approximately `$0.024` before any provider pricing change.
The exact `50000` micro-USD acknowledgement therefore retains conservative headroom. It is
not expected cost, invoice truth, a provider-enforced billing cap, standing authorization, or
permission to retry.

The committed Attempt will continue to use RANK-02's frozen pricing-basis string
`dataforseo-labs-google-ranked-keywords-live-2026-09-01`. This ticket's fresh review does not
rewrite that accepted adapter constant.

Official documentation/pricing are mutable claimed contract, not Observatory Evidence.
Recheck them again immediately before final one-shot authorization if execution does not occur
in the same work session as final ticket acceptance.

## Why activation precedes parser/Recipe work

D12 separates claimed contract, empirical Evidence, and Observatory interpretation. RANK-02
deliberately preserves bytes only. RANK-03 must answer empirical questions before any strict
response contract is frozen, including:

- whether the exact frozen request is accepted live;
- actual provider envelope/result shape and additive fields;
- actual `total_count`, `items_count`, returned-item count, response size, and provider cost;
- actual result-level `metrics` and `metrics_absolute` shapes;
- whether the first page contains live and/or lost item testimony;
- actual `ranked_serp_element.is_lost` and `rank_changes` attachment/state shapes when present;
- which requested SERP item types actually appear;
- whether multiple returned items can share keyword text or URLs;
- actual ranked URL/domain/main-domain/relative-URL testimony;
- actual embedded `keyword_data` structure, state/null/empty distinctions, monthly series,
  intent/backlink/SERP subobjects, and independent provider clocks;
- whether `keyword_data.serp_info` is object, array, null, absent, or otherwise differs from
  contradictory documentation;
- whether AI Overview reference testimony appears and its exact text/reference shape;
- actual provider target echo/normalization;
- whether the complete body is suitable as the primary Conformance fixture.

One Capture proves observed testimony for this exact exchange, not provider invariance.
Absence of lost/paid/featured/local/AIO rows in the first returned prefix does not prove those
contract branches do not exist.

## Strategy-readiness review after Capture

After successful protected Evidence exists, the Steward review must inspect the **entire
provider response**, not a convenient sample, and record both:

1. **Observatory fidelity:** what fact/relationship grains, field states, clocks, periods,
   cardinality/completeness boundaries, provider-native identifiers, duplicates, URLs,
   aggregate metrics, and ranking/movement/loss distinctions must be preserved faithfully;
2. **downstream Strategy usefulness:** what the returned testimony could later support for
   ranking visibility, keyword/page relationships, competitor/gap analysis, lost/gained
   visibility, AI Overview reference visibility, demand/rank combinations, and content/topic
   analysis.

Strategy observations remain research input only. Do not implement scoring, opportunities,
recommendations, competitor importance, or SEO/GEO conclusions inside Observatory.

## One-shot and hard-stop semantics

Exactly one capture-process invocation and at most one provider POST may be authorized later.
The first invocation of the paid capture process consumes the human live authorization
regardless of exit code or provider/transport result.

No retry, replacement Evidence root, offset follow-up, pagination, continuation, polling,
changed target/request shape, or second provider exchange is pre-authorized.

If a paid Attempt is committed but no fixture-quality complete Capture/body results, stop.
Preserve and protect all committed paid Evidence, record the honest authorized/unresolved,
partial, no-response, credential-echo, or other result, and require a new later
Steward/Product boundary before any second exchange.

F3 broad rollout and F12 recurring acquisition remain unfired. F7 remains unfired because
this is one fresh Evidence root and one operator process. Ranked Keywords is born with the
hardened closure-owned gate, so this activation does not fire F13.

## Candidate operator record

The final reconciled ticket must freeze before live authorization:

- exact clean activation HEAD and required synchronization state;
- exact fresh Evidence root;
- exact target `theconspiratory.com`;
- exact public capture command;
- exact `50000` acknowledgement;
- fresh official contract/pricing basis;
- exact no-spend preflight and hard stops;
- exact local inspect/status/scrub sequence;
- exact source Attempt/Capture inventory;
- exact encrypted restic remote/repository and RANK-03 tags;
- exact fresh restore path and restored scrub;
- exact Attempt/Capture set equality;
- restored response-body byte-count/SHA-256 equality when complete Evidence exists;
- explicit no retry, replacement root, pagination, continuation, follow-up, or second call.

Candidate fresh Evidence root:

`$HOME/.local/share/observatory/rank03-ranked-keywords-theconspiratory-2026-09-01`

Candidate source inspect file:

`/tmp/rank03-ranked-keywords-response.body`

Accepted bounded manual F6 destination remains the encrypted restic repository via rclone
remote `vedaops-drive:` at `VedaOps Backups/Observatory/evidence-store/repository`, using
password file `$HOME/.config/restic/observatory-password`.

Candidate snapshot tags:

- `observatory-evidence-store`
- `f6-paid-rank03`

This ticket does not authorize changing the backup framework or resuming deferred R2/F6
automation.

## Mandatory independent [GROK] activation review

Before this ticket becomes final, [GROK] must perform a read-only review against the exact
repository state. Public official documentation research is allowed; DataForSEO API calls,
credentials, spend, Evidence creation, repository mutation, PostgreSQL mutation, and push are
forbidden.

At minimum review:

1. RANK-02 implementation/closure and whether the public CLI is actually ready for one live
   invocation without code changes;
2. whether exact `theconspiratory.com` passes the implemented target grammar;
3. whether current provider contract/pricing still support the frozen request and `50000`
   acknowledgement;
4. whether the one-shot/fresh-root/hard-stop semantics accurately match implementation;
5. credential/root ordering and what can remain after every abnormal failure class;
6. whether successful `inspect` is the proper complete/nonempty Capture witness without
   claiming provider semantic success;
7. whether every committed paid Attempt must be inventoried/protected even if no Capture
   exists;
8. whether the accepted manual F6 backup/restore sequence is compatible with the current
   operator tooling and candidate paths/tags;
9. whether any hidden F3/F6/F7/F12/F13, multi-exchange, retention, or synchronization blocker
   exists;
10. whether the full-response post-Capture review explicitly preserves Strategy-usefulness
    analysis downstream without moving Strategy into Observatory;
11. any genuine Product choice still unresolved before final live authorization.

Return `RECOMMENDATION: READY | RECONCILE | STOP`, with exact repository/code references and
concrete ticket corrections. Do not implement or mutate anything.

## Hard boundaries

- This provisional ticket authorizes **zero provider transport and zero spend**.
- No DataForSEO API endpoint may be called during review, including Sandbox, account, Status,
  Locations/Languages, pricing API, or Ranked Keywords itself.
- No real credentials may be accessed or printed during review.
- No Evidence root may be created or mutated during review.
- No parser, fixture, Recipe, Derivation, schema, PostgreSQL production work, API,
  Outcomes/Holdings, Strategy, recurring acquisition, or backup-framework implementation.
- No amend and no push.

## Steward reconciliation of [GROK] activation review — 2026-09-01

[GROK] returned `RECONCILE`. The adapter itself is accepted as live-ready; no source/test
change is required. The blocking gap was operator authority: the provisional ticket named the
steps that later had to be frozen but did not yet freeze exact argv, failure recovery, explicit
Evidence-root checks, or the manual F6 sequence. The Steward accepts that finding and records
the exact activation procedure below.

The review also confirmed that `theconspiratory.com` passes the implemented two-label ASCII
target restriction, the public CLI exposes `--target` and not the private endpoint/body-ceiling
seams, at most one provider POST exists, successful `inspect` is the verified-complete/nonempty
transport witness, current official contract/pricing still support the closed request, and no
F3/F7/F12/F13 or retention blocker exists. No Product choice remains except the later explicit
one-shot live authorization itself.

`AGENTS.md` is updated by Steward authority to list the implemented Ranked Keywords module
entrypoint. Listing the command is not live-call authorization.

## Final operator boundary — frozen before live authorization

A later [CHAZ] live authorization may cover exactly one invocation of this command and no
other provider process:

```bash
cd /home/chaz/projects/vedaops/observatory

uv run python -m observatory.dataforseo_google_ranked_keywords_paid_probe capture \
  --evidence-root "$HOME/.local/share/observatory/rank03-ranked-keywords-theconspiratory-2026-09-01" \
  --target "theconspiratory.com" \
  --authorize-max-micro-usd 50000
```

The live authorization is **not** consumed by ticket review, ticket edits, commit, push,
synchronization, or a failed preflight before this command starts. It is consumed when this
frozen capture process is first invoked, regardless of exit code or provider/transport result.
After process start there is no pre-authorized retry, replacement Evidence root, changed target,
pagination/offset follow-up, continuation, polling, or second provider exchange.

The eventual durable authorization record must name its exact activation HEAD. Before process
start that exact HEAD must be clean on `main` and synchronized to the required remote state.
Any repository mutation after synchronization invalidates the preflight until reconciled.
Nothing in this accepted boundary itself authorizes a push; repository synchronization remains
subject to explicit [CHAZ] push authorization.

## Exact no-spend preflight

Before the paid process starts, perform and record the following without printing secrets:

1. canonical repository is `/home/chaz/projects/vedaops/observatory`;
2. branch is `main`, HEAD equals the later durable authorization-record activation HEAD, and
   the tree is clean;
3. the activation HEAD is synchronized to the remote state required by that authorization;
4. exact Evidence root
   `$HOME/.local/share/observatory/rank03-ranked-keywords-theconspiratory-2026-09-01` does not
   exist;
5. no competing Observatory capture writer or conflicting restic/rclone operation is active;
6. `OBSERVATORY_DATAFORSEO_LOGIN` and `OBSERVATORY_DATAFORSEO_PASSWORD` are both nonempty in
   the same operator shell, checked only by presence/nonempty status and never printed;
7. `$HOME/.config/restic/observatory-password` exists and is readable by the operator without
   printing its contents;
8. rclone remote `vedaops-drive:` and the accepted restic repository remain available through
   the existing operator tooling;
9. the fresh official Ranked Keywords contract/pricing recheck remains current for the work
   session; if execution moves to a later session, recheck before authorization/process start.

Missing credentials fail before root creation. Wrong `50000` acknowledgement also fails before
root creation. After credential/ack gates succeed, `_open_or_create` can create FORMAT before a
later pre-Attempt failure; therefore a FORMAT-only root is possible. If that happens after the
authorized process starts, do **not** delete/recreate the root and do not rerun. Stop for new
Steward/[CHAZ] reconciliation.

The HTTP read timeout is 120 seconds per read phase, not a total wall-clock deadline. Do not
manually interrupt merely because 120 seconds passes. If the authorized process is still
running after five minutes, report the live state to the Steward before intervention. Five
minutes is an escalation threshold, not permission to kill or retry.

## Immediate post-invocation record and hard stop

After the one authorized process starts:

1. record UTC start/end, exit code, exact repo HEAD/tree state, and any emitted Attempt/Capture
   IDs;
2. never rerun the paid capture command under the same authorization;
3. a nonzero exit may print no IDs. If the exact Evidence root exists, recover committed IDs
   read-only from COMMITTED marker parent directories before drawing any sent/unsent conclusion;
4. always run Evidence `status` and `scrub` with the exact explicit `--evidence-root`;
5. if a Capture ID exists, attempt the Ranked byte-exact `inspect`; successful inspect is the
   adapter witness for a verified event-v2 Ranked Capture with `response_complete`, response
   completeness `complete`, and present nonempty body. It is **not** provider semantic-success
   proof; a complete provider-error envelope can inspect successfully;
6. partial/no-response/inspect refusal/credential echo/scrub failure/provider error/unexpected
   transport result is a hard stop, not retry permission;
7. preserve and protect every committed paid Attempt even when no Capture or fixture-quality
   body exists.

If an Attempt is committed without a Capture, treat it as **authorized/unresolved**. It is not
proof that no request was sent and not proof that no charge occurred. Credential echo rejects
before Capture commit and discards the response bytes, but the paid Attempt must still be
inventoried and protected.

A PF-09 body-ceiling case is `response_partial`, not a separate `over_limit` transport state.
`response_partial` and `no_response` Captures remain Evidence and must be protected even though
Ranked `inspect` refuses them as fixture-quality bodies.

## Exact source inventory and local Evidence checks

Use the exact root and inventory paths:

```bash
EVIDENCE_ROOT="$HOME/.local/share/observatory/rank03-ranked-keywords-theconspiratory-2026-09-01"
INVENTORY="/tmp/rank03-ranked-keywords-source-inventory.txt"
BODY_FILE="/tmp/rank03-ranked-keywords-response.body"

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

uv run python -m observatory.evidence status --evidence-root "$EVIDENCE_ROOT"
uv run python -m observatory.evidence scrub --evidence-root "$EVIDENCE_ROOT"
```

`status` proves only that the format-2 store opens. `scrub` verifies the commitment-claiming
directories it discovers under the accepted Evidence contract. Neither proves a provider
semantic success or complete Capture.

When a Capture ID exists, the only fixture-quality body witness is:

```bash
uv run python -m observatory.dataforseo_google_ranked_keywords_paid_probe inspect \
  --evidence-root "$EVIDENCE_ROOT" \
  --capture-id "<CAPTURE_ID>" \
  > "$BODY_FILE"

wc -c "$BODY_FILE"
sha256sum "$BODY_FILE"
```

If inspect fails, do not fabricate a body file and do not rerun the provider call. Continue
with inventory/protection of whatever paid Evidence exists.

## Bounded manual F6 protection — exact command skeleton

Reuse the accepted manual D10/RK-02 protection spine; build no backup automation.

Set the accepted remote repository without printing secrets:

```bash
export RESTIC_REPOSITORY="rclone:vedaops-drive:VedaOps Backups/Observatory/evidence-store/repository"
export RESTIC_PASSWORD_FILE="$HOME/.config/restic/observatory-password"
```

After the source root is quiescent, status/scrub is clean enough to continue, and the exact
source inventory has been recorded, create one encrypted non-destructive snapshot containing
the complete Evidence root plus the outside-root inventory:

```bash
restic backup \
  "$EVIDENCE_ROOT" \
  "$INVENTORY" \
  --tag observatory-evidence-store \
  --tag f6-paid-rank03
```

Record the full snapshot ID and non-secret command receipt. No destructive prune/forget action
belongs to RANK-03.

Restore that exact snapshot into a new temporary directory:

```bash
RESTORE_BASE="$(mktemp -d /tmp/rank03-ranked-keywords-restore.XXXXXX)"
restic restore "<SNAPSHOT_ID>" --target "$RESTORE_BASE"
```

Because restic restores absolute source paths beneath the chosen target, define and verify the
restored Evidence root explicitly from the restored path produced by this snapshot; do not
silently substitute another local source root. Run `observatory.evidence status` and `scrub`
against that exact restored Evidence root.

Recompute a sorted restored Attempt/Capture inventory using the same COMMITTED-parent algorithm
as the source inventory and require exact Attempt-set and Capture-set equality with the source.
Hash both inventories and preserve the comparison outside both Evidence roots.

If source `inspect` produced a complete body, run the same Ranked `inspect` against the restored
Capture and record `wc -c` plus SHA-256. Require exact source/restored byte count and SHA-256,
and preferably byte-for-byte equality (`cmp`) before the paid Evidence is considered protected.

The final activation closure must record at minimum:

- exact activation HEAD and process timestamps/exit;
- exact Attempt/Capture inventories and inventory SHA-256;
- source status/scrub result;
- source body byte count/SHA-256 when inspect succeeds;
- full restic snapshot ID and tags;
- fresh restore path and restored status/scrub result;
- exact source/restored Attempt-set and Capture-set equality;
- restored body byte count/SHA-256 equality when a complete body exists;
- non-secret backup/restore receipt identifiers/hashes under the accepted off-host receipt
  convention;
- explicit confirmation that no retry, replacement root, pagination, continuation, follow-up,
  changed target, or second provider call occurred.

Routine F6 automation remains deferred. This manual proof protects this one paid Evidence root
only.

## Post-protection full-response review

Only after the source and fresh-restored Evidence verify may the project perform the deep
payload review. Inspect the **entire exact provider body**, not a convenient row sample.

The review has two distinct outputs:

1. **Observatory fidelity** — identify the provider's actual fact/relationship grains,
   requested/returned subjects, target/keyword/page/URL identities, aggregate versus item-level
   testimony, live/lost/movement distinctions, field states, null/empty/zero/absent branches,
   clocks/Data Periods, provider-native identifiers, duplicates/order/cardinality,
   `total_count`/`items_count`/limit completeness boundaries, unknown/additive fields, exact
   response size/cost, and which documented branches remain unobserved;
2. **future Strategy usefulness** — record what the Evidence could later let a downstream
   Strategy consumer ask about ranking visibility, keyword↔page relationships, competitor/gap
   analysis, gained/lost visibility, AI Overview references, demand+rank combinations, and
   content/topic patterns.

The second output is research input about consumer usefulness only. Observatory must not emit
opportunity rankings, scores, recommendations, competitor importance, campaign tactics, or
SEO/GEO conclusions. Those remain downstream Strategy-layer work.

One Capture proves the exact observed exchange only. It cannot prove provider invariance,
full-corpus completeness, presence of every requested SERP type, universal lost-item shape,
future billing formula, 32 MiB headroom, device/OS of the Labs index, a fixed previous-check
interval, or any Strategy conclusion. Missing item types or `is_lost=true` rows in the first
100-row prefix are not evidence that those branches do not exist.

## [CHAZ] one-shot live authorization — 2026-09-01

[CHAZ] explicitly authorizes exactly one RANK-03 DataForSEO Labs Google Ranked Keywords Live
provider invocation under the frozen activation contract above, with:

- exact target `theconspiratory.com`;
- exact `location_code=2840` and `language_code="en"`;
- exact five-item `item_types` order already frozen by RANK-02;
- `ignore_synonyms=false`, `include_clickstream_data=false`, `limit=100`, `offset=0`,
  `load_rank_absolute=true`, and `historical_serp_mode="all"`;
- exact ordering `ranked_serp_element.serp_item.rank_group,asc`;
- filters/tag absent;
- exact operator acknowledgement `50000` micro-USD;
- exactly one invocation of the frozen public capture command and at most one provider POST;
- no retry, replacement Evidence root, pagination, offset follow-up, continuation, polling,
  changed target/request shape, or second provider exchange.

[CHAZ] also explicitly authorizes the Git push needed to synchronize the durable authorization
record to `origin/main`. This is push authorization for the authorization-record synchronization
only; it does not create standing push authority for later work.

The authorization was issued while `main` was clean at
`04f352b9990b8884ed6075b62aa3585323c43b0d`. It is **not consumed** by this ticket edit,
its governed commit, the authorized synchronization push, or any failed no-spend preflight
before the frozen capture command starts. The first invocation of that frozen capture process
consumes the one-shot live authorization regardless of exit code or provider/transport result.
After process start, no failure class authorizes retry or a replacement root.

The clean commit containing this durable authorization record becomes the RANK-03 activation
HEAD once it is synchronized to `origin/main`. Record that concrete HEAD in the operator
preflight/output and later closure. Any repository mutation after synchronization invalidates
the activation preflight and requires Steward reconciliation before the paid process starts.

## Activation gate — satisfied

The durable authorization record was committed at activation HEAD
`eeece3d02d5a2b9c0852dacf466e86c66d1dbb4b`, synchronized to `origin/main` under the narrow
[CHAZ] authorization above, and verified clean before the paid process started. The no-spend
preflight passed every frozen gate. The one-shot live authorization was then consumed exactly
once. Nothing below reopens transport authority.

## Steward live Evidence and F6 closure — 2026-09-01

The one authorized capture process started at `2026-09-01T05:32:46Z`, ended at
`2026-09-01T05:32:49Z`, returned exit code `0`, and left the repository clean at activation
HEAD `eeece3d02d5a2b9c0852dacf466e86c66d1dbb4b`.

Committed paid Evidence:

- Attempt `af0b78285bf7dd7043eaade7307de86dccb607d2e3e88b895bc322d3dac5f341`;
- Capture `cd5152c65e27b24610606b545ce014121a72562328df27f3d91e3ce33cf6c3f1`;
- source Evidence status `format-2 ok` and source scrub clean;
- exact inspected provider body `390955` bytes;
- body SHA-256
  `5b0e7cb6a03a921039a2845c62bd6a91eba9d61e2b54240e9af15414ba1fbc84`;
- independently recorded source Attempt/Capture inventory SHA-256
  `9fb185b668675f8ee6fe7d39085e93558d5728e2f03d17f0fc1371f2b40a0830`.

Exactly one Attempt and one Capture exist in this RANK-03 Evidence root. No retry,
replacement root, pagination/offset follow-up, continuation, polling, changed target, or second
provider exchange occurred.

### Accepted bounded F6 proof

The existing encrypted restic repository `52a88583` through `vedaops-drive:` created snapshot
`df746a45a69c65e456e108626a530d794fc21ba9b8d80cf759226dd05a8412a3`, tagged
`observatory-evidence-store` and `f6-paid-rank03`. A fresh restore into
`/tmp/rank03-ranked-keywords-restore.VO4eZG` opened as `format-2 ok` and scrubbed clean.

Source inventory, snapshot-restored inventory, and independently recomputed restored inventory
were byte-identical and all had the same inventory SHA-256 above. The restored Capture
inspected successfully as exactly `390955` bytes with the same body SHA-256 as the source, and
the source/restored body files were byte-identical.

Non-secret receipt files were copied to the accepted off-host `receipts/` and
`restore-proofs/` folders and downloaded again to fresh local files. Each remote round trip
was byte-identical:

- `rank03-ranked-keywords-backup-df746a45.ok.json` SHA-256
  `1c512d08e981a78079267457243a23c92daf44c88f1a41ef685ee7000a6c16d0`;
- `rank03-ranked-keywords-restore-df746a45.ok.json` SHA-256
  `c7da5e659336d1042c89cc1ed0b3a4113b4374fb0461ce358905ae23dee621a9`.

This satisfies the accepted bounded manual F6 requirement for this paid Evidence root. It does
not complete routine F6 automation.

## Independent full-body reconciliation — accepted 2026-09-01

After F6 protection, independent read-only [CLAUDE] and [GROK] reviews plus a separate
[GPT] Steward census inspected the same exact protected `390955`-byte body. Both independent
reviewers returned `READY`, found the Capture sufficient primary Conformance material, and
recommended no second provider call. The Steward reconciles their reports below against the
actual activation contract and existing Related Keywords precedent.

Where reviewer analyses diverged, no new semantic invariant is accepted. In particular, the
returned array is observed as nondecreasing by `rank_group`, consistent with the requested
ordering, but tie-break semantics inside equal-rank groups remain unproven. Likewise, observed
formula-like correlations among provider-modeled traffic values are not promoted into
Observatory derivation rules.

### Verified provider envelope, request, cost, and completeness

- Envelope version is `0.1.20260831`; root and task both report `status_code=20000` /
  `status_message="Ok."`; `tasks_count=1`, `tasks_error=0`, and task `result_count=1`.
- Provider task ID is `09010532-1463-0381-0000-8f2c825ce89d`; task path is exactly
  `["v3","dataforseo_labs","google","ranked_keywords","live"]`.
- Root/provider cost and task cost are both `0.024`. For this Capture only, that agrees with
  the published calculation `0.012 + (100 * 0.00012)`. This is billing testimony for this
  exchange, not a universal billing formula.
- Task request echo agrees with the frozen RANK-02 request: exact target
  `theconspiratory.com`, US `2840`, English `en`, `ignore_synonyms=false`, exact five requested
  item types, clickstream disabled, `limit=100`, `offset=0`, absolute metrics requested,
  `historical_serp_mode="all"`, and rank-group-ascending order.
- Result echo preserves `target=theconspiratory.com`, `location_code=2840`,
  `language_code="en"`, and `se_type="google"`.
- Provider claims `total_count=248` while `items_count=100` and exactly 100 item objects were
  returned. The body is therefore a bounded returned prefix of a larger provider corpus, not
  the site's complete row-level Ranked Keywords set.
- Result-level `metrics.organic` position buckets account for all 248 corpus rows. The first
  returned page contains all 9 rows in rank-group 11–20, all 18 in 21–30, all 43 in 31–40,
  and 30 of the provider's 59 rows in 41–50. Thus this exact prefix is empirically complete
  through `rank_group <= 40` and partial within 41–50. The remaining 148 corpus rows have no
  row-level testimony in this Capture.
- Returned `rank_group` is nondecreasing, with observed range 14–46. Returned
  `rank_absolute` ranges 18–57 and is not the requested sort key. No universal tie-break rule
  is proven.

### Aggregate and ranking testimony must remain distinct

- Both result-level aggregate families contain the five requested type keys: `organic`,
  `paid`, `featured_snippet`, `local_pack`, and `ai_overview_reference`.
- `metrics.organic` includes corpus `count=248`, ETV, estimated paid-traffic cost, movement
  counts, and position buckets. Its position buckets sum to 248.
- `metrics_absolute.organic` has a different shape: it does not state `count`, ETV, or
  estimated paid-traffic cost. Its 1–100 position buckets sum to 244, not 248. Four corpus
  rows therefore do not appear in those absolute-rank buckets. The reason is not available as
  row-level testimony in this returned prefix and must not be invented.
- All four non-organic requested aggregate families are present and zero-valued for their
  ranking/movement testimony in both aggregate variants. Present zero is materially distinct
  from an absent family.
- All 100 returned ranked items have `serp_item.type="organic"` and
  `ranked_serp_element.is_lost=false`.
- All 100 returned `rank_changes` objects state `is_new=true`, `is_up=false`,
  `is_down=false`, and `previous_rank_absolute=null`; corpus aggregates state organic
  `is_new=248`, `is_up=0`, `is_down=0`, `is_lost=0`.
- Provider `is_new`/`is_up`/`is_down`/`is_lost` is provider-internal comparison testimony,
  not Observatory Capture-to-Capture change and not proof that the domain never ranked before.
  `historical_serp_mode="all"` exercised the request mode but this Capture contains no lost
  row shape.
- `serp_item.position` is the string `"left"` on all returned rows. It is SERP layout/pane
  testimony, not a ranking number and must not be conflated with `rank_group` or
  `rank_absolute`.

### Identity and occurrence testimony

- All 100 returned keyword strings are distinct in this prefix. Exact keyword text remains
  occurrence testimony; near-duplicate spelling/hyphenation variants must not be normalized
  away by the parser.
- The 100 rows reference 57 distinct absolute URLs. One URL can rank for multiple returned
  keywords, so URL and keyword are not interchangeable identities.
- Provider `domain` preserves two hosts: `theconspiratory.com` on 75 rows and
  `www.theconspiratory.com` on 25. Provider `main_domain` is `theconspiratory.com` on all 100.
  URL host agrees with `domain` in this Capture. The two provider paths must remain distinct;
  collapsing `www` and apex would invent canonical-page identity.
- There are 55 distinct `relative_url` values. At least `/theory/atlantis` and
  `/theory/denver-airport` occur under both apex and `www`, proving that `relative_url` alone
  is not an occurrence/page identity.
- Page/query multiplicity is real testimony: a ranked URL may serve several returned keyword
  rows. The strongest returned absolute-URL multiplicity is nine keywords; path-level grouping
  can be larger when apex and `www` are collapsed, which Observatory must not do implicitly.
- `keyword_properties.core_keyword` is non-null on 35 returned rows and is never equal to its
  row keyword in this Capture. It is a separate provider clustering/reference field, not a
  canonical keyword foreign key or an Observatory identity decision.
- Provider item array position may be preserved as occurrence/order testimony but must not be
  promoted into semantic identity.

### Embedded keyword testimony

- Every returned item contains a `keyword_data` object with the same observed twelve-key
  family, including `keyword_info`, `keyword_properties`, `search_intent_info`,
  `avg_backlinks_info`, `serp_info`, and the three clickstream/Bing-normalized paths.
- Every `keyword_info.monthly_searches` array contains 12 points: 1200 monthly provider facts
  across the 100 returned rows. The rows do not share one Capture-wide monthly window: 62 use
  July 2026 through August 2025, while 38 use June 2026 through July 2025. Across this body,
  13 distinct `(year, month)` Data Periods occur. Monthly Data Period is therefore row-local
  testimony, not a single result-level period.
- Current `keyword_info.search_volume` differs from the newest monthly point on 81 of 100
  rows. Current volume and monthly-series facts must remain distinct and neither may be
  derived from the other.
- `competition_level` is `LOW` on all 100 returned rows while numeric `competition` includes
  zero; null, zero, and categorical state must remain distinct. CPC and top-of-page-bid fields
  are independently nullable and must not be modeled as one all-or-nothing commercial-metrics
  state.
- `keyword_properties.keyword_difficulty` is numeric, including real zero values, and agrees
  with the duplicated `ranked_serp_element.keyword_difficulty` path on all 100 rows. Agreement
  in one Capture does not authorize path collapse.
- Detected language is not request-language identity: the provider classifies 94 rows as `en`
  and six as other detected languages while the request/result locale remains English.
- Provider main-intent vocabulary observed here is `informational` (89), `navigational` (9),
  `transactional` (1), and `commercial` (1). `foreign_intent` is separately nullable/array
  testimony.
- `keyword_data.serp_info` is an object on all 100 real rows in this Capture, resolving the
  contradictory documentation question for this fixture only. Its non-object/null/absent
  branches remain unobserved and synthetic-testable.
- The three clickstream/Bing-normalized keyword-data paths are JSON null on all 100 rows under
  `include_clickstream_data=false`. Their non-null shapes remain unobserved.
- `avg_backlinks_info` is present on all 100 rows and is separate from
  `serp_item.backlinks_info`, which is null on all 100. Same-looking backlink/rank words on
  different provider paths must not be reconciled by name.

### SERP composition is not target participation

- `serp_item_types` is provider SERP-composition testimony for the query's SERP and remains an
  ordered provider-native list; it is not the target's ranked-element type set.
- `ai_overview` appears in `serp_item_types` on 80 of the 100 returned organic-query SERPs,
  while the target-level `ai_overview_reference` aggregate family states zero matching rows
  across the full 248-row corpus. These facts are complementary and must not be collapsed into
  either “the target has AI Overview visibility” or “there is no AI Overview testimony.”
- `featured_snippet` appears in SERP-composition testimony on four returned query SERPs while
  the target's `featured_snippet` aggregate family is zero across the full corpus. This is a
  second concrete proof that SERP feature presence differs from target participation.

### Independent Provider Update Times and Data Periods

This one Capture joins several provider datasets with materially different clocks:

- Observatory acquisition/Capture occurred on 2026-09-01;
- ranked-SERP `last_updated_time`: 2026-07-10 through 2026-07-19;
- ranked-SERP `previous_updated_time`: 2026-04-09 through 2026-06-02;
- `keyword_info.last_updated_time`: 2026-07-10 through 2026-08-26;
- `search_intent_info.last_updated_time`: 2026-04-24 through 2026-05-08;
- `avg_backlinks_info.last_updated_time`: 2026-07-10 through 2026-07-19;
- monthly `(year, month)` facts span the two row-local 12-month windows above.

Capture time must not be exposed as ranking “as-of” time. No generic Provider Update Time may
be inherited across structures. `previous_updated_time` remains separate testimony even though
all returned `previous_rank_absolute` values are null. Relative prose such as `pre_snippet`
`"N days ago"` is not a provider timestamp and must not be interpreted against Capture time.

### Null, zero, empty, absent, and opaque provider values

The body exercises present JSON null and numeric zero as distinct states inside the same
families. It does not exercise absent optional keys or empty arrays for the major nullable
children reviewed here. Strict parsing must preserve those distinctions and use synthetic
adversarial variants for unobserved branches rather than inventing provider invariants.

Provider-native strings, category IDs, SERP feature names, URLs, host/domain fields, and
clustering/intent vocabularies remain attributed provider testimony. They are not an invitation
to silently normalize identities, de-duplicate ordered lists, or define Observatory enums more
narrowly than the accepted contract warrants.

## Candidate modeling implications — not a schema freeze

The reconciled Evidence demonstrates at least the following distinct testimony grains for
later design review:

1. result/request context and corpus-completeness testimony;
2. target-level per-SERP-type `metrics` aggregate testimony;
3. target-level per-SERP-type `metrics_absolute` aggregate testimony with a distinct shape;
4. returned ranked keyword/URL occurrence testimony, including exact provider order and ranks;
5. ranked-SERP context and composition testimony with its own clocks;
6. embedded Ranked-local keyword enrichment testimony;
7. monthly search-volume Data Period facts;
8. ordered/multiplicity-preserving child vocabularies where provider arrays carry occurrence
   testimony.

These are candidate semantic grains, not accepted PostgreSQL tables or final Observation kinds.
The later Recipe review must decide the smallest faithful decomposition, identities, relations,
typed Field/FieldState use, admission rules, and API shape. Mechanical low-level parsing may be
shared with Keyword Overview/Related Keywords where the byte/value semantics genuinely match;
Ranked Keywords Observation identity must remain Ranked-local unless a later reviewed contract
proves equivalence.

Any history/API consumer must be able to distinguish at minimum provider `total_count=248`,
provider `items_count=100`, actual returned item count, request `limit=100`, `offset=0`, and the
requested/observed sort context. It must never present the returned prefix as the complete
corpus. Aggregate facts must be explicitly corpus-scoped rather than visually attached to the
100 returned rows as if computed only from them.

## Downstream capability implications — preserved for later Strategy work

Without moving scoring or recommendations into Observatory, this Capture demonstrates that a
future Strategy consumer could use admitted Ranked testimony to investigate:

- which exact queries the domain is reported as ranking for and which exact URL/host occurrence
  received the ranking;
- proximity to page one using distinct `rank_group` and `rank_absolute` facts;
- page/query clusters and host fragmentation while keeping apex/`www` identity explicit;
- demand, intent, difficulty, CPC/competition, and monthly history alongside ranking position;
- overlap between the Related Keywords discovery neighborhood and actual target participation;
- SERP feature context, including organic presence on AI-Overview-bearing SERPs versus actual
  target `ai_overview_reference` participation;
- later cross-surface comparisons with Google Organic, Keyword Overview, Search Mentions,
  Target Metrics, Historical LLM Mentions, or future competitor surfaces, provided their
  distinct clocks and semantics remain explicit;
- true gained/lost Observatory visibility only after repeated Ranked Captures exist.

Possible “cannibalization,” opportunity, competitor gap, topic importance, campaign priority,
SEO/GEO score, or recommendation remains downstream inference. Provider `is_new` is not a
substitute for Observatory longitudinal change.

## Fixture sufficiency and unproven limits

The exact protected body is accepted as strong primary Conformance material for the next strict
Ranked parser boundary. It exercises a real 100-of-248 truncation, both aggregate variants,
explicit zero requested types, 100 organic ranked occurrences, apex/`www` host divergence,
multi-keyword pages, distinct current/monthly demand testimony, two monthly windows, provider
intent/difficulty/backlink/SERP context, ordered SERP-composition vocabularies, request-disabled
clickstream nulls, and independent structure-local clocks.

This single Capture does **not** prove:

- row-level testimony for the 148 unreturned corpus rows or offset/pagination behavior;
- stable `total_count`, returned ordering tie-breaks, or future limit behavior;
- `is_lost=true`, non-null previous-rank, provider up/down, or other lost-item shapes;
- paid, featured-snippet, local-pack, or AI-Overview-reference ranked-item polymorphism;
- non-null clickstream/Bing-normalized, rating, links, item-backlinks, or other unobserved
  optional shapes;
- absent-key/empty-array behavior, alternate competition levels, alternate layout positions,
  shorter/longer monthly arrays, sentinel timestamps, subdomain/page targets, other locales,
  `ignore_synonyms=true`, provider-error envelopes, or future additive fields;
- semantic equivalence with Keyword Overview, Related Keywords, Google Organic, or any AI
  surface;
- canonical page/host identity, core-keyword canonicalization, competitor relationships, or
  any Strategy conclusion;
- a universal provider billing formula or stable weekly comparison interval.

The 148 unreturned rows are historically unavailable at row level for this exact provider
epoch, but the independent reviews agree that they are not required to learn this contract:
the best-ranked prefix is already fixture-rich and full-corpus aggregate testimony is preserved.
Another live request is therefore not justified by RANK-03. Any future deeper acquisition is a
new Product/acquisition-policy question under D12 with new provenance and authorization.

## Closure decision and next boundary

[CLAUDE] and [GROK] independently return `READY`; the Steward accepts their converged Evidence
findings, preserves the explicit limits above, and closes RANK-03 as `done`.

No `src/` or `tests/` behavior changes in this closure. The next bounded Ranked Keywords work
is **RANK-04: strict Ranked Keywords response parser plus frozen primary Conformance fixture**
derived from these exact verified bytes, with synthetic adversarial mutations for the unproven
branches above. RANK-04 must not silently freeze the later Recipe, Observation identity,
PostgreSQL schema, history API, canonical host/page identity, Strategy scoring, recurring
acquisition, or another provider exchange.

Only after the strict parser/fixture boundary is reviewed and accepted should a separate
Ranked Recipe/Derivation/persistence ticket decide the smallest faithful testimony grains and
relations; a later separately reviewed read/history API then exposes the admitted contract.
No additional provider call or push is authorized by this closure.
