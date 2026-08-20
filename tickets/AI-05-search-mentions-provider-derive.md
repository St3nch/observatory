# AI-05 — Search Mentions provider Derivation and typed persistence

**Status:** ready  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none; GROK technical review reconciled  
**Approved by:** Project Steward  
**Technical-review base:** 9782ab37b4a949c514c90feee0aa29a8940dde32  
**Implementation start:** the ready-transition commit supplied in the Steward handoff  

## Purpose

Implement the first Search Mentions Derivation Recipe, semantic Observation identities,
typed PostgreSQL persistence, and deterministic rebuild proof for the exact closed adapter:

    dataforseo-ai-optimization-llm-mentions-search-mentions-live-paid-probe-v1

This is the persistence half of the Search Mentions vertical slice. AI-06 remains a separate
recipe-selection and read/history API ticket. AI-05 authorizes no provider exchange,
continuation request, recurring acquisition, Target Metrics work, second platform, or
cross-provider projection.

GROK independently challenged the identity, occurrence, schema, time, and complete-set
rules and returned READY_AFTER_TICKET_RECONCILIATION. The accepted corrections below are
implementation authority. No provider call or additional probe is required.

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

## Recipe contract

The Recipe is a closed canonical I-JSON document registered through the accepted provider
recipe substrate. Its derivation_version_id is SHA-256 of exact JCS Recipe bytes. The
implementation must publish the final byte length and digest and prove independent
recomputation.

The Recipe fixes:

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

## Observation families

The accepted model has exactly three semantic families. Their occurrence relations follow
the accepted Organic distinction between semantic identity and repeated placement, but their
keys and field rules are Search Mentions-specific.

### 1. Search Mentions result item

Kind:

    dataforseo.google.ai_optimization.search_mentions.item.v1

Semantic identity axes:

- exact requested keyword from the verified Attempt;
- exact provider model_name;
- exact returned question.

model_name and question must each be nonempty exact strings. An empty semantic identity
string rejects the entire Capture-stage unit as provider_envelope_rejected. Whitespace and
Unicode remain exact testimony and are not normalized.

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

Persist every item occurrence in a subordinate relation. item_index is defined as the
zero-based index in the parsed items tuple and may be assigned by enumerate; it is not a
provider JSON field. It is physical occurrence/order testimony only and must never enter
within_capture_identity or Recipe axes. Identical duplicate item occurrences produce one
semantic envelope plus multiple occurrence rows.

All occurrence identity columns are NOT NULL. Item occurrence uniqueness is ordinary UNIQUE
on (capture_id, derivation_version_id, within_capture_identity, item_index). The occurrence
must foreign-key to the matching typed item parent, including exact kind, not merely to an
arbitrary observation_envelopes row.

### 2. Monthly AI search volume

Kind:

    dataforseo.google.ai_optimization.search_mentions.monthly_search_volume.v1

Semantic identity axes:

- exact requested keyword;
- exact provider model_name;
- exact returned question;
- provider-stated year;
- provider-stated month.

Persist exact nonnegative monthly search_volume. Data Period is the explicit year/month and
is independent of Capture time, the item first/last clocks, and current ai_search_volume.

A repeated semantic monthly identity must agree exactly on search_volume or reject the whole
Capture-stage unit. Persist a subordinate monthly occurrence row carrying item_index so
identical duplicate question items do not disappear. Monthly occurrence uniqueness is
ordinary UNIQUE on (capture_id, derivation_version_id, within_capture_identity, item_index),
with a foreign key to the matching typed monthly parent.

Monthly array position is not persisted: explicit year/month is the Data Period. Duplicate
question items with unequal monthly windows admit the union of periods. Overlapping periods
must agree on search_volume or the entire unit is rejected.

Current ai_search_volume remains item detail and must not be derived from the newest monthly
point. The frozen fixture contains three real disagreements.

### 3. Structured Search Mention source

Kind:

    dataforseo.google.ai_optimization.search_mentions.source.v1

Semantic identity axes:

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
source identity. Source occurrence uniqueness is ordinary UNIQUE on (capture_id,
derivation_version_id, within_capture_identity, item_index, rank), with a foreign key to the
matching typed source parent. Rank restarts per item, so omitting item_index is a collision.
Duplicate exact URLs within one item or across repeated semantic items must remain separate
occurrence rows.

All occurrences sharing one semantic source identity must agree exactly on source detail.
Disagreement rejects the entire Capture-stage unit as provider_envelope_rejected. Do not
select a preferred rank or metadata spelling.

