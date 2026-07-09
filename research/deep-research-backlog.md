# Deep Research Backlog

Status: backlog / research planning support
Authority: planning support only; not doctrine, not provider admission, not implementation approval
Milestone: M6 — Research Gate Execution
Date: 2026-07-07

---

## Purpose

This file preserves topics that need deeper research, validation, or owner review after the current M6 research gates.

The M6 research gates are answering what is needed to enter M7 contract planning. They are not intended to exhaust every provider, platform, legal, methodology, or implementation question.

This backlog prevents those deeper questions from disappearing.

---

## Working distinction

### Answered enough for M7

A topic is answered enough for M7 when current research can define:

- contract inputs;
- boundary constraints;
- fail-closed behavior;
- owner-ruling candidates;
- hammers needed before implementation;
- provider/capture admission blockers.

### Needs deeper research later

A topic needs deeper research when it is required before:

- provider admission;
- paid provider pulls;
- customer-facing reports;
- schema design;
- raw payload retention;
- marketplace capture;
- AI/GEO methodology claims;
- cross-provider proof;
- recurring capture;
- implementation acceptance.

---

## Backlog topics

### DR1 — DataForSEO endpoint-by-endpoint admission research

Why it matters:
RG1 confirmed DataForSEO is plausible but not admitted. Before any paid pull, the project needs endpoint-specific rights, payload, cost, and retention answers.

Questions to answer later:

- Which exact endpoints are first-slice candidates?
- What does each endpoint return now?
- What fields are raw-only vs promoted hot-path candidates?
- What are task/call costs under current pricing?
- What duplicate-task risks exist per endpoint?
- What provider task IDs, timestamps, and status fields are available?
- What raw retention is permitted under terms and project law?
- What exact stop conditions should be enforced?

Blocks:

- DataForSEO provider admission;
- validation budget use;
- CapturePackage provider recipe;
- raw archive policy for provider payloads.

Feeds:

- M13 provider admission;
- M8 hammers;
- M10 schema planning;
- RG11 raw archive/provider drift.

---

### DR2 — Raw payload retention and allowed-use interpretation

Why it matters:
RG1 did not fully clear long-term raw payload retention. RG10 requires raw payload pointer/hash handling if raw retention is admitted.

Questions to answer later:

- Which source families allow durable raw retention?
- Which require capture-and-purge?
- Which require no-storage overlay only?
- What should be stored as raw payload versus derived observation?
- What redaction or minimization rules are needed?
- What purge proof is required?
- How should retention expiration affect evidence IDs and citations?

Blocks:

- raw archive implementation;
- provider admission;
- long-term evidence preservation;
- customer-facing auditability.

Feeds:

- RG11;
- M7 raw support contract;
- M8 retention hammers;
- M10 schema planning.

---

### DR3 — DataForSEO / Ahrefs / Semrush comparison methodology

Why it matters:
Provider disagreement is a feature, not a bug. But each provider defines metrics differently.

Questions to answer later:

- Which metrics are meaningfully comparable across providers?
- Which are proprietary and non-comparable by default?
- How do volume, keyword difficulty, backlink counts, ranking observations, authority metrics, and SERP features differ by provider?
- What provider documentation explains definitions?
- What must read tools disclose beside each value?
- Can disagreement itself be categorized without ranking providers?

Blocks:

- Provider Cross-Check proof;
- customer-facing provider disagreement output;
- multi-provider capture design.

Feeds:

- M16 Provider Cross-Check proof;
- M7 Provider Cross-Check contract;
- M15 SearchClarity report language.

---

### DR4 — GEO / AI citation measurement methodology

Why it matters:
RG6 establishes caution, but customer-facing GEO/AI reports need deeper methodology before they can be trusted.

Questions to answer later:

- What sample sizes are reasonable for AI answer-surface claims?
- Which providers/surfaces should be included first?
- How should prompts be selected and versioned?
- How should mention, citation, citation position, and possible influence be separated?
- When is citation absorption/influence scoring too speculative?
- How should absence be phrased across repeated runs?
- What current research or provider docs should be treated as methodology anchors?

Blocks:

- report-safe AI visibility metrics;
- AI Optimization validation pull;
- customer-facing GEO proof;
- recurring AI monitoring.

Feeds:

- M15 SearchClarity proof;
- M13 provider admission;
- M8 claim-safety hammers.

---

### DR5 — Google AI Overview / AI Mode capture and visibility limits

Why it matters:
AI Overviews and AI Mode may not behave like classic SERP results, and direct capture may have source/platform constraints.

Questions to answer later:

- What can be captured from Google AI Overviews through admitted providers?
- What can be captured manually without violating platform constraints?
- What source/citation metadata is visible or provider-exposed?
- How volatile are results by query, location, account, and time?
- How does query fan-out affect measurement?
- What language is safe for customer-facing reports?

