# DataForSEO Research Report for The Observatory

## Executive framing

### Executive Summary

DataForSEO is an API-first data vendor for search, SEO, backlink, local/business, shopping, app-store, content-analysis, domain, and now AI-visibility data. Its commercial shape is very different from Ahrefs and Semrush: DataForSEO’s core offer is structured APIs with pay-as-you-go billing, a $50 minimum deposit, and a small free trial credit, while Ahrefs and Semrush remain subscription-led platforms whose APIs ride on plan eligibility and/or API-unit systems. That makes DataForSEO much more compatible with an evidence-only observatory that wants selective pulls instead of a full operator dashboard. citeturn10search10turn12view2turn12view0turn27search15turn27search7turn27search3

For The Observatory’s doctrine, DataForSEO is strongest when treated as a witness, not an oracle. Some returned fields are close to direct observations, such as SERP URLs, titles, snippets, positions, cited-source links, or backlink first-seen dates. Other fields are clearly provider-normalized or estimated, including keyword volume, clickstream-derived traffic, backlink “Rank,” keyword difficulty, and AI search volume. Those estimated fields are usable as attributed evidence, but only with careful provenance language. citeturn31view0turn35search15turn8search12turn11search14turn28search12turn32view2turn33search10

DataForSEO is promising as a first Observatory provider, but not cleanly approved yet. The main blockers are not capability. They are rights clarity and recent pricing churn. Official materials clearly show that DataForSEO expects customers to store some results on their own side, especially for Live endpoints, and explicitly says you can store Keyword Data results in your own database for filtering. But the reviewed legal pages do **not** provide a clean, explicit grant covering long-term archival of all raw payloads, redistribution, or customer-facing republication across all endpoint families. The Terms of Service do include a specific restriction on SERP data use against search-engine providers’ business interests. Also, a July 1, 2026 pricing update removed prior monthly commitments for Backlinks API and LLM Mentions API, while older help-center pages still describe those commitments. That mismatch means pricing and access rules must be revalidated before schema work or broad rollout. citeturn19view0turn10search2turn9view4turn29view0turn29view1

My decision-ready conclusion is this: **DataForSEO is a strong candidate for a later controlled pilot, but broad approval should be blocked until DataForSEO confirms storage, retention, and customer-facing display rights in writing, endpoint by endpoint.** For an internal-only pilot, the best first endpoints are Google Organic SERP Advanced, Google Local Finder or Maps SERP, Google Shopping, Google Ads Search Volume, selected DataForSEO Labs endpoints, and Backlinks Summary or narrow backlink extracts. AI features are real and materially useful, but the safest entry point is Google AI Overviews through Google Organic SERP, not the more ambitious LLM Mentions/LLM Responses layer. citeturn6view0turn30search2turn36view0turn14view6turn20search2turn31view0turn32view3turn18search11

### Confidence and Source Quality

Confidence is **high** on DataForSEO product scope, endpoint availability, pricing mechanics, rate limits, and task/result retention mechanics because those points are documented in official product pages, docs, help-center articles, and the current Terms of Service. Confidence is **medium** on current pricing details for Backlinks API and LLM Mentions API because official sources are internally inconsistent after the July 1, 2026 pricing update. Confidence is **low to medium** on storage, archival, redistribution, and customer-facing display rights because the official legal language reviewed is sparse and incomplete for those use cases. Confidence is **medium** on third-party comparison context because it depends partly on review platforms and competitor docs rather than a single normalized benchmark. Access date for all web sources below: **July 8, 2026**. citeturn29view0turn29view1turn9view4turn23view0turn12view1

### Source List

The load-bearing official sources used here were DataForSEO API docs, product pages, pricing pages, help-center articles, and the current Terms of Service. In particular: API introduction and product catalog; SERP API overview and pricing; Keyword Data API overview and pricing; DataForSEO Labs API docs and pricing; Backlinks API overview and pricing; OnPage pricing; Business Data API overview and pricing; Merchant Google Shopping docs and pricing; App Data API overview and pricing; AI Optimization product and docs; rate-limit guidance; result-retention guidance; database update guidance; and the Terms of Service updated June 12, 2026. citeturn10search6turn15search15turn12view1turn33search11turn14view6turn6view3turn7search0turn13view0turn14view5turn6view7turn36view0turn30search1turn7search3turn36view1turn6view4turn18search7turn23view0turn19view0turn22view0turn9view4

Third-party context used sparingly: G2 review summaries for current market perception, plus official Ahrefs and Semrush developer and pricing pages to compare platform shape and API access models. Those sources are contextual only; they do not override DataForSEO’s own docs. citeturn26search1turn26search3turn27search15turn27search7turn27search3turn27search2

## Provider and endpoint landscape

### Provider Overview

DataForSEO sells structured data APIs rather than a classic all-in-one SEO workbench. The company’s API catalog spans SERP data, keyword data, backlinks, technical crawling, local/business data, shopping/merchant data, app-store data, domain intelligence, content-analysis, and AI optimization. The dashboard exists mainly for account control, API credentials, billing, error inspection, and the API Playground, not as the primary product surface. That lines up much better with an instrument-provider role than with a strategy platform role. citeturn10search10turn10search6turn28search2

Relative to Ahrefs and Semrush, the practical difference is business model and product posture. DataForSEO is API-native and pay-as-you-go. Semrush and Ahrefs remain subscription suites first, with APIs attached to paid/eligible plans and unit or plan constraints. For a small operator doing selective, evidence-grade pulls, that is a real structural advantage: DataForSEO does not force a high monthly software subscription just to make a narrow set of calls. The tradeoff is that you must build your own handling, provenance, QA, and rights controls, because you are buying a data feed, not an opinionated workflow stack. citeturn12view2turn12view0turn27search15turn27search7turn27search3turn27search2

