# SERP Feature and SERP Snapshot Evidence Research Report for The Observatory

## Executive Summary

A safe working definition for this project is: **a SERP snapshot is an observation of a search result surface at a specific time and request context, not universal ranking truth**. Google explicitly says search results can differ by time, place, device, and recent history, and Search Console’s own position/impression heuristics are described as subject to change. That makes a SERP snapshot evidence of **what was observed**, not proof of what every user sees. citeturn18view2turn18view1turn36view2

For The Observatory, the best candidate evidence is the combination of: query, search engine/surface, provider, location, language, device, timestamp, page/depth, provider request or task ID, structured result objects, feature classifications, and—when the provider allows it—raw HTML and a screenshot. DataForSEO and SerpApi are the strongest documented sources here because they expose structured result objects and raw HTML, and DataForSEO also documents screenshots and pixel rectangles. Google Search Console and Bing Webmaster Tools are first-party performance telemetry for owned properties, but they are **not** full-page SERP snapshots. Ahrefs and Semrush are useful comparison instruments, but their documented outputs are more feature/ranking analytics than literal browser-state recordings. citeturn19view2turn19view4turn33view0turn21view0turn22view0turn18view2turn34view5turn34view3turn24view1turn24view3

Organic rank alone is not enough. Google’s own documentation explains that position is a heuristic, compound elements can occupy a single position, and a prominent module can have a worse numeric position while still taking more visual attention. Search Console also assigns every link inside an AI Overview the same position as the AI Overview container, and every item in a qualifying carousel the same container position. In other words, “rank #3” can mean very different things depending on layout. That is exactly why The Observatory should treat **rank, feature presence, and visual real estate** as separate evidence classes. citeturn36view2turn36view3turn18view1

Volatility is real, and some surfaces are chaos wearing a tie. Google publishes ranking updates on the Search Status Dashboard; Search Console now has separate generative AI reporting for a subset of sites; Bing launched AI Performance in public preview in 2026; Semrush and Ahrefs both publish current studies showing meaningful AI Overview volatility and shifting feature prevalence. Freshness, rollout state, and provider cache state therefore need to be treated as first-class provenance. citeturn16search0turn16search7turn27view0turn34view5turn18view3turn25view2turn17search1

The strictest claim-safety rule is simple: **record “observed” and “not observed,” never “exists everywhere” or “does not exist.”** A target URL that does not appear in a particular snapshot is only “not observed within depth N, provider P, context C, at time T.” It is not proof of non-existence, non-ranking everywhere, or durable absence. That boundary is supported by Google’s explicit context-specificity language and by provider-specific limits such as depth, feature coverage, caching, and parsing strategy. citeturn18view2turn19view2turn21view0turn24view6turn24view7

## Confidence and Source Quality

**Official facts.** This report is strongest where it relies on Google Search Central, Search Console Help, Bing Webmaster API and Bing Webmaster blog documentation, DataForSEO API docs, SerpApi docs, Ahrefs Help, and Semrush Help. Those sources directly document feature definitions, counting rules, request parameters, exposed metadata, API objects, and rollout caveats. citeturn18view0turn18view1turn18view2turn34view0turn34view1turn34view3turn18view3turn19view2turn19view4turn33view0turn21view0turn21view1turn21view2turn24view0turn24view1turn24view3turn25view0

**Third-party claims.** This report uses Semrush, Ahrefs, and BrightLocal mainly for volatility studies, local/device variation guidance, and practical rank-tracking limitations. Those claims are useful and current, but they remain provider-specific analyses rather than search-engine source-of-truth. They are treated as directional evidence, not doctrine engraved on a stone tablet by the ranking gods. citeturn25view2turn17search0turn17search1turn17search3turn35search6

**Inferences.** The following conclusions are inferences from the source material rather than direct quotations from any one document: the proposed “instrument/witness” framing for providers, the recommended observatory handling categories, the safe/unsafe claim matrix wording, the suggested freshness buckets, and the recommendation to separate rank, feature presence, and visual real estate into distinct contracts. These inferences are grounded in the cited official counting rules, provider parameter docs, and rollout caveats. citeturn18view1turn36view2turn19view2turn19view4turn21view0turn34view5turn18view3

**Unclear — needs confirmation.** Bing Webmaster’s public-preview AI Performance UI is documented, but a formal Bing Webmaster API endpoint for that report is not documented in the primary API overview loaded here. Google’s generative AI performance reports are still in partial rollout. Some SERP feature names are provider abstractions rather than Google/Bing official surface names. Social/X modules remain inconsistently documented and can be region- and product-dependent. citeturn18view3turn34view3turn27view0turn34view5turn24view0turn24view3

## Source List

Key primary and near-primary sources used in this report. All were accessed **July 10, 2026**.