## Frozen-Capture cardinality

Under the accepted three-kind model, the accepted AI-03 fixture emits:

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

Tests must independently recompute these counts. The live five questions and 48 URLs are
unique, so duplicate-identity behavior requires synthetic proofs; 113 is a frozen-Capture
count, not a provider invariant.

## Capture result context

Persist exactly one Search Mentions result-context row per Capture and Recipe, structurally
bound to the exact Capture Outcome by derivation_version_id, attempt_id, and capture_id.

Typed context:

- exact requested keyword, match_type, search_filter, and search_scope;
- Attempt platform, location_code, language_code, limit, and offset;
- result total_count, offset, and items_count;
- search_after_token state and exact opaque value.

The context makes the 5-of-3055 truncated page explicit. A transport-complete page is not a
complete-corpus claim. A JSON-null cursor and a non-null cursor remain distinct. The token
must never become identity, be decoded, be followed, or be exposed as authorization for
another request.

Provider root/task version, messages, durations, costs, task ID/path, and task.data echo
remain typed parser IR and raw Evidence only; they are not duplicated into PostgreSQL.
Echo disagreement remains recoverable from Evidence and IR. Do not add JSONB or a generic
provider-envelope dump.

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

Persist first_response_at and last_response_at as TEXT NOT NULL in the exact provider lexical
form already validated by AI-04. PostgreSQL must CHECK last_response_at >= first_response_at;
lexical order is valid for the fixed zero-padded UTC grammar and equality is legal. Do not
store TIMESTAMPTZ, dual timestamp columns, or label these clocks Provider Update Time.

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

No normal rows from one Capture survive a whole-unit semantic disagreement. A
provider_envelope_rejected unit writes its Capture Outcome with observation_count zero and
writes no result context, envelopes, details, or occurrences. Result context is written only
for observation_admitted and observation_admitted_empty.

## Schema and provenance requirements

Use existing provider_recipes, outcomes, observation_envelopes, and
derivation_diagnostics. Add exactly these bounded Search Mentions relations:

- search_mentions_items
- search_mentions_item_occurrences
- search_mentions_monthly_search_volume
- search_mentions_monthly_occurrences
- search_mentions_sources
- search_mentions_source_occurrences
- search_mentions_result_context

Every typed detail relation must carry exact observation_kind and be structurally bound to a
matching generic envelope through the accepted candidate key. Every occurrence relation must
be bound to the correct typed parent, not merely to an arbitrary envelope identity.

The result context must cite a real matching Capture Outcome through the full provenance
tuple. Existing outcomes_identity must be present before the foreign key is applied.

Use BIGINT for provider structural/count/rank/volume integers within the accepted I-JSON safe
range. Counts, volumes, and item indexes are 0..9007199254740991; rank is
1..9007199254740991. Monthly year is 1..9999 and month is 1..12, matching AI-04 rather than
Keyword Overview's narrower period bounds. Use NUMERIC only for a decimal value explicitly
authorized for persistence; AI-05 persists no cost.

Field-state/value CHECKs must enforce stated plus non-NULL and non-stated plus SQL NULL.
Google-null-only item states are state-only and constrained exactly to json_null; the generic
state/value helper is insufficient because it would admit stated or absent.

Put constraints for these new relations inside CREATE TABLE IF NOT EXISTS statements appended
to the current PF-15 schema sequence. Add a relation-scoped conrelid plus conname probe only
if an existing relation must be altered. Do not introduce a global-conname probe or copy
Organic's UNIQUE NULLS NOT DISTINCT: every Search Mentions occurrence key is NOT NULL.

Schema changes are additive over a representative populated PF-15 schema containing fixture,
Keyword Overview, and Google Organic rows, preserve those rows, and are idempotent.
Same-named decoy constraints on other relations must not suppress target constraints.

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

Complete-set comparison is scoped by (capture_id, derivation_version_id) and includes
attempt_id on Outcomes. Item and monthly occurrence sets compare
(within_capture_identity, item_index); source occurrence sets compare
(within_capture_identity, item_index, rank). Identity-only counts are insufficient.

A second Search Mentions Recipe for the same Capture must coexist under its own Outcome,
context, envelope, detail, and occurrence sets. Each Recipe's complete-set comparison must
ignore the other Recipe's rows without becoming Capture-global. observation_count is per
Recipe Outcome.

