# Marketplace Evidence Ceiling Research Report for The Observatory

## Executive Summary

The evidence ceiling for marketplace visibility observation is set by two hard boundaries: (1) what each surface exposes publicly vs. behind seller login, and (2) what each platform's Terms and API license permit you to store, cache, and redistribute. For The Observatory — which stores observations while the connected LLM interprets at read time — the safest early candidates are **public, external, point-in-time observations of listings, gigs, product pages, pins, and search-result positions**, captured manually with full provenance and public/private classification attached. Everything that touches seller-private analytics, orders, customers, messages, or Admin-scoped data belongs in SearchClarity / the customer engagement layer, not The Observatory.

Four findings drive every recommendation below:

1. **APIs are mostly seller-authorization gates, not observation firehoses.** Etsy, Pinterest, Shopify Admin, Fiverr (no public API at all), TikTok Shop, and Google Merchant Center all require OAuth/seller authorization for anything beyond thin public data. An API token typically returns *that seller's own* data — which is customer-private and out of scope by default.

2. **Storage and caching are contractually limited even for legitimately accessed data.** Etsy's API Terms cap how stale displayed data may be and forbid caching "longer than is reasonably necessary." Pinterest's developer guidelines bar storing API data except campaign analytics. These rules make an "archive everything from the API" model non-compliant.

3. **Scraping is broadly prohibited by Terms across all four core surfaces.** Etsy, Fiverr, and Pinterest explicitly prohibit scraping; Shopify's `/products.json` is technically open but its Terms and per-store robots.txt constrain automated collection. The Observatory should not build a scraping system.

4. **Marketplace SEO tool metrics are provider testimony, not marketplace truth.** eRank, Marmalead, EverBee, Sale Samurai, Alura, etc. produce *estimates* and *model outputs* (search "volume," estimated sales/revenue). Etsy does not publish sales or true search-volume figures, so every such number is a modeled inference. Observatory may store these only as "Provider X estimated Y on date Z," never as facts about demand.

**Decision-ready surface status:** Etsy = safe candidate for public manual observation + narrow public-API listing/shop reads (with caching limits); Pinterest = public manual observation + Trends screenshots safe, API storage restricted; Shopify = public storefront-page observation safe, Admin/Storefront-API and `/products.json` bulk collection cautious/avoid; Fiverr = public manual observation only, no API, automation risky/avoid. Tool estimates = store as provider testimony only.

## Confidence and Source Quality

- **High confidence (official primary sources, quoted):** Etsy API Terms of Use (last updated Jun 16, 2025), Etsy Search/Advertisement/Recommendation Ranking Disclosures, Etsy Open API v3 docs, Pinterest Developer Guidelines and Terms of Service, Pinterest Trends business help, Shopify API License and Terms of Use, Shopify Storefront/Admin API and protected-customer-data docs, Google Merchant/Content API terms, Fiverr Community Standards and Terms of Service.
- **Medium confidence (vendor self-description + independent review corroboration):** eRank/Marmalead/EverBee/Sale Samurai feature and pricing claims; EverBee's ~80% accuracy claim is vendor-stated and corroborated as directional-only by multiple independent reviewers.
- **Lower confidence / flagged:** Third-party "how to scrape X" blogs (used only to establish that scraping is technically possible and where anti-bot friction sits, NOT as endorsement); some tool comparison sites are affiliate-driven and should be treated as marketing.
- **Explicitly unverified:** Fiverr has no published developer/API documentation; all "Fiverr API" offerings found are third-party scrapers, not official. Any Fiverr programmatic access claim is **Unclear — needs confirmation** against Fiverr directly.

## Source List

- Etsy API Terms of Use — https://www.etsy.com/legal/api/ (last updated Jun 16, 2025; accessed Jul 8, 2026)
- Etsy Open API v3 documentation — https://developers.etsy.com/documentation/ (accessed Jul 8, 2026)
- Etsy Authentication / Quick Start — https://developers.etsy.com/documentation/essentials/authentication/ ; https://developers.etsy.com/documentation/tutorials/quickstart/
- Etsy Open API v3 FAQ (rate limits) — https://developers.etsy.com/documentation/migration/faq/
- Etsy Search, Advertisement & Recommendation Ranking Disclosures — https://www.etsy.com/legal/policy/search-advertisement-recommendation/899478564529
- Etsy Terms of Use ("Don't Steal Our Stuff" anti-scraping) — https://www.etsy.com/legal/terms-of-use/
- Pinterest Developer Guidelines — https://policy.pinterest.com/en/developer-guidelines
- Pinterest Terms of Service — https://policy.pinterest.com/en/terms-of-service
- Pinterest API access tiers / auth — https://developers.pinterest.com/docs/getting-started/set-up-authentication-and-authorization/ ; https://developers.pinterest.com/docs/key-concepts/access-tiers/
- Pinterest Trends (business help) — https://help.pinterest.com/en/business/article/pinterest-trends
- Shopify API License and Terms of Use — https://www.shopify.com/legal/api-terms
- Shopify protected customer data — https://shopify.dev/docs/apps/launch/protected-customer-data
- Shopify Storefront vs Admin API — https://www.shopify.com/partners/blog/storefront-api-learning-kit
- Shopify robots.txt editing / agentic storefronts — https://help.shopify.com/en/manual/promoting-marketing/seo/editing-robots-txt
- Google Content API for Shopping terms — https://developers.google.com/shopping-content/guides/terms ; Merchant API — https://developers.google.com/merchant/api
- Fiverr Terms of Service — https://www.fiverr.com/legal-portal/legal-terms/terms-of-service
- Fiverr Community Standards — https://help.fiverr.com/hc/en-us/articles/37333125829649-Our-Community-Standards
- TikTok Shop Partner/Seller API — https://partner.tiktokshop.com/docv2/page/seller-api-overview
- eRank — https://erank.com/ ; Marmalead, EverBee (https://everbee.io/), Sale Samurai, Alura, Koalanda (vendor sites + independent reviews)

