# RK-01 — DataForSEO Google Related Keywords Live paid-probe adapter

**Status:** provisional-review  
**Owner:** [CLAUDE] implementation / [GPT] Steward review  
**Blocked by:** designated implementer read-only pre-implementation review and Steward reconciliation  
**Approved by:** [CHAZ] for bounded Related Keywords MVP preparation; [CLAUDE] designated Writer  
**Start commit:** pending final Steward acceptance

## Purpose

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
- whether `include_serp_info=true` materially changes billed cost for this exact endpoint;
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

The operator keyword is exactly one seed query, not a domain or list. The implementer must
propose and test a conservative bounded grammar based on provider documentation and existing
accepted operator-subject precedents. The grammar must be broad enough for ordinary search
queries such as `conspiracy theories` without silently importing Google Organic query
operator semantics or Search Mentions target grammar. If current provider documentation
requires a materially different length/character bound than existing precedents, the
pre-implementation review must report it before implementation.

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
Pricing must be freshly rechecked in the later activation ticket before any live command.

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
   consumed state. Caller-visible capability fields are mirrors only.
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
    transport testimony. Provider HTTP or JSON status does not redefine transport state.
13. Expose byte-exact read-only inspect of a verified complete nonempty Related Keywords
    Capture. Inspect performs no parsing, normalization, network access, or mutation.
14. The internal endpoint seam may target only an exact loopback URL with the production
    Related Keywords path. Every other override shape fails closed before transport.
15. A response claiming `total_count > items_count`, a nonzero remaining result set, or any
    other pagination opportunity must still produce at most the one authorized exchange.
    RK-01 never follows `offset` or performs a second request.
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

Before implementation, the designated [CLAUDE] Writer must challenge this exact provisional
ticket read-only against current authority, current capture-event/provider code/tests,
PF-09, PF-16/PF-17, D12/D13, and current official DataForSEO Related Keywords documentation.

Specifically challenge:

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

External technical/provider uncertainty should be resolved with current official/primary
documentation rather than guessing. Web research is evidence, not repository authority and
does not authorize provider transport.

Return exactly one:

`READY`

`READY_AFTER_TICKET_RECONCILIATION`

or

`NOT_READY`

Do not edit, commit, push, invoke providers, use credentials, or create Evidence during the
review.

## Hard boundaries

No implementation begins from this provisional ticket commit. No provider call, credentials,
spend, live Evidence, activation, pagination, or push is authorized.

[CLAUDE] is the designated Writer for RK-01. [GPT] owns this ticket except the implementer's
later permitted Start commit, Status=`review`, and Implementation report fields. The
implementer never sets `done`.

## Next boundary

Commit this provisional ticket only. [CHAZ] relays the read-only ticket-review result to
[GPT]. [GPT] reconciles the findings, commits the final accepted RK-01 ticket, and issues the
exact implementation start commit. Only then may the designated [CLAUDE] Writer modify the
allowlisted implementation paths.
