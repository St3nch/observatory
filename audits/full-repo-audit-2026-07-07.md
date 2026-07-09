# Observatory Full Repository Audit — M7 / Post-M6 Closure

Auditor: Claude (Observatory Project Steward role)
Date: 2026-07-07
Authority: audit report; planning input only; nothing here is doctrine until promoted.

---

## 1. Executive verdict

The repo is in good shape and the boundary law is intact everywhere I looked — including the deliberately dangerous planning docs, which are all correctly labeled non-authority. The problems are hygiene problems, and they cluster in exactly the places a repo accumulates them: tracker files whose status columns froze several milestones ago, "open issues" notes that were resolved but never updated, one brand-new folder (`audits/`) that exists outside every index and rule the repo wrote for itself, and one historical file (`planning-inbox/CLAUDE_START_HERE.md`) that carries a stale read order with no deprecation header inside the file itself.

Nothing violates doctrine. Nothing stores strategy, customers, or truth-scores. No fake mustaches found — and I went looking in the dangerous docs specifically.

**Full repo audit verdict: Repo is clean enough after small cleanup.** The only item that *hard-blocks* contract drafting is the contract template + `contracts/README.md`, which the roadmap itself names as an M7 blocker and which is M7's own first deliverable anyway. Everything else is cleanup that should happen in the first M7 session so future agents don't inherit the confusion.

---

## 2. Audit scope actually performed

**Inspected in full:** `README.md`, `LLM_START_HERE.md`, `ACTIVE_CONTEXT.md`, `ROADMAP.md`, `ROADMAP_RULES.md`, `REPO_MAP.md`, `00-project-overview.md`, `01-harvest-register.md`, `02-boundaries.md`, `NEXT_SESSION_HANDOFF.md`, `FOLDER_README_TEMPLATE.md`, `.gitignore`, `.gitattributes`; all of `research/` (README, m5 plan, RG1–RG13, deep-research backlog); all of `decisions/` (README, template, M2 decision); `archive/README.md`; `audits/m7-audit-report-2026-07-07.md`; `planning-inbox/README.md`, `audit-response-2026-07-07.md`, `repo-first-research-triage.md`, `m4-boundary-reconciliation.md`.

**Inspected by header/opening sections (labels, status, posture verified; full body skimmed on the prior pass or spot-checked):** `planning-inbox/strategy-layer-dangerous-design.md`, `deep-research-danger-agenda.md`, `steward-context-dump.md`, `observatory-working-notes.md`, `CLAUDE_START_HERE.md`, `knowledgebase-reconciliation.md`.

**Could NOT inspect:** Git tracked/untracked status, commit state, local-vs-origin divergence. My filesystem tools read files on your machine but cannot run `git`. I can confirm `.git/` exists and that `.gitignore`/`.gitattributes` are sane; I cannot confirm whether `audits/m7-audit-report-2026-07-07.md` is committed, staged, or untracked, nor whether AUD-002 ("push before multi-tool handoff") is still true. Verify with `git status` yourself.

---

## 3. Full repo tree / folder audit

Tree at audit time:

```text
C:\dev\observatory\
  .git/  .gitattributes  .gitignore
  00-project-overview.md  01-harvest-register.md  02-boundaries.md
  ACTIVE_CONTEXT.md  FOLDER_README_TEMPLATE.md  LLM_START_HERE.md
  NEXT_SESSION_HANDOFF.md  README.md  REPO_MAP.md  ROADMAP.md  ROADMAP_RULES.md
  archive/            README.md
  audits/             m7-audit-report-2026-07-07.md          <-- NO README, NOT IN REPO_MAP
  decisions/          README.md, decision-record-template.md, 2026-07-07-m2-folder-subset.md
  planning-inbox/     README.md + 9 docs (all indexed)
  research/           README.md + m5 plan + RG1–RG13 + deep-research-backlog (all indexed)
```

