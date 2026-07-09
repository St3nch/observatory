# Observatory M7 Audit Report — Post-M6 Research Gate Closure

Auditor: Claude (Observatory Project Steward role)
Date: 2026-07-07
Scope: All root authority docs, `research/README.md`, all 13 RG outputs, `deep-research-backlog.md`, `m5-research-gate-plan.md`, planning-inbox index and M4 reconciliation note.
Authority: audit report; planning input only; nothing here is doctrine until promoted.

---

## 1. Executive verdict

The M6 research set is real work, not vibes. All 13 gates exist, are indexed, are internally cross-referenced, and consistently refuse to authorize anything they weren't allowed to authorize. Doctrine discipline is unusually good — every RG ends with non-goals, owner-ruling candidates, and blockers, and none of them smuggles admission, schema, or strategy storage.

**Verdict: Yes, with caveats.** M7 contract planning can proceed. The caveats are real but small: a hammer-category gap in RG13 (append-only, concurrency, audit-record, migration rollback are in roadmap/inherited doctrine but missing from the RG13 matrix), two soft spots in RG6 that could drift toward interpretation storage, a silent mapping gap between the 12 gate topics in ROADMAP's M5 section and the 13 gates actually executed (surface-coverage/blind-spot reporting fell through the crack), stale text in `research/README.md`, and roughly forty owner-ruling candidates scattered across thirteen files with no consolidated tracker.

None of these blocks contract drafting. Two should be fixed before the first contract is written; the rest during M7.

---

## 2. M6 completion audit

All 13 expected gates exist under `research/`, match the M5 plan's output-doc names, and are indexed in `research/README.md` with correct anti-authority labels ("contract-planning input only, not schema approval"). `deep-research-backlog.md` exists with DR1–DR15. Every gate answers its M5 gate question at contract-planning depth, cites local sources, and cites current external sources where the M5 plan required them (RG1, RG5, RG6, RG7). Gates that skipped external sourcing (RG2, RG3, RG4, RG8–RG13) explain why, and the reasons hold — they define internal models, not external facts.

Two mapping notes, not failures:

- RG11's gate question in the output file ("What raw archive and provider drift rules are needed before provider payloads, parsers, or observations can be trusted?") is a reworded version of the M5 plan's question. Same intent, no scope drift. Same for RG12. Fine.
- ROADMAP's *planned* M5 section still lists the original 12 gate *topics* (which include "negative evidence / absence rules," "surface coverage / blind spots," "provider personality profiles," "owned property telemetry boundary"), while the M5 output defined 13 differently-cut gates. Most folded in cleanly: negative evidence/absence → RG6/RG8; provider personality → RG9; owned telemetry → RG2/RG12/DR11. **Surface coverage / blind spots (NC5) folded into nothing.** See Section 6.

M6 is complete. It closed correctly.

---

## 3. Milestone/status consistency audit

Checked: `README.md`, `LLM_START_HERE.md`, `ACTIVE_CONTEXT.md`, `ROADMAP.md`, `NEXT_SESSION_HANDOFF.md`, `research/README.md`, `REPO_MAP.md`, `planning-inbox/README.md`.

Consistent: README (M7 active), LLM_START_HERE (M7 after M6 closure), ACTIVE_CONTEXT (M6 closed, M7 active, M8 next), ROADMAP summary table and Active Milestone section, NEXT_SESSION_HANDOFF. The closure convention was followed.

Stale references found:

| File | Stale content | Severity |
|---|---|---|
| `research/README.md` — Reading Order | "No full research corpus exists yet. When M5 activates, read…" — the corpus exists and M5/M6 are closed | useful cleanup, fix now (it actively misleads a fresh session using the folder index as required reading) |
| `research/README.md` — Last Review Notes | "Open issues: M5 must create a research gate template before research execution" — done | useful cleanup |
| `REPO_MAP.md` — Current Folders table | `research/` status: "no research execution until M5/M6" — M6 executed and closed | useful cleanup |
| `ROADMAP.md` — Planned Milestones section | M4/M5/M6 full entries retained with "closed; closure details live above" stubs, and M7 appears in both Active and Planned sections | later improvement; duplication is a drift vector but currently harmless |
| `00-project-overview.md` header | "Status: draft" while REPO_MAP labels it authority | useful cleanup — pick one |
| `01-harvest-register.md` header | "Status: draft 1" while REPO_MAP labels it authority | useful cleanup — dispositions are owner-confirmed; "draft" undersells binding content |

