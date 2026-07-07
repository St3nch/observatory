# The Observatory — Boundaries

Status: authority
Authority: boundary law
Purpose: define what The Observatory may and may not store, expose, or become

---

## Purpose

This file is the boundary law for The Observatory.

It exists to prevent scope drift, strategy-storage creep, customer-data contamination, and the classic software disease known as "what if we just add one more table." Spoiler: no.

---

## Core Boundary

The Observatory stores observations, not conclusions.

```text
The Observatory stores what was observed.
The connected LLM interprets what it means at read time.
Accepted conclusions promote out to the owning consumer.
```

The Observatory is the telescope.

The connected LLM is the astronomer.

The database must never become the astronomer.

---

## In-Scope Content

The Observatory may eventually store scoped, rights-labeled, provenance-complete observations such as:

- SERP observations
- ranking observations
- keyword demand observations
- AI answer-surface mention/citation observations
- public page snapshots
- public marketplace listing observations
- provider response metadata
- capture timestamps
- capture method
- capture actor or provider
- operator intent when applicable
- rights class
- retention class
- freshness/staleness metadata
- stable evidence IDs

These are observations. They are not recommendations, strategies, or accepted business conclusions.

---

## Out-of-Scope Content

The Observatory must not store:

- customer records
- customer identities
- customer orders
- customer engagements as business records
- customer report records
- customer deliverables
- customer consent records as the primary system of record
- customer private first-party analytics
- strategy records
- recommendations
- opportunity scores as truth
- execution plans
- agent action records
- accepted business decisions
- SearchClarity customer workflow state
- Neon Ronin workspace operational state
- Kaizen governance records

Those belong to the owning consumer system.

---

## Customer Boundary

Customer records are out.

SearchClarity or another consumer owns:

- customer identity
- order / engagement / report records
- private customer files
- consent records
- report delivery history
- private first-party analytics inputs

The Observatory may later store customer-scoped public search observations only if they are:

- scoped
- rights-labeled
- retention-labeled
- provenance-complete
- captured through approved methods
- allowed by the active roadmap gate

Customer-scoped observation does not mean customer database.

---

## Customer First-Party Data Boundary

Customer first-party data is out of Observatory.

Examples include:

- Google Search Console exports
- GA4 exports
- Etsy Stats
- Shopify analytics
- seller dashboard screenshots
- private conversion data
- customer-provided private performance files

Current allowed posture:

```text
Customer first-party series may be supplied to read tools as read-time overlays.
The Observatory aligns external observations against the supplied series.
The Observatory does not store the customer first-party series.
```

Changing this requires an explicit owner ruling and boundary update.

---

## Internal First-Party Telemetry Boundary

Owned internal first-party telemetry is a separate case.

The Observatory may eventually store owner-internal first-party performance observations only under explicit `internal`-scope handling.

Before any such storage, the project must define:

- internal scope rules
- rights class
- retention class
- provenance fields
- access controls
- read-tool behavior
- hammer tests

No internal first-party telemetry is admitted merely because it is owned. It still needs boundary handling.

---

## Strategy and Recommendation Boundary

Strategy and recommendations are forbidden inside Observatory storage.

The Observatory must not store:

- keyword recommendations
- content recommendations
- marketplace listing recommendations
- SEO strategy
- GEO strategy
- customer report conclusions
- opportunity scores as truth
- accepted action plans
- experiment plans
- agent task decisions

The connected LLM may interpret Observatory evidence at read time.

Accepted outputs must promote out to the owning consumer, such as:

- SearchClarity for customer-facing reports and service work
- Neon Ronin for workflow orchestration and review queues
- Kaizen for governance, decisions, improvement candidates, and implementation returns

Temporary LLM reasoning is not Observatory data.

---

## Provider Evidence Boundary

Provider data is observed testimony, not truth.

The Observatory must preserve:

- provider identity
- endpoint or capture source
- request context
- capture time
- returned payload or raw payload pointer
- provider-reported timestamps when available
- cost metadata when applicable
- confidence/freshness labels
- fact / estimate / observation labels

Provider disagreement must be preserved.

Do not average disagreement into fake truth.

Do not collapse different provider surfaces into one pretend-universal measurement.

---

## Rights and Retention Boundary

Rights and retention fail closed.

If the project cannot determine whether data may be captured, stored, reused, or retained, the default answer is no.

A future provider or capture instrument must define:

- permitted capture use
- storage rights
- retention rules
- reuse rules
- customer-scope rules where applicable
- deletion or purge expectations
- human approval gates

Unclear rights block capture or require capture-and-purge rules with explicit owner approval.

---

## LLM and Agent Access Boundary

LLMs and agents must not receive:

- direct PostgreSQL credentials
- direct SQL access
- arbitrary query tools
- table CRUD tools
- schema mutation tools
- provider spend tools without human approval
- direct write access to observation tables

Future access direction:

```text
LLM / agent
  -> typed MCP tools
  -> Observatory API
  -> validation / authorization / rights / provenance layer
  -> PostgreSQL
```

MCP tools are not database clients.

The API owns database access.

The LLM receives shaped evidence packs, not raw mystery rows.

---

## Hammer Test Boundary

Hammer tests are a hard gate for implementation.

Any future implementation that claims a boundary must prove it under real execution.

Required hammer categories will likely include:

- persistence
- contract
- append-only behavior
- scope isolation
- provenance enforcement
- rights fail-closed behavior
- retention enforcement
- provider disagreement preservation
- no strategy/recommendation storage
- no direct SQL/credential exposure
- hostile-path rejection

No fake coverage. No mock theater pretending to be proof.

---

## Killed Concepts

Killed ancestor concepts stay killed.

Explicitly killed or forbidden here:

- VEDA Brain
- intelligence synthesis tables inside Observatory
- persistent Observatory strategy layer
- recommendation store
- content graph ownership
- customer database
- direct SQL access for agents
- strategy/recommendation tables wearing renamed hats

If a proposal sounds like VEDA Brain with a fake mustache, it is still VEDA Brain.

---

## Deferred / Future Layers

Future layers may be discussed only as separate concerns unless owner ruling changes project law.

Deferred/future concepts include:

- Strategy / IMI layer outside Observatory
- dashboard or operator console
- cross-scope aggregate analysis
- embeddings or vector store
- automated recurring capture
- customer-facing report automation
- provider capture runner
- MCP/API implementation

Naming a future layer does not approve it.

Deferred means remembered, not built.

---

## Anti-Drift Admission Test

Every proposed table, tool, or file should pass this test:

```text
Does this store an observation, or does it store what someone thinks the observation means?
```

If it stores meaning, strategy, recommendation, or accepted conclusion, it does not belong in Observatory.

---

## Final Rule

```text
The Observatory can show the sky with brutal fidelity.
It must not decide what the sky means.
```
