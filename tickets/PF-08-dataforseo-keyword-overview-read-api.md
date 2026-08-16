# PF-08 — Keyword Overview provider read API and recipe selection

**Status:** planned
**Parent spec:** `docs/specs/capture-event-v2.md`
**Kind:** read API
**Blocked by:** PF-07
**Approved by:** Project Steward
**Start commit:** <!-- implementer fills -->

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

<!-- implementer fills; may set Status: review; never Status: done -->

## Closure

<!-- Project Steward only -->
