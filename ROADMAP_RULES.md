# Roadmap Rules — The Observatory

Status: authority
Authority: roadmap control rules
Purpose: preserve project memory and prevent roadmap drift

---

## Purpose

The roadmap is the project's memory spine.

It exists so The Observatory does not become a pile of half-remembered chat decisions, stale ambitions, and one lonely README screaming into the void.

Roadmap changes must preserve context, boundaries, required reading, and implementation gates.

---

## Roadmap Preservation Rules

1. Keep milestone intent visible.
2. Keep current status visible.
3. Keep deferred work visible without pretending it is approved.
4. Keep killed concepts visibly killed.
5. Preserve required reading before implementation.
6. Record blockers instead of silently skipping them.
7. Do not collapse planning notes into authority without an explicit edit class and reason.
8. Do not start implementation work before the relevant milestone gate.
9. Do not delete roadmap history silently.

---

## Roadmap Edit Classes

Every meaningful roadmap edit should fit one of these classes.

### Maintenance

Small upkeep that does not change meaning.

Examples:

- typo fixes
- link fixes
- status date updates
- adding a missing file reference
- formatting cleanup

### Clarification

Improves wording or makes an existing rule easier to understand without changing scope.

Examples:

- clearer milestone wording
- sharper boundary phrasing
- adding an example that matches existing doctrine
- splitting a vague sentence into a precise checklist

### Scope Change

Changes what the roadmap includes, excludes, sequences, or prioritizes.

Examples:

- adding a milestone
- removing a milestone
- moving provider validation earlier or later
- introducing a new folder family
- turning a deferred item into an active planning item

Scope changes require owner approval or an explicit accepted planning decision.

### Doctrine Change

Changes project law.

Examples:

- allowing customer first-party data into Observatory
- allowing stored recommendations
- allowing direct SQL access for an agent
- weakening hammer-test gates
- reviving a killed ancestor concept

Doctrine changes require explicit owner ruling. Treat them like a loaded nail gun.

---

## Milestone Required-Reading Rule

Every milestone must list required reading before implementation begins.

Required reading may name:

- exact files
- exact folders
- exact external source documents when unavoidable

If a milestone lists a folder as required reading, that folder must contain a `README.md` that summarizes what each important document in that folder is for.

No folder README, no folder-as-required-reading. Simple. Brutal. Effective.

---

## Folder README Rule

Every folder that becomes part of a required read path must include a `README.md` with:

- purpose
- what belongs there
- what does not belong there
- reading order
- file index
- related roadmap milestones
- notes for LLMs
- last review notes

Use `FOLDER_README_TEMPLATE.md` unless there is a good reason not to.

---

## Required Milestone Format

Each roadmap milestone should include:

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

Optional but recommended:

```text
Owner rulings needed:
Files likely touched:
Hammer implications:
Notes for LLMs:
```

---

## Planned Milestone Context Rule

Planned milestones must point to the planning/context documents that will matter when the milestone activates.

For early planned milestones, list exact files where possible.

For later milestones whose complete inputs will be produced by earlier gates, the roadmap must still name the expected prior milestone outputs, such as:

- M4 boundary outputs
- M6 research outputs
- M7 contract outputs
- M8 hammer matrix
- M9 first-slice decision

Do not leave future milestones as contextless labels.

Full `Required reading`, `Blockers`, and `Owner rulings needed` fields become mandatory when a milestone is activated. Before activation, the roadmap must at least preserve enough planning-document context for the next steward to know what to read and why.

---

## Milestone Closure Convention

A milestone closes only through an explicit closure edit.

A closure edit must:

1. verify the milestone exit criteria against the live repo;
2. update the milestone summary table;
3. move the closing milestone to `closed` status;
4. move the next milestone to `active` status;
5. update `ACTIVE_CONTEXT.md`;
6. update `NEXT_SESSION_HANDOFF.md`;
7. record unresolved audit findings or blockers in the appropriate planning/control doc;
8. commit the exact changed paths;
9. push before handing work to another tool or clone when push tooling is available.

Do not leave a completed milestone marked active just because the work feels done. If it is not closed in the repo, it is not closed.

---

## Required Reading Proof

Before implementation begins for a milestone, the acting steward must report:

- files read
- folders read through their README index
- missing files, if any
- contradictions or stale docs found
- whether the milestone gate is open or blocked

If required reading cannot be completed, the milestone is blocked.

---

## Implementation Gate Rule

Implementation may begin only when:

1. the roadmap milestone allows implementation;
2. required reading is complete;
3. boundaries are not contradictory;
4. required folder READMEs exist;
5. owner approval has been recorded where needed;
6. hammer expectations are known for the implementation area.

M0 does not allow implementation.

---

## Anti-Drift Rule

If a proposed roadmap edit would make The Observatory store strategy, recommendations, customer records, or fake truth, stop and classify it as a doctrine change.

Default answer: no.

The project can get fancier later. First it has to stop stepping on rakes.
