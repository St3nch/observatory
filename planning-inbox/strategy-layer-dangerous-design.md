# Strategy Layer — Dangerous Design

Status: planning artifact, Authority: none
Date: 2026-07-06
Author: Observatory Steward (Claude Fable 5), at owner request
Home: `planning-inbox/` — this is future design captured while hot, NOT implementation approval
Governing law: `02-boundaries.md` (Strategy/IMI Boundary) and harvest register V21 (amended)

Label vocabulary used throughout:
`[active v0.1 rule]` `[near-term candidate]` `[future candidate]` `[research topic]`
`[forbidden]` `[requires owner ruling]`

---

## 0. The one-paragraph answer

A dangerous strategy layer is not a smarter database. It is a disciplined *process*
sitting on top of an honest one: read-time LLM interpretation over accumulated,
scoped, provenance-complete evidence, triangulated across surfaces nobody else joins
(SERP × keyword demand × marketplace × AI answers × first-party ground truth),
aware of its own blind spots, feeding a promotion loop whose accepted outputs get
executed downstream and whose *outcomes come back as new evidence*. The moat is not
the LLM and not DataForSEO — anyone can rent both. The moat is the longitudinal,
intervention-aligned, rights-clean evidence corpus plus the outcome-fed loop, which
compounds and cannot be casually copied because it takes time, discipline, and
scars to accumulate. `[active v0.1 rule for the framing; the loop matures by phase]`

---

## 1. What "Strategy Layer" should mean

The Strategy Layer is a **boundary name for a set of processes**, not a system with
its own storage. `[active v0.1 rule]` Decomposed:

| Function | What it is | Where it lives | Label |
|---|---|---|---|
| Read-time interpretation | LLM reasoning over evidence packs in a session | LLM session only | active v0.1 rule |
| Opportunity discovery | Gap-hunting scans (demand present × competition weak × presence absent) | Read-time tool calls; outputs ephemeral | active v0.1 rule |
| Recommendation drafting | Structured candidate objects (see §5) produced in-session | Ephemeral until promoted | active v0.1 rule |
| Competitive intelligence | Competitor SERP/listing/AI-citation observations + read-time synthesis | Evidence families in Observatory; synthesis in session | active v0.1 rule (families per register) |
| Customer-facing strategy | Report sections, audit recommendations, action plans | SearchClarity owns storage and delivery | active v0.1 rule |
| Internal project strategy | Improvement candidates, decisions, experiments | Kaizen owns storage and governance | active v0.1 rule |
| Promotion | The contract moving accepted candidates into a named consumer with evidence IDs attached | Contract, not storage; consumer review queues receive | near-term candidate (v0.3 proof) |
| Tactic ingestion | Capturing + triaging strategies found online | Capture = candidate Observatory family; verdicts = review records (see §4) | requires owner ruling |
| Recurring scans | Scheduled read-time scans over *existing* evidence producing review-queue candidates | Scheduler downstream (Neon Ronin-shaped); no new storage | future candidate (v0.4) |
| Persistent strategy records | Durable findings/opportunities/experiment outcomes with lifecycle | Future V21 boundary only | future candidate — friction evidence + owner approval required |

What belongs in the Observatory: evidence, capture governance, query panels, coverage
metadata. What belongs downstream: every accepted conclusion, every customer artifact,
every decision, every task. What belongs nowhere yet: durable strategy truth.
`[active v0.1 rule]`

---

## 2. Data the Strategy Layer would use

Mapped to the Tier model (Tier 0 raw / Tier 1 normalized / Tier 2 mechanical derived /
Tier 3 ephemeral interpretation / promoted = lives in a consumer):

