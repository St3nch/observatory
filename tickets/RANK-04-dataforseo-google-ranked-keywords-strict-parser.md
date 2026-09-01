# RANK-04 — DataForSEO Google Ranked Keywords strict parser and RANK-03 Conformance fixture

**Status:** implemented by the designated Writer from the authorized base; awaiting Steward review and [CHAZ] full-suite integration validation  
**Owner:** [CLAUDE] designated Writer / [GPT] Steward review / [GROK] independent reviewer  
**Blocked by:** none; RANK-03 closed at `fbd53534aea47f114822e071c178b3ae1e378055`  
**Draft base:** `fbd53534aea47f114822e071c178b3ae1e378055`  
**Provider authority:** zero calls, zero spend; protected RANK-03 Evidence only  

## Purpose

Build the zero-network interpretation boundary for the closed adapter
`dataforseo-labs-google-ranked-keywords-live-paid-probe-v1`.

Promote the already protected RANK-03 response bytes once through the existing verified
read-only inspector into one frozen deterministic Conformance fixture, then parse those exact
bytes into a strict typed in-memory Ranked Keywords representation that retains the provider's
result/corpus summaries, returned occurrence order, keyword/page/host testimony, aggregate and
absolute-rank distinctions, field states, SERP composition, keyword enrichment, and independent
time/Data-Period axes without inventing Recipe or Strategy semantics.

RANK-04 does **not** create a Derivation Recipe, repository Outcome, Observation kind or natural
identity, PostgreSQL schema or rows, derive command, Recipe selection, read/history API,
canonical host/page identity, cross-surface normalization, competitor model, Strategy score or
recommendation, recurring acquisition, pagination/offset continuation, or another provider
exchange. Those remain separate later boundaries.

[CHAZ] designates [CLAUDE] as the one RANK-04 implementation Writer. [GROK] is the independent
adversarial reviewer. This designation does **not** authorize implementation: [CLAUDE] must first
perform the read-only code-first ticket review below, [GROK] must independently review the same
clean ticket HEAD, and the Steward must reconcile both before [CHAZ] separately authorizes
implementation from an exact clean accepted-ticket HEAD. Ticket review, fixture planning, and
Steward edits authorize no source/test mutation by the Writer and no push.

## Authority and accepted foundation

- VISION and VOCABULARY Evidence, Conformance, Derivation, Observation, Provenance, Provider
  Update Time, Data Period, and Strategy boundaries.
- D11 — strict provider parsing, exact numerics, field-state preservation, time-axis separation,
  and semantic reconciliation restraint.
- D12 — claimed contract, bounded real Evidence, Conformance fixture, parser, and Recipe are
  distinct; one Capture proves observed testimony, not invariance.
- D14 consumer-resource semantics remain outside this parser boundary.
- `docs/specs/capture-event-v2.md` verified complete-body/provider-interpretation boundary.
- RANK-01 closed the empirical activation/request contract.
- RANK-02 closed the Evidence-only one-shot adapter and frozen request bytes.
- RANK-03 closed the one authorized live exchange, exact body inspection, bounded encrypted
  F6 protection/fresh restore, and independent [CLAUDE]/[GROK]/[GPT] whole-body reconciliation.
- RK-03, AI-04, AI-10, and AI-15 are strict-parser precedents. Related Keywords supplies the
  closest Labs keyword-enrichment value shapes; Search Mentions supplies returned-prefix and
  occurrence precedent. Neither surface supplies Ranked Keywords Observation identity or
  reconciliation semantics.
- PF-11 Google Organic is a structural **negative precedent** for Ranked SERP items. Do not
  import its closed item-type/position vocabularies, placement-uniqueness rules, keyword/text
  normalization, or placement identity. RANK-03 proves repeated `rank_group` and
  `rank_absolute`, open SERP-feature vocabulary, exact near-duplicate keyword strings, and
  apex/`www` host testimony that those Organic rules would reject or collapse.

RANK-04 authorizes no provider, DNS, account, credential, restic, rclone, pricing, public-network,
Evidence mutation, or PostgreSQL activity.

## Exact protected fixture provenance

The fixture is copied once from already protected RANK-03 Evidence through the existing
read-only Ranked Keywords inspector. Do not copy from `/tmp`, pretty-print, reserialize,
canonicalize, or otherwise regenerate the provider body.

- Evidence root:
  `/home/chaz/.local/share/observatory/rank03-ranked-keywords-theconspiratory-2026-09-01`;
- Attempt:
  `af0b78285bf7dd7043eaade7307de86dccb607d2e3e88b895bc322d3dac5f341`;
- Capture:
  `cd5152c65e27b24610606b545ce014121a72562328df27f3d91e3ce33cf6c3f1`;
- exact response bytes: `390955`;
- exact response SHA-256:
  `5b0e7cb6a03a921039a2845c62bd6a91eba9d61e2b54240e9af15414ba1fbc84`.

Required fixture path:

`tests/fixtures/dataforseo_google_ranked_keywords_rank03.json`

The one-time fixture promotion command is frozen to inspector stdout and must retain an atomic
temporary-file/length/hash guard:

```bash
set -euo pipefail

FIXTURE=tests/fixtures/dataforseo_google_ranked_keywords_rank03.json
TMP="${FIXTURE}.tmp"

test ! -e "$FIXTURE"
rm -f "$TMP"
trap 'rm -f "$TMP"' EXIT

uv run python -m observatory.dataforseo_google_ranked_keywords_paid_probe inspect \
  --evidence-root "$HOME/.local/share/observatory/rank03-ranked-keywords-theconspiratory-2026-09-01" \
  --capture-id cd5152c65e27b24610606b545ce014121a72562328df27f3d91e3ce33cf6c3f1 \
  > "$TMP"

test "$(wc -c < "$TMP")" -eq 390955
test "$(sha256sum "$TMP" | awk '{print $1}')" = \
  5b0e7cb6a03a921039a2845c62bd6a91eba9d61e2b54240e9af15414ba1fbc84

mv "$TMP" "$FIXTURE"
trap - EXIT

test ! -e "$TMP"
wc -c "$FIXTURE"
sha256sum "$FIXTURE"
```

The committed fixture must be byte-identical to verified inspector stdout. Tests independently
prove exact length and SHA-256. After the one-time promotion, ordinary tests must not depend on
the operator Evidence root or any `/tmp` body file. Provider wire bytes are not RFC 8785/JCS
material; their identity is the exact recorded SHA-256 above.

## Frozen verified Attempt context

The parser accepts the exact verified Attempt parameter object plus response-body bytes. The
complete parameter key set is closed to the RANK-02 adapter contract:

- `contract=RANKED_KEYWORDS_ADAPTER_CONTRACT`;
- one adapter-valid target domain string; only `target` varies within the existing RANK-02
  grammar;
- `location_code=2840`;
- `language_code="en"`;
- ordered `item_types=["organic","paid","featured_snippet","local_pack",
  "ai_overview_reference"]`;
- `ignore_synonyms=false`;
- `include_clickstream_data=false`;
- `limit=100`;
- `offset=0`;
- `load_rank_absolute=true`;
- `historical_serp_mode="all"`;
- ordered `order_by=["ranked_serp_element.serp_item.rank_group,asc"]`.

No filters or tag parameter is part of this adapter parameter object. The parser must not edit
`capture_event.py` merely to share target validation; the designated Writer must inspect the
existing adapter validator and either reuse a semantics-free exported constant/helper if one
already exists or duplicate the exact bounded grammar locally as precedent requires.

