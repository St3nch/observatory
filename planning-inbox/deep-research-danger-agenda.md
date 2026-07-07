# Deep-Research Danger Agenda

Status: planning artifact, Authority: none
Date: 2026-07-06
Author: Observatory Steward (Claude Fable 5)
Home: `planning-inbox/`
Purpose: the ranked list of deep-research lanes that determine whether this project
becomes genuinely dangerous, plus new dangerous-feature candidates not yet in any doc.
Companion to `strategy-layer-dangerous-design.md`. Labels per repo vocabulary.

---

## 1. The danger thesis to validate

Everything below tests one compound claim:

```text
A small operator with (a) longitudinal, scoped, provenance-complete evidence,
(b) cross-surface joins nobody else does (SERP × demand × marketplace × AI answers
× first-party), and (c) an outcome-fed promotion loop, can out-see subscription
tools and out-prove guru agencies at a fraction of their cost.
```

Each research lane either strengthens a leg of this or exposes where it fails.
Knowing where it fails early is itself a competitive edge — we don't build the
non-dangerous parts.

---

## 2. Ranked deep-research lanes

Ranked by danger-leverage: how much the answer changes what we build and how hard
the resulting capability is to copy.

### R1 — GEO / AI-citation selection science `[research topic — highest leverage]`
The question: **what observable page/brand/entity properties correlate with being
cited or mentioned by AI answer surfaces** (AI Overview, ChatGPT, Perplexity,
Gemini), and how volatile is that selection per query class?
Why it's the #1 lane: GEO is young enough that nobody owns the measurement science.
Traditional SEO knowledge is 20 years consolidated; AI-citation behavior is 2 years
old and shifting. Whoever builds a measured (not folklore) model of citation
selection has the rarest asset in the market right now.
Sub-questions: which source types dominate citations per vertical (docs, Reddit,
review sites, brand pages)? does structured data / entity clarity / llms.txt
measurably matter? how do fan-out queries reshape what gets cited? how stable are
citations day-over-day (this sets capture cadence AND honest report language)? what
can DataForSEO AI Optimization actually see vs. what it misses?
Output: AI-surface family design v2; citation-asymmetry workflow spec; volatility
classes for AI evidence; claim-safety language for GEO reports.

### R2 — SERP weakness signal science `[research topic — high leverage]`
The question: **which observable SERP-composition properties actually predict a
beatable position** — UGC/forum results ranking, thin or aged content in top spots,
low domain diversity, missing SERP features, mismatched intent — versus which
"weakness signals" are folklore?
Why: §3 of the strategy design assumes weak-competition detection works. Turning it
from vibes into measurable, hammer-testable signal definitions is what makes
gap-hunting outputs citable instead of guru-flavored.
Output: a signal catalog with definitions computable from SERP snapshots (Tier 2
candidates), each marked measured / plausible / folklore.

### R3 — Evidence unit economics `[research topic — high leverage]`
The question: **what does a maintained scope actually cost per month** (DataForSEO
pricing per endpoint family, panel size × cadence math), versus the decision value
it feeds and versus what Ahrefs/Semrush/eRank/GEO tools charge?
Why: the danger thesis claims cost asymmetry. If a 50-query panel with monthly SERP
+ AI-surface refresh costs a few dollars while competitors pay $100+/mo
subscriptions per seat for shallower, non-owned data — that's the business model.
If the math doesn't work, cadence and panel design must change now, not after spend.
Output: cost model per scope class; recommended panel sizes/cadences; the exact
plan for the reserved $50 validation milestone; feeds NC7 directly.

### R4 — Freshness & volatility empirics `[research topic]`
The question: **how fast do SERPs, rankings, keyword metrics, and AI answers
actually churn, per query class?** Head vs. long-tail, commercial vs. informational,
marketplace vs. web, AI vs. traditional.
Why: capture cadence is the biggest spend lever and freshness self-description
(NC4) is only honest if the volatility classes are grounded. Also enables the
volatility-spike detector (F3 below).
Output: initial volatility class vocabulary with evidence behind each class;
per-family staleness thresholds; cadence recommendations feeding R3's cost model.

