# DataForSEO Surface Roadmap

**Status:** product-direction inventory; not implementation or spend authorization  
**Provider:** DataForSEO  
**Capability snapshot verified:** 2026-08-16 against the official DataForSEO API v3
documentation

## Purpose

Observatory is intended to preserve the useful provider testimony that a downstream SEO/GEO
strategy system may need for historical analysis, opportunity discovery, gap analysis,
competitive analysis, and AI-search visibility analysis. DataForSEO exposes substantially
more useful testimony than the first Keyword Overview probe.

This document records the DataForSEO **surface direction** so later sessions do not have to
rediscover which provider datasets matter. It does not authorize an adapter, provider call,
spend, schedule, bulk collection, or schema. Every implemented surface still requires a
bounded decision/ticket and must obey the existing Attempt → Capture → Evidence → Derivation
→ Observation lifecycle, D11 recipe identity, and provider-specific API semantics.

The list is intentionally about testimony we may want, not about reproducing the complete
DataForSEO catalog. Broad, materially useful coverage is product direction; this inventory
does not rank whether a family deserves to exist. Build and activation order may change as
architecture dependencies, provider contract shape, historical uniqueness, overlap,
acquisition safety/cost, and implementation complexity are rechecked.

## Selection principles

- Prefer provider testimony that is historically queryable, difficult to reconstruct later,
  or uniquely useful to SEO/GEO analysis.
- Preserve source-specific meaning instead of forcing unlike Google, YouTube, backlink, or
  LLM metrics into one universal score.
- Preserve exact request context, provider time, data period, model/search surface, location,
  language, device, and other measurement context when they affect meaning.
- Treat DataForSEO-computed metrics, classifications, intent, sentiment, traffic estimates,
  and AI-search metrics as attributed provider testimony, not Observatory conclusions.
- Avoid redundant collection merely because two endpoints expose overlapping fields. Use
  the surface with the best historical coverage, context, cost, or measurement value, and add a
  second source only when its independent testimony is useful.
- Historical provider databases and active measurements are different observations. For
  example, an indexed LLM Mentions record and a newly requested LLM response are not the
  same kind of fact.
- Provider catalogs, account data, pricing, and status endpoints are operational metadata;
  they do not automatically become SEO/GEO Observations.
- Provider methodology/changelog and measurement-context catalogs may still be meaning-bearing
  operational/context testimony when they explain a series break, supported model/location,
  or acquisition meaning; preserve or cite them as context rather than keyword-like facts.
- Prefer exact records and relationships over summary counts when the relationships are what
  later reasoning needs: exact ranked/cited/referring/target URLs, source order, discovery
  parent→child relationships, and provider-native place/video/channel/entity identifiers.
- Preserve the exact raw URL and request context as testimony. Any URL normalization or
  cross-surface equivalence is versioned and rebuildable rather than silently becoming
  Evidence identity.
- Similar words do not imply identical facts across surfaces. A web/content-analysis
  citation is not an LLM citation; a Google video SERP item is not a YouTube Organic result;
  provider-modeled AI demand is not direct LLM query-log demand.
- Intentional cross-surface overlap can be more valuable than unrelated panels: measuring the
  same supplied subject/query across demand, SERP, AI, video, or other relevant surfaces can
  support later joins. The intended coordinated set remains downstream/orchestration policy,
  not an Observatory priority-panel identity.

## Surface activation review

Before authorizing a new DataForSEO surface, the Steward reviews the **current complete
provider capability family**, not only the first endpoint name that appears useful. The
review records enough information to choose deliberately among overlapping endpoints and
request options:

- what questions the surface can answer for SEO, GEO, SERP visibility, competitor analysis,
  opportunity/gap discovery, and downstream LLM reasoning;
- every materially useful returned field/relationship, provider-native identifier, and
  exact request option/enrichment that enables it;
- requested subject/context versus provider-returned or normalized identity where those can
  differ;
- historical availability, provider update cadence, data periods, and active-vs-indexed
  measurement semantics;
- location, language, device, model/platform, search-surface, domain/page/entity, and other
  context that changes meaning;
