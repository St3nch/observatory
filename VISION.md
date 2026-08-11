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
- Every consumer—including LLMs, agents, applications, and scripts—uses a versioned API.
- No consumer directly accesses Observatory's database, evidence storage, credentials,
  or internal implementation.
- Observatory remains useful without any particular consumer or strategy layer.

## Sole responsibility

Observatory owns the observation-data lifecycle:

1. Record capture attempts before external activity.
2. Preserve exact request, response, timing, source, and processing context.
3. Distinguish successful observations from refusals, failures, malformed responses,
   partial responses, and unresolved attempts.
4. Validate admitted observations without rewriting historical evidence.
5. Derive rebuildable, query-friendly forms from preserved evidence.
6. Serve stable, explicit, provenance-complete historical data through the API.
7. Export, restore, verify, and re-derive the data on fresh infrastructure.

## Data doctrine

- Provider output is attributed testimony, not universal truth.
- Provider disagreement remains visible.
- Raw evidence and later interpretation are different things.
- Parsed and indexed forms are rebuildable conveniences, never the only surviving record.
- Every observation traces to its capture context and derivation version.
- Missing, unstated, inapplicable, refused, and failed are distinct states.
- Absence claims are bounded by the exact request, source, surface, time, and sample.
- API reads disclose freshness, caveats, truncation, omissions, and known blind spots.
- Stable opaque identifiers survive schema changes and re-derivation.
- API structures favor explicit fields and predictable semantics so ordinary software and
  LLMs can read them reliably.

## Survival requirement

The data must survive for many years. Survival does not mean freezing one application or
one PostgreSQL installation forever. Observatory must tolerate:

- forward schema migrations;
- PostgreSQL and operating-system upgrades;
- application and adapter rewrites;
- new providers and changed provider payloads;
- off-host backup and restoration onto a clean system;
- deterministic re-derivation of query models;
- integrity verification after migration or recovery.

An irreplaceable observation is not safely preserved until its independent recovery path
has been proved.

## Boundary

Observatory does not own:

- SEO or GEO strategy;
- recommendations, conclusions, scoring, or reporting narratives;
- campaign planning or project workflows;
- customer-specific strategy state or private overlays;
- direct database access for consumers;
- a universal interpretation that hides disagreement among sources.

Those concerns belong to downstream projects or a separate strategy layer.

## What v1 must prove

V1 is a narrow, working vertical slice—not broad provider coverage.

Through the API, an authorized consumer must be able to:

1. create or initiate a provider-neutral capture attempt using fixture infrastructure;
2. obtain an honest terminal outcome;
3. retrieve the admitted observation and its provenance;
4. page through historical results using stable cursors;
5. verify that the same evidence can rebuild the same consumer-facing result.

The exact first provider, schema, and endpoint design are implementation decisions. The
product proof is the complete data path and its durability, not the number of integrations.

## Success tests

Observatory is on course when:

- a second project can integrate through the documented API without storage knowledge;
- the API can answer historical questions without embedding strategy;
- failed and uncertain attempts remain visible and cannot masquerade as observations;
- a parser change produces a new derivation without mutating the original evidence;
- a clean restore can verify evidence and rebuild equivalent API results;
- ordinary development remains fast while high-consequence survival claims receive
  decisive proof before production use.

## Working restraint

Governance must not outrun execution. A document exists only when it unblocks work or
protects an irreversible decision. Planning becomes tickets, ordinary tests are the
default, and broad future features stay deferred until an observable trigger fires.
