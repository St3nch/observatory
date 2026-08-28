# RK-01 — DataForSEO Google Related Keywords Live paid-probe adapter

**Status:** review  
**Owner:** [CLAUDE] implementation / [GPT] Steward review  
**Blocked by:** Steward review of this implementation commit  
**Approved by:** [CHAZ] for bounded Related Keywords MVP preparation; [CLAUDE] designated Writer  
**Start commit:** 3d9f5900647767f8d911859ff98c4e70b6966313

## Purpose

Final Steward reconciliation: **ACCEPTED** after the required read-only ticket review
returned `READY_AFTER_TICKET_RECONCILIATION`. The material findings are incorporated below.
Implementation is authorized only from the exact final ticket commit issued by the Steward;
that commit becomes the Writer's `Start commit` in the implementation report.

Implement one closed, Evidence-only DataForSEO Labs Google Related Keywords Live adapter.
The adapter commits and verifies an HTTP-v2 Attempt before its only send-capable path,
performs at most one bounded exchange, commits at most one Capture, and exposes a byte-exact
read-only inspect operation.

This ticket makes **no provider call**. It creates no live Evidence, parser, Conformance
fixture, Recipe, Derivation, Observation, PostgreSQL schema, read API, Measurement Outcome,
Holdings surface, Strategy behavior, panel, cadence, or recurring acquisition.

Related Keywords is selected as one of the two remaining intended Observatory MVP discovery
surfaces before the downstream Strategy Layer checkpoint. Its bounded analytical purpose is
**related-query discovery**: preserve provider testimony connecting one requested seed query
to provider-discovered related queries and their returned provider-native measurements.

Ranked Keywords remains a separate later surface. No work on Ranked Keywords is authorized
by this ticket.

## Authority and Product locks

This ticket follows VISION, VOCABULARY, D2, D3, D8–D13, the current DataForSEO surface
roadmap, PF-09, PF-16/PF-17's closure-owned transport-authority pattern, and the accepted
HTTP-v2 Evidence boundary.

The read-only D12 capability review found the surface suitable for the accepted one-exchange
substrate and returned `READY_AFTER_PRODUCT_RESOLUTION`. [CHAZ] resolves the Product choices
for the first contract as follows:

- provider family: DataForSEO Labs Google Related Keywords Live;
- location: United States, exact `location_code=2840`;
- language: English, exact `language_code="en"`;
- `depth=3`;
- `limit=1000`;
- `offset=0`;
- exact ordering: `keyword_data.keyword_info.search_volume,desc`;
- `include_seed_keyword=true`;
- `include_serp_info=true`;
- `include_clickstream_data=false`;
- `ignore_synonyms=false`;
- `replace_with_core_keyword=false`;
- no filters;
- no tag;
- first later live-capture candidate seed: exact string `conspiracy theories`;
- clickstream demographic acquisition remains out of scope unless a later accepted Product
  decision establishes a reason and retention/privacy posture;
- Related Keywords is sequenced before Ranked Keywords.

The first live-capture candidate does **not** freeze that phrase into product code. The
adapter accepts exactly one bounded operator-supplied keyword under a closed grammar. All
other request dimensions above are fixed by the adapter contract. A later activation ticket
will freeze the exact first live keyword and independently authorize any credentials, spend,
provider transport, and Evidence creation.

## Claimed provider contract — reviewed 2026-08-28

Official provider pages used by the D12 review:

- `https://docs.dataforseo.com/v3/dataforseo_labs/google/related_keywords/live/`
- `https://docs.dataforseo.com/v3/dataforseo_labs/google/keyword_overview/live/`
- `https://dataforseo.com/pricing/dataforseo-labs/dataforseo-google-api`
- `https://dataforseo.com/apis/dataforseo-labs-api/keyword-research`

These are **claimed contract**, not Evidence and not Observatory interpretation authority.
The review reports the current provider documentation as claiming:

- Live-only `POST /v3/dataforseo_labs/google/related_keywords/live`;
- one task per Live call;
- `depth` values 0..4, with documented approximate maximum discovered-keyword counts of
  1 / 8 / 72 / 584 / 4680 respectively;
- `limit` up to 1000 and `offset` pagination;
- default result ordering by `keyword_data.keyword_info.search_volume,desc`;
- optional `include_seed_keyword`, `include_serp_info`, `include_clickstream_data`,
  `ignore_synonyms`, `replace_with_core_keyword`, filters, and tag;
- result-level `seed_keyword`, optional `seed_keyword_data`, `location_code`,
  `language_code`, `total_count`, `items_count`, and `items[]`;
- each item may include `se_type`, `keyword_data`, traversal `depth`, and
  `related_keywords[]`;
- the provider-native `keyword_data` family substantially overlaps Keyword Overview fields
  such as keyword metrics, monthly searches/trend, properties/difficulty, SERP information,
  backlinks information, intent information, and independently updated provider subobjects;
