# Freshness / Staleness Windows Research Report for The Observatory

## Executive Summary

The core result is simple: **freshness is evidence fitness, not truth**. Evidence does not become false merely because it is old, but its claim strength, safe uses, and comparison value change with time, volatility, context, and provider behavior. Fresh evidence can still be partial, delayed, sampled, or plain wrong; old evidence can still be the best evidence for trend, precedent, and “what was observed then.” Google explicitly warns that Search Console data can be preliminary and usually appears after a delay; Google also warns that AI Overviews and AI Mode can make mistakes. YouTube analytics can lag by days. Provider estimates such as search volume and traffic are updated on provider-specific cycles, not in real time. citeturn31view0turn34view5turn34view4turn33view12turn33view13turn32view2turn31view4

The fastest-aging evidence types are **live observation surfaces**: SERP snapshots, rank positions, SERP feature presence, local/map pack observations, AI answer/citation captures, marketplace search captures, and YouTube search result captures. These are highly context-bound. Google says search results differ by location, language, and device. Google AI Mode fans out a query into multiple searches; AI Overviews appear only when Google’s systems decide they are helpful; Microsoft Copilot Search, ChatGPT Search, Perplexity, and Gemini all ground responses in current web data or source links, but none of that makes a single capture stable or reproducible. Recent academic and tool-vendor studies found substantial day-to-day or rerun volatility in AI-source sets, even when brand mentions are more stable than citations. citeturn21search2turn21search14turn21search20turn34view4turn34view5turn31view8turn31view9turn31view10turn31view11turn25view0turn36view1turn36view0

The slowest-aging evidence types are **archival captures and bounded historical reports**: timestamped HTML snapshots, screenshots, provider policy pages as-observed, repo decisions, owner rulings, and first-party historical analytics within the provider’s retention window. Those remain useful for audit, change detection, and trend analysis. But they are often **stale for present-tense claims**. Etsy lets sellers view shop stats back to November 2017; Search Console and Bing Webmaster Tools expose up to 16 months of performance data; Shopify reports are near-real-time for many views; Pinterest explicitly notes that Pins can gain engagement months or years later. That makes history useful, not current by default. citeturn31view13turn35view0turn35view5turn32view10turn31view12turn32view13

Provider cadence matters because it sets an upper bound on what any observation can honestly claim. Search Console performance data is typically visible in two to three days and the last two days may be preliminary; Ahrefs updates backlinks every 15–30 minutes but keyword/SERP data can range from multiple times a day to every one to two months depending on popularity; Semrush updates keyword databases from daily to monthly depending on keyword popularity, search volume monthly, Authority Score every two weeks, and Position Tracking daily within 24–48 hours; DataForSEO updates keyword metrics monthly, SERPs on roughly 30–90 day cycles depending on query/location, and markets its backlinks database as a continuously updated live index; YouTube Reporting API files expire after 30–60 days depending on report type, and YouTube developer policies impose 30-day refresh/delete rules on many stored statistics. citeturn31view0turn31view2turn31view7turn32view0turn32view1turn31view3turn31view4turn31view5turn33view9turn33view10turn33view11

The practical implication for The Observatory is ruthless and boring in the best way: every evidence item needs, at minimum, a **capture timestamp, capture context, provider/source, surface, and freshness caveat**. Current-state claims should be blocked or heavily warned when they rely on stale high-volatility evidence. Comparisons across providers should record the capture-time distance and warn when the comparison is non-synchronous. Rights, pricing, and terms evidence should always be rechecked before action. Freshness doctrine should therefore be written as a **contract about safe use**, not as a universal refresh schedule. citeturn37view0turn37view1turn37view2turn32view8turn32view9

## Confidence and Source Quality

### Confidence and Source Quality

This report is strongest where providers publish explicit freshness behavior: Search Console latency, Ahrefs backlink refresh, Semrush Position Tracking cadence, DataForSEO keyword/SERP timing, YouTube reporting retention, Shopify analytics freshness, Etsy stats history, Pinterest Trends change windows, and Microsoft’s AI Performance preview caveats. Confidence there is **high** because the claims come from current vendor documentation or official vendor blogs/help centers. citeturn31view0turn31view7turn31view3turn31view4turn33view9turn32view10turn31view13turn32view12turn32view8

Confidence drops to **medium** for questions about true surface volatility of Google SERPs, AI citations, and marketplace search because providers do not publish a clean “changes every X hours” rule. For those areas, this report uses current third-party studies and academic work, but treats them as evidence of behavior under sampled conditions, not universal law. The AI-volatility evidence is especially mixed: an arXiv paper found low day-to-day overlap in cited sources; Ahrefs reported frequent AI Overview churn; BrightEdge found that most tracked domains were stable week-to-week at aggregate level, while changes were typically binary and negative when they occurred. Those results are not contradictory so much as differently scoped: **per-prompt day-to-day instability can coexist with aggregate domain-level week-over-week stability**. citeturn25view0turn36view1turn36view0

This report marks several areas as **Unclear — needs confirmation** because current official documentation did not state a verified cadence or retention rule in the sources reviewed. That includes exact Google SERP update cadence, exact YouTube public-statistics latency, exact public YouTube search-result refresh cadence, exact Pinterest Analytics latency/retention, and exact customer-visible retention windows for some AI visibility reports. That uncertainty is not a bug. It is the point. The Observatory should encode unknown cadence as a warning state, not a hidden assumption. citeturn34view5turn8search15turn35view7turn32view8turn32view9

### Source List

All sources below were accessed on **July 10, 2026**.

| Source | Type | Used for | Link |
|---|---|---|---|
| Google Search Console Performance report help | Official | Search performance metrics and date-range behavior | citeturn35view1 |
| Google Search Console Discover performance help | Official | Search Console latency and preliminary-data warning | citeturn31view0 |
| Google Search Central blog on hourly Search Analytics API | Official | Hourly GSC data, 10-day hourly window, partial hourly state | citeturn31view1 |
| Google Search Central blog introducing new Search Console | Official | 16-month Search Console history | citeturn35view0 |
| Search Console data anomalies page | Official | Caveat that report data can be affected by anomalies | citeturn35view2 |
| Google Search Help on differing search results | Official | Device/location/language context binding for SERPs | citeturn21search2turn21search14turn21search20 |
| Google Search Help on AI Overviews | Official | AI Overviews behavior and mistake warning | citeturn34view5 |
| Google Search Help on AI Mode | Official | AI Mode fan-out behavior and quality caveat | citeturn34view4 |
| Bing Webmaster Tools blog on 16 months history | Official | Bing Search Performance historical window | citeturn35view5 |
| Bing Webmaster AI Performance public preview | Official | AI citation reporting, aggregation, sample queries, preview caveats | citeturn32view8 |
| Bing Webmaster AI visibility update | Official | Preview/early-stage caution and evolving signal quality | citeturn32view9 |
| Microsoft Support on Copilot web mode | Official | Bing-index grounding for web-mode Copilot | citeturn34view3 |
| Ahrefs help on links database updates | Official | Backlink refresh cadence | citeturn31view7 |
| Ahrefs help on keyword/Site Explorer data updates | Official | Keyword/SERP update variability by popularity | citeturn31view2 |
| Ahrefs help on organic traffic calculation | Official | Estimated monthly traffic and uneven update timing | citeturn33view0turn33view1 |
| Ahrefs help on SERP updates and KD refresh | Official | Manual refreshability of keyword/SERP evidence | citeturn33view2turn33view4 |
| Ahrefs Brand Radar / custom prompt docs | Official | AI visibility report and prompt-tracking cadence | citeturn32view6turn32view7 |
| Semrush Data & Metrics | Official | Keyword-database update cadence | citeturn32view0 |
| Semrush Search Volume doc | Official | Monthly search-volume updates and history to 2012 | citeturn32view2 |
| Semrush Authority Score doc | Official | Biweekly authority-score updates | citeturn32view1 |
| Semrush Position Tracking docs | Official | Daily update cadence and historical storage model | citeturn31view3turn32view3 |
| Semrush backlinks update doc | Official | Backlink discovery timing, interface refresh, fresh index | citeturn31view6 |
| Semrush AI Visibility docs | Official | Daily rolling AI visibility refresh | citeturn32view4turn32view5 |
| DataForSEO Labs API update-time doc | Official | Monthly keyword metrics and 30–90 day SERP cycles | citeturn31view4 |
| DataForSEO search-volume timing doc | Official | Google/Bing source timing for keyword data | citeturn33view6turn33view7turn33view8 |
| DataForSEO live-index help | Official | Continuously updated live backlink index | citeturn31view5 |
| OpenAI ChatGPT Search launch post | Official | Timely web answers with links | citeturn31view8 |
| OpenAI API web-search guide | Official | Up-to-date web search with sourced citations | citeturn34view2 |
| Perplexity Search API / Search docs | Official | Real-time access, continuously refreshed index, date and last_updated fields | citeturn31view9turn34view0turn34view1 |
| Copilot Search in Bing launch post | Official | Clearly cited sources and answer grounding | citeturn31view10 |
| Gemini source-links help | Official | Related sources in Gemini responses | citeturn31view11 |
| YouTube Analytics help | Official | Analytics delay of a few days; earnings delay about 2 days | citeturn33view12turn33view13 |
| YouTube Analytics and Reporting docs | Official | Analytics API targeted queries, Reporting API retention windows | citeturn34view7turn33view9turn33view10 |
| YouTube Developer Policies | Official | 30-day refresh/delete rules for stored statistics | citeturn33view11 |
| YouTube Data API revision history / channels docs | Official | Shorts viewCount methodology change affecting comparability | citeturn9search12turn8search5 |
| Etsy Stats help | Official | Stats history from Nov 2017; hourly recent stats | citeturn31view13turn35view6 |
| Fiverr analytics and gig-management help | Official | Real-time analytics and gig impression/click metrics | citeturn32view11turn35view10turn35view11 |
| Shopify analytics and report docs | Official | Near-real-time analytics and report caveats | citeturn32view10turn31view12turn35view8turn35view9 |
| Pinterest Trends / Analytics / Pin performance help | Official | Weekly/monthly/yearly trend views, pin longevity, analytics overview | citeturn32view12turn35view7turn32view13 |
| arXiv paper on measuring visibility in AI search | Academic | Day-to-day and rerun AI citation instability | citeturn25view0turn26view0 |
| Ahrefs study on AI Overview churn | Third-party current study | AIO persistence and citation changes | citeturn36view1 |
| BrightEdge study on week-to-week AI citation stability | Third-party current study | Aggregate stability with binary loss dynamics | citeturn36view0 |

