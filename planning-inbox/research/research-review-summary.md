# Research Review Summary — R1–R10 Foundation Batch

Status: research review / planning input
Authority: planning input only; not doctrine, not schema approval, not implementation approval
Milestone context: M7 — Core Contract Planning
Date: 2026-07-07

---

## Purpose

This review summarizes the standalone research batch in `planning-inbox/research/` and extracts decision-useful inputs for later Observatory planning.

The reviewed reports are source material. They are not accepted doctrine, schema approval, provider admission, customer claim approval, subscription approval, or automation approval.

The review goal is to identify what the reports establish, what remains uncertain, what belongs in contracts or hammers, what affects later provider/customer work, and which dependency topics should remain parked.

---

## Inventory reviewed

| Conceptual ID | Report file | Review status |
|---|---|---|
| R1 | `DataForSEO Research Report for The Observatory.md` | reviewed |
| R2 | `Provider Metric Comparison Research Report for The Observatory.md` | reviewed |
| R3 | `Google Search Console and Bing Webmaster Boundary Research Report for The Observatory.md` | reviewed |
| R4 | `Marketplace Evidence Ceiling Research Report for The Observatory.md` | reviewed |
| R5A | `YouTube Evidence Ceiling and Video Search Visibility Research Report for The Observatory.md` | reviewed |
| R5 | `GEO AI Citation Surface Research Report for The Observatory.md` | reviewed |
| R6 | `SERP Feature and SERP Snapshot Evidence Research Report for The Observatory.md` | reviewed |
| R7 | `SEO Metric Claim-Safety Research Report for The Observatory.md` | reviewed |
| R8 | `Freshness and Staleness Windows Research Report for The Observatory.md` | reviewed |
| R9 | `SEO Tool Pricing and ROI Research Report for The Observatory.md` | reviewed |
| R10 | `Public Page Snapshot and Archival Evidence Research Report for The Observatory.md` | reviewed |

Small hygiene issue: `planning-inbox/research/` does not currently have its own `README.md` index.

---

## Executive summary

The batch is useful and should be preserved as a foundation research set. It strongly reinforces current Observatory doctrine:

```text
The Observatory stores what was observed.
The connected LLM interprets what it means at read time.
Accepted conclusions promote out to the owning consumer.
```

The strongest cross-report conclusion is that Observatory should treat every external source as an instrument or witness, not a truth-provider. Public observations, provider API outputs, marketplace snapshots, SERP results, AI citations, tool scores, first-party webmaster data, and customer/private analytics all have different rights, provenance, freshness, and claim-safety ceilings.

The reports support M7 contract planning, but they do not authorize schema, implementation, provider admission, customer-facing reports, subscriptions, automation, or recurring capture.

---

## Cross-report findings

### CF1 — Evidence must stay source/context/time-bound

Nearly every report converges on the same rule:

```text
Provider/surface P showed or reported value X for target T under context C at time Z.
```

This is the safe observation unit. Unsafe conversions include universal rank, true demand, objective authority, AI trust, marketplace-wide rank, guaranteed improvement, or causal claims from timing alone.

Classification: accepted repo doctrine already / candidate contract input / claim-safety input.

---

### CF2 — Provider disagreement is first-class evidence

R2 makes this explicit, and R1/R3/R5/R6/R7/R9 all reinforce it. Ahrefs, Semrush, DataForSEO, GSC, Bing, YouTube APIs, marketplace tools, and GEO tools measure different things on different cadences with different rights and model assumptions.

The correct response is not to crown a winner or average disagreement into fake truth. The correct response is to preserve provider identity, metric definition, capture context, freshness, and caveats.

Classification: accepted repo doctrine already / candidate contract input / hammer-test input.

---

### CF3 — Claim safety must become a contract spine

R7 is the strongest single report in the batch for M7. It defines the difference between observation, interpretation, recommendation, and accepted conclusion. It also supplies forbidden claim classes, safe wording patterns, and S0–S4 severity candidates.

This should feed a claim-safety contract that also absorbs absence/negative-evidence rules, predictive-claim rules, causality caveats, provider-score caveats, AI/GEO caveats, and marketplace-claim caveats.

