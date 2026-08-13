# OPS-01 — Machine-enforced lane and commit guardrail

**Status:** deferred
**Parent spec:** None — governed by `AGENTS.md` §Agent lanes and §Commit boundary
**Kind:** tooling guardrail (not Capture Event behaviour)
**Blocked by:** Deferred by Steward decision — see §Deferral below
**Approved by:** Project Steward
**Start commit:**

## Deferral

**Deferred 2026-08-13. Do not implement without an explicit Steward decision reversing
this.**

This ticket was written to mechanize the lane rules after a drift incident. Designing it
consumed three review rounds and produced no product behaviour, while Observatory still has
one passing test. That is a worse outcome than the risk it addresses. The human-relayed
review loop already catches the failure this was meant to catch.

**Trigger to revisit:** a second real drift incident that the review loop failed to catch.
At that point, build the smallest guardrail that addresses that specific failure — probably
not this whole ticket.

The design below is preserved because the analysis was expensive and the defects found in
it (ticket inventory must come from the resulting commit; hooks cannot import `src/guardrail`
via pytest's `pythonpath`; a lane test must use a valid agent value or it proves nothing)
are real and would be rediscovered otherwise. Treat it as research, not as approved work.

## What to build

End-to-end behaviour this ticket makes work: once `core.hooksPath` is configured on a
machine, a commit made there through ordinary `git commit` is refused when it violates the
lane rules or the commit boundary in `AGENTS.md`.

That claim is deliberately narrow. It does not extend to machines where the hook path is
unset, to `git commit --no-verify`, or to any push, server, or CI path. Local hooks stop
drift and accident, not determination.

Today those rules are prose. Nothing enforces them. A drift incident before CE-02 produced
a red suite and orphaned implementation files that sat undetected because no mechanism
looked.

## Sequencing

Steward decision, recorded here rather than in `decisions/` because it is process rather
than architecture:

- **CE-02 runs before OPS-01.** The relayed review loop in `AGENTS.md` §Review loop is
  itself drift control, human-mediated at every hop, which lowers this ticket's urgency.
  CE-02 is also the first ticket producing real product behaviour, and the owner's working
  time is limited.
- **Ticket-status parsing rules were cut to OPS-02.** Guards on `Status: done` and
  `Status: review` require parsing ticket markdown — the fiddliest part of the build and
  the furthest from the failure that motivated this ticket. The rules below catch that
  failure. The rest is hygiene and can wait.

## Authority

- `AGENTS.md` — §Agent lanes (three path groups: core authority, `tickets/`, implementation
  paths; Grok is sole implementer; the Steward writes core authority and tickets)
- `AGENTS.md` — §Commit boundary (implementation begins from a clean tree at a named commit
  and ends with one commit; the assigned ticket travels inside it; `uv run pytest -q` must
  exit 0 at every commit on `main`)
- `AGENTS.md` — §Review loop (relayed traffic; no direct agent-to-agent contact)
- `decisions/decisions.md` — D7 (working restraint; no sprawl)

## Scope

- `src/guardrail/` — a pure, importable module holding all decision logic
- `.githooks/pre-commit` and `.githooks/commit-msg` — thin shims that call the module
- Commit trailer grammar: `Ticket:` and `Agent:`
- Automated tests for every rule at `tests/test_guardrail.py`
- A short §Guardrail section appended to `README.md` covering the one-time
  `git config core.hooksPath .githooks` enablement

## Out of scope

- CI, server-side hooks, or any remote enforcement
- Ticket-status parsing guards — deferred to OPS-02
- Capture Event behaviour of any kind; no `src/observatory/` changes
- Agent identity verification (the `Agent:` trailer is self-declared, not authenticated)
- Rewriting or enforcing history that already exists

## Design constraints

- All decision logic lives in `src/guardrail/`. Hooks contain no logic beyond reading
  input and calling in.
- Hatch packages only `src/observatory`, so `src/guardrail/` must not be imported by the
  service and must not appear in the wheel.
- mypy runs `strict` over `src` and `tests`; the module is fully annotated.
- Decision functions are pure: they take staged paths, the commit message, the suite
  result, **and the ticket inventory of the resulting commit** (see §Ticket inventory) as
  arguments, and return a verdict. They do not shell out and do not read the filesystem.
  Only the hook shims touch Git, compute the inventory, and run the suite, so every rule is
  unit-testable without making commits.
- **The hooks must be able to import `src/guardrail` at hook runtime.** `pythonpath =
  ["src"]` in `pyproject.toml` is pytest configuration only, and hatch packages just
  `src/observatory`, so the module is not installed into the environment. The hook shims
  run as ordinary processes outside pytest and will not find it by default. Choose and
  document an explicit import seam — setting `PYTHONPATH`, invoking through
  `uv run python -m`, or another mechanism. A test suite that imports the module while the
  real hook cannot is a false pass, and one acceptance criterion below exists to catch it.
- The hook must stay fast. The suite currently runs in well under a second on a warm cache;
  if it ever exceeds roughly five seconds, report that rather than adding a skip flag.

## Rules to enforce

All rules classify staged paths into the three groups defined in `AGENTS.md` §Agent lanes:
**core authority** (`AGENTS.md`, `VISION.md`, `VOCABULARY.md`, `decisions/`, `docs/`),
**`tickets/`**, and **implementation paths** (everything else tracked). Classification is
by group, never by a hardcoded `src/`-and-`tests/` shortcut — the implementer's lane
extends to tooling and configuration, and a shortcut would silently permit ticketless work
there.

**pre-commit**

1. Run `uv run pytest -q`. Any non-zero exit refuses the commit, whoever is committing and
   whatever the staged paths. A collection error is a failure, not a partial pass. This
   matches `AGENTS.md` §Commit boundary, which requires a green suite at every commit on
   `main`.
2. If staged paths include any implementation path **and** any core-authority path, refuse:
   authority and implementation do not travel in one commit. `tickets/` is deliberately
   excluded — the assigned ticket is required to travel with the implementation commit.

**commit-msg**

3. Require a `Ticket:` trailer. The value is either a ticket filename present in the
   **resulting commit** (see §Ticket inventory) or the literal `none`. **`Ticket: none` is
   refused when staged paths include any implementation path** — no ticket ID means no
   implementation work, per `AGENTS.md` §Agent lanes. It is accepted for commits touching
   only core authority, only `tickets/`, or both.
4. Require an `Agent:` trailer whose value is one of `grok`, `steward`.
5. If staged paths include any implementation path, `Agent:` must be `grok`. `steward` is
   refused — this is the rule that would have caught the drift incident.
6. If staged paths include any core-authority path, `Agent:` must be `steward`.
7. When `Ticket:` names a ticket and staged paths include anything under `tickets/`, the
   staged ticket paths must be exactly that one ticket. Staging a second ticket, or a
   different ticket than the trailer names, is refused.

## Ticket inventory

The inventory a decision function receives is the set of ticket filenames that will exist
in the **resulting commit** — the tickets at `HEAD`, plus staged additions, minus staged
deletions. It is **not** a listing of the working directory.

This distinction is load-bearing. An untracked, unstaged `tickets/FAKE.md` would satisfy a
working-directory listing, validate a `Ticket: FAKE.md` trailer, and then be absent from
the commit entirely — leaving a commit that references a ticket no reviewer can find.

## Trailer grammar

Fixing this is part of the ticket, not left to the implementer's judgement:

- `Ticket:` takes the **bare filename** as it appears under `tickets/`, including the `.md`
  extension and excluding any directory prefix — for example
  `Ticket: CE-02-jcs-schemas-content-ids.md`. A bare ID (`CE-02`) or a path
  (`tickets/CE-02-…md`) is malformed and refused.
- Trailers appear one per line, `Key: value`, case-sensitive keys, in the commit message
  body. Leading and trailing whitespace around the value is stripped.
- A duplicated `Ticket:` or `Agent:` trailer is refused rather than resolved by precedence.

## Acceptance criteria

- [ ] With `core.hooksPath` set, a commit touching `src/` with `Agent: steward` and an otherwise valid `Ticket:` trailer is refused, and the refusal names Rule 5. `steward` is used deliberately: it is a permitted value, so the refusal can only come from the lane rule and not from trailer validation.
- [ ] A commit touching `src/` with `Agent: grok` and a valid `Ticket:` trailer succeeds.
- [ ] A commit touching `src/` with `Ticket: none` and `Agent: grok` is refused by Rule 3.
- [ ] A commit touching **only `README.md`** with `Agent: steward`, `Ticket: none` is refused. `README.md` is an implementation path, so this proves classification is by path group and not by an `src/`-and-`tests/` shortcut.
- [ ] A commit touching **only `.githooks/`** with `Agent: grok`, `Ticket: none` is refused by Rule 3.
- [ ] A commit touching only `AGENTS.md` with `Agent: grok` is refused by Rule 6.
- [ ] A commit staging an implementation path plus **two** ticket files is refused by Rule 7; so is one whose staged ticket differs from the `Ticket:` trailer.
- [ ] An untracked, unstaged `tickets/FAKE.md` does **not** validate `Ticket: FAKE.md`; the inventory is the resulting commit, not the working directory.
- [ ] A commit touching only `docs/` with `Ticket: none` and `Agent: steward` succeeds.
- [ ] A commit is refused while `uv run pytest -q` exits non-zero, including when the cause is an import or collection error rather than an assertion, and including an authority-only Steward commit with no ticket status change.
- [ ] A commit mixing an implementation path with a core-authority path is refused; a commit pairing `src/` with the assigned ticket succeeds.
- [ ] Malformed `Ticket:` values are refused: bare ID, path-prefixed, unknown filename, duplicated trailer.
- [ ] A missing or unknown-valued `Agent:` trailer is refused.
- [ ] **The installed hook actually imports `src/guardrail` when Git invokes it** — demonstrated by a real refused commit, not only by a passing unit test.
- [ ] Every rule has a unit test exercising the pure decision function directly, with no real commit and no subprocess.
- [ ] `uv run ruff check .` and `uv run mypy` pass with the new module included.
- [ ] `README.md` documents the one-time enablement command and states that `--no-verify` bypasses the hooks.

## Verification

- Commands: `uv run pytest -q`; `uv run ruff check .`; `uv run mypy`
- Substrate: ordinary unit tests against pure functions, plus manual confirmation that the
  hooks fire once `core.hooksPath` is set
- Forbidden claims: no proof of enforcement against a determined actor; no CI or
  server-side coverage; no claim that agent identity is verified

## Required automated tests

- Path-group classification: core authority, `tickets/`, implementation paths; nested
  paths, renames, and the tooling files that are implementation paths without being
  `src/` or `tests/` (`README.md`, `.githooks/`, `pyproject.toml`, `.gitignore`)
- Lane violation: implementation paths with `Agent: steward`
- Lane pass: implementation paths with `Agent: grok` and a valid ticket
- Core-authority paths with `Agent: grok` refused
- Ticketless implementation refused, for `src/` and for tooling paths alike
- Suite-red refusal, including the collection-error case and an authority-only commit
- Mixed implementation-plus-core-authority refusal; implementation-plus-assigned-ticket pass
- Staged-ticket agreement: two tickets staged, and a staged ticket differing from the
  trailer
- Ticket inventory drawn from the resulting commit, not the working directory: an
  untracked `tickets/FAKE.md` does not validate
- Trailer grammar: missing, malformed, unknown value, unknown ticket, duplicated, `none`

## Forbidden claims

- That the guardrail cannot be bypassed. `git commit --no-verify` defeats every hook here,
  and that is acknowledged, not solved.
- That the `Agent:` trailer proves who wrote the commit. It is self-declared.
- Any Capture Event, Evidence, durability, or API behaviour.

## One implementation commit must prove

On a machine with `core.hooksPath` configured, an ordinary `git commit` that violates a
lane rule or arrives with a red suite is refused by the installed hook, the installed hook
resolves its own imports, and every rule is covered by a unit test — without any later
ticket. Nothing beyond that configured-local-hook substrate is proven.

## Later tickets

Later tickets are **not** required to make this ticket's acceptance criteria truthful.
OPS-02 (ticket-status guards) is a follow-up, not a dependency.

## Beyond authority

This ticket adds **no** behaviour beyond committed authority. It mechanizes rules already
recorded in `AGENTS.md` §Agent lanes and §Commit boundary.

## Implementation report

<!-- implement fills; may set Status: review; never Status: done -->

- End commit:
- Acceptance evidence:
- Unproven limits:
- Review findings remaining:

## Closure

<!-- Project Steward only -->

- Closed at commit:
- Evidence accepted: yes/no