## Research Findings

### Freshness / Staleness Concept

A practical vocabulary for The Observatory should distinguish between **capture age** and **safe use**. The table below is a candidate working glossary, not doctrine.

| Term | Working definition |
|---|---|
| Freshness | How fit an observation is for a specific use at the time of reading |
| Staleness | The degree to which an observation’s safe uses have narrowed as it ages |
| Volatility | How much the observed surface can change across time, context, or rerun |
| Reporting delay | Time between the underlying event and provider visibility |
| Provider update cadence | How often the provider recomputes, refreshes, or republishes the data |
| Capture timestamp | When the observation was actually recorded |
| Observation half-life | Approximate period after which the evidence loses a meaningful share of its strength for a given use |
| Stale-for-claim | Too old or too unstable to support a present-tense claim safely |
| Stale-for-comparison | Too old or too asynchronous to compare fairly with another observation |
| Stale-for-customer-facing-use | Too old, caveated, delayed, or context-poor for safe external communication |

**Inference:** Evidence age is not the same as evidence uselessness. A three-month-old SERP snapshot may be weak evidence for “this ranks now,” but strong evidence for “this was observed on that date.” A same-day AI answer may be current but still weak evidence if the prompt, account, location, model, or retrieval context is missing, or if the surface itself warns that responses may contain mistakes. Search Console’s last two days may be preliminary; YouTube analytics can lag by days; Google AI responses may be wrong. Fresh does not mean correct. Old does not mean dead. citeturn31view0turn33view13turn34view5turn34view4

**Required principle:** Evidence does not become false merely because it is old, but its claim strength and use cases change as it ages. Official analytics tools themselves prove the point by preserving historical windows precisely because older data still matters for trend and diagnosis. Search Console and Bing expose 16 months; Etsy exposes stats back to November 2017; Semrush and Shopify support period comparison; Pinterest says Pins can keep resurfacing over months or years. citeturn35view0turn35view5turn31view13turn29search0turn32view13

**Inference:** Staleness depends on intended use because “current-state claim,” “trend claim,” “historical audit,” and “provider-change detection” are not the same job. A policy page captured six months ago may be perfect evidence that the policy once said X, but unacceptable support for “the current terms allow X” if the provider can change terms with notice or even immediately for some legal or functional reasons. YouTube’s API terms expressly allow modification of the agreement, and YouTube site policies may be updated from time to time. citeturn37view1turn37view2

The Observatory should therefore avoid false certainty by separating at least four things at read time: **what was observed, when it was observed, what provider/surface generated it, and what the evidence is still safe to support now**. That is the difference between a telescope and a horoscope. The database stores the sky photo; it should not pretend the stars are standing still. The funny part is that the lie usually starts with a missing timestamp. citeturn21search2turn25view0turn32view8

### Evidence Types Covered

The table below classifies the requested evidence types by likely volatility. Where provider docs were silent, the classification is marked as inference or unknown.

