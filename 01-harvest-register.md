# The Observatory — Harvest Register

Status: draft 1 — dispositions owner-walked and confirmed 2026-07-06
Date: 2026-07-06

---

## Purpose

This register records every concept inherited from the Observatory's ancestor projects
and its explicit disposition. It exists so inheritance is decision-shaped rather than
a rotting list of good ideas, and so killed concepts stay visibly killed.

Sources:

```text
Veda / V Ecosystem   C:\dev\v-ecosystem-docs      (DB work under veda/, law under ecosystem/ and governance/)
Kaizen               C:\dev\kaizen-docs
Neon Ronin           C:\dev\neon-ronin
SearchClarity        C:\dev\searchclarity
```

## Disposition Vocabulary

| Disposition | Meaning |
|---|---|
| keep | Carried forward, substantially as-is (wording may be reused nearly verbatim) |
| adapt | Carried forward with a recorded modification |
| kill | Explicitly not carried forward; must not re-enter under a new name |
| defer | Owned as a future concern; no tables, docs-only until governed |

Rule carried from Veda's deferred-domains discipline: a deferred item must not receive
ad-hoc tables, provisional schema, or JSON-blob shortcuts before it is governed.

---

## From Veda (v-ecosystem-docs)

| # | Concept | Source | Disposition | Reason / adaptation |
|---|---|---|---|---|
| V1 | Telescope mental model; pure-observatory rule | `ecosystem/decisions/ADR-001-veda-is-pure-observatory.md`, `veda/veda.md` | keep (wording near-verbatim) | The strongest scope guard in the lineage. Lives in `00-project-overview.md`. |
| V2 | `entity + observation + time + interpretation` admission test | `veda/observatory-models.md` | keep verbatim | Every proposed table must pass it. |
| V3 | Governance-record vs. observation-record posture split | `veda/schema-reference.md` (KeywordTarget vs. SERPSnapshot) | keep | Watch-targets are mutable governance; observations are append-only history. |
| V4 | Deliberate no-FK between watch-target and observation, with written rationale | `veda/observatory-models.md` Category 4 | keep, rationale carried | Historical observations must survive governance changes. Correlation is analytical (join on shared fields), never structural. |
| V5 | Raw / structured / derived three-layer rule; rawPayload evidence archive + promoted hot-path columns | `veda/schema-reference.md`, `veda/evidence-and-source-provenance.md` | keep | The reader must always know which layer it is looking at. Merges Neon Ronin's JSON Sludge Rule (N5). |
| V6 | Compute-on-read default + materialization test | `veda/data-boundaries.md` | keep | "Would removing the materialized data and computing on-read produce the same result?" This rule is what lets the connected LLM be the intelligence layer. |
| V7 | Provider registry pattern: admission settles identity/trust/spend, not schema | `veda/providers/registry.md` | keep | DataForSEO AI Optimization and Firecrawl admission docs carry as prior art. Extended to capture instruments (see Q2 ruling). |
| V8 | Required, non-suppressible provenance fields (`capturedBy`, `operatorIntent`, `source`, `capturedAt`) | `veda/schema-reference.md`, `veda/evidence-and-source-provenance.md` | keep | Non-negotiable evidence integrity. |
| V9 | Append-only EventLog; same-transaction atomicity; no read events | `veda/schema-reference.md` Category/Family 4 | keep | Merges Neon Ronin's audit-first invariant (N4): no required audit record means no persisted consequential change. |
| V10 | Deferred-domains rule (owned-but-deferred; no ad-hoc tables) | `veda/schema-reference.md` | keep | How we stay ambitious without schema sprawl. |
| V11 | Controlled vocabularies, governed-change-only | `veda/schema-reference.md` | keep | |
| V12 | Bucket/blob posture for large payloads (pointer + hash + promoted hot fields in DB) | `veda/data-boundaries.md` | keep | Needed for page snapshots and large provider responses. |
| V13 | Hammer testing doctrine | `ecosystem/decisions/ADR-006-hammer-doctrine-is-ecosystem-law.md`, `project-v/hammer-doctrine.md` | keep, near-wholesale | Owner-declared must. Inherited law: hammer is a hard gate; invariants first; real execution over mock theater; exact assertions; hostile-path coverage required; concurrency scenarios required; rollback probes and cross-scope violation probes non-optional; reproducibility (flaky = defect); hammer coverage for a changed area is part of the change; hammer runs on every provider/instrument integration. Observatory hammer categories: persistence, contract, append-only, scope-isolation, provenance, boundary (anti-VEDA-Brain probe), derivation, rights (new — fail-closed on unclear rights, retention enforcement). |
| V14 | Cross-system references as locators/URLs, never FKs into other systems' tables | `veda/data-boundaries.md`, `veda/schema-reference.md` | keep | Now: no FKs into Kaizen, Neon Ronin, or SearchClarity stores. |
| V15 | Thin `Project` partition record | `veda/schema-reference.md` Family 1 | adapt | Becomes flat `scope` + scope-class label (`internal`, `customer_engagement`, `market_watch`); scope-class drives consent/retention behavior. Consumers translate their own identity (Kaizen project, Neon Ronin workspace, SearchClarity engagement) into a scope. Owner ruling Q1, 2026-07-06. |
| V16 | `SourceFeed` / `SourceItem` intake families | `veda/schema-reference.md` Families 2–3 | adapt | `SourceFeed` killed (not an RSS reader). A slim manual/operator capture family survives, inheriting `capturedBy` / `operatorIntent` provenance, to hold operator-introduced evidence (manual marketplace search observations, occasional LLM probe test captures). Owner rulings Q2/Q4. |
| V17 | `SearchPerformance` first-party family (GSC-style) | `veda/schema-reference.md` Family 7 | keep, `internal`-scope only | Ground truth for "this improved" on owner-internal properties. Customer first-party is excluded — see S4. |
| V18 | AI-surface observability domain: mentions, citations, fan-out queries, brand entity, AI Overview — distinct families, never collapsed | `veda/schema-reference.md` deferred domains; `veda/providers/registry.md` | keep | The GEO half of dangerous. Veda's open design questions carry as our open questions. Converges with Kaizen K6. |
| V19 | Content graph (`Cg*` families) | `ecosystem/decisions/ADR-002-content-graph-moves-to-v-forge.md` | kill — stays dead | Page *snapshots* are observations and are in. A living editorial content model is not, and must not be recreated here under any name. |
| V20 | VEDA Brain / intelligence-synthesis tables | `ecosystem/decisions/ADR-003-veda-brain-eliminated.md` | kill — stays dead | "Not moved, not renamed — does not exist." The connected LLM replaces it at read time. |
| V21 | VEDA Strategy as a standing system | `veda-strategy/`, `ecosystem/v-ecosystem-overview.md` | kill as system; absorb as rule | No stored strategy layer. Interpretation is compute-on-read; accepted conclusions promote out to the consumer that owns them. |
| V22 | `observatory_scope` / `topic_monitor` pre-project observability | `veda/schema-reference.md` deferred domains | defer, flagged valuable | "Watch this niche before any project exists" = the `market_watch` scope-class plus a future watch-family. Directly serves gap-hunting. |
| V23 | Firecrawl as admitted provider | `veda/providers/registry.md`, `veda/providers/firecrawl.md` | defer | Demoted to fallback candidate for off-marketplace web pages only. Resolved inside the page-snapshot family drill-in. See Q2. |
| V24 | Tier 1/2/3 doc authority; four-peer-system structure; desktop doctrine layer | `README.md`, `ecosystem/` | kill | The ceremony that killed the ecosystem. This project runs flat. |
| V25 | Doc skeleton: Purpose → Core Rule → Scope → Anti-Drift Rules → LLM Use Principle → Final Rule | all `veda/*.md` | keep as template | The "LLM Use Principle" section ("if an LLM could use this doc to justify X, this doc is failing") is unusually strong and is used across this project's docs. |

