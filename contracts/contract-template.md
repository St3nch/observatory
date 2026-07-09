# Contract Template

Status: template
Authority: reusable contract structure; binding for contract format once contracts are drafted
Purpose: standardize Observatory non-schema contracts so every contract preserves sources, boundaries, fail-closed behavior, owner rulings, and hammer expectations

---

Copy this structure into every new contract under `contracts/`.

---

# Contract — [Name]

Status: draft / ready for review / accepted / superseded
Authority: contract (binds only when accepted; subordinate to `02-boundaries.md`)
Version: 0.1
Date:
Milestone: M7 — Core Contract Planning
Source research: [RG docs and other inputs this contract is drafted from]
Supersedes / superseded by:

---

## Purpose

One paragraph: what behavior this contract governs and why it must exist before schema/implementation.

---

## Governing boundaries

List the specific `02-boundaries.md` rules this contract operationalizes. On conflict, boundaries win.

---

## Definitions

Terms and vocabularies this contract owns or imports. Cite the source RG for imported vocabularies.

---

## Contract rules

The normative core. Numbered rules. Each rule should be testable — if M8 cannot imagine a hammer for a rule, the rule is too vague.

```text
R1.
R2.
```

---

## Required fields / shapes

Contract-level required fields, statuses, and vocabularies. These are behavior requirements, NOT schema. M10 derives schema from them; this section must not pre-draw tables.

---

## Fail-closed behavior

What happens when information is missing, unknown, ambiguous, or in conflict. Every contract must fail closed somewhere; say exactly where and how.

---

## Forbidden patterns

What this contract explicitly forbids, including renamed/fake-mustache variants. If persistence of any interpretive output is even adjacent, state that it requires the V6 materialization test plus owner ruling.

---

## Examples

At least one valid example and one invalid example with the reason it fails.

---

## Owner-ruling candidates

Open rulings this contract needs, cross-referenced to `planning-inbox/owner-ruling-tracker.md`. A contract may be accepted with open rulings only if each open ruling is marked and the affected behavior fails closed until ruled.

---

## Deeper-research blockers

DR items or future gates that block parts of this contract from becoming operative (e.g., provider-specific bindings blocked until M13/DR1).

---

## Hammer expectations

Which RG13 hammer categories (H1–H22) must prove this contract under M8+. Name the hostile paths specific to this contract.

---

## Feeds milestones

Which later milestones consume this contract.

---

## Change log

```text
0.1 — [date] — initial draft from [sources]
```