### R5 — Outcome attribution methodology `[research topic]`
The question: **how do we honestly say "this improved because of what we did"**
given confounds — seasonality, algorithm updates, competitor motion, marketplace
dynamics?
Why: intervention-attributed proof (NC3 + NC9) is the sentence that closes
customers. Done naively it's guru math; done well (baseline windows, control
queries from the same panel, update-aware annotation) it's the most defensible
claim in the product.
Output: before/after methodology spec for read tools; control-query panel pattern;
required caveat language tiers; what confidence is claimable at what evidence depth.

### R6 — Marketplace search mechanics + legal ceiling `[research topic]`
The question: what actually drives Etsy/Fiverr search placement (observable,
documented, or credibly tested), and **what is legally/ToS-cleanly observable** per
platform (extends research lane E and the extension admission)?
Why: SearchClarity's near-term revenue lives here, and the legal ceiling defines
the family design. Includes: Etsy API capability map, what operator-witnessed
capture can defensibly include, Fiverr's posture, and per-platform risk table.
Output: marketplace family design constraints; extension admission inputs; what
SearchClarity audits can honestly claim per platform.

### R7 — Competitor landscape teardown `[research topic]`
The question: **what do the incumbent tools actually do and where are their
structural blind spots** — SEO suites (Ahrefs/Semrush), marketplace tools
(eRank/EverBee/Sale Samurai), and the new GEO-tracking startups?
Why: "hard to casually copy" requires knowing what they can't or won't do.
Hypothesis to test: none of them join surfaces per-scope longitudinally with
owned data and outcome feedback — their business model (broad index, per-seat
subscription) prevents it. Confirm or correct.
Output: capability matrix; the specific joins/claims only we can make; pricing
context for R3; feature ideas worth stealing openly.

### R8 — LLM-first evidence-tool design (extends lane C) `[research topic]`
The question: what tool-contract shapes make an LLM analyst *measurably better* —
evidence-pack structure, comparison-native outputs, blind-spot injection, citation
handles, context-window economics for large evidence sets, when retrieval needs
embeddings vs. never `[the embeddings sub-question requires owner ruling before any
vector store]`.
Why: §5 of the context dump — perfect schema + row-fetch tools = dumb astronomer.
Output: MCP contract patterns; evidence-pack schema; anti-patterns list.

