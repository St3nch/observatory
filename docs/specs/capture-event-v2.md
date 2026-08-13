# Capture Event v2 — Normative Contract

**Status:** accepted normative specification (CE-01 authority package; Q37 schemas)
**Authority parents:** VISION.md, VOCABULARY.md, D8, ADR 0001
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
13. Fixture-first (`fixture-panel-v1`); no real provider network.
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

### Future HTTP adapters

Must introduce a new Capture layout/manifest version. Must not add keys to capture-event v1.

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
that honours `fsync` and provides atomic `link(2)` and `rename(2)` within that filesystem.
It does not claim protection against hardware that acknowledges `fsync` without persisting,
filesystems lacking those guarantees, writes spanning two filesystems, or concurrent writers
— multi-process writer safety is deferred (F7). Tests prove the protocol, not the hardware.

#### D1 — Durable file materialization

Every file entering the store is materialized identically:

1. Create a uniquely named file under `.tmp/` and write its complete bytes.
2. `fsync` that file descriptor, then close it.
3. Install it at its final path by `link(2)` from the temporary path. `link(2)` fails with
   `EEXIST` if the target exists; this is the required exclusive no-overwrite install.
   `rename(2)` **must not** be used to install, because it silently replaces.
4. `unlink` the temporary path, leaving link count 1 at the final path.
5. `fsync` the directory containing the final path.

A partially written file therefore never occupies a final path, and no install can
overwrite.

#### D2 — Durable directory creation

Directories are created parent-first. After each newly created directory, `fsync` its
parent. A directory must be durable before any child is installed within it.

#### D3 — `EEXIST` handling differs by kind

- **Object pool** (`objects/sha256/...`): paths are content-addressed, so recurrence is
  normal. Read the existing object, verify its byte length and SHA-256 against the expected
  values, and accept it on match. On mismatch, fail closed as store corruption. Never
  overwrite, never truncate, never trust the path without verifying the content.
- **Bundle directories, manifests, body files, and `COMMITTED`**: `EEXIST` is an anomaly.
  Fail closed. Event identities are digest-derived and Attempts carry a fresh nonce, so a
  collision indicates corruption or a defect, never ordinary recurrence.

#### D4 — Bundle commit order

A bundle is built at its final path, not staged and moved. An incomplete bundle is
invisible as Evidence because `COMMITTED` is absent — that is the mechanism.

1. Create the bundle directory chain per D2.
2. Install the manifest (`attempt.json` / `capture.json`) per D1.
3. Install body files (`request.body` / `response.body`) per D1, when present. Materialize
   by independent copy or COW reflink from the pool object. **Ordinary hardlinks from a
   bundle into the object pool are forbidden**: a bundle body file must have link count 1
   and must not share an inode with its pool object.
4. `fsync` the bundle directory.
5. Install `COMMITTED` per D1, content exactly `<event_id>\n`. This is always last.
6. `fsync` the bundle directory again.

After step 6 the event is Evidence. Before it, it is not — at any interruption point.

#### D5 — Verify after commit

After step 6, read the event back from disk and verify before the caller may rely on it:
re-hash the stored manifest bytes and compare to the event ID, verify each body object's
digest and length, and confirm `COMMITTED` content equals `<event_id>\n`. A commit that
cannot be verified is a failure, not a success with a warning.

#### D6 — Reading

A bundle directory without `COMMITTED` is **ignored** — not Evidence, and not an error. It
is the expected residue of an interrupted commit. A bundle with `COMMITTED` that fails D5
verification is an integrity failure and must be reported as one, never silently skipped.

#### D7 — `FORMAT.json`

Written once at store creation per D1, followed by `fsync` of the Evidence root. Opening
requires exact canonical bytes and matching digest; anything else fails closed.

#### D8 — No transport before durable Attempt

Fixture or provider transport must not begin until the Attempt has completed D4 and passed
D5. This ordering is structural, not advisory: the transport call must be unreachable from
any path that has not first obtained a verified committed Attempt.

---

## Rebuildable PostgreSQL / entrypoints / API

`derivation_versions`, `outcomes`, `observations`; capture/derive/status/scrub CLIs;
`GET /v1/health`, `GET /v1/attempts/{attempt_id}`; loopback; no auth; 409
`evidence_integrity_failure` on failed verify-on-read. Observation natural identity
`(capture_id, derivation_version_id, within_capture_result_id)` with
`within_capture_result_id = "result:"` + decimal index; provider `fixture`.

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
| UTF-8 | `{"contract":"fixture-panel-v1",` |
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