## 1. Marketplace / Surface Overview

Each surface is treated as an instrument: it emits some public signal, gates some private signal behind login, and imposes Terms on what may be collected and stored.

| Surface | Public Search/Discovery Data | Seller Private Data | Official API? | Export? | Biggest Risk |
|---|---|---|---|---|---|
| **Etsy** | Listing pages, shop pages, reviews, prices, favorites counts, search-result ordering (all visible without login) | Shop Stats/analytics, orders/receipts, buyer data, traffic sources | Yes — Open API v3 (public listing/shop reads via app key; private data via seller OAuth) | Seller can export some data; API returns seller-authorized data | Caching/storage limits in API Terms; scraping prohibited; analytics/ML use of API content prohibited |
| **Fiverr** | Gig pages, seller profiles, ratings, review counts, price tiers, search-result ordering | Orders, buyer messages, earnings, seller analytics | **No official public API** (affiliate API only; general API Unclear — needs confirmation) | Not via official API | Terms explicitly prohibit scraping and ranking manipulation; anti-bot (Cloudflare); account bans |
| **Shopify** | Storefront product/collection pages, prices, variants, schema.org markup, `/products.json` (open by default) | Admin data: orders, customers, analytics, inventory internals | Yes — Storefront API (public, token) + Admin API (private, OAuth) | Merchant can export; Admin API returns merchant-private data | Shopify is a platform, not one marketplace; Admin/customer data is merchant-private; `/products.json` bulk collection constrained by Terms/robots.txt |
| **Pinterest** | Pins, boards, profiles, search results, Pinterest Trends (relative interest, US/UK/CA) | Account Analytics (impressions, saves, clicks), audience insights | Yes — API v5 (OAuth, trial→standard review) | Account owner sees analytics; API returns authorized account data | Developer guidelines bar storing API data except campaign analytics; scraping prohibited |
| **Amazon Handmade** | Product listings, prices, ratings, Best Seller ranks | Seller Central sales/analytics | Via Amazon SP-API (seller-authorized) | Seller export | Strict Terms; SP-API is seller-scoped |
| **eBay** | Listings, prices, sold/completed data (limited), ratings | Seller performance dashboards | Yes — Browse/Marketplace APIs | Some | API terms restrict storage/redistribution |
| **Google Shopping / Merchant Center** | Public Shopping results (product listings) | Merchant Center product feed, performance | Merchant API / Content API (merchant-authorized) | Merchant-controlled | API returns *your own* merchant data; not competitor intelligence |
| **TikTok Shop** | Product cards, prices, shop rating/review counts, sold counts | Orders, seller analytics | Yes — Seller/Partner API (OAuth, main account) | Seller export | API is seller-scoped; public data via unofficial scrapers only |
| **Instagram Shopping** | Public shop/product tags | Account insights | Graph API (business-authorized) | Limited | Heavily authorization-gated |
| **YouTube Shopping** | Public product shelves on videos | Channel commerce analytics | Partial (Data API + Shopping affiliate) | Limited | Authorization-gated |
| **Reddit discovery** | Public posts/comments, subreddit discussion | — | Yes — Reddit API (paid tiers, terms tightened) | Limited | API pricing/terms; content licensing restrictions |

**Interpretation:** The pattern is uniform — *public discovery surface is observable; private seller data sits behind OAuth and is customer-private by default; APIs are authorization gates, not open observation feeds.* Only Shopify's `/products.json` and Etsy's public listing/shop reads offer meaningful un-authenticated structured data, and both carry storage/collection constraints.

## 2. Etsy Evidence Ceiling

**Publicly visible (no login):** listing pages (title, tags visible in HTML, price, images, description, processing time, reviews, favorites count, shop name), shop pages (policies, announcement, review aggregate, sales count where shown), and **search-result ordering** for a query. Etsy's own **Search, Advertisement & Recommendation Ranking Disclosures** page is the authoritative description of how organic ranking, ads, and recommendations work: organic search runs in two phases — "query matching" then ranking by listing quality score, recency, CSR (Context Specific Ranking), shipping price, and other signals; Etsy states "Etsy does not offer sellers a higher ranking placement in organic search results in exchange for any compensation or fee," and that Star Seller and running Etsy Ads do not change organic ordering.

**Behind seller login:** Shop Stats/analytics, traffic sources, orders/receipts, buyer data, billing.

**Etsy Open API v3 (verified Jul 8, 2026):**
- Every request requires an app **API key** (`x-api-key`); as of Jan 18, 2026 the header must carry keystring:shared_secret.
- **Public, app-key-only reads:** `findAllListingsActive` (`GET /v3/application/listings/active`) is a marketplace-wide listing-search endpoint requiring only the app API key, not seller OAuth. It supports keywords, sort, price, taxonomy, and shop-location parameters. Also app-key-only: listings by shop, individual listings, public shop data, seller taxonomy, and the ping test endpoint.
- **Seller-OAuth-required (scoped):** receipts/orders (`transactions_r`), listing create/update/delete (`listings_w`/`listings_d`), inventory writes, buyer email (`email_r`), shipping addresses. Access tokens expire in 1 hour; refresh tokens last 90 days.
- **Default rate limit:** per Etsy's Open API v3 FAQ, verbatim: "By default, an Etsy app — making public requests authenticated with its API key — can make 10,000 requests per 24-hour period, with a limit of 10 queries per second." Etsy's Rate Limits doc adds that these operate on a "progressive Sliding Window Rate Limiting Algorithm" over a rolling 24-hour window (not a fixed midnight cycle). Exceeding 3 million calls/day requires the Enterprise Tier.
- **No native webhooks** — polling only.

