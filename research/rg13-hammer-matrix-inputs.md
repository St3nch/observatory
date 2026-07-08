# RG13 — Hammer Matrix Inputs

Status: research output
Authority: source-grounded research input; not doctrine by itself; not test implementation
Milestone: M6 — Research Gate Execution
Date: 2026-07-07

---

## Gate question

What hostile-path hammer categories must M8 prove before Observatory implementation, provider capture, read tools, or consumer integration can be trusted?

---

## Sources checked

Local/current sources checked during RG13:

- `02-boundaries.md`
- `01-harvest-register.md`
- `research/m5-research-gate-plan.md`
- `research/rg1-dataforseo-rights-retention-cost.md`
- `research/rg2-scope-rights-retention-model.md`
- `research/rg3-evidence-id-citation-model.md`
- `research/rg4-query-panel-model.md`
- `research/rg5-freshness-staleness-volatility.md`
- `research/rg6-geo-ai-citation-methodology.md`
- `research/rg7-marketplace-evidence-ceiling.md`
- `research/rg8-claim-safety-report-language.md`
- `research/rg9-provider-cross-check-disagreement-model.md`
- `research/rg10-capturepackage-v0-1-inputs.md`
- `research/rg11-raw-archive-provider-drift.md`
- `research/rg12-consumer-contract-inputs.md`
- `research/deep-research-backlog.md`

No current external source was required for RG13 because this gate synthesizes hammer inputs from already completed M6 research. Actual hammer implementation belongs to M8 or later implementation milestones.

---

## Current source-grounded findings

### F1 — Hammer tests are a hard gate

Boundary law says hammer tests are required for implementation and should include persistence, contract, append-only behavior, scope isolation, provenance enforcement, rights fail-closed behavior, retention enforcement, provider disagreement preservation, no strategy/recommendation storage, no direct SQL/credential exposure, and hostile-path rejection.

Implication:

- M8 cannot be a normal happy-path unit-test pass.
- It must include hostile paths that try to break Observatory boundaries.
- If a boundary is claimed, it must be proven under real execution.

---

### F2 — Fail-closed behavior must be proven, not assumed

RG2, RG10, RG11, and RG12 repeatedly require fail-closed behavior for unclear rights, retention, source family, scope, raw payload retention, overlay storage, and consumer requests.

Implication:

- Missing fields must block admission.
- Unknown rights must block capture/storage.
- Ambiguous source/capture rules must quarantine or reject.
- Hammers must prove rejection, not just validate good payloads.

---

### F3 — No strategy storage is a primary hostile-path category

Boundary law, RG8, and RG12 all say recommendations, conclusions, accepted decisions, workflow records, and customer report records live outside Observatory.

Implication:

- Hammers must attempt to sneak recommendations into multiple fields.
- Hammers must reject renamed strategy tables/fields.
- Hammers must prove temporary candidate caches do not become durable strategy storage.

---

### F4 — Provider and raw payload hammers need special attention

RG1, RG9, RG10, and RG11 require no spend without approval, no duplicate paid tasks, provider attribution, no provider winner logic, raw hash/pointer integrity, drift quarantine, and parser-safe behavior.

Implication:

- Provider/capture hammers must simulate cost abuse, duplicate capture, malformed payloads, provider drift, stale timestamps, and disagreement averaging attempts.
- Raw archive hammers must prove raw data cannot bypass rights/retention.

---

### F5 — Consumer integration must prove evidence-only boundaries

RG12 says consumers may ask for governed evidence packs but may not use Observatory as customer database, workflow store, strategy store, or report system.

Implication:

- Consumer hammers must reject customer-private payloads.
- Overlay hammers must prove no persistence.
- Read-tool hammers must prove caveats and promotion warnings are returned.

---

## Hammer matrix input categories

### H1 — Scope isolation hammers

Risk:
Customer, project, workspace, or market-watch data leaks across scopes or uses consumer IDs as Observatory identity.

Must test:

- missing `scope_id` rejected;
- unknown `scope_class` rejected;
- customer email/name/order ID rejected as scope identity;
- consumer foreign key cannot become Observatory primary identity;
- cross-scope read blocked unless explicitly allowed;
- cross-scope aggregate read rejected by default.

Proof needed:

- hostile fixtures;
- rejection result;
- no persistence after rejection;
- audit/error record if contract later requires it.

Feeds:

- M7 scope contract;
- M8 core hammers;
- M14 read tools.

---

### H2 — Rights fail-closed hammers

Risk:
Unclear rights are treated as permission.

Must test:

- missing `rights_class` rejected;
- `provider_clarification_required` blocks capture/admission;
- `legal_review_required` blocks capture/admission;
- `not_expressly_granted` cannot durable-store by default;
- source-specific restrictions override generic class;
- marketplace capture with unclear platform rights rejected.

Proof needed:

- rejected capture package;
- no raw payload retained unless explicit capture-and-purge path exists;
- claim-use warning or hard error returned.

Feeds:

- M7 rights contract;
- M8 fail-closed hammers;
- M13 provider/capture admission.

---

### H3 — Retention enforcement hammers

Risk:
Data survives longer than allowed or gets durable evidence status when it should be purged/overlay-only.

Must test:

- missing `retention_class` rejected;
- `no_storage_overlay_only` cannot persist payload;
- `capture_and_purge` requires purge deadline;
- expired retention blocks current use;
- payload purge updates raw support status;
- manifest-only retention does not retain forbidden payload.

Proof needed:

- before/after persistence check;
- purge proof or manifest status;
- read tool reports unavailable raw support correctly.

Feeds:

- M7 retention contract;
- M8 persistence hammers;
- M11 raw archive planning.

---

### H4 — Customer-private data rejection hammers

Risk:
Customer first-party data or workflow records enter Observatory.

Must test rejection for:

```text
customer records
customer identity
customer order/report IDs as business records
GSC exports
GA4 exports
Etsy Stats
Shopify analytics
seller dashboard screenshots
private conversion data
customer report conclusions
report delivery state
```

Proof needed:

- rejected request/capture;
- no persisted payload;
- overlay-only path discards input;
- consumer-promotion warning returned where applicable.

Feeds:

- M7 consumer contract;
- M8 consumer hammers;
- M15 SearchClarity proof.

---

### H5 — No strategy / recommendation storage hammers

Risk:
Strategy storage sneaks in under renamed fields.

Must test rejection for fields or payloads containing:

```text
recommendation
strategy
opportunity score as truth
action plan
accepted conclusion
experiment plan
agent task decision
report conclusion
best keyword to target
rewrite title to X
```

Must also test:

- strategy content hidden in `notes`;
- strategy content hidden in `operator_intent`;
- strategy content hidden in raw payload metadata;
- temporary candidate cache attempt.

Proof needed:

- durable storage blocked;
- error identifies boundary violation;
- downstream promotion path indicated if appropriate.

Feeds:

- M7 claim/consumer contracts;
- M8 anti-veda hammers;
- M14 read tools.

---

### H6 — CapturePackage validation hammers

Risk:
CapturePackage becomes a payload dump or implementation loophole.

Must test rejection for missing:

```text
scope_id
scope_class
source_family
provider_or_capture_instrument
capture_method
operator_intent
captured_at
rights_class
retention_class
approval_reference when paid
cost ceiling when paid
raw hash when raw retained
```

Must test:

- bad source family;
- mismatched capture method;
- hidden strategy intent;
- unknown panel version;
- candidate observations admitted before validation.

Proof needed:

- package status `blocked` or equivalent;
- no observations/evidence IDs admitted;
- no raw retention unless allowed.

Feeds:

- M7 CapturePackage contract;
- M8 package hammers;
- M13 capture admission.

---

### H7 — Provider spend and duplicate task hammers

Risk:
Provider tools spend money or repeat tasks without human approval.

Must test:

- paid capture without approval rejected;
- missing dollar ceiling rejected;
- missing task/call ceiling rejected;
- duplicate task rejected before spend;
- stop condition prevents further tasks;
- provider endpoint not in approved list rejected;
- budget exhaustion blocks capture.

Proof needed:

- no provider call made in rejected cases;
- no cost incurred in rejected cases;
- duplicate fingerprint check recorded;
- explicit owner approval required in accepted path.

Feeds:

- M7 provider/capture contract;
- M8 cost hammers;
- M13 provider admission.

---

### H8 — Provider attribution and disagreement hammers

Risk:
Provider metrics become truth, or disagreement gets averaged into fake truth.

Must test:

- provider score cannot be stored/displayed without provider attribution;
- difficulty/authority/confidence metric cannot be relabeled as fact;
- two provider values cannot auto-average into truth;
- provider winner logic rejected;
- incomparable metrics produce `unresolved_incomparability` or warning;
- provider disagreement preserved in read output.

Proof needed:

- read output retains provider identity;
- claim-use warning present;
- no blended truth field created;
- no recommendation generated.

Feeds:

- M7 Provider Cross-Check contract;
- M8 provider hammers;
- M16 cross-check proof.

---

### H9 — Freshness / volatility / claim-use hammers

