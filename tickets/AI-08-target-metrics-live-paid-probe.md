# AI-08 — Target Metrics Live paid-probe adapter

**Status:** done  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** AI-07 — Target Metrics activation review (`closed`)  
**Approved by:** Project Steward  
**Start commit:** `c8f142f2ddca6b3acc8ef2a9918ce60d0ca47fc3`

## Purpose

Implement one closed, Evidence-only DataForSEO AI Optimization Target Metrics Live paid-probe
adapter. The adapter commits and verifies an HTTP-v2 Attempt before the only send-capable
path, performs at most one bounded exchange, commits at most one Capture, and exposes a
byte-exact read-only inspect command.

This ticket performs no real provider call and creates no provider Derivation, Observation,
PostgreSQL schema, Recipe selection, or read API. A later activation ticket owns the one
operator call and its bounded F6 protection proof.

## Accepted contract

Adapter token:

`dataforseo-ai-optimization-llm-mentions-target-metrics-live-paid-probe-v1`

Transport:

- method: `POST`;
- scheme/host: `https://api.dataforseo.com`;
- path: `/v3/ai_optimization/llm_mentions/target_metrics/live`;
- query: none;
- exactly one task in the JCS request array;
- application-header equation, credential injection, response-header retention/omission,
  redirect refusal, and complete/partial/no-response mapping reuse the accepted PF-09
  bounded single-exchange transport;
- adapter-owned timeout:
  `httpx.Timeout(connect=30.0, read=120.0, write=30.0, pool=30.0)`;
- adapter-owned response-body ceiling: `8_388_608` bytes;
- no retry, continuation, polling, response-derived follow-up, or second provider exchange.

Closed task parameters:

- one caller-supplied `keyword` using the accepted Search Mentions keyword grammar;
- `target` exactly
  `[{"keyword": keyword, "search_filter": "include", "search_scope": ["answer"], "match_type": "word_match"}]`;
- `location_code=2840`;
- `language_code="en"`;
- `platform="google"`, never omitted;
- `internal_list_limit=10`, sent explicitly rather than relying on the provider default.

Reject domain targets, more than one target, exclude filters, other scopes, partial match,
include-subdomains, `initial_dataset_filters`, `tag`, ChatGPT, omitted platform,
location/language names or alternate codes, list limits other than exact JSON integer
`10`, continuation/pagination keys, catalog operations, and every unknown parameter.

Policy:

- `mode="paid_probe"`;
- `policy_version="dataforseo-ai-optimization-target-metrics-live-paid-probe-v1"`;
- `pricing_basis="dataforseo-llm-mentions-live-2026-08-23"`;
- `max_authorized_cost_micro_usd=200000`;
- public capture and the internal capability issuer require exact Python `int` `200000`;
  booleans, floats, strings, decimals, null, missing acknowledgement, and every other
  integer fail before Attempt creation or send.

The acknowledgement is a fail-closed ceiling, not expected cost, provider invoice proof, or
permission to retry. Current claimed pricing is approximately `$0.10` per request plus
`$0.001` per returned row and must be rechecked before activation.

## Event-v2 and Evidence requirements

- Add this token as one explicit closed event-v2 adapter branch.
- Dispatch still peeks only `schema` and `version`, then revalidates the complete selected
  closed document and exact JCS bytes.
- Preserve every published event-v1, sandbox-v2, Keyword Overview-v2, Organic-v2, and Search
  Mentions-v2 byte vector and identifier.
- Attempt parameters include the complete closed Target Metrics request context, including
  explicit `internal_list_limit=10`.
- Commit and fully read back the Attempt plus exact request-body bytes before issuing the
  caller-unconstructible, immutable, one-use capability.
- Recheck adapter, version, provider, policy, host, path, headers, parameters, and request
  body after read-back and immediately before exchange.
- The one-shot guard scans the whole Evidence root and refuses any second committed Attempt
  for this exact adapter token, including after unresolved, credential-echo, partial,
  over-limit, failed, or complete paths.
- Neighbor adapter Evidence may coexist and must not consume this adapter's one-shot.
- Complete, partial, and no-response branches each commit at most one verified Capture under
  the accepted HTTP-v2 rules.
- Credential echo in the would-be retained body or retained response-header values fails
  closed before Capture commit. The committed Attempt remains and consumes the one-shot.
