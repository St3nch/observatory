# RK-03 — DataForSEO Google Related Keywords strict parser and RK-02 Conformance fixture

**Status:** ready — [CHAZ] authorized [CLAUDE] implementation from the exact accepted-ticket HEAD  
**Owner:** [CLAUDE] implementation / [GPT] Steward review  
**Blocked by:** none inside RK-03; implementation must remain on the accepted changed-path and no-network boundary  
**Product direction:** [CHAZ] selected RK-03 as the next active Related Keywords boundary after RK-02 closure on 2026-08-31  
**Draft base:** `3e9f347e6d2c4abdaa007943a629d98caa2bc830`  
**Claude pre-implementation review:** `RECONCILE` at `80349a3d902f4919cc695bbed815e887f8a529a6`  
**Grok independent review:** `RECONCILE` at `80349a3d902f4919cc695bbed815e887f8a529a6`  
**Steward reconciliation:** accepted into this ticket before implementation; no Product question remains  
**Implementation start commit:** `bf6a32a418e89ba51ad36f40802d80e909be52ec` — explicitly authorized by [CHAZ]  

## Purpose

Build the zero-network interpretation boundary for the exact closed adapter
`dataforseo-labs-google-related-keywords-live-paid-probe-v1`.

Promote the already accepted RK-02 response bytes into one frozen deterministic Conformance
fixture, then parse those bytes into a strict typed in-memory Related Keywords representation
that faithfully preserves the provider's returned-node, relationship, reference, enrichment,
field-state, order, and time/data-period testimony.

RK-03 does **not** create a Derivation Recipe, repository Outcome, Observation identity,
graph persistence model, PostgreSQL schema or rows, derive command, Recipe selection, API,
Holdings, Measurement Outcomes, canonical keyword identity, graph union across Captures,
frontier-node persistence policy, Strategy scoring, Ranked Keywords work, F12/F13 work, or
another provider exchange. Those remain separate later boundaries.

[CHAZ] explicitly authorized [CLAUDE] to implement RK-03 from exact clean accepted-ticket
HEAD `bf6a32a418e89ba51ad36f40802d80e909be52ec`. That authorization is limited to this
ticket's accepted parser/fixture scope and changed-path allowlist. It authorizes no provider
call, credential use, Evidence mutation, PostgreSQL mutation, Recipe/API/RK-04 work, Ranked
Keywords work, amend, or push.

## Authority and accepted foundation

- VISION and VOCABULARY Evidence, Derivation, Observation, Provenance, Provider Update Time,
  Data Period, and Strategy boundaries.
- D11 — strict provider parsing, exact numerics, field states, time-axis separation, and
  semantic reconciliation restraint.
- D12 — claimed contract, bounded real Evidence, Conformance fixture, parser, and Recipe are
  distinct; one Capture proves existence, not invariance.
- D14 consumer resources remain outside this parser boundary. Any local parser
  classification is parser-only and is not a repository Measurement Outcome.
- `docs/specs/capture-event-v2.md` provider interpretation and verified-body rules.
- RK-01 closed the Related Keywords Evidence-only adapter.
- RK-02 closed the one authorized live exchange, exact inspection, bounded encrypted F6
  protection, fresh restore/equality proof, three-way payload reconciliation, and explicit
  interpretation limits.
- AI-15 Historical is the closest current parser-only precedent. AI-10 Target Metrics and
  AI-04 Search Mentions supply strict JSON/envelope/field-state precedent. Keyword Overview
  supplies reusable value-shape precedent only where semantics genuinely match; its request
  reconciliation, Recipe assumptions, Observation kinds, timestamp bounds, and disabled-SERP
  behavior are not Related Keywords semantics.

RK-03 authorizes no provider, DNS, account, credential, restic, rclone, pricing, or other
public-network activity.

## Provisional technical boundary for adversarial review

The designated Writer must challenge these choices rather than merely restating them:

1. **Parser, not Recipe.** RK-03 types and preserves provider testimony. It does not decide
   which returned rows/edges become Observations, canonical keyword identity, graph node
   identity, completeness, cross-Capture union, or Strategy meaning.
2. **Verified Attempt context remains independent.** The parser accepts the exact verified
   Attempt parameter object plus body bytes. Provider task echo and result context are typed
   independently. A well-typed disagreement remains visible and does not overwrite Attempt
   context or automatically fail parsing.
3. **Provider order is testimony.** Returned item order and every `related_keywords` array
   order are retained with zero-based provider indexes. The parser does not sort by search
   volume, recompute depth, or infer traversal order.