Risk:
Stale or volatile evidence supports overstrong current claims.

Must test:

- unknown captured_at fails current claim;
- stale evidence returns historical-only or recapture-required warning;
- high-volatility AI/marketplace evidence requires caveat;
- update-window evidence requires warning;
- current-state claim blocked when freshness insufficient;
- absence claim requires sampled-absence warning.

Proof needed:

- read output includes freshness_status;
- volatility_class shown;
- recapture_recommendation shown;
- claim blocked/downgraded as appropriate.

Feeds:

- M7 freshness/claim contract;
- M8 claim hammers;
- M14 read tools.

---

### H10 — AI / GEO overclaim hammers

Risk:
AI answer-surface evidence becomes universal AI visibility or trust/influence claims.

Must test forbidden outputs:

```text
you rank X in AI
you are absent from AI search
AI trusts this source
citation caused the answer
guaranteed AI citations
AI visibility score as truth
```

Must test allowed outputs:

- sampled mention observation;
- sampled citation observation;
- absence observed in sample;
- citation not equal influence warning.

Proof needed:

- forbidden claim rejected;
- safe wording returned;
- sample size/surface/prompt/date shown.

Feeds:

- M7 AI observation contract;
- M8 AI hammers;
- M15 GEO proof.

---

### H11 — Marketplace evidence hammers

Risk:
Marketplace public pages or private seller data are captured/stored without platform clearance.

Must test:

- Etsy browser-extension capture rejected by default;
- Etsy scraping/crawling capture rejected by default;
- Fiverr automated capture rejected/not-cleared;
- seller dashboard screenshots rejected or overlay-only;
- marketplace rank claim requires point-in-time caveat;
- marketplace traffic/sales inference rejected.

Proof needed:

- capture blocked when platform posture requires it;
- no raw page payload retained;
- claim-use warning returned for allowed point-in-time manual/public observation candidate.

Feeds:

- M7 marketplace contract;
- M8 marketplace hammers;
- M15 SearchClarity proof.

---

### H12 — Raw archive integrity hammers

Risk:
Raw payload storage bypasses contracts or corrupts evidence.

Must test:

- raw retained without rights rejected;
- raw payload without SHA-256 rejected;
- hash mismatch blocks parse/admission;
- missing pointer blocks raw-supported evidence;
- retained payload past retention blocked/purged;
- raw payload includes forbidden private data and is rejected.

Proof needed:

- hash verification result;
- blocked parser/admission result;
- purge or no-storage proof;
- manifest status if payload unavailable.

Feeds:

- M7 raw archive contract;
- M8 raw hammers;
- M11/M13 provider proof.

---

### H13 — Provider drift / parser safety hammers

Risk:
Provider payload shape changes silently corrupt observations.

Must test:

- new shape quarantined;
- breaking shape blocks admission;
- provider error payload not parsed as normal observation;
- missing required field does not become fake value;
- field type change blocks or warns;
- parser version recorded;
- drift status surfaced to read tools.

Proof needed:

- drift_status assigned;
- no admitted observation on breaking/unknown shape;
- parser warnings retained;
- evidence IDs not minted from unsafe parse.

Feeds:

- M7 drift contract;
- M8 parser hammers;
- M13 provider admission.

---

### H14 — Query panel immutability and run hammers

Risk:
Panel versions mutate after use or captures attach to wrong panel context.

Must test:

- used panel version cannot be edited in place;
- new query/item requires new panel version;
- run cannot attach to missing panel version;
- stale evidence does not mutate panel version;
- result changes do not create hidden panel mutation;
- panel cannot include recommendation fields.

Proof needed:

- immutable version enforcement;
- rejected mutation;
- clean new-version path;
- no recommendation fields stored.

Feeds:

- M7 query panel contract;
- M8 panel hammers;
- M14 read tools.

---

### H15 — Evidence ID / citation integrity hammers

Risk:
Evidence IDs, raw payload IDs, provider IDs, and report-safe references get confused.

Must test:

- provider job ID cannot be used as evidence ID;
- raw_payload_id cannot be used as report-safe reference;
- evidence ID remains stable across read calls;
- withdrawn/superseded/expired evidence status is respected;
- customer identity not encoded in citation handle;
- report-safe references do not expose private identifiers.

Proof needed:

- ID layer validation;
- stable lookup;
- status-aware read output;
- privacy-safe handle format.

Feeds:

- M7 evidence contract;
- M8 evidence hammers;
- M14 read API;
- M15 reports.

---

### H16 — Consumer request / overlay hammers

Risk:
Consumers use Observatory as customer database, report system, workflow store, or overlay persistence layer.

