# Capture Event v2 — Normative Contract

**Status:** accepted normative specification (CE-01 authority package; Q37 schemas)
**Authority parents:** VISION.md, VOCABULARY.md, D8, D9, D10, ADR 0001
**Store format:** 2
**Attempt bundle layout:** v1
**Capture bundle layout:** v1

This document is the implementation contract for Attempt, Capture, Evidence Store,
fixture-panel-v1, rebuildable Outcomes/Observations, and the fixture vertical-slice proof.
It does not supersede VISION or the decision register. When a term is defined in
VOCABULARY.md, that definition controls.

Identity-bearing JSON documents are **closed schemas**. Unknown properties are
**forbidden recursively** on every object type defined below. Two independent
implementations that follow only this document and the same inputs must produce
byte-for-byte identical canonical documents and content IDs.

fixture-panel-v1 transport is fully deterministic for **every** valid request
(`panel_id`, `subject_key`, `depth`, `scenario`). The scenario construction algorithm
below has zero implementation choices.

---

## Problem

Observatory must preserve irreplaceable authorized-request and transport testimony,
admit Observations only when justified, and rebuild query data without treating
PostgreSQL as the sole surviving record.

## Authority

| Layer | Owns |
|---|---|
| VISION.md | Product lifecycle, survival, v1 proof intent |
| VOCABULARY.md | Term meanings |
| decisions/decisions.md (D8) | Settled trade-offs |
| docs/adr/0001-capture-event-evidence-boundary.md | Why the boundary is fixed |
| **This spec** | Format, closed schemas, construction, fixture algorithm, vectors |
| decisions/deferred.md | Deferred work |

`docs-temp/`, external drafts, and git stash are not authority.

---

## Invariants

1. No transport before a verified committed Attempt.
2. ≤1 Capture per Attempt; retry = new Attempt + new `attempt_nonce`.
3. Evidence = committed Attempt/Capture manifests + body objects only.
4. PostgreSQL is disposable and rebuildable.
5. Outcome is derived classification, not Evidence.
6. Observations only from complete + admission success.
7. Full lowercase 64-hex SHA-256 identities; no truncated digests.
8. Verify-on-read; never silent repair.
9. `COMMITTED` last.
10. Ordinary hardlinks into the object pool forbidden.
11. No secrets in Evidence.
12. Local commit ≠ off-host protection.
13. The accepted first proof is fixture-only (`fixture-panel-v1`); provider network is
    permitted only under D9/D10 and never from ordinary automated tests.
14. Recursive unknown-key rejection on all identity-bearing objects.
15. fixture-panel-v1 transport is in-process, not HTTP; Capture v1 response has no HTTP
    status, `http_version`, or `url`.
16. Each conformance Capture cites exactly one scenario-matching Attempt; no multi-Capture
    reuse of one `attempt_id` in the published corpus.

---

## Evidence Store format 2

### FORMAT.json

Single Evidence root. `FORMAT.json` written once, exclusive no-overwrite. Opening requires
**exact** canonical UTF-8 RFC 8785/JCS bytes (no trailing newline) and matching digest.

```text
{"attempt_bundle_layout":"v1","body_addressing":"sha256-content","bundle_body_materialization":"fixed-names-v1","canonical_json":"rfc8785-jcs","capture_bundle_layout":"v1","committed_marker":"event-id-newline","durability_profile":"local-posix-fsync-v1","event_id_encoding":"lowercase-hex-sha256","hash_algorithm":"sha256","path_sharding":"sha256-aa-bb","schema":"observatory.evidence-store-format","store_format":2,"timestamp_encoding":"utc-six-fractional-digits-z"}
```

**SHA-256 (no trailing newline):**

```text
67fb338d3237a22a29f50110c705e552cd9af29f830c1bfffa9ee1cafa876c7e
```

### Paths and bundles

```text
FORMAT.json
objects/sha256/<aa>/<bb>/<64-hex>
attempts/v1/<fp[0:2]>/<fp[2:4]>/<request_fingerprint>/<YYYY>/<MM>/<DD>/<attempt_id>/
captures/v1/<capture_id[0:2]>/<capture_id[2:4]>/<capture_id>/
journal/
derived/
.locks/
.tmp/
```

Date path components derive only from Attempt `authorized_at`. Bundle files:
`attempt.json` / `capture.json`, optional `request.body` / `response.body`, `COMMITTED`
with exact content `<event_id>\n`. Materialize bodies by independent copy or COW
reflink only.

### Scalar constraints (global)

| Kind | Exact constraint |
|---|---|
| Timestamp string | `YYYY-MM-DDTHH:MM:SS.ffffffZ` only (six fractional digits, uppercase `Z`) |
| Digest / ID / fingerprint / nonce hex | lowercase `[0-9a-f]{64}` only |
| Non-negative integer | JSON number without fraction/exponent; `0 ≤ n ≤ 9007199254740991` (2⁵³−1) |
| `depth` | JSON integer 1..16 inclusive |
| `observatory_version` | `[A-Za-z0-9._+:-]{1,128}` |
| `panel_id` / `subject_key` | `[A-Za-z0-9._:-]{1,128}` |
| Header name | lowercase string as stored |
| Pair | JSON array of exactly two strings |

No floating-point values in identity-bearing documents.

**Integer range is normative, not incidental.** Every integer in an identity-bearing
document must satisfy `-9007199254740991 ≤ n ≤ 9007199254740991` — the I-JSON
safe-integer range. Values outside it are rejected, not serialized.

This bound is **Observatory policy**, not a rule RFC 8785 imposes. RFC 8785 requires I-JSON
conformance and defers number serialization to ECMAScript; I-JSON (RFC 7493 §2.2) states
that a sender cannot expect a receiver to treat an integer outside
`[-(2**53)+1, (2**53)-1]` as an exact value. We turn that interoperability guidance into a
hard limit because these integers are identity-bearing: a value a receiver may not preserve
exactly is a value whose digest may not reproduce.

What the bound buys, stated precisely:

- **Exactness.** Every integer within the range has an exact IEEE 754 double
  representation. Outside it, *some* integers remain exact — 2⁵⁴ and other larger powers of
  two among them — but the representable set grows sparse, and inexact values round to a
  neighbour: `9007199254740993` becomes `9007199254740992`.
- **Plain decimal rendering.** ECMAScript switches to exponential notation at magnitude
  10²¹ and above, so a conforming serializer emits `1e+30` for `10³⁰`. That threshold sits
  far **above** 2⁵³−1 (≈ 9.007×10¹⁵), so the safe-integer bound binds first and exponential
  formatting never arises for a permitted value.

Together these mean a plain decimal rendering of any permitted integer is byte-identical to
conforming JCS output. An implementation needs no exponential serializer — but only because
the range is bounded. Rendering unbounded integers as plain decimals is not JCS.

The encoder applies the signed range. Fields that this specification defines as non-negative
are further constrained to `0 ≤ n ≤ 9007199254740991` by their own field rules.

### I-JSON admissibility (complete set)

RFC 8785 requires I-JSON input, so an identity-bearing document is admissible only if it
satisfies **every** constraint below. These are the RFC 7493 **MUST**-level constraints,
plus the integer range Observatory hardens from a SHOULD to a MUST. It is enumerated here
because these were previously discovered one defect at a time.

| # | Requirement | Source |
|---|---|---|
| 1 | Encoded as UTF-8 | RFC 7493 §2.1 |
| 2 | No surrogate code points in object names or string values | RFC 7493 §2.1 |
| 3 | No Unicode **noncharacters** in object names or string values | RFC 7493 §2.1 |
| 4 | Integers within the safe range above | RFC 7493 §2.2, hardened by Observatory |
| 5 | No duplicate object member names | RFC 7493 §2.3 |

RFC 7493 §2.2 carries a second, SHOULD-level constraint: avoid numbers exceeding IEEE 754
binary64 magnitude or precision, such as `1E400`. Observatory subsumes it by forbidding
floating-point values outright, which is stricter. It is therefore absent from the table by
satisfaction, not by oversight.

RFC 7493 §4 constraints — top-level object or array, must-ignore, ISO 8601 timestamps,
base64url — are protocol-design SHOULDs rather than message admissibility rules, and closed
schemas deliberately contradict must-ignore. Well-formed JSON is a prerequisite of §2, not a
sixth rule.

Constraints 2 and 3 apply to code points **however they arrive** — encoded directly or
arriving as `\u` escapes in parsed input. Rejecting them at serialization alone is
insufficient when a document is validated from stored bytes.

A **valid surrogate pair is not a surrogate.** `"\uD800\uDEAD"` is legal I-JSON: it decodes
to a single scalar value, and rejecting it would be a conformance defect in the opposite
direction. Only unpaired surrogates are inadmissible.

The noncharacters are the 66 code points `U+FDD0`–`U+FDEF`, plus the last two of every
plane: any code point where `cp & 0xFFFE == 0xFFFE`, which covers `U+FFFE`, `U+FFFF`,
`U+1FFFE`, `U+1FFFF`, through `U+10FFFE` and `U+10FFFF`. `U+FDCF` and `U+FDF0` sit just
outside the block and are ordinary characters.

Inadmissible input is rejected. It is never serialized, substituted, or repaired — a
repaired document would carry an identity for content that was never received.

Discovered during CE-02 implementation: the bound was previously unstated.

### Canonicalization and verify-on-read

1. Build a value that matches a closed schema (unknown keys already rejected).
2. Serialize with RFC 8785 JCS as UTF-8 **without** trailing newline.
3. Hash = lowercase hex SHA-256 of those exact bytes.
4. Persist exactly those bytes.

**Verify-on-read (unchanged order):**

1. Read exact stored manifest bytes.
2. SHA-256; require equality with directory/`COMMITTED` ID.
3. Schema-validate; require re-JCS of the parsed value equals stored bytes.
4. Cross-field rules.
5. Verify every cited body digest and size.
6. Fail closed on any mismatch; never silent repair.

`attempt_id` / `capture_id` = SHA-256 of stored manifest bytes; those IDs are **not**
fields inside the preimage. Body address = SHA-256 of body bytes; `bytes` = length.

---

## Closed schemas

### Recursive unknown-key rule

Every object type below has a **closed** property set. Any property not listed for that
type, at any nesting depth, is invalid. Arrays have no extra elements beyond stated
structure.

### `body_ref`

| Property | JSON type | Required | Null? | Constraint |
|---|---|---|---|---|
| `sha256` | string | yes | no | `[0-9a-f]{64}` |
| `bytes` | integer | yes | no | ≥ 0; equals actual body length |

No other properties (including no `representation`).

### `body_state`

Discriminated by `state`. Exactly one of three shapes:

| `state` value | Other properties | Rules |
|---|---|---|
| `absent` | *(none)* | `body` must be **omitted** (not null) |
| `present_zero_bytes` | `body` (`body_ref`, required) | `body.bytes` = 0; `body.sha256` = SHA-256 of empty bytes `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `present_nonempty` | `body` (`body_ref`, required) | `body.bytes` ≥ 1 |

`state` is string enum: `absent` | `present_zero_bytes` | `present_nonempty`.

### `request`

| Property | JSON type | Required | Null? | Constraint |
|---|---|---|---|---|
| `method` | string | yes | no | non-empty |
| `scheme` | string | yes | no | non-empty |
| `host` | string | yes | no | non-empty |
| `port` | integer or null | yes | **may be null** | if integer: 1..65535 |
| `path` | string | yes | no | non-empty; begins with `/` |
| `query` | array | yes | no | each element pair of two strings; may be `[]` |
| `headers` | array | yes | no | each element pair of two strings; names lowercase |
| `body` | object | yes | no | closed `body_state` |

Array order of `query` and `headers` is identity-bearing.

### fixture-panel-v1 request constants

For every fixture-panel-v1 Attempt and Capture, `request` **must** equal exactly:

| Property | Exact constant |
|---|---|
| `method` | `POST` |
| `scheme` | `fixture` |
| `host` | `fixture-panel` |
| `port` | `null` |
| `path` | `/v1/measure` |
| `query` | `[]` |
| `headers` | `[["content-type","application/json"]]` |
| `body.state` | `present_nonempty` |
| `body.body` | `body_ref` for the exact JCS UTF-8 request document bytes |

No additional or duplicate request headers.

### `parameters` / fixture request document

| Property | JSON type | Required | Null? | Constraint |
|---|---|---|---|---|
| `contract` | string | yes | no | exactly `fixture-panel-v1` |
| `panel_id` | string | yes | no | `[A-Za-z0-9._:-]{1,128}` |
| `subject_key` | string | yes | no | `[A-Za-z0-9._:-]{1,128}` |
| `depth` | integer | yes | no | 1..16 |
| `scenario` | string | yes | no | enum below |

**`scenario` enum (exactly ten):**
`admitted_results` | `admitted_empty` | `provider_refusal` | `provider_failure` |
`malformed_response` | `wrong_media_type` | `response_partial` | `no_response` |
`extra_subject` | `too_many_results`

Unknown scenario → reject before Attempt. Request body bytes = JCS(`parameters`) UTF-8
with no trailing newline. Attempt.`parameters` must deep-equal the decoded body object.

### `software`

| Property | JSON type | Required | Null? | Constraint |
|---|---|---|---|---|
| `observatory_version` | string | yes | no | `[A-Za-z0-9._+:-]{1,128}` |

### `policy` (fixture-panel-v1)

| Property | JSON type | Required | Null? | Constraint |
|---|---|---|---|---|
| `mode` | string | yes | no | exactly `fixture_no_spend` |
| `policy_version` | string | yes | no | exactly `fixture-v1` |

### `request-fingerprint` document

| Property | JSON type | Required | Null? | Constraint |
|---|---|---|---|---|
| `schema` | string | yes | no | exactly `observatory.request-fingerprint` |
| `version` | integer | yes | no | exactly `1` |
| `provider` | string | yes | no | exactly `fixture` |
| `adapter_contract` | string | yes | no | exactly `fixture-panel-v1` |
| `request` | object | yes | no | closed `request` (fixture constants) |

No other keys. `request_fingerprint` (Attempt/Capture field) = SHA-256(JCS(this document)).

### Attempt manifest (`observatory.attempt-event`)

| Property | JSON type | Required | Null? | Constraint |
|---|---|---|---|---|
| `schema` | string | yes | no | exactly `observatory.attempt-event` |
| `version` | integer | yes | no | exactly `1` |
| `attempt_nonce` | string | yes | no | `[0-9a-f]{64}` encoding **exactly 256 bits** |
| `provider` | string | yes | no | exactly `fixture` |
| `adapter_contract` | string | yes | no | exactly `fixture-panel-v1` |
| `authorized_at` | string | yes | no | timestamp string syntax |
| `request_fingerprint` | string | yes | no | `[0-9a-f]{64}`; must equal recompute |
| `request` | object | yes | no | closed `request` |
| `parameters` | object | yes | no | closed `parameters` |
| `policy` | object | yes | no | closed `policy` |
| `software` | object | yes | no | closed `software` |
| `prior_attempt_id` | string | **optional** | **never null** | if present: `[0-9a-f]{64}`; **omit when absent** |

**Forbidden:** `attempt_id` inside preimage, response fields, Outcome fields, secrets,
unknown keys.

`attempt_id` = SHA-256(JCS(Attempt manifest)).

### Capture `response` object (when non-null)

| Property | JSON type | Required | Null? | Constraint |
|---|---|---|---|---|
| `headers` | array | yes | no | pairs; fixture rules below |
| `body` | object | yes | no | closed `body_state` |
| `completeness` | string | yes | no | exactly `complete` or `partial` |

**Forbidden:** HTTP `status`, `http_version`, `url`, unknown keys.

### Capture `transport_failure` object (when non-null)

| Property | JSON type | Required | Null? | Constraint |
|---|---|---|---|---|
| `phase` | string | yes | no | exactly `receive_response` |
| `code` | string | yes | no | exactly `fixture_no_response` |

### Capture manifest (`observatory.capture-event`)

| Property | JSON type | Required | Null? | Constraint |
|---|---|---|---|---|
| `schema` | string | yes | no | exactly `observatory.capture-event` |
| `version` | integer | yes | no | exactly `1` |
| `attempt_id` | string | yes | no | `[0-9a-f]{64}` of parent Attempt |
| `provider` | string | yes | no | exactly `fixture`; equals Attempt |
| `adapter_contract` | string | yes | no | exactly `fixture-panel-v1`; equals Attempt |
| `transport_state` | string | yes | no | `response_complete` \| `response_partial` \| `no_response` |
| `request` | object | yes | no | closed `request`; deep-equals Attempt.request |
| `request_fingerprint` | string | yes | no | `[0-9a-f]{64}`; equals Attempt |
| `software` | object | yes | no | closed `software` |
| `request_started_at` | string | yes | no | timestamp |
| `response_headers_at` | string or null | yes | **null only for `no_response`** | timestamp when non-null |
| `response_body_ended_at` | string or null | yes | **null only for `no_response`** | timestamp when non-null |
| `transport_ended_at` | string | yes | no | timestamp |
| `response` | object or null | yes | **null only for `no_response`** | closed response object when non-null |
| `transport_failure` | object or null | yes | **null except `no_response`** | closed failure when non-null |

**Branch rules:**

| `transport_state` | `response_headers_at` | `response_body_ended_at` | `response` | `transport_failure` |
|---|---|---|---|---|
| `response_complete` | non-null | non-null | non-null; `completeness=complete` | `null` |
| `response_partial` | non-null | non-null | non-null; `completeness=partial`; body `present_nonempty` | `null` |
| `no_response` | `null` | `null` | `null` | exact failure object |

Timestamp order when intermediates non-null:
`request_started_at <= response_headers_at <= response_body_ended_at <= transport_ended_at`.
Always: `request_started_at <= transport_ended_at`.

`capture_id` = SHA-256(JCS(Capture manifest)). **Forbidden** inside preimage: `capture_id`,
Outcome fields, secrets, unknown keys, `elapsed_ms`.

### Provider HTTP event version 2

D9 authorizes this section. It does not change `FORMAT.json`, store format 2, or either
bundle layout v1. “New Capture layout/manifest version” means a new event-manifest
version in the existing layout, not a new Evidence Store format.

#### Dispatch and compatibility

`observatory.request-fingerprint`, `observatory.attempt-event`, and
`observatory.capture-event` version 1 remain exact and continue to mean
`fixture-panel-v1`. Version 2 is the HTTP envelope below. A reader may inspect only
`schema` and `version` to choose a validator; the selected validator must then re-check
both fields, the complete closed schema, cross-field rules, and re-JCS equality. Unknown
schema/version or adapter contract fails closed. A committed unknown event is an integrity
failure, not an ignored event.

Store paths remain `attempts/v1/...` and `captures/v1/...`. Scrub verifies every candidate
under its event version. A mixed store containing valid event versions 1 and 2 is healthy.
Fixture derivation must select `adapter_contract == "fixture-panel-v1"` before writing any
PostgreSQL row; it skips version-2 DataForSEO events without rows and without an integrity
failure. Existing fixture API reads remain valid in a mixed store. Provider HTTP events
have no API resource until a provider-specific Derivation exists.

#### First adapter contract

The only event-version-2 adapter initially recognized is:

    dataforseo-serp-google-organic-live-advanced-sandbox-v1

Its provider is exactly `dataforseo`. Its HTTP target is exactly one POST to
`https://sandbox.dataforseo.com/v3/serp/google/organic/live/advanced`. The request contains
exactly one task. Redirect following is disabled; a 3xx response is complete testimony for
this exchange and never authorizes an implicit second request.

The closed `parameters` object is:

| Property | JSON type | Constraint |
|---|---|---|
| `contract` | string | exact adapter-contract token above |
| `keyword` | string | 1..700 Unicode scalar values; global I-JSON rules apply |
| `location_code` | integer | 1..9007199254740991 |
| `language_code` | string | lowercase `[a-z]{2}` |
| `depth` | integer | exactly `10` |
| `device` | string | exactly `desktop` |
| `os` | string | exactly `windows` |

The provider task is `parameters` without `contract`. Request-body bytes are the UTF-8 JCS
serialization of a singleton array containing that task, with no trailing newline. Those
exact bytes are installed before Attempt commit and sent unchanged. JCS here is this
adapter's deterministic construction rule, not a general rule that provider bodies are
normalized; future adapters may freeze other exact byte forms.

The closed `policy` is
`{"mode":"sandbox_no_spend","policy_version":"dataforseo-sandbox-v1"}`. Cross-field
validation requires scheme `https`, host `sandbox.dataforseo.com`, null port, the exact
path above, and empty query. A production host or different policy is rejected before
transport. This authorizes no paid call.

The committed request header array is exactly, in this identity-bearing order:

    [["accept","application/json"],["accept-encoding","identity"],
     ["connection","close"],["content-type","application/json"],
     ["user-agent","observatory-dataforseo-v1"]]

It represents the complete credential-free application header set. The transport may add
only: (a) `authorization` after verified Attempt issuance, and (b) protocol-computed
`host` and `content-length`. No other sent header is permitted. Request header names are
lowercase. `authorization`, `proxy-authorization`, and `cookie` are forbidden in the
committed request; credentials are also forbidden in URL userinfo, query, parameters, and
body. The transport client must use `trust_env=False` so credentials cannot be routed
through an ambient proxy.

Credential environment names are `OBSERVATORY_DATAFORSEO_LOGIN` and
`OBSERVATORY_DATAFORSEO_PASSWORD`. Names are configuration; values must never enter
Evidence, stdout/stderr, logs, exceptions, or test snapshots.

#### Paid Keyword Overview probe adapter

D10 adds exactly one second event-version-2 adapter:

    dataforseo-labs-google-keyword-overview-live-paid-probe-v1

Its provider is exactly `dataforseo`. Its target is exactly one POST to
`https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_overview/live`. The
request contains exactly one task. Redirects, retries, polling, task-post/task-get,
account/catalog/User-Data preflights, and any second exchange are forbidden.

The closed `parameters` object is:

| Property | JSON type | Constraint |
|---|---|---|
| `contract` | string | exact paid adapter-contract token above |
| `keywords` | array of strings | length 1..5; order identity-bearing; no duplicates |
| each keyword | string | 1..80 printable ASCII characters; at most 10 words, where a word is a maximal nonempty run separated by ASCII space; begins and ends with ASCII alphanumeric; internal characters limited to `A-Z a-z 0-9 space & ' ( ) + , . / : -` |
| `location_code` | integer | exactly `2840` |
| `language_code` | string | exactly `en` |
| `include_serp_info` | boolean | exactly `false` |
| `include_clickstream_data` | boolean | exactly `false` |

