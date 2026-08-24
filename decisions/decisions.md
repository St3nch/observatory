# Observatory Decisions

This register contains settled product decisions. Each entry names the rejected
alternative so future work can review the trade-off without reopening it by accident.

## D1 — Observatory is a standalone multi-consumer data service

**Decision:** Observatory acquires, validates, preserves, and serves reusable SEO/GEO
observation data for many present and future projects.

**Why:** Shared infrastructure prevents each project from building a partial evidence
store and lets historical value compound independently of any one consumer.

**Cost:** Observatory needs a stable service contract and operational ownership even when
only one consumer exists initially.

**Rejected:** Build Observatory as an internal component of the first strategy project.
That would couple the data's lifetime and model to one consumer.

## D2 — Every consumer uses the API

**Decision:** Projects, LLMs, agents, applications, and scripts interact only through a
versioned API for data access. Internal tables, files, credentials, Evidence Store layout,
and storage implementation are private. Service-owned CLI entrypoints may perform capture
and derive operations; they are part of the service, not a consumer bypass of the data
boundary.

**Why:** A durable API boundary lets storage and implementation evolve without forcing
every consumer to migrate in lockstep.

**Cost:** Internal tools must obey the same boundary, and the API must support real
operational needs instead of relying on direct SQL shortcuts.

**Rejected:** Permit trusted local projects or LLM tools to read the database or Evidence
Store directly. Trust does not remove coupling, migration risk, or accidental contract
creation.

## D3 — Strategy stays downstream

**Decision:** Observatory stores observations and their provenance. Interpretation,
recommendations, scoring, reporting narratives, and SEO/GEO strategy belong to separate
consumer systems.

**Why:** Observation history remains broadly reusable only when it is not rewritten around
one project's judgment.

**Cost:** Downstream systems must join Observatory data with their own private context and
strategy state.

**Rejected:** Store strategy beside evidence for convenience. That would blur authority,
introduce consumer-specific state, and make the service less reusable.

## D4 — The data must survive changing software and infrastructure

**Decision:** Multi-year survival is a day-one architecture requirement. The system must
support migrations, upgrades, exports, verified restores, and re-derivation on fresh
infrastructure.

**Why:** Historical SEO/GEO observations cannot be recreated after the fact, and their
value increases over time.

**Cost:** Evidence identity, provenance, migration discipline, backup design, and recovery
verification constrain early implementation choices.

**Rejected:** Treat repository backup or a running database as sufficient durability.
Neither proves that the data can be restored, verified, and served correctly.

**Clarified by D8:** Authoritative survival is proved from the filesystem Evidence Store
(restore → scrub → re-derive into empty PostgreSQL). PostgreSQL backups may speed recovery
but do not satisfy the authoritative recovery proof. Local Evidence commit is not off-host
protection. See D8 and deferred F6.

## D5 — Evidence and projections have different authority

**Status:** Superseded by **D8** for the capture/evidence storage boundary and the
authority of Attempt, Capture, Outcome, and PostgreSQL. Original text retained for
history.

**Decision:** Exact capture evidence and immutable attempt/outcome history are authoritative.
Parsed observations, indexes, summaries, and API query models are versioned and rebuildable.

**Why:** Provider shapes and parsers will change. Preserved evidence permits honest
reprocessing without rewriting history.

**Cost:** The service must track derivation versions and operate rebuild paths.

**Rejected:** Store only normalized rows or provider JSON. Normalized-only storage loses
source detail; JSON-only storage leaves consumer semantics unstable and implicit.

**Supersession note:** D5 correctly separated preserved material from rebuildable
interpretations, but its phrasing treated “attempt/outcome history” as co-equal durable
authority and did not establish the filesystem capture-event aggregate, content-addressed
bodies, full SHA-256 identities, or disposable PostgreSQL. **D8** replaces that boundary
detail. Outcome remains vocabulary (derived classification), not immutable Evidence. The
separation of preserved Evidence from rebuildable Observations/Projections remains in force
under D8.

## D6 — Ordinary tests lead; hammer tests are bounded release work

**Decision:** Unit, integration, API, and real-PostgreSQL tests are the normal development
loop. Suspected high-consequence invariants enter a small backlog for one dedicated
adversarial-testing ticket near production readiness. A smallest decisive hostile test
runs earlier only when a foundational assumption would make continued work unsafe.

**Why:** This preserves development speed without pretending that mocks can prove
concurrency, crash, authorization, spend, or recovery claims.

**Cost:** The project must maintain a disciplined hammer backlog and may occasionally pause
early development for a narrow substrate test.

**Rejected:** Hammer every ticket or defer every hostile test until the end. The first
turns testing into the product; the second can reveal foundational failure too late.

