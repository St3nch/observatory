# Audit Response — 2026-07-07 Claude Repo Audit

Status: planning
Authority: none
Purpose: track every Claude audit finding, route it to the right milestone/file, and prevent partial audit cherry-picking
Source: `observatory-repo-audit-2026-07-07.md` uploaded project knowledge
Created: 2026-07-07

---

## Owner correction

Claude audit findings must not be handled partially. Every finding gets one of these outcomes:

```text
apply now
assign to milestone
defer with reason
reject with reason
needs owner ruling
```

Do not fix only the loudest issues and let the rest disappear into chat memory. Audit response items must be written into the repo, pointed at the correct roadmap milestone, and revisited when that milestone activates.

---

## Source-of-truth rule

```text
Live repo + Go8 state = source of truth for committed project state.
Audit docs = serious review input and gap evidence.
Chat summaries = lowest trust unless reconciled into repo.
```

---

## Audit verdict captured

Claude's audit verdict was healthy but not clean-closed:

```text
Ready for M2: yes, after closure/hygiene actions.
Ready for research: not yet.
Ready for schema planning: no.
Ready for implementation: no.
Ready for provider pulls: no.
Ready for API/MCP work: no.
```

The audit found process and roadmap hygiene issues, not project-collapse issues.

---

## Audit finding backlog