DataForSEO is suitable for small-scale selective pulls **economically** and **architecturally**, but only if you are comfortable with API complexity. A low-volume pattern is explicitly supported by their docs, the trial gives $1 of testing credit, and the general rate limit is large enough that selective Observatory pulls are nowhere near the ceiling. The real constraint for a small operator is not throughput. It is operational correctness: choosing the right endpoint, avoiding accidental duplicate tasking, distinguishing live snapshots from database-derived estimates, and not over-storing raw payloads before rights are clarified. citeturn12view0turn23view0turn21search13turn11search13turn9view4

### Endpoint Inventory

The table below is the short Observatory-first map. “Useful now” means strong fit for provider-as-witness evidence capture; “later” means useful but secondary; “not now” means the endpoint family is either too estimate-heavy or too far from the Observatory’s initial scope.

| Endpoint family | What it returns | Example evidence objects | Observatory use | Raw snapshot vs estimate | Usefulness | Main risks / limits | Pricing unit | Docs / pricing |
|---|---|---|---|---|---|---|---|---|
| SERP API | Organic, local, maps, shopping-adjacent, news, jobs, images, AI Mode, HTML/raw SERPs | query, location, device, SERP items, `ai_overview`, HTML, screenshot task | Core visibility observation | Mostly raw observed SERP output; some feature parsing | **Useful now** | volatility by device/location; extra parameter multipliers; rights uncertainty for raw HTML/screenshots | Google Organic: $0.0006 standard / $0.002 live per 10 results; AI Mode: $0.0012 standard / $0.004 live per page | citeturn15search15turn6view0turn12view1turn15search7turn24view0 |
| Keywords Data API | Google Ads and Bing Ads search volume, CPC, competition, keyword suggestions; Google Trends; DataForSEO Trends | keyword, monthly searches, CPC, competition, trend series | Baseline keyword evidence | Mostly provider/third-party metrics, not direct observation | **Useful now** | estimates, update lag, no raw SERP context | Google Ads: $0.06 standard / $0.09 live per task up to 1,000 keywords | citeturn33search11turn14view6turn21search0 |
| DataForSEO Labs API | Database-driven ranked keywords, competitors, domain rank, historical SERPs, keyword difficulty, search intent, app and Amazon research | ranked keyword row, historical SERP row, keyword difficulty, domain rank overview | Cross-sectional/historical evidence | Mixed: database observations plus proprietary estimates | **Useful now, but selective** | easy to over-trust modeled metrics; freshness varies | Usually $0.012 + $0.00012 per item; historical SERPs $0.00012 per SERP | citeturn6view3turn14view7turn35search9turn35search19 |
| Backlinks API | live backlink records, referring domains/pages, history, summary, intersection, timeseries | backlink row, referring domain, `first_seen`, lost date, summary counts | Link evidence and longitudinal changes | Mostly observed/live index data plus provider scores | **Useful now** | recent pricing churn; “Rank” is proprietary; high raw-volume storage risk | request + row pricing; currently $0.024 per request and $0.000036 per row on pricing page | citeturn7search0turn13view0turn20search6turn20search18turn29view0 |
| OnPage API | crawl tasks, page audits, HTML, internal links, page-speed and Lighthouse-style findings | crawl task, page check, page HTML, page screenshot | Technical evidence about owned/observed pages | Observed crawl output plus rule-based checks | **Later** | raw-volume explosion; expensive if JS/rendering enabled; not first visibility witness | from $0.00015 per crawled page, multipliers for resources/JS/rendering | citeturn7search1turn14view5turn5search14 |
| Domain Analytics API | Whois, expiring domains, registrar data, technology stack, domains by technology/HTML terms | domain technology stack, Whois record enriched with rank/backlink data | Adjacent context, not core SEO observation | Mixed direct registry/scan data and enriched metrics | **Later** | broad but not central to Observatory’s mission | around $0.012 + $0.0012 per item for many endpoints | citeturn35search0turn35search4turn35search12turn14view4 |
| Merchant Google Shopping API | product listings, sellers, product info, reviews, seller ad URLs | product row, seller row, review row | Ecommerce visibility evidence | Observed shopping marketplace data | **Useful now if ecommerce scope matters** | rights unclear; product pages can change quickly | $0.001 standard / $0.002 priority per product-seller-SERP; reviews per 10 | citeturn36view0turn30search1 |
| Business Data API | Google Business profile info/updates, reviews, hotels, Trustpilot, Tripadvisor, business listings | business info row, review row, hotel record | Local reputation and local-surface evidence | Mostly observed profile/review data | **Useful now for local** | multiple sources with different semantics; rights and moderation-state issues | GMB info $0.0015 standard per profile; reviews/hotels vary | citeturn6view7turn14view1turn14view3 |
| App Data API | Google Play and App Store searches, lists, app info, reviews, listings | app search result, app info row, review row | App-store visibility evidence | Observed store/search data | **Later** unless app visibility is in scope | secondary to web observatory; multiple result types | searches/list: $0.0012 standard per 100 items; reviews and info vary | citeturn7search3turn36view1 |
| Content Analysis API | web citations, sentiment, phrase/category trends, rating distribution | citation row, polarity, fetch time | Brand/citation evidence beyond SERP | Mostly observed citation data plus sentiment modeling | **Later** | sentiment is modeled; web cite rights unclear | $0.024 per request + $0.000036 per row | citeturn34search0turn34search1turn34search3turn34search5 |
| AI Optimization API | AI keyword data, LLM mentions, LLM responses, LLM scraper | AI search-volume row, mention row, ChatGPT/Gemini/Claude/Perplexity response, cited sources, fan-out queries | GEO / AI-search evidence | Mixed raw/generated/model-derived data | **Useful, but controlled** | platform coverage uneven; legacy/new paths coexist; pricing clarity weaker than SERP | AI Keyword Data $0.01 + $0.0001 per keyword; LLM Responses adds LLM cost; LLM Mentions pricing needs support confirmation | citeturn18search7turn18search11turn32view3turn14view0turn29view0 |

### Appendix A

