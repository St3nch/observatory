# Observatory Agent Instructions

## Authority

Read in this order:

1. `VISION.md`
2. `VOCABULARY.md`
3. `decisions/decisions.md`
4. `decisions/deferred.md`
5. `docs/dataforseo-surface-roadmap.md` when the work touches a DataForSEO provider
   surface, Derivation, typed provider schema, or provider read API
6. Relevant ticket under `tickets/`
7. Relevant ADR under `docs/adr/`, when one exists
8. Normative capture/evidence contract: `docs/specs/capture-event-v2.md` when the work
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

- **[GROK]** implements when designated for a ticket. One ticket at a time; no ticket, no
  implementation.
- **[GPT]** is Project Steward and primary reviewer: maintains authority and tickets,
  sequences work, issues bounded prompts, reviews the designated implementer's committed
  implementation,
  reconciles findings, and records acceptance. Writes no code or tests.
- **[CLAUDE]** may implement when [CHAZ] explicitly designates Claude for a ticket, under
  the same ticket, start-commit, review, and bounded-assignment rules as [GROK]. Otherwise
  [CHAZ] may invite Claude or another model for a read-only milestone audit; audit findings
  are inputs, not authority.
- Exactly one of **[GROK]** or **[CLAUDE]** is the implementation writer for a ticket.
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
- A provider-surface, Derivation-schema, or read-API ticket is defective unless it states
  the downstream consumer questions, fact and relationship grain, completeness/absence/limit
  semantics, provenance and Recipe disclosure, and inference traps. This consumer-readiness
  review must not move strategy, scoring, recommendations, panels, or cadence into Observatory.
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
6. **Steward provisional acceptance** of one bounded ticket for technical review
7. **Designated implementer read-only pre-implementation ticket review** → false premises, missing proofs,
   overconstraints, architecture/provider traps, consumer-readiness gaps for applicable
   provider/schema/API work, and ready-or-reconcile recommendation; no implementation or
   repository mutation
8. **Steward reconciliation and final ticket acceptance** → commit the reviewed ticket and
   issue the exact implementation start commit
9. `implement` → `tdd` → `code-review` → remediation
10. implement sets ticket status to `review` and records evidence; never `done`
11. `handoff` as needed; **Steward closure** sets `done`

### Question-resolution gate

Before any major provider-surface review, ticket review, remediation, or implementation
prompt:

1. **Designated implementer code-first questions** — inspect the actual authority, code, schema, tests, and
   Evidence boundary, then return uncertainties and coworker questions without mutation.
2. **[GPT] consolidation** — independently verify the material premises, remove answered or
   duplicate questions, and separate Steward technical judgments from Product choices.
3. **[CHAZ] Product resolution** — answer spending, scope, consumer meaning, live-provider,
   and other Product questions before the major prompt is drafted.
4. **Bounded [GROK] reaction when needed** — explain technical consequences of CHAZ's
   answers without reopening settled Product direction or expanding the task.
5. **[GPT] decision lock** — reconcile the answers into authority or the accepted work
   boundary, then issue one major prompt with those decisions embedded.

Questions discovered during major work are resolved before remediation, implementation
expansion, or closure. Do not repeatedly rewrite large prompts around unresolved choices,
bury CHAZ-directed questions inside an implementation report, or treat a coworker question
as authorization.

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

1. [GPT] (Steward) prepares one bounded draft ticket.
2. Before implementation, the designated implementer performs a read-only adversarial ticket review and reports
   false premises, missing acceptance proofs, overconstraints, likely false greens,
   architecture/provider traps, and whether the ticket is ready or needs reconciliation.
3. [CHAZ] relays that review to [GPT].
4. [GPT] reconciles the findings, updates and commits the final accepted ticket, and issues
   a bounded implementation prompt naming its exact start commit.
5. The designated implementer implements and returns an implementation report.
6. [CHAZ] relays that report to [GPT].
7. [GPT] reviews the committed code and tests, reconciles the report and findings against
   authority, and accepts the ticket or issues the next bounded prompt through [CHAZ].

The designated implementer is the only agent writing the working code for that ticket and
the only one carrying the working context of having built it. That implementer's judgement on what is weak, fragile, or under-tested is a
first-class input. Every implementation report must candidly state the strongest and weakest
parts, possible false greens, remaining caller influence, architecture drift/coupling,
parser/provider traps, closure blockers, deferred work, what later surfaces should reuse,
and what should deliberately remain duplicated. When the work exposes provider testimony,
the report also distinguishes Evidence, claimed contract, synthetic proof, recommendation,
and unproven inference, and assesses useful/not-useful future strategy and data-model
implications without implementing strategy or broadening scope.

This does not make [GROK] the only reader: [GPT] reads the committed code and tests directly
when reviewing, because an implementer's account of their own work cannot be the only
evidence. Such findings are inputs, not authority: they change the project only after the
Steward reconciles them and records the result.

[GPT] treats the designated implementer as a coworker and asks direct bounded questions when an answer is
uncertain or the implementer's context can materially improve judgement. Questions do not
transfer Steward or Product Owner authority. A question relayed through [CHAZ] costs less
than a wrong sequencing decision.

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
    uv run python -m observatory.dataforseo_ai_optimization_search_mentions_paid_probe
    uv run python -m observatory.dataforseo_ai_optimization_target_metrics_paid_probe
    uv run python -m observatory.dataforseo_ai_optimization_llm_mentions_historical_paid_probe
    uv run python -m observatory.target_metrics_derive
    uv run python -m observatory.llm_mentions_historical_derive
    uv run python -m observatory.dataforseo_google_related_keywords_paid_probe
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

## Automated development orchestration

This section supersedes the earlier global one-writer-at-a-time and mandatory-human-relay
coordination sentences where they conflict with the rules below.

- One finally accepted ticket has exactly one designated Writer, either [GROK] or [CLAUDE].
  The same Writer owns remediation unless the Steward explicitly abandons/reassigns it.
- The Steward may run multiple tickets concurrently only when dependency order and
  changed-path boundaries are parallel-safe; each Writer uses a separate branch/worktree.
- Read-only recon/review workers may fan out concurrently but never become additional Writers.
- GitHub/repository state may relay bounded execution/review traffic; CHAZ is not required
  to copy/paste routine messages. Agent traffic cannot create Product or Steward authority.
- Headless Grok Build may start only from a final accepted ticket and exact Steward start
  commit, in an isolated worktree, with bounded permissions. No autonomous merge/main push.
- Provider/DNS/credential/spend/Evidence/production-DB boundaries remain separately gated.
- [GPT] reviews committed diffs/check evidence but does not execute repository tests through
  MCP; the Writer runs ticket-scoped checks and CHAZ supplies final full-suite validation.
- Development concurrency is not F7 capture-writer safety or F12 acquisition orchestration.

This supersession is process governance only; it does not change Observatory product semantics.