4. **Provider `depth` is row testimony.** Accept claimed-contract integer depth `0..4` and
   preserve it exactly. Do not require `depth <=` the requested depth or recompute depth from
   related-keyword references; later Recipe reconciliation decides any request disagreement.
5. **Related references are occurrences, not a tree.** Preserve source item occurrence,
   target exact string, and target array index. Empty arrays, duplicate target strings,
   repeated references, same-depth/backward references, and self-references are parseable
   well-typed testimony; RK-03 does not deduplicate or reject them merely because RK-02 did
   not observe some branches.
6. **Returned item identity is not settled.** Preserve each returned item with its provider
   array index. Duplicate returned keyword strings are not silently collapsed by the parser.
7. **`seed_keyword_data` is a separate provider path.** Preserve result-level seed data
   independently from the depth-0 item's `keyword_data`. RK-02 observed byte/value equality,
   but parser correctness must not require equality or deduplicate one path into the other.
8. **`core_keyword` is a reference layer, not canonical identity.** Preserve exact stated,
   null, and absent state without replacing item/edge strings or clustering them.
9. **Current metrics and monthly points are independent testimony.** Do not derive current
   `search_volume` from the newest monthly row or require equality. Do not require twelve
   monthly rows, newest-first order, or the exact RK-02 Data Period window.
10. **Monthly rows preserve provider order but keyed periods remain unique.** Calendar-valid
    rows retain their provider array index and are not sorted, but duplicate `(year, month)`
    rows fail closed as `duplicate_period`. Relationship occurrences and monthly Data Period
    identity intentionally follow different parser rules.
11. **SERP year-1 value is not semanticized here.** Exact provider timestamps use the
    provider lexical UTC form and must be real calendar datetimes with year `1..9999`.
    `0001-01-01 00:00:00 +00:00` therefore remains a stated exact string in the typed SERP
    object, not an ordinary Provider Update Time declaration and not a parser-invented
    `never_updated` meaning. Later Recipe work decides its semantic status.
12. **Opaque provider vocab stays opaque in RK-03.** Provider-native values such as intent,
    competition level, synonym-clustering algorithm, category IDs, and SERP item types are
    preserved at their proper types without turning values observed in one Capture into closed
    enums or vocabularies. Unknown
    object members still fail closed so additive schema drift is never silently discarded.
13. **Request-disabled clickstream is explicit.** With verified
    `include_clickstream_data=false`, absent/null clickstream structures become parser field
    state `NOT_REQUESTED`; a populated request-disabled structure fails. The separate
    Bing-normalized field is not controlled by that flag: absent/null is preserved as such,
    while a non-null shape remains unsupported by this v1 parser until separately understood.
14. **No shared Labs parser framework.** Small mechanical helpers may be duplicated or
    reused only when semantics genuinely match. Do not move KO/Organic parsing into a new
    generic provider framework in this ticket.

## Steward reconciliation lock — 2026-08-31

Independent [CLAUDE] and [GROK] reviews converged on the same load-bearing corrections. GPT
rechecked current parser precedents and accepts the following final technical lock for RK-03.
These rules supersede any provisional wording above that conflicts with them:

1. **Monthly Data Period duplicates fail closed.** A `monthly_searches` array is a keyed Data
   Period series, not an occurrence list. Duplicate `(year, month)` rows fail with a
   deterministic `duplicate_period` parser error, matching Keyword Overview, Search Mentions,
   and Historical precedent. This does not change the relationship layer: duplicate returned
   keyword strings and duplicate/self/repeated `related_keywords` targets remain distinct
   provider-indexed occurrences.
2. **Reuse only the shared parser value vocabulary.** Import `Field`, `FieldState`, and
   `ParseClassification` unchanged from `observatory.dataforseo_keyword_overview`. Do not
   import or reuse Keyword Overview parsing/reconciliation functions, Recipe constants,
   year bounds, closed intent/competition enums, Observation kinds, or disabled-SERP logic.
   `ParseClassification.ADMITTED` remains a parser-local label despite its historical string
   value `observation_admitted`; it is not a repository Measurement Outcome. A successful
   `items=[]` result is empty parser IR only and acquires no admitted-empty semantics here.
3. **Attempt context is the exact closed RK-01 contract.** The parser validates the complete
   verified Attempt parameter key set and fixed values: contract token; one operator seed;
   `location_code=2840`; `language_code="en"`; `depth=3`; `limit=1000`; `offset=0`;
   exact search-volume-descending `order_by`; seed/SERP inclusion true; clickstream,
   ignore-synonyms, and core-keyword replacement false. Only the already bounded seed string
   varies. Do not edit `capture_event.py` merely to share this validation.