For The Observatory’s first slice, the best endpoint families are the ones that create durable, provenance-rich evidence units with small payloads and obvious semantics: Google Organic SERP Advanced, Google Local Finder or Maps, Google Shopping, Google Ads Search Volume, DataForSEO Labs Domain Rank or Ranked Keywords, and Backlinks Summary or narrow backlink extracts. OnPage, Content Analysis, App Data, and large-scale LLM features are all usable later, but they carry a much higher risk of volume sprawl, modeling ambiguity, or rights ambiguity. citeturn6view0turn30search2turn36view0turn14view6turn35search9turn20search2

## GEO and AI visibility

### GEO / AI Visibility Support

DataForSEO has **real, documented support** for Google AI Overviews. In Google Organic SERP responses, AI Overviews appear automatically when detected, under a dedicated `ai_overview` item in the `items` array. Official help content says the returned data can include AI-generated text, images, cited-source name/domain/URL/title/text, videos, and AI-generated tables with source references. That is excellent Observatory material because it reads like a witnessed surface capture, not merely a feature-flag saying “AI Overview present.” citeturn31view0turn31view1

DataForSEO also has a **separate Google AI Mode SERP API**. Official docs and help content describe AI Mode as a standalone AI-powered search surface, not just a SERP feature, and say the API can retrieve summaries plus quoted-website references. Current reviewed docs also show a meaningful limitation: in the help article, AI Mode support was described as English-only at the time reviewed. That makes the feature useful, but scope-limited. citeturn15search7turn31view2turn24view0

For non-Google AI surfaces, DataForSEO now documents three distinct layers. First, **LLM Responses API** supports ChatGPT, Claude, Gemini, and Perplexity and can generate structured responses from those models. Second, **LLM Scraper** is documented for ChatGPT and Gemini search-mode result capture and can return structured answer elements, including text, tables, images, and in ChatGPT’s case, products, local businesses, fan-out queries, and brand mentions. Third, **LLM Mentions API** provides aggregated visibility and citation datasets, but the reviewed official docs show platform scope in the main search/top-domain docs as currently `google` or `chat_gpt`, with ChatGPT availability limited to U.S. English in the reviewed documentation. That means DataForSEO’s AI coverage is broad in marketing terms, but not uniform in evidence form or geography. citeturn32view3turn18search0turn31view4turn18search11turn32view0turn32view1

For Bing, DataForSEO documents Copilot-style AI summaries within Bing SERP output. Their help-center material says Bing Organic SERP API can return Copilot AI summaries, including generated text and sourced links, which makes Bing relevant to later GEO work even though it is not packaged as a standalone Copilot observation product in the same way AI Mode is for Google. citeturn25search1turn25search3turn25search5

The capability classification is below.

| Capability | Status | What it actually returns | Stability / caveat |
|---|---|---|---|
| Google AI Overviews via Google Organic SERP | **Available and documented** | `ai_overview` item, text, images, cited sources, tables, videos, related AI-overview elements in other SERP features | Strongest AI/GEO fit today citeturn31view0turn31view1 |
| Google AI Mode API | **Available and documented** | AI Mode summary plus referenced sites; device/location fields; separate surface | Useful, but language support in reviewed help was limited to English citeturn31view2turn24view0 |
| ChatGPT LLM Responses | **Available and documented** | structured model responses for selected ChatGPT models | More like synthetic run output than witnessed public search surface citeturn18search8turn32view3 |
| Claude / Gemini / Perplexity LLM Responses | **Available and documented** | structured generated responses; Perplexity live-only in reviewed docs | Useful for comparative experiments, not equivalent to SERP witness data citeturn18search1turn18search2turn18search3turn32view3 |
| ChatGPT / Gemini LLM Scraper | **Available and documented** | search-mode answer elements, sources, tables, images, fan-out queries, brand mentions; ChatGPT adds products/local businesses | Stronger evidence fit than plain LLM Responses for search-mode surfaces citeturn18search0turn31view4 |
| LLM Mentions | **Available but operationally unclear** | aggregated mentions, top domains/pages, full Q&A and sources in search endpoint; reviewed legacy/new-path coexistence | Real capability, but path migration and pricing clarity need confirmation citeturn18search11turn31view3turn32view0turn29view0 |
| Bing Copilot summaries | **Available but partly help-center documented** | AI summaries and quoted sources inside Bing organic results | Good later feature, weaker docs footprint than Google AI surfaces citeturn25search1turn25search3 |
| Gemini / ChatGPT citation tracking in LLM Mentions | **Available but narrower than marketing copy suggests** | reviewed docs show platform values `google` and `chat_gpt` for main mentions endpoints | Needs support confirmation for current platform breadth and rollout status citeturn32view0turn32view1 |
| Customer-grade “AI visibility score” truth metric | **Not a direct observation** | AI search volume and mention metrics are modeled / aggregated | Safe only as provider-attributed estimates citeturn32view2turn18search11 |

## Pricing and commercial model

### Pricing and Cost Model

DataForSEO uses a pay-as-you-go model. The general pricing page states a **$50 minimum payment amount**, and the free-trial help article says new accounts receive **$1 in credit** for testing. API families bill in different ways: per SERP page, per task, per row, per result, or mixed task-plus-row models. Live mode is generally faster and pricier; standard queue is cheaper and retrievable later by task ID for a limited time. citeturn12view2turn12view0turn12view1turn13view0

The ugly part is recent pricing drift. On July 1, 2026, DataForSEO announced a broad pricing update touching eight APIs and explicitly said the **$100 monthly commitments for Backlinks API and LLM Mentions API were removed**. However, an older official help-center article still describes the old Backlinks subscription requirement. So the current pricing policy is the update notice plus current pricing pages, not old help content. This is exactly the kind of thing that can wreck Observatory budgeting if taken on faith. citeturn29view0turn29view1

