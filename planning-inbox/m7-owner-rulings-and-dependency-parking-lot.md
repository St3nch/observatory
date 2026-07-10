# M7 Owner Rulings and Dependency Parking Lot

Status: planning control / dependency parking lot
Authority: planning input only; not doctrine, not schema approval, not implementation approval
Milestone context: M7 — Core Contract Planning
Created: 2026-07-10
Source inputs:

- `planning-inbox/research/research-review-summary.md`
- R1–R10 foundation research batch
- Hermes research review discussion, parked outside Observatory core
- Strategy Layer / Neon Ronin gateway discussion, parked for later consumer-layer work

---

## Purpose

This document extracts unanswered, deferred, or milestone-dependent topics from the research review so they are not lost and are not accidentally activated early.

The research batch answered enough to proceed with M7 contract planning. The items below are either:

- owner rulings needed during M7;
- dependency topics that must remain parked until their owning milestone;
- targeted verification work needed before later provider/tool/customer admission;
- future architecture notes that should not contaminate Observatory core.

This document does not authorize implementation, schema, provider pulls, subscriptions, capture automation, customer-facing reports, or strategy-layer work.

---

## Current stewardship verdict

```text
Foundation deep research is complete enough for M7.
The next work is contract planning, not more broad research.
Unanswered items are milestone-dependent and parked here so M7 can proceed cleanly.
```

---

## M7 questions that must be answered by contracts

These are not broad research blockers. They are the immediate contract questions M7 should resolve.

| ID | Question | Expected M7 disposition | Notes |
|---|---|---|---|
| M7-Q1 | What is the minimum M7 contract set? | decide and draft spine contracts | Avoid overbuilding consumer/API/provider-specific contracts. |
| M7-Q2 | What is a valid observation? | define minimum fields, blockers, and warning-only gaps | Core of CapturePackage / evidence contract. |
| M7-Q3 | What are the source-admission classes? | classify admitted/candidate/blocked/source-specific review needed | Prevent flattening all data into generic rows. |
| M7-Q4 | What is the raw archive rule? | default restrictive; raw retention exception-only | Full HTML/DOM/raw payloads must not become default. |
| M7-Q5 | What claim language is allowed, caveated, or forbidden? | draft claim-safety contract | Must keep strategy/recommendations out of Observatory core. |
| M7-Q6 | What does “not observed” mean? | define absence / negative-evidence rules | Must remain context-bound. |
| M7-Q7 | What freshness and warning labels exist? | define vocabulary, not implementation | Feeds M8 hammers and M14 typed reads later. |
| M7-Q8 | How is provider disagreement represented? | provider-attributed evidence now; comparison likely read-time later | Do not persist fake provider-truth scores. |
| M7-Q9 | What evidence/citation handles are needed? | define contract concept | Exact global vs artifact-local handle design can remain owner/M7 decision. |
| M7-Q10 | What manual capture rules are needed before any capture tool exists? | define boundaries | Chrome extension/Hermes implementation stays later. |

---

## Recommended minimum M7 contract spine

Candidate contract families to draft first:

1. Scope / Source Admission / Rights / Retention
2. Evidence ID / Citation Handle
3. Claim Safety / Negative Evidence
4. Freshness / Volatility
5. Capture Package / Raw Archive / Manual Capture
6. Provider Testimony / Cross-Check
7. Query Panel / Prompt Panel Context

Consumer-specific, API-specific, provider-specific, and strategy-layer contracts should remain skeletal unless M7 directly requires a boundary placeholder.

---

## Owner-ruling candidates

These are decisions the owner/steward may need to make before or during M7 contract closure.

| Ruling ID | Topic | Default starting posture | Needed by | Source/context |
|---|---|---|---|---|
| OR-M7-1 | Minimum M7 contract set | draft spine contracts only | M7 | Research review summary |
| OR-M7-2 | Claim statuses that block downstream output | block unsafe claims by default | M7/M8 | R7 claim-safety research |
| OR-M7-3 | Predictive/recommendation text in Observatory read tools | no durable storage; consumer-owned only | M7/M14 | R7, doctrine boundary |
| OR-M7-4 | Citation handle model | contract concept now; exact design later if needed | M7/M15 | R5/R6/R7/R10 |
| OR-M7-5 | Raw archive defaults | raw retention exception-only | M7 | R1/R4/R5/R6/R10 |
| OR-M7-6 | Manual screenshot retention and redistribution | allow only with rights/context caveats | M7/M15 | R4/R10 |
| OR-M7-7 | Collector context envelope | require geo/device/language/query/prompt context where relevant | M7/M8 | R6/R7/R8 |
| OR-M7-8 | Public comments / UGC retention | excluded by default unless specifically admitted | M7/M13/M15 | R4/R5A/R10 |
| OR-M7-9 | Provider disagreement ledger persistence | compute/read-time by default; no persisted ledger yet | M7/M14 | R2/R7/R9 |
| OR-M7-10 | Evidence package minimum fields | define minimum and reject/warn states | M7 | Cross-report finding |