No contradictions in milestone state. Handoff is clean.

---

## 4. Doctrine consistency audit

Checked all 13 gates against: observation/conclusion separation, no customer database, no customer first-party storage, provider testimony not truth, disagreement preserved, rights/retention fail closed, no direct SQL/credentials, no strategy storage, hammers as hard gate.

Overall: **the research set preserves doctrine, and in several places strengthens it.** No gate authorizes provider admission, pulls, schema, raw retention, marketplace capture, extension capture, customer-facing claims, visibility scores, strategy storage, or workflow storage. Every gate's non-goals section explicitly re-blocks these. RG10's invalid examples and RG13's hostile paths are actively hostile to renamed violations.

Three places where language could drift if copied into contracts unedited:

**D-A (RG6, `ai_entity_mention_observation`):** "sentiment/tone only if source/provider supplies it or downstream consumer computes it outside Observatory… If stored, it must be provider-attributed **or mechanically derived** under a later contract." Sentiment is judgment-laden; "mechanically derived sentiment" is a fake mustache away from stored interpretation. M4's D5 ruling limits mechanical derivation to no-judgment/no-weighting cases. The contract should permit sentiment fields only when provider-supplied and provider-attributed; drop "mechanically derived" or gate it behind explicit owner ruling.

**D-B (RG6, `ai_visibility_sample_summary`):** described as "an aggregate read model candidate" — ambiguous between a stored family and a read-time output. If stored, it's a derived/materialized record and must pass the V6 materialization test ("would computing on read produce the same result?"). The M7 contract must pin this as read-time output by default, with any stored summary requiring the materialization test plus owner sign-off.

**D-C (RG9, Provider Disagreement Ledger):** the roadmap lists a "Provider Disagreement Ledger candidate contract," and RG9's `disagreement_summary` includes `methodology_notes` and `caveats` — mostly mechanical comparison, but a persisted "ledger" of disagreement summaries is a derived store. Same treatment as D-B: default compute-on-read; a persisted ledger is a materialization-test + owner-ruling question inside the Cross-Check contract, not a presumed table.

Minor: RG4 panel items carry a `priority` field with no caveat that priority is a measurement-program ordering, not strategic importance-as-truth. One sentence fixes it in the contract. RG2's Example 1 pairs `not_expressly_prohibited` with `retain_with_source_terms`, which reads slightly more generous than RG2's own table ("not enough for broad storage"); tighten the example when contracted.

Nothing here authorizes forbidden work. These are pre-drift warnings, not violations.

---

## 5. Gate-by-gate assessment table