- `include_serp_info=true` makes SERP testimony available where supported;
- clickstream acquisition may expose demographic testimony and carries a materially higher
  pricing/privacy burden;
- current Labs pricing for this family is claimed as `$0.012` per task plus `$0.00012` per
  returned item; pricing must be freshly rechecked before any later live invocation.

The following remain **unproven until committed real Evidence exists** and must not be baked
into parser or Recipe semantics by RK-01:

- whether `total_count` denotes only the selected depth traversal or a broader provider
  corpus;
- whether `related_keywords[]` can be null, absent, empty, duplicated, or unexpectedly
  ordered for returned items;
- whether documented approximate depth maxima are observed for the selected first seed;
- real response key presence, nullability, ordering, additive fields, status behavior,
  provider timestamps, and cost;
- whether the live endpoint accepts the complete frozen request key set exactly as sent,
  including the currently documented-but-undescribed `include_clickstream_data` and
  `ignore_synonyms` booleans;
- whether `include_serp_info=true` materially changes billed cost for this exact endpoint;
- whether the selected `limit=1000` ever binds for a real `depth=3` response; the provider's
  documented depth cardinalities are claimed estimates, not Observatory completeness proof;
- whether one captured response exercises every response-semantic branch needed by a later
  strict Recipe.

## Exact adapter contract

Adapter identity:

`dataforseo-labs-google-related-keywords-live-paid-probe-v1`

Production exchange:

- method: `POST`;
- scheme/host: `https://api.dataforseo.com`;
- path: `/v3/dataforseo_labs/google/related_keywords/live`;
- query: none;
- exactly one task in a canonical JCS UTF-8 JSON array;
- timeout: `httpx.Timeout(connect=30.0, read=120.0, write=30.0, pool=30.0)`;
- adapter-owned response-body ceiling: `33_554_432` bytes;
- redirects, environment proxies, HTTP/2, retry, polling, continuation, pagination,
  response-derived follow-up, and automatic second requests: disabled;
- maximum exchanges under one invocation and one fresh Evidence root: one;
- exact authorization acknowledgement: `200000` micro-USD.

The 32 MiB response ceiling is deliberately conservative for the first enriched Related
Keywords contract because no real Evidence yet establishes response size with up to 1000
returned items and `include_serp_info=true`. It is an adapter-local bound, not a shared Labs
default and not a claim that a normal response is expected to approach 32 MiB.

The exact provider task is:

```json
{
  "keyword": "<one operator-supplied keyword>",
  "location_code": 2840,
  "language_code": "en",
  "depth": 3,
  "limit": 1000,
  "offset": 0,
  "order_by": ["keyword_data.keyword_info.search_volume,desc"],
  "include_seed_keyword": true,
  "include_serp_info": true,
  "include_clickstream_data": false,
  "ignore_synonyms": false,
  "replace_with_core_keyword": false
}
```

`filters` and `tag` are absent rather than sent as null/empty placeholders. Request-body
bytes are `JCS([task])`.

Committed Attempt parameters contain the complete task plus:

```json
{
  "contract": "dataforseo-labs-google-related-keywords-live-paid-probe-v1"
}
```

`contract` is Evidence context and is not sent to DataForSEO.

The closed validator must require the exact key set and fixed values above. It rejects
location/language names, alternate codes, depth other than 3, limit other than 1000,
nonzero offset, alternate ordering, omitted or alternate inclusion flags, clickstream=true,
synonym suppression, core-keyword replacement, filters, tag, unknown keys, boolean values
where exact integers are required, multiple tasks, alternate provider paths, and any hidden
continuation or pagination shape.

The operator keyword is exactly one seed query, not a domain or list. Current Related
Keywords provider documentation requires UTF-8 and lowercases the supplied keyword but does
not publish a Related Keywords-specific character-count or word-count maximum. RK-01 therefore
uses an explicit **Observatory-chosen conservative operator bound**, not a claimed provider
limit: 1..80 printable ASCII characters; at most 10 words separated by ASCII space; must
begin and end with an ASCII alphanumeric; internal characters are limited to
`A-Z a-z 0-9 space & ' ( ) + , . / : -`. This intentionally matches accepted bounded
keyword precedents while keeping the first contract small and deterministic. It does **not**
inherit the Google Organic query-operator deny set; that deny set is SERP-contract policy,
not Related Keywords provider authority.

The first later live activation candidate is `conspiracy theories`, but RK-01 ordinary tests
must use deterministic synthetic/sentinel subjects as appropriate and never call the
provider.

## Cost and policy boundary

The proposed closed Evidence policy is:

```json
{
  "max_authorized_cost_micro_usd": 200000,
  "mode": "paid_probe",
  "policy_version": "dataforseo-labs-google-related-keywords-live-paid-probe-v1",
  "pricing_basis": "dataforseo-labs-google-related-keywords-live-2026-08-28"
}
```

