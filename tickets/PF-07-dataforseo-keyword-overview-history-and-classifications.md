# PF-07 — Keyword Overview history, properties, backlinks, and intent

**Status:** planned
**Parent spec:** `docs/specs/capture-event-v2.md`
**Kind:** provider derivation expansion
**Blocked by:** PF-06
**Approved by:** Project Steward
**Start commit:** <!-- implementer fills -->

## What to build

Complete the first Keyword Overview recipe's useful typed provider testimony beyond PF-06:
historical monthly search volume, provider-computed search-volume trends, keyword properties,
average backlink summary, and search intent. Preserve each structure's independent provider
time semantics and the exact provider quirks already present in Evidence.

## Authority

- D11
- §Provider Derivation after F11
- PF-05 strict parser
- PF-06 provider derive spine

## Observation kinds

### `dataforseo.google.keyword_overview.monthly_search_volume.v1`

One Observation per exact requested keyword and provider `(year, month)` point.

- identity: exact requested keyword + year + month + kind, within Capture/recipe
- value: exact integer monthly search volume, including legitimate zero
- Data Period: exact year/month
- Capture/acquisition time remains separate provenance
- Provider Update Time is included only if the recipe explicitly establishes which provider
  timestamp governs the series; do not infer it from a sibling structure by convenience

Different Captures may legitimately disagree about the same historical month. Capture ID
keeps those testimonies distinct; no overwrite/current projection is created here.

### `dataforseo.google.keyword_overview.search_volume_trend.v1`

Typed provider-computed relative trend fields (`monthly`, `quarterly`, `yearly` or the exact
recipe-authorized equivalents). Preserve provider semantics; do not convert them into a
universal trend score.

### `dataforseo.google.keyword_overview.properties.v1`

Typed provider properties/classifications including the admitted fields present in the
recipe such as core keyword, keyword difficulty, detected language, language flag, and any
other explicitly accepted first-recipe property. Provider quirks are stored as testimony;
request language does not overwrite detected language.

### `dataforseo.google.keyword_overview.avg_backlinks.v1`

Typed average backlink summary with decimal-capable values stored exactly and its own
`last_updated_time` interpreted only as this kind's Provider Update Time.

### `dataforseo.google.keyword_overview.search_intent.v1`

Typed main/foreign intent testimony with its own Provider Update Time. Provider intent is an
Observation value, never an Observatory Outcome. Nullable/array forms follow the recipe's
field-state rules rather than being coerced to one shape.

## Acceptance criteria

- [ ] PF-03 monthly history produces deterministic point identities based on exact requested
      keyword + year/month, never array index.
- [ ] Point counts follow the actual frozen provider fixture rather than a hard-coded 12-month
      assumption.
- [ ] Legitimate monthly zero remains a stated numeric zero.
- [ ] Re-deriving a later synthetic Capture that revises one historical month creates distinct
      Capture-anchored testimony without rewriting the earlier row.
- [ ] Search-volume trend values remain provider-computed testimony with no strategy score.
- [ ] Keyword properties preserve exact provider quirks, nulls, and classifications.
- [ ] Average backlink decimal values are exact and use only the backlink structure's Provider
      Update Time.
- [ ] Search intent uses only the intent structure's Provider Update Time and preserves
      nullable/multi-valued intent semantics.
- [ ] No sibling provider timestamp is silently inherited by another Observation kind.
- [ ] Same-recipe exact-content idempotency, damage refusal, and two-database logical rebuild
      equivalence extend across all new kinds.
- [ ] PF-06 coverage/core metrics and all fixture regressions remain true.

## Required tests

- Real frozen PF-03 expected row counts/natural identities for every new kind
- Historical-period boundaries/identity and zero point
- Synthetic revised historical point in a later Capture
- Distinct provider timestamps across metrics/backlinks/intent
- Null versus stated array/string fields for properties/intent
- Integer-looking and decimal-looking backlink values normalize identically in type semantics
- Same-recipe conflict mismatch refusal across one new detail kind
- Full empty-DB rebuild equivalence on real PostgreSQL

## Out of scope

- SERP enrichment normalization (disabled in PF-03)
- Clickstream normalization (disabled in PF-03)
- Other DataForSEO endpoints or YouTube surfaces
- Cross-provider joins or projections
- Consumer/API history endpoint (PF-08)
- Additional paid calls

## One implementation commit must prove

The first provider recipe preserves the PF-03 historical and independently timed provider
structures as deterministic typed Observations without collapsing time, nulls, decimals, or
provider classifications.

## Implementation report

<!-- implementer fills; may set Status: review; never Status: done -->

## Closure

<!-- Project Steward only -->
