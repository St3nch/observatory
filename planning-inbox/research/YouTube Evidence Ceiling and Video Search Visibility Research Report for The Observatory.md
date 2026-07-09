# YouTube Evidence Ceiling and Video Search Visibility Research Report for The Observatory

## Executive Summary

The short answer is that the evidence ceiling for YouTube is real, and it is lower than many SEO/video tools pretend. Public YouTube evidence exists and is useful, but it is fragmented across several very different surfaces: public YouTube pages, the official YouTube Data API, creator-authorized YouTube Analytics and Reporting APIs, Google Search video surfaces, third-party provider outputs, and manual public evidence capture. Those are not the same thing, and The Observatory should not flatten them into one blob called “YouTube data.” citeturn21view3turn21view4turn20view0turn14view3turn19view0

DataForSEO **does now provide YouTube-native support** in its SERP API. In the official docs reviewed, DataForSEO documents YouTube Organic search results, YouTube Video Info, YouTube Video Comments, and YouTube Video Subtitles endpoints. Those endpoints return structured observations such as query, captured time, result type, title, URL, video ID, thumbnail URL, channel identifier/name/URL, descriptions, badges, views count, publication date text, duration, and comment/subtitle blocks depending on endpoint. That means the earlier caution “do not assume DataForSEO has YouTube-native data” was correct as a research posture but no longer correct as a conclusion. It does; just not as official YouTube platform truth. It is provider-collected testimony about what DataForSEO observed on YouTube. citeturn2view0turn4view3turn2view1turn4view0turn3view5turn2view2turn4view2

The official YouTube Data API is the clearest source for **public metadata** and some public statistics, but it comes with hard policy boundaries. Public API data generally cannot just be stored forever. YouTube’s Developer Policies say non-authorized data generally must be deleted or refreshed after 30 days, and stored API data must be kept current; user-authorized data must be deleted within 7 days after revocation. The policies also prohibit downloading or caching YouTube audiovisual content without prior written approval and prohibit creating replacement or derived metrics from API data that masquerade as YouTube metrics. That is the part where many tools step on a rake and then act surprised when the rake fights back. citeturn9view0turn9view1turn9view2turn9view3turn8view3

The YouTube Analytics API is creator-private by design. All requests must be authorized. Channel reports are for the authenticated user’s channel or a specific channel owned by the authorizing user; content-owner reports are for YouTube content partners. Metrics include views, watch time, average view duration, shares, likes, subscribers gained/lost, estimated revenue, and breakdowns by country, age, gender, traffic source, device, and more. That is **not** public ecosystem evidence. It is first-party private performance data. Under your doctrine, customer YouTube Analytics belongs in SearchClarity or another customer layer by default, not in The Observatory. citeturn14view3turn14view2turn14view0turn14view1turn15view0turn15view1turn15view3turn15view4

Google Search video evidence is useful, but it proves only what Google showed in a particular context at a particular time. Google’s own documentation emphasizes that search-result visual elements change over time and vary by country, language, device, and other factors. So a captured Google video result can safely support a claim like “Google showed this YouTube URL in a video result or short-videos feature for query X under context Y at timestamp Z.” It cannot safely support “this video ranks number one on YouTube.” Different telescope. Different sky. Different liar. citeturn19view0turn19view1turn2view4turn2view3

Third-party YouTube SEO tools are mostly best treated as **provider testimony**. Tools such as vidIQ, TubeBuddy, Semrush’s Keyword Analytics for YouTube, Ahrefs’ YouTube keyword tooling, Keyword Tool, Morningfame, and Social Blade expose a mix of public platform metadata, creator-authorized overlays, modeled search-volume estimates, proprietary competition/difficulty scores, opportunity scores, earnings estimates, and trend products. Those outputs can be observed and stored as “provider X said Y on date Z,” but not promoted to platform truth. The tools themselves often make clear that they are estimating, weighting, or personalizing scores. citeturn26search2turn26search5turn23search1turn23search9turn27search0turn27search1turn27search2turn28search6turn24search2

The practical admission rule that falls out of this research is strict: The Observatory should favor **public, context-bound, provenance-complete observations** from official APIs where possible and from carefully bounded provider surfaces where necessary. It should reject customer-private analytics by default, reject scraping automation against YouTube pages absent explicit permission, and treat third-party scores as testimony instead of truth. citeturn30view0turn8view1turn8view3turn33view0

## Confidence and Source Quality

Confidence is highest on the following points because they are supported by current official documentation from Google/YouTube or current provider docs from DataForSEO: DataForSEO’s existence of YouTube-native endpoints; YouTube Data API endpoint behavior and quotas; YouTube API Services Terms and Developer Policies; YouTube Analytics API authorization rules and supported metrics/dimensions; and Google Search’s guidance that visual elements vary by context. citeturn2view0turn2view1turn2view2turn21view0turn21view2turn8view1turn8view0turn14view3turn14view0turn19view0

Confidence is medium on third-party tool classifications because public product pages and help docs often describe features and pricing, but they do not always fully disclose sourcing methodology, data-refresh logic, export rights, redistribution rights, or whether a metric is directly observed versus modeled. Where a provider explicitly disclosed estimation, weighting, or third-party licensed data, that is stated directly; where it did not, the report marks the point as **unclear — needs confirmation**. citeturn23search1turn23search9turn27search0turn27search1turn27search2turn28search6turn24search2

Confidence is lower on broad legal conclusions about manual screenshot retention and later redistribution because the reviewed terms clearly constrain automation, copying, use of API data, and reproduction of content, but they do not provide a neat, blessed paragraph saying “yes, your internal evidence archive is fine, sweetheart.” Where this report infers a boundary from the terms, it says so explicitly. citeturn30view0turn8view1turn8view0

All web sources cited below were accessed on **July 8, 2026** in the user’s stated time context. citeturn7search0turn33view0

## Source List

The highest-value sources used for this report were the current official and provider documents below, all accessed on **July 8, 2026**:

| Source | What it established | Accessed |
|---|---|---|
| YouTube API Services Terms of Service | Governing rules for API access and use | 2026-07-08 citeturn8view1 |
| YouTube API Services Developer Policies | Storage, refresh, deletion, aggregation, metric-derivation, privacy rules | 2026-07-08 citeturn8view0turn9view0turn9view1turn9view2turn9view3turn9view4 |
| Google API Services User Data Policy | User-consent and user-data handling rules for OAuth-authorized data | 2026-07-08 citeturn8view2 |
| YouTube Data API reference pages | Public metadata/search/comments/playlists/captions endpoint behavior and quotas | 2026-07-08 citeturn20view0turn21view0turn21view1turn21view2turn21view3turn21view4turn21view5turn22view0 |
| YouTube Analytics API docs | Private analytics authorization, metrics, dimensions, report scope | 2026-07-08 citeturn14view3turn14view2turn14view0turn14view1turn15view0turn15view1turn15view3turn15view4 |
| YouTube Reporting API docs and revision history | Bulk reports, reach reports, thumbnail impression/CTR availability | 2026-07-08 citeturn17search0turn17search2turn17search3 |
| Google Search Central docs | Video result behavior, context variation, video-result eligibility and features | 2026-07-08 citeturn19view0turn19view1turn19view2 |
| YouTube Terms of Service | General restrictions on automated access, copying, harvesting identifying info | 2026-07-08 citeturn30view0 |
| DataForSEO YouTube SERP docs | Official provider proof of YouTube-native endpoints and returned fields | 2026-07-08 citeturn2view0turn2view1turn2view2turn3view5turn4view0turn4view2turn4view3 |
| DataForSEO Google SERP docs and feature docs | Indirect Google video evidence capture | 2026-07-08 citeturn2view3turn2view4 |
| DataForSEO terms and API pages | Provider-side data usage restrictions and product coverage | 2026-07-08 citeturn33view0turn32search1 |
| Third-party tool docs | Practical context for keyword scores, estimates, exports, pricing | 2026-07-08 citeturn23search1turn23search9turn26search0turn27search0turn27search1turn27search2turn28search0turn24search2 |

## Research Findings

**YouTube surface overview**

The surfaces that matter for YouTube/video visibility are not one surface. At minimum they break into: public YouTube watch/channel/playlist pages, YouTube search result pages, the official YouTube Data API, creator-authorized YouTube Analytics and Reporting APIs, Google Search video results, third-party optimizer tools, and manual public evidence capture. Google’s own Search docs emphasize that search-result visual elements change over time and vary by device, country, language, and other factors; YouTube’s own Data and Analytics APIs also split sharply between public metadata and authorized private analytics. citeturn19view0turn20view0turn21view3turn21view4turn14view3

| Surface / Source | Public Data | Private Data | Official API | Export | Biggest Risk |
|---|---|---|---|---|---|
| Public YouTube watch/channel/playlist pages | Titles, descriptions, thumbnails, visible counts, channel names, public comments, playlists if public | None by default on page view; viewer/account personalization may affect experience | No | Manual capture possible; systematic automation restricted | YouTube ToS restrict automated access and copying; page state may be personalized or volatile. citeturn30view0turn21view5 |
| YouTube Data API | Public video/channel/playlist metadata, search responses, comments; some stats | OAuth-authorized account/channel data and owner-only parts | Yes | JSON/API response export | 30-day refresh/deletion rules for much API data; no derived replacement metrics; no caching/downloading content. citeturn12search1turn20view0turn21view0turn21view2turn9view0turn9view1turn9view2 |
| YouTube Analytics API | None without authorization | Channel/content-owner analytics and revenue data | Yes | Query export via API | This is creator-private performance data, not public observation. citeturn14view3turn14view2 |
| YouTube Reporting API | None without authorization | Bulk analytics and reach reports, including thumbnail impression metrics | Yes | Bulk downloadable reports | Same privacy/authorization boundary as analytics; bulk private data. citeturn17search3turn17search2turn17search0 |
| Google Search video results | Query-bound video result appearances, URLs, snippets, thumbnails, visual features | None, unless tied to account-personalized browsing | No YouTube API; Google Search surfaces documented, SERP APIs may observe | Manual or provider export | Mistaking a Google observation for YouTube rank truth. citeturn19view0turn19view1turn2view4 |
| DataForSEO YouTube SERP API | Provider-observed YouTube result sets, video page info, comments, subtitles | No creator-private analytics in docs reviewed | Provider API, not official YouTube API | Yes | Treating provider observation as platform truth; provider terms + search-engine provider terms matter. citeturn2view0turn2view1turn2view2turn3view5turn33view0 |
| Third-party YouTube SEO tools | Mixed public metadata, SERP-like observations, estimates, scores | Some creator-authorized overlays depending on tool | Usually no official YouTube API surface to you directly | Often CSV/PDF/app export | Scores/volumes are often modeled or weighted; methodology opaque. citeturn23search1turn23search9turn27search0turn24search2 |
| Manual public evidence capture | Screenshots of public pages/results with timestamp/context | None unless you capture logged-in/private views | No | Internal archive | Copyright/reuse caution; systematic automation boundary remains. citeturn30view0turn19view0 |

**DataForSEO YouTube and video coverage**

The answer to “does DataForSEO provide YouTube-native data?” is now **yes**. DataForSEO’s own API and product pages document a YouTube SERP API and specific YouTube search-engine types. The core documented YouTube-native endpoints found in the reviewed sources are: YouTube Organic, YouTube Video Info, YouTube Video Comments, and YouTube Video Subtitles. DataForSEO’s SERP product page also explicitly lists a YouTube SERP API alongside Google, Bing, Yahoo, and Baidu SERP APIs. citeturn2view0turn2view1turn3view5turn2view2turn32search1

