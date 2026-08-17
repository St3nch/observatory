# PF-08 — Keyword Overview provider read API and recipe selection

**Status:** review
**Parent spec:** `docs/specs/capture-event-v2.md`
**Kind:** read API
**Blocked by:** none; PF-07 closed
**Approved by:** Project Steward
**Start commit:** `df280e644e51ae1dd71aa1856ceab14814fa3d72`

## What to build

Expose the first provider-derived history through the versioned Observatory API without
breaking the existing fixture Attempt audit resource or pretending unlike provider surfaces
share a universal metric schema.

## Authority

- D2 — all consumers use the versioned API
- D11 — Attempt resource retained; adapter-aware recipe selection; provider/surface-explicit
  first history API
- F8 remains deferred: loopback/no-auth only
- F9 remains deferred: HTTP API stays read-only
- F10 remains deferred: no cross-provider projection table

## Recipe selection

The API must no longer apply one process-global `Settings.derivation_version_id` to every
adapter.

Add an adapter-aware current-recipe selection mechanism in rebuildable/operational state,
mapping an exact `adapter_contract` to one registered provider `derivation_version_id`.
Selection never deletes or rewrites prior versions. Provider read endpoints may accept an
explicit `derivation_version_id` to pin historical interpretation; otherwise they resolve
the selected recipe for their exact adapter.

The fixture endpoint may keep its existing configured fixture default for compatibility in
this ticket. Do not force fixture-v1 into the provider recipe selector merely for symmetry.

## Existing Attempt resource

`GET /v1/attempts/{attempt_id}` remains the Evidence-backed provenance/audit resource and
retains fixture logical compatibility. Provider Attempts may use a discriminated provider
representation or a bounded provider-specific extension only if the ticket's tests make the
response unambiguous; do not silently return fixture `panel_id/score` fields for provider
Observations.

At minimum the provider path must disclose:

- Attempt/Capture identities
- provider/adapter
- selected or explicitly pinned recipe identity
- provider Outcome classifications
- Evidence integrity 409 behavior

## Consumer history resource

Add one surface-explicit read resource for DataForSEO Labs Google Keyword Overview history.
The route name may follow the existing `/v1` router style but must identify DataForSEO,
Google Keyword Overview, and history rather than exposing a universal metric endpoint.

It must support at least:

- exact requested keyword filter
- current selected recipe or explicit recipe pin
- bounded Capture/acquisition-time range or bounded result limit/order suitable for history
- provider location/language/request context from provenance

Returned history exposes the typed PF-06/PF-07 Observation kinds with:

- exact requested keyword and returned provider keyword where applicable
- `attempt_id`, `capture_id`, provider, adapter, recipe identity
- Capture/acquisition context
- Provider Update Time independently
- Data Period independently for historical points
- field-level null/absence/not-requested state where applicable

It does not merge unlike Observation kinds into one score, choose strategy actions, or
collapse multiple provider recipe versions.

## Integrity

API success remains backed by verify-on-read of cited Evidence. Damaged Attempt/Capture/body
that backs selected provider rows yields HTTP 409 with the stable
`evidence_integrity_failure` signal, not a stale normal response.

## Acceptance criteria

- [ ] Fixture `/v1/attempts/{attempt_id}` logical responses remain equivalent under the
      fixture default and all CE-07 integrity behavior stays green.
- [ ] Two provider recipes for the same adapter can coexist; changing current selection does
      not mutate/delete prior derived rows.
- [ ] Explicit provider recipe pin returns that version even when another recipe is current.
- [ ] Selection for one adapter does not select a recipe for another adapter.
- [ ] Keyword Overview history returns multiple Capture-anchored testimonies in deterministic
      history order with full provenance and independent time/period fields.
- [ ] Historical monthly points remain period facts, not capture-time facts.
- [ ] Provider null/not-requested/unstated states remain distinguishable in API output.
- [ ] Damaged provider Evidence after derive returns 409 and no normal history payload.
- [ ] API reads do not mutate Evidence or derived PostgreSQL rows.
- [ ] API remains loopback/no-auth and read-only; F8/F9 are not claimed complete.

## Required tests

- Fixture CE-07 regression suite unchanged
- Adapter-specific current recipe selection
- Explicit old/new provider recipe pin
- Provider history by exact requested keyword
- Multi-Capture historical testimony including revised prior month
- Independent acquisition/provider-update/data-period serialization
- Field-state serialization
- Provider Evidence damage 409
- API read-only xmin/content proof
- Two-database rebuild-visible API equivalence for the same selected provider recipe

