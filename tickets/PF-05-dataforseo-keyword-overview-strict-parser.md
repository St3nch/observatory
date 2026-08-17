# PF-05 — DataForSEO Keyword Overview strict parser and PF-03 conformance fixture

**Status:** ready
**Parent spec:** `docs/specs/capture-event-v2.md`
**Kind:** parser/conformance
**Blocked by:** none; PF-04 closed
**Approved by:** Project Steward
**Start commit:** <!-- implementer fills -->

## What to build

Build a zero-network, provider-specific parser for the exact paid adapter contract
`dataforseo-labs-google-keyword-overview-live-paid-probe-v1`. Promote the verified PF-03
response bytes into a frozen deterministic test fixture and prove a typed in-memory
interpretation plus fail-closed adversarial cases.

This ticket writes no provider-derived PostgreSQL rows and exposes no provider API.

PF-05 parses and validates the **full first-surface typed intermediate representation**,
including the field families later persisted by PF-07. PF-07 must reuse this parser/typed
IR rather than adding a second provider parser. PF-05 also authors the first production
Keyword Overview **core recipe** for PF-06, whose emitted kinds are coverage and core
metrics only. Adding the PF-07 Observation kinds is a semantic expansion and therefore
uses a new extended recipe digest in PF-07; the PF-06 recipe is never mutated in place.

## Authority

- D11
- D12
- `docs/specs/capture-event-v2.md` — §Provider Derivation after F11
- PF-03 exact paid Evidence and read-only inspector
- PF-04 provider recipe/Observation foundation

PF-03 is the accepted Provider contract probe for this exact live adapter. PF-05 continues
from its verified Evidence plus the claimed provider contract and bounded synthetic
adversarial cases. It does not restart Keyword Overview reconnaissance and does not claim
contracts for request-disabled SERP/clickstream enrichment, Standard/asynchronous workflows,
or other DataForSEO endpoints.

## PF-03 fixture acquisition

Read the exact response bytes only through the existing verified read-only paid-probe
inspection path. Record exact byte length and SHA-256 in the deterministic test vector, then
copy those exact bytes into the test corpus. Tests must not depend on the operator Evidence
root after the copy is established.

No capture command, provider network, DNS, credentials, or paid host is permitted.

## Parser contract

Implement a narrowly named DataForSEO Keyword Overview parser; do not grow the fixture
`_classify_capture` / `_admit_ok_results` code into provider parsing.

The parser must:

- strict-decode UTF-8;
- reject duplicate JSON object member names;
- reject `NaN`, `Infinity`, `-Infinity`, and equivalent non-finite constants;
- parse JSON structural integers as integers and decimal lexical forms without binary-float
  normalization; known decimal-capable provider fields accept integer or decimal lexical
  input and normalize exactly to `Decimal` or equivalent exact decimal values;
- validate the DataForSEO v3 envelope and the adapter's exact one-task/one-result contract;
- distinguish `tasks[0].result[0].items` from `result_count` and `items_count`;
- distinguish response/task execution-duration strings from Provider Update Time;
- preserve exact provider-returned keyword text;
- reconcile items against exact requested keywords from the verified Attempt parameters,
  never against array indexes or provider `task.data` echoes;
- parse provider timestamps under a provider-specific rule, not Observatory's frozen
  timestamp serializer;
- classify each known object as closed or extension-permitted per the first recipe;
- return stable diagnostics for tolerated additive fields on extension-permitted objects.

## Reconciliation rules

- Exact requested keyword is request authority and eventual Observatory subject.
- Exact returned keyword is provider testimony.
- The recipe-defined provider normalization is used only for matching.
- Result item order is irrelevant.
- A documented omitted requested keyword is represented in the typed parse result as provider
  no-data/coverage absence, not drift.
- Duplicate returned items, unrequested returned items, or an ambiguous many-request-to-one-
  provider-key normalization fail reconciliation.

The PF-03 real response does not prove every documented normalization edge; tests must add
synthetic collision vectors without claiming those collisions occurred in PF-03.

## Acceptance criteria

- [ ] Exact PF-03 response bytes are frozen with recorded byte length and SHA-256 after
      verify-on-read inspection.
- [ ] The parser walks `tasks[] -> result[] -> items[]` correctly and is independent of item
      order.
- [ ] Every PF-03 requested keyword is reconciled to the correct returned item or an explicit
      no-data omission state without using request/result position.
- [ ] Decimal-capable values retain exact decimal meaning for integer-looking and decimal
      lexical forms.
- [ ] PF-03 provider update timestamps are parsed independently for the structures that state
      them; execution durations are not timestamps.
- [ ] Present values, legitimate zero, JSON null, permitted absence, and request-disabled
      data are distinguishable in the typed parse result where the recipe requires it.
- [ ] Provider quirks in the frozen response are preserved verbatim rather than corrected.
- [ ] Duplicate JSON keys, non-finite numbers, known-field type drift, bad timestamp/period,
      impossible counts, duplicate/unrequested items, and ambiguous reconciliation fail
      deterministically.
- [ ] A permitted unknown additive field produces a stable diagnostic and does not alter
      known typed values.
- [ ] Full ordinary test/lint/typecheck suite remains zero-network.

## Required adversarial tests

- reorder the real `items` array
- duplicate a returned keyword item
- remove one requested keyword item
- add an unrequested item
- normalization collision between two synthetic requested keywords
- mismatch `items_count` / `result_count`
- duplicate JSON member name
- `NaN` / infinity
- integer lexical form versus decimal lexical form for one decimal-capable field
- malformed Provider Update Time
- invalid historical `(year, month)`
- provider task status error inside HTTP-complete testimony
- known nullable field as value/null/absent
- disabled SERP/clickstream field state from Attempt parameters
- unknown additive field on extension-permitted object
- unknown field on a closed object

- `tasks` length other than exactly one and `result` length other than exactly one
- `items` missing, JSON null, and an empty list in the all-omitted/no-data case
- top-level success with task-level failure, and the inverse inconsistent status shape
- integer-looking `1300` versus decimal-looking `1300.0` on a decimal-capable field
- a decimal with enough precision to prove there is no binary-float round trip
- invalid UTF-8, UTF-8 BOM, and trailing non-whitespace data after the JSON document
- Provider Update Time missing versus explicitly JSON null where the recipe permits either
- duplicate historical `(year, month)` points inside one returned keyword item
- negative monthly search volume
- invalid month `0` / `13` and recipe-invalid year bounds

## Out of scope

- PostgreSQL provider Outcomes/Observations
- API routes or recipe selection
- Other DataForSEO endpoints/sandbox parsing
- Live contract tests
- Additional paid calls
- Cross-provider abstractions

## One implementation commit must prove

The exact real PF-03 body and bounded mutants deterministically parse into a strict typed
Keyword Overview interpretation without provider network or PostgreSQL side effects.

## Implementation report

<!-- implementer fills; may set Status: review; never Status: done -->

## Closure

<!-- Project Steward only -->