The provider task is `parameters` without `contract`. Request-body bytes are UTF-8
JCS of a singleton array containing that task, with no trailing newline. The exact
credential-free request is POST, HTTPS, host `api.dataforseo.com`, null port, path
`/v3/dataforseo_labs/google/keyword_overview/live`, empty query, the same five committed
application headers in the same order as the sandbox adapter, and the exact body reference.
Transport may add only the D9 Authorization, Host, and Content-Length headers.

The closed `policy` is:

    {"max_authorized_cost_micro_usd":20000,"mode":"paid_probe","policy_version":"dataforseo-paid-probe-v1","pricing_basis":"dataforseo-labs-google-live-2026-08-16"}

`max_authorized_cost_micro_usd` is an I-JSON integer and exactly 20,000. It records
[CHAZ]'s maximum authorization for the one exchange. It is not a provider-side billing
guarantee. `pricing_basis` records the dated official price schedule used when this
contract was authorized. A live run requires a fresh Steward price check and exact
`--authorize-max-micro-usd 20000` operator acknowledgement before Attempt creation.

The public paid CLI accepts no endpoint, task JSON, location, language, enrichment,
timeout, header, credential, retry, or alternate-ceiling argument. It rejects a store that
already contains a committed Attempt for this paid adapter before creating a new Attempt.
This is a single-process one-shot guard, not F7 concurrency proof.

After committed Capture read-back, no automatic envelope parsing or follow-up occurs.
Capture mode prints only `attempt_id` and `capture_id`. A separately invoked read-only
inspection mode may accept only an Evidence root and Capture ID, require a verified
complete Capture from this exact adapter, then emit its exact response-body bytes to
stdout. Inspection performs no network, mutation, normalization, summary, or persistence.
Provider cost, status, task IDs, messages, results, and nulls therefore remain raw
testimony rather than Outcomes or Observations.

Implementation and ordinary review use sentinel credentials plus mock/127.0.0.1 only.
The internal loopback seam accepts only
`http://127.0.0.1:<port>/v3/dataforseo_labs/google/keyword_overview/live` and is
unreachable from the public CLI. No real paid invocation is authorized until F6 is
satisfied and the Steward provides the exact operator command.

#### Planned Google Organic Live Advanced paid-probe adapter

PF-10 freezes a third exact event-version-2 adapter contract for later implementation:

    dataforseo-serp-google-organic-live-advanced-paid-probe-v1

This section is normative for PF-10 when that ticket is transitioned to `ready`. It does not
authorize a provider call. A real call remains separately gated by fresh provider contract
and pricing review, retention/privacy/terms/API-redistribution acceptance, bounded F6
off-host protection, and explicit [CHAZ] authorization.

Its provider is exactly `dataforseo`. Its production target is exactly one POST to
`https://api.dataforseo.com/v3/serp/google/organic/live/advanced`. The request contains
exactly one task. Redirects, retries, polling, task-post/task-get, account/catalog preflights,
and any automatic second exchange are forbidden. `load_async_ai_overview=true` is provider-
side work represented in this one Live POST response; it does not create Observatory
multi-exchange provenance.

The closed `parameters` object has exactly:

| Property | JSON type | Constraint |
|---|---|---|
| `contract` | string | exact adapter token above |
| `keyword` | string | closed natural-language grammar and operator denial below |
| `location_code` | integer | exactly `2840` |
| `language_code` | string | exactly `en` |
| `depth` | integer | exactly `100` |
| `device` | string | exactly `desktop` |
| `os` | string | exactly `windows` |
| `load_async_ai_overview` | boolean | exactly `true` |
| `group_organic_results` | boolean | exactly `true` |

`keyword` is 1..80 printable ASCII characters and at most 10 words, where a word is a
maximal nonempty run separated by ASCII space. It begins and ends with ASCII alphanumeric.
Internal characters are limited to `A-Z a-z 0-9 space & ' ( ) + , . / : -`.

After ASCII lowercasing, validation rejects the keyword before Attempt creation if it
contains any of these substrings anywhere:

    allinanchor: allintext: allintitle: allinurl: cache: define: definition:
    filetype: id: inanchor: info: intext: intitle: inurl: link: related: site:

The deny set is intentionally conservative. It is the adapter contract even where mutable
provider documentation lists a smaller set. A fresh provider review may stop the probe; it
may not silently widen the accepted keyword grammar. Changing the grammar requires an
amended adapter contract.

The provider task is `parameters` without `contract`. Request-body bytes are UTF-8 JCS of a
singleton array containing that task, with no trailing newline. The credential-free request
is HTTPS, host `api.dataforseo.com`, null port, exact path
`/v3/serp/google/organic/live/advanced`, method `POST`, empty query, and the same five
committed application headers in the same identity-bearing order as the accepted DataForSEO
HTTP-v2 adapters:

    [["accept","application/json"],["accept-encoding","identity"],
     ["connection","close"],["content-type","application/json"],
     ["user-agent","observatory-dataforseo-v1"]]

Transport may add only the accepted Authorization, Host, and Content-Length fields after a
verified Attempt capability is issued.

The closed `policy` is exactly:

    {"max_authorized_cost_micro_usd":30000,"mode":"paid_probe",
     "policy_version":"dataforseo-google-organic-live-paid-probe-v1",
     "pricing_basis":"dataforseo-google-organic-live-2026-08-18"}

The public capture path requires exact `--authorize-max-micro-usd 30000`. The one-shot guard
is keyed by this exact adapter token, not merely by `policy.mode`; Keyword Overview
paid-probe Evidence in the same store does not block this distinct adapter. No automatic
retry is allowed after Attempt creation.

The adapter-owned response-body ceiling is `33_554_432` bytes. Its adapter-owned timeout
profile is `httpx.Timeout(connect=30.0, read=120.0, write=30.0, pool=30.0)`. PF-09 may share
the streaming/client mechanics but neither value becomes an Observatory-wide default or a
public caller option.

`group_organic_results=true` is identity-bearing request context. Under the claimed provider
contract, related results are nested under their parent organic item. `false` would promote
them to separate organic items and can change result cardinality and later rank
interpretation, so it is a materially distinct future contract branch.

`depth=100` is requested provider parse depth. It is not a promise of 100 organic rows and
does not establish logical corpus completeness. A transport-complete response may contain
fewer organic rows plus heterogeneous SERP features. Any later Derivation must use
provider-returned counts/context from verified Evidence rather than infer completeness from
requested depth.

The event-v2 validator may add this exact Google Organic adapter branch. It must validate
request, parameters, policy, body equation, provider, and target for this token without
weakening the sandbox or Keyword Overview branches and without introducing a dynamic
registry. Existing event-v2 conformance bytes/IDs remain unchanged. Existing Derivations
skip this Evidence-only adapter until a separate Google Organic recipe is accepted.

The internal deterministic loopback seam, used only by tests, may replace scheme/host/port
with `http`, `127.0.0.1`, and an explicit test port while retaining the exact production
path. It is not reachable through the public CLI.

Explicit non-acquisition remains part of this contract: `group_organic_results=false`,
mobile/macOS/iOS, explicit `se_domain`, `search_param`/time-filtered context, depth 101..200,
PAA expansion, rectangles, target/stop-crawl, direct URL input/rewriting, and other optional
fields require separately authorized contract branches when their distinct testimony is
materially required.

#### Planned Search Mentions Live paid-probe adapter

AI-02 freezes a fourth exact event-version-2 adapter contract:

    dataforseo-ai-optimization-llm-mentions-search-mentions-live-paid-probe-v1

This section is normative for AI-02. It authorizes implementation of the guarded
Evidence-only adapter, not a provider call. Transport against the production host remains
separately gated by fresh contract and price confirmation, bounded F6 off-host protection,
the exact operator command, and explicit [CHAZ] authorization.

Its provider is exactly `dataforseo`. Its production target is exactly one POST to
`https://api.dataforseo.com/v3/ai_optimization/llm_mentions/search_mentions/live`.
The request contains exactly one task. Redirects, retries, polling, continuation,
account/catalog preflights, and any automatic second exchange are forbidden.

The closed `parameters` object has exactly:

| Property | JSON type | Constraint |
|---|---|---|
| `contract` | string | exact adapter token above |
| `target` | array | exactly one closed target object below |
| `location_code` | integer | exactly `2840`; boolean is not an integer |
| `language_code` | string | exactly `en` |
| `platform` | string | exactly `google` |
| `offset` | integer | exactly `0`; boolean is not an integer |
| `limit` | integer | exactly `5`; boolean is not an integer |

The one target object has exactly:

| Property | JSON type | Constraint |
|---|---|---|
| `keyword` | string | closed natural-language grammar below |
| `search_filter` | string | exactly `include` |
| `search_scope` | array | exactly `["answer"]` |
| `match_type` | string | exactly `word_match` |

The accepted key is `match_type`. A key with trailing whitespace, including
`"match_type "`, is unknown and rejected. Domain targets, `include_subdomains`, extra
target entries, missing or extra keys, multi-platform requests, filters, ordering, tags,
`search_after_token`, and any continuation form are rejected before Attempt creation.

`keyword` is 1..80 printable ASCII characters and at most 10 words, where a word is a
maximal nonempty run separated by ASCII space. It begins and ends with ASCII alphanumeric.
Internal characters are limited to `A-Z a-z 0-9 space & ' ( ) + , . / : -`. This adapter
does not inherit the Google Organic query-operator deny set. Changing this grammar requires
an amended adapter contract.

The provider task is `parameters` without `contract`. Request-body bytes are UTF-8 JCS of a
singleton array containing that task, with no trailing newline. The credential-free request
is HTTPS, host `api.dataforseo.com`, null port, the exact path above, method `POST`, empty
query, and the same five committed application headers in the same identity-bearing order
as the other accepted provider HTTP-v2 adapters:

    [["accept","application/json"],["accept-encoding","identity"],
     ["connection","close"],["content-type","application/json"],
     ["user-agent","observatory-dataforseo-v1"]]

Transport may add only the accepted Authorization, Host, and Content-Length fields after a
verified Attempt capability is issued.

The closed `policy` is exactly:

    {"max_authorized_cost_micro_usd":200000,"mode":"paid_probe",
     "policy_version":"dataforseo-ai-optimization-search-mentions-live-paid-probe-v1",
     "pricing_basis":"dataforseo-llm-mentions-live-2026-08-20"}

The public capture path requires exact `--authorize-max-micro-usd 200000`. The one-shot
guard is keyed by this exact adapter token. Existing Evidence for another accepted adapter
does not block it, and an unresolved Attempt for this adapter does. No automatic retry or
continuation is allowed after Attempt creation.

The adapter-owned response-body ceiling is `33_554_432` bytes. Its adapter-owned timeout
profile is `httpx.Timeout(connect=30.0, read=120.0, write=30.0, pool=30.0)`. The shared
streaming/client mechanics do not make either value a global default or caller option.

The event-v2 validator may add this exact fourth adapter as an explicit branch. It must
validate request, parameters, policy, body equation, provider, and target for this token
without weakening an existing branch and without introducing a dynamic registry. Every
existing event-v2 identity and conformance byte remains unchanged. Existing Derivation and
read/API dispatch remain fail-closed for this Evidence-only adapter until separate
authority accepts a recipe.

