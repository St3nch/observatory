# Observatory Agent Instructions

## Authority

Read in this order:

1. VISION.md
2. VOCABULARY.md
3. decisions/decisions.md
4. decisions/deferred.md
5. Relevant ticket under `tickets/`
6. Relevant ADR under `docs/adr/`, when one exists
7. Parent spec under `docs/specs/`, when the ticket names one

VOCABULARY.md defines canonical domain language. Do not silently invent synonyms, overload
a defined term, or introduce a new domain concept in code alone. Proposed vocabulary
changes require Project Steward reconciliation with existing authority.

Files under `docs-temp/` are ignored working notes and are never project authority.
External design drafts and stashed work are not repository authority until the Steward
reconciles them into the files above.

## Roles

- The human product owner owns product purpose, priorities, major trade-offs, final
  decisions, and release approval.
- The Project Steward owns sequencing, architectural coherence, authority maintenance,
  ticket quality, integration, acceptance evidence, and drift control.
- Coding and review agents implement or inspect bounded assignments under the current
  authority and ticket. They do not replace the Project Steward or silently redefine
  project direction.
- Agent findings are inputs. A finding changes the project only after the Project Steward
  reconciles it with existing authority and records any resulting decision.
- No agent may broaden its assignment merely because it discovers adjacent work; report
  the finding and keep the current ticket bounded.

## Hard boundaries

- Observatory is a standalone observation-data service.
- Every consumer uses the versioned API; never create direct database or file access for a
  project, LLM, agent, or script.
- Keep strategy, recommendations, conclusions, scoring, reporting narratives, customer
  overlays, and campaign workflow outside Observatory.
- Preserve exact evidence and immutable attempt/outcome history; make query projections
  rebuildable and versioned.
- Never collapse missing, refused, failed, partial, malformed, or inapplicable states.
- Never make provider calls from ordinary automated tests.
- Never claim fixture or mock success proves real PostgreSQL, crash, concurrency, or
  recovery behavior.
- Do not weaken durability to improve development convenience.

## Work method

- Work from one ticket with observable acceptance criteria.
- Ordinary tests are the default.
- Add a hammer candidate only when the invariant, consequence, and required proof substrate
  can be named.
- Create an ADR only when the choice is hard to reverse, surprising without context, and
  the result of a real trade-off.
- Do not generate planning, audit, closure, or status document trees.
- When a decision changes, update the existing authority instead of adding a competing file.
- Do not implement deferred work before its recorded trigger fires.

## Artifact locations

| Kind | Path | Authority? |
|---|---|---|
| Vision, vocabulary, decisions | repo root / `decisions/` | yes |
| Accepted specs | `docs/specs/<slug>.md` | yes (normative when accepted) |
| ADRs | `docs/adr/` (create lazily) | yes |
| Implementation tickets | `tickets/<feature-prefix>-<ordinal>-<slug>.md` | yes (work units) |
| Spec drafts, grilling notes, wayfinder maps, handoff | `docs-temp/…` | no |
| Handoff file | `docs-temp/GROK-HANDOFF.md` | no |

Ticket IDs use feature-specific forms such as `CE-01` or `API-03`. Create directories only
when they have content. Do not add auxiliary README or index files under `tickets/` or
`docs/specs/`.

## Workflow

Main chain:

1. `grill-with-docs` (uses `grilling` + `domain-modeling`) → proposal package
2. **Steward reconciliation** → authority updates only when accepted
3. `to-spec` → draft at `docs-temp/specs/`; promote to `docs/specs/` only on explicit
   Steward direction
4. **Steward acceptance** of the durable spec
5. `to-tickets` → files under `tickets/` after breakdown approval
6. **Steward acceptance** of the ticket set
7. `implement` → `tdd` → `code-review` → remediation
8. implement sets ticket status to `review` and records evidence; never `done`
9. `handoff` as needed; **Steward closure** sets `done`

Optional and situational: `prototype` (throwaway design question), `wayfinder`
(multi-session decision fog in `docs-temp/wayfinder/` only).

Do not create `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/agents/`, `.scratch/`, or external
issue-tracker scaffolding.

## VedaOps lease

Require an active Observatory lease before every filesystem mutation, including under
`docs-temp/`. Renew when fewer than 30 minutes remain. Align lease `expected_git_head`
with the repository HEAD you intend to mutate.

## Commands

These are the intended repository commands once the Python project scaffold exists:

    uv run pytest -q
    uv run ruff check .
    uv run mypy
    uv run python -m observatory.migrate
    uv run python -m observatory.derive

## Grok skill policy

The approved Grok skills for Observatory are the project-local copies under
`.grok/skills/`:

- `setup-matt-pocock-skills`
- `implement`
- `tdd`
- `code-review`
- `diagnosing-bugs`
- `research`
- `domain-modeling`
- `codebase-design`
- `handoff`
- `wait-what`
- `grilling`
- `grill-with-docs`
- `to-spec`
- `to-tickets`
- `wayfinder`
- `prototype`
- `writing-for-agents`

These project copies override same-named user-plugin skills. Every skill invocation must
report the absolute path of the project-local `SKILL.md` it loaded. Do not invoke another
Pocock/plugin skill in Observatory unless the Project Steward explicitly directs it.

The setup skill validates this existing project layout; it must not create a parallel
`CONTEXT.md`, `docs/agents/`, issue-tracker configuration, or triage system.

`skills-lock.json` records installer upstream provenance only. Local adaptations live in
the skill files and git history. Do not invent lockfile schema fields. A future skills
update must not blindly overwrite adapted project-local skills.

Skill output is working input, not project authority. Skills may propose vocabulary,
decision, or architecture changes, but only the Project Steward reconciles and records
them. An approved ticket supplies the implementation scope, acceptance behavior, and
test seams; do not repeatedly ask the product owner to reconfirm them.

## Completion

A ticket is complete only when the Project Steward closes it and:

- its acceptance behavior is observable;
- relevant ordinary tests pass on the correct substrate;
- data and API boundary rules remain intact;
- the exact unproven limits are stated;
- authority docs changed only if the ticket made a real decision.