- Google Search Central, **Visual Elements gallery of Google Search**. citeturn18view0  
- Google Search Central, **Featured snippets and your website**. citeturn34view1  
- Google Search Central, **AI features and your website**. citeturn34view0  
- Google Search Central, **Structured data markup that Google Search supports**. citeturn34view2  
- Google Search Console Help, **Performance report** and **What are impressions, position, and clicks?**. citeturn18view2turn18view1  
- Google Search Console Help, **Generative AI performance report**. citeturn34view5  
- Google Search Central Blog, **Introducing Search Generative AI performance reports in Search Console**. citeturn27view0  
- Google Search Central Blog, **Changes to HowTo and FAQ rich results** and Search Console **data anomalies** page. citeturn29search1turn28search13  
- Bing Webmaster API overview. citeturn34view3  
- Bing Webmaster Blog, **Introducing AI Performance in Bing Webmaster Tools Public Preview**. citeturn18view3  
- Bing Webmaster Blog, **Start Using Bing Webmaster Tools to Improve Your Site Visibility**. citeturn31search1  
- DataForSEO API docs, **Google SERP overview**, **Live Advanced**, **Live HTML**, **AI Mode Advanced**, and **SERP Screenshot**. citeturn19view2turn19view0turn19view4turn19view1turn33view0  
- SerpApi docs, **Google Search API**, **Google AI Overview API**, **Google AI Mode API**, **Google Shopping API**, and pricing. citeturn21view0turn21view1turn21view2turn21view4turn23search0  
- Ahrefs Help, **What are SERP features?**, **SERP Overview**, and **SERP updates**. citeturn24view0turn24view1turn24view2  
- Semrush Help, **Researching SERP Features**, **SERP Features API codes**, **Position Tracking Overview**, **AI Overview**, and related feature pages. citeturn24view3turn24view4turn24view5turn25view0turn24view6turn24view7  
- Semrush Sensor and Semrush AI Overview study. citeturn16search2turn25view2  
- Ahrefs volatility studies on SERPs and AI Overviews. citeturn17search1turn17search3  
- BrightLocal local ranking/device variation guidance. citeturn35search6

## Core Findings

**SERP Snapshot Concept.** A SERP snapshot is best treated as a **time-bound, context-bound observation package**. At minimum, it may capture the query, engine or vertical, location, language, device, results page and depth, result and feature objects, and provider metadata. It is time-bound because search engines and provider pipelines change over time; context-bound because Google itself says results can vary by time, place, device, and recent history. DataForSEO and SerpApi further show this in their request models through location, language, device, safe search, and pagination parameters. citeturn18view2turn19view2turn19view0turn21view0

**What a snapshot can prove.** It can prove that **provider or surface Y reported or rendered feature/result X for query Q at time T under context C**. If HTML or a screenshot is also stored, it can additionally prove that the provider represented the layout in that captured form. If pixel rectangles are provided, it can support a bounded claim about relative on-screen footprint for that provider-rendered view. citeturn19view4turn19view1turn33view0

**What a snapshot cannot prove.** It cannot prove universal ranking truth, all-user visibility, persistence over time, click-through behavior, causality, or that one provider’s parser exactly equals the native search engine UI in all cases. Google’s own help pages warn that results vary by context and that position heuristics are approximate. Provider APIs also expose caches, task timing, and parsing abstractions that can diverge from a live signed-in browser. citeturn18view2turn36view2turn23search2turn19view3

**Organic rank vs feature presence vs visual real estate.** These are different evidence classes and should stay different. Organic rank is a position measure for a URL within some provider/result model. Feature presence is evidence that a module existed on the page, such as a local pack, AI Overview, or PAA block. Visual real estate is the layout footprint and prominence that a user actually encounters. Google documents many compound elements as occupying a single position; DataForSEO documents pixel rectangles and browser viewport parameters to estimate screen footprint. A numeric rank without layout context can therefore be simultaneously true and misleading. Fun. Terrible, but fun. citeturn36view2turn36view3turn19view1turn19view4

**SERP context metadata required for meaningful observation**