Provider `task.data` is typed echo testimony, never request authority. Result target/locale/
surface context is independently typed testimony. A well-typed disagreement with verified
Attempt parameters remains visible in parser IR for later Recipe reconciliation unless a final
review identifies a true adapter-local typing invariant that must fail earlier.

## Verified RANK-03 testimony the parser must retain

The exact protected body establishes one provider-successful one-task/one-result response:

- envelope version `0.1.20260831`, root/task status `20000` / `Ok.`, root duration
  `1.4853 sec.`, task duration `1.4599 sec.`, and exact Decimal-valued costs `0.024`;
- task ID `09010532-1463-0381-0000-8f2c825ce89d` and path
  `["v3","dataforseo_labs","google","ranked_keywords","live"]`;
- exact frozen request echo plus provider-added `api`, `function`, and `se_type` fields;
- result `target=theconspiratory.com`, `location_code=2840`, `language_code="en"`,
  `se_type="google"`, `total_count=248`, `items_count=100`, and exactly 100 item objects;
- the returned body is a bounded rank-group-ordered prefix of a larger provider corpus. It is
  not row-level testimony for the remaining 148 matches.

The full-corpus aggregate and returned-prefix facts are materially distinct:

- `metrics.organic.count=248`; its rank-group position buckets sum to 248;
- the returned prefix contains all 9 corpus rows in rank-group 11–20, all 18 in 21–30,
  all 43 in 31–40, and 30 of 59 in 41–50;
- `metrics_absolute.organic` has a different object shape and its 1–100 buckets sum to 244;
  it does not state `count`, ETV, or estimated paid-traffic cost;
- the parser must not require aggregate bucket sums to equal one another or derive missing
  corpus rows from the returned prefix;
- all four requested non-organic aggregate families are present with zero ranking/movement
  testimony. Present zero is not absence.

All 100 returned rows are organic ranked occurrences. Observed ranges are `rank_group=14..46`
and `rank_absolute=18..57`; `rank_group` is nondecreasing in provider order, while tie-break
semantics remain unproven. `serp_item.position="left"` on all 100 is layout testimony, not rank.

Provider movement/loss paths must remain distinct and unreconciled:

- `ranked_serp_element.is_lost=false` on all 100;
- every `rank_changes` object states `is_new=true`, `is_up=false`, `is_down=false`, and
  `previous_rank_absolute=null`;
- full-corpus organic aggregates state `is_new=248`, `is_up=0`, `is_down=0`, `is_lost=0`;
- every returned row nevertheless has non-null `previous_updated_time`.

This is provider-internal comparison testimony, not Observatory Capture-to-Capture change and
not proof that a keyword never ranked before. The parser must preserve contradictory paths rather
than harmonize them.

Identity/occurrence testimony in the returned prefix includes:

- 100 distinct keyword strings in this fixture, but duplicate keyword occurrences remain a
  synthetic-supported parser possibility and must not be collapsed;
- 57 distinct absolute URLs and 55 distinct `relative_url` strings;
- provider `domain=theconspiratory.com` on 75 rows and
  `domain=www.theconspiratory.com` on 25, while `main_domain=theconspiratory.com` on all 100;
- at least `/theory/atlantis` and `/theory/denver-airport` occur under both host variants;
- one absolute URL may occur with multiple keywords; maximum observed absolute-URL multiplicity
  is nine. URL, relative URL, domain, main domain, keyword, and provider item index are separate
  testimony and must not be canonicalized into one page/subject identity in RANK-04;
- `core_keyword` is non-null on 35 rows and is a provider clustering/reference field, not a
  canonical keyword foreign key.

Embedded keyword testimony includes:

- one observed twelve-key `keyword_data` family on all 100 rows;
- 12 `monthly_searches` rows per item, 1200 monthly facts total;
- 62 item rows have the July-2026 through August-2025 window, while 38 have June-2026 through
  July-2025. There is no honest Capture-global 12-month Data Period;
- current `keyword_info.search_volume` differs from the newest monthly point on 81/100 rows;
- `competition_level="LOW"` on all 100 while numeric competition includes real zero;
- CPC and low/high bid fields have independent nullability;
- detected-language testimony is `en` on 94 and another provider language on six despite the
  request/result locale remaining English;
- main intent values observed are informational 89, navigational 9, transactional 1,
  commercial 1; provider vocabulary remains open;
- `keyword_data.serp_info` is a six-key object on all 100 real rows in this fixture;
- request-disabled clickstream/normalized-clickstream paths are null on all 100;
- Bing-normalized keyword info is also null on all 100 but is not controlled by the clickstream
  request flag;
- `avg_backlinks_info` is present on all 100 while `serp_item.backlinks_info` is null on all
  100; same-looking provider names are not semantic identity.

SERP composition and target participation are explicitly different facts:

- `serp_item_types` is an ordered provider-native list describing the query SERP;
- `ai_overview` appears in those SERP-composition lists on 80/100 returned query rows, while
  target-level `ai_overview_reference` aggregate testimony is zero across all 248 matches;
- `featured_snippet` appears in SERP-composition lists on four returned rows while target-level
  featured-snippet aggregate testimony is zero;
- the parser must not infer target participation from a SERP feature string or infer SERP
  absence from a zero target-participation aggregate.

Provider time axes are independently stated by structure:

- ranked-SERP `last_updated_time`: 2026-07-10 through 2026-07-19;
- ranked-SERP `previous_updated_time`: 2026-04-09 through 2026-06-02;
- `keyword_info.last_updated_time`: 2026-07-10 through 2026-08-26;
- `search_intent_info.last_updated_time`: 2026-04-24 through 2026-05-08;
- `avg_backlinks_info.last_updated_time`: 2026-07-10 through 2026-07-19;
- monthly Data Periods span the two row-local windows above;
- Observatory Capture occurred on 2026-09-01 and is not a provider ranking update time.

One Capture proves these observed states only. Fixture facts are golden assertions, not parser
invariants unless separately locked below.

## Provisional parser / IR boundary for adversarial review

The designated Writer and independent reviewer must challenge these choices rather than merely
restating them.

1. **Parser, not Recipe.** RANK-04 types and preserves provider testimony. It decides no
   Observation admission, subject identity, page canonicalization, cross-Capture change,
   completeness policy, or Strategy meaning.
2. **Provider occurrences stay occurrences.** Every returned item retains zero-based provider
   array index. Duplicate keyword strings, duplicate URLs, near-duplicate spelling, shared page
   paths, and apex/`www` hosts remain representable without deduplication.
3. **Attempt, echo, and result context remain separate.** Verified Attempt parameters are request
   authority. Provider echo/result context is typed independently and does not overwrite them.
4. **`total_count`, `items_count`, returned length, `limit`, and `offset` are separate facts.**
   `items_count` must equal the actual item-array length. `total_count` is nonnegative testimony
   but the parser does not require equality with `items_count`, returned length, or any aggregate
   bucket sum and does not invent completeness.
5. **`metrics` and `metrics_absolute` are distinct typed families.** Their object shapes remain
   different. No parser calculation equates rank-group and rank-absolute buckets, fills the four
   missing absolute-bucket rows, or recomputes aggregates from returned items.
6. **Movement/loss fields do not reconcile one another.** `is_lost`, `rank_changes`, aggregate
   is-new/up/down/lost, `previous_rank_absolute`, and previous/current SERP clocks are each
   preserved on their own provider paths. Cross-field contradiction remains parseable well-typed
   testimony.
7. **Rank fields are independent.** Preserve `rank_group`, `rank_absolute`, and the opaque layout
   string `position` separately. Do not require the fixture correlation
   `rank_group < rank_absolute`, infer page numbers, or invent tie-break rules.
