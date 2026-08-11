# Observatory Vocabulary

This file defines Observatory's canonical domain language. These terms are project
authority: schemas, APIs, tickets, tests, and agent work must use them consistently.
A new synonym does not create a new concept, and a new concept is not settled until this
file and any affected decision are reconciled by the Project Steward.

## Core terms

**API consumer** — A project, application, agent, LLM tool, or script authorized to use
Observatory through its versioned service contract.

**Attempt** — A durable record that external capture activity was requested or authorized,
including the context required to explain what was supposed to happen. An attempt exists
even when no provider response is received.

**Outcome** — The terminal transport result associated with an attempt, including success,
refusal, failure, malformed response, partial response, timeout, or another explicit state.
An outcome is not automatically an observation.

**Evidence** — The preserved request, response, metadata, timestamps, hashes, and software
context used to support an observation. Evidence remains distinct from later derivations
and interpretations.

**Observation** — An admitted, source-attributed fact derived from evidence. A failed,
refused, malformed, or unresolved attempt is not an observation.

**Projection** — A rebuildable, versioned representation optimized for queries or API
responses. A projection is never the sole surviving authority for an observation.

**Derivation** — A versioned, deterministic process that transforms preserved evidence into
observations or projections without changing the source evidence.

**Provider** — An external source or instrument that returns SEO/GEO-related data. Provider
output is attributed to that provider and is not treated as universal truth.

**Provenance** — The information connecting an observation to its provider, attempt,
outcome, evidence, capture context, and derivation.

**Strategy layer** — A separate downstream system that interprets observations and produces
recommendations, conclusions, scores, reports, or SEO/GEO strategy.

**Query panel** — A named, versioned measurement definition. Its long-term owning system is
deferred until multiple consumers require shared panel identity.

**Hammer test** — A rare adversarial proof for a named high-consequence invariant that
ordinary tests cannot adequately establish.