**What Etsy Terms say about storage, redistribution, automation, scraping (API Terms of Use, last updated Jun 16, 2025):**
- **Caching/staleness (Section 5, "Display of Data"), verbatim:** "You will not display listing content more than six (6) hours older than the corresponding information on the Etsy Site or the Etsy Apps. You will not display any other Etsy content more than twenty-four (24) hours older than the content displayed on the Etsy Site or the Etsy Apps. Once you've accessed, stored, or displayed Etsy content, you will not cache or store it longer than is reasonably necessary to provide service to your Application's users."
- **Analytics/ML prohibition (Prohibited Behavior item 25), verbatim:** "Use the Etsy API to collect, scan, or otherwise request Etsy content for purposes of analytics, machine learning, training artificial intelligence models, licensing, or content removal, unless expressly authorized in writing by Etsy."
- **Internal-systems prohibition (item 19), verbatim:** "Use the Etsy API in a manner unrelated to Etsy Member activity, such as to obtain information about Etsy's internal systems and processes."
- **Automated/scraping prohibition (item 24), verbatim:** "Use or promote the use of automated systems or browser extensions to access, analyze, or scrape the Etsy Site, the Etsy API or any Etsy data, including but not limited to Etsy listings, shops, or user profiles, unless expressly authorized in writing by Etsy."
- **General Terms of Use:** "You agree not to crawl, scrape, or spider any page of the Services… without our express permission. If you want to use our API, please follow our API Terms of Use."
- **Member data:** developers act as a service provider to the seller; member personal data may only be processed to fulfill services under an Application agreement with that seller.

**Critical implication for Observatory:** Even Etsy's *public* API content cannot be lawfully warehoused for analytics/ML, and cannot be displayed stale beyond 6/24-hour windows. This makes an Observatory "store the API response and interpret later" pattern non-compliant for Etsy API data specifically. The compliant path is **manual, human-captured point-in-time observation** (screenshot/snapshot of a public page or search result), classified as public evidence with a timestamp — analogous to a researcher's field note, not an automated data pipeline.

**Marketplace SEO tools around Etsy:** eRank, Marmalead, EverBee, Sale Samurai, Alura, EtsyHunt, Koalanda — all provide estimated keyword search volume, estimated sales/revenue, and competition scores. None have access to Etsy's private sales data; all are modeled estimates.

| Evidence Type | Public/Private | Store in Observatory Now? | Later Possible? | Notes / Conditions |
|---|---|---|---|---|
| Public listing snapshot (manual) | Public | Candidate — yes | Yes | Timestamp + URL + public flag; treat as point-in-time field note |
| Public shop snapshot (manual) | Public | Candidate — yes | Yes | Same conditions |
| Public search-result observation (manual, query+position) | Public | Candidate — yes | Yes | Record query, filters/sort, locale, device, date, observed position |
| Seller-authorized private stats (Shop Stats) | Private | **No** | Only with explicit seller authorization + SearchClarity layer | Customer-private by default |
| API-returned listing/shop data (public reads) | Public-origin | **No (default)** | Cautious — caching limits + analytics/ML prohibition | 6/24-hr staleness cap; cannot warehouse for analytics |
| API-returned seller data (OAuth) | Private | **No** | SearchClarity only, with authorization | Service-provider obligations attach |
| Third-party tool estimate | Provider testimony | Candidate — as testimony only | Yes | Store as "Provider X estimated Y on date Z" |
| Manual screenshot/capture | Public | Candidate — yes | Yes | Preferred provenance artifact |
| Scraped data | Public-origin, prohibited method | **No** | **No** | Scraping violates Etsy Terms |

**Default caution honored:** Customer Etsy Stats / seller-private analytics are not stored in Observatory by default.

## 3. Fiverr Evidence Ceiling

**Publicly visible:** gig pages (title, description, package/price tiers, delivery time, rating, review count, seller level), seller profiles (bio, skills, languages, country, member-since, gig list), and search-result ordering for a query/category.

**Behind login:** orders, buyer/seller messages, earnings, private seller analytics/insights.

**Official API:** Fiverr does **not** publish a general-purpose public developer API. There is an **affiliate API** (for promoting gigs, requires affiliate approval). Every "Fiverr API" surfaced in research is a **third-party scraper** (Apify actors, PyPI `fiverr-api`, ScrapingBee, Piloterr, Netrows) that extracts data from Fiverr pages — not an official, sanctioned channel. Any claim of official Fiverr programmatic marketplace access is **Unclear — needs confirmation**.

**Terms on automation/scraping/reuse (Fiverr Community Standards / Terms of Service):** Fiverr prohibits "Any attempts to access the platform through unauthorized methods, affect and manipulate the Fiverr ranking system, send artificial web traffic to Gigs… scrape data from the platform, or undermine the security and integrity of our marketplace in any way." Fiverr also requires users to respect third parties' Terms. Fiverr uses automated + human moderation and Cloudflare-class anti-bot; scraping risks IP/account bans.

**Can public gig snapshots be captured safely?** A human viewing a public gig page and taking a screenshot as a point-in-time observation is low-risk and analogous to normal browsing. **Automated** collection of the same data is prohibited by Terms. The distinction is method, not the data.