8. **SERP composition is not participation.** Preserve `serp_item_types` ordered and separately
   from `serp_item.type` and result aggregate type families. No `ai_overview` →
   `ai_overview_reference` or featured-snippet participation inference.
9. **Duplicated provider paths are not collapsed.** `ranked_serp_element` and
   `keyword_data.serp_info` duplicate several values in this fixture; duplicated difficulty also
   agrees. The parser must retain both paths and synthetic-test well-typed disagreement.
10. **Current search volume and monthly points are independent.** Preserve provider order and
    explicit `(year, month)` identity. Do not require 12 rows, newest-first order, a shared
    window, or equality with current volume.
11. **Monthly duplicate periods fail closed.** A monthly array is keyed Data-Period testimony;
    duplicate `(year, month)` rows are contradictory within that series and fail deterministically.
    This does not imply keyword/URL occurrence deduplication.
12. **Host/page normalization is forbidden.** `url`, `relative_url`, `domain`, `main_domain`,
    `website_name`, and target are separate exact provider strings. Parser validation may prove
    syntactic type/absolute-URL form where appropriate but must not canonicalize `www`, path,
    case, query, fragment, or trailing slash.
13. **Opaque provider vocabulary stays open.** Intent, competition level, clustering algorithm,
    detected language, category IDs, `position`, SERP feature strings, and ranked item-type text
    remain provider-native typed testimony. Unknown object **members** still fail closed.
14. **Request-disabled clickstream is explicit.** Under verified
    `include_clickstream_data=false`, absent/null clickstream-controlled paths become
    `NOT_REQUESTED`; populated clickstream-controlled structures fail. Bing-normalized keyword
    info is not controlled by that flag: absent/null remain their own state and a populated shape
    is unsupported until separately understood.
15. **No shared Labs parser framework.** Reuse only semantics-free value vocabulary/helpers that
    already match. Do not refactor KO/RK/Ranked into a generic provider parser in this ticket.

## Required production module and public interface

Required new production module:

`src/observatory/dataforseo_google_ranked_keywords.py`

Required public parser shape:

`parse_ranked_keywords(body: bytes, parameters: Mapping[str, object]) -> RankedKeywordsIR`

The parser accepts only complete response-body bytes plus verified Attempt parameters. It
accepts no HTTP status/header, transport state, Capture classification, Evidence path,
credential, client, endpoint, network, restic, rclone, PostgreSQL, Recipe, or API seam.

Do not edit the paid-probe implementation to host parser logic.

## Typed testimony requirements

The IR must retain enough exact testimony for the later Recipe review to make decisions without
rereading ad hoc JSON or reconstructing distinctions from lossy summaries.

### Request/envelope/task/result context

Retain exact verified Attempt parameters; provider version/status/message/duration/cost;
`tasks_count`/`tasks_error`; task ID/path/status/message/duration/cost/result_count; typed
`task.data`; result `se_type`, target, location, language, `total_count`, `items_count`; and
separate typed `metrics` / `metrics_absolute` families.

Provider durations remain strings, never timestamps. Decimal-capable costs/metrics use
`Decimal`, never binary float. Parser success/provider-error classification is local parser IR,
not a repository Measurement Outcome.

### Aggregate testimony

Represent each requested SERP-type aggregate under its exact provider key. `metrics` retains
its fixture-observed count, ETV, estimated paid-traffic cost, movement counts, 12 position
buckets, and clickstream-controlled fields. `metrics_absolute` retains its distinct fixture
shape without inventing count/ETV/cost fields.

All structural counts/buckets are nonnegative JSON integers with booleans rejected. Decimal-
capable traffic/cost fields preserve JSON null versus exact numeric value where the claimed
field permits it. Aggregate family order/keys are provider structure, not Strategy categories.
Missing required type families, unknown type-family keys, or additive members fail closed under
this v1 contract unless adversarial review identifies a better claimed-contract boundary.

No bucket-sum consistency rule is imposed beyond syntactic typing in RANK-04. Fixture-specific
tests independently prove the observed 248 and 244 totals.

### Returned ranked occurrence

Each item retains:

- `provider_array_index`;
- item `se_type`;
- exact `keyword_data` testimony;
- exact `ranked_serp_element` testimony.

`ranked_serp_element` retains exact `check_url`, `se_results_count`, `keyword_difficulty`,
`is_lost`, `last_updated_time`, `previous_updated_time`, ordered `serp_item_types`, nested
`se_type`, and typed `serp_item`. Do not require equality with `keyword_data.serp_info`.

`serp_item` retains all known fixture fields, including exact ranked type, rank group, rank
absolute, layout `position`, XPath, URL/relative URL/domain/main-domain/website-name/breadcrumb,
title/description/pre-snippet/highlighted testimony, provider traffic/cost fields, rank changes,
rank info, booleans, and nullable/unsupported nested fields. Exact text retention does not
authorize later API redistribution.

`rank_changes` retains booleans and field-stateful previous absolute rank. `rank_info` retains
its separately named values without reconciliation to backlink metrics. Arrays such as
`highlighted` preserve provider order and duplicates.

### Ranked-local keyword enrichment

Retain the full known `keyword_data` family and field states for keyword string, locale/surface,
`keyword_info`, `keyword_properties`, `avg_backlinks_info`, `search_intent_info`, `serp_info`,
Bing-normalized, clickstream-normalized, and clickstream keyword-info paths.

`KeywordInfo` retains provider update time; competition and level; CPC; current search volume;
low/high bids; categories; monthly searches; search-volume trend; and nested `se_type`.
Categories are provider-ordered integer occurrences and may contain duplicates. Do not sort or
deduplicate them.

Monthly rows retain `(year, month, search_volume, provider_array_index)` in provider order.
Calendar-valid periods use `year=1..9999`, `month=1..12`; search volume is nonnegative; signed
search-volume-trend integers remain signed. No 12-row/window/newest-first equation is imposed.

`KeywordProperties` retains `core_keyword`, clustering algorithm, keyword difficulty, detected
language, `is_another_language`, and nested `se_type` without canonicalization.

`SearchIntentInfo` retains main intent, ordered foreign intents, provider update time, and nested
`se_type`. `AvgBacklinksInfo` retains its exact decimal-capable values/provider clock and is not
the target page's `serp_item.backlinks_info`. `SerpInfo` retains exact check URL, ordered
SERP-item-type strings, result count, current/previous clocks, and nested `se_type`.

### Time handling

When stated on known provider timestamp fields, require exact lexical form
`YYYY-MM-DD HH:MM:SS +00:00`, validate a real UTC calendar datetime with year `1..9999`, and
preserve the exact string. Do not inherit Capture time or synthesize a generic Provider Update
Time. `pre_snippet` relative prose such as `"N days ago"` remains exact text, not a timestamp.

## Strict JSON, topology, and drift rules

Reject UTF-8 BOM, invalid UTF-8, duplicate JSON object members, trailing non-whitespace bytes,
invalid JSON, and non-finite constants. Known object layers are closed: unknown members fail
deterministically rather than disappearing. This is a versioned parser drift boundary, not a
claim that DataForSEO will never add fields.

Root `tasks_count` must equal the task array length and exactly one task is required. Top/task
success disagreement fails. On consistent root+task non-success, return parser-only provider-
error IR after typing verified Attempt context, provider echo, envelope/task testimony, and
nonnegative `result_count`; do not interpret Ranked result/items on that branch. `tasks_error`
must reconcile with the exactly-one-task JSON status topology as in the accepted newer parser
precedent.

