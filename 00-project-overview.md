# The Observatory — Project Overview

Status: draft
Date: 2026-07-06
Owner: Project owner
Steward: The Observatory Project Steward (LLM-assisted)

---

## Purpose

This is the first document any human or LLM should read when working in `C:\dev\observatory`.

It exists to answer:

```text
What is the Observatory, what goal does it serve, what truth does it own,
how does it relate to Kaizen, Neon Ronin, and SearchClarity, and what
mental model prevents it from drifting into something else?
```

---

## Goal Statement

The Observatory exists to make a connected LLM dangerous at SEO, GEO, and SERP work.

Concretely, it is the historical evidence substrate that lets a connected LLM say, with grounding:

- "This improved after that change."
- "There is a money-making gap in this market we can take advantage of."
- "This keyword should no longer be used on this webpage."
- "Here is a detailed, evidence-cited visibility report for this customer."
- "This project is now mentioned/cited by AI answer surfaces; this one is not, and here is what changed."

The Observatory achieves this by storing longitudinal, provenance-complete, rights-labeled
observations of external search reality — SERP results, keyword demand, rankings,
AI-surface mentions and citations, page snapshots, and first-party performance for
owner-internal properties — and exposing them through typed, comparison-native read tools.

The database itself never forms an opinion. The connected LLM is the interpretation layer.

---

## Core Rule

The Observatory is a pure observatory.

```text
A telescope does not measure planetary distance. It observes.
The measurement, the interpretation, the conclusion — those happen elsewhere,
by other systems, using what the telescope saw.

The Observatory is the telescope. The connected LLM is the astronomer.
```

If a proposed capability cannot be described as something a telescope does,
it does not belong in the Observatory.

The Observatory observes external reality, records what it sees with timestamps,
provenance, and fidelity, and exposes it faithfully. It does not interpret on behalf
of its consumers. It does not propose action. It does not plan. It does not execute.
It does not store opinions, scores, strategies, or recommendations.

Every proposed table must pass the admission test:

```text
entity + observation + time + interpretation
```

Where interpretation is compute-on-read by the connected LLM — never a stored family.

(Carried from Veda ADR-001, `C:\dev\v-ecosystem-docs\ecosystem\decisions\ADR-001-veda-is-pure-observatory.md`.)

---

## Lineage

The Observatory is the third generation of this idea:

1. **Veda** (`C:\dev\v-ecosystem-docs`) — the observatory system of the V Ecosystem.
   Architecturally strong but embedded in a four-system ecosystem whose governance
   complexity killed it. Veda's own history purified it: VEDA Brain (intelligence
   synthesis) was eliminated (ADR-003), the content graph was transferred out (ADR-002),
   and the pure-observatory rule was made law (ADR-001).
2. **Kaizen-era Observatory** (`C:\dev\kaizen-docs`) — Decision 0009/0010 planned a
   dedicated Internet Marketing Intelligence database; Result 506 (packet 030B) parked it
   with a narrow evidence-only definition after the envelope grew too broad.
3. **This project** — the standalone rebuild. It keeps Veda's engineering discipline,
   Kaizen's governance and rights posture, Neon Ronin's boundary hygiene, and
   SearchClarity's provenance-honesty vocabulary, and drops the ecosystem ceremony.

The full inheritance record is `01-harvest-register.md`. The register is
decision-shaped: every inherited concept is dispositioned keep / adapt / kill / defer
with a source path and reason. Killed concepts stay killed.

---

## What the Observatory Is

- A standalone PostgreSQL evidence database plus a typed read/query surface (API and
  MCP tools) — the only door in or out.
- The single long-term home for external SERP / SEO / GEO / visibility observations
  across all of the owner's projects.
- Append-only where it matters: observations are historical truth and are never
  silently overwritten.
- Provenance-complete: every observation knows its source, capture time, capture
  actor, rights class, and fact/estimate/observation label.
- Scope-partitioned: every record belongs to exactly one scope, with a scope-class
  label (`internal`, `customer_engagement`, `market_watch`) that drives consent and
  retention behavior.
- LLM-first: the read tools are designed so a connected LLM can compare, diff,
  detect gaps, cite evidence by stable ID, and know the freshness and blind spots
  of what it is reading.

## What the Observatory Is Not

- Not Kaizen, not Neon Ronin, not SearchClarity, and not a subsystem of any of them.
- Not a strategy engine, scoring system, or recommendation store. VEDA Brain does not
  exist here. It was not moved, not renamed — it does not exist. Interpretation is
  produced fresh at read time by the connected LLM; accepted conclusions are promoted
  *out* to the consumer that owns them.
