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
