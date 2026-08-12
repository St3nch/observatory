# Capture-event Evidence boundary

**Status:** accepted
**Decision register:** D8
**Normative contract:** `docs/specs/capture-event-v2.md`

Observatory’s irreplaceable history is the authorized request and transport testimony for
each capture, not a normalized observation row and not a derived classification. The
clean rebuild therefore places authoritative Evidence on a local POSIX filesystem
**Evidence Store** (store format 2): immutable **Attempt** events committed before
transport, immutable **Capture** events committed after transport (at most one Capture per
Attempt), content-addressed body objects, `COMMITTED`-last visibility, verify-on-read, and
no-overwrite durable installs. **PostgreSQL** holds rebuildable **Outcomes** and
**Observations** only and must not be required to recover original testimony. **Outcome**
is a versioned derived classification, never an Evidence event or parent of Evidence.

This boundary is hard to reverse once paid or otherwise irreplaceable captures accumulate.
It is surprising without context because many systems would store request/response bytes
in the database. It is a real trade-off: filesystem commit discipline, scrub, and
operator protection of the Evidence root in exchange for disposable query stores and
honest re-derivation.

## Considered options

| Option | Result |
|---|---|
| PostgreSQL (including `BYTEA`) as sole live Evidence authority | **Rejected.** Couples irreplaceable bytes to schema evolution, weakens independent recovery proof, and repeats “normalized row is history” failure modes. |
| Dual live authorities (FS + PG must stay synchronized) | **Rejected.** Two coordination surfaces; green on one side can hide death on the other. |
| Flat payload + separate capture-record files without Attempt/Capture aggregate | **Rejected.** Historical audit findings: missing envelopes, false success, unverified provenance, non-durable installs. |
| Outcome as immutable Evidence / transport parent | **Rejected.** Collapses classification with testimony; blocks honest reclassification. |
| Ordinary hardlinks between pool objects and event bundles | **Rejected.** Shared-inode mutation blast radius. Use independent copy or COW reflink. |
| Capture-event Evidence Store format 2 (this decision) | **Accepted.** |

## Consequences

- Capture implementation must own durability primitives, path layout, scrub, and
  fixture-safe orchestration before rich multi-provider features.
- Authoritative recovery is Evidence restore → scrub → re-derive empty PostgreSQL.
- Local commit does not equal off-host protection (see deferred F6).
- Multi-process writer safety is unproved until F7 triggers.
- First implementation is fixture-only (`fixture-panel-v1`); paid providers remain deferred
  (F3).
