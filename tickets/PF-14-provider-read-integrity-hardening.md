# PF-14 — Provider read-path integrity hardening

**Status:** ready  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none; PF-13 closed  
**Approved by:** Project Steward  
**Start commit:** 59559a1e5cf1671f2867d902530032de6ab9685f

## Purpose

Make normal fixture, Keyword Overview, and Google Organic API success fail closed when
their rebuildable PostgreSQL provenance or typed Observation rows no longer agree with the
Capture Outcome being served.

This ticket reconciles the read-path findings from the independent milestone audit at
59559a1e. It is a bounded integrity hardening ticket, not a new feature, Derivation pass,
repair path, schema migration, shared-provider refactor, or acquisition-surface ticket.

## Authority and accepted precedent

- VISION data doctrine — a non-admitted path is not an Observation; API reads disclose
  omissions rather than silently serving incomplete testimony.
- D2 — consumers use the versioned API.
- D8 — every authoritative Evidence read verifies identities and referenced bytes.
- D11 — provider identity/provenance is exact and normal histories remain
  provider/surface-explicit.
- PF-08 — accepted Keyword Overview recipe-aware history and verify-before-limit behavior.
- PF-12 — accepted Google Organic Capture-wide Outcome count, six semantic Observation
  families, result context, and subordinate occurrence relations.
- PF-13 — accepted Organic admission predicate, full provenance join, verify-all-before-limit,
  and read-only API behavior.

PostgreSQL remains disposable and rebuildable. A detected mismatch means the API refuses
the stale or damaged projection with the existing 409 evidence_integrity_failure signal; a
GET never repairs, derives, or mutates either PostgreSQL or Evidence.

## Audit findings accepted into PF-14

### 1. Keyword Overview admission membership

The Keyword Overview history candidate query currently joins coverage, envelopes, and
Outcomes but does not require an admitted Capture Outcome. Match Organic's accepted
admission boundary:

- candidate membership requires Outcome classification observation_admitted or
  observation_admitted_empty;
- a planted coverage/envelope/non-admitted Outcome combination must not enter normal
  history;
- the full recipe/Capture/Attempt provenance join remains required;
- healthy Keyword Overview response JSON and ordering remain unchanged.

This is an admission filter, not permission to manufacture an admitted-empty Capture group.
The existing Keyword Overview coverage anchor and response contract otherwise remain
unchanged.

### 2. Capture-wide Outcome/envelope/detail consistency

Before sorting and limiting matching history candidates, validate each candidate at the
grain of its exact Capture and resolved recipe.

For both provider surfaces:

1. Load the complete observation_envelopes key set for the exact
   (capture_id, derivation_version_id). Keys are
   (within_capture_identity, observation_kind).
2. Require the envelope cardinality to equal the Capture Outcome observation_count.
3. Load the complete typed semantic-row key set for that same Capture and recipe from the
   surface's recipe-enabled Observation tables.
4. Require the typed semantic-row key set to equal the envelope key set exactly: no missing,
   extra, wrong-kind, or duplicate semantic row may be served as a complete Capture.
5. Perform this check for every matching candidate before history sort/limit. A damaged
   matching Capture outside the returned limit must still fail closed.
6. Raise IntegrityError on disagreement so the existing API boundary returns HTTP 409 with
   evidence_integrity_failure.

The check is deliberately Capture-wide. Outcome observation_count is Capture-wide, while a
Keyword Overview history response is filtered to one requested keyword and a single Capture
may contain several requested keywords. Never compare one keyword's response-array count
directly with the Capture Outcome count.

Keyword Overview semantic tables are:

- keyword_overview_coverage;
- keyword_overview_metrics;
- keyword_overview_monthly_search_volume;
- keyword_overview_search_volume_trend;
- keyword_overview_properties;
- keyword_overview_avg_backlinks;
- keyword_overview_search_intent.

Only kinds enabled by the resolved recipe participate. Coverage remains the accepted
candidate anchor. The whole-Capture consistency check may inspect rows for other requested
keywords in the same Capture; they are not added to the requested keyword's response.

