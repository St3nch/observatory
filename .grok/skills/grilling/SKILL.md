---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

# Grilling

## Observatory preflight

1. Report the absolute path of this loaded file:
   `/home/chaz/projects/vedaops/observatory/.grok/skills/grilling/SKILL.md`
   Prefer the resolved project-local path under `.grok/skills/grilling/SKILL.md`.
   Project-local skills override plugin copies.
2. When the topic touches Observatory product work, read `VISION.md`, `VOCABULARY.md`,
   `decisions/decisions.md`, and `decisions/deferred.md` before asking product questions.
3. Produce no durable authority. Optional working notes go only under
   `docs-temp/grilling/<slug>.md`.

## Process

Interview the user relentlessly until you reach a shared understanding. Map this as a
**design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are
already settled — the questions you can ask _now_ without guessing at answers you have
not heard yet. Ask the whole frontier in one round: number each question and give your
recommended answer. Then wait for the user's answers before the next round.

Format each question:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round reshapes the tree — settled decisions push the frontier outward. Recompute the
frontier and ask the next round. A question whose answer depends on another still open in
this round belongs to a later round.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from
the environment, dispatch a sub-agent — do not ask the user for anything you can look up.
Do not block the rest of the frontier on a running exploration: only questions downstream
of that fact wait. The _decisions_ are the user's — put each to them and wait.

## Completion

The session is done when the frontier is empty: every branch visited, nothing left silently
assumed. Do not act on the result until the user confirms shared understanding. Hand
accepted product implications to the Project Steward for reconciliation; do not edit
authority files from this skill.