Two fresh PostgreSQL databases rebuilt from the same verified Evidence and Recipe must be
logically equivalent across every AI-05 relation, including token state/value, exact clocks,
Google-null states, item indexes, and source ranks.

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
- identical duplicate question items create one semantic item plus multiple occurrences,
  and their synthetic envelope count is recomputed rather than hardcoded to 113;
- empty model_name or question rejects the whole Capture unit;
- conflicting duplicate item detail rejects the whole Capture unit with zero context;
- duplicate exact source URL creates one semantic source plus multiple distinct
  (item_index, rank) occurrences without URL identity collapse;
- conflicting same-identity source metadata rejects the whole Capture unit;
- duplicate monthly identity with conflicting volume rejects the whole Capture unit;
- unequal duplicate-item monthly windows admit the union of nonoverlapping periods;
- empty sources and empty monthly arrays emit zero child envelopes without inventing absence;
- wrong-kind typed detail, orphan/wrong-parent occurrence, duplicate occurrence key, invalid
  item index/rank, and state/value inconsistency are rejected by PostgreSQL;
- admitted empty page writes context but zero normal envelopes;
- provider error, parser rejection, reconciliation failure, partial/no-response, complete
  non-admissible transport, and Evidence damage produce the exact closed behavior;
- exact-content rerun, missing-row repair, planted extra rows, content conflict, wrong count,
  and foreign-Attempt Outcome behavior;
- a second Search Mentions Recipe on the same Capture proves Recipe-scoped coexistence;
- migration over representative populated PF-15 fixture, Keyword Overview, and Organic rows;
- fresh versus upgraded schema parity for the bounded AI-05 catalog;
- two-database logical equivalence over every new column, not a selected thin projection;
- existing fixture, Keyword Overview, Google Organic, AI-04 parser, recipes, and frozen
  fixture identities remain unchanged;
- ordinary tests have no provider, DNS, credential, paid-gate, or external-network activity.

## GROK technical-review reconciliation

GROK reviewed the parser, recipe helpers, provider writers, migration catalog, and PostgreSQL
proofs from clean commit 9782ab37b4a949c514c90feee0aa29a8940dde32. He independently
verified the fixture digest, 5/48/60 occurrences, 3055/0 result context, 628-character opaque
cursor, five unique live questions, 48 unique live URLs, and fixture-specific 113 envelopes.

Recommendation: READY_AFTER_TICKET_RECONCILIATION. No additional provider probe is justified.

Accepted findings:

- the three semantic families remain intact;
- model_name is an exact identity axis and persisted content, not a fixed enum;
- item_index is zero-based parsed-array occurrence testimony, never Observation identity;
- every occurrence key is NOT NULL and uses ordinary UNIQUE with item_index;
- monthly array position is not persisted;
- same-identity disagreement rejects the whole Capture-stage unit;
- provider echo, costs, task metadata, messages, and durations remain Evidence/IR only;
- exact provider clocks are TEXT, not TIMESTAMPTZ or Provider Update Time;
- year bounds match AI-04 at 1..9999;
- complete-set comparison is Recipe-scoped and proves second-Recipe coexistence;
- migration proof begins from populated PF-15 state;
- AI-04 retains every field needed for persistence;
- continuation, other platforms, Target Metrics, and a shared derive kernel remain deferred.

This will be the third surface-local provider writer. Accept that duplication here. Reconsider
a shared kernel only at a fourth provider surface or after a real copy-paste complete-set
defect.

## One implementation commit must prove

One verified AI-03-shaped Capture re-derives into 113 semantic typed, provenance-bound
Observation envelopes while every item/monthly/source occurrence survives without becoming
identity, truncation and opaque cursor context remain explicit, and all failure, conflict,
migration, coexistence, and rebuild-equivalence paths above hold.

## Implementer report required

The implementation commit must fill Implementation start, set Status to review, and record
exact parent, changed paths, final Recipe bytes/digest, frozen fixture identity,
acceptance-to-test map, targeted/full commands and results, and no-container state.

Report candidly:

- what generalized safely from PF-12 and what did not;
- strongest and weakest identity/occurrence/constraint/complete-set proofs;
- every under-proved adversarial branch or fixture limitation;
- whether any accepted table or identity was awkward in actual code;
- any false-green discovered during TDD or two-database comparison;
- the exact future trigger for extracting a shared provider-derive kernel;
- confirmation that AI-04 parser and fixture bytes, existing Recipes, and existing rows are
  unchanged;
- confirmation of no provider/network/credential call, no selection/API/AI-06/Target Metrics
  work, no other surface, and no push.

Do not broaden implementation to fix adjacent findings. Stop at one clean implementation
commit for Steward review.