| Evidence Type | Public/Private | Store in Observatory Now? | Later Possible? | Notes / Conditions |
|---|---|---|---|---|
| Public gig snapshot (manual) | Public | Candidate — yes | Yes | Timestamp + URL + public flag |
| Public seller/profile snapshot (manual) | Public | Candidate — yes | Yes | Avoid collecting personal data beyond what's publicly displayed |
| Public search-result observation (manual) | Public | Candidate — yes | Yes | Record query/category, sort, locale, date, observed position |
| Seller-private analytics | Private | **No** | SearchClarity only, with authorization | Out of scope by default |
| Order/customer/message data | Private | **No** | **No** | Never in Observatory |
| Manual screenshot/capture | Public | Candidate — yes | Yes | Preferred artifact |
| Third-party estimate | Provider testimony | Cautious — testimony only | Yes | No authoritative Fiverr metrics exist publicly |
| Scraped data | Prohibited method | **No** | **No** | Violates Fiverr Terms |

**Default caution honored:** Fiverr orders, customers, messages, and private seller analytics belong outside Observatory.

## 4. Shopify Evidence Ceiling

Shopify is uniquely dual-natured: it is **both a platform and the merchant's own storefront**. A Shopify-powered storefront is the merchant's website — it is not a shared marketplace like Etsy. This changes the boundary model.

**Publicly observable from a Shopify storefront:** product pages, collection pages, prices, variants, availability, images, structured data / schema.org (JSON-LD) markup, and — by Shopify's default — the `/products.json`, `/collections.json`, and per-product `.json` endpoints, which return structured catalog data (titles, variants, prices, SKUs, images, created/updated timestamps) without authentication.

**Private merchant data (Admin):** orders, customers, analytics, inventory internals, draft/unpublished products.

**Storefront API vs Admin API:**
- **Storefront API** — public, unauthenticated (public access token, safe client-side), primarily read-only: products, variants, collections, store content, plus cart/checkout. "Any data exposed by the Storefront API can be seen by any visitor to the store."
- **Admin API** — merchant-private, OAuth-scoped: full read/write to products, orders, customers, inventory, shipping. **Protected customer data** requirements apply: customer-related fields are redacted by default and require an approval process and data-protection commitments (retention limits, encryption).

**Terms on API use and storage (Shopify API License and Terms of Use):** Developers are bound by the Partner Program Agreement and API Terms; must present merchants a compliant privacy policy; must secure Merchant Data; Shopify may audit. Per the Jan 29, 2026 update (effective Feb 27, 2026), "Merchant Data and Customer Data (including derived or aggregated data) may not be used for development or training of AI or machine learning systems unless you have explicit written consent from Shopify (or from the merchant, for merchant-specific data)," and Shopify "clarified existing scraping and mining restrictions." The `/products.json` endpoint, while open by default, is subject to per-store robots.txt and the storefront's own Terms; bulk automated collection is unauthenticated-rate-limited (commonly ~2 req/s per store) and is where anti-bot/legal friction concentrates.

**How Observatory should treat Shopify differently from Etsy/Fiverr:** A Shopify storefront is analogous to observing any merchant's public website, not a marketplace with cross-seller ranking. There is **no unified Shopify "search" surface** to observe rankings across merchants — discovery of Shopify products happens off-platform (Google, Shopping, social). So Shopify evidence for Observatory is about **individual public product/page snapshots and their structured markup**, not marketplace-position observation.

| Evidence Type | Public/Private | Store in Observatory Now? | Later Possible? | Notes / Conditions |
|---|---|---|---|---|
| Public storefront page snapshot (manual) | Public | Candidate — yes | Yes | Merchant's own public website; timestamp + URL |
| Public product/collection metadata (visible on page) | Public | Candidate — yes | Yes | Record what was displayed |
| schema.org / JSON-LD on page | Public | Candidate — yes | Yes | Strong provenance; record fields exposed on date |
| `/products.json` structured data | Public-origin | Cautious | Cautious | Open by default but bulk collection constrained by Terms/robots.txt/rate limits; prefer manual single-page capture |
| Storefront API data | Public-origin, token | Cautious | Cautious | Merchant grants token; treat as merchant-facing |
| Admin API product data | Merchant-private | **No** | Only via merchant authorization → SearchClarity | Not Observatory |
| Admin API order/customer data | Merchant-private / protected | **No** | **No** | Protected customer data; never Observatory |
| Shopify analytics | Merchant-private | **No** | **No** | Never Observatory |
| Customer exports | Private | **No** | **No** | Never Observatory |
| Manual screenshot/capture | Public | Candidate — yes | Yes | Preferred artifact |

**Default caution honored:** Shopify customer/order/analytics/Admin data is merchant-private and not stored in Observatory by default.

## 5. Pinterest Evidence Ceiling

**Publicly visible:** pins (image, title, description, destination URL, board), boards, profiles, search results, and **Pinterest Trends** (trends.pinterest.com and inside business accounts). Pinterest's business help states verbatim that the tool "displays a historic view (up to the last two years) of the top search, save, and shopping trends across different regions and countries," currently limited to US/UK/CA. Crucially, Pinterest shows **normalized relative interest, not absolute counts**: "Pinterest normalizes search volume by only considering the ratio of searches for each trend to the total number of searches that happened on our platform during the same time frame. To make comparisons between terms easier, the highest point of the search term is indexed to 100, and the lowest point is indexed to 0 on each plot." **Pinterest does not publish absolute search-volume counts**, so any tool showing a "Pinterest search volume" number is an estimate (Keywords Everywhere, for example, discloses it substitutes Google volume as a proxy).

