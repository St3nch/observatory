# OPS-01 — Machine-enforced lane and commit guardrail

**Status:** ready-for-agent
**Parent spec:** None — governed by `AGENTS.md` §Agent lanes and §Commit boundary
**Kind:** tooling guardrail (not Capture Event behaviour)
**Blocked by:** None technically — but sequenced after CE-02 (see §Sequencing)
**Approved by:** Project Steward
**Start commit:**

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
- Decision functions are pure: they take staged paths, the commit message, the suite
  result, **and the set of ticket filenames currently present under `tickets/`** as
  arguments, and return a verdict. They do not shell out and do not read the filesystem.
  Only the hook shims touch Git, enumerate `tickets/`, and run the suite, so every rule is
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

**pre-commit**

1. Run `uv run pytest -q`. Any non-zero exit refuses the commit. A collection error is a
   failure, not a partial pass.
2. If staged paths touch `src/` or `tests/`, and also touch any authority-set path
   (`AGENTS.md`, `VISION.md`, `VOCABULARY.md`, `decisions/`, `docs/`), refuse: authority
   and implementation do not travel in one commit. **`tickets/` is deliberately excluded**
   — the assigned ticket's status fields and Implementation report are required to travel
   with the implementation commit, per `AGENTS.md` §Agent lanes.

**commit-msg**

3. Require a `Ticket:` trailer. The value is either a filename that exists under
   `tickets/`, or the literal `none`. **`Ticket: none` is refused when staged paths touch
   `src/` or `tests/`** — no ticket ID means no implementation work, per `AGENTS.md`
   §Agent lanes. It is accepted only for authority, tooling, and documentation commits.
4. Require an `Agent:` trailer whose value is one of `grok`, `steward`.
5. If staged paths touch `src/` or `tests/`, `Agent:` must be `grok`. Any other permitted
   value is refused — this is the rule that would have caught the drift incident.

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
- [ ] A commit touching only `docs/` with `Ticket: none` and `Agent: steward` succeeds.
- [ ] A commit is refused while `uv run pytest -q` exits non-zero, including when the cause is an import or collection error rather than an assertion.
- [ ] A commit mixing `src/` or `tests/` with any authority-set path is refused; a commit pairing `src/` with the assigned ticket succeeds.
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