| Gate | File | Verdict | Why | M7 impact | Later deep research needed? |
|---|---|---|---|---|---|
| RG1 | rg1-dataforseo-rights-retention-cost.md | Usable but needs caveat | Solid current sourcing (pricing, ToS, DPA, privacy); correctly leaves long-term raw retention unresolved; correctly refuses admission | Provider testimony contract can be drafted as skeleton; rights/retention fields grounded | Yes — DR1 (endpoints), DR2 (raw retention) before M13 |
| RG2 | rg2-scope-rights-retention-model.md | Strong enough for M7 | Clean scope/rights/retention vocabularies with fail-closed defaults; six-way Kaizen rights model preserved | Draft first — this is the spine contract | DR2 for retention edge cases; provider-specific binding at M13 |
| RG3 | rg3-evidence-id-citation-model.md | Strong enough for M7 | Six ID layers properly separated; stability + status vocab; open choices explicitly parked | Draft second — everything else references evidence IDs | DR14 before M14/M15 finalization |
| RG4 | rg4-query-panel-model.md | Strong enough for M7 | Immutable versioning, run concept, no-nonsense checks; correctly separates panel from strategy | Query panel contract drafteable | DR12 (cadence) before M18 |
| RG5 | rg5-freshness-staleness-volatility.md | Strong enough for M7 | Vocabularies + age bands honestly labeled provisional; update-window handling; externally grounded | Freshness contract drafteable; bands must be labeled provisional in contract | DR12; RG6/RG7 family refinements |
| RG6 | rg6-geo-ai-citation-methodology.md | Usable but needs caveat | Excellent methodology rules and claim patterns; two soft spots (sentiment field, sample-summary storage ambiguity — Section 4 D-A/D-B) | AI observation contract drafteable after tightening those two | Yes — DR4, DR5 before any customer-facing GEO claim or validation pull |
| RG7 | rg7-marketplace-evidence-ceiling.md | Strong enough for M7 | Current Etsy/Fiverr terms checked; honest about what the Fiverr fetch didn't show; blocked-by-default posture correct | Marketplace ceiling contract drafteable | Yes — DR6, DR7, DR8 before any capture design |
| RG8 | rg8-claim-safety-report-language.md | Strong enough for M7 | Claim classes, matrix, forbidden list, checklist, statuses — the strongest gate in the set | Claim-safety contract drafteable; add a `predictive_claim` class (Section 10) | DR9 before M15 customer-facing language |
| RG9 | rg9-provider-cross-check-disagreement-model.md | Strong enough for M7 | Three-layer model, disagreement types, incomparability defaults, no-winner rules | Cross-Check contract drafteable; ledger persistence question stays open (D-C) | DR3 before M16 real-provider proof |
| RG10 | rg10-capturepackage-v0-1-inputs.md | Strong enough for M7 | Required fields, validation groups, invalid examples, approval hooks — directly contractable | CapturePackage contract drafteable | Provider-specific fields at M13 |
| RG11 | rg11-raw-archive-provider-drift.md | Strong enough for M7 (contract level) | Manifest fields, retention postures, drift statuses, parser rules — good, and honest that it's not implementation-ready | Raw archive/drift contract drafteable | Yes — DR2, DR13 before M11/M12 |
| RG12 | rg12-consumer-contract-inputs.md | Usable but needs caveat | Consumer categories, request/response/overlay shapes, promotion rule are solid; internal telemetry and consumer authn/authz are thin | Consumer + promotion contracts drafteable; owned-telemetry piece is placeholder-only | Yes — DR9, DR10, DR11; add authn/authz research (Section 8) |
| RG13 | rg13-hammer-matrix-inputs.md | Usable but needs caveat | H1–H18 cover the prompt's full category list; but misses four categories the roadmap/inherited doctrine already require (Section 11) | Enough for M8 to start; fix the gap before M8 activates | DR15 |

No gate is unsafe or inconsistent. None needs owner ruling *before drafting begins* — rulings are needed inside/after drafting, not before.

---

## 6. Errors, weak spots, and improvement opportunities