## From Kaizen (kaizen-docs)

| # | Concept | Source | Disposition | Reason / adaptation |
|---|---|---|---|---|
| K1 | 030B parking-lot exclusions: no customer / gig / order / report / strategy / decision / recommendation / agent-action / business-operation records | `03-research-results/506-packet-030b-...md` | keep as boundary spine | Refined: customer-*scoped observations* are allowed under scope-class + consent/retention labels; customer *records* never. Customer first-party data is excluded per S4. |
| K2 | Shared observation ≠ request-that-caused-collection ≠ provider job/cost ≠ project relevance | `04-design-decisions/0010-dedicated-internet-marketing-intelligence-database.md` | keep | Solves customer-triggered pulls: requester lives in job metadata; the observation stays clean and reusable. |
| K3 | Six-way rights classification + fail-closed rule | Decision 0010 | keep | expressly permitted / expressly restricted / not expressly prohibited / not expressly granted / provider clarification required / legal review required. Unclear rights = no capture, or capture-and-purge with explicit window. OBR-01 gates DataForSEO long-term storage. |
| K4 | Controlled paid-capture ceremony | Decision 0010 | keep, right-sized | Non-negotiable elements: exact research question, endpoint family, row/call ceiling, cost ceiling, stop conditions, human approval. Full Kaizen packet ceremony not required here. |
| K5 | Provider disagreement preserved, never averaged | Decision 0010 | keep | Serves LLM honesty directly. |
| K6 | Distinct AI/LLM evidence families never collapsed into one "AI record" | Decision 0010 | keep | Converges with V18. |
| K7 | "Not yet — earn it" stewardship stance | `00-entrypoint/LLM_START_HERE.md` | keep as project voice | Enforced by the Steward. |
| K8 | M19 relationship | Results 505/506/508; `ROADMAP_V0.4.md` M19 gates | keep | This project feeds an eventual M19 reopening packet; it does not bypass Kaizen governance. Recorded in `00-project-overview.md`. |
| K9 | Typed-API-only access; agents never receive SQL or direct credentials | `04-design-decisions/0005-api-only-structured-data-access.md` | keep | The MCP/typed read tools are the only door. |

