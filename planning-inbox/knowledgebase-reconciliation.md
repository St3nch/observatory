# Knowledgebase Reconciliation — M0.1 Candidate Decision Pass

Status: planning
Authority: none
Purpose: reconcile project knowledge docs against the live repo, preserve serious base doctrine, and classify candidate ideas before M1 roadmap sequencing
Created: 2026-07-07
Milestone: M0.1 — Knowledgebase-to-Repo Reconciliation and Candidate Decision Pass

---

## 1. Owner correction / stewardship note

The Claude-authored base docs are serious project source material from the early project steward and prior DB-work consolidation. They should not be discarded. The dangerous feature lists are suggestions/candidates, not implementation approval. This reconciliation preserves the base, classifies the suggestions, and decides what can become active roadmap work.

Correct posture:

```text
Do not discard Claude.
Do not blindly obey Claude.
Reconcile Claude.
Classify GPT suggestions.
Then roadmap the sane next moves.
```

This document is not a build plan. It is a controlled decision pass over what can be preserved now, turned into docs now, promoted into research topics, sequenced into roadmap milestones, deferred, or forbidden unless the owner changes project law.

---

## 2. Source-of-truth hierarchy

Use this hierarchy:

```text
1. Live repo + Go8 state = source of truth for what is actually committed.
2. Project knowledge docs = serious source material / candidate material / missing repo gap evidence.
3. Chat claims = lowest trust unless verified against live repo or project knowledge docs.
```

Working rule:

```text
Knowledge docs matter.
Repo state decides what is live.
No invisible authority.
```

Uploaded/project-knowledge documents are not live repo authority until committed into the repo with clear status labels. But they are also not disposable. They are project inheritance and must be reconciled instead of ignored.

---

## 3. Knowledge docs classification

| Doc | Repo status | Recommended path | Authority label | Use now? | Notes |
|---|---|---|---|---|---|
| `strategy-layer-dangerous-design.md` | Missing from live repo | `planning-inbox/strategy-layer-dangerous-design.md` | planning | Yes, as M1/M3 input | Valuable candidate map. Its own header says planning artifact / authority none. Preserve it, but do not activate implementation. Strategy Layer is allowed only as read-time interpretation and promotion workflow planning unless future owner ruling says otherwise. |
| `deep-research-danger-agenda.md` | Missing from live repo | `planning-inbox/deep-research-danger-agenda.md` | research agenda | Yes, as M1/M3 input | Valuable research-lane list. Treat as ranked research agenda, not authorization to build. Good source for M1 sequencing and M3 research gates. |
| `STEWARD_CONTEXT_DUMP.md` | Missing from live repo | `planning-inbox/steward-context-dump.md` | advisory context | Yes, as context if preserved with label | Serious continuity dump from the early steward. It captures cross-repo audit reasoning and failure modes. It should not override `02-boundaries.md` or `01-harvest-register.md`. |
| `CLAUDE_START_HERE.md` | Present at `planning-inbox/CLAUDE_START_HERE.md` | Keep current path for now; possible future `archive/` | historical/model-specific | Yes, limited | Model-specific historical onboarding. Superseded by root `LLM_START_HERE.md`, but still useful to understand Claude-era context. Do not promote back to root authority. |
| `observatory-working-notes.md` | Present at `planning-inbox/observatory-working-notes.md` | Keep current path | working note | Yes | Important planning substrate. Not authority. Should feed M1 sequencing and later split/promotion decisions. |
| `repo-first-research-triage.md` | Present at `planning-inbox/repo-first-research-triage.md` | Keep current path | working note / research triage | Yes | Important M1/M3 input. It reduces obvious research by pointing to local repo answers first. |
| `01-harvest-register.md` | Present at root | Keep root | authority | Yes | Serious inherited-concept disposition record. Live repo authority. Uploaded version may contain additions; compare before changing. |
| `README.md` | Present at root | Keep root | authority | Yes | Live repo entrypoint now points to LLM-first path. Uploaded older version is superseded unless it contains useful historical context. |
| `NEXT_SESSION_HANDOFF.md` | Present at root | Keep root | authority | Yes | Live repo version is current handoff after M0 repair. Uploaded Claude version is historical/advisory unless reconciled. It contains useful context about Claude's 2026-07-06 pass. |
| `02-boundaries.md` | Present at root | Keep root | authority | Yes | Live repo has a conservative boundary doc. Uploaded Claude version appears richer and should be compared in a future boundary-reconciliation pass, not blindly overwritten. |

