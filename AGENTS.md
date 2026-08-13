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

D5’s original text is preserved for history and is superseded by D8 for the
capture/evidence storage boundary and Outcome-as-history phrasing.

## Roles

- The human product owner owns product purpose, priorities, major trade-offs, final
  decisions, and release approval.
- The Project Steward owns sequencing, architectural coherence, authority maintenance,
  ticket quality, integration, acceptance evidence, and drift control.
- The Project Steward holds no memory between sessions. Every decision, sequencing choice,
  and acceptance judgement must be written into this repository when it is made. Authority
  on disk is the only continuity this project has; Steward recall is not evidence.
- Coding and review agents implement or inspect bounded assignments under the current
  authority and ticket. They do not replace the Project Steward or silently redefine
  project direction.
- Agent findings are inputs. A finding changes the project only after the Project Steward
  reconciles it with existing authority and records any resulting decision.
- No agent may broaden its assignment merely because it discovers adjacent work; report
  the finding and keep the current ticket bounded.

### Agent lanes

| Agent | Lane | May write | May read |
|---|---|---|---|
| Grok | Implementer | `src/`, `tests/`, and the assigned ticket's Implementation report | everything |
| Claude | Project Steward | authority documents, `tickets/`, `decisions/`; never `src/` or `tests/` | everything |
| GPT and any other agent | Reviewer | nothing in the repository; findings are reported to the Steward | everything |

**Every agent may read the entire repository.** Read access is not a lane. A reviewer who
cannot open the code cannot distinguish a test that proves a criterion from one that merely
appears to, and a review built only on an implementer's own account of their work is not an
independent check.

Reviewers may also run non-mutating verification against a named commit — `uv run pytest
-q`, `uv run ruff check .`, `uv run mypy`, and read-only Git inspection. A reviewer must not
commit, must not modify tracked files, and must report rather than repair if the working
tree is dirty or the suite is red.

Grok is the sole implementer. The Steward role is an authority role, not an implementation
lane: the Steward sequences, maintains authority, judges ticket quality and acceptance
evidence, and sets `done` — but does not write `src/` or `tests/` under any circumstance.

A review agent that concludes code is required stops and
reports the finding; it does not write, patch, or "just fix" `src/` or `tests/`, and it
does not repair a broken build it happens to notice. An agent editing files outside its
lane has already drifted—stop and report instead.

An agent works under exactly one ticket ID at a time. No ticket ID means no implementation
work. Every skill invocation reports the absolute path of the project-local `SKILL.md` it
loaded and the ticket ID it is working under.

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
- Never make real provider network calls from ordinary automated tests. First
  implementation remains fixture-only (`fixture-panel-v1`).
- Never claim fixture or mock success proves real PostgreSQL behavior, Evidence Store
  crash/fsync/commit behavior, concurrency of Attempt authorization, or recovery.
- Ordinary hardlinks from event bundles into the content-addressed object pool are
  forbidden.
- Do not weaken durability to improve development convenience.
- Do not implement capture-event storage against obsolete models (flat payload without
  Capture root, Outcome-as-Evidence-parent, PG-as-Evidence).
- Do not implement deferred work (F1–F10) before its recorded trigger fires.

## Work method

- Work from one ticket with observable acceptance criteria.
- Ordinary tests are the default.
- Add a hammer candidate only when the invariant, consequence, and required proof substrate
  can be named (Evidence Store vs PostgreSQL as appropriate under D6/D8).
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

### Commit boundary

The handoff between lanes is a commit, not a working tree.

- `implement` ends with a commit. Uncommitted work is not delivered work, and a ticket is
  never moved to `review` from a dirty tree.
- `code-review` starts from a named commit and refuses to review uncommitted work.
- Before any ticket status changes: `git status` is clean and `uv run pytest -q` exits 0.
  A suite that fails to collect is a red suite, not a partial pass.
- An abandoned or interrupted assignment leaves no untracked files behind. Record the
  stopping point in the ticket's Implementation report and leave the tree clean.
- A ticket's **Start commit** is stamped when implementation actually begins, and names the
  commit the work started from.

Optional and situational: `prototype` (throwaway design question), `wayfinder`
(multi-session decision fog in `docs-temp/wayfinder/` only).

### Review loop

All agent traffic is relayed by [CHAZ]. No agent contacts another directly.

1. [CLAUDE] (Steward) issues a bounded work prompt naming exactly one ticket.
2. [GROK] implements and returns an implementation report.
3. [CHAZ] relays that report to [GPT], who returns a review.
4. [CHAZ] relays [GROK]'s report, then [GPT]'s review, to [CLAUDE].
5. [CLAUDE] reconciles both against authority and issues the next prompt or accepts the
   ticket.

[GROK] is the only agent writing the working code, and the only one carrying the working
context of having built it. His judgement on what is weak, fragile, or under-tested is a
first-class input, and every work prompt must solicit it explicitly. This does not make him
the only reader: [GPT] and [CLAUDE] read the committed code and tests directly when
reviewing, because an implementer's account of their own work cannot be the only evidence.
Such findings are inputs, not authority: they change the project only after the Steward
reconciles them and records the result.

[CLAUDE] asks [GROK] or [GPT] direct questions when an answer is uncertain rather than
assuming. A question relayed through [CHAZ] costs less than a wrong sequencing decision.

Do not create `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/agents/`, `.scratch/`, or external
issue-tracker scaffolding.

## Commands

Intended repository commands as modules exist:

    uv run pytest -q
    uv run ruff check .
    uv run mypy
    uv run python -m observatory.migrate
    uv run python -m observatory.capture
    uv run python -m observatory.derive
    uv run python -m observatory.evidence status
    uv run python -m observatory.evidence scrub

Migration, capture, derivation, and evidence commands remain placeholders until
implemented.

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