4. **Status topology follows the newer Historical/Target Metrics strict boundary.** Root/task
   success disagreement fails. Consistent root+task non-success returns parser
   `PROVIDER_ERROR` after typing request/echo/envelope testimony and nonnegative
   `result_count`, without reading Related Keywords result/items. On provider success,
   `result` must be an array of exactly one object; JSON null, omitted, empty, or multiple
   successful result topology fails. `items=[]` with `items_count=0` remains parseable empty
   provider testimony once a valid result object exists.
5. **Numeric sign rules are explicit.** Structural counts, current/monthly search volume,
   keyword difficulty, and SERP result count are nonnegative integers; booleans are rejected.
   `search_volume_trend.monthly`, `.quarterly`, and `.yearly` are signed provider integers and
   negative values remain valid testimony. Decimal-capable metrics use `Decimal` and never
   binary float.
6. **Depth `0..4` is a claimed-contract parser drift bound, not an RK-02 invariant.** A
   returned depth `4` is syntactically parseable even though this Attempt requested depth 3;
   depth below 0 or above 4 fails. Request/depth disagreement remains visible for RK-04.
7. **Stated nested `se_type` is adapter-typed.** When present as a string in Related Keywords
   result/keyword/SERP/backlink/intent structures, it must equal `google`. Provider vocabularies
   such as intent, competition level, clustering algorithm, and SERP item types remain open
   well-typed strings rather than one-Capture closed enums.
8. **The year-1 SERP value remains stated testimony.** The two RK-02 hollow SERP objects are
   `STATED` SERP objects whose `last_updated_time` is exactly
   `0001-01-01 00:00:00 +00:00`; the other hollow fields are JSON null as actually returned.
   Do not map the object or timestamp to null, `never_updated`, a sentinel enum, or an
   ordinary Provider Update Time flag. Exact lexical/calendar validation may accept year
   `1..9999`; RK-04 decides semantic clock usability.
9. **`total_count` is independent testimony.** It is a nonnegative integer but RK-03 does not
   require `total_count >= items_count` or equality. `items_count` alone must equal the actual
   item-array length. Any semantic completeness/count conflict is later reconciliation work.
10. **`check_url` is exact provider text in RK-03.** When stated, require a string and preserve
    it text-exactly; do not normalize it or impose Google Organic/Search Mentions URL
    validation in this parser-only ticket.
11. **Bing-normalized remains unsupported, not request-disabled.** Null/absent is preserved;
    a populated `keyword_info_normalized_with_bing` fails explicitly as an unsupported v1
    shape and is a trigger for later parser/Recipe review, not silent discard. Clickstream
    fields continue to use `NOT_REQUESTED` under the frozen false request flag.
12. **No cross-field inference.** In particular, do not infer `related_keywords` state from
    SERP state, `related_searches`, depth, `core_keyword`, or any one-Capture correlation.

## Exact fixture provenance

The fixture is copied once from already protected RK-02 Evidence through the existing
read-only Related Keywords inspector. No provider request is permitted.

- Evidence root:
  `/home/chaz/.local/share/observatory/rk02-related-keywords-conspiracy-theories-2026-08-31`;
- Attempt:
  `d41ba58d56a4adfa297c832175b9efe21606af3b4a1b78b1f05119700364e7fb`;
- Capture:
  `774ab90603bd32c906023290f2c10acab69ff0dbfd95a87d928278d9a1322d63`;
- exact response bytes: `177120`;
- exact response SHA-256:
  `e128f2f81d51479237f1bd7e51feee3dfffcae4596558ebff67365f03cd1decb`.

Required fixture path:

`tests/fixtures/dataforseo_google_related_keywords_rk02.json`

The one-time fixture promotion command is frozen to the verified inspector, not a `/tmp`
copy:

```bash
FIXTURE=tests/fixtures/dataforseo_google_related_keywords_rk02.json
TMP="${FIXTURE}.tmp"
test ! -e "$FIXTURE"
rm -f "$TMP"
if uv run python -m observatory.dataforseo_google_related_keywords_paid_probe inspect \
  --evidence-root "$HOME/.local/share/observatory/rk02-related-keywords-conspiracy-theories-2026-08-31" \
  --capture-id 774ab90603bd32c906023290f2c10acab69ff0dbfd95a87d928278d9a1322d63 \
  > "$TMP"; then
  test "$(wc -c < "$TMP")" -eq 177120
  test "$(sha256sum "$TMP" | awk '{print $1}')" = \
    e128f2f81d51479237f1bd7e51feee3dfffcae4596558ebff67365f03cd1decb
  mv "$TMP" "$FIXTURE"
else
  rc=$?
  rm -f "$TMP"
  exit "$rc"
fi
wc -c "$FIXTURE"
sha256sum "$FIXTURE"
```

