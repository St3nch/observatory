# RANK-01 — DataForSEO Google Ranked Keywords activation review

**Status:** closed — [GPT] Steward accepted after independent Grok `RECONCILE`, technical reconciliation, and [CHAZ] Product resolution on 2026-09-01  
**Owner:** [GPT] Steward reconciliation / [GROK] technical review  
**Blocked by:** none; Related Keywords RK-01 through RK-05 are closed  
**Draft base:** `0bb93ba49464a098088b138efebc5e593c53de4f`  
**Product direction:** Ranked Keywords is the next planned provider feature slice before the accepted MVP provider-testimony deep-review closeout gate  

## Purpose

Determine the first bounded DataForSEO Labs Google Ranked Keywords adapter contract and the
smallest useful real provider probe set before any implementation, credentials, spend, or
Evidence creation.

The downstream analytical purpose is to preserve source-attributed testimony answering
questions such as:

- which queries a specified domain, subdomain, or exact webpage is reported as ranking for;
- which exact provider SERP element represents that target's ranking for each returned query;
- how provider-reported ranking distributions, traffic estimates, movement/loss counts, and
  keyword metrics relate without being collapsed into one score;
- whether a target is reported in ordinary organic, paid, featured-snippet, local-pack, or
  Google AI Overview reference result types;
- which ranking testimony is current versus provider-classified as previously present but
  lost.

Observatory preserves provider testimony and provenance. It does not decide which rankings
are opportunities, which competitors matter, which keywords should be targeted, or what SEO/
GEO action to take.

## Current claimed provider contract — review snapshot 2026-08-31

Official documentation currently describes one Live POST endpoint:

    /v3/dataforseo_labs/google/ranked_keywords/live

The claimed request contract includes:

- required `target`, with materially different domain/subdomain versus exact-page URL forms;
- optional country/location and language scoping;
- `ignore_synonyms`, default `false`;
- `item_types`, default `['organic', 'paid']`, with currently documented values
  `organic`, `paid`, `featured_snippet`, `local_pack`, and `ai_overview_reference`;
- `include_clickstream_data`, default `false`; current documentation says enabling it adds
  clickstream/normalized structures and doubles request price;
- `limit`, default `100`, maximum `1000`, plus `offset`;
- `load_rank_absolute`, default `false`, which adds an absolute-position distribution in
  addition to the normal same-element-type `rank_group` distribution;
- `historical_serp_mode`, default `live`, with documented values `live`, `lost`, and `all`;
- filters and up to three `order_by` rules; the documented default order is ascending
  `ranked_serp_element.serp_item.rank_group`.

The claimed response contract includes one result-level target/location/language context,
`total_count`, `items_count`, ranking-distribution/traffic/movement metrics by SERP type,
optional absolute-rank metrics, and returned items containing rich `keyword_data` plus the
`ranked_serp_element` for the target. The provider documentation states that this Labs data
is updated weekly while nested keyword/SERP structures expose their own update testimony.

This section records the provider's claimed contract only. It is not a Derivation Recipe,
not proof of provider invariance, and not authorization to call the API.

Official sources for this review:

- https://docs.dataforseo.com/v3/dataforseo_labs-google-ranked_keywords-live/
- https://dataforseo.com/apis/dataforseo-labs-api/competitor-research

Exact pricing, request fields, accepted item types, and provider semantics must be rechecked
immediately before any later live-call authorization.

## Review method

- Read current Observatory authority, this ticket, Related Keywords RK-01 through RK-05,
  Keyword Overview, Google Organic, and shared provider transport/Recipe/read precedents.
- Inspect the actual current code/tests only to identify reusable seams, false analogies, and
  transport constraints. Do not edit anything.
- Review current official DataForSEO Ranked Keywords documentation and pricing deeply enough
  to understand materially distinct request/response modes. Public documentation research is
  authorized; API calls, account access, credentials, sandbox/provider requests, and spend are
  not.
- Keep claimed provider contract, future real Evidence, synthetic adversarial proof, and any
  later Derivation Recipe explicitly distinct under D12.
- Treat one future Capture as testimony of one exact exchange, never as proof of all provider
  invariants.

## Required analysis

1. **Analytical grain and identities** — determine the useful fact and relationship grains:
   requested target, provider-returned target, returned keyword, ranked SERP element, exact
   ranked URL/domain/page identity where exposed, SERP item type, rank-group position,
   absolute position, target-level metric bucket, and provider occurrence/order. Identify
   which identities must remain distinct.