Current claimed pricing puts a fully returned 1000-item response at approximately `$0.132`.
The exact-int `200000` acknowledgement is a bounded fail-closed ceiling with headroom, not
an expected cost, invoice claim, standing spend authorization, or permission to retry.
Current official pricing explicitly documents a 2x multiplier for
`include_clickstream_data=true`, which this contract fixes to `false`; it does not currently
state a separate `include_serp_info=true` multiplier. Do not invent one. Pricing must be
freshly rechecked in the later activation ticket before any live command, and that recheck
must explicitly confirm whether `include_serp_info=true` changes billing for this exact
endpoint before the `200000` acknowledgement is accepted for RK-02.

RK-01 authorizes **zero spend** and **zero provider transport**.

## Required implementation

1. Add one explicit Related Keywords HTTP-v2 adapter branch without changing any accepted
   existing adapter token, byte vector, or identifier.
2. Add one Related Keywords-local paid-probe module and public CLI with `capture` and
   `inspect` operations.
3. Reuse PF-09 `perform_bounded_http_exchange`; do not introduce a generic provider or
   transport-capability framework.
4. Build the transport gate hardened from birth using the accepted PF-16/PF-17 conceptual
   pattern: closure-owned issuance record binds capability identity, concrete
   `EvidenceStore`, committed Attempt identity/preimage, exact committed body bytes, and
   consumed state. Caller-visible capability fields are mirrors only. Unlike PF-16/PF-17's
   deliberately bounded remediation scope, this new gate must also keep the closure-owned
   committed Attempt identity/document authoritative after exchange: expose only the
   smallest Related Keywords-private closure accessor or equivalent closure-local operation
   needed by Capture commit and capture-return construction. Do not add a shared capability
   framework or a caller-visible authority seam.
5. Preserve credential/endpoint validation before closure-owned consumption. After those
   validations succeed, consume before visible-field comparison, committed-Evidence
   revalidation, authorization-header construction, or send.
6. Immediately pre-send, re-read the exact committed Attempt by closure identity,
   integrity-verify the exact Attempt directory, require canonical preimage/content identity,
   read the committed `request.body`, revalidate the Related Keywords-specific closed
   parameters, recompute the exact request body, and require equality across recomputed,
   committed, and closure-owned bytes.
7. Send only closure-owned bytes through PF-09 with the Related Keywords headers, timeout,
   response ceiling, client seam, and exact production path.
8. Require exact Python `int` `200000` authorization. Missing, lower, higher, boolean,
   float, string, decimal, null, or any other value fails before Attempt creation/send.
9. Commit and fully read back the Attempt and exact request body before a transport
   capability is issued.
10. Refuse a second committed Attempt for this exact adapter token in the same Evidence
    root, including unresolved, credential-echo, complete, partial, over-limit, and
    no-response first attempts. Neighbor adapter Evidence may coexist.
11. Inject credentials only after request/store/authorization gates have passed and never
    persist credentials in Evidence. Credential echo in retained body/header testimony
    fails before Capture commit and still consumes the one-shot.
12. Commit at most one verified Capture preserving PF-09 complete/partial/no-response
    transport testimony. Construct the Capture parent from the closure-owned committed
    Attempt document and use the closure-owned `attempt_id` in the returned capture result;
    post-exchange mutation of caller-visible capability mirrors must not alter either.
    Provider HTTP or JSON status does not redefine transport state.
13. Expose byte-exact read-only inspect of a verified complete nonempty Related Keywords
    Capture. Inspect performs no parsing, normalization, network access, or mutation.
14. The internal endpoint seam may target only an exact loopback URL with the production
    Related Keywords path. Every other override shape fails closed before transport.
15. RK-01 must have **no response-body awareness of pagination**. A response body may contain
    bytes that later parse as `total_count > items_count`, a nonzero remainder, a token, or
    any other apparent pagination opportunity, but the adapter does not parse or inspect
    those bytes and still performs at most the one authorized exchange. The proof is
    structural: synthetic response bytes containing such fields are captured byte-exactly
    while the test asserts exactly one handler call. RK-01 never follows `offset` or performs
    a second request.
16. Existing provider Derivations and APIs must not accidentally interpret Related Keywords
    Evidence. Valid Related Keywords Evidence remains raw until RK-03/RK-04.

## Consumer-readiness and inference boundary

RK-01 preserves Evidence only, but its contract must be designed so later stages can answer
the bounded downstream questions honestly.

Later consumers should be able to distinguish:

- the exact requested seed query;
- location/language and the fixed discovery depth;
- returned provider-discovered keyword set and traversal testimony;
- result ordering requested from the provider;
- returned count from any provider-stated larger total;
- provider-native metrics and their own Provider Update Times from Capture time;
- provider monthly Data Periods from acquisition time;
- SERP testimony requested by the verified Attempt;
- a returned zero/empty state from request failure, partial/no-response, or unresolved state.

The unique future fact/relationship family is the provider discovery graph: requested seed
to returned/discovered keyword, traversal depth, and any provider-returned
`related_keywords[]` relationships. The later Recipe should type that graph rather than
discard it, but **RK-01 does not define Observation identity or schema**.