On provider success, `result_count` must match the result-array length and exactly one result
object is required. Missing/null/wrong-typed result fails. `items` must be an array;
`items_count` must equal its length. A syntactically valid successful `items=[]` /
`items_count=0` is empty parser IR only; RANK-04 assigns no admitted-empty Observation semantics.

Known optional nested fields preserve absence/null/stated states where the final reviewed
contract supports them. Wrong container/scalar types fail. Numeric structural fields reject
booleans. Decimal-capable values never pass through binary float.

## Required golden-fixture proofs

At minimum prove from the exact RANK-03 fixture:

- exact fixture length `390955` and SHA-256
  `5b0e7cb6a03a921039a2845c62bd6a91eba9d61e2b54240e9af15414ba1fbc84`;
- exact envelope/task/result statuses, messages, durations, Decimal costs, task ID/path, request
  echo, and result context;
- `total_count=248`, `items_count=100`, 100 returned item occurrences, provider order retained;
- `metrics.organic.count=248`; exact rank-group corpus buckets; exact
  `metrics_absolute.organic` 244 bucket sum; distinct aggregate object shapes;
- all four non-organic requested aggregate families are present-zero, not absent;
- returned `rank_group` range 14–46, `rank_absolute` 18–57, rank-group nondecreasing, and no
  parser invariant depends on those ranges/order correlations;
- 100 organic ranked types, 100 `is_lost=false`, 100 all-new/no-up/no-down/null-previous-rank
  change objects, and full-corpus organic movement counts retained exactly;
- exact two-domain distribution 75 apex / 25 `www`, one `main_domain`, 57 absolute URLs,
  55 relative URLs, and provider strings remain distinct;
- at least two exact relative paths occurring under both hosts remain two host-specific URL
  occurrences rather than being canonicalized;
- exact multi-keyword page multiplicity can be recomputed from IR without the parser storing
  cluster/importance scores;
- 100 distinct fixture keywords retained, plus at least one pinned near-duplicate spelling or
  hyphenation pair proving exact keyword text is not normalized;
- all 100 known keyword-data families retained; 1200 monthly rows retained;
- exact two monthly-window distribution 62/38 and 81 current/newest-month disagreements;
- categories/foreign-intent/highlighted ordered state and duplicate preservation where fixture
  examples exist;
- exact intent distribution 89/9/1/1 and detected-language distribution 94/6 while request
  language remains `en`;
- `serp_info` object on all 100 real rows; overlapping ranked-element/SERP-info values are both
  retained and fixture equality is tested without becoming a parser requirement;
- `ai_overview` SERP-composition occurrence count 80 with target AIO-reference aggregate zero;
  featured-snippet SERP-composition count 4 with target featured-snippet aggregate zero;
- all request-disabled clickstream paths remain distinguishable from separately null
  Bing-normalized testimony;
- structure-local provider clocks remain on their own structures and exact observed ranges are
  testable without Capture-time inheritance;
- ordinary tests contain no operator Evidence-root or `/tmp` dependency after promotion;
- the parser test module has an autouse no-public-network guard;
- all pre-existing provider Conformance fixtures remain byte-identical.

## Required synthetic adversarial proofs

Synthetic mutation proves parser behavior, not provider occurrence.

### Decode/schema/numerics

- BOM, invalid UTF-8, trailing junk, invalid JSON, duplicate object members, NaN/Infinity;
- Decimal integer/fraction/exponent/high-precision forms without binary-float round-trip;
- booleans/strings/decimals where structural integers are required;
- unknown members at root, task, task-data, result, aggregate-family objects, item,
  ranked-serp-element, serp-item, rank-change/rank-info, keyword-data, and every known nested
  enrichment object fail closed;
- new well-typed provider **values** in open string vocabularies remain parseable.

### Attempt/echo/status/result topology

- exact Attempt key set and all frozen non-target values enforced; target parser grammar stays
  aligned with RANK-02;
- root/task status disagreement, wrong tasks count/error, two tasks, negative/boolean
  `result_count`, provider-error branch, and malformed provider-error echo/counts;
- well-typed provider echo/result target/locale disagreement remains visible and does not
  overwrite verified Attempt context;
- successful result null/omitted/wrong type/empty/two-result topology fails as appropriate;
- `items_count` mismatch fails; `total_count` smaller/equal/larger than items count remains
  independently typed without completeness inference; successful empty items parses as empty IR.

### Aggregates and ranking

- `metrics` and `metrics_absolute` are independently parsed with their distinct key sets;
- missing/unknown requested type families and additive aggregate members hit the reviewed drift
  policy rather than being silently ignored;
- zero versus null aggregate values remain distinct;
- arbitrary well-typed aggregate bucket sums, including sums different from `total_count`,
  remain parseable; no 248/244 equation appears in parser logic;
- shuffled returned-item order is preserved with new provider indexes and never resorted;
- duplicate keyword strings and duplicate URL strings remain separate occurrences;
- rank group/absolute can disagree in either direction or equal each other without a
  one-Capture correlation check, while invalid negative/boolean structural ranks fail;
- layout `position` accepts a new well-typed provider string and is never parsed as an integer;
- synthetic `is_lost=true`, non-null previous rank, `is_up=true`, or `is_down=true` combinations
  remain representable without cross-field inference if otherwise well typed;
- previous clock and previous-rank null/value combinations remain independent.

### URL/host/SERP occurrence preservation

- apex and `www` variants remain exact distinct strings; no canonicalization helper is invoked;
- the same relative path under two hosts remains two URL occurrences;
- exact URL query/fragment/trailing slash survives parsing; malformed required URL behavior must
  be explicitly reviewed rather than borrowed blindly from another surface;
- duplicated ranked-element vs `serp_info` fields may disagree synthetically and both values
  survive;
- `serp_item_types` accepts reordered, empty, duplicate, and new provider-native strings while
  preserving order/multiplicity according to the final reviewed field-state contract;
- `serp_item.type="ai_overview_reference"` and a separate
  `serp_item_types=["ai_overview", ...]` remain different fields; no cross-inference;
- nullable/unsupported `about_this_result`, links, rating, extended snippet, item backlinks,
  and similar unobserved branches receive explicit fail/preserve behavior rather than silent
  discard.

### Keyword enrichment/monthly/time states

- known optional enrichment absent/null/stated states remain distinct where supported;
- current search volume never checked against monthly rows;
- monthly arrays may be empty, shorter, longer, shuffled, and cover different valid windows;
  duplicate `(year,month)` fails; invalid month/year and negative volume fail;
- current/monthly explicit zero remains zero testimony; search-volume-trend signed values parse;
- categories null/empty/duplicates/arbitrary order preserved; foreign-intent null/empty/nonempty
  arrays preserved; core keyword and clustering states remain independent;
- detected language may disagree with request language without parser reconciliation;
- exact provider timestamp lexical/calendar failures are rejected; structure-local clocks may
  disagree and are never replaced with Capture time;
- request-disabled clickstream absent/null maps to `NOT_REQUESTED`; populated request-disabled
  shapes fail; Bing-normalized absent/null remains independent and non-null unsupported shape
  fails visibly unless review finds current parser precedent supports more.

## Out of scope

- any provider call, retry, offset follow-up, pagination, changed target, or credentials;
- Recipe/Recipe hash, Derivation, repository Outcome, Observation kinds or identities;
- PostgreSQL migration/rows/derive/Recipe selection/history API/Outcomes/Holdings;
- canonical page identity, apex/`www` collapse, URL normalization for Strategy, `core_keyword`
  canonicalization, page cluster identity, competitor relationships, ranking opportunity logic;
- cross-Capture gained/lost visibility, cadence, scheduler, F12/F13 work;
- cross-surface Observation equivalence or acquisition substitution;
- generic Labs/provider parser framework;
- modifying RANK-02 transport, RANK-03 Evidence, existing provider fixtures, or existing
  provider semantics.

