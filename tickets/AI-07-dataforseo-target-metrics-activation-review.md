# AI-07 — DataForSEO AI Optimization Target Metrics activation review

**Status:** approved  
**Owner:** [GROK] technical review / [GPT] Steward reconciliation  
**Blocked by:** AI-06 — Search Mentions recipe selection and read API (`done`)  
**Approved by:** Project Steward  
**Start commit:** `fd133ba0fb9b9e3744484f98df2cce9ade8d86b4`

## Purpose

Decide whether DataForSEO AI Optimization Target Metrics should become Observatory's next
bounded provider contract after the completed Search Mentions vertical slice. Select one
exact adapter contract for a later probe ticket or recommend stopping.

AI-01 identified Target Metrics as the runner-up. That ranking is an input, not a foregone
conclusion. This review must recheck the complete current capability family and challenge
whether Target Metrics still offers the best readiness and learning value.

The intended analytical purpose is source-attributed target-level AI-search visibility
testimony that a downstream strategy system may later compare with Search Mentions,
Keyword Overview, and Google Organic without Observatory producing scores, recommendations,
or cross-provider conclusions.

## Authority and accepted foundation

- VISION API-only boundary, provenance, and strategy separation
- VOCABULARY definitions of Evidence, Derivation Recipe, Observation, Provenance, Data
  Period, and Provider Update Time
- D3 and D8 through D13
- F3, F6, F7, F8, F9, F10, and F12 remain unfired except for their explicitly recorded
  bounded satisfactions
- PF-09 shared bounded one-exchange transport
- PF-14 provider-read integrity hardening
- PF-15 migration hygiene
- AI-01 activation review and AI-02 through AI-06 accepted Search Mentions slice
- `docs/dataforseo-surface-roadmap.md`

## Review method

- Load the project-local `research`, `domain-modeling`, `codebase-design`, and
  `code-review` skills and report their absolute `SKILL.md` paths.
- Re-read current Observatory authority in the order required by `AGENTS.md`.
- Review current official DataForSEO documentation, pricing, and relevant terms for the
  complete Target Metrics capability family and directly adjacent contracts needed to make
  a deliberate selection. Correct every premise in this ticket against current official
  sources.
- Inspect the accepted Search Mentions, Keyword Overview, Google Organic, shared transport,
  Recipe, Derivation, PostgreSQL, and read-API code/tests only to identify reusable and
  dangerous seams. Do not edit files.
- Distinguish provider claimed contract, possible probe Evidence, and future normative
  Derivation Recipe under D12.

Ordinary public HTTPS access to official documentation is authorized. Provider API hosts,
account endpoints, credentials, authenticated requests, and real contract probes are not.

## Required analysis

1. Inventory the current Target Metrics family, including single-target and multi-target
   forms, Live/task/standard or other workflow variants, target kinds, platforms/models,
   historical/timeseries variants, and nearby top-page/domain/brand/category contracts
   where overlap affects the choice. Correct names and boundaries from current official
   documentation.
2. State the exact questions each materially distinct contract can answer. Separate
   indexed aggregate target testimony from Search Mentions question/answer/source records,
   Google Organic SERP testimony, Keyword Overview demand, and active LLM execution.
3. Record every request option that can materially change meaning or acquisition:
   target syntax/type, platform/model, location, language, date/period, filters, ordering,
   limits, pagination/continuation, enrichments, and any provider defaults.
4. Record every materially useful returned field and relationship, provider-native
   identifier, classification, metric, count, period, update time, target echo, and
   completeness/truncation statement. Identify ambiguous, undocumented, or internally
   inconsistent semantics.
5. Determine workflow shape precisely: one exchange versus submission/poll/result fetch,
   continuation or multi-page requirements, response-derived follow-up, documented timeout,
   expected response size, and whether the current HTTP event model can represent the
   contract honestly without overloading `prior_attempt_id`.