| Priority | File/Area | Problem | Why it matters | Suggested fix | Timing |
|---|---|---|---|---|---|
| important before M7 drafting | RG13 vs ROADMAP M8 / harvest V13/V9 | RG13 has no hammer categories for **append-only observation behavior**, **concurrency scenarios**, **audit-record-on-consequential-change (V9 audit-first)**, or **migration rollback/recovery** — all four are named in ROADMAP's M8 hammer category list and/or inherited hammer doctrine (V13 requires concurrency + rollback probes) | M8 will draft the matrix from RG13; a category missing from the input tends to go missing from the matrix | Add a short RG13 addendum (or a note in the M7 audit-response file) naming H19 append-only/no-silent-overwrite, H20 concurrency, H21 audit-record-required, H22 migration rollback/recovery | now (one small edit) |
| important before M7 drafting | Owner-ruling sprawl | ~40 owner-ruling candidates are scattered across 13 RG files with no consolidated view | M7 exit criteria require owner-ruling candidates to be "explicit"; scattered means forgotten, and forgotten rulings become silent assumptions in contracts | Create a single owner-ruling tracker (planning-inbox or decisions/ pending file) that lists every candidate with source gate and blocking milestone | now |
| important before M7 drafting | NC5 coverage/blind-spot reporting | The M5 planned-topic "surface coverage / blind spots" got no dedicated gate; NC5 is a planned day-one capability but appears only as passing mentions in RG4/RG5 checks; no M7 contract candidate covers it | Coverage/blind-spot output is a read-tool contract concern ("what does Observatory NOT know") — hard to retrofit into evidence packs, same argument as evidence IDs | Either fold explicit coverage/blind-spot output fields into the freshness or typed-read-tool contract, or add a DR item; record the choice | during M7, decide now |
| important before M7 drafting | NC3 intervention timeline join | The intervention-timeline join contract (read tools accept external intervention timeline, return aligned before/after windows; interventions never stored) is a planned capability with no RG coverage and no M7 contract candidate | Before/after alignment is the "this improved after that change" core promise; if it isn't in the overlay/read-tool contract now, someone will later store interventions to make it work — which is strategy storage | Fold intervention-timeline-as-ephemeral-input into the overlay contract (it is structurally identical to the customer overlay: external series, read-time join, no storage), or add DR item | during M7 |
| useful cleanup | research/README.md | Reading Order says no corpus exists; Last Review Notes carry a closed M5 open issue | Fresh sessions use this file as the required-reading index for M7; it actively misdirects | Rewrite Reading Order to point at the 13 RG files + backlog in M6 execution order; refresh review notes | now |
| useful cleanup | REPO_MAP.md | research/ folder status stale ("no research execution until M5/M6") | Minor confusion | Update status text | during M7 |
| useful cleanup | 00-project-overview.md / 01-harvest-register.md headers | "draft" status headers on documents REPO_MAP labels authority | Label mismatch invites an LLM to treat harvest dispositions as negotiable | Promote headers to authority (they are owner-walked) or downgrade REPO_MAP labels; recommend promote | during M7 |
| useful cleanup | ROADMAP.md M5→M6 gate mapping | Planned-M5 section's 12 topics don't map visibly to the 13 executed gates; two topics (provider personality, owned telemetry) folded silently and one (surface coverage) fell through | Future stewards may believe topics were dropped or, worse, believe they were covered | One-paragraph mapping note in the M6 closure note or M5 plan | during M7 |
| useful cleanup | RG6 language (D-A, D-B) | "mechanically derived" sentiment; ambiguous stored-vs-read sample summary | Copy-paste into contracts propagates the drift vector | Tighten during contract drafting; don't need to edit the RG itself if the contract is explicit | during M7 |
| later improvement | ROADMAP.md structure | Closed milestones duplicated in Planned section as stubs; M7 in two places | Duplication drifts | Collapse stubs after M7 closes | later |
| later improvement | RG8 | No explicit `predictive_claim` class though checklist mentions "predictive" | Predictive claims ("this will improve rank") are the most-requested and most-forbidden shape | Add class in claim-safety contract: default `forbidden_overclaim` / `consumer_owned_recommendation` | during M7 |
| deep-research backlog item | Consumer authn/authz | RG12 names "consumer authentication/authorization" as an owner-ruling candidate but no DR item exists | Blocks M14; without research it becomes an improvised implementation detail | Add DR16 | during M7 |
| deep-research backlog item | Provider credential/secret handling | No research topic covers API key storage/secret management posture before provider admission; M11 only says "local config without secrets" | Blocks M13 in practice | Add DR17 or fold into DR1 | during M7 |

The repo is solid. Top 5 improvements that make M7 safer/faster: (1) owner-ruling tracker, (2) RG13 hammer-category addendum, (3) research/README fix, (4) NC3/NC5 disposition decision, (5) contract template + contracts/README before the first contract.

---

## 7. M7 contract-readiness map

Recommended packaging. Dependencies flow downward.

**Package A — Spine (draft first):**
1. `contracts/README.md` + contract template (ROADMAP blocker — nothing drafts before this exists)
2. Scope / scope_class / rights / retention contract ← RG2. Everything else references it.
3. Evidence ID / citation contract ← RG3. Second, because every other contract cites evidence handles.

**Package B — Evidence behavior:**
4. Freshness / staleness / volatility contract ← RG5 (bands labeled provisional).
5. Claim-safety / claim-language matrix contract ← RG8 + RG6 claim patterns. **Merge the "negative evidence / absence rules contract" into this one** — absence rules are claim rules; a standalone absence contract would duplicate RG6/RG8 material. Add `predictive_claim` class here.

**Package C — Capture and raw support:**
6. Query panel contract ← RG4.
7. CapturePackage v0.1 contract ← RG10.
8. Raw archive / payload pointer / provider drift contract ← RG11. **Merge "raw archive/payload pointer" and "provider payload diff/drift" into one contract** — RG11 already treats them as one system; splitting invites inconsistency.