---

## 4. Base doctrine docs to preserve

These docs are serious source material, not throwaway suggestions:

| Doc | Preservation decision | Current action |
|---|---|---|
| `02-boundaries.md` | Preserve as boundary law. Compare uploaded richer version against live conservative version. | Do next as M1/M2/M3 input; do not overwrite blindly. |
| `01-harvest-register.md` | Preserve as core inheritance/disposition authority. | Keep root authority. Compare uploaded version for missing addenda before any change. |
| `STEWARD_CONTEXT_DUMP.md` | Preserve as advisory continuity context. | Recommended to add to `planning-inbox/` with advisory label, not authority. |
| `NEXT_SESSION_HANDOFF.md` | Preserve current live root handoff; preserve Claude handoff as historical context only if useful. | Do not replace live handoff. Extract useful open questions/failure modes later. |
| `observatory-working-notes.md` | Preserve as working source material. | Already in repo. Keep as planning inbox material. |
| `README.md` | Preserve live root README as current entrypoint. | Already updated for M0. Uploaded older README is superseded. |
| `CLAUDE_START_HERE.md` | Preserve as model-specific historical context. | Already in planning inbox. Do not make active root authority. |
| `repo-first-research-triage.md` | Preserve as research triage / obvious-question reducer. | Already in repo. Use as M1/M3 input. |

Decision: base docs are part of the project base. The next move is not to discard them, but to decide which parts become root authority, planning material, research agenda, or historical context.

---

## 5. Dangerous suggestions classification

The dangerous docs are valuable, but they are not implementation approval.

Important rule:

```text
The Strategy Layer idea is allowed only as read-time interpretation / promotion workflow planning.
It is not permission to create persistent strategy tables in Observatory.
```

### Strategy Layer posture

| Candidate | Source | Decision bucket | Possible future milestone | Build now? | Notes |
|---|---|---|---|---|---|
| Read-time strategy interpretation | `strategy-layer-dangerous-design.md` | Do next as M1 roadmap input | M1 / later promotion-workflow proof | No implementation now | Allowed as process framing. LLM session reasoning over evidence packs only. |
| Opportunity discovery / gap scans | `strategy-layer-dangerous-design.md` | Do later as contract/design milestone | Evidence-pack/read-tool contract milestone | No | Outputs must be ephemeral until promoted to consumer. |
| Recommendation drafting candidate object | `strategy-layer-dangerous-design.md` | Do later as contract/design milestone | Promotion workflow / claim-safety milestone | No | Candidate shape can be researched/documented; no Observatory recommendation table. |
| Promotion workflow | `strategy-layer-dangerous-design.md` | Do next as M1 roadmap input | Promotion workflow proof milestone | No | Good future loop: evidence -> candidate -> consumer review -> execution -> outcome reference. |
| Tactic ingestion / anti-guru pipeline | `strategy-layer-dangerous-design.md` | Forbidden unless owner ruling | CapturePackage / tactic-capture research only | No | Could become a capture family later, but verdicts/strategy storage inside Observatory are forbidden. |
| Recurring opportunity scans | `strategy-layer-dangerous-design.md` | Defer | Scheduler / Neon Ronin-adjacent future milestone | No | Requires scheduling posture, existing evidence, review queue destination, and no auto-capture/spend. |
| Persistent strategy records | `strategy-layer-dangerous-design.md` | Forbidden unless owner ruling | Future V21-style boundary only | No | Explicitly forbidden until friction evidence and owner approval exist. |
| Competitor natural-experiment mining | `deep-research-danger-agenda.md` F1 | Do soon as research gate | SERP/page snapshot + outcome attribution research | No | Powerful but needs page-snapshot family, change detection, and legal/rights posture. |
| Citation-hub reverse engineering | `deep-research-danger-agenda.md` F2 | Do soon as research gate | GEO / AI citation methodology | No | Good research lane; future report advantage. No build now. |
| Volatility seismograph / update detection | `deep-research-danger-agenda.md` F3 | Forbidden unless owner ruling for cross-scope aggregate | Cross-scope aggregate governance milestone | No | Cross-scope aggregate read is denied by default. Needs explicit governed exception and hammers. |
| Demand early-warning | `deep-research-danger-agenda.md` F4 | Do later as contract/design milestone | Query-panel / freshness / longitudinal milestone | No | Needs longitudinal depth. Candidate for future read-time analysis. |
| SERP real-estate accounting | `deep-research-danger-agenda.md` F5 | Do next as M1 roadmap input | Evidence model / report support milestone | No | Useful future visibility series, but depends on observation families. |
| Decay and cannibalization detector | `deep-research-danger-agenda.md` F6 | Do soon as research gate | Freshness/staleness/visibility research | No | Useful for SearchClarity/internal workflows; read-time only. |
| Evidence-priced quoting | `deep-research-danger-agenda.md` F7 | Do later as contract/design milestone | Cost/coverage tooling + SearchClarity consumer milestone | No | Consumer-side sales artifact; Observatory supplies coverage/cost evidence only. |
| Cross-engagement playbook mining | `deep-research-danger-agenda.md` F8 | Forbidden unless owner ruling for persistent form | Future V21 boundary only | No | Honest friction path to future strategy records, also highest risk for boundary violation. |
| Query-panel marketplace templates | `deep-research-danger-agenda.md` F9 | Do next as M1 roadmap input | Query panel model milestone | No | Governance/planning object; useful but no schema yet. |

