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

**Routine F6 accepted — 2026-09-01:** [CHAZ] resumed F6 commissioning and created the
dedicated private Cloudflare R2 bucket
`vedaops-observatory-backups` with a bucket-scoped account-owned machine credential limited
to R2 Bucket Item read/write. The encrypted restic repository at the R2 S3 endpoint was
initialized as repository `1137afe0`; credentials remain outside the repository and are
stored locally under owner-only permissions, with recovery copies retained in Bitwarden.

The replaceable-Evidence migration rehearsal passed end to end. Fresh fixture-panel-v1
Evidence containing one Attempt and one Capture opened as format 2 and scrubbed clean; restic
snapshot `8f51ae5135b21b885702e11a77291bf71d5d54e749125ebd8f6648926ac5e168`
was restored into a fresh directory; the restored store opened and scrubbed clean; and both
the independently recomputed restored Attempt/Capture inventory and the snapshotted
outside-root inventory were byte-identical to the source inventory, SHA-256
`a41cfefb0c02283fb30686f54095fa923ffb800c837ceac6af3e7fedbe709a6c`.

All four irreplaceable provider Evidence roots present on the VPS were then snapshotted to R2
without deleting or altering the existing Google Drive copies. Fresh restores of all four
opened as format 2, scrubbed clean, and exactly reproduced their independently recorded
Attempt/Capture inventories:

- AI-09 Target Metrics — R2 snapshot
  `b6ece774b2ec837c9098c4d029b7936c32e3f4abd2ed36c4c1e8dc931825ff5d`, inventory SHA-256
  `c9b236dbfb7bf12b2764fb6d28e5e697aa5ff300b8b042739c2c8c166d7386a5`;
- AI-14 Historical LLM Mentions — R2 snapshot
  `774c913177db5f37b92a6438fe3d8cfa47b4c82027b798034421907fc4652324`, inventory SHA-256
  `86be371907404b4903ad5bb73ce70e71ffdaf1328d60d645e5638e6486c3d07e`;
- RANK-03 Ranked Keywords — R2 snapshot
  `171f08450a682af6647fe2521d4402bd214de61403eb3a8e4046329c897f8394`, inventory SHA-256
  `9fb185b668675f8ee6fe7d39085e93558d5728e2f03d17f0fc1371f2b40a0830`;
- RK-02 Related Keywords — R2 snapshot
  `e9816316ceb76d7c574e8bd5e1ea995b1d7c5e19804721046c711065892d931a`, inventory SHA-256
  `6d6b229b2f5e1084c9bf753550364db226d7ab92c032a72da1fdf37809e23801`.

The R2 repository check completed with no errors after all five migration/rehearsal snapshots.
Routine automation was then commissioned as owner-user systemd units with lingering enabled.
`observatory-f6-r2-backup.timer` runs daily at 03:30 America/Detroit with `Persistent=true`
and up to ten minutes of randomized delay. Its shared operation lock refuses overlap with
another F6 operation; the backup wrapper validates and scrubs every discovered non-rehearsal
Evidence root, records an exact aggregate inventory, creates an encrypted `f6-routine` restic
snapshot, requires the post-backup inventory to remain byte-identical, revalidates the source,
and writes a non-secret PASS/FAIL status receipt while systemd records process failure in the
user journal. Retention is indefinite: no automated `forget`, `prune`, or other destructive
repository operation is authorized.

A forced systemd execution of the daily service exited successfully and created routine
snapshot `1985deccf9e9bccfbf624297bf2514c0b6e13e887665089a4723e2e3b62291cb` over all four
current provider Evidence roots. Its aggregate inventory SHA-256 is
`a8eaee37e7d2ab7baaf334349cf8f70ce60856763e59d7075f2623159f18705c`; the persisted receipt
reported `status=PASS`, `root_count=4`, and `retention=indefinite`.

`observatory-f6-r2-restore-drill.timer` runs monthly on day 1 at 04:30 America/Detroit with
`Persistent=true` and up to thirty minutes of randomized delay, using the same operation lock.
The drill performs `restic check`, selects the newest `f6-routine` snapshot, restores it into a
fresh temporary directory, opens and scrubs every restored Evidence root, independently
recomputes the aggregate Attempt/Capture inventory, requires byte equality with the inventory
stored inside that snapshot, writes a PASS/FAIL receipt, and removes the temporary restore.
A forced systemd drill against snapshot `1985deccf9e9bccfbf624297bf2514c0b6e13e887665089a4723e2e3b62291cb`
completed successfully: repository check PASS, restore PASS, inventory equality PASS, four
roots, and the same aggregate inventory SHA-256
`a8eaee37e7d2ab7baaf334349cf8f70ce60856763e59d7075f2623159f18705c`.

The Project Steward accepts routine F6 as complete. Cloudflare R2 is the commissioned routine
off-host Evidence destination with proven automated backup and automated recovery drill;
retention is indefinite until separately changed. The existing Google Drive copies remain
preserved as additional off-host protection. No provider call, Evidence deletion, repository
pruning, or push is authorized by this acceptance.

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

## F13 — Older transport-capability authority hardening

**Deferred by:** AI-08's Target Metrics-only scope and the requirement to preserve each
adapter's closed transport contract rather than introduce a generic capability framework.

**Why not now:** AI-08 replaced caller-visible capability fields with closure-owned
transport authority for Target Metrics. Review found that the older sandbox, Keyword
Overview, Google Organic, and Search Mentions gates still treat capability attributes such
as the request body, document, or used flag as transport authority. Deliberate
same-process abuse of private seams, including `object.__setattr__`, can therefore bypass
their intended immutability or replay checks. Remediating those four gates is outside
AI-08 and should remain separately bounded so their published bytes, one-shot rules, and
surface-specific transport behavior stay independently reviewable.