## Changed-path allowlist for later implementation

When and only when this ticket is finally accepted and [CHAZ] explicitly authorizes the
designated Writer, implementation may change exactly:

- `src/observatory/dataforseo_google_ranked_keywords.py` (new);
- `tests/test_dataforseo_google_ranked_keywords.py` (new);
- `tests/fixtures/dataforseo_google_ranked_keywords_rank03.json` (new exact fixture);
- this ticket only for implementation-start/status/report updates.

If an existing production helper genuinely must change, stop and report the exact need rather
than widening the allowlist during implementation.

## Mandatory pre-implementation adversarial review

Before implementation authorization, [CHAZ] must designate exactly one Writer. That Writer
must perform a read-only code-first review of this provisional ticket against current authority,
RANK-01/RANK-02/RANK-03, strict parser precedents, and the actual relevant modules/tests.

One independent reviewer must separately review the same clean ticket HEAD without anchoring on
the designated Writer's report. The Steward then reconciles both reviews, resolves technical
questions against repository authority/Evidence, and returns any genuine Product question to
[CHAZ]. Reviewers do not edit files, promote the fixture, call the provider, access credentials,
mutate Evidence/PostgreSQL, commit, amend, or push.

Challenge especially:

- whether the proposed IR preserves every materially useful RANK-03 distinction without
  prematurely freezing Recipe/storage semantics;
- exact Attempt target grammar and frozen parameter validation;
- provider success/error and `tasks_error`/`result_count` topology;
- whether aggregate type families/fields are required, optional, or unsupported under the
  current claimed contract, especially `metrics_absolute` asymmetry;
- field-state rules for clickstream-disabled, Bing-normalized, `serp_info`, categories,
  foreign intents, highlighted text, CPC/bids, links/rating/backlinks, and other null-only or
  partially populated fields;
- whether URL validation can be strict without collapsing host identity or importing Organic
  semantics;
- whether rank values should be positive or merely nonnegative and which one-Capture
  correlations must remain synthetic-permitted;
- exact Decimal/int typing for SERP ETV/cost, avg-backlinks values, CPC/bids, competition,
  rank-info values, and structural counts;
- duplicate monthly-period parser failure versus duplicate occurrence preservation elsewhere;
- which low-level RK/KO value helpers/types can safely be reused and which carry the wrong
  reconciliation, clock, enum, subject, or Observation semantics;
- missing golden facts, adversarial false greens, excessive fixture-specific assertions, and
  whether the changed-path allowlist is sufficient without a shared parser refactor.

Return `READY`, `RECONCILE`, or `NOT_READY` with concrete code/ticket references and explicit
questions. No implementation begins until the Steward reconciles the reviews and [CHAZ]
authorizes the exact implementation start commit.

## Completed dual review and Steward reconciliation lock — 2026-09-01

[CLAUDE], the designated Writer, independently returned `RECONCILE`. [GROK] independently
returned `RECONCILE` from the same clean review HEAD without reading Claude's report. Both
accepted the parser-only architecture and four-path allowlist, found no need for another
provider call, and converged on the same load-bearing corrections: repair the fixture-promotion
guard; treat PF-11 Organic as a negative structural precedent; freeze explicit v1 object/state
contracts rather than leaving them to Writer discretion; cover every clickstream-controlled
locus; preserve all structure-local clocks; and prevent URL/rank/host helpers from collapsing
real Ranked testimony.

The rules below supersede conflicting provisional wording above. They are parser/Conformance
rules only. They do not define Recipe admission, Observation identity, PostgreSQL schema,
canonical pages, cross-surface equivalence, longitudinal change, or Strategy meaning.

### 1. Fixture promotion is fail-closed

The guarded command above, with `set -euo pipefail` and the temporary-file cleanup trap, is the
accepted one-time promotion procedure. A pre-existing fixture, inspector failure, wrong byte
count, or wrong digest must stop before `mv`. The committed fixture must remain exactly
`390955` bytes with SHA-256
`5b0e7cb6a03a921039a2845c62bd6a91eba9d61e2b54240e9af15414ba1fbc84`.
Ordinary tests may read only the committed fixture and must not depend on the operator Evidence
root or `/tmp`.

### 2. Safe reuse boundary

RANK-04 may import only:

- `RANKED_KEYWORDS_ADAPTER_CONTRACT` from `capture_event`; and
- `Field`, `FieldState`, and `ParseClassification` from
  `dataforseo_keyword_overview`.

All Ranked parsing/IR helpers and dataclasses remain Ranked-local. Do not import Related
Keywords Recipe/Observation-kind constants or parsing functions, Keyword Overview closed
intent/competition vocabularies, or Google Organic placement/normalization helpers. The
Related Keywords module now contains later Recipe symbols and is not a parser-only dependency.
Small decode/type/timestamp/value helper logic may be duplicated locally deliberately.

PF-11 Organic is explicitly a **negative precedent**: do not import its closed item-type set,
closed `{left,right}` position set, placement uniqueness, keyword normalization, or placement
identity. RANK-03 contains repeated `rank_group` and `rank_absolute` values, exact
near-duplicate keywords, open SERP-feature strings, and real apex/`www` host divergence.

### 3. Exact verified Attempt contract

Validate exactly the closed RANK-02 parameter key set and values already listed in this ticket.
Only the adapter-valid `target` varies. Duplicate the exact bounded target grammar locally so
parser failures use parser-local deterministic error semantics; do not call the Attempt-document
validator as the parser implementation and do not edit `capture_event.py` merely for reuse.
The local grammar must remain byte-for-byte semantically aligned with RANK-02, including:

- two ASCII labels only;
- lower-case adapter grammar;
- exact `\A...\Z`/full-match behavior, so a trailing newline is rejected;
- no `www` first label;
- no `xn--` label;
- label-length bounds already enforced by RANK-02.

A verified Attempt target `www.theconspiratory.com` therefore fails even though provider result
`domain=www.theconspiratory.com` is valid returned testimony. Request target grammar and provider
host testimony are different contracts.

### 4. Status/topology and successful-empty rules

Follow the newer strict parser topology:

- exactly one task; `tasks_count` equals task-array length;
- root/task success disagreement fails;
- with exactly one task, `tasks_error=0` iff that task is provider-success, otherwise `1`;
- `result_count` is a nonnegative JSON integer on every declared branch; booleans fail;
- consistent provider non-success returns parser-local `PROVIDER_ERROR` only after typing
  verified Attempt context, required task echo/envelope/task testimony, and `result_count`; do
  not inspect result/items on that branch;
- provider success requires a result array containing exactly one object and
  `result_count == 1`;
- successful `result` null/absent/wrong-type/empty/multiple fails;
- successful `items` must be an array. `items=null` or absent fails closed in v1 because that
  branch is unobserved and no claimed null-empty semantics is accepted here;
- `items_count` must equal actual array length;
- `items=[]` with `items_count=0` is valid empty parser IR only and creates no admitted-empty
  Observation meaning;
- `total_count` is an independent nonnegative provider fact. Deliberately unlike the older
  Search Mentions rule, RANK-04 imposes no `total_count >= items_count` equation.

No `total_count`, aggregate count, bucket-sum, movement-count, or returned-prefix arithmetic is
a parser consistency equation merely because some values agree in this Capture.

### 5. Closed-member policy and known v1 object families

Every parsed object has a closed known-member vocabulary: unknown member names fail
`unknown_field`. Open provider **values** remain open where typed below. Structural outer
objects require their known v1 members; explicitly nullable/request-controlled/unsupported
nested fields retain the field-state rules below rather than being silently defaulted.