The YouTube Organic endpoint is essentially a structured observation of YouTube search results under a specified keyword, location, language, device, and OS. It can return mixed result types such as `youtube_video`, `youtube_channel`, `youtube_video_paid`, and `youtube_playlist`, along with `rank_group`, `rank_absolute`, `block_rank`, `check_url`, `datetime`, query context, and per-item fields such as video ID, title, URL, thumbnail URL, channel name/ID/URL, description, badges, views count, publication text, timestamps, and duration. That is a legitimate evidence surface for time-bound search observations. It is not an official YouTube ranking truth service. citeturn2view0turn3view0turn3view1turn4view3

The YouTube Video Info endpoint returns watch-page level observations for a specified video ID, including the captured datetime, video URL, title, thumbnail URL, channel identifiers, channel URL, logo, and description, and the docs describe it as providing “key video and content metrics” from the watch page. The reviewed example clearly shows page-level metadata and identifiers, though not a full official YouTube statistics schema. citeturn2view1turn3view4turn4view0

The YouTube Video Comments and Video Subtitles endpoints also exist officially in DataForSEO. Comments returns the top comments for a specified video plus author information and key comment metrics; Subtitles returns subtitled text segments with timing, original/translated language context, and subtitle counts. These can be useful as evidence of what was publicly observed on a video page at a point in time, but they also raise higher privacy and retention sensitivity than simple metadata capture. citeturn3view5turn4view1turn2view2turn4view2

DataForSEO also provides important **indirect** YouTube/video evidence through Google SERP observation. Its Google SERP API documents rank fields like `rank_group` and `rank_absolute`, explicit location/language/device emulation, and structured SERP features. Its “Short Videos” feature page shows that Google video-like features can return structured cards with title, URL, domain, and source, including YouTube Shorts URLs. That makes DataForSEO a viable bridge for cross-checking YouTube content visibility in Google Search without claiming YouTube-internal rank truth. citeturn2view3turn2view4

The public docs reviewed did **not** clearly show a YouTube-native keyword-volume or keyword-demand database from DataForSEO. The DataForSEO keyword-data help/articles reviewed referenced Google Ads / Google Ads API as the principal source for keyword volume in those products, not YouTube-native keyword demand. So the most defensible classification is: YouTube keyword-volume support from DataForSEO is **unclear or not publicly documented in the reviewed official sources**. citeturn31search8turn31search12turn31search22

| DataForSEO Capability | Native YouTube | Indirect Google SERP | Fields Returned | Pricing Unit | Storage / Rights Notes | Source |
|---|---|---|---|---|---|---|
| YouTube Organic search results | Yes | No | Query context, datetime, result types, rank fields, title, URL, video/channel/playlist IDs, thumbnails, channel fields, description, badges, views, publication text, duration | Request/block-based; exact current public line-item price not clearly confirmed in reviewed 2026 docs | Provider ToS includes data-usage restrictions tied to source-provider interests | citeturn2view0turn3view0turn3view1turn4view3turn33view0 |
| YouTube Video Info | Yes | No | Video ID, title, URL, thumbnail, channel identifiers, description, page-capture metadata | Request-based; exact current public price unclear in reviewed docs | Provider observation of watch page, not official YouTube API stats | citeturn2view1turn3view4turn4view0 |
| YouTube Video Comments | Yes | No | Top comments, author info, comment metrics | Request/block-based in provider docs; exact current public price unclear | Higher privacy sensitivity because commenters are persons | citeturn3view5turn4view1 |
| YouTube Video Subtitles | Yes | No | Subtitle text, language, start/end/duration per segment | Per-result/request per docs; exact current public price unclear | Content reuse sensitivity higher than metadata | citeturn2view2turn4view2 |
| Google video / short-videos evidence for YouTube URLs | No | Yes | Rank fields, feature type, title, URL, domain, visible source, device/location context | SERP task pricing | Strong candidate for cross-check evidence | citeturn2view3turn2view4 |
| YouTube-native keyword volume | Unclear | No | Not clearly documented in reviewed official sources | Unclear | Do not assume exists | citeturn31search8turn31search12 |
| Creator-private channel analytics | No | No | Not documented in reviewed DataForSEO YouTube docs | N/A | Not a DataForSEO YouTube SERP feature in reviewed docs | citeturn2view0turn2view1turn3view5 |

**YouTube Data API evidence ceiling**

The YouTube Data API clearly supports retrieval of public resource metadata for videos, channels, playlists, playlist items, comments, and search-result sets. It also supports write and owner-only operations, but those are not the public-evidence layer. The most relevant public-facing read capabilities for The Observatory are `videos.list`, `channels.list`, `playlists.list`, `playlistItems.list`, `commentThreads.list`, `comments.list`, and `search.list`. citeturn12search1turn21view0turn21view1turn21view3turn21view4turn21view5turn22view0turn20view0

A `video` resource can include `snippet`, `contentDetails`, `player`, `statistics`, `status`, `topicDetails`, and other parts. The `snippet` includes fields such as `publishedAt`, `channelId`, `title`, `description`, `thumbnails`, and `channelTitle`. A `channel` resource similarly exposes metadata, content details, statistics, branding settings, and status. A `playlist` resource is public by default unless private, and `playlistItems.list` exposes item-level `snippet`, `contentDetails`, `status`, and a `position` field within the playlist. citeturn21view3turn21view4turn21view5turn22view0

The search endpoint returns a result set matching a query and can be filtered or shaped by `q`, `type`, `channelId`, `eventType`, `location`, `order`, `publishedAfter/Before`, `regionCode`, `relevanceLanguage`, and `safeSearch`, among others. By default it can return videos, channels, and playlists. That makes it useful for observing what the API returned for a given request context, but the response does **not** expose a first-class “global YouTube rank truth” field. The order of returned items is observable; the universal claim is not. citeturn20view0turn20view1

