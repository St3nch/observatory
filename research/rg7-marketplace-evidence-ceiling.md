# RG7 — Marketplace Evidence Ceiling

Status: research output
Authority: source-grounded research input; not doctrine by itself; not schema approval
Milestone: M6 — Research Gate Execution
Date: 2026-07-07

---

## Gate question

What marketplace public evidence can Observatory safely observe for Etsy/Fiverr/etc. without storing customer-private data or violating platform ceilings?

---

## Sources checked

Local/current sources checked during RG7:

- `01-harvest-register.md`
- `02-boundaries.md`
- `research/m5-research-gate-plan.md`
- `planning-inbox/repo-first-research-triage.md`
- `research/rg2-scope-rights-retention-model.md`
- `research/rg3-evidence-id-citation-model.md`
- `research/rg4-query-panel-model.md`
- `research/rg5-freshness-staleness-volatility.md`

Current external sources checked during RG7:

- Etsy Terms of Use — `https://www.etsy.com/legal/terms-of-use`
- Etsy API Terms of Use — `https://www.etsy.com/legal/api`
- Fiverr Terms of Service — `https://www.fiverr.com/legal-portal/legal-terms/terms-of-service`
- General legal/scraping context checked only to frame uncertainty, not to override marketplace terms.

External-source use is narrow: these sources support marketplace ceiling classification, not implementation or capture admission.

---

## Current source-grounded findings

### F1 — Marketplace evidence is owned-but-deferred, not automatically admitted

The harvest register records marketplace gig/listing-page snapshots as an owned-but-deferred family.

It also records that a browser-extension idea is only a candidate capture instrument requiring admission, provider-registry-style review, and per-marketplace ToS review.

Implication:

- Marketplace evidence is important, but not active.
- Marketplace capture must not proceed from vibes.
- RG7 cannot admit scraping, browser automation, extension capture, or marketplace panels.

---

### F2 — Etsy explicitly blocks crawling/scraping in general Terms

Etsy Terms of Use say users agree not to crawl, scrape, or spider any page of Etsy Services or reverse engineer/attempt to obtain source code without express permission, and direct API users to Etsy API Terms.

Implication:

- Etsy page scraping is blocked unless Etsy expressly authorizes it.
- Browser-extension capture against Etsy pages is not safe by default.
- Manual visual observation may still be a human workflow question, but not an automated Observatory capture family.

---

### F3 — Etsy API terms explicitly restrict automated systems, browser extensions, scraping, analytics, ML/training, and overcollection

Etsy API Terms say API users must request only the minimum amount of data needed. They also prohibit automated systems or browser extensions to access, analyze, or scrape the Etsy Site, Etsy API, or Etsy data, including listings, shops, or user profiles, unless expressly authorized in writing. The API Terms also prohibit using the API to collect/scan/request Etsy content for analytics, machine learning, AI training, licensing, or content removal unless expressly authorized in writing.

Implication:

- Etsy is not merely `be polite with rate limits.`
- Etsy is `do not automate/scrape/analyze Etsy data unless expressly authorized.`
- Etsy API use for SearchClarity-style analytics is not automatically permitted by having an API key.
- Any Etsy capture path requires explicit purpose review, minimum-data design, authorization posture, and likely owner ruling.

---

### F4 — Etsy API content has short freshness/display expectations

Etsy API Terms say listing content displayed through the API must not be more than six hours older than corresponding Etsy Site/App information, and other Etsy content must not be more than twenty-four hours older than site/app content. They also say API-accessed content should not be cached or stored longer than reasonably necessary to provide service to application users.

Implication:

- Durable Observatory retention of Etsy API content is not cleared.
- Etsy marketplace evidence may require `capture_and_purge`, `no_storage_overlay_only`, or another tightly scoped retention class unless explicit authorization permits durable storage.
- Etsy public listing evidence for reports may need fresh/manual/customer-side handling rather than Observatory long-term storage.

---

### F5 — Fiverr official terms fetch did not expose a clear automation/scraping clause in parsed content

The current official Fiverr Terms of Service page was checked. The parsed content did not expose a clear crawl/scrape/automated-access clause in the accessible text retrieved during RG7.

The same page does expose marketplace categories including Data Scraping as a service category, but a service category is not authorization to scrape Fiverr itself.

Implication:

- Fiverr cannot be classified as allowed.
- Fiverr should be classified as `not-cleared / provider_clarification_required` for automated capture.
- Public manual review may be less obviously blocked than Etsy from this fetch alone, but RG7 does not admit capture.