- Inspect returns only the exact nonempty body of a verified complete Capture for this
  adapter, performs no network or mutation, and fails closed on wrong adapter, partial,
  no-response, zero body, invalid ID, unknown version, or tamper.
- Mixed stores scrub clean. Existing fixture and provider Derivations skip valid Target
  Metrics Evidence and write no rows for it.

## Public surface

Module:

`observatory.dataforseo_ai_optimization_target_metrics_paid_probe`

Capture:

```bash
uv run python -m observatory.dataforseo_ai_optimization_target_metrics_paid_probe capture \
  --evidence-root PATH \
  --keyword "…" \
  --authorize-max-micro-usd 200000
```

Inspect:

```bash
uv run python -m observatory.dataforseo_ai_optimization_target_metrics_paid_probe inspect \
  --evidence-root PATH \
  --capture-id 64_LOWERCASE_HEX
```

The public Python capture function and CLI expose no URL, host, path, headers, request JSON,
client, timeout, body ceiling, platform, location, language, target options,
`internal_list_limit`, retry, continuation, alternate spend ceiling, or credential
arguments.

An internal deterministic test seam may replace the production endpoint only with:

`http://127.0.0.1:<1..65535>/v3/ai_optimization/llm_mentions/target_metrics/live`

Reject every other scheme, host, implicit/missing port, path, query, fragment, and userinfo
before Attempt creation and again before exchange. The committed Attempt must still name the
production HTTPS target.

## Acceptance criteria

- [x] Independent test literals and `hashlib.sha256` prove exact request-body,
      fingerprint, Attempt, and representative complete-Capture vectors without using the
      production constructors to derive expected values.
- [x] Constructors reproduce those vectors; all previously published event identities
      remain byte-identical.
- [x] Closed validator tests accept only the contract above and reject confused adapter,
      host, path, policy, target, platform, list-limit, and unknown-field cases.
- [x] Exact authorization, concrete-store, commit, read-back, capability, and target gates
      prevent all send-capable paths before a verified committed Attempt exists.
- [x] One-shot tests cover complete, unresolved, credential-echo, partial/over-limit, and
      neighbor-adapter stores.
- [x] Forged, copied, pickled, replayed, subclassed, and cross-adapter capabilities cannot
      transport.
- [x] Mock and loopback tests prove one request, exact JCS body, the sent-header equation,
      no redirect follow, and no extra provider exchange.
- [x] Complete nonempty/zero-byte/3xx/4xx/5xx, partial body failure, 8 MiB boundary,
      connect/send/header no-response, duplicate retained headers, denylist omissions, and
      credential echo follow the accepted HTTP-v2/PF-09 behavior.
- [x] Each committed branch reads back, satisfies D5, and leaves a clean scrub result.
- [x] Inspect emits exact verified bytes with no newline, write, or network and rejects
      every forbidden state above.
- [x] Mixed fixture/sandbox/Keyword Overview/Organic/Search Mentions/Target Metrics stores
      scrub clean; existing fixture and provider Derivations skip the new Evidence without
      integrity failure or PostgreSQL rows citing its IDs.
- [x] Ordinary tests use only `httpx.MockTransport` and loopback. A test guard fails any
      non-loopback socket connection and removes real credential environment variables.
- [x] `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy` pass.

## Required implementation report

Return:

- loaded project-local skill paths;
- exact parent and child commits;
- changed-path allowlist;
- acceptance criterion to proving-test map;
- independent vector bytes and SHA-256 identities;
- exact structural-gate and one-shot mechanism;
- exact mock/loopback request count, body, and sent headers;
- complete/partial/no-response and 8 MiB accounting;
- mixed-store scrub and zero-derive/PostgreSQL accounting;
- credential non-disclosure evidence;
- full command results;
- strongest and weakest tests;
- what genuinely reused the shared substrate and what remained surface-specific;
- likely false-green tests, architecture drift hazards, parser traps exposed for the later
  Recipe ticket, and improvements that should or should not block the next step;
- exact unproven limits;
- confirmation of zero provider/API-host/DNS calls, zero real credentials, zero live
  Evidence, and zero credit spend.

Use the project-local `implement`, `tdd`, `codebase-design`, and `code-review` skills.
Report the absolute `SKILL.md` path for each. Treat your own judgement on strengths,
weaknesses, gaps, dangerous seams, and worthwhile improvements as a first-class deliverable,
not an afterthought.