---

## 6. Prior GPT suggestions classification

| Idea | Source | Decision bucket | Possible future milestone | Build now? | Notes |
|---|---|---|---|---|---|
| Evidence Cost Ledger | Prior GPT | Do next as M1 roadmap input | Provider/cost gate or capture contract milestone | No | Useful to control paid evidence economics. No provider calls yet. |
| Golden Sample Set | Prior GPT | Do next as M1 roadmap input | Provider validation / hammer fixture milestone | No | Good proof fixture set for future DataForSEO/payload work. |
| Provider Payload Diff Log | Prior GPT | Do next as M1 roadmap input | Provider drift detection milestone | No | Strongly aligned with provider-drift doctrine. No automation now. |
| Claim Language Matrix | Prior GPT | Do next as M1 roadmap input | Claim-safety milestone | No | Important for SearchClarity/customer-facing outputs; contract later. |
| Negative Evidence / Absence Rules | Prior GPT | Do next as M1 roadmap input | Evidence interpretation / answerability milestone | No | Critical to avoid false absence claims. Research/contract later. |
| Experiment Graveyard | Prior GPT | Do later as contract/design milestone | Outcome/promotion hygiene milestone | No | Useful after promotion workflow exists. Not first. |
| Red-Team Review Questions | Prior GPT | Do later as contract/design milestone | Hammer/review checklist milestone | No | Good for hammers and owner review. Later. |
| Surface Coverage Map | Prior GPT | Do next as M1 roadmap input | Coverage/blind-spot milestone | No | Strong fit for read-tool planning and collection planning. |
| Provider Cross-Check / Disagreement Model | Prior GPT / owner correction | Do now as preserved planning/contract candidate; do next as M1 roadmap input; do soon as research gate | Provider evidence/disagreement research gate before schema/provider implementation | No | Important early design rule. Provider disagreement is first-class evidence. Preserve model now; do not implement now. |
| Owned Property Telemetry Boundary | Prior GPT | Do next as M1 roadmap input | Boundary hardening milestone | No | Important boundary candidate. No telemetry storage until explicit internal-scope handling. |
| Hammer Matrix | Prior GPT | Do next as M1 roadmap input | Hammer matrix milestone | No | Hard gate before implementation. Roadmap it early. |
| LLM-first MCP Read Tool Contract | Prior GPT | Do next as M1 roadmap input | API/MCP contract milestone | No | Must precede MCP implementation. No tools now. |

### Provider Cross-Check & Disagreement Model preservation note

Status:

```text
important early design rule / future contract candidate
```

Build now: no.

Document now: yes.

Roadmap: yes.

Core rule:

```text
The Observatory should eventually compare DataForSEO, Ahrefs, Semrush, Google Search Console, Bing Webmaster Tools, Etsy tools, and other admitted instruments without treating any single provider as truth.
Provider disagreement is first-class evidence.
```

This model should likely become an early research gate or design milestone before schema/provider implementation because it affects evidence design, capture timing, read-tool output, claim safety, and provider-admission rules.

#### Provider Disagreement Ledger