Do not infer from one Capture:

- global keyword absence;
- complete Google related-search coverage;
- provider-corpus completeness;
- stable graph membership over time;
- guaranteed depth cardinality;
- guaranteed item ordering unless verified and accepted later;
- strategy importance, topic clusters, opportunity, difficulty, recommendation, desired
  content, or acquisition cadence.

`depth=3` plus `limit=1000` is selected to make a materially richer first graph while
avoiding the documented depth-4 shape that can exceed one call's 1000-item return ceiling.
That is a Product acquisition boundary, not a claim that depth 3 is complete in the provider
corpus.

If a future verified response reports truncation under this contract, the returned rows are
bounded by the exact request ordering `keyword_data.keyword_info.search_volume,desc`; they
must not be represented as a random or representative sample. RK-01 preserves only the raw
Evidence and request context; RK-03/RK-04 must decide what the real Evidence justifies about
returned-prefix and completeness semantics.

## Public surface

Proposed module:

`observatory.dataforseo_google_related_keywords_paid_probe`

Capture shape:

```bash
uv run python -m observatory.dataforseo_google_related_keywords_paid_probe capture \
  --evidence-root PATH \
  --keyword "ONE SEED QUERY" \
  --authorize-max-micro-usd 200000
```

Inspect shape:

```bash
uv run python -m observatory.dataforseo_google_related_keywords_paid_probe inspect \
  --evidence-root PATH \
  --capture-id 64_LOWERCASE_HEX
```

The public surface exposes no depth, limit, offset, ordering, filters, SERP flag,
clickstream flag, synonym flag, core-keyword replacement, location, language, URL, host,
path, headers, timeout, body ceiling, retry, continuation, or alternate spend argument.

Internal deterministic construction may vary only the operator keyword plus ordinary
Attempt metadata needed for deterministic Evidence identity (`attempt_nonce`,
`authorized_at`, `observatory_version`).

## Required proofs

At minimum, ordinary credential-free tests must prove:

- independent literal JCS request bytes and independent SHA-256 values for one deterministic
  representative seed, without deriving expected literals from production constructors;
- `contract` is committed in parameters and excluded from provider POST bytes;
- every fixed request key/value above is exact, including explicit boolean false values;
- filters/tag are absent, not silently added;
- alternate depth/limit/offset/order/location/language/flags/unknown keys fail closed;
- the operator keyword grammar accepts the intended first candidate and rejects invalid
  subject shapes at the agreed boundary;
- exact `200000` authorization and concrete `EvidenceStore` are required before Attempt
  creation;
- Attempt and exact body are committed/read-back verified before the first local/mock
  handler can observe the request;
- commit failure never reaches transport;
- forged/unissued/subclass/cross-gate capability cannot transport;
- visible request-body replacement, valid Related Keywords document replacement, and
  matching document+body replacement all fail before transport;
- visible `_used=False` reset after one success cannot replay;
- post-exchange mutation of visible `attempt_id`, `document`, or request-body mirrors cannot
  change the Capture's parent Attempt or the returned capture-result `attempt_id`;
- committed object-pool tamper and independent Attempt-bundle `request.body` tamper are
  separately detected before transport;
- pre-send Evidence-verification failure consumes issuance and cannot be retried;
- credential-validation and endpoint-validation failures leave a genuine issuance reusable;
- local handler sees exactly one POST, exact body, exact path, and expected application +
  authorization headers;
- production endpoint restrictions and loopback-only private test seam fail closed;
- a synthetic complete response with `total_count > items_count` performs exactly one
  exchange and no continuation/pagination;
- complete 2xx/non-2xx HTTP response, zero-byte complete response, body-limit partial,
  mid-body partial, and no-response paths retain PF-09 semantics;
- response-header credential names remain omitted and credential echo is rejected before
  Capture commit;
- one-shot refusal applies after unresolved, complete, partial, no-response, and
  credential-echo cases while neighboring adapter Evidence may coexist;
- inspect returns exact complete nonempty body bytes and rejects wrong adapter, malformed
  ID, tampered Evidence, partial/no-response, and zero-body cases;
- existing accepted adapter identity vectors remain byte-identical;
- mixed-store scrub remains clean;
- existing provider Derivations skip valid Related Keywords Evidence and write no rows
  citing its Attempt/Capture IDs;
- public capture/CLI exposes no hidden provider-contract widening seam;
- ordinary tests fail any attempted public-network/DNS access and use sentinel credentials
  only.

The pre-implementation review may recommend deleting redundant proofs or adding a narrowly
missing proof, but it must not weaken Attempt-before-send, one-exchange, closure-owned
authority, Evidence verification, no-network, or exact-contract guarantees.

## Expected changed-path allowlist

Implementation is expected to change only:

- `src/observatory/capture_event.py`;
- `src/observatory/dataforseo_google_related_keywords_paid_probe.py` (new);
- `tests/test_dataforseo_google_related_keywords_paid_probe.py` (new);
- this ticket for implementer Start commit, Status=`review`, and Implementation report.

If a different production/test path is genuinely required, stop and report the exact need
before widening. Do not modify PF-09, Evidence Store, existing provider modules/tests,
parsers, Recipes, Derivations, migrations, PostgreSQL schema, APIs, roadmap/authority docs,
or Strategy.

## Validation boundary

The implementer runs the new Related Keywords test module, any directly affected existing
capture-event/provider tests needed to prove identity preservation, Ruff, touched-path mypy,
and repo-wide mypy relative to the exact final start baseline.

Final repository-wide `uv run pytest -q` remains [CHAZ]-run after Steward review of the
implementation commit.

All ordinary tests require zero DataForSEO/provider calls, zero API-host/DNS/public-network
activity, zero real credentials, zero live Evidence, and zero spend. Local loopback/mock
transport and temporary Evidence Stores are permitted test substrates.

## Required pre-implementation ticket review

Completed by the designated [CLAUDE] Writer at provisional ticket commit
`8644479b388ff992ae4aab30b69e8a85c0367605`. Verdict:
`READY_AFTER_TICKET_RECONCILIATION`.

The Steward independently verified the material findings against repository authority,
current transport/Evidence code, PF-17, and current official DataForSEO documentation. The
accepted reconciliation is:

- close the known PF-17 post-exchange caller-mirror window for this **new** gate rather than
  deliberately reproducing it;
- define the 80-character / 10-word keyword grammar as Observatory policy because the
  Related Keywords documentation publishes no endpoint-specific length/word bound;
- make the no-pagination proof structural and parser-free;
- record live acceptance of the complete frozen key set and real `limit=1000` binding as
  RK-02 Evidence questions;
- retain the `200000` micro-USD acknowledgement because current published pricing keeps the
  documented 1000-item non-clickstream case below it, while requiring RK-02 to recheck
  `include_serp_info=true` billing explicitly rather than speculate about an undocumented
  surcharge;
- retain the 32 MiB adapter-local response ceiling as a conservative first-Evidence bound.

The completed review challenged the ticket against current authority, current
capture-event/provider code/tests, PF-09, PF-16/PF-17, D12/D13, and current official
DataForSEO Related Keywords documentation.

The completed review specifically challenged:

- whether one operator-supplied keyword with every other request knob fixed is the correct
  reuse boundary rather than hardcoding `conspiracy theories` or exposing more options;
- the exact documented keyword constraints and the proposed need for a conservative grammar;
- exact request key names/types and whether explicit false-valued flags are accepted;
- depth=3 / limit=1000 / include_serp_info=true / clickstream=false semantics;
- current pricing and whether the `200000` ceiling remains safely bounded;
- timeout and 32 MiB response-ceiling suitability;
- one-task Live-only/no-continuation assumptions;
- whether the expected changed-path allowlist is sufficient;
- the new gate's closure-owned implementation ordering and whether any PF-17 weakness would
  be copied accidentally;
- one-shot store semantics and coexistence with neighboring adapters;
- deterministic vector/identity preservation proofs;
- synthetic truncation proof (`total_count > items_count`) without parser creep;
- existing Derivation skip/mixed-store behavior without widening production paths;
- consumer-readiness, completeness/absence/limit semantics, provenance, and inference traps;
- any false premise, missing proof, false green, overconstraint, unnecessary coupling, or
  provider-specific fact that should remain unproven until RK-02 Evidence exists.

External technical/provider uncertainty was checked against current official/primary
documentation. That claimed contract remains evidence for design, not repository authority,
and authorizes no provider transport.

## Hard boundaries

Implementation begins only from the exact final accepted ticket commit issued by [GPT]. No
provider call, credentials,
spend, live Evidence, activation, pagination, or push is authorized.

[CLAUDE] is the designated Writer for RK-01. [GPT] owns this ticket except the implementer's
later permitted Start commit, Status=`review`, and Implementation report fields. The
implementer never sets `done`.

## Next boundary

[GPT] commits this final accepted RK-01 ticket and issues that exact commit as the
implementation start commit. Only then may the designated [CLAUDE] Writer modify the
allowlisted implementation paths. No provider transport, credentials, spend, live Evidence,
pagination, or push is authorized by implementation start.

## Implementation report

**Start commit:** `3d9f5900647767f8d911859ff98c4e70b6966313`
**Writer:** [CLAUDE] (designated under `AGENTS.md` §Agent lanes)

### Changed paths

- `src/observatory/capture_event.py` — **purely additive**, 339 insertions, 0 deletions
- `src/observatory/dataforseo_google_related_keywords_paid_probe.py` — new
- `tests/test_dataforseo_google_related_keywords_paid_probe.py` — new
- this ticket — Start commit, Status, Implementation report only

No path outside the allowlist was required.

### Published Related Keywords vector