For SERP API, current Google Organic pricing is simple at the base layer: standard queue is **$0.0006** per SERP of 10 results, priority queue is **$0.0012**, and live is **$0.002**. Additional parameters can multiply cost. Official help says depth above the default introduces extra cost, and other modifiers such as certain advanced operators or `calculate_rectangles` can also increase cost. Google Local Finder and Google Maps reviewed pages used the same base price. Google AI Mode is pricier: **$0.0012 / $0.0024 / $0.004** per page for standard / priority / live. citeturn12view1turn11search4turn30search0turn30search2turn24view0

For keyword metrics, Google Ads Search Volume is unusually economical because billing is per task, not per keyword, up to task limits. The reviewed pricing page states **$0.06** standard or **$0.09** live for a task with up to 1,000 keywords. That means 100-keyword and 1,000-keyword batches can cost the same if they fit in one task. Labs pricing is typically **$0.012 plus $0.00012 per item**, though historical SERPs are billed at **$0.00012 per SERP** and some clickstream-enhanced outputs can effectively double cost. citeturn14view6turn13view6turn14view7turn11search14

Backlinks and Content Analysis follow mixed request-plus-row pricing. Reviewed current pricing showed Backlinks at **$0.024 per request plus $0.000036 per row**, and Content Analysis at the same pattern. OnPage starts at **$0.00015 per crawled page** in Basic mode, then multiplies sharply if you load resources, JavaScript, or full rendering. Merchant Google Shopping is **$0.001** standard or **$0.002** priority per product/seller/SERP, with reviews billed per 10. Business Data varies by source, such as Google My Business business info at **$0.0015** standard per profile. citeturn13view0turn34search1turn14view5turn30search1turn14view1turn14view3

### Appendix B

The cost examples below are based on the reviewed current official pricing inputs and simple arithmetic. Where DataForSEO uses task-plus-row billing, I show formulas rather than pretending precision I do not have. If you use non-default depth, screenshot capture, `calculate_rectangles`, or advanced search operators, expected cost goes up. citeturn12view1turn11search4turn30search1turn13view0

| Example pull | Pricing input | Example cost | Notes |
|---|---|---:|---|
| 1 keyword Google organic SERP snapshot | 1 SERP of 10 results | $0.0006 standard / $0.002 live | AI Overview included if present in organic SERP output; no separate AI Overview fee found citeturn12view1turn31view0 |
| 100 keyword Google organic SERP snapshots | 100 SERPs | $0.06 standard / $0.20 live | assumes 1 page per keyword, default depth citeturn12view1 |
| 1,000 keyword Google organic SERP snapshots | 1,000 SERPs | $0.60 standard / $2.00 live | same assumption citeturn12view1 |
| Keyword volume batch for 100 keywords | Google Ads Search Volume task | $0.06 standard / $0.09 live | same cost as a 1,000-keyword task if it fits one task citeturn14view6 |
| Keyword volume batch for 1,000 keywords | Google Ads Search Volume task | $0.06 standard / $0.09 live | per official page, up to 1,000 keywords per task citeturn14view6turn21search16 |
| Competitor domain overview | Labs Domain Rank Overview assumption: $0.012 + $0.00012 × 1 item | about $0.01212 | assumption: one returned item; confirm exact row count behavior per endpoint citeturn13view6turn35search9 |
| Backlink pull for one domain summary | Backlinks request-plus-row pricing | about $0.024036 if summary returns one row | exact billing for summary-style single-row responses should be confirmed citeturn13view0turn20search2 |
| Google AI Overview visibility pull | Google Organic SERP live page | $0.002 live | only if overview is present; you still pay for the SERP request either way citeturn12view1turn31view0 |
| Google AI Mode pull | Google AI Mode SERP | $0.0012 standard / $0.004 live | separate surface from normal SERP citeturn24view0turn31view2 |
| Local SERP snapshot | Google Local Finder or Maps page | $0.0006 standard / $0.002 live | reviewed pricing matches base Google SERP costs citeturn30search0turn30search2 |
| Shopping / merchant result snapshot | Google Shopping product-seller-SERP | $0.001 standard / $0.002 priority | product/review depth rounding rules apply citeturn30search1 |

Unclear items that should **not** be hardcoded yet: whether empty but valid zero-result responses are billed differently; whether all failed tasks are non-billable; the exact current pricing line for LLM Mentions in the wake of the July 1 pricing change; and whether old help-center pricing articles were fully updated. Those are support-ticket questions, not assumptions. citeturn29view0turn29view1turn20search3

## Rights, retention, and provenance

### Rights, Storage, and Retention

This is the report’s weakest area, and that weakness matters. I found **operational evidence** that DataForSEO expects customers to store some results on their side. Their help center says Live-mode results are not retained by DataForSEO and recommends saving them yourself if you need them later. A separate help article says Keyword Data API results can be stored in your own database for filtering on your side. That is meaningful evidence that internal storage is contemplated. citeturn19view0turn10search2

But that is **not the same thing** as an explicit contractual grant for indefinite archival, redistribution, public display, or customer-facing republication of raw source payloads. In the reviewed Terms of Service, the only clearly relevant use restriction I found was Section 7.1, which says SERP data obtained through the service must not be used to compete with or adversely affect the business interests of the originating search-engine providers. I did **not** find a reviewed official clause that cleanly says, “You may archive all raw JSON indefinitely,” or, “You may freely show raw SERP captures in customer reports,” or, “Redistribution is broadly licensed.” That is why rights remain unresolved. citeturn9view4

Retention mechanics are clearer than rights. Standard queue task results are generally retrievable for **30 days** by task ID. Live-mode results are **not stored** by DataForSEO. Standard SERP HTML results are kept for **7 days**, and page-screenshot artifacts have an even narrower access window: the screenshot endpoint can be called within 7 days of task creation, but once you fetch a screenshot URL from DataForSEO storage, the URL remains available for only **one day**. DataForSEO specifically recommends saving those images on your own storage the same day. That creates a very obvious Observatory implication: if you want durable provenance, you must decide your own retention policy, because the vendor will not do it for you. citeturn19view0turn7search11

### Appendix C

This table separates what is **explicitly supported by the reviewed materials** from what appears merely **tolerated operationally** and what remains **unclear**.

