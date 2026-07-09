# Google Search Console and Bing Webmaster Boundary Research Report for The Observatory

## Executive Summary

Google Search Console and Bing Webmaster Tools are strong first-party witnesses for verified properties, but neither is universal truth, and neither should be treated as raw fact without provider caveats. Google explicitly documents privacy filtering, row limits, aggregation differences, canonicalization effects, preliminary data, and report-specific omissions. Bing explicitly documents that key traffic APIs are updated weekly, the search-performance UI covers up to six months, and several features are ownership-gated and quota-gated, but Microsoft’s current official documentation is materially thinner and in places older or less crawlable than Google’s. citeturn10view0turn10view1turn33view0turn35search14turn24search0turn19view2turn22search28turn20search1

For The Observatory’s current doctrine, customer GSC/Bing data should be treated as customer first-party private telemetry and excluded from Observatory storage now. That conclusion is not because the data is bad; it is because the data is ownership-gated, user-authorized, and inherently tied to a private verified property’s search performance. Google’s API access is gated by OAuth 2.0 and Search Console permissions; Bing’s API access is gated by OAuth 2.0 or API key access tied to verified sites. Google additionally states that Google API Services User Data Policy governs use of Google user data requested via Google APIs. Microsoft states Bing Webmaster API use is governed by the Microsoft Services Agreement, and Microsoft’s Privacy Statement covers personal data processing and disclosure. citeturn14search5turn5search17turn14search0turn14search1turn20search1turn20search0turn19view0turn25search0turn25search1

The clean boundary for now is simple and boring, which is exactly what you want before a data boundary accident turns into a legal piñata. Publicly observable external data and provider-estimated third-party data can live in The Observatory. Customer GSC/Bing data should not. If first-party webmaster data is ever used later, the safest near-term pattern is read-time overlay from the customer layer, not storage inside Observatory. Owner-internal properties are a separate case: they may be possible later under explicit owner ruling, internal-only scope, strict provenance, and deletion/retention rules, but they should still not be assumed safe by default. That is an inference from the access models, user-data policies, and the doctrine you supplied, not an official Google/Microsoft rule. citeturn14search0turn14search1turn20search1turn19view0turn25search1

The practical product conclusion is therefore:

| Recommended status | Conclusion |
|---|---|
| Customer GSC/Bing exports | **Excluded from Observatory storage now** |
| Customer GSC/Bing at read time | **Allowed only as future read-time overlay, if separately governed** |
| Owner-internal verified properties | **Possible later only with explicit owner ruling and internal-only boundary controls** |
| Public SERP / crawl / provider-estimated external data | **Suitable for Observatory** |
| Claim generation from GSC/Bing | **Allowed only with provider-attributed, caveated wording** |

This conclusion aligns with the Observatory doctrine that the database stores observations, not conclusions; the LLM interprets at read time; and accepted conclusions promote outward later. GSC/Bing are therefore witnesses, not judges, and certainly not database wallpaper paste. citeturn10view0turn9view1turn19view0turn24search0

## Confidence and Source Quality

This report is based primarily on current official Google and Microsoft sources accessed on **July 8, 2026**. Google’s documentation quality is materially stronger, more current, and more explicit than Bing’s for this topic. Google has recent official docs for Search Console reports, API surface, BigQuery bulk export, privacy filtering, dimensions, URL Inspection fields, and API auth/terms. Microsoft has official API and help content, but several Bing Webmaster help pages are JavaScript-only in the crawler environment, so some Bing UI facts rely on official search-result snippets rather than fully opened text pages. That lowers confidence on some Bing UI details, especially retention specifics and UI-only feature behavior. citeturn26view0turn32view0turn13view0turn13view1turn19view0turn20search1turn24search0turn22search28

Confidence is **high** for these Google statements: API-accessible services; performance metrics and dimensions; privacy filtering; UI/API/export row limits; 16-month performance history; BigQuery bulk export behavior; URL Inspection API behavior; and the fact that some report families are UI-only. citeturn26view0turn27view3turn10view1turn13view0turn13view1turn7search0turn32view0

Confidence is **moderate** for these Bing statements: ownership verification requirement; API auth options; the existence of search performance, backlinks, URL inspection, site scan, keyword research, Clarity integration, AI Performance, and IndexNow/URL submission features; weekly update cadence for major traffic APIs; daily crawl-stats updates; six-month UI windows for search performance and keyword research; and twice-monthly SEO Reports cadence. Those are all officially surfaced, but Bing’s documentation is more fragmented and some evidence arrives as search-result snippets rather than fully openable docs. citeturn21search0turn20search1turn20search0turn16search3turn16search13turn16search12turn24search10turn21search9turn16search8turn22search3turn22search26turn24search0turn22search28

Confidence is **lower** for any claim that Bing publishes a comprehensive retention policy for Webmaster performance data, a broad API quota table for all endpoints, or a fully current mapping of every UI feature to API/export behavior. On those points, the official public docs reviewed here are incomplete. Where the docs were incomplete, this report says so instead of pretending the gap is a feature. citeturn19view0turn20search1turn24search0turn22search28

## Source List

The following are the main sources used in this report. All were accessed on **July 8, 2026**.

Official Google sources:

- Google Search Console API Reference. citeturn26view0
- Search Analytics query method. citeturn27view3
- URL Inspection API method and `UrlInspectionResult` reference. citeturn7search0turn32view0
- Search Console Help: Reports at a glance. citeturn4view2turn6view0turn6view3turn6view5
- Search Console Help: Performance report, dimensions and data groupings. citeturn33view0
- Google Search Central Blog: deep dive into performance data filtering and limits. citeturn9view0turn10view1turn10view4
- Search Console Help: What are impressions, position, and clicks? citeturn9view1
- Search Console Help: bulk data export docs. citeturn13view0turn13view1turn13view2
- Search Console Help: Core Web Vitals, Page indexing, URL Inspection, Links. citeturn28view0turn28view1turn28view2turn28view3
- Search Console Help and blog entries on preliminary / hourly / recent data. citeturn35search1turn35search2turn35search6turn35search14turn35search20
- Google API auth, OAuth scopes, Google API Services User Data Policy, Google APIs Terms. citeturn14search5turn14search2turn14search0turn14search1

Official Microsoft/Bing sources:

- Bing Webmaster API overview and interface reference. citeturn19view0turn19view1
- Bing Webmaster API access and OAuth docs. citeturn20search1turn20search0
- Bing Webmaster verification docs and official help snippets. citeturn19view4turn21search0turn24search15
- Bing Webmaster help snippets for Search Performance, Backlinks, URL Inspection, Site Scan, Keyword Research, Sitemaps, Clarity, AI Performance, URL Submission, and refreshed Webmaster Tools. citeturn22search0turn16search3turn16search13turn16search12turn16search16turn16search7turn21search9turn16search8turn21search6turn24search2
- Bing Webmaster API method docs for query stats, crawl stats, URL submission quota/batch size. citeturn19view2turn22search26turn18search12turn18search6turn18search16
- Microsoft Services Agreement, Microsoft Privacy Statement, Microsoft APIs Terms of Use. citeturn25search0turn25search1turn25search3

Third-party sources used only for comparison context:

- Ahrefs keyword-volume / estimate positioning. citeturn36search0turn36search6turn36search15
- Semrush position-tracking positioning. citeturn36search1turn36search4turn36search16
- DataForSEO keyword-volume positioning. citeturn36search2turn36search8turn36search17

## Platform Overview

Google Search Console is Google’s verified-property search-performance and indexing console. The API officially exposes only four service families: Search Analytics, Sitemaps, Sites, and URL Inspection. Search Console permissions are explicit enough that the API itself returns permission levels such as `siteOwner`, `siteFullUser`, `siteRestrictedUser`, and `siteUnverifiedUser`. Search Console bulk export to BigQuery is owner-gated. Google’s official docs also make clear that performance data is subject to privacy filtering, row limits, canonical aggregation behavior, and preliminary/fresh-data states. citeturn26view0turn5search17turn13view1turn10view0turn10view1turn33view0turn35search14

Bing Webmaster Tools is Microsoft’s verified-site webmaster platform. Microsoft’s API overview says it programmatically exposes information about registered sites such as rank and traffic stats, link details, keyword details, crawl stats, URL submission, and sitemap submission. Access can be obtained either through OAuth 2.0 or an API key generated in Bing Webmaster Tools. Current public official snippets also show that Bing Webmaster includes Search Performance, Backlinks, URL Inspection, Site Scan, Keyword Research, Clarity integration, AI Performance, URL Submission / IndexNow-related submission, and Sitemaps. citeturn19view0turn20search1turn20search0turn22search0turn16search3turn16search13turn16search12turn16search16turn21search9turn16search8turn21search6turn16search7

### Platform overview table

| Platform | Access requirement | Core data | API available | Export available | Main caveats |
|---|---|---|---|---|---|
| Google Search Console | Verified property plus granted user/owner permissions; API requires OAuth 2.0; two property forms are evidenced in official docs by `sc-domain:` and URL-prefix examples. citeturn14search5turn5search17turn13view2 | Search performance, indexing/page indexing, sitemaps, URL inspection, CWV, links, manual actions, security issues, rich-result/enhancement reports. citeturn6view4turn6view0turn6view1turn6view2turn6view3turn6view5turn28view0turn28view1turn28view3 | Yes, but only for Search Analytics, Sitemaps, Sites, and URL Inspection. citeturn26view0 | Yes: UI export, API, Looker Studio connector, and owner-only BigQuery bulk export. citeturn9view0turn13view0turn13view1 | Privacy-filtered anonymized queries, row limits, canonical aggregation, preliminary data, heuristics that can change, and many UI reports not in API. citeturn10view1turn10view4turn33view0turn35search14turn9view1 |
| Bing Webmaster Tools | Verified site plus authorized user; API access via OAuth 2.0 or API key. Official public snippets show ownership verification and XML/meta-tag methods. citeturn20search1turn20search0turn21search0turn19view4 | Search performance, backlinks, crawl stats, URL inspection, site scan/SEO reports, sitemaps, keyword research, Clarity, AI Performance, URL submission / IndexNow-related notification flows. citeturn22search0turn16search3turn16search13turn16search12turn16search7turn16search16turn21search9turn16search8turn21search6 | Yes, for rank/traffic, links, keyword details, crawl stats, URLs, sitemaps, site/user management, URL submission. citeturn19view0turn19view1 | Yes in UI for some reports; API exportability exists for many data classes, but Microsoft’s current official public docs are less explicit than Google’s on full export coverage. citeturn19view0turn19view1turn24search0 | Docs are thinner and older; many help pages are JS-only in crawlable view; weekly update cadence for core query/page traffic APIs; public retention/limit disclosures are incomplete. citeturn19view2turn24search0turn24search10turn22search28 |

### Official facts, third-party claims, and inferences

Official facts are strong enough to conclude that both platforms are first-party search-performance instruments for verified properties, not public observability platforms. That alone matters for The Observatory: the data is not public web evidence; it is private provider-returned owner telemetry. citeturn14search5turn5search17turn20search1turn21search0

Third-party claims were only needed for the comparison section later. They are useful for explaining how Ahrefs, Semrush, and DataForSEO position their own keyword-volume and rank-tracking products, but they do not override official Google or Microsoft documentation. citeturn36search0turn36search4turn36search17

Inference used in this report is limited and labeled. The most important inference is boundary-related: if access depends on property verification and owner authorization, then the resulting data should be treated as private verified-property telemetry, not as public Observatory storage by default. That inference is consistent with the docs and with your doctrine. citeturn14search5turn20search1turn21search0turn14search0turn25search1

## Google Search Console Data Inventory

Google’s official report inventory is broad, but the official API surface is narrow. The UI includes performance reports for Search, Discover, and Google News; Page indexing; URL Inspection; Sitemaps; Core Web Vitals; rich-result status reports; manual actions; security issues; and Links. The API only covers Search Analytics, Sitemaps, Sites, and URL Inspection. So the immediate Observatory question is not “does GSC have it?” but “does GSC expose it in a stable machine interface, or is it UI-only?” That distinction matters because UI export is not the same thing as a durable provenance contract. citeturn4view2turn6view0turn6view1turn6view2turn6view3turn6view5turn26view0

Google’s strongest official caveats for search-performance data are the ones people love to forget after one too many dashboards: anonymized queries are omitted from tables for privacy; chart totals can exceed summed table rows; export and API rows are capped outside bulk export; performance data is aggregated and filtered; page data is usually canonicalized; and the heuristics for impressions and position are subject to change. That is why GSC is a strong witness, not a perfect transcript of reality. citeturn10view0turn10view1turn10view4turn33view0turn9view1

### Appendix A — GSC Data Table