| Evidence Type | Likely Volatility | Basis | Practical note |
|---|---|---|---|
| SERP snapshot | Very high | Google results vary by location/language/device; Semrush Sensor measures daily volatility. citeturn21search2turn21search7 | Strong for “what was observed then,” weak for “what ranks now.” |
| SERP feature presence | High | Search features change with query and result context; daily SERP volatility is monitored by Semrush. citeturn21search7turn21search3 | Feature-on/feature-off claims age fast. |
| Rank position | High | Search results move; trackers refresh daily or weekly depending on tool. citeturn31view3turn6search1 | Current-rank claims require recent synchronized capture. |
| Local/map pack result | Very high | Local results depend on location; Semrush tracks local pack daily and map rank by map pin. citeturn21search2turn22search7turn22search18 | Hyper-contextual; national comparisons are dangerous. |
| Google AI Overview observation | Very high | AIO appears when Google decides it is helpful; responses may include mistakes; third-party studies show churn. citeturn34view5turn36view1 | Prompt/time/context-bound. |
| Google AI Mode observation | Very high | AI Mode fans out searches and may provide links only in some cases; responses may be wrong. citeturn34view4 | Repeatability is limited. |
| ChatGPT citation observation | Very high | ChatGPT Search provides timely answers with links; web-grounded behavior depends on search state. citeturn31view8turn34view2 | Capture prompt/context/model. |
| Perplexity citation observation | Very high | Perplexity uses real-time search from a continuously refreshed index. citeturn31view9turn34view1 | Capture query, filters, and result timestamps. |
| Bing Copilot citation observation | Very high | Bing/Copilot web mode is grounded in Bing web index and cited sources. citeturn31view10turn34view3 | Current web grounding does not equal reproducibility. |
| Gemini citation observation | Very high | Gemini may show sources/related links; source visibility can differ by response. citeturn31view11turn15search11 | Capture whether sources were shown. |
| Third-party AI visibility score | Medium to high | Ahrefs/Semrush update on daily/weekly/monthly track schedules depending on product. citeturn32view4turn32view6turn24search2 | Estimate/reporting product, not ground truth. |
| Keyword volume estimate | Medium | Semrush monthly; DataForSEO monthly following Ads cycles; Ahrefs data freshness varies by keyword popularity. citeturn32view2turn33view6turn31view2 | Supports demand estimation, not exact live demand. |
| Keyword difficulty / competition score | Medium | Provider estimate derived from SERPs or ad data; can often be manually refreshed. citeturn33view3turn33view2turn31view4 | Ages with underlying SERP or ad-cycle refresh. |
| CPC / paid competition estimate | Medium | DataForSEO monthly on Ads cycle; Semrush averages across prior 12 months. citeturn33view6turn7search13 | Not a live auction readout. |
| Ahrefs/Semrush/DataForSEO domain metrics | Medium | Mixed cadences: backlinks fast, authority/traffic/visibility slower. citeturn31view7turn32view1turn31view5 | Metrics disagree across providers. |
| Backlink count | High | Providers crawl continuously but with different scopes and recrawl priorities. citeturn31view7turn31view6turn31view5turn5search20 | Fast-changing, provider-relative. |
| Referring domains | High | Same as backlink counts; depends on crawl/update state. citeturn31view7turn31view6turn31view5 | Better as comparative trend than exact fact. |
| Estimated organic traffic | Medium | Ahrefs monthly estimate; Semrush based on estimated monthly traffic. citeturn33view0turn33view1turn22search13 | Useful as estimate, not first-party truth. |
| GSC clicks/impressions/CTR/avg position | Medium | Official first-party, but delayed and sometimes preliminary. citeturn31view0turn35view1 | Strong for history inside retention window. |
| Bing Webmaster clicks/impressions/CTR/position | Medium | Official first-party, 16-month history, cadence less explicit in docs reviewed. citeturn35view5turn27search15 | Unclear exact delay — needs confirmation. |
| YouTube public video metadata | Medium | Metadata is mutable; policy and counting methodology can change. citeturn8search12turn8search5 | Title/description snapshots are time-bound. |
| YouTube Data API statistics | High | Public counters can change continuously; official exact latency not stated in reviewed docs. citeturn8search21turn8search5 | Unclear official public-stat delay — needs confirmation. |
| YouTube Analytics metrics | Medium | Official first-party, but delay of a few days; some revenue data delayed ~2 days. citeturn33view12turn33view13turn34view7 | Strong for channel history, not instant state. |
| YouTube search result observation | Very high | Search surface behavior is dynamic; official cadence not published in reviewed docs. citeturn8search18turn34view7 | Unclear — needs confirmation. Treat like live SERP evidence. |
| Google SERP video result | High | Google SERP context varies by device/query/location. citeturn21search2 | Usually ages like any SERP feature. |
| Etsy listing snapshot | Medium | Listings are editable; listing URLs remain stable after first publish. citeturn16search9turn16search20 | Good archival evidence of listing state. |
| Etsy marketplace search result | High | Search visibility depends on listing state and marketplace context. citeturn16search1turn16search8 | Search observations age faster than listing snapshots. |
| Fiverr gig snapshot | Medium | Gigs have status changes and editable fields; gig can be paused/active. citeturn35view10turn17search2 | Stronger as as-observed listing evidence. |
| Shopify public product/page snapshot | Medium | Merchant can edit public pages at any time; public cadence not prescribed. Inference from platform mutability. citeturn32view10turn31view12 | Snapshot is durable; page state is not. |
| Pinterest trend/search observation | High | Weekly/monthly/yearly changes are surfaced; trends and engagement are seasonal. citeturn32view12turn32view13 | Time-bounded and often seasonal. |
| Marketplace SEO tool estimates | Unknown to medium | Cadence varies widely by provider; official marketplace-tool cadence often not stated. | Unclear — needs confirmation. |
| Public page HTML snapshot | Archival / durable | Inference | Excellent for “what this page said then.” Weak for “what it says now.” |
| Manual screenshot evidence | Archival / durable | Inference | Same as HTML snapshot, but with OCR/interpretation caveats. |
| Provider terms/rights/pricing docs | Low for history, F5 for action | Providers can update terms and pricing; documentation is time-sensitive. citeturn37view0turn37view1turn37view2 | Historical proof is durable; current-rights use requires recheck. |
| Owner rulings / repo decisions | Archival / durable | Inference | Usually durable as internal precedent; may still be superseded later. |

### Provider Update Cadence and Reporting Delay

The table below gives the main cadence facts needed for contract design. Where the official sources reviewed did not say, the entry is marked **Unclear — needs confirmation**.

| Provider / Source | Data Type | Update Cadence | Reporting Delay | Historical Window | Source | Caveat |
|---|---|---:|---:|---:|---|---|
| Google Search Console | Search performance report | Data published in intervals; hourly API now available | Usually 2–3 days; last 2 days may be preliminary | 16 months in report; hourly API up to 10 days | citeturn31view0turn31view1turn35view0 | Official first-party but not same-day final data |
| Bing Webmaster Tools | Search Performance | Unclear in reviewed docs; tool supports performance reporting | Unclear — needs confirmation | 16 months | citeturn35view5turn27search15 | Historical window is clear; exact latency is not |
| Bing Webmaster Tools | AI Performance | Preview reporting over aggregated AI citation signals | Unclear — preview and sampled/aggregated signals | Unclear — needs confirmation | citeturn32view8turn32view9 | Sample grounding queries; not a rank report |
| DataForSEO Keyword Data API | Search volume, CPC, competition | Monthly, following Google/Bing Ads update cycles | Google usually mid-month; Bing previous month usually within 72 hours | Past 12 months from source data | citeturn33view6turn33view7turn33view8 | Estimate data, not live demand |
| DataForSEO Labs API | Keyword metrics + SERP-derived data | Keyword metrics monthly; SERPs on ~30/60/90 day cycles depending on query/location | Depends on source cycle | Location-specific latest-update tables available | citeturn31view4 | Freshness varies materially by query and market |
| DataForSEO Backlinks API | Backlink index | Continuously updated “live index” | Real-time availability as records update | Unclear — needs confirmation | citeturn31view5 | “Live” still depends on crawling and record updates |
| Ahrefs | Backlinks / DR / UR inputs | Every 15–30 minutes | Near-real-time once Ahrefs has crawled it | 10+ years of historical data advertised | citeturn31view7turn5search19 | Crawl priority varies by page/site importance |
| Ahrefs | Keyword / SERP database | Multiple times a day to once in 1–2 months depending on keyword popularity | Inherits refresh interval | Depends on report/plan | citeturn31view2turn33view1 | Low-volume keywords age much faster |
| Ahrefs | Rank Tracker | Weekly by default | Inherits tracker schedule | From campaign start | citeturn6search1turn6search18 | Tracked ranks are not “live SERP now” |
| Ahrefs | Custom AI prompt tracking | Daily, weekly, or monthly | Inherits selected schedule | As tracked | citeturn32view6 | Product-defined cadence, not ground truth |
| Semrush | Keyword database / organic positions | Ongoing; once a day to once a month depending on keyword popularity | Inherits keyword refresh | Varies by database; search-volume history to Jan 2012 | citeturn32view0turn32view2 | Low-popularity keywords update less often |
| Semrush | Search volume | Monthly | Monthly | History to Jan 2012 | citeturn32view2 | Average monthly estimate |
| Semrush | Authority Score | Every two weeks | N/A | Trend widget across year | citeturn32view1turn7search22 | Proprietary compound score |
| Semrush | Backlinks | New links usually within an hour; interface every 15 minutes | ~40 minutes average for recent links | Fresh index = last 6 months | citeturn31view6 | Crawl/index scope still provider-specific |
| Semrush | Position Tracking | Daily within 24–48 hours | 24–48 hours | Daily for 60 days, then weekly for 140 weeks | citeturn31view3turn32view3 | Great for campaign history, not an instant SERP capture |
| Semrush | AI Visibility Toolkit | Daily rolling basis | Inherits platform/report pipeline | Unclear — needs confirmation | citeturn32view4turn32view5 | Product score layer, not raw engine ground truth |
| YouTube Data API | Public resources and statistics | Unclear official cadence in reviewed docs | Unclear — needs confirmation | N/A for public resource fetches | citeturn8search18turn8search21turn8search5 | Public counts can change and counting rules can change |
| YouTube Analytics API | Query metrics | “Real-time” targeted queries, but viewability can lag by days | A few days; earnings about 2 days | Unclear for active query history in reviewed docs | citeturn34view7turn33view12turn33view13 | Official first-party but not same-day final across all metrics |
| YouTube Reporting API | Bulk reports | Reports generated per job; historical reports posted within a couple days | Historical reports usually arrive within a couple days | Non-historical files 60 days; historical files 30 days | citeturn33view9turn33view10 | File availability window is short |
| ChatGPT Search | Web-grounded answers with links | On-demand | Depends on web search at query time | Conversation-dependent | citeturn31view8turn34view2 | No official reproducibility guarantee |
| Perplexity Search / Sonar | Real-time search / cited answers | On-demand from continuously refreshed index | Depends on search state | Results can include `date` and `last_updated` | citeturn31view9turn34view0turn34view1 | Great metadata; still prompt/time-bound |
| Copilot Search / Copilot web mode | Bing-index grounded responses | On-demand | Depends on Bing search state | Conversation-dependent | citeturn31view10turn34view3 | Cited, but still generative and current-web dependent |
| Gemini | Response sources / related links | On-demand | Unclear — needs confirmation | Conversation-dependent | citeturn31view11turn15search11 | Sources may appear on some responses, not all |
| Etsy Stats | Shop stats | Ongoing; hourly recent stats visible | Unclear precise lag | November 2017 to present | citeturn31view13turn35view6 | Recent hourly views use local time zone; others UTC |
| Fiverr Analytics | Sales analytics | Real-time view | Minimal / real-time | Unclear — needs confirmation | citeturn32view11 | Marketplace-specific metrics remain platform-bound |
| Shopify Analytics | Dashboard and many reports | About 1 minute for many analytics/reports | Some views can lag 12 hours or 24 hours; Live View can lag 1–2 hours under load | Any date range supported in reports; some app/tool views show last 30 days | citeturn32view10turn31view12turn29search2turn29search10turn35view8turn35view9 | Report family matters; not all reports are equally current |
| Pinterest Trends | Keyword trend views | Unclear explicit cadence; shows weekly/monthly/yearly changes | Unclear — needs confirmation | Graph-based trend history in product | citeturn32view12 | Trend tool is directional, not a search-volume ledger |
| Pinterest Analytics | Account / pin analytics | Unclear explicit cadence | Unclear — needs confirmation | Unclear — needs confirmation | citeturn35view7turn32view13 | Pins can resurface long after publication |