- request body: **315 bytes** for seed `conspiracy theories`
- body SHA-256: `cf6e74c5ee61c617145fc6e4901046056779815dd3d3dbf154e604a53702bdc1`
- fingerprint: `a766fbbd886e720b4af1ab2016e0b86bcf54a1d2dfb62300e009649f9982b10e`
- Attempt: `5a673a457e994be7fa432f755a1ff8bd7df65a0da9d2c9a5aa35c309a26e9fc6`

The body bytes and SHA-256 were computed by hand during the read-only pre-implementation
review, before any implementation existed, and the production constructors reproduce them
exactly. The test module pins the literals independently of the constructors.

### Validation

- new module: `uv run pytest tests/test_dataforseo_google_related_keywords_paid_probe.py -q`
  — **65 passed**.
- directly affected existing suites (`test_capture_event`, `test_http_event_v2`,
  `test_dataforseo_paid_probe`, `test_dataforseo_sandbox`,
  `test_dataforseo_google_organic_paid_probe`, the three AI Optimization paid probes,
  `test_evidence_store`, `test_evidence_status_scrub`) — **611 passed**.
- `uv run ruff check .` — **All checks passed**.
- touched-path mypy (all three code paths) — **Success, no issues**.
- repo-wide `uv run mypy` — **14 errors in 5 files (82 source files)**, an error set
  byte-identical to the same command at start commit `3d9f590` (80 files). No error is in a
  touched path; the baseline errors are the known `tools/` module-search omission and
  pre-existing Target Metrics / Historical API test typing.
- full-suite `uv run pytest -q` deliberately **not** run; that remains [CHAZ]-run.
- Zero DataForSEO/provider calls, zero API-host/DNS/public-network activity, zero real
  credentials, zero live Evidence, zero spend.

### Strongest part

> **Corrected after Steward review.** The original report claimed closure-owned state was
> authoritative for the entire lifecycle. That claim was **wrong** as first implemented:
> `_Issuance` stored the mutable committed `read_back` mapping and `_committed_attempt`
> returned it directly, so a caller reaching the private seam could mutate closure authority
> in place. See "Steward-directed remediation" below. The claim is accurate only as of the
> amended commit.

The gate is hardened from birth and closure-owned state is authoritative for the **entire**
lifecycle, not only pre-send. `_committed_attempt` is a Related-Keywords-private accessor
that returns the closure-recorded `attempt_id` and a detached Attempt snapshot; Capture
commit and the returned capture result both use it. I verified this is a real proof by
mutation: reverting `_commit_related_keywords_capture` to the sibling adapters'
`attempt=capability.document` makes
`test_post_exchange_mirror_mutation_cannot_change_capture_or_result` commit a Capture whose
parent is `c35831f0…` instead of `5a673a45…` — a genuinely mis-parented Capture. Reverting
`_require_visible_fields_match` fails all three pre-send replacement proofs. Neither test
passes for an adjacent reason.

The post-exchange proof deliberately commits the replacement Attempt into the store first,
so a mis-parented Capture would be a *valid* commit if the mirror still had authority.
Without that step the test would have failed only because `commit_capture`'s
`_require_verified_parent` could not find the replacement — a weaker result that would not
have distinguished the hardening from an Evidence-layer accident.

### Weakest / most fragile part

`_validate_related_keywords_seed` is Observatory policy with no provider-documented bound
behind it. Current Related Keywords documentation specifies only "single keyword", UTF-8,
and lowercase conversion — no character or word maximum — so the 80-character / 10-word /
printable-ASCII rule is a conservative Observatory invention. If the provider silently
accepts richer seeds, this bound rejects work the provider would have served; if the
provider is stricter than we assume, RK-02 discovers it at the cost of the one-shot. The
grammar deliberately allows `site:example.com` because the Google Organic operator deny set
is SERP-contract policy, not Related Keywords authority — but that means an operator-shaped
seed will be sent verbatim and will probably return a thin or empty graph.

Secondary: `_issuance_for` is a linear scan over a closure list that never shrinks, holding
the committed body and preimage for process lifetime. Correct and bounded for a one-shot
adapter; it would need revisiting if a gate ever issued many capabilities.

### Possible false greens

- Mock transport does not prove real httpx wire behaviour; PF-09 is unchanged and separately
  covered.
- The no-pagination proof is structural, not semantic: it proves the adapter performs one
  handler call while capturing bytes that *would* parse as `total_count=5000,
  items_count=100`. It proves the adapter cannot continue because it never parses. It does
  **not** prove anything about real provider pagination.
- `test_seed_grammar_accepts_ordinary_queries` asserts the grammar admits the intended
  shapes; it cannot prove the provider accepts them.
- The alternate-seed adversary (`flat earth`) differs from the issued seed only in keyword,
  reusing nonce and `authorized_at`. Sufficient for distinct preimage and `attempt_id`, but
  it does not prove nonce-level discrimination.