| GSC data type | UI | API | Exportable | Retention / window | Granularity / caveats | Observatory usefulness | Boundary classification |
|---|---|---|---|---|---|---|---|
| Search performance: clicks, impressions, CTR, avg position by query/page/country/device/date/search appearance | Yes. citeturn5search19turn33view0 | Yes via Search Analytics. citeturn26view0turn27view3 | Yes via UI, API, Looker Studio, BigQuery bulk export. citeturn9view0turn13view0turn13view1 | 16 months in report/API; 24-hour view available for very recent hourly data. citeturn11search12turn35search2 | Canonical aggregation, privacy filtering, truncation, preliminary recent data, position heuristics subject to change. citeturn10view1turn10view4turn33view0turn35search14turn9view1 | Very strong for owned verified-property observation | **Customer properties: exclude from storage now; possible read-time overlay later. Owner-internal: possible later only with owner ruling.** |
| Discover performance | Yes if property reaches minimum Discover impressions. citeturn4view3turn35search6 | Yes via `type=discover`. citeturn27view1 | Yes via UI/API/bulk export. citeturn27view1turn13view0turn13view2 | Same performance-history regime as Search Console performance reporting; preliminary newest data explicitly documented. citeturn35search6turn11search12 | Threshold-gated; property aggregation differs; preliminary data. citeturn4view3turn27view1turn35search6 | Strong but limited witness for Discover exposure | Same as above |
| Google News performance | Yes if property has sufficient traffic on News. citeturn4view4turn6view5 | Yes via `type=googleNews`; separate from Search “News” tab. citeturn27view1turn27view3 | Yes via UI/API/bulk export. citeturn27view1turn13view0turn13view2 | Same performance-history regime; preliminary newest data documented. citeturn35search20turn11search12 | Not the same as Google Search News-tab data; threshold-gated; recent data can be preliminary. citeturn4view4turn27view1turn35search20 | Strong for News-surface observation | Same as above |
| Page indexing report | Yes. citeturn28view1 | No direct Page indexing API report; partial overlap via URL Inspection API. citeturn26view0turn32view0 | UI export available on many reports, but no dedicated public API report. citeturn12search14turn26view0 | Not clearly published as a fixed retention window. citeturn28view1 | Shows all URLs Google knows in property; some 404 examples only last month; specific URL lookup must use URL Inspection. citeturn28view1 | High for indexing-state evidence, weaker for bulk automation than performance data | **Customer properties: exclude from storage now; read-time overlay later if needed.** |
| URL Inspection | Yes. citeturn28view2 | Yes. citeturn7search0turn32view0 | API response storable by consumer; no bulk report export in the GSC sense. citeturn32view0 | Per-request current indexed-state response, not a long-range historical report. citeturn7search0turn32view0 | API only returns indexed/indexable status of version in Google’s index; cannot test live URL indexability via API; UI live test covers more immediate state. citeturn7search0turn28view2 | Very high for URL-level evidence and provenance | **Prefer read-time overlay; avoid broad shared storage now.** |
| Sitemaps report / sitemap status | Yes. citeturn6view1 | Yes. citeturn26view0turn5search20 | Yes via API/UI. citeturn26view0turn5search7turn5search13 | No explicit global retention window published. citeturn26view0turn5search20 | Returns last submitted/downloaded, warnings, errors, submitted/indexed counts. citeturn5search20 | Strong technical provenance | Same as other customer first-party telemetry |
| Rich results / enhancements | Yes, report per rich-result type if detected. citeturn6view2turn35search17 | No dedicated rich-results status report API; URL Inspection API can return rich-results analysis for a URL. citeturn26view0turn32view0 | UI export widely available; no dedicated report API. citeturn12search14turn32view0 | No explicit fixed retention window published. citeturn35search17turn32view0 | URL Inspection rich-results output exists; sitewide reports are UI-centered. citeturn32view0turn35search17 | Useful for evidence, but not public truth about eligibility/display | Same as other customer first-party telemetry |
| Core Web Vitals | Yes. citeturn28view0 | No public Search Console API for the report itself. citeturn26view0 | UI export available. citeturn12search14turn28view0 | No fixed retention window stated in report doc reviewed here. citeturn28view0 | Based on CrUX field data; grouped by similar URLs; only indexed URLs can appear; report omits URLs lacking sufficient data and is not comprehensive. citeturn28view0 | Good for UX witness, but heavily sampled/aggregated | Same as other customer first-party telemetry |
| Manual actions | Yes. citeturn4view5turn6view5 | No public API in Search Console API surface. citeturn26view0 | UI visible/export patterns unclear; API absent. citeturn26view0turn4view5 | Includes current actions and history in UI. citeturn4view5 | Extremely sensitive site-state signal; not a public ranking proof beyond Google’s own report. citeturn4view5 | High operational value, high sensitivity | **Exclude from Observatory storage now; if used, read-time overlay only.** |
| Security issues | Yes. citeturn6view5 | No public API in Search Console API surface. citeturn26view0 | UI-centered. citeturn6view5turn26view0 | Not clearly published here. | Sensitive security state, owner-only relevance. citeturn6view5 | High sensitivity; not Observatory-safe now | **Exclude from Observatory storage now.** |
| Links report | Yes. citeturn28view3 | No links API in current Search Console API surface. citeturn26view0 | UI export available; tables truncated to 1,000 rows, exports for sample/latest links up to 100,000 rows. citeturn28view3 | Links found over time; may include links since removed. citeturn28view3 | Sample only, not comprehensive, grouped/canonicalized/deduped, nofollow not specified. citeturn28view3 | Useful as a witness, weak as exhaustive link truth | Same as other customer first-party telemetry |
| Robots / crawl-blocking status | Indirectly via Page indexing and URL Inspection. citeturn28view1turn28view2 | Yes indirectly via URL Inspection fields like `robotsTxtState` and `pageFetchState`. citeturn32view0 | API per-URL or UI per-URL/report. citeturn32view0turn28view2 | Per URL response; report windows vary. | Strong URL-level technical witness, not a global robots-history API. citeturn32view0turn28view1 | Good for evidence; use with narrow scope | Same as other customer first-party telemetry |

### Key official caveats for Observatory use

A safe Observatory stance for GSC performance evidence is: **“Google reported this for this verified property/date range/dimension set.”** That wording is defensible because Google explicitly documents private-query suppression, filtered tables, canonical aggregation, data truncation, and preliminary fresh data. “This keyword had exactly X searches” is not defensible because GSC reports property impressions, not universal market demand, and even its own tables can omit anonymized queries. citeturn10view4turn33view0turn35search14turn9view1