Comments are retrievable through `commentThreads.list` and `comments.list`, but comment resources can include user-related information and owner-only moderation fields. That means comments are technically retrievable, but they are a poor fit for long-lived public-observation storage unless the organization has a very explicit reason and retention policy. Same story for captions: `captions.list` requires authorization and only returns track metadata; `captions.download` requires edit permission on the video and carries obvious content-rights and private-account implications. citeturn21view0turn21view1turn12search7turn21view2turn10search10

The biggest practical ceiling is policy, not JSON. Under YouTube’s Developer Policies, non-authorized API data generally cannot be stored for more than 30 days without refresh, and stored API data must be kept current. User-authorized data has stricter consent and deletion obligations. API clients also must not create replacement or derived metrics that stand in for YouTube’s own metrics, and must not download/cache/store copies of YouTube audiovisual content without prior written approval. citeturn9view0turn9view1turn9view2turn9view3turn8view3

| Evidence Type | Public / Private | API Endpoint | Store in Observatory Now | Later Possible | Notes / Conditions |
|---|---|---|---|---|---|
| Public video metadata | Public | `videos.list` | Yes, with hard policy caveat | Yes | Safe candidate if treated as time-bound API observation and refreshed/deleted per policy. citeturn12search3turn21view3turn9view0 |
| Public channel metadata | Public | `channels.list` | Yes, with hard policy caveat | Yes | Same 30-day refresh/deletion rule for non-authorized data applies. citeturn11search5turn21view4turn9view0 |
| Public playlist metadata | Public unless playlist private | `playlists.list` | Yes, with hard policy caveat | Yes | Public by default, but private playlists cross into authorized/private territory. citeturn11search6turn21view5turn9view0 |
| Public playlist item observations | Public if underlying playlist public | `playlistItems.list` | Yes, with hard policy caveat | Yes | Includes playlist position, useful for evidence of list composition. citeturn22view0turn9view0 |
| Public search response | Public/time-bound | `search.list` | Yes, cautiously | Yes | Store request context and timestamp; do not over-claim rank truth. citeturn20view0turn20view1 |
| Public comment data | Public but person-linked | `commentThreads.list`, `comments.list` | Usually no | Possibly, with explicit narrow rules | Person-identifying and harvest-risk concerns make this a bad default Observatory fit. citeturn21view0turn21view1turn8view3 |
| Caption track metadata | Authorized/private boundary | `captions.list` | No | Maybe only in customer/private layer | Requires authorization. Metadata only, no actual captions. citeturn21view2 |
| Caption file contents | Private/owner-permission | `captions.download` | No | Only with explicit owner authorization outside Observatory | Requires permission to edit the video. citeturn10search10 |
| Public statistics such as views / likes / comments count | Public in some contexts, but API-storage rules still apply | `videos.list`, `channels.list` | Yes, cautiously | Yes | Useful if stored as timestamped retrievals, not timeless truth. citeturn12search3turn11search5turn9view0 |
| OAuth-authorized private account/channel data | Private | Various `mine` or owner-scoped reads | No | Maybe later in customer layer only | Consent, deletion, and privacy controls required. citeturn20view0turn8view2turn9view2 |

**YouTube Analytics API boundary**

The YouTube Analytics API is not a public-evidence API. All requests must be authorized. Channel reports require `ids=channel==MINE` or a specific channel ID owned by the authorizing user; content-owner reports are only for YouTube content partners. The authorization scopes distinguish between activity reports and monetary reports. That already answers the doctrinal question: by default, this is private creator/channel evidence and belongs outside The Observatory. citeturn14view3turn14view2

Official Analytics docs support metrics such as `views`, `estimatedMinutesWatched`, `averageViewDuration`, `likes`, `comments`, `shares`, `subscribersGained`, `subscribersLost`, and `estimatedRevenue`. Official dimensions support country, age group, gender, traffic source, device type, and more. That means the API can absolutely answer performance questions like “which geographies watched the most,” “what device types drove views,” or “how many subscribers were gained,” but it does so only for an owner-authorized channel/content owner. citeturn14view0turn14view1turn15view0turn15view1turn15view3turn15view4

One important 2026 nuance: official documentation reviewed indicates that **thumbnail impressions and thumbnail CTR reach reports are now in the YouTube Reporting API bulk reports**, not in the standard targeted-query YouTube Analytics API docs reviewed here. The Reporting API revision history says reach reports for channels and content owners were added in January 2026 with metrics `video_thumbnail_impressions` and `video_thumbnail_impressions_ctr`. So if someone says “YouTube Analytics API gives me thumbnail CTR,” the precise answer is: maybe through YouTube’s analytics/reporting family, but the reviewed official evidence points to **Reporting API bulk reach reports**, not ordinary targeted Analytics queries. citeturn17search0turn17search2turn17search3

| Metric / Data Type | Private | Store in Observatory Now | Later Possible | Boundary Notes |
|---|---|---|---|---|
| Views | Yes when pulled from Analytics | No | Maybe in customer layer only | Private performance metric when obtained via Analytics API. citeturn14view0turn14view2 |
| Watch time / estimated minutes watched | Yes | No | Maybe in customer layer only | Same. citeturn14view0turn14view2 |
| Average view duration | Yes | No | Maybe in customer layer only | Same. citeturn14view0turn14view2 |
| Thumbnail impressions | Yes in Reporting API reach reports | No | Maybe in customer layer only | Bulk private reach report, not public evidence. citeturn17search0turn17search2 |
| Thumbnail impression CTR | Yes in Reporting API reach reports | No | Maybe in customer layer only | Same. citeturn17search0turn17search2 |
| Traffic sources | Yes | No | Maybe in customer layer only | Creator-private internal performance breakdown. citeturn15view0turn14view1 |
| Audience geography | Yes | No | Maybe in customer layer only | Country/city/province dimensions are private analytics when sourced here. citeturn15view3turn14view1 |
| Device / OS | Yes | No | Maybe in customer layer only | DeviceType dimension supported. citeturn15view1turn14view1 |
| Subscribers gained / lost | Yes | No | Maybe in customer layer only | Explicit supported metrics. citeturn14view0 |
| Revenue / ad performance | Yes, highly sensitive | No | Maybe in customer layer only with explicit authorization | Monetary scopes required. citeturn14view2turn14view3 |
| Demographics | Yes | No | Maybe in customer layer only | Age/gender dimensions supported. citeturn15view4turn14view1 |

