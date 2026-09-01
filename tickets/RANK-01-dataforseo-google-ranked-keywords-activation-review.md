# RANK-01 — DataForSEO Google Ranked Keywords activation review

**Status:** provisional review — awaiting independent [GROK] read-only code-first/provider-contract review  
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
