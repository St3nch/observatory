# Decision — Observatory v1 Acceptance

Status: accepted decision
Date: 2026-07-12
Milestone: M20 — Observatory v1 Acceptance
Owner ruling: explicit acceptance in project conversation

## Decision

The owner accepted the following ruling exactly:

```text
ACCEPT OBSERVATORY V1 AT THE BOUNDED PROOF-SYSTEM CEILING
ACCEPT THE M20 KNOWN-LIMIT AND DEFERRED-CAPABILITY REGISTER
CLOSE M20 WITHOUT AUTHORIZING PRODUCTION OR POST-V1 IMPLEMENTATION
```

## Accepted v1 ceiling

Observatory v1 is accepted as a bounded, local, evidence-only proof system.

Acceptance confirms that the repository has proven:

- observations remain separate from conclusions and strategy;
- scope, rights, retention, freshness, provenance, and evidence boundaries fail closed;
- customer records and first-party analytics remain outside durable Observatory storage;
- provider output remains attributed testimony rather than truth;
- provider disagreement remains first-class evidence;
- one narrow DataForSEO probe was controlled, reviewed, and purged with proof;
- typed-read behavior works as a bounded local prototype;
- SearchClarity evidence-support boundaries are useful without becoming report generation;
- synthetic overlay inputs remain ephemeral and unpromoted;
- repository archive and disposable restore recovery passed;
- 184 tests passed locally and from the restored repository.

## Companion acceptance

The owner also accepted:

```text
planning-inbox/m20-known-limits-and-deferred-capabilities.md
```

Those limitations are part of the v1 acceptance boundary and must remain visible.

## Explicit non-authorizations

This decision does not authorize:

```text
production deployment
post-v1 implementation
live Postgres or physical schema
migrations
provider expansion or new paid pulls
recurring capture
autonomous spend
customer data handling
customer report generation
production API/MCP
encrypted or off-machine recovery claims
cloud backup upload
automatic backup jobs
credentials or secret transfer
strategy or recommendation storage
destructive cleanup
```

## Milestone state

M20 is closed.

No post-v1 milestone, implementation package, production launch, or roadmap expansion is active. Any further work requires a new explicit owner-approved roadmap or bounded decision.

## Final rule

```text
Observatory v1 is accepted at the bounded proof-system ceiling only.
Proof-system acceptance is not production readiness.
No new authority is inferred from closure.
```
