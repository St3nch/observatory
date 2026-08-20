# AI-05 — Search Mentions provider Derivation and typed persistence

**Status:** technical review  
**Owner:** [GPT] Steward design / [GROK] technical review and later implementation  
**Blocked by:** GROK technical review and Steward reconciliation  
**Approved by:** not yet; this ticket is not ready for implementation  
**Review base:** 90e213f0a31067a4c19d29a94229f8748d3977ce  

## Purpose

Design and, only after a separate ready transition, implement the first Search Mentions
Derivation Recipe, semantic Observation identities, typed PostgreSQL persistence, and
deterministic rebuild proof for the exact closed adapter:

    dataforseo-ai-optimization-llm-mentions-search-mentions-live-paid-probe-v1

This is the persistence half of the Search Mentions vertical slice. AI-06 remains a separate
recipe-selection and read/history API ticket. AI-05 authorizes no provider exchange,
continuation request, recurring acquisition, Target Metrics work, second platform, or
cross-provider projection.

The current ticket is deliberately in technical review. GROK must challenge the proposed
identity, occurrence, schema, time, and complete-set rules before the Steward marks it ready.
No src/ or tests/ implementation may begin from this status.

## Authority and accepted foundation

- VISION data doctrine and survival requirement
- VOCABULARY definitions of Evidence, Outcome, Observation, Derivation, Derivation Recipe,
  Provider Update Time, Data Period, and Conformance fixture
- D11 recipe-addressed typed provider Derivation
- D12 bounded claimed-contract plus real-Evidence interpretation
- Capture Event v2, Provider Derivation after F11
- PF-04 through PF-08 provider recipe, envelope, typed-detail, writer, selection, and API
  substrate
- PF-12 Google Organic occurrence and complete-set precedent
- PF-14 provider read-integrity precedent
- PF-15 additive PostgreSQL migration hygiene
- AI-02 exact one-shot acquisition adapter
- AI-03 verified Evidence and restore proof
- AI-04 strict parser, typed IR, and frozen Conformance fixture

AI-04 closed at Steward commit 90e213f0a31067a4c19d29a94229f8748d3977ce.

Fixed fixture identity:

- path: tests/fixtures/dataforseo_ai_optimization_search_mentions_ai03.json
- bytes: 48466
- SHA-256: 8b3cd0fb0c9fa23c102696bfe6b7212396c0f7c110e9ca8ca5b8ee5af182e80a
- five item occurrences
- 48 source occurrences
- 60 monthly points
- total_count 3055, offset 0, items_count 5
- one opaque non-null continuation token

One body proves existence, not invariance. Synthetic adversaries remain required for duplicate
questions, duplicate URLs, field disagreement, order changes, nullable states, empty pages,
and provider failures. D12 does not justify another paid sample merely to increase sample
count for this already exercised branch.

## Boundary

AI-05 may add:

- one content-addressed closed Search Mentions Derivation Recipe;
- one dedicated Search Mentions derive module and local operator entrypoint;
- additive typed PostgreSQL relations and constraints;
- bounded parser-IR occurrence testimony only if persistence cannot otherwise retain it;
- zero-network real-PostgreSQL tests over the frozen fixture and synthetic mutations.

AI-05 must not add:

- provider transport, DNS, credentials, spend, continuation, polling, or another Evidence root;
- recipe selection or a current-pointer mutation;
- Attempt/read/history API behavior;
- Target Metrics, ChatGPT, another platform, or another acquisition surface;
- URL normalization, Page identity, brand/entity consolidation, scoring, recommendations,
  strategy, or reporting;
- a generic provider-derive framework or unrelated parser/migration refactor;
- Evidence mutation or PostgreSQL authority over raw bodies.

## Proposed Recipe contract for technical review

The Recipe is a closed canonical I-JSON document registered through the accepted provider
recipe substrate. Its derivation_version_id is SHA-256 of exact JCS Recipe bytes. The
implementation must publish the final byte length and digest and prove independent
recomputation.

The proposed Recipe fixes:

- exact provider and adapter contract;
- the AI-04 parser contract;
- verified Attempt parameters as request authority;
- task.data as non-authoritative provider echo testimony;
- closed-object drift with no tolerated additive-extension diagnostics in version 1;
- exact decimal cost parsing in the parser, while cost remains Evidence-only in AI-05;
- exact structural integers and I-JSON-safe BIGINT persistence;
- one-task/one-result declared-count reconciliation;
- item context reconciliation to verified Attempt platform, location, and language;
- opaque continuation treatment;
- item, monthly-period, and source semantics below;
- the closed Capture-stage Outcome taxonomy;
- exact-content and complete-set write behavior.

