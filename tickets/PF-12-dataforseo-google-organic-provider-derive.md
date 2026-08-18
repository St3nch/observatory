# PF-12 — DataForSEO Google Organic provider Derivation and persistence

**Status:** ready  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none; PF-11 closed  
**Approved by:** Project Steward  
**Start commit:** to be recorded by the implementer

## Purpose

Derive the first DataForSEO Google Organic Outcomes and typed Observations from verified
Evidence into real PostgreSQL under the exact PF-11 recipe.

This ticket is the Google Organic analogue of PF-06/PF-07: it adds the provider-specific
Derivation and persistence boundary only. A later ticket will add adapter-aware recipe
selection and a surface-specific Google Organic read/history API, following the separation
already established by PF-08.

No provider exchange, acquisition widening, read API, recipe-selection mutation, or
cross-provider projection is authorized here.

## Authority and fixed identities

- D11 and D12
- the Provider Derivation section following resolved F11
- PF-04 provider recipe/envelope substrate
- PF-06/PF-07 provider write and exact-content idempotency precedent
- PF-10 accepted Google Organic Evidence contract
- PF-11 strict parser, typed IR, frozen Conformance fixture, and corrected semantic identity

Implementation begins from clean `main` at the ticket's recorded Start commit.

The accepted Google Organic recipe must remain byte-for-byte unchanged:

- adapter:
  `dataforseo-serp-google-organic-live-advanced-paid-probe-v1`
- recipe length: `2487` bytes
- derivation version:
  `338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde`

The PF-10 response fixture must remain byte-for-byte unchanged:

- length: `135722` bytes
- SHA-256:
  `7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f`

PF-12 may extend PF-11 typed IR only where necessary to retain non-identity occurrence
placement for persistence. It must not change the recipe axes, recipe bytes, parser
admission semantics, or the frozen response bytes.

## Dispatch and provenance boundary

Add a provider-specific Google Organic derive module/entrypoint following the bounded
Keyword Overview provider pattern. Do not make fixture `observatory.derive` reinterpret
provider Captures and do not dispatch by guessing from response JSON.

Derivation starts only from committed, verify-on-read Attempt/Capture/body Evidence whose
adapter is the exact Google Organic adapter above. Every normal Observation envelope cites
the verified `attempt_id`, `capture_id`, provider, adapter, and exact recipe identity.

Attempt-stage classification is `authorized_unresolved`. Capture-stage classifications are
the same closed provider taxonomy already accepted for the recipe:

- `no_response`
- `response_partial`
- `transport_complete_non_admissible`
- `provider_error`
- `provider_envelope_rejected`
- `reconciliation_failed`
- `observation_admitted`
- `observation_admitted_empty`

Provider errors, strict-parser failures, reconciliation failures, incomplete transport, or
damaged Evidence emit zero normal provider Observations for that Capture. Attempt-stage
Outcome may survive independently when the Attempt verifies.

## Observation kinds and typed detail

Persist all six PF-11 kinds under generic `observation_envelopes` plus kind-bound typed
relations. Each typed relation must carry the exact `observation_kind` and be structurally
bound to a matching envelope candidate key, as accepted in PF-06/PF-07.

### `dataforseo.google.organic.serp_feature_presence.v1`

Emit one Observation per admitted top-level item placement.

Identity axes are exactly:

- requested keyword
- provider item type
- page
- position
- `rank_group`
- `rank_absolute`

Persist those axes as typed placement testimony. Neither response-array index nor URL is
identity.

### `dataforseo.google.organic.ranked_result.v1`

Emit one Observation per admitted organic placement.

Identity axes are exactly requested keyword, page, position, `rank_group`, and
`rank_absolute`. Persist exact URL, provider domain, title, optional description state,
optional website-name state, and all placement axes.

Exact URL is content, not identity. The frozen PF-10 Capture has 97 organic placements but
only 87 unique exact URLs. All 97 placement Observations must survive; no URL-based
deduplication or normalization is permitted.

### `dataforseo.google.organic.ai_overview_presence.v1`

Emit the admitted AIO presence Observation identified by requested keyword. Persist
`asynchronous_ai_overview` and the provider placement axes. Do not interpret the flag as
an Observatory success/completeness state.

### `dataforseo.google.organic.ai_overview_source.v1`

Emit one semantic Observation per exact
`(requested_keyword, locus, exact_url)`, with `locus` remaining
`top_level` or `element`. Persist exact URL and the field-state/value pairs for provider
domain, title, and source.