## From Neon Ronin (neon-ronin)

| # | Concept | Source | Disposition | Reason / adaptation |
|---|---|---|---|---|
| N1 | Naming resolution: "Observatory" = this project | conflict identified in boundary audit vs. `docs/core/04-observatory.md` | keep | Neon Ronin's sanitized-signal layer is renamed on the Neon Ronin side (their docs change, not ours). |
| N2 | Observatory-as-external-integration from Neon Ronin's perspective | `docs/core/18-external-integration-contract.md` | keep | Their contract wraps our API: workspace-scoped permission, read + queue action classes, no autonomous spending on pull requests. |
| N3 | Sanitized workspace signals as Observatory input | `docs/core/08-sanitization.md`, ADR-004 | kill as input | Flow A stays in Neon Ronin. Workspace signals carry customer-derived provenance; our evidence is external reality. Never merged. |
| N4 | Audit-first invariant | `docs/ROADMAP.md` Phase 6 proof | keep | Merged into V9. |
| N5 | JSON Sludge Rule wording | `docs/core/11-data-boundaries.md` | keep | Merged into V5/V12. |

## From SearchClarity (searchclarity)

| # | Concept | Source | Disposition | Reason / adaptation |
|---|---|---|---|---|
| S1 | Fact/estimate/observation labels: `fact_public`, `fact_seller_private`, `estimate_tool`, `observation_point_in_time`, `inference_internal` | `docs/operations/data-sources/agent-data-acquisition-strategy.md` | keep, promoted Observatory-wide | The best provenance-honesty vocabulary in the lineage; maps directly onto what a report-writing LLM must respect. (`fact_seller_private` exists in the vocabulary but such data is not stored here — see S4.) |
| S2 | Acquisition compliance law: no Etsy scraping as production dependency; no paid-dashboard scraping; API/exports/screenshots/manual paths | same source | keep as capture-side law | Constraints on how observations may be born, regardless of requester. |
| S3 | Volatility caveat language: "Observed on [date] using [context]; results may differ" | same source | keep | Becomes part of the read-tool output contract — observations self-describe volatility. |
| S4 | Customer first-party data (Etsy Stats extractions etc.) | `docs/operations/records-and-consent/recordkeeping-and-consent.md`, `docs/r05-...md` §2 | kill as Observatory content — stays SearchClarity-side | Owner ruling Q3, 2026-07-06, following the repos' consistent answer (r05: client data and generalized intelligence must be cleanly separable; 030B excludes customer data). "This improved" for customer engagements works through a read-time overlay contract: read tools accept an externally supplied first-party series and align it against Observatory time-series — join without storage. Owner-internal first-party (V17) is the only first-party data stored, under `internal` scope. |