Classification: candidate contract input / claim-safety input / hammer-test input.

---

### CF4 — Freshness is evidence fitness, not truth

R8 establishes that stale evidence may remain historically true but unsafe for current claims. Fast-aging evidence includes SERP snapshots, AI answers/citations, local packs, marketplace search, YouTube search, pricing pages, and terms pages. Slower-aging evidence includes archival captures and bounded historical reports.

Freshness classes, volatility classes, preliminary-data warnings, non-synchronous comparison warnings, and recheck-required warnings should be part of M7 contracts and M14 read-tool outputs.

Classification: candidate contract input / freshness-volatility input / hammer-test input.

---

### CF5 — Public visibility is not storage or automation permission

R4, R5A, R5, R6, and R10 repeat this in different domains. Manual public observation may be lower risk, but scraping, API warehousing, platform automation, raw HTML retention, comment harvesting, and customer-facing redistribution all require source-specific rights review.

Classification: rights/retention blocker / provider admission blocker / candidate contract input.

---

### CF6 — Customer/private first-party data stays outside Observatory

R3, R4, R5A, R9, and R7 reinforce the same boundary. Customer GSC, Bing Webmaster, Etsy Stats, Shopify analytics, YouTube Analytics, Pinterest Analytics, Merchant Center, orders, customers, messages, revenue, and private seller/channel data should not be stored in Observatory.

Future use, if any, should be read-time overlay or consumer-layer data, not Observatory storage, unless owner ruling changes project law.

Classification: accepted repo doctrine already / SearchClarity boundary input / owner ruling needed for exceptions.

---

### CF7 — DataForSEO is the strongest first external provider candidate, but not admitted

R1 and R9 both support DataForSEO as the most practical API-first, pay-as-you-go provider for selective evidence pulls. It is cheaper and more instrument-like than dashboard subscriptions.

But provider admission is blocked by endpoint-level rights, raw retention, customer-facing display rights, pricing drift, current AI/LLM product coverage, spend caps, duplicate-task prevention, and source-license questions.

Classification: provider admission input / provider admission blocker / rights-retention blocker.

---

### CF8 — Marketplace and YouTube/video evidence should start manual/API-safe, not scraper-first

R4 and R5A strongly reject scraping-first thinking. Etsy/Pinterest/Fiverr/YouTube automation is restricted or risky. Shopify public storefront observation is different from marketplace rank. YouTube Data API is official but has retention/refresh rules. YouTube Analytics is private.

Classification: source admission input / manual capture dependency / SearchClarity boundary input.

---

### CF9 — GEO/AI citation visibility is measurable but volatile and non-authoritative

R5 says AI citation visibility can be measured, but only as prompt/context/time-bound evidence. Citation is not authority. Mention is not recommendation. Absence in one run is not universal absence. Third-party AI visibility scores are provider testimony, not fact.

Classification: candidate contract input / claim-safety input / freshness-volatility input / deferred dependency topic.

---

### CF10 — Tool ROI matters, but pricing research is not buying advice

R9 supports a practical tool-rent discipline: use free first-party tools and low-cost trials first; do not buy Ahrefs/Semrush/GEO subscriptions until there is revenue or weekly use; DataForSEO is the likely first paid provider only after rights/cost gates.

Classification: candidate roadmap input / provider admission input / do-not-build warning.

---

## Report-by-report extraction

### R7 — SEO Metric Claim-Safety

Main findings:

- SEO/GEO/SERP/marketplace/video metrics are bounded evidence, not truth.
- Claim language must separate observation, interpretation, recommendation, and accepted conclusion.
- Provider estimates, scores, and tool outputs require source/date/context caveats.
- Absence means not observed in a specific context, not non-existence.

Highest-confidence facts:

- GSC query rows can omit substantial anonymized/private long-tail data.
- Ahrefs, Semrush, DataForSEO, marketplace tools, and GEO tools use estimates/model outputs for many headline metrics.
- Structured data, citations, and ranking signals do not guarantee display, traffic, or improvement.

Uncertainties:

- Exact report-safe language for SearchClarity remains future consumer-side work.
- Which claim statuses should automatically block downstream output needs owner/steward decision.

Contract inputs:

- Claim-safety contract.
- Absence/negative-evidence rules.
- Provider-score attribution rules.
- Recommendation/conclusion handoff rules.
- Read-tool warning fields.

Hammer inputs:

- Reject universal rank from a single snapshot.
- Reject exact demand from keyword volume.
- Reject AI trust from citation.
- Reject causal/predictive claims from observation alone.
- Reject recommendation/opportunity/verdict storage.

Owner-ruling inputs:

- Whether any claim status blocks consumer output automatically.
- Final SearchClarity report-safe phrasing.
- Whether any predictive/recommendation text can be returned by Observatory read tools. Recommended default: no durable storage; consumer-owned only.

Do-not-build warnings:

- No recommendation/opportunity/verdict tables.
- No provider score as truth.
- No exact demand or guaranteed improvement claims.

---

### R8 — Freshness and Staleness Windows

Main findings:

- Freshness determines evidence fitness for a claim, not whether the evidence historically existed.
- High-volatility evidence needs recapture or warning before current-state use.
- Terms, pricing, provider docs, and platform policies can become stale and require recheck before decisions.

Highest-confidence facts:

- GSC has latency/preliminary data and 16-month history.
- Provider update cadences differ sharply: SERPs and AI are fast-moving; keyword/search-volume databases are often monthly; backlinks differ by provider.
- YouTube and other APIs have retention/refresh limits.

Uncertainties:

- Exact staleness windows per source family need owner/steward approval.
- Some provider cadence details require endpoint-level confirmation.

Contract inputs:

- Freshness/volatility contract.
- Claim-safety interaction rules.
- Read-tool warnings: stale/current/historical-only/recapture-required/preliminary/non-synchronous.

Hammer inputs:

- Block current claims from stale snapshots.
- Warn on non-synchronous provider comparisons.
- Recheck terms/pricing before provider admission.

Do-not-build warnings:

- No automated recurring cadence doctrine yet.
- No current-state claims from stale evidence.

---

### R6 — SERP Feature and SERP Snapshot Evidence

Main findings:

- SERP snapshots are context-bound observations, not universal rank truth.
- Rank, feature presence, and visual real estate should be separate evidence classes.
- GSC/Bing telemetry is not the same thing as SERP snapshot evidence.

Highest-confidence facts:

- SERPs vary by location, language, device, time, personalization, depth, and feature treatment.
- DataForSEO/SerpApi-style providers can return structured SERP objects, raw HTML, screenshots, and feature fields.
- Google position/impression logic is not identical to a third-party rank tracker.

Uncertainties:

- Whether screenshots are required for visual prominence claims needs owner ruling.
- Which SERP features are admitted first remains a contract/source-admission question.

Contract inputs:

- SERP evidence contract.
- Query panel context envelope.
- Capture package minimum fields.
- Provider Cross-Check separation between snapshot providers and first-party telemetry.

Hammer inputs:

- Reject universal rank claims.
- Reject missing-context SERP observations.
- Reject AI citation as classic rank.

Do-not-build warnings:

- No direct first-party SERP scraping approval by implication.
- No user-attention claims from position alone.

---

### R10 — Public Page Snapshot and Archival Evidence

Main findings:

- Page snapshots are time/context-bound observations.
- Prefer screenshots, normalized metadata, hashes, licensed API payloads, or trusted archive references.
- Full HTML/raw DOM/raw HTTP retention should be exception, not default.
- Hashes prove stored artifact integrity, not lawful capture or universal truth.

Highest-confidence facts:

- Robots/crawl controls are not blanket legal permission.
- Wayback/Perma are useful reference amplifiers but not perfect replay truth.
- Platform pages, UGC, comments, usernames, faces, and review data carry rights/privacy risk.

Uncertainties:

- Legal/terms position for long-term full HTML/body retention.
- Customer-facing screenshot redistribution rules.
- Manual capture at repeated operational scale.

Contract inputs:

- CapturePackage contract.
- Raw archive/payload retention contract.
- Rights/retention contract.
- Evidence ID/citation contract.
- Manual capture rules.

Hammer inputs:

- Missing provenance rejection.
- Rights mismatch rejection.
- Privacy leak rejection.
- Dynamic-page hash/replay caveat.
- Overclaim wording rejection.