The committed fixture must be byte-identical to verified inspector stdout. Tests independently
prove exact length and SHA-256. After the one-time copy, ordinary tests must not depend on the
operator Evidence root or any `/tmp` body file. The fixture is deterministic Conformance
material, not authoritative Evidence.

## Verified RK-02 testimony that the parser must retain

The exact protected body establishes one HTTP-complete provider-success response with one
task/result, exact frozen request echo, `total_count=80`, `items_count=80`, and 80 returned
item objects. Returned depth counts are `0:1`, `1:8`, `2:30`, `3:41`; the exact seed is the
depth-0 item and result-level `seed_keyword_data` is value-identical to that row's
`keyword_data` in this Capture only.

The 80 returned rows name a richer provider neighborhood:

- `related_keywords` is array on 60 rows and JSON null on 20; 59 arrays have eight targets
  and one has five, for 477 ordered reference occurrences;
- those references name 246 distinct target strings, including 167 frontier-only strings;
- returned-target depth deltas include `+1`, `0`, `-1`, and `-2`, so the relation is not a
  parent-child traversal tree;
- 67 targets receive more than one reference and maximum observed in-degree is 26;
- `core_keyword` is stated 21 times, names 20 distinct strings, and 16 of those strings are
  absent from both returned keywords and related-target strings;
- across returned, related-target, and core-keyword spaces, 263 distinct strings are named.

Every returned `keyword_data` has the observed 12-key family covering keyword identity,
metrics/history/trend, properties, backlinks, intent, SERP, normalized fields, and
clickstream fields. All 80 returned rows carry exactly twelve monthly-search points over the
same July-2026 through August-2025 sequence in this Capture, for 960 points; 50 monthly values
are explicit zero and current `search_volume` differs from the newest monthly point on 63 of
80 rows. Those counts are golden-fixture facts, not parser invariants.

SERP testimony has three structural states in RK-02: 60 metrics-bearing objects, 18 JSON
nulls, and two present objects whose useful SERP fields are null while
`last_updated_time="0001-01-01 00:00:00 +00:00"`. The two exact affected keywords are
`conspiracy theories in science` and `conspiracy theories meaning in hindi`. Metrics-bearing
SERP objects expose provider-native item-type strings including `organic`, `related_searches`,
`ai_overview`, `people_also_ask`, `video`, `images`, `discussions_and_forums`, and smaller
categories. These strings are one-Capture testimony, not a closed parser enum.

`avg_backlinks_info` is object on 59 rows and null on 21. `keyword_info`,
`keyword_properties`, and `search_intent_info` are objects on all 80. Provider `main_intent`
is `informational` on 78 rows and `commercial` on two. Both clickstream structures and the
Bing-normalized keyword-info field are null on all 80 in this Capture. Structure-local
provider times differ independently across keyword info, SERP, backlinks, and intent.

One Capture proves these states exist. It does not prove stable ordering, tree structure,
fanout, frontier omission reason, `related_keywords=null` meaning, twelve-row history,
field nullability, enum closure, SERP sentinel meaning, cross-surface semantic equivalence,
or a billing formula.

Category-ID and other provider arrays are occurrence/order testimony where the contract does
not define a key. Preserve exact order and duplicates; do not sort or deduplicate them merely
because some fixture arrays happen to appear ordered.

## Required production module and public interface

Required new production module:

`src/observatory/dataforseo_google_related_keywords.py`

Required public parser shape:

`parse_related_keywords(body: bytes, parameters: Mapping[str, object]) -> RelatedKeywordsIR`

The parser accepts only complete response-body bytes plus verified Attempt parameters. It
accepts no HTTP status/header, transport state, Capture classification, Evidence path,
credential, client, URL, network, restic, rclone, PostgreSQL, Recipe, or API seam.

Do not edit the paid-probe implementation to host parser logic.

## Typed IR requirements

The IR must retain enough exact testimony for RK-04 to author a Recipe and typed persistence
without rereading ad hoc JSON or reconstructing relationships from lossy summaries.

### Request and envelope testimony

Verified Attempt context retains the exact closed parameter object:

