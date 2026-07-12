# Decision: M13 Closure and M14 Planning Activation

Status: accepted decision
Authority: owner milestone closure / roadmap transition
Date: 2026-07-12
Milestone closed: M13 — Provider Admission and Controlled Pull Plan
Milestone activated: M14 — Typed Read API / MCP Contract and Prototype
Closure basis: `planning-inbox/m13-closure-readiness-review-2026-07-12.md`
Owner authorization: `APPROVE M13 CLOSURE AND ACTIVATE M14 PLANNING BOUNDARY`

---

## Decision

M13 is closed.

M14 — Typed Read API / MCP Contract and Prototype is now active for planning only.

M13 closure accepts the bounded DataForSEO C00 provider probe as lawful, reviewed, cost-reconciled, provider-attributed payload-shape evidence.

This closure does not broadly admit DataForSEO, authorize another paid request, approve recurring capture, approve provider ingestion, or convert one payload into schema authority.

---

## Accepted M13 Evidence

The accepted M13 proof includes:

```text
one Google Organic Live Advanced C00 request
one billable task
HTTP 200
provider and task status 20000
expected cost 0.002 USD
provider top-level cost 0.002 USD
provider task-level cost 0.002 USD
zero retries
zero polling requests
one reviewed evidence package
raw payload purged with durable proof
```

Accepted probe identity:

```text
2026-07-12_C00_145948Z-f0b5410c
```

Accepted request SHA-256:

```text
f0b5410c5cc490b64ec4bb471a92c24647dccf432962fcd952c4070b03b2c4c9
```

Accepted pre-purge raw SHA-256:

```text
17d2050963ca374458b7b2b1e8354702c80f362f66ce44fd34e997cb1d59012c
```

Accepted package findings:

```text
12 items
10 organic
1 people_also_ask
1 related_searches
162 normalized field paths
0 unknown item types
```

These findings are provider payload-shape evidence only.

---

## Accepted Control Proof

M13 accepts bounded proof for:

```text
H2  rights fail-closed
H6  CapturePackage paid-capture evidence
H7  spend ceiling and duplicate-task controls
H8  provider attribution / no truth collapse
H12 raw hash, retention, and purge proof
H13 provider-shape inspection and drift evidence inputs
H20 duplicate and replacement-attempt protection
```

The accidental placeholder-credential 401 incident was preserved rather than erased. One explicit replacement request was separately authorized, executed once, and then consumed. Automatic retry remained disabled.

---

## What M13 Proved

M13 proved that The Observatory can:

- bind one immutable provider request to explicit owner authority;
- enforce request, task, price, endpoint, retry, and polling ceilings;
- keep credentials outside committed evidence;
- preserve provider testimony without treating it as truth;
- capture raw support locally under a time-bounded retention posture;
- generate durable request, field, shape, item-type, and cost evidence;
- inspect a real provider payload before schema or persistence decisions;
- preserve incidents and duplicate-attempt history;
- purge raw provider payload with hash-locked durable proof;
- stop after the authorized request.

---

## What M13 Did Not Prove

M13 did not prove:

- stable DataForSEO shape across time, devices, languages, locations, depths, or endpoints;
- broad DataForSEO admission;
- production ingestion safety;
- recurring capture safety;
- provider comparison safety;
- customer-data handling;
- report-safe output;
- typed read API design;
- MCP authentication or authorization;
- Postgres physical design;
- schema or migration authority;
- dashboard or operator-console requirements;
- strategy or recommendation storage.

---

## M14 Planning Boundary

M14 is active for planning and bounded prototype preparation only.

M14 may:

- audit the existing contracts, hammers, C2 fixture slice, and M13 provider evidence for read-boundary requirements;
- define typed read contracts for observations, provenance, scope, rights, retention, freshness, provider attribution, disagreement, and evidence handles;
- define safe filtering, pagination, bounded query shape, and deterministic error behavior;
- define consumer-safe redaction and field-visibility rules;
- define authentication and authorization requirements without exposing credentials or direct SQL;
- define MCP/tool guidance metadata and misuse-resistant tool descriptions;
- define read-time LLM context assembly boundaries;
- define prototype acceptance tests and hostile-path hammers;
- build a fixture-backed or local bounded prototype only after a separate implementation gate.

M14 must preserve:

```text
The Observatory stores what was observed.
The connected LLM interprets what it means at read time.
Accepted conclusions promote out to the owning consumer.
```

---

## M14 Non-Authorizations

This decision does not authorize:

```text
Postgres creation
physical schema
migrations
live provider ingestion
another paid provider request
bulk or recurring capture
customer data
customer first-party analytics storage
direct SQL access for LLMs or agents
database credentials for LLMs or agents
production API deployment
production MCP deployment
public exposure
dashboard work
customer-facing reports
strategy storage
recommendation storage
automatic conclusion promotion
```

Any M14 implementation requires a separate bounded task and acceptance gate.

---

## Audit Input

Because the last broad external Claude audit predates the completion of M8 through M13, a new repo-first deep audit is now appropriate.

The audit is advisory only. It must not become doctrine, roadmap authority, implementation authority, provider-spend authority, schema authority, or M14 build authority without owner review.

---

## Closure Result

```text
M13 closed.
M14 planning active.
No additional provider request authorized.
No schema or persistence authority granted.
```