Do-not-build warnings:

- No bulk platform-page copying.
- No archive.today as preferred evidence spine.
- No storing sensitive public personal data just because visible.

---

### R1 — DataForSEO

Main findings:

- DataForSEO is a strong API-first provider candidate for selective Observatory pulls.
- It supports SERP, keyword, backlinks, labs, shopping, business/local, YouTube, and AI/GEO-related data.
- It is not admitted; rights, retention, pricing drift, source-license, and customer-facing display questions remain.

Highest-confidence facts:

- Pay-as-you-go model, $50 minimum payment, small trial credit.
- Standard SERP and keyword costs are low enough for controlled evidence sampling.
- Standard results / HTML / screenshot retention windows on DataForSEO side are short.
- July 2026 pricing update created stale-doc risk around Backlinks/LLM Mentions.

Uncertainties:

- Endpoint-by-endpoint raw JSON retention rights.
- Customer-facing display rights for raw/normalized output.
- LLM Mentions pricing and coverage.
- Empty/error billing behavior.
- AI/geography/platform coverage details.

Contract inputs:

- Provider testimony contract.
- Source/provider admission contract.
- Cost ceiling and duplicate-task controls.
- CapturePackage provider fields.
- Freshness-model labels.

Hammer inputs:

- No spend without approval.
- Duplicate-task prevention.
- Provider metric as testimony, not truth.
- Pricing/terms recheck before admission.

Do-not-build warnings:

- No broad integration.
- No raw HTML/screenshot library by default.
- No customer-facing raw output.
- No LLM Mentions admission without support confirmation.

---

### R2 — Provider Metric Comparison

Main findings:

- Provider disagreement is evidence, not a bug.
- First-party tools and third-party instruments must not be flattened together.
- Proprietary scores must never become truth fields.

Highest-confidence facts:

- Ahrefs/Semrush/DataForSEO/GSC/Bing use different definitions, cadences, indexes, score formulas, and source classes.
- AI/GEO visibility products measure different corpora and units.

Uncertainties:

- Exact Ahrefs/Semrush API packaging and terms require future confirmation.
- Marketplace SEO tool methodology remains weakly disclosed.

Contract inputs:

- Provider Cross-Check contract.
- Provider testimony/source-class fields.
- Same-target/same-time comparison rules.
- Metric definition and cadence requirements.

Hammer inputs:

- Reject provider winner logic.
- Reject cross-provider averaging into truth.
- Require provider attribution and metric definition.
- Warn on non-synchronous comparisons.

Do-not-build warnings:

- No normalized provider-truth score.
- No score worship.
- No paying for overlapping dashboards without evidence justification.

---

### R3 — Google Search Console and Bing Webmaster Boundary

Main findings:

- GSC and Bing Webmaster are strong first-party witnesses for verified/owned properties.
- Customer GSC/Bing data is customer-private first-party telemetry and should not be stored in Observatory now.
- Future use should be read-time overlay unless owner ruling changes doctrine.

Highest-confidence facts:

- GSC is OAuth/permission-gated and subject to user-data policy.
- GSC performance data is filtered, aggregated, row-limited, canonicalized, and delayed/preliminary.
- Bing Webmaster is verified-site/API-key/OAuth-gated, with thinner docs and some unclear AI Performance API/export coverage.

Uncertainties:

- Bing AI Performance API/export status.
- Bing retention/export details by report family.
- Whether owner-internal telemetry becomes a future internal-scope track.

Contract inputs:

- First-party overlay contract.
- Customer/private-data boundary contract.
- Provider Cross-Check caveats for first-party vs third-party comparison.
- Credential/access/revocation rules for future tools.

Hammer inputs:

- No customer first-party persistence.
- Overlay no-storage proof.
- Revocation/deletion behavior.
- No Clarity/customer analytics leakage.

Do-not-build warnings:

- No customer GSC/Bing storage.
- No manual-action/security issue storage in Observatory.
- No private telemetry as generic evidence rows.

---

### R4 — Marketplace Evidence Ceiling

Main findings:

- Marketplace evidence should be manual-observation-first.
- APIs mostly expose seller-private data or impose caching/storage limits.
- Etsy/Pinterest/Fiverr automation is blocked or risky by terms.
- Marketplace SEO tool metrics are provider estimates/testimony.

Highest-confidence facts:

- Etsy API has strict 6/24-hour display freshness/caching limits and prohibits API use for analytics/ML unless authorized.
- Fiverr has no official general public API found; scraping is prohibited.
- Pinterest API storage is barred except campaign analytics.
- Shopify public storefronts differ from marketplaces; Admin/customer/order/analytics data is private.

Uncertainties:

- Fiverr official programmatic access, if any.
- Legal position on repeated manual screenshots at operational scale.
- eBay/Reddit current terms before admission.

Contract inputs:

- Marketplace source admission contract.
- Manual capture rules.
- Public/private classification.
- Rights/retention rules by surface.
- Tool-estimate testimony rules.

Hammer inputs:

- Reject scraping/automation.
- Reject API warehousing where barred.
- Reject private seller analytics storage.
- Reject marketplace estimate as demand truth.

Do-not-build warnings:

- No marketplace scraper system.
- No Etsy/Pinterest API warehouse.
- No automated Fiverr.
- No seller-private customer data.

---

### R5A — YouTube Evidence Ceiling and Video Search Visibility

Main findings:

- YouTube evidence spans public pages, official Data API, creator-private Analytics/Reporting, Google video SERPs, DataForSEO YouTube endpoints, third-party tools, and manual capture.
- DataForSEO now has YouTube-native endpoints, but they are provider testimony, not official YouTube truth.
- YouTube Data API public metadata/search is useful but governed by refresh/deletion/storage rules.
- YouTube Analytics/Reporting is creator-private and out of Observatory storage by default.

Highest-confidence facts:

- YouTube Data API has public metadata/search/comment endpoints and 30-day refresh/delete rules for non-authorized API data.
- User-authorized data must be deleted after revocation under API policies.
- Creator Analytics/Reporting metrics are private.
- Direct scraping/automated access to YouTube pages is restricted.

Uncertainties:

- DataForSEO YouTube endpoint pricing details.
- YouTube-native keyword volume availability from DataForSEO.
- Long-term handling of public comments/person-linked data.

Contract inputs:

- YouTube source admission rules.
- YouTube API retention/refresh contract rules.
- Private analytics overlay boundary.
- DataForSEO YouTube provider testimony rules.
- UGC/comment retention restrictions.

Hammer inputs:

- Reject direct YouTube scraping.
- Enforce refresh/delete policies if API data is stored.
- Reject private analytics storage.
- Reject YouTube search result as universal rank truth.
- Reject third-party score as YouTube truth.

Do-not-build warnings:

- No customer channel analytics in Observatory.
- No bulk comment/person-linked data by default.
- No raw audiovisual caching.
- No replacement metrics masquerading as YouTube metrics.

---

### R5 — GEO / AI Citation Surface

Main findings:

- AI citation visibility is measurable only as prompt/context/time-bound observation.
- Citation is not authority, endorsement, trust, or rank.
- Official APIs are safer than consumer UI scraping.
- DataForSEO has useful AI/GEO capabilities but mixes direct capture, scraper capture, and provider-estimate layers.

Highest-confidence facts:

- Google AI Overviews/AI Mode are public surfaces with context variability; GSC now has owner-facing generative AI reporting for some sites.
- Bing Webmaster AI Performance exists in public preview; API export unclear.
- OpenAI web search API exposes citation annotations; consumer UI automation/extraction is prohibited.
- Perplexity, Gemini, Claude, and Azure/Bing grounding have official API-style grounded/citation paths.
- Academic/source literature supports high volatility and citation support problems.

Uncertainties:

- Google public live-capture API for AI Overviews/AI Mode not found in reviewed docs.
- Bing AI Performance API/export status.
- Perplexity answer-text storage/redistribution rights.
- Third-party GEO methodology transparency.
- DataForSEO ChatGPT scraper legal posture.

Contract inputs:

- AI/GEO observation contract.
- Prompt/panel context envelope.
- Citation/source metadata rules.
- Provider testimony and score caveats.
- AI claim-safety warnings.

