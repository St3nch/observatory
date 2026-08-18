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

## F3 — Routine broad provider/surface rollout

**Deferred by:** D8–D12 bounded provider activation discipline.

**Why not now:** Broad, materially useful measurement coverage is product direction, but
moving from individually authorized adapters to routine multi-surface/provider acquisition
would multiply spend, acquisition workflows, completeness/retention obligations, and
recurring operations before their shared prerequisites and orchestration are accepted.

**Trigger:** The Product Owner and Steward explicitly authorize routine multi-surface or
multi-provider acquisition after the required workflow-specific provenance, routine F6
Evidence protection, text-retention posture where applicable, and acquisition orchestration
are accepted for the intended operating mode.

**Cost of forgetting:** Observatory may remain adapter-by-adapter indefinitely, or broad
acquisition may emerge ad hoc without adequate spend, provenance, retention, cadence, or
recovery controls.

**Bounded activation:** D9 authorizes the provider-neutral HTTP event foundation and one
DataForSEO Google Organic Live Advanced tracer against the free sandbox. D10 additionally
authorizes implementation of one tightly budgeted DataForSEO Labs Google Keyword Overview
Live adapter, with a maximum of five keywords and one exchange. D11 subsequently authorizes
provider Derivation for the captured Keyword Overview contract, and D12 defines the bounded
provider-discovery method. Future individually authorized adapters and probes may proceed
under D12 without firing F3 when their contract fits the accepted substrate and all other
gates. An unresolved asynchronous/continuation design for one contract does not by itself
block a bounded one-exchange contract. F3 remains unfired and does not authorize recurring
acquisition.

**Provider direction:** DataForSEO is the first provider, not Observatory's exclusive
provider. Additional independent providers and materially useful surface families are
expected future coverage where their testimony adds value. Naming a provider or family
records product direction only; it does not authorize an integration, call, spend, or
schedule and does not fire the trigger above.

The intended DataForSEO testimony families are inventoried in
`docs/dataforseo-surface-roadmap.md`. That roadmap records product direction and sequencing
constraints only; it does not authorize an adapter, provider call, spend, schedule, bulk
collection, or F3 rollout by itself.

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

**Current state:** D10's first paid Capture completed the accepted manual off-host protection
sequence. F6 remains deferred for routine paid or production Evidence until a separately
accepted automated snapshot, retention, and restore-drill policy exists.

**D10 rehearsal accepted — 2026-08-16:** [CHAZ] completed the minimum replaceable-Evidence
rehearsal against the clean PF-02 sandbox smoke store
`/home/chaz/.local/share/vedaops/observatory/pf02-smoke-20260816T144311Z` using Google Drive
as the off-host destination, rclone transport, and an encrypted restic repository at
`VedaOps Backups/Observatory/evidence-store/repository`. The source store was quiescent,
opened as format 2, and scrubbed clean with exit 0. An independently recorded inventory
contained exactly one committed Attempt and one committed Capture. Restic 0.19.1 created
snapshot
`f368f806325106f7a24f7da7d997e583ac10b1147ab6f542fce56bbe7b9d3d85` containing the full
Evidence root and that inventory. A restore into a fresh local directory opened and
scrubbed clean with exit 0; restored Attempt and Capture ID sets each matched the recorded
source sets exactly. Human-readable backup and restore-proof receipts were copied to the
corresponding `receipts/` and `restore-proofs/` Drive folders. No credentials were included
in the snapshot inventory or receipts. The Project Steward accepts this as the D10
replaceable-Evidence rehearsal and as the separately accepted off-host protection path
required before issuing the first paid operator command.

**Rehearsal-only gate status at acceptance time:**

This acceptance does **not** complete F6 generally and does not itself authorize a provider
call. Before D10's live command, the Steward must still freshly recheck official pricing
and [CHAZ] must explicitly authorize the one-shot operator sequence. After the first paid
Capture, that store must undergo the same quiesce → inspect/scrub → exact inventory →
encrypted snapshot → fresh restore → scrub → exact set-equality sequence before the paid
Evidence is treated as safely protected. Routine paid capture still requires the separately
accepted automated snapshot, retention, and restore-drill policy below.