The internal deterministic loopback seam may replace only scheme, host, and port with
`http`, `127.0.0.1`, and an explicit test port while retaining the exact production path.
It and any body-limit override are private test seams, not public CLI options.

Credentials are nonempty environment inputs and may fail before Attempt creation.
Authorization is constructed and injected only after the verified one-shot capability is
issued. This adapter does not perform an account, balance, catalog, or User Data preflight.

Operator inspection is verify-on-read and read-only. It accepts only a complete Capture
for this adapter with a present nonempty body and writes those exact response bytes to
stdout. It does not parse, pretty-print, summarize, normalize, or mutate the testimony.

`limit=5` is bounded learning, not logical corpus completeness. A response that includes a
continuation token or reports more available results still produces at most one Capture
and no follow-up exchange. Provider status, task IDs, cost, counts, returned question and
answer text, sources, timestamps, and continuation testimony remain uninterpreted response
body bytes in AI-02.

#### Request fingerprint and Attempt version 2

The request object uses the shared closed `request` shape. Its constants and body are
selected by the exact adapter contract above; adapter contracts are never mixed.

The request-fingerprint document has exactly:

| Property | Constraint |
|---|---|
| `schema` | `observatory.request-fingerprint` |
| `version` | integer `2` |
| `provider` | `dataforseo` |
| `adapter_contract` | exact recognized event-v2 adapter token |
| `request` | closed request for that same adapter |

`request_fingerprint` is SHA-256(JCS(document)).

Attempt version 2 has exactly the version-1 top-level fields except
`prior_attempt_id` is not permitted; `version` is `2` and provider, adapter, request,
parameters, and policy follow the selected adapter section. `software` remains the closed
object containing only `observatory_version`. `attempt_id` remains
SHA-256(JCS(Attempt manifest)).
`prior_attempt_id` must not be overloaded to claim that a later request was constructed
from earlier response testimony. Standard/asynchronous provenance is deferred and may
require a later event version with an explicit source-Capture citation.

#### Response headers and body testimony

Response-body Evidence is the exact received entity bytes after HTTP transfer framing and
before content decoding. Chunk delimiters are not body bytes; gzip or other content-coded
bytes would be body bytes. This adapter requests `accept-encoding: identity`.

Response header names are lowercased; values are ISO-8859-1 round-trip strings from raw
header bytes. Pair order and duplicates are preserved among retained headers. Under
`header_policy = "http-headers-v1"`, these names are secret-class and their values are
never committed:

    api-key
    authentication-info
    authorization
    cookie
    proxy-authentication-info
    proxy-authorization
    set-cookie
    x-access-token
    x-api-key
    x-auth-token

For each omitted name, `omitted_headers` contains exactly one closed
`{"name": <lowercase-name>, "count": <positive-integer>}` object. Objects are sorted by
name; values, value hashes, and original positions are absent. A name cannot occur in both
`headers` and `omitted_headers`. Empty omission evidence is `[]`. The adapter contract
pins this policy, so a policy change requires a new adapter contract or event version.

The closed response object contains:

| Property | JSON type | Constraint |
|---|---|---|
| `status` | integer | 100..599 |
| `http_version` | string | `HTTP/1.0`, `HTTP/1.1`, or `HTTP/2` |
| `header_policy` | string | exactly `http-headers-v1` |
| `headers` | array | retained normalized pairs above |
| `omitted_headers` | array | closed omission objects above |
| `body` | object | shared closed `body_state` |
| `completeness` | string | `complete` or `partial` |

There is no final-URL or redirect-chain field. The committed request already identifies
the target and redirects are disabled.

#### Transport failure and Capture version 2

`transport_failure` is either null or the closed object `{"phase":...,"code":...}`. No
message, exception representation, URL, or provider body is permitted.

Phase enum:

    connect | send_request | receive_headers | receive_body

Code enum:

    timeout | connection_failed | write_failed | protocol_failed | read_failed

Cross-field rules reject nonsensical pairs: `connect` permits `timeout` or
`connection_failed`; `send_request` permits `timeout`, `connection_failed`, or
`write_failed`; `receive_headers` permits `timeout`, `connection_failed`,
`protocol_failed`, or `read_failed`; `receive_body` permits `timeout`,
`connection_failed`, `protocol_failed`, or `read_failed`.

Capture version 2 has the same top-level field names as Capture version 1, with `version=2`,
the provider/adapter/request rules above, and this section's response/failure objects.
There is no `url` or `final_url` field.

| `transport_state` | Response/timestamps | Failure |
|---|---|---|
| `response_complete` | non-null headers/body timestamps; response completeness `complete` | null |
| `response_partial` | non-null headers/body timestamps; response completeness `partial`; body present, zero or more bytes | non-null; phase `receive_body` |
| `no_response` | response and both response timestamps null | non-null; phase other than `receive_body` |

Timestamp ordering and Capture parent equality remain the version-1 rules. Status 4xx/5xx
is still `response_complete` when the body exchange completes. Provider-level status,
task IDs, cost, result arrays, and error messages remain raw body testimony; this event
version does not interpret them.

#### Construction and proof obligations

1. Validate parameters; construct and install exact request-body bytes.
2. Construct the credential-free request, fingerprint, and Attempt version 2.
3. Commit through D1–D4a and complete full D5 verify-on-read.
4. Only a capability issued after step 3 can reach HTTP transport.
5. Inject Basic Authorization from the two environment values; never mutate the committed
   request object or body.
6. Send with redirects disabled and `trust_env=False`.
7. Capture raw bounded HTTP testimony, apply the closed header-omission rule, then commit
   and verify Capture version 2.

Ordinary tests use no provider network. They must prove the structural gate, exact request
body, the closed sent-header equation, credential absence from all persisted/error
surfaces, complete/partial/no-response branches, and unknown-version failure. A
deterministic loopback test additionally proves on-wire request-body equality and a genuine
truncated-body partial response. It proves no TLS, HTTP/2, timeout realism, or provider
behavior.

PF-02 code acceptance uses deterministic tests. Steward closure additionally requires one
operator-run sandbox smoke by [CHAZ]: committed Attempt, real sandbox response committed as
Capture, both verify-on-read, and scrub succeeds. The smoke proves sandbox authentication,
reachability, one real response, Evidence commit, and scrub only. Sandbox data is dummy; it
does not prove production data, paid mode, rates, or error coverage.

#### HTTP-v2 conformance vector

All displayed bytes are UTF-8 with no trailing newline. Fixed inputs:
`authorized_at=2026-08-14T20:00:00.000000Z`,
`observatory_version=conformance-http-v2`, keyword `observatory test`,
`location_code=2840`, `language_code=en`, depth 10, desktop/windows, and nonce
`3333333333333333333333333333333333333333333333333333333333333333`.

Request body (119 bytes; SHA-256
`d10484d2237e4b08e37a4f3fe66bd678a3dbc2dab96f9b712af1b858b8d6d070`):

    [{"depth":10,"device":"desktop","keyword":"observatory test","language_code":"en","location_code":2840,"os":"windows"}]

Fingerprint preimage (612 bytes):

    {"adapter_contract":"dataforseo-serp-google-organic-live-advanced-sandbox-v1","provider":"dataforseo","request":{"body":{"body":{"bytes":119,"sha256":"d10484d2237e4b08e37a4f3fe66bd678a3dbc2dab96f9b712af1b858b8d6d070"},"state":"present_nonempty"},"headers":[["accept","application/json"],["accept-encoding","identity"],["connection","close"],["content-type","application/json"],["user-agent","observatory-dataforseo-v1"]],"host":"sandbox.dataforseo.com","method":"POST","path":"/v3/serp/google/organic/live/advanced","port":null,"query":[],"scheme":"https"},"schema":"observatory.request-fingerprint","version":2}

`request_fingerprint =
6b28e6d02fee14c8d8852889336baeb46bfa9918c5d4eee7b51e889f1823a2bb`.

Attempt preimage (1159 bytes):

    {"adapter_contract":"dataforseo-serp-google-organic-live-advanced-sandbox-v1","attempt_nonce":"3333333333333333333333333333333333333333333333333333333333333333","authorized_at":"2026-08-14T20:00:00.000000Z","parameters":{"contract":"dataforseo-serp-google-organic-live-advanced-sandbox-v1","depth":10,"device":"desktop","keyword":"observatory test","language_code":"en","location_code":2840,"os":"windows"},"policy":{"mode":"sandbox_no_spend","policy_version":"dataforseo-sandbox-v1"},"provider":"dataforseo","request":{"body":{"body":{"bytes":119,"sha256":"d10484d2237e4b08e37a4f3fe66bd678a3dbc2dab96f9b712af1b858b8d6d070"},"state":"present_nonempty"},"headers":[["accept","application/json"],["accept-encoding","identity"],["connection","close"],["content-type","application/json"],["user-agent","observatory-dataforseo-v1"]],"host":"sandbox.dataforseo.com","method":"POST","path":"/v3/serp/google/organic/live/advanced","port":null,"query":[],"scheme":"https"},"request_fingerprint":"6b28e6d02fee14c8d8852889336baeb46bfa9918c5d4eee7b51e889f1823a2bb","schema":"observatory.attempt-event","software":{"observatory_version":"conformance-http-v2"},"version":2}

`attempt_id =
22adc4841c86b7cd98b90bba683aeac204a0cb568428b590fd399e8627eb4640`.

Complete-response body (55 bytes; SHA-256
`a38a556da546f074db94ab0ea18cf557bdac6b44d637f414cc0d431a7c19a9b3`):

    {"status_code":20000,"status_message":"Ok.","tasks":[]}

Capture preimage (1482 bytes):

    {"adapter_contract":"dataforseo-serp-google-organic-live-advanced-sandbox-v1","attempt_id":"22adc4841c86b7cd98b90bba683aeac204a0cb568428b590fd399e8627eb4640","provider":"dataforseo","request":{"body":{"body":{"bytes":119,"sha256":"d10484d2237e4b08e37a4f3fe66bd678a3dbc2dab96f9b712af1b858b8d6d070"},"state":"present_nonempty"},"headers":[["accept","application/json"],["accept-encoding","identity"],["connection","close"],["content-type","application/json"],["user-agent","observatory-dataforseo-v1"]],"host":"sandbox.dataforseo.com","method":"POST","path":"/v3/serp/google/organic/live/advanced","port":null,"query":[],"scheme":"https"},"request_fingerprint":"6b28e6d02fee14c8d8852889336baeb46bfa9918c5d4eee7b51e889f1823a2bb","request_started_at":"2026-08-14T20:00:00.100000Z","response":{"body":{"body":{"bytes":55,"sha256":"a38a556da546f074db94ab0ea18cf557bdac6b44d637f414cc0d431a7c19a9b3"},"state":"present_nonempty"},"completeness":"complete","header_policy":"http-headers-v1","headers":[["content-type","application/json"],["x-request-id","sandbox-vector"]],"http_version":"HTTP/1.1","omitted_headers":[{"count":1,"name":"set-cookie"}],"status":200},"response_body_ended_at":"2026-08-14T20:00:00.300000Z","response_headers_at":"2026-08-14T20:00:00.200000Z","schema":"observatory.capture-event","software":{"observatory_version":"conformance-http-v2"},"transport_ended_at":"2026-08-14T20:00:00.400000Z","transport_failure":null,"transport_state":"response_complete","version":2}