## Hard boundaries

- One ticket, one implementation commit on clean `main`; do not amend or push.
- Only [GROK] edits `src/` and `tests/`. Ticket status may become `review`, never
  `done`.
- Do not edit another ticket, authority document, existing provider fixture, or Evidence
  Store implementation.
- Do not make a DataForSEO, sandbox, DNS, paid-host, account, credential, or other public
  network request.
- Do not run the public capture CLI with real credentials or create live provider Evidence.
- Do not implement a parser, conformance fixture from provider testimony, Recipe,
  Derivation, Outcome, Observation, migration, PostgreSQL relation, Recipe selection, API
  route, projection, report, strategy feature, scheduler, F6 automation, F7 locking, generic
  provider framework, second list-limit contract, ChatGPT branch, domain target, Historical,
  Lite, Multi-Target, top-list, or another surface.
- Deliberate local duplication is acceptable where Target Metrics semantics differ. Do not
  widen Search Mentions schemas or admission meaning to share code.

## Next boundary

After independent Steward review and closure of this zero-network implementation, a separate
AI-09 activation ticket may authorize exactly one `generative engine optimization` call in
one fresh Evidence root after a fresh contract/pricing check and explicit [CHAZ]
authorization. AI-09 must inspect and scrub the resulting Evidence and complete the accepted
single-root encrypted off-host snapshot, fresh restore, scrub, and exact committed-ID
set-equality proof before closure.

## Implementation report

**Parent:** `c8f142f2ddca6b3acc8ef2a9918ce60d0ca47fc3`
**Child:** this implementation commit
**Status:** `review`
**AI-08 only:** yes. Nothing pushed.

Loaded skills:

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

### Changed-path allowlist

- `src/observatory/capture_event.py` (fifth exact HTTP-v2 adapter branch)
- `src/observatory/dataforseo_ai_optimization_target_metrics_paid_probe.py` (new)
- `tests/test_dataforseo_ai_optimization_target_metrics_paid_probe.py` (new)
- this ticket (Start commit, Status, Implementation report)

### Adapter token

`dataforseo-ai-optimization-llm-mentions-target-metrics-live-paid-probe-v1`

Production POST `https://api.dataforseo.com/v3/ai_optimization/llm_mentions/target_metrics/live`

### Independent vectors

Fixed inputs: keyword `observatory test`, nonce `7777…77`,
`authorized_at=2026-08-23T20:00:00.000000Z`,
`observatory_version=conformance-target-metrics-paid-probe-v1`.
Independent `hashlib.sha256` of literal JCS bytes (`test_independent_literal_vectors`);
constructors reproduce them (`test_closed_request_vector_and_attempt_identity`).

| Artifact | Value |
|---|---|
| request body | `[{"internal_list_limit":10,"language_code":"en","location_code":2840,"platform":"google","target":[{"keyword":"observatory test","match_type":"word_match","search_filter":"include","search_scope":["answer"]}]}]` |
| request SHA-256 | `4414f03561a728f03a6b0e859bcb210f8876968c5e2b7c2e2cc5eeb1d209e170` |
| fingerprint | `1404ce81eb7884e21a5571a30db02e1c0555fdcf6db5e805391255cf6e604bbd` |
| Attempt ID | `1d2716ea2a6888c3c7b7aeb0d0ec4f9b5b3f84d4e8780f1ae270d306f89c907d` |
| complete Capture ID (`{"ok":true}`) | `36ba18e80cce117709c56fab7e7b1df8256defd87390d43a7550c1faa8681e84` |

Previously published sandbox / Keyword Overview / Organic / Search Mentions Attempt IDs remain byte-identical.

### Structural gate and one-shot

- Public capture and `_issue_verified_attempt` require `type is int` and value exactly `200000` before Attempt commit or send.
- Concrete `EvidenceStore` only; subclass cannot issue.
- `_target_metrics_attempt_exists` scans every committed Attempt in the root for this adapter token (including unresolved).
- Refuse at `_open_or_create`, `_run_gated_capture`, and issuer.
- Capability is unconstructible, immutable, one-use, identity-checked; exchange rechecks adapter/version/provider/policy/host/path/headers/parameters.
- Neighbors (fixture, sandbox, KO, Organic, Search Mentions) coexist and do not consume this one-shot.

