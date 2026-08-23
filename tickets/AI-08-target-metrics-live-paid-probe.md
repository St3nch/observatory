# AI-08 — Target Metrics Live paid-probe adapter

**Status:** approved  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** AI-07 — Target Metrics activation review (`closed`)  
**Approved by:** Project Steward  
**Start commit:** [GROK] records the exact clean `main` HEAD before implementation

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

- [ ] Independent test literals and `hashlib.sha256` prove exact request-body,
      fingerprint, Attempt, and representative complete-Capture vectors without using the
      production constructors to derive expected values.
- [ ] Constructors reproduce those vectors; all previously published event identities
      remain byte-identical.
- [ ] Closed validator tests accept only the contract above and reject confused adapter,
      host, path, policy, target, platform, list-limit, and unknown-field cases.
- [ ] Exact authorization, concrete-store, commit, read-back, capability, and target gates
      prevent all send-capable paths before a verified committed Attempt exists.
- [ ] One-shot tests cover complete, unresolved, credential-echo, partial/over-limit, and
      neighbor-adapter stores.
- [ ] Forged, copied, pickled, replayed, subclassed, and cross-adapter capabilities cannot
      transport.
- [ ] Mock and loopback tests prove one request, exact JCS body, the sent-header equation,
      no redirect follow, and no extra provider exchange.
- [ ] Complete nonempty/zero-byte/3xx/4xx/5xx, partial body failure, 8 MiB boundary,
      connect/send/header no-response, duplicate retained headers, denylist omissions, and
      credential echo follow the accepted HTTP-v2/PF-09 behavior.
- [ ] Each committed branch reads back, satisfies D5, and leaves a clean scrub result.
- [ ] Inspect emits exact verified bytes with no newline, write, or network and rejects
      every forbidden state above.
- [ ] Mixed fixture/sandbox/Keyword Overview/Organic/Search Mentions/Target Metrics stores
      scrub clean; existing fixture and provider Derivations skip the new Evidence without
      integrity failure or PostgreSQL rows citing its IDs.
- [ ] Ordinary tests use only `httpx.MockTransport` and loopback. A test guard fails any
      non-loopback socket connection and removes real credential environment variables.
- [ ] `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy` pass.

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