2. **Domain versus exact-page target** — explain what changes semantically and empirically
   between a domain/subdomain request and an exact webpage request. Recommend which form gives
   the highest-value first probe, or whether more than one probe is materially necessary.
3. **Current versus lost testimony** — analyze `historical_serp_mode=live|lost|all`. Determine
   whether `all` is a richer single-probe contract or whether mixing live and lost creates an
   ambiguous response that should remain a different adapter/probe mode. Explain what
   provider evidence distinguishes a currently ranked item from a lost item.
4. **SERP item types** — analyze organic, paid, featured snippet, local pack, and
   `ai_overview_reference`. Decide which types belong in the first bounded probe and which are
   materially separate modes. In particular, keep Google SERP AI Overview reference testimony
   distinct from AI Optimization LLM Mentions testimony.
5. **Rank semantics** — compare `rank_group`, item `rank_absolute`, and
   `load_rank_absolute/metrics_absolute`. Determine what is independent testimony versus a
   projection or distribution, and identify common inference traps.
6. **Aggregate versus item testimony** — inspect result-level ranking buckets, `etv`,
   `estimated_paid_traffic_cost`, counts, `is_new`, `is_up`, `is_down`, `is_lost`, and
   clickstream variants. Determine whether these are provider-computed facts worth preserving
   separately from returned item rows and what scope/time caveats they require.
7. **KeywordData reuse versus false equivalence** — compare the Ranked Keywords
   `keyword_data` family against accepted Keyword Overview and Related Keywords structures.
   Identify structural reuse opportunities but do not assume same endpoint, state domain,
   clock attachment, completeness, or semantic identity merely because field names match.
8. **Time and freshness** — inventory every provider-stated update time, Data Period, weekly
   endpoint cadence claim, ranking movement comparison frame, and any unstated timing. Do not
   invent a universal event time or assume movement/loss counts describe change since the
   Observatory Capture.
9. **Completeness and pagination** — analyze `total_count`, `items_count`, `limit`, `offset`,
   ordering, filters, item-type filtering, historical mode, and any provider caps. State what a
   first Capture can and cannot prove about the full ranking corpus. Determine whether one
   bounded page is sufficient for reconnaissance and how truncation must remain visible.
10. **Request options with irreversible acquisition consequences** — review `ignore_synonyms`,
    item types, clickstream, absolute-rank loading, historical mode, filters, sort, limit,
    location, and language. Explicitly record any historically useful testimony deliberately
    left unacquired and the trigger for revisiting it.
11. **Target selection criteria** — recommend the properties a real first target should have
    so the probe exercises useful branches (sufficient keyword corpus, more than one ranking
    type if practical, stable public target, manageable response size). Do not silently choose
    a Product target if more than one reasonable candidate exists; surface the choice to
    [CHAZ].
12. **Transport fit** — determine whether the first candidate contract honestly fits the
    existing bounded single-exchange HTTP event-v2 model and what exact response-size/read-
    timeout/spend bounds a later probe ticket should use. Flag any F13 hardening trigger if
    reuse of an older affected gate would be required.
13. **Probe matrix** — propose the smallest useful real probe set. Each proposed provider
    call must exercise a materially distinct contract branch and state exact target form,
    location/language, item types, historical mode, absolute-rank setting, clickstream setting,
    filters/sort/limit/offset, expected learning, and conservative maximum cost. Proposal is
    not authorization.
14. **Future consumer readiness** — identify what a later typed API must expose so a strategy
    LLM can answer ranking-history and visibility questions without direct PostgreSQL/Evidence
    access and without mistaking provider estimates, movement flags, rank positions, or
    incomplete returned pages for Observatory conclusions.

## Questions the review must try to resolve

- Is one domain-level `historical_serp_mode=all` probe sufficient to learn both live and lost
  item testimony, or does D12 justify separate live/lost probes?
- Should the first probe request only organic results, preserve the provider default
  organic+paid pair, or deliberately include featured snippet/local pack/AI Overview
  references?
- Is `load_rank_absolute=true` important enough to acquire on the first probe even though the
  item itself already exposes absolute rank?
- Does `ignore_synonyms=false` expose useful duplicate/near-duplicate testimony that a strict
  parser must preserve rather than normalize away?
- Are result-level movement metrics tied to a provider-defined previous check in a way that
  must be preserved as opaque provider comparison testimony rather than interpreted as a
  Capture-to-Capture delta?
