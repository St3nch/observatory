# SEO Metric Claim-Safety Research Report for The Observatory

## Executive Summary

The core finding: **every SEO/GEO/SERP/marketplace/video metric The Observatory will encounter is bounded evidence about what a specific source reported under a specific context at a specific time — none of it is truth about the web, the market, the customer's business, or the future.** This is not a stylistic preference; it is forced by how the metrics are actually produced. Ahrefs' April 2025 study of 22 billion clicks across 887,534 Google Search Console properties found anonymized queries made up 46.77% of website traffic (up from 46.08% across 9 billion clicks in 2022), with the most common per-site range running 45%–80%. Ahrefs' own study of 1,635 sites found its US organic-traffic estimate deviates from Google Search Console by a median of 49.52% (Semrush's median deviation in the same study was 68.36%; Ahrefs' correlation to GSC was 0.76). Google Keyword Planner returns rounded ranges ("1K–10K"), not counts. Ahrefs states plainly that Domain Rating is "purely link-based" — and a documented Xamsor experiment paid $35 to lift a site to DR 51 (later DR 60) while it ranked for nothing and had zero traffic. Google says structured data "enables a feature to be present, it does not guarantee that it will be present." SE Ranking's June 2025 study of 10,000 keywords found only 9.2% of AI Mode citation URLs matched across three same-day runs of the same query, with 21.2% of keywords showing zero URL overlap.

The Observatory doctrine — the database stores observations, the connected LLM interprets at read time, and accepted conclusions promote out to the owning consumer — is the correct architecture for exactly this reason. The database must never harden a provider's estimate, score, or ranking snapshot into a fact. The safe unit of storage is: *Provider/surface P reported value X for target T, under request/context C, captured at time Z.* Everything beyond that — causation, prediction, universal ranking, market demand, AI "trust," business health, opportunity verdicts, recommendations — is either a read-time interpretation the LLM must caveat, or a conclusion that only an owning consumer outside The Observatory may accept.

This report classifies ~30 metric families by evidence type, provides a large Safe vs Unsafe Claim Matrix, defines forbidden claim classes, sets rules for causal language, absence/negative evidence, minimum metadata, and proposes candidate severity levels (S0–S4) and Hammer Test inputs. It is decision input for the future Claim-Safety Contract, Absence/Negative Evidence Contract, Provider Cross-Check Contract, Freshness/Volatility Contract, typed read-tool warnings, and SearchClarity report-safe language. It does not design schema and does not build the contracts.

## Confidence and Source Quality

**High confidence (official/primary sources):** metric definitions and stated limitations from Google Search Console Help and Search Central, Google structured-data guidelines, Google AI-features documentation, Bing Webmaster Tools/blog, YouTube Data API and YouTube Analytics API documentation, DataForSEO help center and API docs, Ahrefs help/blog, Semrush knowledge base/blog, Etsy Seller Handbook and legal disclosures, Pinterest Business Help. These state, in the providers' own words, what each metric is and is not.