- adapter contract;
- seed keyword;
- location/language;
- depth, limit, offset, and ordered `order_by` tuple;
- `include_seed_keyword`, `include_serp_info`, `include_clickstream_data`,
  `ignore_synonyms`, and `replace_with_core_keyword`.

The Attempt parameter key set is closed to exactly those adapter fields plus `contract`, and
all non-seed values must equal the frozen RK-01 adapter values recorded above. Only the one
bounded operator seed string varies under the existing adapter grammar. Booleans must not
satisfy integer fields.

Provider task echo retains independently the exact well-typed echo fields present in the
closed contract/fixture, including API/function and the echoed request dimensions. Result
context retains provider `seed_keyword`, field-stateful `seed_keyword_data`, location,
language, `se_type`, `total_count`, and `items_count`. Well-typed echo/result disagreement
with Attempt context is preserved for later Recipe reconciliation.

Envelope/task IR retains version; root/task status/message/duration; exact Decimal costs;
`tasks_count`, `tasks_error`; task ID/path; and `result_count`. Provider duration remains a
string, never a timestamp. A local parser classification may distinguish successful parsed
testimony from consistent provider error, but is explicitly not a repository Outcome.

### Returned item and relationship testimony

Each returned item retains:

- `provider_array_index`;
- exact integer `depth`;
- exact `se_type` string;
- field-stateful `keyword_data`;
- field-stateful ordered tuple of `RelatedKeywordReference` values.

Each `RelatedKeywordReference` retains exact target string and zero-based
`provider_array_index` within the source item's provider array. The source occurrence is the
containing returned item; do not create global graph/node identity in RK-03.

### Keyword-data testimony

`KeywordData` retains exact provider fields and field states for:

- keyword string, location code, language code, and `se_type`;
- `keyword_info`;
- `keyword_properties`;
- `avg_backlinks_info`;
- `search_intent_info`;
- `serp_info`;
- `keyword_info_normalized_with_bing`;
- `keyword_info_normalized_with_clickstream`;
- `clickstream_keyword_info`.

The known keyword-data object is closed against unknown member loss, but known optional
members preserve `ABSENT`, `JSON_NULL`, `STATED`, and where request-controlled,
`NOT_REQUESTED` distinctly.

`KeywordInfo` retains exact field states for provider time, competition, competition level,
CPC, current search volume, low/high top-of-page bid, category-ID array, monthly-search
array, search-volume-trend object, and nested `se_type`. Decimal-capable numbers use
`Decimal`, never binary float. Monthly rows retain `(year, month, search_volume,
provider_array_index)`; calendar validity is `year=1..9999`, `month=1..12`; search volume is
nonnegative and stated zero is zero testimony. Array order is preserved and no
twelve-row/newest-first/current-volume equation is imposed. Duplicate `(year, month)` rows
fail closed as contradictory keyed Data Period testimony; raw Evidence remains authoritative
and unchanged.

`SearchVolumeTrend` retains field-stateful `monthly`, `quarterly`, and `yearly` provider
integers without computing a trend or score.

`KeywordProperties` retains exact field states for `core_keyword`,
`synonym_clustering_algorithm`, `keyword_difficulty`, `detected_language`,
`is_another_language`, and nested `se_type`. No core-keyword replacement or canonicalization
occurs.

`AvgBacklinksInfo` retains exact Decimal-capable provider values for backlinks, dofollow,
referring pages/domains/main domains, rank, main-domain rank, provider time, and nested
`se_type` with null/absence preserved at the enclosing-object and field levels.

`SearchIntentInfo` retains exact `main_intent`, ordered `foreign_intent` strings, provider
time, and nested `se_type`. Intent strings remain opaque provider vocabulary in RK-03.

`SerpInfo` retains exact field states for `check_url`, ordered `serp_item_types` strings,
`se_results_count`, `last_updated_time`, `previous_updated_time`, and nested `se_type`.
`check_url` remains the exact provider string; do not normalize it into a page identity.
SERP item-type strings remain provider-native vocabulary.

Do not add graph centrality, cluster IDs, normalized keywords, inferred parent/child links,
current-vs-history deltas, trend calculations, Strategy labels, Capture-time inheritance,
Provider Update Time semantics for the year-1 value, or Observation identities.

## Strict JSON, topology, and field rules

The parser must reject UTF-8 BOM, invalid UTF-8, duplicate JSON object members, trailing
non-whitespace bytes, invalid JSON, and non-finite constants. Known object layers are closed:
unknown members fail deterministically rather than being ignored. This is a parser-version
drift boundary, not a claim that the provider can never add fields.

