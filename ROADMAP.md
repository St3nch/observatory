# Roadmap - The Observatory

Status: authority
Authority: roadmap operating document
Purpose: preserve milestone memory, required reading, gates, and execution sequence from planning through Observatory v1
Last updated: 2026-07-07

---

## Roadmap Role

This file is the operating roadmap for The Observatory.

It is not provider authorization.
It is not direct implementation approval.
It is not permission to create schema, migrations, MCP tools, dashboards, provider integrations, or strategy storage.

The roadmap exists to preserve:

- current active milestone
- required reading before work
- allowed work
- forbidden work
- milestone gates
- research gates
- future build order
- deferred ideas
- killed ideas
- sequencing memory

Roadmap edit rules live in `ROADMAP_RULES.md`.

---

## Core Project Law

The Observatory stores observations, not conclusions.

The connected LLM interprets at read time.

Accepted conclusions promote out to the owning consumer.

The Observatory is the telescope. The connected LLM is the astronomer. The database must never become the astronomer.

Hard boundaries:

- no customer records
- no customer first-party analytics storage in Observatory
- no strategy tables
- no recommendation tables
- no score-as-truth tables
- no provider-as-truth model
- no direct SQL or credentials for LLMs/agents
- no VEDA Brain resurrection
- rights and retention fail closed
- provider disagreement is first-class evidence
- hammer tests are a hard gate before implementation acceptance

---

## Status Labels

| Status | Meaning |
|---|---|
| closed | Exit criteria met and committed |
| active | Current milestone |
| planned | Sequenced but not active |
| blocked | Cannot proceed until blocker is resolved |
| ready for review | Work complete enough for owner/steward review |
| deferred | Owned future concern, not active |
| forbidden unless owner ruling | Not allowed unless owner changes project law |
| killed | Explicitly rejected; must not re-enter under another name |

---

## Required Milestone Template

Each milestone must include:

```text
Milestone ID:
Name:
Status:
Purpose:
Required reading:
Allowed work:
Forbidden work:
Exit criteria:
Blockers:
Next milestone:
```

Optional fields:

```text
Owner rulings needed:
Files likely touched:
Hammer implications:
Notes for LLMs:
```

If required reading includes a folder, that folder must have a `README.md` index.

---

## Milestone Summary

| Milestone | Name | Status | Purpose |
|---|---|---|---|
| M0 | LLM-First Repo Navigation and Roadmap Preservation | closed | Create repo navigation, boundaries, and roadmap-control files |
| M0.1 | Knowledgebase-to-Repo Reconciliation and Candidate Decision Pass | closed | Classify Claude/GPT docs and candidate ideas without activating them blindly |
| M1 | Roadmap Content Draft and Milestone Sequencing | closed | Turn planning inputs into the real staged project roadmap |
| M2 | Folder Structure and Folder README Indexes | closed | Create only earned folders and folder indexes |
| M3 | Knowledge Doc Preservation and Planning-Inbox Expansion | closed | Add classified Claude docs to planning-inbox with labels |
| M4 | Boundary Reconciliation and Doctrine Hardening | closed | Reconcile richer boundary material and harden project law |
| M5 | Research Gate Plan | closed | Define research questions, outputs, and gates before design/build |
| M6 | Research Gate Execution | closed | Complete required research before contracts/schema/provider work |
| M7 | Core Contract Planning | active | Draft non-schema contracts for evidence, scope, provider, query panels, capture packages |
| M8 | Hammer Matrix and Acceptance Gates | planned | Define hostile-path tests and hard gates before implementation |
| M9 | First Evidence Slice Definition | planned | Choose the smallest useful evidence slice to build first |
| M10 | Schema Planning Only | planned | Design schema after contracts and research; no migrations yet |
| M11 | Implementation Foundation | planned | Create project implementation skeleton only after gates open |
| M12 | First Evidence Slice Build | planned | Build and test the first observation path |
| M13 | Provider Admission and Controlled Pull Plan | planned | Admit first provider through rights/cost/recipe gates |
| M14 | Typed Read API / MCP Contract and Prototype | planned | Expose evidence through bounded read tools, not raw SQL |
| M15 | SearchClarity Proof Workflow | planned | Prove customer-facing evidence support without storing customer records |
| M16 | Provider Cross-Check Proof | planned | Prove provider disagreement as first-class evidence |
| M17 | Owned Telemetry Overlay Proof | planned | Prove read-time overlay without storing customer first-party data |
| M18 | Recurring Watch Panel Planning | planned | Plan recurring capture only after provider/cost/hammers exist |
| M19 | Hardening, Backup, Recovery, and Operations | planned | Make the system durable and recoverable |
| M20 | Observatory v1 Acceptance | planned | Accept or reject v1 against doctrine, evidence, and hammers |

