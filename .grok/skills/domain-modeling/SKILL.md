---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when the user wants to pin down domain terminology or a ubiquitous language, record an architectural decision, or when another skill needs to maintain the domain model.
---

# Domain Modeling

## Observatory rules

Observatory uses one authoritative glossary: `VOCABULARY.md`. Never create
`CONTEXT.md`, `CONTEXT-MAP.md`, or a second glossary. Read `VISION.md`, both decision
registers, `AGENTS.md`, and the relevant ticket before proposing model changes.

Challenge fuzzy or conflicting terms and test them with concrete scenarios, but present
the proposed definition and affected code/API/schema names to the Project Steward.
Do not edit vocabulary or create an ADR as an automatic side effect. The Project Steward
reconciles accepted changes with existing authority. ADRs remain subject to the
three-part bar in `AGENTS.md`.

Actively build and sharpen the project's domain model as you design. This is the *active*
discipline: challenge terms, invent edge-case scenarios, and propose precise language.
Merely reading `VOCABULARY.md` is a normal project habit, not invocation of this skill.

## Authority locations

- Canonical terms live only in `VOCABULARY.md`.
- Settled product decisions live in `decisions/decisions.md`.
- Deliberately deferred work lives in `decisions/deferred.md`.
- Create `docs/adr/` lazily only after the Project Steward accepts a decision that meets
  the ADR bar.
- Working scenarios and unresolved proposals belong in ignored `docs-temp/`, not authority.

## During the session

### Challenge against the glossary

When a term conflicts with `VOCABULARY.md`, call it out immediately and quote the
existing definition. Ask which concept is intended only when the surrounding ticket and
authority do not resolve the ambiguity.

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Propose authority reconciliation

State the proposed canonical term, its concise definition, avoided synonyms, affected
existing definitions, and affected API/schema/code names. The Project Steward decides
whether and when to update `VOCABULARY.md` and related authority.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).
