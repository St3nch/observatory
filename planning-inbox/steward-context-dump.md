# STEWARD_CONTEXT_DUMP — The Observatory

Status: advisory context, Authority: none except where it cites owner rulings
Written: 2026-07-06 by the Observatory Steward (Claude Fable 5)
Purpose: preserve the Steward's full analytical context — cross-repo audit findings,
design reasoning, leanings, and warnings — so no future agent has to rediscover it.
Where this conflicts with `02-boundaries.md` or the harvest register, those win.

---

## 1. Why this document exists

The chat context that produced this repo contained a deep read of four ancestor
repos (v-ecosystem-docs, kaizen-docs, neon-ronin, searchclarity), a full boundary
audit, a walked harvest register, and several owner rulings. The docs capture the
decisions. This file captures the *reasoning and remaining design knowledge* behind
them, so continuity survives without Claude.

---

## 2. The cross-repo boundary audit — full findings

The original audit evaluated four ownership models for the Observatory:

- Option A (Kaizen-owned internal DB): rejected — violates Kaizen's own 030B line
  ("Kaizen does not become Observatory") and Decision 0009's one-canonical-home rule.
- Option B (inside Neon Ronin): rejected — Neon Ronin's own core/17 forbids raw
  external provider payloads as inputs to its layer; putting portfolio-wide evidence
  inside one downstream project traps it (the exact anti-pattern Kaizen Decision
  0010 warns about: "observations should not be trapped inside the project that
  first requested them").
- Option C (independent project): right ownership, incomplete alone.
- **Option D + C ownership (adopted): independent, Kaizen-governed project whose DB
  stores only evidence + mechanical derived indexes; interpretation is a separate
  boundary.** "Independent" means independent repo/database/authority boundary,
  NOT independent of Kaizen governance.

Conflicts found between the repos (still true, mostly unresolved on their side):

- **C1 (high):** "Observatory" name collision. Kaizen's parked Observatory =
  external evidence store (provider data in, top-down). Neon Ronin's "Observatory"
  (docs/core/04, ADR-004) = internal sanitized-signal exchange (workspace
  observations in, bottom-up). Different provenance classes, different privacy
  risk, opposite trust models. Resolution adopted: this project keeps the name;
  Neon Ronin renames its layer in its own docs. **That Neon Ronin doc change has
  not been made yet.**
- **C2 (high):** Kaizen Decision 0010's envelope includes derived trends,
  opportunity candidates, strategy hypotheses, experiments — but Result 506 (030B)
  excludes strategy/recommendation records. 030B explicitly did not amend 0010,
  so Kaizen's accepted doctrine and its active parking lot still disagree. **An
  eventual M19 reopening packet should carry a small explicit Decision 0010
  amendment recording the raw/derived split**, or the broad envelope will silently
  pull strategy tables back in.
- **C3 (medium):** neon-ronin/research-docs/r10 is overfitted to SearchClarity —
  it hardcodes a 12-factor scoring formula with Etsy/Fiverr/Pinterest factors and
  migrates SearchClarity r05 worked examples wholesale. This violates Neon Ronin's
  own ADR-004 rule ("a concrete business-specific scoring formula must not become
  core doctrine"). Treat r10 as workspace-adapter input, never as architecture.
- **C4 (medium):** SearchClarity docs assume signals flow to Neon Ronin
  ("handoff_status: Sent to Neon Ronin"); Kaizen assumes downstream layers consume
  Observatory evidence. Both are true only because there are two separate flows
  (see §3). No ancestor doc states that separation; only this repo does.
- **C5 (low):** kaizen-docs internal drift — ROADMAP_V0.4's milestone body still
  shows M18 as "not authorized" while the checkpoint and CURRENT_STATE show M18
  closed (Operator Workbench v0.1 implemented, Result 514). Docs-only tidy on
  Kaizen's side.

---

## 3. The two flows (never merge them)

```text
FLOW B (external, top-down — OURS):
  providers / admitted capture instruments -> Observatory evidence
  provenance: provider-attributed, rights-classified, customer-clean

FLOW A (internal, bottom-up — THEIRS):
  workspace operational work -> human-approved sanitized signals
  -> Neon Ronin's shared-intelligence layer
  provenance: customer-derived even after sanitization; re-identification risk
```

Contamination risk #1 in this whole system is muddling these. A listing snapshot
captured *during* customer work is Flow A material (workspace-owned) even though
the fields are public; an Observatory observation must come from an
Observatory-initiated, admitted capture job. A customer request may *trigger* a
pull; the requester lives in job metadata (Kaizen Decision 0010's model:
shared observation ≠ request ≠ provider job/cost ≠ project relevance).

---

## 4. The Tier model (the enforceable raw/derived line)

```text
Tier 0: raw/near-raw provider artifacts — object/file storage, rights-gated,
        pointer + hash in DB
Tier 1: normalized observations — provider-attributed, provenance-complete
Tier 2: mechanical derived indexes — dedup, normalization, classification;
        labeled derived; admitted only when no judgment is involved
Tier 3+: interpretation — clusters, trends, scores, opportunities, strategies.
        NOT stored. Compute-on-read by the LLM; accepted outputs promote out.
```

The Tier 2/3 test (memorize this): **if producing the record requires judgment,
weighting, or a scoring-method version, it is interpretation and stays out.**
A SERP-feature classification is Tier 2. A keyword-difficulty *opinion* is Tier 3.
A provider's keyword-difficulty *number* is a Tier 1 observation (it's what the
provider said, attributed — an observation about the provider's model, not truth).

---

## 5. What makes the connected LLM "dangerous" — the goal decomposed

The owner's three example sentences each imply concrete data requirements:

- **"This improved"** = longitudinal comparability (same query × locale × device ×
  URL, append-only, repeated) + an intervention timeline. Interventions live
  project-side (Kaizen returns, SearchClarity action plans); the read tools accept
  them as an external timeline and return aligned before/after windows (NC3).
  For customers, ground truth is their first-party data → NC9 overlay, never stored.
  For owner properties, ground truth is `internal`-scope GSC-style data (V17).
- **"Money-making gap"** = three legs, all observable: demand present (keyword
  volume/trend), competition weak (SERP composition, competitor observations),
  our presence absent (rank/visibility for the scope's properties). A gap is the
  LLM noticing all three at once at read time. If any leg's data family is missing,
  the LLM cannot say the sentence honestly — this is the acceptance test for the
  family list.
- **"Stop using this keyword on this page"** = page-level content awareness via
  point-in-time public-page snapshots (a legitimate telescope act) — never a
  living content graph (Veda ADR-002 blood was spilled here; the line is:
  snapshot of what a page showed the world at time T = in; editorial model of
  what a site should be = out). This is also why the owner likely needs only one
  Firecrawl-like feature (single-page extraction), not a crawler.
- **"LLM citation dominance"** = the AI-surface families (mentions, citations,
  fan-out, brand entity, AI Overview), sourced from DataForSEO (owner ruling Q4),
  with model/version/date dimensions preserved.

Second half of dangerous: **the read tools matter as much as the schema.** A
perfectly modeled database with fetch-one-row tools produces a dumb astronomer.
Tools must serve comparisons natively (deltas, "what changed since T",
presence/absence flips), self-describe freshness/volatility, report blind spots,
and carry stable citation IDs (NC1, NC4, NC5, NC8).

---

## 6. Dimension model (for eventual schema work)

Observations should be dimensioned on, at minimum: query/keyword, engine/surface,
location (provider location code), language, device, capture timestamp, provider +
endpoint family, and scope. AI-surface observations add: model, model version where
reported, requested-vs-actual settings (e.g., web_search divergence — both must be
kept, per the Veda corpus finding), and prompt/panel identity. Provider-reported
`ai_search_volume` and normal `search_volume` stay distinct fields forever.
Query panels (NC6) are the longitudinal backbone: named, versioned query sets per
scope, evolved from Veda's KeywordTarget with the same governance-vs-observation
posture and the same deliberate no-FK to snapshots (correlation by shared fields,
never structural — so deleting a panel entry can never damage history).

---

## 7. Consumer requirement sketches (pre-work for the consumer docs)

**SearchClarity (write this doc first):** needs, per engagement scope — SERP +
rank + AI-surface evidence for a customer's target queries; competitor listing/gig
observations (deferred family + admitted instrument); before/after windows aligned
to its action plans (NC3); first-party overlay (NC9); citation IDs + volatility
caveat language (S3) flowing straight into report templates; blind-spot reports to
scope what an audit can honestly claim. Its own layer keeps: customers, orders,
intake, reports, consent, deletion, QC, pricing, action plans, outcomes. Its
claim-safety rules (no guarantees; observed-on-date language) constrain what read
tools should even make easy to say.

**Kaizen:** consumes by reference only. Needs stable observation/insight IDs
citable in Markdown artifacts; governance events *about* the Observatory
(approvals, capture authorizations, budget ceilings) live in kaizen_core, never
here. The M19 reopening packet will need: this repo's boundary docs, the OBR-01
disposition, a Decision 0010 amendment (see C2), and real-use evidence from the
Operator Workbench week.

**Neon Ronin:** wraps our API in its external-integration contract (core/18):
workspace-scoped permission, read + queue action classes, audit records, no
autonomous spend (a paid pull request is spending → human gate, per its own
hard-no rules). Its agents get evidence packs and promotion targets, never SQL.
Owed on their side: rename their internal "Observatory" layer.

**Generic future website project:** identical pattern to SearchClarity minus the
customer layer — search-before-collect (query existing evidence first, request
pulls only for gaps), which mirrors Kaizen's search-before-create economy rule.

---

## 8. First implementation slice (when it is finally authorized)

Smallest defensible slice, refined across both audits: one provider (DataForSEO),
one or two evidence families (SERP snapshots + keyword metric snapshots), Tiers
0–1 only, single Postgres deployment, typed read API with evidence packs, manual
human-approved recipe-driven pulls with hard row/cost ceilings, rights-classified
rows, freshness self-description and citation IDs from day one (NC4/NC8 — brutal
to retrofit), and a hammer suite including the fail-closed rights path. Success
criterion: one real SearchClarity or Neon Ronin research question answered from
stored evidence and cited by stable ID in a Kaizen artifact. Everything else —
Tier 2 indexes, more providers, page snapshots, extension, drift detection —
earns its way in afterward. The reserved ~$50 is the fuel for exactly this
provider-validation milestone and nothing earlier.

## 9. Hammer priorities (what to break first)

In order: append-only enforcement on observation + event tables (update/delete
must fail at DB level); cross-scope read/FK violation probes; provenance
suppression attempts (insert without source/capturedAt/rights → rejected);
the anti-VEDA-Brain boundary probe (attempt to store a score/recommendation/
customer record → rejected); rights fail-closed path; rollback mid-ingest;
duplicate-capture concurrency; deterministic read-tool ordering. Per ADR-006,
hammers run as part of every provider/instrument admission, and per Project V
doctrine, a change without hostile-path coverage has not cleared the gate.

## 10. Ranked failure modes (carry this list forward)

1. Building against Kaizen Decision 0010's broad envelope instead of the narrow
   evidence-only definition → strategy/evidence mongrel (C2 unresolved upstream).
2. Name-collision leakage: Neon Ronin sanitized-signal semantics bleeding into
   evidence schema, or vice versa (C1; their rename still pending).
3. SearchClarity overfit — r10's 12-factor Etsy scoring becoming the implicit
   data model ("SearchClarity with extra steps").
4. Customer contamination via engagement-captured snapshots entering shared
   storage (the Flow A/B muddle, §3).
5. Rights violation: long-term DataForSEO storage before OBR-01 — could poison
   years of "clean" evidence retroactively. Fail closed.
6. Premature schema before the definition work is finished (the exact failure
   Kaizen Results 506/508 already blocked once).
7. Kaizen drifting into being the warehouse because references feel slower than
   copies.
8. The standing-strategy-layer re-entry attempt — it already happened once in
   planning (working-notes §6 pre-edit); expect it to keep trying under new names.
9. JSON sludge: semantic truth hiding in blobs instead of promoted, labeled fields.
10. Tool-shape failure: perfect schema, row-fetch tools, dumb astronomer (§5).

## 11. Steward leanings on open questions (advisory only, not rulings)

- Physical infrastructure: one Postgres deployment, separate database/schema, is
  fine for years; logical/governance independence is what matters now.
- Repo strategy: docs and eventual code both live in this repo unless/until a
  platform repo is earned; onboard as a Kaizen-governed project the way Neon Ronin
  was (M17R pattern) when M19 reopens.
- Firecrawl: expect the answer to be "one feature (single-page scrape) or nothing";
  decide inside the page-snapshot family drill-in, after the extension's admission
  review, not before.
- Freshness/volatility classes: start with a small controlled vocabulary
  (e.g., serp_volatile / metric_monthly / page_slow / ai_surface_very_volatile)
  rather than numeric thresholds; thresholds are research lane D/F output.
- Evidence ID format: opaque, stable, prefixed by family (e.g., obs_serp_...,
  obs_kw_...) so citations are self-describing in Markdown; exact format is
  research lane B output.
- Etsy: assume the API path is the only durable production path; everything else
  is interim evidence. Plan accordingly and it will never bite.

## 12. Source map (where the law lives upstream)

- Telescope/purity: v-ecosystem-docs/ecosystem/decisions/ADR-001, -002, -003.
- Hammer law: ADR-006 + project-v/hammer-doctrine.md (+ neon-ronin core/19).
- Schema patterns: v-ecosystem-docs/veda/schema-reference.md, observatory-models.md,
  data-boundaries.md, evidence-and-source-provenance.md, providers/registry.md.
- DataForSEO prior art: v-ecosystem-docs/transition-steward/* + dataforseo-json/
  (inheritance evidence only — V26).
- Rights/request/observation split: kaizen-docs/04-design-decisions/0010 (+ 0005,
  0009); parking-lot law: 03-research-results/506 (030B); roadmap gates:
  ROADMAP_V0.4.md M19 + OBR table; current Kaizen state: Result 514, M18 closed.
- Boundary hygiene: neon-ronin/docs/core/11, /13, /17, /18, ADR-004.
- Provenance vocabulary + capture compliance + claim safety: searchclarity/docs/
  operations/data-sources/agent-data-acquisition-strategy.md,
  records-and-consent/recordkeeping-and-consent.md, r05, r07.

---

## Final note

Everything decided is in `02-boundaries.md` and the harvest register. Everything
argued is here. If a future agent finds this file persuading them to store an
interpretation, re-read §4 until it stops.