---

## Active Milestone

### Milestone ID

M7

### Name

Core Contract Planning

### Status

active

### Purpose

Draft non-schema contracts that define Observatory evidence behavior before database design, provider admission, API/MCP implementation, dashboard work, or customer-facing workflow work.

M7 uses the completed M6 research outputs as contract-planning input. It does not authorize schema design, migrations, provider pulls, implementation, customer data handling, or strategy/recommendation storage.

### Required Reading

- `README.md`
- `LLM_START_HERE.md`
- `ACTIVE_CONTEXT.md`
- `ROADMAP.md`
- `ROADMAP_RULES.md`
- `REPO_MAP.md`
- `00-project-overview.md`
- `01-harvest-register.md`
- `02-boundaries.md`
- `NEXT_SESSION_HANDOFF.md`
- `research/README.md`
- all M6 research outputs in `research/`
- `research/deep-research-backlog.md`
- `audits/README.md` and the 2026-07-07 audit reports
- `planning-inbox/m7-audit-response-2026-07-07.md`
- `planning-inbox/owner-ruling-tracker.md`
- `contracts/README.md` and `contracts/contract-template.md`

### Allowed Work

- audit completed M6 research outputs before contract drafting
- create a contract document template if needed
- create earned `contracts/` folder/index if M7 work proceeds
- draft non-schema contracts from M6 research outputs
- preserve owner-ruling candidates and deeper research blockers
- keep all contracts aligned with `02-boundaries.md`

### Forbidden Work

- physical schema design
- migrations
- provider purchases
- paid provider pulls
- provider admission
- API/MCP implementation
- dashboard work
- customer data handling
- strategy/recommendation storage
- capture runner implementation
- automated recurring capture

### Blockers

- M6 research outputs must exist and be indexed. — met
- Contract template must exist before drafting contract docs. — met 2026-07-07 (`contracts/contract-template.md`)
- Claude audit or steward audit should review M6 outputs before broad M7 contract drafting. — met 2026-07-07 (two audits preserved in `audits/`; findings routed in `planning-inbox/m7-audit-response-2026-07-07.md`)
- Any doctrine change requires explicit owner ruling before promotion.

### M7 Progress Log

2026-07-07 — M7 first move complete: M6 research set audited (M6/M7-readiness audit) and full repo audited; both reports preserved in `audits/`. Audit-fix pass executed with owner approval:

- `audits/` earned and governed (`decisions/2026-07-07-audits-folder.md`, `audits/README.md`, REPO_MAP row)
- `contracts/` created with README and contract template (drafting blocker cleared)
- `planning-inbox/m7-audit-response-2026-07-07.md` routes all findings (ISS-01..22, SEQ-01)
- `planning-inbox/owner-ruling-tracker.md` consolidates all open owner-ruling candidates (groups A–G)
- RG13 gained H19–H22 (append-only, concurrency, audit-first, migration rollback) via dated addendum
- `research/deep-research-backlog.md` gained DR16 (consumer authn/authz) and DR17 (provider secrets)
- M5 plan gained the planned-topics-to-executed-gates mapping addendum
- stale references fixed across `research/README.md`, REPO_MAP, decisions, archive, planning-inbox; `CLAUDE_START_HERE.md` archived; 00/01 headers promoted to authority; closure convention now requires tracker/review-note refreshes

