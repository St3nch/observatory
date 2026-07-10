# SEO Tool Pricing and ROI Research Report for The Observatory

## Executive Summary
For The Observatory — an evidence-only observation system — the single most important finding is that **DataForSEO's pay-as-you-go API ($0.0006 per SERP in Standard queue, $50 minimum deposit, no subscription) can replace the majority of paid-subscription "witness" data that Ahrefs ($129+/mo for Lite), Semrush ($139.95+/mo for Pro), and most SERP tools charge a monthly rent for** — and should be treated as the default programmatic instrument once rights and cost gates are confirmed. DataForSEO's own SERP API pricing page confirms it "operates on a pay-as-you-go model — no subscriptions, no hidden fees… 1000 SERPs will cost you $0.6… There is no monthly fee for SERP API. Instead, we have a $50 minimum payment." Nothing here should be purchased yet. Every tool below is treated as a witness whose claims must be recorded with provenance, not as a source of truth.

Key conclusions:
- **The free/first-party layer (Google Search Console, Bing Webmaster Tools, Google Trends, YouTube Data API, eRank free, EverBee free) is the correct starting stack.** It provides genuine first-party and observational evidence at zero or near-zero cash cost. GSC and Bing Webmaster APIs are free; the YouTube Data API is free within a default 10,000-unit/day quota (Google's docs confirm "a default quota allocation of 100 search.list calls, 100 videos.insert calls, and 10,000 units per day combined for all other endpoints").
- **The dangerous subscriptions are the full SEO suites (Ahrefs, Semrush, Moz, Similarweb) and the enterprise GEO tools (Profound, and stacked Ahrefs Brand Radar).** They bill monthly regardless of use, their headline prices understate true cost (seats, add-ons, API overages), and much of what they sell is proprietary *estimate* plus dashboard comfort — not unique observational evidence. They should wait until SearchClarity has revenue and a weekly-use justification.
- **The GEO/AI-visibility category is real but immature, non-deterministic, and mostly measurement-only.** Cheap entry points exist (Otterly.ai's official pricing lists a Lite plan at $29/month with 15 search prompts), but no tool "fixes" anything, outputs fluctuate run-to-run, and provider metrics must be heavily caveated. This category is a SearchClarity/customer-layer candidate, not an Observatory foundation.

## Confidence and Source Quality
- **High confidence (official pricing pages, official docs):** DataForSEO per-request pricing and pay-as-you-go model; Ahrefs tier prices; Semrush tier prices; Moz Pro tiers; eRank tier prices; GSC/Bing API free status and limits; YouTube Data API quota; DataForSEO terms of service; Ahrefs and Semrush terms of service (redistribution/storage clauses); Otterly.ai pricing.
- **Medium confidence (reputable third-party, multiple corroborating sources):** SerpApi tier prices; GEO tool prices (Profound, Peec — vendor pages plus multiple buyer guides); vidIQ/TubeBuddy tiers; Marmalead/EverBee/Sale Samurai prices; Ahrefs API overage rates.
- **Lower confidence / needs confirmation:** Social Blade Business API dollar pricing (gated behind login); client-report display rights for both major suites (terms are silent/ambiguous).
- **Caveat on affiliate content:** Many SEO-tool "pricing" and "comparison" pages are affiliate-driven and biased toward a "buy" conclusion. Prices were cross-checked against official pages wherever possible; affiliate commentary was used only for practical caveats, not as price-of-record.
- Research date: July 10, 2026. Prices in USD unless noted. Where a vendor bills in EUR (Peec AI), the euro figure is retained.

## Source List
- DataForSEO — SERP API pricing, pricing hub, terms of service, privacy policy, FAQ (dataforseo.com); DataForSEO API guides (nextgrowth.ai, buildmvpfast.com, costbench.com)
- Ahrefs — official pricing and plan blog (ahrefs.com); Ahrefs Terms of Service (ahrefs.com/legal/terms) and Domain Rating License (ahrefs.com/legal/domain-rating-license); third-party pricing (vendr.com, g2.com, thatmarketingbuddy.com, checkthat.ai)
- Semrush — official pricing and AI Visibility pricing (semrush.com); Semrush Terms of Service (semrush.com/company/legal/terms-of-service) and Content Policy; third-party (demandsage.com, tekpon.com, vendr.com, g2.com, smartguidehubs.com)
- SerpApi — official pricing and enterprise pages (serpapi.com); SearchApi (searchapi.io); comparison guides (scrapebadger.com, apiserpent.com, scrappa.co, nextgrowth.ai)
- Moz — G2, Capterra, TrustRadius, Tekpon, thenextweb.com, morningscore.io, mentionagent.ai
- eRank — official plans (erank.com), help center; merchtitans.com, goldcityventures.com, sellertoolshq.com
- Marmalead / EverBee / Sale Samurai — salesamurai.io, everbee.io, goldcityventures.com, growingyourcraft.com, outrank.so
- vidIQ / TubeBuddy — official (tubebuddy.com), outlierkit.com, checkthat.ai, toolsurf.com
- Social Blade — official (socialblade.com), outlierkit.com, capterra.com, apify.com
- GEO/AI tools — peec.ai, otterly.ai, semrush.com, zapier.com, surmado.com, loamly.ai, visiblie.com, siftly.ai, aipeekaboo.com
- Google/Bing first-party — developers.google.com (Search Console API, YouTube Data API), learn.microsoft.com (Bing Webmaster API), seotesting.com, heyseo.app
- Semrush AI Visibility / Ahrefs Brand Radar — semrush.com/pricing/ai, ewrdigital.com, ekamoira.com, frictionai.co, tryanalyze.ai, slatehq.com

## 1. Tool Overview and Category Fit

| Tool | Category | Surfaces Covered | API? | Export? | Best Use | Main Caveat |
|---|---|---|---|---|---|---|
| DataForSEO | API/Data provider | Google/Bing/YouTube/eBay/Walmart/App stores SERPs, keywords, backlinks, AI Overview/AI Mode | Yes (core) | Yes (JSON/HTML) | Observatory programmatic evidence backbone | Async task model; data is scraped SERP data (search-engine ToS risk sits with user) |
| SerpApi | API/Data provider | 80+ engines incl. Google, Bing, YouTube, Maps, Shopping | Yes (core) | Yes (JSON) | Premium SERP capture, edge-case blocks | ~25× DataForSEO cost at scale; monthly subscription, credits expire |
| SearchApi.io / others | API/Data provider | Google + verticals | Yes | Yes | DataForSEO alternative | Lower brand track record; verify reliability |
| Ahrefs | SEO suite | Backlinks, keywords, rank, site audit, Brand Radar (AI) | Yes (Advanced+; capped rows) | Yes (capped) | Backlink/keyword research, one-off deep dives | Expensive; internal-use-only license; near-real-time backlink DB is the unique draw |
| Semrush | SEO suite | Keywords, rank, backlinks, audit, PPC, local, AI Visibility | Business tier only | Yes | All-in-one breadth for client work | Add-on/seat sprawl; API gated to $499.95 tier |
| Moz Pro | SEO suite | Keywords, rank, links, Domain Authority, audit | Yes (paid) | Yes | Domain Authority as industry-lingua-franca metric | DA is a proprietary estimate |
| Similarweb | SEO/traffic intel | Traffic estimates, audience, competitive | Yes (paid) | Yes | Traffic/market estimates | Estimates, not first-party; enterprise pricing |
| SE Ranking | SEO suite (mid) | Rank, keywords, audit, AI visibility | Yes | Yes | Cheaper all-in-one; AI tracking included | Still a monthly subscription |
| Mangools | SEO suite (budget) | KWFinder, SERPChecker, SERPWatcher, LinkMiner | Limited | Yes | Cheap keyword/SERP research | Shallow depth; light API |
| Ubersuggest | SEO suite (budget) | Keywords, audit, rank, backlinks | Limited | Yes | Cheapest paid entry; lifetime deal | Data depth lags; upsell-heavy UI |
| Google Search Console | First-party platform | Google Search impressions/clicks/position for owned sites | Yes (free) | Yes (1,000 UI / 25,000 API rows) | Primary first-party truth for owned/client sites | Google only; 16-month retention; sampled/anonymized long-tail |
| Bing Webmaster Tools | First-party platform | Bing organic for owned sites | Yes (free) | Yes | First-party Bing evidence | Smaller share; API has documented bugs |
| Google Trends | First-party platform | Relative search interest | No official (unofficial) | Manual/CSV | Directional demand signal | Relative, not absolute volume |
| Google Keyword Planner | First-party platform | Keyword volume ranges (Ads) | Via Google Ads API | Yes | Volume ranges | Requires Ads account; bucketed ranges |
| YouTube Data API | First-party platform | Public video/channel metadata, search | Yes (free, quota) | Yes | Video observational evidence | 10,000 units/day; search=100 units; no historical trends for others |
| YouTube Studio/Analytics | First-party platform | Owner's own channel performance | Analytics API (OAuth) | Yes | Owned-channel first-party truth | Owner-only; boundary reference |
| Pinterest Trends/Analytics | First-party platform | Pin trends, owned account | Limited | Partial | Pinterest visibility signal | Limited API |
| Shopify Analytics | First-party platform | Owned store performance | Yes (owner) | Yes | Owned-store truth | Boundary reference, not Observatory storage |
| Etsy Stats | First-party platform | Owned shop stats | Limited | Partial | Owned-shop truth | Boundary reference |
| eRank | Marketplace SEO | Etsy keywords, competition, trends, rank checks | No public API | Yes (CSV) | Etsy keyword/competition observation | Relative indicators, not exact volume; grading unreliable |
| Marmalead | Marketplace SEO | Etsy keyword research, seasonality | No | Limited | Etsy keyword ideation | Possible inaccurate volume estimates |
| EverBee | Marketplace SEO | Etsy product/sales estimates, keywords | No public API | Limited | Product/sales-estimate research | Estimates; Chrome-extension-centric |
| Sale Samurai | Marketplace SEO | Etsy keywords, tags, sales estimates | No public API | Yes (spreadsheet) | Cheap Etsy keyword research | Estimates |
| vidIQ | YouTube/video SEO | Keyword research, competitor, AI ideation | Limited | Yes | Video keyword/idea research | Estimates; AI-credit tiering |
| TubeBuddy | YouTube/video SEO | Keyword, A/B testing, bulk tools | Limited | Yes (export) | Video optimization + A/B evidence | Auto-renew complaints; per-channel |
| Social Blade | YouTube/video SEO | Public channel stats/rankings across platforms | Yes (paid, credit) | Yes (CSV on paid) | Public channel-size observation | Earnings are rough estimates; API price gated |
| Profound | GEO/AI visibility | ChatGPT/Perplexity/Gemini/AIO brand citations | Yes (higher tier) | Yes | Enterprise AI-visibility depth | Enterprise pricing; measurement-only |
| Peec AI | GEO/AI visibility | ChatGPT/Perplexity/AIO citations | Looker connector | Yes | Mid-market AI visibility | Add-ons for Gemini/Claude/AI Mode |
| Otterly.ai | GEO/AI visibility | ChatGPT/AIO/Perplexity/Copilot + GEO audit | No API (Looker) | Partial | Cheapest AI-visibility entry | Fewer engines; add-ons for Gemini/AI Mode |
| Semrush AI Visibility | GEO/AI visibility | ChatGPT Search, Google AI Mode, share of voice | Via Semrush | Yes | Bolt-on if already on Semrush | Per-domain pricing; per-user AI seat cost |
| Ahrefs Brand Radar | GEO/AI visibility | 6 AI surfaces incl. AIO, ChatGPT, Perplexity | Via Ahrefs | Yes | Bolt-on if already on Ahrefs | Very expensive stacked; snapshot accuracy gaps |

**Fit summary:** API-first providers (DataForSEO especially) and first-party platform tools are the strongest fits for the Observatory (they produce exportable, provenance-clean observational evidence). SEO suites are dashboard-first and mostly SearchClarity/one-off-research candidates. GEO tools are model-output witnesses suited to SearchClarity's AI-readiness service, not Observatory storage foundations.

## 2. Pricing Survey

| Tool | Free/Trial? | Lowest Useful Paid Plan | Monthly Cost | API/Usage Cost | Key Limits | Source |
|---|---|---|---|---|---|---|
| DataForSEO | $1 trial credit; unlimited sandbox | Pay-as-you-go (no plan) | $0 base; $50 min deposit | SERP Standard $0.0006/req ($0.60/1k); Priority $0.0012; Live $0.002; AI Overview async +$0.0006; AI Summary $0.01/task; Google AI Mode Standard $0.0012/SERP | Depth-based billing since Sept 19, 2025 (extra pages +75% of base); balance no expiry | Official |
| SerpApi | 250 free searches/mo | Developer | $75/mo (5,000 searches, $0.015/search) | Starter $25/mo (1k); ~$15/1k at Developer | Credits expire monthly (use-it-or-lose-it); max 20% of credits/hour | Official + third-party |
| SearchApi.io | 100 free | Entry | $40/mo | Per-plan | Lower track record | Official |
| Ahrefs | Free (verified-site tools only); no full trial | Starter (research) / Lite (real work) | $29/mo Starter; $129/mo Lite | API: Lite 10k units/mo; overage $0.35–1.00/1k rows; full API access begins at Advanced ($449) | Starter: 1 project, ~500 kw reports; $29→$129 gap | Official + Vendr + checkthat.ai |
| Semrush | 7-day trial (+7-day money-back); limited free | Pro | $139.95/mo ($117.33 annual / $1,399.40/yr) | API Business tier only ($499.95/mo) | 5 projects/500 kw (Pro); seats +$45 (Pro) to $80–100; add-ons $20–289 | Official + Vendr |
| Moz Pro | 30-day trial (card req.) | Standard | $99/mo ($79 annual); Starter $49 ($39 annual) | API paid | Standard: 3 campaigns/300 kw; Medium $179; Large $299 | G2 + Tekpon |
| Similarweb | Limited free checker | Team/Custom | Custom (enterprise) | Paid | Enterprise quotes | Third-party |
| SE Ranking | Trial | Essential | $65/mo | Yes | Mid-tier limits | Third-party |
| Mangools | Free/trial | Entry/Basic | $18.85–$31.85/mo | Light | Lookup caps | Third-party |
| Ubersuggest | Free (3 queries/day) | Individual | $12/mo (or $120 lifetime) | Limited | Data depth lags | Third-party |
| Google Search Console | Free | — | $0 | Free API (no charge) | 1,000 UI rows; 25,000/API req; 16-mo retention | Official |
| Bing Webmaster Tools | Free | — | $0 | Free API (key) | Documented API bugs; content submission 10k URLs/day | Official |
| Google Trends | Free | — | $0 | No official API | Relative index | Official |
| Google Keyword Planner | Free (Ads acct) | — | $0 | Via Google Ads API (up to 1,000 kw/req) | Bucketed ranges w/o active spend | Official |
| YouTube Data API | Free | — | $0 | Free within quota | 10,000 units/day; search.list=100 units (~100 searches/day); upload ~100 units since Dec 2025; no paid quota tier | Official |
| eRank | Free (no card, unlimited) | Basic | $5.99/mo (Pro $9.99, Expert $29.99) | No public API | Free: 10 rank checks/day, 1 shop; Basic 5 competitors | Official |
| Marmalead | 14-day trial | Single plan | $19/mo ($15.83 annual) | No | Single tier | Third-party |
| EverBee | Free (10–20 searches/mo) | Growth | $29.99/mo (Pro $7.99) | No public API | Free search cap low | Vendor + third-party |
| Sale Samurai | 3-day trial | Standard | $9.99/mo ($8.30 annual / $99/yr) | No public API | Use code for 20% off | Vendor + third-party |
| vidIQ | Free (generous) | Pro | $7.50/mo ($5 annual); Boost $19 | Limited | AI-credit tiers | Third-party |
| TubeBuddy | Free (1 channel) | Pro | ~$3.50/mo annual (Legend ~$23) | Limited | Per-channel; auto-renew | Official + third-party |
| Social Blade | Free (ad-supported) | Bronze | $3.34/mo annual (to Platinum $83.34) | Business API: prepaid credits, ~1/lookup, price gated | Free: ~2 wks history, no export | Official + third-party |
| Profound | Demo only, no free trial | Starter | ~$82.50/mo annual (50 prompts); Growth ~$332.50 (100 prompts); "from $99" monthly | Yes (higher tier) | Enterprise realistically $399–$499+; $2k–5k+ enterprise | Third-party + vendor |
| Peec AI | Free trial | Starter | €89/mo (25 prompts); Pro €199 (100 prompts) | Looker connector | 2,250 AI answers (Starter)/9,000 (Pro); Gemini/Claude/AI Mode = paid add-ons | Vendor + third-party |
| Otterly.ai | Free trial | Lite | $29/mo (15 prompts); Standard $189 (100 prompts); Premium $489 (400 prompts) | No API (Looker connector) | Gemini/AI Mode add-ons $9–149; 4 base engines; Lite no API | Official |
| Semrush AI Visibility | 7/14-day trial | Toolkit add-on | $99/mo per domain (Semrush One from $199) | Via Semrush | +$99 per AI-access user; +$60/50 prompts; +$99/domain | Official + third-party |
| Ahrefs Brand Radar | Free beta indexes for paid subs | Index add-on | $199/mo per platform index; $699/mo all six; +$129 base Lite ≈ $828 all-in | Via Ahrefs | Custom prompts +$50/mo/2,500; snapshot accuracy gaps | Third-party |

## 3. Feature Overlap Matrix

| Feature | DataForSEO | Ahrefs | Semrush | GSC/Bing | Marketplace Tools | YouTube Tools | GEO Tools | Notes |
|---|---|---|---|---|---|---|---|---|
| Keyword research | ✅ (API) | ✅ | ✅ | Partial (own) | ✅ (Etsy) | ✅ (YT) | ❌ | Heavy overlap; DataForSEO supplies raw |
| Keyword volume | ✅ (Ads/Bing metrics) | ✅ (estimate) | ✅ (estimate) | Ranges (KP) | ✅ (estimate) | ✅ (estimate) | ❌ | Suite volumes are estimates |
| Keyword difficulty | ✅ (Labs) | ✅ (proprietary) | ✅ (proprietary) | ❌ | Partial | Partial | ❌ | Proprietary scores differ |
| SERP snapshots | ✅ (raw) | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | DataForSEO gives raw SERP incl. HTML/screenshot |
| Rank tracking | ✅ (build) | ✅ | ✅ | Position (own) | ✅ (Etsy rank) | Partial | ❌ | GSC gives real own position |
| SERP features | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | Partial | Feature blocks in raw SERP |
| Backlinks | ✅ (API) | ✅ (best DB) | ✅ | Partial (own) | ❌ | ❌ | ❌ | Ahrefs unique near-real-time refresh |
| Domain authority/rating | ✅ (Labs rank) | ✅ (DR) | ✅ (AS) | ❌ | ❌ | ❌ | ❌ | All proprietary estimates |
| Competitor domain research | ✅ | ✅ | ✅ | ❌ | ✅ (Etsy shops) | ✅ (channels) | Partial | — |
| Content gap | Partial | ✅ | ✅ | ❌ | Partial | ❌ | ❌ | Suite feature |
| Site audit/on-page | ✅ (On-Page API) | ✅ | ✅ | Partial | ✅ (listing audit) | ✅ (SEO studio) | Partial (GEO audit) | — |
| Local SEO | ✅ (Maps) | Partial | ✅ (add-on) | ✅ (GBP) | ❌ | ❌ | ❌ | — |
| Google AI Overview/AI visibility | ✅ (AIO/AI Mode API) | ✅ (Brand Radar) | ✅ (AI Toolkit) | ❌ | ❌ | ❌ | ✅ (core) | Fast-moving |
| ChatGPT/Perplexity/LLM citation | ✅ (LLM Mentions API) | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ (core) | GEO tools specialize |
| YouTube/video SEO | ✅ (YT SERP) | Partial (Brand Radar beta) | ❌ | YT API (own) | ❌ | ✅ (core) | ❌ | — |
| Etsy marketplace SEO | Partial (eBay/Walmart, not Etsy natively) | ❌ | ❌ | ❌ | ✅ (core) | ❌ | ❌ | Marketplace tools unique for Etsy |
| Pinterest visibility | ❌ | ❌ | ❌ | Partial (own) | ❌ | ❌ | ❌ | Mostly first-party |
| Shopify/storefront SEO | Partial | Partial | Partial | ✅ (own) | ❌ | ❌ | ❌ | First-party best |
| Export/API access | ✅ (both) | ✅ (capped) | ✅ (Business API) | ✅ (free API) | ✅ (CSV) | ✅ | Partial | — |
| Reporting/dashboard | ❌ (data only) | ✅ | ✅ | Basic | ✅ | ✅ | ✅ | Observatory does NOT need vendor dashboards |

## 4. Unique Evidence Value

| Tool | Unique Evidence | Replaceable By | Needed Early? | Notes |
|---|---|---|---|---|
| DataForSEO | Raw, structured, geo-targeted SERP snapshots + AIO/AI Mode/LLM mentions at per-request cost | Manual capture (slow) / SerpApi (pricier) | Yes (small controlled pulls) | The backbone instrument; observational, timestamped |
| GSC | First-party clicks/impressions/position for owned+client-verified sites | Nothing (proprietary first-party) | Yes | Highest-trust evidence class |
| Bing Webmaster | First-party Bing organic | Nothing | Yes | Under-used; free |
| Ahrefs | Near-real-time backlink graph + large keyword/Content Explorer DB | DataForSEO backlinks (partial); no full equal | No | Backlink DB is the genuine unique draw; one-off use |
| Semrush | Breadth (PPC + traffic + local + AI) in one place | Multiple cheaper tools stacked | No | Convenience, not unique evidence |
| Moz | Domain Authority (industry-recognized shorthand) | Any proprietary authority score | No | DA valuable only because others speak it |
| Similarweb | Cross-site traffic/audience estimates | Partial (Ads data, DataForSEO) | No | Estimate, enterprise cost |
| eRank/Marmalead/EverBee/Sale Samurai | Etsy-specific keyword/competition/sales estimates | Manual Etsy search + scraping (ToS risk) | Maybe (free tiers) | Estimates; unique because Etsy data is otherwise closed |
| vidIQ/TubeBuddy | YouTube keyword/competitor + A/B test outcomes | YouTube API (partial) | Maybe | TubeBuddy A/B = genuine experimental evidence |
| Social Blade | Public cross-platform channel size/history | YouTube API (own metrics only) | No | Third-party public estimates |
| Profound/Peec/Otterly | Structured, tracked LLM citation share over time | Manual prompting (non-deterministic) / DataForSEO LLM Mentions | No (until revenue) | Model output; must caveat non-determinism |
| Semrush/Ahrefs AI add-ons | AI visibility inside existing suite | Dedicated GEO tools | No | Only if already paying base suite |

**Evidence-type classification:**
- **Observational (highest value for Observatory):** DataForSEO SERP snapshots, YouTube API metadata, TubeBuddy A/B outcomes.
- **Private first-party (highest trust):** GSC, Bing Webmaster, YouTube Analytics, Shopify/Etsy owned stats.
- **Proprietary estimate (must caveat):** Ahrefs DR/keyword volume, Semrush volume/Authority Score, Moz DA, Similarweb traffic, all marketplace sales estimates.
- **Model output (must heavily caveat, non-deterministic):** all GEO/AI-visibility tools, DataForSEO AI Summary/LLM Mentions.

## 5. Small-Operator ROI Risk

- **Dangerous subscriptions (bill regardless of use, high monthly floor):** Ahrefs Lite+ ($129+), Semrush Pro+ ($139.95+ with predictable creep to $400–1,000 once seats/add-ons stack), Profound, stacked Ahrefs Brand Radar (~$828 all-in), Similarweb. These fail the anti-goblin test unless used weekly for revenue-producing customer work.
- **Cheap enough to test (low absolute risk):** eRank Basic ($5.99), Sale Samurai ($9.99), Ubersuggest ($12), Marmalead ($19), TubeBuddy Pro (~$3.50), vidIQ Pro ($5–7.50), Otterly Lite ($29), EverBee Growth ($29.99), Mangools ($18.85+). All are month-to-month-cancelable; treat as one-off research spends.
- **Should wait until customer revenue:** All full SEO suites at Lite/Pro+ and above; all enterprise GEO tools; Semrush/Ahrefs AI add-ons.
- **Only worth it if used weekly:** Ahrefs, Semrush, Moz, SE Ranking, any GEO monitoring subscription. A rank tracker or AI-visibility monitor delivers ROI only through repeated observation.
- **Useful for one-off research, not monthly retention:** Ahrefs (backlink deep-dive), Similarweb (market snapshot), Marmalead/EverBee (niche validation). Buy one month, extract, cancel.
- **Mostly dashboard comfort (weak for Observatory):** Semrush all-in-one dashboards, Moz interface, most GEO dashboards. The Observatory does not need a vendor UI — it needs exportable evidence.
- **Produce exportable evidence (Observatory-friendly):** DataForSEO (JSON/HTML), GSC/Bing (API/CSV), YouTube API (JSON), eRank (CSV), Social Blade (CSV on paid), TubeBuddy (spreadsheet export).
- **Anti-goblin verdict:** Pay rent only where a tool provides (a) evidence unavailable more cheaply, (b) direct support to paid customer work, or (c) an internal decision improvement. On that test, DataForSEO (controlled pulls) and the free first-party layer pass immediately; the suites and enterprise GEO tools do not pass until SearchClarity revenue exists.

## 6. Tool ROI Tracker Candidate (fields only — not an implementation)

| Field | Purpose | Required? | Notes |
|---|---|---|---|
| tool | Identify instrument/witness | Yes | Canonical name |
| category | Group by instrument type | Yes | API/suite/first-party/marketplace/video/GEO |
| monthly_cost | Recurring cash outflow | Yes | USD; note currency if not |
| annual_cost | True annual commitment | Yes | Capture annual-discount lock-in |
| billing_model | Understand cost risk | Yes | PAYG / subscription / credit / seat-based |
| features_used | What is actually consumed | Yes | Distinguish from features available |
| evidence_types_supported | Map to evidence taxonomy | Yes | Observational/first-party/estimate/model-output |
| unique_data_not_available_elsewhere | Anti-goblin justification | Yes | If blank → cancel candidate |
| reports_supported | SearchClarity deliverable link | No | Which customer reports it feeds |
| customer_work_supported | Revenue linkage | Yes | Which paid work it enables |
| internal_projects_supported | Internal decision linkage | No | Observatory/roadmap use |
| provider_admission_status | Governance state | Yes | pending/admitted/rejected |
| rights_storage_notes | Legal exposure | Yes | Export/store/redistribute/retention |
| export_api_notes | Integration feasibility | Yes | API? export format? caching limits |
| frequency_used | ROI signal | Yes | daily/weekly/monthly/one-off |
| last_used_date | Detect dormant rent | Yes | Trigger cancel review |
| keep_cancel_upgrade_reason | Decision rationale | Yes | Written justification |
| decision_date | Audit trail | Yes | When decided |

## 7. Provider Admission Cost Gates

Before subscribing / before first paid API pull, the following must be known:
- **Purpose:** the specific question the tool answers that cannot be answered more cheaply.
- **Budget cap:** hard ceiling (e.g., DataForSEO daily spend limit set in dashboard; $50 min deposit acknowledged).
- **Expected evidence output:** what evidence class it yields and where it lands.
- **Data rights confirmed:** export, storage, retention, redistribution, client-report display (see Section 10).
- **Storage/retention confirmed:** how long raw outputs may be retained (Semrush API terms bar caching data more than one month without written consent; GSC retains source data ~16 months).
- **Cancel date / review date:** pre-set month-two review; calendar reminder before auto-renew.
- **Owner approval:** explicit sign-off for any recurring subscription.
- **Stop conditions:** e.g., spend exceeds cap; evidence duplicative of a cheaper instrument; not used in N days; rights unclear.

**Usage ceiling:** define a per-tool monthly cash ceiling and (for APIs) a hard daily spend limit. DataForSEO supports a daily expense limit natively and returns a 40200 error when funds run out — use it.

**Evidence required to justify renewal:** at least one instance of unique, exportable evidence used in customer work or an internal decision within the billing period, logged in the ROI Tracker with last_used_date.

**Month-two questions:** Was it used weekly? Did it produce evidence unavailable elsewhere? Did it support revenue or an internal decision? Are rights still clear? If any answer is "no," cancel.

## 8. Free / Low-Cost First Stack

| Tool | Use Now? | Why / Why Not | Cost Risk |
|---|---|---|---|
| Google Search Console | Yes | Free, first-party, highest-trust evidence for owned/verified sites; free API | None |
| Bing Webmaster Tools | Yes | Free first-party Bing organic; free API (mind documented bugs) | None |
| Google Trends | Yes | Free directional demand signal; manual/CSV capture | None |
| Google Keyword Planner | Yes (if Ads account accessible) | Free volume ranges; bucketed without active spend | None (needs Ads acct) |
| YouTube Data API | Yes | Free video observational evidence within 10,000 units/day; search=100 units | None (quota, not $) |
| Pinterest Trends | Yes | Free trend signal | None |
| Manual SERP capture | Yes | Zero-cost observational evidence with provenance; slow | Time only |
| DataForSEO (small controlled pulls) | Yes — after rights/cost gate | Cheapest programmatic SERP/AIO evidence; set daily cap; confirm ToS indemnity clause | Low if capped ($50 min) |
| eRank free / EverBee free / Sale Samurai trial | Yes (limited) | Cheap/free Etsy observation for SearchClarity discovery | Low |
| vidIQ free / TubeBuddy free | Yes (limited) | Free video research baseline | Low |
| Otterly Lite ($29) | Only if a specific customer needs AI-visibility proof | Cheapest GEO entry; measurement-only, non-deterministic | Low, but premature |
| Ahrefs / Semrush monthly | No | Not justified until weekly use + revenue | High |
| Profound / Brand Radar bundle | No | Enterprise cost, premature | High |

**Do not buy anything yet.** This stack establishes evidence-gathering capability at near-zero cash cost. DataForSEO is the only paid instrument worth admitting early, and only through small controlled pulls behind a confirmed cost gate.

## 9. SearchClarity Launch Stack (tool–evidence fit only; no service packages)

- **Etsy listing visibility audit:** *Free/minimal:* Etsy own search + eRank free (keyword/competition, listing audit) + manual capture. *Paid upgrade:* eRank Basic/Pro ($5.99–9.99), Sale Samurai ($9.99), EverBee Growth ($29.99). *Evidence:* keyword competition indicators, listing-audit flags, sales estimates. *Manual:* Etsy autocomplete, visible ranking checks. *Caveat:* all volumes/sales are estimates; eRank grades unreliable. *Wait for revenue:* none needed — cheap tier.
- **Marketplace SEO audit (broader):** *Free/minimal:* first-party owned stats + manual. *Paid:* DataForSEO (eBay/Walmart SERP), marketplace tools. *Evidence:* marketplace SERP position, competitor tags. *Caveat:* Etsy not natively in DataForSEO; marketplace tools fill that gap.
- **SERP visibility audit:** *Free/minimal:* GSC (owned), manual SERP capture. *Paid:* DataForSEO controlled pulls (raw SERP + features + AIO). *Evidence:* timestamped SERP snapshots, feature presence, position. *Caveat:* scraped SERP ToS risk sits with requester; GSC only covers owned/verified.
- **AI/GEO citation readiness audit:** *Free/minimal:* manual prompting of ChatGPT/Perplexity + Otterly free trial + DataForSEO AIO/LLM Mentions small pulls. *Paid:* Otterly Lite ($29), Peec Starter (€89). *Evidence:* citation presence/share over tracked prompts, GEO audit score. *Caveat:* non-deterministic — same prompt varies run-to-run; measurement-only, fixes are separate work. *Wait for revenue:* yes for any monthly subscription.
- **YouTube/video visibility audit:** *Free/minimal:* YouTube Data API + YouTube Studio (owned) + vidIQ/TubeBuddy free. *Paid:* TubeBuddy Pro (~$3.50, incl. A/B testing evidence), vidIQ Pro ($5–7.50), Social Blade Bronze ($3.34). *Evidence:* keyword/tag data, A/B test outcomes, public channel history. *Caveat:* third-party channel history unavailable via official API; earnings estimates rough.
- **Shopify/product page visibility audit:** *Free/minimal:* Shopify Analytics (owned) + GSC + manual. *Paid:* DataForSEO product/SERP pulls. *Evidence:* owned-store first-party + SERP position. *Caveat:* first-party is boundary reference, not Observatory-stored.

## 10. Rights / Export / Storage Caveats

| Tool/Category | Export? | Raw Storage? | Customer Report Use? | Retention Concern | Notes |
|---|---|---|---|---|---|
| DataForSEO | Yes (JSON/HTML) | Yes | Yes (data is yours to use) | Balance/no expiry; you indemnify DataForSEO for search-engine ToS violations | ToS §7.2: user indemnifies for SERP-data use violating search-engine ToS; scraping publicly available SERP data positioned as legal but sending automated queries can violate Google ToS |
| SerpApi | Yes (JSON) | Yes | Yes | ZeroTrace mode optional | Standard commercial SERP API |
| Ahrefs | Yes (capped) | No explicit grant | Unclear (except Domain Rating) | License = internal business use only (ToS §12.4) | ToS §12.7 bars reselling/publishing data without written consent; §4.3 no scraping; §4.3(l) no competing product; Domain Rating separately licensed for display WITH attribution |
| Semrush | Yes | API data: no caching >1 month | Unclear (built-in reports exist, raw data redistribution restricted) | API cache limit 1 month (§3.3) | ToS §3.2 internal-use only; §3.3(a) no resell/transfer to third parties; §3.3(r) explicit ban on using outputs to train AI/build competing dataset; §3.3(p) no scraping |
| Moz | Yes | Likely internal-use | Unclear | Standard | Confirm ToS before client redistribution |
| Marketplace tools (eRank etc.) | Yes (CSV) | Likely internal | Unclear | Standard | Confirm each; data is estimates |
| YouTube tools | Yes | Partial | Unclear | — | Social Blade estimates; verify |
| First-party (GSC/Bing/YouTube API) | Yes | Yes (your own data) | Yes (your/client's own data) | GSC ~16-mo source retention; YouTube API ToS restricts long-term storage & competing-dataset building | Best rights posture — it's the site/channel owner's own data |
| GEO tools | Partial (Looker) | Partial | Yes (own brand) | — | Confirm per vendor; Otterly no API |

**Critical rulings needed:** (1) Client-report display of Ahrefs and Semrush metrics is **Unclear — needs confirmation** in both ToS despite both selling reporting tools; Ahrefs Domain Rating is the one metric explicitly displayable with attribution under its separate Domain Rating License. (2) Semrush's §3.3(r) explicit prohibition on using its outputs (including generative-AI outputs) as inputs to develop, train, fine-tune, or enhance any AI/ML model or competing dataset is directly relevant to the Observatory's "connected LLM interprets" doctrine — Semrush data should NOT be fed to the interpreting LLM in any way that could be construed as training/enhancing a model or competing dataset. (3) DataForSEO's indemnity clause means the Observatory (not DataForSEO) bears search-engine ToS risk for stored SERP data.

## 11. Tool Personality Profiles

- **DataForSEO** — *Good for:* cheap, structured, exportable SERP/keyword/backlink/AIO evidence at scale. *Weak for:* turnkey dashboards, Etsy-native data. *Best evidence:* observational SERP snapshots with provenance. *Worst evidence:* anything needing a UI. *ROI risk:* very low (PAYG, capped, $50 min). *API/export:* excellent, JSON/HTML, async task model. *Caveat metrics:* record as "observed via DataForSEO at time Z"; note scraping/indemnity. *Early use:* Yes — controlled pulls behind cost gate.
- **Ahrefs** — *Good for:* backlinks (near-real-time), keyword/content research. *Weak for:* AI-visibility value-for-money, cheap entry. *Best evidence:* backlink graph. *Worst evidence:* proprietary DR treated as truth. *ROI risk:* high ($129 Lite floor, no full trial, no refunds). *API/export:* capped rows, overage $0.35–1.00/1k. *Caveat metrics:* DR/volume are estimates. *Early use:* No — one-off month only if backlink evidence needed.
- **Semrush** — *Good for:* all-in-one breadth. *Weak for:* cost control (seat/add-on sprawl). *Best evidence:* competitive breadth snapshot. *Worst evidence:* volume estimates as truth. *ROI risk:* high ($139.95 Pro floor); API gated to $499.95 tier. *API/export:* Business only; 1-month cache limit. *Caveat metrics:* estimates; §3.3(r) AI-training ban. *Early use:* No.
- **Google Search Console** — *Good for:* first-party Google truth. *Weak for:* non-Google, long-tail (sampled). *Best evidence:* real clicks/impressions/position for owned sites. *Worst evidence:* complete keyword universe (hidden long-tail). *ROI risk:* none (free). *API/export:* free API, 25k rows/req, ~16-mo retention. *Caveat:* Google-only, sampled. *Early use:* Yes — foundational.
- **Bing Webmaster Tools** — *Good for:* first-party Bing organic, free. *Weak for:* share of market; API has bugs. *Best evidence:* owned-site Bing data. *ROI risk:* none. *API/export:* free key-based API. *Early use:* Yes.
- **eRank** — *Good for:* affordable Etsy keyword/competition/trends. *Weak for:* exact volumes; grading. *Best evidence:* Etsy competition indicators, listing-audit flags. *Worst evidence:* letter grades. *ROI risk:* very low ($5.99). *API/export:* CSV, no public API. *Caveat:* relative indicators only. *Early use:* Yes (free tier) for SearchClarity Etsy work.
- **Marmalead** — *Good for:* Etsy keyword ideation/seasonality. *Weak for:* volume accuracy. *ROI risk:* low ($19). *Early use:* one-off trial.
- **EverBee** — *Good for:* Etsy product/sales-estimate research. *Weak for:* listing optimization depth. *ROI risk:* low (free tier; $29.99 growth). *Early use:* free tier.
- **Sale Samurai** — *Good for:* cheap Etsy keyword/tag research + Chrome extension. *Weak for:* dashboard depth. *ROI risk:* very low ($9.99). *Early use:* trial/one-off.
- **vidIQ** — *Good for:* YouTube keyword/idea research. *Weak for:* treating AI ideation as evidence. *ROI risk:* low. *Early use:* free tier.
- **TubeBuddy** — *Good for:* video optimization + A/B test outcomes (genuine experimental evidence), bulk tools, export. *Weak for:* auto-renew traps. *ROI risk:* low but watch renewals. *Early use:* free tier; Pro if video customer work.
- **Social Blade** — *Good for:* public cross-platform channel size/history. *Weak for:* earnings accuracy; API price opacity. *Best evidence:* subscriber/view history. *Worst evidence:* earnings estimates. *ROI risk:* very low. *API/export:* paid CSV; Business API price gated. *Early use:* Bronze if needed.
- **Perplexity/GEO monitoring tools (Profound/Peec/Otterly)** — *Good for:* tracked LLM citation share over time. *Weak for:* determinism, fixing anything, ROI at enterprise price. *Best evidence:* citation presence/share for tracked prompts. *Worst evidence:* any single run treated as stable truth. *ROI risk:* low (Otterly) to very high (Profound enterprise). *API/export:* limited (Otterly none; Peec Looker). *Caveat:* non-deterministic; measurement-only. *Early use:* No — SearchClarity customer layer only, cheapest tier if a customer explicitly needs it.

## 12. Recommended Observatory Handling

- **Consider early (evidence-positive, low risk):** DataForSEO (controlled pulls, post-gate), GSC, Bing Webmaster Tools, Google Trends, Google Keyword Planner, YouTube Data API, eRank free, EverBee/Sale Samurai/vidIQ/TubeBuddy free tiers.
- **Wait (until SearchClarity revenue + weekly-use justification):** Ahrefs, Semrush, Moz, SE Ranking, Similarweb, all GEO monitoring subscriptions, Semrush/Ahrefs AI add-ons.
- **Too expensive/premature:** Profound (enterprise), Ahrefs Brand Radar full bundle (~$828 all-in), Similarweb enterprise, SerpApi at scale (use DataForSEO instead).
- **Need rights review before use:** Ahrefs & Semrush (client-report display unclear; Semrush AI-training ban §3.3(r)); DataForSEO (indemnity/scraping); any tool whose data would be shown to customers.
- **Need provider admission before stored evidence:** every paid tool, and any tool whose raw output the Observatory would retain — especially DataForSEO (SERP-data retention/indemnity) and Semrush (1-month API cache limit).
- **Dashboard-only / weak for Observatory:** Semrush/Moz dashboards, most GEO dashboards, Similarweb UI. Value is in export, not the UI.
- **SearchClarity/customer layer only:** marketplace tools (Etsy), video tools, GEO tools — they support customer deliverables, not Observatory foundations.
- **Belongs in Provider Admission Rules:** rights confirmation, retention limits, indemnity awareness, cost caps, cancel/review dates.
- **Belongs in Tool ROI Tracker:** every tool considered, with the Section 6 fields.
- **Belongs in M13 provider admission:** DataForSEO first (as primary instrument), then case-by-case admission of any paid witness with confirmed rights and a live customer/internal need.
- **No schema, no implementation, no subscriptions recommended yet.**

## 13. Questions / Unknowns To Confirm
- Client-facing report display rights for Ahrefs (non-DR metrics) and Semrush — **Unclear — needs confirmation** with each vendor.
- Exact Ahrefs API overage per-1k-row pricing (~$0.35–1.00/1k rows cited) and standalone API entry price (full API access begins at the Advanced $449 tier) — confirm against current official docs.
- Social Blade Business API dollar cost — gated behind login — **Unclear — needs confirmation.**
- Whether feeding DataForSEO/other vendor data to the Observatory's connected LLM for read-time interpretation could trigger any "competing dataset/AI training" clause (clearly implicated for Semrush §3.3(r)) — **owner ruling needed.**
- Etsy-native keyword volume: no official API; all tools estimate — confirm acceptable evidence caveat language.
- GSC vs YouTube API "100 searches/day" framing appears conflated in some sources — the 100-search figure is the YouTube Data API's search.list bucket, not a GSC limit; confirm exact GSC row/QPS limits against official limits page.
- Pinterest/Shopify/Etsy API export scope for owned accounts — confirm per platform.

## 14. Decision Inputs For M1 / M7 / M13 / M15 Roadmap

**Recommended status per major tool/category:**
- DataForSEO — *Suitable as Provider Admission input (primary); Tool ROI Tracker input; SearchClarity launch planning input.* Needs rights/indemnity ruling before stored evidence.
- GSC / Bing / Google Trends / Keyword Planner / YouTube API — *Suitable as first-stack; Tool ROI Tracker input.* No admission cost; confirm retention/export handling.
- Ahrefs / Semrush / Moz / Similarweb — *Not recommended — too early.* Needs owner ruling + revenue + rights confirmation.
- eRank / Marmalead / EverBee / Sale Samurai — *Suitable as SearchClarity launch planning input.* Cheap-test tier only.
- vidIQ / TubeBuddy / Social Blade — *Suitable as SearchClarity launch planning input.* Free/cheap tier.
- Profound / Peec / Otterly / Semrush AI / Ahrefs Brand Radar — *Needs owner ruling; not recommended for Observatory storage.* SearchClarity customer layer, cheapest tier, only on explicit customer need. Needs rights/pricing confirmation.

**Must know before M1 roadmap sequencing:** which evidence classes the Observatory will store (observational vs estimate vs model-output vs first-party) and that first-party + DataForSEO cover the core cheaply.

**Must know before M13 provider admission:** confirmed data rights, retention limits, and indemnity exposure for each admitted witness — starting with DataForSEO.

**Must know before first paid subscription:** the specific unique evidence justifying rent, the weekly-use case, the cancel/review date, and owner approval.

**Must know before first paid API pull:** DataForSEO cost gate (daily spend cap set, $50 minimum acknowledged), rights/indemnity ruling, and where the pulled evidence lands with provenance.

**Must know before SearchClarity customer-facing use:** client-report display rights (Ahrefs non-DR & Semrush unclear; Ahrefs DR OK with attribution), caveat language for all estimates and model outputs, and non-determinism disclosure for GEO tools.

---

### DECISION OUTPUT (decision-ready summary)

| Tool / Category | Recommended Status |
|---|---|
| **DataForSEO** | Suitable as Tool ROI Tracker input **+** Provider Admission input (primary instrument) **+** SearchClarity launch planning input. Needs rights/indemnity confirmation before stored evidence. |
| **GSC / Bing WT / Google Trends / Keyword Planner / YouTube Data API** | Suitable as free first-stack **+** Tool ROI Tracker input. No admission cost. |
| **Ahrefs / Semrush** | Not recommended — too early. Needs owner ruling + rights confirmation (client-report display; Semrush §3.3(r) AI clause). |
| **Moz / Similarweb / SE Ranking / Mangools / Ubersuggest** | Not recommended — too early / needs owner ruling. One-off research only. |
| **eRank / Marmalead / EverBee / Sale Samurai** | Suitable as SearchClarity launch planning input. Cheap-test tier; needs rights confirmation for client reports. |
| **vidIQ / TubeBuddy / Social Blade** | Suitable as SearchClarity launch planning input. Free/cheap tier; Social Blade API pricing needs confirmation. |
| **Profound / Peec / Otterly / Semrush AI Visibility / Ahrefs Brand Radar** | Needs owner ruling; not recommended for Observatory storage. SearchClarity customer layer only, cheapest tier, on explicit customer need. Needs rights/pricing confirmation. |

**Must know before M1 roadmap sequencing:** the evidence taxonomy the Observatory will store, and confirmation that first-party tools + DataForSEO cover the core cheaply.
**Must know before M13 provider admission:** confirmed data rights, retention limits, and indemnity exposure per witness — DataForSEO first.
**Must know before first paid subscription:** unique-evidence justification, weekly-use case, cancel/review date, owner approval.
**Must know before first paid API pull:** DataForSEO daily spend cap set, $50 minimum acknowledged, rights/indemnity ruling, provenance destination defined.
**Must know before SearchClarity customer-facing use:** client-report display rights (Ahrefs non-DR & Semrush = unclear; Ahrefs DR = OK with attribution), caveat language for all estimates/model outputs, non-determinism disclosure for GEO tools.

*Remember: The Observatory stores observations. The connected LLM interprets at read time. Provider tools are witnesses, not truth. A subscription must earn its rent through evidence unavailable cheaper, customer work supported, or internal decisions improved. On current evidence, only the free first-party layer and DataForSEO (behind a cost/rights gate) earn early standing; every monthly SEO suite and enterprise GEO tool remains "wait until revenue."*

## Appendix A — Pricing Table
Headline entry points (USD unless noted): **DataForSEO** SERP Standard $0.0006/req ($0.60/1k), $50 min deposit, no subscription, $1 signup credit; **SerpApi** Developer $75/mo (5k searches, $0.015 each), free 250/mo; **SearchApi.io** $40/mo; **Ahrefs** Starter $29, Lite $129, Standard $249, Advanced $449, Enterprise $1,499; **Semrush** Pro $139.95, Guru $249.95, Business $499.95, Semrush One Starter $199/Pro+ $299/Advanced $549; **Moz Pro** Starter $49 ($39 annual), Standard $99 ($79 annual), Medium $179, Large $299; **SE Ranking** $65; **Mangools** $18.85–$31.85; **Ubersuggest** $12 (or $120 lifetime); **GSC / Bing WT / Trends / Keyword Planner / YouTube Data API** $0; **eRank** Basic $5.99 / Pro $9.99 / Expert $29.99; **Marmalead** $19 ($15.83 annual); **EverBee** Pro $7.99 / Growth $29.99; **Sale Samurai** $9.99 ($99/yr); **vidIQ** Pro $5–7.50 / Boost $19; **TubeBuddy** Pro ~$3.50 / Legend ~$23 (annual); **Social Blade** Bronze $3.34 → Platinum $83.34 (annual); Business API prepaid credits (price gated); **Profound** ~$82.50–$332.50 annual, "from $99" monthly, enterprise $2k–5k+; **Peec AI** Starter €89 / Pro €199; **Otterly.ai** Lite $29 (15 prompts) / Standard $189 (100) / Premium $489 (400); **Semrush AI Visibility** $99/mo per domain; **Ahrefs Brand Radar** $199/index or $699 bundle + $129 base ≈ $828 all-in.

## Appendix B — Feature Overlap Matrix
(See Section 3 for the full matrix comparing DataForSEO, Ahrefs, Semrush, GSC/Bing, marketplace tools, YouTube tools, and GEO tools across keyword research, volume, difficulty, SERP snapshots, rank tracking, SERP features, backlinks, domain authority, competitor research, content gap, site audit, local SEO, AI Overview/AI visibility, LLM citation monitoring, YouTube/video SEO, Etsy, Pinterest, Shopify, export/API, and reporting.)

## Appendix C — Tool Personality Profiles
(See Section 11 for full profiles of DataForSEO, Ahrefs, Semrush, GSC, Bing WT, eRank, Marmalead, EverBee, Sale Samurai, vidIQ, TubeBuddy, Social Blade, and Perplexity/GEO monitoring tools.)

## Appendix D — Tool ROI Tracker Candidate Fields
(See Section 6 for the 18 candidate fields: tool, category, monthly_cost, annual_cost, billing_model, features_used, evidence_types_supported, unique_data_not_available_elsewhere, reports_supported, customer_work_supported, internal_projects_supported, provider_admission_status, rights_storage_notes, export_api_notes, frequency_used, last_used_date, keep_cancel_upgrade_reason, decision_date.)