Any later change to these semantics requires different Recipe bytes and identity. The Recipe
does not claim that provider order, item index, source array index, token contents, answer
Markdown links, or raw value fields are Observation identity.

## Proposed Observation families

GROK must test whether these are the smallest honest families. Do not accept them merely
because they resemble Google Organic.

### 1. Search Mention result item

Proposed kind:

    dataforseo.google.ai_optimization.search_mention.v1

Proposed semantic identity axes:

- exact requested keyword from the verified Attempt;
- exact provider model_name;
- exact returned question.

The adapter already fixes Google platform, United States location, English language,
answer-scope word matching, offset zero, and limit five. Those remain typed Capture context
rather than redundant within-Capture identity axes.

Persist exact typed item detail:

- requested keyword;
- platform, model_name, location_code, and language_code;
- exact returned question;
- exact Markdown answer;
- ai_search_volume as nonnegative BIGINT;
- is_web_search_based;
- parsed first_response_at and last_response_at provider clocks;
- explicit states for search_results, brand_entities, and fan_out_queries.

For this Google Recipe the last three fields are required JSON-null testimony. Do not store
them as JSON blobs or reinterpret them using another platform schema.

Answer, current volume, boolean, clocks, and null-state fields are content, never identity.
A repeated semantic item identity must agree exactly on all item detail or reject the entire
Capture-stage unit as provider_envelope_rejected. It must never choose first/last, merge
answers, or silently discard one occurrence.

Persist every item occurrence in a subordinate relation carrying its nonnegative provider
item_index. item_index is physical occurrence/order testimony only and must never enter
within_capture_identity or Recipe axes. Identical duplicate item occurrences produce one
semantic envelope plus multiple occurrence rows.

### 2. Monthly AI search volume

Proposed kind:

    dataforseo.google.ai_optimization.search_mentions.monthly_search_volume.v1

Proposed semantic identity axes:

- exact requested keyword;
- exact provider model_name;
- exact returned question;
- provider-stated year;
- provider-stated month.

Persist exact nonnegative monthly search_volume. Data Period is the explicit year/month and
is independent of Capture time, the item first/last clocks, and current ai_search_volume.

A repeated semantic monthly identity must agree exactly on search_volume or reject the whole
Capture-stage unit. Persist a subordinate monthly occurrence row carrying item_index so
identical duplicate question items do not disappear. Monthly array position is neither
identity nor required persistent testimony because the explicit period is authoritative;
GROK must challenge this omission if provider ordering carries a distinct necessary fact.

Current ai_search_volume remains item detail and must not be derived from the newest monthly
point. The frozen fixture contains three real disagreements.

### 3. Structured Search Mention source

Proposed kind:

    dataforseo.google.ai_optimization.search_mentions.source.v1

Proposed semantic identity axes:

- exact requested keyword;
- exact provider model_name;
- exact returned question;
- exact structured source URL.

Persist exact typed source detail:

- exact URL, including query and fragment;
- title;
- domain;
- source_name;
- snippet;
- publication_date state/value;
- thumbnail state/value;
- source markdown state/value.

No URL normalization, Markdown-link extraction, domain deduplication, or Page identity.
The source optional fields remain required null-or-opaque-string states under AI-04.

Persist every source occurrence in a subordinate relation carrying item_index and the
positive provider rank. Rank is scoped to one item and is occurrence testimony, not semantic
source identity. Duplicate exact URLs within one item or across repeated semantic items must
remain separate occurrence rows.

All occurrences sharing one semantic source identity must agree exactly on source detail.
Disagreement rejects the entire Capture-stage unit as provider_envelope_rejected. Do not
select a preferred rank or metadata spelling.

## Proposed frozen cardinality

Under the proposed three-kind model, the accepted AI-03 fixture emits:

| Kind | Semantic envelopes |
|---|---:|
| Search Mention result item | 5 |
| Monthly AI search volume | 60 |
| Structured source | 48 |
| **Total / Outcome observation_count** | **113** |

Subordinate occurrence counts are:

- five item occurrences;
- 60 monthly occurrences;
- 48 source occurrences.

These occurrence rows and the Capture result-context row do not increase
outcomes.observation_count.

GROK must independently recompute these counts from the frozen fixture and challenge any
identity collision hidden by the fact that the live five questions and 48 URLs are unique.

## Proposed Capture result context