**Behind account authorization:** Pinterest Analytics (impressions, saves, pin clicks, outbound clicks, audience insights) — visible to the account owner and to authorized apps.

**Pinterest API (v5):** OAuth 2.0; apps start at **Trial** access (created pins/boards visible only to creator as sandbox entities) and must pass a **video-demo review** to reach **Standard** access. Read scopes (e.g., `pins:read`, `boards:read`, `trends_read`) vs write scopes. Rate limits are per-category.

**Terms on automated collection, storage, redistribution (Pinterest Developer Guidelines):**
- **Storage restriction:** developers "cannot store information accessed through Pinterest APIs except for campaign analytics. Apps must call the API each time you need to access information." This directly forbids the warehouse-the-API pattern.
- **No scraping:** "no automated scraping or extraction except where Pinterest explicitly permits."
- **No resale/sharing:** "Don't share or sell information from our API with a third party."
- Ads-data use is restricted to serving/evaluating Pinterest ads; data may not be used to target ads off-platform.

**Relevance to Etsy/SearchClarity visibility work:** Pinterest is a major upstream discovery/traffic source for Etsy and DTC/Shopify sellers, and its Trends tool is a legitimate *leading indicator* of seasonal demand (search interest often rises weeks/months before purchase). For Observatory, the safe, high-value evidence is **manual capture of public Pinterest Trends curves and search-result observations** — recorded as "Pinterest Trends showed relative interest pattern X for term Y in region Z on date D," never as absolute volume or guaranteed traffic.

| Evidence Type | Public/Private | Store in Observatory Now? | Later Possible? | Notes / Conditions |
|---|---|---|---|---|
| Public pin snapshot (manual) | Public | Candidate — yes | Yes | Timestamp + URL |
| Public board/profile snapshot (manual) | Public | Candidate — yes | Yes | Same |
| Public search/trend observation (manual) | Public | Candidate — yes | Yes | Record query, region, date |
| Pinterest Trends data (manual capture) | Public | Candidate — yes | Yes | Record as relative/normalized (0–100); note US/UK/CA limit |
| Authorized account analytics | Private | **No** | SearchClarity only, with authorization | Owner-private |
| API-returned data | Mixed | **No** | **No (storage barred except campaign analytics)** | Guidelines forbid storing API data |
| Manual screenshot/capture | Public | Candidate — yes | Yes | Preferred artifact |
| Scraped data | Prohibited method | **No** | **No** | Violates guidelines |

**Default caution honored:** Private Pinterest Analytics is not stored in Observatory by default.

## 6. Marketplace SEO Tools

**Doctrine:** A marketplace SEO tool's score is **an observation of that tool's model output**, not a fact about marketplace demand. Etsy publishes neither sales data nor true search volume, so every "search volume," "estimated sales," or "revenue" figure is a proprietary estimate or model output. Store as provider testimony with attribution and date.

| Tool | Marketplace(s) | Metrics | Metric class | Export/API | Terms note | Pricing (approx.) | Strong / Weak |
|---|---|---|---|---|---|---|---|
| **eRank** | Etsy (+ Amazon, eBay trend data, Pinterest via search) | Keyword search volume indicators, competition, CTR, top-100 listing analysis, estimated shop sales, rank tracking | Proprietary estimate + provider-normalized observation; some data from Google Keyword Planner | CSV export | Third-party; connects to seller's Etsy via authorization | Free; Basic ~$5.99/mo; Pro ~$9.99/mo; Expert ~$29.99/mo | Strong: breadth at low price, free plan. Weak: relative (high/med/low), not exact volume; monthly data freshness |
| **Marmalead** | Etsy | Estimated searches, engagement, competition, seasonal trends, listing optimization | Proprietary estimate + model output | PDF only (no CSV) | Third-party | ~$19/mo ($15.83/mo annual); 14-day trial | Strong: engagement scoring, "Storm" tag tool. Weak: reviewers flag possibly inaccurate volume; higher price |
| **EverBee** | Etsy (Chrome extension + web) | Estimated monthly sales/revenue, conversion rate, keyword volume, shop analytics | Proprietary estimate (extrapolated from public signals) | CSV export | Uses official Etsy API (read-only) per vendor; connects seller account | Free (Hobby, hides revenue); Growth ~$19.99–29.99/mo; Business ~$69–99/mo | Strong: product research, sales estimates. Weak: estimates drift on low-volume listings; annual auto-renew complaints |
| **Sale Samurai** | Etsy | Keyword discovery, estimated search volume, tag analysis | Proprietary estimate | No export | Third-party; Chrome extension on Etsy | ~$9.99/mo ($8.30/mo annual); 3-day trial | Strong: keyword ideation. Weak: shallow analytics; reviewers call data less fresh |
| **Alura** | Etsy | Product research, estimated sales/trends, keyword research, listing optimization, review AI | Proprietary estimate + model output | CSV/Excel | Third-party; Chrome extension | Free tier; Growth ~$19.99/mo (annual); Pro ~$49.99/mo | Strong: product research, AI review analysis. Weak: SEO depth |
| **EtsyHunt** | Etsy (+ Amazon Handmade search) | Product DB, competition, estimated sales, keyword | Proprietary estimate | Some | Third-party | ~$3.99/mo entry | Strong: large product DB, cheap. Weak: interface, occasional inaccuracy |
| **Koalanda** | Etsy | Keyword research, competitor analysis, listing optimization, SEO alerts, listing backups | Proprietary estimate + provider-normalized | — | Third-party | — | Strong: real-time keyword + backups. Weak: less established |