| Data | Tier / handling | Status |
|---|---|---|
| Raw DataForSEO payloads | Tier 0 blob + hash; never read directly by strategy prompts — read tools serve Tier 1 | active rule; capture gated by OBR-01 |
| Normalized keyword demand/difficulty/trend | Tier 1, provider-attributed, disagreement preserved | near-term (first slice) |
| SERP snapshots incl. AI Overview | Tier 1, polymorphic item families (no caveman table) | near-term (first slice) |
| Rank/visibility time-series | Tier 1, panel-anchored | near-term |
| Competitor public pages (point-in-time snapshots) | Tier 0 blob + Tier 1 extracted fields | future candidate (deferred family) |
| Marketplace listing/gig data | Tier 0/1, per-platform admitted instruments only | future candidate (deferred; extension admission pending) |
| AI/LLM visibility observations (mentions, citations, fan-out, AI Overview) | Tier 1, distinct families, model/version/date dimensions, requested-vs-actual settings both kept | near-term after first slice |
| Backlink/domain authority signals | Provider-reported observations could be Tier 1; a stored link *graph* is a different beast | research topic + requires owner ruling (new family, not in register) |
| Local SEO signals (GBP, local pack, maps presence) | Same posture as above | research topic + requires owner ruling (new family) |
| Customer first-party data | Read-time overlay ONLY (NC9); never stored | active v0.1 rule; storage is forbidden absent a future governed ruling |
| Historical drift/change records | Tier 2 mechanical ("what changed between snapshots") + provider drift fingerprints (NC12) | future candidate |
| Online strategies/tactics found by the owner | New capture family — see §4 | requires owner ruling |
| Outcome evidence (did the promoted recommendation work) | Stored in the consumer that executed (Kaizen returns, SearchClarity outcomes); read back by reference + first-party/rank series | active rule for location; loop matures v0.3+ |

Rule of thumb `[active v0.1 rule]`: raw is archived, normalized is served, mechanical
derivation is labeled, interpretation is ephemeral, and anything accepted is promoted
— nothing interpretive is "cached for later" anywhere.

---

## 3. What actually makes it dangerous

Blunt version: the capabilities below are dangerous because each one is a *join the
market doesn't do*, grounded in evidence competitors don't keep.

1. **Weak-competition detection.** SERP composition analysis at read time: thin
   content in top results, aged snapshots, forum/UGC results ranking (a classic
   weakness signal), missing SERP features, low-authority domains holding positions.
   Dangerous because it converts "keyword difficulty score" (a provider opinion)
   into observed, citable weakness. `[active v0.1 rule — needs SERP snapshots only]`
2. **Underserved-intent discovery.** Demand observed (volume/trend) × intent
   classification × SERP results that answer a *different* intent than the query
   carries. The gap between what people ask and what ranks is the cheapest
   opportunity class on the internet. `[active v0.1 rule capability; intent data
   near-term]`
3. **Three-legged gap hunting.** Demand present + competition weak + our/customer
   presence absent, in one pass, per scope. Any tool shows one leg; the join is the
   edge. `[active v0.1 rule]`
4. **AI-citation asymmetry.** Queries where AI surfaces cite competitors but not
   us/the customer — plus the *why* (which pages get cited, what they have that ours
   lack, observed from citation sources). GEO is young enough that systematic
   asymmetry detection is a genuine head start. `[near-term candidate — needs
   AI-surface families]`
5. **Decay and freshness-gap detection.** Rank series trending down before it's
   obvious; top results whose snapshots show staleness a fresh page could beat;
   panels whose SERP volatility spiked (something changed — investigate).
   `[near-term candidate — needs longitudinal depth, which only time builds]`
6. **Marketplace listing-gap analysis.** Category demand vs. listing-field weakness
   (tags, titles, media, price bands) across competitor listings, per admitted
   platform. `[future candidate — deferred families + instrument admission]`
7. **Boring-but-profitable niche discovery.** market_watch scopes scanning for
   demand-stable, competition-thin, monetizable clusters with no incumbent moat —
   ranked by evidence, not vibes, with cost-to-close-blind-spots attached (NC7).
   `[future candidate — v0.4 recurring scans]`