Google Organic semantic tables are:

- google_organic_serp_features;
- google_organic_ranked_results;
- google_organic_aio_presence;
- google_organic_aio_sources;
- google_organic_related_questions;
- google_organic_related_queries.

google_organic_result_context is Capture context, not an Observation envelope.
google_organic_aio_source_occurrences and
google_organic_related_question_occurrences are subordinate placement testimony, not
Observation envelopes, and must not be counted toward the accepted 237.

### 3. Organic subordinate occurrence sanity

For a matching Organic candidate, every persisted semantic AIO source and every persisted
semantic related-question parent must have at least one subordinate occurrence at the same
Capture, recipe, and within-Capture identity. A parent with zero occurrences is inconsistent
with PF-12 Derivation and fails closed.

Existing foreign-key and locus constraints remain the database boundary for orphaned or
misattached occurrence rows. Do not add schema or re-derive Evidence on GET merely to make
the read path prove more than the persisted model records.

### 4. Fixture Attempt/Capture provenance

The fixture Attempt audit route must apply the same explicit provenance discipline already
used by provider reads:

- the verified Attempt backing fixture Outcome/Observation rows must be the exact fixture
  provider and fixture-panel-v1 adapter;
- every cited Capture must name the requested attempt_id as its parent;
- every cited Capture must be for the fixture-panel-v1 adapter and expected fixture provider
  fields exposed by the closed manifest;
- a valid Capture belonging to another valid Attempt cannot back the requested fixture
  resource merely because both Evidence bundles independently verify.

Missing, damaged, cross-linked, or wrong-adapter backing remains HTTP 409
evidence_integrity_failure. Ordinary unknown Attempts and no-derived-row behavior retain
their accepted 404 semantics.

## Honest detection boundary

PF-14 must not claim that a PostgreSQL-only read check proves equality with Evidence.

It detects at least:

- Outcome count disagreement with the complete envelope set;
- an envelope whose required typed semantic row is missing;
- a typed semantic key set that disagrees with envelopes;
- a zero-occurrence persisted AIO source or PAA question;
- non-admitted Keyword Overview candidates;
- fixture Capture-to-Attempt or adapter/provider cross-linking.

Without adding new independently derived state or re-running Derivation on GET, it cannot
prove:

- a coordinated deletion that removes typed rows and envelopes and also changes the Outcome
  count consistently;
- deletion of the candidate anchor itself, such as the only matching Keyword Overview
  coverage row or Organic result-context row, when no remaining selected-history row points
  at that candidate;
- loss of one occurrence when the same semantic AIO/PAA parent still has another occurrence;
- semantic correctness of surviving row values or identities against raw Evidence.

These are accepted limits for this ticket. Report them in the implementation assessment.
Do not smuggle Derivation, repair, Evidence-body parsing, a stored expected occurrence
count, or a broad Outcome scan into GET.

## Implementation constraints

- GROK is the sole writer of src/ and tests/.
- Keep history routes read-only and use the existing read-only connection discipline.
- No schema or migration change.
- No Evidence mutation, repair, automatic Derivation, or recipe selection write.
- No recipe, fixture, parser, identity, Outcome writer, or Derivation semantic change.
- No provider, DNS, credential, paid-gate, or network use.
- No new acquisition surface.
- Do not relocate load_provider_attempt or extract a universal provider-read framework.
  Shared-helper placement may be assessed and reported, but refactoring is out of scope.
- Preserve healthy fixture, Keyword Overview, and Organic response contracts byte-for-byte
  at the JSON data-model level.
- Preserve verify-all-before-limit and deterministic history ordering.
- Keep one bounded implementation commit and do not push without [CHAZ] authorization.

## Required adversarial proof

At minimum, tests must prove:

- a planted Keyword Overview coverage/envelope/Outcome candidate with a non-admitted
  classification is excluded from normal history;
- a real multi-keyword Keyword Overview Capture succeeds, proving the consistency check uses
  the full Capture rather than one keyword's returned arrays;