---

## Dependency topic parking lot

These topics are real, but they are not all M7 blockers. Do not activate all of them now.

| Topic ID | Topic | Current disposition | Owning milestone / phase | Activation trigger | Why parked |
|---|---|---|---|---|---|
| D1 | Consumer Auth/AuthZ and Evidence Access Boundary | parked | M14+ | typed read tools or consumer access design starts | Not needed before core contracts. |
| D2 | Provider Credentials, Secrets, Cost Controls, and Pull Authority | parked | M13 | provider admission or paid probe packet starts | Needed before paid pulls, not before M7 contracts. |
| D3 | First-Party Telemetry Overlay and Customer Data Separation | parked | M14/M15/M17 | GSC/Bing/YouTube Analytics/customer overlay work starts | Customer/private data remains outside Observatory core. |
| D4 | Intervention Timeline Joins Without Causal Overclaiming | parked | M15 | before/after SearchClarity proof is attempted | Prevents causal overclaiming from timing alone. |
| D5 | Coverage, Blind Spots, and Not-Observed Reporting | partial M7 input; fuller later | M7/M8/M14 | absence claims or typed read warnings are drafted | Needed for claim safety and hammers. |
| D6 | Ahrefs / Semrush Admission and Replacement Analysis | parked | M16 or paid subscription consideration | subscription/API/provider admission is considered | Not early; no new Semrush posture change here. |
| D7 | Manual Evidence Capture Workflow and Browser Extension Boundary | partial M7 input; implementation later | M7/M15+ | capture instrument proof starts | Contract boundaries before tools. |
| D8 | Report-Safe Citation Handles and Evidence Reference Rules | active M7 input | M7/M15 | evidence/citation contract drafting starts | Needed before reports can safely cite evidence. |
| D9 | Typed Read Tool Output Warnings and Evidence Response Shape | skeleton only | M14 | typed API/MCP/read tool design starts | M7 should define vocabulary only. |
| D10 | SearchClarity First Proof Service Evidence Boundary | parked | M15 | SearchClarity proof planning starts | SearchClarity owns reports/recommendations/customer outputs. |
| D11 | DataForSEO Evidence Probe CLI and Payload Inspection | parked; likely controlled probe later | pre-M13/M13 | owner approves credits, spend cap, endpoint list | Needed to inspect real payloads before schema/provider admission. |
| D12 | Source-Report Citation Hygiene and External Claim Reverification | parked; targeted cleanup | before contract promotion or provider/tool admission | a report claim becomes load-bearing contract language | Some report citations/access dates need recheck. |
| D13 | Google Maps / GBP / Local-Pack Evidence Boundary | parked | M13/M15 | local-pack or GBP evidence is admitted | Must avoid Maps/GBP content warehousing. |
| D14 | Chrome Extension Evidence Capture Candidate | parked implementation; contract input only | after M7 / before capture proof | capture tooling is authorized | Extension is a capture instrument, not Observatory core. |
| D15 | Hermes External Operator-Assist Boundary | parked outside Observatory core | strategy/SearchClarity/Neon Ronin later | strategy/operator layer work begins | Hermes is not a core capture/write engine. |
| D16 | Strategy Layer / Neon Ronin Gateway | parked future architecture | later consumer/strategy milestone | Neon Ronin agents need governed Observatory evidence access | Strategy layer belongs outside Observatory core. |

---

## DataForSEO evidence probe — parked concept

Owner proposal: add controlled credits and build a small CLI probe to pull actual DataForSEO API data.

Current disposition:

```text
Valid future research/probe concept.
Not provider admission.
Not schema approval.
Not implementation approval yet.
```

Purpose when activated:

- inspect real payloads instead of designing from docs alone;
- confirm endpoint response shapes;
- identify required provenance/cost/status/error metadata;
- preserve sample JSON as probe evidence;
- inform later schema and provider admission decisions.