- `RK_RESPONSE_BODY` is a 14-byte synthetic stand-in. Nothing here establishes real response
  size, and the 32 MiB ceiling remains untested against a real 1000-item enriched payload.

### Remaining caller influence

A same-process caller can still replace visible `attempt_id`, `document`, `request_body`,
and `_used` through `object.__setattr__` — they remain mirrors. They can no longer influence
what is sent, whether a replay is permitted, whether Evidence revalidation passes, which
Attempt the Capture cites, or the returned result's `attempt_id`. Caller-supplied
`endpoint`, `client`, and `max_response_body_bytes` remain private `_run_gated_capture`
seams absent from the public function and CLI.

### Architecture drift / coupling

No shared or generic capability framework. `_Issuance`, `_require_visible_fields_match`,
`_revalidate_committed`, `_require_issued`, and `_committed_attempt` are all private to the
Related Keywords closure. Revalidation calls only
`validate_related_keywords_http_parameters` and `related_keywords_request_body_bytes` — no
foreign adapter validator or constructor. The `capture_event.py` change is purely additive:
one recognizer branch, one attempt-v2 branch, two request-only dispatch branches, and the
six Related-Keywords functions. PF-09, the Evidence Store, and every sibling adapter are
untouched, and the KO and Organic published vectors are re-asserted in the new module.

This gate now differs structurally from the other six adapters, which still build their
Capture from `capability.document`. That divergence is deliberate and Steward-directed, but
it is a genuine readability cost: a reader comparing adapters will find seven gates and one
of them shaped differently.

### Evidence / provider traps

- All 12 sent request keys are frozen and validated exactly; `filters` and `tag` are absent
  rather than empty placeholders, so the Attempt records "not requested" rather than a value
  the provider might act on.
- `contract` is committed in Attempt parameters and excluded from the POST bytes.
- Explicit `false` booleans are sent, so a later null `serp_info` or absent clickstream block
  is provably request-disabled by the verified Attempt rather than ambiguous absence.
- Depth 3 with limit 1000 means `limit` is very unlikely to bind (documented depth-3 estimate
  is ~584), so real Evidence will probably not exercise limit truncation. Nothing downstream
  should treat truncation semantics as proven.
- One-shot refusal is keyed on the adapter token within an Evidence root and holds after
  unresolved, complete, partial, and credential-echo first attempts; fixture, KO, and Organic
  Evidence coexist in the same root and scrub clean.

### Closure blockers

None known in scope. Closure needs [CHAZ] full-suite validation and [GPT] review of this
committed diff.

### Deferred / out of scope

- Live acceptance of the frozen key set — including the documented-but-undescribed
  `ignore_synonyms` — remains an RK-02 question; a rejected key would consume the one-shot.
- Whether `include_serp_info=true` changes billing is unproven and must be rechecked before
  RK-02 accepts the `200000` acknowledgement. No surcharge is implemented or assumed.
- Real response semantics, `total_count` meaning, `related_keywords[]` nullability/ordering,
  and depth cardinality all remain RK-02/RK-03 Evidence questions.
- No parser, Conformance fixture, Recipe, Derivation, PostgreSQL schema, API, Holdings,
  Measurement Outcomes, Ranked Keywords, or Strategy work was performed.
- The other six gates retain the PF-16/PF-17-parity post-exchange window; closing it there
  is separate work.

### What later provider gates should reuse conceptually

The shape, not the code: a closure-owned issuance record as sole transport authority;
visible attributes demoted to mirrors for the whole lifecycle, not just pre-send; a minimal
private accessor so Capture commit and the returned result stay authoritative; credential
and endpoint validation before consumption so their failure leaves the issuance reusable;
consumption before any Evidence read so verification failure cannot be retried; pre-send
re-read plus adapter-local recomputation requiring three-way byte equality; and structural
rather than parsed proof that an Evidence-only adapter cannot continue a paginated response.

### What should deliberately remain provider-local

The closed parameter validator and body constructor, the seed grammar, the frozen twelve-key
task, the 200000 micro-USD ceiling, the 32 MiB response ceiling, the one-shot adapter-token
rule, the loopback path restriction, and every error-message text. Each gate must keep its
own published bytes and closed contract independently reviewable; a shared abstraction here
would let one adapter's drift silently change another adapter's authorized request.

## Steward-directed remediation

Steward review of `10e594bf299a367ddb49fb3082d76dad84937119` found one implementation
blocker and three missing required proofs. Remediated in place; the final implementation
remains one commit from start commit `3d9f5900647767f8d911859ff98c4e70b6966313`.

Remediation touched only:

- `src/observatory/dataforseo_google_related_keywords_paid_probe.py`
- `tests/test_dataforseo_google_related_keywords_paid_probe.py`
- this report

`src/observatory/capture_event.py` needed no remediation and is unchanged from the first
implementation; all accepted request bytes, vectors, and existing adapter identities are
untouched.

### Blocker 1 — closure-owned Attempt authority leaked (fixed)