Root `tasks_count` must equal the task-array length and exactly one task is required.
`tasks_error` must be zero for a successful single task and one for a non-success single task.
Top-level/task success disagreement fails. On consistent provider non-success, return
parser-only provider-error IR after structurally typing Attempt context, task echo,
envelope/task testimony, and nonnegative `result_count`; do not interpret Related Keywords
result/items on that branch.

On provider success, `result_count` must match the result-array length and exactly one result
is required; missing/null/wrong-typed `result` fails rather than becoming empty testimony.
`items` must be an array; `items_count` must equal its length. `total_count` is typed and
preserved independently; RK-03 does not require `total_count == items_count` or
`total_count >= items_count`, and does not infer completeness from either. `items=[]` with
`items_count=0` is parseable empty provider testimony only, not an admitted-empty Observation.

Known optional nested objects/fields preserve absence/null/value states rather than
synthesizing defaults. Wrong container/scalar types fail. Structural counts and array indexes
are JSON integers with booleans rejected. Decimal-capable provider metrics accept JSON
integer or Decimal lexical forms without float round-trip.

Provider timestamp strings, when stated on known timestamp fields, must match exact lexical
form `YYYY-MM-DD HH:MM:SS +00:00` and represent a real UTC calendar datetime with year
`1..9999`. Preserve the exact string. Keyword Overview's `2000..2100` restriction is a
monthly Data Period rule and must not be imported here. Do not promote the year-1 SERP string
into semantic Provider Update Time testimony.

## Required golden fixture proofs

At minimum prove from the exact RK-02 fixture:

- exact fixture length `177120` and SHA-256
  `e128f2f81d51479237f1bd7e51feee3dfffcae4596558ebff67365f03cd1decb`;
- exact root/task/result topology, statuses, messages, duration strings, Decimal costs,
  task ID/path, request echo, and result context;
- `total_count=80`, `items_count=80`, 80 returned item occurrences, and exact provider order;
- depth distribution `0:1`, `1:8`, `2:30`, `3:41`;
- result seed and `seed_keyword_data` retained separately from the depth-0 item, while the
  golden fixture independently proves their observed equality;
- `related_keywords` state counts 60 stated arrays / 20 JSON null, array-length distribution
  59×8 + 1×5, and 477 exact ordered reference occurrences;
- exact distinct-target facts from the fixture: 246 targets, 167 frontier-only; no parser
  rule depends on those counts;
- returned-target depth-delta counts `+1:96`, `0:96`, `-1:69`, `-2:21`, proving the parser
  retained depth separately from edges;
- 67 multiply referenced targets and maximum observed incoming-reference count 26 can be
  recomputed from the typed IR without the parser storing centrality/importance;
- `core_keyword` stated/null counts 21/59, 20 distinct stated strings, and the 16
  core-only strings remain available without canonicalization;
- SERP structural states 60 metrics-bearing objects / 18 JSON null / 2 present year-1
  objects, including the exact two affected keywords and exact year-1 string;
- exact SERP item-type arrays remain provider ordered; aggregate fixture checks may confirm
  observed counts such as `organic=60`, `related_searches=51`, `ai_overview=48`,
  `people_also_ask=43`, `video=21`, `images=14`, `discussions_and_forums=8` without making
  those values parser enums;
- backlinks object/null counts 59/21 and exact provider intent testimony including
  `informational=78`, `commercial=2` main-intent values;
- all 80 current keyword-info objects and all 960 item-level monthly rows are retained exactly;
  golden checks prove the one observed 12-period sequence, 50 stated monthly zeros, and 63
  item rows where current search volume differs from the newest monthly point. The separately
  retained `seed_keyword_data` contributes another 12 monthly rows and must not be accidentally
  folded into or dropped from the independent seed path;
- the 20 null `related_keywords` rows include ten depth-2 and ten depth-3 items, proving the
  parser cannot infer null from the requested depth boundary;
- pin at least one exact provider-ordered relationship tuple from the depth-0 seed, one named
  frontier target referenced by a source below depth 3, and one named core-only string, so
  count-only graph tests cannot pass after reordering or collapsing testimony;
- both hollow SERP keywords are asserted by exact keyword string and exact nested field states,
  not merely counted as two special objects;
- request-disabled clickstream fields remain distinguishable from the separately null
  Bing-normalized field;
- structure-local timestamp strings remain on their own nested structures and are not
  replaced by Capture time;
- ordinary tests contain no operator Evidence-root or `/tmp` dependency after fixture
  promotion;
- the parser test module installs an autouse no-public-network guard so a false-green parser
  test cannot reach a provider host;