**Moderate confidence (reputable third-party studies):** Ahrefs anonymized-query study (46.77% of clicks hidden), traffic-estimate accuracy comparisons (Screaming Frog, Collaborator, Ahrefs' own deviation study), AI citation volatility studies (SE Ranking, Similarweb, BrightEdge, Semrush). These are directionally consistent across independent sources but use different samples and methods; treat magnitudes as indicative, not exact.

**Lower confidence / needs confirmation:** exact internal weightings of proprietary scores (DR, Authority Score, KD) are not disclosed; AI-surface source-selection mechanics are described mostly by SEO researchers, not by the AI vendors themselves; some marketplace ranking factors are described qualitatively by the platform without weights. These are flagged inline as "Unclear — needs confirmation."

The most important epistemic hazard: many secondary sources use future-tense and marketing language ("this will drive traffic," "proves demand," "AI trusts"). None of that is evidence and none of it may be stored as fact.

## Source List

Primary/official:
- Google Search Console Help — "What are impressions, position, and clicks?" https://support.google.com/webmasters/answer/7042828 (accessed 10 Jul 2026)
- Google Search Central Blog — "A deep dive into Search Console performance data filtering and limits" (2022-10) https://developers.google.com/search/blog/2022/10/performance-data-deep-dive (accessed 10 Jul 2026)
- Google Search Console Help — Query guidelines / anonymized queries https://support.google.com/webmasters/answer/12917174 (accessed 10 Jul 2026)
- Google Search Central — "AI features and your website" (updated 2025-12-10) https://developers.google.com/search/docs/appearance/ai-features (accessed 10 Jul 2026)
- Google Search Console Help — "Generative AI performance report (Search)" https://support.google.com/webmasters/answer/16984139 (accessed 10 Jul 2026)
- Google Search Central Blog — "Introducing Search Generative AI performance reports in Search Console" (2026-06) https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports (accessed 10 Jul 2026)
- Google Search Central — General Structured Data Guidelines https://developers.google.com/search/docs/appearance/structured-data/sd-policies (accessed 10 Jul 2026)
- Bing Webmaster Blog — "Unlocking insights with the new Bing Webmaster Tools Performance Report" (2023-09) (accessed 10 Jul 2026)
- YouTube Analytics API — Data Model & Metrics https://developers.google.com/youtube/analytics/data_model (accessed 10 Jul 2026)
- YouTube Data API — Videos resource https://developers.google.com/youtube/v3/docs/videos (accessed 10 Jul 2026)
- DataForSEO Help Center — Search Volume, Clickstream, Competition, CPC, clickstream ETV https://dataforseo.com/help-center (accessed 10 Jul 2026)
- Ahrefs — "What is Domain Rating (DR)?" and blog https://ahrefs.com/blog/domain-rating/ (accessed 10 Jul 2026)
- Ahrefs — "How Accurate Are the Search Traffic Estimations in Ahrefs?" https://ahrefs.com/blog/traffic-estimations-accuracy/ (accessed 10 Jul 2026)
- Ahrefs — "You Can't Compare Backlink Counts in SEO Tools" https://ahrefs.com/blog/link-index-comparison/ (accessed 10 Jul 2026)
- Semrush — "Keyword Difficulty score" https://www.semrush.com/kb/1158-what-is-kd and "Authority Score" (accessed 10 Jul 2026)
- Etsy Seller Handbook — "How Etsy Search Works" and Search/Advertisement/Recommendation Ranking Disclosures (accessed 10 Jul 2026)
- Pinterest Business Help — "Browse Pinterest Trends" (accessed 10 Jul 2026)

Reputable third-party:
- Ahrefs — "Anonymized Queries Make Up Nearly Half of GSC Traffic" (46.77%, April 2025; 22 billion clicks, 887,534 properties) (accessed 10 Jul 2026)
- Ahrefs — "38% of AI Overview Citations Pull From The Top 10" (863,000 keyword SERPs, 4M AIO URLs) via Search Engine Journal (accessed 10 Jul 2026)
- Screaming Frog — "How Accurate Are Website Traffic Estimators?" (accessed 10 Jul 2026)
- Collaborator — Semrush vs Similarweb vs Ahrefs traffic accuracy study (accessed 10 Jul 2026)
- SE Ranking — "AI Mode Research: Sources, Volatility" (Jun 2025, 10,000 keywords) (accessed 10 Jul 2026)
- Similarweb — "AI Citation Volatility" (accessed 10 Jul 2026)
- Semrush — "Who Has the Best Backlink Database?" study (Feb 2021, 10K domains) (accessed 10 Jul 2026)
- Xamsor — Ahrefs DR manipulation experiment (27 Mar 2024) (accessed 10 Jul 2026)

## 1. Claim-Safety Concept

**Claim safety** for The Observatory is the discipline of ensuring that every stored or spoken statement is bounded by (a) its source, (b) its context, (c) its capture time, and (d) its evidence type — and never exceeds what that bounded observation can support.

Four distinct layers must never be collapsed:

1. **Observation** — what a source reported. "GSC reported 88 clicks for query Q on property P over date range D." This is the only thing The Observatory stores. It is safe because it is a faithful record of a provider output, not a claim about reality.
2. **Interpretation** — what the observation might mean, generated by the connected LLM at read time, always caveated. "This suggests low click volume from named Google queries in that window, though GSC anonymizes rare queries so true demand is likely higher."
3. **Recommendation** — a suggested action derived from interpretation. "Consider consolidating these pages." This belongs to the connected consumer, never to the database.
4. **Accepted consumer conclusion** — a ruling an owning consumer has explicitly accepted and now owns outside The Observatory. "We have decided this keyword is a priority." Only the consumer may make and own this.

**A safe evidence claim** describes a bounded observation: source + surface + target + context + timestamp + raw value + provider's own definition. **An unsafe conclusion claim** asserts causation, prediction, universality, provider-truth, market demand, AI trust, business health, or a verdict, as though the metric proved it.

**Why The Observatory must not store conclusions:** a conclusion is time-, context-, and interpretation-dependent. The moment it is stored as a field, it loses its caveats, outlives the evidence that produced it, and becomes indistinguishable from fact to every downstream reader. The database becoming "the astronomer" is precisely this failure — the telescope inventing conclusions instead of recording light.

**How connected LLMs should speak from evidence without overclaiming:** lead with the bounded observation, attribute it to the named source, attach the required caveat, and refuse to promote interpretation to fact. The governing principle: **a metric supports bounded language about what was observed; it does not automatically support causal, predictive, or universal claims.**

## 2. Metric Families Covered

Classification scheme: **DO** = direct observation; **FP** = first-party reported observation (verified owned account); **PN** = provider-normalized observation; **PE** = proprietary estimate; **PS** = proprietary score/model output; **3P** = third-party tool estimate; **PUB** = public surface snapshot; **PRIV** = private/customer first-party data; **?** = unclear.

| # | Metric family | Classification | Notes |
|---|---|---|---|
| 1 | SERP snapshot | DO / PUB | One SERP under one context/time; personalized, volatile |
| 2 | Rank position | DO / PUB | Position for one query/location/device/time; not universal |
| 3 | SERP feature presence (AIO, PAA, local, video) | DO / PUB | Observed present in that capture only |
| 4 | SERP absence / not observed | DO (negative) | Not-observed-in-context; never proof of non-existence |
| 5 | Keyword search volume | PE / PN | Google rounds to ranges; tools normalize with Bing/clickstream |
| 6 | Keyword difficulty / competition | PS | Proprietary model of top-10 link/SERP features |
| 7 | CPC / paid competition | PN / PE | Ad-auction metric, not organic |
| 8 | Traffic estimates (organic) | PE | Modeled rank × volume × CTR; large deviation from actuals |
| 9 | Domain authority / DR / Authority Score | PS | Provider link-model output 0–100 |
| 10 | URL/page authority scores (UR, PA) | PS | Same, page level |
| 11 | Backlink counts | 3P / PE | Index coverage varies; live vs historic differ |
| 12 | Referring domains | 3P / PE | More consistent than raw links but index-bound |
| 13 | Organic keyword counts | 3P / PE | Bound by tool index and tracking depth |
| 14 | Estimated organic traffic | PE | ~50% median deviation vs GSC (provider's study) |
| 15 | GSC impressions | FP / PN | Privacy-filtered, row-limited, canonical-deduped |
| 16 | GSC clicks | FP / PN | ~Half hidden via anonymized queries when filtered |
| 17 | GSC CTR | FP / PN | Derived; distorted by AI features/feature mix |
| 18 | GSC average position | FP / PN | Weighted, topmost-position, query-averaged |
| 19 | Bing WMT impressions/clicks/CTR/position | FP / PN | Same class; now merges web + chat |
| 20 | AI Overview / AI citation presence | DO / PUB | Prompt/context/time-bound; highly volatile |
| 21 | AI answer brand mention | DO / PUB | One answer instance only |
| 22 | AI visibility / share-of-voice scores | PS / 3P | Vendor model over sampled prompts |
| 23 | YouTube video metadata | DO / PUB | Public snapshot at capture |
| 24 | YouTube Data API statistics | PN / PUB | Public counts; subs rounded to 3 sig figs >1000 |
| 25 | YouTube Analytics metrics | FP / PRIV | Owner-only; estimated, thresholded, delayed |
| 26 | YouTube search observations | DO / PUB | Personalized, non-reproducible ordering |
| 27 | Marketplace listing snapshots (Etsy, Fiverr) | DO / PUB | Public listing state at capture |
| 28 | Marketplace search observations | DO / PUB | Personalized (Etsy CSR); not universal |
| 29 | Marketplace tool keyword estimates | 3P / PE | Third-party proxy; platforms publish no true counts |
| 30 | Pinterest trend observations | PN / PUB | Normalized 0–100 index, not absolute volume |
| 31 | Shopify public page/product | DO / PUB | Public snapshot; store analytics are PRIV |
| 32 | Reviews / ratings / counts | DO / PUB or FP | Public snapshot or first-party; recency-weighted |

## 3. Safe vs Unsafe Claim Matrix

(Full extended matrix in Appendix A; representative rows here.)

| Evidence/metric | Can safely support | Cannot prove | Safe wording | Unsafe wording | Required caveat | Min metadata |
|---|---|---|---|---|---|---|
| DataForSEO keyword volume | Provider estimated ~N monthly searches under location/language | Exact count; actual/future demand | "DataForSEO estimated ~N monthly searches (US/en) as of {date}" | "This keyword gets exactly N searches" | Estimate normalized from Google Ads + Bing/clickstream; rounded; location/language-bound | provider, keyword, location, language, date, method, raw value |
| GSC clicks | Owned property recorded N clicks from named Google queries in range | Total real demand; that only N people searched | "GSC recorded 88 clicks from named queries for P over D" | "Only 88 people searched for this" | 46.77% of clicks anonymized on average; filtered views omit anonymized rows; 16-month window | property, query/page, range, device, country, time |
| Rank position (SERP snapshot) | Target appeared at position N for Q under context C at time Z | Ranks #N everywhere/for everyone | "Observed at position N for Q, {location/device}, {time}" | "Ranks #N on Google" | Personalized/localized/volatile; single capture | query, location, language, device, login, time, depth |
| Ahrefs DR | Ahrefs scored the domain's backlink profile at N/100 | Traffic; quality; Google ranking; real authority | "Ahrefs DR is N/100 as of {date}" | "This is a high-authority, trusted site" | Purely link-based; relative/logarithmic; manipulable; not a Google factor | provider, domain, score, date |
| AI Overview citation | Surface S returned an answer citing URL A for prompt Q at time Z | That "AI trusts" the brand; that it recurs | "For prompt Q, {surface} cited URL A on {date}" | "AI trusts/recommends this brand" | Prompt/context/time-bound; may not reproduce | surface, prompt, cited URL, time, account/login |
| Not observed in first N results | Target not seen within depth N for Q under context C at time Z | That target "does not rank" / does not exist | "Not observed in top N for Q, {context}, {time}" | "This page does not rank" | Absence scoped to source/panel/depth/context/time | query, depth, context, time, source |

## 4. Forbidden Claim Classes

For each: definition · dangerous example · why unsafe · evidence needed before a consumer accepts it *outside* Observatory · safe alternative. (Full table Appendix B.)

1. **Causal claims** — asserting one thing caused another. "The title change caused the ranking increase." Unsafe: timing ≠ causation; SERPs move for many reasons (competitors, algorithm updates, personalization). Consumer needs a controlled test/hold-out and ruling. Safe: "Ranking movement was observed after the recorded change; causality is not established."
2. **Guaranteed-outcome claims** — "Doing X will get you to page 1." Unsafe: no provider or Observatory can guarantee ranking; Google itself does not. Consumer owns any bet. Safe: "No outcome can be guaranteed from this evidence."
3. **Predictive claims** — "This page will gain traffic next quarter." Unsafe: metrics are lagging observations; **predictive claims are forbidden inside Observatory unless framed as external consumer-owned conclusions outside Observatory.** Safe: "Past observations are X; any forecast is a consumer-owned conclusion."
4. **Universal rank claims** — "Ranks #1." Unsafe: one snapshot under one context; personalization/localization make universality false. Safe: bounded position statement.
5. **Provider-truth claims** — "Search volume is N." / "DR proves authority." Unsafe: treats a provider model output as a fact about the web. Safe: attribute to provider as estimate/score.
6. **Customer business-health claims** — "Your business is doing well/poorly." Unsafe: visibility metrics are not revenue/health. Consumer owns with first-party financials. Safe: restrict to observed visibility metric.
7. **Intent-certainty claims** — "Searchers of Q want to buy." Unsafe: intent is inferred, not observed. Safe: "Provider labels intent as commercial; this is a classification, not certainty."
8. **AI authority/trust claims** — "AI trusts this site." Unsafe: a citation is one retrieval event, not trust. Safe: bounded citation observation.
9. **Market-demand-certainty claims** — "There is strong demand for X." Unsafe: volume estimates are rounded proxies; demand ≠ clicks. Safe: "Estimated search volume is ~N (provider, date)."
10. **Strategy/recommendation claims** — "You should target these keywords." Unsafe: recommendations belong to the consumer. Safe: LLM may suggest at read time; not stored.
11. **Opportunity verdicts** — "This is a high-opportunity keyword." Unsafe: verdict compresses many caveated estimates into a stored truth. Safe: present component observations only.
12. **Winner/loser verdicts** — "You beat competitor X." Unsafe: depends on context/sample; snapshot-bound. Safe: "For sampled queries under C at Z, target appeared above X in N of M."

## 5. Causal Claim Safety

Evidence can show **correlation** (two series move together across enough observations), **timing sequence** (event B recorded after event A), and **possible relationship** (a hypothesis worth a consumer-owned test). It can almost never show causation, because the observational environment is uncontrolled: Google runs continuous ranking changes, competitors act, personalization and localization vary results, and SERP features shift. Rank trackers strip personalization to a baseline that no real user sees; multiple independent same-day captures of AI surfaces disagree.

Before causal language is even considered, the minimum is: a recorded intervention with a precise timestamp, a stable measurement context held constant, a control/hold-out or at least a clear counterfactual, sufficient observations to rule out noise, and explicit consideration of confounders (algorithm updates, competitor changes, seasonality). Even then the causal conclusion is consumer-owned, not an Observatory fact.

The Observatory should therefore treat **intervention timelines as read-time overlays**: the database stores the recorded change (with timestamp) and the metric series (with timestamps) as separate observations; the LLM may, at read time, note temporal adjacency and explicitly label it non-causal. Safe wording: **"Ranking movement occurred after the recorded change, but causality is not established."** Unsafe wording: **"This title change caused the ranking increase."**

## 6. Prediction and Recommendation Boundaries

Evidence (observed value) → interpretation (what it might mean, caveated) → recommendation (suggested action) → accepted strategy (consumer-owned decision) is a one-way escalation of ownership. The Observatory owns only the first. The connected LLM produces the second and may voice the third at read time. Only the consumer owns the fourth.

The Observatory must not store recommendations because a stored recommendation is a conclusion: it drops its caveats, outlives its evidence, and reads as fact. Recommendation tables, opportunity tables, and score-as-truth fields all convert bounded evidence into stored verdicts and are therefore out of scope.

How the LLM phrases possible next steps without writing them into Observatory as facts: frame them as options conditioned on the evidence and explicitly hand ownership to the consumer — "Based on the observed values, one option a decision-maker might consider is X; this is a suggestion, not a stored conclusion." Consumer-owned strategy outputs live in the owning consumer system (CRM, planning tool, human decision), cross-referenced to Observatory evidence IDs but never written back as Observatory truth. Required rule: **The Observatory may support recommendations at read time, but recommendation outputs belong to the connected consumer, not the Observatory database.**

## 7. Provider Score and Estimate Safety

Governing principle: **proprietary provider scores are observations of that provider's model output, not facts about the web.**

- **Ahrefs DR/UR** — Ahrefs: DR "shows the relative strength of a website's backlink profile" on a logarithmic 0–100 scale and is "purely link-based" (no traffic, domain age, or brand signals). Ahrefs states DR "does not directly influence Google rankings." A documented Xamsor experiment (27 Mar 2024) paid $35 to raise AuthorityCheckLab.com to DR 51 (later DR 60) while the site ranked for nothing and had zero traffic. Safe: "Ahrefs DR is N/100 (link-profile model, {date})." Unsafe: "high-authority/trusted." Caveat: relative, logarithmic, manipulable, not a ranking factor.
- **Semrush Authority Score** — Semrush: combines "link power, organic traffic, and spam factors"; "not a ranking factor itself, since it's a third-party metric"; "no universal 'good' Authority Score." Safe/unsafe/caveat parallel to DR, noting it does incorporate estimated traffic.
- **Semrush KD / Ahrefs KD** — Semrush: KD is a 0–100% score of "how difficult Semrush predicts it would be to rank," from median referring domains, dofollow/nofollow ratio, authority score of ranking domains, and SERP features. Ahrefs KD is backlink-count-based. Safe: "Provider predicts ranking difficulty at N%." Unsafe: "It is impossible/guaranteed to rank." Caveat: prediction from top-10 proxies; tools disagree.
- **DataForSEO volume/competition/CPC** — Volume is normalized from Google Ads with Bing/clickstream; DataForSEO explicitly notes Google's "Competition" is an ad metric that "does not indicate the level of organic competition." CPC is an ad-auction historical value. Safe: attribute as estimate with method and date. Unsafe: exact counts, organic difficulty, demand certainty.
- **Marketplace / YouTube SEO tool scores** — third-party proxies (e.g., eRank); platforms publish no true search counts, so any "search volume" is a modeled proxy. Treat as 3P estimates.
- **AI visibility scores** — vendor models over sampled prompts; see §9.

Every score row requires the same minimum metadata: provider, metric name, provider's own definition, raw value, scale, capture date, and the provider's stated caveat.

## 8. First-Party Metric Safety

Safe principle: **first-party platform data is stronger for the verified/owned account or property, but it remains platform-reported, scoped, delayed, filtered, and bounded.**

First-party data (GSC, Bing Webmaster, YouTube Analytics, Pinterest Analytics, Shopify Analytics, Etsy Stats) is stronger than third-party estimates because it is measured by the platform on the owner's verified property rather than modeled from outside. That is why GSC clicks beat any traffic estimate for the owned site. But limitations remain and are severe:

- **GSC**: anonymized queries hide 46.77% of clicks on average (Ahrefs, April 2025), with the most common per-site range at 45%–80%; "not all queries beyond anonymized queries will be shown" (top rows only); filtered views omit anonymized rows entirely; data is deduped to Google-selected canonical URLs; 16-month retention in-UI; 1,000-row UI cap. Average position is a weighted, topmost-position, query-averaged figure that can move the "wrong" way when a page starts ranking for more terms, and is further distorted when AI Overviews occupy a single position with all links sharing it.
- **Bing Webmaster**: same metric family; the Performance report now *combines web and chat clicks/impressions*, so a Bing figure mixes classic and AI-surface activity.
- **YouTube Analytics**: owner-only; metrics are "estimated," subject to thresholds (data withheld below minimum traffic), and delayed; daily aggregates can exceed video-level sums when videos are deleted.

Why first-party data still is not universal truth: it is scoped to one property/account, one platform's definitions, one measurement pipeline, and specific filters and delays. It describes *that property's reported experience*, not the web or the market.

Why customer first-party data should stay outside Observatory by default: it is private/PRIV, often contractually and legally restricted, and mixing it into an evidence store risks retention, privacy, and ownership violations. The Observatory should reference it by pointer/consumer ownership, not ingest it as shared evidence, unless an explicit owner ruling authorizes scoped ingestion.

## 9. AI / GEO Claim Safety

An AI citation observation supports exactly one thing: **that a named surface returned an answer citing/linking a specific URL for a specific prompt at a specific time under a specific account/login state.** It cannot prove trust, authority, endorsement, ranking, or that the same result will recur.

Volatility is the defining hazard and it is documented. SE Ranking's June 2025 study of 10,000 keywords found that across three same-day runs of the same query, only 9.2% of AI Mode citation URLs matched, 21.2% of keywords showed zero URL overlap across the three runs, and each answer carried ~12.6 links on average. AI Overviews' overlap with the organic top 10 fell from 76% (Ahrefs, July 2025, 1.9M citations) to 37.9% (Ahrefs, ~February 2026, 863,000 keyword SERPs / 4M AIO URLs) — a roughly seven-month shift, with the remainder split between positions 11–100 (31.2%) and beyond 100 (31.0%). Citation sets shift with model updates, retrieval changes, and competitor content — with no change to the cited page.

Google's own documentation confirms the non-guaranteed, variable nature. Google states AI Overviews "are only shown when our systems determine that it is additive to classic Search, and as such, often don't trigger," and that "AI Mode and AI Overviews may use different models and techniques, so the set of responses and links they show will vary" (AI features doc, updated 2025-12-10). Both surfaces "may use a 'query fan-out' technique — issuing multiple related searches across subtopics." In Search Console, AI-feature traffic is *merged into the "Web" search type*; a separate Generative AI performance report (rolling out to a subset of owners as of June 2026) shows **impressions only**, does not separate AI Overviews from AI Mode, and provides no clicks/CTR/query data. For position, Google states "an AI Overview occupies a single position in search results, and all links in the AI Overview are assigned that same position."

How to caveat provider AI visibility / share-of-voice scores: they are vendor models over a sampled, prompt-dependent, time-bound set of queries — proprietary scores (PS), not measurements of trust. Attribute to the vendor, state the sample and date, never present as authority.

How to phrase absence: "For prompt Q on {surface}, no citation of {target} was observed on {date} under {account state}" — never "AI does not cite this brand."

Safe wording: **"For prompt/query X, surface Y returned an answer on date Z that cited/source-linked URL A."** Unsafe: **"AI trusts this brand."** Required caveat: **AI/GEO observations are prompt/context/time-bound and may not reproduce exactly.**

## 10. Marketplace / Video Claim Safety

- **Etsy listing snapshots** — public state (title, tags, price, reviews) at capture; safe as snapshot. Etsy search results are personalized via Context Specific Ranking and include a temporary new-listing boost, so any observed position is context/time-bound and non-universal. Unsafe: "ranks #1 on Etsy," exact search counts, "this listing will sell."
- **Etsy search observations** — DO/PUB but personalized; record as observed-in-context.
- **Fiverr gig snapshots** — public snapshot; same rules.
- **Shopify public product/page** — public snapshot is safe; the store's own conversion/sales analytics are PRIV and stay outside Observatory by default.
- **Pinterest trend/search** — Pinterest Trends is a *normalized* 0–100 index ("the highest point of the search term is indexed to 100, and the lowest point is indexed to 0"), not absolute volume; Shopping Trends and audience data are region/account-scoped. Third-party tools acknowledge "no tool can show a true Pinterest search volume." Safe: "Pinterest Trends indexed interest in X at N/100 for {region/date}." Unsafe: "N people searched X on Pinterest."
- **YouTube public video metadata / statistics** — public counts; subscriber counts are rounded to three significant figures above 1,000 via the API. Safe: "viewCount was N at {capture}." Unsafe: treating a snapshot count as precise/current without timestamp.
- **YouTube search observations / Google SERP video results** — personalized, non-reproducible ordering; bounded position only.
- **Third-party marketplace/video tool estimates** — 3P proxies; attribute and caveat.

Claims especially dangerous in customer-facing reports (all forbidden as stated): exact search counts, "ranks #1 generally," "this video will get traffic," "this product will sell," "score proves demand." Each converts a bounded snapshot or proxy estimate into a universal, predictive, or demand-certainty claim.

## 11. Negative Evidence / Absence Rules

Absence means different things per surface, and none of them mean non-existence:

- **SERP panels**: a feature (AIO, PAA, local pack) not present in this capture may be present in the next; Google states features are shown only when its systems judge them additive and "often don't trigger."
- **AI citation checks**: not cited in this run says nothing about the next run — same-day reproduction is ~9% at the URL level (SE Ranking).
- **Provider tools**: "no data" often means below the tool's index/threshold, not zero. Semrush's Feb 2021 study found at least one referring domain for 99.5% of analyzed URLs — more than any other tool tested — meaning Ahrefs, Moz, and Majestic returned zero (no data) for more of the same URL set. "Zero referring domains" is therefore often index coverage, not reality.
- **Marketplace search**: not seen in depth N under personalization ≠ not listed.
- **YouTube search**: personalized ordering means not-seen is context-bound.

Required rule: **absence must be recorded as *not observed* within a specific source/panel/context/depth/time, not as proof of non-existence.** Every absence record needs the same scoping metadata as a positive observation, plus explicit depth/sample size.

## 12. Minimum Metadata Before Claiming

| Claim type | Minimum metadata required | If missing |
|---|---|---|
| Rank/position observation | provider/source, surface, query, target, location, language, device, login state, capture timestamp, depth | Cannot claim position; store as unqualified fragment or reject |
| Keyword volume/estimate | provider, keyword, location, language, method, raw value, capture date, provider caveat | Cannot state volume; must not be spoken as demand |
| Provider score (DR/AS/KD) | provider, metric name+definition, raw value, scale, capture date | Cannot cite score; no interpretation allowed |
| First-party metric (GSC/Bing/YT) | property/account, verified ownership, metric, date range, device, country, filters, capture time, privacy/retention class | Cannot attribute as first-party; treat as unverified |
| AI citation | surface, prompt/query, cited URL, capture timestamp, account/login state, geo | Cannot claim citation; reject |
| Absence / not observed | source/panel, query/prompt, context (geo/device/login), depth/sample size, capture timestamp | Cannot record absence; must not become "does not exist" |
| Backlink/referring domain | provider, index type (live/historic), target, raw value, capture date | Cannot compare across tools; flag index-bound |
| Traffic estimate | provider, target, geo, method, raw value, capture date, provider deviation caveat | Cannot state traffic |
| Public snapshot (marketplace/video/Shopify) | source URL/entity, captured fields, capture timestamp, public/private class | Cannot treat as current; reject as stale |

Universal metadata every evidence record needs: provider/source, target, capture timestamp, metric definition, raw value, rights/retention class, public/private classification, freshness/staleness class, evidence ID/citation handle, and (where applicable) provider task/request ID and provider caveat.

## 13. Claim-Safety Severity Levels (candidate contract input, not doctrine)

| Level | Definition | Allowed wording | Disallowed wording | Example |
|---|---|---|---|---|
| **S0** | Direct observation, safe to state as recorded | "Source P reported X for T at Z under C" | Any extrapolation | "GSC recorded 88 clicks for Q on P over D" |
| **S1** | Bounded interpretation by LLM at read time | "This suggests…, bounded by {caveat}" | Causal/universal/predictive phrasing | "This suggests low named-query clicks; ~47% of clicks are anonymized" |
| **S2** | Cautious hypothesis, explicitly non-causal, test-worthy | "One possible relationship, not established, is…" | "caused," "because of" | "Movement occurred after the change; causality not established" |
| **S3** | Consumer-owned recommendation only | "A decision-maker might consider… (consumer-owned)" | Storing it; asserting it as fact | "You might prioritize Q — this is your decision to own" |
| **S4** | Forbidden inside Observatory | — | All of §4's forbidden classes | "AI trusts this site"; "ranks #1"; "will sell" |

## 14. Hammer Test Inputs (suggested future tests, not implemented)

1. Reject universal rank claims derived from a single SERP snapshot (require context+time scoping).
2. Reject exact-demand claims from keyword volume estimates (require estimate framing + method + date).
3. Reject causal claims from timing alone (require "causality not established" and consumer ownership).
4. Reject AI trust/authority claims from citation presence (require prompt/surface/time scoping).
5. Reject customer-private first-party claims stored inside Observatory (require owner ruling for any ingestion).
6. Reject provider-score-as-truth wording (require provider attribution + definition + caveat).
7. Reject not-observed → does-not-exist conversion (require scoped absence with depth/sample).
8. Reject recommendation storage (recommendations must be read-time, consumer-owned).
9. Reject predictive claims inside Observatory (must be external consumer-owned conclusions).
10. Reject cross-tool backlink/traffic comparisons without index-type and method flags.
11. Reject any stored field named as a verdict, opportunity, score-as-truth, or winner/loser.
12. Reject public-snapshot claims lacking capture timestamp (staleness guard).

## 15. Recommended Observatory Handling

- **Claim-Safety Contract** should encode: the four-layer separation, the S0–S4 severity levels, the bounded-language principle, per-metric safe/unsafe wording from Appendix A, and the forbidden classes from Appendix B.
- **Absence/Negative Evidence Contract** should require the not-observed-in-context rule with mandatory scoping metadata (source/panel/context/depth/time) and forbid non-existence conversion.
- **Provider Cross-Check Contract** should record that different providers measure different things (index coverage, normalization, model) and that disagreement is expected — cross-checks corroborate direction, not exact values; never average provider outputs into a single "truth."
- **Freshness/Volatility Contract** should assign staleness classes and flag high-volatility evidence (AI citations, SERP snapshots, rank positions) as requiring recency and reproduction caveats.
- **Typed read-tool response warnings** should attach the required caveat to every evidence type at read time (estimate, first-party-scoped, snapshot, volatile, private).
- **SearchClarity / customer-facing report-safe language** should default to bounded observation phrasing and strip verdicts, predictions, and demand/trust language.
- **Consumer-owned outside Observatory**: all recommendations, accepted conclusions, strategy, and customer-private first-party data.
- **Forbidden unless owner ruling**: ingestion of customer-private first-party data; any stored recommendation/opportunity/verdict/score-as-truth field.

## 16. Questions / Unknowns To Confirm

- Exact internal weightings of DR, Authority Score, and KD — **Unclear — needs confirmation** (providers disclose factors, not formulas).
- Whether The Observatory's own SERP/AI collectors will run logged-out with controlled geo/device — determines how absence and position are scoped; **needs confirmation**.
- Precise mechanics of AI-surface source selection per vendor (ChatGPT, Perplexity, Gemini, Copilot) — described by SEO researchers, not vendors; **Unclear — needs confirmation**.
- Whether customer first-party data will ever be authorized for scoped ingestion, and under what retention class — **needs owner ruling**.
- Exact freshness thresholds per surface — **needs owner ruling**.
- Whether Bing's merged web+chat metrics can be separated for claim purposes — currently appears not; **needs confirmation**.

## 17. Decision Inputs For M1 / M7 / M8 Roadmap

- **M1 (evidence capture)**: enforce universal metadata (§12) at capture or the evidence cannot be safely claimed later. Public/private classification and capture timestamp are non-negotiable.
- **M7 (contracts)**: the Claim-Safety, Absence/Negative Evidence, Provider Cross-Check, and Freshness/Volatility contracts should adopt §1, §11, §7, and the volatility findings respectively; the forbidden classes (§4) are contract inputs.
- **M8 (hammers)**: the twelve Hammer Test inputs (§14) are candidate assertions to implement as automated guards.

---

**Decision-ready summary — recommended status:**

- **Suitable as Claim-Safety Contract input:** YES — §1, §3, §4, §7, §13 are ready to feed the contract.
- **Suitable as Absence-Negative Evidence Contract input:** YES — §11 rule and scoping metadata are ready.
- **Suitable as Hammer Matrix input:** YES — §14's twelve tests are ready as candidates.
- **Needs owner ruling:** customer-private first-party ingestion; stored recommendation/opportunity/verdict fields; freshness thresholds per surface.
- **Needs more research:** proprietary score internals; per-vendor AI source-selection mechanics; Observatory collector context settings.

**Must know before M7 contracts:** the four-layer ownership model and the forbidden classes are locked; confirm collector context (logged-out/geo/device) so scoping rules are precise.

**Must know before M8 hammers:** exact wording patterns to reject (universal rank, exact demand, causal-from-timing, AI trust, score-as-truth, absence-to-nonexistence).

**Must know before typed read tools:** the per-evidence-type caveat set and severity mapping (S0–S4).

**Must know before SearchClarity / customer-facing reports:** report-safe language defaults; verdict/prediction/demand/trust language is stripped; every figure carries source + context + time.

**Must know before any recommendation/promotion workflow:** recommendations and accepted conclusions are consumer-owned outside Observatory; promotion writes to the owning consumer, never back into Observatory as fact.

## Appendix A — Safe vs Unsafe Claim Matrix (extended)

Each row: evidence · safely supports · cannot prove · safe wording · unsafe wording · caveat.

1. **SERP snapshot** · this result set under context C at Z · the universal SERP · "Observed SERP for Q, {geo/device/login}, {Z}" · "Google's results for Q are…" · personalized/volatile.
2. **Rank position** · position seen for Q under C at Z · ranks #N everywhere · "Position N for Q, {context}, {Z}" · "Ranks #N" · single capture, personalized.
3. **SERP feature presence** · feature present this capture · feature always present · "AIO present for Q at {Z}" · "Q triggers an AI Overview" · features often don't trigger.
4. **Keyword volume (Google KP)** · Google's rounded range · exact demand · "Google range 1K–10K" · "N searches/month" · rounded, exact-match, seasonal average.
5. **Keyword volume (DataForSEO)** · provider estimate under method · exact count · "~N est. (clickstream/Bing), {date}" · "exactly N" · normalized estimate.
6. **KD/competition** · provider difficulty prediction · that ranking is impossible/guaranteed · "Provider KD N%" · "cannot/will rank" · top-10 proxy model.
7. **CPC/paid competition** · historical ad-auction value · organic difficulty/demand · "Est. CPC $X (ads)" · "organic competition is high" · ad metric, not organic.
8. **Traffic estimate** · provider's modeled traffic · actual traffic · "Est. ~N (provider), {date}" · "gets N visits" · median ~50% deviation vs GSC (Semrush ~68%).
9. **DR/AS** · provider link/authority model score · real authority/traffic/ranking · "DR N/100 (link model)" · "trusted/authoritative site" · relative, manipulable, not a Google factor.
10. **UR/PA** · page-level model score · page quality/ranking · "UR N/100" · "best page" · same as DR.
11. **Backlink count** · provider's indexed live/historic count · true link count · "Provider indexed N links (live)" · "has N backlinks" · index coverage; live vs historic differ.
12. **Referring domains** · provider's indexed RD count · true RD count · "Provider: N referring domains" · "N sites link here" · index-bound.
13. **Organic keyword count** · provider's tracked ranking terms · all terms the site ranks for · "Provider tracks N ranking keywords" · "ranks for N keywords" · index/depth-bound.
14. **GSC impressions** · owned property impressions in range · true visibility/demand · "GSC N impressions for P/Q over D" · "seen N times by everyone" · privacy-filtered, canonical-deduped.
15. **GSC clicks** · owned property clicks from named queries · total demand · "GSC 88 clicks (named queries)" · "only 88 searched" · 46.77% anonymized on average.
16. **GSC CTR** · derived clicks/impressions · quality/intent certainty · "GSC CTR X% for P over D" · "users prefer us" · distorted by AI/feature mix.
17. **GSC average position** · weighted topmost query-averaged position · true rank; simple average · "GSC avg position N for Q" · "we rank N" (site-level) · can move 'wrong' way; AIO shares one position.
18. **Bing WMT metrics** · owned property Bing web+chat activity · Google performance; pure web · "BWT N clicks (web+chat)" · "Bing organic clicks = N" · merges web and chat.
19. **AIO/AI citation presence** · surface cited URL for prompt at Z · trust/recurrence · "Surface cited URL A for Q at {Z}" · "AI trusts us" · prompt/time-bound; ~9% same-day reproduction.
20. **AI brand mention** · brand named in one answer · endorsement/consistency · "Brand mentioned in {surface} answer for Q at Z" · "AI recommends brand" · single instance.
21. **AI visibility/SoV score** · vendor model over sampled prompts · real AI authority · "Vendor AI-visibility score N (sample, date)" · "AI-dominant brand" · sampled, proprietary.
22. **YT video metadata** · public fields at capture · current state · "Title/tags at {Z}" · "the tags are…" (no time) · snapshot.
23. **YT Data API stats** · public counts at capture · precise/current counts · "viewCount N at {Z}" · "has exactly N subs" · subs rounded to 3 sig figs >1000.
24. **YT Analytics** · owner's estimated metrics · universal truth · "YT Analytics est. N (owner, range)" · "N real views" · estimated, thresholded, delayed, private.
25. **YT search observation** · ordering seen under C at Z · universal ranking · "Video at position N for Q at {Z}" · "ranks N on YouTube" · personalized.
26. **Etsy listing snapshot** · public listing state at Z · current/sales · "Listing fields at {Z}" · "this will sell" · snapshot.
27. **Etsy search observation** · position under CSR at Z · universal rank · "Position N for Q at {Z}" · "ranks #1 on Etsy" · CSR-personalized; new-listing boost.
28. **Marketplace tool keyword est.** · third-party proxy value · platform-true demand · "eRank est. N (proxy)" · "N Etsy searches" · platform publishes no counts.
29. **Pinterest Trends** · normalized 0–100 interest index · absolute volume · "Indexed interest N/100 for {region/date}" · "N Pinterest searches" · normalized, region-scoped.
30. **Shopify public product** · public page state at Z · sales/conversion · "Product fields at {Z}" · "sells well" · public snapshot; analytics private.
31. **Reviews/ratings** · displayed/first-party rating at Z · quality certainty · "Rating 4.8 (26.8k) at {Z}" · "best product" · recency-weighted by platform.
32. **Absence/not observed** · not seen in source/depth/context at Z · non-existence · "Not observed in top N for Q, {context}, {Z}" · "does not rank/exist" · scoped only.

## Appendix B — Forbidden Claim Classes

| Class | Dangerous example | Why unsafe | Evidence needed before consumer accepts (outside Observatory) | Safe alternative |
|---|---|---|---|---|
| Causal | "Title change caused ranking rise" | Uncontrolled environment; timing≠cause | Controlled test/hold-out, confounders ruled out, consumer ruling | "Movement occurred after the change; causality not established" |
| Guaranteed outcome | "This will reach page 1" | No one can guarantee ranking | Never acceptable as guarantee | "No outcome can be guaranteed" |
| Predictive | "Traffic will rise next quarter" | Metrics are lagging | Consumer-owned forecast with stated assumptions | "Past values are X; forecasts are consumer-owned" |
| Universal rank | "Ranks #1" | Snapshot/personalized | Inherently false as universal | Bounded position statement |
| Provider-truth | "Volume is N" / "DR proves authority" | Model output ≠ web fact | N/A | Attribute as estimate/score |
| Business-health | "Your business is healthy" | Visibility ≠ revenue | First-party financials owned by consumer | Restrict to visibility metric |
| Intent-certainty | "They want to buy" | Intent inferred | Consumer research | "Provider labels intent commercial (classification)" |
| AI authority/trust | "AI trusts this site" | Citation = one retrieval | N/A | Bounded citation observation |
| Market-demand-certainty | "Strong demand exists" | Rounded proxy | Consumer market validation | "Est. volume ~N (provider, date)" |
| Strategy/recommendation | "You should target these" | Recommendations consumer-owned | Consumer decision | Read-time suggestion, not stored |
| Opportunity verdict | "High-opportunity keyword" | Compresses caveated estimates into stored truth | Consumer ruling | Present component observations |
| Winner/loser | "You beat competitor X" | Context/sample-bound | Consumer ruling on defined sample | "In N of M sampled queries under C at Z, target appeared above X" |

## Appendix C — Minimum Metadata Table

See §12. Universal fields required on every evidence record: provider/source; surface; query/prompt/URL/entity; target; capture timestamp; date range (if applicable); location; language; device; account/login state; depth/sample size; provider task/request ID (if applicable); metric definition; raw value; provider caveat; rights/retention class; freshness/staleness class; public/private classification; evidence ID/citation handle.

## Appendix D — Hammer Test Candidate List

See §14 for the twelve candidate tests. Each is stated as a rejection rule (reject the unsafe conversion) rather than an implementation; all are candidate inputs to the M8 Hammer Matrix, not doctrine.