- overlap with already collected DataForSEO testimony and whether the independent source or
  methodology adds useful evidence rather than redundant cost;
- task/live/standard/asynchronous alternatives and whether the contract is one exchange or
  requires task submission, polling, continuation, or multiple result fetches;
- corpus/completeness semantics: provider total count, returned count, requested limit/depth,
  offset/token/continuation, sampling/prefix behavior, and Observatory transport truncation;
- the response-size bound appropriate to this adapter contract rather than silently treating
  D10's 8 MiB bound as a permanent global limit;
- expected cost and operational complexity;
- whether text-rich or personal-data testimony requires an explicit retention, privacy,
  provider-terms, or API-redistribution decision before acquisition;
- which useful testimony should become typed Observations now, which can remain preserved in
  raw Evidence for later recipes, and which fields are operational noise rather than
  strategy-relevant provider testimony.
- what an empty consumer response means and how the API distinguishes unmeasured, failed,
  incomplete, admitted-zero, and admitted-empty states;
- how list limits disclose total matching records, returned records, and whether more records
  exist rather than silently presenting a bounded slice as the complete history;
- when identity includes rank, position, or array index, how a consumer can honestly track
  the same URL, domain, question, or other stable subject across Captures;
- which materially useful, historically irrecoverable testimony is deliberately not
  requested and what trigger would justify revisiting that non-acquisition.

The purpose is not to maximize field count. It is to avoid discovering later that a cheap,
historically valuable, or strategically important provider dimension was available but was
never captured or was discarded because the first adapter was unnecessarily thin.

A task/poll/continuation or other multi-exchange contract requires explicit provenance for
how later requests depend on earlier provider testimony before that workflow is accepted.
D9's `prior_attempt_id` must not be overloaded to claim that dependency. This prerequisite
does **not** freeze bounded one-exchange Live contracts whose request and completeness can be
stated honestly under the current HTTP event model.

### Evidence-first activation method

Surface inventory and provider probing are different activities. Inventory reviews the
relevant capability family broadly enough to understand what testimony exists, what request
options can change it, and what historical dimensions could be permanently missed. It does
not authorize a call. A real Provider contract probe is authorized only for one named adapter
contract when an unexercised branch can materially change response shape/cardinality,
identity/reconciliation, field state, numeric/time/data-period semantics, pagination, or
failure behavior.

For an activated contract, design proceeds in this order:

1. state the analytical purpose the testimony could serve downstream;
2. review the current claimed provider contract and materially different modes;
3. authorize the smallest useful real probe set under the normal Evidence/spend gates;
4. preserve exact responses as Evidence and inspect what was actually returned;
5. author the closed Derivation Recipe, typed IR, Observation kinds, identities, times,
   field states, and diagnostics from the claimed contract plus verified testimony;
6. copy exact verified bytes into deterministic Conformance fixtures and test zero-network;
7. type only testimony whose semantics can be stated honestly; leave other returned facts
   available in raw Evidence for later recipes;
8. record a deliberate non-acquisition when a known historically irrecoverable dimension is
   not captured, together with the trigger for revisiting it.

The rule is **inventory broadly enough not to miss irreversible choices; probe narrowly
enough that each paid exchange teaches a material contract branch**. Raw Evidence protects
against under-modeling of returned data, not against data that was never requested. PF-03
already satisfies the live Keyword Overview reconnaissance step for its exact closed adapter;
PF-05 continues from that Evidence and does not restart exploration.

## Broadly useful measurement families

These families are expected to be broadly useful to downstream Strategy and are intended
eventual coverage candidates. Their order in this document is not activation priority; each
adapter contract still passes D12 review and separate authorization.

### 1. DataForSEO Labs — Google keyword research and historical demand

**Current first surface:** Google Keyword Overview is already captured by PF-03 and is the
PF-04 through PF-08 foundation run.

Additional expected keyword-research testimony:

- Keywords For Site — provider-discovered keywords relevant to a domain;
- Related Keywords — related-query discovery;
- Keyword Suggestions — lexical/seed expansion;
- Keyword Ideas — category/relevance-based expansion;
- Bulk Keyword Difficulty — provider difficulty testimony at scale;
- Search Intent — provider intent classification at scale;
- Historical Keyword Data — historical search-demand and related keyword metrics.

These surfaces support discovery and expansion of the universe of keywords/topics before
the downstream strategy layer decides which opportunities matter.

### 2. DataForSEO Labs — Google competitor, ranking, and domain history

Expected testimony includes:

- Ranked Keywords;
- SERP Competitors;
- Competitors Domain;
- Domain Intersection and Page Intersection;
- Relevant Pages;
- Domain Rank Overview;
- Historical SERPs;
- Historical Rank Overview;
- Bulk Traffic Estimation and historical traffic-estimation variants where useful.

This family is intended to let downstream consumers ask what domains/pages ranked, which
queries overlapped, how visibility changed, and where competitors gained or lost apparent
search exposure without Observatory itself deciding what action to take.

### 3. AI Optimization — LLM Mentions

**Current bounded surfaces:** Search Mentions is implemented through Recipe selection,
history, Measurement Outcomes, and Holdings. Target Metrics is implemented through typed
Derivation, Recipe selection, and its admitted-history API; Target Metrics Measurement
Outcomes and Holdings remain separately gated. Multi-Target Metrics, top-mentioned,
Historical, Timeseries, and other family members remain future direction under separate
activation.

This family is expected to be one of Observatory's most valuable GEO datasets because
DataForSEO maintains provider-side AI-search/LLM mention testimony rather than requiring
Observatory to create every observation itself.

Expected useful surfaces include:

- Search Mentions;
- Target Metrics and Multi-Target Metrics;
- Top Mentioned Pages;
- Top Mentioned Domains;
- Top Mentioned Brands and brand categories;
- Historical;
- Timeseries Delta;
- Timeseries New & Lost;
- Lite variants only when they provide a materially better cost/coverage tradeoff.

Useful testimony can include keyword/brand/site mentions, cited or source domains/pages,
AI-search-volume style metrics, answer/source context, model/platform context, and historical
change. Exact fields and supported platforms remain recipe- and endpoint-specific.

The downstream strategy layer may later use these observations to find citation gaps,
competitor visibility, source/domain patterns, growing or declining AI visibility, and
topics with AI-search demand. Those conclusions remain downstream; Observatory preserves
the testimony.

Search Mentions is indexed response/source testimony, not a historical archive of prior
answer and citation sets. Its current contract is paginated and exposes total/returned
counts plus offset/continuation state. Historical and timeseries endpoints provide
aggregated mention/AI-search-volume history; their counts do not reconstruct an earlier
answer body or citation set. If answer/source-set history matters, Observatory needs
deliberate repeated Captures of the appropriate record-bearing contract.

### 4. AI Optimization — AI Keyword Data

Expected use: provider-modeled AI Search Volume and trend testimony. The currently documented
AI Search Volume calculation uses statistical data from questions in Google's People Also Ask
SERP element, so this is attributed provider estimation—not direct LLM query-log demand and
not citation testimony.

This is independent from traditional Google search demand. The strategy layer should be
able to compare the two without Observatory claiming they measure the same population.

### 5. AI Optimization — LLM Scraper and LLM Responses

These are active-observation surfaces and must remain distinct from DataForSEO's accumulated
LLM Mentions dataset.

- LLM Scraper: structured observations of supported AI search experiences for specified
  queries, including returned answer/source testimony where exposed.
- LLM Responses: structured responses to specified prompts from supported model families.
  The provider currently documents ChatGPT, Claude, Gemini, and Perplexity response
  families; exact model/version is measurement context and must be preserved.

Likely uses include repeatable benchmark panels, citation/source observation, brand/entity
presence, answer drift, and cross-model comparison. Scheduling, prompt-panel ownership, and
how frequently to repeat active LLM observations remain separate decisions.

### 6. SERP API — Google search surfaces

Expected core search observation surfaces:

- Google Organic rankings and SERP features;
- Google AI Mode;
- Google Maps / Local Finder when local-search measurement is required;
- other Google SERP feature families when their distinct testimony is materially useful.

SERP observations are point-in-time measurements with exact query/location/language/device
context. Historical DataForSEO Labs testimony and newly captured SERPs must remain distinct.

### 7. SERP API — YouTube

Expected useful YouTube testimony includes:

- YouTube Organic search results/rankings;
- Video Info;
- Subtitles when textual/video-topic analysis requires them;
- Comments only when their testimony is materially useful and the text-retention gate is accepted.

YouTube search interest/rank behavior is not Google search demand and must retain its own
surface identity.

A Google Organic SERP video item and a YouTube Organic result are different provider facts;
they may be joined through `video_id` when the provider actually exposes that identifier.

### 8. Backlinks API

Expected useful backlink testimony includes:

- Summary and History;
- detailed Backlinks;
- Anchors;
- Domain Pages / page summaries;
- Referring Domains and Referring Networks;
- backlink Competitors;
- Domain/Page Intersection;
- Timeseries Summary and New & Lost history;
- bulk rank/backlink/referring-domain/spam-score summaries when they materially reduce
  acquisition cost for known targets.

The goal is historical source/link testimony and provider-computed backlink metrics, not an
Observatory link-authority score.

### 9. Keywords Data / Trends / Clickstream

Expected comparison or complementary demand testimony includes:

- Google Ads search-volume and keyword-discovery surfaces when their independent datasource
  adds value beyond Labs;
- DataForSEO Trends Explore and related regional/demographic/merged trend testimony;
- Clickstream search-volume/global/bulk demand estimates where available and useful.

These are especially useful when independent demand estimates or trend shapes can reveal
gaps that one keyword database alone would hide. Overlap with Labs must be evaluated before
collecting redundantly.

## Additional materially useful measurement families

These remain part of the coverage map; their activation is dependency- and contract-driven,
not conditional on a consumer first proving that the family deserves to exist.

### Content Analysis API

Candidate testimony: citation/search results, citation summaries, sentiment, rating
distribution, phrase trends, and category trends. Useful for broader brand/entity mention
and sentiment history beyond LLM-specific visibility. A Content Analysis citation is broader
web/content-analysis testimony and must not be collapsed into an LLM citation.

### Business Data API / Business Listings

Candidate testimony for local SEO: business listings, public business profile information,
categories, ratings/reviews, business updates, and other location-specific public business
data exposed by an accepted endpoint. This is a materially useful local-search family; its
activation still requires a closed subject/geography/review contract.

### OnPage API

Candidate technical-site testimony: crawl/page summaries, indexability, duplicate content,
links, redirects, resources, structured data/microdata, performance/Lighthouse-style data,
and content parsing. Bounded page/content/technical state is valid Observatory measurement
when deliberately acquired as source-attributed historical testimony. DataForSEO OnPage is
one possible instrument; the product boundary does not require it to be the only instrument
or require a crawler merely because the provider offers one.

### Domain Analytics

Candidate supplementary testimony: technologies used by a domain and Whois/domain context.
Useful for competitor/site profiling when its independent measurement value justifies the
contract and acquisition cost.

### Labs market/category analysis

Categories For Domain, Keywords For Categories, Domain Metrics By Categories, Top Searches,
and related market-category endpoints remain candidates where category/market discovery adds
material testimony beyond ordinary keyword/domain research.

## Specialized families retained as candidates

These are not rejected and do not require an immediate consumer ticket merely to remain in
the future coverage map. Activation still requires a later review showing material value to
Observatory's search/AI visibility scope and the same bounded D12 contract discipline:

- Merchant / Google Shopping / Amazon product-price monitoring;
- DataForSEO Labs Amazon product research;
- Google Play and App Store app-intelligence surfaces;
- hotel/travel-specialized business datasets;
- finance, jobs, events, image-search, advertiser, or other specialized SERP families that
  have not yet shown material value to Observatory's visibility scope;
- full provider database downloads as a substitute for the Observatory API/Evidence model.

