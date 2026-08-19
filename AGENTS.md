# Observatory Agent Instructions

## Authority

Read in this order:

1. `VISION.md`
2. `VOCABULARY.md`
3. `decisions/decisions.md`
4. `decisions/deferred.md`
5. Relevant ticket under `tickets/`
6. Relevant ADR under `docs/adr/`, when one exists
7. Normative capture/evidence contract: `docs/specs/capture-event-v2.md` when the work
   touches Attempt, Capture, Evidence, Evidence Store, derive-from-capture, or fixture
   capture

VOCABULARY.md defines canonical domain language. Do not silently invent synonyms, overload
a defined term, or introduce a new domain concept in code alone. Proposed vocabulary
changes require Project Steward reconciliation with existing authority.

Files under `docs-temp/` are ignored working notes and are never project authority.
External design drafts and stashed work are not repository authority until the Steward
reconciles them into the files above.

### Authority hierarchy (capture/evidence)

- Product doctrine and lifecycle: `VISION.md`
- Term meanings: `VOCABULARY.md`
- Settled decisions (including D8): `decisions/decisions.md`
- Why the boundary is hard to reverse: `docs/adr/0001-capture-event-evidence-boundary.md`
- Normative implementation contract: `docs/specs/capture-event-v2.md`
- Work cut only: `tickets/`

A ticket says which slice of the contract to build; the spec says what correct means. Where
they disagree, the spec wins and the ticket is defective — stop and report it rather than
implementing either reading.

D5’s original text is preserved for history and is superseded by D8 for the
capture/evidence storage boundary and Outcome-as-history phrasing.

## Roles

- The human product owner owns product purpose, priorities, major trade-offs, final
  decisions, and release approval.
- The Project Steward owns sequencing, architectural coherence, authority maintenance,
  ticket quality, integration, acceptance evidence, and drift control.
- The Project Steward holds no memory between sessions. **Durable** decisions — sequencing,
  acceptance, supersession, and anything a later session would otherwise have to
  re-derive — must be written into this repository when made. Transient judgement is not
  recorded; recording everything would violate D7. Authority on disk is the only continuity
  this project has; Steward recall is not evidence.
- Coding and review agents implement or inspect bounded assignments under the current
  authority and ticket. They do not replace the Project Steward or silently redefine
  project direction.
- Agent findings are inputs. A finding changes the project only after the Project Steward
  reconciles it with existing authority and records any resulting decision.
- No agent may broaden its assignment merely because it discovers adjacent work; report
  the finding and keep the current ticket bounded.

### Agent lanes

- **[GROK]** implements. He is the only agent who writes code and tests. One ticket at a
  time; no ticket, no implementation.
- **[GPT]** is Project Steward and primary reviewer: maintains authority and tickets,
  sequences work, issues bounded prompts, reviews [GROK]'s committed implementation,
  reconciles findings, and records acceptance. Writes no code or tests.
- **[CLAUDE]** has no standing role in the project loop. [CHAZ] may explicitly invite
  Claude or another model for a read-only milestone audit; audit findings are inputs, not
  authority.
- **[CHAZ]** decides. He relays all traffic; agents never contact each other directly.

Every agent may read the whole repository, and [GPT] may run `uv run pytest -q`,
`uv run ruff check .`, and `uv run mypy` against a named implementation commit.
Reviewing an implementer's account of his own work is not an independent check. [GPT] does
not modify `src/` or `tests/`; authority and ticket changes are explicit Steward work.

Only the Steward writes `AGENTS.md`, `VISION.md`, `VOCABULARY.md`, `decisions/`, `docs/`,
and `tickets/` — except that the implementer fills his own assigned ticket's `Start commit`,
`Status` (never `done`), and Implementation report, which travel in his implementation
commit. An agent editing outside its lane has already drifted: stop and report.

This is the whole model. It exists because one unbounded implementation left a broken test
suite, not because the project needs a permissions system. If a real failure exposes a gap,
add the smallest rule that addresses that failure — nothing more.

## Hard boundaries

- Observatory is a standalone observation-data service.
- Every consumer uses the versioned API for data access; never create direct database or
  Evidence Store access for a project, LLM, agent, or script consumer.
- Keep strategy, recommendations, conclusions, scoring, reporting narratives, customer
  overlays, and campaign workflow outside Observatory.
- **Evidence** is committed Attempt and Capture manifests plus body objects on the
  filesystem Evidence Store. PostgreSQL is **not** authoritative Evidence.
- Do not store authoritative Attempt/Capture history or raw request/response bodies as
  PostgreSQL/`BYTEA` source of truth.
- Do not treat Outcome as an Evidence event, Capture substitute, or parent of Evidence.
  Outcome is a derived, versioned classification.
- Lifecycle is Attempt → Capture → derived Outcome → Derivation → Observation → API.
  Do not implement attempt → outcome → observation as if Outcome were the transport
  archive.