`capture_id =
f347962c8dad05a762a19898898fff7ed60b7c06270b61dc3d7a158fa0d396b7`.

The omission marker states that one `set-cookie` field was received; its value is
deliberately not part of the vector or Evidence. Version-2 branch tests for partial and
no-response use the closed rules above; this published complete vector fixes the shared
request, omission, status, HTTP-version, body, and identity semantics.

#### Paid-probe conformance vector

This vector fixes the second adapter without changing any published sandbox byte or ID.
Inputs: authorized time `2026-08-16T16:00:00.000000Z`, nonce = 64 `4` characters,
software `conformance-paid-probe-v1`, and keywords in this exact order:
`seo api`, `keyword research`, `local seo`,
`generative engine optimization`, `ai search optimization`.

Request body (216 bytes):

    [{"include_clickstream_data":false,"include_serp_info":false,"keywords":["seo api","keyword research","local seo","generative engine optimization","ai search optimization"],"language_code":"en","location_code":2840}]

| Vector | Bytes | SHA-256 |
|---|---:|---|
| request body | 216 | `3fc7205a55a1a5c464c0ae4ebca21a1e3088c2022565929a670fdf757ab7987b` |
| request-fingerprint preimage | 622 | `6cc5765911abe752a974d2fba268d927fdc055147c1286fffdfe0ee585cdc610` |
| Attempt preimage | 1367 | `89904bf8a6812fb3d0d845310e4705962bb4db928b80da3be67342dff5def185` |
| sample response body `{"cost":0.0126,"tasks":[]}` | 26 | `5b69c7675c3f03d95bb5071bf0da855e3a476521939dccd757d3295746cd33d1` |
| complete Capture preimage | 1433 | `dbaaf68a38e54e39d4fc03807d72eda37f8efd9a212220c0a99d270ddcec6917` |

The sample Capture uses HTTP 200/1.1, retained
`[["content-type","application/json"]]`, no omitted headers, timestamps at
`.100000Z`, `.200000Z`, `.300000Z`, and `.400000Z` in request/header/body/end
order, and the Attempt/software values above. Tests must recompute these bytes and IDs
independently of production constructors.


---

## Normative construction order

For a successful fixture capture that yields a Capture:

1. Validate and freeze `parameters` (closed fixture request document).
2. `request_body_bytes` = UTF-8 RFC 8785/JCS(`parameters`) with no trailing newline.
3. Install and verify the content-addressed body object for `request_body_bytes`; build
   `body_state` = `present_nonempty` + `body_ref`.
4. Build closed `request` with fixture constants and that `body_state`.
5. Build closed `request-fingerprint` document from `provider`, `adapter_contract`, and
   `request`; JCS-serialize; `request_fingerprint` = SHA-256 of those bytes.
6. Generate `attempt_nonce` as 256-bit value encoded as lowercase 64-hex; build closed
   Attempt manifest (omit `prior_attempt_id` when absent); JCS-serialize;
   `attempt_id` = SHA-256 of those bytes; persist; `COMMITTED` last; verify.
7. Only after Attempt is committed and verified: run fixture transport for
   `parameters.scenario` using §Fixture response-construction algorithm (zero choices).
8. Install response body object when body present; build closed Capture per branch rules;
   JCS-serialize; `capture_id` = SHA-256 of those bytes; persist; `COMMITTED` last; verify.

**Verification order** remains §Canonicalization and verify-on-read (hash stored bytes
before trusting parse).

---

## Fixture response-construction algorithm

**Inputs:** validated `parameters` = (`contract`, `panel_id`, `subject_key`, `depth`,
`scenario`).
**Outputs:** Capture `transport_state`, `response` or null, `transport_failure` or null,
exact response body bytes when present, and the expected Capture-based classification and
Observation count.

Let `P = panel_id`, `S = subject_key`, `D = depth`.

### Helper objects (JCS-serialized when used as body bytes)

**`admitted_results_body(P, S, D)`** — closed object:

| Property | Value |
|---|---|
| `contract` | `fixture-panel-v1` |
| `panel_id` | `P` |
| `subject_key` | `S` |
| `status` | `ok` |
| `result_count` | `D` |
| `results` | array of length `D`; for `i` in `1..D` exactly: `result_index=i`, `subject_key=S`, `label="fixture-result-"+decimal(i)`, `score=1000-i` (JSON integers; labels ASCII) |

**`admitted_empty_body(P, S)`** — closed object:

| Property | Value |
|---|---|
| `contract` | `fixture-panel-v1` |
| `panel_id` | `P` |
| `subject_key` | `S` |
| `status` | `ok` |
| `result_count` | `0` |
| `results` | `[]` |

**`refusal_body(P, S)`** — closed object with exactly:
`contract="fixture-panel-v1"`, `panel_id=P`, `subject_key=S`, `status=refused`,
`code=fixture_refusal`.

**`failure_body(P, S)`** — closed object with exactly:
`contract="fixture-panel-v1"`, `panel_id=P`, `subject_key=S`, `status=failed`,
`code=fixture_failure`.

**`alt_subject_key(S)`:** if `S == "other-subject"` then `"other-subject-2"`, else
`"other-subject"`. Always a valid `subject_key` string and always ≠ `S`.

**`extra_subject_body(P, S)`** — closed object with exactly:
`contract="fixture-panel-v1"`, `status=ok`, `panel_id=P`, `subject_key=S`,
`result_count=1`, `results=[{"label":"fixture-result-1","result_index":1,"score":999,"subject_key": alt_subject_key(S)}]`.
Admission rejects this body because the result `subject_key` differs from the requested
`S`, not because `contract` is missing.

**`too_many_results_body(P, S, D)`** — like `admitted_results_body` but with `N = D + 1`
results and `result_count = N` (indexes `1..N`, `score=1000-i`, `label=fixture-result-i`,
`subject_key=S`).

**`malformed_bytes`:** exact UTF-8 (not valid JSON), single line, no trailing newline, ends with a comma:

```text
{"contract":"fixture-panel-v1","status":"ok",
```

The line above is exactly 45 bytes: `7b22636f6e7472616374223a22666978747572652d70616e656c2d7631222c22737461747573223a226f6b222c`.
Implementations must use those 45 bytes only—not a trailing newline after the comma.

**Headers:**
`H_json = [["content-type","application/json"]]`
`H_plain = [["content-type","text/plain"]]`

### Per-scenario construction (normative; no alternatives)

| scenario | transport_state | response.headers | response.completeness | response.body bytes | transport_failure | classification | Observation count |
|---|---|---|---|---|---|---|---|
| `admitted_results` | `response_complete` | `H_json` | `complete` | JCS(`admitted_results_body(P,S,D)`) | `null` | `observation_admitted` | `D` |
| `admitted_empty` | `response_complete` | `H_json` | `complete` | JCS(`admitted_empty_body(P,S)`) | `null` | `observation_admitted_empty` | `0` |
| `provider_refusal` | `response_complete` | `H_json` | `complete` | JCS(`refusal_body(P,S)`) | `null` | `provider_refusal` | `0` |
| `provider_failure` | `response_complete` | `H_json` | `complete` | JCS(`failure_body(P,S)`) | `null` | `provider_failure` | `0` |
| `malformed_response` | `response_complete` | `H_json` | `complete` | `malformed_bytes` | `null` | `transport_complete_non_admissible` | `0` |
| `wrong_media_type` | `response_complete` | `H_plain` | `complete` | JCS(`admitted_empty_body(P,S)`) *(same body as empty success for these parameters)* | `null` | `transport_complete_non_admissible` | `0` |
| `response_partial` | `response_partial` | `H_json` | `partial` | first **32** UTF-8 bytes of JCS(`admitted_results_body(P,S,D)`) | `null` | `response_partial` | `0` |
| `no_response` | `no_response` | *(no response)* | *(n/a)* | *(none)* | `{"code":"fixture_no_response","phase":"receive_response"}` | `no_response` | `0` |
| `extra_subject` | `response_complete` | `H_json` | `complete` | JCS(`extra_subject_body(P,S)`) | `null` | `admission_rejected` | `0` |
| `too_many_results` | `response_complete` | `H_json` | `complete` | JCS(`too_many_results_body(P,S,D)`) | `null` | `admission_rejected` | `0` |

For every row with a response body: `body_state` is `present_nonempty` with matching
digest/size. For `no_response`: `response` is JSON `null` and no response body file.

**Identity agreement:** every structured success/refusal/failure body that is not
`extra_subject` sets top-level `panel_id=P` and `subject_key=S` from the request.
`admitted_results` results use `subject_key=S`. `extra_subject` uses `alt_subject_key(S)`
on the result only.

**Admission for `status=ok` structured bodies:** require contract match; top-level
`panel_id`/`subject_key` equal request; `result_count == len(results)`;
`0 <= result_count <= depth`; indexes unique contiguous `1..result_count`; every result
`subject_key` equals request `S`; full accounting. Else `admission_rejected`.

These classifications hold for **every** valid `(P,S,D)`, not only the published vectors.

Every verified Attempt also yields Attempt-stage Outcome `authorized_unresolved`
(`capture_id` NULL) under the derivation version.

---

## Commit visibility

Evidence only after verified manifest + bodies + `COMMITTED`. Journal ≠ Evidence. Fixture
journal skip only when full in-process result retained before Capture construction.

### Durability profile `local-posix-fsync-v1`

Normative. One durability module implements this; nothing else writes into the Evidence
root. Steps are ordered; an implementation must not reorder them.

**Scope of the claim.** This protocol is defined against a single local POSIX filesystem
that honours `fsync` and provides atomic `link(2)` within that filesystem. It does not claim
protection against hardware that acknowledges `fsync` without persisting, filesystems
lacking those guarantees, or writes spanning two filesystems.

**Concurrency.** One writer at a time; multi-process writer safety is deferred (F7). Readers
of a **quiescent** store are supported; a reader racing an active writer is not, and D4a
says why. A reader never observes a partially written file, because D1 installs only
complete files, and never observes a partial bundle as Evidence, because `COMMITTED` is
installed last.

Tests prove the protocol, not the hardware.

#### D1 — Durable file materialization

Every file entering the store is materialized identically:

1. Create a uniquely named file under `.tmp/` and write its complete bytes.
2. `fsync` that file descriptor, then close it.
3. Install it at its final path by `link(2)` from the temporary path. `link(2)` fails with
   `EEXIST` if the target exists; this is the required exclusive no-overwrite install.
   `rename(2)` **must not** be used to install, because it silently replaces.
4. `unlink` the temporary path.
5. `fsync` the directory containing the final path.

A partially written file therefore never occupies a final path, and no install can
overwrite.

On `EEXIST` at step 3, unlink the temporary path first, then apply D3.

**`.tmp/` is scratch, never Evidence.** Step 4's `unlink` is deliberately not made durable —
`.tmp/` is not `fsync`ed here, because the cost buys nothing. A crash between steps 3 and 4
may therefore leave a temporary name after recovery, so the installed file can show link
count 2 until cleanup. Opening a store purges `.tmp/` — after `FORMAT.json` validation, per
D7 — restoring link count 1. The link-count-1 requirement in D4 is therefore asserted of
bundle body files **after** a store open, and `.tmp/` residue is expected interruption
debris, not corruption.

#### D2 — Durable directory creation