Next M7 work: resolve owner-ruling group A (see tracker), then draft contracts in the sequence recorded in `contracts/README.md` (spine first: scope/rights/retention, evidence ID/citation).

### Exit Criteria

M7 may close when:

- core contracts are drafted and indexed;
- contracts clearly separate observations from conclusions;
- forbidden storage patterns remain excluded;
- owner-ruling candidates and deeper-research blockers are explicit;
- M8 can define hammer tests without guessing;
- `ACTIVE_CONTEXT.md` and `NEXT_SESSION_HANDOFF.md` point to the correct next milestone;
- changes are committed.

### Next Milestone

M8 - Hammer Matrix and Acceptance Gates

---

## Closed Milestones

### M6 - Research Gate Execution

Status: closed

Purpose:
Execute the planned research gates and produce source-grounded docs before contract/schema work.

Completed outputs:

- `research/rg1-dataforseo-rights-retention-cost.md`
- `research/rg2-scope-rights-retention-model.md`
- `research/rg3-evidence-id-citation-model.md`
- `research/rg4-query-panel-model.md`
- `research/rg5-freshness-staleness-volatility.md`
- `research/rg6-geo-ai-citation-methodology.md`
- `research/rg7-marketplace-evidence-ceiling.md`
- `research/rg8-claim-safety-report-language.md`
- `research/rg9-provider-cross-check-disagreement-model.md`
- `research/rg10-capturepackage-v0-1-inputs.md`
- `research/rg11-raw-archive-provider-drift.md`
- `research/rg12-consumer-contract-inputs.md`
- `research/rg13-hammer-matrix-inputs.md`
- `research/deep-research-backlog.md`
- `research/README.md` indexed the completed M6 outputs

Closure note:
M6 executed all 13 planned research gates and added a deep-research backlog so unresolved deeper questions are preserved without blocking M7 contract planning. M6 did not authorize provider purchases, paid pulls, schema design, migrations, API/MCP implementation, dashboard work, customer-data handling, provider admission, capture runner implementation, or strategy/recommendation storage. M7 is now active for audit and non-schema core contract planning.

### M5 - Research Gate Plan

Status: closed

Purpose:
Define the research gates that must be completed before contracts, schema, provider admission, or API/MCP implementation.

Completed outputs:

- `research/m5-research-gate-plan.md`
- `research/README.md` indexed the gate plan

Closure note:
M5 defined 13 M6 research gates, output doc names, source priorities, completion rules, owner-ruling candidates, and execution order. It did not execute research, spend provider budget, design schema, or open implementation. M6 is now active for source-grounded research execution.

### M4 - Boundary Reconciliation and Doctrine Hardening

Status: closed

Purpose:
Compare richer uploaded/project-knowledge boundary material against live root `02-boundaries.md` and harden project law before design work.

Completed outputs:

- `planning-inbox/m4-boundary-reconciliation.md`
- `02-boundaries.md` hardened with safe boundary clarifications

Closure note:
M4 classified boundary deltas, strengthened root boundary law, and did not admit new capabilities. Strategy / IMI remains read-time/process only, provider scores remain provider-attributed observations, workspace-derived signals remain out, hidden candidate stores remain forbidden, and cross-scope aggregate analysis remains forbidden by default unless future owner ruling creates a governed exception. M5 is now active for research gate planning only.

### M3 - Knowledge Doc Preservation and Planning-Inbox Expansion

Status: closed

Purpose:
Add classified Claude/project knowledge docs to the repo with labels, without promoting them into authority.

Completed outputs:

- `planning-inbox/strategy-layer-dangerous-design.md`
- `planning-inbox/deep-research-danger-agenda.md`
- `planning-inbox/steward-context-dump.md`
- `planning-inbox/README.md` updated to index the M3 docs with authority-none labels

Closure note:
M3 preserved the approved source docs as planning-inbox material only. The added docs remain planning artifact / research agenda / advisory context, not authority and not implementation approval. M4 is now active for boundary reconciliation and doctrine hardening.

### M0 - LLM-First Repo Navigation and Roadmap Preservation

Status: closed

Purpose:
Make the repo self-explaining for humans and LLMs before deeper planning or implementation begins.

