# Claude Deep Audit Directive — Post-M13 / Pre-M14 Observatory Review

You are performing a fresh, repo-first deep audit of **The Observatory**.

This is not a project reset.

Do not rely on a prior summary, memory, or a narrow milestone view. Clone the live repository and derive current project truth from the repo itself.

Repository:

```text
https://github.com/St3nch/observatory.git
```

Expected local clone root:

```text
C:\dev\observatory
```

Use your strongest available reasoning model for the audit. The owner wants a serious second set of eyes from a capable independent LLM, not a shallow document summary.

---

## 1. Why This Audit Is Happening

The last broad Claude audit was around the M7 era. Since then, The Observatory has completed substantial work through M13, including:

```text
M8  Hammer Matrix and Acceptance Gates
M9  First Evidence Slice Definition
M10 Schema Planning Only
M11 Implementation Foundation
M12 First Evidence Slice Build
M13 Provider Admission and Controlled Pull Plan
```

M13 has now closed. M14 planning is active.

The audit must review everything completed since the earlier M7-era review and also re-evaluate the full project as it exists now, because later work may expose weaknesses in earlier assumptions.

---

## 2. What The Observatory Is

The Observatory is an evidence-only SEO / GEO / SERP / marketplace / video visibility observation system.

Core doctrine:

```text
The Observatory stores what was observed.
The connected LLM interprets what it means at read time.
Accepted conclusions promote out to the owning consumer.
```

Mental model:

```text
The Observatory is the telescope.
The connected LLM is the astronomer.
The database must never become the astronomer.
```

The Observatory is not:

```text
a strategy engine
a recommendation engine
a customer CRM
a customer-report database
a generic SEO dashboard
a scraper farm
a provider-spend machine
a Kaizen replacement
a Neon Ronin subsystem
a SearchClarity customer database
a place to store conclusions as facts
```

Customer and private analytics do not belong in The Observatory under current doctrine.

Provider output is testimony, not truth.

Provider disagreement is first-class evidence.

Rights, retention, scope, provenance, freshness, and claim safety must fail closed.

LLMs and agents must not receive direct SQL access or database credentials. Future access is through typed, bounded read tools only.

---

## 3. What “Dangerous” Means Here

The owner wants The Observatory to become a **dangerously capable** system in the positive sense:

```text
unusually powerful
hard to fool
rich in evidence most competitors do not collect or preserve well
excellent at combining SERP, SEO, GEO, marketplace, video, public-page, and provider evidence
able to support profitable future products and services
useful to strong LLM reasoning at read time
hardened against bad data, false confidence, provider drift, rights mistakes, accidental spend, and architectural shortcuts
```

Do not interpret “dangerous” as harmful, illegal, deceptive, exploitative, or abusive.

Do interpret it as a request to think aggressively about how to make the system more capable, differentiated, defensible, evidence-rich, and commercially useful while remaining lawful, governed, and honest.

The future business value may include supporting SearchClarity, Neon Ronin workspaces, internal research, marketplace visibility products, GEO/AI citation analysis, competitive intelligence, and future services that make money from superior evidence and interpretation.

The Observatory itself must still remain the telescope rather than the strategy engine.

---

## 4. Current Milestone Boundary

M13 is closed.

M14 is active for planning only:

```text
M14 — Typed Read API / MCP Contract and Prototype
```

M14 may plan typed read contracts, authorization, redaction, bounded filtering, evidence handles, LLM-context assembly, MCP/tool semantics, and hostile-path acceptance tests.

M14 does not currently authorize:

```text
Postgres creation
physical schema
migrations
live provider ingestion
another paid provider request
bulk or recurring capture
customer data
direct SQL for LLMs or agents
production API deployment
production MCP deployment
public exposure
dashboards
customer-facing reports
strategy storage
recommendation storage
automatic conclusion promotion
```

Do not implement anything during this audit.

Do not create schema.

Do not make provider calls.

Do not spend money.

Do not alter repo files unless the owner separately asks you to produce a patch after the audit.

---

## 5. M13 Live-Probe Context

M13 completed one tightly controlled DataForSEO C00 probe against:

```text
/v3/serp/google/organic/live/advanced
```

The accepted probe used:

```text
keyword: observatory test page
location_code: 2840
domain/language posture: Google organic, English, United States
device: desktop
os: windows
depth: 10
```

Accepted result:

```text
HTTP 200
provider status 20000
one request
one billable task
zero retries
zero polling
cost 0.002 USD
12 SERP items
10 organic
1 people_also_ask
1 related_searches
162 normalized field paths
```

The raw response was reviewed, hashed, summarized, and purged with durable proof under a seven-day maximum retention posture.

An accidental test request using placeholder credentials produced HTTP 401. The incident was preserved. A single replacement request was separately authorized and consumed. The system did not silently erase the incident or automatically retry.