| Metadata Field | Why It Matters | Required? | Notes |
|---|---|---:|---|
| Query | Defines the observed search intent input | Yes | Without the exact query, the observation is basically a postcard from nowhere. citeturn19view0turn21view0 |
| Search engine / surface | Web, Images, News, Shopping, Local, AI Mode, etc. are different surfaces | Yes | Google and providers document separate search types and engines. citeturn18view2turn21view0turn21view1turn21view2 |
| Provider | Needed because provider parsing is testimony, not authority | Yes | GSC, Bing, DataForSEO, SerpApi, Ahrefs, and Semrush expose materially different evidence surfaces. citeturn34view3turn19view2turn21view0turn24view1turn24view3 |
| Capture timestamp | Makes the observation time-bound and comparable | Yes | SerpApi exposes created/processed timestamps; provider tasks are time-specific. citeturn22view1turn19view2 |
| Location | SERPs vary by geography and proximity | Yes | Google, DataForSEO, and SerpApi all document location parameters. citeturn18view2turn19view0turn22view3 |
| Language | Search language changes result mix and feature eligibility | Yes | Documented in Google and provider localization parameters. citeturn30search0turn19view0turn21view0 |
| Country / domain | Country bias and Google domain can affect filtering | Usually | SerpApi documents `gl` and `google_domain`; Google multilingual docs support language/locale distinctions. citeturn21view0turn30search0 |
| Device type | Desktop vs mobile changes layout and visibility | Yes | Google and providers document device-level differences and parameters. citeturn18view2turn19view2turn21view4 |
| OS / browser preset | Some providers emulate OS/device presets and screenshots around them | Usually | Important when provider rendering depends on browser profile. citeturn19view0turn33view0 |
| Viewport / screen size | Needed for pixel/panel prominence claims | Conditional | Required only if visual real estate is part of the evidence package. citeturn19view1turn33view0 |
| Result depth | “Not observed” means nothing without knowing how deep you looked | Yes | Depth and page are explicitly documented by providers. citeturn19view2turn33view0 |
| Page number | Needed because page 1 and page 5 are not the same planet | Yes | Providers expose pagination and page references. citeturn20view3turn22view2 |
| SafeSearch | Can suppress or alter results | Usually | SerpApi documents `safe`; include when specified. citeturn21view0 |
| Personalization / login state | Major caveat on whether the capture is depersonalized | Yes, if known | Google says results vary by recent history; DataForSEO says personalized factors are ignored in its Google News system. citeturn18view2turn19view3 |
| Search Labs / experimental state | Needed because some Google experiments are excluded from reporting | Conditional | Search Console excludes Search Labs experiments. citeturn18view1turn34view5 |
| Provider request / task ID | Enables provenance, replay, and cross-checks | Yes | Documented by DataForSEO, SerpApi, and screenshot endpoints. citeturn19view0turn22view1turn33view0 |
| Raw result objects | Core observable evidence | Yes for API snapshots | Prefer storing provider-returned objects over provider summaries only. citeturn19view0turn21view0 |
| HTML reference | Helps verify provider parsing and support disputes | Conditional | DataForSEO and SerpApi document raw HTML outputs. citeturn19view4turn22view0 |
| Screenshot reference | Needed for visual claims and dispute review | Conditional | DataForSEO documents SERP screenshot support; manual capture may also be needed later. citeturn33view0 |
| Status / error / cost metadata | Useful for auditability and replay confidence | Usually | DataForSEO and SerpApi both expose status and task metadata; some expose cost. citeturn32search6turn22view1turn33view0 |
| Rights / retention classification | Needed before persistent storage or customer display | Yes | Providers document retention windows and plan features; HTML/screenshots may have storage caveats. citeturn33view0turn23search0 |

**Variation factors that change SERPs**

| Variation Factor | Effect on SERP | Caveat Needed |
|---|---|---|
| Geography | Changes local packs, country-sensitive results, and regional content eligibility | “Observed in recorded location only.” citeturn18view2turn22view3 |
| Language | Changes result language mix and multilingual result handling | “Observed in recorded query/interface language only.” citeturn30search0turn21view0 |
| Device | Changes layout, feature prominence, and mobile-local behavior | “Observed on recorded device class only.” citeturn18view2turn35search6 |
| Viewport / screen size | Changes visible rows, above-the-fold area, and image/video packing | “Visual prominence depends on recorded viewport.” citeturn36view2turn19view1 |
| Recent history / personalization | Changes individualized results and can alter ranking order | “May differ for users with different history/profile state.” citeturn18view2 |
| Signed-in / Search Labs state | Can enable or exclude experimental/AI experiences | “Experiment and account state may change the surface.” citeturn18view1turn34view5 |
| SafeSearch | Can suppress or alter explicit results | “Observed with recorded SafeSearch state.” citeturn21view0 |
| Time / freshness | News, shopping, events, and AI answers can change rapidly | “Observation is time-bound.” citeturn16search0turn18view3turn25view2 |
| Provider cache vs live fetch | Cached responses can diverge from current live results | “Provider cache/live mode affects recency.” citeturn23search2turn21view1 |
| Provider parsing differences | Feature naming and object boundaries differ by provider | “Classification reflects provider parsing.” citeturn24view3turn24view0turn19view0 |
| Local proximity / GPS | Especially affects local results on mobile | “Local results may vary within the same city.” citeturn22view3turn35search6 |

**Required warning language.**  
**This SERP observation is bound to the recorded search context and may differ by location, language, device, personalization, and time.** That phrasing is directly aligned with Google’s description of result variability and with provider-specific context parameters. citeturn18view2turn19view0turn21view0

**Volatility model**

| SERP Type / Feature | Volatility | Refresh Consideration | Caveat |
|---|---|---|---|
| Standard organic web results on evergreen queries | Moderate | Daily to weekly checks are usually more meaningful than minute-level panic | Core updates and competitor changes can still cause sharp movement. citeturn16search0turn16search7turn17search3 |
| Featured snippets | Medium to high | Frequent rechecks if snippet ownership matters | Google determines eligibility algorithmically; no manual “mark as featured snippet.” citeturn34view1 |
| People Also Ask | High | Refresh often if PAA coverage matters | Expansion behavior and contained links are dynamic; impressions depend on expansion/visibility. citeturn36view0 |
| Local pack / map pack | High | Refresh more often and by precise geo points | Proximity, device, and business information freshness matter heavily. citeturn35search6turn18view3 |
| Shopping / product modules | High | Refresh often for commerce workflows | Inventory, pricing, merchant data, and policy/markup changes can shift presentation quickly. citeturn13search10turn21view4 |
| Top stories / news | Very high | Near-real-time if you care about it | Freshness and breaking events dominate. citeturn19view3turn30search16 |
| Image and video packs | Moderate to high | Depends on content cadence and query class | Layout and visibility vary by device and screen width. citeturn18view0turn36view2 |
| Jobs / events / travel modules | High | Refresh according to feed currency and event timing | Underlying structured data and provider feeds change quickly. citeturn13search12turn13search15 |
| Knowledge panels / entity panels | Moderate | Refresh after major entity/profile changes | Facts may be sourced and updated independently of your page ranking. citeturn11search4turn34view2 |
| AI Overviews | Very high | Short refresh cycles for affected queries | Google reporting is still evolving; Semrush and Ahrefs both show rapid change. citeturn34view5turn25view2turn17search1 |
| AI Mode | Very high | Treat as experimental/fast-changing | Coverage and reporting are still developing; not all languages are supported equally in provider docs. citeturn34view5turn21view2 |