Hammer inputs:

- Reject AI trust/authority from citation.
- Reject single-run absence as nonexistence.
- Reject consumer UI scraping by default.
- Reject AI visibility score as truth.
- Require prompt/context/time metadata.

Do-not-build warnings:

- No consumer UI scraper default.
- No stored AI visibility authority score.
- No broad answer-text storage without rights review.
- No customer prompt logs in Observatory core.

---

### R9 — SEO Tool Pricing and ROI

Main findings:

- Free/first-party tools plus low-cost selective pulls are the correct starting posture.
- DataForSEO is the strongest paid provider candidate if admitted through cost/rights gates.
- Ahrefs/Semrush/Moz/Similarweb/GEO enterprise tools are premature until revenue and weekly-use justification.
- Tool pricing research is not buying approval.

Highest-confidence facts:

- DataForSEO is pay-as-you-go with low unit costs and $50 minimum deposit.
- GSC/Bing/Google Trends/Keyword Planner/YouTube Data API provide major free/first-party evidence layers.
- Ahrefs/Semrush subscriptions and AI add-ons create high recurring rent.
- Some vendor terms restrict redistribution, caching, AI/ML use, or competitive dataset creation.

Uncertainties:

- Ahrefs/Semrush client-report display rights for many metrics.
- Social Blade API pricing.
- Whether vendor data interpreted by connected LLM creates contractual issue for specific vendors.
- Exact API overage/current package details.

Contract inputs:

- Provider admission cost gate.
- Tool ROI tracker fields.
- Paid subscription approval rules.
- Rights/export/storage caveats.

Hammer inputs:

- No spend without approval.
- Spend cap/cancel review date required.
- Provider output must have evidence type and rights notes.

Do-not-build warnings:

- Do not buy anything yet.
- Do not let subscription tooling dictate schema or roadmap.
- Do not feed restricted vendor data into workflows that violate terms.

---

## M7 contract inputs

The research batch supports these contract families as candidates. It does not draft or approve them.

| Contract family | Inputs from reports | Readiness |
|---|---|---|
| Scope / Source Admission / Rights / Retention | R1, R3, R4, R5A, R5, R10 | needed; must be careful and source-specific |
| Evidence ID / Citation Handle | R6, R7, R10, R5 | needed; exact handle design still owner/M7 decision |
| Capture Package / Raw Archive | R6, R10, R1, R4, R5A, R5 | needed; raw retention should default restrictive |
| Provider Testimony / Cross-Check | R1, R2, R7, R9 | strong input; provider disagreement as design pillar |
| Query Panel / Prompt Panel | R6, R5, R5A, R8 | needed for reproducibility and absence claims |
| Claim-Safety / Negative Evidence | R7, R8, R6, R5, R4, R5A | very strong input; should likely be one merged contract |
| Freshness / Volatility | R8 plus all volatile-surface reports | strong input; thresholds still provisional |
| Typed Read Tool Output Skeleton | R7, R8, R2, R3, R5 | needed later; M7 should keep skeleton non-implementation |
| Manual Evidence Capture Rules | R4, R6, R10, R5A, R5 | needed before marketplace/manual workflows |
| SearchClarity Boundary / Consumer Output | R3, R4, R5A, R5, R7, R9 | placeholder/input only until M15 proof work |

Recommended M7 ordering:

1. Scope/source/rights/retention spine.
2. Evidence ID/citation handle spine.
3. Claim-safety/absence/freshness contracts.
4. CapturePackage/raw archive/manual capture contracts.
5. Provider testimony/Cross-Check contract.
6. Query/prompt panel contract.
7. Consumer/overlay/read-tool skeleton placeholders.

---

## M8 hammer-test inputs

The reports justify hammers for:

- stale evidence used for current claims;
- single SERP snapshot used as universal rank;
- provider score used as fact;
- cross-provider averaging/winner logic;
- absence/not-observed converted into nonexistence;
- AI citation converted into trust/authority/rank;
- platform scraping or barred API warehousing;
- private customer/seller/channel analytics entering Observatory;
- raw HTML/screenshot retained without rights;
- missing capture metadata;
- tool/subscription spend without owner approval/cost cap;
- customer-facing claims without caveats;
- manual capture used to launder automation;
- marketplace/video/GEO estimates stored as demand/performance truth.