| Folder | Exists? | Indexed in REPO_MAP? | README? | Status | Issues |
|---|---|---|---|---|---|
| `archive/` | yes | yes | yes | clean | Stale open-issue note (CLAUDE_START_HERE move "after M3" — M3 closed, move never happened) |
| `audits/` | yes | **no** | **no** | **unindexed, un-governed** | Not in REPO_MAP Current Folders or Planned Folder Layout; no README; not referenced by any root doc; violates the repo's own "no random folders / folder README rule" — see ISS-01/02 |
| `decisions/` | yes | yes | yes | mostly clean | README open-issue stale; M2 decision follow-up table stale (ISS-07/08) |
| `planning-inbox/` | yes | yes | yes | clean index | All 9 docs indexed with correct labels; CLAUDE_START_HERE lacks an in-file deprecation header (ISS-06); tracker staleness (ISS-05) |
| `research/` | yes | yes (stale status text) | yes | complete but stale header text | Reading Order + review notes stale (ISS-03); REPO_MAP status text stale (ISS-04) |
| `contracts/` | correctly absent | listed as deferred-until-M7 | n/a | correct | M7 is active, so creating it is now earned — that's a first move, not an error |
| `hammers/` | correctly absent | listed as deferred-until-M8 | n/a | correct | none |

Nothing in any folder looks like implementation, schema, customer data, provider payloads, secrets, or strategy storage. `.gitignore` proactively ignores `captures/`, `raw-captures/`, `.env*`, `secrets/` — good hygiene consistent with boundary law.

**On `audits/` specifically:** the folder is the right idea (audit reports are project evidence and were previously being lost — the earlier Claude audit that produced the AUD-001..033 backlog exists only as "uploaded project knowledge," referenced by `audit-response-2026-07-07.md` as `observatory-repo-audit-2026-07-07.md`, a file that is **not in the repo at all**). But as created, `audits/` breaks the repo's own rules: REPO_MAP says "do not create random folders," ROADMAP_RULES says required-reading folders need READMEs, and the M2 decision explicitly enumerated the earned folder set. The fix is cheap: an `audits/README.md` that labels audit reports as *planning input / advisory, never authority*, a REPO_MAP row, and ideally a small retroactive decision note or a line in the M7 audit-response file recording that the owner earned the folder. Audit reports should live in `audits/` (not planning-inbox) — they're a distinct artifact class with a distinct trust posture, and the folder makes the "audit the previous audit" workflow possible.

**Naming-collision warning:** the repo now contains two different 2026-07-07 Claude audits: the M1-era repo audit (external, responded to by `planning-inbox/audit-response-2026-07-07.md`) and `audits/m7-audit-report-2026-07-07.md`. A future agent reading the audit-response file could reasonably assume it responds to the file in `audits/`. It does not. One clarifying sentence in each file's header fixes this permanently (ISS-09).

---

## 4. Milestone and status consistency audit

Expected posture (M6 closed / M7 active / M8 next) is consistent across `README.md`, `LLM_START_HERE.md`, `ACTIVE_CONTEXT.md`, `ROADMAP.md` (summary table + Active section), and `NEXT_SESSION_HANDOFF.md`. The closure convention was followed for M6.

Stale-reference sweep against the prompt's checklist:

| Pattern | Found? | Where |
|---|---|---|
| "M5 active" / "M6 active" | no | — |
| "research corpus does not exist" | **yes** | `research/README.md` Reading Order: "No full research corpus exists yet. When M5 activates, read…" |
| "M5 must create a research gate template" | **yes** | `research/README.md` Last Review Notes open issue |
| "no research execution yet" | **yes (variant)** | `REPO_MAP.md` research row: "no research execution until M5/M6" |
| contracts/ deferred while M7 active | no contradiction — "deferred until M7" reads correctly now that M7 is active | REPO_MAP, decisions |
| hammers/schema/provider/API/proof active early | no | — |
| Other stale statuses | **yes** | `decisions/README.md` open issue ("first decision record still needed" — it exists, indexed two sections up); M2 decision follow-up rows "pending" for work done in M2/M3; `planning-inbox/audit-response-2026-07-07.md` status column frozen around M2-era (see §5); `archive/README.md` open issue re: CLAUDE_START_HERE move |