## Out of scope

- Generic `/observations` cross-provider query contract
- Universal keyword/topic identity across providers
- YouTube, Ahrefs, Semrush, or another DataForSEO surface
- F8 production auth/non-loopback
- F9 HTTP writes
- F10 projections/current-metric materialization
- Strategy/opportunity/recommendation APIs
- Additional provider calls

## One implementation commit must prove

The first real provider history is consumable only through a versioned, Evidence-backed,
recipe-aware API while fixture audit behavior and provider-version history remain intact.

## Implementation report

**Parent:** `df280e644e51ae1dd71aa1856ceab14814fa3d72`  
**Child:** recorded in this implementation commit.

**Loaded skills:**
- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

### A. Start gate

- branch: `main`
- exact HEAD: `df280e644e51ae1dd71aa1856ceab14814fa3d72`
- clean start: yes
- skills: the four project-local paths listed above

### B. Recipe selection schema

- relation: `provider_recipe_selections`
- identity: `adapter_contract PRIMARY KEY`
- selected: `derivation_version_id` (64-hex)
- candidate key: additive unique `provider_recipes_adapter_version`
  `(adapter_contract, derivation_version_id)`
- composite FK: `provider_recipe_selections_recipe`
  `(adapter_contract, derivation_version_id)` → `provider_recipes`
- populated PF-07 proof: `test_additive_selection_schema_works_on_populated_pf07_tables`
  creates `derivation_versions`/`provider_recipes` only, registers CORE+EXTENDED,
  then `apply_migrations`; recipes unchanged and unique/FK install
- wrong-adapter proof: Python `WrongAdapterRecipe` plus raw SQL `ForeignKeyViolation`
  (`test_wrong_adapter_selection_is_structurally_refused`)

### C. Selection service/operator seam

- module: `src/observatory/provider_recipe_selection.py`
- writer: `select_provider_recipe(connection, adapter_contract, derivation_version_id)`
- reader: `resolve_provider_recipe(connection, adapter_contract, pinned_version=None)`
- operator command:

```text
uv run python -m observatory.provider_recipe_selection \
  --adapter-contract dataforseo-labs-google-keyword-overview-live-paid-probe-v1 \
  --derivation-version-id <64hex> \
  [--database-url <dsn>]
```

- update: `INSERT ... ON CONFLICT (adapter_contract) DO UPDATE SET derivation_version_id`
- missing current selection: `ProviderRecipeNotSelected` / `provider_recipe_not_selected`
- unknown recipe: `UnknownProviderRecipe`
- wrong adapter: `WrongAdapterRecipe`
- invalid digest: `InvalidProviderRecipeId`
- no HTTP POST/PUT/PATCH selection route exists

### D. Provider Attempt API

- dispatch: validate 64-hex → `store.read_attempt` → paid adapter from verified
  Evidence; missing Attempt with leftover `outcomes` is 409; fixture adapter keeps
  `Settings.derivation_version_id`
- fixture JSON keys remain
  `{attempt_id, derivation_version_id, attempt_outcome, capture_outcome, observations}`
  with `panel_id`/`score` (`test_fixture_attempt_json_is_unchanged_when_provider_rows_exist`;
  CE-07 file unchanged)
- provider JSON: `attempt_id`, `provider`, `adapter_contract`, `derivation_version_id`,
  `recipe_resolution`, `attempt_outcome`, `capture_outcome`; no fixture observation list
- selected EXTENDED Capture `observation_count=471`; explicit CORE pin `10`; changing
  current selection to CORE does not delete EXTENDED rows

### E. History route

- `GET /v1/providers/dataforseo/google/keyword-overview/history`
- query: required `requested_keyword`; optional `derivation_version_id`;
  `limit` default 20 max 100; `order=asc|desc` default `asc`
- limit applies to Capture groups after verify/sort; one Capture is never truncated
- no-data: HTTP 200 with `captures: []` for a valid selected/pinned recipe and exact
  keyword with no coverage rows (including CORE-only Evidence under an EXTENDED pin)
- candidate Outcome join is the full natural key:
  `o.capture_id = c.capture_id AND o.derivation_version_id = c.derivation_version_id
  AND o.attempt_id = e.attempt_id`