Directories are created parent-first. After each newly created directory, `fsync` its
parent. A directory must be durable before any child is installed within it.

Two kinds of directory, with different existence rules:

- **Shared path directories** — pool shards, fingerprint shards, date components, capture
  shards. Many events share these and they recur constantly. Creation is idempotent:
  already existing is success, and only a newly created directory requires the parent
  `fsync`.
- **Terminal event bundle directories** — the directory named by `attempt_id` or
  `capture_id`. Created **exclusively**; `EEXIST` is an anomaly under D3.

#### D3 — `EEXIST` handling differs by kind

- **Object pool files** (`objects/sha256/...`): paths are content-addressed, so recurrence
  is normal. Read the existing object, verify its byte length and SHA-256 against the
  expected values, and accept it on match. On mismatch, fail closed as store corruption.
  Never overwrite, never truncate, never trust the path without verifying the content.
- **Shared path directories** (D2): already existing is success, not an anomaly.
- **Terminal event bundle directories, manifests, bundle body files, and `COMMITTED`**:
  `EEXIST` is an anomaly. Fail closed. Event identities are digest-derived and Attempts
  carry a fresh nonce, so a collision indicates corruption or a defect, never ordinary
  recurrence.

#### D4 — Bundle commit order

A bundle is built at its final path, not staged and moved. An incomplete bundle is not
Evidence because `COMMITTED` is absent — that is the mechanism.

1. Create the shared path directories, then the terminal bundle directory, per D2.
2. Install the manifest (`attempt.json` / `capture.json`) per D1.
3. Install body files per D1, when present. Materialize by independent copy or COW reflink
   from the pool object. **Ordinary hardlinks from a bundle into the object pool are
   forbidden**: a bundle body file must not share an inode with its pool object, and must
   have link count 1 once `.tmp/` has been purged.
4. Install `COMMITTED` per D1, content exactly `<event_id>\n`. This is always last.

No separate bundle-directory `fsync` step is required. D1 step 5 already `fsync`s the
containing directory after every install, so the manifest and bodies are durable before
`COMMITTED` is linked, and `COMMITTED` is durable when its own D1 completes.

**Which bundle holds which body.** The Attempt bundle contains `request.body` when the
request carries one. The Capture bundle contains `response.body` when the response carries
one. Neither contains the other's: the Attempt is committed before transport and cannot
hold a response, and the Capture cites its parent `attempt_id`, so duplicating
`request.body` would store identical bytes twice without adding recoverability.

#### D4a — Commit completion and concurrency

A commit is complete only when `COMMITTED`'s D1 has fully finished — `link`, temporary
unlink, and directory `fsync` — **and** D5 verification has passed. Only then is the event
Evidence, and only then may the writer report success. Nothing before that point is
Evidence, consistent with `VOCABULARY.md`, which defines Attempt and Capture as durably
committed.

**Concurrency scope.** One writer, plus readers of a **quiescent** store. A reader racing an
active writer is out of scope: CE-03 does not support it, and coordinating the two waits
until the service actually needs it, alongside multi-process writer safety (F7).

**After an interruption**, whatever survives on disk is judged by D6 alone. There is no
separate record of writer intent, and none is needed, because of D4's ordering: D1 makes the
manifest and every body file durable *before* `COMMITTED` is linked. Therefore a surviving
`COMMITTED` implies durable, complete content, and D6's predicate is sound.

The two interruption outcomes are both safe:

- `COMMITTED` did not survive — the bundle is uncommitted and D6 ignores it. An
  unacknowledged commit is lost, which is the intended failure direction.
- `COMMITTED` survived — the content behind it is durable and complete by the ordering
  above, so D5 either verifies it or reports an integrity failure.

The protocol may lose an unacknowledged commit. It can never present a partial bundle as
Evidence.

#### D5 — Verify after commit

Before the caller may rely on a committed event, read it back from disk and run the full
**Verify-on-read** sequence in §Canonicalization and verify-on-read — all six steps, not a
reduced form: stored manifest bytes; SHA-256 equal to the directory and `COMMITTED`
identity; schema validation with re-JCS of the parsed value equal to the stored bytes;
cross-field rules; every cited body digest and size; fail closed on any mismatch with no
silent repair.

In addition, confirm `COMMITTED` content equals `<event_id>\n` exactly.

**Bodies are verified in both locations.** The pool object and the bundle's independently
materialized body file are separate copies on disk and can rot independently, so each is
verified against the cited digest and length. Verifying one leaves the other unproven.

A commit that cannot be verified is a failure, not a success with a warning.

#### D6 — Reading

A bundle directory without `COMMITTED` is **ignored** — not Evidence, and not an error. It
is the expected residue of an interrupted commit. A bundle with `COMMITTED` that fails D5
verification is an integrity failure and must be reported as one, never silently skipped.

Discovery-based verification and scrub prove the integrity of commitment-claiming
directories they find. They do **not** prove historical completeness: deleting an entire
bundle directory together with its `COMMITTED` marker removes the discovery claim and is
therefore invisible to scrub. A clean scrub must never be represented as proof that no
committed event is missing. Off-host restore acceptance uses an independently recorded
sorted Attempt/Capture ID inventory and exact set comparison under F6.

#### D7 — `FORMAT.json`

Written once at store creation per D1, followed by `fsync` of the Evidence root.

Opening is strictly ordered, because the store must be **recognised before it is touched**:

1. Read `FORMAT.json` and require exact canonical bytes and matching digest. Missing,
   malformed, noncanonical, unsupported, or conflicting content fails closed here, with
   nothing modified.
2. Only once the root is confirmed to be an Observatory Evidence Store, purge its `.tmp/`
   per D1.
3. Proceed with Evidence operations.

Purging before validation would let a mistaken or misidentified path be mutated — unrelated
files under some other directory's `.tmp/` could be destroyed before the open failed.

#### D8 — No transport before durable Attempt

Fixture or provider transport must not begin until the Attempt has completed D4 and passed
D5. This ordering is structural, not advisory: the transport call must be unreachable from
any path that has not first obtained a verified committed Attempt.

Pure deterministic calculation of bytes prescribed by a fixture conformance algorithm is
not, by itself, a transport call: it performs no acquisition and cannot create Evidence.
Any service path that adopts calculated bytes as transport testimony or commits a Capture
remains subject to the structural gate above. Importability of a pure conformance helper
does not authorize transport or Evidence creation.

---

## Rebuildable PostgreSQL / entrypoints / API

`derivation_versions`, `outcomes`, `observations`; capture/derive/status/scrub CLIs;
`GET /v1/health`, `GET /v1/attempts/{attempt_id}`; loopback; no auth; 409
`evidence_integrity_failure` on failed verify-on-read. Observation natural identity
`(capture_id, derivation_version_id, within_capture_result_id)` with
`within_capture_result_id = "result:"` + decimal index; provider `fixture`.

### Current provider schema and read-surface pointer

The accepted Keyword Overview, Google Organic, and Search Mentions implementations add
rebuildable provider relations without changing the Evidence boundary. Shared relations are
`provider_recipes`, `provider_recipe_selections`, `observation_envelopes`, and
`derivation_diagnostics`. Keyword Overview typed details are
`keyword_overview_coverage`, `keyword_overview_metrics`,
`keyword_overview_monthly_search_volume`, `keyword_overview_search_volume_trend`,
`keyword_overview_properties`, `keyword_overview_avg_backlinks`, and
`keyword_overview_search_intent`. Google Organic uses
`google_organic_result_context`, `google_organic_serp_features`,
`google_organic_ranked_results`, `google_organic_aio_presence`,
`google_organic_aio_sources`, `google_organic_aio_source_occurrences`,
`google_organic_related_questions`,
`google_organic_related_question_occurrences`, and
`google_organic_related_queries`. Search Mentions uses
`search_mentions_result_context`, `search_mentions_items`,
`search_mentions_item_occurrences`, `search_mentions_monthly_search_volume`,
`search_mentions_monthly_occurrences`, `search_mentions_sources`, and
`search_mentions_source_occurrences`. Their closed recipes and accepted semantics remain
authoritative through the registered canonical recipe bytes, PF-04 through PF-15 acceptance
records, and AI-02 through AI-06 Search Mentions acceptance records; this paragraph is a
discovery pointer, not a duplicate schema.

The canonical versioned resource namespace is `/v1`. Current provider reads are
`GET /v1/attempts/{attempt_id}`,
`GET /v1/providers/dataforseo/google/keyword-overview/history`, and
`GET /v1/providers/dataforseo/google/organic/history`, and
`GET /v1/providers/dataforseo/google/ai-optimization/search-mentions/history`.
Development documentation is served at `/api/v1/docs` with OpenAPI at
`/api/v1/openapi.json`; those documentation locations do not create a second `/api/v1`
resource namespace or a compatibility mount. The API remains read-only, loopback-only, and
unauthenticated until the recorded deferred triggers fire.

For fixture v1, `derivation_version_id` is an operator-supplied semantic label matching
`[A-Za-z0-9._+:-]{1,128}`. It is the immutable identity of one derivation meaning under
its registered `adapter_contract`; changing derivation behavior requires a new label.
Registering an absent label creates it. Reusing a label is permitted only when its
immutable registration metadata agrees exactly. A conflicting `adapter_contract` fails
closed before any Outcome or Observation write and never mutates the existing registration.
A content-addressed derivation-recipe document is not part of fixture v1.

### Provider Derivation after F11

D11 authorizes provider-specific Derivation only on a provider-capable rebuildable
substrate. It does not change event version 2, store format 2, Attempt/Capture identities,
body Evidence, or D10's statement that the paid probe itself performed no automatic
normalization. The already-committed PF-03 Capture may later be interpreted by a separately
invoked, versioned Derivation.

#### Provider recipe identity

For a provider Derivation, the exact `derivation_version_id` is lowercase
`sha256(JCS(recipe))`, represented as 64 lowercase hex characters. The recipe is a closed
I-JSON document whose semantic content fixes at least:

- the exact `provider` and `adapter_contract`;
- provider-envelope/parser contract version;
- request/result reconciliation and Observation identity rules;
- admission and Capture-stage Outcome rules;
- numeric normalization rules;
- Provider Update Time and Data Period rules;
- field-state rules for nullable/optional/request-disabled facts;
- the emitted Observation kinds and their kind versions;
- object-level extension policy and fail-closed drift rules.

A human-readable recipe name may be registered as metadata but does not participate in
identity. Repository software/build version is execution provenance and does not, by
itself, change recipe identity. If any semantic rule above changes, the canonical recipe
bytes and digest must change.

Registration of a provider recipe stores or otherwise makes its exact canonical bytes
available to rebuildable PostgreSQL and verifies that an existing digest has identical
bytes and adapter metadata. A hash/byte or adapter conflict fails before derived writes.
Fixture-v1 registration remains governed by the preceding section.

#### Provider JSON parsing and drift

Provider body parsing is independent from the fixture admission parser. It starts only
after the referenced Attempt/Capture/body pass Evidence verify-on-read.

The parser MUST:

- decode UTF-8 strictly;
- reject duplicate JSON object member names;
- reject non-finite numeric constants;
- avoid binary-float normalization of decimal-capable provider values; structural JSON
  integers may remain integers, while known decimal-capable fields accept integer or
  decimal lexical forms and normalize exactly to a decimal representation;