Persist exactly one Search Mentions result-context row per Capture and Recipe, structurally
bound to the exact Capture Outcome by derivation_version_id, attempt_id, and capture_id.

Proposed typed context:

- exact requested keyword, match_type, search_filter, and search_scope;
- Attempt platform, location_code, language_code, limit, and offset;
- result total_count, offset, and items_count;
- search_after_token state and exact opaque value.

The context makes the 5-of-3055 truncated page explicit. A transport-complete page is not a
complete-corpus claim. A JSON-null cursor and a non-null cursor remain distinct. The token
must never become identity, be decoded, be followed, or be exposed as authorization for
another request.

Provider root/task version, messages, durations, costs, task ID/path, and task.data echo
remain typed parser IR and raw Evidence in this proposal but are not duplicated into
PostgreSQL. GROK must specifically assess whether omitting any of them would make AI-06
materially under-specified. If one is justified, propose a bounded typed context column;
do not add JSONB or a generic provider-envelope dump.

A valid admitted empty page writes observation_admitted_empty, zero normal envelopes, and
one result-context row preserving total_count, offset, item count zero, and cursor state.

## Time rules

- Capture/acquisition time remains Evidence provenance.
- first_response_at and last_response_at are item-level provider response clocks.
- They are not Capture time and are not inherited by sources or monthly points.
- The proposal does not label them Provider Update Time without a stronger contract basis.
- Monthly year/month is Data Period only.
- Provider duration strings remain Evidence/IR durations, never timestamps.
- Missing time is not filled from Capture or sibling structures.

GROK must review whether first_response_at and last_response_at should be stored as
TIMESTAMPTZ, exact strings with checked grammar, or paired typed/exact testimony. The chosen
representation must retain their ordering constraint and must not imply precision or meaning
the provider did not claim.

## Outcome and failure behavior

Attempt-stage classification remains authorized_unresolved.

Capture-stage taxonomy is exactly:

- no_response
- response_partial
- transport_complete_non_admissible
- provider_error
- provider_envelope_rejected
- reconciliation_failed
- observation_admitted
- observation_admitted_empty

Parser/closed-contract failures, known-field drift, impossible counts, context disagreement,
or semantic duplicate-content disagreement produce zero normal Search Mentions rows.
Provider JSON errors remain provider_error. Damaged Attempt/Capture/body Evidence produces no
Capture-stage provider rows; a separately verified Attempt-stage Outcome may remain.

No normal rows from one Capture survive a whole-unit semantic disagreement.

## Schema and provenance requirements

Use existing provider_recipes, outcomes, observation_envelopes, and
derivation_diagnostics. Add only bounded Search Mentions typed relations.

Every typed detail relation must carry exact observation_kind and be structurally bound to a
matching generic envelope through the accepted candidate key. Every occurrence relation must
be bound to the correct typed parent, not merely to an arbitrary envelope identity.

The result context must cite a real matching Capture Outcome through the full provenance
tuple. Existing outcomes_identity must be present before the foreign key is applied.

Use BIGINT for provider structural/count/rank/volume integers within the accepted I-JSON safe
range. Use NUMERIC only for any decimal value that is actually authorized for persistence;
the current proposal persists no cost.

Field-state/value CHECKs must enforce stated plus non-NULL and non-stated plus SQL NULL.
Google-null-only item states must be constrained to json_null.

Schema changes are additive over the accepted PF-15 schema, preserve all existing fixture,
Keyword Overview, and Google Organic rows, and are idempotent. Same-named decoy constraints
on other relations must not suppress target constraints.

## Atomic and complete-set behavior

One Capture unit includes its Capture Outcome, result context, generic envelopes, all typed
details, all occurrence rows, and any diagnostics.

Same Recipe plus same verified Evidence is content-consistent, not conflict-ignored:

- compare every existing natural-identity row to intended content;
- restore a missing rebuildable planned row only if the final stored set becomes exact;
- reject content disagreement;
- reject a foreign-Attempt or extra Outcome;
- reject extra or missing context, envelope, detail, occurrence, or diagnostic rows;
- require exactly one intended Capture Outcome;
- require Outcome observation_count to equal both planned and stored envelope counts;
- compare all relevant tables before commit;
- never use ON CONFLICT DO NOTHING or last-write-wins as semantic equality.

Two fresh PostgreSQL databases rebuilt from the same verified Evidence and Recipe must be
logically equivalent across every AI-05 relation.

Do not extract a shared provider-derive kernel in this ticket. Report repeated structure and
a concrete later trigger instead.

## Required adversarial proofs

At minimum, a later ready implementation must prove on real PostgreSQL:

- exact frozen 113 semantic envelopes and per-kind/detail counts;
- exact 5/60/48 occurrence counts and one result context;
- exact 5-of-3055 truncation context and opaque cursor state/value;
- exact current-volume vector and separation from monthly points;
- exact answers, clocks, null-only states, and all 48 source URL/rank attachments;
- source query/fragment preservation and no Markdown-link synthesis;
- item reorder leaves semantic identity sets unchanged while occurrence indexes remain
  non-identity testimony;
- monthly reorder leaves semantic period identities unchanged;
- identical duplicate question items create one semantic item plus multiple occurrences;
- conflicting duplicate item detail rejects the whole Capture unit;
- duplicate exact source URL occurrences survive without URL identity collapse;
- conflicting same-identity source metadata rejects the whole Capture unit;
- duplicate monthly identity with conflicting volume rejects the whole Capture unit;
- wrong-kind typed detail, orphan/wrong-parent occurrence, invalid item index/rank, and
  state/value inconsistency are rejected by PostgreSQL;
- admitted empty page writes context but zero normal envelopes;
- provider error, parser rejection, reconciliation failure, partial/no-response, complete
  non-admissible transport, and Evidence damage produce the exact closed behavior;
- exact-content rerun, missing-row repair, planted extra rows, content conflict, wrong count,
  and foreign-Attempt Outcome behavior;
- migration over a representative populated PF-15 schema;
- fresh versus upgraded schema parity for the bounded AI-05 catalog;
- two-database logical equivalence;
- existing fixture, Keyword Overview, Google Organic, AI-04 parser, recipes, and frozen
  fixture identities remain unchanged;
- ordinary tests have no provider, DNS, credential, paid-gate, or external-network activity.

## Technical-review questions for GROK

Before implementation, inspect the current parser, provider recipe helpers, Organic/Keyword
Overview writers, migrations, and PostgreSQL tests. Answer directly:

1. Are the three proposed Observation families semantically honest, or should answer/current
   volume/source testimony be split differently?
2. Is exact model_name a necessary identity axis, a content field whose disagreement should
   reject, or a closed enum/context field? Explain the consequences across captures and
   duplicate items.
3. Does requested keyword plus model plus returned question safely identify a semantic item
   without using provider order? Name any collision the ticket misses.
4. Are item/monthly/source occurrence tables sufficient to preserve duplicate questions and
   duplicate URLs? Identify every nullable-key or restarted-index trap.
5. Should monthly array position be retained as occurrence testimony despite explicit
   year/month identity?
6. Is whole-unit rejection the correct response to same-identity answer, volume, or source
   metadata disagreement? If not, propose an identity that does not smuggle values or array
   indexes into identity.
7. Is the proposed 113 envelope count correct?
8. Is the result context sufficient for AI-06? Assess the opaque token, provider echo,
   cost/task metadata, truncation, and request/result agreement.
9. What is the least misleading PostgreSQL representation of first_response_at and
   last_response_at?
10. Which constraints must be relation-scoped or NULL-safe under PF-15?
11. Where can complete-set comparison false-green, especially with a second Recipe for the
    same Capture?
12. What generalized safely from PF-12, and what would be cargo-culting?
13. What is strongest, weakest, awkward, under-proved, or likely to become debt?
14. Did AI-04 parser semantics omit any field needed for correct persistence?
15. Is another provider probe materially justified before AI-05? D12 says no unless a
    distinct unexercised branch could change the contract; identify that branch precisely
    rather than asking for a statistical resample.

Return one of:

- READY_AFTER_TICKET_RECONCILIATION
- BLOCKED_BY_IDENTITY_OR_CONTRACT
- NEEDS_DISTINCT_PROBE

For every proposed correction, cite the exact current code/schema/test reason and supply
replacement ticket language. Do not edit any file during technical review.

## Review deliverable

GROK returns:

- loaded project-local skill paths;
- exact branch, HEAD, clean status, and origin divergence;
- confirmation that AI-05 is technical review, not ready;
- fixture byte/hash verification and independently recomputed cardinalities;
- answers to all 15 questions;
- proposed Recipe kind names and exact identity axes;
- proposed table/constraint shape;
- acceptance-to-test critique;
- strongest and weakest design points;
- false-green and migration risks;
- explicit recommendation;
- confirmation of no files changed, no provider/network/credential access, no PostgreSQL
  mutation, no implementation, and no push.

The Steward will reconcile the report into this existing ticket. Only a later Steward commit
may set Status ready and supply an exact implementation Start commit.