The v1 known key sets are frozen from the reviewed contract/Evidence:

- root: `cost`, `status_code`, `status_message`, `tasks`, `tasks_count`, `tasks_error`, `time`,
  `version`;
- task: `cost`, `data`, `id`, `path`, `result`, `result_count`, `status_code`,
  `status_message`, `time`;
- task echo: `api`, `function`, `historical_serp_mode`, `ignore_synonyms`,
  `include_clickstream_data`, `item_types`, `language_code`, `limit`, `load_rank_absolute`,
  `location_code`, `offset`, `order_by`, `se_type`, `target`;
- result: `items`, `items_count`, `language_code`, `location_code`, `metrics`,
  `metrics_absolute`, `se_type`, `target`, `total_count`;
- item: `keyword_data`, `ranked_serp_element`, `se_type`;
- `ranked_serp_element`: `check_url`, `is_lost`, `keyword_difficulty`,
  `last_updated_time`, `previous_updated_time`, `se_results_count`, `se_type`, `serp_item`,
  `serp_item_types`;
- `serp_item`: `about_this_result`, `amp_version`, `backlinks_info`, `breadcrumb`,
  `clickstream_etv`, `description`, `domain`, `estimated_paid_traffic_cost`, `etv`,
  `extended_snippet`, `highlighted`, `is_featured_snippet`, `is_image`, `is_malicious`,
  `is_video`, `links`, `main_domain`, `position`, `pre_snippet`, `rank_absolute`,
  `rank_changes`, `rank_group`, `rank_info`, `rating`, `relative_url`, `se_type`, `title`,
  `type`, `url`, `website_name`, `xpath`;
- `rank_changes`: `is_down`, `is_new`, `is_up`, `previous_rank_absolute`;
- `rank_info`: `main_domain_rank`, `page_rank`;
- Ranked `keyword_data`, `keyword_info`, `keyword_properties`, `avg_backlinks_info`,
  `search_intent_info`, `serp_info`, monthly-row, and trend key vocabularies match the exact
  reviewed RANK-03 family shapes already recorded above;
- each `metrics.<requested_type>` object has the 12 `pos_*` buckets plus `count`, `etv`,
  `estimated_paid_traffic_cost`, `is_new`, `is_up`, `is_down`, `is_lost`,
  `clickstream_etv`, `clickstream_gender_distribution`, and
  `clickstream_age_distribution` (22 members);
- each `metrics_absolute.<requested_type>` object has the same members except `count`, `etv`,
  and `estimated_paid_traffic_cost` (19 members).

The parser must not import documentation copy/paste mistakes into these Evidence-backed v1
shapes. In particular, `metrics_absolute` does not gain count/ETV/cost because a mutable docs
example happens to show them on some family.

### 6. Aggregate family lock

On provider success under this frozen Attempt, `metrics` and `metrics_absolute` are both
required objects with exactly the five requested family keys:
`organic`, `paid`, `featured_snippet`, `local_pack`, `ai_overview_reference`.
They are required because the verified Attempt requests exactly those five families and the
reviewed v1 contract returns those five aggregate loci, not because one Capture proves a
universal provider invariant. A missing family or sixth family fails closed in v1.

`metrics` and `metrics_absolute` remain distinct typed structures. Never synthesize the three
fields absent from `metrics_absolute`. Position buckets, `count`, and movement values are
nonnegative JSON integers with booleans rejected. ETV/cost values are Decimal-capable and
preserve JSON null versus stated numeric zero/value. No parser rule requires:

- bucket sum = aggregate count;
- aggregate count = `total_count`;
- sum of family counts = `total_count`;
- `is_new` = count;
- `metrics` and `metrics_absolute` bucket sums to agree.

The fixture's 248 versus 244 arithmetic is golden testimony only.

### 7. Complete request-disabled clickstream lock

The verified Attempt has `include_clickstream_data=false`. Therefore absent or JSON-null at
**every** clickstream-controlled locus below is represented as `NOT_REQUESTED`; any populated
value fails deterministically as `request_disabled_populated`:

- `keyword_data.clickstream_keyword_info`;
- `keyword_data.keyword_info_normalized_with_clickstream`;
- `serp_item.clickstream_etv`;
- every `metrics.<requested_type>.clickstream_etv`;
- every `metrics.<requested_type>.clickstream_gender_distribution`;
- every `metrics.<requested_type>.clickstream_age_distribution`;
- every corresponding `metrics_absolute.<requested_type>.clickstream_*` field.

The non-null shapes of the gender/age distribution objects remain intentionally unsupported.
`keyword_info_normalized_with_bing` remains independent of the request flag, matching the
accepted RK parser boundary: absent and JSON null remain distinguishable field states;
populated content fails `unsupported_shape` until separately reviewed. This is an explicit
v1 drift trigger, not silent data loss.

### 8. Ranked SERP item/rank lock

`serp_item.type` and layout `position` are open provider strings. Do not import Organic closed
enums. `rank_group`, `rank_absolute`, and a stated `rank_changes.previous_rank_absolute` are
**nonnegative JSON integers** with booleans rejected. RANK-04 deliberately does not infer a
semantic prohibition on rank zero from one positive-only fixture; zero meaning is an unproven
provider branch for later review. Negative values fail.

`rank_info.page_rank` and `rank_info.main_domain_rank` are separately named nonnegative integer
provider scores. Real fixture zero is valid (`page_rank=0` on all 100; `main_domain_rank=0` on
99 and `36` on one). No generic “rank fields are positive” helper is allowed.

Duplicate rank values are valid occurrences. No uniqueness, monotonicity, relation
`rank_group < rank_absolute`, equality, page-number inference, or Organic placement identity is
imposed. Provider item order and zero-based array index are retained without resorting.

### 9. URL/host/text fidelity lock

Only `serp_item.url` receives a narrow syntax check: exact string retained; scheme must be
`http` or `https`; netloc must be nonempty; ASCII space is rejected. Query, fragment, case,
`www`, path, and trailing slash are not normalized or stripped, and URL host is not required to
match `domain`, `main_domain`, or Attempt target.

All other URL-like/layout/text fields are exact strings with no URL canonicalization:
`relative_url`, `domain`, `main_domain`, `website_name`, `breadcrumb`, both `check_url` paths,
`xpath`, `title`, `description`, and `pre_snippet`. Do not apply Attempt target grammar to
provider `domain`; that would reject the 25 real `www` rows. `pre_snippet` is free provider
text and is never timestamp-validated; the fixture includes both relative prose and the
string `07/08/2026 00:00:00`.

Synthetic tests must prove that provider `website_name`, `domain`, `main_domain`, URL host, and
relative path may disagree without parser reconciliation, while exact strings survive.

### 10. Null-only unsupported SERP children

For `serp_item.about_this_result`, `backlinks_info`, `extended_snippet`, `links`, and `rating`,
RANK-03 observes JSON null only and no Ranked-local non-null contract was empirically learned.
Absent and JSON-null remain explicit states; any populated value fails `unsupported_shape` in
v1. Do not import Organic nested schemas. This intentional fail-closed boundary is a named
revisit trigger if a later Capture populates one of these fields.

Other nullable value fields such as `pre_snippet`, `highlighted`, CPC/bids, categories,
foreign intents, `core_keyword`, clustering algorithm, and estimated paid-traffic cost retain
field-stateful null/stated behavior according to their reviewed scalar/array types. Their
fixture co-nullability is not an invariant.

### 11. Duplicated provider paths stay independently addressable

