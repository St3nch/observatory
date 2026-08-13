# CE-02 — Canonical JCS, closed schemas, and content-ID vectors

**Status:** done
**Parent spec:** docs/specs/capture-event-v2.md
**Kind:** necessary prefactor
**Blocked by:** None — can start immediately
**Approved by:** Project Steward
**Start commit:** b6d795e

## What to build

End-to-end behaviour this ticket makes work: pure, in-memory construction and validation of
identity-bearing Capture Event documents so that published content IDs and digests match
authority and invalid closed-schema inputs fail closed—without writing Evidence, running
transport, PostgreSQL, or HTTP.

## Authority

- `docs/specs/capture-event-v2.md` — §Scalar constraints (global)
- `docs/specs/capture-event-v2.md` — §Canonicalization and verify-on-read (JCS, hash algorithm, re-JCS equality)
- `docs/specs/capture-event-v2.md` — §Closed schemas (recursive unknown-key rule; `body_ref` through Capture/Attempt/request-fingerprint)
- `docs/specs/capture-event-v2.md` — §Conformance vectors (Sets AR, RP, NR; empty-body digest)
- `decisions/decisions.md` — D8 (full SHA-256 identities; JCS manifests)
- `VOCABULARY.md` — Attempt, Capture, request_fingerprint

## Scope

- RFC 8785 / JCS UTF-8 serialization (no trailing newline) for identity-bearing documents
- Recursive closed-schema validation (unknown properties forbidden at every nested object)
- Content digests and IDs: body SHA-256, `request_fingerprint`, `attempt_id`, `capture_id`
- Null-versus-omit rules as specified (including optional non-null `prior_attempt_id`)
- All published AR / RP / NR vector documents and digests as automated golden tests

## Out of scope

- Evidence Store filesystem, FORMAT.json on disk, paths, durability, COMMITTED
- Fixture transport, capture/derive/status/scrub CLIs
- PostgreSQL, HTTP API
- Provider network calls
- Deferred work (F3, F6–F10)

## Acceptance criteria

- [ ] Every published JCS document in §Conformance vectors (request bodies, fingerprint preimages, Attempt manifests, Capture manifests, response bodies as applicable) hashes to its published lowercase SHA-256 when encoded as UTF-8 with no trailing newline.
- [ ] For published AR / RP / NR inputs, computed `request_fingerprint`, `attempt_id`, and `capture_id` match the published identity digests.
- [ ] Documents with unknown properties at any depth are rejected.
- [ ] `attempt_nonce` must be exactly `[0-9a-f]{64}`; invalid length/charset rejected.
- [ ] Timestamps not matching the frozen syntax are rejected.
- [ ] Closed enums and exact constants (`schema`, `version`, `provider`, `adapter_contract`, fixture request constants) are enforced.
- [ ] `prior_attempt_id`, when absent, is omitted (not null); null is rejected when the field is present incorrectly.
- [ ] Re-JCS of a parsed valid document equals the original stored/canonical bytes for vector cases.
- [ ] No filesystem Evidence write is required for these tests to pass.

## Verification

- Commands: `uv run pytest -q`; `uv run ruff check .`; `uv run mypy` as applicable
- Substrate: ordinary unit tests
- Forbidden claims: no durability, PostgreSQL, or live-provider proof; mocks of FS/PG not required and must not be claimed as substrate proof

## Required automated tests

- Schema-closure / unknown-property rejection
- JCS canonicalization
- Byte-count and SHA-256 vector tests (all published vectors)
- Request-fingerprint tests
- Attempt ID tests
- Capture ID tests
- Negative and boundary-input tests (nonce, timestamps, enums, omit/null)

## Forbidden claims

- Store durability, crash recovery, multi-process safety
- API or derive behavior
- Anything beyond pure identity/schema correctness

## One implementation commit must prove

Identity construction and closed-schema enforcement match committed vectors and rules without any later ticket.

## Later tickets