- all existing provider Conformance fixtures remain byte-identical, at minimum:
  `dataforseo_keyword_overview_pf03.json`,
  `dataforseo_google_organic_pf10.json`,
  `dataforseo_ai_optimization_search_mentions_ai03.json`,
  `dataforseo_ai_optimization_target_metrics_ai09.json`, and
  `dataforseo_ai_optimization_llm_mentions_historical_ai14.json`.

## Required synthetic adversarial proofs

At minimum mutate decoded copies or dedicated synthetic JSON; never edit the frozen fixture.

### Decode, numerics, and schema drift

- UTF-8 BOM, invalid UTF-8, trailing junk, invalid JSON, duplicate object members,
  `NaN`/`Infinity`;
- Decimal integer/fraction/exponent/high-precision forms without binary-float round-trip;
- booleans/strings/decimals where structural integers are required;
- unknown members at root, task, task-data, result, item, keyword-data, and every nested
  known object layer fail rather than disappear;
- unknown **values** of opaque string vocabularies remain parseable where the field type is
  otherwise valid.

### Envelope, request, echo, and result topology

- wrong `tasks_count`, two tasks, wrong `tasks_error`, inconsistent root/task success;
- consistent provider error preserves request/echo/envelope testimony and nonnegative
  `result_count` without interpreting result items;
- malformed provider-error echo/count topology still fails;
- wrong/negative/boolean `result_count`; empty/two-result successful topology;
- exact Attempt parameter key set, seed type/grammar, and every frozen non-seed parameter value
  are enforced;
- well-typed provider echo/result seed/location/language/se-type/count disagreement remains
  visible and does not overwrite Attempt context;
- `total_count` may differ from returned `items_count`, including being smaller, without the
  parser inventing completeness; `items_count` must still equal actual item-array length;
- successful `result=null`, omitted result, and otherwise wrong-typed result fail;
- successful empty `items=[]` / `items_count=0` parses as empty parser IR only.

### Returned rows and relationship preservation

- shuffled returned-item order parses without re-sorting; provider indexes follow the
  synthetic order;
- duplicate returned keyword strings remain separate item occurrences;
- calendar/claimed-contract-valid depth `4` remains parseable even though the frozen Attempt
  requested depth `3`; invalid depth outside `0..4` fails;
- `related_keywords` absent, JSON null, and empty array remain distinct states;
- duplicate related target strings, repeated target strings, and self-reference parse as
  separate ordered occurrences; no dedup/tree rule appears in RK-03;
- wrong-type related targets fail;
- `seed_keyword_data` absent/null/object states remain distinct; a well-typed seed-data value
  that differs from the depth-0 item still parses and remains visible.

### Keyword-data, monthly, reference, and SERP states

- known optional enrichment object absent/null/value states remain distinct;
- stated `core_keyword` may equal an item, edge target, or neither without replacement;
- null and stated `synonym_clustering_algorithm` remain independent from `core_keyword`;
- monthly arrays may be empty, shorter, longer, shuffled, or contain a calendar-valid
  out-of-window point without parser sorting/completeness inference;
- stated monthly search-volume zero remains zero; current search volume is never checked
  against the newest monthly row;
- duplicate `(year, month)` rows fail closed with `duplicate_period`;
- invalid month `0/13` and year `0/10000` fail calendar typing;
- negative current or monthly `search_volume`, negative keyword difficulty, and negative
  `se_results_count` fail; negative search-volume-trend values parse and remain exact;
- competition/difficulty explicit zero versus JSON null remain distinguishable;
- categories JSON null, empty array, duplicates, and arbitrary provider order remain
  distinguishable/preserved; foreign-intent JSON null, empty array, and nonempty ordered
  arrays remain distinguishable;
- an otherwise well-typed new `main_intent`, `competition_level`,
  `synonym_clustering_algorithm`, or SERP item-type string remains parseable opaque testimony;
- a newly present `search_partners` member fails as unknown rather than being silently
  imported from Keyword Overview semantics;
- item location/language disagreement with result/Attempt and absence of a depth-0 seed row
  remain visible parser testimony rather than parser reconciliation failures;
- exact `0001-01-01 00:00:00 +00:00` is preserved as a stated SERP timestamp string;
  malformed/non-UTC/impossible timestamp strings fail;
- SERP null, present hollow year-1 object, and metrics-bearing object remain
  structurally distinguishable without a parser-invented sentinel enum;
