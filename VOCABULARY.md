# Observatory Vocabulary

This file defines Observatory's canonical domain language. These terms are project
authority: schemas, APIs, tickets, tests, and agent work must use them consistently.
A new synonym does not create a new concept, and a new concept is not settled until this
file and any affected decision are reconciled by the Project Steward.

## Core terms

**API consumer** — A project, application, agent, LLM tool, or script authorized to use
Observatory through its versioned service contract.

**Attempt** — An immutable **attempt event** durably committed on the Evidence Store
**before** any fixture or provider transport I/O. It records that a specific prepared
credential-free request was authorized and may have been sent or charged, including the
safe request envelope, request-body state and identity, authorization-policy context,
software context, and a fresh 256-bit `attempt_nonce`. Its identity is `attempt_id`, the
full 64-character lowercase SHA-256 of the exact canonical UTF-8 RFC 8785/JCS attempt
manifest bytes (the identifier is not embedded in those hashed bytes). An Attempt may
exist with no Capture (**authorized/unresolved**). A retry or re-send always creates a
new Attempt with a new `attempt_id`.

**Capture** — An immutable **capture event** durably committed on the Evidence Store after
a transport outcome. It is the sole authoritative **transport testimony**: the duplicated
safe request envelope and request-body state/reference; when any response material exists,
the response envelope and response-body identity; and a `transport_state` of
`response_complete`, `response_partial`, or `no_response`. Its identity is `capture_id`,
the full 64-character lowercase SHA-256 of the exact canonical capture manifest bytes. A
Capture cites its `attempt_id`. Each committed Attempt permits at most one Capture.
Semantic provider interpretation is not stored as an immutable Capture fact.

**Outcome** — A derived, versioned, operator-facing classification over Attempt and
Capture state under a Derivation version. Outcomes are materialized in disposable
PostgreSQL for efficient access and are rebuildable from verified Evidence. An Outcome is
**not** an immutable Evidence event, **not** a substitute for Capture, and **not** a
parent of Evidence. Storage success is not observation success; an Outcome must never make
refusal, failure, malformed material, partial response, no response, or unresolved
activity masquerade as an Observation. Reclassification appends a new Outcome row under a
new or repeated derivation version per the uniqueness rules; it never mutates Capture.
“Current Outcome” is a rebuildable selection over versioned Outcome history.

**Evidence** — Verified preserved source material: committed Attempt manifests, committed
Capture manifests, and their referenced request and response body objects. Unresolved
recovery journals are authoritative recovery material until resolved, but are not committed
Capture events. Evidence is retained on the filesystem Evidence Store, not as
authoritative PostgreSQL rows. Exact request and response bytes are immutable
SHA-256-addressed filesystem objects.

**Evidence Store** — The filesystem subsystem that durably retains, verifies, inventories,
and recovers Evidence under a supported local POSIX root (store format 2). Do not conflate
Evidence (the preserved material) with Evidence Store (the subsystem that holds it).
Layout, commit markers, scrub, and recovery protocol are specified in
`docs/specs/capture-event-v2.md`.

**Observation** — An admitted, source-attributed fact produced by Derivation from a
verified Capture that passes adapter admission rules. Every Observation cites one verified
`capture_id`, its `attempt_id`, and a Derivation version. A failed, refused, malformed,
partial, no-response, unresolved, or admission-rejected path is not an Observation.
Observations live in rebuildable stores (typically PostgreSQL) and are never the sole
surviving authority for the fact.

**Projection** — A rebuildable, versioned representation optimized for queries or API
responses. A projection is never the sole surviving authority for an Observation.
Separate projection tables are deferred for fixture v1; the API may map Observation rows
directly.

**Derivation** — A versioned, deterministic process that starts from committed, verified
Capture events (and their bodies) and Attempts, produces Outcomes and—when admission
allows—Observations, without changing Evidence.

**request_fingerprint** — The full lowercase 64-hex SHA-256 of a versioned canonical
credential-free request-identity document (RFC 8785/JCS). It groups equivalent serialized
requests for path routing, investigation, and duplicate-authorization policy. It is not
an Attempt identity, authorization token, idempotency key that reuses an Attempt, or
Observation provenance identifier. `attempt_id` remains the content identity of the full
Attempt manifest (including `attempt_nonce`). The exact closed schema for the fingerprint
preimage and for Attempt/Capture manifests is normative in
`docs/specs/capture-event-v2.md` (store format 2, layout v1).

**Provider** — An external source or instrument that returns SEO/GEO-related data. Provider
output is attributed to that provider and is not treated as universal truth. The first
implementation remains fixture-only (`fixture-panel-v1`) and must not perform real
provider network activity.

**Provenance** — The information connecting an Observation to its Provider, Attempt
(`attempt_id`), Capture (`capture_id`), Evidence bodies, capture context, derived Outcome
classification where disclosed, and Derivation version. Authoritative reads verify cited
event and body identities before use.

**Strategy layer** — A separate downstream system that interprets observations and produces
recommendations, conclusions, scores, reports, or SEO/GEO strategy.

**Query panel** — A named, versioned measurement definition. Its long-term owning system is
deferred until multiple consumers require shared panel identity. The fixture contract’s
`panel_id` is a synthetic measurement identifier for the vertical slice only.

**Hammer test** — A rare adversarial proof for a named high-consequence invariant that
ordinary tests cannot adequately establish.