### SERP Freshness and Volatility

**Required warning:** SERP observations are context-bound and time-bound; older snapshots remain useful for history, but current claims require current captures. Google explicitly says results differ by location, language, and device. Semrush’s volatility tooling exists because rankings fluctuate day to day, and Semrush also notes that search results can change many times over a day due to new content and crawling schedules. citeturn21search2turn21search14turn21search20turn21search7turn22search11

Normal organic SERPs are not equally volatile. News-driven and event-driven queries churn faster than evergreen queries. Local results are more volatile than broad national results because location is not a nuisance variable there; it is part of the query meaning. Device, language, login state, and return-to-SERP behavior can all change what appears to be “the SERP.” That means The Observatory should treat “SERP snapshot” as a context object, not just ten blue links plus vibes. citeturn21search2turn21search14turn21search20

Rank trackers soften this chaos by imposing a cadence. Ahrefs Rank Tracker is weekly by default. Semrush Position Tracking is generally daily within 24–48 hours and preserves daily points for 60 days, then weekly points. Those tools are useful for trend and campaign monitoring, but their numbers are still **provider-captured observations on a schedule**, not live universal truth. citeturn6search1turn31view3turn32view3

| SERP Evidence | Volatility | Likely Freshness Use | Customer-Facing Caveat |
|---|---|---|---|
| Generic organic SERP snapshot | High | Same-day to a few days for current-state discussion; longer for historical review | “Captured on [time/context]; may differ by device, location, language, and later recrawl.” citeturn21search2turn21search7 |
| Rank position | High | Very recent for present-tense rank claims | “Tracker/snapshot position is time-bound and may differ from live results.” citeturn22search11turn31view3 |
| SERP feature presence | High | Recent only for present-tense feature claims | “Feature appearance varies by query intent and current SERP composition.” citeturn21search7 |
| Local pack / map pack | Very high | Same-day preferred; very short for comparison | “Local results depend heavily on location and search context.” citeturn21search2turn22search18 |
| News/trending query snapshot | Very high | Same-day only for current-state claim | “Trend-sensitive results can change within hours.” Inference from provider volatility tooling and search-context behavior. citeturn21search7turn22search11 |
| Evergreen query snapshot | Medium to high | Can stay useful longer for directional trend and page-presence history | “Older snapshot still useful historically, not proof of current ranking.” citeturn35view0turn35view5 |
| Google video-result observation | High | Recent-only for current-state claim | “Video blocks and ranking order are context-bound like any SERP feature.” citeturn21search2 |

### AI / GEO Freshness and Volatility

Official platform docs agree on one thing and dodge the rest. They agree that these products are **web-grounded** and often **source-linked**. Google says AI Overviews provide an AI-generated snapshot with links and may contain mistakes. AI Mode uses query fan-out and may provide web links when confidence is insufficient. ChatGPT Search says it gives fast, timely answers with links to relevant web sources. Perplexity documents real-time search against a continuously refreshed index, and even exposes `date` and `last_updated` in result objects. Copilot Search says it cites sources prominently. Gemini says it may show sources and related links. citeturn34view5turn34view4turn31view8turn31view9turn34view0turn31view10turn31view11

What the official docs do **not** give you is a stable reproducibility promise. Third-party and academic evidence says not to assume one. The 2026 arXiv study found average day-to-day cited-source overlap of roughly **0.34 to 0.42**, implying that a large share of cited sources changed from one day to the next across the observed prompts and engines; the same study concluded that true GEO visibility should be aggregated over multiple runs rather than read from a single observation. Ahrefs reported that AI Overviews in its sample changed every **2.15 days on average** and that **45.5%** of citations changed when AI Overviews updated. BrightEdge, using a different methodology and aggregation level, found that **96.8% of cited domains** showed zero week-over-week change, but when changes did happen they were usually binary drops rather than gradual drift. citeturn25view0turn36view1turn36view0

That disagreement is not a research failure. It is a scope warning. **Inference:** AI answers can be stable at the aggregate domain level while still being unstable at the prompt/run level. Therefore, The Observatory should treat AI citation observations as **prompt/context/time-bound observations**, not durable facts about intrinsic brand visibility. A single capture without prompt text, timestamp, engine, mode, location, account state, result links, and if possible model/version is too weak for customer-facing present-tense claims. citeturn25view0turn32view8turn34view4

**Required warning:** AI/GEO observations are prompt/context/time-bound and may not reproduce exactly. Old AI observations still matter for trend and change detection, especially if collected consistently across the same prompt set and context envelope. But for customer-facing claims like “you are cited in ChatGPT” or “Google AI Overview cites you for this intent,” the safe current-use window should be short unless the claim is explicitly historical. If the prompt or capture context is missing, the evidence should be treated as stale-for-claim immediately. citeturn25view0turn36view1turn36view0turn31view8turn31view9

### Keyword and Provider Estimate Freshness

**Required principle:** Keyword volume and difficulty metrics are provider estimates with update cadences, not exact current demand facts. Semrush states that search volumes are updated monthly and are average monthly values, with history back to January 2012. DataForSEO says it updates keyword metrics such as search volume, CPC, and competition monthly following Google Ads and Bing Ads cycles. Ahrefs says data refresh depends on keyword popularity, from multiple times a day to every one to two months, and that organic traffic is an estimated monthly figure based on the past 30 days with uneven SERP refresh by keyword popularity. citeturn32view2turn31view4turn33view6turn31view2turn33view1

Old keyword estimates can still support **relative prioritization, historical demand comparisons, seasonality interpretation, portfolio triage, and trend analysis**, especially when the provider has stable historical series. They become weak support for customer-facing claims like “current demand is X right now” or “this keyword is definitely worth Y today,” because the number is usually an average, often lagged, and sometimes computed from the prior 12 months or prior month’s ad-source refresh. citeturn32view2turn33view7turn7search13

Difficulty, competition, and CPC estimates should inherit provider-specific caveats. Ahrefs allows manual SERP updates that can change KD and related metrics. Semrush Keyword Magic metrics are monthly, and local volume consumes specific update allowances. DataForSEO explicitly ties freshness to the upstream ad platforms. The correct stance for The Observatory is therefore: **capture the metric, provider, source family, and as-of date; never strip out the estimate-ness.** citeturn33view2turn33view4turn33view5turn33view6

### Backlink and Authority Metric Freshness