The six overlapping paths between `ranked_serp_element` and `keyword_data.serp_info` are:
`check_url`, `se_results_count`, `last_updated_time`, `previous_updated_time`,
`serp_item_types`, and `se_type`. They agree 100/100 in the fixture but parser correctness must
not require equality. Synthetic disagreement must survive on both paths.

Likewise, `ranked_serp_element.keyword_difficulty` and
`keyword_properties.keyword_difficulty` remain separate; fixture equality is golden testimony
only. `rank_info.main_domain_rank` is not `avg_backlinks_info.main_domain_rank`; the fixture's
very different values/scales are an explicit anti-collapse proof. `serp_item` paid-cost
nullability is not derived from keyword CPC even where their fixture states correlate.

### 12. Ranked-local keyword-data lock

Reuse only the low-level value vocabulary, not another surface's semantic identity.

- current and monthly `search_volume` are nonnegative JSON integers and independent facts;
- monthly rows retain provider order/index and explicit `(year, month)`; no length,
  newest-first, shared-window, or current-volume equation;
- duplicate `(year, month)` within one item's monthly series fails `duplicate_period` because
  this is keyed Data-Period testimony; duplicate item/keyword/URL occurrences remain valid;
- calendar month is `1..12`, year `1..9999`; negative monthly/current volume fails;
- search-volume-trend members are signed JSON integers; real negative fixture values must be
  preserved;
- competition/CPC/bids/backlink metrics are Decimal-capable where the provider supplies
  decimal numerics; never route through binary float;
- categories are ordered integer occurrences and may contain duplicates; null, stated empty,
  and stated nonempty are distinct where the field-state contract permits them;
- foreign-intent and highlighted arrays preserve provider order/multiplicity;
- `main_intent`, competition level, clustering algorithm, detected language, SERP feature
  names, item type, and layout position are open provider-native strings;
- `core_keyword` remains an independent clustering/reference string, not a foreign key;
- detected language may disagree with request/result language without reconciliation.

Golden fixture language testimony is exactly `en:94`, `nl:3`, `hu:1`, `de:1`, `es:1`.
Golden clustering testimony is `text_processing:55`, `keyword_metrics:1`, null:44. These are
fixture facts, not enum closure.

### 13. Structure-local clocks

When stated, provider timestamps use exact lexical form `YYYY-MM-DD HH:MM:SS +00:00`, must be
real UTC calendar datetimes with year `1..9999`, and retain the exact input string. The parser
must preserve all separately stated time paths, including:

- `ranked_serp_element.last_updated_time`;
- `ranked_serp_element.previous_updated_time`;
- `keyword_data.serp_info.last_updated_time`;
- `keyword_data.serp_info.previous_updated_time`;
- `keyword_info.last_updated_time`;
- `search_intent_info.last_updated_time`;
- `avg_backlinks_info.last_updated_time`;
- monthly `(year, month)` Data Periods as a different time axis.

The two `serp_info` clocks agree with the ranked-element clocks in this fixture only. Capture
time remains provenance outside this parser input, provider duration strings remain durations,
and `pre_snippet` remains ordinary text.

### 14. SERP composition versus target participation

`serp_item_types` is an ordered, multiplicity-preserving, open provider list about the query
SERP. It is independent from `serp_item.type`, booleans such as `is_featured_snippet`, and
result aggregate family participation. Golden proofs must include:

- `ai_overview` on 80 returned SERP-composition lists with target
  `ai_overview_reference` aggregate zero;
- `featured_snippet` in four SERP-composition lists while target featured-snippet aggregate is
  zero and those four returned organic `serp_item.is_featured_snippet` values remain false.

No parser inference connects these paths.

### 15. Strengthened golden and adversarial proofs

In addition to the existing required proofs, the implementation tests must pin enough exact
fixture testimony that normalization/reordering cannot false-green:

- exact duplicate-category row for keyword `yuba county 5 map`:
  `[10007,10108,10108,10756,10756,11500,13418,13600,13600,13601]`;
- exact near-duplicate keyword pairs including `tb test lam elisa` / `tb test lam-elisa` and
  `project sea spray` / `project sea-spray`;
- at least one provider string containing punctuation/nontrivial text retained exactly;
- `website_name=theconspiratory.com` retained on the 25 rows whose `domain` is
  `www.theconspiratory.com`;
- both mixed-host relative paths remain host-specific absolute-URL occurrences;
- `rank_info.page_rank=0` on all 100 and `main_domain_rank` distribution `0:99, 36:1`;
- duplicated `rank_group` and `rank_absolute` values remain valid occurrence testimony;
- rank-group provider order is nondecreasing in this fixture while `rank_absolute` is not;
  neither becomes a universal parser ordering equation;
- the six duplicated ranked-element/SERP-info paths and duplicated difficulty are independently
  retained and synthetically allowed to disagree;
- CPC versus bid presence proves independent nullability, including CPC-only, bids-only, both,
  and neither fixture rows;
- real negative search-volume-trend values survive;
- exact detected-language and clustering distributions above;
- the `pre_snippet` date-looking string remains unparsed text;
- every aggregate/item/keyword-data clickstream locus is proved `NOT_REQUESTED` in the golden
  fixture and a synthetic populated locus fails;
- the five null-only unsupported SERP children are proved null/unsupported separately;
- all six prior provider Conformance fixtures remain byte-identical: Keyword Overview PF-03,
  Organic PF-10, Search Mentions AI-03, Target Metrics AI-09, Historical AI-14, and Related
  Keywords RK-02.

Synthetic tests must additionally prove: Attempt `www` target rejection while returned `www`
domain is allowed; `rank_group=0`, `rank_absolute=0`, and stated previous rank zero remain
well-typed while negatives fail; `rank_info` zero remains valid; two tasks cannot be rescued by
`tasks_error=2`; successful `items=null` fails; a sixth aggregate family fails; adding
`count`/ETV/cost to `metrics_absolute` fails; a populated clickstream distribution fails;
query/fragment/trailing-slash URL text survives; `breadcrumb` is never URL-validated; and exact
duplicate keyword/URL occurrences retain distinct provider indexes.

Golden counts/ranges/order are one-Capture testimony and must not be implemented as parser
invariants unless explicitly locked above.

### 16. Allowlist and remaining questions

Both independent reviews conclude the four-path implementation allowlist is sufficient. No
existing production helper needs modification. If [CLAUDE] discovers otherwise during later
authorized implementation, stop and report instead of widening scope.

The dual review leaves **no Product question** and no justification for another provider call.
The technical questions raised by reviewers are resolved by this lock: Bing remains separate;
`position` remains open; only `serp_item.url` receives the narrow non-canonicalizing HTTP(S)
check; successful null `items` fails; rank fields use nonnegative typing without Organic
uniqueness; null-only Ranked SERP child objects are unsupported when populated; and all five
aggregate families are required because of this frozen Attempt/v1 result contract.

RANK-04 is therefore ticket-ready but still **not implementation-authorized**. [CHAZ] must
separately authorize [CLAUDE] to implement from the exact clean accepted-ticket HEAD created by
the Steward reconciliation commit.

## Implementation verification boundary

After later authorization, the designated Writer should run the bounded Ranked parser tests,
plus:

- `uv run ruff check .`;
- targeted mypy for the new parser/test modules, and the configured repository mypy command to
  detect inherited versus introduced defects.

Do not run the full pytest suite from the Writer lane unless the finally accepted ticket changes
this boundary. [CHAZ] supplies the final full-suite integration validation before Steward
closure, consistent with the current project workflow.

## Next boundary after accepted RANK-04 implementation