PF-11's `element_index` and `reference_index` are occurrence testimony, never
Observation identity. Persist every admitted occurrence in a subordinate typed occurrence
relation:

- top-level occurrence: `element_index IS NULL`, nonnegative `reference_index`;
- element occurrence: nonnegative `element_index` and `reference_index`;
- no sentinel and no split Observation kind;
- constraints must distinguish top-level and element occurrence shapes;
- duplicate occurrence keys are refused rather than conflict-ignored.

All occurrences sharing one semantic identity must agree exactly on semantic detail
(including every field state/value). Disagreement is an ambiguous Derivation and fails
closed; do not choose first/last testimony.

The frozen fixture must produce 15 semantic AIO-source envelopes from 18 occurrence rows:
seven top-level and eleven element-level occurrences. Reordering returned reference arrays
may change occurrence indexes but must not change the semantic Observation identity set.

### `dataforseo.google.organic.related_question.v1`

Emit one semantic Observation per exact `(requested_keyword, title)`.
`question_index` is block-local occurrence/order testimony and is never identity.

PF-12 must retain the parent PAA block's provider placement
`(page, position, rank_group, rank_absolute)` on each question occurrence, extending the
typed IR if necessary without changing recipe bytes. Persist every occurrence in a
subordinate typed relation keyed by the semantic question plus parent block placement and
nonnegative block-local `question_index`.

A synthetic second PAA block with the same four titles must yield four semantic question
envelopes and eight occurrence rows. A restarted `question_index` must neither collide nor
create a new semantic Observation.

### `dataforseo.google.organic.related_query.v1`

Emit one Observation per exact deduplicated returned query string under the PF-11 identity
`(requested_keyword, query)`. Preserve the parser's exact-string, first-seen semantic
deduplication; do not normalize queries or recreate repeated per-page chips as new facts.

## Result context and time semantics

Persist the typed result context needed for later Evidence-backed reads under the
Capture/recipe Derivation unit, without turning it into extra Observation kinds:

- exact requested and provider-returned keyword testimony;
- request location/language context;
- `se_domain` field state/value;
- result `datetime` field state/value;
- `se_results_count` and `pages_count` field state/value;
- `items_count` and exact `item_types`.

Name and treat result `datetime` as provider SERP result/retrieval time. It is distinct
from Observatory Capture/acquisition time and is not Provider Update Time. Never inherit a
missing provider result time from Capture time or another structure.

Every optional state/value pair must be constrained so `stated` requires a non-NULL value
and non-stated states require SQL NULL. Retain legitimate zero, `FALSE`, and empty values.
PostgreSQL types must preserve exact testimony without binary-float round trip.

Provider cost, task UUID, and check URL do not become Observations or new API fields in this
ticket.

## Frozen-Capture cardinality

For the accepted PF-10 Capture, the recipe emits exactly 237 normal Observation envelopes:

| Kind | Envelopes |
|---|---:|
| SERP feature placement/presence | 111 |
| Organic ranked result | 97 |
| AI Overview presence | 1 |
| Semantic AI Overview source | 15 |
| Semantic related question | 4 |
| Related query | 9 |
| **Total / Outcome observation_count** | **237** |

The 18 AIO-source occurrences and four PAA occurrences are subordinate testimony and do not
increase `outcomes.observation_count`.

## Write semantics

- Register and use the exact accepted provider recipe; never write these rows under the
  fixture semantic label or a Keyword Overview recipe.
- One Capture's Outcome, typed result context, diagnostics, envelopes, typed details, and
  subordinate occurrence rows are atomic.
- Same recipe + same verified Evidence compares the complete intended row set. Identical
  content is idempotent; any planted mismatch, missing row, extra row, or occurrence-detail
  disagreement fails closed.
- Do not use `ON CONFLICT DO NOTHING` or last-write-wins as semantic equality.
- Diagnostics preserve PF-11 bounded unknown-extension paths.
- Two fresh PostgreSQL databases rebuilt from the same verified Evidence/recipe must be
  logically equivalent across all PF-12 relations.
- Schema changes are additive and must apply safely over the accepted PF-08 schema.

## Acceptance criteria

- [ ] Exact adapter/recipe dispatch from verified Evidence produces the closed
      Attempt/Capture Outcomes and no fixture-provider confusion.