### R9 — Confidence calibration for strategy outputs `[research topic]`
The question: how to make candidate `confidence` fields mean something —
calibration methods, resolution criteria per candidate type, tracking whether
high-confidence candidates actually pan out (feeds the promotion loop's honesty).
Output: confidence rubric per candidate type; resolution/outcome tracking pattern
(stored consumer-side).

### R10 — Intent & fan-out mapping `[research topic]`
The question: how well can intent be classified from provider data + SERP
composition, and how do AI fan-out queries reshape the demand landscape around a
seed query? Feeds R1 and underserved-intent discovery.
Output: intent dimension design; fan-out family design questions.

---

## 3. New dangerous-feature candidates (not yet in any doc)

Each labeled; none is authorized by this document.

**F1 — Competitor natural-experiment mining.** `[future candidate — high danger]`
Snapshot competitor pages/listings over time; when a competitor changes something
(title, structure, tags, content), align *their* rank/visibility series before and
after. Competitors run experiments constantly and publish the results in public —
nobody harvests them. This converts the whole market into our test lab, using only
public observations and existing families (page snapshots + rank series + NC3
pointed at inferred external interventions). Requires: page-snapshot family, change
detection (Tier 2). Ruling needed only for the family itself, already registered
as deferred.

**F2 — Citation-hub reverse engineering.** `[future candidate — pairs with R1]`
From AI-surface observations, catalog which domains/pages get cited per topic
cluster. The output is an evidence-backed "get mentioned here" target list — digital
PR aimed by measurement instead of guesswork. Dangerous because it turns GEO from
content-tweaking into a targeting problem we can see and others guess at.

**F3 — Volatility seismograph / update detection.** `[future candidate — requires
owner ruling]` Aggregate volatility across panels detects search/AI algorithm
updates from our own data, per-niche impact included. Ruling needed: this is a
cross-scope aggregate read, which the boundaries deny by default. A governed
exception (anonymized, aggregate-only, internal + market_watch scopes only, no
customer_engagement leakage) would need explicit approval and hammer coverage.

**F4 — Demand early-warning.** `[future candidate]` Trend-derivative detection on
keyword series + newly appearing fan-out/related queries = catch rising demand
before difficulty and CPC rise. Mechanically Tier 2 + read-time interpretation;
needs longitudinal depth (time is the ingredient, start panels early).

**F5 — SERP real-estate accounting.** `[near-term candidate once families land]`
Per scope: positions and surface-presence owned across organic + SERP features +
AI citations, as one portfolio series. Turns "how visible are we" into a single
honest, trend-able answer — the spine of every customer report and internal review.

**F6 — Decay & cannibalization detector.** `[near-term candidate]` Own/customer
properties: rank series decaying, multiple URLs competing for one query, freshness
gaps vs. SERP expectations. Pure read-time over existing families; cheap and
immediately useful for both SearchClarity retainers and internal upkeep.

**F7 — Evidence-priced quoting for SearchClarity.** `[future candidate]` Quote
audits/retainers from coverage + capture-cost math (NC5 + NC7): "we already hold
N observations on your niche; closing your blind spots costs $X." Instant-margin
advantage and a sales artifact no competitor can produce. Consumer-side feature;
Observatory only supplies the coverage/cost tools.

**F8 — Cross-engagement playbook mining.** `[future candidate — flagged as the
likely V21 friction case]` Learning which intervention types produce improvements
per niche across engagements. This is exactly the capability that may eventually
*earn* persistent strategy records: it needs durable outcome-linked findings.
Until friction evidence exists, it runs read-time over Kaizen/SearchClarity outcome
records by reference. Watch this one — it is the honest path to future V21, and
also the most seductive path to violating it early. `[persistent form: forbidden
until future V21 ruling]`

**F9 — Query-panel marketplace templates.** `[future candidate]` Reusable,
versioned panel templates per business type (Etsy seller, local service, SaaS,
content site) so a new Neon Ronin child project gets a competent observation
program on day one. Compounds the multi-project advantage; pure governance records.

---

## 4. Kill-risks — what would make this NOT dangerous

Honest validation checks; research these on purpose, not by accident:

1. AI answers may churn too fast for citation tracking to support claims (R1/R4
   decide the honest cadence and language — or shrink the GEO promise).
2. DataForSEO's AI-surface data may lag or distort reality (R1 must compare
   provider-reported vs. spot manual probes before GEO reports lean on it).
3. Unit economics may fail at useful panel sizes (R3 before any recurring spend).
4. Etsy's legal ceiling may cap marketplace depth (R6 defines what SearchClarity
   can ever promise — better to know now).
5. Longitudinal moat takes months to exist — the danger compounds with time,
   which argues for starting panels early and cheap, not big and late.
6. Rights posture (OBR-01) could retroactively poison stored evidence — remains
   the hard gate before long-term storage.

---

## 5. Suggested research order

R3 + R6 first (they gate money and legality and are answerable now, docs-only).
R1 + R2 next (they define the schema-facing science while families are designed).
R4 + R5 alongside the first-slice data (they need a little real evidence to bite).
R7 opportunistically (fast, motivating, sharpens positioning).
R8–R10 as the API/tool design work begins.

Feature rulings to queue for the owner: F3's cross-scope aggregate exception;
F8's V21-watch status; embeddings question from R8. F5/F6 need no ruling — they
ride existing law.

---

## Final rule

```text
Danger is validated, not declared.
Research the legs the thesis stands on; build only the legs that hold.
```