A second safe stance is to separate **provider observation** from **product inference**. Example: “URL Inspection reported Google-selected canonical Y and crawl blocked by robots.txt.” Good. “This page is definitively unindexable everywhere.” Bad. URL Inspection is specific to Google’s indexed view or live test scope, not a cosmic law of the internet. citeturn28view2turn32view0

## Bing Webmaster Tools Data Inventory

Bing Webmaster’s official surface is broader than many teams remember, but its public documentation is less polished and less current than Google’s. The official API overview says Bing Webmaster APIs expose rank and traffic stats, link details, keyword details, crawl stats, URL submission, sitemap submission, and related site-management functions. The interface reference shows methods for query/page stats, crawl stats, link counts, URL info, URL links, feeds, user sites, site roles, blocked URLs, and URL submission quota operations. citeturn19view0turn19view1

Bing’s help-system snippets show a modern UI that includes Search Performance, Backlinks, URL Inspection, Site Scan, Keyword Research, Microsoft Clarity, AI Performance, and Sitemaps. Microsoft also surfaces URL Submission / IndexNow-style immediate notification workflows and explicitly notes AI Performance as a report for Microsoft Copilots and partner surfaces. That matters because Bing is already blurring the classic “search engine only” model in its own webmaster telemetry. citeturn22search0turn16search3turn16search13turn16search12turn16search16turn21search9turn16search8turn16search7turn22search25

### Appendix B — Bing Webmaster Data Table

| Bing data type | UI | API | Exportable | Retention / window | Granularity / caveats | Observatory usefulness | Boundary classification |
|---|---|---|---|---|---|---|---|
| Search performance: clicks, impressions, pages, keywords | Yes. Official snippet says it shows clicks/impressions per page and per keyword and trends for the last six months. citeturn24search0turn24search2 | Yes through query/page/rank-and-traffic methods. citeturn19view1turn19view2 | API yes; UI export likely, but Microsoft’s current public docs reviewed here are not as explicit as Google’s on export mechanics. citeturn19view1turn24search0 | **Officially documented UI window:** up to six months. Broader retention policy for all endpoints is unclear. citeturn24search0turn24search2 | Traffic APIs reviewed here say data updated every week. citeturn19view2turn22search1 | Strong first-party witness for Bing-owned verified-property visibility | **Customer properties: exclude from storage now; possible read-time overlay later.** |
| Query stats / page-query stats | UI yes as part of search performance. citeturn24search2 | Yes. `GetQueryStats`, `GetQueryPageStats`, `GetPageQueryStats`, etc. citeturn19view1turn19view2turn22search1 | Yes via API. citeturn19view2 | UI last six months documented; endpoint-level full retention not clearly published. citeturn24search0 | Weekly updated, so not a near-real-time feed. citeturn19view2turn22search1 | Strong but delayed | Same as above |
| Crawl stats / crawl issues | Yes in platform feature set. citeturn22search19turn16search17 | Yes via `GetCrawlStats` and `GetCrawlIssues`. citeturn19view1turn22search26 | Yes via API. citeturn19view1 | No comprehensive retention statement found. | `GetCrawlStats` says data updated every day. citeturn22search26 | Good technical witness | Same as other customer first-party telemetry |
| URL inspection / URL info | Yes. citeturn16search13 | Yes via `GetUrlInfo`, `GetChildrenUrlInfo`, traffic-info methods. citeturn19view1 | Yes via API. citeturn19view1 | Per-request state; no broad history publication found. | Official snippet says it shows crawling issues, index status, SEO errors, and markup info. citeturn16search13 | Strong URL-level evidence | Prefer read-time overlay over broad storage |
| Sitemaps | Yes. citeturn16search7 | Yes via `GetFeeds`, `GetFeedDetails`, `SubmitFeed`, `RemoveFeed`. citeturn19view1 | Yes via API/UI. citeturn19view1turn16search7 | No global retention statement found. | Standard sitemap witness, not public truth. | Good technical provenance | Same as other customer first-party telemetry |
| Backlinks / link details | Yes. Official snippet says backlinks data can be exported for further analysis. citeturn16search3 | Yes via `GetLinkCounts` and `GetUrlLinks`. citeturn19view1 | Yes according to official snippet and API. citeturn16search3turn19view1 | No explicit retention statement found. | Coverage/completeness caveats are not as clearly documented publicly as Google’s. | Useful but not exhaustive link truth | Same as other customer first-party telemetry |
| Site Scan / SEO Reports / Recommendations | Yes. citeturn16search12turn16search5turn24search13 | No clearly documented current API coverage found in reviewed sources. | UI-centered. | SEO Reports run automatically every alternate week, about twice a month. citeturn22search28 | Audit-style and recommendation-style, so especially unsuited to “database as astronomer.” | Low direct fit for Observatory raw-observation storage | **Better treated as read-time advisory context, or excluded.** |
| Keyword Research | Yes. Official snippet says any timeframe in the last six months. citeturn24search10 | API includes keyword endpoints such as `GetKeyword`, `GetKeywordStats`, `GetRelatedKeywords`. citeturn19view1turn23search0 | API yes; UI yes. | Six-month timeframe documented for UI tool. citeturn24search10 | This is research / estimate / opportunity tooling, not pure property telemetry. | Weak fit for Observatory evidence doctrine | **Prefer exclusion now or use only as caveated context.** |
| Microsoft Clarity integration | Yes. Website must be verified first. citeturn21search9 | No Bing Webmaster API coverage confirmed in reviewed docs. | UI integration. | Not established here. | Cross-tool behavioral analytics, not purely search-engine witness data. | Poor fit for current Observatory doctrine | **SearchClarity/customer layer, not Observatory.** |
| AI Performance | Yes. Official snippet says it contains site AI performance on Microsoft Copilots and partner surfaces. citeturn16search8turn24search6 | **Unclear — needs confirmation.** A 2026 Microsoft Q&A thread asks whether an API exists, suggesting uncertainty. citeturn20search4 | UI yes; API unclear. | Not clearly published. | Newer surface, documentation thinner, higher interpretation risk. | Interesting, but unsafe to treat as settled feed yet | **Needs more research before any boundary decision.** |
| URL Submission / IndexNow-related notification | Yes. Official snippets describe manual submission and immediate notification behaviors. citeturn21search6turn22search25 | Yes. `SubmitUrl`, `SubmitUrlBatch`, quota methods. citeturn19view1turn18search6turn18search16turn18search12 | Yes via API/UI. | Not historical telemetry; operational submission feed. | Batch max 500 unless quota lower; quota should be checked via API. citeturn18search6turn18search12 | Useful operationally, weak fit as Observatory evidence | **Exclude from Observatory storage now.** |