This probe is payload-shape evidence only. It is not broad DataForSEO admission, schema authority, or permission for another pull.

---

## 6. Required Repo-First Read Path

Clone the repo and verify branch, HEAD, working-tree state, and remote synchronization before auditing.

Then read enough of the repo to understand the full project. At minimum, inspect:

```text
README.md
ACTIVE_CONTEXT.md
ROADMAP.md
NEXT_SESSION_HANDOFF.md
CLAUDE_START_HERE.md
planning-inbox/README.md
planning-inbox/steward-context-dump.md
planning-inbox/observatory-working-notes.md
planning-inbox/strategy-layer-dangerous-design.md
planning-inbox/deep-research-danger-agenda.md
planning-inbox/research/research-review-summary.md
contracts/README.md
hammers/README.md if present
decisions/README.md
```

Read the accepted milestone closure decisions from M7 through M13.

Read the M7 contract set, especially:

```text
scope-rights-retention.md
provider-testimony.md
provider-cross-check.md
claim-safety.md
freshness-staleness-volatility.md
capturepackage-v0-1.md
raw-archive-provider-drift.md
evidence-id-citation.md
consumer-promotion.md
query-panel.md
searchclarity-consumer-placeholder.md
```

Read the M8 hammer matrix and acceptance-gate policy.

Read the M9–M12 planning and implementation artifacts.

Inspect the actual source and tests under:

```text
src/
tests/
```

Read the M13 decision, plan, live-execution, post-pull, purge, and closure artifacts.

Inspect the sanitized M13 evidence summaries and purge proof. Do not complain that the raw provider payload is absent; it was intentionally purged under the accepted retention posture.

Use the repository as the source of truth. When a tracker, handoff, or context file is stale, call that out explicitly rather than assuming the stale statement is current.

---

## 7. Audit Goals

Perform a hostile but constructive architecture, product, governance, evidence, and commercial-readiness audit.

The audit must identify:

### A. Doctrine and boundary integrity

- contradictions between doctrine, decisions, contracts, code, tests, and milestone claims;
- places where the database could accidentally become the astronomer;
- places where strategy, recommendation, customer data, or conclusion storage could leak inward;
- places where provider testimony could collapse into truth;
- rights, retention, provenance, freshness, or claim-safety ambiguity;
- ways typed read tools could accidentally expose raw support or unsafe identifiers.

### B. Evidence-model completeness

- missing observation concepts;
- weak provenance or capture-context handling;
- missing disagreement, uncertainty, volatility, or temporal semantics;
- missing evidence needed for SERP, SEO, GEO, AI citation, marketplace, video, page snapshot, first-party overlay, and provider-comparison use cases;
- fields or evidence classes that should remain raw-support-only;
- concepts that deserve future structured representation without designing physical schema now;
- whether current evidence IDs and citation boundaries will survive real multi-provider, multi-surface use.

### C. M8 hammer quality

- hammers that are too weak, vague, redundant, or untestable;
- missing adversarial tests;
- tests needed for races, duplicate spend, stale reads, wrong-scope reads, rights downgrade, raw leakage, prompt/tool misuse, provider drift, semantic drift, pagination abuse, filter explosion, evidence-handle guessing, customer-data contamination, and misleading LLM context;
- whether the hammer system can actually stop dangerous implementation rather than merely document concerns.

### D. M9–M12 implementation quality

- whether the C2 first slice proves the right things;
- false confidence created by fixture-only tests;
- gaps between logical contracts and code;
- implementation choices that will make M14 or later persistence harder;
- missing recovery, append-only, identity, validation, redaction, or audit semantics;
- unnecessary abstractions or premature architecture.

### E. M13 provider-control quality

- whether the DataForSEO probe actually proved the intended gates;
- weaknesses in credential handling, spend controls, duplicate prevention, incident handling, evidence packaging, raw retention, purge proof, or provider attribution;
- whether the one-time replacement mechanism created any reusable-danger or loophole;
- what should be hardened before any future distinct probe;
- what the 162-field result implies for parser, drift, and read-tool design;
- whether sanitized evidence retained enough useful structure after raw purge.

### F. M14 typed read API / MCP planning

Without implementing, specify what M14 must get right:

- typed read surfaces;
- query/filter boundaries;
- scope and authorization;
- evidence handles versus provider IDs and raw pointers;
- pagination and result ceilings;
- freshness and stale-result caveats;
- provider attribution and disagreement;
- claim-safety metadata;
- rights and retention visibility;
- redaction;
- tool descriptions and guidance metadata;
- LLM-context assembly;
- error taxonomy;
- audit events;
- rate/cost protections even for reads;
- malicious or confused-agent resistance;
- deterministic behavior;
- prototype acceptance criteria;
- what absolutely must remain deferred.

