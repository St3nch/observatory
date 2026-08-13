# OPS-01 — Machine-enforced lane and commit guardrail

**Status:** ready-for-agent
**Parent spec:** None — governed by `AGENTS.md` §Agent lanes and §Commit boundary
**Kind:** tooling guardrail (not Capture Event behaviour)
**Blocked by:** None technically — but sequenced after CE-02 (see §Sequencing)
**Approved by:** Project Steward
**Start commit:**

## What to build

End-to-end behaviour this ticket makes work: a commit that violates the lane rules or the
commit boundary in `AGENTS.md` is refused by Git itself, on this machine, without anyone
reading a document first.

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
  the furthest from the failure that motivated this ticket. Rules 1–5 below catch that
  failure. The rest is hygiene and can wait.

## Authority

- `AGENTS.md` — §Agent lanes (Grok is sole implementer; Claude is Steward; neither the
  Steward nor any review agent writes `src/` or `tests/`)
- `AGENTS.md` — §Commit boundary (implement ends with a commit; clean status and green
  suite before any ticket status change)
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

- All decision logic lives in `src/guardrail/`, importable under the existing
  `pythonpath = ["src"]`. Hooks contain no logic beyond reading input and calling in.
- Hatch packages only `src/observatory`, so `src/guardrail/` must not be imported by the
  service and must not appear in the wheel.
- mypy runs `strict` over `src` and `tests`; the module is fully annotated.
- Decision functions are pure: they take staged paths, a commit message, and a suite
  result as arguments and return a verdict. They do not shell out. Only the hook shims
  touch Git or run the suite, so every rule is unit-testable without making commits.
- The hook must stay fast. The suite currently runs in well under a second; if it ever
  exceeds roughly five seconds, report that rather than adding a skip flag.

## Rules to enforce

**pre-commit**

1. Run `uv run pytest -q`. Any non-zero exit refuses the commit. A collection error is a
   failure, not a partial pass.
2. If staged paths touch `src/` or `tests/`, and also touch any of `docs/`, `decisions/`,
   `VISION.md`, `VOCABULARY.md`, or `AGENTS.md`, refuse: authority and implementation do
   not travel in one commit.

**commit-msg**

3. Require a `Ticket:` trailer naming a file that exists under `tickets/`, or the literal
   `Ticket: none` for authority-only and tooling commits.
4. Require an `Agent:` trailer whose value is one of `grok`, `steward`.
5. If staged paths touch `src/` or `tests/`, `Agent:` must be `grok`. Any other value is
   refused — this is the rule that would have caught the drift incident.

## Acceptance criteria

- [ ] With `core.hooksPath` set, a commit touching `src/` with `Agent: claude` is refused, and the refusal message names the violated rule.
- [ ] A commit touching `src/` with `Agent: grok` and a valid `Ticket:` trailer succeeds.
- [ ] A commit is refused while `uv run pytest -q` exits non-zero, including when the cause is an import or collection error rather than an assertion.
- [ ] A commit mixing `src/` or `tests/` with any authority path is refused.
- [ ] A missing, malformed, or unknown-valued `Ticket:` or `Agent:` trailer is refused.
- [ ] A `Ticket:` trailer naming a file absent from `tickets/` is refused; `Ticket: none` is accepted.
- [ ] Every rule above has a unit test that exercises the pure decision function directly, with no real commit and no subprocess.
- [ ] `uv run ruff check .` and `uv run mypy` pass with the new module included.
- [ ] `README.md` documents the one-time enablement command.

## Verification

- Commands: `uv run pytest -q`; `uv run ruff check .`; `uv run mypy`
- Substrate: ordinary unit tests against pure functions, plus manual confirmation that the
  hooks fire once `core.hooksPath` is set
- Forbidden claims: no proof of enforcement against a determined actor; no CI or
  server-side coverage; no claim that agent identity is verified

## Required automated tests

- Lane violation: implementation paths with a non-`grok` agent
- Lane pass: implementation paths with `grok`
- Suite-red refusal, including the collection-error case
- Mixed authority-plus-implementation refusal
- Trailer grammar: missing, malformed, unknown value, unknown ticket, `none`
- Path classification boundaries (e.g. `tests/` versus `docs/`, nested paths, renames)

## Forbidden claims

- That the guardrail cannot be bypassed. `git commit --no-verify` defeats every hook here,
  and that is acknowledged, not solved.
- That the `Agent:` trailer proves who wrote the commit. It is self-declared.
- Any Capture Event, Evidence, durability, or API behaviour.

## One implementation commit must prove

A lane-violating or suite-red commit is refused by Git on this machine, and every rule is
covered by a unit test, without any later ticket.

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