Future contract/schema candidate. Do not build now, but preserve candidate fields:

```text
target
query_or_url
surface
provider_a
provider_b
metric_name
provider_a_value
provider_b_value
difference
capture_time_a
capture_time_b
capture_time_distance
likely_reason
confidence
usefulness_note
```

#### Provider Personality Profiles

Planning doc seed. Each provider has strengths, weaknesses, blind spots, proprietary estimation behavior, and best-fit use cases.

Possible future path:

```text
planning-inbox/provider-comparison-notes.md
```

Possible later promoted path:

```text
docs/provider-personality-profiles.md
```

Example posture:

```text
DataForSEO = raw/API-scale capture, needs our interpretation
Ahrefs = backlinks/competitor domains, proprietary estimates
Semrush = broad SEO suite, proprietary estimates/noise
GSC = owned first-party impressions/clicks only
Bing Webmaster = owned Bing-side data
Etsy tools = marketplace-specific ideas, often opaque estimates
```

#### Same Target, Same Time Rule

Planning/doctrine candidate:

```text
Provider comparisons should record capture-time distance and warn when comparisons are stale or non-synchronous.
```

Do not compare Ahrefs Monday, Semrush Friday, and DataForSEO after a Google update as if they are one clean moment.

This rule should feed future freshness/staleness/volatility work and read-tool warnings.

#### No Proprietary Score Worship

Boundary / claim-safety rule candidate:

```text
Proprietary provider scores are observations of that provider's model output, not facts about the web.
```

Examples:

```text
Ahrefs DR
Semrush KD
traffic estimates
difficulty scores
intent labels
authority scores
backlink counts
```

These are useful observations, not truth.

#### Tool ROI Tracker

Future ops/cost candidate. Do not build now, but preserve candidate fields:

```text
tool
monthly_cost
features_used
reports_supported
opportunities_found
customer_work_supported
internal_projects_supported
data_not_available_elsewhere
cancel_keep_upgrade_reason
```

This belongs near future cost/coverage/provider-admission planning. It is not a subscription tracker to build during M0.1.

---

## 7. Do now / do next / defer / forbidden

### Do now as M0.1 documentation/reconciliation

- `planning-inbox/knowledgebase-reconciliation.md`
- base docs preservation note
- knowledge doc classification table
- dangerous suggestions classification table
- prior GPT suggestions classification table
- Provider Cross-Check & Disagreement Model preservation note
- repo placement recommendations
- M1 input summary
- open owner questions

### Do next as M1 roadmap input

- Evidence Cost Ledger
- Golden Sample Set
- Provider Payload Diff Log
- Claim Language Matrix
- Negative Evidence / Absence Rules
- Surface Coverage Map
- Provider Cross-Check / Disagreement Model as important early design rule / future contract candidate
- Provider Disagreement Ledger candidate fields
- Provider Personality Profiles planning-doc seed
- Same Target, Same Time Rule
- No Proprietary Score Worship rule candidate
- Tool ROI Tracker ops/cost candidate
- Owned Property Telemetry Boundary
- Hammer Matrix
- LLM-first MCP Read Tool Contract
- query panel marketplace templates
- SERP real-estate accounting
- promotion workflow proof
- Strategy Layer as read-time interpretation/process only

### Do soon as research gates

- DataForSEO rights / retention / cost
- marketplace evidence ceiling
- GEO / AI citation methodology
- SERP weakness signal model
- Provider Cross-Check & Disagreement Model before schema/provider work
- provider comparison model
- claim-safety language
- freshness / staleness / volatility
- competitor natural-experiment mining
- citation-hub reverse engineering
- decay and cannibalization detector

### Do later as contract/design milestone

- CapturePackage v0.1 contract
- evidence ID / citation contract
- query panel model
- evidence cost / coverage tooling
- promotion workflow contract
- report-support claim contract
- provider drift / payload diff contract
- red-team review checklist
- experiment graveyard / outcome hygiene

### Defer

- schema families
- provider pulls
- MCP implementation
- API implementation
- dashboard/operator console
- automated recurring capture
- embeddings/vector store
- customer-facing report automation
- cross-scope aggregate seismograph unless owner ruling opens a governed exception

### Forbidden unless owner ruling