Pattern worth naming: the repo's *authority* files get updated at closure (the convention works), but *tracker/review-notes* fields inside folder READMEs and decision records do not. ISS-14 proposes adding "refresh tracker statuses and folder-README review notes touched by this milestone" to the closure convention in `ROADMAP_RULES.md`, which prevents this whole class permanently.

---

## 5. Authority and index consistency audit

- **Authority labels:** root docs all carry status/authority headers. Two mismatches: `00-project-overview.md` says "Status: draft" and `01-harvest-register.md` says "Status: draft 1" while REPO_MAP labels both `authority`. Given the harvest dispositions are owner-walked and every RG treats both as binding, promote the headers (ISS-10).
- **Dangerous docs:** `strategy-layer-dangerous-design.md`, `deep-research-danger-agenda.md`, `steward-context-dump.md` all carry "Authority: none" in-file *and* in the planning-inbox index, with explicit subordination to `02-boundaries.md`. Correct.
- **In-file vs index labeling gap:** `planning-inbox/CLAUDE_START_HERE.md` has **no status header at all**. The index labels it historical, but the file itself opens with an authoritative-sounding read order (which is stale: no LLM_START_HERE, no ACTIVE_CONTEXT, no boundaries doc). A fresh agent opening the file directly gets misdirected. Either add a "Status: historical / superseded by LLM_START_HERE.md / Authority: none" header, or execute the long-planned move to `archive/` (ISS-06). Archiving is cleaner and closes the archive README's open issue simultaneously.
- **Index completeness:** planning-inbox README indexes all 9 docs; research README indexes all 16 files; decisions README indexes both files; archive README correctly shows "none yet." The only unindexed material in the entire repo is the `audits/` folder and its one file (ISS-01/02).
- **Dangling reference:** `audit-response-2026-07-07.md` names its source as `observatory-repo-audit-2026-07-07.md` — not present anywhere in the repo. If that original audit still exists as an upload/export, `audits/` is now the right home for it; if it's gone, the audit-response header should say the source is external and unrecoverable (ISS-09).
- **Audit-response tracker staleness (the biggest tracker problem):** the AUD table's status column stopped being maintained around M2. Verifiably complete items still marked open/assigned: AUD-013 (M3 delivered the three classified docs — "assigned"), AUD-014–018 (M4 applied all five boundary hardenings per the M4 reconciliation note — "assigned"), AUD-019 (OBR-01 named on M13 + RG1 exists — "assigned"), AUD-020 (RG9 exists — "assigned"), AUD-021/022 (promotion contract + SearchClarity placeholder now in the M7 contract list — "open"). Meanwhile nearly every roadmap milestone lists this file as required reading, so its staleness compounds. Refresh the status column early in M7 (ISS-05). AUD-002 (push to origin) I cannot verify — check git yourself.

---

## 6. Previous audit report assessment