---

## Owner Rulings (2026-07-06)

| Q | Question | Ruling |
|---|---|---|
| Q1 | Scoping model | Flat `scope` + scope-class label (`internal`, `customer_engagement`, `market_watch`); scope-class drives consent/retention. |
| Q2 | Manual/operator capture and marketplace pages | Kill `SourceFeed`; keep slim manual-capture family. Marketplace gig/listing-page snapshots = owned-but-deferred family. Owner's Chrome-extension idea = candidate capture instrument, requiring admission (provider-registry pattern, V7) with per-marketplace ToS review. Fiverr capture likely clean (already SearchClarity's designated safe target); Etsy = interim manual evidence only, Etsy API is the compliant production path (matches SearchClarity's accepted decision). Firecrawl = fallback for off-marketplace web only. Owner ~60% on own capture method; fleshed out during family drill-in. |
| Q3 | Customer first-party data | Stays in SearchClarity's layer; Observatory never stores it. Overlay contract at read time. See S4. |
| Q4 | GEO probing | DataForSEO AI Optimization is the canonical AI-surface source. Own-probe infrastructure killed as a system; occasional manual test probes land in the manual-capture family as `observation_point_in_time`. |

---

## New Capabilities — Not Documented in Any Ancestor

These close the gap between "well-modeled evidence DB" and "LLM that dominates rankings."

| # | Capability | Status |
|---|---|---|
| NC1 | Comparison-native read tools: time-series deltas, "what changed since T", presence/absence flips, rank-movement summaries as first-class tool outputs | planned — early build-plan slice |
| NC2 | Direct LLM answer-surface probing infrastructure | killed as infrastructure (Q4); ad-hoc manual test captures only, via V16 family |
| NC3 | Intervention timeline join contract: read tools accept an external intervention timeline (Kaizen returns, SearchClarity action plans) and return aligned before/after windows; interventions are never stored here | planned |
| NC4 | Freshness/staleness self-description: every read-tool response declares observation age and volatility class | planned — day-one, brutal to retrofit |
| NC5 | Coverage/blind-spot reporting: "what does the Observatory NOT know about this scope" — unobserved queries, series gaps, missing surfaces; drives collection planning | planned |
| NC6 | Query panels: named, versioned query sets observed consistently per scope — the longitudinal backbone (formalizes Veda's `KeywordTarget` seed) | planned |
| NC7 | Cost-aware collection planning: provider spend attribution per scope/family; "what would it cost to close this blind spot" | planned |
| NC8 | Evidence citation IDs: every read-tool response carries stable observation IDs so reports and Kaizen artifacts cite evidence durably | planned — day-one |
| NC9 | First-party overlay contract (from S4 ruling): read-time alignment of externally supplied customer first-party series against Observatory series, without storage | planned |

---

## Register Change Rule

Dispositions in this register are owner-confirmed. Changing a `kill` to anything else,
or admitting a deferred family/instrument, requires an explicit owner decision recorded
here (or in `decisions/` once that folder is earned).

---

## Final Rule

```text
Inheritance is a set of decisions, not a pile of ideas.
Killed concepts stay killed. Deferred concepts stay tableless until governed.
```