### G. Dangerous-capability opportunities

Look beyond gap-finding. Identify what could make The Observatory unusually valuable and defensible later, while respecting its doctrine.

Explore opportunities such as:

```text
multi-provider disagreement maps
SERP feature evolution and volatility evidence
AI citation / GEO surface comparison
entity and source recurrence across answer engines
public-page change and evidence lineage
marketplace visibility evidence ceilings
YouTube/video search visibility
query-panel intelligence
cross-surface mention and citation graphs
provider-model-output comparisons
historical observation replay
freshness-aware LLM context packs
claim-safe competitive intelligence
low-cost sentinel campaigns
rare SERP feature capture
rights-aware evidence reuse across consumer projects
```

Do not turn these into approved roadmap changes. Classify them by value, prerequisites, rights risk, cost risk, technical risk, and milestone fit.

### H. Commercial usefulness

Assess whether the planned evidence system can eventually support profitable work without contaminating the core.

Consider:

- SearchClarity services;
- Neon Ronin workspaces and projects;
- internal evidence products;
- SEO/GEO audits;
- marketplace visibility services;
- competitive intelligence;
- historical monitoring;
- differentiated reports assembled outside Observatory;
- high-value observations competitors often fail to preserve.

Identify where consumer-layer products should live and what evidence they would need from Observatory.

Do not recommend putting customer workflows, recommendations, or report state inside Observatory.

### I. Project hygiene and authority drift

- stale files, trackers, context dumps, handoffs, or milestone statements;
- duplicate or conflicting authority;
- documents that should be archived, superseded, indexed, or corrected;
- missing acceptance records;
- decisions implied by code but not recorded;
- accidental implementation authority;
- test evidence that is not tied clearly enough to commits or decisions.

---

## 8. Required Audit Method

Use evidence from the repo for every major finding.

For each finding:

```text
Finding ID
Severity
Confidence
Category
Exact file paths and relevant sections
What is wrong or missing
Why it matters
Failure scenario
Recommended correction
Recommended milestone or owner gate
Whether it blocks M14 planning, M14 implementation, later provider work, persistence, or consumer work
```

Severity scale:

```text
Critical — doctrine, rights, security, spend, or evidence-integrity failure that should stop advancement
High — serious architectural or governance weakness likely to cause expensive rework or unsafe behavior
Medium — meaningful gap that should be scheduled
Low — cleanup, clarity, or optimization
Opportunity — capability or commercial leverage worth considering
```

Distinguish carefully between:

```text
proven defect
likely defect
missing proof
open design question
future opportunity
personal preference
```

Do not call something a defect merely because you would have designed it differently.

---

## 9. Required Deliverable Structure

Produce one substantial Markdown audit report with these sections:

1. Executive verdict
2. Repo state verified
3. What changed since the M7-era audit
4. Project doctrine as actually implemented
5. Strongest parts of the current system
6. Critical and high-severity findings
7. Medium and low findings
8. M8 hammer audit
9. M9–M12 implementation audit
10. M13 provider-probe audit
11. M14 planning requirements
12. Dangerous-capability opportunities
13. Commercial leverage and consumer-boundary analysis
14. Project hygiene and stale-authority findings
15. Recommended correction sequence
16. Owner decisions required
17. What must remain deferred
18. Final go / conditional-go / no-go recommendation for M14 planning

Include a compact findings table near the top.

Include a dependency-aware correction order, not a random wishlist.

Include a section named exactly:

```text
What I Would Want Before Trusting This With Expensive, High-Value Visibility Evidence
```

Include another section named exactly:

```text
How The Observatory Could Become Unusually Powerful Without Becoming The Strategy Engine
```

---

## 10. Output and Authority Rules

The audit report is advisory source material.

It is not:

```text
accepted doctrine
an owner decision
schema approval
implementation approval
provider admission approval
spend approval
M14 prototype approval
roadmap authority
permission to modify the repo
```

Do not create patches or commits unless explicitly asked after the audit.

Do not stop at praise. The owner wants gaps, failure modes, hard questions, and high-leverage improvements.

Do not manufacture problems to appear thorough. Be precise and evidence-based.

Do not recommend generic enterprise complexity without a concrete failure mode or value case.

Do not confuse a hardened evidence system with a bloated one.

---

## 11. Final Instruction

Clone the repository, read it deeply, and audit the project that actually exists now.

Think like:

```text
a hostile architecture reviewer
a data-provenance specialist
a security and authorization reviewer
a SERP/SEO/GEO measurement expert
a provider-integration skeptic
a commercial intelligence product designer
a future LLM tool consumer
a maintainer who will inherit the consequences
```

The goal is to help the owner and the active ChatGPT steward make The Observatory harder, smarter, more useful, more differentiated, and more commercially powerful without violating its evidence-only identity.