Later tickets are **not** required to make this ticket’s acceptance criteria truthful.

## Beyond authority

This ticket adds **no** behavior beyond committed authority.

## Implementation report

<!-- implement fills; may set Status: review; never Status: done -->

- End commit: c099d3a
- Acceptance evidence:
  - `uv run pytest -q` — 72 passed after integer-bound remediation
  - I-JSON safe-integer bound on every identity-bearing integer
    (`test_canonical_json_accepts_safe_integer_boundaries`,
    `test_canonical_json_rejects_integers_outside_safe_range`,
    `test_canonical_json_applies_integer_bound_in_objects_and_arrays`,
    `test_body_ref_bytes_rejects_integer_outside_safe_range`).
  - `uv run ruff check .` — clean
  - `uv run mypy` — clean
  - Published AR/RP/NR request bodies, fingerprint preimages, Attempt/Capture
    manifests, and response bodies hash to the spec digests
    (`test_published_request_bodies_hash_to_published_digests`,
    `test_constructed_ar_rp_nr_identities_match_published_digests`,
    `test_attempt_construction_matches_published_ar_bytes_and_id`,
    `test_capture_ar_construction_matches_published_id`,
    `test_fingerprint_id_matches_published_ar_vector`).
  - Unknown properties rejected at document and nested depth
    (`test_parameters_rejects_unknown_property`,
    `test_body_ref_rejects_unknown_property`,
    `test_request_rejects_unknown_top_level_property`,
    `test_request_rejects_unknown_property_at_nested_body`,
    `test_policy_rejects_unknown_property`,
    `test_software_rejects_unknown_property`,
    `test_fingerprint_rejects_unknown_property`,
    `test_attempt_rejects_embedded_attempt_id`,
    `test_transport_failure_rejects_unknown_property`,
    `test_capture_rejects_unknown_top_level_property`,
    `test_capture_rejects_unknown_property_at_response_depth`).
  - `attempt_nonce` charset/length
    (`test_attempt_nonce_rejects_invalid_length_and_charset`).
  - Frozen timestamp syntax
    (`test_attempt_rejects_timestamp_not_matching_frozen_syntax`).
  - Closed enums/constants
    (`test_parameters_rejects_unknown_scenario`,
    `test_request_rejects_non_fixture_constants`,
    `test_attempt_rejects_wrong_schema_version_provider_or_contract`,
    `test_fingerprint_rejects_wrong_schema_version_provider_or_contract`,
    `test_capture_rejects_wrong_schema_version_provider_or_contract`).
  - `prior_attempt_id` omit-not-null
    (`test_attempt_omits_prior_attempt_id_when_absent`,
    `test_attempt_rejects_null_prior_attempt_id`,
    `test_attempt_accepts_present_prior_attempt_id`).
  - Re-JCS of published bytes
    (`test_re_jcs_of_parsed_published_vectors_equals_original_bytes`).
  - No Evidence write
    (`test_vector_validation_does_not_write_the_filesystem`; tests are in-memory).
  - Cross-field: fingerprint recompute
    (`test_attempt_rejects_mismatched_request_fingerprint`).
  - Cross-field: parameters vs request body identity
    (`test_attempt_rejects_parameters_that_do_not_match_request_body`).
  - Cross-field: body_state discriminant
    (`test_body_state_absent_rejects_null_body`,
    `test_body_state_present_zero_requires_empty_digest`,
    `test_body_state_present_zero_accepted_on_complete_response`,
    `test_body_state_present_nonempty_rejects_zero_bytes`,
    `test_capture_partial_rejects_absent_or_zero_body`).
  - Cross-field: Capture branch nulls / completeness
    (`test_capture_complete_rejects_non_null_transport_failure`,
    `test_capture_complete_rejects_null_response`,
    `test_capture_complete_rejects_partial_completeness`,
    `test_capture_no_response_rejects_non_null_response_fields`,
    `test_capture_no_response_rejects_null_transport_failure`,
    `test_capture_no_response_rejects_wrong_failure_object`).
  - Cross-field: timestamp order
    (`test_capture_rejects_timestamp_order_violation`).
  - Cross-field: parent Attempt agreement when supplied
    (`test_capture_rejects_parent_attempt_mismatch`).