**Confirmed defect.** `_Issuance` held the mutable committed `read_back` mapping and
`committed_attempt()` returned that live object. A same-process caller using the private
seam could mutate closure authority in place; a later `_commit_related_keywords_capture()`
would then consume the mutated parent. Reproduced against `10e594…` before fixing: after
one in-place edit, a re-read of the accessor returned a document canonicalizing to
`c35831f0d74e324677660e58584fd26b22f241c29b889e270c23e73ba1173ce3` instead of the issued
`5a673a457e994be7fa432f755a1ff8bd7df65a0da9d2c9a5aa35c309a26e9fc6`.

**Fix.** The issuance record no longer stores any Attempt mapping. Closure authority is now
exclusively immutable: `attempt_id` (`str`) and `document_preimage` (`bytes`), alongside the
already-immutable `request_body`. A closure-local `_committed_snapshot()` rebuilds a
**detached** document from those bytes on every call via `validate_attempt(preimage)`,
re-canonicalizes it, and requires the recomputed identity to equal the closure `attempt_id`
before returning. Because reconstruction parses bytes, every returned mapping and every
nested child is a fresh object; nothing returned aliases closure state, so mutating a
snapshot — at any depth — cannot reach closure authority. No shared or generic framework was
added; `_committed_snapshot` is private to the Related Keywords closure.

**Adversarial proof.** `test_private_snapshot_mutation_cannot_poison_closure_authority`
commits the replacement Attempt first so mis-parentage would be a *valid* commit, takes the
accessor's return, clears and replaces it in place including a nested `parameters` child,
then requires a fresh accessor read and the committed Capture to still cite
`5a673a45…`. `test_private_snapshot_is_detached_on_every_call` additionally proves distinct
objects and distinct nested children per call. Both **fail against `10e594…`** at the
closure-poisoning assertion — the authority-leak reason, not a missing or malformed parent —
and pass against the amended commit.

### Missing proof 2 — one-shot after `no_response` (added)

`no_response` added to the one-shot parameterisation. The branch performs a genuine
connect-failure first exchange, asserts the committed Capture is
`transport_state=no_response`, then requires the second Related Keywords Attempt in that
Evidence root to be refused before transport.

### Missing proof 3 — inspect wrong adapter (added)

`test_inspect_rejects_valid_wrong_adapter_capture` now supplies two *committed, verifiable*
wrong-adapter Captures — a fixture Capture and a full Google Organic Capture — and requires
Related Keywords inspect to refuse both. The previous test only committed an Organic
Attempt, so it never exercised the decisive valid-Evidence/wrong-adapter path.

### Missing proof 4 — inspect `no_response` (added)

`test_inspect_rejects_no_response_capture` builds a valid Related Keywords `no_response`
Capture, asserts `response is None`, and requires inspect to reject it. Existing partial and
zero-body inspect proofs are preserved unchanged.

### Candid note on proofs 2-4

These three were **coverage gaps, not defects**: all three pass against the original
`10e594…` production code as well as the amended code. Only Blocker 1 was a real behavioural
fault. The Steward was right that their absence left the ticket's required proof set
incomplete, and I should have caught that the wrong-adapter test committed an Attempt where
the requirement called for a Capture.

### Remediation validation

- `tests/test_dataforseo_google_related_keywords_paid_probe.py` — **70 passed** (65 before,
  plus 3 new tests and 2 new parameterised cases).
- affected existing suites (`test_capture_event`, `test_dataforseo_paid_probe`,
  `test_dataforseo_google_organic_paid_probe`, `test_evidence_status_scrub`) —
  **259 passed**.
- `uv run ruff check .` — **All checks passed**.
- touched-path mypy — **Success, no issues**.
- repo-wide `uv run mypy` — **14 errors in 5 files (82 source files)**, error set
  byte-identical to start commit `3d9f590`.
- full-suite `uv run pytest -q` remains [CHAZ]-run after Steward acceptance.
- Zero provider calls, credentials, live Evidence, or spend.

### Updated weaknesses and false-green analysis

The prior report's weakest-part assessment stands: the seed grammar remains Observatory
policy with no provider-documented bound behind it, and `_issuance_for` remains a linear
scan over a never-shrinking closure list.

Two additions:

- **`_committed_snapshot` re-parses and re-validates on every call.** That is what makes it
  safe, but it means Capture construction now depends on `validate_attempt` accepting the
  stored preimage bytes. If a future capture-event change made validation stricter than the
  bytes committed by an older Attempt, Capture commit would fail closed rather than silently
  mis-parent. Failing closed is correct, but it is a new coupling worth naming.
- **A false green I nearly shipped.** The original post-exchange proof would have passed even
  with the authority leak, because it mutated only the *capability mirror*, which the
  accessor never consulted. It took an adversary aimed at the accessor's own return value to
  expose the seam. Any later gate copying this pattern must attack the accessor, not just the
  mirrors — proving the mirror is inert says nothing about whether the accessor is.