If later review establishes material value, the surface receives the same bounded
Evidence/Derivation review and authorization as any other adapter.

## Strategy-consumer retrofit sequence

The current retrofit reviews implemented provider surfaces from the viewpoint of a future
strategy LLM that can use only the versioned API. Reviews remain surface-specific, while a
genuinely shared API defect may be remediated once across affected surfaces after each has
been inspected. The sequence is:

1. keep agent onboarding and this roadmap aligned with the consumer-readiness contract;
2. perform a full read-only Keyword Overview review as the first complete API template;
3. reconcile a proposed shared provider-history contract covering Outcome visibility,
   observed-subject discovery, list completeness, limitations, and provider Attempt audit;
4. review Google Organic and Search Mentions against that proposal, preserving their
   different fact grains and provider semantics;
5. after explicit [CHAZ] selection, implement shared API corrections in one bounded ticket
   where behavior is truly shared and use separate tickets for surface-local changes;
6. complete the Target Metrics code-first review and AI-12 admitted-history design from the
   accepted contract rather than copying another surface;
7. review future provider capability families when they approach bounded activation, then
   select individual adapters rather than treating this roadmap as implementation order.

Each full surface pass is read-only first: [GROK] inspects code, tests, schema, fixtures, and
API behavior; [GPT] independently verifies and reconciles the findings; [CHAZ] decides what
should change; only then does the normal reviewed-ticket implementation loop begin. No step
authorizes a provider call, spend, recurring acquisition, strategy state, or F5/F12 work.

The **question-resolution gate** runs before each major surface-review, remediation, or
implementation prompt: [GROK] inspects the actual code and raises uncertainties; [GPT]
independently verifies, consolidates, and separates technical from Product questions;
[CHAZ] resolves Product choices; [GROK] gives only a bounded technical reaction when needed;
and [GPT] locks the decisions before issuing the major prompt. Questions discovered later
are resolved before remediation or closure rather than causing repeated large-prompt
rewrites.

### Accepted shared provider-consumer contract

Keyword Overview established this boundary; Google Organic and Search Mentions subsequently
confirmed it with their surface-specific semantics:

- surface-explicit Observation history contains admitted, subject-bound documents only;
- a sibling Outcomes resource exposes all measurement classifications without pretending
  failures are Observations;
- a holdings resource exposes observed subjects and measurement inventory, not importance,
  desired panels, cadence, or strategy;
- every bounded list discloses scope, total matching, returned count, applied limit,
  deterministic order, and whether more matching records exist;
- per-adapter paths may share a lossless list envelope, while fact bodies and valid
  admitted-empty semantics remain surface-specific;
- subject-indexed failure inventory is not assumed to be API-only: Keyword Overview retains
  failed subjects in verified Attempt Evidence, not current typed PostgreSQL rows.

All three reviews confirm that current PostgreSQL does not retain requested-subject identity
for every non-admitted path. A bounded verified-Evidence scan remains a possible low-volume
bridge, but recurring F12-scale acquisition requires a scalable rebuildable
measurement-subject index. API-02 and API-03 implement that bounded scan as the current
Outcomes/Holdings bridge. No coverage row may be invented for a failure or zero-envelope
Capture, and no consumer receives direct Evidence access. D14 records the accepted decision.

Google Organic confirms the contract with a real subject-bearing admitted-empty document,
accepted placement identity with URL as content, and the same Evidence-only failure-subject
gap as Keyword Overview. Its prose remains Evidence-only. Non-null `related_result` is a
stop-before-derive trigger for any newly encountered Capture. The completed Outcomes ledger
proves Observation-envelope cardinality. The completed D14 resources type the shared outer,
Outcomes, and Holdings contracts; full typing of nested history fact bodies remains a
separately gated surface-local boundary.