8. **Intervention-attributed proof.** Before/after windows aligned to what was
   actually changed (NC3) + first-party overlays (NC9) = "we did X, this improved,
   here is the evidence" — the sentence that closes customers and compounds
   reputation. `[near-term candidate]`
9. **Cross-surface strategy synthesis.** One workflow connecting SEO + GEO +
   marketplace + business goal per scope, because the evidence lives in one place
   with one scope model. This is the structural advantage of the whole architecture.
   `[active framing; matures with families]`
10. **Calibrated honesty as a feature.** Every output carries confidence, evidence
    labels, freshness, and blind spots. Customers and Kaizen can audit any claim to
    its observation IDs. Guru shops cannot copy this without rebuilding their whole
    epistemics. `[active v0.1 rule]`

What is NOT dangerous and should never be pitched as such `[forbidden]`: volume of
recommendations, confident tone, secret sauce claims, guaranteed rankings, or any
output that can't survive "show me the observation IDs."

---

## 4. Online strategy/tactic ingestion (anti-guru pipeline)

Owner need: learn from tactics found on Reddit/YouTube/agency blogs without letting
folklore become doctrine. Design: `[requires owner ruling to admit the capture
family; pipeline shape is a near-term candidate]`

**Step 1 — TacticCapture (observation, telescope-clean).** A tactic found online is
captured as an *observation of a claim*: someone claimed X at URL Y on date Z. That
passes the admission test — it records what was observed, not whether it's true.
Candidate fields: `capture_id`, `source_url`, `platform`, `author_handle`,
`published_at` (if known), `captured_at`, `capturedBy`, `operator_intent`,
`claim_summary` (what they say happens), `tactic_description` (what they say to do),
`claimed_evidence` (screenshots? case study? nothing?), `evidence_label`
(usually `observation_point_in_time` or `inference_internal`), `rights_class`
(quote/excerpt handling), `raw_pointer` (page snapshot/screenshot hash).
Storage location: candidate deferred Observatory family — or flat files under a
`captures/` convention until ruled. `[requires owner ruling]`

**Step 2 — Quarantine.** Every capture lands with Authority: none. Nothing captured
is usable in customer work, internal doctrine, or recommendations by virtue of
existing. `[active rule the moment any capture exists]`

**Step 3 — Triage (human-owned review verdict).** A reviewer (owner, or LLM-drafted
+ owner-approved) assigns: **claim type** (ranking tactic / GEO tactic / marketplace
tactic / measurement method / tool claim); **mechanism hypothesis** (why would this
work — if no plausible mechanism, grade collapses); **evidence grade** E0 anecdote /
E1 screenshot / E2 described experiment / E3 reproducible experiment with data /
E4 independently replicated; **hat class** white / gray / black / unknown; **risk
class** (penalty risk, platform-ToS risk, brand risk, customer-harm risk);
**suitability**: `customer_eligible_after_local_proof` | `internal_experiment_only` |
`mechanism_study_only` | `rejected`. Verdicts are mutable governance records, not
observations — cleanest home is a review-queue record (Neon Ronin-shaped) or a thin
governance table beside query panels. `[requires owner ruling on verdict storage]`

**Step 4 — Hard routing rules.** `[active rules if pipeline is adopted]`
Black-hat or platform-ToS-violating tactics are **mechanism_study_only, always** —
understood to defend against and to recognize competitor behavior, never executed,
never customer-adjacent. Gray-hat is internal_experiment_only at most, and never on
customer properties. Nothing reaches `customer_eligible` without local experiment
evidence (E3 by our own hands). Author fame is not evidence. "It worked for them"
is E1 at best.

**Step 5 — Experiment proposal.** A promising tactic becomes an internal experiment
proposal (a §5 candidate object) promoted to Kaizen/Neon Ronin, run on internal
scope properties, with the metrics defined *before* the test and outcome windows
read through NC3.

**Step 6 — Doctrine promotion.** Only after our own experiment evidence does a
tactic graduate — as a Kaizen decision or SearchClarity service-template change,
citing both the original capture and the local outcome observations. The tactic
library never self-promotes. `[active rule if adopted]`