- empty/duplicate/new provider-native `serp_item_types` strings remain ordered testimony;
- exact raw `check_url` string is preserved without URL normalization;
- request-disabled clickstream absent/null parses as `NOT_REQUESTED`; populated clickstream
  fails; Bing-normalized absent/null remains its own state and a non-null unsupported shape
  fails explicitly rather than being silently discarded.

## Out of scope

- any provider call, retry, pagination, offset follow-up, changed seed, or credentials;
- Derivation Recipe, Recipe hash, repository Outcome, Observation kinds/identities;
- graph tables, node/edge persistence, frontier persistence, canonical keyword identity,
  graph union across Captures, centrality, importance, semantic similarity, or Strategy;
- PostgreSQL migration/derive/API/Recipe selection/Outcomes/Holdings;
- deciding RK versus Keyword Overview semantic equivalence or acquisition substitution;
- Ranked Keywords, F12 orchestration, F13 work, generic provider parser framework;
- changes to Evidence, capture transport, paid-probe code, existing provider fixtures, or
  existing provider semantics.

## Changed-path allowlist for later implementation

When and only when the final ticket is accepted and [CHAZ] authorizes implementation, the
designated Writer may modify exactly:

- `src/observatory/dataforseo_google_related_keywords.py`;
- `tests/test_dataforseo_google_related_keywords.py`;
- `tests/fixtures/dataforseo_google_related_keywords_rk02.json`;
- this ticket only for Start commit, status, and Implementation report.

If an existing production helper genuinely must change, stop and report the exact need rather
than broadening the allowlist during implementation.

## Required designated-Writer pre-implementation review

Before implementation, the designated Writer must inspect current authority, RK-01/RK-02,
the actual parser precedents, paid adapter/tests, and this provisional ticket read-only.

Challenge especially:

- parser-versus-Recipe placement of item duplication, duplicate monthly periods,
  `total_count`, depth/request disagreement, provider-error handling, and seed-data
  disagreement;
- whether the IR preserves all materially useful provider testimony without inventing graph
  or canonical-keyword semantics;
- year-1 SERP timestamp handling and whether any existing helper would silently promote or
  reject it incorrectly;
- exact field-state handling for clickstream-disabled, Bing-normalized, SERP, backlinks,
  `core_keyword`, and optional seed data;
- which KO mechanical value parsers are safe to duplicate/reuse versus which carry Recipe,
  reconciliation, enum, year-bound, or Observation semantics that must remain separate;
- whether closed-object policy plus opaque string values gives the correct drift boundary;
- missing fixture facts, adversarial branches, false greens, and excessive test assertions;
- whether the changed-path allowlist is sufficient without a generic parser refactor;
- whether any rule accidentally loses provider order/occurrence testimony or turns a
  one-Capture correlation into an invariant.

Return `READY`, `RECONCILE`, or `NOT_READY` with concrete code/ticket references and any
questions for GPT/[CHAZ]. Do not edit files, copy/promote the fixture, call the provider,
access credentials, mutate Evidence/PostgreSQL, commit, amend, or push.

### Completed dual review and Steward resolution

[CLAUDE], the designated Writer, returned `RECONCILE` from the exact clean review HEAD.
Independently, [GROK] returned `RECONCILE` from the same HEAD without reading or anchoring on
Claude's review. Both identified duplicate monthly periods as a parser-level contradiction,
the need to preserve the year-1 SERP string as stated structural testimony, and several
false-green/test-isolation risks. Claude additionally caught the shared field-state vocabulary,
full-repository mypy scope, category-order/duplicate risk, and fixture-promotion retry hazard;
Grok sharpened the frozen Attempt-value contract, status topology, open provider vocabulary,
and no-cross-field-inference rules.

GPT independently checked the current repository precedents and resolves the remaining
technical questions as follows: duplicate monthly periods fail closed; successful
`result=null` fails; `check_url` is exact string testimony without URL normalization in
RK-03; depth `0..4` is retained as an explicitly claimed-contract parser bound; nested stated
`se_type` is `google`; `total_count < items_count` remains visible parser testimony; negative
current/monthly search volume fails while trend values remain signed; and RK-03 reuses the
existing `Field`/`FieldState`/`ParseClassification` vocabulary with an explicit parser-only
D14 lock. No Product question remains and no second provider call is justified.

## Implementation verification after later authorization

The Writer should run the bounded Related Keywords parser tests plus:

- `uv run ruff check .`;
- `uv run mypy`.

Do not run the full suite unless the accepted final ticket explicitly changes that boundary.
Per current project process, [CHAZ] supplies final full-suite validation at the later
integration/closure point.
