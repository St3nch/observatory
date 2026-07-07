# M4 Boundary Reconciliation — Delta Classification

Status: planning / reconciliation note
Authority: none
Purpose: classify boundary deltas before and after root boundary-law hardening
Date: 2026-07-07

---

## Scope

This note supports active M4:

```text
M4 - Boundary Reconciliation and Doctrine Hardening
```

It compares the live boundary law in `02-boundaries.md` against the newly preserved M3 planning/context docs:

- `planning-inbox/strategy-layer-dangerous-design.md`
- `planning-inbox/deep-research-danger-agenda.md`
- `planning-inbox/steward-context-dump.md`

This note does not change doctrine. It classifies what should be confirmed, clarified, deferred, or escalated for owner ruling.

---

## Current boundary baseline

Live `02-boundaries.md` already establishes:

- Observatory stores observations, not conclusions.
- Strategy and recommendations are forbidden inside Observatory storage.
- Customer records and customer first-party analytics are out.
- Customer first-party series may only be supplied as read-time overlays.
- Owner-internal first-party telemetry requires explicit internal-scope boundary handling before storage.
- Provider data is observed testimony, not truth.
- Provider disagreement must be preserved and not averaged into fake truth.
- LLMs and agents receive no direct SQL credentials, arbitrary query tools, or table CRUD tools.
- Hammer tests are a hard gate for implementation.
- VEDA Brain, intelligence synthesis tables, recommendation stores, and persistent Observatory strategy layers stay killed.

M4 should not weaken any of these.

---

## Delta classification

### D1 — Strategy Layer wording should be hardened

Classification: clarification candidate, likely safe

Planning source:
`strategy-layer-dangerous-design.md` repeatedly frames Strategy Layer as a process / verb, not a stored Observatory system.

Live boundary coverage:
`02-boundaries.md` already forbids strategy and recommendation storage and lists Strategy / IMI as a deferred future layer outside Observatory.

Gap:
The live boundary could say more explicitly that Strategy Layer means read-time interpretation and downstream promotion, not a new Observatory storage family.

Suggested root-boundary direction:
Add clarification under Strategy and Recommendation Boundary or Deferred / Future Layers:

```text
A Strategy Layer, if discussed, is a read-time/process boundary over Observatory evidence, not an Observatory storage system. Its durable outputs must live in the owning consumer, not in Observatory.
```

Owner ruling needed: likely no, if treated as clarification of existing law.

---

### D2 — TacticCapture / online tactic ingestion is not admitted

Classification: owner-ruling required before any family or workflow is admitted

Planning source:
`strategy-layer-dangerous-design.md` proposes capturing online SEO/GEO tactics as observations of claims, with quarantine and triage.

Live boundary coverage:
`02-boundaries.md` allows eventual scoped, rights-labeled observations and deferred capture runner / provider work, but does not admit a tactic-capture family.

Gap:
A tactic claim may be a valid observation of someone else's claim, but triage verdicts and tactic suitability decisions are interpretation/governance, not Observatory evidence.

Suggested posture:
Do not add TacticCapture to root boundary law yet. Preserve as future candidate requiring owner ruling and probably M5/M7 handling.

Owner ruling needed:
Yes. Questions:

- Are tactic captures allowed as a deferred observation family?
- If yes, are captures files only for now, or future Observatory evidence?
- Where do triage verdicts live: Neon Ronin review queue, Kaizen decision/governance, or another consumer layer?

---

### D3 — Cross-scope aggregate analysis remains dangerous

Classification: explicit owner-ruling required

Planning source:
`deep-research-danger-agenda.md` flags volatility seismograph / update detection as a future candidate that may require cross-scope aggregate reads.

Live boundary coverage:
`ROADMAP.md` already lists cross-scope aggregate seismograph as forbidden unless owner ruling. `02-boundaries.md` does not yet spell out the cross-scope aggregate rule.

Gap:
Root boundary law could explicitly state that cross-scope aggregate analysis is forbidden unless owner-approved, because it can leak customer-engagement intelligence.

Suggested root-boundary direction:
Add a short Cross-Scope Aggregate Boundary section saying cross-scope aggregation is forbidden by default and requires owner ruling, scope restrictions, anonymization expectations, and hammers.

Owner ruling needed:
Yes, if any exception is desired. No ruling needed to add the default-forbidden clarification.

---

### D4 — Provider scores need stronger wording

Classification: clarification candidate, likely safe

Planning source:
`steward-context-dump.md` says a provider's keyword-difficulty number is a Tier 1 observation of what the provider said, not truth. The Strategy doc says keyword difficulty must not become a provider opinion treated as fact.

Live boundary coverage:
`02-boundaries.md` says provider data is observed testimony, not truth, and provider disagreement must be preserved.

Gap:
Live boundary does not explicitly name proprietary provider scores / difficulty metrics.

Suggested root-boundary direction:
Add wording under Provider Evidence Boundary:

```text
Provider scores, difficulty metrics, authority metrics, or confidence scores are observations of provider model output. They are not facts about the web and must remain provider-attributed.
```

Owner ruling needed: likely no, if treated as clarification of existing law.

---

### D5 — Tier model is useful but not yet boundary law

Classification: planning candidate, defer to contracts/schema gates

Planning source:
`steward-context-dump.md` gives Tier 0 raw, Tier 1 normalized observations, Tier 2 mechanical derived indexes, Tier 3+ interpretation.

Live boundary coverage:
`02-boundaries.md` already separates observations from interpretation and forbids strategy/recommendation storage.

Gap:
The Tier model is strong, but adding it wholesale to boundary law may over-define implementation before contracts/schema gates.

Suggested posture:
Do not promote the full Tier model into `02-boundaries.md` during M4. Add only a small boundary clarification if needed:

```text
Mechanical derivations may be considered later only when they do not require judgment, weighting, or strategy interpretation.
```

Owner ruling needed: maybe not for a narrow clarification; yes if Tier 2 derived records are admitted as a storage family.

---

### D6 — Customer first-party overlay boundary is already strong

Classification: confirmed; no immediate change required

Planning source:
Strategy and steward docs repeatedly preserve customer first-party data as read-time overlay only.

Live boundary coverage:
`02-boundaries.md` already has a dedicated Customer First-Party Data Boundary section.

Gap:
No major gap found.

Suggested posture:
No boundary edit needed unless M4 wants to add stronger wording that overlay inputs must not be logged, cached, or persisted by Observatory read tools later.

Owner ruling needed: no.

---

### D7 — Internal first-party telemetry boundary is present but may need future contract detail

Classification: confirmed with future contract need

Planning source:
Steward context allows owner-internal first-party performance observations under explicit internal-scope handling.

Live boundary coverage:
`02-boundaries.md` has a dedicated Internal First-Party Telemetry Boundary.

Gap:
The boundary is adequate for M4. Future M7/M8 work must define contracts and hammers before any storage.

Suggested posture:
No immediate boundary edit required.

Owner ruling needed: no, unless trying to admit storage before its contract gate.

---

### D8 — Flow A / Flow B contamination should be more explicit

Classification: clarification candidate, likely useful

Planning source:
`steward-context-dump.md` strongly distinguishes:

```text
Flow B: providers / admitted capture instruments -> Observatory evidence
Flow A: workspace operational work -> sanitized signals -> Neon Ronin layer
```

Live boundary coverage:
`02-boundaries.md` says SearchClarity workflow state, Neon Ronin workspace operational state, and Kaizen governance records are out.

Gap:
The live boundary does not explicitly explain Flow A / Flow B contamination risk.

Suggested root-boundary direction:
Add a short contamination rule:

```text
Workspace-derived operational signals, even when sanitized, do not become Observatory evidence. Observatory observations must come from approved Observatory capture methods or admitted provider/capture instruments.
```

Owner ruling needed: likely no, if treated as clarification of existing out-of-scope boundaries.

---

### D9 — Recurring scans and scheduler posture remain deferred

Classification: confirmed deferred / future candidate

Planning source:
Strategy doc discusses recurring read-time scans over existing evidence.

Live boundary coverage:
`02-boundaries.md` lists automated recurring capture as deferred. `ROADMAP.md` delays recurring watch panel planning to M18.

Gap:
No immediate boundary gap. Read-time scans over existing evidence may be conceptually different from new capture/spend, but still need future scheduler/governance handling.

Suggested posture:
Do not add to boundary law now beyond preserving deferred status.

Owner ruling needed: yes before any recurring scheduler or autonomous queue emission.

---

### D10 — Persistent strategy records remain forbidden unless future V21-style ruling

Classification: confirmed forbidden / future doctrine-change path

Planning source:
Strategy and danger docs identify persistent strategy records / cross-engagement playbook mining as seductive but dangerous.

Live boundary coverage:
`02-boundaries.md` forbids strategy records, recommendations, opportunity scores as truth, accepted action plans, and persistent Observatory strategy layers.

Gap:
No doctrine gap. M4 may strengthen language against hidden candidate caches, scratch schemas, or session-note tables if desired.

Suggested root-boundary direction:
Optional clarification:

```text
Temporary candidate caches, scratch schemas, session-note tables, or hidden side stores are strategy/recommendation storage if they preserve interpretive outputs. They are forbidden inside Observatory.
```

Owner ruling needed: no if this clarifies existing prohibition.

---

## Recommended M4 root-boundary edits

Safe clarification candidates:

1. Strategy Layer is a process/read-time boundary, not Observatory storage.
2. Proprietary provider scores are provider-attributed observations, not facts.
3. Workspace-derived / sanitized operational signals do not become Observatory evidence.
4. Hidden candidate caches / scratch strategy stores are forbidden.
5. Cross-scope aggregate analysis is forbidden by default unless owner ruling grants a governed exception.

Owner-ruling candidates before activation:

1. TacticCapture as an admitted or deferred observation family.
2. Tactic triage verdict storage location.
3. Cross-scope aggregate exception for volatility seismograph / update detection.
4. Any persistent strategy records / V21-style future layer.
5. Any owned or customer first-party storage beyond current boundaries.

---

## M4 hardening applied

Applied to root `02-boundaries.md` during M4:

- Strategy / IMI layer clarified as read-time process boundary, not Observatory storage.
- Hidden candidate caches, scratch schemas, session-note tables, and side stores clarified as forbidden if they preserve interpretive outputs.
- Proprietary provider scores clarified as provider-attributed observations, not facts about the web.
- Workspace-derived operational signals / sanitized signals clarified as not Observatory evidence.
- Cross-scope aggregate analysis clarified as forbidden by default unless owner ruling grants a governed exception.

Still not admitted:

- TacticCapture family or workflow.
- Tactic triage verdict storage.
- Cross-scope aggregate exceptions.
- Persistent strategy records / V21-style future layer.
- Owned or customer first-party storage beyond current boundaries.
- Provider work, schema work, API/MCP work, dashboard work, recurring scans, or research execution.

---

## Suggested next move

M4 can proceed toward closure review after verifying `02-boundaries.md`, `ACTIVE_CONTEXT.md`, `ROADMAP.md`, and `NEXT_SESSION_HANDOFF.md` remain aligned and no new capabilities were admitted.

Do not admit TacticCapture, cross-scope aggregate exceptions, persistent strategy records, provider work, schema work, or recurring scans during M4 without explicit owner ruling.

---

## Final rule

```text
M4 hardens the walls.
It does not open new doors.
```