### Mock/loopback request

One POST, exact JCS body above, sent headers:
`accept`, `accept-encoding: identity`, `connection: close`, `content-type`,
`user-agent: observatory-dataforseo-v1`, `host: api.dataforseo.com`,
`content-length: 210`, `authorization: Basic <sentinel>`.
Loopback override only `http://127.0.0.1:<port>/v3/ai_optimization/llm_mentions/target_metrics/live`.
Committed Attempt still names production HTTPS. Redirects not followed (302 is complete Capture).

### Transport accounting

- Adapter ceiling `8_388_608`; shared transport does not own it.
- Default ceiling: `8_388_608+1` body → `response_partial` of exactly 8 MiB.
- 200/302/404/500 nonempty → `response_complete`.
- Zero-byte 200 → complete, `present_zero_bytes`.
- Mid-body timeout → `response_partial`.
- `ConnectError` → `no_response`.
- Duplicate `x-request-id` retained; denylist names omitted.
- Credential echo in body or retained header: no Capture; Attempt remains; one-shot consumed.

### Mixed-store / derive

Fixture + sandbox + KO + Organic + Search Mentions + Target Metrics: `scrub_store` empty.
Fixture/KO/Organic/Search Mentions derive skip Target Metrics Evidence; zero PostgreSQL
`outcomes` rows cite its Attempt/Capture IDs.

### Credential non-disclosure

Sentinel login/password/basic never appear in committed manifests or retained headers.
Authorization is injected only after the capability is issued. Ordinary tests delete
credential env vars and fail any non-loopback `socket.create_connection`.

### Acceptance criterion to proving-test map

| Criterion | Tests |
|---|---|
| Independent literals + hashlib | `test_independent_literal_vectors`, `test_closed_request_vector_and_attempt_identity` |
| Constructors reproduce; old IDs unchanged | `test_closed_request_vector_and_attempt_identity`, `test_existing_adapter_identities_unchanged` |
| Closed validator / unknown fields | `test_frozen_fields_are_rejected`, `test_missing_required_keys_are_rejected`, `test_wrong_policy_fields_are_rejected`, `test_confused_contracts_are_rejected`, keyword grammar tests |
| Auth/concrete-store/commit/read-back/capability | `test_authorization_required_before_attempt`, `test_subclassed_store_cannot_issue`, `test_attempt_is_committed_before_first_handler`, `test_failed_attempt_commit_never_reaches_handler` |
| One-shot complete/unresolved/echo/partial/neighbors | `test_one_shot_is_adapter_specific_and_allows_neighbors`, `test_unresolved_attempt_blocks_second_invocation`, `test_credential_echo_leaves_unresolved_one_shot`, `test_over_limit_partial_consumes_one_shot`, `test_default_8mib_ceiling_is_partial` |
| Forged/copied/pickled/replayed/cross-adapter | `test_forged_copied_mutated_and_replayed_capability_cannot_transport`, `test_cross_adapter_capabilities_are_isolated` |
| One request, JCS, headers, no redirect | `test_attempt_is_committed_before_first_handler`, `test_loopback_server_sees_attempt_and_does_not_follow_redirect`, `test_token_in_body_is_still_one_exchange` |
| Complete/partial/no-response/8 MiB | `test_complete_status_classes_and_zero_byte`, `test_mid_body_timeout_and_no_response`, `test_default_8mib_ceiling_is_partial`, `test_secret_headers_omitted` |
| Inspect | `test_inspect_emits_exact_bytes_without_mutation`, `test_inspect_rejects_wrong_adapter_partial_zero_and_tamper` |
| Mixed scrub / zero derive | `test_one_shot_is_adapter_specific_and_allows_neighbors`, `test_fixture_and_provider_derive_skip_target_metrics` |
| No public network / no real credentials | autouse `_no_public_network`, `_isolate_credentials` |
| Public surface has no injection | `test_public_cli_and_function_have_no_injection_seams` |

### Code-review

**Standards:** 0 hard / 5 judgement. Worst: `_validate_target_metrics_http_parameters` reuses `_validate_mentions_target`, so a later Search Mentions target-admission change would retarget Target Metrics. Ticket authorized local duplication; this reuse is the accepted keyword/target grammar, not a widened Search Mentions schema.