- [ ] The frozen PF-10 response derives exactly 237 normal envelopes and the six exact
      per-kind counts above on real PostgreSQL.
- [ ] Every typed detail is kind-bound to its matching envelope in PostgreSQL.
- [ ] Feature and organic identities use provider placement axes, never array position or
      URL.
- [ ] All 97 organic placements persist despite ten duplicate exact URLs.
- [ ] AIO sources persist as 15 semantic Observations plus all 18 occurrences; nullable
      `element_index` is testimony, not a sentinel or identity axis.
- [ ] Same-identity AIO semantic-content disagreement fails closed atomically.
- [ ] PAA title identity survives reorder and a second block; parent block placement plus
      local index preserves all occurrences without identity collision.
- [ ] Related queries remain nine exact semantic facts for the frozen Capture.
- [ ] Provider result time is independently named/stored and never inherited from Capture
      time or mislabeled Provider Update Time.
- [ ] Field-state/value constraints, exact values, diagnostics, and provenance are enforced
      in PostgreSQL rather than only by Python planning.
- [ ] Provider/task/parser/reconciliation/transport failures produce their closed Outcomes
      and zero normal Observations.
- [ ] Damaged Attempt/Capture/body Evidence produces no Capture-stage provider rows; a
      separately verified Attempt-stage Outcome remains valid.
- [ ] Exact-content rerun is idempotent; planted envelope/detail/context/occurrence conflicts
      are refused.
- [ ] Two real PostgreSQL databases rebuilt from the same Evidence/recipe are logically
      equivalent.
- [ ] Existing fixture, Keyword Overview derivation/selection/API, and PF-11 parser behavior
      remain green.
- [ ] Ordinary tests perform zero provider/DNS activity.

## Required tests

- Real-PostgreSQL derivation of a committed synthetic PF-10-shaped Attempt/Capture using the
  exact frozen response bytes
- Exact 237 Outcome count and per-kind envelope/detail counts
- 97 placement rows versus 87 unique URLs, including duplicate-URL distinct identities
- AIO 15 semantic rows / 18 occurrence rows / 7 top-level / 11 element, including
  field-state agreement and planted disagreement refusal
- PAA reorder and duplicated second-block proof: four semantic rows / eight occurrence rows
- Wrong-kind typed-detail and invalid occurrence-shape PostgreSQL rejection
- Result-context field-state constraints and independent provider-result/Capture times
- Provider error, strict-envelope rejection, reconciliation failure, transport states, and
  Evidence damage
- Exact-content idempotency plus planted context/detail/occurrence mismatch
- Additive migration over an accepted populated PF-08 schema
- Two-database logical equivalence across every new table
- Full existing regression suite

## Out of scope

- Google Organic recipe selection or current-pointer mutation
- Google Organic Attempt/read/history API; cut that as the next ticket after PF-12
- generic `/observations` or cross-provider query contracts
- provider HTTP calls, new paid probes, recurring acquisition, or F12 orchestration
- another SERP adapter, device, locale, search engine, or acquisition surface
- AIO prose/markdown, sentence citations, PAA expanded answers, sitelinks,
  `related_result`, organic publication timestamp, top-stories/video detail
- URL normalization, Page identity, universal rank, scoring, strategy, or projection
- refactoring the shared parser kernel, `Field` type, or unrelated architecture
- F6 automation, F7 concurrency, F8 production auth, F9 HTTP writes, or F10 projections

## One implementation commit must prove

One verified Google Organic Capture can be re-derived into the exact accepted recipe's
237 semantic, typed, provenance-bound Observations while all AIO/PAA occurrence testimony
and duplicate organic URL placements survive without becoming identity.

## Implementer report required

The implementation commit must update this ticket to `review`, record its exact parent,
changed paths, acceptance-to-test map, commands/results, and state explicitly:

- whether the ticket or existing architecture was awkward;
- what generalized cleanly from PF-06/PF-07 and what did not;
- the weakest identity, aggregation, schema, transaction, or test assumption;
- any under-proved adversarial case or fixture surprise;
- why any changed PF-11 IR field is occurrence testimony rather than recipe identity;
- confirmation that recipe/fixture bytes and both accepted Keyword Overview recipe IDs are
  unchanged;
- confirmation of no provider/network call, no API/selection work, no other surface, and no
  push.

Do not broaden the implementation to fix adjacent findings. Report them for Steward
reconciliation.