| Data type | Can store raw? | Can store normalized? | Can show in report? | Retention limit from DataForSEO side | Redistribution limit | Confidence | Notes / evidence |
|---|---|---|---|---|---|---|---|
| SERP organic results | **Internal storage appears contemplated; legal grant unclear** | Same | **Unclear** | 30 days for standard task result retrieval; live not retained | SERP use restricted against competing with search engines; broader redistribution not clearly granted | Low-Med | Live results should be stored on your side if needed later; ToS has SERP-use restriction citeturn19view0turn9view4 |
| SERP features | Same as above | Same | **Unclear** | Same as SERP | Same as SERP | Low-Med | Includes AI Overview if returned inside SERP citeturn31view0turn19view0turn9view4 |
| AI Overview / AI answer data from SERP | **Likely yes internally** | Same | **Unclear** | Lives inside SERP retention mechanics | No explicit grant found | Low | Operationally part of SERP payload, but no explicit rights language found citeturn31view0turn19view0turn9view4 |
| SERP HTML | Technically yes if fetched; legal/display rights unclear | N/A | **Unclear** | 7 days on vendor side | No explicit grant found | Low | HTML retrieval window documented; export/display rights not found citeturn19view0turn35search15 |
| Screenshots / rendered captures | Technically yes; vendor recommends saving same day | N/A | **Unclear** | URL accessible one day after fetch; screenshot callable within 7 days | No explicit grant found | Low | Strong operational evidence, weak legal clarity citeturn19view0turn12view1 |
| Keyword volume / CPC / competition | Internal storage appears contemplated | Yes | **Probably operationally yes, legally still not explicit** | depends on task mode | No explicit grant found | Med | Keyword Data article explicitly says you can store in your own DB; rights language still sparse citeturn10search2turn19view0 |
| Keyword difficulty / search intent / other Labs metrics | **Likely yes internally** | Yes | **Unclear** | live only for many Labs calls, so vendor won’t retain | No explicit grant found | Low-Med | Treat as provider estimates, not facts citeturn19view0turn33search10 |
| Backlink data | **Likely yes internally** | Yes | **Unclear** | live not retained | No explicit grant found | Low-Med | Operational storage implied for live-only APIs; subscription terms changed recently citeturn19view0turn29view0 |
| Domain analytics | **Likely yes internally** | Yes | **Unclear** | depends on endpoint/mode | No explicit grant found | Low | No reviewed clause found on customer-facing republication citeturn35search0turn19view0 |
| Merchant / shopping results | **Likely yes internally** | Yes | **Unclear** | queue retrieval limits apply | No explicit grant found | Low | Rights likely source-sensitive because marketplace data is third-party in origin citeturn30search1turn19view0 |
| Local / business profile data | **Likely yes internally** | Yes | **Unclear** | queue retrieval limits apply | No explicit grant found | Low | Public-business data, but legal display rights still not expressly documented in reviewed pages citeturn6view7turn19view0 |
| OnPage crawl data / page HTML | Technically yes | Yes | **Unclear** | many live-only outputs not retained | No explicit grant found | Low | Especially sensitive if crawling pages you do not control citeturn19view0turn7search1 |
| Content Analysis citations / sentiment | **Likely yes internally** | Yes | **Unclear** | live-only API patterns mean self-storage needed | No explicit grant found | Low | Sentiment is modeled and rights for downstream display were not explicitly found citeturn34search0turn19view0 |

Bottom line: **Internal storage for operational use looks contemplated. Broad archival, redistribution, and customer-facing display rights remain unclear and should be confirmed directly with DataForSEO support or counsel before raw-payload storage policy is finalized.** citeturn19view0turn9view4turn10search2

### Raw Payload and Provenance Fit

On provenance, DataForSEO scores much better than on rights. Official docs show stable task IDs, task-level status codes and messages, execution time, task cost, `data` objects echoing request parameters, path metadata, result counts, and retrievability by task ID for standard queue results. There is also an Errors endpoint with internal status codes and explicit advice to store error-code context in your application log. That is all very Observatory-friendly. citeturn7search11turn20search13turn20search4turn20search3

The platform also carries useful contextual metadata. SERP and AI docs show support for query/keyword, location, language, device, OS, and other request parameters inside or alongside responses. Some endpoint families add more concrete timestamps, such as backlink `first_seen`, `lost_date`, or content-analysis `fetch_time`. For standard SERP, DataForSEO explicitly says the observation is captured when the task is set, not when you later retrieve the result, which is exactly the kind of provenance nuance the Observatory should preserve in storage. citeturn31view2turn20search18turn21search7turn19view0

What is weaker is the presence of a single universal “observed_at” field across every endpoint family in the reviewed materials. Some results clearly contain natural timestamps; others mainly expose task timing and freshness/update metadata. So the correct answer is not “perfect auditability.” It is “strong auditability if you persist both the raw vendor payload and your own ingestion timestamp, and keep the provider task ID plus request context.” citeturn20search13turn19view0turn21search15

| Need | DataForSEO support | Notes | Source |
|---|---|---|---|
| Stable provider request / task ID | **Yes** | UUID-style task IDs documented and reusable for standard retrieval windows | citeturn7search11turn19view0 |
| Capture timestamp | **Partial** | task timing exists; some endpoints expose `first_seen`, `fetch_time`, update times; not one universal observed-at field found in reviewed docs | citeturn20search18turn21search7turn19view0 |
| Search engine / location / language / device metadata | **Yes** | documented across SERP and AI Mode requests/responses | citeturn6view0turn31view2 |
| Query or target | **Yes** | request echoed in `data` object or target fields | citeturn20search13turn32view0 |
| Raw payload | **Yes** | JSON responses; SERP HTML endpoints also available in many SERP families | citeturn10search6turn35search15 |
| Provider cost metadata | **Yes** | task and response `cost` fields documented | citeturn20search13turn20search4 |
| Status / error metadata | **Yes** | internal status codes and Errors endpoint documented | citeturn20search3turn11search11 |
| Result freshness metadata | **Partial** | some endpoints expose update cadence or updated times; standard SERP freshness tied to task-set time | citeturn19view0turn18search10turn21search15 |
| Pagination / depth metadata | **Yes** | `depth` and result-count/paging behaviors documented | citeturn11search2turn20search13 |
| Ability to re-fetch task result | **Yes for standard; no for live** | standard results retrievable for 30 days; live results must be stored by client | citeturn19view0 |
| Auditability | **Good, not perfect** | strong task metadata, but client should add its own ingest timestamp and request fingerprint | citeturn20search13turn19view0 |