- validate required known paths, types, counts, timestamps, periods, and closed enum
  values according to the recipe;
- distinguish provider execution-duration strings from provider data/update timestamps.

Each known object in the recipe is either closed or extension-permitted. An unknown field
on a closed object is drift. An unknown additive field on an extension-permitted object is
tolerated for the known mapping but produces a rebuildable Derivation diagnostic identified
by stable code plus JSON Pointer path. Tolerated extensions are not Observations and do not
alter raw Evidence.

Malformed JSON/UTF-8, duplicate members, missing or wrong-typed required known fields,
malformed provider timestamps/periods, impossible declared counts, unknown values of a
closed enum, and other recipe-declared semantic drift produce no normal provider
Observations from that Capture. A well-formed provider-level failure inside an HTTP-complete
Capture is a provider Outcome, not schema drift.

#### Request/result reconciliation and provider identity

The verified Attempt, not a provider request echo, is request authority. For the first
Keyword Overview recipe, the exact requested keyword string is the Observatory subject.
The exact returned keyword string is preserved as provider testimony. Result/task/item
array position is never a subject identity.

A recipe may define a provider-specific normalization function solely for reconciliation.
For admitted data, reconciliation from exact requested subjects to returned items must be
unambiguous. If two requested subjects normalize to one provider key and the response does
not supply an unambiguous mapping, the affected Capture fails reconciliation. Duplicate or
unrequested returned items likewise fail reconciliation for the first recipe rather than
being silently assigned. A requested keyword omitted under a provider contract that
documents omission as “no provider data for that keyword” may yield a typed provider-
coverage Observation keyed by the exact requested keyword.

Filesystem traversal order, request-array order, provider result order, and provider task
echo order are never Observation identities.

#### Accepted Google Organic AIO optionality

For the current Google Organic recipe, an AI Overview item's top-level `references` and
`items` members are required arrays; either missing or JSON null fails parsing closed. For
an `ai_overview_element` inside `items`, an absent `references` member and a JSON-null
`references` member are intentionally interpreted alike: neither emits element-locus AIO
source occurrences, and neither establishes an absence Observation. The exact distinction
remains recoverable from raw Evidence. Aligning or otherwise changing that asymmetry is a
recipe-semantic change and therefore requires new canonical recipe bytes and a new
`derivation_version_id`.

#### Provider Observation envelope and typed details

The provider-capable rebuildable substrate has one generic Observation envelope and typed
Observation-kind detail relations. The envelope carries at least:

- verified `attempt_id` and `capture_id` provenance;
- provider `derivation_version_id` (recipe digest);
- `provider` and `adapter_contract`;
- recipe-declared `observation_kind`;
- a deterministic within-Capture Observation identity derived from semantic identity axes,
  never provider array position.

The current physical `observations` table remains the accepted fixture-v1 representation
during the first additive provider tickets and MUST NOT be widened with provider-specific
nullable columns. The new envelope is the canonical direction for provider-capable
Observations. Migrating fixture values into that envelope, if later useful, is a separate
bounded rebuildable migration and must preserve fixture-v1 semantic identities/API behavior.

Provider-specific values live in typed detail relations. Decimal-capable values are stored
exactly (for PostgreSQL, a decimal/`NUMERIC` representation), and values never participate
in content identity. Where a field can carry materially different testimony, its state is
modeled at that field/fact, not once for the whole provider item. The first provider state
vocabulary distinguishes at least:

- stated value (including legitimate numeric zero and stated empty arrays);
- provider JSON null;
- permitted provider-unstated/absent field;
- not requested, proven from the verified Attempt parameters;
- recipe-defined inapplicable.

Malformed or wrong-typed fields are Derivation/admission failures, not value states.

#### Provider time and period

Three axes are independent:

1. **Capture/acquisition time** — Observatory transport provenance from the verified
   Capture. It may be exposed with an Observation without being treated as provider data
   time.
2. **Provider Update Time** — parsed only from the exact provider structure whose recipe
   states that the timestamp governs. A sibling structure's timestamp is never inherited.
3. **Data Period** — an independent period such as historical `(year, month)`.

An Observation may have both Provider Update Time and Data Period. If either is not stated
for the fact, it remains explicitly unstated. Capture time never fills either gap.

#### Provider Outcome and write behavior

Provider Attempt-stage Outcome remains `authorized_unresolved` while the verified Attempt
has no derived Capture-stage meaning. The first provider recipe may use the existing generic
transport classifications `no_response`, `response_partial`, and
`transport_complete_non_admissible`, plus provider-specific closed classifications for a
well-formed provider-level error, envelope/schema rejection, request/result reconciliation
failure, and successful admission. Provider classifications such as search intent or
competition level are Observation values, never Observatory Outcomes.

All derived rows/diagnostics for one admitted provider Capture are written atomically as a
Capture unit. Re-running the same recipe against the same verified Evidence is idempotent
only when every existing row under the same natural identity equals the newly intended
content. A mismatch fails closed; provider code MUST NOT use conflict-ignore behavior to
mask divergent intended rows.

#### PF-03 conformance fixture and ordinary tests

Before the first provider parser is accepted, the exact verified PF-03 response body is
read through the existing read-only inspector, its byte length and SHA-256 are recorded,
and those exact bytes are copied into the deterministic test corpus. Ordinary tests never
read the operator Evidence root and never perform provider network activity.

The frozen response is a conformance input, not new Evidence authority. Tests pair it with
expected typed interpretation and bounded mutations covering at least item reordering,
duplicate JSON keys, non-finite numbers, integer/decimal lexical variation, missing/extra/
duplicate result items, count mismatch, malformed timestamps/periods, provider task error,
field null/absence/request-disabled cases, and additive fields on extension-permitted
objects.

Later separately authorized real API calls may create new Evidence that is run through the
same parser as a contract probe. Live provider access is never a dependency of ordinary
tests.

#### Provider contract discovery and conformance

D12 separates three artifacts that must not be conflated. Current official provider
documentation is the provider's claimed contract. A verified Attempt/Capture/body is
empirical Evidence of one exact exchange. The content-addressed Derivation Recipe is
Observatory's normative interpretation contract for an adapter: it states what known
semantics are accepted, which additive extensions are tolerated and diagnosed, which
observed provider quirks are deliberately preserved, which states are proven request-disabled,
and which divergences fail closed as drift.

Before a new adapter contract is accepted, the Steward reviews the relevant capability
family only far enough to identify the named analytical purpose, request options, historical
dimensions, overlap/cost, and materially different response contracts. Inventory does not
authorize transport. A Provider contract probe is a separately authorized ordinary
Attempt → Capture exchange. Probe selection is branch-oriented rather than statistical: a
new probe is warranted only when an unexercised mode can materially change envelope or
cardinality, reconciliation/identity, field-state, numeric/time/data-period semantics,
pagination/continuation, or failure taxonomy. A materially different path, live/standard/
asynchronous workflow, pagination model, or option set is a different adapter contract.

The probe set is sufficient when every material mode for the authorized adapter is either
represented by verified Evidence, proven request-disabled by the verified Attempt, or
explicitly deferred with a reason. One observed value never proves non-nullability,
ordering, omission, update cadence, or other invariance. Synthetic adversarial fixtures
remain required for closed rules that a bounded real corpus cannot economically exhibit.

Exact verified probe bytes may be copied to the deterministic test corpus as Conformance
fixtures with byte length and SHA-256 recorded. Those bytes test a recipe/parser; they do
not become a second Evidence authority or silently define the external provider contract.
Provider drift is resolved through the recipe/version rules in D11, never by silently
re-freezing a fixture under unchanged semantics.

Raw Evidence makes under-modeling reversible but cannot repair under-acquisition. When a
known option or surface contains materially useful time-indexed testimony that may be
irrecoverable later and the project deliberately does not acquire it, the activation review
records the non-acquisition and a trigger for reconsideration. This is a bounded decision,
not authorization for speculative catalog-wide collection.

PF-03 is the accepted reconnaissance Capture for
`dataforseo-labs-google-keyword-overview-live-paid-probe-v1`: one live task, United States,
English, SERP enrichment off, and clickstream off. PF-05 may design the first Keyword
Overview parser/typed IR from that verified Evidence plus the claimed provider contract and
bounded synthetic adversarial cases. PF-03 does not establish contracts for SERP enrichment,
clickstream, Standard/asynchronous workflows, or other DataForSEO endpoints, and PF-05 must
not issue additional provider calls to fill those gaps.

#### Provider API sequencing

`GET /v1/attempts/{attempt_id}` remains an Evidence-backed audit/provenance resource. Before
provider-derived values are exposed, the API must support adapter-appropriate recipe
selection rather than applying one process-global `derivation_version_id` to every adapter,
and prior provider recipe versions must remain addressable.

The first consumer-facing Keyword Overview history resource stays provider/surface explicit
and exposes provenance, recipe identity, exact request/returned subject context, independent
time/period semantics, and field states. A generic cross-provider metric or generic
strategy-facing Observation query is not authorized by this section; F10 projections and
the downstream Strategy layer remain the places to generalize after real consumers prove a
common shape.

---

## Conformance vectors

All documents: single-line JCS UTF-8, **no trailing newline**. Digests recomputed from
displayed bytes. Three independent Attempts (distinct nonces); one Capture each; scenario
matches Capture.

Shared fixed inputs: `authorized_at=2026-08-11T20:15:30.123456Z`,
`observatory_version=conformance-v1`, `panel_id=panel-alpha`, `subject_key=subject-one`,
`depth=2`, capture start `2026-08-11T20:15:30.200000Z`, headers time
`2026-08-11T20:15:30.900000Z`, transport end `2026-08-11T20:15:31.000000Z`.

### Set AR — `admitted_results` (nonce `0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef`)

#### V0-AR request body

```text
{"contract":"fixture-panel-v1","depth":2,"panel_id":"panel-alpha","scenario":"admitted_results","subject_key":"subject-one"}
```

| Field | Value |
|---|---|
| Trailing newline | absent |
| Byte length | `124` |
| SHA-256 | `f16972cae6bea7a84acc0c6d0b181a2de3fabf7870663b1fb76f389aed4c38ec` |

#### V1-AR fingerprint preimage

```text
{"adapter_contract":"fixture-panel-v1","provider":"fixture","request":{"body":{"body":{"bytes":124,"sha256":"f16972cae6bea7a84acc0c6d0b181a2de3fabf7870663b1fb76f389aed4c38ec"},"state":"present_nonempty"},"headers":[["content-type","application/json"]],"host":"fixture-panel","method":"POST","path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},"schema":"observatory.request-fingerprint","version":1}
```

| Field | Value |
|---|---|
| Trailing newline | absent |
| `request_fingerprint` | `d18682cc029a8db08b0b761b900db2c7c91f92a99087597281cbdbdaec70e88b` |

#### V2-AR Attempt

```text
{"adapter_contract":"fixture-panel-v1","attempt_nonce":"0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef","authorized_at":"2026-08-11T20:15:30.123456Z","parameters":{"contract":"fixture-panel-v1","depth":2,"panel_id":"panel-alpha","scenario":"admitted_results","subject_key":"subject-one"},"policy":{"mode":"fixture_no_spend","policy_version":"fixture-v1"},"provider":"fixture","request":{"body":{"body":{"bytes":124,"sha256":"f16972cae6bea7a84acc0c6d0b181a2de3fabf7870663b1fb76f389aed4c38ec"},"state":"present_nonempty"},"headers":[["content-type","application/json"]],"host":"fixture-panel","method":"POST","path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},"request_fingerprint":"d18682cc029a8db08b0b761b900db2c7c91f92a99087597281cbdbdaec70e88b","schema":"observatory.attempt-event","software":{"observatory_version":"conformance-v1"},"version":1}
```