- Unproven limits:
  - JCS is the in-repo subset needed for this document set (UTF-16 key sort,
    integer-only numbers inside the I-JSON safe-integer range, RFC 8785 string
    escapes, no trailing newline). Floats are rejected. Integers outside
    ±9007199254740991 are rejected; there is no exponential serializer.
  - `validate_fixture_request` always enforces fixture-panel-v1 request
    constants. There is no general-request mode.
  - Capture `response.headers` are validated as lowercase pairs, not restricted
    to the two fixture header arrays `H_json` / `H_plain`.
  - Timestamps must match the frozen syntax and also parse as a calendar datetime
    (`datetime.strptime`); Feb 31 is rejected.
  - Isolated Capture validation checks `attempt_id` format only; parent identity
    is enforced when `attempt=` is passed or via `capture_document`.
  - No Evidence Store, FORMAT.json-on-disk, durability, PostgreSQL, HTTP, or
    live-provider claim. The other seven fixture scenarios are not constructed.
- Review findings remaining:
  - Public documents are `dict[str, object]`, not TypedDicts. CE-03 will cast.
  - `test_vector_validation_does_not_write_the_filesystem` only proves one
    constructor left `tmp_path` empty; the real proof is that the suite needs
    no store.
  - Remediation after cca1191: U+2028/U+2029 no longer escaped; lone surrogates
    raise DocumentError; per-object unknown-key tests; fingerprint and Capture
    exact-constant tests; `validate_request` renamed to
    `validate_fixture_request`. RFC 8785 string tests added so goldens are not
    the only escape-table proof.
  - Remediation after 780f7b2 / c099d3a: encoder and `_json_int` reject
    integers outside ±9007199254740991. Also key-escape, empty-object, and
    signed-boundary tests.

### Public module surface (`observatory.capture_event`)

In-repo JCS; no new dependency; pydantic not used.

- `DocumentError(ValueError)` — canonicalization or closed-schema failure.
- `EMPTY_BODY_SHA256: str` — published empty-bytes digest.
- `canonical_json(value: object) -> bytes` — RFC 8785 JCS UTF-8, no trailing
  newline; rejects floats and lone surrogates. U+2028/U+2029 are literal.
- `content_digest(data: bytes) -> str` — 64-char lowercase hex SHA-256.
- `body_ref(data: bytes) -> dict[str, int | str]` — `{bytes, sha256}`.
- `fixture_request(*, body: bytes) -> dict[str, object]` — closed fixture
  `request` with `present_nonempty` body.
- `fingerprint_document(*, request: Mapping[str, object]) -> dict[str, object]`
  — closed `observatory.request-fingerprint` v1.
- `attempt_document(*, parameters, attempt_nonce, authorized_at,
  observatory_version, prior_attempt_id=None) -> dict[str, object]` — builds
  request, fingerprint, and closed Attempt; omits `prior_attempt_id` when
  absent. `request_fingerprint` is computed, not caller-supplied.
- `capture_document(*, attempt, request_started_at, transport_ended_at,
  transport_state, response, transport_failure, response_headers_at,
  response_body_ended_at, observatory_version=None) -> dict[str, object]` —
  cites parent Attempt identity; software defaults to the Attempt's.
- `validate_parameters/fixture_request/fingerprint/attempt(value) -> dict[str, object]`
  — `value` is a mapping or UTF-8 JSON `bytes`. Bytes require re-JCS equality.
- `validate_capture(value, *, attempt=None) -> dict[str, object]` — same, plus
  parent cross-field rules when `attempt` is supplied.

Identity IDs are `content_digest(canonical_json(document))` after validation.