## SERP Feature Taxonomy

**Taxonomy principle.** A feature matters when it changes either **eligibility**, **visibility**, **click opportunity**, or **citation opportunity**. That includes classic SEO features like featured snippets and local packs, GEO-relevant features like AI Overviews and AI Mode, marketplace features like shopping/product modules, and video/image surfaces that compete for screen real estate. Google’s visual elements gallery and structured-data gallery confirm that the modern results page is made of multiple result element types beyond plain text results. citeturn18view0turn34view2

**Appendix A — SERP Feature Taxonomy Table**

| Feature name | What it is | What evidence it provides | Observable fields | SEO/GEO relevance | Common caveats | Stable / volatile |
|---|---|---|---|---|---|---|
| Organic result | Standard text result based on page content | URL/page observed in result set; title/snippet/site name | URL, domain, title, snippet, position, page | Core SEO baseline | Position is approximate and context-dependent. citeturn18view0turn36view2 | Moderate |
| Paid ad | Sponsored search result | Paid presence observed on page | Ad position, title, link, domain, sometimes sitelinks | Important for true page-share accounting | Not organic visibility; provider classification varies. citeturn21view0turn19view2 | High |
| Featured snippet | Promoted extract from one source page | Source page observed as snippet source | Source URL, title, snippet text, container position | High SEO value; can displace clicks | Google decides eligibility; one snapshot does not prove durable ownership. citeturn34view1turn36view0 | Medium-high |
| People Also Ask | Expandable Q&A suggestions | PAA block present; linked sources observed if expanded/returned | Questions, linked URLs, snippet text | Strong intent and query-expansion signal | Expansion changes what is visible/counted. citeturn34view1turn36view0 | High |
| Knowledge panel / entity panel | Entity/business info panel | Entity presence; facts, links, actions, images | Entity name, attributes, links, profile/business details | High for brand/entity SEO and local | Facts may reflect Google/entity sources, not your site alone. citeturn11search4turn34view2 | Moderate |
| Local pack / map pack | Local business group for local intent | Local module presence; listed businesses | Business names, ratings, hours, address, CID/place IDs, links | Critical for local SEO and local GEO | Highly geo/device/proximity sensitive. citeturn34view2turn35search6turn20view4 | High |
| Local finder | Expanded local results view | Broader local candidate set | Business listing objects, map identifiers | Important for deeper local observation | Not the same as pack visibility on page one. citeturn2search10turn35search4 | High |
| Image pack / image result | Image thumbnails in web or image search | Image feature presence; linked image sources | Image URL, landing page, source, position/container | Important for image SEO and blended SERP share | Layout changes with screen width; position is rough. citeturn18view0turn36view2turn13search7 | Moderate-high |
| Video pack / video result | Video results or carousel | Video surface present; source pages/videos | Video title, source, duration, thumbnail, watch/landing URL | Important for video SEO | Can be blended, carousel-based, or tab-specific. citeturn18view0turn4search18 | Moderate-high |
| Top stories / news | News-focused module | News module present; cited stories | Publisher, headline, timestamp, URL | Strong for news visibility | Extremely freshness-sensitive. citeturn21view3turn19view3 | Very high |
| Shopping / merchant listing / product grid | Commerce-oriented product modules | Commercial module present; product entries observed | Product title, price, rating, seller/source, availability | Core marketplace/ecommerce visibility signal | Prices and inventory move; modules can be feed-driven. citeturn13search10turn21view4 | High |
| Review stars / ratings | Review-rich decorations or panel ratings | Review snippet observed | Rating value, votes/review count, associated URL/entity | Important CTR and trust signal | Eligibility depends on markup/content type; not always URL-scoped. citeturn13search1turn11search8 | Moderate |
| Sitelinks | Additional links under a result | Brand/navigation expansion observed | Child links, labels, sometimes search box | Important branded/nav visibility signal | Often algorithmic and query-dependent. citeturn24view0turn24view3 | Moderate |
| FAQ rich result | FAQ expansion from structured data | Historically: FAQ presence and linked answers | Questions, answers, source URL | Formerly useful; currently poor target | Google says FAQ rich results stopped appearing as of May 7, 2026. citeturn29search4turn28search13 | Not currently active on Google web search |
| How-to rich result | Step-based instructional rich result | Historically: step cards/summary | Steps, images, source URL | Formerly useful; currently poor target | Google says How-to rich results are deprecated and no longer shown. citeturn29search1 | Deprecated |
| Recipe | Food result or host carousel | Recipe module presence; source page inclusion | Rating, cook time, nutrition, image, source URL | Important for food content and image search | Structured-data driven, but still context-dependent. citeturn13search9turn34view2 | Moderate |
| Jobs | Job search experience | Job module present; postings observed | Job title, employer, location, salary, apply target | Important for job marketplace visibility | Special search experience, feed/data freshness matters. citeturn13search15turn34view2 | High |
| Events | Event search experience | Event module present | Event title, date, venue, ticket/action links | Important for venues, ticketing, local discovery | Event timing makes stale data toxic. citeturn13search12 | High |
| Flights / hotels / travel modules | Travel-specific experiences | Travel module presence and listings | Destination/property, price, dates, booking links | Important in travel verticals | Often vertical-specific and geo/date-sensitive. citeturn20view1turn19view2 | High |
| Discussions / forums / Reddit/forum blocks | Forum/community result groupings | Discussion module present; thread sources observed | Thread titles, forum domains, URLs | Meaningful for community/forum visibility | Provider naming varies; Google support also changes over time. citeturn11search10turn15search4 | Medium-high |
| Social / tweets / X modules | Social or tweet blocks where present | Social surface presence | Post/user/card links | Can matter for news/brand queries | Inconsistent and region/product dependent; treat as unstable. citeturn24view0 | High / unclear |
| AI Overview | AI-generated overview with supporting links | AI feature presence; cited/supporting URLs observed | Summary blocks, cited URLs, container position, sometimes page token | Critical GEO surface | Reporting and parsing still evolving; cited link position ≠ classic rank. citeturn34view5turn36view3turn21view1 | Very high |
| AI Mode | Conversational AI search surface | AI Mode presence; follow-up flow and sources | Answer/source links, follow-up state, sometimes language support caveats | Critical GEO surface | Still rapidly evolving; follow-ups count as new queries in GSC. citeturn21view2turn18view1turn34view5 | Very high |
| Related searches / people also search for | Query refinement suggestions | Query-expansion feature presence | Suggested queries, sometimes grouped topics | Useful for query-panel evidence, not ranking proof | Often no URL-level evidence; Semrush can detect presence only. citeturn24view7turn21view4 | Moderate |
| Zero-click answer / answer box / instant answer | Direct answer rendered on SERP | Query answered on page without click requirement | Answer text, source if present, container type | Important for click displacement analysis | Can be source-less or query-refinement-like; not always URL-rankable. citeturn21view0turn24view5 | Medium-high |

