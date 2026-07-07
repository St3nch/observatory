# RG1 — DataForSEO Rights / Retention / Cost

Status: research output
Authority: source-grounded research input; not doctrine by itself; not provider admission
Milestone: M6 — Research Gate Execution
Date: 2026-07-07

---

## Gate question

What are the current DataForSEO rights, retention, storage, reuse, pricing, endpoint, and stop-condition requirements for Observatory use?

---

## Sources checked

Official/current sources checked during RG1:

- DataForSEO Pricing — `https://dataforseo.com/pricing`
- DataForSEO Product Pricing — `https://dataforseo.com/pricing-list`
- DataForSEO SERP API Pricing — `https://dataforseo.com/pricing/serp`
- DataForSEO AI Optimization API Pricing — `https://dataforseo.com/pricing/ai-optimization`
- DataForSEO Terms of Service — `https://dataforseo.com/terms-of-service`
- DataForSEO Privacy Policy — `https://dataforseo.com/privacy-policy`
- DataForSEO Data Processing Agreement PDF — `https://dataforseo.com/wp-content/uploads/2026/06/DataForSEO_DPA-12-06-26.pdf`

Local context sources for later cross-check:

- `research/m5-research-gate-plan.md`
- `planning-inbox/repo-first-research-triage.md`
- `02-boundaries.md`
- `planning-inbox/m4-boundary-reconciliation.md`

---

## Current official-source findings

### F1 — Pricing posture is pay-as-you-go with a minimum payment

DataForSEO describes its pricing as pay-as-you-go: customers pay only for individual services consumed.

The pricing page states a minimum payment amount of `$50`.

Implication for Observatory:

- The reserved validation budget aligns with the public minimum payment amount.
- No provider spend is authorized by this research doc.
- Any later validation pull must still have a recipe, endpoint list, ceiling, stop conditions, and owner approval.

---

### F2 — Account panel includes cost-management tools

DataForSEO says the account panel includes free cost-management tools for monitoring usage/spending, controlling budgets, setting limits, and more.

Implication for Observatory:

- Any later provider-admission plan should require account-level spend controls before a pull.
- Identical/repeated task submission must be treated as a cost-risk hammer case.

---

### F3 — Product surface is broad; first validation must stay narrow

The current product/pricing pages list major API families including SERP API, AI Optimization API, DataForSEO Labs API, Keywords Data APIs, Backlinks API, OnPage API, Merchant API, Business Data API, Reviews API, Domain Analytics API, Content Analysis API, and app/marketplace-related surfaces.

The AI Optimization pricing page specifically lists:

- LLM Mentions
- AI Keyword Search Volume
- LLM Responses
- LLM Scraper

Implication for Observatory:

- The first validation plan should not sample everything.
- Candidate first validation endpoint families should be limited to the minimum evidence slice needed for later M9/M13 decisions.
- AI Optimization is relevant, but must remain methodology-cautious because AI-surface evidence is volatile and provider-mediated.

---

### F4 — Terms incorporate DPA when GDPR applies

DataForSEO Terms state that the Terms incorporate the DataForSEO DPA when GDPR applies to use of the Services and processing of Service Data.

Implication for Observatory:

- If Observatory handles any personal data through DataForSEO services, DPA obligations matter.
- M4 boundary law already blocks customer first-party analytics storage and customer records; RG1 does not change that.

---

### F5 — DPA places responsibility on client-side compliance and data-minimization instructions

The DPA says the client is responsible for complying with GDPR and other applicable requirements, including data minimization, purpose limitation, and storage limitation for instructions issued to DataForSEO.

Implication for Observatory:

- Observatory must not assume provider legality equals project legality.
- Capture recipes must encode purpose, scope, storage/retention class, and deletion expectations before provider admission.
- Rights and retention still fail closed.

---

### F6 — DataForSEO says API task data is stored for 365 days and stored data older than 365 days is deleted

The Privacy Policy says DataForSEO stores API task data for 365 days. It also states that all data stored for more than 365 days will be permanently deleted from its system.