**Google SERP video evidence and YouTube search evidence**

Google Search offers video results as a distinct visual element, and Google explicitly warns that the appearance of search-result elements changes over time and can differ by device, country, language, query, and other factors. Google’s video guidance also describes eligibility for search-page video features, Video mode, key moments, live badges, and related formats. That means a Google SERP capture is rich evidence for what Google showed in a specific observed context, not for universal discoverability across all contexts. citeturn19view0turn19view1turn19view2

A Google video result observation can safely establish the following kinds of facts: query, visible title, visible source, URL, feature type, position within the captured page/provider response, device/location/language context if known, and capture timestamp. It **cannot** safely establish YouTube-native rank position, total demand, or creator performance. If DataForSEO or a similar SERP provider reports a YouTube Shorts URL in a Google short-videos feature, the safe claim is about Google’s observed surface, not YouTube’s ranking system. citeturn2view3turn2view4turn19view0

For YouTube search itself, the official `search.list` endpoint absolutely can return a context-bound result set for a query, and it exposes controls like `order`, `regionCode`, `relevanceLanguage`, `safeSearch`, `publishedAfter`, and more. That is enough to treat a result set as a captured observation under defined request conditions. But one capture does not prove a universal rank truth because the endpoint is parameter-sensitive, page-tokened, limited in page size, and separate from logged-in personalized web experience. The docs also cap certain channel searches at 500 videos in some parameter combinations, which is another reminder that this is an API result set, not some god’s-eye ranking oracle. citeturn20view0turn20view1

| Evidence | What It Supports | What It Does Not Prove | Caveat |
|---|---|---|---|
| Google video result capture | Google showed URL Y as a video result for query X in context C at time Z | YouTube rank truth or creator performance | SERPs vary by device, country, language, and time. citeturn19view0turn19view1 |
| Google short-videos / video feature via SERP API | Structured observation of a Google video feature containing YouTube URLs | That the same result exists on all Google surfaces or on YouTube search | Provider observation of Google, not official Google Search export. citeturn2view4turn2view3 |
| YouTube Data API `search.list` response | API returned resource Y in response to request X at time Z | Universal “#1 on YouTube” claim | Must preserve request parameters like region/language/order/type. citeturn20view0 |
| DataForSEO YouTube Organic response | Provider observed result Y at position P under query/location/language/device context | Official YouTube ranking truth | Treat as provider testimony. citeturn4view3turn33view0 |

**Third-party YouTube SEO tools**

The reviewed tool landscape splits into a few camps. vidIQ and TubeBuddy combine public platform metadata with keyword research, ranking/optimization features, and channel-personalized overlays. vidIQ’s public materials advertise keyword search volume, competition, related queries, trend data, channel audits, and a browser extension that surfaces “real-time keyword data.” TubeBuddy’s docs explicitly say its Keyword Explorer exposes search volume plus both **weighted** and **unweighted** scores, where the weighted score is channel-specific and the unweighted score is general. Those are not platform facts; they are provider outputs, and TubeBuddy says so in substance. citeturn26search2turn26search5turn26search16turn23search1turn23search9

Semrush’s Keyword Analytics for YouTube is unusually candid on one key point: the product says it licenses its data from **third-party data providers**, updates nightly, provides search volume, competition rate, top keywords, fast-growing keywords, trends, top videos, and PDF export, and costs $10/month after a 7-day trial. That makes its metrics useful provider testimony, but not direct YouTube truth. citeturn27search0

Ahrefs’ YouTube keyword tooling says it shows YouTube search volumes in many countries and that its keyword metrics are powered by clickstream data. Keyword Tool says Google/Bing come from planner ecosystems while “other platforms use reliable modeled estimates,” and its YouTube product says it uses YouTube autocomplete and offers search volume/trend/competition data, with web, API, and MCP access on paid plans. Again: useful testimony, not proof carved into the moon. citeturn27search1turn27search2turn25search0turn25search13

Morningfame is clearly a creator-oriented overlay tool. Its FAQ says you connect your YouTube account so it can read your channel statistics, and its site markets keyword research plus rich channel analytics. It also visibly uses internal grades and scoring logic such as relevance scores and competition grades in its own docs. That firmly places much of its output in the bucket of creator-authorized private overlay plus proprietary scoring. citeturn28search6turn28search2turn28search5

Social Blade exposes public statistical data via its Business API, historical performance data, top charts, and premium/API credit systems. Its marketing clearly positions the API as “all our public statistical data.” Social Blade’s familiar earnings/projection figures therefore belong in the “public platform metadata plus provider estimate/model output” bucket, not in the “official YouTube fact” bucket. citeturn24search2turn24search12turn24search7