Blocks:

- Google AI-surface evidence family admission;
- SearchClarity GEO reports;
- AI answer-surface query panels.

Feeds:

- RG6 refinements;
- M13 provider/capture admission;
- M15 proof workflow.

---

### DR6 — Marketplace platform evidence limits: Etsy

Why it matters:
RG7 found Etsy automation is blocked by default and Etsy API use has strong restrictions.

Questions to answer later:

- Is there any Etsy API use case that safely supports SearchClarity visibility evidence?
- Is express written authorization realistic or needed?
- What public evidence can be used manually in reports without Observatory storage?
- What must remain SearchClarity-side only?
- What retention rules apply to Etsy API/displayed content?
- Can Etsy evidence ever become Observatory evidence, or should it remain consumer/report-side?

Blocks:

- Etsy marketplace observation family;
- Etsy report-safe evidence;
- browser-extension capture decisions.

Feeds:

- M15 SearchClarity proof;
- M13 capture admission;
- M8 marketplace boundary hammers.

---

### DR7 — Marketplace platform evidence limits: Fiverr

Why it matters:
RG7 did not clear Fiverr automated capture. Fiverr may still matter for SearchClarity launch and gig/report workflows.

Questions to answer later:

- What do current Fiverr terms say about automated access, scraping, public gig capture, and data use?
- Is public manual review acceptable as consumer-side workflow evidence?
- Is any API/provider path available?
- What data must stay out of Observatory?
- What report language is safe for Fiverr marketplace observations?

Blocks:

- Fiverr capture admission;
- Fiverr marketplace panels;
- customer-facing Fiverr evidence claims.

Feeds:

- M15 SearchClarity proof;
- M13 capture admission.

---

### DR8 — Manual capture and browser-extension capture admissibility

Why it matters:
The harvest register keeps a slim manual/operator capture family but defers marketplace gig/listing snapshots and browser-extension capture.

Questions to answer later:

- What counts as manual observation versus automated capture?
- Can human notes become Observatory evidence?
- When are screenshots allowed, forbidden, or capture-and-purge only?
- Can a browser extension ever be an admitted capture instrument?
- What per-platform ToS reviews are required?
- What provenance fields prove human/operator capture integrity?

Blocks:

- manual marketplace evidence;
- browser-extension capture;
- screenshot/raw payload retention.

Feeds:

- M13 capture admission;
- M8 hammers;
- M15 proof workflow.

---

### DR9 — SearchClarity customer-facing report language validation

Why it matters:
RG8 provides claim-safety patterns, but final report language belongs to SearchClarity and must fit actual services.

Questions to answer later:

- What language should SearchClarity use for Etsy/Fiverr/SEO/GEO audit reports?
- What guarantees must be explicitly disclaimed?
- What evidence caveats should be shown to customers?
- How should provider estimates be explained simply?
- How should AI/GEO visibility be sold without overclaiming?
- What standard report sections should cite Observatory evidence IDs?

Blocks:

- customer-facing proof workflow;
- report-safe evidence handles;
- service launch copy tied to evidence.

Feeds:

- M15 SearchClarity proof;
- consumer contract inputs;
- M14 read-tool output shape.

---

### DR10 — Customer first-party overlay contract

Why it matters:
Customer first-party data stays out of Observatory, but read tools may align external observations against supplied overlays.

Questions to answer later:

- What overlay inputs can read tools accept?
- How are overlay timestamps/freshness supplied?
- How is overlay data prevented from being stored?
- How does before/after analysis work without storing customer private data?
- What proof shows no overlay leakage into Observatory persistence?

Blocks:

- customer before/after claims;
- SearchClarity report proof;
- read-tool overlay design.

Feeds:

- M14 typed read API;
- M15 SearchClarity proof;
- M17 owned/customer overlay proof.

---

### DR11 — Owned internal first-party telemetry

Why it matters:
Owned internal telemetry is possible under `internal` scope but not automatically admitted.

Questions to answer later:

- Which owner-owned properties are in scope?
- What data can be stored directly?
- What rights/retention rules apply?
- How does internal telemetry differ from customer first-party overlays?
- What hammers prove customer telemetry cannot leak in under internal scope?

Blocks:

- internal first-party storage;
- owned-property before/after proof;
- internal telemetry schema planning.

Feeds:

- M17 owned telemetry overlay proof;
- M10 schema planning;
- M8 scope-isolation hammers.

---

### DR12 — Query panel sampling and recapture cadence

Why it matters:
RG4 and RG5 define panels and freshness, but cadence needs deeper methodology before recurring capture.

Questions to answer later:

- How often should each evidence family be recaptured?
- Which surfaces need daily, weekly, monthly, or event-triggered recapture?
- What cadence is affordable under provider costs?
- What cadence is necessary for customer-facing claims?
- How should update windows trigger recapture?
- What blind spots should drive new capture requests?

Blocks:

- recurring capture;
- cost-aware collection planning;
- customer-facing current-state claims.

Feeds:

- M13 capture recipes;
- M14 read tools;
- M8 cost/cadence hammers.

---

### DR13 — Raw archive layout and provider drift fingerprints

Why it matters:
Provider payloads change. Drift should become evidence instead of breakage.

Questions to answer later:

- Should raw archive be filesystem-first, object-storage-first, database-first, or hybrid?
- What manifest fields are required?
- How should shape fingerprints be generated?
- What counts as provider drift versus parser bug?
- How should provider drift affect observation parsing and evidence IDs?
- What retention and purge rules apply to drift artifacts?

Blocks:

- raw archive implementation;
- provider drift hammers;
- parser/schema planning.

Feeds:

- RG11;
- M10 schema planning;
- M12/M13 capture proof.

---

### DR14 — Evidence ID, citation handle, and report-safe reference finalization

Why it matters:
RG3 separates identifier concepts, but final formats and resolution behavior still need contract decisions.

Questions to answer later:

- Are citation handles global or artifact-local?
- Are report-safe references separate from evidence IDs?
- How are withdrawn/superseded/expired evidence IDs handled?
- What can customers see?
- How do citations survive schema evolution?

Blocks:

- report-safe evidence packs;
- customer reports;
- API/MCP evidence lookup.

Feeds:

- M7 evidence contract;
- M14 read API;
- M15 SearchClarity proof.

---

### DR15 — Hammer matrix hostile-path expansion

Why it matters:
M8 will need hostile-path tests. RG13 will draft inputs, but deeper hammer design may be needed before implementation.

Questions to answer later:

- What exact tests prove no strategy storage?
- What tests prove rights fail closed?
- What tests prove customer-private data cannot enter Observatory?
- What tests prove provider disagreement is not averaged?
- What tests prove no direct SQL/credential exposure?
- What tests prove cost ceilings and duplicate-task rejection?

Blocks:

- implementation acceptance;
- provider admission;
- customer-adjacent read tools.

Feeds:

- RG13;
- M8 hammer matrix;
- M13 provider/capture admission.

---

### DR16 — Consumer authentication / authorization model

Added 2026-07-07 during the M7 audit-fix pass (both 2026-07-07 audits).

Why it matters:
RG12 names consumer authentication/authorization as an owner-ruling candidate, but no research topic owned it. Without it, M14 would improvise access control as an implementation detail.

Questions to answer later:

- How do consumers (SearchClarity, Neon Ronin, Kaizen, internal) authenticate to the Observatory API?
- How is per-consumer, per-scope authorization enforced at the API layer?
- How do consumer identities map to scopes without becoming customer records or foreign keys?
- What audit records must consumer requests produce?
- How are read-tool permissions scoped so no consumer can read another consumer's engagement scopes?
- What token/credential lifecycle rules apply, and where do secrets live (never with LLMs/agents)?

Blocks:

- M14 typed read API / MCP contract and prototype;
- consumer-facing read-tool exposure;
- M15 SearchClarity proof workflow access path.

Feeds:

- M14 typed read API / MCP contract;
- M8 access-boundary and scope-isolation hammers (H1, H17);
- M7 consumer contract (as a named blocker section).

---

### DR17 — Provider credential and secret handling posture

Added 2026-07-07 during the M7 audit-fix pass (both 2026-07-07 audits).

Why it matters:
No research topic covered provider API key storage or secret management. M11 only says "local config pattern without secrets." Provider admission (M13) practically requires this answered.

Questions to answer later:

- Where do provider API keys live (env, OS keystore, secret manager), and what is forbidden (repo, planning docs, prompts, LLM context)?
- How does the capture path access credentials without exposing them to LLMs/agents (boundary law: no credentials to LLMs)?
- What rotation, revocation, and compromise-response expectations apply?
- What audit trail exists for credential use and provider spend attribution?
- What hammers prove secrets cannot leak into raw payloads, manifests, evidence packs, logs, or read-tool output?

Blocks:

- M13 provider admission and any funded provider account;
- capture runner planning;
- M19 operations hardening for secret exposure checks.

Feeds:

- M13 provider admission plan;
- M8 hostile-path hammers (H7, H17, H18);
- M19 secret exposure checks.

---

## Backlog use rule

This backlog is a parking lot for deeper research, not permission to build.

Before any item becomes active work, a roadmap milestone, owner ruling, or research gate must explicitly activate it.

---

## Final rule

```text
M6 answers what contracts need next.
This backlog preserves what still needs deeper proof before providers, captures, reports, schema, or implementation are admitted.
```