## Provider SERP Feature Support

**Provider comparison principle.** These sources should be treated as different instruments, not interchangeable truth machines. Broadly: DataForSEO and SerpApi are **snapshot providers**; GSC and Bing Webmaster are **first-party owner telemetry**; Ahrefs and Semrush are **analytical SERP observers**. That distinction matters more than vendor marketing copy. Marketing copy is always very confident right up until reality shows up with a folding chair. citeturn19view2turn21view0turn18view2turn34view3turn24view1turn24view3

**Appendix B — Provider SERP Feature Support Table**

| Provider | SERP Feature Coverage | Raw Objects? | Context Metadata? | AI/SERP Features? | Caveats |
|---|---|---:|---:|---:|---|
| DataForSEO SERP API | Broad coverage across Google web, images, news, local, AI Overview, AI Mode, and more; Advanced endpoint documents extra SERP elements | Yes | Strong | Yes | Exposes raw HTML, task IDs, status/cost, screenshots, and pixel rectangles; personalized factors may be ignored in some systems; extra charges for some AI/screenshot/rectangle features. citeturn19view2turn19view0turn19view4turn19view1turn33view0turn19view3 |
| SerpApi | Broad Google coverage across organic, ads, local, knowledge graph, answer box, images, news, shopping, videos, plus dedicated AI Overview and AI Mode endpoints | Yes | Strong | Yes | Documents raw HTML and structured JSON; exposes `search_metadata.id`, timestamps, location/language/device params; default cache is 1 hour unless disabled. citeturn21view0turn21view1turn21view2turn22view0turn22view1turn23search2 |
| Google Search Console | No full SERP snapshot; own-site search, News, Discover, and generative AI performance only | No | Moderate | Yes, for owned-site reporting | First-party performance telemetry, not competitor or whole-page SERP evidence; reports are rolled out selectively and exclude Search Labs experiments. citeturn18view2turn18view1turn34view5turn27view0 |
| Bing Webmaster Tools / API | Search performance for owned sites; AI Performance preview for AI citations in Bing/Copilot/partner surfaces | No | Moderate | Yes, in UI | Site-owner data only; official API overview lists rank & traffic, link, keyword, crawl stats; AI Performance API support is not documented here. Unclear — needs confirmation. citeturn34view3turn18view3turn31search1 |
| Ahrefs | Tracks many SERP features; SERP Overview shows recent and historical SERPs, location/date comparisons, top 100 results | Partial | Moderate | Yes | Useful for comparison/history; not documented as raw HTML or screenshot evidence in the sources reviewed; plan limits affect historical access. citeturn24view0turn24view1turn24view2 |
| Semrush | Tracks up to 50 SERP features; Organic Research, Position Tracking, Sensor, and AI Overview support | Partial | Moderate | Yes | Good feature/rank analytics; not a raw browser-state snapshot; some features are presence-only with no URL attribution or saved position. citeturn24view3turn24view4turn24view5turn25view0turn24view6turn24view7 |