Only after the parser/fixture is independently reviewed and closed should a separate Ranked
Keywords Recipe/Derivation/persistence ticket decide the smallest faithful Observation grains,
semantic identities, corpus-summary relations, Ranked-local enrichment relations, and rebuild
proof. A later separately reviewed ticket exposes the admitted read/history API.

No additional provider call, Strategy implementation, or push is authorized by RANK-04.

## Implementation record — 2026-09-01

[CHAZ] explicitly authorized [CLAUDE], the designated Writer, to implement RANK-04 from the
exact clean accepted-ticket HEAD `7149bc58f520a87ef609747c706e1c79da29b41a`. Verified before
editing: branch `main`, HEAD exactly that commit, working tree clean. The implementation is one
direct child commit of that base containing only the accepted four-path allowlist. No amend, no
rebase, no push.

### Fixture promotion

Promoted once through the existing read-only inspector using the accepted fail-closed command,
with `set -euo pipefail`, the temporary-file cleanup trap, and the pre-`mv` length/digest guard.
The committed fixture is inspector stdout bytes exactly — not copied from a temporary directory,
reserialized, pretty-printed, canonicalized, regenerated, or hand-edited.

- `tests/fixtures/dataforseo_google_ranked_keywords_rank03.json`;
- exact byte count `390955`;
- exact SHA-256 `5b0e7cb6a03a921039a2845c62bd6a91eba9d61e2b54240e9af15414ba1fbc84`.

Ordinary tests read only the committed fixture. A test asserts the parser and test sources
contain no operator Evidence-root, temporary-directory, or Evidence-path token.

### Implemented boundary

`parse_ranked_keywords(body: bytes, parameters: Mapping[str, object]) -> RankedKeywordsIR` in
`src/observatory/dataforseo_google_ranked_keywords.py`. The module imports exactly
`RANKED_KEYWORDS_ADAPTER_CONTRACT` from `capture_event` and `Field`/`FieldState`/
`ParseClassification` from `dataforseo_keyword_overview`; every key set, dataclass, grammar, and
decode/type/timestamp helper is Ranked-local and deliberately duplicated. No production helper
outside the allowlist required modification.

Reconciliation-lock rules implemented as accepted: closed v1 member vocabularies for root, task,
echo, result, item, `ranked_serp_element`, the 31-key `serp_item`, `rank_changes`, `rank_info`,
the Ranked keyword-data family, and the 22-key `metrics` / 19-key `metrics_absolute` family
shapes; five required aggregate families with no arithmetic reconciliation; complete
request-disabled clickstream lock at every accepted locus; Bing kept independent of that flag;
nonnegative rank typing without uniqueness, monotonicity, or ordering equations; the narrow
non-canonicalizing HTTP(S) check on `serp_item.url` only; six duplicated provider paths and both
keyword-difficulty paths independently addressable; monthly duplicate `(year, month)` fail-closed
while duplicate keyword/URL/rank occurrences are preserved; and all structure-local clocks kept
on their own axes.

Two Writer typing decisions inside the lock, recorded for Steward review: the structural spine
members whose absence makes an object uninterpretable are required (root, task, the result
topology and both aggregate objects, item, `serp_item.type`/`rank_group`/`rank_absolute`/`url`,
and every member of the 22/19-key aggregate family shapes), while every other known member keeps
an explicit `Field` state; and `se_type` is closed to `google` at every locus, following the
Related Keywords precedent, since the ticket leaves it out of the open-vocabulary list.

### Verification performed

- bounded RANK-04 parser tests: 264 passed;
- `uv run ruff check .`: clean;
- targeted mypy on the new parser and test module: clean;
- configured repository `uv run mypy`: 14 errors in 5 files, byte-identical to the baseline
  captured at the authorized base before any edit. All are inherited defects in pre-existing
  test modules outside the allowlist; none were introduced and none were repaired;
- the suite was mutation-checked: fourteen deliberate parser mutations were applied to a scratch
  copy and reverted, confirming the duplicate-period, rank-typing, clickstream, unsupported-shape,
  `total_count` independence, item-order, aggregate-family, serp-item-spine, punycode, and
  target-grammar locks are load-bearing rather than vacuous. One shadowed rule was found this
  way: deleting the `www` first-label check changed nothing, because the two-label arity check
  already refuses `www.theconspiratory.com`. A reachable `www.com` / `wwx.com` proof now pins
  that rule, and a test-only differential over a 35-target corpus proves the duplicated grammar
  agrees with the RANK-02 adapter validator in both directions — it catches both widening and
  narrowing. That differential is the only call to the adapter validator anywhere in RANK-04 and
  is not parser logic. The explicit 1..63 label-length check is likewise defensive in both the
  adapter and the parser, since the grammar already caps a label at 63 characters; both bounds
  are duplicated so the two stay aligned.

The full pytest suite was deliberately not run from the Writer lane, per the accepted
verification boundary. [CHAZ] supplies final full-suite integration validation.

### Authority confirmation

No provider call, provider request, credential access, public network, Evidence mutation,
PostgreSQL activity, Recipe, Derivation, Observation kind, schema/migration, read/history API,
Strategy, pagination, or parser-framework refactor. The only Evidence access was the single
read-only inspector fixture promotion frozen above.

## Credential-isolation remediation — 2026-09-01

[CHAZ]'s final full-suite integration run at the implementation commit
`e40344a98bc61d10b1da8a37829c654e955193af` produced `2489 passed, 2 failed, 1 skipped,
1 warning`. Both failures were the same credential-environment assertion:

- `tests/test_dataforseo_google_ranked_keywords.py::test_no_credentials_in_environment`;
- `tests/test_dataforseo_google_related_keywords.py::test_no_credentials_in_environment`.

Root cause: the RK-03 and RANK-04 autouse `_no_public_network` fixtures omitted the AI-15
`monkeypatch.delenv(...)` credential-isolation setup. Both assertions therefore tested whether
the **operator environment itself** was credential-free rather than proving the parser test
module executes independently of credentials. The operator VPS legitimately carries
`OBSERVATORY_DATAFORSEO_LOGIN` in its shell, so the assertion failed for the right environment
and the wrong reason. This is a test-harness defect only: no Ranked or Related Keywords parser
defect is implicated, and no parser semantics changed.

[CHAZ] explicitly authorized this bounded remediation from
`e40344a98bc61d10b1da8a37829c654e955193af`.

Remediation, applied identically to both modules using the accepted AI-15 precedent: after the
existing network guard is installed and without altering its semantics, the autouse fixture now
removes both provider credential variables with `monkeypatch.delenv(..., raising=False)`. The
existing `test_no_credentials_in_environment` tests are retained and now prove that the whole
parser test module runs with credentials deliberately removed, even when the operator shell
legitimately contains them.

Exact remediation paths:

- `tests/test_dataforseo_google_ranked_keywords.py`;
- `tests/test_dataforseo_google_related_keywords.py`;
- this ticket.

No production source, parser behaviour, or fixture byte changed.

Verification. The failure was first reproduced at the base commit with a synthetic sentinel
value — never a real credential — and both named tests failed exactly as [CHAZ] reported. After
the remediation, every check below was run twice: once with a clean shell and once with both
credential variables set to that sentinel, to prove the isolation actually holds under the
condition that caused the failure.

- targeted two-test run: 2 passed under both conditions;
- both parser modules: 465 passed under both conditions;
- `uv run ruff check .`: clean;
- configured repository `uv run mypy`: 14 errors in 5 files, byte-identical to the baseline
  captured at the authorized base. All inherited, all outside the allowlist, none introduced.

The full repository suite was deliberately not run from the Writer lane. [CHAZ] still owns the
final full-suite rerun before Steward closure.