**Clarified by D8:** Claims about Evidence durability, commit markers, fsync, exclusive
no-overwrite install, process death around Attempt/Capture, and multi-process Attempt
authorization require a real supported Evidence Store substrate—not mocks and not
PostgreSQL alone. Claims about rebuildable Outcomes, Observations, and SQL constraints
still use real PostgreSQL. See D8 and deferred F7.

## D7 — Documentation remains compact and pull-based

**Decision:** Observatory follows the VedaOps Project Method: one forcing choice at a time,
immediate decision records, explicit rejected alternatives, ticket-based planning, and
skills invoked only when they unblock the next build step.

**Why:** Prior projects proved that individually reasonable documents can collectively
outgrow execution.

**Cost:** Some useful-looking future design remains unwritten until needed.

**Rejected:** Generate a complete documentation system before implementation. That creates
scope and stale authority faster than it creates working software.

## D8 — Capture-event Evidence boundary

**Decision:** Observatory’s authoritative capture path is a **capture-event aggregate** on
a local POSIX **Evidence Store** (store format 2):

1. **Two immutable event types:** Attempt (committed before any network or fixture
   transport I/O) and Capture (committed after a transport outcome when possible). Each
   Attempt permits at most one Capture. A retry creates a new Attempt.
2. **Filesystem Evidence authority:** Evidence is committed Attempt and Capture manifests
   plus referenced body objects. Request and response bodies are immutable
   SHA-256-addressed filesystem objects. Unresolved recovery journals are recovery
   material until resolved, but are not committed Captures. Ordinary hardlinks from
   event bundles into the content-addressed object pool are forbidden; use independent
   copy or copy-on-write reflink.
3. **Disposable PostgreSQL:** Outcomes and Observations in PostgreSQL are rebuildable from
   a restored, scrubbed Evidence Store. PostgreSQL is not authoritative Evidence and must
   not be required to recover original testimony. Projection tables are deferred for
   fixture v1.
4. **Full SHA-256 identities:** `attempt_id`, `capture_id`, request-body address, and
   response-body address are all 64-character lowercase hexadecimal SHA-256 values. Event
   manifests use RFC 8785 / JCS canonical JSON and exclude their own identifiers from the
   hashed bytes. Every Attempt includes a fresh 256-bit `attempt_nonce`.
5. **Verify-on-read:** Every authoritative read verifies event identity against exact
   stored manifest bytes, the `COMMITTED` marker, body identities, and body sizes before
   use.
6. **No transport before committed Attempt:** Fixture or provider transport must not begin
   until the Attempt event and its request body (when present) are durably committed and
   visible.
7. **Capture transport states:** A Capture records `response_complete`, `response_partial`,
   or `no_response`. Attempt without Capture is **authorized/unresolved** and must not be
   treated as definitely unsent.
8. **Derived Outcome and admission:** Provider interpretation and observation admission
   are versioned Derivations. Outcome is a derived, versioned, operator-facing
   classification—not an Evidence event, Capture substitute, or Evidence parent.
   Observations are admitted only from verified complete Captures that pass adapter
   admission rules.
9. **Observation provenance:** Every Observation cites one verified `capture_id` and its
   `attempt_id`. Refusal, failure, malformed material, partial response, no-response, and
   unresolved activity never masquerade as Observations.
10. **Local commit ≠ off-host protection:** Local Capture commit and off-host replica
    status are distinct and must be reported separately when replica status exists.
11. **Fixture-first implementation:** The first implementation exercises this contract with
    `fixture-panel-v1` without real provider network activity. Paid-provider sequence
    remains unsettled.
12. **Normative detail:** Provider-neutral capture/evidence protocol lives in
    `docs/specs/capture-event-v2.md` and ADR
    `docs/adr/0001-capture-event-evidence-boundary.md`.

**Why:** Irreplaceable history is the exact authorized request and transport testimony.
Collapsing that into PostgreSQL rows, Outcome parents, or free-standing payload files
allows provenance loss, silent overwrite, and false-success Observations. Content-
addressed bodies and verify-on-read make tampering and bit-rot detectable. Disposable
PostgreSQL keeps parser and schema evolution honest.

**Cost:** Capture implementation must own durable filesystem primitives, commit markers,
scrub/restore, and fixture-safe orchestration before rich API features. Operators must
protect the Evidence Store off-host, not only the database.

**Rejected:**

- PostgreSQL (including `BYTEA` columns) as the authoritative store for Attempt, Capture,
  Evidence, or raw request/response bodies;