Additional hammers from prior M7 audit still stand:

- append-only/no silent overwrite;
- concurrency;
- audit-record-required;
- migration rollback/recovery.

---

## M13 provider admission inputs

Potential later candidates, not admitted now:

| Provider/surface | Current posture | Needed before admission |
|---|---|---|
| DataForSEO | strongest first paid provider candidate | endpoint list, rights/retention/display answers, pricing confirmation, spend caps, stop conditions, raw-payload policy |
| Ahrefs | defer | use case, pricing/API package, rights/export/display, unique evidence justification |
| Semrush | defer | rights/API/cache/AI-use terms, cost justification, customer report display rules |
| SerpApi/SearchApi | alternate SERP providers | cost/reliability/rights comparison against DataForSEO |
| YouTube Data API | official public API candidate | retention/refresh policy handling, quota, no audiovisual caching, comment/UGC rules |
| OpenAI/Perplexity/Gemini/Claude APIs | official AI/GEO API candidates | terms/reuse/storage, prompt panel contract, cost caps, output caveats |
| Etsy/Pinterest APIs | highly constrained | platform-specific storage/caching rules, written authorization if needed, likely not Observatory raw archive |
| Fiverr | manual-only by default | official programmatic access confirmation; automation blocked unless proven otherwise |
| Shopify public storefront | manual/public-page observation candidate | per-store terms/robots/rate handling, no Admin/customer data |

---

## M14 typed read/API/MCP planning inputs

Read tools must return shaped evidence packs, not raw mystery rows. Required warning/output candidates:

- source/provider/surface;
- captured_at / provider-reported time;
- context envelope;
- rights/retention class;
- freshness/volatility status;
- provider attribution required;
- estimate/score/model-output warning;
- sample-bound warning;
- absence warning;
- recapture recommendation;
- customer-private overlay warning;
- consumer-promotion-required warning;
- coverage/blind-spot warning.

M14 dependency topics likely real:

- D1 Consumer Auth/AuthZ;
- D8 Report-Safe Citation Handles;
- D9 Typed Read Tool Output Warnings and Evidence Response Shape;
- D5 Coverage, Blind Spots, and Not-Observed Reporting.

---

## M15 SearchClarity proof planning inputs

SearchClarity can use Observatory evidence only as governed support. It must own customer identity, orders, reports, recommendations, deliverables, consent records, and customer/private first-party data.

Early SearchClarity evidence candidates:

- manual Etsy listing/search observations;
- eRank/free marketplace estimates as provider testimony;
- public Shopify page/schema snapshots;
- public YouTube metadata/search observations;
- GSC/Bing/YouTube Analytics only as customer-layer overlays, not Observatory storage;
- DataForSEO SERP/AI observations only after provider admission.

Claims to avoid:

- guaranteed rank/traffic/sales;
- exact Etsy/Pinterest/YouTube demand from tool estimates;
- AI trust/authority from citation;
- marketplace-wide/global rank from point-in-time observation;
- causal claims from before/after timing alone.

M15 dependency topics likely real:

- D3 First-Party Telemetry Overlay and Customer Data Separation;
- D4 Intervention Timeline Joins Without Causal Overclaiming;
- D8 Report-Safe Citation Handles;
- D10 SearchClarity First Proof Service Evidence Boundary;
- D7 Manual Evidence Capture Workflow if marketplace proof is early.

---

## Owner-ruling inputs

The review supports preserving the owner-ruling Group A items and adds source-specific context.

| Ruling | Recommended starting posture | Source reports |
|---|---|---|
| OR-A1 Provider Disagreement Ledger persistence | default compute-on-read; no persisted ledger yet | R2, R7, R9 |
| OR-A2 Sentiment handling | provider-attributed only; no Observatory-derived sentiment unless future ruling | R5, R7 |
| OR-A3 AI visibility sample summary storage | read-time output only by default | R5, R7, R8 |
| OR-A4 Citation handles | contract concept now; global vs artifact-local in M7 evidence contract | R5, R6, R7, R10 |
| OR-A5 NC3/NC5 disposition | intervention timelines as ephemeral overlays; coverage/blind spots as read-tool requirement | R7, R8, R6, R3 |
| OR-A6 Minimum M7 contract set | draft spine first; do not overbuild all consumer/provider specifics | all reports |