Implication for Observatory:

- DataForSEO's own retention period is not the same as Observatory's right to store raw outputs long term.
- If Observatory wants durable raw payload archives, RG1 does not fully clear that question from the parsed official sources alone.
- Treat long-term raw retention as unresolved until a provider-admission doc explicitly ties terms, rights class, and owner approval together.

---

### F7 — Data export is available by request

The Privacy Policy says data tracked/stored in DataForSEO can be exported to CSV or JSON by request to support, with export guaranteed within five business days after request receipt.

Implication for Observatory:

- Export availability supports auditability but does not replace raw capture at time of pull.
- Observatory should still preserve raw response payloads or raw pointers at capture time if a later provider-admission ruling allows it.

---

### F8 — SERP data has explicit usage restrictions

DataForSEO Terms say SERP data or content obtained through the Service, including from Google, Bing, Yahoo, and other search engine providers, must not be used to compete with or adversely affect those providers' business interests.

Implication for Observatory:

- Observatory must not position itself as a search-engine substitute, broad republisher, or competing SERP database.
- Narrow internal evidence, customer-scoped public observation, and report-support use may still be plausible, but require provider-admission language and stop conditions.
- Any raw SERP archive posture must preserve rights and permitted-use limits.

---

### F9 — Repeated identical tasks are a user-side error and may not be refunded

DataForSEO Terms say identical API tasks are considered a user-side error, and refunds will not be issued for tasks affected by user-side errors because they consume resources and affect system performance.

Implication for Observatory:

- Capture runner design must include duplicate-task prevention before any paid pull.
- M8 hammers should include duplicate-capture and repeated-task rejection.
- Manual validation plans must use tiny task counts and exact stop conditions.

---

## Current RG1 disposition

RG1 partially clears DataForSEO for continued planning, but not for provider admission or paid pulls.

Cleared for later planning:

- DataForSEO remains a plausible first provider candidate.
- The official pricing posture is compatible with a small controlled validation plan later.
- SERP API and AI Optimization API remain relevant endpoint families to evaluate later.
- Cost-control tools and minimum payment are now known planning constraints.

Not cleared:

- No provider purchase.
- No paid pull.
- No bulk capture.
- No recurring capture.
- No provider admission.
- No long-term raw payload retention approval.
- No customer first-party analytics storage.

---

## Recommended later validation posture

A later M13 provider-admission plan should require:

1. owner approval before account funding or use of credits;
2. exact endpoint family list;
3. exact task count ceiling;
4. maximum dollar ceiling;
5. no duplicate tasks;
6. raw payload capture plan;
7. hash/manifest plan;
8. retention class;
9. allowed-use summary;
10. stop conditions;
11. post-pull review before any second pull.

Suggested first validation scope, not yet approved:

- one tiny SERP API validation sample; and/or
- one tiny AI Optimization validation sample only if RG6 requires it;
- no marketplace, backlink, Labs, or broad multi-family pull until later gates justify it.

---

## Owner-ruling candidates

Owner ruling is required before:

- funding or using a DataForSEO account;
- authorizing the reserved validation budget;
- preserving raw API payloads long term;
- using AI Optimization endpoint families for validation;
- adding DataForSEO as an admitted provider;
- designing a capture recipe that spends money.

---

## Blockers carried forward

- Need explicit provider-admission decision before any paid pull.
- Need M7 contract language for provider testimony, rights/retention, raw payload pointers, and provider score treatment.
- Need M8 hammers for duplicate task rejection, cost ceiling enforcement, rights fail-closed behavior, and no strategy/recommendation storage.
- Need M13 controlled pull plan before spending.

---

## Feeds later milestones

- M7 provider testimony / rights / retention / raw payload contracts
- M8 hammer matrix
- M9 first evidence slice selection
- M13 provider admission and controlled pull plan

---

## Final RG1 rule

```text
DataForSEO remains plausible.
DataForSEO is not admitted.
The $50 minimum is planning evidence, not spend approval.
```
