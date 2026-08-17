# Observatory

## North star

Observatory is a standalone, long-lived data service for SEO and GEO observations.
It acquires, validates, preserves, and serves clean historical data that many projects
can use through an API.

Observatory succeeds when a consumer can ask what was observed, when, where, by which
source and capture process, receive an explicit answer with its limits, and continue to
do so years after the original software and infrastructure have changed.

## Product shape

Observatory is infrastructure, not a strategy product.

- Many present and future projects may use the same service.
- Every consumer—including LLMs, agents, applications, and scripts—uses a versioned API
  for data access.
- No consumer directly accesses Observatory's database, Evidence Store, credentials, or
  internal implementation.
- Observatory remains useful without any particular consumer or strategy layer.

## Sole responsibility

Observatory owns the observation-data lifecycle:

1. Prepare the exact credential-free request, then durably commit an immutable **Attempt**
   on the Evidence Store before any fixture or provider transport I/O.
2. Perform transport using the recorded request bytes; when possible, durably commit an
   immutable **Capture** for complete, partial, or no-response transport testimony.
3. Preserve exact request and response bodies as content-addressed filesystem objects with
   verified event manifests and commit markers.
4. Derive versioned **Outcomes** (classifications) and admit **Observations** only from
   verified Captures that pass admission rules—never from unresolved, partial, no-response,
   refused, failed, or malformed paths presented as success.
5. Derive rebuildable, query-friendly Observations without rewriting Evidence.
6. Serve stable, explicit, provenance-complete historical data through the API, citing
   `attempt_id` and `capture_id`.
7. Export, restore, and scrub the Evidence Store, then re-derive disposable PostgreSQL on
   fresh infrastructure.

## Canonical lifecycle

```text
prepared request
  → committed Attempt
  → transport
  → committed Capture when possible
  → derived Outcome / classification
  → Derivation / admission
  → Observation
  → API (and optional later Projection)
```

**Authorized/unresolved** means a committed Attempt exists without a committed Capture.
That state must not be treated as definitely unsent, successful, failed, or safe to retry
automatically under the same Attempt. Process death after Attempt commit and before Capture
commit leaves honest unresolved history.

## Data doctrine

- Provider output is attributed testimony, not universal truth.
- Provider disagreement remains visible.
- Evidence (committed Attempt and Capture events plus body objects) and later
  interpretation are different things.
- Parsed Observations, indexes, and API query models are rebuildable conveniences, never
  the only surviving record.
- Every Observation traces to a verified Capture, its Attempt, and a Derivation version.
- Missing, unstated, inapplicable, refused, failed, partial, and unresolved are distinct
  states; they must not collapse into each other or into silent nulls.
- Absence claims are bounded by the exact request, source, surface, time, and sample.
- API reads disclose freshness, caveats, truncation, omissions, and known blind spots.
- Stable opaque identifiers for Attempt, Capture, and body addresses are full 64-character
  lowercase SHA-256 values and survive schema changes and re-derivation.
- Every authoritative read of Evidence verifies event identity, commit marker, body
  identities, and body sizes before use.
- API structures favor explicit fields and predictable semantics so ordinary software and
  LLMs can read them reliably.
- Observatory is deliberately **data-sufficient for downstream reasoning**. When selecting
  provider surfaces and fields, prefer preserving useful source-attributed testimony that
  would be expensive, impossible, or misleading to reconstruct later: rankings and SERP
  composition, citations/sources, competitor/domain/page relationships, query/topic
  discovery, demand/history, provider classifications, measurement context, and independent
  provider times/periods. A field does not need an immediate UI or strategy rule to be worth
  preserving when it can materially support later historical or comparative analysis.
- Data sufficiency does not mean indiscriminate collection. Provider catalogs are reviewed
  surface by surface for strategic information value, historical uniqueness, overlap,
  acquisition cost, and consumer need. Observatory keeps the useful testimony and its
  provenance; the downstream strategy layer—not Observatory—uses that corpus with LLMs and
  other analysis to discover opportunities, gaps, competitor advantages, visibility change,
  and possible SEO/GEO actions.