- dual live authorities that must stay transactionally synchronized;
- flat payload objects without a committed Capture event root;
- Outcome as an immutable Evidence event, Capture substitute, or parent of Evidence;
- truncated digests or UUID (or other non-SHA-256) identities for Attempt, Capture, or
  body addresses;
- ordinary hardlinks that share mutable inode risk between pool objects and bundles;
- treating authorized/unresolved as definitely unsent;
- admitting Observations from partial, no-response, refused, failed, malformed, or
  unresolved paths;
- silently importing provider-specific (for example DataForSEO), pagination, or legacy
  cutover choices from external design drafts as product authority for this clean rebuild.

**Clarifies:** D4 (recovery proof substrate) and D6 (which claims need Evidence Store
vs PostgreSQL tests). **Supersedes:** only D5’s storage-boundary and Outcome-as-history
phrasing; D5’s original text remains above for history. The broader D5 idea that
rebuildable forms are not sole authority remains in force under D8.

## D9 — Provider HTTP foundation is versioned, sandboxed, and Evidence-first

**Decision:** The next bounded provider proof adds HTTP event version 2 on the existing
Evidence Store format 2 and bundle layouts v1. Event version 1 remains byte-for-byte
frozen. One HTTP exchange is one committed Attempt and at most one Capture; redirects are
disabled so transport never performs an uncommitted follow-up request. The first real
adapter is one DataForSEO Google Organic Live Advanced request against
`sandbox.dataforseo.com` under `sandbox_no_spend` policy.

The Attempt preserves the exact credential-free prepared request semantics and exact body
bytes. Credentials are injected only inside transport after the Attempt is durably
committed and verified, and never enter Evidence, logs, URLs, or error text. The Capture
preserves raw response-body bytes and bounded HTTP testimony. Secret-class response-header
values are omitted under a closed rule and their names/counts are recorded so omission
cannot masquerade as absence.

The sandbox tracer is Evidence-only: fixture derivation explicitly skips its adapter
contract before writing any PostgreSQL row. It creates no provider Outcome or Observation
and therefore has no read-API resource yet. A later provider-specific Derivation must emit
an Attempt-stage Outcome for every verified Attempt before it may expose provider Captures
through the API.

**Why:** The completed fixture slice proves the Evidence boundary but cannot admit real
HTTP manifests because its closed event-v1 schemas are intentionally fixture-specific.
Versioned HTTP testimony extends the durable substrate without reinterpreting historical
Evidence, leaking credentials, or prematurely defining strategy-facing provider data.

**Cost:** Mixed stores require version dispatch and explicit adapter filtering. The first
provider Capture is not queryable through PostgreSQL or the API until a provider
Derivation is deliberately designed. Asynchronous provider workflows may require a later
event version with explicit provenance from a source Capture.

**Rejected:**

- changing `FORMAT.json` or the bundle layout merely to add an event schema;
- adding HTTP keys to event version 1;
- following redirects inside one Attempt/Capture exchange;
- using `prior_attempt_id` to imply that a later request was constructed from earlier
  response testimony;
- committing credential headers, cookies, secret-derived hashes, or free-text transport
  errors;
- running fixture admission over provider bodies or writing provider rows under a fixture
  derivation label;
- treating a coarse Outcome as a substitute for the first raw provider Evidence;
- implementing Standard/asynchronous calls, paid transport, a provider catalog, provider
  Observations, project goals, tactics, or strategy in this proof.

**Sequencing authorization:** This is a bounded exception to F3's unmet broad-provider
trigger, authorized by the Product Owner and Steward for sandbox HTTP foundation only.
Paid transport remains blocked by F4, off-host protection by F6, concurrent writers by F7,
HTTP write APIs by F9, and projections by F10.

**Normative detail:** `docs/specs/capture-event-v2.md`, section “Provider HTTP event
version 2.”

## D10 — The first paid probe is one bounded Keyword Overview exchange

**Decision:** Observatory may implement one paid DataForSEO adapter contract for learning:
`dataforseo-labs-google-keyword-overview-live-paid-probe-v1`. One explicit operator
invocation authorizes exactly one POST, containing one task and one to five keywords, to
DataForSEO Labs Google Keyword Overview Live. Location is fixed to United States
(`location_code=2840`), language to English (`language_code=en`), and both SERP
enrichment and clickstream data are fixed off. Redirects, retries, polling, asynchronous
task workflows, endpoint overrides, and automatic follow-up probes are forbidden.

The Attempt records an integer authorization ceiling of 20,000 micro-USD ($0.02) and the
dated published-pricing basis used to judge the closed request shape. The command must
carry the exact ceiling as a deliberate operator acknowledgement; it is not inferred from
credential presence. This is an authorization limit, not a claim that Observatory can
force an external provider's invoice. The request shape and current published price are
verified before the operator run, and the provider-reported cost remains raw Capture body
testimony.