**Spec:** no wrong implementation or scope creep. Remaining partial proofs (listed below) do not block AI-09.

### Strongest / weakest

Strongest: independent JCS vectors; adapter-keyed whole-root one-shot including unresolved and credential-echo; Attempt-before-handler with sent-header equation; 8 MiB default-ceiling partial; mixed-store skip.

Weakest: send/header-phase no-response not separately driven (ConnectError only, matching Search Mentions); inspect unknown-version not planted (cannot commit an invalid v2 Capture through constructors); capability subclass untested (`__slots__` + private class); `_require_target_metrics_target` does not re-read request-body bytes immediately before exchange (issuer already did).

### Shared vs surface-specific

Reused: Evidence Store commit/verify, PF-09 `perform_bounded_http_exchange`, credential env, header denylist, HTTP-v2 envelope, Search Mentions keyword grammar.

Surface-specific: token, path, `internal_list_limit=10` (no `offset`/`limit`), policy/pricing_basis date, 8 MiB ceiling, one-shot scan keyed to this token, CLI module.

### False-green / drift / parser traps for the later Recipe

- Empty `items` + `total_count=0` in a real Target Metrics body must not be classified as Search Mentions emptiness.
- Do not treat `internal_list_limit` truncation of `sources_domain` as corpus size.
- Grouping `key` types mix int (location) and string (language/platform/domain).
- `aggregated_metrics` is the payload; copying Search Mentions `_RESULT_KEYS` will fail closed or mis-admit.
- Reusing `_validate_mentions_target` is a coupling hazard if Search Mentions target grammar ever changes.

Improvements that **should not** block AI-09: generic dispatch table; send/header no-response extras; inspect unknown-version plant; duplicating the target validator.

Improvements that **should** land in the Recipe/parser ticket, not here: Target Metrics emptiness vs Search Mentions; grouping identity; cost decimal; ChatGPT-only arrays on a google request.

### Exact unproven limits

- No live provider call, so real envelope, billing grain, and `internal_list_limit` honoring remain AI-09 Evidence.
- F6, F7, power-loss, concurrent writers unproved.
- `argparse type=int` CLI path is not the same as `type is int` on the public Python function; CLI still requires `--authorize-max-micro-usd 200000`.
- AGENTS.md does not yet list this module entrypoint (Steward-owned).

### Command evidence

Final implementation bytes, then:

```
uv run mypy
```

UTC ~`2026-08-23T23:42:47Z` → `2026-08-23T23:47:39Z` (combined with ruff/pytest), exit 0, no issues in 58 source files.

```
uv run ruff check .
```

exit 0, all checks passed.

```
uv run pytest -q
```

exit 0, **1109 passed**, **1 skipped**, 1 Starlette TestClient deprecation warning, 289.04s.

No leftover `observatory-ce05-*` containers. No behavior-affecting change after this suite.

### Confirmation

Zero DataForSEO / sandbox / DNS / paid-host / account / public-network requests.
Zero real credentials. Zero live Evidence. Zero credit spend.
No parser, conformance fixture from provider testimony, Recipe, Derivation, PostgreSQL
schema, API route, ChatGPT branch, domain target, Historical, second list-limit, generic
framework, other ticket, or authority document except this ticket's implementer fields.
No amend. No push.

## Remediation report

**Parent:** `78f4db32c6d492e88ef305578432563ebb90785d`
**Child:** this remediation commit
**Status:** `review` (unchanged)
**AI-08 only:** yes. Nothing pushed. No amend.

Loaded skills:

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

### Changed-path allowlist

- `src/observatory/dataforseo_ai_optimization_target_metrics_paid_probe.py`
- `tests/test_dataforseo_ai_optimization_target_metrics_paid_probe.py`
- this ticket (remediation report only; Status remains `review`)

### Bypass to proving-test map

| Bypass | Proof |
|---|---|
| `object.__setattr__` replaces `request_body` on a genuinely issued capability | `test_issued_request_body_replacement_cannot_transport`; first block of `test_pre_send_verifies_committed_attempt_and_request_body` |
| `object.__setattr__` replaces `document` (and matching body) with a valid-looking Target Metrics Attempt | `test_issued_document_replacement_cannot_transport` (`validate_attempt` on the replacement) |
| `object.__setattr__(_used, False)` after one successful exchange | `test_closure_owned_replay_protection_ignores_used_attribute` |
| Committed Evidence body tamper (pool object with bundle `request.body` left original; bundle `request.body` tamper) | `test_pre_send_verifies_committed_attempt_and_request_body` |
| Unchanged issued capability still one exchange | last block of `test_pre_send_verifies_committed_attempt_and_request_body` |