- `attempt_id`, `capture_id`, and body addresses are full 64-character lowercase SHA-256
  values—not UUIDs and not truncated digests.
- No fixture or provider transport before a committed Attempt.
- Authorized/unresolved (Attempt without Capture) must not be treated as definitely unsent.
- Partial, no-response, refused, failed, malformed, and unresolved paths must never
  masquerade as Observations.
- Every Observation cites verified `capture_id` and `attempt_id`.
- Preserve immutable Evidence; re-derive rebuildable Outcomes/Observations without
  rewriting events or bodies.
- Never collapse missing, unstated, inapplicable, refused, failed, partial, or malformed
  states.
- Never make real provider network calls from ordinary automated tests. The accepted
  first proof remains fixture-only (`fixture-panel-v1`); provider work is limited by D9–D12
  and the deferred register.
- Never claim fixture or mock success proves real PostgreSQL behavior, Evidence Store
  crash/fsync/commit behavior, concurrency of Attempt authorization, or recovery.
- Ordinary hardlinks from event bundles into the content-addressed object pool are
  forbidden.
- Do not weaken durability to improve development convenience.
- Do not implement capture-event storage against obsolete models (flat payload without
  Capture root, Outcome-as-Evidence-parent, PG-as-Evidence).
- Do not implement deferred work before its recorded trigger fires.

## Work method

- Work from one ticket with observable acceptance criteria.
- Ordinary tests are the default.
- Add a hammer candidate only when the invariant, consequence, and required proof substrate
  can be named (Evidence Store vs PostgreSQL as appropriate under D6/D8).
- Propose an ADR to the Steward only when the choice is hard to reverse, surprising without
  context, and the result of a real trade-off. The Steward writes it.
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
5. `to-tickets` → breakdown proposed to the Steward, who files the result under `tickets/`.
   Only the Steward writes `tickets/`, except for an implementer's own assigned ticket.
6. **Steward acceptance** of the ticket set
7. `implement` → `tdd` → `code-review` → remediation
8. implement sets ticket status to `review` and records evidence; never `done`
9. `handoff` as needed; **Steward closure** sets `done`

Optional and situational: `prototype` (throwaway design question), `wayfinder`
(multi-session decision fog in `docs-temp/wayfinder/` only).

### Commit boundary

The handoff between lanes is a commit, not a working tree.

- Implementation begins from a clean tree at a named commit and ends with one commit. The
  ticket's status change and Implementation report travel inside it. Uncommitted work is
  not delivered work.
- Review starts from that named commit. A red suite never lands — `uv run pytest -q` exits
  0 at every commit on `main`, and a suite that fails to collect is red, not a partial
  pass. Intermediate red states are fine in the working tree and resolved before the
  commit.
- An abandoned assignment leaves no untracked files behind. Record where you stopped in the
  ticket and leave the tree clean.

### Review loop

All agent traffic is relayed by [CHAZ]. No agent contacts another directly.

1. [GPT] (Steward) issues a bounded work prompt naming exactly one ticket.
2. [GROK] implements and returns an implementation report.
3. [CHAZ] relays that report to [GPT].
4. [GPT] reviews the committed code and tests, reconciles the report and findings against
   authority, and accepts the ticket or issues the next bounded prompt through [CHAZ].

[GROK] is the only agent writing the working code, and the only one carrying the working
context of having built it. His judgement on what is weak, fragile, or under-tested is a
first-class input, and every work prompt must solicit it explicitly. This does not make him
the only reader: [GPT] reads the committed code and tests directly when reviewing,
because an implementer's account of their own work cannot be the only evidence.
Such findings are inputs, not authority: they change the project only after the Steward
reconciles them and records the result.

[GPT] asks [GROK] direct questions when an answer is uncertain rather than
assuming. A question relayed through [CHAZ] costs less than a wrong sequencing decision.

Do not create `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/agents/`, `.scratch/`, or external
issue-tracker scaffolding.

## Commands

Repository verification commands:

    uv run pytest -q
    uv run ruff check .
    uv run mypy

Implemented module entrypoints:

    uv run python -m observatory.migrate
    uv run python -m observatory.capture
    uv run python -m observatory.derive
    uv run python -m observatory.evidence status
    uv run python -m observatory.evidence scrub
    uv run python -m observatory.dataforseo_sandbox
    uv run python -m observatory.dataforseo_paid_probe
    uv run python -m observatory.keyword_overview_derive
    uv run python -m observatory.provider_recipe_selection
    uv run python -m observatory.dataforseo_google_organic_paid_probe
    uv run python -m observatory.google_organic_derive
    uv run python -m observatory.serve

Listing an entrypoint does not authorize provider transport, credentials, spend, Evidence
creation, or deferred work. The relevant authority, ticket, and explicit Product Owner
gate still apply.

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
- data, Evidence Store, and API boundary rules remain intact;
- the exact unproven limits are stated;
- authority docs changed only if the ticket made a real decision.