- Which target characteristics are needed to avoid a misleadingly sparse first Capture?
- Can clickstream remain deliberately request-disabled for the MVP without losing a uniquely
  historical dimension we cannot economically recover later?

## Mandatory candid report

Return:

- `RECOMMENDATION: READY | RECONCILE | STOP` for cutting the first implementation/probe ticket;
- recommended first adapter/probe contract and any runner-up;
- direct official-source links and dated pricing/contract observations;
- Product questions requiring [CHAZ] resolution before a final probe ticket;
- false premises, overconstraints, architecture traps, and dangerous analogies in this draft;
- reusable code/test seams versus things that should deliberately remain Ranked-specific;
- likely false-green tests and adversarial cases;
- strongest and weakest assumptions;
- exact historically irrecoverable dimensions deliberately deferred and revisit triggers;
- proposed minimum call count and conservative spend ceiling, with no authorization implied;
- unproven provider invariants that must remain synthetic or version-gated after one Capture.

## Hard boundaries

- Read-only review only: no repository edits, file creation, commit, amend, push, branch/
  worktree mutation, or ticket status change.
- No DataForSEO API request of any kind, including Sandbox, account, Status, pricing API,
  Locations/Languages API, or the Ranked Keywords endpoint itself. No credentials, spend,
  provider transport, Evidence creation, or Evidence mutation.
- No PostgreSQL mutation and no ordinary/full test run unless a read-only code-inspection
  question genuinely requires identifying an existing test by name; do not execute it.
- No adapter, parser, Recipe, schema/migration, fixture, Derivation, API, Ranked Keywords
  implementation, recurring acquisition, Strategy logic, scoring, or recommendation engine.
- Do not activate F3, F6 routine automation, F7, F8, F9, F10, or F12.
- Public HTTPS access to official provider documentation/pricing is the only authorized
  external network activity for this review.

## Deliverable and next gate

Return one technical review to [CHAZ] for relay to [GPT]. Stop after the report.

The Steward will independently adjudicate the findings against repository authority and
current provider documentation. If the review is reconciled, [GPT] will revise this ticket or
cut the next bounded implementation/probe ticket and commit that accepted boundary. A real
provider call remains a later, separately explicit [CHAZ] authorization after implementation,
fresh pricing/contract recheck, and the accepted Evidence-protection sequence.

## Steward reconciliation — 2026-09-01

Independent [GROK] read-only review of exact HEAD
`4172b55e6bbdae6121d94c8ca4730abccc2f857e` returned **`RECONCILE`**. The Steward
independently rechecked the material findings against current official Ranked Keywords
documentation/pricing and current repository authority/code. The technical findings below are
accepted and supersede provisional alternatives elsewhere in this ticket. Two Product choices
remain for [CHAZ] before the first probe implementation ticket is cut: the exact domain target
and the explicit Evidence-retention acknowledgement described below.

### Accepted first-probe contract shape

The intended first adapter remains one bounded Live single-exchange contract:

    dataforseo-labs-google-ranked-keywords-live-paid-probe-v1

against:

    POST /v3/dataforseo_labs/google/ranked_keywords/live

The future request must contain exactly one task with this closed shape, except for the exact
[CHAZ]-chosen domain string:

    {
      "target": "<CHAZ-chosen registrable domain>",
      "location_code": 2840,
      "language_code": "en",
      "ignore_synonyms": false,
      "item_types": [
        "organic",
        "paid",
        "featured_snippet",
        "local_pack",
        "ai_overview_reference"
      ],
      "include_clickstream_data": false,
      "limit": 100,
      "offset": 0,
      "load_rank_absolute": true,
      "historical_serp_mode": "all",
      "order_by": ["ranked_serp_element.serp_item.rank_group,asc"]
    }

No filters, `tag`, location/language names, caller-supplied ordering, caller-supplied item-type
order, or additional task keys belong to this first contract.

The target grammar is deliberately **domain-only** for the first Capture: one registrable
domain string with no scheme, no `www.`, no path, query, fragment, port, credentials, or
subdomain form. Current provider documentation explicitly states that domain/subdomain and
webpage forms are parsed differently and that a webpage-looking value without `https://` or
`www.` is treated as a domain request. The adapter must reject ambiguous/foreign forms rather
than normalize them into a different provider subject. Exact-page and subdomain requests are
later contracts, not aliases for this one.

Location and language are mandatory in the closed request. Current provider documentation
states that omitting them requests all available locations/languages, which is materially
different testimony rather than a harmless provider default.