| Audit file | Actual scope | Useful findings | Missed areas | Preserve? | Next action |
|---|---|---|---|---|---|
| `audits/m7-audit-report-2026-07-07.md` | M6-research-set + M7-readiness audit, per the prompt it was given. Read all root authority docs, research/README, all 13 RGs, backlog, M5 plan, planning-inbox index, M4 note. Explicitly **not** a full repo audit. | RG-by-RG verdicts; RG13 hammer-category gap (append-only, concurrency, audit-first, migration rollback); RG6 soft spots (mechanically-derived sentiment; sample-summary stored-vs-read ambiguity); Disagreement Ledger materialization-test question; NC3/NC5 coverage gaps; owner-ruling sprawl + grouped consolidation; M5-topics→13-gates mapping gap; research/README staleness; contract packaging/merge recommendations; DR16/DR17 candidates | Everything folder-level outside research/: `audits/` un-governed (folder didn't exist when the audit ran — it was created to hold this very report); audit-response tracker staleness; decisions follow-up staleness; decisions/archive README open-issue staleness; CLAUDE_START_HERE missing header; dangling `observatory-repo-audit-2026-07-07.md` reference; audit-file naming collision; git-state limits not stated | **Yes** — preserve in `audits/` with a README labeling it planning input | Add `audits/README.md` indexing it; convert its findings + this audit's findings into one `planning-inbox/m7-audit-response-*.md` tracker (the AUD-pattern worked; reuse it) |

Findings that should become tracked issues: all of its "recommended now / during M7" items — they map into §9 below (ISS-03, 11, 12, 13, plus its contract-sequencing guidance).

Wrong or overstated findings: one refinement. It said surface-coverage/blind-spot reporting (NC5) "folded into nothing." Slightly overstated — RG4 and RG5 both name coverage gaps/blind spots in their read-tool output requirement lists. Accurate version: NC5 has *no owning gate and no owning M7 contract candidate*, only passing mentions in two RGs' output lists. The recommendation (assign it an explicit owner: read-tool contract section or DR item) stands unchanged. Everything else re-verified accurate on this pass, including the RG13 gap and both RG6 soft spots.

---

## 7. M6 research set verification

All 14 expected files exist (RG1–RG13 + `deep-research-backlog.md`), plus `m5-research-gate-plan.md`, all indexed in `research/README.md`. Every RG carries "research output / source-grounded research input; not doctrine by itself; not schema approval" (RG13 correctly varies to "not test implementation"; backlog says "planning support only"). The m5 plan is correctly described as plan-not-execution in both its own header and the index. Every RG has non-goals, owner-ruling candidates, blockers-carried-forward, and feeds-milestones sections. None authorizes forbidden work — spot-verified against provider admission, pulls, schema, raw retention, marketplace/extension capture, customer data, and strategy storage. All feed M7/M8/M13/M14/M15 explicitly.

Residual quality caveats (carried from the prior audit, re-verified): RG13 missing four hammer categories the roadmap/inherited doctrine require; RG6's two drift-prone phrases; RG9's ledger persistence question. Details and fixes in §9.

The one stale element is the `research/README.md` framing text, not the research itself.

---

## 8. Doctrine and boundary consistency audit

Checked the full corpus — including, on this pass, the dangerous planning docs — against the required doctrine list. Result: **intact everywhere.**

- Observations-not-conclusions, no strategy/recommendation storage: enforced in boundaries, roadmap, every RG; the strategy-layer doc frames itself as process-not-storage and cites amended V21; RG10's invalid examples and RG13 H5 actively attack renamed violations.
- Customer database / records / first-party analytics: excluded in boundaries, RG2, RG7, RG12; overlays read-time only with `no_storage_overlay_only` retention class and H16 hammers.
- Provider testimony / disagreement preserved / no averaging: boundaries, RG8, RG9, H8. No provider-truth-score, winner logic, or blended metric anywhere.
- Rights/retention fail closed: RG2 vocabularies default closed; RG10 validation groups fail closed; H2/H3.
- No direct SQL/credentials; typed API/MCP only: boundaries, LLM_START_HERE, K9, H17.
- Hammers hard gate: boundaries, V13, RG13, roadmap M8.
- Killed concepts: V19/V20/V21/V24 + N3 stay killed; boundaries' Killed Concepts section; no resurrection found under any name.

Fake-mustache scan (strategy cache, candidate recommendation store, opportunity score table, AI visibility authority score, provider truth score, intelligence synthesis table, customer report store, workflow state table, conclusion scratch table, agent action queue): **none present as proposals.** All appear only inside forbidden-lists and hammer targets. The three *watch items* (not violations) remain: RG6 "mechanically derived" sentiment, RG6 `ai_visibility_sample_summary` stored-vs-read ambiguity, RG9/roadmap "Provider Disagreement Ledger candidate contract" presuming persistence. All three must be resolved in contract language via the V6 materialization test and, for sentiment, provider-attribution-only or owner ruling.

One nuance worth preserving visibly (already handled): the triage note's §6 correctly documents that Kaizen Result 506's parking-lot exclusions vs. the standalone clarified rule (customer records out; customer-scoped *public observations* allowed under controls) is a resolved distinction, not a contradiction. `02-boundaries.md` reflects the resolution. No action needed.

---

## 9. Complete issue list

| Issue ID | Severity | File/Area | Problem | Why it matters | Suggested fix | Timing |
|---|---|---|---|---|---|---|
| ISS-01 | important before M7 contracts | `audits/` | Folder exists with no README, violating the repo's own folder-README rule | The repo's core defense is self-explanation; an un-governed folder is exactly the "random folder" REPO_MAP forbids, and audit reports without a trust label risk being read as authority | Create `audits/README.md` (use FOLDER_README_TEMPLATE): audits are planning input/advisory, never authority; index the M7 report | now |
| ISS-02 | important before M7 contracts | `REPO_MAP.md` | `audits/` absent from Current Folders table | Fresh agents navigating by REPO_MAP won't find the audit corpus; map-vs-reality mismatch is the exact failure REPO_MAP exists to prevent | Add row; optionally note the folder was owner-created post-M6 | now |
| ISS-03 | important before M7 contracts | `research/README.md` | Reading Order says no research corpus exists / "when M5 activates"; Last Review open issue cites a closed M5 task | This file is M7 required reading and the index to everything M7 drafts from; it actively misdirects | Rewrite Reading Order to the 13 RGs + backlog in M6 execution order; refresh review notes | now |
| ISS-04 | useful cleanup | `REPO_MAP.md` research row | Status text: "no research execution until M5/M6" | Minor confusion | Update to "M6 research corpus complete; feeds M7" | during M7 |
| ISS-05 | important during M7 | `planning-inbox/audit-response-2026-07-07.md` | Status column frozen ~M2: AUD-013–020 verifiably done but marked assigned; AUD-021/022 addressed in roadmap but marked open | Nearly every milestone lists this file as required reading; its own header rule forbids letting findings rot; stale trackers train agents to ignore trackers | Refresh every status with a dated pass note; close what M3/M4/M5/M6 delivered | during M7 (early) |
| ISS-06 | useful cleanup | `planning-inbox/CLAUDE_START_HERE.md` | No in-file status header; contains stale read order; archive move planned "after M3" never happened | A fresh agent opening it directly gets a wrong read path with no warning | Move to `archive/` with a one-line supersession header (also closes archive README's open issue), or add "Status: historical / Authority: none / superseded by LLM_START_HERE.md" in place | during M7 |
| ISS-07 | useful cleanup | `decisions/README.md` | Open issue says the M2 decision record is "still needed" — it exists and is indexed in the same file | Self-contradicting index erodes trust in review notes | Refresh Last Review Notes | during M7 |
| ISS-08 | useful cleanup | `decisions/2026-07-07-m2-folder-subset.md` | Follow-up rows "pending" for work completed (REPO_MAP update, M3 docs) | Decision records are durable authority-support artifacts; stale follow-ups misreport project state | Update follow-up statuses; leave contracts/(M7)/hammers/(M8) rows accurate | during M7 |
| ISS-09 | useful cleanup | `audit-response-2026-07-07.md` + `audits/m7-audit-report-2026-07-07.md` | Two different 2026-07-07 audits; audit-response's named source file (`observatory-repo-audit-2026-07-07.md`) is not in the repo | Future agents will link the response to the wrong audit; the original audit is unpreserved evidence | One header sentence in each file disambiguating; if the original audit export exists, place it in `audits/`; if not, note source is external | during M7 |
| ISS-10 | useful cleanup | `00-project-overview.md`, `01-harvest-register.md` | Headers say draft while REPO_MAP labels both authority | Label mismatch invites treating owner-walked dispositions as negotiable | Promote headers to authority | during M7 |
| ISS-11 | important before M7 contracts | RG13 vs ROADMAP M8 / V13 / V9 | No hammer categories for append-only behavior, concurrency, audit-record-on-write, migration rollback/recovery — all required by roadmap M8 list and inherited doctrine | M8 drafts from RG13; missing input categories become missing tests | Short RG13 addendum or M7 audit-response note naming H19–H22 | now |
| ISS-12 | important before M7 contracts | Owner-ruling sprawl (13 RG files) | ~40 owner-ruling candidates, no consolidated tracker | M7 exit criteria require candidates explicit; scattered rulings become silent contract assumptions | Create tracker file; log §11 below | now |
| ISS-13 | important during M7 | NC3 / NC5 (harvest register vs M7 contract list) | Intervention-timeline join (NC3) has no gate and no contract candidate; coverage/blind-spot (NC5) has read-tool mentions in RG4/RG5 but no owning gate or contract | Both are day-one read-contract concerns, brutal to retrofit; NC3 unowned invites storing interventions later (strategy storage) | Fold NC3 into the overlay contract as ephemeral-input twin; give NC5 an explicit home in the read-tool contract skeleton or a DR item; record the choice | during M7, decide early |
| ISS-14 | useful cleanup | `ROADMAP_RULES.md` closure convention | Convention updates authority files but not tracker statuses/folder-README review notes — root cause of ISS-05/07/08 and the research/README staleness | Prevents this entire recurring class | Add closure step: "refresh tracker statuses and Last Review Notes in folders touched by this milestone" | during M7 |
| ISS-15 | later cleanup | `ROADMAP.md` structure | Closed M4/M5/M6 duplicated as stubs in Planned section; M7 in two places | Duplication drifts | Collapse stubs after M7 closes | later |
| ISS-16 | useful cleanup | ROADMAP M5 section vs executed gates | 12 planned topics vs 13 executed gates; two folded silently, NC5 fell through | Future stewards may think topics were dropped — or worse, covered | One-paragraph mapping note in M6 closure note or M5 plan | during M7 |
| ISS-17 | important during M7 (contract language) | RG6 | "Mechanically derived" sentiment; `ai_visibility_sample_summary` ambiguous stored-vs-read | Both are the likeliest interpretation-storage drift vectors in the corpus | Contract: sentiment provider-attributed-only absent owner ruling; sample summary read-time-only unless V6 materialization test + owner sign-off | during M7 |
| ISS-18 | owner ruling needed | RG9 / ROADMAP contract list | "Provider Disagreement Ledger candidate contract" presumes a persisted ledger | A persisted disagreement store is a derived-record question requiring the materialization test | Fold ledger into the Cross-Check contract as an open-question section; owner rules on persistence | during M7 |
| ISS-19 | deep research backlog item | `deep-research-backlog.md` | Missing DR16 consumer authn/authz, DR17 provider credential/secret handling | Block M14 and M13 respectively; currently nobody owns them | Add both | during M7 |
| ISS-20 | do not fix / acceptable as-is | Prior audit "folded into nothing" claim re NC5 | Slightly overstated (RG4/RG5 mention blind spots in output lists) | Recorded here for honesty; recommendation unchanged | Corrected in §6 | — |
| ISS-21 | do not fix / acceptable as-is (verify manually) | Git state / AUD-002 | Cannot verify tracked/untracked/push state with available tools | Multi-tool workflow depends on origin being current | Run `git status` / push before next cross-tool handoff | now (manual) |
| ISS-22 | useful cleanup | RG8 / claim-safety contract | No explicit `predictive_claim` class though the checklist names "predictive" | Predictions are the most-requested forbidden claim shape | Add class in the claim-safety contract, default forbidden/consumer-owned | during M7 |

**Blocks M7 contract drafting:** only the contract template + `contracts/README.md` (roadmap's own named blocker — an M7 deliverable, not damage). **Should precede the first contract as a half-session cleanup:** ISS-01, 02, 03, 11, 12. **Everything else:** during-M7 or later.

---

## 10. Improvement recommendations

| Suggestion | Verdict |
|---|---|
| `audits/README.md` + REPO_MAP row + "audits are planning input, never authority" label | recommended now |
| Owner-ruling tracker file (single file, all candidates, source refs, blocking milestone) | recommended now |
| New `planning-inbox/m7-audit-response-2026-07-XX.md` consolidating both audits' findings in the proven AUD-table pattern | recommended now |
| RG13 addendum (H19 append-only, H20 concurrency, H21 audit-first, H22 migration rollback) | recommended now |
| `contracts/` + README + contract template | recommended now (M7 blocker) |
| Refresh audit-response AUD statuses; refresh decisions/archive/research review notes | recommended during M7 |
| Archive or header-fix CLAUDE_START_HERE | recommended during M7 |
| Closure-convention addition: refresh trackers + Last Review Notes at every closure (ISS-14) | recommended during M7 |
| Add DR16/DR17; M5→gates mapping note; `predictive_claim` class; NC3/NC5 disposition | recommended during M7 |
| Audit workflow convention (one line in `audits/README.md`: audits are read → responded to via an audit-response tracker → findings routed to milestones — never silently absorbed) | recommended during M7 |
| Collapse ROADMAP closed-milestone stubs | recommended later |
| Rename either 2026-07-07 audit artifact | do not do — header disambiguation (ISS-09) suffices; renames churn history |
| Move audit reports into planning-inbox instead of audits/ | do not do — distinct artifact class, distinct trust posture; folder is right, governance was missing |
| Promote Tier 0–3 model into boundaries; standalone negative-evidence contract; split RG6 | do not do (unchanged from prior audit; M4 D5 already ruled on the Tier model) |

---

## 11. Owner-ruling consolidation

Deduplicated across all 13 RGs, boundaries, roadmap, and both audits:

**Needed before M7 contracts (shape rulings):** none strictly — drafting can start. **Needed during M7:**
1. Provider Cross-Check: standalone contract? Persisted Disagreement Ledger, or compute-on-read only? (RG9, ISS-18)
2. RG6 sentiment: provider-attributed-only, or any mechanical derivation? (ISS-17)
3. `ai_visibility_sample_summary`: read-time output only, or stored under materialization test? (ISS-17)
4. Citation handles global vs artifact-local; report-safe references separate or derived? (RG3/DR14 — delegable to contract decision)
5. NC3 and NC5 disposition: contract sections vs DR items (ISS-13)
6. Minimum M7 contract set required for closure (which of the ~14 candidates are mandatory)
7. Retroactive blessing of `audits/` as an earned folder (cheap decision-record or audit-response line)

**Needed before M8 hammers:** hammer acceptance criteria + acceptable mock/stub level pre-implementation (RG13); whether any freshness class auto-blocks customer-facing use (RG5).

**Needed before M13 provider admission:** fund/use DataForSEO account; validation-budget release + recipe/ceilings/endpoints; long-term raw payload retention posture (RG1/DR1/DR2); Etsy API pursuit / express-authorization outreach; browser-extension instrument fate; Fiverr posture (RG7/DR6/DR7/DR8); manual public-observation capture as Observatory evidence (RG10/DR8); market_watch panel execution before validation spend (RG4); capture-and-purge exceptions for unclear rights (RG2).

**Needed before M14 API/MCP:** consumer authentication/authorization model (RG12/DR16-new); raw payload pointer exposure outside internal tools (RG3); evidence withdrawal/deprecation behavior finalization (RG3/DR14).

**Needed before M15 SearchClarity proof:** report-safe language + evidence-handle exposure to customers (RG8/DR9); marketplace evidence in customer reports (RG7/RG8); report-safe AI visibility metrics + sampling thresholds (RG6/DR4); provider disagreement in customer reports (RG9).

**Needed before M17 overlay/internal telemetry:** customer overlay acceptance rules into read tools (DR10); internal first-party telemetry admission + scope handling (DR11); overlay freshness metadata in customer-facing conclusions (RG5).

**Defer:** cross-scope aggregate exceptions; TacticCapture family; recurring capture/schedulers; new scope_class additions; Ahrefs/Semrush anything.

There is no tracker for any of this. Create one now (ISS-12).

---

## 12. Deep-research backlog additions

| Topic | Add/defer? | Why | Blocks milestone? |
|---|---|---|---|
| Consumer auth/authz model (DR16) | add during M7 | RG12 flags it as owner-ruling candidate; nothing researches it | M14 |
| Provider credential/secret handling (DR17) | add during M7 | Nothing covers key storage/secret posture; M11 only says "config without secrets" | M13 (practically) |
| Intervention timeline join methodology (NC3) | add during M7 **only if** not folded into the overlay contract — folding is the better move (same ephemeral-input mechanism) | Day-one "this improved after that change" promise; unowned = future strategy-storage temptation | M15 |
| Surface coverage / blind-spot reporting (NC5) | add during M7 only if not given a read-tool-contract home | Named day-one capability with no owner | M14 |
| Ahrefs/Semrush rights/cost admission research | defer | M16 allows fixtures; DR3 covers comparison methodology; admission research only when real multi-provider capture is wanted | none currently |
| Audit workflow / audit preservation policy | do not add to DR backlog | Not research — repo process. Belongs in `audits/README.md` + one closure-convention line | — |
| Repo authority/index consistency checks | do not add to DR backlog | Same — process, not research. ISS-14's closure-convention addition is the durable fix; a steward checklist in ROADMAP_RULES if desired | — |

---

## 13. M7 contract-readiness verdict

**Yes, after small cleanup.**

Exact cleanup before the first contract is drafted (half a session):
1. `audits/README.md` + REPO_MAP row (ISS-01/02)
2. Fix `research/README.md` reading order + review notes (ISS-03)
3. RG13 H19–H22 addendum note (ISS-11)
4. Create the owner-ruling tracker and log §11 (ISS-12)
5. Create `contracts/` + `contracts/README.md` + contract template (roadmap blocker)
6. Manually verify git state / push if ahead (ISS-21 — I cannot check this)

Everything else (ISS-04–10, 13–14, 16–19, 22) lands during M7 without blocking drafting.

---

## 14. Recommended immediate fixes

In order: the six items in §13, plus create `planning-inbox/m7-audit-response-2026-07-07.md` consolidating both audits' findings in the AUD-table format with routing/status columns — that file then becomes the during-M7 checklist for ISS-04 through ISS-22 and prevents this audit from evaporating into chat history, which is precisely the failure mode the audit-response pattern was invented for.

---

## 15. Recommended M7 first moves after fixes

1. Put owner-ruling group "during M7" (§11 items 1–7) in front of the owner; record outcomes in the tracker/decisions.
2. Draft the spine: scope/rights/retention contract (RG2), then evidence ID/citation contract (RG3).
3. Draft freshness/volatility (RG5, bands labeled provisional), then merged claim-safety + absence contract (RG8/RG6) including the `predictive_claim` class and the RG6 tightenings.
4. Draft query panel (RG4), CapturePackage (RG10), merged raw-archive + drift (RG11).
5. Draft provider testimony + Cross-Check (ledger as open-question section per ruling #1).
6. Draft consumer + promotion contract (RG12); overlay contract covering customer first-party overlays **and** NC3 intervention timelines as the same ephemeral-input mechanism; SearchClarity placeholder (placeholder only); typed read-tool skeleton (with NC5 coverage/blind-spot output fields if so ruled).
7. Refresh the stale trackers (ISS-05/07/08), archive CLAUDE_START_HERE (ISS-06), add DR16/DR17, add the M5→gates mapping note, add the closure-convention line (ISS-14).
8. Close M7 per the (now-improved) closure convention; commit; push before any cross-tool handoff.

---

## 16. Stop / do-not-build warnings

- No schema, migrations, or "quick tables" for any RG field list — every field list is contract input and says so.
- The typed read-tool contract stays a skeleton in M7; M14 owns the real contract.
- Owned-telemetry contract: placeholder only until DR11. SearchClarity contract: placeholder only until DR9.
- The three fake-mustache entry points — persisted Disagreement Ledger, stored `ai_visibility_sample_summary`, "mechanically derived" sentiment — require the V6 materialization test and/or an owner ruling before any contract permits persistence. Default answer stays no.
- Nothing automated touches Etsy. Fiverr stays not-cleared. The extension stays a candidate requiring admission.
- The $50 stays holstered. Minimum-payment knowledge is planning evidence, not a fuse.
- Audit reports, including this one, are planning input. If any future doc cites an audit as authority for a capability, that citation is invalid by construction.

---

## Full repo audit verdict:

**Repo is clean enough after small cleanup.**

Cleanup items (blocking-adjacent, one short session): `audits/README.md` + REPO_MAP row; `research/README.md` staleness fix; RG13 H19–H22 addendum; owner-ruling tracker; `contracts/` + README + contract template (the roadmap's own M7 drafting blocker); manual git-state verification/push. All remaining issues (ISS-04–10, 13–19, 22) are during-M7 work, tracked in §9, and none blocks the first contract.
