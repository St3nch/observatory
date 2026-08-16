# PF-03 — DataForSEO Keyword Overview bounded paid probe

**Status:** review
**Parent spec:** docs/specs/capture-event-v2.md, “Paid Keyword Overview probe adapter”
**Authority:** D8, D9, D10; HAM-01 closure
**Kind:** bounded paid-provider implementation
**Blocked by:** none for implementation/review; live operator call blocked by F6
**Approved by:** Project Steward
**Start commit:** `56ba6953cdbfeb35c8583e75e7cea23836cfdd9d`

## Why this ticket exists

PF-02 proved one authenticated free sandbox exchange and HAM-01 proved the relevant
process-death boundaries. The sandbox response is dummy data. This ticket implements the
smallest paid request that can preserve real keyword metrics for later inspection while
keeping spend, request shape, and transport count closed.

DataForSEO remains the only current provider. Do not add Ahrefs, Semrush, a provider
catalog, or a generic HTTP runner.

## Exact adapter

Implement only
`dataforseo-labs-google-keyword-overview-live-paid-probe-v1`:

- one POST to
  `https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_overview/live`;
- exactly one task and one exchange;
- one to five ordered, unique keywords, each with at most 10 words;
- fixed `location_code=2840`, `language_code=en`;
- fixed `include_serp_info=false` and `include_clickstream_data=false`;
- exact JCS singleton task-array body;
- no redirect, retry, poll, second request, price/account preflight, or endpoint override;
- exact paid policy and 20,000 micro-USD acknowledgement from the normative spec.

Use the existing credential environment names and memory-only credential object. The
public entrypoint accepts no credentials, URL, host, path, headers, arbitrary JSON,
location, language, enrichments, timeout, retry, or alternate ceiling.

## CLI and one-shot guard

Provide a service-owned capture mode equivalent to:

    uv run python -m observatory.dataforseo_paid_probe capture \
      --evidence-root PATH \
      --keyword "seo api" \
      --keyword "keyword research" \
      --authorize-max-micro-usd 20000

The authorization value must be exactly integer `20000`; missing, malformed, smaller,
or larger values fail before Attempt creation. Credential presence alone is not paid-call
authorization.

Before Attempt creation, inspect the store and fail if it already has a committed Attempt
for this paid adapter. Valid fixture and sandbox events may coexist. This prevents a
second sequential paid call in the same root. Do not claim it prevents simultaneous
processes; F7 remains deferred.

Capture success prints only `attempt_id` and `capture_id`. It never prints the response,
credentials, request exceptions, provider messages, price claims, or a success
classification.

Provide a separate read-only inspection mode equivalent to:

    uv run python -m observatory.dataforseo_paid_probe inspect \
      --evidence-root PATH \
      --capture-id 64_HEX

It performs no network and no mutation. It must require full D5 read-back of a complete
Capture for this exact adapter and emit the exact stored response-body bytes to stdout,
unchanged and with no added newline. It rejects partial/no-response, zero/absent body,
wrong adapter/version, invalid/tampered Evidence, and extra arguments. Diagnostics are
fixed and go to stderr. It is an operator inspection surface, not Derivation, an API,
Outcome, Observation, or second authority.

## Closed event construction

Extend event-version-2 validation by exact adapter-contract dispatch. Schema/version
dispatch remains the existing two-field peek; after it selects v2, the v2 validator must
select one of the two recognized closed adapters and then revalidate schema, version,
provider, adapter, request, parameters, policy, and every cross-field rule. Unknown or
confused combinations fail closed.

Do not change event-v1 or the existing sandbox contract, vectors, constructors, or IDs.
Use adapter-specific paid constructors/validators with names that do not silently change
the sandbox functions' meaning.

Keyword rules are exactly normative: array length 1..5, order preserved, no duplicates,
and each keyword matches the spec's printable-ASCII/length/boundary rule plus its maximum
of 10 maximal nonempty word runs separated by ASCII space. Request-body bytes equal JCS of
one task formed by removing only `contract` from parameters.