Completed outputs:

- `README.md`
- `LLM_START_HERE.md`
- `ACTIVE_CONTEXT.md`
- `ROADMAP.md`
- `ROADMAP_RULES.md`
- `REPO_MAP.md`
- `FOLDER_README_TEMPLATE.md`
- `NEXT_SESSION_HANDOFF.md`
- `planning-inbox/README.md`
- `02-boundaries.md`

### M0.1 - Knowledgebase-to-Repo Reconciliation and Candidate Decision Pass

Status: closed

Purpose:
Reconcile important project knowledge docs against the live repo and classify candidate ideas before roadmap activation.

Completed output:

- `planning-inbox/knowledgebase-reconciliation.md`

Key preserved decisions:

- base Claude docs are serious project source material;
- dangerous docs are candidate/suggestion material, not implementation approval;
- Provider Cross-Check & Disagreement Model is an important early design rule / future contract candidate;
- persistent Strategy/IMI storage remains forbidden unless owner ruling changes project law.

### M1 - Roadmap Content Draft and Milestone Sequencing

Status: closed

Purpose:
Turn M0/M0.1 planning into a real staged roadmap from current docs through Observatory v1.

Completed outputs:

- detailed M0 through M20 roadmap sequence
- Provider Cross-Check preserved as early design rule / research gate / future contract candidate
- M2/M3/M4 next steps established
- research-before-contracts-before-schema-before-implementation sequence established
- audit-response backlog created and indexed

Closure note:
M1 closed through an audit-response closure pass after Claude's 2026-07-07 repo audit found that M1 was substantively complete but still marked active.

### M2 - Folder Structure and Folder README Indexes

Status: closed

Purpose:
Create only the folder structure that the roadmap earned, with README indexes for every required-reading folder created in M2.

Completed outputs:

- `.gitattributes`
- `decisions/README.md`
- `decisions/decision-record-template.md`
- `decisions/2026-07-07-m2-folder-subset.md`
- `archive/README.md`
- `research/README.md`
- `REPO_MAP.md` updated to match actual folders
- `README.md` read-order and sibling-repo note cleaned up
- `planning-inbox/README.md` updated with audit-response and Go8 note

Closure note:
M2 created the owner-approved folder subset: `decisions/`, `archive/`, and `research/`. `contracts/` remains deferred until M7 and `hammers/` remains deferred until M8.

---

## Planned Milestones

### M4 - Boundary Reconciliation and Doctrine Hardening

Status: closed; closure details live in the Closed Milestones section above

Purpose:
Compare richer uploaded/project-knowledge boundary material against live root `02-boundaries.md` and harden project law before design work.

Required reading / planning context:

- `02-boundaries.md`
- `01-harvest-register.md`
- `planning-inbox/knowledgebase-reconciliation.md`
- `planning-inbox/audit-response-2026-07-07.md`
- added M3 steward/context docs
- uploaded/project-knowledge boundary material available to the steward

Allowed work:

- compare uploaded/project-knowledge `02-boundaries.md` against live root version
- add missing boundary rules if owner-approved
- clarify customer first-party data boundary
- clarify internal owned telemetry boundary
- clarify Strategy Layer boundary
- clarify provider disagreement / proprietary score rule
- clarify forbidden/killed concepts

Forbidden work:

- weakening boundaries
- admitting customer first-party storage without owner ruling
- allowing strategy/recommendation tables
- allowing direct SQL/credentials

Exit criteria:

- root `02-boundaries.md` is strong enough to gate research/contracts;
- known boundary deltas are resolved or explicitly deferred.

Next milestone: M5

---

### M5 - Research Gate Plan

Status: closed; closure details live in the Closed Milestones section above

Purpose:
Define the research gates that must be completed before contracts, schema, provider admission, or API/MCP implementation.

Required reading / planning context:

- `planning-inbox/repo-first-research-triage.md`
- `planning-inbox/knowledgebase-reconciliation.md`
- `planning-inbox/audit-response-2026-07-07.md`
- M4 boundary outputs

Research gates to plan:

1. DataForSEO rights / retention / cost
2. marketplace evidence ceiling
3. GEO / AI citation methodology
4. Provider Cross-Check & Disagreement Model
5. provider personality profiles / proprietary score treatment
6. freshness / staleness / volatility
7. claim-safety language
8. negative evidence / absence rules
9. surface coverage / blind spots
10. owned property telemetry boundary
11. CapturePackage v0.1 inputs
12. evidence ID / citation model needs

Forbidden work:

- paid provider pulls
- schema design
- implementation

Exit criteria:

- each research gate has question, output doc, required sources, and completion rule;
- M6 execution order is clear.

Next milestone: M6

---

### M6 - Research Gate Execution

Status: closed; closure details live in the Closed Milestones section above

Purpose:
Execute the planned research gates and produce source-grounded docs before contract/schema work.

Required reading / planning context:

- M5 research gate plan
- `planning-inbox/audit-response-2026-07-07.md`
- M4 boundary outputs
- source docs named by each research gate

Blockers:

- M5 research gate plan must exist.
- M4 boundary reconciliation must be complete or explicitly scoped for research.

Allowed work:

- research current provider docs and terms
- research methodology for GEO/AI citation measurement
- research provider comparison and score interpretation
- research claim-safety/report language
- research evidence/citation models
- create research docs under `research/`

Forbidden work:

- provider purchases
- paid pulls
- schema or migration work
- MCP/API implementation

Exit criteria:

- research docs exist and are indexed;
- blockers are known;
- contract planning can begin without guessing.

Next milestone: M7

---

### M7 - Core Contract Planning

Status: active; full active-milestone details live in the Active Milestone section above

Purpose:
Draft non-schema contracts that define evidence behavior before database design.

Required reading / planning context:

- M6 research outputs
- M4 boundary outputs
- `planning-inbox/audit-response-2026-07-07.md`
- future contract document template

Blockers:

- M6 research outputs must exist.
- Contract template must exist before drafting contract docs.

Contracts to draft (annotated 2026-07-07 per audit routing SEQ-01; sequencing lives in `contracts/README.md`):

- scope / scope_class / rights / retention contract
- evidence ID and citation contract
- provider registry / provider testimony contract
- Provider Cross-Check & Disagreement Model contract (absorbs the Provider Disagreement Ledger as an open-question section — ledger persistence requires the V6 materialization test and owner ruling OR-A1; no standalone ledger contract)
- query panel contract
- CapturePackage v0.1 contract
- raw archive / payload pointer / provider drift contract (merged: raw pointer + payload diff/drift are one contract)
- freshness / staleness / volatility contract
- claim language matrix contract (absorbs negative evidence / absence rules; includes predictive_claim class)
- owned telemetry overlay contract (placeholder only until DR11; covers customer first-party overlays and NC3 intervention-timeline ephemeral inputs)
- promotion / conclusion-handoff contract
- SearchClarity consumer-contract placeholder (placeholder only until DR9)
- typed API/MCP read-tool contract (skeleton only — M14 owns the real contract; includes NC5 coverage/blind-spot output fields)

Forbidden work:

- physical schema
- migrations
- provider pulls
- implementation

Exit criteria:

- contracts are coherent enough for schema planning;
- forbidden storage patterns remain excluded.

Next milestone: M8

---

### M8 - Hammer Matrix and Acceptance Gates

Status: planned

Purpose:
Define hard tests and hostile-path gates before implementation starts.

Required reading / planning context:

- M7 contract outputs
- M4 boundary outputs
- `planning-inbox/audit-response-2026-07-07.md`

Blockers:

- Core contracts must be coherent enough to test.

Hammer categories:

- observation vs conclusion separation
- no customer records
- no customer first-party storage
- rights fail-closed
- retention fail-closed
- provider disagreement preservation
- proprietary score treatment
- raw payload preservation / pointer integrity
- no direct SQL/credentials for LLMs
- no strategy/recommendation storage
- no fake scratch/candidate strategy cache
- overlay no-persistence
- append-only observation behavior (RG13 H19)
- concurrency safety (RG13 H20)
- audit-first enforcement (RG13 H21)
- schema migration rollback/recovery expectations (RG13 H22)
- capture package validation
- read-tool scope isolation