**Package D — Provider:**
9. Provider registry / provider testimony contract ← RG1 + RG9 + V7. Skeleton is drafteable now; provider-specific bindings wait for M13/DR1.
10. Provider Cross-Check & Disagreement Model contract ← RG9. **The "Provider Disagreement Ledger candidate contract" should be a section inside this contract, not a standalone contract** — a persisted ledger is a materialization-test + owner-ruling question (Section 4 D-C), and a standalone contract doc presumes the answer.

**Package E — Consumer and access:**
11. Consumer contract (request/response/promotion) ← RG12. Promotion / conclusion-handoff can be a section of this contract or a thin companion; either is fine, but don't let them contradict.
12. Overlay contract ← RG12 + DR10 shape. Draft as a thin contract covering customer first-party overlays **and intervention-timeline inputs (NC3)** as the same ephemeral-input mechanism. Internal owned-telemetry portion: **placeholder only** — DR11 hasn't run; a full owned-telemetry contract now would be built on guesses.
13. SearchClarity consumer-contract placeholder ← RG12. Placeholder means placeholder: named sections, DR9 blockers, no report language.
14. Typed API/MCP read-tool contract ← RG3/RG5/RG8/RG12 output-shape material. **Draft as a skeleton/requirements doc only** — the real contract is M14's job; a fully specified read API in M7 is unearned implementation shaping. Include NC5 coverage/blind-spot output fields here if that's the chosen disposition.

**Delay past M7 / route elsewhere:**
- Owned internal telemetry contract (full version) → after DR11 (M17 track).
- Anything provider-endpoint-specific → M13/DR1.
- Hammer definitions themselves → M8 (RG13 + addendum is the input, not the contract).
- Recapture cadence policy → DR12/M18.

Drafting order within M7: A → B → C → D → E. B before C because CapturePackage carries `claim_use_warning` and freshness fields; D before E because consumer output shapes reference disagreement output.

---

## 8. Deep-research backlog critique

DR1–DR15 are the right topics, correctly scoped, correctly blocking-mapped. Splits are justified (DR6/DR7 per-platform; DR4/DR5 methodology vs Google-specific limits).