### Bing-specific cautions

Bing’s official docs make two important caution points even though they say them quietly. First, major traffic endpoints like `GetQueryStats` are weekly updated, not fine-grained real-time reporting. Second, Bing’s official public retention picture is incomplete, so any product assumption about long-range replay or historical durability should be treated as unproven until separately tested. citeturn19view2turn22search1turn24search0

That means Bing should be treated as a credible but less fully documented witness than GSC. If Google is the witness who brought receipts and an over-organized folder, Bing is the witness who definitely saw something but forgot where the stapler went. Still useful. Just don’t build doctrine on vibes. citeturn19view0turn24search0turn22search28

## Retention, Freshness, Delay, API and Export Practicalities

Google publicly documents substantially more than Bing on these points. Search Console performance data is available for 16 months, and Google explicitly suggests using the Search Analytics API or bulk data exports if you want to preserve a longer history in your own systems. Search Console’s new 24-hour view and hourly API access expose very recent data with only a delay of a few hours, but Google also flags preliminary data and visually marks it in charts. Outside bulk export, the UI max export is 1,000 rows, and the Search Analytics API limit is up to 50,000 rows per day per site per search type through pagination. Bulk export to BigQuery includes all performance data available to Search Console except anonymized queries, starts prospectively after setup, and the BigQuery tables retain forever by default unless you set expiration. citeturn11search12turn35search2turn35search14turn10view1turn13view0turn13view1turn13view2

Google’s API auth model is clean: Search Console API requires OAuth 2.0, no other auth protocol is supported, and methods specify `webmasters.readonly` or `webmasters` scopes. Official API usage limits documentation also separates Search Analytics load quotas from URL Inspection quotas. Search Analytics uses load quotas; URL Inspection has explicit per-site and per-project quotas. Google’s URL Inspection API itself returns only indexed/indexable status of the version in Google’s index and cannot do the live-test function that the UI can do. citeturn14search5turn14search2turn7search0turn1view2

Bing’s official API auth model allows either OAuth 2.0 or API key usage. Publicly reviewed Bing docs clearly disclose some operational limits — for example, URL submission batch size up to 500 unless the remaining quota is lower, and a quota-check endpoint exists — but Microsoft does not present a Google-style consolidated limit matrix for all Bing Webmaster APIs in the materials reviewed here. For performance data, official docs show a six-month UI window for Search Performance and a weekly update cadence for major query/page traffic endpoints. Crawl stats are documented as daily updated. SEO Reports run approximately twice a month. citeturn20search1turn20search0turn18search6turn18search12turn24search0turn19view2turn22search26turn22search28

### Appendix C — Retention / API Limits Table

| Platform | Data type | Retention / window | Reporting delay | API limit | Export limit | Source |
|---|---|---|---|---|---|---|
| Google | Search performance | 16 months. citeturn11search12 | Fresh 24-hour view appears with only a few hours delay; newest data can be preliminary. citeturn35search2turn35search14 | Search Analytics API default 1,000 rows, `rowLimit` up to 25,000, pagination to 50,000 rows/day/site/search type. citeturn27view3turn10view1 | UI export max 1,000 rows. citeturn10view1 | Official |
| Google | BigQuery bulk export | Starts after setup; first export within up to 48 hours; first export includes day of export only; no backfill by feature itself. citeturn13view1 | Daily export. citeturn13view0turn13view2 | Owner-gated feature, not query-row limited like Search Analytics; includes all performance data except anonymized queries. citeturn13view0turn9view3 | BigQuery tables retained forever by default unless you set expiration. citeturn13view2 | Official |
| Google | URL Inspection API | Per-request URL response, not historical report. citeturn7search0turn32view0 | Current indexed-state response, but API is not live-test indexability. citeturn7search0 | URL Inspection quotas are separately documented in Google’s usage-limits page. citeturn1view2 | N/A | Official |
| Google | Search Console API auth | N/A | N/A | OAuth 2.0 only. citeturn14search5 | N/A | Official |
| Bing | Search performance UI | Up to six months. citeturn24search0turn24search2 | Not clearly stated as hourly/daily; main query/page traffic APIs say weekly updated. citeturn19view2turn22search1 | No consolidated official quota matrix found in reviewed sources. | Export exists for some areas; full export mechanics not clearly consolidated in reviewed docs. | Official / incomplete |
| Bing | Query/page traffic APIs | Full retention horizon unclear from reviewed docs. | Weekly updated. citeturn19view2turn22search1 | Endpoint family exists (`GetQueryStats`, `GetPageStats`, etc.). citeturn19view1 | API retrievable | Official |
| Bing | Crawl stats API | Retention unclear. | Daily updated. citeturn22search26 | Endpoint exists. citeturn19view1 | API retrievable | Official |
| Bing | URL submission | Not retention-oriented; operational submission flow. | Immediate notification intent in UI/API docs. citeturn21search6turn22search25 | Batch max 500 unless quota lower; quota endpoint exists. citeturn18search6turn18search12 | UI/API submission | Official |
| Bing | Keyword Research UI | Any timeframe in last six months. citeturn24search10 | Not specified here. | Keyword APIs exist. citeturn19view1turn23search0 | UI/API | Official |
| Bing | SEO Reports | Not document-retention oriented; recurring audits. | Runs every alternate week, roughly twice a month. citeturn22search28 | API coverage unclear in reviewed sources. | UI-centered | Official / incomplete |

### Safe caveat language

Use language like this for Google:

> Google Search Console reported **X clicks / Y impressions / Z average position** for this **verified property** over this **date range and dimension set**. This is first-party Google-reported data, but it is subject to Google’s aggregation, privacy filtering, canonicalization, truncation, and reporting-delay limitations. citeturn10view1turn10view4turn33view0turn35search14

Use language like this for Bing:

> Bing Webmaster Tools reported **X clicks / Y impressions / ranking metrics** for this **verified site** in the reviewed window. This is first-party Bing-reported data for a verified property, but official Microsoft docs indicate update cadence limits and do not fully publish all retention and reporting-boundary details for every endpoint. citeturn24search0turn19view2turn20search1

### Practical storage and caching implication

