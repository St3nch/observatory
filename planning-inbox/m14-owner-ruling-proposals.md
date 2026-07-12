# M14 Owner-Ruling Proposals

Status: planning / owner-decision proposal
Authority: none until accepted in `decisions/`
Milestone: M14
Date: 2026-07-12

---

## Purpose

Present the minimum owner rulings needed before the M14 typed-read contract can be accepted or a bounded prototype can be implemented.

These proposals preserve fail-closed defaults. Silence does not approve implementation.

---

## Proposal D1 — Consumer Authentication and Authorization

Tracker: OR-D1

Proposed ruling:

```text
M14 read access uses authenticated caller classes with explicit scope and request-type grants.
Caller identity is supplied by the access layer and cannot be self-asserted or widened by request content.
Cross-scope access is forbidden by default.
```

Initial caller classes:

```text
internal_llm
operator
kaizen
neon_ronin
searchclarity_internal
```

Initial posture:

- least privilege;
- explicit scope grants;
- explicit request-type grants;
- no customer-facing/public caller;
- no direct SQL or credentials;
- uniform not-found for nonexistent versus unauthorized handles;
- no self-service grant changes.

This is a contract ruling, not an auth implementation choice.

## Proposal D2 — Raw Pointer Exposure

Tracker: OR-D2

Proposed ruling:

```text
Raw payload pointers and archive paths remain internal-only.
Typed read outputs may expose raw-support status but never raw filesystem/object-store paths or credentials.
```

Allowed status examples:

```text
present_internal
purged_with_proof
blocked_by_rights
expired_by_retention
not_captured
unknown
```

Any later customer-facing raw-reference concept requires a separate owner ruling.

## Proposal D3 — Evidence Withdrawal, Supersession, and Status-Aware Reads

Tracker: OR-D3

Proposed ruling:

```text
Evidence is never silently overwritten.
Current status controls read behavior.
Superseded evidence may be returned only as historical/status-caveated evidence.
Withdrawn, invalidated, blocked-by-rights, and expired-by-retention evidence must not be returned as active evidence.
```

Citation/evidence handle resolution must be status-aware.

A status transition after initial admission must affect later reads and invalidate stale cursors/cache assumptions.

## Proposal D4 — Update-Window Feeds

Tracker: OR-D4

Proposed ruling:

```text
Update-window feed metadata is optional evidence input, not a requirement for every M14 prototype fixture.
When a relevant feed is missing, freshness/volatility behavior fails closed to unknown or caveated status.
No missing feed may be replaced with an invented cadence.
```

Actual provider/source update-window integration remains later work.

## Proposal A4-M14 — Citation Handle Scope-Down

Tracker: OR-A4

Proposed M14-scoped ruling:

```text
M14 supports internal evidence handles only.
Report-safe/customer-facing references remain deferred to M15.
```

Handles must be non-enumerable and status-aware.

This ruling does not settle the final report-safe reference class.

## Proposal R1 — Read Security Logging

New M14 ruling candidate.

Proposed ruling:

```text
Ordinary successful reads do not create Observatory evidence events.
Authentication failures, authorization failures, enumeration attempts, and rate/ceiling breaches may create security/access logs outside the evidence corpus.
```

Security logs:

- are operational/security records, not observations;
- do not become customer records;
- must avoid credentials and private payload content;
- follow a separately defined retention posture before production use.

## Proposal R2 — Machine-Readable Test-Result Register

Proposed ruling:

```text
M14 may define a committed machine-readable test-result register for implementation proof metadata.
The register is repository test evidence, not Observatory business evidence and not a database requirement.
```

Every result must name proof class, execution surface, proof strength, commit, result, evidence path, and limitations.

## Proposal R3 — Prototype Scope

Proposed ruling:

```text
After contract and hostile-path acceptance, M14 may propose one bounded local fixture-backed prototype.
```

The prototype remains:

- local-only;
- in-memory;
- no network listener;
- no real MCP registration;
- no database;
- no customer data;
- no provider call;
- no persistence;
- no overlay;
- no report output.

Implementation still requires a separate exact task approval after these rulings are accepted.

---

## Recommended Owner Decision Set

Recommended acceptance bundle:

```text
ACCEPT OR-D1 proposal
ACCEPT OR-D2 internal-only raw pointer posture
ACCEPT OR-D3 status-aware read behavior
ACCEPT OR-D4 fail-closed update-window posture
ACCEPT OR-A4 M14 internal-handle scope-down
ACCEPT M14 read-security logging distinction
ACCEPT machine-readable test-result register as repository proof metadata
```

Do not combine prototype implementation approval into the same decision.

---

## Still Deferred

- production auth technology;
- public/customer-facing callers;
- report-safe references;
- real API/MCP deployment;
- database access layer;
- provider execution;
- overlays;
- customer data;
- recurring capture.