- Not a content graph or CMS model. Point-in-time snapshots of public pages are
  observations; a living editorial model of site structure is not, and belongs elsewhere.
- Not a customer database. Customer identities, orders, reports, intake, consent
  records, and customer first-party analytics live in SearchClarity's layer. See
  `02-boundaries.md`.
- Not Neon Ronin's sanitized-signal exchange. Workspace-derived signals are a separate
  flow with separate provenance and never enter this database.

Full boundary law lives in `02-boundaries.md`.

---

## Consumers and Relationships

```text
                         Kaizen
              (governs by reference; cites
               observation IDs in decisions,
               improvement candidates, returns)
                            |
   providers (DataForSEO,   |
   admitted instruments) ---+---> OBSERVATORY <--- typed read tools / pull-request queue
                            |        |
        +-------------------+--------+-------------------+
        |                            |                   |
   Neon Ronin                  SearchClarity        Connected LLM
   (consumer via its own       (consumer; keeps     (the astronomer:
   external-integration        customer records     interpretation,
   contract; workspace-        and customer         reports, gap
   scoped permissions)         first-party data     hunting, ranking
                               on its own side)     work — compute-on-read)
```

- **Kaizen** governs the Observatory's creation and evolution and stores references,
  never observation data. This project feeds Kaizen's parked M19 — see below.
- **Neon Ronin** treats the Observatory as an external integration under its own
  contract (`neon-ronin/docs/core/18-external-integration-contract.md`): workspace-scoped
  permission, read + queue action classes, no autonomous spending on pull requests.
- **SearchClarity** consumes evidence for customer reports. Customer-triggered data
  pulls are recorded as requests in job metadata; the resulting observations stay
  customer-clean and shared.
- **The connected LLM** is the reason this database exists. Every schema and tool
  decision is judged by one question: does this make the astronomer more dangerous?

Two flows, never merged:

```text
Flow B (ours):   providers / admitted capture instruments -> Observatory evidence
Flow A (theirs): workspace operational work -> sanitized signals -> Neon Ronin's layer
```

---

## Relationship to Kaizen M19

Kaizen's Milestone 19 (Observatory / Internet Marketing Intelligence foundation) is
parked and evidence-blocked (kaizen-docs Results 506 and 508). This project is the
evidence-gathering and definition workspace that will eventually feed an M19 reopening
packet. It is not a bypass of Kaizen governance. Schema implementation, provider
purchase, and data capture remain gated behind their named gates (OBR-01 rights
clarification first among them) until explicitly approved.

---

## Governance Posture

This project deliberately runs lighter than its ancestors:

- Flat doc set. No doc-authority tiers. No packet ceremony until friction earns it.
- Stewardship stance carried from Kaizen: **"not yet — earn it."** The default answer
  to new tables, families, tools, vocabularies, and automation is no, until real
  friction or evidence justifies yes.
- **Hammer tests are a hard gate.** No schema change, API change, or logic change
  ships without passing hammer coverage, including hostile-path coverage. Hammer
  doctrine is inherited from Veda ADR-006 and adapted in the harvest register (V13)
  and boundaries doc.
- Human approval gates all paid capture, provider admission, capture-instrument
  admission, and rights-posture decisions.
- Decisions that change project law get a file in `decisions/` when that folder is
  earned. Until then, dispositions live in the harvest register.

---

## Document Map

```text
00-project-overview.md     this file — identity, goal, telescope rule, relationships
01-harvest-register.md     decision-shaped inheritance record from Veda / Kaizen /
                           Neon Ronin / SearchClarity, plus new-capability list
02-boundaries.md           boundary law: what is in, what is out, scope model,
                           rights/provenance/access rules, anti-drift rules
(planned) consumer docs    one per consumer (Kaizen, Neon Ronin, SearchClarity),
                           written backward from that consumer's goals
(planned) build plan       families -> dimensions -> read-tool contracts -> first slice
(earned)  decisions/       project decision records, when ceremony is earned
```

---

## LLM Use Principle

A capable LLM should be able to infer from this document that:

- the Observatory stores what was observed, never what it means
- the connected LLM is the interpretation layer; interpretation is compute-on-read
- consumers connect through typed interfaces and never receive SQL or raw credentials
- customer records and customer first-party data are never stored here
- killed ancestor concepts (VEDA Brain, content graph ownership, strategy layers)
  must not be reintroduced under new names
- hammer tests and human approval gates are hard requirements, not suggestions

If an LLM could use this document to justify storing a score, a recommendation,
a customer record, or a planning conclusion in the Observatory, this document is failing.

---

## Final Rule

```text
The Observatory makes the astronomer dangerous.
It never becomes the astronomer.
```