**Trigger:** Before the next live operator invocation, substantive modification, or reuse
of any affected gate, harden that gate with closure-owned issuance and consumption state,
committed-Attempt revalidation immediately before send, and adversarial tests for body and
document replacement, used-flag reset, replay, and committed-Evidence tamper. Start with
Search Mentions when no earlier affected gate fires the trigger.

**Cost of forgetting:** A same-process caller with access to private seams could change
what an already-authorized capability sends or replay it, breaking the Attempt-before-send
and one-exchange claims even though ordinary attribute assignment remains blocked.

**Current state — 2026-09-01:** PF-16 closed the Keyword Overview F13 hardening and PF-17
closed the Google Organic F13 hardening, each with surface-local closure-owned issuance /
consumption authority and immediate committed-Attempt revalidation before send. Search
Mentions remains separately F13-gated if it is reused or substantively modified. New provider
adapters should be born with the hardened closure-owned pattern rather than reusing an older
caller-visible gate; doing so does not itself fire F13 or create a generic transport-capability
framework.

## Strategy-consumer pressure watchlist — 2026-09-02

**Source and status:** After Observatory MVP closure, an independent Fable 5.1
commissioning review inspected accepted HEAD
`40ecd819b26fb28d808f92e75adcb9ff505c1972` as an API-only future Strategy consumer.
The Project Steward reconciled the Observatory-specific findings below. They are retained
as deferred consumer-pressure signals, **not** as tickets, implementation authorization,
provider-call authorization, or evidence that the accepted MVP is incomplete. No item
below reopens MVP-01. The review found no current Observatory blocker to beginning Strategy
product work.

### Read-API symmetry and scale

- Keyword Overview, Google Organic, and Search Mentions expose History, Outcomes, and
  Holdings, while Target Metrics, Historical LLM Mentions, Related Keywords, and Ranked
  Keywords expose History only. For those four History-only surfaces, an API-only consumer
  cannot uniformly distinguish never-measured from unresolved/failed acquisition using the
  same discovery path. **Trigger:** a real consumer repeatedly needs that distinction on one
  of those surfaces. Until then, empty History remains unknown rather than proof of
  non-acquisition.
- Provider History deliberately caps one response at 100 matching Captures and does not
  expose outer pagination. **Trigger:** a real subject accumulates more than 100 comparable
  Captures and the consumer must retrieve older history. Do not add pagination merely in
  anticipation of recurrence.
- Holdings are intentionally a low-volume bridge with a bounded result count and store-wide
  verification posture. **Trigger:** more than 100 holding groups, or measured consumer
  latency/ergonomics that makes the current bridge materially inadequate.
- History request-context filtering remains a consumer concern at current scale. A consumer
  can partition returned Captures by disclosed request context. **Trigger:** repeated
  multi-context histories make that deterministic client-side partition materially awkward
  or expensive. Exact-string provider subject identity remains deliberate and is not a
  defect to normalize inside Observatory.
- Google Organic expanded-history verification cost grows with matching Capture count.
  **Trigger:** measured history-read cost becomes material after repeated acquisition; only
  then consider the already-anticipated scalable verified index/projection path.

### Acquisition is not an Observatory scheduling mandate

- The review correctly distinguished "Observatory can preserve history" from "the system
  has accumulated repeated comparable history." Current provider Evidence is primarily the
  accepted commissioning set, not a recurring Strategy measurement panel.
- This does **not** change F12. Observatory must not decide strategic importance, subject
  panels, cadence, or recapture policy for downstream consumers. If Strategy later requires
  repeated or coordinated measurement, resolve the ownership and human-authorization
  boundary first; only then does F12's recorded trigger determine whether acquisition
  orchestration work belongs here.
- Additional competitor targets, keywords, locations, devices, or repeated Captures are
  acquisition choices, not missing Observatory implementation by themselves.

### Potential future testimony families

- **First-party search-performance testimony:** Strategy may eventually need Search
  Console-class source-attributed testimony to reason about owned-property impressions,
  clicks, query/page relationships, and apparent post-change effects. `VISION.md` already
  permits separately activated first-party/provider testimony; no activation is implied
  here. **Trigger:** a concrete downstream question cannot be answered honestly from the
  accepted external-provider surfaces plus consumer-owned state, and the acquisition / data
  retention consequences have been separately reviewed.
- **Live generative-answer / citation observation:** the accepted indexed AI-optimization
  surfaces and Google Organic AI Overview testimony are not equivalent to repeatedly
  observing live generative answers. Such a surface may matter for future GEO questions,
  especially when answer/citation variability itself is material. **Trigger:** Strategy
  demonstrates a concrete decision that requires live-sample testimony rather than the
  accepted indexed/historical surfaces. Any future activation must preserve sampling
  context and must not present a one-shot generative answer as deterministic visibility.
- **Owned-site state / independent demand triangulation:** page inventories, internal-link
  state, Search Trends-class data, or other instruments may eventually support Strategy,
  but the existence of a provider/tool does not assign that state to Observatory. Resolve
  consumer ownership and the exact unanswered question before activating another surface.

### Consumer-ready behavior to protect

The review found no reason to weaken or redesign the accepted MVP's time-axis discipline,
Recipe pinning, provenance identifiers, fail-closed integrity behavior, request-context
echoes, completeness/prefix disclosures, exact provider identity, or Evidence boundaries.
Future consumer friction should first be classified as downstream reasoning, API ergonomics,
genuinely absent testimony, or a new provider/instrument need before Observatory work is
proposed.