**Missing:**
- **DR16 — Consumer authentication/authorization model.** RG12 flags it as owner-ruling candidate; nothing researches it. Blocks M14.
- **DR17 — Provider credential/secret handling posture.** Blocks M13 practically. Could fold into DR1 but is cross-provider.
- **NC3 intervention-timeline join methodology** — if not folded into the M7 overlay contract (Section 7 #12), it needs a DR item. Blocks M15's "this improved after that change" story.
- **NC5 coverage/blind-spot reporting** — same treatment: contract section or DR item, decided explicitly.
- (Optional) **Ahrefs/Semrush rights/cost admission research** — DR3 compares methodology but nothing researches their terms/cost. Not blocking (M16 allows fixtures); add when/if real multi-provider capture is wanted.

**Redundant:** none worth merging. DR4/DR5 overlap at the edges but block different milestones.

**Split/merge:** no changes needed to existing items.

**Blocker mapping:**
- Blocking M7 contracts: **none.** Every DR item is correctly downstream of contract planning.
- Blocking M13 provider admission: DR1, DR2, DR8 (if manual/extension capture is wanted), DR13, DR17(new).
- Blocking M15 SearchClarity proof: DR9, DR10, DR4/DR5 (for any GEO content), DR6/DR7 (for any marketplace content), DR14.
- Blocking implementation acceptance broadly: DR13, DR15, DR2.
- Safely deferred: DR3 (until M16 uses real providers), DR11 (until M17), DR12 (until M18).

**Direct answers:** Yes — the M6 docs are enough for M7, at contract-planning depth, which is what they claimed to be. Deeper research that still must happen later: everything provider-endpoint-specific (DR1/DR2), everything customer-facing (DR9/DR4/DR5/DR6/DR7), everything raw-archive-physical (DR13), plus the two new items above.

---

## 9. Provider/capture risk classification

| Provider/Capture Area | Current posture | Risk | Needed before use | Milestone |
|---|---|---|---|---|
| DataForSEO (SERP, Labs, keywords) | Plausible, not admitted; terms/pricing researched (RG1) | SERP-use restrictions (F8); duplicate-task cost trap (F9); raw retention unresolved (F6) | DR1, DR2, admission doc, recipe, ceilings, stop conditions, owner approval | M13 admission research needed |
| DataForSEO AI Optimization | Named canonical GEO source (owner ruling Q4), not admitted | AI-surface volatility; methodology immaturity | Above + DR4; RG6 methodology binding | M13 admission research needed |
| Ahrefs | Deferred; no research | Terms/cost unresearched | Own admission research + DR3 | deferred |
| Semrush | Deferred; no research | Same | Same | deferred |
| Google Search Console | Internal first-party candidate only (V17) | Scope-leak risk (customer GSC is overlay-only; owner GSC is internal-scope) | DR11 + internal-scope contract + hammers | M17 track; deeper review needed |
| Bing Webmaster Tools | Not researched | Same class as GSC | Same | deferred |
| Google AI Overview / AI Mode capture | Not cleared | Platform constraints; fan-out opacity; extreme volatility | DR5 | blocked by default |
| Etsy site pages / extension capture | Forbidden by default (ToS blocks crawl/scrape; extension prohibited) | ToS violation; short cache windows even via API | Express authorization or owner ruling; DR6, DR8 | forbidden unless owner ruling |
| Etsy API | Possible, not admitted; analytics/ML uses need written authorization | Overcollection; 6h/24h freshness rules; no durable retention cleared | DR6; per-purpose review; likely owner ruling | M13 admission research needed; deeper legal/platform review needed |
| Fiverr public pages | Not cleared (RG7 fetch didn't establish permission — which is not permission) | Unverified terms | DR7 full-terms review | deferred; deeper platform review needed |
| Manual/operator capture | Slim family kept (V16) but not contracted | Provenance-integrity; screenshot rights | DR8 + manual-capture contract | M13 admission research needed; owner ruling for marketplace use |
| Browser extension instrument | Candidate only, per-marketplace ToS review required (Q2) | Etsy already forbids it; others unreviewed | DR8; per-platform admission | blocked by default |
| Raw payload archives | Not admitted; manifest/drift model exists (RG11) | Retention overreach; rights ambiguity | DR2, DR13, owner ruling on retention | M7 contract-ready (contract only); implementation blocked |
| Provider drift handling | Model defined (RG11) | Silent parser corruption if unimplemented | M7 contract + M8 hammers | M7 contract-ready |

"Provider exists" ≠ "provider is admitted" is respected everywhere in the RG set. No RG pre-admits anything.

---

## 10. Claim-safety critique

RG8 (with RG5/RG6/RG7 feeding it) is strong enough to block every overclaim in the audit prompt's list: "rank X everywhere" (forbidden list), "absent from AI search" (forbidden + absence class), "AI trusts your site" (forbidden), "citation caused the answer" (forbidden + RG6 Rule 5), "ranks globally" (marketplace matrix row), "provider score is truth" (provider_metric_claim), "will increase traffic/sales/rank" (guaranteed-* forbidden entries + "this optimization will improve rank").

Missing rules to add during contracting:
1. **Explicit `predictive_claim` class.** The checklist mentions "predictive" but no class exists. Default: `forbidden_overclaim` or `consumer_owned_recommendation` — predictions are interpretation and belong to the consumer with its own disclaimers.
2. **Causality-adjacent comparative language.** "X improved after Y" is allowed as aligned before/after observation, but the matrix should carry an explicit "temporal adjacency is not causation" caveat pattern — the NC3 intervention-join output will need it on day one.
3. **Aggregate-sample inflation rule.** `domain_share_in_sample` and similar RG6 metrics need a forbidden pattern for quietly presenting sample share as market share.

Structure recommendation: **one M7 claim-safety contract (absorbing absence rules) plus an M8 hammer suite (H9/H10), plus DR9 as the consumer-facing language backlog item.** Do not split into multiple M7 contracts — the matrix is the unifying artifact and splitting it fragments the forbidden list.

---

## 11. Hammer-readiness critique

RG13 gives M8 a genuinely draftable matrix. H1–H18 cover every category in the audit prompt's checklist: scope isolation (H1), rights (H2), retention (H3), customer-private rejection (H4), no recommendation storage (H5), CapturePackage validation (H6), spend/duplicate prevention (H7), attribution/disagreement (H8), freshness/volatility (H9), AI/GEO overclaim (H10), marketplace restrictions (H11), raw hash/pointer integrity (H12), drift quarantine (H13), panel immutability (H14), evidence/citation integrity (H15), overlay no-storage (H16), LLM/agent access boundary (H17), hostile input (H18). The minimum-suite proposal and result vocabulary ("blocked_not_implemented is not pass") are exactly right.

**Missing hostile paths — the one real gap in M6:**

1. **Append-only violation hammers.** Boundary law and V3/V9 say observations are append-only history, never silently overwritten. H14 protects panel immutability only. Missing: hostile attempts to UPDATE/overwrite an admitted observation, backdate `captured_at`, or mutate raw-linked fields must fail.
2. **Concurrency hammers.** V13 inherited doctrine: "concurrency scenarios required." Nothing in H1–H18 tests concurrent capture admission, concurrent purge-vs-read, or duplicate-fingerprint races (the duplicate-task check in H7 is single-threaded as written).
3. **Audit-first hammers.** V9/N4: no required audit record → no persisted consequential change. No hammer proves a consequential write without its audit/event record is rejected atomically.
4. **Migration rollback/recovery hammers.** ROADMAP's own M8 category list includes "schema migration rollback/recovery expectations"; RG13 never mentions it.

Additionally worth naming for M8 (lower priority): retention-purge-under-concurrent-citation (what happens to an evidence pack mid-read when purge fires), and a no-read-event probe (V9 says no read events — confirm read paths don't write).

Fix: a one-page RG13 addendum or a section in the M7 audit-response file listing H19–H22. Cheap now, expensive if M8 drafts from an incomplete input.

---

## 12. Required owner rulings

Grouped and deduplicated from all 13 gates. None blocks the *start* of M7 drafting; groups A–B should be resolved during M7 so contracts don't ship with holes.

**A — Needed during M7 (contract-shape rulings):**
1. Provider Cross-Check: standalone contract, and is a *persisted* Disagreement Ledger permitted or compute-on-read only? (RG9; Section 4 D-C)
2. Citation handles: global vs artifact-local; report-safe references separate or derived? (RG3/DR14 — can be a contract decision if owner delegates)
3. Disposition of NC5 (coverage/blind-spot) and NC3 (intervention timeline): contract sections now vs DR items? (this audit)
4. RG6 sentiment field: provider-attributed-only, or is any mechanical derivation permitted? (Section 4 D-A)
5. Minimum M7 contract set for closure (which of the 14 candidates in Section 7 are required vs optional for M7 exit).

**B — Needed before M8 closes:**
6. Hammer acceptance criteria and acceptable mock/stub level pre-implementation (RG13).
7. Whether any freshness class auto-blocks customer-facing use (RG5).

**C — Needed before M13 (park now, do not resolve in M7):**
8. Fund/use DataForSEO account; validation budget release; endpoint list; raw retention posture (RG1/DR1/DR2).
9. Etsy API pursuit and/or express-authorization outreach; extension instrument fate; Fiverr posture (RG7/DR6/DR7/DR8).
10. Manual public observation capture as Observatory evidence (RG10/DR8).
11. Market_watch panel execution before validation spend (RG4).

**D — Needed before M15/M17:**
12. SearchClarity report-safe language and evidence-handle exposure (RG8/DR9).
13. Customer overlay acceptance into read tools; internal telemetry admission (RG12/DR10/DR11).

Recommendation: create the tracker file now and log all of these with source-gate references; resolve group A as M7's second move.

---

## 13. Recommended M7 first moves

1. Fix `research/README.md` reading order + review notes (5-minute maintenance; it is the M7 required-reading index).
2. Create `planning-inbox/m7-audit-response-2026-07-07.md` recording this audit's findings and their assigned fixes (mirrors the M1 audit-response pattern that already worked).
3. Create the owner-ruling tracker; log Section 12; put group A in front of the owner.
4. Add the RG13 H19–H22 addendum (append-only, concurrency, audit-first, migration rollback).
5. Create `contracts/` + `contracts/README.md` + contract template (ROADMAP blocker for all drafting).
6. Draft the scope/rights/retention contract (RG2).
7. Draft the evidence ID/citation contract (RG3).
8. Draft freshness/volatility, then the merged claim-safety+absence contract (RG5, RG8/RG6) with the `predictive_claim` class.
9. Draft query panel, CapturePackage, and merged raw-archive+drift contracts (RG4, RG10, RG11).
10. Draft provider testimony + Cross-Check (ledger as an open-question section), then consumer + promotion + overlay (with NC3 folded in) + SearchClarity placeholder + typed-read-tool skeleton (with NC5 fields if so ruled).
11. Record the M5-topics→13-gates mapping note.
12. Close M7 per the closure convention: update summary table, ACTIVE_CONTEXT, NEXT_SESSION_HANDOFF, commit.

---

## 14. Concrete repo improvement suggestions

| Suggestion | Verdict |
|---|---|
| Fix `research/README.md` reading order + last-review notes | recommended now |
| Create M7 audit-response file in planning-inbox | recommended now |
| Create owner-ruling tracker (single file, all candidates, source refs) | recommended now |
| RG13 addendum: H19 append-only, H20 concurrency, H21 audit-first, H22 migration rollback | recommended now |
| Create `contracts/README.md` + contract template | recommended now (M7 blocker) |
| Update REPO_MAP research-folder status text | recommended during M7 |
| Resolve draft-vs-authority headers on 00/01 docs | recommended during M7 |
| Add M5-topics→executed-gates mapping note | recommended during M7 |
| Add DR16 (consumer authn/authz) and DR17 (provider secrets) to backlog | recommended during M7 |
| Merge absence-rules contract into claim-safety contract; merge raw-pointer + drift contracts; fold Disagreement Ledger into Cross-Check | recommended during M7 (drafting decisions) |
| Collapse duplicated closed-milestone stubs in ROADMAP Planned section | recommended later (after M7 closure) |
| Add stronger overlay wording ("read tools must not log/cache/persist overlay inputs") to overlay contract | recommended during M7 (contract text, not boundary edit) |
| Split RG6 into separate mention/citation methodology docs | do not do — the gate is coherent as one doc; splitting research adds ceremony |
| Promote the Tier 0–3 model into `02-boundaries.md` | do not do — M4 D5 already ruled correctly; keep it a contract-level tool |
| Standalone "negative evidence" contract | do not do — merge into claim-safety |

No file edits performed; this audit was read-only per instructions.

---

## 15. Stop / do-not-build warnings

- Do not create schema, migrations, or "just a quick table" for anything in the RG field lists. Every field list in RG2–RG12 is contract input, and each doc says so — believe them.
- Do not let the typed read-tool contract become an API implementation spec in M7. Skeleton only; M14 owns the real contract.
- Do not draft a full owned-telemetry contract before DR11. Placeholder with named blockers only.
- Do not persist a Provider Disagreement Ledger, `ai_visibility_sample_summary`, or any "cache" of comparison outputs without passing the V6 materialization test and an owner ruling. These are the three most likely fake-mustache entry points in the current corpus.
- Do not let "mechanically derived" sentiment into any contract without an explicit owner ruling. Sentiment is interpretation wearing a lab coat.
- Do not touch Etsy with anything automated. RG7's findings are unambiguous.
- Do not treat RG age bands, volatility defaults, or freshness thresholds as product promises — label them provisional in the contracts, exactly as RG5 does.
- Do not spend the $50. It is planning evidence, not a fuse waiting for a match.

---

## 16. Final readiness verdict

**Is Observatory ready to proceed with M7 contract planning?**

**Yes, with caveats.**

Caveats:
1. Before drafting the first contract: fix `research/README.md`, create the contract template + `contracts/README.md`, create the owner-ruling tracker, and add the RG13 H19–H22 addendum. Half a session of work.
2. During M7: resolve owner-ruling group A (Section 12); tighten RG6's two soft spots in contract language; decide NC3/NC5 disposition explicitly; draft the owned-telemetry and SearchClarity contracts as placeholders only.
3. Nothing in M6 blocks M7. Several things in M6 correctly block M13/M15/implementation, and they must stay blocking.

The telescope's paperwork is in order. The astronomer may start writing contracts. Nobody gets to buy a lens yet.
