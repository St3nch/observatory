# Observatory Glossary

**API consumer** — A project, application, agent, LLM tool, or script authorized to use
Observatory through its service contract.

**Attempt** — A durable record that external capture activity was requested or authorized,
including the context required to explain what was supposed to happen.

**Outcome** — The terminal transport result associated with an attempt, including success,
refusal, failure, malformed response, partial response, timeout, or another explicit state.

**Evidence** — The preserved request, response, metadata, timestamps, hashes, and software
context used to support an observation.

**Observation** — An admitted, source-attributed fact derived from capture evidence.

**Projection** — A rebuildable, versioned representation optimized for queries or API
responses.

**Derivation** — A versioned process that transforms preserved evidence into observations
or projections without changing the source evidence.

**Provider** — An external source or instrument that returns SEO/GEO-related data.

**Provenance** — The information connecting an observation to its source, capture context,
evidence, and derivation.

**Strategy layer** — A separate downstream system that interprets observations and produces
recommendations, conclusions, reports, or SEO/GEO strategy.

**Query panel** — A named, versioned measurement definition. Its long-term owning system is
deferred until multiple consumers require shared panel identity.

**Hammer test** — A rare adversarial proof for a named high-consequence invariant that
ordinary tests cannot adequately establish.