Backlink and authority evidence changes fast but not cleanly. Ahrefs updates its live backlink index every **15–30 minutes**. Semrush says new backlinks are added to its database within **an hour** of publication on average, with interface refresh every **15 minutes**, and its fresh index reflects the last **6 months** of crawling. DataForSEO describes its backlinks database as a continuously updated **live backlink index**. Those are fast cadences, but they are still bounded by crawling, processing, and per-page priority. Ahrefs explicitly notes that crawl speed depends on URL/Domain rating and site “popularity.” citeturn31view7turn31view6turn31view5turn5search20

Why do providers disagree? Because they crawl different parts of the web, at different times, with different deduplication and recrawl rules, and compute different summary metrics on top. A link can exist on the web and still be absent from one provider’s current view because that crawler has not yet rechecked the page, cannot access it, has dropped the page, or prioritizes it differently. Semrush’s Authority Score updates every two weeks; Ahrefs DR/UR are driven by its fast link index; DataForSEO markets live link availability. That alone guarantees some disagreement even before method differences show up. citeturn31view7turn32view1turn31view5turn5search11

Current-state claims such as “the site has X backlinks” or “this domain currently has authority score Y” should therefore be phrased as **provider-observed counts/metrics as of capture time**. Backlink evidence becomes too stale for current claims faster than most people admit, but it stays useful for trend, campaign-impact direction, and provider-relative benchmarking. In other words: the count is slippery, the direction is often more useful, and pretending otherwise is how dashboards end up lying in a tie. citeturn31view6turn31view7turn31view5

### First-Party Performance Freshness

Search Console is strong evidence and still not instant truth. Google says collected performance data is usually available in **2–3 days**, and the last **2 days** may be preliminary. The Search Performance report exposes clicks, impressions, CTR, and average position, and Search Console gives **16 months** of report data. That makes GSC excellent for historical performance interpretation and period comparison, but weak for same-day certainty unless explicitly using hourly/partial states and saying so. citeturn31view0turn35view1turn35view0turn31view1

Bing Webmaster Tools also provides up to **16 months** of Search Performance history, but the reviewed official sources were less explicit about standard reporting delay. That is exactly the kind of gap The Observatory should preserve as a caveat. AI Performance in Bing Webmaster Tools is even more caveated: it is in preview, uses aggregated signals, and says grounding queries are a **sample** of overall citation activity, not a full rank list or deterministic source ledger. citeturn35view5turn32view8turn32view9

YouTube first-party data is fresher than many SEO tools but still delayed. YouTube says there can be **a delay of a few days** before data is viewable in YouTube Analytics; estimated earnings are updated daily but have an **approximately 2-day** delay; Reporting API files expire quickly; and developer policies require 30-day refresh/delete behavior for many stored statistics. Also, Shorts view-count methodology changed in 2025, which means historical comparisons across that boundary need explicit caution. citeturn33view12turn33view13turn33view9turn33view11turn9search12

Etsy, Fiverr, Pinterest, and Shopify show the same pattern in different outfits. Etsy stats go back to November 2017 and show hourly recent views; Fiverr describes sales analytics as real-time; Shopify updates many analytics views within about one minute but warns that some reports can be delayed by 12–24 hours or longer under load; Pinterest analytics shows overall organic and paid content performance, but the reviewed docs did not provide a clean latency rule. citeturn31view13turn35view6turn32view11turn32view10turn29search2turn29search10turn35view9turn35view7

**Boundary reminder:** customer first-party/private analytics do not belong in Observatory by default. Even when first-party data is the strongest evidence, its use is still bounded by retention, privacy, authorization, and surface-specific caveats. Before customer-facing use, refresh if the claim is current-state and the underlying provider has known delay or provisional states. That means GSC, YouTube Analytics, AI Performance preview surfaces, and some Shopify/Fiverr/Etsy views should all carry age and freshness warnings. citeturn31view0turn33view12turn32view8turn32view10

### Marketplace and Video Freshness

Marketplace and video evidence splits into two different species: **listing/page state** and **search/discovery state**. Listing/page snapshots age more slowly because they are archival evidence of what the page or gig said at capture time. Search/discovery observations age faster because search order, recommendation surfaces, and shopper context shift continuously. Etsy listing URLs are now stable after first publish, which is good for longitudinal identity, but listing content and search visibility can still change. Fiverr gigs can move between active, paused, pending, and modified states, and platform analytics track impressions, clicks, and orders in real time. citeturn16search20turn16search1turn35view10turn32view11

Pinterest is the best reminder that “old” is not the same as “finished.” Pinterest says there is **no set engagement window** for Pins, and that Pins can gain engagement hours, days, months, or years after publication; seasonal topics can resurface. That means a Pinterest snapshot can retain trend value for a long time. The flip side is that a recent search/trend observation can be highly seasonal and not representative of steady-state demand. Pinterest Trends exposes weekly, monthly, and yearly change views, which is useful but also a clue that the right grain for interpretation is often comparative rather than absolute. citeturn32view13turn32view12

For YouTube, public metadata, public counters, analytics, search results, and Google video results should not be treated as one evidence class. Metadata snapshots are medium-volatility archival evidence. Public counters are high-volatility. Analytics is first-party but delayed. Search-result observations on YouTube or Google age quickly because they are discovery-surface captures, not durable state records. Current official docs reviewed here do not state a single public-search cadence for YouTube search results or Google’s video blocks, so those should default to **high-volatility with unknown cadence caveat**. citeturn8search5turn33view13turn21search2

### Rights / Terms / Pricing Evidence Freshness

**Required principle:** Rights, pricing, and terms evidence must be treated as time-sensitive and re-verified before provider admission, paid pulls, automation, or customer-facing use. This is not paranoia. It is how provider docs behave in the real world. DataForSEO announced pricing changes effective **July 1, 2026** across multiple APIs. YouTube’s API Terms expressly allow modification of the agreement, with some changes effective as soon as notice is given for legal or new-functionality reasons. YouTube’s service terms also say related policy documents may be updated from time to time. Ahrefs and other vendors publish current pricing pages that can change outside your evidence capture. citeturn37view0turn37view1turn37view2turn37view3turn37view4

That means terms/pricing evidence lives in two separate safety classes at once. As **historical evidence**, it is durable: it can prove what the provider said on date Z. As **action evidence**, it expires fast: current permissions, costs, and storage rights must be re-checked before relying on them. In Observatory terms, this is the classic case where evidence can be perfectly valid and still unsafe for current action. Bureaucracy is undefeated. citeturn37view0turn37view1turn37view2

## Candidate Contracts and Controls

### Proposed Freshness Classes

These are candidate contract inputs, not doctrine.

| Class | Definition | Example evidence types | Safe use | Unsafe use | Required warning |
|---|---|---|---|---|---|
| F0 current | Captured same day and still inside the shortest reasonable current-use window for the surface | Same-day SERP capture, same-day AI answer capture with full prompt/context, same-day local pack, same-day price/terms recheck | Present-tense observation with context | Broad truth claims without caveats | “Current as observed at capture time; surface may still vary by context.” |
| F1 recent | Recent enough for cautious current-use, depending on volatility class | Recent rank-tracker pull, recent GSC hourly/partial, recent marketplace search capture | Current-state directional use with caveat | “Guaranteed current” language | “Recent, but not live; verify before strong current-state claims.” |
| F2 aging but usable with caveat | No longer ideal for current-state claims on volatile surfaces, but still usable directionally or comparatively | Two-week-old keyword estimate, month-old domain metric, week-old analytics export | Trend, prioritization, historical comparison | Hard present-tense customer claims | “Evidence age may reduce current-state reliability.” |
| F3 historical trend only | Best used for history, precedent, deltas, and change detection | Old SERP snapshot, old AI citation capture, old listing snapshot, year-old analytics series | Trend, historical evidence, audit | Claims about current market state | “Historical evidence only; not proof of current state.” |
| F4 stale for current claims | Too old or too context-poor for safe current-state use | Old AI capture without prompt/context, old rank snapshot, old pricing page | Maybe internal archival reference | Current-rank, current-citation, current-rights, current-price claims | “Stale for current claims.” |
| F5 expired / re-check required | Action-sensitive evidence requiring immediate re-verification before use | Terms, pricing, rights, API limits, storage rules | Historical audit only until rechecked | Any action or customer-facing advisory without recheck | “Re-check required before use.” |