- Do not prematurely collapse rich provider testimony into a score or thin convenience row
  when doing so would discard relationships or dimensions a later consumer may need. Raw
  Evidence remains available for re-derivation, while normalized Observations expose the
  useful typed facts needed for reliable machine and LLM analysis.

## Survival requirement

The data must survive for many years. Survival does not mean freezing one application or
one PostgreSQL installation forever. Observatory must tolerate:

- forward schema migrations of rebuildable stores;
- PostgreSQL and operating-system upgrades;
- application and adapter rewrites;
- new providers and changed provider payloads;
- off-host backup and restoration of the **Evidence Store** onto a clean system;
- integrity scrub of restored Evidence;
- deterministic re-derivation of Outcomes and Observations into empty PostgreSQL;
- integrity verification after migration or recovery.

**PostgreSQL is disposable and rebuildable.** Authoritative recovery proves: restore the
Evidence Store → scrub → migrate/derive into empty PostgreSQL → compare equivalent
consumer-facing results. A PostgreSQL dump alone does not satisfy authoritative recovery.

**Local commit and off-host protection are distinct.** A Capture may be committed locally
while off-host replica protection is still pending, stale, or failed; those states must
not be conflated. Git or the source repository is not Evidence backup.

An irreplaceable observation path is not safely preserved until independent recovery of
its Evidence has been proved.

Supported primary Evidence Store roots are local POSIX filesystems with the durability
primitives in `docs/specs/capture-event-v2.md`. Unsupported network or sync filesystems
must not be treated as durable evidence roots.

## Boundary

Observatory does not own:

- SEO or GEO strategy;
- recommendations, conclusions, scoring, or reporting narratives;
- campaign planning or project workflows;
- customer-specific strategy state or private overlays;
- direct database or Evidence Store access for consumers;
- a universal interpretation that hides disagreement among sources.

Those concerns belong to downstream projects or a separate strategy layer.

## What v1 must prove

V1 is a narrow, working vertical slice—not broad provider coverage.

The first implementation remains **fixture-only** (`fixture-panel-v1`). It must exercise
the capture-event contract without real provider network activity. Paid-provider sequence
remains unsettled and deferred.

The fixture vertical slice proves:

1. A valid Evidence Store format-2 root can be created and opened fail-closed.
2. A service-owned fixture capture entrypoint commits Attempt before transport and Capture
   after fixture transport under the evidence contract.
3. Derivation into empty PostgreSQL produces deterministic versioned Outcomes and admitted
   Observations for the full fixture classification matrix.
4. A read-only API returns both Outcomes and Observations with provenance citing verified
   `attempt_id` and `capture_id`, distinguishing every fixture-v1 classification.
5. The same verified Evidence rebuilds equivalent derived results and API-visible data.
6. Basic tamper detection and report-only scrub refuse damaged material as valid Evidence.

The product proof is the complete data path and its local durability discipline, not the
number of integrations. Capture-event storage boundaries are settled product authority
(see D8 and `docs/specs/capture-event-v2.md`).

## Success tests

Observatory is on course when:

- a second project can integrate through the documented API without storage knowledge;
- the API can answer historical questions without embedding strategy;
- failed and uncertain attempts remain visible and cannot masquerade as observations;
- a parser or admission change produces a new derivation without mutating Evidence;
- a clean Evidence restore can scrub, re-derive empty PostgreSQL, and rebuild equivalent
  API results;
- ordinary development remains fast while high-consequence survival claims receive
  decisive proof before production use.

## Working restraint

Governance must not outrun execution. A document exists only when it unblocks work or
protects an irreversible decision. Planning becomes tickets, ordinary tests are the
default, and broad future features stay deferred until an observable trigger fires.
