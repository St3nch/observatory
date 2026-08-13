# CE-03 — Evidence Store foundation: format, durable install, commit and read

**Status:** ready-for-agent
**Parent spec:** docs/specs/capture-event-v2.md
**Kind:** necessary prefactor
**Blocked by:** CE-02 — Canonical JCS, closed schemas, and content-ID vectors
**Approved by:** Project Steward
**Start commit:**

## What to build

End-to-end behaviour this ticket makes work: create and open a format-2 Evidence Store, and
durably commit, read, and verify a Capture Event bundle under the committed durability
protocol — such that a partial or unverifiable bundle is never admitted as Evidence and a
tampered committed event fails closed.

This ticket builds the **store mechanism only**. It performs no fixture transport, builds no
documents from the fixture algorithm, and ships no CLI. Bundles under test are constructed
directly from CE-02's document builders using published AR vector inputs.

CE-03B consumes this to produce the first real vertical capture.

## Authority

- `docs/specs/capture-event-v2.md` — §FORMAT.json (exact bytes and digest)
- `docs/specs/capture-event-v2.md` — §Paths and bundles
- `docs/specs/capture-event-v2.md` — §Commit visibility, and §Durability profile
  `local-posix-fsync-v1` D1–D7 including D4a (D8 belongs to CE-03B)
- `docs/specs/capture-event-v2.md` — §Canonicalization and verify-on-read (the six-step
  sequence that D5 invokes)
- `decisions/decisions.md` — D8 (FS Evidence; verify-on-read; no ordinary hardlinks;
  COMMITTED)
- `docs/adr/0001-capture-event-evidence-boundary.md` — Evidence Store boundary

## Scope

- FORMAT-2 create/open; fail-closed validation of exact FORMAT bytes and digest; `.tmp/`
  purge on open
- Path and sharding rules for objects, attempts, captures
- Object pool install with digest and byte-count verification
- Bundle body materialization by independent copy or COW reflink; no ordinary hardlinks
  into the pool
- The committed durability protocol D1–D7 exactly: temp write, file fsync, `link(2)`
  exclusive install, temp unlink, directory fsync; parent-first durable directory creation;
  `EEXIST` handling by kind; bundle commit order with `COMMITTED` last; commit point versus
  durability window; verify-after-commit; reading rules
- Verify-on-read of committed events, and tamper detection

## Out of scope

- Fixture transport of any scenario, and the fixture response-construction algorithm
- D8 no-transport-before-durable-Attempt — CE-03B
- Capture CLI — CE-03B
- Derive, PostgreSQL, HTTP API, status/scrub CLIs
- Multi-process locking (F7), off-host backup (F6), paid providers (F3)
- Crash-recovery, power-loss, or hardware claims beyond the protocol under test

## Acceptance criteria

- [ ] A format-2 root can be created and opened; FORMAT exact JCS bytes (no trailing newline) and SHA-256 `67fb338d3237a22a29f50110c705e552cd9af29f830c1bfffa9ee1cafa876c7e` are enforced.
- [ ] Missing, malformed, noncanonical, unsupported, or conflicting FORMAT fails closed on open **with nothing modified**; `.tmp/` is purged only after FORMAT validation succeeds, per D7.
- [ ] Bundles built from published AR vector inputs land at format-2 paths; date components derive only from Attempt `authorized_at`.
- [ ] Request and response bodies are content-addressed; digests and sizes verify in both the pool object and the bundle body file.
- [ ] Each of D1, D2, D3, D4, D4a, D5, D6, D7 has at least one named test. `link(2)` is used for exclusive install and `rename(2)` is not used to install. Bundle body files have link count 1 after a store open and do not share an inode with their pool object. A pool object recurring at an existing path is verified and accepted; a mismatching one fails closed. Shared path directories recur without error; a terminal event bundle directory that already exists fails closed.
- [ ] A bundle lacking `COMMITTED` is ignored rather than erroring; a bundle with `COMMITTED` that fails verification is reported as an integrity failure.
- [ ] Verify-on-read runs the full six-step sequence from §Canonicalization and verify-on-read, not a reduced form.
- [ ] Bit-flip of a committed manifest, a pool object, or a bundle body file fails closed.

## Verification

- Commands: `uv run pytest -q`; `uv run ruff check .`; `uv run mypy`
- Substrate: real local POSIX temporary Evidence roots. Mocked or faked filesystems prove
  nothing here and must not be claimed as substrate.
- Forbidden claims: tests prove the committed durability **protocol** under the supported
  profile — not arbitrary power-loss, multi-filesystem, concurrent-writer, or hardware
  guarantees

## Required automated tests

- FORMAT create, open, and each fail-closed case; a failed open leaves `.tmp/` untouched;
  `.tmp/` purged only after successful validation
- Path layout and sharding for AR-derived events
- Pool object install, digest and size verification, recurrence accepted, mismatch fails
  closed
- Exclusive install via `link(2)`; occupied final path fails closed
- Shared ancestor directory recurrence; terminal bundle directory `EEXIST` fails closed
- Bundle body materialization: no shared inode with the pool object; link count 1
- `COMMITTED`-last ordering; uncommitted bundle ignored
- Verify-after-commit runs the full six-step sequence
- Tamper: manifest, pool object, and bundle body file each fail closed

## Forbidden claims

- Any fixture transport, scenario, or capture behaviour
- Attempt-before-transport ordering (CE-03B)
- PostgreSQL, API, derive, scrub
- Off-host recovery or multi-process writer safety

## One implementation commit must prove

A format-2 Evidence Store can durably commit, read, and verify an event bundle under the
committed protocol, fails closed on tamper, and never admits partial state after interruption
— without needing later tickets for that claim to be true.

## Later tickets

Later tickets are **not** required to make this ticket's acceptance criteria truthful.

## Beyond authority

This ticket adds **no** behavior beyond committed authority.

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
