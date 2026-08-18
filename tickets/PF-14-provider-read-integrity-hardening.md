# PF-14 — Provider read-path integrity hardening

**Status:** done  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none; PF-13 closed  
**Approved by:** Project Steward  
**Start commit:** `db0ceec246d19556be79cf40e1eb419b05e272ff`

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

These envelope/detail and subordinate-occurrence consistency checks apply to the two
provider history resources only. PF-14 does not add them to the shared provider
GET /v1/attempts/{attempt_id} audit representation. That resource continues to verify cited
Evidence and may still display a stale PostgreSQL observation_count until the corresponding
history read or a rebuild detects the projection mismatch; this is an accepted PF-14 limit.

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

Fixture provenance checks must not leak IntegrityError as HTTP 500. They must either retain
the existing direct HTTPException mapping or add an explicit fixture-path catch so every
new fixture integrity failure returns the stable HTTP 409 evidence_integrity_failure signal.

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
  classification is excluded while a healthy admitted sibling Capture remains in the same
  history response; captures: [] is not sufficient proof;
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

The fixture Attempt route refuses the bounded fixture-provenance inconsistencies, and both
provider history routes refuse the bounded admission/projection inconsistencies this ticket
can detect. Healthy Evidence-backed fixture and provider responses remain unchanged and GET
remains a read-only projection operation.

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

## Pre-implementation technical-review reconciliation

GROK completed the mandatory read-only review at
6d7ea14bb358556107a314560df2f1ac59f02850 with no design blocker and no authority decision.
The review confirmed the admission defect, Capture-wide count grain, complete recipe table
sets, occurrence-parent invariant, fixture cross-link feasibility, read-only implementation
shape, and the ticket's detection limits.

The Steward accepted three IMPORTANT clarifications into this amendment:

- fixture integrity failures must map to the stable 409 rather than escape as an uncaught
  IntegrityError;
- envelope/detail/occurrence consistency is explicitly history-only in PF-14;
- the KO admission adversary must retain a healthy admitted sibling to prevent an empty
  history false green.

Optional batching remains an implementation judgment. Shared-module relocation, migration
hygiene, authority refresh, and broader completeness mechanisms remain deferred.

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

## Implementation report

**Parent:** `db0ceec246d19556be79cf40e1eb419b05e272ff`  
**Child:** supplied in the implementer handoff (a commit cannot embed its own final hash).  
**Status:** `review`

### Loaded skills

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

### A. Start gate

- branch: `main`
- exact HEAD: `db0ceec246d19556be79cf40e1eb419b05e272ff`
- working tree: clean
- PF-14: `ready` at start; set `in-progress` then `review`

### B. Changed paths

- `src/observatory/keyword_overview_read.py` (admission predicate; Capture-wide key-set check)
- `src/observatory/google_organic_read.py` (Capture-wide key-set check; occurrence-parent check)
- `src/observatory/api.py` (fixture provider/adapter/parent provenance; HTTP 409)
- `tests/test_api_keyword_overview.py`
- `tests/test_api_google_organic.py`
- `tests/test_api_attempts.py`
- this ticket

No schema, migration, recipe, fixture, parser, identity, Derivation writer, Evidence, or selection change.

### C. Behavior

Keyword Overview history membership now requires
`classification IN ('observation_admitted', 'observation_admitted_empty')`.
After Evidence verify and before sort/limit, every matching candidate is checked
Capture-wide: envelope keys `(within_capture_identity, observation_kind)` must have
cardinality equal to Outcome `observation_count` and must equal the union of
recipe-enabled typed keys. CORE uses coverage+metrics. EXTENDED uses all seven
tables. One keyword's response arrays are never compared to the Capture count.

Organic history uses the same envelope/typed equality across the six semantic
tables. Result context and occurrence rows are excluded from the 237 count.
Every AIO source and every related-question parent must have at least one
occurrence. Admitted-empty (0 envelopes, 0 typed rows, context present) remains
valid.

Fixture `_verify_backing` now requires fixture `provider`/`fixture-panel-v1` on
the Attempt and every cited Capture, and `capture.attempt_id ==` requested
Attempt. Failures raise `HTTPException(409, evidence_integrity_failure)` and
cannot leak as 500. Provider Attempt GET is unchanged and may still show a stale
count.

