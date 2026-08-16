# Observatory Deferred Register

Deferred means deliberately unbuilt. Entries contain no design beyond the trigger.

## F1 — Shared query-panel ownership

**Deferred by:** D1 and D3.

**Why not now:** The first vertical slice can preserve exact request context without
deciding whether reusable measurement panels belong in Observatory or orchestration.

**Trigger:** Two independent consumers need to refer to the same versioned measurement
definition.

**Cost of forgetting:** Consumers may invent incompatible panel identities that weaken
historical comparison.

## F2 — Table partitioning and incremental backup chains

**Deferred by:** D4 (clarified by D8).

**Why not now:** Both add operational complexity before real volume and recovery windows
are measured. This entry concerns rebuildable PostgreSQL (or similar query-store)
maintenance and backup chains—not the authoritative filesystem Evidence Store layout.

**Trigger:** Measured table size, maintenance time, backup duration, or restore objectives
for the rebuildable query store cannot be met with the simpler design.

**Cost of forgetting:** Maintenance or recovery windows for rebuildable stores may
eventually exceed acceptable limits. Evidence Store backup remains governed by D8 and F6.

## F3 — Broad provider coverage

**Deferred by:** The narrow v1 proof in VISION.md and D8 fixture-first rule.

**Why not now:** Each adapter multiplies capture and normalization cases before the shared
capture-event Evidence path has proved itself. First implementation remains fixture-only
(`fixture-panel-v1`).

**Trigger:** The first provider-neutral vertical slice passes its API and Evidence Store
recovery acceptance tests and a real consumer requires another source; Steward authorizes
paid-provider sequencing.

**Cost of forgetting:** Observatory may prove a sound data path but remain too narrow for
the next consumer.

**Bounded activation:** D9 authorizes the provider-neutral HTTP event foundation and one
DataForSEO Google Organic Live Advanced tracer against the free sandbox. D10 additionally
authorizes implementation of one tightly budgeted DataForSEO Labs Google Keyword Overview
Live adapter, with a maximum of five keywords and one exchange. Neither decision fires
broad provider coverage, Standard/asynchronous operation, provider derivation, or a
capability catalog. Those remain deferred to their recorded triggers.

**Provider direction:** DataForSEO is the first provider, not Observatory's exclusive
provider. Ahrefs and Semrush are expected future supplementary and comparison sources.
Naming them records product direction only; neither integration is currently authorized
or scheduled, and this does not fire the trigger above.

## F4 — Dedicated hammer ticket

**Deferred by:** D6 (substrate clarified by D8).

**Why not now:** Ordinary tests and narrow early substrate checks provide the fastest useful
feedback during construction.

**Trigger:** The first production candidate exists, before any real paid capture is
authorized.

**Cost of forgetting:** High-consequence Evidence Store durability, Attempt authorization
concurrency, recovery, or rebuild claims may reach production without adversarial proof.

**Satisfied for bounded paid-probe sequencing:** HAM-01 closed on 2026-08-16 after 42
Attempt-phase and 30 Capture-phase process-death fault points plus the operator run on the
supported ext4 Evidence filesystem. This satisfies F4 for D10 only; it does not prove
power-loss, device-cache, off-host recovery, or concurrent writers.

## F5 — Strategy-layer design

**Deferred by:** D3.

**Why not now:** It is a separate product and is not needed to prove Observatory's API data
path.

**Trigger:** A separate strategy-layer project is started with an identified consumer
outcome.

**Cost of forgetting:** None inside Observatory; downstream projects would simply lack the
strategy product.

## F6 — Off-host Evidence protection

**Deferred by:** D8.

**Why not now:** The fixture vertical slice proves the local Evidence path only. Local
durable commit is not replication. Git or the source repository is not Evidence backup.

**Trigger:** Before any irreplaceable paid or production Evidence becomes sole-copy
authority.

**Cost of forgetting:** Host loss, disk failure, or operator deletion permanently destroys
irreplaceable capture history.

**Current state:** Triggered for D10's first real paid response. PF-03 implementation and
zero-network review may proceed, but the operator paid invocation remains blocked until a
separately accepted off-host protection path exists.

## F7 — Multi-process capture authorization locking

**Deferred by:** D8 and the fixture vertical-slice single-process proof boundary.

**Why not now:** The first accepted slice proves single-process correctness only.
Fingerprint-scoped multi-process locking is not required to accept the fixture tracer.

**Trigger:** A second concurrent capture writer, or production shared use of one Evidence
root by multiple processes, is required.

**Cost of forgetting:** Concurrent writers may bypass duplicate-window or spend policy and
create conflicting authorization outcomes. The first implementation must not claim
multi-process writer safety.

## F8 — Production API authentication and non-loopback binding

**Deferred by:** The fixture/dev tracer authentication boundary.

**Why not now:** The first slice binds only to loopback with no authentication and is
explicitly not production-safe.

**Trigger:** Any non-loopback bind, multi-consumer production exposure, or non-dev
deployment of the API.

**Cost of forgetting:** Unauthenticated or network-exposed read access to historical
observation data.

## F9 — HTTP write API for capture

**Deferred by:** The fixture vertical-slice write-surface decision (service-owned CLI).

**Why not now:** The first slice uses `python -m observatory.capture` (fixture-panel-v1
only). The HTTP API is read-only.

**Trigger:** A consumer requires API-initiated capture without the service CLI.

**Cost of forgetting:** Pressure for ad-hoc write paths or direct Evidence Store access.

## F10 — Projection tables

**Deferred by:** D8 and the minimum rebuildable PostgreSQL model for fixture v1.

**Why not now:** The API maps Observation rows into its versioned response schema directly.
Separate projection relations add schema and rebuild surface before a consumer needs them.

**Trigger:** A real consumer requires a distinct, persistently queryable reshape beyond
Observation rows and API mapping.

**Cost of forgetting:** Consumers invent incompatible derived stores, or Observation
tables absorb reshape pressure that belongs in a versioned projection.