## Closure

<!-- Project Steward only -->

- Closed at commit: `c0a2189a66adcd4807c1b2ae3ce886f7810cd5d9`
- Evidence accepted: **yes**

Implementation landed across three commits: `cca1191` (initial), `780f7b2` (escape,
surrogate, and proof-coverage remediation), `c0a2189` (integer bound). The Implementation
report's `End commit` names a parent by design — a commit cannot contain its own hash. This
line is authoritative.

### Steward verification at c0a2189

Checked directly, not taken from the implementation report: 72 tests pass; `ruff` and `mypy`
clean; golden constants traced to `docs/specs/capture-event-v2.md` lines 83, 595, and 629,
confirming expectations are fixed from the spec rather than derived from implementation
output; `validate_request` has zero occurrences repository-wide; `_jcs` routes integers
through `_jcs_int`, with `bool` tested before `int`; the safe-integer bound is enforced at
the encoder, the validator, and the `body_ref` constructor, so an oversized body length
fails before serialization.

### Review history — three rounds, three defect classes

All three were invisible behind a green suite, and none was caught by the published vectors,
which are ASCII and small-integer.

1. **U+2028/U+2029 escaped.** Found independently by [GPT] and [CLAUDE]. The committed test
   asserted the wrong output, entrenching it.
2. **Lone surrogates leaked `UnicodeEncodeError`.** Found by [GPT]. The module declares
   `DocumentError` as its canonicalization failure.
3. **Unbounded `str(int)`.** Found by [CLAUDE], understated as a 2⁵³ precision issue,
   recorded as an accepted limit, and the ticket closed. [GPT] demonstrated by hostile test
   that `10**30` renders as thirty-one digits where JCS requires `1e+30`, and that closing
   was wrong.

[GROK] predicted this entire class in his first report — that a wrong escape or number rule
would pass every golden — before either reviewer looked. Encoder correctness now rests on
RFC-derived and non-ASCII tests rather than on the project's own vectors.

**Steward error, recorded because it should not recur:** accepting a known conformance
divergence in identity-bearing serialization on the grounds that it was unreachable by the
current document set. Reachability bears on urgency, never on whether a wrong identity is
acceptable. Separately, the first written rationale for the bound overstated RFC 8785 in
three places and was corrected in `c099d3a` after [GPT] caught it.

### Decisions recorded here

- Calendar-valid timestamps: `strptime`, so an impossible date such as Feb 31 is rejected.
- Fixture constants enforced on every request validation, consistent with the fixture-only
  boundary. Named `validate_fixture_request` so no later ticket mistakes it for a general
  validator.
- Response headers accept any lowercase pairs. Scenario-specific headers belong to CE-04.
- Integer range bounded to ±(2⁵³−1). Recorded in the spec, not here, because it constrains
  every future document. The encoder applies the signed range; field rules add `≥ 0`.

### Unproven limits

- Behaviour differs from a conforming JCS implementation only in being **fail-closed**: we
  reject floats, out-of-range integers, lone surrogates, and non-JSON types rather than
  serializing them. No divergence remains on a value we accept.
- C1 controls and U+007F as string content are untested, but take the literal-BMP branch
  already covered by non-ASCII tests — same path, not a separate rule.
- Duplicate keys on the bytes-parse path resolve last-wins via `json.loads`, which is parser
  behaviour rather than encoder output. I-JSON forbids duplicate names; this is not
  currently rejected. Revisit if any input arrives from outside our own construction.
- A lone surrogate in an object key raises `DocumentError` via the `canonical_json`
  `UnicodeEncodeError` wrapper rather than the `_jcs_string` boundary check, so its message
  reads "JCS output is not valid UTF-8" instead of naming surrogates. Contract holds;
  wording imprecise.
- Nothing here proves Evidence Store, durability, `COMMITTED`, derive, API, PostgreSQL, or
  the seven fixture scenarios outside AR/RP/NR.