## Structural send gate

Use a paid-adapter-specific caller-unconstructible one-use capability. It must require the
exact concrete `EvidenceStore` and this order:

1. validate authorization, one-shot store state, closed parameters, and exact body;
2. construct the credential-free paid HTTP-v2 Attempt;
3. commit Attempt plus exact request body;
4. read back and fully verify document identity, body bytes, adapter, paid policy, target,
   task count, enrichments off, and authorization ceiling;
5. only then issue the capability and inject Basic Authorization;
6. perform exactly one exchange;
7. commit at most one Capture and require full read-back.

The send primitive accepts only its own issued capability and frozen bytes. It must not
accept arbitrary mappings or public client/endpoint arguments. For deterministic tests,
an internal seam may accept only
`http://127.0.0.1:<1..65535>/v3/dataforseo_labs/google/keyword_overview/live`,
checked before Attempt and again immediately before exchange. It is unreachable from the
public capture mode.

Use the same exact sent-header equation, `trust_env=False`, TLS verification, HTTP/2
setting, redirects-disabled behavior, timeouts, raw streaming, 8 MiB limit,
`http-headers-v1` omission policy, timestamp rules, transport-failure table, and
credential-echo fail-closed rule as PF-02. Share code only when the resulting adapter
checks remain explicit and closed; do not introduce a generic provider transport API.

Completed 3xx/4xx/5xx is still complete HTTP testimony. Provider status is not transport
status. If the response echoes login, password, full Basic value, or bare token in its
retained body/header testimony, fail closed and commit no Capture.

## Paid-call prohibition during implementation

Implementation, ordinary tests, focused tests, formal review, and the implementer's report
must make zero DataForSEO/public-network calls and spend zero credit. Use only
`httpx.MockTransport` and a real `127.0.0.1` loopback server. An autouse network guard
must fail any non-loopback connection.

The implementer must not run the public CLI with real credentials. A live operator
command is not part of this implementation ticket's execution authority. F6 must close
first; afterward the Steward will recheck current official pricing and issue one exact
command to [CHAZ].

## Required automated proof

At minimum:

- independent test literals reproduce the paid vector's five byte lengths/digests/IDs;
- existing event-v1 and sandbox HTTP-v2 bytes/IDs remain unchanged;
- valid mixed stores containing fixture, sandbox, and paid event-v2 Evidence verify and
  scrub clean;
- fixture derive writes exactly its prior rows and skips both valid provider adapters with
  zero provider rows and no integrity failure;
- paid parameter boundaries, duplicates, keyword character/length/10-word rules, fixed
  booleans, fixed location/language, exact policy, and exact task bytes are closed;
- sandbox/paid adapter, host, path, policy, parameter, and body-confusion cases fail;
- missing/wrong authorization acknowledgement fails before Attempt, handler, or credential
  injection;
- a store with one committed paid Attempt refuses another before handler/send, including
  when the first Attempt has no Capture;
- forged/subclass/failed-commit/failed-readback/tampered-capability cases cannot send;
- loopback proves one request, exact on-wire body/content-length/header equation, no
  redirect, no retry, and a verified committed Attempt at request time;
- complete, partial, no-response, status classes, 8 MiB boundary, duplicate/denylisted
  headers, and credential echo retain PF-02 semantics;
- each branch commits at most one verified Capture and scrub is clean;
- read-only inspect emits exact verified bytes and performs zero writes/network;
- inspect rejects wrong adapter, partial/no-response/zero/absent body, unknown version,
  invalid ID, and tampered Evidence without emitting body bytes;
- credentials and Basic forms are absent from Evidence and terminal/exception surfaces;
- public CLI has no endpoint/client/header/credential/enrichment/location/language/retry
  arguments.

Tests should reuse existing PF-02 coverage where truthful, but acceptance cannot rest on
untested assumptions that the sandbox constants also protect the paid adapter.

## Scope constraints

One implementation commit; do not amend or push. The implementer may change only:

- `src/observatory/capture_event.py`;
- new `src/observatory/dataforseo_paid_probe.py`;
- `src/observatory/dataforseo_sandbox.py` only for the smallest explicitly reported
  shared-helper extraction that keeps both adapter gates closed;
- new `tests/test_dataforseo_paid_probe.py`;
- existing `tests/test_http_event_v2.py` only for mixed-adapter/vector regressions;
- this ticket's Status and Implementation report only.

No dependency changes are expected. Do not change Evidence Store format/layout,
`evidence_store.py`, fixture capture/derive/API code, settings or credential environment
names, PostgreSQL schema, another ticket, or authority documents.

If an unlisted production path is genuinely necessary, stop and report the exact
authority/technical conflict instead of editing it.

## Out of scope

- real provider/sandbox/DNS/TLS call by the implementer or automated suite;
- live paid operator smoke before F6 closure;
- DataForSEO User Data, balance, pricing, catalog, Suggestions, Related Keywords, SERP,
  Google Ads Search Volume, Standard/asynchronous, task-post/task-get, or bulk runners;
- provider envelope normalization, schema catalog, Outcome, Observation, Derivation,
  PostgreSQL, or HTTP API;
- response-dependent follow-up, retry, replay, scheduling, batching beyond five keywords;
- Ahrefs, Semrush, generic provider interfaces, or strategy-layer work;
- F6 off-host implementation, F7 concurrency, power-loss/device-cache claims.

## Verification and report

Run:

- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy`

Set Status to `review`, never `done`. Report:

- loaded skill paths;
- exact parent/child SHAs and changed paths;
- acceptance criterion to proving-test map;
- independently recomputed paid and unchanged sandbox/vector bytes and IDs;
- exact structural gate and one-shot-store mechanism;
- mock/loopback request counts and sent-header/body evidence;
- mixed-store scrub and exact PostgreSQL row accounting;
- inspect-mode byte equality and zero-write/network proof;
- credential non-disclosure evidence;
- full command results;
- weakest/most-fragile area, exact unproven limits, and authority disagreements;
- explicit zero-provider-call/zero-credit confirmation.

Only the Project Steward may close PF-03 after review and the later authorized operator
sequence.

## Implementation report

**Parent:** `56ba6953cdbfeb35c8583e75e7cea23836cfdd9d`  
**Child:** recorded in this implementation commit.

**Loaded skills:**
- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

**Changed paths:**
- `src/observatory/capture_event.py` (paid constructors/validators + v2 adapter dispatch)
- `src/observatory/dataforseo_paid_probe.py` (new; closed gate, one-shot, CLI capture/inspect)
- `tests/test_dataforseo_paid_probe.py` (new)
- `tests/test_http_event_v2.py` (paid vector + mixed fixture/sandbox/paid scrub/derive)
- this ticket (Status + Start commit + Implementation report)

`src/observatory/dataforseo_sandbox.py` was not changed. Shared-helper extraction was attempted and reverted so the paid send primitive would not import sandbox-private names and would not introduce a generic transport API. The paid module duplicates the PF-02 stream/header/echo machinery behind its own gate (D10).

**Structural gate:** `_build_transport_gate()` issues a closure-held `_VerifiedAttempt` only after `type(authorize_max_micro_usd) is int` and the value is exactly `20000`, `type(store) is EvidenceStore`, `inspect_store` one-shot refusal, paid target/policy/parameter recheck, `commit_attempt`, full `read_attempt` + request-body byte match, and paid-target recheck. `_exchange` accepts only an issued instance, marks it used, and sends the frozen body once. Public `capture_dataforseo_paid_probe` has no URL/header/client parameters. CLI never reaches `_run_gated_capture`'s injection seam.

**One-shot store:** before Attempt creation, `inspect_store(root)` lists committed Attempts and `read_attempt`s them. A committed `dataforseo-labs-google-keyword-overview-live-paid-probe-v1` Attempt fails closed, including when it has no Capture. Fixture and sandbox neighbors are allowed. The issuer repeats the same inspect. This is single-process sequential refusal, not F7.

### Acceptance → proving tests

| Criterion | Test |
|---|---|
| Independent paid vector lengths/digests/IDs | `test_independent_paid_vector_bytes_and_ids`, `test_published_paid_vector_bytes_and_constructors` |
| Event-v1 and sandbox HTTP-v2 bytes/IDs unchanged | `test_event_v1_and_sandbox_ids_remain_unchanged`, `test_published_http_v2_vectors_match_independent_sha256_and_lengths`, `test_event_v1_published_bytes_and_ids_are_unchanged` |
| Mixed fixture+sandbox+paid verify/scrub | `test_mixed_store_scrubs_clean_and_unknown_version_is_failure`, `test_one_shot_allows_fixture_and_sandbox_neighbors` |
| Fixture derive skips both provider adapters, zero provider PG rows | `test_mixed_store_derive_writes_only_fixture_rows`, `test_provider_only_store_writes_zero_postgresql_rows` |
| Paid parameter/keyword/policy/task-byte closures | `test_closed_paid_parameters_and_independent_jcs_request_bytes`, `test_paid_keywords_reject_boundaries`, `test_paid_keywords_accept_permitted_charset`, `test_paid_parameters_reject_fixed_field_violations`, `test_paid_keywords_accept_exactly_ten_simple_words`, `test_paid_keywords_accept_exactly_ten_words_with_repeated_internal_spaces`, `test_paid_keywords_reject_eleven_simple_words_below_eighty_characters`, `test_paid_keywords_reject_eleven_words_with_repeated_spaces` |
| Sandbox/paid adapter, host, path, policy, parameter, body confusion | `test_sandbox_and_paid_validators_reject_confused_contracts`, `test_paid_request_rejects_sandbox_host_path_and_policy`, `test_wrong_adapter_sandbox_host_and_unknown_version_cannot_issue` |
| Missing/wrong authorization before Attempt/handler | `test_wrong_authorization_fails_before_attempt`, `test_missing_authorization_cli_fails_before_attempt`, `test_issuer_requires_authorization_before_attempt_or_exchange`, `test_issuer_rejects_malformed_and_wrong_authorization_before_attempt`, `test_public_path_rejects_non_int_authorization_before_attempt`, `test_exact_integer_20000_still_permits_mock_and_loopback` |
| One-shot refuses second paid Attempt, including no Capture | `test_one_shot_refuses_second_paid_attempt_without_capture` |
| Forged/subclass/failed-commit/failed-readback/tampered capability cannot send | `test_forged_capability_cannot_reach_send`, `test_subclassed_store_cannot_issue`, `test_failed_commit_prevents_send`, `test_failed_readback_prevents_send` |
| Loopback one request, exact body/headers, no redirect/retry, verified Attempt | `test_loopback_on_wire_headers_body_and_single_request`, `test_loopback_redirect_is_complete_and_not_followed`, `test_mock_sent_headers_and_body_equation` |
| Complete/partial/no-response, status classes, 8 MiB, denylist, echo | `test_complete_nonempty_zero_byte_and_status_classes`, `test_partial_body_read_failure`, `test_connect_send_and_header_failures_are_no_response`, `test_eight_mib_boundary`, `test_duplicate_retained_and_every_denylisted_header`, `test_credential_echo_in_body_commits_no_capture`, `test_credential_echo_in_retained_header_commits_no_capture` |
| At most one verified Capture; scrub clean | `test_each_branch_commits_one_verified_capture` |
| Inspect exact bytes, zero write/network | `test_inspect_emits_exact_bytes_without_write_or_network` |
| Inspect rejects wrong adapter/partial/no-response/zero/unknown version/invalid ID/tamper | `test_inspect_rejects_wrong_adapter_partial_zero_and_tamper`, `test_inspect_rejects_zero_body_and_tampered_evidence` |
| Credentials absent from Evidence and surfaces | `test_credentials_absent_from_evidence_stdout_repr_and_exceptions` |
| Public CLI has no endpoint/client/header/credential/enrichment/location/language/retry args | `test_cli_rejects_forbidden_arguments`, `test_public_api_has_no_url_or_header_injection`, `test_cli_prints_only_ids` |

### Independently recomputed bytes and IDs

Paid (literals hashed with `hashlib.sha256`, not production constructors):

| Vector | Bytes | SHA-256 |
|---|---:|---|
| request body | 216 | `3fc7205a55a1a5c464c0ae4ebca21a1e3088c2022565929a670fdf757ab7987b` |
| fingerprint preimage | 622 | `6cc5765911abe752a974d2fba268d927fdc055147c1286fffdfe0ee585cdc610` |
| Attempt preimage | 1367 | `89904bf8a6812fb3d0d845310e4705962bb4db928b80da3be67342dff5def185` |
| sample response `{"cost":0.0126,"tasks":[]}` | 26 | `5b69c7675c3f03d95bb5071bf0da855e3a476521939dccd757d3295746cd33d1` |
| complete Capture preimage | 1433 | `dbaaf68a38e54e39d4fc03807d72eda37f8efd9a212220c0a99d270ddcec6917` |

Unchanged sandbox HTTP-v2 / event-v1:

- sandbox request 119 / `d10484d2237e4b08e37a4f3fe66bd678a3dbc2dab96f9b712af1b858b8d6d070`
- sandbox Attempt `22adc4841c86b7cd98b90bba683aeac204a0cb568428b590fd399e8627eb4640`
- sandbox Capture `f347962c8dad05a762a19898898fff7ed60b7c06270b61dc3d7a158fa0d396b7`
- event-v1 AR Attempt `46d5fb97c109b9f64a42ff3a5e62978e2c25551d6b7274603fc88456acfd9a0f`

### Mock / loopback accounting

- Mock complete path: **exactly 1** request; entity bytes = 216-byte JCS task array; sent headers are the five committed application headers + `authorization` + `host=api.dataforseo.com` + `content-length=216`.
- Loopback HTTP/1.1: **exactly 1** request; same body; `host=127.0.0.1:<port>`; `content-length=216`; no extra headers; committed Attempt still names `api.dataforseo.com` and the paid path. Redirect 302 is complete testimony and is not followed. Remote/sandbox/paid-host endpoint overrides: **0** handler calls, **0** Attempts, **0** Captures.

### Mixed-store scrub and PostgreSQL

- Mixed fixture + sandbox HTTP-v2 + paid HTTP-v2: `scrub_store(store) == []`.
- Provider-only (sandbox + paid): `derivation_versions=0`, `outcomes=0`, `observations=0`.
- Mixed with fixture: same fixture counts as a fixture-only baseline — `derivation_versions=1` (`fixture-panel-v1`), `outcomes=2`, `observations=2`. Zero rows cite the sandbox or paid Attempt/Capture IDs. No integrity failure.

### Inspect proof

`inspect_store` + `inspect_paid_probe_body` emit the exact stored response-body bytes. CLI writes those bytes to stdout with no added newline. A full-tree inode/size/bytes snapshot is unchanged. No handler/client/endpoint is involved. Wrong adapter, partial, no-response, zero-byte, unknown version, invalid ID, and tampered Evidence fail closed and emit no body.

### Credential evidence

Sentinel login, password, full Basic value, and bare token are absent from Evidence files, stdout/stderr, `repr`/`str` of credentials and exceptions, and denylisted response-header values. Echo in body or retained header commits the Attempt and **no** Capture.

### Commands

- `uv run pytest -q` — 680 passed, 1 skipped (HAM-01 opt-in matrix), 1 warning
- `uv run ruff check .` — All checks passed
- `uv run mypy` — Success: no issues found in 27 source files

### Review

Two-axis review vs `56ba695…`:

- **Standards:** hard finding was production import of sandbox `_` helpers. Resolved by reverting `dataforseo_sandbox.py` and keeping a paid-local stream/gate. Remaining judgement: intentional D10 duplication of the sandbox transport.
- **Spec:** issuer now repeats the one-shot inspect; inspect tests cover no-response and unknown version. The issuer-authorization residual is closed in the remediation below.

### Weakest / most fragile area

Paid transport is a closed copy of the PF-02 stream, header equation, 8 MiB bound, and exception-to-phase mapping. Drift between the two copies is possible. httpx exception classification remains best-effort. One-shot is inspect-then-act in one process.

### Exact unproven limits

- No TLS, HTTP/2, DNS, timeout-realism, or `api.dataforseo.com` behavior
- No live paid operator invocation (blocked by F6)
- No claim that 20,000 micro-USD is a provider-enforced invoice cap
- No F7 concurrent-writer safety
- No off-host Evidence protection
- No provider Outcome/Observation/Derivation/API
- Ordinary suite does not run the HAM-01 kill matrix

### Confirmation

Implementation, tests, and this report made **zero** DataForSEO, sandbox, DNS, paid-host, or other public-network calls and spent **zero** provider credit. Tests used only `httpx.MockTransport` and `127.0.0.1` loopback. Autouse `socket.create_connection` guard fails any other host. Sentinel credentials only. The public CLI was never run with real credentials. F6 live operator probe was not performed.

### Authority

Assigned start `56ba6953…` is the clean HEAD named in the Steward handoff. No authority documents were edited. No disagreement that changes the implementation. Live paid remains Steward-issued after F6.

### Remediation (on this commit; parent `a3121c63b624b758bdfe7600d1f2b9f0b1a50ae9`)

Steward formal review required the authorization acknowledgement to be bound into the capability issuer, not only `_run_gated_capture`. Status remains `review`.

1. **`_issue_verified_attempt` requires acknowledgement.** `issue()` takes required keyword `authorize_max_micro_usd` and calls `_require_authorization` before store-type check, one-shot inspect, Attempt commit, capability issuance, or `_exchange`. Missing keyword is `TypeError`; no capability is issued, so `_exchange` remains unreachable.
2. **Exact runtime type and value.** `_require_authorization` accepts only `type(value) is int` and `value == 20000`. `20000.0`, strings, `Decimal`, booleans, `None`, and other integers fail with `StoreError` before Attempt or handler.
3. **Adversarial proof.** `test_issuer_requires_authorization_before_attempt_or_exchange`, `test_issuer_rejects_malformed_and_wrong_authorization_before_attempt`, `test_public_path_rejects_non_int_authorization_before_attempt`, `test_exact_integer_20000_still_permits_mock_and_loopback`, plus unchanged one-shot tests. Rejected cases leave 0 Attempts, 0 Captures, and 0 handler calls.

## Steward audit reconciliation — 2026-08-16

Official DataForSEO Keyword Overview documentation states a maximum of 10 words per
keyword phrase in addition to the existing 80-character limit. The accepted event-v2
authority and this ticket now close that boundary as at most 10 maximal nonempty runs
separated by ASCII space.

PF-03 remains `review`. Before any live provider command, add production validation and
tests proving 10-word acceptance, 11-word rejection before Attempt/handler/network, and
unchanged published paid/sandbox/event-v1 vectors. Start from the clean Steward authority
HEAD named in the handoff; create one new commit; do not amend or push. Implementation and
tests remain mock/127.0.0.1 only and must spend zero provider credit.

### 10-word limit remediation (on this commit; parent `7b1fa349509a13d5c1e1f5125917423a3aac53b6`)

Steward audit reconciliation required official DataForSEO 10-word-per-keyword validation.
Status remains `review`. Child SHA is this implementation commit.

**Loaded skills:**
- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

**Changed paths:**
- `src/observatory/capture_event.py` (`_PAID_KEYWORD_MAX_WORDS`, `_paid_keyword_word_count`, `_paid_keywords`)
- `tests/test_dataforseo_paid_probe.py` (adversarial 10/11-word, public-capture accounting, bypass, vector identity)
- this ticket Implementation report only

**Word-count mechanism:** `_paid_keyword_word_count` splits on ASCII space (`str.split(" ")`) and counts nonempty parts. Repeated internal spaces are separators, not empty words. The check runs in `_paid_keywords` after charset/length/boundary match, so `closed_paid_parameters`, `validate_paid_http_parameters`, `paid_http_attempt_document`, and `validate_attempt` share one closed rule. Rejection is `DocumentError` before Attempt commit, capability issue, credential injection, or handler/network.

| Criterion | Test |
|---|---|
| 10 simple words accepted | `test_paid_keywords_accept_exactly_ten_simple_words`, `test_document_validation_accepts_ten_word_keywords`, `test_ten_word_public_capture_is_accepted` |
| 10 words with repeated internal spaces accepted | `test_paid_keywords_accept_exactly_ten_words_with_repeated_internal_spaces`, `test_document_validation_accepts_ten_word_keywords`, `test_ten_word_public_capture_is_accepted` |
| 11 simple words rejected, including below 80 characters | `test_paid_keywords_reject_eleven_simple_words_below_eighty_characters`, `test_document_validation_rejects_eleven_word_keywords` |
| 11 words with repeated spaces rejected | `test_paid_keywords_reject_eleven_words_with_repeated_spaces`, `test_document_validation_rejects_eleven_word_keywords` |
| Rejected public capture: handler=0, Attempts=0, Captures=0 | `test_eleven_word_public_capture_creates_no_attempt_handler_or_capture` (both 11-word literals) |
| Confused/manual parameters cannot bypass | `test_confused_and_manual_paid_parameters_cannot_bypass_ten_word_limit` |
| Published paid/sandbox/event-v1 vector bytes and IDs unchanged | `test_published_paid_request_vector_remains_byte_identical`, existing independent-vector tests |

**Rejected-case accounting:** both public 11-word captures raise `DocumentError` from closed parameter validation. Handler calls = 0. Committed Attempts = 0. Committed Captures = 0.

**Unchanged published vectors:**
- paid request body 216 / `3fc7205a55a1a5c464c0ae4ebca21a1e3088c2022565929a670fdf757ab7987b`
- paid Attempt `89904bf8a6812fb3d0d845310e4705962bb4db928b80da3be67342dff5def185`
- sandbox Attempt `22adc4841c86b7cd98b90bba683aeac204a0cb568428b590fd399e8627eb4640`
- event-v1 AR Attempt `46d5fb97c109b9f64a42ff3a5e62978e2c25551d6b7274603fc88456acfd9a0f`

**Commands**
- `uv run pytest -q` — 711 passed, 1 skipped (HAM-01 opt-in matrix), 1 warning
- `uv run ruff check .` — All checks passed
- `uv run mypy` — Success: no issues found in 27 source files

**Review** vs `7b1fa349…`:
- **Standards:** 0 hard / 3 judgement (explicit adversarial tests duplicate existing vector/charset shapes). Kept because the Steward assignment required those named proofs.
- **Spec:** 0 missing/partial / 0 scope / 0 wrong.

**Weakest remaining area:** paid transport remains a closed copy of the PF-02 stream. One-shot remains inspect-then-act in one process. Word-count is a closed local rule and is not a live DataForSEO enforcement proof.

**Exact unproven limits:**
- No TLS, HTTP/2, DNS, timeout-realism, or `api.dataforseo.com` behavior
- No live paid operator invocation (blocked by F6)
- No claim that DataForSEO will invoice or reject using this same word definition
- No F7 concurrent-writer safety
- No off-host Evidence protection
- No provider Outcome/Observation/Derivation/API
- Ordinary suite does not run the HAM-01 kill matrix

**Authority disagreements:** none that change this implementation. Spec, ticket, and assignment agree on maximal nonempty ASCII-space runs and a maximum of 10.

**Confirmation:** this remediation, tests, and report made **zero** DataForSEO, sandbox, DNS, paid-host, or other public-network calls and spent **zero** provider credit. Tests used only `httpx.MockTransport` and the existing autouse `socket.create_connection` guard. The public CLI was never run with real credentials.