Consistency SELECTs are batched with `capture_id = ANY(%s)` so cost is one
envelope query plus one query per recipe-enabled table (plus two Organic
occurrence-existence queries) per history request, not per candidate.

### D. Acceptance map

| Criterion | Proving test |
|---|---|
| KO non-admitted excluded; healthy sibling remains | `test_history_excludes_non_admitted_sibling_and_keeps_healthy_capture` |
| Multi-keyword Capture-wide check (471 vs 85 monthly) | `test_history_core_and_extended_shapes` |
| KO missing non-anchor typed row → 409; Attempt GET still 200 | `test_history_missing_typed_row_is_409` |
| KO wrong Outcome count → 409; Attempt GET still 200 | `test_history_wrong_outcome_count_is_409` |
| KO damage outside `limit=1` → 409 | `test_history_consistency_damage_outside_limit_is_409` |
| Organic missing typed row → 409 | `test_history_missing_typed_row_is_409` |
| Organic wrong Outcome count → 409 | `test_history_wrong_organic_outcome_count_is_409` |
| Zero-occurrence AIO / PAA → 409 | `test_history_zero_aio_occurrences_is_409`; `test_history_zero_paa_occurrences_is_409` |
| Organic damage outside `limit=1` → 409 | `test_history_consistency_damage_outside_limit_is_409` |
| Fixture cross-linked valid Capture → 409; sibling 200; unknown 404 | `test_fixture_cross_linked_capture_is_409` |
| Healthy fixture / CORE / EXTENDED / Organic / 237 / AIO 15/18 / PAA | existing PF-08/PF-13 tests remain green |
| Read-only after 409 GET | xmin/ops in KO missing-row and wrong-count tests; existing Organic/fixture read-only tests |
| Non-empty two-database equality | existing KO and Organic two-database tests |
| Network guard | KO module autouse guard; Organic existing guard |

### E. Validation

Before: HEAD `db0ceec246d19556be79cf40e1eb419b05e272ff`, dirty working tree with PF-14 edits.

| Command | UTC start | UTC end | Elapsed | Exit |
|---|---|---|---|---|
| `uv run pytest -q` | 2026-08-18T23:46:24.955Z | 2026-08-18T23:48:58.559Z | 153.604 s (pytest 153.04 s) | 0 |
| `uv run ruff check .` | 2026-08-18T23:48:58.560Z | 2026-08-18T23:48:58.595Z | 0.035 s | 0 |
| `uv run mypy` | 2026-08-18T23:48:58.596Z | 2026-08-18T23:48:59.065Z | 0.469 s | 0 |

`906 passed, 1 skipped, 1 warning`. Prior PF-13 count was 896. 48 source files. No leftover `observatory-ce05-*` container. Final suite covers the final product bytes (test rename and blank-line cleanup only; no logic change after pytest).

### F. Review

Code-review against `db0ceec246d19556be79cf40e1eb419b05e272ff`.

**Standards:** 0 hard. Residual: duplicated surface-local consistency helpers (in-scope); positional candidate tuples deferred.

**Spec:** 0 missing/partial/wrong. History-only consistency confirmed. Admission sibling proof present.

### G. Candid assessment

**Capture-wide vs keyword grain.** Envelope/typed equality and Outcome count are Capture-wide, including other requested keywords. History membership and response families remain requested-keyword grain. Organic occurrence-parent check is Capture-wide for matching candidates.

**Detected.** Non-admitted KO membership; missing typed row; extra/missing envelope vs typed keys; wrong Outcome count; zero-occurrence AIO/PAA parent; fixture cross-link and wrong fixture adapter/provider; Evidence damage (pre-existing).

**Undetectable without re-Derivation.** Coordinated delete of typed+envelope+matching count; deletion of the only candidate anchor; partial occurrence loss while ≥1 remains; value/identity corruption that preserves keys and counts. Provider Attempt GET may still display a stale count (accepted PF-14 limit).

**Query cost.** Batched: 1 envelope SELECT + 2 (CORE) or 7 (EXTENDED) typed SELECTs per KO history request; Organic 1+6+2. Independent of `limit`. Dominant cost remains Evidence `read_capture`/`read_attempt` per matching candidate.

**Helpers.** Surface-local copies are acceptable. No shared framework extracted. `load_provider_attempt` not relocated.