**EverBee accuracy — provider testimony, quoted:** EverBee's own site states verbatim: "While Etsy doesn't directly disclose sales data, EverBee utilizes a sophisticated algorithm incorporating various metrics. Our algorithm maintains an average accuracy rate of approximately 80%." This is a **vendor claim, not a measured fact**; independent reviewers corroborate it as directional only, noting estimates drift on low-volume listings. EverBee's own homepage is internally inconsistent about its database size, stating both "Search 170M+ listings and 50M+ keywords" and "Search and filter over 206 million Etsy products" — a useful reminder that even a tool's self-reported scale figures are testimony, not verified fact.

**Metric classification key:** "search volume" = proprietary estimate/model output; "estimated sales/revenue" = proprietary estimate (extrapolated); "top-100 listing analysis" = provider-normalized observation of public listings; "seller-connected shop data" = seller-authorized private data (out of Observatory scope). Some tools (EverBee, InsightAgent) claim daily/API-based freshness; eRank/Marmalead rely more on Google Keyword Planner-derived data with monthly updates — differences that matter for interpretation but do not change the "testimony not truth" doctrine.

## 7. Public vs Private Evidence Boundary

| Category | Store in Observatory Now? | Later Possible? | Belongs in SearchClarity/customer layer? | Notes |
|---|---|---|---|---|
| Public marketplace surface data (listings, gigs, pins) | Yes — candidate | Yes | No (unless customer's own) | Manual point-in-time capture preferred |
| Public merchant/storefront page data (Shopify) | Yes — candidate | Yes | No | Merchant's own public site |
| Public search-result observation (query + position) | Yes — candidate | Yes | No | Highest-value visibility evidence |
| Seller-authorized private analytics | No | Only with explicit authorization + overlay ruling | Yes | Customer-private by default |
| Customer/order/message data | No | No | Yes | Never in Observatory |
| Platform API data | Cautious/No | Depends on platform terms | Sometimes | Etsy caching limits; Pinterest storage bar; treat per-surface |
| Third-party tool estimates | Yes — as provider testimony | Yes | No | Attribute to provider + date; never as fact |
| Manual screenshots | Yes — candidate | Yes | No | Preferred provenance artifact |
| Scraped/automated collection | No | No | No | Prohibited across core surfaces |
| Derived claims (LLM interpretation) | No (not stored as observation) | Read-time only | Promote accepted conclusions to consumer | The astronomer interprets; the telescope stores observations |

**Default doctrine honored:** Public external observations are candidates for Observatory; customer/seller-private data belongs outside Observatory unless a future owner ruling creates strict overlay/internal-scope rules.

## 8. Terms, Automation, Scraping, and Capture Risk

| Surface | API Allowed? | Scraping Risk | Storage Risk | Report/Redistribution Risk | Manual Capture Risk | Notes |
|---|---|---|---|---|---|---|
| **Etsy** | Yes (public reads via app key; private via OAuth) | High — scraping explicitly prohibited | High — 6/24-hr staleness cap; analytics/ML use of API content prohibited; cache no longer than reasonably necessary | Medium-High — member data reuse restricted; trademark disclaimer required | Low — human viewing/screenshot of public page is normal browsing | Strongest documented constraints of the four |
| **Fiverr** | No official general API | High — scraping explicitly prohibited; anti-bot | Unclear — no API terms to govern stored data; general web-content caution | High — Terms bar unauthorized access & ranking manipulation | Low — manual public view/screenshot | No official channel; treat automation as off-limits |
| **Shopify** | Yes (Storefront public; Admin private) | Medium — `/products.json` open but Terms/robots.txt/rate limits constrain bulk collection; scraping/mining restrictions clarified | Medium — Merchant/Customer Data (incl. derived/aggregated) barred from AI/ML training without consent | Medium — Merchant Data protections; protected customer data | Low — public storefront is merchant's own site | Per-store robots.txt varies |
| **Pinterest** | Yes (v5 OAuth; trial→standard review) | High — scraping prohibited except where permitted | **Very High — API data may not be stored except campaign analytics** | High — no selling/sharing API data | Low — manual public/Trends capture | Storage bar is the sharpest edge |
| **Google Merchant/Shopping** | Yes (Merchant/Content API, merchant-authorized) | N/A (returns your own merchant data) | Governed by Google API ToS | Medium | Low — public Shopping results viewable | API is not competitor-intelligence |
| **TikTok Shop** | Yes (Seller/Partner API, OAuth main account) | High — public data only via unofficial scrapers | Governed by API terms; seller-scoped | High | Low — manual public view | Research API separate, approval-gated |
| **eBay** | Yes (Browse/Marketplace APIs) | Medium | API terms restrict storage/redistribution | Medium | Low | Confirm current Browse API terms — needs confirmation |
| **Amazon Handmade** | Via SP-API (seller-authorized) | High | Strict | High | Low | Seller-scoped |
| **Reddit** | Yes (paid API tiers) | High | API terms/licensing restrictions | High | Low | Terms tightened; confirm current — needs confirmation |

**Cautious-language rule:** Where a surface's storage/redistribution position is not explicitly documented for Observatory's use case (notably Fiverr, eBay Browse API specifics, Reddit current terms), the correct status is **Unclear — needs confirmation** rather than an assumption of permission.

## 9. Evidence and Provenance Fit

The Observatory needs provenance-complete evidence. Support for each need, per surface:

| Evidence Need | Etsy | Fiverr | Shopify | Pinterest | Notes |
|---|---|---|---|---|---|
| Surface/provider name | Yes | Yes | Yes | Yes | Always record |
| Target listing/gig/product/profile URL | Yes | Yes | Yes | Yes | Stable identifiers vary (Etsy listing_id; Shopify handle; pin id) |
| Query / search term | Yes | Yes | N/A (no unified search) | Yes | Shopify has no cross-merchant search |
| Category/filter/sort context | Yes | Yes | Partial (collection) | Yes | Essential to interpret position |
| Location/language/device | Yes (affects results) | Yes | Partial | Yes (region drives Trends) | Record locale/device for reproducibility |
| Capture timestamp | Yes | Yes | Yes | Yes | Mandatory for all evidence |
| Rank/position if observed | Yes | Yes | N/A | Yes | Core visibility datapoint |
| Page/result snapshot | Yes | Yes | Yes | Yes | Manual capture preferred |
| Screenshot/hash | Yes | Yes | Yes | Yes | Strong provenance artifact |
| HTML/hash if allowed | Cautious (Etsy Terms) | Cautious (Fiverr Terms) | Cautious (public page ok; storage limits) | Cautious (storage bar) | Prefer screenshot over stored HTML where Terms restrict |
| API request/response metadata | Yes (public reads) | N/A (no API) | Yes (Storefront) | Yes (but storage barred) | Record that a call occurred even if payload not warehoused |
| Seller authorization status | Yes | Yes | Yes | Yes | Public vs authorized must be explicit |
| Public/private classification | Yes | Yes | Yes | Yes | Mandatory field |
| Rights/retention classification | Yes | Yes | Yes | Yes | Encode caching/retention limit per source |
| Source caveat | Yes | Yes | Yes | Yes | e.g., "normalized, not absolute" for Trends |

**Interpretation:** Etsy, Fiverr, and Pinterest fit a *search-position + snapshot* provenance model well. Shopify fits a *page + schema.org snapshot* model (no cross-merchant ranking). The retention/rights field is not optional — each source imposes different storage limits that must travel with the evidence so the LLM can caveat correctly at read time.

## 10. Safe and Unsafe Claim Language

| Evidence | Safe Wording | Unsafe Wording | Required Caveat |
|---|---|---|---|
| Etsy search position | "This Etsy listing appeared at observed position N in search results for query X, sort=relevancy, US locale, on date Y." | "This Etsy keyword gets exactly X searches." / "This listing ranks #1." | Position is a single point-in-time observation; Etsy ranking is personalized (CSR) and changes |
| Etsy keyword volume (tool) | "eRank estimated search volume for 'X' as [range/indicator] on date Y." | "This keyword gets X searches per month." | Provider estimate; Etsy publishes no true search volume |
| Etsy sales (tool) | "EverBee estimated this listing's monthly sales at ~N on date Y (vendor-claimed ~80% accuracy)." | "This listing sells N units/month." | Extrapolated estimate; drifts on low-volume listings |
| Fiverr gig | "This Fiverr gig displayed rating R across C reviews and price tier $P on date Y." | "This gig ranks #1 generally." / "This gig is the best." | Ratings/counts are as-displayed; ranking is query- and personalization-dependent |
| Shopify product page | "This Shopify product page exposed schema.org fields [list] and price $P on date Y." | "This product will sell." | Public page snapshot; no demand or sales inference |
| Pinterest Trends | "Pinterest Trends showed relative (normalized 0–100) interest pattern X for term T in region R on date Y." | "This term gets X Pinterest searches." / "This pin is guaranteed to drive traffic." | Normalized relative interest, not absolute volume; US/UK/CA only |
| Any tool score | "Provider P's model output for metric M was V on date Y." | "This marketplace score proves demand." | Model output = provider testimony, not marketplace fact |

**Rule:** Every stored observation is past-tense, dated, source-attributed, and scoped ("appeared," "displayed," "exposed," "estimated"). No predictive, superlative, or guarantee language enters the store; interpretation is the LLM's job at read time.

## 11. Recommended Observatory Handling

**Safe candidate material for Observatory (public, external, point-in-time):**
- Manual snapshots of public Etsy listings, shops, and search-result positions (query + sort + locale + date + position).
- Manual snapshots of public Fiverr gigs, profiles, and search-result positions.
- Manual snapshots of public Shopify storefront product/collection pages and their schema.org markup.
- Manual captures of public Pinterest pins, boards, search results, and Pinterest Trends curves (recorded as normalized/relative).
- Screenshots/hashes as the preferred provenance artifact for all of the above.

**Store only as provider testimony (attributed + dated):**
- eRank/Marmalead/EverBee/Sale Samurai/Alura/EtsyHunt estimates (volume, sales, competition scores).

**Belongs only in SearchClarity / customer layer:**
- Etsy Shop Stats, Fiverr seller analytics/orders/messages, Shopify Admin/analytics/orders/customers, Pinterest account Analytics — i.e., any seller-private/first-party data, even the customer's own.

**Needs explicit owner/customer authorization before any handling:**
- Any OAuth-scoped API pull of a customer's own marketplace data (Etsy seller OAuth, Shopify Admin, Pinterest account, TikTok Shop, Merchant Center) — and even then it routes to SearchClarity, not Observatory.

**Should be avoided entirely:**
- Any scraping/automated extraction of Etsy, Fiverr, or Pinterest (Terms-prohibited).
- Warehousing Etsy API content for analytics/ML (Terms-prohibited) or beyond caching windows.
- Storing Pinterest API data (barred except campaign analytics).
- Bulk automated `/products.json` harvesting as a system.

**Best early surface candidates:** **Etsy** (richest public listing/shop/search surface; well-documented ranking disclosures) and **Pinterest Trends** (legitimate public leading-indicator), both via **manual capture**. **Shopify public product-page + schema.org snapshots** are a solid third.

**Too risky / too private for early automation:** **Fiverr** (no API, scraping-prohibited, anti-bot), all **Admin/seller-authorized** surfaces, and any **API warehousing** pattern.

**M1/M3 research gates (what must be resolved before building):**
- M1 gate: confirm a *manual-capture* evidence model (human-in-the-loop screenshots/observations) is the default, since automated API/scraping paths are constrained or prohibited.
- M3 gate: define the retention/rights field so each observation carries its source's storage limit (Etsy 6/24-hr display cap; Pinterest no-store; Shopify no-AI-training).

**Future boundary/contracts:** a Marketplace Source Admission ruleset (per-surface allow/deny), a Claim-Safety Matrix (Section 10), and a Provider Cross-Check model (tool estimates cross-referenced against public observations, never merged into "truth").

## 12. Questions / Unknowns To Confirm

- **Fiverr:** Is there ANY official, sanctioned programmatic access beyond the affiliate API? **Unclear — needs confirmation** (no developer docs found).
- **eBay Browse API:** exact current storage/redistribution limits for observed listing data — **needs confirmation**.
- **Reddit API:** current pricing tier and content-licensing terms for discovery observation — **needs confirmation**.
- **Etsy "reasonably necessary" caching:** how does a point-in-time *observation snapshot* (vs. a live display cache) interact with the 6/24-hr display rule? Likely different (observation ≠ display of current data), but the owner should get a legal read before storing any Etsy API-origin payload. **Needs confirmation.**
- **Manual screenshots of public pages:** confirm the owner's risk tolerance/legal position on retaining screenshots of third-party public pages (generally low-risk as field notes, but confirm).
- **TikTok Shop / Instagram / YouTube Shopping:** depth of any *public* (non-authorized) observable surface — treat as authorization-gated until confirmed.

## 13. Decision Inputs For M1 Roadmap

- **The Observatory's marketplace evidence is fundamentally a manual-observation product, not an API/scraping product.** The Terms landscape forces this: APIs gate private data and restrict storage; scraping is prohibited. Design M1 around human-captured, provenance-complete public observations.
- **Public search-result position is the single highest-value, lowest-risk marketplace datapoint** (Etsy, Fiverr, Pinterest). Prioritize a clean schema-agnostic observation format: surface + query + sort/filter + locale/device + timestamp + observed position + snapshot.
- **Tool estimates are admissible only as provider testimony.** Build the admission rule so no tool number can be promoted to a "fact about demand."
- **The public/private classification and rights/retention fields are mandatory, not optional.** They are what let the LLM caveat correctly and what keep Observatory out of customer-database / ToS-risk territory.
- **Etsy and Pinterest Trends are the recommended first surfaces; Fiverr and all authorized/API-warehousing paths are deferred.**

## Appendix A — Surface Comparison Table
(See Section 1 table — public/private, API, export, and risk per surface.)

## Appendix B — Evidence Category Boundary Table
(See Section 7 table — store-now / later / SearchClarity per category.)

## Appendix C — Tool Metrics Table
(See Section 6 table — marketplace, metric class, export, terms, pricing, strengths/weaknesses.)

## Appendix D — Safe vs Unsafe Claim Matrix
(See Section 10 table — safe wording, unsafe wording, required caveat.)

---

### Decision Output — Recommended status by surface

- **Etsy** — *Safe candidate for public observation* (manual capture of public listings/shops/search positions). Public-API listing/shop reads are *allowed only through official API* with caching limits and an analytics/ML-storage prohibition — so **do not warehouse Etsy API content**. Seller stats = *customer-layer only*.
- **Pinterest** — *Safe candidate for public observation* (pins, boards, search, Trends via manual capture). API data = *do not store* (barred except campaign analytics). Account analytics = *customer-layer only*.
- **Shopify** — *Safe candidate for public observation* of storefront pages + schema.org (manual). `/products.json` and Storefront API = *cautious*. Admin/customer/analytics = *not recommended / customer-layer only*.
- **Fiverr** — *Safe only for manual public observation.* No official API. Automation = *risky / avoid*. Seller/order/message data = *not recommended*.
- **Google Merchant / TikTok Shop / Amazon Handmade / Instagram / YouTube Shopping** — *Allowed only as customer-layer/read-time overlay via seller authorization*; public observation limited. TikTok public data only via unofficial scrapers = *avoid automation*.
- **eBay / Reddit** — *Needs more research* on current API storage/redistribution terms before admission.

### Must know before M1 roadmap sequencing
That the marketplace-evidence model is manual-capture-first; automated API/scraping is constrained or prohibited across all four core surfaces.

### Must know before schema
The mandatory provenance fields: public/private classification; rights/retention limit per source; query/locale/position context; snapshot artifact.

### Must know before marketplace source admission
Per-surface allow/deny and storage rules: Etsy (no API warehousing; 6/24-hr caching caps), Pinterest (no API storage except campaign analytics), Shopify (no AI-training on merchant/customer data), Fiverr (no automation).

### Must know before first customer-facing marketplace report
The Claim-Safety Matrix (Section 10) — safe past-tense, dated, attributed wording; tool numbers labeled as provider estimates; no demand/guarantee claims.

### Must know before any automation
Whether the owner has explicit written authorization from the platform (Etsy/Pinterest/Shopify) and/or the customer — absent that, automated collection is off-limits across all four core surfaces.