**Evidence and provenance fit**

| Evidence Need | SERP API Support? | Notes |
|---|---|---|
| Provider name | Yes | All reviewed tools/providers identify themselves or the API used. citeturn19view2turn21view0turn34view3 |
| Search engine / surface | Yes | DataForSEO and SerpApi explicitly model engine/surface types. citeturn19view2turn21view0 |
| Query | Yes | Fundamental request parameter everywhere. citeturn19view0turn21view0 |
| Location | Usually yes | Strong in snapshot APIs; owner tools aggregate by country rather than whole-page replay. citeturn19view0turn22view3turn34view5 |
| Language | Usually yes | Strong in snapshot APIs; weaker in owner telemetry. citeturn19view0turn21view0 |
| Device | Usually yes | Strong in snapshot APIs and GSC/Bing reporting dimensions. citeturn19view2turn21view4turn34view5turn31search1 |
| Capture timestamp | Yes | Strong in DataForSEO tasks and SerpApi metadata. citeturn22view1turn32search6 |
| Request/task ID | Yes in APIs | Important provenance anchor. citeturn22view1turn33view0turn32search6 |
| Result depth / page number | Yes in snapshot APIs | Essential for safe absence claims. citeturn20view3turn22view2 |
| Result objects | Yes in snapshot APIs; partial in analytics tools | DataForSEO/SerpApi strongest. citeturn19view0turn21view0 |
| SERP feature objects | Yes in snapshot APIs; partial elsewhere | Semrush and Ahrefs expose many feature states, but not always full raw objects. citeturn19view0turn24view0turn24view3 |
| Rank / position | Yes, but semantics vary | GSC position is heuristic; Semrush AI Overview can record citation as #1 feature rank; do not flatten these. citeturn36view2turn25view0 |
| URL / domain / title / snippet | Usually yes | Not universal for every feature; Semrush documents some presence-only features with no URL capture. citeturn20view3turn24view6turn24view7 |
| Paid / organic / feature classification | Usually yes | Snapshot APIs and analytics tools both do this, though taxonomies differ. citeturn21view0turn24view3 |
| Raw payload if allowed | Yes in snapshot APIs | Prefer yes where terms allow retention. citeturn19view4turn22view0 |
| Screenshot / HTML if allowed | Partial | DataForSEO documents both; SerpApi documents HTML; screenshot support was not documented in the SerpApi sources reviewed. citeturn33view0turn22view0 |
| Cost metadata | Partial | Strong in DataForSEO; some commercial providers expose pricing plans rather than per-result cost. citeturn33view0turn23search0 |
| Status / error metadata | Yes in APIs | Strong in DataForSEO and SerpApi. citeturn32search6turn22view1 |
| Rights / retention classification | Partial | Must be tracked by Observatory; provider docs show retention windows and plan constraints. citeturn33view0turn23search0 |
| Volatility caveat | No direct field | Must be attached by Observatory/LLM based on source class and query class. Inference grounded in docs and studies. citeturn16search0turn25view2turn17search1 |

## Claim Safety and Decision Inputs

**Safe principle for rank and visual real estate.** Google’s position metric is approximate, container-based for many elements, and can mislead when taken literally. A prominent knowledge panel or AI Overview may occupy one position while dominating page attention, and a carousel can assign one position to multiple items. DataForSEO’s rectangle/pixel parameters show that visual prominence is a separate measurable layer. Therefore: **ranking position is only one visibility signal; SERP layout and feature presence can change actual attention opportunity.** citeturn36view2turn36view3turn19view1

**Appendix C — Safe vs Unsafe Claim Matrix**  
The matrix below is an Observatory policy inference grounded in the cited context-specificity, counting, and provider-parsing rules. citeturn18view2turn18view1turn19view2turn21view0