Required controls before activation:

- explicit owner approval;
- fixed credit/spend cap;
- tiny endpoint list;
- no recurring pulls;
- no customer data;
- no customer-facing output;
- no broad integration;
- raw JSON saved as probe/research evidence only;
- payload field summary produced after each pull;
- no schema/migration decision from first sample alone.

Likely owning phase: controlled pre-M13 probe or M13 provider admission preparation.

---

## Hermes / browser-agent topic — parked outside Observatory core

Hermes is not part of Observatory core.

Current disposition:

```text
Hermes may be useful later as an external operator-assist or strategy-layer tool.
It is not admitted as an Observatory capture/write engine.
```

Allowed future consideration outside core:

- operator research assistance;
- capture-session organization;
- duplicate-capture reminders;
- SearchClarity work notes;
- strategy-layer interpretation drafts;
- Neon Ronin / Kaizen workflow assistance.

Blocked for Observatory core:

- direct Observatory writes;
- recurring capture;
- stealth/anti-bot browser backends;
- marketplace automation;
- agent memory as evidence;
- agent summaries as evidence;
- strategy/recommendation storage;
- unattended browser crawling.

Related future topic: Strategy Layer / Neon Ronin Gateway.

---

## Strategy Layer / Neon Ronin Gateway — parked architecture note

The Strategy Layer is a future governed tunnel between Observatory evidence and systems that need to act on that evidence.

Working model:

```text
Observatory stores evidence.
Strategy Layer interprets evidence.
Neon Ronin manages project action.
Kaizen governs accepted decisions.
SearchClarity turns accepted work into service/customer outputs.
```

Current disposition:

```text
Important future architecture note.
Not part of M7 Observatory core contract work except as a boundary reminder.
```

Boundary:

- Neon Ronin agents should not directly access raw Observatory internals.
- Neon Ronin should go through a strategy/evidence-to-action gateway.
- Strategy outputs must not be stored back into Observatory as facts.
- SearchClarity customer-facing reports/recommendations remain outside Observatory core.

---

## Targeted verification list

These are not broad research tasks. They are recheck tasks before a claim becomes contract language or a provider/tool/surface is admitted.

| Verification topic | Recheck before | Notes |
|---|---|---|
| DataForSEO current pricing, endpoint coverage, terms, retention, display rights | DataForSEO probe/admission | Current provider docs/pricing can drift. |
| DataForSEO indemnity / upstream search-engine ToS exposure | DataForSEO admission | Owner-risk/admission issue. |
| YouTube Data API retention/deletion rules | YouTube public API admission | Especially public metadata/comment handling. |
| Etsy API / ToU caching and automation rules | Etsy API or capture-tool admission | Manual observation remains separate from API warehousing. |
| Pinterest API storage restrictions | Pinterest admission | Storage limits are central. |
| Fiverr programmatic access / automation terms | Fiverr capture/tool admission | Current terms posture must be confirmed. |
| Google Maps / GBP storage restrictions | local/GBP admission | Avoid Maps/GBP content warehousing. |
| OpenAI / AI-surface consumer UI automation restrictions | AI/GEO surface admission | Prefer official APIs where possible. |
| Ahrefs/Semrush display/export/API terms | paid suite admission | Not early; no current posture change. |
| Source-report citation placeholders/access dates | before contract promotion | Re-verify load-bearing external claims. |

---

## Do-not-activate-now list

Do not start these from this document:

- schema;
- migrations;
- provider integrations;
- paid pulls;
- DataForSEO CLI implementation;
- Chrome extension implementation;
- Hermes integration;
- strategy layer implementation;
- typed API/MCP tool implementation;
- customer-facing report drafting;
- marketplace automation;
- recurring capture;
- SearchClarity proof work;
- dashboard/operator console work.

---

## Immediate next step after this document

Proceed to M7 contract planning.

Recommended order:

1. Confirm the minimum M7 contract set.
2. Draft Scope / Source Admission / Rights / Retention contract.
3. Draft Evidence ID / Citation Handle and CapturePackage contract.
4. Draft Claim Safety / Negative Evidence contract.
5. Draft Freshness / Volatility contract.
6. Draft Provider Testimony / Cross-Check contract.
7. Convert accepted contract rules into M8 hammer candidates.

---

## Final rule

```text
The parked topics are real.
They are not permission to build.
They exist so M7 can proceed without losing future dependencies or activating them too early.
```
