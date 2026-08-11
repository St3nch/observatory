---
name: wayfinder
description: Plan a huge chunk of work — more than one agent session can hold — as a shared map of decision tickets on your issue tracker, and resolve them one at a time until the way to the destination is clear.
disable-model-invocation: true
---

# Wayfinder

Situational only. Use when one grilling or to-spec session cannot hold the decision fog.
Not part of the default Observatory main chain.

## Observatory preflight

1. Report the absolute path of this loaded file:
   `/home/chaz/projects/vedaops/observatory/.grok/skills/wayfinder/SKILL.md`
   Prefer the resolved project-local path. Project-local skills override plugin copies.
2. Read `VISION.md`, `VOCABULARY.md`, and both decision registers when product-related.
3. Require an active VedaOps lease before any filesystem write.
4. Maps are working state under `docs-temp/` only — never authority, never
   `tickets/`, never an issue tracker, never `.scratch/` or `docs/agents/`.
5. Material decisions still require **Steward reconciliation** before authority or specs change.

## Plan, don't do

Each map ticket resolves a **decision**, not a build slice. The map is done when the way
to the destination is clear. Absent an explicit Notes override, produce decisions, not
deliverables. Refer to tickets by **name**, not bare ids.

## Map location

- Map file: `docs-temp/wayfinder/<slug>-map.md`
- Decision notes (optional siblings): `docs-temp/wayfinder/<slug>/…`
- Create directories lazily. No index README.

### Map body

```markdown
## Destination

<what clear way looks like — one or two lines>

## Notes

<skills to consult; standing preferences>

## Decisions so far

- <closed ticket name> — <one-line gist>

## Not yet specified

<!-- fog toward the destination; graduate when sharp enough to ticket -->

## Open decision tickets

- **<name>** (`research` | `prototype` | `grilling` | `task`) — <question>
  - Blocked by: …

## Out of scope

<!-- ruled beyond this destination -->
```

## Ticket types

- **Research** (AFK): facts from primary sources via project-local `research`; findings in
  `docs-temp/`, never authority.
- **Prototype** (HITL): cheap artifact via project-local `prototype`.
- **Grilling** (HITL): conversation via `grilling` + `domain-modeling`. Agent never answers
  for the human.
- **Task** (HITL or AFK): manual prerequisite that unblocks a decision, not the destination.

## Fog of war

Ticket when the question is sharp (even if blocked). Leave in **Not yet specified** when
you cannot yet phrase it sharply. Out of scope is not fog.

## Invocation

Never resolve more than one non-research decision ticket per session.

### Chart the map

1. Name the destination with `grilling` + `domain-modeling`.
2. Breadth-first grill for the first takeable decisions. If no fog remains and the work fits
   one session, stop and ask whether to skip Wayfinder.
3. Under lease, write the map under `docs-temp/wayfinder/`.
4. Add only the decision tickets you can specify now; keep the rest as fog.
5. Fire research subagents for research tickets when useful; capture under `docs-temp/`.
6. Stop — charting hand-resolves nothing.

### Work through the map

1. Load the map (low-res index).
2. Take the named ticket or the first unblocked open ticket. Claim it in the map body
   (assignee / in-progress note) before work.
3. Resolve via the type's skills. Zoom related closed tickets as needed.
4. Record the answer on the ticket note, move a one-line gist into **Decisions so far**,
   and graduate fog when sharp.
5. Do not edit `VISION.md`, `VOCABULARY.md`, decisions, ADRs, or `docs/specs/` from
   Wayfinder. Hand material outcomes to Steward reconciliation; when the way is clear,
   proceed to `to-spec` or Steward-directed next step.

## Completion

Map updated; at most one decision resolved this session (research excepted). Durable
product change waits on Steward recon.