Exit criteria:

- hammers are defined before build;
- first slice has acceptance tests.

Next milestone: M9

---

### M9 - First Evidence Slice Definition

Status: planned

Purpose:
Choose the smallest useful first slice that proves Observatory behavior without overbuilding.

Required reading / planning context:

- M7 contract outputs
- M8 hammer matrix
- M6 research outputs
- `planning-inbox/audit-response-2026-07-07.md`

Blockers:

- Contracts and hammer expectations must exist before first-slice selection.

Likely first-slice candidates:

- DataForSEO SERP/keyword observation sample
- manual/public page snapshot package
- provider-response raw archive plus metadata
- query panel plus evidence ID output
- provider disagreement mini-proof using controlled fixture data before real provider spend

Decision rule:

The first slice must prove observation storage, provenance, rights labels, raw preservation, evidence ID, and read-time interpretation support.

Forbidden work:

- broad schema families
- dashboard
- recurring capture
- multiple providers at once

Exit criteria:

- first slice chosen;
- contract coverage known;
- hammer set named explicitly;
- evidence ID behavior named;
- scope/rights/retention behavior named;
- schema planning can target the slice.

Next milestone: M10

---

### M10 - Schema Planning Only

Status: planned

Purpose:
Design schema for the approved first slice only, after research/contracts/hammers exist.

Required reading / planning context:

- M9 first-slice decision
- M7 contract outputs
- M8 hammer matrix
- M6 research outputs
- `planning-inbox/audit-response-2026-07-07.md`

Blockers:

- Evidence ID model must be settled.
- Scope/rights/retention model must be settled.
- First-slice hammer set must be named.

Allowed work:

- logical schema design
- migration plan draft
- table responsibility notes
- anti-pattern checks
- evidence/query examples

Forbidden work:

- running migrations
- connecting providers
- implementing API/MCP
- adding strategy/recommendation tables
- broad schema beyond first slice

Exit criteria:

- schema plan passes boundary review and hammer expectations.

Next milestone: M11

---

### M11 - Implementation Foundation

Status: planned

Purpose:
Create the minimal implementation foundation only after schema plan and gates are approved.

Required reading / planning context:

- M10 schema plan
- M8 hammer matrix
- M9 first-slice decision
- `planning-inbox/audit-response-2026-07-07.md`

Blockers:

- Schema plan must pass boundary review.
- M11 deliverables must be re-specified concretely before implementation begins.

Allowed work:

- repo implementation skeleton if needed
- test harness
- migration folder setup
- local config pattern without secrets
- initial hammer test scaffold

Forbidden work:

- provider calls
- dashboard
- strategy storage
- MCP tool exposure before contract

Exit criteria:

- foundation exists;
- no boundary violations;
- tests run locally.

Next milestone: M12

---

### M12 - First Evidence Slice Build

Status: planned

Purpose:
Build the approved first evidence slice.

Required reading / planning context:

- M10 schema plan
- M11 implementation foundation outputs
- M8 hammer matrix
- M9 first-slice decision
- `planning-inbox/audit-response-2026-07-07.md`

Blockers:

- M12 deliverables must be re-specified concretely before build begins.
- Raw archive backup/hash-verification expectation must be defined before real raw evidence is accepted.

Allowed work:

- migrations for first slice only
- fixture/sample ingestion path
- raw archive pointer behavior
- evidence ID behavior
- bounded read path
- hammer tests

Forbidden work:

- broad provider integrations
- recurring capture
- dashboards
- strategy tables

Exit criteria:

- first slice works under hammers;
- raw archive pointers are backed by hash verification expectations;
- observations are separate from interpretation.

Next milestone: M13

---

### M13 - Provider Admission and Controlled Pull Plan

Status: planned

Purpose:
Admit the first real provider through rights, retention, cost, recipe, and stop-condition gates.

Required reading / planning context:

- M6 provider/right/cost research outputs
- M7 provider testimony/disagreement contracts
- M12 first-slice proof outputs
- `planning-inbox/audit-response-2026-07-07.md`