The paid adapter reuses HTTP event version 2, store format 2, bundle layouts v1, the D9
Attempt-before-send capability gate, credential boundary, response-header omission policy,
8 MiB response bound, and complete/partial/no-response semantics. The adapter contract,
target, parameters, policy, and exact request bytes are independently closed. Sandbox
bytes and identities remain unchanged.

The first paid probe remains Evidence-only. It emits no provider Outcome, Observation,
PostgreSQL row, or HTTP API resource. A separately invoked service-owned read-only
operator command may emit the exact verified response body for this adapter so [CHAZ] can
inspect what the endpoint actually returned; that command does not capture, retry, mutate,
normalize, or create a second authority.

**Why:** The sandbox proved authentication, transport, Evidence commit, and scrub, but its
dummy response cannot show which real keyword fields, values, nulls, or costs DataForSEO
returns. A five-keyword Overview request gives high learning value for a few cents while
preserving the one-Attempt/one-exchange boundary and all raw bytes needed for later
provider-specific Derivation.

**Cost:** Event-version-2 validation must dispatch by adapter contract after schema/version
dispatch. The paid transport is intentionally single-purpose and partly duplicates the
sandbox gate. Provider pricing is external and mutable. The first real response cannot be
accepted as sole-copy authority until F6 off-host protection is satisfied.

**Rejected:**

- a generic endpoint runner or caller-supplied URL, headers, task object, location,
  language, enrichment flags, or spend ceiling;
- loading the provider catalog, account User Data, balance, or price endpoints as hidden
  preflight exchanges;
- using one paid invocation for more than five keywords, or automatically issuing the
  next endpoint after success;
- enabling `include_serp_info` or `include_clickstream_data`;
- claiming the $0.02 policy value is a provider-enforced billing guarantee;
- parsing the probe into Outcomes/Observations, PostgreSQL, or an HTTP API;
- authorizing Ahrefs, Semrush, Standard/asynchronous DataForSEO tasks, or another paid
  endpoint.

**Sequencing authorization:** HAM-01 satisfies F4 for this bounded adapter. Implementation
and zero-network deterministic review may proceed. A real paid operator invocation remains
blocked until F6 has an accepted off-host protection path and the Steward issues the exact
one-shot command after rechecking current official pricing. F7 remains deferred because
the accepted runner is one operator and one process; it must not claim concurrent-writer
safety.

**Normative detail:** `docs/specs/capture-event-v2.md`, section “Paid Keyword Overview
probe adapter.”

## D11 — Provider Derivation is recipe-addressed, typed, and time-explicit

**Decision:** The first provider-specific Derivation is authorized only on a new
provider-capable rebuildable substrate. Attempt/Capture/Evidence Store semantics from D8–D10
remain unchanged. Raw provider bytes stay immutable Evidence; every provider Outcome and
Observation remains rebuildable from verified Evidence plus an immutable Derivation recipe.

For provider Derivations, `derivation_version_id` is the lowercase 64-hex SHA-256 of a
closed RFC 8785/JCS **Derivation Recipe** document. A human-readable name may accompany the
recipe but is not identity. The recipe fixes the adapter contract, provider-envelope parser
contract, request/result reconciliation rule, admission and Outcome rules, numeric parsing
semantics, provider-time/data-period semantics, field-state semantics, emitted Observation
kinds, and the extension/drift policy. Any semantic change to those rules requires different
recipe bytes and therefore a new `derivation_version_id`. Fixture v1 keeps its already
accepted operator-supplied semantic labels and is not retrofitted merely to satisfy this
provider rule.

Provider response parsing is strict on known semantics: UTF-8 decoding is strict; duplicate
JSON object member names and non-finite JSON numbers are rejected; decimal-capable provider
values are normalized without a binary-float round trip; required known fields and known
enums/types are versioned by the recipe. A recipe may explicitly mark an object as
extension-permitted. Unknown additive fields in such an object do not invalidate Evidence or
known Observations; they produce rebuildable Derivation diagnostics. Missing/wrong-typed
known fields, malformed provider timestamps/periods, unknown values of a closed enum, or
other recipe-declared semantic drift fail closed for that Capture's provider Observation
set. Drift never rewrites or repairs Evidence.

