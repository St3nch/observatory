# RANK-03 — DataForSEO Google Ranked Keywords Live one-shot Evidence activation

**Status:** provisional review — awaiting independent [GROK] read-only activation review  
**Owner:** [CHAZ] operator / [GPT] Steward verification  
**Blocked by:** none; RANK-02 closed at `5a4903b96b46069ceb5738c441622134ce92cc0c`  
**Draft base:** `5a4903b96b46069ceb5738c441622134ce92cc0c`  
**Live authorization:** not yet granted; this ticket draft authorizes zero provider calls and zero spend  

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

## Next gate

After independent review, the Steward reconciles the activation boundary. Only then may
[CHAZ] separately authorize exactly one live invocation from a named clean activation HEAD.
That later authorization must be explicit and durable before the paid process starts.