| ID | Finding | Timing | Target milestone | Target files | Action | Status | Notes |
|---|---|---|---|---|---|---|---|
| AUD-001 | M1 is substantively complete but still marked active | apply now | M1 closure / M2 activation | `ROADMAP.md`, `ACTIVE_CONTEXT.md`, `NEXT_SESSION_HANDOFF.md` | Close M1, mark M2 active, update handoff/context | done in closure pass | M1 closed and M2 activated. |
| AUD-002 | Local repo is ahead of origin and must be pushed before multi-tool handoff | apply now / manual if no push tool | M1 closure | Git remote | Push after closure commits | open | Avoid Claude/GitHub reading stale repo. |
| AUD-003 | Line-ending churn creates noisy diffs | apply now | M1 closure / M2 prep | `.gitattributes` | Add LF normalization rule and avoid CRLF goblin noise | done in closure pass | `.gitattributes` added; any remaining normalization can be handled by Git after commit. |
| AUD-004 | Milestone closure convention is missing | apply now | M1 closure / M2 prep | `ROADMAP_RULES.md` | Add closure convention and status transition rule | done in closure pass | Closure convention added to roadmap rules. |
| AUD-005 | Planned milestones do not all include full required reading/blockers fields | apply now / assign | M1 closure / M2 prep | `ROADMAP.md`, `ROADMAP_RULES.md` | Clarify minimum context for planned milestones and mandatory full fields at activation | done in closure pass / carry forward | Rule clarified and future milestones now point to planning context; full required-reading details remain mandatory at activation. |
| AUD-006 | M2 folder subset needs owner ruling | apply now | M2 | `ROADMAP.md`, `decisions/2026-07-07-m2-folder-subset.md` | Record decision: create `decisions/`, `archive/`, `research/`; defer `contracts/`, `hammers` | done in M2 | Ruling recorded as an accepted decision. |
| AUD-007 | Decision record template missing | during M2 | M2 | `decisions/README.md`, `decisions/decision-record-template.md` | Create template | done in M2 | Supports owner rulings and scope/doctrine changes. |
| AUD-008 | Archive rule missing | during M2 | M2 | `archive/README.md` | Create archive README/rules | done in M2 | Archive rule created. |
| AUD-009 | REPO_MAP must match actual folders | during M2 | M2 | `REPO_MAP.md` | Update after folders exist | done in M2 | Repo map now lists `decisions/`, `archive/`, and `research/`. |
| AUD-010 | README/LLM_START_HERE read-order circularity | during M2 | M2 | `README.md`, `LLM_START_HERE.md` | Make one canonical order; likely LLM_START_HERE owns full path | done in M2 | README now defers to `LLM_START_HERE.md` as canonical read order and includes `README.md` in the list. |
| AUD-011 | Sibling repos optional context note missing | during M2 | M2 | `README.md` | Add note that ancestor repos are optional context; current repo is authority | done in M2 | Added note to README. |
| AUD-012 | Go8 term is undefined | during M2 or later glossary | M2 / glossary | `planning-inbox/README.md`, future glossary | Define briefly or avoid unexplained term | done in M2 | Added a brief Go8 note to planning-inbox README. |
| AUD-013 | Classified Claude docs absent from repo | before M5 | M3 | `planning-inbox/strategy-layer-dangerous-design.md`, `planning-inbox/deep-research-danger-agenda.md`, `planning-inbox/steward-context-dump.md` | Add with labels, no authority promotion | assigned | Must happen before boundary/research use. |
| AUD-014 | Cross-scope aggregation denial is not authority law | before M5 | M4 | `02-boundaries.md` | Add denial-by-default section | assigned | Prevent customer-engagement leakage. |
| AUD-015 | Scope / scope_class model absent from boundary law | before M5 | M4 | `02-boundaries.md` | Add `scope` + `scope_class` boundary section | assigned | Must connect rights/retention to scope. |
| AUD-016 | Proprietary-score sentence not in `02-boundaries.md` | before M5 | M4 | `02-boundaries.md` | Promote exact rule and examples | assigned | Provider scores are model outputs, not web facts. |
| AUD-017 | Anti-cache strategy loophole only in non-authority doc | before M5 | M4 | `02-boundaries.md` | Add no fake scratch/candidate strategy storage clause | assigned | Closes likely strategy leakage path. |
| AUD-018 | Read-time derived outputs need no-persist clarification | before M5 | M4 | `02-boundaries.md` | Add no persisted derived read-tool outputs rule | assigned | Prevent read tools from creating strategy result tables. |
| AUD-019 | OBR-01 / DataForSEO rights-retention-cost blocker not named on M13 | before M5/M13 | M5/M13 | `ROADMAP.md`, research docs | Add named blocker and research gate | assigned | $50 stays holstered until gate clears. |
| AUD-020 | Provider Cross-Check needs standalone gate-spec doc | before M7 | M5 | future `research/` doc | Create research gate spec | assigned | Already early in roadmap; needs focused doc. |
| AUD-021 | Promotion / conclusion-handoff contract missing | before M7 | M7 | `ROADMAP.md`, future `contracts/` doc | Add to M7 contract list and later draft | open | Doctrine says conclusions promote out; shape must exist. |
| AUD-022 | Consumer contracts underrepresented | before M7 | M7 / M15 | `ROADMAP.md`, future contracts | Add SearchClarity consumer-contract placeholder; defer Neon Ronin/Kaizen if needed | open | Avoid vague consumer boundary. |
| AUD-023 | Contract document template missing | before M7 | M7 or M2 if contracts folder early | future `contracts/` | Create before drafting contracts | assigned | Deferred with contracts folder unless owner pulls earlier. |
| AUD-024 | M7 contract priority not explicit | before M7 | M7 | `ROADMAP.md`, future contracts README | Prioritize scope/rights/retention, evidence ID, CapturePackage, provider testimony/disagreement | assigned | Prevents 14-contract pileup. |
| AUD-025 | Evidence ID and scope models must settle before schema | before M10 | M7-M10 | contracts, `ROADMAP.md` | Ensure schema blocked until settled | assigned | Schema must not guess. |
| AUD-026 | M9 first slice must name contract coverage and hammer set | before M10 | M9 | `ROADMAP.md`, future first-slice doc | Add to M9 expectations | assigned | Prevents vague first slice. |
| AUD-027 | M11/M12 deliverables too vague for later implementation | before implementation | M9-M12 | `ROADMAP.md`, future implementation docs | Re-spec during M9/M10 | assigned | Fine now, dangerous later. |
| AUD-028 | Raw archive backup/hash verification arrives too late | before implementation | M12/M19 | `ROADMAP.md`, future hammers | Add minimal M12 expectation | assigned | Evidence IDs cannot point to fragile raw files. |
| AUD-029 | Hammer matrix must cover overlay no-persistence and anti-cache | before implementation | M8/M17 | `ROADMAP.md`, hammers | Add to hammer categories | assigned | Ties boundary law to tests. |
| AUD-030 | M20 acceptance evidence bundle missing | later | M19/M20 | `ROADMAP.md`, future ops/acceptance docs | Define later | deferred | Not needed before M2. |
| AUD-031 | Recurring capture execution should be explicitly post-v1 if not in v1 | later | M18/M20 | `ROADMAP.md` | Clarify when M18 activates | deferred | Planning only for now. |
| AUD-032 | Neon Ronin / Kaizen consumer contracts likely post-v1 | later | M7/M15/post-v1 | future contracts | Defer unless friction arrives | deferred | SearchClarity proof comes first. |
| AUD-033 | Glossary / terms note missing | later / opportunistic | M2-M4 | future glossary or README | Define Go8, IMI, OBR-01, Hermes, 030B, scope_class | assigned | Helpful but not M2 blocker. |

---

## M1 closure action plan

Apply immediately before M2 work:

1. Close M1 in `ROADMAP.md`.
2. Mark M2 active in `ROADMAP.md`.
3. Update `ACTIVE_CONTEXT.md` and `NEXT_SESSION_HANDOFF.md` to M2.
4. Add `.gitattributes` for line-ending normalization.
5. Add closure convention and planned-milestone context rule to `ROADMAP_RULES.md`.
6. Ensure M2 required reading includes this audit-response artifact.
7. Commit and push if a push tool is available.

---

## M2 owner ruling captured for execution

M2 should create only the earned folders needed now or soon:

```text
decisions/
archive/
research/
```

Defer until their owning milestones:

```text
contracts/  -> M7
hammers/    -> M8
```

Reason: decisions and archive are needed immediately; research is next soon; contracts and hammers are real but not yet earned as active folders.

---

## Milestone context rule reminder

Each milestone must point to the planning documents needed when that milestone activates.

For planned milestones, the roadmap should either list the planning/context docs directly or state that the full required reading list is finalized at activation from prior milestone outputs.

Do not leave future milestones as contextless labels.