Blockers:

- OBR-01: DataForSEO rights / retention / cost must be researched and accepted before any paid pull.
- Provider admission doc, recipe, cost ceiling, and stop conditions must exist.

Likely first provider:

- DataForSEO, if research gates clear it

Allowed work:

- provider admission doc
- capture recipe
- cost ceiling
- stop conditions
- raw payload preservation plan
- tiny controlled pull proposal

Forbidden work:

- unapproved paid pulls
- Ahrefs/Semrush spend
- bulk capture
- recurring capture

Exit criteria:

- provider admission approved;
- pull recipe and stop conditions exist.

Next milestone: M14

---

### M14 - Typed Read API / MCP Contract and Prototype

Status: planned

Purpose:
Expose evidence through bounded typed read tools without giving LLMs SQL or credentials.

Required reading / planning context:

- M7 typed API/MCP read-tool contract
- M12 first-slice outputs
- M8 read-tool hammer expectations
- `planning-inbox/audit-response-2026-07-07.md`

Blockers:

- Typed read-tool contract must exist.
- First evidence slice must exist to read from.

Allowed work:

- read API contract
- MCP read tool contract
- evidence-pack output shape
- freshness/blind-spot warnings
- provider disagreement output
- prototype after contract gate

Forbidden work:

- arbitrary SQL tool
- table CRUD tools
- direct DB credentials to LLM/agents
- write tools before separate governance

Exit criteria:

- read tools expose evidence safely;
- no direct SQL/credential path exists.

Next milestone: M15

---

### M15 - SearchClarity Proof Workflow

Status: planned

Purpose:
Prove Observatory can support SearchClarity-style evidence without becoming a customer database.

Required reading / planning context:

- M7 SearchClarity consumer-contract placeholder
- M7 promotion / conclusion-handoff contract
- M14 typed read outputs
- M6 claim-safety research outputs
- `planning-inbox/audit-response-2026-07-07.md`

Blockers:

- Typed read surface must exist.
- Claim-safety and customer-data boundaries must be contractually clear.

Allowed work:

- evidence-pack to report-support workflow
- claim-safety matrix use
- customer-scoped public observation handling
- read-time first-party overlay contract if needed

Forbidden work:

- customer records in Observatory
- report delivery records in Observatory
- customer first-party storage in Observatory

Exit criteria:

- evidence can support a customer-facing report workflow externally;
- customer data boundary holds.

Next milestone: M16

---

### M16 - Provider Cross-Check Proof

Status: planned

Purpose:
Prove provider disagreement can be represented and read without making any provider truth.

Required reading / planning context:

- M7 Provider Cross-Check & Disagreement Model contract
- M7 Provider Disagreement Ledger candidate contract
- M14 typed read outputs
- M13 admitted provider/pull plan if real providers are involved
- `planning-inbox/audit-response-2026-07-07.md`

Blockers:

- Provider disagreement contract must exist.
- If using real provider observations, provider admission must be complete.

Allowed work:

- compare admitted provider fixtures or controlled observations
- capture-time-distance warnings
- proprietary score labels
- provider personality/profile notes
- disagreement evidence output

Forbidden work:

- truth scores
- provider winner logic
- unapproved tool purchases
- recurring cross-provider capture

Exit criteria:

- disagreement appears as evidence;
- read tools explain disagreement and caveats.

Next milestone: M17

---

### M17 - Owned Telemetry Overlay Proof

Status: planned

Purpose:
Prove read-time overlay behavior for owned/internal or customer first-party series without contaminating Observatory storage.

Required reading / planning context:

- M7 owned telemetry overlay contract
- M8 overlay no-persistence hammers
- M14 typed read outputs
- M4 boundary outputs
- `planning-inbox/audit-response-2026-07-07.md`

Blockers:

- Overlay contract and no-storage hammers must exist.

Allowed work:

- overlay contract
- ephemeral input behavior
- alignment against Observatory evidence
- no-storage tests

Forbidden work:

- customer first-party storage in Observatory
- private analytics ingestion as canonical data