Official docs make one thing very clear for Google: if you configure bulk export or store API responses in your own systems, the data can outlive Google’s native 16-month Search Console reporting window. Google even says to use API or bulk export if you want longer history. That means “what can technically be stored” and “what should be stored in The Observatory” are different questions. The former is yes; the latter is no for customer data under your current doctrine. citeturn11search12turn13view1turn13view2

## Boundaries, Evidence Fit, Claim Safety, and Recommended Handling

### First-Party vs Third-Party Data

For a verified owned property, GSC/Bing are more direct than Ahrefs, Semrush, or DataForSEO because the search engine itself is the reporting source and the property owner is authenticated into a verified-property context. GSC tells you what Google says happened for that verified property. Bing tells you what Bing says happened for that verified site. Third-party tools, by contrast, position themselves around estimated search volumes, keyword databases, and tracked rankings for chosen keywords, locations, devices, or snapshots. Ahrefs explicitly markets search-volume estimates. Semrush explicitly markets daily position tracking for selected keywords. DataForSEO explicitly defines search volume as an estimate and describes it as derived from Google/Bing-type source metrics and clickstream/refinement methods. citeturn14search5turn20search1turn36search0turn36search6turn36search1turn36search4turn36search17turn36search8

That does **not** make GSC/Bing perfect truth. Google explicitly says performance data is privacy-filtered, limited, aggregated, canonicalized, and heuristic-bound. Google also states impression/position heuristics can change. Bing explicitly shows weekly update cadence for major query/page traffic APIs and thinner public retention/limit documentation. So first-party data is stronger for owned verified properties, but still not universal truth. It is provider truth under provider measurement rules. Same telescope, different fog. citeturn10view0turn10view1turn10view4turn9view1turn19view2turn24search0

What GSC/Bing can prove:

- The provider reported clicks, impressions, CTR, ranking-position metrics, indexing states, crawl states, or link samples for a verified property in a given reported window. citeturn26view0turn32view0turn19view0turn19view1

What they cannot prove:

- Total market search demand for a keyword.
- Exact universal rank for every user, locale, and moment.
- Exhaustive link graphs.
- That a zero in a table means zero real-world opportunity rather than thresholding, privacy filtering, truncation, or missing coverage. citeturn10view4turn33view0turn28view3turn24search0

When GSC actual impressions disagree with keyword-volume estimates, the safer interpretation is that GSC is stronger for **what Google reported showing for that property**, while the volume tool is stronger only for its own **estimated demand model**. The two are not measuring the same thing. Ahrefs and DataForSEO both describe search volume as estimated / modeled. citeturn36search6turn36search17turn10view0turn9view1

When average position disagrees with a rank tracker snapshot, the safest reading is that GSC/Bing position is provider-aggregated performance reporting over impressions, while rank trackers are location/device/query-specific tracked snapshots or daily monitored campaigns. Semrush explicitly describes position tracking as daily monitoring for selected keywords, locations, devices, and search engines. Those are different measurement systems, so disagreement is expected, not scandalous. citeturn9view1turn36search4turn36search16

### Customer Data Boundary

This is the most important operational conclusion in the report.

Google Search Console data for a customer property is private verified-property telemetry. Access requires ownership verification plus granted permissions; the API requires OAuth 2.0; and Google’s API user-data policy applies when requesting Google user data. Bing Webmaster data for a customer property is similarly private verified-site telemetry: access requires verified-site ownership/authorization, and the API requires OAuth 2.0 or API key access to the verified account/site context. citeturn14search5turn5search17turn14search0turn20search1turn20search0turn21search0

That means customer GSC/Bing exports should be treated as **customer first-party/private data** for Observatory-boundary purposes. The risk is not theoretical. If stored in a shared Observatory DB, this data can create cross-customer scope leakage, ambiguous retention/deletion obligations, over-broad access by internal users, provenance confusion between public observations and customer-private overlays, and dangerous false confidence when private telemetry gets mixed with public SERP evidence. Those are architectural and governance inferences grounded in the access model and user-data nature of the feeds, not quoted provider terms. citeturn14search0turn25search1turn20search1turn19view0

### Data category table

| Data category | Store in Observatory now | Later possible | Boundary notes |
|---|---|---|---|
| Customer first-party data | **No** | Yes, but only by explicit owner doctrine change | Includes customer GSC/Bing verified-property data. Treat as private customer telemetry. citeturn14search5turn20search1 |
| Owner-internal first-party data | **No by default** | **Possible later** | Treat separately from customer data; needs explicit owner ruling and internal-only controls. This is an inference/policy recommendation. |
| Publicly observable external data | **Yes** | Yes | Fits Observatory doctrine best. |
| Provider-estimated third-party data | **Yes, with caveats** | Yes | Ahrefs/Semrush/DataForSEO estimates are not first-party truth; safe as caveated witness/context. citeturn36search0turn36search4turn36search17 |
| Read-time overlay data | **Not stored now** | **Yes** | Best near-term pattern for customer GSC/Bing if ever allowed. |
| Derived/cited claim data | **Yes, selectively** | Yes | Store only promoted, provenance-linked conclusions if your doctrine allows accepted conclusions to promote outward. |

Default doctrine preserved: **Customer GSC/Bing data should not be stored in Observatory now.** If used later, the safest default is a read-time overlay from SearchClarity / customer engagement systems, not ingestion into shared Observatory storage. That is the cleanest way to honor “the database must never become the astronomer.” citeturn14search0turn20search1turn25search1

### Owner-Internal Telemetry Boundary

Owner-internal GSC/Bing data is different from customer GSC/Bing data because the owner is both the operator and the beneficiary. That reduces consent and commercial-boundary problems, but it does **not** erase the need for internal provenance, access segregation, retention rules, and clear labeling that the data is internal telemetry rather than public Observatory evidence. This section is inference and governance reasoning, not provider doctrine. citeturn14search5turn20search1

Minimum boundary rules if owner-internal telemetry is ever considered later:

- Internal-only scope must be explicit and non-expandable by accident.
- Every record/view must carry source, property identifier, retrieval time, permission scope, and “internal first-party” labeling.
- Read paths must prevent confusion between public observations and internal telemetry.
- Deletion and retention rules must be owner-defined before ingestion.
- Promotion into outward-facing claims must preserve provider attribution and caveats.  

Those are not implementation details; they are survival requirements. Without them, “internal-only” becomes “surprise, this screenshot is in a sales deck.” Charming. Also bad. The classification below reflects that. citeturn14search0turn25search1

### Owner-internal status classification