- persistent Strategy/IMI storage
- recommendation tables
- score-as-truth tables
- opportunity/finding tables in Observatory
- customer first-party data storage in Observatory
- direct SQL/credentials for agents
- VEDA Brain resurrection under another name
- cross-engagement playbook mining in persistent form
- cross-scope aggregates involving customer engagement leakage
- tactic verdict tables inside Observatory
- any candidate cache or scratch strategy store pretending not to be storage

### Killed / do not revive

- VEDA Brain
- content graph ownership inside Observatory
- Observatory as customer database
- Observatory as dashboard-first product
- raw SQL access for LLMs/agents
- provider data collapsed into fake truth

---

## 8. Recommended repo placement

| Item | Recommended placement | Timing | Notes |
|---|---|---|---|
| `knowledgebase-reconciliation.md` | `planning-inbox/knowledgebase-reconciliation.md` | Now | This file. Planning label, no authority. |
| `strategy-layer-dangerous-design.md` | `planning-inbox/strategy-layer-dangerous-design.md` | Add after owner accepts M0.1 classification | Preserve as planning artifact; no implementation approval. |
| `deep-research-danger-agenda.md` | `planning-inbox/deep-research-danger-agenda.md` | Add after owner accepts M0.1 classification | Preserve as research agenda. |
| `STEWARD_CONTEXT_DUMP.md` | `planning-inbox/steward-context-dump.md` | Add after owner accepts M0.1 classification | Preserve as advisory context. Lowercase path recommended for consistency. |
| Uploaded Claude `02-boundaries.md` | compare against root `02-boundaries.md` | Later boundary-reconciliation pass | Do not overwrite root doc blindly. |
| Uploaded Claude `NEXT_SESSION_HANDOFF.md` | maybe `planning-inbox/claude-next-session-handoff-2026-07-06.md` or extract into reconciliation notes | Later | Historical context. Current root handoff wins. |
| `CLAUDE_START_HERE.md` | Keep `planning-inbox/CLAUDE_START_HERE.md` for now | Now | Historical/model-specific. Possible archive later. |

Placement rule: planning/context docs can enter `planning-inbox/` with labels. Authority docs require review and explicit promotion. Dangerous capability maps must not enter root authority.

---

## 9. Recommended M1 inputs

M1 should use this artifact to sequence milestones around:

1. Boundary reconciliation and doc promotion rules.
2. Folder structure and folder README indexes.
3. Research gates before implementation.
4. DataForSEO rights / retention / cost research.
5. Marketplace evidence ceiling research.
6. GEO / AI citation methodology research.
7. Provider Cross-Check & Disagreement Model as an early research gate before schema/provider work.
8. Provider Personality Profiles and No Proprietary Score Worship claim-safety rule.
9. Freshness / staleness / volatility model.
10. Claim language matrix.
11. Evidence ID / citation model.
12. Query panel model.
13. Surface coverage / blind-spot model.
14. CapturePackage v0.1.
15. Provider payload diff / drift log.
16. Hammer matrix.
17. LLM-first MCP read-tool contract.
18. Promotion workflow proof.

M1 should not design schema, call providers, implement MCP, build dashboard, or activate strategy storage.

---

## 10. Open owner questions

1. Should `strategy-layer-dangerous-design.md`, `deep-research-danger-agenda.md`, and `STEWARD_CONTEXT_DUMP.md` be added to `planning-inbox/` now that they are classified?
2. Should uploaded Claude `02-boundaries.md` be compared against the live conservative `02-boundaries.md` in a dedicated boundary-reconciliation pass before M1?
3. Should uploaded Claude `NEXT_SESSION_HANDOFF.md` be preserved as a historical planning-inbox doc, or should only useful points be extracted?
4. Should `CLAUDE_START_HERE.md` stay in `planning-inbox/` or move to a future `archive/` once archive rules exist?
5. Which M1 input is highest priority: provider rights/cost, claim safety, query panels, CapturePackage, or hammer matrix?
6. Should `Owned Property Telemetry Boundary` become an early boundary-hardening doc before provider work?
7. Should Strategy Layer vocabulary remain as a named concept, or should it be renamed later to avoid future agents mistaking it for a storage system?

---

## Final operating rule

```text
Preserve the base.
Inventory the weapons.
Choose the sane next moves.
Roadmap before build.
```

The base docs are serious source material. The dangerous feature lists are suggestion/candidate material. All material must be reconciled into the repo with labels before it becomes active project authority.