### Proposed Evidence Half-Life Table

The table below is deliberately ranged and caveated. It is a candidate input, not fake precision masquerading as science.

| Evidence Type | Volatility | Current-Use Window | Trend-Use Window | Refresh Before Customer Use? | Required Caveat | Confidence |
|---|---|---:|---:|---:|---|---|
| SERP snapshot | Very high | Hours to 3 days | Months+ for history | Yes | Context-bound by location/device/language/time | Medium |
| Rank position | High | Same day to ~3 days | Weeks to months | Yes | Tracker/snapshot position is time-bound | High citeturn31view3turn6search1 |
| Local/map pack result | Very high | Same day | Weeks for history only | Yes | Hyper-local and highly context-bound | Medium |
| SERP feature presence | High | Same day to ~3 days | Weeks to months | Yes | Feature presence can come and go with query context | Medium |
| Google AI Overview / AI Mode capture | Very high | Same day to ~48 hours | Weeks to months for trend | Yes | Prompt/context/time-bound; may not reproduce | Medium citeturn34view4turn34view5turn25view0 |
| ChatGPT / Perplexity / Copilot / Gemini citation capture | Very high | Same day to ~48 hours | Weeks to months for trend | Yes | Prompt/context/time-bound; may not reproduce | Medium |
| Third-party AI visibility score | Medium to high | 1–7 days if product refreshes daily; otherwise provider cadence-bound | Months for trend | Usually | Provider score, not ground truth | Medium |
| Keyword volume estimate | Medium | ~2–6 weeks | Years if same provider series | Sometimes | Estimate with monthly/provider cadence | High |
| Keyword difficulty / competition score | Medium | ~2–6 weeks unless freshly refreshed | Months to years | Sometimes | Estimate derived from SERPs/ad data | Medium |
| CPC / paid competition estimate | Medium | ~2–6 weeks | Months to years | Sometimes | Ad-market estimate, not live auction truth | Medium |
| Backlink count / referring domains | High | 1–14 days depending on provider and use | Months for trend | Usually | Provider-observed count as of capture time | High |
| Ahrefs/Semrush/DataForSEO authority/domain metrics | Medium | ~2–4 weeks | Months to years | Sometimes | Proprietary metric, provider-relative | High |
| Estimated organic traffic | Medium | ~2–4 weeks | Months to years | Sometimes | Estimated monthly traffic, not first-party truth | High |
| GSC metrics | Medium | Refresh before present-tense claims if age exceeds provider lag window | 16 months in-interface | Often | Last days may be preliminary | High |
| Bing Webmaster metrics | Medium | Refresh for present-tense claims | 16 months | Often | Exact delay unclear in reviewed docs | Medium |
| YouTube Analytics | Medium | Refresh before current-performance claims if not within last settled days | Strong for historical performance | Often | Delay of a few days; some metrics differ more | High |
| YouTube public statistics | High | 1–7 days | Months for trend if methodology stable | Usually | Public counts and counting rules can change | Medium |
| YouTube search-result observation | Very high | Same day to ~3 days | Weeks to months for history | Yes | Search surface cadence unclear | Low |
| Etsy listing snapshot | Medium | ~1–4 weeks for descriptive state, shorter if claim is “currently listed this way” | Months+ for archive | Often | Listing content may have changed since capture | Medium |
| Etsy/Fiverr/marketplace search result | High | Same day to ~7 days | Weeks to months for history | Yes | Search/discovery context changes quickly | Medium |
| Shopify public page snapshot | Medium | ~1–4 weeks for descriptive state | Months+ for archive | Often | Merchant may have edited page | Medium |
| Pinterest trend/search observation | High | ~1–14 days depending on seasonality | Months to years for seasonality analysis | Usually | Seasonal and trend-sensitive | Medium |
| Public HTML snapshot / screenshot | Archival / durable | Not for “current state” unless very recent | Long-term archival | If used for current claims | Proves observed state at capture time only | High |
| Provider pricing / terms / rights docs | Low for history, F5 for action | Same day recheck for action use | Long-term for audit history | Yes, always | Re-verify before action/customer use | High |

### Same Target / Same Time Comparison Rules

**Required rule:** Provider comparisons should record capture-time distance and warn when comparisons are stale or non-synchronous. This matters most when providers crawl at different rates or when surfaces are inherently volatile. Ahrefs, Semrush, and DataForSEO all run materially different refresh patterns; GSC and YouTube both have reporting delays; AI surfaces can vary by rerun or day. Comparing capture A from Monday with capture B from three weeks ago and pretending they are peers is not analysis. It is cosplay. citeturn31view2turn31view3turn31view4turn31view0turn33view13turn25view0

Candidate comparison rules:

| Comparison Type | Preferred max capture-time distance | Warning threshold | Unsafe threshold | Why |
|---|---:|---:|---:|---|
| AI answer vs AI answer | Same session or same day | >24 hours | >72 hours for current-state comparison | Prompt/run/day effects are large |
| Live SERP vs live SERP | Same hour or same day | >24 hours | >72 hours for current-rank comparison | SERP context drifts quickly |
| Local/map pack vs local/map pack | Same hour | >12 hours | >24 hours | Local context is extra fragile |
| Marketplace search vs marketplace search | Same day | >24 hours | >72 hours | Discovery order changes quickly |
| Rank tracker vs rank tracker | Same scheduled update cycle | >3 days | >7 days | Tracker cadence defines comparability |
| Backlink provider vs backlink provider | Same week | >7 days | >14 days | Crawl/index timing differs materially |
| Keyword estimate provider vs provider | Same monthly cycle | Cross-month comparison without note | Multiple-cycle gap without note | These are cadence-bound estimates |
| First-party analytics vs third-party estimate | Same settled reporting period | Mismatched date windows | Different periods with no note | Different latency, scope, and definitions |
| Terms/pricing doc vs anything action-related | Same day recheck | >7 days | Any stale action use | Rights/pricing can change suddenly |

**Inference:** The Observatory should store a computed **capture-time distance** for any comparison pair and classify it into at least: synchronous, near-synchronous, non-synchronous, and unsafe-for-current-comparison. For high-volatility surfaces, “near-synchronous” should still emit a warning. For low-volatility archival evidence, longer gaps are acceptable if the use is explicitly historical. citeturn25view0turn31view0turn31view4

### Typed Read Tool Warning Requirements

These warnings are candidates for future typed reads. They are wording recommendations, not implementation work.

| Warning Type | Trigger Condition | Warning Text | Affected Evidence Types |
|---|---|---|---|
| evidence_age_warning | Evidence age exceeds soft threshold for its volatility class | “This observation may still be useful historically, but its reliability for current-state use decreases with age.” | Most evidence types |
| stale_for_current_claim_warning | Evidence exceeds current-use window for that type | “This evidence is stale for present-tense claims. Treat as historical or refresh before asserting current state.” | SERP, AI, search/discovery, pricing/terms |
| provider_update_unknown_warning | Official cadence or delay not confirmed | “Provider update cadence is unclear from reviewed documentation. Do not assume this is current without an explicit caveat.” | Bing performance delay, YouTube public stats, Pinterest analytics, some marketplace tools |
| non_synchronous_comparison_warning | Comparison capture-time distance exceeds comparison threshold | “These observations were captured far enough apart in time that direct comparison may be misleading.” | Cross-provider comparisons |
| high_volatility_surface_warning | Evidence type is classified high or very high volatility | “This surface changes quickly and may not reproduce across time, location, device, prompt, or account context.” | SERP, AI answers, marketplace search, YouTube search |
| rights_recheck_required_warning | Rights/terms/pricing docs older than allowed recheck window | “Provider terms, rights, or pricing must be re-verified before action or customer-facing use.” | Terms, pricing, usage rights |
| customer_private_overlay_warning | Read combines public observations with customer-private metrics | “This output includes customer-private analytics. Do not treat it as default Observatory evidence.” | GSC/Bing/YT/Shopify/Etsy/Pinterest private reports |
| AI_reproducibility_warning | AI capture lacks sufficient prompt/context metadata or is old | “AI response/citation observations are prompt/context/time-bound and may not reproduce exactly.” | AI visibility captures |
| preliminary_data_warning | Provider says data may be preliminary | “Provider indicates this period may include preliminary data.” | GSC recent days, some analytics windows |
| estimate_not_fact_warning | Metric is provider-estimated, not first-party actuals | “This is a provider estimate with its own update cadence, not an exact real-time fact.” | Keyword volume, traffic estimates, authority scores |