| Status | Owner-internal GSC/Bing data |
|---|---|
| Forbidden now | **Yes** |
| Possible later under internal-only scope | **Yes** |
| Possible later as read-time overlay | **Yes** |
| Needs explicit owner ruling | **Yes** |
| Needs hammer tests | **Yes** |

### API and export practicalities table

| Platform | API | Auth | Quotas / limits | Export format | Practical caveat |
|---|---|---|---|---|---|
| Google | Search Analytics | OAuth 2.0 only. citeturn14search5 | Search Analytics row handling: default 1,000, `rowLimit` to 25,000, pagination to 50,000 rows/day/site/search type; usage-limits page also sets load quotas. citeturn27view3turn10view1turn1view2 | JSON API; UI exports; Looker Studio; BigQuery bulk export. citeturn9view0turn13view0 | Privacy-filtered, truncated, canonicalized, preliminary-recent data. citeturn10view4turn33view0turn35search14 |
| Google | URL Inspection | OAuth 2.0 only. citeturn14search5 | Separate per-site and per-project quotas documented on usage-limits page. citeturn1view2 | JSON API response | API is not live-test indexability; only indexed/indexable status from Google’s index. citeturn7search0 |
| Google | Sitemaps / Sites | OAuth 2.0 only. citeturn14search5 | Standard API usage constraints; no unusual export story. | JSON API response | Limited scope compared with UI report breadth. citeturn26view0 |
| Bing | Webmaster API general | OAuth 2.0 or API key. citeturn20search1turn20search0 | No consolidated official public quota sheet found in reviewed sources. | XML or JSON request/response patterns documented on methods. citeturn19view2 | Official docs older and less consolidated. |
| Bing | Query/page traffic | OAuth 2.0 or API key. citeturn20search1 | Endpoint family exists; traffic methods reviewed here update weekly. citeturn19view2turn22search1 | JSON/XML API patterns | Weekly cadence makes it weaker for near-real-time monitoring. |
| Bing | URL submission | OAuth 2.0 or API key. citeturn20search1 | Batch max 500 unless quota lower; quota endpoint available. citeturn18search6turn18search12 | API / manual UI submission | Operational feed, not historical evidence system. |

### Evidence and Provenance Fit

The Observatory needs provenance-complete evidence. GSC does surprisingly well on this for API-accessible data because the API request itself supplies property, date range, dimensions, filters, aggregation type, row limits, and retrieval time can be captured externally. URL Inspection responses also include index-state fields like sitemap references, referring URLs, robots state, indexing state, page fetch state, canonical data, crawl timestamp, and a link back to the Search Console inspection view. Bing can support provenance too, but its current public docs are less explicit and less consistently modern. citeturn27view3turn32view0turn19view1turn19view2

### Evidence Fit table

| Need | GSC support | Bing support | Notes |
|---|---|---|---|
| Provider name | Strong | Strong | Both are provider-native platforms. citeturn26view0turn19view0 |
| Property ID / site URL | Strong | Strong | GSC uses `siteUrl`; Bing methods use `siteUrl`. citeturn13view2turn19view2 |
| Verification / permission context | Strong | Moderate | GSC has explicit permission levels; Bing clearly requires verified sites, but less explicit permission taxonomy was found in reviewed docs. citeturn5search17turn21search0 |
| Date range | Strong for Search Analytics | Moderate | GSC request explicitly carries start/end date; Bing traffic method examples expose dated stats but reviewed docs are less standardized. citeturn27view3turn19view2 |
| Query/page/country/device/search appearance dimensions | Strong | Moderate | GSC explicitly documents these dimensions and appearance mappings; Bing query/page coverage is clear, other dimension coverage less clearly documented in reviewed sources. citeturn27view3turn33view0turn19view1 |
| Retrieval timestamp | Partial | Partial | Usually captured by client system, not always returned as a report field. |
| Request parameters | Strong | Strong | Both API approaches allow request capture externally. citeturn27view3turn19view2 |
| Response metadata | Strong | Moderate | GSC URL Inspection especially rich; Bing method docs show typed responses but less comprehensive metadata detail in reviewed docs. citeturn32view0turn19view2 |
| Row counts / pagination context | Strong | Moderate | GSC documents row limits and pagination; Bing limits less consolidated publicly. citeturn27view3turn10view1turn18search6 |
| Aggregation / filtering notes | Strong | Weak to moderate | Google is explicit; Bing much less so in reviewed docs. citeturn10view0turn33view0turn24search0 |
| Freshness / delay notes | Strong | Moderate | Google explicitly documents preliminary / hourly / fresh data; Bing weekly/daily cadence is documented on some methods. citeturn35search2turn35search14turn19view2turn22search26 |
| Errors / status codes | Strong | Moderate | Standard API behavior exists for both; GSC docs are cleaner. citeturn26view0turn19view2 |
| Export hashability | Strong | Moderate | API responses and BigQuery exports are hashable; Bing API outputs are also hashable, but public export surface is less centralized. |

### Appendix D — Safe vs Unsafe Claim Matrix

| Metric | Safe wording | Unsafe wording | Caveat |
|---|---|---|---|
| Clicks | “GSC reported 88 clicks for this verified property/query/date range.” citeturn9view1turn10view0 | “This keyword got 88 clicks on Google overall.” | Property-scoped, not universal. |
| Impressions | “GSC reported 88 impressions for this verified property/query/date range.” citeturn9view1turn10view4 | “This keyword has only 88 searches.” | Impressions are not market search volume; anonymized rows may be omitted. |
| CTR | “GSC reported a CTR of X% for this verified property/date range/dimension set.” citeturn9view1 | “Users click this result X% of the time in general.” | Context-specific, provider-calculated. |
| Average position | “GSC average position suggests Google often showed this URL around position X in the reported impression set.” citeturn9view1 | “The page ranked exactly #X.” | Averaged, heuristic, impression-weighted, can vary by user/context. |
| Query | “Google reported this query row for the property, subject to privacy filtering and truncation.” citeturn10view4turn33view0 | “This is the complete list of queries.” | Not complete. |
| Page | “This page row is reported under Google’s canonical/page aggregation rules.” citeturn33view0 | “This exact URL received all of these clicks directly.” | Canonical aggregation can shift credit. |
| Country | “Provider grouped this activity under country X.” citeturn27view3turn13view2 | “All users were physically in country X.” | Provider grouping, not perfect geolocation truth. |
| Device | “Provider grouped these impressions/clicks under device type X.” citeturn27view3turn33view0 | “Every user used this device category exactly as tracked.” | Device categories are provider abstractions. |
| Search appearance | “Google reported this search appearance for the URL/result set.” citeturn33view0 | “The click definitely happened on that feature element.” | Google warns appearance filtering does not guarantee click occurred on that exact feature. |
| Indexing status | “URL Inspection reported this Google index status at retrieval time.” citeturn32view0 | “This page is absolutely indexable / non-indexable everywhere.” | Provider- and time-specific. |
| Crawl issue | “Provider reported this crawl/fetch issue for the inspected URL.” citeturn32view0turn22search26 | “The page is unreachable to all crawlers.” | Search-engine specific. |
| Manual action | “Search Console shows a manual action affecting this verified property.” citeturn4view5 | “The site is banned.” | Manual actions vary in scope and effect. |
| Security issue | “Search Console shows a Google-detected security issue for this verified property.” citeturn6view5 | “The site is definitively hacked in every sense.” | It is Google-reported security-state telemetry. |
| Rich result / enhancement | “Google reported structured-data / rich-result issues for this property or URL.” citeturn35search17turn32view0 | “This page will always show rich results once fixed.” | Eligibility is not guaranteed display. |
| Backlink / link data | “Provider link report shows sampled / grouped link data for this property.” citeturn28view3turn16search3 | “This is the complete backlink profile.” | Google explicitly says sample only; Bing completeness boundaries are less documented. |