Request/result reconciliation is semantic, never positional. The exact requested keyword
from the verified Attempt is the Observatory subject for the first Keyword Overview recipe;
the exact provider-returned keyword is preserved separately as provider testimony. A
recipe-defined provider normalization may be used only to reconcile the two. Reconciliation
must be unambiguous: response array order, filesystem walk order, provider task echoes, and
array indexes are not identities. A documented provider omission of a requested keyword may
be admitted as a bounded provider-coverage Observation. Duplicate/unrequested returned
items, or two requested subjects that collapse to one returned provider key without an
unambiguous mapping, fail reconciliation rather than being guessed.

Provider time is explicitly multi-axis. Capture/acquisition time is Observatory provenance;
provider-stated update time belongs only to the provider structure that states it; a data
period such as `(year, month)` is independent of both. Provider-unstated time or period stays
unstated and never inherits Capture time. Provider duration fields are not timestamps.

The provider-capable Observation model uses a generic Observation envelope plus typed
Observation-kind detail relations. The current physical `observations` relation is a
fixture-v1 implementation detail and must not be widened into a universal provider row.
The first provider tickets may add the canonical envelope alongside the existing fixture
relation to keep fixture acceptance stable; that additive sequencing does not make the
fixture relation the long-term definition of Observation. Provider field state is modeled
at the field/fact level where necessary so stated values (including numeric zero), provider
JSON null, permitted absence, request-disabled data, and recipe-defined inapplicability are
not collapsed. Malformed/wrong-typed data is a Derivation failure, not a value state.

Same-recipe re-derivation is content-consistent, not merely duplicate-suppressing. When a
provider Outcome, Observation, or diagnostic natural identity already exists, the intended
derived content must agree exactly; disagreement is a Derivation failure. Provider
idempotency must not rely on `ON CONFLICT DO NOTHING` to conceal changed meaning.

The existing `GET /v1/attempts/{attempt_id}` remains an audit/provenance resource. Before
provider-derived API exposure, recipe selection must no longer be one process-global version
for all adapters. The first consumer-facing provider history API should remain explicit to
its provider/surface semantics rather than prematurely defining a universal SEO metric or
generic cross-provider Observation query contract. Prior recipe versions remain addressable;
strategy, opportunity scoring, and cross-provider interpretation remain downstream.

Ordinary tests never call the paid provider. The verified PF-03 response is promoted, after
exact-byte/hash verification, to a frozen zero-network conformance fixture. Parser and
Derivation tests use that fixture plus bounded adversarial mutations (ordering, duplicate
keys/items, omitted/extra items, count mismatches, decimal lexical forms, invalid numbers,
timestamps/periods, task errors, nullable fields, and permitted unknown extensions). Later
real provider calls, when separately authorized, are contract probes captured as Evidence;
they are not dependencies of the normal test suite.

**Why:** PF-03 exposed real provider structure that the fixture model cannot represent
honestly: nested provider envelopes, non-positional result order, decimal metrics, multiple
independent provider update clocks, revisable historical monthly testimony, and distinct
null/absence/request-disabled states. The Evidence boundary already preserves all of this;
the rebuildable layer must now interpret it without universalizing provider semantics or
inventing false time/identity.

**Cost:** Provider Derivation adds recipe registration, strict parsing, typed detail
relations, diagnostics, reconciliation rules, and adapter-aware API selection. Fixture and
provider rows temporarily use different physical rebuildable relations during the additive
migration. Provider schema changes may require new recipes and re-derivation. This is
deliberate complexity on the disposable side in exchange for preserving Evidence truth and
historical reproducibility.

**Rejected:**

- widening the fixture `observations` row with provider-specific nullable columns;
- a JSONB/EAV provider dump presented as normalized Observation semantics;
- returned-array index or provider result order as Observation identity;
- provider-returned keyword text alone as the subject identity;
- silently mapping ambiguous provider-normalized keywords to request subjects;
- binary floating-point normalization for decimal provider testimony;
- one Observation-level null/value flag for multi-field provider structures;
- inheriting Capture time when the provider does not state update time or data period;
- failing all derivation merely because an explicitly extension-permitted object gained an
  unknown additive field;
- tolerating known-field type/enum/time drift as if it were a harmless extension;
- reusing the fixture parser/classifier as the provider parser;
- live paid-provider access from ordinary tests;
- replacing the Attempt audit endpoint with the first consumer history endpoint;
- designing Google search demand, YouTube interest, YouTube rankings, or future third-party
  metrics as one universal metric before real consumers prove a common projection.

**Normative detail:** `docs/specs/capture-event-v2.md`, section “Provider Derivation after
F11.”

## D12 — Provider interpretation is designed from claimed contract plus bounded real Evidence