**Strong.** Admission hole closed. Capture-wide key-set avoids the one-keyword/471 trap. Fixture parent check is the exact missing provenance test. 409 vs Attempt GET 200 proves history-only scope.

**Weak.** Duplicated consistency helpers. KO admitted-empty filter remains unreachable via coverage. Naive per-request table count is fine today but still O(candidates) Evidence reads.

**False-green risks avoided.** Admission test keeps a healthy sibling. Two-database tests remain non-empty. Outside-limit damage uses a later Capture. Attempt GET 200 on stale count is asserted so the history-only limit cannot be mistaken for a missed 409.

**Ticket premises.** All held. No product defect in writers; these are read-path holes.

**PF-15 / next surface.** PF-15 still owns migration hygiene. Next acquisition history should ship with an admission predicate and Capture-wide envelope/detail key-set from day one, plus occurrence-parent rules taken from that surface's writer.

### H. Confirmations

- no schema/recipe/parser/identity/Derivation/Evidence/selection/new-surface change
- no provider/DNS/credentials/paid-gate use
- no push

### I. Commit

- parent SHA: `db0ceec246d19556be79cf40e1eb419b05e272ff`
- child SHA: recorded in this implementation commit

## Steward closure — 2026-08-18

**Accepted by:** Project Steward  
**Accepted implementation:** `307c1d19d682c0382c2a60655605ea88633e1e4c`  
**Accepted parent:** `db0ceec246d19556be79cf40e1eb419b05e272ff`

PF-14 is accepted and closed after GROK's mandatory pre-implementation technical review,
ticket reconciliation, one bounded implementation commit, independent Steward code review,
and independent operator verification.

Keyword Overview normal-history membership now requires an admitted Capture Outcome.
Every matching Keyword Overview and Google Organic history candidate is Evidence-verified
and then checked before sort/limit at full Capture/recipe grain: the envelope cardinality
must equal the Capture Outcome observation_count, and the recipe-enabled typed semantic key
set must equal the envelope key set. Keyword Overview CORE covers coverage and metrics;
EXTENDED covers all seven accepted kinds. The check never mistakes one requested keyword's
response arrays for the multi-keyword Capture-wide Outcome count.

Google Organic preserves the accepted 237-envelope boundary: result context and subordinate
occurrence rows are excluded, while every persisted AIO source and related-question parent
must retain at least one occurrence. Admitted-empty context with zero envelopes remains
valid. Fixture Attempt reads now require exact fixture provider/adapter provenance and each
cited Capture's parent Attempt, returning the stable 409 evidence_integrity_failure signal
for cross-links rather than leaking a 500.

The accepted implementation batches consistency SELECTs by matching Capture set. Added
database cost is one envelope query plus two CORE or seven EXTENDED typed-table queries for
Keyword Overview, and one envelope plus six semantic plus two occurrence-existence queries
for Organic, independent of the returned limit. Existing Evidence verification remains
per matching candidate and therefore O(matching history), consistent with the accepted
verify-all-before-limit rule.

Independent Steward review found no authority, spec, correctness, security, or scope
blocker. The diff is limited to the three read modules, three dedicated API test modules,
and this ticket. Independent static verification at the accepted child:

- `uv run ruff check .`: clean;
- `uv run mypy`: clean, 48 source files.

Independent operator verification at the accepted child:

- exact HEAD `307c1d19d682c0382c2a60655605ea88633e1e4c`;
- clean working tree before and after;
- `uv run pytest -q`: 906 passed, 1 skipped, 1 upstream Starlette/httpx
  deprecation warning, exit 0;
- 150.94 seconds wall time;
- no remaining `observatory-ce05-*` container.

Accepted limits remain explicit. Provider Attempt GET retains Evidence verification but does
not run the new history completeness checks and may display a stale PostgreSQL count.
Coordinated typed/envelope deletion with a matching Outcome-count rewrite, deletion of the
only candidate anchor, partial occurrence loss while another occurrence survives, and
value corruption that preserves persisted keys/counts remain undetectable without new
independent state or re-Derivation. Those mechanisms remain outside PF-14.

No schema, migration, recipe, parser, identity, Derivation, Evidence, selection, provider,
credential, paid-gate, network, or new-surface change occurred. Nothing was pushed during
closure.