Anti-guru invariants: a claim is evidence *about the claim*, never about reality;
evidence grades never inflate on repetition (100 gurus repeating one anecdote is
still E0); mechanism-free tactics stall at triage; every graduated tactic carries
its full provenance chain from Reddit post to local proof.

---

## 5. Strategy outputs (candidate object shape)

All outputs are **ephemeral candidate objects** — they exist in-session and in the
promotion payload, never in an Observatory table. `[active v0.1 rule]`

Output types: opportunity candidate · content gap candidate · SERP weakness finding ·
GEO visibility finding · competitor weakness note · marketplace listing improvement
candidate · customer recommendation draft · internal experiment proposal · Kaizen
task-packet candidate · Neon Ronin workflow candidate · SearchClarity report section
candidate · tactic experiment proposal (§4).

Required fields on every candidate `[active v0.1 rule — this IS the promotion
contract's payload shape; near-term candidate to formalize as a JSON schema in v0.3]`:

```yaml
candidate_type:        one of the types above
scope_id / scope_class: where this applies
evidence_refs:         stable observation IDs (NC8) — REQUIRED, no refs = no candidate
evidence_labels:       S1 vocabulary summary of what kind of evidence backs this
confidence:            calibrated (e.g. low/medium/high + one-line basis)
blind_spots:           what the Observatory does NOT know that could change this (NC5)
freshness:             age/volatility statement of underlying evidence (NC4)
rights_provenance:     rights classes of cited evidence; anything restricted flagged
risk:                  what happens if this is wrong or executed badly
recommended_next_action: one concrete step
destination:           SearchClarity | Kaizen | Neon Ronin | named future consumer
human_review:          REQUIRED — always true; named review queue
expiry_note:           candidates go stale; unpromoted candidates simply evaporate
```

A candidate without evidence refs, without a destination, or marked no-review-needed
is malformed and must be refused by the promotion contract. `[active v0.1 rule]`

---

## 6. Guardrails

Forbidden — the Strategy Layer must never become `[forbidden, all]`:

- a source of truth (its outputs are proposals until a consumer accepts them)
- a durable recommendation database or hidden side store ("session notes" tables,
  "scratch" schemas, and cached-candidates files are the same sin wearing a hat)