- planted same-Capture/same-recipe/foreign-Attempt Outcome is ignored
  (`test_history_ignores_foreign_attempt_outcome_for_same_capture`)

### F. History response model

- top level: provider, adapter_contract, requested_keyword, derivation_version_id,
  recipe_resolution, observation_kinds, captures
- each Capture: attempt_id, capture_id, provider, adapter, recipe, authorized_at,
  request_started_at, transport_ended_at, request
  `{location_code, language_code, include_serp_info, include_clickstream_data}`,
  capture_outcome, typed families
- families are kind-specific objects; CORE omits EXTENDED keys
- no `score` / universal `value` / metric flattening

### G. Evidence integrity

- Attempt: `read_attempt`; Capture: `read_capture()` (full parent/body/pool verify)
- missing derived Evidence after derive: 409 `evidence_integrity_failure`
- tests: damaged Attempt manifest, Capture manifest, response body, and unlinked
  Attempt `COMMITTED`; no `captures` / `capture_outcome` on 409

### H. Recipe resolution

- current EXTENDED default: Attempt 471 + history EXTENDED kinds
- explicit CORE pin: Attempt 10 + CORE kinds only
- change current to CORE: default Attempt reports CORE; EXTENDED `outcomes` row remains 471
- no silent CORE↔EXTENDED fallback; unknown/wrong-adapter pin is 404

### I. Historical revision through API

- test-local two Captures under one store, same EXTENDED recipe
- keyword: `ai search optimization`; Data Period 2019-06
- values 0 then 7; later Capture has later `request_started_at`
- same `within_capture_identity` (semantic year/month identity)
- `order=asc` earlier Capture first; `order=desc` later first; `limit=1` returns one
  complete 85-point monthly series
- Data Period remains `{year, month}`, not acquisition time

### J. Field states

API examples from accepted/synthetic PF-03-shaped Evidence:

- stated zero: monthly 2019-06 `{"state":"stated","value":0}`
- stated FALSE: metrics `search_partners` `{"state":"stated","value":false}`
- stated empty array: metrics `categories` `{"state":"stated","value":[]}`
- JSON null: properties `core_keyword` `{"state":"json_null","value":null}`
- absent: omitted `local seo` coverage
  `{"state":"absent","value":null}` with `covered=false` and `metrics=null`

`not_requested` is not invented; PF-06/PF-07 did not persist it on emitted kinds.

### K. Independent clocks

For `ai search optimization`:

- metrics PUT: `2026-07-16 07:54:24 +00:00`
- backlinks PUT: `2026-08-01 07:28:00 +00:00`
- intent PUT: `2026-04-29 01:54:23 +00:00`

Monthly, trend, and properties omit `provider_update_time`.

### L. Decimal preservation

- stated NUMERIC values serialize with `format(Decimal, "f")` strings
- high-precision CPC `1.234567890123456789` survives; it is not
  `str(float(...))`
- backlinks `1571.3` is `"1571.3"`

### M. Adapter isolation

- DataForSEO selection stays on the paid adapter
- `test-provider-recipe-foundation-v1` selection is independent
- CORE cannot be selected under the test adapter (Python + FK)
- test recipe cannot be pinned on the DataForSEO Attempt/history path (404)

### N. Read-only proof

- API uses `default_transaction_read_only=on`
- `test_api_reads_do_not_mutate_provider_state` compares xmin/content of
  recipes, selections, outcomes, envelopes, and all seven KO tables plus
  `store.recorded_ops` before/after Attempt + history GET
- selection CLI is not invoked by GET

### O. Two-database equivalence

- same Evidence, same EXTENDED derive, same selection
- `GET .../history?requested_keyword=keyword research` JSON equal

### P. Regression

- CE-07 `tests/test_api_attempts.py` unchanged and green
- CORE digest `319af798f3e0b3e5fe4579539442c4ca5d384b683e1f4bce0f7a1b3e26cd5908`
- EXTENDED digest `cade41cb916bc5595f62ac8ea4ef73d6c688974a1ee5caad0c9d8f95f51664c7`
- PF-06/PF-07 derive tests remain in the full suite

### Q. Acceptance map