Additional owner/source rulings likely later:

- DataForSEO raw retention and customer display rights.
- Whether/when DataForSEO first paid pull budget is released.
- YouTube Data API public metadata retention policy inside Observatory.
- Whether public comments/UGC are excluded by default.
- Manual screenshot retention and report redistribution rules.
- Whether any vendor subscription is allowed before customer revenue.

---

## Dependency topic parking lot disposition

| Topic | Current disposition | Why |
|---|---|---|
| D1 Consumer Auth/AuthZ and Evidence Access Boundary | not needed before initial M7 contracts; needed before M14 typed read tools | access model depends on final evidence/read contracts |
| D2 Provider Credentials, Secrets, Cost Controls, and Pull Authority | needed before M13 provider admission | R1/R9 show cost/secret/pull authority is a real blocker before paid pulls |
| D3 First-Party Telemetry Overlay and Customer Data Separation | needed before M14/M15/M17; thin M7 overlay contract useful | R3/R5A/R4 show private telemetry must not enter Observatory |
| D4 Intervention Timeline Joins Without Causal Overclaiming | needed before M15 proof if before/after reports are attempted | R7/R8 make causal overclaim risk explicit |
| D5 Coverage, Blind Spots, and Not-Observed Reporting | needed before M14 typed read tools and M8 hammers | R6/R7/R8/R5 show absence/coverage warnings are central |
| D6 Ahrefs / Semrush Admission and Replacement Analysis | defer until M16 or paid subscription consideration | R2/R9 say useful but not early |
| D7 Manual Evidence Capture Workflow and Browser Extension Boundary | needed before marketplace/manual capture admission | R4/R10/R5A/R5 make manual-vs-automation distinction central |
| D8 Report-Safe Citation Handles and Evidence Reference Rules | needed during M7 evidence/citation contract and before M15 reports | R5/R6/R7/R10 all need report-safe references |
| D9 Typed Read Tool Output Warnings and Evidence Response Shape | needed before M14; M7 skeleton should preserve fields | R7/R8/R2/R5 provide warning requirements |
| D10 SearchClarity First Proof Service Evidence Boundary | needed before M15 | R4/R5A/R7/R9 show service-boundary risks |

Do not activate all dependency topics immediately. They are real, but most are milestone-specific blockers, not M7 blockers.

---

## Do-not-build warnings

Do not build or approve:

- schema or migrations from these reports;
- provider integrations or paid pulls;
- DataForSEO admission;
- Ahrefs/Semrush subscriptions;
- marketplace scraping;
- YouTube scraping;
- ChatGPT consumer UI scraping;
- raw HTML/page archive by default;
- customer GSC/Bing/YouTube/Etsy/Shopify/Pinterest analytics storage;
- seller orders/messages/customer data storage;
- strategy/recommendation/opportunity/verdict tables;
- provider truth scores;
- AI visibility authority scores;
- recurring capture cadence;
- customer-facing report claims;
- dashboard/operator console work.

---

## Recommended next steps

1. Preserve this review as planning input only.
2. Add a `planning-inbox/research/README.md` later, if owner approves, because the folder now holds a major research batch.
3. Create or update an owner-ruling tracker for OR-A1–OR-A6 and source-specific rulings.
4. During M7, draft only the spine contracts first:
   - scope/source/rights/retention;
   - evidence ID/citation;
   - claim-safety/absence;
   - freshness/volatility;
   - CapturePackage/raw archive/manual capture;
   - provider testimony/Cross-Check.
5. Keep consumer/API/tool-specific contracts skeletal until their milestone demands them.
6. Keep D1–D10 parked unless their target milestone is activated or the owner declares a blocker.
7. Before any M13 provider work, revalidate current provider terms/pricing and secure explicit owner approval for spend.

---

## Final rule

```text
The batch gives Observatory strong contract input.
It does not give Observatory permission to build.
The research proves where the rails must go, not that the train may leave the station.
```