### Hammer Test Inputs

These are candidate hammer tests, not implementations.

| Candidate Hammer | Expected behavior |
|---|---|
| Reject current-rank claims from stale SERP snapshots | A read that says “currently ranks #3” from an old snapshot should fail or hard-warn |
| Warn on non-synchronous provider comparisons | A comparison of two providers captured weeks apart should emit explicit timing warnings |
| Reject customer-facing rights/pricing claims from stale docs | Pricing/terms captures older than the recheck window should fail for action use |
| Reject AI citation claims without prompt/context/timestamp | Missing prompt, engine, or capture time should block or heavily warn |
| Warn when provider update cadence is unknown | Unknown cadence should never be silently treated as live/current |
| Warn when recent provider data may be preliminary | GSC/analytics recent-period reads should surface preliminary-data status |
| Reject freshness-blind summaries | Any synthesized output that omits evidence age on volatile surfaces should fail |
| Warn when estimate metrics are described as facts | “Demand is X” from keyword estimates should fail unless caveated as estimate |
| Reject direct comparison across mismatched date windows | First-party analytics vs third-party estimates on different windows should fail comparison safety |
| Warn when historical evidence is used for current action | Terms, API limits, pricing, and rights should force recheck workflows |

### Recommended Observatory Handling

What belongs in the **Freshness / Volatility Contract** is the classification logic: evidence type, volatility class, provider cadence, reporting delay, current-use window, trend-use window, and comparison-time thresholds. It should also define required metadata such as capture timestamp, provider/source, surface, and context envelope. The contract should say what the evidence *is fit for*, not what it *means*. citeturn31view0turn31view2turn31view4turn32view8

What belongs in the **Claim-Safety Contract** is the conversion of freshness state into claim permissions: what can support a current-state claim, what is only safe for historical/trend use, what requires provider-cadence caveats, what requires recheck-before-use, and what is blocked without prompt/context metadata. AI reproducibility, preliminary-data warnings, estimate-not-fact warnings, and stale-for-current-claim logic belong here. citeturn34view5turn34view4turn36view1turn36view0

What belongs in the **Provider Cross-Check Contract** is timing discipline: same-target/same-time rules, capture-time distance measurement, and provider-relative caveats. It should explicitly distinguish “different providers disagree because they update differently” from “one provider is wrong.” Backlink, keyword estimate, and AI visibility data all need this. citeturn31view7turn31view6turn31view5turn32view0turn32view1

What belongs in the **Query Panel Contract** is the definition of the context envelope required to interpret volatile evidence safely: search engine, device, locale, language, location, login/account state where relevant, prompt text, model or mode, and capture timestamp. If the panel cannot express the context, the read tool should not pretend the evidence is generic. citeturn21search2turn34view4turn31view10turn31view11

What belongs in the **Capture Package Contract** is a minimum evidentiary bundle: raw observation, capture time, source/provider, surface, relevant context, and any provider freshness tags or update indicators available from the source. For Perplexity, that can include `date` and `last_updated`; for Semrush Position Tracking, “Last Update”; for GSC, whether the queried period includes preliminary days. citeturn34view0turn31view3turn31view0

What belongs in **typed read-tool warnings** is not business advice. It is surface safety: age warnings, cadence-unknown warnings, non-synchronous comparison warnings, AI reproducibility warnings, estimate warnings, and rights recheck warnings. What should become **hammer tests** is anything that would let a volatile, delayed, or context-poor observation sneak into customer-facing language as if it were current truth. What should remain **owner/consumer-owned** are the threshold choices that are ultimately policy decisions: how conservative to be for customer outputs, what counts as “too old” in a given business context, and what to do when the freshest lawful evidence is still imperfect. What needs more research is listed below. citeturn37view1turn37view2turn32view9turn33view11

## Open Questions and Decision Inputs

### Questions / Unknowns To Confirm

| Question | Current status |
|---|---|
| Exact standard reporting delay for Bing Search Performance | Unclear — needs confirmation. |
| Exact public-latency behavior for YouTube Data API statistics | Unclear — needs confirmation. |
| Exact freshness/retention rules for Pinterest Analytics | Unclear — needs confirmation. |
| Exact retention/history window for Bing AI Performance and compare views | Unclear — needs confirmation. |
| Exact official cadence for public YouTube search results and Google video blocks | Unclear — needs confirmation. |
| Exact cadence/exposed timestamps for every DataForSEO endpoint family beyond reviewed help docs | Unclear — needs confirmation. |
| Freshness/retention details for official third-party GEO tools beyond Ahrefs/Semrush/Bing | Unclear — needs confirmation. |
| Marketplace-tool estimate cadences for Etsy/Fiverr/Shopify-focused external tools | Unclear — needs confirmation. |

### Decision Inputs For M1 / M7 / M8 Roadmap

This report is already suitable as input for a **Freshness / Volatility Contract**, a **Claim-Safety Contract**, a **Provider Cross-Check Contract**, a **Query Panel Contract**, a **Capture Package Contract**, typed **read-tool warnings**, and a **hammer matrix**—with one limitation: the unresolved provider-cadence gaps above should be preserved as explicit unknowns rather than smoothed over. The correct next move is not to invent certainty. The correct next move is to formalize where certainty ends. citeturn31view0turn32view8turn25view0

Recommended status:  
- suitable as Freshness / Volatility Contract input  
- suitable as Claim-Safety Contract input  
- suitable as Provider Cross-Check input  
- suitable as Hammer Matrix input  
- needs owner ruling  
- needs more research

**Must know before M7 contracts:** the final volatility classes, what minimum context envelope is mandatory per volatile surface, and which evidence classes are automatically stale-for-current-claim without refresh.  
**Must know before M8 hammers:** exact blocking vs warning behavior for stale evidence, missing-cadence evidence, and non-synchronous comparisons.  
**Must know before provider admission:** pricing/terms recheck rules, storage/refresh restrictions, and whether the provider exposes enough freshness metadata to support safe reads.  
**Must know before typed read tools:** which warnings are mandatory, which are soft, and which missing fields make the read unsafe.  
**Must know before customer-facing reports:** what current-use windows to enforce by volatility class, and how to phrase estimate and preview caveats.  
**Must know before recurring capture decisions:** nothing about cadence should be automated into doctrine until owner rulings establish the risk tolerance for each evidence class and each target output. If you automate too early, congratulations, you have built a stale-data sprinkler system. citeturn37view0turn37view1turn33view11turn32view9

## Appendices

### Appendix — Provider Update Cadence Table

This appendix expands the main cadence table into the most decision-relevant source/provider pairings.