## Freshness, truth risk, and operational assessment

### Freshness and Historical Availability

Freshness depends completely on endpoint family. SERP API is a live or queued snapshot system: the observation happens when the task is set, and queued GET retrieval later does **not** make it fresh again. Backlinks API is based on a live index that DataForSEO says is crawled continuously. Keyword Data sourced from Google Ads usually updates in the middle of each month and represents source-lagged monthly metrics rather than immediate search behavior. Labs is a database layer updated continuously in aggregate, but some specific historical/rank endpoints are weekly. Content Analysis trend history is available back to October 31, 2022. Backlinks history goes back to January 1, 2019. Labs historical search volume goes back to the start of 2019; historical rank overview goes back to October 1, 2020. citeturn19view0turn21search3turn21search0turn21search2turn18search10turn34search5turn20search6turn15search9

| Endpoint family | Freshness model | Update cadence | Historical availability | Staleness caveat |
|---|---|---|---|---|
| SERP API | live / queued snapshot | immediate at task-set time | standard results retrievable 30 days; HTML 7 days | later GET is stale snapshot, not fresh pull citeturn19view0turn12view1 |
| Google AI Overview in SERP | same as SERP | same as SERP | same as SERP | only observed when triggered on SERP at capture time citeturn31view0turn19view0 |
| Google AI Mode | live / queued page capture | immediate at task-set time | queue/live rules per family | evolving product surface; language/device constraints apply citeturn31view2turn24view0 |
| Keywords Data Google Ads | source-lagged monthly metrics | usually mid-month source update | monthly trend windows; not true real-time demand | latest month can lag if source has not updated yet citeturn21search0turn21search12 |
| DataForSEO Labs keyword metrics | database-based | updated continuously overall; keyword metrics monthly after source update | historical search volume since 2019 | database freshness varies from live-snapshot expectations citeturn21search2turn33search2 |
| Labs domain-rank / competitor history | database / weekly on reviewed endpoints | weekly for reviewed historical rank endpoints | historical rank from 2020-10-01 | treat as periodic database state, not direct live crawl | citeturn18search10turn35search19 |
| Backlinks API | live index | continuous crawling | history since 2019 for history endpoint | vendor index coverage and spam filtering affect counts citeturn21search3turn20search6turn8search8 |
| Business Listings databases | database-based | 90–180 day cycles by geography, some categories yearly | yes in database form | too stale for snapshot-grade local observations | citeturn22view0 |
| Content Analysis | live search plus historical trend endpoints | live request + stored dataset | phrase/category trends since 2022-10-31 | citation dataset freshness not equivalent to real-time web crawl guarantee | citeturn34search5turn34search8 |

Observatory implication: every stored evidence unit should carry a **freshness model label** such as `live_snapshot`, `queued_snapshot`, `monthly_source_metric`, `continuously_updated_database_metric`, or `historical_database_metric`. Without that, your read-time LLM will lie by accident. citeturn19view0turn21search0turn21search2turn21search3

### Provider-Truth Risk

This is where the Observatory either stays honest or turns into astrology software.

| Metric / field | Category | Safe wording | Unsafe wording | Notes |
|---|---|---|---|---|
| SERP URL / title / snippet / rank position | Direct observation | “DataForSEO returned URL X at rank Y for query Q under context C on date Z.” | “This page is truly rank Y everywhere.” | Still subject to location/device/personalization caveats citeturn35search15turn6view0 |
| AI Overview presence and cited URLs | Direct observation of a surfaced feature | “DataForSEO observed an AI Overview with cited source D for query Q.” | “Google always cites D for Q.” | Surface behavior is volatile across time and context citeturn31view0 |
| Google Ads search volume | Third-party metric / estimate | “DataForSEO returned Google Ads search-volume metric X.” | “This keyword gets exactly X searches.” | Monthly, source-lagged, estimate-like citeturn8search12turn21search0 |
| CPC / competition | Third-party ad-platform metrics | “DataForSEO returned CPC/competition metric X from its keyword data source.” | “CPC is exactly X in market reality.” | Ad-platform-derived, not transactional truth citeturn8search16turn33search2 |
| Keyword difficulty | Proprietary estimate | “DataForSEO’s keyword-difficulty metric for K was X.” | “Ranking for K has X% real-world difficulty.” | Logarithmic proprietary score citeturn33search10 |
| Clickstream ETV / clickstream search volume | Proprietary estimate | “DataForSEO returned clickstream-based estimate X.” | “The keyword will drive exactly X visits.” | Explicitly clickstream-based modeled metric citeturn8search15turn11search14 |
| Backlink row / first_seen / lost_date | Direct observation within provider index | “DataForSEO’s index recorded backlink B first seen at T.” | “The web’s complete backlink reality is B at T.” | Index-based observation, not universal ground truth citeturn20search18turn21search3 |
| Backlink counts | Provider-normalized observation | “DataForSEO reported N backlinks in its live index.” | “The domain has exactly N backlinks.” | Coverage and spam filtering matter citeturn21search3turn8search8 |
| Backlinks Rank / domain rank / spam score | Proprietary metric | “DataForSEO Rank / spam score was X.” | “Authority is X.” | Explicitly analogous to DR-style abstraction, not fact | citeturn28search12turn21search7 |
| AI search volume | Proprietary estimate | “DataForSEO returned AI search-volume estimate X.” | “Users make exactly X AI searches.” | Official help says it is not actual logs and should be treated directionally | citeturn32view2turn33search0 |
| LLM mentions / impressions | Provider-aggregated dataset output | “DataForSEO’s LLM mentions dataset reported X mentions / impressions.” | “The model ecosystem truly mentions us X times.” | Depends on platform coverage, filters, and dataset scope citeturn18search11turn31view3 |