Must test:

- customer order/report record rejected;
- report conclusion rejected;
- workflow task rejected;
- overlay accepted only as ephemeral input if contract allows;
- overlay not persisted;
- consumer request with private context rejected;
- response includes consumer_promotion_required.

Proof needed:

- no persisted overlay rows;
- rejection evidence;
- shaped evidence pack only;
- promotion warning returned.

Feeds:

- M7 consumer contract;
- M8 consumer hammers;
- M14/M15 integration.

---

### H17 — LLM / agent access hammers

Risk:
LLMs or agents get direct DB powers, credentials, or arbitrary mutation tools.

Must test:

- no direct PostgreSQL credentials exposed;
- no arbitrary SQL tool exposed;
- no table CRUD tool exposed;
- no schema mutation tool exposed;
- no direct observation write tool exposed;
- provider spend tool requires human approval;
- read tools return shaped evidence packs only.

Proof needed:

- tool registry inspection;
- denied direct SQL/credential request;
- typed tool boundary only;
- no mutation without approved path.

Feeds:

- M7 access contract;
- M8 access hammers;
- M14 MCP/API contract.

---

### H18 — Hostile path / weird input hammers

Risk:
Paths, payloads, and text fields bypass validation through odd formatting or injection-like content.

Must test:

- path traversal rejected;
- absolute file paths rejected where not allowed;
- huge payload rejected or bounded;
- malformed JSON rejected;
- unexpected encoding rejected;
- control characters handled safely;
- duplicate IDs rejected;
- hidden recommendation text in nested object rejected.

Proof needed:

- deterministic rejection;
- no partial writes;
- no raw/private leak;
- bounded error output.

Feeds:

- M8 hostile hammers;
- M10 schema/API planning;
- M14 read tools.

---

## Minimum M8 hammer suite proposal

M8 should not try to test everything forever. It should build a first hammer matrix covering at minimum:

```text
scope isolation
rights fail-closed
retention fail-closed
customer-private rejection
no strategy/recommendation storage
CapturePackage required fields
provider spend/no duplicate tasks
provider attribution/no averaging
freshness/claim-use warnings
AI/GEO overclaim rejection
marketplace blocked-by-default cases
raw hash/pointer integrity
provider drift quarantine
consumer overlay no-storage
LLM/agent access boundary
```

This minimum suite should run against real implementation surfaces once implementation exists. Mock-only proof is insufficient for acceptance.

---

## Test result vocabulary candidates

```text
pass
fail
blocked_not_implemented
blocked_contract_missing
blocked_owner_ruling_required
blocked_provider_not_admitted
blocked_manual_review_required
```

Rules:

- `blocked_not_implemented` is not pass.
- `blocked_contract_missing` is not pass.
- Hammers can be planned before implementation, but they do not close until executed.

---

## Non-goals

RG13 does not authorize:

- test implementation;
- schema design;
- migrations;
- API/MCP implementation;
- provider admission;
- paid provider pulls;
- raw archive implementation;
- customer data handling;
- production capture.

---

## Owner-ruling candidates

Owner ruling or later contract decision is required before:

- finalizing M8 hammer acceptance criteria;
- choosing which hammers are hard gates for each milestone;
- deciding what mock/stub level is acceptable for early pre-implementation hammers;
- activating provider/capture hammers against real provider data;
- activating customer-adjacent consumer hammers.

---

## Deeper research carried forward

DR15 remains active for hostile-path expansion.

Other backlog items feed specific hammer sets:

- DR1/DR2/DR13 feed provider/raw hammers;
- DR4/DR5 feed AI/GEO hammers;
- DR6/DR7/DR8 feed marketplace/manual capture hammers;
- DR9/DR10/DR14 feed consumer/report/evidence hammers.

RG13 answers enough for M7/M8 planning, not enough to claim implementation proof.

---

## Blockers carried forward

- M7 must convert research outputs into enforceable contracts before many hammers can be executable.
- M8 must create the actual hammer matrix and acceptance rules.
- M10/M13/M14 implementation milestones must run hammers against real surfaces before acceptance.

---

## Feeds later milestones

- M7 contract planning
- M8 hammer matrix
- M10 schema planning
- M13 provider/capture admission
- M14 typed API / MCP contract
- M15 SearchClarity proof workflow
- M16 Provider Cross-Check proof
- M17 overlay/internal telemetry proof

---

## Final RG13 rule

```text
If Observatory claims a boundary, M8 must try to break it.
Happy-path tests do not prove Observatory safe.
The hammer matrix exists to prove the database stays a telescope, not an astronomer with a fake mustache.
```