**Decision:** Provider onboarding is Evidence-first and bounded by one named analytical
purpose and one materially distinct adapter contract at a time. Before a provider-specific
Derivation Recipe is accepted, the Steward reviews the relevant current provider capability
family far enough to identify useful testimony, request options, historical dimensions,
overlap, cost, and materially different response contracts. That inventory is research, not
authorization. Real **Provider contract probes** are separately authorized only when they
exercise a material contract branch that can change envelope/cardinality, reconciliation or
identity, field state, numeric/time/period semantics, pagination/continuation, or failure
taxonomy.

Official provider documentation is the provider's **claimed contract**. A committed Capture
and its bodies are empirical **Evidence** of what the provider actually returned for one
exact exchange. Neither is Observatory's interpretation contract. The content-addressed
**Derivation Recipe** is normative for what Observatory accepts and how it interprets that
Evidence: required semantics, tolerated additive extensions, preserved provider quirks,
request-disabled states, and fail-closed drift. One observed payload establishes existence,
not invariance; absence from one payload does not prove absence from the provider contract.

Verified probe bytes may be copied into the deterministic test corpus as **Conformance
fixtures**. The fixture proves the recipe/parser against known testimony; it never replaces
Evidence authority, silently tracks the provider's latest behavior, or permits live provider
access from ordinary tests. Resolving provider drift changes recipe semantics only through a
new recipe identity when required; historical Evidence and prior recipes remain unchanged.

Acquisition and interpretation have different reversibility. Interpretation is rebuildable:
returned testimony can remain raw Evidence and be typed later under a new recipe. Acquisition
is not: a time-indexed SERP, citation, ranking, provider snapshot, location/language slice, or
request-enabled enrichment that was never captured may be impossible to reconstruct later.
Therefore raw retention protects against **under-modeling**, not **under-acquisition**. When a
materially useful, historically irrecoverable provider dimension is deliberately not acquired,
the activation review records that choice and the trigger for revisiting it. This requirement
does not justify speculative catalog-wide capture.

A probe set is sufficient when each material mode of the authorized adapter is either
exercised by Evidence, proven request-disabled by the verified Attempt, or explicitly
deferred with a reason. A different path, live/standard/asynchronous workflow, pagination
model, or option set that materially changes response semantics is a different adapter
contract, not merely another sample. Additional calls require separate authorization under
the existing spend, Evidence-protection, and deferred-work gates.

Providers share Observatory's Evidence/Derivation/Observation spine and may later share
lossless subject identity where genuinely common, but provider measurements remain
source-attributed and provider-native. DataForSEO, future Ahrefs, and future Semrush metrics
must not be collapsed into a universal metric merely because field names appear comparable;
semantic comparison and strategy remain downstream under D3.

**Why:** PF-03 demonstrated that real provider testimony can invalidate documentation-only
assumptions about ordering, independent clocks, historical series, decimal forms, and
null/request-disabled states. At the same time, a finite probe corpus cannot establish every
invariant of an external API. Treating documentation, Evidence, and the recipe as distinct
artifacts preserves both empirical truth and a stable fail-closed interpretation boundary.

**Cost:** Each newly activated adapter may require a small number of deliberately chosen
provider probes and explicit decisions about testimony not acquired. The project must resist
both catalog-wide reconnaissance and fixture-as-contract thinking.

**Rejected:**

- designing provider recipes from documentation alone;
- treating one or several observed payloads as the complete provider contract;
- probing an entire provider catalog before a bounded adapter and analytical purpose exist;
- issuing extra paid calls merely to increase sample count after material branches are
  exercised, request-disabled, or explicitly deferred;
- silently re-freezing fixtures to accept provider drift under an unchanged recipe;
- assuming raw Evidence can recover testimony that was never requested or captured;
- requiring a universal cross-provider metric layer before provider-native history APIs.

**Does not fire F3:** Capability-family inventory remains product research. Each new adapter,
paid probe, recurring schedule, or provider still requires its own recorded authorization.

**Normative detail:** `docs/specs/capture-event-v2.md`, section “Provider contract discovery
and conformance.”

## D13 — Materially useful measurement coverage is product direction; activation remains bounded

**Decision:** Observatory intends eventual coverage of materially useful search/AI visibility
measurement families. A family does not require an immediate downstream consumer ticket to
qualify for eventual coverage. Build and activation order is determined by architectural
dependencies, provider contract shape, acquisition safety, historical uniqueness, overlap,
cost, and implementation complexity. Each adapter, provider call, recurring schedule, and
other irreversible acquisition step still requires the existing bounded authorization and
D12 evidence-first review.

**Why:** Historical value compounds only for testimony that was actually acquired. Requiring
an immediate consumer request before a useful family can enter the product direction risks
permanently missing time-indexed evidence and encourages thin adapters. At the same time,
broad product direction must not become speculative catalog-wide collection or bypass spend,
retention, provenance, completeness, and Evidence-protection gates.