`historical_serp_mode="all"` is selected because it is the richest documented one-call mode:
the provider claims it returns both currently ranking and previously-ranking-but-lost keyword
sets. This does **not** establish that the first returned page will contain a lost item. A
second `lost`-only call is not currently justified. It becomes a D12 candidate only if the
accepted first Evidence indicates a lost population while the returned prefix contains no
item-level lost testimony and therefore does not reveal the lost-item shape.

All five documented result types are requested with `organic` first. Current documentation
states that when non-organic types are requested, returned ordering depends on the first item
type in the array. Array order is therefore request/sample testimony, not cosmetic ordering.
The first page may still be heavily organic-biased; absence of a rare requested type from the
100 returned rows is not absence from the provider corpus.

`load_rank_absolute=true` is accepted because item-level `rank_absolute` does not replace the
separate result-level `metrics_absolute` distribution. `ignore_synonyms=false` preserves the
provider's near-duplicate/core-keyword behavior for empirical review instead of suppressing it.
Clickstream remains request-disabled for this MVP probe: it doubles current published request
pricing, adds demographic/clickstream-normalized testimony with separate retention/modeling
cost, and is not required to learn the Ranked Keywords ranking relationship grain.

### Accepted semantic distinctions and traps

The later parser/Recipe/API must keep these provider facts distinct unless real Evidence plus
the claimed contract prove a narrower relationship:

- requested domain subject, echoed result target, ranked SERP `domain`, `main_domain`, exact
  `url`, and `relative_url`;
- returned keyword text, any `core_keyword`, returned item occurrence, SERP result type, ranked
  URL/page occurrence, `rank_group`, and `rank_absolute`;
- item-level `ranked_serp_element.is_lost`;
- item SERP `rank_changes.previous_rank_absolute` plus `is_new`/`is_up`/`is_down`;
- result-level per-type integer `metrics.*.is_new`/`is_up`/`is_down`/`is_lost`;
- ordinary `metrics` rank-group distributions versus optional `metrics_absolute` absolute-rank
  distributions;
- provider ETV / estimated-paid-traffic-cost testimony versus Observatory Capture history;
- Ranked Keywords embedded `keyword_data` versus structurally similar Keyword Overview and
  Related Keywords testimony.

Provider movement/loss facts are comparison-to-provider-prior-check testimony. They are **not**
Observatory Capture-to-Capture deltas, and the provider's comparison interval is not a named
Observatory Data Period unless the response explicitly states one. Capture time, nested
provider update times, `previous_updated_time`, monthly Data Periods, and the provider's weekly
Labs-update claim remain separate time axes.

Current documentation itself contains contradictory or suspicious copy that the future real
Capture must arbitrate rather than the Recipe silently "repairing": `keyword_data.serp_info`
is documented as an array while the provider example shows an object; `rank_changes.is_new`
contains contradictory prose; and some ETV/clickstream/AI-Overview descriptions appear to
reuse text from different grains. These are provider-documentation defects, not license to
guess the wire contract.

### Completeness and one-Capture limit

`total_count`, `items_count`, aggregate metric counts, and returned item counts are different
claims. The first request intentionally returns only the rank-group-sorted prefix with
`limit=100`, `offset=0`. It is reconnaissance Evidence, not a complete corpus capture and not a
representative sample of every requested SERP type or lost state. No continuation or automatic
offset follow-up is authorized.

One future Capture can establish existence and exact observed shapes only for its request. It
cannot establish provider invariance, all nullability/state domains, all requested result-type
shapes, lost-item shape if none is returned, device/OS of the Labs index, the provider's true
prior-check interval, equivalence with Google Organic/Keyword Overview/Related Keywords/LLM
Mentions, or any Strategy conclusion.

### Transport and spend lock for the later probe ticket

The first contract fits the existing HTTP event-v2 single-exchange Evidence spine. The future
Ranked adapter must create its **own Ranked-local closure-owned issuance and consumption gate**
from the modern provider-probe precedents; do not reuse another surface's private gate or
introduce a generic capability framework. Reuse PF-09 bounded transport and the established
Attempt-before-send / at-most-one-Capture / credential boundary.

The current bounded transport proposal is:

- timeout: connect 30 / read 120 / write 30 / pool 30 seconds;
- response-body ceiling: 33,554,432 bytes (32 MiB);
- one fresh Evidence root;
- one POST, one task, no redirect/retry/poll/continuation/follow-up;
- Evidence-only first implementation: no parser, Recipe, schema, Derivation, PostgreSQL, or
  consumer API.