Ordinary `__setattr__` rejection remains in `test_forged_copied_mutated_and_replayed_capability_cannot_transport` and is not the new proof.

### Closure-owned issuance and consumption

`_build_transport_gate` keeps a process-local `issued: list[_Issuance]`. Each record binds:

- capability object identity (`record.capability is attempt`);
- the concrete `EvidenceStore` instance that committed;
- `attempt_id`;
- `document_preimage` (`canonical_json` of the verified read-back Attempt);
- `request_body` bytes copied from the committed bundle;
- `consumed: bool`.

Caller-visible `attempt_id` / `document` / `request_body` / `_used` remain on the capability for inspect/capture/outcome surfaces. They are not transport authority. `_exchange` never reads `_used`.

On `_exchange`: require `type(attempt) is _VerifiedAttempt` and `record.capability is attempt`; if `record.consumed`, raise the existing one-exchange `StoreError`; set `record.consumed = True` (and `_used=True` only as a non-authoritative mirror) **before** field comparison, Evidence revalidation, or `perform_bounded_http_exchange`. Resetting `_used` cannot replay.

### Pre-send revalidation sequence

Immediately before `perform_bounded_http_exchange`:

1. exact private type + exact issued object identity;
2. consume the closure record;
3. reject any difference between caller-visible `attempt_id`, JCS(`document`), and `request_body` vs the closure record;
4. `store.read_attempt(attempt_id)` (D5 verify-on-read) on the bound concrete store;
5. `store.verify_attempt_directory(bundle)` on the normative path (no weaker parallel verifier);
6. exact canonical Attempt equality to the issuance preimage and identity `content_digest == attempt_id`;
7. re-read bundle `request.body` and require byte equality with the closure-owned body;
8. `validate_target_metrics_http_parameters` on the verified parameters, recompute singleton-task JCS, require equality with stored and closure-owned bytes;
9. `_require_target_metrics_target` on the verified store document (adapter, version, provider, policy, production target, headers, parameters, 200000 ceiling);
10. send `bytes(record.request_body)` only.

### Request / handler accounting

| Case | Handler calls | Bytes that can reach the handler |
|---|---|---|
| Issued `request_body` replacement | 0 | none |
| Issued `document` (+ matching body) replacement | 0 | none |
| Successful exchange then `_used=False` replay | 1 | original `TARGET_METRICS_REQUEST_BODY` once |
| Pool-object Evidence tamper (bundle body unchanged) | 0 | none |
| Bundle `request.body` Evidence tamper | 0 | none |
| Unchanged issued capability | 1 | original `TARGET_METRICS_REQUEST_BODY` once |

### Published vectors

Unchanged. `test_independent_literal_vectors`, `test_closed_request_vector_and_attempt_identity`, and `test_existing_adapter_identities_unchanged` still pin:

- request SHA-256 `4414f03561a728f03a6b0e859bcb210f8876968c5e2b7c2e2cc5eeb1d209e170`
- Attempt `1d2716ea2a6888c3c7b7aeb0d0ec4f9b5b3f84d4e8780f1ae270d306f89c907d`
- complete Capture `36ba18e80cce117709c56fab7e7b1df8256defd87390d43a7550c1faa8681e84`
- prior sandbox / KO / Organic / Search Mentions Attempt IDs byte-identical

Adapter token, production URL, closed parameters, policy, timeouts, and 8 MiB ceiling are unchanged.

### Code-review

**Standards:** 0 hard / 4 judgement. Worst: `_require_target_metrics_target` remains a second closed-contract walk on the send path (pre-existing; this remediation also runs `validate_target_metrics_http_parameters`). Nested lists in `_freeze_maps` stay mutable; canonical compare now fails closed on that mutation.

**Spec:** 1 partial (resolved) / 0 creep / 0 wrong. Worst was that Evidence tamper only overwrote bundle `request.body`, which a weaker disk-vs-closure compare would also refuse. The test now tampers the pool object while leaving bundle `request.body` original, so a verifier that skipped `read_attempt` / `verify_attempt_directory` would send.