| Evidence | Safe Wording | Unsafe Wording | Required Caveat |
|---|---|---|---|
| Organic result | “For query X, provider Y observed URL Z as an organic result at observed position N on date/time T under context C.” | “URL Z ranks #N everywhere.” | Bound by provider, time, location, language, device, and depth. |
| Featured snippet | “A featured snippet sourcing URL Z was observed for query X in provider Y at time T.” | “URL Z owns the featured snippet for this query.” | Snapshot proves observation, not permanence. |
| Local pack | “A local pack was observed, and business/entity X appeared within the returned local listings in context C.” | “Business X is in the map pack for everyone.” | Local results vary heavily by geography, device, and proximity. |
| Video carousel | “A video carousel was observed for this query/context at capture time.” | “Video is always required for this query.” | Presence does not prove universal necessity or durability. |
| Image pack | “An image module was observed, and target asset/page was present/not present in the returned image results.” | “The image does not rank.” | Absence is only within recorded depth/surface. |
| Shopping result | “A shopping/product module was observed, with product/result X returned by provider Y.” | “This product is guaranteed visible in Google Shopping.” | Feed state, merchant data, geography, and time matter. |
| People Also Ask | “PAA questions were observed for this snapshot; expanded/returned links included X.” | “Google always associates these questions with this query.” | PAA is dynamic and expansion-dependent. |
| AI Overview source | “An AI Overview was observed, and provider Y returned URL/domain X as a cited or supporting source.” | “Google endorses X as the best answer.” | Citation/source presence is not classic rank or endorsement. |
| Knowledge panel | “A knowledge/entity panel was observed containing attribute(s) X.” | “These panel facts are authoritative truth.” | Panel facts are surface observations, not guaranteed truth. |
| Review stars | “Review stars/rating metadata were observed on this result/entity at capture time.” | “This result permanently has review stars.” | Eligibility and rendering vary. |
| Site links | “Sitelinks were observed beneath result X in this snapshot.” | “Google always shows sitelinks for this brand.” | Sitelinks are query- and context-dependent. |
| SERP absence | “The target was not observed in the first N results/pages returned by provider Y for context C at time T.” | “The target does not rank for this keyword.” | Absence must be bounded by provider, depth, context, and time. |
| Rank position | “Provider Y reported/returned position N in this observation.” | “Position N represents actual user attention share.” | Rank does not equal prominence or click opportunity. |

**Appendix D — Negative Evidence Rules**

| Rule | Safe handling |
|---|---|
| Absence is bounded, never absolute | Record **not observed within recorded depth/page/provider/context/time**. |
| Depth must be attached | “Not observed” without page/depth is junk evidence wearing a trench coat. |
| Surface must be attached | Not observed in Web ≠ not observed in News, Images, Local, Shopping, AI Overview, or AI Mode. |
| Provider must be attached | Not observed by Semrush, GSC, or a SERP API are different statements. |
| Target type must be attached | Domain absence, URL absence, and feature absence are different facts. |
| Rollout/threshold caveats must be attached | Owner-tool reports may omit data because of thresholds, rollouts, or exclusions. citeturn34view5turn28search5 |
| Canonicalization caveat must be attached | GSC may assign performance to canonical URLs, not necessarily the literal clicked variant. citeturn18view1 |
| Personalization caveat must be attached if unknown | If login/history state is unknown, absence claims are weaker. |

**Provider cross-check disagreements**

| Disagreement Type | Likely Cause | Observatory Handling |
|---|---|---|
| Same query, different result set | Time drift, freshness, different crawl time, provider cache state | Record timestamps and cache/live state; do not collapse into one truth. citeturn23search2turn22view1 |
| Same query, different ranking | Location, language, device, recent history, or personalization | Compare only when context is aligned. citeturn18view2turn19view0turn21view0 |
| Same page, different position semantics | GSC uses average/topmost/container-style position heuristics | Store provider-specific position semantics and avoid naive normalization. citeturn36view2turn36view3 |
| Feature present in one provider, absent in another | Parsing/classification differences or limited feature support | Record provider testimony separately; prefer screenshot/HTML when available. citeturn24view6turn24view7turn19view4turn22view0 |
| AI feature disagreement | Rollout stage, language support, labs/experiment status, provider-specific AI handling | Treat AI observations as high-volatility evidence and tag rollout uncertainty. citeturn34view5turn21view2turn25view2 |
| Manual browser differs from provider API | Signed-in state, Search Labs, personalization, geolocation granularity, parser/rendering gaps | Preserve both as separate witnesses and compare only with full context notes. citeturn18view2turn19view3turn22view3 |
| Owned-site telemetry differs from live SERP API | GSC/Bing aggregate clicks/impressions/positions, not literal page-state | Do not compare as if they are the same artifact class. citeturn18view2turn34view3turn18view3 |

**Recommended Observatory handling**

Safe candidate material for Observatory:

- Full-context SERP observations from provider APIs with query, surface, location, language, device, timestamp, request/task ID, depth/page, structured result objects, and provider status metadata. citeturn19view0turn21view0turn22view1
- First-party owner telemetry from Google Search Console and Bing Webmaster Tools for owned properties, clearly labeled as **property performance reporting**, not raw SERP snapshots. citeturn18view2turn34view5turn18view3turn34view3
- HTML and screenshots where provider terms/documentation support them, especially for visual-real-estate evidence and dispute review. citeturn19view4turn22view0turn33view0

Most important features to prioritize early:

- Organic results  
- Paid ads  
- Featured snippets  
- People Also Ask  
- Local pack / local finder  
- Shopping / merchant listing / product modules  
- Image and video modules  
- Top stories / news  
- Knowledge panels / entity panels  
- AI Overviews  
- AI Mode observations where provider support exists, but with heavier volatility warnings. citeturn18view0turn34view1turn34view2turn34view5turn18view3turn21view1turn21view2

Features that should wait or be heavily deprioritized:

- FAQ rich results for Google web search, because Google says they stopped appearing as of May 7, 2026. citeturn29search4turn28search13
- How-to rich results, because Google says they are deprecated / no longer shown. citeturn29search1
- Provider-only presence indicators that do not expose URL attribution or stable object detail, unless clearly labeled as weak evidence. Semrush explicitly documents this limitation for some features such as related products and related searches. citeturn24view6turn24view7
- Social/X module tracking unless the supported markets/surfaces are explicitly defined. Unclear — needs confirmation. citeturn24view0

Evidence that needs strict caveats:

- Any position metric. Google’s own docs say it is approximate and context-sensitive. citeturn36view2
- Any AI Overview or AI Mode citation/source observation. Citation is not classic rank, and container position is not source position. citeturn36view3turn25view0
- Any absence statement. It must be bounded by depth, provider, time, and context. citeturn18view2turn19view2
- Any knowledge panel/entity fact observed on-SERP. Treat as page-surface observation, not authority. citeturn11search4turn34view2

Evidence that should use screenshots/manual capture later:

- Above-the-fold claims  
- Pixel/viewport prominence claims  
- Disputes about what was visually dominant  
- AI answer text/ordering disputes  
- Cases where provider parsing and live browser output disagree. citeturn19view1turn33view0turn22view0

Evidence that should remain provider testimony only:

- Provider-classified feature types where no HTML or screenshot is retained  
- Historical provider SERP databases without contemporaneous image proof  
- Analytic “feature present” signals from Ahrefs/Semrush where raw page-state is not documented. citeturn32search5turn24view1turn24view3

**Questions / unknowns to confirm**

- Whether Bing AI Performance will receive a documented export/API surface. Unclear — needs confirmation. citeturn18view3turn34view3
- Whether your provider admission policy will require screenshot retention for all “visual prominence” claims, or only for disputed claims. This is a product rule, not a documented external fact.  
- Which specific marketplace/video surfaces are in-scope at M1 if the Observatory later expands beyond Google/Bing web SERPs. The provider landscape is broader, but this report intentionally stayed on SERP evidence boundaries first.  
- Provider-specific retention and rights treatment for stored screenshots/HTML beyond the documented API retention windows. DataForSEO documents screenshot retrieval timing; other providers may require separate review. citeturn33view0turn23search0

**Decision inputs for M1 / M7 / M8 roadmap**

**Must know before M1 roadmap sequencing**

- Which evidence classes are admitted: structured objects only, or structured objects plus HTML plus screenshots.  
- Which features are “tier one”: organic, paid, featured snippet, PAA, local, shopping, image, video, news, knowledge panel, AI Overview.  
- Whether owner telemetry and SERP snapshots are stored in separate evidence lanes.  
- Whether visual real-estate claims are out of scope until screenshot or rectangle support exists.  

**Must know before M7 contracts**

- Required provenance fields: query, surface, provider, timestamp, location, language, device, depth/page, task/request ID, status/error, and retention classification.  
- Position semantics by provider must remain provider-specific.  
- “Not observed” language must be formally bounded.  
- AI citation/source evidence must be formally distinguished from classic rank evidence.  

**Must know before M8 hammers**

- Same-query cross-provider alignment requirements  
- Cache-vs-live comparison rules  
- Mobile-vs-desktop and geo-point hammer cases  
- Parser-vs-screenshot disagreement handling  
- Threshold/rollout exclusions for GSC and Bing AI reporting. citeturn34view5turn18view3

**Must know before provider admission**

- Does the provider expose raw objects, HTML, screenshots, timestamps, IDs, status, and rights/retention constraints?  
- Does the provider document location/language/device controls clearly?  
- Does the provider classify features in a stable, auditable way?  
- Does the provider distinguish live fetch from cache? citeturn19view2turn19view4turn33view0turn21view0turn23search2

**Must know before first customer-facing SERP claim**

- The exact safe language templates  
- The exact caveat strings required per feature class  
- The exact threshold for when a screenshot is mandatory  
- The exact rule separating “provider testimony” from “browser-observed capture.”  

**Decision-ready summary**

Recommended status:

- **Safe candidate for public SERP observation:** structured SERP/API observations with full context and explicit caveats; first-party owner telemetry clearly labeled as owner telemetry, not raw SERP truth. citeturn19view0turn21view0turn18view2turn18view3
- **Allowed only through provider/API:** Google/Bing SERP and AI-feature observations where supported by documented provider APIs and terms; HTML/screenshot use only where documented by the provider. citeturn19view4turn33view0turn21view1turn21view2
- **Risky / avoid automation:** direct non-permitted scraping, universal claims from single captures, visual-prominence claims without image/rectangle support, and collapsing position metrics across providers into a fake single truth. citeturn36view2turn19view1turn22view0
- **Not recommended:** using FAQ or How-to as current Google-web target features; claiming “does not rank” from absence in one panel or one provider. citeturn29search4turn29search1turn18view2
- **Needs more research:** Bing AI Performance API availability, provider retention/rights classification policy, and stable support expectations for AI Mode across providers. citeturn18view3turn34view3turn21view2

The bottom line is strict and boring in the best possible way: **The Observatory should store what was observed, with provenance and caveats. The LLM can argue about meaning later. The database should not cosplay as certainty.** citeturn18view2turn19view2turn21view0