| Field | Value |
|---|---|
| Trailing newline | absent |
| `attempt_id` | `46d5fb97c109b9f64a42ff3a5e62978e2c25551d6b7274603fc88456acfd9a0f` |

#### V3 Capture `response_complete` (body end `2026-08-11T20:15:30.950000Z`)

Response body JCS:

```text
{"contract":"fixture-panel-v1","panel_id":"panel-alpha","result_count":2,"results":[{"label":"fixture-result-1","result_index":1,"score":999,"subject_key":"subject-one"},{"label":"fixture-result-2","result_index":2,"score":998,"subject_key":"subject-one"}],"status":"ok","subject_key":"subject-one"}
```

| Field | Value |
|---|---|
| Byte length | `299` |
| SHA-256 | `40735fbc1cd0f98e140857bec1b1e8c6d6f666baa0fb49bfd0e782aaa6513eac` |

Capture:

```text
{"adapter_contract":"fixture-panel-v1","attempt_id":"46d5fb97c109b9f64a42ff3a5e62978e2c25551d6b7274603fc88456acfd9a0f","provider":"fixture","request":{"body":{"body":{"bytes":124,"sha256":"f16972cae6bea7a84acc0c6d0b181a2de3fabf7870663b1fb76f389aed4c38ec"},"state":"present_nonempty"},"headers":[["content-type","application/json"]],"host":"fixture-panel","method":"POST","path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},"request_fingerprint":"d18682cc029a8db08b0b761b900db2c7c91f92a99087597281cbdbdaec70e88b","request_started_at":"2026-08-11T20:15:30.200000Z","response":{"body":{"body":{"bytes":299,"sha256":"40735fbc1cd0f98e140857bec1b1e8c6d6f666baa0fb49bfd0e782aaa6513eac"},"state":"present_nonempty"},"completeness":"complete","headers":[["content-type","application/json"]]},"response_body_ended_at":"2026-08-11T20:15:30.950000Z","response_headers_at":"2026-08-11T20:15:30.900000Z","schema":"observatory.capture-event","software":{"observatory_version":"conformance-v1"},"transport_ended_at":"2026-08-11T20:15:31.000000Z","transport_failure":null,"transport_state":"response_complete","version":1}
```

| Field | Value |
|---|---|
| Trailing newline | absent |
| `capture_id` | `604663f0e7842f1e076189652667357083d4c4a5e56a44d67ea4596ef624ad44` |
| Parent | V2-AR only |

### Set RP — `response_partial` (nonce `1123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef`)

#### V0-RP request body

```text
{"contract":"fixture-panel-v1","depth":2,"panel_id":"panel-alpha","scenario":"response_partial","subject_key":"subject-one"}
```

| Field | Value |
|---|---|
| Byte length | `124` |
| SHA-256 | `96681c6e071e21092d930892b95218d2f84df814ee47034de23715b5fa6dac01` |

#### V1-RP fingerprint preimage

```text
{"adapter_contract":"fixture-panel-v1","provider":"fixture","request":{"body":{"body":{"bytes":124,"sha256":"96681c6e071e21092d930892b95218d2f84df814ee47034de23715b5fa6dac01"},"state":"present_nonempty"},"headers":[["content-type","application/json"]],"host":"fixture-panel","method":"POST","path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},"schema":"observatory.request-fingerprint","version":1}
```

| Field | Value |
|---|---|
| `request_fingerprint` | `decf4fda3e0dafde1ddd1857b74c86603453c056c3a151cb882099f29b2291ce` |

#### V2-RP Attempt

```text
{"adapter_contract":"fixture-panel-v1","attempt_nonce":"1123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef","authorized_at":"2026-08-11T20:15:30.123456Z","parameters":{"contract":"fixture-panel-v1","depth":2,"panel_id":"panel-alpha","scenario":"response_partial","subject_key":"subject-one"},"policy":{"mode":"fixture_no_spend","policy_version":"fixture-v1"},"provider":"fixture","request":{"body":{"body":{"bytes":124,"sha256":"96681c6e071e21092d930892b95218d2f84df814ee47034de23715b5fa6dac01"},"state":"present_nonempty"},"headers":[["content-type","application/json"]],"host":"fixture-panel","method":"POST","path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},"request_fingerprint":"decf4fda3e0dafde1ddd1857b74c86603453c056c3a151cb882099f29b2291ce","schema":"observatory.attempt-event","software":{"observatory_version":"conformance-v1"},"version":1}
```

| Field | Value |
|---|---|
| `attempt_id` | `2af733226ee72e74ee0a1d5196353d74df816faf0a7801f634fb1a0d0d6784e0` |

#### V4 Capture `response_partial` (body end `2026-08-11T20:15:30.920000Z`)

Partial body = first 32 bytes of JCS(`admitted_results_body(panel-alpha, subject-one, 2)`)
= first 32 bytes of V3 response body.

| Field | Value |
|---|---|
| Hex | `7b22636f6e7472616374223a22666978747572652d70616e656c2d7631222c22` |
| UTF-8 | `{"contract":"fixture-panel-v1","` |
| Byte length | `32` |
| SHA-256 | `02e3821de6b9055e97976f31da2896fd48f513e011459a84841665990fed04df` |

Capture:

```text
{"adapter_contract":"fixture-panel-v1","attempt_id":"2af733226ee72e74ee0a1d5196353d74df816faf0a7801f634fb1a0d0d6784e0","provider":"fixture","request":{"body":{"body":{"bytes":124,"sha256":"96681c6e071e21092d930892b95218d2f84df814ee47034de23715b5fa6dac01"},"state":"present_nonempty"},"headers":[["content-type","application/json"]],"host":"fixture-panel","method":"POST","path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},"request_fingerprint":"decf4fda3e0dafde1ddd1857b74c86603453c056c3a151cb882099f29b2291ce","request_started_at":"2026-08-11T20:15:30.200000Z","response":{"body":{"body":{"bytes":32,"sha256":"02e3821de6b9055e97976f31da2896fd48f513e011459a84841665990fed04df"},"state":"present_nonempty"},"completeness":"partial","headers":[["content-type","application/json"]]},"response_body_ended_at":"2026-08-11T20:15:30.920000Z","response_headers_at":"2026-08-11T20:15:30.900000Z","schema":"observatory.capture-event","software":{"observatory_version":"conformance-v1"},"transport_ended_at":"2026-08-11T20:15:31.000000Z","transport_failure":null,"transport_state":"response_partial","version":1}
```

| Field | Value |
|---|---|
| `capture_id` | `f1d0ba4aaba85458c6e9aae540d6baf30ba958ebe7104d59c13e65107a6f677b` |
| Parent | V2-RP only (not V2-AR) |

### Set NR — `no_response` (nonce `2123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef`)

#### V0-NR request body

```text
{"contract":"fixture-panel-v1","depth":2,"panel_id":"panel-alpha","scenario":"no_response","subject_key":"subject-one"}
```

| Field | Value |
|---|---|
| Byte length | `119` |
| SHA-256 | `62ac69e163508f05477523a344d9bf491225aa241a9969cf4138372f73808105` |

#### V1-NR fingerprint preimage

```text
{"adapter_contract":"fixture-panel-v1","provider":"fixture","request":{"body":{"body":{"bytes":119,"sha256":"62ac69e163508f05477523a344d9bf491225aa241a9969cf4138372f73808105"},"state":"present_nonempty"},"headers":[["content-type","application/json"]],"host":"fixture-panel","method":"POST","path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},"schema":"observatory.request-fingerprint","version":1}
```

| Field | Value |
|---|---|
| `request_fingerprint` | `54a73fea1fa17796ac1e3b5a97d16687f506a43a9d861380cd2c9b311f75aaa6` |

#### V2-NR Attempt

```text
{"adapter_contract":"fixture-panel-v1","attempt_nonce":"2123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef","authorized_at":"2026-08-11T20:15:30.123456Z","parameters":{"contract":"fixture-panel-v1","depth":2,"panel_id":"panel-alpha","scenario":"no_response","subject_key":"subject-one"},"policy":{"mode":"fixture_no_spend","policy_version":"fixture-v1"},"provider":"fixture","request":{"body":{"body":{"bytes":119,"sha256":"62ac69e163508f05477523a344d9bf491225aa241a9969cf4138372f73808105"},"state":"present_nonempty"},"headers":[["content-type","application/json"]],"host":"fixture-panel","method":"POST","path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},"request_fingerprint":"54a73fea1fa17796ac1e3b5a97d16687f506a43a9d861380cd2c9b311f75aaa6","schema":"observatory.attempt-event","software":{"observatory_version":"conformance-v1"},"version":1}
```

| Field | Value |
|---|---|
| `attempt_id` | `8d94de30e27141dc315bc747afdc8f4ea5877709279a6383c738d6dade855ca2` |

#### V5 Capture `no_response`

No response body.

```text
{"adapter_contract":"fixture-panel-v1","attempt_id":"8d94de30e27141dc315bc747afdc8f4ea5877709279a6383c738d6dade855ca2","provider":"fixture","request":{"body":{"body":{"bytes":119,"sha256":"62ac69e163508f05477523a344d9bf491225aa241a9969cf4138372f73808105"},"state":"present_nonempty"},"headers":[["content-type","application/json"]],"host":"fixture-panel","method":"POST","path":"/v1/measure","port":null,"query":[],"scheme":"fixture"},"request_fingerprint":"54a73fea1fa17796ac1e3b5a97d16687f506a43a9d861380cd2c9b311f75aaa6","request_started_at":"2026-08-11T20:15:30.200000Z","response":null,"response_body_ended_at":null,"response_headers_at":null,"schema":"observatory.capture-event","software":{"observatory_version":"conformance-v1"},"transport_ended_at":"2026-08-11T20:15:31.000000Z","transport_failure":{"code":"fixture_no_response","phase":"receive_response"},"transport_state":"no_response","version":1}
```

| Field | Value |
|---|---|
| `capture_id` | `b7cde7e1f921598fd7daf1ac7f7fe16a964832a58adb3cf5b6e47ed017e02134` |
| Parent | V2-NR only |

### Empty body digest

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

---

## Verification / out of scope / unproven

Vertical slice: real format-2 FS + real PostgreSQL; full ten-scenario algorithm; rebuild;
tamper; API Outcomes+Observations. Deferred: multi-process locks, off-host backup, paid
providers, production auth, Projection tables, HTTP Capture v1 fields.

---

## Appendix A — Q1–Q37 index (non-normative)

| Topics | Owner |
|---|---|
| Q1–Q11 domain/storage/admission | D8, VOCABULARY, this spec |
| Q12–Q19 slice/API | VISION, this spec |
| Q20–Q22 FORMAT/paths | this spec |
| Q23–Q25 tooling/deferrals | this spec; deferred.md |
| Q26–Q32 timestamps/fixture/API integrity | this spec |
| Q33 authority package | CE-01 |
| Q37 closed tables, construction order, general algorithm, vectors | this section set |
