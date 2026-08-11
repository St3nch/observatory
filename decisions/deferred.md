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

**Deferred by:** D4.

**Why not now:** Both add operational complexity before real volume and recovery windows
are measured.

**Trigger:** Measured table size, maintenance time, backup duration, or restore objectives
cannot be met with the simpler design.

**Cost of forgetting:** Maintenance or recovery windows may eventually exceed acceptable
limits.

## F3 — Broad provider coverage

**Deferred by:** The narrow v1 proof in VISION.md.

**Why not now:** Each adapter multiplies capture and normalization cases before the shared
evidence path has proved itself.

**Trigger:** The first provider-neutral vertical slice passes its API and recovery
acceptance tests and a real consumer requires another source.

**Cost of forgetting:** Observatory may prove a sound data path but remain too narrow for
the next consumer.

## F4 — Dedicated hammer ticket

**Deferred by:** D6.

**Why not now:** Ordinary tests and narrow early substrate checks provide the fastest useful
feedback during construction.

**Trigger:** The first production candidate exists, before any real paid capture is
authorized.

**Cost of forgetting:** High-consequence survival, concurrency, retry, authorization, or
recovery claims may reach production without adversarial proof.

## F5 — Strategy-layer design

**Deferred by:** D3.

**Why not now:** It is a separate product and is not needed to prove Observatory's API data
path.

**Trigger:** A separate strategy-layer project is started with an identified consumer
outcome.

**Cost of forgetting:** None inside Observatory; downstream projects would simply lack the
strategy product.