### Appendix D

The safe language pattern for The Observatory is simple: **attribute every non-literal fact to the provider, preserve the capture context, and separate observation from interpretation.** The unsafe pattern is to convert a provider field into a universal truth claim. citeturn32view2turn28search12turn8search12

### Operational Risks

| Risk | Severity | Likelihood | Mitigation | Notes |
|---|---|---|---|---|
| Rights ambiguity for raw storage and customer-facing display | High | High | get written confirmation by endpoint family before raw archival or report display | strongest blocker found citeturn9view4turn19view0turn10search2 |
| Pricing surprises from stale docs / recent changes | High | Medium-High | use current pricing pages + July 1 update notice; verify with support before M1 budgets | old and new official pages conflict citeturn29view0turn29view1 |
| Endpoint overlap and confusion | Med-High | High | start with a very short approved endpoint list | SERP vs Labs vs Keyword Data often answer similar questions differently citeturn33search11turn6view3 |
| Over-trusting proprietary metrics | High | High | store provider attribution and metric category; ban truthy language in downstream prompts | core epistemic hazard citeturn32view2turn28search12turn33search10 |
| Raw-payload volume explosion | High | Medium | cap depth, rows, and crawl size; compress and hash raw payloads; store selectively | OnPage, Backlinks, Content Analysis can balloon fast citeturn14view5turn13view0turn34search1 |
| Localization/device volatility | Medium | High | treat location/language/device/OS as required provenance fields | DataForSEO supports granular targeting precisely because results vary | citeturn6view0turn31view2 |
| Live vs database freshness confusion | High | High | add freshness-model label to every evidence unit | snapshot and database metrics are not interchangeable citeturn19view0turn21search0turn21search2 |
| Rate-limit / concurrency errors | Medium | Medium | honor 2,000 rpm general limit and 30 simultaneous-request cap on database-backed APIs | very manageable for selective Observatory pulls | citeturn23view0 |
| Duplicate-task billing / operator mistakes | Medium | Medium | dedupe request fingerprints before pull | repeated identical tasks are explicitly called out as user-side errors | citeturn9view4turn11search13 |
| AI/GEO platform volatility | High | High | prefer raw observed AI outputs over aggregate “AI visibility” metrics in v1 | fast-changing products, path migrations, restricted platform coverage | citeturn32view0turn32view1turn31view2 |

## Observatory recommendation

### Recommended Observatory Use

Best first endpoints:

Use **Google Organic SERP Advanced** as the primary telescope for classic search visibility, because it yields direct observed results, rich request context, and AI Overview data when present. Add **Google Local Finder or Maps** if local observation matters, and **Google Shopping API** if ecommerce surfaces matter. Add **Google Ads Search Volume** for low-cost keyword metrics, but tag every returned value as source-lagged provider evidence, not present-tense truth. Use **DataForSEO Labs** only for a narrow set of historical or domain-overview endpoints where the database nature is explicitly useful, such as Domain Rank Overview, Ranked Keywords, and Historical SERPs. Add **Backlinks Summary** and then selective backlink extracts only after you have row caps and storage rules. citeturn6view0turn30search2turn36view0turn14view6turn35search9turn20search2

Endpoints to avoid for now:

Avoid broad **OnPage** crawling in the first provider pilot. It is easy to turn a clean observatory into a data landfill with crawl payloads, HTML, JS-rendered variants, screenshots, and multi-page audits. Avoid **Content Analysis** in v1 unless your mission already includes off-SERP citation monitoring. Avoid **LLM Responses** as a first AI/GEO layer for Observatory evidence because those calls generate model outputs on demand and blur the line between public-surface observation and synthetic prompting. Avoid **LLM Mentions** until pricing, coverage, and rights questions are answered in writing. citeturn14view5turn34search0turn32view3turn29view0

Minimum metadata to store for every approved pull:

Store provider name, endpoint family, exact endpoint path, provider task ID, your own request fingerprint, raw request context, location, language, device, OS where relevant, task mode, priority, cost, status code/message, result count, vendor freshness/update metadata if supplied, your ingest timestamp, and the raw payload hash. If you persist raw payloads, store them as evidence blobs, not as first-class truth tables. The database should record **what DataForSEO returned**, **when**, **for what context**, and **what it cost**. Interpretation belongs later. citeturn20search13turn20search4turn19view0turn20search3

Raw payload handling recommendation:

Internally, retain raw JSON for approved endpoint families because it is the only reliable way to preserve provenance-complete evidence and reproduce later interpretation. But do **not** default to storing raw HTML, screenshots, or giant row-heavy payloads indefinitely until rights are clarified. Start with JSON payloads for selected families, strict row/depth caps, and short default retention for bulky artifacts. If DataForSEO gives written permission later, expand carefully by endpoint. citeturn19view0turn10search2turn9view4

Rights / retention cautions:

Do not assume that “DataForSEO says store it on your side” equals “you may archive and redistribute it however you want.” It does not. Until clarified, keep the pilot **internal-only**, avoid customer-facing raw SERP screenshots/HTML, and keep downstream presentation at the normalized observation layer with clear provider attribution. citeturn19view0turn9view4

Cost controls:

Use standard queue wherever freshness requirements permit. Use one-task “keyword volume batches” to exploit Google Ads per-task pricing. Keep SERP depth at the base level unless you have a ranking-specific reason to go deeper. Avoid `calculate_rectangles`, screenshots, and render-heavy OnPage settings in the initial phase. Add request deduplication before sending tasks. citeturn12view1turn14view6turn11search4turn14view5turn11search13