### Recommended Observatory Handling

What should be excluded from Observatory now:

- Customer GSC/Bing search-performance exports.
- Customer URL Inspection outputs.
- Customer indexing, manual action, security issue, sitemap, link, CWV, and rich-result status data.
- Bing Site Scan / SEO Reports / recommendations.
- Clarity-linked behavioral telemetry.  

These are all customer first-party or customer-adjacent private operational data streams. They belong in SearchClarity / customer engagement layers, not Observatory storage. citeturn14search5turn20search1turn21search9turn16search12

What may be allowed as future read-time overlay:

- Customer GSC/Bing performance summaries.
- Customer URL Inspection outputs for cited pages.
- Customer indexing / sitemap / crawl states used to interpret public observations.
- Customer security/manual-action signals if the owner explicitly authorizes them and they are never persisted in Observatory.  

That satisfies the telescope doctrine better than ingestion because the private witness appears only at read time, with explicit consumer/legal context attached. This is a governance recommendation inferred from the official access models and your doctrine. citeturn14search0turn20search1turn25search1

What may be allowed later for owner-internal properties:

- Possibly GSC/Bing search performance and indexing telemetry for owner-controlled domains only.
- Only after explicit owner ruling.
- Only with internal-only scope labeling, retention rules, access segregation, and a claim-safety layer.  

Again: possible later, not approved now.

What belongs in Provider Cross-Check as caveated context later:

- “Google reported X for verified property Y.”
- “Bing reported Z for verified site Y.”
- “Third-party provider estimated volume A / tracked rank B.”
- “Observed public SERP snapshot showed C.”  

The useful move is the comparison, not the storage of all sources in one bucket where they start impersonating each other.

### Questions / Unknowns To Confirm

- **Unclear — needs confirmation:** whether Microsoft currently publishes a comprehensive retention policy for Bing Webmaster traffic data beyond the six-month UI claims surfaced in official snippets. citeturn24search0
- **Unclear — needs confirmation:** full current Bing export mechanics by report family, because several help pages are JS-only in crawlable view. citeturn17view0
- **Unclear — needs confirmation:** whether Bing AI Performance has official API coverage today. Official public materials reviewed here do not settle that cleanly. citeturn20search4
- **Needs hammer tests:** exact operational differences between GSC UI exports, Search Analytics API, and BigQuery bulk export for the same high-volume property and date range, especially around late-arriving adjustments and anonymized-query handling. Google documents the concepts, but product boundary work should still test them. citeturn10view1turn13view2
- **Needs hammer tests:** Bing API response shape, pagination, and practical quota behavior for high-volume multi-property access. Official docs reviewed here are not enough to derive a production-safe boundary alone. citeturn19view1turn20search1

### Decision Inputs For M1 Roadmap

Must know before M1 roadmap sequencing:

- Whether M1 includes **any** first-party overlay path at all, or whether first-party data is fully out of scope for M1.
- Whether owner-internal properties are in scope for M1 as a separate track or explicitly deferred.

Must know before schema:

- Whether Observatory stores only public observations in M1.
- Whether any future provider-overlay reference needs pointer/provenance fields without storing the underlying customer-private payload.

Must know before owner-internal telemetry decision:

- Explicit owner ruling on whether internal first-party telemetry is conceptually allowed.
- Required retention, deletion, access, and audit rules if allowed.

Must know before read-time overlay contract:

- Who holds the OAuth/API credentials.
- Where customer-private data lives.
- What minimum provenance and consent metadata must accompany read-time use.
- Whether overlays are ephemeral only or can produce cached derived claims elsewhere.

Must know before customer-facing use:

- Safe claim language library.
- Review / citation policy for provider-reported metrics.
- Deletion and revocation behavior when customer access is removed.

### Decision-ready summary

Recommended status:

- **Excluded from Observatory storage now:** customer GSC/Bing data; customer indexing/security/manual-action/link/CWV/enhancement data; Bing Site Scan / recommendation / Clarity-linked behavioral data.
- **Allowed only as future read-time overlay:** customer GSC/Bing verified-property telemetry, if separately governed and provenance-complete.
- **Possible later for owner-internal properties with explicit owner ruling:** owner-controlled GSC/Bing properties, under internal-only governance.
- **Suitable for SearchClarity / customer layer, not Observatory:** customer first-party webmaster data in general.
- **Needs more research:** Bing AI Performance API/export status; Bing long-range retention specifics; full Bing export and quota matrix. citeturn20search4turn24search0turn20search1

Must know before M1 roadmap sequencing:

- Whether first-party overlay is in or out for M1.
- Whether owner-internal telemetry is a separate workstream or deferred.

Must know before schema:

- Whether Observatory needs only public-source provenance now, or public-source provenance plus future overlay-pointer support.

Must know before owner-internal telemetry decision:

- Explicit owner ruling, retention rules, and access boundaries.

Must know before read-time overlay contract:

- Credential ownership, access model, provenance fields, revocation/deletion behavior, and claim-promotion rules.

Must know before customer-facing use:

- Approved caveat language, conflict-resolution rules between first-party and third-party instruments, and deletion/access procedures if a customer disconnects property access.