**Cost:** The roadmap must distinguish eventual coverage from activation priority, and the
Steward must sequence adapters by readiness and dependency rather than a permanent family
ranking. Some useful families remain unimplemented for long periods while prerequisites are
resolved.

**Rejected:** Treat consumer demand as the existence gate for every measurement family; or,
at the opposite extreme, treat broad product direction as standing authorization to collect
every available provider surface.

**Clarifies:** D12 and deferred F3. F3 remains unfired for routine broad provider/surface
rollout; individually authorized bounded adapters may proceed under D12 when their contract
fits the accepted substrate and all other gates.

## D14 — Provider consumer APIs separate admitted facts, measurement activity, and holdings

**Status:** Accepted shared contract boundary after Keyword Overview, Google Organic, and
Search Mentions consumer reviews. Implementation and the exact failure-inventory mechanism
remain separately gated.

**Decision:** A future connected strategy LLM remains an ordinary API consumer under D2 and
D3. Provider-facing APIs use surface-explicit paths and may share a lossless list envelope,
but they do not share one universal fact body or SEO metric model.

Three consumer resources have distinct meanings:

1. **Observation history** contains only admitted, subject-bound Observation documents under
   one resolved Recipe. Its totals describe that admitted series, not all probes. Keyword
   Overview history contains `observation_admitted` Captures; it must not promise
   `observation_admitted_empty`, because a zero-envelope Keyword Overview Capture has no
   subject-bound coverage document. Another surface may expose admitted-empty history only
   when its Recipe preserves a valid subject-bearing result context.
2. **Measurement Outcomes** expose Attempt- and Capture-stage classifications, including
   unresolved activity, transport/provider failures, rejection, and admitted results, without
   presenting failure material as Observations.
3. **Holdings** expose subjects and measurement inventory that Observatory actually holds.
   Holdings state no importance, priority, desired panel, recommendation, monitoring cadence,
   or strategy-layer intent.

Every bounded consumer list must disclose its scope, `total_matching`, `returned_count`,
applied `limit`, deterministic `order`, and `has_more`. Multiple Captures prove multiple
measurements, not an intentional monitoring program. Reads remain verify-on-read and fail
closed with no partial fact payload when Evidence or rebuildable state disagrees.

Subject identity for non-admitted activity must come from verified Evidence or a rebuildable
index derived from it, not from invented coverage. Reviews of Keyword Overview, Google
Organic, and Search Mentions confirm that current PostgreSQL rows do not retain the requested
subject for all failed or zero-envelope activity, so subject-filtered Outcomes and holdings
are not merely JSON-envelope work. A bounded verified-Evidence scan remains a possible
low-volume bridge, but before recurring F12-scale acquisition the durable path must have a
scalable, rebuildable measurement-subject index. The exact bridge/index mechanism remains a
later Outcomes/holdings ticket boundary; no consumer receives direct Evidence access.

**Google Organic reconciliation:** Google Organic confirms this split with surface-specific
limits:

- admitted-empty history is valid because a successful zero-top-level-item result still
  writes subject-bearing `google_organic_result_context`; it means zero returned top-level
  items, not no organic result, failure, or never measured;
- ranked-result identity remains the accepted placement axes (page, position, rank group,
  absolute rank, and requested keyword). Exact URL and domain remain content; matching them
  across Captures is downstream analysis. A URL-on-SERP identity requires a separately
  authorized new Recipe and digest;
- snippets, AI Overview prose/markdown and source text, and expanded People Also Ask answers
  remain Evidence-only. Serving them requires a new Recipe plus an explicit retention, terms,
  and redistribution decision;
- the closed Live Advanced request and interpretation limits belong in the versioned
  route/OpenAPI contract. Runtime omission arrays are not required. Typed surface response
  models and concise descriptions wait for the shared envelope decision after Search
  Mentions review;
- `group_organic_results=true` can produce non-null `related_result`, which the current
  Recipe deliberately leaves unvalidated and Evidence-only. Any newly encountered complete
  Capture containing non-null `related_result` may be preserved as Evidence but must stop
  before derivation, admission, or API service until the Steward chooses explicit disclosure
  under the current Recipe or a new Recipe. This branch must be resolved before recurring
  F12 acquisition;
- an Outcomes ledger that serves `observation_count` must verify committed Evidence and
  require the stored count to equal Observation-envelope cardinality. Full typed-row and
  subordinate-occurrence consistency remains the admitted fact-document/history boundary.
  The current Attempt audit retains PF-14's accepted narrower behavior until a later Outcomes
  ticket explicitly hardens it.