| Tool | Main Metrics / Outputs | Classification | OAuth / Channel Auth | Export / API | Pricing Signal |
|---|---|---|---|---|---|
| vidIQ | Search volume, competition, related queries, trend data, channel audit, extension overlays | Public metadata + proprietary estimate/score + channel-personalized overlays | Yes for some channel-linked features | Export/API to user not clearly documented in reviewed public sources; enterprise exists | Plans page and support docs show paid plans and enterprise. citeturn26search0turn26search2turn26search16turn26search17 |
| TubeBuddy | Search volume, weighted/unweighted keyword scores, SEO/growth tools | Public metadata + proprietary score; weighted score is channel-specific | Yes for channel-linked use | Public site/tool exports unclear in reviewed sources | Pricing page exists; paid licenses needed for some features. citeturn23search1turn23search9turn24search1turn24search19 |
| Morningfame | Keyword tool, channel analytics, relevance score, competition grades | Creator-authorized private overlay + proprietary score | Yes | Public API not identified in reviewed sources | Pricing page and invite/session model documented. citeturn28search6turn28search2turn28search5turn28search0 |
| Social Blade | Public channel stats, history, rankings, projections, public API data | Public metadata + provider-normalized observation + estimates | Not required for public stats | Business API available | API credits and premium tiers documented. citeturn24search2turn24search12turn24search7 |
| Semrush Keyword Analytics for YouTube | Search volume, competitive rate, top keywords, fast-growing keywords, top videos, trends | Licensed third-party data + provider estimate / normalized observation | No creator auth required for keyword app | PDF export documented | $10/month after 7-day trial. citeturn27search0 |
| Ahrefs YouTube keyword tool | Monthly search volume, clicks, CPS, RR, keyword ideas | Clickstream-based provider estimate | No | Stored in Ahrefs product; public API rights not established in reviewed sources | Pricing tied to Ahrefs product, not clearly separated for YouTube tool in reviewed sources. citeturn27search1turn25search1 |
| Keyword Tool | Autocomplete-based suggestions, modeled search volume/trends/competition for non-Google/Bing platforms, API/MCP | Autocomplete observation + modeled estimates | No | API and MCP documented | Paid plans with daily limits documented. citeturn25search0turn27search2turn25search13 |

## Boundary, Risk, and Provenance Fit

The cleanest public-vs-private model is this: **public external observations are candidates for The Observatory; creator-private or customer-private analytics are not**. Public video, channel, and playlist metadata are candidates if stored as time-stamped observations and handled in line with applicable API/provider rules. Public YouTube search observations and Google video SERP observations are also candidates if they retain request/capture context. OAuth-authorized account data, YouTube Analytics data, and customer channel analytics should remain outside The Observatory by default and live in SearchClarity or an equivalent customer/private layer. citeturn20view0turn21view3turn14view3turn8view2

The comments boundary is stricter. Comments may be public to view, and comment endpoints exist, but YouTube’s policy guidance separately warns against harvesting or storing identifying user information without consent and sets high expectations for privacy and deletion. Public comments are therefore a bad default candidate for Observatory automation, especially if usernames or other person-linked data would be stored in bulk. The safer posture is manual, case-specific evidence use only, if at all. citeturn21view0turn21view1turn8view3

Automation risk is highest for direct YouTube page scraping. YouTube’s Terms of Service say you may not access the service using automated means such as robots, botnets, or scrapers except public search engines under robots.txt or with prior written permission, and you may not collect or harvest identifying information such as usernames or faces unless permitted by the person or allowed under the automation exception. That makes “just scrape YouTube” a bad idea technically, legally, and philosophically for this system. Wonderful way to build an evidence machine that immediately becomes exhibit A. citeturn30view0

By contrast, official APIs are the least-bad automation surface, but they still have storage, deletion, and display rules. DataForSEO is an intermediate-risk provider surface: it is contractually cleaner than ad hoc scraping from your side, but the returned data is still provider-collected and their ToS say SERP data must not be used to compete with or adversely affect the business interests of source search-engine providers. That restriction matters in product design and commercialization reviews. citeturn9view0turn9view1turn9view2turn33view0

For provenance completeness, YouTube and Google video observations are a decent fit if the system stores source/provider name, object URL/ID, query context when search-based, geographic/language/device context where known, authorization state, capture timestamp, result position if applicable, and snapshot or response evidence. The weakest sources for provenance are third-party scores without transparent methodology and creator-private metrics mixed into public-observation systems. citeturn2view3turn4view3turn20view0turn14view3

| Source / Method | API Allowed | Scraping Risk | Storage Risk | Report / Redistribution Risk | Manual Capture Risk | Notes |
|---|---|---|---|---|---|---|
| YouTube Data API public metadata | Yes | Low | Medium | Medium | N/A | Refresh/delete rules apply; no derived replacement metrics. citeturn9view0turn9view3 |
| YouTube Analytics / Reporting APIs | Yes, with OAuth | Low | High | High | N/A | Private creator/customer analytics. Not default Observatory material. citeturn14view3turn17search3 |
| Direct YouTube page scraping | No clear permission in reviewed terms | High | High | High | N/A | Automated access by robots/scrapers restricted. citeturn30view0 |
| DataForSEO YouTube SERP API | Yes via provider API | Lower for you operationally than self-scraping | Medium | Medium | N/A | Still provider-collected testimony; provider ToS impose source-data restrictions. citeturn2view0turn33view0 |
| Google SERP API capture for video features | Yes via provider API | Lower for you operationally than self-scraping | Medium | Medium | N/A | Good for cross-checking Google video visibility only. citeturn2view3turn2view4 |
| Manual screenshots of public pages/results | N/A | Low | Medium | Medium | Medium | Lower automation risk, but copying/distribution/copyright questions remain. Inference from terms; unclear for systematic long-term archival beyond internal evidence use. citeturn30view0turn8view1 |
| Third-party tool screenshots / exports | Usually yes under tool UI | Low | Medium | Medium to High | Medium | Rights vary by provider contract; public marketing pages often do not fully spell out redistribution rights. **Unclear — needs confirmation.** citeturn27search0turn24search2 |

## Claim Safety and Recommended Observatory Handling

The safest claim pattern for this system is brutally literal: “surface/provider X showed Y under context C at time T.” That works for YouTube Data API responses, DataForSEO captures, Google SERP captures, third-party tool outputs, and manual evidence snapshots. The unsafe pattern is “therefore Y is the universal truth of YouTube.” That leap is where evidence systems quietly mutate into strategy engines, fantasy novels, or legal headaches. citeturn20view0turn19view0turn14view3turn27search0