### Questions for DataForSEO Support

The following questions must be answered **before** schema/provider work goes further:

Can customers archive raw JSON payloads indefinitely for all endpoint families, or only for internal operational use? Is this allowed for SERP, AI Overview, AI Mode, LLM Mentions, LLM Scraper, Backlinks, Merchant, Business Data, and Content Analysis separately? citeturn19view0turn9view4

Is customer-facing display of normalized output allowed? Is customer-facing display of raw output allowed? Please answer separately for raw SERP HTML, page screenshots, AI Overview text/citations, Google Business outputs, Google Shopping outputs, and review data. The reviewed official materials do not answer this cleanly. citeturn9view4turn19view0

What is the current, endpoint-level pricing for **LLM Mentions** after the July 1, 2026 pricing update? Which existing official help-center pages are stale and should be ignored? citeturn29view0turn29view1

Are empty-but-successful responses billed the same as non-empty responses for queue and live modes? Are validation failures or upstream provider failures ever billable? The reviewed materials did not answer this precisely. citeturn20search3turn11search10

For each AI product, what is the current platform, geography, and language coverage in production: Google AI Overview, Google AI Mode, ChatGPT search, Gemini search, Bing Copilot, Perplexity, and LLM Mentions datasets? Reviewed docs show uneven support and some legacy/new-path coexistence. citeturn32view0turn32view1turn32view3turn31view2

Does DataForSEO have any endpoint-specific license differences because some results originate from search engines, app stores, shopping marketplaces, review platforms, or registrars? That distinction is implied by product families, but not spelled out in the reviewed legal text. citeturn9view4turn6view7turn36view0turn36view1

### Decision Inputs for Observatory Roadmap

The good news: DataForSEO is credibly capable, cheap enough for selective evidence pulls, provenance-rich enough for a serious observatory, and broad enough that one vendor can cover classic search, local, shopping, backlinks, and a meaningful chunk of AI visibility. The bad news: rights and pricing hygiene are not clean enough yet to let this provider silently shape your schema or storage plan. citeturn10search10turn12view2turn19view0turn29view0

If you proceed, proceed narrowly. The correct first move is not “integrate all the APIs.” It is “treat DataForSEO as a witness for a tiny approved set of evidence units, under internal-only rights assumptions, with explicit freshness and metric-type tagging.” That preserves Observatory doctrine and prevents the database from turning into a creepy little pundit. citeturn6view0turn14view6turn35search9turn20search2

### Decision-ready summary

**Recommended status:** **promising but blocked by rights/pricing questions**

**Can Observatory safely use DataForSEO?**  
Yes, **for a controlled internal pilot** using a narrow endpoint set and strict provenance capture. No, **not yet for broad raw-payload retention or customer-facing use** without written clarification on rights and current pricing. citeturn19view0turn9view4turn29view0

**Which endpoints are most relevant?**  
Google Organic SERP Advanced, Google Local Finder or Maps, Google Shopping, Google Ads Search Volume, selected DataForSEO Labs visibility/history endpoints, and Backlinks Summary / capped backlink extracts. citeturn6view0turn30search2turn36view0turn14view6turn35search9turn20search2

**What can be stored?**  
High-confidence answer: internal normalized observations plus full provenance metadata. Medium-confidence answer: internal raw JSON for approved pilot endpoints appears operationally contemplated. Low-confidence answer: long-term archival of all raw payloads and customer-facing raw display rights remain unclear. citeturn19view0turn10search2turn9view4

**What should not be stored?**  
Not yet: broad raw HTML archives, screenshot libraries, giant row-heavy payloads, or customer-facing reproductions of third-party surfaces before rights are clarified. Also do not store strategy conclusions or provider metrics as facts. citeturn19view0turn9view4turn32view2turn28search12

**What does one useful evidence unit cost?**  
At the low end, a Google SERP page is fractions of a cent; a Google Ads keyword-volume task covering up to 1,000 keywords is a few cents; a Labs single-item domain overview is roughly one cent; a backlink request starts around two cents plus row charges. In other words: cheap enough for evidence sampling, expensive enough to punish sloppy pulling. citeturn12view1turn14view6turn13view6turn13view0

**What must be researched further before schema/provider work?**  
Rights, redistribution permissions, raw-archive permissions, customer-facing display rights, current LLM Mentions pricing, billing behavior on empty/error cases, and endpoint-by-endpoint source-license differences. citeturn9view4turn29view0turn20search3

**Must know before schema**  
Written answers on raw storage rights; endpoint-level freshness classes; which metrics are modeled vs observed; which AI endpoints are truly production-stable. citeturn19view0turn32view2turn32view3

**Must know before first paid pull**  
Current official pricing for approved endpoints after July 1, 2026; depth/parameter multipliers; live-vs-standard rules; duplicate-task protections. citeturn29view0turn12view1turn11search4turn11search13

**Must know before storing raw payloads**  
Whether raw JSON archival is permitted indefinitely; whether HTML/screenshot storage is permitted; whether customer-facing export is restricted by source family. citeturn19view0turn9view4

**Must know before customer-facing use**  
Display and redistribution rights for raw and normalized outputs by endpoint family, especially SERP, AI Overview, AI Mode, Shopping, Google Business, and reviews. citeturn9view4turn6view7turn36view0

**Must know before M1 roadmap sequencing**  
Whether AI visibility in M1 should mean only observed Google AI Overviews and AI Mode, or whether LLM Mentions and LLM Scraper are mature and licensed enough to include. Right now, the conservative answer is “observed Google AI surfaces first, broader LLM products later.” citeturn31view0turn31view2turn32view0turn32view3

**Open questions and limitations**  
The reviewed official materials were strongest on capability and weakest on legal permission. Some official pricing/help content is currently inconsistent because of the July 1, 2026 update. Where that happened, I treated the newer update notice and current pricing pages as higher-confidence than older help-center articles. Rights questions remain unresolved and should be treated as blocking, not as footnotes. citeturn29view0turn29view1turn9view4