| Provider / Source | Data Type | Update Cadence | Reporting Delay | Historical Window | Source | Caveat |
|---|---|---:|---:|---:|---|---|
| Google Search Console | Search performance | Published in intervals | Usually 2–3 days; last 2 days preliminary | 16 months | citeturn31view0turn35view0 | Strong history, not same-day finality |
| Google Search Console API | Hourly reporting | Hourly breakdown available | Hourly data may be partial | Up to 10 days hourly | citeturn31view1 | Requires partial-state caveat |
| Bing Webmaster Tools | Search Performance | Unclear official standard cadence in reviewed docs | Unclear — needs confirmation | 16 months | citeturn35view5 | Preserve unknown, do not assume daily |
| Bing Webmaster Tools | Crawl stats API | Updated every day | Daily | Unclear | citeturn35view4 | Crawl stats cadence does not prove performance cadence |
| Bing Webmaster Tools | AI Performance preview | Preview, evolving aggregated signal set | Unclear | Unclear | citeturn32view8turn32view9 | Sample query data; not deterministic rank evidence |
| DataForSEO Keyword Data API | Search volume / CPC / competition | Monthly on Ads cycle | Google mid-month; Bing previous month often within 72 hours | 12-month upstream source frame | citeturn33view6turn33view7turn33view8 | Estimate-only |
| DataForSEO Labs API | Keyword and SERP-derived data | Monthly metrics; SERP windows ~30/60/90 days | Inherits source refresh | Location tables available | citeturn31view4 | Query/location-specific freshness |
| DataForSEO Backlinks | Live index | Continuous | Real-time as records update | Unclear | citeturn31view5 | Crawl and recrawl still matter |
| Ahrefs | Backlinks | Every 15–30 minutes | Near-real-time after crawl | 10+ years advertised | citeturn31view7turn5search19 | Fast index, uneven crawl priority |
| Ahrefs | Keywords Explorer / Site Explorer SERPs | Multiple times a day to once in 1–2 months | Keyword dependent | Varies | citeturn31view2turn33view1 | Long tail can be materially older |
| Ahrefs | DR/UR | Inherit backlink-index updates | Near-real-time after crawl | Varies | citeturn31view7turn5search2 | Provider-relative metric |
| Ahrefs | Rank Tracker | Weekly default | Scheduled | Campaign-start history | citeturn6search1turn6search18 | Weekly trend tool, not live snapshot |
| Ahrefs | Brand Radar custom prompts | Daily/weekly/monthly selectable | Scheduled | As tracked | citeturn32view6 | Product-defined monitoring schedule |
| Semrush | Keywords/global DB | Once a day to once a month | Inherits database refresh | Search-volume history to 2012 | citeturn32view0turn32view2 | Popularity-dependent |
| Semrush | Search Volume | Monthly | Monthly | Jan 2012 onward | citeturn32view2 | Average monthly estimate |
| Semrush | Authority Score | Every two weeks | N/A | Trend by year | citeturn32view1 | Proprietary quality metric |
| Semrush | Backlinks | Within an hour on average; interface every 15 min | ~40 minutes average | Fresh index last 6 months | citeturn31view6 | Strong freshness, still provider-relative |
| Semrush | Position Tracking | Daily within 24–48 hours | 24–48 hours | Daily 60d, weekly 140w | citeturn31view3turn32view3 | Good trend history, not universal now-state |
| Semrush | AI Visibility | Daily rolling refresh | Product-defined | Unclear | citeturn32view4turn32view5 | Score/report layer |
| YouTube Analytics | Channel/content-owner metrics | Targeted queries | Delay of a few days; earnings ~2 days | Active-history retention unclear in docs reviewed | citeturn34view7turn33view12turn33view13 | First-party but delayed |
| YouTube Reporting API | Bulk report jobs | Generated per job | Historical reports usually within a couple days | 30-day historical files; 60-day non-historical files | citeturn33view9turn33view10 | Short file-expiry windows |
| YouTube Data API | Public statistics/resources | On-demand fetch | Unclear official latency | N/A | citeturn8search21turn8search5 | Methodology changes affect comparability |
| Etsy Stats | Shop stats | Ongoing; hourly recent views | Unclear | Nov 2017 to present | citeturn31view13turn35view6 | Recent hourly is local-time-zone scoped |
| Fiverr Analytics | Seller analytics | Real-time | Minimal | Unclear | citeturn32view11 | Platform-private, marketplace-specific |
| Shopify Analytics | Dashboard and many reports | About 1 minute | Some views can lag 12–24h; Live View 1–2h under load | Flexible date ranges; some views last 30 days | citeturn32view10turn31view12turn35view8turn35view9 | Report family matters |
| Pinterest Trends | Trend keywords | Unclear explicit cadence | Unclear | Product graph/history | citeturn32view12 | Comparative directional tool |
| Pinterest Analytics | Account/pin analytics | Unclear | Unclear | Unclear | citeturn35view7turn32view13 | Needs confirmation |

### Appendix — Evidence Half-Life Table

| Evidence Type | Volatility | Suggested current-use window | Suggested trend-use window | Refresh before customer use | Caveat | Confidence |
|---|---|---:|---:|---:|---|---|
| SERP snapshot | Very high | Hours to 3 days | Long for history | Yes | Context-bound | Medium |
| Rank position | High | Same day to 3 days | Weeks to months | Yes | Position can drift quickly | High |
| Local/map pack | Very high | Same day | Weeks for history only | Yes | Locality-sensitive | Medium |
| SERP feature presence | High | Same day to 3 days | Weeks to months | Yes | Feature churn | Medium |
| AI answer / citation capture | Very high | Same day to 48 hours | Weeks to months | Yes | Prompt/context/time-bound | Medium |
| AI visibility score | Medium/high | 1–7 days if daily product | Months | Usually | Product estimate | Medium |
| Keyword volume/CPC/competition | Medium | 2–6 weeks | Months to years | Sometimes | Monthly cadence estimate | High |
| Backlink counts / referring domains | High | 1–14 days | Months | Usually | Provider-relative | High |
| Authority/domain metrics | Medium | 2–4 weeks | Months to years | Sometimes | Proprietary metric | High |
| Estimated organic traffic | Medium | 2–4 weeks | Months to years | Sometimes | Provider estimate | High |
| GSC/Bing first-party search metrics | Medium | Refresh if used current-state beyond provider lag | Inside retention window | Often | Reporting delay/provisional data | High/Medium |
| YouTube Analytics | Medium | Refresh if current-performance claim | Good historical use | Often | Few-days lag | High |
| Etsy/Fiverr/Shopify/Pinterest private analytics | Medium | Depends on report freshness | Strong for history within native windows | Often | Platform-specific delay rules | Medium |
| Listing/page snapshot | Medium | 1–4 weeks for descriptive state | Long archival | Often | Page may have changed | Medium |
| Marketplace search result | High | Same day to 7 days | Weeks to months | Yes | Discovery surface churn | Medium |
| Pinterest trend/search observation | High | 1–14 days | Seasonal/yearly | Usually | Trend-sensitive | Medium |
| Screenshot/HTML snapshot | Archival | Not for “now” unless very recent | Long archival | If used for current claim | Proves observed then, not now | High |
| Rights/pricing/terms | F5 for action | Same-day recheck | Long archival as historical record | Yes | Re-verify before action | High |

### Appendix — Warning Types

| Warning | Trigger | Text |
|---|---|---|
| evidence_age_warning | Age exceeds soft threshold | “Observation age may limit safe current-state use.” |
| stale_for_current_claim_warning | Age exceeds current-use window | “Stale for present-tense claims; use historically or refresh.” |
| provider_update_unknown_warning | Cadence not verified | “Provider update cadence is unclear; do not assume recency.” |
| non_synchronous_comparison_warning | Capture-time distance too large | “Comparison is non-synchronous and may mislead.” |
| high_volatility_surface_warning | Evidence type high/very high volatility | “This surface changes quickly and may not reproduce.” |
| rights_recheck_required_warning | Terms/pricing/rights not freshly verified | “Re-check required before action or customer-facing use.” |
| customer_private_overlay_warning | Public read mixed with private analytics | “Includes customer-private analytics; not default Observatory evidence.” |
| AI_reproducibility_warning | AI capture missing context or old | “AI observations are prompt/context/time-bound and may not reproduce.” |
| preliminary_data_warning | Provider flags provisional data | “This period may include preliminary provider data.” |
| estimate_not_fact_warning | Metric is estimated | “This is a provider estimate, not an exact current fact.” |

### Appendix — Hammer Test Candidate List

| Candidate test | Intent |
|---|---|
| Current-rank claim from stale SERP capture fails | Prevent false present-tense rank claims |
| AI-citation claim without prompt/timestamp fails | Prevent context-free AI visibility claims |
| Non-synchronous provider comparison warns/fails by threshold | Enforce timing discipline |
| Rights/pricing claim from stale doc fails | Enforce re-verification before action |
| Estimate described as factual demand fails | Preserve estimate caveat |
| Unknown provider cadence without caveat fails | Prevent hidden certainty |
| Preliminary-data periods without warning fail | Preserve native provider caveats |
| Historical evidence used as current state without warning fails | Preserve safe-use boundaries |
| Missing capture context on local/AI/search surfaces fails | Prevent decontextualized reads |
| Mixed private/public overlay without warning fails | Respect evidence boundary and report safety |