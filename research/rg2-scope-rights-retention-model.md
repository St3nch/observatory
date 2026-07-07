# RG2 — Scope / Rights / Retention Model

Status: research output
Authority: source-grounded research input; not doctrine by itself; not schema approval
Milestone: M6 — Research Gate Execution
Date: 2026-07-07

---

## Gate question

What exact `scope`, `rights_class`, and `retention_class` model should govern observations before schema planning?

---

## Sources checked

Local/current sources checked during RG2:

- `02-boundaries.md`
- `01-harvest-register.md`
- `research/m5-research-gate-plan.md`
- `planning-inbox/repo-first-research-triage.md`

No current external source was required for this gate because RG2 is defining the project-local pre-contract model and does not admit a provider, marketplace, or legal exception. Provider/platform-specific rights remain delegated to later provider/capture gates.

---

## Current source-grounded findings

### F1 — Scope is flat, not a customer/project foreign key

The harvest register adapts Veda's thin `Project` partition into a flat `scope` plus `scope_class` label.

Initial `scope_class` values are:

- `internal`
- `customer_engagement`
- `market_watch`

Consumers translate their own identities into Observatory scope values. Observatory must not foreign-key into Kaizen, Neon Ronin, SearchClarity, or customer systems.

Implication:

- `scope` should be an Observatory-local label/identifier.
- Consumer-owned identifiers may be referenced as external locators only when needed.
- Scope does not make Observatory a customer database.

---

### F2 — Customer-scoped observation is allowed only as public evidence under strict controls

`02-boundaries.md` says Observatory may later store customer-scoped public search observations only if they are scoped, rights-labeled, retention-labeled, provenance-complete, captured through approved methods, and allowed by the active roadmap gate.

Implication:

- `customer_engagement` scope-class may exist.
- It must never contain customer records, identities, orders, private files, report records, consent records as primary system of record, or customer first-party analytics.
- Any customer-scoped public observation must be evidence about public surfaces, not customer workflow state.

---

### F3 — Customer first-party data remains read-time overlay only

`02-boundaries.md` says customer first-party data is out of Observatory and may be supplied to read tools as read-time overlays.

Implication:

- `customer_engagement` is not permission to store GSC, GA4, Etsy Stats, Shopify analytics, seller dashboard screenshots, private conversion data, or customer-provided private performance files.
- Overlay data must remain outside Observatory storage unless a future owner ruling changes the law.

---

### F4 — Internal first-party telemetry is separate and not automatically admitted

`02-boundaries.md` says owner-internal first-party performance observations may eventually be stored only under explicit `internal`-scope handling.

Before any such storage, the project must define internal scope rules, rights class, retention class, provenance fields, access controls, read-tool behavior, and hammer tests.

Implication:

- `internal` is a valid scope class, not a free pass.
- Internal first-party telemetry is a later contract/hammers problem.
- RG2 can define placeholders but cannot admit storage.

---

### F5 — Rights and retention fail closed

`02-boundaries.md` says if the project cannot determine whether data may be captured, stored, reused, or retained, the default answer is no.

The future provider/capture instrument must define permitted capture use, storage rights, retention rules, reuse rules, customer-scope rules, deletion/purge expectations, and human approval gates.

Implication:

- Every admitted observation must carry rights and retention classes.
- `unknown` cannot mean proceed.
- Unclear rights must block capture or force an explicitly approved capture-and-purge rule.

---

### F6 — Provider and capture rules refine rights per source family

RG1 found DataForSEO remains plausible but not admitted, and long-term raw payload retention remains unresolved.

Implication:

- Generic rights/retention classes are necessary but insufficient.
- Each provider or capture instrument must bind the generic model to source-specific rules.

---

## Proposed pre-contract model

This section proposes the model M7 should turn into contracts. It is not schema approval.

### Scope record concept

A future `scope` concept should carry at least:

```text
scope_id
scope_class
scope_label
owning_consumer
consumer_reference_kind
consumer_reference_value
created_at
status
notes
```

Required posture:

- `scope_id` is Observatory-owned.
- `owning_consumer` names the consumer boundary, such as `searchclarity`, `neon_ronin`, `kaizen`, `internal`, or `market_watch`.
- `consumer_reference_value` is a locator, not a foreign key into another database.
- `notes` must not contain customer private data.

Do not store:

- customer name as scope identity;
- customer email;
- customer account credentials;
- customer order/report IDs as primary business records;
- private files;
- private analytics payloads.

---

## Proposed `scope_class` vocabulary

### `internal`

Meaning:
Owner-controlled internal properties, experiments, or market evidence programs.

Allowed future use:

- owner-owned public web/SERP/GEO observations;
- owner-internal first-party telemetry only after explicit internal-scope contract/hammers;
- internal market-watch-like panels that are not customer engagements.

Forbidden:

- customer data;
- strategy records;
- accepted action plans;
- private analytics without explicit internal handling.

Example:

```text
scope_class: internal
scope_label: searchclarity_owned_site_visibility
owning_consumer: internal
```

---

### `customer_engagement`

Meaning:
Public evidence observed for, about, or around a customer engagement, while customer records remain in the consumer system.

Allowed future use:

- public SERP observations scoped to an engagement;
- public marketplace listing observations if platform/capture rules allow;
- public page snapshots if capture method is admitted;
- external evidence aligned at read time with customer-owned first-party overlays.

Forbidden:

- customer identity records;
- customer orders;
- customer report records;
- consent records as primary system of record;
- private customer files;
- GSC/GA4/Etsy Stats/Shopify analytics storage;
- seller dashboard screenshots unless future owner ruling explicitly admits a capture-and-purge or consumer-side path.

Example:

```text
scope_class: customer_engagement
scope_label: sc_engagement_public_visibility_2026_001
owning_consumer: searchclarity
consumer_reference_kind: external_locator
```

---

### `market_watch`

Meaning:
Pre-project or non-customer watch scope for observing a market, niche, SERP set, topic, platform, or evidence panel.

Allowed future use:

- query panels for niches;
- market-wide SERP/AI-surface observations;
- competitor/public surface observations when rights/capture rules allow;
- provider disagreement comparisons across public market evidence.

Forbidden:

- customer engagement leakage;
- cross-scope aggregate analysis without owner ruling;
- strategy/recommendation storage;
- broad recurring capture before provider/cost/rights/hammers exist.

Example:

```text
scope_class: market_watch
scope_label: etsy_cleaning_products_visibility_watch
owning_consumer: observatory
```

---

## Proposed `rights_class` vocabulary

The harvest register imports the six-way rights classification from Kaizen Decision 0010. RG2 proposes preserving it as the starting contract vocabulary:

| rights_class | Meaning | Default behavior |
|---|---|---|
| `expressly_permitted` | Source/provider/platform explicitly permits capture/storage/reuse under defined conditions | Allowed only within stated conditions |
| `expressly_restricted` | Source/provider/platform explicitly restricts relevant capture/storage/reuse | Block or purge as required |
| `not_expressly_prohibited` | No explicit prohibition found, but no explicit grant either | Requires owner-approved caution; not enough for broad storage |
| `not_expressly_granted` | Permission is not granted clearly enough for the intended use | Fail closed unless capture-and-purge is approved |
| `provider_clarification_required` | Terms/docs are ambiguous and provider clarification is needed | Block until clarified |
| `legal_review_required` | Risk or ambiguity is high enough that legal review is needed | Block until resolved |

Additional operational labels may be needed later, but these should not weaken the fail-closed rule.

---

## Proposed `retention_class` vocabulary

RG2 proposes a small initial retention vocabulary for M7 contract planning:

| retention_class | Meaning | Notes |
|---|---|---|
| `retain_until_review` | Preserve only until human/provider-rights review resolves retention | Safe default for uncertain sources |
| `retain_with_source_terms` | Retain according to provider/platform/source terms | Requires source-specific term binding |
| `retain_project_evidence` | Retain as durable Observatory evidence | Requires rights clearance and owner-approved contract |
| `capture_and_purge` | Capture temporarily, then purge within explicit window | Requires exact purge deadline and approval |
| `no_storage_overlay_only` | Do not store; use only as ephemeral read-time overlay | Required for customer first-party data under current law |
| `forbidden_no_capture` | Do not capture or store | Default for prohibited/high-risk cases |

Recommended default:

```text
rights unclear -> retention_class: forbidden_no_capture
```

or, if explicitly owner-approved for a narrow case:

```text
rights unclear but temporary verification allowed -> retention_class: capture_and_purge
```

---

## Required observation-level fields later

Every future observation should be able to answer:

```text
What was observed?
Who/what captured it?
For what scope?
Under what rights class?
Under what retention class?
When was it captured?
What source/provider/capture instrument produced it?
What raw payload or raw pointer supports it?
What must happen if rights are unclear or retention expires?
```

Candidate fields for M7/M10 discussion:

```text
observation_id
scope_id
scope_class
source_family
provider_or_capture_instrument
capture_method
captured_at
captured_by
operator_intent
rights_class
rights_basis
retention_class
retention_basis
retention_expires_at
raw_payload_pointer
raw_payload_sha256
freshness_status
evidence_id
```

This is a contract planning input, not schema approval.

---

## Examples

### Example 1 — owner internal public SERP observation

```text
scope_class: internal
rights_class: not_expressly_prohibited or provider-specific class
retention_class: retain_with_source_terms
```

Allowed only after provider/capture admission.

---

### Example 2 — customer engagement public SERP observation

```text
scope_class: customer_engagement
rights_class: provider-specific class
retention_class: retain_with_source_terms or retain_project_evidence
```

Allowed only if customer-scoped public observation is admitted for that evidence family. Customer identity and private analytics remain outside Observatory.

---

### Example 3 — customer GSC export overlay

```text
scope_class: customer_engagement
rights_class: not applicable to stored Observatory observation
retention_class: no_storage_overlay_only
```

Current rule: do not store in Observatory.

---

### Example 4 — market-watch AI citation panel

```text
scope_class: market_watch
rights_class: provider-specific class
retention_class: retain_with_source_terms
```

Allowed only after provider/source rights and methodology gates clear. No strategy/recommendation storage.

---

### Example 5 — ambiguous marketplace page capture

```text
scope_class: customer_engagement or market_watch
rights_class: provider_clarification_required
retention_class: forbidden_no_capture
```

Until marketplace/API/capture rules are researched and admitted, capture is blocked or remains deferred.

---

## Non-goals

RG2 does not authorize:

- schema design;
- migrations;
- provider admission;
- capture runner implementation;
- provider spend;
- long-term raw payload storage;
- customer first-party analytics storage;
- cross-scope aggregate exceptions;
- strategy/recommendation records.

---

## Owner-ruling candidates

Owner ruling is required before:

- allowing any cross-customer reuse beyond strict public-observation reuse rules;
- admitting customer first-party storage, which current law blocks;
- admitting owner-internal first-party telemetry storage;
- approving any retention exception for ambiguous provider/source terms;
- permitting capture-and-purge for unclear rights;
- admitting cross-scope aggregate reads;
- adding a new `scope_class` beyond `internal`, `customer_engagement`, and `market_watch`.

---

## Blockers carried forward

- M7 must turn this model into a contract before schema planning.
- Provider/capture-specific rights must be resolved in provider or capture admission gates.
- M8 must hammer rights fail-closed, retention fail-closed, scope isolation, and overlay no-storage behavior.
- Customer first-party overlay behavior still needs its own contract later.

---

## Feeds later milestones

- M7 scope / rights / retention contract
- M8 rights and retention hammers
- M10 schema planning
- M13 provider admission
- M17 owned telemetry overlay proof

---

## Final RG2 rule

```text
Scope says where an observation belongs.
Rights say whether it may exist.
Retention says how long it may survive.
None of them make Observatory a customer database.
```
