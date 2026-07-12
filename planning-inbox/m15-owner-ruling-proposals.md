# M15 Owner-Ruling Proposals

Status: planning / owner-decision proposal
Authority: none until accepted in `decisions/`
Milestone: M15
Date: 2026-07-12

---

## Purpose

Present the minimum owner rulings required before the M15 SearchClarity consumer contract can be accepted or a bounded proof task can be authorized.

These rulings preserve the project boundary that SearchClarity owns customers, reports, recommendations, consent, delivery state, and private analytics while Observatory supplies governed evidence support only.

---

## OR-E1 — Report-safe references and customer-facing exposure

Proposed ruling:

```text
M15 treats report-safe references as a separate consumer-facing class from internal Observatory evidence handles.
```

For the first proof:

- report-safe references are synthetic and artifact-local;
- they are opaque and non-enumerable;
- they reveal no internal evidence handle, provider task ID, raw pointer, path, database identity, customer identifier, or other scope;
- they are resolvable only through the `searchclarity_internal` path in a later admitted implementation;
- customer-facing resolution is not implemented;
- SearchClarity owns placement and explanation in report artifacts.

This does not authorize production references or public lookup.

## OR-E2 — Marketplace evidence in customer reports

Proposed ruling:

```text
Marketplace report support remains blocked by default until the exact platform, public/private surface, capture method, rights, retention, and claim ceiling are admitted.
```

M15 may preserve contract requirements and synthetic blocked-path tests. It may not treat Etsy, Fiverr, Amazon, or another marketplace as admitted merely because the data is publicly visible.

No scraping, private dashboard inference, traffic/sales inference, or customer-behavior inference is allowed.

## OR-E3 — AI/GEO report-support thresholds

Proposed ruling:

```text
M15 does not create a durable AI visibility score or universal presence/absence claim.
```

Any future AI/GEO report support must preserve:

- prompt/query panel and version;
- answer surface;
- locale/device/account context where relevant;
- capture time;
- sample/run count;
- recurrence or volatility context;
- citation/mention/absence distinction;
- explicit statement that citation is not trust, endorsement, authority, recommendation, or influence.

A single run may support only a sampled point-in-time observation. Repeated-sampling thresholds remain a methodology decision under DR4/DR5 and are not invented by M15.

## OR-E4 — Provider disagreement in customer-facing work

Proposed ruling:

```text
SearchClarity may later show provider-attributed disagreement side by side, but Observatory must not choose a winner, average values into truth, or create a composite score.
```

The first M15 proof may demonstrate internal report-support metadata for side-by-side testimony only when fixtures exist. It may not generate customer-facing prose.

Provider methodology and incomparability caveats are mandatory.

## OR-E5 — Automatic report-support blockers

Proposed ruling:

The following evidence conditions automatically block report support for the affected claim:

```text
blocked_by_rights
expired_by_retention
withdrawn
invalidated
blocked_private_data
missing provider attribution for provider metrics
missing sampled context for absence claims
stale or unknown freshness for current-state claims
missing mandatory caveats
source/capture family not admitted
```

`superseded` may support historical-only use with an explicit status warning.

`stale` or `unknown` may support historical-only use when the claim intent permits it; they cannot silently support a current-state claim.

This is an evidence-support block, not approval or rejection of final SearchClarity wording.

## OR-F1 — Customer first-party overlay posture during M15

Proposed ruling:

```text
Real customer first-party overlays remain deferred to M17.
```

M15 may define overlay interfaces, blocked-path behavior, and hostile-path criteria only.

The first M15 proof must reject real overlay values, screenshots, CSVs, PDFs, exports, private files, and customer identifiers with `blocked_not_admitted` or `blocked_private_data`.

No overlay cache, logging of values, discard implementation, or comparison output is authorized.

## M15-R1 — Consent boundary

Proposed ruling:

```text
Customer consent remains a SearchClarity business record and is not stored in Observatory.
```

A future admitted request may contain a non-private consumer-side authorization assertion for an already admitted input class. It must not contain the customer's identity, signature, consent document, account ID, or private file.

The first proof does not implement consent handling beyond rejecting consent records and private identifiers.

## M15-R2 — Human review and customer-facing output

Proposed ruling:

```text
No Observatory report-support disposition authorizes customer-facing delivery.
```

SearchClarity owns human review, caveat translation, final wording, recommendations, acceptance, delivery, and revision state.

The first proof must always return:

```text
consumer_promotion_required: true
customer_facing_output_authorized: false
```

## M15-R3 — Bounded proof scope

Proposed ruling:

After contract and hostile-path acceptance, M15 may propose one local fixture-backed proof using:

- the accepted M14 typed-read prototype;
- committed synthetic Observatory evidence fixtures;
- sanitized provider evidence already admitted for structural/provider-testimony use;
- synthetic SearchClarity request and handoff fixtures with no real customer identity, private analytics, report prose, external files, or overlay values.

The proof remains:

- local-only;
- in-memory;
- no network listener;
- no real MCP registration;
- no Postgres;
- no persistence;
- no customer data;
- no overlays;
- no report generation;
- no SearchClarity repo integration;
- no provider calls.

Implementation requires a separate exact owner authorization.

---

## Recommended owner decision bundle

```text
ACCEPT OR-E1 separate synthetic report-safe reference class for M15 proof
ACCEPT OR-E2 marketplace evidence blocked until platform-specific admission
ACCEPT OR-E3 sampled-only AI/GEO posture; no invented repeated-sampling threshold
ACCEPT OR-E4 provider-attributed disagreement only; no winner/average/composite
ACCEPT OR-E5 automatic report-support blocker set
ACCEPT OR-F1 real overlays deferred to M17
ACCEPT M15 consent boundary
ACCEPT mandatory SearchClarity human review and customer-facing-output block
ACCEPT bounded M15 proof eligibility, not implementation
```

Do not combine implementation authorization with this ruling bundle.

---

## Still deferred

- production report-safe references;
- customer-facing reference resolution;
- final SearchClarity report language;
- real customer/private overlays;
- screenshot/file intake;
- marketplace platform admission;
- AI/GEO repeated-sampling methodology;
- customer reports and recommendations;
- SearchClarity production integration;
- provider execution;
- Postgres, schema, migrations, and production API/MCP.
