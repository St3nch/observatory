# Observatory Decisions

This register contains settled product decisions. Each entry names the rejected
alternative so future work can review the trade-off without reopening it by accident.

## D1 — Observatory is a standalone multi-consumer data service

**Decision:** Observatory acquires, validates, preserves, and serves reusable SEO/GEO
observation data for many present and future projects.

**Why:** Shared infrastructure prevents each project from building a partial evidence
store and lets historical value compound independently of any one consumer.

**Cost:** Observatory needs a stable service contract and operational ownership even when
only one consumer exists initially.

**Rejected:** Build Observatory as an internal component of the first strategy project.
That would couple the data's lifetime and model to one consumer.

## D2 — Every consumer uses the API

**Decision:** Projects, LLMs, agents, applications, and scripts interact only through a
versioned API. Internal tables, files, credentials, and storage layouts are private.

**Why:** A durable API boundary lets storage and implementation evolve without forcing
every consumer to migrate in lockstep.

**Cost:** Internal tools must obey the same boundary, and the API must support real
operational needs instead of relying on direct SQL shortcuts.

**Rejected:** Permit trusted local projects or LLM tools to read the database directly.
Trust does not remove coupling, migration risk, or accidental contract creation.

## D3 — Strategy stays downstream

**Decision:** Observatory stores observations and their provenance. Interpretation,
recommendations, scoring, reporting narratives, and SEO/GEO strategy belong to separate
consumer systems.

**Why:** Observation history remains broadly reusable only when it is not rewritten around
one project's judgment.

**Cost:** Downstream systems must join Observatory data with their own private context and
strategy state.

**Rejected:** Store strategy beside evidence for convenience. That would blur authority,
introduce consumer-specific state, and make the service less reusable.

## D4 — The data must survive changing software and infrastructure

**Decision:** Multi-year survival is a day-one architecture requirement. The system must
support migrations, upgrades, exports, verified restores, and re-derivation on fresh
infrastructure.

**Why:** Historical SEO/GEO observations cannot be recreated after the fact, and their
value increases over time.

**Cost:** Evidence identity, provenance, migration discipline, backup design, and recovery
verification constrain early implementation choices.

**Rejected:** Treat repository backup or a running database as sufficient durability.
Neither proves that the data can be restored, verified, and served correctly.

## D5 — Evidence and projections have different authority

**Decision:** Exact capture evidence and immutable attempt/outcome history are authoritative.
Parsed observations, indexes, summaries, and API query models are versioned and rebuildable.

**Why:** Provider shapes and parsers will change. Preserved evidence permits honest
reprocessing without rewriting history.

**Cost:** The service must track derivation versions and operate rebuild paths.

**Rejected:** Store only normalized rows or provider JSON. Normalized-only storage loses
source detail; JSON-only storage leaves consumer semantics unstable and implicit.

## D6 — Ordinary tests lead; hammer tests are bounded release work

**Decision:** Unit, integration, API, and real-PostgreSQL tests are the normal development
loop. Suspected high-consequence invariants enter a small backlog for one dedicated
adversarial-testing ticket near production readiness. A smallest decisive hostile test
runs earlier only when a foundational assumption would make continued work unsafe.

**Why:** This preserves development speed without pretending that mocks can prove
concurrency, crash, authorization, spend, or recovery claims.

**Cost:** The project must maintain a disciplined hammer backlog and may occasionally pause
early development for a narrow substrate test.

**Rejected:** Hammer every ticket or defer every hostile test until the end. The first
turns testing into the product; the second can reveal foundational failure too late.

## D7 — Documentation remains compact and pull-based

**Decision:** Observatory follows the VedaOps Project Method: one forcing choice at a time,
immediate decision records, explicit rejected alternatives, ticket-based planning, and
skills invoked only when they unblock the next build step.

**Why:** Prior projects proved that individually reasonable documents can collectively
outgrow execution.

**Cost:** Some useful-looking future design remains unwritten until needed.

**Rejected:** Generate a complete documentation system before implementation. That creates
scope and stale authority faster than it creates working software.