### Strongest / weakest remaining tests

Strongest: pool-object tamper with original bundle body; issued-object `object.__setattr__` body and valid-looking document replacement; closure-owned replay after `_used=False`.

Weakest: send/header-phase no-response still ConnectError-only (pre-existing); inspect unknown-version still unplanted; capability `_used` is still written and still present on `__slots__`, which can mislead a later reader even though exchange ignores it.

### Remaining caller-controlled influence (judgement)

These cannot change the sent request body through capability attributes, but they remain:

- `_exchange` still takes `client`, `endpoint`, and `max_response_body_bytes` (approved test seam). A holder can still deliver the **verified** body to loopback/mock, not a substitute body.
- `_commit_target_metrics_capture` and the outcome `attempt_id` still read capability attributes after transport. Post-exchange `object.__setattr__` on `document` / `attempt_id` can still affect Capture construction and the returned id, not the HTTP body.
- The bound `EvidenceStore` instance is mutable (`root`, monkeypatched `read_attempt` / `verify_attempt_directory`). Preimage + body equality still fail closed unless the attacker forges a store API that returns the original committed bytes (in which case the sent body is still the original).
- `_Issuance` lives in `_exchange.__closure__`. A same-process caller can reach the list and flip `consumed` or replace `request_body`. Single-process closure state is accepted for AI-08; this is not F7.

### Older adapter gates

The same capability-attribute authority (`request_body`, `document`, `_used`) and `object.__setattr__` hole exist in:

- `src/observatory/dataforseo_sandbox.py`
- `src/observatory/dataforseo_paid_probe.py`
- `src/observatory/dataforseo_google_organic_paid_probe.py`
- `src/observatory/dataforseo_ai_optimization_search_mentions_paid_probe.py`

Not remediated here. Recommended follow-up: four separately bounded tickets, one per remaining gate, each copying this proof list. Smallest first boundary: Search Mentions (nearest sibling). Do not introduce a shared capability framework in those tickets.

### Exact unproven limits

- No live provider call; real envelope/billing remain AI-09.
- F6 / F7 / power-loss / concurrent writers unproved. Closure-owned `consumed` is single-process only.
- TOCTOU between `verify_attempt_directory` and the subsequent `request.body` read is unproved.
- `argparse type=int` CLI vs `type is int` on the Python function, as before.
- AGENTS.md still does not list this module entrypoint (Steward-owned).

### Command evidence

Final remediation bytes, then:

```
uv run mypy
```

exit 0, no issues in 58 source files.

```
uv run ruff check .
```

exit 0, all checks passed.

```
uv run pytest -q
```

exit 0, **1113 passed**, **1 skipped**, 1 Starlette TestClient deprecation warning, 290.35s.

### Confirmation

Zero DataForSEO / sandbox / DNS / paid-host / account / public-network requests.
Zero real credentials. Zero live Evidence. Zero credit spend.
No other production module, `capture_event.py`, other adapter gate, authority document, or other ticket.
No amend. No push.

## Steward closure

**Closed:** 2026-08-24  
**Accepted implementation:** `78f4db32c6d492e88ef305578432563ebb90785d`  
**Accepted remediation:** `342a86a99ebf0603dbbc0db417c174dc902a3223`

Independent review accepted the closed Target Metrics adapter after the remediation moved
transport authority and replay state into the issuer closure, revalidated the committed
Attempt and exact request-body bytes immediately before send, and proved fail-closed
behavior for genuine issued-capability mutation, used-flag reset, replay, and committed
Evidence tamper.

Closure evidence:

- implementer full suite: **1113 passed, 1 skipped**, with the one known Starlette
  deprecation warning;
- independent operator targeted suite at the exact remediation commit: **68 passed**;
- independent MCP `ruff` and `mypy` tasks passed at the exact remediation commit;
- published event identities, mixed-store behavior, zero-derive accounting, and
  zero-network/zero-credit boundaries remain as reported above.

No live DataForSEO call, credential use, paid Evidence, Recipe, Derivation, PostgreSQL
projection, or API surface is authorized or claimed by this closure. AI-09 remains the
separate activation boundary. The inherited capability-authority weakness found in the
four older transport gates is recorded as F13 with an explicit before-next-live-use or
reuse trigger; it was not folded into this adapter's implementation.