| Evidence | Safe Wording | Unsafe Wording | Required Caveat |
|---|---|---|---|
| Public video metadata | “YouTube Data API returned title/description/stat fields for video Y at retrieval time Z.” | “This is the permanent canonical truth of the video.” | API data is time-bound and subject to refresh/deletion rules. citeturn21view3turn9view0 |
| Public channel metadata | “YouTube Data API returned subscriberCount / channel metadata for channel Y at time Z.” | “Channel Y has exactly this subscriber count, full stop.” | Counts can change; non-authorized storage rules apply. citeturn11search5turn9view0 |
| YouTube search observation | “For request context C, `search.list` returned video Y in the result set on date Z.” | “This video ranks #1 on YouTube.” | Request parameters matter; not universal rank truth. citeturn20view0 |
| DataForSEO YouTube Organic result | “DataForSEO observed video Y at rank_absolute P for query X under location/language/device context C at time Z.” | “Video Y is universally ranked P on YouTube.” | Provider observation, not official YouTube export. citeturn4view3turn33view0 |
| Google SERP video result | “Google Search returned YouTube URL Y in a video result / short-videos feature for query X at time Z.” | “This URL ranks #1 on YouTube.” | Google surface ≠ YouTube search surface. citeturn19view0turn2view4 |
| YouTube Analytics metric | “Authorized YouTube Analytics reports metric X for channel/video Y over period Z.” | “The public market observed metric X.” | Private creator analytics; authorization required. citeturn14view3turn14view2 |
| Third-party keyword volume | “Provider Y estimated YouTube keyword demand / search volume as X.” | “This keyword has exactly X searches on YouTube.” | Provider estimate/model output, not official YouTube fact. citeturn27search0turn27search1turn27search2 |
| Third-party score | “Provider Y assigned competition / weighted / opportunity score X.” | “YouTube says this keyword is easy.” | Tool score is provider testimony. citeturn23search1turn23search9turn28search5 |
| Comments | “A public comment with visible text X was observed on the page / API response at time Z.” | “This comment population represents audience sentiment.” | Privacy, moderation, deletion, and sampling caveats. citeturn21view0turn21view1 |

The strongest early candidate materials for The Observatory are: public YouTube video/channel/playlist metadata retrieved through the YouTube Data API; time-bound YouTube search result observations via the official API; Google SERP video/short-video result observations; and DataForSEO YouTube SERP captures used as provider testimony with preserved capture metadata. These are externally observable, provenance-friendly, and do not require customer-private analytics by default. citeturn21view3turn21view4turn20view0turn19view0turn2view0

Evidence that belongs only in SearchClarity or a customer/private layer includes: customer channel analytics from YouTube Analytics/Reporting; any OAuth-authorized owner-only data; private playlist/channel resources; caption downloads; and any internal performance overlays tied to a customer’s channel account. Even if technically accessible, they violate the stated Observatory doctrine by default. citeturn14view3turn17search3turn21view2

Evidence that should be avoided or very tightly constrained includes: direct automated scraping of YouTube pages; bulk storage of comments/user-linked data; storage of raw copied audiovisual content; and unsupported derived metrics that try to replace YouTube’s own metrics. Third-party scores and estimates should be admitted, if at all, only as provider testimony with source, timestamp, methodology label, and caveat language. citeturn30view0turn9view1turn9view3turn8view3

**Decision-ready source status**

Recommended status by source:

- **YouTube Data API public metadata/search** — **safe candidate for public observation**, but only through official API handling rules and with refresh/deletion logic. citeturn20view0turn21view3turn9view0
- **YouTube Analytics API / Reporting API** — **allowed only as customer-layer/read-time overlay** by default; not Observatory storage material under current doctrine. citeturn14view3turn17search3
- **Google video SERP observations** — **safe candidate for public observation**, especially for cross-checking video visibility outside YouTube. citeturn19view0turn2view4
- **DataForSEO YouTube SERP API** — **safe candidate for public observation with caveats**; store as provider testimony, not platform truth. citeturn2view0turn4view3turn33view0
- **Third-party YouTube SEO tools** — **needs strict caveating**; safe only as provider testimony, not as factual YouTube truth. citeturn23search1turn27search0turn27search1turn28search5
- **Direct YouTube scraping automation** — **risky / avoid automation**. citeturn30view0
- **Manual public capture** — **needs more research for scaled retention/redistribution rules**, but acceptable as narrow internal evidentiary support if used sparingly and contextually. This is an inference, not a clean official blessing. citeturn30view0turn8view1

**Must know before M1 roadmap sequencing**

You need a clear product decision on whether the first admitted YouTube sources are limited to public API metadata/search plus Google SERP captures, or whether DataForSEO YouTube SERP testimony is admitted in M1. That decision affects policy posture more than code posture. citeturn20view0turn2view0

**Must know before schema**

You need explicit policy treatment for API refresh/deletion windows, historical snapshots versus canonical current state, and whether comment/person-linked data is out of scope entirely. The YouTube Developer Policies make those choices non-optional. citeturn9view0turn9view2turn8view3

**Must know before YouTube source admission**

You need a formal rule that third-party scores, estimated search volumes, earnings estimates, and weighted scores are stored only as provider testimony with attached methodology labels. Without that, the database starts doing astrology with better branding. citeturn23search1turn23search9turn27search0turn24search2

**Must know before first YouTube customer-facing report**

You need approved safe-claim language that distinguishes public observation, official API retrieval, authorized private analytics, and provider estimates. The claim-safety matrix below is not optional trim; it is core product hygiene. citeturn20view0turn14view3turn19view0

**Must know before any automation**

You need a hard prohibition on direct YouTube scraping unless explicit written permission exists, plus a documented preference order of official API first, provider API second, manual capture last. citeturn30view0turn8view1turn33view0

**Open questions / limitations**

The reviewed public sources did not clearly disclose a current 2026 public price calculator output for every DataForSEO YouTube endpoint, and they did not clearly document a YouTube-native keyword-volume product from DataForSEO. Those points remain **unclear — needs confirmation**. citeturn2view0turn31search12