6. Recheck current pricing and billing grain from official sources. Separate per-request,
   per-task, per-target, per-row, and continuation/page charges. Propose a conservative
   worst-case micro-USD ceiling for the smallest useful probe set; this is not spend
   authorization.
7. Define candidate semantic identities and occurrence relationships without writing a
   Recipe: requested target versus returned identity, target kind, platform/model, location,
   language, time/period, metric/classification kind, duplicates, ordering, null/absence,
   and parent/child attachment.
8. Explain corpus and absence semantics. Distinguish provider total count, returned count,
   omitted target, true stated zero, JSON null, permitted absence, unsupported context,
   request-disabled testimony, truncation, and provider failure.
9. Map overlap and independent-disagreement value against the accepted Search Mentions,
   Keyword Overview, and Google Organic testimony. State which fields would be redundant
   cost and which would add independently useful testimony.
10. Assess retention, privacy/personal-data, provider-terms, and API-redistribution risk for
    every proposed retained field. Do not assume AI Optimization family members share one
    text-retention posture.
11. Identify architecture and test seams that genuinely generalize from the three accepted
    provider surfaces, and seams that must remain Target-Metrics-specific. Explicitly assess
    the shared transport profile, closed event-v2 adapter dispatch, Recipe identity,
    envelope/typed-detail pattern, result-context membership, occurrence modeling,
    classification-gated emptiness, verify-before-limit, and read-only API boundaries.
12. Identify likely false-green tests, adversarial cases, drift hazards, high-cost mistakes,
    and assumptions one real payload cannot prove.
13. Propose the smallest useful real probe matrix. Every proposed call must exercise a
    material contract branch. Give exact purpose, request shape, expected learning, maximum
    call count, response-size expectation, and conservative worst-case cost.
14. Recommend one exact first adapter contract, retain a runner-up, or recommend stopping.
    Explain whether Target Metrics remains the best next major surface after AI-06.

## Mandatory candid report

Return:

- recommendation, exact proposed contract, and runner-up;
- direct official-source links and the date each external claim was checked;
- strong, weak, ambiguous, undocumented, and conflicting provider-contract areas;
- the exact probe matrix and conservative maximum spend;
- reusable architecture seams and surface-specific seams;
- code/test weaknesses exposed by inspecting the current implementation;
- likely false-green tests and required adversarial proofs;
- most fragile assumptions and highest-cost mistakes;
- materially useful or historically irrecoverable dimensions deliberately not proposed for
  acquisition, with the trigger for revisiting each;
- open Product Owner or Steward decisions required before any probe ticket;
- whether a bounded one-exchange adapter fits current authority or requires new
  multi-exchange provenance first;
- exact unproven limits and any false premises in this assignment;
- confirmation of zero repository mutation and zero provider/API-host/credential/spend use.

Do not merely summarize documentation. Use frontier-model judgment: tell the Steward what
the current implementation makes easy, what it makes dangerous, what should be improved
before another surface, and what should remain deliberately duplicated or surface-local.

## Hard boundaries

- Read-only technical review. Do not edit, create, delete, format, commit, amend, push,
  branch, stash, or change ticket status.
- No DataForSEO API-host request, DNS diagnostic, account login, credentials, provider
  transport, paid gate, Evidence creation, PostgreSQL mutation, or provider spend.
- No ordinary/full test run. Read existing code and tests; this ticket proves analysis, not
  executable behavior.
- No adapter, event schema, transport profile, parser, Recipe, fixture, Derivation,
  migration, typed relation, selection, API route, generic framework, scheduler, strategy,
  report, or backup implementation.
- Do not activate continuation, multi-exchange provenance, F3, routine F6, F7, F8, F9,
  F10, or F12.
- Do not reopen AI-06 or implement the separately recorded unknown-query or
  Organic/Keyword Overview classification findings.
- Do not treat a proposed probe matrix as authorization to issue any call.

## Deliverable

Return one bounded technical report to [CHAZ] for relay to the Project Steward, then stop.
The Steward will reconcile the findings and decide whether to authorize a separate
Evidence-only probe ticket.