---

### F6 — Public marketplace data can still carry rights, privacy, and platform constraints

RG2 says rights and retention fail closed. RG5 says marketplace observations are high-volatility. RG4 says marketplace query panels are measurement programs, not strategy.

Implication:

- Public visibility does not equal storage permission.
- Public marketplace observations need source-specific rights, retention, freshness, and capture-method controls.
- Seller dashboards, private stats, order histories, messages, conversion data, and customer-supplied screenshots remain outside Observatory unless future owner ruling changes law.

---

## Marketplace ceiling classifications

This section proposes contract-planning classifications. It is not provider/capture admission.

| Marketplace/source | Public observation posture | Automated capture posture | Storage posture | RG7 classification |
|---|---|---|---|---|
| Etsy Site pages | Human-visible public pages exist, but Terms block crawl/scrape/spider without express permission | Blocked by default | Durable storage not cleared | `forbidden_by_default / owner_ruling_required` |
| Etsy API | API exists, but purpose, minimum-data, API terms, rate limits, and restrictions apply | Not admitted; analytics/automation uses need express authorization posture | Short freshness/cache limits; durable retention not cleared | `defer / provider_clarification_required` |
| Etsy seller dashboard / Etsy Stats | Customer-private first-party data | Not admitted | Out of Observatory | `no_storage_overlay_only` |
| Fiverr public gig/search pages | Public pages exist; current parsed official terms did not establish clear automation permission | Not admitted | Not cleared | `not_cleared / provider_clarification_required` |
| Fiverr seller dashboard/order/message data | Customer-private / account-private data | Not admitted | Out of Observatory | `no_storage_overlay_only` |
| Generic marketplace public pages | Depends on platform terms and capture method | Not admitted | Fail closed until per-platform review | `defer` |
| Customer-provided manual notes about public marketplace observations | Possible consumer-owned input | Not Observatory evidence by default | Consumer-side unless admitted as manual-capture family | `consumer_owned / owner_ruling_required` |

---

## Proposed evidence ceiling vocabulary

### `allowed_public_observation_candidate`

Meaning:
Potentially observable public marketplace evidence, pending platform/capture review.

Example:
Public listing title, price display, search result position, public seller profile snippet.

Caution:
Candidate does not mean admitted.

---

### `api_possible_not_admitted`

Meaning:
A platform API exists or may exist, but use is not admitted until purpose, rights, retention, rate limits, and terms are resolved.

Example:
Etsy API listing/search endpoints, if they fit an approved purpose and terms.

---

### `forbidden_by_default`

Meaning:
Terms or boundary law block capture/storage unless express authorization or owner ruling changes posture.

Example:
Etsy site scraping/crawling/spidering; browser-extension scraping of Etsy data.

---

### `overlay_only_private`

Meaning:
Private/customer first-party marketplace data may be supplied to read tools at read time but is not stored by Observatory.

Example:
Etsy Stats, seller dashboard exports, customer screenshots, private conversion data.

---

### `provider_clarification_required`

Meaning:
Current source review did not establish clear permission for intended use.

Example:
Fiverr public gig/search capture, pending deeper official terms/API/permission review.

---

### `consumer_owned_manual_note`

Meaning:
A human may make notes during a customer workflow, but those notes belong to SearchClarity/consumer layer unless an admitted manual-capture contract exists.

Example:
Consultant notes that a listing appeared visually in a search result during a manual review.

---

## Proposed marketplace observation fields later

If a marketplace public-observation family is ever admitted, it should preserve:

```text
observation_id
evidence_id
scope_id
scope_class
marketplace
surface_family
capture_method
provider_or_capture_instrument
query_panel_id
query_panel_version_id
panel_run_id
query_text or marketplace_search_context
public_listing_url or stable locator if allowed
public_shop_or_seller_locator if allowed
observed_public_title if allowed
observed_public_position if applicable
observed_public_price_display if allowed
observed_at
rights_class
retention_class
freshness_status
volatility_class
raw_payload_id or screenshot/hash pointer if permitted
```

Potentially forbidden or high-risk fields:

```text
seller dashboard metrics
conversion data
buyer/order data
private messages
private shop analytics
customer account identifiers
login/session data
unauthorized screenshots
scraped image/content archives without rights
```

---

## Platform-specific posture

### Etsy

RG7 posture:

```text
Etsy automated page capture: forbidden by default.
Etsy browser-extension capture: forbidden by default unless express written authorization.
Etsy API: possible but not admitted; analytics/collection use needs terms review and likely authorization.
Etsy private seller data: out of Observatory; overlay-only if used at read time.
```

Recommended next handling:

- Keep Etsy production capture deferred.
- Prefer no Etsy automation until explicit authorization or a narrow API-compliant purpose is approved.
- Treat customer-provided Etsy Stats as consumer-side overlay only.
- Any Etsy evidence for SearchClarity proof should be manual/report-side unless a later owner-approved path exists.

---

### Fiverr

RG7 posture:

```text
Fiverr automated capture: not cleared.
Fiverr public manual review: possible consumer workflow candidate, not Observatory evidence by default.
Fiverr private seller/order/message data: out of Observatory.
Fiverr API/provider path: unresolved; provider clarification required.
```

Recommended next handling:

- Do not admit Fiverr capture yet.
- Perform deeper official-source review before any capture design.
- If Fiverr remains the SearchClarity launch surface, start with manual human review notes in SearchClarity, not Observatory automated capture.

---

## Relationship to RG4 query panels

Marketplace query panels can be planned, but not executed, until platform/capture admission clears.

A marketplace panel should include:

```text
marketplace
query_text
locale/language if applicable
surface type
manual/API/provider capture candidate
rights_class
retention_class
freshness/volatility posture
```

A marketplace panel must not include:

```text
private customer metrics
seller dashboard data
strategy recommendation
content/listing optimization plan
accepted conclusion
```

---

## Relationship to RG5 freshness / volatility

Marketplace search/listing observations should default to high volatility unless later evidence proves otherwise.

Read tools should use language like:

```text
Observed on [date/time] on [marketplace/surface] using [capture context]. Marketplace results may differ by location, personalization, account state, time, and platform ranking changes.
```

Strong current marketplace claims should require recent evidence or recapture.

---

## Relationship to RG8 claim safety

RG7 pushes several claim-safety rules into RG8:

Allowed:

```text
This listing was observed at position X in the sampled marketplace search on [date/time/context].
```

Forbidden:

```text
This listing ranks X on Etsy.
```

```text
This seller gets more traffic than you.
```

```text
This optimization will improve marketplace rank.
```

---

## No-nonsense checks

Before any marketplace evidence supports a claim, the evidence pack should answer:

1. Which marketplace was observed?
2. Which surface was observed: public search, listing page, shop page, dashboard, API, or external provider?
3. Is the surface public or private/customer-first-party?
4. What capture method was used?
5. Does the platform permit the capture method?
6. What rights_class applies?
7. What retention_class applies?
8. Is raw/screenshot retention allowed?
9. Is the observation fresh enough for the claim?
10. Could this evidence leak customer workflow state?
11. Is this evidence being turned into strategy inside Observatory?
12. Does the output overclaim marketplace rank or traffic?

If these cannot be answered, the evidence is blocked or overlay-only.

---

## Non-goals

RG7 does not authorize:

- schema design;
- migrations;
- Etsy scraping;
- Etsy API use;
- browser-extension capture;
- Fiverr capture;
- paid provider pulls;
- recurring marketplace scans;
- dashboard work;
- customer private data handling;
- strategy/recommendation storage;
- marketplace rank guarantees.

---

## Owner-ruling candidates

Owner ruling or later contract decision is required before:

- admitting any Etsy API use;
- seeking Etsy express written authorization for analytics/capture use;
- admitting any browser-extension capture instrument;
- admitting Fiverr public capture;
- using manual marketplace observations as Observatory evidence;
- retaining marketplace screenshots or raw page payloads;
- treating marketplace evidence as report-safe;
- executing marketplace query panels.

---

## Blockers carried forward

- M7 must turn marketplace ceiling classifications into contract language.
- M8 must hammer public/private surface separation, rights fail-closed, retention fail-closed, no dashboard/private data storage, and no strategy storage.
- M13 must decide if any marketplace provider/capture instrument is admitted.
- M15 must decide what SearchClarity can safely use in reports.

---

## Feeds later milestones

- M7 marketplace evidence ceiling contract
- M8 marketplace/private-data hammers
- M10 schema planning
- M13 provider/capture admission
- M15 SearchClarity proof workflow

---

## Final RG7 rule

```text
Public marketplace pages are not automatically Observatory evidence.
Platform permission, capture method, rights, retention, and customer-data boundaries decide.
Etsy automation is blocked by default.
Fiverr automation is not cleared.
Customer marketplace dashboards stay outside Observatory.
```