Public marketing docs for several third-party tools did not fully resolve redistribution rights, contractual export rights, or methodology transparency for every metric. Those are procurement/legal review questions, not facts I can safely invent. citeturn27search0turn27search1turn24search2

## Appendices

**Appendix A — Source / Surface Comparison Table**

| Surface | Best Use in Observatory | Boundaries |
|---|---|---|
| YouTube Data API | Public metadata and search observations with provenance | Refresh/delete rules; no derived replacement metrics; no raw audiovisual caching. citeturn9view0turn9view1turn21view3 |
| YouTube Analytics / Reporting | Customer/private performance overlay only | OAuth, privacy, deletion, monetization sensitivity. citeturn14view3turn17search3 |
| Google SERP video capture | Cross-check video visibility outside YouTube | Proves Google display only. citeturn19view0turn2view4 |
| DataForSEO YouTube SERP | Provider-observed YouTube search/page testimony | Not official YouTube truth; provider terms matter. citeturn2view0turn33view0 |
| Third-party SEO tools | Provider testimony / market context | Scores and volumes are estimates/models unless proven otherwise. citeturn23search1turn27search0 |
| Manual public capture | Supporting evidence when APIs do not expose the surface | Use narrowly; copyright/reuse questions remain. citeturn30view0 |

**Appendix B — Evidence Category Boundary Table**

| Category | Store in Observatory Now | Later Possible | Belongs in SearchClarity / Customer Layer | Notes |
|---|---|---|---|---|
| Public video page metadata | Yes | Yes | No | Best candidate, with terms-aware handling. citeturn21view3turn9view0 |
| Public channel page metadata | Yes | Yes | No | Same. citeturn21view4turn9view0 |
| Public playlist metadata | Yes | Yes | No | Public-only. citeturn21view5turn9view0 |
| Public YouTube search observation | Yes | Yes | No | Time/context bound. citeturn20view0 |
| Public Google video SERP observation | Yes | Yes | No | Strong for cross-check. citeturn19view0turn2view4 |
| Public comments | Usually no | Maybe under very narrow rule | Possibly | Privacy/user-ID concerns. citeturn21view0turn8view3 |
| OAuth-authorized YouTube account data | No | Maybe | Yes | Private. citeturn8view2turn20view0 |
| YouTube Analytics data | No | Maybe | Yes | Private creator/customer performance data. citeturn14view3 |
| Owner-internal channel analytics | No | Maybe | Yes | Same. citeturn14view2 |
| Third-party YouTube SEO estimates/scores | Yes, as testimony only | Yes | Sometimes | Store as provider output, not truth. citeturn23search1turn27search0 |
| Manual screenshots | Yes, sparingly | Yes | No | Evidence support only. citeturn30view0 |
| Scraped/automated direct collection from YouTube pages | No | No recommendation | No | Avoid absent explicit permission. citeturn30view0 |
| Derived claims | No | No | No | LLM interprets at read time; DB should store observations, not conclusions. Logical consequence of doctrine and API metric restrictions. citeturn8view3 |

**Appendix C — Tool Metrics Table**

| Tool / Source | Direct Observation | Provider-Normalized Observation | Public Platform Metadata | Creator-Authorized Private Data | Proprietary Estimate | Proprietary Score / Model Output | Unknown |
|---|---|---|---|---|---|---|---|
| YouTube Data API public resources | Yes | No | Yes | Sometimes, if authorized | No | No | No citeturn12search1turn20view0 |
| YouTube Analytics / Reporting | No | No | No | Yes | No | No | No citeturn14view3turn17search3 |
| DataForSEO YouTube SERP | Yes, provider-observed | Yes | Yes | No | No | No | Some field provenance still provider-dependent. citeturn2view0turn4view0 |
| vidIQ | Some | Yes | Yes | Some | Yes | Yes | Some methodology unclear. citeturn26search2turn26search5 |
| TubeBuddy | Some | Yes | Yes | Some | Yes | Yes | Some methodology unclear. citeturn23search1turn23search9 |
| Morningfame | Some | Yes | Yes | Yes | Yes | Yes | Yes. citeturn28search6turn28search5 |
| Social Blade | Some | Yes | Yes | No in public mode | Yes | Yes | Yes. citeturn24search2turn24search7 |
| Semrush Keyword Analytics for YouTube | No obvious direct platform feed to user | Yes | No | No | Yes | Yes / competitive rate | Licensed-source specifics beyond disclosed statement remain limited. citeturn27search0 |
| Ahrefs YouTube keyword tool | No obvious direct platform feed to user | Yes | No | No | Yes | Yes | Clickstream method stated, full methodology not public. citeturn27search1 |
| Keyword Tool | Autocomplete observation for suggestions | Yes | No | No | Yes | Competition scoring present | Some modeling details limited. citeturn25search0turn27search2 |

**Appendix D — Safe vs Unsafe Claim Matrix**

| Evidence Category | Safe Claim | Unsafe Claim | Caveat |
|---|---|---|---|
| Public metadata via official API | “Official API returned X at time Z.” | “X is permanently true.” | Refresh/change risk. citeturn21view3turn9view0 |
| YouTube search result observation | “Returned in the result set under request C.” | “Ranks #1 on YouTube.” | Request-context bound. citeturn20view0 |
| Google video SERP observation | “Google showed the result.” | “YouTube ranked the result.” | Different surface. citeturn19view0 |
| Creator analytics | “Authorized analytics showed metric X.” | “The public ecosystem observed metric X.” | Private/internal data. citeturn14view3 |
| Third-party keyword volume | “Provider estimated demand as X.” | “YouTube search volume is exactly X.” | Estimate/model output. citeturn27search0turn27search1turn27search2 |
| Third-party opportunity/competition score | “Provider assigned score X.” | “This keyword is objectively easy.” | Score is tool logic. citeturn23search1turn23search9 |
| DataForSEO YouTube position | “DataForSEO observed rank_absolute P.” | “Official YouTube rank is P everywhere.” | Provider observation. citeturn4view3turn33view0 |