Search Mentions confirms the contract while preserving a uniquely rich returned-prefix fact
document: exact question/answer text, structured source URLs and occurrences, current and
monthly volume testimony, and explicit inner corpus/truncation state. The AI-03 prefix
contains five item, sixty monthly, and forty-eight source envelopes;
`observation_count=113` is their envelope cardinality, not provider `items_count` or corpus
size. The database/API preserve those returned facts faithfully. API-01, API-02, and API-03
corrected the shared silent outer Capture slice and added typed Outcomes and Holdings
resources. Full nested history fact-body typing remains separate. No Recipe, identity,
text-exposure, pagination, or provider-acquisition change followed from the retrofit.

**Current checkpoint — 2026-08-25:** The D14 retrofit is complete for Keyword Overview,
Google Organic, and Search Mentions. API-01 closed the shared history-list envelope; API-02
closed subject-filtered Measurement Outcomes; API-03 closed Evidence-backed Holdings.
The accepted limits remain: no outer cursor/offset or retrieval beyond 100, no Holdings
subject/scope filter or direct event link, separate history/Outcomes/Holdings meanings,
and the bounded store-wide Evidence scan as a low-volume bridge. AI-12 separately closed
Target Metrics Recipe selection and its fully typed admitted-history API; Target Metrics
Measurement Outcomes and Holdings remain separately gated. There is no active next
implementation ticket: future provider capability families require read-only review and
explicit selection under D12. This checkpoint authorizes no provider exchange, F12/F13
activity, strategy state, or further API/schema remediation.

## Dependency-based sequencing direction

PF-04 → PF-08 established the provider recipe/parser/Observation/API foundation. From that
foundation, sequencing minimizes rework and acquisition risk rather than ranking which
valuable measurement families deserve to exist.

- A bounded one-exchange Live contract may proceed on the current HTTP event model when its
  request and corpus/completeness boundary can be stated honestly.
- Task/poll, continuation, multi-GET, or site-crawl workflows wait for explicit
  multi-exchange provenance appropriate to that contract; they must not overload
  `prior_attempt_id` as response-derived parentage.
- Text-rich contracts wait for the accepted retention/privacy/provider-terms/API posture.
- Routine recurring irreplaceable acquisition does not outrun routine F6 protection.
- Subject sets, cadence, cross-surface coordination, promotion, and event-triggered recapture
  remain deferred acquisition-orchestration concerns under F12.
- Provider capability, overlap, cost, current contract stability, and learning value are
  rechecked before each bounded adapter/probe.

No fixed family order is authority. The next adapter is selected by readiness and learning
value under separate authorization, while the broader coverage direction remains intact.

## Provider-documentation snapshot used for this inventory

The 2026-08-16 review used the official DataForSEO API v3 documentation for these capability
families: AI Optimization; LLM Mentions; AI Keyword Data; LLM Responses; LLM Scraper;
DataForSEO Labs Google; SERP Google and YouTube; Backlinks; Keywords Data; Business Data;
Content Analysis; OnPage; and Domain Analytics. Provider capabilities are external and may
change; exact endpoint/schema truth is always re-verified when a surface is activated.

### Superseding near-term checkpoint — 2026-08-25

AI-13 closed the Evidence-only LLM Mentions Historical Live adapter without a provider
exchange or live Historical Evidence. [CHAZ] subsequently selected Historical as the next
active workstream and approved reuse of the accepted bounded manual F6 protection path
rather than new transport or backup machinery.

The next intended boundary is a separately gated one-shot Historical Evidence activation.
It requires a reviewed operator ticket, fresh contract/pricing recheck, an exact fresh
Evidence root and command, separate explicit [CHAZ] authorization, at most one POST with no
retry, local inspect/scrub, encrypted restic snapshot through the existing accepted remote,
fresh restore, scrub, and exact Evidence equality. This checkpoint does not itself authorize
transport or spend.

If accepted live Evidence results, anticipated sequencing is strict Historical parser and
Conformance fixture, then Recipe-addressed typed Derivation/persistence, then a
Recipe-selected admitted-history API. Those remain separate reviewed boundaries and may
change when the actual Evidence is inspected. Target Metrics Outcomes/Holdings, earlier
surface nested-body typing, other LLM Mentions families, F13 hardening, and F12 recurring
acquisition remain separately gated and are not Historical prerequisites.
