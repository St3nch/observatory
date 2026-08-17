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
DataForSEO catalog. Surfaces may move in priority as downstream consumers reveal which data
actually changes decisions.

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
  the surface with the best historical coverage, context, cost, or consumer value, and add a
  second source only when its independent testimony is useful.
- Historical provider databases and active measurements are different observations. For
  example, an indexed LLM Mentions record and a newly requested LLM response are not the
  same kind of fact.
- Provider catalogs, account data, pricing, and status endpoints are operational metadata;
  they do not automatically become SEO/GEO Observations.

## Surface activation review

Before authorizing a new DataForSEO surface, the Steward reviews the **current complete
provider capability family**, not only the first endpoint name that appears useful. The
review records enough information to choose deliberately among overlapping endpoints and
request options:

- what questions the surface can answer for SEO, GEO, SERP visibility, competitor analysis,
  opportunity/gap discovery, and downstream LLM reasoning;
- every materially useful returned field/relationship and which request options enable it;
- historical availability, provider update cadence, data periods, and active-vs-indexed
  measurement semantics;
- location, language, device, model/platform, search-surface, domain/page/entity, and other
  context that changes meaning;
- overlap with already collected DataForSEO testimony and whether the independent source or
  methodology adds useful evidence rather than redundant cost;
- task/live/standard/asynchronous alternatives, pagination/bulk limits, expected cost, and
  operational complexity;
- which useful testimony should become typed Observations now, which can remain preserved in
  raw Evidence for later recipes, and which fields are operational noise rather than
  strategy-relevant provider testimony.

The purpose is not to maximize field count. It is to avoid discovering later that a cheap,
historically valuable, or strategically important provider dimension was available but was
never captured or was discarded because the first consumer did not yet ask for it.

## Priority A — expected core provider testimony

These families are expected to be broadly useful to the downstream strategy system and are
the default candidates for future Observatory adapters after the current Keyword Overview
run proves the provider-Derivation foundation.

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

**High-priority future surface.** This family is expected to be one of Observatory's most
valuable GEO datasets because DataForSEO maintains provider-side AI-search/LLM mention
testimony rather than requiring Observatory to create every observation itself.

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

### 4. AI Optimization — AI Keyword Data

Expected use: provider estimates of keyword demand/trends in conversational or AI-search
interfaces, including AI keyword search-volume testimony and provider-stated intent/context
when exposed by the selected endpoint version.

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
- other Google SERP feature families only when a consumer needs their distinct testimony.

SERP observations are point-in-time measurements with exact query/location/language/device
context. Historical DataForSEO Labs testimony and newly captured SERPs must remain distinct.

### 7. SERP API — YouTube

Expected useful YouTube testimony includes:

- YouTube Organic search results/rankings;
- Video Info;
- Subtitles when textual/video-topic analysis requires them;
- Comments only when a consumer has a defined analysis requiring that testimony.

YouTube search interest/rank behavior is not Google search demand and must retain its own
surface identity.

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

## Priority B — valuable when the consumer/use case requires them

### Content Analysis API

Candidate testimony: citation/search results, citation summaries, sentiment, rating
distribution, phrase trends, and category trends. Useful for broader brand/entity mention
and sentiment history beyond LLM-specific visibility.

### Business Data API / Business Listings

Candidate testimony for local SEO: business listings, public business profile information,
categories, ratings/reviews, business updates, and other location-specific public business
data exposed by an accepted endpoint. This becomes important when a local-search consumer is
identified.

### OnPage API

Candidate technical-site testimony: crawl/page summaries, indexability, duplicate content,
links, redirects, resources, structured data/microdata, performance/Lighthouse-style data,
and content parsing. This is useful if Observatory becomes the shared historical source for
technical-site measurements; it is not required merely because DataForSEO offers it.

### Domain Analytics

Candidate supplementary testimony: technologies used by a domain and Whois/domain context.
Useful for competitor/site profiling when a real strategy workflow requires it.

### Labs market/category analysis

Categories For Domain, Keywords For Categories, Domain Metrics By Categories, Top Searches,
and related market-category endpoints are candidates when category/market discovery proves
useful beyond ordinary keyword/domain research.

## Not currently planned without a specific consumer trigger

These are not rejected forever; they simply are not part of the present SEO/GEO provider
roadmap:

- Merchant / Google Shopping / Amazon product-price monitoring;
- DataForSEO Labs Amazon product research;
- Google Play and App Store app-intelligence surfaces;
- hotel/travel-specialized business datasets;
- finance, jobs, events, image-search, advertiser, or other specialized SERP families that
  do not yet serve an identified Observatory consumer;
- full provider database downloads as a substitute for the Observatory API/Evidence model.

If a future consumer needs one of these, F3's broad-provider/surface trigger is revisited and
the surface receives the same bounded Evidence/Derivation review as any other adapter.

## Sequencing direction

The current PF-04 → PF-08 Keyword Overview run comes first because it establishes and proves
the provider recipe/parser/Observation/API machinery.

After that foundation is accepted, the default exploration order is:

1. LLM Mentions — highest-priority GEO historical/citation dataset;
2. AI Keyword Data — AI-query demand;
3. Google Organic + Google AI Mode SERP observation;
4. Labs keyword-discovery and competitor/history families;
5. Backlinks history and source graph testimony;
6. YouTube search/video testimony;
7. LLM Scraper / LLM Responses for active benchmark panels;
8. local Business Data, Content Analysis, OnPage, Domain Analytics, and category/market
   surfaces as consumer needs justify them.

This ordering is direction, not authorization. Cost, historical availability, provider
contract stability, overlap, consumer need, and learning value are rechecked before every
new adapter/probe.

## Provider-documentation snapshot used for this inventory

The 2026-08-16 review used the official DataForSEO API v3 documentation for these capability
families: AI Optimization; LLM Mentions; AI Keyword Data; LLM Responses; LLM Scraper;
DataForSEO Labs Google; SERP Google and YouTube; Backlinks; Keywords Data; Business Data;
Content Analysis; OnPage; and Domain Analytics. Provider capabilities are external and may
change; exact endpoint/schema truth is always re-verified when a surface is activated.