**D10 first paid Capture accepted — 2026-08-16:** After a fresh official-pricing recheck
and explicit [CHAZ] authorization, PF-03 committed Attempt
`c0da493c3a44f1f60bc21d7afaab290e852dadafa8157386b79bd58ebec07462` and Capture
`b4fc36a7799b497d0d183a88449bf0a770ce741ec1f0d8eaade2d75c930154d5` in the fresh Evidence
root `/home/chaz/.local/share/vedaops/observatory/pf03-paid-20260816T213724Z`. No retry or
second paid invocation was performed. The source was quiescent, opened as format 2, and
scrubbed clean with exit 0; an independent inventory recorded exactly one committed
Attempt and one committed Capture. Restic 0.19.1 created encrypted off-host snapshot
`e549c887dfdb8d7006f3f7e9fd99eea2aa7097e3c6bb6fd0320cd99baa09eb82`. A fresh restore
opened and scrubbed clean with exit 0; restored Attempt and Capture ID sets exactly matched
the recorded source sets. Original and restored inventory SHA-256 both equal
`58ac410ae1625c1088aceb32769d05e25b0474eecca083e075102512e1686d21`. Corresponding
`.ok.json` backup and restore-proof files are present in the approved off-host folders.
The Project Steward accepts completion of D10's first-paid-Capture protection requirement.

This completes F6 only for D10's first bounded probe. Routine paid or production capture
still requires the separately accepted automated snapshot, retention, and restore-drill policy.

**Minimum acceptance for D10 only:** Before the paid command is authorized, the exact
procedure and destination must be rehearsed with replaceable Evidence. The destination is
not a filesystem on the capture host: it is encrypted remote/cloud storage, a separate
host, or a disconnected removable medium stored separately. Another directory, another
internal disk, Git, and the source repository do not qualify. A destructive mirror without
retained snapshots does not qualify.

The rehearsal and the first paid-Capture protection sequence must each:

1. quiesce the source store, inspect it, and scrub every discovered commitment clean;
2. record sorted exact committed Attempt and Capture ID sets outside the source store;
3. create a timestamped, non-destructive off-host snapshot containing the full Evidence
   root and the recorded inventory, without credentials or unrelated configuration;
4. restore that snapshot into a fresh local directory;
5. open and scrub the restored store clean; and
6. require exact equality between the restored committed-ID sets and the recorded source
   sets.

Scrub proves integrity only for commitment-claiming directories it discovers; the
independent inventory/set comparison supplies the completeness witness for this snapshot.
[CHAZ] performs the operator sequence and the Project Steward records acceptance evidence.
This manual proof is proportionate only to D10's first bounded probe. Routine paid capture
requires a separately accepted automated snapshot, retention, and restore-drill policy.

**Routine automation status — deferred 2026-08-16:** The accepted manual D10 protection
path remains available, but unattended backup automation is not yet accepted. The intended
long-term destination is Cloudflare R2 with a dedicated project backup bucket and scoped
machine credentials. R2 onboarding, bucket creation, credentials, migration rehearsal,
systemd automation, retention, and restore-drill policy remain deferred until the Product
Owner explicitly resumes this work. The existing Google Drive rehearsal copy is preserved
meanwhile.

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

## F11 — Provider Derivation identity, drift, and data time

**Resolved by:** D11 on 2026-08-16. This entry remains as trigger history.

**Original deferral:** D9/D10's raw-provider-testimony boundary preserved provider responses
as Evidence without interpreting them into provider Outcomes or Observations. Fixture v1
remained governed by its closed conformance contract and semantic label.

**Trigger:** Before the first provider-specific Derivation, provider Outcome/Observation
mapping, or API exposure of provider-derived values is accepted.

**Trigger result:** PF-03 returned the first real paid provider response and exposed
non-positional item order, multiple independently updated provider structures, historical
monthly testimony, decimal values, and distinct null/disabled states. The trigger fired.
D11 now defines content-addressed provider recipe identity, strict/versioned parsing and
drift handling, semantic request/result reconciliation, typed Observation kinds, exact
numeric normalization, field-level value states where needed, and independent
capture/provider-update/data-period time axes. Fixture v1 identity remains unchanged.

**Cost of forgetting:** Different derivation behavior can reuse one label, provider schema
changes can silently alter or break ingestion, and monthly or provider-updated metrics can
be presented as if they described the capture instant, producing false comparisons across
time or providers.

## F12 — Acquisition orchestration

**Deferred by:** D3 and the current bounded operator/service-CLI acquisition model.

**Why not now:** Isolated captures can be explicitly authorized with exact request context
without creating durable Observatory state for why a subject is important, which surfaces
should be coordinated, or when a measurement should repeat. Observatory must not turn
strategy importance into its own scheduling policy.

**Trigger:** Recurring or coordinated acquisition requires durable ownership of intended
subject sets, cadence, cross-surface measurement policy, requested depth/limits,
promotion/demotion to deeper monitoring, or event-triggered recapture beyond isolated
operator runs.

**Cost of forgetting:** Ad hoc schedules can create irregular or incompatible histories
that weaken comparison and forecasting, obscure why deep monitoring began or ended, and
pressure Observatory to absorb customer-specific strategy state or an internal scheduler.

**Related deferrals:** F1 remains the separate, unfired question of canonical shared
query-panel ownership. If a consumer later requires HTTP-initiated capture instead of the
service CLI, F9 separately fires.