Current official Labs Google pricing rechecked on 2026-09-01 lists "all other endpoints" at
`$0.012` per Live task plus `$0.00012` per returned item. At the closed `limit=100`, the
published arithmetic is approximately `$0.024` before any provider pricing change. The later
probe ticket may use a conservative authorization ceiling of **50,000 micro-USD ($0.05)**,
but current pricing and the exact closed request must be rechecked immediately before any
real-call authorization. This record does not authorize spend.

### F13 reconciliation relevant to Ranked

The independent review correctly warned against reusing an older caller-visible transport
capability gate, but its list of currently affected precedents was stale. `PF-16` already
hardened Keyword Overview and `PF-17` already hardened Google Organic with surface-local
closure-owned issuance/consumption and committed-Attempt revalidation. Search Mentions remains
separately F13-gated if it is ever reused. Ranked Keywords does not need to fire F13 because it
will be a new adapter born with its own closure-owned gate; it should use the modern pattern
without importing another adapter's semantics.

### Deferred acquisition from the first probe

- **Clickstream** — omits that weekly snapshot's clickstream ETV/demographics/normalized
  structures. Revisit only if a downstream consumer needs this provider's independent demand
  model and the retention/privacy posture is explicitly accepted.
- **Exact-page target** — omits page-as-request-subject corpus/aggregate testimony. Revisit
  when a consumer needs page-scoped holdings/history rather than page URLs discovered inside a
  domain request.
- **Subdomain target** — omit until subdomain is an explicit consumer subject.
- **Dedicated live/lost calls** — omit unless first `all` Evidence cannot expose the material
  lost-item shape despite provider testimony that a lost population exists.
- **`ignore_synonyms=true`** — omit because the first contract needs duplicate/near-duplicate
  testimony; revisit only for a separately useful synonym-suppressed provider contract.
- **filters/custom sorting/offset/limit 1000** — omit because they primarily change which
  corpus prefix is sampled, not a currently proven material response branch. Revisit from
  Evidence or later acquisition requirements, not curiosity.
- **unscoped location/language** — not a future form of this adapter; mixed-locale testimony is
  a materially different contract.

### Remaining Product questions for [CHAZ]

1. **Exact first domain target.** It should be a public, non-sensitive, stable registrable
   domain with meaningful US/English ranking breadth, likely `total_count > 100`, and enough
   ranking variety/volatility to give movement/lost and non-organic/AI-Overview testimony a
   reasonable chance of appearing. Do not choose a domain merely because the provider example
   uses it.
2. **SERP-text Evidence retention acknowledgement.** Ranked Keywords may return titles,
   descriptions/snippets, XPath and AI Overview reference text. Google Organic has already
   established that equivalent SERP prose may be preserved as immutable provider Evidence
   under an explicit retention/terms posture; serving or semantically promoting that text later
   remains a separate Recipe/API decision. [CHAZ] must explicitly confirm that the Ranked probe
   may preserve the exact provider response body containing this text before a real call is
   authorized.

After those two Product choices, the Steward may mark this activation review accepted/closed
and cut the separate bounded first-probe implementation ticket. No provider call is authorized
by RANK-01 itself.

## Product resolution and closure — 2026-09-01

[CHAZ] accepted the Steward recommendations and resolved the two remaining Product choices:

- first later live-capture candidate target: exact domain `theconspiratory.com`;
- exact provider response-body Evidence retention is accepted even when the Ranked Keywords
  response contains SERP titles, descriptions/snippets, XPath, or AI Overview reference text.

The target is selected for contract-learning continuity with the existing conspiracy-themed
provider reconnaissance rather than as a Strategy judgment. RANK-01 does not claim the domain
will exercise every requested result type or lost/movement branch; that remains empirical.
The implementation adapter should not silently generalize subdomain/page targets from this
choice. A separate later activation ticket must freeze the exact live request again before
credentials, spend, provider transport, or Evidence creation.

The retention choice authorizes preservation of exact provider bytes only when a later live
call is separately authorized. It does not authorize consumer API exposure, semantic promotion,
Strategy use, redistribution decisions, or additional text acquisition beyond the exact bounded
Ranked Keywords response.

RANK-01 is accepted and closed. The next work unit is a separately reviewed, Evidence-only
Ranked Keywords Live paid-probe adapter ticket. No provider call, credentials, spend, or new
Evidence is authorized by this closure.