- a black-box (any output whose evidence refs can't be walked is invalid)
- an auto-publisher or auto-client-advisor (human review is structural, not polite)
- a spam engine (no tactic executes at scale without per-scope human approval;
  black/gray-hat routing per §4 is absolute)
- a hidden decision-maker (decisions live in Kaizen, deliveries in SearchClarity,
  execution in Neon Ronin — the layer proposes, only consumers dispose)
- a duplicate Kaizen (no roadmaps, no governance state, no approval records here)
- a place where customer private data is stored (overlay only, per Q3/S4/NC9,
  absent an explicit future governed ruling)
- a spender (no provider pull without recipe + ceiling + human gate; interpretation
  never triggers capture autonomously)

Boundary rules `[active v0.1 rule]`: gap-scan and comparison outputs are ephemeral;
confidence must cite its basis; every customer-facing sentence must be reconstructible
from observation IDs + the S3 volatility caveat; anything that smells like Tier 3
persistence goes to the future-V21 question, not into a table.

---

## 7. Build path

**v0.1 — Read-time strategy interpretation** `[active now]`
Goal: prove the LLM can produce §5-shaped candidates from evidence packs.
Inputs: existing docs; later, first-slice evidence. Outputs: session candidates,
prompt/workflow patterns documented in planning-inbox. Must not build: any storage,
any tool code, any scheduler. Proof: one candidate a human reads and says "that is
grounded and useful."

**v0.2 — CapturePackage + tactic ingestion** `[near-term candidate]`
Goal: every capture (provider, manual, tactic) shares one contract (NC10) including
`evidence_label`; TacticCapture pipeline operating on flat files.
Inputs: NC10 research (lane B), §4 design, owner ruling on the tactic family.
Outputs: CapturePackage v0.1 schema + examples + invalid examples; first triaged
tactic captures. Must not build: Postgres, runner automation, verdict tables.
Proof: one real Reddit/YouTube tactic captured, triaged, and correctly routed
(including one correctly *rejected*).

**v0.3 — Promotion workflow proof** `[near-term candidate — roadmap #18]`
Goal: one full loop: evidence → read-time candidate → promoted into a real consumer
→ human reviewed → executed → outcome observed and read back by reference.
Inputs: first-slice evidence, one live SearchClarity or internal question.
Outputs: promotion contract schema; one closed loop with citations end-to-end.
Must not build: recurring scans, strategy storage. Proof: the outcome readback —
the loop closing is the whole point.

**v0.4 — Recurring opportunity scans** `[future candidate; requires owner ruling on
scheduling posture]` Goal: scheduled read-time scans over *existing* evidence
(no new capture, no spend) emitting candidates into consumer review queues.
Inputs: v0.3 contract, panels with history, a scheduler home (Neon Ronin-shaped).
Outputs: recurring gap/decay/asymmetry candidates. Must not build: auto-capture,
auto-spend, candidate persistence outside consumer queues. Proof: a scan surfaces
an opportunity a human hadn't noticed, and at least one scan's output is correctly
boring (honesty check).

**v0.5 — Customer-facing report support** `[future candidate]`
Goal: SearchClarity report sections assembled from evidence packs + candidates,
with citations, freshness, and S3 caveats flowing automatically.
Inputs: v0.3/v0.4, SearchClarity consumer doc, report templates.
Outputs: report-section candidate pipeline into SearchClarity's own store.
Must not build: report storage here; auto-delivery. Proof: a paying customer report
where every claim walks back to observation IDs.

**Later — persistent strategy records** `[future candidate, future V21 boundary
only]` Trigger: demonstrated friction — e.g., candidates repeatedly re-derived at
real cost, or outcome-learning demonstrably blocked by statelessness. Requires:
friction evidence, accepted schema, rights/provenance/lifecycle rules, human
approval, register amendment. Until then: `[forbidden]`.

---

## 8. Database implications (suggestion only — nothing here is implementation approval)

**Definitely needed soon** (all already registered): scope registry, query panels,
provider job/capture-request records, SERP snapshot families, keyword observation
families, event log, blob pointer/hash records.

**Likely later:** AI-surface families; page-snapshot family; marketplace-snapshot
family; Tier-2 change/drift records; coverage/blind-spot statistics; TacticCapture
family `[requires owner ruling]`.

**Maybe never:** stored backlink graph (provider-reported backlink *observations*
maybe; a maintained link graph is a product in itself — earn it or buy it at read
time); local-SEO families (unless a business demands them); any embedding/vector
store over observations (read-time retrieval may suffice — research topic).

**Dangerous unless governed** (future V21 territory, `[forbidden]` until then):
opportunity/finding/recommendation tables; tactic *verdict* tables inside
Observatory; experiment-result tables; any "candidate cache"; customer first-party
storage; cross-scope intelligence aggregates.

Placement rule (restating law): raw payloads in blob storage with DB pointers;
normalized records in Observatory tables; mechanical derivations labeled Tier 2;
candidates ephemeral; promoted decisions in the consumer that owns them.

---

## 9. Example workflows

**9.1 SearchClarity customer Etsy listing audit.** Engagement scope created →
query panel drafted from customer's target terms → existing evidence checked
(coverage tool) → gaps trigger a recipe-driven, ceiling-gated pull request (human
approved) → read-time pass: rank/visibility for the listing's terms, SERP + AI
Overview composition, competitor listing observations (manual/admitted capture),
customer's Etsy Stats as read-time overlay (never stored) → outputs: SERP weakness
findings, listing improvement candidates, report section candidates, each with
evidence refs + freshness + S3 caveats → promoted into SearchClarity's report
pipeline → human review → delivery → 30/60-day before/after windows via NC3 =
next report's proof section. `[near-term shape; marketplace legs deferred]`

**9.2 Neon Ronin internal niche selection.** market_watch scope over 3 candidate
niches → panels per niche → demand + SERP-composition + AI-surface evidence
accumulated over several capture cycles → read-time three-legged scan ranks niches
with confidence + blind spots + cost-to-close (NC7) → internal opportunity candidate
promoted to Kaizen as an improvement/decision input → decision recorded in Kaizen;
chosen niche's scope graduates from market_watch to internal. `[future candidate —
needs market_watch depth]`

**9.3 GEO citation asymmetry.** Scope's query panel run against AI-surface families
(DataForSEO AI Optimization) → tool: `find_ai_citation_absence_gaps` → queries where
competitors are cited and we are not → read-time inspection of *which* competitor
pages are cited (page snapshots if family exists; otherwise noted as blind spot) →
GEO visibility finding candidate: the asymmetry, the cited pages' observable
properties, confidence, and an experiment proposal (create/adjust a page, measure
citation change over N weeks) → promoted to Kaizen (internal) or SearchClarity
(customer). `[near-term candidate once AI-surface families land]`

**9.4 SERP gap-hunting from DataForSEO snapshots.** Panel snapshots refreshed →
`find_weak_serp_competition` + `find_demand_without_presence` at read time →
candidate list of queries with observed thin/stale/UGC-heavy SERPs and demand →
each becomes a content-gap candidate with the exact snapshot IDs as proof →
promoted to the owning consumer's queue; nothing persisted here; if the human
ignores them, they evaporate — correctly. `[active shape; first-slice data]`

**9.5 Capturing an online tactic.** Owner finds a YouTube video claiming a parasite-
SEO variant ranks in days → TacticCapture: URL, author, date, claim, tactic,
claimed evidence (E1 screenshots), raw snapshot hash → quarantine → triage:
mechanism plausible (authority piggybacking), hat class gray-to-black, platform
risk high, suitability `mechanism_study_only` → routed: never customer work,
documented mechanism note promoted to Kaizen as defensive knowledge ("recognize
this pattern in competitor SERPs") → a second capture, a white-hat internal-linking
experiment from an agency blog (E2), triages to `internal_experiment_only` →
experiment proposal promoted to Kaizen → run on an internal property → E3 local
evidence → graduates to SearchClarity service-template consideration.
`[near-term candidate pending §4 ruling]`

---

## 10. Final recommendation

**Build first (in order):** (1) SearchClarity consumer requirements doc — it is the
consumer with a real near-term workload and it forces the read-tool contracts to be
honest; (2) the promotion contract / candidate JSON schema (v0.3 prep — §5 shape);
(3) CapturePackage v0.1 with `evidence_label` (lane B), because §4 and all capture
depends on it; (4) the TacticCapture design as a one-page family proposal for owner
ruling. All docs-only.

**Do not build yet:** any storage, any scheduler, recurring scans, verdict tables,
backlink/local families, embeddings, anything in §8's dangerous list, and nothing
that spends the reserved $50 before the provider-validation milestone.

**Next artifacts:** `consumers/searchclarity-requirements.md`;
`contracts/candidate-object-v0.1.md` (or planning-inbox first);
`contracts/capture-package-v0.1.md`; `proposals/tactic-capture-family.md`.

**Owner rulings still needed:** admit TacticCapture as a deferred Observatory family
(or keep captures as files)? · where do triage *verdicts* live (Neon Ronin review
queue vs. thin governance table)? · backlink and local-SEO families — research or
drop? · recurring-scan scheduling posture (touches the no-autonomous-anything rules
even though scans are read-only)? · embedding/vector store over observations —
research topic or maybe-never?

---

## Final rule

```text
The Strategy Layer is a verb, not a noun, until friction proves otherwise.
Everything it says must walk back to observation IDs.
Everything it convinces anyone of must live somewhere that has an owner.
```