**Search Mentions question-resolution lock:** The code-first gate fixes these Product and
Steward boundaries for the major review:

- one current Search Mentions Capture is a bounded first-page prefix under the closed
  one-exchange request: offset 0, limit 5, answer scope, and word match.
  `total_count`, `items_count`, and the opaque `search_after_token` are provider
  corpus/truncation testimony, not a continuation queue or authority for another exchange.
  The five returned rows are not a representative sample; unretrieved rows are unknown, not
  unmentioned or absent. Pagination, token-following, another exchange, and recurring F12
  acquisition require separate authorization and provenance design;
- exact Search Mentions question text, Markdown answer, source snippet, and source Markdown
  field state/value remain intentionally typed and API-visible under the accepted
  surface-specific Recipe and read contract. This does not generalize to Google Organic,
  whose prose remains Evidence-only, or authorize text exposure for another surface;
- `observation_admitted_empty` remains a valid subject-bearing Search Mentions history
  document because `search_mentions_result_context` is retained. `total_count=0`
  distinguishes an empty provider corpus from a zero-item page of a nonempty corpus; neither
  state means failure, never measured, or complete absence beyond the closed request;
- Search Mention item identity remains requested keyword, model name, and exact question.
  Source identity additionally includes exact URL. Item indexes and source ranks preserve
  occurrences and ordering; they do not create cross-Capture or cross-surface semantic
  identity;
- D14's future shared list envelope applies to the outer Capture-history list. Inner provider
  paging and truncation remain surface-specific result context. Failure subjects remain
  available only through verified Evidence until a rebuildable inventory boundary exists;
  no failure coverage row may be invented.

This lock authorizes no pagination, provider call, Recipe change, API/schema remediation,
F12 work, or F13-triggering acquisition-gate reuse. F13 still applies before the next live
Search Mentions invocation, substantive gate modification, or reuse.

**Search Mentions reconciliation:** The major review confirms the locked boundary and adds
these implementation facts:

- the typed PostgreSQL and API fact document faithfully preserves the returned AI-03 prefix:
  five item envelopes, sixty monthly-volume envelopes, and forty-eight structured-source
  envelopes with their occurrences. Outcome `observation_count=113` correctly counts those
  Observation envelopes; it is not provider `items_count=5`, corpus size, or question
  count. The required correction is typed contract disclosure, not changing either count;
- the inner result context already preserves `total_count=3055`, `items_count=5`, offset,
  and the opaque token. The remaining defect is that the route/OpenAPI contract does not
  explain the bounded-prefix, identity, text, empty-state, or count semantics clearly enough
  for an API-only LLM;
- the outer history list still slices matching Captures at `limit` without
  `total_matching`, `returned_count`, or `has_more`. History also cannot distinguish
  failed activity from never measured. These confirm the shared list-envelope and separate
  Outcomes/holdings work rather than a Search Mentions Recipe defect;
- requested keyword remains top-level/result-context testimony and is revalidated against
  the verified Attempt. Its deliberate omission from the nested request object is not data
  loss. Current item/source identities, occurrence relations, and Search Mentions text
  exposure require no remediation;
- exact question/answer text linked to structured source URLs, occurrence testimony, distinct
  current and monthly volumes, and explicit unknown remainder are unusually valuable
  downstream testimony. Provider count, volume, model, clock, and source claims remain
  attributed and must not be promoted to universal truth or cross-surface equivalence.

With all three implemented provider surfaces reviewed, the intended implementation sequence
is the shared history list envelope, then sibling Outcomes, then holdings. Search
Mentions-local typed/OpenAPI descriptions should build on the accepted shared envelope.
This reconciliation authorizes none of that implementation.

**Why:** The first Keyword Overview consumer review found strong typed facts, field states,
Recipe identity, time axes, and integrity behavior, but admitted-only subject lookup, silent
list slicing, no discovery, and no failure inventory can mislead an API-only LLM about what
was measured and whether a returned list is complete.

**Cost:** The API gains several explicit resources instead of one convenient generic query.
Failure-aware subject discovery may require a new rebuildable index. Each surface must define
whether admitted-empty is a meaningful subject-bound document.

**Rejected:** Treat `/history` as all measurement activity; return a bounded slice without
cardinality disclosure; manufacture coverage rows for failures or empty Captures; overload
Outcome with provider-specific subject arrays; expose direct database or Evidence access;
encode panels, cadence, scoring, or recommendations in Observatory; or force unlike provider
facts into one shared response body.

**Implementation boundary:** This decision records the accepted consumer contract only. It
does not authorize API/schema work, provider calls, spending, F12 orchestration, or AI-12.