Exit criteria:

- overlay works without persistence;
- boundary is proven by tests.

Next milestone: M18

---

### M18 - Recurring Watch Panel Planning

Status: planned

Purpose:
Plan recurring capture only after provider, cost, rights, recipe, and hammer gates exist. M18 is planning only; recurring capture execution is not part of v1 unless the owner explicitly changes the roadmap.

Required reading / planning context:

- M13 provider admission outputs
- M16 provider cross-check proof outputs
- M8 hammer matrix
- M6 freshness/staleness/volatility research outputs
- `planning-inbox/audit-response-2026-07-07.md`

Blockers:

- Provider/cost/rights gates must exist before recurring capture planning is meaningful.

Allowed work:

- watch panel design
- cadence policy
- budget policy
- stop conditions
- stale/coverage warnings

Forbidden work:

- scheduler implementation before approval
- autonomous spend
- broad crawling/scraping

Exit criteria:

- recurring capture can be approved or rejected responsibly.

Next milestone: M19

---

### M19 - Hardening, Backup, Recovery, and Operations

Status: planned

Purpose:
Make Observatory durable, auditable, and recoverable.

Required reading / planning context:

- M12 first-slice build outputs
- M18 recurring watch panel plan
- M8 hammer matrix
- `planning-inbox/audit-response-2026-07-07.md`

Blockers:

- Evidence system must exist enough to harden.
- Raw archive/hash expectations must be known.

Allowed work:

- backup plan
- restore proof
- audit log expectations
- secret exposure checks
- retention cleanup proof
- operational runbooks

Exit criteria:

- restore proof exists;
- operational risk is documented;
- evidence system is not fragile glassware.

Next milestone: M20

---

### M20 - Observatory v1 Acceptance

Status: planned

Purpose:
Accept or reject Observatory v1 against doctrine, evidence behavior, hammers, and consumer usefulness.

Required reading / planning context:

- M19 hardening / backup / recovery outputs
- M8 hammer matrix and hammer results
- M12 first-slice proof outputs
- M15 SearchClarity proof outputs
- M16 Provider Cross-Check proof outputs
- M17 owned telemetry overlay proof outputs
- `planning-inbox/audit-response-2026-07-07.md`

Blockers:

- Acceptance evidence bundle must be defined by M19 or before M20 activation.

Acceptance questions:

- Does it store observations, not conclusions?
- Does it preserve raw/provenance/rights/freshness?
- Does it keep provider disagreement first-class?
- Does it avoid customer-record and first-party-data contamination?
- Does it expose evidence through safe typed reads?
- Does it support a useful SearchClarity/internal proof?
- Do hammers pass?

Exit criteria:

- v1 accepted, rejected, or returned for hardening.

---

## Deferred / Maybe Later

These are visible so they do not keep reincarnating as surprise side quests.

| Item | Status | Current rule |
|---|---|---|
| dashboard/operator console | deferred | Not active until evidence/read workflows prove need |
| persistent Strategy/IMI storage | forbidden unless owner ruling | Must not live inside Observatory; requires explicit future doctrine change elsewhere |
| cross-scope aggregate seismograph | forbidden unless owner ruling | Requires governed exception because cross-scope aggregation can leak customer-engagement intelligence |
| embeddings/vector store | deferred | No vector store until retrieval need is proven and boundary-safe |
| automated recurring capture | deferred | Requires provider admission, cost gates, rights rules, recipes, and hammers |
| customer-facing report automation | deferred | Belongs to SearchClarity/consumer workflow, not Observatory core |
| Ahrefs/Semrush integration | deferred | Future provider admission only; no purchase/integration now |
| tactic verdict database | forbidden unless owner ruling | Too close to Strategy/IMI storage and VEDA Brain revival |

---

## Notes for LLMs

The roadmap is not permission to build everything named in it.

A named future item is not approved work.

A contract milestone is not a schema milestone.

A research gate is not a provider purchase.

Deferred means: remember it, do not build it.

Forbidden unless owner ruling means: stop unless the owner explicitly changes project law.

Killed means: do not sneak it back in wearing a fake mustache.