| Criterion / required test | Proving test |
|---|---|
| Fixture Attempt logical compatibility + CE-07 integrity | `test_fixture_attempt_json_is_unchanged_when_provider_rows_exist`; `tests/test_api_attempts.py` |
| Two recipes coexist; selection does not delete rows | `test_provider_attempt_selected_and_pinned_recipes`; `test_select_and_resolve_are_adapter_specific` |
| Explicit pin ignores current selection | `test_provider_attempt_selected_and_pinned_recipes`; `test_history_core_and_extended_shapes` |
| Adapter isolation | `test_wrong_adapter_selection_is_structurally_refused`; `test_selector_isolation_does_not_leak` |
| Multi-Capture history order + independent period | `test_historical_revision_is_visible_through_history_api` |
| Monthly points are period facts | same |
| Field-state distinguishability | `test_field_states_clocks_and_decimals` |
| Provider Evidence damage 409 | `test_provider_damage_returns_409` |
| API reads do not mutate | `test_api_reads_do_not_mutate_provider_state` |
| Loopback/no-auth/read-only; F8/F9 unclaimed | existing TestClient GETs; no write routes; F8/F9 not asserted complete |
| Adapter-specific current selection | `tests/test_provider_recipe_selection.py` |
| History by exact requested keyword | `test_history_core_and_extended_shapes` |
| History Outcome bound to envelope Attempt | `test_history_ignores_foreign_attempt_outcome_for_same_capture` |
| Independent clocks | `test_field_states_clocks_and_decimals` |
| Two-database API equivalence | `test_two_databases_return_equal_history` |

### R. Verification

- `uv run pytest -q` — 787 passed, 1 skipped
- `uv run ruff check .` — clean
- `uv run mypy` — clean

### S. Changed paths

- `src/observatory/api.py`
- `src/observatory/keyword_overview_read.py`
- `src/observatory/provider_recipe_selection.py`
- `src/observatory/migrate.py`
- `tests/test_api_keyword_overview.py`
- `tests/test_provider_recipe_selection.py`
- `tickets/PF-08-dataforseo-keyword-overview-read-api.md`

### T. Commit

- parent SHA: `df280e644e51ae1dd71aa1856ceab14814fa3d72`
- child SHA: recorded in this implementation commit

### U. Weakest area

History 409s if **any** coverage-matching Capture for the keyword/recipe is damaged,
including Captures that a `limit` window would have omitted. That is fail-closed and
tested for in-window damage, but it is stricter than “only the returned page.”
Selection is a mutable pointer with no prior-pointer history. `not_requested` is not
visible in API output because accepted PF-06/PF-07 rows do not persist that state on
emitted kinds.

GET Attempt 404 when the selected/pinned recipe has no derived rows is intentional
(selection is not a Derivation trigger). Missing Evidence with leftover Outcomes is
409.

### V. Scope confirmation

- no PF-09 / post-foundation work
- no generic observations API
- no write HTTP API
- no strategy
- no projection / current-metric layer
- no auth expansion
- no provider/sandbox call, DNS, credentials, or spend
- no Evidence mutation in product paths
- CORE and EXTENDED recipe bytes/digests unchanged
- no parser/reconciliation change
- no YouTube/other endpoint work
- no authority edits outside PF-08 implementer fields
- no push

### Review

Code-review against start commit. Valid findings addressed: unused 404 branch,
unused history 503 assignment, missing-Attempt-with-rows 409, `HISTORY_ADAPTER`
reuse. Steward review remediation: history Outcome join now includes
`o.attempt_id = e.attempt_id` so a planted foreign-Attempt Outcome for the same
Capture/recipe cannot supply classification or `observation_count`. Residual
judgement: closed-kind SQL in `_capture_group` is an explicit switch over the
seven accepted Observation kinds rather than a generic table walker.

### Implementer judgement

- Weakest selector design: operational pointer has no audit of previous current
  recipes; coexistence is proved only by leftover derived rows.
- History shape is surface-specific and verbose; Capture-group families are
  clearer than a kind union but make CORE vs EXTENDED key presence part of the
  contract.
- Discriminated Attempt resource (separate JSON, no fixture fields) rather than
  an extension of the fixture envelope, so CE-07 JSON stays literally keyed.
- Thinnest proof: two-database equality covers one history keyword, not Attempt
  plus every kind; damage-outside-limit-window 409 is implied by verify-all-
  candidates but not isolated.
- Adjacent leftover: fixture and provider still share `GET /v1/attempts/{id}`;
  a later ticket may want a documented media/type discriminator. Not changed here.

## Closure

<!-- Project Steward only -->