- deleting one non-anchor Keyword Overview typed row while its envelope remains yields 409;
- changing a Keyword Overview Capture Outcome count while complete rows remain yields 409;
- deleting one Google Organic semantic typed row while its envelope remains yields 409;
- changing a Google Organic Capture Outcome count while complete rows remain yields 409;
- an Organic AIO source or related-question parent with all its occurrences removed yields
  409, while the accepted 15-source/18-occurrence and four-question frozen response remains
  unchanged;
- a consistency-damaged matching candidate outside limit=1 still yields 409 before limiting;
- a verified fixture Capture cross-linked to the wrong valid fixture Attempt yields 409;
- normal fixture, Keyword Overview CORE/EXTENDED, and Google Organic selected/pinned reads
  remain logically unchanged;
- every new failure path leaves Evidence and PostgreSQL unchanged;
- two independently derived healthy databases still return equivalent provider histories;
- the network guard remains active and no provider path is invoked.

Tests must assert the exact 409 signal where corruption is detected and must avoid a
false-green pair of empty histories. Use real PostgreSQL and real local Evidence fixtures
where the existing suites do.

## Validation

Use targeted tests while implementing. Run the repository acceptance commands once after
the final implementation state:

- uv run pytest -q
- uv run ruff check .
- uv run mypy

Record UTC start/end, elapsed time, exit code, pass/skip/warning counts, exact HEAD, tree
state before/after, and leftover observatory-ce05-* containers. A type- or comment-only edit
after pytest must be named explicitly; otherwise the final suite must cover the final bytes.

Do not route the full suite through a synchronous MCP gateway.

## Out of scope

- migration constraint-name scoping, INTEGER-to-BIGINT widening proof, or fresh/upgrade
  constraint parity; those belong to PF-15 migration hygiene;
- AGENTS.md commands, provider-relation documentation, or the /v1 versus /api/v1 authority
  decision; those are Steward-only authority refresh work;
- element-level AIO references null-versus-absence recipe semantics;
- shared provider module relocation, helper deduplication, positional-tuple cleanup, cursors,
  indexing, or performance architecture;
- new schema, stored completeness digests, occurrence counts, or PostgreSQL repair;
- parsing or re-deriving Evidence during API GET;
- new recipes, new adapters, new surfaces, provider calls, scheduling, backup automation,
  auth, HTTP writes, or generic/cross-provider Observations.

## One implementation commit must prove

All three accepted read paths refuse the bounded projection/provenance inconsistencies this
ticket can detect, while healthy Evidence-backed fixture and provider responses remain
unchanged and GET remains a read-only projection operation.

## Mandatory pre-implementation technical review

Before editing any file, GROK must perform a deep read-only technical review against this
ticket and the exact Start commit. The review must inspect authority, PF-08/PF-12/PF-13,
read modules, schemas, writers, and adversarial tests; verify the actual count grains,
recipe-enabled table sets, candidate anchors, transaction behavior, and fixture manifest
fields; and identify false-green or performance risks.

GROK must stop and report one of:

- PROCEED UNCHANGED;
- AMEND TICKET, with exact blocking/important amendments;
- AUTHORITY DECISION REQUIRED.

No implementation, ticket edit, commit, full suite, or provider/network call occurs during
that review. Implementation begins only after Steward reconciliation.

## Implementer report required

The implementation commit must update this ticket to review and record exact parent/child,
changed paths, acceptance-to-test map, and command evidence. It must also report candidly:

- which invariants are proved at Capture-wide versus requested-keyword grain;
- which corruptions are detected and which remain undetectable without re-Derivation;
- query count/cost added before limit and the expected scaling behavior;
- whether helper placement remains acceptable without refactoring;
- strongest and weakest parts of the implementation and tests;
- false-green risks, synthetic-only adversaries, gaps, and improvements;
- whether any ticket premise proved wrong or exposed a product defect;
- what should influence PF-15 or the next acquisition surface;
- confirmation of no schema/recipe/Derivation/Evidence/provider/new-surface change;
- confirmation of no push.

Do not broaden implementation to repair adjacent findings. Report them for Steward
reconciliation.
